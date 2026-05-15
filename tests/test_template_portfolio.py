"""Tests for template salvage-board and portfolio helpers."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.template_portfolio import (
    build_portfolio_report,
    build_salvage_board,
    default_salvage_registry_path,
    load_salvage_registry,
)
from wikidata_simpleqa.template_status import build_template_status_index
from wikidata_simpleqa.workflow import (
    status_accepted_paths,
    status_rejected_paths,
    status_summary_paths,
)


class TemplatePortfolioTests(unittest.TestCase):
    """Check salvage-board and portfolio reporting behavior."""

    def test_salvage_registry_loads_defaults(self) -> None:
        registry = load_salvage_registry(default_salvage_registry_path(ROOT))
        self.assertIn("promotion_thresholds", registry)
        self.assertIn("templates", registry)
        self.assertIn("product_manufacturer", registry["templates"])

    def test_salvage_board_infers_expected_fields(self) -> None:
        index = build_template_status_index(
            review_bundle_path=ROOT / "outputs" / "review_2026_all_generated_qas.tsv",
            summary_paths=status_summary_paths(ROOT),
            rejected_paths=status_rejected_paths(ROOT),
            accepted_paths=status_accepted_paths(ROOT),
            status_mode="best_known_semantic_status",
        )
        board = build_salvage_board(
            status_index=index,
            registry=load_salvage_registry(default_salvage_registry_path(ROOT)),
        )
        row = next(item for item in board["templates"] if item["template_key"] == "new_nature_reserve_country")
        self.assertEqual(row["domain"], "Geography")
        self.assertEqual(row["salvage_potential"], "high")
        self.assertEqual(row["salvage_stage"], "family_scope_rewrite")
        self.assertIn("direct_candidate_query_failed", row["top_request_problem_kinds"])
        self.assertEqual(row["workstream"], "A_semantic_rewrite")

    def test_portfolio_report_counts_non_proven_templates(self) -> None:
        index = build_template_status_index(
            review_bundle_path=ROOT / "outputs" / "review_2026_all_generated_qas.tsv",
            summary_paths=status_summary_paths(ROOT),
            rejected_paths=status_rejected_paths(ROOT),
            accepted_paths=status_accepted_paths(ROOT),
            status_mode="best_known_semantic_status",
        )
        board = build_salvage_board(
            status_index=index,
            registry=load_salvage_registry(default_salvage_registry_path(ROOT)),
        )
        report = build_portfolio_report(board, index)
        self.assertEqual(
            report["headline"]["non_proven_templates"],
            len(board["templates"]),
        )
        self.assertGreaterEqual(report["headline"]["proven_templates"], 1)
        self.assertIn("A_semantic_rewrite", report["workstream_counts"])


if __name__ == "__main__":
    unittest.main()
