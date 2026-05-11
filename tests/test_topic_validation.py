"""Tests for deterministic template topic validation."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.models import CandidateFact, DomainTemplate
from wikidata_simpleqa.validators import candidate_matches_topic_constraints


class TopicValidationTests(unittest.TestCase):
    """Check template topic gates based on deterministic metadata."""

    def test_accepts_candidate_when_main_subject_matches_required_topic(self) -> None:
        template = DomainTemplate(
            domain="paper_conference_ai",
            topic="Computer Science and AI",
            answer_type="Organization",
            question_family="which_conference_published_ai_paper",
            subject_type_qid="Q13442814",
            subject_type_label="scholarly article",
            date_property_pid="P577",
            target_property_pid="P1433",
            target_property_label="published in",
            canonical_question_template="At which venue was the AI paper {descriptor} published?",
            required_topic_keywords=["artificial intelligence", "machine learning"],
        )
        candidate = CandidateFact(
            subject_qid="Q1",
            subject_label="Example AI Paper",
            subject_aliases=[],
            domain=template.domain,
            topic=template.topic,
            answer_type=template.answer_type,
            question_family=template.question_family,
            subject_type_qids=["Q13442814"],
            target_property_pid=template.target_property_pid,
            target_property_label=template.target_property_label,
            answer_qids=["Q2"],
            answer_labels=["Example Venue"],
            answer_aliases=[],
            date_property_pid=template.date_property_pid,
            date_value="2026-01-01",
            target_time="2026",
            canonical_question="",
            source_metadata={
                "subject_description": "scholarly article about artificial intelligence safety",
                "subject_main_subject_labels": ["artificial intelligence"],
            },
        )
        self.assertTrue(candidate_matches_topic_constraints(candidate, template))

    def test_rejects_candidate_when_required_topic_is_missing(self) -> None:
        template = DomainTemplate(
            domain="biology_article_journal",
            topic="Life Sciences",
            answer_type="Organization",
            question_family="which_journal_published_biology_article",
            subject_type_qid="Q13442814",
            subject_type_label="scholarly article",
            date_property_pid="P577",
            target_property_pid="P1433",
            target_property_label="published in",
            canonical_question_template="In which journal was the biology article {descriptor} published?",
            required_topic_keywords=["biology", "genetics"],
        )
        candidate = CandidateFact(
            subject_qid="Q1",
            subject_label="Library Social Work: The Overlooked Macro Practice Opportunity",
            subject_aliases=[],
            domain=template.domain,
            topic=template.topic,
            answer_type=template.answer_type,
            question_family=template.question_family,
            subject_type_qids=["Q13442814"],
            target_property_pid=template.target_property_pid,
            target_property_label=template.target_property_label,
            answer_qids=["Q2"],
            answer_labels=["Example Journal"],
            answer_aliases=[],
            date_property_pid=template.date_property_pid,
            date_value="2026-01-01",
            target_time="2026",
            canonical_question="",
            source_metadata={
                "subject_description": "article on social work in libraries",
                "subject_main_subject_labels": ["social work", "library science"],
            },
        )
        self.assertFalse(candidate_matches_topic_constraints(candidate, template))


if __name__ == "__main__":
    unittest.main()
