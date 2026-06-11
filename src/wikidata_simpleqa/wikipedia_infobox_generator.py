"""Wikipedia infobox/table route for table-grounded QA generation."""

from __future__ import annotations

import json
import hashlib
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from functools import lru_cache
from html.parser import HTMLParser
from pathlib import Path
from time import perf_counter
from typing import Any, Iterable

from .cheap_model_qa import parse_json_object
from .generation_models import EntityReference, EvidenceRecord, GeneratedCandidate
from .date_reference import normalize_date_answer, normalize_gate_date_answer
from .llm_rewrite import NO_SOCIAL_SCIENCE_RESEARCH_PROMPT
from .number_reference import parse_number_token
from .route3_quality_rules import external_links_table_filter_reason
from .text_normalization import (
    build_text_matcher,
    display_cleanup,
    display_key,
    source_display_cleanup,
    text_contains_match,
)
from .wikipedia_client import (
    WikipediaClient,
    build_parse_api_url,
    build_pageviews_api_url,
    normalize_wikipedia_page_id,
    normalize_wikipedia_title,
)

ROUTE_NAME = "route3_wikipedia_infobox"
SOURCE_TYPE = "wikipedia_tables"
MAX_TABLE_ROWS = 40
MAX_TABLE_MARKDOWN_CHARS = 2500
MIN_TABLE_TOTAL_ROWS = 3
SUBJECT_ANCHOR_ALIAS_CUTOFF_YEAR = 2025
ERA_QUALIFIED_YEAR_PATTERN = re.compile(
    r"^(?:c\.|ca\.|circa)?\s*\d{1,4}\s*(?:B\.?\s*C\.?(?:\s*E\.?)?|A\.?\s*D\.?|C\.?\s*E\.?)$",
    re.IGNORECASE,
)
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
DEFAULT_ROUTE3_REASONING_TYPES = ("single_fact",)
ROUTE3_ANSWER_TYPES = ("Person", "Place", "Number", "Date", "Other")
ROUTE3_ANSWER_TYPE_SET = set(ROUTE3_ANSWER_TYPES)
ROUTE3_ANSWER_TYPE_MODES = ("single", "all5")
DEFAULT_ROUTE3_ANSWER_TYPE_MODE = "single"
ROUTE3_TABLE_SOURCE_TYPES = ("infobox", "wikitable")
ROUTE3_TABLE_SOURCE_TYPE_SET = set(ROUTE3_TABLE_SOURCE_TYPES)
DEFAULT_ROUTE3_TABLE_SOURCE_TYPES = ROUTE3_TABLE_SOURCE_TYPES
DEFAULT_ROUTE3_PAGE_ARCHIVE_DIR = Path("cache") / "route3_pages"
DEFAULT_ROUTE3_PAGEVIEW_PREFILTER_ENABLED = False
DEFAULT_ROUTE3_PAGEVIEW_WINDOW_MONTHS = 12
DEFAULT_ROUTE3_MAX_MONTHLY_AVERAGE_PAGEVIEWS = 5000.0
DEFAULT_ROUTE3_MAX_UNDERFILLED_MONTHLY_PAGEVIEWS = 10000.0
ROUTE3_PAGEVIEW_UNAVAILABLE_POLICIES = ("allow", "reject", "rerun")
DEFAULT_ROUTE3_PAGEVIEW_UNAVAILABLE_POLICY = "allow"
DEFAULT_ROUTE3_INFOBOX_MAX_REMOVED_ROW_RATE = 0.60
DEFAULT_ROUTE3_INFOBOX_MIN_REMAINING_ROWS = 5
INFOBOX_PAGE_START_MAX_CHAR_OFFSET = 15000
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
    "Place": "answer must be a place name, location, or geographic entity on Earth, not a company/award/ceremony/planet/sports club etc.",
    "Number": "answer must be numeric, do not ask `what year`",
    "Date": "answer must be a date, a month, or a year, do not ask `how many years` or ask about a time range",
    "Other": "answer must not be a person, place, number, or date; exclude numeric measurements, percentages, counts, scores, indices, rates, temperatures, durations, ranges, dates, years, people, and places",
}
ROUTE3_EXTRA_PROMPTS = {
    "no_social_science_research_prompt": NO_SOCIAL_SCIENCE_RESEARCH_PROMPT,
}
ROUTE3_TABLE_FILTER_MODES = (
    "no_external_links_tables",
    "no_horizontal_companion_tables",
    "no_picture_heavy_tables",
    "no_incomplete_tables",
    "not_number_dominant",
    "no_social_science_research",
)
ROUTE3_TABLE_FILTER_MODE_SET = set(ROUTE3_TABLE_FILTER_MODES)
DEFAULT_ROUTE3_TABLE_FILTER_MODES = ROUTE3_TABLE_FILTER_MODES
INFOBOX_ROW_FILTER_MODES = (
    "no_incomplete_tables",
    "not_number_dominant",
    "no_social_science_research",
)
PICTURE_HEAVY_INFOBOX_MAX_NON_TITLE_IMAGE_CELL_RATE = 0.5
INFOBOX_MEDIA_CAPTION_CLASS_MARKERS = {
    "caption",
    "infobox-caption",
    "image-caption",
    "mapframe-caption",
    "thumbcaption",
}
INFOBOX_MEDIA_TITLE_CLASS_MARKERS = {
    "infobox-header",
    "infobox-label",
}
INFOBOX_MEDIA_TITLE_TEXTS = {
    "image",
    "photo",
    "photograph",
    "logo",
    "map",
    "location map",
    "signature",
}
DEFAULT_ROUTE3_PROSE_LEAKAGE_SCORING_ENABLED = True
PROSE_LEAKAGE_LOW_RATE_THRESHOLD = 0.2
PROSE_LEAKAGE_HIGH_RATE_THRESHOLD = 0.8
PROSE_LEAKAGE_LOW_SCORE_BONUS = 0.5
PROSE_LEAKAGE_HIGH_SCORE_PENALTY = 0.5
HORIZONTAL_COMPANION_TABLE_MAX_WIDTH = 3
HORIZONTAL_COMPANION_TABLE_MAX_ROWS = 8
ANSWER_TYPE_PERSON_TABLE_SCORE_BONUS = 1.0
ANSWER_TYPE_PLACE_TABLE_SCORE_BONUS = 2.0
ANSWER_TYPE_DATE_TABLE_SCORE_BONUS = 2.0
COMMON_WORD_LEXICON_PATH = Path("cache") / "rule_based_qa_gate" / "common_words_100k.txt"
COMMON_WORD_FALLBACKS = {
    "a",
    "and",
    "by",
    "for",
    "from",
    "in",
    "of",
    "on",
    "the",
    "to",
    "with",
}
NUMBER_DOMINANCE_WORD_MARKERS = ("thousand", "million", "billion", "trillion")
NUMBER_DOMINANCE_LOW_NUMERIC_THRESHOLD = 1000
NUMBER_DOMINANCE_YEAR_LIKE_MIN = 1500
NUMBER_DOMINANCE_YEAR_LIKE_MAX = 2040
NUMBER_DOMINANCE_MIN_ALPHA_RATE = 0.5
ANSWER_TYPE_DATE_YEAR_MIN = 1500
ANSWER_TYPE_DATE_YEAR_MAX = 2040
ANSWER_TYPE_MONTH_MARKERS = (
    "january",
    "jan",
    "february",
    "feb",
    "march",
    "mar",
    "april",
    "apr",
    "may",
    "june",
    "jun",
    "july",
    "jul",
    "august",
    "aug",
    "september",
    "sept",
    "sep",
    "october",
    "oct",
    "november",
    "nov",
    "december",
    "dec",
)
ANSWER_TYPE_DATE_NUMERIC_MDY_PATTERN = re.compile(
    r"(?<!\d)(?P<month>\d{1,2})[-/](?P<day>\d{1,2})[-/](?P<year>\d{4})(?!\d)"
)
ANSWER_TYPE_DATE_YEAR_PATTERN = re.compile(r"(?<![\d,])(?P<year>\d{4})(?![\d,])")
ANSWER_TYPE_WORD_PATTERN = re.compile(r"\b[A-Za-z][A-Za-z'.-]*\b")
PLACE_SEED_WHITELIST = {
    "abbey",
    "airport",
    "area",
    "arena",
    "arrondissement",
    "borough",
    "building",
    "campus",
    "capital city",
    "castle",
    "cave",
    "church",
    "city",
    "city and country",
    "city and province",
    "city and state",
    "coast",
    "college",
    "country",
    "county",
    "district",
    "doab",
    "duchy",
    "dukedom",
    "field",
    "fort",
    "garden",
    "geographic area",
    "geographic entity",
    "geographic location",
    "geographic region",
    "geographic section",
    "grammar school",
    "high school",
    "hospital",
    "hotel",
    "island",
    "kibbutz",
    "kingdom",
    "lake",
    "location",
    "middle school",
    "mountain",
    "municipality",
    "observatory",
    "ocean",
    "palace",
    "parochial school",
    "peninsular plateau",
    "place",
    "plateau",
    "prison",
    "province",
    "republic",
    "river",
    "school",
    "state",
    "stadium",
    "street address",
    "studio",
    "theater",
    "theater venue",
    "theatre",
    "town",
    "track",
    "university",
    "venue",
    "village",
    "ward",
    "zoo",
}
INCOMPLETE_TABLE_MARKERS = (
    "unlisted",
    "incomplete",
    "unknown",
    "approx.",
    "approximate",
    "approximately",
    "citation needed",
    "clarification needed",
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

    def to_metadata(self, *, max_rows: int = MAX_TABLE_ROWS, max_text_chars: int = MAX_TABLE_MARKDOWN_CHARS) -> dict[str, Any]:
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
    route3_page_archive: dict[str, Any] = field(default_factory=dict)
    pageview_prefilter: dict[str, Any] = field(default_factory=dict)


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
    allowed_reasoning_types: tuple[str, ...] = DEFAULT_ROUTE3_REASONING_TYPES
    allowed_answer_types: tuple[str, ...] = ()
    extra_prompts: tuple[str, ...] = ()
    table_filter_modes: tuple[str, ...] = DEFAULT_ROUTE3_TABLE_FILTER_MODES
    table_source_types: tuple[str, ...] = DEFAULT_ROUTE3_TABLE_SOURCE_TYPES
    prose_leakage_scoring_enabled: bool = DEFAULT_ROUTE3_PROSE_LEAKAGE_SCORING_ENABLED
    llm_choose_table: bool = False
    answer_type_mode: str = DEFAULT_ROUTE3_ANSWER_TYPE_MODE
    page_archive_dir: Path | None = DEFAULT_ROUTE3_PAGE_ARCHIVE_DIR
    page_archive_paths_by_url: dict[str, Path] | None = None
    read_only_page_archive_paths: tuple[Path, ...] = ()
    pageview_prefilter_enabled: bool = DEFAULT_ROUTE3_PAGEVIEW_PREFILTER_ENABLED
    pageview_window_months: int = DEFAULT_ROUTE3_PAGEVIEW_WINDOW_MONTHS
    max_monthly_average_pageviews: float = DEFAULT_ROUTE3_MAX_MONTHLY_AVERAGE_PAGEVIEWS
    max_underfilled_monthly_pageviews: float = DEFAULT_ROUTE3_MAX_UNDERFILLED_MONTHLY_PAGEVIEWS
    pageview_unavailable_policy: str = DEFAULT_ROUTE3_PAGEVIEW_UNAVAILABLE_POLICY
    infobox_max_removed_row_rate: float = DEFAULT_ROUTE3_INFOBOX_MAX_REMOVED_ROW_RATE
    infobox_min_remaining_rows: int = DEFAULT_ROUTE3_INFOBOX_MIN_REMAINING_ROWS

    def __post_init__(self) -> None:
        """Normalize optional Route 3 prompt restrictions."""
        self.allowed_reasoning_types = normalize_route3_reasoning_types(self.allowed_reasoning_types)
        self.allowed_answer_types = normalize_route3_answer_types(self.allowed_answer_types)
        self.extra_prompts = normalize_route3_extra_prompts(self.extra_prompts)
        self.table_filter_modes = normalize_route3_table_filter_modes(self.table_filter_modes)
        self.table_source_types = normalize_route3_table_source_types(self.table_source_types)
        self.answer_type_mode = normalize_route3_answer_type_mode(self.answer_type_mode)
        self.pageview_window_months = max(1, int(self.pageview_window_months or DEFAULT_ROUTE3_PAGEVIEW_WINDOW_MONTHS))
        self.max_monthly_average_pageviews = float(self.max_monthly_average_pageviews)
        self.max_underfilled_monthly_pageviews = float(self.max_underfilled_monthly_pageviews)
        self.pageview_unavailable_policy = normalize_route3_pageview_unavailable_policy(
            self.pageview_unavailable_policy
        )
        self.infobox_max_removed_row_rate = max(0.0, min(1.0, float(self.infobox_max_removed_row_rate)))
        self.infobox_min_remaining_rows = max(0, int(self.infobox_min_remaining_rows))
        self.read_only_page_archive_paths = tuple(
            Path(path)
            for path in self.read_only_page_archive_paths or ()
            if str(path).strip()
        )
        if (
            self.page_archive_dir == DEFAULT_ROUTE3_PAGE_ARCHIVE_DIR
            and not isinstance(self.wikipedia_client, WikipediaClient)
        ):
            self.page_archive_dir = None

    def generate(self, *, run_date: str, cutoff_year: int) -> list[GeneratedCandidate]:
        """Generate candidates from up to ``record_limit`` Wikipedia URLs."""
        generated: list[GeneratedCandidate] = []
        for url in self.urls[: self.record_limit]:
            candidate_start = perf_counter()
            timings: dict[str, float] = {}
            try:
                page = self._fetch_and_parse_page(url, timings=timings)
                page_candidates = self._candidate_from_page(
                    page,
                    run_date=run_date,
                    cutoff_year=cutoff_year,
                    timings=timings,
                )
            except Exception as exc:  # noqa: BLE001
                timings["total_generation_seconds"] = _elapsed(candidate_start)
                page_candidates = [_rejected_placeholder(
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
                    answer_type_mode=self.answer_type_mode,
                )]
            if isinstance(page_candidates, GeneratedCandidate):
                page_candidates = [page_candidates]
            for candidate in page_candidates:
                candidate.source_metadata["llm_choose_table"] = bool(self.llm_choose_table)
                candidate.source_metadata["table_source_types"] = list(self.table_source_types)
                candidate.source_metadata["prose_leakage_scoring_enabled"] = bool(self.prose_leakage_scoring_enabled)
                candidate.source_metadata["answer_type_mode"] = self.answer_type_mode
                candidate.source_metadata.setdefault("phase_timings_seconds", {}).update(timings)
                candidate.source_metadata["phase_timings_seconds"]["total_generation_seconds"] = _elapsed(candidate_start)
                generated.append(candidate)
        return generated

    def _fetch_and_parse_page(self, url: str, *, timings: dict[str, float]) -> WikipediaPageTables:
        """Fetch one page through MediaWiki APIs and extract table records."""
        archive_path = self._page_archive_path_for_url(url)
        archive_payload, archive_cache_hit = _load_route3_page_archive(archive_path)
        archive_fetch_status = {
            "archive_path": str(archive_path) if archive_path is not None else "",
            "cache_hit": bool(archive_cache_hit),
            "parse_fetch_status": "archive_hit" if archive_cache_hit and archive_payload.get("parse_payload") else "",
        }
        fetch_start = perf_counter()
        parse_payload = archive_payload.get("parse_payload") if isinstance(archive_payload.get("parse_payload"), dict) else {}
        if not parse_payload:
            archived_html = str(archive_payload.get("parsed_html", "") or "").strip()
            if archived_html:
                parse_payload = {
                    "parse": {
                        "title": str(archive_payload.get("title") or normalize_wikipedia_title(url)).strip(),
                        "pageid": archive_payload.get("page_id"),
                        "text": archived_html,
                    }
                }
                archive_fetch_status["parse_fetch_status"] = "archive_parsed_html_hit"
        if not parse_payload:
            parse_payload = self.wikipedia_client.fetch_parse(url)
            archive_fetch_status["parse_fetch_status"] = "fetched"
        timings["page_fetch_seconds"] = _elapsed(fetch_start)
        parse_body = parse_payload.get("parse", {}) if isinstance(parse_payload, dict) else {}
        title = str(parse_body.get("title", normalize_wikipedia_title(url))).strip()
        canonical_url = "https://en.wikipedia.org/wiki/" + title.replace(" ", "_") if title else url
        html = str(parse_body.get("text", "")).strip()

        parse_start = perf_counter()
        tables = extract_wikipedia_tables(html, page_title=title)
        prose_text = extract_non_table_prose(html)
        timings["table_parse_seconds"] = _elapsed(parse_start)
        archive_read_only = self._page_archive_path_is_read_only(archive_path)
        if archive_read_only:
            archive_metadata = _read_only_route3_page_archive_metadata(
                archive_path,
                archive_payload,
                archive_fetch_status=archive_fetch_status,
            )
        else:
            archive_metadata = _update_route3_page_archive(
                archive_path,
                archive_payload,
                source_url=url,
                title=title,
                canonical_url=canonical_url,
                parse_payload=parse_payload,
                html=html,
                prose_text=prose_text,
                tables=tables,
                archive_fetch_status=archive_fetch_status,
            )
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
            route3_page_archive=archive_metadata,
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
        _merge_route3_page_archive(
            page,
            {
                "first_paragraph": page.first_paragraph,
                "first_paragraph_fetch_error": page.first_paragraph_fetch_error,
            },
        )

    def _apply_pageview_prefilter(
        self,
        page: WikipediaPageTables,
        *,
        run_date: str,
        timings: dict[str, float],
    ) -> None:
        """Populate pageview prefilter metadata and update the unified page archive."""
        if page.pageview_prefilter:
            return
        pageview_start = perf_counter()
        page.pageview_prefilter = _route3_pageview_prefilter(
            page=page,
            wikipedia_client=self.wikipedia_client,
            run_date=run_date,
            enabled=self.pageview_prefilter_enabled,
            window_months=self.pageview_window_months,
            max_monthly_average=self.max_monthly_average_pageviews,
            max_underfilled_monthly=self.max_underfilled_monthly_pageviews,
            unavailable_policy=self.pageview_unavailable_policy,
        )
        timings["pageview_prefilter_seconds"] = _elapsed(pageview_start)
        archive_updates = {"pageview_prefilter": page.pageview_prefilter}
        if isinstance(page.pageview_prefilter.get("pageview"), dict):
            archive_updates["pageview"] = page.pageview_prefilter["pageview"]
        _merge_route3_page_archive(page, archive_updates)

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

    def _page_archive_path_for_url(self, url: str) -> Path | None:
        """Return an explicit or hash-derived Route 3 archive path for one URL."""
        if self.page_archive_paths_by_url:
            explicit_path = self.page_archive_paths_by_url.get(url)
            if explicit_path is not None:
                return Path(explicit_path)
        return _route3_page_archive_path(self.page_archive_dir, url)

    def _page_archive_path_is_read_only(self, path: Path | None) -> bool:
        """Return whether this archive path must not be modified."""
        path_key = _route3_archive_path_key(path)
        if not path_key:
            return False
        return any(
            path_key == _route3_archive_path_key(read_only_path)
            for read_only_path in self.read_only_page_archive_paths
        )

    def _candidate_from_page(
        self,
        page: WikipediaPageTables,
        *,
        run_date: str,
        cutoff_year: int,
        timings: dict[str, float],
    ) -> GeneratedCandidate | list[GeneratedCandidate]:
        """Ask the small model for one QA candidate and convert it to the shared shape."""
        self._apply_pageview_prefilter(page, run_date=run_date, timings=timings)
        pageview_decision = str(page.pageview_prefilter.get("decision") or "").strip()
        if pageview_decision in {"reject", "rerun"}:
            return _rejected_placeholder(
                url=page.source_url,
                reason="wikipedia_pageview_prefilter_rejected"
                if pageview_decision == "reject"
                else "wikipedia_pageview_prefilter_unavailable",
                run_date=run_date,
                timings=timings,
                title=page.title,
                canonical_url=page.canonical_url,
                content_domain=page.content_domain,
                first_paragraph=page.first_paragraph,
                discard_reason=str(page.pageview_prefilter.get("reason") or pageview_decision),
                tables=page.tables,
                min_table_score=self.min_table_score,
                allowed_reasoning_types=self.allowed_reasoning_types,
                allowed_answer_types=self.allowed_answer_types,
                extra_prompts=self.extra_prompts,
                table_filter_modes=self.table_filter_modes,
                table_source_types=self.table_source_types,
                page_archive=page.route3_page_archive,
                pageview_prefilter=page.pageview_prefilter,
                answer_type_mode=self.answer_type_mode,
            )
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
                table_source_types=self.table_source_types,
                page_archive=page.route3_page_archive,
                pageview_prefilter=page.pageview_prefilter,
                answer_type_mode=self.answer_type_mode,
            )
        source_tables = _tables_matching_source_types(page.tables, self.table_source_types)
        if not source_tables:
            available_types = sorted(
                {
                    table.table_type
                    for table in page.tables
                    if str(table.table_type).strip()
                }
            )
            return _rejected_placeholder(
                url=page.source_url,
                reason="wikipedia_infobox_no_allowed_table_source_types",
                run_date=run_date,
                timings=timings,
                title=page.title,
                canonical_url=page.canonical_url,
                content_domain=page.content_domain,
                first_paragraph=page.first_paragraph,
                discard_reason=(
                    "no_allowed_table_source_types:"
                    f"allowed={','.join(self.table_source_types)};"
                    f"available={','.join(available_types) if available_types else 'none'}"
                ),
                tables=page.tables,
                min_table_score=self.min_table_score,
                allowed_reasoning_types=self.allowed_reasoning_types,
                allowed_answer_types=self.allowed_answer_types,
                extra_prompts=self.extra_prompts,
                table_filter_modes=self.table_filter_modes,
                table_source_types=self.table_source_types,
                page_archive=page.route3_page_archive,
                pageview_prefilter=page.pageview_prefilter,
                answer_type_mode=self.answer_type_mode,
            )
        table_selection: list[dict[str, Any]] = []
        answer_type_hints_for_ranking = _answer_type_hints_for_table_ranking(
            answer_type_mode=self.answer_type_mode,
            allowed_answer_types=self.allowed_answer_types,
        )
        for source_type in self.table_source_types:
            channel_source_tables = _tables_matching_source_types(source_tables, (source_type,))
            if not channel_source_tables:
                continue
            scoring_tables = _prepare_route3_tables_for_scoring(
                channel_source_tables,
                self.table_filter_modes,
                infobox_max_removed_row_rate=self.infobox_max_removed_row_rate,
                infobox_min_remaining_rows=self.infobox_min_remaining_rows,
            )
            channel_selection = rank_wikipedia_tables(
                scoring_tables,
                first_paragraph=page.first_paragraph,
                prose_text=page.prose_text,
                prose_leakage_scoring_enabled=self.prose_leakage_scoring_enabled,
                answer_type_hints=answer_type_hints_for_ranking,
            )
            channel_selection = _annotate_table_score_cutoff(channel_selection, self.min_table_score)
            channel_selection = _annotate_table_filter_modes(
                channel_selection,
                self.table_filter_modes,
                infobox_max_removed_row_rate=self.infobox_max_removed_row_rate,
                infobox_min_remaining_rows=self.infobox_min_remaining_rows,
            )
            for row in channel_selection:
                row["source_channel"] = source_type
            table_selection.extend(channel_selection)
        table_selection = sorted(
            table_selection,
            key=lambda row: (
                -_selection_score(row),
                0 if str(row.get("table_type", "")) == "infobox" else 1,
                float(row.get("prose_leakage", {}).get("leakage_rate", 0.0)),
                int(row.get("table_index", 0) or 0),
            ),
        )
        safe_table_selection = [
            row
            for row in table_selection
            if not str(row.get("live_scope_rejection_reason", "")).strip()
            and not bool(row.get("below_min_table_score"))
            and not str(row.get("table_filter_rejection_reason", "")).strip()
        ]
        llm_table_limit = 3 if self.llm_choose_table else 1
        selected_table_rows = [
            row
            for row in safe_table_selection
            if isinstance(row.get("table"), WikipediaTable)
        ][:llm_table_limit]
        selected_tables = [_finalize_table_for_llm(row["table"]) for row in selected_table_rows]
        selected_table_selection = []
        for row, table in zip(selected_table_rows, selected_tables):
            copied = dict(row)
            copied["table"] = table
            selected_table_selection.append(copied)
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
                    table_source_types=self.table_source_types,
                    page_archive=page.route3_page_archive,
                    pageview_prefilter=page.pageview_prefilter,
                    answer_type_mode=self.answer_type_mode,
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
                    table_source_types=self.table_source_types,
                    page_archive=page.route3_page_archive,
                    pageview_prefilter=page.pageview_prefilter,
                    answer_type_mode=self.answer_type_mode,
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
                    table_source_types=self.table_source_types,
                    page_archive=page.route3_page_archive,
                    pageview_prefilter=page.pageview_prefilter,
                    answer_type_mode=self.answer_type_mode,
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
                table_source_types=self.table_source_types,
                page_archive=page.route3_page_archive,
                pageview_prefilter=page.pageview_prefilter,
                answer_type_mode=self.answer_type_mode,
            )
        self._extract_first_paragraph_context(page, timings=timings)
        llm_first_paragraph = display_cleanup(page.first_paragraph)
        llm_subject_anchors = _subject_anchor_context(
            page.title,
            llm_first_paragraph,
            selected_tables,
            cutoff_year,
        )
        prompt_builder = (
            build_route3_infobox_prompt
            if selected_tables and selected_tables[0].table_type == "infobox"
            else build_route3_wikitable_prompt
        )
        prompt = prompt_builder(
            title=page.title,
            canonical_url=page.canonical_url,
            first_paragraph=llm_first_paragraph,
            subject_anchors=llm_subject_anchors,
            tables=selected_tables,
            table_selection=selected_table_selection,
            cutoff_year=cutoff_year,
            search_query_count=self.search_query_count,
            allowed_reasoning_types=self.allowed_reasoning_types,
            allowed_answer_types=self.allowed_answer_types,
            extra_prompts=self.extra_prompts,
            llm_choose_table=self.llm_choose_table,
            answer_type_mode=self.answer_type_mode,
        )
        llm_start = perf_counter()
        llm_audit = _complete_text_with_audit(self.llm_client, prompt)
        response = parse_json_object(str(llm_audit.get("text", "")))
        llm_audit["parsed_response"] = response
        timings["llm_question_generation_seconds"] = _elapsed(llm_start)
        if self.answer_type_mode == "all5":
            return self._candidates_from_all5_response(
                response,
                page=page,
                run_date=run_date,
                timings=timings,
                prompt=prompt,
                llm_audit=llm_audit,
                tables=page.tables,
                selected_tables=selected_tables,
                table_selection=table_selection,
                selected_table_selection=selected_table_selection,
                cutoff_year=cutoff_year,
            )
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
                llm_audit=llm_audit,
                table_selection=table_selection,
                min_table_score=self.min_table_score,
                allowed_reasoning_types=self.allowed_reasoning_types,
                allowed_answer_types=self.allowed_answer_types,
                extra_prompts=self.extra_prompts,
                table_filter_modes=self.table_filter_modes,
                table_source_types=self.table_source_types,
                page_archive=page.route3_page_archive,
                pageview_prefilter=page.pageview_prefilter,
                answer_type_mode=self.answer_type_mode,
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
                llm_audit=llm_audit,
                table_selection=table_selection,
                min_table_score=self.min_table_score,
                allowed_reasoning_types=self.allowed_reasoning_types,
                allowed_answer_types=self.allowed_answer_types,
                extra_prompts=self.extra_prompts,
                table_filter_modes=self.table_filter_modes,
                table_source_types=self.table_source_types,
                page_archive=page.route3_page_archive,
                pageview_prefilter=page.pageview_prefilter,
                answer_type_mode=self.answer_type_mode,
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
                llm_audit=llm_audit,
                table_selection=table_selection,
                source_table=source_table,
                question=question,
                answer=answer,
                min_table_score=self.min_table_score,
                allowed_reasoning_types=self.allowed_reasoning_types,
                allowed_answer_types=self.allowed_answer_types,
                extra_prompts=self.extra_prompts,
                table_filter_modes=self.table_filter_modes,
                table_source_types=self.table_source_types,
                page_archive=page.route3_page_archive,
                pageview_prefilter=page.pageview_prefilter,
                answer_type_mode=self.answer_type_mode,
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
                llm_audit=llm_audit,
                table_selection=table_selection,
                source_table=source_table,
                question=question,
                answer=answer,
                min_table_score=self.min_table_score,
                allowed_reasoning_types=self.allowed_reasoning_types,
                allowed_answer_types=self.allowed_answer_types,
                extra_prompts=self.extra_prompts,
                table_filter_modes=self.table_filter_modes,
                table_source_types=self.table_source_types,
                page_archive=page.route3_page_archive,
                pageview_prefilter=page.pageview_prefilter,
                answer_type_mode=self.answer_type_mode,
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
                llm_audit=llm_audit,
                table_selection=table_selection,
                question=question,
                answer=answer,
                min_table_score=self.min_table_score,
                allowed_reasoning_types=self.allowed_reasoning_types,
                allowed_answer_types=self.allowed_answer_types,
                extra_prompts=self.extra_prompts,
                table_filter_modes=self.table_filter_modes,
                table_source_types=self.table_source_types,
                page_archive=page.route3_page_archive,
                pageview_prefilter=page.pageview_prefilter,
                answer_type_mode=self.answer_type_mode,
            )
        search_queries = _sanitize_answer_blind_queries(
            response.get("search_queries", []),
            answer=answer,
            answer_aliases=aliases,
            answer_items=answer_items,
            max_queries=self.search_query_count,
        )
        declared_reasoning_type = _declared_reasoning_type(response)
        if (
            _model_selects_reasoning_type(self.allowed_reasoning_types)
            and self.allowed_reasoning_types
            and declared_reasoning_type not in self.allowed_reasoning_types
        ):
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
                llm_audit=llm_audit,
                table_selection=table_selection,
                source_table=source_table,
                question=question,
                answer=answer,
                min_table_score=self.min_table_score,
                allowed_reasoning_types=self.allowed_reasoning_types,
                allowed_answer_types=self.allowed_answer_types,
                extra_prompts=self.extra_prompts,
                table_filter_modes=self.table_filter_modes,
                table_source_types=self.table_source_types,
                page_archive=page.route3_page_archive,
                pageview_prefilter=page.pageview_prefilter,
                answer_type_mode=self.answer_type_mode,
            )
        reasoning_type = _resolved_reasoning_type(response, self.allowed_reasoning_types)
        tie_problem = _tie_completion_problem(
            source_table=source_table,
            reasoning_type=reasoning_type,
            answer=answer,
            answer_items=answer_items,
        )
        evidence_text = source_table.normalized_text if source_table is not None else llm_first_paragraph
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
                llm_audit=llm_audit,
                source_table=source_table,
                table_selection=table_selection,
                timings=timings,
                answer_items=answer_items,
                answer_type=answer_type,
                reasoning_type=reasoning_type,
                tie_completion_warning=tie_problem,
                subject_anchors=llm_subject_anchors,
                min_table_score=self.min_table_score,
                allowed_reasoning_types=self.allowed_reasoning_types,
                allowed_answer_types=self.allowed_answer_types,
                extra_prompts=self.extra_prompts,
                table_filter_modes=self.table_filter_modes,
                table_source_types=self.table_source_types,
                prose_leakage_scoring_enabled=self.prose_leakage_scoring_enabled,
                llm_choose_table=self.llm_choose_table,
                page_archive=page.route3_page_archive,
                pageview_prefilter=page.pageview_prefilter,
                answer_type_mode=self.answer_type_mode,
            ),
        )

    def _candidates_from_all5_response(
        self,
        response: dict[str, Any],
        *,
        page: WikipediaPageTables,
        run_date: str,
        timings: dict[str, float],
        prompt: str,
        llm_audit: dict[str, Any],
        tables: list[WikipediaTable],
        selected_tables: list[WikipediaTable],
        table_selection: list[dict[str, Any]],
        selected_table_selection: list[dict[str, Any]],
        cutoff_year: int,
    ) -> list[GeneratedCandidate]:
        """Return one accepted/rejected candidate per all5 answer-type slot."""
        outputs = response.get("outputs", [])
        output_rows = outputs if isinstance(outputs, list) else []
        by_answer_type: dict[str, dict[str, Any]] = {}
        for output in output_rows:
            if not isinstance(output, dict):
                continue
            answer_type = _normalize_answer_type_value(output.get("answer_type"))
            if answer_type in ROUTE3_ANSWER_TYPE_SET and answer_type not in by_answer_type:
                by_answer_type[answer_type] = dict(output)
        candidates: list[GeneratedCandidate] = []
        for answer_type in ROUTE3_ANSWER_TYPES:
            slot_response = by_answer_type.get(answer_type, {})
            if not slot_response:
                candidates.append(
                    _rejected_placeholder(
                        url=page.source_url,
                        reason="wikipedia_infobox_llm_discarded",
                        run_date=run_date,
                        timings=timings,
                        title=page.title,
                        canonical_url=page.canonical_url,
                        content_domain=page.content_domain,
                        first_paragraph=page.first_paragraph,
                        discard_reason=f"all5_slot_missing:{answer_type}",
                        tables=tables,
                        llm_response={"answer_type": answer_type, "discard_reason": f"all5_slot_missing:{answer_type}"},
                        llm_prompt=prompt,
                        llm_audit=llm_audit,
                        table_selection=table_selection,
                        min_table_score=self.min_table_score,
                        allowed_reasoning_types=self.allowed_reasoning_types,
                        allowed_answer_types=(answer_type,),
                        extra_prompts=self.extra_prompts,
                        table_filter_modes=self.table_filter_modes,
                        table_source_types=self.table_source_types,
                        page_archive=page.route3_page_archive,
                        pageview_prefilter=page.pageview_prefilter,
                        answer_type_mode=self.answer_type_mode,
                        route3_slot_id=answer_type,
                    )
                )
                continue
            candidates.append(
                self._candidate_from_single_model_response(
                    slot_response,
                    page=page,
                    run_date=run_date,
                    timings=timings,
                    prompt=prompt,
                    llm_audit=llm_audit,
                    tables=tables,
                    selected_tables=selected_tables,
                    table_selection=table_selection,
                    subject_anchors=_subject_anchor_context(
                        page.title,
                        display_cleanup(page.first_paragraph),
                        selected_tables,
                        cutoff_year,
                    ),
                    forced_answer_type=answer_type,
                )
            )
        return candidates

    def _candidate_from_single_model_response(
        self,
        response: dict[str, Any],
        *,
        page: WikipediaPageTables,
        run_date: str,
        timings: dict[str, float],
        prompt: str,
        llm_audit: dict[str, Any],
        tables: list[WikipediaTable],
        selected_tables: list[WikipediaTable],
        table_selection: list[dict[str, Any]],
        subject_anchors: dict[str, Any],
        forced_answer_type: str = "",
    ) -> GeneratedCandidate:
        """Build one candidate or rejected placeholder from one model JSON object."""
        slot_allowed_answer_types = (forced_answer_type,) if forced_answer_type else self.allowed_answer_types
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
                tables=tables,
                llm_response=response,
                llm_prompt=prompt,
                llm_audit=llm_audit,
                table_selection=table_selection,
                min_table_score=self.min_table_score,
                allowed_reasoning_types=self.allowed_reasoning_types,
                allowed_answer_types=slot_allowed_answer_types,
                extra_prompts=self.extra_prompts,
                table_filter_modes=self.table_filter_modes,
                table_source_types=self.table_source_types,
                page_archive=page.route3_page_archive,
                pageview_prefilter=page.pageview_prefilter,
                answer_type_mode=self.answer_type_mode,
                route3_slot_id=forced_answer_type,
            )
        question = str(response.get("question", "")).strip()
        answer_value = response.get("answer", "")
        answer = _answer_display_text(answer_value)
        source_table_index = _coerce_table_index(response.get("source_table"))
        source_table = _table_by_index(selected_tables, source_table_index)
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
                tables=tables,
                llm_response=response,
                llm_prompt=prompt,
                llm_audit=llm_audit,
                table_selection=table_selection,
                min_table_score=self.min_table_score,
                allowed_reasoning_types=self.allowed_reasoning_types,
                allowed_answer_types=slot_allowed_answer_types,
                extra_prompts=self.extra_prompts,
                table_filter_modes=self.table_filter_modes,
                table_source_types=self.table_source_types,
                page_archive=page.route3_page_archive,
                pageview_prefilter=page.pageview_prefilter,
                answer_type_mode=self.answer_type_mode,
                route3_slot_id=forced_answer_type,
            )
        answer, aliases = _normalize_generated_answer(
            answer_value,
            _string_list(response.get("answer_aliases", [])),
        )
        answer_items = _answer_items(answer_value)
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
                tables=tables,
                llm_response=response,
                llm_prompt=prompt,
                llm_audit=llm_audit,
                table_selection=table_selection,
                source_table=source_table,
                question=question,
                answer=answer,
                min_table_score=self.min_table_score,
                allowed_reasoning_types=self.allowed_reasoning_types,
                allowed_answer_types=slot_allowed_answer_types,
                extra_prompts=self.extra_prompts,
                table_filter_modes=self.table_filter_modes,
                table_source_types=self.table_source_types,
                page_archive=page.route3_page_archive,
                pageview_prefilter=page.pageview_prefilter,
                answer_type_mode=self.answer_type_mode,
                route3_slot_id=forced_answer_type,
            )
        answer_type = _normalize_answer_type(response.get("answer_type"), answer, question)
        if slot_allowed_answer_types and answer_type not in slot_allowed_answer_types:
            return _rejected_placeholder(
                url=page.source_url,
                reason="wikipedia_infobox_answer_type_not_allowed",
                run_date=run_date,
                timings=timings,
                title=page.title,
                canonical_url=page.canonical_url,
                content_domain=page.content_domain,
                first_paragraph=page.first_paragraph,
                discard_reason=_answer_type_not_allowed_reason(response, slot_allowed_answer_types),
                tables=tables,
                llm_response=response,
                llm_prompt=prompt,
                llm_audit=llm_audit,
                table_selection=table_selection,
                source_table=source_table,
                question=question,
                answer=answer,
                min_table_score=self.min_table_score,
                allowed_reasoning_types=self.allowed_reasoning_types,
                allowed_answer_types=slot_allowed_answer_types,
                extra_prompts=self.extra_prompts,
                table_filter_modes=self.table_filter_modes,
                table_source_types=self.table_source_types,
                page_archive=page.route3_page_archive,
                pageview_prefilter=page.pageview_prefilter,
                answer_type_mode=self.answer_type_mode,
                route3_slot_id=forced_answer_type,
            )
        declared_reasoning_type = _declared_reasoning_type(response)
        if (
            _model_selects_reasoning_type(self.allowed_reasoning_types)
            and self.allowed_reasoning_types
            and declared_reasoning_type not in self.allowed_reasoning_types
        ):
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
                tables=tables,
                llm_response=response,
                llm_prompt=prompt,
                llm_audit=llm_audit,
                table_selection=table_selection,
                source_table=source_table,
                question=question,
                answer=answer,
                min_table_score=self.min_table_score,
                allowed_reasoning_types=self.allowed_reasoning_types,
                allowed_answer_types=slot_allowed_answer_types,
                extra_prompts=self.extra_prompts,
                table_filter_modes=self.table_filter_modes,
                table_source_types=self.table_source_types,
                page_archive=page.route3_page_archive,
                pageview_prefilter=page.pageview_prefilter,
                answer_type_mode=self.answer_type_mode,
                route3_slot_id=forced_answer_type,
            )
        reasoning_type = _resolved_reasoning_type(response, self.allowed_reasoning_types)
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
                tables=tables,
                llm_response=response,
                llm_prompt=prompt,
                llm_audit=llm_audit,
                table_selection=table_selection,
                source_table=source_table,
                question=question,
                answer=answer,
                min_table_score=self.min_table_score,
                allowed_reasoning_types=self.allowed_reasoning_types,
                allowed_answer_types=slot_allowed_answer_types,
                extra_prompts=self.extra_prompts,
                table_filter_modes=self.table_filter_modes,
                table_source_types=self.table_source_types,
                page_archive=page.route3_page_archive,
                pageview_prefilter=page.pageview_prefilter,
                answer_type_mode=self.answer_type_mode,
                route3_slot_id=forced_answer_type,
            )
        search_queries = _sanitize_answer_blind_queries(
            response.get("search_queries", []),
            answer=answer,
            answer_aliases=aliases,
            answer_items=answer_items,
            max_queries=self.search_query_count,
        )
        tie_problem = _tie_completion_problem(
            source_table=source_table,
            reasoning_type=reasoning_type,
            answer=answer,
            answer_items=answer_items,
        )
        evidence_text = source_table.normalized_text if source_table is not None else display_cleanup(page.first_paragraph)
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
                tables=tables,
                llm_response=response,
                llm_prompt=prompt,
                llm_audit=llm_audit,
                source_table=source_table,
                table_selection=table_selection,
                timings=timings,
                answer_items=answer_items,
                answer_type=answer_type,
                reasoning_type=reasoning_type,
                tie_completion_warning=tie_problem,
                subject_anchors=subject_anchors,
                min_table_score=self.min_table_score,
                allowed_reasoning_types=self.allowed_reasoning_types,
                allowed_answer_types=slot_allowed_answer_types,
                extra_prompts=self.extra_prompts,
                table_filter_modes=self.table_filter_modes,
                table_source_types=self.table_source_types,
                prose_leakage_scoring_enabled=self.prose_leakage_scoring_enabled,
                llm_choose_table=self.llm_choose_table,
                page_archive=page.route3_page_archive,
                pageview_prefilter=page.pageview_prefilter,
                answer_type_mode=self.answer_type_mode,
                route3_slot_id=forced_answer_type,
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
    allowed_reasoning_types: Iterable[str] | None = DEFAULT_ROUTE3_REASONING_TYPES,
    allowed_answer_types: Iterable[str] | None = None,
    extra_prompts: Iterable[str] | str | None = None,
    llm_choose_table: bool = False,
    source_channel: str = "",
    answer_type_mode: str = DEFAULT_ROUTE3_ANSWER_TYPE_MODE,
) -> str:
    """Build the small-model prompt for Wikipedia table QA generation."""
    normalized_allowed_reasoning_types = normalize_route3_reasoning_types(allowed_reasoning_types)
    normalized_allowed_answer_types = normalize_route3_answer_types(allowed_answer_types)
    normalized_extra_prompts = normalize_route3_extra_prompts(extra_prompts)
    normalized_answer_type_mode = normalize_route3_answer_type_mode(answer_type_mode)
    is_all5_mode = normalized_answer_type_mode == "all5"
    prompt_answer_types = ROUTE3_ANSWER_TYPES if is_all5_mode else normalized_allowed_answer_types
    model_selects_reasoning_type = _model_selects_reasoning_type(normalized_allowed_reasoning_types)
    table_limit = 3 if llm_choose_table else 1
    prompt_tables = tables[:table_limit]
    prompt_source_label = _route3_prompt_source_label(
        prompt_tables,
        llm_choose_table=llm_choose_table,
        fallback_source_channel=source_channel,
    )
    has_wikitable_prompt_table = any(table.table_type == "wikitable" for table in prompt_tables)
    rendered_payload = _render_route3_prompt_payload(
        first_paragraph=first_paragraph,
        subject_anchors=subject_anchors,
        tables=prompt_tables,
        llm_choose_table=llm_choose_table,
    )
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
    output_schema = _route3_prompt_output_schema(
        normalized_answer_type_mode,
        prompt_answer_types,
        normalized_allowed_reasoning_types,
        include_source_table=bool(llm_choose_table),
    )
    mode_instruction = (
        "- Generate exactly one candidate for the configured answer type scope.\n"
        if not is_all5_mode
        else (
            "- Return exactly one JSON object with an `outputs` array containing exactly five fixed answer-type slots, in this order: Person, Place, Number, Date, Other.\n"
            "- Each slot must keep its fixed `answer_type`; do not choose a different answer_type for that slot.\n"
        )
    )
    answer_type_instruction = (
        _all5_answer_type_prompt_rule()
        if is_all5_mode
        else _answer_type_prompt_rule(normalized_allowed_answer_types)
    )
    unsupported_instruction = (
        ""
        if is_all5_mode
        else ""
    )
    answer_type_verification_instruction = (
        ""
    )
    search_query_instruction = (
        f"- For each generated all5 slot, generate exactly {search_query_count} answer-blind search queries. For discarded slots, use an empty search_queries array.\n"
        if is_all5_mode
        else f"- Generate exactly {search_query_count} answer-blind search queries.\n"
    )
    discard_instruction = (
        (
            "- For each all5 slot, if the table cannot support that answer type or the candidate would violate any rule, still include the slot with its fixed `answer_type`, set `discard_reason`, and set question, answer, answer_aliases, search_queries, source_table, and derivation_summary to empty values. Reject only that slot; still generate every other supported slot.\n\n"
            if llm_choose_table
            else "- For each all5 slot, if the table cannot support that answer type or the candidate would violate any rule, still include the slot with its fixed `answer_type`, set `discard_reason`, and set question, answer, answer_aliases, search_queries, and derivation_summary to empty values. Reject only that slot; still generate every other supported slot.\n\n"
        )
        if is_all5_mode
        else _discard_prompt_rule(
            normalized_allowed_reasoning_types,
            normalized_allowed_answer_types,
            model_selects_reasoning_type=model_selects_reasoning_type,
        )
    )
    wikitable_scope_instruction = (
        (
            "Wikitable-only guidance:\n"
            "- Use subject_anchors only to understand the page/table scope; do not copy anchor text mechanically into the question.\n"
            "- Let the table caption, nearby paragraph intro, or nearby section heading define the safe scope. Pay special attention to nearby intros with words like `following` or `above`; they often state which rows are included or excluded. For example, `15 largest commercial banks in Ukraine` supports asking which bank is largest in Ukraine, but not how many banks exist in Ukraine. A `1980 chart` table supports asking about facts in that 1980 chart, but not when a song first entered a chart because it may have entered in another year.\n"
        )
        if has_wikitable_prompt_table
        else ""
    )
    wikitable_answerable_instruction = (
        (
            "Wikitable-only guidance:\n"
            f"{toy_table_instruction}"
            "- Treat curated list pages such as `List of national parks of the United States` as complete and authoritative for membership within their stated scope. Do not hedge by saying `according to the List of ...`.\n"
        )
        if has_wikitable_prompt_table
        else ""
    )
    task_line = (
        f"Generate five fixed answer-type slots for long-tail SimpleQA-style factual questions from a Wikipedia {prompt_source_label}.\n"
        if is_all5_mode
        else f"Generate one long-tail SimpleQA-style factual question from a Wikipedia {prompt_source_label}.\n"
    )
    # PROMPT TEMPLATE:
    return (
        task_line +
        "Return JSON only.\n\n"
        "Requirements:\n\n"

        "### Must have a single answer.\n\n"
        "- The question must have exactly one intended, indisputable answer.\n"
        "- The answer must be a value from the table, not from the first paragraph etc.\n"
        f"{table_instruction}"
        "- Avoid questions with unclear or overly broad answer categories, such as `What equipment ...` `What genre ...`. Instead, ask about a more specific and verifiable attribute.\n"
        f"{_answer_precision_prompt_rule(prompt_answer_types)}"
        "- If a table cell has a parenthetical alias, put the plain entity name in answer and the parenthetical text in answer_aliases.\n"

        "### Reasoning type and Answer type rules:\n\n"
        "- Your question must match the reasoning type and answer type.\n"
        f"{mode_instruction}"
        f"{_reasoning_type_prompt_rule(normalized_allowed_reasoning_types)}"
        f"{answer_type_instruction}"
        f"{_tie_answer_prompt_rule(normalized_allowed_reasoning_types)}"
        f"{unsupported_instruction}"

        "### Reference answers should not change over time.\n\n"
        f"{_route3_stability_prompt_rule()}"
        "- Do not ask cumulative-statistic questions such as how many goals Messi has scored, total wins, career points, revenue, downloads, citations, or followers unless the statistic is explicitly scoped to a historically settled slice, completed event, completed season, or fixed table/list.\n"
        "- Do not ask about current, latest, most recent, or live-status facts such as the governor of a county.\n"
        "- Avoid mutable-sounding wording such as `total number`, `current`, or `latest`.\n"
        # "- For completed historical tables, phrase the comparison as a fixed result within the named event or list.\n"

        "### Use careful wording to avoid ambiguity.\n\n"
        f"{wikitable_scope_instruction}"
        "- Avoid vague phrases like `linked to`.\n"

        "### Must be challenging.\n\n"
        "- Prefer table facts that are not easily found in article prose outside tables.\n"
        "- Prefer answers that look unfamiliar to you and are likely to remain long-tail after search filtering.\n"
        
        "### Must be answerable.\n\n"
        f"- If the page title contains a cutoff-year marker in {cutoff_year} or later, use one of safe_subject_aliases when you need to name the subject; do not use the cutoff-year title text.\n"
        "- The question must be self-contained. It should be answerable without seeing the list or the table. Do not ask `What is ... in the list(table)?`.\n"
        # "- Do not cite the list unless the source is a well-known named chart or list, such as a Billboard chart, UNESCO list or a sports tournament chart. Phrases to avoid: `according to the table`, `according to the [source] table`, or `in the List of ...`. \n"
        # "- Ask about the facts in the table. Do not ask questions about the table itself, such as `What year does the estimate refer to`.\n"
        # "- Rendered markdown preserves table layout: a non-empty cell followed by blank cells may represent an HTML colspan cell. Treat it as one spanned cell, not as repeated field values.\n"
        # "- Full-width or partial-width spanned rows can appear anywhere in a table. Use them as local visual/context labels for nearby rows, not as direct answers to unrelated fields.\n"
        f"{wikitable_answerable_instruction}"
        "### Other prompt rules:\n\n"
        f"{_extra_prompt_rule(normalized_extra_prompts)}"
        "- Do not include the answer or answer aliases in the question or search queries.\n"
        f"{search_query_instruction}"
        f"{answer_type_verification_instruction}"
        f"{discard_instruction}"
        "\nOutput schema:\n"
        f"{output_schema}\n\n"
        f"Payload:\n{rendered_payload}"
    )


def build_route3_infobox_prompt(**kwargs: Any) -> str:
    """Build the Route 3 infobox-specific generation prompt."""
    return build_wikipedia_infobox_prompt(source_channel="infobox", **kwargs)


def build_route3_wikitable_prompt(**kwargs: Any) -> str:
    """Build the Route 3 wikitable-specific generation prompt."""
    return build_wikipedia_infobox_prompt(source_channel="wikitable", **kwargs)


def _route3_prompt_source_label(
    tables: list[WikipediaTable],
    *,
    llm_choose_table: bool,
    fallback_source_channel: str = "",
) -> str:
    """Return the source label shown in the generation prompt."""
    prompt_types = [
        table.table_type
        for table in tables
        if table.table_type in ROUTE3_TABLE_SOURCE_TYPE_SET
    ]
    unique_types = set(prompt_types)
    if llm_choose_table and {"wikitable", "infobox"}.issubset(unique_types):
        return "wikitable or infobox"
    if "wikitable" in unique_types:
        return "wikitable"
    if "infobox" in unique_types:
        return "infobox"
    fallback = str(fallback_source_channel or "").strip()
    if fallback in ROUTE3_TABLE_SOURCE_TYPE_SET:
        return fallback
    return "wikitable or infobox" if llm_choose_table else "table"


def _render_route3_prompt_payload(
    *,
    first_paragraph: str,
    subject_anchors: dict[str, Any],
    tables: list[WikipediaTable],
    llm_choose_table: bool,
) -> str:
    """Render the LLM-facing Route 3 payload as compact Markdown."""
    return "\n".join(
        [
            _render_route3_subject_anchor_section(subject_anchors),
            _render_route3_table_context_section(
                first_paragraph=first_paragraph,
                tables=tables,
                llm_choose_table=llm_choose_table,
            ),
            _render_route3_table_content_section(
                tables=tables,
                llm_choose_table=llm_choose_table,
            ),
        ]
    )


def _render_route3_subject_anchor_section(subject_anchors: dict[str, Any]) -> str:
    """Render subject anchor hints with explicit labels."""
    title_aliases = _string_list(subject_anchors.get("title_aliases", []))
    page_title = title_aliases or str(subject_anchors.get("page_title", "") or "").strip()
    safe_subject_aliases = _string_list(subject_anchors.get("safe_subject_aliases", []))
    return "\n".join(
        [
            "### subject_anchors",
            "",
            f"- `page title`: {_route3_prompt_value(page_title)}",
            f"- `safe_subject_aliases`: {_route3_prompt_value(safe_subject_aliases)}",
        ]
    )


def _render_route3_table_context_section(
    *,
    first_paragraph: str,
    tables: list[WikipediaTable],
    llm_choose_table: bool,
) -> str:
    """Render non-table context passed to the LLM."""
    lines = [
        "### table context",
        "",
        f"- `first_paragraph`: {_route3_prompt_value(first_paragraph)}",
    ]
    for table in tables:
        if llm_choose_table:
            lines.append(f"- `source_table`: {table.table_index}")
            lines.append(f"- `table_type`: {_route3_prompt_value(table.table_type)}")
        if table.table_type != "wikitable":
            continue
        lines.append(f"- `section_heading`: {_route3_prompt_value(table.section_heading)}")
        lines.append(f"- `caption`: {_route3_prompt_value(table.caption)}")
        lines.append(f"- `nearby_intro`: {_route3_prompt_value(table.nearby_intro)}")
    return "\n".join(lines)


def _render_route3_table_content_section(
    *,
    tables: list[WikipediaTable],
    llm_choose_table: bool,
) -> str:
    """Render table Markdown separately from the surrounding context."""
    lines = ["### table content", ""]
    for table_index, table in enumerate(tables):
        if table_index:
            lines.append("")
        if llm_choose_table:
            lines.append(f"- `source_table`: {table.table_index}")
        lines.append(f"- `table_type`: {_route3_prompt_value(table.table_type)}")
        lines.append(_route3_prompt_value(table.markdown or table.normalized_text))
    return "\n".join(lines)


def _route3_prompt_value(value: Any) -> str:
    """Return a readable Markdown scalar/list value for a prompt label."""
    if isinstance(value, (list, tuple)):
        cleaned = [str(item).strip() for item in value if str(item).strip()]
        return "; ".join(cleaned) if cleaned else "(none)"
    text = str(value or "").strip()
    return text if text else "(none)"


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


def normalize_route3_table_source_types(values: Iterable[str] | str | None) -> tuple[str, ...]:
    """Return normalized Route 3 source table types."""
    if values is None:
        return DEFAULT_ROUTE3_TABLE_SOURCE_TYPES
    raw_values: Iterable[str]
    if isinstance(values, str):
        raw_values = [values]
    else:
        raw_values = values
    normalized_values: list[str] = []
    seen: set[str] = set()
    for raw_value in raw_values:
        for part in str(raw_value or "").split(","):
            normalized_parts = _normalize_table_source_type(part)
            if not normalized_parts:
                continue
            for normalized in normalized_parts:
                if normalized not in ROUTE3_TABLE_SOURCE_TYPE_SET:
                    allowed = ", ".join((*ROUTE3_TABLE_SOURCE_TYPES, "both"))
                    raise ValueError(f"Unsupported Route 3 table source type {part!r}. Allowed values: {allowed}.")
                if normalized not in seen:
                    normalized_values.append(normalized)
                    seen.add(normalized)
    return tuple(normalized_values) or DEFAULT_ROUTE3_TABLE_SOURCE_TYPES


def normalize_route3_answer_type_mode(value: str | None) -> str:
    """Return the canonical Route 3 answer-type generation mode."""
    normalized = str(value or DEFAULT_ROUTE3_ANSWER_TYPE_MODE).strip().lower().replace("-", "_")
    aliases = {
        "one": "single",
        "single_type": "single",
        "all": "all5",
        "all_5": "all5",
        "five": "all5",
        "five_types": "all5",
    }
    normalized = aliases.get(normalized, normalized)
    if normalized not in ROUTE3_ANSWER_TYPE_MODES:
        allowed = ", ".join(ROUTE3_ANSWER_TYPE_MODES)
        raise ValueError(f"Unsupported Route 3 answer-type mode {value!r}. Allowed values: {allowed}.")
    return normalized


def _answer_type_hints_for_table_ranking(
    *,
    answer_type_mode: str,
    allowed_answer_types: Iterable[str] | str | None,
) -> tuple[str, ...]:
    """Return table-ranking answer-type hints only for explicit single-type generation."""
    if normalize_route3_answer_type_mode(answer_type_mode) != "single":
        return ()
    return _single_answer_type_hint(allowed_answer_types)


def _single_answer_type_hint(answer_type_hints: Iterable[str] | str | None) -> tuple[str, ...]:
    """Return a single normalized answer-type hint, or none for broad/multi-type scopes."""
    normalized_allowed_answer_types = normalize_route3_answer_types(answer_type_hints)
    if len(normalized_allowed_answer_types) != 1:
        return ()
    return normalized_allowed_answer_types


def normalize_route3_pageview_unavailable_policy(value: str | None) -> str:
    """Return the canonical policy for unavailable Route 3 pageview data."""
    normalized = str(value or DEFAULT_ROUTE3_PAGEVIEW_UNAVAILABLE_POLICY).strip().lower().replace("-", "_")
    if normalized not in ROUTE3_PAGEVIEW_UNAVAILABLE_POLICIES:
        allowed = ", ".join(ROUTE3_PAGEVIEW_UNAVAILABLE_POLICIES)
        raise ValueError(f"Unsupported Route 3 pageview unavailable policy {value!r}. Allowed values: {allowed}.")
    return normalized


def _normalize_table_source_type(value: str) -> tuple[str, ...]:
    """Return one or more canonical table source types for a configured value."""
    normalized = re.sub(r"[\s-]+", "_", str(value or "").strip().casefold())
    if not normalized:
        return ()
    if normalized in {
        "all",
        "all_tables",
        "both",
        "either",
        "infobox_and_wikitable",
        "infobox_and_wikitables",
        "infoboxes_and_wikitables",
        "infobox_wikitable",
        "infobox_wikitables",
    }:
        return DEFAULT_ROUTE3_TABLE_SOURCE_TYPES
    if normalized in {"infobox", "infoboxes", "right_infobox", "right_side_infobox"}:
        return ("infobox",)
    if normalized in {
        "wikitable",
        "wikitables",
        "article_table",
        "article_tables",
        "table",
        "tables",
    }:
        return ("wikitable",)
    return (normalized,)


def _route3_page_archive_path(cache_dir: Path | None, source_url: str) -> Path | None:
    """Return the unified Route 3 archive path for one page source."""
    if cache_dir is None:
        return None
    digest = hashlib.sha256(str(source_url or "").encode("utf-8")).hexdigest()
    return Path(cache_dir) / f"page_{digest}.json"


def _load_route3_page_archive(path: Path | None) -> tuple[dict[str, Any], bool]:
    """Load a Route 3 page archive, returning empty metadata when absent."""
    if path is None or not path.exists():
        return {}, False
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}, False
    return payload if isinstance(payload, dict) else {}, True


def _route3_archive_path_key(path: Path | None) -> str:
    """Return a stable comparison key for an archive path."""
    if path is None:
        return ""
    try:
        return str(Path(path).resolve(strict=False)).casefold()
    except OSError:
        return str(Path(path)).casefold()


def _read_only_route3_page_archive_metadata(
    path: Path | None,
    archive_payload: dict[str, Any],
    *,
    archive_fetch_status: dict[str, Any],
) -> dict[str, Any]:
    """Return archive audit metadata without writing a reused archive."""
    payload = dict(archive_payload) if isinstance(archive_payload, dict) else {}
    archive_sha256 = ""
    if path is not None and path.exists():
        try:
            archive_sha256 = _sha256_text(path.read_text(encoding="utf-8").rstrip("\n"))
        except OSError:
            archive_sha256 = ""
    archive_info = {
        "archive_path": str(path) if path is not None else "",
        "archive_enabled": path is not None,
        "archive_sha256": archive_sha256,
        "updated_at": str(payload.get("updated_at", "") or ""),
        "page_id": _positive_route3_page_id(payload.get("page_id")),
        "archive_read_only": True,
    }
    archive_info.update(archive_fetch_status)
    return archive_info


def _update_route3_page_archive(
    path: Path | None,
    archive_payload: dict[str, Any],
    *,
    source_url: str,
    title: str,
    canonical_url: str,
    parse_payload: dict[str, Any],
    html: str,
    prose_text: str,
    tables: list[WikipediaTable],
    archive_fetch_status: dict[str, Any],
) -> dict[str, Any]:
    """Write parse/table fields to the unified Route 3 page archive."""
    payload = dict(archive_payload) if isinstance(archive_payload, dict) else {}
    page_id = normalize_wikipedia_page_id(source_url)
    parse_body = parse_payload.get("parse", {}) if isinstance(parse_payload, dict) else {}
    if page_id is None and isinstance(parse_body, dict):
        try:
            page_id = int(parse_body.get("pageid"))
        except (TypeError, ValueError):
            page_id = None
    payload.update(
        {
            "source_url": source_url,
            "page_id": page_id,
            "title": title,
            "canonical_url": canonical_url,
            "parse_api_url": build_parse_api_url(source_url),
            "parse_payload": parse_payload,
            "parsed_html": html,
            "prose_text": prose_text,
            "extracted_tables": [table.to_metadata() for table in tables],
            "content_hashes": {
                **dict(payload.get("content_hashes", {}) if isinstance(payload.get("content_hashes"), dict) else {}),
                "parsed_html_sha256": _sha256_text(html),
                "parse_payload_sha256": _sha256_text(json.dumps(parse_payload, ensure_ascii=False, sort_keys=True)),
            },
            "updated_at": _utc_timestamp(),
        }
    )
    payload.setdefault("created_at", payload["updated_at"])
    archive_info = _write_route3_page_archive(path, payload)
    archive_info.update(archive_fetch_status)
    return archive_info


def _merge_route3_page_archive(page: WikipediaPageTables, updates: dict[str, Any]) -> None:
    """Merge additional fields into the unified Route 3 page archive."""
    archive = page.route3_page_archive if isinstance(page.route3_page_archive, dict) else {}
    path_text = str(archive.get("archive_path") or "").strip()
    if not path_text:
        return
    if bool(archive.get("archive_read_only")):
        merged = dict(archive)
        pageview_prefilter = updates.get("pageview_prefilter", {})
        if isinstance(pageview_prefilter, dict):
            merged["pageview_decision"] = str(pageview_prefilter.get("decision", "") or "")
            merged["pageview_status"] = str(pageview_prefilter.get("status", "") or "")
            pageview_payload = pageview_prefilter.get("pageview", {})
            if isinstance(pageview_payload, dict):
                merged["pageview_fetch_status"] = str(pageview_payload.get("fetch_status", "") or "")
        page.route3_page_archive = merged
        return
    path = Path(path_text)
    payload, _ = _load_route3_page_archive(path)
    payload.update(updates)
    payload["updated_at"] = _utc_timestamp()
    archive_info = _write_route3_page_archive(path, payload)
    merged = dict(archive)
    merged.update(archive_info)
    pageview_prefilter = updates.get("pageview_prefilter", {})
    if isinstance(pageview_prefilter, dict):
        merged["pageview_decision"] = str(pageview_prefilter.get("decision", "") or "")
        merged["pageview_status"] = str(pageview_prefilter.get("status", "") or "")
        pageview_payload = pageview_prefilter.get("pageview", {})
        if isinstance(pageview_payload, dict):
            merged["pageview_fetch_status"] = str(pageview_payload.get("fetch_status", "") or "")
    page.route3_page_archive = merged


def _write_route3_page_archive(path: Path | None, payload: dict[str, Any]) -> dict[str, Any]:
    """Persist one Route 3 archive and return audit metadata for records."""
    if path is None:
        return {
            "archive_path": "",
            "archive_enabled": False,
            "archive_sha256": "",
            "page_id": _positive_route3_page_id(payload.get("page_id")),
        }
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    path.write_text(text + "\n", encoding="utf-8")
    return {
        "archive_path": str(path),
        "archive_enabled": True,
        "archive_sha256": _sha256_text(text),
        "updated_at": payload.get("updated_at", ""),
        "page_id": _positive_route3_page_id(payload.get("page_id")),
    }


def _route3_pageview_prefilter(
    *,
    page: WikipediaPageTables,
    wikipedia_client: WikipediaClient,
    run_date: str,
    enabled: bool,
    window_months: int,
    max_monthly_average: float,
    max_underfilled_monthly: float,
    unavailable_policy: str,
) -> dict[str, Any]:
    """Return pageview prefilter metadata for one Route 3 page."""
    start, end = _pageview_month_range(run_date, window_months)
    article_title = page.title.replace(" ", "_")
    request_url = build_pageviews_api_url(article_title, start=start, end=end) if article_title else ""
    base = {
        "enabled": bool(enabled),
        "window_months": int(window_months),
        "max_monthly_average_pageviews": float(max_monthly_average),
        "max_underfilled_monthly_pageviews": float(max_underfilled_monthly),
        "unavailable_policy": unavailable_policy,
        "request": {
            "article": article_title,
            "start": start,
            "end": end,
            "url": request_url,
        },
        "archive_path": str(page.route3_page_archive.get("archive_path", "")) if isinstance(page.route3_page_archive, dict) else "",
    }
    if not enabled:
        return {**base, "status": "disabled", "decision": "allow", "reason": "pageview_prefilter_disabled"}
    archived_pageview = {}
    archive_path = str(page.route3_page_archive.get("archive_path", "")) if isinstance(page.route3_page_archive, dict) else ""
    if archive_path:
        archive_payload, _ = _load_route3_page_archive(Path(archive_path))
        archived_pageview = archive_payload.get("pageview", {}) if isinstance(archive_payload.get("pageview"), dict) else {}
    response = {}
    fetch_status = "archive_hit"
    errors: list[dict[str, str]] = []
    archived_request = archived_pageview.get("request", {}) if isinstance(archived_pageview, dict) else {}
    if (
        isinstance(archived_pageview, dict)
        and isinstance(archived_pageview.get("response"), dict)
        and archived_request.get("start") == start
        and archived_request.get("end") == end
        and archived_request.get("article") == article_title
    ):
        response = archived_pageview.get("response", {})
    else:
        fetch_status = "fetched"
        try:
            response = wikipedia_client.fetch_pageviews(article_title, start=start, end=end)
        except Exception as exc:  # noqa: BLE001
            response = {}
            fetch_status = "error"
            errors.append({"error_type": type(exc).__name__, "error_message": str(exc)})
    items = _pageview_items(response)
    pageview_payload = {
        "request": base["request"],
        "response": response,
        "fetch_status": fetch_status,
        "errors": errors,
    }
    if not items:
        decision = unavailable_policy
        if decision == "allow":
            reason = "pageview_unavailable_allowed"
        elif decision == "rerun":
            reason = "pageview_unavailable_rerun"
        else:
            reason = "pageview_unavailable_rejected"
        return {
            **base,
            "status": "unavailable" if not errors else "error",
            "decision": decision,
            "reason": reason,
            "pageview": pageview_payload,
            "monthly_items": [],
            "monthly_sum": 0,
            "monthly_average": None,
            "errors": errors,
        }
    monthly_sum = sum(int(item.get("views", 0) or 0) for item in items)
    monthly_average = monthly_sum / len(items)
    max_observed_monthly = max(int(item.get("views", 0) or 0) for item in items)
    observed_month_count = len(items)
    required_month_count = max(1, int(window_months))
    incomplete_window = observed_month_count < required_month_count
    if incomplete_window:
        decision = "reject" if max_observed_monthly > float(max_underfilled_monthly) else "allow"
        reason = (
            f"underfilled_monthly_pageviews>{float(max_underfilled_monthly):.4f}"
            if decision == "reject"
            else "underfilled_monthly_pageviews_within_threshold"
        )
    else:
        decision = "reject" if monthly_average > float(max_monthly_average) else "allow"
        reason = (
            f"monthly_average_pageviews>{float(max_monthly_average):.4f}"
            if decision == "reject"
            else "monthly_average_pageviews_within_threshold"
        )
    return {
        **base,
        "status": "incomplete_window" if incomplete_window else "ok",
        "decision": decision,
        "reason": reason,
        "pageview": pageview_payload,
        "monthly_items": items,
        "monthly_sum": monthly_sum,
        "monthly_average": round(monthly_average, 4),
        "max_observed_monthly": max_observed_monthly,
        "observed_month_count": observed_month_count,
        "required_month_count": required_month_count,
        "incomplete_window": incomplete_window,
        "errors": errors,
    }


def _pageview_month_range(run_date: str, window_months: int) -> tuple[str, str]:
    """Return Wikimedia monthly pageview start/end timestamps."""
    current = _coerce_iso_date(run_date)
    first_of_current = date(current.year, current.month, 1)
    end_month = _add_months(first_of_current, -1)
    start_month = _add_months(end_month, -(max(1, int(window_months)) - 1))
    return (
        f"{start_month.year:04d}{start_month.month:02d}0100",
        f"{end_month.year:04d}{end_month.month:02d}0100",
    )


def _add_months(value: date, months: int) -> date:
    """Return the first day shifted by a month offset."""
    month_index = value.year * 12 + value.month - 1 + int(months)
    year = month_index // 12
    month = month_index % 12 + 1
    return date(year, month, 1)


def _coerce_iso_date(value: str) -> date:
    """Return a date from an ISO-like string, falling back to today's UTC date."""
    try:
        return date.fromisoformat(str(value or "")[:10])
    except ValueError:
        return datetime.now(timezone.utc).date()


def _pageview_items(response: dict[str, Any]) -> list[dict[str, Any]]:
    """Return compact monthly pageview items from a Wikimedia response."""
    raw_items = response.get("items", []) if isinstance(response, dict) else []
    if not isinstance(raw_items, list):
        return []
    items: list[dict[str, Any]] = []
    for raw_item in raw_items:
        if not isinstance(raw_item, dict):
            continue
        try:
            views = int(raw_item.get("views", 0))
        except (TypeError, ValueError):
            continue
        items.append(
            {
                "timestamp": str(raw_item.get("timestamp", "")),
                "views": views,
            }
        )
    return items


def _complete_text_with_audit(llm_client: Any, prompt: str) -> dict[str, Any]:
    """Return LLM text and audit metadata, accepting legacy fake clients."""
    if hasattr(llm_client, "complete_text_with_audit"):
        audit = llm_client.complete_text_with_audit(prompt)
        if isinstance(audit, dict):
            return audit
    text = llm_client.complete_text(prompt)
    return {
        "text": str(text).strip(),
        "request_payload": {},
        "response_body": {},
    }


def _utc_timestamp() -> str:
    """Return an ISO UTC timestamp for archive metadata."""
    return datetime.now(timezone.utc).isoformat()


def _sha256_text(text: str) -> str:
    """Return the SHA-256 digest for one text value."""
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def _tables_matching_source_types(
    tables: list[WikipediaTable],
    table_source_types: Iterable[str] | str | None,
) -> list[WikipediaTable]:
    """Return only tables whose Route 3 source type is enabled."""
    allowed = set(normalize_route3_table_source_types(table_source_types))
    return [table for table in tables if table.table_type in allowed]


def _reasoning_type_prompt_rule(allowed_reasoning_types: tuple[str, ...]) -> str:
    """Return the Route 3 prompt rule for configured reasoning types."""
    reasoning_types = allowed_reasoning_types or ROUTE3_REASONING_TYPES
    if len(reasoning_types) == 1:
        reasoning_type = reasoning_types[0]
        return (
            f"- Use fixed `{reasoning_type}` reasoning: "
            f"{ROUTE3_REASONING_TYPE_PROMPT_RULES[reasoning_type]}. Do not include a `reasoning_type` field in the JSON.\n"
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


def _all5_answer_type_prompt_rule() -> str:
    """Return the Route 3 prompt rule for fixed all5 answer-type slots."""
    return (
        "- Apply each answer_type rule to its matching all5 slot:\n"
        f"{_type_rule_lines(ROUTE3_ANSWER_TYPE_PROMPT_RULES, ROUTE3_ANSWER_TYPES)}"
    )


def _type_rule_lines(rule_map: dict[str, str], values: tuple[str, ...]) -> str:
    """Return one explanatory rule per configured type."""
    return "".join(f"- `{value}`: {rule_map[value]}.\n" for value in values)

def _tie_answer_prompt_rule(allowed_reasoning_types: tuple[str, ...]) -> str:
    """Return tie-answer guidance when a tied reasoning operation is available."""
    if allowed_reasoning_types and not {"max", "min", "ordinal", "count"}.intersection(allowed_reasoning_types):
        return ""
    return "- If max/min/ordinal/count has tied answers, return answer as a JSON array containing every tied answer.\n"


def _discard_prompt_rule(
    allowed_reasoning_types: tuple[str, ...],
    allowed_answer_types: tuple[str, ...] = (),
    *,
    model_selects_reasoning_type: bool = True,
) -> str:
    """Return the prompt rule for impossible generation cases."""
    scopes: list[str] = []
    if allowed_reasoning_types:
        scopes.append("fixed reasoning rule")
    elif model_selects_reasoning_type:
        scopes.append("chosen reasoning_type rule")
    if allowed_answer_types:
        scopes.append("allowed answer_type rule")
    elif not allowed_answer_types:
        scopes.append("chosen answer_type rule")
    scope_text = " and ".join(scopes)
    return f"- If no safe question matching the {scope_text} is possible, set discard_reason and leave the other fields empty.\n\n"


def _reasoning_type_schema(allowed_reasoning_types: tuple[str, ...]) -> str:
    """Return the prompt schema value for reasoning_type."""
    return "|".join(allowed_reasoning_types or ROUTE3_REASONING_TYPES)


def _model_selects_reasoning_type(allowed_reasoning_types: tuple[str, ...]) -> bool:
    """Return whether the model must output a reasoning_type field."""
    return len(allowed_reasoning_types) != 1


def _fixed_reasoning_type(allowed_reasoning_types: tuple[str, ...]) -> str:
    """Return the configured reasoning type when it can be passed through."""
    return allowed_reasoning_types[0] if len(allowed_reasoning_types) == 1 else ""


def _answer_type_schema(allowed_answer_types: tuple[str, ...]) -> str:
    """Return the prompt schema value for answer_type."""
    return "|".join(allowed_answer_types or ROUTE3_ANSWER_TYPES)


def _route3_prompt_output_schema(
    answer_type_mode: str,
    allowed_answer_types: tuple[str, ...],
    allowed_reasoning_types: tuple[str, ...],
    *,
    include_source_table: bool,
) -> str:
    """Return the Route 3 prompt output schema for single or all5 mode."""
    include_reasoning_type = _model_selects_reasoning_type(allowed_reasoning_types)
    if normalize_route3_answer_type_mode(answer_type_mode) == "all5":
        slots = ",\n".join(
            _all5_prompt_output_schema_slot(
                answer_type,
                allowed_reasoning_types,
                include_reasoning_type=include_reasoning_type,
                include_source_table=include_source_table,
            )
            for answer_type in ROUTE3_ANSWER_TYPES
        )
        return (
            "{\n"
            '  "outputs": [\n'
            f"{slots}\n"
            "  ]\n"
            "}"
        )
    return (
        "{\n"
        '  "question": string,\n'
        '  "answer": string | string[],\n'
        f'  "answer_type": "{_answer_type_schema(allowed_answer_types)}",\n'
        '  "answer_aliases": string[],\n'
        '  "search_queries": string[],\n'
        + (
            f'  "reasoning_type": "{_reasoning_type_schema(allowed_reasoning_types)}",\n'
            if include_reasoning_type
            else ""
        )
        +
        ('  "source_table": integer,\n' if include_source_table else "")
        +
        '  "derivation_summary": string,\n'
        '  "discard_reason": string | null\n'
        "}"
    )


def _all5_prompt_output_schema_slot(
    answer_type: str,
    allowed_reasoning_types: tuple[str, ...],
    *,
    include_reasoning_type: bool,
    include_source_table: bool,
) -> str:
    """Return one fixed answer-type object for the all5 prompt schema."""
    return (
        "    {\n"
        f'      "answer_type": "{answer_type}",\n'
        '      "question": string,\n'
        '      "answer": string | string[],\n'
        '      "answer_aliases": string[],\n'
        '      "search_queries": string[],\n'
        + (
            f'      "reasoning_type": "{_reasoning_type_schema(allowed_reasoning_types)}",\n'
            if include_reasoning_type
            else ""
        )
        +
        ('      "source_table": integer | null,\n' if include_source_table else "")
        +
        '      "derivation_summary": string,\n'
        '      "discard_reason": string | null\n'
        "    }"
    )


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


def extract_wikipedia_tables(html: str, *, page_title: str = "") -> list[WikipediaTable]:
    """Extract infobox and wikitable records from MediaWiki parse HTML."""
    parser = _WikipediaTableParser(html)
    parser.feed(html)
    expected_infobox_title = _expected_infobox_page_title(page_title)
    first_infobox_like_seen = False
    tables: list[WikipediaTable] = []
    for index, frame in enumerate(parser.frames):
        if frame.get("table_type") == "infobox":
            if first_infobox_like_seen:
                continue
            first_infobox_like_seen = True
            recognition = _infobox_recognition(frame, page_title=page_title)
            frame["infobox_recognition"] = recognition
            if expected_infobox_title:
                if not recognition.get("at_page_start"):
                    continue
                if not recognition.get("title_matches_page_title"):
                    continue
        table = _build_wikipedia_table(index + 1, frame, page_title=page_title)
        if len(table.rows) > MAX_TABLE_ROWS:
            continue
        if len(table.markdown) > MAX_TABLE_MARKDOWN_CHARS:
            continue
        tables.append(table)
    _annotate_horizontal_companion_table_groups(tables)
    return tables


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
    prose_leakage_scoring_enabled: bool = DEFAULT_ROUTE3_PROSE_LEAKAGE_SCORING_ENABLED,
    answer_type_hints: Iterable[str] | str | None = None,
) -> list[dict[str, Any]]:
    """Rank tables by structured composition value and low prose leakage."""
    prose = source_display_cleanup(f"{first_paragraph} {prose_text}")
    normalized_answer_type_hints = _single_answer_type_hint(answer_type_hints)
    ranked: list[dict[str, Any]] = []
    for table in tables:
        data_rows = _data_rows(table)
        data_row_count = len(data_rows)
        structure = table.structure if isinstance(table.structure, dict) else {}
        row_count = _metadata_int(structure.get("row_count")) or data_row_count
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
        leaked_values, checked_values = _prose_leakage_counts(table, prose)
        leakage_rate = leaked_values / checked_values if checked_values else 0.0
        score = 0.0
        reasons: list[str] = []
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
        if prose_leakage_scoring_enabled and leakage_rate < PROSE_LEAKAGE_LOW_RATE_THRESHOLD:
            score += PROSE_LEAKAGE_LOW_SCORE_BONUS
            reasons.append("low_prose_leakage")
        elif prose_leakage_scoring_enabled and leakage_rate > PROSE_LEAKAGE_HIGH_RATE_THRESHOLD:
            score -= PROSE_LEAKAGE_HIGH_SCORE_PENALTY
            reasons.append("high_prose_leakage")
        answer_type_score_bonus, answer_type_score = _table_answer_type_score(
            table,
            normalized_answer_type_hints,
        )
        if answer_type_score_bonus:
            score += answer_type_score_bonus
            reasons.append("answer_type_score_bonus")
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
                "data_row_count": data_row_count,
                "numeric_cell_count": numeric_cell_count,
                "comparable_header_hits": comparable_header_hits,
                "preferred_context_hits": preferred_context_hits,
                "mutable_context_hits": mutable_context_hits,
                "live_scope_rejection_reason": live_scope_reason,
                "zero_numeric_rate": round(zero_numeric_rate, 4),
                "answer_type_score_bonus": round(answer_type_score_bonus, 4),
                "answer_type_score": answer_type_score,
                "prose_leakage": {
                    "checked_values": checked_values,
                    "leaked_values": leaked_values,
                    "leakage_rate": round(leakage_rate, 4),
                    "scoring_enabled": bool(prose_leakage_scoring_enabled),
                    "low_rate_threshold": PROSE_LEAKAGE_LOW_RATE_THRESHOLD,
                    "low_score_bonus": PROSE_LEAKAGE_LOW_SCORE_BONUS,
                    "high_rate_threshold": PROSE_LEAKAGE_HIGH_RATE_THRESHOLD,
                    "high_score_penalty": PROSE_LEAKAGE_HIGH_SCORE_PENALTY,
                },
            }
        )
    return sorted(
        ranked,
        key=lambda row: (
            -float(row["score"]),
            0 if str(row.get("table_type", "")) == "infobox" else 1,
            float(row.get("prose_leakage", {}).get("leakage_rate", 0.0)),
            int(row["table_index"]),
        ),
    )


def _table_answer_type_score(
    table: WikipediaTable,
    answer_type_hints: Iterable[str] | str | None,
) -> tuple[float, dict[str, Any]]:
    """Return answer-type ranking bonus and audit metadata for a table."""
    hints = normalize_route3_answer_types(answer_type_hints)
    hits: list[dict[str, Any]] = []
    score = 0.0
    text = _table_answer_type_text(table)
    if "Person" in hints:
        person_hit = _person_answer_type_hit(text)
        if person_hit:
            score += ANSWER_TYPE_PERSON_TABLE_SCORE_BONUS
            hits.append(
                {
                    "answer_type": "Person",
                    "bonus": ANSWER_TYPE_PERSON_TABLE_SCORE_BONUS,
                    "rule": "consecutive_initial_caps_non_common_words",
                    **person_hit,
                }
            )
    if "Place" in hints:
        place_hits = _place_answer_type_markers(table)
        if place_hits:
            score += ANSWER_TYPE_PLACE_TABLE_SCORE_BONUS
            hits.append(
                {
                    "answer_type": "Place",
                    "bonus": ANSWER_TYPE_PLACE_TABLE_SCORE_BONUS,
                    "rule": "place_seed_whitelist",
                    "markers": place_hits[:10],
                }
            )
    if "Date" in hints:
        date_hits = _date_answer_type_markers(text)
        if date_hits:
            score += ANSWER_TYPE_DATE_TABLE_SCORE_BONUS
            hits.append(
                {
                    "answer_type": "Date",
                    "bonus": ANSWER_TYPE_DATE_TABLE_SCORE_BONUS,
                    "rule": "date_marker",
                    "markers": date_hits,
                }
            )
    return round(score, 4), {
        "hints": list(hints),
        "bonus": round(score, 4),
        "hits": hits,
    }


def _table_answer_type_text(table: WikipediaTable) -> str:
    """Return table-owned text used for answer-type ranking hints."""
    parts = [
        table.section_heading,
        table.caption,
        table.nearby_intro,
        " ".join(table.headers),
        table.normalized_text,
    ]
    parts.extend(cell for row in table.rows for cell in row)
    return " ".join(str(part or "") for part in parts)


@lru_cache(maxsize=1)
def _answer_type_common_words() -> set[str]:
    """Load the cached common-word lexicon used by the Person table hint."""
    try:
        lines = COMMON_WORD_LEXICON_PATH.read_text(encoding="utf-8").splitlines()
    except OSError:
        return set(COMMON_WORD_FALLBACKS)
    words: set[str] = set()
    for line in lines:
        token = str(line or "").strip().split()
        if token:
            words.add(token[0].lower())
    return words or set(COMMON_WORD_FALLBACKS)


def _person_answer_type_hit(text: str) -> dict[str, Any]:
    """Return a Person hint hit when two adjacent initial-cap words are uncommon."""
    common_words = _answer_type_common_words()
    previous: str | None = None
    for match in ANSWER_TYPE_WORD_PATTERN.finditer(text):
        word = match.group(0)
        if _is_uncommon_initial_cap_word(word, common_words):
            if previous is not None:
                return {"pair": [previous, word]}
            previous = word
        else:
            previous = None
    return {}


def _is_uncommon_initial_cap_word(word: str, common_words: set[str]) -> bool:
    """Return whether a token is initial-capitalized and not a common word."""
    stripped = word.strip("'-.")
    if len(stripped) < 2:
        return False
    return stripped[0].isupper() and stripped.lower() not in common_words


def _place_answer_type_markers(table: WikipediaTable) -> list[str]:
    """Return Place answer-type whitelist markers present in table text."""
    return _text_exact_markers(
        _table_marker_text(table),
        sorted(PLACE_SEED_WHITELIST, key=lambda marker: (-len(marker), marker)),
    )


def _date_answer_type_markers(text: str) -> list[dict[str, Any]]:
    """Return Date answer-type marker hits present in table text."""
    normalized_text = _normalize_marker_text(text)
    markers: list[dict[str, Any]] = []
    month_hits = _text_exact_markers(normalized_text, ANSWER_TYPE_MONTH_MARKERS)
    if month_hits:
        markers.append({"rule": "month_name", "matches": month_hits[:10]})
    year_hits: list[str] = []
    for match in ANSWER_TYPE_DATE_YEAR_PATTERN.finditer(text):
        year = int(match.group("year"))
        if ANSWER_TYPE_DATE_YEAR_MIN <= year <= ANSWER_TYPE_DATE_YEAR_MAX:
            year_hits.append(match.group("year"))
    year_hits = _dedupe_preserving_order(year_hits)
    if year_hits:
        markers.append({"rule": "year_1500_2040_no_comma", "matches": year_hits[:10]})
    numeric_date_hits: list[str] = []
    for match in ANSWER_TYPE_DATE_NUMERIC_MDY_PATTERN.finditer(text):
        month = int(match.group("month"))
        day = int(match.group("day"))
        year = int(match.group("year"))
        if (
            1 <= month <= 12
            and 1 <= day <= 31
            and ANSWER_TYPE_DATE_YEAR_MIN <= year <= ANSWER_TYPE_DATE_YEAR_MAX
        ):
            numeric_date_hits.append(match.group(0))
    numeric_date_hits = _dedupe_preserving_order(numeric_date_hits)
    if numeric_date_hits:
        markers.append({"rule": "numeric_month_day_year", "matches": numeric_date_hits[:10]})
    return markers


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


def _prepare_route3_tables_for_scoring(
    tables: list[WikipediaTable],
    table_filter_modes: Iterable[str] | str | None,
    *,
    infobox_max_removed_row_rate: float = DEFAULT_ROUTE3_INFOBOX_MAX_REMOVED_ROW_RATE,
    infobox_min_remaining_rows: int = DEFAULT_ROUTE3_INFOBOX_MIN_REMAINING_ROWS,
) -> list[WikipediaTable]:
    """Return tables prepared for ranking with infobox row-level cleanup applied."""
    modes = normalize_route3_table_filter_modes(table_filter_modes)
    return [
        _prepare_infobox_table_for_row_filters(
            table,
            modes,
            infobox_max_removed_row_rate=infobox_max_removed_row_rate,
            infobox_min_remaining_rows=infobox_min_remaining_rows,
        )
        for table in tables
    ]


def _prepare_infobox_table_for_row_filters(
    table: WikipediaTable,
    table_filter_modes: Iterable[str] | str | None,
    *,
    infobox_max_removed_row_rate: float = DEFAULT_ROUTE3_INFOBOX_MAX_REMOVED_ROW_RATE,
    infobox_min_remaining_rows: int = DEFAULT_ROUTE3_INFOBOX_MIN_REMAINING_ROWS,
) -> WikipediaTable:
    """Return an infobox copy with image and low-quality key-value rows removed."""
    if table.table_type != "infobox":
        return table
    structure = table.structure if isinstance(table.structure, dict) else {}
    existing_filtering = structure.get("infobox_row_filtering", {})
    if isinstance(existing_filtering, dict) and existing_filtering.get("applied"):
        return table

    modes = normalize_route3_table_filter_modes(table_filter_modes)
    row_filter_modes = [mode for mode in INFOBOX_ROW_FILTER_MODES if mode in modes]
    header_row_count = _metadata_int(structure.get("header_row_count"))
    image_grid_row_indexes = _metadata_int_set(structure.get("image_row_indexes", []))
    image_caption_grid_row_indexes = _metadata_int_set(structure.get("image_caption_row_indexes", []))
    image_title_grid_row_indexes = _metadata_int_set(structure.get("image_title_row_indexes", []))
    key_value_grid_row_indexes = _metadata_int_set(structure.get("key_value_row_indexes", []))
    original_picture_stats = _picture_heavy_table_stats(table)
    original_row_count = _metadata_int(structure.get("row_count")) or len(table.rows)

    filtered_rows: list[list[str]] = []
    removed_rows: list[dict[str, Any]] = []
    for table_row_index, raw_row in enumerate(table.rows):
        grid_row_index = table_row_index + header_row_count
        row = [str(cell or "").strip() for cell in raw_row]
        if grid_row_index in image_grid_row_indexes:
            removed_rows.append(
                _infobox_removed_row_payload(
                    table_row_index=table_row_index,
                    grid_row_index=grid_row_index,
                    row=row,
                    reasons=["no_picture_heavy_tables:image_row"],
                    details={},
                )
            )
            continue
        if grid_row_index in image_caption_grid_row_indexes:
            removed_rows.append(
                _infobox_removed_row_payload(
                    table_row_index=table_row_index,
                    grid_row_index=grid_row_index,
                    row=row,
                    reasons=["no_picture_heavy_tables:image_caption_row"],
                    details={},
                )
            )
            continue
        if grid_row_index in image_title_grid_row_indexes:
            removed_rows.append(
                _infobox_removed_row_payload(
                    table_row_index=table_row_index,
                    grid_row_index=grid_row_index,
                    row=row,
                    reasons=["no_picture_heavy_tables:image_title_row"],
                    details={},
                )
            )
            continue
        if _is_infobox_key_value_row(
            row,
            grid_row_index=grid_row_index,
            key_value_grid_row_indexes=key_value_grid_row_indexes,
        ):
            row_reasons, row_details = _infobox_quality_row_filter_reasons(
                table,
                row,
                row_filter_modes,
            )
            if row_reasons:
                removed_rows.append(
                    _infobox_removed_row_payload(
                        table_row_index=table_row_index,
                        grid_row_index=grid_row_index,
                        row=row,
                        reasons=row_reasons,
                        details=row_details,
                    )
                )
                continue
        filtered_rows.append(row)

    filtered_markdown = _grid_to_markdown(table.headers, filtered_rows)
    filtered_structure = _filtered_infobox_structure(
        table,
        filtered_rows=filtered_rows,
        removed_rows=removed_rows,
        row_filter_modes=row_filter_modes,
        original_row_count=original_row_count,
        original_picture_stats=original_picture_stats,
        infobox_max_removed_row_rate=infobox_max_removed_row_rate,
        infobox_min_remaining_rows=infobox_min_remaining_rows,
    )
    normalized_parts = [
        table.section_heading,
        table.caption,
        filtered_markdown,
    ]
    return WikipediaTable(
        table_index=table.table_index,
        table_type=table.table_type,
        section_heading=table.section_heading,
        caption=table.caption,
        nearby_intro=table.nearby_intro,
        headers=list(table.headers),
        rows=filtered_rows,
        row_dicts=list(table.row_dicts),
        normalized_text="\n".join(part for part in normalized_parts if part),
        markdown=filtered_markdown,
        structure=filtered_structure,
    )


def _infobox_quality_row_filter_reasons(
    source_table: WikipediaTable,
    row: list[str],
    row_filter_modes: Iterable[str],
) -> tuple[list[str], dict[str, Any]]:
    """Return row-level infobox quality rejection reasons and audit details."""
    row_table = _infobox_single_row_table(source_table, row)
    reasons: list[str] = []
    details: dict[str, Any] = {}
    if "no_incomplete_tables" in row_filter_modes:
        incomplete_markers = _incomplete_table_markers(row_table)
        details["incomplete_table_markers"] = incomplete_markers
        if incomplete_markers:
            reasons.append(f"no_incomplete_tables:{','.join(incomplete_markers)}")
    if "not_number_dominant" in row_filter_modes:
        number_dominance_stats = _number_dominance_table_stats(row_table)
        details["number_dominance_stats"] = number_dominance_stats
        number_dominance_reason = _number_dominance_table_filter_reason(number_dominance_stats)
        if number_dominance_reason:
            reasons.append(number_dominance_reason)
    if "no_social_science_research" in row_filter_modes:
        social_science_markers = _table_text_markers(row_table, SOCIAL_SCIENCE_TABLE_MARKERS)
        details["social_science_markers"] = social_science_markers
        if social_science_markers:
            reasons.append(f"no_social_science_research:{','.join(social_science_markers)}")
    return reasons, details


def _infobox_single_row_table(source_table: WikipediaTable, row: list[str]) -> WikipediaTable:
    """Build a tiny table so existing row-quality rules can be reused."""
    headers = (
        list(source_table.headers)
        if source_table.headers
        else [f"Column {index + 1}" for index, _ in enumerate(row)]
    )
    markdown = _grid_to_markdown(headers, [row])
    return WikipediaTable(
        table_index=source_table.table_index,
        table_type=source_table.table_type,
        section_heading="",
        caption="",
        nearby_intro="",
        headers=headers,
        rows=[row],
        row_dicts=[],
        normalized_text=markdown or " ".join(row),
        markdown=markdown,
        structure={"row_count": 1, "header_row_count": 0},
    )


def _filtered_infobox_structure(
    table: WikipediaTable,
    *,
    filtered_rows: list[list[str]],
    removed_rows: list[dict[str, Any]],
    row_filter_modes: list[str],
    original_row_count: int,
    original_picture_stats: dict[str, Any],
    infobox_max_removed_row_rate: float = DEFAULT_ROUTE3_INFOBOX_MAX_REMOVED_ROW_RATE,
    infobox_min_remaining_rows: int = DEFAULT_ROUTE3_INFOBOX_MIN_REMAINING_ROWS,
) -> dict[str, Any]:
    """Return updated infobox structure metadata after row-level cleanup."""
    source_structure = table.structure if isinstance(table.structure, dict) else {}
    structure = dict(source_structure)
    header_row_count = _metadata_int(structure.get("header_row_count"))
    key_value_row_indexes = [
        index + header_row_count
        for index, row in enumerate(filtered_rows)
        if _is_key_value_text_row(row)
    ]
    removed_reasons = _dedupe_preserving_order(
        reason
        for removed_row in removed_rows
        for reason in removed_row.get("reasons", [])
    )
    original_non_header_row_count = max(0, int(original_row_count) - int(header_row_count))
    removed_row_rate = (
        len(removed_rows) / original_non_header_row_count
        if original_non_header_row_count
        else 0.0
    )
    max_removed_row_rate = max(0.0, min(1.0, float(infobox_max_removed_row_rate)))
    min_remaining_rows = max(0, int(infobox_min_remaining_rows))
    remaining_non_header_row_count = len(filtered_rows)
    structure.setdefault("original_row_count", original_row_count)
    structure.setdefault("original_image_row_indexes", list(structure.get("image_row_indexes", [])))
    structure.setdefault("original_image_caption_row_indexes", list(structure.get("image_caption_row_indexes", [])))
    structure.setdefault("original_image_title_row_indexes", list(structure.get("image_title_row_indexes", [])))
    structure.setdefault("original_image_context_row_indexes", list(structure.get("image_context_row_indexes", [])))
    structure.setdefault("original_key_value_row_indexes", list(structure.get("key_value_row_indexes", [])))
    structure["row_count"] = header_row_count + len(filtered_rows)
    structure["filtered_row_count"] = len(filtered_rows)
    structure["filtered_key_value_row_count"] = len(key_value_row_indexes)
    structure["key_value_row_indexes"] = key_value_row_indexes
    structure["image_row_indexes"] = []
    structure["image_caption_row_indexes"] = []
    structure["image_title_row_indexes"] = []
    structure["image_context_row_indexes"] = []
    for key in (
        "image_raw_cell_count",
        "image_covered_cell_count",
        "non_title_image_raw_cell_count",
        "non_title_image_covered_cell_count",
    ):
        structure[key] = 0
    structure["image_cell_rate"] = 0.0
    structure["non_title_image_cell_rate"] = 0.0
    structure["infobox_row_filtering"] = {
        "applied": True,
        "row_filter_modes": row_filter_modes,
        "original_row_count": original_row_count,
        "remaining_row_count": header_row_count + len(filtered_rows),
        "remaining_non_header_row_count": remaining_non_header_row_count,
        "min_remaining_rows": min_remaining_rows,
        "remaining_rows_below_minimum": remaining_non_header_row_count < min_remaining_rows,
        "remaining_key_value_row_count": len(key_value_row_indexes),
        "removed_row_count": len(removed_rows),
        "original_non_header_row_count": original_non_header_row_count,
        "removed_row_rate": round(removed_row_rate, 4),
        "max_removed_row_rate": max_removed_row_rate,
        "removed_row_rate_exceeded": removed_row_rate > max_removed_row_rate,
        "removed_reasons": removed_reasons,
        "removed_rows": removed_rows[:20],
        "original_picture_heavy_table_stats": original_picture_stats,
    }
    return structure


def _infobox_removed_row_payload(
    *,
    table_row_index: int,
    grid_row_index: int,
    row: list[str],
    reasons: list[str],
    details: dict[str, Any],
) -> dict[str, Any]:
    """Return compact audit metadata for one removed infobox row."""
    payload = {
        "table_row_index": table_row_index,
        "grid_row_index": grid_row_index,
        "row": row,
        "reasons": reasons,
    }
    payload.update(details)
    return payload


def _is_infobox_key_value_row(
    row: list[str],
    *,
    grid_row_index: int,
    key_value_grid_row_indexes: set[int],
) -> bool:
    """Return whether an infobox row should be treated as a key-value pair."""
    if key_value_grid_row_indexes:
        return grid_row_index in key_value_grid_row_indexes
    return _is_key_value_text_row(row)


def _is_key_value_text_row(row: list[str]) -> bool:
    """Return whether a rendered row looks like one infobox key-value pair."""
    if len(row) < 2:
        return False
    if not str(row[0]).strip():
        return False
    return any(str(cell).strip() for cell in row[1:])


def _metadata_int_set(values: Any) -> set[int]:
    """Return integer metadata values, dropping invalid entries."""
    if values is None:
        return set()
    if isinstance(values, (str, bytes)) or not hasattr(values, "__iter__"):
        values = [values]
    parsed: set[int] = set()
    for value in values:
        try:
            parsed.add(int(str(value).strip()))
        except (TypeError, ValueError):
            continue
    return parsed


def _refresh_selection_payload_table_counts(row: dict[str, Any], table: WikipediaTable) -> None:
    """Refresh ranked-row audit counts after infobox row filtering."""
    data_rows = _data_rows(table)
    structure = table.structure if isinstance(table.structure, dict) else {}
    row["row_count"] = _metadata_int(structure.get("row_count")) or len(data_rows)
    row["data_row_count"] = len(data_rows)
    row["numeric_cell_count"] = sum(
        1
        for data_row in data_rows
        for cell in data_row
        if _is_numeric_value_cell(cell)
    )


def _annotate_table_filter_modes(
    table_selection: list[dict[str, Any]],
    table_filter_modes: Iterable[str] | str | None,
    *,
    infobox_max_removed_row_rate: float = DEFAULT_ROUTE3_INFOBOX_MAX_REMOVED_ROW_RATE,
    infobox_min_remaining_rows: int = DEFAULT_ROUTE3_INFOBOX_MIN_REMAINING_ROWS,
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
            table = _prepare_infobox_table_for_row_filters(
                table,
                modes,
                infobox_max_removed_row_rate=infobox_max_removed_row_rate,
                infobox_min_remaining_rows=infobox_min_remaining_rows,
            )
            copied["table"] = table
            if table.table_type == "infobox":
                _refresh_selection_payload_table_counts(copied, table)
                structure = table.structure if isinstance(table.structure, dict) else {}
                copied["infobox_row_filtering"] = structure.get("infobox_row_filtering", {})
                copied["picture_heavy_table_stats"] = _picture_heavy_table_stats(table)
                infobox_filtering = copied["infobox_row_filtering"]
                if isinstance(infobox_filtering, dict) and infobox_filtering.get("removed_row_rate_exceeded"):
                    reasons.append(
                        "infobox_removed_row_rate_gt_max:"
                        f"removed_row_rate={float(infobox_filtering.get('removed_row_rate', 0.0)):.4f};"
                        f"max={float(infobox_filtering.get('max_removed_row_rate', infobox_max_removed_row_rate)):.4f}"
                    )
                if isinstance(infobox_filtering, dict) and infobox_filtering.get("remaining_rows_below_minimum"):
                    reasons.append(
                        "infobox_remaining_rows_lt_min:"
                        f"remaining_non_header_rows={int(infobox_filtering.get('remaining_non_header_row_count', 0) or 0)};"
                        f"min={int(infobox_filtering.get('min_remaining_rows', infobox_min_remaining_rows) or 0)}"
                    )
            too_few_rows_reason = _too_few_total_rows_filter_reason(table)
            if not reasons and too_few_rows_reason:
                reasons.append(too_few_rows_reason)
            elif "no_external_links_tables" in modes:
                external_links_reason = external_links_table_filter_reason(table.section_heading)
                if external_links_reason:
                    reasons.append(external_links_reason)
            if not reasons and "no_horizontal_companion_tables" in modes:
                horizontal_reason = _horizontal_companion_table_filter_reason(table)
                if horizontal_reason:
                    reasons.append(horizontal_reason)
            if not reasons and table.table_type != "infobox" and "no_picture_heavy_tables" in modes:
                picture_stats = _picture_heavy_table_stats(table)
                copied["picture_heavy_table_stats"] = picture_stats
                picture_reason = _picture_heavy_table_filter_reason(table, picture_stats)
                if picture_reason:
                    reasons.append(picture_reason)
            if not reasons and table.table_type != "infobox" and "no_incomplete_tables" in modes:
                incomplete_markers = _incomplete_table_markers(table)
                copied["incomplete_table_markers"] = incomplete_markers
                if incomplete_markers:
                    reasons.append(f"no_incomplete_tables:{','.join(incomplete_markers)}")
            if not reasons and table.table_type != "infobox" and "not_number_dominant" in modes:
                number_dominance_stats = _number_dominance_table_stats(table)
                copied["number_dominance_stats"] = number_dominance_stats
                number_dominance_reason = _number_dominance_table_filter_reason(number_dominance_stats)
                if number_dominance_reason:
                    reasons.append(number_dominance_reason)
            if not reasons and table.table_type != "infobox" and "no_social_science_research" in modes:
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


def _too_few_total_rows_filter_reason(table: WikipediaTable) -> str:
    """Return the hard row-count rejection reason for tables too short to be useful."""
    structure = table.structure if isinstance(table.structure, dict) else {}
    row_count = _metadata_int(structure.get("row_count")) or len(table.rows)
    if row_count < MIN_TABLE_TOTAL_ROWS:
        return f"too_few_rows:row_count={row_count};min_rows={MIN_TABLE_TOTAL_ROWS}"
    return ""


def _horizontal_companion_table_filter_reason(table: WikipediaTable) -> str:
    """Return the horizontal-companion rejection reason for one table, if any."""
    if table.table_type != "wikitable":
        return ""
    structure = table.structure if isinstance(table.structure, dict) else {}
    group_size = _metadata_int(structure.get("horizontal_companion_group_size"))
    if group_size < 2:
        return ""
    layout_markers = [
        str(marker)
        for marker in structure.get("horizontal_layout_markers", [])
        if str(marker).strip()
    ]
    if not layout_markers:
        return ""
    width = _metadata_int(structure.get("expanded_width"))
    row_count = _metadata_int(structure.get("row_count"))
    if width > HORIZONTAL_COMPANION_TABLE_MAX_WIDTH:
        return ""
    if row_count > HORIZONTAL_COMPANION_TABLE_MAX_ROWS:
        return ""
    markers = ",".join(layout_markers)
    return (
        "no_horizontal_companion_tables:"
        f"{markers};group_size={group_size};width={width};rows={row_count}"
    )


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
    non_title_image_covered = int(structure.get("non_title_image_covered_cell_count", image_covered) or 0)
    non_title_total_covered = int(structure.get("non_title_total_cell_coverage_count", total_covered) or 0)
    non_title_image_raw = int(structure.get("non_title_image_raw_cell_count", image_raw) or 0)
    non_title_total_raw = int(structure.get("non_title_raw_cell_count", total_raw) or 0)
    rate = image_covered / total_covered if total_covered > 0 else 0.0
    non_title_rate = (
        non_title_image_covered / non_title_total_covered
        if non_title_total_covered > 0
        else 0.0
    )
    return {
        "image_raw_cell_count": image_raw,
        "raw_cell_count": total_raw,
        "image_covered_cell_count": image_covered,
        "total_cell_coverage_count": total_covered,
        "image_cell_rate": round(rate, 4),
        "non_title_image_raw_cell_count": non_title_image_raw,
        "non_title_raw_cell_count": non_title_total_raw,
        "non_title_image_covered_cell_count": non_title_image_covered,
        "non_title_total_cell_coverage_count": non_title_total_covered,
        "non_title_image_cell_rate": round(non_title_rate, 4),
        "non_title_image_cell_rate_threshold": PICTURE_HEAVY_INFOBOX_MAX_NON_TITLE_IMAGE_CELL_RATE,
    }


def _picture_heavy_table_filter_reason(table: WikipediaTable, stats: dict[str, Any]) -> str:
    """Return the picture-heavy rejection reason for one table, if any."""
    image_rate = float(stats.get("image_cell_rate", 0.0) or 0.0)
    image_count = int(stats.get("image_covered_cell_count", 0) or 0)
    if table.table_type == "wikitable" and image_count:
        return f"no_picture_heavy_tables:wikitable_image_cell_count={image_count}"
    non_title_image_rate = float(stats.get("non_title_image_cell_rate", image_rate) or 0.0)
    non_title_image_count = int(stats.get("non_title_image_covered_cell_count", image_count) or 0)
    if (
        table.table_type == "infobox"
        and non_title_image_count
        and non_title_image_rate > PICTURE_HEAVY_INFOBOX_MAX_NON_TITLE_IMAGE_CELL_RATE
    ):
        return f"no_picture_heavy_tables:non_title_image_cell_rate={non_title_image_rate:.4f}"
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
    texts = [table.section_heading, table.caption, *table.headers]
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
    checked_text = source_display_cleanup(
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
    return [
        marker
        for marker in markers
        if text_contains_match(checked_text, build_text_matcher(marker), cleanup=source_display_cleanup)
    ]


def _selection_score(row: dict[str, Any]) -> float:
    """Return one ranked table score as a float."""
    try:
        return float(row.get("score", 0.0))
    except (TypeError, ValueError):
        return 0.0


def _metadata_int(value: Any) -> int:
    """Return an integer metadata value, defaulting to zero."""
    try:
        return int(str(value or "").strip())
    except (TypeError, ValueError):
        return 0


class _FirstParagraphParser(HTMLParser):
    """Minimal paragraph text collector."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._in_paragraph = False
        self._current: list[str] = []
        self.paragraphs: list[list[str]] = []
        self._suppressed_tag = ""

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style"}:
            self._suppressed_tag = tag
            return
        if self._suppressed_tag:
            return
        if tag == "p" and not self.paragraphs:
            self._in_paragraph = True
            self._current = []

    def handle_endtag(self, tag: str) -> None:
        if tag == self._suppressed_tag:
            self._suppressed_tag = ""
            return
        if self._suppressed_tag:
            return
        if tag == "p" and self._in_paragraph:
            text = _clean_text(" ".join(self._current))
            if text:
                self.paragraphs.append([text])
            self._in_paragraph = False

    def handle_data(self, data: str) -> None:
        if self._in_paragraph and not self._suppressed_tag:
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


def _expected_infobox_page_title(page_title: str) -> str:
    """Return the page title form that an article-level infobox title must match."""
    title = _clean_text(str(page_title or "").replace("_", " "))
    if not title:
        return ""
    previous = None
    while previous != title:
        previous = title
        title = re.sub(r"\s*\([^()]*\)", "", title)
        title = _clean_text(title)
    return title


def _infobox_title_key(text: str) -> str:
    """Return the exact-match key for infobox title comparison."""
    return unicodedata.normalize("NFKC", _clean_text(str(text or "").replace("_", " ")))


def _infobox_first_row_title_text(raw_rows: list[list[dict[str, Any]]]) -> str:
    """Return first-row title text when the row has one visible text value."""
    if not raw_rows:
        return ""
    visible_values = [
        _clean_text(str(cell.get("text", "") or ""))
        for cell in raw_rows[0]
        if _clean_text(str(cell.get("text", "") or ""))
    ]
    if len(visible_values) != 1:
        return ""
    return visible_values[0]


def _infobox_recognition(frame: dict[str, Any], *, page_title: str) -> dict[str, Any]:
    """Return audit metadata for article-level infobox recognition."""
    expected_title = _expected_infobox_page_title(page_title)
    expected_key = _infobox_title_key(expected_title)
    caption_text = _clean_text(str(frame.get("caption", "") or ""))
    first_row_text = _infobox_first_row_title_text(frame.get("rows", []))
    caption_matches = bool(expected_key and _infobox_title_key(caption_text) == expected_key)
    first_row_matches = bool(expected_key and _infobox_title_key(first_row_text) == expected_key)
    start_offset = _metadata_int(frame.get("start_offset"))
    at_page_start = start_offset >= 0 and start_offset <= INFOBOX_PAGE_START_MAX_CHAR_OFFSET
    title_source = ""
    matched_title_text = ""
    if caption_matches:
        title_source = "caption"
        matched_title_text = caption_text
    elif first_row_matches:
        title_source = "first_row"
        matched_title_text = first_row_text
    return {
        "expected_page_title": expected_title,
        "caption_text": caption_text,
        "first_row_text": first_row_text,
        "caption_matches_page_title": caption_matches,
        "first_row_matches_page_title": first_row_matches,
        "title_matches_page_title": bool(caption_matches or first_row_matches),
        "title_source": title_source,
        "matched_title_text": matched_title_text,
        "start_offset": start_offset,
        "start_line": _metadata_int(frame.get("start_line")),
        "start_column": _metadata_int(frame.get("start_column")),
        "page_start_max_char_offset": INFOBOX_PAGE_START_MAX_CHAR_OFFSET,
        "at_page_start": at_page_start,
    }


def _positive_cell_span(value: Any, *, default: int = 1) -> int:
    """Return a positive HTML table cell span."""
    try:
        parsed = int(str(value or "").strip())
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


class _WikipediaTableParser(HTMLParser):
    """Small HTML parser for Wikipedia infoboxes and wikitables."""

    def __init__(self, html: str = "") -> None:
        super().__init__(convert_charrefs=True)
        self._line_start_offsets = _line_start_offsets(html)
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
        self._active_row_class_text = ""
        self._active_row_style = ""
        self._active_cell: dict[str, Any] | None = None
        self._active_caption: list[str] | None = None
        self._suppressed_tag = ""

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style"}:
            self._suppressed_tag = tag
            return
        if self._suppressed_tag:
            return
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
            start_line, start_column = self.getpos()
            self._active_table = {
                "table_type": table_type,
                "class_text": class_text,
                "style": attr_map.get("style", ""),
                "start_offset": self._char_offset(start_line, start_column),
                "start_line": start_line,
                "start_column": start_column,
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
            self._active_row_class_text = attr_map.get("class", "")
            self._active_row_style = attr_map.get("style", "")
        elif tag in {"th", "td"} and self._active_row is not None:
            self._active_cell = {
                "text_parts": [],
                "header": tag == "th",
                "rowspan": _positive_cell_span(attr_map.get("rowspan", ""), default=1),
                "colspan": _positive_cell_span(attr_map.get("colspan", ""), default=1),
                "image_count": 0,
                "class_text": attr_map.get("class", ""),
                "style": attr_map.get("style", ""),
                "row_class_text": self._active_row_class_text,
                "row_style": self._active_row_style,
            }
        elif tag == "img" and self._active_cell is not None:
            self._active_cell["image_count"] = int(self._active_cell.get("image_count", 0) or 0) + 1

    def handle_startendtag(self, tag: str, attrs) -> None:
        if tag in {"script", "style"}:
            return
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        if tag == self._suppressed_tag:
            self._suppressed_tag = ""
            return
        if self._suppressed_tag:
            return
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
                        "class_text": str(self._active_cell.get("class_text", "") or ""),
                        "style": str(self._active_cell.get("style", "") or ""),
                        "row_class_text": str(self._active_cell.get("row_class_text", "") or ""),
                        "row_style": str(self._active_cell.get("row_style", "") or ""),
                    }
                )
            self._active_cell = None
        elif tag == "tr" and self._active_row is not None:
            if self._active_row:
                self._active_table["rows"].append(self._active_row)
            self._active_row = None
            self._active_row_class_text = ""
            self._active_row_style = ""
        elif tag == "caption" and self._active_caption is not None:
            self._active_table["caption"] = _clean_text(" ".join(self._active_caption))
            self._active_caption = None

    def handle_data(self, data: str) -> None:
        if self._suppressed_tag:
            return
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

    def _char_offset(self, line: int, column: int) -> int:
        """Return the absolute character offset for a parser line/column pair."""
        line_index = max(0, int(line) - 1)
        if line_index >= len(self._line_start_offsets):
            return -1
        return self._line_start_offsets[line_index] + max(0, int(column))


def _line_start_offsets(text: str) -> list[int]:
    """Return absolute offsets for every line start in a string."""
    offsets = [0]
    for match in re.finditer(r"\n", text):
        offsets.append(match.end())
    return offsets


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
            normalized = display_key(value)
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
    cleaned = display_cleanup(cleaned)
    return cleaned.replace("|", "\\|")


def _source_markdown_cell(value: str) -> str:
    """Escape a pre-gate table cell for GitHub-flavored Markdown."""
    cleaned = _clean_text(str(value).replace("\r", " ").replace("\n", " "))
    return cleaned.replace("|", "\\|")


def _grid_to_markdown(
    headers: list[str],
    data_rows: list[list[str]],
    *,
    final_cleanup: bool = False,
) -> str:
    """Render a rectangular grid as a GitHub-flavored Markdown table."""
    if not headers:
        return ""
    width = len(headers)
    cell_renderer = _markdown_cell if final_cleanup else _source_markdown_cell
    lines = [
        "| " + " | ".join(cell_renderer(header) for header in headers) + " |",
        "| " + " | ".join("---" for _ in range(width)) + " |",
    ]
    for row in data_rows:
        padded = [*row[:width], *([""] * max(0, width - len(row)))]
        lines.append("| " + " | ".join(cell_renderer(cell) for cell in padded[:width]) + " |")
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


def _non_image_full_width_heading_row_indexes(
    raw_rows: list[list[dict[str, Any]]],
    *,
    width: int,
) -> set[int]:
    """Return title/context rows that should not count toward infobox image density."""
    indexes: set[int] = set()
    for row in _full_width_heading_rows(raw_rows, width=width):
        row_index = int(row.get("row", -1))
        raw_row = raw_rows[row_index] if 0 <= row_index < len(raw_rows) else []
        if any(int(cell.get("image_count", 0) or 0) > 0 for cell in raw_row):
            continue
        indexes.add(row_index)
    return indexes


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


def _horizontal_layout_markers(frame: dict[str, Any]) -> list[str]:
    """Return HTML layout markers that indicate a table is horizontally arranged."""
    style = re.sub(r"\s+", "", str(frame.get("style", "") or "").casefold())
    markers: list[str] = []
    if "display:inline-table" in style:
        markers.append("display_inline_table")
    if "display:inline-block" in style:
        markers.append("display_inline_block")
    if "float:left" in style:
        markers.append("float_left")
    if "float:right" in style:
        markers.append("float_right")
    return markers


def _annotate_horizontal_companion_table_groups(tables: list[WikipediaTable]) -> None:
    """Annotate consecutive horizontally arranged table groups for later filtering."""

    def flush(group: list[WikipediaTable]) -> None:
        if len(group) < 2:
            return
        indexes = [table.table_index for table in group]
        for table in group:
            table.structure["horizontal_companion_group_size"] = len(group)
            table.structure["horizontal_companion_table_indexes"] = indexes

    group: list[WikipediaTable] = []
    group_key: tuple[str, str] | None = None
    for table in tables:
        structure = table.structure if isinstance(table.structure, dict) else {}
        markers = structure.get("horizontal_layout_markers", [])
        current_key = (table.section_heading, table.nearby_intro)
        if table.table_type == "wikitable" and markers:
            if group and current_key == group_key:
                group.append(table)
            else:
                flush(group)
                group = [table]
                group_key = current_key
            continue
        flush(group)
        group = []
        group_key = None
    flush(group)


def _raw_row_text(raw_row: list[dict[str, Any]]) -> str:
    """Return normalized text from one raw HTML table row."""
    return _clean_text(" ".join(str(cell.get("text", "") or "") for cell in raw_row))


def _raw_row_class_tokens(raw_row: list[dict[str, Any]]) -> set[str]:
    """Return normalized class tokens found on a raw row or its cells."""
    class_text = " ".join(
        " ".join(
            [
                str(cell.get("row_class_text", "") or ""),
                str(cell.get("class_text", "") or ""),
            ]
        )
        for cell in raw_row
    )
    return {token.strip().casefold() for token in re.split(r"\s+", class_text) if token.strip()}


def _raw_row_has_image(raw_row: list[dict[str, Any]]) -> bool:
    """Return whether one raw row contains an image-bearing cell."""
    return any(int(cell.get("image_count", 0) or 0) > 0 for cell in raw_row)


def _raw_row_is_full_width_context(raw_row: list[dict[str, Any]], *, width: int) -> bool:
    """Return whether one raw row is a single full-width contextual cell."""
    if width <= 0:
        return False
    non_empty_cells = [
        cell
        for cell in raw_row
        if str(cell.get("text", "") or "").strip() or int(cell.get("image_count", 0) or 0) > 0
    ]
    if len(non_empty_cells) != 1:
        return False
    colspan = _positive_cell_span(non_empty_cells[0].get("colspan", 1), default=1)
    return colspan >= width


def _image_context_row_indexes(
    raw_rows: list[list[dict[str, Any]]],
    grid: list[list[str]],
    *,
    header_row_count: int,
    width: int,
) -> tuple[set[int], set[int]]:
    """Return infobox media caption/title rows that should be removed with images."""
    image_row_indexes = {
        row_index
        for row_index, raw_row in enumerate(raw_rows)
        if _raw_row_has_image(raw_row)
    }
    key_value_row_indexes = {
        row_index
        for row_index, row in enumerate(grid)
        if row_index >= header_row_count and _is_key_value_text_row(row)
    }
    caption_row_indexes: set[int] = set()
    title_row_indexes: set[int] = set()
    for row_index, raw_row in enumerate(raw_rows):
        if row_index in image_row_indexes or row_index in key_value_row_indexes:
            continue
        if not _raw_row_is_full_width_context(raw_row, width=width):
            continue
        class_tokens = _raw_row_class_tokens(raw_row)
        if class_tokens.intersection(INFOBOX_MEDIA_CAPTION_CLASS_MARKERS):
            caption_row_indexes.add(row_index)
            continue
        normalized_text = _normalize_marker_text(_raw_row_text(raw_row))
        next_row_has_image = row_index + 1 in image_row_indexes
        previous_row_has_image = row_index - 1 in image_row_indexes
        if (
            next_row_has_image
            and class_tokens.intersection(INFOBOX_MEDIA_TITLE_CLASS_MARKERS)
            and normalized_text in INFOBOX_MEDIA_TITLE_TEXTS
        ):
            title_row_indexes.add(row_index)
            continue
        if previous_row_has_image and _looks_like_unclassed_media_caption(normalized_text):
            caption_row_indexes.add(row_index)
    return caption_row_indexes, title_row_indexes


def _looks_like_unclassed_media_caption(normalized_text: str) -> bool:
    """Return whether unclassed text is precise enough to treat as a media caption."""
    if not normalized_text:
        return False
    if normalized_text.startswith("interactive map of "):
        return True
    return False


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
    non_title_raw_cell_count = 0
    non_title_total_cell_coverage_count = 0
    non_title_image_raw_cell_count = 0
    non_title_image_covered_cell_count = 0
    image_row_indexes: set[int] = set()
    width = len(grid[0]) if grid else 0
    title_row_indexes = _non_image_full_width_heading_row_indexes(
        raw_rows,
        width=width,
    )
    image_caption_row_indexes, image_title_row_indexes = _image_context_row_indexes(
        raw_rows,
        grid,
        header_row_count=header_row_count,
        width=width,
    )
    for row_index, row in enumerate(raw_rows):
        for column_index, cell in enumerate(row):
            raw_cell_count += 1
            rowspan = _positive_cell_span(cell.get("rowspan", 1), default=1)
            colspan = _positive_cell_span(cell.get("colspan", 1), default=1)
            coverage = max(1, rowspan * colspan)
            total_cell_coverage_count += coverage
            if row_index not in title_row_indexes:
                non_title_raw_cell_count += 1
                non_title_total_cell_coverage_count += coverage
            if int(cell.get("image_count", 0) or 0) > 0:
                image_raw_cell_count += 1
                image_covered_cell_count += coverage
                for covered_row_index in range(row_index, min(len(raw_rows), row_index + rowspan)):
                    image_row_indexes.add(covered_row_index)
                if row_index not in title_row_indexes:
                    non_title_image_raw_cell_count += 1
                    non_title_image_covered_cell_count += coverage
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
        "html_class": str(frame.get("class_text", "")).strip(),
        "html_style": str(frame.get("style", "")).strip(),
        "horizontal_layout_markers": _horizontal_layout_markers(frame),
        "row_count": len(grid),
        "expanded_width": len(grid[0]) if grid else 0,
        "raw_row_cell_counts": raw_row_cell_counts,
        "header_row_count": header_row_count,
        "title_row_count": len(title_row_indexes),
        "title_row_indexes": sorted(title_row_indexes),
        "image_row_indexes": sorted(image_row_indexes),
        "non_title_image_row_indexes": sorted(
            row_index for row_index in image_row_indexes if row_index not in title_row_indexes
        ),
        "image_caption_row_indexes": sorted(image_caption_row_indexes),
        "image_title_row_indexes": sorted(image_title_row_indexes),
        "image_context_row_indexes": sorted(image_caption_row_indexes | image_title_row_indexes),
        "key_value_row_indexes": [
            row_index
            for row_index, row in enumerate(grid)
            if row_index >= header_row_count and _is_key_value_text_row(row)
        ],
        "non_title_row_count": max(0, len(raw_rows) - len(title_row_indexes)),
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
        "non_title_raw_cell_count": non_title_raw_cell_count,
        "non_title_total_cell_coverage_count": non_title_total_cell_coverage_count,
        "non_title_image_raw_cell_count": non_title_image_raw_cell_count,
        "non_title_image_covered_cell_count": non_title_image_covered_cell_count,
        "non_title_image_cell_rate": round(
            non_title_image_covered_cell_count / non_title_total_cell_coverage_count,
            4,
        )
        if non_title_total_cell_coverage_count
        else 0.0,
    }


def _build_wikipedia_table(table_index: int, frame: dict[str, Any], *, page_title: str = "") -> WikipediaTable:
    """Convert one parser frame into a table model."""
    table_type = str(frame.get("table_type", "")).strip()
    raw_rows = list(frame.get("rows", []))
    recognition = (
        dict(frame.get("infobox_recognition", {}))
        if isinstance(frame.get("infobox_recognition"), dict)
        else _infobox_recognition(frame, page_title=page_title)
    )
    caption = str(frame.get("caption", "")).strip()
    if table_type == "infobox" and recognition.get("title_source") == "first_row":
        caption = str(recognition.get("matched_title_text", "") or recognition.get("first_row_text", "")).strip()
        raw_rows = raw_rows[1:]
    grid, header_grid = _expand_table_grid(raw_rows)
    full_width_heading_rows = _full_width_heading_rows(raw_rows, width=len(grid[0]) if grid else 0)
    header_rows = _header_row_count(grid, header_grid)
    headers = _combined_markdown_headers(grid, header_rows)
    data_rows = grid[header_rows:] if header_rows else grid
    markdown = _grid_to_markdown(headers, data_rows)
    rows = data_rows
    structure = _table_structure_stats(raw_rows, grid, header_rows, frame)
    if full_width_heading_rows:
        structure["full_width_heading_row_count"] = len(full_width_heading_rows)
        structure["full_width_heading_rows"] = full_width_heading_rows[:20]
    normalized_parts = [
        str(frame.get("section_heading", "")).strip(),
        caption,
        markdown,
    ]
    if table_type == "infobox":
        structure["infobox_recognition"] = recognition
    return WikipediaTable(
        table_index=table_index,
        table_type=table_type,
        section_heading=str(frame.get("section_heading", "")).strip(),
        caption=caption,
        nearby_intro=str(frame.get("nearby_intro", "")).strip(),
        headers=headers,
        rows=rows,
        row_dicts=[],
        normalized_text="\n".join(part for part in normalized_parts if part),
        markdown=markdown,
        structure=structure,
    )


def _finalize_table_for_llm(table: WikipediaTable) -> WikipediaTable:
    """Return an LLM/evidence-facing copy after row filters have run."""
    headers = [display_cleanup(header) for header in table.headers]
    rows = [[display_cleanup(cell) for cell in row] for row in table.rows]
    section_heading = display_cleanup(table.section_heading)
    caption = display_cleanup(table.caption)
    nearby_intro = display_cleanup(table.nearby_intro)
    row_dicts = [
        {display_cleanup(key): display_cleanup(value) for key, value in row.items()}
        for row in table.row_dicts
    ]
    markdown = _grid_to_markdown(headers, rows, final_cleanup=True)
    normalized_parts = [section_heading, caption, markdown]
    return WikipediaTable(
        table_index=table.table_index,
        table_type=table.table_type,
        section_heading=section_heading,
        caption=caption,
        nearby_intro=nearby_intro,
        headers=headers,
        rows=rows,
        row_dicts=row_dicts,
        normalized_text="\n".join(part for part in normalized_parts if part),
        markdown=markdown,
        structure=dict(table.structure),
    )


def _route3_archive_record_metadata(
    page_archive: dict[str, Any],
    pageview_prefilter: dict[str, Any],
) -> dict[str, Any]:
    """Return per-record page archive metadata with pageview decision fields included."""
    metadata = dict(page_archive or {})
    if not isinstance(pageview_prefilter, dict) or not pageview_prefilter:
        return metadata
    metadata["pageview_decision"] = str(pageview_prefilter.get("decision", "") or "")
    metadata["pageview_status"] = str(pageview_prefilter.get("status", "") or "")
    pageview_payload = pageview_prefilter.get("pageview", {})
    if isinstance(pageview_payload, dict):
        metadata["pageview_fetch_status"] = str(pageview_payload.get("fetch_status", "") or "")
    return metadata


def _positive_route3_page_id(value: object) -> int | None:
    """Return a positive page ID from an archive/source value."""
    try:
        page_id = int(value)
    except (TypeError, ValueError):
        return None
    return page_id if page_id > 0 else None


def _resolved_route3_page_id(source_url: str, archive_metadata: dict[str, Any]) -> int | None:
    """Resolve a record page ID from a pageid URL or stored archive metadata."""
    page_id = normalize_wikipedia_page_id(source_url)
    if page_id is not None and page_id > 0:
        return page_id
    if isinstance(archive_metadata, dict):
        return _positive_route3_page_id(archive_metadata.get("page_id"))
    return None


def _source_metadata(
    *,
    page: WikipediaPageTables,
    tables: list[WikipediaTable],
    llm_response: dict[str, Any],
    llm_prompt: str,
    llm_audit: dict[str, Any] | None = None,
    source_table: WikipediaTable | None,
    table_selection: list[dict[str, Any]],
    timings: dict[str, float],
    answer_items: list[str] | None = None,
    answer_type: str = "",
    reasoning_type: str = "",
    tie_completion_warning: str = "",
    subject_anchors: dict[str, Any] | None = None,
    min_table_score: float = 0.0,
    allowed_reasoning_types: Iterable[str] | None = DEFAULT_ROUTE3_REASONING_TYPES,
    allowed_answer_types: Iterable[str] | None = None,
    extra_prompts: Iterable[str] | str | None = None,
    table_filter_modes: Iterable[str] | str | None = None,
    table_source_types: Iterable[str] | str | None = None,
    prose_leakage_scoring_enabled: bool = DEFAULT_ROUTE3_PROSE_LEAKAGE_SCORING_ENABLED,
    llm_choose_table: bool = False,
    page_archive: dict[str, Any] | None = None,
    pageview_prefilter: dict[str, Any] | None = None,
    answer_type_mode: str = DEFAULT_ROUTE3_ANSWER_TYPE_MODE,
    route3_slot_id: str = "",
) -> dict[str, Any]:
    """Build Route 3 audit metadata."""
    safe_subject_aliases = _first_paragraph_aliases(page.title, page.first_paragraph)
    normalized_allowed_reasoning_types = normalize_route3_reasoning_types(allowed_reasoning_types)
    normalized_allowed_answer_types = normalize_route3_answer_types(allowed_answer_types)
    normalized_extra_prompts = normalize_route3_extra_prompts(extra_prompts)
    normalized_table_filter_modes = normalize_route3_table_filter_modes(table_filter_modes)
    normalized_table_source_types = normalize_route3_table_source_types(table_source_types)
    archive_metadata = _route3_archive_record_metadata(
        page_archive or page.route3_page_archive or {},
        pageview_prefilter or page.pageview_prefilter or {},
    )
    page_id = _resolved_route3_page_id(page.source_url, archive_metadata)
    metadata = {
        "source_url": page.source_url,
        "page_id": page_id,
        "canonical_url": page.canonical_url,
        "page_title": page.title,
        "content_domain": page.content_domain,
        "first_paragraph": page.first_paragraph,
        "subject_anchor_aliases": _subject_anchor_options(
            page.title,
            page.first_paragraph,
            SUBJECT_ANCHOR_ALIAS_CUTOFF_YEAR,
        ),
        "safe_subject_aliases": safe_subject_aliases,
        "subject_anchors": subject_anchors or [],
        "min_table_score": float(min_table_score),
        "allowed_reasoning_types": list(normalized_allowed_reasoning_types),
        "allowed_answer_types": list(normalized_allowed_answer_types),
        "extra_prompts": list(normalized_extra_prompts),
        "table_filter_modes": list(normalized_table_filter_modes),
        "table_source_types": list(normalized_table_source_types),
        "prose_leakage_scoring_enabled": bool(prose_leakage_scoring_enabled),
        "llm_choose_table": bool(llm_choose_table),
        "answer_type_mode": normalize_route3_answer_type_mode(answer_type_mode),
        "route3_slot_id": route3_slot_id,
        "route3_page_archive": archive_metadata,
        "pageview_prefilter": dict(pageview_prefilter or page.pageview_prefilter or {}),
        "parsed_tables": [table.to_metadata() for table in tables],
        "table_selection": [_selection_payload(row) for row in table_selection],
        "selected_source_table": source_table.to_metadata() if source_table is not None else {},
        "llm_prompt": llm_prompt,
        "llm_response": llm_response,
        "small_model_qa_response": llm_response,
        "llm_audit": dict(llm_audit or {}),
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
        "route_validation_policy": "provenance_and_parsed_tables_stored_for_review",
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
    allowed_reasoning_types: Iterable[str] | None = DEFAULT_ROUTE3_REASONING_TYPES,
    allowed_answer_types: Iterable[str] | None = None,
    extra_prompts: Iterable[str] | str | None = None,
    table_filter_modes: Iterable[str] | str | None = None,
    table_source_types: Iterable[str] | str | None = None,
    prose_leakage_scoring_enabled: bool = DEFAULT_ROUTE3_PROSE_LEAKAGE_SCORING_ENABLED,
    page_archive: dict[str, Any] | None = None,
    pageview_prefilter: dict[str, Any] | None = None,
    llm_audit: dict[str, Any] | None = None,
    answer_type_mode: str = DEFAULT_ROUTE3_ANSWER_TYPE_MODE,
    route3_slot_id: str = "",
) -> GeneratedCandidate:
    """Build a placeholder candidate so shared output records route-local failures."""
    normalized_allowed_reasoning_types = normalize_route3_reasoning_types(allowed_reasoning_types)
    normalized_allowed_answer_types = normalize_route3_answer_types(allowed_answer_types)
    normalized_extra_prompts = normalize_route3_extra_prompts(extra_prompts)
    normalized_table_filter_modes = normalize_route3_table_filter_modes(table_filter_modes)
    normalized_table_source_types = normalize_route3_table_source_types(table_source_types)
    archive_metadata = _route3_archive_record_metadata(page_archive or {}, pageview_prefilter or {})
    page_id = _resolved_route3_page_id(url, archive_metadata)
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
            "page_id": page_id,
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
            "table_source_types": list(normalized_table_source_types),
            "prose_leakage_scoring_enabled": bool(prose_leakage_scoring_enabled),
            "answer_type_mode": normalize_route3_answer_type_mode(answer_type_mode),
            "route3_slot_id": route3_slot_id,
            "route3_page_archive": archive_metadata,
            "pageview_prefilter": dict(pageview_prefilter or {}),
            "parsed_tables": [table.to_metadata() for table in tables or []],
            "table_selection": [_selection_payload(row) for row in table_selection or []],
            "selected_source_table": source_table.to_metadata() if source_table is not None else {},
            "llm_prompt": llm_prompt,
            "llm_response": llm_response or {},
            "small_model_qa_response": llm_response or {},
            "llm_audit": dict(llm_audit or {}),
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
        "source_channel": row.get("source_channel", row.get("table_type", "")),
        "caption": row.get("caption"),
        "section_heading": row.get("section_heading"),
        "nearby_intro": row.get("nearby_intro", ""),
        "score": row.get("score"),
        "reasons": row.get("reasons", []),
        "row_count": row.get("row_count"),
        "data_row_count": row.get("data_row_count"),
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
        "infobox_row_filtering": row.get("infobox_row_filtering", {}),
        "min_table_score": row.get("min_table_score"),
        "below_min_table_score": bool(row.get("below_min_table_score", False)),
        "zero_numeric_rate": row.get("zero_numeric_rate"),
        "answer_type_score_bonus": row.get("answer_type_score_bonus", 0.0),
        "answer_type_score": row.get("answer_type_score", {}),
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
    blocked = [
        matcher
        for raw_value in [answer, *(answer_items or []), *answer_aliases]
        if (matcher := build_text_matcher(raw_value)) is not None
    ]
    queries = [
        query
        for query in _string_list(value)
        if not any(text_contains_match(query, matcher) for matcher in blocked)
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
        "external_links": "no_external_links_tables",
        "external_link": "no_external_links_tables",
        "no_external_links": "no_external_links_tables",
        "no_external_link": "no_external_links_tables",
        "horizontal": "no_horizontal_companion_tables",
        "horizontal_tables": "no_horizontal_companion_tables",
        "horizontal_companion": "no_horizontal_companion_tables",
        "horizontal_companion_tables": "no_horizontal_companion_tables",
        "side_by_side": "no_horizontal_companion_tables",
        "side_by_side_tables": "no_horizontal_companion_tables",
        "inline_tables": "no_horizontal_companion_tables",
        "floating_tables": "no_horizontal_companion_tables",
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


def _resolved_reasoning_type(response: dict[str, Any], allowed_reasoning_types: tuple[str, ...]) -> str:
    """Return the configured or model-selected Route 3 reasoning type."""
    fixed_reasoning_type = _fixed_reasoning_type(allowed_reasoning_types)
    if fixed_reasoning_type:
        return fixed_reasoning_type
    return _declared_reasoning_type(response) or _reasoning_type(response)


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
    checked_text = display_key(question)
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
    provided = {display_key(item) for item in provided_items if display_key(item)}
    expected = {display_key(item) for item in expected_items if display_key(item)}
    if expected and not expected.issubset(provided):
        missing = [item for item in expected_items if display_key(item) not in provided]
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
    normalized_question = display_key(question)
    looks_like_temporal_answer = _looks_like_temporal_answer(answer)
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


def _looks_like_temporal_answer(answer: str) -> bool:
    """Return whether an answer string looks like a date/year answer."""
    stripped = str(answer or "").strip()
    return (
        normalize_gate_date_answer(stripped) is not None
        or re.fullmatch(r"\d{4}(?:\s*\W+\s*\d{2,4})?", stripped) is not None
        or ERA_QUALIFIED_YEAR_PATTERN.fullmatch(stripped) is not None
    )


def _normalize_generated_answer(answer: Any, aliases: list[str]) -> tuple[str, list[str]]:
    """Return footnote-cleaned answer text and aliases without rewriting semantics."""
    answer_items = _answer_items(answer)
    if answer_items:
        cleaned_items = [_strip_footnote_markers(item) for item in answer_items]
        canonical_answer = "; ".join(item for item in cleaned_items if item)
        return canonical_answer, _dedupe_aliases(canonical_answer, aliases)
    canonical = _strip_footnote_markers(str(answer))
    return canonical, _dedupe_aliases(canonical, aliases)


def _dedupe_aliases(canonical: str, values: list[str]) -> list[str]:
    """Return aliases deduplicated against a canonical answer."""
    cleaned_aliases: list[str] = []
    seen = {_alias_dedupe_key(canonical)}
    for value in values:
        alias = _strip_footnote_markers(value)
        normalized = _alias_dedupe_key(alias)
        if not alias or not normalized or normalized in seen:
            continue
        seen.add(normalized)
        cleaned_aliases.append(alias)
    return cleaned_aliases


def _alias_dedupe_key(value: str) -> str:
    """Normalize aliases for exact duplicate removal without dropping parenthetical meaning."""
    return display_key(value)


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


def _strip_footnote_markers(value: str) -> str:
    """Remove common Wikipedia footnote symbols from a cell value."""
    cleaned = value.replace("‡", " ").replace("†", " ").replace("鈥?", " ")
    return display_cleanup(cleaned)


def _data_rows(table: WikipediaTable) -> list[list[str]]:
    """Return table data rows, tolerating legacy rows that stored headers first."""
    if table.headers and table.rows and table.rows[0] == table.headers:
        return table.rows[1:]
    return table.rows


def _prose_leakage_counts(table: WikipediaTable, prose: str) -> tuple[int, int]:
    """Count table row values that are visible in non-table article prose."""
    checked = 0
    leaked = 0
    for row in _data_rows(table):
        for cell in row:
            cleaned = source_display_cleanup(cell)
            if not _is_checkable_cell(cleaned):
                continue
            checked += 1
            if text_contains_match(prose, build_text_matcher(cleaned), cleanup=source_display_cleanup):
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
        key = display_key(cleaned)
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
    return source_display_cleanup(text)


def _clean_cell_text(text: str) -> str:
    """Normalize table cell text and remove Wikipedia reference markers."""
    return source_display_cleanup(text)


def _elapsed(start: float) -> float:
    """Return rounded elapsed seconds."""
    return round(perf_counter() - start, 4)
