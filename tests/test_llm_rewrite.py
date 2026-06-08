"""Tests for rewrite payload parsing and validation."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from unittest.mock import patch

from wikidata_simpleqa.cheap_model_qa import OpenRouterCheapModelQAClient
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
        self.assertIn("Do not add, remove, narrow, broaden, or change any information", prompt)
        self.assertIn("The rewritten_question must not contain the answer or any answer alias", prompt)
        self.assertIn("Generate exactly 3 answer-blind search queries", prompt)
        self.assertIn("May 20, 2024", prompt)
        self.assertIn("May 2024", prompt)
        self.assertIn("specify the counted quantity or unit", prompt)
        self.assertIn("Do not add units to the reference answer", prompt)
        self.assertIn("Do not phrase questions as `according to the table`", prompt)
        self.assertIn("Do not ask cumulative-statistic questions", prompt)
        self.assertIn("historically settled and cannot change", prompt)

    def test_route4_two_hop_prompt_includes_hidden_entity_rules(self) -> None:
        prompt = build_rewrite_prompt(
            {
                "task_type": "route1_question_and_queries",
                "canonical_question": "Who was the director of the film whose based on was Example Book?",
                "wikidata_triplet_text": "Example Film -- director -- Jane Doe",
                "route_contract": "route4_two_hop",
                "answer_hop": {"subject_label": "Example Film", "property_label": "director", "answer_labels": ["Jane Doe"]},
                "clue_hop": {"subject_label": "Example Film", "property_label": "based on", "answer_labels": ["Example Book"]},
                "clue_orientation": "hidden_subject",
                "hidden_entities": [{"qid": "Q1", "label": "Example Film"}],
                "visible_clue": {"qid": "Q3", "label": "Example Book"},
                "required_reasoning_clues": ["based on", "Example Book"],
                "answer_labels": ["Jane Doe"],
                "forbidden_patterns": ["current", "latest"],
                "cutoff_year": 2025,
            }
        )
        self.assertIn("hidden-entity two-hop", prompt)
        self.assertIn("Answer hop", prompt)
        self.assertIn("Clue hop", prompt)
        self.assertIn("Hidden entities", prompt)
        self.assertIn("Do not name any hidden entity", prompt)

    def test_route2_prompt_includes_time_and_number_normalization_rules(self) -> None:
        prompt = build_rewrite_prompt(
            {
                "task_type": "route2_question_and_queries",
                "canonical_question": "How much fuel did Example carry?",
                "evidence_text": "Example carried 5,000 gallons of fuel.",
                "forbidden_patterns": ["current", "latest"],
                "cutoff_year": 2025,
            }
        )
        self.assertIn("Evidence text", prompt)
        self.assertIn("May 20, 2024", prompt)
        self.assertIn("May 2024", prompt)
        self.assertIn("how many months", prompt)
        self.assertIn("specify the counted quantity or unit", prompt)
        self.assertIn("Do not add units to the reference answer", prompt)
        self.assertIn("Billboard chart or UNESCO list", prompt)
        self.assertIn("completed event, completed season, or fixed table/list", prompt)
        self.assertIn("historically settled and cannot change", prompt)

    def test_other_rewrite_prompt_omits_number_and_date_precision_rules(self) -> None:
        prompt = build_rewrite_prompt(
            {
                "canonical_question": "What license did Example use?",
                "answer_type": "Other",
                "answer": "MIT License",
                "forbidden_patterns": ["current", "latest"],
                "cutoff_year": 2025,
            }
        )
        self.assertIn("Preserve the configured answer_type `Other`", prompt)
        self.assertNotIn("specify the counted quantity or unit", prompt)
        self.assertNotIn("Do not add units to the reference answer", prompt)
        self.assertNotIn("May 20, 2024", prompt)
        self.assertNotIn("May 2024", prompt)

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
        self.assertIn("Do not add, remove, narrow, broaden, or change information", prompt)
        self.assertIn("The rewritten_question must not contain the answer or any alias", prompt)
        self.assertIn("generate exactly 3 answer-blind search queries", prompt)
        self.assertIn("May 20, 2024", prompt)
        self.assertIn("May 2024", prompt)
        self.assertIn("Only ask for temporal precision that is actually supported by the source", prompt)
        self.assertIn("Do not add units to the reference answer", prompt)
        self.assertIn("Do not phrase questions as `according to the table`", prompt)
        self.assertIn("Do not ask cumulative-statistic questions", prompt)
        self.assertIn("historically settled and cannot change", prompt)

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

    def test_openrouter_rewrite_audit_keeps_full_response_and_sanitized_request(self) -> None:
        config = LLMConfig(
            provider="openrouter",
            model="openai/gpt-4.1-mini",
            api_key_env="OPENROUTER_API_KEY",
        )
        response_body = {
            "id": "resp-1",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": '{"rewritten_question":"Where was Peter Kelland educated?","search_queries":[],"discard_reason":null}',
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
        }
        with (
            patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"}),
            patch.object(OpenRouterRewriteClient, "_request_with_retry", return_value=response_body),
        ):
            client = OpenRouterRewriteClient(config=config, timeout_seconds=30.0)
            audit = client.rewrite_question_with_audit({"canonical_question": "Where did Peter Kelland study?"})

        self.assertEqual(audit["response_body"], response_body)
        self.assertEqual(audit["raw_text"], response_body["choices"][0]["message"]["content"])
        self.assertEqual(audit["parsed_response"]["rewritten_question"], "Where was Peter Kelland educated?")
        self.assertNotIn("Authorization", audit["request_payload"])
        self.assertIn("messages", audit["request_payload"])

    def test_openrouter_generation_audit_keeps_full_response_and_sanitized_request(self) -> None:
        config = LLMConfig(
            provider="openrouter",
            model="openai/gpt-4.1-mini",
            api_key_env="OPENROUTER_API_KEY",
        )
        response_body = {
            "id": "resp-2",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "{\"ok\": true}"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 3, "completion_tokens": 2},
        }
        with (
            patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"}),
            patch.object(OpenRouterCheapModelQAClient, "_request_with_retry", return_value=response_body),
        ):
            client = OpenRouterCheapModelQAClient(config=config, timeout_seconds=30.0)
            audit = client.complete_text_with_audit("Generate one question.")

        self.assertEqual(audit["text"], "{\"ok\": true}")
        self.assertEqual(audit["response_body"], response_body)
        self.assertNotIn("Authorization", audit["request_payload"])
        self.assertEqual(audit["request_payload"]["messages"][-1]["content"], "Generate one question.")

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
