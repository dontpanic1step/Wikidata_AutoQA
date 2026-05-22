"""Tests for date-answer normalization and formatting."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.models import CandidateFact
from wikidata_simpleqa.date_answers import format_iso_date_for_answer, normalize_wikidata_date_literal
from wikidata_simpleqa.validators import reasoning_path_is_temporally_safe


class DateAnswerTests(unittest.TestCase):
    """Check SimpleQA-Verified-style date answer formatting."""

    def test_normalizes_wikidata_datetime_to_iso_day(self) -> None:
        self.assertEqual(
            normalize_wikidata_date_literal("1988-01-22T00:00:00Z"),
            "1988-01-22",
        )

    def test_formats_iso_date_as_month_day_year(self) -> None:
        self.assertEqual(format_iso_date_for_answer("1988-01-22"), "January 22, 1988")

    def test_date_answer_candidate_allows_temporal_answer_hop_label(self) -> None:
        candidate = CandidateFact(
            subject_qid="Q1",
            subject_label="Example Terminal",
            subject_aliases=[],
            domain="terminal_opening_date",
            topic="Architecture and Transportation",
            answer_type="Date",
            question_family="when_terminal_opened",
            subject_type_qids=["Q55488"],
            target_property_pid="P571",
            target_property_label="inception",
            answer_qids=["VALUE:date:2026-03-14"],
            answer_labels=["March 14, 2026"],
            answer_aliases=["2026-03-14"],
            date_property_pid="P571",
            date_value="2026-03-14",
            target_time="2026",
            canonical_question="On what month, day, and year did the terminal Example Terminal open?",
            reasoning_style="single_fact",
            hop_count=1,
            reasoning_path=[
                {
                    "source_qid": "Q1",
                    "source_label": "Example Terminal",
                    "property_pid": "P571",
                    "property_label": "inception",
                    "target_qid": "VALUE:date:2026-03-14",
                    "target_label": "March 14, 2026",
                    "role": "answer",
                }
            ],
            provenance_complete=True,
        )
        self.assertTrue(reasoning_path_is_temporally_safe(candidate))


if __name__ == "__main__":
    unittest.main()
