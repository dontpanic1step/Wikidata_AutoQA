"""Tests for Wikidata client cache helpers."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.wikidata_client import WikidataClient


class FakeResponse:
    """Small context-manager response used to avoid live network calls."""

    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None

    def read(self) -> bytes:
        import json

        return json.dumps(self.payload).encode("utf-8")


class WikidataClientTests(unittest.TestCase):
    """Check local cache helpers without network access."""

    def test_text_mapping_cache_round_trips_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            client = WikidataClient(user_agent="test", proxy=None, cache_dir=Path(tmpdir))
            payload = {"qid": "Q1", "label": "Example"}
            client.store_text_mapping("labels", "Example", payload)
            self.assertEqual(client.load_text_mapping("labels", "Example"), payload)

    def test_missing_text_mapping_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            client = WikidataClient(user_agent="test", proxy=None, cache_dir=Path(tmpdir))
            self.assertIsNone(client.load_text_mapping("labels", "Missing"))

    def test_stats_snapshot_includes_problem_reports(self) -> None:
        client = WikidataClient(user_agent="test", proxy=None, cache_dir=None)
        client.record_problem("example", "Something happened", qid="Q1")
        snapshot = client.stats_snapshot()
        self.assertEqual(snapshot["problems"][0]["kind"], "example")
        self.assertEqual(snapshot["problems"][0]["context"]["qid"], "Q1")

    def test_search_entities_skips_blank_query(self) -> None:
        client = WikidataClient(user_agent="test", proxy=None, cache_dir=None)
        with patch("wikidata_simpleqa.wikidata_client.urlopen") as urlopen_mock:
            self.assertEqual(client.search_entities("   "), [])
        urlopen_mock.assert_not_called()
        snapshot = client.stats_snapshot()
        self.assertEqual(snapshot["problems"][0]["kind"], "wbsearchentities_blank_query")

    def test_request_json_raises_on_http_200_api_error_payload(self) -> None:
        client = WikidataClient(user_agent="test", proxy=None, cache_dir=None, max_retries=1)
        with patch(
            "wikidata_simpleqa.wikidata_client.urlopen",
            return_value=FakeResponse({"error": {"code": "badvalue", "info": "Bad value"}, "servedby": "test"}),
        ):
            with self.assertRaisesRegex(RuntimeError, "Wikidata API error: badvalue: Bad value"):
                client._request_json("https://example.test/api")
        snapshot = client.stats_snapshot()
        self.assertEqual(snapshot["errors"], 1)
        self.assertEqual(snapshot["events"][0]["status"], "error")
        self.assertEqual(snapshot["events"][0]["error_type"], "WikidataAPIError")

    def test_request_json_retries_retryable_api_error_payload(self) -> None:
        client = WikidataClient(
            user_agent="test",
            proxy=None,
            cache_dir=None,
            max_retries=2,
            min_retry_after_seconds=0,
        )
        with patch(
            "wikidata_simpleqa.wikidata_client.urlopen",
            side_effect=[
                FakeResponse({"error": {"code": "maxlag", "info": "Waiting for lagged replica"}}),
                FakeResponse({"search": []}),
            ],
        ):
            self.assertEqual(client._request_json("https://example.test/api"), {"search": []})
        snapshot = client.stats_snapshot()
        self.assertEqual(snapshot["retry_count"], 1)
        self.assertEqual(snapshot["errors"], 0)
        self.assertEqual(snapshot["events"][0]["status"], "sleeping_before_retry")
        self.assertEqual(snapshot["events"][1]["status"], "ok")


if __name__ == "__main__":
    unittest.main()
