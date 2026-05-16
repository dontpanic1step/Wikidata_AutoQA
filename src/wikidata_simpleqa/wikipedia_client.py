"""Lightweight MediaWiki client for summary-style evidence retrieval."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter
from typing import Any
from urllib.parse import parse_qs, quote, unquote, urlencode, urlparse
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

    def fetch_parse(self, title_or_url: str) -> dict[str, Any]:
        """Return cached MediaWiki action=parse payload for one English Wikipedia page."""
        title = normalize_wikipedia_title(title_or_url)
        if not title:
            return {}
        url = build_parse_api_url(title)
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


def normalize_wikipedia_title(title_or_url: str) -> str:
    """Return a MediaWiki page title from an English Wikipedia URL or raw title."""
    value = title_or_url.strip()
    if not value:
        return ""
    parsed = urlparse(value)
    if parsed.scheme and parsed.netloc:
        host = parsed.netloc.lower()
        if host not in {"en.wikipedia.org", "www.en.wikipedia.org"}:
            return ""
        if parsed.path.startswith("/wiki/"):
            title = parsed.path[len("/wiki/") :]
            return unquote(title).replace("_", " ").strip()
        if parsed.path.endswith("/w/index.php"):
            title_values = parse_qs(parsed.query).get("title", [])
            if title_values:
                return title_values[0].replace("_", " ").strip()
            return ""
        return ""
    return unquote(value).replace("_", " ").strip()


def build_parse_api_url(title_or_url: str) -> str:
    """Build the MediaWiki action=parse API URL for one title or page URL."""
    title = normalize_wikipedia_title(title_or_url)
    query = urlencode(
        {
            "action": "parse",
            "page": title,
            "prop": "text|displaytitle|sections|properties",
            "format": "json",
            "formatversion": "2",
            "redirects": "1",
        }
    )
    return f"https://en.wikipedia.org/w/api.php?{query}"
