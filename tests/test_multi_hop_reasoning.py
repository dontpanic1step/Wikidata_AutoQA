"""Tests for compositional multi-hop provenance behavior."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.models import CandidateFact
from wikidata_simpleqa.reasoning import build_reasoning_hop
from wikidata_simpleqa.validators import (
    answer_is_unique,
    ordinal_candidate_is_safe,
    question_leaks_bridge_entities,
    question_requires_all_hops,
    reasoning_path_is_connected,
    reasoning_path_is_temporally_safe,
    reasoning_provenance_is_complete,
    shortcut_check,
)


def make_multi_hop_candidate() -> CandidateFact:
    """Build a minimal connected multi-hop candidate."""
    return CandidateFact(
        subject_qid="Q-film",
        subject_label="Example Film",
        subject_aliases=[],
        domain="film_source_work_author",
        topic="Arts and Media",
        answer_type="Person",
        question_family="who_wrote_source_work_for_film",
        subject_type_qids=["Q11424"],
        target_property_pid="COMPOSED_SOURCE_WORK_AUTHOR",
        target_property_label="author of source work",
        answer_qids=["Q-author"],
        answer_labels=["Example Author"],
        answer_aliases=[],
        date_property_pid="P577",
        date_value="2026-02-01",
        target_time="2026",
        canonical_question="Who wrote the work that the film Example Film was based on?",
        reasoning_style="multi_hop_join",
        hop_count=2,
        reasoning_path=[
            {
                "source_qid": "Q-film",
                "source_label": "Example Film",
                "property_pid": "P144",
                "property_label": "based on",
                "target_qid": "Q-book",
                "target_label": "Hidden Source Work",
                "role": "bridge",
            },
            {
                "source_qid": "Q-book",
                "source_label": "Hidden Source Work",
                "property_pid": "P50",
                "property_label": "author",
                "target_qid": "Q-author",
                "target_label": "Example Author",
                "role": "answer",
            },
        ],
        bridge_entities=[{"qid": "Q-book", "label": "Hidden Source Work", "role": "source_work"}],
        derivation_signature={"style": "multi_hop_join", "rule": "film_based_on_source_work_author"},
        provenance_complete=True,
        source_metadata={
            "required_reasoning_clues": ["based on"],
            "multi_hop_unique": True,
        },
    )


class MultiHopReasoningTests(unittest.TestCase):
    """Check multi-hop connectedness, shortcut, and output semantics."""

    def test_reasoning_path_must_be_connected(self) -> None:
        candidate = make_multi_hop_candidate()
        self.assertTrue(reasoning_path_is_connected(candidate))
        candidate.reasoning_path[1]["source_qid"] = "Q-other"
        self.assertFalse(reasoning_path_is_connected(candidate))

    def test_question_must_preserve_reasoning_clues(self) -> None:
        candidate = make_multi_hop_candidate()
        self.assertTrue(
            question_requires_all_hops(
                candidate,
                "Who wrote the work that the film Example Film was based on?",
            )
        )
        self.assertFalse(question_requires_all_hops(candidate, "Who wrote Example Film?"))

    def test_shortcut_check_rejects_single_hop_surface(self) -> None:
        candidate = make_multi_hop_candidate()
        result = shortcut_check(candidate, "Who wrote Example Film?")
        self.assertFalse(result["question_requires_all_hops"])
        self.assertFalse(result["shortcut_free"])

    def test_bridge_leakage_is_rejected_when_bridge_should_stay_latent(self) -> None:
        candidate = make_multi_hop_candidate()
        self.assertTrue(
            question_leaks_bridge_entities(
                "Who wrote the work Hidden Source Work that the film Example Film was based on?",
                candidate,
            )
        )
        self.assertFalse(question_leaks_bridge_entities(candidate.canonical_question, candidate))

    def test_bridge_label_matching_subject_label_is_not_treated_as_new_leakage(self) -> None:
        candidate = make_multi_hop_candidate()
        candidate.bridge_entities = [{"qid": "Q-book", "label": "Example Film", "role": "source_work"}]
        candidate.reasoning_path[0]["target_label"] = "Example Film"
        self.assertFalse(question_leaks_bridge_entities(candidate.canonical_question, candidate))

    def test_bridge_label_inside_subject_title_is_not_treated_as_new_leakage(self) -> None:
        candidate = make_multi_hop_candidate()
        candidate.subject_label = "Haikyu!! The Dumpster Battle"
        candidate.bridge_entities = [{"qid": "Q-book", "label": "Haikyu!!", "role": "source_work"}]
        candidate.canonical_question = (
            "Who wrote the work that the film Haikyu!! The Dumpster Battle was based on?"
        )
        self.assertFalse(question_leaks_bridge_entities(candidate.canonical_question, candidate))
        self.assertTrue(
            question_leaks_bridge_entities(
                "Who wrote Haikyu!!, the work that Haikyu!! The Dumpster Battle was based on?",
                candidate,
            )
        )

    def test_derivation_uniqueness_can_fail_even_with_single_answer_slot(self) -> None:
        candidate = make_multi_hop_candidate()
        self.assertTrue(answer_is_unique(candidate))
        candidate.source_metadata["multi_hop_unique"] = False
        self.assertFalse(answer_is_unique(candidate))

    def test_provenance_contract_requires_reasoning_signature_and_path(self) -> None:
        candidate = make_multi_hop_candidate()
        self.assertTrue(reasoning_provenance_is_complete(candidate))
        candidate.derivation_signature = {}
        self.assertFalse(reasoning_provenance_is_complete(candidate))

    def test_ordinal_candidate_requires_history_metadata(self) -> None:
        candidate = make_multi_hop_candidate()
        candidate.reasoning_style = "multi_hop_ordinal"
        candidate.source_metadata["ordinal_metadata"] = {
            "series_history_complete": True,
            "descriptor": "Melodifestivalen",
        }
        self.assertTrue(ordinal_candidate_is_safe(candidate))
        candidate.source_metadata["ordinal_metadata"]["series_history_complete"] = False
        self.assertFalse(ordinal_candidate_is_safe(candidate))

    def test_hidden_temporal_bridge_labels_are_allowed(self) -> None:
        candidate = make_multi_hop_candidate()
        candidate.reasoning_path[0]["target_label"] = "2026 Hidden Source Work"
        candidate.reasoning_path[1]["source_label"] = "2026 Hidden Source Work"
        self.assertTrue(reasoning_path_is_temporally_safe(candidate))

    def test_output_record_includes_multi_hop_metadata(self) -> None:
        candidate = make_multi_hop_candidate()
        record = candidate.to_output_record("example_1")
        self.assertEqual(record["reasoning_style"], "multi_hop_join")
        self.assertEqual(record["hop_count"], 2)
        self.assertIn("reasoning_path", record)
        self.assertIn("derivation_signature", record)

    def test_reasoning_hop_can_serialize_qualifier_provenance(self) -> None:
        hop = build_reasoning_hop(
            source_qid="Q1",
            source_label="Example Person",
            property_pid="P69",
            property_label="educated at",
            target_qid="Q2",
            target_label="Example University",
            role="bridge",
            qualifiers={"P512": "Q3", "P582": "2026-02-15"},
        )
        self.assertEqual(hop["qualifiers"]["P512"], "Q3")


if __name__ == "__main__":
    unittest.main()
