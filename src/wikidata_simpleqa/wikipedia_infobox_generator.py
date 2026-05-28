"""Wikipedia infobox/table route for table-grounded QA generation."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from html import unescape
from html.parser import HTMLParser
from time import perf_counter
from typing import Any, Iterable

from .cheap_model_qa import parse_json_object
from .generation_models import EntityReference, EvidenceRecord, GeneratedCandidate
from .entity_normalization import normalize_name
from .date_reference import normalize_date_answer
from .llm_rewrite import NO_SOCIAL_SCIENCE_RESEARCH_PROMPT
from .number_reference import parse_number_token
from .wikipedia_client import WikipediaClient, normalize_wikipedia_page_id, normalize_wikipedia_title

ROUTE_NAME = "route3_wikipedia_infobox"
SOURCE_TYPE = "wikipedia_tables"
ROUTE3_REASONING_TYPES = (
    "single_fact",
    "max",
    "min",
    "sum",
    "count",
    "comparison",
    "ordinal",
    "other",
)
ROUTE3_REASONING_TYPE_SET = set(ROUTE3_REASONING_TYPES)
ROUTE3_ANSWER_TYPES = ("Person", "Place", "Number", "Date", "Other")
ROUTE3_ANSWER_TYPE_SET = set(ROUTE3_ANSWER_TYPES)
ROUTE3_REASONING_TYPE_PROMPT_RULES = {
    "single_fact": "ask a direct single fact lookup from the structured source; do not ask a compositional question such as min, max, count, sum, comparison, or ordinal",
    "max": "ask for the row or value with the largest value within a fixed historical table scope",
    "min": "ask for the row or value with the smallest value within a fixed historical table scope",
    "sum": "ask for a sum over a clearly bounded fixed set of table values",
    "count": "ask for a count over a clearly bounded fixed set of table rows or values",
    "comparison": "ask for a comparison between clearly named rows or values in the table",
    "ordinal": "ask a temporal ordinal question like first or second by date, time, or order of occurrence; do not ask magnitude rankings such as largest or second largest",
    "other": "ask only if the reasoning is clearly described by the table and does not fit the named reasoning types",
}
ROUTE3_ANSWER_TYPE_PROMPT_RULES = {
    "Person": "answer must be a person's name, not a team's name, an official position or a named group of people. Do not ask `Who ...` unless the answer is a person's name",
    "Place": "answer must be a place name, location, or geographic entity on Earth, not a company/award/ceremony/planet etc.",
    "Number": "answer must be numeric",
    "Date": "answer must be a date, a month, or a year, do not ask `how many years` or ask about a time range",
    "Other": "answer must not be a person, place, number, or date; exclude numeric measurements, percentages, counts, scores, indices, rates, temperatures, durations, ranges, dates, years, people, and places",
}
ROUTE3_EXTRA_PROMPTS = {
    "no_social_science_research_prompt": NO_SOCIAL_SCIENCE_RESEARCH_PROMPT,
}
ROUTE3_TABLE_FILTER_MODES = (
    "no_picture_heavy_tables",
    "no_incomplete_tables",
    "not_number_dominant",
    "no_social_science_research",
)
ROUTE3_TABLE_FILTER_MODE_SET = set(ROUTE3_TABLE_FILTER_MODES)
DEFAULT_ROUTE3_TABLE_FILTER_MODES = ROUTE3_TABLE_FILTER_MODES
PICTURE_HEAVY_TABLE_MAX_IMAGE_CELL_RATE = 0.25
NUMBER_DOMINANCE_WORD_MARKERS = ("thousand", "million", "billion", "trillion")
NUMBER_DOMINANCE_LOW_NUMERIC_THRESHOLD = 1000
NUMBER_DOMINANCE_YEAR_LIKE_MIN = 1500
NUMBER_DOMINANCE_YEAR_LIKE_MAX = 2040
NUMBER_DOMINANCE_MIN_ALPHA_RATE = 0.5
INCOMPLETE_TABLE_MARKERS = (
    "unlisted",
    "incomplete",
    "unknown",
    "approx.",
    "approximate",
    "approximately",
    "citation needed",
    "citing needed",
)
NUMBER_DOMINANCE_UNIT_MARKERS = (
    "acre",
    "acres",
    "barrel",
    "barrels",
    "bbl",
    "bytes",
    "centimeter",
    "centimeters",
    "centimetre",
    "centimetres",
    "cm",
    "cubic feet",
    "cubic foot",
    "cubic meter",
    "cubic meters",
    "cubic metre",
    "cubic metres",
    "degree celsius",
    "degree fahrenheit",
    "degrees",
    "feet",
    "foot",
    "ft",
    "gal",
    "gallon",
    "gallons",
    "gigabyte",
    "gigabytes",
    "gigawatt",
    "gigawatts",
    "gram",
    "grams",
    "gw",
    "ha",
    "hectare",
    "hectares",
    "hz",
    "joule",
    "joules",
    "kb",
    "kg",
    "kilobyte",
    "kilobytes",
    "kilogram",
    "kilograms",
    "kilometer",
    "kilometers",
    "kilometre",
    "kilometres",
    "kilotonne",
    "kilotonnes",
    "kilowatt",
    "kilowatt hours",
    "kilowatts",
    "km",
    "km2",
    "kmh",
    "kph",
    "kt",
    "kw",
    "kwh",
    "lb",
    "lbs",
    "liter",
    "liters",
    "litre",
    "litres",
    "m2",
    "mb",
    "megabyte",
    "megabytes",
    "megawatt",
    "megawatt hours",
    "megawatts",
    "meter",
    "meters",
    "metre",
    "metres",
    "mg",
    "mi",
    "mile",
    "miles",
    "milligram",
    "milligrams",
    "millimeter",
    "millimeters",
    "millimetre",
    "millimetres",
    "ml",
    "mph",
    "mw",
    "mwh",
    "ounce",
    "ounces",
    "oz",
    "pascal",
    "pascals",
    "pound",
    "pounds",
    "psi",
    "sq km",
    "square feet",
    "square foot",
    "square kilometer",
    "square kilometers",
    "square kilometre",
    "square kilometres",
    "square meter",
    "square meters",
    "square metre",
    "square metres",
    "ton",
    "tons",
    "tonne",
    "tonnes",
    "watt",
    "watts",
    "yard",
    "yards",
    "yd",
)
NUMBER_DOMINANCE_AMBIGUOUS_UNIT_MARKERS = ("g", "m")
NUMBER_DOMINANCE_UNIT_REGEX_PATTERNS = (re.compile(r"(?<!\w)kilo[a-z]+(?!\w)"),)
SOCIAL_SCIENCE_TABLE_MARKERS = (
    "census",
    "survey",
    "demographic",
    "self reported",
    "ancestry group",
    "ethinic group",
    "ethinicity",
    "population",
    "language speaker",
)
ENABLE_NUMERIC_TABLE_RANKING_POINTS = False
ORDINAL_EVENT_PATTERN = re.compile(
    r"\b\d+(?:st|nd|rd|th)\s+(?:[A-Z][A-Za-z0-9&'()-]*\s+){0,8}(?:World Cup|Olympics|Championship|Tournament)\b"
)
NUMBER_PATTERN = re.compile(r"\b\d[\d,]*(?:\.\d+)?\b")
COMPOSITION_HEADER_HINTS = {
    "capacity",
    "attendance",
    "population",
    "area",
    "length",
    "height",
    "depth",
    "age",
    "vote",
    "votes",
    "score",
    "points",
    "rank",
    "ranking",
    "number",
    "count",
    "total",
    "date",
    "year",
    "opened",
}
PREFERRED_TABLE_HINTS = {
    "venue",
    "venues",
    "stadium",
    "stadiums",
}
MUTABLE_OR_PLACEHOLDER_TABLE_HINTS = {
    "ranking of third-placed teams",
    "standings",
    "match schedule",
    "tie-breaking",
    "qualification",
}
LIVE_TABLE_SCOPE_TERMS = ("current", "active", "incumbent", "present", "latest")
ANSWER_PRECISION_PROMPT_RULES = (
    "- If the answer is a temporal value, the question must specify the requested precision or unit, "
    "such as what year, what month, what day, or how many months.\n"
    "- If the answer is a full calendar date, ask `what month, day, and year ...` and format the "
    "reference answer like `May 20, 2024`; if the answer is a month, ask `what month and year ...` "
    "and format it like `May 2024`.\n"
    "- If the answer is a number, specify the counted quantity or unit in the question, such as gallons, "
    "people, months, authors, tracks, seats, or metres.\n"
    "- If the answer is a place, the question should specify the type of place or geographic entity, such as city, country, river, or mountain, instead of just asking `What place ...` `What location ...`.\n"
    "- Do not add units to the reference answer or answer_aliases; keep numeric reference answers as "
    "normalized values only.\n"
)
DATE_PRECISION_PROMPT_RULES = (
    "- If the answer is a temporal value, the question must specify the requested precision or unit, "
    "such as what year, what month, what day, or how many months.\n"
    "- If the answer is a full calendar date, ask `what month, day, and year ...` and format the "
    "reference answer like `May 20, 2024`; if the answer is a month, ask `what month and year ...` "
    "and format it like `May 2024`.\n"
)
NUMBER_PRECISION_PROMPT_RULES = (
    "- If the answer is a number, specify the counted quantity or unit in the question, such as gallons, "
    "people, months, authors, tracks, seats, or metres.\n"
    "- Do not add units to the reference answer or answer_aliases; keep numeric reference answers as "
    "normalized values only.\n"
)
PLACE_PRECISION_PROMPT_RULES = (
    "- If the answer is a place, the question should specify the type of place or geographic entity, such as city, country, river, or mountain, instead of just asking `What place ...` `What location ...`.\n"
)


@dataclass(slots=True)
class WikipediaTable:
    """One extracted Wikipedia infobox or article table."""

    table_index: int
    table_type: str
    section_heading: str
    caption: str
    nearby_intro: str
    headers: list[str]
    rows: list[list[str]]
    row_dicts: list[dict[str, str]]
    normalized_text: str
    markdown: str = ""
    structure: dict[str, Any] = field(default_factory=dict)

    def to_metadata(self, *, max_rows: int = 50, max_text_chars: int = 4000) -> dict[str, Any]:
        """Return a compact audit representation for output metadata."""
        return {
            "table_index": self.table_index,
            "table_type": self.table_type,
            "section_heading": self.section_heading,
            "caption": self.caption,
            "nearby_intro": self.nearby_intro[:1000],
            "headers": self.headers,
            "rows": self.rows[:max_rows],
            "markdown": self.markdown[:max_text_chars],
            "normalized_text": self.normalized_text[:max_text_chars],
            "structure": self.structure,
            "truncated": len(self.rows) > max_rows or len(self.normalized_text) > max_text_chars,
        }


@dataclass(slots=True)
class WikipediaPageTables:
    """Parsed Wikipedia page metadata and structured tables."""

    source_url: str
    title: str
    canonical_url: str
    content_domain: str
    html: str
    first_paragraph: str
    first_paragraph_fetch_error: str
    prose_text: str
    tables: list[WikipediaTable]


@dataclass(slots=True)
class WikipediaInfoboxTableGenerator:
    """Generate one table-grounded QA candidate per supplied Wikipedia URL."""

    urls: list[str]
    wikipedia_client: WikipediaClient
    llm_client: Any
    record_limit: int = 10
    route_name: str = ROUTE_NAME
    source_type: str = SOURCE_TYPE
    url_domains: dict[str, str] | None = None
    search_query_count: int = 3
    enable_rest_summary_fallback: bool = False
    min_table_score: float = 0.0
    allowed_reasoning_types: tuple[str, ...] = ()
    allowed_answer_types: tuple[str, ...] = ()
    extra_prompts: tuple[str, ...] = ()
    table_filter_modes: tuple[str, ...] = DEFAULT_ROUTE3_TABLE_FILTER_MODES
    llm_choose_table: bool = False

    def __post_init__(self) -> None:
        """Normalize optional Route 3 prompt restrictions."""
        self.allowed_reasoning_types = normalize_route3_reasoning_types(self.allowed_reasoning_types)
        self.allowed_answer_types = normalize_route3_answer_types(self.allowed_answer_types)
        self.extra_prompts = normalize_route3_extra_prompts(self.extra_prompts)
        self.table_filter_modes = normalize_route3_table_filter_modes(self.table_filter_modes)

    def generate(self, *, run_date: str, cutoff_year: int) -> list[GeneratedCandidate]:
        """Generate candidates from up to ``record_limit`` Wikipedia URLs."""
        generated: list[GeneratedCandidate] = []
        for url in self.urls[: self.record_limit]:
            candidate_start = perf_counter()
            timings: dict[str, float] = {}
            try:
                page = self._fetch_and_parse_page(url, timings=timings)
                candidate = self._candidate_from_page(
                    page,
                    run_date=run_date,
                    cutoff_year=cutoff_year,
                    timings=timings,
                )
            except Exception as exc:  # noqa: BLE001
                timings["total_generation_seconds"] = _elapsed(candidate_start)
                candidate = _rejected_placeholder(
                    url=url,
                    reason=f"wikipedia_infobox_generation_error:{type(exc).__name__}",
                    run_date=run_date,
                    timings=timings,
                    content_domain=self._domain_for_url(url, url, normalize_wikipedia_title(url)),
                    error_message=str(exc),
                    allowed_reasoning_types=self.allowed_reasoning_types,
                    allowed_answer_types=self.allowed_answer_types,
                    extra_prompts=self.extra_prompts,
                    table_filter_modes=self.table_filter_modes,
                )
            candidate.source_metadata["llm_choose_table"] = bool(self.llm_choose_table)
            candidate.source_metadata.setdefault("phase_timings_seconds", {}).update(timings)
            candidate.source_metadata["phase_timings_seconds"]["total_generation_seconds"] = _elapsed(candidate_start)
            generated.append(candidate)
        return generated

    def _fetch_and_parse_page(self, url: str, *, timings: dict[str, float]) -> WikipediaPageTables:
        """Fetch one page through MediaWiki APIs and extract table records."""
        fetch_start = perf_counter()
        parse_payload = self.wikipedia_client.fetch_parse(url)
        timings["page_fetch_seconds"] = _elapsed(fetch_start)
        parse_body = parse_payload.get("parse", {}) if isinstance(parse_payload, dict) else {}
        title = str(parse_body.get("title", normalize_wikipedia_title(url))).strip()
        canonical_url = "https://en.wikipedia.org/wiki/" + title.replace(" ", "_") if title else url
        html = str(parse_body.get("text", "")).strip()

        parse_start = perf_counter()
        tables = extract_wikipedia_tables(html)
        prose_text = extract_non_table_prose(html)
        timings["table_parse_seconds"] = _elapsed(parse_start)
        return WikipediaPageTables(
            source_url=url,
            title=title,
            canonical_url=canonical_url,
            content_domain=self._domain_for_url(url, canonical_url, title),
            html=html,
            first_paragraph="",
            first_paragraph_fetch_error="",
            prose_text=prose_text,
            tables=tables,
        )

    def _extract_first_paragraph_context(self, page: WikipediaPageTables, *, timings: dict[str, float]) -> None:
        """Populate first-paragraph context after a page has surviving tables."""
        if page.first_paragraph or page.first_paragraph_fetch_error:
            return
        paragraph_start = perf_counter()
        page.first_paragraph = extract_first_paragraph(page.html)
        timings["first_paragraph_extract_seconds"] = _elapsed(paragraph_start)
        if not page.first_paragraph and page.title and self.enable_rest_summary_fallback:
            paragraph_fetch_start = perf_counter()
            try:
                summary = self.wikipedia_client.fetch_summary(page.title)
                page.first_paragraph = str(summary.get("extract", "")).strip()
            except Exception as exc:  # noqa: BLE001
                page.first_paragraph_fetch_error = f"{type(exc).__name__}:{exc}"
            finally:
                timings["first_paragraph_fetch_seconds"] = _elapsed(paragraph_fetch_start)

    def _domain_for_url(self, source_url: str, canonical_url: str, title: str) -> str:
        """Return the configured broad content domain for one page."""
        if not self.url_domains:
            return ""
        candidates = [
            source_url,
            canonical_url,
            title,
            title.replace(" ", "_"),
            normalize_wikipedia_title(source_url),
            normalize_wikipedia_title(canonical_url),
        ]
        for candidate in candidates:
            domain = self.url_domains.get(candidate)
            if domain:
                return domain
        return ""

    def _candidate_from_page(
        self,
        page: WikipediaPageTables,
        *,
        run_date: str,
        cutoff_year: int,
        timings: dict[str, float],
    ) -> GeneratedCandidate:
        """Ask the small model for one QA candidate and convert it to the shared shape."""
        if not page.tables:
            return _rejected_placeholder(
                url=page.source_url,
                reason="wikipedia_infobox_no_tables",
                run_date=run_date,
                timings=timings,
                title=page.title,
                canonical_url=page.canonical_url,
                content_domain=page.content_domain,
                first_paragraph=page.first_paragraph,
                min_table_score=self.min_table_score,
                allowed_reasoning_types=self.allowed_reasoning_types,
                allowed_answer_types=self.allowed_answer_types,
                extra_prompts=self.extra_prompts,
                table_filter_modes=self.table_filter_modes,
            )
        table_selection = rank_wikipedia_tables(
            page.tables,
            first_paragraph=page.first_paragraph,
            prose_text=page.prose_text,
        )
        table_selection = _annotate_table_score_cutoff(table_selection, self.min_table_score)
        table_selection = _annotate_table_filter_modes(table_selection, self.table_filter_modes)
        safe_table_selection = [
            row
            for row in table_selection
            if not str(row.get("live_scope_rejection_reason", "")).strip()
            and not bool(row.get("below_min_table_score"))
            and not str(row.get("table_filter_rejection_reason", "")).strip()
        ]
        llm_table_limit = 3 if self.llm_choose_table else 1
        selected_tables = [
            row["table"]
            for row in safe_table_selection
            if isinstance(row.get("table"), WikipediaTable)
        ][:llm_table_limit]
        selected_table_selection = safe_table_selection[:llm_table_limit]
        if not selected_tables:
            live_scope_rows = [
                row
                for row in table_selection
                if str(row.get("live_scope_rejection_reason", "")).strip()
            ]
            below_min_rows = [
                row
                for row in table_selection
                if bool(row.get("below_min_table_score"))
            ]
            below_min_non_live_rows = [
                row
                for row in below_min_rows
                if not str(row.get("live_scope_rejection_reason", "")).strip()
            ]
            table_filter_rows = [
                row
                for row in table_selection
                if str(row.get("table_filter_rejection_reason", "")).strip()
            ]
            table_filter_non_live_rows = [
                row
                for row in table_filter_rows
                if not str(row.get("live_scope_rejection_reason", "")).strip()
                and not bool(row.get("below_min_table_score"))
            ]
            if live_scope_rows and not below_min_non_live_rows:
                return _rejected_placeholder(
                    url=page.source_url,
                    reason="wikipedia_infobox_live_table_scope",
                    run_date=run_date,
                    timings=timings,
                    title=page.title,
                    canonical_url=page.canonical_url,
                    content_domain=page.content_domain,
                    first_paragraph=page.first_paragraph,
                    discard_reason=str(live_scope_rows[0].get("live_scope_rejection_reason", "")),
                    tables=page.tables,
                    table_selection=table_selection,
                    min_table_score=self.min_table_score,
                    allowed_reasoning_types=self.allowed_reasoning_types,
                    allowed_answer_types=self.allowed_answer_types,
                    extra_prompts=self.extra_prompts,
                    table_filter_modes=self.table_filter_modes,
                )
            if below_min_rows and not table_filter_non_live_rows:
                return _rejected_placeholder(
                    url=page.source_url,
                    reason="wikipedia_infobox_table_score_below_minimum",
                    run_date=run_date,
                    timings=timings,
                    title=page.title,
                    canonical_url=page.canonical_url,
                    content_domain=page.content_domain,
                    first_paragraph=page.first_paragraph,
                    discard_reason=_table_score_cutoff_discard_reason(below_min_rows, self.min_table_score),
                    tables=page.tables,
                    table_selection=table_selection,
                    min_table_score=self.min_table_score,
                    allowed_reasoning_types=self.allowed_reasoning_types,
                    allowed_answer_types=self.allowed_answer_types,
                    extra_prompts=self.extra_prompts,
                    table_filter_modes=self.table_filter_modes,
                )
            if table_filter_rows:
                return _rejected_placeholder(
                    url=page.source_url,
                    reason="wikipedia_infobox_table_filter_rejected",
                    run_date=run_date,
                    timings=timings,
                    title=page.title,
                    canonical_url=page.canonical_url,
                    content_domain=page.content_domain,
                    first_paragraph=page.first_paragraph,
                    discard_reason=_table_filter_discard_reason(table_filter_rows),
                    tables=page.tables,
                    table_selection=table_selection,
                    min_table_score=self.min_table_score,
                    allowed_reasoning_types=self.allowed_reasoning_types,
                    allowed_answer_types=self.allowed_answer_types,
                    extra_prompts=self.extra_prompts,
                    table_filter_modes=self.table_filter_modes,
                )
            return _rejected_placeholder(
                url=page.source_url,
                reason="wikipedia_infobox_no_suitable_tables",
                run_date=run_date,
                timings=timings,
                title=page.title,
                canonical_url=page.canonical_url,
                content_domain=page.content_domain,
                first_paragraph=page.first_paragraph,
                tables=page.tables,
                table_selection=table_selection,
                min_table_score=self.min_table_score,
                allowed_reasoning_types=self.allowed_reasoning_types,
                allowed_answer_types=self.allowed_answer_types,
                extra_prompts=self.extra_prompts,
                table_filter_modes=self.table_filter_modes,
            )
        self._extract_first_paragraph_context(page, timings=timings)
        prompt = build_wikipedia_infobox_prompt(
            title=page.title,
            canonical_url=page.canonical_url,
            first_paragraph=page.first_paragraph,
            subject_anchors=_subject_anchor_context(
                page.title,
                page.first_paragraph,
                selected_tables,
                cutoff_year,
            ),
            tables=selected_tables,
            table_selection=selected_table_selection,
            cutoff_year=cutoff_year,
            search_query_count=self.search_query_count,
            allowed_reasoning_types=self.allowed_reasoning_types,
            allowed_answer_types=self.allowed_answer_types,
            extra_prompts=self.extra_prompts,
            llm_choose_table=self.llm_choose_table,
        )
        llm_start = perf_counter()
        response = parse_json_object(self.llm_client.complete_text(prompt))
        timings["llm_question_generation_seconds"] = _elapsed(llm_start)
        discard_reason = str(response.get("discard_reason", "") or "").strip()
        if discard_reason:
            return _rejected_placeholder(
                url=page.source_url,
                reason="wikipedia_infobox_llm_discarded",
                run_date=run_date,
                timings=timings,
                title=page.title,
                canonical_url=page.canonical_url,
                content_domain=page.content_domain,
                first_paragraph=page.first_paragraph,
                discard_reason=discard_reason,
                tables=page.tables,
                llm_response=response,
                llm_prompt=prompt,
                table_selection=table_selection,
                min_table_score=self.min_table_score,
                allowed_reasoning_types=self.allowed_reasoning_types,
                allowed_answer_types=self.allowed_answer_types,
                extra_prompts=self.extra_prompts,
                table_filter_modes=self.table_filter_modes,
            )

        question = str(response.get("question", "")).strip()
        answer_value = response.get("answer", "")
        answer = _answer_display_text(answer_value)
        if not question or not answer:
            return _rejected_placeholder(
                url=page.source_url,
                reason="wikipedia_infobox_llm_missing_question_or_answer",
                run_date=run_date,
                timings=timings,
                title=page.title,
                canonical_url=page.canonical_url,
                content_domain=page.content_domain,
                first_paragraph=page.first_paragraph,
                tables=page.tables,
                llm_response=response,
                llm_prompt=prompt,
                table_selection=table_selection,
                min_table_score=self.min_table_score,
                allowed_reasoning_types=self.allowed_reasoning_types,
                allowed_answer_types=self.allowed_answer_types,
                extra_prompts=self.extra_prompts,
                table_filter_modes=self.table_filter_modes,
            )

        answer, aliases = _normalize_generated_answer(
            answer_value,
            _string_list(response.get("answer_aliases", [])),
        )
        answer_items = _answer_items(answer_value)
        source_table_index = _coerce_table_index(response.get("source_table"))
        source_table = _table_by_index(selected_tables, source_table_index)
        if self.allowed_reasoning_types == ("single_fact",) and len(answer_items) > 1:
            return _rejected_placeholder(
                url=page.source_url,
                reason="wikipedia_infobox_single_fact_list_answer",
                run_date=run_date,
                timings=timings,
                title=page.title,
                canonical_url=page.canonical_url,
                content_domain=page.content_domain,
                first_paragraph=page.first_paragraph,
                discard_reason="single_fact_list_answer_not_allowed",
                tables=page.tables,
                llm_response=response,
                llm_prompt=prompt,
                table_selection=table_selection,
                source_table=source_table,
                question=question,
                answer=answer,
                min_table_score=self.min_table_score,
                allowed_reasoning_types=self.allowed_reasoning_types,
                allowed_answer_types=self.allowed_answer_types,
                extra_prompts=self.extra_prompts,
                table_filter_modes=self.table_filter_modes,
            )
        social_science_violation = _extra_prompt_violation(
            extra_prompts=self.extra_prompts,
            question=question,
            answer=answer,
            page=page,
            source_table=source_table,
        )
        if social_science_violation:
            return _rejected_placeholder(
                url=page.source_url,
                reason="wikipedia_infobox_extra_prompt_violation",
                run_date=run_date,
                timings=timings,
                title=page.title,
                canonical_url=page.canonical_url,
                content_domain=page.content_domain,
                first_paragraph=page.first_paragraph,
                discard_reason=social_science_violation,
                tables=page.tables,
                llm_response=response,
                llm_prompt=prompt,
                table_selection=table_selection,
                source_table=source_table,
                question=question,
                answer=answer,
                min_table_score=self.min_table_score,
                allowed_reasoning_types=self.allowed_reasoning_types,
                allowed_answer_types=self.allowed_answer_types,
                extra_prompts=self.extra_prompts,
                table_filter_modes=self.table_filter_modes,
            )
        answer_type = _normalize_answer_type(response.get("answer_type"), answer, question)
        if self.allowed_answer_types and answer_type not in self.allowed_answer_types:
            return _rejected_placeholder(
                url=page.source_url,
                reason="wikipedia_infobox_answer_type_not_allowed",
                run_date=run_date,
                timings=timings,
                title=page.title,
                canonical_url=page.canonical_url,
                content_domain=page.content_domain,
                first_paragraph=page.first_paragraph,
                discard_reason=_answer_type_not_allowed_reason(response, self.allowed_answer_types),
                tables=page.tables,
                llm_response=response,
                llm_prompt=prompt,
                table_selection=table_selection,
                question=question,
                answer=answer,
                min_table_score=self.min_table_score,
                allowed_reasoning_types=self.allowed_reasoning_types,
                allowed_answer_types=self.allowed_answer_types,
                extra_prompts=self.extra_prompts,
                table_filter_modes=self.table_filter_modes,
            )
        search_queries = _sanitize_answer_blind_queries(
            response.get("search_queries", []),
            answer=answer,
            answer_aliases=aliases,
            answer_items=answer_items,
            max_queries=self.search_query_count,
        )
        declared_reasoning_type = _declared_reasoning_type(response)
        if self.allowed_reasoning_types and declared_reasoning_type not in self.allowed_reasoning_types:
            return _rejected_placeholder(
                url=page.source_url,
                reason="wikipedia_infobox_reasoning_type_not_allowed",
                run_date=run_date,
                timings=timings,
                title=page.title,
                canonical_url=page.canonical_url,
                content_domain=page.content_domain,
                first_paragraph=page.first_paragraph,
                discard_reason=_reasoning_type_not_allowed_reason(response, self.allowed_reasoning_types),
                tables=page.tables,
                llm_response=response,
                llm_prompt=prompt,
                table_selection=table_selection,
                source_table=source_table,
                question=question,
                answer=answer,
                min_table_score=self.min_table_score,
                allowed_reasoning_types=self.allowed_reasoning_types,
                allowed_answer_types=self.allowed_answer_types,
                extra_prompts=self.extra_prompts,
                table_filter_modes=self.table_filter_modes,
            )
        reasoning_type = declared_reasoning_type or _reasoning_type(response)
        tie_problem = _tie_completion_problem(
            source_table=source_table,
            reasoning_type=reasoning_type,
            answer=answer,
            answer_items=answer_items,
        )
        evidence_text = source_table.normalized_text if source_table is not None else page.first_paragraph
        return GeneratedCandidate(
            source_type=self.source_type,
            generation_route=self.route_name,
            question=question,
            canonical_question=question,
            rewritten_question=question,
            answer=answer,
            answer_aliases=aliases,
            subject_entity=EntityReference(
                name=page.title,
                wikipedia_title=page.title.replace(" ", "_"),
                url=page.canonical_url,
            ),
            answer_entity=EntityReference(name=answer),
            relation_or_claim=reasoning_type or "wikipedia_table_fact",
            evidence=EvidenceRecord(
                text=evidence_text,
                url=page.canonical_url,
                source_title=page.title,
                section=source_table.section_heading if source_table is not None else "",
                retrieved_at=run_date,
            ),
            question_family="wikipedia_infobox_table_fact",
            answer_type=answer_type,
            topic="Wikipedia semi-structured data",
            target_time=run_date[:4],
            source_template_domain="wikipedia_infobox_table",
            search_queries=search_queries,
            source_metadata=_source_metadata(
                page=page,
                tables=page.tables,
                llm_response=response,
                llm_prompt=prompt,
                source_table=source_table,
                table_selection=table_selection,
                timings=timings,
                answer_items=answer_items,
                answer_type=answer_type,
                reasoning_type=reasoning_type,
                tie_completion_warning=tie_problem,
                subject_anchors=_subject_anchor_context(
                    page.title,
                    page.first_paragraph,
                    selected_tables,
                    cutoff_year,
                ),
                min_table_score=self.min_table_score,
                allowed_reasoning_types=self.allowed_reasoning_types,
                allowed_answer_types=self.allowed_answer_types,
                extra_prompts=self.extra_prompts,
                table_filter_modes=self.table_filter_modes,
                llm_choose_table=self.llm_choose_table,
            ),
        )


def build_wikipedia_infobox_prompt(
    *,
    title: str,
    canonical_url: str,
    first_paragraph: str,
    subject_anchors: dict[str, Any],
    tables: list[WikipediaTable],
    table_selection: list[dict[str, Any]],
    cutoff_year: int,
    search_query_count: int = 3,
    allowed_reasoning_types: Iterable[str] | None = None,
    allowed_answer_types: Iterable[str] | None = None,
    extra_prompts: Iterable[str] | str | None = None,
    llm_choose_table: bool = False,
) -> str:
    """Build the small-model prompt for Wikipedia table QA generation."""
    normalized_allowed_reasoning_types = normalize_route3_reasoning_types(allowed_reasoning_types)
    normalized_allowed_answer_types = normalize_route3_answer_types(allowed_answer_types)
    normalized_extra_prompts = normalize_route3_extra_prompts(extra_prompts)
    table_limit = 3 if llm_choose_table else 1
    payload = {
        "title": title,
        "canonical_url": canonical_url,
        "first_paragraph": first_paragraph[:2500],
        "safe_subject_aliases": subject_anchors.get("safe_subject_aliases", []),
        "subject_anchors": subject_anchors,
        "allowed_reasoning_types": list(normalized_allowed_reasoning_types),
        "allowed_answer_types": list(normalized_allowed_answer_types),
        "extra_prompt_rules": list(normalized_extra_prompts),
        "llm_choose_table": bool(llm_choose_table),
        "ranked_table_selection": [
            _selection_payload(row)
            for row in table_selection[:table_limit]
        ],
        "tables": [table.to_metadata(max_rows=40, max_text_chars=2500) for table in tables[:table_limit]],
    }
    if llm_choose_table:
        payload["table_selection_criteria"] = [
            "Prefer tables with many structured data rows.",
            # "Prefer tables with numeric, ordinal, date, rank, count, or comparable value columns.",
            "Prefer tables whose row values are mostly not repeated in non-table prose, because these are less directly answerable from the article text.",
        ]
    table_instruction = (
        "- Choose from the top three ranked tables. Prefer rank 1 unless it cannot support a safe question.\n"
        if llm_choose_table
        else "- Use the provided top-ranked table as the only structured evidence table.\n"
    )
    toy_table_instruction = (
        "- If the table is only a toy, tutorial, or teaching example rather than real-world factual data, choose another table.\n"
        if llm_choose_table
        else "- If the provided table is only a toy, tutorial, or teaching example rather than real-world factual data, discard it.\n"
    )
    return (
        "Generate one long-tail SimpleQA-style factual question from a Wikipedia infobox or table.\n"
        "Return JSON only.\n\n"
        "Requirements:\n\n"

        "### Must have a single answer.\n\n"
        "- The question must have exactly one intended, indisputable answer.\n"
        f"{table_instruction}"
        "- Avoid questions with unclear or overly broad answer categories, such as `What equipment ...` `What genre ...`. Instead, ask about a more specific and verifiable attribute.\n"
        f"{_answer_precision_prompt_rule(normalized_allowed_answer_types)}"
        "- If a table cell has a parenthetical alias, put the plain entity name in answer and the parenthetical text in answer_aliases.\n"

        "### Reasoning type and Answer type rules:\n\n"
        "- Your question must match the reasoning type and answer type.\n"
        f"{_reasoning_type_prompt_rule(normalized_allowed_reasoning_types)}"
        f"{_answer_type_prompt_rule(normalized_allowed_answer_types)}"
        f"{_tie_answer_prompt_rule(normalized_allowed_reasoning_types)}"
        f"- If the tables provided cannot support the allowed answer types {', '.join(normalized_allowed_answer_types)}, discard the table, set other fields empty, and write `discard_reason` in your response.\n"

        "### Reference answers should not change over time.\n\n"
        f"{_route3_stability_prompt_rule()}"
        "- Do not ask cumulative-statistic questions such as how many goals Messi has scored, total wins, career points, revenue, downloads, citations, or followers unless the statistic is explicitly scoped to a historically settled slice, completed event, completed season, or fixed table/list.\n"
        "- Do not ask about current, latest, most recent, or live-status facts.\n"
        "- Avoid mutable-sounding wording such as `total assets`, `total number`, `current`, or `as of`.\n"
        # "- For completed historical tables, phrase the comparison as a fixed result within the named event or list.\n"

        "### Use careful wording to avoid ambiguity.\n\n"
        "- Use subject_anchors only to understand the page/table scope; do not copy anchor text mechanically into the question.\n"
        "- Let the table caption, nearby paragraph intro, or nearby section heading define the safe scope. Pay special attention to nearby intros with words like `following` or `above`; they often state which rows are included or excluded. For example, `15 largest commercial banks in Ukraine` supports asking which bank is largest in Ukraine, but not how many banks exist in Ukraine. A `1980 chart` table supports asking about facts in that 1980 chart, but not when a song first entered a chart because it may have entered in another year.\n"
        "- Avoid vague phrases like `linked to`.\n"

        "### Must be challenging.\n\n"
        "- Prefer table facts that are not easily found in article prose outside tables.\n"
        "- Prefer answers that look unfamiliar to you and are likely to remain long-tail after search filtering.\n"
        
        "### Must be answerable.\n\n"
        "- If the page title contains a cutoff-year marker, use one of safe_subject_aliases when you need to name the subject; do not use the cutoff-year title text.\n"
        f"- Do not make the question text depend on events in {cutoff_year} or later.\n"
        "- The question must be self-contained. It should be answerable without seeing the list or the table. Do not ask `What is ... in the list(table)?`.\n"
        # "- Do not cite the list unless the source is a well-known named chart or list, such as a Billboard chart, UNESCO list or a sports tournament chart. Phrases to avoid: `according to the table`, `according to the [source] table`, or `in the List of ...`. \n"
        # "- Ask about the facts in the table. Do not ask questions about the table itself, such as `What year does the estimate refer to`.\n"
        # "- Rendered markdown preserves table layout: a non-empty cell followed by blank cells may represent an HTML colspan cell. Treat it as one spanned cell, not as repeated field values.\n"
        # "- Full-width or partial-width spanned rows can appear anywhere in a table. Use them as local visual/context labels for nearby rows, not as direct answers to unrelated fields.\n"
        f"{toy_table_instruction}"
        "- Treat curated list pages such as `List of national parks of the United States` as complete and authoritative for membership within their stated scope. Do not hedge by saying `according to the List of ...`.\n"
        "### Other prompt rules:\n\n"
        f"{_extra_prompt_rule(normalized_extra_prompts)}"
        "- Do not include the answer or answer aliases in the question or search queries.\n"
        f"- Generate exactly {search_query_count} answer-blind search queries.\n"
        f"- Verify whether the generated question and answer match the allowed answer type {', '.join(normalized_allowed_answer_types)}. If not, discard the question, set other fields empty, and write `discard_reason` in your response.\n"
        f"{_discard_prompt_rule(normalized_allowed_reasoning_types)}"
        "\nOutput schema:\n"
        "{\n"
        '  "question": string,\n'
        '  "answer": string | string[],\n'
        f'  "answer_type": "{_answer_type_schema(normalized_allowed_answer_types)}",\n'
        '  "answer_aliases": string[],\n'
        '  "search_queries": string[],\n'
        f'  "reasoning_type": "{_reasoning_type_schema(normalized_allowed_reasoning_types)}",\n'
        '  "source_table": integer,\n'
        '  "derivation_summary": string,\n'
        '  "discard_reason": string | null\n'
        "}\n\n"
        f"Payload:\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )


def normalize_route3_reasoning_types(values: Iterable[str] | str | None) -> tuple[str, ...]:
    """Return normalized configured Route 3 reasoning types."""
    if values is None:
        return ()
    raw_values: Iterable[str]
    if isinstance(values, str):
        raw_values = [values]
    else:
        raw_values = values
    normalized_values: list[str] = []
    seen: set[str] = set()
    for raw_value in raw_values:
        for part in str(raw_value or "").split(","):
            normalized = _normalize_reasoning_type_value(part)
            if not normalized:
                continue
            if normalized not in ROUTE3_REASONING_TYPE_SET:
                allowed = ", ".join(ROUTE3_REASONING_TYPES)
                raise ValueError(f"Unsupported Route 3 reasoning_type {part!r}. Allowed values: {allowed}.")
            if normalized not in seen:
                normalized_values.append(normalized)
                seen.add(normalized)
    return tuple(normalized_values)


def normalize_route3_answer_types(values: Iterable[str] | str | None) -> tuple[str, ...]:
    """Return normalized configured Route 3 answer types."""
    if values is None:
        return ()
    raw_values: Iterable[str]
    if isinstance(values, str):
        raw_values = [values]
    else:
        raw_values = values
    normalized_values: list[str] = []
    seen: set[str] = set()
    for raw_value in raw_values:
        for part in str(raw_value or "").split(","):
            normalized = _normalize_answer_type_value(part)
            if not normalized:
                continue
            if normalized not in ROUTE3_ANSWER_TYPE_SET:
                allowed = ", ".join(ROUTE3_ANSWER_TYPES)
                raise ValueError(f"Unsupported Route 3 answer_type {part!r}. Allowed values: {allowed}.")
            if normalized not in seen:
                normalized_values.append(normalized)
                seen.add(normalized)
    return tuple(normalized_values)


def normalize_route3_extra_prompts(values: Iterable[str] | str | None) -> tuple[str, ...]:
    """Return expanded stricter prompt rules for Route 3."""
    if values is None:
        return ()
    raw_values: Iterable[str]
    if isinstance(values, str):
        raw_values = [values]
    else:
        raw_values = values
    normalized_values: list[str] = []
    seen: set[str] = set()
    for raw_value in raw_values:
        direct_prompt = _normalize_extra_prompt(raw_value)
        if direct_prompt and (direct_prompt != str(raw_value or "").strip() or direct_prompt in ROUTE3_EXTRA_PROMPTS.values()):
            parts = [direct_prompt]
        else:
            parts = [
                _normalize_extra_prompt(part)
                for part in str(raw_value or "").split(",")
            ]
        for prompt in parts:
            if not prompt:
                continue
            if prompt not in seen:
                normalized_values.append(prompt)
                seen.add(prompt)
    return tuple(normalized_values)


def normalize_route3_table_filter_modes(values: Iterable[str] | str | None) -> tuple[str, ...]:
    """Return normalized configured Route 3 table prefilter modes."""
    if values is None:
        return ()
    raw_values: Iterable[str]
    if isinstance(values, str):
        raw_values = [values]
    else:
        raw_values = values
    normalized_values: list[str] = []
    seen: set[str] = set()
    for raw_value in raw_values:
        for part in str(raw_value or "").split(","):
            normalized = _normalize_table_filter_mode(part)
            if not normalized:
                continue
            if normalized not in ROUTE3_TABLE_FILTER_MODE_SET:
                allowed = ", ".join(ROUTE3_TABLE_FILTER_MODES)
                raise ValueError(f"Unsupported Route 3 table filter mode {part!r}. Allowed values: {allowed}.")
            if normalized not in seen:
                normalized_values.append(normalized)
                seen.add(normalized)
    return tuple(normalized_values)


def _reasoning_type_prompt_rule(allowed_reasoning_types: tuple[str, ...]) -> str:
    """Return the Route 3 prompt rule for configured reasoning types."""
    reasoning_types = allowed_reasoning_types or ROUTE3_REASONING_TYPES
    if len(reasoning_types) == 1:
        reasoning_type = reasoning_types[0]
        return (
            f"- Use only `{reasoning_type}` reasoning_type: "
            f"{ROUTE3_REASONING_TYPE_PROMPT_RULES[reasoning_type]}.\n"
        )
    if not allowed_reasoning_types:
        return (
            "- Choose exactly one reasoning_type from "
            f"{', '.join(f'`{value}`' for value in ROUTE3_REASONING_TYPES)}. "
            "Use the matching rule below and no other reasoning_type rule.\n"
            f"{_type_rule_lines(ROUTE3_REASONING_TYPE_PROMPT_RULES, reasoning_types)}"
        )
    allowed_text = ", ".join(f"`{value}`" for value in allowed_reasoning_types)
    return (
        f"- Use only these reasoning_type values: {allowed_text}. "
        "Use the matching rule below and no other reasoning_type rule.\n"
        f"{_type_rule_lines(ROUTE3_REASONING_TYPE_PROMPT_RULES, reasoning_types)}"
    )


def _route3_stability_prompt_rule() -> str:
    """Return the Route 3 settled-answer rule without duplicating shared wording."""
    return (
        "- Only ask for an answer that is historically settled in the provided table content and cannot change; "
        "reject mutable statuses, current roles, live affiliations, and other facts whose answer can change over time.\n"
    )


def _answer_type_prompt_rule(allowed_answer_types: tuple[str, ...]) -> str:
    """Return the Route 3 prompt rule for configured answer types."""
    answer_types = allowed_answer_types or ROUTE3_ANSWER_TYPES
    if len(answer_types) == 1:
        answer_type = answer_types[0]
        return (
            f"- Use only `{answer_type}` answer_type: "
            f"{ROUTE3_ANSWER_TYPE_PROMPT_RULES[answer_type]}.\n"
        )
    if not allowed_answer_types:
        return (
            "- Choose exactly one SimpleQA Verified answer_type from "
            f"{', '.join(f'`{value}`' for value in ROUTE3_ANSWER_TYPES)}. "
            "Use the matching rule below and no other answer_type rule.\n"
            f"{_type_rule_lines(ROUTE3_ANSWER_TYPE_PROMPT_RULES, answer_types)}"
        )
    allowed_text = ", ".join(f"`{value}`" for value in allowed_answer_types)
    return (
        f"- Use only these answer_type values: {allowed_text}. "
        "Use the matching rule below and no other answer_type rule.\n"
        f"{_type_rule_lines(ROUTE3_ANSWER_TYPE_PROMPT_RULES, answer_types)}"
    )


def _type_rule_lines(rule_map: dict[str, str], values: tuple[str, ...]) -> str:
    """Return one explanatory rule per configured type."""
    return "".join(f"- `{value}`: {rule_map[value]}.\n" for value in values)

def _tie_answer_prompt_rule(allowed_reasoning_types: tuple[str, ...]) -> str:
    """Return tie-answer guidance when a tied reasoning operation is available."""
    if allowed_reasoning_types and not {"max", "min", "ordinal", "count"}.intersection(allowed_reasoning_types):
        return ""
    return "- If max/min/ordinal/count has tied answers, return answer as a JSON array containing every tied answer.\n"


def _discard_prompt_rule(allowed_reasoning_types: tuple[str, ...]) -> str:
    """Return the prompt rule for impossible generation cases."""
    if allowed_reasoning_types:
        return "- If no safe question matching the allowed reasoning_type rules is possible, set discard_reason and leave the other fields empty.\n\n"
    return "- If no safe single fact or table reasoning question is possible, set discard_reason and leave the other fields empty.\n\n"


def _reasoning_type_schema(allowed_reasoning_types: tuple[str, ...]) -> str:
    """Return the prompt schema value for reasoning_type."""
    return "|".join(allowed_reasoning_types or ROUTE3_REASONING_TYPES)


def _answer_type_schema(allowed_answer_types: tuple[str, ...]) -> str:
    """Return the prompt schema value for answer_type."""
    return "|".join(allowed_answer_types or ROUTE3_ANSWER_TYPES)


def _answer_precision_prompt_rule(allowed_answer_types: tuple[str, ...]) -> str:
    """Return precision wording only for answer types available in this run."""
    if not allowed_answer_types:
        return ANSWER_PRECISION_PROMPT_RULES
    parts: list[str] = []
    if "Date" in allowed_answer_types:
        parts.append(DATE_PRECISION_PROMPT_RULES)
    if "Number" in allowed_answer_types:
        parts.append(NUMBER_PRECISION_PROMPT_RULES)
    if "Place" in allowed_answer_types:
        parts.append(PLACE_PRECISION_PROMPT_RULES)
    return "".join(parts)


def _extra_prompt_rule(extra_prompts: tuple[str, ...]) -> str:
    """Return optional stricter prompt rules."""
    return "".join(f"- {prompt.rstrip('.')}.\n" for prompt in extra_prompts)


def extract_wikipedia_tables(html: str) -> list[WikipediaTable]:
    """Extract infobox and wikitable records from MediaWiki parse HTML."""
    parser = _WikipediaTableParser()
    parser.feed(html)
    return [
        _build_wikipedia_table(index + 1, frame)
        for index, frame in enumerate(parser.frames)
    ]


def extract_first_paragraph(html: str) -> str:
    """Extract the first non-empty paragraph from a MediaWiki parse HTML fragment."""
    parser = _FirstParagraphParser()
    parser.feed(html)
    return _clean_text(" ".join(parser.paragraphs[0])) if parser.paragraphs else ""


def extract_non_table_prose(html: str) -> str:
    """Extract readable prose outside tables for table-leakage scoring."""
    parser = _NonTableProseParser()
    parser.feed(html)
    return _clean_text(" ".join(parser.parts))


def rank_wikipedia_tables(
    tables: list[WikipediaTable],
    *,
    first_paragraph: str,
    prose_text: str,
) -> list[dict[str, Any]]:
    """Rank tables by structured composition value and low prose leakage."""
    normalized_prose = normalize_name(f"{first_paragraph} {prose_text}")
    ranked: list[dict[str, Any]] = []
    for table in tables:
        data_rows = _data_rows(table)
        row_count = len(data_rows)
        header_text = " ".join(table.headers).lower()
        numeric_cell_count = sum(
            1
            for row in data_rows
            for cell in row
            if _is_numeric_value_cell(cell)
        )
        comparable_header_hits = sorted(
            hint for hint in COMPOSITION_HEADER_HINTS if hint in header_text
        )
        table_context = " ".join(
            [table.section_heading, table.caption, table.nearby_intro, " ".join(table.headers)]
        ).lower()
        preferred_context_hits = sorted(
            hint for hint in PREFERRED_TABLE_HINTS if hint in table_context
        )
        mutable_context_hits = sorted(
            hint for hint in MUTABLE_OR_PLACEHOLDER_TABLE_HINTS if hint in table_context
        )
        live_scope_reason = _live_table_scope_rejection_reason(table)
        zero_numeric_count = sum(
            1
            for row in data_rows
            for cell in row
            if _is_zero_numeric_value_cell(cell)
        )
        zero_numeric_rate = zero_numeric_count / numeric_cell_count if numeric_cell_count else 0.0
        leaked_values, checked_values = _prose_leakage_counts(table, normalized_prose)
        leakage_rate = leaked_values / checked_values if checked_values else 0.0
        score = 0.0
        reasons: list[str] = []
        if row_count >= 3:
            score += min(row_count, 12) * 0.15
            reasons.append("multi_row")
        else:
            score -= 1.0
            reasons.append("too_few_rows")
        if table.headers:
            score += 1.0
            reasons.append("has_headers")
        if ENABLE_NUMERIC_TABLE_RANKING_POINTS and numeric_cell_count:
            score += min(numeric_cell_count, 20) * 0.1
            reasons.append("numeric_values")
        if ENABLE_NUMERIC_TABLE_RANKING_POINTS and comparable_header_hits:
            score += 3.0
            reasons.append("comparable_headers")
        elif ENABLE_NUMERIC_TABLE_RANKING_POINTS:
            score -= 1.0
            reasons.append("no_comparable_headers")
        if preferred_context_hits:
            score += 2.5
            reasons.append("preferred_table_context")
        if mutable_context_hits:
            score -= 3.0
            reasons.append("mutable_or_placeholder_context")
        if live_scope_reason:
            score -= 5.0
            reasons.append("live_table_scope")
        if ENABLE_NUMERIC_TABLE_RANKING_POINTS and zero_numeric_rate >= 0.5 and numeric_cell_count >= 6:
            score -= 4.0
            reasons.append("zero_dominant_numeric_values")
        if leakage_rate <= 0.2:
            score += 2.0
            reasons.append("low_prose_leakage")
        elif leakage_rate >= 0.6:
            score -= 2.0
            reasons.append("high_prose_leakage")
        if len(table.normalized_text) > 10000:
            score -= 1.0
            reasons.append("large_table_penalty")
        ranked.append(
            {
                "table": table,
                "table_index": table.table_index,
                "table_type": table.table_type,
                "caption": table.caption,
                "section_heading": table.section_heading,
                "nearby_intro": table.nearby_intro[:1000],
                "score": round(score, 4),
                "reasons": reasons,
                "row_count": row_count,
                "numeric_cell_count": numeric_cell_count,
                "comparable_header_hits": comparable_header_hits,
                "preferred_context_hits": preferred_context_hits,
                "mutable_context_hits": mutable_context_hits,
                "live_scope_rejection_reason": live_scope_reason,
                "zero_numeric_rate": round(zero_numeric_rate, 4),
                "prose_leakage": {
                    "checked_values": checked_values,
                    "leaked_values": leaked_values,
                    "leakage_rate": round(leakage_rate, 4),
                },
            }
        )
    return sorted(
        ranked,
        key=lambda row: (
            float(row["score"]),
            int(row["row_count"]),
            int(row["numeric_cell_count"]) if ENABLE_NUMERIC_TABLE_RANKING_POINTS else 0,
        ),
        reverse=True,
    )


def _annotate_table_score_cutoff(
    table_selection: list[dict[str, Any]],
    min_table_score: float,
) -> list[dict[str, Any]]:
    """Mark ranked tables that are below the configured score cutoff."""
    annotated: list[dict[str, Any]] = []
    threshold = float(min_table_score)
    for row in table_selection:
        score = _selection_score(row)
        copied = dict(row)
        copied["min_table_score"] = threshold
        copied["below_min_table_score"] = score < threshold
        if copied["below_min_table_score"]:
            reasons = list(copied.get("reasons", []))
            if "below_min_table_score" not in reasons:
                reasons.append("below_min_table_score")
            copied["reasons"] = reasons
        annotated.append(copied)
    return annotated


def _annotate_table_filter_modes(
    table_selection: list[dict[str, Any]],
    table_filter_modes: Iterable[str] | str | None,
) -> list[dict[str, Any]]:
    """Mark ranked tables rejected by configured early table filter modes."""
    modes = normalize_route3_table_filter_modes(table_filter_modes)
    annotated: list[dict[str, Any]] = []
    for row in table_selection:
        copied = dict(row)
        reasons: list[str] = []
        table = copied.get("table")
        copied["table_filter_modes"] = list(modes)
        if isinstance(table, WikipediaTable):
            if "no_picture_heavy_tables" in modes:
                picture_stats = _picture_heavy_table_stats(table)
                copied["picture_heavy_table_stats"] = picture_stats
                picture_reason = _picture_heavy_table_filter_reason(table, picture_stats)
                if picture_reason:
                    reasons.append(picture_reason)
            if "no_incomplete_tables" in modes:
                incomplete_markers = _incomplete_table_markers(table)
                copied["incomplete_table_markers"] = incomplete_markers
                if incomplete_markers:
                    reasons.append(f"no_incomplete_tables:{','.join(incomplete_markers)}")
            if not reasons and "not_number_dominant" in modes:
                number_dominance_stats = _number_dominance_table_stats(table)
                copied["number_dominance_stats"] = number_dominance_stats
                number_dominance_reason = _number_dominance_table_filter_reason(number_dominance_stats)
                if number_dominance_reason:
                    reasons.append(number_dominance_reason)
            if not reasons and "no_social_science_research" in modes:
                markers = _table_text_markers(table, SOCIAL_SCIENCE_TABLE_MARKERS)
                copied["social_science_markers"] = markers
                if markers:
                    reasons.append(f"no_social_science_research:{','.join(markers)}")
        copied["table_filter_rejection_reasons"] = reasons
        copied["table_filter_rejection_reason"] = ";".join(reasons)
        if reasons:
            row_reasons = list(copied.get("reasons", []))
            for reason in reasons:
                mode = reason.split(":", 1)[0]
                if mode not in row_reasons:
                    row_reasons.append(mode)
            copied["reasons"] = row_reasons
        annotated.append(copied)
    return annotated


def _table_score_cutoff_discard_reason(rows: list[dict[str, Any]], min_table_score: float) -> str:
    """Return a concise rejection reason when no table meets the score cutoff."""
    best_score = max((_selection_score(row) for row in rows), default=0.0)
    return f"table_score_below_minimum:min_table_score={float(min_table_score):.4f};best_score={best_score:.4f}"


def _table_filter_discard_reason(rows: list[dict[str, Any]]) -> str:
    """Return a concise rejection reason for table prefilter drops."""
    for row in rows:
        reason = str(row.get("table_filter_rejection_reason", "")).strip()
        if reason:
            return reason
    return "route3_table_filter_rejected"


def _incomplete_table_markers(table: WikipediaTable) -> list[str]:
    """Return incomplete-data markers present in table-owned text."""
    checked_text = _table_marker_text(table)
    return _text_exact_markers(checked_text, INCOMPLETE_TABLE_MARKERS)


def _picture_heavy_table_stats(table: WikipediaTable) -> dict[str, Any]:
    """Return audit stats for tables dominated by image-bearing cells."""
    structure = table.structure if isinstance(table.structure, dict) else {}
    image_covered = int(structure.get("image_covered_cell_count", 0) or 0)
    total_covered = int(structure.get("total_cell_coverage_count", 0) or 0)
    image_raw = int(structure.get("image_raw_cell_count", 0) or 0)
    total_raw = int(structure.get("raw_cell_count", 0) or 0)
    rate = image_covered / total_covered if total_covered > 0 else 0.0
    return {
        "image_raw_cell_count": image_raw,
        "raw_cell_count": total_raw,
        "image_covered_cell_count": image_covered,
        "total_cell_coverage_count": total_covered,
        "image_cell_rate": round(rate, 4),
        "image_cell_rate_threshold": PICTURE_HEAVY_TABLE_MAX_IMAGE_CELL_RATE,
    }


def _picture_heavy_table_filter_reason(table: WikipediaTable, stats: dict[str, Any]) -> str:
    """Return the picture-heavy rejection reason for one table, if any."""
    image_rate = float(stats.get("image_cell_rate", 0.0) or 0.0)
    image_count = int(stats.get("image_covered_cell_count", 0) or 0)
    if table.table_type == "wikitable" and image_count:
        return f"no_picture_heavy_tables:wikitable_image_cell_count={image_count}"
    if table.table_type == "infobox" and image_count and image_rate > PICTURE_HEAVY_TABLE_MAX_IMAGE_CELL_RATE:
        return f"no_picture_heavy_tables:image_cell_rate={image_rate:.4f}"
    return ""


def _number_dominance_table_stats(table: WikipediaTable) -> dict[str, Any]:
    """Return audit stats for the not-number-dominant table prefilter."""
    marker_text = _table_marker_text(table)
    word_markers = _text_exact_markers(marker_text, NUMBER_DOMINANCE_WORD_MARKERS)
    unit_markers = _dedupe_preserving_order(
        [
            *_text_exact_markers(marker_text, NUMBER_DOMINANCE_UNIT_MARKERS),
            *_text_regex_markers(marker_text, NUMBER_DOMINANCE_UNIT_REGEX_PATTERNS),
            *_ambiguous_unit_markers(table),
        ]
    )
    numeric_entries = _number_dominance_numeric_entries(table)
    comma_entries = [entry for entry in numeric_entries if bool(entry["has_comma"])]
    decimal_entries = [entry for entry in numeric_entries if bool(entry["has_decimal"])]
    out_of_range_entries = [
        entry for entry in numeric_entries if bool(entry["is_out_of_allowed_no_comma_range"])
    ]
    alpha_count, total_count, alpha_rate = _table_alpha_coverage(table)
    return {
        "numeric_token_count": len(numeric_entries),
        "word_markers": word_markers,
        "unit_markers": unit_markers,
        "comma_number_count": len(comma_entries),
        "comma_number_values": [str(entry["token"]) for entry in comma_entries[:20]],
        "decimal_number_count": len(decimal_entries),
        "decimal_number_values": [str(entry["token"]) for entry in decimal_entries[:20]],
        "out_of_allowed_no_comma_range_count": len(out_of_range_entries),
        "out_of_allowed_no_comma_range_values": [str(entry["token"]) for entry in out_of_range_entries[:20]],
        "alpha_character_count": alpha_count,
        "total_character_count": total_count,
        "alpha_character_rate": round(alpha_rate, 4),
        "alpha_character_threshold": NUMBER_DOMINANCE_MIN_ALPHA_RATE,
    }


def _number_dominance_table_filter_reason(stats: dict[str, Any]) -> str:
    """Return the not-number-dominant rejection reason for one table, if any."""
    markers = stats.get("word_markers", [])
    if markers:
        return f"not_number_dominant:word_marker={','.join(str(marker) for marker in markers)}"
    unit_markers = stats.get("unit_markers", [])
    if unit_markers:
        return f"not_number_dominant:unit_marker={','.join(str(marker) for marker in unit_markers)}"
    comma_count = int(stats.get("comma_number_count", 0) or 0)
    if comma_count:
        return f"not_number_dominant:comma_number_count={comma_count}"
    decimal_count = int(stats.get("decimal_number_count", 0) or 0)
    if decimal_count:
        return f"not_number_dominant:decimal_number_count={decimal_count}"
    out_of_range_count = int(stats.get("out_of_allowed_no_comma_range_count", 0) or 0)
    if out_of_range_count:
        return f"not_number_dominant:out_of_allowed_no_comma_range_count={out_of_range_count}"
    alpha_rate = float(stats.get("alpha_character_rate", 1.0) or 0.0)
    if alpha_rate <= NUMBER_DOMINANCE_MIN_ALPHA_RATE:
        return f"not_number_dominant:alpha_character_rate={alpha_rate:.4f}"
    return ""


def _number_dominance_numeric_entries(table: WikipediaTable) -> list[dict[str, Any]]:
    """Return numeric tokens from the table for number-dominance filtering."""
    entries: list[dict[str, Any]] = []
    for text in _table_number_texts(table):
        cleaned = _strip_footnote_markers(str(text or ""))
        for match in NUMBER_PATTERN.finditer(cleaned):
            token = match.group(0)
            parsed = parse_number_token(token)
            if parsed is None:
                continue
            has_comma = "," in token
            has_decimal = "." in token
            entries.append(
                {
                    "token": token,
                    "value": parsed,
                    "has_comma": has_comma,
                    "has_decimal": has_decimal,
                    "is_out_of_allowed_no_comma_range": (
                        not has_comma
                        and not has_decimal
                        and _is_out_of_allowed_no_comma_number(parsed)
                    ),
                }
            )
    return entries


def _is_out_of_allowed_no_comma_number(value: Any) -> bool:
    """Return whether a no-comma integer sits outside the allowed year-like window."""
    if abs(value) <= NUMBER_DOMINANCE_LOW_NUMERIC_THRESHOLD:
        return False
    return not (
        NUMBER_DOMINANCE_YEAR_LIKE_MIN <= abs(value) <= NUMBER_DOMINANCE_YEAR_LIKE_MAX
    )


def _table_alpha_coverage(table: WikipediaTable) -> tuple[int, int, float]:
    """Return alphabetic character coverage over table-owned non-whitespace text."""
    text = "".join(str(part or "") for part in _table_number_texts(table))
    alpha_count = sum(1 for char in text if char.isalpha())
    total_count = sum(1 for char in text if not char.isspace())
    if total_count <= 0:
        return alpha_count, total_count, 1.0
    return alpha_count, total_count, alpha_count / total_count


def _table_number_texts(table: WikipediaTable) -> list[str]:
    """Return table-owned text fields to scan for numeric table filters."""
    texts = [table.section_heading, table.caption]
    texts.extend(cell for row in table.rows for cell in row)
    return texts


def _table_marker_text(table: WikipediaTable) -> str:
    """Return normalized table/context text for exact marker checks."""
    return _normalize_marker_text(
        " ".join(
            [
                table.section_heading,
                table.caption,
                table.nearby_intro,
                " ".join(table.headers),
                table.normalized_text,
            ]
        )
    )


def _normalize_marker_text(text: str) -> str:
    """Normalize marker text without deleting parenthetical content."""
    normalized = unicodedata.normalize("NFKD", text)
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    normalized = normalized.lower()
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _text_exact_markers(checked_text: str, markers: Iterable[str]) -> list[str]:
    """Return exact word/phrase markers present in normalized text."""
    hits: list[str] = []
    for marker in markers:
        normalized_marker = _normalize_marker_text(marker)
        if not normalized_marker:
            continue
        pattern = rf"(?<!\w){re.escape(normalized_marker)}(?!\w)"
        if re.search(pattern, checked_text):
            hits.append(marker)
    return hits


def _text_regex_markers(checked_text: str, patterns: Iterable[re.Pattern[str]]) -> list[str]:
    """Return normalized marker hits captured by regex patterns."""
    hits: list[str] = []
    for pattern in patterns:
        hits.extend(match.group(0) for match in pattern.finditer(checked_text))
    return hits


def _ambiguous_unit_markers(table: WikipediaTable) -> list[str]:
    """Return short unit markers only when raw text gives unit-like context."""
    texts = _table_number_texts(table)
    hits: list[str] = []
    for marker in NUMBER_DOMINANCE_AMBIGUOUS_UNIT_MARKERS:
        escaped = re.escape(marker)
        number_unit_pattern = re.compile(
            rf"(?<![\w.])-?(?:\d{{1,3}}(?:,\d{{3}})+|\d+)(?:\.\d+)?\s*{escaped}(?!\w)",
            flags=re.IGNORECASE,
        )
        parenthetical_pattern = re.compile(rf"[\(\[]\s*{escaped}\s*[\)\]]", flags=re.IGNORECASE)
        slash_pattern = re.compile(rf"(?<!\w){escaped}\s*/\s*[a-z]+", flags=re.IGNORECASE)
        if any(
            number_unit_pattern.search(text)
            or parenthetical_pattern.search(text)
            or slash_pattern.search(text)
            for text in texts
        ):
            hits.append(marker)
    return hits


def _dedupe_preserving_order(values: Iterable[str]) -> list[str]:
    """Return unique non-empty strings in first-seen order."""
    deduped: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value).strip()
        if not text or text in seen:
            continue
        deduped.append(text)
        seen.add(text)
    return deduped


def _table_text_markers(table: WikipediaTable, markers: Iterable[str]) -> list[str]:
    """Return markers present in normalized table text."""
    checked_text = normalize_name(
        " ".join(
            [
                table.section_heading,
                table.caption,
                table.nearby_intro,
                " ".join(table.headers),
                table.normalized_text,
            ]
        )
    )
    return [marker for marker in markers if marker in checked_text]


def _selection_score(row: dict[str, Any]) -> float:
    """Return one ranked table score as a float."""
    try:
        return float(row.get("score", 0.0))
    except (TypeError, ValueError):
        return 0.0


class _FirstParagraphParser(HTMLParser):
    """Minimal paragraph text collector."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._in_paragraph = False
        self._current: list[str] = []
        self.paragraphs: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag == "p" and not self.paragraphs:
            self._in_paragraph = True
            self._current = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "p" and self._in_paragraph:
            text = _clean_text(" ".join(self._current))
            if text:
                self.paragraphs.append([text])
            self._in_paragraph = False

    def handle_data(self, data: str) -> None:
        if self._in_paragraph:
            self._current.append(data)


class _NonTableProseParser(HTMLParser):
    """Collect readable text outside table/script/style fragments."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._table_depth = 0
        self._suppressed_tag = ""

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag == "table":
            self._table_depth += 1
        elif tag in {"script", "style"}:
            self._suppressed_tag = tag

    def handle_endtag(self, tag: str) -> None:
        if tag == "table" and self._table_depth:
            self._table_depth -= 1
        elif tag == self._suppressed_tag:
            self._suppressed_tag = ""

    def handle_data(self, data: str) -> None:
        if self._table_depth or self._suppressed_tag:
            return
        text = _clean_text(data)
        if text:
            self.parts.append(text)


def _positive_cell_span(value: Any, *, default: int = 1) -> int:
    """Return a positive HTML table cell span."""
    try:
        parsed = int(str(value or "").strip())
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


class _WikipediaTableParser(HTMLParser):
    """Small HTML parser for Wikipedia infoboxes and wikitables."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.frames: list[dict[str, Any]] = []
        self.current_heading = ""
        self._last_paragraph = ""
        self._heading_tag = ""
        self._heading_parts: list[str] = []
        self._active_paragraph = False
        self._paragraph_parts: list[str] = []
        self._active_table: dict[str, Any] | None = None
        self._table_depth = 0
        self._active_row: list[dict[str, Any]] | None = None
        self._active_cell: dict[str, Any] | None = None
        self._active_caption: list[str] | None = None

    def handle_starttag(self, tag: str, attrs) -> None:
        attr_map = {name: value or "" for name, value in attrs}
        if tag in {"h2", "h3", "h4"}:
            self._heading_tag = tag
            self._heading_parts = []
            return
        if tag == "p" and self._active_table is None:
            self._active_paragraph = True
            self._paragraph_parts = []
            return
        if tag == "table":
            if self._active_table is not None:
                self._table_depth += 1
                self._active_table["nested_table_count"] = int(self._active_table.get("nested_table_count", 0)) + 1
                return
            class_text = attr_map.get("class", "")
            table_type = _table_type(class_text)
            if not table_type:
                return
            self._active_table = {
                "table_type": table_type,
                "section_heading": self.current_heading,
                "caption": "",
                "nearby_intro": self._last_paragraph,
                "rows": [],
                "nested_table_count": 0,
            }
            self._table_depth = 1
            return
        if self._active_table is None or self._table_depth != 1:
            return
        if tag == "caption":
            self._active_caption = []
        elif tag == "tr":
            self._active_row = []
        elif tag in {"th", "td"} and self._active_row is not None:
            self._active_cell = {
                "text_parts": [],
                "header": tag == "th",
                "rowspan": _positive_cell_span(attr_map.get("rowspan", ""), default=1),
                "colspan": _positive_cell_span(attr_map.get("colspan", ""), default=1),
                "image_count": 0,
            }
        elif tag == "img" and self._active_cell is not None:
            self._active_cell["image_count"] = int(self._active_cell.get("image_count", 0) or 0) + 1

    def handle_startendtag(self, tag: str, attrs) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        if tag == self._heading_tag:
            heading = _clean_text(" ".join(self._heading_parts))
            if heading:
                self.current_heading = heading
                self._last_paragraph = ""
            self._heading_tag = ""
            self._heading_parts = []
            return
        if tag == "p" and self._active_paragraph:
            paragraph = _clean_text(" ".join(self._paragraph_parts))
            if paragraph:
                self._last_paragraph = paragraph
            self._active_paragraph = False
            self._paragraph_parts = []
            return
        if self._active_table is None:
            return
        if tag == "table":
            self._table_depth -= 1
            if self._table_depth <= 0:
                self.frames.append(self._active_table)
                self._active_table = None
                self._active_row = None
                self._active_cell = None
                self._active_caption = None
            return
        if self._table_depth != 1:
            return
        if tag in {"th", "td"} and self._active_cell is not None:
            text = _clean_cell_text(" ".join(self._active_cell["text_parts"]))
            if self._active_row is not None:
                self._active_row.append(
                    {
                        "text": text,
                        "header": bool(self._active_cell["header"]),
                        "rowspan": int(self._active_cell.get("rowspan", 1)),
                        "colspan": int(self._active_cell.get("colspan", 1)),
                        "image_count": int(self._active_cell.get("image_count", 0) or 0),
                    }
                )
            self._active_cell = None
        elif tag == "tr" and self._active_row is not None:
            if self._active_row:
                self._active_table["rows"].append(self._active_row)
            self._active_row = None
        elif tag == "caption" and self._active_caption is not None:
            self._active_table["caption"] = _clean_text(" ".join(self._active_caption))
            self._active_caption = None

    def handle_data(self, data: str) -> None:
        if self._heading_tag:
            self._heading_parts.append(data)
        if self._active_paragraph:
            self._paragraph_parts.append(data)
        if self._active_table is None or self._table_depth != 1:
            return
        if self._active_cell is not None:
            self._active_cell["text_parts"].append(data)
        elif self._active_caption is not None:
            self._active_caption.append(data)


def _expand_table_grid(raw_rows: list[list[dict[str, Any]]]) -> tuple[list[list[str]], list[list[bool]]]:
    """Expand HTML rowspan/colspan cells into a rectangular text grid."""
    grid: list[list[str]] = []
    header_grid: list[list[bool]] = []
    pending: dict[int, dict[str, Any]] = {}

    def consume_pending(column: int, row_values: list[str], row_headers: list[bool]) -> bool:
        pending_cell = pending.get(column)
        if pending_cell is None:
            return False
        row_values.append(str(pending_cell.get("text", "")).strip())
        row_headers.append(bool(pending_cell.get("header", False)))
        pending_cell["remaining"] = int(pending_cell.get("remaining", 0)) - 1
        if int(pending_cell.get("remaining", 0)) <= 0:
            pending.pop(column, None)
        return True

    for raw_row in raw_rows:
        row_values: list[str] = []
        row_headers: list[bool] = []
        column = 0
        for cell in raw_row:
            while consume_pending(column, row_values, row_headers):
                column += 1
            text = str(cell.get("text", "")).strip()
            is_header = bool(cell.get("header"))
            rowspan = _positive_cell_span(cell.get("rowspan", 1), default=1)
            colspan = _positive_cell_span(cell.get("colspan", 1), default=1)
            for offset in range(colspan):
                spanned_text = text if offset == 0 else ""
                row_values.append(spanned_text)
                row_headers.append(is_header)
                if rowspan > 1:
                    pending[column + offset] = {
                        "text": spanned_text,
                        "header": is_header,
                        "remaining": rowspan - 1,
                    }
            column += colspan
        while pending and column <= max(pending):
            if not consume_pending(column, row_values, row_headers):
                row_values.append("")
                row_headers.append(False)
            column += 1
        if row_values:
            grid.append(row_values)
            header_grid.append(row_headers)

    width = max((len(row) for row in grid), default=0)
    for row, header_row in zip(grid, header_grid):
        if len(row) < width:
            row.extend([""] * (width - len(row)))
            header_row.extend([False] * (width - len(header_row)))
    return grid, header_grid


def _header_row_count(grid: list[list[str]], header_grid: list[list[bool]]) -> int:
    """Return the number of consecutive top rows that are table headers."""
    count = 0
    for row, header_row in zip(grid, header_grid):
        if _is_full_width_context_grid_row(row, header_row):
            break
        if row and any(cell.strip() for cell in row) and all(header_row):
            count += 1
            continue
        break
    return count


def _is_full_width_context_grid_row(row: list[str], header_row: list[bool]) -> bool:
    """Return whether a rendered row is a full-width context label, not column headers."""
    if len(row) <= 1 or not all(header_row):
        return False
    return sum(1 for cell in row if cell.strip()) == 1


def _combined_markdown_headers(grid: list[list[str]], header_row_count: int) -> list[str]:
    """Combine one or more expanded header rows into Markdown column names."""
    if not grid:
        return []
    width = len(grid[0])
    if header_row_count <= 0:
        return [f"Column {index + 1}" for index in range(width)]
    headers: list[str] = []
    for column in range(width):
        parts: list[str] = []
        seen: set[str] = set()
        for row in _header_rows_for_combination(grid[:header_row_count]):
            value = row[column].strip()
            normalized = normalize_name(value)
            if value and normalized not in seen:
                parts.append(value)
                seen.add(normalized)
        if parts:
            headers.append(" / ".join(parts))
        elif header_row_count == 1:
            headers.append("")
        else:
            headers.append(f"Column {column + 1}")
    return headers


def _header_rows_for_combination(header_rows: list[list[str]]) -> list[list[str]]:
    """Propagate parent headers only when child header rows exist."""
    if len(header_rows) <= 1:
        return header_rows
    combined_rows: list[list[str]] = []
    for row in header_rows:
        filled: list[str] = []
        active = ""
        for value in row:
            text = value.strip()
            if text:
                active = text
                filled.append(value)
            else:
                filled.append(active)
        combined_rows.append(filled)
    return combined_rows


def _markdown_cell(value: str) -> str:
    """Escape a table cell for GitHub-flavored Markdown."""
    cleaned = _clean_text(str(value).replace("\r", " ").replace("\n", " "))
    return cleaned.replace("|", "\\|")


def _grid_to_markdown(headers: list[str], data_rows: list[list[str]]) -> str:
    """Render a rectangular grid as a GitHub-flavored Markdown table."""
    if not headers:
        return ""
    width = len(headers)
    lines = [
        "| " + " | ".join(_markdown_cell(header) for header in headers) + " |",
        "| " + " | ".join("---" for _ in range(width)) + " |",
    ]
    for row in data_rows:
        padded = [*row[:width], *([""] * max(0, width - len(row)))]
        lines.append("| " + " | ".join(_markdown_cell(cell) for cell in padded[:width]) + " |")
    return "\n".join(lines)


def _full_width_heading_rows(
    raw_rows: list[list[dict[str, Any]]],
    *,
    width: int,
) -> list[dict[str, Any]]:
    """Return raw rows that span the whole table and should be contextual headings."""
    if width <= 1:
        return []
    heading_rows: list[dict[str, Any]] = []
    for row_index, raw_row in enumerate(raw_rows):
        non_empty_cells = [
            cell
            for cell in raw_row
            if str(cell.get("text", "")).strip()
        ]
        if len(non_empty_cells) != 1:
            continue
        cell = non_empty_cells[0]
        colspan = _positive_cell_span(cell.get("colspan", 1), default=1)
        if colspan < width:
            continue
        heading_rows.append(
            {
                "row": row_index,
                "text": str(cell.get("text", "")).strip(),
                "colspan": colspan,
            }
        )
    return heading_rows


def _drop_grid_rows(
    grid: list[list[str]],
    header_grid: list[list[bool]],
    row_indexes: set[int],
) -> tuple[list[list[str]], list[list[bool]]]:
    """Return a table grid without contextual raw rows."""
    if not row_indexes:
        return grid, header_grid
    filtered_grid: list[list[str]] = []
    filtered_header_grid: list[list[bool]] = []
    for row_index, (row, header_row) in enumerate(zip(grid, header_grid)):
        if row_index in row_indexes:
            continue
        filtered_grid.append(row)
        filtered_header_grid.append(header_row)
    return filtered_grid, filtered_header_grid


def _table_structure_stats(
    raw_rows: list[list[dict[str, Any]]],
    grid: list[list[str]],
    header_row_count: int,
    frame: dict[str, Any],
) -> dict[str, Any]:
    """Return cheap audit stats about the original and expanded table shape."""
    raw_row_cell_counts = [len(row) for row in raw_rows]
    span_cells: list[dict[str, int]] = []
    empty_cells: list[dict[str, int]] = []
    raw_cell_count = 0
    total_cell_coverage_count = 0
    image_raw_cell_count = 0
    image_covered_cell_count = 0
    for row_index, row in enumerate(raw_rows):
        for column_index, cell in enumerate(row):
            raw_cell_count += 1
            rowspan = _positive_cell_span(cell.get("rowspan", 1), default=1)
            colspan = _positive_cell_span(cell.get("colspan", 1), default=1)
            coverage = max(1, rowspan * colspan)
            total_cell_coverage_count += coverage
            if int(cell.get("image_count", 0) or 0) > 0:
                image_raw_cell_count += 1
                image_covered_cell_count += coverage
            if rowspan > 1 or colspan > 1:
                span_cells.append(
                    {
                        "row": row_index,
                        "column": column_index,
                        "rowspan": rowspan,
                        "colspan": colspan,
                    }
                )
            if not str(cell.get("text", "")).strip():
                empty_cells.append({"row": row_index, "column": column_index})
    return {
        "parser": "expanded_markdown_table",
        "legacy_row_dict_parser_enabled": False,
        "row_count": len(grid),
        "expanded_width": len(grid[0]) if grid else 0,
        "raw_row_cell_counts": raw_row_cell_counts,
        "header_row_count": header_row_count,
        "empty_cell_count": len(empty_cells),
        "empty_cells": empty_cells[:20],
        "span_cell_count": len(span_cells),
        "span_cells": span_cells[:20],
        "nested_table_count": int(frame.get("nested_table_count", 0) or 0),
        "raw_cell_count": raw_cell_count,
        "total_cell_coverage_count": total_cell_coverage_count,
        "image_raw_cell_count": image_raw_cell_count,
        "image_covered_cell_count": image_covered_cell_count,
        "image_cell_rate": round(
            image_covered_cell_count / total_cell_coverage_count,
            4,
        )
        if total_cell_coverage_count
        else 0.0,
    }


def _build_wikipedia_table(table_index: int, frame: dict[str, Any]) -> WikipediaTable:
    """Convert one parser frame into a table model."""
    raw_rows = frame.get("rows", [])
    grid, header_grid = _expand_table_grid(raw_rows)
    table_type = str(frame.get("table_type", "")).strip()
    full_width_heading_rows = _full_width_heading_rows(raw_rows, width=len(grid[0]) if grid else 0)
    header_rows = _header_row_count(grid, header_grid)
    headers = _combined_markdown_headers(grid, header_rows)
    data_rows = grid[header_rows:] if header_rows else grid
    markdown = _grid_to_markdown(headers, data_rows)
    rows = [headers, *data_rows] if headers else data_rows
    structure = _table_structure_stats(raw_rows, grid, header_rows, frame)
    if full_width_heading_rows:
        structure["full_width_heading_row_count"] = len(full_width_heading_rows)
        structure["full_width_heading_rows"] = full_width_heading_rows[:20]
    normalized_parts = [
        str(frame.get("section_heading", "")).strip(),
        str(frame.get("caption", "")).strip(),
        markdown,
    ]
    return WikipediaTable(
        table_index=table_index,
        table_type=table_type,
        section_heading=str(frame.get("section_heading", "")).strip(),
        caption=str(frame.get("caption", "")).strip(),
        nearby_intro=str(frame.get("nearby_intro", "")).strip(),
        headers=headers,
        rows=rows,
        row_dicts=[],
        normalized_text="\n".join(part for part in normalized_parts if part),
        markdown=markdown,
        structure=structure,
    )


def _source_metadata(
    *,
    page: WikipediaPageTables,
    tables: list[WikipediaTable],
    llm_response: dict[str, Any],
    llm_prompt: str,
    source_table: WikipediaTable | None,
    table_selection: list[dict[str, Any]],
    timings: dict[str, float],
    answer_items: list[str] | None = None,
    answer_type: str = "",
    reasoning_type: str = "",
    tie_completion_warning: str = "",
    subject_anchors: dict[str, Any] | None = None,
    min_table_score: float = 0.0,
    allowed_reasoning_types: Iterable[str] | None = None,
    allowed_answer_types: Iterable[str] | None = None,
    extra_prompts: Iterable[str] | str | None = None,
    table_filter_modes: Iterable[str] | str | None = None,
    llm_choose_table: bool = False,
) -> dict[str, Any]:
    """Build Route 3 audit metadata."""
    safe_subject_aliases = _first_paragraph_aliases(page.title, page.first_paragraph)
    normalized_allowed_reasoning_types = normalize_route3_reasoning_types(allowed_reasoning_types)
    normalized_allowed_answer_types = normalize_route3_answer_types(allowed_answer_types)
    normalized_extra_prompts = normalize_route3_extra_prompts(extra_prompts)
    normalized_table_filter_modes = normalize_route3_table_filter_modes(table_filter_modes)
    metadata = {
        "source_url": page.source_url,
        "page_id": normalize_wikipedia_page_id(page.source_url),
        "canonical_url": page.canonical_url,
        "page_title": page.title,
        "content_domain": page.content_domain,
        "first_paragraph": page.first_paragraph,
        "subject_anchor_aliases": _subject_anchor_options(page.title, page.first_paragraph, 2025),
        "safe_subject_aliases": safe_subject_aliases,
        "subject_anchors": subject_anchors or [],
        "min_table_score": float(min_table_score),
        "allowed_reasoning_types": list(normalized_allowed_reasoning_types),
        "allowed_answer_types": list(normalized_allowed_answer_types),
        "extra_prompts": list(normalized_extra_prompts),
        "table_filter_modes": list(normalized_table_filter_modes),
        "llm_choose_table": bool(llm_choose_table),
        "parsed_tables": [table.to_metadata() for table in tables],
        "table_selection": [_selection_payload(row) for row in table_selection],
        "selected_source_table": source_table.to_metadata() if source_table is not None else {},
        "llm_prompt": llm_prompt,
        "llm_response": llm_response,
        "small_model_qa_response": llm_response,
        "answer_items": answer_items or [],
        "answer_is_list": bool(answer_items),
        "answer_type": answer_type,
        "route_guard_warnings": {
            "wikipedia_infobox_incomplete_tie_answer": tie_completion_warning,
        } if tie_completion_warning else {},
        "reasoning_type": reasoning_type or _reasoning_type(llm_response),
        "legacy_composition_type": str(llm_response.get("composition_type", "")).strip(),
        "derivation_summary": str(llm_response.get("derivation_summary", "")).strip(),
        "phase_timings_seconds": dict(timings),
        "route_validation_policy": "no_route_local_factual_validation; provenance_and_parsed_tables_stored_for_review",
    }
    if page.first_paragraph_fetch_error:
        metadata["first_paragraph_fetch_error"] = page.first_paragraph_fetch_error
    return metadata


def _rejected_placeholder(
    *,
    url: str,
    reason: str,
    run_date: str,
    timings: dict[str, float],
    title: str = "",
    canonical_url: str = "",
    content_domain: str = "",
    first_paragraph: str = "",
    error_message: str = "",
    discard_reason: str = "",
    tables: list[WikipediaTable] | None = None,
    llm_response: dict[str, Any] | None = None,
    llm_prompt: str = "",
    table_selection: list[dict[str, Any]] | None = None,
    source_table: WikipediaTable | None = None,
    question: str = "",
    answer: str = "",
    min_table_score: float = 0.0,
    allowed_reasoning_types: Iterable[str] | None = None,
    allowed_answer_types: Iterable[str] | None = None,
    extra_prompts: Iterable[str] | str | None = None,
    table_filter_modes: Iterable[str] | str | None = None,
) -> GeneratedCandidate:
    """Build a placeholder candidate so shared output records route-local failures."""
    normalized_allowed_reasoning_types = normalize_route3_reasoning_types(allowed_reasoning_types)
    normalized_allowed_answer_types = normalize_route3_answer_types(allowed_answer_types)
    normalized_extra_prompts = normalize_route3_extra_prompts(extra_prompts)
    normalized_table_filter_modes = normalize_route3_table_filter_modes(table_filter_modes)
    placeholder_reasoning_type = (
        normalized_allowed_reasoning_types[0] if len(normalized_allowed_reasoning_types) == 1 else "wikipedia_table_fact"
    )
    return GeneratedCandidate(
        source_type=SOURCE_TYPE,
        generation_route=ROUTE_NAME,
        question=question or title or url,
        canonical_question=question or title or url,
        answer=answer,
        answer_aliases=[],
        subject_entity=EntityReference(
            name=title or normalize_wikipedia_title(url),
            wikipedia_title=(title or normalize_wikipedia_title(url)).replace(" ", "_"),
            url=canonical_url or url,
        ),
        answer_entity=EntityReference(name=answer),
        relation_or_claim=placeholder_reasoning_type,
        evidence=EvidenceRecord(
            text=first_paragraph,
            url=canonical_url or url,
            source_title=title,
            retrieved_at=run_date,
        ),
        topic="Wikipedia semi-structured data",
        notes=[reason],
        source_metadata={
            "source_url": url,
            "page_id": normalize_wikipedia_page_id(url),
            "canonical_url": canonical_url or url,
            "page_title": title,
            "content_domain": content_domain,
            "first_paragraph": first_paragraph,
            "min_table_score": float(min_table_score),
            "allowed_reasoning_types": list(normalized_allowed_reasoning_types),
            "allowed_answer_types": list(normalized_allowed_answer_types),
            "reasoning_type": placeholder_reasoning_type if placeholder_reasoning_type != "wikipedia_table_fact" else "",
            "extra_prompts": list(normalized_extra_prompts),
            "table_filter_modes": list(normalized_table_filter_modes),
            "parsed_tables": [table.to_metadata() for table in tables or []],
            "table_selection": [_selection_payload(row) for row in table_selection or []],
            "selected_source_table": source_table.to_metadata() if source_table is not None else {},
            "llm_prompt": llm_prompt,
            "llm_response": llm_response or {},
            "small_model_qa_response": llm_response or {},
            "discard_reason": discard_reason,
            "error_message": error_message,
            "phase_timings_seconds": dict(timings),
        },
    )


def _table_type(class_text: str) -> str:
    """Return the supported table type for a class attribute."""
    classes = {part.strip().lower() for part in class_text.split()}
    if "infobox" in classes:
        return "infobox"
    if "wikitable" in classes:
        return "wikitable"
    return ""


def _table_by_index(tables: list[WikipediaTable], table_index: int | None) -> WikipediaTable | None:
    """Return one table by one-based index."""
    if table_index is None:
        return tables[0] if tables else None
    for table in tables:
        if table.table_index == table_index:
            return table
    return tables[0] if tables else None


def _live_table_scope_rejection_reason(table: WikipediaTable | None) -> str:
    """Return a rejection reason for live/current table scopes."""
    if table is None:
        return ""
    context_parts = {
        "section_heading": table.section_heading,
        "caption": table.caption,
        "nearby_intro": table.nearby_intro,
    }
    for field_name, text in context_parts.items():
        normalized = str(text or "").lower()
        for term in LIVE_TABLE_SCOPE_TERMS:
            if re.search(rf"\b{re.escape(term)}\b", normalized):
                return f"live_table_scope:{field_name}:{term}"
    return ""


def _selection_payload(row: dict[str, Any]) -> dict[str, Any]:
    """Return serializable table-selection metadata."""
    return {
        "table_index": row.get("table_index"),
        "table_type": row.get("table_type"),
        "caption": row.get("caption"),
        "section_heading": row.get("section_heading"),
        "nearby_intro": row.get("nearby_intro", ""),
        "score": row.get("score"),
        "reasons": row.get("reasons", []),
        "row_count": row.get("row_count"),
        "numeric_cell_count": row.get("numeric_cell_count"),
        "comparable_header_hits": row.get("comparable_header_hits", []),
        "preferred_context_hits": row.get("preferred_context_hits", []),
        "mutable_context_hits": row.get("mutable_context_hits", []),
        "live_scope_rejection_reason": row.get("live_scope_rejection_reason", ""),
        "table_filter_modes": row.get("table_filter_modes", []),
        "table_filter_rejection_reason": row.get("table_filter_rejection_reason", ""),
        "table_filter_rejection_reasons": row.get("table_filter_rejection_reasons", []),
        "picture_heavy_table_stats": row.get("picture_heavy_table_stats", {}),
        "incomplete_table_markers": row.get("incomplete_table_markers", []),
        "number_dominance_stats": row.get("number_dominance_stats", {}),
        "social_science_markers": row.get("social_science_markers", []),
        "min_table_score": row.get("min_table_score"),
        "below_min_table_score": bool(row.get("below_min_table_score", False)),
        "zero_numeric_rate": row.get("zero_numeric_rate"),
        "prose_leakage": row.get("prose_leakage", {}),
    }


def _coerce_table_index(value: Any) -> int | None:
    """Coerce a model-provided table index."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _string_list(value: Any) -> list[str]:
    """Return a clean string list from model JSON."""
    if not isinstance(value, list):
        return []
    cleaned: list[str] = []
    seen: set[str] = set()
    for item in value:
        text = str(item).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        cleaned.append(text)
    return cleaned


def _sanitize_answer_blind_queries(
    value: Any,
    *,
    answer: str,
    answer_aliases: list[str],
    answer_items: list[str] | None = None,
    max_queries: int | None = None,
) -> list[str]:
    """Return model queries after dropping answer-containing strings."""
    blocked = {
        normalize_name(answer),
        *{normalize_name(item) for item in answer_items or [] if normalize_name(item)},
        *{normalize_name(alias) for alias in answer_aliases if normalize_name(alias)},
    }
    queries = [
        query
        for query in _string_list(value)
        if not any(blocked_value and blocked_value in normalize_name(query) for blocked_value in blocked)
    ]
    if max_queries is None:
        return queries
    return queries[: max(0, max_queries)]


def _raw_reasoning_type(response: dict[str, Any]) -> str:
    """Return the raw Route 3 reasoning type, accepting legacy composition_type."""
    raw_value = response.get("reasoning_type")
    if raw_value in {None, ""}:
        raw_value = response.get("composition_type")
    return str(raw_value or "").strip()


def _normalize_reasoning_type_value(value: Any) -> str:
    """Normalize one Route 3 reasoning type string."""
    normalized = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    if normalized == "simple_fact":
        normalized = "single_fact"
    return normalized


def _normalize_answer_type_value(value: Any) -> str:
    """Normalize one Route 3 answer type string."""
    normalized = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "person": "Person",
        "people": "Person",
        "human": "Person",
        "place": "Place",
        "location": "Place",
        "geographic_entity": "Place",
        "number": "Number",
        "numeric": "Number",
        "date": "Date",
        "time": "Date",
        "year": "Date",
        "other": "Other",
        "entity": "Other",
        "organization": "Other",
        "organisation": "Other",
        "work": "Other",
        "value": "Other",
    }
    return aliases.get(normalized, str(value or "").strip())


def _normalize_extra_prompt(value: Any) -> str:
    """Normalize one named or literal extra prompt rule."""
    raw_value = str(value or "").strip()
    if not raw_value:
        return ""
    key = raw_value.lower().replace("-", "_").replace(" ", "_")
    return ROUTE3_EXTRA_PROMPTS.get(key, raw_value)


def _normalize_table_filter_mode(value: Any) -> str:
    """Normalize one Route 3 table prefilter mode."""
    normalized = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "incomplete_tables": "no_incomplete_tables",
        "no_incomplete": "no_incomplete_tables",
        "incomplete": "no_incomplete_tables",
        "big_numbers": "not_number_dominant",
        "no_big_number": "not_number_dominant",
        "no_big_numbers": "not_number_dominant",
        "number_dominant": "not_number_dominant",
        "social_science": "no_social_science_research",
        "no_social_science": "no_social_science_research",
        "no_social_science_research_prompt": "no_social_science_research",
        "picture_heavy": "no_picture_heavy_tables",
        "pictures": "no_picture_heavy_tables",
        "images": "no_picture_heavy_tables",
        "no_pictures": "no_picture_heavy_tables",
        "no_images": "no_picture_heavy_tables",
        "no_picture_heavy": "no_picture_heavy_tables",
        "no_image_heavy_tables": "no_picture_heavy_tables",
        "approx": "no_incomplete_tables",
        "approximate": "no_incomplete_tables",
        "approximately": "no_incomplete_tables",
        "precision_gate": "no_incomplete_tables",
        "no_approx": "no_incomplete_tables",
        "no_approximate": "no_incomplete_tables",
        "no_approximately": "no_incomplete_tables",
    }
    return aliases.get(normalized, normalized)


def _declared_reasoning_type(response: dict[str, Any]) -> str:
    """Return the model-declared Route 3 reasoning type when it is supported."""
    normalized = _normalize_reasoning_type_value(_raw_reasoning_type(response))
    return normalized if normalized in ROUTE3_REASONING_TYPE_SET else ""


def _declared_answer_type(response: dict[str, Any], answer: str, question: str) -> str:
    """Return the model-declared answer type when supported, with conservative fallback inference."""
    normalized = _normalize_answer_type(response.get("answer_type"), answer, question)
    return normalized if normalized in ROUTE3_ANSWER_TYPE_SET else "Other"


def _reasoning_type(response: dict[str, Any]) -> str:
    """Return the normalized Route 3 reasoning type, accepting legacy composition_type."""
    return _declared_reasoning_type(response) or "single_fact"


def _reasoning_type_not_allowed_reason(response: dict[str, Any], allowed_reasoning_types: tuple[str, ...]) -> str:
    """Return an audit string for a configured reasoning-type rejection."""
    raw_reasoning_type = _raw_reasoning_type(response)
    declared_reasoning_type = _declared_reasoning_type(response)
    rejected_value = declared_reasoning_type or raw_reasoning_type or "<missing>"
    return (
        "reasoning_type_not_allowed:"
        f"{rejected_value}; allowed={','.join(allowed_reasoning_types)}"
    )


def _answer_type_not_allowed_reason(response: dict[str, Any], allowed_answer_types: tuple[str, ...]) -> str:
    """Return an audit string for a configured answer-type rejection."""
    raw_answer_type = str(response.get("answer_type") or "").strip()
    rejected_value = _normalize_answer_type_value(raw_answer_type) or raw_answer_type or "<missing>"
    return (
        "answer_type_not_allowed:"
        f"{rejected_value}; allowed={','.join(allowed_answer_types)}"
    )


def _extra_prompt_violation(
    *,
    extra_prompts: tuple[str, ...],
    question: str,
    answer: str,
    page: WikipediaPageTables,
    source_table: WikipediaTable | None,
) -> str:
    """Return a deterministic rejection reason for known stricter extra prompt rules."""
    if NO_SOCIAL_SCIENCE_RESEARCH_PROMPT not in extra_prompts:
        return ""
    checked_text = normalize_name(question)
    blocked_markers = (
        "census",
        "survey",
        "demographic",
        "self reported",
        "ancestry group",
        "ethinic group",
        "ethinicity",
        "population",
        "language speaker",
    )
    for marker in blocked_markers:
        if marker in checked_text:
            return f"no_social_science_research_prompt:{marker}"
    return ""


def _tie_completion_problem(
    *,
    source_table: WikipediaTable | None,
    reasoning_type: str,
    answer: str,
    answer_items: list[str],
) -> str:
    """Return a rejection note when a simple grouped max/min table has an incomplete tie answer."""
    if source_table is None or reasoning_type not in {"max", "min"}:
        return ""
    expected_items = _simple_grouped_extreme_items(source_table, reasoning_type)
    if len(expected_items) <= 1:
        return ""
    provided_items = answer_items or [answer]
    provided = {normalize_name(item) for item in provided_items if normalize_name(item)}
    expected = {normalize_name(item) for item in expected_items if normalize_name(item)}
    if expected and not expected.issubset(provided):
        missing = [item for item in expected_items if normalize_name(item) not in provided]
        return "incomplete_tie_answer; missing tied answers: " + "; ".join(missing)
    return ""


def _simple_grouped_extreme_items(table: WikipediaTable, reasoning_type: str) -> list[str]:
    """Infer tied max/min answer items from simple two-column grouped numeric tables."""
    if len(table.headers) < 2:
        return []
    groups: dict[float, list[str]] = {}
    current_value: float | None = None
    saw_continuation = False
    for row in _data_rows(table):
        if not row:
            continue
        metric = parse_number_token(row[0])
        if metric is not None and len(row) >= 2:
            current_value = float(metric)
            item = _strip_footnote_markers(row[1])
            if item:
                groups.setdefault(current_value, []).append(item)
            continue
        non_empty_cells = [cell for cell in row if str(cell).strip()]
        if current_value is not None and len(non_empty_cells) == 1:
            item = _strip_footnote_markers(non_empty_cells[0])
            if item:
                groups.setdefault(current_value, []).append(item)
                saw_continuation = True
    if not saw_continuation or not groups:
        return []
    target_value = max(groups) if reasoning_type == "max" else min(groups)
    return groups.get(target_value, [])


def _normalize_answer_type(value: Any, answer: str, question: str) -> str:
    """Return a supported answer type with conservative fallback inference."""
    normalized = _normalize_answer_type_value(value)
    normalized_question = normalize_name(question)
    normalized_date = normalize_date_answer(answer, "Date")
    looks_like_temporal_answer = normalized_date != answer.strip() or re.fullmatch(
        r"\d{4}(?:\s*\W+\s*\d{2,4})?",
        answer.strip(),
    ) is not None
    if looks_like_temporal_answer and any(
        token in normalized_question
        for token in ("year", "date", "day", "month", "when")
    ):
        return "Date"
    if normalized in ROUTE3_ANSWER_TYPE_SET:
        return normalized
    if parse_number_token(answer) is not None:
        return "Number"
    return "Other"


def _normalize_generated_answer(answer: Any, aliases: list[str]) -> tuple[str, list[str]]:
    """Split table-cell aliases out of a generated canonical answer."""
    answer_items = _answer_items(answer)
    if answer_items:
        cleaned_items: list[str] = []
        item_aliases: list[str] = []
        for item in answer_items:
            split_answer = _split_answer_alias_cell(item)
            if split_answer is not None:
                canonical, extracted_aliases = split_answer
                cleaned_items.append(canonical)
                item_aliases.extend(extracted_aliases)
                item_aliases.append(item.strip())
            else:
                cleaned_items.append(_strip_footnote_markers(item))
        canonical_answer = "; ".join(item for item in cleaned_items if item)
        return canonical_answer, _dedupe_aliases(canonical_answer, [*item_aliases, *aliases])
    candidates = [answer, *aliases]
    canonical = str(answer).strip()
    extra_aliases: list[str] = []
    split_answer = _split_answer_alias_cell(str(answer))
    if split_answer is not None:
        canonical, extracted_aliases = split_answer
        extra_aliases.extend(extracted_aliases)
        extra_aliases.append(answer.strip())
    return canonical, _dedupe_aliases(canonical, [*extra_aliases, *candidates[1:]])


def _dedupe_aliases(canonical: str, values: list[str]) -> list[str]:
    """Return aliases deduplicated against a canonical answer."""
    cleaned_aliases: list[str] = []
    seen = {normalize_name(canonical)}
    for value in values:
        alias = _strip_footnote_markers(value)
        normalized = normalize_name(alias)
        if _is_rank_like_alias(alias):
            continue
        if not alias or not normalized or normalized in seen:
            continue
        seen.add(normalized)
        cleaned_aliases.append(alias)
    return cleaned_aliases


def _is_rank_like_alias(alias: str) -> bool:
    """Return whether an alias is just a table rank marker."""
    stripped = alias.strip()
    return bool(re.fullmatch(r"#?\d+(?:st|nd|rd|th)?", stripped, flags=re.IGNORECASE))


def _answer_items(answer: Any) -> list[str]:
    """Return model-provided answer list items, if this is a list answer."""
    if not isinstance(answer, list):
        return []
    return [str(item).strip() for item in answer if str(item).strip()]


def _answer_display_text(answer: Any) -> str:
    """Return a stable display string for string or list answers."""
    items = _answer_items(answer)
    if items:
        return "; ".join(items)
    return str(answer).strip()


def _split_answer_alias_cell(answer: str) -> tuple[str, list[str]] | None:
    """Split a Wikipedia table answer cell into canonical label and aliases."""
    cleaned = _strip_footnote_markers(answer)
    if "(" in cleaned and ")" in cleaned:
        before, after = cleaned.split("(", 1)
        alias = after.split(")", 1)[0].strip()
        canonical = re.sub(r"[\s?‡†�鈥]+$", "", before.strip()).strip(" -–—")
        if canonical and alias:
            return canonical, [alias]
    return None


def _strip_footnote_markers(value: str) -> str:
    """Remove common Wikipedia footnote symbols from a cell value."""
    cleaned = value.replace("‡", " ").replace("†", " ").replace("鈥?", " ")
    cleaned = re.sub(r"\[\s*\d+\s*\]", " ", cleaned)
    return _clean_text(cleaned)


def _data_rows(table: WikipediaTable) -> list[list[str]]:
    """Return rows excluding a header row when present."""
    if table.headers and table.rows:
        return table.rows[1:]
    return table.rows


def _prose_leakage_counts(table: WikipediaTable, normalized_prose: str) -> tuple[int, int]:
    """Count table row values that are visible in non-table article prose."""
    checked = 0
    leaked = 0
    for row in _data_rows(table):
        for cell in row:
            normalized = normalize_name(cell)
            if not _is_checkable_cell(normalized):
                continue
            checked += 1
            if normalized in normalized_prose:
                leaked += 1
    return leaked, checked


def _is_checkable_cell(normalized_cell: str) -> bool:
    """Return whether a cell value is useful for prose-leakage scoring."""
    if len(normalized_cell) < 4:
        return False
    if normalized_cell.isdigit():
        return False
    if len(normalized_cell.split()) > 12:
        return False
    return True


def _is_numeric_value_cell(cell: str) -> bool:
    """Return whether a table cell is primarily a comparable numeric value."""
    stripped = cell.strip()
    if not NUMBER_PATTERN.search(stripped):
        return False
    without_refs = re.sub(r"\[\s*\d+\s*\]", "", stripped)
    compact = re.sub(r"[$€£¥,%\s,.\-–—()/]", "", without_refs)
    if not compact:
        return True
    letters = sum(1 for char in compact if char.isalpha())
    digits = sum(1 for char in compact if char.isdigit())
    return digits > 0 and letters <= 2 and digits >= letters


def _is_zero_numeric_value_cell(cell: str) -> bool:
    """Return whether a numeric value cell is exactly zero-like."""
    if not _is_numeric_value_cell(cell):
        return False
    numbers = NUMBER_PATTERN.findall(cell.replace(",", ""))
    return bool(numbers) and all(float(number) == 0.0 for number in numbers)


def _first_paragraph_aliases(title: str, first_paragraph: str) -> list[str]:
    """Extract conservative subject aliases from the first paragraph."""
    aliases: list[str] = []
    for marker in (" is the ", " was the "):
        if marker not in first_paragraph:
            continue
        remainder = first_paragraph.split(marker, 1)[1]
        alias = remainder.split(",", 1)[0].split(".", 1)[0].strip()
        if alias and title not in alias:
            aliases.append(alias)
    for match in ORDINAL_EVENT_PATTERN.finditer(first_paragraph):
        alias = match.group(0).strip()
        if alias and alias not in aliases:
            aliases.append(alias)
    return aliases


def _subject_anchor_options(title: str, first_paragraph: str, cutoff_year: int) -> list[str]:
    """Return title and first-paragraph aliases that are safe subject anchors."""
    aliases = _first_paragraph_aliases(title, first_paragraph)
    aliases.extend(_title_subject_aliases(title))
    options: list[str] = []
    if not _text_has_cutoff_year(title, cutoff_year):
        options.append(title)
    options.extend(aliases)
    seen: set[str] = set()
    deduped: list[str] = []
    for option in options:
        cleaned = option.strip()
        key = normalize_name(cleaned)
        if not cleaned or not key or key in seen:
            continue
        seen.add(key)
        deduped.append(cleaned)
    return deduped


def _subject_anchor_context(
    title: str,
    first_paragraph: str,
    tables: list[WikipediaTable],
    cutoff_year: int,
) -> dict[str, Any]:
    """Return page and table scope hints for prompt grounding."""
    first_paragraph_aliases = _first_paragraph_aliases(title, first_paragraph)
    title_aliases = _title_subject_aliases(title)
    safe_page_title = "" if _text_has_cutoff_year(title, cutoff_year) else title
    return {
        "page_title": title,
        "safe_page_title": safe_page_title,
        "safe_subject_aliases": first_paragraph_aliases,
        "title_aliases": title_aliases,
        "table_scopes": [
            {
                "table_index": table.table_index,
                "table_title": table.caption,
                "nearby_section_heading": table.section_heading,
            }
            for table in tables
        ],
        "usage_note": (
            "Use these fields to understand the page and table scope. "
            "They are context hints, not required wording for the question."
        ),
    }


def _title_subject_aliases(title: str) -> list[str]:
    """Return natural aliases for list-style Wikipedia page titles."""
    cleaned = title.strip()
    aliases: list[str] = []
    list_prefix = "List of "
    if cleaned.startswith(list_prefix):
        without_prefix = cleaned[len(list_prefix) :].strip()
        if without_prefix:
            aliases.append(without_prefix)
        top_ten_match = re.match(r"(.+?)\s+top-ten singles in\s+(\d{4})$", without_prefix, flags=re.IGNORECASE)
        if top_ten_match:
            chart_name = top_ten_match.group(1).strip()
            chart_year = top_ten_match.group(2)
            aliases.append(f"{chart_name} in {chart_year}")
            if chart_name.lower() == "uk":
                aliases.append(f"UK Singles Chart in {chart_year}")
                aliases.append(f"UK top-ten singles chart in {chart_year}")
        for plural, singular in (
            ("buildings", "building"),
            ("landmarks", "landmark"),
            ("structures", "structure"),
            ("institutions", "institution"),
            ("singles", "single"),
            ("banks", "bank"),
            ("artworks", "artwork"),
        ):
            if plural in without_prefix:
                aliases.append(without_prefix.replace(plural, singular))
    return aliases


def _text_has_cutoff_year(text: str, cutoff_year: int) -> bool:
    """Return whether text contains a year at or after the cutoff."""
    for match in re.finditer(r"\b(1[5-9]\d{2}|20\d{2}|21\d{2})\b", text):
        try:
            if int(match.group(0)) >= cutoff_year:
                return True
        except ValueError:
            continue
    return False


def _clean_text(text: str) -> str:
    """Normalize table text."""
    return " ".join(unescape(text).replace("\xa0", " ").split())


def _clean_cell_text(text: str) -> str:
    """Normalize table cell text and remove numeric citation markers."""
    return re.sub(r"\s*\[\s*\d+\s*\]", "", _clean_text(text)).strip()


def _elapsed(start: float) -> float:
    """Return rounded elapsed seconds."""
    return round(perf_counter() - start, 4)
