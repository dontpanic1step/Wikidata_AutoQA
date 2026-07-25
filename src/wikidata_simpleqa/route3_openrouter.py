"""Crash-aware OpenRouter execution for the formal Route 3 workflow."""

from __future__ import annotations

import json
import os
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .cheap_model_qa import (
    OPENROUTER_REFERER,
    OPENROUTER_TITLE,
    OPENROUTER_USER_AGENT,
    SYSTEM_PROMPT,
)
from .config import LLMConfig
from .route3_circuit import ServiceCircuit
from .grading import ModelPanelMember
from .network import install_proxy
from .route3_external_calls import ExternalCallRecordStore
from .route3_run_ledger import canonical_json_sha256


@dataclass(frozen=True, slots=True)
class OpenRouterRawResponse:
    """One raw HTTP response returned by the thin transport."""

    status_code: int
    body_text: str


class OpenRouterThinTransportError(RuntimeError):
    """Base class for typed failures from one physical HTTP request."""


class OpenRouterHTTPError(OpenRouterThinTransportError):
    """A definite HTTP response returned by OpenRouter."""

    def __init__(self, *, status_code: int, body_text: str) -> None:
        self.status_code = int(status_code)
        self.body_text = str(body_text)
        super().__init__(f"OpenRouter returned HTTP {self.status_code}")


class OpenRouterAmbiguousTransportError(OpenRouterThinTransportError):
    """A transport failure where request delivery cannot be determined."""


class AmbiguousExternalCallError(RuntimeError):
    """An intent exists without a durable definite outcome."""

    def __init__(
        self,
        *,
        call_key: str,
        request_hash: str,
        transport_error: str = "",
        call_attempt: int = 1,
    ) -> None:
        self.call_key = str(call_key)
        self.request_hash = str(request_hash)
        self.transport_error = str(transport_error)
        self.call_attempt = int(call_attempt)
        self.retry_eligible = self.call_attempt == 1
        message = f"Ambiguous external call requires explicit resolution: {self.call_key}"
        if self.transport_error:
            message = f"{message}: {self.transport_error}"
        super().__init__(message)


class AbandonedExternalCallError(RuntimeError):
    """An ambiguous logical call was explicitly abandoned."""

    def __init__(self, *, call_key: str, request_hash: str, call_attempt: int) -> None:
        self.call_key = str(call_key)
        self.request_hash = str(request_hash)
        self.call_attempt = int(call_attempt)
        super().__init__(f"Ambiguous external call was abandoned: {self.call_key}")


class DefiniteOpenRouterHTTPError(RuntimeError):
    """A persisted explicit HTTP failure for one logical call."""

    def __init__(
        self,
        *,
        call_key: str,
        request_hash: str,
        status_code: int,
        body_text: str,
    ) -> None:
        self.call_key = str(call_key)
        self.request_hash = str(request_hash)
        self.status_code = int(status_code)
        self.body_text = str(body_text)
        super().__init__(f"OpenRouter logical call {self.call_key} returned HTTP {self.status_code}")


class DefiniteOpenRouterResponseError(RuntimeError):
    """A persisted response that cannot be decoded as an OpenRouter object."""

    def __init__(self, *, call_key: str, request_hash: str, error: Exception) -> None:
        self.call_key = str(call_key)
        self.request_hash = str(request_hash)
        self.error_type = type(error).__name__
        self.error_message = str(error)
        super().__init__(
            f"Persisted OpenRouter response is not valid JSON for {self.call_key}: "
            f"{self.error_type}: {self.error_message}"
        )


@dataclass(slots=True)
class Route3OpenRouterTransport:
    """Send exactly one physical OpenRouter request and return its raw response."""

    config: LLMConfig
    timeout_seconds: float
    base_url: str = ""
    api_key: str = ""

    def __post_init__(self) -> None:
        self.base_url = self.config.base_url or "https://openrouter.ai/api/v1"
        self.api_key = os.environ.get(self.config.api_key_env, "")
        if not self.api_key:
            raise ValueError(f"Missing API key in environment variable {self.config.api_key_env}")
        install_proxy(self.config.proxy)

    def send_once(self, payload: dict[str, Any]) -> OpenRouterRawResponse:
        """Perform one HTTP request without retry, fallback, or parsing."""
        request = Request(
            url=f"{self.base_url.rstrip('/')}/chat/completions",
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
                return OpenRouterRawResponse(
                    status_code=int(response.status),
                    body_text=response.read().decode("utf-8"),
                )
        except HTTPError as exc:
            raise OpenRouterHTTPError(
                status_code=int(exc.code),
                body_text=exc.read().decode("utf-8", errors="replace"),
            ) from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise OpenRouterAmbiguousTransportError(f"{type(exc).__name__}: {exc}") from exc


@dataclass(slots=True)
class Route3DurableOpenRouterExecutor:
    """Journal one logical OpenRouter call around a one-request transport."""

    store: ExternalCallRecordStore
    transport: Any
    circuit: ServiceCircuit | None = None

    def execute(self, *, call_key: str, request_payload: dict[str, Any]) -> dict[str, Any]:
        """Return a persisted or newly received OpenRouter response object."""
        request_hash = canonical_json_sha256(request_payload)
        call_attempt = self._call_attempt(
            call_key=call_key,
            request_hash=request_hash,
        )
        outcome = self.store.load_matching_outcome(
            call_key=call_key,
            request_hash=request_hash,
            call_attempt=call_attempt,
        )
        if outcome is not None:
            return self._resolve_outcome(outcome, call_key=call_key, request_hash=request_hash)

        if self.circuit is not None:
            self.circuit.before_call()
        try:
            self.store.commit(
                call_key=call_key,
                record_kind="intent",
                request_hash=request_hash,
                payload={"request_payload": deepcopy(request_payload)},
                call_attempt=call_attempt,
            )
        except FileExistsError as exc:
            raise AmbiguousExternalCallError(
                call_key=call_key,
                request_hash=request_hash,
                call_attempt=call_attempt,
            ) from exc
        try:
            raw_response = self.transport.send_once(request_payload)
        except OpenRouterHTTPError as exc:
            self._record_http_failure(exc.status_code)
            try:
                self.store.commit(
                    call_key=call_key,
                    record_kind="http_error",
                    request_hash=request_hash,
                    payload={
                        "status_code": exc.status_code,
                        "body_text": exc.body_text,
                    },
                    call_attempt=call_attempt,
                )
            except Exception as persistence_error:  # noqa: BLE001
                raise AmbiguousExternalCallError(
                    call_key=call_key,
                    request_hash=request_hash,
                    transport_error=(
                        "outcome_persistence_failed:"
                        f"{type(persistence_error).__name__}:{persistence_error}"
                    ),
                    call_attempt=call_attempt,
                ) from persistence_error
            raise DefiniteOpenRouterHTTPError(
                call_key=call_key,
                request_hash=request_hash,
                status_code=exc.status_code,
                body_text=exc.body_text,
            ) from exc
        except OpenRouterAmbiguousTransportError as exc:
            if self.circuit is not None:
                self.circuit.record_failure(reason="transport_ambiguity")
            raise AmbiguousExternalCallError(
                call_key=call_key,
                request_hash=request_hash,
                transport_error=str(exc),
                call_attempt=call_attempt,
            ) from exc

        try:
            self.store.commit(
                call_key=call_key,
                record_kind="response",
                request_hash=request_hash,
                payload={
                    "status_code": raw_response.status_code,
                    "body_text": raw_response.body_text,
                },
                call_attempt=call_attempt,
            )
        except Exception as persistence_error:  # noqa: BLE001
            raise AmbiguousExternalCallError(
                call_key=call_key,
                request_hash=request_hash,
                transport_error=(
                    "outcome_persistence_failed:"
                    f"{type(persistence_error).__name__}:{persistence_error}"
                ),
                call_attempt=call_attempt,
            ) from persistence_error
        if self.circuit is not None:
            self.circuit.record_success()
        return self._decode_response(
            raw_response.body_text,
            call_key=call_key,
            request_hash=request_hash,
        )

    def _call_attempt(self, *, call_key: str, request_hash: str) -> int:
        """Resolve a logical call to initial, explicitly retried, or abandoned state."""
        for attempt in (2, 1):
            intent = self.store.load(
                call_key=call_key,
                record_kind="intent",
                call_attempt=attempt,
            )
            outcome = self.store.load_matching_outcome(
                call_key=call_key,
                request_hash=request_hash,
                call_attempt=attempt,
            )
            if outcome is not None:
                if intent is None:
                    raise ValueError(f"External-call outcome has no intent: {call_key}")
                if str(intent.get("request_hash", "")) != request_hash:
                    raise ValueError(f"External-call request hash mismatch: {call_key}")
                return attempt
            if intent is None:
                continue
            if str(intent.get("request_hash", "")) != request_hash:
                raise ValueError(f"External-call request hash mismatch: {call_key}")
            abandoned = self.store.load(
                call_key=call_key,
                record_kind="abandoned_ambiguous",
                call_attempt=attempt,
            )
            if abandoned is not None:
                raise AbandonedExternalCallError(
                    call_key=call_key,
                    request_hash=request_hash,
                    call_attempt=attempt,
                )
            if attempt == 2:
                raise AmbiguousExternalCallError(
                    call_key=call_key,
                    request_hash=request_hash,
                    call_attempt=2,
                )
            resolution = self.store.load(
                call_key=call_key,
                record_kind="resolution",
                call_attempt=1,
            )
            action = str((resolution or {}).get("payload", {}).get("action", ""))
            if action == "retry":
                return 2
            if action == "abandon":
                raise AbandonedExternalCallError(
                    call_key=call_key,
                    request_hash=request_hash,
                    call_attempt=1,
                )
            raise AmbiguousExternalCallError(
                call_key=call_key,
                request_hash=request_hash,
                call_attempt=1,
            )
        return 1

    def _record_http_failure(self, status_code: int) -> None:
        """Record only milestone-defined OpenRouter infrastructure statuses."""
        if self.circuit is None:
            return
        status = int(status_code)
        if status in {401, 402}:
            self.circuit.record_failure(
                reason=f"http_{status}",
                immediate_open=True,
            )
        elif status in {408, 429} or status >= 500:
            self.circuit.record_failure(reason=f"http_{status}")

    def _resolve_outcome(
        self,
        outcome: dict[str, Any],
        *,
        call_key: str,
        request_hash: str,
    ) -> dict[str, Any]:
        payload = dict(outcome.get("payload", {}))
        if str(outcome.get("record_kind", "")) == "http_error":
            raise DefiniteOpenRouterHTTPError(
                call_key=call_key,
                request_hash=request_hash,
                status_code=int(payload["status_code"]),
                body_text=str(payload.get("body_text", "")),
            )
        return self._decode_response(
            str(payload.get("body_text", "")),
            call_key=call_key,
            request_hash=request_hash,
        )

    @staticmethod
    def _decode_response(
        body_text: str,
        *,
        call_key: str,
        request_hash: str,
    ) -> dict[str, Any]:
        try:
            payload = json.loads(body_text)
        except (TypeError, ValueError) as exc:
            raise DefiniteOpenRouterResponseError(
                call_key=call_key,
                request_hash=request_hash,
                error=exc,
            ) from exc
        if not isinstance(payload, dict):
            error = TypeError("OpenRouter response body must contain a JSON object")
            raise DefiniteOpenRouterResponseError(
                call_key=call_key,
                request_hash=request_hash,
                error=error,
            )
        return payload


def bind_route3_allocation_client(
    client: Any,
    *,
    record_root: Path,
    canonical_page_id: int,
    call_key: str,
) -> Any:
    """Bind a formal factory to one allocation and leave test clients unchanged."""
    if isinstance(client, Route3OpenRouterClientFactory):
        return client.for_allocation(
            record_root=record_root,
            canonical_page_id=canonical_page_id,
            call_key=call_key,
        )
    return client


def bind_route3_allocation_panel(
    members: list[ModelPanelMember] | None,
    *,
    record_root: Path,
    canonical_page_id: int,
) -> list[ModelPanelMember] | None:
    """Bind every formal answer-model factory to one allocation."""
    if members is None:
        return None
    return [
        ModelPanelMember(
            name=member.name,
            client=bind_route3_allocation_client(
                member.client,
                record_root=record_root,
                canonical_page_id=canonical_page_id,
                call_key="",
            ),
        )
        for member in members
    ]


@dataclass(slots=True)
class Route3DurableOpenRouterClient:
    """Expose the existing text-completion interface over the durable executor."""

    config: LLMConfig
    executor: Route3DurableOpenRouterExecutor
    call_key: str
    disable_caller_retry: bool = True

    def for_call(self, call_key: str) -> "Route3DurableOpenRouterClient":
        """Bind the same allocation executor to another stable logical call key."""
        return Route3DurableOpenRouterClient(
            config=self.config,
            executor=self.executor,
            call_key=str(call_key),
        )

    def complete_text(self, prompt: str) -> str:
        """Return assistant text for one durable logical call."""
        return str(self.complete_text_with_audit(prompt)["text"]).strip()

    def complete_text_with_audit(self, prompt: str) -> dict[str, Any]:
        """Return assistant text with the existing Route 3 audit shape."""
        request_payload = {
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        }
        body = self.executor.execute(
            call_key=self.call_key,
            request_payload=request_payload,
        )
        try:
            choice = body["choices"][0]
            text = str(choice["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            raise DefiniteOpenRouterResponseError(
                call_key=self.call_key,
                request_hash=canonical_json_sha256(request_payload),
                error=exc,
            ) from exc
        return {
            "text": text.strip(),
            "request_payload": deepcopy(request_payload),
            "response_body": body,
            "raw_text": text,
            "finish_reason": str(choice.get("finish_reason") or ""),
            "native_finish_reason": str(choice.get("native_finish_reason") or ""),
        }


@dataclass(slots=True)
class Route3OpenRouterClientFactory:
    """Create allocation-scoped durable clients over one shared transport."""

    config: LLMConfig
    transport: Any
    circuit: ServiceCircuit | None = None

    @classmethod
    def from_config(
        cls,
        config: LLMConfig,
        *,
        timeout_seconds: float,
        circuit: ServiceCircuit,
    ) -> "Route3OpenRouterClientFactory":
        """Build a factory with the formal one-request transport."""
        return cls(
            config=config,
            transport=Route3OpenRouterTransport(
                config=config,
                timeout_seconds=timeout_seconds,
            ),
            circuit=circuit,
        )

    def for_allocation(
        self,
        *,
        record_root: Path,
        canonical_page_id: int,
        call_key: str,
    ) -> Route3DurableOpenRouterClient:
        """Bind this factory to one allocation and logical call."""
        store = ExternalCallRecordStore(
            record_root,
            canonical_page_id=canonical_page_id,
        )
        return Route3DurableOpenRouterClient(
            config=self.config,
            executor=Route3DurableOpenRouterExecutor(
                store=store,
                transport=self.transport,
                circuit=self.circuit,
            ),
            call_key=call_key,
        )
