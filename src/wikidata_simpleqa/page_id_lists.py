"""Helpers for maintaining Route 3 Wikipedia page-ID lists."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Iterable

from .wikipedia_client import normalize_wikipedia_page_id

PAGE_ID_SCALAR_KEYS = ("page_id", "pageid")
PAGE_ID_LIST_KEYS = ("page_ids", "accepted_ids", "rejected_ids", "in_progress_ids", "rerun_pool")
PAGE_ID_NESTED_KEYS = ("source_metadata", "streaming_discovery")
ROUTE3_PAGE_ID_ANSWER_TYPES = ("Person", "Place", "Number", "Date", "Other")
ROUTE3_PAGE_ID_TABLE_TYPES = ("infobox", "wikitable")


@dataclass(frozen=True, order=True, slots=True)
class PageIdListEntry:
    """One Route 3 page-ID list entry, optionally scoped by answer/table type."""

    page_id: int
    answer_type: str = ""
    table_type: str = ""

    def to_record(self) -> dict[str, object]:
        """Return the stable JSON representation."""
        return {
            "page_id": self.page_id,
            "answer_type": self.answer_type,
            "table_type": self.table_type,
        }


@dataclass(slots=True)
class PageIdDirectoryCollection:
    """Page IDs and source-file diagnostics collected from a run directory."""

    page_ids: set[int] = field(default_factory=set)
    entries: set[PageIdListEntry] = field(default_factory=set)
    files_read: list[str] = field(default_factory=list)
    skipped_files: list[str] = field(default_factory=list)
    errors: list[dict[str, str]] = field(default_factory=list)


def extract_page_ids_from_payload(payload: object, *, include_used_ids: bool = False) -> set[int]:
    """Extract positive page IDs from common Route 3 JSON/plain-text shapes."""
    page_ids: set[int] = set()
    if isinstance(payload, int):
        if payload > 0:
            page_ids.add(payload)
        return page_ids
    if isinstance(payload, str):
        stripped = payload.strip()
        if stripped.isdigit():
            page_ids.add(int(stripped))
            return page_ids
        page_id = normalize_wikipedia_page_id(stripped)
        if page_id is not None and page_id > 0:
            page_ids.add(page_id)
        return page_ids
    if isinstance(payload, list):
        for item in payload:
            page_ids.update(extract_page_ids_from_payload(item, include_used_ids=include_used_ids))
        return page_ids
    if isinstance(payload, dict):
        for key in PAGE_ID_SCALAR_KEYS:
            page_ids.update(extract_page_ids_from_payload(payload.get(key), include_used_ids=include_used_ids))
        list_keys = PAGE_ID_LIST_KEYS + (("used_ids",) if include_used_ids else ())
        for key in list_keys:
            page_ids.update(extract_page_ids_from_payload(payload.get(key), include_used_ids=include_used_ids))
        for key in PAGE_ID_NESTED_KEYS:
            nested = payload.get(key)
            if isinstance(nested, dict):
                page_ids.update(extract_page_ids_from_payload(nested, include_used_ids=include_used_ids))
    return page_ids


def read_page_id_list(path: Path, *, include_used_ids: bool = False) -> set[int]:
    """Read page IDs from a JSON list/object, JSONL file, or plain ID list."""
    return {entry.page_id for entry in read_page_id_entries(path, include_used_ids=include_used_ids)}


def read_page_id_entries(path: Path, *, include_used_ids: bool = False) -> set[PageIdListEntry]:
    """Read Route 3 page-ID entries from JSON, JSONL, or plain ID formats."""
    if path is None or not Path(path).exists():
        return set()
    text = Path(path).read_text(encoding="utf-8").strip()
    if not text:
        return set()
    try:
        payload = json.loads(text)
    except JSONDecodeError:
        return _read_page_id_entry_lines(text.splitlines(), include_used_ids=include_used_ids)
    return extract_page_id_entries_from_payload(payload, include_used_ids=include_used_ids)


def write_page_id_list(path: Path, page_ids: Iterable[int]) -> None:
    """Write a sorted JSON page-ID list."""
    clean_ids: set[int] = set()
    for value in page_ids:
        try:
            page_id = int(value)
        except (TypeError, ValueError):
            continue
        if page_id > 0:
            clean_ids.add(page_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sorted(clean_ids), indent=2) + "\n", encoding="utf-8")


def write_page_id_entries(path: Path, entries: Iterable[PageIdListEntry]) -> None:
    """Write sorted Route 3 page-ID list entries."""
    clean_entries = sorted(
        {
            entry
            for entry in entries
            if isinstance(entry, PageIdListEntry) and entry.page_id > 0
        }
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [entry.to_record() for entry in clean_entries]
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def extract_page_id_entries_from_payload(
    payload: object,
    *,
    include_used_ids: bool = False,
    default_answer_type: str = "",
    default_table_type: str = "",
) -> set[PageIdListEntry]:
    """Extract Route 3 page-ID entries from JSON-like payloads."""
    answer_type = normalize_page_id_answer_type(_record_answer_type(payload) or default_answer_type)
    table_type = normalize_page_id_table_type(_record_table_type(payload) or default_table_type)
    if isinstance(payload, (int, str)):
        return {
            PageIdListEntry(page_id=page_id, answer_type=answer_type, table_type=table_type)
            for page_id in extract_page_ids_from_payload(payload, include_used_ids=include_used_ids)
        }
    if isinstance(payload, list):
        entries: set[PageIdListEntry] = set()
        for item in payload:
            entries.update(
                extract_page_id_entries_from_payload(
                    item,
                    include_used_ids=include_used_ids,
                    default_answer_type=answer_type,
                    default_table_type=table_type,
                )
            )
        return entries
    if isinstance(payload, dict):
        entries: set[PageIdListEntry] = set()
        direct_page_ids: set[int] = set()
        for key in PAGE_ID_SCALAR_KEYS:
            direct_page_ids.update(extract_page_ids_from_payload(payload.get(key), include_used_ids=include_used_ids))
        for page_id in direct_page_ids:
            entries.add(PageIdListEntry(page_id=page_id, answer_type=answer_type, table_type=table_type))
        list_keys = PAGE_ID_LIST_KEYS + (("used_ids",) if include_used_ids else ())
        for key in list_keys:
            entries.update(
                extract_page_id_entries_from_payload(
                    payload.get(key),
                    include_used_ids=include_used_ids,
                    default_answer_type=answer_type,
                    default_table_type=table_type,
                )
            )
        for key in PAGE_ID_NESTED_KEYS:
            nested = payload.get(key)
            if isinstance(nested, dict):
                entries.update(
                    extract_page_id_entries_from_payload(
                        nested,
                        include_used_ids=include_used_ids,
                        default_answer_type=answer_type,
                        default_table_type=table_type,
                    )
                )
        return entries
    return set()


def build_page_id_entries(
    page_ids: Iterable[int],
    *,
    answer_types: Iterable[str],
    table_types: Iterable[str],
) -> set[PageIdListEntry]:
    """Build the cross product of page IDs and Route 3 answer/table contexts."""
    normalized_answer_types = tuple(normalize_page_id_answer_type(value) for value in answer_types)
    normalized_answer_types = tuple(value for value in normalized_answer_types if value) or ("",)
    normalized_table_types = tuple(normalize_page_id_table_type(value) for value in table_types)
    normalized_table_types = tuple(value for value in normalized_table_types if value) or ("",)
    entries: set[PageIdListEntry] = set()
    for raw_page_id in page_ids:
        try:
            page_id = int(raw_page_id)
        except (TypeError, ValueError):
            continue
        if page_id < 1:
            continue
        for answer_type in normalized_answer_types:
            for table_type in normalized_table_types:
                entries.add(PageIdListEntry(page_id=page_id, answer_type=answer_type, table_type=table_type))
    return entries


def page_ids_excluded_for_context(
    entries: Iterable[PageIdListEntry],
    *,
    answer_types: Iterable[str],
    table_types: Iterable[str],
) -> set[int]:
    """Return page IDs blocked by page-only entries or exact generation contexts."""
    contexts = _generation_contexts(answer_types=answer_types, table_types=table_types)
    by_page: dict[int, list[PageIdListEntry]] = {}
    for entry in entries:
        if not isinstance(entry, PageIdListEntry) or entry.page_id < 1:
            continue
        by_page.setdefault(entry.page_id, []).append(entry)
    excluded: set[int] = set()
    for page_id, page_entries in by_page.items():
        if any(not entry.answer_type and not entry.table_type for entry in page_entries):
            excluded.add(page_id)
            continue
        if contexts and any(_entry_exactly_matches_context(entry, context) for entry in page_entries for context in contexts):
            excluded.add(page_id)
    return excluded


def restore_route3_page_id_entries_from_accepted_directory(
    directory: Path,
    *,
    triadic_entries: bool = False,
) -> PageIdDirectoryCollection:
    """Restore Route 3 page-ID entries from accepted JSONL records in a directory."""
    collection = PageIdDirectoryCollection()
    root = Path(directory)
    if not root.exists():
        collection.errors.append({"path": str(root), "error": "directory_not_found"})
        return collection
    for path in sorted(root.rglob("*.jsonl")):
        if not path.is_file():
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            collection.errors.append({"path": str(path), "error": f"{type(exc).__name__}:{exc}"})
            continue
        collection.files_read.append(str(path))
        for line_number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except JSONDecodeError as exc:
                collection.errors.append(
                    {"path": str(path), "line": str(line_number), "error": f"JSONDecodeError:{exc}"}
                )
                continue
            entries = _accepted_record_page_id_entries(payload, triadic_entries=triadic_entries)
            collection.entries.update(entries)
            collection.page_ids.update(entry.page_id for entry in entries)
    return collection


def collect_route3_page_ids_from_directory(
    directory: Path,
    *,
    include_used_ids: bool = False,
) -> PageIdDirectoryCollection:
    """Collect page IDs represented by Route 3 run artifacts under one directory."""
    collection = PageIdDirectoryCollection()
    root = Path(directory)
    if not root.exists():
        collection.errors.append({"path": str(root), "error": "directory_not_found"})
        return collection
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if not _is_route3_page_id_artifact(path):
            collection.skipped_files.append(str(path))
            continue
        try:
            entries = read_page_id_entries(path, include_used_ids=include_used_ids)
        except (OSError, JSONDecodeError) as exc:
            collection.errors.append({"path": str(path), "error": f"{type(exc).__name__}:{exc}"})
            continue
        collection.files_read.append(str(path))
        collection.entries.update(entries)
        collection.page_ids.update(entry.page_id for entry in entries)
    return collection


def _read_page_id_lines(lines: Iterable[str], *, include_used_ids: bool) -> set[int]:
    return {entry.page_id for entry in _read_page_id_entry_lines(lines, include_used_ids=include_used_ids)}


def _read_page_id_entry_lines(lines: Iterable[str], *, include_used_ids: bool) -> set[PageIdListEntry]:
    entries: set[PageIdListEntry] = set()
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        try:
            payload = json.loads(stripped)
        except JSONDecodeError:
            payload = stripped
        entries.update(extract_page_id_entries_from_payload(payload, include_used_ids=include_used_ids))
    return entries


def _record_answer_type(payload: object) -> str:
    if not isinstance(payload, dict):
        return ""
    for key in ("answer_type", "recipe_answer_type"):
        value = normalize_page_id_answer_type(payload.get(key))
        if value:
            return value
    metadata = payload.get("source_metadata")
    if isinstance(metadata, dict):
        for key in ("answer_type", "recipe_answer_type"):
            value = normalize_page_id_answer_type(metadata.get(key))
            if value:
                return value
    return ""


def _record_table_type(payload: object) -> str:
    if not isinstance(payload, dict):
        return ""
    metadata = payload.get("source_metadata")
    if isinstance(metadata, dict):
        selected = metadata.get("selected_source_table")
        if isinstance(selected, dict):
            value = normalize_page_id_table_type(selected.get("table_type"))
            if value:
                return value
    for key in ("table_type", "source_channel", "recipe_table_type"):
        value = normalize_page_id_table_type(payload.get(key))
        if value:
            return value
    if isinstance(metadata, dict):
        for key in ("table_type", "source_channel", "recipe_table_type"):
            value = normalize_page_id_table_type(metadata.get(key))
            if value:
                return value
        source_types = metadata.get("table_source_types")
        if isinstance(source_types, list) and len(source_types) == 1:
            return normalize_page_id_table_type(source_types[0])
    return ""


def _accepted_record_page_id_entries(payload: object, *, triadic_entries: bool = False) -> set[PageIdListEntry]:
    if not isinstance(payload, dict):
        return set()
    if payload.get("rejection_reason") or payload.get("failing_reason"):
        return set()
    page_ids = extract_page_ids_from_payload(payload, include_used_ids=False)
    if not page_ids:
        return set()
    if triadic_entries:
        answer_type = normalize_page_id_answer_type(_record_answer_type(payload))
        table_type = normalize_page_id_table_type(_record_table_type(payload))
        if not answer_type or not table_type:
            return set()
        return {
            PageIdListEntry(page_id=page_id, answer_type=answer_type, table_type=table_type)
            for page_id in page_ids
        }
    return {
        PageIdListEntry(page_id=page_id)
        for page_id in page_ids
    }


def normalize_page_id_answer_type(value: object) -> str:
    """Return canonical Route 3 answer type text for page-ID list entries."""
    text = str(value or "").strip()
    if not text:
        return ""
    lowered = text.lower()
    for answer_type in ROUTE3_PAGE_ID_ANSWER_TYPES:
        if lowered == answer_type.lower():
            return answer_type
    return text


def normalize_page_id_table_type(value: object) -> str:
    """Return canonical Route 3 table type text for page-ID list entries."""
    text = str(value or "").strip().lower()
    if text in {"infobox", "info_box", "infoboxes"}:
        return "infobox"
    if text in {"wikitable", "wikitables", "table", "article_table", "article_tables"}:
        return "wikitable"
    return text


def _generation_contexts(*, answer_types: Iterable[str], table_types: Iterable[str]) -> set[tuple[str, str]]:
    answers = tuple(normalize_page_id_answer_type(value) for value in answer_types)
    answers = tuple(value for value in answers if value) or ("",)
    tables = tuple(normalize_page_id_table_type(value) for value in table_types)
    tables = tuple(value for value in tables if value) or ("",)
    return {(answer, table) for answer in answers for table in tables}


def _entry_exactly_matches_context(entry: PageIdListEntry, context: tuple[str, str]) -> bool:
    answer_type, table_type = context
    return bool(entry.answer_type and entry.table_type) and entry.answer_type == answer_type and entry.table_type == table_type


def _is_route3_page_id_artifact(path: Path) -> bool:
    name = path.name.lower()
    if name.endswith(".jsonl"):
        return True
    return name.endswith("_summary.json") or name.endswith("_state.json")
