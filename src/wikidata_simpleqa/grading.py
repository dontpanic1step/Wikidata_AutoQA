"""SimpleQA-style grading helpers for model predictions."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import json
from time import perf_counter
from typing import Any

from .cheap_model_qa import make_cheap_model_qa_client, parse_json_object
from .config import LLMConfig
from .number_reference import reference_answer_for_grading

VALID_GRADES = {"CORRECT", "INCORRECT", "NOT_ATTEMPTED"}


@dataclass(slots=True)
class ModelPanelMember:
    """One model used in the second-stage grading panel."""

    name: str
    client: Any


def make_grader_client(config: LLMConfig | None, timeout_seconds: float):
    """Construct the configured grader client."""
    return make_cheap_model_qa_client(config, timeout_seconds)


def grade_prediction(
    *,
    question: str,
    gold_answer: str,
    predicted_answer: str,
    gold_aliases: list[str] | None = None,
    answer_type: str = "",
    source_metadata: dict[str, Any] | None = None,
    grader_client=None,
) -> dict[str, Any]:
    """Grade one model answer as CORRECT, INCORRECT, or NOT_ATTEMPTED."""
    grading_start = perf_counter()
    if grader_client is None:
        raise ValueError("grader_client is required for SimpleQA-style grading.")
    reference_answer = reference_answer_for_grading(gold_answer, source_metadata or {})
    prompt = _build_grader_prompt(
        question=question,
        reference_answer=reference_answer,
        predicted_answer=predicted_answer,
        gold_aliases=gold_aliases or [],
        answer_type=answer_type,
        source_metadata=source_metadata or {},
    )
    grader_audit = _complete_text_with_audit(grader_client, prompt)
    parsed = parse_json_object(_audit_text(grader_audit))
    grade = _normalize_grade(str(parsed.get("grade", "")).strip())
    return {
        "grade": grade,
        "reason": str(parsed.get("reason", "")).strip(),
        "method": "llm_grader",
        "grader_audit": grader_audit,
        "grading_duration_seconds": _elapsed(grading_start),
    }


def grade_predictions_batch(
    *,
    question: str,
    gold_answer: str,
    predictions: list[dict[str, Any]],
    gold_aliases: list[str] | None = None,
    answer_type: str = "",
    source_metadata: dict[str, Any] | None = None,
    grader_client=None,
) -> list[dict[str, Any]]:
    """Grade multiple model answers, using one LLM call when a grader is configured."""
    if not predictions:
        return []
    if grader_client is None:
        raise ValueError("grader_client is required for SimpleQA-style batch grading.")

    grading_start = perf_counter()
    reference_answer = reference_answer_for_grading(gold_answer, source_metadata or {})
    prompt = _build_batch_grader_prompt(
        question=question,
        reference_answer=reference_answer,
        predictions=predictions,
        gold_aliases=gold_aliases or [],
        answer_type=answer_type,
        source_metadata=source_metadata or {},
    )
    grader_audit = _complete_text_with_audit(grader_client, prompt)
    parsed = parse_json_object(_audit_text(grader_audit))
    raw_grades = parsed.get("grades", [])
    if not isinstance(raw_grades, list):
        raise ValueError("Batch grader response must contain a grades list.")
    rows_by_index: dict[int, dict[str, Any]] = {}
    for row in raw_grades:
        if not isinstance(row, dict):
            continue
        try:
            index = int(row.get("index"))
        except (TypeError, ValueError):
            continue
        rows_by_index[index] = row
    duration = _elapsed(grading_start)
    graded_rows: list[dict[str, Any]] = []
    for index, _prediction in enumerate(predictions):
        raw_row = rows_by_index.get(index)
        if raw_row is None:
            raise ValueError(f"Batch grader response missing grade for prediction index {index}.")
        graded_rows.append(
            {
                "grade": _normalize_grade(str(raw_row.get("grade", "")).strip()),
                "reason": str(raw_row.get("reason", "")).strip(),
                "method": "llm_grader_batch",
                "grader_audit": grader_audit,
                "grading_duration_seconds": duration,
            }
        )
    return graded_rows


def evaluate_model_panel(
    *,
    question: str,
    gold_answer: str,
    gold_aliases: list[str],
    answer_type: str,
    source_metadata: dict[str, Any],
    model_panel: list[ModelPanelMember],
    grader_client=None,
    accuracy_threshold: float | None = None,
    early_stop_on_threshold: bool = False,
    parallel_answers: bool = True,
    batch_grader: bool = True,
) -> dict[str, Any]:
    """Run answer models and grade their responses."""
    model_rows: list[dict[str, Any]] = []
    total_configured = len(model_panel)
    early_stopped = False
    early_stop_reason = ""

    remaining_panel = model_panel
    if (
        early_stop_on_threshold
        and accuracy_threshold is not None
        and total_configured > 0
        and model_panel
    ):
        first_row = _answer_panel_member(question, model_panel[0])
        first_grade = _grade_panel_predictions(
            question=question,
            gold_answer=gold_answer,
            rows=[first_row],
            gold_aliases=gold_aliases,
            answer_type=answer_type,
            source_metadata=source_metadata,
            grader_client=grader_client,
            batch_grader=batch_grader,
        )[0]
        first_row.update(first_grade)
        model_rows.append(first_row)
        counts = _panel_counts(model_rows)
        if counts["correct_count"] / total_configured > accuracy_threshold:
            early_stopped = True
            early_stop_reason = "first_model_correct_exceeds_accuracy_threshold"
            remaining_panel = []
        else:
            remaining_panel = model_panel[1:]

    if remaining_panel:
        unanswered_rows = _answer_panel_members(
            question,
            remaining_panel,
            parallel=parallel_answers,
        )
        grade_rows = _grade_panel_predictions(
            question=question,
            gold_answer=gold_answer,
            rows=unanswered_rows,
            gold_aliases=gold_aliases,
            answer_type=answer_type,
            source_metadata=source_metadata,
            grader_client=grader_client,
            batch_grader=batch_grader,
        )
        for answer_row, grade_row in zip(unanswered_rows, grade_rows):
            answer_row.update(grade_row)
            model_rows.append(answer_row)

    counts = _panel_counts(model_rows)
    denominator = total_configured if early_stopped else len(model_rows)
    return {
        "enabled": True,
        "question": question,
        "gold_answer": gold_answer,
        "gold_aliases": gold_aliases,
        "reference_answer_for_grading": reference_answer_for_grading(gold_answer, source_metadata),
        "models": model_rows,
        "model_count": denominator,
        "configured_model_count": total_configured,
        "executed_model_count": len(model_rows),
        "correct_count": counts["correct_count"],
        "attempted_count": counts["attempted_count"],
        "accuracy": (counts["correct_count"] / denominator) if denominator else 0.0,
        "attempt_rate": (counts["attempted_count"] / denominator) if denominator else 0.0,
        "early_stopped": early_stopped,
        "early_stop_reason": early_stop_reason,
    }


def summarize_panel_runs(panel_runs: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize second-stage grading panel results."""
    per_model: dict[str, dict[str, Any]] = {}
    for run in panel_runs:
        for row in run.get("models", []):
            model_name = str(row.get("model", "")).strip()
            if not model_name:
                continue
            stats = per_model.setdefault(
                model_name,
                {"runs": 0, "correct": 0, "incorrect": 0, "not_attempted": 0, "accuracy": 0.0},
            )
            stats["runs"] += 1
            grade = row.get("grade")
            if grade == "CORRECT":
                stats["correct"] += 1
            elif grade == "INCORRECT":
                stats["incorrect"] += 1
            elif grade == "NOT_ATTEMPTED":
                stats["not_attempted"] += 1
    for stats in per_model.values():
        stats["accuracy"] = (stats["correct"] / stats["runs"]) if stats["runs"] else 0.0
    return {
        "run_count": len(panel_runs),
        "per_model": per_model,
    }


def _elapsed(start: float) -> float:
    """Return rounded elapsed seconds from a perf_counter start."""
    return round(perf_counter() - start, 4)


def _answer_panel_member(question: str, member: ModelPanelMember) -> dict[str, Any]:
    """Run one second-stage answer model."""
    answer_start = perf_counter()
    answer_audit = _complete_text_with_audit(member.client, question)
    predicted_answer = _audit_text(answer_audit).strip()
    return {
        "model": member.name,
        "predicted_answer": predicted_answer,
        "answer_audit": answer_audit,
        "answer_duration_seconds": _elapsed(answer_start),
    }


def _answer_panel_members(
    question: str,
    model_panel: list[ModelPanelMember],
    *,
    parallel: bool,
) -> list[dict[str, Any]]:
    """Run panel answer models, preserving configured order."""
    if not model_panel:
        return []
    if not parallel or len(model_panel) == 1:
        return [_answer_panel_member(question, member) for member in model_panel]
    rows: list[dict[str, Any] | None] = [None] * len(model_panel)
    with ThreadPoolExecutor(max_workers=len(model_panel)) as executor:
        future_to_index = {
            executor.submit(_answer_panel_member, question, member): index
            for index, member in enumerate(model_panel)
        }
        for future in as_completed(future_to_index):
            rows[future_to_index[future]] = future.result()
    return [row for row in rows if row is not None]


def _grade_panel_predictions(
    *,
    question: str,
    gold_answer: str,
    rows: list[dict[str, Any]],
    gold_aliases: list[str],
    answer_type: str,
    source_metadata: dict[str, Any],
    grader_client,
    batch_grader: bool,
) -> list[dict[str, Any]]:
    """Grade panel answer rows using batched or per-row grading."""
    if not rows:
        return []
    if batch_grader:
        return grade_predictions_batch(
            question=question,
            gold_answer=gold_answer,
            predictions=rows,
            gold_aliases=gold_aliases,
            answer_type=answer_type,
            source_metadata=source_metadata,
            grader_client=grader_client,
        )
    return [
        grade_prediction(
            question=question,
            gold_answer=gold_answer,
            predicted_answer=str(row.get("predicted_answer", "")),
            gold_aliases=gold_aliases,
            answer_type=answer_type,
            source_metadata=source_metadata,
            grader_client=grader_client,
        )
        for row in rows
    ]


def _panel_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    """Count correct and attempted panel rows."""
    correct_count = 0
    attempted_count = 0
    for row in rows:
        grade = row.get("grade")
        if grade == "CORRECT":
            correct_count += 1
            attempted_count += 1
        elif grade == "INCORRECT":
            attempted_count += 1
    return {
        "correct_count": correct_count,
        "attempted_count": attempted_count,
    }


def _complete_text_with_audit(client: Any, prompt: str) -> dict[str, Any]:
    """Return text-completion audit metadata, accepting legacy text-only clients."""
    if hasattr(client, "complete_text_with_audit"):
        audit = client.complete_text_with_audit(prompt)
        if isinstance(audit, dict):
            return audit
    response = client.complete_text(prompt)
    return {
        "text": str(response).strip(),
        "response_body": response,
        "response": response,
    }


def _audit_text(audit: dict[str, Any]) -> str:
    """Return assistant text from one text-completion audit payload."""
    if "text" in audit:
        return str(audit.get("text", ""))
    if "raw_text" in audit:
        return str(audit.get("raw_text", ""))
    return str(audit.get("response", ""))


def _normalize_grade(raw_grade: str) -> str:
    """Normalize grader labels to the supported SimpleQA-style labels."""
    upper = raw_grade.upper().replace(" ", "_")
    if upper in VALID_GRADES:
        return upper
    raise ValueError(f"Unsupported grader label: {raw_grade}")


def _build_grader_prompt(
    *,
    question: str,
    reference_answer: str,
    predicted_answer: str,
    gold_aliases: list[str],
    answer_type: str,
    source_metadata: dict[str, Any],
) -> str:
    """Build a compact SimpleQA Verified-style grading prompt."""
    return (
        "Grade the predicted answer to the factual question using SimpleQA Verified-style rules.\n"
        "Return JSON only with grade and reason; do not include extra text.\n"
        "Allowed grades: CORRECT, INCORRECT, NOT_ATTEMPTED.\n"
        "Use CORRECT only when the prediction gives the same answer as the reference answer or a valid alias, "
        "without adding a contradiction.\n"
        "If the reference answer is a list, use CORRECT only when the prediction includes every required list "
        "item or a valid alias for every item; partial lists are INCORRECT.\n"
        "Use NOT_ATTEMPTED only for empty answers, explicit abstentions, or responses that do not attempt the "
        "question.\n"
        "Use INCORRECT for wrong, vague, partial, contradictory, or overbroad answers.\n"
        "If the reference answer includes an acceptable numeric range, any numeric prediction inside that range "
        "is CORRECT and any numeric prediction outside that range is INCORRECT.\n\n"
        f"Question: {question}\n"
        f"Reference answer: {reference_answer}\n"
        f"Gold aliases: {gold_aliases}\n"
        f"Predicted answer: {predicted_answer}\n"
        f"Answer type: {answer_type}\n"
        f"Metadata: {source_metadata}\n\n"
        '{"grade": "CORRECT|INCORRECT|NOT_ATTEMPTED", "reason": "short explanation"}'
    )


def _build_batch_grader_prompt(
    *,
    question: str,
    reference_answer: str,
    predictions: list[dict[str, Any]],
    gold_aliases: list[str],
    answer_type: str,
    source_metadata: dict[str, Any],
) -> str:
    """Build a compact grading prompt for several model predictions."""
    prediction_rows = [
        {
            "index": index,
            "model": str(row.get("model", "")),
            "predicted_answer": str(row.get("predicted_answer", "")),
        }
        for index, row in enumerate(predictions)
    ]
    return (
        "Grade each predicted answer to the factual question using SimpleQA Verified-style rules.\n"
        "Return JSON only with a grades array; do not include extra text.\n"
        "Allowed grades: CORRECT, INCORRECT, NOT_ATTEMPTED.\n"
        "Use CORRECT only when the prediction gives the same answer as the reference answer or a valid alias, "
        "without adding a contradiction.\n"
        "If the reference answer is a list, use CORRECT only when the prediction includes every required list "
        "item or a valid alias for every item; partial lists are INCORRECT.\n"
        "Use NOT_ATTEMPTED only for empty answers, explicit abstentions, or responses that do not attempt the "
        "question.\n"
        "Use INCORRECT for wrong, vague, partial, contradictory, or overbroad answers.\n"
        "If the reference answer includes an acceptable numeric range, any numeric prediction inside that range "
        "is CORRECT and any numeric prediction outside that range is INCORRECT.\n\n"
        f"Question: {question}\n"
        f"Reference answer: {reference_answer}\n"
        f"Gold aliases: {gold_aliases}\n"
        f"Answer type: {answer_type}\n"
        f"Metadata: {source_metadata}\n"
        f"Predictions: {json.dumps(prediction_rows, ensure_ascii=False)}\n\n"
        '{"grades": [{"index": 0, "grade": "CORRECT|INCORRECT|NOT_ATTEMPTED", "reason": "short explanation"}]}'
    )
