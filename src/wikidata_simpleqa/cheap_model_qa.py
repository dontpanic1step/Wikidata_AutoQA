"""OpenRouter text-completion client support for grading and lightweight judges."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from time import sleep
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .config import LLMConfig
from .network import clear_proxy, install_proxy

SYSTEM_PROMPT = "Answer the user's question directly and concisely."
OPENROUTER_REFERER = "https://example.com/wikidata-simpleqa"
OPENROUTER_TITLE = "Wikidata SimpleQA Generator"
OPENROUTER_USER_AGENT = "wikidata-simpleqa-generator/0.1"


def parse_json_object(text: str) -> dict[str, Any]:
    """Parse the first JSON object embedded in a model response."""
    stripped = text.strip()
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("Model response did not contain a JSON object.")
    return json.loads(stripped[start : end + 1])


@dataclass(slots=True)
class OpenRouterCheapModelQAClient:
    """Small OpenRouter client exposing the complete_text interface."""

    config: LLMConfig
    timeout_seconds: float
    base_url: str = ""
    api_key: str = ""
    proxy: str | None = None

    def __post_init__(self) -> None:
        self.base_url = self.config.base_url or "https://openrouter.ai/api/v1"
        self.api_key = os.environ.get(self.config.api_key_env)
        if not self.api_key:
            raise ValueError(f"Missing API key in environment variable {self.config.api_key_env}")
        self.proxy = self.config.proxy
        install_proxy(self.proxy)

    def complete_text(self, prompt: str) -> str:
        """Return the assistant text for one prompt."""
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
        return str(body["choices"][0]["message"]["content"]).strip()

    def _request_with_retry(self, request_payload: dict[str, Any], *, use_proxy: bool) -> dict[str, Any]:
        """Send one OpenRouter request with retries and direct fallback."""
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
                    last_error = RuntimeError(f"{type(exc).__name__}: {exc} body={response_body}")
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


def make_cheap_model_qa_client(
    config: LLMConfig | None,
    timeout_seconds: float,
) -> OpenRouterCheapModelQAClient | None:
    """Construct a cheap QA client for the selected provider."""
    if config is None:
        return None
    if config.provider == "openrouter":
        return OpenRouterCheapModelQAClient(config=config, timeout_seconds=timeout_seconds)
    raise ValueError(f"Unsupported cheap model provider: {config.provider}")
