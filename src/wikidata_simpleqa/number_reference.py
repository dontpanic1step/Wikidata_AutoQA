"""Numeric reference-answer margin helpers for SimpleQA Verified-style grading."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re
from typing import Any

NUMBER_REFERENCE_MARGIN_KEY = "number_reference_margin"

_NUMBER_TOKEN_PATTERN = re.compile(
    r"(?<![\w.])-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?!\w|\.\d)"
)
_SCALED_NUMBER_TOKEN_PATTERN = re.compile(
    r"(?<![\w.])(?P<number>-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)\s+"
    r"(?P<scale>hundred|thousand|million|billion)\b",
    flags=re.IGNORECASE,
)
_UNIT_ATTACHED_NUMBER_FALLBACK_PATTERN = re.compile(
    r"(?<![\w.])(?P<number>-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)(?=[A-Za-z%°²³/])"
)
_WORD_TOKEN_PATTERN = re.compile(r"[a-z]+")
_SMALL_NUMBER_WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
}
_TENS_NUMBER_WORDS = {
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
}
_SCALE_NUMBER_WORDS = {
    "hundred": 100,
    "thousand": 1_000,
    "million": 1_000_000,
    "billion": 1_000_000_000,
}
_NUMBER_WORD_VOCABULARY = (
    set(_SMALL_NUMBER_WORDS)
    | set(_TENS_NUMBER_WORDS)
    | set(_SCALE_NUMBER_WORDS)
    | {"and", "minus", "negative"}
)


def build_number_reference_margin(answer: str, answer_type: str) -> dict[str, Any]:
    """Build an auditable numeric tolerance range for Number answer templates."""
    if answer_type != "Number":
        return {
            "enabled": False,
            "reason": "non_number_answer_type",
        }
    value = parse_number_token(answer)
    if value is None:
        return {
            "enabled": False,
            "reason": "unparseable_number_answer",
            "original_answer": answer,
        }
    is_integer = value == value.to_integral_value()
    normalized_answer = format_decimal(value)
    margin = _default_margin(value, is_integer=is_integer)
    lower_bound = value - margin
    upper_bound = value + margin
    reference_answer = (
        f"{normalized_answer} (acceptable range: anything between "
        f"{format_decimal(lower_bound)} and {format_decimal(upper_bound)})"
    )
    return {
        "enabled": True,
        "reason": "simpleqa_verified_number_margin",
        "original_answer": answer,
        "numeric_value": format_decimal(value),
        "lower_bound": format_decimal(lower_bound),
        "upper_bound": format_decimal(upper_bound),
        "margin": format_decimal(margin),
        "margin_kind": "max_one_absolute_or_one_percent",
        "reference_answer": reference_answer,
    }


def normalize_number_answer(answer: str, answer_type: str) -> str:
    """Return a canonical numeric answer string for Number templates."""
    if answer_type != "Number":
        return answer
    value = parse_number_token(answer)
    if value is None:
        return answer.strip()
    return format_decimal(value)


def reference_answer_for_grading(gold_answer: str, source_metadata: dict[str, Any] | None) -> str:
    """Return the reference answer text supplied to an LLM grader."""
    margin = get_number_reference_margin(source_metadata)
    if margin is None:
        return gold_answer
    return str(margin.get("reference_answer") or gold_answer)


def prediction_within_number_margin(
    predicted_answer: str,
    source_metadata: dict[str, Any] | None,
) -> bool:
    """Return whether the prediction contains a number inside the reference range."""
    return bool(number_margin_hits(predicted_answer, source_metadata))


def number_margin_hits(text: str, source_metadata: dict[str, Any] | None) -> list[str]:
    """Return formatted number mentions in text that fall inside the reference range."""
    margin = get_number_reference_margin(source_metadata)
    if margin is None:
        return []
    lower = parse_number_token(str(margin.get("lower_bound", "")))
    upper = parse_number_token(str(margin.get("upper_bound", "")))
    if lower is None or upper is None:
        return []
    hits: list[str] = []
    seen: set[str] = set()
    for value in extract_number_mentions(text):
        if lower <= value <= upper:
            formatted = format_decimal(value)
            if formatted in seen:
                continue
            seen.add(formatted)
            hits.append(formatted)
    return hits


def extract_number_mentions(text: str) -> list[Decimal]:
    """Extract cheap Arabic-number and English-number mentions from free text."""
    values: list[Decimal] = []
    seen: set[str] = set()
    for token in _NUMBER_TOKEN_PATTERN.findall(text):
        value = parse_number_token(token)
        if value is None:
            continue
        formatted = format_decimal(value)
        if formatted not in seen:
            seen.add(formatted)
            values.append(value)

    tokens = _WORD_TOKEN_PATTERN.findall(text.lower().replace("-", " "))
    index = 0
    while index < len(tokens):
        value, end_index = _parse_number_words(tokens, index)
        if value is None:
            index += 1
            continue
        formatted = format_decimal(value)
        if formatted not in seen:
            seen.add(formatted)
            values.append(value)
        index = end_index
    return values


def get_number_reference_margin(source_metadata: dict[str, Any] | None) -> dict[str, Any] | None:
    """Return enabled number-reference metadata when present."""
    if not source_metadata:
        return None
    margin = source_metadata.get(NUMBER_REFERENCE_MARGIN_KEY)
    if not isinstance(margin, dict) or not margin.get("enabled"):
        return None
    return margin


def parse_number_token(value: str) -> Decimal | None:
    """Parse the first Arabic-number token or exact English-number phrase in a string."""
    stripped = value.strip()
    scaled_match = _SCALED_NUMBER_TOKEN_PATTERN.search(stripped)
    if scaled_match is not None:
        parsed = _parse_decimal_number(scaled_match.group("number"))
        if parsed is not None:
            return parsed * Decimal(_SCALE_NUMBER_WORDS[scaled_match.group("scale").lower()])

    match = _NUMBER_TOKEN_PATTERN.search(stripped)
    if match is not None:
        return _parse_decimal_number(match.group(0))

    fallback_match = _UNIT_ATTACHED_NUMBER_FALLBACK_PATTERN.search(stripped)
    if fallback_match is not None:
        return _parse_decimal_number(fallback_match.group("number"))

    tokens = _WORD_TOKEN_PATTERN.findall(value.lower().replace("-", " "))
    parsed, end_index = _parse_number_words(tokens, 0)
    if parsed is None or end_index != len(tokens):
        return None
    return parsed


def _parse_decimal_number(value: str) -> Decimal | None:
    """Parse one decimal-like token after stripping comma group separators."""
    compact = value.replace(",", "")
    try:
        return Decimal(compact)
    except InvalidOperation:
        return None


def format_decimal(value: Decimal) -> str:
    """Format Decimal values without scientific notation or unnecessary zeros."""
    if value == value.to_integral_value():
        return str(value.quantize(Decimal("1")))
    text = format(value.normalize(), "f")
    return text.rstrip("0").rstrip(".")


def _default_margin(value: Decimal, *, is_integer: bool) -> Decimal:
    """Return a conservative default tolerance for generated Number templates."""
    one_percent = (abs(value) * Decimal("0.01"))
    if is_integer:
        rounded = one_percent.to_integral_value(rounding=ROUND_HALF_UP)
        return max(Decimal("1"), rounded)
    return max(Decimal("0.01"), one_percent)


def _parse_number_words(tokens: list[str], start: int) -> tuple[Decimal | None, int]:
    """Parse a contiguous English-number phrase beginning at start."""
    if start >= len(tokens) or tokens[start] not in _NUMBER_WORD_VOCABULARY:
        return None, start
    sign = 1
    index = start
    if tokens[index] in {"minus", "negative"}:
        sign = -1
        index += 1
        if index >= len(tokens):
            return None, start

    total = 0
    current = 0
    consumed_value = False
    last_was_scale = False
    while index < len(tokens):
        token = tokens[index]
        if token == "and":
            if not consumed_value:
                break
            index += 1
            continue
        if token in _SMALL_NUMBER_WORDS:
            current += _SMALL_NUMBER_WORDS[token]
            consumed_value = True
            last_was_scale = False
            index += 1
            continue
        if token in _TENS_NUMBER_WORDS:
            current += _TENS_NUMBER_WORDS[token]
            consumed_value = True
            last_was_scale = False
            index += 1
            continue
        if token == "hundred":
            if current == 0:
                break
            current *= _SCALE_NUMBER_WORDS[token]
            consumed_value = True
            last_was_scale = True
            index += 1
            continue
        if token in {"thousand", "million", "billion"}:
            scale = _SCALE_NUMBER_WORDS[token]
            total += (current or 1) * scale
            current = 0
            consumed_value = True
            last_was_scale = True
            index += 1
            continue
        break

    if not consumed_value:
        return None, start
    if last_was_scale and index < len(tokens) and tokens[index] in _NUMBER_WORD_VOCABULARY:
        return None, start
    return Decimal(sign * (total + current)), index
