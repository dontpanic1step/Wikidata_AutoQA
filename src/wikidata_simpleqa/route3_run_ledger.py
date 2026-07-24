"""Durable segment manifests and page-attempt ledgers for formal Route 3 runs."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .wikipedia_streaming import PageIdStreamState


SEGMENT_MANIFEST_VERSION = 1
PAGE_ATTEMPT_SCHEMA_VERSION = 1
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
    temp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temp_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temp_path, path)


def atomic_write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    """Write one JSONL artifact atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temp_path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    os.replace(temp_path, path)


def build_segment_fingerprint(inputs: dict[str, Any]) -> dict[str, Any]:
    """Return the immutable fingerprint record for resolved segment inputs."""
    resolved = json.loads(json.dumps(inputs, ensure_ascii=False, sort_keys=True))
    return {
        "sha256": canonical_json_sha256(resolved),
        "inputs": resolved,
    }


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
        "fingerprint": fingerprint,
        "artifacts": dict(artifacts),
        "created_at_utc": now,
        "updated_at_utc": now,
    }


def load_segment_manifest(path: Path) -> dict[str, Any] | None:
    """Load a segment manifest when it exists."""
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Segment manifest must contain a JSON object: {path}")
    return payload


def require_matching_fingerprint(
    manifest: dict[str, Any],
    fingerprint: dict[str, Any],
    *,
    path: Path,
) -> None:
    """Reject reuse when a segment manifest has a different fingerprint."""
    existing = manifest.get("fingerprint", {})
    existing_hash = str(existing.get("sha256", "")) if isinstance(existing, dict) else ""
    requested_hash = str(fingerprint.get("sha256", ""))
    if existing_hash != requested_hash:
        raise ValueError(
            f"Segment fingerprint mismatch for {path}: existing={existing_hash} requested={requested_hash}. "
            "Use a new run or top-up segment."
        )


def update_segment_manifest(
    path: Path,
    manifest: dict[str, Any],
    *,
    status: str,
    ledger_summary: dict[str, Any],
    pre_review_quantity_prediction: dict[str, Any],
) -> dict[str, Any]:
    """Persist an updated segment status without changing its fingerprint."""
    if status not in {"incomplete", "complete"}:
        raise ValueError(f"Unsupported segment status: {status}")
    updated = dict(manifest)
    updated["status"] = status
    updated["ledger_summary"] = dict(ledger_summary)
    updated["pre_review_quantity_prediction"] = dict(pre_review_quantity_prediction)
    updated["updated_at_utc"] = utc_now_iso()
    atomic_write_json(path, updated)
    return updated


def page_attempt_path(ledger_dir: Path, canonical_page_id: int, attempt_number: int) -> Path:
    """Return the canonical file path for one page attempt."""
    if canonical_page_id < 1 or attempt_number < 1:
        raise ValueError("canonical_page_id and attempt_number must be positive")
    return ledger_dir / f"p{canonical_page_id}_attempt{attempt_number:03d}.json"


def load_page_attempts(ledger_dir: Path) -> list[dict[str, Any]]:
    """Load committed page attempts in stable page/attempt order."""
    attempts: list[dict[str, Any]] = []
    if not ledger_dir.exists():
        return attempts
    for path in sorted(ledger_dir.glob("p*_attempt*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"Page-attempt ledger must contain a JSON object: {path}")
        payload = dict(payload)
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


def next_attempt_number(ledger_dir: Path, canonical_page_id: int) -> int:
    """Return the next uncommitted attempt number for one page."""
    attempts = [
        int(row["attempt_number"])
        for row in load_page_attempts(ledger_dir)
        if int(row["canonical_page_id"]) == canonical_page_id
    ]
    return max(attempts, default=0) + 1


def commit_page_attempt(ledger_dir: Path, payload: dict[str, Any]) -> Path:
    """Atomically commit one immutable page-attempt ledger record."""
    page_id = int(payload["canonical_page_id"])
    attempt_number = int(payload["attempt_number"])
    status = str(payload["status"])
    if status not in PAGE_ATTEMPT_STATUSES:
        raise ValueError(f"Unsupported page-attempt status: {status}")
    path = page_attempt_path(ledger_dir, page_id, attempt_number)
    if path.exists():
        raise FileExistsError(f"Page attempt is already committed: {path}")
    record = dict(payload)
    record["schema_version"] = PAGE_ATTEMPT_SCHEMA_VERSION
    record["committed_at_utc"] = utc_now_iso()
    atomic_write_json(path, record)
    return path


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
    ledger_dir: Path,
    *,
    accepted_path: Path,
    rejected_path: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Rebuild JSONL endpoints solely from committed page-attempt ledgers."""
    accepted, rejected, rerun = derived_records(load_page_attempts(ledger_dir))
    atomic_write_jsonl(accepted_path, accepted)
    atomic_write_jsonl(rejected_path, rejected)
    return accepted, rejected, rerun


def recover_stream_state_from_ledger(state: PageIdStreamState, ledger_dir: Path) -> dict[str, int]:
    """Make committed ledger decisions authoritative over the runtime state cache."""
    latest = latest_page_attempts(load_page_attempts(ledger_dir))
    ledger_page_ids = set(latest)
    state.accepted_ids.difference_update(ledger_page_ids)
    state.rejected_ids.difference_update(ledger_page_ids)
    state.in_progress_ids.difference_update(ledger_page_ids)
    state.rerun_pool = [page_id for page_id in state.rerun_pool if page_id not in ledger_page_ids]
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
                state.rerun_error_details[page_id] = {str(key): str(value) for key, value in details.items()}
    if latest:
        state._record_event("recover_from_page_attempt_ledger", sorted(latest), "ledger_authoritative")
        state.save()
    return {
        "committed_pages": len(latest),
        "accepted_pages": sum(str(row["status"]) == "accepted" for row in latest.values()),
        "rejected_pages": sum(str(row["status"]) == "rejected" for row in latest.values()),
        "rerun_pages": sum(str(row["status"]) == "rerun" for row in latest.values()),
    }


def ledger_summary(ledger_dir: Path) -> dict[str, Any]:
    """Return compact counts for one page-attempt ledger."""
    attempts = load_page_attempts(ledger_dir)
    latest = latest_page_attempts(attempts)
    primary_page_ids = {
        int(attempt["canonical_page_id"])
        for attempt in attempts
        if bool(attempt.get("primary_page_attempt", False))
    }
    return {
        "attempt_files": len(attempts),
        "committed_pages": len(latest),
        "primary_pages": len(primary_page_ids),
        "accepted_pages": sum(str(row["status"]) == "accepted" for row in latest.values()),
        "rejected_pages": sum(str(row["status"]) == "rejected" for row in latest.values()),
        "rerun_pages": sum(str(row["status"]) == "rerun" for row in latest.values()),
    }


def rebuild_summary_from_ledger(
    summary_path: Path,
    ledger_dir: Path,
    *,
    base_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Rebuild ledger-derived summary fields and atomically write the summary."""
    summary = dict(base_summary or {})
    attempts = load_page_attempts(ledger_dir)
    latest = latest_page_attempts(attempts)
    accepted, rejected, rerun = derived_records(attempts)
    primary_page_ids = sorted(
        {
            int(attempt["canonical_page_id"])
            for attempt in attempts
            if bool(attempt.get("primary_page_attempt", False))
        }
    )
    summary.update(
        {
            "attempted_page_ids": len(primary_page_ids),
            "attempted_page_ids_unique": len(primary_page_ids),
            "page_ids": primary_page_ids,
            "accepted": len(accepted),
            "rejected": len(rejected),
            "rerun": sum(str(attempt["status"]) == "rerun" for attempt in latest.values()),
            "page_attempt_ledger_dir": str(ledger_dir),
            "page_attempt_ledger": ledger_summary(ledger_dir),
        }
    )
    atomic_write_json(summary_path, summary)
    return summary


def _record_dicts(values: Any) -> list[dict[str, Any]]:
    if not isinstance(values, list):
        return []
    return [dict(value) for value in values if isinstance(value, dict)]
