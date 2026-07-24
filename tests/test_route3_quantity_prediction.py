"""Tests for Route 3 pre-review quantity prediction."""

from __future__ import annotations

from copy import deepcopy

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.route3_quantity_prediction import (
    ANSWER_TYPES,
    assign_canonical_pages,
    predict_pre_review_quantities,
)


def candidate(
    candidate_id: str,
    page_id: int,
    answer_type: str,
    *,
    ddg_overall_hit_rate: float = 0.0,
    topic: str = "",
) -> dict:
    """Build one formal accepted candidate for allocation tests."""
    return {
        "id": candidate_id,
        "answer_type": answer_type,
        "topic": topic,
        "source_metadata": {"canonical_page_id": page_id},
        "search_verification_features": {
            "category_hit_rates": {
                "overall": {"answer_hit_rate": ddg_overall_hit_rate},
            }
        },
    }


def test_allocation_is_independent_of_input_order_and_records_seed() -> None:
    records = [
        candidate("single-person", 1, "Person"),
        candidate("single-place", 2, "Place"),
        candidate("date-10", 10, "Date"),
        candidate("other-10", 10, "Other"),
        candidate("number-11", 11, "Number"),
        candidate("person-11", 11, "Person"),
    ]

    forward = assign_canonical_pages(records, recipe_seed=42)
    reverse = assign_canonical_pages(reversed(records), recipe_seed=42)
    prediction = predict_pre_review_quantities(records, recipe_seed=42)

    assert forward == reverse
    assert prediction["recipe_seed"] == 42
    assert prediction["accepted_total"] == 6
    assert prediction["canonical_unique_pages"] == 4
    assert prediction["multi_qa_pages"] == 2


def test_allocation_only_uses_types_present_on_each_page() -> None:
    records = [
        candidate("person-1", 1, "Person"),
        candidate("place-20", 20, "Place"),
        candidate("other-20", 20, "Other"),
    ]

    assignments = assign_canonical_pages(records, recipe_seed=7)
    page_20 = next(row for row in assignments if row["canonical_page_id"] == 20)

    assert page_20["answer_type"] in {"Place", "Other"}
    assert page_20["answer_type"] != "Person"


def test_allocation_prefers_lower_assigned_count_then_lower_raw_count() -> None:
    assigned_count_records = [
        candidate("single-person", 1, "Person"),
        candidate("person-10", 10, "Person"),
        candidate("place-10", 10, "Place"),
    ]
    assigned_count_rows = assign_canonical_pages(assigned_count_records, recipe_seed=3)
    assert next(row for row in assigned_count_rows if row["canonical_page_id"] == 10)["answer_type"] == "Place"

    raw_count_records = [
        candidate("person-10", 10, "Person"),
        candidate("place-10", 10, "Place"),
        candidate("person-20", 20, "Person"),
        candidate("date-20", 20, "Date"),
    ]
    raw_count_rows = assign_canonical_pages(raw_count_records, recipe_seed=3)
    assert next(row for row in raw_count_rows if row["canonical_page_id"] == 10)["answer_type"] == "Place"

def test_same_page_same_type_prefers_lower_ddg_then_candidate_id() -> None:
    records = [
        candidate("person-high", 30, "Person", ddg_overall_hit_rate=0.2),
        candidate("person-z", 30, "Person", ddg_overall_hit_rate=0.1),
        candidate("person-a", 30, "Person", ddg_overall_hit_rate=0.1),
    ]

    assignments = assign_canonical_pages(records, recipe_seed=9)

    assert assignments == [
        {
            "canonical_page_id": 30,
            "answer_type": "Person",
            "candidate_id": "person-a",
        }
    ]


def test_prediction_uses_rebalance_formula_without_topic_selection() -> None:
    records = [
        candidate(f"{answer_type}-1", index, answer_type, topic=f"topic-{index}")
        for index, answer_type in enumerate(ANSWER_TYPES, start=1)
    ]
    original = deepcopy(records)

    prediction = predict_pre_review_quantities(records, recipe_seed=13)

    assert prediction["assigned_answer_type_counts"] == {
        "Person": 1,
        "Place": 1,
        "Number": 1,
        "Date": 1,
        "Other": 1,
    }
    assert prediction["rebalance_n"] == 5
    assert prediction["projected_answer_type_targets"] == {
        "Person": 1,
        "Place": 1,
        "Number": 1,
        "Date": 1,
        "Other": 1,
    }
    assert prediction["projected_final_total"] == 5
    assert records == original
