"""One-shot LLM rewrite support for canonical questions."""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from time import sleep
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .config import LLMConfig
from .models import CandidateFact
from .network import clear_proxy, install_proxy

SYSTEM_PROMPT = "You rewrite verified factual questions. Return JSON only."
OPENROUTER_REFERER = "https://example.com/wikidata-simpleqa"
OPENROUTER_TITLE = "Wikidata SimpleQA Generator"
OPENROUTER_USER_AGENT = "wikidata-simpleqa-generator/0.1"


class RewriteClient(ABC):
    """Abstract interface for one-shot question rewriting."""

    @abstractmethod
    def rewrite_question(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Return a JSON object with a rewritten question."""
        raise NotImplementedError


class OpenRouterRewriteClient(RewriteClient):
    """Rewrite client for OpenRouter via the OpenAI-compatible endpoint."""

    def __init__(self, config: LLMConfig, timeout_seconds: float) -> None:
        self.config = config
        self.timeout_seconds = timeout_seconds
        self.base_url = config.base_url or "https://openrouter.ai/api/v1"
        self.api_key = os.environ.get(config.api_key_env)
        if not self.api_key:
            raise ValueError(f"Missing API key in environment variable {config.api_key_env}")
        self.proxy = config.proxy
        install_proxy(config.proxy)

    def rewrite_question(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Call OpenRouter and return a parsed JSON object."""
        request_payload = {
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_rewrite_prompt(payload)},
            ],
        }
        body = self._request_with_retry(request_payload, use_proxy=bool(self.proxy))
        text = body["choices"][0]["message"]["content"]
        return parse_json_object(text)

    def _request_with_retry(self, request_payload: dict[str, Any], *, use_proxy: bool) -> dict[str, Any]:
        """Send one OpenRouter request with retries and optional direct fallback."""
        if use_proxy:
            install_proxy(self.proxy)
        else:
            clear_proxy()
        last_error: Exception | None = None
        try:
            for attempt in range(3):
                request = Request(
                    url=f"{self.base_url.rstrip('/')}/chat/completions",
                    data=json.dumps(request_payload).encode("utf-8"),
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
                    except Exception:  # noqa: BLE001
                        response_body = ""
                    last_error = RuntimeError(
                        f"{type(exc).__name__}: {exc} body={response_body}"
                    )
                    if attempt == 2:
                        break
                    sleep(min(2 ** attempt, 4))
                except URLError as exc:
                    last_error = exc
                    if attempt == 2:
                        break
                    sleep(min(2 ** attempt, 4))
        finally:
            if self.proxy:
                install_proxy(self.proxy)
            else:
                clear_proxy()
        if use_proxy and self.proxy:
            return self._request_with_retry(request_payload, use_proxy=False)
        if last_error is not None:
            raise last_error
        raise RuntimeError("OpenRouter request failed without an explicit error")


def make_rewrite_client(config: LLMConfig | None, timeout_seconds: float) -> RewriteClient | None:
    """Construct a rewrite client for the selected provider."""
    if config is None:
        return None
    if config.provider == "openrouter":
        return OpenRouterRewriteClient(config=config, timeout_seconds=timeout_seconds)
    raise ValueError(f"Unsupported rewrite provider: {config.provider}")


def build_rewrite_payload(candidate: CandidateFact) -> dict[str, Any]:
    """Build the rewrite payload for one candidate."""
    required_anchors = list(candidate.disambiguation_signature)
    required_anchors.extend(candidate.source_metadata.get("required_reasoning_clues", []))
    if candidate.subject_label:
        required_anchors.append(candidate.subject_label)
    return {
        "task_type": "route1_question_and_queries",
        "canonical_question": candidate.canonical_question,
        "wikidata_triplet_text": (
            f"{candidate.subject_label} -- {candidate.target_property_label} -- "
            f"{candidate.answer_labels[0] if candidate.answer_labels else ''}"
        ).strip(),
        "answer_labels": candidate.answer_labels,
        "answer_aliases": candidate.answer_aliases,
        "required_anchors": required_anchors,
        "forbidden_patterns": [
            "years",
            "dates",
            "this year",
            "current",
            "latest",
            "recent",
            "as of",
        ],
        "target_property": candidate.target_property_label,
        "domain": candidate.domain,
        "reasoning_style": candidate.reasoning_style,
    }


def build_rewrite_prompt(payload: dict[str, Any]) -> str:
    """Build the one-shot prompt for question rewriting."""
    if payload.get("task_type") == "kelm_question_and_queries":
        return build_kelm_rewrite_prompt(payload)
    if payload.get("task_type") == "route1_question_and_queries":
        return build_route1_rewrite_prompt(payload)
    if payload.get("task_type") == "route2_question_and_queries":
        return build_route2_rewrite_prompt(payload)
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)
    forbidden_patterns = payload.get(
        "forbidden_patterns",
        [
            "years",
            "dates",
            "this year",
            "current",
            "latest",
            "recent",
            "as of",
        ],
    )
    forbidden_text = ", ".join(str(pattern) for pattern in forbidden_patterns)
    cutoff_year = payload.get("cutoff_year")
    cutoff_rule = ""
    if cutoff_year is not None:
        cutoff_rule = f"- Avoid question wording that depends on events in {cutoff_year} or later.\n"
    return (
        "Rewrite the question into one concise SimpleQA-style fact-seeking question.\n\n"
        "Rules:\n"
        "- Return JSON only.\n"
        "- Preserve all required anchors.\n"
        "- Preserve the same answer relation and information scope as the canonical question.\n"
        "- Do not add, remove, narrow, broaden, or change any information from the canonical question; only rephrase it so it sounds natural.\n"
        "- Do not add a more specific degree, award, role, date, or other fact that is not already explicit in the canonical question or required anchors.\n"
        "- Do not include the answer or any answer alias in any casing, capitalization, or normalized variant.\n"
        "- The rewritten_question must not contain the answer or any answer alias.\n"
        f"- Avoid these forbidden patterns: {forbidden_text}.\n"
        f"{cutoff_rule}"
        "- Generate exactly 5 answer-blind search queries.\n\n"
        f"Payload:\n{serialized}\n\n"
        "Output valid JSON only:\n"
        "{\n"
        '  "rewritten_question": string,\n'
        '  "search_queries": string[],\n'
        '  "answer_aliases": string[],\n'
        '  "discard_reason": string | null\n'
        "}\n"
    )


def build_route1_rewrite_prompt(payload: dict[str, Any]) -> str:
    """Build the Route 1 rewrite-and-query prompt."""
    forbidden_patterns = payload.get("forbidden_patterns", [])
    forbidden_text = ", ".join(str(pattern) for pattern in forbidden_patterns)
    return (
        "You are generating a SimpleQA-style factual question and answer-blind search queries for Route 1.\n\n"
        "Input:\n"
        f"- Canonical question: {payload.get('canonical_question', '')}\n"
        f"- Wikidata triplet text: {payload.get('wikidata_triplet_text', '')}\n"
        f"- Forbidden text: {forbidden_text}\n"
        f"- Cutoff year: {payload.get('cutoff_year', '')}\n\n"
        "Task:\n"
        "1. Rewrite the canonical question into a natural factual question.\n"
        "2. Preserve the fact expressed by the Wikidata triplet text.\n"
        "3. Do not add, remove, narrow, broaden, or change any information from the canonical question; only rephrase it so it sounds natural.\n"
        "4. Keep all required anchors and disambiguating cues.\n"
        "5. The rewritten_question must not contain the answer or any answer alias.\n"
        "6. Generate exactly 5 answer-blind search queries for long-tail verification.\n"
        "7. Return extra answer aliases or abbreviations that may appear in snippets, using [] if none.\n\n"
        "Important constraints:\n"
        "- The search queries must not contain the answer or any answer alias.\n"
        "- The queries should use only non-answer context from the canonical question or triplet text.\n"
        "- Preserve the same answer relation as the canonical question. Do not narrow or specialize it.\n"
        "- If the canonical question says `first degree`, do not rewrite it as a named degree such as `Doctor of Medicine`.\n"
        "- Do not add any degree name, date, title, role, or other factual detail that is absent from the canonical question unless it is already required for disambiguation.\n"
        f"- Avoid these forbidden patterns: {forbidden_text}.\n"
        f"- Avoid question wording that depends on events in {payload.get('cutoff_year', '')} or later.\n"
        "- The first query will be the rewritten question itself and will be added by code. Do not repeat it in search_queries.\n\n"
        "Output valid JSON only:\n"
        "{\n"
        '  "rewritten_question": string,\n'
        '  "search_queries": string[],\n'
        '  "answer_aliases": string[],\n'
        '  "discard_reason": string | null\n'
        "}\n"
    )


def build_route2_rewrite_prompt(payload: dict[str, Any]) -> str:
    """Build the Route 2 rewrite-and-query prompt."""
    forbidden_patterns = payload.get("forbidden_patterns", [])
    forbidden_text = ", ".join(str(pattern) for pattern in forbidden_patterns)
    return (
        "You are generating a SimpleQA-style factual question and answer-blind search queries for Route 2.\n\n"
        "Input:\n"
        f"- Canonical question: {payload.get('canonical_question', '')}\n"
        f"- Evidence text: {payload.get('evidence_text', '')}\n"
        f"- Forbidden text: {forbidden_text}\n"
        f"- Cutoff year: {payload.get('cutoff_year', '')}\n\n"
        "Task:\n"
        "1. Rewrite the canonical question into a natural factual question.\n"
        "2. Preserve the fact supported by the evidence text.\n"
        "3. Do not add, remove, narrow, broaden, or change any information from the canonical question; only rephrase it so it sounds natural.\n"
        "4. Keep all required anchors.\n"
        "5. The rewritten_question must not contain the answer or any answer alias.\n"
        "6. Generate exactly 5 answer-blind search queries for long-tail verification.\n"
        "7. Return extra answer aliases or abbreviations that may appear in snippets, using [] if none.\n\n"
        "Important constraints:\n"
        "- The search queries must not contain the answer or any answer alias.\n"
        "- Preserve the same answer relation as the canonical question. Do not narrow or specialize it.\n"
        "- Do not add a more specific degree, award, role, date, or other factual detail that is absent from the canonical question unless it is already required for disambiguation.\n"
        f"- Avoid these forbidden patterns: {forbidden_text}.\n"
        f"- Avoid question wording that depends on events in {payload.get('cutoff_year', '')} or later.\n"
        "- The first query will be the rewritten question itself and will be added by code. Do not repeat it in search_queries.\n\n"
        "Output valid JSON only:\n"
        "{\n"
        '  "rewritten_question": string,\n'
        '  "search_queries": string[],\n'
        '  "answer_aliases": string[],\n'
        '  "discard_reason": string | null\n'
        "}\n"
    )


def build_kelm_rewrite_prompt(payload: dict[str, Any]) -> str:
    """Build the KELM-specific rewrite-and-query prompt."""
    forbidden_patterns = payload.get("forbidden_patterns", [])
    forbidden_text = ", ".join(str(pattern) for pattern in forbidden_patterns)
    return (
        "You are generating a SimpleQA-style factual question and answer-blind search queries for long-tail verification.\n\n"
        "Input:\n"
        f"- Serialized triple: {payload.get('serialized_triple', '')}\n"
        f"- KELM sentence: {payload.get('kelm_sentence', '')}\n"
        f"- Answer: {payload.get('answer', '')}\n"
        f"- Forbidden text: {forbidden_text}\n"
        f"- Cutoff year: {payload.get('cutoff_year', '')}\n\n"
        "Task:\n"
        "1. Rewrite the KELM sentence and triple into a natural factual question whose answer is exactly the provided answer.\n"
        "2. Preserve as much non-answer contextual information from the KELM sentence as possible in the question, including descriptors, locations, roles, and names, as long as they do not leak the answer.\n"
        "3. Do not add, remove, narrow, broaden, or change information from the source sentence or triple; only rephrase supported source information into a question.\n"
        "4. Do not use rigid templates. Write naturally.\n"
        "5. The rewritten_question must not contain the answer or any alias, casing variant, capitalization variant, or normalized form of the answer.\n"
        "6. Then generate exactly 5 answer-blind search queries that a user might try before knowing the answer.\n\n"
        "Important constraints:\n"
        "- The search queries must not contain the answer or any alias, casing variant, capitalization variant, or normalized form of the answer.\n"
        "- The queries should use only information available in the question, KELM sentence, or non-answer parts of the triple.\n"
        "- Preserve the same answer relation and information scope as the source.\n"
        "- Do not add a more specific degree, award, role, date, or other factual detail that is not explicit in the source.\n"
        f"- Avoid these forbidden patterns: {forbidden_text}.\n"
        f"- Avoid question wording that depends on events in {payload.get('cutoff_year', '')} or later.\n"
        "- The first query will be the rewritten question itself and will be added by code. Do not include the whole rewritten question in search_queries.\n"
        "- Prefer queries combining the subject with relation words, descriptors, locations, or other non-answer context.\n"
        "- Use quotation marks around rare names or exact entity names when helpful.\n\n"
        "Date and number constraints:\n"
        "- If the answer is a number, the unit or quantity type must be clear in the question.\n"
        "- If the answer is a date, only ask for the precision that is actually supported by the source. If the source only states a year, ask for the year, not the day/month/year.\n"
        "- Do not create false precision from serialized dates such as \"01 January YYYY\" unless the KELM sentence or source explicitly supports the full date.\n\n"
        "Output valid JSON only:\n"
        "{\n"
        '  "rewritten_question": string,\n'
        '  "search_queries": string[],\n'
        '  "answer_aliases": string[],\n'
        '  "discard_reason": string | null\n'
        "}\n"
    )


def parse_json_object(text: str) -> dict[str, Any]:
    """Parse a JSON object from a model response."""
    stripped = text.strip()
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("Model response did not contain a JSON object.")
    return json.loads(stripped[start : end + 1])
