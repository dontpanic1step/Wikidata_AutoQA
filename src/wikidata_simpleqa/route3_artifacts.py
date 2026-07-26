"""Stable Route 3 candidate artifact schema and revision operations."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from dataclasses import dataclass, replace
from typing import Any


ROUTE3_CANDIDATE_SCHEMA_VERSION = 1
SINGLE_CANDIDATE_SLOT = "single"
ALL5_CANDIDATE_SLOTS = ("Person", "Place", "Number", "Date", "Other")
REVISION_STATUSES = ("accepted", "rejected", "rerun")


@dataclass(frozen=True, slots=True)
class Route3CandidateIdentity:
    """Immutable fields that define one stable Route 3 candidate ID."""

    run_group_id: str
    segment_id: str
    canonical_page_id: int
    original_candidate_slot: str

    def __post_init__(self) -> None:
        """Validate the four identity fields."""
        if not self.run_group_id.strip():
            raise ValueError("run_group_id is required")
        if not self.segment_id.strip():
            raise ValueError("segment_id is required")
        if self.canonical_page_id < 1:
            raise ValueError("canonical_page_id must be positive")
        if self.original_candidate_slot not in (SINGLE_CANDIDATE_SLOT, *ALL5_CANDIDATE_SLOTS):
            raise ValueError(f"invalid original_candidate_slot: {self.original_candidate_slot!r}")

    @property
    def candidate_id(self) -> str:
        """Return an ID derived only from the immutable identity fields."""
        payload = json.dumps(
            [
                self.run_group_id,
                self.segment_id,
                self.canonical_page_id,
                self.original_candidate_slot,
            ],
            ensure_ascii=False,
            separators=(",", ":"),
        )
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        slot = self.original_candidate_slot.lower()
        return f"route3_p{self.canonical_page_id}_{slot}_{digest}"

    def to_dict(self) -> dict[str, Any]:
        """Serialize the identity."""
        return {
            "run_group_id": self.run_group_id,
            "segment_id": self.segment_id,
            "canonical_page_id": self.canonical_page_id,
            "original_candidate_slot": self.original_candidate_slot,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Route3CandidateIdentity":
        """Deserialize the identity."""
        return cls(
            run_group_id=str(payload["run_group_id"]),
            segment_id=str(payload["segment_id"]),
            canonical_page_id=int(payload["canonical_page_id"]),
            original_candidate_slot=str(payload["original_candidate_slot"]),
        )


@dataclass(frozen=True, slots=True)
class Route3CandidateProvenance:
    """Immutable generation and source audit for one candidate."""

    run_group_id: str
    segment_id: str
    page_attempt: int
    canonical_page_id: int
    canonical_page_url: str
    selected_table: dict[str, Any]
    selected_table_type: str
    page_archive_hash: str
    generation_prompt: str
    generation_request: Any
    generation_raw_response: Any
    original_question: str
    original_reference_answer: str
    original_aliases: tuple[str, ...]
    original_search_queries: tuple[str, ...]
    answer_type: str
    generation_model: str
    generation_parameters: dict[str, Any]
    recipe_seed: Any

    def to_dict(self) -> dict[str, Any]:
        """Serialize immutable provenance without sharing mutable values."""
        return {
            "run_group_id": self.run_group_id,
            "segment_id": self.segment_id,
            "page_attempt": self.page_attempt,
            "canonical_page_id": self.canonical_page_id,
            "canonical_page_url": self.canonical_page_url,
            "selected_table": deepcopy(self.selected_table),
            "selected_table_type": self.selected_table_type,
            "page_archive_hash": self.page_archive_hash,
            "generation_prompt": self.generation_prompt,
            "generation_request": deepcopy(self.generation_request),
            "generation_raw_response": deepcopy(self.generation_raw_response),
            "original_question": self.original_question,
            "original_reference_answer": self.original_reference_answer,
            "original_aliases": list(self.original_aliases),
            "original_search_queries": list(self.original_search_queries),
            "answer_type": self.answer_type,
            "generation_model": self.generation_model,
            "generation_parameters": deepcopy(self.generation_parameters),
            "recipe_seed": deepcopy(self.recipe_seed),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Route3CandidateProvenance":
        """Deserialize immutable provenance."""
        return cls(
            run_group_id=str(payload["run_group_id"]),
            segment_id=str(payload["segment_id"]),
            page_attempt=int(payload["page_attempt"]),
            canonical_page_id=int(payload["canonical_page_id"]),
            canonical_page_url=str(payload["canonical_page_url"]),
            selected_table=deepcopy(payload["selected_table"]),
            selected_table_type=str(payload["selected_table_type"]),
            page_archive_hash=str(payload["page_archive_hash"]),
            generation_prompt=str(payload["generation_prompt"]),
            generation_request=deepcopy(payload["generation_request"]),
            generation_raw_response=deepcopy(payload["generation_raw_response"]),
            original_question=str(payload["original_question"]),
            original_reference_answer=str(payload["original_reference_answer"]),
            original_aliases=tuple(str(value) for value in payload["original_aliases"]),
            original_search_queries=tuple(str(value) for value in payload["original_search_queries"]),
            answer_type=str(payload["answer_type"]),
            generation_model=str(payload["generation_model"]),
            generation_parameters=deepcopy(payload["generation_parameters"]),
            recipe_seed=deepcopy(payload["recipe_seed"]),
        )


@dataclass(frozen=True, slots=True)
class Route3CandidateRevision:
    """One authoritative candidate revision."""

    revision_number: int
    authoritative_question: str
    reference_answer: str
    active_aliases: tuple[str, ...]
    active_search_queries: tuple[str, ...]
    topic: str
    delete: bool
    edit_reason: str
    source_validation: dict[str, Any]
    integrated_answer_type_gate: dict[str, Any]
    ddg: dict[str, Any]
    second_stage: dict[str, Any]
    status: str

    def __post_init__(self) -> None:
        """Validate revision numbering and status."""
        if self.revision_number < 1:
            raise ValueError("revision_number must be positive")
        if self.status not in REVISION_STATUSES:
            raise ValueError(f"invalid revision status: {self.status!r}")

    def to_dict(self) -> dict[str, Any]:
        """Serialize one revision."""
        return {
            "revision_number": self.revision_number,
            "authoritative_question": self.authoritative_question,
            "reference_answer": self.reference_answer,
            "active_aliases": list(self.active_aliases),
            "active_search_queries": list(self.active_search_queries),
            "topic": self.topic,
            "delete": self.delete,
            "edit_reason": self.edit_reason,
            "source_validation": deepcopy(self.source_validation),
            "integrated_answer_type_gate": deepcopy(self.integrated_answer_type_gate),
            "ddg": deepcopy(self.ddg),
            "second_stage": deepcopy(self.second_stage),
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Route3CandidateRevision":
        """Deserialize one revision."""
        return cls(
            revision_number=int(payload["revision_number"]),
            authoritative_question=str(payload["authoritative_question"]),
            reference_answer=str(payload["reference_answer"]),
            active_aliases=tuple(str(value) for value in payload["active_aliases"]),
            active_search_queries=tuple(str(value) for value in payload["active_search_queries"]),
            topic=str(payload["topic"]),
            delete=bool(payload["delete"]),
            edit_reason=str(payload["edit_reason"]),
            source_validation=deepcopy(payload["source_validation"]),
            integrated_answer_type_gate=deepcopy(payload["integrated_answer_type_gate"]),
            ddg=deepcopy(payload["ddg"]),
            second_stage=deepcopy(payload["second_stage"]),
            status=str(payload["status"]),
        )


@dataclass(frozen=True, slots=True)
class Route3CandidateArtifact:
    """Complete immutable provenance plus append-only revisions."""

    identity: Route3CandidateIdentity
    provenance: Route3CandidateProvenance
    revisions: tuple[Route3CandidateRevision, ...]
    schema_version: int = ROUTE3_CANDIDATE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        """Require consistent identity, provenance, and revision numbering."""
        if self.schema_version != ROUTE3_CANDIDATE_SCHEMA_VERSION:
            raise ValueError(f"unsupported schema_version: {self.schema_version}")
        if not self.revisions:
            raise ValueError("at least one revision is required")
        if self.identity.run_group_id != self.provenance.run_group_id:
            raise ValueError("identity and provenance run_group_id differ")
        if self.identity.segment_id != self.provenance.segment_id:
            raise ValueError("identity and provenance segment_id differ")
        if self.identity.canonical_page_id != self.provenance.canonical_page_id:
            raise ValueError("identity and provenance canonical_page_id differ")
        expected_numbers = tuple(range(1, len(self.revisions) + 1))
        actual_numbers = tuple(revision.revision_number for revision in self.revisions)
        if actual_numbers != expected_numbers:
            raise ValueError("revision numbers must be contiguous from 1")

    @property
    def candidate_id(self) -> str:
        """Return the stable candidate ID."""
        return self.identity.candidate_id

    @property
    def current_revision(self) -> Route3CandidateRevision:
        """Return the latest authoritative revision."""
        return self.revisions[-1]

    def to_dict(self) -> dict[str, Any]:
        """Serialize the complete artifact."""
        return {
            "schema_version": self.schema_version,
            "id": self.candidate_id,
            "identity": self.identity.to_dict(),
            "provenance": self.provenance.to_dict(),
            "revision_number": self.current_revision.revision_number,
            "revisions": [revision.to_dict() for revision in self.revisions],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Route3CandidateArtifact":
        """Deserialize and validate the complete artifact."""
        artifact = cls(
            schema_version=int(payload["schema_version"]),
            identity=Route3CandidateIdentity.from_dict(payload["identity"]),
            provenance=Route3CandidateProvenance.from_dict(payload["provenance"]),
            revisions=tuple(
                Route3CandidateRevision.from_dict(revision)
                for revision in payload["revisions"]
            ),
        )
        if str(payload["id"]) != artifact.candidate_id:
            raise ValueError("stored candidate ID does not match immutable identity")
        if int(payload["revision_number"]) != artifact.current_revision.revision_number:
            raise ValueError("stored revision_number does not match latest revision")
        return artifact


def create_route3_candidate_artifact(
    *,
    identity: Route3CandidateIdentity,
    provenance: Route3CandidateProvenance,
    question: str,
    reference_answer: str,
    aliases: tuple[str, ...],
    search_queries: tuple[str, ...],
    topic: str = "",
    source_validation: dict[str, Any] | None = None,
    integrated_answer_type_gate: dict[str, Any] | None = None,
    ddg: dict[str, Any] | None = None,
    second_stage: dict[str, Any] | None = None,
    status: str = "accepted",
) -> Route3CandidateArtifact:
    """Create the first authoritative revision without changing provenance."""
    revision = Route3CandidateRevision(
        revision_number=1,
        authoritative_question=question,
        reference_answer=reference_answer,
        active_aliases=tuple(aliases),
        active_search_queries=tuple(search_queries),
        topic=topic,
        delete=False,
        edit_reason="",
        source_validation=deepcopy(source_validation or {}),
        integrated_answer_type_gate=deepcopy(integrated_answer_type_gate or {}),
        ddg=deepcopy(ddg or {}),
        second_stage=deepcopy(second_stage or {}),
        status=status,
    )
    return Route3CandidateArtifact(
        identity=identity,
        provenance=provenance,
        revisions=(revision,),
    )


def revise_route3_candidate_artifact(
    artifact: Route3CandidateArtifact,
    *,
    edited_question: str | None = None,
    edited_reference_answer: str | None = None,
    topic: str | None = None,
    delete: bool | None = None,
    edit_reason: str = "",
) -> Route3CandidateArtifact:
    """Append one authoritative revision while preserving identity and provenance."""
    current = artifact.current_revision
    question = current.authoritative_question if edited_question is None else edited_question
    answer = current.reference_answer if edited_reference_answer is None else edited_reference_answer
    question_changed = question != current.authoritative_question
    answer_changed = answer != current.reference_answer
    qa_changed = question_changed or answer_changed
    delete_value = current.delete if delete is None else delete

    revision = Route3CandidateRevision(
        revision_number=current.revision_number + 1,
        authoritative_question=question,
        reference_answer=answer,
        active_aliases=() if answer_changed else current.active_aliases,
        active_search_queries=current.active_search_queries,
        topic=current.topic if topic is None else topic,
        delete=delete_value,
        edit_reason=edit_reason,
        source_validation={} if qa_changed else deepcopy(current.source_validation),
        integrated_answer_type_gate={} if qa_changed else deepcopy(current.integrated_answer_type_gate),
        ddg={} if qa_changed else deepcopy(current.ddg),
        second_stage={} if qa_changed else deepcopy(current.second_stage),
        status="rerun" if qa_changed else ("rejected" if delete_value else current.status),
    )
    return replace(artifact, revisions=(*artifact.revisions, revision))

def complete_route3_candidate_rerun(
    artifact: Route3CandidateArtifact,
    *,
    source_validation: dict[str, Any],
    integrated_answer_type_gate: dict[str, Any],
    ddg: dict[str, Any],
    second_stage: dict[str, Any],
    status: str,
) -> Route3CandidateArtifact:
    """Complete the latest rerun revision with fresh post-generation results."""
    if artifact.current_revision.status != "rerun":
        raise ValueError("Only a rerun revision can receive fresh validation results")
    if status not in REVISION_STATUSES:
        raise ValueError(f"invalid rerun completion status: {status!r}")
    completed = replace(
        artifact.current_revision,
        source_validation=deepcopy(source_validation),
        integrated_answer_type_gate=deepcopy(integrated_answer_type_gate),
        ddg=deepcopy(ddg),
        second_stage=deepcopy(second_stage),
        status=status,
    )
    return replace(artifact, revisions=(*artifact.revisions[:-1], completed))


def complete_route3_topic_classification(
    artifact: Route3CandidateArtifact,
    *,
    topic: str,
    status: str,
) -> Route3CandidateArtifact:
    """Complete topic classification on the latest accepted revision."""
    current = artifact.current_revision
    if current.status != "accepted" or current.topic:
        raise ValueError("Topic classification requires an accepted revision without a topic")
    if status not in {"accepted", "rejected"}:
        raise ValueError(f"invalid topic classification status: {status!r}")
    completed = replace(current, topic=topic, status=status)
    return replace(artifact, revisions=(*artifact.revisions[:-1], completed))
