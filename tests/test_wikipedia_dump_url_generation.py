"""Tests for dump-backed Wikipedia Route 3 URL discovery."""

from __future__ import annotations

import gzip
import bz2
import sys
import tempfile
import unittest
from pathlib import Path

from test_support import ROOT

SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from generate_wikipedia_table_urls import (  # noqa: E402
    SubdomainSpec,
    build_spec_index,
    collect_page_dump_candidates,
    collect_title_candidates,
    is_article_title_candidate,
    matching_specs,
    normalize_title_text,
    score_title_for_spec,
    selected_specs,
)


class WikipediaDumpUrlGenerationTests(unittest.TestCase):
    """Check title-dump candidate selection without network access."""

    def test_title_filter_rejects_namespaces_and_cutoff_years(self) -> None:
        self.assertFalse(is_article_title_candidate("Category:Lists of lakes", cutoff_year=2025))
        self.assertFalse(is_article_title_candidate("2026 example election", cutoff_year=2025))
        self.assertTrue(is_article_title_candidate("List of lakes of Minnesota", cutoff_year=2025))

    def test_score_title_prefers_scoped_list_titles(self) -> None:
        spec = SubdomainSpec(
            domain="Geography",
            subdomain="lakes",
            required_terms=("lake",),
            bonus_terms=("list", "area"),
        )
        score, reasons = score_title_for_spec("List of lakes of Minnesota", spec, cutoff_year=2025)
        self.assertGreater(score, 0)
        self.assertIn("list_title", reasons)
        self.assertIn("scoped_title", reasons)

    def test_collect_title_candidates_keeps_top_titles_per_subdomain(self) -> None:
        specs = [
            SubdomainSpec("Geography", "lakes", ("lake",), ("list", "area")),
            SubdomainSpec("History", "battles", ("battle",), ("casualties", "list")),
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            dump_path = Path(tmpdir) / "titles.gz"
            with gzip.open(dump_path, "wt", encoding="utf-8") as handle:
                handle.write("List_of_lakes_of_Minnesota\n")
                handle.write("Lake\n")
                handle.write("List_of_battles_by_casualties\n")
                handle.write("Category:Battle_lists\n")
            buckets = collect_title_candidates(
                dump_path,
                specs=specs,
                per_subdomain=2,
                cutoff_year=2025,
            )
        self.assertEqual(buckets[("Geography", "lakes")][0].title, "List of lakes of Minnesota")
        self.assertEqual(buckets[("History", "battles")][0].title, "List of battles by casualties")

    def test_selected_specs_limits_domains_and_subdomains(self) -> None:
        specs = (
            SubdomainSpec("A", "a1", ("a",)),
            SubdomainSpec("A", "a2", ("a",)),
            SubdomainSpec("B", "b1", ("b",)),
            SubdomainSpec("B", "b2", ("b",)),
        )
        selected = selected_specs(specs, domain_limit=1, subdomains_per_domain=2)
        self.assertEqual([spec.subdomain for spec in selected], ["a1", "a2"])

    def test_matching_specs_uses_required_term_index(self) -> None:
        specs = [
            SubdomainSpec("Geography", "lakes", ("lake",), ("list",)),
            SubdomainSpec("Sports and Recreation", "stadiums", ("stadium",), ("capacity",)),
        ]
        normalized = normalize_title_text("List of lakes of Example")
        matches = matching_specs(normalized, normalized.split(), build_spec_index(specs))
        self.assertEqual([(spec.domain, spec.subdomain) for spec in matches], [("Geography", "lakes")])

    def test_collect_page_dump_candidates_uses_wikitext_tables(self) -> None:
        specs = [SubdomainSpec("Geography", "lakes", ("lake",), ("list", "area"))]
        page_xml = """<mediawiki>
<page>
<title>List of lakes of Example</title>
<ns>0</ns>
<revision><text xml:space="preserve">{| class="wikitable sortable"
! Lake !! Area
|-
| Alpha || 12
|}</text></revision>
</page>
</mediawiki>
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            dump_path = Path(tmpdir) / "slice.bz2"
            with bz2.open(dump_path, "wt", encoding="utf-8") as handle:
                handle.write(page_xml)
            buckets, stats = collect_page_dump_candidates(
                [dump_path],
                specs=specs,
                per_subdomain=2,
                cutoff_year=2025,
            )
        self.assertEqual(stats["pages_seen"], 1)
        self.assertEqual(stats["table_like_pages_seen"], 1)
        self.assertEqual(buckets[("Geography", "lakes")][0].title, "List of lakes of Example")


if __name__ == "__main__":
    unittest.main()
