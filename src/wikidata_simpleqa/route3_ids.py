"""Stable Route 3 record identifiers."""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from typing import Any


def route3_record_id(record: dict[str, Any], *, run_date: object = "") -> str:
    """Return the stable Route 3 ID for one record, if its triadic page-ID entry is known."""
    entry = route3_page_id_entry(record)
    page_id = _positive_int(entry.get("page_id"))
    answer_type = _slug(entry.get("answer_type"))
    table_type = _slug(entry.get("table_type"))
    date_slug = _date_slug(run_date or route3_record_run_date(record))
    if page_id is None or not answer_type or not table_type or not date_slug:
        return ""
    return f"route3_{date_slug}_p{page_id}_{answer_type}_{table_type}"


def assign_unique_route3_record_ids(records: list[dict[str, Any]], *, run_date: object = "") -> None:
    """Assign stable Route 3 IDs, adding a deterministic question hash only for real collisions."""
    base_ids = [route3_record_id(record, run_date=run_date) for record in records]
    counts = Counter(base_id for base_id in base_ids if base_id)
    for record, base_id in zip(records, base_ids):
        if not base_id:
            continue
        record["id"] = base_id if counts[base_id] == 1 else f"{base_id}_{_question_hash(record)}"


def route3_page_id_entry(record: dict[str, Any]) -> dict[str, Any]:
    """Return the triadic page-ID entry stored on a Route 3 record, when available."""
    metadata = record.get("source_metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
    explicit = metadata.get("page_id_list_entry")
    if isinstance(explicit, dict):
        return dict(explicit)
    return {
        "page_id": metadata.get("page_id") or record.get("page_id"),
        "answer_type": record.get("answer_type") or metadata.get("answer_type"),
        "table_type": _record_table_type(record, metadata),
    }


def route3_record_run_date(record: dict[str, Any]) -> str:
    """Return the best stored run date for one Route 3 record."""
    metadata = record.get("source_metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
    for source in (record, metadata):
        for key in ("run_date", "route3_run_date", "recipe_run_date", "recipe_segment_run_date"):
            value = source.get(key) if isinstance(source, dict) else ""
            if _date_slug(value):
                return str(value)
    streaming = metadata.get("streaming_discovery")
    if isinstance(streaming, dict) and _date_slug(streaming.get("run_date")):
        return str(streaming.get("run_date"))
    return ""


def _record_table_type(record: dict[str, Any], metadata: dict[str, Any]) -> Any:
    selected = metadata.get("selected_source_table")
    if isinstance(selected, dict) and selected.get("table_type"):
        return selected.get("table_type")
    for source in (record, metadata):
        if not isinstance(source, dict):
            continue
        for key in ("table_type", "source_channel", "recipe_table_type"):
            if source.get(key):
                return source.get(key)
    source_types = metadata.get("table_source_types")
    if isinstance(source_types, list) and len(source_types) == 1:
        return source_types[0]
    return ""


def _positive_int(value: object) -> int | None:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _date_slug(value: object) -> str:
    text = str(value or "").strip()
    match = re.search(r"(20\d{2}|19\d{2})[-_]?(\d{2})[-_]?(\d{2})", text)
    if not match:
        return ""
    return "".join(match.groups())


def _slug(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower()).strip("_")


def _question_hash(record: dict[str, Any]) -> str:
    key = "\n".join(
        str(record.get(field) or "")
        for field in ("question", "answer", "answer_type")
    )
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:8]
