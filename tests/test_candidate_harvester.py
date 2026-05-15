"""Tests for candidate hydration helpers."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.candidate_harvester import (
    _extract_label,
    _iter_date_windows,
    _seed_window_days,
    _select_label,
    _select_subject_kind,
    _use_staged_seed_strategy,
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

    def test_seed_window_granularity_defaults_to_year(self) -> None:
        template = DomainTemplate(
            domain="product_manufacturer",
            topic="Economy and Business",
            answer_type="Organization",
            question_family="which_company_manufactured_product",
            subject_type_qid="Q2424752",
            subject_type_label="product",
            date_property_pid="P577",
            target_property_pid="P176",
            target_property_label="manufacturer",
            canonical_question_template="Which company manufactured the product {descriptor}?",
        )
        self.assertEqual(_seed_window_days(template, "year"), 366)
        self.assertIsNone(_seed_window_days(template, "month"))
        self.assertEqual(_seed_window_days(template, "day"), 1)

    def test_day_windows_can_be_processed_in_descending_order(self) -> None:
        windows = _iter_date_windows("2026-01-01", "2026-01-03", 1)
        self.assertEqual(
            list(reversed(windows)),
            [
                ("2026-01-03", "2026-01-03"),
                ("2026-01-02", "2026-01-02"),
                ("2026-01-01", "2026-01-01"),
            ],
        )

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

    def test_single_fact_template_uses_direct_wdqs_by_default(self) -> None:
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
                return [
                    {
                        "item": {"value": "http://www.wikidata.org/entity/Q1"},
                        "answer": {"type": "uri", "value": "http://www.wikidata.org/entity/Q2"},
                        "date": {"value": "+2026-01-02T00:00:00Z"},
                    }
                ]

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
        settings = Settings(target_time="2026", date_upper_bound="2026-01-01", harvest_limit_per_template=5)

        candidates = harvest_candidates(client=client, settings=settings, template=template)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].subject_label, "Example Person")
        self.assertEqual(candidates[0].answer_labels, ["Example City"])
        self.assertEqual(len(client.queries), 1)
        self.assertIn("wdt:P569", client.queries[0])
        self.assertIn("?answer", client.queries[0])
        self.assertTrue(
            any(problem["kind"] == "direct_candidate_query_used" for problem in client.problems)
        )

    def test_staged_seed_query_tag_still_uses_direct_wdqs_first(self) -> None:
        template = DomainTemplate(
            domain="product_manufacturer",
            topic="Economy and Business",
            answer_type="Organization",
            question_family="which_company_manufactured_product",
            subject_type_qid="Q2424752",
            subject_type_label="product",
            date_property_pid="P577",
            target_property_pid="P176",
            target_property_label="manufacturer",
            canonical_question_template="Which company manufactured the product {descriptor}?",
            reasoning_style="single_fact",
            query_tags=["staged_seed_query", "seed_window_weekly"],
        )

        class FakeClient:
            def __init__(self) -> None:
                self.queries: list[str] = []
                self.problems: list[dict] = []

            def record_problem(self, kind: str, message: str, **context) -> None:
                self.problems.append({"kind": kind, "message": message, "context": context})

            def sparql_query(self, query: str):
                self.queries.append(query)
                return [
                    {
                        "item": {"value": "http://www.wikidata.org/entity/Q10"},
                        "answer": {"type": "uri", "value": "http://www.wikidata.org/entity/Q20"},
                        "date": {"value": "+2026-01-02T00:00:00Z"},
                    }
                ]

            def get_entities(self, ids):
                records = {}
                for qid in ids:
                    if qid == "Q10":
                        records[qid] = {
                            "labels": {"en": {"value": "Example Product"}},
                            "claims": {
                                "P31": [{"mainsnak": {"datavalue": {"value": {"id": "Q2424752"}}}}],
                                "P176": [
                                    {
                                        "rank": "normal",
                                        "mainsnak": {
                                            "snaktype": "value",
                                            "datavalue": {"value": {"id": "Q20"}},
                                        },
                                    }
                                ],
                            },
                        }
                    elif qid == "Q20":
                        records[qid] = {
                            "labels": {"en": {"value": "Example Manufacturer"}},
                            "claims": {},
                        }
                return records

        client = FakeClient()
        settings = Settings(target_time="2026", date_upper_bound="2026-01-01", harvest_limit_per_template=5)

        candidates = harvest_candidates(client=client, settings=settings, template=template)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(len(client.queries), 1)
        self.assertIn("?answer", client.queries[0])
        self.assertTrue(
            any(problem["kind"] == "direct_candidate_query_used" for problem in client.problems)
        )

    def test_exact_instance_templates_may_use_fast_seed_fallback(self) -> None:
        template = DomainTemplate(
            domain="museum_country",
            topic="Society and Culture",
            answer_type="Place",
            question_family="which_country_museum_located",
            subject_type_qid="Q33506",
            subject_type_label="museum",
            date_property_pid="P571",
            target_property_pid="P17",
            target_property_label="country",
            canonical_question_template="In which country is the museum {descriptor} located?",
            exact_instance_only=True,
        )
        self.assertTrue(_use_staged_seed_strategy(template))

    def test_direct_query_failure_falls_back_to_subject_seed_path(self) -> None:
        template = DomainTemplate(
            domain="film_director",
            topic="Arts and Media",
            answer_type="Person",
            question_family="who_directed_film",
            subject_type_qid="Q11424",
            subject_type_label="film",
            date_property_pid="P577",
            target_property_pid="P57",
            target_property_label="director",
            canonical_question_template="Who directed the film {descriptor}?",
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
                    raise RuntimeError("direct failed")
                return [
                    {
                        "item": {"value": "http://www.wikidata.org/entity/Q1"},
                        "date": {"value": "+2020-01-02T00:00:00Z"},
                    }
                ]

            def get_entities(self, ids):
                records = {}
                for qid in ids:
                    if qid == "Q1":
                        records[qid] = {
                            "labels": {"en": {"value": "Example Film"}},
                            "claims": {
                                "P31": [{"mainsnak": {"datavalue": {"value": {"id": "Q11424"}}}}],
                                "P57": [
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
                            "labels": {"en": {"value": "Jane Doe"}},
                            "claims": {},
                        }
                return records

        client = FakeClient()
        settings = Settings(target_time="2026", date_upper_bound="2026-01-01", harvest_limit_per_template=5)
        candidates = harvest_candidates(client=client, settings=settings, template=template)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].subject_label, "Example Film")
        self.assertEqual(candidates[0].answer_labels, ["Jane Doe"])
        self.assertEqual(len(client.queries), 2)
        self.assertIn("?answer", client.queries[0])
        self.assertNotIn("?answer", client.queries[1])
        self.assertTrue(
            any(problem["kind"] == "subject_seed_fallback_used" for problem in client.problems)
        )

    def test_direct_query_no_rows_then_seed_hydration_failure_returns_empty(self) -> None:
        template = DomainTemplate(
            domain="film_director",
            topic="Arts and Media",
            answer_type="Person",
            question_family="who_directed_film",
            subject_type_qid="Q11424",
            subject_type_label="film",
            date_property_pid="P577",
            target_property_pid="P57",
            target_property_label="director",
            canonical_question_template="Who directed the film {descriptor}?",
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
                    return []
                return [
                    {
                        "item": {"value": "http://www.wikidata.org/entity/Q1"},
                        "date": {"value": "+2020-01-02T00:00:00Z"},
                    }
                ]

            def get_entities(self, ids):
                if ids == ["Q1"]:
                    raise RuntimeError("hydration failed")
                return {}

        client = FakeClient()
        settings = Settings(target_time="2026", date_upper_bound="2026-01-01", harvest_limit_per_template=5)
        candidates = harvest_candidates(client=client, settings=settings, template=template)

        self.assertEqual(candidates, [])
        self.assertEqual(len(client.queries), 2)
        self.assertTrue(
            any(problem["kind"] == "subject_seed_path_failed" for problem in client.problems)
        )

    def test_direct_query_no_rows_does_not_use_disabled_light_fallback(self) -> None:
        template = DomainTemplate(
            domain="film_director",
            topic="Arts and Media",
            answer_type="Person",
            question_family="who_directed_film",
            subject_type_qid="Q11424",
            subject_type_label="film",
            date_property_pid="P577",
            target_property_pid="P57",
            target_property_label="director",
            canonical_question_template="Who directed the film {descriptor}?",
        )

        class FakeClient:
            def __init__(self) -> None:
                self.queries: list[str] = []
                self.problems: list[dict] = []

            def record_problem(self, kind: str, message: str, **context) -> None:
                self.problems.append({"kind": kind, "message": message, "context": context})

            def sparql_query(self, query: str):
                self.queries.append(query)
                return []

            def get_entities(self, ids):
                return {}

        client = FakeClient()
        settings = Settings(
            target_time="2026",
            harvest_limit_per_template=5,
            route1_light_fallback_enabled=False,
        )
        candidates = harvest_candidates(client=client, settings=settings, template=template)

        self.assertEqual(candidates, [])
        self.assertEqual(len(client.queries), 1)
        self.assertTrue(
            any(problem["kind"] == "subject_seed_fallback_disabled" for problem in client.problems)
        )

    def test_direct_query_no_rows_falls_back_to_subject_seed_success(self) -> None:
        template = DomainTemplate(
            domain="film_director",
            topic="Arts and Media",
            answer_type="Person",
            question_family="who_directed_film",
            subject_type_qid="Q11424",
            subject_type_label="film",
            date_property_pid="P577",
            target_property_pid="P57",
            target_property_label="director",
            canonical_question_template="Who directed the film {descriptor}?",
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
                    return []
                return [
                    {
                        "item": {"value": "http://www.wikidata.org/entity/Q1"},
                        "date": {"value": "+2020-01-02T00:00:00Z"},
                    }
                ]

            def get_entities(self, ids):
                records = {}
                for qid in ids:
                    if qid == "Q1":
                        records[qid] = {
                            "labels": {"en": {"value": "Example Film"}},
                            "claims": {
                                "P31": [{"mainsnak": {"datavalue": {"value": {"id": "Q11424"}}}}],
                                "P57": [
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
                            "labels": {"en": {"value": "Jane Doe"}},
                            "claims": {},
                        }
                return records

        client = FakeClient()
        settings = Settings(target_time="2026", date_upper_bound="2026-01-01", harvest_limit_per_template=5)
        candidates = harvest_candidates(client=client, settings=settings, template=template)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(len(client.queries), 2)
        self.assertIn("?answer", client.queries[0])
        self.assertNotIn("?answer", client.queries[1])
        self.assertTrue(
            any(problem["kind"] == "subject_seed_fallback_used" for problem in client.problems)
        )

    def test_legacy_seed_hydration_failure_fixture_no_longer_falls_back_to_direct(self) -> None:
        template = DomainTemplate(
            domain="film_director",
            topic="Arts and Media",
            answer_type="Person",
            question_family="who_directed_film",
            subject_type_qid="Q11424",
            subject_type_label="film",
            date_property_pid="P577",
            target_property_pid="P57",
            target_property_label="director",
            canonical_question_template="Who directed the film {descriptor}?",
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
                            "answer": {"type": "uri", "value": "http://www.wikidata.org/entity/Q2"},
                            "date": {"value": "+2020-01-02T00:00:00Z"},
                        }
                    ]
                raise AssertionError("light fallback should not run after direct success")

            def get_entities(self, ids):
                if ids == ["Q1"]:
                    raise RuntimeError("hydration failed")
                records = {}
                for qid in ids:
                    if qid == "Q1":
                        records[qid] = {
                            "labels": {"en": {"value": "Example Film"}},
                            "claims": {"P31": [{"mainsnak": {"datavalue": {"value": {"id": "Q11424"}}}}]},
                        }
                    elif qid == "Q2":
                        records[qid] = {
                            "labels": {"en": {"value": "Jane Doe"}},
                            "claims": {},
                        }
                return records

        client = FakeClient()
        settings = Settings(target_time="2026", harvest_limit_per_template=5)
        candidates = harvest_candidates(client=client, settings=settings, template=template)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(len(client.queries), 1)
        self.assertEqual(candidates[0].answer_labels, ["Jane Doe"])

    def test_seed_fallback_drops_missing_subject_label_candidate(self) -> None:
        template = DomainTemplate(
            domain="new_nature_reserve_country",
            topic="Geography",
            answer_type="Place",
            question_family="which_country_nature_reserve_located",
            subject_type_qid="Q473972",
            subject_type_label="nature reserve",
            date_property_pid="P571",
            target_property_pid="P17",
            target_property_label="country",
            canonical_question_template="In which country is the nature reserve {descriptor} located?",
            reasoning_style="single_fact",
            query_tags=["staged_seed_query"],
        )

        class FakeClient:
            def __init__(self) -> None:
                self.problems: list[dict] = []

            def record_problem(self, kind: str, message: str, **context) -> None:
                self.problems.append({"kind": kind, "message": message, "context": context})

            def sparql_query(self, _query: str):
                return [
                    {
                        "item": {"value": "http://www.wikidata.org/entity/Q30"},
                        "date": {"value": "+2026-02-03T00:00:00Z"},
                    }
                ]

            def get_entities(self, ids):
                records = {}
                for qid in ids:
                    if qid == "Q30":
                        records[qid] = {
                            "claims": {
                                "P31": [{"mainsnak": {"datavalue": {"value": {"id": "Q473972"}}}}],
                                "P17": [
                                    {
                                        "rank": "normal",
                                        "mainsnak": {
                                            "snaktype": "value",
                                            "datavalue": {"value": {"id": "Q34"}},
                                        },
                                    }
                                ],
                            },
                        }
                    elif qid == "Q34":
                        records[qid] = {
                            "labels": {"en": {"value": "Sweden"}},
                            "claims": {},
                        }
                return records

        client = FakeClient()
        settings = Settings(target_time="2026", harvest_limit_per_template=5)

        candidates = harvest_candidates(client=client, settings=settings, template=template)

        self.assertEqual(candidates, [])

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
        self.assertEqual(_seed_window_days(template, "month"), 7)


if __name__ == "__main__":
    unittest.main()
