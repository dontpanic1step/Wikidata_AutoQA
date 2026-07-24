"""Manual review artifacts and revision loop for formal Route 3 runs."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Callable, Iterable

from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.datavalidation import DataValidation

from .generation_models import EntityReference, EvidenceRecord, GeneratedCandidate
from .route3_artifacts import (
    Route3CandidateArtifact,
    Route3CandidateProvenance,
    complete_route3_candidate_rerun,
    create_route3_candidate_artifact,
    revise_route3_candidate_artifact,
)
from .route3_ids import route3_record_identity
from .route3_run_ledger import atomic_write_json


REVIEW_STATE_VERSION = 1
REVIEW_COLUMNS = (
    "id",
    "question",
    "reference_answer",
    "wikipedia_url",
    "topic",
    "delete",
    "edited_question",
    "edited_reference_answer",
    "edit_reason",
)
REVIEW_TOPICS = (
    "Science & technology",
    "Politics",
    "Art",
    "Other",
    "Geography",
    "Sports",
    "Music",
    "TV shows",
    "History",
    "Video games",
)
DELETE_VALUES = ("Yes", "No")
RERUN_REJECTION_REASONS = {
    "search_longtail_verifier_error",
    "second_stage_grading_error",
}


def create_review_state(
    records: Iterable[dict[str, Any]],
    *,
    segment_fingerprints: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Create a review state from formal accepted records."""
    bundles = [_review_bundle(record) for record in records]
    segment_ids = {str(bundle["artifact"]["identity"]["segment_id"]) for bundle in bundles}
    missing_segments = sorted(segment_ids - set(segment_fingerprints))
    if missing_segments:
        raise ValueError(f"missing segment fingerprints: {', '.join(missing_segments)}")
    candidate_ids = [str(bundle["artifact"]["id"]) for bundle in bundles]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError("duplicate candidate ID in accepted review input")
    return {
        "review_state_version": REVIEW_STATE_VERSION,
        "segment_fingerprints": deepcopy(segment_fingerprints),
        "candidates": bundles,
    }


def load_review_state(path: Path) -> dict[str, Any]:
    """Load and validate one review-state JSON document."""
    state = json.loads(path.read_text(encoding="utf-8"))
    if int(state["review_state_version"]) != REVIEW_STATE_VERSION:
        raise ValueError("unsupported review state version")
    for bundle in state["candidates"]:
        Route3CandidateArtifact.from_dict(bundle["artifact"])
    return state


def write_review_state(path: Path, state: dict[str, Any]) -> None:
    """Atomically write one review state."""
    atomic_write_json(path, state)


def accepted_review_bundles(state: dict[str, Any]) -> list[dict[str, Any]]:
    """Return bundles whose latest revision is active and accepted."""
    rows: list[dict[str, Any]] = []
    for bundle in state["candidates"]:
        artifact = Route3CandidateArtifact.from_dict(bundle["artifact"])
        revision = artifact.current_revision
        if revision.status == "accepted" and not revision.delete:
            rows.append(bundle)
    return sorted(rows, key=lambda bundle: str(bundle["artifact"]["id"]))


def render_review_markdown(state: dict[str, Any], *, run_id: str) -> str:
    """Render accepted candidates with source tables and two-model answers."""
    bundles = accepted_review_bundles(state)
    lines = [
        f"# Route 3 Review: `{run_id}`",
        "",
        f"Accepted candidates: {len(bundles)}",
        "",
    ]
    for index, bundle in enumerate(bundles, start=1):
        artifact = Route3CandidateArtifact.from_dict(bundle["artifact"])
        revision = artifact.current_revision
        provenance = artifact.provenance
        lines.extend(
            [
                f"## {index}. `{artifact.candidate_id}`",
                "",
                f"Question: {revision.authoritative_question}",
                "",
                f"Reference answer: **{revision.reference_answer}**",
                "",
                f"Answer type: `{provenance.answer_type}`",
                "",
                f"Wikipedia: [{provenance.canonical_page_url}]({provenance.canonical_page_url})",
                "",
                f"Canonical page ID: `{provenance.canonical_page_id}`",
                "",
                "Selected table:",
                "",
                str(provenance.selected_table["markdown"]),
                "",
                "Two-model answers:",
                "",
            ]
        )
        for model in revision.second_stage["models"]:
            lines.extend(
                [
                    f"- `{model['model']}`: {model['predicted_answer']}",
                    f"  - Grade: `{model['grade']}`",
                    f"  - Reason: {model['reason']}",
                ]
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_review_workbook(path: Path, state: dict[str, Any]) -> None:
    """Write the formal English-column review workbook."""
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "review"
    worksheet.append(list(REVIEW_COLUMNS))
    for bundle in accepted_review_bundles(state):
        artifact = Route3CandidateArtifact.from_dict(bundle["artifact"])
        revision = artifact.current_revision
        worksheet.append(
            [
                artifact.candidate_id,
                revision.authoritative_question,
                revision.reference_answer,
                artifact.provenance.canonical_page_url,
                revision.topic,
                "No",
                "",
                "",
                "",
            ]
        )
    last_row = max(2, worksheet.max_row)
    topic_validation = DataValidation(
        type="list",
        formula1='"' + ",".join(REVIEW_TOPICS) + '"',
        allow_blank=True,
    )
    delete_validation = DataValidation(type="list", formula1='"Yes,No"', allow_blank=False)
    worksheet.add_data_validation(topic_validation)
    worksheet.add_data_validation(delete_validation)
    topic_validation.add(f"E2:E{last_row}")
    delete_validation.add(f"F2:F{last_row}")
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(path)
    workbook.close()


def read_review_workbook(path: Path) -> list[dict[str, str]]:
    """Read formal review rows and require the exact English header order."""
    workbook = load_workbook(path, data_only=False)
    worksheet = workbook["review"]
    values = list(worksheet.iter_rows(values_only=True))
    workbook.close()
    headers = tuple(str(value or "") for value in values[0])
    if headers != REVIEW_COLUMNS:
        raise ValueError(f"Review columns must exactly match: {', '.join(REVIEW_COLUMNS)}")
    rows: list[dict[str, str]] = []
    for values_row in values[1:]:
        if all(value is None or str(value).strip() == "" for value in values_row):
            continue
        rows.append(
            {
                column: str(values_row[index] or "").strip()
                for index, column in enumerate(REVIEW_COLUMNS)
            }
        )
    return rows


def validate_review_rows(
    rows: Iterable[dict[str, str]],
    *,
    known_ids: set[str],
    finalization: bool = False,
) -> None:
    """Validate IDs, topics, deletion values, and edit combinations."""
    seen_ids: set[str] = set()
    for row in rows:
        candidate_id = row["id"]
        if candidate_id in seen_ids:
            raise ValueError(f"duplicate review ID: {candidate_id}")
        if candidate_id not in known_ids:
            raise ValueError(f"unknown review ID: {candidate_id}")
        seen_ids.add(candidate_id)
        topic = row["topic"]
        if topic and topic not in REVIEW_TOPICS:
            raise ValueError(f"invalid review topic: {topic}")
        if finalization and not topic:
            raise ValueError(f"topic is required for finalization: {candidate_id}")
        delete_value = row["delete"]
        if delete_value not in DELETE_VALUES:
            raise ValueError(f"invalid delete value for {candidate_id}: {delete_value}")
        if delete_value == "Yes" and (row["edited_question"] or row["edited_reference_answer"]):
            raise ValueError(f"deleted row cannot contain edited Q/A: {candidate_id}")


def apply_review_rows(state: dict[str, Any], rows: Iterable[dict[str, str]]) -> dict[str, Any]:
    """Apply review edits as append-only revisions without running network checks."""
    updated = deepcopy(state)
    active = accepted_review_bundles(updated)
    known_ids = {str(bundle["artifact"]["id"]) for bundle in active}
    row_list = list(rows)
    validate_review_rows(row_list, known_ids=known_ids)
    rows_by_id = {row["id"]: row for row in row_list}
    for bundle in updated["candidates"]:
        artifact = Route3CandidateArtifact.from_dict(bundle["artifact"])
        row = rows_by_id.get(artifact.candidate_id)
        if row is None:
            continue
        current = artifact.current_revision
        edited_question = row["edited_question"] or None
        edited_answer = row["edited_reference_answer"] or None
        delete = row["delete"] == "Yes"
        topic = row["topic"]
        if (
            edited_question is None
            and edited_answer is None
            and delete == current.delete
            and topic == current.topic
        ):
            continue
        artifact = revise_route3_candidate_artifact(
            artifact,
            edited_question=edited_question,
            edited_reference_answer=edited_answer,
            topic=topic,
            delete=delete,
            edit_reason=row["edit_reason"],
        )
        bundle["artifact"] = artifact.to_dict()
        active_record = bundle["active_record"]
        active_record["topic"] = artifact.current_revision.topic
        if edited_question is not None or edited_answer is not None:
            active_record["question"] = artifact.current_revision.authoritative_question
            active_record["canonical_question"] = artifact.current_revision.authoritative_question
            active_record["answer"] = artifact.current_revision.reference_answer
            active_record["answer_aliases"] = list(artifact.current_revision.active_aliases)
            active_record["search_queries"] = list(artifact.current_revision.active_search_queries)
            active_record["validation"] = {}
            active_record["search_verification_features"] = {}
            active_record["panel_grading_features"] = {}
            active_record["source_metadata"].pop("rule_based_qa_gate", None)
    return updated


def rerun_review_candidates(
    state: dict[str, Any],
    *,
    processor: Callable[[GeneratedCandidate], tuple[str, dict[str, Any]]],
) -> dict[str, Any]:
    """Run fresh post-generation processing for every active rerun revision."""
    updated = deepcopy(state)
    for bundle in updated["candidates"]:
        artifact = Route3CandidateArtifact.from_dict(bundle["artifact"])
        if artifact.current_revision.status != "rerun":
            continue
        candidate = _generated_candidate(bundle["active_record"], artifact)
        status, processed_record = processor(candidate)
        processed_record["id"] = artifact.candidate_id
        processed_record["topic"] = artifact.current_revision.topic
        metadata = processed_record["source_metadata"]
        artifact = complete_route3_candidate_rerun(
            artifact,
            source_validation=processed_record["validation"],
            integrated_answer_type_gate=metadata.get("rule_based_qa_gate", {}),
            ddg=processed_record["search_verification_features"],
            second_stage=processed_record["panel_grading_features"],
            status=status,
        )
        bundle["artifact"] = artifact.to_dict()
        bundle["active_record"] = processed_record
    return updated


def post_generation_processor(
    *,
    settings,
    search_client,
    second_stage_model_clients,
    grading_grader_client,
) -> Callable[[GeneratedCandidate], tuple[str, dict[str, Any]]]:
    """Build a processor that executes the formal post-generation pipeline."""
    from .generation_pipeline import process_generated_candidates

    def process(candidate: GeneratedCandidate) -> tuple[str, dict[str, Any]]:
        result = process_generated_candidates(
            [candidate],
            settings=settings,
            search_client=search_client,
            rewrite_client=None,
            second_stage_model_clients=second_stage_model_clients,
            grading_grader_client=grading_grader_client,
        )
        if result.accepted:
            return "accepted", result.accepted[0]
        record = result.rejected[0]
        status = "rerun" if str(record["rejection_reason"]) in RERUN_REJECTION_REASONS else "rejected"
        return status, record

    return process


def _review_bundle(record: dict[str, Any]) -> dict[str, Any]:
    metadata = record["source_metadata"]
    identity = route3_record_identity(record)
    llm_audit = metadata["llm_audit"]
    selected_table = metadata["selected_source_table"]
    provenance = Route3CandidateProvenance(
        run_group_id=identity.run_group_id,
        segment_id=identity.segment_id,
        page_attempt=int(metadata["page_attempt"]),
        canonical_page_id=identity.canonical_page_id,
        canonical_page_url=str(metadata["canonical_url"]),
        selected_table=deepcopy(selected_table),
        selected_table_type=str(selected_table["table_type"]),
        page_archive_hash=str(metadata["route3_page_archive"]["archive_sha256"]),
        generation_prompt=str(metadata["llm_prompt"]),
        generation_request=deepcopy(llm_audit["request_payload"]),
        generation_raw_response=deepcopy(metadata["llm_response"]),
        original_question=str(record["question"]),
        original_reference_answer=str(record["answer"]),
        original_aliases=tuple(str(value) for value in record["answer_aliases"]),
        original_search_queries=tuple(str(value) for value in record["search_queries"]),
        answer_type=str(record["answer_type"]),
        generation_model=str(metadata["generation_model"]),
        generation_parameters=deepcopy(metadata["generation_parameters"]),
        recipe_seed=metadata["recipe_seed"],
    )
    artifact = create_route3_candidate_artifact(
        identity=identity,
        provenance=provenance,
        question=str(record["question"]),
        reference_answer=str(record["answer"]),
        aliases=tuple(str(value) for value in record["answer_aliases"]),
        search_queries=tuple(str(value) for value in record["search_queries"]),
        topic=str(record["topic"]),
        source_validation=record["validation"],
        integrated_answer_type_gate=metadata["rule_based_qa_gate"],
        ddg=record["search_verification_features"],
        second_stage=record["panel_grading_features"],
        status="accepted",
    )
    return {"artifact": artifact.to_dict(), "active_record": deepcopy(record)}


def _generated_candidate(record: dict[str, Any], artifact: Route3CandidateArtifact) -> GeneratedCandidate:
    revision = artifact.current_revision
    subject = record["subject_entity"]
    evidence = record["evidence"]
    return GeneratedCandidate(
        source_type=str(record["source_type"]),
        generation_route=str(record["generation_route"]),
        question=revision.authoritative_question,
        answer=revision.reference_answer,
        answer_aliases=list(revision.active_aliases),
        subject_entity=EntityReference(**subject),
        answer_entity=EntityReference(name=revision.reference_answer),
        relation_or_claim=str(record["relation_or_claim"]),
        evidence=EvidenceRecord(**evidence),
        canonical_question=revision.authoritative_question,
        question_family=str(record["question_family"]),
        answer_type=artifact.provenance.answer_type,
        topic=revision.topic,
        target_time=str(record["target_time"]),
        source_template_domain=str(record["template_key"]),
        search_queries=list(revision.active_search_queries),
        source_metadata=deepcopy(record["source_metadata"]),
    )
