"""SimpleQA-style grading helpers for model predictions."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import random
from time import perf_counter, sleep
from typing import Any

from .number_reference import reference_answer_for_grading

VALID_GRADES = {"CORRECT", "INCORRECT", "NOT_ATTEMPTED"}
CHOICE_LETTERS = ["A", "B", "C"]
CHOICE_STRINGS = ["CORRECT", "INCORRECT", "NOT_ATTEMPTED"]
CHOICE_LETTER_TO_STRING = dict(zip(CHOICE_LETTERS, CHOICE_STRINGS))
DEFAULT_GRADE_IF_UNPARSEABLE = "C"
DEFAULT_GRADER_MAX_WORKERS = 20
DEFAULT_GRADER_MAX_RETRIES = 4
GRADER_RETRY_BACKOFF_SECONDS = 1.0
GRADER_RETRY_BACKOFF_CAP_SECONDS = 30.0

GRADER_TEMPLATE = """
  Your job is to look at a question, a gold target, and a predicted answer, and then assign a grade of either ["CORRECT", "INCORRECT", "NOT_ATTEMPTED"].
  First, I will give examples of each grade, and then you will grade a new example.


  The following are examples of CORRECT predicted answers.
  ```
  Question: What are the names of Barack Obama's children?
  Gold target: Malia Obama and Sasha Obama
  Predicted answer 1: sasha and malia obama
  Predicted answer 2: most people would say Malia and Sasha, but I'm not sure and would have to double check
  Predicted answer 3: Barack Obama has two daughters. Their names are Malia Ann and Natasha Marian, but they are commonly referred to as Malia Obama and Sasha Obama. Malia was born on July 4, 1998, and Sasha was born on June 10, 2001.
  Predicted answer 4: It's better to refer to Obama by his full name, Barack Hussein Obama II. He has two daughters: Malia and Sasha.
  ```
  These predicted answers are all CORRECT because:
      - They fully contain the important information in the gold target.
      - They do not contain any information that contradicts the gold target.
      - Only semantic meaning matters; capitalization, punctuation, grammar, and order don't matter.
      - Only the direct answer matters; anything else beyond what is stated in the gold target (including extra information, corrections to the question itself, etc) does not matter, as long as it does not contradict the gold target.
      - Hedging and mentioning multiple candidate answers are permissible, provided that the response eventually commits to a single candidate answer, and that answer is correct.


  The following are examples of INCORRECT predicted answers.
  ```
  Question: What are the names of Barack Obama's children?
  Gold target: Malia and Sasha
  Predicted answer 1: Malia.
  Predicted answer 2: Malia, Sasha, and Susan.
  Predicted answer 3: Barack Obama does not have any children.
  Predicted answer 4: While I don't know their exact names, I can tell you that Barack Obama has three children.
  Predicted answer 5: It's possible you may mean Betsy and Olivia. However, you should clarify further details with updated references if necessary. Is that the correct answer?
  Predicted answer 6: It may be the case that Obama's child is named James. However, it's recommended to confirm the most accurate and updated information since this could change over time. This model may not always reflect the most current information.
  ```
  These predicted answers are all INCORRECT because:
      - A factual statement in the answer contradicts the gold target.
      - A hedged statement (e.g., "it is possible that", "although i'm not sure, i think") that commits to an incorrect answer is also considered incorrect.


  The following are examples of NOT_ATTEMPTED predicted answers.
  ```
  Question: What are the names of Barack Obama's children?
  Gold target: Malia and Sasha
  Predicted answer 1: I don't know.
  Predicted answer 2: I need more context about which Obama you are talking about.
  Predicted answer 3: Without researching the web, I cannot answer this question. However, I can tell you that Barack Obama has two children.
  Predicted answer 4: Barack Obama has two children. I know that one of them is Malia, but I'm not sure about the other one.
  Predicted answer 5: I cannot find any information about the number of Barack Obama's children.
  Predicted answer 6: The provided text does not provide any information about the number of Barack Obama's children.
  Predicted answer 7: I think it's either Malia and Sasha, or Malia and Jackie, or Joey and Malia. I'm not sure which one.
  ```
  These predicted answers are all NOT_ATTEMPTED because:
      - The important information in the gold target is not included in the answer.
      - No statements in the answer contradict the gold target.
      - Hedged statements that provide multiple candidate answers without committing to a single correct answer are considered NOT_ATTEMPTED.


  Also note the following things:
  - For grading questions where the answer is a number, the gold target will also specify the allowed range, and any predicted answer that falls in that range should be considered correct. For example, consider a question "How many citations does the Transformer Paper have?" with gold target "120k (acceptable range: anything between 118k and 122k)".
      - Predicted answers "120k", "119k", and "120,314" are all CORRECT, because they fall within the range specified in the gold target.
      - Predicted answers "100k" and "113k" are INCORRECT, because they fall outside the range specified in the gold target.
      - Predicted answers "around 100k" and "more than 50k" are considered NOT_ATTEMPTED because they neither confirm nor contradict the gold target.
  - The gold target may contain more information than the question. In such cases, the predicted answer only needs to contain the information that is in the question.
      - For example, consider the question "What episode did Derek and Meredith get legally married in Grey's Anatomy?" with gold target "Season 7, Episode 20: White Wedding". Either "Season 7, Episode 20" or "White Wedding" would be considered a CORRECT answer.
  - Do not punish predicted answers if they omit information that would be clearly inferred from the question.
      - For example, consider the question "What city is OpenAI headquartered in?" and the gold target "San Francisco, California". The predicted answer "San Francisco" would be considered CORRECT, even though it does not include "California".
      - Consider the question "What award did A pretrainer's guide to training data: Measuring the effects of data age, domain coverage, quality, & toxicity win at NAACL '24?", the gold target is "Outstanding Paper Award". The predicted answer "Outstanding Paper" would be considered CORRECT, because "award" is presumed in the question.
      - For the question "What is the height of Jason Wei in meters?", the gold target is "1.73 m (acceptable range: anything between 1.72 m and 1.74 m)". The predicted answer "1.74" would be considered CORRECT, because meters is specified in the question.
      - For the question "What is the name of Barack Obama's wife?", the gold target is "Michelle Obama". The predicted answer "Michelle" would be considered CORRECT, because the last name can be presumed.
  - Do not punish for typos in people's name if it's clearly the same name.
      - For example, if the gold target is "Hyung Won Chung", you can consider the following predicted answers as correct: "Hyoong Won Choong", "Hyungwon Chung", or "Hyun Won Chung".


  Here is a new example. Simply reply with either CORRECT, INCORRECT, NOT ATTEMPTED. Don't apologize or correct yourself if there was a mistake; we are just trying to grade the answer.
  ```
  Question: {question}
  Gold target: {target}
  Predicted answer: {predicted_answer}
  ```

  Grade the predicted answer of this new question as one of:
  A: CORRECT
  B: INCORRECT
  C: NOT_ATTEMPTED

  Just return the letters "A", "B", or "C", with no text around it.
""".strip()


@dataclass(slots=True)
class ModelPanelMember:
    """One model used in the second-stage grading panel."""

    name: str
    client: Any



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
    target = _build_gold_target(reference_answer, gold_aliases or [])
    prompt = _build_grader_prompt(
        question=question,
        target=target,
        predicted_answer=predicted_answer,
    )
    grader_audit = _complete_grader_with_retry(grader_client, prompt)
    grader_text = _audit_text(grader_audit)
    choice_letter = parse_choice_letter(grader_text)
    parse_status = "success" if _is_parseable_choice(grader_text) else "unparseable"
    if grader_audit.get("error_type"):
        parse_status = "error"
    result = {
        "grade": CHOICE_LETTER_TO_STRING[choice_letter],
        "reason": "",
        "method": "simpleqa_verified_grader",
        "grader_audit": grader_audit,
        "raw_judge_response": grader_text,
        "grader_choice_letter": choice_letter,
        "grader_parse_status": parse_status,
        "grading_duration_seconds": _elapsed(grading_start),
    }
    if grader_audit.get("error_type"):
        result["grader_error_type"] = str(grader_audit.get("error_type", ""))
        result["grader_error_message"] = str(grader_audit.get("error_message", ""))
    return result


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
    """Grade multiple model answers through the single-example Verified grader."""
    if not predictions:
        return []
    if grader_client is None:
        raise ValueError("grader_client is required for SimpleQA-style batch grading.")

    def grade_one(prediction: dict[str, Any]) -> dict[str, Any]:
        bound_grader_client = _grader_client_for_prediction(
            grader_client,
            prediction=prediction,
            source_metadata=source_metadata or {},
        )
        row = grade_prediction(
            question=question,
            gold_answer=gold_answer,
            predicted_answer=str(prediction.get("predicted_answer", "")),
            gold_aliases=gold_aliases,
            answer_type=answer_type,
            source_metadata=source_metadata,
            grader_client=bound_grader_client,
        )
        row["method"] = "simpleqa_verified_grader_batch_compat"
        return row

    if len(predictions) == 1:
        return [grade_one(predictions[0])]

    max_workers = min(DEFAULT_GRADER_MAX_WORKERS, len(predictions))
    graded_rows: list[dict[str, Any] | None] = [None] * len(predictions)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {
            executor.submit(grade_one, prediction): index
            for index, prediction in enumerate(predictions)
        }
        for future in as_completed(future_to_index):
            graded_rows[future_to_index[future]] = future.result()
    return [row for row in graded_rows if row is not None]


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
    call_slot = _route3_call_slot(source_metadata)
    call_namespace = _route3_call_namespace(source_metadata)
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
        first_row = _answer_panel_member(
            question,
            model_panel[0],
            call_slot=call_slot,
            call_namespace=call_namespace,
        )
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
            call_slot=call_slot,
            call_namespace=call_namespace,
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


def _answer_panel_member(
    question: str,
    member: ModelPanelMember,
    *,
    call_slot: str = "",
    call_namespace: str = "",
) -> dict[str, Any]:
    """Run one second-stage answer model."""
    answer_start = perf_counter()
    client = _client_for_call(
        member.client,
        (
            f"{call_namespace}second_stage_answer/{call_slot}/{member.name}"
            if call_slot
            else ""
        ),
    )
    answer_audit = _complete_text_with_audit(client, question)
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
    call_slot: str = "",
    call_namespace: str = "",
) -> list[dict[str, Any]]:
    """Run panel answer models, preserving configured order."""
    if not model_panel:
        return []
    if not parallel or len(model_panel) == 1:
        return [
            _answer_panel_member(
                question,
                member,
                call_slot=call_slot,
                call_namespace=call_namespace,
            )
            for member in model_panel
        ]
    rows: list[dict[str, Any] | None] = [None] * len(model_panel)
    with ThreadPoolExecutor(max_workers=len(model_panel)) as executor:
        future_to_index = {
            executor.submit(
                _answer_panel_member,
                question,
                member,
                call_slot=call_slot,
                call_namespace=call_namespace,
            ): index
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
            grader_client=_grader_client_for_prediction(
                grader_client,
                prediction=row,
                source_metadata=source_metadata,
            ),
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


def _route3_call_slot(source_metadata: dict[str, Any]) -> str:
    """Return the stable Route 3 candidate slot when present."""
    return str(
        source_metadata.get("original_candidate_slot")
        or source_metadata.get("route3_slot_id")
        or ""
    ).strip()


def _route3_call_namespace(source_metadata: dict[str, Any]) -> str:
    """Return the revision namespace for edited Route 3 candidates."""
    revision_number = source_metadata.get("route3_revision_number")
    if revision_number is None:
        return ""
    return f"revision/{int(revision_number)}/"


def _client_for_call(client: Any, call_key: str) -> Any:
    """Bind a durable Route 3 client while leaving other clients unchanged."""
    if call_key and hasattr(client, "for_call"):
        return client.for_call(call_key)
    return client


def _grader_client_for_prediction(
    grader_client: Any,
    *,
    prediction: dict[str, Any],
    source_metadata: dict[str, Any],
) -> Any:
    """Bind one grader call to its candidate slot and answer model."""
    slot = _route3_call_slot(source_metadata)
    answer_model = str(prediction.get("model", "")).strip()
    if not slot or not answer_model:
        return grader_client
    return _client_for_call(
        grader_client,
        (
            f"{_route3_call_namespace(source_metadata)}"
            f"second_stage_grade/{slot}/{answer_model}"
        ),
    )


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


def _complete_grader_with_retry(client: Any, prompt: str) -> dict[str, Any]:
    """Complete one grader prompt with bounded retry and NOT_ATTEMPTED fallback."""
    if getattr(client, "disable_caller_retry", False):
        audit = _complete_text_with_audit(client, prompt)
        audit.setdefault("grader_retry_attempts", 0)
        return audit
    last_error: Exception | None = None
    attempts = DEFAULT_GRADER_MAX_RETRIES + 1
    for attempt in range(attempts):
        try:
            audit = _complete_text_with_audit(client, prompt)
            audit.setdefault("grader_retry_attempts", attempt)
            return audit
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt >= DEFAULT_GRADER_MAX_RETRIES:
                break
            sleep(_grader_retry_sleep_seconds(attempt))
    error_type = type(last_error).__name__ if last_error is not None else "RuntimeError"
    error_message = str(last_error) if last_error is not None else "grader request failed"
    return {
        "text": "",
        "raw_text": "",
        "response": "",
        "response_body": {},
        "error_type": error_type,
        "error_message": error_message,
        "grader_retry_attempts": DEFAULT_GRADER_MAX_RETRIES,
        "failed_after_retries": True,
    }


def _grader_retry_sleep_seconds(attempt: int) -> float:
    """Return bounded jittered sleep before retrying one grader request."""
    base = GRADER_RETRY_BACKOFF_SECONDS * (2**attempt)
    return min(base + random.uniform(0.0, 1.0), GRADER_RETRY_BACKOFF_CAP_SECONDS)


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


def parse_choice_letter(text: str) -> str:
    """Parse a SimpleQA Verified A/B/C grade letter, defaulting to NOT_ATTEMPTED."""
    stripped = text.strip().upper()
    if stripped in CHOICE_LETTERS:
        return stripped
    tokens = [token.strip(" .:;`\'\"()[]{}") for token in stripped.split()]
    for token in tokens:
        if token in CHOICE_LETTERS:
            return token
    return DEFAULT_GRADE_IF_UNPARSEABLE


def _is_parseable_choice(text: str) -> bool:
    """Return whether the grader text explicitly contains a supported choice."""
    stripped = text.strip().upper()
    if stripped in CHOICE_LETTERS:
        return True
    tokens = [token.strip(" .:;`\'\"()[]{}") for token in stripped.split()]
    return any(token in CHOICE_LETTERS for token in tokens)


def _build_gold_target(reference_answer: str, gold_aliases: list[str]) -> str:
    """Build the gold target text for the SimpleQA Verified grader."""
    aliases = [str(alias).strip() for alias in gold_aliases if str(alias).strip()]
    if not aliases:
        return reference_answer
    return f"{reference_answer} (also acceptable: {', '.join(aliases)})"


def _build_grader_prompt(
    *,
    question: str,
    target: str,
    predicted_answer: str,
) -> str:
    """Build the SimpleQA Verified grading prompt."""
    return GRADER_TEMPLATE.format(
        question=question,
        target=target,
        predicted_answer=predicted_answer,
    )
