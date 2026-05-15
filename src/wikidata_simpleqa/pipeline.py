"""Pipeline for conservative single-fact and compositional multi-hop generation."""

from __future__ import annotations

from dataclasses import dataclass, field

from .canonical_questions import build_canonical_question
from .candidate_harvester import harvest_candidates
from .config import Settings
from .domain_templates import get_stage1_templates
from .io import write_jsonl
from .llm_rewrite import build_rewrite_payload, make_rewrite_client
from .models import CandidateFact, RejectedCandidate
from .route1_validators import (
    ensure_route1_subject_resource,
    validate_route1_candidate,
    validate_route1_rewritten_question,
)
from .validators import (
    question_leaks_any_answer,
    question_leaks_answer,
    question_leaks_bridge_entities,
    question_leaks_location_answer_context,
    reasoning_provenance_is_complete,
    shortcut_check,
    violates_cutoff_year_policy,
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


def run_pipeline_for_templates(
    settings: Settings,
    templates,
    client: WikidataClient | None = None,
    seen_questions: set[str] | None = None,
    seen_subject_resources: set[str] | None = None,
) -> PipelineResult:
    """Run the pipeline for an explicit template list."""
    if client is None:
        client = WikidataClient(
            user_agent=settings.user_agent,
            proxy=settings.proxy,
            timeout_seconds=settings.timeout_seconds,
            max_entity_ids_per_request=settings.wikidata_max_entity_ids_per_request,
            log_checkpoints=settings.wikidata_log_checkpoints,
            cache_dir=settings.cache_dir,
        )
    rewrite_client = None
    if settings.rewrite_enabled:
        rewrite_client = make_rewrite_client(settings.rewrite_llm, settings.timeout_seconds)
    accepted_records: list[dict] = []
    rejected_records: list[dict] = []
    if seen_questions is None:
        seen_questions = set()
    if seen_subject_resources is None:
        seen_subject_resources = set()

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
            candidate.validation_flags["no_year"] = True
            candidate.validation_flags["no_temporal_expression"] = (
                not violates_cutoff_year_policy(candidate.canonical_question, settings.cutoff_year)
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

            _apply_rewrite_if_enabled(candidate, rewrite_client, settings)
            final_question = (candidate.rewritten_question or candidate.canonical_question).strip()
            ensure_route1_subject_resource(candidate)
            if candidate.subject_resource_key in seen_subject_resources:
                rejected_records.append(
                    RejectedCandidate(
                        reason="duplicate_subject_resource",
                        candidate=candidate,
                        notes={
                            "subject_resource_url": candidate.subject_resource_url,
                            "subject_resource_key": candidate.subject_resource_key,
                        },
                    ).to_output_record()
                )
                continue
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
            seen_subject_resources.add(candidate.subject_resource_key)
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


def _apply_rewrite_if_enabled(candidate: CandidateFact, rewrite_client, settings: Settings) -> None:
    candidate.validation_flags["llm_rewrite_used"] = False
    if rewrite_client is None:
        candidate.validation_flags["rewrite_failure_reason"] = "rewrite_disabled"
        return

    payload = build_rewrite_payload(candidate)
    try:
        rewritten = rewrite_client.rewrite_question(payload)
    except Exception as exc:  # noqa: BLE001
        candidate.validation_flags["rewrite_failure_reason"] = f"rewrite_request_failed:{type(exc).__name__}"
        return
    discard_reason_value = rewritten.get("discard_reason")
    discard_reason = ""
    if discard_reason_value not in {None, ""}:
        discard_reason = str(discard_reason_value).strip()
    if discard_reason:
        candidate.validation_flags["rewrite_failure_reason"] = f"rewrite_discarded:{discard_reason}"
        return
    rewritten_question = str(
        rewritten.get("rewritten_question", rewritten.get("question", ""))
    ).strip()

    failure_reason = validate_route1_rewritten_question(
        candidate,
        payload["required_anchors"],
        rewritten_question,
        cutoff_year=settings.cutoff_year,
    )
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
    return validate_route1_rewritten_question(
        candidate,
        required_anchors,
        rewritten_question,
        cutoff_year=2025,
    )


def _validate_candidate(
    client: WikidataClient,
    settings: Settings,
    candidate: CandidateFact,
    template,
):
    return validate_route1_candidate(client, settings, candidate, template)


def _question_must_be_non_temporal(candidate: CandidateFact) -> bool:
    """Return whether the question surface must avoid explicit temporal wording."""
    return False


def _ensure_subject_resource(candidate: CandidateFact) -> None:
    """Populate a stable subject resource URL/key when missing."""
    ensure_route1_subject_resource(candidate)
