"""One-shot LLM rewrite support for canonical questions."""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from dataclasses import asdict
from typing import Any
from urllib.request import Request, urlopen

from .config import LLMConfig
from .models import CandidateFact
from .network import install_proxy

SYSTEM_PROMPT = "You rewrite verified factual questions. Return JSON only."


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
        request = Request(
            url=f"{self.base_url.rstrip('/')}/chat/completions",
            data=json.dumps(request_payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        with urlopen(request, timeout=self.timeout_seconds) as response:
            body = json.loads(response.read().decode("utf-8"))
        text = body["choices"][0]["message"]["content"]
        return parse_json_object(text)


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
        "canonical_question": candidate.canonical_question,
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
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)
    return (
        "Rewrite the canonical question into one concise SimpleQA-style fact-seeking question.\n\n"
        "Rules:\n"
        '- Return JSON only: {"question": "..."}.\n'
        "- Do not answer the question.\n"
        "- Do not add or remove factual constraints.\n"
        "- Preserve all required anchors.\n"
        "- Do not include any year, date, month, or temporal phrase.\n"
        "- Do not use words like current, latest, recent, former, previous, or as of.\n"
        "- Do not include the answer or any answer alias.\n"
        "- Do not change the target relation.\n"
        "- Prefer a short, plain, natural question.\n\n"
        f"Payload:\n{serialized}"
    )


def parse_json_object(text: str) -> dict[str, Any]:
    """Parse a JSON object from a model response."""
    stripped = text.strip()
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("Model response did not contain a JSON object.")
    return json.loads(stripped[start : end + 1])
