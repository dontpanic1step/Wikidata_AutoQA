"""Tests for subject-kind rendering in canonical questions."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.canonical_questions import build_canonical_question
from wikidata_simpleqa.domain_templates import get_template_by_domain
from wikidata_simpleqa.models import CandidateFact


class SubjectKindTests(unittest.TestCase):
    """Check that canonical questions can use specific subject kinds."""

    def test_uses_specific_subject_kind_when_available(self) -> None:
        template = get_template_by_domain("artwork_creator")
        assert template is not None
        candidate = CandidateFact(
            subject_qid="Q1",
            subject_label="Souvenir",
            subject_aliases=[],
            domain="artwork_creator",
            topic="Arts and Media",
            answer_type="Person",
            question_family="who_created_artwork",
            subject_type_qids=["Q838948", "Q219423"],
            target_property_pid="P170",
            target_property_label="creator",
            answer_qids=["Q2"],
            answer_labels=["NEVERCREW"],
            answer_aliases=[],
            date_property_pid="P571",
            date_value="2026-01-01",
            target_time="2026",
            canonical_question="",
            source_metadata={"question_format_args": {"subject_kind": "mural"}},
        )
        question = build_canonical_question(candidate, template)
        self.assertEqual(question, "Who created the mural Souvenir?")

    def test_falls_back_to_template_subject_kind(self) -> None:
        template = get_template_by_domain("film_director")
        assert template is not None
        candidate = CandidateFact(
            subject_qid="Q1",
            subject_label="Project Hail Mary",
            subject_aliases=[],
            domain="film_director",
            topic="Arts and Media",
            answer_type="Person",
            question_family="who_directed_film",
            subject_type_qids=["Q11424"],
            target_property_pid="P57",
            target_property_label="director",
            answer_qids=["Q2"],
            answer_labels=["Director"],
            answer_aliases=[],
            date_property_pid="P577",
            date_value="2026-03-01",
            target_time="2026",
            canonical_question="",
        )
        question = build_canonical_question(candidate, template)
        self.assertEqual(question, "Who directed the film Project Hail Mary?")


if __name__ == "__main__":
    unittest.main()
