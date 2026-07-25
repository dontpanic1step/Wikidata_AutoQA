"""Tests for formal Route 3 finalization."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

import pytest

from test_support import ROOT  # noqa: F401
from test_route3_review import accepted_record, review_row
from wikidata_simpleqa.route3_finalization import (
    FINAL_CSV_COLUMNS,
    finalize_review_state,
    write_final_csv,
)
from wikidata_simpleqa.route3_review import (
    apply_review_rows,
    create_review_state,
    write_review_state,
    write_review_workbook,
)


def finalized_inputs() -> tuple[dict, list[dict[str, str]], set[str]]:
    """Build reviewed candidates with five available rows per answer type."""
    answer_types = ("Person", "Place", "Number", "Date", "Other")
    records = []
    page_id = 1
    for answer_type in answer_types:
        for _ in range(5):
            records.append(accepted_record(page_id=page_id, answer_type=answer_type))
            page_id += 1
    records.append(accepted_record(page_id=1, slot="Place", answer_type="Place"))
    state = create_review_state(
        records,
        segment_fingerprints={"01_alltypes_10": {"sha256": "fingerprint"}},
        segment_artifact_roots={"01_alltypes_10": "C:/artifacts/01_alltypes_10"},
    )
    rows = [review_row(record["id"], topic="History") for record in records]
    state = apply_review_rows(state, rows)
    final_rows = [
        review_row(
            str(bundle["artifact"]["id"]),
            topic="History",
        )
        for bundle in state["candidates"]
    ]
    return state, final_rows, {record["id"] for record in records}


def test_finalization_deduplicates_pages_and_hits_answer_type_targets() -> None:
    state, rows, source_ids = finalized_inputs()

    result = finalize_review_state(state, review_rows=rows)

    summary = result["summary"]
    assert summary["accepted_before_page_dedup"] == 26
    assert summary["canonical_pages_after_dedup"] == 25
    assert summary["rebalance_n"] == 21
    assert summary["answer_type_targets"] == {
        "Person": 5,
        "Place": 4,
        "Number": 4,
        "Date": 5,
        "Other": 5,
    }
    assert summary["final_answer_type_counts"] == summary["answer_type_targets"]
    assert summary["final_total"] == 23
    assert set(summary["selected_candidate_ids"]) <= source_ids
    page_ids = {
        next(
            bundle["artifact"]["identity"]["canonical_page_id"]
            for bundle in state["candidates"]
            if bundle["artifact"]["id"] == record["id"]
        )
        for record in result["records"]
    }
    assert len(page_ids) == len(result["records"])


def test_finalization_is_seeded_and_independent_of_input_order() -> None:
    state, rows, _ = finalized_inputs()
    reversed_state = deepcopy(state)
    reversed_state["candidates"].reverse()

    forward = finalize_review_state(state, review_rows=rows)
    reverse = finalize_review_state(reversed_state, review_rows=reversed(rows))

    assert forward == reverse
    assert forward["summary"]["recipe_seed"] == 42


def test_finalization_rejects_unready_review_state() -> None:
    record = accepted_record()
    state = create_review_state(
        [record],
        segment_fingerprints={"01_alltypes_10": {}},
        segment_artifact_roots={"01_alltypes_10": "C:/artifacts/01_alltypes_10"},
    )
    candidate_id = record["id"]

    with pytest.raises(ValueError, match="topic is required"):
        finalize_review_state(state, review_rows=[review_row(candidate_id, topic="")])

    reviewed = apply_review_rows(state, [review_row(candidate_id, topic="History")])
    with pytest.raises(ValueError, match="missing"):
        finalize_review_state(reviewed, review_rows=[])
    with pytest.raises(ValueError, match="unprocessed Q/A edit"):
        finalize_review_state(
            reviewed,
            review_rows=[review_row(candidate_id, topic="History", edited_question="Edited?")],
        )
    with pytest.raises(ValueError, match="question does not match"):
        finalize_review_state(
            reviewed,
            review_rows=[review_row(candidate_id, topic="History", question="Stale question?")],
        )

    rerun = apply_review_rows(
        reviewed,
        [review_row(candidate_id, topic="History", edited_question="Edited?")],
    )
    with pytest.raises(ValueError, match="unresolved rerun"):
        finalize_review_state(
            rerun,
            review_rows=[review_row(candidate_id, topic="History")],
        )


def test_final_csv_has_exact_columns_and_json_urls() -> None:
    state, rows, _ = finalized_inputs()
    result = finalize_review_state(state, review_rows=rows)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "final.csv"
        write_final_csv(path, result["records"])
        with path.open("r", encoding="utf-8", newline="") as handle:
            csv_rows = list(csv.DictReader(handle))
            assert tuple(csv_rows[0]) == FINAL_CSV_COLUMNS
            assert isinstance(json.loads(csv_rows[0]["urls"]), list)
            assert json.loads(csv_rows[0]["urls"])[0].startswith("https://en.wikipedia.org/")


def test_finalization_cli_writes_traceable_csv() -> None:
    state, _, source_ids = finalized_inputs()
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        state_path = root / "review_state.json"
        workbook_path = root / "review.xlsx"
        output_path = root / "final.csv"
        write_review_state(state_path, state)
        write_review_workbook(workbook_path, state)

        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "finalize_route3_review.py"),
                "--state-input",
                str(state_path),
                "--xlsx-input",
                str(workbook_path),
                "--output",
                str(output_path),
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        summary = json.loads(completed.stdout)
        assert summary["final_total"] == 23
        with output_path.open("r", encoding="utf-8", newline="") as handle:
            output_ids = {row["id"] for row in csv.DictReader(handle)}
        assert output_ids <= source_ids
