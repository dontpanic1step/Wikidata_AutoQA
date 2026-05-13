"""Minimal Wikidata access client for the Stage 1 vertical slice."""

from __future__ import annotations

import hashlib
import json
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
        url = "https://query.wikidata.org/sparql?" + urlencode(
            {"query": query, "format": "json"}
        )
        payload = self._request_json(url, accept="application/sparql-results+json")
        bindings = payload.get("results", {}).get("bindings")
        if bindings is None:
            raise RuntimeError(f"WDQS response missing results.bindings keys: {sorted(payload.keys())}")
        return bindings

    def get_entities(self, ids: list[str]) -> dict[str, Any]:
        """Hydrate Wikidata entities by QID."""
        merged_entities: dict[str, Any] = {}
        for chunk_start in range(0, len(ids), self.max_entity_ids_per_request):
            chunk = ids[chunk_start : chunk_start + self.max_entity_ids_per_request]
            params = {
                "action": "wbgetentities",
                "ids": "|".join(chunk),
                "props": "labels|aliases|descriptions|claims|sitelinks",
                "languages": "en",
                "format": "json",
            }
            url = "https://www.wikidata.org/w/api.php?" + urlencode(params)
            payload = self._request_json(url)
            entities = payload.get("entities")
            if entities is None:
                raise RuntimeError(f"wbgetentities response missing entities key: {sorted(payload.keys())}")
            merged_entities.update(entities)
        return merged_entities

    def search_entities(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Search for possible label competitors."""
        params = {
            "action": "wbsearchentities",
            "search": query,
            "language": "en",
            "type": "item",
            "limit": str(limit),
            "format": "json",
        }
        url = "https://www.wikidata.org/w/api.php?" + urlencode(params)
        payload = self._request_json(url)
        search = payload.get("search")
        if search is None:
            raise RuntimeError(f"wbsearchentities response missing search key: {sorted(payload.keys())}")
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
            sleep(min(2 ** attempt, 4))
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
