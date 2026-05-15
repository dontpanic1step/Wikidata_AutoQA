"""Grade prediction records with the shared SimpleQA-style grader."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from wikidata_simpleqa.grading import grade_prediction
from wikidata_simpleqa.io import write_jsonl


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--format", choices=["jsonl", "tsv"], default="jsonl")
    parser.add_argument("--question-field", default="question")
    parser.add_argument("--gold-field", default="answer")
    parser.add_argument("--prediction-field", default="prediction")
    parser.add_argument("--aliases-field", default="answer_aliases")
    parser.add_argument("--answer-type-field", default="answer_type")
    return parser.parse_args()


def main() -> None:
    """Grade input rows and write JSONL records."""
    args = parse_args()
    rows = _read_rows(args.input, args.format)
    graded_rows: list[dict[str, Any]] = []
    for row in rows:
        aliases = _parse_aliases(row.get(args.aliases_field, []))
        grade = grade_prediction(
            question=str(row.get(args.question_field, "")),
            gold_answer=str(row.get(args.gold_field, "")),
            predicted_answer=str(row.get(args.prediction_field, "")),
            gold_aliases=aliases,
            answer_type=str(row.get(args.answer_type_field, "")),
            source_metadata=row,
        )
        graded_rows.append({**row, **grade})
    write_jsonl(args.output, graded_rows)


def _read_rows(path: Path, input_format: str) -> list[dict[str, Any]]:
    if input_format == "jsonl":
        return [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _parse_aliases(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if not isinstance(value, str) or not value.strip():
        return []
    stripped = value.strip()
    if stripped.startswith("["):
        parsed = json.loads(stripped)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    return [part.strip() for part in stripped.split("|") if part.strip()]


if __name__ == "__main__":
    main()
