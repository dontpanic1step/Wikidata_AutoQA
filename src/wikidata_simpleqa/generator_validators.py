"""Shared validators for the staged multi-generator pipeline."""

from __future__ import annotations

from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
import json
import re
from typing import Any

from .cheap_model_qa import parse_json_object
from .entity_normalization import normalize_name
from .generation_models import GeneratedCandidate
from .number_reference import extract_number_mentions, format_decimal, get_number_reference_margin, number_margin_hits, parse_number_token
from .validators import (
    YEAR_PATTERN,
    candidate_is_time_invariant,
    has_forbidden_temporal_text,
    is_simple_question,
    question_leaks_any_answer,
    question_leaks_bridge_entities,
    question_targets_mutable_fact,
    shortcut_check,
)

ALLOW_RELATION_FAMILY_KEYWORDS = {
    "director",
    "author",
    "publisher",
    "architect",
    "creator",
    "founder",
    "developer",
    "journal",
    "country",
    "date of birth",
    "date of death",
    "inception",
    "educated at",
    "narrator",
    "taxon rank",
    "published in",
    "record label",
    "performer",
    "language of work or name",
    "original language",
}

MONTH_VARIANTS = {
    "january": ("january", "jan"),
    "february": ("february", "feb"),
    "march": ("march", "mar"),
    "april": ("april", "apr"),
    "may": ("may",),
    "june": ("june", "jun"),
    "july": ("july", "jul"),
    "august": ("august", "aug"),
    "september": ("september", "sep", "sept"),
    "october": ("october", "oct"),
    "november": ("november", "nov"),
    "december": ("december", "dec"),
}
MONTH_INDEX = {
    alias: index
    for index, aliases in enumerate(MONTH_VARIANTS.values(), start=1)
    for alias in aliases
}
POSITIVE_NUMBER_WORDS = {
    0: "zero",
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
    11: "eleven",
    12: "twelve",
    13: "thirteen",
    14: "fourteen",
    15: "fifteen",
    16: "sixteen",
    17: "seventeen",
    18: "eighteen",
    19: "nineteen",
    20: "twenty",
    21: "twenty one",
    22: "twenty two",
    23: "twenty three",
    24: "twenty four",
    25: "twenty five",
    26: "twenty six",
    27: "twenty seven",
    28: "twenty eight",
    29: "twenty nine",
    30: "thirty",
}
NUMBER_WORDS = {
    **POSITIVE_NUMBER_WORDS,
    **{
        -number: f"minus {word}"
        for number, word in POSITIVE_NUMBER_WORDS.items()
        if 1 <= number <= 20
    },
}
COUNTRY_ALIAS_GROUPS = [
    {"united states", "united states of america", "usa", "us", "u s", "u s a", "america"},
    {"united kingdom", "uk", "u k", "great britain", "britain"},
    {"united arab emirates", "uae", "u a e"},
]
ISO_DATE_PATTERN = re.compile(r"^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})$")
ISO_MONTH_PATTERN = re.compile(r"^(?P<year>\d{4})-(?P<month>\d{2})$")
LONG_DATE_PATTERN = re.compile(
    r"^(?P<month>[a-z]+)\s+(?P<day>\d{1,2})\s+(?P<year>\d{4})$"
)
DMY_DATE_PATTERN = re.compile(
    r"^(?P<day>\d{1,2})\s+(?P<month>[a-z]+)\s+(?P<year>\d{4})$"
)
INTEGER_PATTERN = re.compile(r"^-?\d+$")
NUMBER_IN_TEXT_PATTERN = re.compile(r"\b\d[\d,]*\b")
GENERIC_TABLE_SOURCE_PATTERN = re.compile(
    r"\baccording\s+to\s+(?:the|this|that|provided|source)?\s*(?:[\w\s,'&().-]{0,80}\s+)?table\b",
    flags=re.IGNORECASE,
)
WELL_KNOWN_TABLE_SOURCE_TERMS = (
    "billboard",
    "hot 100",
    "uk singles chart",
    "official singles chart",
    "official albums chart",
    "unesco",
    "world heritage list",
)


def run_fact_level_longtail_prefilter(
    candidate: GeneratedCandidate,
    *,
    max_sitelinks: int,
    max_claims: int,
) -> tuple[bool, dict[str, Any]]:
    """Run a cheap, high-recall long-tail prefilter on one candidate."""
    features = {
        "wikidata_sitelink_count": candidate.source_metadata.get("subject_sitelink_count"),
        "wikidata_claim_count": candidate.source_metadata.get("subject_claim_count"),
        "subject_label_token_count": len(candidate.subject_entity.name.split()),
        "relation_family_allowed": _relation_family_allowed(candidate.relation_or_claim),
        "prefilter_score": 0.0,
        "prefilter_passed": True,
        "triggered_rules": [],
    }
    sitelinks = features["wikidata_sitelink_count"]
    if isinstance(sitelinks, int) and sitelinks > max_sitelinks:
        features["prefilter_passed"] = False
        features["triggered_rules"].append("high_sitelink_count")
        features["prefilter_score"] -= 1.0
    claims = features["wikidata_claim_count"]
    if isinstance(claims, int) and claims > max_claims:
        features["prefilter_passed"] = False
        features["triggered_rules"].append("high_claim_count")
        features["prefilter_score"] -= 1.0
    if not features["relation_family_allowed"]:
        features["prefilter_passed"] = False
        features["triggered_rules"].append("relation_family_not_allowed")
        features["prefilter_score"] -= 1.0
    if features["subject_label_token_count"] <= 1:
        features["prefilter_score"] -= 0.25
        features["triggered_rules"].append("short_subject_label")
    return bool(features["prefilter_passed"]), features


def build_removed_prefilter_stub(candidate: GeneratedCandidate) -> dict[str, Any]:
    """Return audit metadata for the removed internal-popularity prefilter."""
    return {
        "enabled": False,
        "reason": "internal_popularity_prefilter_removed_in_5_13",
        "wikidata_sitelink_count": candidate.source_metadata.get("subject_sitelink_count"),
        "wikidata_claim_count": candidate.source_metadata.get("subject_claim_count"),
    }


def validate_generated_candidate(
    candidate: GeneratedCandidate,
    *,
    cutoff_year: int,
) -> tuple[bool, dict[str, Any]]:
    """Run shared deterministic validation on one generated candidate."""
    if candidate.generation_route == "route3_wikipedia_infobox":
        return _validate_wikipedia_infobox_candidate(candidate, cutoff_year=cutoff_year)
    validation = {
        "stable_answer": False,
        "answer_in_evidence": False,
        "question_unambiguous": False,
        "rewrite_guard_passed": False,
    }
    source_candidate = candidate.source_candidate
    if source_candidate is None:
        return False, validation
    if source_candidate.source_metadata.get("stable_answer_override", False):
        validation["stable_answer"] = True
    else:
        validation["stable_answer"] = candidate_is_time_invariant(
            source_candidate,
            source_candidate.source_metadata.get("wikidata_access_date", candidate.target_time),
        )
    validation["answer_in_evidence"] = evidence_supports_answer(candidate)
    validation["question_unambiguous"] = bool(source_candidate.ambiguity_status)
    validation["rewrite_guard_passed"] = validate_question_surface(
        candidate.final_question,
        candidate,
        cutoff_year=cutoff_year,
    ) is None
    return all(validation.values()), validation


def _validate_wikipedia_infobox_candidate(
    candidate: GeneratedCandidate,
    *,
    cutoff_year: int,
) -> tuple[bool, dict[str, Any]]:
    """Run the limited shared validation that applies to Wikipedia-only table candidates."""
    validation = {
        "stable_answer": True,
        "answer_in_evidence": evidence_supports_answer(candidate),
        "question_unambiguous": bool(candidate.subject_entity.url),
        "rewrite_guard_passed": validate_question_surface(
            candidate.final_question,
            candidate,
            cutoff_year=cutoff_year,
        ) is None,
        "route_local_factual_validation": False,
        "route_validation_policy": "provenance_only_for_wikipedia_infobox_route",
    }
    return all(
        bool(validation[key])
        for key in ("stable_answer", "answer_in_evidence", "question_unambiguous", "rewrite_guard_passed")
    ), validation


def evidence_supports_answer(candidate: GeneratedCandidate) -> bool:
    """Return whether evidence text contains the answer or one alias."""
    normalized_evidence = normalize_name(candidate.evidence.text)
    if not normalized_evidence:
        return False
    if _text_contains_answer(candidate.evidence.text, _build_answer_matchers(candidate)):
        return True
    answer_items = candidate.source_metadata.get("answer_items", [])
    if isinstance(answer_items, list) and answer_items:
        return all(
            normalize_name(str(item)) and normalize_name(str(item)) in normalized_evidence
            for item in answer_items
        )
    if normalize_name(candidate.answer) in normalized_evidence:
        return True
    return any(
        normalize_name(alias) and normalize_name(alias) in normalized_evidence
        for alias in candidate.answer_aliases
    )


def validate_question_surface(
    question: str,
    candidate: GeneratedCandidate,
    *,
    cutoff_year: int,
) -> str | None:
    """Return a failure reason when the final question surface is invalid."""
    if not question.strip():
        return "missing_question"
    if not _question_has_subject_anchor(question, candidate):
        _record_surface_warning(candidate, "lost_subject_anchor")
    if _question_leaks_candidate_answer(question, candidate):
        return "answer_leakage"
    source_candidate = candidate.source_candidate
    if source_candidate is not None:
        shortcut_results = shortcut_check(source_candidate, question)
        if not shortcut_results.get("question_requires_all_hops", True):
            return "lost_required_reasoning_clue"
        if question_leaks_bridge_entities(question, source_candidate):
            return "bridge_entity_leakage"
    if not is_simple_question(question):
        return "not_simple_question"
    if has_forbidden_temporal_text(question):
        years = [int(match.group(0)) for match in YEAR_PATTERN.finditer(question)]
        if not years:
            return "forbidden_temporal_phrase"
        if any(year >= cutoff_year for year in years):
            return "cutoff_year_exceeded"
    return None


def _record_surface_warning(candidate: GeneratedCandidate, warning: str) -> None:
    """Attach a non-blocking surface warning without duplicating entries."""
    warnings = candidate.source_metadata.setdefault("surface_validation_warnings", [])
    if isinstance(warnings, list) and warning not in warnings:
        warnings.append(warning)


def _question_leaks_candidate_answer(question: str, candidate: GeneratedCandidate) -> bool:
    """Return whether the question leaks the answer, with numeric-safe matching."""
    if candidate.answer_type == "Number":
        answer_numbers = _answer_number_values(candidate)
        if answer_numbers:
            question_numbers = {
                format_decimal(value)
                for value in extract_number_mentions(question)
            }
            return bool(answer_numbers.intersection(question_numbers))
    return question_leaks_any_answer(
        question,
        _answer_labels_for_leakage(candidate),
        candidate.answer_aliases,
    )


def _answer_number_values(candidate: GeneratedCandidate) -> set[str]:
    """Return normalized numeric values from a numeric answer and aliases."""
    values: set[str] = set()
    for raw_value in [*_answer_labels_for_leakage(candidate), *candidate.answer_aliases]:
        value = parse_number_token(str(raw_value))
        if value is not None:
            values.add(format_decimal(value))
    return values


def _uses_generic_table_source_wording(question: str) -> bool:
    """Return whether a question leans on generic source-table wording."""
    lowered = question.lower()
    if not GENERIC_TABLE_SOURCE_PATTERN.search(lowered):
        return False
    return not any(term in lowered for term in WELL_KNOWN_TABLE_SOURCE_TERMS)


def _question_has_subject_anchor(question: str, candidate: GeneratedCandidate) -> bool:
    """Return whether one question keeps the route's required subject anchor."""
    subject_name = normalize_name(candidate.subject_entity.name)
    normalized_question = normalize_name(question)
    if not subject_name:
        return True
    if subject_name in normalized_question:
        return True
    aliases = candidate.source_metadata.get("subject_anchor_aliases", [])
    if isinstance(aliases, list):
        return any(
            normalize_name(str(alias)) and normalize_name(str(alias)) in normalized_question
            for alias in aliases
        )
    return False


def _answer_labels_for_leakage(candidate: GeneratedCandidate) -> list[str]:
    """Return canonical answer labels for question-leakage checks."""
    answer_items = candidate.source_metadata.get("answer_items", [])
    if isinstance(answer_items, list) and answer_items:
        return [str(item) for item in answer_items if str(item).strip()]
    return [candidate.answer]


def run_search_based_longtail_verifier(
    candidate: GeneratedCandidate,
    *,
    search_client,
    snippet_judge_client=None,
    top_k: int,
    max_full_question_hit_rate: float,
    max_keyword_hit_rate: float,
    max_overall_hit_rate: float,
    max_parallel_queries: int = 1,
) -> tuple[bool, dict[str, Any]]:
    """Run the stricter post-rewrite search-based long-tail verification."""
    queries = _build_longtail_queries(candidate)
    query_plan = [
        {
            "query_index": index,
            "query_name": query_name,
            "query_text": query_text,
            "query_category": query_category,
        }
        for index, (query_name, query_text, query_category) in enumerate(queries)
    ]
    features: dict[str, Any] = {
        "top_k": top_k,
        "max_parallel_queries": max_parallel_queries,
        "early_stopped": False,
        "queries": [],
        "category_hit_rates": {},
        "thresholds": {
            "full_question": max_full_question_hit_rate,
            "keyword_queries": max_keyword_hit_rate,
            "overall": max_overall_hit_rate,
        },
        "passed": True,
        "triggered_rule": "",
    }
    answer_matchers = _build_answer_matchers(candidate)
    normalized_question = normalize_name(candidate.final_question)

    max_workers = max(1, int(max_parallel_queries or 1))
    next_query_index = 0
    pending = {}
    executor = ThreadPoolExecutor(max_workers=max_workers)
    try:
        while next_query_index < len(query_plan) or pending:
            while next_query_index < len(query_plan) and len(pending) < max_workers:
                row = query_plan[next_query_index]
                future = executor.submit(
                    _run_one_longtail_query,
                    row,
                    search_client,
                    top_k,
                    answer_matchers,
                    normalized_question,
                )
                pending[future] = row
                next_query_index += 1
            if not pending:
                break
            done, _ = wait(pending, return_when=FIRST_COMPLETED)
            for future in done:
                pending.pop(future)
                row = future.result()
                features["queries"].append(row)
                features["queries"].sort(key=lambda item: int(item.get("query_index", 0)))
                if row.get("exact_question_hit") and not features["triggered_rule"]:
                    features["passed"] = False
                    features["triggered_rule"] = f"{row.get('query_name', 'query')}:exact_question_hit"
                    features["early_stopped"] = True
                if not features["triggered_rule"]:
                    title_rule = _first_title_hit_rate_rule(
                        features["queries"],
                        full_question_threshold=max_full_question_hit_rate,
                        keyword_threshold=max_keyword_hit_rate,
                        overall_threshold=max_overall_hit_rate,
                    )
                    if title_rule is not None:
                        features["passed"] = False
                        features["triggered_rule"] = title_rule
                        features["early_stopped"] = True
                if not features["triggered_rule"]:
                    impossible_rule = _impossible_hit_rate_recovery_rule(
                        features["queries"],
                        query_plan=query_plan,
                        top_k=top_k,
                        full_question_threshold=max_full_question_hit_rate,
                        keyword_threshold=max_keyword_hit_rate,
                        overall_threshold=max_overall_hit_rate,
                    )
                    if impossible_rule is not None:
                        features["passed"] = False
                        features["triggered_rule"] = impossible_rule
                        features["early_stopped"] = True
                if features["triggered_rule"]:
                    for pending_future in pending:
                        pending_future.cancel()
                    pending.clear()
                    break
    finally:
        executor.shutdown(wait=True, cancel_futures=True)

    for row in features["queries"]:
        row.pop("query_index", None)
    features["category_hit_rates"] = _compute_category_hit_rates(features["queries"])
    if features["triggered_rule"]:
        return False, features

    title_rule = _first_title_hit_rate_rule(
        features["queries"],
        full_question_threshold=max_full_question_hit_rate,
        keyword_threshold=max_keyword_hit_rate,
        overall_threshold=max_overall_hit_rate,
    )
    if title_rule is not None:
        features["passed"] = False
        features["triggered_rule"] = title_rule
        return False, features
    snippet_judge_features = _run_low_integer_snippet_judge(
        candidate,
        features["queries"],
        snippet_judge_client=snippet_judge_client,
    )
    if snippet_judge_features is not None:
        features["number_snippet_judge"] = snippet_judge_features
        if snippet_judge_features.get("found_in_every_snippet"):
            features["passed"] = False
            features["triggered_rule"] = "number_snippet_judge:found_in_every_snippet"
            return False, features
    if not features["triggered_rule"]:
        full_question_rate = features["category_hit_rates"].get("full_question", {}).get("answer_hit_rate", 0.0)
        keyword_rate = features["category_hit_rates"].get("keyword_queries", {}).get("answer_hit_rate", 0.0)
        overall_rate = features["category_hit_rates"].get("overall", {}).get("answer_hit_rate", 0.0)
        if full_question_rate > max_full_question_hit_rate:
            features["passed"] = False
            features["triggered_rule"] = "full_question:hit_rate_exceeded"
        elif keyword_rate > max_keyword_hit_rate:
            features["passed"] = False
            features["triggered_rule"] = "keyword_queries:hit_rate_exceeded"
        elif overall_rate > max_overall_hit_rate:
            features["passed"] = False
            features["triggered_rule"] = "overall:hit_rate_exceeded"
    return bool(features["passed"]), features


def _run_one_longtail_query(
    query_plan_row: dict[str, Any],
    search_client,
    top_k: int,
    answer_matchers: dict[str, Any],
    normalized_question: str,
) -> dict[str, Any]:
    """Run one search query and return its serialized long-tail evidence row."""
    query_name = str(query_plan_row["query_name"])
    query_text = str(query_plan_row["query_text"])
    query_category = str(query_plan_row["query_category"])
    results = search_client.search(query_text, max_results=top_k)
    title_hits = 0
    snippet_hits = 0
    exact_question_hit = False
    answer_hit_results = 0
    serialized_results: list[dict[str, Any]] = []
    for result in results:
        normalized_title = normalize_name(result.title)
        title_number_margin_hits = _answer_number_margin_hits(result.title, answer_matchers)
        snippet_number_margin_hits = _answer_number_margin_hits(result.snippet, answer_matchers)
        title_hit = bool(title_number_margin_hits) or _text_contains_answer(result.title, answer_matchers)
        snippet_hit = bool(snippet_number_margin_hits) or _text_contains_answer(result.snippet, answer_matchers)
        if title_hit:
            title_hits += 1
        if snippet_hit:
            snippet_hits += 1
        if title_hit or snippet_hit:
            answer_hit_results += 1
        if normalized_question and normalized_question in normalized_title:
            exact_question_hit = True
        serialized_results.append(
            {
                "title": result.title,
                "snippet": result.snippet,
                "url": result.url,
                "answer_hit": bool(title_hit or snippet_hit),
                "title_number_margin_hits": title_number_margin_hits,
                "snippet_number_margin_hits": snippet_number_margin_hits,
            }
        )
    return {
        "query_index": int(query_plan_row["query_index"]),
        "query_name": query_name,
        "query_category": query_category,
        "query": query_text,
        "result_count": len(results),
        "title_hits": title_hits,
        "snippet_hits": snippet_hits,
        "answer_hit_results": answer_hit_results,
        "exact_question_hit": exact_question_hit,
        "results": serialized_results,
    }


def _impossible_hit_rate_recovery_rule(
    query_rows: list[dict[str, Any]],
    *,
    query_plan: list[dict[str, Any]],
    top_k: int,
    full_question_threshold: float,
    keyword_threshold: float,
    overall_threshold: float,
) -> str | None:
    """Return a rejection rule when remaining queries cannot lower a hit rate enough."""
    processed_indexes = {int(row.get("query_index", -1)) for row in query_rows}
    checks = [
        ("full_question", full_question_threshold),
        ("keyword_queries", keyword_threshold),
        ("overall", overall_threshold),
    ]
    for category, threshold in checks:
        if category == "overall":
            current_rows = [
                row for row in query_rows if row.get("query_category") in {"full_question", "keyword_queries"}
            ]
            remaining_count = sum(
                1
                for row in query_plan
                if int(row["query_index"]) not in processed_indexes
                and row.get("query_category") in {"full_question", "keyword_queries"}
            )
        else:
            current_rows = [row for row in query_rows if row.get("query_category") == category]
            remaining_count = sum(
                1
                for row in query_plan
                if int(row["query_index"]) not in processed_indexes
                and row.get("query_category") == category
            )
        hit_results = sum(int(row.get("answer_hit_results", 0)) for row in current_rows)
        current_results = sum(int(row.get("result_count", 0)) for row in current_rows)
        possible_total_results = current_results + remaining_count * top_k
        if possible_total_results and hit_results / possible_total_results > threshold:
            return f"{category}:hit_rate_exceeded"
    return None


def _first_title_hit_rate_rule(
    query_rows: list[dict[str, Any]],
    *,
    full_question_threshold: float,
    keyword_threshold: float,
    overall_threshold: float,
) -> str | None:
    """Return the first title-hit threshold violation, if any."""
    total_title_hits = 0
    total_results = 0
    for row in query_rows:
        result_count = int(row.get("result_count", 0))
        title_hits = int(row.get("title_hits", 0))
        total_title_hits += title_hits
        total_results += result_count
        if result_count <= 0 or title_hits <= 0:
            continue
        threshold = (
            full_question_threshold
            if row.get("query_category") == "full_question"
            else keyword_threshold
        )
        if title_hits / result_count > threshold:
            return f"{row.get('query_name', 'query')}:answer_in_title"
    if total_results > 0 and total_title_hits / total_results > overall_threshold:
        return "overall:answer_in_title"
    return None


def _relation_family_allowed(relation_or_claim: str) -> bool:
    """Return whether one coarse relation family is allowed by the prefilter."""
    normalized = relation_or_claim.strip().lower()
    return normalized in ALLOW_RELATION_FAMILY_KEYWORDS


def _build_longtail_queries(candidate: GeneratedCandidate) -> list[tuple[str, str, str]]:
    """Return ordered query rows for post-rewrite long-tail verification."""
    queries: list[tuple[str, str, str]] = [("full_question", candidate.final_question, "full_question")]
    if candidate.search_queries:
        for index, query in enumerate(candidate.search_queries):
            queries.append((f"keyword_query_{index + 1}", query, "keyword_queries"))
        return queries
    if candidate.generation_route == "kelm_bootstrap_half_pipeline":
        return queries
    queries.extend(
        [
            ("subject_relation", f"{candidate.subject_entity.name} {candidate.relation_or_claim}", "keyword_queries"),
            (
                "subject_relation_answer",
                f"{candidate.subject_entity.name} {candidate.relation_or_claim} {candidate.answer}",
                "answer_probe",
            ),
        ]
    )
    return queries


def _compute_category_hit_rates(query_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Aggregate answer-hit rates by query category and overall."""
    grouped_rows = {
        "full_question": [row for row in query_rows if row.get("query_category") == "full_question"],
        "keyword_queries": [row for row in query_rows if row.get("query_category") == "keyword_queries"],
        "answer_probe": [row for row in query_rows if row.get("query_category") == "answer_probe"],
        "overall": [
            row
            for row in query_rows
            if row.get("query_category") in {"full_question", "keyword_queries"}
        ],
    }
    summary: dict[str, dict[str, Any]] = {}
    for category_name, rows in grouped_rows.items():
        total_results = sum(int(row.get("result_count", 0)) for row in rows)
        answer_hit_results = sum(int(row.get("answer_hit_results", 0)) for row in rows)
        title_hit_results = sum(int(row.get("title_hits", 0)) for row in rows)
        snippet_hit_results = sum(int(row.get("snippet_hits", 0)) for row in rows)
        summary[category_name] = {
            "query_count": len(rows),
            "total_results": total_results,
            "answer_hit_results": answer_hit_results,
            "title_hit_results": title_hit_results,
            "snippet_hit_results": snippet_hit_results,
            "answer_hit_rate": (answer_hit_results / total_results) if total_results else 0.0,
        }
    return summary


def _build_accepted_answer_set(candidate: GeneratedCandidate) -> set[str]:
    """Return normalized accepted answer strings."""
    return {
        normalize_name(candidate.answer),
        *{
            normalize_name(alias)
            for alias in candidate.answer_aliases
            if normalize_name(alias)
        },
    }


def _build_answer_matchers(candidate: GeneratedCandidate) -> dict[str, Any]:
    """Build normalized answer variants and regexes for search matching."""
    answer_items = candidate.source_metadata.get("answer_items", [])
    if isinstance(answer_items, list) and answer_items:
        item_matchers = [
            _build_single_answer_matcher(
                str(item),
                [],
                answer_type=candidate.answer_type,
                source_metadata=candidate.source_metadata,
            )
            for item in answer_items
            if str(item).strip()
        ]
        if item_matchers:
            return {
                "answer_items": [str(item).strip() for item in answer_items if str(item).strip()],
                "item_matchers": item_matchers,
            }
    return _build_single_answer_matcher(
        candidate.answer,
        candidate.answer_aliases,
        answer_type=candidate.answer_type,
        source_metadata=candidate.source_metadata,
    )


def _build_single_answer_matcher(
    answer: str,
    answer_aliases: list[str],
    *,
    answer_type: str,
    source_metadata: dict[str, Any],
) -> dict[str, Any]:
    """Build normalized variants and regexes for one answer string."""
    raw_answers = [answer, *answer_aliases]
    normalized_variants = {
        normalize_name(value)
        for value in raw_answers
        if normalize_name(value)
    }
    regexes: list[re.Pattern[str]] = []
    integer_value = _parse_integer_answer(answer)
    if answer_type == "Number" and integer_value is not None:
        normalized_variants.update(_number_variants(integer_value))
        regexes.extend(_number_regexes(integer_value))
        if integer_value < -10 or integer_value > 30:
            margin = get_number_reference_margin(source_metadata)
            if margin is not None:
                return {
                    "normalized_variants": {variant for variant in normalized_variants if variant},
                    "regexes": regexes,
                    "number_reference_margin": margin,
                }
    else:
        for value in raw_answers:
            normalized_variants.update(_country_alias_variants(value))
            normalized_variants.update(_date_variants(value))
        if answer_type == "Number":
            margin = get_number_reference_margin(source_metadata)
            if margin is not None:
                return {
                    "normalized_variants": {variant for variant in normalized_variants if variant},
                    "regexes": regexes,
                    "number_reference_margin": margin,
                }
    return {
        "normalized_variants": {variant for variant in normalized_variants if variant},
        "regexes": regexes,
    }


def _text_contains_answer(text: str, answer_matchers: dict[str, Any]) -> bool:
    """Return whether one title or snippet contains an answer variant."""
    item_matchers = answer_matchers.get("item_matchers")
    if isinstance(item_matchers, list) and item_matchers:
        return all(_text_contains_single_answer(text, matcher) for matcher in item_matchers)
    return _text_contains_single_answer(text, answer_matchers)


def _text_contains_single_answer(text: str, answer_matchers: dict[str, Any]) -> bool:
    """Return whether one title or snippet contains one answer variant."""
    lowered = text.lower()
    for pattern in answer_matchers.get("regexes", []):
        if pattern.search(lowered):
            return True
    normalized_text = normalize_name(text)
    return any(
        variant and variant in normalized_text
        for variant in answer_matchers.get("normalized_variants", set())
    )


def _answer_number_margin_hits(text: str, answer_matchers: dict[str, Any]) -> list[str]:
    """Return numeric mentions that match the optional reference margin."""
    margin = answer_matchers.get("number_reference_margin")
    if not isinstance(margin, dict) or not margin.get("enabled"):
        return []
    return number_margin_hits(text, {"number_reference_margin": margin})


def _country_alias_variants(value: str) -> set[str]:
    """Return conservative country alias variants for search matching."""
    normalized = normalize_name(value)
    variants = {normalized} if normalized else set()
    for alias_group in COUNTRY_ALIAS_GROUPS:
        if normalized in alias_group:
            variants.update(alias_group)
    return variants


def _date_variants(value: str) -> set[str]:
    """Return normalized date variants for search matching."""
    normalized = normalize_name(value)
    variants = {normalized} if normalized else set()
    match = ISO_DATE_PATTERN.fullmatch(value.strip())
    if match:
        year = match.group("year")
        month = int(match.group("month"))
        day = int(match.group("day"))
        for month_alias in MONTH_VARIANTS.get(list(MONTH_VARIANTS.keys())[month - 1], ()):
            variants.add(normalize_name(f"{month_alias} {day} {year}"))
            variants.add(normalize_name(f"{day} {month_alias} {year}"))
        variants.add(normalize_name(f"{year} {month} {day}"))
        return variants
    match = ISO_MONTH_PATTERN.fullmatch(value.strip())
    if match:
        year = match.group("year")
        month = int(match.group("month"))
        if 1 <= month <= 12:
            for month_alias in MONTH_VARIANTS.get(list(MONTH_VARIANTS.keys())[month - 1], ()):
                variants.add(normalize_name(f"{month_alias} {year}"))
                variants.add(normalize_name(f"{year} {month_alias}"))
            variants.add(normalize_name(f"{year} {month}"))
        return variants
    for pattern in (LONG_DATE_PATTERN, DMY_DATE_PATTERN):
        match = pattern.fullmatch(normalized)
        if not match:
            continue
        year = match.group("year")
        month_name = match.group("month")
        day = int(match.group("day"))
        month_number = MONTH_INDEX.get(month_name)
        if month_number is None:
            return variants
        for month_alias in MONTH_VARIANTS.get(list(MONTH_VARIANTS.keys())[month_number - 1], ()):
            variants.add(normalize_name(f"{month_alias} {day} {year}"))
            variants.add(normalize_name(f"{day} {month_alias} {year}"))
        variants.add(normalize_name(f"{year} {month_number} {day}"))
        return variants
    return variants


def _parse_integer_answer(value: str) -> int | None:
    """Parse an exact integer answer from digits or simple English words."""
    stripped = value.strip()
    compact = stripped.replace(",", "")
    if INTEGER_PATTERN.fullmatch(compact):
        return int(compact)
    normalized = normalize_name(stripped)
    for number, phrase in NUMBER_WORDS.items():
        if normalized in {phrase, phrase.replace("minus ", "negative ")}:
            return number
    return None


def _number_variants(value: int) -> set[str]:
    """Return normalized textual number variants."""
    variants = {str(value), normalize_name(f"{value:,}")}
    word_form = NUMBER_WORDS.get(value)
    if word_form:
        variants.add(normalize_name(word_form))
        if word_form.startswith("minus "):
            variants.add(normalize_name(word_form.replace("minus ", "negative ")))
        if " " in word_form:
            variants.add(normalize_name(word_form.replace(" ", "-")))
    return {variant for variant in variants if variant}


def _number_regexes(value: int) -> list[re.Pattern[str]]:
    """Return regexes for matching numeric forms in raw snippets."""
    patterns = [re.compile(rf"(?<![\w-]){re.escape(str(value))}(?![\w-])")]
    if value >= 1000:
        patterns.append(re.compile(rf"(?<![\w-]){value:,}(?![\w-])"))
    word_form = NUMBER_WORDS.get(value)
    if word_form:
        hyphen_form = word_form.replace(" ", "-")
        patterns.append(re.compile(rf"\b{re.escape(word_form)}\b"))
        if word_form.startswith("minus "):
            negative_form = word_form.replace("minus ", "negative ")
            patterns.append(re.compile(rf"\b{re.escape(negative_form)}\b"))
        if hyphen_form != word_form:
            patterns.append(re.compile(rf"\b{re.escape(hyphen_form)}\b"))
    return patterns


def _run_low_integer_snippet_judge(
    candidate: GeneratedCandidate,
    query_rows: list[dict[str, Any]],
    *,
    snippet_judge_client,
) -> dict[str, Any] | None:
    """Judge snippet answer visibility for exact integer answers in [-10, 30]."""
    integer_value = _parse_integer_answer(candidate.answer)
    if candidate.answer_type != "Number" or integer_value is None or integer_value < -10 or integer_value > 30:
        return None
    snippets = [
        str(result.get("snippet", "")).strip()
        for row in query_rows
        for result in row.get("results", [])
        if str(result.get("snippet", "")).strip()
    ]
    if not snippets:
        return {
            "enabled": True,
            "model_used": "",
            "answer_integer": integer_value,
            "snippet_count": 0,
            "found_in_every_snippet": False,
            "reason": "no_snippets_available",
        }
    if snippet_judge_client is None:
        return {
            "enabled": False,
            "model_used": "",
            "answer_integer": integer_value,
            "snippet_count": len(snippets),
            "found_in_every_snippet": False,
            "reason": "snippet_judge_unavailable",
        }
    prompt = _build_number_snippet_judge_prompt(candidate.final_question, candidate.answer, snippets)
    response = parse_json_object(snippet_judge_client.complete_text(prompt))
    found_in_every_snippet = bool(response.get("found_in_every_snippet", False))
    reason = str(response.get("reason", "")).strip()
    return {
        "enabled": True,
        "model_used": getattr(getattr(snippet_judge_client, "config", None), "model", ""),
        "answer_integer": integer_value,
        "snippet_count": len(snippets),
        "found_in_every_snippet": found_in_every_snippet,
        "reason": reason,
    }


def _build_number_snippet_judge_prompt(question: str, answer: str, snippets: list[str]) -> str:
    """Build the prompt for the low-integer snippet visibility judge."""
    payload = {
        "question": question,
        "gold_answer": answer,
        "snippets": snippets,
    }
    return (
        "Decide whether the gold answer can be found in every snippet.\n"
        "Return JSON only.\n"
        'Format: {"found_in_every_snippet": boolean, "reason": string}.\n'
        "Treat equivalent number forms as matches, including digits, commas, and English number words.\n\n"
        f"{json.dumps(payload, ensure_ascii=False)}"
    )
