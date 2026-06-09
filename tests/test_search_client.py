"""Tests for search-client diagnostics."""

from __future__ import annotations

import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.search_client import (
    DUCKDUCKGO_HTML_SEARCH_URL,
    DUCKDUCKGO_LITE_SEARCH_URL,
    DuckDuckGoSearchError,
    DuckDuckGoSearchClient,
    SearchResult,
)


class FakeSearchResponse:
    def __init__(self, *, status: int, html: str) -> None:
        self.status = status
        self._html = html

    def __enter__(self) -> "FakeSearchResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self._html.encode("utf-8")


class DuckDuckGoSearchClientTests(unittest.TestCase):
    def tearDown(self) -> None:
        DuckDuckGoSearchClient.reset_global_cooldown()

    def test_parses_lite_result_link_rows(self) -> None:
        client = DuckDuckGoSearchClient(
            user_agent="test-agent",
            proxy=None,
            timeout_seconds=1.0,
            cache_dir=None,
            prefer_ddgs=False,
        )
        html = """
        <html>
          <a rel="nofollow" href="https://example.com/a" class='result-link'>Example <b>Title</b></a>
          <td class='result-snippet'>Example &amp; snippet</td>
        </html>
        """

        results = client._parse_results(html, max_results=5)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Example Title")
        self.assertEqual(results[0].snippet, "Example & snippet")
        self.assertEqual(results[0].url, "https://example.com/a")

    def test_html_status_202_switches_to_lite_without_retrying_html(self) -> None:
        client = DuckDuckGoSearchClient(
            user_agent="test-agent",
            proxy=None,
            timeout_seconds=1.0,
            cache_dir=None,
            prefer_ddgs=False,
        )
        lite_html = """
        <html>
          <a class="result-link" href="https://example.com/lite">Lite Result</a>
          <td class="result-snippet">Lite snippet</td>
        </html>
        """

        with patch(
            "wikidata_simpleqa.search_client.urlopen",
            side_effect=[
                FakeSearchResponse(status=202, html=""),
                FakeSearchResponse(status=200, html=lite_html),
            ],
        ) as mocked_urlopen, patch("wikidata_simpleqa.search_client.sleep", return_value=None):
            results = client.search("example query")

        called_urls = [call.args[0].full_url for call in mocked_urlopen.call_args_list]
        self.assertEqual(
            called_urls,
            [
                DUCKDUCKGO_HTML_SEARCH_URL + quote_plus("example query"),
                DUCKDUCKGO_LITE_SEARCH_URL + quote_plus("example query"),
            ],
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Lite Result")
        self.assertEqual(results[0].snippet, "Lite snippet")
        self.assertEqual(client.request_events[-1]["used_lite_fallback"], True)
        self.assertEqual(
            [attempt["endpoint"] for attempt in client.request_events[-1]["attempts"]],
            ["html", "lite"],
        )
        self.assertEqual(client.request_events[-1]["attempts"][0]["status"], 202)
        self.assertEqual(client.request_events[-1]["attempts"][0]["switched_to_endpoint"], "lite")

    def test_html_http_error_202_switches_to_lite_without_retrying_html(self) -> None:
        client = DuckDuckGoSearchClient(
            user_agent="test-agent",
            proxy=None,
            timeout_seconds=1.0,
            cache_dir=None,
            prefer_ddgs=False,
        )
        lite_html = """
        <html>
          <a class="result-link" href="https://example.com/lite">Lite Result</a>
        </html>
        """

        with patch(
            "wikidata_simpleqa.search_client.urlopen",
            side_effect=[
                HTTPError(
                    DUCKDUCKGO_HTML_SEARCH_URL + quote_plus("example query"),
                    202,
                    "Accepted",
                    hdrs=None,
                    fp=None,
                ),
                FakeSearchResponse(status=200, html=lite_html),
            ],
        ) as mocked_urlopen, patch("wikidata_simpleqa.search_client.sleep", return_value=None):
            results = client.search("example query")

        called_urls = [call.args[0].full_url for call in mocked_urlopen.call_args_list]
        self.assertEqual(called_urls[0], DUCKDUCKGO_HTML_SEARCH_URL + quote_plus("example query"))
        self.assertEqual(called_urls[1], DUCKDUCKGO_LITE_SEARCH_URL + quote_plus("example query"))
        self.assertEqual(len(results), 1)
        self.assertEqual(client.request_events[-1]["attempts"][0]["http_status"], 202)

    def test_lite_status_202_retries_lite_once_before_returning_results(self) -> None:
        client = DuckDuckGoSearchClient(
            user_agent="test-agent",
            proxy=None,
            timeout_seconds=1.0,
            cache_dir=None,
            prefer_ddgs=False,
        )
        lite_html = """
        <html>
          <a class="result-link" href="https://example.com/lite">Lite Result</a>
        </html>
        """

        with patch(
            "wikidata_simpleqa.search_client.urlopen",
            side_effect=[
                FakeSearchResponse(status=202, html=""),
                FakeSearchResponse(status=202, html=""),
                FakeSearchResponse(status=200, html=lite_html),
            ],
        ) as mocked_urlopen, patch("wikidata_simpleqa.search_client.sleep", return_value=None):
            results = client.search("example query")

        called_urls = [call.args[0].full_url for call in mocked_urlopen.call_args_list]
        self.assertEqual(
            called_urls,
            [
                DUCKDUCKGO_HTML_SEARCH_URL + quote_plus("example query"),
                DUCKDUCKGO_LITE_SEARCH_URL + quote_plus("example query"),
                DUCKDUCKGO_LITE_SEARCH_URL + quote_plus("example query"),
            ],
        )
        attempts = client.request_events[-1]["attempts"]
        self.assertEqual([attempt["endpoint"] for attempt in attempts], ["html", "lite", "lite"])
        self.assertEqual([attempt["status"] for attempt in attempts], [202, 202, 200])
        self.assertEqual(attempts[1]["retry_reason"], "lite_status_202")
        self.assertFalse(attempts[1]["ok"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Lite Result")

    def test_failed_no_proxy_search_records_only_meaningful_attempts(self) -> None:
        client = DuckDuckGoSearchClient(
            user_agent="test-agent",
            proxy=None,
            timeout_seconds=1.0,
            cache_dir=None,
            prefer_ddgs=False,
        )

        with patch("wikidata_simpleqa.search_client.urlopen", side_effect=URLError("timed out")), patch(
            "wikidata_simpleqa.search_client.sleep",
            return_value=None,
        ):
            with self.assertRaises(DuckDuckGoSearchError):
                client.search("example query")

        self.assertEqual(len(client.request_events), 1)
        event = client.request_events[0]
        self.assertTrue(event["failed"])
        self.assertEqual(event["error_type"], "URLError")
        self.assertEqual(len(event["attempts"]), 3)
        self.assertEqual([attempt["path"] for attempt in event["attempts"]], ["direct", "direct", "direct"])
        self.assertEqual([attempt["endpoint"] for attempt in event["attempts"]], ["html", "lite", "lite"])
        self.assertEqual(event["attempts"][0]["fallback_reason"], "html_transport_error")
        self.assertEqual(event["attempts"][0]["switched_to_endpoint"], "lite")
        self.assertEqual(event["attempts"][1]["retry_reason"], "lite_transport_error")
        self.assertEqual(event["attempts"][2]["retry_reason"], "lite_transport_error")
        self.assertTrue(all(not attempt["ok"] for attempt in event["attempts"]))

    def test_proxy_path_failure_falls_back_to_direct_once(self) -> None:
        html = """
        <html>
          <a class="result__a" href="https://example.com/direct">Direct Result</a>
        </html>
        """
        with patch("wikidata_simpleqa.search_client.install_proxy"), patch(
            "wikidata_simpleqa.search_client.clear_proxy"
        ), patch(
            "wikidata_simpleqa.search_client.urlopen",
            side_effect=[
                URLError("proxy unavailable"),
                FakeSearchResponse(status=200, html=html),
            ],
        ) as mocked_urlopen:
            client = DuckDuckGoSearchClient(
                user_agent="test-agent",
                proxy="socks5://127.0.0.1:9999",
                timeout_seconds=1.0,
                cache_dir=None,
                prefer_ddgs=False,
            )
            results = client.search("example query")

        called_urls = [call.args[0].full_url for call in mocked_urlopen.call_args_list]
        self.assertEqual(
            called_urls,
            [
                DUCKDUCKGO_HTML_SEARCH_URL + quote_plus("example query"),
                DUCKDUCKGO_HTML_SEARCH_URL + quote_plus("example query"),
            ],
        )
        event = client.request_events[-1]
        self.assertFalse(event["failed"])
        self.assertTrue(event["used_direct_fallback"])
        self.assertFalse(event["used_lite_fallback"])
        self.assertEqual([attempt["path"] for attempt in event["attempts"]], ["configured_proxy", "direct_fallback"])
        self.assertEqual([attempt["endpoint"] for attempt in event["attempts"]], ["html", "html"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Direct Result")

    def test_ddgs_is_preferred_before_legacy_html(self) -> None:
        client = DuckDuckGoSearchClient(
            user_agent="test-agent",
            proxy="socks5://127.0.0.1:7890",
            timeout_seconds=1.0,
            cache_dir=None,
        )
        ddgs_results = [SearchResult(title="DDGS Result", snippet="DDGS snippet", url="https://example.com/ddgs")]

        with patch.object(
            DuckDuckGoSearchClient,
            "_search_with_ddgs",
            return_value=(ddgs_results, 12, [{"endpoint": "ddgs", "path": "ddgs", "ok": True}]),
        ) as mocked_ddgs, patch("wikidata_simpleqa.search_client.urlopen") as mocked_urlopen:
            results = client.search("example query")

        mocked_ddgs.assert_called_once()
        mocked_urlopen.assert_not_called()
        self.assertEqual(results, ddgs_results)
        event = client.request_events[-1]
        self.assertEqual(event["backend"], "ddgs")
        self.assertTrue(event["used_ddgs"])
        self.assertFalse(event["used_legacy_fallback"])

    def test_ddgs_failure_falls_back_to_legacy_by_default(self) -> None:
        client = DuckDuckGoSearchClient(
            user_agent="test-agent",
            proxy=None,
            timeout_seconds=1.0,
            cache_dir=None,
        )
        ddgs_error = DuckDuckGoSearchError(
            "ddgs failed",
            url="ddgs",
            duration_ms=1,
            attempt_events=[
                {
                    "attempt": 1,
                    "path": "ddgs",
                    "endpoint": "ddgs",
                    "ok": False,
                    "error_type": "URLError",
                    "error_message": "timed out",
                    "retry_reason": "ddgs_transport_error",
                }
            ],
            original_error=URLError("timed out"),
        )
        html = """
        <html>
          <a class="result__a" href="https://example.com/html">HTML Result</a>
        </html>
        """

        with patch.object(DuckDuckGoSearchClient, "_search_with_ddgs", side_effect=ddgs_error), patch(
            "wikidata_simpleqa.search_client.urlopen",
            return_value=FakeSearchResponse(status=200, html=html),
        ):
            results = client.search("example query")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "HTML Result")
        event = client.request_events[-1]
        self.assertEqual(event["backend"], "legacy")
        self.assertTrue(event["used_ddgs"])
        self.assertTrue(event["used_legacy_fallback"])
        self.assertEqual([attempt["endpoint"] for attempt in event["attempts"]], ["ddgs", "html"])

    def test_disabled_legacy_fallback_raises_after_ddgs_failure(self) -> None:
        client = DuckDuckGoSearchClient(
            user_agent="test-agent",
            proxy=None,
            timeout_seconds=1.0,
            cache_dir=None,
            disable_fallbacks=("legacy",),
        )
        ddgs_error = DuckDuckGoSearchError(
            "ddgs failed",
            url="ddgs",
            duration_ms=1,
            attempt_events=[
                {
                    "attempt": 1,
                    "path": "ddgs",
                    "endpoint": "ddgs",
                    "ok": False,
                    "error_type": "URLError",
                    "error_message": "timed out",
                    "retry_reason": "ddgs_transport_error",
                }
            ],
            original_error=URLError("timed out"),
        )

        with patch.object(DuckDuckGoSearchClient, "_search_with_ddgs", side_effect=ddgs_error), patch(
            "wikidata_simpleqa.search_client.urlopen"
        ) as mocked_urlopen:
            with self.assertRaises(DuckDuckGoSearchError):
                client.search("example query")

        mocked_urlopen.assert_not_called()
        event = client.request_events[-1]
        self.assertTrue(event["failed"])
        self.assertTrue(event["legacy_fallback_disabled"])
        self.assertEqual(event["backend"], "ddgs")

    def test_disabled_direct_fallback_blocks_proxy_to_direct_retry(self) -> None:
        with patch("wikidata_simpleqa.search_client.install_proxy"), patch(
            "wikidata_simpleqa.search_client.clear_proxy"
        ), patch("wikidata_simpleqa.search_client.urlopen", side_effect=URLError("proxy unavailable")) as mocked_urlopen:
            client = DuckDuckGoSearchClient(
                user_agent="test-agent",
                proxy="socks5://127.0.0.1:9999",
                timeout_seconds=1.0,
                cache_dir=None,
                prefer_ddgs=False,
                disable_fallbacks=("direct",),
            )
            with self.assertRaises(DuckDuckGoSearchError):
                client.search("example query")

        self.assertEqual(mocked_urlopen.call_count, 1)
        event = client.request_events[-1]
        self.assertTrue(event["failed"])
        self.assertEqual([attempt["path"] for attempt in event["attempts"]], ["configured_proxy"])

    def test_global_cooldown_waits_after_consecutive_transport_failures(self) -> None:
        client = DuckDuckGoSearchClient(
            user_agent="test-agent",
            proxy=None,
            timeout_seconds=1.0,
            cache_dir=None,
            prefer_ddgs=False,
            cooldown_failure_threshold=1,
            cooldown_initial_seconds=5.0,
            cooldown_max_seconds=5.0,
        )
        html = """
        <html>
          <a class="result__a" href="https://example.com/recovered">Recovered</a>
        </html>
        """

        with patch("wikidata_simpleqa.search_client.sleep", return_value=None) as mocked_sleep:
            with patch("wikidata_simpleqa.search_client.urlopen", side_effect=URLError("timed out")):
                with self.assertRaises(DuckDuckGoSearchError):
                    client.search("first query")
            with patch("wikidata_simpleqa.search_client.urlopen", return_value=FakeSearchResponse(status=200, html=html)):
                results = client.search("second query")

        self.assertEqual(len(results), 1)
        sleep_values = [call.args[0] for call in mocked_sleep.call_args_list]
        self.assertTrue(any(value >= 4.0 for value in sleep_values))
        self.assertEqual(client.request_events[-1]["attempts"][0]["endpoint"], "global_cooldown")

    def test_global_cooldown_counts_retryable_failures_even_when_fallback_succeeds(self) -> None:
        client = DuckDuckGoSearchClient(
            user_agent="test-agent",
            proxy=None,
            timeout_seconds=1.0,
            cache_dir=None,
            prefer_ddgs=False,
            cooldown_failure_threshold=1,
            cooldown_initial_seconds=5.0,
            cooldown_max_seconds=5.0,
        )
        lite_html = """
        <html>
          <a class="result-link" href="https://example.com/lite">Lite Result</a>
        </html>
        """

        with patch(
            "wikidata_simpleqa.search_client.urlopen",
            side_effect=[
                FakeSearchResponse(status=202, html=""),
                FakeSearchResponse(status=200, html=lite_html),
            ],
        ):
            results = client.search("example query")

        self.assertEqual(len(results), 1)
        attempts = client.request_events[-1]["attempts"]
        self.assertTrue(attempts[-1]["cooldown_triggered"])
        self.assertEqual(attempts[-1]["endpoint"], "global_cooldown")


if __name__ == "__main__":
    unittest.main()
