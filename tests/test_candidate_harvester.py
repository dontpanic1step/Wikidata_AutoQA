"""Tests for candidate hydration helpers."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.candidate_harvester import _extract_label, _select_label, _select_subject_kind
from wikidata_simpleqa.models import DomainTemplate


class CandidateHarvesterTests(unittest.TestCase):
    """Check small label-cleanup behaviors."""

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
        subject_kind = _select_subject_kind(template, ["Antal Türr", "company"])
        self.assertEqual(subject_kind, "company")


if __name__ == "__main__":
    unittest.main()
