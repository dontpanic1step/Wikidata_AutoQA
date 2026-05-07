"""Helpers for Wikidata-backed date answers."""

from __future__ import annotations

from datetime import date

MONTH_NAMES = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}


def normalize_wikidata_date_literal(value: str) -> str:
    """Normalize a Wikidata date literal to ISO day precision."""
    return value[:10]


def format_iso_date_for_answer(value: str) -> str:
    """Format an ISO date as `22 January 1988`."""
    parsed = date.fromisoformat(normalize_wikidata_date_literal(value))
    return f"{parsed.day} {MONTH_NAMES[parsed.month]} {parsed.year}"
