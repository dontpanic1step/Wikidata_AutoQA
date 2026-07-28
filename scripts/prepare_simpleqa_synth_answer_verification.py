"""Prepare SimpleQA Synth CSV answers for gold-free Verification Agent review.

Each CSV answer becomes the response of one synthetic model named
``simpleqa_synth``. No reference answer is written. The corresponding offline
prefetch evidence is sanitized so answer-assessment fields and answer-directed
guidance cannot act as an implicit gold label during verification.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Iterable


DEFAULT_CSV = Path(
    "outputs/evaluation_benchmarks/"
    "wikipedia_stream_recipe_integrated_2026_07_28/simpleqa_synth.csv"
)
DEFAULT_EXPECTED_COUNT = 328
DEFAULT_MODEL_NAME = "simpleqa_synth"
SCHEMA_VERSION = 1


def main() -> None:
    args = parse_args()
    report = prepare_answer_verification(
        csv_path=Path(args.csv),
        prefetch_input=Path(args.prefetch),
        output_dir=Path(args.output_dir),
        model_name=args.model_name,
        expected_count=args.expected_count,
        questions_per_shard=args.questions_per_shard,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Treat all 328 SimpleQA Synth CSV answers as one model's gold-free "
            "responses and build a Verification Agent run bundle."
        )
    )
    parser.add_argument("--csv", default=str(DEFAULT_CSV))
    parser.add_argument(
        "--prefetch",
        required=True,
        help=(
            "First-script output directory or its "
            "topic_guidance_with_answer.jsonl file."
        ),
    )
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--model-name", default=DEFAULT_MODEL_NAME)
    parser.add_argument("--expected-count", type=int, default=DEFAULT_EXPECTED_COUNT)
    parser.add_argument("--questions-per-shard", type=int, default=10)
    return parser.parse_args()


def prepare_answer_verification(
    *,
    csv_path: Path,
    prefetch_input: Path,
    output_dir: Path,
    model_name: str = DEFAULT_MODEL_NAME,
    expected_count: int = DEFAULT_EXPECTED_COUNT,
    questions_per_shard: int = 10,
) -> dict[str, Any]:
    model_name = clean_text(model_name)
    if not model_name:
        raise ValueError("model_name must not be empty")
    if questions_per_shard <= 0:
        raise ValueError("questions_per_shard must be positive")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"Output directory is not empty: {output_dir}")

    csv_rows = load_csv_answers(csv_path)
    if expected_count and len(csv_rows) != expected_count:
        raise ValueError(
            f"Expected {expected_count} SimpleQA Synth rows, found {len(csv_rows)}"
        )
    prefetch_path = resolve_prefetch_path(prefetch_input)
    prefetch_by_key = load_sanitized_prefetch(prefetch_path)

    csv_keys = [(row["id"], row["question"]) for row in csv_rows]
    missing = [key for key in csv_keys if key not in prefetch_by_key]
    if missing:
        preview = ", ".join(repr(key) for key in missing[:5])
        raise ValueError(f"Missing prefetch for {len(missing)} CSV rows: {preview}")
    unused = [key for key in prefetch_by_key if key not in set(csv_keys)]
    if unused:
        preview = ", ".join(repr(key) for key in unused[:5])
        raise ValueError(f"Found {len(unused)} unused prefetch topics: {preview}")

    model_rows: list[dict[str, Any]] = []
    grounding_rows: list[dict[str, Any]] = []
    lineage_rows: list[dict[str, Any]] = []
    for row in csv_rows:
        key = (row["id"], row["question"])
        response = row["response"]
        model_rows.append(
            {
                "original_index": row["id"],
                "query": row["question"],
                "model": model_name,
                "response": response,
            }
        )
        grounding_rows.append(prefetch_by_key[key])
        lineage_rows.append(
            {
                "original_index": row["id"],
                "query": row["question"],
                "model_sequence_id": 1,
                "model": model_name,
                "response_sha256": hashlib.sha256(response.encode("utf-8")).hexdigest(),
                "source_csv": str(csv_path.resolve()),
                "source_line_number": row["source_line_number"],
                "source_column": "answer",
            }
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    atomic_write_jsonl(output_dir / "model_answers.jsonl", model_rows)
    atomic_write_jsonl(output_dir / "topic_grounding.jsonl", grounding_rows)
    atomic_write_jsonl(output_dir / "topic_guidance.jsonl", grounding_rows)
    atomic_write_jsonl(output_dir / "lineage_crosswalk.jsonl", lineage_rows)
    shard_reports = write_shards(
        output_dir=output_dir,
        model_rows=model_rows,
        grounding_rows=grounding_rows,
        lineage_rows=lineage_rows,
        questions_per_shard=questions_per_shard,
    )

    report = {
        "schema_version": SCHEMA_VERSION,
        "output_dir": str(output_dir.resolve()),
        "source_csv": str(csv_path.resolve()),
        "source_prefetch": str(prefetch_path.resolve()),
        "question_count": len(model_rows),
        "response_count": len(model_rows),
        "model": model_name,
        "has_reference_answers": False,
        "prefetch_sanitization": {
            "removed_fields": ["answer", "answer_assessment", "topic_brief"],
            "replaced_topic_guidance": True,
            "fixed_evidence_preserved": True,
        },
        "shard_count": len(shard_reports),
        "questions_per_shard": questions_per_shard,
        "main_run": {
            "input_mode": "model_jsonl",
            "input_path": str((output_dir / "model_answers.jsonl").resolve()),
            "start_line": 1,
            "num_lines": len(model_rows),
            "topic_grounding_path": str((output_dir / "topic_grounding.jsonl").resolve()),
            "topic_guidance_path": str((output_dir / "topic_guidance.jsonl").resolve()),
        },
        "shards": shard_reports,
    }
    atomic_write_json(
        output_dir / "prepare_simpleqa_synth_answer_verification_report.json",
        report,
    )
    return report


def load_csv_answers(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    rows: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_questions: set[str] = set()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for line_number, raw in enumerate(csv.DictReader(handle), start=2):
            topic_id = clean_text(raw.get("id"))
            question = clean_text(raw.get("problem"))
            response = clean_multiline(raw.get("answer"))
            if not topic_id or not question or not response:
                raise ValueError(f"Incomplete CSV row at line {line_number}")
            if topic_id in seen_ids:
                raise ValueError(f"Duplicate CSV ID: {topic_id}")
            if question in seen_questions:
                raise ValueError(f"Duplicate CSV question: {question}")
            seen_ids.add(topic_id)
            seen_questions.add(question)
            rows.append(
                {
                    "id": topic_id,
                    "question": question,
                    "response": response,
                    "source_line_number": line_number,
                }
            )
    return rows


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


def load_sanitized_prefetch(path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    indexed: dict[tuple[str, str], dict[str, Any]] = {}
    id_to_query: dict[str, str] = {}
    query_to_id: dict[str, str] = {}
    for line_number, raw in read_jsonl(path):
        topic_id = clean_text(raw.get("topic_id"))
        query = clean_text(raw.get("query"))
        if not topic_id or not query:
            raise ValueError(f"Missing topic_id/query at {path}:{line_number}")
        if topic_id in id_to_query and id_to_query[topic_id] != query:
            raise ValueError(f"Prefetch topic ID maps to multiple queries: {topic_id}")
        if query in query_to_id and query_to_id[query] != topic_id:
            raise ValueError(f"Prefetch query maps to multiple IDs: {query}")

        evidence_items = sanitize_evidence_items(
            raw.get("evidence_items"),
            path=path,
            line_number=line_number,
        )
        snippet_ids = [item["snippet_id"] for item in evidence_items]
        references = ", ".join(f"[{snippet_id}]" for snippet_id in snippet_ids)
        sanitized = {
            "topic_id": topic_id,
            "query": query,
            "topic_guidance": (
                f"Use the fixed source evidence {references} to check the factual "
                "claims in the response. Do not treat the response as a reference answer."
            ),
            "evidence_items": evidence_items,
        }
        key = (topic_id, query)
        if key in indexed:
            if canonical_json(indexed[key]) != canonical_json(sanitized):
                raise ValueError(f"Conflicting duplicate prefetch topic: {key}")
            continue
        indexed[key] = sanitized
        id_to_query[topic_id] = query
        query_to_id[query] = topic_id
    return indexed


def sanitize_evidence_items(
    value: Any,
    *,
    path: Path,
    line_number: int,
) -> list[dict[str, str]]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"Missing fixed evidence at {path}:{line_number}")
    rows: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            raise ValueError(f"Invalid evidence item at {path}:{line_number}")
        snippet_id = clean_text(item.get("snippet_id")).upper()
        content = clean_multiline(item.get("content") or item.get("relevant_text"))
        if not re.fullmatch(r"S\d+", snippet_id) or not content:
            raise ValueError(f"Invalid fixed evidence at {path}:{line_number}")
        if snippet_id in seen_ids:
            raise ValueError(f"Duplicate snippet ID at {path}:{line_number}: {snippet_id}")
        seen_ids.add(snippet_id)
        rows.append(
            {
                "snippet_id": snippet_id,
                "source_url": clean_text(item.get("source_url") or item.get("url")),
                "source_title": clean_text(
                    item.get("source_title") or item.get("title")
                ),
                "content": content,
            }
        )
    return rows


def write_shards(
    *,
    output_dir: Path,
    model_rows: list[dict[str, Any]],
    grounding_rows: list[dict[str, Any]],
    lineage_rows: list[dict[str, Any]],
    questions_per_shard: int,
) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    shards_root = output_dir / "shards"
    for start in range(0, len(model_rows), questions_per_shard):
        stop = start + questions_per_shard
        shard_number = len(reports) + 1
        shard_dir = shards_root / f"shard_{shard_number:03d}"
        shard_models = model_rows[start:stop]
        shard_grounding = grounding_rows[start:stop]
        shard_lineage = lineage_rows[start:stop]
        atomic_write_jsonl(shard_dir / "model_answers.jsonl", shard_models)
        atomic_write_jsonl(shard_dir / "topic_grounding.jsonl", shard_grounding)
        atomic_write_jsonl(shard_dir / "topic_guidance.jsonl", shard_grounding)
        atomic_write_jsonl(shard_dir / "lineage_crosswalk.jsonl", shard_lineage)
        report = {
            "shard": shard_number,
            "directory": str(shard_dir.resolve()),
            "question_count": len(shard_models),
            "response_count": len(shard_models),
            "first_question_id": shard_models[0]["original_index"],
            "last_question_id": shard_models[-1]["original_index"],
            "main_run": {
                "input_path": str((shard_dir / "model_answers.jsonl").resolve()),
                "start_line": 1,
                "num_lines": len(shard_models),
                "topic_grounding_path": str(
                    (shard_dir / "topic_grounding.jsonl").resolve()
                ),
                "topic_guidance_path": str(
                    (shard_dir / "topic_guidance.jsonl").resolve()
                ),
            },
        }
        atomic_write_json(shard_dir / "shard_manifest.json", report)
        reports.append(report)
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
