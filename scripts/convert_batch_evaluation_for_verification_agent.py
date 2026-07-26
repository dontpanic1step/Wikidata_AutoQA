"""Batch-convert evaluation JSONL files for Project Verification Agent.

The input directory is scanned non-recursively. Every JSONL file matching the
current batch prediction/judging output schema is converted independently into
a same-named model_jsonl file under a new output directory.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any


ADAPTER_SCHEMA_VERSION = 1
SUMMARY_FILENAME = "conversion_summary.json"
SAFE_MODEL_SUFFIX = re.compile(
    r"(?:^|\.)(?P<model>[0-9A-Za-z_-]+__[0-9A-Za-z._-]+)$"
)


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)

    validate_directories(input_dir=input_dir, output_dir=output_dir)
    source_files = sorted(path for path in input_dir.glob("*.jsonl") if path.is_file())
    if not source_files:
        raise SystemExit(f"No top-level JSONL files found in input directory: {input_dir}")

    prepared: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    unconverted_items: list[dict[str, Any]] = []
    conforming_file_count = 0

    for source_file in source_files:
        try:
            records = load_jsonl(source_file)
        except ValueError as exc:
            skipped.append(
                {
                    "source_file": str(source_file.resolve()),
                    "reason": str(exc),
                }
            )
            continue

        format_error = batch_evaluation_format_error(records)
        if format_error:
            skipped.append(
                {
                    "source_file": str(source_file.resolve()),
                    "reason": format_error,
                }
            )
            continue

        conforming_file_count += 1
        output_rows, file_unconverted = convert_records(
            records,
            source_file=source_file,
            model_fallback=args.model_fallback,
        )
        unconverted_items.extend(file_unconverted)
        output_rows, question_group_count = cluster_rows_by_question(output_rows)
        if not output_rows:
            skipped.append(
                {
                    "source_file": str(source_file.resolve()),
                    "reason": "conforming file has no agent-compatible response rows",
                }
            )
            continue

        prepared.append(
            {
                "source_file": source_file,
                "output_file": output_dir / source_file.name,
                "records": output_rows,
                "source_record_count": len(records),
                "question_group_count": question_group_count,
                "unconverted_item_count": len(file_unconverted),
            }
        )

    if conforming_file_count == 0:
        skipped_details = "\n".join(
            f"- {row['source_file']}: {row['reason']}" for row in skipped
        )
        raise SystemExit(
            "No files matched the current batch-evaluation output schema; "
            f"no output directory was created.\n{skipped_details}"
        )

    output_dir.mkdir(parents=True, exist_ok=False)
    converted_summary: list[dict[str, Any]] = []
    for item in prepared:
        atomic_write_jsonl(item["output_file"], item["records"])
        converted_summary.append(
            {
                "source_file": str(item["source_file"].resolve()),
                "output_file": str(item["output_file"].resolve()),
                "source_records": item["source_record_count"],
                "response_rows": len(item["records"]),
                "question_groups": item["question_group_count"],
                "unconverted_items": item["unconverted_item_count"],
            }
        )

    summary = {
        "schema_version": ADAPTER_SCHEMA_VERSION,
        "input_dir": str(input_dir.resolve()),
        "output_dir": str(output_dir.resolve()),
        "conforming_file_count": conforming_file_count,
        "converted_file_count": len(converted_summary),
        "skipped_file_count": len(skipped),
        "unconverted_item_count": len(unconverted_items),
        "converted_files": converted_summary,
        "skipped_files": skipped,
        "unconverted_items": unconverted_items,
    }
    atomic_write_json(output_dir / SUMMARY_FILENAME, summary)
    print(
        json.dumps(
            {
                "output_dir": summary["output_dir"],
                "conforming_file_count": summary["conforming_file_count"],
                "converted_file_count": summary["converted_file_count"],
                "skipped_file_count": summary["skipped_file_count"],
                "unconverted_item_count": summary["unconverted_item_count"],
            }
        )
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Non-recursively convert every top-level JSONL file matching the current "
            "batch prediction/judging output schema into a new directory of Project "
            "Verification Agent model_jsonl files."
        )
    )
    parser.add_argument("input_dir", help="Directory containing batch-evaluation JSONL files.")
    parser.add_argument("output_dir", help="New directory for same-named converted JSONL files.")
    parser.add_argument(
        "--model-fallback",
        default=None,
        help=(
            "Exact model id used only when prediction data, its raw response, the "
            "source record, and the current batch filename do not identify a model."
        ),
    )
    return parser.parse_args()


def validate_directories(*, input_dir: Path, output_dir: Path) -> None:
    if not input_dir.exists():
        raise SystemExit(f"Input directory does not exist: {input_dir}")
    if not input_dir.is_dir():
        raise SystemExit(f"Input path is not a directory: {input_dir}")
    if output_dir.exists():
        raise SystemExit(f"Output directory must be new and not already exist: {output_dir}")
    if input_dir.resolve() == output_dir.resolve():
        raise SystemExit("Input and output directories must differ")


def load_jsonl(path: Path) -> list[tuple[int, dict[str, Any]]]:
    records: list[tuple[int, dict[str, Any]]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                value = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON at line {line_number}: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"line {line_number} is not a JSON object")
            records.append((line_number, value))
    return records


def batch_evaluation_format_error(
    records: list[tuple[int, dict[str, Any]]],
) -> str:
    """Return an explanation when a file is not a current batch-output JSONL."""
    if not records:
        return "empty JSONL file"
    for line_number, record in records:
        required = ("id", "question", "answer", "predictions")
        missing = [key for key in required if key not in record]
        if missing:
            return f"line {line_number} is missing batch fields: {', '.join(missing)}"
        predictions = record.get("predictions")
        if not isinstance(predictions, list):
            return f"line {line_number} predictions is not a list"
        if any(not isinstance(prediction, dict) for prediction in predictions):
            return f"line {line_number} predictions contains a non-object item"
    return ""


def convert_records(
    records: list[tuple[int, dict[str, Any]]],
    *,
    source_file: Path,
    model_fallback: str | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    output_rows: list[dict[str, Any]] = []
    unconverted_items: list[dict[str, Any]] = []
    for source_line_number, record in records:
        rows, rejected = convert_record(
            record,
            source_file=source_file,
            source_line_number=source_line_number,
            model_fallback=model_fallback,
        )
        output_rows.extend(rows)
        unconverted_items.extend(rejected)
    return output_rows, unconverted_items


def convert_record(
    record: dict[str, Any],
    *,
    source_file: Path,
    source_line_number: int,
    model_fallback: str | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    source_id = stable_question_id(record)
    question = record.get("question")
    predictions = record.get("predictions")
    if not isinstance(predictions, list):
        predictions = []

    batch_record = {key: value for key, value in record.items() if key != "predictions"}
    prediction_count = len(predictions)
    rows: list[dict[str, Any]] = []
    unconverted_items: list[dict[str, Any]] = []

    record_reason = ""
    if source_id is None or not stringify(source_id):
        record_reason = "missing stable question id"
    elif not stringify(question):
        record_reason = "missing question"

    if not predictions:
        unconverted_items.append(
            preserved_unconverted_item(
                source_file=source_file,
                source_line_number=source_line_number,
                prediction_index=None,
                prediction_count=0,
                batch_record=batch_record,
                batch_prediction=None,
                reason=record_reason or "predictions is empty",
            )
        )
        return rows, unconverted_items

    for prediction_index, prediction in enumerate(predictions):
        reason = record_reason
        response = prediction_answer(prediction)
        model = ""
        if not reason and not stringify(response):
            reason = "prediction has an empty answer"
        if not reason:
            model = resolve_model(
                prediction,
                record=record,
                source_file=source_file,
                model_fallback=model_fallback,
            )
            if not model:
                reason = "prediction has no resolvable model id"

        if reason:
            unconverted_items.append(
                preserved_unconverted_item(
                    source_file=source_file,
                    source_line_number=source_line_number,
                    prediction_index=prediction_index,
                    prediction_count=prediction_count,
                    batch_record=batch_record,
                    batch_prediction=prediction,
                    reason=reason,
                )
            )
            continue

        rows.append(
            {
                "original_index": source_id,
                "query": question,
                "model": model,
                "response": response,
                "reference_answer": record.get("answer"),
                "verification_agent_adapter": {
                    "schema_version": ADAPTER_SCHEMA_VERSION,
                    "source_file": str(source_file.resolve()),
                    "source_line_number": source_line_number,
                    "prediction_index": prediction_index,
                    "prediction_count": prediction_count,
                    "batch_record": batch_record,
                    "batch_prediction": prediction,
                },
            }
        )
    return rows, unconverted_items


def preserved_unconverted_item(
    *,
    source_file: Path,
    source_line_number: int,
    prediction_index: int | None,
    prediction_count: int,
    batch_record: dict[str, Any],
    batch_prediction: dict[str, Any] | None,
    reason: str,
) -> dict[str, Any]:
    return {
        "source_file": str(source_file.resolve()),
        "source_line_number": source_line_number,
        "prediction_index": prediction_index,
        "prediction_count": prediction_count,
        "reason": reason,
        "batch_record": batch_record,
        "batch_prediction": batch_prediction,
    }


def cluster_rows_by_question(
    rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], int]:
    """Keep every model/round response for one source file's question contiguous."""
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        key = (
            stringify(row.get("original_index")),
            stringify(row.get("query")),
        )
        groups.setdefault(key, []).append(row)
    clustered = [row for group_rows in groups.values() for row in group_rows]
    return clustered, len(groups)


def prediction_answer(prediction: dict[str, Any]) -> Any:
    value = prediction.get("answer")
    if value is None:
        value = prediction.get("predicted_answer")
    return value


def stable_question_id(record: dict[str, Any]) -> Any:
    """Prefer dataset-level identity over response/model/repeat-specific ids."""
    for key in ("original_index", "simpleqa_verified_id", "original_id", "id"):
        value = record.get(key)
        if value is not None and stringify(value):
            return value
    return None


def resolve_model(
    prediction: dict[str, Any],
    *,
    record: dict[str, Any],
    source_file: Path,
    model_fallback: str | None,
) -> str:
    candidates = [
        prediction.get("model"),
        nested_value(prediction, "raw_response", "model"),
        record.get("model"),
        infer_model_from_current_output_name(source_file),
        model_fallback,
    ]
    for candidate in candidates:
        value = stringify(candidate)
        if value:
            return value
    return ""


def nested_value(value: dict[str, Any], outer_key: str, inner_key: str) -> Any:
    nested = value.get(outer_key)
    if not isinstance(nested, dict):
        return None
    return nested.get(inner_key)


def infer_model_from_current_output_name(path: Path) -> str:
    name = path.name
    if name.lower().endswith(".jsonl"):
        name = name[:-6]
    if name.lower().endswith(".judged"):
        name = name[:-7]
    match = SAFE_MODEL_SUFFIX.search(name)
    if match is None:
        return ""
    return match.group("model").replace("__", "/")


def atomic_write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    atomic_write_text(
        path,
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
    )


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            tmp_name = handle.name
            handle.write(content)
        os.replace(tmp_name, path)
        tmp_name = None
    finally:
        if tmp_name is not None:
            Path(tmp_name).unlink(missing_ok=True)


def stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


if __name__ == "__main__":
    main()
