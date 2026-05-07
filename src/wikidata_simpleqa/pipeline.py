"""Pipeline for conservative single-fact and compositional multi-hop generation."""

from __future__ import annotations

from dataclasses import dataclass, field

from .ambiguity import resolve_subject_ambiguity
from .canonical_questions import build_canonical_question
from .candidate_harvester import harvest_candidates
from .config import Settings
from .domain_templates import get_stage1_templates
from .io import write_jsonl
from .llm_rewrite import build_rewrite_payload, make_rewrite_client
from .models import CandidateFact, RejectedCandidate
from .validators import (
    answer_is_unique,
    candidate_is_time_invariant,
    find_exact_name_competitors,
    has_forbidden_temporal_text,
    has_year,
    is_simple_question,
    ordinal_candidate_is_safe,
    preserves_required_anchors,
    question_leaks_any_answer,
    question_leaks_answer,
    question_leaks_bridge_entities,
    question_leaks_location_answer_context,
    reasoning_path_is_connected,
    reasoning_path_is_temporally_safe,
    reasoning_provenance_is_complete,
    shortcut_check,
)
from .wikidata_client import WikidataClient


@dataclass(slots=True)
class PipelineResult:
    """Accepted and rejected outputs from one pipeline run."""

    accepted: list[dict] = field(default_factory=list)
    rejected: list[dict] = field(default_factory=list)
    telemetry: dict = field(default_factory=dict)


def run_pipeline(settings: Settings) -> PipelineResult:
    """Run the conservative generation flow and write accepted/rejected JSONL."""
    return run_pipeline_for_templates(settings=settings, templates=get_stage1_templates())


def run_pipeline_for_templates(settings: Settings, templates, client: WikidataClient | None = None) -> PipelineResult:
    """Run the pipeline for an explicit template list."""
    if client is None:
        client = WikidataClient(
            user_agent=settings.user_agent,
            proxy=settings.proxy,
            timeout_seconds=settings.timeout_seconds,
            cache_dir=settings.cache_dir,
        )
    rewrite_client = None
    if settings.rewrite_enabled:
        rewrite_client = make_rewrite_client(settings.rewrite_llm, settings.timeout_seconds)
    accepted_records: list[dict] = []
    rejected_records: list[dict] = []
    seen_questions: set[str] = set()

    for template in templates:
        accepted_for_template = 0
        candidates = harvest_candidates(client=client, settings=settings, template=template)
        for candidate in candidates:
            validation = _validate_candidate(client, settings, candidate, template)
            if isinstance(validation, RejectedCandidate):
                rejected_records.append(validation.to_output_record())
                continue

            candidate.ambiguity_status = validation.status
            candidate.disambiguation_signature = validation.signature
            candidate.competitor_qids = validation.competitor_qids
            candidate.canonical_question = build_canonical_question(candidate, template, validation)
            enforce_non_temporal_question = _question_must_be_non_temporal(candidate)
            candidate.validation_flags["no_year"] = (
                not has_year(candidate.canonical_question)
                if enforce_non_temporal_question
                else True
            )
            candidate.validation_flags["no_temporal_expression"] = (
                not has_forbidden_temporal_text(candidate.canonical_question)
                if enforce_non_temporal_question
                else True
            )
            candidate.validation_flags["answer_unique"] = True
            candidate.validation_flags["subject_unique_under_question"] = True
            candidate.validation_flags["answer_not_leaked"] = not question_leaks_answer(
                candidate.canonical_question, candidate.answer_labels
            )
            candidate.validation_flags["location_context_not_leaked"] = (
                not question_leaks_location_answer_context(candidate.canonical_question, candidate)
            )
            candidate.validation_flags["bridge_not_leaked"] = not question_leaks_bridge_entities(
                candidate.canonical_question, candidate
            )
            shortcut_results = shortcut_check(candidate, candidate.canonical_question)
            candidate.shortcut_checks = shortcut_results
            candidate.question_requires_all_hops = bool(
                shortcut_results.get("question_requires_all_hops", True)
            )
            candidate.validation_flags["question_requires_all_hops"] = candidate.question_requires_all_hops
            candidate.validation_flags["shortcut_free"] = bool(
                shortcut_results.get("shortcut_free", True)
            )
            candidate.validation_flags["provenance_complete"] = reasoning_provenance_is_complete(
                candidate
            )

            if not all(candidate.validation_flags.values()):
                rejected_records.append(
                    RejectedCandidate(
                        reason="canonical_question_failed_validation",
                        candidate=candidate,
                        notes={"validation_flags": candidate.validation_flags},
                    ).to_output_record()
                )
                continue

            _apply_rewrite_if_enabled(candidate, rewrite_client)
            final_question = (candidate.rewritten_question or candidate.canonical_question).strip()
            if final_question in seen_questions:
                rejected_records.append(
                    RejectedCandidate(
                        reason="duplicate_question",
                        candidate=candidate,
                        notes={"question": final_question},
                    ).to_output_record()
                )
                continue

            seen_questions.add(final_question)
            example_id = f"wikidata_verified_pilot_{len(accepted_records) + 1:06d}"
            accepted_records.append(candidate.to_output_record(example_id))
            accepted_for_template += 1

            if accepted_for_template >= 1 or len(accepted_records) >= settings.pilot_total:
                break
        if len(accepted_records) >= settings.pilot_total:
            break

    write_jsonl(settings.output_path, accepted_records)
    write_jsonl(settings.rejected_output_path, rejected_records)
    return PipelineResult(
        accepted=accepted_records,
        rejected=rejected_records,
        telemetry=client.stats_snapshot(),
    )


def _apply_rewrite_if_enabled(candidate: CandidateFact, rewrite_client) -> None:
    candidate.validation_flags["llm_rewrite_used"] = False
    if rewrite_client is None:
        candidate.validation_flags["rewrite_failure_reason"] = "rewrite_disabled"
        return

    payload = build_rewrite_payload(candidate)
    try:
        rewritten = rewrite_client.rewrite_question(payload)
        rewritten_question = str(rewritten.get("question", "")).strip()
    except Exception as exc:  # noqa: BLE001
        candidate.validation_flags["rewrite_failure_reason"] = f"rewrite_request_failed:{type(exc).__name__}"
        return

    failure_reason = _validate_rewritten_question(candidate, payload["required_anchors"], rewritten_question)
    if failure_reason is not None:
        candidate.validation_flags["rewrite_failure_reason"] = failure_reason
        return

    candidate.rewritten_question = rewritten_question
    candidate.validation_flags["llm_rewrite_used"] = True
    candidate.validation_flags.pop("rewrite_failure_reason", None)


def _validate_rewritten_question(
    candidate: CandidateFact,
    required_anchors: list[str],
    rewritten_question: str,
) -> str | None:
    if not rewritten_question:
        return "rewrite_missing_question"
    if _question_must_be_non_temporal(candidate):
        if has_year(rewritten_question):
            return "rewrite_contains_year"
        if has_forbidden_temporal_text(rewritten_question):
            return "rewrite_contains_temporal_expression"
    if not preserves_required_anchors(rewritten_question, required_anchors):
        return "rewrite_lost_required_anchor"
    shortcut_results = shortcut_check(candidate, rewritten_question)
    if not shortcut_results.get("question_requires_all_hops", True):
        return "rewrite_lost_required_anchor"
    if question_leaks_any_answer(
        rewritten_question,
        candidate.answer_labels,
        candidate.answer_aliases,
    ):
        return "rewrite_leaks_answer"
    if question_leaks_bridge_entities(rewritten_question, candidate):
        return "rewrite_leaks_answer"
    if not is_simple_question(rewritten_question):
        return "rewrite_not_simple_question"
    return None


def _validate_candidate(
    client: WikidataClient,
    settings: Settings,
    candidate: CandidateFact,
    template,
):
    if not candidate.subject_label:
        return RejectedCandidate(reason="no_english_label", candidate=candidate)
    if not candidate.answer_labels:
        return RejectedCandidate(reason="no_answer_label", candidate=candidate)
    if has_year(candidate.subject_label) and not settings.allow_year_in_official_title:
        return RejectedCandidate(reason="subject_label_contains_year", candidate=candidate)
    if has_forbidden_temporal_text(candidate.subject_label):
        return RejectedCandidate(
            reason="subject_label_contains_temporal_expression",
            candidate=candidate,
        )
    if not candidate_is_time_invariant(candidate, settings.run_date):
        if candidate.target_property_pid != "P57":
            return RejectedCandidate(reason="answer_not_time_invariant", candidate=candidate)
        return RejectedCandidate(reason="future_dated_or_unsettled_fact", candidate=candidate)
    if not answer_is_unique(candidate):
        return RejectedCandidate(reason="answer_not_unique", candidate=candidate)
    if not reasoning_provenance_is_complete(candidate):
        return RejectedCandidate(
            reason="provenance_incomplete",
            candidate=candidate,
            notes={"reasoning_error": "provenance_incomplete"},
        )
    if not reasoning_path_is_temporally_safe(candidate):
        return RejectedCandidate(
            reason="same_label_competitor_requires_temporal_disambiguation",
            candidate=candidate,
            notes={"reasoning_error": "hop_requires_temporal_disambiguation"},
        )
    if not reasoning_path_is_connected(candidate):
        return RejectedCandidate(
            reason="reasoning_path_not_connected",
            candidate=candidate,
            notes={"reasoning_error": "reasoning_path_not_connected"},
        )
    if not ordinal_candidate_is_safe(candidate):
        return RejectedCandidate(
            reason="ordinal_derivation_not_safe",
            candidate=candidate,
            notes={"reasoning_error": "ordinal_derivation_not_safe"},
        )
    if template.composition_style != "single_fact":
        from .models import AmbiguityResolution

        return AmbiguityResolution(
            status="resolved_by_non_temporal_descriptor",
            descriptor=candidate.source_metadata.get("question_format_args", {}).get(
                "descriptor", candidate.subject_label
            ),
            signature=candidate.source_metadata.get("required_reasoning_clues", []),
            competitor_qids=[],
        )

    search_results = client.search_entities(candidate.subject_label, limit=10)
    competitor_qids = find_exact_name_competitors(
        subject_qid=candidate.subject_qid,
        subject_label=candidate.subject_label,
        search_results=search_results,
    )
    competitor_entities = client.get_entities(competitor_qids) if competitor_qids else {}
    resolution = resolve_subject_ambiguity(candidate, template, competitor_entities)
    if resolution is None:
        return RejectedCandidate(
            reason="same_label_competitor_requires_temporal_disambiguation",
            candidate=candidate,
            notes={"competitor_qids": competitor_qids},
        )
    return resolution


def _question_must_be_non_temporal(candidate: CandidateFact) -> bool:
    """Return whether the question surface must avoid explicit temporal wording."""
    return candidate.answer_type != "Date"
