"""Fixture-backed regression tests for workflow and status behavior."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from test_support import ROOT  # noqa: F401
from scripts.run_stage5b_workflow import collect_problem_backlog_items, render_workflow_report
from wikidata_simpleqa.template_status import build_template_status_index
from wikidata_simpleqa.workflow import discovered_run_artifacts, review_run_artifacts

FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "workflow_snapshot"


class WorkflowFixtureTests(unittest.TestCase):
    """Lock current workflow behavior against a small file fixture."""

    def test_artifact_discovery_ignores_orphan_summary_files(self) -> None:
        discovered_names = {
            artifact.source_name
            for artifact in discovered_run_artifacts(FIXTURE_ROOT)
        }
        self.assertIn("discovered_focus", discovered_names)
        self.assertNotIn("ignored", discovered_names)

    def test_review_artifacts_include_discovered_fixture_with_accepts(self) -> None:
        review_names = {
            artifact.source_name
            for artifact in review_run_artifacts(FIXTURE_ROOT)
        }
        self.assertIn("prior_proven_stage5b", review_names)
        self.assertIn("rerun_nonreject_2026", review_names)
        self.assertIn("discovered_focus", review_names)
        self.assertNotIn("ignored", review_names)

    def test_fixture_status_resolution_matches_current_behavior(self) -> None:
        fixture_outputs = FIXTURE_ROOT / "outputs"
        index = build_template_status_index(
            review_bundle_path=FIXTURE_ROOT / "review_bundle.tsv",
            summary_paths=[fixture_outputs / "fixture_status_summary.json"],
            rejected_paths=[fixture_outputs / "fixture_status_rejected.jsonl"],
            accepted_paths=[fixture_outputs / "fixture_status_accepted.jsonl"],
            status_mode="latest_live_status",
        )
        dataset_row = next(
            template
            for template in index["templates"]
            if template["domain"] == "dataset_creator_math"
        )
        accepted_row = next(
            template
            for template in index["templates"]
            if template["domain"] == "product_manufacturer"
        )
        proven_row = next(
            template
            for template in index["templates"]
            if template["domain"] == "film_director"
        )
        self.assertEqual(dataset_row["current_status"], "unproven_no_result")
        self.assertEqual(dataset_row["best_known_semantic_status"], "rejected_only")
        self.assertEqual(accepted_row["current_status"], "untracked")
        self.assertEqual(accepted_row["latest_run"]["status"], "accepted")
        self.assertEqual(proven_row["current_status"], "proven")

    def test_fixture_workflow_report_and_backlog_match_current_behavior(self) -> None:
        phase_results = json.loads(
            (FIXTURE_ROOT / "workflow_phase_results.json").read_text(encoding="utf-8")
        )
        markdown = render_workflow_report(phase_results)
        backlog = collect_problem_backlog_items(phase_results)
        self.assertIn("| offline | completed |", markdown)
        self.assertIn("| live | failed |", markdown)
        self.assertEqual(len(backlog), 1)
        self.assertEqual(backlog[0]["scope"], "ordinal_spouse")
        self.assertIn("URLError", backlog[0]["evidence"])


if __name__ == "__main__":
    unittest.main()
