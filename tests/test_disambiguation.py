"""Tests for strict ambiguity handling."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.ambiguity import resolve_subject_ambiguity
from wikidata_simpleqa.domain_templates import FILM_DIRECTOR_TEMPLATE, get_date_answer_pilot_templates
from wikidata_simpleqa.models import CandidateFact, DomainTemplate
from wikidata_simpleqa.validators import find_exact_name_competitors


class DisambiguationTests(unittest.TestCase):
    """Check exact normalized-label competitor detection."""

    def make_candidate(self) -> CandidateFact:
        """Build a minimal film candidate."""
        return CandidateFact(
            subject_qid="Q-film",
            subject_label="Project Hail Mary",
            subject_aliases=[],
            domain="film",
            topic="Arts and Media",
            answer_type="Person",
            question_family="who_directed_film",
            subject_type_qids=["Q11424"],
            target_property_pid="P57",
            target_property_label="director",
            answer_qids=["Q-director"],
            answer_labels=["Director"],
            answer_aliases=[],
            date_property_pid="P577",
            date_value="2026-03-01",
            target_time="2026",
            canonical_question="",
        )

    def test_finds_book_film_same_title_collision(self) -> None:
        competitors = find_exact_name_competitors(
            subject_qid="Q-film",
            subject_label="Project Hail Mary",
            search_results=[
                {"id": "Q-film", "label": "Project Hail Mary"},
                {"id": "Q-book", "label": "Project Hail Mary"},
                {"id": "Q-other", "label": "Different Title"},
            ],
        )
        self.assertEqual(competitors, ["Q-book"])

    def test_resolves_cross_media_collision_with_medium_descriptor(self) -> None:
        resolution = resolve_subject_ambiguity(
            candidate=self.make_candidate(),
            template=FILM_DIRECTOR_TEMPLATE,
            competitor_entities={
                "Q-book": {
                    "claims": {
                        "P31": [
                            {
                                "mainsnak": {
                                    "datavalue": {
                                        "value": {"id": "Q571"}
                                    }
                                }
                            }
                        ]
                    }
                }
            },
        )
        self.assertIsNotNone(resolution)
        assert resolution is not None
        self.assertEqual(resolution.status, "resolved_by_non_temporal_descriptor")
        self.assertEqual(resolution.signature, ["film"])

    def test_rejects_same_medium_collision(self) -> None:
        resolution = resolve_subject_ambiguity(
            candidate=self.make_candidate(),
            template=FILM_DIRECTOR_TEMPLATE,
            competitor_entities={
                "Q-other-film": {
                    "claims": {
                        "P31": [
                            {
                                "mainsnak": {
                                    "datavalue": {
                                        "value": {"id": "Q11424"}
                                    }
                                }
                            }
                        ]
                    }
                }
            },
        )
        self.assertIsNone(resolution)

    def test_same_medium_collision_can_use_safe_location_descriptor(self) -> None:
        terminal_template = next(
            template
            for template in get_date_answer_pilot_templates()
            if template.domain == "terminal_opening_date"
        )
        candidate = CandidateFact(
            subject_qid="Q-station",
            subject_label="Haga station",
            subject_aliases=[],
            domain=terminal_template.domain,
            topic=terminal_template.topic,
            answer_type=terminal_template.answer_type,
            question_family=terminal_template.question_family,
            subject_type_qids=["Q55488"],
            target_property_pid="P571",
            target_property_label="inception",
            answer_qids=["VALUE:date:2026-01-01"],
            answer_labels=["1 January 2026"],
            answer_aliases=["2026-01-01"],
            date_property_pid="P571",
            date_value="2026-01-01",
            target_time="2026",
            canonical_question="",
            source_metadata={
                "subject_location_labels": ["Gothenburg Municipality"],
                "answer_subdivision_labels": [],
            },
        )
        resolution = resolve_subject_ambiguity(
            candidate=candidate,
            template=terminal_template,
            competitor_entities={
                "Q-other-station": {
                    "claims": {
                        "P31": [
                            {
                                "mainsnak": {
                                    "datavalue": {
                                        "value": {"id": "Q55488"}
                                    }
                                }
                            }
                        ]
                    }
                }
            },
        )
        self.assertIsNotNone(resolution)
        assert resolution is not None
        self.assertEqual(
            resolution.descriptor,
            "Haga station in Gothenburg Municipality",
        )

    def test_country_questions_do_not_use_location_descriptor_for_same_medium_collision(self) -> None:
        country_template = DomainTemplate(
            domain="rail_station_country",
            topic="Architecture and Transportation",
            answer_type="Place",
            question_family="which_country_station_located",
            subject_type_qid="Q55488",
            subject_type_label="railway station",
            date_property_pid="P571",
            target_property_pid="P17",
            target_property_label="country",
            canonical_question_template="In which country is the railway station {descriptor} located?",
        )
        candidate = CandidateFact(
            subject_qid="Q-station",
            subject_label="Haga station",
            subject_aliases=[],
            domain=country_template.domain,
            topic=country_template.topic,
            answer_type=country_template.answer_type,
            question_family=country_template.question_family,
            subject_type_qids=["Q55488"],
            target_property_pid="P17",
            target_property_label="country",
            answer_qids=["Q34"],
            answer_labels=["Sweden"],
            answer_aliases=[],
            date_property_pid="P571",
            date_value="2026-01-01",
            target_time="2026",
            canonical_question="",
            source_metadata={
                "subject_location_labels": ["Gothenburg Municipality"],
                "answer_subdivision_labels": ["Västra Götaland County"],
            },
        )
        resolution = resolve_subject_ambiguity(
            candidate=candidate,
            template=country_template,
            competitor_entities={
                "Q-other-station": {
                    "claims": {
                        "P31": [
                            {
                                "mainsnak": {
                                    "datavalue": {
                                        "value": {"id": "Q55488"}
                                    }
                                }
                            }
                        ]
                    }
                }
            },
        )
        self.assertIsNone(resolution)

    def test_matches_parenthetical_disambiguation_after_normalization(self) -> None:
        competitors = find_exact_name_competitors(
            subject_qid="Q1",
            subject_label="Stitch Head",
            search_results=[
                {"id": "Q2", "label": "Stitch Head (film)"},
                {"id": "Q3", "label": "Stitch Head"},
            ],
        )
        self.assertEqual(competitors, ["Q2", "Q3"])

    def test_ignores_non_matching_labels(self) -> None:
        competitors = find_exact_name_competitors(
            subject_qid="Q1",
            subject_label="Alpha",
            search_results=[
                {"id": "Q2", "label": "Alpha Beta"},
                {"id": "Q3", "label": "Beta"},
            ],
        )
        self.assertEqual(competitors, [])


if __name__ == "__main__":
    unittest.main()
