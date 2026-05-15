"""Tests for rewrite payload parsing and validation."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from unittest.mock import patch

from wikidata_simpleqa.llm_rewrite import (
    OPENROUTER_REFERER,
    OPENROUTER_TITLE,
    OPENROUTER_USER_AGENT,
    OpenRouterRewriteClient,
    build_rewrite_payload,
    build_rewrite_prompt,
    parse_json_object,
)
from wikidata_simpleqa.config import LLMConfig
from wikidata_simpleqa.models import CandidateFact
from wikidata_simpleqa.route1_validators import validate_route1_rewritten_question
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
        self.assertEqual(payload["task_type"], "route1_question_and_queries")
        self.assertIn("Project Hail Mary", payload["required_anchors"])
        self.assertIn("film", payload["required_anchors"])
        self.assertIn("Project Hail Mary -- director --", payload["wikidata_triplet_text"])

    def test_route1_prompt_requests_queries_and_discard_reason(self) -> None:
        prompt = build_rewrite_prompt(
            {
                "task_type": "route1_question_and_queries",
                "canonical_question": "Who directed the film Project Hail Mary?",
                "wikidata_triplet_text": "Project Hail Mary -- director -- Phil Lord and Christopher Miller",
                "forbidden_patterns": ["current", "latest"],
                "cutoff_year": 2025,
            }
        )
        self.assertIn("Canonical question", prompt)
        self.assertIn("Wikidata triplet text", prompt)
        self.assertIn('"search_queries"', prompt)
        self.assertIn('"answer_aliases"', prompt)
        self.assertIn('"discard_reason"', prompt)
        self.assertIn("Do not narrow or specialize it", prompt)

    def test_kelm_prompt_requests_queries_and_discard_reason(self) -> None:
        prompt = build_rewrite_prompt(
            {
                "task_type": "kelm_question_and_queries",
                "serialized_triple": "Shiels Jewellers inception 01 January 1945",
                "kelm_sentence": "Shiels Jewellers is an Australian jewellery retailer and was founded by Jack Shiels in Adelaide in 1945.",
                "answer": "1945",
                "forbidden_patterns": ["current", "latest"],
                "cutoff_year": 2025,
            }
        )
        self.assertIn("KELM sentence", prompt)
        self.assertIn('"search_queries"', prompt)
        self.assertIn('"answer_aliases"', prompt)
        self.assertIn('"discard_reason"', prompt)
        self.assertIn("casing variant", prompt)
        self.assertIn("capitalization variant", prompt)

    def test_openrouter_request_constants_are_defined(self) -> None:
        self.assertTrue(OPENROUTER_REFERER.startswith("https://"))
        self.assertTrue(OPENROUTER_TITLE)
        self.assertIn("wikidata-simpleqa-generator", OPENROUTER_USER_AGENT)

    def test_openrouter_retries_direct_after_proxy_failure(self) -> None:
        config = LLMConfig(
            provider="openrouter",
            model="openai/gpt-4.1-mini",
            api_key_env="OPENROUTER_API_KEY",
            proxy="socks5://127.0.0.1:7897",
        )
        with (
            patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"}),
            patch.object(OpenRouterRewriteClient, "_request_with_retry") as request_with_retry,
        ):
            request_with_retry.return_value = {
                "choices": [
                    {
                        "message": {
                            "content": '{"rewritten_question":"Where was Peter Kelland educated?","search_queries":[],"discard_reason":null}',
                        }
                    }
                ]
            }
            client = OpenRouterRewriteClient(config=config, timeout_seconds=30.0)
            result = client.rewrite_question({"canonical_question": "Where did Peter Kelland study?"})
        self.assertEqual(result["rewritten_question"], "Where was Peter Kelland educated?")
        request_with_retry.assert_called_once()

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
        reason = validate_route1_rewritten_question(
            make_candidate(),
            ["film", "Project Hail Mary"],
            "Who directed the recent film Project Hail Mary?",
            cutoff_year=2025,
        )
        self.assertEqual(reason, "rewrite_contains_temporal_expression")

    def test_rewrite_validation_rejects_answer_leakage(self) -> None:
        reason = validate_route1_rewritten_question(
            make_candidate(),
            ["film", "Project Hail Mary"],
            "Which Lord and Miller film is Project Hail Mary?",
            cutoff_year=2025,
        )
        self.assertEqual(reason, "rewrite_leaks_answer")

    def test_rewrite_validation_accepts_valid_rewrite(self) -> None:
        reason = validate_route1_rewritten_question(
            make_candidate(),
            ["film", "Project Hail Mary"],
            "Who directed the 2020 film Project Hail Mary?",
            cutoff_year=2025,
        )
        self.assertIsNone(reason)

    def test_simple_question_rejects_explanatory_prompt(self) -> None:
        self.assertFalse(is_simple_question("Who directed X and why?"))


if __name__ == "__main__":
    unittest.main()
