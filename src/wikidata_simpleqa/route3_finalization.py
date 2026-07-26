"""Formal canonical-page deduplication and final selection for Route 3."""

from __future__ import annotations

import csv
import json
import random
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from .route3_artifacts import Route3CandidateArtifact
from .route3_quantity_prediction import (
    ANSWER_TYPES,
    assign_canonical_pages,
    rebalance_targets,
)
from .route3_review import accepted_review_bundles, validate_review_rows


FINAL_CSV_COLUMNS = ("id", "problem", "answer", "topic", "answer_type", "urls")


def finalize_review_state(
    state: dict[str, Any],
    *,
    review_rows: Iterable[dict[str, str]],
) -> dict[str, Any]:
    """Validate reviewed candidates and return the reproducible final selection."""
    rows = list(review_rows)
    bundles = accepted_review_bundles(state)
    _validate_finalization(state, bundles=bundles, rows=rows)
    artifacts_by_id = {
        str(bundle["artifact"]["id"]): Route3CandidateArtifact.from_dict(bundle["artifact"])
        for bundle in bundles
    }
    records_by_id = {
        str(bundle["artifact"]["id"]): bundle["active_record"]
        for bundle in bundles
    }
    recipe_seeds = {artifact.provenance.recipe_seed for artifact in artifacts_by_id.values()}
    if len(recipe_seeds) != 1:
        raise ValueError("finalization requires one recipe seed across active candidates")
    recipe_seed = int(recipe_seeds.pop())

    assignments = assign_canonical_pages(records_by_id.values(), recipe_seed=recipe_seed)
    selected_ids = [str(assignment["candidate_id"]) for assignment in assignments]
    selected_artifacts = {candidate_id: artifacts_by_id[candidate_id] for candidate_id in selected_ids}
    answer_type_counts = Counter({answer_type: 0 for answer_type in ANSWER_TYPES})
    for artifact in selected_artifacts.values():
        answer_type_counts[artifact.provenance.answer_type] += 1
    zero_answer_types = [
        answer_type for answer_type in ANSWER_TYPES if answer_type_counts[answer_type] == 0
    ]
    if zero_answer_types:
        rebalance_n = None
        targets = dict(answer_type_counts)
        final_ids = set(selected_artifacts)
    else:
        rebalance_n, targets = rebalance_targets(answer_type_counts)
        final_ids = _remove_topic_excess(
            selected_artifacts,
            answer_type_counts=answer_type_counts,
            targets=targets,
            recipe_seed=recipe_seed,
        )
    final_records = [_final_csv_record(selected_artifacts[candidate_id]) for candidate_id in sorted(final_ids)]
    final_counts = Counter(record["answer_type"] for record in final_records)
    return {
        "records": final_records,
        "summary": {
            "recipe_seed": recipe_seed,
            "accepted_before_page_dedup": len(bundles),
            "canonical_pages_after_dedup": len(assignments),
            "rebalance_skipped": bool(zero_answer_types),
            "zero_answer_types": zero_answer_types,
            "rebalance_n": rebalance_n,
            "answer_type_targets": targets,
            "final_answer_type_counts": {
                answer_type: final_counts[answer_type]
                for answer_type in ANSWER_TYPES
            },
            "final_total": len(final_records),
            "selected_candidate_ids": [record["id"] for record in final_records],
        },
    }


def write_final_csv(path: Path, records: Iterable[dict[str, str]]) -> None:
    """Write the exact formal final CSV columns."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(FINAL_CSV_COLUMNS))
        writer.writeheader()
        writer.writerows(records)


def _validate_finalization(
    state: dict[str, Any],
    *,
    bundles: list[dict[str, Any]],
    rows: list[dict[str, str]],
) -> None:
    for bundle in state["candidates"]:
        artifact = Route3CandidateArtifact.from_dict(bundle["artifact"])
        if artifact.current_revision.status == "rerun":
            raise ValueError(f"unresolved rerun: {artifact.candidate_id}")
    known_ids = {str(bundle["artifact"]["id"]) for bundle in bundles}
    validate_review_rows(rows, known_ids=known_ids, finalization=True)
    row_ids = {row["id"] for row in rows}
    if row_ids != known_ids:
        missing = sorted(known_ids - row_ids)
        raise ValueError(f"XLSX IDs do not match active candidate revisions; missing={missing}")
    rows_by_id = {row["id"]: row for row in rows}
    for bundle in bundles:
        artifact = Route3CandidateArtifact.from_dict(bundle["artifact"])
        revision = artifact.current_revision
        row = rows_by_id[artifact.candidate_id]
        if row["edited_question"] or row["edited_reference_answer"]:
            raise ValueError(f"unprocessed Q/A edit: {artifact.candidate_id}")
        if row["question"] != revision.authoritative_question:
            raise ValueError(f"XLSX question does not match candidate revision: {artifact.candidate_id}")
        if row["reference_answer"] != revision.reference_answer:
            raise ValueError(f"XLSX answer does not match candidate revision: {artifact.candidate_id}")
        if row["wikipedia_url"] != artifact.provenance.canonical_page_url:
            raise ValueError(f"XLSX URL does not match candidate provenance: {artifact.candidate_id}")
        if row["topic"] != revision.topic:
            raise ValueError(f"XLSX topic does not match candidate revision: {artifact.candidate_id}")
        if row["delete"] != "No":
            raise ValueError(f"active finalization row must use delete=No: {artifact.candidate_id}")


def _remove_topic_excess(
    artifacts: dict[str, Route3CandidateArtifact],
    *,
    answer_type_counts: Counter,
    targets: dict[str, int],
    recipe_seed: int,
) -> set[str]:
    selected_ids = set(artifacts)
    topic_counts = Counter(artifact.current_revision.topic for artifact in artifacts.values())
    rng = random.Random(recipe_seed)
    while any(answer_type_counts[answer_type] > targets[answer_type] for answer_type in ANSWER_TYPES):
        eligible_ids = sorted(
            candidate_id
            for candidate_id in selected_ids
            if answer_type_counts[artifacts[candidate_id].provenance.answer_type]
            > targets[artifacts[candidate_id].provenance.answer_type]
        )
        largest_topic_count = max(
            topic_counts[artifacts[candidate_id].current_revision.topic]
            for candidate_id in eligible_ids
        )
        tied_ids = [
            candidate_id
            for candidate_id in eligible_ids
            if topic_counts[artifacts[candidate_id].current_revision.topic] == largest_topic_count
        ]
        removed_id = rng.choice(tied_ids)
        removed = artifacts[removed_id]
        selected_ids.remove(removed_id)
        answer_type_counts[removed.provenance.answer_type] -= 1
        topic_counts[removed.current_revision.topic] -= 1
    return selected_ids


def _final_csv_record(artifact: Route3CandidateArtifact) -> dict[str, str]:
    revision = artifact.current_revision
    return {
        "id": artifact.candidate_id,
        "problem": revision.authoritative_question,
        "answer": revision.reference_answer,
        "topic": revision.topic,
        "answer_type": artifact.provenance.answer_type,
        "urls": json.dumps([artifact.provenance.canonical_page_url], ensure_ascii=False),
    }
