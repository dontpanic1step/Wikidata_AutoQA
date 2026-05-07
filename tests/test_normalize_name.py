"""Tests for label normalization."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.entity_normalization import normalize_name


class NormalizeNameTests(unittest.TestCase):
    """Check normalization used in ambiguity matching."""

    def test_removes_parenthetical_disambiguator(self) -> None:
        self.assertEqual(normalize_name("Title (film)"), "title")

    def test_removes_accents(self) -> None:
        self.assertEqual(normalize_name("Amélie"), "amelie")

    def test_collapses_punctuation_and_spaces(self) -> None:
        self.assertEqual(normalize_name("A:  B, C!"), "a b c")

    def test_normalizes_apostrophes(self) -> None:
        self.assertEqual(normalize_name("Andy Weir's novel"), "andy weir s novel")


if __name__ == "__main__":
    unittest.main()
