"""Tests for the staged generator validators."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa import generator_validators as generator_validator_module
from wikidata_simpleqa import route3_quality_rules
from wikidata_simpleqa.generation_models import EntityReference, EvidenceRecord, GeneratedCandidate
from wikidata_simpleqa.generator_validators import (
    evidence_supports_answer,
    run_search_based_longtail_verifier,
    validate_generated_candidate,
    validate_question_surface,
)
from wikidata_simpleqa.rule_based_answer_type_gate import evaluate_candidate_answer_type_gate


class FakeSearchClient:
    """Simple search client stub for long-tail verifier tests."""

    def __init__(self, results_by_query: dict[str, list[dict[str, str]]]) -> None:
        self.results_by_query = results_by_query

    def search(self, query: str, *, max_results: int = 5):
        rows = self.results_by_query.get(query, [])[:max_results]
        return [type("SearchResult", (), row)() for row in rows]



def make_generated_candidate() -> GeneratedCandidate:
    """Build a minimal shared candidate for validator tests."""
    return GeneratedCandidate(
        source_type="hybrid",
        generation_route="route3_wikipedia_infobox",
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
        source_metadata={
            "wikidata_access_date": "2024-05-01",
            "subject_sitelink_count": 12,
            "subject_claim_count": 44,
        },
    )


class GeneratorValidatorTests(unittest.TestCase):
    """Check deterministic and search-based validators."""

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

    def test_question_surface_allows_month_names(self) -> None:
        candidate = make_generated_candidate()
        reason = validate_question_surface(
            "Who directed the May release Example Film?",
            candidate,
            cutoff_year=2025,
        )
        self.assertIsNone(reason)

    def test_question_surface_allows_generic_according_to_table_wording(self) -> None:
        candidate = make_generated_candidate()
        reason = validate_question_surface(
            "Who directed Example Film according to the table?",
            candidate,
            cutoff_year=2025,
        )
        self.assertIsNone(reason)

    def test_question_surface_allows_named_public_chart_wording(self) -> None:
        candidate = make_generated_candidate()
        reason = validate_question_surface(
            "Who directed Example Film according to the Billboard chart table?",
            candidate,
            cutoff_year=2025,
        )
        self.assertIsNone(reason)

    def test_question_surface_allows_mutable_wording_when_rule_disabled(self) -> None:
        candidate = make_generated_candidate()
        reason = validate_question_surface(
            "Who is the spouse in Example Film?",
            candidate,
            cutoff_year=2025,
        )
        self.assertIsNone(reason)

    def test_question_surface_allows_lost_subject_anchor_when_rule_disabled(self) -> None:
        candidate = make_generated_candidate()
        reason = validate_question_surface(
            "Who directed the drama film?",
            candidate,
            cutoff_year=2025,
        )
        self.assertIsNone(reason)
        self.assertIn("lost_subject_anchor", candidate.source_metadata["surface_validation_warnings"])

    def test_question_surface_number_leakage_uses_extracted_number_values(self) -> None:
        candidate = make_generated_candidate()
        candidate.answer = "6"
        candidate.answer_aliases = []
        candidate.answer_type = "Number"
        candidate.answer_entity.name = "6"
        reason = validate_question_surface(
            "Which Example Film district had the highest vote count in 2016?",
            candidate,
            cutoff_year=2025,
        )
        self.assertIsNone(reason)
        leaked_reason = validate_question_surface(
            "Which Example Film district was district 6?",
            candidate,
            cutoff_year=2025,
        )
        self.assertEqual(leaked_reason, "answer_leakage")

    def test_question_surface_rejects_geographic_context_answer_leakage(self) -> None:
        candidate = make_generated_candidate()
        candidate.answer = "United States"
        candidate.answer_aliases = []
        candidate.answer_type = "Place"
        candidate.answer_entity.name = "United States"
        reason = validate_question_surface(
            "Which country is New York associated with in Example Film?",
            candidate,
            cutoff_year=2025,
        )
        self.assertEqual(reason, "answer_leakage")

    def test_route3_evidence_matches_text_inside_selected_table_cell(self) -> None:
        candidate = make_generated_candidate()
        candidate.generation_route = "route3_wikipedia_infobox"
        candidate.source_type = "wikipedia_tables"
        candidate.answer = "Archive Hall"
        candidate.answer_aliases = []
        candidate.answer_type = "Place"
        candidate.subject_entity.url = "https://en.wikipedia.org/wiki/Example"
        candidate.evidence.text = ""
        candidate.source_metadata = {
            "selected_source_table": {
                "headers": ["Venue", "Notes"],
                "rows": [["Ceremony", "The event was held at Archive Hall in 1998."]],
                "markdown": "| Venue | Notes |\n| --- | --- |\n| Ceremony | The event was held at Archive Hall in 1998. |",
            }
        }
        self.assertTrue(evidence_supports_answer(candidate))
        self.assertTrue(candidate.source_metadata["answer_in_evidence_match"]["matched"])
        self.assertIn("selected_source_table.rows", candidate.source_metadata["answer_in_evidence_match"]["source"])

    def test_route3_evidence_matches_explicit_alias_without_inventing_aliases(self) -> None:
        candidate = make_generated_candidate()
        candidate.generation_route = "route3_wikipedia_infobox"
        candidate.source_type = "wikipedia_tables"
        candidate.answer = "University of British Columbia"
        candidate.answer_aliases = ["UBC"]
        candidate.answer_type = "Other"
        candidate.subject_entity.url = "https://en.wikipedia.org/wiki/Example"
        candidate.evidence.text = ""
        candidate.source_metadata = {
            "selected_source_table": {
                "headers": ["Institution"],
                "rows": [["The record lists UBC as the institution."]],
            }
        }
        self.assertTrue(evidence_supports_answer(candidate))

    def test_route3_validation_only_reports_effective_checks(self) -> None:
        candidate = make_generated_candidate()
        candidate.generation_route = "route3_wikipedia_infobox"
        candidate.source_type = "wikipedia_tables"
        candidate.answer = "Archive Hall"
        candidate.answer_aliases = []
        candidate.subject_entity.url = "https://en.wikipedia.org/wiki/Example"
        candidate.source_metadata = {
            "selected_source_table": {
                "headers": ["Venue"],
                "rows": [["Archive Hall"]],
            }
        }

        passed, validation = validate_generated_candidate(candidate, cutoff_year=2025)

        self.assertTrue(passed)
        self.assertEqual(
            validation,
            {
                "answer_in_evidence": True,
                "route_validation_policy": "answer_in_selected_table",
            },
        )
        self.assertNotIn("prefilter_longtail_features", candidate.to_output_record("example-1"))

    def test_person_answer_type_has_no_rule_based_heuristic(self) -> None:
        candidate = make_generated_candidate()
        candidate.answer_type = "Person"
        candidate.answer = "The Red Blue"
        candidate.answer_entity.name = candidate.answer

        result = evaluate_candidate_answer_type_gate(candidate)

        self.assertTrue(result.matched)
        self.assertEqual(result.details["rule"], "no_rule_for_answer_type")

    def test_removed_rule_helpers_are_absent(self) -> None:
        self.assertFalse(hasattr(route3_quality_rules, "oversized_table_filter_reasons"))
        self.assertFalse(hasattr(generator_validator_module, "run_fact_level_longtail_prefilter"))
        self.assertFalse(hasattr(generator_validator_module, "build_removed_prefilter_stub"))
        self.assertFalse(hasattr(generator_validator_module, "_uses_generic_table_source_wording"))
        self.assertFalse(hasattr(generator_validator_module, "candidate_is_time_invariant"))

    def test_route3_list_answer_items_can_match_anywhere_in_selected_table(self) -> None:
        candidate = make_generated_candidate()
        candidate.generation_route = "route3_wikipedia_infobox"
        candidate.source_type = "wikipedia_tables"
        candidate.answer = "Alpha; Beta"
        candidate.answer_aliases = []
        candidate.answer_type = "Other"
        candidate.subject_entity.url = "https://en.wikipedia.org/wiki/Example"
        candidate.evidence.text = ""
        candidate.source_metadata = {
            "answer_items": ["Alpha", "Beta"],
            "selected_source_table": {
                "headers": ["Name"],
                "rows": [["Alpha appears in this row."], ["A different row mentions Beta."]],
            },
        }
        self.assertTrue(evidence_supports_answer(candidate))

    def test_route3_number_evidence_matches_comma_number(self) -> None:
        candidate = make_generated_candidate()
        candidate.generation_route = "route3_wikipedia_infobox"
        candidate.source_type = "wikipedia_tables"
        candidate.answer = "1500"
        candidate.answer_aliases = []
        candidate.answer_type = "Number"
        candidate.subject_entity.url = "https://en.wikipedia.org/wiki/Example"
        candidate.evidence.text = ""
        candidate.source_metadata = {
            "selected_source_table": {
                "headers": ["Attendance"],
                "rows": [["The attendance was 1,500 people."]],
            }
        }
        self.assertTrue(evidence_supports_answer(candidate))

    def test_route3_date_evidence_matches_date_variant(self) -> None:
        candidate = make_generated_candidate()
        candidate.generation_route = "route3_wikipedia_infobox"
        candidate.source_type = "wikipedia_tables"
        candidate.answer = "May 21, 2026"
        candidate.answer_aliases = []
        candidate.answer_type = "Date"
        candidate.subject_entity.url = "https://en.wikipedia.org/wiki/Example"
        candidate.evidence.text = ""
        candidate.source_metadata = {
            "selected_source_table": {
                "headers": ["Date"],
                "rows": [["The ceremony took place on 21 May 2026."]],
            }
        }
        self.assertTrue(evidence_supports_answer(candidate))

    def test_route3_date_evidence_does_not_match_unrelated_number(self) -> None:
        candidate = make_generated_candidate()
        candidate.generation_route = "route3_wikipedia_infobox"
        candidate.source_type = "wikipedia_tables"
        candidate.answer = "May 21, 2026"
        candidate.answer_aliases = []
        candidate.answer_type = "Date"
        candidate.subject_entity.url = "https://en.wikipedia.org/wiki/Example"
        candidate.evidence.text = ""
        candidate.source_metadata = {
            "selected_source_table": {
                "headers": ["Notes"],
                "rows": [["The unrelated count was 21."]],
            }
        }
        self.assertFalse(evidence_supports_answer(candidate))

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

    def test_search_verifier_does_not_match_short_alias_inside_words(self) -> None:
        candidate = make_generated_candidate()
        candidate.answer = "US"
        candidate.answer_aliases = []
        candidate.answer_type = "Other"
        client = FakeSearchClient(
            {
                "Who directed Example Film?": [],
                "Example Film director": [
                    {
                        "title": "Example museum archive",
                        "snippet": "The museum record is unrelated.",
                        "url": "https://example.test/museum",
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
        self.assertFalse(features["queries"][1]["results"][0]["answer_hit"])

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

    def test_search_verifier_allows_hit_rate_equal_to_threshold(self) -> None:
        candidate = make_generated_candidate()
        candidate.search_queries = ["Example Film director query"]
        client = FakeSearchClient(
            {
                "Who directed Example Film?": [
                    {
                        "title": f"Question result {index}",
                        "snippet": "No answer here.",
                        "url": f"https://example.test/q{index}",
                    }
                    for index in range(10)
                ],
                "Example Film director query": [
                    {
                        "title": f"Keyword result {index}",
                        "snippet": "Jane Doe appears here." if index < 3 else "No answer here.",
                        "url": f"https://example.test/k{index}",
                    }
                    for index in range(10)
                ],
            }
        )
        passed, features = run_search_based_longtail_verifier(
            candidate,
            search_client=client,
            top_k=10,
            max_full_question_hit_rate=0.3,
            max_keyword_hit_rate=0.3,
            max_overall_hit_rate=0.3,
        )
        self.assertTrue(passed)
        self.assertEqual(features["category_hit_rates"]["keyword_queries"]["answer_hit_rate"], 0.3)

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

    def test_search_verifier_does_not_match_date_answer_by_number_only(self) -> None:
        candidate = make_generated_candidate()
        candidate.answer = "May 21, 2026"
        candidate.answer_aliases = []
        candidate.answer_type = "Date"
        client = FakeSearchClient(
            {
                "Who directed Example Film?": [],
                "Example Film director": [
                    {
                        "title": "Archived record",
                        "snippet": "The unrelated count was 21.",
                        "url": "https://example.test/date-number",
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
        self.assertEqual(features["queries"][1]["snippet_hits"], 0)

    def test_search_verifier_does_not_match_text_answer_by_number_only(self) -> None:
        candidate = make_generated_candidate()
        candidate.answer = "Melnick 35"
        candidate.answer_aliases = []
        candidate.answer_type = "Other"
        client = FakeSearchClient(
            {
                "Who directed Example Film?": [],
                "Example Film director": [
                    {
                        "title": "Archived record",
                        "snippet": "The unrelated count was 35.",
                        "url": "https://example.test/text-number",
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
        self.assertEqual(features["queries"][1]["snippet_hits"], 0)

    def test_search_verifier_matches_short_year_date_variants_in_snippets(self) -> None:
        candidate = make_generated_candidate()
        candidate.answer = "0924-03-03"
        candidate.answer_aliases = []
        candidate.answer_type = "Date"
        client = FakeSearchClient(
            {
                "Who directed Example Film?": [],
                "Example Film director": [
                    {
                        "title": "Archived record",
                        "snippet": "The relevant date was March 3 924.",
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

    def test_search_verifier_matches_bc_date_variants_in_snippets(self) -> None:
        candidate = make_generated_candidate()
        candidate.answer = "200 BC"
        candidate.answer_aliases = []
        candidate.answer_type = "Date"
        client = FakeSearchClient(
            {
                "Who directed Example Film?": [],
                "Example Film director": [
                    {
                        "title": "Archived record",
                        "snippet": "The relevant year was 200 BCE.",
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
        from wikidata_simpleqa.route3_post_generation import _apply_number_reference_margin

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
        from wikidata_simpleqa.route3_post_generation import _apply_number_reference_margin

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
        from wikidata_simpleqa.route3_post_generation import _apply_number_reference_margin

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
        from wikidata_simpleqa.route3_post_generation import _apply_number_reference_margin

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
        self.assertNotIn("number_snippet_judge", features)


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

    def test_search_verifier_requires_every_list_answer_item_in_same_result(self) -> None:
        candidate = make_generated_candidate()
        candidate.answer = "Alpha; Beta"
        candidate.answer_aliases = []
        candidate.source_metadata["answer_items"] = ["Alpha", "Beta"]
        client = FakeSearchClient(
            {
                "Who directed Example Film?": [],
                "Example Film director": [
                    {
                        "title": "Partial record",
                        "snippet": "Alpha appears here without the other tied answer.",
                        "url": "https://example.test/partial",
                    },
                    {
                        "title": "Complete record",
                        "snippet": "The tied answers are Alpha and Beta.",
                        "url": "https://example.test/complete",
                    },
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
        self.assertEqual(features["queries"][1]["snippet_hits"], 1)
        self.assertFalse(features["queries"][1]["results"][0]["answer_hit"])
        self.assertTrue(features["queries"][1]["results"][1]["answer_hit"])


if __name__ == "__main__":
    unittest.main()
