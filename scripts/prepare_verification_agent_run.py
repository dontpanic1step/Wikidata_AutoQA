"""Assemble prefetch and batch-evaluation artifacts for Verification Agent.

All responses for one ``(question_id, query)`` group remain contiguous and are
placed in the same shard, allowing the Verification Agent to share one evidence
pool across models and rounds. The command also writes a lineage sidecar because
the upstream agent intentionally drops adapter-specific metadata.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import convert_batch_evaluation_for_verification_agent as evaluation_adapter


DEFAULT_EXPECTED_QUESTION_COUNT = 428
DEFAULT_EXPECTED_RESPONSE_COUNT = 11_052
SCHEMA_VERSION = 1


def main() -> None:
    args = parse_args()
    report = prepare_verification_run(
        prefetch_inputs=[Path(path) for path in args.prefetch],
        evaluation_inputs=[Path(path) for path in args.evaluation_input],
        output_dir=Path(args.output_dir),
        questions_per_shard=args.questions_per_shard,
        expected_question_count=args.expected_question_count,
        expected_response_count=args.expected_response_count,
        model_fallback=args.model_fallback,
        allow_unconverted=args.allow_unconverted,
        allow_unused_prefetch=args.allow_unused_prefetch,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Merge answer-aware prefetch products with protected batch-evaluation "
            "outputs and create question-aligned Verification Agent shards."
        )
    )
    parser.add_argument(
        "--prefetch",
        action="append",
        required=True,
        help=(
            "Prefetch JSONL or a directory containing "
            "topic_guidance_with_answer.jsonl. Repeat for multiple datasets."
        ),
    )
    parser.add_argument(
        "--evaluation-input",
        action="append",
        required=True,
        help=(
            "Batch-evaluation JSONL, converted model_jsonl, or a directory of "
            "top-level JSONL files. Repeat for multiple runs/models."
        ),
    )
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--questions-per-shard", type=int, default=10)
    parser.add_argument(
        "--expected-question-count",
        type=int,
        default=DEFAULT_EXPECTED_QUESTION_COUNT,
    )
    parser.add_argument(
        "--expected-response-count",
        type=int,
        default=DEFAULT_EXPECTED_RESPONSE_COUNT,
    )
    parser.add_argument("--model-fallback", default=None)
    parser.add_argument(
        "--allow-unconverted",
        action="store_true",
        help="Preserve and report unusable predictions instead of failing.",
    )
    parser.add_argument(
        "--allow-unused-prefetch",
        action="store_true",
        help="Allow prefetch topics that have no evaluation responses.",
    )
    return parser.parse_args()


def prepare_verification_run(
    *,
    prefetch_inputs: list[Path],
    evaluation_inputs: list[Path],
    output_dir: Path,
    questions_per_shard: int = 10,
    expected_question_count: int = DEFAULT_EXPECTED_QUESTION_COUNT,
    expected_response_count: int = DEFAULT_EXPECTED_RESPONSE_COUNT,
    model_fallback: str | None = None,
    allow_unconverted: bool = False,
    allow_unused_prefetch: bool = False,
) -> dict[str, Any]:
    if questions_per_shard <= 0:
        raise ValueError("questions_per_shard must be positive")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"Output directory is not empty: {output_dir}")

    prefetch_rows, prefetch_sources = load_prefetch_rows(prefetch_inputs)
    model_rows, unconverted, evaluation_sources = load_evaluation_rows(
        evaluation_inputs,
        model_fallback=model_fallback,
    )
    if unconverted and not allow_unconverted:
        raise ValueError(
            f"Found {len(unconverted)} unconverted evaluation items; "
            "rerun with --allow-unconverted to preserve them in the report"
        )

    grouped = group_model_rows(model_rows)
    if expected_question_count and len(grouped) != expected_question_count:
        raise ValueError(
            f"Expected {expected_question_count} question groups, found {len(grouped)}"
        )
    if expected_response_count and len(model_rows) != expected_response_count:
        raise ValueError(
            f"Expected {expected_response_count} responses, found {len(model_rows)}"
        )

    prefetch_by_key = index_prefetch(prefetch_rows)
    missing_prefetch = [key for key in grouped if key not in prefetch_by_key]
    if missing_prefetch:
        preview = ", ".join(repr(key) for key in missing_prefetch[:5])
        raise ValueError(
            f"Missing prefetch for {len(missing_prefetch)} question groups: {preview}"
        )
    unused_prefetch = [key for key in prefetch_by_key if key not in grouped]
    if unused_prefetch and not allow_unused_prefetch:
        preview = ", ".join(repr(key) for key in unused_prefetch[:5])
        raise ValueError(
            f"Found {len(unused_prefetch)} unused prefetch topics: {preview}"
        )

    ordered_keys = list(grouped)
    ordered_model_rows: list[dict[str, Any]] = []
    ordered_prefetch_rows: list[dict[str, Any]] = []
    lineage_rows: list[dict[str, Any]] = []
    for key in ordered_keys:
        topic_prefetch = prefetch_by_key[key]
        ordered_prefetch_rows.append(topic_prefetch)
        expected_answer = clean_text(topic_prefetch.get("answer"))
        for sequence_id, source_row in enumerate(grouped[key], start=1):
            reference_answer = clean_text(source_row.get("reference_answer"))
            if reference_answer and expected_answer and reference_answer != expected_answer:
                raise ValueError(
                    f"Reference answer mismatch for {key}: "
                    f"{reference_answer!r} != {expected_answer!r}"
                )
            output_row = {
                "original_index": key[0],
                "query": key[1],
                "model": clean_text(source_row.get("model")),
                "response": clean_multiline(source_row.get("response")),
                "reference_answer": expected_answer or reference_answer,
            }
            ordered_model_rows.append(output_row)
            lineage_rows.append(
                build_lineage_row(
                    key=key,
                    sequence_id=sequence_id,
                    model_row=output_row,
                    source_row=source_row,
                )
            )

    output_dir.mkdir(parents=True, exist_ok=True)
    atomic_write_jsonl(output_dir / "model_answers.jsonl", ordered_model_rows)
    atomic_write_jsonl(output_dir / "topic_grounding.jsonl", ordered_prefetch_rows)
    atomic_write_jsonl(output_dir / "topic_guidance.jsonl", ordered_prefetch_rows)
    atomic_write_jsonl(output_dir / "lineage_crosswalk.jsonl", lineage_rows)
    if unconverted:
        atomic_write_jsonl(output_dir / "unconverted_items.jsonl", unconverted)

    shard_reports = write_shards(
        output_dir=output_dir,
        ordered_keys=ordered_keys,
        grouped=grouped,
        prefetch_by_key=prefetch_by_key,
        lineage_rows=lineage_rows,
        questions_per_shard=questions_per_shard,
    )
    report = {
        "schema_version": SCHEMA_VERSION,
        "output_dir": str(output_dir.resolve()),
        "question_count": len(ordered_keys),
        "response_count": len(ordered_model_rows),
        "prefetch_topic_count": len(prefetch_rows),
        "unused_prefetch_topic_count": len(unused_prefetch),
        "unconverted_item_count": len(unconverted),
        "shard_count": len(shard_reports),
        "questions_per_shard": questions_per_shard,
        "prefetch_sources": prefetch_sources,
        "evaluation_sources": evaluation_sources,
        "main_run": {
            "input_mode": "model_jsonl",
            "input_path": str((output_dir / "model_answers.jsonl").resolve()),
            "start_line": 1,
            "num_lines": len(ordered_model_rows),
            "topic_grounding_path": str((output_dir / "topic_grounding.jsonl").resolve()),
            "topic_guidance_path": str((output_dir / "topic_guidance.jsonl").resolve()),
        },
        "shards": shard_reports,
    }
    atomic_write_json(output_dir / "prepare_verification_agent_run_report.json", report)
    return report


def load_prefetch_rows(paths: Iterable[Path]) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    sources: list[str] = []
    for supplied in paths:
        path = resolve_prefetch_path(supplied)
        sources.append(str(path.resolve()))
        for line_number, row in read_jsonl(path):
            topic_id = clean_text(row.get("topic_id"))
            query = clean_text(row.get("query"))
            evidence_items = row.get("evidence_items")
            if not topic_id or not query:
                raise ValueError(f"Missing topic_id/query at {path}:{line_number}")
            if not isinstance(evidence_items, list) or not evidence_items:
                raise ValueError(f"Missing fixed evidence at {path}:{line_number}")
            seen_snippets: set[str] = set()
            for item in evidence_items:
                if not isinstance(item, dict):
                    raise ValueError(f"Invalid evidence item at {path}:{line_number}")
                snippet_id = clean_text(item.get("snippet_id")).upper()
                content = clean_multiline(item.get("content") or item.get("relevant_text"))
                if not re.fullmatch(r"S\d+", snippet_id) or not content:
                    raise ValueError(f"Invalid fixed evidence at {path}:{line_number}")
                if snippet_id in seen_snippets:
                    raise ValueError(f"Duplicate snippet ID at {path}:{line_number}")
                seen_snippets.add(snippet_id)
            rows.append(row)
    return rows, sources


def resolve_prefetch_path(path: Path) -> Path:
    if path.is_file():
        return path
    if not path.is_dir():
        raise FileNotFoundError(path)
    candidate = path / "topic_guidance_with_answer.jsonl"
    if not candidate.is_file():
        raise FileNotFoundError(
            f"Prefetch directory has no topic_guidance_with_answer.jsonl: {path}"
        )
    return candidate


def load_evaluation_rows(
    inputs: Iterable[Path], *, model_fallback: str | None
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    unconverted: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    for path in discover_evaluation_files(inputs):
        records = evaluation_adapter.load_jsonl(path)
        format_error = evaluation_adapter.batch_evaluation_format_error(records)
        if not format_error:
            converted, rejected = evaluation_adapter.convert_records(
                records,
                source_file=path,
                model_fallback=model_fallback,
            )
            rows.extend(converted)
            unconverted.extend(rejected)
            sources.append(
                {
                    "path": str(path.resolve()),
                    "format": "batch_evaluation_jsonl",
                    "source_record_count": len(records),
                    "response_count": len(converted),
                    "unconverted_item_count": len(rejected),
                }
            )
            continue

        converted_rows = normalize_converted_rows(path, records)
        rows.extend(converted_rows)
        sources.append(
            {
                "path": str(path.resolve()),
                "format": "verification_agent_model_jsonl",
                "source_record_count": len(records),
                "response_count": len(converted_rows),
                "unconverted_item_count": 0,
            }
        )
    if not sources:
        raise ValueError("No evaluation JSONL files were found")
    return rows, unconverted, sources


def discover_evaluation_files(inputs: Iterable[Path]) -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()
    for supplied in inputs:
        candidates: Iterable[Path]
        if supplied.is_file():
            candidates = [supplied]
        elif supplied.is_dir():
            candidates = sorted(supplied.glob("*.jsonl"))
        else:
            raise FileNotFoundError(supplied)
        for path in candidates:
            resolved = path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                files.append(path)
    return files


def normalize_converted_rows(
    path: Path, records: list[tuple[int, dict[str, Any]]]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, raw in records:
        topic_id = clean_text(raw.get("original_index") or raw.get("id"))
        query = clean_text(raw.get("query") or raw.get("original_question"))
        model = clean_text(raw.get("model") or raw.get("actual_model_used"))
        response = clean_multiline(
            raw.get("response") or raw.get("model_answer") or raw.get("answer")
        )
        if not topic_id or not query or not model or not response:
            raise ValueError(
                f"Nonconforming evaluation JSONL at {path}:{line_number}; "
                "it is neither a current batch output nor model_jsonl"
            )
        rows.append(
            {
                "original_index": topic_id,
                "query": query,
                "model": model,
                "response": response,
                "reference_answer": raw.get("reference_answer"),
                "verification_agent_adapter": raw.get("verification_agent_adapter")
                or {
                    "schema_version": SCHEMA_VERSION,
                    "source_file": str(path.resolve()),
                    "source_line_number": line_number,
                    "prediction_index": None,
                    "prediction_count": 1,
                },
            }
        )
    return rows


def group_model_rows(
    rows: Iterable[dict[str, Any]],
) -> dict[tuple[str, str], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    id_to_query: dict[str, str] = {}
    query_to_id: dict[str, str] = {}
    for row in rows:
        topic_id = clean_text(row.get("original_index"))
        query = clean_text(row.get("query"))
        if not topic_id or not query:
            raise ValueError("Model row is missing original_index/query")
        if topic_id in id_to_query and id_to_query[topic_id] != query:
            raise ValueError(f"Question ID maps to multiple queries: {topic_id}")
        if query in query_to_id and query_to_id[query] != topic_id:
            raise ValueError(f"Query maps to multiple question IDs: {query}")
        id_to_query[topic_id] = query
        query_to_id[query] = topic_id
        grouped.setdefault((topic_id, query), []).append(row)
    return grouped


def index_prefetch(rows: Iterable[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    indexed: dict[tuple[str, str], dict[str, Any]] = {}
    id_to_query: dict[str, str] = {}
    query_to_id: dict[str, str] = {}
    for row in rows:
        topic_id = clean_text(row.get("topic_id"))
        query = clean_text(row.get("query"))
        key = (topic_id, query)
        if topic_id in id_to_query and id_to_query[topic_id] != query:
            raise ValueError(f"Prefetch topic ID maps to multiple queries: {topic_id}")
        if query in query_to_id and query_to_id[query] != topic_id:
            raise ValueError(f"Prefetch query maps to multiple topic IDs: {query}")
        if key in indexed:
            if canonical_json(indexed[key]) != canonical_json(row):
                raise ValueError(f"Conflicting duplicate prefetch topic: {key}")
            continue
        id_to_query[topic_id] = query
        query_to_id[query] = topic_id
        indexed[key] = row
    return indexed


def build_lineage_row(
    *,
    key: tuple[str, str],
    sequence_id: int,
    model_row: dict[str, Any],
    source_row: dict[str, Any],
) -> dict[str, Any]:
    adapter = source_row.get("verification_agent_adapter")
    return {
        "original_index": key[0],
        "query": key[1],
        "model_sequence_id": sequence_id,
        "model": model_row["model"],
        "response_sha256": hashlib.sha256(
            model_row["response"].encode("utf-8")
        ).hexdigest(),
        "verification_agent_adapter": adapter if isinstance(adapter, dict) else {},
    }


def write_shards(
    *,
    output_dir: Path,
    ordered_keys: list[tuple[str, str]],
    grouped: dict[tuple[str, str], list[dict[str, Any]]],
    prefetch_by_key: dict[tuple[str, str], dict[str, Any]],
    lineage_rows: list[dict[str, Any]],
    questions_per_shard: int,
) -> list[dict[str, Any]]:
    lineage_by_key: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in lineage_rows:
        key = (clean_text(row.get("original_index")), clean_text(row.get("query")))
        lineage_by_key.setdefault(key, []).append(row)

    reports: list[dict[str, Any]] = []
    shards_root = output_dir / "shards"
    for start in range(0, len(ordered_keys), questions_per_shard):
        keys = ordered_keys[start : start + questions_per_shard]
        shard_number = len(reports) + 1
        shard_dir = shards_root / f"shard_{shard_number:03d}"
        model_rows: list[dict[str, Any]] = []
        shard_lineage: list[dict[str, Any]] = []
        for key in keys:
            for source_row in grouped[key]:
                model_rows.append(
                    {
                        "original_index": key[0],
                        "query": key[1],
                        "model": clean_text(source_row.get("model")),
                        "response": clean_multiline(source_row.get("response")),
                        "reference_answer": clean_text(
                            prefetch_by_key[key].get("answer")
                            or source_row.get("reference_answer")
                        ),
                    }
                )
            shard_lineage.extend(lineage_by_key[key])
        prefetch_rows = [prefetch_by_key[key] for key in keys]
        atomic_write_jsonl(shard_dir / "model_answers.jsonl", model_rows)
        atomic_write_jsonl(shard_dir / "topic_grounding.jsonl", prefetch_rows)
        atomic_write_jsonl(shard_dir / "topic_guidance.jsonl", prefetch_rows)
        atomic_write_jsonl(shard_dir / "lineage_crosswalk.jsonl", shard_lineage)
        shard_report = {
            "shard": shard_number,
            "directory": str(shard_dir.resolve()),
            "question_count": len(keys),
            "response_count": len(model_rows),
            "first_question_id": keys[0][0],
            "last_question_id": keys[-1][0],
            "main_run": {
                "input_path": str((shard_dir / "model_answers.jsonl").resolve()),
                "start_line": 1,
                "num_lines": len(model_rows),
                "topic_grounding_path": str(
                    (shard_dir / "topic_grounding.jsonl").resolve()
                ),
                "topic_guidance_path": str(
                    (shard_dir / "topic_guidance.jsonl").resolve()
                ),
            },
        }
        atomic_write_json(shard_dir / "shard_manifest.json", shard_report)
        reports.append(shard_report)
    return reports


def read_jsonl(path: Path) -> list[tuple[int, dict[str, Any]]]:
    rows: list[tuple[int, dict[str, Any]]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"Expected JSON object at {path}:{line_number}")
            rows.append((line_number, value))
    return rows


def clean_text(value: Any) -> str:
    return " ".join(str(value or "").split()).strip()


def clean_multiline(value: Any) -> str:
    return str(value or "").replace("\r\n", "\n").strip()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def atomic_write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    atomic_write_text(
        path,
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
    )


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
            temp_name = handle.name
        os.replace(temp_name, path)
    finally:
        if temp_name:
            Path(temp_name).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
