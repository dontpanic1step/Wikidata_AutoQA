"""Tests for template-status index helpers."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.template_status import _build_status_detail, _resolve_template_status


class TemplateStatusTests(unittest.TestCase):
    """Check canonical template-status resolution."""

    def test_proven_status_takes_precedence(self) -> None:
        status = _resolve_template_status(
            "film_director",
            {"film_director": {"question": "Who directed X?", "answer": "Y"}},
            {"status": "rejected_only"},
            [],
        )
        self.assertEqual(status, "proven")

    def test_rejected_only_is_preserved(self) -> None:
        status = _resolve_template_status(
            "festival_host_city",
            {},
            {"status": "rejected_only"},
            [],
        )
        self.assertEqual(status, "rejected_only")

    def test_error_status_is_preserved(self) -> None:
        status = _resolve_template_status(
            "person_birth_date",
            {},
            {"status": "error:TimeoutError"},
            [],
        )
        self.assertEqual(status, "error")

    def test_no_result_maps_to_unproven_no_result(self) -> None:
        status = _resolve_template_status(
            "bridge_architect",
            {},
            {"status": "no_result"},
            [],
        )
        self.assertEqual(status, "unproven_no_result")

    def test_filtered_accepted_record_maps_to_rejected_only(self) -> None:
        status = _resolve_template_status(
            "medical_school_country",
            {},
            {"status": "accepted"},
            ["subject_topic_mismatch"],
        )
        self.assertEqual(status, "rejected_only")

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

if __name__ == "__main__":
    unittest.main()
