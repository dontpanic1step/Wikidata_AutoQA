from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[1]


def load_adapter() -> ModuleType:
    path = ROOT / "scripts" / "convert_batch_evaluation_for_verification_agent.py"
    spec = importlib.util.spec_from_file_location("verification_agent_adapter_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def reconstruct_source_record(rows: list[dict[str, object]]) -> dict[str, object]:
    ordered = sorted(
        rows,
        key=lambda row: row["verification_agent_adapter"]["prediction_index"],
    )
    adapter = ordered[0]["verification_agent_adapter"]
    record = dict(adapter["batch_record"])
    record["predictions"] = [
        row["verification_agent_adapter"]["batch_prediction"] for row in ordered
    ]
    return record


def write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(record) + "\n" for record in records),
        encoding="utf-8",
    )


def test_convert_record_is_agent_compatible_and_lossless(tmp_path: Path) -> None:
    module = load_adapter()
    source = {
        "id": "q1",
        "question": "Which city hosted the example event?",
        "answer": "Example City",
        "predictions": [
            {
                "answer": "First answer",
                "raw_response": {
                    "id": "generation-1",
                    "model": "openai/gpt-example",
                    "choices": [{"message": {"content": "First answer"}}],
                },
                "usage": {"completion_tokens": 3},
                "request_settings": {"temperature": 1.0},
            },
            {
                "model": "other/model",
                "answer": "Second answer",
                "judge": {
                    "model": "openai/gpt-4.1-mini",
                    "grade": "INCORRECT",
                    "raw_response": {"choices": [{"message": {"content": "B"}}]},
                },
            },
        ],
    }

    rows, unconverted = module.convert_record(
        source,
        source_file=tmp_path / "questions.openai__gpt-example.judged.jsonl",
        source_line_number=7,
    )

    assert unconverted == []
    assert [(row["original_index"], row["query"]) for row in rows] == [
        ("q1", source["question"]),
        ("q1", source["question"]),
    ]
    assert [row["model"] for row in rows] == ["openai/gpt-example", "other/model"]
    assert [row["response"] for row in rows] == ["First answer", "Second answer"]
    assert all(row["reference_answer"] == "Example City" for row in rows)
    assert reconstruct_source_record(rows) == source
    assert rows[0]["verification_agent_adapter"]["source_line_number"] == 7
    assert rows[0]["verification_agent_adapter"]["prediction_count"] == 2


def test_batch_format_detection_matches_current_evaluation_schema() -> None:
    module = load_adapter()
    conforming = [
        (
            1,
            {
                "id": "q1",
                "question": "Question?",
                "answer": "Gold",
                "predictions": [],
            },
        )
    ]
    nonconforming = [
        (
            1,
            {
                "id": "q1",
                "question": "Question?",
                "answer": "Gold",
            },
        )
    ]

    assert module.batch_evaluation_format_error(conforming) == ""
    assert "missing batch fields: predictions" in module.batch_evaluation_format_error(
        nonconforming
    )


def test_infers_current_prediction_filename_without_losing_model_version(tmp_path: Path) -> None:
    module = load_adapter()
    source_file = tmp_path / "date.rebalanced.openai__gpt-5.6-sol.judged.jsonl"

    assert module.infer_model_from_current_output_name(source_file) == "openai/gpt-5.6-sol"


def test_preserves_empty_prediction_outside_agent_rows(tmp_path: Path) -> None:
    module = load_adapter()
    source = {
        "id": "q1",
        "question": "Question?",
        "answer": "Gold",
        "predictions": [
            {"answer": "usable", "model": "example/model"},
            {"answer": "", "error": "timeout", "model": "example/model"},
        ],
    }

    rows, unconverted = module.convert_record(
        source,
        source_file=tmp_path / "predictions.jsonl",
        source_line_number=1,
    )

    assert [row["response"] for row in rows] == ["usable"]
    assert len(unconverted) == 1
    assert unconverted[0]["reason"] == "prediction has an empty answer"
    assert unconverted[0]["batch_prediction"] == source["predictions"][1]
    assert unconverted[0]["batch_record"] == {
        key: value for key, value in source.items() if key != "predictions"
    }
def test_main_nonrecursively_converts_each_conforming_file_to_new_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = load_adapter()
    input_dir = tmp_path / "batch_outputs"
    output_dir = tmp_path / "agent_inputs"
    input_dir.mkdir()

    first_records = [
        {
            "id": "q1",
            "question": "First question?",
            "answer": "Gold 1",
            "predictions": [
                {"model": "vendor/model-a", "answer": "First response"},
                {"model": "vendor/model-a", "answer": "Second round"},
            ],
        },
        {
            "id": "q2",
            "question": "Second question?",
            "answer": "Gold 2",
            "predictions": [{"model": "vendor/model-a", "answer": "Second response"}],
        },
    ]
    second_records = [
        {
            "id": "q3::model::repeat-0",
            "simpleqa_verified_id": "q3",
            "question": "Third question?",
            "answer": "Gold 3",
            "predictions": [{"model": "vendor/model-b", "answer": "Third response"}],
        }
    ]
    write_jsonl(input_dir / "first.vendor__model-a.jsonl", first_records)
    write_jsonl(input_dir / "second.vendor__model-b.judged.jsonl", second_records)
    write_jsonl(
        input_dir / "route3_candidates.jsonl",
        [{"id": "candidate", "question": "Not evaluation output"}],
    )
    (input_dir / "notes.txt").write_text("ignored", encoding="utf-8")

    nested_dir = input_dir / "nested"
    nested_dir.mkdir()
    write_jsonl(nested_dir / "nested.vendor__model-c.jsonl", first_records)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "convert_batch_evaluation_for_verification_agent.py",
            str(input_dir),
            str(output_dir),
        ],
    )
    module.main()

    assert {path.name for path in output_dir.iterdir()} == {
        "first.vendor__model-a.jsonl",
        "second.vendor__model-b.judged.jsonl",
        "conversion_summary.json",
    }

    first_rows = [
        json.loads(line)
        for line in (output_dir / "first.vendor__model-a.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    second_rows = [
        json.loads(line)
        for line in (output_dir / "second.vendor__model-b.judged.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    assert [row["original_index"] for row in first_rows] == ["q1", "q1", "q2"]
    assert reconstruct_source_record(first_rows[:2]) == first_records[0]
    assert reconstruct_source_record(first_rows[2:]) == first_records[1]
    assert second_rows[0]["original_index"] == "q3"
    assert reconstruct_source_record(second_rows) == second_records[0]

    summary = json.loads(
        (output_dir / "conversion_summary.json").read_text(encoding="utf-8")
    )
    assert summary["converted_file_count"] == 2
    assert summary["skipped_file_count"] == 1
    assert summary["conforming_file_count"] == 2
    assert summary["unconverted_item_count"] == 0
    assert [row["source_records"] for row in summary["converted_files"]] == [2, 1]
    assert [row["response_rows"] for row in summary["converted_files"]] == [3, 1]
    assert summary["skipped_files"][0]["source_file"].endswith(
        "route3_candidates.jsonl"
    )

    stdout_summary = json.loads(capsys.readouterr().out)
    assert stdout_summary == {
        "output_dir": summary["output_dir"],
        "conforming_file_count": 2,
        "converted_file_count": 2,
        "skipped_file_count": 1,
        "unconverted_item_count": 0,

    }

def test_existing_output_directory_is_preserved(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_adapter()
    input_dir = tmp_path / "inputs"
    output_dir = tmp_path / "existing"
    input_dir.mkdir()
    output_dir.mkdir()
    marker = output_dir / "keep.txt"
    marker.write_text("keep me", encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "convert_batch_evaluation_for_verification_agent.py",
            str(input_dir),
            str(output_dir),
        ],
    )

    with pytest.raises(SystemExit, match="must be new"):
        module.main()

    assert marker.read_text(encoding="utf-8") == "keep me"


def test_agent_incompatible_items_are_preserved_in_summary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_adapter()
    input_dir = tmp_path / "inputs"
    output_dir = tmp_path / "outputs"
    input_dir.mkdir()
    prediction = {"answer": "", "error": "timeout"}
    source = {
        "id": "q1",
        "question": "Question?",
        "answer": "Gold",
        "predictions": [prediction],
    }
    write_jsonl(input_dir / "batch.vendor__model.jsonl", [source])
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "convert_batch_evaluation_for_verification_agent.py",
            str(input_dir),
            str(output_dir),
        ],
    )

    module.main()

    assert {path.name for path in output_dir.iterdir()} == {
        "conversion_summary.json"
    }
    summary = json.loads(
        (output_dir / "conversion_summary.json").read_text(encoding="utf-8")
    )
    assert summary["conforming_file_count"] == 1
    assert summary["converted_file_count"] == 0
    assert summary["skipped_file_count"] == 1
    assert summary["unconverted_item_count"] == 1
    assert summary["unconverted_items"][0]["reason"] == (
        "prediction has an empty answer"
    )
    assert summary["unconverted_items"][0]["batch_prediction"] == prediction
    assert summary["unconverted_items"][0]["batch_record"] == {
        key: value for key, value in source.items() if key != "predictions"
    }
def test_no_conforming_file_creates_no_output_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_adapter()
    input_dir = tmp_path / "inputs"
    output_dir = tmp_path / "outputs"
    input_dir.mkdir()
    write_jsonl(input_dir / "unrelated.jsonl", [{"id": "not-a-batch-record"}])
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "convert_batch_evaluation_for_verification_agent.py",
            str(input_dir),
            str(output_dir),
        ],
    )

    with pytest.raises(SystemExit, match="No files matched"):
        module.main()

    assert not output_dir.exists()
