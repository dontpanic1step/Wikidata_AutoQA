"""Tests for the staged multi-generator pipeline."""

from __future__ import annotations

import unittest
from unittest.mock import patch
from pathlib import Path
import tempfile

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.config import Settings
from wikidata_simpleqa.generation_pipeline import process_generated_candidates, run_generation_pipeline
from wikidata_simpleqa.generation_models import EntityReference, EvidenceRecord, GeneratedCandidate
from wikidata_simpleqa.generator_validators import run_search_based_longtail_verifier
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
        return {"question": f"Who directed Example Film according to rewrite {payload['target_property']}?"}


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
                patch("wikidata_simpleqa.generators._validate_candidate", return_value=resolution),
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
                patch("wikidata_simpleqa.generators._validate_candidate", return_value=resolution),
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
        self.assertNotIn("rewrite_disabled", result.accepted[0]["notes"])

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


if __name__ == "__main__":
    unittest.main()
