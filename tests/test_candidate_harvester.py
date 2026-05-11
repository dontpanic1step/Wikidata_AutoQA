"""Tests for candidate hydration helpers."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.candidate_harvester import (
    _extract_label,
    _seed_window_days,
    _select_label,
    _select_subject_kind,
    harvest_candidates,
)
from wikidata_simpleqa.config import Settings
from wikidata_simpleqa.models import DomainTemplate


class CandidateHarvesterTests(unittest.TestCase):
    """Check small label-cleanup and staged-harvest behaviors."""

    def test_extract_label_rejects_qid_like_fallback(self) -> None:
        self.assertEqual(_extract_label({}, "Q138497647"), "")

    def test_extract_label_prefers_real_english_label(self) -> None:
        entity = {"labels": {"en": {"value": "Real title"}}}
        self.assertEqual(_extract_label(entity, "Q138497647"), "Real title")

    def test_select_label_uses_wdqs_fallback_when_hydration_label_missing(self) -> None:
        label, source = _select_label({}, "Fallback title")
        self.assertEqual(label, "Fallback title")
        self.assertEqual(source, "wdqs_label_fallback")

    def test_select_subject_kind_rejects_unrelated_proper_name_labels(self) -> None:
        template = DomainTemplate(
            domain="company_founder",
            topic="Economy and Business",
            answer_type="Person",
            question_family="who_founded_company",
            subject_type_qid="Q783794",
            subject_type_label="company",
            date_property_pid="P571",
            target_property_pid="P112",
            target_property_label="founder",
            canonical_question_template="Who founded the {subject_kind} {descriptor}?",
        )
        subject_kind = _select_subject_kind(template, ["Antal Turr", "company"])
        self.assertEqual(subject_kind, "company")

    def test_broad_template_uses_staged_seed_query_and_local_claim_extraction(self) -> None:
        template = DomainTemplate(
            domain="biography_birth_place_recent_subject",
            topic="People",
            answer_type="Place",
            question_family="where_person_born",
            subject_type_qid="Q5",
            subject_type_label="human",
            date_property_pid="P569",
            target_property_pid="P19",
            target_property_label="place of birth",
            canonical_question_template="Where was {descriptor} born?",
            reasoning_style="single_fact",
        )

        class FakeClient:
            def __init__(self) -> None:
                self.queries: list[str] = []
                self.problems: list[dict] = []

            def record_problem(self, kind: str, message: str, **context) -> None:
                self.problems.append({"kind": kind, "message": message, "context": context})

            def sparql_query(self, query: str):
                self.queries.append(query)
                if len(self.queries) == 1:
                    return [
                        {
                            "item": {"value": "http://www.wikidata.org/entity/Q1"},
                            "date": {"value": "+2026-01-02T00:00:00Z"},
                        }
                    ]
                return []

            def get_entities(self, ids):
                records = {}
                for qid in ids:
                    if qid == "Q1":
                        records[qid] = {
                            "labels": {"en": {"value": "Example Person"}},
                            "claims": {
                                "P31": [{"mainsnak": {"datavalue": {"value": {"id": "Q5"}}}}],
                                "P19": [
                                    {
                                        "rank": "normal",
                                        "mainsnak": {
                                            "snaktype": "value",
                                            "datavalue": {"value": {"id": "Q2"}},
                                        },
                                    }
                                ],
                            },
                        }
                    elif qid == "Q2":
                        records[qid] = {
                            "labels": {"en": {"value": "Example City"}},
                            "aliases": {"en": [{"value": "City Alias"}]},
                            "claims": {},
                        }
                return records

        client = FakeClient()
        settings = Settings(target_time="2026", harvest_limit_per_template=5)

        candidates = harvest_candidates(client=client, settings=settings, template=template)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].subject_label, "Example Person")
        self.assertEqual(candidates[0].answer_labels, ["Example City"])
        self.assertIn("wdt:P569", client.queries[0])
        self.assertIn("wdt:P19", client.queries[0])
        self.assertNotIn("?answerLabel", client.queries[0])
        self.assertTrue(
            any(problem["kind"] == "staged_seed_strategy_used" for problem in client.problems)
        )
        self.assertTrue(
            any(
                problem["kind"] == "windowed_subject_seed_queries_used"
                for problem in client.problems
            )
        )

    def test_query_tags_can_override_seed_window_size(self) -> None:
        template = DomainTemplate(
            domain="custom_timeout_sensitive_template",
            topic="Tests",
            answer_type="Place",
            question_family="where_subject_born",
            subject_type_qid="Q999",
            subject_type_label="test subject",
            date_property_pid="P569",
            target_property_pid="P19",
            target_property_label="place of birth",
            canonical_question_template="Where was {descriptor} born?",
            query_tags=["seed_window_weekly"],
        )
        self.assertEqual(_seed_window_days(template), 7)


if __name__ == "__main__":
    unittest.main()
