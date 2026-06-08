"""Lightweight MediaWiki client for summary-style evidence retrieval."""

from __future__ import annotations

import hashlib
import json
import random
import ssl
from http.client import RemoteDisconnected
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock
from time import perf_counter, sleep
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, unquote, urlencode, urlparse
from urllib.request import Request, urlopen

from .network import clear_proxy, install_proxy

WIKIPEDIA_REQUEST_ATTEMPTS_PER_PATH = 2
WIKIPEDIA_RETRY_INITIAL_SLEEP_SECONDS = 0.5
WIKIPEDIA_RETRY_MAX_SLEEP_SECONDS = 4.0
WIKIPEDIA_RETRY_JITTER_SECONDS = 0.25


@dataclass(slots=True)
class WikipediaSearchHit:
    """One MediaWiki search result row."""

    page_id: int
    title: str
    snippet: str
    query: str
    offset: int


@dataclass(slots=True)
class WikipediaClient:
    """Small client for English Wikipedia summary retrieval."""

    user_agent: str
    proxy: str | None = None
    timeout_seconds: float = 30.0
    cache_dir: Path | None = None
    rate_limit_backoff_seconds: float = 0.0
    rate_limit_max_backoff_seconds: float = 0.0
    rate_limit_recovery_seconds: float = 120.0
    request_events: list[dict[str, Any]] = field(init=False, default_factory=list)
    _rate_limit_lock: Lock = field(init=False, repr=False)
    _rate_limit_resume_at: float = field(init=False, default=0.0, repr=False)
    _rate_limit_current_sleep: float = field(init=False, default=0.0, repr=False)
    _rate_limit_last_429_at: float = field(init=False, default=0.0, repr=False)

    def __post_init__(self) -> None:
        install_proxy(self.proxy)
        if self.cache_dir is not None:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.request_events = []
        self._rate_limit_lock = Lock()
        self.rate_limit_backoff_seconds = max(0.0, float(self.rate_limit_backoff_seconds or 0.0))
        self.rate_limit_max_backoff_seconds = max(0.0, float(self.rate_limit_max_backoff_seconds or 0.0))
        self.rate_limit_recovery_seconds = max(0.0, float(self.rate_limit_recovery_seconds or 0.0))

    def fetch_summary(self, title: str) -> dict[str, Any]:
        """Return the MediaWiki REST page summary payload for one title."""
        normalized_title = title.strip().replace(" ", "_")
        if not normalized_title:
            return {}
        url = (
            "https://en.wikipedia.org/api/rest_v1/page/summary/"
            + quote(normalized_title, safe=":_()")
        )
        try:
            return self._fetch_json(url)
        except HTTPError as exc:
            if exc.code == 404:
                return {}
            raise

    def fetch_parse(self, title_or_url: str) -> dict[str, Any]:
        """Return cached MediaWiki action=parse payload for one English Wikipedia page."""
        title = normalize_wikipedia_title(title_or_url)
        page_id = normalize_wikipedia_page_id(title_or_url)
        if not title and page_id is None:
            return {}
        url = build_parse_api_url(title if title else title_or_url)
        return self._fetch_json(url)

    def fetch_pageviews(self, title: str, *, start: str, end: str) -> dict[str, Any]:
        """Return uncached Wikimedia pageview payload for one English Wikipedia page."""
        normalized_title = title.strip().replace(" ", "_")
        if not normalized_title:
            return {}
        url = build_pageviews_api_url(normalized_title, start=start, end=end)
        started = perf_counter()
        try:
            payload, used_direct_fallback, attempts = self._request_json_with_retry(url)
        except Exception as exc:
            self.request_events.append(
                {
                    "url": url,
                    "cache_hit": False,
                    "duration_ms": int((perf_counter() - started) * 1000),
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "request_type": "pageviews",
                }
            )
            raise
        self.request_events.append(
            {
                "url": url,
                "cache_hit": False,
                "duration_ms": int((perf_counter() - started) * 1000),
                "attempts": attempts,
                "used_direct_fallback": used_direct_fallback,
                "request_type": "pageviews",
            }
        )
        return payload

    def search_page_ids(
        self,
        search_query: str,
        *,
        namespace: int = 0,
        limit: int = 50,
        offset: int = 0,
    ) -> list[WikipediaSearchHit]:
        """Search English Wikipedia and return namespace-bounded page IDs."""
        query = search_query.strip()
        if not query:
            return []
        bounded_limit = max(1, min(50, int(limit)))
        bounded_offset = max(0, int(offset))
        url = build_search_api_url(
            query,
            namespace=namespace,
            limit=bounded_limit,
            offset=bounded_offset,
        )
        payload = self._fetch_json(url)
        rows = payload.get("query", {}).get("search", []) if isinstance(payload, dict) else []
        hits: list[WikipediaSearchHit] = []
        for row in rows:
            try:
                page_id = int(row.get("pageid", 0))
            except (TypeError, ValueError):
                continue
            if page_id <= 0:
                continue
            hits.append(
                WikipediaSearchHit(
                    page_id=page_id,
                    title=str(row.get("title") or ""),
                    snippet=str(row.get("snippet") or ""),
                    query=query,
                    offset=bounded_offset,
                )
            )
        return hits

    def _fetch_json(self, url: str) -> dict[str, Any]:
        """Fetch one JSON URL with cache, retry, and direct fallback."""
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
        try:
            payload, used_direct_fallback, attempts = self._request_json_with_retry(url)
        except Exception as exc:
            self.request_events.append(
                {
                    "url": url,
                    "cache_hit": False,
                    "duration_ms": int((perf_counter() - started) * 1000),
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                }
            )
            raise
        if cache_path is not None:
            cache_path.write_text(json.dumps(payload), encoding="utf-8")
        self.request_events.append(
            {
                "url": url,
                "cache_hit": False,
                "duration_ms": int((perf_counter() - started) * 1000),
                "attempts": attempts,
                "used_direct_fallback": used_direct_fallback,
            }
        )
        return payload

    def _request_json_with_retry(self, url: str) -> tuple[dict[str, Any], bool, int]:
        """Request JSON with retries for transient TLS/socket failures."""
        attempts = 0
        last_error: Exception | None = None
        use_proxy_options = [bool(self.proxy)]
        if self.proxy:
            use_proxy_options.append(False)
        try:
            for use_proxy in use_proxy_options:
                if use_proxy:
                    install_proxy(self.proxy)
                else:
                    clear_proxy()
                for attempt in range(WIKIPEDIA_REQUEST_ATTEMPTS_PER_PATH):
                    attempts += 1
                    waited_seconds = self._wait_for_rate_limit()
                    request = Request(
                        url,
                        headers={
                            "Accept": "application/json",
                            "Accept-Encoding": "identity",
                            "Connection": "close",
                            "User-Agent": self.user_agent,
                        },
                    )
                    try:
                        with urlopen(request, timeout=self.timeout_seconds) as response:
                            self._record_rate_limit_success()
                            if waited_seconds > 0:
                                self.request_events.append(
                                    {
                                        "url": url,
                                        "cache_hit": False,
                                        "rate_limit_wait_seconds": round(waited_seconds, 4),
                                        "event": "wikipedia_429_shared_wait",
                                    }
                                )
                            return (
                                json.loads(response.read().decode("utf-8")),
                                not use_proxy and bool(self.proxy),
                                attempts,
                            )
                    except HTTPError as exc:
                        last_error = exc
                        if exc.code == 429:
                            self._record_rate_limit_429(exc)
                        if 400 <= exc.code < 500 and exc.code != 429:
                            raise
                        if attempt == WIKIPEDIA_REQUEST_ATTEMPTS_PER_PATH - 1:
                            break
                        _sleep_before_retry(attempt)
                    except (URLError, OSError, TimeoutError, RemoteDisconnected, ssl.SSLError) as exc:
                        last_error = exc
                        if attempt == WIKIPEDIA_REQUEST_ATTEMPTS_PER_PATH - 1:
                            break
                        _sleep_before_retry(attempt)
        finally:
            if self.proxy:
                install_proxy(self.proxy)
            else:
                clear_proxy()
        if last_error is not None:
            raise last_error
        raise RuntimeError("Wikipedia JSON request failed without an explicit error")

    def _cache_path(self, url: str) -> Path | None:
        """Return the cache path for one Wikipedia request."""
        if self.cache_dir is None:
            return None
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
        return self.cache_dir / f"wikipedia_{digest}.json"

    def _wait_for_rate_limit(self) -> float:
        """Block until the shared Wikipedia 429 backoff window has passed."""
        waited = 0.0
        while True:
            with self._rate_limit_lock:
                delay = self._rate_limit_resume_at - perf_counter()
            if delay <= 0:
                return waited
            sleep(delay)
            waited += delay

    def _record_rate_limit_429(self, exc: HTTPError) -> None:
        """Extend the shared Wikipedia 429 backoff window."""
        retry_after_delay = self._rate_limit_retry_after_seconds(exc)
        if self.rate_limit_backoff_seconds <= 0 and retry_after_delay <= 0:
            return
        now = perf_counter()
        with self._rate_limit_lock:
            if (
                self._rate_limit_current_sleep > 0
                and self.rate_limit_recovery_seconds > 0
                and now - self._rate_limit_last_429_at > self.rate_limit_recovery_seconds
            ):
                self._rate_limit_current_sleep = 0.0
            if self._rate_limit_current_sleep <= 0:
                synthetic_sleep = self.rate_limit_backoff_seconds
            else:
                synthetic_sleep = max(self.rate_limit_backoff_seconds, self._rate_limit_current_sleep * 2)
            if self.rate_limit_max_backoff_seconds > 0:
                synthetic_sleep = min(synthetic_sleep, self.rate_limit_max_backoff_seconds)
            sleep_seconds = max(synthetic_sleep, retry_after_delay)
            self._rate_limit_current_sleep = sleep_seconds
            self._rate_limit_last_429_at = now
            self._rate_limit_resume_at = max(self._rate_limit_resume_at, now + sleep_seconds)

    def _record_rate_limit_success(self) -> None:
        """Reset the shared 429 backoff after a quiet recovery window."""
        if self.rate_limit_recovery_seconds <= 0:
            return
        now = perf_counter()
        with self._rate_limit_lock:
            if self._rate_limit_last_429_at and now - self._rate_limit_last_429_at >= self.rate_limit_recovery_seconds:
                self._rate_limit_current_sleep = 0.0

    def _rate_limit_retry_after_seconds(self, exc: HTTPError) -> float:
        """Return the polite shared wait after a Wikipedia 429."""
        retry_after = ""
        try:
            retry_after = str(exc.headers.get("Retry-After", "")).strip()
        except AttributeError:
            retry_after = ""
        if retry_after.isdigit():
            return max(float(retry_after), self.rate_limit_backoff_seconds)
        return self.rate_limit_backoff_seconds


def _sleep_before_retry(attempt: int) -> None:
    """Sleep briefly before retrying a transient Wikipedia API failure."""
    base_delay = min(
        WIKIPEDIA_RETRY_INITIAL_SLEEP_SECONDS * (2 ** attempt),
        WIKIPEDIA_RETRY_MAX_SLEEP_SECONDS,
    )
    sleep(base_delay + random.uniform(0.0, WIKIPEDIA_RETRY_JITTER_SECONDS))


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


def normalize_wikipedia_page_id(title_or_url: str) -> int | None:
    """Return a MediaWiki page ID from a curid or pageid URL."""
    value = title_or_url.strip()
    if not value:
        return None
    parsed = urlparse(value)
    if not (parsed.scheme and parsed.netloc):
        return None
    host = parsed.netloc.lower()
    if host not in {"en.wikipedia.org", "www.en.wikipedia.org"}:
        return None
    query = parse_qs(parsed.query)
    for key in ("curid", "pageid"):
        values = query.get(key, [])
        if not values:
            continue
        try:
            page_id = int(values[0])
        except ValueError:
            return None
        return page_id if page_id > 0 else None
    return None


def build_parse_api_url(title_or_url: str) -> str:
    """Build the MediaWiki action=parse API URL for one title or page URL."""
    title = normalize_wikipedia_title(title_or_url)
    page_id = normalize_wikipedia_page_id(title_or_url)
    query_args: dict[str, str | int] = {
        "action": "parse",
        "prop": "text|displaytitle",
        "format": "json",
        "formatversion": "2",
        "redirects": "1",
    }
    if page_id is not None:
        query_args["pageid"] = page_id
    else:
        query_args["page"] = title
    query = urlencode(
        query_args
    )
    return f"https://en.wikipedia.org/w/api.php?{query}"


def build_search_api_url(
    search_query: str,
    *,
    namespace: int = 0,
    limit: int = 50,
    offset: int = 0,
) -> str:
    """Build a MediaWiki API URL for namespace-scoped search."""
    query = urlencode(
        {
            "action": "query",
            "list": "search",
            "srnamespace": int(namespace),
            "srlimit": max(1, min(50, int(limit))),
            "sroffset": max(0, int(offset)),
            "srsearch": search_query,
            "format": "json",
            "formatversion": "2",
        }
    )
    return f"https://en.wikipedia.org/w/api.php?{query}"


def build_pageviews_api_url(title: str, *, start: str, end: str) -> str:
    """Build a Wikimedia monthly pageviews URL for one article title."""
    normalized_title = title.strip().replace(" ", "_")
    quoted_title = quote(normalized_title, safe=":_()")
    return (
        "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
        f"en.wikipedia/all-access/user/{quoted_title}/monthly/{start}/{end}"
    )
