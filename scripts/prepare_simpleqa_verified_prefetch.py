"""Convert the selected SimpleQA Verified CSV into prefetch topic JSONL."""

from __future__ import annotations

import argparse
import csv
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable


DEFAULT_INPUT = Path(
    "outputs/evaluation_benchmarks/simpleqa_verified/simpleqa_verified_100.csv"
)
DEFAULT_EXPECTED_COUNT = 100
SCHEMA_VERSION = 1


def main() -> None:
    args = parse_args()
    report = prepare_prefetch_topics(
        input_csv=Path(args.input_csv),
        output_dir=Path(args.output_dir),
        expected_count=args.expected_count,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare the 100-question SimpleQA Verified CSV for the answer-aware "
            "Verification Agent prefetch entry point."
        )
    )
    parser.add_argument("--input-csv", default=str(DEFAULT_INPUT))
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--expected-count", type=int, default=DEFAULT_EXPECTED_COUNT)
    return parser.parse_args()


def prepare_prefetch_topics(
    *, input_csv: Path, output_dir: Path, expected_count: int = DEFAULT_EXPECTED_COUNT
) -> dict[str, Any]:
    if not input_csv.is_file():
        raise FileNotFoundError(input_csv)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"Output directory is not empty: {output_dir}")

    topics: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_questions: set[str] = set()
    repaired_url_count = 0
    with input_csv.open("r", encoding="utf-8-sig", newline="") as handle:
        for line_number, row in enumerate(csv.DictReader(handle), start=2):
            topic_id = clean_text(row.get("original_index") or row.get("id"))
            question = clean_text(row.get("problem") or row.get("question"))
            answer = clean_text(row.get("answer"))
            urls, repair_count = parse_source_urls(row.get("urls"))
            repaired_url_count += repair_count
            if not topic_id or not question or not answer:
                raise ValueError(f"Incomplete SimpleQA Verified row at line {line_number}")
            if not urls:
                raise ValueError(f"No usable URLs at line {line_number}")
            if topic_id in seen_ids:
                raise ValueError(f"Duplicate topic ID: {topic_id}")
            if question in seen_questions:
                raise ValueError(f"Duplicate question text: {question}")
            seen_ids.add(topic_id)
            seen_questions.add(question)
            topics.append(
                {
                    "id": topic_id,
                    "question": question,
                    "answer": answer,
                    "url": urls,
                }
            )

    if expected_count and len(topics) != expected_count:
        raise ValueError(
            f"Expected {expected_count} SimpleQA Verified rows, found {len(topics)}"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    topics_path = output_dir / "prefetch_topics.jsonl"
    report_path = output_dir / "prepare_simpleqa_verified_prefetch_report.json"
    report = {
        "schema_version": SCHEMA_VERSION,
        "input_csv": str(input_csv.resolve()),
        "topic_count": len(topics),
        "url_count": sum(len(row["url"]) for row in topics),
        "repaired_unmatched_trailing_parenthesis_count": repaired_url_count,
        "prefetch_input_path": str(topics_path.resolve()),
        "verification_prefetch_fields": {
            "topic_id": "id",
            "query": "question",
            "answer": "answer",
            "trusted_urls": "url",
        },
    }
    atomic_write_jsonl(topics_path, topics)
    atomic_write_json(report_path, report)
    return report


def parse_source_urls(value: Any) -> tuple[list[str], int]:
    text = clean_text(value)
    if not text:
        return [], 0
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = [part.strip() for part in text.split(",")]
    if isinstance(parsed, str):
        parsed = [parsed]
    if not isinstance(parsed, list):
        raise ValueError("URLs must be a JSON list or comma-separated text")

    urls: list[str] = []
    repair_count = 0
    for raw in parsed:
        url = strip_wrapping_quotes(clean_text(raw))
        if not url:
            continue
        repaired = strip_unmatched_trailing_parentheses(url)
        repair_count += int(repaired != url)
        url = repaired
        if not url.startswith(("http://", "https://")):
            raise ValueError(f"Unsupported source URL: {url}")
        if url not in urls:
            urls.append(url)
    return urls, repair_count


def strip_wrapping_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1].strip()
    return value


def strip_unmatched_trailing_parentheses(url: str) -> str:
    """Remove CSV punctuation without damaging balanced Wikipedia titles."""
    cleaned = url
    while cleaned.endswith(")") and cleaned.count(")") > cleaned.count("("):
        cleaned = cleaned[:-1].rstrip()
    return cleaned


def clean_text(value: Any) -> str:
    return " ".join(str(value or "").split()).strip()


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
