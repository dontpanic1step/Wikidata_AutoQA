"""Tests for the rule-based QA gate."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from test_support import ROOT  # noqa: F401

SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from run_rule_based_qa_gate import (  # noqa: E402
    BOOL_KEY,
    atomic_write_json,
    discover_input_files,
    evaluate_place_gate,
    evaluate_record,
    normalize_gate_date_answer,
    extract_place_category,
    load_simpleqa_place_categories,
    run_gate,
    write_grouped_by_answer_type,
)


def _record(**overrides):
    values = {
        "id": "qa1",
        "question": "Who wrote Example?",
        "answer": "Jane Smith",
        "answer_type": "Person",
    }
    values.update(overrides)
    return values


class RuleBasedQAGateTests(unittest.TestCase):
    def test_extract_place_category_examples(self) -> None:
        self.assertEqual(
            extract_place_category("At which awards ceremony did Tracy Chapman win Best International Album?"),
            "awards ceremony",
        )
        self.assertEqual(
            extract_place_category("In which district of Uttarakhand was Ila Pant born?"),
            "district",
        )
        self.assertEqual(
            extract_place_category("Which peninsular plateau of India extends 900 km?"),
            "peninsular plateau",
        )
        self.assertEqual(
            extract_place_category("What castle overlooked Carmel Glen and its burn and was situated in Knockentiber?"),
            "castle",
        )
        self.assertEqual(
            extract_place_category("What are the names of the three stadiums in South Africa that were most used?"),
            "stadium",
        )
        self.assertEqual(
            extract_place_category("In which Canadian city was the Gigantour concert held?"),
            "city",
        )
        self.assertEqual(
            extract_place_category("Which New Jersey county has a popularly elected county executive?"),
            "county",
        )

    def test_place_gate_rejects_non_whitelisted_category(self) -> None:
        matched, details = evaluate_place_gate(
            _record(
                answer_type="Place",
                question="At which awards ceremony did Tracy Chapman win the Best International Album award in 1989?",
            ),
            place_whitelist={"city", "country", "district"},
        )

        self.assertFalse(matched)
        self.assertEqual(details["extracted_category"], "awards ceremony")
        self.assertIn("not in the place whitelist", details["reason"])

    def test_place_gate_accepts_whitelisted_category(self) -> None:
        matched, details = evaluate_place_gate(
            _record(answer_type="Place", question="Which city in Nepal is known as the City of Nine Hills?"),
            place_whitelist={"city"},
        )

        self.assertTrue(matched)
        self.assertEqual(details["extracted_category"], "city")

    def test_simpleqa_place_categories_are_loaded_from_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = Path(tmpdir) / "simpleqa_verified.json"
            fixture.write_text(
                json.dumps(
                    [
                        {
                            "question": "At what zoo did August Scherl demonstrate his gyro-monorail?",
                            "answer_type": "Place",
                        },
                        {
                            "question": "Who wrote Example?",
                            "answer_type": "Person",
                        },
                    ]
                ),
                encoding="utf-8",
            )

            categories = load_simpleqa_place_categories(fixture)

        self.assertIn("zoo", categories)
        self.assertNotIn("who", categories)

    def test_run_gate_splits_matched_and_mismatched_records(self) -> None:
        records = [
            _record(id="p1", answer="The Red Blue", answer_type="Person"),
            _record(
                id="pl1",
                answer="Brit Awards",
                answer_type="Place",
                question="At which awards ceremony did Tracy Chapman win the Best International Album award?",
            ),
            _record(id="n1", answer="42", answer_type="Number", question="How many examples?"),
        ]

        matched, mismatched = run_gate(
            records,
            place_whitelist={"city", "country"},
        )

        self.assertEqual([record["id"] for record in matched], ["p1", "n1"])
        self.assertEqual([record["id"] for record in mismatched], ["pl1"])
        self.assertTrue(matched[0]["bool_result"][BOOL_KEY])
        self.assertEqual(mismatched[0]["rule_based_qa_gate"]["details"]["extracted_category"], "awards ceremony")

    def test_write_grouped_outputs_uses_atomic_jsonl_and_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            records = [
                _record(id="p1", answer_type="Person"),
                _record(id="pl1", answer_type="Place"),
            ]
            written = write_grouped_by_answer_type(
                records,
                output_dir,
                prefix="rule_gate_matched",
                overwrite=False,
            )

            self.assertEqual(
                sorted(path.name for path in written),
                ["person.rule_gate_matched.jsonl", "place.rule_gate_matched.jsonl"],
            )
            self.assertFalse(list(output_dir.glob("*.tmp")))
            with self.assertRaises(FileExistsError):
                write_grouped_by_answer_type(
                    records,
                    output_dir,
                    prefix="rule_gate_matched",
                    overwrite=False,
                )

    def test_atomic_write_json_writes_inspectable_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "place_whitelist.json"
            atomic_write_json(path, ["city", "country"])

            payload = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(payload, ["city", "country"])

    def test_discover_input_files_can_exclude_date_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            person = root / "01_person_accepted.jsonl"
            date = root / "01_date_accepted.jsonl"
            person.write_text("{}", encoding="utf-8")
            date.write_text("{}", encoding="utf-8")

            files = discover_input_files(root, "*accepted*.jsonl", "*date*")

        self.assertEqual(files, [person])

    def test_date_gate_accepts_standard_formats(self) -> None:
        self.assertEqual(normalize_gate_date_answer("May 25, 2026"), "May 25, 2026")
        self.assertEqual(normalize_gate_date_answer("July 17, 924"), "July 17, 924")
        self.assertEqual(normalize_gate_date_answer("July 17, 0924"), "July 17, 924")
        self.assertEqual(normalize_gate_date_answer("May 2026"), "May 2026")
        self.assertEqual(normalize_gate_date_answer("May 924"), "May 924")
        self.assertEqual(normalize_gate_date_answer("May, 2026"), "May 2026")
        self.assertEqual(normalize_gate_date_answer("2026"), "2026")
        self.assertEqual(normalize_gate_date_answer("0924"), "924")
        self.assertEqual(normalize_gate_date_answer("200 BC"), "200 BC")
        self.assertEqual(normalize_gate_date_answer("200 bce"), "200 BCE")

    def test_date_gate_normalizes_numeric_formats(self) -> None:
        self.assertEqual(normalize_gate_date_answer("1940-03"), "March 1940")
        self.assertEqual(normalize_gate_date_answer("924-07"), "July 924")
        self.assertEqual(normalize_gate_date_answer("04-1940"), "April 1940")
        self.assertEqual(normalize_gate_date_answer("2026-05-25"), "May 25, 2026")
        self.assertEqual(normalize_gate_date_answer("924-07-17"), "July 17, 924")
        self.assertEqual(normalize_gate_date_answer("-0200-07-17"), "July 17, 200 BC")
        self.assertEqual(normalize_gate_date_answer("5/25/2026"), "May 25, 2026")
        self.assertEqual(normalize_gate_date_answer("7/17/924"), "July 17, 924")

    def test_date_gate_rejects_ranges_and_vague_periods(self) -> None:
        self.assertIsNone(normalize_gate_date_answer("2020-2021"))
        self.assertIsNone(normalize_gate_date_answer("late Middle ages"))
        self.assertIsNone(normalize_gate_date_answer("2014-15"))
        self.assertIsNone(normalize_gate_date_answer("0 BC"))

    def test_date_gate_updates_answer_when_normalized(self) -> None:
        output, matched = evaluate_record(
            _record(id="d1", answer_type="Date", answer="1940-03"),
            place_whitelist=set(),
        )

        self.assertTrue(matched)
        self.assertEqual(output["answer"], "March 1940")
        self.assertTrue(output["bool_result"][BOOL_KEY])
        self.assertEqual(
            output["rule_based_qa_gate"]["details"]["normalized_answer"],
            "March 1940",
        )


if __name__ == "__main__":
    unittest.main()
