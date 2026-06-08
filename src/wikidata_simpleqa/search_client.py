"""Search-client support for long-tail verification."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from html import unescape
from http.client import RemoteDisconnected
from pathlib import Path
from time import perf_counter, sleep
from typing import Any
from urllib.parse import quote_plus
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .network import clear_proxy, install_proxy

RESULT_LINK_PATTERN = re.compile(
    r"<a\b"
    r"(?=[^>]*\bclass\s*=\s*(?P<class_quote>['\"])[^'\"]*(?:result__a|result-link)[^'\"]*(?P=class_quote))"
    r"(?=[^>]*\bhref\s*=\s*(?P<href_quote>['\"])(?P<url>[^'\"]+)(?P=href_quote))"
    r"[^>]*>(?P<title>.*?)</a>",
    re.IGNORECASE | re.DOTALL,
)
RESULT_SNIPPET_PATTERN = re.compile(
    r"<(?:a|td|div|span)\b"
    r"(?=[^>]*\bclass\s*=\s*(?P<class_quote>['\"])[^'\"]*(?:result__snippet|result-snippet)[^'\"]*(?P=class_quote))"
    r"[^>]*>(?P<snippet>.*?)</(?:a|td|div|span)>",
    re.IGNORECASE | re.DOTALL,
)
TAG_PATTERN = re.compile(r"<[^>]+>")
NETWORK_ERRORS = (HTTPError, URLError, TimeoutError, OSError, RemoteDisconnected)
DUCKDUCKGO_HTML_SEARCH_URL = "https://html.duckduckgo.com/html/?q="
DUCKDUCKGO_LITE_SEARCH_URL = "https://lite.duckduckgo.com/lite/?q="
DUCKDUCKGO_LITE_MAX_ATTEMPTS = 2
DUCKDUCKGO_HTML_FALLBACK_HTTP_STATUSES = {202, 403, 429, 500, 502, 503, 504}
DUCKDUCKGO_LITE_RETRYABLE_HTTP_STATUSES = {202, 429, 500, 502, 503, 504}


@dataclass(slots=True)
class SearchResult:
    """One parsed search result row."""

    title: str
    snippet: str
    url: str


class DuckDuckGoSearchError(RuntimeError):
    """Search request failure with attempt-level diagnostics."""

    def __init__(
        self,
        message: str,
        *,
        url: str,
        duration_ms: int,
        attempt_events: list[dict[str, Any]],
        original_error: BaseException,
    ) -> None:
        super().__init__(message)
        self.url = url
        self.duration_ms = duration_ms
        self.attempt_events = attempt_events
        self.original_error = original_error


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
        encoded_query = quote_plus(query)
        url = DUCKDUCKGO_HTML_SEARCH_URL + encoded_query
        lite_url = DUCKDUCKGO_LITE_SEARCH_URL + encoded_query
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

        try:
            html, used_direct_fallback, used_lite_fallback, duration_ms, attempt_events = self._fetch_html(
                url,
                lite_url,
            )
        except DuckDuckGoSearchError as exc:
            self.request_events.append(
                {
                    "url": url,
                    "cache_hit": False,
                    "duration_ms": exc.duration_ms,
                    "failed": True,
                    "error_type": type(exc.original_error).__name__,
                    "error_message": str(exc.original_error),
                    "attempts": exc.attempt_events,
                }
            )
            raise
        if cache_path is not None:
            cache_path.write_text(html, encoding="utf-8")
        self.request_events.append(
            {
                "url": url,
                "cache_hit": False,
                "duration_ms": duration_ms,
                "used_direct_fallback": used_direct_fallback,
                "used_lite_fallback": used_lite_fallback,
                "failed": False,
                "attempts": attempt_events,
            }
        )
        return self._parse_results(html, max_results=max_results)

    def _fetch_html(
        self,
        url: str,
        lite_url: str,
    ) -> tuple[str, bool, bool, int, list[dict[str, Any]]]:
        """Fetch one DuckDuckGo page, switching to Lite immediately on HTML 202."""
        started = perf_counter()
        attempt_events: list[dict[str, Any]] = []
        last_error: BaseException | None = None
        try:
            install_proxy(self.proxy)
            html = self._fetch_from_network_path(
                url,
                lite_url,
                path="configured_proxy" if self.proxy else "direct",
                proxy=self.proxy,
                started=started,
                attempt_events=attempt_events,
                start_with_lite=False,
            )
            return (
                html,
                False,
                _used_lite_endpoint(attempt_events),
                int((perf_counter() - started) * 1000),
                attempt_events,
            )
        except NETWORK_ERRORS as exc:
            last_error = exc
            if not self.proxy:
                raise DuckDuckGoSearchError(
                    f"DuckDuckGo search request failed after {len(attempt_events)} attempts: {exc}",
                    url=url,
                    duration_ms=int((perf_counter() - started) * 1000),
                    attempt_events=attempt_events,
                    original_error=exc,
                ) from exc
            clear_proxy()
            try:
                html = self._fetch_from_network_path(
                    url,
                    lite_url,
                    path="direct_fallback",
                    proxy=None,
                    started=started,
                    attempt_events=attempt_events,
                    start_with_lite=_html_status_202_seen(attempt_events),
                )
                return (
                    html,
                    True,
                    _used_lite_endpoint(attempt_events),
                    int((perf_counter() - started) * 1000),
                    attempt_events,
                )
            except NETWORK_ERRORS as fallback_exc:
                last_error = fallback_exc
                raise DuckDuckGoSearchError(
                    f"DuckDuckGo search request failed after {len(attempt_events)} attempts: {fallback_exc}",
                    url=url,
                    duration_ms=int((perf_counter() - started) * 1000),
                    attempt_events=attempt_events,
                    original_error=fallback_exc,
                ) from fallback_exc
        finally:
            if self.proxy:
                install_proxy(self.proxy)
            else:
                clear_proxy()
        if last_error is not None:
            raise DuckDuckGoSearchError(
                f"DuckDuckGo search request failed after {len(attempt_events)} attempts: {last_error}",
                url=url,
                duration_ms=int((perf_counter() - started) * 1000),
                attempt_events=attempt_events,
                original_error=last_error,
            ) from last_error
        raise DuckDuckGoSearchError(
            "DuckDuckGo search request failed without an explicit error",
            url=url,
            duration_ms=int((perf_counter() - started) * 1000),
            attempt_events=attempt_events,
            original_error=RuntimeError("unknown search error"),
        )

    def _fetch_from_network_path(
        self,
        url: str,
        lite_url: str,
        *,
        path: str,
        proxy: str | None,
        started: float,
        attempt_events: list[dict[str, Any]],
        start_with_lite: bool,
    ) -> str:
        """Fetch through one proxy/direct path, with endpoint fallback when needed."""
        if not start_with_lite:
            html = self._fetch_html_endpoint_once(
                url,
                lite_url,
                path=path,
                proxy=proxy,
                attempt_events=attempt_events,
            )
            if html is not None:
                return html
        return self._fetch_lite_endpoint_with_bounded_retry(
            lite_url,
            path=path,
            proxy=proxy,
            started=started,
            attempt_events=attempt_events,
        )

    def _fetch_html_endpoint_once(
        self,
        url: str,
        lite_url: str,
        *,
        path: str,
        proxy: str | None,
        attempt_events: list[dict[str, Any]],
    ) -> str | None:
        """Fetch HTML once; return None when the caller should switch to Lite."""
        attempt_started = perf_counter()
        request = Request(
            url,
            headers={
                "Accept": "text/html",
                "User-Agent": self.user_agent,
            },
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                status = getattr(response, "status", None)
                fallback_reason = _html_endpoint_fallback_reason_for_status(status)
                if fallback_reason is not None:
                    attempt_events.append(
                        _endpoint_switch_event(
                            attempt=1,
                            path=path,
                            proxy=proxy,
                            timeout_seconds=self.timeout_seconds,
                            started=attempt_started,
                            url=url,
                            endpoint="html",
                            status=status,
                            fallback_reason=fallback_reason,
                        )
                    )
                    return None
                if status is not None and int(status) >= 400:
                    raise HTTPError(url, int(status), "HTTP error", hdrs=None, fp=None)
                html = response.read().decode("utf-8", errors="replace")
                attempt_events.append(
                    _attempt_event(
                        attempt=1,
                        path=path,
                        proxy=proxy,
                        timeout_seconds=self.timeout_seconds,
                        started=attempt_started,
                        url=url,
                        endpoint="html",
                        status=status,
                    )
                )
                return html
        except NETWORK_ERRORS as exc:
            fallback_reason = _html_endpoint_fallback_reason_for_error(exc, proxy=proxy)
            if fallback_reason is not None:
                attempt_events.append(
                    _endpoint_switch_event(
                        attempt=1,
                        path=path,
                        proxy=proxy,
                        timeout_seconds=self.timeout_seconds,
                        started=attempt_started,
                        url=url,
                        endpoint="html",
                        error=exc,
                        fallback_reason=fallback_reason,
                    )
                )
                return None
            attempt_events.append(
                _attempt_event(
                    attempt=1,
                    path=path,
                    proxy=proxy,
                    timeout_seconds=self.timeout_seconds,
                    started=attempt_started,
                    url=url,
                    endpoint="html",
                    error=exc,
                )
            )
            raise

    def _fetch_lite_endpoint_with_bounded_retry(
        self,
        lite_url: str,
        *,
        path: str,
        proxy: str | None,
        started: float,
        attempt_events: list[dict[str, Any]],
    ) -> str:
        """Fetch Lite with only bounded retries for transient DDG conditions."""
        last_status_error: HTTPError | None = None
        for attempt in range(1, DUCKDUCKGO_LITE_MAX_ATTEMPTS + 1):
            request = Request(
                lite_url,
                headers={
                    "Accept": "text/html",
                    "User-Agent": self.user_agent,
                },
            )
            attempt_started = perf_counter()
            try:
                with urlopen(request, timeout=self.timeout_seconds) as response:
                    status = getattr(response, "status", None)
                    if _is_lite_retryable_status(status):
                        attempt_events.append(
                            _retryable_status_event(
                                attempt=attempt,
                                path=path,
                                proxy=proxy,
                                timeout_seconds=self.timeout_seconds,
                                started=attempt_started,
                                url=lite_url,
                                endpoint="lite",
                                status=status,
                            )
                        )
                        if attempt == DUCKDUCKGO_LITE_MAX_ATTEMPTS:
                            last_status_error = HTTPError(lite_url, int(status), "Retryable HTTP status", hdrs=None, fp=None)
                            break
                        sleep(_duckduckgo_retry_sleep_seconds(attempt))
                        continue
                    if status is not None and int(status) >= 400:
                        raise HTTPError(lite_url, int(status), "HTTP error", hdrs=None, fp=None)
                    html = response.read().decode("utf-8", errors="replace")
                    attempt_events.append(
                        _attempt_event(
                            attempt=attempt,
                            path=path,
                            proxy=proxy,
                            timeout_seconds=self.timeout_seconds,
                            started=attempt_started,
                            url=lite_url,
                            endpoint="lite",
                            status=status,
                        )
                    )
                    return html
            except NETWORK_ERRORS as exc:
                retry_reason = _lite_retry_reason_for_error(exc)
                if retry_reason is not None:
                    attempt_events.append(
                        _retryable_error_event(
                            attempt=attempt,
                            path=path,
                            proxy=proxy,
                            timeout_seconds=self.timeout_seconds,
                            started=attempt_started,
                            url=lite_url,
                            endpoint="lite",
                            error=exc,
                            retry_reason=retry_reason,
                        )
                    )
                    if attempt == DUCKDUCKGO_LITE_MAX_ATTEMPTS:
                        raise
                    sleep(_duckduckgo_retry_sleep_seconds(attempt))
                    continue
                attempt_events.append(
                    _attempt_event(
                        attempt=attempt,
                        path=path,
                        proxy=proxy,
                        timeout_seconds=self.timeout_seconds,
                        started=attempt_started,
                        url=lite_url,
                        endpoint="lite",
                        error=exc,
                    )
                )
                raise
        if last_status_error is not None:
            raise last_status_error
        raise DuckDuckGoSearchError(
            "DuckDuckGo search request failed without an explicit error",
            url=lite_url,
            duration_ms=int((perf_counter() - started) * 1000),
            attempt_events=attempt_events,
            original_error=RuntimeError("unknown search error"),
        )

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


def _attempt_event(
    *,
    attempt: int,
    path: str,
    proxy: str | None,
    timeout_seconds: float,
    started: float,
    url: str | None = None,
    endpoint: str | None = None,
    status: int | None = None,
    error: BaseException | None = None,
) -> dict[str, Any]:
    """Return one HTTP attempt diagnostic payload."""
    event: dict[str, Any] = {
        "attempt": attempt,
        "path": path,
        "proxy_configured": bool(proxy),
        "timeout_seconds": timeout_seconds,
        "duration_ms": int((perf_counter() - started) * 1000),
        "ok": error is None,
    }
    if url is not None:
        event["url"] = url
    if endpoint is not None:
        event["endpoint"] = endpoint
    if status is not None:
        event["status"] = status
    if error is not None:
        event["error_type"] = type(error).__name__
        event["error_message"] = str(error)
        if isinstance(error, HTTPError):
            event["http_status"] = error.code
    return event


def _endpoint_switch_event(
    *,
    attempt: int,
    path: str,
    proxy: str | None,
    timeout_seconds: float,
    started: float,
    url: str,
    endpoint: str,
    status: int | None = None,
    error: BaseException | None = None,
    fallback_reason: str = "html_status_202",
) -> dict[str, Any]:
    """Return one diagnostic payload for an HTML-to-Lite endpoint switch."""
    event = _attempt_event(
        attempt=attempt,
        path=path,
        proxy=proxy,
        timeout_seconds=timeout_seconds,
        started=started,
        url=url,
        endpoint=endpoint,
        status=status,
        error=error,
    )
    event["ok"] = False
    event["fallback_reason"] = fallback_reason
    event["switched_to_endpoint"] = "lite"
    return event


def _retryable_status_event(
    *,
    attempt: int,
    path: str,
    proxy: str | None,
    timeout_seconds: float,
    started: float,
    url: str,
    endpoint: str,
    status: int,
) -> dict[str, Any]:
    """Return one diagnostic payload for a retryable HTTP status."""
    event = _attempt_event(
        attempt=attempt,
        path=path,
        proxy=proxy,
        timeout_seconds=timeout_seconds,
        started=started,
        url=url,
        endpoint=endpoint,
        status=status,
    )
    event["ok"] = False
    event["retry_reason"] = f"{endpoint}_status_{status}"
    return event


def _retryable_error_event(
    *,
    attempt: int,
    path: str,
    proxy: str | None,
    timeout_seconds: float,
    started: float,
    url: str,
    endpoint: str,
    error: BaseException,
    retry_reason: str,
) -> dict[str, Any]:
    """Return one diagnostic payload for a retryable transport failure."""
    event = _attempt_event(
        attempt=attempt,
        path=path,
        proxy=proxy,
        timeout_seconds=timeout_seconds,
        started=started,
        url=url,
        endpoint=endpoint,
        error=error,
    )
    event["ok"] = False
    event["retry_reason"] = retry_reason
    return event


def _html_endpoint_fallback_reason_for_status(status: int | None) -> str | None:
    """Return why an HTML response should switch to Lite instead of retrying HTML."""
    if status is None:
        return None
    normalized_status = int(status)
    if normalized_status in DUCKDUCKGO_HTML_FALLBACK_HTTP_STATUSES:
        return f"html_status_{normalized_status}"
    return None


def _html_endpoint_fallback_reason_for_error(error: BaseException, *, proxy: str | None) -> str | None:
    """Return why an HTML exception should switch to Lite on this network path."""
    if isinstance(error, HTTPError):
        return _html_endpoint_fallback_reason_for_status(error.code)
    if proxy:
        return None
    if isinstance(error, NETWORK_ERRORS):
        return "html_transport_error"
    return None


def _is_lite_retryable_status(status: int | None) -> bool:
    """Return whether a Lite response status deserves a small bounded retry."""
    return status is not None and int(status) in DUCKDUCKGO_LITE_RETRYABLE_HTTP_STATUSES


def _lite_retry_reason_for_error(error: BaseException) -> str | None:
    """Return the bounded retry reason for a Lite endpoint exception."""
    if isinstance(error, HTTPError):
        if int(error.code) in DUCKDUCKGO_LITE_RETRYABLE_HTTP_STATUSES:
            return f"lite_status_{int(error.code)}"
        return None
    if isinstance(error, NETWORK_ERRORS):
        return "lite_transport_error"
    return None


def _duckduckgo_retry_sleep_seconds(attempt: int) -> int:
    """Return bounded polite backoff between retryable Lite attempts."""
    return min(2 ** (attempt - 1), 4)


def _html_status_202_seen(attempt_events: list[dict[str, Any]]) -> bool:
    """Return whether the request already saw HTML status 202."""
    return any(
        event.get("endpoint") == "html"
        and (event.get("status") == 202 or event.get("http_status") == 202)
        for event in attempt_events
    )


def _used_lite_endpoint(attempt_events: list[dict[str, Any]]) -> bool:
    """Return whether any attempt used or switched to the Lite endpoint."""
    return any(
        event.get("endpoint") == "lite" or event.get("switched_to_endpoint") == "lite"
        for event in attempt_events
    )
