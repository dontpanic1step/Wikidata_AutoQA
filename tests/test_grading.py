"""Tests for SimpleQA-style grading helpers."""

from __future__ import annotations

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
