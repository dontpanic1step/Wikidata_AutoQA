"""Tests for conservative display cleanup and text matching."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.text_normalization import (
    build_text_matcher,
    display_cleanup,
    display_key,
    source_display_cleanup,
    text_contains_match,
)


class TextNormalizationTests(unittest.TestCase):
    """Check the three-layer text normalization boundary helpers."""

    def test_display_cleanup_removes_reference_markers_and_preserves_text_brackets(self) -> None:
        self.assertEqual(
            display_cleanup("Alpha&nbsp; [1]\nBeta\t[a] [note 1] [semantic note]"),
            "Alpha Beta [semantic note]",
        )

    def test_source_display_cleanup_preserves_non_reference_bracketed_notes(self) -> None:
        self.assertEqual(
            source_display_cleanup("Alpha&nbsp; [1]\nBeta\t[a] [note 1] [citation needed] [semantic note]"),
            "Alpha Beta [citation needed] [semantic note]",
        )

    def test_display_cleanup_preserves_unicode_parentheses_and_punctuation(self) -> None:
        value = "Amélie 北京 Αθήνα O'Connor St John’s Mercury (planet)"
        self.assertEqual(display_cleanup(value), value)
        self.assertEqual(display_key(" Amélie  "), "amélie")

    def test_layer2_matches_possessive_and_apostrophe_boundaries(self) -> None:
        self.assertTrue(text_contains_match("Andy Weir's novel", build_text_matcher("Andy Weir")))
        self.assertTrue(text_contains_match("O Connor wrote it", build_text_matcher("O'Connor")))
        self.assertFalse(text_contains_match("OConnor wrote it", build_text_matcher("O'Connor")))

    def test_layer2_does_not_match_short_ascii_inside_words(self) -> None:
        self.assertFalse(text_contains_match("museum archive", build_text_matcher("US")))
        self.assertTrue(text_contains_match("in the US archive", build_text_matcher("US")))
        self.assertFalse(text_contains_match("grade A result", build_text_matcher("A")))

    def test_layer2_allows_non_ascii_and_cjk_substrings(self) -> None:
        self.assertTrue(text_contains_match("颜色是红色", build_text_matcher("红")))
        self.assertTrue(text_contains_match("The β-value changed.", build_text_matcher("β")))

    def test_layer2_uses_variants_without_changing_answer_text(self) -> None:
        matcher = build_text_matcher("award")
        self.assertTrue(text_contains_match("The awards ceremony", matcher))


if __name__ == "__main__":
    unittest.main()
