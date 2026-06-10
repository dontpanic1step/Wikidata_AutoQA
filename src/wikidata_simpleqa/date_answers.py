"""Helpers for Wikidata-backed date answers."""

from __future__ import annotations

import re

from .date_reference import normalize_gate_date_answer

WIKIDATA_DATE_LITERAL_PATTERN = re.compile(
    r"^(?P<sign>[+-]?)(?P<year>\d+)(?:-(?P<month>\d{1,2})(?:-(?P<day>\d{1,2}))?)?"
)


def normalize_wikidata_date_literal(value: str) -> str:
    """Normalize a Wikidata date literal without padding the year."""
    date_text = str(value or "").strip().split("T", 1)[0]
    match = WIKIDATA_DATE_LITERAL_PATTERN.fullmatch(date_text)
    if not match:
        return date_text.lstrip("+")[:10]
    year = int(match.group("year"))
    signed_year = f"-{year}" if match.group("sign") == "-" else str(year)
    month_text = match.group("month")
    day_text = match.group("day")
    if not month_text or int(month_text) == 0:
        return signed_year
    month = int(month_text)
    if not day_text or int(day_text) == 0:
        return f"{signed_year}-{month:02d}"
    return f"{signed_year}-{month:02d}-{int(day_text):02d}"


def format_iso_date_for_answer(value: str) -> str:
    """Format an ISO-like date as `January 22, 1988`."""
    normalized = normalize_wikidata_date_literal(value)
    answer = normalize_gate_date_answer(normalized)
    if answer is None:
        raise ValueError(f"Invalid date literal: {value!r}")
    return answer
