"""Tests for the staged generator validators."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.generation_models import EntityReference, EvidenceRecord, GeneratedCandidate
from wikidata_simpleqa.generator_validators import (
    build_removed_prefilter_stub,
    run_fact_level_longtail_prefilter,
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
    """Simple text-completion stub for snippet-judge tests."""

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

    def test_search_verifier_allows_answer_in_title_when_threshold_is_one(self) -> None:
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
            max_full_question_hit_rate=1.0,
            max_keyword_hit_rate=1.0,
            max_overall_hit_rate=1.0,
        )
        self.assertTrue(passed)
        self.assertEqual(features["triggered_rule"], "")

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

    def test_search_verifier_matches_date_variants_in_snippets(self) -> None:
        candidate = make_generated_candidate()
        candidate.answer = "2020-01-02"
        candidate.answer_aliases = []
        candidate.answer_type = "Date"
        client = FakeSearchClient(
            {
                "Who directed Example Film?": [],
                "Example Film director": [
                    {
                        "title": "Archived record",
                        "snippet": "The relevant date was January 2 2020.",
                        "url": "https://example.test/date",
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
        self.assertEqual(features["queries"][1]["snippet_hits"], 1)

    def test_search_verifier_matches_number_with_comma_in_snippets(self) -> None:
        candidate = make_generated_candidate()
        candidate.answer = "1200"
        candidate.answer_aliases = []
        candidate.answer_type = "Number"
        from wikidata_simpleqa.generation_pipeline import _apply_number_reference_margin

        _apply_number_reference_margin(candidate)
        client = FakeSearchClient(
            {
                "Who directed Example Film?": [],
                "Example Film director": [
                    {
                        "title": "Archived record",
                        "snippet": "The total was 1,200.",
                        "url": "https://example.test/number",
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
        self.assertEqual(features["queries"][1]["snippet_hits"], 1)

    def test_search_verifier_matches_number_margin_for_non_low_integer(self) -> None:
        candidate = make_generated_candidate()
        candidate.answer = "1200"
        candidate.answer_aliases = []
        candidate.answer_type = "Number"
        from wikidata_simpleqa.generation_pipeline import _apply_number_reference_margin

        _apply_number_reference_margin(candidate)
        client = FakeSearchClient(
            {
                "Who directed Example Film?": [],
                "Example Film director": [
                    {
                        "title": "Archived record",
                        "snippet": "The recorded total was 1,205.",
                        "url": "https://example.test/number-margin",
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
        self.assertEqual(
            features["queries"][1]["results"][0]["snippet_number_margin_hits"],
            ["1205"],
        )

    def test_search_verifier_matches_english_number_margin_for_non_low_integer(self) -> None:
        candidate = make_generated_candidate()
        candidate.answer = "13000"
        candidate.answer_aliases = []
        candidate.answer_type = "Number"
        from wikidata_simpleqa.generation_pipeline import _apply_number_reference_margin

        _apply_number_reference_margin(candidate)
        client = FakeSearchClient(
            {
                "Who directed Example Film?": [],
                "Example Film director": [
                    {
                        "title": "Archived record",
                        "snippet": "The report describes roughly thirteen thousand entries.",
                        "url": "https://example.test/number-words",
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
        self.assertEqual(
            features["queries"][1]["results"][0]["snippet_number_margin_hits"],
            ["13000"],
        )

    def test_search_verifier_does_not_use_margin_for_low_integer_answers(self) -> None:
        candidate = make_generated_candidate()
        candidate.answer = "30"
        candidate.answer_aliases = []
        candidate.answer_type = "Number"
        from wikidata_simpleqa.generation_pipeline import _apply_number_reference_margin

        _apply_number_reference_margin(candidate)
        client = FakeSearchClient(
            {
                "Who directed Example Film?": [],
                "Example Film director": [
                    {
                        "title": "Archived record",
                        "snippet": "The adjacent total was 31.",
                        "url": "https://example.test/low-integer-margin",
                    }
                ],
            }
        )
        passed, features = run_search_based_longtail_verifier(
            candidate,
            search_client=client,
            snippet_judge_client=None,
            top_k=5,
            max_full_question_hit_rate=0.0,
            max_keyword_hit_rate=0.1,
            max_overall_hit_rate=0.1,
        )
        self.assertTrue(passed)
        self.assertEqual(features["queries"][1]["snippet_hits"], 0)
        self.assertEqual(
            features["queries"][1]["results"][0]["snippet_number_margin_hits"],
            [],
        )

    def test_search_verifier_matches_answer_aliases_in_snippets(self) -> None:
        candidate = make_generated_candidate()
        candidate.answer = "University of British Columbia"
        candidate.answer_aliases = ["UBC"]
        candidate.answer_type = "Organization"
        client = FakeSearchClient(
            {
                "Who directed Example Film?": [],
                "Example Film director": [
                    {
                        "title": "Archived record",
                        "snippet": "The record lists UBC as the relevant institution.",
                        "url": "https://example.test/alias",
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
        self.assertEqual(features["queries"][1]["snippet_hits"], 1)

    def test_search_verifier_runs_low_integer_snippet_judge_for_minus_ten_to_thirty(self) -> None:
        candidate = make_generated_candidate()
        candidate.answer = "-10"
        candidate.answer_aliases = []
        candidate.answer_type = "Number"
        snippet_judge = FakeCheapModelClient(
            '{"found_in_every_snippet": true, "reason": "All snippets explicitly mention minus ten."}'
        )
        client = FakeSearchClient(
            {
                "Who directed Example Film?": [
                    {
                        "title": "Archived record",
                        "snippet": "The table lists minus ten points.",
                        "url": "https://example.test/5",
                    }
                ],
                "Example Film director": [
                    {
                        "title": "Another record",
                        "snippet": "A total of -10 were recorded.",
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
        self.assertEqual(features["number_snippet_judge"]["answer_integer"], -10)
        self.assertIn("minus ten", snippet_judge.prompts[0])

    def test_search_verifier_does_not_run_snippet_judge_for_decimal_number(self) -> None:
        candidate = make_generated_candidate()
        candidate.answer = "12.5"
        candidate.answer_aliases = []
        candidate.answer_type = "Number"
        snippet_judge = FakeCheapModelClient(
            '{"found_in_every_snippet": true, "reason": "Should not be called."}'
        )
        client = FakeSearchClient(
            {
                "Who directed Example Film?": [
                    {
                        "title": "Archived record",
                        "snippet": "The table lists 12.5.",
                        "url": "https://example.test/decimal",
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
        self.assertTrue(passed)
        self.assertNotIn("number_snippet_judge", features)
        self.assertEqual(snippet_judge.prompts, [])


if __name__ == "__main__":
    unittest.main()
