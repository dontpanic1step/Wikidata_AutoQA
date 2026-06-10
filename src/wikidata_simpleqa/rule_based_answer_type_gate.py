"""Rule-based answer-type gate for post-rewrite generated candidates."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from .generation_models import GeneratedCandidate

DEFAULT_LEXICON_DIR = Path("cache") / "rule_based_qa_gate"
GATED_ANSWER_TYPES = {"Date", "Person", "Place"}
BOOL_KEY = "rule_answer_type_match"
PERSON_COMMON_WORD_THRESHOLD = 0.5
PERSON_TOKEN_RE = re.compile(r"[^\W\d_][^\W\d_'.-]*")
PERSON_TITLE_SUFFIX_RE = re.compile(r"^(?P<prefix>.+?)\s+the\s+(?P<title>[^\W\d_][^\W\d_'.-]*)$")
PERSON_ROMAN_NUMERAL_SUFFIX_RE = re.compile(r"^(?P<prefix>.+?)\s+(?P<roman>[MDCLXVI]+)$")
ROMAN_NUMERAL_RE = re.compile(r"(?=[MDCLXVI]+\Z)M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})")
PERSON_MEDIAL_NAME_PARTICLES = {
    "abd",
    "abu",
    "af",
    "al",
    "ap",
    "bin",
    "bint",
    "de",
    "der",
    "di",
    "el",
    "ibn",
    "mac",
    "mc",
    "van",
    "von",
}
PERSON_PREFIX_NAME_PARTICLES = {
    "abd",
    "abu",
    "af",
    "al",
    "ap",
    "bin",
    "bint",
    "el",
    "ibn",
    "mac",
    "mc",
}
MONTH_NAMES = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}
MONTH_LABELS = {
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
    "province",
    "prison",
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
PLACE_CATEGORY_PATTERNS = (
    r"\bwhat is the name of the (?P<cat>[a-z][a-z -]{1,60}?)\s+(?:that|where|with|in|near|of|called|located)\b",
    r"\bwhat is the name of (?P<cat>the [a-z][a-z -]{1,60}?)\s+(?:that|where|with|in|near|of|called|located)\b",
    r"\bwhat is the (?P<cat>[a-z][a-z -]{1,60}?)\s+(?:where|that|with|in|near|of|called|located)\b",
    r"\bin which (?P<cat>[a-z][a-z -]{1,60}?)\s+(?:was|were|is|are|did|does|had|has|do|will|would|can)\b",
    r"\bin what (?P<cat>[a-z][a-z -]{1,60}?)\s+(?:was|were|is|are|did|does|had|has|do|will|would|can)\b",
    r"\bat which (?P<cat>[a-z][a-z -]{1,60}?)\s+(?:was|were|is|are|did|does|had|has|do|will|would|can)\b",
    r"\bat what (?P<cat>[a-z][a-z -]{1,60}?)\s+(?:was|were|is|are|did|does|had|has|do|will|would|can)\b",
    r"\bfrom which (?P<cat>[a-z][a-z -]{1,60}?)\s+(?:did|was|were|is|are|has|had|does)\b",
    r"\bfrom what (?P<cat>[a-z][a-z -]{1,60}?)\s+(?:did|was|were|is|are|has|had|does)\b",
    r"\bwhich (?P<cat>[a-z][a-z -]{1,60}?)\s+(?:was|were|is|are|did|does|has|had|do|will|would|can|extends)\b",
    r"\bwhat (?P<cat>[a-z][a-z -]{1,60}?)\s+(?:did|was|were|is|are|has|had|does)\b",
    r"\bname the (?P<cat>[a-z][a-z -]{1,60}?)\s+(?:in|of|near|where|that)\b",
)
CATEGORY_PREFIX_WORDS = {
    "american",
    "boston",
    "canadian",
    "english",
    "former",
    "first",
    "first public",
    "indian",
    "israeli",
    "ivy league",
    "largest",
    "mexican",
    "nassau county ny",
    "nebraska",
    "new jersey",
    "norwegian",
    "nyc",
    "only",
    "original",
    "paris",
    "rhode island",
    "second largest",
    "second-largest",
    "singapore",
    "small",
    "south american",
    "specific",
    "swiss",
    "the",
    "third-tallest",
    "tokyo",
    "two",
    "u s",
    "u.s.",
    "venezuelan",
    "vermont",
}
DERIVED_CATEGORY_HEADS = {
    "art school",
    "baseball field",
    "body of water",
    "capital city",
    "catholic church",
    "grammar school",
    "high school",
    "middle school",
    "parochial school",
    "peninsular plateau",
    "street address",
    "abbey",
    "airport",
    "area",
    "arrondissement",
    "borough",
    "building",
    "campus",
    "castle",
    "cave",
    "church",
    "city",
    "coast",
    "college",
    "country",
    "county",
    "district",
    "doab",
    "field",
    "fort",
    "garden",
    "geographic area",
    "geographic entity",
    "geographic location",
    "geographic region",
    "geographic section",
    "hospital",
    "hotel",
    "island",
    "kibbutz",
    "lake",
    "location",
    "mountain",
    "municipality",
    "observatory",
    "ocean",
    "palace",
    "place",
    "plateau",
    "province",
    "prison",
    "republic",
    "river",
    "school",
    "stadium",
    "state",
    "theater",
    "theater venue",
    "studio",
    "town",
    "track",
    "university",
    "venue",
    "village",
    "ward",
    "zoo",
}


@dataclass(frozen=True, slots=True)
class RuleBasedAnswerTypeGateResult:
    """Result from the post-rewrite answer-type gate."""

    matched: bool
    answer_type: str
    details: dict[str, Any]
    normalized_answer: str | None = None


def utc_now_iso() -> str:
    """Return a compact UTC timestamp for audit metadata."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_word_lines(text: str, *, max_words: int | None = None) -> set[str]:
    """Parse one word per line or frequency-list rows into a lowercase lexicon."""
    words: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        token = re.split(r"[\s,]+", stripped, maxsplit=1)[0].strip().lower()
        if re.fullmatch(r"[a-z][a-z'.-]*", token):
            words.add(token)
            if max_words is not None and len(words) >= max_words:
                break
    return words


@lru_cache(maxsize=1)
def load_cached_person_lexicons(lexicon_dir: str = str(DEFAULT_LEXICON_DIR)) -> tuple[set[str], set[str]]:
    """Load cached person gate lexicons without any network download."""
    root = Path(lexicon_dir)
    common_words = _load_word_file(
        root / "common_words_100k.txt",
        fallback={"the", "and", "of", "in", "a", "for", "to", "with", "on", "by", "from"},
        max_words=100000,
    )
    common_names: set[str] = set()
    common_names.update(
        _load_word_file(
            root / "common_names_1.txt",
            fallback={"jack", "john", "mary", "maria", "may"},
            max_words=None,
        )
    )
    common_names.update(
        _load_word_file(
            root / "common_names_2.txt",
            fallback={"robert", "william", "smith", "brown", "wilson"},
            max_words=None,
        )
    )
    return common_words, common_names


def _load_word_file(path: Path, *, fallback: set[str], max_words: int | None) -> set[str]:
    if not path.exists():
        return set(fallback)
    words = parse_word_lines(path.read_text(encoding="utf-8", errors="replace"), max_words=max_words)
    return words or set(fallback)


def answer_words(answer: Any) -> list[str]:
    """Return answer tokens used by the Person common-word gate."""
    tokens = [match.group(0).strip("'.-").lower() for match in PERSON_TOKEN_RE.finditer(str(answer or ""))]
    return [token for token in tokens if len(token) > 1]


def _person_name_particle_words(tokens: list[str]) -> list[str]:
    return [tokens[index] for index in sorted(_person_medial_name_particle_indexes(tokens))]


def _person_medial_name_particle_indexes(tokens: list[str]) -> set[int]:
    indexes = {
        index
        for index, token in enumerate(tokens)
        if (
            0 < index < len(tokens) - 1
            and token in PERSON_MEDIAL_NAME_PARTICLES
        )
        or (
            index == 0
            and len(tokens) > 1
            and token in PERSON_PREFIX_NAME_PARTICLES
        )
    }
    return indexes if 1 <= len(indexes) <= 2 else set()


def _person_marker_words(tokens: list[str], *, common_words: set[str], common_names: set[str]) -> list[str]:
    name_particle_indexes = _person_medial_name_particle_indexes(tokens)
    return [
        token
        for index, token in enumerate(tokens)
        if index not in name_particle_indexes
        and token in common_words
        and token not in common_names
    ]


def _valid_roman_numeral(text: str) -> bool:
    return bool(ROMAN_NUMERAL_RE.fullmatch(text))


def _capitalized_word(text: str) -> bool:
    stripped = text.strip("'.-")
    return bool(stripped) and stripped[0].isupper()


def _person_allowed_name_pattern(
    answer: Any,
    *,
    common_words: set[str],
    common_names: set[str],
) -> dict[str, Any] | None:
    text = re.sub(r"\s+", " ", str(answer or "").strip())
    title_match = PERSON_TITLE_SUFFIX_RE.fullmatch(text)
    if title_match and _capitalized_word(title_match.group("title")):
        prefix_tokens = answer_words(title_match.group("prefix"))
        prefix_markers = _person_marker_words(prefix_tokens, common_words=common_words, common_names=common_names)
        if prefix_tokens and not prefix_markers:
            return {
                "pattern": "name_prefix_the_capitalized_epithet",
                "prefix_words": prefix_tokens,
                "prefix_marker_words": prefix_markers,
                "ignored_suffix_words": ["the", title_match.group("title").lower()],
            }

    roman_match = PERSON_ROMAN_NUMERAL_SUFFIX_RE.fullmatch(text)
    if roman_match and _valid_roman_numeral(roman_match.group("roman")):
        prefix_tokens = answer_words(roman_match.group("prefix"))
        prefix_markers = _person_marker_words(prefix_tokens, common_words=common_words, common_names=common_names)
        if prefix_tokens and not prefix_markers:
            return {
                "pattern": "name_prefix_roman_numeral_suffix",
                "prefix_words": prefix_tokens,
                "prefix_marker_words": prefix_markers,
                "ignored_suffix_words": [roman_match.group("roman").lower()],
            }

    return None


def evaluate_person_gate(
    answer: Any,
    *,
    common_words: set[str],
    common_names: set[str],
    threshold: float = PERSON_COMMON_WORD_THRESHOLD,
) -> tuple[bool, dict[str, Any]]:
    """Return whether a Person answer looks name-like under the script gate."""
    tokens = [token for token in answer_words(answer) if token]
    name_particles = _person_name_particle_words(tokens)
    markers = _person_marker_words(tokens, common_words=common_words, common_names=common_names)
    ratio = (len(markers) / len(tokens)) if tokens else 0.0
    allowed_name_pattern = _person_allowed_name_pattern(
        answer,
        common_words=common_words,
        common_names=common_names,
    )
    if allowed_name_pattern is not None:
        return True, {
            "rule": "person_common_words_minus_common_names",
            "answer_words": tokens,
            "marker_words": markers,
            "name_particle_words": name_particles,
            "marker_ratio": round(ratio, 4),
            "threshold": threshold,
            "allowed_name_pattern": allowed_name_pattern,
            "reason": "Person answer matches a conservative monarch or epithet name pattern.",
        }
    matched = ratio < threshold
    return matched, {
        "rule": "person_common_words_minus_common_names",
        "answer_words": tokens,
        "marker_words": markers,
        "name_particle_words": name_particles,
        "marker_ratio": round(ratio, 4),
        "threshold": threshold,
        "reason": (
            "Person answer has too many common non-name words."
            if not matched
            else "Person answer is below the common non-name word threshold."
        ),
    }


def normalize_category(text: str) -> str:
    """Normalize a question-extracted Place category."""
    category = re.sub(r"[^a-z0-9 &.-]+", " ", text.lower()).strip()
    category = re.sub(r"\s+", " ", category)
    category = category.replace("u.s.", "u s")
    if category.startswith("are the names of the three stadiums"):
        return "stadium"
    changed = True
    while changed:
        changed = False
        for prefix in sorted(CATEGORY_PREFIX_WORDS, key=len, reverse=True):
            if category == prefix:
                return category
            if category.startswith(prefix + " "):
                category = category[len(prefix) + 1 :].strip()
                changed = True
                break
    if not category.startswith("body of water"):
        for separator in (" in ", " of ", " near ", " from ", " at "):
            if separator in category:
                head = category.split(separator, 1)[0].strip()
                if head:
                    category = head
                    break
    for head in sorted(DERIVED_CATEGORY_HEADS, key=len, reverse=True):
        if category == head or category.startswith(head + " ") or category.endswith(" " + head):
            category = head
            break
    if category in {"countries", "villages", "stadiums", "schools", "universities"}:
        category = {
            "countries": "country",
            "villages": "village",
            "stadiums": "stadium",
            "schools": "school",
            "universities": "university",
        }[category]
    return category


def extract_place_category(question: Any) -> str | None:
    """Extract the place-category head from a SimpleQA-style Place question."""
    text = str(question or "").lower()
    for pattern in PLACE_CATEGORY_PATTERNS:
        match = re.search(pattern, text)
        if not match:
            continue
        category = normalize_category(match.group("cat"))
        if category and category not in {"is", "was", "were", "are", "did", "does", "the", "name"}:
            return category
    return None


def load_simpleqa_place_categories(path: Path) -> set[str]:
    """Load extra Place category heads from a SimpleQA Verified-style JSON file."""
    data = json.loads(path.read_text(encoding="utf-8"))
    categories: set[str] = set()
    for record in data:
        if not isinstance(record, dict) or record.get("answer_type") != "Place":
            continue
        category = extract_place_category(record.get("question"))
        if category:
            categories.add(category)
    return categories


@lru_cache(maxsize=1)
def load_place_whitelist(simpleqa_verified_path: str = "") -> set[str]:
    """Return the Place category whitelist without requiring the script module."""
    whitelist = set(PLACE_SEED_WHITELIST)
    if simpleqa_verified_path:
        path = Path(simpleqa_verified_path)
        if path.exists():
            whitelist.update(load_simpleqa_place_categories(path))
    return whitelist


def evaluate_place_gate(question: Any, *, place_whitelist: set[str]) -> tuple[bool, dict[str, Any]]:
    """Return whether a Place question asks for a whitelisted place category."""
    category = extract_place_category(question)
    if category is None:
        return True, {
            "rule": "place_question_category_whitelist",
            "extracted_category": None,
            "reason": "No explicit place category was extracted; passing by default.",
        }
    matched = category in place_whitelist
    return matched, {
        "rule": "place_question_category_whitelist",
        "extracted_category": category,
        "whitelist_size": len(place_whitelist),
        "reason": (
            f"Extracted place category is whitelisted: {category}."
            if matched
            else f"Extracted category is not in the place whitelist: {category}."
        ),
    }


def _valid_year(year: int) -> bool:
    return 1 <= year <= 9999


def _valid_month(month: int) -> bool:
    return 1 <= month <= 12


def _valid_day(year: int, month: int, day: int) -> bool:
    if day < 1:
        return False
    days_by_month = {
        1: 31,
        2: 29 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 28,
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


def _format_year(year: int, era: str = "") -> str:
    suffix = f" {era.upper()}" if era else ""
    return f"{year}{suffix}"


def _format_full_date(year: int, month: int, day: int, era: str = "") -> str:
    return f"{MONTH_LABELS[month]} {day}, {_format_year(year, era)}"


def _format_month_year(year: int, month: int, era: str = "") -> str:
    return f"{MONTH_LABELS[month]} {_format_year(year, era)}"


def normalize_gate_date_answer(answer: Any) -> str | None:
    """Return the accepted normalized date answer, or None for mismatch."""
    text = str(answer or "").strip()
    if not text:
        return None
    text = re.sub(r"\s+", " ", text)
    year_only = re.fullmatch(r"(?i)(\d{1,4})(?:\s*(bc|bce|ad|ce))?", text)
    if year_only:
        year = int(year_only.group(1))
        era = year_only.group(2) or ""
        return _format_year(year, era) if _valid_year(year) else None
    month_names = "|".join(MONTH_NAMES)
    month_day_year = re.fullmatch(rf"(?i)({month_names})\s+(\d{{1,2}}),?\s+(\d{{1,4}})(?:\s*(bc|bce|ad|ce))?", text)
    if month_day_year:
        month = MONTH_NAMES[month_day_year.group(1).lower()]
        day = int(month_day_year.group(2))
        year = int(month_day_year.group(3))
        era = month_day_year.group(4) or ""
        return _format_full_date(year, month, day, era) if _valid_year(year) and _valid_day(year, month, day) else None
    day_month_year = re.fullmatch(rf"(?i)(\d{{1,2}})\s+({month_names})\s+(\d{{1,4}})(?:\s*(bc|bce|ad|ce))?", text)
    if day_month_year:
        day = int(day_month_year.group(1))
        month = MONTH_NAMES[day_month_year.group(2).lower()]
        year = int(day_month_year.group(3))
        era = day_month_year.group(4) or ""
        return _format_full_date(year, month, day, era) if _valid_year(year) and _valid_day(year, month, day) else None
    month_year = re.fullmatch(rf"(?i)({month_names}),?\s+(\d{{1,4}})(?:\s*(bc|bce|ad|ce))?", text)
    if month_year:
        month = MONTH_NAMES[month_year.group(1).lower()]
        year = int(month_year.group(2))
        era = month_year.group(3) or ""
        return _format_month_year(year, month, era) if _valid_year(year) else None
    iso_day = re.fullmatch(r"(\d{1,4})[-/](\d{1,2})[-/](\d{1,2})", text)
    if iso_day:
        year = int(iso_day.group(1))
        month = int(iso_day.group(2))
        day = int(iso_day.group(3))
        return (
            _format_full_date(year, month, day)
            if _valid_year(year) and _valid_month(month) and _valid_day(year, month, day)
            else None
        )
    us_day = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{1,4})", text)
    if us_day:
        month = int(us_day.group(1))
        day = int(us_day.group(2))
        year = int(us_day.group(3))
        return (
            _format_full_date(year, month, day)
            if _valid_year(year) and _valid_month(month) and _valid_day(year, month, day)
            else None
        )
    year_month = re.fullmatch(r"(\d{1,4})[-/](\d{1,2})", text)
    if year_month:
        year = int(year_month.group(1))
        month = int(year_month.group(2))
        return _format_month_year(year, month) if _valid_year(year) and _valid_month(month) else None
    month_year_numeric = re.fullmatch(r"(\d{1,2})[-/](\d{1,4})", text)
    if month_year_numeric:
        month = int(month_year_numeric.group(1))
        year = int(month_year_numeric.group(2))
        return _format_month_year(year, month) if _valid_year(year) and _valid_month(month) else None
    return None


def evaluate_date_gate(answer: Any) -> tuple[bool, dict[str, Any]]:
    """Return whether a Date answer is standard or normalizable."""
    original = str(answer or "").strip()
    normalized = normalize_gate_date_answer(original)
    matched = normalized is not None
    return matched, {
        "rule": "date_standard_or_normalizable_format",
        "original_answer": original,
        "normalized_answer": normalized,
        "reason": (
            "Date answer is standard or normalizable into the accepted date format."
            if matched
            else "Date answer is not an accepted standard or normalizable date format."
        ),
    }


def evaluate_candidate_answer_type_gate(candidate: GeneratedCandidate) -> RuleBasedAnswerTypeGateResult:
    """Evaluate a generated candidate after rewrite and before search long-tail."""
    answer_type = str(candidate.answer_type or "")
    if answer_type == "Date":
        matched, details = evaluate_date_gate(candidate.answer)
        return RuleBasedAnswerTypeGateResult(
            matched=matched,
            answer_type=answer_type,
            details=details,
            normalized_answer=details.get("normalized_answer") if matched else None,
        )
    if answer_type == "Person":
        common_words, common_names = load_cached_person_lexicons()
        matched, details = evaluate_person_gate(
            candidate.answer,
            common_words=common_words,
            common_names=common_names,
            threshold=PERSON_COMMON_WORD_THRESHOLD,
        )
        return RuleBasedAnswerTypeGateResult(matched=matched, answer_type=answer_type, details=details)
    if answer_type == "Place":
        matched, details = evaluate_place_gate(candidate.final_question, place_whitelist=load_place_whitelist())
        return RuleBasedAnswerTypeGateResult(matched=matched, answer_type=answer_type, details=details)
    return RuleBasedAnswerTypeGateResult(
        matched=True,
        answer_type=answer_type,
        details={
            "rule": "no_rule_for_answer_type",
            "reason": f"No rule-based gate is currently applied for answer_type={answer_type!r}.",
        },
    )


def attach_rule_based_gate_result(candidate: GeneratedCandidate, result: RuleBasedAnswerTypeGateResult) -> None:
    """Attach rule-gate metadata and normalize Date answers when applicable."""
    if result.normalized_answer:
        original_answer = candidate.answer
        candidate.answer = result.normalized_answer
        candidate.answer_entity.name = result.normalized_answer
        if original_answer and original_answer != result.normalized_answer and original_answer not in candidate.answer_aliases:
            candidate.answer_aliases.append(original_answer)
    candidate.source_metadata["rule_based_qa_gate"] = {
        "status": "matched" if result.matched else "mismatched",
        "answer_type": result.answer_type,
        "details": result.details,
        "created_at": utc_now_iso(),
    }
    candidate.source_metadata[BOOL_KEY] = result.matched
    if result.matched:
        return
    candidate.validation = {
        **(candidate.validation or {}),
        BOOL_KEY: False,
        "rule_based_qa_gate": candidate.source_metadata["rule_based_qa_gate"],
    }
