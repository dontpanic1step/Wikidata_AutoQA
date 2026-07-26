"""One-shot LLM rewrite support for canonical questions."""

from __future__ import annotations

import json
import os
from copy import deepcopy
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
ANSWER_PRECISION_PROMPT_RULES = (
    "- If the answer is a temporal value, the question must specify the requested precision or unit, "
    "such as what year, what month, what day, or how many months.\n"
    "- If the answer is a full calendar date, ask `what month, day, and year ...` and format the "
    "reference answer like `May 20, 2024`; if the answer is a month, ask `what month and year ...` "
    "and format it like `May 2024`.\n"
    "- If the answer is a number, specify the counted quantity or unit in the question, such as gallons, "
    "people, months, authors, or tracks.\n"
    "- Do not add units to the reference answer or answer_aliases; keep numeric reference answers as "
    "normalized values only.\n"
)
DATE_PRECISION_PROMPT_RULES = (
    "- If the answer is a temporal value, the question must specify the requested precision or unit, "
    "such as what year, what month, what day, or how many months.\n"
    "- If the answer is a full calendar date, ask `what month, day, and year ...` and format the "
    "reference answer like `May 20, 2024`; if the answer is a month, ask `what month and year ...` "
    "and format it like `May 2024`.\n"
)
NUMBER_PRECISION_PROMPT_RULES = (
    "- If the answer is a number, specify the counted quantity or unit in the question, such as gallons, "
    "people, months, authors, or tracks.\n"
    "- Do not add units to the reference answer or answer_aliases; keep numeric reference answers as "
    "normalized values only.\n"
)
SOURCE_TABLE_WORDING_RULE = (
    "- Do not phrase questions as `according to the table` or `according to the [source] table`; "
    "name the actual subject/event/list instead. Only use `according to ...` when the source is a "
    "well-known named chart or list, such as a Billboard chart or UNESCO list.\n"
)
CUMULATIVE_FACT_PROMPT_RULE = (
    "- Do not ask cumulative-statistic questions such as how many goals Messi has scored, total wins, "
    "career points, revenue, downloads, citations, or followers unless the statistic is explicitly "
    "scoped to a historically settled slice, completed event, completed season, or fixed table/list.\n"
)
HISTORICALLY_SETTLED_PROMPT_RULE = (
    "- Only ask for an answer that is historically settled and cannot change; reject mutable "
    "statuses, current roles, live affiliations, and other facts whose answer can change over time.\n"
)
NO_SOCIAL_SCIENCE_RESEARCH_PROMPT = (
    "Ask factual questions, not questions about the findings or conclusions of social science research, "
    "such as results derived from census studies."
)


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
        return self.rewrite_question_with_audit(payload)["parsed_response"]

    def rewrite_question_with_audit(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Call OpenRouter and return parsed JSON plus full sanitized audit metadata."""
        prompt = build_rewrite_prompt(payload)
        request_payload = {
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        }
        body = self._request_with_retry(request_payload, use_proxy=bool(self.proxy))
        text = str(body["choices"][0]["message"]["content"])
        parsed = parse_json_object(text)
        return {
            "prompt": prompt,
            "request_payload": _sanitize_openrouter_request_payload(request_payload),
            "response_body": body,
            "raw_text": text,
            "parsed_response": parsed,
        }

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
        "answer_type": candidate.answer_type,
    }


def build_rewrite_prompt(payload: dict[str, Any]) -> str:
    """Build the one-shot prompt for question rewriting."""
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
    query_count = _query_count(payload)
    extra_prompt = _extra_prompt_text(payload)
    return (
        "Rewrite the question into one concise SimpleQA-style fact-seeking question.\n\n"
        "Rules:\n"
        "- Return JSON only.\n"
        "- Preserve all required anchors.\n"
        "- Preserve the same answer relation and information scope as the canonical question.\n"
        f"- Preserve the configured answer_type `{payload.get('answer_type', '')}` when one is provided.\n"
        "- Do not add, remove, narrow, broaden, or change any information from the canonical question; only rephrase it so it sounds natural.\n"
        "- Do not add a more specific degree, award, role, date, or other fact that is not already explicit in the canonical question or required anchors.\n"
        "- Do not include the answer or any answer alias in any casing, capitalization, or normalized variant.\n"
        "- The rewritten_question must not contain the answer or any answer alias.\n"
        f"{_answer_precision_prompt_rules(payload)}"
        f"{SOURCE_TABLE_WORDING_RULE}"
        f"{CUMULATIVE_FACT_PROMPT_RULE}"
        f"{HISTORICALLY_SETTLED_PROMPT_RULE}"
        f"{extra_prompt}"
        f"- Avoid these forbidden patterns: {forbidden_text}.\n"
        f"{cutoff_rule}"
        f"- Generate exactly {query_count} answer-blind search queries.\n\n"
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
    """Build the Wikidata-route rewrite-and-query prompt."""
    forbidden_patterns = payload.get("forbidden_patterns", [])
    forbidden_text = ", ".join(str(pattern) for pattern in forbidden_patterns)
    query_count = _query_count(payload)
    extra_prompt = _extra_prompt_text(payload)
    required_anchors = ", ".join(str(anchor) for anchor in payload.get("required_anchors", []))
    required_reasoning_clues = ", ".join(
        str(clue) for clue in payload.get("required_reasoning_clues", [])
    )
    route_contract = str(payload.get("route_contract", "")).strip()
    multi_hop_rule = ""
    if route_contract == "route1_qid_first_multihop_join":
        multi_hop_rule = (
            "- This is a Route 1 QID-first multi-hop join question. Preserve the required reasoning clues so the question cannot be answered as a simpler single-hop question.\n"
            "- Do not name hidden bridge entities from the reasoning path unless the canonical question already names them.\n"
        )
    hidden_entity_contracts = {"route1_hidden_entity_two_hop"}
    if route_contract in hidden_entity_contracts:
        route_label = "Route 1"
        multi_hop_rule = (
            f"- This is a {route_label} hidden-entity two-hop question. Ask for the answer hop's object while identifying the hidden entity only through the clue hop.\n"
            "- Do not name any hidden entity in the rewritten question or search queries.\n"
            "- Preserve the clue relation and visible clue so the question cannot be answered as a simple one-hop fact about a named subject.\n"
        )
    route_specific_context = ""
    if route_contract in hidden_entity_contracts:
        route_specific_context = (
            f"- Answer hop: {json.dumps(payload.get('answer_hop', {}), ensure_ascii=False)}\n"
            f"- Clue hop: {json.dumps(payload.get('clue_hop', {}), ensure_ascii=False)}\n"
            f"- Clue orientation: {payload.get('clue_orientation', '')}\n"
            f"- Hidden entities: {json.dumps(payload.get('hidden_entities', []), ensure_ascii=False)}\n"
            f"- Visible clue: {json.dumps(payload.get('visible_clue', {}), ensure_ascii=False)}\n"
        )
    return (
        "You are generating a SimpleQA-style factual question and answer-blind search queries for a Wikidata-backed route.\n\n"
        "Input:\n"
        f"- Canonical question: {payload.get('canonical_question', '')}\n"
        f"- Wikidata triplet text: {payload.get('wikidata_triplet_text', '')}\n"
        f"{route_specific_context}"
        f"- Required anchors: {required_anchors}\n"
        f"- Required reasoning clues: {required_reasoning_clues}\n"
        f"- Answer type: {payload.get('answer_type', '')}\n"
        f"- Route contract: {route_contract}\n"
        f"- Forbidden text: {forbidden_text}\n"
        f"- Cutoff year: {payload.get('cutoff_year', '')}\n\n"
        "Task:\n"
        "1. Rewrite the canonical question into a natural factual question.\n"
        "2. Preserve the fact expressed by the Wikidata triplet text.\n"
        "3. Do not add, remove, narrow, broaden, or change any information from the canonical question; only rephrase it so it sounds natural.\n"
        "4. Keep all required anchors and disambiguating cues.\n"
        "5. The rewritten_question must not contain the answer or any answer alias.\n"
        f"6. Generate exactly {query_count} answer-blind search queries for long-tail verification.\n"
        "7. Return extra answer aliases or abbreviations that may appear in snippets, using [] if none.\n\n"
        "Important constraints:\n"
        "- The search queries must not contain the answer or any answer alias.\n"
        "- The queries should use only non-answer context from the canonical question or triplet text.\n"
        "- Preserve the same answer relation as the canonical question. Do not narrow or specialize it.\n"
        "- Preserve the configured answer type; do not rewrite the question so it asks for a different type of answer.\n"
        "- If the canonical question says `first degree`, do not rewrite it as a named degree such as `Doctor of Medicine`.\n"
        "- Do not add any degree name, date, title, role, or other factual detail that is absent from the canonical question unless it is already required for disambiguation.\n"
        f"{multi_hop_rule}"
        f"{_answer_precision_prompt_rules(payload)}"
        f"{SOURCE_TABLE_WORDING_RULE}"
        f"{CUMULATIVE_FACT_PROMPT_RULE}"
        f"{HISTORICALLY_SETTLED_PROMPT_RULE}"
        f"{extra_prompt}"
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
    query_count = _query_count(payload)
    extra_prompt = _extra_prompt_text(payload)
    return (
        "You are generating a SimpleQA-style factual question and answer-blind search queries for Route 2.\n\n"
        "Input:\n"
        f"- Canonical question: {payload.get('canonical_question', '')}\n"
        f"- Evidence text: {payload.get('evidence_text', '')}\n"
        f"- Answer type: {payload.get('answer_type', '')}\n"
        f"- Forbidden text: {forbidden_text}\n"
        f"- Cutoff year: {payload.get('cutoff_year', '')}\n\n"
        "Task:\n"
        "1. Rewrite the canonical question into a natural factual question.\n"
        "2. Preserve the fact supported by the evidence text.\n"
        "3. Do not add, remove, narrow, broaden, or change any information from the canonical question; only rephrase it so it sounds natural.\n"
        "4. Keep all required anchors.\n"
        "5. The rewritten_question must not contain the answer or any answer alias.\n"
        f"6. Generate exactly {query_count} answer-blind search queries for long-tail verification.\n"
        "7. Return extra answer aliases or abbreviations that may appear in snippets, using [] if none.\n\n"
        "Important constraints:\n"
        "- The search queries must not contain the answer or any answer alias.\n"
        "- Preserve the same answer relation as the canonical question. Do not narrow or specialize it.\n"
        "- Preserve the configured answer type; do not rewrite the question so it asks for a different type of answer.\n"
        "- Do not add a more specific degree, award, role, date, or other factual detail that is absent from the canonical question unless it is already required for disambiguation.\n"
        f"{_answer_precision_prompt_rules(payload)}"
        f"{SOURCE_TABLE_WORDING_RULE}"
        f"{CUMULATIVE_FACT_PROMPT_RULE}"
        f"{HISTORICALLY_SETTLED_PROMPT_RULE}"
        f"{extra_prompt}"
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




def parse_json_object(text: str) -> dict[str, Any]:
    """Parse a JSON object from a model response."""
    stripped = text.strip()
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("Model response did not contain a JSON object.")
    return json.loads(stripped[start : end + 1])


def _query_count(payload: dict[str, Any]) -> int:
    """Return the configured answer-blind query count for a rewrite prompt."""
    try:
        return max(0, int(payload.get("search_query_count", 3)))
    except (TypeError, ValueError):
        return 3


def _answer_precision_prompt_rules(payload: dict[str, Any]) -> str:
    """Return answer precision guidance only when it matches the configured answer type."""
    answer_type = str(payload.get("answer_type") or "").strip()
    if not answer_type:
        return ANSWER_PRECISION_PROMPT_RULES
    if answer_type == "Date":
        return DATE_PRECISION_PROMPT_RULES
    if answer_type == "Number":
        return NUMBER_PRECISION_PROMPT_RULES
    return ""


def _extra_prompt_text(payload: dict[str, Any]) -> str:
    """Return optional stricter prompt rules supplied by upstream routes."""
    raw_values = payload.get("extra_prompt") or payload.get("extra_prompts") or []
    if isinstance(raw_values, str):
        values = [raw_values]
    elif isinstance(raw_values, list):
        values = [str(value).strip() for value in raw_values]
    else:
        values = []
    lines = [value.rstrip(".") for value in values if value]
    return "".join(f"- {line}.\n" for line in lines)


def _sanitize_openrouter_request_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of an OpenRouter request payload without secret-bearing fields."""
    return deepcopy(payload)
