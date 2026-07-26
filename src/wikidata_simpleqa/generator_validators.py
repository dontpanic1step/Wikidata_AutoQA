"""Deterministic validators for the formal Route 3 workflow."""

from __future__ import annotations

from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
import re
from time import perf_counter
from typing import Any

from .constants import TEMPORAL_PHRASES
from .date_reference import date_answer_variant_strings
from .entity_normalization import normalize_name
from .generation_models import GeneratedCandidate
from .geographic_leakage import question_leaks_geographic_answer_context
from .number_reference import extract_number_mentions, format_decimal, get_number_reference_margin, number_margin_hits, parse_number_token
from .text_normalization import (
    TextMatcher,
    build_text_matcher,
    display_cleanup,
    display_key,
    text_contains_any,
    text_contains_match,
)
YEAR_PATTERN = re.compile(r"\b(17|18|19|20|21)\d{2}\b")
DATE_PATTERN = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
TEMPORAL_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(phrase) for phrase in TEMPORAL_PHRASES) + r")\b",
    re.IGNORECASE,
)

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
class SearchLongtailVerifierError(RuntimeError):
    """Raised when search long-tail verification fails with audit features."""

    def __init__(self, message: str, *, features: dict[str, Any], original_error: BaseException | None = None) -> None:
        super().__init__(message)
        self.features = features
        self.original_error = original_error
INTEGER_PATTERN = re.compile(r"^-?\d+$")
NUMBER_IN_TEXT_PATTERN = re.compile(r"\b\d[\d,]*\b")


def validate_generated_candidate(
    candidate: GeneratedCandidate,
    *,
    cutoff_year: int,
) -> tuple[bool, dict[str, Any]]:
    """Run deterministic Route 3 validation on one generated candidate."""
    return _validate_wikipedia_infobox_candidate(candidate)

def _validate_wikipedia_infobox_candidate(
    candidate: GeneratedCandidate,
) -> tuple[bool, dict[str, Any]]:
    """Validate answer support in the selected Route 3 source table."""
    validation = {
        "answer_in_evidence": evidence_supports_answer(candidate),
        "route_validation_policy": "answer_in_selected_table",
    }
    return bool(validation["answer_in_evidence"]), validation


def evidence_supports_answer(candidate: GeneratedCandidate) -> bool:
    """Return whether Route 3 evidence contains the answer or one alias."""
    return _route3_evidence_supports_answer(candidate)

def _route3_evidence_supports_answer(candidate: GeneratedCandidate) -> bool:
    """Return whether Route 3 selected table evidence supports the answer."""
    texts = _route3_selected_table_texts(candidate)
    if not texts:
        texts = [("evidence.text", candidate.evidence.text)]
    answer_items = candidate.source_metadata.get("answer_items", [])
    if isinstance(answer_items, list) and answer_items:
        item_sources: list[dict[str, str]] = []
        for item in answer_items:
            item_text = str(item).strip()
            if not item_text:
                continue
            source = _first_answer_hit_source(item_text, [], candidate.answer_type, texts, candidate.source_metadata)
            if not source:
                _record_answer_evidence_match(candidate, matched=False, source="selected_source_table")
                return False
            item_sources.append({"item": item_text, "source": source})
        matched = bool(item_sources)
        candidate.source_metadata["answer_in_evidence_match"] = {
            "matched": matched,
            "source": "selected_source_table",
            "item_sources": item_sources,
        }
        return matched
    source = _first_answer_hit_source(
        candidate.answer,
        candidate.answer_aliases,
        candidate.answer_type,
        texts,
        candidate.source_metadata,
    )
    _record_answer_evidence_match(candidate, matched=bool(source), source=source or "selected_source_table")
    return bool(source)


def _route3_selected_table_texts(candidate: GeneratedCandidate) -> list[tuple[str, str]]:
    """Return Route 3 selected-table text locations in matching order."""
    selected = candidate.source_metadata.get("selected_source_table", {})
    if not isinstance(selected, dict) or not selected:
        return []
    texts: list[tuple[str, str]] = []
    headers = selected.get("headers", [])
    if isinstance(headers, list):
        for index, header in enumerate(headers):
            texts.append((f"selected_source_table.headers[{index}]", str(header)))
    rows = selected.get("rows", [])
    if isinstance(rows, list):
        for row_index, row in enumerate(rows):
            if not isinstance(row, list):
                continue
            row_parts = [str(cell) for cell in row]
            texts.append((f"selected_source_table.rows[{row_index}]", " ".join(row_parts)))
            for column_index, cell in enumerate(row):
                texts.append((f"selected_source_table.rows[{row_index}][{column_index}]", str(cell)))
    for key in ("markdown", "normalized_text"):
        value = selected.get(key, "")
        if str(value).strip():
            texts.append((f"selected_source_table.{key}", str(value)))
    if candidate.evidence.text.strip():
        texts.append(("evidence.text", candidate.evidence.text))
    return texts


def _first_answer_hit_source(
    answer: str,
    answer_aliases: list[str],
    answer_type: str,
    texts: list[tuple[str, str]],
    source_metadata: dict[str, Any],
) -> str:
    """Return the first text source containing one answer matcher."""
    matcher = _build_single_answer_matcher(
        answer,
        answer_aliases,
        answer_type=answer_type,
        source_metadata=source_metadata,
    )
    for source, text in texts:
        if _text_contains_single_answer(text, matcher):
            return source
    return ""


def _record_answer_evidence_match(candidate: GeneratedCandidate, *, matched: bool, source: str) -> None:
    """Attach a compact Route 3 evidence-support audit row."""
    candidate.source_metadata["answer_in_evidence_match"] = {
        "matched": bool(matched),
        "source": source,
    }


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
    if not _is_simple_question(question):
        return "not_simple_question"
    if _has_forbidden_temporal_text(question):
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
    answer_labels = _answer_labels_for_leakage(candidate) + candidate.answer_aliases
    return text_contains_any(question, answer_labels) or question_leaks_geographic_answer_context(
        question,
        answer_labels,
    )


def _has_forbidden_temporal_text(text: str) -> bool:
    """Return whether text contains a temporal phrase handled by the cutoff policy."""
    return bool(YEAR_PATTERN.search(text) or DATE_PATTERN.search(text) or TEMPORAL_PATTERN.search(text))


def _is_simple_question(question: str) -> bool:
    """Return whether the question has the supported short fact-seeking surface."""
    lowered = question.lower()
    forbidden_patterns = ("and why", "explain", "compare", "list all")
    return not any(pattern in lowered for pattern in forbidden_patterns) and len(question.strip()) <= 200

def _answer_number_values(candidate: GeneratedCandidate) -> set[str]:
    """Return normalized numeric values from a numeric answer and aliases."""
    values: set[str] = set()
    for raw_value in [*_answer_labels_for_leakage(candidate), *candidate.answer_aliases]:
        value = parse_number_token(str(raw_value))
        if value is not None:
            values.add(format_decimal(value))
    return values


def _question_has_subject_anchor(question: str, candidate: GeneratedCandidate) -> bool:
    """Return whether one question keeps the route's required subject anchor."""
    subject_name = display_cleanup(candidate.subject_entity.name)
    if not subject_name:
        return True
    if text_contains_any(question, [subject_name]):
        return True
    aliases = candidate.source_metadata.get("subject_anchor_aliases", [])
    if isinstance(aliases, list):
        return text_contains_any(question, aliases)
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
        "query_errors": [],
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
    normalized_question = display_key(candidate.final_question)

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
                if row.get("error"):
                    features["passed"] = False
                    features["triggered_rule"] = f"{row.get('query_name', 'query')}:query_error"
                    features["early_stopped"] = True
                    features["query_errors"].append(_longtail_query_error_payload(row))
                    for pending_future in pending:
                        pending_future.cancel()
                    pending.clear()
                    break
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
    if features["query_errors"]:
        first_error = features["query_errors"][0]
        raise SearchLongtailVerifierError(
            (
                "Search long-tail verifier query failed: "
                f"{first_error.get('query_name', 'query')} "
                f"{first_error.get('error_type', 'Error')}: {first_error.get('error_message', '')}"
            ),
            features=features,
        )
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
    query_started = perf_counter()
    request_event_start = _search_request_event_count(search_client)
    try:
        results = search_client.search(query_text, max_results=top_k)
    except Exception as exc:  # noqa: BLE001
        return {
            "query_index": int(query_plan_row["query_index"]),
            "query_name": query_name,
            "query_category": query_category,
            "query": query_text,
            "duration_seconds": round(perf_counter() - query_started, 4),
            "error": True,
            "error_type": _root_error_type(exc),
            "error_message": _root_error_message(exc),
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "search_request_events": _search_request_events_since(search_client, request_event_start),
        }
    title_hits = 0
    snippet_hits = 0
    exact_question_hit = False
    answer_hit_results = 0
    serialized_results: list[dict[str, Any]] = []
    for result in results:
        normalized_title = display_key(result.title)
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
        "duration_seconds": round(perf_counter() - query_started, 4),
        "error": False,
        "search_request_events": _search_request_events_since(search_client, request_event_start),
        "result_count": len(results),
        "title_hits": title_hits,
        "snippet_hits": snippet_hits,
        "answer_hit_results": answer_hit_results,
        "exact_question_hit": exact_question_hit,
        "results": serialized_results,
    }


def _longtail_query_error_payload(row: dict[str, Any]) -> dict[str, Any]:
    """Return compact query-error diagnostics for candidate-level metadata."""
    return {
        "query_name": row.get("query_name", ""),
        "query_category": row.get("query_category", ""),
        "query": row.get("query", ""),
        "duration_seconds": row.get("duration_seconds"),
        "error_type": row.get("error_type", ""),
        "error_message": row.get("error_message", ""),
        "exception_type": row.get("exception_type", ""),
        "exception_message": row.get("exception_message", ""),
        "search_request_events": row.get("search_request_events", []),
    }


def _search_request_event_count(search_client: Any) -> int:
    """Return the current search-client request event count, if available."""
    events = getattr(search_client, "request_events", None)
    return len(events) if isinstance(events, list) else 0


def _search_request_events_since(search_client: Any, start_index: int) -> list[dict[str, Any]]:
    """Return search-client request events observed since one index."""
    events = getattr(search_client, "request_events", None)
    if not isinstance(events, list):
        return []
    return [dict(event) for event in events[start_index:]]


def _root_error_type(exc: BaseException) -> str:
    """Return the original network error type when wrapped by the search client."""
    original = getattr(exc, "original_error", None)
    if isinstance(original, BaseException):
        return type(original).__name__
    return type(exc).__name__


def _root_error_message(exc: BaseException) -> str:
    """Return the original network error message when wrapped by the search client."""
    original = getattr(exc, "original_error", None)
    if isinstance(original, BaseException):
        return str(original)
    return str(exc)


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


def _build_longtail_queries(candidate: GeneratedCandidate) -> list[tuple[str, str, str]]:
    """Return ordered query rows for post-rewrite long-tail verification."""
    queries: list[tuple[str, str, str]] = [("full_question", candidate.final_question, "full_question")]
    if candidate.search_queries:
        for index, query in enumerate(candidate.search_queries):
            queries.append((f"keyword_query_{index + 1}", query, "keyword_queries"))
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
    text_matchers: list[TextMatcher] = []
    normalized_variants: set[str] = set()
    regexes: list[re.Pattern[str]] = []
    number_values: set[str] = set()
    if answer_type == "Number":
        number_values = {
            format_decimal(value)
            for raw_value in raw_answers
            if (value := parse_number_token(str(raw_value))) is not None
        }
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
                    "number_values": number_values,
                    "answer_type": answer_type,
                }
    elif answer_type == "Date":
        for value in raw_answers:
            text_matchers.extend(_date_matchers(value))
    else:
        for value in raw_answers:
            matcher = build_text_matcher(value)
            if matcher is not None:
                text_matchers.append(matcher)
        if answer_type == "Number":
            margin = get_number_reference_margin(source_metadata)
            if margin is not None:
                return {
                    "normalized_variants": {variant for variant in normalized_variants if variant},
                    "regexes": regexes,
                    "number_reference_margin": margin,
                    "number_values": number_values,
                    "answer_type": answer_type,
                }
    return {
        "normalized_variants": {variant for variant in normalized_variants if variant},
        "regexes": regexes,
        "text_matchers": text_matchers,
        "number_values": number_values,
        "answer_type": answer_type,
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
    number_values = answer_matchers.get("number_values", set())
    if answer_matchers.get("answer_type") == "Number" and isinstance(number_values, set) and number_values:
        text_numbers = {format_decimal(value) for value in extract_number_mentions(text)}
        if number_values.intersection(text_numbers):
            return True
    for pattern in answer_matchers.get("regexes", []):
        if pattern.search(lowered):
            return True
    for matcher in answer_matchers.get("text_matchers", []):
        if text_contains_match(text, matcher):
            return True
    normalized_text = display_key(text)
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


def _date_matchers(value: str) -> list[TextMatcher]:
    """Return typed date variant matchers."""
    raw_variants = {str(value), *date_answer_variant_strings(value)}
    return [
        matcher
        for variant in raw_variants
        if (matcher := build_text_matcher(variant)) is not None
    ]


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
