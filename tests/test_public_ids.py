"""Tests for durable public benchmark ID allocation."""

from __future__ import annotations

import json

import pytest

from test_support import ROOT  # noqa: F401

from wikidata_simpleqa.public_ids import (
    assign_public_ids,
    load_public_id_registry,
    new_public_id_registry,
    validate_public_id_registry,
    write_public_id_registry,
)


def _record(candidate_id: str) -> dict[str, str]:
    return {
        "id": candidate_id,
        "problem": f"Question for {candidate_id}?",
        "answer": "Answer",
        "topic": "History",
        "answer_type": "Other",
        "urls": "[]",
    }


def test_initial_assignment_uses_candidate_order_not_input_order() -> None:
    records, registry = assign_public_ids(
        [_record("page2_other_b"), _record("page1_person_a")],
        new_public_id_registry(),
    )

    assert [record["id"] for record in records] == [
        "simpleqa_synth_000001",
        "simpleqa_synth_000002",
    ]
    assert registry["assignments"] == [
        {
            "candidate_id": "page1_person_a",
            "public_id": "simpleqa_synth_000001",
        },
        {
            "candidate_id": "page2_other_b",
            "public_id": "simpleqa_synth_000002",
        },
    ]


def test_existing_ids_survive_removal_reordering_and_addition() -> None:
    _, registry = assign_public_ids(
        [_record("page1_person_a"), _record("page2_other_b")],
        new_public_id_registry(),
    )

    records, updated = assign_public_ids(
        [_record("page3_date_c"), _record("page2_other_b")],
        registry,
    )

    assert [record["id"] for record in records] == [
        "simpleqa_synth_000002",
        "simpleqa_synth_000003",
    ]
    assert updated["next_sequence"] == 4
    assert len(updated["assignments"]) == 3


def test_registry_round_trip_and_duplicate_rejection(tmp_path) -> None:
    _, registry = assign_public_ids([_record("page1_single_a")], new_public_id_registry())
    path = tmp_path / "public_ids.json"
    write_public_id_registry(path, registry)

    assert load_public_id_registry(path) == registry
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["assignments"].append(dict(payload["assignments"][0]))
    with pytest.raises(ValueError, match="duplicate public-ID candidate"):
        validate_public_id_registry(payload)
