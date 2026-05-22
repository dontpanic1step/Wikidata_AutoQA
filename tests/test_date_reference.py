"""Tests for date answer normalization."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.date_reference import normalize_date_answer
from wikidata_simpleqa.generation_models import EntityReference, GeneratedCandidate


class DateReferenceTests(unittest.TestCase):
    """Check shared date normalization."""

    def test_normalize_date_answer_handles_common_formats(self) -> None:
        self.assertEqual(normalize_date_answer("January 2, 2020", "Date"), "January 2, 2020")
        self.assertEqual(normalize_date_answer("2 January 2020", "Date"), "January 2, 2020")
        self.assertEqual(normalize_date_answer("2026-5-21", "Date"), "May 21, 2026")
        self.assertEqual(normalize_date_answer("2026-05-21", "Date"), "May 21, 2026")
        self.assertEqual(normalize_date_answer("2026/5/21", "Date"), "May 21, 2026")
        self.assertEqual(normalize_date_answer("5/21/2026", "Date"), "May 21, 2026")
        self.assertEqual(normalize_date_answer("January 2020", "Date"), "2020-01")
        self.assertEqual(normalize_date_answer("2020", "Date"), "2020")
        self.assertEqual(normalize_date_answer("2024-2025", "Date"), "2024-2025")
        self.assertEqual(normalize_date_answer("2014-15", "Date"), "2014-2015")
        self.assertEqual(normalize_date_answer("Jane Doe", "Person"), "Jane Doe")

    def test_generated_candidate_normalizes_date_answers(self) -> None:
        candidate = GeneratedCandidate(
            source_type="test",
            generation_route="test_route",
            question="On what month, day, and year did Example open?",
            answer="January 2, 2020",
            answer_aliases=["2 January 2020"],
            subject_entity=EntityReference(name="Example", qid="Q1"),
            answer_entity=EntityReference(name="January 2, 2020"),
            relation_or_claim="opening date",
            answer_type="Date",
        )
        self.assertEqual(candidate.answer, "January 2, 2020")
        self.assertEqual(candidate.answer_aliases, ["January 2, 2020"])
        self.assertEqual(candidate.answer_entity.name, "January 2, 2020")


if __name__ == "__main__":
    unittest.main()
