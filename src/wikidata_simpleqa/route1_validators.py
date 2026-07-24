"""Route 1 Wikidata-specific validator bundle."""

from __future__ import annotations

import re

from .ambiguity import resolve_subject_ambiguity
from .models import AmbiguityResolution, CandidateFact, DomainTemplate, RejectedCandidate
from .validators import (
    answer_is_unique,
    candidate_is_time_invariant,
    candidate_matches_topic_constraints,
    find_exact_name_competitors,
    is_simple_question,
    question_leaks_any_answer,
    question_leaks_bridge_entities,
    question_leaks_location_answer_context,
    preserves_required_anchors,
    reasoning_path_is_connected,
    reasoning_path_is_temporally_safe,
    reasoning_provenance_is_complete,
    shortcut_check,
    violates_cutoff_year_policy,
)

QID_LIKE_LABEL_PATTERN = re.compile(r"^Q\d+$")


def validate_route1_candidate(
    client,
    settings,
    candidate: CandidateFact,
    template: DomainTemplate,
) -> AmbiguityResolution | RejectedCandidate:
    """Validate one Wikidata-derived Route 1 candidate before rewrite."""
    ensure_route1_subject_resource(candidate)
    if not candidate.subject_label.strip():
        return RejectedCandidate(reason="subject_label_missing", candidate=candidate)
    if QID_LIKE_LABEL_PATTERN.fullmatch(candidate.subject_label.strip()):
        return RejectedCandidate(reason="subject_label_qid_like", candidate=candidate)
    if any(QID_LIKE_LABEL_PATTERN.fullmatch(label.strip()) for label in candidate.answer_labels):
        return RejectedCandidate(reason="answer_label_qid_like", candidate=candidate)
    if not answer_is_unique(candidate):
        return RejectedCandidate(reason="answer_not_unique", candidate=candidate)
    if not candidate_matches_topic_constraints(candidate, template):
        return RejectedCandidate(reason="topic_constraints_failed", candidate=candidate)
    if not reasoning_path_is_connected(candidate):
        return RejectedCandidate(reason="reasoning_path_not_connected", candidate=candidate)
    if not reasoning_path_is_temporally_safe(candidate, cutoff_year=settings.cutoff_year):
        return RejectedCandidate(reason="reasoning_path_temporally_unsafe", candidate=candidate)
    if not reasoning_provenance_is_complete(candidate):
        return RejectedCandidate(reason="provenance_incomplete", candidate=candidate)
    if not candidate_is_time_invariant(
        candidate,
        candidate.source_metadata.get("wikidata_access_date", settings.run_date),
    ):
        return RejectedCandidate(reason="time_variant_or_unsettled", candidate=candidate)

    try:
        search_results = client.search_entities(candidate.subject_label, limit=10)
    except Exception as exc:  # noqa: BLE001
        if hasattr(client, "record_problem"):
            client.record_problem(
                "route1_ambiguity_search_failed",
                "wbsearchentities failed during Route 1 ambiguity validation; falling back to hydrated-candidate uniqueness only.",
                domain=template.template_key,
                subject_qid=candidate.subject_qid,
                subject_label=candidate.subject_label,
                error_type=type(exc).__name__,
                error_message=str(exc),
            )
        search_results = []
    competitor_qids = find_exact_name_competitors(
        candidate.subject_qid,
        candidate.subject_label,
        search_results,
    )
    competitor_entities = client.get_entities(competitor_qids) if competitor_qids and hasattr(client, "get_entities") else {}
    resolution = resolve_subject_ambiguity(
        candidate,
        template,
        competitor_entities,
        cutoff_year=settings.cutoff_year,
    )
    if resolution is None:
        return RejectedCandidate(
            reason="subject_ambiguous",
            candidate=candidate,
            notes={"competitor_qids": competitor_qids},
        )
    return resolution


def ensure_route1_subject_resource(candidate: CandidateFact) -> None:
    """Populate a stable subject resource URL and dedup key for Route 1."""
    if not candidate.subject_resource_url:
        metadata_url = str(candidate.source_metadata.get("subject_wikipedia_url", "")).strip()
        title = str(candidate.source_metadata.get("subject_wikipedia_title", "")).strip()
        if metadata_url:
            candidate.subject_resource_url = metadata_url
        elif title:
            candidate.subject_resource_url = "https://en.wikipedia.org/wiki/" + title.replace(" ", "_")
        elif candidate.subject_qid:
            candidate.subject_resource_url = f"https://www.wikidata.org/wiki/{candidate.subject_qid}"
    if not candidate.subject_resource_key:
        candidate.subject_resource_key = candidate.subject_resource_url or candidate.subject_qid


def validate_route1_rewritten_question(
    candidate: CandidateFact,
    required_anchors: list[str],
    rewritten_question: str,
    *,
    cutoff_year: int,
) -> str | None:
    """Return a failure reason for an invalid Route 1 rewrite."""
    question = rewritten_question.strip()
    if not question:
        return "rewrite_missing_question"
    if not preserves_required_anchors(question, required_anchors):
        return "rewrite_lost_required_anchor"
    if question_leaks_any_answer(question, candidate.answer_labels, candidate.answer_aliases):
        return "rewrite_leaks_answer"
    if question_leaks_location_answer_context(question, candidate):
        return "rewrite_leaks_location_answer_context"
    if question_leaks_bridge_entities(question, candidate):
        return "rewrite_leaks_bridge_entity"
    shortcut_results = shortcut_check(candidate, question)
    if not shortcut_results.get("question_requires_all_hops", True):
        return "rewrite_lost_required_reasoning_clue"
    if violates_cutoff_year_policy(question, cutoff_year):
        return "rewrite_contains_temporal_expression"
    if not is_simple_question(question):
        return "rewrite_not_simple_question"
    return None
