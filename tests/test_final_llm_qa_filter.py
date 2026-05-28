"""Tests for the final LLM QA filtering script."""

from __future__ import annotations

import asyncio
import json
import sys
import tempfile
import unittest
from pathlib import Path

from test_support import ROOT  # noqa: F401

SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from run_final_llm_qa_filter import (  # noqa: E402
    ANSWER_TYPE_DEFINITIONS,
    DOMAIN_CHOICES,
    build_context_text,
    build_judge_prompt,
    bool_result_from_rubrics,
    discover_input_files,
    load_jsonl,
    openrouter_chat_completions_endpoint,
    parse_judge_response,
    run_filter,
    write_grouped_outputs,
)


def _record(**overrides):
    values = {
        "id": "qa1",
        "question": "Who proposed the organism-like colony analysis?",
        "answer": "Jack A. Wilson",
        "answer_aliases": [],
        "answer_type": "Person",
        "source_metadata": {
            "page_title": "Organism",
            "first_paragraph": "An organism is any living thing.",
            "parsed_tables": [
                {
                    "table_index": 3,
                    "section_heading": "Organism-like colonies",
                    "caption": "Jack A. Wilson's analysis",
                    "nearby_intro": "The philosopher Jack A. Wilson examines boundary cases.",
                    "markdown": "| Function | Siphonophore |\n| --- | --- |\n| Composition | Many zooids |",
                }
            ],
        },
    }
    values.update(overrides)
    return values


class FakeJudgeClient:
    def __init__(self, response: str | Exception) -> None:
        self.response = response
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


class FinalLLMQAFilterTests(unittest.TestCase):
    def test_load_jsonl_and_discover_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            accepted = root / "01_person_accepted.jsonl"
            ignored = root / "01_person_rejected.jsonl"
            accepted.write_text(json.dumps(_record(), ensure_ascii=False) + "\n", encoding="utf-8")
            ignored.write_text(json.dumps(_record(id="bad"), ensure_ascii=False) + "\n", encoding="utf-8")

            files = discover_input_files(root, "*accepted*.jsonl")
            records = load_jsonl(files[0])

        self.assertEqual(files, [accepted])
        self.assertEqual(records[0]["id"], "qa1")

    def test_build_context_uses_markdown_tables_and_page_context(self) -> None:
        context = build_context_text(_record())

        self.assertIn("Page title: Organism", context)
        self.assertIn("First paragraph: An organism is any living thing.", context)
        self.assertIn("Table index: 3", context)
        self.assertIn("Section heading: Organism-like colonies", context)
        self.assertIn("Nearby paragraph: The philosopher Jack A. Wilson", context)
        self.assertIn("| Function | Siphonophore |", context)

    def test_prompt_includes_answer_type_definitions_and_domain_choices(self) -> None:
        prompt = build_judge_prompt(_record(answer_type="Other"))

        self.assertIn("question_matches_answer_type", prompt)
        self.assertIn("Other: " + ANSWER_TYPE_DEFINITIONS["Other"], prompt)
        self.assertIn("Science & technology", prompt)
        self.assertIn("This is not the answer type", prompt)
        self.assertIn("Place: " + ANSWER_TYPE_DEFINITIONS["Place"], prompt)
        self.assertIn("not an organization, company, ceremony or event", prompt)
        self.assertNotIn("overall_reason", prompt.split("Required JSON schema:", 1)[1])

    def test_parse_structured_response_keeps_reasons_and_domain(self) -> None:
        response = json.dumps(
            {
                "rubrics": {
                    "answer_derivable_from_context": {"verdict": "YES", "reason": "table says it"},
                    "unique_and_stable_answer": {"verdict": "NO", "reason": "not unique"},
                    "self_contained_question": {"verdict": "N/A", "reason": "unclear"},
                    "question_matches_answer_type": {"verdict": "YES", "reason": "asks who"},
                },
                "domain_choice": "Science & technology",
            }
        )

        rubrics, domain = parse_judge_response(response)
        bools = bool_result_from_rubrics(rubrics)

        self.assertEqual(domain, "Science & technology")
        self.assertEqual(rubrics["answer_derivable_from_context"]["reason"], "table says it")
        self.assertEqual(
            bools,
            {
                "answer_derivable_from_context": True,
                "unique_and_stable_answer": False,
                "self_contained_question": None,
                "question_matches_answer_type": True,
            },
        )

    def test_parse_textual_fallback_response(self) -> None:
        response = """1. YES - The answer is in the table.
2. NO - The answer may change.
3. N/A - Hard to tell.
4. YES - It asks for a person.
domain_choice: History
"""
        rubrics, domain = parse_judge_response(response)

        self.assertEqual(domain, "History")
        self.assertEqual(rubrics["answer_derivable_from_context"]["verdict"], "YES")
        self.assertEqual(rubrics["unique_and_stable_answer"]["verdict"], "NO")
        self.assertEqual(rubrics["self_contained_question"]["verdict"], "N/A")
        self.assertIn("person", rubrics["question_matches_answer_type"]["reason"])

    def test_invalid_domain_in_structured_response_raises(self) -> None:
        response = json.dumps(
            {
                "rubrics": {
                    "answer_derivable_from_context": {"verdict": "YES", "reason": ""},
                    "unique_and_stable_answer": {"verdict": "YES", "reason": ""},
                    "self_contained_question": {"verdict": "YES", "reason": ""},
                    "question_matches_answer_type": {"verdict": "YES", "reason": ""},
                },
                "domain_choice": "Cooking",
            }
        )

        with self.assertRaises(ValueError):
            parse_judge_response(response)

    def test_run_filter_preserves_record_and_adds_success_metadata(self) -> None:
        response = json.dumps(
            {
                "rubrics": {
                    "answer_derivable_from_context": {"verdict": "YES", "reason": "context"},
                    "unique_and_stable_answer": {"verdict": "YES", "reason": "stable"},
                    "self_contained_question": {"verdict": "YES", "reason": "self-contained"},
                    "question_matches_answer_type": {"verdict": "YES", "reason": "person"},
                },
                "domain_choice": "History",
            }
        )
        client = FakeJudgeClient(response)

        judged = asyncio.run(
            run_filter([_record()], client, concurrency=2, judge_model="openai/gpt-4.1-mini")
        )

        self.assertEqual(judged[0]["id"], "qa1")
        self.assertEqual(judged[0]["domain_choice"], "History")
        self.assertTrue(judged[0]["bool_result"]["question_matches_answer_type"])
        self.assertEqual(judged[0]["final_llm_qa_filter"]["analysis_status"], "success")
        self.assertNotIn("overall_reason", judged[0]["final_llm_qa_filter"])
        self.assertIn("Markdown table:", client.prompts[0])

    def test_run_filter_failed_call_writes_nulls_and_error_metadata(self) -> None:
        client = FakeJudgeClient(RuntimeError("network timeout"))

        judged = asyncio.run(run_filter([_record()], client, concurrency=1, judge_model="model"))

        self.assertIsNone(judged[0]["domain_choice"])
        self.assertTrue(all(value is None for value in judged[0]["bool_result"].values()))
        self.assertEqual(judged[0]["final_llm_qa_filter"]["analysis_status"], "error")
        self.assertIn("network timeout", judged[0]["final_llm_qa_filter"]["error"])

    def test_write_grouped_outputs_is_grouped_and_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            records = [_record(answer_type="Person"), _record(id="qa2", answer_type="Date")]
            written = write_grouped_outputs(records, output)

            self.assertEqual(
                sorted(path.name for path in written),
                ["date.final_llm_qa_filtered.jsonl", "person.final_llm_qa_filtered.jsonl"],
            )
            self.assertEqual(len(load_jsonl(output / "person.final_llm_qa_filtered.jsonl")), 1)
            self.assertFalse(list(output.glob("*.tmp")))
            with self.assertRaises(FileExistsError):
                write_grouped_outputs(records, output)

    def test_write_grouped_outputs_can_overwrite_atomically(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            write_grouped_outputs([_record(id="old", answer_type="Person")], output)
            write_grouped_outputs([_record(id="new", answer_type="Person")], output, overwrite=True)

            records = load_jsonl(output / "person.final_llm_qa_filtered.jsonl")

        self.assertEqual(records[0]["id"], "new")

    def test_openrouter_endpoint_accepts_base_or_full_path(self) -> None:
        self.assertEqual(
            openrouter_chat_completions_endpoint("https://openrouter.ai/api/v1"),
            "https://openrouter.ai/api/v1/chat/completions",
        )
        self.assertEqual(
            openrouter_chat_completions_endpoint("https://openrouter.ai/api/v1/chat/completions"),
            "https://openrouter.ai/api/v1/chat/completions",
        )

    def test_domain_choices_include_requested_enum(self) -> None:
        self.assertEqual(
            DOMAIN_CHOICES,
            (
                "Science & technology",
                "Politics",
                "Art",
                "Geography",
                "Sports",
                "Music",
                "TV Shows",
                "History",
                "Video Games",
                "Other",
            ),
        )


if __name__ == "__main__":
    unittest.main()
