"""Tests for numeric answer normalization and margin helpers."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.generation_models import EntityReference, GeneratedCandidate
from wikidata_simpleqa.models import CandidateFact
from wikidata_simpleqa.number_reference import (
    build_number_reference_margin,
    normalize_number_answer,
)


class NumberReferenceTests(unittest.TestCase):
    """Check shared numeric answer normalization."""

    def test_normalize_number_answer_handles_commas_decimals_and_words(self) -> None:
        self.assertEqual(normalize_number_answer("1,200.0", "Number"), "1200")
        self.assertEqual(normalize_number_answer("thirteen thousand", "Number"), "13000")
        self.assertEqual(normalize_number_answer("Jane Doe", "Person"), "Jane Doe")

    def test_normalize_number_answer_strips_unit_suffixes_with_regex_fallback(self) -> None:
        self.assertEqual(normalize_number_answer("5,000 gallons", "Number"), "5000")
        self.assertEqual(normalize_number_answer("14.7km", "Number"), "14.7")
        self.assertEqual(normalize_number_answer("2.5 million gallons", "Number"), "2500000")

    def test_number_reference_margin_uses_unit_free_reference_answer(self) -> None:
        margin = build_number_reference_margin("5,000 gallons", "Number")
        self.assertEqual(margin["original_answer"], "5,000 gallons")
        self.assertEqual(margin["numeric_value"], "5000")
        self.assertEqual(margin["reference_answer"], "5000 (acceptable range: anything between 4950 and 5050)")

    def test_candidate_fact_normalizes_number_answer_labels(self) -> None:
        candidate = CandidateFact(
            subject_qid="Q1",
            subject_label="Example Work",
            subject_aliases=[],
            domain="example",
            topic="Tests",
            answer_type="Number",
            question_family="numeric_fact",
            subject_type_qids=[],
            target_property_pid="P1",
            target_property_label="count",
            answer_qids=[],
            answer_labels=["1,200.0"],
            answer_aliases=["twelve hundred"],
            date_property_pid="P2",
            date_value="2020-01-01",
            target_time="2020",
            canonical_question="What is the count of Example Work?",
        )
        self.assertEqual(candidate.answer_labels, ["1200"])
        self.assertEqual(candidate.answer_aliases, ["1200"])

    def test_generated_candidate_normalizes_number_answer_before_margin_generation(self) -> None:
        candidate = GeneratedCandidate(
            source_type="test",
            generation_route="test_route",
            question="What is the count of Example Work?",
            answer="1,200.0 pages",
            answer_aliases=["twelve hundred"],
            subject_entity=EntityReference(name="Example Work", qid="Q1"),
            answer_entity=EntityReference(name="1,200.0 pages"),
            relation_or_claim="count",
            answer_type="Number",
        )
        self.assertEqual(candidate.answer, "1200")
        self.assertEqual(candidate.answer_aliases, ["1200"])
        self.assertEqual(candidate.answer_entity.name, "1200")
        margin = build_number_reference_margin(candidate.answer, candidate.answer_type)
        self.assertEqual(margin["lower_bound"], "1188")
        self.assertEqual(margin["upper_bound"], "1212")


if __name__ == "__main__":
    unittest.main()
