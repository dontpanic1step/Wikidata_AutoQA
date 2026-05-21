"""Tests for Route 1 and Route 2 candidate generators."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.config import Settings
from wikidata_simpleqa.generators import (
    WikidataHiddenEntityTwoHopGenerator,
    WikidataLightGenerator,
    WikidataMultiHopJoinGenerator,
    WikidataWikipediaHybridGenerator,
)
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


def make_multihop_template() -> DomainTemplate:
    """Build a minimal multi-hop join template."""
    return DomainTemplate(
        domain="film_source_work_author",
        topic="Arts and Media",
        answer_type="Person",
        question_family="who_wrote_source_work_for_film",
        subject_type_qid="Q11424",
        subject_type_label="film",
        date_property_pid="P577",
        target_property_pid="COMPOSED_SOURCE_WORK_AUTHOR",
        target_property_label="author of source work",
        canonical_question_template="Who wrote the work that the film {descriptor} was based on?",
        composition_style="fact_join",
        reasoning_style="multi_hop_join",
        reasoning_recipe={"required_reasoning_clues": ["based on"]},
    )


def make_multihop_candidate() -> CandidateFact:
    """Build a minimal Route 1 multi-hop join candidate."""
    return CandidateFact(
        subject_qid="Q10",
        subject_label="Example Film",
        subject_aliases=[],
        domain="film_source_work_author",
        topic="Arts and Media",
        answer_type="Person",
        question_family="who_wrote_source_work_for_film",
        subject_type_qids=["Q11424"],
        target_property_pid="COMPOSED_SOURCE_WORK_AUTHOR",
        target_property_label="author of source work",
        answer_qids=["Q12"],
        answer_labels=["Author A"],
        answer_aliases=[],
        date_property_pid="P577",
        date_value="2020-01-01",
        target_time="2020",
        canonical_question="",
        reasoning_style="multi_hop_join",
        hop_count=2,
        reasoning_path=[
            {
                "source_qid": "Q10",
                "source_label": "Example Film",
                "property_pid": "P144",
                "property_label": "based on",
                "target_qid": "Q11",
                "target_label": "Source Work",
                "role": "bridge",
            },
            {
                "source_qid": "Q11",
                "source_label": "Source Work",
                "property_pid": "P50",
                "property_label": "author",
                "target_qid": "Q12",
                "target_label": "Author A",
                "role": "answer",
            },
        ],
        bridge_entities=[{"qid": "Q11", "label": "Source Work", "role": "source_work"}],
        derivation_signature={"style": "multi_hop_join", "rule": "film_source_work_author"},
        provenance_complete=True,
        source_metadata={
            "required_reasoning_clues": ["based on"],
            "multi_hop_unique": True,
            "wikidata_access_date": "2024-05-01",
        },
        subject_resource_url="https://www.wikidata.org/wiki/Q10",
        subject_resource_key="https://www.wikidata.org/wiki/Q10",
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

    def test_route1_multihop_join_emits_qid_seeded_shared_candidate(self) -> None:
        template = make_multihop_template()
        candidate = make_multihop_candidate()
        resolution = AmbiguityResolution(
            status="label_unique",
            descriptor="Example Film",
        )
        with (
            patch("wikidata_simpleqa.generators.harvest_candidates", return_value=[candidate]),
            patch("wikidata_simpleqa.generators.validate_route1_candidate", return_value=resolution),
        ):
            generated = WikidataMultiHopJoinGenerator().generate(
                templates=[template],
                settings=Settings(target_time="2020"),
                client=FakeClient(),
            )

        self.assertEqual(len(generated), 1)
        self.assertEqual(generated[0].generation_route, "route1_wikidata_multihop_join")
        self.assertEqual(generated[0].source_metadata["route1_qid_seed_unit"]["subject_qid"], "Q10")
        self.assertIn("Example Film -- based on -- Source Work", generated[0].evidence.text)
        self.assertEqual(generated[0].source_candidate.reasoning_style, "multi_hop_join")

    def test_route4_two_hop_emits_composed_candidate(self) -> None:
        answer_template = make_template()
        clue_template = DomainTemplate(
            domain="film_based_on",
            topic="Arts and Media",
            answer_type="Other",
            question_family="what_film_based_on",
            subject_type_qid="Q11424",
            subject_type_label="film",
            date_property_pid="P577",
            target_property_pid="P144",
            target_property_label="based on",
            canonical_question_template="What was {descriptor} based on?",
        )
        answer_candidate = make_candidate()
        clue_candidate = make_candidate()
        clue_candidate.domain = clue_template.template_key
        clue_candidate.answer_type = "Other"
        clue_candidate.target_property_pid = "P144"
        clue_candidate.target_property_label = "based on"
        clue_candidate.answer_qids = ["Q3"]
        clue_candidate.answer_labels = ["Example Book"]
        clue_candidate.answer_aliases = []
        clue_candidate.provenance_complete = True
        resolution = AmbiguityResolution(status="label_unique", descriptor="Example Film")

        def fake_harvest(*, template, **_kwargs):
            if template.template_key == answer_template.template_key:
                return [answer_candidate]
            if template.template_key == clue_template.template_key:
                return [clue_candidate]
            return []

        with (
            patch("wikidata_simpleqa.generators.harvest_candidates", side_effect=fake_harvest),
            patch("wikidata_simpleqa.generators.validate_route1_candidate", return_value=resolution),
        ):
            generated = WikidataHiddenEntityTwoHopGenerator().generate(
                templates=[answer_template, clue_template],
                settings=Settings(target_time="2020"),
                client=FakeClient(),
            )

        director_candidate = next(item for item in generated if item.relation_or_claim == "director")
        self.assertEqual(director_candidate.generation_route, "route4_wikidata_two_hop")
        self.assertEqual(director_candidate.answer, "Jane Doe")
        self.assertEqual(director_candidate.source_candidate.reasoning_style, "multi_hop_hidden_entity")
        self.assertIn("Example Book", director_candidate.question)
        self.assertNotIn("Example Film", director_candidate.question)


if __name__ == "__main__":
    unittest.main()
