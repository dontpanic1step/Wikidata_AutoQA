"""Analyze current Route 3 all5 rejection order and extract discard snapshots."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


PAGEVIEW_REASON = "wikipedia_pageview_prefilter_rejected"
SEARCH_ERROR_REASON = "search_longtail_verifier_error"
LLM_DISCARDED_REASON = "wikipedia_infobox_llm_discarded"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rejected", type=Path, required=True)
    parser.add_argument("--summary-output", type=Path, required=True)
    parser.add_argument("--discarded-output", type=Path, required=True)
    parser.add_argument("--chunk-count", type=int, default=5)
    parser.add_argument("--rolling-window", type=int, default=20)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = _load_jsonl(args.rejected)
    observation = _build_observation(
        rows,
        chunk_count=max(1, int(args.chunk_count)),
        rolling_window=max(1, int(args.rolling_window)),
    )
    discarded = [_discard_snapshot(row) for row in rows if row["reason"] == LLM_DISCARDED_REASON]
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.discarded_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(observation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    _write_jsonl(args.discarded_output, discarded)
    print(json.dumps(observation, indent=2, ensure_ascii=False))
    print(f"discarded_snapshot_count={len(discarded)} output={args.discarded_output}")
    return 0


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                rows.append(
                    {
                        "line_number": line_number,
                        "parse_error": str(exc),
                        "reason": "json_parse_error",
                        "record": {},
                    }
                )
                continue
            rows.append(
                {
                    "line_number": line_number,
                    "reason": str(payload.get("rejection_reason") or ""),
                    "failing_reason": str(payload.get("failing_reason") or payload.get("rejection_rule") or ""),
                    "record": payload,
                }
            )
    return rows


def _build_observation(
    rows: list[dict[str, Any]],
    *,
    chunk_count: int,
    rolling_window: int,
) -> dict[str, Any]:
    non_pageview = [row for row in rows if row["reason"] != PAGEVIEW_REASON]
    search_error_positions = [
        index
        for index, row in enumerate(non_pageview, start=1)
        if row["reason"] == SEARCH_ERROR_REASON
    ]
    streaks = _streaks(search_error_positions)
    chunks = _chunk_stats(non_pageview, chunk_count=chunk_count)
    rolling = _rolling_stats(non_pageview, window=rolling_window)
    reasons = Counter(row["reason"] for row in rows)
    non_pageview_reasons = Counter(row["reason"] for row in non_pageview)
    failing_reasons = Counter(row["failing_reason"] for row in rows if row.get("failing_reason"))
    trend = _trend_label(chunks)
    return {
        "input_record_count": len(rows),
        "pageview_prefilter_rejected_count": reasons.get(PAGEVIEW_REASON, 0),
        "non_pageview_record_count": len(non_pageview),
        "search_longtail_verifier_error_count": len(search_error_positions),
        "search_longtail_verifier_error_rate_excluding_pageview": _rate(
            len(search_error_positions),
            len(non_pageview),
        ),
        "search_error_positions_excluding_pageview": search_error_positions,
        "search_error_streaks_excluding_pageview": streaks,
        "max_search_error_streak_excluding_pageview": max((row["length"] for row in streaks), default=0),
        "chunk_stats_excluding_pageview": chunks,
        "rolling_window": rolling_window,
        "rolling_stats_excluding_pageview": rolling,
        "trend_label": trend,
        "reason_counts": reasons.most_common(),
        "non_pageview_reason_counts": non_pageview_reasons.most_common(),
        "failing_reason_counts": failing_reasons.most_common(),
    }


def _streaks(positions: list[int]) -> list[dict[str, int]]:
    if not positions:
        return []
    streak_rows: list[dict[str, int]] = []
    start = previous = positions[0]
    for position in positions[1:]:
        if position == previous + 1:
            previous = position
            continue
        streak_rows.append({"start": start, "end": previous, "length": previous - start + 1})
        start = previous = position
    streak_rows.append({"start": start, "end": previous, "length": previous - start + 1})
    return streak_rows


def _chunk_stats(rows: list[dict[str, Any]], *, chunk_count: int) -> list[dict[str, Any]]:
    if not rows:
        return []
    chunks: list[dict[str, Any]] = []
    total = len(rows)
    for index in range(chunk_count):
        start = (index * total) // chunk_count
        end = ((index + 1) * total) // chunk_count
        chunk = rows[start:end]
        error_count = sum(1 for row in chunk if row["reason"] == SEARCH_ERROR_REASON)
        chunks.append(
            {
                "chunk_index": index + 1,
                "start_non_pageview_position": start + 1 if chunk else 0,
                "end_non_pageview_position": end if chunk else 0,
                "record_count": len(chunk),
                "search_error_count": error_count,
                "search_error_rate": _rate(error_count, len(chunk)),
                "reason_counts": Counter(row["reason"] for row in chunk).most_common(),
            }
        )
    return chunks


def _rolling_stats(rows: list[dict[str, Any]], *, window: int) -> list[dict[str, Any]]:
    if not rows:
        return []
    stats: list[dict[str, Any]] = []
    for start in range(0, len(rows), window):
        chunk = rows[start : start + window]
        error_count = sum(1 for row in chunk if row["reason"] == SEARCH_ERROR_REASON)
        stats.append(
            {
                "start_non_pageview_position": start + 1,
                "end_non_pageview_position": start + len(chunk),
                "record_count": len(chunk),
                "search_error_count": error_count,
                "search_error_rate": _rate(error_count, len(chunk)),
            }
        )
    return stats


def _trend_label(chunks: list[dict[str, Any]]) -> str:
    rates = [float(row.get("search_error_rate", 0.0) or 0.0) for row in chunks if row.get("record_count")]
    if len(rates) < 2:
        return "insufficient_data"
    if all(right >= left for left, right in zip(rates, rates[1:])) and rates[-1] > rates[0]:
        return "increasing"
    if rates[-1] > rates[0] and rates[-1] >= max(rates[:-1]):
        return "higher_late"
    if rates[-1] < rates[0]:
        return "lower_late"
    return "mixed"


def _discard_snapshot(row: dict[str, Any]) -> dict[str, Any]:
    record = row.get("record", {})
    metadata = record.get("source_metadata", {}) if isinstance(record, dict) else {}
    if not isinstance(metadata, dict):
        metadata = {}
    notes = record.get("rejection_notes", {}) if isinstance(record, dict) else {}
    if not isinstance(notes, dict):
        notes = {}
    llm_response = metadata.get("llm_response") or metadata.get("small_model_qa_response") or {}
    llm_audit = metadata.get("llm_audit") or {}
    return {
        "line_number": row.get("line_number"),
        "page_id": metadata.get("page_id"),
        "page_title": metadata.get("page_title"),
        "source_url": (
            metadata.get("stream_source_url")
            or metadata.get("source_url")
            or metadata.get("canonical_url")
            or record.get("source_url", "")
        ),
        "route3_slot_id": metadata.get("route3_slot_id"),
        "answer_type_mode": metadata.get("answer_type_mode"),
        "answer_type": record.get("answer_type"),
        "question": record.get("question") or record.get("canonical_question"),
        "answer": record.get("answer"),
        "discard_reason": metadata.get("discard_reason") or notes.get("discard_reason"),
        "llm_response": llm_response,
        "llm_audit_parsed_response": llm_audit.get("parsed_response") if isinstance(llm_audit, dict) else None,
        "llm_audit_text": llm_audit.get("text", "") if isinstance(llm_audit, dict) else "",
        "selected_source_table": metadata.get("selected_source_table"),
        "page_id_list_entry": metadata.get("page_id_list_entry"),
    }


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _rate(numerator: int, denominator: int) -> float:
    return round((numerator / denominator), 4) if denominator else 0.0


if __name__ == "__main__":
    raise SystemExit(main())
