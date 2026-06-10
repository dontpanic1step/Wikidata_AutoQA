"""Tests for the KELM half-pipeline generator."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.kelm_generator import KELMTSVGenerator, _normalize_date_value, _render_date_answer


class FakeWikidataClient:
    """Minimal client stub for KELM generator tests."""

    def __init__(self) -> None:
        self.text_mappings: dict[tuple[str, str], dict] = {}

    def search_entities(self, query: str, limit: int = 5):
        rows = {
            "Shiels Jewellers": [
                {"id": "Q1", "label": "Shiels Jewellers", "description": "Australian jewellery retailer"},
            ],
            "University of Cambridge": [
                {"id": "Q2", "label": "University of Cambridge", "description": "collegiate public research university in Cambridge, England"},
            ],
            "Peter Kelland": [
                {"id": "Q3", "label": "Peter Kelland", "description": "mathematician"},
            ],
        }
        return rows.get(query, [])

    def get_entities(self, ids):
        payload = {
            "Q1": {
                "labels": {"en": {"value": "Shiels Jewellers"}},
                "aliases": {"en": []},
                "sitelinks": {"enwiki": {"title": "Shiels_Jewellers"}},
                "claims": {"P31": [{}], "P571": [{}]},
            },
            "Q2": {
                "labels": {"en": {"value": "University of Cambridge"}},
                "aliases": {"en": []},
                "sitelinks": {"enwiki": {"title": "University_of_Cambridge"}},
                "claims": {"P31": [{}]},
            },
            "Q3": {
                "labels": {"en": {"value": "Peter Kelland"}},
                "aliases": {"en": []},
                "sitelinks": {"enwiki": {"title": "Peter_Kelland"}},
                "claims": {"P31": [{}]},
            },
        }
        return {qid: payload[qid] for qid in ids if qid in payload}

    def load_text_mapping(self, namespace: str, key: str):
        return self.text_mappings.get((namespace, key))

    def store_text_mapping(self, namespace: str, key: str, payload: dict):
        self.text_mappings[(namespace, key)] = payload


class KELMGeneratorTests(unittest.TestCase):
    """Check extraction and grounding for the KELM route."""

    def test_generator_extracts_supported_records(self) -> None:
        records = [
            {
                "triples": [["Shiels Jewellers", "inception", "01 January 1945"]],
                "serialized_triples": "Shiels Jewellers inception 01 January 1945",
                "sentence": "Shiels Jewellers is an Australian jewellery retailer and was founded by Jack Shiels in Adelaide in 1945.",
            },
            {
                "triples": [["Peter Kelland", "educated at", "University of Cambridge"]],
                "serialized_triples": "Peter Kelland educated at University of Cambridge",
                "sentence": "After two years in the Marines Peter Kelland began his studies at the University of Cambridge.",
            },
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "kelm.tsv"
            path.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")
            generated = KELMTSVGenerator(input_path=path, record_limit=10).generate(
                client=FakeWikidataClient(),
                run_date="2026-05-12",
            )
        self.assertEqual(len(generated), 2)
        self.assertEqual(generated[0].answer, "1945")
        self.assertEqual(generated[0].subject_entity.qid, "Q1")
        self.assertEqual(generated[1].answer_entity.qid, "Q2")
        self.assertEqual(generated[1].question, "")
        self.assertEqual(generated[1].canonical_question, "")
        self.assertEqual(generated[1].question_family, "")
        self.assertEqual(generated[1].source_template_domain, "")
        self.assertNotIn("subject_kind", generated[1].source_metadata)

    def test_generator_marks_entity_grounding_failures_explicitly(self) -> None:
        records = [
            {
                "triples": [["Unknown Example Person", "date of death", "01 January 1918"]],
                "serialized_triples": "Unknown Example Person date of death 01 January 1918",
                "sentence": "Unknown Example Person died in 1918.",
            }
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "kelm.tsv"
            path.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")
            generated = KELMTSVGenerator(input_path=path, record_limit=10).generate(
                client=FakeWikidataClient(),
                run_date="2026-05-12",
            )
        self.assertEqual(len(generated), 1)
        self.assertIn("entity_grounding_failed", generated[0].notes)

    def test_literal_date_helpers_handle_bc_years(self) -> None:
        self.assertEqual(_normalize_date_value("01 January 200 BC"), "-200-01-01")
        self.assertEqual(
            _render_date_answer("01 January 200 BC", relation_text="inception"),
            "200 BC",
        )


if __name__ == "__main__":
    unittest.main()
