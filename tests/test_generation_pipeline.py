"""Tests for the staged multi-generator pipeline."""

from __future__ import annotations

import unittest
from unittest.mock import patch
from pathlib import Path
import tempfile

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.config import Settings
from wikidata_simpleqa.generation_pipeline import (
    ROUTE3_POPULAR_EXACT_ANSWERS,
    _apply_number_reference_margin,
    _build_route_rewrite_payload,
    _post_rewrite_answer_scope_ambiguity_failure,
    process_generated_candidates,
    run_generation_pipeline,
)
from wikidata_simpleqa.generation_models import EntityReference, EvidenceRecord, GeneratedCandidate
from wikidata_simpleqa.generator_validators import run_search_based_longtail_verifier
from wikidata_simpleqa.grading import ModelPanelMember, evaluate_model_panel
from wikidata_simpleqa.models import AmbiguityResolution, CandidateFact, DomainTemplate
from wikidata_simpleqa.route3_openrouter import (
    DefiniteOpenRouterHTTPError,
    DefiniteOpenRouterResponseError,
)
from wikidata_simpleqa.rule_based_answer_type_gate import RuleBasedAnswerTypeGateResult


class FakeWikipediaClient:
    """Minimal summary client for pipeline tests."""

    request_events: list[dict] = []

    def fetch_summary(self, title: str) -> dict:
        return {
            "title": title.replace("_", " "),
            "extract": "Example Film is a 2020 drama film directed by Jane Doe.",
            "content_urls": {
                "desktop": {
                    "page": "https://en.wikipedia.org/wiki/Example_Film",
                }
            },
        }


class FakeSearchClient:
    """Simple search client stub for pipeline tests."""

    request_events: list[dict] = []

    def __init__(self, results_by_query: dict[str, list[dict[str, str]]]) -> None:
        self.results_by_query = results_by_query

    def search(self, query: str, *, max_results: int = 5):
        rows = self.results_by_query.get(query, [])[:max_results]
        return [type("SearchResult", (), row)() for row in rows]


class ErrorSearchClient:
    """Search client stub that raises one network-like error."""

    def search(self, query: str, *, max_results: int = 5):
        raise RuntimeError("search backend unavailable")


class FakePanelModelClient:
    """Answer-model stub for the second-stage grading panel."""

    def __init__(self, response: str) -> None:
        self.response = response

    def complete_text(self, prompt: str) -> str:
        return self.response

    def complete_text_with_audit(self, prompt: str) -> dict:
        return {
            "text": self.response,
            "request_payload": {"prompt": prompt},
            "response_body": {"fake_answer_response": self.response},
        }


class FakePanelGraderClient:
    """Grader stub that returns configured or prompt-aware responses."""

    def __init__(self, responses: list[str] | None = None) -> None:
        self.responses = list(responses or [])
        self.prompts: list[str] = []

    def complete_text(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if self.responses:
            return self.responses.pop(0)
        if "Predicted answer: Jane Doe" in prompt or "Predicted answer: J. Doe" in prompt:
            return "A"
        if "Predicted answer: John Smith" in prompt:
            return "B"
        return "C"

    def complete_text_with_audit(self, prompt: str) -> dict:
        text = self.complete_text(prompt)
        return {
            "text": text,
            "request_payload": {"prompt": prompt},
            "response_body": {"fake_grader_response": text},
        }


class FakeRewriteClient:
    """Simple rewrite stub that returns one rewritten question."""

    def rewrite_question(self, payload: dict) -> dict:
        return {
            "rewritten_question": f"Who directed Moonlit Harbor according to rewrite {payload['target_property']}?",
            "search_queries": [
                f"{payload.get('canonical_question', '')} context",
                f"{payload['target_property']} Moonlit Harbor production",
            ],
            "answer_aliases": ["J. Doe", "Jane D."],
            "discard_reason": None,
        }


class FakeWikidataClient:
    """Minimal Wikidata client stub for the pipeline tests."""

    def search_entities(self, query: str, limit: int = 10):
        return []

    def stats_snapshot(self):
        return {"events": [], "problems": []}


def make_template() -> DomainTemplate:
    """Build a minimal single-hop template."""
    return DomainTemplate(
        domain="film_director",
        topic="Arts and Media",
        answer_type="Person",
        question_family="who_directed_film",
        subject_type_qid="Q11424",
        subject_type_label="film",
        date_property_pid="P577",
        target_property_pid="P57",
        target_property_label="director",
        canonical_question_template="Who directed the {subject_kind} {descriptor}?",
    )


def make_candidate() -> CandidateFact:
    """Build a minimal harvested candidate for end-to-end pipeline tests."""
    return CandidateFact(
        subject_qid="Q1",
        subject_label="Example Film",
        subject_aliases=[],
        domain="film_director",
        topic="Arts and Media",
        answer_type="Person",
        question_family="who_directed_film",
        subject_type_qids=["Q11424"],
        target_property_pid="P57",
        target_property_label="director",
        answer_qids=["Q2"],
        answer_labels=["Jane Doe"],
        answer_aliases=["J. Doe"],
        date_property_pid="P577",
        date_value="2020-01-01",
        target_time="2020",
        canonical_question="",
        provenance_complete=True,
        source_metadata={
            "question_format_args": {"subject_kind": "film"},
            "subject_wikipedia_title": "Example_Film",
            "subject_wikipedia_url": "https://en.wikipedia.org/wiki/Example_Film",
            "subject_sitelink_count": 12,
            "subject_claim_count": 44,
            "wikidata_access_date": "2024-05-01",
        },
        subject_resource_url="https://en.wikipedia.org/wiki/Example_Film",
        subject_resource_key="https://en.wikipedia.org/wiki/Example_Film",
    )


def make_route3_candidate(
    *,
    answer: str,
    answer_type: str = "Other",
    question: str = "Which organization signed the Harbor Lights agreement?",
) -> GeneratedCandidate:
    """Build a minimal Route 3 generated candidate for shared-pipeline tests."""
    return GeneratedCandidate(
        source_type="wikipedia_tables",
        generation_route="route3_wikipedia_infobox",
        question=question,
        canonical_question=question,
        answer=answer,
        answer_aliases=[],
        subject_entity=EntityReference(
            name="Harbor Lights",
            wikipedia_title="Harbor_Lights",
            url="https://en.wikipedia.org/wiki/Harbor_Lights",
        ),
        answer_entity=EntityReference(name=answer),
        relation_or_claim="single_fact",
        evidence=EvidenceRecord(
            text=f"Harbor Lights agreement party: {answer}.",
            url="https://en.wikipedia.org/wiki/Harbor_Lights",
            source_title="Harbor Lights",
            retrieved_at="2026-05-12",
        ),
        question_family="wikipedia_infobox_table_fact",
        answer_type=answer_type,
        topic="Wikipedia semi-structured data",
        target_time="2026",
        source_template_domain="wikipedia_infobox_table",
    )


class GenerationPipelineTests(unittest.TestCase):
    """Check acceptance and rejection in the shared pipeline."""

    def test_pipeline_keeps_valid_candidates_from_the_same_subject(self) -> None:
        template = make_template()
        candidate = make_candidate()
        resolution = AmbiguityResolution(status="label_unique", descriptor="Example Film")
        search_client = FakeSearchClient(
            {
                "Who directed the drama film Example Film?": [],
                "Example Film director": [],
                "Example Film director Jane Doe": [],
                "Who directed the film Example Film?": [],
            }
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(
                target_time="2020",
                pilot_total=2,
                output_path=Path(tmpdir) / "accepted.jsonl",
                rejected_output_path=Path(tmpdir) / "rejected.jsonl",
            )
            with (
                patch("wikidata_simpleqa.generators.harvest_candidates", return_value=[candidate]),
                patch("wikidata_simpleqa.generators.validate_route1_candidate", return_value=resolution),
            ):
                result = run_generation_pipeline(
                    settings,
                    templates=[template],
                    wikidata_client=FakeWikidataClient(),
                    wikipedia_client=FakeWikipediaClient(),
                    search_client=search_client,
                )
        self.assertEqual(len(result.accepted), 2)
        self.assertEqual(result.rejected, [])
        self.assertEqual(
            {record["generation_route"] for record in result.accepted},
            {"route1_wikidata_light", "route2_wikidata_wikipedia_hybrid"},
        )

    def test_shared_pipeline_keeps_same_subject_and_exact_question(self) -> None:
        first = make_route3_candidate(answer="Archive Guild")
        second = make_route3_candidate(answer="Second Guild")

        with tempfile.TemporaryDirectory() as tmpdir:
            result = process_generated_candidates(
                [first, second],
                settings=Settings(
                    target_time="2020",
                    pilot_total=2,
                    output_path=Path(tmpdir) / "accepted.jsonl",
                    rejected_output_path=Path(tmpdir) / "rejected.jsonl",
                ),
                search_client=FakeSearchClient({}),
            )

        self.assertEqual(len(result.accepted), 2)
        self.assertEqual(result.rejected, [])
        self.assertEqual(
            [record["question"] for record in result.accepted],
            [first.question, second.question],
        )
        self.assertEqual(len({record["subject_resource_key"] for record in result.accepted}), 1)

    def test_pipeline_rejects_candidate_at_search_verifier_stage(self) -> None:
        template = make_template()
        candidate = make_candidate()
        resolution = AmbiguityResolution(status="label_unique", descriptor="Example Film")
        search_client = FakeSearchClient(
            {
                "Who directed the drama film Example Film?": [
                    {
                        "title": "Jane Doe directed Example Film",
                        "snippet": "direct answer",
                        "url": "https://example.test/1",
                    }
                ],
                "Who directed the film Example Film?": [
                    {
                        "title": "Jane Doe directed Example Film",
                        "snippet": "direct answer",
                        "url": "https://example.test/2",
                    }
                ],
            }
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(
                target_time="2020",
                pilot_total=2,
                output_path=Path(tmpdir) / "accepted.jsonl",
                rejected_output_path=Path(tmpdir) / "rejected.jsonl",
            )
            with (
                patch("wikidata_simpleqa.generators.harvest_candidates", return_value=[candidate]),
                patch("wikidata_simpleqa.generators.validate_route1_candidate", return_value=resolution),
            ):
                result = run_generation_pipeline(
                    settings,
                    templates=[template],
                    wikidata_client=FakeWikidataClient(),
                    wikipedia_client=FakeWikipediaClient(),
                    search_client=search_client,
                )
        self.assertEqual(result.accepted, [])
        self.assertEqual(result.rejected[0]["rejection_reason"], "search_longtail_verifier_rejected")

    def test_process_generated_candidates_applies_rewrite_client(self) -> None:
        source_candidate = make_candidate()
        source_candidate.source_metadata["stable_answer_override"] = True
        candidate = GeneratedCandidate(
            source_type="test",
            generation_route="route2_wikidata_wikipedia_hybrid",
            question="Who directed the film Example Film?",
            canonical_question="Who directed the film Example Film?",
            answer="Jane Doe",
            answer_aliases=["J. Doe"],
            subject_entity=EntityReference(
                name="Example Film",
                qid="Q1",
                wikipedia_title="Example_Film",
                url="https://en.wikipedia.org/wiki/Example_Film",
            ),
            answer_entity=EntityReference(name="Jane Doe", qid="Q2"),
            relation_or_claim="director",
            evidence=EvidenceRecord(
                text="Example Film is a 2020 drama film directed by Jane Doe.",
                url="https://en.wikipedia.org/wiki/Example_Film",
                source_title="Example Film",
                retrieved_at="2026-05-12",
            ),
            question_family="who_directed_film",
            answer_type="Person",
            topic="Arts and Media",
            target_time="2020",
            source_template_domain="film_director",
            source_metadata={
                "subject_wikipedia_title": "Example_Film",
                "subject_wikipedia_url": "https://en.wikipedia.org/wiki/Example_Film",
                "subject_sitelink_count": 12,
                "subject_claim_count": 44,
                "stable_answer_override": True,
            },
            source_candidate=source_candidate,
        )
        search_client = FakeSearchClient(
            {
                "Who directed Moonlit Harbor according to rewrite director?": [],
                "Example Film director": [],
                "Example Film director Jane Doe": [],
            }
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(
                target_time="2020",
                pilot_total=1,
                output_path=Path(tmpdir) / "accepted.jsonl",
                rejected_output_path=Path(tmpdir) / "rejected.jsonl",
                rewrite_enabled=True,
            )
            result = process_generated_candidates(
                [candidate],
                settings=settings,
                search_client=search_client,
                rewrite_client=FakeRewriteClient(),
            )
        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(
            result.accepted[0]["rewritten_question"],
            "Who directed Moonlit Harbor according to rewrite director?",
        )
        self.assertEqual(
            result.accepted[0]["search_queries"],
            [
                "Who directed the film Example Film? context",
                "director Moonlit Harbor production",
            ],
        )
        self.assertEqual(result.accepted[0]["answer_aliases"], ["J. Doe", "Jane D."])
        self.assertEqual(
            result.accepted[0]["source_metadata"]["small_model_rewrite_response"]["rewritten_question"],
            "Who directed Moonlit Harbor according to rewrite director?",
        )
        self.assertNotIn("rewrite_disabled", result.accepted[0]["notes"])

    def test_process_generated_candidates_rejects_non_self_contained_rewrite_before_search(self) -> None:
        source_candidate = make_candidate()
        source_candidate.source_metadata["stable_answer_override"] = True
        candidate = GeneratedCandidate(
            source_type="test",
            generation_route="route2_wikidata_wikipedia_hybrid",
            question="Who directed the film Harbor Lights?",
            canonical_question="Who directed the film Harbor Lights?",
            answer="Jane Doe",
            answer_aliases=["J. Doe"],
            subject_entity=EntityReference(
                name="Harbor Lights",
                qid="Q1",
                wikipedia_title="Harbor_Lights",
                url="https://en.wikipedia.org/wiki/Harbor_Lights",
            ),
            answer_entity=EntityReference(name="Jane Doe", qid="Q2"),
            relation_or_claim="director",
            evidence=EvidenceRecord(
                text="Harbor Lights is a 2020 drama film directed by Jane Doe.",
                url="https://en.wikipedia.org/wiki/Harbor_Lights",
                source_title="Harbor Lights",
                retrieved_at="2026-05-12",
            ),
            question_family="who_directed_film",
            answer_type="Person",
            topic="Arts and Media",
            target_time="2020",
            source_template_domain="film_director",
            source_metadata={
                "subject_wikipedia_title": "Harbor_Lights",
                "subject_wikipedia_url": "https://en.wikipedia.org/wiki/Harbor_Lights",
                "stable_answer_override": True,
            },
            source_candidate=source_candidate,
        )

        class ListedRewriteClient:
            def rewrite_question(self, payload: dict) -> dict:
                return {
                    "rewritten_question": "Which Director is Listed in the Table?",
                    "search_queries": ["listed table director"],
                    "discard_reason": None,
                }

        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(
                target_time="2020",
                pilot_total=1,
                output_path=Path(tmpdir) / "accepted.jsonl",
                rejected_output_path=Path(tmpdir) / "rejected.jsonl",
                rewrite_enabled=True,
            )
            result = process_generated_candidates(
                [candidate],
                settings=settings,
                search_client=ErrorSearchClient(),
                rewrite_client=ListedRewriteClient(),
            )

        self.assertEqual(result.accepted, [])
        self.assertEqual(result.rejected[0]["rejection_reason"], "rewrite_guard_rejected")
        self.assertEqual(
            result.rejected[0]["rejection_rule"],
            "post_rewrite_self_containment_forbidden_phrase:listed",
        )
        self.assertEqual(
            result.rejected[0]["source_metadata"]["post_rewrite_self_containment_failure_reason"],
            "post_rewrite_self_containment_forbidden_phrase:listed",
        )

    def test_process_generated_candidates_rejects_table_marker_rewrite_before_search(self) -> None:
        source_candidate = make_candidate()
        source_candidate.source_metadata["stable_answer_override"] = True
        candidate = GeneratedCandidate(
            source_type="test",
            generation_route="route2_wikidata_wikipedia_hybrid",
            question="Who directed the film Harbor Lights?",
            canonical_question="Who directed the film Harbor Lights?",
            answer="Jane Doe",
            answer_aliases=["J. Doe"],
            subject_entity=EntityReference(
                name="Harbor Lights",
                qid="Q1",
                wikipedia_title="Harbor_Lights",
                url="https://en.wikipedia.org/wiki/Harbor_Lights",
            ),
            answer_entity=EntityReference(name="Jane Doe", qid="Q2"),
            relation_or_claim="director",
            evidence=EvidenceRecord(
                text="Harbor Lights is a 2020 drama film directed by Jane Doe.",
                url="https://en.wikipedia.org/wiki/Harbor_Lights",
                source_title="Harbor Lights",
                retrieved_at="2026-05-12",
            ),
            question_family="who_directed_film",
            answer_type="Person",
            topic="Arts and Media",
            target_time="2020",
            source_template_domain="film_director",
            source_metadata={"stable_answer_override": True},
            source_candidate=source_candidate,
        )

        class TableRewriteClient:
            def rewrite_question(self, payload: dict) -> dict:
                return {
                    "rewritten_question": "Which table names the director of Harbor Lights?",
                    "search_queries": ["table director"],
                    "discard_reason": None,
                }

        with tempfile.TemporaryDirectory() as tmpdir:
            result = process_generated_candidates(
                [candidate],
                settings=Settings(
                    target_time="2020",
                    pilot_total=1,
                    output_path=Path(tmpdir) / "accepted.jsonl",
                    rejected_output_path=Path(tmpdir) / "rejected.jsonl",
                    rewrite_enabled=True,
                ),
                search_client=ErrorSearchClient(),
                rewrite_client=TableRewriteClient(),
            )

        self.assertEqual(result.accepted, [])
        self.assertEqual(result.rejected[0]["rejection_reason"], "rewrite_guard_rejected")
        self.assertEqual(
            result.rejected[0]["rejection_rule"],
            "post_rewrite_self_containment_forbidden_phrase:table",
        )

    def test_process_generated_candidates_rejects_infobox_marker_rewrite_before_search(self) -> None:
        candidate = make_route3_candidate(answer="Harbor Guild", answer_type="Other")

        class InfoboxRewriteClient:
            def rewrite_question(self, payload: dict) -> dict:
                return {
                    "rewritten_question": "Which infobox names the organization for Harbor Lights?",
                    "search_queries": ["infobox organization"],
                    "discard_reason": None,
                }

        with tempfile.TemporaryDirectory() as tmpdir:
            result = process_generated_candidates(
                [candidate],
                settings=Settings(
                    target_time="2020",
                    pilot_total=1,
                    output_path=Path(tmpdir) / "accepted.jsonl",
                    rejected_output_path=Path(tmpdir) / "rejected.jsonl",
                    rewrite_enabled=True,
                ),
                search_client=ErrorSearchClient(),
                rewrite_client=InfoboxRewriteClient(),
            )

        self.assertEqual(result.accepted, [])
        self.assertEqual(result.rejected[0]["rejection_reason"], "rewrite_guard_rejected")
        self.assertEqual(
            result.rejected[0]["rejection_rule"],
            "post_rewrite_self_containment_forbidden_phrase:infobox",
        )
        self.assertEqual(
            result.rejected[0]["source_metadata"]["post_rewrite_self_containment_failure_reason"],
            "post_rewrite_self_containment_forbidden_phrase:infobox",
        )

    def test_post_rewrite_answer_scope_ambiguity_uses_case_insensitive_word_boundaries(self) -> None:
        candidate = make_route3_candidate(answer="Jane Doe")
        cases = (
            ("AVERAGE score?", "post_rewrite_answer_scope_ambiguous_phrase:average"),
            ("What percentage voted yes?", "post_rewrite_answer_scope_ambiguous_phrase:percentage"),
            ("How is Harbor Lights classified?", "post_rewrite_answer_scope_ambiguous_phrase:classified"),
            (
                "WHAT   CATEGORY does Harbor Lights belong to?",
                "post_rewrite_answer_scope_ambiguous_phrase:what_category",
            ),
            (
                "What other name was Harbor Lights released under?",
                "post_rewrite_answer_scope_ambiguous_phrase:other_name",
            ),
            (
                "What translation of Harbor Lights won the prize?",
                "post_rewrite_answer_scope_ambiguous_phrase:translation",
            ),
            (
                "What transliteration is used for Harbor Lights?",
                "post_rewrite_answer_scope_ambiguous_phrase:transliteration",
            ),
            (
                "What is another name for Harbor Lights?",
                "post_rewrite_answer_scope_ambiguous_phrase:another_name",
            ),
            ("Who averaged the Harbor Lights reviews?", None),
            ("Who built the unclassified Harbor Lights archive?", None),
            ("Which translationist reviewed Harbor Lights?", None),
            ("Who used another naming scheme for Harbor Lights?", None),
        )
        for rewritten_question, expected_reason in cases:
            with self.subTest(rewritten_question=rewritten_question):
                candidate.rewritten_question = rewritten_question
                self.assertEqual(_post_rewrite_answer_scope_ambiguity_failure(candidate), expected_reason)

    def test_process_generated_candidates_rejects_answer_scope_ambiguous_rewrite_before_search(self) -> None:
        class ScopeRewriteClient:
            def __init__(self, rewritten_question: str) -> None:
                self.rewritten_question = rewritten_question

            def rewrite_question(self, payload: dict) -> dict:
                return {
                    "rewritten_question": self.rewritten_question,
                    "search_queries": ["ambiguous scope query"],
                    "discard_reason": None,
                }

        for marker, rewritten_question in (
            ("meaning", "What is the meaning of Harbor Lights?"),
            ("genre", "What genre is Harbor Lights?"),
            ("type", "What type of film is Harbor Lights?"),
            ("average", "What is the average rating of Harbor Lights?"),
            ("percentage", "What percentage of reviews praised Harbor Lights?"),
            ("classified", "How is Harbor Lights classified?"),
            ("what_category", "What category is Harbor Lights in?"),
            ("other_name", "What other name was Harbor Lights released under?"),
            ("translation", "What translation of Harbor Lights won the prize?"),
            ("transliteration", "What transliteration is used for Harbor Lights?"),
            ("another_name", "What is another name for Harbor Lights?"),
        ):
            with self.subTest(marker=marker):
                source_candidate = make_candidate()
                source_candidate.source_metadata["stable_answer_override"] = True
                candidate = GeneratedCandidate(
                    source_type="test",
                    generation_route="route2_wikidata_wikipedia_hybrid",
                    question="Who directed the film Harbor Lights?",
                    canonical_question="Who directed the film Harbor Lights?",
                    answer="Jane Doe",
                    answer_aliases=["J. Doe"],
                    subject_entity=EntityReference(
                        name="Harbor Lights",
                        qid="Q1",
                        wikipedia_title="Harbor_Lights",
                        url="https://en.wikipedia.org/wiki/Harbor_Lights",
                    ),
                    answer_entity=EntityReference(name="Jane Doe", qid="Q2"),
                    relation_or_claim="director",
                    evidence=EvidenceRecord(
                        text="Harbor Lights is a 2020 drama film directed by Jane Doe.",
                        url="https://en.wikipedia.org/wiki/Harbor_Lights",
                        source_title="Harbor Lights",
                        retrieved_at="2026-05-12",
                    ),
                    question_family="who_directed_film",
                    answer_type="Person",
                    topic="Arts and Media",
                    target_time="2020",
                    source_template_domain="film_director",
                    source_metadata={"stable_answer_override": True},
                    source_candidate=source_candidate,
                )

                with tempfile.TemporaryDirectory() as tmpdir:
                    result = process_generated_candidates(
                        [candidate],
                        settings=Settings(
                            target_time="2020",
                            pilot_total=1,
                            output_path=Path(tmpdir) / "accepted.jsonl",
                            rejected_output_path=Path(tmpdir) / "rejected.jsonl",
                            rewrite_enabled=True,
                        ),
                        search_client=ErrorSearchClient(),
                        rewrite_client=ScopeRewriteClient(rewritten_question),
                    )

                expected_reason = f"post_rewrite_answer_scope_ambiguous_phrase:{marker}"
                self.assertEqual(result.accepted, [])
                self.assertEqual(result.rejected[0]["rejection_reason"], "rewrite_guard_rejected")
                self.assertEqual(result.rejected[0]["rejection_rule"], expected_reason)
                self.assertEqual(
                    result.rejected[0]["source_metadata"]["post_rewrite_answer_scope_ambiguity_failure_reason"],
                    expected_reason,
                )

    def test_process_generated_candidates_rejects_time_invariant_rewrite_before_search(self) -> None:
        source_candidate = make_candidate()
        source_candidate.source_metadata["stable_answer_override"] = True
        candidate = GeneratedCandidate(
            source_type="test",
            generation_route="route2_wikidata_wikipedia_hybrid",
            question="Who directed the film Harbor Lights?",
            canonical_question="Who directed the film Harbor Lights?",
            answer="Jane Doe",
            answer_aliases=["J. Doe"],
            subject_entity=EntityReference(
                name="Harbor Lights",
                qid="Q1",
                wikipedia_title="Harbor_Lights",
                url="https://en.wikipedia.org/wiki/Harbor_Lights",
            ),
            answer_entity=EntityReference(name="Jane Doe", qid="Q2"),
            relation_or_claim="director",
            evidence=EvidenceRecord(
                text="Harbor Lights is a 2020 drama film directed by Jane Doe.",
                url="https://en.wikipedia.org/wiki/Harbor_Lights",
                source_title="Harbor Lights",
                retrieved_at="2026-05-12",
            ),
            question_family="who_directed_film",
            answer_type="Person",
            topic="Arts and Media",
            target_time="2020",
            source_template_domain="film_director",
            source_metadata={"stable_answer_override": True},
            source_candidate=source_candidate,
        )

        class LatestRewriteClient:
            def rewrite_question(self, payload: dict) -> dict:
                return {
                    "rewritten_question": "Who is the latest director associated with Harbor Lights?",
                    "search_queries": ["latest director"],
                    "discard_reason": None,
                }

        with tempfile.TemporaryDirectory() as tmpdir:
            result = process_generated_candidates(
                [candidate],
                settings=Settings(
                    target_time="2020",
                    pilot_total=1,
                    output_path=Path(tmpdir) / "accepted.jsonl",
                    rejected_output_path=Path(tmpdir) / "rejected.jsonl",
                    rewrite_enabled=True,
                ),
                search_client=ErrorSearchClient(),
                rewrite_client=LatestRewriteClient(),
            )

        self.assertEqual(result.accepted, [])
        self.assertEqual(result.rejected[0]["rejection_reason"], "rewrite_guard_rejected")
        self.assertEqual(
            result.rejected[0]["rejection_rule"],
            "post_rewrite_time_invariance_forbidden_phrase:latest",
        )
        self.assertEqual(
            result.rejected[0]["source_metadata"]["post_rewrite_time_invariance_failure_reason"],
            "post_rewrite_time_invariance_forbidden_phrase:latest",
        )

    def test_process_generated_candidates_rejects_award_what_year_without_month(self) -> None:
        source_candidate = make_candidate()
        source_candidate.source_metadata["stable_answer_override"] = True
        candidate = GeneratedCandidate(
            source_type="wikipedia_tables",
            generation_route="route3_wikipedia_infobox",
            question="In what year did Jane Doe win the ASCAP Award for Harbor Lights?",
            canonical_question="In what year did Jane Doe win the ASCAP Award for Harbor Lights?",
            answer="1997",
            answer_aliases=[],
            subject_entity=EntityReference(
                name="Harbor Lights",
                wikipedia_title="Harbor_Lights",
                url="https://en.wikipedia.org/wiki/Harbor_Lights",
            ),
            answer_entity=EntityReference(name="1997"),
            relation_or_claim="single_fact",
            evidence=EvidenceRecord(
                text="Jane Doe won the ASCAP Award in 1997.",
                url="https://en.wikipedia.org/wiki/Harbor_Lights",
                source_title="Harbor Lights",
                retrieved_at="2026-05-12",
            ),
            question_family="wikipedia_infobox_table_fact",
            answer_type="Date",
            topic="Wikipedia semi-structured data",
            target_time="2026",
            source_template_domain="wikipedia_infobox_table",
            source_metadata={"stable_answer_override": True},
            source_candidate=source_candidate,
        )

        class AwardRewriteClient:
            def rewrite_question(self, payload: dict) -> dict:
                return {
                    "rewritten_question": "In what year did Jane Doe win the ASCAP Award for Harbor Lights?",
                    "search_queries": ["Jane Doe ASCAP Award Harbor Lights"],
                    "discard_reason": None,
                }

        with tempfile.TemporaryDirectory() as tmpdir:
            result = process_generated_candidates(
                [candidate],
                settings=Settings(
                    target_time="2020",
                    pilot_total=1,
                    output_path=Path(tmpdir) / "accepted.jsonl",
                    rejected_output_path=Path(tmpdir) / "rejected.jsonl",
                    rewrite_enabled=True,
                ),
                search_client=ErrorSearchClient(),
                rewrite_client=AwardRewriteClient(),
            )

        self.assertEqual(result.accepted, [])
        self.assertEqual(result.rejected[0]["rejection_reason"], "rewrite_guard_rejected")
        self.assertEqual(result.rejected[0]["rejection_rule"], "post_rewrite_award_year_without_month")
        self.assertEqual(
            result.rejected[0]["source_metadata"]["post_rewrite_award_year_precision_failure_reason"],
            "post_rewrite_award_year_without_month",
        )

    def test_route3_rejects_exact_popular_answer_after_rewrite(self) -> None:
        candidate = make_route3_candidate(
            answer="United States",
            answer_type="Place",
            question="In which country was the Harbor Lights agreement signed?",
        )

        class CountryRewriteClient:
            def rewrite_question(self, payload: dict) -> dict:
                return {
                    "rewritten_question": "In which country was the Harbor Lights agreement signed?",
                    "search_queries": ["Harbor Lights agreement country"],
                    "discard_reason": None,
                }

        with tempfile.TemporaryDirectory() as tmpdir:
            result = process_generated_candidates(
                [candidate],
                settings=Settings(
                    target_time="2020",
                    pilot_total=1,
                    output_path=Path(tmpdir) / "accepted.jsonl",
                    rejected_output_path=Path(tmpdir) / "rejected.jsonl",
                    rewrite_enabled=True,
                ),
                search_client=ErrorSearchClient(),
                rewrite_client=CountryRewriteClient(),
            )

        self.assertEqual(result.accepted, [])
        self.assertEqual(result.rejected[0]["rejection_reason"], "rewrite_guard_rejected")
        self.assertEqual(result.rejected[0]["rejection_rule"], "answer_too_popular:United States")
        self.assertEqual(result.rejected[0]["failing_reason"], "answer_too_popular:United States")
        self.assertEqual(
            result.rejected[0]["source_metadata"]["post_rewrite_answer_popularity_failure_reason"],
            "answer_too_popular:United States",
        )

    def test_route3_rejects_popular_continent_ocean_and_city_answers(self) -> None:
        for answer in (
            "People's Republic of China",
            "Asia",
            "Pacific Ocean",
            "New York",
            "New York City",
            "Los Angeles",
        ):
            with self.subTest(answer=answer):
                candidate = make_route3_candidate(
                    answer=answer,
                    answer_type="Place",
                    question="In which place was the Harbor Lights agreement signed?",
                )

                with tempfile.TemporaryDirectory() as tmpdir:
                    result = process_generated_candidates(
                        [candidate],
                        settings=Settings(
                            target_time="2020",
                            pilot_total=1,
                            output_path=Path(tmpdir) / "accepted.jsonl",
                            rejected_output_path=Path(tmpdir) / "rejected.jsonl",
                        ),
                        search_client=ErrorSearchClient(),
                        rewrite_client=None,
                    )

                self.assertEqual(result.accepted, [])
                self.assertEqual(result.rejected[0]["rejection_reason"], "rewrite_guard_rejected")
                self.assertEqual(result.rejected[0]["rejection_rule"], f"answer_too_popular:{answer}")

    def test_route3_popular_answer_marker_list_includes_global_places(self) -> None:
        expected = {
            "Africa",
            "Antarctica",
            "Asia",
            "Australia",
            "People's Republic of China",
            "Europe",
            "North America",
            "Oceania",
            "South America",
            "Arctic Ocean",
            "Atlantic Ocean",
            "Indian Ocean",
            "Pacific Ocean",
            "Southern Ocean",
            "New York",
            "New York City",
            "London",
            "Paris",
            "Tokyo",
            "Beijing",
            "Los Angeles",
        }

        self.assertTrue(expected.issubset(set(ROUTE3_POPULAR_EXACT_ANSWERS)))

    def test_route3_popular_answer_guard_requires_exact_answer_match(self) -> None:
        for answer in ("United States Postal Service", "China (band)"):
            with self.subTest(answer=answer):
                candidate = make_route3_candidate(answer=answer)

                with tempfile.TemporaryDirectory() as tmpdir:
                    result = process_generated_candidates(
                        [candidate],
                        settings=Settings(
                            target_time="2020",
                            pilot_total=1,
                            output_path=Path(tmpdir) / "accepted.jsonl",
                            rejected_output_path=Path(tmpdir) / "rejected.jsonl",
                        ),
                        search_client=FakeSearchClient({}),
                        rewrite_client=None,
                    )

                self.assertEqual(len(result.accepted), 1)
                self.assertEqual(result.accepted[0]["answer"], answer)
                self.assertNotIn(
                    "post_rewrite_answer_popularity_failure_reason",
                    result.accepted[0]["source_metadata"],
                )

    def test_route1_rewrite_payload_uses_triplet_text_contract(self) -> None:
        source_candidate = make_candidate()
        source_candidate.source_metadata["stable_answer_override"] = True
        candidate = GeneratedCandidate(
            source_type="wikidata",
            generation_route="route1_wikidata_light",
            question="Who directed the film Example Film?",
            canonical_question="Who directed the film Example Film?",
            answer="Jane Doe",
            answer_aliases=["J. Doe"],
            subject_entity=EntityReference(
                name="Example Film",
                qid="Q1",
                wikipedia_title="Example_Film",
                url="https://en.wikipedia.org/wiki/Example_Film",
            ),
            answer_entity=EntityReference(name="Jane Doe", qid="Q2"),
            relation_or_claim="director",
            evidence=EvidenceRecord(
                text="Example Film director Jane Doe",
                url="https://en.wikipedia.org/wiki/Example_Film",
                source_title="Example Film",
                retrieved_at="2026-05-13",
            ),
            question_family="who_directed_film",
            answer_type="Person",
            topic="Arts and Media",
            target_time="2020",
            source_template_domain="film_director",
            source_metadata={"stable_answer_override": True},
            source_candidate=source_candidate,
        )
        captured_payloads: list[dict] = []

        class CaptureRewriteClient:
            def rewrite_question(self, payload: dict) -> dict:
                captured_payloads.append(dict(payload))
                return {
                    "rewritten_question": "Who directed Example Film according to rewrite director?",
                    "search_queries": ["Example Film production history"],
                    "answer_aliases": [],
                    "discard_reason": None,
                }

        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(
                target_time="2020",
                pilot_total=1,
                output_path=Path(tmpdir) / "accepted.jsonl",
                rejected_output_path=Path(tmpdir) / "rejected.jsonl",
                rewrite_enabled=True,
            )
            process_generated_candidates(
                [candidate],
                settings=settings,
                search_client=FakeSearchClient(
                    {
                        "Who directed Example Film according to rewrite director?": [],
                        "Example Film production history": [],
                    }
                ),
                rewrite_client=CaptureRewriteClient(),
            )
        self.assertEqual(captured_payloads[0]["task_type"], "route1_question_and_queries")
        self.assertEqual(
            captured_payloads[0]["wikidata_triplet_text"],
            "Example Film -- director -- Jane Doe",
        )

    def test_process_generated_candidates_rejects_multi_hop_rewrite_that_drops_required_clue(self) -> None:
        source_candidate = make_candidate()
        source_candidate.source_metadata["stable_answer_override"] = True
        source_candidate.reasoning_style = "multi_hop_join"
        source_candidate.hop_count = 2
        source_candidate.reasoning_path = [
            {
                "source_qid": "Q1",
                "source_label": "Naomi C Futhey",
                "property_pid": "P69",
                "property_label": "educated at",
                "target_qid": "Q2",
                "target_label": "University of British Columbia",
                "role": "bridge",
                "qualifiers": {"P512": "Q913404", "P582": "2026-04-01"},
            },
            {
                "source_qid": "Q2",
                "source_label": "University of British Columbia",
                "property_pid": "DERIVED_FIRST_DEGREE_SELECTION",
                "property_label": "first degree selection",
                "target_qid": "Q2",
                "target_label": "University of British Columbia",
                "role": "answer",
            },
        ]
        source_candidate.bridge_entities = [
            {"qid": "Q2", "label": "University of British Columbia", "role": "university"}
        ]
        source_candidate.source_metadata["required_reasoning_clues"] = ["first degree"]
        candidate = GeneratedCandidate(
            source_type="test",
            generation_route="route2_wikidata_wikipedia_hybrid",
            question="From which university did Naomi C Futhey receive a first degree?",
            canonical_question="From which university did Naomi C Futhey receive a first degree?",
            answer="University of British Columbia",
            answer_aliases=[],
            subject_entity=EntityReference(
                name="Naomi C Futhey",
                qid="Q96429409",
                wikipedia_title="Naomi_C_Futhey",
                url="https://www.wikidata.org/wiki/Q96429409",
            ),
            answer_entity=EntityReference(name="University of British Columbia", qid="Q391028"),
            relation_or_claim="first degree university",
            evidence=EvidenceRecord(
                text="Naomi C Futhey studied medicine at the University of British Columbia.",
                url="https://example.test/naomi",
                source_title="Naomi C Futhey",
                retrieved_at="2026-05-15",
            ),
            question_family="which_university_first_degree",
            answer_type="Organization",
            topic="People",
            target_time="2026",
            source_template_domain="person_first_degree_university",
            source_metadata={"stable_answer_override": True},
            source_candidate=source_candidate,
        )

        class BadRewriteClient:
            def rewrite_question(self, payload: dict) -> dict:
                return {
                    "rewritten_question": "From which university did Naomi C Futhey earn her Doctor of Medicine degree?",
                    "search_queries": ["Naomi C Futhey medical degree institution"],
                    "answer_aliases": ["UBC"],
                    "discard_reason": None,
                }

        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(
                target_time="2026",
                pilot_total=1,
                output_path=Path(tmpdir) / "accepted.jsonl",
                rejected_output_path=Path(tmpdir) / "rejected.jsonl",
                rewrite_enabled=True,
            )
            result = process_generated_candidates(
                [candidate],
                settings=settings,
                search_client=FakeSearchClient({}),
                rewrite_client=BadRewriteClient(),
            )
        self.assertEqual(result.accepted, [])
        self.assertEqual(result.rejected[0]["rejection_reason"], "rewrite_guard_rejected")
        self.assertEqual(result.rejected[0]["rejection_rule"], "lost_required_reasoning_clue")
        self.assertEqual(result.rejected[0]["rejection_notes"]["failure_reason"], "lost_required_reasoning_clue")
        self.assertEqual(
            result.rejected[0]["source_metadata"]["surface_validation_failure_reason"],
            "lost_required_reasoning_clue",
        )


    def test_route3_processing_stage_order_is_fixed(self) -> None:
        candidate = make_route3_candidate(answer="Archive Guild")
        calls: list[str] = []

        def surface_check(*args, **kwargs):
            calls.append("surface_time")
            return None

        def answer_type_gate(*args, **kwargs):
            calls.append("answer_type_gate")
            return RuleBasedAnswerTypeGateResult(
                matched=True,
                answer_type="Other",
                details={"rule": "no_rule_for_answer_type"},
            )

        def answer_validation(*args, **kwargs):
            calls.append("answer_in_selected_table")
            return True, {
                "answer_in_evidence": True,
                "route_validation_policy": "answer_in_selected_table",
            }

        def duckduckgo(*args, **kwargs):
            calls.append("duckduckgo")
            return True, {"queries": []}

        def second_stage(*args, **kwargs):
            calls.append("second_stage")
            return {
                "enabled": True,
                "accuracy": 0.0,
                "models": [],
            }

        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(
                target_time="2020",
                pilot_total=1,
                output_path=Path(tmpdir) / "accepted.jsonl",
                rejected_output_path=Path(tmpdir) / "rejected.jsonl",
                second_stage_grading_enabled=True,
            )
            with (
                patch(
                    "wikidata_simpleqa.generation_pipeline.validate_question_surface",
                    side_effect=surface_check,
                ),
                patch(
                    "wikidata_simpleqa.generation_pipeline.evaluate_candidate_answer_type_gate",
                    side_effect=answer_type_gate,
                ),
                patch(
                    "wikidata_simpleqa.generation_pipeline.validate_generated_candidate",
                    side_effect=answer_validation,
                ),
                patch(
                    "wikidata_simpleqa.generation_pipeline.run_search_based_longtail_verifier",
                    side_effect=duckduckgo,
                ),
                patch(
                    "wikidata_simpleqa.generation_pipeline.evaluate_model_panel",
                    side_effect=second_stage,
                ),
            ):
                result = process_generated_candidates(
                    [candidate],
                    settings=settings,
                    search_client=FakeSearchClient({}),
                    second_stage_model_clients=[object()],
                    grading_grader_client=object(),
                )

        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(
            calls,
            [
                "surface_time",
                "answer_type_gate",
                "answer_in_selected_table",
                "duckduckgo",
                "second_stage",
            ],
        )

    def test_route3_unexpected_search_exception_propagates(self) -> None:
        candidate = make_route3_candidate(answer="Archive Guild")

        class UnexpectedVerifierStore:
            def verify(self, *args, **kwargs):
                raise ValueError("corrupt verifier state")

        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(
                target_time="2020",
                pilot_total=1,
                output_path=Path(tmpdir) / "accepted.jsonl",
                rejected_output_path=Path(tmpdir) / "rejected.jsonl",
            )
            with (
                patch("wikidata_simpleqa.generation_pipeline.validate_question_surface", return_value=None),
                patch(
                    "wikidata_simpleqa.generation_pipeline.evaluate_candidate_answer_type_gate",
                    return_value=RuleBasedAnswerTypeGateResult(
                        matched=True,
                        answer_type="Other",
                        details={"rule": "no_rule_for_answer_type"},
                    ),
                ),
                patch(
                    "wikidata_simpleqa.generation_pipeline.validate_generated_candidate",
                    return_value=(True, {"answer_in_evidence": True}),
                ),
            ):
                with self.assertRaisesRegex(ValueError, "corrupt verifier state"):
                    process_generated_candidates(
                        [candidate],
                        settings=settings,
                        search_client=FakeSearchClient({}),
                        ddg_verifier_result_store=UnexpectedVerifierStore(),
                    )

    def test_route3_unexpected_second_stage_exception_propagates(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(
                target_time="2020",
                pilot_total=1,
                output_path=Path(tmpdir) / "accepted.jsonl",
                rejected_output_path=Path(tmpdir) / "rejected.jsonl",
                second_stage_grading_enabled=True,
            )
            candidate = make_route3_candidate(answer="Archive Guild")
            with (
                patch("wikidata_simpleqa.generation_pipeline.validate_question_surface", return_value=None),
                patch(
                    "wikidata_simpleqa.generation_pipeline.evaluate_candidate_answer_type_gate",
                    return_value=RuleBasedAnswerTypeGateResult(
                        matched=True,
                        answer_type="Other",
                        details={"rule": "no_rule_for_answer_type"},
                    ),
                ),
                patch(
                    "wikidata_simpleqa.generation_pipeline.validate_generated_candidate",
                    return_value=(True, {"answer_in_evidence": True}),
                ),
                patch(
                    "wikidata_simpleqa.generation_pipeline.run_search_based_longtail_verifier",
                    return_value=(True, {"queries": []}),
                ),
                patch(
                    "wikidata_simpleqa.generation_pipeline.evaluate_model_panel",
                    side_effect=RuntimeError("panel implementation bug"),
                ),
            ):
                with self.assertRaisesRegex(RuntimeError, "panel implementation bug"):
                    process_generated_candidates(
                        [candidate],
                        settings=settings,
                        search_client=FakeSearchClient({}),
                        second_stage_model_clients=[object()],
                        grading_grader_client=object(),
                    )

    def test_route3_persisted_unparseable_second_stage_response_rejects_slot(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(
                target_time="2020",
                pilot_total=1,
                output_path=Path(tmpdir) / "accepted.jsonl",
                rejected_output_path=Path(tmpdir) / "rejected.jsonl",
                second_stage_grading_enabled=True,
            )
            candidate = make_route3_candidate(answer="Archive Guild")
            error = DefiniteOpenRouterResponseError(
                call_key="slot/second-stage",
                request_hash="request-hash",
                error=ValueError("invalid JSON"),
            )
            with (
                patch("wikidata_simpleqa.generation_pipeline.validate_question_surface", return_value=None),
                patch(
                    "wikidata_simpleqa.generation_pipeline.evaluate_candidate_answer_type_gate",
                    return_value=RuleBasedAnswerTypeGateResult(
                        matched=True,
                        answer_type="Other",
                        details={"rule": "no_rule_for_answer_type"},
                    ),
                ),
                patch(
                    "wikidata_simpleqa.generation_pipeline.validate_generated_candidate",
                    return_value=(True, {"answer_in_evidence": True}),
                ),
                patch(
                    "wikidata_simpleqa.generation_pipeline.run_search_based_longtail_verifier",
                    return_value=(True, {"queries": []}),
                ),
                patch("wikidata_simpleqa.generation_pipeline.evaluate_model_panel", side_effect=error),
            ):
                result = process_generated_candidates(
                    [candidate],
                    settings=settings,
                    search_client=FakeSearchClient({}),
                    second_stage_model_clients=[object()],
                    grading_grader_client=object(),
                )

        self.assertEqual(result.accepted, [])
        self.assertEqual(result.rejected[0]["rejection_reason"], "second_stage_unparseable_response")
        self.assertEqual(result.rejected[0]["rejection_notes"]["call_key"], "slot/second-stage")

    def test_route3_nonretryable_second_stage_http_error_rejects_slot(self) -> None:
        error = DefiniteOpenRouterHTTPError(
            call_key="slot/second-stage",
            request_hash="request-hash",
            status_code=403,
            body_text="forbidden",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(
                target_time="2020",
                pilot_total=1,
                output_path=Path(tmpdir) / "accepted.jsonl",
                rejected_output_path=Path(tmpdir) / "rejected.jsonl",
                second_stage_grading_enabled=True,
            )
            with (
                patch("wikidata_simpleqa.generation_pipeline.validate_question_surface", return_value=None),
                patch(
                    "wikidata_simpleqa.generation_pipeline.evaluate_candidate_answer_type_gate",
                    return_value=RuleBasedAnswerTypeGateResult(
                        matched=True,
                        answer_type="Other",
                        details={},
                    ),
                ),
                patch(
                    "wikidata_simpleqa.generation_pipeline.validate_generated_candidate",
                    return_value=(True, {"answer_in_evidence": True}),
                ),
                patch(
                    "wikidata_simpleqa.generation_pipeline.run_search_based_longtail_verifier",
                    return_value=(True, {"queries": []}),
                ),
                patch("wikidata_simpleqa.generation_pipeline.evaluate_model_panel", side_effect=error),
            ):
                result = process_generated_candidates(
                    [make_route3_candidate(answer="Archive Guild")],
                    settings=settings,
                    search_client=FakeSearchClient({}),
                    second_stage_model_clients=[object()],
                    grading_grader_client=object(),
                )

        self.assertEqual(result.rejected[0]["rejection_reason"], "openrouter_http_error:403")

    def test_process_generated_candidates_rejects_when_search_verifier_errors(self) -> None:
        source_candidate = make_candidate()
        source_candidate.source_metadata["stable_answer_override"] = True
        candidate = GeneratedCandidate(
            source_type="test",
            generation_route="route2_wikidata_wikipedia_hybrid",
            question="Who directed the film Example Film?",
            canonical_question="Who directed the film Example Film?",
            answer="Jane Doe",
            answer_aliases=["J. Doe"],
            subject_entity=EntityReference(
                name="Example Film",
                qid="Q1",
                wikipedia_title="Example_Film",
                url="https://en.wikipedia.org/wiki/Example_Film",
            ),
            answer_entity=EntityReference(name="Jane Doe", qid="Q2"),
            relation_or_claim="director",
            evidence=EvidenceRecord(
                text="Example Film is a 2020 drama film directed by Jane Doe.",
                url="https://en.wikipedia.org/wiki/Example_Film",
                source_title="Example Film",
                retrieved_at="2026-05-13",
            ),
            question_family="who_directed_film",
            answer_type="Person",
            topic="Arts and Media",
            target_time="2020",
            source_template_domain="film_director",
            source_metadata={
                "subject_wikipedia_title": "Example_Film",
                "subject_wikipedia_url": "https://en.wikipedia.org/wiki/Example_Film",
                "subject_sitelink_count": 12,
                "subject_claim_count": 44,
                "stable_answer_override": True,
            },
            source_candidate=source_candidate,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(
                target_time="2020",
                pilot_total=1,
                output_path=Path(tmpdir) / "accepted.jsonl",
                rejected_output_path=Path(tmpdir) / "rejected.jsonl",
            )
            result = process_generated_candidates(
                [candidate],
                settings=settings,
                search_client=ErrorSearchClient(),
                rewrite_client=None,
        )
        self.assertEqual(result.accepted, [])
        self.assertEqual(result.rejected[0]["rejection_reason"], "search_longtail_verifier_error")
        notes = result.rejected[0]["rejection_notes"]
        self.assertEqual(notes["error_type"], "RuntimeError")
        features = notes["search_verification_features"]
        self.assertTrue(features["triggered_rule"].endswith(":query_error"))
        self.assertTrue(features["query_errors"][0]["query_name"])
        self.assertEqual(features["query_errors"][0]["error_type"], "RuntimeError")
        self.assertIn("duration_seconds", features["query_errors"][0])

    def test_shared_validation_runs_before_search_longtail_verifier(self) -> None:
        source_candidate = make_candidate()
        source_candidate.source_metadata["stable_answer_override"] = True
        candidate = GeneratedCandidate(
            source_type="test",
            generation_route="route2_wikidata_wikipedia_hybrid",
            question="Who directed the film Example Film?",
            canonical_question="Who directed the film Example Film?",
            answer="Jane Doe",
            answer_aliases=[],
            subject_entity=EntityReference(
                name="Example Film",
                qid="Q1",
                wikipedia_title="Example_Film",
                url="https://en.wikipedia.org/wiki/Example_Film",
            ),
            answer_entity=EntityReference(name="Jane Doe", qid="Q2"),
            relation_or_claim="director",
            evidence=EvidenceRecord(
                text="Example Film is a 2020 drama film.",
                url="https://en.wikipedia.org/wiki/Example_Film",
                source_title="Example Film",
                retrieved_at="2026-05-13",
            ),
            question_family="who_directed_film",
            answer_type="Person",
            topic="Arts and Media",
            target_time="2020",
            source_template_domain="film_director",
            source_metadata={
                "subject_wikipedia_title": "Example_Film",
                "subject_wikipedia_url": "https://en.wikipedia.org/wiki/Example_Film",
                "stable_answer_override": True,
            },
            source_candidate=source_candidate,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(
                target_time="2020",
                pilot_total=1,
                output_path=Path(tmpdir) / "accepted.jsonl",
                rejected_output_path=Path(tmpdir) / "rejected.jsonl",
            )
            result = process_generated_candidates(
                [candidate],
                settings=settings,
                search_client=ErrorSearchClient(),
                rewrite_client=None,
            )
        self.assertEqual(result.accepted, [])
        self.assertEqual(result.rejected[0]["rejection_reason"], "shared_validation_failed")
        self.assertFalse(result.rejected[0]["rejection_notes"]["validation"]["answer_in_evidence"])
        self.assertNotIn("duckduckgo_search_seconds", result.rejected[0]["source_metadata"]["phase_timings_seconds"])

    def test_rule_based_answer_type_gate_runs_before_search_longtail_verifier(self) -> None:
        source_candidate = make_candidate()
        source_candidate.source_metadata["stable_answer_override"] = True
        candidate = GeneratedCandidate(
            source_type="test",
            generation_route="route3_wikipedia_infobox",
            question="At which awards ceremony did Example Artist win the Best International Album award?",
            canonical_question="At which awards ceremony did Example Artist win the Best International Album award?",
            answer="Brit Awards",
            answer_aliases=[],
            subject_entity=EntityReference(
                name="Example Artist",
                qid="Q1",
                wikipedia_title="Example_Artist",
                url="https://en.wikipedia.org/wiki/Example_Artist",
            ),
            answer_entity=EntityReference(name="Brit Awards", qid="Q2"),
            relation_or_claim="award received",
            evidence=EvidenceRecord(
                text="Example Artist won Best International Album at the Brit Awards.",
                url="https://en.wikipedia.org/wiki/Example_Artist",
                source_title="Example Artist",
                retrieved_at="2026-05-13",
            ),
            question_family="route3_single_fact",
            answer_type="Place",
            topic="Arts and Media",
            target_time="2020",
            source_template_domain="route3_table",
            source_metadata={
                "stable_answer_override": True,
            },
            source_candidate=source_candidate,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(
                target_time="2020",
                pilot_total=1,
                output_path=Path(tmpdir) / "accepted.jsonl",
                rejected_output_path=Path(tmpdir) / "rejected.jsonl",
            )
            result = process_generated_candidates(
                [candidate],
                settings=settings,
                search_client=ErrorSearchClient(),
                rewrite_client=None,
            )

        self.assertEqual(result.accepted, [])
        self.assertEqual(result.rejected[0]["rejection_reason"], "rule_based_answer_type_gate_rejected")
        gate = result.rejected[0]["source_metadata"]["rule_based_qa_gate"]
        self.assertEqual(gate["details"]["extracted_category"], "awards ceremony")
        self.assertFalse(result.rejected[0]["source_metadata"]["rule_answer_type_match"])
        self.assertNotIn("duckduckgo_search_seconds", result.rejected[0]["source_metadata"]["phase_timings_seconds"])

    def test_rule_based_date_gate_normalizes_answer_before_acceptance(self) -> None:
        source_candidate = make_candidate()
        source_candidate.source_metadata["stable_answer_override"] = True
        candidate = GeneratedCandidate(
            source_type="test",
            generation_route="route3_wikipedia_infobox",
            question="What month and year did the Example venue open?",
            canonical_question="What month and year did the Example venue open?",
            answer="03-1940",
            answer_aliases=[],
            subject_entity=EntityReference(
                name="Example venue",
                qid="Q1",
                wikipedia_title="Example_venue",
                url="https://en.wikipedia.org/wiki/Example_venue",
            ),
            answer_entity=EntityReference(name="03-1940", qid=""),
            relation_or_claim="opened",
            evidence=EvidenceRecord(
                text="The Example venue opened in 03-1940.",
                url="https://en.wikipedia.org/wiki/Example_venue",
                source_title="Example venue",
                retrieved_at="2026-05-13",
            ),
            question_family="route3_single_fact",
            answer_type="Date",
            topic="Architecture and Transportation",
            target_time="2020",
            source_template_domain="route3_table",
            source_metadata={
                "stable_answer_override": True,
            },
            source_candidate=source_candidate,
        )
        search_client = FakeSearchClient({"What month and year did the Example venue open?": []})
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(
                target_time="2020",
                pilot_total=1,
                output_path=Path(tmpdir) / "accepted.jsonl",
                rejected_output_path=Path(tmpdir) / "rejected.jsonl",
            )
            result = process_generated_candidates(
                [candidate],
                settings=settings,
                search_client=search_client,
                rewrite_client=None,
            )

        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(result.accepted[0]["answer"], "March 1940")
        gate = result.accepted[0]["source_metadata"]["rule_based_qa_gate"]
        self.assertEqual(gate["details"]["normalized_answer"], "March 1940")
        self.assertTrue(result.accepted[0]["source_metadata"]["rule_answer_type_match"])

    def test_process_generated_candidates_records_removed_cheap_model_rejection_phase(self) -> None:
        source_candidate = make_candidate()
        source_candidate.source_metadata["stable_answer_override"] = True
        candidate = GeneratedCandidate(
            source_type="test",
            generation_route="route2_wikidata_wikipedia_hybrid",
            question="Who directed the film Example Film?",
            canonical_question="Who directed the film Example Film?",
            answer="Jane Doe",
            answer_aliases=["J. Doe"],
            subject_entity=EntityReference(
                name="Example Film",
                qid="Q1",
                wikipedia_title="Example_Film",
                url="https://en.wikipedia.org/wiki/Example_Film",
            ),
            answer_entity=EntityReference(name="Jane Doe", qid="Q2"),
            relation_or_claim="director",
            evidence=EvidenceRecord(
                text="Example Film is a 2020 drama film directed by Jane Doe.",
                url="https://en.wikipedia.org/wiki/Example_Film",
                source_title="Example Film",
                retrieved_at="2026-05-13",
            ),
            question_family="who_directed_film",
            answer_type="Person",
            topic="Arts and Media",
            target_time="2020",
            source_template_domain="film_director",
            source_metadata={
                "subject_wikipedia_title": "Example_Film",
                "subject_wikipedia_url": "https://en.wikipedia.org/wiki/Example_Film",
                "subject_sitelink_count": 12,
                "subject_claim_count": 44,
                "stable_answer_override": True,
            },
            source_candidate=source_candidate,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(
                target_time="2020",
                pilot_total=1,
                output_path=Path(tmpdir) / "accepted.jsonl",
                rejected_output_path=Path(tmpdir) / "rejected.jsonl",
            )
            result = process_generated_candidates(
                [candidate],
                settings=settings,
                search_client=FakeSearchClient(
                    {
                        "Who directed the film Example Film?": [],
                        "Example Film director": [],
                        "Example Film director Jane Doe": [],
                    }
                ),
                rewrite_client=None,
            )
        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(result.accepted[0]["cheap_model_verification_features"]["enabled"], False)
        self.assertEqual(
            result.accepted[0]["cheap_model_verification_features"]["reason"],
            "cheap_model_longtail_rejection_removed_for_simpleqa_verified_alignment",
        )

    def test_number_reference_margin_runs_before_search_without_cheap_model_rejection(self) -> None:
        source_candidate = make_candidate()
        source_candidate.source_metadata["stable_answer_override"] = True
        candidate = GeneratedCandidate(
            source_type="test",
            generation_route="route2_wikidata_wikipedia_hybrid",
            question="What is the chapter count of Example Film?",
            canonical_question="What is the chapter count of Example Film?",
            answer="100",
            answer_aliases=[],
            subject_entity=EntityReference(
                name="Example Film",
                qid="Q1",
                wikipedia_title="Example_Film",
                url="https://en.wikipedia.org/wiki/Example_Film",
            ),
            answer_entity=EntityReference(name="100"),
            relation_or_claim="chapter count",
            evidence=EvidenceRecord(
                text="Example Film has 100 chapters.",
                url="https://example.test/score",
                source_title="Example Film",
                retrieved_at="2026-05-15",
            ),
            question_family="how_many_chapters",
            answer_type="Number",
            topic="Tests",
            target_time="2020",
            source_template_domain="example_score",
            source_metadata={
                "stable_answer_override": True,
            },
            source_candidate=source_candidate,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(
                target_time="2020",
                pilot_total=1,
                output_path=Path(tmpdir) / "accepted.jsonl",
                rejected_output_path=Path(tmpdir) / "rejected.jsonl",
            )
            result = process_generated_candidates(
                [candidate],
                settings=settings,
                search_client=FakeSearchClient(
                    {
                        "What is the chapter count of Example Film?": [],
                        "Example Film chapter count": [],
                        "Example Film chapter count 100": [],
                    }
                ),
                rewrite_client=None,
            )
        self.assertEqual(len(result.accepted), 1)
        margin = result.accepted[0]["source_metadata"]["number_reference_margin"]
        self.assertEqual(margin["reference_answer"], "100 (acceptable range: anything between 99 and 101)")
        cheap_features = result.accepted[0]["cheap_model_verification_features"]
        self.assertFalse(cheap_features["enabled"])
        self.assertEqual(
            cheap_features["reason"],
            "cheap_model_longtail_rejection_removed_for_simpleqa_verified_alignment",
        )

    def test_number_reference_margin_is_disabled_for_mislabeled_year_answers(self) -> None:
        candidate = GeneratedCandidate(
            source_type="test",
            generation_route="route3_wikipedia_infobox",
            question="What year had the highest number of viewers for the Academy Awards?",
            canonical_question="What year had the highest number of viewers for the Academy Awards?",
            answer="1998",
            answer_aliases=[],
            subject_entity=EntityReference(name="Academy Awards"),
            answer_entity=EntityReference(name="1998"),
            relation_or_claim="max",
            evidence=EvidenceRecord(text="1998 had the highest viewership."),
            answer_type="Number",
            source_metadata={},
        )

        _apply_number_reference_margin(candidate)

        margin = candidate.source_metadata["number_reference_margin"]
        self.assertFalse(margin["enabled"])
        self.assertEqual(margin["reason"], "temporal_question_year_answer_should_use_date_type")

    def test_route3_rewrite_payload_does_not_include_first_paragraph(self) -> None:
        candidate = GeneratedCandidate(
            source_type="test",
            generation_route="route3_wikipedia_infobox",
            question="Which stadium hosting the 23rd FIFA World Cup has the largest capacity?",
            canonical_question="Which stadium hosting the 23rd FIFA World Cup has the largest capacity?",
            answer="AT&T Stadium",
            answer_aliases=[],
            subject_entity=EntityReference(name="2026 FIFA World Cup"),
            answer_entity=EntityReference(name="AT&T Stadium"),
            relation_or_claim="max",
            evidence=EvidenceRecord(text="Venue | Capacity\nAT&T Stadium | 80000"),
            answer_type="Entity",
            source_metadata={"first_paragraph": "The 2026 FIFA World Cup is the 23rd FIFA World Cup."},
        )

        payload = _build_route_rewrite_payload(
            candidate,
            cutoff_year=2025,
            forbidden_patterns=["current"],
            search_query_count=3,
        )

        self.assertEqual(payload["task_type"], "generic_question_and_queries")
        self.assertNotIn("first_paragraph", payload)
        self.assertNotIn("evidence_text", payload)

    def test_route1_multihop_rewrite_payload_includes_reasoning_contract(self) -> None:
        source_candidate = make_candidate()
        source_candidate.reasoning_style = "multi_hop_join"
        source_candidate.hop_count = 2
        source_candidate.reasoning_path = [
            {
                "source_qid": "Q1",
                "source_label": "Example Film",
                "property_pid": "P144",
                "property_label": "based on",
                "target_qid": "Q3",
                "target_label": "Source Work",
                "role": "bridge",
            },
            {
                "source_qid": "Q3",
                "source_label": "Source Work",
                "property_pid": "P50",
                "property_label": "author",
                "target_qid": "Q2",
                "target_label": "Jane Doe",
                "role": "answer",
            },
        ]
        source_candidate.bridge_entities = [{"qid": "Q3", "label": "Source Work", "role": "source_work"}]
        source_candidate.source_metadata["required_reasoning_clues"] = ["based on"]
        candidate = GeneratedCandidate(
            source_type="wikidata",
            generation_route="route1_wikidata_multihop_join",
            question="Who wrote the work that the film Example Film was based on?",
            canonical_question="Who wrote the work that the film Example Film was based on?",
            answer="Jane Doe",
            answer_aliases=[],
            subject_entity=EntityReference(name="Example Film", qid="Q1"),
            answer_entity=EntityReference(name="Jane Doe", qid="Q2"),
            relation_or_claim="author of source work",
            evidence=EvidenceRecord(text="Example Film -- based on -- Source Work; Source Work -- author -- Jane Doe"),
            answer_type="Person",
            source_template_domain="film_source_work_author",
            source_candidate=source_candidate,
        )

        payload = _build_route_rewrite_payload(
            candidate,
            cutoff_year=2025,
            forbidden_patterns=["current"],
            search_query_count=2,
        )

        self.assertEqual(payload["task_type"], "route1_question_and_queries")
        self.assertEqual(payload["route_contract"], "route1_qid_first_multihop_join")
        self.assertEqual(payload["reasoning_style"], "multi_hop_join")
        self.assertEqual(payload["required_reasoning_clues"], ["based on"])
        self.assertEqual(payload["bridge_entities"][0]["label"], "Source Work")


    def test_process_generated_candidates_records_second_stage_panel_accuracy(self) -> None:
        source_candidate = make_candidate()
        source_candidate.source_metadata["stable_answer_override"] = True
        candidate = GeneratedCandidate(
            source_type="test",
            generation_route="route2_wikidata_wikipedia_hybrid",
            question="Who directed the film Example Film?",
            canonical_question="Who directed the film Example Film?",
            answer="Jane Doe",
            answer_aliases=["J. Doe"],
            subject_entity=EntityReference(
                name="Example Film",
                qid="Q1",
                wikipedia_title="Example_Film",
                url="https://en.wikipedia.org/wiki/Example_Film",
            ),
            answer_entity=EntityReference(name="Jane Doe", qid="Q2"),
            relation_or_claim="director",
            evidence=EvidenceRecord(
                text="Example Film is a 2020 drama film directed by Jane Doe.",
                url="https://en.wikipedia.org/wiki/Example_Film",
                source_title="Example Film",
                retrieved_at="2026-05-13",
            ),
            question_family="who_directed_film",
            answer_type="Person",
            topic="Arts and Media",
            target_time="2020",
            source_template_domain="film_director",
            source_metadata={
                "subject_wikipedia_title": "Example_Film",
                "subject_wikipedia_url": "https://en.wikipedia.org/wiki/Example_Film",
                "subject_sitelink_count": 12,
                "subject_claim_count": 44,
                "stable_answer_override": True,
            },
            source_candidate=source_candidate,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(
                target_time="2020",
                pilot_total=1,
                output_path=Path(tmpdir) / "accepted.jsonl",
                rejected_output_path=Path(tmpdir) / "rejected.jsonl",
                second_stage_grading_enabled=True,
                second_stage_grading_accuracy_threshold=0.5,
                second_stage_grading_grader_llm=None,
            )
            result = process_generated_candidates(
                [candidate],
                settings=settings,
                search_client=FakeSearchClient(
                    {
                        "Who directed the film Example Film?": [],
                        "Example Film director": [],
                        "Example Film director Jane Doe": [],
                    }
                ),
                second_stage_model_clients=[
                    ModelPanelMember("openai/gpt-5.4-mini", FakePanelModelClient("Jane Doe")),
                    ModelPanelMember("google/gemini-3-flash-preview", FakePanelModelClient("John Smith")),
                ],
                grading_grader_client=FakePanelGraderClient(),
                rewrite_client=None,
            )
        self.assertEqual(len(result.accepted), 1)
        features = result.accepted[0]["panel_grading_features"]
        self.assertTrue(features["enabled"])
        self.assertAlmostEqual(features["accuracy"], 0.5)
        self.assertEqual(features["models"][0]["grade"], "CORRECT")
        self.assertEqual(features["models"][1]["grade"], "INCORRECT")
        self.assertEqual(
            features["models"][0]["answer_audit"]["response_body"]["fake_answer_response"],
            "Jane Doe",
        )
        self.assertIn("grader_audit", features["models"][0])
        self.assertEqual(
            features["models"][0]["grader_audit"]["response_body"]["fake_grader_response"],
            "A",
        )
        self.assertEqual(features["models"][0]["raw_judge_response"], "A")
        self.assertAlmostEqual(
            result.telemetry["process_generated_candidates"]["second_stage_grading_summary"]["per_model"]["openai/gpt-5.4-mini"]["accuracy"],
            1.0,
        )

    def test_process_generated_candidates_rejects_when_second_stage_panel_accuracy_exceeds_threshold(self) -> None:
        source_candidate = make_candidate()
        source_candidate.source_metadata["stable_answer_override"] = True
        candidate = GeneratedCandidate(
            source_type="test",
            generation_route="route2_wikidata_wikipedia_hybrid",
            question="Who directed the film Example Film?",
            canonical_question="Who directed the film Example Film?",
            answer="Jane Doe",
            answer_aliases=["J. Doe"],
            subject_entity=EntityReference(
                name="Example Film",
                qid="Q1",
                wikipedia_title="Example_Film",
                url="https://en.wikipedia.org/wiki/Example_Film",
            ),
            answer_entity=EntityReference(name="Jane Doe", qid="Q2"),
            relation_or_claim="director",
            evidence=EvidenceRecord(
                text="Example Film is a 2020 drama film directed by Jane Doe.",
                url="https://en.wikipedia.org/wiki/Example_Film",
                source_title="Example Film",
                retrieved_at="2026-05-13",
            ),
            question_family="who_directed_film",
            answer_type="Person",
            topic="Arts and Media",
            target_time="2020",
            source_template_domain="film_director",
            source_metadata={
                "subject_wikipedia_title": "Example_Film",
                "subject_wikipedia_url": "https://en.wikipedia.org/wiki/Example_Film",
                "subject_sitelink_count": 12,
                "subject_claim_count": 44,
                "stable_answer_override": True,
            },
            source_candidate=source_candidate,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(
                target_time="2020",
                pilot_total=1,
                output_path=Path(tmpdir) / "accepted.jsonl",
                rejected_output_path=Path(tmpdir) / "rejected.jsonl",
                second_stage_grading_enabled=True,
                second_stage_grading_accuracy_threshold=0.5,
                second_stage_grading_grader_llm=None,
            )
            result = process_generated_candidates(
                [candidate],
                settings=settings,
                search_client=FakeSearchClient(
                    {
                        "Who directed the film Example Film?": [],
                        "Example Film director": [],
                        "Example Film director Jane Doe": [],
                    }
                ),
                second_stage_model_clients=[
                    ModelPanelMember("openai/gpt-5.4-mini", FakePanelModelClient("Jane Doe")),
                    ModelPanelMember("google/gemini-3-flash-preview", FakePanelModelClient("J. Doe")),
                ],
                grading_grader_client=FakePanelGraderClient(),
                rewrite_client=None,
            )
        self.assertEqual(result.accepted, [])
        self.assertEqual(
            result.rejected[0]["rejection_reason"],
            "second_stage_grading_accuracy_threshold_exceeded",
        )

    def test_per_row_panel_grading_records_grader_audit(self) -> None:
        features = evaluate_model_panel(
            question="Who directed the film Example Film?",
            gold_answer="Jane Doe",
            gold_aliases=[],
            answer_type="Person",
            source_metadata={},
            model_panel=[ModelPanelMember("openai/gpt-5.4-mini", FakePanelModelClient("Jane Doe"))],
            grader_client=FakePanelGraderClient(["A"]),
            parallel_answers=False,
            batch_grader=False,
        )

        self.assertEqual(features["models"][0]["grade"], "CORRECT")
        self.assertEqual(
            features["models"][0]["grader_audit"]["response_body"]["fake_grader_response"],
            "A",
        )
        self.assertEqual(features["models"][0]["raw_judge_response"], "A")


if __name__ == "__main__":
    unittest.main()
