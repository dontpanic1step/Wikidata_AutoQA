"""Shared validators for the staged multi-generator pipeline."""

from __future__ import annotations

from typing import Any

from .entity_normalization import normalize_name
from .generation_models import GeneratedCandidate
from .validators import (
    YEAR_PATTERN,
    candidate_is_time_invariant,
    has_forbidden_temporal_text,
    is_simple_question,
    question_leaks_any_answer,
    question_targets_mutable_fact,
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


def validate_generated_candidate(
    candidate: GeneratedCandidate,
    *,
    cutoff_year: int,
) -> tuple[bool, dict[str, Any]]:
    """Run shared deterministic validation on one generated candidate."""
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


def evidence_supports_answer(candidate: GeneratedCandidate) -> bool:
    """Return whether evidence text contains the answer or one alias."""
    normalized_evidence = normalize_name(candidate.evidence.text)
    if not normalized_evidence:
        return False
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
    if candidate.subject_entity.name and normalize_name(candidate.subject_entity.name) not in normalize_name(question):
        return "lost_subject_anchor"
    if question_leaks_any_answer(question, [candidate.answer], candidate.answer_aliases):
        return "answer_leakage"
    if question_targets_mutable_fact(question):
        return "mutable_fact_wording"
    if not is_simple_question(question):
        return "not_simple_question"
    if has_forbidden_temporal_text(question):
        years = [int(match.group(0)) for match in YEAR_PATTERN.finditer(question)]
        if not years:
            return "forbidden_temporal_phrase"
        if any(year >= cutoff_year for year in years):
            return "cutoff_year_exceeded"
    return None


def run_search_based_longtail_verifier(
    candidate: GeneratedCandidate,
    *,
    search_client,
    top_k: int,
    max_full_question_hit_rate: float,
    max_keyword_hit_rate: float,
    max_overall_hit_rate: float,
) -> tuple[bool, dict[str, Any]]:
    """Run the stricter post-rewrite search-based long-tail verification."""
    queries = _build_longtail_queries(candidate)
    features: dict[str, Any] = {
        "top_k": top_k,
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
    normalized_answer_strings = {
        normalize_name(candidate.answer),
        *{
            normalize_name(alias)
            for alias in candidate.answer_aliases
            if normalize_name(alias)
        },
    }
    normalized_question = normalize_name(candidate.final_question)

    for query_name, query_text, query_category in queries:
        results = search_client.search(query_text, max_results=top_k)
        title_hits = 0
        snippet_hits = 0
        exact_question_hit = False
        answer_hit_results = 0
        serialized_results: list[dict[str, Any]] = []
        for result in results:
            normalized_title = normalize_name(result.title)
            normalized_snippet = normalize_name(result.snippet)
            title_hit = any(answer in normalized_title for answer in normalized_answer_strings if answer)
            snippet_hit = any(answer in normalized_snippet for answer in normalized_answer_strings if answer)
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
                }
            )
        features["queries"].append(
            {
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
        )
        if title_hits > 0:
            features["triggered_rule"] = f"{query_name}:answer_in_title"
        if exact_question_hit and not features["triggered_rule"]:
            features["passed"] = False
            features["triggered_rule"] = f"{query_name}:exact_question_hit"
            break
    features["category_hit_rates"] = _compute_category_hit_rates(features["queries"])
    if features["triggered_rule"].endswith(":answer_in_title"):
        features["passed"] = False
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
