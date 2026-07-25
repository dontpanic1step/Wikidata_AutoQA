"""Durable segment manifests, page allocations, and attempt ledgers for Route 3."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4

from .wikipedia_streaming import PageIdStreamState


SEGMENT_MANIFEST_VERSION = 2
PAGE_ALLOCATION_SCHEMA_VERSION = 1
PAGE_ATTEMPT_SCHEMA_VERSION = 2
SEGMENT_MANIFEST_STATUSES = {"incomplete", "complete"}
SEGMENT_BLOCKING_REASONS = {"external_service", "ambiguous"}
PAGE_ALLOCATION_SOURCES = {"cache", "fresh"}
PAGE_ATTEMPT_STATUSES = {"accepted", "rejected", "rerun"}


def utc_now_iso() -> str:
    """Return a UTC timestamp for durable artifact metadata."""
    return datetime.now(timezone.utc).isoformat()


def canonical_json_sha256(payload: Any) -> str:
    """Hash one JSON-compatible value using a stable encoding."""
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    """Return the SHA-256 digest of one file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_write_json(path: Path, payload: Any) -> None:
    """Write one JSON document using a sibling temporary file and os.replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.{os.getpid()}.{uuid4().hex}.tmp")
    temp_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temp_path, path)


def atomic_write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    """Write one JSONL artifact atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.{os.getpid()}.{uuid4().hex}.tmp")
    with temp_path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    os.replace(temp_path, path)


def build_segment_fingerprint(inputs: dict[str, Any]) -> dict[str, Any]:
    """Return the immutable fingerprint record for resolved segment inputs."""
    resolved = json.loads(json.dumps(inputs, ensure_ascii=False, sort_keys=True))
    return {"sha256": canonical_json_sha256(resolved), "inputs": resolved}


def create_segment_manifest(
    *,
    run_group_id: str,
    segment_id: str,
    fingerprint: dict[str, Any],
    artifacts: dict[str, str],
) -> dict[str, Any]:
    """Create an incomplete formal segment manifest."""
    now = utc_now_iso()
    return {
        "manifest_version": SEGMENT_MANIFEST_VERSION,
        "run_group_id": run_group_id,
        "segment_id": segment_id,
        "status": "incomplete",
        "blocking_reasons": [],
        "fingerprint": fingerprint,
        "artifacts": dict(artifacts),
        "created_at_utc": now,
        "updated_at_utc": now,
    }


def load_segment_manifest(path: Path) -> dict[str, Any] | None:
    """Load a segment manifest when it exists."""
    if not path.exists():
        return None
    return _load_json_object(path, artifact_name="Segment manifest")


def require_matching_fingerprint(
    manifest: dict[str, Any],
    fingerprint: dict[str, Any],
    *,
    path: Path,
) -> None:
    """Reject legacy resume and reuse with a different segment fingerprint."""
    version = int(manifest.get("manifest_version", 0) or 0)
    if version != SEGMENT_MANIFEST_VERSION:
        status = str(manifest.get("status", "incomplete"))
        raise ValueError(
            f"Segment manifest schema {version} is not resumable under schema "
            f"{SEGMENT_MANIFEST_VERSION}: {path} (status={status}). Use a new run."
        )
    existing = manifest.get("fingerprint", {})
    existing_hash = str(existing.get("sha256", "")) if isinstance(existing, dict) else ""
    requested_hash = str(fingerprint.get("sha256", ""))
    if existing_hash != requested_hash:
        raise ValueError(
            f"Segment fingerprint mismatch for {path}: existing={existing_hash} "
            f"requested={requested_hash}. Use a new run or top-up segment."
        )


def derive_segment_manifest_state(
    manifest: dict[str, Any],
    index: SegmentLedgerIndex,
    external_call_records: Iterable[dict[str, Any]] = (),
) -> dict[str, Any]:
    """Derive segment status and blocking reasons from durable records."""
    fingerprint = manifest.get("fingerprint", {})
    inputs = fingerprint.get("inputs", {}) if isinstance(fingerprint, dict) else {}
    target = int(inputs.get("page_attempt_count", 0) or 0)
    latest = latest_page_attempts(index.attempts)
    blocking_reasons: set[str] = set()
    unresolved_external_calls = 0
    for record in external_call_records:
        state = str(record.get("state", ""))
        if state == "ambiguous_external_call":
            blocking_reasons.add("ambiguous")
            unresolved_external_calls += 1
        elif state == "blocked_external_service":
            blocking_reasons.add("external_service")
            unresolved_external_calls += 1
        elif state == "intent":
            unresolved_external_calls += 1
    terminal_page_ids = {
        page_id
        for page_id, attempt in latest.items()
        if str(attempt.get("status", "")) in {"accepted", "rejected"}
    }
    complete = (
        target > 0
        and len(index.primary_page_ids) == target
        and terminal_page_ids == index.primary_page_ids
        and unresolved_external_calls == 0
        and not blocking_reasons
    )
    return {
        "status": "complete" if complete else "incomplete",
        "blocking_reasons": sorted(blocking_reasons),
    }


def update_segment_manifest(
    path: Path,
    manifest: dict[str, Any],
    *,
    segment_state: dict[str, Any],
    ledger_summary: dict[str, Any],
    pre_review_quantity_prediction: dict[str, Any],
) -> dict[str, Any]:
    """Persist record-derived segment state without changing its fingerprint."""
    status = str(segment_state.get("status", ""))
    blocking_reasons = {
        str(reason)
        for reason in segment_state.get("blocking_reasons", [])
    }
    if status not in SEGMENT_MANIFEST_STATUSES:
        raise ValueError(f"Unsupported segment status: {status}")
    if not blocking_reasons.issubset(SEGMENT_BLOCKING_REASONS):
        raise ValueError(f"Unsupported segment blocking reasons: {sorted(blocking_reasons)}")
    if status == "complete" and blocking_reasons:
        raise ValueError("A complete segment cannot have blocking reasons")
    updated = dict(manifest)
    updated["status"] = status
    updated["blocking_reasons"] = sorted(blocking_reasons)
    updated["ledger_summary"] = dict(ledger_summary)
    updated["pre_review_quantity_prediction"] = dict(pre_review_quantity_prediction)
    updated["updated_at_utc"] = utc_now_iso()
    atomic_write_json(path, updated)
    return updated

def page_allocation_path(
    allocation_dir: Path,
    allocation_ordinal: int,
    canonical_page_id: int,
) -> Path:
    """Return the canonical path for one immutable page allocation."""
    if allocation_ordinal < 1 or canonical_page_id < 1:
        raise ValueError("allocation_ordinal and canonical_page_id must be positive")
    return allocation_dir / f"a{allocation_ordinal:06d}_p{canonical_page_id}.json"


def page_attempt_path(ledger_dir: Path, canonical_page_id: int, attempt_number: int) -> Path:
    """Return the canonical file path for one page attempt."""
    if canonical_page_id < 1 or attempt_number not in {1, 2}:
        raise ValueError("canonical_page_id must be positive and attempt_number must be 1 or 2")
    return ledger_dir / f"p{canonical_page_id}_attempt{attempt_number:03d}.json"


def load_page_allocations(allocation_dir: Path) -> list[dict[str, Any]]:
    """Load page allocations from one segment directory in stable ordinal order."""
    if not allocation_dir.exists():
        return []
    rows = [
        _load_json_object(path, artifact_name="Page allocation")
        for path in sorted(allocation_dir.glob("a*_p*.json"))
    ]
    return sorted(rows, key=lambda row: int(row["allocation_ordinal"]))


def load_page_attempts(ledger_dir: Path) -> list[dict[str, Any]]:
    """Load page attempts from one segment directory in stable page/attempt order."""
    if not ledger_dir.exists():
        return []
    attempts: list[dict[str, Any]] = []
    for path in sorted(ledger_dir.glob("p*_attempt*.json")):
        payload = _load_json_object(path, artifact_name="Page-attempt ledger")
        payload["ledger_path"] = str(path)
        attempts.append(payload)
    return sorted(
        attempts,
        key=lambda row: (int(row["canonical_page_id"]), int(row["attempt_number"])),
    )


def latest_page_attempts(attempts: Iterable[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    """Return the highest committed attempt for each canonical page ID."""
    latest: dict[int, dict[str, Any]] = {}
    for attempt in attempts:
        page_id = int(attempt["canonical_page_id"])
        previous = latest.get(page_id)
        if previous is None or int(attempt["attempt_number"]) > int(previous["attempt_number"]):
            latest[page_id] = attempt
    return latest


class SegmentLedgerIndex:
    """Hold one startup scan of a segment ledger and update it on commits."""

    def __init__(
        self,
        *,
        allocation_dir: Path,
        attempt_dir: Path,
        run_group_id: str,
        segment_id: str,
        run_group_segments_dir: Path | None = None,
    ) -> None:
        self.allocation_dir = Path(allocation_dir)
        self.attempt_dir = Path(attempt_dir)
        self.run_group_id = str(run_group_id)
        self.segment_id = str(segment_id)
        self.run_group_segments_dir = (
            Path(run_group_segments_dir)
            if run_group_segments_dir is not None
            else self.allocation_dir.parent.parent
        )
        self.scan_counts = {"allocations": 0, "attempts": 0}
        self._run_group_allocations: dict[int, dict[str, Any]] = {}
        self._segment_allocations: dict[int, dict[str, Any]] = {}
        self._segment_ordinals: dict[int, int] = {}
        self._attempts_by_page: dict[int, list[dict[str, Any]]] = {}
        self._scan_startup_files()

    @property
    def allocations(self) -> list[dict[str, Any]]:
        """Return current-segment allocations in ordinal order."""
        return sorted(
            (dict(row) for row in self._segment_allocations.values()),
            key=lambda row: int(row["allocation_ordinal"]),
        )

    @property
    def attempts(self) -> list[dict[str, Any]]:
        """Return current-segment attempts in stable page/attempt order."""
        return [
            dict(attempt)
            for page_id in sorted(self._attempts_by_page)
            for attempt in self._attempts_by_page[page_id]
        ]

    @property
    def primary_page_ids(self) -> set[int]:
        """Return page IDs whose immutable allocations consume primary budget."""
        return set(self._segment_allocations)

    @property
    def pending_primary_page_ids(self) -> list[int]:
        """Return allocated pages that have not started attempt001."""
        return [
            int(row["canonical_page_id"])
            for row in self.allocations
            if not self._attempts_by_page.get(int(row["canonical_page_id"]))
        ]

    def allocation_for(self, canonical_page_id: int) -> dict[str, Any] | None:
        """Return the current-segment allocation for a page."""
        row = self._segment_allocations.get(int(canonical_page_id))
        return dict(row) if row is not None else None

    def latest_attempt_for(self, canonical_page_id: int) -> dict[str, Any] | None:
        """Return the highest committed attempt for one allocated page."""
        rows = self._attempts_by_page.get(int(canonical_page_id), [])
        return dict(rows[-1]) if rows else None

    def page_state(self, canonical_page_id: int) -> str:
        """Derive one page state from its allocation and highest attempt."""
        page_id = int(canonical_page_id)
        if page_id not in self._segment_allocations:
            return "unallocated"
        latest = self.latest_attempt_for(page_id)
        if latest is None:
            return "pending_primary"
        status = str(latest["status"])
        if status != "rerun":
            return status
        return "rerun_eligible" if int(latest["attempt_number"]) == 1 else "rerun_exhausted"

    def next_attempt_number(self, canonical_page_id: int) -> int:
        """Derive the only valid next attempt number from committed schema."""
        page_id = int(canonical_page_id)
        if page_id not in self._segment_allocations:
            raise ValueError(f"Page {page_id} has no allocation in segment {self.segment_id}")
        rows = self._attempts_by_page.get(page_id, [])
        if not rows:
            return 1
        if len(rows) == 1 and int(rows[0]["attempt_number"]) == 1:
            return 2
        raise ValueError(f"Page {page_id} already consumed attempt002")

    @staticmethod
    def attempt_kind(attempt_number: int) -> str:
        """Derive primary or rerun identity from the schema attempt number."""
        if int(attempt_number) == 1:
            return "primary"
        if int(attempt_number) == 2:
            return "rerun"
        raise ValueError("Only attempt001 and attempt002 are valid")

    def commit_allocation(
        self,
        *,
        canonical_page_id: int,
        page_source: str,
        source_url: str = "",
        cached_archive_path: str = "",
    ) -> Path:
        """Commit one immutable allocation and update the in-memory index."""
        page_id = int(canonical_page_id)
        source = str(page_source)
        if page_id < 1:
            raise ValueError("canonical_page_id must be positive")
        if source not in PAGE_ALLOCATION_SOURCES:
            raise ValueError(f"Unsupported page allocation source: {source}")
        existing = self._run_group_allocations.get(page_id)
        if existing is not None:
            raise ValueError(
                f"Run group {self.run_group_id} already allocated page {page_id} "
                f"to segment {existing.get('segment_id', '')}"
            )
        ordinal = max(self._segment_ordinals, default=0) + 1
        path = page_allocation_path(self.allocation_dir, ordinal, page_id)
        if path.exists():
            raise FileExistsError(f"Page allocation is already committed: {path}")
        record = {
            "schema_version": PAGE_ALLOCATION_SCHEMA_VERSION,
            "run_group_id": self.run_group_id,
            "segment_id": self.segment_id,
            "canonical_page_id": page_id,
            "allocation_ordinal": ordinal,
            "page_source": source,
            "allocated_at": utc_now_iso(),
        }
        if source_url:
            record["source_url"] = str(source_url)
        if cached_archive_path:
            record["cached_archive_path"] = str(cached_archive_path)
        atomic_write_json(path, record)
        self._insert_allocation(record, path=path)
        return path

    def commit_attempt(self, payload: dict[str, Any]) -> Path:
        """Commit one immutable attempt and update the in-memory index."""
        if "primary_page_attempt" in payload:
            raise ValueError("Attempt identity is derived from attempt_number, not a caller boolean")
        page_id = int(payload["canonical_page_id"])
        attempt_number = int(payload["attempt_number"])
        expected_attempt = self.next_attempt_number(page_id)
        if attempt_number != expected_attempt:
            raise ValueError(
                f"Expected attempt{expected_attempt:03d} for page {page_id}, "
                f"received attempt{attempt_number:03d}"
            )
        if attempt_number == 2:
            previous = self._attempts_by_page[page_id][-1]
            if str(previous["status"]) != "rerun":
                raise ValueError(f"Page {page_id} is not eligible for attempt002")
        status = str(payload["status"])
        if status not in PAGE_ATTEMPT_STATUSES:
            raise ValueError(f"Unsupported page-attempt status: {status}")
        path = page_attempt_path(self.attempt_dir, page_id, attempt_number)
        if path.exists():
            raise FileExistsError(f"Page attempt is already committed: {path}")
        record = dict(payload)
        record["run_group_id"] = self.run_group_id
        record["segment_id"] = self.segment_id
        record["schema_version"] = PAGE_ATTEMPT_SCHEMA_VERSION
        record["attempt_kind"] = self.attempt_kind(attempt_number)
        record["committed_at_utc"] = utc_now_iso()
        atomic_write_json(path, record)
        self._insert_attempt(record, path=path)
        return path

    def _scan_startup_files(self) -> None:
        self.scan_counts["allocations"] += 1
        allocation_paths = (
            sorted(self.run_group_segments_dir.glob("*/page_allocations/a*_p*.json"))
            if self.run_group_segments_dir.exists()
            else []
        )
        if self.allocation_dir.exists() and not allocation_paths:
            allocation_paths = sorted(self.allocation_dir.glob("a*_p*.json"))
        for path in allocation_paths:
            self._insert_allocation(
                _load_json_object(path, artifact_name="Page allocation"),
                path=path,
            )
        self.scan_counts["attempts"] += 1
        if self.attempt_dir.exists():
            for path in sorted(self.attempt_dir.glob("p*_attempt*.json")):
                self._insert_attempt(
                    _load_json_object(path, artifact_name="Page-attempt ledger"),
                    path=path,
                )

    def _insert_allocation(self, payload: dict[str, Any], *, path: Path) -> None:
        version = int(payload.get("schema_version", 0) or 0)
        if version != PAGE_ALLOCATION_SCHEMA_VERSION:
            raise ValueError(f"Unsupported page allocation schema {version}: {path}")
        run_group_id = str(payload.get("run_group_id", ""))
        segment_id = str(payload.get("segment_id", ""))
        page_id = int(payload["canonical_page_id"])
        ordinal = int(payload["allocation_ordinal"])
        source = str(payload["page_source"])
        if run_group_id != self.run_group_id:
            return
        if source not in PAGE_ALLOCATION_SOURCES:
            raise ValueError(f"Unsupported page allocation source in {path}: {source}")
        existing = self._run_group_allocations.get(page_id)
        if existing is not None:
            raise ValueError(
                f"Duplicate primary allocation for run group {run_group_id}, page {page_id}: {path}"
            )
        row = dict(payload)
        row["allocation_path"] = str(path)
        self._run_group_allocations[page_id] = row
        if segment_id != self.segment_id:
            return
        if ordinal in self._segment_ordinals:
            raise ValueError(f"Duplicate allocation ordinal {ordinal} in segment {segment_id}: {path}")
        self._segment_allocations[page_id] = row
        self._segment_ordinals[ordinal] = page_id

    def _insert_attempt(self, payload: dict[str, Any], *, path: Path) -> None:
        version = int(payload.get("schema_version", 0) or 0)
        if version != PAGE_ATTEMPT_SCHEMA_VERSION:
            raise ValueError(f"Unsupported page-attempt schema {version}: {path}")
        run_group_id = str(payload.get("run_group_id", ""))
        segment_id = str(payload.get("segment_id", ""))
        if run_group_id != self.run_group_id or segment_id != self.segment_id:
            raise ValueError(f"Attempt identity does not match the current segment: {path}")
        page_id = int(payload["canonical_page_id"])
        attempt_number = int(payload["attempt_number"])
        if page_id not in self._segment_allocations:
            raise ValueError(f"Attempt has no current-segment allocation: {path}")
        expected_kind = self.attempt_kind(attempt_number)
        if str(payload.get("attempt_kind", "")) != expected_kind:
            raise ValueError(f"Attempt kind does not match attempt number: {path}")
        status = str(payload.get("status", ""))
        if status not in PAGE_ATTEMPT_STATUSES:
            raise ValueError(f"Unsupported page-attempt status in {path}: {status}")
        rows = self._attempts_by_page.setdefault(page_id, [])
        if any(int(row["attempt_number"]) == attempt_number for row in rows):
            raise ValueError(f"Duplicate attempt{attempt_number:03d} for page {page_id}: {path}")
        if attempt_number == 2:
            primary = next(
                (row for row in rows if int(row["attempt_number"]) == 1),
                None,
            )
            if primary is None:
                raise ValueError(f"Attempt002 has no attempt001 for page {page_id}: {path}")
            if str(primary["status"]) != "rerun":
                raise ValueError(f"Attempt002 follows an ineligible attempt001 for page {page_id}: {path}")
        row = dict(payload)
        row["ledger_path"] = str(path)
        rows.append(row)
        rows.sort(key=lambda item: int(item["attempt_number"]))


def derived_records(
    attempts: Iterable[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Derive accepted, rejected, and rerun outputs from latest page attempts."""
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    rerun: list[dict[str, Any]] = []
    for page_id, attempt in sorted(latest_page_attempts(attempts).items()):
        status = str(attempt["status"])
        if status == "accepted":
            accepted.extend(_record_dicts(attempt.get("accepted_records", [])))
            rejected.extend(_record_dicts(attempt.get("rejected_records", [])))
        elif status == "rejected":
            rejected.extend(_record_dicts(attempt.get("rejected_records", [])))
        else:
            rerun.append(
                {
                    "status": "rerun",
                    "page_id": page_id,
                    "url": attempt.get("canonical_page_url", ""),
                    "reason": attempt.get("reason", ""),
                    **dict(attempt.get("error_details", {})),
                }
            )
    return accepted, rejected, rerun


def rebuild_derived_outputs(
    index: SegmentLedgerIndex,
    *,
    accepted_path: Path,
    rejected_path: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Rebuild endpoint JSONL files from the current in-memory ledger index."""
    accepted, rejected, rerun = derived_records(index.attempts)
    atomic_write_jsonl(accepted_path, accepted)
    atomic_write_jsonl(rejected_path, rejected)
    return accepted, rejected, rerun


def recover_stream_state_from_ledger(
    state: PageIdStreamState,
    index: SegmentLedgerIndex,
) -> dict[str, int]:
    """Project authoritative allocation and attempt records into runtime telemetry."""
    latest = latest_page_attempts(index.attempts)
    allocated_page_ids = index.primary_page_ids
    state.accepted_ids.difference_update(allocated_page_ids)
    state.rejected_ids.difference_update(allocated_page_ids)
    state.in_progress_ids.difference_update(allocated_page_ids)
    state.rerun_pool = [page_id for page_id in state.rerun_pool if page_id not in allocated_page_ids]
    for page_id in index.pending_primary_page_ids:
        state.used_ids.add(page_id)
        state.in_progress_ids.add(page_id)
    for page_id, attempt in latest.items():
        state.used_ids.add(page_id)
        status = str(attempt["status"])
        if status == "accepted":
            state.accepted_ids.add(page_id)
            state.failure_reasons.pop(page_id, None)
            state.rerun_error_details.pop(page_id, None)
        elif status == "rejected":
            state.rejected_ids.add(page_id)
            state.failure_reasons[page_id] = str(attempt.get("reason", ""))
            state.rerun_error_details.pop(page_id, None)
        else:
            state.rerun_pool.append(page_id)
            state.failure_reasons[page_id] = str(attempt.get("reason", ""))
            details = dict(attempt.get("error_details", {}))
            if details:
                state.rerun_error_details[page_id] = {
                    str(key): str(value) for key, value in details.items()
                }
    if allocated_page_ids:
        state._record_event(
            "recover_from_page_attempt_ledger",
            sorted(allocated_page_ids),
            "allocation_and_attempt_ledger_authoritative",
        )
        state.save()
    return {
        "allocated_pages": len(allocated_page_ids),
        "committed_pages": len(latest),
        "pending_primary_pages": len(index.pending_primary_page_ids),
        "accepted_pages": sum(str(row["status"]) == "accepted" for row in latest.values()),
        "rejected_pages": sum(str(row["status"]) == "rejected" for row in latest.values()),
        "rerun_pages": sum(str(row["status"]) == "rerun" for row in latest.values()),
    }


def ledger_summary(index: SegmentLedgerIndex) -> dict[str, Any]:
    """Return compact counts derived from allocations and highest attempts."""
    latest = latest_page_attempts(index.attempts)
    return {
        "allocation_files": len(index.allocations),
        "attempt_files": len(index.attempts),
        "committed_pages": len(latest),
        "pending_primary_pages": len(index.pending_primary_page_ids),
        "primary_pages": len(index.primary_page_ids),
        "accepted_pages": sum(str(row["status"]) == "accepted" for row in latest.values()),
        "rejected_pages": sum(str(row["status"]) == "rejected" for row in latest.values()),
        "rerun_pages": sum(str(row["status"]) == "rerun" for row in latest.values()),
    }


def rebuild_summary_from_ledger(
    summary_path: Path,
    index: SegmentLedgerIndex,
    *,
    base_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Rebuild ledger-derived summary fields and atomically write the summary."""
    summary = dict(base_summary or {})
    latest = latest_page_attempts(index.attempts)
    accepted, rejected, _ = derived_records(index.attempts)
    primary_page_ids = sorted(index.primary_page_ids)
    summary.update(
        {
            "attempted_page_ids": len(primary_page_ids),
            "attempted_page_ids_unique": len(primary_page_ids),
            "page_ids": primary_page_ids,
            "accepted": len(accepted),
            "rejected": len(rejected),
            "rerun": sum(str(attempt["status"]) == "rerun" for attempt in latest.values()),
            "page_allocation_ledger_dir": str(index.allocation_dir),
            "page_attempt_ledger_dir": str(index.attempt_dir),
            "page_attempt_ledger": ledger_summary(index),
        }
    )
    atomic_write_json(summary_path, summary)
    return summary


def _load_json_object(path: Path, *, artifact_name: str) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{artifact_name} must contain a JSON object: {path}")
    return dict(payload)


def _record_dicts(values: Any) -> list[dict[str, Any]]:
    if not isinstance(values, list):
        return []
    return [dict(value) for value in values if isinstance(value, dict)]
