"""Tests for temporal validation behavior."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.validators import (
    has_forbidden_temporal_text,
    has_year,
    violates_cutoff_year_policy,
)


class TemporalValidatorTests(unittest.TestCase):
    """Check strict temporal rejection rules."""

    def test_rejects_explicit_year(self) -> None:
        self.assertTrue(has_year("Who directed the 2026 film X?"))
        self.assertTrue(has_forbidden_temporal_text("Who directed the 2026 film X?"))
        self.assertTrue(violates_cutoff_year_policy("Who directed the 2026 film X?", 2025))

    def test_rejects_relative_temporal_phrase(self) -> None:
        self.assertTrue(has_forbidden_temporal_text("Who directed X this year?"))
        self.assertTrue(violates_cutoff_year_policy("Who directed X this year?", 2025))

    def test_rejects_current_fact_wording(self) -> None:
        self.assertTrue(has_forbidden_temporal_text("Who is the current CEO of X?"))

    def test_rejects_latest_fact_wording(self) -> None:
        self.assertTrue(has_forbidden_temporal_text("Who won the latest edition of X?"))

    def test_rejects_month_name(self) -> None:
        self.assertTrue(has_forbidden_temporal_text("Who published X in January?"))

    def test_allows_non_temporal_disambiguation(self) -> None:
        text = "Who directed the film adaptation of Andy Weir's novel Project Hail Mary?"
        self.assertFalse(has_forbidden_temporal_text(text))
        self.assertFalse(violates_cutoff_year_policy(text, 2025))

    def test_allows_pre_cutoff_historical_year(self) -> None:
        text = "Who directed the 2020 film Example X?"
        self.assertTrue(has_forbidden_temporal_text(text))
        self.assertFalse(violates_cutoff_year_policy(text, 2025))

    def test_does_not_treat_mayhem_as_month(self) -> None:
        self.assertFalse(has_forbidden_temporal_text("Who created Mayhem Avenue?"))


if __name__ == "__main__":
    unittest.main()
