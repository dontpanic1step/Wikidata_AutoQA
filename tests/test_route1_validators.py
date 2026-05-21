"""Tests for the Route 1 Wikidata validator bundle."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.config import Settings
from wikidata_simpleqa.models import AmbiguityResolution, CandidateFact, DomainTemplate, RejectedCandidate
from wikidata_simpleqa.route1_validators import (
    ensure_route1_subject_resource,
    validate_route1_candidate,
    validate_route1_rewritten_question,
)


class FakeClient:
    """Minimal Wikidata client stub."""

    def __init__(self, search_results: list[dict[str, str]] | None = None, entities: dict | None = None) -> None:
        self.search_results = search_results or []
        self.entities = entities or {}
        self.search_call_count = 0

    def search_entities(self, query: str, limit: int = 10):
        self.search_call_count += 1
        return self.search_results[:limit]

    def get_entities(self, ids: list[str]):
        return {qid: self.entities[qid] for qid in ids if qid in self.entities}


def make_template() -> DomainTemplate:
    """Build a minimal Route 1 template."""
    return DomainTemplate(
        domain="film_director",
        topic="Arts and Media",
        answer_type="Person",
        question_family="who_directed_film",
        subject_type_qid="Q11424",
        subject_type_label="film",
        date_property_pid="P577",
        target_property_pid="P57",
        target_property_label="director",
        canonical_question_template="Who directed the {subject_kind} {descriptor}?",
    )


def make_candidate() -> CandidateFact:
    """Build a minimal valid Route 1 candidate."""
    return CandidateFact(
        subject_qid="Q1",
        subject_label="Example Film",
        subject_aliases=[],
        domain="film_director",
        topic="Arts and Media",
        answer_type="Person",
        question_family="who_directed_film",
        subject_type_qids=["Q11424"],
        target_property_pid="P57",
        target_property_label="director",
        answer_qids=["Q2"],
        answer_labels=["Jane Doe"],
        answer_aliases=["J. Doe"],
        date_property_pid="P577",
        date_value="2020-01-01",
        target_time="2020",
        canonical_question="Who directed the film Example Film?",
        provenance_complete=True,
        source_metadata={
            "subject_wikipedia_title": "Example_Film",
            "wikidata_access_date": "2024-05-01",
        },
    )


class Route1ValidatorTests(unittest.TestCase):
    """Check Route 1 candidate and rewrite validation."""

    def test_ensure_subject_resource_prefers_wikipedia_title(self) -> None:
        candidate = make_candidate()
        ensure_route1_subject_resource(candidate)
        self.assertEqual(candidate.subject_resource_url, "https://en.wikipedia.org/wiki/Example_Film")
        self.assertEqual(candidate.subject_resource_key, candidate.subject_resource_url)

    def test_candidate_validator_accepts_label_unique_candidate(self) -> None:
        result = validate_route1_candidate(
            FakeClient(),
            Settings(target_time="2020"),
            make_candidate(),
            make_template(),
        )
        self.assertIsInstance(result, AmbiguityResolution)
        self.assertEqual(result.status, "label_unique")

    def test_candidate_validator_rejects_missing_subject_label_before_search(self) -> None:
        client = FakeClient()
        candidate = make_candidate()
        candidate.subject_label = ""
        result = validate_route1_candidate(
            client,
            Settings(target_time="2020"),
            candidate,
            make_template(),
        )
        self.assertIsInstance(result, RejectedCandidate)
        self.assertEqual(result.reason, "subject_label_missing")
        self.assertEqual(client.search_call_count, 0)

    def test_candidate_validator_rejects_qid_like_subject_label_before_search(self) -> None:
        client = FakeClient()
        candidate = make_candidate()
        candidate.subject_label = "Q130598234"
        result = validate_route1_candidate(
            client,
            Settings(target_time="2020"),
            candidate,
            make_template(),
        )
        self.assertIsInstance(result, RejectedCandidate)
        self.assertEqual(result.reason, "subject_label_qid_like")
        self.assertEqual(client.search_call_count, 0)

    def test_candidate_validator_rejects_qid_like_answer_label_before_search(self) -> None:
        client = FakeClient()
        candidate = make_candidate()
        candidate.answer_labels = ["Q42"]
        result = validate_route1_candidate(
            client,
            Settings(target_time="2020"),
            candidate,
            make_template(),
        )
        self.assertIsInstance(result, RejectedCandidate)
        self.assertEqual(result.reason, "answer_label_qid_like")
        self.assertEqual(client.search_call_count, 0)

    def test_candidate_validator_rejects_ambiguous_same_medium_candidate(self) -> None:
        result = validate_route1_candidate(
            FakeClient(
                search_results=[
                    {"id": "Q1", "label": "Example Film"},
                    {"id": "Q3", "label": "Example Film"},
                ],
                entities={
                    "Q3": {
                        "claims": {
                            "P31": [{"mainsnak": {"datavalue": {"value": {"id": "Q11424"}}}}],
                        }
                    }
                },
            ),
            Settings(target_time="2020"),
            make_candidate(),
            make_template(),
        )
        self.assertIsInstance(result, RejectedCandidate)
        self.assertEqual(result.reason, "subject_ambiguous")

    def test_rewrite_validator_allows_pre_cutoff_year(self) -> None:
        reason = validate_route1_rewritten_question(
            make_candidate(),
            ["Example Film"],
            "Who directed the 2020 film Example Film?",
            cutoff_year=2025,
        )
        self.assertIsNone(reason)

    def test_rewrite_validator_rejects_answer_leakage(self) -> None:
        reason = validate_route1_rewritten_question(
            make_candidate(),
            ["Example Film"],
            "Was Jane Doe the director of Example Film?",
            cutoff_year=2025,
        )
        self.assertEqual(reason, "rewrite_leaks_answer")

    def test_rewrite_validator_rejects_live_temporal_wording(self) -> None:
        reason = validate_route1_rewritten_question(
            make_candidate(),
            ["Example Film"],
            "Who is currently credited as director of Example Film?",
            cutoff_year=2025,
        )
        self.assertEqual(reason, "rewrite_contains_temporal_expression")


if __name__ == "__main__":
    unittest.main()
