from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from wikidata_simpleqa.route3_run_ledger import (
    PAGE_ALLOCATION_SCHEMA_VERSION,
    PAGE_ATTEMPT_SCHEMA_VERSION,
    SEGMENT_MANIFEST_VERSION,
    SegmentLedgerIndex,
    atomic_write_json,
    build_segment_fingerprint,
    create_segment_manifest,
    derived_records,
    ledger_summary,
    require_matching_fingerprint,
    update_segment_manifest,
)


class Route3RunLedgerTests(unittest.TestCase):
    def make_index(
        self,
        root: Path,
        *,
        segment_id: str = "segment-a",
        run_group_id: str = "run-1",
    ) -> SegmentLedgerIndex:
        segment_root = root / segment_id
        return SegmentLedgerIndex(
            allocation_dir=segment_root / "page_allocations",
            attempt_dir=segment_root / "page_attempts",
            run_group_id=run_group_id,
            segment_id=segment_id,
            run_group_segments_dir=root,
        )

    @staticmethod
    def attempt_payload(
        page_id: int,
        *,
        attempt_number: int = 1,
        status: str = "accepted",
    ) -> dict:
        accepted_records = (
            [{"id": f"accepted-{page_id}", "source_metadata": {}}]
            if status == "accepted"
            else []
        )
        rejected_records = (
            [{"id": f"rejected-{page_id}", "source_metadata": {}}]
            if status == "rejected"
            else []
        )
        return {
            "canonical_page_id": page_id,
            "canonical_page_url": f"https://en.wikipedia.org/?curid={page_id}",
            "attempt_number": attempt_number,
            "status": status,
            "reason": status,
            "accepted_records": accepted_records,
            "rejected_records": rejected_records,
            "error_details": {},
        }

    def test_same_run_group_page_cannot_have_duplicate_primary_allocation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first = self.make_index(root, segment_id="segment-a")
            first.commit_allocation(canonical_page_id=101, page_source="fresh")

            second = self.make_index(root, segment_id="segment-b")
            with self.assertRaisesRegex(ValueError, "already allocated page 101"):
                second.commit_allocation(canonical_page_id=101, page_source="cache")

    def test_allocation_without_attempt_is_pending_primary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            index = self.make_index(Path(temp_dir))
            path = index.commit_allocation(
                canonical_page_id=202,
                page_source="cache",
                source_url="https://en.wikipedia.org/?curid=202",
                cached_archive_path="cache/page_202.json",
            )

            record = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(record["schema_version"], PAGE_ALLOCATION_SCHEMA_VERSION)
            self.assertEqual(record["allocation_ordinal"], 1)
            self.assertEqual(record["page_source"], "cache")
            self.assertEqual(index.page_state(202), "pending_primary")
            self.assertEqual(index.pending_primary_page_ids, [202])
            self.assertEqual(ledger_summary(index)["primary_pages"], 1)
            self.assertEqual(ledger_summary(index)["attempt_files"], 0)

    def test_attempt001_and_attempt002_kinds_are_schema_derived(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            index = self.make_index(Path(temp_dir))
            index.commit_allocation(canonical_page_id=303, page_source="fresh")
            first_path = index.commit_attempt(
                self.attempt_payload(303, attempt_number=1, status="rerun")
            )
            second_path = index.commit_attempt(
                self.attempt_payload(303, attempt_number=2, status="accepted")
            )

            first = json.loads(first_path.read_text(encoding="utf-8"))
            second = json.loads(second_path.read_text(encoding="utf-8"))
            self.assertEqual(first["schema_version"], PAGE_ATTEMPT_SCHEMA_VERSION)
            self.assertEqual(first["attempt_kind"], "primary")
            self.assertEqual(second["attempt_kind"], "rerun")
            self.assertEqual(index.page_state(303), "accepted")
            self.assertEqual(len(index.attempts), 2)
            with self.assertRaisesRegex(ValueError, "already consumed attempt002"):
                index.next_attempt_number(303)

    def test_attempt_identity_cannot_be_supplied_by_caller_boolean(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            index = self.make_index(Path(temp_dir))
            index.commit_allocation(canonical_page_id=404, page_source="fresh")
            payload = self.attempt_payload(404)
            payload["primary_page_attempt"] = False
            with self.assertRaisesRegex(ValueError, "derived from attempt_number"):
                index.commit_attempt(payload)

    def test_attempt002_requires_rerun_attempt001_and_attempt003_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            index = self.make_index(Path(temp_dir))
            index.commit_allocation(canonical_page_id=505, page_source="fresh")
            index.commit_attempt(self.attempt_payload(505, status="accepted"))
            with self.assertRaisesRegex(ValueError, "not eligible"):
                index.commit_attempt(
                    self.attempt_payload(505, attempt_number=2, status="accepted")
                )
            with self.assertRaisesRegex(ValueError, "Only attempt001 and attempt002"):
                SegmentLedgerIndex.attempt_kind(3)

    def test_two_thousand_allocations_use_one_startup_scan(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            allocation_dir = root / "segment-a" / "page_allocations"
            for ordinal in range(1, 2001):
                atomic_write_json(
                    allocation_dir / f"a{ordinal:06d}_p{ordinal}.json",
                    {
                        "schema_version": PAGE_ALLOCATION_SCHEMA_VERSION,
                        "run_group_id": "run-1",
                        "segment_id": "segment-a",
                        "canonical_page_id": ordinal,
                        "allocation_ordinal": ordinal,
                        "page_source": "fresh",
                        "allocated_at": "2026-07-25T00:00:00+00:00",
                    },
                )

            index = self.make_index(root)
            for page_id in range(1, 2001):
                self.assertEqual(index.page_state(page_id), "pending_primary")

            self.assertEqual(index.scan_counts, {"allocations": 1, "attempts": 1})
            self.assertEqual(len(index.primary_page_ids), 2000)

    def test_schema_v1_incomplete_manifest_is_rejected(self) -> None:
        fingerprint = build_segment_fingerprint({"page_attempt_count": 20})
        manifest = {
            "manifest_version": 1,
            "run_group_id": "run-1",
            "segment_id": "segment-a",
            "status": "incomplete",
            "fingerprint": fingerprint,
        }
        with self.assertRaisesRegex(ValueError, "schema 1 is not resumable"):
            require_matching_fingerprint(
                manifest,
                fingerprint,
                path=Path("segment_manifest.json"),
            )

    def test_manifest_v2_supports_all_formal_statuses(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "segment_manifest.json"
            fingerprint = build_segment_fingerprint({"page_attempt_count": 2})
            manifest = create_segment_manifest(
                run_group_id="run-1",
                segment_id="segment-a",
                fingerprint=fingerprint,
                artifacts={},
            )
            self.assertEqual(manifest["manifest_version"], SEGMENT_MANIFEST_VERSION)
            for status in (
                "incomplete",
                "blocked_external_service",
                "needs_resolution",
                "complete",
            ):
                manifest = update_segment_manifest(
                    path,
                    manifest,
                    status=status,
                    ledger_summary={},
                    pre_review_quantity_prediction={},
                )
                self.assertEqual(manifest["status"], status)

    def test_derived_outputs_use_highest_attempt(self) -> None:
        attempts = [
            {
                **self.attempt_payload(606, attempt_number=1, status="rerun"),
                "attempt_kind": "primary",
            },
            {
                **self.attempt_payload(606, attempt_number=2, status="accepted"),
                "attempt_kind": "rerun",
            },
        ]
        accepted, rejected, rerun = derived_records(attempts)
        self.assertEqual([row["id"] for row in accepted], ["accepted-606"])
        self.assertEqual(rejected, [])
        self.assertEqual(rerun, [])


if __name__ == "__main__":
    unittest.main()
