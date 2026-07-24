"""Pre-review quantity prediction for formal Route 3 candidates."""

from __future__ import annotations

import math
import random
from collections import Counter, defaultdict
from typing import Any, Iterable


ANSWER_TYPE_RATIOS = {
    "Person": 0.198,
    "Place": 0.146,
    "Number": 0.185,
    "Date": 0.222,
    "Other": 0.249,
}
ANSWER_TYPES = tuple(ANSWER_TYPE_RATIOS)


def assign_canonical_pages(
    records: Iterable[dict[str, Any]],
    *,
    recipe_seed: int,
) -> list[dict[str, Any]]:
    """Choose one candidate per canonical page using the formal allocation order."""
    rows = list(records)
    pages: dict[int, list[dict[str, Any]]] = defaultdict(list)
    raw_counts = Counter({answer_type: 0 for answer_type in ANSWER_TYPES})
    for record in rows:
        answer_type = _answer_type(record)
        raw_counts[answer_type] += 1
        pages[_canonical_page_id(record)].append(record)

    assignments: list[dict[str, Any]] = []
    assigned_counts = Counter({answer_type: 0 for answer_type in ANSWER_TYPES})
    for page_id in sorted(page_id for page_id, candidates in pages.items() if len(candidates) == 1):
        record = pages[page_id][0]
        answer_type = _answer_type(record)
        assignments.append(_assignment(page_id, answer_type, record))
        assigned_counts[answer_type] += 1

    rng = random.Random(recipe_seed)
    for page_id in sorted(page_id for page_id, candidates in pages.items() if len(candidates) > 1):
        candidates_by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for record in pages[page_id]:
            candidates_by_type[_answer_type(record)].append(record)
        available_types = sorted(candidates_by_type)
        minimum_assigned = min(assigned_counts[answer_type] for answer_type in available_types)
        tied_types = [
            answer_type
            for answer_type in available_types
            if assigned_counts[answer_type] == minimum_assigned
        ]
        minimum_raw = min(raw_counts[answer_type] for answer_type in tied_types)
        tied_types = [answer_type for answer_type in tied_types if raw_counts[answer_type] == minimum_raw]
        answer_type = rng.choice(tied_types)
        record = min(
            candidates_by_type[answer_type],
            key=lambda candidate: (_ddg_overall_hit_rate(candidate), _candidate_id(candidate)),
        )
        assignments.append(_assignment(page_id, answer_type, record))
        assigned_counts[answer_type] += 1

    return sorted(assignments, key=lambda assignment: int(assignment["canonical_page_id"]))


def predict_pre_review_quantities(
    records: Iterable[dict[str, Any]],
    *,
    recipe_seed: int,
) -> dict[str, Any]:
    """Predict post-page-dedup and answer-type rebalance quantities."""
    rows = list(records)
    assignments = assign_canonical_pages(rows, recipe_seed=recipe_seed)
    page_counts = Counter(_canonical_page_id(record) for record in rows)
    assigned_counts = Counter({answer_type: 0 for answer_type in ANSWER_TYPES})
    for assignment in assignments:
        assigned_counts[str(assignment["answer_type"])] += 1

    rebalance_n = min(
        math.ceil(assigned_counts[answer_type] / ANSWER_TYPE_RATIOS[answer_type])
        for answer_type in ANSWER_TYPES
    )
    projected_targets = {
        answer_type: min(
            assigned_counts[answer_type],
            math.ceil(rebalance_n * ANSWER_TYPE_RATIOS[answer_type]),
        )
        for answer_type in ANSWER_TYPES
    }
    return {
        "accepted_total": len(rows),
        "canonical_unique_pages": len(page_counts),
        "multi_qa_pages": sum(count > 1 for count in page_counts.values()),
        "assigned_answer_type_counts": dict(assigned_counts),
        "recipe_seed": recipe_seed,
        "rebalance_n": rebalance_n,
        "projected_answer_type_targets": projected_targets,
        "projected_final_total": sum(projected_targets.values()),
    }


def _assignment(page_id: int, answer_type: str, record: dict[str, Any]) -> dict[str, Any]:
    return {
        "canonical_page_id": page_id,
        "answer_type": answer_type,
        "candidate_id": _candidate_id(record),
    }


def _canonical_page_id(record: dict[str, Any]) -> int:
    return int(record["source_metadata"]["canonical_page_id"])


def _answer_type(record: dict[str, Any]) -> str:
    answer_type = str(record["answer_type"])
    if answer_type not in ANSWER_TYPE_RATIOS:
        raise ValueError(f"Unsupported Route 3 answer type: {answer_type}")
    return answer_type


def _candidate_id(record: dict[str, Any]) -> str:
    return str(record["id"])


def _ddg_overall_hit_rate(record: dict[str, Any]) -> float:
    return float(
        record["search_verification_features"]["category_hit_rates"]["overall"]["answer_hit_rate"]
    )
