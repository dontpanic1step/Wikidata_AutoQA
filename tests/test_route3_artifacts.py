"""Tests for the Route 3 candidate artifact schema."""

from __future__ import annotations

import pytest
from test_support import ROOT  # noqa: F401


from wikidata_simpleqa.route3_artifacts import (
    Route3CandidateArtifact,
    Route3CandidateIdentity,
    Route3CandidateProvenance,
    create_route3_candidate_artifact,
    revise_route3_candidate_artifact,
)


def _artifact(slot: str = "single") -> Route3CandidateArtifact:
    identity = Route3CandidateIdentity(
        run_group_id="run_group",
        segment_id="segment_01",
        canonical_page_id=123,
        original_candidate_slot=slot,
    )
    provenance = Route3CandidateProvenance(
        run_group_id="run_group",
        segment_id="segment_01",
        page_attempt=1,
        canonical_page_id=123,
        canonical_page_url="https://en.wikipedia.org/wiki/Example",
        selected_table={"table_index": 2, "markdown": "| Field | Value |"},
        selected_table_type="infobox",
        page_archive_hash="sha256:archive",
        generation_prompt="Generate one question.",
        generation_request={"model": "google/gemini-3-flash-preview"},
        generation_raw_response={"question": "Who designed Example?"},
        original_question="Who designed Example?",
        original_reference_answer="Jane Doe",
        original_aliases=("J. Doe",),
        original_search_queries=("Example architect",),
        answer_type="Person",
        generation_model="google/gemini-3-flash-preview",
        generation_parameters={"max_tokens": 4096},
        recipe_seed=42,
    )
    return create_route3_candidate_artifact(
        identity=identity,
        provenance=provenance,
        question="Who designed Example?",
        reference_answer="Jane Doe",
        aliases=("J. Doe",),
        search_queries=("Example architect",),
        topic="Art",
        source_validation={"answer_in_evidence": True},
        integrated_answer_type_gate={"passed": True},
        ddg={"decision": "accept"},
        second_stage={"decision": "accept"},
        status="accepted",
    )


@pytest.mark.parametrize("slot", ["single", "Person", "Place", "Number", "Date", "Other"])
def test_schema_round_trip_covers_single_and_all5_slots(slot: str) -> None:
    artifact = _artifact(slot)

    restored = Route3CandidateArtifact.from_dict(artifact.to_dict())

    assert restored == artifact
    assert restored.candidate_id == artifact.candidate_id


def test_question_only_edit_preserves_answer_aliases_and_queries() -> None:
    artifact = _artifact()

    revised = revise_route3_candidate_artifact(
        artifact,
        edited_question="Who was the designer of Example?",
        edit_reason="Natural wording",
    )

    current = revised.current_revision
    assert revised.candidate_id == artifact.candidate_id
    assert current.authoritative_question == "Who was the designer of Example?"
    assert current.reference_answer == "Jane Doe"
    assert current.active_aliases == ("J. Doe",)
    assert current.active_search_queries == ("Example architect",)
    assert current.ddg == {}
    assert current.second_stage == {}
    assert current.status == "rerun"
    assert revised.provenance == artifact.provenance


def test_answer_only_edit_clears_active_aliases_and_old_results() -> None:
    artifact = _artifact()

    revised = revise_route3_candidate_artifact(
        artifact,
        edited_reference_answer="Janet Doe",
        edit_reason="Correct transcription",
    )

    current = revised.current_revision
    assert current.authoritative_question == "Who designed Example?"
    assert current.reference_answer == "Janet Doe"
    assert current.active_aliases == ()
    assert current.active_search_queries == ("Example architect",)
    assert current.source_validation == {}
    assert current.integrated_answer_type_gate == {}
    assert current.ddg == {}
    assert current.second_stage == {}
    assert revised.revisions[0].reference_answer == "Jane Doe"
    assert revised.revisions[0].active_aliases == ("J. Doe",)


def test_question_and_answer_edit_uses_authoritative_human_values() -> None:
    revised = revise_route3_candidate_artifact(
        _artifact(),
        edited_question="Which architect designed Example?",
        edited_reference_answer="Janet Doe",
        edit_reason="Correct both fields",
    )

    payload = revised.to_dict()
    restored = Route3CandidateArtifact.from_dict(payload)
    assert restored.current_revision.authoritative_question == "Which architect designed Example?"
    assert restored.current_revision.reference_answer == "Janet Doe"
    assert restored.provenance.original_question == "Who designed Example?"
    assert restored.provenance.original_reference_answer == "Jane Doe"


def test_delete_revision_preserves_selected_table_evidence() -> None:
    artifact = _artifact()

    revised = revise_route3_candidate_artifact(
        artifact,
        delete=True,
        edit_reason="Not suitable for release",
    )

    assert revised.current_revision.delete is True
    assert revised.current_revision.status == "rejected"
    assert revised.provenance.selected_table == artifact.provenance.selected_table
    assert revised.candidate_id == artifact.candidate_id


def test_multiple_revisions_are_contiguous_and_keep_full_history() -> None:
    first = _artifact()
    second = revise_route3_candidate_artifact(
        first,
        edited_question="Who was the designer of Example?",
        edit_reason="Round one",
    )
    third = revise_route3_candidate_artifact(
        second,
        edited_reference_answer="Janet Doe",
        edit_reason="Round two",
    )

    restored = Route3CandidateArtifact.from_dict(third.to_dict())
    assert [revision.revision_number for revision in restored.revisions] == [1, 2, 3]
    assert [revision.reference_answer for revision in restored.revisions] == [
        "Jane Doe",
        "Jane Doe",
        "Janet Doe",
    ]
    assert restored.candidate_id == first.candidate_id
