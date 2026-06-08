"""Temporarily apply reviewed Route 3 answer-type redirects.

This helper recreates the manually appended passed_all files documented in
docs/final_qa_rebalance_trace_2026_05_26.md. It is intentionally a repair
script, not part of the public generation pipeline.
"""

from __future__ import annotations

import argparse
import json
import shutil
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ANSWER_TYPES = ("date", "number", "other", "person", "place")


@dataclass(frozen=True)
class AnswerTypeRedirect:
    """One reviewed answer-type redirect from mismatch-only output."""

    source_relative_path: str
    record_id: str
    target_answer_type: str


DEFAULT_REDIRECTS: tuple[AnswerTypeRedirect, ...] = (
    AnswerTypeRedirect("answer_type_mismatch_only/original_other/supposed_person.jsonl", "wikipedia_stream_000051", "Person"),
    AnswerTypeRedirect("answer_type_mismatch_only/original_other/supposed_person.jsonl", "wikipedia_stream_000055", "Person"),
    AnswerTypeRedirect("answer_type_mismatch_only/original_other/supposed_person.jsonl", "wikipedia_stream_000062", "Person"),
    AnswerTypeRedirect("answer_type_mismatch_only/original_other/supposed_person.jsonl", "wikipedia_stream_000068", "Person"),
    AnswerTypeRedirect("answer_type_mismatch_only/original_other/supposed_person.jsonl", "wikipedia_stream_000070", "Person"),
    AnswerTypeRedirect("answer_type_mismatch_only/original_other/supposed_person.jsonl", "wikipedia_stream_000113", "Person"),
    AnswerTypeRedirect("answer_type_mismatch_only/original_person/supposed_place.jsonl", "wikipedia_stream_000009", "Place"),
    AnswerTypeRedirect("answer_type_mismatch_only/original_place/supposed_other.jsonl", "wikipedia_stream_000036", "Place"),
    AnswerTypeRedirect("answer_type_mismatch_only/original_place/supposed_other.jsonl", "wikipedia_stream_000052", "Place"),
)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--split-dir",
        type=Path,
        required=True,
        help="Route 3 final-LLM split directory containing passed_all and answer_type_mismatch_only.",
    )
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory for redirected passed_all JSONLs.")
    parser.add_argument("--summary-output", type=Path, default=None, help="Optional summary JSON path.")
    return parser.parse_args()


def main() -> int:
    """Run the temporary redirect helper."""
    args = parse_args()
    summary = apply_manual_answer_type_redirects(args.split_dir, args.output_dir)
    if args.summary_output:
        args.summary_output.parent.mkdir(parents=True, exist_ok=True)
        args.summary_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


def apply_manual_answer_type_redirects(
    split_dir: Path,
    output_dir: Path,
    redirects: tuple[AnswerTypeRedirect, ...] = DEFAULT_REDIRECTS,
) -> dict[str, Any]:
    """Create redirected passed_all files by appending reviewed mismatch records."""
    split_dir = split_dir.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    copied_counts = _copy_base_passed_all(split_dir, output_dir)
    appended_counts: Counter[str] = Counter()
    applied: list[dict[str, Any]] = []

    for redirect in redirects:
        source_path = split_dir / Path(redirect.source_relative_path)
        record = _load_unique_record(source_path, redirect.record_id)
        target_key = redirect.target_answer_type.lower()
        if target_key not in ANSWER_TYPES:
            raise ValueError(f"Unsupported target answer type: {redirect.target_answer_type}")
        redirected = _build_redirected_record(record, redirect, source_path)
        target_path = output_dir / f"{target_key}.passed_all_appended.jsonl"
        with target_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(redirected, ensure_ascii=False) + "\n")
        appended_counts[redirect.target_answer_type] += 1
        applied.append(
            {
                "id": redirect.record_id,
                "source": str(source_path),
                "original_answer_type": record.get("answer_type"),
                "target_answer_type": redirect.target_answer_type,
                "output": str(target_path),
            }
        )

    output_counts = {
        answer_type.title(): _count_jsonl(output_dir / f"{answer_type}.passed_all_appended.jsonl")
        for answer_type in ANSWER_TYPES
    }
    return {
        "split_dir": str(split_dir),
        "output_dir": str(output_dir),
        "base_copied_counts": copied_counts,
        "appended_counts": dict(appended_counts),
        "output_counts": output_counts,
        "applied_redirects": applied,
    }


def _copy_base_passed_all(split_dir: Path, output_dir: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    source_dir = split_dir / "passed_all"
    for answer_type in ANSWER_TYPES:
        source_path = source_dir / f"{answer_type}.passed_all.jsonl"
        target_path = output_dir / f"{answer_type}.passed_all_appended.jsonl"
        if not source_path.exists():
            raise FileNotFoundError(source_path)
        shutil.copyfile(source_path, target_path)
        counts[answer_type.title()] = _count_jsonl(target_path)
    return counts


def _build_redirected_record(
    record: dict[str, Any],
    redirect: AnswerTypeRedirect,
    source_path: Path,
) -> dict[str, Any]:
    redirected = dict(record)
    original_answer_type = record.get("answer_type")
    redirected["answer_type"] = redirect.target_answer_type
    original_bool_result = record.get("bool_result")
    bool_result = dict(original_bool_result) if isinstance(original_bool_result, dict) else {}
    bool_result["question_matches_answer_type"] = True
    redirected["bool_result"] = bool_result
    redirected["manual_answer_type_move"] = {
        "original_answer_type": original_answer_type,
        "target_answer_type": redirect.target_answer_type,
        "source_path": str(source_path),
        "move_note": _move_note(original_answer_type, redirect.target_answer_type),
        "original_bool_result": original_bool_result,
        "original_question_matches_answer_type_reason": _question_matches_answer_type_reason(record),
    }
    return redirected


def _move_note(original_answer_type: object, target_answer_type: str) -> str:
    if str(original_answer_type) == target_answer_type:
        return (
            f"Manual promotion: original {target_answer_type} accepted as "
            f"{target_answer_type} after review despite judge mismatch flag."
        )
    return f"Manual promotion: original {original_answer_type} judged/reviewed as {target_answer_type}."


def _question_matches_answer_type_reason(record: dict[str, Any]) -> str:
    filter_result = record.get("final_llm_qa_filter")
    if not isinstance(filter_result, dict):
        return ""
    rubric = filter_result.get("rubric_result")
    if not isinstance(rubric, dict):
        return ""
    result = rubric.get("question_matches_answer_type")
    if not isinstance(result, dict):
        return ""
    return str(result.get("reason") or "")


def _load_unique_record(path: Path, record_id: str) -> dict[str, Any]:
    matches = [record for record in _read_jsonl(path) if record.get("id") == record_id]
    if len(matches) != 1:
        raise ValueError(f"Expected one record for {record_id} in {path}, found {len(matches)}")
    return matches[0]


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def _count_jsonl(path: Path) -> int:
    with path.open(encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


if __name__ == "__main__":
    raise SystemExit(main())
