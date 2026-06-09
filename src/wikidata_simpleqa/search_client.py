"""Search-client support for long-tail verification."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from html import unescape
from http.client import RemoteDisconnected
from pathlib import Path
from threading import Lock
from time import perf_counter, sleep
from typing import Any, ClassVar
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
DUCKDUCKGO_DDGS_MAX_ATTEMPTS = 2
DUCKDUCKGO_LITE_MAX_ATTEMPTS = 2
DUCKDUCKGO_HTML_FALLBACK_HTTP_STATUSES = {202, 403, 429, 500, 502, 503, 504}
DUCKDUCKGO_LITE_RETRYABLE_HTTP_STATUSES = {202, 429, 500, 502, 503, 504}
DUCKDUCKGO_COOLDOWN_HTTP_STATUSES = {202, 403}
DUCKDUCKGO_COOLDOWN_FAILURE_THRESHOLD = 3
DUCKDUCKGO_COOLDOWN_INITIAL_SECONDS = 60.0
DUCKDUCKGO_COOLDOWN_MAX_SECONDS = 300.0
DUCKDUCKGO_FALLBACK_ALIASES = {
    "ddgs": {"ddgs"},
    "legacy": {"legacy", "html", "html_lite", "html-lite", "html+lite"},
    "html": {"legacy", "html", "html_lite", "html-lite", "html+lite"},
    "lite": {"lite", "html_to_lite", "html-to-lite", "html_lite", "html-lite", "html+lite"},
    "direct": {"direct", "direct_fallback", "direct-fallback"},
    "direct_fallback": {"direct", "direct_fallback", "direct-fallback"},
}


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

    _global_cooldown_lock: ClassVar[Lock] = Lock()
    _global_cooldown_resume_at: ClassVar[float] = 0.0
    _global_cooldown_consecutive_failures: ClassVar[int] = 0
    _global_cooldown_last_sleep_seconds: ClassVar[float] = 0.0

    user_agent: str
    proxy: str | None = None
    timeout_seconds: float = 30.0
    cache_dir: Path | None = None
    prefer_ddgs: bool = True
    ddgs_backend: str = "auto"
    ddgs_max_attempts: int = DUCKDUCKGO_DDGS_MAX_ATTEMPTS
    disable_fallbacks: str | tuple[str, ...] | list[str] | set[str] | None = None
    cooldown_enabled: bool = True
    cooldown_failure_threshold: int = DUCKDUCKGO_COOLDOWN_FAILURE_THRESHOLD
    cooldown_initial_seconds: float = DUCKDUCKGO_COOLDOWN_INITIAL_SECONDS
    cooldown_max_seconds: float = DUCKDUCKGO_COOLDOWN_MAX_SECONDS
    _disabled_fallbacks: frozenset[str] = field(init=False, default_factory=frozenset)
    request_events: list[dict[str, Any]] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        self._install_initial_proxy_if_available()
        if self.cache_dir is not None:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._disabled_fallbacks = _normalize_disabled_fallbacks(self.disable_fallbacks)
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

        request_started = perf_counter()
        ddgs_attempt_events: list[dict[str, Any]] = []
        if self.prefer_ddgs and not self._fallback_disabled("ddgs"):
            try:
                results, ddgs_duration_ms, ddgs_attempt_events = self._search_with_ddgs(
                    query,
                    max_results=max_results,
                )
            except DuckDuckGoSearchError as ddgs_exc:
                ddgs_attempt_events = ddgs_exc.attempt_events
                if self._fallback_disabled("legacy"):
                    duration_ms = int((perf_counter() - request_started) * 1000)
                    self._record_global_cooldown_failure_if_needed(ddgs_attempt_events)
                    self.request_events.append(
                        {
                            "url": url,
                            "query": query,
                            "cache_hit": False,
                            "duration_ms": duration_ms,
                            "failed": True,
                            "backend": "ddgs",
                            "used_ddgs": True,
                            "legacy_fallback_disabled": True,
                            "error_type": type(ddgs_exc.original_error).__name__,
                            "error_message": str(ddgs_exc.original_error),
                            "attempts": ddgs_attempt_events,
                        }
                    )
                    raise DuckDuckGoSearchError(
                        f"DuckDuckGo ddgs request failed after {len(ddgs_attempt_events)} attempts: "
                        f"{ddgs_exc.original_error}",
                        url=url,
                        duration_ms=duration_ms,
                        attempt_events=ddgs_attempt_events,
                        original_error=ddgs_exc.original_error,
                    ) from ddgs_exc
            else:
                if not self._record_global_cooldown_failure_if_needed(ddgs_attempt_events):
                    self._record_global_cooldown_success()
                self.request_events.append(
                    {
                        "url": url,
                        "query": query,
                        "cache_hit": False,
                        "duration_ms": ddgs_duration_ms,
                        "used_ddgs": True,
                        "used_legacy_fallback": False,
                        "used_direct_fallback": False,
                        "used_lite_fallback": False,
                        "failed": False,
                        "backend": "ddgs",
                        "attempts": ddgs_attempt_events,
                    }
                )
                return results

        try:
            html, used_direct_fallback, used_lite_fallback, duration_ms, attempt_events = self._fetch_html(
                url,
                lite_url,
            )
        except DuckDuckGoSearchError as exc:
            combined_attempts = ddgs_attempt_events + exc.attempt_events
            duration_ms = int((perf_counter() - request_started) * 1000)
            self._record_global_cooldown_failure_if_needed(combined_attempts)
            self.request_events.append(
                {
                    "url": url,
                    "query": query,
                    "cache_hit": False,
                    "duration_ms": duration_ms,
                    "failed": True,
                    "backend": "legacy",
                    "used_ddgs": bool(ddgs_attempt_events),
                    "used_legacy_fallback": bool(ddgs_attempt_events),
                    "error_type": type(exc.original_error).__name__,
                    "error_message": str(exc.original_error),
                    "attempts": combined_attempts,
                }
            )
            raise DuckDuckGoSearchError(
                f"DuckDuckGo search request failed after {len(combined_attempts)} attempts: {exc.original_error}",
                url=url,
                duration_ms=duration_ms,
                attempt_events=combined_attempts,
                original_error=exc.original_error,
            ) from exc
        if cache_path is not None:
            cache_path.write_text(html, encoding="utf-8")
        combined_attempts = ddgs_attempt_events + attempt_events
        if not self._record_global_cooldown_failure_if_needed(combined_attempts):
            self._record_global_cooldown_success()
        self.request_events.append(
            {
                "url": url,
                "query": query,
                "cache_hit": False,
                "duration_ms": int((perf_counter() - request_started) * 1000),
                "used_ddgs": bool(ddgs_attempt_events),
                "used_legacy_fallback": bool(ddgs_attempt_events),
                "used_direct_fallback": used_direct_fallback,
                "used_lite_fallback": used_lite_fallback,
                "failed": False,
                "backend": "legacy",
                "attempts": combined_attempts,
            }
        )
        return self._parse_results(html, max_results=max_results)

    def _search_with_ddgs(
        self,
        query: str,
        *,
        max_results: int,
    ) -> tuple[list[SearchResult], int, list[dict[str, Any]]]:
        """Search through the optional ddgs package before falling back to HTML/Lite."""
        started = perf_counter()
        attempt_events: list[dict[str, Any]] = []
        self._wait_for_global_cooldown(attempt_events)
        try:
            from ddgs import DDGS  # type: ignore[import-not-found]
        except Exception as exc:  # noqa: BLE001
            attempt_started = perf_counter()
            attempt_events.append(
                _attempt_event(
                    attempt=1,
                    path="ddgs",
                    proxy=self.proxy,
                    timeout_seconds=self.timeout_seconds,
                    started=attempt_started,
                    endpoint="ddgs",
                    error=exc,
                )
            )
            raise DuckDuckGoSearchError(
                f"ddgs import failed: {exc}",
                url="ddgs",
                duration_ms=int((perf_counter() - started) * 1000),
                attempt_events=attempt_events,
                original_error=exc,
            ) from exc

        last_error: BaseException | None = None
        max_attempts = max(1, int(self.ddgs_max_attempts))
        for attempt in range(1, max_attempts + 1):
            if attempt > 1:
                sleep(_duckduckgo_retry_sleep_seconds(attempt - 1))
            attempt_started = perf_counter()
            try:
                ddgs_kwargs: dict[str, Any] = {"timeout": max(1, int(round(self.timeout_seconds)))}
                if self.proxy:
                    ddgs_kwargs["proxy"] = self.proxy
                with DDGS(**ddgs_kwargs) as ddgs:
                    rows = ddgs.text(query, max_results=max_results, backend=self.ddgs_backend)
                results = _search_results_from_ddgs_rows(rows, max_results=max_results)
                attempt_events.append(
                    _attempt_event(
                        attempt=attempt,
                        path="ddgs",
                        proxy=self.proxy,
                        timeout_seconds=self.timeout_seconds,
                        started=attempt_started,
                        endpoint="ddgs",
                        status=200,
                    )
                )
                attempt_events[-1]["result_count"] = len(results)
                return results, int((perf_counter() - started) * 1000), attempt_events
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                attempt_events.append(
                    _attempt_event(
                        attempt=attempt,
                        path="ddgs",
                        proxy=self.proxy,
                        timeout_seconds=self.timeout_seconds,
                        started=attempt_started,
                        endpoint="ddgs",
                        error=exc,
                    )
                )
                attempt_events[-1]["retry_reason"] = _ddgs_retry_reason_for_error(exc)
                attempt_events[-1]["ok"] = False
                if attempt == max_attempts:
                    break
        assert last_error is not None
        raise DuckDuckGoSearchError(
            f"ddgs request failed after {max_attempts} attempts: {last_error}",
            url="ddgs",
            duration_ms=int((perf_counter() - started) * 1000),
            attempt_events=attempt_events,
            original_error=last_error,
        ) from last_error

    def _fetch_html(
        self,
        url: str,
        lite_url: str,
    ) -> tuple[str, bool, bool, int, list[dict[str, Any]]]:
        """Fetch one DuckDuckGo page, switching to Lite immediately on HTML 202."""
        started = perf_counter()
        attempt_events: list[dict[str, Any]] = []
        last_error: BaseException | None = None
        self._wait_for_global_cooldown(attempt_events)
        try:
            self._install_proxy_for_legacy_path(started=started, attempt_events=attempt_events)
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
            if not self.proxy or self._fallback_disabled("direct_fallback"):
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
                self._install_initial_proxy_if_available()
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
        if self._fallback_disabled("lite"):
            raise URLError("DuckDuckGo Lite fallback disabled")
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

    def _fallback_disabled(self, fallback_name: str) -> bool:
        """Return whether one fallback family has been disabled for debugging."""
        aliases = DUCKDUCKGO_FALLBACK_ALIASES.get(fallback_name, {fallback_name})
        return bool(self._disabled_fallbacks.intersection(aliases))

    def _install_initial_proxy_if_available(self) -> None:
        """Install urllib proxy state when the optional SOCKS dependency is present."""
        try:
            install_proxy(self.proxy)
        except RuntimeError:
            if not self.proxy:
                raise
            clear_proxy()

    def _install_proxy_for_legacy_path(self, *, started: float, attempt_events: list[dict[str, Any]]) -> None:
        """Install urllib proxy state and record missing proxy support as a path failure."""
        try:
            install_proxy(self.proxy)
        except RuntimeError as exc:
            if not self.proxy:
                raise
            attempt_events.append(
                _attempt_event(
                    attempt=1,
                    path="configured_proxy",
                    proxy=self.proxy,
                    timeout_seconds=self.timeout_seconds,
                    started=started,
                    endpoint="proxy_setup",
                    error=exc,
                )
            )
            raise URLError(str(exc)) from exc

    def _wait_for_global_cooldown(self, attempt_events: list[dict[str, Any]]) -> None:
        """Sleep when another DDG request recently triggered the shared cooldown."""
        if not self.cooldown_enabled:
            return
        with self._global_cooldown_lock:
            resume_at = self._global_cooldown_resume_at
        remaining_seconds = resume_at - perf_counter()
        if remaining_seconds <= 0:
            return
        sleep_seconds = min(remaining_seconds, max(0.0, float(self.cooldown_max_seconds)))
        cooldown_started = perf_counter()
        attempt_events.append(
            {
                "endpoint": "global_cooldown",
                "path": "global_cooldown",
                "ok": True,
                "cooldown_sleep_seconds": round(sleep_seconds, 3),
                "duration_ms": 0,
            }
        )
        sleep(sleep_seconds)
        attempt_events[-1]["duration_ms"] = int((perf_counter() - cooldown_started) * 1000)

    def _record_global_cooldown_failure_if_needed(self, attempt_events: list[dict[str, Any]]) -> bool:
        """Trigger shared cooldown after repeated DDG throttling or transport failures."""
        if not self.cooldown_enabled or not _is_cooldown_worthy_failure(attempt_events):
            return False
        threshold = max(1, int(self.cooldown_failure_threshold))
        initial_seconds = max(0.0, float(self.cooldown_initial_seconds))
        max_seconds = max(initial_seconds, float(self.cooldown_max_seconds))
        with self._global_cooldown_lock:
            type(self)._global_cooldown_consecutive_failures += 1
            consecutive_failures = type(self)._global_cooldown_consecutive_failures
            if consecutive_failures < threshold:
                return True
            previous_sleep = type(self)._global_cooldown_last_sleep_seconds
            sleep_seconds = initial_seconds if previous_sleep <= 0 else min(previous_sleep * 2, max_seconds)
            type(self)._global_cooldown_last_sleep_seconds = sleep_seconds
            type(self)._global_cooldown_resume_at = max(
                type(self)._global_cooldown_resume_at,
                perf_counter() + sleep_seconds,
            )
        attempt_events.append(
            {
                "endpoint": "global_cooldown",
                "path": "global_cooldown",
                "ok": False,
                "cooldown_triggered": True,
                "cooldown_sleep_seconds": round(sleep_seconds, 3),
                "cooldown_consecutive_failures": consecutive_failures,
                "duration_ms": 0,
            }
        )
        return True

    def _record_global_cooldown_success(self) -> None:
        """Reset the shared DDG cooldown failure streak after a successful request."""
        if not self.cooldown_enabled:
            return
        with self._global_cooldown_lock:
            type(self)._global_cooldown_resume_at = 0.0
            type(self)._global_cooldown_consecutive_failures = 0
            type(self)._global_cooldown_last_sleep_seconds = 0.0

    @classmethod
    def reset_global_cooldown(cls) -> None:
        """Clear shared cooldown state; useful for isolated probes and tests."""
        with cls._global_cooldown_lock:
            cls._global_cooldown_resume_at = 0.0
            cls._global_cooldown_consecutive_failures = 0
            cls._global_cooldown_last_sleep_seconds = 0.0


def _clean_html_text(text: str) -> str:
    """Strip HTML tags and entities from one snippet fragment."""
    return unescape(TAG_PATTERN.sub("", text)).strip()


def _normalize_disabled_fallbacks(
    disable_fallbacks: str | tuple[str, ...] | list[str] | set[str] | None,
) -> frozenset[str]:
    """Normalize fallback-disable debug flags."""
    if disable_fallbacks is None:
        return frozenset()
    if isinstance(disable_fallbacks, str):
        raw_items = re.split(r"[,;\s]+", disable_fallbacks)
    else:
        raw_items = []
        for item in disable_fallbacks:
            raw_items.extend(re.split(r"[,;\s]+", str(item)))
    return frozenset(item.strip().lower() for item in raw_items if item.strip())


def _search_results_from_ddgs_rows(rows: list[dict[str, Any]], *, max_results: int) -> list[SearchResult]:
    """Convert ddgs result dictionaries into the repository search-result shape."""
    results: list[SearchResult] = []
    for row in rows[:max_results]:
        title = str(row.get("title") or "").strip()
        url = str(row.get("href") or row.get("url") or "").strip()
        snippet = str(row.get("body") or row.get("snippet") or row.get("content") or "").strip()
        if not title and not url and not snippet:
            continue
        results.append(SearchResult(title=title, snippet=snippet, url=url))
    return results


def _ddgs_retry_reason_for_error(error: BaseException) -> str:
    """Return a stable retry reason for a ddgs exception."""
    if isinstance(error, HTTPError):
        return f"ddgs_status_{int(error.code)}"
    message = str(error).lower()
    if "no results found" in message:
        return "ddgs_no_results"
    for status in sorted(DUCKDUCKGO_COOLDOWN_HTTP_STATUSES):
        if f"{status}" in message:
            return f"ddgs_status_{status}"
    return "ddgs_transport_error"


def _is_cooldown_worthy_failure(attempt_events: list[dict[str, Any]]) -> bool:
    """Return whether failed attempts look like DDG throttling or transport failure."""
    if not attempt_events:
        return False
    failed_attempts = [event for event in attempt_events if event.get("ok") is False]
    if not failed_attempts:
        return False
    for event in failed_attempts:
        status = event.get("status", event.get("http_status"))
        if status is not None and int(status) in DUCKDUCKGO_COOLDOWN_HTTP_STATUSES:
            return True
        retry_reason = str(event.get("retry_reason") or event.get("fallback_reason") or "").lower()
        if any(f"status_{status}" in retry_reason for status in DUCKDUCKGO_COOLDOWN_HTTP_STATUSES):
            return True
        if retry_reason == "ddgs_no_results":
            continue
        error_type = str(event.get("error_type") or "")
        if error_type in {"HTTPError"}:
            continue
        if retry_reason.endswith("transport_error") or "transport" in retry_reason:
            return True
        if error_type in {"URLError", "TimeoutError", "OSError", "RemoteDisconnected"}:
            return True
    return False


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
