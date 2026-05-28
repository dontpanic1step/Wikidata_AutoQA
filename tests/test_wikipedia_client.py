"""Tests for the lightweight Wikipedia client."""

from __future__ import annotations

import unittest
from time import perf_counter
from urllib.error import HTTPError

from test_support import ROOT  # noqa: F401

from wikidata_simpleqa.wikipedia_client import WikipediaClient


def _http_429(*, retry_after: str = "") -> HTTPError:
    """Return a minimal HTTP 429 error for client backoff tests."""
    headers = {"Retry-After": retry_after} if retry_after else {}
    return HTTPError(
        url="https://en.wikipedia.org/w/api.php",
        code=429,
        msg="Too Many Requests",
        hdrs=headers,
        fp=None,
    )


class WikipediaClientTests(unittest.TestCase):
    def test_http_429_extends_shared_backoff_and_honors_retry_after(self) -> None:
        client = WikipediaClient(
            user_agent="test-agent",
            proxy=None,
            timeout_seconds=1.0,
            cache_dir=None,
            rate_limit_backoff_seconds=30.0,
            rate_limit_max_backoff_seconds=100.0,
        )

        client._record_rate_limit_429(_http_429(retry_after="45"))
        first_resume_at = client._rate_limit_resume_at

        self.assertEqual(client._rate_limit_current_sleep, 45.0)
        self.assertGreaterEqual(first_resume_at, perf_counter())

        client._record_rate_limit_429(_http_429())

        self.assertEqual(client._rate_limit_current_sleep, 90.0)
        self.assertGreater(client._rate_limit_resume_at, first_resume_at)

    def test_http_429_retry_after_is_not_capped_by_local_max_backoff(self) -> None:
        client = WikipediaClient(
            user_agent="test-agent",
            proxy=None,
            timeout_seconds=1.0,
            cache_dir=None,
            rate_limit_backoff_seconds=10.0,
            rate_limit_max_backoff_seconds=120.0,
        )

        client._record_rate_limit_429(_http_429(retry_after="600"))

        self.assertEqual(client._rate_limit_current_sleep, 600.0)

    def test_http_429_synthetic_backoff_is_capped_by_local_max_backoff(self) -> None:
        client = WikipediaClient(
            user_agent="test-agent",
            proxy=None,
            timeout_seconds=1.0,
            cache_dir=None,
            rate_limit_backoff_seconds=10.0,
            rate_limit_max_backoff_seconds=120.0,
        )
        client._rate_limit_current_sleep = 90.0
        client._rate_limit_last_429_at = perf_counter()

        client._record_rate_limit_429(_http_429())

        self.assertEqual(client._rate_limit_current_sleep, 120.0)

    def test_http_429_backoff_resets_after_quiet_recovery_window(self) -> None:
        client = WikipediaClient(
            user_agent="test-agent",
            proxy=None,
            timeout_seconds=1.0,
            cache_dir=None,
            rate_limit_backoff_seconds=30.0,
            rate_limit_max_backoff_seconds=100.0,
            rate_limit_recovery_seconds=120.0,
        )
        client._rate_limit_current_sleep = 90.0
        client._rate_limit_last_429_at = perf_counter() - 121.0

        client._record_rate_limit_success()

        self.assertEqual(client._rate_limit_current_sleep, 0.0)


if __name__ == "__main__":
    unittest.main()
