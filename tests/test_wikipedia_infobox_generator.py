"""Tests for the Wikipedia infobox/table QA route."""

from __future__ import annotations

import sys
import json
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
from wikidata_simpleqa.wikipedia_client import (
    WikipediaClient,
    build_parse_api_url,
    build_search_api_url,
    normalize_wikipedia_page_id,
    normalize_wikipedia_title,
)
from wikidata_simpleqa.wikipedia_infobox_generator import (
    WikipediaInfoboxTableGenerator,
    WikipediaTable,
    extract_non_table_prose,
    extract_wikipedia_tables,
    rank_wikipedia_tables,
    _normalize_answer_type,
    _normalize_generated_answer,
    _subject_anchor_context,
    _tie_completion_problem,
)

SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from run_wikipedia_infobox_pipeline import (  # noqa: E402
    EndpointResumeState,
    _candidate_from_record,
    _filter_endpoint_url_entries,
    _load_endpoint_jsonl,
    _load_url_entries,
    _load_urls,
    _remaining_after_endpoint,
    _run_artifact_summary,
    _should_rerun_stream_rejection,
    _stream_search_queries,
    _write_summary_and_manifest,
    _write_stream_walkthrough,
    UrlEntry,
)


FIXTURE_HTML = """
<div class="mw-parser-output">
<p>The 2026 FIFA World Cup is the 23rd FIFA World Cup. Venue capacities are not listed in prose.</p>
<table class="infobox vevent">
  <tr><th colspan="2">Example event</th></tr>
  <tr><th>Edition</th><td>23rd</td></tr>
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
    "<p>The 2026 FIFA World Cup is the 23rd FIFA World Cup. Venue capacities are not listed in prose.</p>",
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
          "answer_type": "Entity",
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
          "answer_type": "Entity",
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


class FakeSearchClient:
    """Search client that returns configured result rows."""

    request_events: list[dict] = []

    def __init__(self, results_by_query: dict[str, list[dict[str, str]]] | None = None) -> None:
        self.results_by_query = results_by_query or {}

    def search(self, query: str, *, max_results: int = 5):
        rows = self.results_by_query.get(query, [])[:max_results]
        return [type("SearchResult", (), row)() for row in rows]


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
            "source_metadata": {
                "page_id": 111,
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
            "rejection_reason": "rewrite_guard_rejected",
            "rejection_rule": "answer_leakage",
            "source_metadata": {
                "page_id": 112,
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
            "source_metadata": {
                "page_id": 211,
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
            "rejection_reason": "search_longtail_verifier_rejected",
            "rejection_notes": {
                "search_verification_features": {"triggered_rule": "full_question:hit_rate_exceeded"}
            },
            "source_metadata": {
                "page_id": 212,
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
        )

        candidates = generator.generate(run_date="2026-05-16", cutoff_year=2025)

        self.assertEqual(candidates[0].final_question, "Which stadium hosting the 23rd FIFA World Cup has the largest capacity?")
        self.assertEqual(candidates[0].source_metadata["first_paragraph"], "")
        self.assertIn("URLError", candidates[0].source_metadata["first_paragraph_fetch_error"])
        self.assertIn("first_paragraph_fetch_seconds", candidates[0].source_metadata["phase_timings_seconds"])

    def test_broad_table_search_query_is_opt_in(self) -> None:
        default_args = SimpleNamespace(stream_search_query=[], enable_broad_table_search=False)
        self.assertEqual(_stream_search_queries(default_args), ['insource:"wikitable"'])

        broad_args = SimpleNamespace(stream_search_query=[], enable_broad_table_search=True)
        self.assertEqual(_stream_search_queries(broad_args), ['insource:"wikitable"', r"insource:/\{\|/"])

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

    def test_table_extraction_preserves_infobox_and_wikitable_rows(self) -> None:
        tables = extract_wikipedia_tables(FIXTURE_HTML)
        self.assertEqual(len(tables), 2)
        self.assertEqual(tables[0].table_type, "infobox")
        self.assertEqual(tables[0].row_dicts[0], {"Edition": "23rd"})
        self.assertEqual(tables[1].caption, "List of tournament venues")
        self.assertEqual(tables[1].section_heading, "Venues")
        self.assertEqual(tables[1].row_dicts[0]["Venue"], "AT&T Stadium")

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

    def test_table_ranking_prefers_structured_low_prose_leakage_tables(self) -> None:
        tables = extract_wikipedia_tables(FIXTURE_HTML)
        prose_text = extract_non_table_prose(FIXTURE_HTML)
        ranked = rank_wikipedia_tables(
            tables,
            first_paragraph="The 2026 FIFA World Cup is the 23rd FIFA World Cup.",
            prose_text=prose_text,
        )
        self.assertEqual(ranked[0]["table_index"], 2)
        self.assertIn("comparable_headers", ranked[0]["reasons"])
        self.assertIn("low_prose_leakage", ranked[0]["reasons"])

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
            llm_client=FakeLLMClient(),
            record_limit=1,
            url_domains={"https://en.wikipedia.org/wiki/2026_FIFA_World_Cup": "Sports"},
        )
        candidates = generator.generate(run_date="2026-05-16", cutoff_year=2025)
        self.assertEqual(len(candidates), 1)
        candidate = candidates[0]
        self.assertEqual(candidate.generation_route, "route3_wikipedia_infobox")
        self.assertEqual(candidate.final_question, "Which stadium hosting the 23rd FIFA World Cup has the largest capacity?")
        self.assertEqual(candidate.answer, "AT&T Stadium")
        self.assertEqual(candidate.relation_or_claim, "max")
        self.assertEqual(candidate.question_family, "wikipedia_infobox_table_fact")
        self.assertEqual(candidate.source_metadata["selected_source_table"]["caption"], "List of tournament venues")
        self.assertEqual(candidate.source_metadata["table_selection"][0]["caption"], "List of tournament venues")
        self.assertEqual(candidate.source_metadata["reasoning_type"], "max")
        self.assertNotIn("composition_type", candidate.source_metadata)
        self.assertEqual(candidate.source_metadata["content_domain"], "Sports")
        self.assertIn("23rd FIFA World Cup", candidate.source_metadata["subject_anchor_aliases"])
        self.assertEqual(candidate.source_metadata["subject_anchors"]["page_title"], "2026 FIFA World Cup")
        self.assertIn("23rd FIFA World Cup", candidate.source_metadata["subject_anchors"]["safe_subject_aliases"])
        self.assertEqual(
            candidate.source_metadata["subject_anchors"]["table_scopes"][0]["table_title"],
            "List of tournament venues",
        )
        self.assertIn("top three ranked tables", generator.llm_client.prompts[0])
        self.assertIn("what day, month, and year", generator.llm_client.prompts[0])
        self.assertIn("specify the counted quantity or unit", generator.llm_client.prompts[0])
        self.assertIn("Do not add units to the reference answer", generator.llm_client.prompts[0])
        self.assertIn('"subject_anchors"', generator.llm_client.prompts[0])
        self.assertIn('"safe_subject_aliases"', generator.llm_client.prompts[0])
        self.assertIn('"table_scopes"', generator.llm_client.prompts[0])
        self.assertNotIn('"preferred_subject_anchors"', generator.llm_client.prompts[0])
        self.assertIn("If the page title contains a cutoff-year marker", generator.llm_client.prompts[0])
        self.assertIn("do not copy anchor text mechanically", generator.llm_client.prompts[0])
        self.assertIn("Do not write `according to the table`", generator.llm_client.prompts[0])
        self.assertIn("`in the List of ...`", generator.llm_client.prompts[0])
        self.assertNotIn("For the 2026 FIFA World Cup page", generator.llm_client.prompts[0])
        self.assertIn("Do not ask cumulative-statistic questions", generator.llm_client.prompts[0])
        self.assertIn('"answer_type": "Entity|Number|Date"', generator.llm_client.prompts[0])
        self.assertIn('"reasoning_type"', generator.llm_client.prompts[0])
        self.assertIn("single fact question is allowed", generator.llm_client.prompts[0].lower())
        self.assertNotIn('"composition_type"', generator.llm_client.prompts[0])
        self.assertNotIn("preferred_subject_anchor exactly", generator.llm_client.prompts[0])
        self.assertNotIn("local, bounded facts", generator.llm_client.prompts[0])
        self.assertEqual(len(candidate.search_queries), 3)

    def test_single_fact_reasoning_type_is_accepted_for_route3(self) -> None:
        generator = WikipediaInfoboxTableGenerator(
            urls=["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"],
            wikipedia_client=FakeWikipediaClient(),
            llm_client=FakeSingleFactLLMClient(),
            record_limit=1,
            min_table_score=-999.0,
        )
        candidates = generator.generate(run_date="2026-05-16", cutoff_year=2025)
        self.assertEqual(len(candidates), 1)
        candidate = candidates[0]
        self.assertEqual(candidate.relation_or_claim, "single_fact")
        self.assertEqual(candidate.question_family, "wikipedia_infobox_table_fact")
        self.assertEqual(candidate.source_metadata["reasoning_type"], "single_fact")
        self.assertEqual(candidate.source_metadata["selected_source_table"]["table_type"], "infobox")

    def test_generated_answer_normalization_splits_parenthetical_alias(self) -> None:
        answer, aliases = _normalize_generated_answer(
            "AT&T Stadium ‡ (Dallas Stadium)",
            ["AT&T Stadium", "Dallas Stadium"],
        )
        self.assertEqual(answer, "AT&T Stadium")
        self.assertEqual(aliases, ["Dallas Stadium"])

    def test_explicit_entity_answer_type_preserves_numeric_code_list(self) -> None:
        self.assertEqual(
            _normalize_answer_type(
                "Entity",
                "000; 001; 010; 100",
                "In the 3-of-6 code, which original 3 data bits have the maximum number of appended bits set to 1?",
            ),
            "Entity",
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
                  "answer_type": "Entity",
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
            answer_type="Entity",
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
                    "answer_type": "Entity",
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
                    "answer_type": "Entity",
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
        self.assertEqual(candidate.answer_type, "Entity")

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
                    "answer_type": "Entity",
                    "answer_aliases": [],
                    "search_queries": ["3-of-6 code appended bits maximum"],
                    "reasoning_type": "max",
                    "source_table": 1,
                },
            },
        }
        candidate = _candidate_from_record(record)
        self.assertEqual(candidate.answer_type, "Entity")
        self.assertEqual(candidate.answer, "000; 001; 010; 100")
        self.assertEqual(candidate.source_metadata["answer_items"], ["000", "001", "010", "100"])


if __name__ == "__main__":
    unittest.main()
