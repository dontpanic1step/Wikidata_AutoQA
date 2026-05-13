"""Search-client support for long-tail verification."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from html import unescape
from pathlib import Path
from time import perf_counter, sleep
from typing import Any
from urllib.parse import quote_plus
from urllib.error import URLError
from urllib.request import Request, urlopen

from .network import clear_proxy, install_proxy

RESULT_LINK_PATTERN = re.compile(
    r'<a[^>]*class="result__a"[^>]*href="(?P<url>[^"]+)"[^>]*>(?P<title>.*?)</a>',
    re.IGNORECASE | re.DOTALL,
)
RESULT_SNIPPET_PATTERN = re.compile(
    r'<a[^>]*class="result__a"[^>]*>.*?</a>.*?<a[^>]*class="result__snippet"[^>]*>(?P<snippet>.*?)</a>',
    re.IGNORECASE | re.DOTALL,
)
TAG_PATTERN = re.compile(r"<[^>]+>")


@dataclass(slots=True)
class SearchResult:
    """One parsed search result row."""

    title: str
    snippet: str
    url: str


@dataclass(slots=True)
class DuckDuckGoSearchClient:
    """Very small DuckDuckGo HTML search client."""

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

    def search(self, query: str, *, max_results: int = 5) -> list[SearchResult]:
        """Search DuckDuckGo HTML results and return parsed result rows."""
        url = "https://html.duckduckgo.com/html/?q=" + quote_plus(query)
        cache_path = self._cache_path(url)
        if cache_path is not None and cache_path.exists():
            started = perf_counter()
            html = cache_path.read_text(encoding="utf-8")
            self.request_events.append(
                {
                    "url": url,
                    "cache_hit": True,
                    "duration_ms": int((perf_counter() - started) * 1000),
                }
            )
            return self._parse_results(html, max_results=max_results)

        html, used_direct_fallback, duration_ms = self._fetch_html(url)
        if cache_path is not None:
            cache_path.write_text(html, encoding="utf-8")
        self.request_events.append(
            {
                "url": url,
                "cache_hit": False,
                "duration_ms": duration_ms,
                "used_direct_fallback": used_direct_fallback,
            }
        )
        return self._parse_results(html, max_results=max_results)

    def _fetch_html(self, url: str) -> tuple[str, bool, int]:
        """Fetch one DuckDuckGo HTML page, with direct fallback if the proxy path fails."""
        request = Request(
            url,
            headers={
                "Accept": "text/html",
                "User-Agent": self.user_agent,
            },
        )
        started = perf_counter()
        try:
            install_proxy(self.proxy)
            for attempt in range(3):
                try:
                    with urlopen(request, timeout=self.timeout_seconds) as response:
                        return response.read().decode("utf-8", errors="replace"), False, int((perf_counter() - started) * 1000)
                except URLError:
                    if attempt == 2:
                        raise
                    sleep(min(2 ** attempt, 4))
        except URLError:
            clear_proxy()
            for attempt in range(3):
                try:
                    with urlopen(request, timeout=self.timeout_seconds) as response:
                        return response.read().decode("utf-8", errors="replace"), True, int((perf_counter() - started) * 1000)
                except URLError:
                    if attempt == 2:
                        raise
                    sleep(min(2 ** attempt, 4))
        finally:
            if self.proxy:
                install_proxy(self.proxy)
            else:
                clear_proxy()

    def _parse_results(self, html: str, *, max_results: int) -> list[SearchResult]:
        """Parse result titles, snippets, and URLs from DuckDuckGo HTML."""
        links = list(RESULT_LINK_PATTERN.finditer(html))
        snippets = list(RESULT_SNIPPET_PATTERN.finditer(html))
        results: list[SearchResult] = []
        for index, link_match in enumerate(links[:max_results]):
            snippet_text = ""
            if index < len(snippets):
                snippet_text = _clean_html_text(snippets[index].group("snippet"))
            results.append(
                SearchResult(
                    title=_clean_html_text(link_match.group("title")),
                    snippet=snippet_text,
                    url=unescape(link_match.group("url")),
                )
            )
        return results

    def _cache_path(self, url: str) -> Path | None:
        """Return the cache path for one search request."""
        if self.cache_dir is None:
            return None
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
        return self.cache_dir / f"search_{digest}.html"


def _clean_html_text(text: str) -> str:
    """Strip HTML tags and entities from one snippet fragment."""
    return unescape(TAG_PATTERN.sub("", text)).strip()
