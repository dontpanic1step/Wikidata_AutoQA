"""Dataclasses for candidates, templates, and rejections."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class DomainTemplate:
    """Configuration for one supported domain-property pair."""

    domain: str
    topic: str
    answer_type: str
    question_family: str
    subject_type_qid: str
    subject_type_label: str
    date_property_pid: str
    target_property_pid: str
    target_property_label: str
    canonical_question_template: str
    answer_format: str = "entity"
    date_answer_granularity: str | None = None
    composition_style: str = "single_fact"
    reasoning_style: str = "single_fact"
    temporal_mode: str = "atemporal"
    reasoning_recipe: dict[str, Any] = field(default_factory=dict)
    status: str = "active"
    evidence_status: str = "not_run"
    evidence_runs: list[str] = field(default_factory=list)
    evidence_notes: str = ""
    query_tags: list[str] = field(default_factory=list)
    required_topic_keywords: list[str] = field(default_factory=list)
    exact_instance_only: bool = False
    retrieval_limit: int = 100
    allow_non_answer_location_descriptor: bool = True


@dataclass(slots=True)
class AmbiguityResolution:
    """Resolved ambiguity outcome for one candidate."""

    status: str
    descriptor: str
    signature: list[str] = field(default_factory=list)
    competitor_qids: list[str] = field(default_factory=list)


@dataclass(slots=True)
class CandidateFact:
    """Metadata-rich representation of a candidate example."""

    subject_qid: str
    subject_label: str
    subject_aliases: list[str]
    domain: str
    topic: str
    answer_type: str
    question_family: str
    subject_type_qids: list[str]
    target_property_pid: str
    target_property_label: str
    answer_qids: list[str]
    answer_labels: list[str]
    answer_aliases: list[str]
    date_property_pid: str
    date_value: str
    target_time: str
    canonical_question: str
    rewritten_question: str | None = None
    ambiguity_status: str = "unknown"
    disambiguation_signature: list[str] = field(default_factory=list)
    competitor_qids: list[str] = field(default_factory=list)
    validation_flags: dict[str, Any] = field(default_factory=dict)
    newness_metadata: dict[str, Any] = field(default_factory=dict)
    reasoning_style: str = "single_fact"
    hop_count: int = 1
    reasoning_path: list[dict[str, Any]] = field(default_factory=list)
    bridge_entities: list[dict[str, Any]] = field(default_factory=list)
    derivation_signature: dict[str, Any] = field(default_factory=dict)
    shortcut_checks: dict[str, Any] = field(default_factory=dict)
    provenance_complete: bool = False
    question_requires_all_hops: bool | None = None
    subject_resource_url: str = ""
    subject_resource_key: str = ""
    source_metadata: dict[str, Any] = field(default_factory=dict)

    def to_output_record(self, example_id: str) -> dict[str, Any]:
        """Return the accepted-output representation."""
        question = self.rewritten_question or self.canonical_question
        answer = self.answer_labels[0] if self.answer_labels else None
        return {
            "id": example_id,
            "question": question,
            "answer": answer,
            "answer_aliases": self.answer_aliases,
            "subject_qid": self.subject_qid,
            "subject_resource_url": self.subject_resource_url,
            "subject_resource_key": self.subject_resource_key,
            "answer_qids": self.answer_qids,
            "property_pid": self.target_property_pid,
            "domain": self.domain,
            "topic": self.topic,
            "answer_type": self.answer_type,
            "question_family": self.question_family,
            "target_time": self.target_time,
            "date_filter": {
                "property": self.date_property_pid,
                "value": self.date_value,
            },
            "newness_metadata": self.newness_metadata,
            "ambiguity_status": self.ambiguity_status,
            "disambiguation_signature": self.disambiguation_signature,
            "competitor_qids": self.competitor_qids,
            "reasoning_style": self.reasoning_style,
            "hop_count": self.hop_count,
            "reasoning_path": self.reasoning_path,
            "bridge_entities": self.bridge_entities,
            "derivation_signature": self.derivation_signature,
            "shortcut_checks": self.shortcut_checks,
            "provenance_complete": self.provenance_complete,
            "question_requires_all_hops": self.question_requires_all_hops,
            "canonical_question": self.canonical_question,
            "rewritten_question": self.rewritten_question,
            "validation_flags": self.validation_flags,
            "source_metadata": self.source_metadata,
        }


@dataclass(slots=True)
class RejectedCandidate:
    """Serialized form for rejected candidates."""

    reason: str
    candidate: CandidateFact
    notes: dict[str, Any] = field(default_factory=dict)

    def to_output_record(self) -> dict[str, Any]:
        """Return the rejected-output representation."""
        record = asdict(self.candidate)
        record["rejection_reason"] = self.reason
        record["rejection_notes"] = self.notes
        return record
