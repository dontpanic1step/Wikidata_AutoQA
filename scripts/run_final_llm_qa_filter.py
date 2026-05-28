#!/usr/bin/env python3
"""Run final LLM QA filtering for accepted Wikipedia table QA records."""

from __future__ import annotations

import argparse
import asyncio
import glob
import json
import os
import re
import socket
import tempfile
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import sleep
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


RUBRIC_KEYS = (
    "answer_derivable_from_context",
    "unique_and_stable_answer",
    "self_contained_question",
    "question_matches_answer_type",
)

DOMAIN_CHOICES = (
    "Science & technology",
    "Politics",
    "Art",
    "Geography",
    "Sports",
    "Music",
    "TV Shows",
    "History",
    "Video Games",
    "Other",
)

ANSWER_TYPE_DEFINITIONS = {
    "Person": "answer must be a person's name, not a team's name or a named group of people",
    "Place": (
        "answer must be a place name, location, or geographic entity, not an organization, "
        "company, ceremony or event. Question must be specific, e.g., `Which country ...`, "
        "`In which city ...`, instead of vague `Where ...` `Which place ...`"
    ),
    "Number": "answer must be numeric",
    "Date": "answer must be a date, month, or year, not a numeric measurement (e.g., 5 months) or range (e.g.,1920-1921)",
    "Other": (
        "answer must not be a person, place, number, or date; exclude numeric "
        "measurements, percentages, counts, scores, indices, rates, temperatures, "
        "durations, ranges, dates, years, people, and places"
    ),
}

SYSTEM_PROMPT = (
    "You are a conservative final reviewer for SimpleQA-style factual QA records. "
    "Return JSON only."
)

OPENROUTER_REFERER = "https://example.com/wikidata-simpleqa"
OPENROUTER_TITLE = "Wikidata SimpleQA Generator"
OPENROUTER_USER_AGENT = "wikidata-simpleqa-final-qa-filter/0.1"


def utc_now_iso() -> str:
    """Return a compact UTC timestamp for audit metadata."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load a JSONL file into memory."""
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def discover_input_files(input_path: Path, pattern: str) -> list[Path]:
    """Return JSONL input files from a single file or directory."""
    if input_path.is_file():
        return [input_path]
    if input_path.is_dir():
        return sorted(Path(p) for p in glob.glob(str(input_path / pattern)) if Path(p).is_file())
    raise FileNotFoundError(f"Input path does not exist: {input_path}")


def build_context_text(record: dict[str, Any]) -> str:
    """Build the exact judge context from page fields and stored markdown tables."""
    source_metadata = record.get("source_metadata") or {}
    parsed_tables = source_metadata.get("parsed_tables") or []

    lines = [
        f"Page title: {source_metadata.get('page_title', '')}",
        f"First paragraph: {source_metadata.get('first_paragraph', '')}",
        "",
        "Parsed markdown tables:",
    ]

    if not parsed_tables:
        lines.append("(No parsed tables were provided.)")

    for table in parsed_tables:
        if not isinstance(table, dict):
            continue
        lines.extend(
            [
                "",
                f"Table index: {table.get('table_index', '')}",
                f"Section heading: {table.get('section_heading', '')}",
                f"Caption: {table.get('caption', '')}",
                f"Nearby paragraph: {table.get('nearby_intro', '')}",
                "Markdown table:",
                str(table.get("markdown", "")),
            ]
        )

    return "\n".join(lines)


def build_judge_prompt(record: dict[str, Any]) -> str:
    """Build the final QA judge prompt for one accepted record."""
    answer_type_lines = "\n".join(
        f"- {name}: {definition}" for name, definition in ANSWER_TYPE_DEFINITIONS.items()
    )
    domain_choices = ", ".join(DOMAIN_CHOICES)
    aliases = record.get("answer_aliases", [])
    if aliases is None:
        aliases = []

    return f"""Evaluate whether this QA record should pass final filtering.

Return one JSON object only. Do not include markdown fences. Do not include an overall_reason field.

Required JSON schema:
{{
  "rubrics": {{
    "answer_derivable_from_context": {{"verdict": "YES|NO|N/A", "reason": "..."}},
    "unique_and_stable_answer": {{"verdict": "YES|NO|N/A", "reason": "..."}},
    "self_contained_question": {{"verdict": "YES|NO|N/A", "reason": "..."}},
    "question_matches_answer_type": {{"verdict": "YES|NO|N/A", "reason": "..."}}
  }},
  "domain_choice": "one of the allowed domains"
}}

Rubrics:
1. answer_derivable_from_context: Can the reference answer be inferred from the supplied parsed markdown tables plus page/context text?
2. unique_and_stable_answer: Is the intended answer unique, non-ambiguous, and time-invariant?
3. self_contained_question: Is the question self-contained and not overly tied to the table artifact itself?
4. question_matches_answer_type: Does the question ask for the same kind of answer as answer_type?

Answer type definitions:
{answer_type_lines}

Use N/A only when the supplied evidence is genuinely insufficient to decide a rubric.

Choose exactly one topical QA domain from this list. This is not the answer type:
{domain_choices}

QA:
- question: {record.get('question', '')}
- answer: {record.get('answer', '')}
- answer_aliases: {json.dumps(aliases, ensure_ascii=False)}
- answer_type: {record.get('answer_type', '')}

Context:
{build_context_text(record)}
"""


def parse_json_object(text: str) -> dict[str, Any]:
    """Parse the first JSON object embedded in model output."""
    stripped = text.strip()
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("Judge response did not contain a JSON object.")
    return json.loads(stripped[start : end + 1])


def normalize_verdict(value: Any) -> str:
    """Normalize a judge verdict to YES, NO, or N/A."""
    text = str(value or "").strip().upper()
    if text in {"YES", "NO", "N/A"}:
        return text
    if text in {"NA", "N.A.", "N / A"}:
        return "N/A"
    return "N/A"


def verdict_to_bool(verdict: str) -> bool | None:
    """Convert YES/NO/N/A into bool/null output."""
    normalized = normalize_verdict(verdict)
    if normalized == "YES":
        return True
    if normalized == "NO":
        return False
    return None


def empty_rubric_result() -> dict[str, dict[str, str]]:
    """Return an N/A result shell for all rubrics."""
    return {key: {"verdict": "N/A", "reason": ""} for key in RUBRIC_KEYS}


def _parse_textual_rubrics(text: str) -> dict[str, dict[str, str]]:
    """Fallback parser for older numbered YES/NO/N/A rubric responses."""
    rubric_result = empty_rubric_result()
    header_pat = re.compile(
        r"(?im)^\s*(?:\*\*)?(?:Rubric\s*)?(?:Question\s*)?(\d{1,2}|[a-z_]+)\s*(?:\*\*)?\s*[\.:)\-]",
    )
    headers = list(header_pat.finditer(text))
    key_by_number = {str(i): key for i, key in enumerate(RUBRIC_KEYS, start=1)}
    key_by_number.update({key: key for key in RUBRIC_KEYS})

    for index, header in enumerate(headers):
        label = header.group(1).lower()
        key = key_by_number.get(label)
        if not key:
            continue
        start = header.end()
        end = headers[index + 1].start() if index + 1 < len(headers) else len(text)
        segment = text[start:end].strip()
        token_match = re.search(r"\b(YES|NO|N/A|NA)\b", segment, flags=re.IGNORECASE)
        verdict = normalize_verdict(token_match.group(1) if token_match else "N/A")
        reason = segment
        if token_match:
            reason = (segment[: token_match.start()] + segment[token_match.end() :]).strip(" :-\n")
        rubric_result[key] = {"verdict": verdict, "reason": reason}

    return rubric_result


def parse_judge_response(text: str) -> tuple[dict[str, dict[str, str]], str | None]:
    """Parse structured judge output into rubric results and a domain choice."""
    try:
        payload = parse_json_object(text)
    except (json.JSONDecodeError, ValueError):
        rubric_result = _parse_textual_rubrics(text)
        domain_match = re.search(
            r"(?im)\bdomain(?:_choice)?\s*[:\-]\s*(.+?)\s*$",
            text,
        )
        domain = normalize_domain_choice(domain_match.group(1).strip() if domain_match else None)
        return rubric_result, domain

    raw_rubrics = payload.get("rubrics")
    if not isinstance(raw_rubrics, dict):
        raise ValueError("Judge JSON did not contain a rubrics object.")

    rubric_result: dict[str, dict[str, str]] = {}
    for key in RUBRIC_KEYS:
        raw = raw_rubrics.get(key)
        if isinstance(raw, dict):
            verdict = normalize_verdict(raw.get("verdict"))
            reason = str(raw.get("reason") or "")
        else:
            verdict = normalize_verdict(raw)
            reason = ""
        rubric_result[key] = {"verdict": verdict, "reason": reason}

    domain = normalize_domain_choice(payload.get("domain_choice"))
    if domain is None:
        raise ValueError(f"Invalid or missing domain_choice: {payload.get('domain_choice')!r}")
    return rubric_result, domain


def normalize_domain_choice(value: Any) -> str | None:
    """Normalize a judge domain choice to the allowed enum."""
    if value is None:
        return None
    text = str(value).strip()
    for choice in DOMAIN_CHOICES:
        if text.lower() == choice.lower():
            return choice
    return None


def bool_result_from_rubrics(rubric_result: dict[str, dict[str, str]]) -> dict[str, bool | None]:
    """Build the bool_result payload from parsed rubric verdicts."""
    return {
        key: verdict_to_bool((rubric_result.get(key) or {}).get("verdict", "N/A"))
        for key in RUBRIC_KEYS
    }


@dataclass(slots=True)
class OpenRouterJudgeClient:
    """Minimal OpenRouter chat-completions client for final QA judging."""

    api_key_env: str = "OPENROUTER_API_KEY"
    model: str = "openai/gpt-4.1-mini"
    base_url: str = "https://openrouter.ai/api/v1"
    timeout_seconds: float = 60.0
    max_retries: int = 3
    retry_backoff_seconds: float = 1.0
    retry_max_sleep_seconds: float = 30.0
    temperature: float = 0.0
    max_tokens: int = 900
    api_key: str = ""

    def __post_init__(self) -> None:
        self.api_key = os.environ.get(self.api_key_env)
        if not self.api_key:
            raise ValueError(f"Missing API key in environment variable {self.api_key_env}")

    def complete(self, prompt: str) -> str:
        """Return assistant text for one prompt."""
        payload = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        }
        body = self._request_with_retry(payload)
        return str(body["choices"][0]["message"]["content"]).strip()

    def _request_with_retry(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Send one OpenRouter request with retry/backoff."""
        endpoint = openrouter_chat_completions_endpoint(self.base_url)
        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            request = Request(
                url=endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": OPENROUTER_USER_AGENT,
                    "HTTP-Referer": OPENROUTER_REFERER,
                    "X-OpenRouter-Title": OPENROUTER_TITLE,
                },
                method="POST",
            )
            try:
                with urlopen(request, timeout=self.timeout_seconds) as response:
                    return json.loads(response.read().decode("utf-8"))
            except HTTPError as exc:
                response_body = ""
                try:
                    response_body = exc.read().decode("utf-8", errors="replace")
                except Exception:
                    response_body = ""
                last_error = RuntimeError(f"{type(exc).__name__}: {exc} body={response_body}")
                if exc.code not in {408, 409, 425, 429, 500, 502, 503, 504}:
                    break
            except (URLError, TimeoutError, socket.timeout, json.JSONDecodeError, KeyError) as exc:
                last_error = exc

            if attempt < self.max_retries:
                sleep(min(self.retry_backoff_seconds * (2**attempt), self.retry_max_sleep_seconds))

        if last_error is not None:
            raise last_error
        raise RuntimeError("OpenRouter request failed without an explicit error")


def openrouter_chat_completions_endpoint(base_url: str) -> str:
    """Accept either an OpenRouter base URL or the full chat-completions endpoint."""
    normalized = str(base_url).rstrip("/")
    if normalized.endswith("/chat/completions"):
        return normalized
    return f"{normalized}/chat/completions"


async def judge_record(
    record: dict[str, Any],
    client: Any,
    semaphore: asyncio.Semaphore,
    judge_model: str,
) -> dict[str, Any]:
    """Judge one record, preserving original fields and appending final filter data."""
    output = deepcopy(record)
    prompt = build_judge_prompt(record)
    created_at = utc_now_iso()

    try:
        async with semaphore:
            raw_response = await asyncio.to_thread(client.complete, prompt)
        rubric_result, domain_choice = parse_judge_response(raw_response)
        output["bool_result"] = bool_result_from_rubrics(rubric_result)
        output["domain_choice"] = domain_choice
        output["final_llm_qa_filter"] = {
            "analysis_status": "success",
            "judge_model": judge_model,
            "rubric_result": rubric_result,
            "domain_choice": domain_choice,
            "raw_response": raw_response,
            "created_at": created_at,
        }
    except Exception as exc:
        rubric_result = empty_rubric_result()
        output["bool_result"] = {key: None for key in RUBRIC_KEYS}
        output["domain_choice"] = None
        output["final_llm_qa_filter"] = {
            "analysis_status": "error",
            "judge_model": judge_model,
            "rubric_result": rubric_result,
            "domain_choice": None,
            "raw_response": "",
            "error": str(exc),
            "created_at": created_at,
        }

    return output


def answer_type_filename(answer_type: Any) -> str:
    """Convert an answer type into a stable output filename."""
    text = str(answer_type or "unknown").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    if not text:
        text = "unknown"
    return f"{text}.final_llm_qa_filtered.jsonl"


def group_by_answer_type(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group output records by answer_type-derived filename."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[answer_type_filename(record.get("answer_type"))].append(record)
    return dict(grouped)


def write_grouped_outputs(
    records: list[dict[str, Any]],
    output_path: Path,
    *,
    overwrite: bool = False,
) -> list[Path]:
    """Write one JSONL per answer type and return written paths."""
    output_path.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for filename, group in sorted(group_by_answer_type(records).items()):
        out_file = output_path / filename
        if out_file.exists() and not overwrite:
            raise FileExistsError(f"Output already exists; pass --overwrite to replace: {out_file}")
        atomic_write_jsonl(out_file, group)
        written.append(out_file)
    return written


def atomic_write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    """Atomically write JSONL by replacing from a same-directory temp file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name = ""
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temp_name = handle.name
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        if temp_name:
            try:
                Path(temp_name).unlink(missing_ok=True)
            except Exception:
                pass
        raise


async def run_filter(
    records: list[dict[str, Any]],
    client: Any,
    *,
    concurrency: int,
    judge_model: str,
) -> list[dict[str, Any]]:
    """Judge all records with bounded concurrency."""
    semaphore = asyncio.Semaphore(max(1, concurrency))
    tasks = [judge_record(record, client, semaphore, judge_model) for record in records]
    return await asyncio.gather(*tasks)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Run final LLM QA filtering over accepted JSONLs.")
    parser.add_argument("--input-path", required=True, type=Path, help="Accepted JSONL file or directory.")
    parser.add_argument("--output-path", required=True, type=Path, help="Directory for grouped output JSONLs.")
    parser.add_argument("--glob", default="*accepted*.jsonl", help="Directory input glob. Default: *accepted*.jsonl")
    parser.add_argument("--api-key-env", default="OPENROUTER_API_KEY", help="Environment variable containing the OpenRouter API key.")
    parser.add_argument("--judge-model", default="openai/gpt-4.1-mini", help="OpenRouter judge model.")
    parser.add_argument("--base-url", default="https://openrouter.ai/api/v1", help="OpenRouter API base URL.")
    parser.add_argument("--concurrency", type=int, default=10, help="Maximum concurrent judge calls.")
    parser.add_argument("--timeout-seconds", type=float, default=60.0, help="Per-request timeout.")
    parser.add_argument("--max-retries", type=int, default=3, help="Retries for transient OpenRouter errors.")
    parser.add_argument("--retry-backoff-seconds", type=float, default=1.0, help="Initial retry backoff for OpenRouter errors.")
    parser.add_argument("--retry-max-sleep-seconds", type=float, default=30.0, help="Maximum sleep between OpenRouter retries.")
    parser.add_argument("--max-tokens", type=int, default=900, help="Max tokens for judge response.")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing grouped output files.")
    return parser.parse_args()


def main() -> None:
    """CLI entry point."""
    args = parse_args()
    input_files = discover_input_files(args.input_path, args.glob)
    if not input_files:
        raise SystemExit(f"No input JSONL files found under {args.input_path} matching {args.glob!r}")

    records: list[dict[str, Any]] = []
    for input_file in input_files:
        records.extend(load_jsonl(input_file))

    client = OpenRouterJudgeClient(
        api_key_env=args.api_key_env,
        model=args.judge_model,
        base_url=args.base_url,
        timeout_seconds=args.timeout_seconds,
        max_retries=args.max_retries,
        retry_backoff_seconds=args.retry_backoff_seconds,
        retry_max_sleep_seconds=args.retry_max_sleep_seconds,
        max_tokens=args.max_tokens,
    )
    judged_records = asyncio.run(
        run_filter(
            records,
            client,
            concurrency=args.concurrency,
            judge_model=args.judge_model,
        )
    )
    written = write_grouped_outputs(judged_records, args.output_path, overwrite=args.overwrite)
    print(json.dumps({"input_files": [str(p) for p in input_files], "records": len(records), "outputs": [str(p) for p in written]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
