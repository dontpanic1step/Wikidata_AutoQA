"""Inspect and resolve ambiguous Route 3 external-call records."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from .route3_external_calls import ExternalCallRecordStore
from .route3_run_ledger import atomic_write_json, utc_now_iso


AMBIGUOUS_REPORT_SCHEMA_VERSION = 1
POSSIBLE_DUPLICATE_BILLING_NOTE = (
    "Retry may duplicate a billed request because delivery of the prior call is unknown."
)


def scan_ambiguous_external_calls(root: Path) -> list[dict[str, Any]]:
    """Return the latest unresolved attempt for each logical external call."""
    root = Path(root)
    attempts_by_call: dict[tuple[int, str], dict[int, dict[str, Any]]] = {}
    if not root.exists():
        return []
    for intent_path in sorted(root.glob("p*/c_*/attempt*/intent.json")):
        intent = _load_record(intent_path)
        page_id = int(intent["canonical_page_id"])
        call_key = str(intent["call_key"])
        attempt = int(intent["call_attempt"])
        attempt_dir = intent_path.parent
        attempts_by_call.setdefault((page_id, call_key), {})[attempt] = {
            "intent": intent,
            "response": _load_optional_record(attempt_dir / "response.json"),
            "http_error": _load_optional_record(attempt_dir / "http_error.json"),
            "resolution": _load_optional_record(attempt_dir / "resolution.json"),
            "abandoned": _load_optional_record(attempt_dir / "abandoned_ambiguous.json"),
        }

    rows: list[dict[str, Any]] = []
    for (page_id, call_key), attempts in sorted(attempts_by_call.items()):
        latest_attempt = max(attempts)
        records = attempts[latest_attempt]
        if records["response"] is not None or records["http_error"] is not None:
            continue
        resolution_payload = dict((records["resolution"] or {}).get("payload", {}))
        resolution_action = str(resolution_payload.get("action", ""))
        if records["abandoned"] is not None or resolution_action == "abandon":
            continue
        intent = records["intent"]
        request_payload = dict(intent.get("payload", {})).get("request_payload", {})
        if not isinstance(request_payload, dict):
            request_payload = {}
        retry_authorized = latest_attempt == 1 and resolution_action == "retry"
        rows.append(
            {
                "state": "ambiguous_external_call",
                "page_id": page_id,
                "allocation": page_id,
                "attempt": latest_attempt,
                "call_purpose": _call_purpose(call_key),
                "call_key": call_key,
                "model": str(request_payload.get("model", "")),
                "request_hash": str(intent.get("request_hash", "")),
                "intent_time": str(intent.get("committed_at_utc", "")),
                "error": "intent_without_definite_outcome",
                "retry_eligibility": (
                    "retry_authorized"
                    if retry_authorized
                    else ("eligible" if latest_attempt == 1 else "attempt003_forbidden")
                ),
                "possible_duplicate_billing": True,
                "possible_duplicate_billing_note": POSSIBLE_DUPLICATE_BILLING_NOTE,
            }
        )
    return rows


def resolve_ambiguous_external_calls(root: Path, *, action: str) -> list[dict[str, Any]]:
    """Apply one explicit batch action to the current unresolved calls."""
    normalized_action = str(action).strip().lower()
    if normalized_action not in {"retry", "abandon"}:
        raise ValueError("Ambiguous resolution action must be 'retry' or 'abandon'")
    rows = scan_ambiguous_external_calls(root)
    if normalized_action == "retry":
        forbidden = [row for row in rows if int(row["attempt"]) >= 2]
        if forbidden:
            raise ValueError("attempt002 is ambiguous; attempt003 is forbidden, use abandon")
    acted: list[dict[str, Any]] = []
    for row in rows:
        page_id = int(row["page_id"])
        call_key = str(row["call_key"])
        attempt = int(row["attempt"])
        store = ExternalCallRecordStore(Path(root), canonical_page_id=page_id)
        intent = store.load(call_key=call_key, record_kind="intent", call_attempt=attempt)
        if intent is None:
            raise ValueError(f"Ambiguous call has no intent: {call_key}")
        request_hash = str(intent["request_hash"])
        audit_payload = {
            "action": normalized_action,
            "acted_at_utc": utc_now_iso(),
            "possible_duplicate_billing": normalized_action == "retry",
            "possible_duplicate_billing_note": (
                POSSIBLE_DUPLICATE_BILLING_NOTE if normalized_action == "retry" else ""
            ),
        }
        if normalized_action == "retry":
            if row["retry_eligibility"] == "retry_authorized":
                continue
            store.commit(
                call_key=call_key,
                record_kind="resolution",
                request_hash=request_hash,
                payload=audit_payload,
                call_attempt=attempt,
            )
        else:
            if store.load(
                call_key=call_key,
                record_kind="resolution",
                call_attempt=attempt,
            ) is None:
                store.commit(
                    call_key=call_key,
                    record_kind="resolution",
                    request_hash=request_hash,
                    payload=audit_payload,
                    call_attempt=attempt,
                )
            store.commit(
                call_key=call_key,
                record_kind="abandoned_ambiguous",
                request_hash=request_hash,
                payload=audit_payload,
                call_attempt=attempt,
            )
        acted.append({**row, "resolution_action": normalized_action})
    return acted


def write_ambiguous_external_call_reports(
    root: Path,
    *,
    json_path: Path,
    markdown_path: Path,
) -> list[dict[str, Any]]:
    """Write deterministic JSON and Markdown reports for unresolved calls."""
    rows = scan_ambiguous_external_calls(root)
    atomic_write_json(
        Path(json_path),
        {
            "schema_version": AMBIGUOUS_REPORT_SCHEMA_VERSION,
            "unresolved_count": len(rows),
            "calls": rows,
        },
    )
    lines = [
        "# Ambiguous External Calls",
        "",
        f"Unresolved calls: {len(rows)}",
        "",
    ]
    if rows:
        lines.extend(
            [
                (
                    "| Allocation | Attempt | Purpose | Model | Call key | Request hash | "
                    "Intent time | Retry eligibility | Error | Duplicate billing |"
                ),
                "| ---: | ---: | --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for row in rows:
            lines.append(
                (
                    "| {allocation} | {attempt} | {purpose} | {model} | {key} | {request_hash} | "
                    "{intent_time} | {eligibility} | {error} | {billing} |"
                ).format(
                    allocation=row["allocation"],
                    attempt=row["attempt"],
                    purpose=_escape_markdown(row["call_purpose"]),
                    model=_escape_markdown(row["model"]),
                    key=_escape_markdown(row["call_key"]),
                    request_hash=_escape_markdown(row["request_hash"]),
                    intent_time=_escape_markdown(row["intent_time"]),
                    eligibility=_escape_markdown(row["retry_eligibility"]),
                    error=_escape_markdown(row["error"]),
                    billing=_escape_markdown(row["possible_duplicate_billing_note"]),
                )
            )
        lines.extend(
            [
                "",
                POSSIBLE_DUPLICATE_BILLING_NOTE,
                "",
                "The JSON report contains request hashes and intent timestamps for audit.",
                "",
            ]
        )
    else:
        lines.extend(["No unresolved ambiguous external calls.", ""])
    _atomic_write_text(Path(markdown_path), "\n".join(lines))
    return rows


def _call_purpose(call_key: str) -> str:
    parts = [part for part in str(call_key).split("/") if part]
    if len(parts) >= 3 and parts[0] == "revision":
        return parts[2]
    return parts[0] if parts else ""


def _load_optional_record(path: Path) -> dict[str, Any] | None:
    return _load_record(path) if path.exists() else None


def _load_record(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"External-call record must contain a JSON object: {path}")
    return payload


def _escape_markdown(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.{os.getpid()}.{uuid4().hex}.tmp")
    temp_path.write_text(text, encoding="utf-8", newline="\n")
    os.replace(temp_path, path)
