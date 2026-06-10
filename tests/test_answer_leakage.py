"""Tests for answer-leakage detection."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.models import CandidateFact
from wikidata_simpleqa.validators import question_leaks_answer, question_leaks_location_answer_context


class AnswerLeakageTests(unittest.TestCase):
    """Check whether questions reveal the answer."""

    def make_country_candidate(self) -> CandidateFact:
        """Build a minimal country-answer candidate."""
        return CandidateFact(
            subject_qid="Q1",
            subject_label="Football Museum of Wales and Wrexham Museum",
            subject_aliases=[],
            domain="museum_country",
            topic="Society and Culture",
            answer_type="Place",
            question_family="which_country_museum_located",
            subject_type_qids=["Q33506"],
            target_property_pid="P17",
            target_property_label="country",
            answer_qids=["Q145"],
            answer_labels=["United Kingdom"],
            answer_aliases=["the UK"],
            date_property_pid="P571",
            date_value="2026-01-01",
            target_time="2026",
            canonical_question="In which country is the museum Football Museum of Wales and Wrexham Museum located?",
            source_metadata={
                "subject_location_labels": ["Wrexham"],
                "answer_subdivision_labels": ["Wales", "England", "Scotland"],
            },
        )

    def test_rejects_journal_name_leakage(self) -> None:
        question = "In which journal was the Nature article X published?"
        self.assertTrue(question_leaks_answer(question, ["Nature"]))

    def test_rejects_author_name_leakage(self) -> None:
        question = "Who wrote Andy Weir's novel Project Hail Mary?"
        self.assertTrue(question_leaks_answer(question, ["Andy Weir"]))

    def test_allows_non_leaking_question(self) -> None:
        question = "Who directed the film Stitch Head?"
        self.assertFalse(question_leaks_answer(question, ["Steve Hudson"]))

    def test_ignores_blank_or_punctuation_only_answers(self) -> None:
        question = "Who directed the film Stitch Head?"
        self.assertFalse(question_leaks_answer(question, ["...", ""]))

    def test_rejects_country_demonym_answer_leakage(self) -> None:
        self.assertTrue(
            question_leaks_answer(
                "Which writer from Norway wrote the novel?",
                ["Norwegian"],
            )
        )
        self.assertTrue(
            question_leaks_answer(
                "Which Norwegian writer wrote the novel?",
                ["Norway"],
            )
        )

    def test_rejects_country_city_answer_leakage(self) -> None:
        self.assertTrue(
            question_leaks_answer(
                "Which country is New York in?",
                ["United States"],
            )
        )
        self.assertTrue(
            question_leaks_answer(
                "Which city in China hosted the exhibition?",
                ["Shanghai"],
            )
        )
        self.assertTrue(
            question_leaks_answer(
                "Which city in the US hosted the exhibition?",
                ["New York"],
            )
        )

    def test_rejects_country_question_when_subject_title_mentions_subdivision(self) -> None:
        candidate = self.make_country_candidate()
        self.assertTrue(question_leaks_location_answer_context(candidate.canonical_question, candidate))

    def test_allows_country_question_without_leaking_location_context(self) -> None:
        candidate = self.make_country_candidate()
        candidate.canonical_question = "In which country is the museum Shikoku History Museum located?"
        self.assertFalse(question_leaks_location_answer_context(candidate.canonical_question, candidate))

    def test_rejects_country_question_when_title_contains_city_token(self) -> None:
        candidate = CandidateFact(
            subject_qid="Q3312744",
            subject_label="Sea Life London Aquarium",
            subject_aliases=[],
            domain="new_park_country",
            topic="Geography",
            answer_type="Place",
            question_family="which_country_park_located",
            subject_type_qids=["Q22698"],
            target_property_pid="P17",
            target_property_label="country",
            answer_qids=["Q145"],
            answer_labels=["United Kingdom"],
            answer_aliases=["the UK"],
            date_property_pid="P571",
            date_value="2026-03-01",
            target_time="2026",
            canonical_question="In which country is the park Sea Life London Aquarium located?",
            source_metadata={
                "subject_location_labels": ["London Borough of Lambeth"],
                "answer_subdivision_labels": ["England", "Scotland", "Wales"],
            },
        )
        self.assertTrue(question_leaks_location_answer_context(candidate.canonical_question, candidate))


if __name__ == "__main__":
    unittest.main()
