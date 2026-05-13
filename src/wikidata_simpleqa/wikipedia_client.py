"""Lightweight MediaWiki client for summary-style evidence retrieval."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter
from typing import Any
from urllib.parse import quote
from urllib.request import Request, urlopen

from .network import install_proxy


@dataclass(slots=True)
class WikipediaClient:
    """Small client for English Wikipedia summary retrieval."""

    user_agent: str
    proxy: str | None = None
    timeout_seconds: float = 30.0
    cache_dir: Path | None = None
    request_events: list[dict[str, Any]] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        install_proxy(self.proxy)
        if self.cache_dir is not None:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.request_events = []

    def fetch_summary(self, title: str) -> dict[str, Any]:
        """Return the MediaWiki REST page summary payload for one title."""
        normalized_title = title.strip().replace(" ", "_")
        if not normalized_title:
            return {}
        url = (
            "https://en.wikipedia.org/api/rest_v1/page/summary/"
            + quote(normalized_title, safe=":_()")
        )
        cache_path = self._cache_path(url)
        if cache_path is not None and cache_path.exists():
            started = perf_counter()
            payload = json.loads(cache_path.read_text(encoding="utf-8"))
            self.request_events.append(
                {
                    "url": url,
                    "cache_hit": True,
                    "duration_ms": int((perf_counter() - started) * 1000),
                }
            )
            return payload

        started = perf_counter()
        request = Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": self.user_agent,
            },
        )
        with urlopen(request, timeout=self.timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if cache_path is not None:
            cache_path.write_text(json.dumps(payload), encoding="utf-8")
        self.request_events.append(
            {
                "url": url,
                "cache_hit": False,
                "duration_ms": int((perf_counter() - started) * 1000),
            }
        )
        return payload

    def _cache_path(self, url: str) -> Path | None:
        """Return the cache path for one Wikipedia request."""
        if self.cache_dir is None:
            return None
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
        return self.cache_dir / f"wikipedia_{digest}.json"
