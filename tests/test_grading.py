"""Tests for SimpleQA-style grading helpers."""

from __future__ import annotations

import threading
import unittest
from unittest.mock import patch

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.grading import (
    ModelPanelMember,
    evaluate_model_panel,
    grade_prediction,
    parse_choice_letter,
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


class FakeSequenceClient:
    """Text-completion client that returns one configured response per call."""

    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.prompts: list[str] = []

    def complete_text(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if not self.responses:
            raise AssertionError("No fake response configured.")
        return self.responses.pop(0)


class PromptAwareGraderClient:
    """Grader client that returns grades based on the predicted answer in the prompt."""

    def __init__(self) -> None:
        self.prompts: list[str] = []

    def complete_text(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if "Predicted answer: Jane Doe" in prompt:
            return "A"
        if "Predicted answer: John Smith" in prompt:
            return "B"
        return "C"


class FailingClient:
    """Client that simulates persistent grader transport failure."""

    def complete_text(self, prompt: str) -> str:
        raise RuntimeError("temporary network failure")


class GradingTests(unittest.TestCase):
    """Check SimpleQA-style model-grader paths."""

    def test_grade_prediction_requires_grader_client(self) -> None:
        with self.assertRaisesRegex(ValueError, "grader_client is required"):
            grade_prediction(
                question="Who directed Example Film?",
                gold_answer="Jane Doe",
                predicted_answer="J. Doe",
                gold_aliases=["J. Doe"],
            )

    def test_grade_prediction_does_not_use_deterministic_not_attempted_fallback(self) -> None:
        with self.assertRaisesRegex(ValueError, "grader_client is required"):
            grade_prediction(
                question="Who directed Example Film?",
                gold_answer="Jane Doe",
                predicted_answer="I don't know",
            )

    def test_grade_prediction_does_not_use_deterministic_list_fallback(self) -> None:
        with self.assertRaisesRegex(ValueError, "grader_client is required"):
            grade_prediction(
                question="Which items tied?",
                gold_answer="Alpha; Beta",
                predicted_answer="Alpha and Beta",
                source_metadata={"answer_items": ["Alpha", "Beta"]},
            )

    def test_choice_letter_parser_maps_verified_choices(self) -> None:
        self.assertEqual(parse_choice_letter("A"), "A")
        self.assertEqual(parse_choice_letter("B."), "B")
        self.assertEqual(parse_choice_letter("`C`"), "C")

    def test_unparseable_choice_defaults_to_not_attempted(self) -> None:
        result = grade_prediction(
            question="Who directed Example Film?",
            gold_answer="Jane Doe",
            predicted_answer="Jane",
            grader_client=FakeClient("unparseable"),
        )
        self.assertEqual(result["grade"], "NOT_ATTEMPTED")
        self.assertEqual(result["grader_choice_letter"], "C")
        self.assertEqual(result["grader_parse_status"], "unparseable")
        self.assertEqual(result["raw_judge_response"], "unparseable")

    def test_llm_grader_parses_verified_choice_grade(self) -> None:
        result = grade_prediction(
            question="Who directed Example Film?",
            gold_answer="Jane Doe",
            predicted_answer="Jane",
            grader_client=FakeClient("B"),
        )
        self.assertEqual(result["grade"], "INCORRECT")
        self.assertEqual(result["method"], "simpleqa_verified_grader")
        self.assertEqual(result["reason"], "")

    def test_grader_network_error_defaults_to_not_attempted_with_audit(self) -> None:
        with patch("wikidata_simpleqa.grading.sleep"), patch(
            "wikidata_simpleqa.grading._grader_retry_sleep_seconds", return_value=0.0
        ):
            result = grade_prediction(
                question="Who directed Example Film?",
                gold_answer="Jane Doe",
                predicted_answer="Jane",
                grader_client=FailingClient(),
            )
        self.assertEqual(result["grade"], "NOT_ATTEMPTED")
        self.assertEqual(result["grader_parse_status"], "error")
        self.assertEqual(result["raw_judge_response"], "")
        self.assertEqual(result["grader_error_type"], "RuntimeError")
        self.assertIn("temporary network failure", result["grader_error_message"])

    def test_number_margin_requires_llm_grader(self) -> None:
        metadata = {
            "number_reference_margin": build_number_reference_margin("100", "Number"),
        }
        with self.assertRaisesRegex(ValueError, "grader_client is required"):
            grade_prediction(
                question="How many points did Example Film score?",
                gold_answer="100",
                predicted_answer="101",
                answer_type="Number",
                source_metadata=metadata,
            )

    def test_llm_grader_prompt_uses_reference_margin_without_alias_injection(self) -> None:
        metadata = {
            "number_reference_margin": build_number_reference_margin("100", "Number"),
        }
        grader = FakeClient("A")
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
        self.assertIn("Gold target: 100 (acceptable range:", grader.prompts[0])
        self.assertIn("also acceptable: one hundred", grader.prompts[0])
        self.assertNotIn("Reference answer:", grader.prompts[0])
        self.assertNotIn("Metadata:", grader.prompts[0])

    def test_llm_grader_prompt_explains_list_answers(self) -> None:
        grader = FakeClient("B")
        result = grade_prediction(
            question="Which items tied?",
            gold_answer="Alpha; Beta",
            predicted_answer="Alpha",
            source_metadata={"answer_items": ["Alpha", "Beta"]},
            grader_client=grader,
        )
        self.assertEqual(result["grade"], "INCORRECT")
        self.assertIn("The following are examples of NOT_ATTEMPTED predicted answers.", grader.prompts[0])

    def test_llm_grader_prompt_excludes_source_metadata(self) -> None:
        huge_metadata = {
            "selected_source_table": {"markdown": "x" * 10000},
            "llm_response": {"reasoning": "private reasoning"},
        }
        grader = FakeClient("A")
        grade_prediction(
            question="Who directed Example Film?",
            gold_answer="Jane Doe",
            predicted_answer="Jane Doe",
            source_metadata=huge_metadata,
            grader_client=grader,
        )
        self.assertNotIn("Metadata:", grader.prompts[0])
        self.assertNotIn("selected_source_table", grader.prompts[0])
        self.assertNotIn("private reasoning", grader.prompts[0])

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
            grader_client=PromptAwareGraderClient(),
        )
        self.assertEqual(result["correct_count"], 1)
        self.assertAlmostEqual(result["accuracy"], 0.5)

    def test_evaluate_model_panel_batch_compat_grades_each_prediction(self) -> None:
        grader = PromptAwareGraderClient()
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

        self.assertEqual(len(grader.prompts), 2)
        self.assertEqual(result["models"][0]["method"], "simpleqa_verified_grader_batch_compat")
        self.assertEqual(result["models"][1]["method"], "simpleqa_verified_grader_batch_compat")
        self.assertEqual(result["models"][0]["raw_judge_response"], "A")
        self.assertEqual(result["models"][1]["raw_judge_response"], "B")
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
        grader = PromptAwareGraderClient()
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
            grader_client=grader,
            parallel_answers=True,
        )

        self.assertEqual(result["executed_model_count"], 2)
        self.assertAlmostEqual(result["accuracy"], 0.5)

    def test_evaluate_model_panel_early_stops_when_first_model_exceeds_threshold(self) -> None:
        first_model = FakeClient("Jane Doe")
        second_model = FakeClient("John Smith")
        grader = FakeClient("A")

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
