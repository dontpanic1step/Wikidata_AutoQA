"""Tests for temporary Route 3 answer-type redirect helper."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from test_support import ROOT  # noqa: F401

SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from tmp_apply_route3_answer_type_redirects import (  # noqa: E402
    AnswerTypeRedirect,
    apply_manual_answer_type_redirects,
)


def test_apply_manual_answer_type_redirects_appends_reviewed_record(tmp_path: Path) -> None:
    split_dir = tmp_path / "split"
    output_dir = tmp_path / "redirected"
    passed_all = split_dir / "passed_all"
    mismatch = split_dir / "answer_type_mismatch_only" / "original_other"
    passed_all.mkdir(parents=True)
    mismatch.mkdir(parents=True)
    for answer_type in ("date", "number", "other", "person", "place"):
        _write_jsonl(
            passed_all / f"{answer_type}.passed_all.jsonl",
            [{"id": f"{answer_type}_base", "answer_type": answer_type.title(), "bool_result": {}}],
        )
    _write_jsonl(
        mismatch / "supposed_person.jsonl",
        [
            {
                "id": "move_1",
                "answer_type": "Other",
                "question": "Who was the example mayor?",
                "answer": "Jane Doe",
                "bool_result": {"question_matches_answer_type": False},
                "final_llm_qa_filter": {
                    "rubric_result": {
                        "question_matches_answer_type": {
                            "reason": "The question asks for a person."
                        }
                    }
                },
            }
        ],
    )

    summary = apply_manual_answer_type_redirects(
        split_dir,
        output_dir,
        redirects=(AnswerTypeRedirect("answer_type_mismatch_only/original_other/supposed_person.jsonl", "move_1", "Person"),),
    )

    person_rows = _read_jsonl(output_dir / "person.passed_all_appended.jsonl")
    assert summary["output_counts"]["Person"] == 2
    assert person_rows[-1]["id"] == "move_1"
    assert person_rows[-1]["answer_type"] == "Person"
    assert person_rows[-1]["bool_result"]["question_matches_answer_type"] is True
    assert person_rows[-1]["manual_answer_type_move"]["original_answer_type"] == "Other"


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
