"""Tests for Route 4 Wikidata two-hop composition."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.models import CandidateFact, DomainTemplate
from wikidata_simpleqa.route4_two_hop import (
    CLUE_HIDDEN_OBJECT,
    CLUE_HIDDEN_SUBJECT,
    HIDDEN_ENTITY_REASONING_STYLE,
    Route4TwoHopComposer,
    attach_route4_two_hop_seed_metadata,
)
from wikidata_simpleqa.validators import (
    question_leaks_bridge_entities,
    question_requires_all_hops,
    reasoning_path_is_connected,
)


def make_template(
    key: str,
    *,
    property_pid: str,
    property_label: str,
    answer_type: str = "Person",
    subject_type_label: str = "film",
) -> DomainTemplate:
    """Build a minimal single-hop template."""
    return DomainTemplate(
        domain=key,
        topic="Arts and Media",
        answer_type=answer_type,
        question_family=key,
        subject_type_qid="Q11424",
        subject_type_label=subject_type_label,
        date_property_pid="P577",
        target_property_pid=property_pid,
        target_property_label=property_label,
        canonical_question_template="What is {descriptor}?",
    )


def make_fact(
    *,
    template: DomainTemplate,
    subject_qid: str,
    subject_label: str,
    answer_qid: str,
    answer_label: str,
) -> CandidateFact:
    """Build a validated-looking single-hop fact."""
    return CandidateFact(
        subject_qid=subject_qid,
        subject_label=subject_label,
        subject_aliases=[subject_label + " alias"],
        domain=template.template_key,
        topic=template.topic,
        answer_type=template.answer_type,
        question_family=template.question_family,
        subject_type_qids=[template.subject_type_qid],
        target_property_pid=template.target_property_pid,
        target_property_label=template.target_property_label,
        answer_qids=[answer_qid],
        answer_labels=[answer_label],
        answer_aliases=[],
        date_property_pid=template.date_property_pid,
        date_value="2020-01-01",
        target_time="2020",
        canonical_question="single-hop question not used",
        ambiguity_status="label_unique",
        reasoning_style="single_fact",
        hop_count=1,
        reasoning_path=[
            {
                "source_qid": subject_qid,
                "source_label": subject_label,
                "property_pid": template.target_property_pid,
                "property_label": template.target_property_label,
                "target_qid": answer_qid,
                "target_label": answer_label,
                "role": "answer",
            }
        ],
        derivation_signature={"style": "single_fact"},
        provenance_complete=True,
        subject_resource_url=f"https://www.wikidata.org/wiki/{subject_qid}",
        subject_resource_key=f"https://www.wikidata.org/wiki/{subject_qid}",
        source_metadata={
            "wikidata_access_date": "2024-05-01",
            "question_format_args": {"subject_kind": template.subject_type_label},
        },
    )


class Route4TwoHopTests(unittest.TestCase):
    """Check hidden-entity composition semantics."""

    def test_composes_subject_oriented_clue(self) -> None:
        director = make_template("film_director", property_pid="P57", property_label="director")
        based_on = make_template("film_based_on", property_pid="P144", property_label="based on", answer_type="Other")
        answer_hop = make_fact(
            template=director,
            subject_qid="Q-film",
            subject_label="Example Film",
            answer_qid="Q-director",
            answer_label="Jane Director",
        )
        clue_hop = make_fact(
            template=based_on,
            subject_qid="Q-film",
            subject_label="Example Film",
            answer_qid="Q-book",
            answer_label="Example Book",
        )

        composed = Route4TwoHopComposer().compose(
            {
                director.template_key: [answer_hop],
                based_on.template_key: [clue_hop],
            },
            {
                director.template_key: director,
                based_on.template_key: based_on,
            },
        )

        candidate = next(item for item in composed if item.target_property_pid == "P57")
        self.assertEqual(candidate.answer_labels, ["Jane Director"])
        self.assertEqual(candidate.reasoning_style, HIDDEN_ENTITY_REASONING_STYLE)
        self.assertEqual(candidate.source_metadata["clue_orientation"], CLUE_HIDDEN_SUBJECT)
        self.assertIn("Example Book", candidate.canonical_question)
        self.assertNotIn("Example Film", candidate.canonical_question)
        self.assertTrue(reasoning_path_is_connected(candidate))

    def test_composes_object_oriented_clue(self) -> None:
        director = make_template("film_director", property_pid="P57", property_label="director")
        producer = make_template("studio_produced_film", property_pid="P272", property_label="production company", answer_type="Other", subject_type_label="studio")
        answer_hop = make_fact(
            template=director,
            subject_qid="Q-film",
            subject_label="Example Film",
            answer_qid="Q-director",
            answer_label="Jane Director",
        )
        clue_hop = make_fact(
            template=producer,
            subject_qid="Q-studio",
            subject_label="Example Studio",
            answer_qid="Q-film",
            answer_label="Example Film",
        )

        composed = Route4TwoHopComposer().compose(
            {
                director.template_key: [answer_hop],
                producer.template_key: [clue_hop],
            },
            {
                director.template_key: director,
                producer.template_key: producer,
            },
        )

        self.assertEqual(len(composed), 1)
        self.assertEqual(composed[0].source_metadata["clue_orientation"], CLUE_HIDDEN_OBJECT)
        self.assertIn("Example Studio", composed[0].canonical_question)
        self.assertTrue(reasoning_path_is_connected(composed[0]))

    def test_duplicate_clue_path_prunes_ambiguous_hidden_entities(self) -> None:
        director = make_template("film_director", property_pid="P57", property_label="director")
        based_on = make_template("film_based_on", property_pid="P144", property_label="based on", answer_type="Other")
        answer_hop_a = make_fact(template=director, subject_qid="Q-film-a", subject_label="Film A", answer_qid="Q-dir-a", answer_label="Director A")
        answer_hop_b = make_fact(template=director, subject_qid="Q-film-b", subject_label="Film B", answer_qid="Q-dir-b", answer_label="Director B")
        clue_hop_a = make_fact(template=based_on, subject_qid="Q-film-a", subject_label="Film A", answer_qid="Q-book", answer_label="Shared Book")
        clue_hop_b = make_fact(template=based_on, subject_qid="Q-film-b", subject_label="Film B", answer_qid="Q-book", answer_label="Shared Book")

        composed = Route4TwoHopComposer().compose(
            {
                director.template_key: [answer_hop_a, answer_hop_b],
                based_on.template_key: [clue_hop_a, clue_hop_b],
            },
            {
                director.template_key: director,
                based_on.template_key: based_on,
            },
        )

        director_answer_candidates = [
            candidate
            for candidate in composed
            if candidate.target_property_pid == "P57"
        ]
        self.assertEqual(director_answer_candidates, [])

    def test_hidden_entity_leakage_and_required_clues(self) -> None:
        director = make_template("film_director", property_pid="P57", property_label="director")
        based_on = make_template("film_based_on", property_pid="P144", property_label="based on", answer_type="Other")
        candidate = Route4TwoHopComposer().compose(
            {
                director.template_key: [
                    make_fact(template=director, subject_qid="Q-film", subject_label="Example Film", answer_qid="Q-director", answer_label="Jane Director")
                ],
                based_on.template_key: [
                    make_fact(template=based_on, subject_qid="Q-film", subject_label="Example Film", answer_qid="Q-book", answer_label="Example Book")
                ],
            },
            {
                director.template_key: director,
                based_on.template_key: based_on,
            },
        )[0]
        attach_route4_two_hop_seed_metadata(candidate)

        self.assertTrue(
            question_leaks_bridge_entities(
                "Who directed Example Film, which was based on Example Book?",
                candidate,
            )
        )
        self.assertFalse(
            question_leaks_bridge_entities(
                "Who directed the film that was based on Example Book?",
                candidate,
            )
        )
        self.assertFalse(question_requires_all_hops(candidate, "Who directed the film?"))
        self.assertTrue(question_requires_all_hops(candidate, "Who directed the film that was based on Example Book?"))


if __name__ == "__main__":
    unittest.main()
