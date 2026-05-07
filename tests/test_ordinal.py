"""Tests for ordinal helpers."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.composed_harvester import _render_ordinal, _strip_year_tokens


class OrdinalTests(unittest.TestCase):
    """Check ordinal rendering behavior."""

    def test_render_basic_ordinals(self) -> None:
        self.assertEqual(_render_ordinal(1), "1st")
        self.assertEqual(_render_ordinal(2), "2nd")
        self.assertEqual(_render_ordinal(3), "3rd")
        self.assertEqual(_render_ordinal(4), "4th")

    def test_render_teen_ordinals(self) -> None:
        self.assertEqual(_render_ordinal(11), "11th")
        self.assertEqual(_render_ordinal(12), "12th")
        self.assertEqual(_render_ordinal(13), "13th")

    def test_render_larger_ordinals(self) -> None:
        self.assertEqual(_render_ordinal(21), "21st")
        self.assertEqual(_render_ordinal(42), "42nd")
        self.assertEqual(_render_ordinal(103), "103rd")

    def test_strip_year_tokens_from_series_label(self) -> None:
        self.assertEqual(_strip_year_tokens("2026 ARCA Menards Series West"), "ARCA Menards Series West")
        self.assertEqual(_strip_year_tokens("Melodifestivalen 2026"), "Melodifestivalen")


if __name__ == "__main__":
    unittest.main()
