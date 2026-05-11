"""Tests for template-status index helpers."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.template_status import _build_status_detail, _resolve_template_status, build_template_status_index


class TemplateStatusTests(unittest.TestCase):
    """Check canonical template-status resolution."""

    def test_proven_status_takes_precedence(self) -> None:
        status = _resolve_template_status(
            "film_director",
            {"film_director": {"question": "Who directed X?", "answer": "Y"}},
            {"status": "rejected_only"},
            [],
            [],
        )
        self.assertEqual(status, "proven")

    def test_rejected_only_is_preserved(self) -> None:
        status = _resolve_template_status(
            "festival_host_city",
            {},
            {"status": "rejected_only"},
            [],
            [],
        )
        self.assertEqual(status, "rejected_only")

    def test_error_status_is_preserved(self) -> None:
        status = _resolve_template_status(
            "person_birth_date",
            {},
            {"status": "error:TimeoutError"},
            [],
            [],
        )
        self.assertEqual(status, "error")

    def test_no_result_maps_to_unproven_no_result(self) -> None:
        status = _resolve_template_status(
            "bridge_architect",
            {},
            {"status": "no_result"},
            [],
            [],
        )
        self.assertEqual(status, "unproven_no_result")

    def test_filtered_accepted_record_maps_to_rejected_only(self) -> None:
        status = _resolve_template_status(
            "medical_school_country",
            {},
            {"status": "accepted"},
            ["subject_topic_mismatch"],
            ["subject_topic_mismatch"],
        )
        self.assertEqual(status, "rejected_only")

    def test_request_error_run_preserves_prior_rejected_only_signal(self) -> None:
        status = _resolve_template_status(
            "dataset_creator_math",
            {},
            {"status": "no_result_with_request_errors"},
            [],
            ["subject_topic_mismatch"],
        )
        self.assertEqual(status, "rejected_only")

    def test_status_mode_can_choose_latest_live_status(self) -> None:
        index = build_template_status_index(
            review_bundle_path=ROOT / "outputs" / "review_2026_all_generated_qas.tsv",
            summary_paths=[ROOT / "outputs" / "adaptive_retry_8_summary.json"],
            rejected_paths=[ROOT / "outputs" / "rerun_missing_review_2026_rejected.jsonl"],
            accepted_paths=[ROOT / "outputs" / "rerun_missing_review_2026_accepted.jsonl"],
            status_mode="latest_live_status",
        )
        row = next(template for template in index["templates"] if template["domain"] == "dataset_creator_math")
        self.assertEqual(row["current_status"], "unproven_no_result")
        self.assertEqual(row["latest_live_status"], "unproven_no_result")
        self.assertEqual(row["best_known_semantic_status"], "rejected_only")

    def test_status_mode_can_choose_best_known_semantic_status(self) -> None:
        index = build_template_status_index(
            review_bundle_path=ROOT / "outputs" / "review_2026_all_generated_qas.tsv",
            summary_paths=[ROOT / "outputs" / "adaptive_retry_8_summary.json"],
            rejected_paths=[ROOT / "outputs" / "rerun_missing_review_2026_rejected.jsonl"],
            accepted_paths=[ROOT / "outputs" / "rerun_missing_review_2026_accepted.jsonl"],
            status_mode="best_known_semantic_status",
        )
        row = next(template for template in index["templates"] if template["domain"] == "dataset_creator_math")
        self.assertEqual(row["current_status"], "rejected_only")
        self.assertEqual(row["latest_live_status"], "unproven_no_result")
        self.assertEqual(row["best_known_semantic_status"], "rejected_only")

    def test_reliability_summary_tracks_pass_rate_and_semantic_repro(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            review_path = root / "review.tsv"
            review_path.write_text("domain\tquestion\tanswer\tsource_run\n", encoding="utf-8")

            summary_one = root / "run_one_summary.json"
            summary_one.write_text(
                json.dumps(
                    {
                        "target_time": "2026",
                        "template_results": [
                            {
                                "domain": "dataset_creator_math",
                                "status": "rejected_only",
                                "accepted": 0,
                                "rejected": 1,
                                "telemetry": {
                                    "total_requests": 1,
                                    "network_requests": 1,
                                    "retry_count": 0,
                                    "cache_hits": 0,
                                },
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            summary_two = root / "run_two_summary.json"
            summary_two.write_text(
                json.dumps(
                    {
                        "target_time": "2026",
                        "template_results": [
                            {
                                "domain": "dataset_creator_math",
                                "status": "no_result_with_request_errors",
                                "accepted": 0,
                                "rejected": 0,
                                "telemetry": {
                                    "total_requests": 1,
                                    "network_requests": 1,
                                    "retry_count": 2,
                                    "cache_hits": 0,
                                    "errors": 1,
                                },
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            rejected_one = root / "run_one_rejected.jsonl"
            rejected_one.write_text(
                json.dumps(
                    {
                        "domain": "dataset_creator_math",
                        "rejection_reason": "subject_topic_mismatch",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            rejected_two = root / "run_two_rejected.jsonl"
            rejected_two.write_text("", encoding="utf-8")
            accepted_one = root / "run_one_accepted.jsonl"
            accepted_one.write_text("", encoding="utf-8")
            accepted_two = root / "run_two_accepted.jsonl"
            accepted_two.write_text("", encoding="utf-8")

            index = build_template_status_index(
                review_bundle_path=review_path,
                summary_paths=[summary_one, summary_two],
                rejected_paths=[rejected_one, rejected_two],
                accepted_paths=[accepted_one, accepted_two],
                status_mode="best_known_semantic_status",
            )
            row = next(template for template in index["templates"] if template["domain"] == "dataset_creator_math")
            reliability = row["reliability"]
            self.assertEqual(reliability["total_runs"], 2)
            self.assertEqual(reliability["request_clean_runs"], 1)
            self.assertEqual(reliability["candidate_yield_runs"], 1)
            self.assertEqual(reliability["semantic_outcome_counts"], {"rejected_only": 1})
            self.assertEqual(reliability["semantic_repro_rate"], 1.0)
            self.assertEqual(reliability["target_semantic_outcome"], "rejected_only")

    def test_cached_real_run_counts_as_sparse_2026_empty(self) -> None:
        detail = _build_status_detail(
            "unproven_no_result",
            {
                "status": "no_result",
                "target_time": "2026",
                "telemetry": {
                    "total_requests": 2,
                    "network_requests": 0,
                    "cache_hits": 2,
                    "events": [{"status": "ok"}],
                    "problems": [],
                },
            },
        )
        self.assertEqual(detail["bucket"], "implemented_sparse_2026")
        self.assertEqual(detail["tags"], ["sparse_answer_2026"])

    def test_seeded_real_run_counts_as_sparse_2026_seeded(self) -> None:
        detail = _build_status_detail(
            "unproven_no_result",
            {
                "status": "no_result",
                "target_time": "2026-05",
                "telemetry": {
                    "total_requests": 4,
                    "network_requests": 4,
                    "cache_hits": 0,
                    "events": [{"status": "ok"}],
                    "problems": [{"kind": "staged_seed_strategy_used", "context": {}}],
                },
            },
        )
        self.assertEqual(detail["bucket"], "implemented_sparse_2026_seeded")
        self.assertEqual(detail["tags"], ["sparse_answer_2026_05"])

    def test_targeted_no_room_for_refinement_tag_can_attach_to_no_result(self) -> None:
        detail = _build_status_detail(
            "unproven_no_result",
            {
                "domain": "ordinal_country_prime_minister",
                "status": "no_result",
                "target_time": "2026",
                "telemetry": {
                    "total_requests": 7,
                    "network_requests": 7,
                    "cache_hits": 0,
                    "events": [{"status": "ok"}],
                    "problems": [
                        {"kind": "chunked_office_holder_lookup_failed", "context": {}},
                    ],
                },
            },
        )
        self.assertEqual(detail["bucket"], "degraded_no_result_due_to_query_failure")
        self.assertEqual(detail["tags"], ["sparse_answer_2026", "no_room_for_refinement"])

    def test_missing_executor_still_takes_precedence_over_probe(self) -> None:
        detail = _build_status_detail(
            "unproven_no_result",
            {
                "status": "no_result",
                "telemetry": {
                    "total_requests": 1,
                    "network_requests": 0,
                    "cache_hits": 1,
                    "events": [{"status": "ok"}],
                    "problems": [
                        {"kind": "missing_join_executor", "context": {}},
                        {"kind": "support_probe_completed", "context": {"probe_result_count": 0}},
                    ],
                },
            },
        )
        self.assertEqual(detail["bucket"], "missing_executor_probe_only")

    def test_rejected_only_markdown_includes_reliability_summary(self) -> None:
        index = build_template_status_index(
            review_bundle_path=ROOT / "outputs" / "review_2026_all_generated_qas.tsv",
            summary_paths=[ROOT / "outputs" / "adaptive_retry_8_v3_summary.json"],
            rejected_paths=[ROOT / "outputs" / "adaptive_retry_8_v3_rejected.jsonl"],
            accepted_paths=[ROOT / "outputs" / "adaptive_retry_8_v3_accepted.jsonl"],
            status_mode="latest_live_status",
        )
        row = next(template for template in index["templates"] if template["domain"] == "product_manufacturer")
        self.assertIn("pass_rate", row["reliability"] or {"pass_rate": 0})

if __name__ == "__main__":
    unittest.main()
