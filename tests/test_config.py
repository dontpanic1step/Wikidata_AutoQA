"""Tests for configuration parsing."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.config import Settings


class ConfigTests(unittest.TestCase):
    """Check target-time parsing and validation."""

    def test_year_target_time_maps_to_first_day(self) -> None:
        self.assertEqual(Settings(target_time="2026").target_start_date, "2026-01-01")

    def test_month_target_time_maps_to_first_day_of_month(self) -> None:
        self.assertEqual(Settings(target_time="2026-05").target_start_date, "2026-05-01")

    def test_date_target_time_is_preserved(self) -> None:
        self.assertEqual(Settings(target_time="2026-05-09").target_start_date, "2026-05-09")

    def test_invalid_target_time_raises(self) -> None:
        with self.assertRaises(ValueError):
            Settings(target_time="2026-99")


if __name__ == "__main__":
    unittest.main()
