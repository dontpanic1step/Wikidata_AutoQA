"""Date reference-answer normalization helpers."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

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

MONTH_ALIASES = {
    1: ("January", "Jan"),
    2: ("February", "Feb"),
    3: ("March", "Mar"),
    4: ("April", "Apr"),
    5: ("May",),
    6: ("June", "Jun"),
    7: ("July", "Jul"),
    8: ("August", "Aug"),
    9: ("September", "Sep", "Sept"),
    10: ("October", "Oct"),
    11: ("November", "Nov"),
    12: ("December", "Dec"),
}

MONTH_INDEX = {
    alias.lower(): month
    for month, aliases in MONTH_ALIASES.items()
    for alias in aliases
}

YEAR_ERA = r"(?P<sign>[+-]?)(?P<year>\d{1,4})(?:\s*(?P<era>bc|bce|ad|ce))?"
YEAR_ERA_ALT = r"(?P<year_sign>[+-]?)(?P<year>\d{1,4})(?:\s*(?P<era>bc|bce|ad|ce))?"
YEAR_ONLY_PATTERN = re.compile(rf"(?i)^{YEAR_ERA}$")
MDY_PATTERN = re.compile(
    rf"(?i)^(?P<month>[A-Za-z]+)\.?\s+(?P<day>\d{{1,2}})(?:st|nd|rd|th)?[,]?\s+{YEAR_ERA_ALT}$"
)
DMY_PATTERN = re.compile(
    rf"(?i)^(?P<day>\d{{1,2}})(?:st|nd|rd|th)?\s+(?P<month>[A-Za-z]+)\.?,?\s+{YEAR_ERA_ALT}$"
)
MONTH_YEAR_PATTERN = re.compile(rf"(?i)^(?P<month>[A-Za-z]+)\.?,?\s+{YEAR_ERA_ALT}$")
NUMERIC_YMD_PATTERN = re.compile(rf"(?i)^{YEAR_ERA_ALT}[-/](?P<month>\d{{1,2}})[-/](?P<day>\d{{1,2}})$")
NUMERIC_MDY_PATTERN = re.compile(
    rf"(?i)^(?P<month>\d{{1,2}})/(?P<day>\d{{1,2}})/{YEAR_ERA_ALT}$"
)
NUMERIC_YEAR_MONTH_PATTERN = re.compile(rf"(?i)^{YEAR_ERA_ALT}[-/](?P<month>\d{{1,2}})$")
NUMERIC_MONTH_YEAR_PATTERN = re.compile(rf"(?i)^(?P<month>\d{{1,2}})[-/]{YEAR_ERA_ALT}$")


@dataclass(frozen=True, slots=True)
class DateAnswerParts:
    """Parsed date answer components in the project's accepted date range."""

    year: int
    month: int | None = None
    day: int | None = None
    era: str = ""


def normalize_date_answer(answer: str, answer_type: str) -> str:
    """Return a canonical date answer string for Date answers when possible."""
    if answer_type != "Date":
        return answer
    text = " ".join(str(answer).strip().split())
    if not text:
        return text
    normalized = normalize_gate_date_answer(text)
    return normalized if normalized is not None else text


def normalize_gate_date_answer(answer: Any) -> str | None:
    """Return the accepted normalized date answer, or None for mismatch."""
    parts = parse_date_answer(answer)
    return format_date_answer(parts) if parts is not None else None


def parse_date_answer(answer: Any) -> DateAnswerParts | None:
    """Parse one accepted date answer without padding short years."""
    text = _clean_date_text(answer)
    if not text:
        return None
    year_only = YEAR_ONLY_PATTERN.fullmatch(text)
    if year_only:
        return _parts_from_match(year_only)
    for pattern in (MDY_PATTERN, DMY_PATTERN):
        match = pattern.fullmatch(text)
        if not match:
            continue
        parts = _parts_from_match(
            match,
            month=_month_number(match.group("month")),
            day=int(match.group("day")),
        )
        if parts is not None:
            return parts
    month_year = MONTH_YEAR_PATTERN.fullmatch(text)
    if month_year:
        return _parts_from_match(month_year, month=_month_number(month_year.group("month")))
    numeric_ymd = NUMERIC_YMD_PATTERN.fullmatch(text)
    if numeric_ymd:
        return _parts_from_match(
            numeric_ymd,
            month=int(numeric_ymd.group("month")),
            day=int(numeric_ymd.group("day")),
        )
    numeric_mdy = NUMERIC_MDY_PATTERN.fullmatch(text)
    if numeric_mdy:
        return _parts_from_match(
            numeric_mdy,
            month=int(numeric_mdy.group("month")),
            day=int(numeric_mdy.group("day")),
        )
    year_month = NUMERIC_YEAR_MONTH_PATTERN.fullmatch(text)
    if year_month:
        return _parts_from_match(year_month, month=int(year_month.group("month")))
    month_year_numeric = NUMERIC_MONTH_YEAR_PATTERN.fullmatch(text)
    if month_year_numeric:
        return _parts_from_match(
            month_year_numeric,
            month=int(month_year_numeric.group("month")),
        )
    return None


def format_date_answer(parts: DateAnswerParts) -> str:
    """Format parsed date parts in the accepted answer style."""
    if parts.month is None:
        return format_date_year(parts)
    if parts.day is None:
        return f"{MONTH_NAMES[parts.month]} {format_date_year(parts)}"
    return f"{MONTH_NAMES[parts.month]} {parts.day}, {format_date_year(parts)}"


def format_date_year(parts: DateAnswerParts) -> str:
    """Return a year string without zero-padding and with an optional era."""
    suffix = f" {parts.era}" if parts.era else ""
    return f"{parts.year}{suffix}"


def date_answer_sort_key(answer: Any) -> tuple[int, int, int] | None:
    """Return a comparable date key for cutoff checks, or None if unparsable."""
    parts = parse_date_answer(answer)
    if parts is None:
        return None
    signed_year = -parts.year if parts.era in {"BC", "BCE"} else parts.year
    return signed_year, parts.month or 1, parts.day or 1


def date_answer_variant_strings(answer: Any) -> set[str]:
    """Return raw date answer variants for search/evidence matching."""
    parts = parse_date_answer(answer)
    if parts is None:
        return set()
    variants = {format_date_answer(parts)}
    year_strings = _year_variant_strings(parts)
    if parts.month is None:
        variants.update(year_strings)
        return variants
    month_aliases = MONTH_ALIASES.get(parts.month, (MONTH_NAMES[parts.month],))
    if parts.day is None:
        for year_string in year_strings:
            for month_alias in month_aliases:
                variants.add(f"{month_alias} {year_string}")
                variants.add(f"{year_string} {month_alias}")
            _add_numeric_month_variants(variants, year_string, parts.month)
        return variants
    day_strings = {str(parts.day), f"{parts.day:02d}"}
    for year_string in year_strings:
        for month_alias in month_aliases:
            for day_string in day_strings:
                variants.add(f"{month_alias} {day_string} {year_string}")
                variants.add(f"{day_string} {month_alias} {year_string}")
        for day_string in day_strings:
            _add_numeric_day_variants(variants, year_string, parts.month, day_string)
    return variants


def _month_number(value: str) -> int | None:
    """Return a month number for one English month token."""
    return MONTH_INDEX.get(value.strip().lower().rstrip("."))


def _clean_date_text(answer: Any) -> str:
    """Return normalized whitespace for one possible date answer."""
    return re.sub(r"\s+", " ", str(answer or "").strip())


def _parts_from_match(
    match: re.Match[str],
    *,
    month: int | None = None,
    day: int | None = None,
) -> DateAnswerParts | None:
    """Build validated date parts from one regex match."""
    year = int(match.group("year"))
    sign = match.groupdict().get("sign") or match.groupdict().get("year_sign") or ""
    era = _normalize_era(match.groupdict().get("era") or "", sign)
    if not _valid_year(year):
        return None
    if month is not None and not _valid_month(month):
        return None
    if day is not None and (month is None or not _valid_day(year, month, day)):
        return None
    return DateAnswerParts(year=year, month=month, day=day, era=era)


def _normalize_era(era: str, sign: str) -> str:
    """Return the explicit era, or infer BC from a negative signed year."""
    if era:
        return era.upper()
    if sign == "-":
        return "BC"
    return ""


def _valid_year(year: int) -> bool:
    return 1 <= year <= 9999


def _valid_month(month: int) -> bool:
    return 1 <= month <= 12


def _valid_day(year: int, month: int, day: int) -> bool:
    if day < 1:
        return False
    days_by_month = {
        1: 31,
        2: 29 if _is_leap_year(year) else 28,
        3: 31,
        4: 30,
        5: 31,
        6: 30,
        7: 31,
        8: 31,
        9: 30,
        10: 31,
        11: 30,
        12: 31,
    }
    return day <= days_by_month.get(month, 0)


def _is_leap_year(year: int) -> bool:
    """Return Gregorian leap-year status for validation."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _year_variant_strings(parts: DateAnswerParts) -> list[str]:
    """Return year strings with conservative era aliases."""
    if parts.era in {"BC", "BCE"}:
        other = "BCE" if parts.era == "BC" else "BC"
        return [f"{parts.year} {parts.era}", f"{parts.year} {other}"]
    if parts.era in {"AD", "CE"}:
        other = "CE" if parts.era == "AD" else "AD"
        return [f"{parts.year} {parts.era}", f"{parts.year} {other}"]
    return [str(parts.year)]


def _add_numeric_month_variants(variants: set[str], year_string: str, month: int) -> None:
    """Add numeric year-month variants without padding the year."""
    for month_string in {str(month), f"{month:02d}"}:
        variants.add(f"{year_string} {month_string}")
        variants.add(f"{year_string}-{month_string}")
        variants.add(f"{month_string} {year_string}")
        variants.add(f"{month_string}-{year_string}")


def _add_numeric_day_variants(variants: set[str], year_string: str, month: int, day_string: str) -> None:
    """Add numeric full-date variants without padding the year."""
    for month_string in {str(month), f"{month:02d}"}:
        variants.add(f"{year_string} {month_string} {day_string}")
        variants.add(f"{year_string}-{month_string}-{day_string}")
        variants.add(f"{month_string} {day_string} {year_string}")
        variants.add(f"{month_string}/{day_string}/{year_string}")
