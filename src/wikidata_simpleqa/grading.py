"""SimpleQA-style grading helpers for model predictions."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any

from .cheap_model_qa import make_cheap_model_qa_client, parse_json_object
from .config import LLMConfig
from .entity_normalization import normalize_name
from .number_reference import prediction_within_number_margin, reference_answer_for_grading

VALID_GRADES = {"CORRECT", "INCORRECT", "NOT_ATTEMPTED"}
NOT_ATTEMPTED_MARKERS = {
    "",
    "i don't know",
    "i don t know",
    "i do not know",
    "unknown",
    "not sure",
    "not attempted",
    "n/a",
    "no answer",
}


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
    if grader_client is not None:
        reference_answer = reference_answer_for_grading(gold_answer, source_metadata or {})
        prompt = _build_grader_prompt(
            question=question,
            reference_answer=reference_answer,
            predicted_answer=predicted_answer,
            gold_aliases=gold_aliases or [],
            answer_type=answer_type,
            source_metadata=source_metadata or {},
        )
        parsed = parse_json_object(grader_client.complete_text(prompt))
        grade = _normalize_grade(str(parsed.get("grade", "")).strip())
        return {
            "grade": grade,
            "reason": str(parsed.get("reason", "")).strip(),
            "method": "llm_grader",
            "grading_duration_seconds": _elapsed(grading_start),
        }

    normalized_prediction = normalize_name(predicted_answer)
    if normalized_prediction in NOT_ATTEMPTED_MARKERS:
        return {
            "grade": "NOT_ATTEMPTED",
            "reason": "empty_or_abstained_prediction",
            "method": "deterministic_alias_match",
            "grading_duration_seconds": _elapsed(grading_start),
        }
    if prediction_within_number_margin(predicted_answer, source_metadata or {}):
        return {
            "grade": "CORRECT",
            "reason": "prediction_within_number_reference_margin",
            "method": "deterministic_number_margin",
            "grading_duration_seconds": _elapsed(grading_start),
        }
    accepted_answers = _accepted_answers(gold_answer, gold_aliases or [])
    if normalized_prediction in accepted_answers:
        return {
            "grade": "CORRECT",
            "reason": "prediction_matches_gold_or_alias",
            "method": "deterministic_alias_match",
            "grading_duration_seconds": _elapsed(grading_start),
        }
    return {
        "grade": "INCORRECT",
        "reason": "prediction_does_not_match_gold_or_alias",
        "method": "deterministic_alias_match",
        "grading_duration_seconds": _elapsed(grading_start),
    }


def evaluate_model_panel(
    *,
    question: str,
    gold_answer: str,
    gold_aliases: list[str],
    answer_type: str,
    source_metadata: dict[str, Any],
    model_panel: list[ModelPanelMember],
    grader_client=None,
) -> dict[str, Any]:
    """Run answer models and grade their responses."""
    model_rows: list[dict[str, Any]] = []
    correct_count = 0
    attempted_count = 0
    for member in model_panel:
        answer_start = perf_counter()
        predicted_answer = str(member.client.complete_text(question)).strip()
        answer_duration_seconds = _elapsed(answer_start)
        grade_row = grade_prediction(
            question=question,
            gold_answer=gold_answer,
            predicted_answer=predicted_answer,
            gold_aliases=gold_aliases,
            answer_type=answer_type,
            source_metadata=source_metadata,
            grader_client=grader_client,
        )
        grade = grade_row["grade"]
        if grade == "CORRECT":
            correct_count += 1
            attempted_count += 1
        elif grade == "INCORRECT":
            attempted_count += 1
        model_rows.append(
            {
                "model": member.name,
                "predicted_answer": predicted_answer,
                "answer_duration_seconds": answer_duration_seconds,
                **grade_row,
            }
        )
    total = len(model_rows)
    return {
        "enabled": True,
        "question": question,
        "gold_answer": gold_answer,
        "gold_aliases": gold_aliases,
        "reference_answer_for_grading": reference_answer_for_grading(gold_answer, source_metadata),
        "models": model_rows,
        "model_count": total,
        "correct_count": correct_count,
        "attempted_count": attempted_count,
        "accuracy": (correct_count / total) if total else 0.0,
        "attempt_rate": (attempted_count / total) if total else 0.0,
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


def _accepted_answers(gold_answer: str, aliases: list[str]) -> set[str]:
    """Return normalized accepted answer strings."""
    return {
        normalized
        for normalized in [normalize_name(gold_answer), *(normalize_name(alias) for alias in aliases)]
        if normalized
    }


def _elapsed(start: float) -> float:
    """Return rounded elapsed seconds from a perf_counter start."""
    return round(perf_counter() - start, 4)


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
