"""Durable allocation-scoped records for formal Route 3 external calls."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from .route3_run_ledger import canonical_json_sha256, utc_now_iso


EXTERNAL_CALL_RECORD_SCHEMA_VERSION = 2
EXTERNAL_CALL_RECORD_KINDS = {
    "intent",
    "response",
    "http_error",
    "resolution",
    "abandoned_ambiguous",
}
EXTERNAL_CALL_ATTEMPTS = {1, 2}


def _atomic_create_json(path: Path, payload: dict[str, Any]) -> None:
    """Atomically create one complete JSON record without replacing an existing record."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.{os.getpid()}.{uuid4().hex}.tmp")
    try:
        temp_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.link(temp_path, path)
    finally:
        temp_path.unlink(missing_ok=True)


class ExternalCallRecordStore:
    """Persist immutable call-attempt records under one allocation and logical key."""

    def __init__(self, root: Path, *, canonical_page_id: int) -> None:
        self.root = Path(root)
        self.canonical_page_id = int(canonical_page_id)
        if self.canonical_page_id < 1:
            raise ValueError("canonical_page_id must be positive")

    def commit(
        self,
        *,
        call_key: str,
        record_kind: str,
        request_hash: str,
        payload: dict[str, Any],
        call_attempt: int = 1,
    ) -> Path:
        """Commit one immutable external call-attempt record."""
        kind = str(record_kind)
        attempt = int(call_attempt)
        if kind not in EXTERNAL_CALL_RECORD_KINDS:
            raise ValueError(f"Unsupported external-call record kind: {kind}")
        if attempt not in EXTERNAL_CALL_ATTEMPTS:
            raise ValueError("Only external call attempt001 and attempt002 are valid")
        normalized_hash = str(request_hash).strip()
        if not normalized_hash:
            raise ValueError("request_hash is required")
        path = self.record_path(call_key, kind, call_attempt=attempt)
        if path.exists():
            raise FileExistsError(f"External-call record is already committed: {path}")
        record = {
            "schema_version": EXTERNAL_CALL_RECORD_SCHEMA_VERSION,
            "canonical_page_id": self.canonical_page_id,
            "call_key": str(call_key),
            "call_key_hash": canonical_json_sha256(str(call_key)),
            "call_attempt": attempt,
            "record_kind": kind,
            "request_hash": normalized_hash,
            "payload": dict(payload),
            "committed_at_utc": utc_now_iso(),
        }
        _atomic_create_json(path, record)
        return path

    def load(
        self,
        *,
        call_key: str,
        record_kind: str,
        call_attempt: int = 1,
    ) -> dict[str, Any] | None:
        """Load one external call-attempt record when present."""
        path = self.record_path(call_key, record_kind, call_attempt=call_attempt)
        if not path.exists():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"External-call record must contain a JSON object: {path}")
        if int(payload.get("schema_version", 0) or 0) != EXTERNAL_CALL_RECORD_SCHEMA_VERSION:
            raise ValueError(f"Unsupported external-call record schema: {path}")
        if int(payload.get("canonical_page_id", 0) or 0) != self.canonical_page_id:
            raise ValueError(f"External-call record page mismatch: {path}")
        if str(payload.get("call_key", "")) != str(call_key):
            raise ValueError(f"External-call key mismatch: {path}")
        if int(payload.get("call_attempt", 0) or 0) != int(call_attempt):
            raise ValueError(f"External-call attempt mismatch: {path}")
        if str(payload.get("record_kind", "")) != str(record_kind):
            raise ValueError(f"External-call record kind mismatch: {path}")
        return dict(payload)

    def load_matching_outcome(
        self,
        *,
        call_key: str,
        request_hash: str,
        call_attempt: int = 1,
    ) -> dict[str, Any] | None:
        """Return a persisted definite outcome for one logical call attempt."""
        response = self.load(
            call_key=call_key,
            record_kind="response",
            call_attempt=call_attempt,
        )
        http_error = self.load(
            call_key=call_key,
            record_kind="http_error",
            call_attempt=call_attempt,
        )
        if response is not None and http_error is not None:
            raise ValueError(f"Logical call attempt has multiple definite outcomes: {call_key}")
        outcome = response or http_error
        if outcome is None:
            return None
        if str(outcome.get("request_hash", "")) != str(request_hash):
            raise ValueError(f"External-call request hash mismatch: {call_key}")
        return outcome

    def record_path(
        self,
        call_key: str,
        record_kind: str,
        *,
        call_attempt: int = 1,
    ) -> Path:
        """Return a stable allocation, logical-key, and call-attempt record path."""
        key = str(call_key).strip()
        if not key:
            raise ValueError("call_key is required")
        kind = str(record_kind)
        if kind not in EXTERNAL_CALL_RECORD_KINDS:
            raise ValueError(f"Unsupported external-call record kind: {kind}")
        attempt = int(call_attempt)
        if attempt not in EXTERNAL_CALL_ATTEMPTS:
            raise ValueError("Only external call attempt001 and attempt002 are valid")
        key_hash = canonical_json_sha256(key)
        return (
            self.root
            / f"p{self.canonical_page_id}"
            / f"c_{key_hash}"
            / f"attempt{attempt:03d}"
            / f"{kind}.json"
        )
