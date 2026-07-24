"""Stable Route 3 record identifiers."""

from __future__ import annotations

from typing import Any

from .route3_artifacts import Route3CandidateIdentity


def route3_record_id(record: dict[str, Any]) -> str:
    """Return the stable ID derived from the four immutable candidate fields."""
    return route3_record_identity(record).candidate_id


def route3_record_identity(record: dict[str, Any]) -> Route3CandidateIdentity:
    """Read the canonical identity without legacy field fallbacks."""
    metadata = record["source_metadata"]
    explicit = metadata.get("candidate_identity")
    if isinstance(explicit, dict):
        return Route3CandidateIdentity.from_dict(explicit)
    return Route3CandidateIdentity(
        run_group_id=str(metadata["run_group_id"]),
        segment_id=str(metadata["segment_id"]),
        canonical_page_id=int(metadata["canonical_page_id"]),
        original_candidate_slot=str(metadata["original_candidate_slot"]),
    )


def assign_unique_route3_record_ids(records: list[dict[str, Any]]) -> None:
    """Assign stable IDs and reject duplicate immutable identities."""
    identities = [route3_record_identity(record) for record in records]
    candidate_ids = [identity.candidate_id for identity in identities]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError("duplicate Route 3 candidate identity")
    for record, identity, candidate_id in zip(records, identities, candidate_ids):
        metadata = record["source_metadata"]
        metadata["candidate_identity"] = identity.to_dict()
        record["id"] = candidate_id
