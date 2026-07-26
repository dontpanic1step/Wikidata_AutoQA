"""Run one internal Route 3 table-search segment for the formal recipe."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter, defaultdict
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from json import JSONDecodeError
from pathlib import Path
from threading import Lock, Semaphore
from time import perf_counter, sleep

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.cli_output import print_json_summary
from wikidata_simpleqa.config import LLMConfig, Settings
from wikidata_simpleqa.generation_models import GeneratedCandidate
from wikidata_simpleqa.generator_validators import SearchLongtailVerifierError
from wikidata_simpleqa.route3_post_generation import process_route3_candidates
from wikidata_simpleqa.grading import ModelPanelMember
from wikidata_simpleqa.page_id_lists import (
    PageIdListEntry,
    build_page_id_entries,
)
from wikidata_simpleqa.route3_circuit import CircuitOpenError, ServiceCircuit
from wikidata_simpleqa.route3_ddg import Route3DDGVerifierResultStore
from wikidata_simpleqa.route3_external_lifecycle import scan_ambiguous_external_calls
from wikidata_simpleqa.route3_ids import assign_unique_route3_record_ids, route3_record_id
from wikidata_simpleqa.route3_openrouter import (
    AbandonedExternalCallError,
    AmbiguousExternalCallError,
    DefiniteOpenRouterHTTPError,
    DefiniteOpenRouterResponseError,
    Route3OpenRouterClientFactory,
    openrouter_http_failure_is_retryable,
    bind_route3_allocation_client,
    bind_route3_allocation_panel,
)
from wikidata_simpleqa.route3_run_ledger import (
    SegmentLedgerIndex,
    atomic_write_json,
    derived_records,
    ledger_summary,
    load_segment_manifest,
    rebuild_derived_outputs,
    recover_stream_state_from_ledger,
)
from wikidata_simpleqa.search_cli import (
    add_duckduckgo_transport_args,
    duckduckgo_settings_kwargs,
    duckduckgo_summary_fields,
)
from wikidata_simpleqa.search_client import DuckDuckGoSearchClient
from wikidata_simpleqa.wikipedia_client import WikipediaClient, normalize_wikipedia_page_id, normalize_wikipedia_title
from wikidata_simpleqa.wikipedia_infobox_generator import (
    DEFAULT_ROUTE3_ANSWER_TYPE_MODE,
    DEFAULT_ROUTE3_INFOBOX_MAX_REMOVED_ROW_RATE,
    DEFAULT_ROUTE3_INFOBOX_MIN_REMAINING_ROWS,
    DEFAULT_ROUTE3_PAGE_ARCHIVE_DIR,
    DEFAULT_ROUTE3_REASONING_TYPES,
    DEFAULT_ROUTE3_TABLE_FILTER_MODES,
    DEFAULT_ROUTE3_TABLE_SOURCE_TYPES,
    ROUTE3_ANSWER_TYPES,
    WikipediaInfoboxTableGenerator,
    _answer_items,
    _normalize_answer_type,
    _normalize_generated_answer,
    _sanitize_answer_blind_queries,
    normalize_route3_answer_types,
    normalize_route3_answer_type_mode,
    normalize_route3_table_source_types,
)
from wikidata_simpleqa.wikipedia_streaming import (
    DEFAULT_TABLE_SEARCH_QUERIES,
    PageIdStreamState,
    build_pageid_url,
)

from wikidata_simpleqa.route3_worker_support import (
    EndpointResumeState,
    aggregate_phase_timings,
    effective_stream_random_seed,
    ensure_page_id_list_entry_metadata,
    exact_failure_reason,
    failure_reason_counts,
    llm_generation_table_yield_summary,
    load_endpoint_jsonl,
    normalize_stream_fresh_cached_page_count,
    normalize_stream_reuse_cached_page_count,
    phase_timing_stats,
    positive_record_page_id,
    record_answer_type,
    record_page_id,
    record_table_type,
    run_group_id,
    run_segment_id,
    safe_artifact_id,
    source_stage_rejection_reason,
    stream_budget_numeric_count,
    survival_by_layer,
    write_stream_walkthrough,
)



def _apply_big_batch_mode(args: argparse.Namespace) -> None:
    """Apply large-run defaults that keep 10k-style recipes resumable."""
    if not getattr(args, "big_batch_mode", False):
        return
    args.stream_batch_size = max(1, int(getattr(args, "stream_search_limit", 50) or 50))
    args.stream_search_max_rounds = max(500, int(getattr(args, "stream_search_max_rounds", 10) or 10))


@dataclass(slots=True)
class UrlEntry:
    """One Wikipedia URL and its optional broad content domain."""

    url: str
    domain: str = ""
    subdomain: str = ""


@dataclass(frozen=True, slots=True)
class CachedPageArchiveEntry:
    """One reusable Route 3 parsed page archive."""

    page_id: int
    source_url: str
    archive_path: Path


@dataclass(slots=True)
class StreamingConcurrencyContext:
    """Shared locks and service limits for page-id streaming."""

    commit_lock: Lock
    wikipedia_semaphore: Semaphore
    duckduckgo_semaphore: Semaphore
    generation_rewrite_semaphore: Semaphore
    second_stage_semaphore: Semaphore


class SemaphoreWrappedClient:
    """Proxy a client and bound selected method calls with a semaphore."""

    def __init__(self, client, semaphore: Semaphore, methods: set[str]) -> None:
        self._client = client
        self._semaphore = semaphore
        self._methods = methods

    def __getattr__(self, name: str):
        attr = getattr(self._client, name)
        if name not in self._methods or not callable(attr):
            return attr

        def wrapped(*args, **kwargs):
            with self._semaphore:
                return attr(*args, **kwargs)

        return wrapped








def _run_artifact_manifest_path(args: argparse.Namespace, run_group_id: str) -> Path | None:
    """Return the manifest path for a run group, if artifact indexing is enabled."""
    if not run_group_id:
        return None
    explicit_path = getattr(args, "run_artifact_manifest", None)
    if explicit_path is not None:
        return Path(explicit_path)
    return ROOT / "outputs" / "run_manifests" / f"{run_group_id}.json"


def _run_artifact_summary(args: argparse.Namespace) -> dict[str, str]:
    """Return summary fields that identify the artifact group and segment."""
    artifact_group_id = run_group_id(args)
    if not artifact_group_id:
        return {}
    manifest_path = _run_artifact_manifest_path(args, artifact_group_id)
    return {
        "run_group_id": artifact_group_id,
        "run_segment_id": run_segment_id(args),
        "run_artifact_manifest": str(manifest_path) if manifest_path is not None else "",
    }






def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the Wikipedia table route."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stream-state",
        type=Path,
        default=ROOT / "outputs" / "wikipedia_infobox_stream_state.json",
        help="Persistent discovery offsets and non-authoritative streaming telemetry.",
    )
    parser.add_argument("--stream-search-limit", type=int, default=50)
    parser.add_argument("--stream-search-max-rounds", type=int, default=10)
    parser.add_argument(
        "--stream-search-initial-offset",
        type=int,
        default=0,
        help=(
            "Initial Wikipedia search offset for table-search streaming. "
            "Useful for recipe segments with separate stream states."
        ),
    )
    parser.add_argument(
        "--stream-random-seed",
        type=int,
        default=None,
        help=(
            "Segment seed recorded for reproducibility. When omitted, a deterministic seed is derived "
            "from the run and segment identity."
        ),
    )
    parser.add_argument("--stream-batch-size", type=int, default=10)
    parser.add_argument(
        "--stream-discovery-max-retries",
        type=int,
        default=5,
        help="Retry count for transient table-search discovery errors before ending a streaming segment.",
    )
    parser.add_argument(
        "--stream-discovery-retry-backoff-seconds",
        type=float,
        default=10.0,
        help="Initial sleep before retrying a failed table-search discovery request.",
    )
    parser.add_argument(
        "--stream-discovery-retry-max-sleep-seconds",
        type=float,
        default=60.0,
        help="Maximum sleep between table-search discovery retries.",
    )
    parser.add_argument(
        "--stream-page-workers",
        type=int,
        default=4,
        help="Concurrent page IDs to process in streaming mode. Accepted-target runs stay sequential.",
    )
    parser.add_argument(
        "--wikipedia-concurrency-limit",
        type=int,
        default=4,
        help="Maximum concurrent Wikipedia API calls in streaming mode.",
    )
    parser.add_argument(
        "--duckduckgo-concurrency-limit",
        type=int,
        default=4,
        help="Maximum concurrent DuckDuckGo searches across streaming workers.",
    )
    parser.add_argument(
        "--openrouter-generation-rewrite-concurrency-limit",
        type=int,
        default=10,
        help="Maximum concurrent OpenRouter generation/rewrite calls across streaming workers.",
    )
    parser.add_argument(
        "--second-stage-concurrency-limit",
        type=int,
        default=10,
        help="Maximum concurrent second-stage answer/grader OpenRouter calls across streaming workers.",
    )
    parser.add_argument(
        "--stream-reuse-cached-page-count",
        default="all",
        help=(
            "Process this many already parsed Route 3 page archives from --route3-page-archive-dir, "
            "or 'all' to reuse cached pages until the stream target is met or reusable cache is exhausted."
        ),
    )
    parser.add_argument(
        "--stream-fresh-cached-page-count",
        default="fill",
        help=(
            "Discover, fetch, and cache this many fresh streaming pages after cached-page reuse, "
            "or 'fill' to request fresh pages until the stream target is met."
        ),
    )
    parser.add_argument(
        "--stream-page-processing-target",
        type=int,
        default=0,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--page-allocation-ledger-dir",
        type=Path,
        required=True,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--page-attempt-ledger-dir",
        type=Path,
        required=True,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--run-group-segments-dir",
        type=Path,
        required=True,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--external-call-record-dir",
        type=Path,
        required=True,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--ddg-verifier-result-dir",
        type=Path,
        required=True,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--reset-stream-state",
        action="store_true",
        help="Start streaming from a new empty state file. Use only for a new run, not endpoint resume or rerun-pool-only.",
    )
    parser.add_argument(
        "--walkthrough-output",
        type=Path,
        default=None,
        help="Optional markdown walkthrough with survival rates, failure reasons, and timings.",
    )
    parser.add_argument(
        "--start-from-endpoint",
        action="store_true",
        help=(
            "Resume from existing accepted/rejected endpoint JSONL files. "
            "Streaming mode syncs page-ID state and processes the remaining total; URL mode skips completed URLs and appends."
        ),
    )
    parser.add_argument(
        "--run-group-id",
        type=str,
        default="",
        help="Stable artifact group ID shared by resumed segments of the same run.",
    )
    parser.add_argument(
        "--run-segment-id",
        type=str,
        default="",
        help="Unique segment ID for this invocation. Defaults to the summary-output stem.",
    )
    parser.add_argument(
        "--run-artifact-manifest",
        type=Path,
        default=None,
        help="JSON manifest that indexes all artifacts for --run-group-id.",
    )
    parser.add_argument(
        "--run-artifact-include-summary",
        action="append",
        type=Path,
        default=[],
        help="Existing segment summary JSON to include in the run-group artifact manifest. Can be repeated.",
    )
    parser.add_argument("--record-limit", type=int, default=10)
    parser.add_argument("--run-date", type=str, default=None)
    parser.add_argument("--cutoff-year", type=int, default=2025)
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--duckduckgo-top-k", type=int, default=5)
    parser.add_argument("--duckduckgo-parallel-queries", type=int, default=3)
    add_duckduckgo_transport_args(parser)
    parser.add_argument("--generated-search-query-count", type=int, default=2)
    parser.add_argument(
        "--route3-answer-type",
        action="append",
        default=[],
        help=(
            "Restrict Route 3 generation to one or more SimpleQA Verified answer_type values: "
            "Person, Place, Number, Date, Other. Repeat the flag or pass comma-separated values. Default: unrestricted."
        ),
    )
    parser.add_argument(
        "--route3-answer-type-mode",
        choices=["single", "all5"],
        default=DEFAULT_ROUTE3_ANSWER_TYPE_MODE,
        help=(
            "Route 3 small-model output mode. single asks for one QA; all5 asks once for up to one "
            "Person, Place, Number, Date, and Other QA slot."
        ),
    )
    parser.add_argument(
        "--route3-table-source-type",
        action="append",
        default=[],
        help=(
            "Restrict Route 3 generation source tables to infobox, wikitable, or both/all. "
            "Repeat the flag or pass comma-separated values. Default: both."
        ),
    )
    parser.add_argument(
        "--route3-page-archive-dir",
        type=Path,
        default=ROOT / DEFAULT_ROUTE3_PAGE_ARCHIVE_DIR,
        help="Directory for unified Route 3 page archives containing parse HTML and table metadata.",
    )
    parser.add_argument(
        "--route3-infobox-max-removed-row-rate",
        type=float,
        default=DEFAULT_ROUTE3_INFOBOX_MAX_REMOVED_ROW_RATE,
        help="Reject infoboxes when row cleanup removes more than this fraction of non-header rows.",
    )
    parser.add_argument(
        "--route3-infobox-min-remaining-rows",
        type=int,
        default=DEFAULT_ROUTE3_INFOBOX_MIN_REMAINING_ROWS,
        help="Reject infoboxes when row cleanup leaves fewer than this many non-header rows.",
    )
    parser.add_argument(
        "--compact-rejected-output",
        action="store_true",
        help="Deprecated for Route 3; rejected JSONL records are always written in full audit form.",
    )
    parser.add_argument(
        "--compact-output",
        action="store_true",
        help="Deprecated for Route 3; accepted and rejected JSONL records are always written in full audit form.",
    )
    parser.add_argument(
        "--big-batch-mode",
        action="store_true",
        help=(
            "Large-run convenience mode: retry discovery failures and align stream batch size with the table-search page size. "
            "It does not compact accepted or rejected records."
        ),
    )
    parser.add_argument(
        "--wikipedia-429-backoff-seconds",
        type=float,
        default=30.0,
        help="Shared polite sleep after Wikipedia returns HTTP 429 before later Wikipedia requests continue.",
    )
    parser.add_argument(
        "--wikipedia-429-max-backoff-seconds",
        type=float,
        default=300.0,
        help="Maximum shared Wikipedia HTTP 429 backoff sleep.",
    )
    parser.add_argument(
        "--wikipedia-429-recovery-seconds",
        type=float,
        default=120.0,
        help="Quiet period after which successful Wikipedia requests reset the shared HTTP 429 backoff.",
    )
    parser.add_argument("--proxy", type=str, default="none")
    parser.add_argument("--small-model-provider", type=str, default="openrouter")
    parser.add_argument("--generation-model", dest="generation_model", type=str, default="google/gemini-3-flash-preview")
    parser.add_argument(
        "--small-model",
        dest="generation_model",
        type=str,
        default=argparse.SUPPRESS,
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--small-model-api-key-env", type=str, default="OPENROUTER_API_KEY")
    parser.add_argument("--small-model-base-url", type=str, default="https://openrouter.ai/api/v1")
    parser.add_argument("--small-model-max-tokens", type=int, default=4096)
    parser.add_argument("--enable-second-stage-grading", action="store_true", default=True)
    parser.add_argument("--second-stage-grading-accuracy-threshold", type=float, default=0.1)
    parser.add_argument("--search-longtail-max-full-question-hit-rate", type=float, default=0.3)
    parser.add_argument("--search-longtail-max-keyword-hit-rate", type=float, default=0.3)
    parser.add_argument("--search-longtail-max-overall-hit-rate", type=float, default=0.3)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs" / "wikipedia_infobox_accepted.jsonl",
    )
    parser.add_argument(
        "--rejected-output",
        type=Path,
        default=ROOT / "outputs" / "wikipedia_infobox_rejected.jsonl",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=ROOT / "outputs" / "wikipedia_infobox_summary.json",
    )
    args = parser.parse_args()
    args.stream_page_source = "table-search"
    args.route3_table_filter_mode = list(DEFAULT_ROUTE3_TABLE_FILTER_MODES)
    args.route3_prose_leakage_scoring = True
    return args


def main() -> int:
    """Run the Wikipedia table route and persist outputs."""
    args = parse_args()
    _apply_big_batch_mode(args)
    endpoint_resume = _load_endpoint_resume(args)
    args.stream_random_seed_was_explicit = args.stream_random_seed is not None
    args.stream_random_seed = effective_stream_random_seed(args, endpoint_resume)
    effective_record_limit = args.record_limit
    if args.stream_batch_size < 1:
        raise ValueError("--stream-batch-size must be at least 1.")
    if args.stream_search_limit < 1:
        raise ValueError("--stream-search-limit must be at least 1.")
    if args.stream_search_max_rounds < 1:
        raise ValueError("--stream-search-max-rounds must be at least 1.")
    if args.stream_discovery_max_retries < 0:
        raise ValueError("--stream-discovery-max-retries must be non-negative.")
    if args.stream_discovery_retry_backoff_seconds < 0:
        raise ValueError("--stream-discovery-retry-backoff-seconds must be non-negative.")
    if args.stream_discovery_retry_max_sleep_seconds < 0:
        raise ValueError("--stream-discovery-retry-max-sleep-seconds must be non-negative.")
    if args.stream_page_workers < 1:
        raise ValueError("--stream-page-workers must be at least 1.")
    if args.wikipedia_concurrency_limit < 1:
        raise ValueError("--wikipedia-concurrency-limit must be at least 1.")
    if args.duckduckgo_concurrency_limit < 1:
        raise ValueError("--duckduckgo-concurrency-limit must be at least 1.")
    if args.openrouter_generation_rewrite_concurrency_limit < 1:
        raise ValueError("--openrouter-generation-rewrite-concurrency-limit must be at least 1.")
    if args.second_stage_concurrency_limit < 1:
        raise ValueError("--second-stage-concurrency-limit must be at least 1.")
    if args.wikipedia_429_backoff_seconds < 0:
        raise ValueError("--wikipedia-429-backoff-seconds must be non-negative.")
    if args.wikipedia_429_max_backoff_seconds < 0:
        raise ValueError("--wikipedia-429-max-backoff-seconds must be non-negative.")
    if args.wikipedia_429_recovery_seconds < 0:
        raise ValueError("--wikipedia-429-recovery-seconds must be non-negative.")
    args.stream_reuse_cached_page_count = normalize_stream_reuse_cached_page_count(
        args.stream_reuse_cached_page_count
    )
    args.stream_fresh_cached_page_count = normalize_stream_fresh_cached_page_count(
        args.stream_fresh_cached_page_count
    )
    if args.stream_page_processing_target < 0:
        raise ValueError("--stream-page-processing-target must be non-negative.")
    if args.reset_stream_state and args.start_from_endpoint:
        raise ValueError("--reset-stream-state cannot be combined with --start-from-endpoint.")
    if args.run_artifact_manifest is not None and not args.run_group_id.strip():
        raise ValueError("--run-artifact-manifest requires --run-group-id.")
    args.route3_answer_type = list(normalize_route3_answer_types(args.route3_answer_type))
    args.route3_table_source_type = list(
        normalize_route3_table_source_types(args.route3_table_source_type or DEFAULT_ROUTE3_TABLE_SOURCE_TYPES)
    )
    args.route3_answer_type_mode = normalize_route3_answer_type_mode(args.route3_answer_type_mode)
    args.route3_infobox_max_removed_row_rate = max(0.0, min(1.0, float(args.route3_infobox_max_removed_row_rate)))
    args.route3_infobox_min_remaining_rows = max(0, int(args.route3_infobox_min_remaining_rows))
    proxy = _optional_proxy(args.proxy)
    small_llm = LLMConfig(
        provider=args.small_model_provider,
        model=args.generation_model,
        api_key_env=args.small_model_api_key_env,
        base_url=args.small_model_base_url,
        proxy=proxy,
        max_tokens=args.small_model_max_tokens,
    )
    settings = Settings(
        run_date=args.run_date or Settings().run_date,
        pilot_total=effective_record_limit,
        cutoff_year=args.cutoff_year,
        timeout_seconds=args.timeout_seconds,
        duckduckgo_top_k=args.duckduckgo_top_k,
        duckduckgo_parallel_queries=args.duckduckgo_parallel_queries,
        generated_search_query_count=args.generated_search_query_count,
        search_longtail_max_full_question_hit_rate=args.search_longtail_max_full_question_hit_rate,
        search_longtail_max_keyword_hit_rate=args.search_longtail_max_keyword_hit_rate,
        search_longtail_max_overall_hit_rate=args.search_longtail_max_overall_hit_rate,
        second_stage_grading_enabled=args.enable_second_stage_grading,
        second_stage_grading_accuracy_threshold=args.second_stage_grading_accuracy_threshold,
        enabled_routes=("route3_wikipedia_infobox",),
        proxy=proxy,
        **duckduckgo_settings_kwargs(args),
    )
    wikipedia_client = WikipediaClient(
        user_agent=settings.user_agent,
        proxy=settings.proxy,
        timeout_seconds=settings.timeout_seconds,
        cache_dir=settings.cache_dir,
        rate_limit_backoff_seconds=args.wikipedia_429_backoff_seconds,
        rate_limit_max_backoff_seconds=args.wikipedia_429_max_backoff_seconds,
        rate_limit_recovery_seconds=args.wikipedia_429_recovery_seconds,
    )
    search_client = DuckDuckGoSearchClient(**settings.duckduckgo_client_kwargs())
    openrouter_circuit = ServiceCircuit("openrouter")
    duckduckgo_circuit = ServiceCircuit("duckduckgo")
    llm_client = Route3OpenRouterClientFactory.from_config(
        small_llm,
        timeout_seconds=settings.timeout_seconds,
        circuit=openrouter_circuit,
    )
    summary = _run_streaming_page_id_pipeline(
        args=args,
        settings=settings,
        wikipedia_client=wikipedia_client,
        search_client=search_client,
        llm_client=llm_client,
        endpoint_resume=endpoint_resume,
        openrouter_circuit=openrouter_circuit,
        duckduckgo_circuit=duckduckgo_circuit,
    )
    print_json_summary(summary)
    return 0


def _load_endpoint_resume(args: argparse.Namespace) -> EndpointResumeState:
    """Load existing accepted/rejected output files when endpoint resume is enabled."""
    if not getattr(args, "start_from_endpoint", False):
        return EndpointResumeState(enabled=False)
    accepted_records, accepted_skipped = load_endpoint_jsonl(args.output, label="accepted")
    rejected_records, rejected_skipped = load_endpoint_jsonl(args.rejected_output, label="rejected")
    return EndpointResumeState(
        enabled=True,
        accepted_records=accepted_records,
        rejected_records=rejected_records,
        skipped_lines=[*accepted_skipped, *rejected_skipped],
    )




def _write_summary_and_manifest(args: argparse.Namespace, summary: dict) -> None:
    """Write the invocation summary and update its optional run-group manifest."""
    _write_json_atomic(args.summary_output, summary)
    _update_run_artifact_manifest(args, summary)


def _update_run_artifact_manifest(args: argparse.Namespace, summary: dict) -> None:
    """Record this invocation in the run-group artifact manifest."""
    run_group_id = str(summary.get("run_group_id", "") or "")
    if not run_group_id:
        return
    manifest_path = _run_artifact_manifest_path(args, run_group_id)
    if manifest_path is None:
        return
    existing: dict[str, object] = {}
    if manifest_path.exists():
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        existing_group = str(existing.get("run_group_id", "") or "")
        if existing_group and existing_group != run_group_id:
            raise ValueError(
                f"Manifest {manifest_path} belongs to run group {existing_group!r}, not {run_group_id!r}."
            )
    segments = [
        segment
        for segment in existing.get("segments", [])
        if isinstance(segment, dict) and segment.get("segment_id") != summary.get("run_segment_id")
    ]
    for included_segment in _included_manifest_segments(args, run_group_id):
        segments = [
            segment
            for segment in segments
            if isinstance(segment, dict) and segment.get("segment_id") != included_segment.get("segment_id")
        ]
        segments.append(included_segment)
    segments.append(_manifest_segment(summary))
    manifest = {
        "manifest_version": 1,
        "run_group_id": run_group_id,
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "artifact_index": _manifest_artifact_index(segments),
        "segments": segments,
    }
    _write_json_atomic(manifest_path, manifest)


def _manifest_segment(summary: dict) -> dict[str, object]:
    """Return the compact manifest entry for one run segment."""
    return {
        "segment_id": summary.get("run_segment_id", ""),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "start_from_endpoint": bool(summary.get("start_from_endpoint", False)),
        "start_stage": summary.get("start_stage", ""),
        "streaming_mode": summary.get("streaming_mode", ""),
        "stream_reused_cached_page_count": summary.get("stream_reused_cached_page_count", 0),
        "route3_reasoning_types": summary.get("route3_reasoning_types", []),
        "route3_answer_types": summary.get("route3_answer_types", []),
        "route3_extra_prompts": [],
        "route3_table_filter_modes": summary.get("route3_table_filter_modes", []),
        "route3_table_source_types": summary.get("route3_table_source_types", []),
        "route3_prose_leakage_scoring_enabled": bool(summary.get("route3_prose_leakage_scoring_enabled", True)),
        "record_limit": summary.get("record_limit", 0),
        "attempted_page_ids": summary.get("attempted_page_ids", summary.get("attempted_urls", 0)),
        "accepted": summary.get("accepted", 0),
        "accepted_total": summary.get("accepted_total", summary.get("accepted", 0)),
        "rejected": summary.get("rejected", 0),
        "rejected_total": summary.get("rejected_total", summary.get("rejected", 0)),
        "retry_pending": summary.get("retry_pending", 0),
        "wall_clock_seconds": summary.get("wall_clock_seconds"),
        "output_path": summary.get("output_path", ""),
        "rejected_output_path": summary.get("rejected_output_path", ""),
        "summary_output": summary.get("summary_output", ""),
        "walkthrough_output": summary.get("walkthrough_output", ""),
        "stream_state": summary.get("stream_state", ""),
    }


def _included_manifest_segments(args: argparse.Namespace, run_group_id: str) -> list[dict[str, object]]:
    """Build manifest entries from previously written summary JSON files."""
    segments: list[dict[str, object]] = []
    manifest_path = _run_artifact_manifest_path(args, run_group_id)
    for summary_path in getattr(args, "run_artifact_include_summary", []) or []:
        payload = json.loads(Path(summary_path).read_text(encoding="utf-8"))
        existing_group = str(payload.get("run_group_id", "") or "")
        if existing_group and existing_group != run_group_id:
            raise ValueError(
                f"Included summary {summary_path} belongs to run group {existing_group!r}, not {run_group_id!r}."
            )
        payload = dict(payload)
        payload["run_group_id"] = run_group_id
        payload["run_segment_id"] = safe_artifact_id(
            str(payload.get("run_segment_id", "") or Path(summary_path).stem),
            fallback=Path(summary_path).stem,
        )
        payload["summary_output"] = str(payload.get("summary_output") or summary_path)
        payload["run_artifact_manifest"] = str(manifest_path) if manifest_path is not None else ""
        segments.append(_manifest_segment(payload))
    return segments


def _manifest_artifact_index(segments: list[dict]) -> dict[str, list[str]]:
    """Return quick lookup lists for all artifacts in a run group."""
    return {
        "accepted_jsonl": _unique_manifest_paths(segments, "output_path"),
        "rejected_jsonl": _unique_manifest_paths(segments, "rejected_output_path"),
        "summary_json": _unique_manifest_paths(segments, "summary_output"),
        "walkthrough_md": _unique_manifest_paths(segments, "walkthrough_output"),
        "stream_state_json": _unique_manifest_paths(segments, "stream_state"),
    }


def _unique_manifest_paths(segments: list[dict], key: str) -> list[str]:
    """Return sorted non-empty artifact paths for one manifest key."""
    return sorted({str(segment.get(key, "") or "") for segment in segments if str(segment.get(key, "") or "")})


def _write_json_atomic(path: Path, payload: dict) -> None:
    """Atomically write one JSON document with the shared durable boundary."""
    atomic_write_json(path, payload)

def _remaining_after_endpoint(record_limit: int | str, final_decision_count: int) -> int:
    """Return how many additional final decisions are needed for a resumed endpoint."""
    return max(0, int(record_limit) - max(0, int(final_decision_count)))












def _filter_endpoint_url_entries(
    entries: list[UrlEntry],
    endpoint_resume: EndpointResumeState,
) -> tuple[list[UrlEntry], list[str]]:
    """Remove URL entries already present in accepted/rejected endpoint records."""
    if not endpoint_resume.enabled:
        return entries, []
    completed_keys = _endpoint_source_keys(endpoint_resume.accepted_records + endpoint_resume.rejected_records)
    filtered: list[UrlEntry] = []
    skipped: list[str] = []
    for entry in entries:
        keys = _url_entry_keys(entry)
        if completed_keys.intersection(keys):
            skipped.append(entry.url)
            continue
        filtered.append(entry)
    return filtered, skipped


def _endpoint_source_keys(records: list[dict]) -> set[str]:
    """Return URL/title keys represented by endpoint records."""
    keys: set[str] = set()
    for record in records:
        metadata = record.get("source_metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}
        subject_entity = record.get("subject_entity", {})
        if not isinstance(subject_entity, dict):
            subject_entity = {}
        for value in (
            metadata.get("source_url"),
            metadata.get("stream_source_url"),
            metadata.get("canonical_url"),
            subject_entity.get("url"),
            metadata.get("page_title"),
            subject_entity.get("wikipedia_title"),
        ):
            keys.update(_source_key_variants(str(value or "")))
    return keys


def _url_entry_keys(entry: UrlEntry) -> set[str]:
    """Return comparable URL/title keys for a URL entry."""
    return _source_key_variants(entry.url)


def _source_key_variants(value: str) -> set[str]:
    """Return normalized URL/title/page-ID variants for endpoint matching."""
    stripped = value.strip()
    if not stripped:
        return set()
    keys = {stripped, stripped.replace(" ", "_")}
    title = normalize_wikipedia_title(stripped)
    if title:
        keys.add(title)
        keys.add(title.replace(" ", "_"))
        keys.add("https://en.wikipedia.org/wiki/" + title.replace(" ", "_"))
    page_id = normalize_wikipedia_page_id(stripped)
    if page_id is not None:
        keys.add(str(page_id))
        keys.add(build_pageid_url(page_id))
    return {key for key in keys if key}


def _endpoint_page_ids(records: list[dict]) -> list[int]:
    """Extract page IDs from endpoint records for stream-state synchronization."""
    page_ids: list[int] = []
    for record in records:
        metadata = record.get("source_metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}
        streaming = metadata.get("streaming_discovery", {})
        if not isinstance(streaming, dict):
            streaming = {}
        for value in (
            metadata.get("page_id"),
            streaming.get("page_id"),
            normalize_wikipedia_page_id(str(metadata.get("stream_source_url") or "")),
            normalize_wikipedia_page_id(str(metadata.get("source_url") or "")),
        ):
            try:
                page_id = int(value)
            except (TypeError, ValueError):
                continue
            if page_id > 0:
                page_ids.append(page_id)
                break
    return page_ids


def _renumber_accepted_records(records: list[dict]) -> None:
    """Assign stable Route 3 IDs."""
    for record in records:
        ensure_page_id_list_entry_metadata(record)
    assign_unique_route3_record_ids(records)


def _jsonl_record_count(path: Path) -> int:
    """Return the number of non-empty JSONL lines already written."""
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def _wikipedia_stream_record_id(record: dict) -> str:
    """Return the stable stream candidate ID."""
    return route3_record_id(record)


def _accepted_output_records(records: list[dict], args: argparse.Namespace) -> list[dict]:
    """Return accepted records in the configured output shape."""
    for record in records:
        ensure_page_id_list_entry_metadata(record)
    return records


def _rejected_output_records(records: list[dict], args: argparse.Namespace) -> list[dict]:
    """Return rejected records in the configured output shape."""
    for record in records:
        ensure_page_id_list_entry_metadata(record)
    return records








def _compact_accepted_record(record: dict) -> dict:
    """Keep the accepted QA fields needed for large-batch review."""
    metadata = record.get("source_metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
    subject = record.get("subject_entity", {})
    if not isinstance(subject, dict):
        subject = {}
    notes = record.get("rejection_notes", {})
    if not isinstance(notes, dict):
        notes = {}
    panel = record.get("panel_grading_features")
    if panel is None:
        panel = record.get("panel_grading_features", notes.get("panel_grading_features", {}))
    llm_response = metadata.get("llm_response")
    if not isinstance(llm_response, dict):
        llm_response = metadata.get("small_model_qa_response")
    if not isinstance(llm_response, dict):
        llm_response = {}
    return {
        "id": record.get("id", ""),
        "question": record.get("question", record.get("canonical_question", "")),
        "answer": record.get("answer", ""),
        "answer_aliases": record.get("answer_aliases", []),
        "source_type": record.get("source_type", ""),
        "generation_route": record.get("generation_route", ""),
        "subject_entity": {
            "name": subject.get("name", ""),
            "wikipedia_title": subject.get("wikipedia_title", ""),
            "url": subject.get("url", ""),
        },
        "reasoning_type": record.get("relation_or_claim", metadata.get("reasoning_type", "")),
        "answer_type": record.get("answer_type", ""),
        "panel_grading_features": panel if isinstance(panel, dict) else {},
        "source_metadata": {
            "page_title": metadata.get("page_title", ""),
            "first_paragraph": metadata.get("first_paragraph", ""),
            "subject_anchor_aliases": metadata.get("subject_anchor_aliases", []),
            "safe_subject_aliases": metadata.get("safe_subject_aliases", []),
            "subject_anchors": metadata.get("subject_anchors", {}),
            "parsed_tables": metadata.get("parsed_tables", []),
            "selected_source_table": metadata.get("selected_source_table", {}),
            "llm_response": llm_response,
            "small_model_qa_response": llm_response,
            "phase_timings_seconds": metadata.get("phase_timings_seconds", {}),
        },
    }


def _compact_rejected_record(record: dict) -> dict:
    """Keep enough rejected metadata for failure analysis without large evidence blobs."""
    metadata = record.get("source_metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
    notes = record.get("rejection_notes", {})
    if not isinstance(notes, dict):
        notes = {}
    page_id = record_page_id(record)
    return {
        "page_url": (
            metadata.get("stream_source_url")
            or metadata.get("source_url")
            or metadata.get("canonical_url")
            or record.get("source_url", "")
        ),
        "page_id": page_id,
        "id": record.get("id", ""),
        "question": record.get("question", record.get("canonical_question", "")),
        "answer": record.get("answer", ""),
        "rejection_reason": record.get("rejection_reason", ""),
        "failing_reason": exact_failure_reason(record),
        "failure_metrics": _failure_metrics(record),
        "source_metadata": {
            "page_title": metadata.get("page_title", ""),
            "phase_timings_seconds": metadata.get("phase_timings_seconds", {}),
        },
    }


def _failure_metrics(record: dict) -> dict[str, object]:
    """Return compact accuracy or search hit-rate metrics for a rejected record."""
    notes = record.get("rejection_notes", {})
    if not isinstance(notes, dict):
        return {}
    search_features = notes.get("search_verification_features", {})
    if isinstance(search_features, dict) and search_features:
        rates = search_features.get("category_hit_rates", {})
        thresholds = search_features.get("thresholds", {})
        metrics = {
            "triggered_rule": search_features.get("triggered_rule", ""),
            "thresholds": thresholds if isinstance(thresholds, dict) else {},
        }
        if isinstance(rates, dict):
            metrics["hit_rates"] = {
                key: value.get("answer_hit_rate")
                for key, value in rates.items()
                if isinstance(value, dict) and "answer_hit_rate" in value
            }
        return {key: value for key, value in metrics.items() if value not in ({}, "", None)}
    panel = notes.get("panel_grading_features", {})
    if isinstance(panel, dict):
        return {
            key: panel.get(key)
            for key in ("accuracy", "accuracy_threshold", "attempt_rate", "correct_count", "model_count")
            if panel.get(key) is not None
        }
    return {}


def _run_streaming_page_id_pipeline(
    *,
    args: argparse.Namespace,
    settings: Settings,
    wikipedia_client: WikipediaClient,
    search_client: DuckDuckGoSearchClient,
    llm_client,
    endpoint_resume: EndpointResumeState,
    openrouter_circuit: ServiceCircuit,
    duckduckgo_circuit: ServiceCircuit,
) -> dict:
    """Process random Wikipedia page IDs and append decisions incrementally."""
    run_started = perf_counter()
    if llm_client is None:
        raise ValueError("Streaming Route 3 requires a small-model client.")
    concurrency = _build_streaming_concurrency_context(args)
    wikipedia_client = SemaphoreWrappedClient(
        wikipedia_client,
        concurrency.wikipedia_semaphore,
        {"fetch_summary", "fetch_parse", "search_page_ids"},
    )
    search_client = SemaphoreWrappedClient(
        search_client,
        concurrency.duckduckgo_semaphore,
        {"search"},
    )
    if isinstance(llm_client, Route3OpenRouterClientFactory):
        llm_client.transport = SemaphoreWrappedClient(
            llm_client.transport,
            concurrency.generation_rewrite_semaphore,
            {"send_once"},
        )
    else:
        llm_client = SemaphoreWrappedClient(
            llm_client,
            concurrency.generation_rewrite_semaphore,
            {"complete_text", "complete_text_with_audit"},
        )
    second_stage_model_clients = _build_streaming_second_stage_model_panel(
        settings,
        concurrency,
        openrouter_circuit,
    )
    grading_grader_client = _build_streaming_second_stage_grader_client(
        settings,
        concurrency,
        openrouter_circuit,
    )
    ddg_verifier_result_store = _build_ddg_verifier_result_store(args, duckduckgo_circuit)
    if args.reset_stream_state:
        state = PageIdStreamState(path=args.stream_state)
        state.save()
    else:
        state = PageIdStreamState.load(args.stream_state)
    ledger_index = SegmentLedgerIndex(
        allocation_dir=args.page_allocation_ledger_dir,
        attempt_dir=args.page_attempt_ledger_dir,
        run_group_id=run_group_id(args),
        segment_id=run_segment_id(args),
        run_group_segments_dir=args.run_group_segments_dir,
    )
    ambiguous_calls = scan_ambiguous_external_calls(args.external_call_record_dir)
    quarantined_page_ids = {
        int(row["page_id"])
        for row in ambiguous_calls
        if str(row.get("retry_eligibility", "")) != "retry_authorized"
    }
    ledger_recovery = recover_stream_state_from_ledger(state, ledger_index)
    accepted_records, rejected_records, retry_pending_records = rebuild_derived_outputs(
        ledger_index,
        accepted_path=args.output,
        rejected_path=args.rejected_output,
    )
    primary_page_ids_at_start = ledger_index.primary_page_ids
    run_group_allocated_page_ids = ledger_index.run_group_page_ids
    run_group_allocated_page_count_at_start = len(run_group_allocated_page_ids)
    state.used_ids.update(run_group_allocated_page_ids)
    _initialize_table_search_offsets(state, args)
    endpoint_sync = {"accepted_ids_synced": 0, "rejected_ids_synced": 0}
    if args.start_from_endpoint:
        endpoint_sync = state.sync_decided_ids(
            accepted_ids=_endpoint_page_ids(endpoint_resume.accepted_records),
            rejected_ids=_endpoint_page_ids(endpoint_resume.rejected_records),
        )
    rng = random.Random(args.stream_random_seed)

    reuse_budget = args.stream_reuse_cached_page_count
    fresh_budget = args.stream_fresh_cached_page_count
    explicit_processing_target = max(0, int(getattr(args, "stream_page_processing_target", 0) or 0))
    requested_main_page_count = explicit_processing_target or (
        stream_budget_numeric_count(reuse_budget) + stream_budget_numeric_count(fresh_budget)
    )
    page_processing_target_remaining_at_start = max(
        0, requested_main_page_count - len(primary_page_ids_at_start)
    )
    page_workers = max(1, int(args.stream_page_workers))
    batch_limit = max(1, int(args.stream_batch_size))
    processed_this_invocation: list[int] = []
    cached_page_reuse_entries: list[CachedPageArchiveEntry] = []
    cached_page_reuse_summary = _stream_cached_page_reuse_disabled_summary(args)

    def dispatch_allocations(page_ids: list[int]) -> list[dict]:
        """Dispatch one bounded allocation batch and propagate unexpected failures."""
        selected = [page_id for page_id in page_ids if page_id not in quarantined_page_ids]
        if not selected:
            return []
        futures = {}
        with ThreadPoolExecutor(max_workers=min(page_workers, len(selected))) as executor:
            for page_id in selected:
                allocation = ledger_index.allocation_for(page_id)
                if allocation is None:
                    raise ValueError(f"Page {page_id} has no allocation")
                cached_path_text = str(allocation.get("cached_archive_path", ""))
                cached_path = Path(cached_path_text) if cached_path_text else None
                futures[
                    executor.submit(
                        _process_one_stream_page_id,
                        page_id,
                        args=args,
                        settings=settings,
                        state=state,
                        wikipedia_client=wikipedia_client,
                        search_client=search_client,
                        llm_client=llm_client,
                        concurrency=concurrency,
                        second_stage_model_clients=second_stage_model_clients,
                        grading_grader_client=grading_grader_client,
                        ddg_verifier_result_store=ddg_verifier_result_store,
                        ledger_index=ledger_index,
                        source_url=str(allocation.get("source_url", "")) or build_pageid_url(page_id),
                        stream_page_source=(
                            "cached_page_archive"
                            if str(allocation.get("page_source", "")) == "cache"
                            else args.stream_page_source
                        ),
                        cached_archive_path=cached_path,
                    )
                ] = page_id
            decisions = [future.result() for future in as_completed(futures)]
        processed_this_invocation.extend(selected)
        return decisions

    def dispatch_phase(page_ids: list[int]) -> list[dict]:
        """Run ledger-derived work in bounded batches until a circuit opens."""
        decisions: list[dict] = []
        for offset in range(0, len(page_ids), batch_limit):
            if _external_circuit_is_open(openrouter_circuit, duckduckgo_circuit):
                break
            decisions.extend(dispatch_allocations(page_ids[offset : offset + batch_limit]))
        return decisions

    # Resume allocated attempt001 work before discovering any new pages.
    dispatch_phase(ledger_index.pending_primary_page_ids)

    missing_primary = max(0, requested_main_page_count - len(ledger_index.primary_page_ids))
    if reuse_budget == "all":
        reuse_requested = missing_primary
    else:
        reuse_requested = min(stream_budget_numeric_count(reuse_budget), missing_primary)
    while len(cached_page_reuse_entries) < reuse_requested:
        if _external_circuit_is_open(openrouter_circuit, duckduckgo_circuit):
            break
        request_count = min(batch_limit, reuse_requested - len(cached_page_reuse_entries))
        entries, cached_page_reuse_summary = _reserve_stream_cached_page_archives(
            state=state,
            args=args,
            requested_count=request_count,
            excluded_page_ids=run_group_allocated_page_ids,
        )
        if not entries:
            break
        for entry in entries:
            ledger_index.commit_allocation(
                canonical_page_id=entry.page_id,
                page_source="cache",
                source_url=entry.source_url,
                cached_archive_path=str(entry.archive_path),
            )
            run_group_allocated_page_ids.add(entry.page_id)
        cached_page_reuse_entries.extend(entries)
        dispatch_phase([entry.page_id for entry in entries])

    missing_after_cache = max(0, requested_main_page_count - len(ledger_index.primary_page_ids))
    fresh_requested = (
        missing_after_cache
        if fresh_budget == "fill"
        else min(stream_budget_numeric_count(fresh_budget), missing_after_cache)
    )
    fresh_allocated = 0
    while fresh_allocated < fresh_requested:
        if _external_circuit_is_open(openrouter_circuit, duckduckgo_circuit):
            break
        request_count = min(batch_limit, fresh_requested - fresh_allocated)
        reserved_ids = _reserve_stream_page_ids(
            state=state,
            args=args,
            wikipedia_client=wikipedia_client,
            rng=rng,
            count=request_count,
            excluded_page_ids=run_group_allocated_page_ids,
        )
        if not reserved_ids:
            break
        for page_id in reserved_ids:
            ledger_index.commit_allocation(
                canonical_page_id=page_id,
                page_source="fresh",
                source_url=build_pageid_url(page_id),
            )
            run_group_allocated_page_ids.add(page_id)
        fresh_allocated += len(reserved_ids)
        dispatch_phase(reserved_ids)

    # Retry eligibility is derived once from attempt001 history, never from process startup.
    dispatch_phase(ledger_index.eligible_retry_page_ids)

    cached_reuse_page_ids = [entry.page_id for entry in cached_page_reuse_entries]
    accepted_records, rejected_records, retry_pending_records = rebuild_derived_outputs(
        ledger_index,
        accepted_path=args.output,
        rejected_path=args.rejected_output,
    )
    processed_ids = sorted(ledger_index.primary_page_ids)
    fresh_processed_page_ids = [
        int(row["canonical_page_id"])
        for row in ledger_index.allocations
        if str(row.get("page_source", "")) == "fresh"
    ]
    all_decision_records = [*accepted_records, *rejected_records]
    summary = {
        **_run_artifact_summary(args),
        "start_stage": "generate",
        "start_from_endpoint": args.start_from_endpoint,
        "endpoint_resume": {
            **endpoint_resume.summary(),
            **endpoint_sync,
        },
        "streaming_mode": "page_id_stream",
        "stream_page_source": "table-search",
        "stream_search_queries": _stream_search_queries(),
        "stream_search_offsets": state.table_search_offsets.copy(),
        "run_group_allocated_page_ids_at_start": run_group_allocated_page_count_at_start,
        "run_date": settings.run_date,
        "stream_state": str(args.stream_state),
        "page_attempt_ledger_dir": str(args.page_attempt_ledger_dir),
        "page_attempt_ledger": ledger_summary(ledger_index),
        "ledger_state_recovery": ledger_recovery,
        "stream_state_stats": state.stats(),
        "stream_state_reset": bool(args.reset_stream_state),
        "ambiguous_external_calls": ambiguous_calls,
        "quarantined_page_ids": sorted(quarantined_page_ids),
        "stream_reuse_cached_page_count": reuse_requested,
        "stream_reuse_cached_page_count_raw": str(reuse_budget),
        "stream_fresh_cached_page_count": fresh_requested,
        "stream_fresh_cached_page_count_raw": str(fresh_budget),
        "stream_requested_main_page_count": requested_main_page_count,
        "stream_page_processing_target": explicit_processing_target,
        "stream_page_processing_target_remaining_at_start": page_processing_target_remaining_at_start,
        "stream_fresh_page_count_remaining_at_start": fresh_requested,
        "stream_cached_page_reuse": cached_page_reuse_summary,
        "stream_reused_cached_page_ids": cached_reuse_page_ids,
        "stream_reused_cached_page_count": len(cached_page_reuse_entries),
        "stream_fresh_processed_page_ids": fresh_processed_page_ids,
        "stream_fresh_processed_page_count": len(fresh_processed_page_ids),
        "processed_this_invocation": sorted(set(processed_this_invocation)),
        "retry_pending_page_ids": ledger_index.eligible_retry_page_ids,
        "random_seed": args.stream_random_seed,
        "random_seed_was_explicit": bool(getattr(args, "stream_random_seed_was_explicit", False)),
        "record_limit": requested_main_page_count,
        "record_limit_remaining_at_start": page_processing_target_remaining_at_start,
        "record_limit_deprecated_alias": True,
        "compatibility_aliases": {
            "record_limit": "stream_requested_main_page_count",
            "record_limit_remaining_at_start": "stream_page_processing_target_remaining_at_start",
        },
        "stream_batch_size": args.stream_batch_size,
        "stream_discovery_max_retries": args.stream_discovery_max_retries,
        "stream_discovery_retry_backoff_seconds": args.stream_discovery_retry_backoff_seconds,
        "stream_discovery_retry_max_sleep_seconds": args.stream_discovery_retry_max_sleep_seconds,
        "wikipedia_429_backoff_seconds": args.wikipedia_429_backoff_seconds,
        "wikipedia_429_max_backoff_seconds": args.wikipedia_429_max_backoff_seconds,
        "wikipedia_429_recovery_seconds": args.wikipedia_429_recovery_seconds,
        "stream_page_workers": page_workers,
        "wikipedia_concurrency_limit": args.wikipedia_concurrency_limit,
        "duckduckgo_concurrency_limit": args.duckduckgo_concurrency_limit,
        "openrouter_generation_rewrite_concurrency_limit": args.openrouter_generation_rewrite_concurrency_limit,
        "second_stage_concurrency_limit": args.second_stage_concurrency_limit,
        "service_circuits": {
            "openrouter": openrouter_circuit.snapshot(),
            "duckduckgo": duckduckgo_circuit.snapshot(),
        },
        "attempted_page_ids": len(processed_ids),
        "attempted_page_ids_unique": len(set(processed_ids)),
        "page_ids": processed_ids,
        "page_id_list_entries": [
            entry.to_record()
            for entry in sorted(
                _stream_page_id_list_entries(
                    processed_ids,
                    all_decision_records=all_decision_records,
                    answer_types=_page_id_list_answer_types(args),
                    table_types=args.route3_table_source_type,
                    page_level_failure_ids={
                        int(attempt["canonical_page_id"])
                        for attempt in ledger_index.attempts
                        if bool(attempt.get("page_level_failure", False))
                    },
                )
            )
        ],
        "accepted": len(accepted_records),
        "accepted_total": endpoint_resume.accepted_count + len(accepted_records),
        "rejected": len(rejected_records),
        "rejected_total": endpoint_resume.rejected_count + len(rejected_records),
        "retry_pending": len(retry_pending_records),
        "wall_clock_seconds": round(perf_counter() - run_started, 4),
        "output_path": str(args.output),
        "rejected_output_path": str(args.rejected_output),
        "summary_output": str(args.summary_output),
        "walkthrough_output": str(args.walkthrough_output) if args.walkthrough_output else "",
        "domain_policy": "domain_and_subdomain_optional_for_page_id_streaming",
        "enabled_routes": list(settings.enabled_routes),
        "generation_model": args.generation_model,
        "small_model": args.generation_model,
        "second_stage_grading_enabled": settings.second_stage_grading_enabled,
        "duckduckgo_top_k": settings.duckduckgo_top_k,
        "duckduckgo_parallel_queries": settings.duckduckgo_parallel_queries,
        **duckduckgo_summary_fields(settings),
        "generated_search_query_count": settings.generated_search_query_count,
        "min_table_score": 0.0,
        "route3_reasoning_types": list(DEFAULT_ROUTE3_REASONING_TYPES),
        "route3_answer_types": args.route3_answer_type,
        "route3_table_filter_modes": args.route3_table_filter_mode,
        "route3_table_source_types": args.route3_table_source_type,
        "route3_prose_leakage_scoring_enabled": True,
        "route3_answer_type_mode": args.route3_answer_type_mode,
        "route3_page_archive_dir": str(args.route3_page_archive_dir),
        "route3_infobox_max_removed_row_rate": args.route3_infobox_max_removed_row_rate,
        "route3_infobox_min_remaining_rows": args.route3_infobox_min_remaining_rows,
        "compact_output": False,
        "compact_output_ignored": bool(args.compact_output or args.big_batch_mode),
        "compact_rejected_output": False,
        "compact_rejected_output_ignored": bool(args.compact_rejected_output or args.compact_output or args.big_batch_mode),
        **llm_generation_table_yield_summary(accepted_records, rejected_records, rerun_records=retry_pending_records),
        "survival_by_layer": survival_by_layer(
            attempted_count=len(processed_ids),
            accepted_records=accepted_records,
            rejected_records=rejected_records,
            rerun_records=retry_pending_records,
        ),
        "failure_reason_counts": failure_reason_counts(rejected_records, retry_pending_records),
        "phase_timing_stats_seconds": phase_timing_stats(all_decision_records),
        "aggregate_phase_timings_seconds": aggregate_phase_timings(accepted_records, rejected_records),
        "telemetry": {
            "wikipedia": wikipedia_client.request_events.copy(),
            "search": search_client.request_events.copy(),
        },
    }
    if args.walkthrough_output is not None:
        write_stream_walkthrough(
            path=args.walkthrough_output,
            summary=summary,
            accepted_records=accepted_records,
            rejected_records=rejected_records,
            rerun_records=retry_pending_records,
            existing_accepted_records=endpoint_resume.accepted_records if endpoint_resume.enabled else [],
            existing_rejected_records=endpoint_resume.rejected_records if endpoint_resume.enabled else [],
        )
    _write_summary_and_manifest(args, summary)
    return summary


def _build_streaming_concurrency_context(args: argparse.Namespace) -> StreamingConcurrencyContext:
    """Build shared locks and semaphores for one streaming run."""
    return StreamingConcurrencyContext(
        commit_lock=Lock(),
        wikipedia_semaphore=Semaphore(max(1, int(args.wikipedia_concurrency_limit))),
        duckduckgo_semaphore=Semaphore(max(1, int(args.duckduckgo_concurrency_limit))),
        generation_rewrite_semaphore=Semaphore(
            max(1, int(args.openrouter_generation_rewrite_concurrency_limit))
        ),
        second_stage_semaphore=Semaphore(max(1, int(args.second_stage_concurrency_limit))),
    )


def _initialize_table_search_offsets(state: PageIdStreamState, args: argparse.Namespace) -> None:
    """Seed table-search offsets for fresh segmented stream states."""
    initial_offset = max(0, int(getattr(args, "stream_search_initial_offset", 0) or 0))
    if not initial_offset:
        return
    changed = False
    for query in _stream_search_queries():
        if state.table_search_offset(query) >= initial_offset:
            continue
        state.table_search_offsets[query] = initial_offset
        state._record_event("initialize_table_search_offset", [], f"{query}:{initial_offset}")
        changed = True
    if changed:
        state.save()


def _stream_cached_page_reuse_disabled_summary(args: argparse.Namespace) -> dict[str, object]:
    """Return the summary payload used when cached page reuse is disabled."""
    return {
        "enabled": False,
        "requested_count": stream_budget_numeric_count(
            normalize_stream_reuse_cached_page_count(getattr(args, "stream_reuse_cached_page_count", 0) or 0)
        ),
        "requested_count_raw": str(getattr(args, "stream_reuse_cached_page_count", 0) or 0),
        "archive_dir": str(getattr(args, "route3_page_archive_dir", "") or ""),
        "strict_numeric_page_id_matching": True,
        "selected_count": 0,
        "selected_page_ids": [],
    }


def _reserve_stream_cached_page_archives(
    *,
    state: PageIdStreamState,
    args: argparse.Namespace,
    excluded_page_ids: set[int],
    requested_count: int | None = None,
) -> tuple[list[CachedPageArchiveEntry], dict[str, object]]:
    """Reserve reusable cached parsed pages by strict numeric page ID."""
    if requested_count is None:
        requested_count = stream_budget_numeric_count(
            normalize_stream_reuse_cached_page_count(getattr(args, "stream_reuse_cached_page_count", 0) or 0)
        )
    else:
        requested_count = max(0, int(requested_count))
    archive_dir = Path(getattr(args, "route3_page_archive_dir", ROOT / DEFAULT_ROUTE3_PAGE_ARCHIVE_DIR))
    cached_entries, scan_summary = _scan_route3_cached_page_archives(archive_dir)
    available_entries = [
        entry for entry in cached_entries if entry.page_id not in excluded_page_ids
    ]
    selected = available_entries[:requested_count]
    if selected:
        for entry in selected:
            state.used_ids.add(entry.page_id)
            state.in_progress_ids.add(entry.page_id)
        state._record_event(
            "reserve_cached_page_archives",
            [entry.page_id for entry in selected],
            f"requested={requested_count};archive_dir={archive_dir}",
        )
        state.save()
    summary = {
        "enabled": requested_count > 0,
        "requested_count": requested_count,
        "archive_dir": str(archive_dir),
        "strict_numeric_page_id_matching": True,
        **scan_summary,
        "run_group_allocation_excluded_page_count": len(
            {entry.page_id for entry in cached_entries if entry.page_id in excluded_page_ids}
        ),
        "reusable_cached_page_count": len(available_entries),
        "selected_count": len(selected),
        "selected_page_ids": [entry.page_id for entry in selected],
        "selected_archive_paths": [str(entry.archive_path) for entry in selected],
    }
    return selected, summary


def _scan_route3_cached_page_archives(cache_dir: Path) -> tuple[list[CachedPageArchiveEntry], dict[str, object]]:
    """Return reusable parsed page archives from a Route 3 archive directory."""
    root = Path(cache_dir)
    if not root.exists():
        return [], {
            "cached_archive_file_count": 0,
            "cached_archive_valid_page_count": 0,
            "cached_archive_duplicate_page_count": 0,
            "cached_archive_skipped_count": 0,
            "cached_archive_errors": [{"path": str(root), "error": "archive_dir_not_found"}],
        }
    entries: list[CachedPageArchiveEntry] = []
    errors: list[dict[str, str]] = []
    skipped_count = 0
    duplicate_count = 0
    seen_page_ids: set[int] = set()
    archive_paths = sorted(path for path in root.glob("*.json") if path.is_file())
    for path in archive_paths:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append({"path": str(path), "error": f"{type(exc).__name__}:{exc}"})
            skipped_count += 1
            continue
        if not isinstance(payload, dict):
            skipped_count += 1
            continue
        page_id = _cached_archive_page_id(payload)
        if page_id is None or not _cached_archive_has_parse_material(payload):
            skipped_count += 1
            continue
        if page_id in seen_page_ids:
            duplicate_count += 1
            continue
        source_url = str(payload.get("source_url") or "").strip() or build_pageid_url(page_id)
        entries.append(CachedPageArchiveEntry(page_id=page_id, source_url=source_url, archive_path=path))
        seen_page_ids.add(page_id)
    return entries, {
        "cached_archive_file_count": len(archive_paths),
        "cached_archive_valid_page_count": len(entries),
        "cached_archive_duplicate_page_count": duplicate_count,
        "cached_archive_skipped_count": skipped_count,
        "cached_archive_errors": errors[:20],
    }


def _cached_archive_page_id(payload: dict[str, object]) -> int | None:
    """Return the strict numeric page ID stored in one cached archive."""
    page_id = positive_record_page_id(payload.get("page_id"))
    if page_id is not None:
        return page_id
    parse_payload = payload.get("parse_payload")
    parse_body = parse_payload.get("parse", {}) if isinstance(parse_payload, dict) else {}
    if isinstance(parse_body, dict):
        return positive_record_page_id(parse_body.get("pageid"))
    return None


def _cached_archive_has_parse_material(payload: dict[str, object]) -> bool:
    """Return whether one cached archive has enough parsed content to avoid a fetch."""
    parse_payload = payload.get("parse_payload")
    if isinstance(parse_payload, dict) and isinstance(parse_payload.get("parse"), dict):
        return True
    return bool(str(payload.get("parsed_html") or "").strip())


def _page_id_list_answer_types(args: argparse.Namespace) -> list[str]:
    """Return answer-type contexts represented by this Route 3 streaming run."""
    answer_types = list(getattr(args, "route3_answer_type", []) or [])
    if answer_types:
        return answer_types
    if getattr(args, "route3_answer_type_mode", "") == "all5":
        return list(ROUTE3_ANSWER_TYPES)
    return list(ROUTE3_ANSWER_TYPES)


def _stream_page_id_list_entries(
    processed_ids: list[int],
    *,
    all_decision_records: list[dict],
    answer_types: list[str],
    table_types: list[str],
    page_level_failure_ids: set[int] | None = None,
) -> set[PageIdListEntry]:
    """Return used page-ID entries represented by one streaming run."""
    actual_table_types_by_page = _actual_table_types_by_page_id(all_decision_records)
    entries: set[PageIdListEntry] = set()
    for page_id in processed_ids:
        actual_table_types = actual_table_types_by_page.get(page_id)
        entries.update(
            build_page_id_entries(
                [page_id],
                answer_types=answer_types,
                table_types=sorted(actual_table_types) if actual_table_types else table_types,
            )
        )
    page_only_ids = set(page_level_failure_ids or ()) | {
        page_id
        for record in all_decision_records
        if _all5_page_level_prerewrite_rejected(record)
        for page_id in [positive_record_page_id(record_page_id(record))]
        if page_id is not None
    }
    if not page_only_ids:
        return entries
    return {
        entry
        for entry in entries
        if entry.page_id not in page_only_ids
    } | {PageIdListEntry(page_id=page_id) for page_id in page_only_ids}


def _actual_table_types_by_page_id(records: list[dict]) -> dict[int, set[str]]:
    """Return actual selected table types observed in decision records by page ID."""
    table_types_by_page: dict[int, set[str]] = defaultdict(set)
    for record in records:
        page_id = positive_record_page_id(record_page_id(record))
        if page_id is None:
            continue
        table_type = record_table_type(record)
        if table_type:
            table_types_by_page[page_id].add(table_type)
    return table_types_by_page


def _all5_page_generation_failure(
    candidates: list[GeneratedCandidate],
) -> GeneratedCandidate | None:
    """Return the unassigned diagnostic emitted by an all5 page-level failure."""
    for candidate in candidates:
        metadata = candidate.source_metadata
        if str(metadata.get("answer_type_mode") or "").strip() != "all5":
            continue
        if not str(metadata.get("route3_slot_id") or "").strip():
            return candidate
    return None


def _all5_page_level_prerewrite_rejected(record: dict) -> bool:
    """Return whether one all5 rejected record invalidates the whole page before rewrite."""
    metadata = record.get("source_metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
    if str(metadata.get("answer_type_mode") or "").strip() != "all5":
        return False
    if str(metadata.get("route3_slot_id") or "").strip():
        return False
    if record_answer_type(record) != "unknown":
        return False
    return bool(source_stage_rejection_reason(record))


def _page_ids_from_payload(payload: object) -> set[int]:
    """Extract positive page IDs from common JSON/plain-text payload shapes."""
    page_ids: set[int] = set()
    if isinstance(payload, int):
        if payload > 0:
            page_ids.add(payload)
        return page_ids
    if isinstance(payload, str):
        stripped = payload.strip()
        if stripped.isdigit():
            page_ids.add(int(stripped))
        return page_ids
    if isinstance(payload, list):
        for item in payload:
            page_ids.update(_page_ids_from_payload(item))
        return page_ids
    if isinstance(payload, dict):
        for key in ("page_id", "pageid"):
            page_ids.update(_page_ids_from_payload(payload.get(key)))
        for key in ("page_ids", "used_ids", "accepted_ids", "rejected_ids", "rerun_pool"):
            page_ids.update(_page_ids_from_payload(payload.get(key)))
    return page_ids


def _external_circuit_is_open(*circuits: ServiceCircuit) -> bool:
    """Return whether either formal external-service circuit is open."""
    return any(circuit.is_open for circuit in circuits)


def _build_ddg_verifier_result_store(
    args: argparse.Namespace,
    circuit: ServiceCircuit,
) -> Route3DDGVerifierResultStore:
    """Build the candidate-level DDG result store for one formal segment."""
    manifest_path = (
        args.run_group_segments_dir
        / run_segment_id(args)
        / "segment_manifest.json"
    )
    manifest = load_segment_manifest(manifest_path)
    if manifest is None:
        raise ValueError(f"Missing formal segment manifest: {manifest_path}")
    fingerprint = str(manifest["fingerprint"]["sha256"]).strip()
    return Route3DDGVerifierResultStore(
        root=args.ddg_verifier_result_dir,
        segment_fingerprint=fingerprint,
        circuit=circuit,
    )


def _build_streaming_second_stage_model_panel(
    settings: Settings,
    concurrency: StreamingConcurrencyContext,
    circuit: ServiceCircuit,
):
    """Construct formal Route 3 answer-model factories with bounded transports."""
    if not settings.second_stage_grading_enabled:
        return None
    members: list[ModelPanelMember] = []
    for config in settings.second_stage_grading_models:
        resolved = _resolve_route3_openrouter_config(config, settings)
        factory = Route3OpenRouterClientFactory.from_config(
            resolved,
            timeout_seconds=settings.timeout_seconds,
            circuit=circuit,
        )
        factory.transport = SemaphoreWrappedClient(
            factory.transport,
            concurrency.second_stage_semaphore,
            {"send_once"},
        )
        members.append(ModelPanelMember(name=resolved.model, client=factory))
    return members


def _build_streaming_second_stage_grader_client(
    settings: Settings,
    concurrency: StreamingConcurrencyContext,
    circuit: ServiceCircuit,
):
    """Construct the formal Route 3 grader factory with a bounded transport."""
    if not settings.second_stage_grading_enabled:
        return None
    config = settings.second_stage_grading_grader_llm
    if config is None:
        return None
    resolved = _resolve_route3_openrouter_config(config, settings)
    factory = Route3OpenRouterClientFactory.from_config(
        resolved,
        timeout_seconds=settings.timeout_seconds,
        circuit=circuit,
    )
    factory.transport = SemaphoreWrappedClient(
        factory.transport,
        concurrency.second_stage_semaphore,
        {"send_once"},
    )
    return factory


def _resolve_route3_openrouter_config(config: LLMConfig, settings: Settings) -> LLMConfig:
    """Resolve inherited proxy settings for a formal Route 3 OpenRouter call."""
    if config.provider != "openrouter":
        raise ValueError(f"Formal Route 3 requires OpenRouter, got: {config.provider}")
    if config.proxy is not None:
        return config
    return replace(config, proxy=settings.proxy)


def _process_stream_candidate_slots(
    generated_candidates: list[GeneratedCandidate],
    *,
    attempt_number: int,
    settings: Settings,
    search_client: DuckDuckGoSearchClient,
    ddg_verifier_result_store: Route3DDGVerifierResultStore,
    second_stage_model_clients,
    grading_grader_client,
) -> tuple[list[dict], list[dict]]:
    """Process all5 slots without publishing partial page outcomes."""
    accepted_records: list[dict] = []
    rejected_records: list[dict] = []

    for candidate in generated_candidates:
        try:
            result = process_route3_candidates(
                [candidate],
                settings=settings,
                search_client=search_client,
                ddg_verifier_result_store=ddg_verifier_result_store,
                second_stage_model_clients=second_stage_model_clients,
                grading_grader_client=grading_grader_client,
            )
        except SearchLongtailVerifierError as exc:
            if int(attempt_number) == 1:
                raise
            features = dict(exc.features)
            candidate.search_verification_features = features
            original_error = exc.original_error or exc
            rejected_records.append(
                candidate.to_rejected_record(
                    reason="retry_exhausted:duckduckgo",
                    notes={
                        "error_type": type(original_error).__name__,
                        "error_message": str(original_error),
                        "search_verification_features": features,
                    },
                )
            )
            continue
        except DefiniteOpenRouterHTTPError as exc:
            retryable = openrouter_http_failure_is_retryable(exc.status_code)
            if retryable and int(attempt_number) == 1:
                raise
            rejected_records.append(
                candidate.to_rejected_record(
                    reason=(
                        "retry_exhausted:openrouter"
                        if retryable
                        else f"openrouter_http_error:{exc.status_code}"
                    ),
                    notes={
                        "call_key": exc.call_key,
                        "request_hash": exc.request_hash,
                        "status_code": exc.status_code,
                    },
                )
            )
            continue
        except DefiniteOpenRouterResponseError as exc:
            rejected_records.append(
                candidate.to_rejected_record(
                    reason="openrouter_unparseable_response",
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

        accepted_records.extend(result.accepted)
        rejected_records.extend(result.rejected)

    return accepted_records, rejected_records



def _process_one_stream_page_id(
    page_id: int,
    *,
    args: argparse.Namespace,
    settings: Settings,
    state: PageIdStreamState,
    wikipedia_client: WikipediaClient,
    search_client: DuckDuckGoSearchClient,
    llm_client,
    concurrency: StreamingConcurrencyContext,
    second_stage_model_clients,
    grading_grader_client,
    ddg_verifier_result_store: Route3DDGVerifierResultStore,
    ledger_index: SegmentLedgerIndex,
    source_url: str | None = None,
    stream_page_source: str | None = None,
    cached_archive_path: Path | None = None,
) -> dict:
    """Run one page ID and commit its complete decision to the page-attempt ledger."""
    url = source_url or build_pageid_url(page_id)
    page_source = stream_page_source or args.stream_page_source
    existing = ledger_index.latest_attempt_for(page_id)
    if existing is not None and str(existing.get("status", "")) in {"accepted", "rejected"}:
        accepted, rejected, _ = derived_records([existing])
        return {
            "status": str(existing["status"]),
            "page_id": page_id,
            "url": url,
            "accepted_records": accepted,
            "rejected_records": rejected,
            "reused_committed_ledger": True,
        }
    attempt_number = ledger_index.next_attempt_number(page_id)
    if isinstance(llm_client, Route3OpenRouterClientFactory):
        page_llm_client = bind_route3_allocation_client(
            llm_client,
            record_root=args.external_call_record_dir,
            canonical_page_id=page_id,
            call_key="generation",
            page_attempt_number=attempt_number,
        )
        page_second_stage_model_clients = bind_route3_allocation_panel(
            second_stage_model_clients,
            record_root=args.external_call_record_dir,
            canonical_page_id=page_id,
            page_attempt_number=attempt_number,
        )
        page_grading_grader_client = bind_route3_allocation_client(
            grading_grader_client,
            record_root=args.external_call_record_dir,
            canonical_page_id=page_id,
            call_key="",
            page_attempt_number=attempt_number,
        ) if grading_grader_client is not None else None
    else:
        page_llm_client = llm_client
        page_second_stage_model_clients = second_stage_model_clients
        page_grading_grader_client = grading_grader_client
    generated_candidates: list[GeneratedCandidate] = []
    try:
        generator = WikipediaInfoboxTableGenerator(
            urls=[url],
            wikipedia_client=wikipedia_client,
            llm_client=page_llm_client,
            record_limit=1,
            url_domains={},
            search_query_count=args.generated_search_query_count,
            enable_rest_summary_fallback=False,
            min_table_score=0.0,
            allowed_answer_types=tuple(args.route3_answer_type),
            table_filter_modes=DEFAULT_ROUTE3_TABLE_FILTER_MODES,
            table_source_types=tuple(args.route3_table_source_type),
            prose_leakage_scoring_enabled=True,
            answer_type_mode=args.route3_answer_type_mode,
            page_archive_dir=args.route3_page_archive_dir,
            infobox_max_removed_row_rate=args.route3_infobox_max_removed_row_rate,
            infobox_min_remaining_rows=args.route3_infobox_min_remaining_rows,
            page_archive_paths_by_url={url: cached_archive_path} if cached_archive_path is not None else None,
            read_only_page_archive_paths=(
                (cached_archive_path,)
                if page_source == "cached_page_archive" and cached_archive_path is not None
                else ()
            ),
        )
        generated_candidates = generator.generate(
            run_date=settings.run_date,
            cutoff_year=settings.cutoff_year,
        )
        if not generated_candidates:
            return _commit_stream_page_attempt(
                page_id=page_id,
                url=url,
                attempt_number=attempt_number,
                ledger_index=ledger_index,
                status="rejected",
                reason="no_generated_candidate",
                generated_candidates=[],
                accepted_records=[],
                rejected_records=[],
                error_details={},
                args=args,
                state=state,
                concurrency=concurrency,
            )
        for candidate in generated_candidates:
            _attach_stream_metadata(
                candidate,
                page_id=page_id,
                url=url,
                args=args,
                page_source=page_source,
                cached_archive_path=cached_archive_path,
            )
        page_failure = _all5_page_generation_failure(generated_candidates)
        if page_failure is not None:
            diagnostic_record = page_failure.to_output_record("")
            rejection_reason = str(page_failure.notes[0] if page_failure.notes else "").strip()
            diagnostic_record["rejection_reason"] = rejection_reason or "wikipedia_infobox_generation_failed"
            reason = exact_failure_reason(diagnostic_record)
            error_details = _rerun_error_details_from_record(diagnostic_record)
            discard_reason = str(page_failure.source_metadata.get("discard_reason") or "").strip()
            if discard_reason:
                error_details["discard_reason"] = discard_reason
            return _commit_stream_page_attempt(
                page_id=page_id,
                url=url,
                attempt_number=attempt_number,
                ledger_index=ledger_index,
                status="rejected",
                reason=reason,
                generated_candidates=[],
                accepted_records=[],
                rejected_records=[],
                error_details=error_details,
                args=args,
                state=state,
                concurrency=concurrency,
                generation_raw_audit=_generation_raw_audit(generated_candidates),
                page_level_failure=True,
            )
        accepted_records, rejected_records = _process_stream_candidate_slots(
            generated_candidates,
            attempt_number=attempt_number,
            settings=settings,
            search_client=search_client,
            ddg_verifier_result_store=ddg_verifier_result_store,
            second_stage_model_clients=page_second_stage_model_clients,
            grading_grader_client=page_grading_grader_client,
        )
        for record in [*accepted_records, *rejected_records]:
            _attach_stream_record_metadata(
                record,
                page_id=page_id,
                url=url,
                args=args,
                page_source=page_source,
                cached_archive_path=cached_archive_path,
            )
            ensure_page_id_list_entry_metadata(record)
            record["id"] = _wikipedia_stream_record_id(record)
        if accepted_records:
            return _commit_stream_page_attempt(
                page_id=page_id,
                url=url,
                attempt_number=attempt_number,
                ledger_index=ledger_index,
                status="accepted",
                reason="accepted",
                generated_candidates=generated_candidates,
                accepted_records=_accepted_output_records(accepted_records, args),
                rejected_records=_rejected_output_records(rejected_records, args),
                error_details={},
                args=args,
                state=state,
                concurrency=concurrency,
            )
        if rejected_records:
            reason = exact_failure_reason(rejected_records[0])
            return _commit_stream_page_attempt(
                page_id=page_id,
                url=url,
                attempt_number=attempt_number,
                ledger_index=ledger_index,
                status="rejected",
                reason=reason,
                generated_candidates=generated_candidates,
                accepted_records=[],
                rejected_records=_rejected_output_records(rejected_records, args),
                error_details={},
                args=args,
                state=state,
                concurrency=concurrency,
            )
        raise RuntimeError("Pipeline produced neither accepted nor rejected records")
    except CircuitOpenError as exc:
        return {
            "status": "blocked_external_service",
            "state": "blocked_external_service",
            "service": exc.service,
            "reason": exc.reason,
            "page_id": page_id,
            "url": url,
            "attempt": attempt_number,
            "accepted_records": [],
            "rejected_records": [],
        }
    except AmbiguousExternalCallError as exc:
        return {
            "status": "ambiguous_external_call",
            "state": "ambiguous_external_call",
            "page_id": page_id,
            "url": url,
            "attempt": attempt_number,
            "call_attempt": exc.call_attempt,
            "call_key": exc.call_key,
            "accepted_records": [],
            "rejected_records": [],
        }
    except SearchLongtailVerifierError as exc:
        return _commit_typed_infrastructure_failure(
            page_id=page_id,
            url=url,
            attempt_number=attempt_number,
            ledger_index=ledger_index,
            service="duckduckgo",
            generated_candidates=generated_candidates,
            error_details={
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            },
            args=args,
            state=state,
            concurrency=concurrency,
        )
    except DefiniteOpenRouterHTTPError as exc:
        if openrouter_http_failure_is_retryable(exc.status_code):
            return _commit_typed_infrastructure_failure(
                page_id=page_id,
                url=url,
                attempt_number=attempt_number,
                ledger_index=ledger_index,
                service="openrouter",
                generated_candidates=generated_candidates,
                error_details={
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "call_key": exc.call_key,
                    "status_code": str(exc.status_code),
                },
                args=args,
                state=state,
                concurrency=concurrency,
            )
        return _commit_stream_page_attempt(
            page_id=page_id,
            url=url,
            attempt_number=attempt_number,
            ledger_index=ledger_index,
            status="rejected",
            reason=f"openrouter_http_error:{exc.status_code}",
            generated_candidates=generated_candidates,
            accepted_records=[],
            rejected_records=[],
            error_details={
                "call_key": exc.call_key,
                "status_code": str(exc.status_code),
            },
            args=args,
            state=state,
            concurrency=concurrency,
        )
    except AbandonedExternalCallError as exc:
        return _commit_stream_page_attempt(
            page_id=page_id,
            url=url,
            attempt_number=attempt_number,
            ledger_index=ledger_index,
            status="rejected",
            reason="abandoned_ambiguous_external_call",
            generated_candidates=generated_candidates,
            accepted_records=[],
            rejected_records=[],
            error_details={
                "call_key": exc.call_key,
                "call_attempt": str(exc.call_attempt),
            },
            args=args,
            state=state,
            concurrency=concurrency,
        )


def _commit_typed_infrastructure_failure(
    *,
    page_id: int,
    url: str,
    attempt_number: int,
    ledger_index: SegmentLedgerIndex,
    service: str,
    generated_candidates: list[GeneratedCandidate],
    error_details: dict[str, str],
    args: argparse.Namespace,
    state: PageIdStreamState,
    concurrency: StreamingConcurrencyContext,
) -> dict:
    """Commit the sole retry eligibility transition for typed infrastructure failures."""
    retry_pending = int(attempt_number) == 1
    return _commit_stream_page_attempt(
        page_id=page_id,
        url=url,
        attempt_number=attempt_number,
        ledger_index=ledger_index,
        status="retryable_failure" if retry_pending else "rejected",
        reason=(
            f"{service}_infrastructure_failure"
            if retry_pending
            else f"retry_exhausted:{service}"
        ),
        generated_candidates=generated_candidates,
        accepted_records=[],
        rejected_records=[],
        error_details=error_details,
        args=args,
        state=state,
        concurrency=concurrency,
    )
def _commit_stream_page_attempt(
    *,
    page_id: int,
    url: str,
    attempt_number: int,
    ledger_index: SegmentLedgerIndex,
    status: str,
    reason: str,
    generated_candidates: list[GeneratedCandidate],
    accepted_records: list[dict],
    rejected_records: list[dict],
    error_details: dict[str, str],
    args: argparse.Namespace,
    state: PageIdStreamState,
    concurrency: StreamingConcurrencyContext,
    generation_raw_audit: dict[str, Any] | None = None,
    page_level_failure: bool = False,
) -> dict:
    """Commit one ledger record before rebuilding endpoints and updating state."""
    for candidate in generated_candidates:
        candidate.source_metadata["page_attempt"] = attempt_number
    for record in [*accepted_records, *rejected_records]:
        record["source_metadata"]["page_attempt"] = attempt_number
    candidate_snapshots = [candidate.to_output_record("") for candidate in generated_candidates]
    for record in candidate_snapshots:
        record["id"] = _wikipedia_stream_record_id(record)
    raw_audit = (
        generation_raw_audit
        if generation_raw_audit is not None
        else _generation_raw_audit(generated_candidates)
    )
    candidate_ids = [str(record["id"]) for record in candidate_snapshots]
    timings = [
        dict(record.get("source_metadata", {}).get("phase_timings_seconds", {}))
        for record in [*accepted_records, *rejected_records]
        if isinstance(record.get("source_metadata"), dict)
    ]
    payload = {
        "run_group_id": run_group_id(args),
        "segment_id": run_segment_id(args),
        "canonical_page_id": page_id,
        "canonical_page_url": url,
        "attempt_number": attempt_number,
        "status": status,
        "reason": reason,
        "generation_raw_audit": raw_audit,
        "candidates": candidate_snapshots,
        "ddg": [record.get("search_verification_features", {}) for record in candidate_snapshots],
        "second_stage": [record.get("panel_grading_features", {}) for record in candidate_snapshots],
        "accepted_records": accepted_records,
        "rejected_records": rejected_records,
        "candidate_ids": candidate_ids,
        "timings": timings,
        "error_details": dict(error_details),
    }
    if page_level_failure:
        payload["page_level_failure"] = True
    with concurrency.commit_lock:
        ledger_path = ledger_index.commit_attempt(payload)
        if status == "accepted":
            state.mark_accepted(page_id)
        elif status == "rejected":
            state.mark_rejected(page_id, reason=reason)
        else:
            state.mark_retryable_failure(page_id, reason=reason, **error_details)
    return {
        "status": status,
        "page_id": page_id,
        "url": url,
        "accepted_records": accepted_records if status == "accepted" else [],
        "rejected_records": rejected_records if status in {"accepted", "rejected"} else [],
        "reason": reason,
        "ledger_path": str(ledger_path),
        **error_details,
    }


def _generation_raw_audit(candidates: list[GeneratedCandidate]) -> dict[str, Any]:
    """Collect generation prompt, request, response, and archive hashes for one page."""
    rows: list[dict[str, Any]] = []
    for candidate in candidates:
        metadata = candidate.source_metadata if isinstance(candidate.source_metadata, dict) else {}
        audit = metadata.get("llm_audit", {})
        archive = metadata.get("route3_page_archive", {})
        rows.append(
            {
                "slot": metadata.get("original_candidate_slot") or metadata.get("route3_slot_id") or "",
                "prompt": metadata.get("llm_prompt", ""),
                "request": audit.get("request_payload", {}) if isinstance(audit, dict) else {},
                "response": metadata.get("llm_response", {}),
                "audit": audit if isinstance(audit, dict) else {},
                "page_archive_hash": archive.get("archive_sha256", "") if isinstance(archive, dict) else "",
            }
        )
    return {"slots": rows}

def _reserve_stream_page_ids(
    *,
    state: PageIdStreamState,
    args: argparse.Namespace,
    wikipedia_client: WikipediaClient,
    rng: random.Random,
    count: int,
    excluded_page_ids: set[int],
) -> list[int]:
    """Reserve fresh page IDs from the formal table-search discovery source."""
    selected: list[int] = []

    queries = _stream_search_queries()
    rounds = 0
    while len(selected) < count and rounds < args.stream_search_max_rounds:
        rounds += 1
        made_progress = False
        for query in queries:
            offset = state.table_search_offset(query)
            hits = _search_page_ids_with_retries(
                wikipedia_client,
                query=query,
                namespace=0,
                limit=args.stream_search_limit,
                offset=offset,
                args=args,
                state=state,
            )
            if hits is None:
                continue
            state.advance_table_search_offset(query, args.stream_search_limit)
            reserved: list[int] = []
            for hit in hits:
                page_id = hit.page_id
                if page_id in excluded_page_ids or page_id in selected or page_id in reserved:
                    continue
                reserved.append(page_id)
                if len(reserved) >= count - len(selected):
                    break
            if reserved:
                state.used_ids.update(reserved)
                state.in_progress_ids.update(reserved)
                state._record_event(
                    "reserve_table_search_pages",
                    reserved,
                    f"table_search:{query}:offset={offset}",
                )
                state.save()
            if hits:
                made_progress = True
            _extend_unique_page_ids(selected, reserved)
            if len(selected) >= count:
                break
        if not made_progress:
            break
    return selected


def _search_page_ids_with_retries(
    wikipedia_client: WikipediaClient,
    *,
    query: str,
    namespace: int,
    limit: int,
    offset: int,
    args: argparse.Namespace,
    state: PageIdStreamState,
) -> list | None:
    """Search page IDs with retry/backoff for transient discovery failures."""
    max_retries = max(0, int(getattr(args, "stream_discovery_max_retries", 0) or 0))
    base_sleep = max(0.0, float(getattr(args, "stream_discovery_retry_backoff_seconds", 0.0) or 0.0))
    max_sleep = max(0.0, float(getattr(args, "stream_discovery_retry_max_sleep_seconds", 0.0) or 0.0))
    source = f"table_search:{query}:offset={offset}"
    for attempt in range(max_retries + 1):
        try:
            return wikipedia_client.search_page_ids(
                query,
                namespace=namespace,
                limit=limit,
                offset=offset,
            )
        except Exception as exc:  # noqa: BLE001
            error = f"{type(exc).__name__}:{exc}"
            if attempt >= max_retries:
                state.record_discovery_error(source=source, error=f"{error};retries_exhausted={max_retries}")
                return None
            sleep_seconds = min(max_sleep, base_sleep * (2 ** attempt)) if max_sleep else base_sleep * (2 ** attempt)
            state.record_discovery_error(source=source, error=f"{error};retry={attempt + 1}/{max_retries};sleep={sleep_seconds:.2f}")
            if sleep_seconds > 0:
                sleep(sleep_seconds)


def _extend_unique_page_ids(selected: list[int], reserved: list[int]) -> None:
    """Append reserved page IDs while preserving one occurrence per batch."""
    seen = set(selected)
    for raw_page_id in reserved:
        try:
            page_id = int(raw_page_id)
        except (TypeError, ValueError):
            continue
        if page_id in seen:
            continue
        selected.append(page_id)
        seen.add(page_id)


def _stream_search_queries() -> list[str]:
    """Return the fixed formal table-search queries."""
    return list(DEFAULT_TABLE_SEARCH_QUERIES)


def _attach_stream_metadata(
    candidate: GeneratedCandidate,
    *,
    page_id: int,
    url: str,
    args: argparse.Namespace,
    page_source: str | None = None,
    cached_archive_path: Path | None = None,
) -> None:
    """Attach stream sampling metadata to a generated candidate."""
    _ensure_small_model_response_metadata(candidate.source_metadata)
    _attach_run_artifact_metadata(candidate.source_metadata, args=args)
    candidate.source_metadata["table_filter_modes"] = list(args.route3_table_filter_mode)
    candidate.source_metadata["canonical_page_id"] = page_id
    if args.route3_answer_type_mode == "single":
        candidate.source_metadata["original_candidate_slot"] = "single"
    elif candidate.source_metadata.get("route3_slot_id"):
        candidate.source_metadata["original_candidate_slot"] = candidate.source_metadata["route3_slot_id"]
    candidate.source_metadata["table_source_types"] = list(args.route3_table_source_type)
    candidate.source_metadata["prose_leakage_scoring_enabled"] = bool(args.route3_prose_leakage_scoring)
    candidate.source_metadata["page_id"] = page_id
    candidate.source_metadata["stream_source_url"] = url
    candidate.source_metadata["streaming_discovery"] = _streaming_discovery_metadata(
        page_id=page_id,
        url=url,
        args=args,
        page_source=page_source,
        cached_archive_path=cached_archive_path,
    )


def _attach_stream_record_metadata(
    record: dict,
    *,
    page_id: int,
    url: str,
    args: argparse.Namespace,
    page_source: str | None = None,
    cached_archive_path: Path | None = None,
) -> None:
    """Attach stream sampling metadata to a serialized output record."""
    metadata = record.setdefault("source_metadata", {})
    if isinstance(metadata, dict):
        _ensure_small_model_response_metadata(metadata)
        _attach_run_artifact_metadata(metadata, args=args)
        metadata["table_filter_modes"] = list(args.route3_table_filter_mode)
        metadata["canonical_page_id"] = page_id
        if args.route3_answer_type_mode == "single":
            metadata["original_candidate_slot"] = "single"
        elif metadata.get("route3_slot_id"):
            metadata["original_candidate_slot"] = metadata["route3_slot_id"]
        metadata["table_source_types"] = list(args.route3_table_source_type)
        metadata["prose_leakage_scoring_enabled"] = bool(args.route3_prose_leakage_scoring)
        metadata["page_id"] = page_id
        metadata["stream_source_url"] = url
        metadata["streaming_discovery"] = _streaming_discovery_metadata(
            page_id=page_id,
            url=url,
            args=args,
            page_source=page_source,
            cached_archive_path=cached_archive_path,
        )


def _streaming_discovery_metadata(
    *,
    page_id: int,
    url: str,
    args: argparse.Namespace,
    page_source: str | None = None,
    cached_archive_path: Path | None = None,
) -> dict[str, object]:
    """Return stream source metadata for fresh or cached page processing."""
    source = page_source or args.stream_page_source
    metadata: dict[str, object] = {
        "mode": "page_id_stream",
        "page_source": source,
        "page_id": page_id,
        "pageid_url": build_pageid_url(page_id),
        "source_url": url,
        "random_seed": args.stream_random_seed,
        "domain_policy": "domain_and_subdomain_optional",
    }
    if cached_archive_path is not None:
        metadata["cached_archive_reuse"] = True
        metadata["cached_archive_path"] = str(cached_archive_path)
    return metadata


def _attach_run_artifact_metadata(metadata: dict, *, args: argparse.Namespace) -> None:
    """Attach run-group artifact IDs when artifact indexing is enabled."""
    artifact_group_id = run_group_id(args)
    if not artifact_group_id:
        return
    metadata["run_group_id"] = artifact_group_id
    metadata["segment_id"] = run_segment_id(args)
    metadata["generation_model"] = args.generation_model
    metadata["generation_parameters"] = {"max_tokens": args.small_model_max_tokens}
    metadata["recipe_seed"] = args.stream_random_seed
    manifest_path = _run_artifact_manifest_path(args, artifact_group_id)
    if manifest_path is not None:
        metadata["run_artifact_manifest"] = str(manifest_path)


def _ensure_small_model_response_metadata(metadata: dict) -> None:
    """Keep explicit small-model response keys alongside legacy metadata names."""
    llm_response = metadata.get("llm_response")
    if isinstance(llm_response, dict) and "small_model_qa_response" not in metadata:
        metadata["small_model_qa_response"] = llm_response


















































def _rerun_error_details_from_record(record: dict) -> dict[str, str]:
    """Return retryable error details stored on a rejected record."""
    details: dict[str, str] = {}
    for source in (
        record,
        record.get("rejection_notes", {}),
        record.get("source_metadata", {}),
    ):
        if not isinstance(source, dict):
            continue
        for key in ("error_type", "error_message"):
            if details.get(key):
                continue
            text = str(source.get(key) or "").strip()
            if text:
                details[key] = text
    notes = record.get("rejection_notes", {})
    if isinstance(notes, dict):
        features = notes.get("search_verification_features", {})
        if isinstance(features, dict):
            query_errors = features.get("query_errors", [])
            if isinstance(query_errors, list) and query_errors:
                first_error = query_errors[0]
                if isinstance(first_error, dict):
                    for source_key, target_key in (
                        ("query_name", "query_name"),
                        ("query_category", "query_category"),
                        ("query", "query"),
                        ("duration_seconds", "query_duration_seconds"),
                    ):
                        text = str(first_error.get(source_key) or "").strip()
                        if text and not details.get(target_key):
                            details[target_key] = text
                    attempts = first_error.get("search_request_events", [])
                    if isinstance(attempts, list):
                        details.setdefault("search_attempt_count", str(len(attempts)))
                        if attempts and isinstance(attempts[-1], dict):
                            last_attempt = attempts[-1]
                            for source_key, target_key in (
                                ("path", "last_attempt_path"),
                                ("duration_ms", "last_attempt_duration_ms"),
                                ("error_type", "last_attempt_error_type"),
                                ("error_message", "last_attempt_error_message"),
                                ("http_status", "last_attempt_http_status"),
                            ):
                                text = str(last_attempt.get(source_key) or "").strip()
                                if text and not details.get(target_key):
                                    details[target_key] = text
    return details

































































def _escape_inline_code(value: str) -> str:
    return value.replace("`", "'").replace("\n", " ").strip()




def _load_urls(cli_urls: list[str], url_file: Path | None) -> list[str]:
    """Load URLs from repeated CLI flags and an optional file."""
    return [entry.url for entry in _load_url_entries(cli_urls, url_file)]


def _load_url_entries(cli_urls: list[str], url_file: Path | None) -> list[UrlEntry]:
    """Load URL entries from repeated CLI flags and an optional file."""
    entries = [UrlEntry(url=url.strip()) for url in cli_urls if url.strip()]
    if url_file is not None:
        for line in url_file.read_text(encoding="utf-8").splitlines():
            entry = _parse_url_file_line(line)
            if entry is not None:
                entries.append(entry)
    return entries


def _parse_url_file_line(line: str) -> UrlEntry | None:
    """Parse ``url``, ``domain<TAB>url``, or ``domain<TAB>subdomain<TAB>url`` lines."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    parts = [part.strip() for part in stripped.split("\t")]
    if len(parts) >= 3:
        return UrlEntry(url=parts[2], domain=parts[0], subdomain=parts[1])
    if len(parts) == 2:
        domain, url = parts
        return UrlEntry(url=url, domain=domain)
    return UrlEntry(url=stripped)


def _url_domain_map(entries: list[UrlEntry]) -> dict[str, str]:
    """Build lookup keys used by the Route 3 generator."""
    mapping: dict[str, str] = {}
    for entry in entries:
        if not entry.domain:
            continue
        mapping[entry.url] = entry.domain
        title = normalize_wikipedia_title(entry.url)
        if title:
            mapping[title] = entry.domain
            mapping[title.replace(" ", "_")] = entry.domain
    return mapping


def _optional_proxy(value: str) -> str | None:
    """Normalize CLI proxy values."""
    if value.strip().lower() in {"", "none", "direct", "off"}:
        return None
    return value




if __name__ == "__main__":
    raise SystemExit(main())
