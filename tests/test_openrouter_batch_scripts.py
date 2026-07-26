from __future__ import annotations

import csv
import hashlib
import importlib.util
from pathlib import Path
import sys
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]


def load_script_module(name: str, relative_path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_prediction_loader_accepts_route3_final_csv(tmp_path: Path) -> None:
    module = load_script_module(
        "run_openrouter_batch_predictions_route3_csv",
        "scripts/run_openrouter_batch_predictions.py",
    )
    input_path = tmp_path / "route3.csv"
    with input_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["id", "problem", "answer", "topic", "answer_type", "urls"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "id": "route3-1",
                "problem": "Which city hosted the example event?",
                "answer": "Example City",
                "topic": "Geography",
                "answer_type": "Place",
                "urls": '["https://en.wikipedia.org/wiki/Example_City"]',
            }
        )

    records = module.load_csv(input_path)

    assert records == [
        {
            "id": "route3-1",
            "problem": "Which city hosted the example event?",
            "answer": "Example City",
            "topic": "Geography",
            "answer_type": "Place",
            "urls": '["https://en.wikipedia.org/wiki/Example_City"]',
            "question": "Which city hosted the example event?",
        }
    ]


def test_prediction_loader_accepts_simpleqa_verified_csv(tmp_path: Path) -> None:
    module = load_script_module(
        "run_openrouter_batch_predictions_verified_csv",
        "scripts/run_openrouter_batch_predictions.py",
    )
    input_path = tmp_path / "simpleqa_verified.csv"
    with input_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "original_index",
                "problem",
                "answer",
                "topic",
                "answer_type",
                "multi_step",
                "requires_reasoning",
                "urls",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "original_index": "5",
                "problem": "How much money was ordered to be paid?",
                "answer": "120,000 euros",
                "topic": "Politics",
                "answer_type": "Number",
                "multi_step": "true",
                "requires_reasoning": "false",
                "urls": "https://example.com/a,https://example.com/b",
            }
        )

    records = module.load_csv(input_path)

    assert records[0]["id"] == "5"
    assert records[0]["question"] == "How much money was ordered to be paid?"
    assert records[0]["answer"] == "120,000 euros"
    assert records[0]["multi_step"] == "true"
    assert records[0]["requires_reasoning"] == "false"


def test_prediction_from_response_preserves_raw_openrouter_response() -> None:
    module = load_script_module(
        "run_openrouter_batch_predictions",
        "scripts/run_openrouter_batch_predictions.py",
    )
    response = {
        "id": "gen-1",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "<step>internal-looking text</step>\nFinal answer",
                    "reasoning": "optional provider reasoning",
                },
                "finish_reason": "stop",
                "native_finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 3, "completion_tokens": 5},
    }

    prediction = module.prediction_from_response(
        response,
        request_settings={"reasoning": {"effort": "xhigh", "exclude": False}},
    )

    assert prediction["answer"] == "<step>internal-looking text</step>\nFinal answer"
    assert prediction["raw_response"] is response
    assert prediction["raw_response"]["choices"][0]["message"]["reasoning"] == (
        "optional provider reasoning"
    )
    assert prediction["request_settings"]["reasoning"]["exclude"] is False


def test_validate_openrouter_response_allows_missing_content_when_message_exists() -> None:
    module = load_script_module(
        "run_openrouter_batch_predictions",
        "scripts/run_openrouter_batch_predictions.py",
    )
    module.validate_openrouter_response(
        {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "reasoning": "some models may return this field",
                    }
                }
            ]
        },
        model="example/model",
    )


def test_judge_prediction_answer_does_not_fall_back_to_content() -> None:
    module = load_script_module(
        "judge_openrouter_batch_predictions",
        "scripts/judge_openrouter_batch_predictions.py",
    )

    assert module.prediction_answer({"answer": "stored answer", "content": "ignored"}) == (
        "stored answer"
    )
    assert module.prediction_answer({"predicted_answer": "legacy answer"}) == "legacy answer"
    assert module.prediction_answer({"content": "do not extract this"}) == ""


def test_judge_adapts_raw_response_text_record() -> None:
    module = load_script_module(
        "judge_openrouter_batch_predictions_raw_text",
        "scripts/judge_openrouter_batch_predictions.py",
    )
    record = {
        "id": "q1::m::0",
        "question": "Question?",
        "reference_answer": "Gold",
        "model": "example/model",
        "response_text": "Predicted",
        "repeat_index": 0,
    }

    predictions = module.ensure_predictions(record)

    assert module.gold_target_answer(record) == "Gold"
    assert predictions == [
        {
            "model": "example/model",
            "answer": "Predicted",
            "repeat_index": 0,
        }
    ]


def test_judge_adapts_raw_openrouter_response_record() -> None:
    module = load_script_module(
        "judge_openrouter_batch_predictions_raw_response",
        "scripts/judge_openrouter_batch_predictions.py",
    )
    record = {
        "id": "q1::m::1",
        "question": "Question?",
        "gold_answer": "Gold",
        "model": "example/model",
        "response": {"choices": [{"message": {"content": "Predicted from raw"}}]},
    }

    predictions = module.ensure_predictions(record)

    assert module.gold_target_answer(record) == "Gold"
    assert predictions[0]["answer"] == "Predicted from raw"


def test_judge_only_uses_top_level_answer_as_prediction_with_explicit_gold() -> None:
    module = load_script_module(
        "judge_openrouter_batch_predictions_top_answer",
        "scripts/judge_openrouter_batch_predictions.py",
    )

    ambiguous = {"question": "Question?", "answer": "Gold"}
    explicit = {"question": "Question?", "reference_answer": "Gold", "answer": "Predicted"}

    assert module.ensure_predictions(ambiguous) == []
    assert module.ensure_predictions(explicit)[0]["answer"] == "Predicted"


def test_grader_template_and_interpolated_prompt_snapshots() -> None:
    module = load_script_module(
        "judge_openrouter_batch_predictions_prompt_snapshot",
        "scripts/judge_openrouter_batch_predictions.py",
    )
    prompt = module.GRADER_TEMPLATE.format(
        question="Which city hosted the example event?",
        target="Example City",
        predicted_answer="It was held in Example City.",
    )

    assert len(module.GRADER_TEMPLATE) == 7125
    assert hashlib.sha256(module.GRADER_TEMPLATE.encode("utf-8")).hexdigest() == (
        "84c004ec4fcf8f0703bb0d734544036a72e847bfa7116429e5aee5e53ccc8cf3"
    )
    assert len(prompt) == 7165
    assert hashlib.sha256(prompt.encode("utf-8")).hexdigest() == (
        "90ac762a5286b75464a16f6132898cd7a4a7c9f726ee64ce21034a905cc328fe"
    )
    assert "Question: Which city hosted the example event?" in prompt
    assert "Gold target: Example City" in prompt
    assert "Predicted answer: It was held in Example City." in prompt


def test_prediction_runner_user_message_and_mocked_response(monkeypatch, tmp_path: Path) -> None:
    module = load_script_module(
        "run_openrouter_batch_predictions_message_snapshot",
        "scripts/run_openrouter_batch_predictions.py",
    )
    captured: dict[str, object] = {}

    class MockResponse:
        status_code = 200
        text = "ok"
        headers: dict[str, str] = {}

        @staticmethod
        def json() -> dict[str, object]:
            return {"choices": [{"message": {"role": "assistant", "content": "Example City"}}]}

    def mock_post(*args, **kwargs):
        captured.update(kwargs)
        return MockResponse()

    monkeypatch.setattr(module.requests, "post", mock_post)
    settings = module.RunSettings(
        api_key="test-key",
        models=["example/model"],
        output_dir=tmp_path,
        rounds=1,
        concurrency=1,
        timeout_seconds=1.0,
        max_retries=0,
        backoff_base=0.0,
        backoff_cap_seconds=0.0,
        max_tokens=None,
        temperature=0.0,
        reasoning_effort=None,
        proxy=None,
        blob_mode="ignore",
        limit=None,
    )

    user_content = module.build_user_content(
        {"question": "Which city hosted the example event?", "blob": "Context"},
        "ignore",
    )
    response = module.call_openrouter(
        model="example/model",
        user_content=user_content,
        settings=settings,
    )

    assert captured["json"] == {
        "model": "example/model",
        "temperature": 0.0,
        "messages": [
            {"role": "user", "content": "Which city hosted the example event?"}
        ],
    }
    assert response["choices"][0]["message"]["content"] == "Example City"


def test_judge_grade_mapping_and_unparseable_default(monkeypatch) -> None:
    module = load_script_module(
        "judge_openrouter_batch_predictions_grade_mapping",
        "scripts/judge_openrouter_batch_predictions.py",
    )
    client = module.OpenRouterJudgeClient(
        api_key="test-key",
        model="openai/gpt-4.1-mini",
        timeout_seconds=1.0,
        max_retries=0,
        backoff_base=0.0,
        backoff_cap_seconds=0.0,
        temperature=0.0,
        max_tokens=None,
        proxy=None,
    )

    assert module.CHOICE_LETTER_TO_STRING == {
        "A": "CORRECT",
        "B": "INCORRECT",
        "C": "NOT_ATTEMPTED",
    }
    assert module.DEFAULT_GRADE_IF_UNPARSEABLE == "C"
    assert module.parse_choice_letter("unparseable response") == "C"

    captured: dict[str, object] = {}

    class MockResponse:
        status_code = 200
        text = "ok"
        headers: dict[str, str] = {}

        @staticmethod
        def json() -> dict[str, object]:
            return {
                "choices": [
                    {"message": {"role": "assistant", "content": "unparseable response"}}
                ]
            }

    def mock_post(*args, **kwargs):
        captured.update(kwargs)
        return MockResponse()

    monkeypatch.setattr(module.requests, "post", mock_post)
    result = client.grade(question="Question?", target="Gold", predicted_answer="Prediction")

    expected_prompt = module.GRADER_TEMPLATE.format(
        question="Question?",
        target="Gold",
        predicted_answer="Prediction",
    )
    assert captured["json"] == {
        "model": "openai/gpt-4.1-mini",
        "temperature": 0.0,
        "messages": [{"role": "user", "content": expected_prompt}],
    }
    assert result["letter"] == "C"
    assert result["grade"] == "NOT_ATTEMPTED"
    assert result["status"] == "success"


def test_prediction_output_is_readable_by_judge(tmp_path: Path) -> None:
    prediction_module = load_script_module(
        "run_openrouter_batch_predictions_file_contract",
        "scripts/run_openrouter_batch_predictions.py",
    )
    judge_module = load_script_module(
        "judge_openrouter_batch_predictions_file_contract",
        "scripts/judge_openrouter_batch_predictions.py",
    )
    output_path = tmp_path / "predictions.jsonl"
    record = {
        "id": "q1",
        "question": "Which city hosted the example event?",
        "answer": "Example City",
        "predictions": [{"answer": "Example City", "model": "example/model"}],
    }

    prediction_module.atomic_write_jsonl(output_path, [record])
    loaded = judge_module.load_jsonl(output_path)

    assert len(loaded) == 1
    assert judge_module.gold_target_answer(loaded[0]) == "Example City"
    assert judge_module.prediction_answer(judge_module.ensure_predictions(loaded[0])[0]) == (
        "Example City"
    )


def test_route3_generation_and_finalization_do_not_use_batch_evaluation_scripts() -> None:
    route3_files = [
        ROOT / "src" / "wikidata_simpleqa" / "wikipedia_infobox_generator.py",
        ROOT / "src" / "wikidata_simpleqa" / "route3_finalization.py",
        ROOT / "scripts" / "run_wikipedia_infobox_pipeline.py",
        ROOT / "scripts" / "run_wikipedia_infobox_recipe.py",
        ROOT / "scripts" / "finalize_route3_review.py",
    ]
    protected_names = (
        "run_openrouter_batch_predictions",
        "judge_openrouter_batch_predictions",
    )

    for path in route3_files:
        source = path.read_text(encoding="utf-8")
        assert all(name not in source for name in protected_names)
