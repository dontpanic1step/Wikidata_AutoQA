"""Tests for the staged multi-generator pipeline."""

from __future__ import annotations

import unittest
from unittest.mock import patch
from pathlib import Path
import tempfile

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.config import Settings
from wikidata_simpleqa.generation_pipeline import (
    _apply_number_reference_margin,
    _build_route_rewrite_payload,
    process_generated_candidates,
    run_generation_pipeline,
)
from wikidata_simpleqa.generation_models import EntityReference, EvidenceRecord, GeneratedCandidate
from wikidata_simpleqa.generator_validators import run_search_based_longtail_verifier
from wikidata_simpleqa.grading import ModelPanelMember
from wikidata_simpleqa.models import AmbiguityResolution, CandidateFact, DomainTemplate


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


class FakeRewriteClient:
    """Simple rewrite stub that returns one rewritten question."""

    def rewrite_question(self, payload: dict) -> dict:
        if payload.get("task_type") == "kelm_question_and_queries":
            return {
                "rewritten_question": "Where was Peter Kelland educated?",
                "search_queries": [
                    '"Peter Kelland" education',
                    '"Peter Kelland" Marines studies',
                ],
                "discard_reason": None,
            }
        return {
            "rewritten_question": f"Who directed Example Film according to rewrite {payload['target_property']}?",
            "search_queries": [
                f"{payload.get('canonical_question', '')} context",
                f"{payload['target_property']} Example Film production",
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


class GenerationPipelineTests(unittest.TestCase):
    """Check acceptance, rejection, and dedup in the new pipeline."""

    def test_pipeline_accepts_route2_candidate_and_rejects_route1_duplicate(self) -> None:
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
        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(len(result.rejected), 1)
        self.assertEqual(result.accepted[0]["generation_route"], "route2_wikidata_wikipedia_hybrid")
        self.assertEqual(result.rejected[0]["rejection_reason"], "duplicate_subject_resource")

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
                "Who directed Example Film according to rewrite director?": [],
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
            "Who directed Example Film according to rewrite director?",
        )
        self.assertEqual(
            result.accepted[0]["search_queries"],
            [
                "Who directed the film Example Film? context",
                "director Example Film production",
            ],
        )
        self.assertEqual(result.accepted[0]["answer_aliases"], ["J. Doe", "Jane D."])
        self.assertEqual(
            result.accepted[0]["source_metadata"]["small_model_rewrite_response"]["rewritten_question"],
            "Who directed Example Film according to rewrite director?",
        )
        self.assertNotIn("rewrite_disabled", result.accepted[0]["notes"])

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

    def test_process_generated_candidates_uses_llm_generated_kelm_queries(self) -> None:
        source_candidate = make_candidate()
        source_candidate.subject_qid = "Q7175127"
        source_candidate.subject_label = "Peter Kelland"
        source_candidate.answer_qids = ["Q35794"]
        source_candidate.answer_labels = ["University of Cambridge"]
        source_candidate.answer_aliases = []
        source_candidate.target_property_pid = "P69"
        source_candidate.target_property_label = "educated at"
        source_candidate.source_metadata.update(
            {
                "stable_answer_override": True,
                "kelm_sentence": "After two years in the Marines Peter Kelland began his studies at the University of Cambridge.",
                "kelm_serialized_triples": "Peter Kelland educated at University of Cambridge",
                "subject_sitelink_count": 3,
                "subject_claim_count": 20,
            }
        )
        candidate = GeneratedCandidate(
            source_type="external_kelm",
            generation_route="kelm_bootstrap_half_pipeline",
            question="",
            canonical_question="",
            answer="University of Cambridge",
            answer_aliases=[],
            subject_entity=EntityReference(
                name="Peter Kelland",
                qid="Q7175127",
                wikipedia_title="Peter_Kelland",
                url="https://en.wikipedia.org/wiki/Peter_Kelland",
            ),
            answer_entity=EntityReference(name="University of Cambridge", qid="Q35794"),
            relation_or_claim="educated at",
            evidence=EvidenceRecord(
                text="After two years in the Marines Peter Kelland began his studies at the University of Cambridge.",
                url="https://en.wikipedia.org/wiki/Peter_Kelland",
                source_title="Peter Kelland",
                retrieved_at="2026-05-13",
            ),
            question_family="kelm_educated_at",
            answer_type="Organization",
            topic="KELM bootstrap",
            target_time="2026",
            source_template_domain="kelm_educated_at",
            source_metadata=source_candidate.source_metadata.copy(),
            source_candidate=source_candidate,
        )
        search_client = FakeSearchClient(
            {
                "Where was Peter Kelland educated?": [],
                '"Peter Kelland" education': [],
                '"Peter Kelland" Marines studies': [],
            }
        )
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
                search_client=search_client,
                rewrite_client=FakeRewriteClient(),
            )
        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(
            result.accepted[0]["search_queries"],
            ['"Peter Kelland" education', '"Peter Kelland" Marines studies'],
        )

    def test_kelm_without_llm_queries_does_not_fall_back_to_relation_queries(self) -> None:
        source_candidate = make_candidate()
        source_candidate.subject_qid = "Q7175127"
        source_candidate.subject_label = "Peter Kelland"
        source_candidate.answer_qids = ["Q35794"]
        source_candidate.answer_labels = ["University of Cambridge"]
        source_candidate.answer_aliases = []
        source_candidate.target_property_pid = "P69"
        source_candidate.target_property_label = "educated at"
        source_candidate.source_metadata["stable_answer_override"] = True
        candidate = GeneratedCandidate(
            source_type="external_kelm",
            generation_route="kelm_bootstrap_half_pipeline",
            question="",
            canonical_question="",
            answer="University of Cambridge",
            answer_aliases=[],
            subject_entity=EntityReference(
                name="Peter Kelland",
                qid="Q7175127",
                wikipedia_title="Peter_Kelland",
                url="https://en.wikipedia.org/wiki/Peter_Kelland",
            ),
            answer_entity=EntityReference(name="University of Cambridge", qid="Q35794"),
            relation_or_claim="educated at",
            evidence=EvidenceRecord(
                text="After two years in the Marines Peter Kelland began his studies at the University of Cambridge.",
                url="https://en.wikipedia.org/wiki/Peter_Kelland",
                source_title="Peter Kelland",
                retrieved_at="2026-05-13",
            ),
            answer_type="Organization",
            topic="KELM bootstrap",
            target_time="2026",
            rewritten_question="Where was Peter Kelland educated after serving in the Marines?",
            source_metadata=source_candidate.source_metadata.copy(),
            source_candidate=source_candidate,
        )
        passed, features = run_search_based_longtail_verifier(
            candidate,
            search_client=FakeSearchClient(
                {
                    "Where was Peter Kelland educated after serving in the Marines?": [],
                }
            ),
            top_k=5,
            max_full_question_hit_rate=0.0,
            max_keyword_hit_rate=0.1,
            max_overall_hit_rate=0.1,
        )
        self.assertTrue(passed)
        self.assertEqual(len(features["queries"]), 1)
        self.assertEqual(features["queries"][0]["query_name"], "full_question")

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

    def test_route4_two_hop_rewrite_payload_includes_structured_hops(self) -> None:
        source_candidate = make_candidate()
        source_candidate.reasoning_style = "multi_hop_hidden_entity"
        source_candidate.hop_count = 2
        source_candidate.reasoning_path = [
            {
                "source_qid": "Q1",
                "source_label": "Example Film",
                "property_pid": "P144",
                "property_label": "based on",
                "target_qid": "Q3",
                "target_label": "Example Book",
                "role": "clue",
            },
            {
                "source_qid": "Q1",
                "source_label": "Example Film",
                "property_pid": "P57",
                "property_label": "director",
                "target_qid": "Q2",
                "target_label": "Jane Doe",
                "role": "answer",
            },
        ]
        source_candidate.source_metadata.update(
            {
                "answer_hop": {"template_key": "film_director", "property_label": "director"},
                "clue_hop": {"template_key": "film_based_on", "property_label": "based on"},
                "clue_orientation": "hidden_subject",
                "hidden_entities": [{"qid": "Q1", "label": "Example Film"}],
                "visible_clue": {"qid": "Q3", "label": "Example Book"},
                "required_reasoning_clues": ["based on", "Example Book"],
            }
        )
        candidate = GeneratedCandidate(
            source_type="wikidata",
            generation_route="route4_wikidata_two_hop",
            question="Who was the director of the film whose based on was Example Book?",
            canonical_question="Who was the director of the film whose based on was Example Book?",
            answer="Jane Doe",
            answer_aliases=[],
            subject_entity=EntityReference(name="Example Film", qid="Q1"),
            answer_entity=EntityReference(name="Jane Doe", qid="Q2"),
            relation_or_claim="director",
            evidence=EvidenceRecord(text="Example Film -- based on -- Example Book; Example Film -- director -- Jane Doe"),
            answer_type="Person",
            source_template_domain="film_director__via__film_based_on",
            source_candidate=source_candidate,
        )

        payload = _build_route_rewrite_payload(
            candidate,
            cutoff_year=2025,
            forbidden_patterns=["current"],
            search_query_count=2,
        )

        self.assertEqual(payload["route_contract"], "route4_two_hop")
        self.assertEqual(payload["answer_hop"]["template_key"], "film_director")
        self.assertEqual(payload["clue_orientation"], "hidden_subject")
        self.assertEqual(payload["hidden_entities"][0]["label"], "Example Film")
        self.assertEqual(payload["visible_clue"]["label"], "Example Book")

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
                rewrite_client=None,
            )
        self.assertEqual(len(result.accepted), 1)
        features = result.accepted[0]["panel_grading_features"]
        self.assertTrue(features["enabled"])
        self.assertAlmostEqual(features["accuracy"], 0.5)
        self.assertEqual(features["models"][0]["grade"], "CORRECT")
        self.assertEqual(features["models"][1]["grade"], "INCORRECT")
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
                rewrite_client=None,
            )
        self.assertEqual(result.accepted, [])
        self.assertEqual(
            result.rejected[0]["rejection_reason"],
            "second_stage_grading_accuracy_threshold_exceeded",
        )

    def test_number_snippet_judge_trigger_range_is_minus_ten_to_thirty(self) -> None:
        from wikidata_simpleqa.generation_pipeline import _needs_number_snippet_judge

        source_candidate = make_candidate()
        candidate = GeneratedCandidate(
            source_type="test",
            generation_route="route2_wikidata_wikipedia_hybrid",
            question="How many points did Example Film score?",
            canonical_question="How many points did Example Film score?",
            answer="-10",
            answer_aliases=[],
            subject_entity=EntityReference(name="Example Film", qid="Q1"),
            answer_entity=EntityReference(name="-10"),
            relation_or_claim="points",
            evidence=EvidenceRecord(
                text="Example Film scored -10 points.",
                url="https://example.test",
                source_title="Example Film",
                retrieved_at="2026-05-13",
            ),
            answer_type="Number",
            topic="Tests",
            source_candidate=source_candidate,
        )
        self.assertTrue(_needs_number_snippet_judge(candidate))
        candidate.answer = "-11"
        self.assertFalse(_needs_number_snippet_judge(candidate))
        candidate.answer = "30"
        self.assertTrue(_needs_number_snippet_judge(candidate))
        candidate.answer = "31"
        self.assertFalse(_needs_number_snippet_judge(candidate))
        candidate.answer = "12.5"
        self.assertFalse(_needs_number_snippet_judge(candidate))
        candidate.answer = "12th"
        self.assertFalse(_needs_number_snippet_judge(candidate))


if __name__ == "__main__":
    unittest.main()
