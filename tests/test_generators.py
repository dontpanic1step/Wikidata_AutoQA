"""Tests for Route 1 and Route 2 candidate generators."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.config import Settings
from wikidata_simpleqa.generators import WikidataLightGenerator, WikidataWikipediaHybridGenerator
from wikidata_simpleqa.models import AmbiguityResolution, CandidateFact, DomainTemplate


class FakeWikipediaClient:
    """Minimal summary client for generator tests."""

    def fetch_summary(self, title: str) -> dict:
        return {
            "title": title.replace("_", " "),
            "extract": "Example Film is a 2020 drama film directed by Jane Doe.",
            "content_urls": {
                "desktop": {
                    "page": "https://en.wikipedia.org/wiki/Example_Film",
                }
            },
        }


class FakeClient:
    """Minimal Wikidata client stub for generator tests."""

    def search_entities(self, query: str, limit: int = 10):
        return []


def make_template() -> DomainTemplate:
    """Build a minimal single-hop template."""
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
    """Build a minimal harvested candidate with Wikipedia metadata."""
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
        canonical_question="",
        provenance_complete=True,
        source_metadata={
            "question_format_args": {"subject_kind": "film"},
            "subject_wikipedia_title": "Example_Film",
            "subject_wikipedia_url": "https://en.wikipedia.org/wiki/Example_Film",
            "subject_sitelink_count": 12,
            "subject_claim_count": 44,
            "wikidata_access_date": "2024-05-01",
        },
        subject_resource_url="https://en.wikipedia.org/wiki/Example_Film",
        subject_resource_key="https://en.wikipedia.org/wiki/Example_Film",
    )


class GeneratorTests(unittest.TestCase):
    """Check generator output contracts for the first two routes."""

    def test_route1_emits_shared_candidate(self) -> None:
        template = make_template()
        candidate = make_candidate()
        resolution = AmbiguityResolution(
            status="label_unique",
            descriptor="Example Film",
        )
        with (
            patch("wikidata_simpleqa.generators.harvest_candidates", return_value=[candidate]),
            patch("wikidata_simpleqa.generators.validate_route1_candidate", return_value=resolution),
        ):
            generated = WikidataLightGenerator().generate(
                templates=[template],
                settings=Settings(target_time="2020"),
                client=FakeClient(),
            )
        self.assertEqual(len(generated), 1)
        self.assertEqual(generated[0].generation_route, "route1_wikidata_light")
        self.assertEqual(generated[0].answer, "Jane Doe")
        self.assertIn("Example Film", generated[0].evidence.text)

    def test_route2_uses_wikipedia_evidence_and_subject_kind_override(self) -> None:
        template = make_template()
        candidate = make_candidate()
        resolution = AmbiguityResolution(
            status="label_unique",
            descriptor="Example Film",
        )
        with (
            patch("wikidata_simpleqa.generators.harvest_candidates", return_value=[candidate]),
            patch("wikidata_simpleqa.generators.validate_route1_candidate", return_value=resolution),
        ):
            generated = WikidataWikipediaHybridGenerator(
                wikipedia_client=FakeWikipediaClient()
            ).generate(
                templates=[template],
                settings=Settings(target_time="2020"),
                client=FakeClient(),
            )
        self.assertEqual(len(generated), 1)
        self.assertEqual(generated[0].generation_route, "route2_wikidata_wikipedia_hybrid")
        self.assertIn("directed by Jane Doe", generated[0].evidence.text)
        self.assertIn("drama film", generated[0].question)


if __name__ == "__main__":
    unittest.main()
