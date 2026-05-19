"""Tests for SimpleQA-style grading helpers."""

from __future__ import annotations

import threading
import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.grading import (
    ModelPanelMember,
    evaluate_model_panel,
    grade_prediction,
    summarize_panel_runs,
)
from wikidata_simpleqa.number_reference import build_number_reference_margin


class FakeClient:
    """Minimal text-completion client."""

    def __init__(self, response: str) -> None:
        self.response = response
        self.prompts: list[str] = []

    def complete_text(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.response


class GradingTests(unittest.TestCase):
    """Check deterministic and model-grader paths."""

    def test_deterministic_grader_accepts_alias(self) -> None:
        result = grade_prediction(
            question="Who directed Example Film?",
            gold_answer="Jane Doe",
            predicted_answer="J. Doe",
            gold_aliases=["J. Doe"],
        )
        self.assertEqual(result["grade"], "CORRECT")

    def test_deterministic_grader_detects_not_attempted(self) -> None:
        result = grade_prediction(
            question="Who directed Example Film?",
            gold_answer="Jane Doe",
            predicted_answer="I don't know",
        )
        self.assertEqual(result["grade"], "NOT_ATTEMPTED")

    def test_deterministic_grader_requires_complete_list_answer(self) -> None:
        complete = grade_prediction(
            question="Which items tied?",
            gold_answer="Alpha; Beta",
            predicted_answer="Alpha and Beta",
            source_metadata={"answer_items": ["Alpha", "Beta"]},
        )
        partial = grade_prediction(
            question="Which items tied?",
            gold_answer="Alpha; Beta",
            predicted_answer="Alpha",
            source_metadata={"answer_items": ["Alpha", "Beta"]},
        )
        self.assertEqual(complete["grade"], "CORRECT")
        self.assertEqual(complete["method"], "deterministic_list_match")
        self.assertEqual(partial["grade"], "INCORRECT")

    def test_llm_grader_parses_json_grade(self) -> None:
        result = grade_prediction(
            question="Who directed Example Film?",
            gold_answer="Jane Doe",
            predicted_answer="Jane",
            grader_client=FakeClient('{"grade":"INCORRECT","reason":"too vague"}'),
        )
        self.assertEqual(result["grade"], "INCORRECT")
        self.assertEqual(result["method"], "llm_grader")

    def test_deterministic_grader_accepts_number_margin(self) -> None:
        metadata = {
            "number_reference_margin": build_number_reference_margin("100", "Number"),
        }
        inside = grade_prediction(
            question="How many points did Example Film score?",
            gold_answer="100",
            predicted_answer="101",
            answer_type="Number",
            source_metadata=metadata,
        )
        outside = grade_prediction(
            question="How many points did Example Film score?",
            gold_answer="100",
            predicted_answer="103",
            answer_type="Number",
            source_metadata=metadata,
        )
        self.assertEqual(inside["grade"], "CORRECT")
        self.assertEqual(inside["method"], "deterministic_number_margin")
        self.assertEqual(outside["grade"], "INCORRECT")

    def test_llm_grader_prompt_uses_reference_margin_without_alias_injection(self) -> None:
        metadata = {
            "number_reference_margin": build_number_reference_margin("100", "Number"),
        }
        grader = FakeClient('{"grade":"CORRECT","reason":"within range"}')
        result = grade_prediction(
            question="How many points did Example Film score?",
            gold_answer="100",
            predicted_answer="101",
            gold_aliases=["one hundred"],
            answer_type="Number",
            source_metadata=metadata,
            grader_client=grader,
        )
        self.assertEqual(result["grade"], "CORRECT")
        self.assertIn("Reference answer: 100 (acceptable range:", grader.prompts[0])
        self.assertIn("Gold aliases: ['one hundred']", grader.prompts[0])
        self.assertNotIn("Gold answer:", grader.prompts[0])
        self.assertNotIn("one hundred are also acceptable", grader.prompts[0])

    def test_llm_grader_prompt_explains_list_answers(self) -> None:
        grader = FakeClient('{"grade":"INCORRECT","reason":"partial list"}')
        result = grade_prediction(
            question="Which items tied?",
            gold_answer="Alpha; Beta",
            predicted_answer="Alpha",
            source_metadata={"answer_items": ["Alpha", "Beta"]},
            grader_client=grader,
        )
        self.assertEqual(result["grade"], "INCORRECT")
        self.assertIn("If the reference answer is a list", grader.prompts[0])

    def test_evaluate_model_panel_records_accuracy(self) -> None:
        result = evaluate_model_panel(
            question="Who directed Example Film?",
            gold_answer="Jane Doe",
            gold_aliases=["J. Doe"],
            answer_type="Person",
            source_metadata={},
            model_panel=[
                ModelPanelMember("correct-model", FakeClient("Jane Doe")),
                ModelPanelMember("wrong-model", FakeClient("John Smith")),
            ],
        )
        self.assertEqual(result["correct_count"], 1)
        self.assertAlmostEqual(result["accuracy"], 0.5)

    def test_evaluate_model_panel_uses_one_batch_grader_call(self) -> None:
        grader = FakeClient(
            '{"grades": ['
            '{"index": 0, "grade": "CORRECT", "reason": "same"},'
            '{"index": 1, "grade": "INCORRECT", "reason": "wrong"}'
            "]}"
        )
        result = evaluate_model_panel(
            question="Who directed Example Film?",
            gold_answer="Jane Doe",
            gold_aliases=["J. Doe"],
            answer_type="Person",
            source_metadata={},
            model_panel=[
                ModelPanelMember("correct-model", FakeClient("Jane Doe")),
                ModelPanelMember("wrong-model", FakeClient("John Smith")),
            ],
            grader_client=grader,
            batch_grader=True,
        )

        self.assertEqual(len(grader.prompts), 1)
        self.assertEqual(result["models"][0]["method"], "llm_grader_batch")
        self.assertEqual(result["models"][1]["method"], "llm_grader_batch")
        self.assertAlmostEqual(result["accuracy"], 0.5)

    def test_evaluate_model_panel_answers_in_parallel(self) -> None:
        class BarrierClient:
            def __init__(self, response: str, barrier: threading.Barrier) -> None:
                self.response = response
                self.barrier = barrier
                self.prompts: list[str] = []

            def complete_text(self, prompt: str) -> str:
                self.prompts.append(prompt)
                self.barrier.wait(timeout=1.0)
                return self.response

        barrier = threading.Barrier(2)
        result = evaluate_model_panel(
            question="Who directed Example Film?",
            gold_answer="Jane Doe",
            gold_aliases=[],
            answer_type="Person",
            source_metadata={},
            model_panel=[
                ModelPanelMember("correct-model", BarrierClient("Jane Doe", barrier)),
                ModelPanelMember("wrong-model", BarrierClient("John Smith", barrier)),
            ],
            parallel_answers=True,
        )

        self.assertEqual(result["executed_model_count"], 2)
        self.assertAlmostEqual(result["accuracy"], 0.5)

    def test_evaluate_model_panel_early_stops_when_first_model_exceeds_threshold(self) -> None:
        first_model = FakeClient("Jane Doe")
        second_model = FakeClient("John Smith")
        grader = FakeClient('{"grades": [{"index": 0, "grade": "CORRECT", "reason": "same"}]}')

        result = evaluate_model_panel(
            question="Who directed Example Film?",
            gold_answer="Jane Doe",
            gold_aliases=[],
            answer_type="Person",
            source_metadata={},
            model_panel=[
                ModelPanelMember("first-model", first_model),
                ModelPanelMember("second-model", second_model),
            ],
            grader_client=grader,
            accuracy_threshold=0.1,
            early_stop_on_threshold=True,
            batch_grader=True,
        )

        self.assertTrue(result["early_stopped"])
        self.assertEqual(result["early_stop_reason"], "first_model_correct_exceeds_accuracy_threshold")
        self.assertEqual(result["configured_model_count"], 2)
        self.assertEqual(result["executed_model_count"], 1)
        self.assertAlmostEqual(result["accuracy"], 0.5)
        self.assertEqual(len(first_model.prompts), 1)
        self.assertEqual(second_model.prompts, [])
        self.assertEqual(len(grader.prompts), 1)

    def test_summarize_panel_runs_by_model(self) -> None:
        summary = summarize_panel_runs(
            [
                {
                    "models": [
                        {"model": "a", "grade": "CORRECT"},
                        {"model": "b", "grade": "INCORRECT"},
                    ]
                }
            ]
        )
        self.assertAlmostEqual(summary["per_model"]["a"]["accuracy"], 1.0)
        self.assertAlmostEqual(summary["per_model"]["b"]["accuracy"], 0.0)


if __name__ == "__main__":
    unittest.main()
