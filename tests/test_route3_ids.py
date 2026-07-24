"""Tests for stable Route 3 record IDs."""

from __future__ import annotations

import pytest
from test_support import ROOT  # noqa: F401


from wikidata_simpleqa.route3_artifacts import Route3CandidateIdentity
from wikidata_simpleqa.route3_ids import assign_unique_route3_record_ids, route3_record_id


def _record(*, question: str = "Who designed the example building?") -> dict:
    return {
        "question": question,
        "answer": "Jane Doe",
        "answer_type": "Person",
        "source_metadata": {
            "run_group_id": "research_run",
            "segment_id": "01_person_10",
            "canonical_page_id": 123,
            "original_candidate_slot": "single",
        },
    }


def test_route3_record_id_uses_four_immutable_identity_fields() -> None:
    identity = Route3CandidateIdentity(
        run_group_id="research_run",
        segment_id="01_person_10",
        canonical_page_id=123,
        original_candidate_slot="single",
    )

    assert route3_record_id(_record()) == identity.candidate_id


def test_route3_record_id_does_not_change_with_question_edit() -> None:
    assert route3_record_id(_record(question="Original question?")) == route3_record_id(
        _record(question="Edited question?")
    )
def test_top_up_segment_produces_a_new_candidate_id() -> None:
    original = _record()
    top_up = _record()
    top_up["source_metadata"]["segment_id"] = "02_person_10_topup"

    assert route3_record_id(original) != route3_record_id(top_up)




def test_assign_unique_route3_record_ids_stores_canonical_identity() -> None:
    record = _record()

    assign_unique_route3_record_ids([record])

    assert record["source_metadata"]["candidate_identity"] == {
        "run_group_id": "research_run",
        "segment_id": "01_person_10",
        "canonical_page_id": 123,
        "original_candidate_slot": "single",
    }
    assert record["id"] == route3_record_id(record)


def test_assign_unique_route3_record_ids_rejects_duplicate_identity() -> None:
    with pytest.raises(ValueError, match="duplicate Route 3 candidate identity"):
        assign_unique_route3_record_ids(
            [_record(question="First wording?"), _record(question="Second wording?")]
        )
