"""Conservative display cleanup and text matching helpers."""

from __future__ import annotations

import html
import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable

_WIKIPEDIA_REFERENCE_PATTERN = re.compile(
    r"\[\s*(?:\d+|[a-z]|note\s*\d+|notes?\s*\d+|nb\s*\d+|n\s*\d+)\s*\]",
    flags=re.IGNORECASE,
)
_WHITESPACE_PATTERN = re.compile(r"\s+")
_TOKEN_PATTERN = re.compile(r"[^\W_]+(?:['\u2019][^\W_]+)?", flags=re.UNICODE)
_CJK_RANGES = (
    (0x3400, 0x4DBF),
    (0x4E00, 0x9FFF),
    (0xF900, 0xFAFF),
    (0x3040, 0x30FF),
    (0xAC00, 0xD7AF),
)


@dataclass(frozen=True, slots=True)
class TextMatcher:
    """Layer 2 matcher for conservative answer/text containment checks."""

    phrase: str
    variants: frozenset[str]
    allow_substring: bool = False


def source_display_cleanup(value: object) -> str:
    """Return source text cleaned before gates while preserving bracketed notes."""
    text = html.unescape(str(value or ""))
    text = _WIKIPEDIA_REFERENCE_PATTERN.sub(" ", text)
    text = text.replace("\xa0", " ")
    text = text.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    text = _WHITESPACE_PATTERN.sub(" ", text).strip()
    return text


def display_cleanup(value: object) -> str:
    """Compatibility wrapper for retired display-only cleanup.

    New code should call source_display_cleanup directly. This wrapper no
    longer applies extra bracket stripping beyond source-display cleanup.
    """
    return source_display_cleanup(value)


def display_key(value: object) -> str:
    """Return a casefolded display key for exact de-duplication only."""
    return display_cleanup(value).casefold()


def build_text_matcher(value: object) -> TextMatcher | None:
    """Build a conservative Unicode-preserving text matcher."""
    phrase = display_cleanup(value)
    if not phrase:
        return None
    key = phrase.casefold()
    variants = {key}
    variants.update(_apostrophe_spacing_variants(key))
    variants.update(_inflection_variants(key))
    return TextMatcher(
        phrase=phrase,
        variants=frozenset(variant for variant in variants if variant),
        allow_substring=_allows_substring_match(phrase),
    )


def text_contains_match(
    text: object,
    matcher: TextMatcher | None,
    *,
    cleanup=display_cleanup,
) -> bool:
    """Return whether text contains a Layer 2 matcher."""
    if matcher is None:
        return False
    checked = cleanup(text).casefold()
    if not checked:
        return False
    if matcher.allow_substring:
        return any(variant in checked for variant in matcher.variants)
    checked_tokens = _tokens(checked)
    checked_token_text = " ".join(checked_tokens)
    if not checked_token_text:
        return False
    for variant in matcher.variants:
        variant_tokens = _tokens(variant)
        if not variant_tokens:
            continue
        if len(variant_tokens) == 1 and _unsafe_single_ascii_token(variant_tokens[0]):
            continue
        if _token_sequence_contains(checked_tokens, variant_tokens):
            return True
        if len(variant_tokens) > 1 and f" {' '.join(variant_tokens)} " in f" {checked_token_text} ":
            return True
    return False


def text_contains_any(text: object, values: Iterable[object]) -> bool:
    """Return whether text contains any Layer 2 value."""
    return any(text_contains_match(text, build_text_matcher(value)) for value in values)


def text_contains_all(text: object, values: Iterable[object]) -> bool:
    """Return whether text contains every non-empty Layer 2 value."""
    matchers = [matcher for value in values if (matcher := build_text_matcher(value)) is not None]
    return bool(matchers) and all(text_contains_match(text, matcher) for matcher in matchers)


def _tokens(value: str) -> list[str]:
    """Return Unicode word tokens with apostrophes treated as boundaries."""
    return [
        token
        for token in (
            part
            for match in _TOKEN_PATTERN.finditer(value)
            for part in re.split(r"['\u2019]+", match.group(0))
        )
        if token
    ]


def _token_sequence_contains(tokens: list[str], needle: list[str]) -> bool:
    """Return whether a token list contains a contiguous token sequence."""
    if not needle or len(needle) > len(tokens):
        return False
    width = len(needle)
    return any(tokens[index : index + width] == needle for index in range(len(tokens) - width + 1))


def _apostrophe_spacing_variants(value: str) -> set[str]:
    """Return variants that treat apostrophes as token boundaries."""
    variants: set[str] = set()
    for apostrophe in ("'", "\u2019"):
        if apostrophe in value:
            variants.add(value.replace(apostrophe, " "))
    return variants


def _inflection_variants(value: str) -> set[str]:
    """Return conservative English plural and simple tense variants."""
    tokens = value.split()
    if len(tokens) != 1:
        return set()
    token = tokens[0]
    if not token.isascii() or not token.isalpha() or len(token) < 4:
        return set()
    variants: set[str] = set()
    if token.endswith("ies") and len(token) > 4:
        variants.add(f"{token[:-3]}y")
    elif token.endswith("es") and len(token) > 4:
        variants.add(token[:-2])
    elif token.endswith("s") and len(token) > 3:
        variants.add(token[:-1])
    else:
        variants.add(f"{token}s")
        if token.endswith(("s", "x", "z", "ch", "sh")):
            variants.add(f"{token}es")
        if token.endswith("y") and len(token) > 1 and token[-2] not in "aeiou":
            variants.add(f"{token[:-1]}ies")
    if token.endswith("ed") and len(token) > 4:
        variants.add(token[:-2])
        if token.endswith("ied"):
            variants.add(f"{token[:-3]}y")
    elif token.endswith("ing") and len(token) > 5:
        variants.add(token[:-3])
    else:
        variants.add(f"{token}ed")
        variants.add(f"{token}ing")
    return variants


def _allows_substring_match(value: str) -> bool:
    """Return whether the answer is safer to match as a raw substring."""
    if _contains_cjk(value):
        return True
    non_ascii = sum(1 for char in value if ord(char) > 127)
    non_space = sum(1 for char in value if not char.isspace())
    if non_space and non_ascii / non_space >= 0.2:
        return True
    if len(value) == 1 and (ord(value) > 127 or not value.isalnum()):
        return True
    return False


def _contains_cjk(value: str) -> bool:
    """Return whether a string contains CJK-family characters."""
    for char in value:
        codepoint = ord(char)
        if any(start <= codepoint <= end for start, end in _CJK_RANGES):
            return True
    return False


def _unsafe_single_ascii_token(token: str) -> bool:
    """Return whether a single ASCII token is too short to match naked."""
    return token.isascii() and len(token) <= 1
