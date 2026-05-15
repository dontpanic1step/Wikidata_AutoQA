"""Tests for the staged generator validators."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.generation_models import EntityReference, EvidenceRecord, GeneratedCandidate
from wikidata_simpleqa.generator_validators import (
    build_removed_prefilter_stub,
    run_fact_level_longtail_prefilter,
    run_cheap_model_longtail_verifier,
    run_search_based_longtail_verifier,
    validate_question_surface,
)
from wikidata_simpleqa.models import CandidateFact


class FakeSearchClient:
    """Simple search client stub for long-tail verifier tests."""

    def __init__(self, results_by_query: dict[str, list[dict[str, str]]]) -> None:
        self.results_by_query = results_by_query

    def search(self, query: str, *, max_results: int = 5):
        rows = self.results_by_query.get(query, [])[:max_results]
        return [type("SearchResult", (), row)() for row in rows]


class FakeCheapModelClient:
    """Simple cheap-model QA stub for second-stage verifier tests."""

    def __init__(self, response: str) -> None:
        self.response = response
        self.prompts: list[str] = []

    def complete_text(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.response


def make_generated_candidate() -> GeneratedCandidate:
    """Build a minimal shared candidate for validator tests."""
    source_candidate = CandidateFact(
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
        canonical_question="Who directed Example Film?",
        ambiguity_status="label_unique",
        provenance_complete=True,
        source_metadata={
            "wikidata_access_date": "2024-05-01",
            "subject_sitelink_count": 12,
            "subject_claim_count": 44,
        },
        subject_resource_url="https://en.wikipedia.org/wiki/Example_Film",
        subject_resource_key="https://en.wikipedia.org/wiki/Example_Film",
    )
    return GeneratedCandidate(
        source_type="hybrid",
        generation_route="route2_wikidata_wikipedia_hybrid",
        question="Who directed Example Film?",
        canonical_question="Who directed Example Film?",
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
            section="summary",
            retrieved_at="2024-05-01",
        ),
        answer_type="Person",
        topic="Arts and Media",
        source_candidate=source_candidate,
        source_metadata=source_candidate.source_metadata.copy(),
    )


class GeneratorValidatorTests(unittest.TestCase):
    """Check the new prefilter and post-rewrite long-tail validators."""

    def test_prefilter_rejects_obvious_head_candidate(self) -> None:
        candidate = make_generated_candidate()
        candidate.source_metadata["subject_sitelink_count"] = 500
        passed, features = run_fact_level_longtail_prefilter(
            candidate,
            max_sitelinks=80,
            max_claims=400,
        )
        self.assertFalse(passed)
        self.assertIn("high_sitelink_count", features["triggered_rules"])

    def test_prefilter_keeps_borderline_candidate(self) -> None:
        candidate = make_generated_candidate()
        passed, features = run_fact_level_longtail_prefilter(
            candidate,
            max_sitelinks=80,
            max_claims=400,
        )
        self.assertTrue(passed)
        self.assertTrue(features["prefilter_passed"])

    def test_removed_prefilter_stub_records_audit_metadata(self) -> None:
        candidate = make_generated_candidate()
        features = build_removed_prefilter_stub(candidate)
        self.assertFalse(features["enabled"])
        self.assertEqual(
            features["reason"],
            "internal_popularity_prefilter_removed_in_5_13",
        )

    def test_question_surface_allows_historical_year_before_cutoff(self) -> None:
        candidate = make_generated_candidate()
        reason = validate_question_surface(
            "Who directed the 2020 film Example Film?",
            candidate,
            cutoff_year=2025,
        )
        self.assertIsNone(reason)

    def test_question_surface_rejects_cutoff_year_or_later(self) -> None:
        candidate = make_generated_candidate()
        reason = validate_question_surface(
            "Who directed the 2025 film Example Film?",
            candidate,
            cutoff_year=2025,
        )
        self.assertEqual(reason, "cutoff_year_exceeded")

    def test_search_verifier_rejects_answer_in_title(self) -> None:
        candidate = make_generated_candidate()
        client = FakeSearchClient(
            {
                "Who directed Example Film?": [
                    {
                        "title": "Jane Doe directed Example Film",
                        "snippet": "A summary result.",
                        "url": "https://example.test/1",
                    }
                ]
            }
        )
        passed, features = run_search_based_longtail_verifier(
            candidate,
            search_client=client,
            top_k=5,
            max_full_question_hit_rate=0.0,
            max_keyword_hit_rate=0.1,
            max_overall_hit_rate=0.1,
        )
        self.assertFalse(passed)
        self.assertEqual(features["triggered_rule"], "full_question:answer_in_title")

    def test_search_verifier_records_fallback_query_hits(self) -> None:
        candidate = make_generated_candidate()
        client = FakeSearchClient(
            {
                "Who directed Example Film?": [],
                "Example Film director": [],
                "Example Film director Jane Doe": [
                    {
                        "title": "Archived record",
                        "snippet": "Jane Doe",
                        "url": "https://example.test/2",
                    }
                ],
            }
        )
        passed, features = run_search_based_longtail_verifier(
            candidate,
            search_client=client,
            top_k=5,
            max_full_question_hit_rate=0.0,
            max_keyword_hit_rate=0.1,
            max_overall_hit_rate=0.1,
        )
        self.assertTrue(passed)
        self.assertEqual(len(features["queries"]), 3)

    def test_search_verifier_rejects_subject_relation_snippet_leakage(self) -> None:
        candidate = make_generated_candidate()
        client = FakeSearchClient(
            {
                "Who directed Example Film?": [],
                "Example Film director": [
                    {
                        "title": "Archived record",
                        "snippet": "Jane Doe directed the film.",
                        "url": "https://example.test/3",
                    }
                ],
            }
        )
        passed, features = run_search_based_longtail_verifier(
            candidate,
            search_client=client,
            top_k=5,
            max_full_question_hit_rate=0.0,
            max_keyword_hit_rate=0.1,
            max_overall_hit_rate=0.1,
        )
        self.assertFalse(passed)
        self.assertEqual(features["triggered_rule"], "keyword_queries:hit_rate_exceeded")
        self.assertGreater(features["category_hit_rates"]["keyword_queries"]["answer_hit_rate"], 0.1)

    def test_search_verifier_matches_country_aliases_in_snippets(self) -> None:
        candidate = make_generated_candidate()
        candidate.answer = "United States of America"
        candidate.answer_aliases = []
        candidate.answer_type = "Place"
        client = FakeSearchClient(
            {
                "Who directed Example Film?": [],
                "Example Film director": [
                    {
                        "title": "Archived record",
                        "snippet": "The work originated in the USA.",
                        "url": "https://example.test/4",
                    }
                ],
            }
        )
        passed, features = run_search_based_longtail_verifier(
            candidate,
            search_client=client,
            top_k=5,
            max_full_question_hit_rate=0.0,
            max_keyword_hit_rate=0.1,
            max_overall_hit_rate=0.1,
        )
        self.assertFalse(passed)
        self.assertEqual(features["triggered_rule"], "keyword_queries:hit_rate_exceeded")

    def test_search_verifier_runs_low_integer_snippet_judge_for_zero_to_twenty_six(self) -> None:
        candidate = make_generated_candidate()
        candidate.answer = "12"
        candidate.answer_aliases = []
        candidate.answer_type = "Number"
        snippet_judge = FakeCheapModelClient(
            '{"found_in_every_snippet": true, "reason": "All snippets explicitly mention twelve."}'
        )
        client = FakeSearchClient(
            {
                "Who directed Example Film?": [
                    {
                        "title": "Archived record",
                        "snippet": "The list includes twelve items.",
                        "url": "https://example.test/5",
                    }
                ],
                "Example Film director": [
                    {
                        "title": "Another record",
                        "snippet": "A total of 12 were recorded.",
                        "url": "https://example.test/6",
                    }
                ],
            }
        )
        passed, features = run_search_based_longtail_verifier(
            candidate,
            search_client=client,
            snippet_judge_client=snippet_judge,
            top_k=5,
            max_full_question_hit_rate=1.0,
            max_keyword_hit_rate=1.0,
            max_overall_hit_rate=1.0,
        )
        self.assertFalse(passed)
        self.assertEqual(
            features["triggered_rule"],
            "number_snippet_judge:found_in_every_snippet",
        )
        self.assertEqual(features["number_snippet_judge"]["answer_integer"], 12)

    def test_cheap_model_verifier_rejects_when_model_answers_correctly(self) -> None:
        candidate = make_generated_candidate()
        client = FakeCheapModelClient("Jane Doe")
        passed, features = run_cheap_model_longtail_verifier(
            candidate,
            cheap_model_client=client,
        )
        self.assertFalse(passed)
        self.assertEqual(features["triggered_rule"], "cheap_model_answered_correctly")
        self.assertEqual(client.prompts, ["Who directed Example Film?"])

    def test_cheap_model_verifier_passes_on_wrong_answer_or_abstain(self) -> None:
        candidate = make_generated_candidate()
        passed_wrong, _ = run_cheap_model_longtail_verifier(
            candidate,
            cheap_model_client=FakeCheapModelClient("John Smith"),
        )
        passed_abstain, _ = run_cheap_model_longtail_verifier(
            candidate,
            cheap_model_client=FakeCheapModelClient(""),
        )
        self.assertTrue(passed_wrong)
        self.assertTrue(passed_abstain)


if __name__ == "__main__":
    unittest.main()
