"""Rule-based answer-type gate for post-rewrite generated candidates."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from .date_reference import normalize_gate_date_answer
from .generation_models import GeneratedCandidate

BOOL_KEY = "rule_answer_type_match"
PLACE_SEED_WHITELIST = {
    "abbey",
    "airport",
    "area",
    "arena",
    "arrondissement",
    "borough",
    "biosphere reserve",
    "building",
    "campus",
    "capital city",
    "castle",
    "cave",
    "cemetery",
    "church",
    "city",
    "city and country",
    "city and province",
    "city and state",
    "coast",
    "college",
    "country",
    "county",
    "depot",
    "district",
    "doab",
    "duchy",
    "dukedom",
    "exhibition centre",
    "field",
    "fort",
    "garden",
    "geographic area",
    "geographic entity",
    "geographic location",
    "geographic region",
    "geographic section",
    "grammar school",
    "harbor",
    "high school",
    "highest peak",
    "historical hundred",
    "hospital",
    "hotel",
    "island",
    "kibbutz",
    "kingdom",
    "lake",
    "launch pad",
    "location",
    "middle school",
    "mountain",
    "municipality",
    "national park",
    "observatory",
    "ocean",
    "palace",
    "park",
    "parochial school",
    "peak",
    "peninsular plateau",
    "place",
    "plateau",
    "province",
    "prison",
    "racing circuit",
    "railway station",
    "reach",
    "republic",
    "reserve",
    "river",
    "road",
    "school",
    "sports ground",
    "state",
    "stadium",
    "street",
    "street address",
    "studio",
    "temple",
    "theater",
    "theater venue",
    "theatre",
    "town",
    "township",
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
