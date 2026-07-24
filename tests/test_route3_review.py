"""Tests for the formal Route 3 manual review loop."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

import pytest
from openpyxl import load_workbook

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.route3_artifacts import Route3CandidateArtifact
from wikidata_simpleqa.route3_ids import route3_record_id
from wikidata_simpleqa.route3_review import (
    REVIEW_COLUMNS,
    REVIEW_TOPICS,
    accepted_review_bundles,
    apply_review_rows,
    create_review_state,
    read_review_workbook,
    render_review_markdown,
    rerun_review_candidates,
    validate_review_rows,
    write_review_workbook,
)


def accepted_record(
    *,
    page_id: int = 123,
    slot: str = "single",
    answer_type: str = "Person",
    segment_id: str = "01_alltypes_10",
) -> dict:
    """Build one complete formal accepted record."""
    record = {
        "id": "",
        "question": "Who founded the archive?",
        "canonical_question": "Who founded the archive?",
        "answer": "Ada Example",
        "answer_aliases": ["A. Example"],
        "source_type": "wikipedia_tables",
        "generation_route": "route3_wikipedia_infobox",
        "subject_entity": {
            "name": "Archive",
            "qid": "",
            "wikipedia_title": "Archive",
            "url": "https://en.wikipedia.org/wiki/Archive",
        },
        "answer_entity": {
            "name": "Ada Example",
            "qid": "",
            "wikipedia_title": "",
            "url": "",
        },
        "relation_or_claim": "founder",
        "evidence": {
            "text": "| Founder | Ada Example |",
            "url": "https://en.wikipedia.org/wiki/Archive",
            "source_title": "Archive",
            "section": "",
            "retrieved_at": "2026-07-24T00:00:00Z",
        },
        "question_family": "wikipedia_table_single_fact",
        "answer_type": answer_type,
        "template_key": "wikipedia_infobox_table",
        "topic": "",
        "target_time": "2024",
        "search_queries": ["archive founder"],
        "search_verification_features": {
            "passed": True,
            "category_hit_rates": {"overall": {"answer_hit_rate": 0.0}},
        },
        "panel_grading_features": {
            "models": [
                {
                    "model": "openai/gpt-4.1-mini",
                    "predicted_answer": "Ada Example",
                    "grade": "CORRECT",
                    "reason": "Matched.",
                },
                {
                    "model": "google/gemini-3-flash-preview",
                    "predicted_answer": "Ada Example",
                    "grade": "CORRECT",
                    "reason": "Matched.",
                },
            ]
        },
        "validation": {"passed": True},
        "source_metadata": {
            "run_group_id": "review-run",
            "segment_id": segment_id,
            "canonical_page_id": page_id,
            "original_candidate_slot": slot,
            "page_attempt": 1,
            "canonical_url": "https://en.wikipedia.org/wiki/Archive",
            "selected_source_table": {
                "table_type": "infobox",
                "markdown": "| Field | Value |\n| --- | --- |\n| Founder | Ada Example |",
            },
            "route3_page_archive": {"archive_sha256": "abc123"},
            "llm_prompt": "Generate one question.",
            "llm_response": {"question": "Who founded the archive?"},
            "llm_audit": {"request_payload": {"messages": []}},
            "generation_model": "google/gemini-3-flash-preview",
            "generation_parameters": {"max_tokens": 4096},
            "recipe_seed": 42,
            "rule_based_qa_gate": {"status": "matched"},
        },
    }
    record["id"] = route3_record_id(record)
    return record


def review_row(candidate_id: str, **overrides: str) -> dict[str, str]:
    """Build one valid workbook row."""
    row = {
        "id": candidate_id,
        "question": "Who founded the archive?",
        "reference_answer": "Ada Example",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Archive",
        "topic": "History",
        "delete": "No",
        "edited_question": "",
        "edited_reference_answer": "",
        "edit_reason": "",
    }
    row.update(overrides)
    return row


def test_review_state_requires_each_top_up_segment_fingerprint() -> None:
    records = [
        accepted_record(page_id=123, segment_id="01_alltypes_10"),
        accepted_record(page_id=456, segment_id="01_alltypes_10_topup_01"),
    ]

    with pytest.raises(ValueError, match="missing segment fingerprints"):
        create_review_state(
            records,
            segment_fingerprints={"01_alltypes_10": {"sha256": "first"}},
        )

    state = create_review_state(
        records,
        segment_fingerprints={
            "01_alltypes_10": {"sha256": "first"},
            "01_alltypes_10_topup_01": {"sha256": "second"},
        },
    )
    assert set(state["segment_fingerprints"]) == {
        "01_alltypes_10",
        "01_alltypes_10_topup_01",
    }

def test_export_cli_writes_review_state_markdown_and_xlsx() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        accepted_path = root / "accepted.jsonl"
        manifest_path = root / "segment_manifest.json"
        state_path = root / "review_state.json"
        markdown_path = root / "review.md"
        workbook_path = root / "review.xlsx"
        accepted_path.write_text(json.dumps(accepted_record()) + "\n", encoding="utf-8")
        manifest_path.write_text(json.dumps({"segment_id": "01_alltypes_10", "fingerprint": {"sha256": "test"}}), encoding="utf-8")

        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "run_route3_review.py"),
                "export",
                "--accepted-input",
                str(accepted_path),
                "--segment-manifest",
                str(manifest_path),
                "--state-output",
                str(state_path),
                "--markdown-output",
                str(markdown_path),
                "--xlsx-output",
                str(workbook_path),
                "--run-id",
                "review-run",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        assert state_path.exists()
        assert markdown_path.exists()
        assert workbook_path.exists()
        assert json.loads(completed.stdout)["accepted"] == 1
        assert load_workbook(workbook_path)["review"]["F2"].value == "No"
        workbook = load_workbook(workbook_path)
        workbook["review"]["E2"] = "History"
        workbook.save(workbook_path)
        next_state_path = root / "review_state_next.json"
        next_markdown_path = root / "review_next.md"
        next_workbook_path = root / "review_next.xlsx"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "run_route3_review.py"),
                "apply",
                "--state-input",
                str(state_path),
                "--xlsx-input",
                str(workbook_path),
                "--state-output",
                str(next_state_path),
                "--markdown-output",
                str(next_markdown_path),
                "--xlsx-output",
                str(next_workbook_path),
                "--run-id",
                "review-run",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        next_state = json.loads(next_state_path.read_text(encoding="utf-8"))
        next_revision = next_state["candidates"][0]["artifact"]["revisions"][-1]
        assert next_revision["topic"] == "History"
        assert next_revision["status"] == "accepted"
        assert load_workbook(next_workbook_path)["review"]["E2"].value == "History"

def test_markdown_and_workbook_show_only_formal_review_fields() -> None:
    state = create_review_state([accepted_record()], segment_fingerprints={"01_alltypes_10": {"sha256": "fingerprint"}})
    candidate_id = state["candidates"][0]["artifact"]["id"]

    markdown = render_review_markdown(state, run_id="review-run")

    assert candidate_id in markdown
    assert "Who founded the archive?" in markdown
    assert "Ada Example" in markdown
    assert "Canonical page ID: `123`" in markdown
    assert "| Founder | Ada Example |" in markdown
    assert "openai/gpt-4.1-mini" in markdown
    assert "google/gemini-3-flash-preview" in markdown

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "review.xlsx"
        write_review_workbook(path, state)
        workbook = load_workbook(path)
        worksheet = workbook["review"]
        assert tuple(cell.value for cell in worksheet[1]) == REVIEW_COLUMNS
        assert worksheet["F2"].value == "No"
        assert len(worksheet.data_validations.dataValidation) == 2
        formulas = {validation.formula1 for validation in worksheet.data_validations.dataValidation}
        assert '"' + ",".join(REVIEW_TOPICS) + '"' in formulas
        assert read_review_workbook(path)[0]["id"] == candidate_id


def test_workbook_rejects_noncanonical_header() -> None:
    state = create_review_state([accepted_record()], segment_fingerprints={"01_alltypes_10": {}})
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "review.xlsx"
        write_review_workbook(path, state)
        workbook = load_workbook(path)
        workbook["review"]["A1"] = "编号"
        workbook.save(path)

        with pytest.raises(ValueError, match="exactly match"):
            read_review_workbook(path)


def test_review_validation_rejects_invalid_rows() -> None:
    candidate_id = accepted_record()["id"]
    known_ids = {candidate_id}

    with pytest.raises(ValueError, match="duplicate"):
        validate_review_rows(
            [review_row(candidate_id), review_row(candidate_id)],
            known_ids=known_ids,
        )
    with pytest.raises(ValueError, match="unknown"):
        validate_review_rows([review_row("unknown")], known_ids=known_ids)
    with pytest.raises(ValueError, match="invalid review topic"):
        validate_review_rows([review_row(candidate_id, topic="Invalid")], known_ids=known_ids)
    with pytest.raises(ValueError, match="topic is required"):
        validate_review_rows(
            [review_row(candidate_id, topic="")],
            known_ids=known_ids,
            finalization=True,
        )
    with pytest.raises(ValueError, match="invalid delete"):
        validate_review_rows([review_row(candidate_id, delete="Maybe")], known_ids=known_ids)
    with pytest.raises(ValueError, match="deleted row"):
        validate_review_rows(
            [review_row(candidate_id, delete="Yes", edited_question="Edited?")],
            known_ids=known_ids,
        )


def test_question_edit_preserves_id_and_aliases_but_clears_old_checks() -> None:
    original_record = accepted_record()
    state = create_review_state([original_record], segment_fingerprints={"01_alltypes_10": {}})
    candidate_id = original_record["id"]

    updated = apply_review_rows(
        state,
        [review_row(candidate_id, edited_question="Who established the archive?", edit_reason="Clarity")],
    )
    artifact = Route3CandidateArtifact.from_dict(updated["candidates"][0]["artifact"])

    assert artifact.candidate_id == candidate_id
    assert len(artifact.revisions) == 2
    assert artifact.revisions[0].authoritative_question == "Who founded the archive?"
    assert artifact.current_revision.authoritative_question == "Who established the archive?"
    assert artifact.current_revision.active_aliases == ("A. Example",)
    assert artifact.current_revision.ddg == {}
    assert artifact.current_revision.second_stage == {}
    assert artifact.current_revision.status == "rerun"


def test_answer_edit_clears_aliases_and_delete_skips_rerun() -> None:
    original_record = accepted_record()
    state = create_review_state([original_record], segment_fingerprints={"01_alltypes_10": {}})
    candidate_id = original_record["id"]
    answer_edited = apply_review_rows(
        state,
        [review_row(candidate_id, edited_reference_answer="Grace Example")],
    )
    artifact = Route3CandidateArtifact.from_dict(answer_edited["candidates"][0]["artifact"])
    assert artifact.current_revision.active_aliases == ()

    deleted = apply_review_rows(state, [review_row(candidate_id, delete="Yes")])
    calls = []
    rerun = rerun_review_candidates(
        deleted,
        processor=lambda candidate: calls.append(candidate) or ("accepted", {}),
    )
    assert calls == []
    assert accepted_review_bundles(rerun) == []


def test_rerun_uses_fresh_checks_and_only_latest_accepted_is_exported() -> None:
    original = accepted_record()
    state = create_review_state([original], segment_fingerprints={"01_alltypes_10": {}})
    candidate_id = original["id"]
    edited = apply_review_rows(
        state,
        [review_row(candidate_id, edited_question="Who established the archive?")],
    )
    seen_candidates = []

    def processor(candidate):
        seen_candidates.append(deepcopy(candidate))
        assert candidate.search_verification_features == {}
        assert candidate.panel_grading_features == {}
        record = candidate.to_output_record("")
        record["validation"] = {"fresh": True}
        record["source_metadata"]["rule_based_qa_gate"] = {"fresh": True}
        record["search_verification_features"] = {
            "fresh": True,
            "category_hit_rates": {"overall": {"answer_hit_rate": 0.0}},
        }
        record["panel_grading_features"] = {
            "fresh": True,
            "models": deepcopy(original["panel_grading_features"]["models"]),
        }
        return "accepted", record

    rerun = rerun_review_candidates(edited, processor=processor)
    artifact = Route3CandidateArtifact.from_dict(rerun["candidates"][0]["artifact"])

    assert len(seen_candidates) == 1
    assert artifact.candidate_id == candidate_id
    assert len(artifact.revisions) == 2
    assert artifact.revisions[0].ddg["passed"] is True
    assert artifact.current_revision.ddg["fresh"] is True
    assert artifact.current_revision.second_stage["fresh"] is True
    assert artifact.current_revision.status == "accepted"
    assert len(accepted_review_bundles(rerun)) == 1
    assert "Who established the archive?" in render_review_markdown(rerun, run_id="review-run")
