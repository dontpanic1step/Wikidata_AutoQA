"""Temporarily filter Route 3 passed_all JSONL records for repair batches.

This script is intentionally a one-off repair helper. It reads existing passed_all
records and writes new filtered/rejected JSONL files; it does not modify inputs.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.io import write_jsonl
from wikidata_simpleqa.route3_quality_rules import (
    award_year_without_month_question_reason,
    external_links_table_filter_reason,
)

TMP_FILTER_REJECTION_REASON = "tmp_route3_passed_all_filter_rejected"


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", type=Path, required=True, help="passed_all JSONL input.")
    parser.add_argument("--output", type=Path, required=True, help="Filtered passed_all JSONL output.")
    parser.add_argument("--rejected-output", type=Path, required=True, help="Rejected JSONL output.")
    parser.add_argument("--summary-output", type=Path, default=None, help="Optional JSON summary output.")
    return parser.parse_args()


def main() -> int:
    """Run the temporary passed_all filter."""
    args = parse_args()
    records = [record for path in args.input for record in _read_jsonl(path)]
    kept: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for record in records:
        reasons = route3_tmp_filter_rejection_reasons(record)
        if not reasons:
            kept.append(record)
            continue
        rejected_record = dict(record)
        rejected_record["rejection_reason"] = TMP_FILTER_REJECTION_REASON
        rejected_record["rejection_rule"] = reasons[0]
        rejected_record["tmp_filter_rejection_reasons"] = reasons
        rejected.append(rejected_record)

    write_jsonl(args.output, kept)
    write_jsonl(args.rejected_output, rejected)
    summary = {
        "input_files": [str(path) for path in args.input],
        "input_count": len(records),
        "kept_count": len(kept),
        "rejected_count": len(rejected),
        "rejection_reason_counts": dict(Counter(reason for record in rejected for reason in record["tmp_filter_rejection_reasons"])),
        "output": str(args.output),
        "rejected_output": str(args.rejected_output),
    }
    if args.summary_output:
        args.summary_output.parent.mkdir(parents=True, exist_ok=True)
        args.summary_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


def route3_tmp_filter_rejection_reasons(record: dict[str, Any]) -> list[str]:
    """Return temporary repair-filter rejection labels for one passed_all record."""
    reasons: list[str] = []
    external_links_reason = _external_links_source_table_reason(record)
    if external_links_reason:
        reasons.append(external_links_reason)
    award_year_reason = award_year_without_month_question_reason(record.get("question") or record.get("rewritten_question"))
    if award_year_reason:
        reasons.append(award_year_reason)
    return reasons


def _external_links_source_table_reason(record: dict[str, Any]) -> str:
    metadata = record.get("source_metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
    for table in _candidate_source_tables(record, metadata):
        reason = external_links_table_filter_reason(table.get("section_heading"))
        if reason:
            return reason
    return ""


def _candidate_source_tables(record: dict[str, Any], metadata: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for value in (metadata.get("selected_source_table"), record.get("selected_source_table")):
        if isinstance(value, dict):
            candidates.append(value)
    selected_index = _selected_source_table_index(metadata)
    if selected_index is not None:
        for table in metadata.get("parsed_tables", []):
            if isinstance(table, dict) and _safe_int(table.get("table_index")) == selected_index:
                candidates.append(table)
        for row in metadata.get("table_selection", []):
            if isinstance(row, dict) and _safe_int(row.get("table_index")) == selected_index:
                candidates.append(row)
    return candidates


def _selected_source_table_index(metadata: dict[str, Any]) -> int | None:
    for source in (
        metadata.get("llm_response"),
        metadata.get("small_model_response"),
        metadata.get("small_model_generation_response"),
    ):
        if isinstance(source, dict):
            value = _safe_int(source.get("source_table"))
            if value is not None:
                return value
    selected = metadata.get("selected_source_table")
    if isinstance(selected, dict):
        return _safe_int(selected.get("table_index"))
    anchors = metadata.get("subject_anchors")
    if isinstance(anchors, dict):
        table_scopes = anchors.get("table_scopes")
        if isinstance(table_scopes, list):
            for scope in table_scopes:
                if isinstance(scope, dict):
                    value = _safe_int(scope.get("table_index"))
                    if value is not None:
                        return value
    return None


def _safe_int(value: object) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


if __name__ == "__main__":
    raise SystemExit(main())
