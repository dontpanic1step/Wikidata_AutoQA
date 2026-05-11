"""Tests for workflow registries and automation helpers."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from scripts.run_stage5b_workflow import collect_problem_backlog_items, render_workflow_report
from wikidata_simpleqa.workflow import (
    default_policy_registry_path,
    default_run_artifacts,
    discovered_run_artifacts,
    load_policy_registry,
    render_problem_backlog_markdown,
    render_policy_registry_markdown,
    review_run_artifacts,
    status_accepted_paths,
    status_rejected_paths,
    status_summary_paths,
)


class WorkflowTests(unittest.TestCase):
    """Check shared workflow configuration and report rendering."""

    def test_default_run_artifacts_include_expected_sources(self) -> None:
        artifacts = default_run_artifacts(ROOT)
        names = {artifact.source_name for artifact in artifacts}
        self.assertIn("prior_proven_stage5b", names)
        self.assertIn("rerun_focus_templates_2026", names)
        self.assertIn("unproven_templates_2026", names)

    def test_review_run_artifacts_are_subset_of_all_artifacts(self) -> None:
        all_names = {artifact.source_name for artifact in default_run_artifacts(ROOT)}
        review_names = {artifact.source_name for artifact in review_run_artifacts(ROOT)}
        self.assertTrue({"prior_proven_stage5b", "rerun_nonreject_2026"}.issubset(review_names))
        self.assertNotIn("stage5_pilot", review_names)

    def test_review_run_artifacts_include_discovered_accepted_reruns(self) -> None:
        review_names = {artifact.source_name for artifact in review_run_artifacts(ROOT)}
        self.assertIn("rewrite_probe_focus_v2", review_names)

    def test_status_path_helpers_stay_in_sync(self) -> None:
        artifacts = discovered_run_artifacts(ROOT)
        self.assertEqual(len(status_summary_paths(ROOT)), len(artifacts))
        self.assertEqual(len(status_rejected_paths(ROOT)), len(artifacts))
        self.assertEqual(len(status_accepted_paths(ROOT)), len(artifacts))

    def test_discovered_run_artifacts_include_focused_live_rerun(self) -> None:
        names = {artifact.source_name for artifact in discovered_run_artifacts(ROOT)}
        self.assertIn("settled_history_focus", names)

    def test_policy_registry_loads_expected_decisions(self) -> None:
        decisions = load_policy_registry(default_policy_registry_path(ROOT))
        decision_map = {decision.domain: decision for decision in decisions}
        self.assertEqual(decision_map["ordinal_spouse"].approval_status, "approved")
        self.assertEqual(decision_map["footballer_goals_in_ordinal_tournament"].allowed_property_pids, ("P1351",))

    def test_policy_registry_markdown_mentions_reviewed_domains(self) -> None:
        markdown = render_policy_registry_markdown(
            load_policy_registry(default_policy_registry_path(ROOT))
        )
        self.assertIn("ordinal_spouse", markdown)
        self.assertIn("footballer_goals_in_ordinal_tournament", markdown)

    def test_workflow_report_renders_phase_rows(self) -> None:
        markdown = render_workflow_report(
            [
                {"phase": "offline", "status": "completed", "details": {"returncode": 0}},
                {"phase": "rebuild", "status": "completed", "details": {"commands": 3}},
            ]
        )
        self.assertIn("| offline | completed |", markdown)
        self.assertIn("| rebuild | completed |", markdown)

    def test_problem_backlog_collects_live_errors(self) -> None:
        items = collect_problem_backlog_items(
            [
                {
                    "phase": "live",
                    "status": "failed",
                    "details": {
                        "template_results": [
                            {
                                "domain": "ordinal_spouse",
                                "status": "error:URLError",
                                "error_message": "URLError: remote closed",
                            }
                        ]
                    },
                }
            ]
        )
        self.assertEqual(items[0]["scope"], "ordinal_spouse")
        self.assertIn("URLError", items[0]["evidence"])

    def test_problem_backlog_markdown_renders_items(self) -> None:
        markdown = render_problem_backlog_markdown(
            [
                {
                    "scope": "workflow",
                    "title": "Proxy instability",
                    "evidence": "RemoteDisconnected",
                    "next_step": "Retry without proxy",
                }
            ]
        )
        self.assertIn("Proxy instability", markdown)
        self.assertIn("Retry without proxy", markdown)


if __name__ == "__main__":
    unittest.main()
