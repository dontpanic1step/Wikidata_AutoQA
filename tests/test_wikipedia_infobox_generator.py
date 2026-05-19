"""Tests for the Wikipedia infobox/table QA route."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.config import Settings
from wikidata_simpleqa.generation_pipeline import process_generated_candidates
from wikidata_simpleqa.generation_models import EntityReference, EvidenceRecord, GeneratedCandidate
from wikidata_simpleqa.wikipedia_client import build_parse_api_url, normalize_wikipedia_title
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

from run_wikipedia_infobox_pipeline import _candidate_from_record, _load_url_entries, _load_urls  # noqa: E402


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
          "composition_type": "max",
          "source_table": 2,
          "derivation_summary": "Selected the venue row with the largest capacity.",
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

    def test_table_extraction_preserves_infobox_and_wikitable_rows(self) -> None:
        tables = extract_wikipedia_tables(FIXTURE_HTML)
        self.assertEqual(len(tables), 2)
        self.assertEqual(tables[0].table_type, "infobox")
        self.assertEqual(tables[0].row_dicts[0], {"Edition": "23rd"})
        self.assertEqual(tables[1].caption, "List of tournament venues")
        self.assertEqual(tables[1].section_heading, "Venues")
        self.assertEqual(tables[1].row_dicts[0]["Venue"], "AT&T Stadium")

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
        self.assertEqual(candidate.source_metadata["selected_source_table"]["caption"], "List of tournament venues")
        self.assertEqual(candidate.source_metadata["table_selection"][0]["caption"], "List of tournament venues")
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
        self.assertNotIn("preferred_subject_anchor exactly", generator.llm_client.prompts[0])
        self.assertNotIn("local, bounded facts", generator.llm_client.prompts[0])
        self.assertEqual(len(candidate.search_queries), 3)

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
            composition_type="max",
            answer="Juno",
            answer_items=[],
        )
        self.assertIn("incomplete_tie_answer", problem)
        self.assertIn("The Savages", problem)
        self.assertEqual(
            _tie_completion_problem(
                source_table=table,
                composition_type="max",
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
                  "composition_type": "max",
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
                    "composition_type": "max",
                    "source_table": 1,
                },
            },
            "rejection_reason": "wikipedia_infobox_incomplete_tie_answer",
        }
        candidate = _candidate_from_record(record)
        self.assertEqual(candidate.question, "Which Example page entries had the highest score?")
        self.assertEqual(candidate.answer, "Alpha; Beta")
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
                    "composition_type": "min",
                    "source_table": 1,
                },
            },
            "rejection_reason": "wikipedia_infobox_incomplete_tie_answer",
        }
        candidate = _candidate_from_record(record)
        self.assertIn("Bitch Better Have My Money", candidate.evidence.text)
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
                    "composition_type": "max",
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
