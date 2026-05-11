"""Tests for subject-resource-level deduplication."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.config import Settings
from wikidata_simpleqa.models import AmbiguityResolution, CandidateFact, DomainTemplate
from wikidata_simpleqa.pipeline import run_pipeline_for_templates


class FakeClient:
    """Minimal client stub for pipeline dedup tests."""

    def stats_snapshot(self):
        return {"total_requests": 0, "network_requests": 0, "cache_hits": 0, "retry_count": 0, "errors": 0, "events": [], "problems": []}


def make_candidate(question_family: str, question: str) -> CandidateFact:
    """Build a minimal candidate with a fixed subject resource."""
    return CandidateFact(
        subject_qid="Q123",
        subject_label="Same Subject",
        subject_aliases=[],
        domain=question_family,
        topic="Tests",
        answer_type="Number",
        question_family=question_family,
        subject_type_qids=["Q1"],
        target_property_pid="P50",
        target_property_label="author",
        answer_qids=["VALUE:number:4"],
        answer_labels=["4"],
        answer_aliases=[],
        date_property_pid="P577",
        date_value="2026-03-01",
        target_time="2026",
        canonical_question=question,
        provenance_complete=True,
        subject_resource_url="https://en.wikipedia.org/wiki/Same_Subject",
        subject_resource_key="https://en.wikipedia.org/wiki/Same_Subject",
    )


class PipelineDedupTests(unittest.TestCase):
    """Check dataset-level deduplication on canonical subject resources."""

    def test_duplicates_same_subject_resource_across_templates(self) -> None:
        template_a = DomainTemplate(
            domain="paper_author_count",
            topic="Tests",
            answer_type="Number",
            question_family="paper_author_count",
            subject_type_qid="Q1",
            subject_type_label="article",
            date_property_pid="P577",
            target_property_pid="P50",
            target_property_label="author",
            canonical_question_template="{descriptor}",
        )
        template_b = DomainTemplate(
            domain="report_author_count",
            topic="Tests",
            answer_type="Number",
            question_family="report_author_count",
            subject_type_qid="Q1",
            subject_type_label="article",
            date_property_pid="P577",
            target_property_pid="P50",
            target_property_label="author",
            canonical_question_template="{descriptor}",
        )
        candidate_a = make_candidate("paper_author_count", "How many authors wrote Same Subject?")
        candidate_b = make_candidate(
            "report_author_count",
            "How many authors wrote the report Same Subject?",
        )

        settings = Settings(target_time="2026", pilot_total=5)
        resolution = AmbiguityResolution(
            status="label_unique",
            descriptor="Same Subject",
        )

        with (
            patch("wikidata_simpleqa.pipeline.harvest_candidates", side_effect=[[candidate_a], [candidate_b]]),
            patch("wikidata_simpleqa.pipeline._validate_candidate", return_value=resolution),
        ):
            result = run_pipeline_for_templates(
                settings=settings,
                templates=[template_a, template_b],
                client=FakeClient(),
            )

        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(len(result.rejected), 1)
        self.assertEqual(result.rejected[0]["rejection_reason"], "duplicate_subject_resource")

    def test_searches_next_candidate_when_earlier_subject_is_already_assigned(self) -> None:
        template = DomainTemplate(
            domain="album_label",
            topic="Tests",
            answer_type="Organization",
            question_family="which_label_released_album",
            subject_type_qid="Q482994",
            subject_type_label="album",
            date_property_pid="P577",
            target_property_pid="P264",
            target_property_label="record label",
            canonical_question_template="Which label released the album {descriptor}?",
        )
        duplicate_candidate = make_candidate(
            "album_label",
            "Which label released the album Same Subject?",
        )
        unique_candidate = CandidateFact(
            subject_qid="Q456",
            subject_label="Other Album",
            subject_aliases=[],
            domain="album_label",
            topic="Tests",
            answer_type="Organization",
            question_family="which_label_released_album",
            subject_type_qids=["Q482994"],
            target_property_pid="P264",
            target_property_label="record label",
            answer_qids=["Q789"],
            answer_labels=["Example Label"],
            answer_aliases=[],
            date_property_pid="P577",
            date_value="2026-03-02",
            target_time="2026",
            canonical_question="Which label released the album Other Album?",
            provenance_complete=True,
            subject_resource_url="https://en.wikipedia.org/wiki/Other_Album",
            subject_resource_key="https://en.wikipedia.org/wiki/Other_Album",
        )
        settings = Settings(target_time="2026", pilot_total=5)
        resolution = AmbiguityResolution(
            status="label_unique",
            descriptor="Other Album",
        )

        with (
            patch("wikidata_simpleqa.pipeline.harvest_candidates", return_value=[duplicate_candidate, unique_candidate]),
            patch("wikidata_simpleqa.pipeline._validate_candidate", side_effect=[resolution, resolution]),
        ):
            result = run_pipeline_for_templates(
                settings=settings,
                templates=[template],
                client=FakeClient(),
                seen_subject_resources={"https://en.wikipedia.org/wiki/Same_Subject"},
            )

        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(result.accepted[0]["subject_qid"], "Q456")


if __name__ == "__main__":
    unittest.main()
