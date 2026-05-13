"""Staged multi-generator pipeline for SimpleQA-style candidate generation."""

from __future__ import annotations

from dataclasses import dataclass, field

from .entity_normalization import normalize_name

from .config import Settings
from .domain_templates import get_stage1_templates
from .generation_models import GeneratedCandidate
from .generator_validators import (
    run_fact_level_longtail_prefilter,
    run_search_based_longtail_verifier,
    validate_generated_candidate,
    validate_question_surface,
)
from .generators import WikidataLightGenerator, WikidataWikipediaHybridGenerator
from .io import write_jsonl
from .llm_rewrite import make_rewrite_client
from .reasoning import normalize_reasoning_style
from .search_client import DuckDuckGoSearchClient
from .wikipedia_client import WikipediaClient
from .wikidata_client import WikidataClient

EARLY_REJECTION_REASONS = {
    "unsupported_relation_record",
    "entity_grounding_failed",
}


@dataclass(slots=True)
class GenerationResult:
    """Accepted and rejected outputs from the new generation pipeline."""

    accepted: list[dict] = field(default_factory=list)
    rejected: list[dict] = field(default_factory=list)
    telemetry: dict = field(default_factory=dict)


def run_generation_pipeline(
    settings: Settings,
    *,
    templates=None,
    wikidata_client: WikidataClient | None = None,
    wikipedia_client: WikipediaClient | None = None,
    search_client: DuckDuckGoSearchClient | None = None,
) -> GenerationResult:
    """Run the staged multi-generator pipeline and write accepted/rejected outputs."""
    if templates is None:
        templates = [
            template
            for template in get_stage1_templates()
            if normalize_reasoning_style(template.reasoning_style or template.composition_style) == "single_fact"
        ]
    if wikidata_client is None:
        wikidata_client = WikidataClient(
            user_agent=settings.user_agent,
            proxy=settings.proxy,
            timeout_seconds=settings.timeout_seconds,
            cache_dir=settings.cache_dir,
        )
    if wikipedia_client is None:
        wikipedia_client = WikipediaClient(
            user_agent=settings.user_agent,
            proxy=settings.proxy,
            timeout_seconds=settings.timeout_seconds,
            cache_dir=settings.cache_dir,
        )
    if search_client is None:
        search_client = DuckDuckGoSearchClient(
            user_agent=settings.user_agent,
            proxy=settings.proxy,
            timeout_seconds=settings.timeout_seconds,
            cache_dir=settings.cache_dir,
        )
    rewrite_client = None
    if settings.rewrite_enabled:
        rewrite_client = make_rewrite_client(settings.rewrite_llm, settings.timeout_seconds)

    generators = []
    if "route2_wikidata_wikipedia_hybrid" in settings.enabled_routes:
        generators.append(WikidataWikipediaHybridGenerator(wikipedia_client=wikipedia_client))
    if "route1_wikidata_light" in settings.enabled_routes:
        generators.append(WikidataLightGenerator())

    all_generated_candidates: list[GeneratedCandidate] = []
    for generator in generators:
        all_generated_candidates.extend(generator.generate(
            templates=templates,
            settings=settings,
            client=wikidata_client,
        ))
    result = process_generated_candidates(
        all_generated_candidates,
        settings=settings,
        search_client=search_client,
        rewrite_client=rewrite_client,
    )
    write_jsonl(settings.output_path, result.accepted)
    write_jsonl(settings.rejected_output_path, result.rejected)
    telemetry = {
        "wikidata": wikidata_client.stats_snapshot(),
        "wikipedia": wikipedia_client.request_events.copy(),
        "search": search_client.request_events.copy(),
        "enabled_routes": list(settings.enabled_routes),
    }
    result.telemetry = telemetry
    return result


def process_generated_candidates(
    generated_candidates: list[GeneratedCandidate],
    *,
    settings: Settings,
    search_client,
    rewrite_client=None,
) -> GenerationResult:
    """Run shared filtering, rewrite, and dedup over pre-generated candidates."""
    accepted_records: list[dict] = []
    rejected_records: list[dict] = []
    seen_questions: set[str] = set()
    seen_subject_resources: set[str] = set()

    for candidate in generated_candidates:
        early_rejection_reason = next(
            (note for note in candidate.notes if note in EARLY_REJECTION_REASONS),
            "",
        )
        if early_rejection_reason:
            rejected_records.append(
                candidate.to_rejected_record(
                    reason=early_rejection_reason,
                    notes={"source_metadata": candidate.source_metadata},
                )
            )
            continue

        prefilter_passed, prefilter_features = run_fact_level_longtail_prefilter(
            candidate,
            max_sitelinks=settings.longtail_prefilter_max_sitelinks,
            max_claims=settings.longtail_prefilter_max_claims,
        )
        candidate.prefilter_longtail_features = prefilter_features
        if not prefilter_passed:
            rejected_records.append(
                candidate.to_rejected_record(
                    reason="longtail_prefilter_rejected",
                    notes={"prefilter_longtail_features": prefilter_features},
                )
            )
            continue

        _apply_rewrite_if_enabled(candidate, rewrite_client, settings)
        llm_discard_reason = str(candidate.source_metadata.get("llm_discard_reason", "")).strip()
        if llm_discard_reason:
            rejected_records.append(
                candidate.to_rejected_record(
                    reason="llm_rewrite_discarded",
                    notes={"discard_reason": llm_discard_reason},
                )
            )
            continue
        surface_reason = validate_question_surface(
            candidate.final_question,
            candidate,
            cutoff_year=settings.cutoff_year,
        )
        if surface_reason is not None:
            rejected_records.append(
                candidate.to_rejected_record(
                    reason="rewrite_guard_rejected",
                    notes={"failure_reason": surface_reason},
                )
            )
            continue

        try:
            search_passed, search_features = run_search_based_longtail_verifier(
                candidate,
                search_client=search_client,
                top_k=settings.duckduckgo_top_k,
                max_full_question_hit_rate=settings.search_longtail_max_full_question_hit_rate,
                max_keyword_hit_rate=settings.search_longtail_max_keyword_hit_rate,
                max_overall_hit_rate=settings.search_longtail_max_overall_hit_rate,
            )
        except Exception as exc:  # noqa: BLE001
            rejected_records.append(
                candidate.to_rejected_record(
                    reason="search_longtail_verifier_error",
                    notes={"error_type": type(exc).__name__, "error_message": str(exc)},
                )
            )
            continue
        candidate.search_verification_features = search_features
        if not search_passed:
            rejected_records.append(
                candidate.to_rejected_record(
                    reason="search_longtail_verifier_rejected",
                    notes={"search_verification_features": search_features},
                )
            )
            continue

        validation_passed, validation = validate_generated_candidate(
            candidate,
            cutoff_year=settings.cutoff_year,
        )
        candidate.validation = validation
        if not validation_passed:
            rejected_records.append(
                candidate.to_rejected_record(
                    reason="shared_validation_failed",
                    notes={"validation": validation},
                )
            )
            continue

        subject_resource_key = candidate.subject_resource_key
        final_question = candidate.final_question
        if subject_resource_key and subject_resource_key in seen_subject_resources:
            rejected_records.append(
                candidate.to_rejected_record(
                    reason="duplicate_subject_resource",
                    notes={"subject_resource_key": subject_resource_key},
                )
            )
            continue
        if final_question in seen_questions:
            rejected_records.append(
                candidate.to_rejected_record(
                    reason="duplicate_question",
                    notes={"question": final_question},
                )
            )
            continue

        seen_questions.add(final_question)
        if subject_resource_key:
            seen_subject_resources.add(subject_resource_key)
        example_id = f"simpleqa_candidate_{len(accepted_records) + 1:06d}"
        accepted_records.append(candidate.to_output_record(example_id))
        if len(accepted_records) >= settings.pilot_total:
            break

    return GenerationResult(
        accepted=accepted_records,
        rejected=rejected_records,
        telemetry={},
    )


def _apply_rewrite_if_enabled(candidate: GeneratedCandidate, rewrite_client, settings: Settings) -> None:
    """Optionally rewrite one candidate into a more natural final question."""
    if rewrite_client is None:
        candidate.notes.append("rewrite_disabled")
        return
    forbidden_patterns = ["current", "currently", "latest", "most recent", "as of now"]
    payload = {
        "canonical_question": candidate.question,
        "answer_labels": [candidate.answer],
        "answer_aliases": candidate.answer_aliases,
        "required_anchors": [candidate.subject_entity.name],
        "domain": candidate.source_template_domain,
        "target_property": candidate.relation_or_claim,
        "cutoff_year": settings.cutoff_year,
        "forbidden_patterns": forbidden_patterns,
    }
    if candidate.generation_route == "kelm_bootstrap_half_pipeline":
        payload = {
            "task_type": "kelm_question_and_queries",
            "serialized_triple": candidate.source_metadata.get("kelm_serialized_triples", ""),
            "kelm_sentence": candidate.source_metadata.get("kelm_sentence", ""),
            "answer": candidate.answer,
            "answer_aliases": candidate.answer_aliases,
            "forbidden_patterns": forbidden_patterns,
            "cutoff_year": settings.cutoff_year,
        }
    try:
        rewritten = rewrite_client.rewrite_question(payload)
    except Exception as exc:  # noqa: BLE001
        candidate.notes.append(f"rewrite_failed:{type(exc).__name__}")
        return
    discard_reason_value = rewritten.get("discard_reason")
    discard_reason = ""
    if discard_reason_value not in {None, ""}:
        discard_reason = str(discard_reason_value).strip()
    if discard_reason:
        candidate.source_metadata["llm_discard_reason"] = discard_reason
    rewritten_question = str(
        rewritten.get("rewritten_question", rewritten.get("question", ""))
    ).strip()
    if rewritten_question:
        candidate.rewritten_question = rewritten_question
    raw_search_queries = rewritten.get("search_queries", [])
    if isinstance(raw_search_queries, list):
        blocked_strings = {
            normalize_name(candidate.answer),
            *{
                normalize_name(alias)
                for alias in candidate.answer_aliases
                if normalize_name(alias)
            },
        }
        normalized_final_question = normalize_name(candidate.rewritten_question or "")
        candidate.search_queries = [
            str(query).strip()
            for query in raw_search_queries
            if str(query).strip()
            and normalize_name(str(query)) != normalized_final_question
            and not any(
                blocked and blocked in normalize_name(str(query))
                for blocked in blocked_strings
            )
        ]
