"""Run batched OpenRouter predictions over a directory of CSV files.

Inputs are final Route 3 or SimpleQA Verified CSV rows with:
    id/original_index, problem, answer

Outputs are per input file and per model JSONL records with:
    {"id": ..., "question": ..., "answer": ..., "predictions": [...]}
"""

from __future__ import annotations

import argparse
import csv
import concurrent.futures
from dataclasses import dataclass
import json
import os
import random
import re
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parents[1]

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
OPENROUTER_REFERER = "http://localhost"
OPENROUTER_TITLE = "batch-openrouter-predictions"
OPENROUTER_USER_AGENT = "wikidata-simpleqa-openrouter-batch/0.1"

MODELS = [
    "openai/gpt-5.6-sol",
    "google/gemini-3.1-pro-preview",
    "anthropic/claude-sonnet-5",
    "deepseek/deepseek-v4-pro",
    "qwen/qwen3.7-max",
    "z-ai/glm-5.2",
    "moonshotai/kimi-k3",
    "minimax/minimax-m3",
    "xiaomi/mimo-v2.5-pro",
]

MODEL_REASONING_SETTINGS: dict[str, dict[str, Any]] = {
    "openai/gpt-5.6-sol": {
        "reasoning_effort": "max",
    },
    "google/gemini-3.1-pro-preview": {
        "reasoning_effort": "high",
    },
    "anthropic/claude-sonnet-5": {
        "reasoning_effort": "max",
    },
    "deepseek/deepseek-v4-pro": {
        "reasoning_effort": "xhigh",
    },
    "qwen/qwen3.7-max": {
        "reasoning_effort": None,
    },
    "z-ai/glm-5.2": {
        "reasoning_effort": "xhigh",
    },
    "moonshotai/kimi-k3": {
        "reasoning_effort": "max",
    },
    "minimax/minimax-m3": {
        "reasoning_effort": None,
    },
    "xiaomi/mimo-v2.5-pro": {
        "reasoning_effort": None,
    },
}

RETRY_STATUS_CODES = {408, 409, 425, 429, 500, 502, 503, 504}


def main() -> None:
    args = parse_args()
    models = parse_models(args.models)
    if args.input_dir:
        validate_reasoning_configuration(
            models=models,
            reasoning_effort=args.reasoning_effort,
            use_provider_reasoning_defaults=args.use_provider_reasoning_defaults,
        )
    api_key = os.environ.get(args.api_key_env)
    if not api_key and not args.print_model_defaults:
        raise SystemExit(f"Missing API key in environment variable {args.api_key_env}")

    if args.print_model_defaults:
        rows = fetch_model_defaults(
            models=models,
            timeout_seconds=args.timeout_seconds,
            proxy=optional_proxy(args.proxy),
        )
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        if not args.input_dir:
            return

    input_dir = Path(args.input_dir)
    input_files = discover_input_files(input_dir, args.glob, recursive=args.recursive)
    if not input_files:
        raise SystemExit(f"No CSV files matched {args.glob!r} under {input_dir}")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    settings = RunSettings(
        api_key=api_key or "",
        models=models,
        output_dir=output_dir,
        rounds=args.rounds,
        concurrency=args.concurrency,
        timeout_seconds=args.timeout_seconds,
        max_retries=args.max_retries,
        backoff_base=args.backoff_base,
        backoff_cap_seconds=args.backoff_cap_seconds,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        reasoning_effort=args.reasoning_effort,
        use_provider_reasoning_defaults=args.use_provider_reasoning_defaults,
        proxy=optional_proxy(args.proxy),
        blob_mode=args.blob_mode,
        limit=args.limit,
    )

    run_global_queue(input_files=input_files, settings=settings)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Batch OpenRouter chat completions for SimpleQA-style CSV files."
    )
    parser.add_argument("input_dir", nargs="?", help="Directory containing CSV input files.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "outputs" / "openrouter_batch_predictions",
        help="Output directory. Default: outputs/openrouter_batch_predictions",
    )
    parser.add_argument("--glob", default="*.csv", help="Input glob under input_dir.")
    parser.add_argument("--recursive", action="store_true", help="Search input_dir recursively.")
    parser.add_argument(
        "--models",
        default=",".join(MODELS),
        help="Comma-separated OpenRouter model ids.",
    )
    parser.add_argument("--api-key-env", default="OPENROUTER_API_KEY")
    parser.add_argument("--proxy", default="none")
    parser.add_argument("--concurrency", type=int, default=20)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--timeout-seconds", type=float, default=240.0)
    parser.add_argument("--max-retries", type=int, default=6)
    parser.add_argument("--backoff-base", type=float, default=1.5)
    parser.add_argument("--backoff-cap-seconds", type=float, default=90.0)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=None,
        help="Optional max_tokens/max_completion_tokens override. Default: omit it and use OpenRouter/provider default.",
    )
    parser.add_argument(
        "--reasoning-effort",
        default="auto",
        choices=["auto", "minimal", "low", "medium", "high", "xhigh", "max"],
        help=(
            "Reasoning effort override. Default auto uses audited per-model settings from "
            "MODEL_REASONING_SETTINGS and rejects models absent from that table."
        ),
    )
    parser.add_argument(
        "--use-provider-reasoning-defaults",
        action="store_true",
        help=(
            "For models absent from MODEL_REASONING_SETTINGS, omit the reasoning field and use "
            "the provider default instead of rejecting the batch."
        ),
    )
    parser.add_argument(
        "--blob-mode",
        choices=["ignore", "append", "only"],
        default="ignore",
        help=(
            "How to handle an input field named blob. ignore sends only question; "
            "append sends blob plus question as raw user content; only sends blob."
        ),
    )
    parser.add_argument("--limit", type=int, default=None, help="Optional per-file record limit.")
    parser.add_argument(
        "--print-model-defaults",
        action="store_true",
        help="Fetch OpenRouter model metadata and print context/max token defaults.",
    )
    return parser.parse_args()


class RunSettings:
    def __init__(
        self,
        *,
        api_key: str,
        models: list[str],
        output_dir: Path,
        rounds: int,
        concurrency: int,
        timeout_seconds: float,
        max_retries: int,
        backoff_base: float,
        backoff_cap_seconds: float,
        max_tokens: int | None,
        temperature: float,
        reasoning_effort: str,
        use_provider_reasoning_defaults: bool,
        proxy: str | None,
        blob_mode: str,
        limit: int | None,
    ) -> None:
        self.api_key = api_key
        self.models = models
        self.output_dir = output_dir
        self.rounds = rounds
        self.concurrency = concurrency
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.backoff_cap_seconds = backoff_cap_seconds
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.reasoning_effort = reasoning_effort
        self.use_provider_reasoning_defaults = use_provider_reasoning_defaults
        self.proxy = proxy
        self.blob_mode = blob_mode
        self.limit = limit


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


def parse_models(value: str) -> list[str]:
    models = [part.strip() for part in value.split(",") if part.strip()]
    if not models:
        raise SystemExit("At least one model is required.")
    return models


def validate_reasoning_configuration(
    *,
    models: list[str],
    reasoning_effort: str,
    use_provider_reasoning_defaults: bool,
) -> None:
    if reasoning_effort != "auto" or use_provider_reasoning_defaults:
        return
    missing = list(
        dict.fromkeys(model for model in models if model not in MODEL_REASONING_SETTINGS)
    )
    if not missing:
        return
    count = len(missing)
    noun = "model" if count == 1 else "models"
    model_lines = "\n".join(f"- {model}" for model in missing)
    raise SystemExit(
        f"Cannot start evaluation: {count} {noun} have no audited reasoning defaults\n"
        "and no explicit reasoning configuration:\n\n"
        f"{model_lines}\n\n"
        "No evaluation requests were sent.\n\n"
        "Add these models to MODEL_REASONING_SETTINGS, explicitly specify their\n"
        "reasoning configuration, or opt into provider defaults with\n"
        "--use-provider-reasoning-defaults."
    )


def discover_input_files(input_dir: Path, pattern: str, *, recursive: bool) -> list[Path]:
    if not input_dir.exists():
        raise SystemExit(f"Input directory does not exist: {input_dir}")
    if not input_dir.is_dir():
        raise SystemExit(f"Input path is not a directory: {input_dir}")
    iterator = input_dir.rglob(pattern) if recursive else input_dir.glob(pattern)
    return sorted(path for path in iterator if path.is_file())


def load_csv(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            record = dict(row)
            record["id"] = record.get("id") or record.get("original_index", "")
            record["question"] = record.get("problem", "")
            records.append(record)
    return records


@dataclass(frozen=True)
class PredictionTask:
    state_key: tuple[str, str]
    model: str
    input_name: str
    record_index: int
    record_key: str
    record: dict[str, Any]
    round_number: int


class OutputState:
    def __init__(
        self,
        *,
        input_file: Path,
        model: str,
        records: list[dict[str, Any]],
        output_path: Path,
        existing: dict[str, dict[str, Any]],
    ) -> None:
        self.input_file = input_file
        self.model = model
        self.records = records
        self.output_path = output_path
        self.existing = existing
        self.lock = threading.Lock()


class ProgressTracker:
    def __init__(self, total: int) -> None:
        self.total = total
        self.done = 0
        self.success = 0
        self.errors = 0
        self.started_at = time.monotonic()
        self.lock = threading.Lock()

    def record(self, *, ok: bool, task: PredictionTask, elapsed_seconds: float) -> None:
        with self.lock:
            self.done += 1
            if ok:
                self.success += 1
            else:
                self.errors += 1
            if self.done % 10 == 0 or self.done == self.total or not ok:
                runtime = time.monotonic() - self.started_at
                rate = self.done / runtime if runtime > 0 else 0.0
                print(
                    "[progress] "
                    f"{self.done}/{self.total} tasks, success={self.success}, errors={self.errors}, "
                    f"rate={rate:.2f}/s, last={task.model} {task.input_name} "
                    f"record={task.record_index} round={task.round_number} "
                    f"elapsed={elapsed_seconds:.1f}s",
                    flush=True,
                )


def run_global_queue(*, input_files: list[Path], settings: RunSettings) -> None:
    states: dict[tuple[str, str], OutputState] = {}
    tasks: list[PredictionTask] = []

    for input_file in input_files:
        records = load_csv(input_file)
        if settings.limit is not None:
            records = records[: settings.limit]
        if not records:
            print(f"[skip] {input_file}: no records", flush=True)
            continue
        print(f"[load] {input_file.name}: {len(records)} records", flush=True)
        for model in settings.models:
            state = build_output_state(input_file=input_file, records=records, model=model, settings=settings)
            state_key = (str(input_file), model)
            states[state_key] = state
            model_tasks = build_prediction_tasks(state_key=state_key, state=state, settings=settings)
            tasks.extend(model_tasks)
            completed_records = sum(
                1
                for index, record in enumerate(records)
                if prediction_count(state.existing.get(record_key(record, index), {})) >= settings.rounds
            )
            print(
                f"[queue] {model} {input_file.name}: records_complete={completed_records}/{len(records)}, "
                f"tasks={len(model_tasks)}, output={state.output_path}",
                flush=True,
            )

    if not tasks:
        print("[done] no missing prediction tasks", flush=True)
        return

    random.shuffle(tasks)
    print(
        f"[run] global task queue: tasks={len(tasks)}, files_models={len(states)}, "
        f"concurrency={settings.concurrency}, rounds={settings.rounds}",
        flush=True,
    )
    progress = ProgressTracker(total=len(tasks))
    with concurrent.futures.ThreadPoolExecutor(max_workers=settings.concurrency) as executor:
        futures = [
            executor.submit(process_prediction_task, task, states[task.state_key], settings, progress)
            for task in tasks
        ]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as exc:  # noqa: BLE001
                print(f"[error] worker crashed unexpectedly: {type(exc).__name__}: {exc}", flush=True)

    print(
        f"[done] global task queue: tasks={progress.done}, success={progress.success}, "
        f"errors={progress.errors}",
        flush=True,
    )


def build_output_state(
    *,
    input_file: Path,
    records: list[dict[str, Any]],
    model: str,
    settings: RunSettings,
) -> OutputState:
    output_path = settings.output_dir / f"{input_file.stem}.{safe_model_name(model)}.jsonl"
    existing = load_existing_output(output_path)
    state = OutputState(
        input_file=input_file,
        model=model,
        records=records,
        output_path=output_path,
        existing=existing,
    )
    atomic_write_jsonl(output_path, ordered_existing_records(existing, records, settings.rounds))
    return state


def build_prediction_tasks(
    *,
    state_key: tuple[str, str],
    state: OutputState,
    settings: RunSettings,
) -> list[PredictionTask]:
    tasks: list[PredictionTask] = []
    for index, record in enumerate(state.records):
        key = record_key(record, index)
        previous = state.existing.get(key) or {}
        starting_success_count = prediction_count(previous)
        missing_rounds = max(settings.rounds - starting_success_count, 0)
        for offset in range(missing_rounds):
            tasks.append(
                PredictionTask(
                    state_key=state_key,
                    model=state.model,
                    input_name=state.input_file.name,
                    record_index=index,
                    record_key=key,
                    record=record,
                    round_number=starting_success_count + offset + 1,
                )
            )
    return tasks


def process_prediction_task(
    task: PredictionTask,
    state: OutputState,
    settings: RunSettings,
    progress: ProgressTracker,
) -> None:
    started_at = time.monotonic()
    ok = False
    try:
        response = call_openrouter(
            model=task.model,
            user_content=build_user_content(task.record, settings.blob_mode),
            settings=settings,
        )
        prediction = prediction_from_response(
            response,
            request_settings=request_settings_for_output(
                model=task.model,
                settings=settings,
            ),
        )
        ok = True
    except Exception as exc:  # noqa: BLE001
        prediction = {
            "answer": "",
            "error": f"{type(exc).__name__}: {exc}",
            "request_settings": request_settings_for_output(
                model=task.model,
                settings=settings,
            ),
        }
        print(
            f"[error] {task.model} {task.input_name} record={task.record_index} "
            f"round={task.round_number}: {exc}",
            flush=True,
        )

    append_prediction(task=task, state=state, prediction=prediction, rounds=settings.rounds)
    progress.record(ok=ok, task=task, elapsed_seconds=time.monotonic() - started_at)


def append_prediction(
    *,
    task: PredictionTask,
    state: OutputState,
    prediction: dict[str, Any],
    rounds: int,
) -> None:
    with state.lock:
        previous = state.existing.get(task.record_key) or {}
        predictions = previous.get("predictions")
        if not isinstance(predictions, list):
            predictions = []
        predictions = list(predictions)
        predictions.append(prediction)
        state.existing[task.record_key] = {
            "id": task.record.get("id", task.record_key),
            "question": stringify(task.record.get("question")),
            "answer": task.record.get("answer", task.record.get("reference_answer", "")),
            "predictions": predictions,
        }
        atomic_write_jsonl(
            state.output_path,
            ordered_existing_records(state.existing, state.records, rounds),
        )


def build_user_content(record: dict[str, Any], blob_mode: str) -> str:
    question = stringify(record.get("question"))
    blob = stringify(record.get("blob"))
    if blob_mode == "only":
        return blob
    if blob_mode == "append" and blob:
        return f"{blob}\n\n{question}" if question else blob
    return question


def call_openrouter(*, model: str, user_content: str, settings: RunSettings) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": model,
        "temperature": settings.temperature,
        "messages": [{"role": "user", "content": user_content}],
    }
    if settings.max_tokens is not None:
        payload["max_tokens"] = settings.max_tokens
    apply_reasoning_settings(
        payload,
        model=model,
        reasoning_effort=settings.reasoning_effort,
        use_provider_reasoning_defaults=settings.use_provider_reasoning_defaults,
    )

    headers = {
        "Authorization": f"Bearer {settings.api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": OPENROUTER_USER_AGENT,
        "HTTP-Referer": OPENROUTER_REFERER,
        "X-Title": OPENROUTER_TITLE,
    }
    last_error: str | None = None

    for attempt in range(settings.max_retries + 1):
        try:
            response = requests.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload,
                timeout=settings.timeout_seconds,
                proxies=requests_proxies(settings.proxy),
            )
            if response.status_code in RETRY_STATUS_CODES:
                last_error = f"HTTP {response.status_code}: {response.text[:800]}"
                if attempt >= settings.max_retries:
                    break
                sleep_before_retry(attempt, settings, retry_after=response.headers.get("Retry-After"))
                continue
            if response.status_code != 200:
                raise RuntimeError(f"HTTP {response.status_code}: {response.text[:800]}")
            data = response.json()
            validate_openrouter_response(data, model=model)
            return data
        except (
            TimeoutError,
            ConnectionError,
            OSError,
            json.JSONDecodeError,
            requests.RequestException,
            RuntimeError,
        ) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt >= settings.max_retries:
                break
            sleep_before_retry(attempt, settings, retry_after=None)

    raise RuntimeError(f"OpenRouter call failed after retries. Last error: {last_error}")


def apply_reasoning_settings(
    payload: dict[str, Any],
    *,
    model: str,
    reasoning_effort: str,
    use_provider_reasoning_defaults: bool = False,
) -> None:
    """Apply audited defaults or an explicit reasoning configuration."""
    if reasoning_effort == "auto":
        model_settings = MODEL_REASONING_SETTINGS.get(model)
        if model_settings is None:
            if use_provider_reasoning_defaults:
                return
            raise ValueError(f"No audited reasoning default for model: {model}")
        effort = model_settings.get("reasoning_effort")
        if effort:
            payload["reasoning"] = {"effort": str(effort), "exclude": False}
        else:
            payload["reasoning"] = {"enabled": True, "exclude": False}
        return
    payload["reasoning"] = {"effort": reasoning_effort, "exclude": False}


def request_settings_for_output(*, model: str, settings: RunSettings) -> dict[str, Any]:
    """Return request settings used for the OpenRouter call."""
    payload: dict[str, Any] = {}
    apply_reasoning_settings(
        payload,
        model=model,
        reasoning_effort=settings.reasoning_effort,
        use_provider_reasoning_defaults=settings.use_provider_reasoning_defaults,
    )
    return {
        "temperature": settings.temperature,
        "max_tokens": settings.max_tokens,
        "reasoning": payload.get("reasoning"),
        "verbosity": payload.get("verbosity"),
    }


def sleep_before_retry(
    attempt: int,
    settings: RunSettings,
    *,
    retry_after: str | None,
) -> None:
    retry_after_seconds = parse_retry_after(retry_after)
    if retry_after_seconds is not None:
        time.sleep(min(retry_after_seconds, settings.backoff_cap_seconds))
        return
    base = settings.backoff_base * (2**attempt)
    delay = min(base + random.uniform(0.0, 1.0), settings.backoff_cap_seconds)
    time.sleep(delay)


def parse_retry_after(value: str | None) -> float | None:
    if not value:
        return None
    try:
        parsed = float(value)
    except ValueError:
        return None
    return max(parsed, 0.0)


def validate_openrouter_response(data: dict[str, Any], *, model: str) -> None:
    error = data.get("error")
    if error:
        raise RuntimeError(f"OpenRouter JSON error for {model}: {error}")
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices:
        snippet = json.dumps(data, ensure_ascii=False)[:800]
        raise RuntimeError(f"OpenRouter returned no choices for {model}: {snippet}")
    message = (choices[0] or {}).get("message")
    if not isinstance(message, dict):
        snippet = json.dumps(data, ensure_ascii=False)[:800]
        raise RuntimeError(f"OpenRouter returned empty message for {model}: {snippet}")


def prediction_from_response(
    data: dict[str, Any],
    *,
    request_settings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the raw predicted answer plus the unmodified OpenRouter response."""
    choice = (data.get("choices") or [{}])[0] or {}
    message = choice.get("message") or {}
    usage = dict(data.get("usage") or {})
    usage["finish_reason"] = choice.get("finish_reason")
    usage["native_finish_reason"] = choice.get("native_finish_reason")
    return {
        "answer": message.get("content"),
        "raw_response": data,
        "usage": usage,
        "request_settings": request_settings if isinstance(request_settings, dict) else {},
    }


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
            if previous is None:
                best[key] = obj
                continue
            if prediction_count(obj) >= prediction_count(previous):
                best[key] = obj
    return best


def ordered_existing_records(
    existing: dict[str, dict[str, Any]],
    source_records: list[dict[str, Any]],
    rounds: int,
) -> list[dict[str, Any]]:
    ordered: list[dict[str, Any]] = []
    for index, source in enumerate(source_records):
        key = record_key(source, index)
        record = existing.get(key)
        if not record:
            continue
        predictions = record.get("predictions")
        if isinstance(predictions, list):
            record["predictions"] = predictions
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


def record_key(record: dict[str, Any], index: int) -> str:
    raw_id = record.get("id")
    if stringify(raw_id):
        return stringify(raw_id)
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


def prediction_count(record: dict[str, Any]) -> int:
    predictions = record.get("predictions")
    if not isinstance(predictions, list):
        return 0
    return sum(1 for prediction in predictions if successful_prediction(prediction))


def successful_prediction(prediction: Any) -> bool:
    """Return whether a prediction should count toward requested rounds."""
    if isinstance(prediction, dict):
        return "error" not in prediction
    return prediction is not None


def safe_model_name(model: str) -> str:
    return re.sub(r"[^0-9A-Za-z._-]+", "_", model.replace("/", "__"))


def stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def fetch_model_defaults(
    *,
    models: list[str],
    timeout_seconds: float,
    proxy: str | None,
) -> list[dict[str, Any]]:
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            response = requests.get(
                OPENROUTER_MODELS_URL,
                headers={"Accept": "application/json", "User-Agent": OPENROUTER_USER_AGENT},
                timeout=timeout_seconds,
                proxies=requests_proxies(proxy),
            )
            response.raise_for_status()
            data = response.json()
            break
        except (TimeoutError, OSError, json.JSONDecodeError, requests.RequestException) as exc:
            last_error = exc
            if attempt == 3:
                raise
            time.sleep(min(1.5 * (2**attempt) + random.uniform(0.0, 1.0), 20.0))
    else:  # pragma: no cover - loop always breaks or raises
        raise RuntimeError(f"Could not fetch model metadata: {last_error}")
    by_id = {item.get("id"): item for item in data.get("data", []) if isinstance(item, dict)}
    rows: list[dict[str, Any]] = []
    for model in models:
        item = by_id.get(model)
        if not item:
            rows.append({"id": model, "missing": True})
            continue
        rows.append(
            {
                "id": model,
                "context_length": item.get("context_length"),
                "max_completion_tokens": (item.get("top_provider") or {}).get(
                    "max_completion_tokens"
                ),
                "supported_parameters": item.get("supported_parameters"),
                "default_parameters": item.get("default_parameters"),
                "configured_reasoning": MODEL_REASONING_SETTINGS.get(model, {}),
                "openrouter_default_reasoning": "medium when reasoning.enabled is used; otherwise provider/model default",
            }
        )
    return rows


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        raise SystemExit(130)
