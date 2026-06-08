"""Tests for the Wikipedia infobox/table QA route."""

from __future__ import annotations

import sys
import json
import hashlib
import random
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from urllib.error import URLError
from unittest.mock import patch

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.config import Settings
from wikidata_simpleqa.generation_pipeline import process_generated_candidates
from wikidata_simpleqa.generation_models import EntityReference, EvidenceRecord, GeneratedCandidate
from wikidata_simpleqa.page_id_lists import PageIdListEntry
from wikidata_simpleqa.wikipedia_client import (
    WikipediaClient,
    build_parse_api_url,
    build_search_api_url,
    normalize_wikipedia_page_id,
    normalize_wikipedia_title,
)
from wikidata_simpleqa.wikipedia_streaming import PageIdStreamState
from wikidata_simpleqa.wikipedia_infobox_generator import (
    WikipediaInfoboxTableGenerator,
    WikipediaTable,
    extract_first_paragraph,
    extract_non_table_prose,
    extract_wikipedia_tables,
    rank_wikipedia_tables,
    _annotate_table_filter_modes,
    _normalize_answer_type,
    _normalize_generated_answer,
    _rejected_placeholder,
    _subject_anchor_context,
    _tie_completion_problem,
    normalize_route3_table_source_types,
)

SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from run_wikipedia_infobox_pipeline import (  # noqa: E402
    EndpointResumeState,
    _accepted_output_records,
    _apply_big_batch_mode,
    _candidate_from_record,
    _compact_accepted_record,
    _compact_rejected_record,
    _filter_endpoint_url_entries,
    _failure_reason_counts,
    _load_endpoint_jsonl,
    _load_stream_excluded_page_ids,
    _load_url_entries,
    _load_urls,
    _remaining_after_endpoint,
    _record_reasoning_type,
    _rejected_output_records,
    _rerun_error_details_from_record,
    _reserve_stream_cached_page_archives,
    _reserve_stream_page_ids,
    _run_artifact_summary,
    _should_rerun_stream_rejection,
    _stream_rerun_pool_run_limit,
    _stream_page_id_list_entries,
    _stream_search_queries,
    _survival_by_layer,
    _wikipedia_stream_record_id,
    _write_summary_and_manifest,
    _write_stream_walkthrough,
    UrlEntry,
)


FIXTURE_HTML = """
<div class="mw-parser-output">
<p>The 2026 FIFA World Cup is the 23rd FIFA World Cup. Table capacities are not listed in prose. Example event metadata names Jane Doe as a sample host.</p>
<table class="infobox vevent">
  <tr><th colspan="2">Example event</th></tr>
  <tr><th>Edition</th><td>23rd</td></tr>
  <tr><th>Example host</th><td>Jane Doe</td></tr>
  <tr><th>Format</th><td>International tournament</td></tr>
  <tr><th>Region</th><td>North America</td></tr>
  <tr><th>Founded</th><td>1994</td></tr>
</table>
<h2><span class="mw-headline" id="Venues">Venues</span></h2>
<table class="wikitable sortable">
<caption>List of tournament venues</caption>
<tr><th>Venue</th><th>City</th><th>Capacity</th></tr>
<tr><td>AT&amp;T Stadium</td><td>Arlington</td><td>80,000</td></tr>
<tr><td>MetLife Stadium</td><td>East Rutherford</td><td>82,500</td></tr>
</table>
</div>
"""

NO_PARAGRAPH_FIXTURE_HTML = FIXTURE_HTML.replace(
    "<p>The 2026 FIFA World Cup is the 23rd FIFA World Cup. Table capacities are not listed in prose. Example event metadata names Jane Doe as a sample host.</p>",
    "",
)


class FakeWikipediaClient:
    """Fake Wikipedia client returning one parse payload and summary."""

    request_events: list[dict] = []

    def fetch_parse(self, title_or_url: str) -> dict:
        return {
            "parse": {
                "title": "2026 FIFA World Cup",
                "text": FIXTURE_HTML,
            }
        }

    def fetch_summary(self, title: str) -> dict:
        return {
            "title": title,
            "extract": (
                "The 2026 FIFA World Cup is scheduled to be the 23rd FIFA World Cup, "
                "a quadrennial international men's soccer championship."
            ),
        }


class FakeLLMClient:
    """Fake small model for deterministic Route 3 tests."""

    def __init__(self) -> None:
        self.prompts: list[str] = []

    def complete_text(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return """{
          "question": "Which stadium hosting the 23rd FIFA World Cup has the largest capacity?",
          "answer": "AT&T Stadium",
          "answer_type": "Other",
          "answer_aliases": ["AT and T Stadium"],
          "search_queries": [
            "23rd FIFA World Cup tournament venues largest capacity stadium",
            "23rd FIFA World Cup venue capacity table",
            "FIFA World Cup 23rd edition venue capacities",
            "tournament venues capacity FIFA World Cup 23rd",
            "largest capacity venue 23rd FIFA World Cup"
          ],
          "reasoning_type": "max",
          "source_table": 2,
          "derivation_summary": "Selected the venue row with the largest capacity.",
          "discard_reason": null
        }"""


class FakeSingleFactLLMClient(FakeLLMClient):
    """Fake Route 3 model output for the single fact contract."""

    def complete_text(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return """{
          "question": "What edition is the FIFA World Cup described as the 23rd FIFA World Cup?",
          "answer": "23rd",
          "answer_type": "Other",
          "answer_aliases": [],
          "search_queries": [
            "FIFA World Cup edition number",
            "FIFA World Cup 23rd edition",
            "quadrennial soccer championship edition number"
          ],
          "reasoning_type": "single_fact",
          "source_table": 1,
          "derivation_summary": "Read the Edition field from the infobox.",
          "discard_reason": null
        }"""


class FakePersonLLMClient(FakeLLMClient):
    """Fake Route 3 model output for a Person answer contract."""

    def complete_text(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return """{
          "question": "Who is listed as the example host of the 23rd FIFA World Cup?",
          "answer": "Jane Doe",
          "answer_type": "Person",
          "answer_aliases": [],
          "search_queries": [
            "23rd FIFA World Cup example host",
            "FIFA World Cup example host Jane",
            "23rd FIFA World Cup host table"
          ],
          "reasoning_type": "single_fact",
          "source_table": 1,
          "derivation_summary": "Read the person name from the table.",
          "discard_reason": null
        }"""


class FakeSocialScienceLLMClient(FakeLLMClient):
    """Fake output that violates the no-social-science-research prompt."""

    def complete_text(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return """{
          "question": "Who is the person linked to the largest self-reported ancestry group in Illinois according to the 2022 American Community Survey?",
          "answer": "German",
          "answer_type": "Person",
          "answer_aliases": [],
          "search_queries": [
            "Illinois 2022 American Community Survey largest ancestry group",
            "self-reported ancestry group Illinois ACS",
            "Illinois ancestry group 2022 survey"
          ],
          "reasoning_type": "single_fact",
          "source_table": 2,
          "derivation_summary": "Read the ancestry group row from a census-derived table.",
          "discard_reason": null
        }"""


class FakeSingleFactListLLMClient(FakeLLMClient):
    """Fake output that violates the single-fact scalar-answer contract."""

    def complete_text(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return """{
          "question": "Who are the commentators on the pilot episode in the DVD release?",
          "answer": ["Larry David", "Jeff Garlin"],
          "answer_type": "Person",
          "answer_aliases": [],
          "search_queries": [
            "pilot episode DVD commentary commentators",
            "DVD pilot episode commentary cast",
            "commentators on pilot episode DVD"
          ],
          "reasoning_type": "single_fact",
          "source_table": 2,
          "derivation_summary": "Read commentator names from the table.",
          "discard_reason": null
        }"""


class FakeAll5LLMClient(FakeLLMClient):
    """Fake all5 output with two generated slots and three discards."""

    def complete_text(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return """{
          "outputs": [
            {
              "answer_type": "Person",
              "question": "Who is named as the sample host for the 23rd FIFA World Cup?",
              "answer": "Jane Doe",
              "answer_aliases": [],
              "search_queries": ["23rd FIFA World Cup sample host field"],
              "reasoning_type": "single_fact",
              "derivation_summary": "Read the Example host field from the infobox."
            },
            {
              "answer_type": "Place",
              "discard_reason": "No stable place question is supported."
            },
            {
              "answer_type": "Number",
              "discard_reason": "No stable number question is supported."
            },
            {
              "answer_type": "Date",
              "question": "In what year was the 23rd FIFA World Cup record founded?",
              "answer": "1994",
              "answer_aliases": [],
              "search_queries": ["23rd FIFA World Cup founded field"],
              "reasoning_type": "single_fact",
              "derivation_summary": "Read the Founded field from the infobox."
            },
            {
              "answer_type": "Other",
              "discard_reason": "No stable other-type question is supported."
            }
          ]
        }"""


class FakeSearchClient:
    """Search client that returns configured result rows."""

    request_events: list[dict] = []

    def __init__(self, results_by_query: dict[str, list[dict[str, str]]] | None = None) -> None:
        self.results_by_query = results_by_query or {}

    def search(self, query: str, *, max_results: int = 5):
        rows = self.results_by_query.get(query, [])[:max_results]
        return [type("SearchResult", (), row)() for row in rows]


def _pageview_payload(views: int, *, months: int = 12) -> dict:
    """Return a simple monthly pageview payload."""
    return {
        "items": [
            {"timestamp": f"2025{month:02d}0100", "views": views}
            for month in range(1, months + 1)
        ]
    }


class WikipediaInfoboxGeneratorTests(unittest.TestCase):
    """Check URL normalization, table extraction, generation, and shared processing."""

    def test_url_normalization_and_parse_url(self) -> None:
        title = normalize_wikipedia_title("https://en.wikipedia.org/wiki/2026_FIFA_World_Cup")
        self.assertEqual(title, "2026 FIFA World Cup")
        api_url = build_parse_api_url(title)
        self.assertIn("action=parse", api_url)
        self.assertIn("page=2026+FIFA+World+Cup", api_url)
        curid_url = "https://en.wikipedia.org/w/index.php?curid=12345"
        self.assertEqual(normalize_wikipedia_page_id(curid_url), 12345)
        self.assertIn("pageid=12345", build_parse_api_url(curid_url))
        pageid_url = "https://en.wikipedia.org/w/index.php?pageid=12345"
        self.assertEqual(normalize_wikipedia_page_id(pageid_url), 12345)
        self.assertIn("pageid=12345", build_parse_api_url(pageid_url))
        search_url = build_search_api_url(r"insource:/\{\|/", namespace=0, limit=50, offset=100)
        self.assertIn("list=search", search_url)
        self.assertIn("srnamespace=0", search_url)
        self.assertIn("srlimit=50", search_url)
        self.assertIn("sroffset=100", search_url)
        self.assertIn("srsearch=insource", search_url)

    def test_wikipedia_client_retries_transient_url_errors(self) -> None:
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, traceback):
                return False

            def read(self) -> bytes:
                return b'{"parse": {"title": "Retry page", "text": ""}}'

        calls = {"count": 0}

        def fake_urlopen(request, timeout):
            calls["count"] += 1
            if calls["count"] == 1:
                raise URLError("transient tls eof")
            return FakeResponse()

        client = WikipediaClient(user_agent="test-agent", proxy=None, timeout_seconds=1.0, cache_dir=None)
        with patch("wikidata_simpleqa.wikipedia_client.urlopen", side_effect=fake_urlopen):
            payload = client.fetch_parse("https://en.wikipedia.org/w/index.php?pageid=12345")
        self.assertEqual(payload["parse"]["title"], "Retry page")
        self.assertEqual(calls["count"], 2)
        self.assertEqual(client.request_events[-1]["attempts"], 2)

    def test_wikipedia_client_stops_after_two_transient_errors(self) -> None:
        calls = {"count": 0}

        def fake_urlopen(request, timeout):
            calls["count"] += 1
            raise URLError("transient tls eof")

        client = WikipediaClient(user_agent="test-agent", proxy=None, timeout_seconds=1.0, cache_dir=None)
        with patch("wikidata_simpleqa.wikipedia_client.urlopen", side_effect=fake_urlopen), patch(
            "wikidata_simpleqa.wikipedia_client._sleep_before_retry"
        ):
            with self.assertRaises(URLError):
                client.fetch_parse("https://en.wikipedia.org/w/index.php?pageid=12345")
        self.assertEqual(calls["count"], 2)

    def test_walkthrough_labels_second_stage_responses_as_small_model_qa(self) -> None:
        accepted_record = {
            "question": "Who directed the film Example Film?",
            "answer": "Jane Doe",
            "panel_grading_features": {
                "enabled": True,
                "question": "Who directed the film Example Film?",
                "gold_answer": "Jane Doe",
                "models": [
                    {
                        "model": "openai/gpt-4.1-mini",
                        "predicted_answer": "Jane Doe",
                        "grade": "CORRECT",
                    },
                    {
                        "model": "google/gemini-3-flash-preview",
                        "predicted_answer": "John Smith",
                        "grade": "INCORRECT",
                    },
                ],
            },
            "source_metadata": {
                "page_id": 123,
                "small_model_qa_response": {"question": "Generated source question"},
                "small_model_rewrite_response": {"rewritten_question": "Who directed the film Example Film?"},
            },
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "walkthrough.md"
            _write_stream_walkthrough(
                path=path,
                summary={
                    "run_date": "2026-05-19",
                    "streaming_mode": "page_id_stream",
                    "stream_page_source": "table-search",
                    "attempted_page_ids": 1,
                    "accepted": 1,
                    "rejected": 0,
                    "rerun": 0,
                    "stream_page_workers": 4,
                    "wikipedia_concurrency_limit": 4,
                    "duckduckgo_concurrency_limit": 4,
                    "openrouter_generation_rewrite_concurrency_limit": 10,
                    "second_stage_concurrency_limit": 10,
                },
                accepted_records=[accepted_record],
                rejected_records=[],
                rerun_records=[],
            )
            text = path.read_text(encoding="utf-8")

        self.assertIn("## Second-Stage Filtering Responses", text)
        self.assertIn("| Page ID | Question | Reference answer | openai/gpt-4.1-mini | google/gemini-3-flash-preview |", text)
        self.assertIn("CORRECT; predicted_answer: Jane Doe", text)
        self.assertIn("INCORRECT; predicted_answer: John Smith", text)
        self.assertIn("Stream page workers: 4", text)
        self.assertIn("Second-stage concurrency limit: 10", text)
        self.assertNotIn("## Route 3 Generation Responses", text)
        self.assertNotIn("Route 3 generation response", text)

    def test_walkthrough_splits_endpoint_and_incremental_records(self) -> None:
        existing_accepted = {
            "question": "Who directed the existing film?",
            "answer": "Jane Doe",
            "answer_type": "Person",
            "relation_or_claim": "single_fact",
            "source_metadata": {
                "page_id": 111,
                "answer_type": "Person",
                "reasoning_type": "single_fact",
                "stream_source_url": "https://en.wikipedia.org/w/index.php?curid=111",
                "phase_timings_seconds": {
                    "total_generation_seconds": 1.0,
                    "total_processing_seconds": 2.0,
                    "second_stage_grading_seconds": 0.5,
                },
            },
        }
        existing_rejected = {
            "question": "What leaked answer appears in the old question?",
            "answer": "Leak",
            "answer_type": "Other",
            "relation_or_claim": "max",
            "rejection_reason": "rewrite_guard_rejected",
            "rejection_rule": "answer_leakage",
            "source_metadata": {
                "page_id": 112,
                "answer_type": "Other",
                "reasoning_type": "max",
                "phase_timings_seconds": {
                    "total_generation_seconds": 3.0,
                    "total_processing_seconds": 4.0,
                    "second_stage_grading_seconds": 1.0,
                },
            },
        }
        incremental_accepted = {
            "question": "Who directed the incremental film?",
            "answer": "Alex Roe",
            "answer_type": "Person",
            "relation_or_claim": "single_fact",
            "source_metadata": {
                "page_id": 211,
                "answer_type": "Person",
                "reasoning_type": "single_fact",
                "stream_source_url": "https://en.wikipedia.org/w/index.php?curid=211",
                "phase_timings_seconds": {
                    "total_generation_seconds": 5.0,
                    "total_processing_seconds": 6.0,
                    "second_stage_grading_seconds": 1.5,
                },
            },
        }
        incremental_rejected = {
            "question": "Who directed the rejected incremental film?",
            "answer": "Sam Poe",
            "answer_type": "Person",
            "relation_or_claim": "single_fact",
            "rejection_reason": "search_longtail_verifier_rejected",
            "rejection_notes": {
                "search_verification_features": {"triggered_rule": "full_question:hit_rate_exceeded"}
            },
            "source_metadata": {
                "page_id": 212,
                "answer_type": "Person",
                "reasoning_type": "single_fact",
                "phase_timings_seconds": {
                    "total_generation_seconds": 7.0,
                    "total_processing_seconds": 8.0,
                    "second_stage_grading_seconds": 2.5,
                },
            },
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "walkthrough.md"
            manifest_path = Path(tmpdir) / "manifest.json"
            summary_output = "outputs\\incremental_summary.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "segments": [
                            {"summary_output": "outputs\\fresh_summary.json", "wall_clock_seconds": 7.5},
                            {"summary_output": summary_output, "wall_clock_seconds": 12.5},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            _write_stream_walkthrough(
                path=path,
                summary={
                    "run_date": "2026-05-19",
                    "streaming_mode": "page_id_stream",
                    "stream_page_source": "table-search",
                    "run_artifact_manifest": str(manifest_path),
                    "summary_output": summary_output,
                    "endpoint_resume": {
                        "enabled": True,
                        "accepted_records_loaded": 1,
                        "rejected_records_loaded": 1,
                    },
                    "attempted_page_ids": 2,
                    "accepted": 1,
                    "accepted_total": 2,
                    "rejected": 1,
                    "rejected_total": 2,
                    "rerun": 0,
                    "wall_clock_seconds": 12.5,
                },
                accepted_records=[incremental_accepted],
                rejected_records=[incremental_rejected],
                rerun_records=[],
                existing_accepted_records=[existing_accepted],
                existing_rejected_records=[existing_rejected],
            )
            text = path.read_text(encoding="utf-8")

        self.assertIn("Existing accepted QAs before run: 1", text)
        self.assertIn("Existing rejected QAs/pages before run: 1", text)
        self.assertIn("### Overall Displayed Stats", text)
        self.assertIn("| Existing endpoint records | 2 | 1 | 1 | 0 | 50.0% |", text)
        self.assertIn("| Incremental run | 2 | 1 | 1 | 0 | 50.0% |", text)
        self.assertIn("| Overall displayed | 4 | 2 | 2 | 0 | 50.0% |", text)
        self.assertIn("### Answer Type Stats", text)
        self.assertIn("| Existing Endpoint Records | `Person` | 1 | 0 | 1 | 100.0% |", text)
        self.assertIn("| Incremental Records | `Person` | 1 | 1 | 2 | 50.0% |", text)
        self.assertIn("### Reasoning Type Stats", text)
        self.assertIn("| Existing Endpoint Records | `single_fact` | 1 | 0 | 1 | 100.0% |", text)
        self.assertIn("| Incremental Records | `single_fact` | 1 | 1 | 2 | 50.0% |", text)
        self.assertIn("#### Time Stats By Scope", text)
        self.assertIn("| Incremental run | 12.5000 | 2 | 2 | 12.0000 | 6.0000 | 14.0000 | 7.0000 | 4.0000 | 2.0000 |", text)
        self.assertIn("| Total displayed run | 20.0000 | 4 | 4 | 16.0000 | 4.0000 | 20.0000 | 5.0000 | 5.5000 | 1.3750 |", text)
        self.assertIn("#### Incremental Run Phase Timings", text)
        self.assertIn("#### Total Displayed Run Phase Timings", text)
        self.assertIn("### Existing Endpoint Records", text)
        self.assertIn("### Incremental Records", text)
        self.assertIn("Who directed the existing film?", text)
        self.assertIn("Who directed the incremental film?", text)
        self.assertIn("rewrite_guard_rejected:answer_leakage", text)
        self.assertIn("search_longtail_verifier_rejected:full_question:hit_rate_exceeded", text)

    def test_generator_uses_parse_paragraph_without_summary_fetch(self) -> None:
        class NoSummaryWikipediaClient(FakeWikipediaClient):
            def fetch_summary(self, title: str) -> dict:
                raise AssertionError("summary fetch should be a fallback only")

        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=NoSummaryWikipediaClient(),
            llm_client=FakeLLMClient(),
            record_limit=1,
            table_filter_modes=(),
        )

        candidates = generator.generate(run_date="2026-05-16", cutoff_year=2025)

        self.assertEqual(candidates[0].final_question, "Which stadium hosting the 23rd FIFA World Cup has the largest capacity?")
        timings = candidates[0].source_metadata["phase_timings_seconds"]
        self.assertIn("first_paragraph_extract_seconds", timings)
        self.assertNotIn("first_paragraph_fetch_seconds", timings)

    def test_generator_does_not_fetch_summary_fallback_by_default(self) -> None:
        class NoSummaryWikipediaClient(FakeWikipediaClient):
            def fetch_parse(self, title_or_url: str) -> dict:
                return {
                    "parse": {
                        "title": "2026 FIFA World Cup",
                        "text": NO_PARAGRAPH_FIXTURE_HTML,
                    }
                }

            def fetch_summary(self, title: str) -> dict:
                raise AssertionError("REST summary fallback is opt-in")

        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=NoSummaryWikipediaClient(),
            llm_client=FakeLLMClient(),
            record_limit=1,
            table_filter_modes=(),
        )

        candidates = generator.generate(run_date="2026-05-16", cutoff_year=2025)

        self.assertEqual(candidates[0].source_metadata["first_paragraph"], "")
        self.assertNotIn("first_paragraph_fetch_seconds", candidates[0].source_metadata["phase_timings_seconds"])
        self.assertNotIn("first_paragraph_fetch_error", candidates[0].source_metadata)

    def test_generator_treats_summary_fallback_as_nonfatal(self) -> None:
        class SummaryErrorWikipediaClient(FakeWikipediaClient):
            def fetch_parse(self, title_or_url: str) -> dict:
                return {
                    "parse": {
                        "title": "2026 FIFA World Cup",
                        "text": NO_PARAGRAPH_FIXTURE_HTML,
                    }
                }

            def fetch_summary(self, title: str) -> dict:
                raise URLError("summary tls eof")

        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=SummaryErrorWikipediaClient(),
            llm_client=FakeLLMClient(),
            record_limit=1,
            enable_rest_summary_fallback=True,
            allowed_reasoning_types=("max",),
            table_filter_modes=(),
        )

        candidates = generator.generate(run_date="2026-05-16", cutoff_year=2025)

        self.assertEqual(candidates[0].final_question, "Which stadium hosting the 23rd FIFA World Cup has the largest capacity?")
        self.assertEqual(candidates[0].source_metadata["first_paragraph"], "")
        self.assertIn("URLError", candidates[0].source_metadata["first_paragraph_fetch_error"])

    def test_route3_page_archive_reuses_parse_and_pageview_payloads(self) -> None:
        class ArchiveWikipediaClient(FakeWikipediaClient):
            def __init__(self) -> None:
                self.parse_calls = 0
                self.pageview_calls = 0
                self.request_events = []

            def fetch_parse(self, title_or_url: str) -> dict:
                self.parse_calls += 1
                return super().fetch_parse(title_or_url)

            def fetch_pageviews(self, title: str, *, start: str, end: str) -> dict:
                self.pageview_calls += 1
                return _pageview_payload(10)

        with tempfile.TemporaryDirectory() as tmpdir:
            first_client = ArchiveWikipediaClient()
            first_generator = WikipediaInfoboxTableGenerator(
                urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
                wikipedia_client=first_client,
                llm_client=FakeLLMClient(),
                record_limit=1,
                table_filter_modes=(),
                page_archive_dir=Path(tmpdir),
                pageview_prefilter_enabled=True,
            )
            first = first_generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]

            second_client = ArchiveWikipediaClient()
            second_generator = WikipediaInfoboxTableGenerator(
                urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
                wikipedia_client=second_client,
                llm_client=FakeLLMClient(),
                record_limit=1,
                table_filter_modes=(),
                page_archive_dir=Path(tmpdir),
                pageview_prefilter_enabled=True,
            )
            second = second_generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
            archive_path = Path(second.source_metadata["route3_page_archive"]["archive_path"])
            archive_payload = json.loads(archive_path.read_text(encoding="utf-8"))

        self.assertEqual(first_client.parse_calls, 1)
        self.assertEqual(first_client.pageview_calls, 1)
        self.assertEqual(second_client.parse_calls, 0)
        self.assertEqual(second_client.pageview_calls, 0)
        self.assertEqual(first.source_metadata["pageview_prefilter"]["decision"], "allow")
        self.assertTrue(second.source_metadata["route3_page_archive"]["cache_hit"])
        self.assertEqual(second.source_metadata["route3_page_archive"]["parse_fetch_status"], "archive_hit")
        self.assertEqual(second.source_metadata["route3_page_archive"]["pageview_fetch_status"], "archive_hit")
        self.assertIn("parsed_html", archive_payload)
        self.assertIn("pageview", archive_payload)
        self.assertEqual(archive_payload["pageview_prefilter"]["monthly_average"], 10.0)

    def test_route3_page_archive_can_reuse_parsed_html_without_parse_payload(self) -> None:
        class NoFetchWikipediaClient(FakeWikipediaClient):
            request_events: list[dict] = []

            def fetch_parse(self, title_or_url: str) -> dict:
                raise AssertionError("cached parsed HTML should avoid fetching parse payload")

        url = "https://en.wikipedia.org/w/index.php?pageid=2468"
        with tempfile.TemporaryDirectory() as tmpdir:
            archive_path = Path(tmpdir) / f"page_{hashlib.sha256(url.encode('utf-8')).hexdigest()}.json"
            archive_path.write_text(
                json.dumps(
                    {
                        "source_url": url,
                        "page_id": 2468,
                        "title": "2026 FIFA World Cup",
                        "canonical_url": "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup",
                        "parsed_html": FIXTURE_HTML,
                    }
                ),
                encoding="utf-8",
            )
            generator = WikipediaInfoboxTableGenerator(
                urls=[url],
                wikipedia_client=NoFetchWikipediaClient(),
                llm_client=FakeLLMClient(),
                record_limit=1,
                table_filter_modes=(),
                page_archive_dir=Path(tmpdir),
            )
            candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]

        self.assertEqual(candidate.final_question, "Which stadium hosting the 23rd FIFA World Cup has the largest capacity?")
        self.assertEqual(candidate.source_metadata["page_id"], 2468)
        self.assertEqual(
            candidate.source_metadata["route3_page_archive"]["parse_fetch_status"],
            "archive_parsed_html_hit",
        )

    def test_stream_cached_page_reuse_uses_strict_numeric_page_id_exclusions(self) -> None:
        def write_archive(path: Path, page_id: int) -> None:
            path.write_text(
                json.dumps(
                    {
                        "source_url": f"https://en.wikipedia.org/w/index.php?pageid={page_id}",
                        "page_id": page_id,
                        "parse_payload": {
                            "parse": {
                                "title": f"Cached page {page_id}",
                                "pageid": page_id,
                                "text": FIXTURE_HTML,
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cache_dir = root / "route3_pages"
            cache_dir.mkdir()
            write_archive(cache_dir / "page_a.json", 101)
            write_archive(cache_dir / "page_b.json", 102)
            write_archive(cache_dir / "page_c.json", 103)
            (cache_dir / "page_invalid.json").write_text(json.dumps({"page_id": 104}), encoding="utf-8")
            used_file = root / "used_ids.json"
            used_file.write_text(
                json.dumps(
                    [
                        101,
                        {"page_id": 102, "answer_type": "Person", "table_type": "infobox"},
                    ]
                ),
                encoding="utf-8",
            )
            state = PageIdStreamState.load(root / "state.json")
            args = SimpleNamespace(
                stream_reuse_cached_page_count=5,
                route3_page_archive_dir=cache_dir,
                stream_reuse_cached_page_used_id_file=[used_file],
            )

            selected, summary = _reserve_stream_cached_page_archives(state=state, args=args)

        self.assertEqual([entry.page_id for entry in selected], [103])
        self.assertEqual(summary["requested_count"], 5)
        self.assertEqual(summary["cached_archive_valid_page_count"], 3)
        self.assertEqual(summary["used_id_excluded_page_count"], 2)
        self.assertEqual(summary["reusable_cached_page_count"], 1)
        self.assertEqual(summary["selected_count"], 1)
        self.assertEqual(state.in_progress_ids, {103})
        self.assertTrue(any(event.get("event") == "reserve_cached_page_archives" for event in state.events))

    def test_pageview_prefilter_disabled_by_default_records_disabled_metadata(self) -> None:
        class NoPageviewWikipediaClient(FakeWikipediaClient):
            def __init__(self) -> None:
                self.pageview_calls = 0
                self.request_events = []

            def fetch_pageviews(self, title: str, *, start: str, end: str) -> dict:
                self.pageview_calls += 1
                raise AssertionError("disabled pageview prefilter must not fetch pageviews")

        llm_client = FakeLLMClient()
        wikipedia_client = NoPageviewWikipediaClient()
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = WikipediaInfoboxTableGenerator(
                urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
                wikipedia_client=wikipedia_client,
                llm_client=llm_client,
                record_limit=1,
                table_filter_modes=(),
                page_archive_dir=Path(tmpdir),
            )
            candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
            archive_path = Path(candidate.source_metadata["route3_page_archive"]["archive_path"])
            archive_payload = json.loads(archive_path.read_text(encoding="utf-8"))

        pageview = candidate.source_metadata["pageview_prefilter"]
        self.assertEqual(wikipedia_client.pageview_calls, 0)
        self.assertEqual(len(llm_client.prompts), 1)
        self.assertEqual(pageview["enabled"], False)
        self.assertEqual(pageview["status"], "disabled")
        self.assertEqual(pageview["decision"], "allow")
        self.assertEqual(pageview["reason"], "pageview_prefilter_disabled")
        self.assertEqual(candidate.source_metadata["route3_page_archive"]["pageview_status"], "disabled")
        self.assertEqual(archive_payload["pageview_prefilter"]["status"], "disabled")
        self.assertNotIn("wikipedia_pageview_prefilter_rejected", candidate.notes)
        self.assertNotIn("wikipedia_pageview_prefilter_unavailable", candidate.notes)

    def test_disabled_pageview_prefilter_preserves_cached_pageview_payload(self) -> None:
        class CachedPageviewWikipediaClient(FakeWikipediaClient):
            def __init__(self, views: int) -> None:
                self.views = views
                self.pageview_calls = 0
                self.request_events = []

            def fetch_pageviews(self, title: str, *, start: str, end: str) -> dict:
                self.pageview_calls += 1
                return _pageview_payload(self.views)

        with tempfile.TemporaryDirectory() as tmpdir:
            enabled_client = CachedPageviewWikipediaClient(views=10)
            enabled_generator = WikipediaInfoboxTableGenerator(
                urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
                wikipedia_client=enabled_client,
                llm_client=FakeLLMClient(),
                record_limit=1,
                table_filter_modes=(),
                page_archive_dir=Path(tmpdir),
                pageview_prefilter_enabled=True,
            )
            enabled_generator.generate(run_date="2026-05-16", cutoff_year=2025)

            disabled_client = CachedPageviewWikipediaClient(views=99)
            disabled_generator = WikipediaInfoboxTableGenerator(
                urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
                wikipedia_client=disabled_client,
                llm_client=FakeLLMClient(),
                record_limit=1,
                table_filter_modes=(),
                page_archive_dir=Path(tmpdir),
            )
            candidate = disabled_generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
            archive_path = Path(candidate.source_metadata["route3_page_archive"]["archive_path"])
            archive_payload = json.loads(archive_path.read_text(encoding="utf-8"))

        self.assertEqual(enabled_client.pageview_calls, 1)
        self.assertEqual(disabled_client.pageview_calls, 0)
        self.assertEqual(candidate.source_metadata["pageview_prefilter"]["status"], "disabled")
        self.assertEqual(archive_payload["pageview_prefilter"]["status"], "disabled")
        self.assertEqual(archive_payload["pageview"]["response"]["items"][0]["views"], 10)

    def test_route3_source_metadata_uses_archive_page_id_for_title_url(self) -> None:
        class PageIdWikipediaClient(FakeWikipediaClient):
            def fetch_parse(self, title_or_url: str) -> dict:
                payload = super().fetch_parse(title_or_url)
                payload["parse"]["pageid"] = 987654
                return payload

            def fetch_pageviews(self, title: str, *, start: str, end: str) -> dict:
                return _pageview_payload(10)

        with tempfile.TemporaryDirectory() as tmpdir:
            generator = WikipediaInfoboxTableGenerator(
                urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
                wikipedia_client=PageIdWikipediaClient(),
                llm_client=FakeLLMClient(),
                record_limit=1,
                table_filter_modes=(),
                page_archive_dir=Path(tmpdir),
            )
            candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
            archive_path = Path(candidate.source_metadata["route3_page_archive"]["archive_path"])
            archive_payload = json.loads(archive_path.read_text(encoding="utf-8"))

        self.assertEqual(candidate.source_metadata["source_url"], "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup")
        self.assertEqual(candidate.source_metadata["page_id"], 987654)
        self.assertEqual(candidate.source_metadata["route3_page_archive"]["page_id"], 987654)
        self.assertEqual(archive_payload["page_id"], 987654)

    def test_route3_page_archive_backfills_missing_pageview_without_refetching_parse(self) -> None:
        class BackfillWikipediaClient(FakeWikipediaClient):
            def __init__(self) -> None:
                self.parse_calls = 0
                self.pageview_calls = 0
                self.request_events = []

            def fetch_parse(self, title_or_url: str) -> dict:
                self.parse_calls += 1
                return super().fetch_parse(title_or_url)

            def fetch_pageviews(self, title: str, *, start: str, end: str) -> dict:
                self.pageview_calls += 1
                return _pageview_payload(20)

        with tempfile.TemporaryDirectory() as tmpdir:
            first_client = BackfillWikipediaClient()
            generator = WikipediaInfoboxTableGenerator(
                urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
                wikipedia_client=first_client,
                llm_client=FakeLLMClient(),
                record_limit=1,
                table_filter_modes=(),
                page_archive_dir=Path(tmpdir),
                pageview_prefilter_enabled=False,
            )
            first = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
            archive_path = Path(first.source_metadata["route3_page_archive"]["archive_path"])

            second_client = BackfillWikipediaClient()
            second_generator = WikipediaInfoboxTableGenerator(
                urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
                wikipedia_client=second_client,
                llm_client=FakeLLMClient(),
                record_limit=1,
                table_filter_modes=(),
                page_archive_dir=Path(tmpdir),
                pageview_prefilter_enabled=True,
            )
            second = second_generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
            archive_exists = archive_path.exists()

        self.assertTrue(archive_exists)
        self.assertEqual(second_client.parse_calls, 0)
        self.assertEqual(second_client.pageview_calls, 1)
        self.assertEqual(second.source_metadata["pageview_prefilter"]["monthly_average"], 20.0)
        self.assertEqual(second.source_metadata["route3_page_archive"]["parse_fetch_status"], "archive_hit")
        self.assertEqual(second.source_metadata["route3_page_archive"]["pageview_fetch_status"], "fetched")

    def test_pageview_prefilter_rejects_high_popularity_before_llm(self) -> None:
        class PopularWikipediaClient(FakeWikipediaClient):
            request_events: list[dict] = []

            def fetch_pageviews(self, title: str, *, start: str, end: str) -> dict:
                return _pageview_payload(5001)

        llm_client = FakeLLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=PopularWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
            table_filter_modes=(),
            pageview_prefilter_enabled=True,
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]

        self.assertIn("wikipedia_pageview_prefilter_rejected", candidate.notes)
        self.assertEqual(llm_client.prompts, [])
        self.assertEqual(candidate.source_metadata["pageview_prefilter"]["decision"], "reject")
        self.assertEqual(candidate.source_metadata["pageview_prefilter"]["monthly_average"], 5001.0)

    def test_shared_processing_preserves_pageview_prefilter_rejection_reason(self) -> None:
        class PopularWikipediaClient(FakeWikipediaClient):
            request_events: list[dict] = []

            def fetch_pageviews(self, title: str, *, start: str, end: str) -> dict:
                return _pageview_payload(5001)

        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=PopularWikipediaClient(),
            llm_client=FakeLLMClient(),
            record_limit=1,
            table_filter_modes=(),
            pageview_prefilter_enabled=True,
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]

        result = process_generated_candidates(
            [candidate],
            settings=Settings(
                target_time="2024",
                pilot_total=1,
                cutoff_year=2025,
                enabled_routes=("route3_wikipedia_infobox",),
            ),
            search_client=FakeSearchClient(),
        )

        self.assertEqual(result.accepted, [])
        self.assertEqual(result.rejected[0]["rejection_reason"], "wikipedia_pageview_prefilter_rejected")
        self.assertEqual(
            result.rejected[0]["source_metadata"]["discard_reason"],
            "monthly_average_pageviews>5000.0000",
        )
        self.assertNotIn("rewrite_disabled", result.rejected[0]["notes"])

    def test_pageview_prefilter_rejects_underfilled_window_when_single_month_above_threshold(self) -> None:
        class UnderfilledPopularWikipediaClient(FakeWikipediaClient):
            request_events: list[dict] = []

            def fetch_pageviews(self, title: str, *, start: str, end: str) -> dict:
                return _pageview_payload(20000, months=11)

        llm_client = FakeLLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=UnderfilledPopularWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
            table_filter_modes=(),
            pageview_prefilter_enabled=True,
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]

        self.assertEqual(llm_client.prompts, [])
        self.assertIn("wikipedia_pageview_prefilter_rejected", candidate.notes)
        pageview = candidate.source_metadata["pageview_prefilter"]
        self.assertEqual(pageview["decision"], "reject")
        self.assertEqual(pageview["status"], "incomplete_window")
        self.assertEqual(pageview["reason"], "underfilled_monthly_pageviews>10000.0000")
        self.assertEqual(pageview["observed_month_count"], 11)
        self.assertEqual(pageview["required_month_count"], 12)
        self.assertTrue(pageview["incomplete_window"])
        self.assertEqual(pageview["max_observed_monthly"], 20000)

    def test_pageview_prefilter_allows_underfilled_window_below_single_month_threshold(self) -> None:
        class UnderfilledAllowedWikipediaClient(FakeWikipediaClient):
            request_events: list[dict] = []

            def fetch_pageviews(self, title: str, *, start: str, end: str) -> dict:
                return _pageview_payload(10000, months=11)

        llm_client = FakeLLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=UnderfilledAllowedWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
            table_filter_modes=(),
            pageview_prefilter_enabled=True,
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]

        self.assertEqual(len(llm_client.prompts), 1)
        pageview = candidate.source_metadata["pageview_prefilter"]
        self.assertEqual(pageview["decision"], "allow")
        self.assertEqual(pageview["status"], "incomplete_window")
        self.assertEqual(pageview["reason"], "underfilled_monthly_pageviews_within_threshold")
        self.assertEqual(pageview["observed_month_count"], 11)
        self.assertEqual(pageview["required_month_count"], 12)
        self.assertTrue(pageview["incomplete_window"])
        self.assertEqual(pageview["monthly_average"], 10000.0)
        self.assertEqual(pageview["max_observed_monthly"], 10000)

    def test_pageview_unavailable_allow_records_error_and_continues(self) -> None:
        class PageviewErrorWikipediaClient(FakeWikipediaClient):
            request_events: list[dict] = []

            def fetch_pageviews(self, title: str, *, start: str, end: str) -> dict:
                raise URLError("pageview offline")

        llm_client = FakeLLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=PageviewErrorWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
            table_filter_modes=(),
            pageview_prefilter_enabled=True,
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]

        self.assertEqual(len(llm_client.prompts), 1)
        pageview = candidate.source_metadata["pageview_prefilter"]
        self.assertEqual(pageview["decision"], "allow")
        self.assertEqual(pageview["status"], "error")
        self.assertEqual(pageview["errors"][0]["error_type"], "URLError")

    def test_broad_table_search_query_is_opt_in(self) -> None:
        default_args = SimpleNamespace(stream_search_query=[], enable_broad_table_search=False)
        self.assertEqual(_stream_search_queries(default_args), ['insource:"wikitable"'])

        broad_args = SimpleNamespace(stream_search_query=[], enable_broad_table_search=True)
        self.assertEqual(_stream_search_queries(broad_args), ['insource:"wikitable"', r"insource:/\{\|/"])

    def test_rerun_pool_only_reservation_does_not_discover_fresh_ids(self) -> None:
        class FailingWikipediaSearchClient:
            def search_page_ids(self, *args, **kwargs):  # noqa: ANN002, ANN003
                raise AssertionError("rerun-pool-only mode must not call discovery")

        with tempfile.TemporaryDirectory() as tmpdir:
            state = PageIdStreamState.load(Path(tmpdir) / "state.json")
            state.mark_rerun(101, reason="search_longtail_verifier_error")
            state.mark_rerun(102, reason="second_stage_grading_error")
            args = SimpleNamespace(stream_page_source="table-search")

            selected = _reserve_stream_page_ids(
                state=state,
                args=args,
                wikipedia_client=FailingWikipediaSearchClient(),
                rng=random.Random(1),
                count=5,
                rerun_pool_only=True,
            )

        self.assertEqual(selected, [101, 102])
        self.assertEqual(state.rerun_pool, [])
        self.assertEqual(state.in_progress_ids, {101, 102})

    def test_normal_table_search_reservation_does_not_consume_rerun_pool(self) -> None:
        class FakeWikipediaSearchClient:
            def search_page_ids(self, *args, **kwargs):  # noqa: ANN002, ANN003
                return [SimpleNamespace(page_id=303)]

        with tempfile.TemporaryDirectory() as tmpdir:
            state = PageIdStreamState.load(Path(tmpdir) / "state.json")
            state.mark_rerun(301, reason="transient")
            args = SimpleNamespace(
                stream_page_source="table-search",
                stream_search_max_rounds=1,
                stream_search_limit=50,
                stream_search_query=[],
                enable_broad_table_search=False,
            )

            selected = _reserve_stream_page_ids(
                state=state,
                args=args,
                wikipedia_client=FakeWikipediaSearchClient(),
                rng=random.Random(1),
                count=1,
            )

        self.assertEqual(selected, [303])
        self.assertEqual(state.rerun_pool, [301])

    def test_table_search_reservation_can_prefer_rerun_pool_then_fresh_ids(self) -> None:
        class FakeWikipediaSearchClient:
            def search_page_ids(self, *args, **kwargs):  # noqa: ANN002, ANN003
                return [SimpleNamespace(page_id=303)]

        with tempfile.TemporaryDirectory() as tmpdir:
            state = PageIdStreamState.load(Path(tmpdir) / "state.json")
            state.mark_rerun(301, reason="transient")
            args = SimpleNamespace(
                stream_page_source="table-search",
                stream_search_max_rounds=1,
                stream_search_limit=50,
                stream_search_query=[],
                enable_broad_table_search=False,
            )

            selected = _reserve_stream_page_ids(
                state=state,
                args=args,
                wikipedia_client=FakeWikipediaSearchClient(),
                rng=random.Random(1),
                count=2,
                prefer_rerun_pool=True,
            )

        self.assertEqual(selected, [301, 303])
        self.assertEqual(state.rerun_pool, [])
        self.assertEqual(state.in_progress_ids, {301, 303})

    def test_stream_state_can_seed_and_free_rerun_pool_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state = PageIdStreamState.load(Path(tmpdir) / "state.json")
            seeded = state.seed_rerun_pool([101, 101, 102], reason="test_seed")
            state.mark_accepted(102)
            cleared = state.clear_rerun_pool([101, 102], free_unused_page_ids=True, reason="test_clear")

        self.assertEqual(seeded, [101, 102])
        self.assertEqual(cleared, [101])
        self.assertNotIn(101, state.used_ids)
        self.assertIn(102, state.used_ids)
        self.assertEqual(state.rerun_pool, [])

    def test_table_search_reservation_skips_external_page_id_exclusions(self) -> None:
        class FakeWikipediaSearchClient:
            def __init__(self) -> None:
                self.calls = 0

            def search_page_ids(self, *args, **kwargs):  # noqa: ANN002, ANN003
                self.calls += 1
                if self.calls == 1:
                    return [SimpleNamespace(page_id=101), SimpleNamespace(page_id=102)]
                return [SimpleNamespace(page_id=201)]

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            exclusion_file = root / "exclude.json"
            exclusion_file.write_text(json.dumps([101, 102]), encoding="utf-8")
            state = PageIdStreamState.load(root / "state.json")
            state.used_ids.update(_load_stream_excluded_page_ids([exclusion_file]))
            args = SimpleNamespace(
                stream_page_source="table-search",
                stream_search_max_rounds=2,
                stream_search_limit=50,
                stream_search_query=[],
                enable_broad_table_search=False,
            )

            selected = _reserve_stream_page_ids(
                state=state,
                args=args,
                wikipedia_client=FakeWikipediaSearchClient(),
                rng=random.Random(1),
                count=1,
            )

        self.assertEqual(selected, [201])
        self.assertEqual(state.table_search_offset('insource:"wikitable"'), 100)
        self.assertTrue({101, 102, 201}.issubset(state.used_ids))

    def test_triadic_stream_exclusions_match_current_answer_and_table_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            exclusion_file = Path(tmpdir) / "exclude.json"
            exclusion_file.write_text(
                json.dumps(
                    [
                        {"page_id": 101, "answer_type": "Person", "table_type": "infobox"},
                        {"page_id": 102, "answer_type": "Person", "table_type": "infobox"},
                        {"page_id": 102, "answer_type": "Person", "table_type": "wikitable"},
                        {"page_id": 103},
                        {"page_id": 104, "answer_type": "Person"},
                        {"page_id": 105, "table_type": "infobox"},
                    ]
                ),
                encoding="utf-8",
            )

            person_infobox = _load_stream_excluded_page_ids(
                [exclusion_file],
                answer_types=["Person"],
                table_types=["infobox"],
            )
            place_infobox = _load_stream_excluded_page_ids(
                [exclusion_file],
                answer_types=["Place"],
                table_types=["infobox"],
            )
            person_both = _load_stream_excluded_page_ids(
                [exclusion_file],
                answer_types=["Person"],
                table_types=["infobox", "wikitable"],
            )

        self.assertEqual(person_infobox, {101, 102, 103})
        self.assertEqual(place_infobox, {103})
        self.assertEqual(person_both, {101, 102, 103})

    def test_table_search_discovery_retries_transient_errors_before_stopping(self) -> None:
        class FlakyWikipediaSearchClient:
            def __init__(self) -> None:
                self.calls = 0

            def search_page_ids(self, *args, **kwargs):  # noqa: ANN002, ANN003
                self.calls += 1
                if self.calls == 1:
                    raise RuntimeError("HTTP Error 429: Too Many Requests")
                return [SimpleNamespace(page_id=501)]

        with tempfile.TemporaryDirectory() as tmpdir:
            state = PageIdStreamState.load(Path(tmpdir) / "state.json")
            args = SimpleNamespace(
                stream_page_source="table-search",
                stream_search_max_rounds=1,
                stream_search_limit=50,
                stream_search_query=[],
                enable_broad_table_search=False,
                stream_discovery_max_retries=2,
                stream_discovery_retry_backoff_seconds=0.0,
                stream_discovery_retry_max_sleep_seconds=0.0,
            )
            client = FlakyWikipediaSearchClient()

            selected = _reserve_stream_page_ids(
                state=state,
                args=args,
                wikipedia_client=client,
                rng=random.Random(1),
                count=1,
            )

        self.assertEqual(selected, [501])
        self.assertEqual(client.calls, 2)
        self.assertEqual(state.table_search_offset('insource:"wikitable"'), 50)
        self.assertTrue(any(event.get("event") == "discovery_error" for event in state.events))

    def test_rerun_pool_limit_defaults_to_whole_pool(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state = PageIdStreamState.load(Path(tmpdir) / "state.json")
            for page_id in [201, 202, 203]:
                state.mark_rerun(page_id, reason="transient")

            self.assertEqual(_stream_rerun_pool_run_limit(state, SimpleNamespace(stream_rerun_pool_limit=0)), 3)
            self.assertEqual(_stream_rerun_pool_run_limit(state, SimpleNamespace(stream_rerun_pool_limit=2)), 2)

    def test_endpoint_resume_loads_jsonl_and_skips_malformed_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "accepted.jsonl"
            path.write_text('{"question": "ok"}\n{"question":\n', encoding="utf-8")

            records, skipped = _load_endpoint_jsonl(path, label="accepted")

        self.assertEqual(records, [{"question": "ok"}])
        self.assertEqual(len(skipped), 1)
        self.assertEqual(skipped[0]["line_number"], 2)

    def test_endpoint_resume_skips_completed_url_entries(self) -> None:
        endpoint = EndpointResumeState(
            enabled=True,
            accepted_records=[
                {
                    "source_metadata": {
                        "source_url": "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup",
                        "canonical_url": "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup",
                    }
                }
            ],
        )
        entries = [
            UrlEntry(url="https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"),
            UrlEntry(url="https://en.wikipedia.org/wiki/Example_Page"),
        ]

        filtered, skipped = _filter_endpoint_url_entries(entries, endpoint)

        self.assertEqual([entry.url for entry in filtered], ["https://en.wikipedia.org/wiki/Example_Page"])
        self.assertEqual(skipped, ["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"])
        self.assertEqual(_remaining_after_endpoint(40, endpoint.final_decision_count), 39)

    def test_wikipedia_stream_id_uses_generation_answer_type_prefix(self) -> None:
        record = {
            "answer_type": "Date",
            "source_metadata": {
                "page_id": 123,
                "selected_source_table": {"table_type": "wikitable"},
            },
        }

        self.assertEqual(
            _wikipedia_stream_record_id(record, 23, run_date="2026-05-25"),
            "route3_20260525_p123_date_wikitable",
        )

        fallback = {"answer_type": "Date", "source_metadata": {"answer_type": "Other"}}
        self.assertEqual(_wikipedia_stream_record_id(fallback, 23), "date_wikipedia_stream_000023")

    def test_run_group_manifest_indexes_resumed_segments(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest = root / "manifest.json"
            prior_summary = root / "fresh_summary.json"
            prior_summary.write_text(
                json.dumps(
                    {
                        "start_from_endpoint": False,
                        "start_stage": "generate",
                        "streaming_mode": "page_id_stream",
                        "record_limit": 40,
                        "attempted_page_ids": 40,
                        "accepted": 9,
                        "rejected": 31,
                        "summary_output": str(prior_summary),
                        "walkthrough_output": str(root / "fresh.md"),
                        "output_path": str(root / "accepted.jsonl"),
                        "rejected_output_path": str(root / "rejected.jsonl"),
                        "stream_state": str(root / "state.json"),
                    }
                ),
                encoding="utf-8",
            )
            args = SimpleNamespace(
                run_group_id="fast40",
                run_segment_id="incremental",
                run_artifact_manifest=manifest,
                run_artifact_include_summary=[prior_summary],
                summary_output=root / "incremental_summary.json",
            )
            summary = {
                **_run_artifact_summary(args),
                "start_from_endpoint": True,
                "start_stage": "generate",
                "streaming_mode": "page_id_stream",
                "record_limit": 80,
                "attempted_page_ids": 40,
                "accepted": 10,
                "accepted_total": 19,
                "rejected": 30,
                "rejected_total": 61,
                "rerun": 0,
                "summary_output": str(args.summary_output),
                "walkthrough_output": str(root / "incremental.md"),
                "output_path": str(root / "accepted.jsonl"),
                "rejected_output_path": str(root / "rejected.jsonl"),
                "stream_state": str(root / "state.json"),
            }

            _write_summary_and_manifest(args, summary)

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(payload["run_group_id"], "fast40")
            self.assertEqual([row["segment_id"] for row in payload["segments"]], ["fresh_summary", "incremental"])
            self.assertEqual(payload["artifact_index"]["accepted_jsonl"], [str(root / "accepted.jsonl")])
            self.assertEqual(
                payload["artifact_index"]["summary_json"],
                [str(prior_summary), str(args.summary_output)],
            )
            self.assertEqual(
                payload["artifact_index"]["walkthrough_md"],
                [str(root / "fresh.md"), str(root / "incremental.md")],
            )

    def test_failure_reason_stats_collapse_noisy_details(self) -> None:
        records = [
            {
                "rejection_reason": "search_longtail_verifier_rejected",
                "rejection_notes": {
                    "search_verification_features": {"triggered_rule": "full_question:hit_rate_exceeded"}
                },
            },
            {
                "rejection_reason": "search_longtail_verifier_rejected",
                "rejection_notes": {
                    "search_verification_features": {"triggered_rule": "keyword_query_1:answer_in_title"}
                },
            },
            {
                "rejection_reason": "second_stage_grading_accuracy_threshold_exceeded",
                "rejection_notes": {"panel_grading_features": {"accuracy": 0.5, "accuracy_threshold": 0.1}},
            },
            {
                "rejection_reason": "wikipedia_infobox_table_filter_rejected",
                "source_metadata": {
                    "discard_reason": (
                        "not_number_dominant:comma_number_count=2;"
                        "no_social_science_research:population"
                    )
                },
            },
            {
                "rejection_reason": "wikipedia_infobox_table_filter_rejected",
                "source_metadata": {"discard_reason": "no_social_science_research:census,population"},
            },
            {
                "rejection_reason": "wikipedia_infobox_llm_discarded",
                "source_metadata": {"discard_reason": "No date or year information is present."},
            },
            {
                "rejection_reason": "shared_validation_failed",
                "notes": ["wikipedia_pageview_prefilter_rejected"],
                "rejection_notes": {"validation": {"answer_in_evidence": False}},
                "source_metadata": {"discard_reason": "monthly_average_pageviews>5000.0000"},
            },
        ]

        counts = {
            (row["stage"], row["reason"]): row["count"]
            for row in _failure_reason_counts(records, [])
        }

        self.assertEqual(counts[("search_longtail", "search_longtail_verifier_rejected")], 2)
        self.assertEqual(
            counts[("second_stage_grading", "second_stage_grading_accuracy_threshold_exceeded")],
            1,
        )
        self.assertEqual(
            counts[("route_generation", "wikipedia_infobox_table_filter_rejected:no_social_science_research")],
            2,
        )
        self.assertEqual(
            counts[("route_generation", "wikipedia_infobox_llm_discarded:No date or year information is present.")],
            1,
        )
        self.assertEqual(
            counts[("route_generation", "wikipedia_pageview_prefilter_rejected:monthly_average_pageviews>5000.0000")],
            1,
        )
        self.assertFalse(any("hit_rate_exceeded" in reason for _, reason in counts))
        self.assertFalse(any("accuracy=" in reason or "threshold=" in reason for _, reason in counts))
        self.assertFalse(any("population" in reason or "comma_number_count" in reason for _, reason in counts))

    def test_survival_stats_place_pageview_placeholder_rejections_at_route_generation(self) -> None:
        records = [
            {
                "rejection_reason": "shared_validation_failed",
                "notes": ["wikipedia_pageview_prefilter_rejected"],
                "rejection_notes": {"validation": {"answer_in_evidence": False}},
                "source_metadata": {"discard_reason": "monthly_average_pageviews>5000.0000"},
            }
        ]

        rows = {row["stage"]: row for row in _survival_by_layer(attempted_count=1, rejected_records=records, rerun_records=[])}

        self.assertEqual(rows["route_generation"]["failed"], 1)
        self.assertEqual(rows["shared_validation"]["failed"], 0)

    def test_all5_page_level_prerewrite_rejection_writes_page_only_used_entry(self) -> None:
        records = [
            {
                "rejection_reason": "wikipedia_pageview_prefilter_rejected",
                "notes": ["wikipedia_pageview_prefilter_rejected"],
                "answer_type": "",
                "source_metadata": {
                    "page_id": 101,
                    "answer_type_mode": "all5",
                    "route3_slot_id": "",
                    "discard_reason": "monthly_average_pageviews>5000.0000",
                    "table_source_types": ["infobox"],
                },
            }
        ]

        entries = _stream_page_id_list_entries(
            [101, 102],
            all_decision_records=records,
            answer_types=["Person", "Place", "Number", "Date", "Other"],
            table_types=["infobox"],
        )

        self.assertIn(PageIdListEntry(page_id=101), entries)
        self.assertFalse(any(entry.page_id == 101 and entry.answer_type for entry in entries))
        self.assertIn(PageIdListEntry(page_id=102, answer_type="Person", table_type="infobox"), entries)
        self.assertIn(PageIdListEntry(page_id=102, answer_type="Other", table_type="infobox"), entries)

    def test_all5_slot_level_prerewrite_rejection_keeps_triadic_used_entries(self) -> None:
        records = [
            {
                "rejection_reason": "wikipedia_infobox_llm_discarded",
                "notes": ["wikipedia_infobox_llm_discarded"],
                "answer_type": "Date",
                "source_metadata": {
                    "page_id": 201,
                    "answer_type_mode": "all5",
                    "route3_slot_id": "Date",
                    "discard_reason": "No stable date question is supported.",
                    "selected_source_table": {"table_type": "infobox"},
                },
            }
        ]

        entries = _stream_page_id_list_entries(
            [201],
            all_decision_records=records,
            answer_types=["Person", "Place", "Number", "Date", "Other"],
            table_types=["infobox"],
        )

        self.assertNotIn(PageIdListEntry(page_id=201), entries)
        self.assertIn(PageIdListEntry(page_id=201, answer_type="Date", table_type="infobox"), entries)
        self.assertIn(PageIdListEntry(page_id=201, answer_type="Person", table_type="infobox"), entries)

    def test_stream_page_id_entries_use_actual_selected_table_type(self) -> None:
        records = [
            {
                "answer_type": "Person",
                "source_metadata": {
                    "page_id": 301,
                    "table_source_types": ["infobox", "wikitable"],
                    "selected_source_table": {"table_type": "infobox"},
                },
            }
        ]

        entries = _stream_page_id_list_entries(
            [301],
            all_decision_records=records,
            answer_types=["Person"],
            table_types=["infobox", "wikitable"],
        )

        self.assertEqual(entries, {PageIdListEntry(page_id=301, answer_type="Person", table_type="infobox")})

    def test_stream_page_id_entries_fall_back_to_configured_table_types_without_decision_metadata(self) -> None:
        entries = _stream_page_id_list_entries(
            [401],
            all_decision_records=[],
            answer_types=["Person"],
            table_types=["infobox", "wikitable"],
        )

        self.assertEqual(
            entries,
            {
                PageIdListEntry(page_id=401, answer_type="Person", table_type="infobox"),
                PageIdListEntry(page_id=401, answer_type="Person", table_type="wikitable"),
            },
        )

    def test_compact_big_batch_records_keep_review_fields(self) -> None:
        accepted = {
            "id": "wikipedia_stream_000001",
            "question": "Who acted in the example?",
            "answer": "Jane Doe",
            "answer_aliases": ["J. Doe"],
            "source_type": "wikipedia_tables",
            "generation_route": "route3_wikipedia_infobox",
            "subject_entity": {
                "name": "Example page",
                "qid": "Q1",
                "wikipedia_title": "Example_page",
                "url": "https://en.wikipedia.org/wiki/Example_page",
            },
            "relation_or_claim": "single_fact",
            "answer_type": "Person",
            "panel_grading_features": {"accuracy": 0.0, "models": [{"model": "m"}]},
            "source_metadata": {
                "page_title": "Example page",
                "first_paragraph": "Intro.",
                "subject_anchor_aliases": ["Example page"],
                "safe_subject_aliases": ["Example"],
                "subject_anchors": {"page_title": "Example page"},
                "parsed_tables": [{"table_index": 1}],
                "selected_source_table": {"table_index": 1},
                "llm_response": {
                    "question": "Who acted in the example?",
                    "answer": "Jane Doe",
                    "reasoning_type": "single_fact",
                },
                "phase_timings_seconds": {"total_generation_seconds": 1.2},
                "discard_reason": "large field should not leak",
            },
            "evidence": {"text": "large evidence should not leak"},
        }
        compact_accepted = _compact_accepted_record(accepted)

        self.assertEqual(
            set(compact_accepted),
            {
                "id",
                "question",
                "answer",
                "answer_aliases",
                "source_type",
                "generation_route",
                "subject_entity",
                "reasoning_type",
                "answer_type",
                "panel_grading_features",
                "source_metadata",
            },
        )
        self.assertEqual(compact_accepted["reasoning_type"], "single_fact")
        self.assertEqual(set(compact_accepted["subject_entity"]), {"name", "wikipedia_title", "url"})
        self.assertEqual(
            set(compact_accepted["source_metadata"]),
            {
                "page_title",
                "first_paragraph",
                "subject_anchor_aliases",
                "safe_subject_aliases",
                "subject_anchors",
                "parsed_tables",
                "selected_source_table",
                "llm_response",
                "small_model_qa_response",
                "phase_timings_seconds",
            },
        )
        self.assertEqual(
            compact_accepted["source_metadata"]["llm_response"],
            {
                "question": "Who acted in the example?",
                "answer": "Jane Doe",
                "reasoning_type": "single_fact",
            },
        )

        rejected = {
            "id": "bad",
            "question": "Who acted in the easy example?",
            "answer": "Jane Doe",
            "rejection_reason": "second_stage_grading_accuracy_threshold_exceeded",
            "rejection_notes": {
                "panel_grading_features": {
                    "accuracy": 0.5,
                    "accuracy_threshold": 0.1,
                    "model_count": 2,
                }
            },
            "source_metadata": {
                "page_id": 123,
                "stream_source_url": "https://en.wikipedia.org/w/index.php?pageid=123",
                "page_title": "Example page",
                "phase_timings_seconds": {"total_processing_seconds": 2.3},
            },
            "evidence": {"text": "large evidence should not leak"},
        }
        compact_rejected = _compact_rejected_record(rejected)

        self.assertEqual(compact_rejected["page_id"], 123)
        self.assertEqual(
            compact_rejected["failing_reason"],
            "second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1",
        )
        self.assertEqual(compact_rejected["failure_metrics"]["accuracy_threshold"], 0.1)
        self.assertNotIn("evidence", compact_rejected)

    def test_route3_output_helpers_ignore_compact_flags_and_keep_full_records(self) -> None:
        accepted = {
            "id": "wikipedia_stream_000001",
            "question": "Who acted in the example?",
            "answer": "Jane Doe",
            "answer_type": "Person",
            "source_metadata": {
                "page_id": 123,
                "llm_prompt": "full prompt",
                "llm_audit": {"response_body": {"id": "resp"}},
                "selected_source_table": {"table_type": "infobox"},
            },
            "evidence": {"text": "full evidence"},
        }
        rejected = {
            "question": "Who acted in the easy example?",
            "answer": "Jane Doe",
            "answer_type": "Person",
            "rejection_reason": "wikipedia_infobox_llm_discarded",
            "source_metadata": {
                "llm_prompt": "full prompt",
                "llm_audit": {"response_body": {"id": "resp"}},
                "selected_source_table": {"table_type": "wikitable"},
                "streaming_discovery": {"page_id": 456},
            },
            "evidence": {"text": "full evidence"},
        }
        args = SimpleNamespace(compact_output=True, compact_rejected_output=True, big_batch_mode=True)

        _apply_big_batch_mode(args)
        accepted_records = _accepted_output_records([accepted], args)
        rejected_records = _rejected_output_records([rejected], args)

        self.assertEqual(accepted_records, [accepted])
        self.assertEqual(rejected_records, [rejected])
        self.assertIn("evidence", accepted_records[0])
        self.assertIn("llm_prompt", rejected_records[0]["source_metadata"])
        self.assertEqual(
            accepted_records[0]["source_metadata"]["page_id_list_entry"],
            {"page_id": 123, "answer_type": "Person", "table_type": "infobox"},
        )
        self.assertEqual(
            rejected_records[0]["source_metadata"]["page_id_list_entry"],
            {"page_id": 456, "answer_type": "Person", "table_type": "wikitable"},
        )

    def test_rejection_placeholder_uses_single_allowed_reasoning_type(self) -> None:
        candidate = _rejected_placeholder(
            url="https://en.wikipedia.org/wiki/Example",
            title="Example",
            canonical_url="https://en.wikipedia.org/wiki/Example",
            question="Example",
            answer="",
            first_paragraph="Example paragraph.",
            run_date="2026-05-21",
            timings={},
            reason="wikipedia_infobox_table_filter_rejected",
            allowed_reasoning_types=("single_fact",),
            allowed_answer_types=("Person",),
        )

        self.assertEqual(candidate.relation_or_claim, "single_fact")
        self.assertEqual(candidate.source_metadata["reasoning_type"], "single_fact")

    def test_walkthrough_reasoning_type_uses_single_allowed_reasoning_type_for_legacy_placeholder(self) -> None:
        record = {
            "relation_or_claim": "wikipedia_table_fact",
            "source_metadata": {"allowed_reasoning_types": ["single_fact"]},
        }

        self.assertEqual(_record_reasoning_type(record), "single_fact")

    def test_table_extraction_preserves_infobox_and_wikitable_rows(self) -> None:
        tables = extract_wikipedia_tables(FIXTURE_HTML)
        self.assertEqual(len(tables), 2)
        self.assertEqual(tables[0].table_type, "infobox")
        self.assertEqual(tables[0].row_dicts, [])
        self.assertIn("| Column 1 | Column 2 |", tables[0].markdown)
        self.assertIn("| Example event |  |", tables[0].markdown)
        self.assertIn("| Edition | 23rd |", tables[0].markdown)
        self.assertIn("| Example host | Jane Doe |", tables[0].markdown)
        self.assertEqual(tables[1].caption, "List of tournament venues")
        self.assertEqual(tables[1].section_heading, "Venues")
        self.assertEqual(tables[1].row_dicts, [])
        self.assertIn("| Venue | City | Capacity |", tables[1].markdown)
        self.assertIn("| AT&T Stadium | Arlington | 80,000 |", tables[1].markdown)
        self.assertFalse(tables[1].structure["legacy_row_dict_parser_enabled"])

    def test_table_rows_do_not_duplicate_headers(self) -> None:
        html = """
        <div class="mw-parser-output">
        <table class="wikitable">
        <tr><th>Award</th><th>Wins</th><th>Nominations</th></tr>
        <tr><td>Emmy Awards</td><td>3</td><td>5</td></tr>
        </table>
        </div>
        """

        table = extract_wikipedia_tables(html)[0]

        self.assertEqual(table.headers, ["Award", "Wins", "Nominations"])
        self.assertEqual(table.rows[0], ["Emmy Awards", "3", "5"])
        self.assertNotEqual(table.rows[0], table.headers)
        self.assertIn("| Award | Wins | Nominations |", table.markdown)
        self.assertIn("| Emmy Awards | 3 | 5 |", table.markdown)

    def test_table_extraction_drops_tables_with_more_than_40_rows_or_markdown_over_2500_chars(self) -> None:
        long_rows = "\n".join(
            f"<tr><td>Very long table row {index}</td><td>{'x' * 80}</td></tr>"
            for index in range(35)
        )
        many_rows = "\n".join(
            f"<tr><td>Row {index}</td><td>{index}</td></tr>"
            for index in range(41)
        )
        html = f"""
        <div class="mw-parser-output">
        <table class="wikitable">
        <tr><th>Name</th><th>Value</th></tr>
        <tr><td>Kept</td><td>1</td></tr>
        </table>
        <table class="wikitable">
        <tr><th>Name</th><th>Value</th></tr>
        {long_rows}
        </table>
        <table class="wikitable">
        <tr><th>Name</th><th>Value</th></tr>
        {many_rows}
        </table>
        </div>
        """

        tables = extract_wikipedia_tables(html)

        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0].table_index, 1)
        self.assertIn("| Kept | 1 |", tables[0].markdown)

    def test_infobox_colspan_rows_are_rendered_in_place_without_duplication(self) -> None:
        html = """
        <div class="mw-parser-output">
        <h2><span class="mw-headline" id="Formation">Formation</span></h2>
        <table class="infobox">
        <tr><th colspan="2">Great Western Railway Act 1835</th></tr>
        <tr><th colspan="2">Act of Parliament</th></tr>
        <tr><td colspan="2">Parliament of the United Kingdom</td></tr>
        <tr><th>Long title</th><td>An Act for making a Railway from Bristol.</td></tr>
        <tr><th>Citation</th><td>5 &amp; 6 Will. 4. c. cvii</td></tr>
        <tr><th colspan="2">Dates</th></tr>
        <tr><th>Royal assent</th><td>31 August 1835</td></tr>
        </table>
        </div>
        """

        table = extract_wikipedia_tables(html)[0]

        self.assertEqual(table.headers, ["Column 1", "Column 2"])
        self.assertIn("| Parliament of the United Kingdom |  |", table.markdown)
        self.assertIn("| Royal assent | 31 August 1835 |", table.markdown)
        self.assertNotIn("| Parliament of the United Kingdom | Parliament of the United Kingdom |", table.markdown)
        self.assertEqual(table.structure["full_width_heading_row_count"], 4)

    def test_wikitable_full_width_rows_are_context_without_shifting_partial_groups(self) -> None:
        html = """
        <div class="mw-parser-output">
        <table class="wikitable">
        <tr><th colspan="8">Japanese era names by period</th></tr>
        <tr><th colspan="8">538-1264</th></tr>
        <tr><th colspan="2">Asuka</th><th colspan="2">Heian</th><th colspan="2">Heian contd</th><th colspan="2">Kamakura contd</th></tr>
        <tr><td>645-650</td><td>Taika</td><td>806-810</td><td>Daido</td><td>964-968</td><td>Koho</td><td>1222-1224</td><td>Joo</td></tr>
        <tr><th colspan="2">Nara</th><td>854-857</td><td>Saiko</td><td>983-985</td><td>Eikan</td><th colspan="2">Kamakura</th></tr>
        <tr><td>715-717</td><td>Reiki</td><td>857-859</td><td>Tenan</td><td>985-987</td><td>Kanna</td><td>1185-1190</td><td>Bunji</td></tr>
        </table>
        </div>
        """

        table = extract_wikipedia_tables(html)[0]

        self.assertEqual(table.structure["full_width_heading_row_count"], 2)
        self.assertEqual(
            [row["text"] for row in table.structure["full_width_heading_rows"]],
            ["Japanese era names by period", "538-1264"],
        )
        self.assertNotIn("| Japanese era names by period | Japanese era names by period |", table.markdown)
        self.assertIn("| Japanese era names by period |  |  |  |  |  |  |  |", table.markdown)
        self.assertIn("| 538-1264 |  |  |  |  |  |  |  |", table.markdown)
        self.assertIn("| Asuka |  | Heian |  | Heian contd |  | Kamakura contd |  |", table.markdown)
        self.assertIn("| Nara |  | 854-857 | Saiko | 983-985 | Eikan | Kamakura |  |", table.markdown)
        self.assertIn("| 715-717 | Reiki | 857-859 | Tenan | 985-987 | Kanna | 1185-1190 | Bunji |", table.markdown)

    def test_table_extraction_strips_numeric_citation_markers_from_cells(self) -> None:
        html = """
        <div class="mw-parser-output">
        <table class="wikitable">
        <tr><th>Name [1]</th><th>Note [a]</th></tr>
        <tr><td>Alpha [ 23 ]</td><td>Kept note [a]</td></tr>
        </table>
        </div>
        """

        table = extract_wikipedia_tables(html)[0]

        self.assertIn("| Name | Note [a] |", table.markdown)
        self.assertIn("| Alpha | Kept note [a] |", table.markdown)
        self.assertNotIn("[ 23 ]", table.markdown)

    def test_table_extraction_suppresses_mw_parser_output_style_noise(self) -> None:
        html = """
        <div class="mw-parser-output">
        <style>.mw-parser-output .hlist{font-size:95%}</style>
        <p><style>.mw-parser-output .plainlist{margin-left:0}</style>Profile prose.</p>
        <table class="infobox">
        <tr><th colspan="2">Profile</th></tr>
        <tr><th>College</th><td><style>.mw-parser-output .nowrap{white-space:nowrap}</style>Gustavus Adolphus College</td></tr>
        <tr><th>Known for</th><td>Stable archive</td></tr>
        </table>
        </div>
        """

        table = extract_wikipedia_tables(html)[0]

        self.assertIn("Gustavus Adolphus College", table.markdown)
        self.assertNotIn(".mw-parser-output", table.markdown)
        self.assertNotIn(".mw-parser-output", table.normalized_text)
        self.assertEqual(extract_first_paragraph(html), "Profile prose.")

    def test_table_extraction_renders_complex_spanning_table_as_markdown(self) -> None:
        html = """
        <div class="mw-parser-output">
        <table class="wikitable">
        <caption>DVD releases of Curb Your Enthusiasm</caption>
        <tr><th rowspan="2">Season</th><th colspan="2">Release dates</th><th rowspan="2">Bonus features</th></tr>
        <tr><th>Region 1</th><th>Region 2</th></tr>
        <tr><td>1</td><td>January 13, 2004</td><td>May 17, 2004</td><td>Commentary by Larry David</td></tr>
        </table>
        </div>
        """

        table = extract_wikipedia_tables(html)[0]

        self.assertEqual(
            table.headers,
            ["Season", "Release dates / Region 1", "Release dates / Region 2", "Bonus features"],
        )
        self.assertIn(
            "| Season | Release dates / Region 1 | Release dates / Region 2 | Bonus features |",
            table.markdown,
        )
        self.assertIn("| 1 | January 13, 2004 | May 17, 2004 | Commentary by Larry David |", table.markdown)
        self.assertEqual(table.structure["span_cell_count"], 3)

    def test_table_extraction_preserves_empty_cells_in_markdown_alignment(self) -> None:
        html = """
        <div class="mw-parser-output">
        <table class="wikitable">
        <tr><th>Place Manner</th><th>Labial</th><th>Dental / Alveolar</th><th>Palatal</th><th>Velar</th><th>Glottal</th></tr>
        <tr><th>Nasal</th><td>m</td><td>n</td><td></td><td>ng</td><td></td></tr>
        </table>
        </div>
        """

        table = extract_wikipedia_tables(html)[0]

        self.assertEqual(table.rows[0], ["Nasal", "m", "n", "", "ng", ""])
        self.assertIn("| Nasal | m | n |  | ng |  |", table.markdown)
        self.assertEqual(table.structure["empty_cell_count"], 2)

    def test_table_extraction_captures_nearby_intro_paragraph(self) -> None:
        html = """
        <div class="mw-parser-output">
        <h2><span class="mw-headline" id="Songs">Songs</span></h2>
        <p>The following songs are covers recorded by artists other than the original band.</p>
        <table class="wikitable">
        <tr><th>Song</th><th>Artist</th></tr>
        <tr><td>Dandy</td><td>Herman's Hermits</td></tr>
        </table>
        </div>
        """

        table = extract_wikipedia_tables(html)[0]

        self.assertEqual(
            table.nearby_intro,
            "The following songs are covers recorded by artists other than the original band.",
        )
        self.assertIn("nearby_intro", table.to_metadata())

    def test_horizontal_companion_tables_are_marked_without_rejecting_following_vertical_table(self) -> None:
        html = """
        <div class="mw-parser-output">
        <h2><span class="mw-headline" id="WTA_Tour_finals">WTA Tour finals</span></h2>
        <h3><span class="mw-headline" id="Singles">Singles: 9 (8 titles, 1 runner-up)</span></h3>
        <table class="wikitable" style="float:left; margin-right:0.5em">
        <tr><th>Legend</th></tr>
        <tr><td>Grand Slam</td></tr>
        <tr><td>Tier I / Premier M &amp; 5 (1-0)</td></tr>
        <tr><td>Tier II / Premier (2-1)</td></tr>
        <tr><td>Tiers III &amp; IV / International (5-0)</td></tr>
        </table>
        <table class="wikitable" style="float:left; margin-right:0.5em">
        <tr><th>Finals by surface</th></tr>
        <tr><td>Hard (6-1)</td></tr>
        <tr><td>Grass (1-0)</td></tr>
        <tr><td>Carpet (1-0)</td></tr>
        </table>
        <table class="wikitable" style="float:left">
        <tr><th>Finals by setting</th></tr>
        <tr><td>Outdoor (7-1)</td></tr>
        <tr><td>Indoor (1-0)</td></tr>
        </table>
        <table class="wikitable sortable">
        <tr><th>Result</th><th>W-L</th><th>Date</th><th>Tournament</th><th>Tier</th><th>Surface</th><th>Opponent</th><th>Score</th></tr>
        <tr><td>Win</td><td>1-0</td><td>Sep 2006</td><td>Guangzhou Open, China</td><td>Tier III</td><td>Hard</td><td>Anabel Medina Garrigues</td><td>6-3, 6-4</td></tr>
        <tr><td>Win</td><td>2-0</td><td>Oct 2006</td><td>Kremlin Cup, Russia</td><td>Tier I</td><td>Carpet (i)</td><td>Nadia Petrova</td><td>6-4, 6-4</td></tr>
        </table>
        </div>
        """

        tables = extract_wikipedia_tables(html)

        self.assertEqual(len(tables), 4)
        self.assertEqual(tables[0].structure["horizontal_companion_group_size"], 3)
        self.assertEqual(tables[1].structure["horizontal_companion_group_size"], 3)
        self.assertEqual(tables[2].structure["horizontal_companion_group_size"], 3)
        self.assertNotIn("horizontal_companion_group_size", tables[3].structure)

        annotated = _annotate_table_filter_modes(
            [{"table": table, "score": 1.0, "reasons": []} for table in tables],
            ("no_horizontal_companion_tables",),
        )

        for row in annotated[:3]:
            self.assertIn(
                "no_horizontal_companion_tables:float_left;group_size=3",
                row["table_filter_rejection_reason"],
            )
        self.assertEqual(annotated[3]["table_filter_rejection_reason"], "")

    def test_table_ranking_prefers_structured_low_prose_leakage_tables(self) -> None:
        tables = extract_wikipedia_tables(FIXTURE_HTML)
        prose_text = extract_non_table_prose(FIXTURE_HTML)
        ranked = rank_wikipedia_tables(
            tables,
            first_paragraph="The 2026 FIFA World Cup is the 23rd FIFA World Cup.",
            prose_text=prose_text,
        )
        self.assertEqual(ranked[0]["table_index"], 2)
        self.assertNotIn("comparable_headers", ranked[0]["reasons"])
        self.assertIn("low_prose_leakage", ranked[0]["reasons"])

    def test_table_ranking_does_not_prefer_wikitable_by_type(self) -> None:
        rows = [
            ["Field", "Value"],
            ["Founded", "1912"],
            ["Architect", "Mabel Harris"],
            ["Style", "Art Deco"],
        ]
        infobox = WikipediaTable(
            table_index=1,
            table_type="infobox",
            section_heading="",
            caption="",
            nearby_intro="",
            headers=["Field", "Value"],
            rows=rows,
            row_dicts=[],
            normalized_text="Founded 1912 Architect Mabel Harris Style Art Deco",
        )
        wikitable = WikipediaTable(
            table_index=2,
            table_type="wikitable",
            section_heading="",
            caption="",
            nearby_intro="",
            headers=["Field", "Value"],
            rows=rows,
            row_dicts=[],
            normalized_text="Founded 1912 Architect Mabel Harris Style Art Deco",
        )

        ranked = rank_wikipedia_tables(
            [wikitable, infobox],
            first_paragraph="",
            prose_text="",
        )

        self.assertEqual(ranked[0]["table_type"], "infobox")
        self.assertEqual(ranked[0]["score"], ranked[1]["score"])
        self.assertNotIn("article_table", ranked[1]["reasons"])

    def test_table_ranking_no_longer_scores_by_row_count(self) -> None:
        short_table = WikipediaTable(
            table_index=1,
            table_type="wikitable",
            section_heading="",
            caption="",
            nearby_intro="",
            headers=["Name", "Value"],
            rows=[
                ["Alpha", "Archive"],
                ["Beta", "Stable"],
            ],
            row_dicts=[],
            normalized_text="Name Value Alpha Archive Beta Stable",
            structure={"row_count": 3},
        )
        long_table = WikipediaTable(
            table_index=2,
            table_type="wikitable",
            section_heading="",
            caption="",
            nearby_intro="",
            headers=["Name", "Value"],
            rows=[
                ["Alpha", "Archive"],
                ["Beta", "Stable"],
                ["Gamma", "Settled"],
                ["Delta", "Historic"],
                ["Epsilon", "Closed"],
            ],
            row_dicts=[],
            normalized_text="Name Value Alpha Archive Beta Stable Gamma Settled Delta Historic Epsilon Closed",
            structure={"row_count": 6},
        )

        ranked = rank_wikipedia_tables([long_table, short_table], first_paragraph="", prose_text="")

        self.assertEqual(ranked[0]["score"], ranked[1]["score"])
        self.assertEqual(ranked[0]["table_index"], 1)
        self.assertEqual(ranked[1]["table_index"], 2)
        self.assertNotIn("multi_row", ranked[0]["reasons"])
        self.assertNotIn("multi_row", ranked[1]["reasons"])
        self.assertNotIn("too_few_rows", ranked[0]["reasons"])
        self.assertNotIn("too_few_rows", ranked[1]["reasons"])

    def test_table_ranking_prefers_lower_prose_leakage_on_score_tie(self) -> None:
        high_leakage_table = WikipediaTable(
            table_index=1,
            table_type="wikitable",
            section_heading="",
            caption="",
            nearby_intro="",
            headers=["Name", "Value"],
            rows=[
                ["Bramley", "Cedar Hall"],
                ["Dunwich", "Elm Yard"],
            ],
            row_dicts=[],
            normalized_text="Name Value Bramley Cedar Hall Dunwich Elm Yard",
            structure={"row_count": 3},
        )
        low_leakage_table = WikipediaTable(
            table_index=2,
            table_type="wikitable",
            section_heading="",
            caption="",
            nearby_intro="",
            headers=["Name", "Value"],
            rows=[
                ["Lancaster", "Aster Hall"],
                ["Raventon", "Kestrel Yard"],
            ],
            row_dicts=[],
            normalized_text="Name Value Lancaster Aster Hall Raventon Kestrel Yard",
            structure={"row_count": 3},
        )

        ranked = rank_wikipedia_tables(
            [high_leakage_table, low_leakage_table],
            first_paragraph="",
            prose_text="Bramley and Cedar Hall are named in prose. Lancaster is also mentioned.",
        )

        self.assertEqual(ranked[0]["score"], ranked[1]["score"])
        self.assertEqual(ranked[0]["table_index"], 2)
        self.assertLess(
            ranked[0]["prose_leakage"]["leakage_rate"],
            ranked[1]["prose_leakage"]["leakage_rate"],
        )

    def test_table_ranking_applies_person_answer_type_bonus(self) -> None:
        person_table = WikipediaTable(
            table_index=1,
            table_type="wikitable",
            section_heading="",
            caption="",
            nearby_intro="",
            headers=["field", "value"],
            rows=[["architect", "Zyphor Qandrel"], ["style", "archive record"]],
            row_dicts=[],
            normalized_text="architect Zyphor Qandrel style archive record",
            structure={"row_count": 3},
        )
        plain_table = WikipediaTable(
            table_index=2,
            table_type="infobox",
            section_heading="",
            caption="",
            nearby_intro="",
            headers=["field", "value"],
            rows=[["material", "stonework"], ["style", "archive record"]],
            row_dicts=[],
            normalized_text="material stonework style archive record",
            structure={"row_count": 3},
        )

        ranked = rank_wikipedia_tables(
            [plain_table, person_table],
            first_paragraph="",
            prose_text="",
            answer_type_hints=("Person",),
        )
        by_index = {row["table_index"]: row for row in ranked}

        self.assertEqual(ranked[0]["table_index"], 1)
        self.assertEqual(by_index[1]["answer_type_score_bonus"], 1.0)
        self.assertIn("answer_type_score_bonus", by_index[1]["reasons"])
        self.assertEqual(by_index[1]["answer_type_score"]["hits"][0]["pair"], ["Zyphor", "Qandrel"])
        self.assertEqual(by_index[2]["answer_type_score_bonus"], 0.0)

        without_hints = rank_wikipedia_tables([person_table], first_paragraph="", prose_text="")
        self.assertEqual(without_hints[0]["answer_type_score_bonus"], 0.0)

    def test_table_ranking_applies_place_answer_type_bonus(self) -> None:
        table = WikipediaTable(
            table_index=1,
            table_type="infobox",
            section_heading="",
            caption="",
            nearby_intro="",
            headers=["field", "value"],
            rows=[["category", "river"], ["name", "silver reach"]],
            row_dicts=[],
            normalized_text="category river name silver reach",
            structure={"row_count": 3},
        )

        ranked = rank_wikipedia_tables(
            [table],
            first_paragraph="",
            prose_text="",
            answer_type_hints=("Place",),
        )

        self.assertEqual(ranked[0]["answer_type_score_bonus"], 2.0)
        self.assertIn("river", ranked[0]["answer_type_score"]["hits"][0]["markers"])
        self.assertIn("answer_type_score_bonus", ranked[0]["reasons"])

    def test_table_ranking_applies_date_answer_type_bonus(self) -> None:
        table = WikipediaTable(
            table_index=1,
            table_type="wikitable",
            section_heading="",
            caption="",
            nearby_intro="",
            headers=["field", "value"],
            rows=[["opened", "3/6/2026"], ["recorded", "March 1998"]],
            row_dicts=[],
            normalized_text="opened 3/6/2026 recorded March 1998",
            structure={"row_count": 3},
        )

        ranked = rank_wikipedia_tables(
            [table],
            first_paragraph="",
            prose_text="",
            answer_type_hints=("Date",),
        )

        self.assertEqual(ranked[0]["answer_type_score_bonus"], 2.0)
        self.assertIn("answer_type_score_bonus", ranked[0]["reasons"])
        self.assertEqual(ranked[0]["answer_type_score"]["hits"][0]["answer_type"], "Date")
        marker_rules = {
            marker["rule"]
            for marker in ranked[0]["answer_type_score"]["hits"][0]["markers"]
        }
        self.assertIn("month_name", marker_rules)
        self.assertIn("year_1500_2040_no_comma", marker_rules)
        self.assertIn("numeric_month_day_year", marker_rules)

    def test_table_ranking_ignores_multiple_answer_type_hints(self) -> None:
        table = WikipediaTable(
            table_index=1,
            table_type="wikitable",
            section_heading="",
            caption="",
            nearby_intro="",
            headers=["field", "value"],
            rows=[["opened", "3/6/2026"], ["recorded", "March 1998"]],
            row_dicts=[],
            normalized_text="opened 3/6/2026 recorded March 1998",
            structure={"row_count": 3},
        )

        ranked = rank_wikipedia_tables(
            [table],
            first_paragraph="",
            prose_text="",
            answer_type_hints=("Date", "Other"),
        )

        self.assertEqual(ranked[0]["answer_type_score_bonus"], 0.0)
        self.assertEqual(ranked[0]["answer_type_score"]["hints"], [])
        self.assertNotIn("answer_type_score_bonus", ranked[0]["reasons"])

    def test_prose_leakage_scoring_uses_light_default_thresholds(self) -> None:
        low_leak_table = WikipediaTable(
            table_index=1,
            table_type="wikitable",
            section_heading="",
            caption="",
            nearby_intro="",
            headers=["Name", "Value"],
            rows=[["Alpha", "Archive"], ["Beta", "Stable"]],
            row_dicts=[],
            normalized_text="Name Value Alpha Archive Beta Stable",
            structure={"row_count": 3},
        )
        high_leak_table = WikipediaTable(
            table_index=2,
            table_type="wikitable",
            section_heading="",
            caption="",
            nearby_intro="",
            headers=["Name", "Value"],
            rows=[["Gamma", "Historic"], ["Delta", "Settled"]],
            row_dicts=[],
            normalized_text="Name Value Gamma Historic Delta Settled",
            structure={"row_count": 3},
        )

        ranked = rank_wikipedia_tables(
            [low_leak_table, high_leak_table],
            first_paragraph="Gamma Historic Delta Settled",
            prose_text="",
        )
        by_index = {row["table_index"]: row for row in ranked}

        self.assertEqual(by_index[1]["score"], 1.5)
        self.assertIn("low_prose_leakage", by_index[1]["reasons"])
        self.assertEqual(by_index[1]["prose_leakage"]["low_score_bonus"], 0.5)
        self.assertEqual(by_index[2]["score"], 0.5)
        self.assertIn("high_prose_leakage", by_index[2]["reasons"])
        self.assertEqual(by_index[2]["prose_leakage"]["high_rate_threshold"], 0.8)

    def test_prose_leakage_scoring_can_be_disabled_without_losing_audit_stats(self) -> None:
        table = WikipediaTable(
            table_index=1,
            table_type="wikitable",
            section_heading="",
            caption="",
            nearby_intro="",
            headers=["Name", "Value"],
            rows=[["Gamma", "Historic"], ["Delta", "Settled"]],
            row_dicts=[],
            normalized_text="Name Value Gamma Historic Delta Settled",
            structure={"row_count": 3},
        )

        ranked = rank_wikipedia_tables(
            [table],
            first_paragraph="Gamma Historic Delta Settled",
            prose_text="",
            prose_leakage_scoring_enabled=False,
        )

        self.assertEqual(ranked[0]["score"], 1.0)
        self.assertNotIn("high_prose_leakage", ranked[0]["reasons"])
        self.assertEqual(ranked[0]["prose_leakage"]["leakage_rate"], 1.0)
        self.assertFalse(ranked[0]["prose_leakage"]["scoring_enabled"])

    def test_table_filter_hard_rejects_two_or_fewer_total_rows(self) -> None:
        table = WikipediaTable(
            table_index=1,
            table_type="wikitable",
            section_heading="",
            caption="",
            nearby_intro="",
            headers=["Name", "Value"],
            rows=[["Alpha", "Archive"]],
            row_dicts=[],
            normalized_text="Name Value Alpha Archive",
            structure={"row_count": 2},
        )

        annotated = _annotate_table_filter_modes(
            [{"table": table, "score": 1.0, "reasons": []}],
            (),
        )

        self.assertEqual(
            annotated[0]["table_filter_rejection_reason"],
            "too_few_rows:row_count=2;min_rows=3",
        )

    def test_current_scope_tables_are_rejected_before_llm_generation(self) -> None:
        class CurrentOnlyWikipediaClient(FakeWikipediaClient):
            def fetch_parse(self, title_or_url: str) -> dict:
                return {
                    "parse": {
                        "title": "King",
                        "text": """
                        <div class="mw-parser-output">
                        <p>King is a royal title.</p>
                        <h2><span class="mw-headline" id="Current_kings">Current kings</span></h2>
                        <table class="wikitable">
                        <tr><th>King</th><th>Since</th></tr>
                        <tr><td>Frederik X</td><td>14 January 2024</td></tr>
                        <tr><td>Carl XVI Gustaf</td><td>15 September 1973</td></tr>
                        </table>
                        </div>
                        """,
                    }
                }

        llm_client = FakeLLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/King"],
            wikipedia_client=CurrentOnlyWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
        )

        candidate = generator.generate(run_date="2026-05-19", cutoff_year=2025)[0]

        self.assertIn("wikipedia_infobox_live_table_scope", candidate.notes)
        self.assertEqual(llm_client.prompts, [])
        self.assertEqual(
            candidate.source_metadata["discard_reason"],
            "live_table_scope:section_heading:current",
        )

    def test_min_table_score_rejects_before_first_paragraph_context(self) -> None:
        llm_client = FakeLLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=FakeWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
            min_table_score=999.0,
            table_filter_modes=(),
        )

        candidate = generator.generate(run_date="2026-05-19", cutoff_year=2025)[0]

        self.assertIn("wikipedia_infobox_table_score_below_minimum", candidate.notes)
        self.assertEqual(llm_client.prompts, [])
        self.assertEqual(candidate.source_metadata["first_paragraph"], "")
        self.assertNotIn("first_paragraph_extract_seconds", candidate.source_metadata["phase_timings_seconds"])
        self.assertEqual(candidate.source_metadata["min_table_score"], 999.0)
        self.assertTrue(all(row["below_min_table_score"] for row in candidate.source_metadata["table_selection"]))
        self.assertIn("table_score_below_minimum:min_table_score=999.0000", candidate.source_metadata["discard_reason"])

    def test_fifa_fixture_generates_expected_candidate(self) -> None:
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=FakeWikipediaClient(),
            llm_client=FakeSingleFactLLMClient(),
            record_limit=1,
            url_domains={"https://en.wikipedia.org/wiki/2026_FIFA_World_Cup": "Sports"},
            table_filter_modes=(),
        )
        candidates = generator.generate(run_date="2026-05-16", cutoff_year=2025)
        self.assertEqual(len(candidates), 1)
        candidate = candidates[0]
        self.assertEqual(candidate.generation_route, "route3_wikipedia_infobox")
        self.assertEqual(candidate.final_question, "What edition is the FIFA World Cup described as the 23rd FIFA World Cup?")
        self.assertEqual(candidate.answer, "23rd")
        self.assertEqual(candidate.relation_or_claim, "single_fact")
        self.assertEqual(candidate.question_family, "wikipedia_infobox_table_fact")
        self.assertEqual(candidate.source_metadata["selected_source_table"]["caption"], "List of tournament venues")
        self.assertTrue(
            all(row["answer_type_score_bonus"] == 0.0 for row in candidate.source_metadata["table_selection"])
        )
        self.assertEqual(candidate.source_metadata["reasoning_type"], "single_fact")
        self.assertEqual(candidate.source_metadata["allowed_reasoning_types"], ["single_fact"])
        self.assertNotIn("composition_type", candidate.source_metadata)
        self.assertEqual(candidate.source_metadata["content_domain"], "Sports")
        self.assertIn("23rd FIFA World Cup", candidate.source_metadata["subject_anchor_aliases"])
        self.assertEqual(candidate.source_metadata["subject_anchors"]["page_title"], "2026 FIFA World Cup")
        self.assertIn("23rd FIFA World Cup", candidate.source_metadata["subject_anchors"]["safe_subject_aliases"])
        self.assertEqual(
            candidate.source_metadata["subject_anchors"]["table_scopes"][0]["table_title"],
            "List of tournament venues",
        )
        self.assertNotIn("top three ranked tables", generator.llm_client.prompts[0])
        self.assertIn("Use the provided top-ranked table as the only structured evidence table", generator.llm_client.prompts[0])
        self.assertIn("May 20, 2024", generator.llm_client.prompts[0])
        self.assertIn("May 2024", generator.llm_client.prompts[0])
        self.assertIn("specify the counted quantity or unit", generator.llm_client.prompts[0])
        self.assertIn("Do not add units to the reference answer", generator.llm_client.prompts[0])
        self.assertIn("### subject_anchors", generator.llm_client.prompts[0])
        self.assertIn("- `page title`:", generator.llm_client.prompts[0])
        self.assertIn("- `safe_subject_aliases`: 23rd FIFA World Cup", generator.llm_client.prompts[0])
        self.assertIn("### table context", generator.llm_client.prompts[0])
        self.assertIn("### table content", generator.llm_client.prompts[0])
        self.assertIn("- `section_heading`: Venues", generator.llm_client.prompts[0])
        self.assertIn("- `caption`: List of tournament venues", generator.llm_client.prompts[0])
        self.assertNotIn('"subject_anchors"', generator.llm_client.prompts[0])
        self.assertNotIn('"preferred_subject_anchors"', generator.llm_client.prompts[0])
        self.assertIn("If the page title contains a cutoff-year marker", generator.llm_client.prompts[0])
        self.assertIn("do not copy anchor text mechanically", generator.llm_client.prompts[0])
        self.assertIn("The question must be self-contained", generator.llm_client.prompts[0])
        self.assertIn("Treat curated list pages such as `List of national parks of the United States`", generator.llm_client.prompts[0])
        self.assertNotIn("For the 2026 FIFA World Cup page", generator.llm_client.prompts[0])
        self.assertIn("Do not ask cumulative-statistic questions", generator.llm_client.prompts[0])
        self.assertIn('"answer_type": "Person|Place|Number|Date|Other"', generator.llm_client.prompts[0])
        schema = generator.llm_client.prompts[0].partition("Output schema:\n")[2].partition("\n\nPayload:")[0]
        self.assertNotIn('"reasoning_type"', schema)
        self.assertNotIn('"source_table"', schema)
        self.assertIn("Use fixed `single_fact` reasoning", generator.llm_client.prompts[0])
        self.assertIn("Do not include a `reasoning_type` field", generator.llm_client.prompts[0])
        self.assertNotIn("allowed answer types ,", generator.llm_client.prompts[0])
        self.assertNotIn("allowed answer type .", generator.llm_client.prompts[0])
        self.assertIn("historically settled in the provided table content", generator.llm_client.prompts[0])
        self.assertIn("cannot change", generator.llm_client.prompts[0])
        self.assertFalse(candidate.source_metadata["llm_choose_table"])
        self.assertNotIn("wikitable or infobox", generator.llm_client.prompts[0])
        self.assertNotIn('"composition_type"', generator.llm_client.prompts[0])
        self.assertNotIn("preferred_subject_anchor exactly", generator.llm_client.prompts[0])
        self.assertNotIn("local, bounded facts", generator.llm_client.prompts[0])
        self.assertEqual(len(candidate.search_queries), 2)

    def test_subject_anchor_aliases_use_fixed_2025_cutoff_but_prompt_context_uses_run_cutoff(self) -> None:
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=FakeWikipediaClient(),
            llm_client=FakeSingleFactLLMClient(),
            record_limit=1,
            min_table_score=-999.0,
            table_filter_modes=(),
        )

        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2027)[0]

        self.assertNotIn("2026 FIFA World Cup", candidate.source_metadata["subject_anchor_aliases"])
        self.assertIn("23rd FIFA World Cup", candidate.source_metadata["subject_anchor_aliases"])
        self.assertEqual(candidate.source_metadata["subject_anchors"]["safe_page_title"], "2026 FIFA World Cup")

    def test_route3_passes_only_top_ranked_table_to_generation_llm_by_default(self) -> None:
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=FakeWikipediaClient(),
            llm_client=FakeLLMClient(),
            record_limit=1,
            allowed_reasoning_types=("max",),
            table_filter_modes=(),
        )

        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        prompt = generator.llm_client.prompts[0]
        payload = prompt.partition("Payload:\n")[2]
        schema = prompt.partition("Output schema:\n")[2].partition("\n\nPayload:")[0]

        self.assertFalse(candidate.source_metadata["llm_choose_table"])
        self.assertTrue(payload.startswith("### subject_anchors"))
        self.assertEqual(payload.count("### table content"), 1)
        self.assertIn("- `table_type`: wikitable", payload)
        self.assertNotIn("- `source_table`:", payload)
        self.assertNotIn('"tables"', payload)
        self.assertNotIn("table_selection_criteria", payload)
        self.assertNotIn('"source_table"', schema)
        self.assertNotIn("Choose from the top three ranked tables", prompt)
        self.assertNotIn("choose another table", prompt)
        self.assertIn("Generate one long-tail SimpleQA-style factual question from a Wikipedia wikitable.", prompt)
        self.assertNotIn("wikitable or infobox", prompt)
        self.assertIn("Use the provided top-ranked table as the only structured evidence table", prompt)
        self.assertIn("If the provided table is only a toy", prompt)

    def test_route3_can_let_llm_choose_among_ranked_tables(self) -> None:
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=FakeWikipediaClient(),
            llm_client=FakeSingleFactLLMClient(),
            record_limit=1,
            table_filter_modes=(),
            min_table_score=-999.0,
            llm_choose_table=True,
        )

        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        prompt = generator.llm_client.prompts[0]
        payload = prompt.partition("Payload:\n")[2]
        schema = prompt.partition("Output schema:\n")[2].partition("\n\nPayload:")[0]

        self.assertTrue(candidate.source_metadata["llm_choose_table"])
        self.assertGreaterEqual(payload.count("- `source_table`:"), 2)
        self.assertIn("- `table_type`: infobox", payload)
        self.assertIn("- `table_type`: wikitable", payload)
        self.assertIn('"source_table": integer', schema)
        self.assertIn("Choose from the top three ranked tables", prompt)
        self.assertIn("choose another table", prompt)
        self.assertIn("wikitable or infobox", prompt)

    def test_route3_can_restrict_generation_to_infobox_source_tables(self) -> None:
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=FakeWikipediaClient(),
            llm_client=FakeSingleFactLLMClient(),
            record_limit=1,
            table_filter_modes=(),
            min_table_score=-999.0,
            table_source_types=("infobox",),
        )

        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        prompt = generator.llm_client.prompts[0]
        payload = prompt.partition("Payload:\n")[2]

        self.assertEqual(candidate.source_metadata["table_source_types"], ["infobox"])
        self.assertEqual(candidate.source_metadata["selected_source_table"]["table_type"], "infobox")
        self.assertIn("Generate one long-tail SimpleQA-style factual question from a Wikipedia infobox.", prompt)
        self.assertIn("- `table_type`: infobox", payload)
        self.assertNotIn("- `section_heading`:", payload)
        self.assertNotIn("- `caption`:", payload)
        self.assertNotIn("- `nearby_intro`:", payload)
        self.assertNotIn("do not copy anchor text mechanically", prompt)
        self.assertNotIn("Treat curated list pages", prompt)

    def test_route3_can_restrict_generation_to_wikitable_source_tables(self) -> None:
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=FakeWikipediaClient(),
            llm_client=FakeLLMClient(),
            record_limit=1,
            table_filter_modes=(),
            table_source_types=("wikitable",),
        )

        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        prompt = generator.llm_client.prompts[0]
        payload = prompt.partition("Payload:\n")[2]

        self.assertEqual(candidate.source_metadata["table_source_types"], ["wikitable"])
        self.assertEqual(candidate.source_metadata["selected_source_table"]["table_type"], "wikitable")
        self.assertIn("Generate one long-tail SimpleQA-style factual question from a Wikipedia wikitable.", prompt)
        self.assertIn("- `table_type`: wikitable", payload)
        self.assertIn("- `section_heading`: Venues", payload)
        self.assertIn("- `caption`: List of tournament venues", payload)
        self.assertIn("do not copy anchor text mechanically", prompt)

    def test_all5_mode_returns_one_candidate_or_rejection_per_answer_type_slot(self) -> None:
        llm_client = FakeAll5LLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=FakeWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
            table_filter_modes=(),
            table_source_types=("infobox",),
            answer_type_mode="all5",
            pageview_prefilter_enabled=False,
        )

        candidates = generator.generate(run_date="2026-05-16", cutoff_year=2025)
        prompt = llm_client.prompts[0]
        schema = prompt.partition("Output schema:\n")[2].partition("\n\nPayload:")[0]
        payload = prompt.partition("Payload:\n")[2]

        self.assertEqual(len(llm_client.prompts), 1)
        self.assertIn("exactly five fixed answer-type slots", prompt)
        self.assertIn("Reject only that slot", prompt)
        self.assertIn("For each generated all5 slot", prompt)
        self.assertIn("Generate five fixed answer-type slots for long-tail SimpleQA-style factual questions from a Wikipedia infobox.", prompt)
        self.assertIn("### subject_anchors", payload)
        self.assertIn("### table context", payload)
        self.assertIn("### table content", payload)
        self.assertNotIn("Wikitable-only guidance", prompt)
        self.assertIn('"outputs"', schema)
        for answer_type in ("Person", "Place", "Number", "Date", "Other"):
            self.assertIn(f'"answer_type": "{answer_type}"', schema)
        self.assertNotIn('"answer_type": "Person|Place|Number|Date|Other"', schema)
        self.assertNotIn('"reasoning_type"', schema)
        self.assertNotIn('"source_table"', schema)
        self.assertEqual(len(candidates), 5)
        self.assertEqual(
            [candidate.source_metadata["route3_slot_id"] for candidate in candidates],
            ["Person", "Place", "Number", "Date", "Other"],
        )
        self.assertEqual([candidate.source_metadata["answer_type_mode"] for candidate in candidates], ["all5"] * 5)
        self.assertEqual(candidates[0].answer, "Jane Doe")
        self.assertIn("wikipedia_infobox_llm_discarded", candidates[1].notes)
        self.assertEqual(candidates[1].source_metadata["discard_reason"], "No stable place question is supported.")
        self.assertEqual(candidates[0].source_metadata["llm_response"]["answer_type"], "Person")
        self.assertIn("outputs", candidates[1].source_metadata["llm_audit"]["parsed_response"])

    def test_all5_mode_does_not_apply_answer_type_table_ranking_bonus(self) -> None:
        llm_client = FakeAll5LLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=FakeWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
            table_filter_modes=(),
            table_source_types=("infobox",),
            answer_type_mode="all5",
            allowed_answer_types=("Date",),
            pageview_prefilter_enabled=False,
        )

        candidates = generator.generate(run_date="2026-05-16", cutoff_year=2025)
        prompt = llm_client.prompts[0]
        schema = prompt.partition("Output schema:\n")[2].partition("\n\nPayload:")[0]

        self.assertEqual(len(candidates), 5)
        self.assertIn("Generate five fixed answer-type slots", prompt)
        self.assertNotIn('"source_table"', schema)
        self.assertIn('"answer_type": "Person"', schema)
        self.assertIn('"answer_type": "Date"', schema)
        self.assertNotIn("Use only `Date` answer_type", prompt)
        slot_positions = [
            schema.index(f'"answer_type": "{answer_type}"')
            for answer_type in ("Person", "Place", "Number", "Date", "Other")
        ]
        self.assertEqual(slot_positions, sorted(slot_positions))
        self.assertTrue(
            all(
                row["answer_type_score_bonus"] == 0.0
                for row in candidates[0].source_metadata["table_selection"]
            )
        )
        self.assertTrue(
            all(
                row["answer_type_score"]["hints"] == []
                for row in candidates[0].source_metadata["table_selection"]
            )
        )

    def test_all5_same_page_accepted_slots_are_not_subject_deduped(self) -> None:
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=FakeWikipediaClient(),
            llm_client=FakeAll5LLMClient(),
            record_limit=1,
            table_filter_modes=(),
            table_source_types=("infobox",),
            answer_type_mode="all5",
            pageview_prefilter_enabled=False,
        )
        candidates = generator.generate(run_date="2026-05-16", cutoff_year=2025)

        result = process_generated_candidates(
            candidates,
            settings=Settings(
                target_time="2024",
                pilot_total=5,
                cutoff_year=2025,
                duckduckgo_top_k=5,
                search_longtail_max_full_question_hit_rate=1.0,
                search_longtail_max_keyword_hit_rate=1.0,
                search_longtail_max_overall_hit_rate=1.0,
            ),
            search_client=FakeSearchClient(),
        )

        self.assertEqual(len(result.accepted), 2)
        self.assertEqual([record["answer_type"] for record in result.accepted], ["Person", "Date"])
        self.assertNotIn("duplicate_subject_resource", [record["rejection_reason"] for record in result.rejected])
        self.assertEqual(
            {record["source_metadata"]["route3_slot_id"] for record in result.accepted},
            {"Person", "Date"},
        )
        self.assertEqual(
            {record["subject_resource_key"] for record in result.accepted},
            {
                "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup#Person",
                "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup#Date",
            },
        )
        self.assertEqual(
            {record["subject_resource_url"] for record in result.accepted},
            {"https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"},
        )

    def test_route3_rejects_when_configured_source_type_is_absent(self) -> None:
        class InfoboxOnlyWikipediaClient(FakeWikipediaClient):
            def fetch_parse(self, title_or_url: str) -> dict:
                return {
                    "parse": {
                        "title": "Infobox only example",
                        "text": """
                        <div class="mw-parser-output">
                        <p>Infobox only example is a settled historical profile.</p>
                        <table class="infobox">
                        <tr><th colspan="2">Profile</th></tr>
                        <tr><th>Field</th><td>Archive</td></tr>
                        <tr><th>Known for</th><td>Stable record</td></tr>
                        </table>
                        </div>
                        """,
                    }
                }

        llm_client = FakeLLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/Infobox_only_example"],
            wikipedia_client=InfoboxOnlyWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
            table_source_types=("wikitable",),
        )

        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]

        self.assertIn("wikipedia_infobox_no_allowed_table_source_types", candidate.notes)
        self.assertEqual(llm_client.prompts, [])
        self.assertEqual(candidate.source_metadata["table_source_types"], ["wikitable"])
        self.assertIn("allowed=wikitable;available=infobox", candidate.source_metadata["discard_reason"])

    def test_route3_table_source_type_normalization_accepts_both_aliases(self) -> None:
        self.assertEqual(normalize_route3_table_source_types("both"), ("infobox", "wikitable"))
        self.assertEqual(normalize_route3_table_source_types(["infoboxes", "article_tables"]), ("infobox", "wikitable"))

    def test_route3_default_single_fact_reasoning_type_is_passed_through(self) -> None:
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=FakeWikipediaClient(),
            llm_client=FakeLLMClient(),
            record_limit=1,
            table_filter_modes=(),
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        prompt = generator.llm_client.prompts[0]
        schema = prompt.partition("Output schema:\n")[2].partition("\n\nPayload:")[0]
        self.assertIn("Use fixed `single_fact` reasoning", prompt)
        self.assertIn("do not ask a compositional question", prompt)
        self.assertIn("Do not include a `reasoning_type` field", prompt)
        self.assertNotIn('"reasoning_type"', schema)
        self.assertNotIn("wikipedia_infobox_reasoning_type_not_allowed", candidate.notes)
        self.assertEqual(candidate.source_metadata["reasoning_type"], "single_fact")
        self.assertEqual(candidate.relation_or_claim, "single_fact")
        self.assertEqual(candidate.source_metadata["allowed_reasoning_types"], ["single_fact"])

    def test_route3_ordinal_reasoning_type_restriction_prompts_for_temporal_ordinal(self) -> None:
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=FakeWikipediaClient(),
            llm_client=FakeLLMClient(),
            record_limit=1,
            allowed_reasoning_types=("ordinal",),
            table_filter_modes=(),
        )
        generator.generate(run_date="2026-05-16", cutoff_year=2025)
        prompt = generator.llm_client.prompts[0]
        schema = prompt.partition("Output schema:\n")[2].partition("\n\nPayload:")[0]
        self.assertIn("Use fixed `ordinal` reasoning", prompt)
        self.assertIn("temporal ordinal question", prompt)
        self.assertIn("first or second by date, time, or order of occurrence", prompt)
        self.assertIn("do not ask magnitude rankings", prompt)
        self.assertIn("largest or second largest", prompt)
        self.assertNotIn('"reasoning_type"', schema)

    def test_route3_multiple_reasoning_type_restriction_accepts_allowed_output(self) -> None:
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=FakeWikipediaClient(),
            llm_client=FakeLLMClient(),
            record_limit=1,
            allowed_reasoning_types=("single_fact", "max"),
            table_filter_modes=(),
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        self.assertNotIn("wikipedia_infobox_reasoning_type_not_allowed", candidate.notes)
        self.assertEqual(candidate.source_metadata["reasoning_type"], "max")
        self.assertEqual(candidate.source_metadata["allowed_reasoning_types"], ["single_fact", "max"])
        prompt = generator.llm_client.prompts[0]
        self.assertIn('"reasoning_type": "single_fact|max"', prompt)
        self.assertIn("Use only these reasoning_type values: `single_fact`, `max`", prompt)
        self.assertIn("`single_fact`: ask a direct single fact lookup", prompt)
        self.assertIn("`max`: ask for the row or value with the largest value", prompt)
        self.assertNotIn("`ordinal`: ask a temporal ordinal question", prompt)

    def test_route3_person_answer_type_restriction_prompts_and_accepts_person_output(self) -> None:
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=FakeWikipediaClient(),
            llm_client=FakePersonLLMClient(),
            record_limit=1,
            allowed_reasoning_types=("single_fact",),
            allowed_answer_types=("Person",),
            extra_prompts=("no_social_science_research_prompt",),
            table_filter_modes=(),
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        prompt = generator.llm_client.prompts[0]
        self.assertEqual(candidate.answer_type, "Person")
        self.assertEqual(candidate.source_metadata["allowed_answer_types"], ["Person"])
        self.assertTrue(
            any(row["answer_type_score"]["hints"] == ["Person"] for row in candidate.source_metadata["table_selection"])
        )
        self.assertIn("Use only `Person` answer_type", prompt)
        self.assertIn('"answer_type": "Person"', prompt)
        self.assertIn("Ask factual questions, not questions about the findings", prompt)
        self.assertIn("social science research", "\n".join(candidate.source_metadata["extra_prompts"]).lower())

    def test_route3_single_date_answer_type_restriction_applies_table_ranking_bonus(self) -> None:
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=FakeWikipediaClient(),
            llm_client=FakeSingleFactLLMClient(),
            record_limit=1,
            allowed_reasoning_types=("single_fact",),
            allowed_answer_types=("Date",),
            table_filter_modes=(),
        )

        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]

        self.assertTrue(
            any(row["answer_type_score_bonus"] == 2.0 for row in candidate.source_metadata["table_selection"])
        )
        self.assertTrue(
            any(row["answer_type_score"]["hints"] == ["Date"] for row in candidate.source_metadata["table_selection"])
        )

    def test_route3_other_answer_type_prompt_excludes_numeric_and_date_guidance(self) -> None:
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=FakeWikipediaClient(),
            llm_client=FakeSingleFactLLMClient(),
            record_limit=1,
            allowed_reasoning_types=("single_fact",),
            allowed_answer_types=("Other",),
            table_filter_modes=(),
        )
        generator.generate(run_date="2026-05-16", cutoff_year=2025)
        prompt = generator.llm_client.prompts[0]
        self.assertIn("Use only `Other` answer_type", prompt)
        self.assertIn("Use only `Other` answer_type: answer must not be a person, place, number, or date", prompt)
        self.assertIn("exclude numeric measurements, percentages, counts", prompt)
        self.assertNotIn("specify the counted quantity or unit", prompt)
        self.assertNotIn("Do not add units to the reference answer", prompt)
        self.assertNotIn("May 20, 2024", prompt)
        self.assertNotIn("May 2024", prompt)

    def test_route3_multiple_answer_type_restriction_lists_each_allowed_type_rule(self) -> None:
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=FakeWikipediaClient(),
            llm_client=FakeSingleFactLLMClient(),
            record_limit=1,
            allowed_reasoning_types=("single_fact",),
            allowed_answer_types=("Date", "Other"),
            table_filter_modes=(),
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        prompt = generator.llm_client.prompts[0]
        self.assertIn("Use only these answer_type values: `Date`, `Other`", prompt)
        self.assertIn("`Date`: answer must be a date, a month, or a year", prompt)
        self.assertIn("`Other`: answer must not be a person, place, number, or date", prompt)
        self.assertNotIn("`Number`: answer must be numeric", prompt)
        self.assertTrue(
            all(row["answer_type_score_bonus"] == 0.0 for row in candidate.source_metadata["table_selection"])
        )
        self.assertTrue(
            all(row["answer_type_score"]["hints"] == [] for row in candidate.source_metadata["table_selection"])
        )

    def test_route3_answer_type_restriction_rejects_disallowed_output(self) -> None:
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=FakeWikipediaClient(),
            llm_client=FakeLLMClient(),
            record_limit=1,
            allowed_answer_types=("Person",),
            table_filter_modes=(),
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        self.assertIn("wikipedia_infobox_answer_type_not_allowed", candidate.notes)
        self.assertIn("answer_type_not_allowed:Other; allowed=Person", candidate.source_metadata["discard_reason"])

    def test_no_social_science_mode_rejects_table_before_llm_generation(self) -> None:
        class PopulationWikipediaClient(FakeWikipediaClient):
            def fetch_parse(self, title_or_url: str) -> dict:
                return {
                    "parse": {
                        "title": "Population example",
                        "text": """
                        <div class="mw-parser-output">
                        <p>Population example is a settled historical list.</p>
                        <table class="wikitable">
                        <tr><th>Venue</th><th>City</th><th>Population</th></tr>
                        <tr><td>Alpha</td><td>Arlington</td><td>800</td></tr>
                        <tr><td>Beta</td><td>East Rutherford</td><td>825</td></tr>
                        </table>
                        </div>
                        """,
                    }
                }

        llm_client = FakePersonLLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/Population_example"],
            wikipedia_client=PopulationWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
            allowed_reasoning_types=("single_fact",),
            allowed_answer_types=("Person",),
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        self.assertIn("wikipedia_infobox_table_filter_rejected", candidate.notes)
        self.assertEqual(llm_client.prompts, [])
        self.assertIn("no_social_science_research:population", candidate.source_metadata["discard_reason"])
        self.assertEqual(
            candidate.source_metadata["table_filter_modes"],
            [
                "no_external_links_tables",
                "no_horizontal_companion_tables",
                "no_picture_heavy_tables",
                "no_incomplete_tables",
                "not_number_dominant",
                "no_social_science_research",
            ],
        )

    def test_external_links_tables_are_rejected_before_llm_generation(self) -> None:
        class ExternalLinksWikipediaClient(FakeWikipediaClient):
            def fetch_parse(self, title_or_url: str) -> dict:
                return {
                    "parse": {
                        "title": "External links example",
                        "text": """
                        <div class="mw-parser-output">
                        <p>External links example is a settled historical profile.</p>
                        <h2><span class="mw-headline" id="External_links">External links</span></h2>
                        <table class="wikitable">
                        <tr><th>Name</th><th>Value</th></tr>
                        <tr><td>Alpha</td><td>Settled</td></tr>
                        <tr><td>Beta</td><td>Archived</td></tr>
                        <tr><td>Gamma</td><td>Stable</td></tr>
                        </table>
                        </div>
                        """,
                    }
                }

        llm_client = FakeLLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/External_links_example"],
            wikipedia_client=ExternalLinksWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        self.assertIn("wikipedia_infobox_table_filter_rejected", candidate.notes)
        self.assertEqual(llm_client.prompts, [])
        self.assertIn(
            "no_external_links_tables:external_links_section",
            candidate.source_metadata["discard_reason"],
        )

    def test_no_incomplete_tables_mode_rejects_unknown_markers_before_llm_generation(self) -> None:
        class UnknownWikipediaClient(FakeWikipediaClient):
            def fetch_parse(self, title_or_url: str) -> dict:
                return {
                    "parse": {
                        "title": "Unknown example",
                        "text": """
                        <div class="mw-parser-output">
                        <p>Unknown example is a settled historical list.</p>
                        <table class="wikitable">
                        <tr><th>Name</th><th>Status</th></tr>
                        <tr><td>Alpha</td><td>Unknown</td></tr>
                        <tr><td>Beta</td><td>Known</td></tr>
                        </table>
                        </div>
                        """,
                    }
                }

        llm_client = FakeLLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/Unknown_example"],
            wikipedia_client=UnknownWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        self.assertIn("wikipedia_infobox_table_filter_rejected", candidate.notes)
        self.assertEqual(llm_client.prompts, [])
        self.assertIn("no_incomplete_tables:unknown", candidate.source_metadata["discard_reason"])
        self.assertIn("unknown", candidate.source_metadata["table_selection"][0]["incomplete_table_markers"])

    def test_no_incomplete_tables_mode_can_be_disabled(self) -> None:
        class UnknownWikipediaClient(FakeWikipediaClient):
            def fetch_parse(self, title_or_url: str) -> dict:
                return {
                    "parse": {
                        "title": "Unknown example",
                        "text": """
                        <div class="mw-parser-output">
                        <p>Unknown example is a settled historical list.</p>
                        <table class="wikitable">
                        <tr><th>Name</th><th>Status</th></tr>
                        <tr><td>Alpha</td><td>Unknown</td></tr>
                        <tr><td>Beta</td><td>Known</td></tr>
                        </table>
                        </div>
                        """,
                    }
                }

        llm_client = FakeLLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/Unknown_example"],
            wikipedia_client=UnknownWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
            table_filter_modes=("not_number_dominant", "no_social_science_research"),
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        self.assertNotIn("wikipedia_infobox_table_filter_rejected", candidate.notes)
        self.assertEqual(len(llm_client.prompts), 1)

    def test_no_picture_heavy_tables_mode_rejects_any_wikitable_image_before_llm_generation(self) -> None:
        class PictureWikipediaClient(FakeWikipediaClient):
            def fetch_parse(self, title_or_url: str) -> dict:
                return {
                    "parse": {
                        "title": "Picture example",
                        "text": """
                        <div class="mw-parser-output">
                        <p>Picture example is a settled historical list.</p>
                        <table class="wikitable">
                        <tr><th>Name</th><th>Role</th><th>Notes</th><th>Portrait</th></tr>
                        <tr><td>Alpha</td><td>Chair</td><td>Settled</td><td><img src="alpha.jpg" alt="Alpha"></td></tr>
                        <tr><td>Beta</td><td>Archivist</td><td>Stable</td><td>None</td></tr>
                        </table>
                        </div>
                        """,
                    }
                }

        llm_client = FakeLLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/Picture_example"],
            wikipedia_client=PictureWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        self.assertIn("wikipedia_infobox_table_filter_rejected", candidate.notes)
        self.assertEqual(llm_client.prompts, [])
        self.assertIn(
            "no_picture_heavy_tables:wikitable_image_cell_count=1",
            candidate.source_metadata["discard_reason"],
        )
        self.assertEqual(
            candidate.source_metadata["table_selection"][0]["picture_heavy_table_stats"]["image_covered_cell_count"],
            1,
        )

    def test_no_picture_heavy_tables_mode_drops_infobox_image_rows_before_generation(self) -> None:
        class SparseInfoboxImageWikipediaClient(FakeWikipediaClient):
            def fetch_parse(self, title_or_url: str) -> dict:
                return {
                    "parse": {
                        "title": "Sparse infobox image example",
                        "text": """
                        <div class="mw-parser-output">
                        <p>Sparse infobox image example is a settled historical profile.</p>
                        <table class="infobox">
                        <tr><th colspan="2">Profile</th></tr>
                        <tr><td colspan="2"><img src="alpha.jpg" alt="Alpha"></td></tr>
                        <tr><th>Role</th><td>Stable office</td></tr>
                        <tr><th>Known for</th><td>Archive record</td></tr>
                        </table>
                        </div>
                        """,
                    }
                }

        llm_client = FakeLLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/Sparse_infobox_image_example"],
            wikipedia_client=SparseInfoboxImageWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        self.assertIn("wikipedia_infobox_table_filter_rejected", candidate.notes)
        self.assertEqual(llm_client.prompts, [])
        selection = candidate.source_metadata["table_selection"][0]
        filtering = selection["infobox_row_filtering"]
        self.assertEqual(filtering["removed_row_count"], 1)
        self.assertIn("no_picture_heavy_tables:image_row", filtering["removed_reasons"])
        self.assertEqual(filtering["remaining_row_count"], 3)
        self.assertTrue(filtering["remaining_rows_below_minimum"])
        self.assertIn("infobox_remaining_rows_lt_min", candidate.source_metadata["discard_reason"])
        self.assertEqual(
            filtering["original_picture_heavy_table_stats"]["non_title_image_cell_rate"],
            0.3333,
        )

    def test_infobox_image_cleanup_removes_media_captions_without_dropping_location_rows(self) -> None:
        html = """
        <div class="mw-parser-output">
        <table class="infobox">
        <tr><th colspan="2">Shanghai Disneyland</th></tr>
        <tr><td colspan="2" class="infobox-image"><img src="logo.png"></td></tr>
        <tr><td colspan="2" class="infobox-image"><img src="castle.jpg"></td></tr>
        <tr><td colspan="2" class="infobox-caption">The Enchanted Storybook Castle, landmark of Shanghai Disneyland</td></tr>
        <tr><td colspan="2" class="infobox-full-data"><img src="map.png"></td></tr>
        <tr><td colspan="2" class="infobox-caption">Interactive map of Shanghai Disneyland</td></tr>
        <tr><th>Location</th><td>Shanghai Disney Resort, Pudong, Shanghai, China</td></tr>
        <tr><th>Opened</th><td>June 16, 2016</td></tr>
        </table>
        </div>
        """

        table = extract_wikipedia_tables(html)[0]
        annotated = _annotate_table_filter_modes([{"table": table}], ("no_picture_heavy_tables",))
        cleaned = annotated[0]["table"]
        filtering = cleaned.structure["infobox_row_filtering"]

        self.assertIn(["Location", "Shanghai Disney Resort, Pudong, Shanghai, China"], cleaned.rows)
        self.assertIn(["Opened", "June 16, 2016"], cleaned.rows)
        self.assertNotIn(["The Enchanted Storybook Castle, landmark of Shanghai Disneyland", ""], cleaned.rows)
        self.assertNotIn(["Interactive map of Shanghai Disneyland", ""], cleaned.rows)
        self.assertEqual(filtering["removed_row_count"], 5)
        self.assertIn("no_picture_heavy_tables:image_row", filtering["removed_reasons"])
        self.assertIn("no_picture_heavy_tables:image_caption_row", filtering["removed_reasons"])

    def test_infobox_image_cleanup_removes_portrait_caption_and_signature_title(self) -> None:
        html = """
        <div class="mw-parser-output">
        <table class="infobox">
        <tr><th colspan="2">Rosa Parks</th></tr>
        <tr><td colspan="2" class="infobox-image"><img src="portrait.jpg"></td></tr>
        <tr><td colspan="2" class="infobox-caption">Parks in 1956</td></tr>
        <tr><th>Born</th><td>Rosa Louise McCauley</td></tr>
        <tr><th>Known for</th><td>Montgomery bus boycott</td></tr>
        <tr><th colspan="2" class="infobox-header">Signature</th></tr>
        <tr><td colspan="2" class="infobox-full-data"><img src="signature.svg"></td></tr>
        </table>
        </div>
        """

        table = extract_wikipedia_tables(html)[0]
        annotated = _annotate_table_filter_modes([{"table": table}], ("no_picture_heavy_tables",))
        cleaned = annotated[0]["table"]
        filtering = cleaned.structure["infobox_row_filtering"]

        self.assertIn(["Born", "Rosa Louise McCauley"], cleaned.rows)
        self.assertIn(["Known for", "Montgomery bus boycott"], cleaned.rows)
        self.assertNotIn(["Parks in 1956", ""], cleaned.rows)
        self.assertNotIn(["Signature", ""], cleaned.rows)
        self.assertEqual(filtering["removed_row_count"], 4)
        self.assertIn("no_picture_heavy_tables:image_caption_row", filtering["removed_reasons"])
        self.assertIn("no_picture_heavy_tables:image_title_row", filtering["removed_reasons"])

    def test_infobox_image_cleanup_keeps_unclassed_section_heading_after_image(self) -> None:
        html = """
        <div class="mw-parser-output">
        <table class="infobox">
        <tr><th colspan="2">Profile</th></tr>
        <tr><td colspan="2" class="infobox-image"><img src="portrait.jpg"></td></tr>
        <tr><th colspan="2">Visitor information</th></tr>
        <tr><th>Location</th><td>Archive Hall</td></tr>
        <tr><th>Opened</th><td>1994</td></tr>
        </table>
        </div>
        """

        table = extract_wikipedia_tables(html)[0]
        annotated = _annotate_table_filter_modes([{"table": table}], ("no_picture_heavy_tables",))
        cleaned = annotated[0]["table"]
        filtering = cleaned.structure["infobox_row_filtering"]

        self.assertIn(["Visitor information", ""], cleaned.rows)
        self.assertIn(["Location", "Archive Hall"], cleaned.rows)
        self.assertEqual(filtering["removed_row_count"], 1)
        self.assertNotIn("no_picture_heavy_tables:image_caption_row", filtering["removed_reasons"])

    def test_infobox_image_rows_are_removed_before_remaining_row_count_check(self) -> None:
        class DenseInfoboxImageWikipediaClient(FakeWikipediaClient):
            def fetch_parse(self, title_or_url: str) -> dict:
                return {
                    "parse": {
                        "title": "Dense infobox image example",
                        "text": """
                        <div class="mw-parser-output">
                        <p>Dense infobox image example is a settled historical profile.</p>
                        <table class="infobox">
                        <tr><th colspan="2">Profile</th></tr>
                        <tr><td colspan="2"><img src="alpha.jpg" alt="Alpha"></td></tr>
                        <tr><td colspan="2"><img src="beta.jpg" alt="Beta"></td></tr>
                        <tr><th>Role</th><td>Stable office</td></tr>
                        </table>
                        </div>
                        """,
                    }
                }

        llm_client = FakeLLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/Dense_infobox_image_example"],
            wikipedia_client=DenseInfoboxImageWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        self.assertIn("wikipedia_infobox_table_filter_rejected", candidate.notes)
        self.assertEqual(llm_client.prompts, [])
        self.assertEqual(
            candidate.source_metadata["discard_reason"],
            "infobox_remaining_rows_lt_min:remaining_non_header_rows=2;min=5",
        )
        filtering = candidate.source_metadata["table_selection"][0]["infobox_row_filtering"]
        self.assertEqual(filtering["removed_row_count"], 2)
        self.assertTrue(filtering["remaining_rows_below_minimum"])
        self.assertIn("no_picture_heavy_tables:image_row", filtering["removed_reasons"])
        self.assertEqual(
            filtering["original_picture_heavy_table_stats"]["non_title_image_cell_rate"],
            0.6667,
        )

    def test_infobox_quality_filters_remove_bad_key_value_rows_before_generation(self) -> None:
        class MixedQualityInfoboxWikipediaClient(FakeWikipediaClient):
            def fetch_parse(self, title_or_url: str) -> dict:
                return {
                    "parse": {
                        "title": "Mixed quality infobox example",
                        "text": """
                        <div class="mw-parser-output">
                        <p>Mixed quality infobox example is a settled historical profile.</p>
                        <table class="infobox">
                        <tr><th colspan="2">Profile</th></tr>
                        <tr><td colspan="2"><img src="alpha.jpg" alt="Alpha"></td></tr>
                        <tr><th>Population</th><td>Archive group</td></tr>
                        <tr><th>Status</th><td>Unknown</td></tr>
                        <tr><th>Capacity</th><td>80,000</td></tr>
                        <tr><th>Role</th><td>Stable office</td></tr>
                        <tr><th>Founded</th><td>1986</td></tr>
                        <tr><th>Location</th><td>Archive Hall</td></tr>
                        <tr><th>Method</th><td>Curated register</td></tr>
                        <tr><th>Series</th><td>Reference file</td></tr>
                        </table>
                        </div>
                        """,
                    }
                }

        llm_client = FakeLLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/Mixed_quality_infobox_example"],
            wikipedia_client=MixedQualityInfoboxWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
            table_source_types=("infobox",),
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        self.assertNotIn("wikipedia_infobox_table_filter_rejected", candidate.notes)
        self.assertEqual(len(llm_client.prompts), 1)
        filtering = candidate.source_metadata["table_selection"][0]["infobox_row_filtering"]
        self.assertEqual(filtering["removed_row_count"], 4)
        self.assertIn("no_picture_heavy_tables:image_row", filtering["removed_reasons"])
        self.assertIn("no_social_science_research:population", filtering["removed_reasons"])
        self.assertIn("no_incomplete_tables:unknown", filtering["removed_reasons"])
        self.assertIn("not_number_dominant:comma_number_count=1", filtering["removed_reasons"])
        self.assertEqual(
            candidate.source_metadata["selected_source_table"]["rows"],
            [
                ["Profile", ""],
                ["Role", "Stable office"],
                ["Founded", "1986"],
                ["Location", "Archive Hall"],
                ["Method", "Curated register"],
                ["Series", "Reference file"],
            ],
        )

    def test_no_incomplete_tables_mode_rejects_precision_and_citation_markers_before_llm_generation(self) -> None:
        class ApproximateWikipediaClient(FakeWikipediaClient):
            def fetch_parse(self, title_or_url: str) -> dict:
                return {
                    "parse": {
                        "title": "Approximate example",
                        "text": """
                        <div class="mw-parser-output">
                        <p>Approximate example is a settled historical list.</p>
                        <table class="wikitable">
                        <tr><th>Name</th><th>Approx. status</th></tr>
                        <tr><td>Alpha</td><td>Approximate status</td></tr>
                        <tr><td>Beta</td><td>Approximately recorded</td></tr>
                        <tr><td>Gamma</td><td>[ citation needed ]</td></tr>
                        <tr><td>Delta</td><td>Citing needed</td></tr>
                        </table>
                        </div>
                        """,
                    }
                }

        llm_client = FakeLLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/Approximate_example"],
            wikipedia_client=ApproximateWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        self.assertIn("wikipedia_infobox_table_filter_rejected", candidate.notes)
        self.assertEqual(llm_client.prompts, [])
        self.assertIn(
            "no_incomplete_tables:approx.,approximate,approximately,citation needed,citing needed",
            candidate.source_metadata["discard_reason"],
        )
        self.assertEqual(
            candidate.source_metadata["table_selection"][0]["incomplete_table_markers"],
            ["approx.", "approximate", "approximately", "citation needed", "citing needed"],
        )

    def test_not_number_dominant_mode_rejects_comma_grouped_numbers_before_llm_generation(self) -> None:
        class BigNumberWikipediaClient(FakeWikipediaClient):
            def fetch_parse(self, title_or_url: str) -> dict:
                return {
                    "parse": {
                        "title": "Big number example",
                        "text": """
                        <div class="mw-parser-output">
                        <p>Big number example is a settled historical list.</p>
                        <table class="wikitable">
                        <tr><th>Venue</th><th>City</th><th>Capacity</th></tr>
                        <tr><td>AT&amp;T Stadium</td><td>Arlington</td><td>80,000</td></tr>
                        <tr><td>MetLife Stadium</td><td>East Rutherford</td><td>82,500</td></tr>
                        </table>
                        </div>
                        """,
                    }
                }

        llm_client = FakeLLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/Big_number_example"],
            wikipedia_client=BigNumberWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        self.assertIn("wikipedia_infobox_table_filter_rejected", candidate.notes)
        self.assertEqual(llm_client.prompts, [])
        self.assertIn("not_number_dominant:comma_number_count=2", candidate.source_metadata["discard_reason"])
        self.assertEqual(
            candidate.source_metadata["table_selection"][0]["number_dominance_stats"]["comma_number_count"],
            2,
        )

    def test_not_number_dominant_mode_does_not_reject_year_heavy_tables(self) -> None:
        class YearTableWikipediaClient(FakeWikipediaClient):
            def fetch_parse(self, title_or_url: str) -> dict:
                return {
                    "parse": {
                        "title": "Year example",
                        "text": """
                        <div class="mw-parser-output">
                        <p>Year example is a settled historical list.</p>
                        <table class="wikitable">
                        <tr><th>Event</th><th>Year</th></tr>
                        <tr><td>Gamma</td><td>1500</td></tr>
                        <tr><td>Alpha</td><td>1998</td></tr>
                        <tr><td>Beta</td><td>2004</td></tr>
                        <tr><td>Delta</td><td>2040</td></tr>
                        </table>
                        </div>
                        """,
                    }
                }

        llm_client = FakeLLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/Year_example"],
            wikipedia_client=YearTableWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        self.assertNotIn("wikipedia_infobox_table_filter_rejected", candidate.notes)
        self.assertEqual(len(llm_client.prompts), 1)
        self.assertEqual(
            candidate.source_metadata["table_selection"][0]["number_dominance_stats"][
                "out_of_allowed_no_comma_range_count"
            ],
            0,
        )
        self.assertEqual(
            candidate.source_metadata["table_selection"][0]["number_dominance_stats"]["numeric_token_count"],
            4,
        )

    def test_not_number_dominant_mode_rejects_no_comma_number_between_1000_and_1500(self) -> None:
        class ThresholdWikipediaClient(FakeWikipediaClient):
            def fetch_parse(self, title_or_url: str) -> dict:
                return {
                    "parse": {
                        "title": "Threshold example",
                        "text": """
                        <div class="mw-parser-output">
                        <p>Threshold example is a settled historical list.</p>
                        <table class="wikitable">
                        <tr><th>Name</th><th>Score</th></tr>
                        <tr><td>Alpha</td><td>999</td></tr>
                        <tr><td>Beta</td><td>1001</td></tr>
                        </table>
                        </div>
                        """,
                    }
                }

        llm_client = FakeLLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/Threshold_example"],
            wikipedia_client=ThresholdWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        self.assertIn("wikipedia_infobox_table_filter_rejected", candidate.notes)
        self.assertEqual(llm_client.prompts, [])
        self.assertIn(
            "not_number_dominant:out_of_allowed_no_comma_range_count=1",
            candidate.source_metadata["discard_reason"],
        )

    def test_not_number_dominant_mode_rejects_comma_separated_year_like_number(self) -> None:
        class CommaYearWikipediaClient(FakeWikipediaClient):
            def fetch_parse(self, title_or_url: str) -> dict:
                return {
                    "parse": {
                        "title": "Comma year example",
                        "text": """
                        <div class="mw-parser-output">
                        <p>Comma year example is a settled historical list.</p>
                        <table class="wikitable">
                        <tr><th>Name</th><th>Value</th></tr>
                        <tr><td>Alpha</td><td>2,024</td></tr>
                        <tr><td>Beta</td><td>2023</td></tr>
                        </table>
                        </div>
                        """,
                    }
                }

        llm_client = FakeLLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/Comma_year_example"],
            wikipedia_client=CommaYearWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        self.assertIn("wikipedia_infobox_table_filter_rejected", candidate.notes)
        self.assertEqual(llm_client.prompts, [])
        self.assertIn("not_number_dominant:comma_number_count=1", candidate.source_metadata["discard_reason"])

    def test_not_number_dominant_mode_rejects_no_comma_number_above_2040(self) -> None:
        class FutureYearWikipediaClient(FakeWikipediaClient):
            def fetch_parse(self, title_or_url: str) -> dict:
                return {
                    "parse": {
                        "title": "Future year example",
                        "text": """
                        <div class="mw-parser-output">
                        <p>Future year example is a settled historical list.</p>
                        <table class="wikitable">
                        <tr><th>Name</th><th>Year</th></tr>
                        <tr><td>Alpha</td><td>2041</td></tr>
                        <tr><td>Beta</td><td>2023</td></tr>
                        </table>
                        </div>
                        """,
                    }
                }

        llm_client = FakeLLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/Future_year_example"],
            wikipedia_client=FutureYearWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        self.assertIn("wikipedia_infobox_table_filter_rejected", candidate.notes)
        self.assertEqual(llm_client.prompts, [])
        self.assertIn(
            "not_number_dominant:out_of_allowed_no_comma_range_count=1",
            candidate.source_metadata["discard_reason"],
        )

    def test_not_number_dominant_mode_rejects_decimal_numbers(self) -> None:
        class DecimalWikipediaClient(FakeWikipediaClient):
            def fetch_parse(self, title_or_url: str) -> dict:
                return {
                    "parse": {
                        "title": "Decimal example",
                        "text": """
                        <div class="mw-parser-output">
                        <p>Decimal example is a settled historical list.</p>
                        <table class="wikitable">
                        <tr><th>Name</th><th>Ratio</th></tr>
                        <tr><td>Alpha</td><td>1.2</td></tr>
                        <tr><td>Beta</td><td>2</td></tr>
                        </table>
                        </div>
                        """,
                    }
                }

        llm_client = FakeLLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/Decimal_example"],
            wikipedia_client=DecimalWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        self.assertIn("wikipedia_infobox_table_filter_rejected", candidate.notes)
        self.assertEqual(llm_client.prompts, [])
        self.assertIn("not_number_dominant:decimal_number_count=1", candidate.source_metadata["discard_reason"])

    def test_not_number_dominant_mode_rejects_low_alpha_character_coverage(self) -> None:
        class LowAlphaWikipediaClient(FakeWikipediaClient):
            def fetch_parse(self, title_or_url: str) -> dict:
                return {
                    "parse": {
                        "title": "Low alpha example",
                        "text": """
                        <div class="mw-parser-output">
                        <p>Low alpha example is a settled historical list.</p>
                        <table class="wikitable">
                        <tr><th>#</th><th>%</th></tr>
                        <tr><td>12</td><td>34</td></tr>
                        <tr><td>56</td><td>78</td></tr>
                        </table>
                        </div>
                        """,
                    }
                }

        llm_client = FakeLLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/Low_alpha_example"],
            wikipedia_client=LowAlphaWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        self.assertIn("wikipedia_infobox_table_filter_rejected", candidate.notes)
        self.assertEqual(llm_client.prompts, [])
        self.assertIn("not_number_dominant:alpha_character_rate=0.0000", candidate.source_metadata["discard_reason"])

    def test_not_number_dominant_mode_rejects_unit_markers_before_llm_generation(self) -> None:
        class UnitWikipediaClient(FakeWikipediaClient):
            def fetch_parse(self, title_or_url: str) -> dict:
                return {
                    "parse": {
                        "title": "Unit example",
                        "text": """
                        <div class="mw-parser-output">
                        <p>Unit example is a settled historical list.</p>
                        <table class="wikitable">
                        <tr><th>Name</th><th>Production (kt)</th></tr>
                        <tr><td>Alpha</td><td>261</td></tr>
                        <tr><td>Beta</td><td>262</td></tr>
                        </table>
                        </div>
                        """,
                    }
                }

        llm_client = FakeLLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/Unit_example"],
            wikipedia_client=UnitWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        self.assertIn("wikipedia_infobox_table_filter_rejected", candidate.notes)
        self.assertEqual(llm_client.prompts, [])
        self.assertIn("not_number_dominant:unit_marker=kt", candidate.source_metadata["discard_reason"])
        self.assertIn("kt", candidate.source_metadata["table_selection"][0]["number_dominance_stats"]["unit_markers"])

    def test_not_number_dominant_mode_rejects_kilo_prefixed_unit_words(self) -> None:
        class KiloUnitWikipediaClient(FakeWikipediaClient):
            def fetch_parse(self, title_or_url: str) -> dict:
                return {
                    "parse": {
                        "title": "Kilo unit example",
                        "text": """
                        <div class="mw-parser-output">
                        <p>Kilo unit example is a settled historical list.</p>
                        <table class="wikitable">
                        <tr><th>Name</th><th>Output in kilocalories</th></tr>
                        <tr><td>Alpha</td><td>261</td></tr>
                        <tr><td>Beta</td><td>262</td></tr>
                        </table>
                        </div>
                        """,
                    }
                }

        llm_client = FakeLLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/Kilo_unit_example"],
            wikipedia_client=KiloUnitWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        self.assertIn("wikipedia_infobox_table_filter_rejected", candidate.notes)
        self.assertEqual(llm_client.prompts, [])
        self.assertIn("not_number_dominant:unit_marker=kilocalories", candidate.source_metadata["discard_reason"])

    def test_not_number_dominant_mode_rejects_ambiguous_unit_marker_with_context(self) -> None:
        class MeterWikipediaClient(FakeWikipediaClient):
            def fetch_parse(self, title_or_url: str) -> dict:
                return {
                    "parse": {
                        "title": "Meter example",
                        "text": """
                        <div class="mw-parser-output">
                        <p>Meter example is a settled historical list.</p>
                        <table class="wikitable">
                        <tr><th>Name</th><th>Length (m)</th></tr>
                        <tr><td>Alpha</td><td>42</td></tr>
                        <tr><td>Beta</td><td>43</td></tr>
                        </table>
                        </div>
                        """,
                    }
                }

        llm_client = FakeLLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/Meter_example"],
            wikipedia_client=MeterWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        self.assertIn("wikipedia_infobox_table_filter_rejected", candidate.notes)
        self.assertEqual(llm_client.prompts, [])
        self.assertIn("not_number_dominant:unit_marker=m", candidate.source_metadata["discard_reason"])

    def test_not_number_dominant_mode_does_not_treat_points_as_unit_marker(self) -> None:
        class PointsWikipediaClient(FakeWikipediaClient):
            def fetch_parse(self, title_or_url: str) -> dict:
                return {
                    "parse": {
                        "title": "Points example",
                        "text": """
                        <div class="mw-parser-output">
                        <p>Points example is a settled historical list.</p>
                        <table class="wikitable">
                        <tr><th>Name</th><th>Points</th></tr>
                        <tr><td>Alpha</td><td>42</td></tr>
                        <tr><td>Beta</td><td>73</td></tr>
                        </table>
                        </div>
                        """,
                    }
                }

        llm_client = FakeLLMClient()
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/Points_example"],
            wikipedia_client=PointsWikipediaClient(),
            llm_client=llm_client,
            record_limit=1,
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        self.assertNotIn("wikipedia_infobox_table_filter_rejected", candidate.notes)
        self.assertEqual(len(llm_client.prompts), 1)
        self.assertEqual(
            candidate.source_metadata["table_selection"][0]["number_dominance_stats"]["unit_markers"],
            [],
        )

    def test_single_fact_restriction_rejects_list_answer(self) -> None:
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=FakeWikipediaClient(),
            llm_client=FakeSingleFactListLLMClient(),
            record_limit=1,
            allowed_reasoning_types=("single_fact",),
            allowed_answer_types=("Person",),
            table_filter_modes=(),
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        self.assertIn("wikipedia_infobox_single_fact_list_answer", candidate.notes)
        self.assertEqual(candidate.source_metadata["discard_reason"], "single_fact_list_answer_not_allowed")

    def test_single_fact_reasoning_type_is_accepted_for_route3(self) -> None:
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=FakeWikipediaClient(),
            llm_client=FakeSingleFactLLMClient(),
            record_limit=1,
            min_table_score=-999.0,
            table_filter_modes=(),
            llm_choose_table=True,
        )
        candidates = generator.generate(run_date="2026-05-16", cutoff_year=2025)
        self.assertEqual(len(candidates), 1)
        candidate = candidates[0]
        self.assertEqual(candidate.relation_or_claim, "single_fact")
        self.assertEqual(candidate.question_family, "wikipedia_infobox_table_fact")
        self.assertEqual(candidate.source_metadata["reasoning_type"], "single_fact")
        self.assertEqual(candidate.source_metadata["selected_source_table"]["table_type"], "infobox")

    def test_generated_answer_normalization_preserves_parenthetical_answer_and_rank_alias(self) -> None:
        answer, aliases = _normalize_generated_answer(
            "AT&T Stadium ‡ (Dallas Stadium)",
            ["AT&T Stadium", "Dallas Stadium", "#1"],
        )
        self.assertEqual(answer, "AT&T Stadium (Dallas Stadium)")
        self.assertEqual(aliases, ["AT&T Stadium", "Dallas Stadium", "#1"])

    def test_explicit_other_answer_type_preserves_numeric_code_list(self) -> None:
        self.assertEqual(
            _normalize_answer_type(
                "Other",
                "000; 001; 010; 100",
                "In the 3-of-6 code, which original 3 data bits have the maximum number of appended bits set to 1?",
            ),
            "Other",
        )

    def test_temporal_question_overrides_mislabeled_number_year_answer(self) -> None:
        self.assertEqual(
            _normalize_answer_type(
                "Number",
                "1998",
                "What year had the highest number of viewers for the Academy Awards?",
            ),
            "Date",
        )

    def test_temporal_question_overrides_mislabeled_era_qualified_year_answer(self) -> None:
        self.assertEqual(
            _normalize_answer_type(
                "Number",
                "401 BC",
                "In which year was the Kingdom of Cilicia annexed by the Achaemenid Empire?",
            ),
            "Date",
        )
        self.assertEqual(
            _normalize_answer_type(
                "Number",
                "402 BCE",
                "What year did the historical event occur?",
            ),
            "Date",
        )

    def test_subject_anchor_context_passes_page_title_alias_and_table_scope(self) -> None:
        context = _subject_anchor_context(
            "List of pontoon bridges",
            "This is a list of pontoon bridges.",
            [
                WikipediaTable(
                    table_index=1,
                    table_type="wikitable",
                    section_heading="Longest",
                    caption="",
                    nearby_intro="",
                    headers=["Bridge", "Length"],
                    rows=[],
                    row_dicts=[],
                    normalized_text="",
                )
            ],
            cutoff_year=2025,
        )
        self.assertEqual(context["page_title"], "List of pontoon bridges")
        self.assertIn("pontoon bridges", context["title_aliases"])
        self.assertEqual(context["safe_subject_aliases"], [])
        self.assertEqual(context["table_scopes"][0]["nearby_section_heading"], "Longest")
        self.assertEqual(context["table_scopes"][0]["table_title"], "")

    def test_tie_completion_guard_rejects_incomplete_grouped_max_answer(self) -> None:
        table = WikipediaTable(
            table_index=1,
            table_type="wikitable",
            section_heading="Films with multiple nominations and awards",
            caption="Films that received multiple nominations",
            nearby_intro="",
            headers=["Nominations", "Film"],
            rows=[
                ["Nominations", "Film"],
                ["4", "Juno"],
                ["The Diving Bell and the Butterfly"],
                ["I'm Not There"],
                ["The Savages"],
                ["3", "A Mighty Heart"],
            ],
            row_dicts=[{"Nominations": "4", "Film": "Juno"}],
            normalized_text="",
        )
        problem = _tie_completion_problem(
            source_table=table,
            reasoning_type="max",
            answer="Juno",
            answer_items=[],
        )
        self.assertIn("incomplete_tie_answer", problem)
        self.assertIn("The Savages", problem)
        self.assertEqual(
            _tie_completion_problem(
                source_table=table,
                reasoning_type="max",
                answer="Juno; The Diving Bell and the Butterfly; I'm Not There; The Savages",
                answer_items=["Juno", "The Diving Bell and the Butterfly", "I'm Not There", "The Savages"],
            ),
            "",
        )

    def test_incomplete_tie_guard_is_a_warning_not_generation_rejection(self) -> None:
        class TieWikipediaClient(FakeWikipediaClient):
            request_events: list[dict] = []

            def fetch_parse(self, title_or_url: str) -> dict:
                return {
                    "parse": {
                        "title": "Example awards",
                        "text": """
                        <div class="mw-parser-output">
                        <p>Example awards was a completed award ceremony.</p>
                        <table class="wikitable">
                        <caption>Films with multiple nominations</caption>
                        <tr><th>Nominations</th><th>Film</th></tr>
                        <tr><td>4</td><td>Juno</td></tr>
                        <tr><td>The Diving Bell and the Butterfly</td></tr>
                        <tr><td>I'm Not There</td></tr>
                        <tr><td>The Savages</td></tr>
                        <tr><td>3</td><td>A Mighty Heart</td></tr>
                        </table>
                        </div>
                        """,
                    }
                }

        class TieLLMClient(FakeLLMClient):
            def complete_text(self, prompt: str) -> str:
                self.prompts.append(prompt)
                return """{
                  "question": "Which film at Example awards had the most nominations?",
                  "answer": "Juno",
                  "answer_type": "Other",
                  "answer_aliases": [],
                  "search_queries": [
                    "Example awards films multiple nominations",
                    "Example awards most nominations films",
                    "Example awards nominations table"
                  ],
                  "reasoning_type": "max",
                  "source_table": 1,
                  "derivation_summary": "Selected one maximum-capacity row.",
                  "discard_reason": null
                }"""

        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/Example_awards"],
            wikipedia_client=TieWikipediaClient(),
            llm_client=TieLLMClient(),
            record_limit=1,
            allowed_reasoning_types=("max",),
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        self.assertNotIn("wikipedia_infobox_incomplete_tie_answer", candidate.notes)
        self.assertEqual(candidate.answer, "Juno")
        self.assertIn(
            "incomplete_tie_answer",
            candidate.source_metadata["route_guard_warnings"]["wikipedia_infobox_incomplete_tie_answer"],
        )

    def test_shared_processing_accepts_wikipedia_candidate_without_source_candidate(self) -> None:
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=FakeWikipediaClient(),
            llm_client=FakeLLMClient(),
            record_limit=1,
            allowed_reasoning_types=("max",),
            table_filter_modes=(),
        )
        candidate = generator.generate(run_date="2026-05-16", cutoff_year=2025)[0]
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(
                target_time="2024",
                pilot_total=1,
                output_path=Path(tmpdir) / "accepted.jsonl",
                rejected_output_path=Path(tmpdir) / "rejected.jsonl",
                enabled_routes=("route3_wikipedia_infobox",),
            )
            result = process_generated_candidates(
                [candidate],
                settings=settings,
                search_client=FakeSearchClient(),
                rewrite_client=None,
            )
        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(result.accepted[0]["answer"], "AT&T Stadium")
        self.assertEqual(
            result.accepted[0]["validation"]["route_validation_policy"],
            "provenance_only_for_wikipedia_infobox_route",
        )
        self.assertIn("candidate_processing_seconds", result.accepted[0]["source_metadata"]["phase_timings_seconds"])

    def test_shared_processing_rejects_answer_leakage_for_wikipedia_route(self) -> None:
        candidate = GeneratedCandidate(
            source_type="wikipedia_tables",
            generation_route="route3_wikipedia_infobox",
            question="Is AT&T Stadium the answer for the 23rd FIFA World Cup?",
            canonical_question="Is AT&T Stadium the answer for the 23rd FIFA World Cup?",
            rewritten_question="Is AT&T Stadium the answer for the 23rd FIFA World Cup?",
            answer="AT&T Stadium",
            answer_aliases=[],
            subject_entity=EntityReference(
                name="2026 FIFA World Cup",
                wikipedia_title="2026_FIFA_World_Cup",
                url="https://en.wikipedia.org/wiki/2026_FIFA_World_Cup",
            ),
            answer_entity=EntityReference(name="AT&T Stadium"),
            relation_or_claim="max",
            evidence=EvidenceRecord(
                text="AT&T Stadium | Arlington | 80,000",
                url="https://en.wikipedia.org/wiki/2026_FIFA_World_Cup",
                source_title="2026 FIFA World Cup",
                retrieved_at="2026-05-16",
            ),
            answer_type="Other",
            source_metadata={"subject_anchor_aliases": ["23rd FIFA World Cup"]},
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(
                target_time="2024",
                pilot_total=1,
                output_path=Path(tmpdir) / "accepted.jsonl",
                rejected_output_path=Path(tmpdir) / "rejected.jsonl",
                enabled_routes=("route3_wikipedia_infobox",),
            )
            result = process_generated_candidates(
                [candidate],
                settings=settings,
                search_client=FakeSearchClient(),
                rewrite_client=None,
            )
        self.assertEqual(result.accepted, [])
        self.assertEqual(result.rejected[0]["rejection_reason"], "rewrite_guard_rejected")
        self.assertEqual(result.rejected[0]["rejection_rule"], "answer_leakage")
        self.assertEqual(result.rejected[0]["rejection_notes"]["failure_reason"], "answer_leakage")

    def test_load_urls_reads_cli_and_file_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "urls.txt"
            path.write_text(
                "# comment\nArchitecture and Transportation\tbridges\thttps://en.wikipedia.org/wiki/Page_Two\n\n",
                encoding="utf-8",
            )
            urls = _load_urls(["https://en.wikipedia.org/wiki/Page_One"], path)
            entries = _load_url_entries([], path)
        self.assertEqual(
            urls,
            [
                "https://en.wikipedia.org/wiki/Page_One",
                "https://en.wikipedia.org/wiki/Page_Two",
            ],
        )
        self.assertEqual(entries[0].domain, "Architecture and Transportation")
        self.assertEqual(entries[0].subdomain, "bridges")

    def test_streaming_retries_transient_wikipedia_generation_errors(self) -> None:
        retryable = {
            "rejection_reason": "wikipedia_infobox_generation_error:URLError",
            "notes": ["wikipedia_infobox_generation_error:URLError"],
            "source_metadata": {
                "error_message": (
                    "<urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] "
                    "EOF occurred in violation of protocol (_ssl.c:1017)>"
                )
            },
        }
        self.assertTrue(_should_rerun_stream_rejection(retryable))
        self.assertTrue(_should_rerun_stream_rejection({"rejection_reason": "search_longtail_verifier_error"}))
        self.assertTrue(_should_rerun_stream_rejection({"rejection_reason": "second_stage_grading_error"}))
        search_error = {
            "rejection_reason": "search_longtail_verifier_error",
            "rejection_notes": {
                "error_type": "URLError",
                "error_message": "timed out while searching",
            },
        }
        self.assertEqual(
            _rerun_error_details_from_record(search_error),
            {
                "error_type": "URLError",
                "error_message": "timed out while searching",
            },
        )
        permanent = {
            "rejection_reason": "wikipedia_infobox_no_tables",
            "source_metadata": {"error_message": ""},
        }
        self.assertFalse(_should_rerun_stream_rejection(permanent))

    def test_candidate_input_salvages_disabled_incomplete_tie_placeholder(self) -> None:
        record = {
            "question": "Example page",
            "answer": "",
            "source_type": "wikipedia_tables",
            "generation_route": "route3_wikipedia_infobox",
            "subject_entity": {
                "name": "Example page",
                "url": "https://en.wikipedia.org/wiki/Example_page",
            },
            "answer_entity": {"name": ""},
            "relation_or_claim": "wikipedia_table_composition",
            "evidence": {"text": "", "url": "https://en.wikipedia.org/wiki/Example_page"},
            "notes": ["wikipedia_infobox_incomplete_tie_answer"],
            "source_metadata": {
                "source_url": "https://en.wikipedia.org/wiki/Example_page",
                "canonical_url": "https://en.wikipedia.org/wiki/Example_page",
                "page_title": "Example page",
                "first_paragraph": "Example page is a list.",
                "parsed_tables": [
                    {
                        "table_index": 1,
                        "section_heading": "Results",
                        "caption": "Results",
                        "normalized_text": "Results\n4 | Alpha\n4 | Beta",
                    }
                ],
                "llm_response": {
                    "question": "Which Example page entries had the highest score?",
                    "answer": ["Alpha", "Beta"],
                    "answer_type": "Other",
                    "answer_aliases": [],
                    "search_queries": ["Example page highest score entries"],
                    "reasoning_type": "max",
                    "source_table": 1,
                },
            },
            "rejection_reason": "wikipedia_infobox_incomplete_tie_answer",
        }
        candidate = _candidate_from_record(record)
        self.assertEqual(candidate.question, "Which Example page entries had the highest score?")
        self.assertEqual(candidate.answer, "Alpha; Beta")
        self.assertEqual(candidate.relation_or_claim, "max")
        self.assertEqual(candidate.question_family, "wikipedia_infobox_table_fact")
        self.assertEqual(candidate.source_metadata["reasoning_type"], "max")
        self.assertEqual(candidate.source_metadata["answer_items"], ["Alpha", "Beta"])
        self.assertEqual(candidate.notes, [])
        self.assertEqual(
            candidate.source_metadata["route_guard_warnings"]["wikipedia_infobox_incomplete_tie_answer"],
            "disabled_incomplete_tie_answer_guard",
        )
        self.assertIn("Alpha", candidate.evidence.text)

    def test_candidate_input_uses_llm_source_table_for_placeholder_evidence(self) -> None:
        record = {
            "question": "Travis Scott production discography",
            "answer": "",
            "source_type": "wikipedia_tables",
            "generation_route": "route3_wikipedia_infobox",
            "subject_entity": {
                "name": "Travis Scott production discography",
                "url": "https://en.wikipedia.org/wiki/Travis_Scott_production_discography",
            },
            "answer_entity": {"name": ""},
            "relation_or_claim": "wikipedia_table_composition",
            "evidence": {
                "text": "The following list is a discography of production by Travis Scott.",
                "url": "https://en.wikipedia.org/wiki/Travis_Scott_production_discography",
            },
            "notes": ["wikipedia_infobox_incomplete_tie_answer"],
            "source_metadata": {
                "source_url": "https://en.wikipedia.org/wiki/Travis_Scott_production_discography",
                "canonical_url": "https://en.wikipedia.org/wiki/Travis_Scott_production_discography",
                "page_title": "Travis Scott production discography",
                "first_paragraph": "The following list is a discography of production by Travis Scott.",
                "parsed_tables": [
                    {
                        "table_index": 1,
                        "section_heading": "Singles produced",
                        "caption": "List of singles produced",
                        "normalized_text": 'Singles produced\n"Bitch Better Have My Money" | Rihanna | 2015 | 1',
                    }
                ],
                "llm_response": {
                    "question": "Which single produced by Travis Scott had the highest peak chart position in the US?",
                    "answer": '" Bitch Better Have My Money "',
                    "answer_type": "Other",
                    "answer_aliases": ["Bitch Better Have My Money"],
                    "search_queries": ["Travis Scott singles peak US chart position"],
                    "reasoning_type": "min",
                    "source_table": 1,
                },
            },
            "rejection_reason": "wikipedia_infobox_incomplete_tie_answer",
        }
        candidate = _candidate_from_record(record)
        self.assertIn("Bitch Better Have My Money", candidate.evidence.text)
        self.assertEqual(candidate.relation_or_claim, "min")
        self.assertEqual(candidate.source_metadata["reasoning_type"], "min")
        self.assertEqual(
            candidate.source_metadata["selected_source_table"]["caption"],
            "List of singles produced",
        )
        self.assertEqual(candidate.answer_type, "Other")

    def test_candidate_input_rebuilds_stale_numeric_code_answer_from_llm_response(self) -> None:
        record = {
            "question": "In the 3-of-6 code, which original 3 data bits have the maximum number of appended bits set to 1?",
            "answer": "0",
            "answer_type": "Number",
            "source_type": "wikipedia_tables",
            "generation_route": "route3_wikipedia_infobox",
            "subject_entity": {
                "name": "Constant-weight code",
                "url": "https://en.wikipedia.org/wiki/Constant-weight_code",
            },
            "answer_entity": {"name": "0"},
            "relation_or_claim": "max",
            "evidence": {
                "text": "3-of-6 code\nOriginal 3 data bits | Appended bits\n000 | 111\n001 | 110\n010 | 110\n100 | 110",
                "url": "https://en.wikipedia.org/wiki/Constant-weight_code",
            },
            "notes": [],
            "source_metadata": {
                "source_url": "https://en.wikipedia.org/wiki/Constant-weight_code",
                "canonical_url": "https://en.wikipedia.org/wiki/Constant-weight_code",
                "page_title": "Constant-weight code",
                "answer_type": "Number",
                "answer_items": ["000", "001", "010", "100"],
                "parsed_tables": [
                    {
                        "table_index": 1,
                        "section_heading": "m-of-n codes",
                        "caption": "3-of-6 code",
                        "normalized_text": "3-of-6 code\n000 | 111\n001 | 110\n010 | 110\n100 | 110",
                    }
                ],
                "llm_response": {
                    "question": "In the 3-of-6 code, which original 3 data bits have the maximum number of appended bits set to 1?",
                    "answer": ["000", "001", "010", "100"],
                    "answer_type": "Other",
                    "answer_aliases": [],
                    "search_queries": ["3-of-6 code appended bits maximum"],
                    "reasoning_type": "max",
                    "source_table": 1,
                },
            },
        }
        candidate = _candidate_from_record(record)
        self.assertEqual(candidate.answer_type, "Other")
        self.assertEqual(candidate.answer, "000; 001; 010; 100")
        self.assertEqual(candidate.source_metadata["answer_items"], ["000", "001", "010", "100"])


if __name__ == "__main__":
    unittest.main()
