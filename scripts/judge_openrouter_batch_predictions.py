"""Judge batch predictions with the SimpleQA Verified grading prompt."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import random
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parents[1]

OPENROUTER_CHAT_COMPLETIONS_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_REFERER = "https://example.com/wikidata-simpleqa"
OPENROUTER_TITLE = "Wikidata SimpleQA Generator"
OPENROUTER_USER_AGENT = "wikidata-simpleqa-verified-grader/0.1"
DEFAULT_JUDGE_MODEL = "openai/gpt-4.1-mini"
DEFAULT_JUDGE_MAX_TOKENS = 2048
RETRY_STATUS_CODES = {408, 409, 425, 429, 500, 502, 503, 504}

CHOICE_LETTERS = ["A", "B", "C"]
CHOICE_STRINGS = ["CORRECT", "INCORRECT", "NOT_ATTEMPTED"]
CHOICE_LETTER_TO_STRING = dict(zip(CHOICE_LETTERS, CHOICE_STRINGS))
DEFAULT_GRADE_IF_UNPARSEABLE = "C"

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


def main() -> None:
    args = parse_args()
    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise SystemExit(f"Missing API key in environment variable {args.api_key_env}")

    proxy = optional_proxy(args.proxy)
    input_files = discover_input_files(Path(args.input_path), args.glob)
    if not input_files:
        raise SystemExit(f"No JSONL inputs found at {args.input_path}")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    client = OpenRouterJudgeClient(
        api_key=api_key,
        model=args.judge_model,
        timeout_seconds=args.timeout_seconds,
        max_retries=args.max_retries,
        backoff_base=args.backoff_base,
        backoff_cap_seconds=args.backoff_cap_seconds,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        proxy=proxy,
    )
    settings = JudgeSettings(
        output_dir=output_dir,
        client=client,
        concurrency=args.concurrency,
        limit=args.limit,
    )

    for input_file in input_files:
        records = load_jsonl(input_file)
        if settings.limit is not None:
            records = records[: settings.limit]
        if not records:
            print(f"[skip] {input_file}: no records")
            continue
        judge_file(input_file=input_file, records=records, settings=settings)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Judge batch model predictions with the SimpleQA Verified grading prompt."
    )
    parser.add_argument("input_path", help="Prediction JSONL file or directory.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "outputs" / "openrouter_batch_judged",
        help="Output directory. Default: outputs/openrouter_batch_judged",
    )
    parser.add_argument("--glob", default="*.jsonl", help="Input glob when input_path is a directory.")
    parser.add_argument("--judge-model", default=DEFAULT_JUDGE_MODEL)
    parser.add_argument("--api-key-env", default="OPENROUTER_API_KEY")
    parser.add_argument("--proxy", default="none")
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--timeout-seconds", type=float, default=60.0)
    parser.add_argument("--max-retries", type=int, default=4)
    parser.add_argument("--backoff-base", type=float, default=1.0)
    parser.add_argument("--backoff-cap-seconds", type=float, default=30.0)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_JUDGE_MAX_TOKENS)
    parser.add_argument("--limit", type=int, default=None, help="Optional per-file record limit.")
    return parser.parse_args()


class JudgeSettings:
    def __init__(
        self,
        *,
        output_dir: Path,
        client: "OpenRouterJudgeClient",
        concurrency: int,
        limit: int | None,
    ) -> None:
        self.output_dir = output_dir
        self.client = client
        self.concurrency = concurrency
        self.limit = limit


class OpenRouterJudgeClient:
    """Minimal OpenRouter chat client for the SimpleQA Verified grader prompt."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        timeout_seconds: float,
        max_retries: int,
        backoff_base: float,
        backoff_cap_seconds: float,
        temperature: float,
        max_tokens: int | None,
        proxy: str | None,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.backoff_cap_seconds = backoff_cap_seconds
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.proxy = proxy

    def grade(self, *, question: str, target: str, predicted_answer: str) -> dict[str, Any]:
        prompt = GRADER_TEMPLATE.format(
            question=question,
            target=target,
            predicted_answer=predicted_answer,
        )
        request_settings = self.request_settings()
        response, raw_response, error = self.complete_response(prompt)
        if response is None:
            print(f"[error] judge {self.model}: {error}")
            letter = DEFAULT_GRADE_IF_UNPARSEABLE
            status = "error"
        else:
            try:
                text = str(response["choices"][0]["message"]["content"]).strip()
                letter = parse_choice_letter(text)
                status = "success" if letter in CHOICE_LETTERS else "unparseable"
            except (KeyError, TypeError, IndexError) as exc:
                print(f"[error] judge {self.model}: {type(exc).__name__}: {exc}")
                letter = DEFAULT_GRADE_IF_UNPARSEABLE
                status = "error"
                error = f"{type(exc).__name__}: {exc}"
        if letter not in CHOICE_LETTERS:
            letter = DEFAULT_GRADE_IF_UNPARSEABLE
        result: dict[str, Any] = {
            "model": self.model,
            "letter": letter,
            "grade": CHOICE_LETTER_TO_STRING[letter],
            "status": status,
            "request_settings": request_settings,
            "raw_response": raw_response,
        }
        if error:
            result["error"] = error
        return result

    def request_settings(self) -> dict[str, Any]:
        """Return judge request settings for audit/debugging."""
        return {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "proxy": self.proxy,
        }

    def complete_response(
        self,
        prompt: str,
    ) -> tuple[dict[str, Any] | None, str | None, str | None]:
        """Return parsed JSON, the complete response body, and any request error."""
        payload = {
            "model": self.model,
            "temperature": self.temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if self.max_tokens is not None:
            payload["max_tokens"] = self.max_tokens
        return self._request_with_retry(payload)

    def _request_with_retry(
        self,
        payload: dict[str, Any],
    ) -> tuple[dict[str, Any] | None, str | None, str | None]:
        last_error: str | None = None
        raw_response: str | None = None
        for attempt in range(self.max_retries + 1):
            headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": OPENROUTER_USER_AGENT,
                    "HTTP-Referer": OPENROUTER_REFERER,
                    "X-OpenRouter-Title": OPENROUTER_TITLE,
            }
            try:
                response = requests.post(
                    OPENROUTER_CHAT_COMPLETIONS_URL,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout_seconds,
                    proxies=requests_proxies(self.proxy),
                )
                raw_response = response.text
                if response.status_code in RETRY_STATUS_CODES:
                    last_error = f"HTTP {response.status_code}: {raw_response}"
                    if attempt >= self.max_retries:
                        break
                    sleep_before_retry(
                        attempt,
                        base=self.backoff_base,
                        cap=self.backoff_cap_seconds,
                        retry_after=response.headers.get("Retry-After"),
                    )
                    continue
                if response.status_code != 200:
                    raise RuntimeError(f"HTTP {response.status_code}: {raw_response}")
                return response.json(), raw_response, None
            except (
                TimeoutError,
                ConnectionError,
                OSError,
                json.JSONDecodeError,
                requests.RequestException,
                RuntimeError,
            ) as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                if attempt >= self.max_retries:
                    break
                sleep_before_retry(
                    attempt,
                    base=self.backoff_base,
                    cap=self.backoff_cap_seconds,
                    retry_after=None,
                )
        error = f"Judge request failed for {self.model}. Last error: {last_error}"
        return None, raw_response, error


def parse_choice_letter(text: str) -> str:
    stripped = text.strip().upper()
    if stripped in CHOICE_LETTERS:
        return stripped
    tokens = [token.strip(" .:;`'\"()[]{}") for token in stripped.split()]
    for token in tokens:
        if token in CHOICE_LETTERS:
            return token
    return DEFAULT_GRADE_IF_UNPARSEABLE


def optional_proxy(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    if not stripped or stripped.lower() in {"none", "off", "false", "direct"}:
        return None
    return stripped


def requests_proxies(proxy: str | None) -> dict[str, str] | None:
    """Build requests proxy config, using remote DNS for socks5 proxies."""
    if not proxy:
        return None
    normalized = proxy
    if proxy.lower().startswith("socks5://"):
        normalized = "socks5h://" + proxy[len("socks5://") :]
    return {"http": normalized, "https": normalized}


def discover_input_files(input_path: Path, pattern: str) -> list[Path]:
    if input_path.is_file():
        return [input_path]
    if input_path.is_dir():
        return sorted(path for path in input_path.glob(pattern) if path.is_file())
    raise SystemExit(f"Input path does not exist: {input_path}")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                obj = json.loads(stripped)
            except json.JSONDecodeError as exc:
                print(f"[warn] {path}:{line_number}: skipped malformed JSON: {exc}")
                continue
            if not isinstance(obj, dict):
                print(f"[warn] {path}:{line_number}: skipped non-object JSONL record")
                continue
            records.append(obj)
    return records


def judge_file(*, input_file: Path, records: list[dict[str, Any]], settings: JudgeSettings) -> None:
    output_path = settings.output_dir / f"{input_file.stem}.judged.jsonl"
    existing = load_existing_output(output_path)
    write_lock = threading.Lock()

    todo: list[tuple[int, dict[str, Any]]] = []
    complete = 0
    for index, record in enumerate(records):
        key = record_key(record, index)
        previous = existing.get(key)
        candidate = previous if previous is not None else record
        if record_is_judged(candidate, settings.client.model):
            complete += 1
            if previous is None:
                existing[key] = candidate
            continue
        todo.append((index, record))

    atomic_write_jsonl(output_path, ordered_existing_records(existing, records))
    if not todo:
        print(f"[done] {input_file.name}: {complete}/{len(records)} records already judged")
        return

    print(
        f"[run] {input_file.name}: {len(todo)} records need judge, "
        f"judge={settings.client.model}, concurrency={settings.concurrency}"
    )
    completed_now = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=settings.concurrency) as executor:
        futures = [
            executor.submit(
                judge_record,
                index,
                record,
                records,
                existing,
                output_path,
                settings,
                write_lock,
            )
            for index, record in todo
        ]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as exc:  # noqa: BLE001
                print(f"[error] worker crashed unexpectedly: {type(exc).__name__}: {exc}")
            completed_now += 1
            if completed_now % 10 == 0 or completed_now == len(todo):
                print(f"[progress] {input_file.name}: {completed_now}/{len(todo)}")
    print(f"[done] {input_file.name}: wrote {output_path}")


def judge_record(
    index: int,
    record: dict[str, Any],
    source_records: list[dict[str, Any]],
    existing: dict[str, dict[str, Any]],
    output_path: Path,
    settings: JudgeSettings,
    write_lock: threading.Lock,
) -> None:
    key = record_key(record, index)
    output_record = merge_existing_judges(record, existing.get(key))
    predictions = ensure_predictions(output_record)

    question = stringify(output_record.get("question"))
    target = gold_target_answer(output_record)
    for prediction in predictions:
        if not isinstance(prediction, dict):
            continue
        existing_judge = prediction.get("judge")
        if isinstance(existing_judge, dict) and existing_judge.get("model") == settings.client.model:
            continue
        prediction["judge"] = settings.client.grade(
            question=question,
            target=target,
            predicted_answer=prediction_answer(prediction),
        )

    with write_lock:
        existing[key] = output_record
        atomic_write_jsonl(output_path, ordered_existing_records(existing, source_records))


def merge_existing_judges(record: dict[str, Any], previous: dict[str, Any] | None) -> dict[str, Any]:
    merged = json.loads(json.dumps(record, ensure_ascii=False))
    ensure_predictions(merged)
    if previous is None:
        return merged
    ensure_predictions(previous)
    previous_predictions = previous.get("predictions")
    merged_predictions = merged.get("predictions")
    if not isinstance(previous_predictions, list) or not isinstance(merged_predictions, list):
        return merged
    for index, prediction in enumerate(merged_predictions):
        if not isinstance(prediction, dict) or index >= len(previous_predictions):
            continue
        previous_judge = previous_predictions[index].get("judge")
        if isinstance(previous_judge, dict):
            prediction["judge"] = previous_judge
    return merged


def record_is_judged(record: dict[str, Any], judge_model: str) -> bool:
    ensure_predictions(record)
    predictions = record.get("predictions")
    if not isinstance(predictions, list) or not predictions:
        return False
    for prediction in predictions:
        if not isinstance(prediction, dict):
            return False
        judge = prediction.get("judge")
        if not isinstance(judge, dict) or judge.get("model") != judge_model:
            return False
    return True


def prediction_answer(prediction: Any) -> str:
    if not isinstance(prediction, dict):
        return "" if prediction is None else str(prediction)
    value = prediction.get("answer")
    if value is None:
        value = prediction.get("predicted_answer")
    return "" if value is None else str(value)


def ensure_predictions(record: dict[str, Any]) -> list[dict[str, Any]]:
    """Ensure a record has prediction rows, adapting raw response-style inputs."""
    predictions = record.get("predictions")
    if isinstance(predictions, list):
        normalized = [prediction for prediction in predictions if isinstance(prediction, dict)]
        if len(normalized) != len(predictions):
            record["predictions"] = normalized
        return normalized

    prediction = prediction_from_raw_record(record)
    predictions = [prediction] if prediction is not None else []
    record["predictions"] = predictions
    return predictions


def prediction_from_raw_record(record: dict[str, Any]) -> dict[str, Any] | None:
    """Build one prediction row from top-level raw model-response fields."""
    answer = raw_prediction_answer(record)
    if answer is None:
        return None
    prediction: dict[str, Any] = {
        "model": stringify(record.get("model")),
        "answer": answer,
    }
    for key in (
        "repeat_index",
        "ok",
        "error",
        "temperature",
        "temperature_requested",
        "temperature_sent",
        "max_tokens",
        "reasoning",
        "reasoning_effort",
        "created_at",
        "original_id",
    ):
        if key in record:
            prediction[key] = record[key]
    return prediction


def raw_prediction_answer(record: dict[str, Any]) -> str | None:
    """Extract a predicted answer from common raw output formats."""
    for key in ("response_text", "predicted_answer", "model_answer"):
        value = record.get(key)
        if value is not None:
            return stringify(value)

    response = record.get("response")
    if isinstance(response, str):
        return stringify(response)
    if isinstance(response, dict):
        extracted = response_text_from_openrouter_response(response)
        if extracted is not None:
            return extracted

    if ("gold_answer" in record or "reference_answer" in record) and "answer" in record:
        return stringify(record.get("answer"))
    return None


def response_text_from_openrouter_response(response: dict[str, Any]) -> str | None:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        return None
    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        return None
    message = first_choice.get("message")
    if not isinstance(message, dict):
        return None
    content = message.get("content")
    if content is None:
        return ""
    return stringify(content)


def gold_target_answer(record: dict[str, Any]) -> str:
    """Return the gold answer, allowing raw formats where answer is a prediction."""
    for key in ("gold_answer", "reference_answer", "answer"):
        value = stringify(record.get(key))
        if value:
            return value
    return ""


def load_existing_output(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    best: dict[str, dict[str, Any]] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                obj = json.loads(stripped)
            except json.JSONDecodeError:
                continue
            if not isinstance(obj, dict):
                continue
            key = output_record_key(obj)
            if key is None:
                continue
            previous = best.get(key)
            if previous is None or judge_count(obj) >= judge_count(previous):
                best[key] = obj
    return best


def ordered_existing_records(
    existing: dict[str, dict[str, Any]],
    source_records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    ordered: list[dict[str, Any]] = []
    for index, source in enumerate(source_records):
        record = existing.get(record_key(source, index))
        if record:
            ordered.append(record)
    return ordered


def atomic_write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        tmp_name = handle.name
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    Path(tmp_name).replace(path)


def sleep_before_retry(
    attempt: int,
    *,
    base: float,
    cap: float,
    retry_after: str | None,
) -> None:
    retry_after_seconds = parse_retry_after(retry_after)
    if retry_after_seconds is not None:
        time.sleep(min(retry_after_seconds, cap))
        return
    time.sleep(min(base * (2**attempt) + random.uniform(0.0, 1.0), cap))


def parse_retry_after(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return max(float(value), 0.0)
    except ValueError:
        return None


def record_key(record: dict[str, Any], index: int) -> str:
    raw_id = stringify(record.get("id"))
    if raw_id:
        return raw_id
    question = stringify(record.get("question"))
    if question:
        return question
    return f"record_{index}"


def output_record_key(record: dict[str, Any]) -> str | None:
    raw_id = stringify(record.get("id"))
    if raw_id:
        return raw_id
    question = stringify(record.get("question"))
    return question or None


def judge_count(record: dict[str, Any]) -> int:
    predictions = record.get("predictions")
    if not isinstance(predictions, list):
        return 0
    return sum(
        1
        for prediction in predictions
        if isinstance(prediction, dict) and isinstance(prediction.get("judge"), dict)
    )


def stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        raise SystemExit(130)
