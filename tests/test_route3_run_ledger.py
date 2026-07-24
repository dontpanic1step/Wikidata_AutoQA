"""Tests for durable Route 3 segment manifests and page-attempt ledgers."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.route3_run_ledger import (
    atomic_write_json,
    build_segment_fingerprint,
    commit_page_attempt,
    create_segment_manifest,
    derived_records,
    ledger_summary,
    load_page_attempts,
    load_segment_manifest,
    rebuild_summary_from_ledger,
    rebuild_derived_outputs,
    recover_stream_state_from_ledger,
    require_matching_fingerprint,
    update_segment_manifest,
)
from wikidata_simpleqa.wikipedia_streaming import PageIdStreamState


def attempt_payload(
    page_id: int,
    *,
    attempt_number: int = 1,
    status: str = "accepted",
    primary_page_attempt: bool = True,
) -> dict:
    """Build one minimal page-attempt payload."""
    accepted = [{"id": f"accepted-{page_id}", "question": f"Question {page_id}?"}]
    rejected = [{"id": f"rejected-{page_id}", "rejection_reason": "filtered"}]
    return {
        "run_group_id": "group",
        "segment_id": "segment",
        "canonical_page_id": page_id,
        "canonical_page_url": f"https://en.wikipedia.org/w/index.php?pageid={page_id}",
        "attempt_number": attempt_number,
        "primary_page_attempt": primary_page_attempt,
        "status": status,
        "reason": "temporary" if status == "rerun" else status,
        "generation_raw_audit": {"prompt": "prompt", "response": "response"},
        "candidates": [{"id": f"candidate-{page_id}"}],
        "accepted_records": accepted if status == "accepted" else [],
        "rejected_records": rejected if status in {"accepted", "rejected"} else [],
        "candidate_ids": [f"candidate-{page_id}"],
        "timings": {"total": 1.0},
        "error_details": {},
    }


class Route3RunLedgerTests(unittest.TestCase):
    """Check ledger authority, rebuilds, and manifest fingerprint rules."""

    def test_commit_is_immutable_and_uses_one_file_for_all_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_dir = Path(tmpdir) / "ledger"
            payload = attempt_payload(101)
            payload["candidates"] = [
                {"id": "person", "slot": "Person"},
                {"id": "date", "slot": "Date"},
            ]

            path = commit_page_attempt(ledger_dir, payload)

            self.assertEqual(path.name, "p101_attempt001.json")
            stored = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual([row["slot"] for row in stored["candidates"]], ["Person", "Date"])
            with self.assertRaises(FileExistsError):
                commit_page_attempt(ledger_dir, payload)

    def test_interruption_before_commit_can_retry_same_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_dir = Path(tmpdir) / "ledger"
            payload = attempt_payload(150)
            expected_path = ledger_dir / "p150_attempt001.json"

            with patch(
                "wikidata_simpleqa.route3_run_ledger.atomic_write_json",
                side_effect=OSError("interrupted before replace"),
            ):
                with self.assertRaisesRegex(OSError, "interrupted"):
                    commit_page_attempt(ledger_dir, payload)

            self.assertFalse(expected_path.exists())
            self.assertEqual(commit_page_attempt(ledger_dir, payload), expected_path)
    def test_ledger_recovers_state_after_commit_before_state_update(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            ledger_dir = root / "ledger"
            state_path = root / "state.json"
            state = PageIdStreamState(path=state_path)
            state.used_ids.add(202)
            state.in_progress_ids.add(202)
            state.save()
            commit_page_attempt(ledger_dir, attempt_payload(202, status="accepted"))

            reloaded = PageIdStreamState.load(state_path)
            summary = recover_stream_state_from_ledger(reloaded, ledger_dir)

            self.assertEqual(summary["accepted_pages"], 1)
            self.assertIn(202, reloaded.accepted_ids)
            self.assertNotIn(202, reloaded.in_progress_ids)
            self.assertNotIn(202, reloaded.rerun_pool)

    def test_rebuild_uses_latest_attempt_and_replaces_broken_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            ledger_dir = root / "ledger"
            accepted_path = root / "accepted.jsonl"
            rejected_path = root / "rejected.jsonl"
            commit_page_attempt(ledger_dir, attempt_payload(303, status="rerun"))
            commit_page_attempt(
                ledger_dir,
                attempt_payload(303, attempt_number=2, status="accepted", primary_page_attempt=False),
            )
            commit_page_attempt(ledger_dir, attempt_payload(404, status="rejected"))
            accepted_path.write_text('{"broken":', encoding="utf-8")
            rejected_path.write_text('{"broken":', encoding="utf-8")

            accepted, rejected, rerun = rebuild_derived_outputs(
                ledger_dir,
                accepted_path=accepted_path,
                rejected_path=rejected_path,
            )

            self.assertEqual([row["id"] for row in accepted], ["accepted-303"])
            self.assertEqual(
                [row["id"] for row in rejected],
                ["rejected-303", "rejected-404"],
            )
            self.assertEqual(rerun, [])
            self.assertEqual(len(accepted_path.read_text(encoding="utf-8").splitlines()), 1)
            self.assertEqual(ledger_summary(ledger_dir)["primary_pages"], 2)

    def test_fingerprint_mismatch_refuses_segment_reuse(self) -> None:
        first = build_segment_fingerprint({"git_sha": "a", "page_attempt_count": 10})
        second = build_segment_fingerprint({"git_sha": "b", "page_attempt_count": 10})

        manifest = create_segment_manifest(
            run_group_id="group",
            segment_id="segment",
            fingerprint=first,
            artifacts={},
        )

        require_matching_fingerprint(manifest, first, path=Path("segment_manifest.json"))
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            require_matching_fingerprint(manifest, second, path=Path("segment_manifest.json"))

    def test_summary_is_rebuilt_from_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            ledger_dir = root / "ledger"
            summary_path = root / "summary.json"
            commit_page_attempt(ledger_dir, attempt_payload(405, status="accepted"))
            summary_path.write_text('{"broken":', encoding="utf-8")

            summary = rebuild_summary_from_ledger(summary_path, ledger_dir)

            self.assertEqual(summary["attempted_page_ids"], 1)
            self.assertEqual(summary["accepted"], 1)
            self.assertEqual(summary["rejected"], 1)
            self.assertEqual(summary["rerun"], 0)
            self.assertEqual(
                json.loads(summary_path.read_text(encoding="utf-8"))["page_ids"],
                [405],
            )

    def test_top_up_manifest_does_not_modify_prior_segment(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            fingerprint = build_segment_fingerprint({"git_sha": "a"})
            first_path = root / "segment-a" / "segment_manifest.json"
            second_path = root / "segment-b" / "segment_manifest.json"
            first = create_segment_manifest(
                run_group_id="group",
                segment_id="segment-a",
                fingerprint=fingerprint,
                artifacts={},
            )
            atomic_write_json(first_path, first)
            first_text = first_path.read_text(encoding="utf-8")

            second = create_segment_manifest(
                run_group_id="group",
                segment_id="segment-b",
                fingerprint=fingerprint,
                artifacts={},
            )
            atomic_write_json(second_path, second)
            update_segment_manifest(
                second_path,
                second,
                status="complete",
                ledger_summary={"primary_pages": 10},
                pre_review_quantity_prediction={"accepted_total": 10},
            )

            self.assertEqual(first_path.read_text(encoding="utf-8"), first_text)
            self.assertEqual(load_segment_manifest(second_path)["status"], "complete")
            self.assertEqual(
                load_segment_manifest(second_path)["pre_review_quantity_prediction"]["accepted_total"],
                10,
            )

    def test_derived_records_keep_all5_slots_in_one_page_decision(self) -> None:
        payload = attempt_payload(505)
        payload["accepted_records"] = [{"id": "person"}, {"id": "date"}]

        accepted, rejected, rerun = derived_records([payload])

        self.assertEqual([row["id"] for row in accepted], ["person", "date"])
        self.assertEqual([row["id"] for row in rejected], ["rejected-505"])
        self.assertEqual(rerun, [])


if __name__ == "__main__":
    unittest.main()
