from __future__ import annotations

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
