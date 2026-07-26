"""Staged multi-generator pipeline for SimpleQA-style candidate generation."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
import re
from time import perf_counter
from typing import Any

from .cheap_model_qa import make_cheap_model_qa_client
from .entity_normalization import normalize_name
from .text_normalization import build_text_matcher, display_key, text_contains_match

from .config import LLMConfig, Settings
from .domain_templates import get_stage1_templates
from .generation_models import GeneratedCandidate
from .route3_circuit import CircuitOpenError
from .route3_openrouter import (
    AbandonedExternalCallError,
    AmbiguousExternalCallError,
    DefiniteOpenRouterHTTPError,
    DefiniteOpenRouterResponseError,
    openrouter_http_failure_is_retryable,
)
from .generator_validators import (
    SearchLongtailVerifierError,
    run_search_based_longtail_verifier,
    validate_generated_candidate,
    validate_question_surface,
)
from .grading import ModelPanelMember, evaluate_model_panel, make_grader_client, summarize_panel_runs
from .generators import (
    WikidataLightGenerator,
    WikidataMultiHopJoinGenerator,
)
from .io import write_jsonl
from .llm_rewrite import make_rewrite_client
from .number_reference import NUMBER_REFERENCE_MARGIN_KEY, build_number_reference_margin
from .reasoning import normalize_reasoning_style
from .route3_quality_rules import award_year_without_month_question_reason
from .route1_multihop import ROUTE1_MULTIHOP_JOIN_ROUTE, get_route1_multihop_join_templates
from .rule_based_answer_type_gate import (
    attach_rule_based_gate_result,
    evaluate_candidate_answer_type_gate,
)
from .search_client import DuckDuckGoSearchClient
from .wikipedia_client import WikipediaClient
from .wikidata_client import WikidataClient

EARLY_REJECTION_REASONS = {
    "unsupported_relation_record",
    "entity_grounding_failed",
}
SOURCE_STAGE_REJECTION_PREFIXES = ("wikipedia_infobox_", "wikipedia_pageview_")
POST_REWRITE_SELF_CONTAIN_FORBIDDEN_PATTERNS = (
    ("list", re.compile(r"\blist\b", flags=re.IGNORECASE)),
    ("listed", re.compile(r"\blisted\b", flags=re.IGNORECASE)),
    ("example", re.compile(r"\bexample\b", flags=re.IGNORECASE)),
    ("infobox", re.compile(r"\binfobox(?:es)?\b", flags=re.IGNORECASE)),
    ("in_the_table", re.compile(r"\bin\s+the\s+table\b", flags=re.IGNORECASE)),
    ("table", re.compile(r"\btable\b", flags=re.IGNORECASE)),
)
POST_REWRITE_ANSWER_SCOPE_AMBIGUOUS_PATTERNS = (
    ("meaning", re.compile(r"\bmeaning\b", flags=re.IGNORECASE)),
    ("genre", re.compile(r"\bgenre\b", flags=re.IGNORECASE)),
    ("type", re.compile(r"\btype\b", flags=re.IGNORECASE)),
    ("average", re.compile(r"\baverage\b", flags=re.IGNORECASE)),
    ("percentage", re.compile(r"\bpercentage\b", flags=re.IGNORECASE)),
    ("classified", re.compile(r"\bclassified\b", flags=re.IGNORECASE)),
    ("what_category", re.compile(r"\bwhat\s+category\b", flags=re.IGNORECASE)),
    ("other_name", re.compile(r"\bother\s+name\b", flags=re.IGNORECASE)),
    ("translation", re.compile(r"\btranslation\b", flags=re.IGNORECASE)),
    ("transliteration", re.compile(r"\btransliteration\b", flags=re.IGNORECASE)),
    ("another_name", re.compile(r"\banother\s+name\b", flags=re.IGNORECASE)),
)
POST_REWRITE_TIME_INVARIANCE_FORBIDDEN_PATTERNS = (
    ("current", re.compile(r"\bcurrent(?:ly)?\b", flags=re.IGNORECASE)),
    ("latest", re.compile(r"\blatest\b", flags=re.IGNORECASE)),
    ("recent", re.compile(r"\brecent(?:ly)?\b", flags=re.IGNORECASE)),
)
ROUTE3_POPULAR_EXACT_ANSWERS = (
    "United States",
    "China",
    "People's Republic of China",
    "United Kingdom",
    "Russia",
    "Germany",
    "France",
    "Japan",
    "Africa",
    "Antarctica",
    "Asia",
    "Australia",
    "Europe",
    "North America",
    "Oceania",
    "South America",
    "Arctic Ocean",
    "Atlantic Ocean",
    "Indian Ocean",
    "Pacific Ocean",
    "Southern Ocean",
    "New York",
    "New York City",
    "London",
    "Paris",
    "Tokyo",
    "Beijing",
    "Los Angeles",
    "English",
    "Spanish",
    "French",
    "Mandarin Chinese",
    "Russian",
    "male",
    "female",
)
ROUTE3_POPULAR_EXACT_ANSWER_BY_NORMALIZED = {
    re.sub(r"\s+", " ", answer.strip()).casefold(): answer
    for answer in ROUTE3_POPULAR_EXACT_ANSWERS
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
    second_stage_model_clients: list[ModelPanelMember] | None = None,
    grading_grader_client=None,
) -> GenerationResult:
    """Run the staged multi-generator pipeline and write accepted/rejected outputs."""
    pipeline_start = perf_counter()
    phase_timings: dict[str, float] = {}
    if templates is None:
        templates = _default_templates_for_enabled_routes(settings)
    if wikidata_client is None:
        wikidata_client = WikidataClient(
            user_agent=settings.user_agent,
            proxy=settings.proxy,
            timeout_seconds=settings.timeout_seconds,
            max_entity_ids_per_request=settings.wikidata_max_entity_ids_per_request,
            log_checkpoints=settings.wikidata_log_checkpoints,
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
        search_client = DuckDuckGoSearchClient(**settings.duckduckgo_client_kwargs())
    rewrite_client = None
    if settings.rewrite_enabled:
        rewrite_client = make_rewrite_client(settings.rewrite_llm, settings.timeout_seconds)

    generation_start = perf_counter()
    generators = []
    if "route1_wikidata_light" in settings.enabled_routes:
        generators.append(WikidataLightGenerator())
    if ROUTE1_MULTIHOP_JOIN_ROUTE in settings.enabled_routes:
        generators.append(WikidataMultiHopJoinGenerator())

    all_generated_candidates: list[GeneratedCandidate] = []
    for generator in generators:
        all_generated_candidates.extend(generator.generate(
            templates=templates,
            settings=settings,
            client=wikidata_client,
        ))
    phase_timings["candidate_generation_seconds"] = _elapsed(generation_start)
    processing_start = perf_counter()
    result = process_generated_candidates(
        all_generated_candidates,
        settings=settings,
        search_client=search_client,
        rewrite_client=rewrite_client,
        second_stage_model_clients=second_stage_model_clients,
        grading_grader_client=grading_grader_client,
    )
    phase_timings["candidate_processing_seconds"] = _elapsed(processing_start)
    write_start = perf_counter()
    write_jsonl(settings.output_path, result.accepted)
    write_jsonl(settings.rejected_output_path, result.rejected)
    phase_timings["output_write_seconds"] = _elapsed(write_start)
    phase_timings["total_seconds"] = _elapsed(pipeline_start)
    process_telemetry = result.telemetry.copy()
    telemetry = {
        "wikidata": wikidata_client.stats_snapshot(),
        "wikipedia": wikipedia_client.request_events.copy(),
        "search": search_client.request_events.copy(),
        "enabled_routes": list(settings.enabled_routes),
        "phase_timings_seconds": phase_timings,
        "bottlenecks": _summarize_bottlenecks(phase_timings),
    }
    telemetry.update(process_telemetry.get("process_generated_candidates", {}))
    result.telemetry = telemetry
    return result


def _default_templates_for_enabled_routes(settings: Settings) -> list:
    """Return default templates compatible with the configured route set."""
    templates = []
    if (
    ):
        templates.extend(
            template
            for template in get_stage1_templates()
            if normalize_reasoning_style(template.reasoning_style or template.composition_style) == "single_fact"
        )
    if ROUTE1_MULTIHOP_JOIN_ROUTE in settings.enabled_routes:
        templates.extend(get_route1_multihop_join_templates())
    return templates


def process_generated_candidates(
    generated_candidates: list[GeneratedCandidate],
    *,
    settings: Settings,
    search_client,
    ddg_verifier_result_store=None,
    rewrite_client=None,
    second_stage_model_clients: list[ModelPanelMember] | None = None,
    grading_grader_client=None,
) -> GenerationResult:
    """Run shared filtering and rewrite over pre-generated candidates."""
    accepted_records: list[dict] = []
    rejected_records: list[dict] = []
    panel_runs: list[dict[str, object]] = []

    if second_stage_model_clients is None and settings.second_stage_grading_enabled:
        second_stage_model_clients = build_second_stage_model_panel(settings)
    if grading_grader_client is None and settings.second_stage_grading_enabled:
        grading_grader_client = build_second_stage_grader_client(settings)

    for candidate in generated_candidates:
        candidate_start = perf_counter()
        candidate_timings: dict[str, float] = {}
        early_rejection_reason = _early_rejection_reason(candidate)
        if early_rejection_reason:
            candidate_timings["total_processing_seconds"] = _elapsed(candidate_start)
            _record_candidate_timings(candidate, candidate_timings)
            rejected_records.append(
                candidate.to_rejected_record(
                    reason=early_rejection_reason,
                    notes={"source_metadata": candidate.source_metadata},
                )
            )
            continue


        rewrite_start = perf_counter()
        _apply_rewrite_if_enabled(candidate, rewrite_client, settings)
        candidate_timings["rewrite_seconds"] = _elapsed(rewrite_start)
        llm_discard_reason = str(candidate.source_metadata.get("llm_discard_reason", "")).strip()
        if llm_discard_reason:
            candidate_timings["total_processing_seconds"] = _elapsed(candidate_start)
            _record_candidate_timings(candidate, candidate_timings)
            rejected_records.append(
                candidate.to_rejected_record(
                    reason="llm_rewrite_discarded",
                    notes={"discard_reason": llm_discard_reason},
                )
            )
            continue
        answer_popularity_reason = _post_rewrite_answer_popularity_failure(candidate)
        if answer_popularity_reason is not None:
            candidate_timings["total_processing_seconds"] = _elapsed(candidate_start)
            candidate.source_metadata["surface_validation_failure_reason"] = answer_popularity_reason
            candidate.source_metadata["post_rewrite_answer_popularity_failure_reason"] = answer_popularity_reason
            candidate.validation = {
                "surface_validation_failure_reason": answer_popularity_reason,
            }
            _record_candidate_timings(candidate, candidate_timings)
            record = candidate.to_rejected_record(
                reason="rewrite_guard_rejected",
                notes={
                    "failure_reason": answer_popularity_reason,
                    "surface_validation_failure_reason": answer_popularity_reason,
                },
            )
            record["failing_reason"] = answer_popularity_reason
            rejected_records.append(record)
            continue
        self_containment_reason = _post_rewrite_self_containment_failure(candidate)
        if self_containment_reason is not None:
            candidate_timings["total_processing_seconds"] = _elapsed(candidate_start)
            candidate.source_metadata["surface_validation_failure_reason"] = self_containment_reason
            candidate.source_metadata["post_rewrite_self_containment_failure_reason"] = self_containment_reason
            candidate.validation = {
                "surface_validation_failure_reason": self_containment_reason,
            }
            _record_candidate_timings(candidate, candidate_timings)
            rejected_records.append(
                candidate.to_rejected_record(
                    reason="rewrite_guard_rejected",
                    notes={
                        "failure_reason": self_containment_reason,
                        "surface_validation_failure_reason": self_containment_reason,
                    },
                )
            )
            continue
        answer_scope_ambiguity_reason = _post_rewrite_answer_scope_ambiguity_failure(candidate)
        if answer_scope_ambiguity_reason is not None:
            candidate_timings["total_processing_seconds"] = _elapsed(candidate_start)
            candidate.source_metadata["surface_validation_failure_reason"] = answer_scope_ambiguity_reason
            candidate.source_metadata["post_rewrite_answer_scope_ambiguity_failure_reason"] = (
                answer_scope_ambiguity_reason
            )
            candidate.validation = {
                "surface_validation_failure_reason": answer_scope_ambiguity_reason,
            }
            _record_candidate_timings(candidate, candidate_timings)
            rejected_records.append(
                candidate.to_rejected_record(
                    reason="rewrite_guard_rejected",
                    notes={
                        "failure_reason": answer_scope_ambiguity_reason,
                        "surface_validation_failure_reason": answer_scope_ambiguity_reason,
                    },
                )
            )
            continue
        time_invariance_reason = _post_rewrite_time_invariance_failure(candidate)
        if time_invariance_reason is not None:
            candidate_timings["total_processing_seconds"] = _elapsed(candidate_start)
            candidate.source_metadata["surface_validation_failure_reason"] = time_invariance_reason
            candidate.source_metadata["post_rewrite_time_invariance_failure_reason"] = time_invariance_reason
            candidate.validation = {
                "surface_validation_failure_reason": time_invariance_reason,
            }
            _record_candidate_timings(candidate, candidate_timings)
            rejected_records.append(
                candidate.to_rejected_record(
                    reason="rewrite_guard_rejected",
                    notes={
                        "failure_reason": time_invariance_reason,
                        "surface_validation_failure_reason": time_invariance_reason,
                    },
                )
            )
            continue
        award_year_reason = _post_rewrite_award_year_precision_failure(candidate)
        if award_year_reason is not None:
            candidate_timings["total_processing_seconds"] = _elapsed(candidate_start)
            candidate.source_metadata["surface_validation_failure_reason"] = award_year_reason
            candidate.source_metadata["post_rewrite_award_year_precision_failure_reason"] = award_year_reason
            candidate.validation = {
                "surface_validation_failure_reason": award_year_reason,
            }
            _record_candidate_timings(candidate, candidate_timings)
            rejected_records.append(
                candidate.to_rejected_record(
                    reason="rewrite_guard_rejected",
                    notes={
                        "failure_reason": award_year_reason,
                        "surface_validation_failure_reason": award_year_reason,
                    },
                )
            )
            continue
        surface_reason = validate_question_surface(
            candidate.final_question,
            candidate,
            cutoff_year=settings.cutoff_year,
        )
        if surface_reason is not None:
            candidate_timings["total_processing_seconds"] = _elapsed(candidate_start)
            candidate.source_metadata["surface_validation_failure_reason"] = surface_reason
            candidate.validation = {
                "surface_validation_failure_reason": surface_reason,
            }
            _record_candidate_timings(candidate, candidate_timings)
            rejected_records.append(
                candidate.to_rejected_record(
                    reason="rewrite_guard_rejected",
                    notes={
                        "failure_reason": surface_reason,
                        "surface_validation_failure_reason": surface_reason,
                    },
                )
            )
            continue

        rule_gate_result = evaluate_candidate_answer_type_gate(candidate)
        attach_rule_based_gate_result(candidate, rule_gate_result)
        if not rule_gate_result.matched:
            candidate_timings["total_processing_seconds"] = _elapsed(candidate_start)
            _record_candidate_timings(candidate, candidate_timings)
            rejected_records.append(
                candidate.to_rejected_record(
                    reason="rule_based_answer_type_gate_rejected",
                    notes={
                        "rule_based_qa_gate": candidate.source_metadata["rule_based_qa_gate"],
                        "failure_reason": rule_gate_result.details.get("rule", ""),
                    },
                )
            )
            continue

        margin_start = perf_counter()
        _apply_number_reference_margin(candidate)
        candidate_timings["number_reference_margin_seconds"] = _elapsed(margin_start)

        validation_passed, validation = validate_generated_candidate(
            candidate,
            cutoff_year=settings.cutoff_year,
        )
        candidate.validation = validation
        if not validation_passed:
            candidate_timings["total_processing_seconds"] = _elapsed(candidate_start)
            _record_candidate_timings(candidate, candidate_timings)
            rejected_records.append(
                candidate.to_rejected_record(
                    reason="shared_validation_failed",
                    notes={"validation": validation},
                )
            )
            continue

        search_start = perf_counter()
        try:
            verifier = (
                ddg_verifier_result_store.verify
                if ddg_verifier_result_store is not None
                else run_search_based_longtail_verifier
            )
            search_passed, search_features = verifier(
                candidate,
                search_client=search_client,
                top_k=settings.duckduckgo_top_k,
                max_full_question_hit_rate=settings.search_longtail_max_full_question_hit_rate,
                max_keyword_hit_rate=settings.search_longtail_max_keyword_hit_rate,
                max_overall_hit_rate=settings.search_longtail_max_overall_hit_rate,
                max_parallel_queries=settings.duckduckgo_parallel_queries,
            )
            candidate_timings["duckduckgo_search_seconds"] = _elapsed(search_start)
            search_features.setdefault(
                "duration_seconds",
                candidate_timings["duckduckgo_search_seconds"],
            )
        except CircuitOpenError:
            raise
        except Exception as exc:  # noqa: BLE001
            if candidate.generation_route == "route3_wikipedia_infobox":
                raise
            candidate_timings["duckduckgo_search_seconds"] = _elapsed(search_start)
            candidate_timings["total_processing_seconds"] = _elapsed(candidate_start)
            _record_candidate_timings(candidate, candidate_timings)
            search_error_features = getattr(exc, "features", None)
            if isinstance(search_error_features, dict):
                search_error_features["duration_seconds"] = candidate_timings["duckduckgo_search_seconds"]
                candidate.search_verification_features = search_error_features
            original_error = exc.original_error if isinstance(exc, SearchLongtailVerifierError) else exc
            query_error = _first_search_query_error(search_error_features)
            notes = {
                "error_type": query_error.get("error_type") or type(original_error).__name__,
                "error_message": query_error.get("error_message") or str(original_error),
            }
            if isinstance(search_error_features, dict):
                notes["search_verification_features"] = search_error_features
            rejected_records.append(
                candidate.to_rejected_record(
                    reason="search_longtail_verifier_error",
                    notes=notes,
                )
            )
            continue
        candidate.search_verification_features = search_features
        if not search_passed:
            candidate_timings["total_processing_seconds"] = _elapsed(candidate_start)
            _record_candidate_timings(candidate, candidate_timings)
            rejected_records.append(
                candidate.to_rejected_record(
                    reason="search_longtail_verifier_rejected",
                    notes={"search_verification_features": search_features},
                )
            )
            continue

        candidate.cheap_model_verification_features = {
            "enabled": False,
            "reason": "cheap_model_longtail_rejection_removed_for_simpleqa_verified_alignment",
        }

        if settings.second_stage_grading_enabled and second_stage_model_clients:
            grading_start = perf_counter()
            try:
                panel_features = evaluate_model_panel(
                    question=candidate.final_question,
                    gold_answer=candidate.answer,
                    gold_aliases=candidate.answer_aliases,
                    answer_type=candidate.answer_type,
                    source_metadata=candidate.source_metadata,
                    model_panel=second_stage_model_clients,
                    grader_client=grading_grader_client,
                    accuracy_threshold=settings.second_stage_grading_accuracy_threshold,
                    early_stop_on_threshold=True,
                    parallel_answers=True,
                    batch_grader=True,
                )
                candidate_timings["second_stage_grading_seconds"] = _elapsed(grading_start)
                panel_features["duration_seconds"] = candidate_timings["second_stage_grading_seconds"]
            except (AmbiguousExternalCallError, CircuitOpenError):
                raise
            except DefiniteOpenRouterHTTPError as exc:
                if openrouter_http_failure_is_retryable(exc.status_code):
                    raise
                candidate_timings["second_stage_grading_seconds"] = _elapsed(grading_start)
                candidate_timings["total_processing_seconds"] = _elapsed(candidate_start)
                _record_candidate_timings(candidate, candidate_timings)
                rejected_records.append(
                    candidate.to_rejected_record(
                        reason=f"openrouter_http_error:{exc.status_code}",
                        notes={
                            "call_key": exc.call_key,
                            "request_hash": exc.request_hash,
                            "status_code": exc.status_code,
                        },
                    )
                )
                continue
            except DefiniteOpenRouterResponseError as exc:
                candidate_timings["second_stage_grading_seconds"] = _elapsed(grading_start)
                candidate_timings["total_processing_seconds"] = _elapsed(candidate_start)
                _record_candidate_timings(candidate, candidate_timings)
                rejected_records.append(
                    candidate.to_rejected_record(
                        reason="second_stage_unparseable_response",
                        notes={
                            "call_key": exc.call_key,
                            "request_hash": exc.request_hash,
                            "error_type": exc.error_type,
                            "error_message": exc.error_message,
                        },
                    )
                )
                continue
            except AbandonedExternalCallError as exc:
                candidate_timings["second_stage_grading_seconds"] = _elapsed(grading_start)
                candidate_timings["total_processing_seconds"] = _elapsed(candidate_start)
                _record_candidate_timings(candidate, candidate_timings)
                rejected_records.append(
                    candidate.to_rejected_record(
                        reason="abandoned_ambiguous_external_call",
                        notes={
                            "call_key": exc.call_key,
                            "request_hash": exc.request_hash,
                            "call_attempt": exc.call_attempt,
                        },
                    )
                )
                continue
            except Exception as exc:  # noqa: BLE001
                if candidate.generation_route == "route3_wikipedia_infobox":
                    raise
                candidate_timings["second_stage_grading_seconds"] = _elapsed(grading_start)
                candidate_timings["total_processing_seconds"] = _elapsed(candidate_start)
                _record_candidate_timings(candidate, candidate_timings)
                rejected_records.append(
                    candidate.to_rejected_record(
                        reason="second_stage_grading_error",
                        notes={"error_type": type(exc).__name__, "error_message": str(exc)},
                    )
                )
                continue
            panel_features["accuracy_threshold"] = settings.second_stage_grading_accuracy_threshold
            candidate.panel_grading_features = panel_features
            panel_runs.append(panel_features)
            if panel_features.get("accuracy", 0.0) > settings.second_stage_grading_accuracy_threshold:
                candidate_timings["total_processing_seconds"] = _elapsed(candidate_start)
                _record_candidate_timings(candidate, candidate_timings)
                rejected_records.append(
                    candidate.to_rejected_record(
                        reason="second_stage_grading_accuracy_threshold_exceeded",
                        notes={"panel_grading_features": panel_features},
                    )
                )
                continue
        else:
            candidate.panel_grading_features = {
                "enabled": False,
                "reason": "second_stage_grading_disabled_or_unconfigured",
            }

        candidate_timings["total_processing_seconds"] = _elapsed(candidate_start)
        _record_candidate_timings(candidate, candidate_timings)
        example_id = f"simpleqa_candidate_{len(accepted_records) + 1:06d}"
        accepted_records.append(candidate.to_output_record(example_id))
        if len(accepted_records) >= settings.pilot_total:
            break

    return GenerationResult(
        accepted=accepted_records,
        rejected=rejected_records,
        telemetry={
            "process_generated_candidates": {
                "generated": len(generated_candidates),
                "accepted": len(accepted_records),
                "rejected": len(rejected_records),
                "second_stage_grading_summary": summarize_panel_runs(panel_runs),
            }
        },
    )


def _elapsed(start: float) -> float:
    """Return rounded elapsed seconds from a perf_counter start."""
    return round(perf_counter() - start, 4)


def _first_search_query_error(features: Any) -> dict[str, str]:
    """Return the first query-level search error from verifier features."""
    if not isinstance(features, dict):
        return {}
    query_errors = features.get("query_errors", [])
    if not isinstance(query_errors, list) or not query_errors:
        return {}
    first_error = query_errors[0]
    if not isinstance(first_error, dict):
        return {}
    return {
        "error_type": str(first_error.get("error_type") or "").strip(),
        "error_message": str(first_error.get("error_message") or "").strip(),
    }


def _record_candidate_timings(candidate: GeneratedCandidate, timings: dict[str, float]) -> None:
    """Attach per-candidate phase timing and bottleneck metadata."""
    cleaned = {key: value for key, value in timings.items() if value >= 0.0}
    if "total_processing_seconds" in cleaned:
        cleaned.setdefault("candidate_processing_seconds", cleaned["total_processing_seconds"])
    existing = candidate.source_metadata.get("phase_timings_seconds", {})
    if isinstance(existing, dict):
        merged = {**existing, **cleaned}
    else:
        merged = cleaned
    candidate.source_metadata["phase_timings_seconds"] = merged
    candidate.source_metadata["bottlenecks"] = _summarize_bottlenecks(merged)


def _early_rejection_reason(candidate: GeneratedCandidate) -> str:
    """Return a route-local early rejection reason, if the candidate already failed."""
    for note in candidate.notes:
        if note in EARLY_REJECTION_REASONS:
            return note
        if _is_source_stage_rejection_note(note):
            return note
    return ""


def _is_source_stage_rejection_note(note: object) -> bool:
    """Return whether one candidate note is a blocking source-stage rejection."""
    text = str(note or "").strip()
    if not text:
        return False
    return text.startswith(SOURCE_STAGE_REJECTION_PREFIXES)


def _summarize_bottlenecks(timings: dict[str, float]) -> list[dict[str, float | str]]:
    """Return phase timings ordered from slowest to fastest."""
    rows = [
        {"phase": phase, "seconds": seconds}
        for phase, seconds in timings.items()
        if not phase.startswith("total") and seconds > 0.0
    ]
    return sorted(rows, key=lambda row: float(row["seconds"]), reverse=True)


def _apply_number_reference_margin(candidate: GeneratedCandidate) -> None:
    """Add SimpleQA Verified-style numeric reference metadata before model grading."""
    if candidate.answer_type != "Number":
        return
    if _looks_like_year_answer_to_temporal_question(candidate.answer, candidate.final_question):
        candidate.source_metadata[NUMBER_REFERENCE_MARGIN_KEY] = {
            "enabled": False,
            "reason": "temporal_question_year_answer_should_use_date_type",
            "original_answer": candidate.answer,
        }
        return
    candidate.source_metadata[NUMBER_REFERENCE_MARGIN_KEY] = build_number_reference_margin(
        candidate.answer,
        candidate.answer_type,
    )


def _looks_like_year_answer_to_temporal_question(answer: str, question: str) -> bool:
    """Return whether a Number answer appears to be a mislabeled year/date answer."""
    if re.fullmatch(r"\d{4}(?:\s*\W+\s*\d{2,4})?", answer.strip()) is None:
        return False
    return re.search(r"\b(year|date|day|month|when)\b", normalize_name(question)) is not None


def _post_rewrite_self_containment_failure(candidate: GeneratedCandidate) -> str | None:
    """Return a post-rewrite self-containment failure reason for table/list wording."""
    rewritten_question = str(candidate.rewritten_question or "").strip()
    if not rewritten_question:
        return None
    for label, pattern in POST_REWRITE_SELF_CONTAIN_FORBIDDEN_PATTERNS:
        if pattern.search(rewritten_question):
            return f"post_rewrite_self_containment_forbidden_phrase:{label}"
    return None


def _post_rewrite_answer_scope_ambiguity_failure(candidate: GeneratedCandidate) -> str | None:
    """Return a post-rewrite failure reason for vague answer-scope wording."""
    rewritten_question = str(candidate.rewritten_question or "").strip()
    if not rewritten_question:
        return None
    for label, pattern in POST_REWRITE_ANSWER_SCOPE_AMBIGUOUS_PATTERNS:
        if pattern.search(rewritten_question):
            return f"post_rewrite_answer_scope_ambiguous_phrase:{label}"
    return None


def _post_rewrite_time_invariance_failure(candidate: GeneratedCandidate) -> str | None:
    """Return a post-rewrite time-invariance failure reason for live-status wording."""
    rewritten_question = str(candidate.rewritten_question or "").strip()
    if not rewritten_question:
        return None
    for label, pattern in POST_REWRITE_TIME_INVARIANCE_FORBIDDEN_PATTERNS:
        if pattern.search(rewritten_question):
            return f"post_rewrite_time_invariance_forbidden_phrase:{label}"
    return None


def _post_rewrite_award_year_precision_failure(candidate: GeneratedCandidate) -> str | None:
    """Return a post-rewrite failure reason for award questions asking only for a year."""
    reason = award_year_without_month_question_reason(candidate.final_question)
    return reason or None


def _post_rewrite_answer_popularity_failure(candidate: GeneratedCandidate) -> str | None:
    """Return a Route 3 failure reason when the exact answer is too popular."""
    if candidate.generation_route != "route3_wikipedia_infobox":
        return None
    normalized_answer = re.sub(r"\s+", " ", str(candidate.answer or "").strip()).casefold()
    if not normalized_answer:
        return None
    popular_answer = ROUTE3_POPULAR_EXACT_ANSWER_BY_NORMALIZED.get(normalized_answer)
    if popular_answer is None:
        return None
    return f"answer_too_popular:{popular_answer}"


def _apply_rewrite_if_enabled(candidate: GeneratedCandidate, rewrite_client, settings: Settings) -> None:
    """Optionally rewrite one candidate into a more natural final question."""
    if rewrite_client is None:
        candidate.notes.append("rewrite_disabled")
        return
    forbidden_patterns = ["current", "currently", "latest", "most recent", "as of now"]
    payload = _build_route_rewrite_payload(
        candidate,
        settings.cutoff_year,
        forbidden_patterns,
        search_query_count=settings.generated_search_query_count,
    )
    try:
        if hasattr(rewrite_client, "rewrite_question_with_audit"):
            rewrite_audit = rewrite_client.rewrite_question_with_audit(payload)
            candidate.source_metadata["small_model_rewrite_audit"] = rewrite_audit
            rewritten = dict(rewrite_audit.get("parsed_response", {}))
        else:
            rewritten = rewrite_client.rewrite_question(payload)
    except Exception as exc:  # noqa: BLE001
        candidate.notes.append(f"rewrite_failed:{type(exc).__name__}")
        return
    candidate.source_metadata["small_model_rewrite_response"] = rewritten
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
    llm_answer_aliases = _sanitize_rewrite_answer_aliases(
        rewritten.get("answer_aliases", []),
        canonical_answer=candidate.answer,
    )
    if llm_answer_aliases:
        candidate.source_metadata["llm_answer_aliases"] = llm_answer_aliases
        candidate.answer_aliases = _merge_answer_aliases(candidate.answer_aliases, llm_answer_aliases)
    raw_search_queries = rewritten.get("search_queries", [])
    if isinstance(raw_search_queries, list):
        blocked_matchers = [
            matcher
            for raw_value in [candidate.answer, *candidate.answer_aliases]
            if (matcher := build_text_matcher(raw_value)) is not None
        ]
        normalized_final_question = display_key(candidate.rewritten_question or "")
        candidate.search_queries = [
            str(query).strip()
            for query in raw_search_queries
            if str(query).strip()
            and display_key(str(query)) != normalized_final_question
            and not any(text_contains_match(str(query), matcher) for matcher in blocked_matchers)
        ]


def _sanitize_rewrite_answer_aliases(raw_aliases, *, canonical_answer: str) -> list[str]:
    """Normalize aliases returned by the rewrite model for snippet matching."""
    if not isinstance(raw_aliases, list):
        return []
    canonical_normalized = display_key(canonical_answer)
    aliases: list[str] = []
    seen: set[str] = set()
    for value in raw_aliases:
        alias = str(value).strip()
        normalized_alias = display_key(alias)
        if not alias or not normalized_alias or normalized_alias == canonical_normalized:
            continue
        if normalized_alias in seen:
            continue
        seen.add(normalized_alias)
        aliases.append(alias)
    return aliases


def _merge_answer_aliases(existing_aliases: list[str], new_aliases: list[str]) -> list[str]:
    """Merge answer aliases while preserving order and normalized uniqueness."""
    merged: list[str] = []
    seen: set[str] = set()
    for value in [*existing_aliases, *new_aliases]:
        alias = str(value).strip()
        normalized_alias = display_key(alias)
        if not alias or not normalized_alias or normalized_alias in seen:
            continue
        seen.add(normalized_alias)
        merged.append(alias)
    return merged


def _build_route_rewrite_payload(
    candidate: GeneratedCandidate,
    cutoff_year: int,
    forbidden_patterns: list[str],
    *,
    search_query_count: int,
) -> dict[str, object]:
    """Build a shared rewrite payload with route-specific inputs."""
    payload: dict[str, object] = {
        "canonical_question": candidate.question,
        "answer_labels": [candidate.answer],
        "answer_aliases": candidate.answer_aliases,
        "answer_type": candidate.answer_type,
        "required_anchors": [candidate.subject_entity.name],
        "domain": candidate.source_template_domain,
        "target_property": candidate.relation_or_claim,
        "cutoff_year": cutoff_year,
        "forbidden_patterns": forbidden_patterns,
        "search_query_count": search_query_count,
    }
    extra_prompts = candidate.source_metadata.get("extra_prompts", [])
    if isinstance(extra_prompts, list) and extra_prompts:
        payload["extra_prompts"] = [str(value) for value in extra_prompts if str(value).strip()]
    source_candidate = candidate.source_candidate
    if candidate.generation_route in {
        "route1_wikidata_light",
        ROUTE1_MULTIHOP_JOIN_ROUTE,
    } and source_candidate is not None:
        payload.update(
            {
                "task_type": "route1_question_and_queries",
                "wikidata_triplet_text": (
                    f"{source_candidate.subject_label} -- {source_candidate.target_property_label} -- "
                    f"{source_candidate.answer_labels[0] if source_candidate.answer_labels else ''}"
                ).strip(),
            }
        )
        if candidate.generation_route == ROUTE1_MULTIHOP_JOIN_ROUTE:
            payload.update(
                {
                    "reasoning_style": source_candidate.reasoning_style,
                    "hop_count": source_candidate.hop_count,
                    "reasoning_path": source_candidate.reasoning_path,
                    "bridge_entities": source_candidate.bridge_entities,
                    "required_reasoning_clues": source_candidate.source_metadata.get(
                        "required_reasoning_clues",
                        [],
                    ),
                    "route_contract": "route1_qid_first_multihop_join",
                }
            )
        return payload
    payload["task_type"] = "generic_question_and_queries"
    return payload



def build_second_stage_model_panel(settings: Settings) -> list[ModelPanelMember]:
    """Construct the configured second-stage answer-model panel."""
    members: list[ModelPanelMember] = []
    for config in settings.second_stage_grading_models:
        resolved = _resolve_llm_config(config, settings)
        if resolved is None:
            continue
        client = make_cheap_model_qa_client(resolved, settings.timeout_seconds)
        if client is None:
            continue
        members.append(ModelPanelMember(name=resolved.model, client=client))
    return members


def build_second_stage_grader_client(settings: Settings):
    """Construct the configured second-stage grader client."""
    return make_grader_client(
        _resolve_llm_config(settings.second_stage_grading_grader_llm, settings),
        settings.timeout_seconds,
    ) if settings.second_stage_grading_grader_llm is not None else None


def _build_second_stage_model_panel(settings: Settings) -> list[ModelPanelMember]:
    """Backward-compatible alias for the public panel builder."""
    return build_second_stage_model_panel(settings)


def _resolve_llm_config(config: LLMConfig | None, settings: Settings) -> LLMConfig | None:
    """Fill in inherited runtime fields for one LLM config."""
    if config is None:
        return None
    if config.proxy is not None:
        return config
    return replace(config, proxy=settings.proxy)
