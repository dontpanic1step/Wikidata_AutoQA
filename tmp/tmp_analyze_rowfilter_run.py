#!/usr/bin/env python3
"""Temporary diagnostics for the Route 3 infobox row-filter AWS test."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                records.append({"_parse_error": str(exc), "_raw": line[:500]})
    return records


def _first_existing(root: Path, patterns: list[str]) -> Path | None:
    for pattern in patterns:
        matches = sorted(root.glob(pattern))
        if matches:
            return matches[0]
    return None


def _artifact_paths(root: Path) -> dict[str, Path | None]:
    """Return run artifact paths, accepting either a directory or a file prefix."""
    if root.is_dir():
        return {
            "accepted": _first_existing(root, ["*_accepted.jsonl", "accepted.jsonl"]),
            "rejected": _first_existing(root, ["*_rejected.jsonl", "rejected.jsonl"]),
            "summary": _first_existing(root, ["*_summary.json", "summary.json"]),
            "state": _first_existing(root, ["*_state.json"]),
        }
    parent = root.parent
    prefix = root.name
    return {
        "accepted": parent / f"{prefix}_accepted.jsonl",
        "rejected": parent / f"{prefix}_rejected.jsonl",
        "summary": parent / f"{prefix}_summary.json",
        "state": parent / f"{prefix}_state.json",
    }


def _reason(record: dict[str, Any]) -> str:
    metadata = record.get("source_metadata", {})
    return str(
        record.get("failing_reason")
        or record.get("rejection_reason")
        or metadata.get("discard_reason")
        or record.get("discard_reason")
        or ""
    )


def _reason_class(reason: str) -> str:
    return reason.split(":", 1)[0] if reason else ""


def _table_filter_reason(reason: str) -> str:
    marker = "wikipedia_infobox_table_filter_rejected:"
    if marker not in reason:
        return ""
    return reason.split(marker, 1)[1]


def _state_error_details(state: dict[str, Any]) -> Counter[str]:
    details = state.get("rerun_error_details", {})
    counter: Counter[str] = Counter()
    if not isinstance(details, dict):
        return counter
    for detail in details.values():
        if not isinstance(detail, dict):
            continue
        error_type = str(detail.get("error_type") or "unknown")
        message = str(detail.get("error_message") or "")
        if "timed out" in message.lower():
            message_bucket = "timed out"
        elif "remote end closed" in message.lower():
            message_bucket = "remote closed"
        elif "connection reset" in message.lower():
            message_bucket = "connection reset"
        else:
            message_bucket = message[:80] or "no message"
        counter[f"{error_type}: {message_bucket}"] += 1
    return counter


def _selection_stats(records: list[dict[str, Any]]) -> dict[str, Any]:
    table_types: Counter[str] = Counter()
    answer_types: Counter[str] = Counter()
    score_bonus: Counter[str] = Counter()
    rowfilter_removed = 0
    rowfilter_seen = 0
    for record in records:
        metadata = record.get("source_metadata", {})
        answer_types[str(record.get("answer_type") or metadata.get("answer_type") or "")] += 1
        selected = metadata.get("selected_source_table") or {}
        table_types[str(selected.get("table_type") or "")] += 1
        for row in metadata.get("table_selection", [])[:1]:
            bonus = row.get("answer_type_score_bonus")
            if bonus is not None:
                score_bonus[str(bonus)] += 1
            filtering = row.get("infobox_row_filtering") or {}
            if filtering:
                rowfilter_seen += 1
                rowfilter_removed += int(filtering.get("removed_row_count") or 0)
    return {
        "table_types": dict(table_types),
        "answer_types": dict(answer_types),
        "answer_type_score_bonus": dict(score_bonus),
        "top_selection_rowfilter_seen": rowfilter_seen,
        "top_selection_rowfilter_removed_total": rowfilter_removed,
    }


def summarize_run(label: str, root: Path) -> dict[str, Any]:
    paths = _artifact_paths(root)
    accepted_path = paths["accepted"]
    rejected_path = paths["rejected"]
    summary_path = paths["summary"]
    state_path = paths["state"]
    accepted = _read_jsonl(accepted_path) if accepted_path else []
    rejected = _read_jsonl(rejected_path) if rejected_path else []
    summary = _load_json(summary_path) if summary_path else {}
    state = _load_json(state_path) if state_path else {}
    reason_counts = Counter(_reason_class(_reason(record)) for record in rejected)
    table_filter_counts = Counter(
        _table_filter_reason(_reason(record))
        for record in rejected
        if _table_filter_reason(_reason(record))
    )
    state_failure_counts = Counter(
        _reason_class(str(reason))
        for reason in (state.get("failure_reasons") or {}).values()
    )
    stats = state.get("stats") if isinstance(state.get("stats"), dict) else {}
    result = {
        "label": label,
        "root": str(root),
        "accepted_path": str(accepted_path) if accepted_path else "",
        "rejected_path": str(rejected_path) if rejected_path else "",
        "summary_path": str(summary_path) if summary_path else "",
        "state_path": str(state_path) if state_path else "",
        "accepted_jsonl": len(accepted),
        "rejected_jsonl": len(rejected),
        "accepted_rate_finalized": round(len(accepted) / max(1, len(accepted) + len(rejected)), 4),
        "state_stats": stats,
        "summary_counts": {
            key: summary.get(key)
            for key in ["accepted", "accepted_total", "rejected", "record_limit", "stream_state_stats"]
            if key in summary
        },
        "rejected_reason_classes": reason_counts.most_common(20),
        "state_failure_classes": state_failure_counts.most_common(20),
        "duckduckgo_error_details": _state_error_details(state).most_common(20),
        "table_filter_reasons": table_filter_counts.most_common(30),
        "accepted_selection_stats": _selection_stats(accepted),
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("runs", nargs="+", help="LABEL=PATH")
    args = parser.parse_args()

    summaries = []
    for value in args.runs:
        label, _, path = value.partition("=")
        summaries.append(summarize_run(label, Path(path)))
    if args.json:
        print(json.dumps(summaries, indent=2, ensure_ascii=False))
        return
    for summary in summaries:
        print(f"\n== {summary['label']} ==")
        print(f"root: {summary['root']}")
        print(f"accepted/rejected jsonl: {summary['accepted_jsonl']} / {summary['rejected_jsonl']}")
        print(f"accepted rate over finalized: {summary['accepted_rate_finalized']:.2%}")
        print(f"state stats: {summary['state_stats']}")
        print(f"summary counts: {summary['summary_counts']}")
        print("rejected reason classes:")
        for reason, count in summary["rejected_reason_classes"]:
            print(f"  {count:5d} {reason}")
        print("state failure classes:")
        for reason, count in summary["state_failure_classes"]:
            print(f"  {count:5d} {reason}")
        print("duckduckgo/rerun error details:")
        for reason, count in summary["duckduckgo_error_details"]:
            print(f"  {count:5d} {reason}")
        print("table filter reasons:")
        for reason, count in summary["table_filter_reasons"][:15]:
            print(f"  {count:5d} {reason}")
        print(f"accepted selection stats: {summary['accepted_selection_stats']}")


if __name__ == "__main__":
    main()
