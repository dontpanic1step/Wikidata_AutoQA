"""Deterministic Route 3 quality rules shared by production gates and repair tools."""

from __future__ import annotations

import re

from .entity_normalization import normalize_name

EXTERNAL_LINKS_TABLE_FILTER_REASON = "no_external_links_tables:external_links_section"
AWARD_YEAR_WITHOUT_MONTH_REASON = "post_rewrite_award_year_without_month"
OVERSIZED_TABLE_ROW_REASON = "no_oversized_tables:row_count_gt_40"
OVERSIZED_TABLE_TEXT_REASON = "no_oversized_tables:markdown_chars_gt_2500"

_AWARD_PATTERN = re.compile(r"\bawards?\b", flags=re.IGNORECASE)
_WHAT_OR_WHICH_YEAR_PATTERN = re.compile(
    r"\b(?:in\s+)?(?:what|which)\s+year\b",
    flags=re.IGNORECASE,
)
_MONTH_PATTERN = re.compile(r"\bmonth\b", flags=re.IGNORECASE)


def external_links_table_filter_reason(section_heading: object) -> str:
    """Return a table-filter reason when a table belongs to the External links section."""
    normalized = normalize_name(str(section_heading or ""))
    if normalized in {"external link", "external links"}:
        return EXTERNAL_LINKS_TABLE_FILTER_REASON
    return ""


def award_year_without_month_question_reason(question: object) -> str:
    """Return a post-rewrite rejection reason for ambiguous award-year questions."""
    text = str(question or "")
    if not text.strip():
        return ""
    if not _AWARD_PATTERN.search(text):
        return ""
    if not _WHAT_OR_WHICH_YEAR_PATTERN.search(text):
        return ""
    if _MONTH_PATTERN.search(text):
        return ""
    return AWARD_YEAR_WITHOUT_MONTH_REASON


def oversized_table_filter_reasons(
    table: dict[str, object],
    *,
    max_rows: int = 40,
    max_markdown_chars: int = 2500,
) -> list[str]:
    """Return table-size rejection labels matching Route 3 extraction limits."""
    reasons: list[str] = []
    rows = table.get("rows")
    if isinstance(rows, list) and len(rows) > max_rows:
        reasons.append(OVERSIZED_TABLE_ROW_REASON)
    markdown = str(table.get("markdown") or table.get("normalized_text") or "")
    if len(markdown) > max_markdown_chars:
        reasons.append(OVERSIZED_TABLE_TEXT_REASON)
    return reasons
