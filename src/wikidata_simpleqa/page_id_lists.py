"""Route 3 page-ID entry helpers used by the formal recipe and worker."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .wikipedia_client import normalize_wikipedia_page_id

PAGE_ID_SCALAR_KEYS = ("page_id", "pageid")
PAGE_ID_LIST_KEYS = ("page_ids", "accepted_ids", "rejected_ids", "in_progress_ids", "rerun_pool")
PAGE_ID_NESTED_KEYS = ("source_metadata", "streaming_discovery")
ROUTE3_PAGE_ID_ANSWER_TYPES = ("Person", "Place", "Number", "Date", "Other")


@dataclass(frozen=True, order=True, slots=True)
class PageIdListEntry:
    """One Route 3 page-ID entry scoped by answer and table type when available."""

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


def extract_page_ids_from_payload(payload: object) -> set[int]:
    """Extract positive page IDs from formal Route 3 payload shapes."""
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
            page_ids.update(extract_page_ids_from_payload(item))
        return page_ids
    if isinstance(payload, dict):
        for key in PAGE_ID_SCALAR_KEYS + PAGE_ID_LIST_KEYS:
            page_ids.update(extract_page_ids_from_payload(payload.get(key)))
        for key in PAGE_ID_NESTED_KEYS:
            nested = payload.get(key)
            if isinstance(nested, dict):
                page_ids.update(extract_page_ids_from_payload(nested))
    return page_ids


def extract_page_id_entries_from_payload(
    payload: object,
    *,
    default_answer_type: str = "",
    default_table_type: str = "",
) -> set[PageIdListEntry]:
    """Extract Route 3 page-ID entries from JSON-like payloads."""
    answer_type = normalize_page_id_answer_type(_record_answer_type(payload) or default_answer_type)
    table_type = normalize_page_id_table_type(_record_table_type(payload) or default_table_type)
    if isinstance(payload, (int, str)):
        return {
            PageIdListEntry(page_id=page_id, answer_type=answer_type, table_type=table_type)
            for page_id in extract_page_ids_from_payload(payload)
        }
    if isinstance(payload, list):
        entries: set[PageIdListEntry] = set()
        for item in payload:
            entries.update(
                extract_page_id_entries_from_payload(
                    item,
                    default_answer_type=answer_type,
                    default_table_type=table_type,
                )
            )
        return entries
    if isinstance(payload, dict):
        entries = {
            PageIdListEntry(page_id=page_id, answer_type=answer_type, table_type=table_type)
            for key in PAGE_ID_SCALAR_KEYS
            for page_id in extract_page_ids_from_payload(payload.get(key))
        }
        for key in PAGE_ID_LIST_KEYS:
            entries.update(
                extract_page_id_entries_from_payload(
                    payload.get(key),
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
    """Build the cross product of page IDs and Route 3 generation contexts."""
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


def normalize_page_id_answer_type(value: object) -> str:
    """Return canonical Route 3 answer type text."""
    text = str(value or "").strip()
    lowered = text.lower()
    for answer_type in ROUTE3_PAGE_ID_ANSWER_TYPES:
        if lowered == answer_type.lower():
            return answer_type
    return text


def normalize_page_id_table_type(value: object) -> str:
    """Return canonical Route 3 table type text."""
    text = str(value or "").strip().lower()
    if text in {"infobox", "info_box", "infoboxes"}:
        return "infobox"
    if text in {"wikitable", "wikitables", "table", "article_table", "article_tables"}:
        return "wikitable"
    return text


def _record_answer_type(payload: object) -> str:
    if not isinstance(payload, dict):
        return ""
    for source in (payload, payload.get("source_metadata")):
        if not isinstance(source, dict):
            continue
        for key in ("answer_type", "recipe_answer_type"):
            value = normalize_page_id_answer_type(source.get(key))
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
    for source in (payload, metadata):
        if not isinstance(source, dict):
            continue
        for key in ("table_type", "source_channel", "recipe_table_type"):
            value = normalize_page_id_table_type(source.get(key))
            if value:
                return value
    return ""
