"""Durable public benchmark ID allocation."""

from __future__ import annotations

import json
import re
import sys
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable, Iterator

from .route3_run_ledger import atomic_write_json


PUBLIC_ID_REGISTRY_SCHEMA_VERSION = 1
DEFAULT_PUBLIC_ID_PREFIX = "simpleqa_synth"
PUBLIC_ID_MIN_WIDTH = 6
_PREFIX_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


def new_public_id_registry(
    *,
    id_prefix: str = DEFAULT_PUBLIC_ID_PREFIX,
) -> dict[str, Any]:
    """Return an empty public-ID registry."""
    _validate_prefix(id_prefix)
    return {
        "schema_version": PUBLIC_ID_REGISTRY_SCHEMA_VERSION,
        "id_prefix": id_prefix,
        "next_sequence": 1,
        "assignments": [],
    }


def load_public_id_registry(
    path: Path,
    *,
    id_prefix: str = DEFAULT_PUBLIC_ID_PREFIX,
) -> dict[str, Any]:
    """Load and validate a registry, or initialize a missing one in memory."""
    if not path.exists():
        return new_public_id_registry(id_prefix=id_prefix)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read public-ID registry {path}: {exc}") from exc
    return validate_public_id_registry(payload, expected_prefix=id_prefix)


def validate_public_id_registry(
    payload: Any,
    *,
    expected_prefix: str = DEFAULT_PUBLIC_ID_PREFIX,
) -> dict[str, Any]:
    """Return a normalized registry after enforcing its durable invariants."""
    _validate_prefix(expected_prefix)
    if not isinstance(payload, dict):
        raise ValueError("public-ID registry must be a JSON object")
    if payload.get("schema_version") != PUBLIC_ID_REGISTRY_SCHEMA_VERSION:
        raise ValueError("unsupported public-ID registry schema_version")
    if payload.get("id_prefix") != expected_prefix:
        raise ValueError(
            f"public-ID registry prefix must be {expected_prefix!r}, "
            f"got {payload.get('id_prefix')!r}"
        )
    next_sequence = payload.get("next_sequence")
    if not isinstance(next_sequence, int) or isinstance(next_sequence, bool) or next_sequence < 1:
        raise ValueError("public-ID registry next_sequence must be a positive integer")
    assignments = payload.get("assignments")
    if not isinstance(assignments, list):
        raise ValueError("public-ID registry assignments must be a list")

    normalized_assignments: list[dict[str, str]] = []
    seen_candidates: set[str] = set()
    seen_public_ids: set[str] = set()
    max_sequence = 0
    for index, assignment in enumerate(assignments):
        if not isinstance(assignment, dict):
            raise ValueError(f"public-ID assignment {index} must be an object")
        candidate_id = str(assignment.get("candidate_id") or "").strip()
        public_id = str(assignment.get("public_id") or "").strip()
        if not candidate_id:
            raise ValueError(f"public-ID assignment {index} has no candidate_id")
        sequence = _public_id_sequence(public_id, expected_prefix)
        if candidate_id in seen_candidates:
            raise ValueError(f"duplicate public-ID candidate assignment: {candidate_id}")
        if public_id in seen_public_ids:
            raise ValueError(f"duplicate public ID: {public_id}")
        seen_candidates.add(candidate_id)
        seen_public_ids.add(public_id)
        max_sequence = max(max_sequence, sequence)
        normalized_assignments.append(
            {"candidate_id": candidate_id, "public_id": public_id}
        )
    if next_sequence <= max_sequence:
        raise ValueError("public-ID registry next_sequence must exceed every assigned ID")
    normalized_assignments.sort(
        key=lambda item: _public_id_sequence(item["public_id"], expected_prefix)
    )
    return {
        "schema_version": PUBLIC_ID_REGISTRY_SCHEMA_VERSION,
        "id_prefix": expected_prefix,
        "next_sequence": next_sequence,
        "assignments": normalized_assignments,
    }


def assign_public_ids(
    candidate_records: Iterable[dict[str, str]],
    registry: dict[str, Any],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    """Assign stable public IDs without coupling them to final CSV row order."""
    updated = validate_public_id_registry(deepcopy(registry))
    records = [dict(record) for record in candidate_records]
    candidate_ids = [str(record.get("id") or "").strip() for record in records]
    if any(not candidate_id for candidate_id in candidate_ids):
        raise ValueError("every final candidate record must have an internal ID")
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError("final candidate records contain duplicate internal IDs")

    by_candidate = {
        assignment["candidate_id"]: assignment["public_id"]
        for assignment in updated["assignments"]
    }
    for candidate_id in sorted(set(candidate_ids) - set(by_candidate)):
        sequence = int(updated["next_sequence"])
        public_id = f"{updated['id_prefix']}_{sequence:0{PUBLIC_ID_MIN_WIDTH}d}"
        updated["assignments"].append(
            {"candidate_id": candidate_id, "public_id": public_id}
        )
        by_candidate[candidate_id] = public_id
        updated["next_sequence"] = sequence + 1

    public_records = []
    for record, candidate_id in zip(records, candidate_ids):
        record["id"] = by_candidate[candidate_id]
        public_records.append(record)
    public_records.sort(
        key=lambda record: _public_id_sequence(record["id"], updated["id_prefix"])
    )
    updated["assignments"].sort(
        key=lambda item: _public_id_sequence(item["public_id"], updated["id_prefix"])
    )
    return public_records, updated


def write_public_id_registry(path: Path, registry: dict[str, Any]) -> None:
    """Validate and atomically persist a public-ID registry."""
    atomic_write_json(path, validate_public_id_registry(registry))


@contextmanager
def public_id_registry_lock(path: Path) -> Iterator[None]:
    """Hold a non-blocking OS lock while allocating and publishing IDs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_name(f"{path.name}.lock")
    handle = lock_path.open("a+b")
    handle.seek(0, 2)
    if handle.tell() == 0:
        handle.write(b"\0")
        handle.flush()
    handle.seek(0)
    try:
        if sys.platform == "win32":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as exc:
        handle.close()
        raise RuntimeError(f"Public-ID registry already has an active writer: {path}") from exc
    try:
        yield
    finally:
        handle.close()


def _public_id_sequence(public_id: str, prefix: str) -> int:
    pattern = re.compile(rf"^{re.escape(prefix)}_(\d{{{PUBLIC_ID_MIN_WIDTH},}})$")
    match = pattern.fullmatch(public_id)
    if match is None:
        raise ValueError(f"invalid public ID for prefix {prefix!r}: {public_id!r}")
    return int(match.group(1))


def _validate_prefix(prefix: str) -> None:
    if _PREFIX_PATTERN.fullmatch(prefix) is None:
        raise ValueError(f"invalid public-ID prefix: {prefix!r}")
