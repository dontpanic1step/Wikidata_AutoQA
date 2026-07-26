"""Deterministic Route 3 quality rules shared by production gates and repair tools."""

from __future__ import annotations

import re

from .entity_normalization import normalize_name

EXTERNAL_LINKS_TABLE_FILTER_REASON = "no_external_links_tables:external_links_section"
AWARD_YEAR_WITHOUT_MONTH_REASON = "post_rewrite_award_year_without_month"
NO_SOCIAL_SCIENCE_RESEARCH_PROMPT = (
    "Ask factual questions, not questions about the findings or conclusions of social science research, "
    "such as results derived from census studies."
)

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
