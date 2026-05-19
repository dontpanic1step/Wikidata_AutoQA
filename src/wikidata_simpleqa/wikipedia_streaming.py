"""Streaming Wikipedia page-id discovery support for Route 3."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .wikipedia_client import normalize_wikipedia_page_id

DEFAULT_PAGE_ID_MIN = 1
DEFAULT_PAGE_ID_MAX = 80_000_000
CURID_URL_PREFIX = "https://en.wikipedia.org/w/index.php?curid="
PAGEID_URL_PREFIX = "https://en.wikipedia.org/w/index.php?pageid="
DEFAULT_TABLE_SEARCH_QUERIES = (
    'insource:"wikitable"',
)
BROAD_TABLE_SEARCH_QUERY = r"insource:/\{\|/"


def build_curid_url(page_id: int) -> str:
    """Return an English Wikipedia curid URL for one page ID."""
    if page_id < 1:
        raise ValueError("page_id must be positive")
    return f"{CURID_URL_PREFIX}{page_id}"


def build_pageid_url(page_id: int) -> str:
    """Return an internal English Wikipedia pageid URL for API parsing."""
    if page_id < 1:
        raise ValueError("page_id must be positive")
    return f"{PAGEID_URL_PREFIX}{page_id}"


def page_id_from_url(url: str) -> int | None:
    """Return a page ID from a curid/pageid URL, if present."""
    return normalize_wikipedia_page_id(url)


@dataclass(slots=True)
class PageIdStreamState:
    """Persistent state for Wikipedia page-id streaming."""

    path: Path
    used_ids: set[int] = field(default_factory=set)
    in_progress_ids: set[int] = field(default_factory=set)
    accepted_ids: set[int] = field(default_factory=set)
    rejected_ids: set[int] = field(default_factory=set)
    rerun_pool: list[int] = field(default_factory=list)
    table_search_offsets: dict[str, int] = field(default_factory=dict)
    failure_reasons: dict[int, str] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> "PageIdStreamState":
        """Load a stream state file, returning an empty state when absent."""
        if not path.exists():
            return cls(path=path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            path=path,
            used_ids=_int_set(payload.get("used_ids", [])),
            in_progress_ids=_int_set(payload.get("in_progress_ids", [])),
            accepted_ids=_int_set(payload.get("accepted_ids", [])),
            rejected_ids=_int_set(payload.get("rejected_ids", [])),
            rerun_pool=_int_list(payload.get("rerun_pool", [])),
            table_search_offsets={
                str(key): int(value)
                for key, value in dict(payload.get("table_search_offsets", {})).items()
                if _is_int_like(value)
            },
            failure_reasons={
                int(key): str(value)
                for key, value in dict(payload.get("failure_reasons", {})).items()
                if _is_int_like(key)
            },
            events=[
                event
                for event in payload.get("events", [])
                if isinstance(event, dict)
            ],
        )

    def save(self) -> None:
        """Persist state to disk."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "used_ids": sorted(self.used_ids),
            "in_progress_ids": sorted(self.in_progress_ids),
            "accepted_ids": sorted(self.accepted_ids),
            "rejected_ids": sorted(self.rejected_ids),
            "rerun_pool": self.rerun_pool.copy(),
            "table_search_offsets": dict(sorted(self.table_search_offsets.items())),
            "failure_reasons": {
                str(page_id): reason
                for page_id, reason in sorted(self.failure_reasons.items())
            },
            "events": self.events[-200:],
            "stats": self.stats(),
        }
        self.path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def recover_stale_in_progress(self, *, reason: str = "recovered_in_progress_from_previous_run") -> list[int]:
        """Move unresolved in-progress IDs into the rerun pool."""
        stale_ids = sorted(self.in_progress_ids - self.accepted_ids - self.rejected_ids)
        if not stale_ids:
            return []
        rerun_seen = set(self.rerun_pool)
        for page_id in stale_ids:
            if page_id not in rerun_seen:
                self.rerun_pool.append(page_id)
                rerun_seen.add(page_id)
            self.failure_reasons[page_id] = reason
        self.in_progress_ids.difference_update(stale_ids)
        self._record_event("recover_stale_in_progress", stale_ids, reason)
        self.save()
        return stale_ids

    def reserve_ids(
        self,
        *,
        count: int,
        lower_bound: int,
        upper_bound: int,
        rng: random.Random,
        prefer_rerun_pool: bool = True,
    ) -> list[int]:
        """Reserve up to ``count`` page IDs and persist the reservation."""
        if count < 1:
            return []
        _validate_bounds(lower_bound, upper_bound)
        selected: list[int] = []
        if prefer_rerun_pool:
            selected.extend(self._reserve_from_rerun_pool(count))
        attempts = 0
        max_attempts = max(1000, count * 100)
        possible_fresh = upper_bound - lower_bound + 1 - len(
            {
                page_id
                for page_id in self.used_ids
                if lower_bound <= page_id <= upper_bound
            }
        )
        while len(selected) < count and possible_fresh > 0:
            if attempts >= max_attempts:
                raise RuntimeError("Could not reserve enough unique Wikipedia page IDs within the configured bounds.")
            attempts += 1
            page_id = rng.randint(lower_bound, upper_bound)
            if page_id in self.used_ids:
                continue
            self.used_ids.add(page_id)
            self.in_progress_ids.add(page_id)
            selected.append(page_id)
            possible_fresh -= 1
        if len(selected) < count and not selected:
            raise RuntimeError("No unused Wikipedia page IDs remain within the configured bounds.")
        self._record_event("reserve_ids", selected, "")
        self.save()
        return selected

    def reserve_candidate_ids(
        self,
        candidate_ids: list[int],
        *,
        count: int,
        source: str,
        prefer_rerun_pool: bool = True,
    ) -> list[int]:
        """Reserve IDs from a discovered candidate pool without reusing prior IDs."""
        if count < 1:
            return []
        selected: list[int] = []
        if prefer_rerun_pool:
            selected.extend(self._reserve_from_rerun_pool(count))
        seen_selected = set(selected)
        for page_id in candidate_ids:
            if len(selected) >= count:
                break
            if page_id < 1 or page_id in self.used_ids or page_id in seen_selected:
                continue
            self.used_ids.add(page_id)
            self.in_progress_ids.add(page_id)
            selected.append(page_id)
            seen_selected.add(page_id)
        if selected:
            self._record_event("reserve_candidate_ids", selected, source)
            self.save()
        return selected

    def table_search_offset(self, query: str) -> int:
        """Return the next table-search offset for one query."""
        return max(0, int(self.table_search_offsets.get(query, 0)))

    def advance_table_search_offset(self, query: str, amount: int) -> None:
        """Advance and persist one table-search offset."""
        self.table_search_offsets[query] = self.table_search_offset(query) + max(0, amount)
        self._record_event("advance_table_search_offset", [], f"{query}:{self.table_search_offsets[query]}")
        self.save()

    def record_discovery_error(self, *, source: str, error: str) -> None:
        """Record a non-fatal discovery error."""
        self._record_event("discovery_error", [], f"{source}:{error}")
        self.save()

    def mark_accepted(self, page_id: int) -> None:
        """Mark one page ID as accepted."""
        self.in_progress_ids.discard(page_id)
        self.accepted_ids.add(page_id)
        self.rejected_ids.discard(page_id)
        self.failure_reasons.pop(page_id, None)
        self._remove_from_rerun_pool(page_id)
        self._record_event("accepted", [page_id], "")
        self.save()

    def mark_rejected(self, page_id: int, *, reason: str) -> None:
        """Mark one page ID as rejected."""
        self.in_progress_ids.discard(page_id)
        self.rejected_ids.add(page_id)
        self.accepted_ids.discard(page_id)
        self.failure_reasons[page_id] = reason
        self._remove_from_rerun_pool(page_id)
        self._record_event("rejected", [page_id], reason)
        self.save()

    def mark_rerun(self, page_id: int, *, reason: str) -> None:
        """Return one unresolved page ID to the rerun pool."""
        self.in_progress_ids.discard(page_id)
        if page_id not in self.rerun_pool and page_id not in self.accepted_ids and page_id not in self.rejected_ids:
            self.rerun_pool.append(page_id)
        self.failure_reasons[page_id] = reason
        self._record_event("rerun", [page_id], reason)
        self.save()

    def sync_decided_ids(
        self,
        *,
        accepted_ids: list[int],
        rejected_ids: list[int],
        reason: str = "endpoint_resume",
    ) -> dict[str, int]:
        """Merge accepted/rejected endpoint IDs into the persistent stream state."""
        accepted = _positive_unique_ids(accepted_ids)
        rejected = [page_id for page_id in _positive_unique_ids(rejected_ids) if page_id not in set(accepted)]
        changed = False
        for page_id in accepted:
            before = (
                page_id in self.used_ids,
                page_id in self.accepted_ids,
                page_id in self.rejected_ids,
                page_id in self.in_progress_ids,
                page_id in self.rerun_pool,
            )
            self.used_ids.add(page_id)
            self.accepted_ids.add(page_id)
            self.rejected_ids.discard(page_id)
            self.in_progress_ids.discard(page_id)
            self.failure_reasons.pop(page_id, None)
            self._remove_from_rerun_pool(page_id)
            after = (
                page_id in self.used_ids,
                page_id in self.accepted_ids,
                page_id in self.rejected_ids,
                page_id in self.in_progress_ids,
                page_id in self.rerun_pool,
            )
            changed = changed or before != after
        for page_id in rejected:
            before = (
                page_id in self.used_ids,
                page_id in self.accepted_ids,
                page_id in self.rejected_ids,
                page_id in self.in_progress_ids,
                page_id in self.rerun_pool,
            )
            self.used_ids.add(page_id)
            self.rejected_ids.add(page_id)
            self.accepted_ids.discard(page_id)
            self.in_progress_ids.discard(page_id)
            self.failure_reasons.setdefault(page_id, reason)
            self._remove_from_rerun_pool(page_id)
            after = (
                page_id in self.used_ids,
                page_id in self.accepted_ids,
                page_id in self.rejected_ids,
                page_id in self.in_progress_ids,
                page_id in self.rerun_pool,
            )
            changed = changed or before != after
        if changed:
            self._record_event("sync_decided_ids", [*accepted, *rejected], reason)
            self.save()
        return {
            "accepted_ids_synced": len(accepted),
            "rejected_ids_synced": len(rejected),
        }

    def stats(self) -> dict[str, int]:
        """Return compact stream-state counts."""
        return {
            "used": len(self.used_ids),
            "in_progress": len(self.in_progress_ids),
            "accepted": len(self.accepted_ids),
            "rejected": len(self.rejected_ids),
            "rerun_pool": len(self.rerun_pool),
            "table_search_queries": len(self.table_search_offsets),
        }

    def _reserve_from_rerun_pool(self, count: int) -> list[int]:
        selected: list[int] = []
        remaining: list[int] = []
        seen_selected: set[int] = set()
        for page_id in self.rerun_pool:
            if len(selected) >= count:
                remaining.append(page_id)
                continue
            if page_id in self.accepted_ids or page_id in self.rejected_ids or page_id in seen_selected:
                continue
            selected.append(page_id)
            seen_selected.add(page_id)
            self.in_progress_ids.add(page_id)
            self.used_ids.add(page_id)
        self.rerun_pool = remaining
        return selected

    def _remove_from_rerun_pool(self, page_id: int) -> None:
        self.rerun_pool = [value for value in self.rerun_pool if value != page_id]

    def _record_event(self, event_type: str, page_ids: list[int], reason: str) -> None:
        self.events.append(
            {
                "event": event_type,
                "page_ids": page_ids,
                "reason": reason,
            }
        )


def _validate_bounds(lower_bound: int, upper_bound: int) -> None:
    if lower_bound < 1:
        raise ValueError("stream page-id lower bound must be positive")
    if upper_bound < lower_bound:
        raise ValueError("stream page-id upper bound must be greater than or equal to lower bound")


def _int_set(value: object) -> set[int]:
    return set(_int_list(value))


def _int_list(value: object) -> list[int]:
    if not isinstance(value, list):
        return []
    return [int(item) for item in value if _is_int_like(item)]


def _positive_unique_ids(values: list[int]) -> list[int]:
    seen: set[int] = set()
    result: list[int] = []
    for value in values:
        try:
            page_id = int(value)
        except (TypeError, ValueError):
            continue
        if page_id < 1 or page_id in seen:
            continue
        seen.add(page_id)
        result.append(page_id)
    return result


def _is_int_like(value: object) -> bool:
    try:
        int(value)
    except (TypeError, ValueError):
        return False
    return True
