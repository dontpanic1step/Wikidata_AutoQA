"""Wikipedia infobox/table route for table-grounded QA generation."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
from time import perf_counter
from typing import Any

from .cheap_model_qa import parse_json_object
from .generation_models import EntityReference, EvidenceRecord, GeneratedCandidate
from .entity_normalization import normalize_name
from .date_reference import normalize_date_answer
from .number_reference import parse_number_token
from .wikipedia_client import WikipediaClient, normalize_wikipedia_page_id, normalize_wikipedia_title

ROUTE_NAME = "route3_wikipedia_infobox"
SOURCE_TYPE = "wikipedia_tables"
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
    "- If the answer is a full calendar date, ask `what day, month, and year ...` so the expected "
    "normalization is clear.\n"
    "- If the answer is a number, specify the counted quantity or unit in the question, such as gallons, "
    "people, months, authors, tracks, seats, or metres.\n"
    "- Do not add units to the reference answer or answer_aliases; keep numeric reference answers as "
    "normalized values only.\n"
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
            "row_dicts": self.row_dicts[:max_rows],
            "normalized_text": self.normalized_text[:max_text_chars],
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
                )
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
            )
        table_selection = rank_wikipedia_tables(
            page.tables,
            first_paragraph=page.first_paragraph,
            prose_text=page.prose_text,
        )
        table_selection = _annotate_table_score_cutoff(table_selection, self.min_table_score)
        safe_table_selection = [
            row
            for row in table_selection
            if not str(row.get("live_scope_rejection_reason", "")).strip()
            and not bool(row.get("below_min_table_score"))
        ]
        selected_tables = [
            row["table"]
            for row in safe_table_selection
            if isinstance(row.get("table"), WikipediaTable)
        ][:3]
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
                )
            if below_min_rows:
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
            table_selection=safe_table_selection,
            cutoff_year=cutoff_year,
            search_query_count=self.search_query_count,
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
            )

        answer, aliases = _normalize_generated_answer(
            answer_value,
            _string_list(response.get("answer_aliases", [])),
        )
        answer_type = _normalize_answer_type(response.get("answer_type"), answer, question)
        answer_items = _answer_items(answer_value)
        search_queries = _sanitize_answer_blind_queries(
            response.get("search_queries", []),
            answer=answer,
            answer_aliases=aliases,
            answer_items=answer_items,
            max_queries=self.search_query_count,
        )
        source_table_index = _coerce_table_index(response.get("source_table"))
        source_table = _table_by_index(selected_tables, source_table_index)
        reasoning_type = _reasoning_type(response)
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
) -> str:
    """Build the small-model prompt for Wikipedia table QA generation."""
    payload = {
        "title": title,
        "canonical_url": canonical_url,
        "first_paragraph": first_paragraph[:2500],
        "safe_subject_aliases": subject_anchors.get("safe_subject_aliases", []),
        "subject_anchors": subject_anchors,
        "table_selection_criteria": [
            "Prefer tables with many structured data rows.",
            "Prefer tables with numeric, ordinal, date, rank, count, or comparable value columns.",
            "Prefer tables whose row values are mostly not repeated in non-table prose, because these are less directly answerable from the article text.",
            "Prefer specific article tables over summary infoboxes when both are available.",
        ],
        "ranked_table_selection": [
            _selection_payload(row)
            for row in table_selection[:3]
        ],
        "tables": [table.to_metadata(max_rows=40, max_text_chars=2500) for table in tables[:3]],
    }
    return (
        "Generate one SimpleQA-style factual question from a Wikipedia infobox or table.\n"
        "Return JSON only.\n\n"
        "Requirements:\n"
        "- Use either a single fact lookup from the structured source or a table reasoning operation over rows or values: max, min, sum, count, comparison, or ordinal.\n"
        "- A single fact question is allowed when it asks for one stable value from an infobox or table and is likely to remain long-tail after search filtering.\n"
        "- The answer must be a stable entity/value from the provided table content, or a complete list when the reasoning operation has a tie.\n"
        "- If max/min/ordinal/count has tied answers, return answer as a JSON array containing every tied answer.\n"
        "- If a table cell has a parenthetical alias, put the plain entity name in answer and the parenthetical text in answer_aliases.\n"
        "- Choose from the top three ranked tables. Prefer rank 1 unless it cannot support a safe question.\n"
        "- Prefer a high-quality article table over an infobox when both support a safe, long-tail question.\n"
        "- Prefer table facts that are not easily found in article prose outside tables.\n"
        f"{ANSWER_PRECISION_PROMPT_RULES}"
        "- Use subject_anchors only to understand the page/table scope; do not copy anchor text mechanically into the question.\n"
        "- If the page title contains a cutoff-year marker, use one of safe_subject_aliases when you need to name the subject; do not use the cutoff-year title text.\n"
        "- Let the table caption, nearby paragraph intro, or nearby section heading define the safe scope. Pay special attention to nearby intros with words like `following` or `above`; they often state which rows are included or excluded. For example, `15 largest commercial banks` supports asking which bank is largest within that listed table, but not how many banks exist in Ukraine. A `1980 chart` table supports asking about facts in that 1980 chart, but not when a song first entered a chart because it may have entered in another year.\n"
        "- Treat curated list pages such as `List of national parks of the United States` as complete and authoritative for membership within their stated scope. Do not hedge by saying `according to the List of ...`.\n"
        "- Do not write `according to the table`, `according to the [source] table`, or `in the List of ...`. Name the actual entity, event, chart, list, or scope naturally. Only use `according to ...` when the source is a well-known named chart or list, such as a Billboard chart or UNESCO list.\n"
        "- Avoid questions with unclear or overly broad answer categories, such as `What equipment ...`. If the answer column is generic, name the domain-specific category in the question, such as telecommunications equipment category, award category, country of birth, or chart entry.\n"
        "- Do not ask cumulative-statistic questions such as how many goals Messi has scored, total wins, career points, revenue, downloads, citations, or followers unless the statistic is explicitly scoped to a historically settled slice, completed event, completed season, or fixed table/list.\n"
        "- Do not use generic phrases like `the listed table`, `the tournament`, or `the award` without naming the source subject.\n"
        "- Do not ask about current, latest, most recent, or live-status facts.\n"
        "- Avoid mutable-sounding wording such as `total assets`, `total number`, `current`, or `as of`.\n"
        "- For completed historical tables, phrase the comparison as a fixed result within the named event or list.\n"
        f"- Do not make the question text depend on events in {cutoff_year} or later.\n"
        "- Do not include the answer or answer aliases in the question or search queries.\n"
        f"- Generate exactly {search_query_count} answer-blind search queries.\n"
        "- If no safe single fact or table reasoning question is possible, set discard_reason and leave the other fields empty.\n\n"
        "Output schema:\n"
        "{\n"
        '  "question": string,\n'
        '  "answer": string | string[],\n'
        '  "answer_type": "Entity|Number|Date",\n'
        '  "answer_aliases": string[],\n'
        '  "search_queries": string[],\n'
        '  "reasoning_type": "single_fact|max|min|sum|count|comparison|ordinal|other",\n'
        '  "source_table": integer,\n'
        '  "derivation_summary": string,\n'
        '  "discard_reason": string | null\n'
        "}\n\n"
        f"Payload:\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )


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
        if table.table_type == "wikitable":
            score += 2.0
            reasons.append("article_table")
        if table.table_type == "infobox":
            score -= 2.0
            reasons.append("infobox_penalty")
        if row_count >= 3:
            score += min(row_count, 12) * 0.15
            reasons.append("multi_row")
        else:
            score -= 1.0
            reasons.append("too_few_rows")
        if table.headers:
            score += 1.0
            reasons.append("has_headers")
        if numeric_cell_count:
            score += min(numeric_cell_count, 20) * 0.1
            reasons.append("numeric_values")
        if comparable_header_hits:
            score += 3.0
            reasons.append("comparable_headers")
        else:
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
        if zero_numeric_rate >= 0.5 and numeric_cell_count >= 6:
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
            int(row["numeric_cell_count"]),
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


def _table_score_cutoff_discard_reason(rows: list[dict[str, Any]], min_table_score: float) -> str:
    """Return a concise rejection reason when no table meets the score cutoff."""
    best_score = max((_selection_score(row) for row in rows), default=0.0)
    return f"table_score_below_minimum:min_table_score={float(min_table_score):.4f};best_score={best_score:.4f}"


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
            self._active_cell = {"text_parts": [], "header": tag == "th"}

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
            text = _clean_text(" ".join(self._active_cell["text_parts"]))
            if text:
                self._active_row.append(
                    {
                        "text": text,
                        "header": bool(self._active_cell["header"]),
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


def _build_wikipedia_table(table_index: int, frame: dict[str, Any]) -> WikipediaTable:
    """Convert one parser frame into a table model."""
    raw_rows = frame.get("rows", [])
    rows = [[str(cell.get("text", "")).strip() for cell in row] for row in raw_rows]
    headers: list[str] = []
    row_dicts: list[dict[str, str]] = []
    if raw_rows and frame.get("table_type") == "infobox":
        for row in rows:
            if len(row) >= 2:
                row_dicts.append({row[0]: " | ".join(row[1:])})
    elif raw_rows:
        first_row = raw_rows[0]
        if first_row and all(bool(cell.get("header")) for cell in first_row):
            headers = [str(cell.get("text", "")).strip() for cell in first_row]
            for row in rows[1:]:
                if len(row) >= 2:
                    row_dicts.append(dict(zip(headers[: len(row)], row)))
    normalized_parts = [
        str(frame.get("section_heading", "")).strip(),
        str(frame.get("caption", "")).strip(),
    ]
    normalized_parts.extend(" | ".join(row) for row in rows)
    return WikipediaTable(
        table_index=table_index,
        table_type=str(frame.get("table_type", "")).strip(),
        section_heading=str(frame.get("section_heading", "")).strip(),
        caption=str(frame.get("caption", "")).strip(),
        nearby_intro=str(frame.get("nearby_intro", "")).strip(),
        headers=headers,
        rows=rows,
        row_dicts=row_dicts,
        normalized_text="\n".join(part for part in normalized_parts if part),
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
) -> dict[str, Any]:
    """Build Route 3 audit metadata."""
    safe_subject_aliases = _first_paragraph_aliases(page.title, page.first_paragraph)
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
) -> GeneratedCandidate:
    """Build a placeholder candidate so shared output records route-local failures."""
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
        relation_or_claim="wikipedia_table_fact",
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


def _reasoning_type(response: dict[str, Any]) -> str:
    """Return the normalized Route 3 reasoning type, accepting legacy composition_type."""
    raw_value = response.get("reasoning_type")
    if raw_value in {None, ""}:
        raw_value = response.get("composition_type")
    normalized = str(raw_value or "").strip().lower().replace("-", "_").replace(" ", "_")
    if normalized == "simple_fact":
        normalized = "single_fact"
    allowed = {
        "single_fact",
        "max",
        "min",
        "sum",
        "count",
        "comparison",
        "ordinal",
        "other",
    }
    return normalized if normalized in allowed else "single_fact"


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
        if current_value is not None and len(row) == 1:
            item = _strip_footnote_markers(row[0])
            if item:
                groups.setdefault(current_value, []).append(item)
                saw_continuation = True
    if not saw_continuation or not groups:
        return []
    target_value = max(groups) if reasoning_type == "max" else min(groups)
    return groups.get(target_value, [])


def _normalize_answer_type(value: Any, answer: str, question: str) -> str:
    """Return a supported answer type with conservative fallback inference."""
    normalized = str(value or "").strip()
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
    if normalized in {"Number", "Date"}:
        return normalized
    if normalized == "Entity":
        return normalized
    if parse_number_token(answer) is not None:
        return "Number"
    return "Entity"


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


def _elapsed(start: float) -> float:
    """Return rounded elapsed seconds."""
    return round(perf_counter() - start, 4)
