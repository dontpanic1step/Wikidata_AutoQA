"""Candidate models for the formal Route 3 workflow."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .date_reference import normalize_date_answer
from .number_reference import normalize_number_answer


@dataclass(slots=True)
class EntityReference:
    """Stable reference to a subject or answer entity."""

    name: str
    qid: str = ""
    wikipedia_title: str = ""
    url: str = ""


@dataclass(slots=True)
class EvidenceRecord:
    """Human-readable evidence attached to one generated candidate."""

    text: str = ""
    url: str = ""
    source_title: str = ""
    section: str = ""
    retrieved_at: str = ""


@dataclass(slots=True)
class GeneratedCandidate:
    """Candidate structure emitted by Route 3 generation."""

    source_type: str
    generation_route: str
    question: str
    answer: str
    answer_aliases: list[str]
    subject_entity: EntityReference
    answer_entity: EntityReference
    relation_or_claim: str
    evidence: EvidenceRecord = field(default_factory=EvidenceRecord)
    canonical_question: str = ""
    question_family: str = ""
    answer_type: str = ""
    topic: str = ""
    target_time: str = ""
    source_template_domain: str = ""
    search_queries: list[str] = field(default_factory=list)
    search_verification_features: dict[str, Any] = field(default_factory=dict)
    cheap_model_verification_features: dict[str, Any] = field(default_factory=dict)
    panel_grading_features: dict[str, Any] = field(default_factory=dict)
    validation: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    source_metadata: dict[str, Any] = field(default_factory=dict)
    rewritten_question: str | None = None

    def __post_init__(self) -> None:
        """Normalize numeric answers at the shared downstream boundary."""
        if self.answer_type == "Number":
            self.answer = normalize_number_answer(self.answer, self.answer_type)
            self.answer_aliases = [
                normalize_number_answer(alias, self.answer_type)
                for alias in self.answer_aliases
            ]
            self.answer_entity.name = normalize_number_answer(self.answer_entity.name, self.answer_type)
        elif self.answer_type == "Date":
            self.answer = normalize_date_answer(self.answer, self.answer_type)
            self.answer_aliases = [
                normalize_date_answer(alias, self.answer_type)
                for alias in self.answer_aliases
            ]
            self.answer_entity.name = normalize_date_answer(self.answer_entity.name, self.answer_type)

    @property
    def final_question(self) -> str:
        """Return the final surfaced question text."""
        return (self.rewritten_question or self.question).strip()

    @property
    def subject_resource_key(self) -> str:
        """Return the stable subject resource key used for deduplication."""
        slot_id = str(self.source_metadata.get("route3_slot_id") or "").strip()
        if slot_id:
            return f"{self.subject_entity.url}#{slot_id}"
        return self.subject_entity.url

    def to_output_record(self, example_id: str) -> dict[str, Any]:
        """Serialize one accepted candidate for JSONL output."""
        record = {
            "id": example_id,
            "question": self.final_question,
            "answer": self.answer,
            "answer_aliases": self.answer_aliases,
            "source_type": self.source_type,
            "generation_route": self.generation_route,
            "subject_entity": {
                "name": self.subject_entity.name,
                "qid": self.subject_entity.qid,
                "wikipedia_title": self.subject_entity.wikipedia_title,
                "url": self.subject_entity.url,
            },
            "answer_entity": {
                "name": self.answer_entity.name,
                "qid": self.answer_entity.qid,
                "wikipedia_title": self.answer_entity.wikipedia_title,
                "url": self.answer_entity.url,
            },
            "relation_or_claim": self.relation_or_claim,
            "evidence": {
                "text": self.evidence.text,
                "url": self.evidence.url,
                "source_title": self.evidence.source_title,
                "section": self.evidence.section,
                "retrieved_at": self.evidence.retrieved_at,
            },
            "canonical_question": self.canonical_question,
            "rewritten_question": self.rewritten_question,
            "question_family": self.question_family,
            "answer_type": self.answer_type,
            "template_key": self.source_template_domain,
            "domain": self.topic,
            "legacy_domain": self.source_template_domain,
            "topic": self.topic,
            "target_time": self.target_time,
            "subject_resource_url": self.subject_entity.url,
            "subject_resource_key": self.subject_resource_key,
            "search_queries": self.search_queries,
            "search_verification_features": self.search_verification_features,
            "cheap_model_verification_features": self.cheap_model_verification_features,
            "panel_grading_features": self.panel_grading_features,
            "validation": self.validation,
            "notes": self.notes,
            "source_metadata": self.source_metadata,
        }
        return record

    def to_rejected_record(
        self,
        *,
        reason: str,
        notes: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Serialize one rejected candidate for JSONL output."""
        record = self.to_output_record(example_id="")
        record.pop("id", None)
        record["rejection_reason"] = reason
        record["rejection_notes"] = notes or {}
        if notes:
            rejection_rule = notes.get("surface_validation_failure_reason") or notes.get("failure_reason")
            if rejection_rule:
                record["rejection_rule"] = str(rejection_rule)
        return record
