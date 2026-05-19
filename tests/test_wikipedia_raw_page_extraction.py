"""Tests for raw Wikipedia dump extraction that preserves table markup."""

from __future__ import annotations

import bz2
import tempfile
import unittest
from pathlib import Path

from test_support import ROOT  # noqa: F401

import sys

SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from extract_wikipedia_raw_pages import iter_pages  # noqa: E402


class WikipediaRawPageExtractionTests(unittest.TestCase):
    """Check that raw wikitext table markup survives extraction."""

    def test_iter_pages_preserves_wikitable_markup(self) -> None:
        xml = """<mediawiki>
<page>
<title>Example table page</title>
<ns>0</ns>
<id>123</id>
<revision><text xml:space="preserve">{| class="wikitable"
! Name !! Count
|-
| Alpha || 7
|}</text></revision>
</page>
</mediawiki>
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "slice.bz2"
            with bz2.open(path, "wt", encoding="utf-8") as handle:
                handle.write(xml)
            pages = list(iter_pages(path))
        self.assertEqual(len(pages), 1)
        self.assertEqual(pages[0].title, "Example table page")
        self.assertIn('{| class="wikitable"', pages[0].text)
        self.assertIn("| Alpha || 7", pages[0].text)


if __name__ == "__main__":
    unittest.main()
