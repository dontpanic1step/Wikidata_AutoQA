"""Date reference-answer normalization helpers."""

from __future__ import annotations

from datetime import date
import re

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

MONTH_INDEX = {
    "january": 1,
    "jan": 1,
    "february": 2,
    "feb": 2,
    "march": 3,
    "mar": 3,
    "april": 4,
    "apr": 4,
    "may": 5,
    "june": 6,
    "jun": 6,
    "july": 7,
    "jul": 7,
    "august": 8,
    "aug": 8,
    "september": 9,
    "sep": 9,
    "sept": 9,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,
}

ISO_DATE_PATTERN = re.compile(r"^(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})$")
YMD_SLASH_PATTERN = re.compile(r"^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})$")
MDY_SLASH_PATTERN = re.compile(r"^(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<year>\d{4})$")
ISO_MONTH_PATTERN = re.compile(r"^(?P<year>\d{4})-(?P<month>\d{2})$")
YEAR_PATTERN = re.compile(r"^\d{4}$")
YEAR_RANGE_PATTERN = re.compile(r"^(?P<start>\d{4})\s*[-–—/]\s*(?P<end>\d{2,4})$")
MDY_PATTERN = re.compile(
    r"^(?P<month>[A-Za-z]+)\.?\s+(?P<day>\d{1,2})(?:st|nd|rd|th)?[,]?\s+(?P<year>\d{4})$"
)
DMY_PATTERN = re.compile(
    r"^(?P<day>\d{1,2})(?:st|nd|rd|th)?\s+(?P<month>[A-Za-z]+)\.?,?\s+(?P<year>\d{4})$"
)
MONTH_YEAR_PATTERN = re.compile(r"^(?P<month>[A-Za-z]+)\.?\s+(?P<year>\d{4})$")


def normalize_date_answer(answer: str, answer_type: str) -> str:
    """Return a canonical date answer string for Date answers when possible."""
    if answer_type != "Date":
        return answer
    text = " ".join(str(answer).strip().split())
    if not text:
        return text
    if YEAR_PATTERN.fullmatch(text):
        return text
    year_range = _normalize_year_range(text)
    if year_range is not None:
        return year_range
    iso_date = _normalize_iso_date(text)
    if iso_date is not None:
        return iso_date
    slash_date = _normalize_slash_date(text)
    if slash_date is not None:
        return slash_date
    iso_month = _normalize_iso_month(text)
    if iso_month is not None:
        return iso_month
    for pattern in (MDY_PATTERN, DMY_PATTERN):
        match = pattern.fullmatch(text)
        if not match:
            continue
        normalized = _format_date(
            int(match.group("year")),
            _month_number(match.group("month")),
            int(match.group("day")),
        )
        if normalized is not None:
            return normalized
    month_year = MONTH_YEAR_PATTERN.fullmatch(text)
    if month_year:
        month = _month_number(month_year.group("month"))
        if month is not None:
            return f"{int(month_year.group('year')):04d}-{month:02d}"
    return text


def _normalize_year_range(text: str) -> str | None:
    """Return a canonical year range such as 2014-2015 when possible."""
    match = YEAR_RANGE_PATTERN.fullmatch(text)
    if not match:
        return None
    start = int(match.group("start"))
    end_text = match.group("end")
    if len(end_text) == 2:
        century = start // 100 * 100
        end = century + int(end_text)
        if end < start:
            end += 100
    else:
        end = int(end_text)
    if end < start:
        return None
    return f"{start:04d}-{end:04d}"


def _normalize_iso_date(text: str) -> str | None:
    """Return a valid full-date reference answer or None."""
    match = ISO_DATE_PATTERN.fullmatch(text)
    if not match:
        return None
    return _format_date(
        int(match.group("year")),
        int(match.group("month")),
        int(match.group("day")),
    )


def _normalize_slash_date(text: str) -> str | None:
    """Return a valid slash-date reference answer or None."""
    for pattern in (YMD_SLASH_PATTERN, MDY_SLASH_PATTERN):
        match = pattern.fullmatch(text)
        if not match:
            continue
        normalized = _format_date(
            int(match.group("year")),
            int(match.group("month")),
            int(match.group("day")),
        )
        if normalized is not None:
            return normalized
    return None


def _normalize_iso_month(text: str) -> str | None:
    """Return a valid ISO year-month or None."""
    match = ISO_MONTH_PATTERN.fullmatch(text)
    if not match:
        return None
    year = int(match.group("year"))
    month = int(match.group("month"))
    if not 1 <= month <= 12:
        return None
    return f"{year:04d}-{month:02d}"


def _format_date(year: int, month: int | None, day: int) -> str | None:
    """Return `Month D, YYYY` if the parts form a real date."""
    if month is None:
        return None
    try:
        parsed = date(year, month, day)
    except ValueError:
        return None
    return f"{MONTH_NAMES[parsed.month]} {parsed.day}, {parsed.year}"


def _month_number(value: str) -> int | None:
    """Return a month number for one English month token."""
    return MONTH_INDEX.get(value.strip().lower().rstrip("."))
