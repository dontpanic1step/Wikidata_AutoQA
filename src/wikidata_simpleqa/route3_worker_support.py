"""Stable support API shared by the Route 3 worker and recipe."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass, field
import hashlib
import json
from json import JSONDecodeError
from pathlib import Path
import re

from .wikipedia_client import normalize_wikipedia_page_id
from .wikipedia_infobox_generator import (
    normalize_route3_answer_types,
    normalize_route3_table_source_types,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STREAM_RANDOM_SEED = 42
PAGE_LEVEL_TIMING_PHASES = {
    "page_fetch_seconds",
    "table_parse_seconds",
    "first_paragraph_extract_seconds",
    "first_paragraph_fetch_seconds",
    "total_generation_seconds",
}
LLM_PROMPT_TIMING_PHASES = {"llm_question_generation_seconds"}
STREAM_REUSE_ALL_VALUES = {"all", "exhaust", "exhaustive"}
STREAM_FRESH_FILL_VALUES = {"fill", "until-target", "until_target", "all"}


@dataclass(slots=True)
class EndpointResumeState:
    """Accepted/rejected endpoint files used as a resume checkpoint."""

    enabled: bool = False
    accepted_records: list[dict] = field(default_factory=list)
    rejected_records: list[dict] = field(default_factory=list)
    skipped_lines: list[dict[str, object]] = field(default_factory=list)

    @property
    def accepted_count(self) -> int:
        return len(self.accepted_records)

    @property
    def rejected_count(self) -> int:
        return len(self.rejected_records)

    @property
    def final_decision_count(self) -> int:
        return self.accepted_count + self.rejected_count

    def summary(self) -> dict[str, object]:
        return {
            "enabled": self.enabled,
            "accepted_records_loaded": self.accepted_count,
            "rejected_records_loaded": self.rejected_count,
            "final_decisions_loaded": self.final_decision_count,
            "skipped_malformed_lines": len(self.skipped_lines),
            "skipped_line_details": self.skipped_lines[:20],
        }


def safe_artifact_id(value: str, *, fallback: str = "") -> str:
    """Return a path-safe artifact identifier."""
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip()).strip("._-")
    if cleaned:
        return cleaned
    return fallback


def run_group_id(args: argparse.Namespace) -> str:
    """Return the normalized run group ID for artifact indexing."""
    return safe_artifact_id(str(getattr(args, "run_group_id", "") or ""))


def run_segment_id(args: argparse.Namespace) -> str:
    """Return the normalized run segment ID for artifact indexing."""
    raw_value = str(getattr(args, "run_segment_id", "") or "").strip()
    if not raw_value:
        raw_value = Path(getattr(args, "summary_output")).stem
    return safe_artifact_id(raw_value, fallback="segment")


def _stable_stream_seed(*parts: object, default: int = DEFAULT_STREAM_RANDOM_SEED) -> int:
    """Return a deterministic non-zero 31-bit seed from stable run identity parts."""
    text = "|".join(str(part) for part in parts if str(part or "").strip())
    if not text:
        return default
    digest = hashlib.blake2s(text.encode("utf-8"), digest_size=8).hexdigest()
    seed = int(digest, 16) & 0x7FFFFFFF
    return seed or default


def effective_stream_random_seed(args: argparse.Namespace, endpoint_resume: EndpointResumeState | None = None) -> int:
    """Return the configured seed, or derive a run-specific default seed."""
    configured_seed = getattr(args, "stream_random_seed", None)
    if configured_seed is not None:
        return int(configured_seed)
    resume_count = endpoint_resume.final_decision_count if endpoint_resume is not None else 0
    return _stable_stream_seed(
        "wikipedia_stream",
        run_group_id(args),
        run_segment_id(args),
        getattr(args, "summary_output", ""),
        getattr(args, "stream_state", ""),
        "endpoint_resume" if getattr(args, "start_from_endpoint", False) else "",
        resume_count if getattr(args, "start_from_endpoint", False) else "",
    )


def load_endpoint_jsonl(path: Path, *, label: str) -> tuple[list[dict], list[dict[str, object]]]:
    """Load a JSONL endpoint, tolerating a malformed trailing line from a crash."""
    if not path.exists():
        return [], []
    records: list[dict] = []
    skipped: list[dict[str, object]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except JSONDecodeError as exc:
            skipped.append(
                {
                    "path": str(path),
                    "endpoint": label,
                    "line_number": line_number,
                    "error": str(exc),
                }
            )
            continue
        if isinstance(value, dict):
            records.append(value)
        else:
            skipped.append(
                {
                    "path": str(path),
                    "endpoint": label,
                    "line_number": line_number,
                    "error": "non_object_jsonl_record",
                }
            )
    return records, skipped


def normalize_stream_reuse_cached_page_count(value: object) -> int | str:
    """Return a non-negative cached-reuse count or the automatic all-cached sentinel."""
    return _normalize_stream_budget_value(
        value,
        flag="--stream-reuse-cached-page-count",
        auto_values=STREAM_REUSE_ALL_VALUES,
        canonical_auto="all",
    )


def normalize_stream_fresh_cached_page_count(value: object) -> int | str:
    """Return a non-negative fresh-page count or the automatic fill-to-target sentinel."""
    return _normalize_stream_budget_value(
        value,
        flag="--stream-fresh-cached-page-count",
        auto_values=STREAM_FRESH_FILL_VALUES,
        canonical_auto="fill",
    )


def _normalize_stream_budget_value(
    value: object,
    *,
    flag: str,
    auto_values: set[str],
    canonical_auto: str,
) -> int | str:
    text = str(value if value is not None else "").strip().lower()
    if not text:
        raise ValueError(f"{flag} must be a non-negative integer or {canonical_auto!r}.")
    if text in auto_values:
        return canonical_auto
    try:
        count = int(text)
    except ValueError as exc:
        raise ValueError(f"{flag} must be a non-negative integer or {canonical_auto!r}.") from exc
    if count < 0:
        raise ValueError(f"{flag} must be non-negative.")
    return count


def stream_budget_numeric_count(value: int | str) -> int:
    """Return the hard numeric part of a stream budget; automatic sentinels contribute no standalone target."""
    return value if isinstance(value, int) else 0


def ensure_page_id_list_entry_metadata(record: dict) -> None:
    """Attach an explicit triadic page-ID entry when record metadata supports it."""
    if not isinstance(record, dict):
        return
    metadata = record.setdefault("source_metadata", {})
    if not isinstance(metadata, dict):
        return
    page_id = record_page_id(record)
    answer_type = record_answer_type(record)
    table_type = record_table_type(record)
    if not page_id or not answer_type or answer_type == "unknown" or not table_type:
        return
    metadata["page_id"] = page_id
    metadata["page_id_list_entry"] = {
        "page_id": page_id,
        "answer_type": answer_type,
        "table_type": table_type,
    }


def record_table_type(record: dict) -> str:
    """Return the actual Route 3 table type represented by one output record."""
    metadata = record.get("source_metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
    selected = metadata.get("selected_source_table")
    if isinstance(selected, dict):
        table_type = _normalize_record_table_type(selected.get("table_type"))
        if table_type:
            return table_type
    for source in (record, metadata):
        if not isinstance(source, dict):
            continue
        for key in ("table_type", "source_channel", "recipe_table_type"):
            table_type = _normalize_record_table_type(source.get(key))
            if table_type:
                return table_type
    source_types = metadata.get("table_source_types")
    if isinstance(source_types, list) and len(source_types) == 1:
        return _normalize_record_table_type(source_types[0])
    return ""


def _normalize_record_table_type(value: object) -> str:
    """Normalize one record table-type value for page-ID entries."""
    text = str(value or "").strip()
    if not text:
        return ""
    try:
        normalized = normalize_route3_table_source_types([text])
    except ValueError:
        return ""
    return normalized[0] if len(normalized) == 1 else ""


def survival_by_layer(
    *,
    attempted_count: int,
    accepted_records: list[dict] | None = None,
    rejected_records: list[dict],
    rerun_records: list[dict],
) -> list[dict[str, object]]:
    """Return layer-by-layer survival stats for a streaming run."""
    accepted_records = accepted_records or []
    all_records = [*accepted_records, *rejected_records]
    llm_input_stats = _llm_generation_input_stats(all_records, rerun_records=rerun_records)
    llm_input_pages = int(llm_input_stats["input_pages"])
    llm_input_tables = int(llm_input_stats["input_tables"])
    stage_failures = Counter(_rejection_stage(record) for record in rejected_records)
    for record in rerun_records:
        stage_failures[_rerun_stage(record)] += 1
    rows: list[dict[str, object]] = []

    page_entered = max(0, int(attempted_count))
    _append_survival_row(
        rows,
        stage="page_id_reservation",
        layer="Page-id reservation",
        unit="page IDs",
        entered=page_entered,
        failed=0,
        cumulative_denominator=page_entered,
    )
    unresolved_failed = int(stage_failures.get("unresolved_rerun", 0))
    page_after_unresolved = max(0, page_entered - unresolved_failed)
    _append_survival_row(
        rows,
        stage="unresolved_rerun",
        layer="Unresolved or returned to rerun pool",
        unit="page IDs",
        entered=page_entered,
        failed=unresolved_failed,
        cumulative_denominator=page_entered,
    )
    pre_llm_failed = max(0, page_after_unresolved - llm_input_pages)
    _append_survival_row(
        rows,
        stage="route_generation_pre_llm",
        layer="Source and table filters before generation LLM",
        unit="page IDs",
        entered=page_after_unresolved,
        failed=pre_llm_failed,
        survived=llm_input_pages,
        cumulative_denominator=page_entered,
    )
    _append_survival_row(
        rows,
        stage="llm_generation_input_tables",
        layer="Tables sent to generation LLM",
        unit="tables",
        entered=llm_input_tables,
        failed=0,
        cumulative_denominator=llm_input_tables,
    )

    accepted_count = len(accepted_records)
    route_generation_post_llm_failed = _post_llm_route_generation_failure_count(rejected_records)
    downstream_stage_order = [
        "rewrite_surface",
        "shared_validation",
        "search_longtail",
        "second_stage_grading",
        "deduplication",
        "other",
    ]
    downstream_failures = {
        stage: int(stage_failures.get(stage, 0))
        for stage in downstream_stage_order
    }
    candidate_rows_denominator = (
        accepted_count
        + route_generation_post_llm_failed
        + sum(downstream_failures.values())
    )
    _append_survival_row(
        rows,
        stage="route_generation",
        layer="Generation LLM output and route-local checks",
        unit="QA candidates/slots",
        entered=candidate_rows_denominator,
        failed=route_generation_post_llm_failed,
        cumulative_denominator=candidate_rows_denominator,
    )
    for index, stage in enumerate(downstream_stage_order):
        entered = accepted_count + sum(
            downstream_failures[downstream_stage]
            for downstream_stage in downstream_stage_order[index:]
        )
        _append_survival_row(
            rows,
            stage=stage,
            layer=_survival_stage_label(stage),
            unit="QA candidates/slots",
            entered=entered,
            failed=downstream_failures[stage],
            cumulative_denominator=candidate_rows_denominator,
        )
    return rows


def _append_survival_row(
    rows: list[dict[str, object]],
    *,
    stage: str,
    layer: str,
    unit: str,
    entered: int,
    failed: int,
    cumulative_denominator: int,
    survived: int | None = None,
) -> None:
    """Append one normalized survival row."""
    entered = max(0, int(entered))
    failed = max(0, int(failed))
    survived = max(0, entered - failed) if survived is None else max(0, int(survived))
    rows.append(
        {
            "stage": stage,
            "layer": layer,
            "unit": unit,
            "entered": entered,
            "failed": failed,
            "survived": survived,
            "survival_rate_from_layer_input": _rate(survived, entered),
            "cumulative_survival_rate": _rate(survived, cumulative_denominator),
        }
    )


def _survival_stage_label(stage: str) -> str:
    """Return the human-facing label for a post-generation survival stage."""
    return {
        "rewrite_surface": "Rewrite and surface validation",
        "shared_validation": "Shared deterministic route-aware validation",
        "search_longtail": "DuckDuckGo long-tail filtering",
        "second_stage_grading": "Second-stage model grading",
        "deduplication": "Deduplication",
        "other": "Other rejection",
    }.get(stage, stage)


def _post_llm_route_generation_failure_count(rejected_records: list[dict]) -> int:
    """Return route-local generation failures that happened after the generation LLM ran."""
    return sum(
        1
        for record in rejected_records
        if _rejection_stage(record) == "route_generation" and _record_entered_llm_generation(record)
    )


def llm_generation_table_yield_summary(
    accepted_records: list[dict],
    rejected_records: list[dict],
    *,
    rerun_records: list[dict] | None = None,
) -> dict[str, object]:
    """Return accepted-QA yield over tables that reached the Route 3 generation LLM."""
    input_stats = _llm_generation_input_stats(
        [*accepted_records, *rejected_records],
        rerun_records=rerun_records or [],
    )
    input_tables = int(input_stats["input_tables"])
    accepted_qas = len(accepted_records)
    return {
        "llm_generation_input_tables": input_tables,
        "llm_generation_input_pages": int(input_stats["input_pages"]),
        "llm_generation_accepted_qas": accepted_qas,
        "llm_generation_table_yield": _rate(accepted_qas, input_tables) if input_tables else None,
    }


def _walkthrough_llm_generation_table_yield(
    summary: dict,
    accepted_records: list[dict],
    rejected_records: list[dict],
    rerun_records: list[dict],
) -> dict[str, object]:
    """Return LLM table-yield fields for display, computing them for older summaries if needed."""
    if "llm_generation_input_tables" in summary:
        return {
            "input_tables": int(summary.get("llm_generation_input_tables", 0) or 0),
            "accepted_qas": int(summary.get("llm_generation_accepted_qas", summary.get("accepted", 0)) or 0),
            "yield": _optional_float(summary.get("llm_generation_table_yield")),
        }
    computed = llm_generation_table_yield_summary(
        accepted_records,
        rejected_records,
        rerun_records=rerun_records,
    )
    return {
        "input_tables": int(computed["llm_generation_input_tables"]),
        "accepted_qas": int(computed["llm_generation_accepted_qas"]),
        "yield": _optional_float(computed["llm_generation_table_yield"]),
    }


def _llm_generation_input_stats(
    records: list[dict],
    *,
    rerun_records: list[dict] | None = None,
) -> dict[str, int]:
    """Return unique page and table counts that entered the generation LLM."""
    page_keys: set[tuple[object, ...]] = set()
    table_keys: set[tuple[object, ...]] = set()
    for record_index, record in enumerate(records):
        if not _record_entered_llm_generation(record):
            continue
        page_key = _record_page_key(record, record_index=record_index)
        page_keys.add(page_key)
        table_keys.update(_record_llm_input_table_keys(record, record_index=record_index))
    for record_index, record in enumerate(rerun_records or []):
        if not _rerun_entered_llm_generation(record):
            continue
        page_key = _record_page_key(record, record_index=record_index)
        page_keys.add(page_key)
        table_keys.add((*page_key, "llm_table", "rerun_unknown"))
    return {"input_pages": len(page_keys), "input_tables": len(table_keys)}


def _rerun_entered_llm_generation(record: dict) -> bool:
    """Return whether one transient rerun happened after generation LLM input."""
    return _rerun_stage(record) in {"search_longtail", "second_stage_grading"}


def _record_entered_llm_generation(record: dict) -> bool:
    """Return whether one final record came from a page/table sent to the generation LLM."""
    timings = record.get("source_metadata", {}).get("phase_timings_seconds", {})
    return isinstance(timings, dict) and "llm_question_generation_seconds" in timings


def _record_llm_input_table_keys(record: dict, *, record_index: int = 0) -> list[tuple[object, ...]]:
    """Return stable keys for tables passed to the generation LLM for one record."""
    metadata = record.get("source_metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
    page_key = _record_page_key(record, record_index=record_index)
    table_selection = metadata.get("table_selection", [])
    table_limit = 1
    keys: list[tuple[object, ...]] = []
    if isinstance(table_selection, list):
        for row in table_selection:
            if not isinstance(row, dict) or not _table_selection_row_enters_llm(row):
                continue
            key = _record_table_key(page_key, row)
            if key not in keys:
                keys.append(key)
            if len(keys) >= table_limit:
                break
    selected = metadata.get("selected_source_table")
    if not keys and isinstance(selected, dict) and selected:
        keys.append(_record_table_key(page_key, selected))
    if not keys:
        keys.append((*page_key, "llm_table", "unknown"))
    return keys


def _table_selection_row_enters_llm(row: dict) -> bool:
    """Return whether one table-selection row survived into the generation prompt."""
    return (
        not str(row.get("live_scope_rejection_reason", "")).strip()
        and not bool(row.get("below_min_table_score", False))
        and not str(row.get("table_filter_rejection_reason", "")).strip()
    )


def _record_table_key(page_key: tuple[object, ...], table: dict) -> tuple[object, ...]:
    """Return a stable key for one table on one page."""
    return (
        *page_key,
        "table",
        str(table.get("table_type", "") or ""),
        str(table.get("table_index", "") or ""),
        str(table.get("caption", "") or ""),
        str(table.get("section_heading", "") or ""),
    )


def _record_page_key(record: dict, *, record_index: int = 0) -> tuple[object, ...]:
    """Return a stable page-attempt key for deduplicating page-level timings."""
    page_id = record_page_id(record)
    if page_id not in {"", None}:
        return ("page_id", page_id)
    metadata = record.get("source_metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
    for key in ("canonical_url", "source_url", "stream_source_url"):
        value = str(metadata.get(key) or "").strip()
        if value:
            return ("url", value)
    question = str(record.get("question", "") or "").strip()
    return ("record", record_index, question)


def failure_reason_counts(rejected_records: list[dict], rerun_records: list[dict]) -> list[dict[str, object]]:
    """Return reviewer-facing failure reasons grouped by stage."""
    counts: Counter[tuple[str, str]] = Counter()
    for record in rejected_records:
        counts[(_rejection_stage(record), _summary_failure_reason(record))] += 1
    for record in rerun_records:
        counts[(_rerun_stage(record), str(record.get("reason", "unresolved")))] += 1
    return [
        {"stage": stage, "reason": reason, "count": count}
        for (stage, reason), count in sorted(counts.items(), key=lambda item: (-item[1], item[0][0], item[0][1]))
    ]


def _rerun_stage(record: dict) -> str:
    """Return the pipeline stage where a retryable stream failure occurred."""
    reason = str(record.get("reason", "")).strip()
    if reason.startswith("search_longtail_verifier_error"):
        return "search_longtail"
    if reason.startswith("second_stage_grading_error"):
        return "second_stage_grading"
    if reason.startswith("wikipedia_infobox_") or reason.startswith("pipeline_exception"):
        return "route_generation"
    return "unresolved_rerun"


def _phase_timing_explanation_rows() -> list[dict[str, str]]:
    """Return the ordered timing glossary used by walkthroughs."""
    return [
        {
            "order": "0",
            "phase": "wall_clock_seconds",
            "kind": "run total",
            "additive": "No",
            "meaning": "Elapsed time for the whole streaming command.",
        },
        {
            "order": "1",
            "phase": "page_fetch_seconds",
            "kind": "child of total_generation_seconds",
            "additive": "Yes, within generation only",
            "meaning": "MediaWiki action=parse fetch for one page, or zero when a cached archive supplies the parse payload.",
        },
        {
            "order": "2",
            "phase": "table_parse_seconds",
            "kind": "child of total_generation_seconds",
            "additive": "Yes, within generation only",
            "meaning": "Local table/prose parsing and table-ranking inputs for one page.",
        },
        {
            "order": "4",
            "phase": "first_paragraph_extract_seconds",
            "kind": "child of total_generation_seconds",
            "additive": "Yes, within generation only",
            "meaning": "Local extraction of first paragraph from parse HTML after a table survives source filters.",
        },
        {
            "order": "5",
            "phase": "first_paragraph_fetch_seconds",
            "kind": "optional child of total_generation_seconds",
            "additive": "Yes, within generation only",
            "meaning": "REST summary fallback when explicitly enabled and parse HTML lacks a paragraph.",
        },
        {
            "order": "6",
            "phase": "llm_question_generation_seconds",
            "kind": "child of total_generation_seconds",
            "additive": "Yes, within generation only",
            "meaning": "Route 3 table-grounded QA generation LLM call.",
        },
        {
            "order": "7",
            "phase": "total_generation_seconds",
            "kind": "parent",
            "additive": "No",
            "meaning": "Overall Route 3 generation time for one page.",
        },
        {
            "order": "8",
            "phase": "rewrite_seconds",
            "kind": "child of total_processing_seconds",
            "additive": "Yes, within processing only",
            "meaning": "Shared rewrite call when enabled.",
        },
        {
            "order": "9",
            "phase": "number_reference_margin_seconds",
            "kind": "child of total_processing_seconds",
            "additive": "Yes, within processing only",
            "meaning": "Numeric reference margin setup after rewrite/surface checks and before shared validation.",
        },
        {
            "order": "10",
            "phase": "duckduckgo_search_seconds",
            "kind": "child of total_processing_seconds",
            "additive": "Yes, within processing only",
            "meaning": "DuckDuckGo long-tail queries and leakage scoring after shared deterministic validation.",
        },
        {
            "order": "11",
            "phase": "second_stage_grading_seconds",
            "kind": "optional child of total_processing_seconds",
            "additive": "Yes, within processing only",
            "meaning": "Model-panel answerability grading when enabled.",
        },
        {
            "order": "12",
            "phase": "total_processing_seconds",
            "kind": "parent",
            "additive": "No",
            "meaning": "Shared rewrite, surface checks, validation, search, grading, and dedup processing for one candidate.",
        },
        {
            "order": "13",
            "phase": "candidate_processing_seconds",
            "kind": "alias",
            "additive": "No",
            "meaning": "Alias of total_processing_seconds for compatibility.",
        },
    ]


def phase_timing_stats(records: list[dict]) -> dict[str, dict[str, float | int]]:
    """Return total, average, and max timings by phase."""
    values_by_phase: dict[str, list[float]] = defaultdict(list)
    seen_phase_keys: set[tuple[object, ...]] = set()
    for record_index, record in enumerate(records):
        timings = record.get("source_metadata", {}).get("phase_timings_seconds", {})
        if not isinstance(timings, dict):
            continue
        for phase, seconds in timings.items():
            phase_name = str(phase)
            dedupe_key = _phase_timing_dedupe_key(record, phase_name, record_index=record_index)
            if dedupe_key in seen_phase_keys:
                continue
            seen_phase_keys.add(dedupe_key)
            try:
                values_by_phase[phase_name].append(float(seconds))
            except (TypeError, ValueError):
                continue
    return {
        phase: {
            "count": len(values),
            "total": round(sum(values), 4),
            "average": round(sum(values) / len(values), 4),
            "max": round(max(values), 4),
        }
        for phase, values in sorted(values_by_phase.items())
        if values
    }


def _phase_timing_dedupe_key(record: dict, phase: str, *, record_index: int) -> tuple[object, ...]:
    """Return the dedupe scope for one recorded timing value."""
    if phase in PAGE_LEVEL_TIMING_PHASES:
        return ("page", phase, *_record_page_key(record, record_index=record_index))
    if phase in LLM_PROMPT_TIMING_PHASES:
        return (
            "llm_prompt",
            phase,
            *tuple(_record_llm_input_table_keys(record, record_index=record_index)),
        )
    return ("record", phase, record_index)


def _rejection_stage(record: dict) -> str:
    """Map one rejected output record to the pipeline stage that rejected it."""
    reason = str(record.get("rejection_reason", "")).strip()
    source_failure = _source_stage_failure(record)
    if source_failure is not None:
        return source_failure[0]
    if reason.startswith("wikipedia_infobox_"):
        return "route_generation"
    if reason in {"llm_rewrite_discarded", "rewrite_guard_rejected", "rule_based_answer_type_gate_rejected"}:
        return "rewrite_surface"
    if reason.startswith("search_longtail_"):
        return "search_longtail"
    if reason.startswith("second_stage_grading"):
        return "second_stage_grading"
    if reason == "shared_validation_failed":
        return "shared_validation"
    if reason.startswith("duplicate_"):
        return "deduplication"
    return "other"


def exact_failure_reason(record: dict) -> str:
    """Return a precise, reviewer-facing failure reason for one rejected record."""
    reason = str(record.get("rejection_reason", "")).strip() or "unknown_rejection"
    source_failure = _source_stage_failure(record)
    if source_failure is not None:
        _, source_reason, detail = source_failure
        return f"{source_reason}:{detail}" if detail else source_reason
    compact_reason = str(record.get("failing_reason", "")).strip()
    if compact_reason:
        return compact_reason
    notes = record.get("rejection_notes", {})
    if not isinstance(notes, dict):
        return reason
    if reason == "rewrite_guard_rejected":
        rule = record.get("rejection_rule") or notes.get("failure_reason") or notes.get("surface_validation_failure_reason")
        return f"{reason}:{rule}" if rule else reason
    if reason == "rule_based_answer_type_gate_rejected":
        gate = notes.get("rule_based_qa_gate", {})
        if isinstance(gate, dict):
            details = gate.get("details", {})
            if isinstance(details, dict) and details.get("rule"):
                return f"{reason}:{details['rule']}"
        rule = record.get("rejection_rule") or notes.get("failure_reason")
        return f"{reason}:{rule}" if rule else reason
    if reason == "search_longtail_verifier_rejected":
        features = notes.get("search_verification_features", {})
        if isinstance(features, dict) and features.get("triggered_rule"):
            return f"{reason}:{features['triggered_rule']}"
    if reason.startswith("second_stage_grading"):
        features = notes.get("panel_grading_features", {})
        if isinstance(features, dict):
            accuracy = features.get("accuracy")
            threshold = features.get("accuracy_threshold")
            if accuracy is not None and threshold is not None:
                return f"{reason}:accuracy={accuracy};threshold={threshold}"
    if reason == "shared_validation_failed":
        validation = notes.get("validation", {})
        if isinstance(validation, dict):
            failed_keys = [key for key, value in validation.items() if value is False]
            if failed_keys:
                return f"{reason}:{','.join(failed_keys)}"
    metadata = record.get("source_metadata", {})
    if isinstance(metadata, dict):
        discard_reason = str(metadata.get("discard_reason") or "").strip()
        error_message = str(metadata.get("error_message") or "").strip()
        if discard_reason:
            return f"{reason}:{discard_reason}"
        if error_message:
            return f"{reason}:{error_message[:160]}"
    return reason


def _source_stage_failure(record: dict) -> tuple[str, str, str] | None:
    """Return a source-stage failure that should take precedence over placeholder QA validation."""
    source_reason = source_stage_rejection_reason(record)
    if not source_reason:
        return None
    detail = _source_metadata_failure_detail(record)
    return "route_generation", source_reason, detail


def source_stage_rejection_reason(record: dict) -> str:
    """Return the source-stage rejection reason represented by one record, if any."""
    reason = str(record.get("rejection_reason", "")).strip()
    if _is_source_stage_rejection_reason(reason):
        return reason
    notes = record.get("notes", [])
    if isinstance(notes, list):
        for note in notes:
            note_text = str(note or "").strip()
            if _is_source_stage_rejection_reason(note_text):
                return note_text
    return ""


def _is_source_stage_rejection_reason(reason: str) -> bool:
    """Return whether one reason represents a blocking Route 3 source-stage rejection."""
    if not reason:
        return False
    return reason.startswith("wikipedia_infobox_")


def _source_metadata_failure_detail(record: dict) -> str:
    """Return the source metadata detail for a rejected record, if present."""
    metadata = record.get("source_metadata", {})
    if not isinstance(metadata, dict):
        return ""
    return str(metadata.get("discard_reason") or metadata.get("error_message") or "").strip()


def _summary_failure_reason(record: dict) -> str:
    """Return the coarser failure reason used in aggregate stats tables."""
    exact_reason = exact_failure_reason(record)
    reason = str(record.get("rejection_reason", "")).strip() or "unknown_rejection"
    if reason == "search_longtail_verifier_rejected":
        return reason
    if reason == "second_stage_grading_accuracy_threshold_exceeded":
        return reason
    if reason == "wikipedia_infobox_table_filter_rejected":
        table_filter_reason = exact_reason.partition(":")[2]
        if "no_picture_heavy_tables" in table_filter_reason:
            return f"{reason}:no_picture_heavy_tables"
        if "no_incomplete_tables" in table_filter_reason:
            return f"{reason}:no_incomplete_tables"
        if "no_social_science_research" in table_filter_reason:
            return f"{reason}:no_social_science_research"
        if "not_number_dominant" in table_filter_reason or "no_big_numbers" in table_filter_reason:
            return f"{reason}:not_number_dominant"
    return exact_reason


def _rate(numerator: int, denominator: int) -> float:
    """Return a rounded rate, guarding against division by zero."""
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 4)


def write_stream_walkthrough(
    *,
    path: Path,
    summary: dict,
    accepted_records: list[dict],
    rejected_records: list[dict],
    rerun_records: list[dict],
    existing_accepted_records: list[dict] | None = None,
    existing_rejected_records: list[dict] | None = None,
) -> None:
    """Write a markdown walkthrough for a streaming Route 3 run."""
    existing_accepted_records = existing_accepted_records or []
    existing_rejected_records = existing_rejected_records or []
    record_groups = _walkthrough_record_groups(
        existing_accepted_records=existing_accepted_records,
        existing_rejected_records=existing_rejected_records,
        accepted_records=accepted_records,
        rejected_records=rejected_records,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append(f"# Route 3 Streaming Wikipedia Page-ID Walkthrough - {summary.get('run_date', '2026-05-19')}")
    lines.append("")
    lines.append("## Stats")
    lines.append("")
    if summary.get("run_group_id"):
        lines.append(f"- Run group ID: `{summary.get('run_group_id', '')}`")
        lines.append(f"- Run segment ID: `{summary.get('run_segment_id', '')}`")
        lines.append(f"- Artifact manifest: `{summary.get('run_artifact_manifest', '')}`")
    lines.append(f"- Mode: `{summary.get('streaming_mode', '')}`")
    lines.append(f"- Page source: `{summary.get('stream_page_source', '')}`")
    search_queries = summary.get("stream_search_queries", [])
    if search_queries:
        lines.append(f"- Table-search queries: `{'; '.join(str(query) for query in search_queries)}`")
    endpoint_resume = summary.get("endpoint_resume", {})
    if isinstance(endpoint_resume, dict) and endpoint_resume.get("enabled"):
        lines.append(
            "- Endpoint resume: "
            f"{endpoint_resume.get('accepted_records_loaded', 0)} accepted and "
            f"{endpoint_resume.get('rejected_records_loaded', 0)} rejected records loaded"
        )
        lines.append(f"- Existing accepted QAs before run: {len(existing_accepted_records)}")
        lines.append(f"- Existing rejected QAs/pages before run: {len(existing_rejected_records)}")
    lines.append(f"- Attempted page IDs: {summary.get('attempted_page_ids', 0)}")
    if summary.get("attempted_page_ids_unique") is not None:
        lines.append(f"- Unique attempted page IDs: {summary.get('attempted_page_ids_unique', 0)}")
    if summary.get("stream_state_reset"):
        lines.append("- Stream state reset at run start: yes")
    lines.append(f"- Accepted QAs: {summary.get('accepted', 0)}")
    if isinstance(endpoint_resume, dict) and endpoint_resume.get("enabled"):
        lines.append(f"- Accepted QAs after resume: {summary.get('accepted_total', 0)}")
    lines.append(f"- Rejected QAs/pages: {summary.get('rejected', 0)}")
    if isinstance(endpoint_resume, dict) and endpoint_resume.get("enabled"):
        lines.append(f"- Rejected QAs/pages after resume: {summary.get('rejected_total', 0)}")
    llm_yield = _walkthrough_llm_generation_table_yield(
        summary,
        accepted_records,
        rejected_records,
        rerun_records,
    )
    lines.append(
        "- LLM generation table yield: "
        f"{_format_percent_or_na(llm_yield['yield'])} "
        f"({llm_yield['accepted_qas']} accepted QAs / {llm_yield['input_tables']} input tables)"
    )
    lines.append(f"- Transient rerun attempts during run: {summary.get('rerun', 0)}")
    if summary.get("wall_clock_seconds") is not None:
        lines.append(f"- Wall-clock runtime: {float(summary.get('wall_clock_seconds', 0.0)):.4f}s")
    lines.append(f"- DuckDuckGo top K: {summary.get('duckduckgo_top_k', '')}")
    lines.append(f"- Generated search queries per QA: {summary.get('generated_search_query_count', '')}")
    lines.append(f"- DuckDuckGo parallel queries: {summary.get('duckduckgo_parallel_queries', '')}")
    if "duckduckgo_prefer_ddgs" in summary:
        lines.append(
            "- DuckDuckGo ddgs primary path: "
            f"`{'enabled' if summary.get('duckduckgo_prefer_ddgs') else 'disabled'}`, "
            f"backend `{summary.get('duckduckgo_ddgs_backend', '')}`, "
            f"attempts {summary.get('duckduckgo_ddgs_max_attempts', '')}"
        )
    if summary.get("duckduckgo_disabled_fallbacks"):
        lines.append(
            "- DuckDuckGo disabled fallbacks: "
            f"`{', '.join(str(item) for item in summary.get('duckduckgo_disabled_fallbacks', []))}`"
        )
    if "duckduckgo_cooldown_enabled" in summary:
        lines.append(
            "- DuckDuckGo global cooldown: "
            f"`{'enabled' if summary.get('duckduckgo_cooldown_enabled') else 'disabled'}`, "
            f"threshold {summary.get('duckduckgo_cooldown_failure_threshold', '')}, "
            f"{summary.get('duckduckgo_cooldown_initial_seconds', '')}s to "
            f"{summary.get('duckduckgo_cooldown_max_seconds', '')}s"
        )
    if summary.get("min_table_score") is not None:
        lines.append(f"- Minimum Route 3 table score: {summary.get('min_table_score', '')}")
    if summary.get("route3_reasoning_types"):
        lines.append(f"- Route 3 reasoning_type constraint: `{', '.join(summary.get('route3_reasoning_types', []))}`")
    if summary.get("route3_answer_types"):
        lines.append(f"- Route 3 answer_type constraint: `{', '.join(summary.get('route3_answer_types', []))}`")
    if summary.get("route3_table_filter_modes"):
        lines.append(f"- Route 3 table filter modes: `{', '.join(summary.get('route3_table_filter_modes', []))}`")
    if summary.get("route3_table_source_types"):
        lines.append(f"- Route 3 table source types: `{', '.join(summary.get('route3_table_source_types', []))}`")
    if "route3_prose_leakage_scoring_enabled" in summary:
        state = "enabled" if summary.get("route3_prose_leakage_scoring_enabled") else "disabled"
        lines.append(f"- Route 3 prose-leakage scoring: `{state}`")
    if summary.get("stream_page_workers") is not None:
        lines.append(f"- Stream page workers: {summary.get('stream_page_workers', '')}")
        lines.append(f"- Wikipedia concurrency limit: {summary.get('wikipedia_concurrency_limit', '')}")
        if "wikipedia_429_backoff_seconds" in summary:
            lines.append(
                "- Wikipedia 429 backoff: "
                f"{summary.get('wikipedia_429_backoff_seconds', '')}s base, "
                f"{summary.get('wikipedia_429_max_backoff_seconds', '')}s max, "
                f"{summary.get('wikipedia_429_recovery_seconds', '')}s recovery"
            )
        lines.append(f"- DuckDuckGo service concurrency limit: {summary.get('duckduckgo_concurrency_limit', '')}")
        lines.append(
            "- OpenRouter generation/rewrite concurrency limit: "
            f"{summary.get('openrouter_generation_rewrite_concurrency_limit', '')}"
        )
        lines.append(f"- Second-stage concurrency limit: {summary.get('second_stage_concurrency_limit', '')}")
    bounds = summary.get("page_id_bounds", {})
    if isinstance(bounds, dict):
        lines.append(f"- Page-id bounds: {bounds.get('min')} to {bounds.get('max')}")
    lines.append(f"- Stream state: `{summary.get('stream_state', '')}`")
    lines.append(f"- Accepted output: `{summary.get('output_path', '')}`")
    lines.append(f"- Rejected output: `{summary.get('rejected_output_path', '')}`")
    lines.append(f"- Domain policy: `{summary.get('domain_policy', '')}`")
    rerun_pool_ids = summary.get("rerun_pool_ids_after_run", [])
    if isinstance(rerun_pool_ids, list):
        lines.append(f"- Rerun pool after run: `{', '.join(str(page_id) for page_id in rerun_pool_ids) or 'empty'}`")
    lines.append("")
    recipe_segments = summary.get("recipe_segments", [])
    if isinstance(recipe_segments, list) and recipe_segments:
        lines.append("### Recipe Segments")
        lines.append("")
        lines.append("| Configured answer_type | Target | Attempted page IDs | Accepted | Rejected | Rerun |")
        lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
        for segment in recipe_segments:
            if not isinstance(segment, dict):
                continue
            lines.append(
                "| {answer_type} | {target} | {attempted} | {accepted} | {rejected} | {rerun} |".format(
                    answer_type=_escape_table_text(str(segment.get("answer_type", ""))),
                    target=int(segment.get("target_count", segment.get("record_limit", 0)) or 0),
                    attempted=int(segment.get("attempted_page_ids", 0) or 0),
                    accepted=int(segment.get("accepted", 0) or 0),
                    rejected=int(segment.get("rejected", 0) or 0),
                    rerun=int(segment.get("rerun", 0) or 0),
                )
            )
        lines.append("")
    if existing_accepted_records or existing_rejected_records:
        _append_overall_resume_stats(
            lines,
            summary=summary,
            existing_accepted_records=existing_accepted_records,
            existing_rejected_records=existing_rejected_records,
            accepted_records=accepted_records,
            rejected_records=rejected_records,
            rerun_records=rerun_records,
        )
        lines.append("")
    lines.append("### Survival By Layer")
    lines.append("")
    lines.append("| Layer | Unit | Entered | Failed | Survived | Layer survival |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: |")
    for row in summary.get("survival_by_layer", []):
        lines.append(
            "| {layer} | {unit} | {entered} | {failed} | {survived} | {layer_rate:.1%} |".format(
                layer=row.get("layer", ""),
                unit=row.get("unit", ""),
                entered=int(row.get("entered", 0)),
                failed=int(row.get("failed", 0)),
                survived=int(row.get("survived", 0)),
                layer_rate=float(row.get("survival_rate_from_layer_input", 0.0)),
            )
        )
    lines.append("")
    lines.append("### Failure Reasons")
    lines.append("")
    lines.append("| Stage | Reason | Count |")
    lines.append("| --- | --- | ---: |")
    for row in summary.get("failure_reason_counts", []):
        lines.append(f"| `{row.get('stage', '')}` | `{_escape_table_text(str(row.get('reason', '')))}` | {row.get('count', 0)} |")
    if not summary.get("failure_reason_counts"):
        lines.append("| n/a | n/a | 0 |")
    lines.append("")
    _append_record_attribute_stats_section(
        lines,
        title="Answer Type Stats",
        attribute_label="Answer type",
        extractor=record_answer_type,
        record_groups=record_groups,
    )
    lines.append("")
    _append_record_attribute_stats_section(
        lines,
        title="Reasoning Type Stats",
        attribute_label="Reasoning type",
        extractor=record_reasoning_type,
        record_groups=record_groups,
    )
    lines.append("")
    lines.append("### Rerun Pool After Run")
    lines.append("")
    rerun_reasons = summary.get("rerun_pool_failure_reasons_after_run", {})
    if isinstance(rerun_pool_ids, list) and rerun_pool_ids:
        lines.append("| Page ID | Exact reason |")
        lines.append("| ---: | --- |")
        for page_id in rerun_pool_ids:
            reason = ""
            if isinstance(rerun_reasons, dict):
                reason = str(rerun_reasons.get(str(page_id), ""))
            lines.append(f"| {page_id} | `{_escape_table_text(reason)}` |")
    else:
        lines.append("Rerun pool is empty.")
    lines.append("")
    _append_in_run_rerun_outcomes_section(
        lines,
        summary=summary,
        accepted_records=accepted_records,
        rejected_records=rejected_records,
        rerun_records=rerun_records,
    )
    lines.append("")
    _append_phase_timings_section(
        lines,
        summary=summary,
        existing_accepted_records=existing_accepted_records,
        existing_rejected_records=existing_rejected_records,
        accepted_records=accepted_records,
        rejected_records=rejected_records,
    )
    lines.append("")
    lines.append("## Accepted Candidates")
    lines.append("")
    if existing_accepted_records or existing_rejected_records:
        lines.append("Existing endpoint records are shown first; incremental records are the records appended by this run.")
        lines.append("")
    if any(group_accepted for _, group_accepted, _ in record_groups):
        for group_label, group_accepted, _ in record_groups:
            if len(record_groups) > 1:
                lines.append(f"### {group_label}")
                lines.append("")
            if group_accepted:
                lines.append("| Page ID | Table type | Answer type | Question | Answer | Source |")
                lines.append("| ---: | --- | --- | --- | --- | --- |")
                for record in group_accepted:
                    lines.append(_walkthrough_candidate_row(record))
            else:
                lines.append("No accepted candidates in this scope.")
            lines.append("")
    else:
        lines.append("No accepted candidates in this run.")
    _append_second_stage_filtering_responses_section(
        lines,
        record_groups=record_groups,
        rerun_records=rerun_records,
    )
    lines.append("")
    lines.append("## Rejected And Rerun Decisions")
    lines.append("")
    if any(group_rejected for _, _, group_rejected in record_groups) or rerun_records:
        for group_label, _, group_rejected in record_groups:
            if len(record_groups) > 1:
                lines.append(f"### {group_label}")
                lines.append("")
            if group_rejected:
                lines.append("| Page ID | Table type | Answer type | Question | Answer | Source | Exact reason |")
                lines.append("| ---: | --- | --- | --- | --- | --- | --- |")
                for record in group_rejected:
                    lines.append(_walkthrough_candidate_row(record, exact_reason=exact_failure_reason(record)))
            else:
                lines.append("No rejected decisions in this scope.")
            lines.append("")
        if rerun_records:
            lines.append("### Rerun Records")
            lines.append("")
            lines.append("| Page ID | Table type | Answer type | Question | Answer | Source | Exact reason |")
            lines.append("| ---: | --- | --- | --- | --- | --- | --- |")
            for record in rerun_records:
                lines.append(_walkthrough_candidate_row(record, exact_reason=str(record.get("reason", ""))))
    else:
        lines.append("No rejected or rerun decisions in this run.")
    lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _walkthrough_candidate_row(record: dict, *, exact_reason: str | None = None) -> str:
    """Render one accepted/rejected/rerun candidate row for the stream walkthrough."""
    cells = [
        str(record_page_id(record) or record.get("page_id", "")),
        f"`{_escape_table_text(_walkthrough_record_table_type(record))}`",
        f"`{_escape_table_text(record_answer_type(record))}`",
        _escape_table_text(str(record.get("question", ""))),
        _escape_table_text(str(record.get("answer", ""))),
        _escape_table_text(_walkthrough_record_source_url(record)),
    ]
    if exact_reason is not None:
        cells.append(f"`{_escape_table_text(str(exact_reason))}`")
    return "| " + " | ".join(cells) + " |"


def _walkthrough_record_table_type(record: dict) -> str:
    """Return the table type displayed in walkthrough candidate tables."""
    table_type = record_table_type(record)
    if table_type:
        return table_type
    return str(record.get("table_type", "") or "unknown").strip() or "unknown"


def _walkthrough_record_source_url(record: dict) -> str:
    """Return the best source URL displayed for a walkthrough candidate row."""
    metadata = record.get("source_metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
    for source in (metadata, record):
        if not isinstance(source, dict):
            continue
        for key in ("canonical_url", "stream_source_url", "source_url", "url"):
            value = str(source.get(key) or "").strip()
            if value:
                return value
    evidence = record.get("evidence", {})
    if isinstance(evidence, dict):
        return str(evidence.get("url") or "").strip()
    return ""


def _append_in_run_rerun_outcomes_section(
    lines: list[str],
    *,
    summary: dict,
    accepted_records: list[dict],
    rejected_records: list[dict],
    rerun_records: list[dict],
) -> None:
    """Append final outcomes for page IDs retried from the rerun pool during this invocation."""
    if not rerun_records:
        return
    accepted_by_page_id = {record_page_id(record): record for record in accepted_records}
    rejected_by_page_id = {record_page_id(record): record for record in rejected_records}
    rerun_pool_ids = {
        page_id
        for page_id in summary.get("rerun_pool_ids_after_run", [])
        if page_id not in {None, ""}
    }
    attempt_counts: dict[int | str, int] = {}
    first_reason: dict[int | str, str] = {}
    for record in rerun_records:
        page_id = record.get("page_id", "")
        if page_id in {None, ""}:
            continue
        attempt_counts[page_id] = attempt_counts.get(page_id, 0) + 1
        first_reason.setdefault(page_id, str(record.get("reason", "")))
    if not attempt_counts:
        return

    lines.append("### In-Run Rerun Outcomes")
    lines.append("")
    lines.append(
        "These rows show transient rerun-pool attempts and whether the same page ID later reached a final decision in this invocation."
    )
    lines.append("")
    lines.append("| Page ID | Rerun attempts | Final outcome | Final reason/question | First transient reason |")
    lines.append("| ---: | ---: | --- | --- | --- |")
    for page_id in sorted(attempt_counts, key=lambda value: str(value)):
        if page_id in accepted_by_page_id:
            outcome = "accepted"
            detail = str(accepted_by_page_id[page_id].get("question", ""))
        elif page_id in rejected_by_page_id:
            outcome = "rejected"
            detail = exact_failure_reason(rejected_by_page_id[page_id])
        elif page_id in rerun_pool_ids:
            outcome = "still_in_rerun_pool"
            detail = ""
        else:
            outcome = "not_finalized_in_this_invocation"
            detail = ""
        lines.append(
            "| {page_id} | {attempts} | `{outcome}` | {detail} | `{reason}` |".format(
                page_id=page_id,
                attempts=attempt_counts[page_id],
                outcome=outcome,
                detail=_escape_table_text(detail),
                reason=_escape_table_text(first_reason.get(page_id, "")),
            )
        )


def _append_phase_timings_section(
    lines: list[str],
    *,
    summary: dict,
    existing_accepted_records: list[dict],
    existing_rejected_records: list[dict],
    accepted_records: list[dict],
    rejected_records: list[dict],
) -> None:
    """Append timing tables for the incremental segment and full displayed run."""
    incremental_records = [*accepted_records, *rejected_records]
    total_records = [
        *existing_accepted_records,
        *existing_rejected_records,
        *accepted_records,
        *rejected_records,
    ]
    incremental_stats = summary.get("phase_timing_stats_seconds")
    if not isinstance(incremental_stats, dict):
        incremental_stats = phase_timing_stats(incremental_records)
    total_stats = phase_timing_stats(total_records)
    is_incremental = bool(existing_accepted_records or existing_rejected_records)

    lines.append("### Phase Timings")
    lines.append("")
    lines.append(
        "Timing nesting: `wall_clock_seconds` is the whole run. "
        "`total_generation_seconds` contains page fetch/cache reuse, table parse, "
        "first-paragraph extraction, and generation LLM work for one page. "
        "`total_processing_seconds` contains rewrite/surface checks, number margin, shared validation, "
        "DuckDuckGo search, second-stage grading when enabled, and dedup checks for one generated candidate. "
        "`candidate_processing_seconds` is an alias of `total_processing_seconds`. "
        "Route-local output checks, shared validation, and dedup currently do not have standalone child timers. "
        "Generation/source timings are deduplicated by page or LLM prompt so all5 slots do not multiply shared work. "
        "Child phase totals are useful for bottlenecks, but they should not be added to parent totals."
    )
    if is_incremental:
        lines.append(
            "For incremental walkthroughs, `Incremental run` means only the current segment. "
            "`Total displayed run` means the endpoint records loaded at resume plus the current segment."
        )
    lines.append("")
    lines.append("| Pipeline order | Phase | Parent/child | Additive? | Meaning |")
    lines.append("| ---: | --- | --- | --- | --- |")
    for row in _phase_timing_explanation_rows():
        lines.append(
            "| {order} | `{phase}` | {kind} | {additive} | {meaning} |".format(
                order=row["order"],
                phase=row["phase"],
                kind=row["kind"],
                additive=row["additive"],
                meaning=row["meaning"],
            )
        )
    lines.append("")

    if is_incremental:
        _append_phase_scope_summary_table(
            lines,
            summary=summary,
            incremental_stats=incremental_stats,
            total_stats=total_stats,
            incremental_record_count=len(incremental_records),
            total_record_count=len(total_records),
        )
        lines.append("")
        lines.append("#### Incremental Run Phase Timings")
    else:
        lines.append("#### Current Run Phase Timings")
    lines.append("")
    _append_phase_stats_table(lines, incremental_stats)
    if is_incremental:
        lines.append("")
        lines.append("#### Total Displayed Run Phase Timings")
        lines.append("")
        _append_phase_stats_table(lines, total_stats)


def _append_phase_scope_summary_table(
    lines: list[str],
    *,
    summary: dict,
    incremental_stats: dict,
    total_stats: dict,
    incremental_record_count: int,
    total_record_count: int,
) -> None:
    """Append compact timing totals for the incremental and cumulative scopes."""
    lines.append("#### Time Stats By Scope")
    lines.append("")
    lines.append(
        "| Scope | Wall-clock seconds | Page IDs/records | Final decision records | "
        "Total generation seconds | Avg generation seconds | Total processing seconds | "
        "Avg processing seconds | Total second-stage seconds | Avg second-stage seconds |"
    )
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    attempted = int(summary.get("attempted_page_ids", 0) or 0)
    incremental_pages = attempted
    endpoint_resume = summary.get("endpoint_resume", {})
    if not isinstance(endpoint_resume, dict):
        endpoint_resume = {}
    existing_record_count = max(0, total_record_count - incremental_record_count)
    final_decisions_loaded = endpoint_resume.get("final_decisions_loaded")
    try:
        existing_pages = int(final_decisions_loaded)
    except (TypeError, ValueError):
        existing_pages = existing_record_count
    total_pages = existing_pages + attempted
    lines.append(
        _phase_scope_summary_row(
            scope="Incremental run",
            wall_clock_seconds=_optional_float(summary.get("wall_clock_seconds")),
            page_count=incremental_pages,
            record_count=incremental_record_count,
            stats=incremental_stats,
        )
    )
    lines.append(
        _phase_scope_summary_row(
            scope="Total displayed run",
            wall_clock_seconds=_walkthrough_total_wall_clock_seconds(summary),
            page_count=total_pages,
            record_count=total_record_count,
            stats=total_stats,
        )
    )


def _phase_scope_summary_row(
    *,
    scope: str,
    wall_clock_seconds: float | None,
    page_count: int,
    record_count: int,
    stats: dict,
) -> str:
    """Return one compact timing summary row."""
    generation = _phase_stats_for(stats, "total_generation_seconds")
    processing = _phase_stats_for(stats, "total_processing_seconds")
    second_stage = _phase_stats_for(stats, "second_stage_grading_seconds")
    return (
        "| {scope} | {wall_clock} | {page_count} | {record_count} | "
        "{generation_total} | {generation_avg} | {processing_total} | {processing_avg} | "
        "{second_stage_total} | {second_stage_avg} |"
    ).format(
        scope=scope,
        wall_clock=_format_optional_seconds(wall_clock_seconds),
        page_count=page_count,
        record_count=record_count,
        generation_total=_format_optional_seconds(generation.get("total")),
        generation_avg=_format_optional_seconds(generation.get("average")),
        processing_total=_format_optional_seconds(processing.get("total")),
        processing_avg=_format_optional_seconds(processing.get("average")),
        second_stage_total=_format_optional_seconds(second_stage.get("total")),
        second_stage_avg=_format_optional_seconds(second_stage.get("average")),
    )


def _append_phase_stats_table(lines: list[str], stats_by_phase: dict) -> None:
    """Append one detailed phase timing table."""
    lines.append("| Phase | Count | Total seconds | Average seconds | Max seconds |")
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    if not stats_by_phase:
        lines.append("| n/a | 0 | n/a | n/a | n/a |")
        return
    for phase, stats in stats_by_phase.items():
        if not isinstance(stats, dict):
            continue
        lines.append(
            "| `{phase}` | {count} | {total} | {average} | {max_value} |".format(
                phase=phase,
                count=int(stats.get("count", 0) or 0),
                total=_format_optional_seconds(stats.get("total")),
                average=_format_optional_seconds(stats.get("average")),
                max_value=_format_optional_seconds(stats.get("max")),
            )
        )


def _phase_stats_for(stats_by_phase: dict, phase: str) -> dict:
    """Return timing stats for one phase, with a stable empty fallback."""
    stats = stats_by_phase.get(phase, {})
    return stats if isinstance(stats, dict) else {}


def _format_optional_seconds(value: object) -> str:
    """Format seconds for markdown timing tables."""
    seconds = _optional_float(value)
    if seconds is None:
        return "n/a"
    return f"{seconds:.4f}"


def _format_percent_or_na(value: object) -> str:
    """Format a ratio as a one-decimal percent."""
    ratio = _optional_float(value)
    if ratio is None:
        return "n/a"
    return f"{ratio:.1%}"


def _optional_float(value: object) -> float | None:
    """Convert a value to float when possible."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _walkthrough_total_wall_clock_seconds(summary: dict) -> float | None:
    """Return cumulative wall-clock seconds for a resumed walkthrough when available."""
    current_wall_clock = _optional_float(summary.get("wall_clock_seconds"))
    if not isinstance(summary.get("endpoint_resume"), dict) or not summary["endpoint_resume"].get("enabled"):
        return current_wall_clock
    manifest_path = _walkthrough_manifest_path(summary)
    if manifest_path is None or not manifest_path.exists():
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, JSONDecodeError):
        return None
    segments = manifest.get("segments", [])
    if not isinstance(segments, list):
        return None
    summary_output = str(summary.get("summary_output") or "")
    segment_id = str(summary.get("run_segment_id") or "")
    total = 0.0
    for segment in segments:
        if not isinstance(segment, dict):
            continue
        segment_wall_clock = _optional_float(segment.get("wall_clock_seconds"))
        if segment_wall_clock is not None:
            total += segment_wall_clock
        if _manifest_segment_matches_summary(segment, summary_output=summary_output, segment_id=segment_id):
            return round(total, 4)
    if total > 0 and current_wall_clock is not None:
        return round(total + current_wall_clock, 4)
    return None


def _walkthrough_manifest_path(summary: dict) -> Path | None:
    """Return the most likely run artifact manifest path for this walkthrough."""
    raw_manifest_path = str(summary.get("run_artifact_manifest") or "").strip()
    if raw_manifest_path:
        return _workspace_relative_path(raw_manifest_path)
    output_path = str(summary.get("output_path") or "").strip()
    if output_path:
        accepted_path = _workspace_relative_path(output_path)
        suffix = "_accepted.jsonl"
        if accepted_path.name.endswith(suffix):
            run_group_id = accepted_path.name[: -len(suffix)]
            return accepted_path.parent / "run_manifests" / f"{run_group_id}.json"
    return None


def _workspace_relative_path(raw_path: str) -> Path:
    """Resolve a possibly relative artifact path against the repository root."""
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return ROOT / path


def _manifest_segment_matches_summary(segment: dict, *, summary_output: str, segment_id: str) -> bool:
    """Return whether one manifest segment is the current summary segment."""
    segment_summary_output = str(segment.get("summary_output") or "")
    segment_identifier = str(segment.get("segment_id") or "")
    return bool(
        (summary_output and segment_summary_output == summary_output)
        or (segment_id and segment_identifier == segment_id)
    )


def _append_overall_resume_stats(
    lines: list[str],
    *,
    summary: dict,
    existing_accepted_records: list[dict],
    existing_rejected_records: list[dict],
    accepted_records: list[dict],
    rejected_records: list[dict],
    rerun_records: list[dict],
) -> None:
    """Append overall counts across endpoint-loaded and incremental records."""
    existing_final = len(existing_accepted_records) + len(existing_rejected_records)
    attempted = int(summary.get("attempted_page_ids", 0) or 0)
    incremental_accepted = len(accepted_records)
    incremental_rejected = len(rejected_records)
    incremental_rerun = len(rerun_records)
    overall_pages = existing_final + attempted
    overall_accepted = len(existing_accepted_records) + incremental_accepted
    overall_rejected = len(existing_rejected_records) + incremental_rejected
    lines.append("### Overall Displayed Stats")
    lines.append("")
    lines.append("| Scope | Page IDs/records | Accepted | Rejected | Rerun | Accepted/page rate |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
    lines.append(
        "| Existing endpoint records | {records} | {accepted} | {rejected} | 0 | {rate:.1%} |".format(
            records=existing_final,
            accepted=len(existing_accepted_records),
            rejected=len(existing_rejected_records),
            rate=_rate(len(existing_accepted_records), existing_final),
        )
    )
    lines.append(
        "| Incremental run | {records} | {accepted} | {rejected} | {rerun} | {rate:.1%} |".format(
            records=attempted,
            accepted=incremental_accepted,
            rejected=incremental_rejected,
            rerun=incremental_rerun,
            rate=_rate(incremental_accepted, attempted),
        )
    )
    lines.append(
        "| Overall displayed | {records} | {accepted} | {rejected} | {rerun} | {rate:.1%} |".format(
            records=overall_pages,
            accepted=overall_accepted,
            rejected=overall_rejected,
            rerun=incremental_rerun,
            rate=_rate(overall_accepted, overall_pages),
        )
    )


def _append_record_attribute_stats_section(
    lines: list[str],
    *,
    title: str,
    attribute_label: str,
    extractor,
    record_groups: list[tuple[str, list[dict], list[dict]]],
) -> None:
    """Append accepted/rejected counts grouped by one record attribute."""
    lines.append(f"### {title}")
    lines.append("")
    lines.append(f"| Scope | {attribute_label} | Accepted | Rejected | Total | Accepted rate |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: |")
    wrote_row = False
    for group_label, group_accepted, group_rejected in record_groups:
        rows = _record_attribute_counts(group_accepted, group_rejected, extractor=extractor)
        for value, accepted_count, rejected_count in rows:
            total = accepted_count + rejected_count
            lines.append(
                f"| {group_label} | `{_escape_table_text(value)}` | {accepted_count} | "
                f"{rejected_count} | {total} | {_rate(accepted_count, total):.1%} |"
            )
            wrote_row = True
    if not wrote_row:
        lines.append("| n/a | n/a | 0 | 0 | 0 | 0.0% |")


def _record_attribute_counts(
    accepted_records: list[dict],
    rejected_records: list[dict],
    *,
    extractor,
) -> list[tuple[str, int, int]]:
    """Return sorted accepted/rejected counts for one extracted record attribute."""
    accepted_counts = Counter(extractor(record) for record in accepted_records)
    rejected_counts = Counter(extractor(record) for record in rejected_records)
    values = sorted(set(accepted_counts) | set(rejected_counts))
    return [
        (value, int(accepted_counts.get(value, 0)), int(rejected_counts.get(value, 0)))
        for value in values
    ]


def record_answer_type(record: dict) -> str:
    """Return the SimpleQA Verified answer type for a JSONL record."""
    source_metadata = record.get("source_metadata", {})
    if not isinstance(source_metadata, dict):
        source_metadata = {}
    value = record.get("answer_type") or source_metadata.get("answer_type")
    if not str(value or "").strip():
        return "unknown"
    try:
        normalized = normalize_route3_answer_types([str(value or "")])
    except ValueError:
        normalized = ()
    if normalized:
        return normalized[0]
    return "Other"


def record_reasoning_type(record: dict) -> str:
    """Return the fixed Route 3 reasoning type for a JSONL record."""
    return "single_fact"

def _walkthrough_record_groups(
    *,
    existing_accepted_records: list[dict],
    existing_rejected_records: list[dict],
    accepted_records: list[dict],
    rejected_records: list[dict],
) -> list[tuple[str, list[dict], list[dict]]]:
    """Return record scopes for walkthrough rendering."""
    if existing_accepted_records or existing_rejected_records:
        return [
            ("Existing Endpoint Records", existing_accepted_records, existing_rejected_records),
            ("Incremental Records", accepted_records, rejected_records),
        ]
    return [("Current Run Records", accepted_records, rejected_records)]


def _append_second_stage_filtering_responses_section(
    lines: list[str],
    *,
    record_groups: list[tuple[str, list[dict], list[dict]]],
    rerun_records: list[dict],
) -> None:
    """Append exact second-stage small-model QA responses to the walkthrough."""
    lines.append("## Second-Stage Filtering Responses")
    lines.append("")
    lines.append(
        "These are the small-model QA responses used by the second-stage filter: "
        "`openai/gpt-4.1-mini` and `google/gemini-3-flash-preview`."
    )
    lines.append("")
    displayed_any = False
    for group_label, group_accepted, group_rejected in record_groups:
        records = [
            record
            for record in [*group_accepted, *group_rejected]
            if _has_second_stage_model_responses(_second_stage_panel_features(record))
        ]
        if len(record_groups) > 1:
            lines.append(f"### {group_label}")
            lines.append("")
        if records:
            displayed_any = True
            lines.append("| Page ID | Question | Reference answer | openai/gpt-4.1-mini | google/gemini-3-flash-preview |")
            lines.append("| ---: | --- | --- | --- | --- |")
            for record in records:
                features = _second_stage_panel_features(record)
                lines.append(
                    "| {page_id} | {question} | {reference_answer} | {openai} | {gemini} |".format(
                        page_id=record_page_id(record),
                        question=_escape_table_text(str(record.get("question", ""))),
                        reference_answer=_escape_table_text(_second_stage_reference_answer(record, features)),
                        openai=_escape_table_text(_second_stage_model_cell(features, "openai/gpt-4.1-mini")),
                        gemini=_escape_table_text(_second_stage_model_cell(features, "google/gemini-3-flash-preview")),
                    )
                )
            lines.append("")
        elif len(record_groups) > 1:
            lines.append("No second-stage model responses in this scope.")
            lines.append("")
    if not displayed_any:
        lines.append("No second-stage model responses were produced in this run.")
    if rerun_records:
        lines.append("")
        lines.append("Rerun-pool entries have no second-stage filtering response unless they reached the panel before the transient failure.")


def _second_stage_panel_features(record: dict) -> dict:
    """Return the stored second-stage panel features for an accepted or rejected record."""
    features = record.get("panel_grading_features")
    if isinstance(features, dict):
        return features
    notes = record.get("rejection_notes", {})
    if isinstance(notes, dict):
        features = notes.get("panel_grading_features")
        if isinstance(features, dict):
            return features
    return {}


def _second_stage_reference_answer(record: dict, features: dict) -> str:
    """Return the reference answer displayed for one second-stage row."""
    reference = features.get("reference_answer_for_grading") or features.get("gold_answer")
    if reference is not None:
        return str(reference)
    return str(record.get("answer", ""))


def _second_stage_model_cell(features: dict, model_name: str) -> str:
    """Return a compact grade/prediction cell for one panel model."""
    models = features.get("models")
    if not isinstance(models, list):
        return "not run"
    for row in models:
        if not isinstance(row, dict) or row.get("model") != model_name:
            continue
        grade = str(row.get("grade", "UNKNOWN")).strip() or "UNKNOWN"
        predicted_answer = str(row.get("predicted_answer", "")).strip()
        if predicted_answer:
            return f"{grade}; predicted_answer: {predicted_answer}"
        return f"{grade}; predicted_answer:"
    return "not run"


def _has_second_stage_model_responses(features: dict) -> bool:
    """Return whether panel features include at least one model answer row."""
    models = features.get("models")
    return isinstance(models, list) and any(isinstance(row, dict) and row.get("model") for row in models)


def record_page_id(record: dict) -> int | str:
    """Return the positive Wikipedia page ID represented by one output record."""
    page_id = positive_record_page_id(record.get("page_id"))
    if page_id is not None:
        return page_id
    metadata = record.get("source_metadata", {})
    if isinstance(metadata, dict):
        page_id = positive_record_page_id(metadata.get("page_id"))
        if page_id is not None:
            return page_id
        streaming = metadata.get("streaming_discovery", {})
        if isinstance(streaming, dict):
            page_id = positive_record_page_id(streaming.get("page_id"))
            if page_id is not None:
                return page_id
        for key in ("source_url", "stream_source_url", "canonical_url"):
            page_id = positive_record_page_id(normalize_wikipedia_page_id(str(metadata.get(key) or "")))
            if page_id is not None:
                return page_id
    return ""


def positive_record_page_id(value: object) -> int | None:
    """Coerce one value into a positive Wikipedia page ID."""
    try:
        page_id = int(value)
    except (TypeError, ValueError):
        return None
    return page_id if page_id > 0 else None


def _escape_table_text(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def aggregate_phase_timings(accepted: list[dict], rejected: list[dict]) -> dict[str, float]:
    """Aggregate phase timings with the same dedupe scope used by walkthroughs."""
    stats = phase_timing_stats([*accepted, *rejected])
    return {
        phase: round(float(values.get("total", 0.0) or 0.0), 4)
        for phase, values in stats.items()
        if isinstance(values, dict)
    }


__all__ = [
    'EndpointResumeState',
    'aggregate_phase_timings',
    'effective_stream_random_seed',
    'ensure_page_id_list_entry_metadata',
    'exact_failure_reason',
    'failure_reason_counts',
    'llm_generation_table_yield_summary',
    'load_endpoint_jsonl',
    'normalize_stream_fresh_cached_page_count',
    'normalize_stream_reuse_cached_page_count',
    'phase_timing_stats',
    'positive_record_page_id',
    'record_answer_type',
    'record_page_id',
    'record_reasoning_type',
    'record_table_type',
    'run_group_id',
    'run_segment_id',
    'safe_artifact_id',
    'source_stage_rejection_reason',
    'stream_budget_numeric_count',
    'survival_by_layer',
    'write_stream_walkthrough',
]
