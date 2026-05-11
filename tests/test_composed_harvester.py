"""Tests for generic composed-harvester fallbacks and problem reporting."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.composed_harvester import harvest_composed_candidates
from wikidata_simpleqa.config import Settings
from wikidata_simpleqa.models import DomainTemplate


class FakeClient:
    """Minimal client stub for composed-harvester tests."""

    def __init__(self, rows=None, entities=None, query_results=None) -> None:
        self.rows = rows or []
        self.entities = entities or {}
        self.query_results = list(query_results or [])
        self.queries: list[str] = []
        self.recorded_problems: list[dict] = []

    def sparql_query(self, query: str):
        self.queries.append(query)
        if self.query_results:
            result = self.query_results.pop(0)
            if isinstance(result, Exception):
                raise result
            return result
        return self.rows

    def get_entities(self, ids):
        records = {}
        for qid in ids:
            if qid in self.entities:
                records[qid] = self.entities[qid]
            else:
                records[qid] = {"labels": {"en": {"value": f"Label {qid}"}}}
        return records

    def record_problem(self, kind: str, message: str, **context):
        self.recorded_problems.append(
            {
                "kind": kind,
                "message": message,
                "context": context,
            }
        )


class ComposedHarvesterTests(unittest.TestCase):
    """Check reusable fallbacks for unsupported composed templates."""

    def test_generic_count_fallback_builds_candidates(self) -> None:
        template = DomainTemplate(
            domain="paper_author_count",
            topic="Physical Sciences",
            answer_type="Number",
            question_family="how_many_authors_paper",
            subject_type_qid="Q13442814",
            subject_type_label="scholarly article",
            date_property_pid="P577",
            target_property_pid="P50",
            target_property_label="author",
            canonical_question_template="How many authors wrote the article {descriptor}?",
            answer_format="number",
            composition_style="fact_join",
            reasoning_style="fact_join",
            status="blueprint",
        )
        client = FakeClient(
            rows=[
                {
                    "item": {"value": "http://www.wikidata.org/entity/Q1"},
                    "itemLabel": {"value": "Example Article"},
                    "date": {"value": "2026-03-01T00:00:00Z"},
                    "answerCount": {"value": "3"},
                }
            ]
        )
        settings = Settings(target_time="2026", harvest_limit_per_template=5)

        candidates = harvest_composed_candidates(client=client, settings=settings, template=template)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].answer_labels, ["3"])
        self.assertEqual(candidates[0].reasoning_style, "single_fact")
        self.assertTrue(any(problem["kind"] == "generic_count_fallback_used" for problem in client.recorded_problems))
        self.assertFalse(any(problem["kind"] == "missing_join_executor" for problem in client.recorded_problems))
        self.assertEqual(len(client.queries), 1)

    def test_generic_count_fallback_rejects_qid_like_subject_labels(self) -> None:
        template = DomainTemplate(
            domain="paper_author_count",
            topic="Physical Sciences",
            answer_type="Number",
            question_family="how_many_authors_paper",
            subject_type_qid="Q13442814",
            subject_type_label="scholarly article",
            date_property_pid="P577",
            target_property_pid="P50",
            target_property_label="author",
            canonical_question_template="How many authors wrote the article {descriptor}?",
            answer_format="number",
            composition_style="fact_join",
            reasoning_style="fact_join",
            status="blueprint",
        )
        client = FakeClient(
            rows=[
                {
                    "item": {"value": "http://www.wikidata.org/entity/Q1"},
                    "itemLabel": {"value": "Q1"},
                    "date": {"value": "2026-03-01T00:00:00Z"},
                    "answerCount": {"value": "3"},
                }
            ],
            entities={"Q1": {"labels": {"en": {"value": "Q1"}}}},
        )
        settings = Settings(target_time="2026", harvest_limit_per_template=5)

        candidates = harvest_composed_candidates(client=client, settings=settings, template=template)

        self.assertEqual(candidates, [])

    def test_associated_office_holder_executor_builds_candidate(self) -> None:
        template = DomainTemplate(
            domain="ordinal_country_president",
            topic="Politics and Law",
            answer_type="Person",
            question_family="who_was_ordinal_president",
            subject_type_qid="Q6256",
            subject_type_label="country",
            date_property_pid="P585",
            target_property_pid="P39",
            target_property_label="position held",
            canonical_question_template="Who was the {ordinal} president of {descriptor}?",
            composition_style="ordinal_fact",
            reasoning_style="ordinal_fact",
            status="blueprint",
        )
        client = FakeClient(
            query_results=[
                [
                    {
                        "subject": {"value": "http://www.wikidata.org/entity/Q60"},
                        "office": {"value": "http://www.wikidata.org/entity/Q61"},
                    }
                ],
                [
                    {
                        "subject": {"value": "http://www.wikidata.org/entity/Q60"},
                        "office": {"value": "http://www.wikidata.org/entity/Q61"},
                        "answer": {"value": "http://www.wikidata.org/entity/Q62"},
                        "start": {"value": "2026-02-01T00:00:00Z"},
                    }
                ],
                [
                    {
                        "answer": {"value": "http://www.wikidata.org/entity/Q59"},
                        "start": {"value": "2025-01-01T00:00:00Z"},
                    },
                    {
                        "answer": {"value": "http://www.wikidata.org/entity/Q62"},
                        "start": {"value": "2026-02-01T00:00:00Z"},
                    },
                ],
            ],
            entities={
                "Q60": {"labels": {"en": {"value": "Exampleland"}}},
                "Q61": {"labels": {"en": {"value": "President of Exampleland"}}},
                "Q62": {"labels": {"en": {"value": "Leader B"}}},
            },
        )
        settings = Settings(target_time="2026", harvest_limit_per_template=5)

        candidates = harvest_composed_candidates(client=client, settings=settings, template=template)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].source_metadata["ordinal_metadata"]["ordinal_value"], 2)
        self.assertEqual(candidates[0].source_metadata["time_invariance"]["allowed_property_pids"], ["P39"])
        self.assertFalse(any(problem["kind"] == "missing_ordinal_executor" for problem in client.recorded_problems))
        self.assertEqual(len(client.queries), 3)

    def test_generic_direct_join_builds_candidates_without_missing_executor(self) -> None:
        template = DomainTemplate(
            domain="religious_leader_successor",
            topic="Philosophy and Religion",
            answer_type="Person",
            question_family="who_succeeded_religious_leader",
            subject_type_qid="Q246434",
            subject_type_label="religious office",
            date_property_pid="P580",
            target_property_pid="P156",
            target_property_label="followed by",
            canonical_question_template="Who succeeded {descriptor}?",
            composition_style="fact_join",
            reasoning_style="fact_join",
            status="blueprint",
        )
        client = FakeClient(
            rows=[
                {
                    "item": {"value": "http://www.wikidata.org/entity/Q1"},
                    "itemLabel": {"value": "Office A"},
                    "answer": {"type": "uri", "value": "http://www.wikidata.org/entity/Q2"},
                    "answerLabel": {"value": "Person B"},
                    "date": {"value": "2026-03-01T00:00:00Z"},
                }
            ],
            entities={
                "Q1": {
                    "labels": {"en": {"value": "Office A"}},
                    "claims": {"P31": [{"mainsnak": {"datavalue": {"value": {"id": "Q246434"}}}}]},
                },
                "Q2": {"labels": {"en": {"value": "Person B"}}},
                "Q246434": {"labels": {"en": {"value": "religious office"}}},
            },
        )
        settings = Settings(target_time="2026", harvest_limit_per_template=5)

        candidates = harvest_composed_candidates(client=client, settings=settings, template=template)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].answer_labels, ["Person B"])
        self.assertEqual(candidates[0].reasoning_style, "single_fact")
        self.assertFalse(any(problem["kind"] == "missing_join_executor" for problem in client.recorded_problems))

    def test_synthetic_source_work_join_builds_two_hop_candidate(self) -> None:
        template = DomainTemplate(
            domain="tv_series_source_work_author",
            topic="Arts and Media",
            answer_type="Person",
            question_family="who_wrote_source_work_for_series",
            subject_type_qid="Q5398426",
            subject_type_label="television series",
            date_property_pid="P577",
            target_property_pid="COMPOSED_SOURCE_WORK_AUTHOR",
            target_property_label="author of source work",
            canonical_question_template="Who wrote the work that the television series {descriptor} was based on?",
            composition_style="fact_join",
            reasoning_style="fact_join",
            temporal_mode="time_related_join",
            reasoning_recipe={"required_reasoning_clues": ["based on"]},
            status="blueprint",
        )
        client = FakeClient(
            rows=[
                {
                    "subject": {"value": "http://www.wikidata.org/entity/Q10"},
                    "subjectLabel": {"value": "Series A"},
                    "sourceWork": {"value": "http://www.wikidata.org/entity/Q11"},
                    "sourceWorkLabel": {"value": "Novel A"},
                    "author": {"value": "http://www.wikidata.org/entity/Q12"},
                    "authorLabel": {"value": "Author A"},
                    "date": {"value": "2026-04-01T00:00:00Z"},
                }
            ]
        )
        settings = Settings(target_time="2026", harvest_limit_per_template=5)

        candidates = harvest_composed_candidates(client=client, settings=settings, template=template)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].reasoning_style, "multi_hop_join")
        self.assertEqual(candidates[0].hop_count, 2)
        self.assertEqual(candidates[0].bridge_entities[0]["label"], "Novel A")
        self.assertFalse(any(problem["kind"] == "missing_join_executor" for problem in client.recorded_problems))

    def test_series_member_ordinal_executor_builds_candidate(self) -> None:
        template = DomainTemplate(
            domain="ordinal_film_in_series_director",
            topic="Arts and Media",
            answer_type="Person",
            question_family="who_directed_ordinal_film_in_series",
            subject_type_qid="Q24856",
            subject_type_label="film series",
            date_property_pid="P577",
            target_property_pid="P57",
            target_property_label="director",
            canonical_question_template="Who directed the {ordinal} film in the series {descriptor}?",
            composition_style="ordinal_fact",
            reasoning_style="ordinal_fact",
            status="blueprint",
        )
        client = FakeClient(
            query_results=[
                [
                    {
                        "series": {"value": "http://www.wikidata.org/entity/Q20"},
                        "seriesLabel": {"value": "Saga A"},
                        "member": {"value": "http://www.wikidata.org/entity/Q21"},
                        "memberLabel": {"value": "Saga A Part 2"},
                        "answer": {"value": "http://www.wikidata.org/entity/Q22"},
                        "answerLabel": {"value": "Director A"},
                        "date": {"value": "2026-05-01T00:00:00Z"},
                    }
                ],
                [
                    {
                        "member": {"value": "http://www.wikidata.org/entity/Q19"},
                        "date": {"value": "2026-04-01T00:00:00Z"},
                    },
                    {
                        "member": {"value": "http://www.wikidata.org/entity/Q21"},
                        "date": {"value": "2026-05-01T00:00:00Z"},
                    },
                ],
            ],
            entities={
                "Q20": {"labels": {"en": {"value": "Saga A"}}},
                "Q21": {"labels": {"en": {"value": "Saga A Part 2"}}},
                "Q22": {"labels": {"en": {"value": "Director A"}}},
            },
        )
        settings = Settings(target_time="2026", harvest_limit_per_template=5)

        candidates = harvest_composed_candidates(client=client, settings=settings, template=template)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].reasoning_style, "multi_hop_ordinal")
        self.assertEqual(candidates[0].source_metadata["ordinal_metadata"]["ordinal_value"], 2)
        self.assertFalse(any(problem["kind"] == "missing_ordinal_executor" for problem in client.recorded_problems))

    def test_ordinal_tournament_host_country_reuses_series_edition_executor(self) -> None:
        template = DomainTemplate(
            domain="ordinal_tournament_host_country",
            topic="Sports and Recreation",
            answer_type="Place",
            question_family="which_country_hosted_ordinal_tournament",
            subject_type_qid="Q132241",
            subject_type_label="tournament",
            date_property_pid="P585",
            target_property_pid="P17",
            target_property_label="country",
            canonical_question_template="Which country hosted the {ordinal} edition of {descriptor}?",
            composition_style="ordinal_fact",
            reasoning_style="ordinal_fact",
            status="blueprint",
        )
        client = FakeClient(
            query_results=[
                [
                    {
                        "edition": {"value": "http://www.wikidata.org/entity/Q23"},
                        "series": {"value": "http://www.wikidata.org/entity/Q24"},
                        "answer": {"value": "http://www.wikidata.org/entity/Q25"},
                        "date": {"value": "2026-05-01T00:00:00Z"},
                        "seriesPropertyPid": {"value": "P179"},
                        "datePropertyPid": {"value": "P585"},
                    }
                ],
                [
                    {
                        "edition": {"value": "http://www.wikidata.org/entity/Q22"},
                        "date": {"value": "2025-05-01T00:00:00Z"},
                    },
                    {
                        "edition": {"value": "http://www.wikidata.org/entity/Q23"},
                        "date": {"value": "2026-05-01T00:00:00Z"},
                    },
                ],
            ],
            entities={
                "Q23": {"labels": {"en": {"value": "2026 Example Cup"}}},
                "Q24": {"labels": {"en": {"value": "Example Cup"}}},
                "Q25": {"labels": {"en": {"value": "Spain"}}},
            },
        )
        settings = Settings(target_time="2026", harvest_limit_per_template=5)

        candidates = harvest_composed_candidates(client=client, settings=settings, template=template)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].answer_labels, ["Spain"])
        self.assertEqual(candidates[0].source_metadata["ordinal_metadata"]["ordinal_value"], 2)
        self.assertFalse(any(problem["kind"] == "missing_ordinal_executor" for problem in client.recorded_problems))

    def test_subject_role_ordinal_executor_builds_candidate(self) -> None:
        template = DomainTemplate(
            domain="ordinal_company_ceo",
            topic="Economy and Business",
            answer_type="Person",
            question_family="who_was_ordinal_company_ceo",
            subject_type_qid="Q783794",
            subject_type_label="company",
            date_property_pid="P585",
            target_property_pid="P169",
            target_property_label="chief executive officer",
            canonical_question_template="Who was the {ordinal} chief executive officer of {descriptor}?",
            composition_style="ordinal_fact",
            reasoning_style="ordinal_fact",
            status="blueprint",
        )
        client = FakeClient(
            query_results=[
                [
                    {
                        "subject": {"value": "http://www.wikidata.org/entity/Q30"},
                        "subjectLabel": {"value": "Example Corp"},
                        "answer": {"value": "http://www.wikidata.org/entity/Q31"},
                        "answerLabel": {"value": "Leader B"},
                        "start": {"value": "2026-02-01T00:00:00Z"},
                    }
                ],
                [
                    {
                        "answer": {"value": "http://www.wikidata.org/entity/Q29"},
                        "start": {"value": "2025-01-01T00:00:00Z"},
                    },
                    {
                        "answer": {"value": "http://www.wikidata.org/entity/Q31"},
                        "start": {"value": "2026-02-01T00:00:00Z"},
                    },
                ],
            ],
            entities={
                "Q30": {"labels": {"en": {"value": "Example Corp"}}},
                "Q31": {"labels": {"en": {"value": "Leader B"}}},
            },
        )
        settings = Settings(target_time="2026", harvest_limit_per_template=5)

        candidates = harvest_composed_candidates(client=client, settings=settings, template=template)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].reasoning_style, "multi_hop_ordinal")
        self.assertEqual(candidates[0].source_metadata["ordinal_metadata"]["ordinal_value"], 2)
        self.assertEqual(candidates[0].date_property_pid, "P580")
        self.assertFalse(any(problem["kind"] == "missing_ordinal_executor" for problem in client.recorded_problems))

    def test_ordinal_spouse_executor_builds_candidate(self) -> None:
        template = DomainTemplate(
            domain="ordinal_spouse",
            topic="People",
            answer_type="Person",
            question_family="who_was_ordinal_spouse",
            subject_type_qid="Q5",
            subject_type_label="human",
            date_property_pid="P580",
            target_property_pid="P26",
            target_property_label="spouse",
            canonical_question_template="Who was the {ordinal} spouse of {descriptor}?",
            composition_style="ordinal_fact",
            reasoning_style="ordinal_fact",
            temporal_mode="time_related_join",
            status="blueprint",
        )
        client = FakeClient(
            query_results=[
                [
                    {
                        "subject": {"value": "http://www.wikidata.org/entity/Q40"},
                        "subjectLabel": {"value": "Example Person"},
                        "answer": {"value": "http://www.wikidata.org/entity/Q41"},
                        "answerLabel": {"value": "Spouse B"},
                        "start": {"value": "2026-03-01T00:00:00Z"},
                    }
                ],
                [
                    {
                        "answer": {"value": "http://www.wikidata.org/entity/Q39"},
                        "start": {"value": "2020-01-01T00:00:00Z"},
                    },
                    {
                        "answer": {"value": "http://www.wikidata.org/entity/Q41"},
                        "start": {"value": "2026-03-01T00:00:00Z"},
                    },
                ],
            ],
            entities={
                "Q40": {"labels": {"en": {"value": "Example Person"}}},
                "Q41": {"labels": {"en": {"value": "Spouse B"}}},
            },
        )
        settings = Settings(target_time="2026", harvest_limit_per_template=5)

        candidates = harvest_composed_candidates(client=client, settings=settings, template=template)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].source_metadata["ordinal_metadata"]["ordinal_value"], 2)
        self.assertEqual(
            candidates[0].source_metadata["time_invariance"]["allowed_property_pids"],
            ["P26"],
        )

    def test_footballer_goals_ordinal_executor_builds_candidate(self) -> None:
        template = DomainTemplate(
            domain="footballer_goals_in_ordinal_tournament",
            topic="Sports and Recreation",
            answer_type="Number",
            question_family="how_many_goals_footballer_in_ordinal_tournament",
            subject_type_qid="Q937857",
            subject_type_label="association football player",
            date_property_pid="P585",
            target_property_pid="COMPOSED_ORDINAL_TOURNAMENT_GOALS",
            target_property_label="goals scored in ordinal tournament",
            canonical_question_template="How many goals did {player_label} score in the {ordinal} edition of {descriptor}?",
            answer_format="number",
            composition_style="ordinal_fact",
            reasoning_style="ordinal_fact",
            temporal_mode="time_related_join",
            status="blueprint",
        )
        client = FakeClient(
            query_results=[
                [
                    {
                        "player": {"value": "http://www.wikidata.org/entity/Q50"},
                        "edition": {"value": "http://www.wikidata.org/entity/Q51"},
                        "series": {"value": "http://www.wikidata.org/entity/Q52"},
                        "date": {"value": "2026-04-01T00:00:00Z"},
                        "seriesPropertyPid": {"value": "P179"},
                        "datePropertyPid": {"value": "P585"},
                    }
                ],
                [
                    {
                        "player": {"value": "http://www.wikidata.org/entity/Q50"},
                        "edition": {"value": "http://www.wikidata.org/entity/Q51"},
                        "goals": {"value": "4"},
                    }
                ],
                [
                    {
                        "edition": {"value": "http://www.wikidata.org/entity/Q49"},
                        "date": {"value": "2025-04-01T00:00:00Z"},
                    },
                    {
                        "edition": {"value": "http://www.wikidata.org/entity/Q51"},
                        "date": {"value": "2026-04-01T00:00:00Z"},
                    },
                ],
            ],
            entities={
                "Q50": {"labels": {"en": {"value": "Player A"}}},
                "Q51": {"labels": {"en": {"value": "2026 Example Cup"}}},
                "Q52": {"labels": {"en": {"value": "Example Cup"}}},
            },
        )
        settings = Settings(target_time="2026", harvest_limit_per_template=5)

        candidates = harvest_composed_candidates(client=client, settings=settings, template=template)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].answer_labels, ["4"])
        self.assertEqual(candidates[0].hop_count, 3)
        self.assertEqual(candidates[0].source_metadata["ordinal_metadata"]["ordinal_value"], 2)
        self.assertEqual(
            candidates[0].source_metadata["time_invariance"]["allowed_property_pids"],
            ["P1351"],
        )
        self.assertEqual(len(client.queries), 3)

    def test_acquisition_purchase_price_executor_builds_candidate(self) -> None:
        template = DomainTemplate(
            domain="acquisition_purchase_price",
            topic="Economy and Business",
            answer_type="Number",
            question_family="how_many_dollars_company_spent_to_acquire_target",
            subject_type_qid="Q783794",
            subject_type_label="company",
            date_property_pid="P571",
            target_property_pid="COMPOSED_ACQUISITION_PRICE",
            target_property_label="acquisition purchase price",
            canonical_question_template="How many dollars did {acquirer_label} spend to acquire {descriptor}?",
            answer_format="number",
            composition_style="fact_join",
            reasoning_style="fact_join",
            temporal_mode="time_related_join",
            status="blueprint",
        )
        client = FakeClient(
            query_results=[
                [
                    {
                        "stmt": {"value": "http://www.wikidata.org/entity/statement/Q70-P127-Q71"},
                        "target": {"value": "http://www.wikidata.org/entity/Q70"},
                        "acquirer": {"value": "http://www.wikidata.org/entity/Q71"},
                        "start": {"value": "2026-04-01T00:00:00Z"},
                    }
                ]
            ],
            entities={
                "Q70": {"labels": {"en": {"value": "Target Co"}}},
                "Q71": {"labels": {"en": {"value": "Buyer Corp"}}},
            },
        )
        client.query_results.append(
            [
                {
                    "stmt": {"value": "http://www.wikidata.org/entity/statement/Q70-P127-Q71"},
                    "priceAmount": {"value": "25000000"},
                }
            ]
        )
        settings = Settings(target_time="2026", harvest_limit_per_template=5)

        candidates = harvest_composed_candidates(client=client, settings=settings, template=template)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].answer_labels, ["25000000"])
        self.assertEqual(
            candidates[0].source_metadata["question_format_args"]["acquirer_label"],
            "Buyer Corp",
        )
        self.assertEqual(len(client.queries), 2)

    def test_associated_office_holder_executor_chunks_large_pair_batches(self) -> None:
        template = DomainTemplate(
            domain="ordinal_country_president",
            topic="Politics and Law",
            answer_type="Person",
            question_family="who_was_ordinal_president",
            subject_type_qid="Q6256",
            subject_type_label="country",
            date_property_pid="P585",
            target_property_pid="P39",
            target_property_label="position held",
            canonical_question_template="Who was the {ordinal} president of {descriptor}?",
            composition_style="ordinal_fact",
            reasoning_style="ordinal_fact",
            status="blueprint",
        )
        pair_rows = [
            {
                "subject": {"value": f"http://www.wikidata.org/entity/Q{100 + index}"},
                "office": {"value": f"http://www.wikidata.org/entity/Q{200 + index}"},
            }
            for index in range(11)
        ]
        recent_rows = [
            {
                "subject": {"value": "http://www.wikidata.org/entity/Q110"},
                "office": {"value": "http://www.wikidata.org/entity/Q210"},
                "answer": {"value": "http://www.wikidata.org/entity/Q310"},
                "start": {"value": "2026-02-01T00:00:00Z"},
            }
        ]
        history_rows = [
            {
                "office": {"value": "http://www.wikidata.org/entity/Q210"},
                "answer": {"value": "http://www.wikidata.org/entity/Q309"},
                "start": {"value": "2025-01-01T00:00:00Z"},
            },
            {
                "office": {"value": "http://www.wikidata.org/entity/Q210"},
                "answer": {"value": "http://www.wikidata.org/entity/Q310"},
                "start": {"value": "2026-02-01T00:00:00Z"},
            },
        ]
        client = FakeClient(
            query_results=[
                pair_rows,
                recent_rows,
                [],
                history_rows,
            ],
            entities={
                "Q110": {"labels": {"en": {"value": "Exampleland"}}},
                "Q210": {"labels": {"en": {"value": "President of Exampleland"}}},
                "Q310": {"labels": {"en": {"value": "Leader B"}}},
            },
        )
        settings = Settings(target_time="2026", harvest_limit_per_template=5)

        candidates = harvest_composed_candidates(client=client, settings=settings, template=template)

        self.assertEqual(len(candidates), 1)
        self.assertGreaterEqual(len(client.queries), 4)
        self.assertIn("VALUES (?subject ?office)", client.queries[1])
        self.assertIn("VALUES (?subject ?office)", client.queries[2])

    def test_heavy_query_problem_skips_support_probe(self) -> None:
        template = DomainTemplate(
            domain="ordinal_country_prime_minister",
            topic="Politics and Law",
            answer_type="Person",
            question_family="who_was_ordinal_prime_minister",
            subject_type_qid="Q6256",
            subject_type_label="country",
            date_property_pid="P585",
            target_property_pid="P39",
            target_property_label="position held",
            canonical_question_template="Who was the {ordinal} prime minister of {descriptor}?",
            composition_style="ordinal_fact",
            reasoning_style="ordinal_fact",
            status="blueprint",
        )
        client = FakeClient(
            query_results=[
                [
                    {
                        "subject": {"value": "http://www.wikidata.org/entity/Q29"},
                        "office": {"value": "http://www.wikidata.org/entity/Q3113035"},
                    }
                ],
                RuntimeError("simulated chunk failure"),
            ]
        )
        settings = Settings(target_time="2026", harvest_limit_per_template=5)

        candidates = harvest_composed_candidates(client=client, settings=settings, template=template)

        self.assertEqual(candidates, [])
        self.assertTrue(
            any(problem["kind"] == "chunked_office_holder_lookup_failed" for problem in client.recorded_problems)
        )
        self.assertTrue(
            any(
                problem["kind"] == "support_probe_skipped"
                and "heavy-query failure" in problem["message"]
                for problem in client.recorded_problems
            )
        )


if __name__ == "__main__":
    unittest.main()
