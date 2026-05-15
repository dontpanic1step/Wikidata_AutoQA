"""Minimal Wikidata access client for the Stage 1 vertical slice."""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter, sleep
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen, Request

from .network import install_proxy


@dataclass(slots=True)
class WikidataClient:
    """Small client for WDQS and Wikibase API calls."""

    user_agent: str
    proxy: str | None = None
    timeout_seconds: float = 30.0
    max_retries: int = 3
    max_entity_ids_per_request: int = 50
    maxlag_seconds: int = 5
    min_retry_after_seconds: float = 5.0
    log_checkpoints: bool = False
    cache_dir: Path | None = None
    request_events: list[dict[str, Any]] = field(init=False, default_factory=list)
    request_counters: dict[str, int] = field(init=False, default_factory=dict)
    problem_reports: list[dict[str, Any]] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        install_proxy(self.proxy)
        if self.cache_dir is not None:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.request_events: list[dict[str, Any]] = []
        self.request_counters: dict[str, int] = {
            "total_requests": 0,
            "network_requests": 0,
            "cache_hits": 0,
            "retry_count": 0,
            "errors": 0,
        }
        self.problem_reports: list[dict[str, Any]] = []

    def sparql_query(self, query: str) -> list[dict[str, Any]]:
        """Execute a SPARQL query and return binding rows."""
        self._log_checkpoint(
            "wdqs_query_start",
            "Starting WDQS query.",
            query_preview=" ".join(query.split())[:240],
        )
        url = "https://query.wikidata.org/sparql?" + urlencode(
            {"query": query, "format": "json"}
        )
        payload = self._request_json(url, accept="application/sparql-results+json")
        bindings = payload.get("results", {}).get("bindings")
        if bindings is None:
            raise RuntimeError(f"WDQS response missing results.bindings keys: {sorted(payload.keys())}")
        self._log_checkpoint(
            "wdqs_query_done",
            "Completed WDQS query.",
            row_count=len(bindings),
        )
        return bindings

    def get_entities(self, ids: list[str]) -> dict[str, Any]:
        """Hydrate Wikidata entities by QID."""
        merged_entities: dict[str, Any] = {}
        total_chunks = max(1, (len(ids) + self.max_entity_ids_per_request - 1) // self.max_entity_ids_per_request)
        for chunk_start in range(0, len(ids), self.max_entity_ids_per_request):
            chunk = ids[chunk_start : chunk_start + self.max_entity_ids_per_request]
            chunk_number = (chunk_start // self.max_entity_ids_per_request) + 1
            self._log_checkpoint(
                "wbgetentities_chunk_start",
                "Starting wbgetentities chunk.",
                chunk_number=chunk_number,
                total_chunks=total_chunks,
                chunk_size=len(chunk),
                first_id=chunk[0] if chunk else "",
                last_id=chunk[-1] if chunk else "",
            )
            params = {
                "action": "wbgetentities",
                "ids": "|".join(chunk),
                "props": "labels|aliases|descriptions|claims|sitelinks",
                "languages": "en",
                "format": "json",
                "maxlag": str(self.maxlag_seconds),
            }
            url = "https://www.wikidata.org/w/api.php?" + urlencode(params)
            payload = self._request_json(url)
            entities = payload.get("entities")
            if entities is None:
                raise RuntimeError(f"wbgetentities response missing entities key: {sorted(payload.keys())}")
            merged_entities.update(entities)
            self._log_checkpoint(
                "wbgetentities_chunk_done",
                "Completed wbgetentities chunk.",
                chunk_number=chunk_number,
                total_chunks=total_chunks,
                entity_count=len(entities),
            )
        return merged_entities

    def search_entities(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Search for possible label competitors."""
        query = query.strip()
        if not query:
            self.record_problem(
                "wbsearchentities_blank_query",
                "Skipped wbsearchentities lookup because the search query was blank.",
                limit=limit,
            )
            return []
        self._log_checkpoint(
            "wbsearchentities_start",
            "Starting wbsearchentities lookup.",
            query=query,
            limit=limit,
        )
        params = {
            "action": "wbsearchentities",
            "search": query,
            "language": "en",
            "type": "item",
            "limit": str(limit),
            "format": "json",
            "maxlag": str(self.maxlag_seconds),
        }
        url = "https://www.wikidata.org/w/api.php?" + urlencode(params)
        payload = self._request_json(url)
        search = payload.get("search")
        if search is None:
            raise RuntimeError(f"wbsearchentities response missing search key: {sorted(payload.keys())}")
        self._log_checkpoint(
            "wbsearchentities_done",
            "Completed wbsearchentities lookup.",
            query=query,
            result_count=len(search),
        )
        return search

    def load_text_mapping(self, namespace: str, key: str) -> dict[str, Any] | None:
        """Load one cached text-to-entity mapping payload."""
        cache_path = self._mapping_cache_path(namespace, key)
        if cache_path is None or not cache_path.exists():
            return None
        return json.loads(cache_path.read_text(encoding="utf-8"))

    def store_text_mapping(self, namespace: str, key: str, payload: dict[str, Any]) -> None:
        """Store one cached text-to-entity mapping payload."""
        cache_path = self._mapping_cache_path(namespace, key)
        if cache_path is None:
            return
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def _request_json(self, url: str, accept: str = "application/json") -> dict[str, Any]:
        """Perform a JSON GET request with a Wikidata-friendly User-Agent."""
        self.request_counters["total_requests"] += 1
        cache_path = self._cache_path(url, accept)
        if cache_path is not None and cache_path.exists():
            started = perf_counter()
            payload = json.loads(cache_path.read_text(encoding="utf-8"))
            if "error" in payload:
                cache_path.unlink(missing_ok=True)
            else:
                duration_ms = int((perf_counter() - started) * 1000)
                self.request_counters["cache_hits"] += 1
                self.request_events.append(
                    {
                        "url": url,
                        "accept": accept,
                        "cache_hit": True,
                        "attempts": 0,
                        "duration_ms": duration_ms,
                        "status": "ok",
                    }
                )
                return payload

        last_error: Exception | None = None
        started = perf_counter()
        for attempt in range(self.max_retries):
            request = Request(
                url,
                headers={
                    "Accept": accept,
                    "User-Agent": self.user_agent,
                },
            )
            try:
                self.request_counters["network_requests"] += 1
                with urlopen(request, timeout=self.timeout_seconds) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                if "error" in payload:
                    error_message = self._api_error_message(payload)
                    last_error = RuntimeError(error_message)
                    retryable = self._api_error_is_retryable(payload)
                    if retryable and attempt < self.max_retries - 1:
                        self.request_counters["retry_count"] += 1
                        self._sleep_before_retry(
                            url=url,
                            attempt=attempt + 1,
                            reason=f"api_{self._api_error_code(payload)}",
                            delay_seconds=self._api_error_retry_delay_seconds(payload, attempt),
                        )
                        continue
                    self.request_counters["errors"] += 1
                    self.request_events.append(
                        {
                            "url": url,
                            "accept": accept,
                            "cache_hit": False,
                            "attempts": attempt + 1,
                            "duration_ms": int((perf_counter() - started) * 1000),
                            "status": "error",
                            "error_type": "WikidataAPIError",
                            "error_message": error_message,
                        }
                    )
                    raise last_error
                if cache_path is not None and "error" not in payload:
                    cache_path.write_text(json.dumps(payload), encoding="utf-8")
                self.request_events.append(
                    {
                        "url": url,
                        "accept": accept,
                        "cache_hit": False,
                        "attempts": attempt + 1,
                        "duration_ms": int((perf_counter() - started) * 1000),
                        "status": "ok",
                    }
                )
                return payload
            except HTTPError as exc:
                last_error = exc
                if attempt < self.max_retries - 1:
                    self.request_counters["retry_count"] += 1
                if exc.code not in {429, 500, 502, 503, 504} or attempt == self.max_retries - 1:
                    self.request_counters["errors"] += 1
                    self.request_events.append(
                        {
                            "url": url,
                            "accept": accept,
                            "cache_hit": False,
                            "attempts": attempt + 1,
                            "duration_ms": int((perf_counter() - started) * 1000),
                            "status": "error",
                            "error_type": type(exc).__name__,
                            "error_message": str(exc),
                        }
                    )
                    raise
                self._sleep_before_retry(
                    url=url,
                    attempt=attempt + 1,
                    reason=f"http_{exc.code}",
                    delay_seconds=self._retry_delay_seconds(exc, attempt),
                    response_headers=exc.headers,
                )
            except URLError as exc:
                last_error = exc
                if attempt < self.max_retries - 1:
                    self.request_counters["retry_count"] += 1
                if attempt == self.max_retries - 1:
                    self.request_counters["errors"] += 1
                    self.request_events.append(
                        {
                            "url": url,
                            "accept": accept,
                            "cache_hit": False,
                            "attempts": attempt + 1,
                            "duration_ms": int((perf_counter() - started) * 1000),
                            "status": "error",
                            "error_type": type(exc).__name__,
                            "error_message": str(exc),
                        }
                    )
                    raise
                self._sleep_before_retry(
                    url=url,
                    attempt=attempt + 1,
                    reason="url_error",
                    delay_seconds=min(2 ** attempt, 4),
                )
        if last_error is not None:
            raise last_error
        raise RuntimeError("Wikidata request failed without an explicit error")

    def stats_snapshot(self) -> dict[str, Any]:
        """Return a structured snapshot of request counters and recent events."""
        return {
            **self.request_counters,
            "events": self.request_events.copy(),
            "problems": self.problem_reports.copy(),
        }

    def record_problem(
        self,
        kind: str,
        message: str,
        **context: Any,
    ) -> None:
        """Store a structured harvesting or query problem for later review."""
        self.problem_reports.append(
            {
                "kind": kind,
                "message": message,
                "context": context,
            }
        )

    def _cache_path(self, url: str, accept: str) -> Path | None:
        """Return the on-disk cache path for one request."""
        if self.cache_dir is None:
            return None
        digest = hashlib.sha256(f"{accept}\n{url}".encode("utf-8")).hexdigest()
        return self.cache_dir / f"{digest}.json"

    def _mapping_cache_path(self, namespace: str, key: str) -> Path | None:
        """Return the cache path for one text-to-entity mapping lookup."""
        if self.cache_dir is None:
            return None
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.cache_dir / "text_mappings" / namespace / f"{digest}.json"

    def _retry_delay_seconds(self, exc: HTTPError, attempt: int) -> float:
        """Resolve retry delay from Retry-After headers or conservative fallback."""
        retry_after_header = ""
        if exc.headers is not None:
            retry_after_header = str(exc.headers.get("Retry-After", "")).strip()
        if retry_after_header.isdigit():
            return max(float(retry_after_header), self.min_retry_after_seconds)
        if exc.code == 429:
            return self.min_retry_after_seconds
        return min(2 ** attempt, 4)

    def _api_error_code(self, payload: dict[str, Any]) -> str:
        """Return a normalized Wikidata API error code."""
        error = payload.get("error", {})
        if not isinstance(error, dict):
            return "unknown"
        return str(error.get("code", "unknown")).strip() or "unknown"

    def _api_error_message(self, payload: dict[str, Any]) -> str:
        """Render a concise message for HTTP-200 Wikidata API errors."""
        error = payload.get("error", {})
        if not isinstance(error, dict):
            return "Wikidata API error: malformed error payload"
        code = self._api_error_code(payload)
        info = str(error.get("info", "")).strip()
        if info:
            return f"Wikidata API error: {code}: {info}"
        return f"Wikidata API error: {code}"

    def _api_error_is_retryable(self, payload: dict[str, Any]) -> bool:
        """Decide whether a JSON-level API error should be retried."""
        code = self._api_error_code(payload).casefold()
        return code in {
            "maxlag",
            "readonly",
            "internal_api_error",
            "ratelimited",
            "timeout",
        }

    def _api_error_retry_delay_seconds(self, payload: dict[str, Any], attempt: int) -> float:
        """Resolve retry delay from Wikidata API error payloads."""
        error = payload.get("error", {})
        retry_after = ""
        if isinstance(error, dict):
            retry_after = str(error.get("retry-after", "") or error.get("retry_after", "")).strip()
        try:
            return max(float(retry_after), self.min_retry_after_seconds)
        except ValueError:
            pass
        if self._api_error_code(payload).casefold() == "maxlag":
            return self.min_retry_after_seconds
        return min(2 ** attempt, 4)

    def _sleep_before_retry(
        self,
        *,
        url: str,
        attempt: int,
        reason: str,
        delay_seconds: float,
        response_headers: Any | None = None,
    ) -> None:
        """Sleep before a retry and surface the wait in logs and telemetry."""
        rounded_delay = max(float(delay_seconds), 0.0)
        warning = (
            f"[wikidata] Sleeping {rounded_delay:.1f}s before retry "
            f"(attempt {attempt}, reason={reason}) for {url}"
        )
        print(warning, file=sys.stderr, flush=True)
        self.record_problem(
            "rate_limit_sleep",
            warning,
            url=url,
            attempt=attempt,
            reason=reason,
            sleep_seconds=rounded_delay,
            retry_after=(str(response_headers.get("Retry-After", "")).strip() if response_headers else ""),
        )
        self.request_events.append(
            {
                "url": url,
                "cache_hit": False,
                "attempts": attempt,
                "status": "sleeping_before_retry",
                "reason": reason,
                "sleep_seconds": rounded_delay,
            }
        )
        sleep(rounded_delay)

    def _log_checkpoint(self, kind: str, message: str, **context: Any) -> None:
        """Emit a visible checkpoint log and store it in request events when enabled."""
        if not self.log_checkpoints:
            return
        detail_parts = [f"{key}={value}" for key, value in context.items() if value not in {None, ""}]
        rendered = f"[wikidata] {message}"
        if detail_parts:
            rendered += " " + ", ".join(detail_parts)
        print(rendered, file=sys.stderr, flush=True)
        self.request_events.append(
            {
                "status": "checkpoint",
                "kind": kind,
                "message": message,
                "context": context,
            }
        )
