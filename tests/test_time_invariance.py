"""Tests for time-invariance checks."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.models import CandidateFact
from wikidata_simpleqa.validators import candidate_is_time_invariant, question_targets_mutable_fact


def make_candidate(
    *,
    target_property_pid: str = "P57",
    date_value: str = "2026-02-19",
    source_metadata: dict | None = None,
    reasoning_path: list[dict] | None = None,
    reasoning_style: str = "single_fact",
) -> CandidateFact:
    """Build a minimal candidate for validator tests."""
    return CandidateFact(
        subject_qid="Q1",
        subject_label="Example",
        subject_aliases=[],
        domain="film",
        topic="Arts and Media",
        answer_type="Person",
        question_family="who_directed_film",
        subject_type_qids=["Q11424"],
        target_property_pid=target_property_pid,
        target_property_label="director",
        answer_qids=["Q2"],
        answer_labels=["Example Answer"],
        answer_aliases=[],
        date_property_pid="P577",
        date_value=date_value,
        target_time="2026",
        canonical_question="Who directed the film Example?",
        source_metadata=source_metadata or {},
        reasoning_path=reasoning_path or [],
        reasoning_style=reasoning_style,
    )


class TimeInvarianceTests(unittest.TestCase):
    """Check settled-fact and mutable-fact behavior."""

    def test_allows_settled_released_film_director(self) -> None:
        candidate = make_candidate()
        self.assertTrue(candidate_is_time_invariant(candidate, "2026-05-05"))

    def test_rejects_future_dated_candidate(self) -> None:
        candidate = make_candidate(date_value="2026-12-01")
        self.assertFalse(candidate_is_time_invariant(candidate, "2026-05-05"))

    def test_allows_short_year_settled_candidate_date(self) -> None:
        candidate = make_candidate(date_value="924-03-03")
        self.assertTrue(candidate_is_time_invariant(candidate, "2026-05-05"))

    def test_allows_bc_settled_candidate_date(self) -> None:
        candidate = make_candidate(date_value="-200-03-03")
        self.assertTrue(candidate_is_time_invariant(candidate, "2026-05-05"))

    def test_rejects_mutable_relationship_property(self) -> None:
        candidate = make_candidate(target_property_pid="P26")
        self.assertFalse(candidate_is_time_invariant(candidate, "2026-05-05"))

    def test_rejects_employer_property(self) -> None:
        candidate = make_candidate(target_property_pid="P108")
        self.assertFalse(candidate_is_time_invariant(candidate, "2026-05-05"))

    def test_allows_historically_settled_spouse_slice(self) -> None:
        candidate = make_candidate(
            target_property_pid="P26",
            source_metadata={
                "time_invariance": {
                    "historically_settled": True,
                    "history_complete": True,
                    "allowed_property_pids": ["P26"],
                }
            },
        )
        self.assertTrue(candidate_is_time_invariant(candidate, "2026-05-05"))

    def test_allows_historically_settled_goal_slice(self) -> None:
        candidate = make_candidate(
            target_property_pid="COMPOSED_ORDINAL_TOURNAMENT_GOALS",
            reasoning_style="multi_hop_ordinal",
            reasoning_path=[
                {"property_pid": "P1344"},
                {"property_pid": "DERIVED_PARTICIPATION_EDITION"},
                {"property_pid": "P1351"},
            ],
            source_metadata={
                "time_invariance": {
                    "historically_settled": True,
                    "history_complete": True,
                    "allowed_property_pids": ["P1351"],
                },
                "ordinal_metadata": {
                    "series_history_complete": True,
                    "descriptor": "Example Cup",
                },
            },
        )
        self.assertTrue(candidate_is_time_invariant(candidate, "2026-05-05"))

    def test_rejects_current_role_wording(self) -> None:
        self.assertTrue(question_targets_mutable_fact("Who is the current CEO of X?"))

    def test_rejects_relationship_wording(self) -> None:
        self.assertTrue(question_targets_mutable_fact("Who is X married to?"))

    def test_rejects_cumulative_statistic_wording(self) -> None:
        self.assertTrue(question_targets_mutable_fact("How many career goals has X scored?"))

    def test_allows_ordinal_spouse_wording(self) -> None:
        self.assertFalse(question_targets_mutable_fact("Who was the first spouse of X?"))

    def test_allows_completed_edition_goal_wording(self) -> None:
        self.assertFalse(
            question_targets_mutable_fact(
                "How many goals did X score in the 2nd edition of Example Cup?"
            )
        )

    def test_allows_stable_authorship_wording(self) -> None:
        self.assertFalse(question_targets_mutable_fact("Who wrote the novel X?"))


if __name__ == "__main__":
    unittest.main()
