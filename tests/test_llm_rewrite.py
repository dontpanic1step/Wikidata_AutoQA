"""Tests for rewrite payload parsing and validation."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.llm_rewrite import build_rewrite_payload, parse_json_object
from wikidata_simpleqa.models import CandidateFact
from wikidata_simpleqa.pipeline import _validate_rewritten_question
from wikidata_simpleqa.validators import is_simple_question, preserves_required_anchors


def make_candidate() -> CandidateFact:
    """Build a minimal candidate for rewrite tests."""
    return CandidateFact(
        subject_qid="Q1",
        subject_label="Project Hail Mary",
        subject_aliases=[],
        domain="film",
        topic="Arts and Media",
        answer_type="Person",
        question_family="who_directed_film",
        subject_type_qids=["Q11424"],
        target_property_pid="P57",
        target_property_label="director",
        answer_qids=["Q2"],
        answer_labels=["Phil Lord and Christopher Miller"],
        answer_aliases=["Lord and Miller"],
        date_property_pid="P577",
        date_value="2026-03-20",
        target_time="2026",
        canonical_question="Who directed the film Project Hail Mary?",
        disambiguation_signature=["film"],
    )


class LLMRewriteTests(unittest.TestCase):
    """Check rewrite helpers and post-rewrite validation."""

    def test_parse_json_object_handles_wrapped_text(self) -> None:
        parsed = parse_json_object('```json\n{"question":"Who directed X?"}\n```')
        self.assertEqual(parsed["question"], "Who directed X?")

    def test_build_payload_includes_subject_anchor(self) -> None:
        payload = build_rewrite_payload(make_candidate())
        self.assertIn("Project Hail Mary", payload["required_anchors"])
        self.assertIn("film", payload["required_anchors"])

    def test_anchor_preservation_passes_when_all_anchors_remain(self) -> None:
        self.assertTrue(
            preserves_required_anchors(
                "Who directed the film Project Hail Mary?",
                ["film", "Project Hail Mary"],
            )
        )

    def test_anchor_preservation_fails_when_medium_is_removed(self) -> None:
        self.assertFalse(
            preserves_required_anchors(
                "Who directed Project Hail Mary?",
                ["film", "Project Hail Mary"],
            )
        )

    def test_rewrite_validation_rejects_temporal_phrase(self) -> None:
        reason = _validate_rewritten_question(
            make_candidate(),
            ["film", "Project Hail Mary"],
            "Who directed the recent film Project Hail Mary?",
        )
        self.assertEqual(reason, "rewrite_contains_temporal_expression")

    def test_rewrite_validation_rejects_answer_leakage(self) -> None:
        reason = _validate_rewritten_question(
            make_candidate(),
            ["film", "Project Hail Mary"],
            "Which Lord and Miller film is Project Hail Mary?",
        )
        self.assertEqual(reason, "rewrite_leaks_answer")

    def test_rewrite_validation_accepts_valid_rewrite(self) -> None:
        reason = _validate_rewritten_question(
            make_candidate(),
            ["film", "Project Hail Mary"],
            "Who directed the film Project Hail Mary?",
        )
        self.assertIsNone(reason)

    def test_simple_question_rejects_explanatory_prompt(self) -> None:
        self.assertFalse(is_simple_question("Who directed X and why?"))


if __name__ == "__main__":
    unittest.main()
