"""Route 1 QID-first multi-hop join support."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Iterable

from .domain_templates import get_template_by_key
from .models import CandidateFact, DomainTemplate
from .reasoning import normalize_reasoning_style

ROUTE1_MULTIHOP_JOIN_ROUTE = "route1_wikidata_multihop_join"

ROUTE1_MULTIHOP_JOIN_TEMPLATE_KEYS: tuple[str, ...] = (
    "person_first_degree_university",
    "film_source_work_author",
    "tv_series_source_work_author",
    "company_that_released_product_founder",
    "company_that_developed_benchmark_founder",
    "terminal_operator_country",
)


@dataclass(slots=True)
class Route1QidSeedUnit:
    """One QID-first Route 1 multi-hop seed unit."""

    template_key: str
    subject_qid: str
    date_anchor: str = ""
    bridge_qids: tuple[str, ...] = ()
    answer_qids: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def state_key(self) -> str:
        """Return the stable state key for this seed unit."""
        explicit_key = str(self.metadata.get("route1_qid_seed_key", "")).strip()
        if explicit_key:
            return explicit_key
        parts = [
            self.template_key,
            self.subject_qid,
            self.date_anchor or "-",
            ",".join(self.bridge_qids) or "-",
            ",".join(self.answer_qids) or "-",
        ]
        return "|".join(parts)

    def to_metadata(self) -> dict[str, Any]:
        """Serialize this seed unit for candidate metadata."""
        return {
            "template_key": self.template_key,
            "subject_qid": self.subject_qid,
            "date_anchor": self.date_anchor,
            "bridge_qids": list(self.bridge_qids),
            "answer_qids": list(self.answer_qids),
            "state_key": self.state_key,
        }


@dataclass(slots=True)
class Route1QidSeedState:
    """Persistent state for Route 1 QID seed streaming."""

    path: Path
    used_keys: set[str] = field(default_factory=set)
    in_progress_keys: set[str] = field(default_factory=set)
    accepted_keys: set[str] = field(default_factory=set)
    rejected_keys: set[str] = field(default_factory=set)
    rerun_pool: list[str] = field(default_factory=list)
    failure_reasons: dict[str, str] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> "Route1QidSeedState":
        """Load a seed state file, returning an empty state when absent."""
        if not path.exists():
            return cls(path=path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            path=path,
            used_keys=set(_string_list(payload.get("used_keys", []))),
            in_progress_keys=set(_string_list(payload.get("in_progress_keys", []))),
            accepted_keys=set(_string_list(payload.get("accepted_keys", []))),
            rejected_keys=set(_string_list(payload.get("rejected_keys", []))),
            rerun_pool=_string_list(payload.get("rerun_pool", [])),
            failure_reasons={
                str(key): str(value)
                for key, value in dict(payload.get("failure_reasons", {})).items()
                if str(key).strip()
            },
            events=[event for event in payload.get("events", []) if isinstance(event, dict)],
        )

    def save(self) -> None:
        """Persist state to disk."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "used_keys": sorted(self.used_keys),
            "in_progress_keys": sorted(self.in_progress_keys),
            "accepted_keys": sorted(self.accepted_keys),
            "rejected_keys": sorted(self.rejected_keys),
            "rerun_pool": self.rerun_pool.copy(),
            "failure_reasons": dict(sorted(self.failure_reasons.items())),
            "events": self.events[-200:],
            "stats": self.stats(),
        }
        self.path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def recover_stale_in_progress(
        self,
        *,
        reason: str = "recovered_in_progress_from_previous_run",
    ) -> list[str]:
        """Move unresolved in-progress seed keys back into the rerun pool."""
        stale_keys = sorted(self.in_progress_keys - self.accepted_keys - self.rejected_keys)
        if not stale_keys:
            return []
        rerun_seen = set(self.rerun_pool)
        for key in stale_keys:
            if key not in rerun_seen:
                self.rerun_pool.append(key)
                rerun_seen.add(key)
            self.failure_reasons[key] = reason
        self.in_progress_keys.difference_update(stale_keys)
        self._record_event("recover_stale_in_progress", stale_keys, reason)
        self.save()
        return stale_keys

    def reserve_seed_units(
        self,
        seed_units: Iterable[Route1QidSeedUnit],
        *,
        count: int,
        prefer_rerun_pool: bool = True,
    ) -> list[Route1QidSeedUnit]:
        """Reserve seed units, preferring unresolved reruns when requested."""
        if count < 1:
            return []
        unit_by_key = {unit.state_key: unit for unit in seed_units}
        selected: list[Route1QidSeedUnit] = []
        if prefer_rerun_pool:
            selected.extend(self._reserve_from_rerun_pool(unit_by_key, count))
        selected_keys = {unit.state_key for unit in selected}
        for key, unit in unit_by_key.items():
            if len(selected) >= count:
                break
            if key in self.used_keys or key in selected_keys:
                continue
            self.used_keys.add(key)
            self.in_progress_keys.add(key)
            selected.append(unit)
            selected_keys.add(key)
        if selected:
            self._record_event("reserve_seed_units", [unit.state_key for unit in selected], "")
            self.save()
        return selected

    def mark_accepted(self, key: str) -> None:
        """Mark one seed key as accepted."""
        self.in_progress_keys.discard(key)
        self.accepted_keys.add(key)
        self.rejected_keys.discard(key)
        self.failure_reasons.pop(key, None)
        self._remove_from_rerun_pool(key)
        self._record_event("accepted", [key], "")
        self.save()

    def mark_rejected(self, key: str, *, reason: str) -> None:
        """Mark one seed key as rejected."""
        self.in_progress_keys.discard(key)
        self.rejected_keys.add(key)
        self.accepted_keys.discard(key)
        self.failure_reasons[key] = reason
        self._remove_from_rerun_pool(key)
        self._record_event("rejected", [key], reason)
        self.save()

    def mark_rerun(self, key: str, *, reason: str) -> None:
        """Return one unresolved seed key to the rerun pool."""
        self.in_progress_keys.discard(key)
        if key not in self.rerun_pool and key not in self.accepted_keys and key not in self.rejected_keys:
            self.rerun_pool.append(key)
        self.failure_reasons[key] = reason
        self._record_event("rerun", [key], reason)
        self.save()

    def sync_decided_keys(
        self,
        *,
        accepted_keys: list[str],
        rejected_keys: list[str],
        reason: str = "endpoint_resume",
    ) -> dict[str, int]:
        """Merge accepted/rejected endpoint keys into the persistent state."""
        accepted = _unique_strings(accepted_keys)
        rejected = [key for key in _unique_strings(rejected_keys) if key not in set(accepted)]
        changed = False
        for key in accepted:
            before = self._key_membership(key)
            self.used_keys.add(key)
            self.accepted_keys.add(key)
            self.rejected_keys.discard(key)
            self.in_progress_keys.discard(key)
            self.failure_reasons.pop(key, None)
            self._remove_from_rerun_pool(key)
            changed = changed or before != self._key_membership(key)
        for key in rejected:
            before = self._key_membership(key)
            self.used_keys.add(key)
            self.rejected_keys.add(key)
            self.accepted_keys.discard(key)
            self.in_progress_keys.discard(key)
            self.failure_reasons.setdefault(key, reason)
            self._remove_from_rerun_pool(key)
            changed = changed or before != self._key_membership(key)
        if changed:
            self._record_event("sync_decided_keys", [*accepted, *rejected], reason)
            self.save()
        return {
            "accepted_keys_synced": len(accepted),
            "rejected_keys_synced": len(rejected),
        }

    def stats(self) -> dict[str, int]:
        """Return compact seed-state counts."""
        return {
            "used": len(self.used_keys),
            "in_progress": len(self.in_progress_keys),
            "accepted": len(self.accepted_keys),
            "rejected": len(self.rejected_keys),
            "rerun_pool": len(self.rerun_pool),
        }

    def _reserve_from_rerun_pool(
        self,
        unit_by_key: dict[str, Route1QidSeedUnit],
        count: int,
    ) -> list[Route1QidSeedUnit]:
        selected: list[Route1QidSeedUnit] = []
        remaining: list[str] = []
        seen_selected: set[str] = set()
        for key in self.rerun_pool:
            if len(selected) >= count:
                remaining.append(key)
                continue
            unit = unit_by_key.get(key)
            if unit is None:
                remaining.append(key)
                continue
            if key in self.accepted_keys or key in self.rejected_keys or key in seen_selected:
                continue
            self.used_keys.add(key)
            self.in_progress_keys.add(key)
            selected.append(unit)
            seen_selected.add(key)
        self.rerun_pool = remaining
        return selected

    def _remove_from_rerun_pool(self, key: str) -> None:
        self.rerun_pool = [value for value in self.rerun_pool if value != key]

    def _key_membership(self, key: str) -> tuple[bool, bool, bool, bool, bool]:
        return (
            key in self.used_keys,
            key in self.accepted_keys,
            key in self.rejected_keys,
            key in self.in_progress_keys,
            key in self.rerun_pool,
        )

    def _record_event(self, event_type: str, keys: list[str], reason: str) -> None:
        self.events.append(
            {
                "event": event_type,
                "seed_keys": keys,
                "reason": reason,
            }
        )


def get_route1_multihop_join_templates(
    template_keys: Iterable[str] | None = None,
) -> list[DomainTemplate]:
    """Return default Route 1 multi-hop join templates."""
    keys = list(template_keys or ROUTE1_MULTIHOP_JOIN_TEMPLATE_KEYS)
    templates: list[DomainTemplate] = []
    for key in keys:
        template = get_template_by_key(key)
        if template is None:
            continue
        if normalize_reasoning_style(template.reasoning_style or template.composition_style) != "multi_hop_join":
            continue
        if template.answer_format == "number" or template.answer_type == "Number":
            continue
        templates.append(template)
    return templates


def seed_unit_from_candidate(candidate: CandidateFact, template: DomainTemplate | None = None) -> Route1QidSeedUnit:
    """Build a stable QID seed unit from one constructed Route 1 candidate."""
    template_key = template.template_key if template is not None else candidate.domain
    bridge_qids = tuple(
        sorted(
            {
                str(bridge.get("qid", "")).strip()
                for bridge in candidate.bridge_entities
                if str(bridge.get("qid", "")).strip()
            }
        )
    )
    answer_qids = tuple(sorted(qid for qid in candidate.answer_qids if qid and not qid.startswith("VALUE:")))
    unit = Route1QidSeedUnit(
        template_key=template_key,
        subject_qid=candidate.subject_qid,
        date_anchor=candidate.date_value,
        bridge_qids=bridge_qids,
        answer_qids=answer_qids,
    )
    unit.metadata["route1_qid_seed_key"] = unit.state_key
    return unit


def attach_seed_metadata(candidate: CandidateFact, template: DomainTemplate | None = None) -> Route1QidSeedUnit:
    """Attach QID seed metadata to one candidate and return the seed unit."""
    unit = seed_unit_from_candidate(candidate, template)
    candidate.source_metadata["route1_qid_seed_key"] = unit.state_key
    candidate.source_metadata["route1_qid_seed_unit"] = unit.to_metadata()
    return unit


def seed_key_from_record(record: dict[str, Any]) -> str:
    """Return a Route 1 QID seed key from an accepted/rejected JSONL record."""
    metadata = record.get("source_metadata", {})
    if isinstance(metadata, dict):
        key = str(metadata.get("route1_qid_seed_key", "")).strip()
        if key:
            return key
    template_key = str(record.get("template_key") or record.get("legacy_domain") or record.get("domain") or "").strip()
    subject_qid = str(record.get("subject_qid") or "").strip()
    date_filter = record.get("date_filter", {})
    date_anchor = ""
    if isinstance(date_filter, dict):
        date_anchor = str(date_filter.get("value") or "").strip()
    if template_key and subject_qid:
        return "|".join([template_key, subject_qid, date_anchor or "-", "-", "-"])
    return ""


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _unique_strings(values: Iterable[str]) -> list[str]:
    unique: list[str] = []
    seen: set[str] = set()
    for raw_value in values:
        value = str(raw_value).strip()
        if not value or value in seen:
            continue
        seen.add(value)
        unique.append(value)
    return unique
