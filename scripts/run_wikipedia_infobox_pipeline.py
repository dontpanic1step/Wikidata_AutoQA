"""Run the Wikipedia infobox/table QA route over supplied page URLs."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from json import JSONDecodeError
from pathlib import Path
from threading import Lock, Semaphore
from time import perf_counter, sleep

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.cheap_model_qa import make_cheap_model_qa_client
from wikidata_simpleqa.config import LLMConfig, Settings
from wikidata_simpleqa.generation_models import EntityReference, EvidenceRecord, GeneratedCandidate
from wikidata_simpleqa.generation_pipeline import (
    build_second_stage_grader_client,
    build_second_stage_model_panel,
    process_generated_candidates,
)
from wikidata_simpleqa.io import append_jsonl, write_jsonl
from wikidata_simpleqa.llm_rewrite import make_rewrite_client
from wikidata_simpleqa.page_id_lists import (
    PageIdListEntry,
    build_page_id_entries,
    page_ids_excluded_for_context,
    read_page_id_entries,
)
from wikidata_simpleqa.route3_ids import assign_unique_route3_record_ids, route3_record_id
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
    DEFAULT_ROUTE3_MAX_MONTHLY_AVERAGE_PAGEVIEWS,
    DEFAULT_ROUTE3_MAX_UNDERFILLED_MONTHLY_PAGEVIEWS,
    DEFAULT_ROUTE3_PAGE_ARCHIVE_DIR,
    DEFAULT_ROUTE3_PAGEVIEW_PREFILTER_ENABLED,
    DEFAULT_ROUTE3_PAGEVIEW_UNAVAILABLE_POLICY,
    DEFAULT_ROUTE3_PAGEVIEW_WINDOW_MONTHS,
    DEFAULT_ROUTE3_PROSE_LEAKAGE_SCORING_ENABLED,
    DEFAULT_ROUTE3_REASONING_TYPES,
    DEFAULT_ROUTE3_TABLE_FILTER_MODES,
    DEFAULT_ROUTE3_TABLE_SOURCE_TYPES,
    ROUTE3_ANSWER_TYPES,
    WikipediaInfoboxTableGenerator,
    _answer_items,
    _normalize_answer_type,
    _normalize_generated_answer,
    _reasoning_type,
    _sanitize_answer_blind_queries,
    normalize_route3_answer_types,
    normalize_route3_answer_type_mode,
    normalize_route3_extra_prompts,
    normalize_route3_pageview_unavailable_policy,
    normalize_route3_reasoning_types,
    normalize_route3_table_filter_modes,
    normalize_route3_table_source_types,
)
from wikidata_simpleqa.wikipedia_streaming import (
    BROAD_TABLE_SEARCH_QUERY,
    DEFAULT_PAGE_ID_MAX,
    DEFAULT_PAGE_ID_MIN,
    DEFAULT_TABLE_SEARCH_QUERIES,
    PageIdStreamState,
    build_pageid_url,
)

DEFAULT_STREAM_RANDOM_SEED = 42


def _apply_big_batch_mode(args: argparse.Namespace) -> None:
    """Apply large-run defaults that keep 10k-style recipes resumable."""
    if not getattr(args, "big_batch_mode", False):
        return
    if getattr(args, "stream_random_page_ids", False) and getattr(args, "stream_page_source", "") == "table-search":
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
class EndpointResumeState:
    """Accepted/rejected endpoint files used as a resume checkpoint."""

    enabled: bool = False
    accepted_records: list[dict] = field(default_factory=list)
    rejected_records: list[dict] = field(default_factory=list)
    skipped_lines: list[dict[str, object]] = field(default_factory=list)

    @property
    def accepted_count(self) -> int:
        return len(self.accepted_records)

    @property
    def rejected_count(self) -> int:
        return len(self.rejected_records)

    @property
    def final_decision_count(self) -> int:
        return self.accepted_count + self.rejected_count

    def summary(self) -> dict[str, object]:
        return {
            "enabled": self.enabled,
            "accepted_records_loaded": self.accepted_count,
            "rejected_records_loaded": self.rejected_count,
            "final_decisions_loaded": self.final_decision_count,
            "skipped_malformed_lines": len(self.skipped_lines),
            "skipped_line_details": self.skipped_lines[:20],
        }


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


def _safe_artifact_id(value: str, *, fallback: str = "") -> str:
    """Return a path-safe artifact identifier."""
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip()).strip("._-")
    if cleaned:
        return cleaned
    return fallback


def _run_group_id(args: argparse.Namespace) -> str:
    """Return the normalized run group ID for artifact indexing."""
    return _safe_artifact_id(str(getattr(args, "run_group_id", "") or ""))


def _run_segment_id(args: argparse.Namespace) -> str:
    """Return the normalized run segment ID for artifact indexing."""
    raw_value = str(getattr(args, "run_segment_id", "") or "").strip()
    if not raw_value:
        raw_value = Path(getattr(args, "summary_output")).stem
    return _safe_artifact_id(raw_value, fallback="segment")


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
    run_group_id = _run_group_id(args)
    if not run_group_id:
        return {}
    manifest_path = _run_artifact_manifest_path(args, run_group_id)
    return {
        "run_group_id": run_group_id,
        "run_segment_id": _run_segment_id(args),
        "run_artifact_manifest": str(manifest_path) if manifest_path is not None else "",
    }


def _stable_stream_seed(*parts: object, default: int = DEFAULT_STREAM_RANDOM_SEED) -> int:
    """Return a deterministic non-zero 31-bit seed from stable run identity parts."""
    text = "|".join(str(part) for part in parts if str(part or "").strip())
    if not text:
        return default
    digest = hashlib.blake2s(text.encode("utf-8"), digest_size=8).hexdigest()
    seed = int(digest, 16) & 0x7FFFFFFF
    return seed or default


def _effective_stream_random_seed(args: argparse.Namespace, endpoint_resume: EndpointResumeState | None = None) -> int:
    """Return the configured seed, or derive a run-specific default seed."""
    configured_seed = getattr(args, "stream_random_seed", None)
    if configured_seed is not None:
        return int(configured_seed)
    resume_count = endpoint_resume.final_decision_count if endpoint_resume is not None else 0
    return _stable_stream_seed(
        "wikipedia_stream",
        _run_group_id(args),
        _run_segment_id(args),
        getattr(args, "summary_output", ""),
        getattr(args, "stream_state", ""),
        "endpoint_resume" if getattr(args, "start_from_endpoint", False) else "",
        resume_count if getattr(args, "start_from_endpoint", False) else "",
        "rerun_pool_only" if getattr(args, "stream_rerun_pool_only", False) else "",
    )


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the Wikipedia table route."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", action="append", default=[], help="Wikipedia URL. Can be repeated.")
    parser.add_argument("--url-file", type=Path, default=None, help="Text file with one Wikipedia URL per line.")
    parser.add_argument(
        "--stream-random-page-ids",
        action="store_true",
        help="Stream Wikipedia page IDs and process action=parse&pageid records incrementally.",
    )
    parser.add_argument(
        "--stream-state",
        type=Path,
        default=ROOT / "outputs" / "wikipedia_infobox_stream_state.json",
        help="Persistent page-id cache, in-progress list, and rerun pool for streaming mode.",
    )
    parser.add_argument("--stream-page-id-min", type=int, default=DEFAULT_PAGE_ID_MIN)
    parser.add_argument("--stream-page-id-max", type=int, default=DEFAULT_PAGE_ID_MAX)
    parser.add_argument(
        "--stream-page-source",
        choices=["table-search", "random-page-id"],
        default="table-search",
        help="How streaming mode finds page IDs before action=parse&pageid processing.",
    )
    parser.add_argument(
        "--stream-search-query",
        action="append",
        default=[],
        help="MediaWiki srsearch query for table-search mode. Can be repeated.",
    )
    parser.add_argument(
        "--enable-broad-table-search",
        action="store_true",
        help=r"Also include the broad MediaWiki table query insource:/\{\|/. Off by default.",
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
        "--stream-exclude-page-id-file",
        action="append",
        type=Path,
        default=[],
        help=(
            "File containing page IDs or page_id/answer_type/table_type entries that streaming discovery must skip."
        ),
    )
    parser.add_argument(
        "--stream-random-seed",
        type=int,
        default=None,
        help=(
            "Seed for random-page-id streaming. When omitted, a deterministic seed is derived "
            "from the run/segment identity so resumed or incremental runs do not reuse the same stream."
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
        "--stream-accepted-target",
        type=int,
        default=0,
        help="Optional accepted-record target; 0 means process --record-limit page IDs.",
    )
    parser.add_argument(
        "--stream-rerun-pool-only",
        action="store_true",
        help="Process the current streaming rerun pool once and do not discover fresh page IDs.",
    )
    parser.add_argument(
        "--stream-rerun-pool-limit",
        type=int,
        default=0,
        help="Maximum rerun-pool IDs to process with --stream-rerun-pool-only; 0 means the whole pool.",
    )
    parser.add_argument(
        "--stream-rerun-pool-seed-file",
        action="append",
        default=[],
        type=Path,
        help="JSON/JSONL file containing rerun-pool page IDs to seed into this stream state before discovery.",
    )
    parser.add_argument(
        "--stream-reuse-cached-page-count",
        type=int,
        default=0,
        help=(
            "Process up to this many already parsed Route 3 page archives from --route3-page-archive-dir "
            "before discovering fresh streaming page IDs. 0 disables cache reuse."
        ),
    )
    parser.add_argument(
        "--stream-reuse-cached-page-used-id-file",
        action="append",
        default=[],
        type=Path,
        help=(
            "Helper-generated used-ID JSON/JSONL/plain file for cached page reuse. "
            "Page-only and triadic entries are treated as strict numeric page-level exclusions."
        ),
    )
    parser.add_argument(
        "--stream-prefer-rerun-pool",
        action="store_true",
        help="In normal streaming mode, reserve rerun-pool IDs before discovering fresh page IDs.",
    )
    parser.add_argument(
        "--stream-free-seeded-rerun-pool-on-completion",
        action="store_true",
        help="When the configured page/accepted target is reached, clear any seeded rerun-pool IDs that remain unresolved.",
    )
    parser.add_argument(
        "--stream-auto-rerun-once",
        action="store_true",
        help="After the normal streaming pass, immediately process the rerun pool once, then stop.",
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
        "--candidate-input",
        action="append",
        default=[],
        type=Path,
        help="Existing accepted/rejected JSONL candidate file. Can be repeated.",
    )
    parser.add_argument(
        "--start-stage",
        choices=["generate", "validation"],
        default="generate",
        help="Start from URL generation or from existing post-rewrite candidates.",
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
    parser.add_argument("--target-time", type=str, default="2024")
    parser.add_argument("--run-date", type=str, default=None)
    parser.add_argument("--cutoff-year", type=int, default=2025)
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--duckduckgo-top-k", type=int, default=5)
    parser.add_argument("--duckduckgo-parallel-queries", type=int, default=3)
    add_duckduckgo_transport_args(parser)
    parser.add_argument("--generated-search-query-count", type=int, default=2)
    parser.add_argument(
        "--min-table-score",
        type=float,
        default=0.0,
        help="Drop Route 3 candidate tables with rank score below this value before paragraph/alias extraction and LLM generation.",
    )
    parser.add_argument(
        "--route3-reasoning-type",
        action="append",
        default=[],
        help=(
            "Restrict Route 3 generation to one or more reasoning_type values. "
            "Repeat the flag or pass comma-separated values. Default: single_fact."
        ),
    )
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
        "--route3-extra-prompt",
        action="append",
        default=[],
        help=(
            "Add a stricter Route 3 prompt rule by passing literal prompt text. Can be repeated. "
            "Social-science table exclusion is now a default table filter mode."
        ),
    )
    parser.add_argument(
        "--route3-table-filter-mode",
        action="append",
        default=list(DEFAULT_ROUTE3_TABLE_FILTER_MODES),
        help=(
            "Enable one or more early Route 3 table filter modes. Repeat the flag or pass comma-separated "
            "values. Defaults: no_external_links_tables,no_horizontal_companion_tables,"
            "no_picture_heavy_tables,no_incomplete_tables,not_number_dominant,no_social_science_research."
        ),
    )
    parser.add_argument(
        "--disable-route3-table-filter-mode",
        action="append",
        default=[],
        help="Disable a default Route 3 table filter mode for this run. Can be repeated.",
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
        "--route3-prose-leakage-scoring",
        action=argparse.BooleanOptionalAction,
        default=DEFAULT_ROUTE3_PROSE_LEAKAGE_SCORING_ENABLED,
        help=(
            "Enable the lightweight prose-leakage rank signal. Default: enabled "
            "(leakage <0.2 adds 0.5; leakage >0.8 subtracts 0.5)."
        ),
    )
    parser.add_argument(
        "--route3-llm-choose-table",
        action=argparse.BooleanOptionalAction,
        default=False,
        help=(
            "Let the Route 3 generation LLM choose among the top three surviving ranked tables. "
            "By default only the single top-ranked table is passed."
        ),
    )
    parser.add_argument(
        "--route3-page-archive-dir",
        type=Path,
        default=ROOT / DEFAULT_ROUTE3_PAGE_ARCHIVE_DIR,
        help="Directory for unified Route 3 page archives containing parse HTML and pageview metadata.",
    )
    parser.add_argument(
        "--route3-pageview-prefilter",
        action=argparse.BooleanOptionalAction,
        default=DEFAULT_ROUTE3_PAGEVIEW_PREFILTER_ENABLED,
        help=(
            "Enable the optional Route 3 pageview popularity prefilter before table grading "
            "and LLM generation. Disabled by default."
        ),
    )
    parser.add_argument(
        "--route3-pageview-window-months",
        type=int,
        default=DEFAULT_ROUTE3_PAGEVIEW_WINDOW_MONTHS,
        help="Complete monthly pageview window used by the Route 3 prefilter.",
    )
    parser.add_argument(
        "--route3-max-monthly-average-pageviews",
        type=float,
        default=DEFAULT_ROUTE3_MAX_MONTHLY_AVERAGE_PAGEVIEWS,
        help="Maximum allowed monthly average pageviews for Route 3 pageview prefilter.",
    )
    parser.add_argument(
        "--route3-max-underfilled-monthly-pageviews",
        type=float,
        default=DEFAULT_ROUTE3_MAX_UNDERFILLED_MONTHLY_PAGEVIEWS,
        help=(
            "Maximum allowed single-month pageviews when the Route 3 pageview response contains fewer months "
            "than --route3-pageview-window-months."
        ),
    )
    parser.add_argument(
        "--route3-pageview-unavailable-policy",
        choices=["allow", "reject", "rerun"],
        default=DEFAULT_ROUTE3_PAGEVIEW_UNAVAILABLE_POLICY,
        help="Route 3 decision when pageview data is unavailable.",
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
    parser.add_argument("--proxy", type=str, default="socks5://127.0.0.1:7897")
    parser.add_argument("--small-model-provider", type=str, default="openrouter")
    parser.add_argument("--small-model", type=str, default="openai/gpt-4.1-mini")
    parser.add_argument("--small-model-api-key-env", type=str, default="OPENROUTER_API_KEY")
    parser.add_argument("--small-model-base-url", type=str, default="https://openrouter.ai/api/v1")
    parser.add_argument("--small-model-max-tokens", type=int, default=1200)
    parser.add_argument(
        "--enable-rest-summary-fallback",
        action="store_true",
        help="Fetch REST page summaries only when action=parse HTML has no first paragraph. Off by default.",
    )
    parser.add_argument("--enable-rewrite", action="store_true")
    parser.add_argument("--rewrite-model", type=str, default="openai/gpt-4.1-mini")
    parser.add_argument("--enable-second-stage-grading", action="store_true")
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
    return parser.parse_args()


def main() -> int:
    """Run the Wikipedia table route and persist outputs."""
    args = parse_args()
    _apply_big_batch_mode(args)
    endpoint_resume = _load_endpoint_resume(args)
    args.stream_random_seed_was_explicit = args.stream_random_seed is not None
    args.stream_random_seed = _effective_stream_random_seed(args, endpoint_resume)
    url_entries = _load_url_entries(args.url, args.url_file)
    skipped_endpoint_urls: list[str] = []
    effective_record_limit = args.record_limit
    if args.start_from_endpoint and args.start_stage == "generate" and not args.stream_random_page_ids:
        url_entries, skipped_endpoint_urls = _filter_endpoint_url_entries(url_entries, endpoint_resume)
        effective_record_limit = _remaining_after_endpoint(args.record_limit, endpoint_resume.final_decision_count)
    urls = [entry.url for entry in url_entries]
    if args.stream_random_page_ids and args.start_stage != "generate":
        raise ValueError("--stream-random-page-ids only supports --start-stage generate.")
    if args.stream_random_page_ids and args.stream_batch_size < 1:
        raise ValueError("--stream-batch-size must be at least 1.")
    if args.stream_random_page_ids and args.stream_search_limit < 1:
        raise ValueError("--stream-search-limit must be at least 1.")
    if args.stream_random_page_ids and args.stream_search_max_rounds < 1:
        raise ValueError("--stream-search-max-rounds must be at least 1.")
    if args.stream_random_page_ids and args.stream_discovery_max_retries < 0:
        raise ValueError("--stream-discovery-max-retries must be non-negative.")
    if args.stream_random_page_ids and args.stream_discovery_retry_backoff_seconds < 0:
        raise ValueError("--stream-discovery-retry-backoff-seconds must be non-negative.")
    if args.stream_random_page_ids and args.stream_discovery_retry_max_sleep_seconds < 0:
        raise ValueError("--stream-discovery-retry-max-sleep-seconds must be non-negative.")
    if args.stream_random_page_ids and args.stream_page_workers < 1:
        raise ValueError("--stream-page-workers must be at least 1.")
    if args.stream_random_page_ids and args.wikipedia_concurrency_limit < 1:
        raise ValueError("--wikipedia-concurrency-limit must be at least 1.")
    if args.stream_random_page_ids and args.duckduckgo_concurrency_limit < 1:
        raise ValueError("--duckduckgo-concurrency-limit must be at least 1.")
    if args.stream_random_page_ids and args.openrouter_generation_rewrite_concurrency_limit < 1:
        raise ValueError("--openrouter-generation-rewrite-concurrency-limit must be at least 1.")
    if args.stream_random_page_ids and args.second_stage_concurrency_limit < 1:
        raise ValueError("--second-stage-concurrency-limit must be at least 1.")
    if args.wikipedia_429_backoff_seconds < 0:
        raise ValueError("--wikipedia-429-backoff-seconds must be non-negative.")
    if args.wikipedia_429_max_backoff_seconds < 0:
        raise ValueError("--wikipedia-429-max-backoff-seconds must be non-negative.")
    if args.wikipedia_429_recovery_seconds < 0:
        raise ValueError("--wikipedia-429-recovery-seconds must be non-negative.")
    if args.stream_random_page_ids and args.stream_rerun_pool_limit < 0:
        raise ValueError("--stream-rerun-pool-limit must be non-negative.")
    if args.stream_random_page_ids and args.stream_reuse_cached_page_count < 0:
        raise ValueError("--stream-reuse-cached-page-count must be non-negative.")
    if args.stream_free_seeded_rerun_pool_on_completion and not args.stream_prefer_rerun_pool:
        raise ValueError("--stream-free-seeded-rerun-pool-on-completion requires --stream-prefer-rerun-pool.")
    if args.reset_stream_state and not args.stream_random_page_ids:
        raise ValueError("--reset-stream-state only applies to streaming page-ID runs.")
    if args.reset_stream_state and args.start_from_endpoint:
        raise ValueError("--reset-stream-state cannot be combined with --start-from-endpoint.")
    if args.reset_stream_state and args.stream_rerun_pool_only:
        raise ValueError("--reset-stream-state cannot be combined with --stream-rerun-pool-only.")
    if args.run_artifact_manifest is not None and not args.run_group_id.strip():
        raise ValueError("--run-artifact-manifest requires --run-group-id.")
    args.route3_reasoning_type = list(
        normalize_route3_reasoning_types(args.route3_reasoning_type) or DEFAULT_ROUTE3_REASONING_TYPES
    )
    args.route3_answer_type = list(normalize_route3_answer_types(args.route3_answer_type))
    args.route3_extra_prompt = list(normalize_route3_extra_prompts(args.route3_extra_prompt))
    enabled_table_filter_modes = list(normalize_route3_table_filter_modes(args.route3_table_filter_mode))
    disabled_table_filter_modes = set(normalize_route3_table_filter_modes(args.disable_route3_table_filter_mode))
    args.route3_table_filter_mode = [
        mode for mode in enabled_table_filter_modes if mode not in disabled_table_filter_modes
    ]
    args.route3_table_source_type = list(
        normalize_route3_table_source_types(args.route3_table_source_type or DEFAULT_ROUTE3_TABLE_SOURCE_TYPES)
    )
    args.route3_answer_type_mode = normalize_route3_answer_type_mode(args.route3_answer_type_mode)
    args.route3_pageview_unavailable_policy = normalize_route3_pageview_unavailable_policy(
        args.route3_pageview_unavailable_policy
    )
    args.route3_pageview_window_months = max(1, int(args.route3_pageview_window_months))
    args.route3_max_monthly_average_pageviews = float(args.route3_max_monthly_average_pageviews)
    args.route3_max_underfilled_monthly_pageviews = float(args.route3_max_underfilled_monthly_pageviews)
    args.route3_infobox_max_removed_row_rate = max(0.0, min(1.0, float(args.route3_infobox_max_removed_row_rate)))
    args.route3_infobox_min_remaining_rows = max(0, int(args.route3_infobox_min_remaining_rows))
    if args.start_stage == "generate" and not urls and not args.stream_random_page_ids and effective_record_limit > 0:
        raise ValueError("Provide at least one Wikipedia URL with --url or --url-file.")
    if args.start_stage == "validation" and not args.candidate_input:
        raise ValueError("Provide --candidate-input when --start-stage validation is used.")
    proxy = _optional_proxy(args.proxy)
    small_llm = LLMConfig(
        provider=args.small_model_provider,
        model=args.small_model,
        api_key_env=args.small_model_api_key_env,
        base_url=args.small_model_base_url,
        proxy=proxy,
        max_tokens=args.small_model_max_tokens,
    )
    rewrite_llm = None
    if args.enable_rewrite:
        rewrite_llm = LLMConfig(
            provider=args.small_model_provider,
            model=args.rewrite_model,
            api_key_env=args.small_model_api_key_env,
            base_url=args.small_model_base_url,
            proxy=proxy,
        )
    settings = Settings(
        target_time=args.target_time,
        run_date=args.run_date or Settings(target_time=args.target_time).run_date,
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
        output_path=args.output,
        rejected_output_path=args.rejected_output,
        rewrite_enabled=args.enable_rewrite,
        rewrite_llm=rewrite_llm,
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
    llm_client = make_cheap_model_qa_client(small_llm, settings.timeout_seconds)
    rewrite_client = make_rewrite_client(settings.rewrite_llm, settings.timeout_seconds) if settings.rewrite_enabled else None
    if args.stream_random_page_ids:
        summary = _run_streaming_page_id_pipeline(
            args=args,
            settings=settings,
            wikipedia_client=wikipedia_client,
            search_client=search_client,
            llm_client=llm_client,
            rewrite_client=rewrite_client,
            endpoint_resume=endpoint_resume,
        )
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0
    if args.start_stage == "validation":
        generated_candidates = _load_candidate_inputs(args.candidate_input, limit=effective_record_limit)
        for candidate in generated_candidates:
            _apply_allowed_reasoning_type_filter(candidate, args.route3_reasoning_type)
            _apply_allowed_answer_type_filter(candidate, args.route3_answer_type)
            _attach_route3_extra_prompts(candidate, args.route3_extra_prompt)
            _attach_route3_table_filter_modes(candidate, args.route3_table_filter_mode)
            _attach_route3_table_source_types(candidate, args.route3_table_source_type)
            _attach_route3_prose_leakage_scoring(candidate, args.route3_prose_leakage_scoring)
        if not generated_candidates:
            raise ValueError("No candidates were loaded from --candidate-input.")
        if not url_entries:
            url_entries = _url_entries_from_candidates(generated_candidates)
    else:
        generator = WikipediaInfoboxTableGenerator(
            urls=urls,
            wikipedia_client=wikipedia_client,
            llm_client=llm_client,
            record_limit=effective_record_limit,
            url_domains=_url_domain_map(url_entries),
            search_query_count=args.generated_search_query_count,
            enable_rest_summary_fallback=args.enable_rest_summary_fallback,
            min_table_score=args.min_table_score,
            allowed_reasoning_types=tuple(args.route3_reasoning_type),
            allowed_answer_types=tuple(args.route3_answer_type),
            extra_prompts=tuple(args.route3_extra_prompt),
            table_filter_modes=tuple(args.route3_table_filter_mode),
            table_source_types=tuple(args.route3_table_source_type),
            prose_leakage_scoring_enabled=args.route3_prose_leakage_scoring,
            llm_choose_table=args.route3_llm_choose_table,
            answer_type_mode=args.route3_answer_type_mode,
            page_archive_dir=args.route3_page_archive_dir,
            pageview_prefilter_enabled=args.route3_pageview_prefilter,
            pageview_window_months=args.route3_pageview_window_months,
            max_monthly_average_pageviews=args.route3_max_monthly_average_pageviews,
            max_underfilled_monthly_pageviews=args.route3_max_underfilled_monthly_pageviews,
            pageview_unavailable_policy=args.route3_pageview_unavailable_policy,
            infobox_max_removed_row_rate=args.route3_infobox_max_removed_row_rate,
            infobox_min_remaining_rows=args.route3_infobox_min_remaining_rows,
            page_archive_paths_by_url={url: cached_archive_path} if cached_archive_path is not None else None,
        )
        generated_candidates = generator.generate(
            run_date=settings.run_date,
            cutoff_year=settings.cutoff_year,
        )
    result = process_generated_candidates(
        generated_candidates,
        settings=settings,
        search_client=search_client,
        rewrite_client=rewrite_client,
    )
    _renumber_accepted_records(
        result.accepted,
        offset=endpoint_resume.accepted_count if args.start_from_endpoint else 0,
        run_date=settings.run_date,
    )
    if args.start_from_endpoint:
        append_jsonl(args.output, _accepted_output_records(result.accepted, args))
        append_jsonl(args.rejected_output, _rejected_output_records(result.rejected, args))
    else:
        write_jsonl(args.output, _accepted_output_records(result.accepted, args))
        write_jsonl(args.rejected_output, _rejected_output_records(result.rejected, args))
    summary = {
        **_run_artifact_summary(args),
        "start_stage": args.start_stage,
        "start_from_endpoint": args.start_from_endpoint,
        "endpoint_resume": endpoint_resume.summary(),
        "candidate_input_paths": [str(path) for path in args.candidate_input],
        "attempted_urls": (
            min(len(urls), effective_record_limit)
            if args.start_stage == "generate"
            else len(generated_candidates)
        ),
        "skipped_endpoint_urls": skipped_endpoint_urls,
        "url_domains": [
            {"url": entry.url, "domain": entry.domain}
            | ({"subdomain": entry.subdomain} if entry.subdomain else {})
            for entry in url_entries[: effective_record_limit]
        ],
        "generated": len(generated_candidates),
        "accepted": len(result.accepted),
        "accepted_total": endpoint_resume.accepted_count + len(result.accepted),
        "rejected": len(result.rejected),
        "rejected_total": endpoint_resume.rejected_count + len(result.rejected),
        "record_limit": args.record_limit,
        "record_limit_remaining_at_start": effective_record_limit,
        "output_path": str(args.output),
        "rejected_output_path": str(args.rejected_output),
        "summary_output": str(args.summary_output),
        "enabled_routes": list(settings.enabled_routes),
        "rest_summary_fallback_enabled": args.enable_rest_summary_fallback,
        "small_model": args.small_model,
        "rewrite_enabled": settings.rewrite_enabled,
        "second_stage_grading_enabled": settings.second_stage_grading_enabled,
        "duckduckgo_top_k": settings.duckduckgo_top_k,
        "duckduckgo_parallel_queries": settings.duckduckgo_parallel_queries,
        **duckduckgo_summary_fields(settings),
        "generated_search_query_count": settings.generated_search_query_count,
        "min_table_score": args.min_table_score,
        "route3_reasoning_types": args.route3_reasoning_type,
        "route3_answer_types": args.route3_answer_type,
        "route3_extra_prompts": args.route3_extra_prompt,
        "route3_table_filter_modes": args.route3_table_filter_mode,
        "route3_table_source_types": args.route3_table_source_type,
        "route3_prose_leakage_scoring_enabled": bool(args.route3_prose_leakage_scoring),
        "route3_llm_choose_table": bool(args.route3_llm_choose_table),
        "route3_answer_type_mode": args.route3_answer_type_mode,
        "route3_page_archive_dir": str(args.route3_page_archive_dir),
        "route3_pageview_prefilter_enabled": bool(args.route3_pageview_prefilter),
        "route3_pageview_window_months": args.route3_pageview_window_months,
        "route3_max_monthly_average_pageviews": args.route3_max_monthly_average_pageviews,
        "route3_max_underfilled_monthly_pageviews": args.route3_max_underfilled_monthly_pageviews,
        "route3_pageview_unavailable_policy": args.route3_pageview_unavailable_policy,
        "route3_infobox_max_removed_row_rate": args.route3_infobox_max_removed_row_rate,
        "route3_infobox_min_remaining_rows": args.route3_infobox_min_remaining_rows,
        "compact_output": False,
        "compact_output_ignored": bool(args.compact_output or args.big_batch_mode),
        "compact_rejected_output": False,
        "compact_rejected_output_ignored": bool(args.compact_rejected_output or args.compact_output or args.big_batch_mode),
        "wikipedia_429_backoff_seconds": args.wikipedia_429_backoff_seconds,
        "wikipedia_429_max_backoff_seconds": args.wikipedia_429_max_backoff_seconds,
        "wikipedia_429_recovery_seconds": args.wikipedia_429_recovery_seconds,
        "aggregate_phase_timings_seconds": _aggregate_phase_timings(result.accepted, result.rejected),
        "telemetry": {
            **result.telemetry,
            "wikipedia": wikipedia_client.request_events.copy(),
            "search": search_client.request_events.copy(),
        },
    }
    _write_summary_and_manifest(args, summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


def _load_endpoint_resume(args: argparse.Namespace) -> EndpointResumeState:
    """Load existing accepted/rejected output files when endpoint resume is enabled."""
    if not getattr(args, "start_from_endpoint", False):
        return EndpointResumeState(enabled=False)
    accepted_records, accepted_skipped = _load_endpoint_jsonl(args.output, label="accepted")
    rejected_records, rejected_skipped = _load_endpoint_jsonl(args.rejected_output, label="rejected")
    return EndpointResumeState(
        enabled=True,
        accepted_records=accepted_records,
        rejected_records=rejected_records,
        skipped_lines=[*accepted_skipped, *rejected_skipped],
    )


def _load_endpoint_jsonl(path: Path, *, label: str) -> tuple[list[dict], list[dict[str, object]]]:
    """Load a JSONL endpoint, tolerating a malformed trailing line from a crash."""
    if not path.exists():
        return [], []
    records: list[dict] = []
    skipped: list[dict[str, object]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except JSONDecodeError as exc:
            skipped.append(
                {
                    "path": str(path),
                    "endpoint": label,
                    "line_number": line_number,
                    "error": str(exc),
                }
            )
            continue
        if isinstance(value, dict):
            records.append(value)
        else:
            skipped.append(
                {
                    "path": str(path),
                    "endpoint": label,
                    "line_number": line_number,
                    "error": "non_object_jsonl_record",
                }
            )
    return records, skipped


def _write_summary_and_manifest(args: argparse.Namespace, summary: dict) -> None:
    """Write the invocation summary and update its optional run-group manifest."""
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
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
        "stream_rerun_pool_only": bool(summary.get("stream_rerun_pool_only", False)),
        "stream_auto_rerun_once": bool(summary.get("stream_auto_rerun_once", False)),
        "stream_reused_cached_page_count": summary.get("stream_reused_cached_page_count", 0),
        "route3_reasoning_types": summary.get("route3_reasoning_types", []),
        "route3_answer_types": summary.get("route3_answer_types", []),
        "route3_extra_prompts": summary.get("route3_extra_prompts", []),
        "route3_table_filter_modes": summary.get("route3_table_filter_modes", []),
        "route3_table_source_types": summary.get("route3_table_source_types", []),
        "route3_prose_leakage_scoring_enabled": bool(summary.get("route3_prose_leakage_scoring_enabled", True)),
        "record_limit": summary.get("record_limit", 0),
        "attempted_page_ids": summary.get("attempted_page_ids", summary.get("attempted_urls", 0)),
        "auto_rerun_attempted_page_ids": summary.get("auto_rerun_attempted_page_ids", 0),
        "accepted": summary.get("accepted", 0),
        "accepted_total": summary.get("accepted_total", summary.get("accepted", 0)),
        "rejected": summary.get("rejected", 0),
        "rejected_total": summary.get("rejected_total", summary.get("rejected", 0)),
        "rerun": summary.get("rerun", 0),
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
        payload["run_segment_id"] = _safe_artifact_id(
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
    """Atomically write one JSON document."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.tmp")
    temp_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temp_path.replace(path)


def _remaining_after_endpoint(record_limit: int, final_decision_count: int) -> int:
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


def _renumber_accepted_records(records: list[dict], *, offset: int, run_date: str = "") -> None:
    """Assign stable Route 3 IDs, with legacy sequential IDs only as a fallback."""
    for record in records:
        _ensure_page_id_list_entry_metadata(record)
    assign_unique_route3_record_ids(records, run_date=run_date)
    for index, record in enumerate(records, start=offset + 1):
        if not str(record.get("id") or "").strip():
            record["id"] = f"simpleqa_candidate_{index:06d}"


def _jsonl_record_count(path: Path) -> int:
    """Return the number of non-empty JSONL lines already written."""
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def _wikipedia_stream_record_id(record: dict, index: int, *, run_date: str = "") -> str:
    """Return a stable stream ID, falling back to the legacy local sequence when needed."""
    stable_id = route3_record_id(record, run_date=run_date)
    if stable_id:
        return stable_id
    answer_type_slug = re.sub(r"[^a-z0-9]+", "_", _record_answer_type(record).lower()).strip("_")
    return f"{answer_type_slug or 'unknown'}_wikipedia_stream_{index:06d}"


def _accepted_output_records(records: list[dict], args: argparse.Namespace) -> list[dict]:
    """Return accepted records in the configured output shape."""
    for record in records:
        _ensure_page_id_list_entry_metadata(record)
    return records


def _rejected_output_records(records: list[dict], args: argparse.Namespace) -> list[dict]:
    """Return rejected records in the configured output shape."""
    for record in records:
        _ensure_page_id_list_entry_metadata(record)
    return records


def _ensure_page_id_list_entry_metadata(record: dict) -> None:
    """Attach an explicit triadic page-ID entry when record metadata supports it."""
    if not isinstance(record, dict):
        return
    metadata = record.setdefault("source_metadata", {})
    if not isinstance(metadata, dict):
        return
    page_id = _record_page_id(record)
    answer_type = _record_answer_type(record)
    table_type = _record_table_type(record)
    if not page_id or not answer_type or answer_type == "unknown" or not table_type:
        return
    metadata["page_id"] = page_id
    metadata["page_id_list_entry"] = {
        "page_id": page_id,
        "answer_type": answer_type,
        "table_type": table_type,
    }


def _record_table_type(record: dict) -> str:
    """Return the actual Route 3 table type represented by one output record."""
    metadata = record.get("source_metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
    selected = metadata.get("selected_source_table")
    if isinstance(selected, dict):
        table_type = _normalize_record_table_type(selected.get("table_type"))
        if table_type:
            return table_type
    for source in (record, metadata):
        if not isinstance(source, dict):
            continue
        for key in ("table_type", "source_channel", "recipe_table_type"):
            table_type = _normalize_record_table_type(source.get(key))
            if table_type:
                return table_type
    source_types = metadata.get("table_source_types")
    if isinstance(source_types, list) and len(source_types) == 1:
        return _normalize_record_table_type(source_types[0])
    return ""


def _normalize_record_table_type(value: object) -> str:
    """Normalize one record table-type value for page-ID entries."""
    text = str(value or "").strip()
    if not text:
        return ""
    try:
        normalized = normalize_route3_table_source_types([text])
    except ValueError:
        return ""
    return normalized[0] if len(normalized) == 1 else ""


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
    page_id = _record_page_id(record)
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
        "failing_reason": _exact_failure_reason(record),
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
    rewrite_client,
    endpoint_resume: EndpointResumeState,
) -> dict:
    """Process random Wikipedia page IDs and append decisions incrementally."""
    run_started = perf_counter()
    if llm_client is None:
        raise ValueError("Streaming Route 3 requires a small-model client.")
    concurrency = _build_streaming_concurrency_context(args)
    wikipedia_client = SemaphoreWrappedClient(
        wikipedia_client,
        concurrency.wikipedia_semaphore,
        {"fetch_summary", "fetch_parse", "fetch_pageviews", "search_page_ids"},
    )
    search_client = SemaphoreWrappedClient(
        search_client,
        concurrency.duckduckgo_semaphore,
        {"search"},
    )
    llm_client = SemaphoreWrappedClient(
        llm_client,
        concurrency.generation_rewrite_semaphore,
        {"complete_text", "complete_text_with_audit"},
    )
    if rewrite_client is not None:
        rewrite_client = SemaphoreWrappedClient(
            rewrite_client,
            concurrency.generation_rewrite_semaphore,
            {"rewrite_question", "rewrite_question_with_audit"},
        )
    second_stage_model_clients = _build_streaming_second_stage_model_panel(settings, concurrency)
    grading_grader_client = _build_streaming_second_stage_grader_client(settings, concurrency)
    if args.reset_stream_state:
        state = PageIdStreamState(path=args.stream_state)
        state.save()
    else:
        state = PageIdStreamState.load(args.stream_state)
    excluded_page_ids = _load_stream_excluded_page_ids(
        args.stream_exclude_page_id_file,
        answer_types=_page_id_list_answer_types(args),
        table_types=args.route3_table_source_type,
    )
    if excluded_page_ids:
        state.used_ids.update(excluded_page_ids)
        state._record_event("stream_exclude_page_ids", sorted(excluded_page_ids), "external_exclusion_file")
        state.save()
    seeded_rerun_pool_ids = sorted(_load_stream_excluded_page_ids(args.stream_rerun_pool_seed_file))
    seeded_rerun_pool_ids = state.seed_rerun_pool(
        seeded_rerun_pool_ids,
        reason="external_rerun_pool_seed_file",
    )
    _initialize_table_search_offsets(state, args)
    endpoint_sync = {"accepted_ids_synced": 0, "rejected_ids_synced": 0}
    if args.start_from_endpoint:
        endpoint_sync = state.sync_decided_ids(
            accepted_ids=_endpoint_page_ids(endpoint_resume.accepted_records),
            rejected_ids=_endpoint_page_ids(endpoint_resume.rejected_records),
        )
    recovered_ids = state.recover_stale_in_progress()
    rng = random.Random(args.stream_random_seed)
    processed_ids: list[int] = []
    accepted_records: list[dict] = []
    rejected_records: list[dict] = []
    rerun_records: list[dict] = []
    accepted_target = max(0, int(args.stream_accepted_target or 0))
    if args.start_from_endpoint and accepted_target:
        accepted_target = max(0, accepted_target - endpoint_resume.accepted_count)
    if args.stream_rerun_pool_only:
        ids_remaining = _stream_rerun_pool_run_limit(state, args)
    else:
        ids_remaining = max(0, int(args.record_limit))
    if args.start_from_endpoint and not args.stream_rerun_pool_only:
        ids_remaining = _remaining_after_endpoint(args.record_limit, endpoint_resume.final_decision_count)
    initial_ids_remaining = ids_remaining
    page_workers = 1 if accepted_target else max(1, int(args.stream_page_workers))
    auto_rerun_pool_ids_at_start: list[int] = []
    auto_rerun_processed_ids: list[int] = []
    cached_page_reuse_entries: list[CachedPageArchiveEntry] = []
    cached_page_reuse_summary = _stream_cached_page_reuse_disabled_summary(args)

    if args.stream_reuse_cached_page_count > 0:
        cached_page_reuse_entries, cached_page_reuse_summary = _reserve_stream_cached_page_archives(
            state=state,
            args=args,
        )
        if cached_page_reuse_entries:
            processed_ids.extend(entry.page_id for entry in cached_page_reuse_entries)
            futures = {}
            with ThreadPoolExecutor(max_workers=min(page_workers, len(cached_page_reuse_entries))) as executor:
                for index, entry in enumerate(cached_page_reuse_entries):
                    futures[
                        executor.submit(
                            _process_one_stream_page_id,
                            entry.page_id,
                            args=args,
                            settings=settings,
                            state=state,
                            wikipedia_client=wikipedia_client,
                            search_client=search_client,
                            llm_client=llm_client,
                            rewrite_client=rewrite_client,
                            concurrency=concurrency,
                            second_stage_model_clients=second_stage_model_clients,
                            grading_grader_client=grading_grader_client,
                            source_url=entry.source_url,
                            stream_page_source="cached_page_archive",
                            cached_archive_path=entry.archive_path,
                        )
                    ] = index
                for future in as_completed(futures):
                    index = futures[future]
                    decision = future.result()
                    accepted_records.extend(decision.get("accepted_records", []))
                    rejected_records.extend(decision.get("rejected_records", []))
                    if decision.get("status") == "rerun":
                        rerun_records.append(decision)
                    if accepted_target and len(accepted_records) >= accepted_target:
                        for pending_future in futures:
                            pending_future.cancel()
                        for unprocessed_entry in cached_page_reuse_entries[index + 1 :]:
                            with concurrency.commit_lock:
                                state.mark_rerun(
                                    unprocessed_entry.page_id,
                                    reason="accepted_target_reached_before_processing",
                                )
                        break

    while ids_remaining > 0:
        if accepted_target and len(accepted_records) >= accepted_target:
            break
        batch_size = 1 if accepted_target else min(max(1, int(args.stream_batch_size)), ids_remaining)
        reserved_ids = _reserve_stream_page_ids(
            state=state,
            args=args,
            wikipedia_client=wikipedia_client,
            rng=rng,
            count=batch_size,
            rerun_pool_only=args.stream_rerun_pool_only,
            prefer_rerun_pool=args.stream_rerun_pool_only or args.stream_prefer_rerun_pool,
        )
        if not reserved_ids:
            break
        ids_remaining -= len(reserved_ids)
        processed_ids.extend(reserved_ids)
        futures = {}
        with ThreadPoolExecutor(max_workers=min(page_workers, len(reserved_ids))) as executor:
            for index, page_id in enumerate(reserved_ids):
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
                        rewrite_client=rewrite_client,
                        concurrency=concurrency,
                        second_stage_model_clients=second_stage_model_clients,
                        grading_grader_client=grading_grader_client,
                    )
                ] = index
            for future in as_completed(futures):
                index = futures[future]
                decision = future.result()
                accepted_records.extend(decision.get("accepted_records", []))
                rejected_records.extend(decision.get("rejected_records", []))
                if decision.get("status") == "rerun":
                    rerun_records.append(decision)
                if accepted_target and len(accepted_records) >= accepted_target:
                    for pending_future in futures:
                        pending_future.cancel()
                    for unprocessed_page_id in reserved_ids[index + 1 :]:
                        with concurrency.commit_lock:
                            state.mark_rerun(
                                unprocessed_page_id,
                                reason="accepted_target_reached_before_processing",
                            )
                    break

    seeded_rerun_pool_ids_freed_on_completion: list[int] = []
    target_reached = ids_remaining <= 0 or (accepted_target > 0 and len(accepted_records) >= accepted_target)
    if args.stream_free_seeded_rerun_pool_on_completion and target_reached and seeded_rerun_pool_ids:
        seeded_rerun_pool_ids_freed_on_completion = state.clear_rerun_pool(
            seeded_rerun_pool_ids,
            free_unused_page_ids=True,
            reason="stream_target_reached_free_seeded_rerun_pool",
        )

    if args.stream_auto_rerun_once and not args.stream_rerun_pool_only and state.rerun_pool:
        auto_rerun_pool_ids_at_start = state.rerun_pool.copy()
        auto_ids_remaining = len(auto_rerun_pool_ids_at_start)
        while auto_ids_remaining > 0:
            batch_size = min(max(1, int(args.stream_batch_size)), auto_ids_remaining)
            reserved_ids = _reserve_stream_page_ids(
                state=state,
                args=args,
                wikipedia_client=wikipedia_client,
                rng=rng,
                count=batch_size,
                rerun_pool_only=True,
                prefer_rerun_pool=True,
            )
            if not reserved_ids:
                break
            auto_ids_remaining -= len(reserved_ids)
            processed_ids.extend(reserved_ids)
            auto_rerun_processed_ids.extend(reserved_ids)
            futures = {}
            with ThreadPoolExecutor(max_workers=min(page_workers, len(reserved_ids))) as executor:
                for index, page_id in enumerate(reserved_ids):
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
                            rewrite_client=rewrite_client,
                            concurrency=concurrency,
                            second_stage_model_clients=second_stage_model_clients,
                            grading_grader_client=grading_grader_client,
                        )
                    ] = index
                for future in as_completed(futures):
                    decision = future.result()
                    accepted_records.extend(decision.get("accepted_records", []))
                    rejected_records.extend(decision.get("rejected_records", []))
                    if decision.get("status") == "rerun":
                        rerun_records.append(decision)

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
        "stream_page_source": args.stream_page_source,
        "stream_search_queries": _stream_search_queries(args),
        "stream_broad_table_search_enabled": args.enable_broad_table_search,
        "stream_search_offsets": state.table_search_offsets.copy(),
        "stream_excluded_page_ids": len(excluded_page_ids),
        "stream_exclude_page_id_files": [str(path) for path in args.stream_exclude_page_id_file],
        "run_date": settings.run_date,
        "stream_state": str(args.stream_state),
        "stream_state_stats": state.stats(),
        "stream_state_reset": bool(args.reset_stream_state),
        "stream_rerun_pool_only": bool(args.stream_rerun_pool_only),
        "stream_rerun_pool_limit": args.stream_rerun_pool_limit,
        "stream_rerun_pool_seed_files": [str(path) for path in args.stream_rerun_pool_seed_file],
        "stream_reuse_cached_page_count": args.stream_reuse_cached_page_count,
        "stream_reuse_cached_page_used_id_files": [str(path) for path in args.stream_reuse_cached_page_used_id_file],
        "stream_cached_page_reuse": cached_page_reuse_summary,
        "stream_reused_cached_page_ids": [entry.page_id for entry in cached_page_reuse_entries],
        "stream_reused_cached_page_count": len(cached_page_reuse_entries),
        "stream_prefer_rerun_pool": bool(args.stream_prefer_rerun_pool),
        "seeded_rerun_pool_ids": seeded_rerun_pool_ids,
        "seeded_rerun_pool_ids_freed_on_completion": seeded_rerun_pool_ids_freed_on_completion,
        "stream_auto_rerun_once": bool(args.stream_auto_rerun_once),
        "auto_rerun_pool_ids_at_start": auto_rerun_pool_ids_at_start,
        "auto_rerun_processed_page_ids": auto_rerun_processed_ids,
        "auto_rerun_attempted_page_ids": len(auto_rerun_processed_ids),
        "rerun_pool_ids_after_run": state.rerun_pool.copy(),
        "rerun_pool_failure_reasons_after_run": {
            str(page_id): state.failure_reasons.get(page_id, "")
            for page_id in state.rerun_pool
        },
        "rerun_pool_error_details_after_run": {
            str(page_id): state.rerun_error_details.get(page_id, {})
            for page_id in state.rerun_pool
            if state.rerun_error_details.get(page_id)
        },
        "recovered_stale_in_progress_ids": recovered_ids,
        "page_id_bounds": {
            "min": args.stream_page_id_min,
            "max": args.stream_page_id_max,
        },
        "random_seed": args.stream_random_seed,
        "random_seed_was_explicit": bool(getattr(args, "stream_random_seed_was_explicit", False)),
        "record_limit": args.record_limit,
        "record_limit_remaining_at_start": initial_ids_remaining,
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
        "stream_accepted_target": args.stream_accepted_target,
        "stream_accepted_target_remaining_at_start": accepted_target,
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
                )
            )
        ],
        "accepted": len(accepted_records),
        "accepted_total": endpoint_resume.accepted_count + len(accepted_records),
        "rejected": len(rejected_records),
        "rejected_total": endpoint_resume.rejected_count + len(rejected_records),
        "rerun": len(rerun_records),
        "wall_clock_seconds": round(perf_counter() - run_started, 4),
        "output_path": str(args.output),
        "rejected_output_path": str(args.rejected_output),
        "summary_output": str(args.summary_output),
        "walkthrough_output": str(args.walkthrough_output) if args.walkthrough_output else "",
        "domain_policy": "domain_and_subdomain_optional_for_page_id_streaming",
        "enabled_routes": list(settings.enabled_routes),
        "rest_summary_fallback_enabled": args.enable_rest_summary_fallback,
        "small_model": args.small_model,
        "rewrite_enabled": settings.rewrite_enabled,
        "second_stage_grading_enabled": settings.second_stage_grading_enabled,
        "duckduckgo_top_k": settings.duckduckgo_top_k,
        "duckduckgo_parallel_queries": settings.duckduckgo_parallel_queries,
        **duckduckgo_summary_fields(settings),
        "generated_search_query_count": settings.generated_search_query_count,
        "min_table_score": args.min_table_score,
        "route3_reasoning_types": args.route3_reasoning_type,
        "route3_answer_types": args.route3_answer_type,
        "route3_extra_prompts": args.route3_extra_prompt,
        "route3_table_filter_modes": args.route3_table_filter_mode,
        "route3_table_source_types": args.route3_table_source_type,
        "route3_prose_leakage_scoring_enabled": bool(args.route3_prose_leakage_scoring),
        "route3_llm_choose_table": bool(args.route3_llm_choose_table),
        "route3_answer_type_mode": args.route3_answer_type_mode,
        "route3_page_archive_dir": str(args.route3_page_archive_dir),
        "route3_pageview_prefilter_enabled": bool(args.route3_pageview_prefilter),
        "route3_pageview_window_months": args.route3_pageview_window_months,
        "route3_max_monthly_average_pageviews": args.route3_max_monthly_average_pageviews,
        "route3_max_underfilled_monthly_pageviews": args.route3_max_underfilled_monthly_pageviews,
        "route3_pageview_unavailable_policy": args.route3_pageview_unavailable_policy,
        "route3_infobox_max_removed_row_rate": args.route3_infobox_max_removed_row_rate,
        "route3_infobox_min_remaining_rows": args.route3_infobox_min_remaining_rows,
        "compact_output": False,
        "compact_output_ignored": bool(args.compact_output or args.big_batch_mode),
        "compact_rejected_output": False,
        "compact_rejected_output_ignored": bool(args.compact_rejected_output or args.compact_output or args.big_batch_mode),
        "survival_by_layer": _survival_by_layer(
            attempted_count=len(processed_ids),
            rejected_records=rejected_records,
            rerun_records=rerun_records,
        ),
        "failure_reason_counts": _failure_reason_counts(rejected_records, rerun_records),
        "phase_timing_stats_seconds": _phase_timing_stats(all_decision_records),
        "aggregate_phase_timings_seconds": _aggregate_phase_timings(accepted_records, rejected_records),
        "telemetry": {
            "wikipedia": wikipedia_client.request_events.copy(),
            "search": search_client.request_events.copy(),
        },
    }
    if args.walkthrough_output is not None:
        _write_stream_walkthrough(
            path=args.walkthrough_output,
            summary=summary,
            accepted_records=accepted_records,
            rejected_records=rejected_records,
            rerun_records=rerun_records,
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


def _stream_rerun_pool_run_limit(state: PageIdStreamState, args: argparse.Namespace) -> int:
    """Return how many rerun-pool IDs this invocation should attempt."""
    pool_size = len(state.rerun_pool)
    configured_limit = max(0, int(getattr(args, "stream_rerun_pool_limit", 0) or 0))
    if configured_limit:
        return min(pool_size, configured_limit)
    return pool_size


def _initialize_table_search_offsets(state: PageIdStreamState, args: argparse.Namespace) -> None:
    """Seed table-search offsets for fresh segmented stream states."""
    initial_offset = max(0, int(getattr(args, "stream_search_initial_offset", 0) or 0))
    if not initial_offset or getattr(args, "stream_page_source", "") != "table-search":
        return
    changed = False
    for query in _stream_search_queries(args):
        if state.table_search_offset(query) >= initial_offset:
            continue
        state.table_search_offsets[query] = initial_offset
        state._record_event("initialize_table_search_offset", [], f"{query}:{initial_offset}")
        changed = True
    if changed:
        state.save()


def _load_stream_excluded_page_ids(
    paths: list[Path],
    *,
    answer_types: list[str] | tuple[str, ...] | None = None,
    table_types: list[str] | tuple[str, ...] | None = None,
) -> set[int]:
    """Load page IDs that the stream should treat as already used for this context."""
    excluded: set[int] = set()
    for path in paths:
        if path is None or not Path(path).exists():
            continue
        entries = read_page_id_entries(Path(path))
        if answer_types is None and table_types is None:
            excluded.update(entry.page_id for entry in entries)
        else:
            excluded.update(
                page_ids_excluded_for_context(
                    entries,
                    answer_types=answer_types or (),
                    table_types=table_types or (),
                )
            )
    return {page_id for page_id in excluded if page_id > 0}


def _stream_cached_page_reuse_disabled_summary(args: argparse.Namespace) -> dict[str, object]:
    """Return the summary payload used when cached page reuse is disabled."""
    return {
        "enabled": False,
        "requested_count": max(0, int(getattr(args, "stream_reuse_cached_page_count", 0) or 0)),
        "archive_dir": str(getattr(args, "route3_page_archive_dir", "") or ""),
        "used_id_files": [str(path) for path in getattr(args, "stream_reuse_cached_page_used_id_file", [])],
        "strict_numeric_page_id_matching": True,
        "selected_count": 0,
        "selected_page_ids": [],
    }


def _reserve_stream_cached_page_archives(
    *,
    state: PageIdStreamState,
    args: argparse.Namespace,
) -> tuple[list[CachedPageArchiveEntry], dict[str, object]]:
    """Reserve reusable cached parsed pages by strict numeric page ID."""
    requested_count = max(0, int(getattr(args, "stream_reuse_cached_page_count", 0) or 0))
    archive_dir = Path(getattr(args, "route3_page_archive_dir", ROOT / DEFAULT_ROUTE3_PAGE_ARCHIVE_DIR))
    used_id_files = list(getattr(args, "stream_reuse_cached_page_used_id_file", []) or [])
    used_ids = _load_stream_reuse_cached_page_used_ids(used_id_files)
    cached_entries, scan_summary = _scan_route3_cached_page_archives(archive_dir)
    available_entries = [entry for entry in cached_entries if entry.page_id not in used_ids]
    state_used_ids = set(state.used_ids)
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
        "used_id_files": [str(path) for path in used_id_files],
        "strict_numeric_page_id_matching": True,
        **scan_summary,
        "used_id_excluded_page_count": len({entry.page_id for entry in cached_entries if entry.page_id in used_ids}),
        "state_already_used_page_count": len(
            {entry.page_id for entry in available_entries if entry.page_id in state_used_ids}
        ),
        "reusable_cached_page_count": len(available_entries),
        "selected_count": len(selected),
        "selected_page_ids": [entry.page_id for entry in selected],
        "selected_archive_paths": [str(entry.archive_path) for entry in selected],
    }
    return selected, summary


def _load_stream_reuse_cached_page_used_ids(paths: list[Path]) -> set[int]:
    """Load page-level cache-reuse exclusions from helper-generated ID files."""
    used_ids: set[int] = set()
    for path in paths:
        if path is None or not Path(path).exists():
            continue
        entries = read_page_id_entries(Path(path), include_used_ids=True)
        used_ids.update(entry.page_id for entry in entries if entry.page_id > 0)
    return used_ids


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
    page_id = _positive_record_page_id(payload.get("page_id"))
    if page_id is not None:
        return page_id
    parse_payload = payload.get("parse_payload")
    parse_body = parse_payload.get("parse", {}) if isinstance(parse_payload, dict) else {}
    if isinstance(parse_body, dict):
        return _positive_record_page_id(parse_body.get("pageid"))
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
    page_only_ids = {
        page_id
        for record in all_decision_records
        if _all5_page_level_prerewrite_rejected(record)
        for page_id in [_positive_record_page_id(_record_page_id(record))]
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
        page_id = _positive_record_page_id(_record_page_id(record))
        if page_id is None:
            continue
        table_type = _record_table_type(record)
        if table_type:
            table_types_by_page[page_id].add(table_type)
    return table_types_by_page


def _all5_page_level_prerewrite_rejected(record: dict) -> bool:
    """Return whether one all5 rejected record invalidates the whole page before rewrite."""
    metadata = record.get("source_metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
    if str(metadata.get("answer_type_mode") or "").strip() != "all5":
        return False
    if str(metadata.get("route3_slot_id") or "").strip():
        return False
    if _record_answer_type(record) != "unknown":
        return False
    return bool(_source_stage_rejection_reason(record))


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


def _build_streaming_second_stage_model_panel(
    settings: Settings,
    concurrency: StreamingConcurrencyContext,
):
    """Construct shared second-stage clients wrapped by the second-stage semaphore."""
    if not settings.second_stage_grading_enabled:
        return None
    members = build_second_stage_model_panel(settings)
    for member in members:
        member.client = SemaphoreWrappedClient(
            member.client,
            concurrency.second_stage_semaphore,
            {"complete_text"},
        )
    return members


def _build_streaming_second_stage_grader_client(
    settings: Settings,
    concurrency: StreamingConcurrencyContext,
):
    """Construct a shared second-stage grader client wrapped by the second-stage semaphore."""
    if not settings.second_stage_grading_enabled:
        return None
    client = build_second_stage_grader_client(settings)
    if client is None:
        return None
    return SemaphoreWrappedClient(client, concurrency.second_stage_semaphore, {"complete_text"})


def _process_one_stream_page_id(
    page_id: int,
    *,
    args: argparse.Namespace,
    settings: Settings,
    state: PageIdStreamState,
    wikipedia_client: WikipediaClient,
    search_client: DuckDuckGoSearchClient,
    llm_client,
    rewrite_client,
    concurrency: StreamingConcurrencyContext,
    second_stage_model_clients,
    grading_grader_client,
    source_url: str | None = None,
    stream_page_source: str | None = None,
    cached_archive_path: Path | None = None,
) -> dict:
    """Run one page ID through generation and shared processing."""
    url = source_url or build_pageid_url(page_id)
    page_source = stream_page_source or args.stream_page_source
    try:
        generator = WikipediaInfoboxTableGenerator(
            urls=[url],
            wikipedia_client=wikipedia_client,
            llm_client=llm_client,
            record_limit=1,
            url_domains={},
            search_query_count=args.generated_search_query_count,
            enable_rest_summary_fallback=args.enable_rest_summary_fallback,
            min_table_score=args.min_table_score,
            allowed_reasoning_types=tuple(args.route3_reasoning_type),
            allowed_answer_types=tuple(args.route3_answer_type),
            extra_prompts=tuple(args.route3_extra_prompt),
            table_filter_modes=tuple(args.route3_table_filter_mode),
            table_source_types=tuple(args.route3_table_source_type),
            prose_leakage_scoring_enabled=args.route3_prose_leakage_scoring,
            llm_choose_table=args.route3_llm_choose_table,
            answer_type_mode=args.route3_answer_type_mode,
            page_archive_dir=args.route3_page_archive_dir,
            pageview_prefilter_enabled=args.route3_pageview_prefilter,
            pageview_window_months=args.route3_pageview_window_months,
            max_monthly_average_pageviews=args.route3_max_monthly_average_pageviews,
            max_underfilled_monthly_pageviews=args.route3_max_underfilled_monthly_pageviews,
            pageview_unavailable_policy=args.route3_pageview_unavailable_policy,
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
            with concurrency.commit_lock:
                state.mark_rerun(page_id, reason="no_generated_candidate")
            return {
                "status": "rerun",
                "page_id": page_id,
                "url": url,
                "reason": "no_generated_candidate",
            }
        for candidate in generated_candidates:
            _attach_stream_metadata(
                candidate,
                page_id=page_id,
                url=url,
                args=args,
                page_source=page_source,
                cached_archive_path=cached_archive_path,
            )
        result = process_generated_candidates(
            generated_candidates,
            settings=settings,
            search_client=search_client,
            rewrite_client=rewrite_client,
            second_stage_model_clients=second_stage_model_clients,
            grading_grader_client=grading_grader_client,
        )
        if result.accepted:
            with concurrency.commit_lock:
                accepted_index_offset = _jsonl_record_count(args.output)
                for index, record in enumerate(result.accepted, start=accepted_index_offset + 1):
                    _attach_stream_record_metadata(
                        record,
                        page_id=page_id,
                        url=url,
                        args=args,
                        page_source=page_source,
                        cached_archive_path=cached_archive_path,
                    )
                    _ensure_page_id_list_entry_metadata(record)
                    record["id"] = _wikipedia_stream_record_id(record, index, run_date=settings.run_date)
                for record in result.rejected:
                    _attach_stream_record_metadata(
                        record,
                        page_id=page_id,
                        url=url,
                        args=args,
                        page_source=page_source,
                        cached_archive_path=cached_archive_path,
                    )
                append_jsonl(args.output, _accepted_output_records(result.accepted, args))
                if result.rejected:
                    append_jsonl(args.rejected_output, _rejected_output_records(result.rejected, args))
                state.mark_accepted(page_id)
            return {
                "status": "accepted",
                "page_id": page_id,
                "url": url,
                "accepted_records": result.accepted,
                "rejected_records": result.rejected,
            }
        if result.rejected:
            for record in result.rejected:
                _attach_stream_record_metadata(
                    record,
                    page_id=page_id,
                    url=url,
                    args=args,
                    page_source=page_source,
                    cached_archive_path=cached_archive_path,
                )
            reason = _exact_failure_reason(result.rejected[0])
            if _should_rerun_stream_rejection(result.rejected[0]):
                error_details = _rerun_error_details_from_record(result.rejected[0])
                with concurrency.commit_lock:
                    state.mark_rerun(page_id, reason=reason, **error_details)
                return {
                    "status": "rerun",
                    "page_id": page_id,
                    "url": url,
                    "accepted_records": [],
                    "rejected_records": [],
                    "reason": reason,
                    **error_details,
                }
            with concurrency.commit_lock:
                append_jsonl(args.rejected_output, _rejected_output_records(result.rejected, args))
                state.mark_rejected(page_id, reason=reason)
            return {
                "status": "rejected",
                "page_id": page_id,
                "url": url,
                "accepted_records": [],
                "rejected_records": result.rejected,
                "reason": reason,
            }
        with concurrency.commit_lock:
            state.mark_rerun(page_id, reason="pipeline_no_accept_or_reject")
        return {
            "status": "rerun",
            "page_id": page_id,
            "url": url,
            "reason": "pipeline_no_accept_or_reject",
        }
    except Exception as exc:  # noqa: BLE001
        error_type = type(exc).__name__
        error_message = str(exc)
        reason = f"pipeline_exception:{error_type}"
        with concurrency.commit_lock:
            state.mark_rerun(
                page_id,
                reason=reason,
                error_type=error_type,
                error_message=error_message,
            )
        return {
            "status": "rerun",
            "page_id": page_id,
            "url": url,
            "reason": reason,
            "error_type": error_type,
            "error_message": error_message,
        }


def _should_rerun_stream_rejection(record: dict) -> bool:
    """Return whether a rejected stream record represents a transient retryable failure."""
    reason = str(record.get("rejection_reason", "")).strip()
    if reason in {"search_longtail_verifier_error", "second_stage_grading_error", "wikipedia_pageview_prefilter_unavailable"}:
        return True
    if not reason.startswith("wikipedia_infobox_generation_error:"):
        return False
    metadata = record.get("source_metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
    error_text = " ".join(
        str(value)
        for value in (
            reason,
            metadata.get("error_message", ""),
            ";".join(str(note) for note in record.get("notes", [])),
        )
        if value
    )
    retryable_markers = (
        "URLError",
        "SSL:",
        "UNEXPECTED_EOF_WHILE_READING",
        "RemoteDisconnected",
        "TimeoutError",
        "timed out",
        "ConnectionResetError",
        "Temporary failure",
        "HTTP Error 429",
        "Too Many Requests",
    )
    return any(marker in error_text for marker in retryable_markers)


def _reserve_stream_page_ids(
    *,
    state: PageIdStreamState,
    args: argparse.Namespace,
    wikipedia_client: WikipediaClient,
    rng: random.Random,
    count: int,
    rerun_pool_only: bool = False,
    prefer_rerun_pool: bool = False,
) -> list[int]:
    """Reserve page IDs from the configured streaming discovery source."""
    if rerun_pool_only:
        return state.reserve_candidate_ids(
            [],
            count=count,
            source="rerun_pool_only",
            prefer_rerun_pool=True,
        )
    if args.stream_page_source == "random-page-id":
        return state.reserve_ids(
            count=count,
            lower_bound=args.stream_page_id_min,
            upper_bound=args.stream_page_id_max,
            rng=rng,
            prefer_rerun_pool=prefer_rerun_pool,
        )

    selected = state.reserve_candidate_ids(
        [],
        count=count,
        source="rerun_pool",
        prefer_rerun_pool=prefer_rerun_pool,
    )
    if len(selected) >= count:
        return selected

    queries = _stream_search_queries(args)
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
            candidate_ids = [hit.page_id for hit in hits]
            reserved = state.reserve_candidate_ids(
                candidate_ids,
                count=count - len(selected),
                source=f"table_search:{query}:offset={offset}",
                prefer_rerun_pool=False,
            )
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


def _stream_search_queries(args: argparse.Namespace) -> list[str]:
    """Return table-search queries for streaming discovery."""
    queries = [query.strip() for query in args.stream_search_query if query.strip()]
    if not queries:
        queries = list(DEFAULT_TABLE_SEARCH_QUERIES)
    if args.enable_broad_table_search and BROAD_TABLE_SEARCH_QUERY not in queries:
        queries.append(BROAD_TABLE_SEARCH_QUERY)
    return queries


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
        "page_id_min": args.stream_page_id_min,
        "page_id_max": args.stream_page_id_max,
        "random_seed": args.stream_random_seed,
        "domain_policy": "domain_and_subdomain_optional",
    }
    if cached_archive_path is not None:
        metadata["cached_archive_reuse"] = True
        metadata["cached_archive_path"] = str(cached_archive_path)
    return metadata


def _attach_run_artifact_metadata(metadata: dict, *, args: argparse.Namespace) -> None:
    """Attach run-group artifact IDs when artifact indexing is enabled."""
    run_group_id = _run_group_id(args)
    if not run_group_id:
        return
    metadata["run_group_id"] = run_group_id
    metadata["run_segment_id"] = _run_segment_id(args)
    manifest_path = _run_artifact_manifest_path(args, run_group_id)
    if manifest_path is not None:
        metadata["run_artifact_manifest"] = str(manifest_path)


def _ensure_small_model_response_metadata(metadata: dict) -> None:
    """Keep explicit small-model response keys alongside legacy metadata names."""
    llm_response = metadata.get("llm_response")
    if isinstance(llm_response, dict) and "small_model_qa_response" not in metadata:
        metadata["small_model_qa_response"] = llm_response


def _survival_by_layer(
    *,
    attempted_count: int,
    rejected_records: list[dict],
    rerun_records: list[dict],
) -> list[dict[str, object]]:
    """Return layer-by-layer survival stats for a streaming run."""
    stage_failures = Counter(_rejection_stage(record) for record in rejected_records)
    for record in rerun_records:
        stage_failures[_rerun_stage(record)] += 1
    layers = [
        ("page_id_reservation", "Page-id reservation"),
        ("unresolved_rerun", "Unresolved or returned to rerun pool"),
        ("route_generation", "Page extraction, table grading, and QA generation"),
        ("rewrite_surface", "Rewrite and surface validation"),
        ("search_longtail", "DuckDuckGo long-tail filtering"),
        ("second_stage_grading", "Second-stage model grading"),
        ("shared_validation", "Shared route-aware validation"),
        ("deduplication", "Deduplication"),
        ("other", "Other rejection"),
    ]
    rows: list[dict[str, object]] = []
    entered = attempted_count
    for stage, label in layers:
        failed = 0 if stage == "page_id_reservation" else int(stage_failures.get(stage, 0))
        survived = max(0, entered - failed)
        rows.append(
            {
                "stage": stage,
                "layer": label,
                "entered": entered,
                "failed": failed,
                "survived": survived,
                "survival_rate_from_layer_input": _rate(survived, entered),
                "cumulative_survival_rate": _rate(survived, attempted_count),
            }
        )
        entered = survived
    return rows


def _failure_reason_counts(rejected_records: list[dict], rerun_records: list[dict]) -> list[dict[str, object]]:
    """Return reviewer-facing failure reasons grouped by stage."""
    counts: Counter[tuple[str, str]] = Counter()
    for record in rejected_records:
        counts[(_rejection_stage(record), _summary_failure_reason(record))] += 1
    for record in rerun_records:
        counts[(_rerun_stage(record), str(record.get("reason", "unresolved")))] += 1
    return [
        {"stage": stage, "reason": reason, "count": count}
        for (stage, reason), count in sorted(counts.items(), key=lambda item: (-item[1], item[0][0], item[0][1]))
    ]


def _rerun_stage(record: dict) -> str:
    """Return the pipeline stage where a retryable stream failure occurred."""
    reason = str(record.get("reason", "")).strip()
    if reason.startswith("search_longtail_verifier_error"):
        return "search_longtail"
    if reason.startswith("second_stage_grading_error"):
        return "second_stage_grading"
    if reason.startswith("wikipedia_infobox_") or reason.startswith("wikipedia_pageview_") or reason.startswith("pipeline_exception"):
        return "route_generation"
    return "unresolved_rerun"


def _phase_timing_explanation_rows() -> list[dict[str, str]]:
    """Return the ordered timing glossary used by walkthroughs."""
    return [
        {
            "order": "0",
            "phase": "wall_clock_seconds",
            "kind": "run total",
            "additive": "No",
            "meaning": "Elapsed time for the whole streaming command.",
        },
        {
            "order": "1",
            "phase": "page_fetch_seconds",
            "kind": "child of total_generation_seconds",
            "additive": "Yes, within generation only",
            "meaning": "MediaWiki action=parse fetch for one page.",
        },
        {
            "order": "2",
            "phase": "first_paragraph_extract_seconds",
            "kind": "child of total_generation_seconds",
            "additive": "Yes, within generation only",
            "meaning": "Local extraction of first paragraph from parse HTML.",
        },
        {
            "order": "3",
            "phase": "first_paragraph_fetch_seconds",
            "kind": "optional child of total_generation_seconds",
            "additive": "Yes, within generation only",
            "meaning": "REST summary fallback when explicitly enabled and parse HTML lacks a paragraph.",
        },
        {
            "order": "4",
            "phase": "table_parse_seconds",
            "kind": "child of total_generation_seconds",
            "additive": "Yes, within generation only",
            "meaning": "Local table/prose parsing and table ranking inputs.",
        },
        {
            "order": "5",
            "phase": "llm_question_generation_seconds",
            "kind": "child of total_generation_seconds",
            "additive": "Yes, within generation only",
            "meaning": "Small-model Route 3 QA generation call.",
        },
        {
            "order": "6",
            "phase": "total_generation_seconds",
            "kind": "parent",
            "additive": "No",
            "meaning": "Overall Route 3 generation time for one page.",
        },
        {
            "order": "7",
            "phase": "rewrite_seconds",
            "kind": "child of total_processing_seconds",
            "additive": "Yes, within processing only",
            "meaning": "Shared rewrite call when enabled.",
        },
        {
            "order": "8",
            "phase": "number_reference_margin_seconds",
            "kind": "child of total_processing_seconds",
            "additive": "Yes, within processing only",
            "meaning": "Numeric reference margin setup for Number answers.",
        },
        {
            "order": "9",
            "phase": "duckduckgo_search_seconds",
            "kind": "child of total_processing_seconds",
            "additive": "Yes, within processing only",
            "meaning": "DuckDuckGo long-tail queries and leakage scoring.",
        },
        {
            "order": "10",
            "phase": "second_stage_grading_seconds",
            "kind": "optional child of total_processing_seconds",
            "additive": "Yes, within processing only",
            "meaning": "Model-panel answerability grading when enabled.",
        },
        {
            "order": "11",
            "phase": "total_processing_seconds",
            "kind": "parent",
            "additive": "No",
            "meaning": "Shared rewrite, filtering, grading, validation, and dedup processing for one candidate.",
        },
        {
            "order": "12",
            "phase": "candidate_processing_seconds",
            "kind": "alias",
            "additive": "No",
            "meaning": "Alias of total_processing_seconds for compatibility.",
        },
    ]


def _phase_timing_stats(records: list[dict]) -> dict[str, dict[str, float | int]]:
    """Return total, average, and max timings by phase."""
    values_by_phase: dict[str, list[float]] = defaultdict(list)
    for record in records:
        timings = record.get("source_metadata", {}).get("phase_timings_seconds", {})
        if not isinstance(timings, dict):
            continue
        for phase, seconds in timings.items():
            try:
                values_by_phase[str(phase)].append(float(seconds))
            except (TypeError, ValueError):
                continue
    return {
        phase: {
            "count": len(values),
            "total": round(sum(values), 4),
            "average": round(sum(values) / len(values), 4),
            "max": round(max(values), 4),
        }
        for phase, values in sorted(values_by_phase.items())
        if values
    }


def _rejection_stage(record: dict) -> str:
    """Map one rejected output record to the pipeline stage that rejected it."""
    reason = str(record.get("rejection_reason", "")).strip()
    source_failure = _source_stage_failure(record)
    if source_failure is not None:
        return source_failure[0]
    if reason.startswith("wikipedia_infobox_") or reason.startswith("wikipedia_pageview_"):
        return "route_generation"
    if reason in {"llm_rewrite_discarded", "rewrite_guard_rejected", "rule_based_answer_type_gate_rejected"}:
        return "rewrite_surface"
    if reason.startswith("search_longtail_"):
        return "search_longtail"
    if reason.startswith("second_stage_grading"):
        return "second_stage_grading"
    if reason == "shared_validation_failed":
        return "shared_validation"
    if reason.startswith("duplicate_"):
        return "deduplication"
    return "other"


def _exact_failure_reason(record: dict) -> str:
    """Return a precise, reviewer-facing failure reason for one rejected record."""
    reason = str(record.get("rejection_reason", "")).strip() or "unknown_rejection"
    source_failure = _source_stage_failure(record)
    if source_failure is not None:
        _, source_reason, detail = source_failure
        return f"{source_reason}:{detail}" if detail else source_reason
    compact_reason = str(record.get("failing_reason", "")).strip()
    if compact_reason:
        return compact_reason
    notes = record.get("rejection_notes", {})
    if not isinstance(notes, dict):
        return reason
    if reason == "rewrite_guard_rejected":
        rule = record.get("rejection_rule") or notes.get("failure_reason") or notes.get("surface_validation_failure_reason")
        return f"{reason}:{rule}" if rule else reason
    if reason == "rule_based_answer_type_gate_rejected":
        gate = notes.get("rule_based_qa_gate", {})
        if isinstance(gate, dict):
            details = gate.get("details", {})
            if isinstance(details, dict) and details.get("rule"):
                return f"{reason}:{details['rule']}"
        rule = record.get("rejection_rule") or notes.get("failure_reason")
        return f"{reason}:{rule}" if rule else reason
    if reason == "search_longtail_verifier_rejected":
        features = notes.get("search_verification_features", {})
        if isinstance(features, dict) and features.get("triggered_rule"):
            return f"{reason}:{features['triggered_rule']}"
    if reason.startswith("second_stage_grading"):
        features = notes.get("panel_grading_features", {})
        if isinstance(features, dict):
            accuracy = features.get("accuracy")
            threshold = features.get("accuracy_threshold")
            if accuracy is not None and threshold is not None:
                return f"{reason}:accuracy={accuracy};threshold={threshold}"
    if reason == "shared_validation_failed":
        validation = notes.get("validation", {})
        if isinstance(validation, dict):
            failed_keys = [key for key, value in validation.items() if value is False]
            if failed_keys:
                return f"{reason}:{','.join(failed_keys)}"
    metadata = record.get("source_metadata", {})
    if isinstance(metadata, dict):
        discard_reason = str(metadata.get("discard_reason") or "").strip()
        error_message = str(metadata.get("error_message") or "").strip()
        if discard_reason:
            return f"{reason}:{discard_reason}"
        if error_message:
            return f"{reason}:{error_message[:160]}"
    return reason


def _source_stage_failure(record: dict) -> tuple[str, str, str] | None:
    """Return a source-stage failure that should take precedence over placeholder QA validation."""
    source_reason = _source_stage_rejection_reason(record)
    if not source_reason:
        return None
    detail = _source_metadata_failure_detail(record)
    return "route_generation", source_reason, detail


def _source_stage_rejection_reason(record: dict) -> str:
    """Return the source-stage rejection reason represented by one record, if any."""
    reason = str(record.get("rejection_reason", "")).strip()
    if _is_source_stage_rejection_reason(reason):
        return reason
    notes = record.get("notes", [])
    if isinstance(notes, list):
        for note in notes:
            note_text = str(note or "").strip()
            if _is_source_stage_rejection_reason(note_text):
                return note_text
    return ""


def _is_source_stage_rejection_reason(reason: str) -> bool:
    """Return whether one reason represents a blocking Route 3 source-stage rejection."""
    if not reason or reason == "wikipedia_infobox_incomplete_tie_answer":
        return False
    return reason.startswith("wikipedia_infobox_") or reason.startswith("wikipedia_pageview_")


def _source_metadata_failure_detail(record: dict) -> str:
    """Return the source metadata detail for a rejected record, if present."""
    metadata = record.get("source_metadata", {})
    if not isinstance(metadata, dict):
        return ""
    return str(metadata.get("discard_reason") or metadata.get("error_message") or "").strip()


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


def _summary_failure_reason(record: dict) -> str:
    """Return the coarser failure reason used in aggregate stats tables."""
    exact_reason = _exact_failure_reason(record)
    reason = str(record.get("rejection_reason", "")).strip() or "unknown_rejection"
    if reason == "search_longtail_verifier_rejected":
        return reason
    if reason == "second_stage_grading_accuracy_threshold_exceeded":
        return reason
    if reason == "wikipedia_infobox_table_filter_rejected":
        table_filter_reason = exact_reason.partition(":")[2]
        if "no_picture_heavy_tables" in table_filter_reason:
            return f"{reason}:no_picture_heavy_tables"
        if "no_incomplete_tables" in table_filter_reason:
            return f"{reason}:no_incomplete_tables"
        if "no_social_science_research" in table_filter_reason:
            return f"{reason}:no_social_science_research"
        if "not_number_dominant" in table_filter_reason or "no_big_numbers" in table_filter_reason:
            return f"{reason}:not_number_dominant"
    return exact_reason


def _rate(numerator: int, denominator: int) -> float:
    """Return a rounded rate, guarding against division by zero."""
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 4)


def _write_stream_walkthrough(
    *,
    path: Path,
    summary: dict,
    accepted_records: list[dict],
    rejected_records: list[dict],
    rerun_records: list[dict],
    existing_accepted_records: list[dict] | None = None,
    existing_rejected_records: list[dict] | None = None,
) -> None:
    """Write a markdown walkthrough for a streaming Route 3 run."""
    existing_accepted_records = existing_accepted_records or []
    existing_rejected_records = existing_rejected_records or []
    record_groups = _walkthrough_record_groups(
        existing_accepted_records=existing_accepted_records,
        existing_rejected_records=existing_rejected_records,
        accepted_records=accepted_records,
        rejected_records=rejected_records,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append(f"# Route 3 Streaming Wikipedia Page-ID Walkthrough - {summary.get('run_date', '2026-05-19')}")
    lines.append("")
    lines.append("## Stats")
    lines.append("")
    if summary.get("run_group_id"):
        lines.append(f"- Run group ID: `{summary.get('run_group_id', '')}`")
        lines.append(f"- Run segment ID: `{summary.get('run_segment_id', '')}`")
        lines.append(f"- Artifact manifest: `{summary.get('run_artifact_manifest', '')}`")
    lines.append(f"- Mode: `{summary.get('streaming_mode', '')}`")
    lines.append(f"- Page source: `{summary.get('stream_page_source', '')}`")
    search_queries = summary.get("stream_search_queries", [])
    if search_queries:
        lines.append(f"- Table-search queries: `{'; '.join(str(query) for query in search_queries)}`")
    endpoint_resume = summary.get("endpoint_resume", {})
    if isinstance(endpoint_resume, dict) and endpoint_resume.get("enabled"):
        lines.append(
            "- Endpoint resume: "
            f"{endpoint_resume.get('accepted_records_loaded', 0)} accepted and "
            f"{endpoint_resume.get('rejected_records_loaded', 0)} rejected records loaded"
        )
        lines.append(f"- Existing accepted QAs before run: {len(existing_accepted_records)}")
        lines.append(f"- Existing rejected QAs/pages before run: {len(existing_rejected_records)}")
    lines.append(f"- Attempted page IDs: {summary.get('attempted_page_ids', 0)}")
    if summary.get("attempted_page_ids_unique") is not None:
        lines.append(f"- Unique attempted page IDs: {summary.get('attempted_page_ids_unique', 0)}")
    if summary.get("stream_state_reset"):
        lines.append("- Stream state reset at run start: yes")
    if summary.get("stream_rerun_pool_only"):
        lines.append("- Rerun-pool-only mode: yes")
        lines.append(f"- Rerun-pool processing limit: {summary.get('stream_rerun_pool_limit', 0) or 'all'}")
    if summary.get("stream_auto_rerun_once"):
        lines.append("- Auto rerun pool once: yes")
        lines.append(f"- Auto-rerun attempted page IDs: {summary.get('auto_rerun_attempted_page_ids', 0)}")
    lines.append(f"- Accepted QAs: {summary.get('accepted', 0)}")
    if isinstance(endpoint_resume, dict) and endpoint_resume.get("enabled"):
        lines.append(f"- Accepted QAs after resume: {summary.get('accepted_total', 0)}")
    lines.append(f"- Rejected QAs/pages: {summary.get('rejected', 0)}")
    if isinstance(endpoint_resume, dict) and endpoint_resume.get("enabled"):
        lines.append(f"- Rejected QAs/pages after resume: {summary.get('rejected_total', 0)}")
    lines.append(f"- Transient rerun attempts during run: {summary.get('rerun', 0)}")
    if summary.get("wall_clock_seconds") is not None:
        lines.append(f"- Wall-clock runtime: {float(summary.get('wall_clock_seconds', 0.0)):.4f}s")
    lines.append(f"- DuckDuckGo top K: {summary.get('duckduckgo_top_k', '')}")
    lines.append(f"- Generated search queries per QA: {summary.get('generated_search_query_count', '')}")
    lines.append(f"- DuckDuckGo parallel queries: {summary.get('duckduckgo_parallel_queries', '')}")
    if "duckduckgo_prefer_ddgs" in summary:
        lines.append(
            "- DuckDuckGo ddgs primary path: "
            f"`{'enabled' if summary.get('duckduckgo_prefer_ddgs') else 'disabled'}`, "
            f"backend `{summary.get('duckduckgo_ddgs_backend', '')}`, "
            f"attempts {summary.get('duckduckgo_ddgs_max_attempts', '')}"
        )
    if summary.get("duckduckgo_disabled_fallbacks"):
        lines.append(
            "- DuckDuckGo disabled fallbacks: "
            f"`{', '.join(str(item) for item in summary.get('duckduckgo_disabled_fallbacks', []))}`"
        )
    if "duckduckgo_cooldown_enabled" in summary:
        lines.append(
            "- DuckDuckGo global cooldown: "
            f"`{'enabled' if summary.get('duckduckgo_cooldown_enabled') else 'disabled'}`, "
            f"threshold {summary.get('duckduckgo_cooldown_failure_threshold', '')}, "
            f"{summary.get('duckduckgo_cooldown_initial_seconds', '')}s to "
            f"{summary.get('duckduckgo_cooldown_max_seconds', '')}s"
        )
    if summary.get("min_table_score") is not None:
        lines.append(f"- Minimum Route 3 table score: {summary.get('min_table_score', '')}")
    if summary.get("route3_reasoning_types"):
        lines.append(f"- Route 3 reasoning_type constraint: `{', '.join(summary.get('route3_reasoning_types', []))}`")
    if summary.get("route3_answer_types"):
        lines.append(f"- Route 3 answer_type constraint: `{', '.join(summary.get('route3_answer_types', []))}`")
    if summary.get("route3_extra_prompts"):
        lines.append(f"- Route 3 extra prompt rules: `{'; '.join(summary.get('route3_extra_prompts', []))}`")
    if summary.get("route3_table_filter_modes"):
        lines.append(f"- Route 3 table filter modes: `{', '.join(summary.get('route3_table_filter_modes', []))}`")
    if summary.get("route3_table_source_types"):
        lines.append(f"- Route 3 table source types: `{', '.join(summary.get('route3_table_source_types', []))}`")
    if "route3_prose_leakage_scoring_enabled" in summary:
        state = "enabled" if summary.get("route3_prose_leakage_scoring_enabled") else "disabled"
        lines.append(f"- Route 3 prose-leakage scoring: `{state}`")
    if "route3_llm_choose_table" in summary:
        lines.append(
            "- Route 3 LLM table choice: "
            f"`{'enabled' if summary.get('route3_llm_choose_table') else 'disabled'}`"
        )
    if summary.get("stream_page_workers") is not None:
        lines.append(f"- Stream page workers: {summary.get('stream_page_workers', '')}")
        lines.append(f"- Wikipedia concurrency limit: {summary.get('wikipedia_concurrency_limit', '')}")
        if "wikipedia_429_backoff_seconds" in summary:
            lines.append(
                "- Wikipedia 429 backoff: "
                f"{summary.get('wikipedia_429_backoff_seconds', '')}s base, "
                f"{summary.get('wikipedia_429_max_backoff_seconds', '')}s max, "
                f"{summary.get('wikipedia_429_recovery_seconds', '')}s recovery"
            )
        lines.append(f"- DuckDuckGo service concurrency limit: {summary.get('duckduckgo_concurrency_limit', '')}")
        lines.append(
            "- OpenRouter generation/rewrite concurrency limit: "
            f"{summary.get('openrouter_generation_rewrite_concurrency_limit', '')}"
        )
        lines.append(f"- Second-stage concurrency limit: {summary.get('second_stage_concurrency_limit', '')}")
    bounds = summary.get("page_id_bounds", {})
    if isinstance(bounds, dict):
        lines.append(f"- Page-id bounds: {bounds.get('min')} to {bounds.get('max')}")
    lines.append(f"- Stream state: `{summary.get('stream_state', '')}`")
    lines.append(f"- Accepted output: `{summary.get('output_path', '')}`")
    lines.append(f"- Rejected output: `{summary.get('rejected_output_path', '')}`")
    lines.append(f"- Domain policy: `{summary.get('domain_policy', '')}`")
    rerun_pool_ids = summary.get("rerun_pool_ids_after_run", [])
    if isinstance(rerun_pool_ids, list):
        lines.append(f"- Rerun pool after run: `{', '.join(str(page_id) for page_id in rerun_pool_ids) or 'empty'}`")
    lines.append("")
    recipe_segments = summary.get("recipe_segments", [])
    if isinstance(recipe_segments, list) and recipe_segments:
        lines.append("### Recipe Segments")
        lines.append("")
        lines.append("| Configured answer_type | Record limit | Attempted page IDs | Accepted | Rejected | Rerun |")
        lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
        for segment in recipe_segments:
            if not isinstance(segment, dict):
                continue
            lines.append(
                "| {answer_type} | {record_limit} | {attempted} | {accepted} | {rejected} | {rerun} |".format(
                    answer_type=_escape_table_text(str(segment.get("answer_type", ""))),
                    record_limit=int(segment.get("record_limit", 0) or 0),
                    attempted=int(segment.get("attempted_page_ids", 0) or 0),
                    accepted=int(segment.get("accepted", 0) or 0),
                    rejected=int(segment.get("rejected", 0) or 0),
                    rerun=int(segment.get("rerun", 0) or 0),
                )
            )
        lines.append("")
    if existing_accepted_records or existing_rejected_records:
        _append_overall_resume_stats(
            lines,
            summary=summary,
            existing_accepted_records=existing_accepted_records,
            existing_rejected_records=existing_rejected_records,
            accepted_records=accepted_records,
            rejected_records=rejected_records,
            rerun_records=rerun_records,
        )
        lines.append("")
    lines.append("### Survival By Layer")
    lines.append("")
    lines.append("| Layer | Entered | Failed | Survived | Layer survival | Cumulative survival |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
    for row in summary.get("survival_by_layer", []):
        lines.append(
            "| {layer} | {entered} | {failed} | {survived} | {layer_rate:.1%} | {cumulative_rate:.1%} |".format(
                layer=row.get("layer", ""),
                entered=int(row.get("entered", 0)),
                failed=int(row.get("failed", 0)),
                survived=int(row.get("survived", 0)),
                layer_rate=float(row.get("survival_rate_from_layer_input", 0.0)),
                cumulative_rate=float(row.get("cumulative_survival_rate", 0.0)),
            )
        )
    lines.append("")
    lines.append("### Failure Reasons")
    lines.append("")
    lines.append("| Stage | Reason | Count |")
    lines.append("| --- | --- | ---: |")
    for row in summary.get("failure_reason_counts", []):
        lines.append(f"| `{row.get('stage', '')}` | `{_escape_table_text(str(row.get('reason', '')))}` | {row.get('count', 0)} |")
    if not summary.get("failure_reason_counts"):
        lines.append("| n/a | n/a | 0 |")
    lines.append("")
    _append_record_attribute_stats_section(
        lines,
        title="Answer Type Stats",
        attribute_label="Answer type",
        extractor=_record_answer_type,
        record_groups=record_groups,
    )
    lines.append("")
    _append_record_attribute_stats_section(
        lines,
        title="Reasoning Type Stats",
        attribute_label="Reasoning type",
        extractor=_record_reasoning_type,
        record_groups=record_groups,
    )
    lines.append("")
    lines.append("### Rerun Pool After Run")
    lines.append("")
    rerun_reasons = summary.get("rerun_pool_failure_reasons_after_run", {})
    if isinstance(rerun_pool_ids, list) and rerun_pool_ids:
        lines.append("| Page ID | Exact reason |")
        lines.append("| ---: | --- |")
        for page_id in rerun_pool_ids:
            reason = ""
            if isinstance(rerun_reasons, dict):
                reason = str(rerun_reasons.get(str(page_id), ""))
            lines.append(f"| {page_id} | `{_escape_table_text(reason)}` |")
    else:
        lines.append("Rerun pool is empty.")
    lines.append("")
    _append_in_run_rerun_outcomes_section(
        lines,
        summary=summary,
        accepted_records=accepted_records,
        rejected_records=rejected_records,
        rerun_records=rerun_records,
    )
    lines.append("")
    _append_phase_timings_section(
        lines,
        summary=summary,
        existing_accepted_records=existing_accepted_records,
        existing_rejected_records=existing_rejected_records,
        accepted_records=accepted_records,
        rejected_records=rejected_records,
    )
    lines.append("")
    lines.append("## Accepted Candidates")
    lines.append("")
    if existing_accepted_records or existing_rejected_records:
        lines.append("Existing endpoint records are shown first; incremental records are the records appended by this run.")
        lines.append("")
    if any(group_accepted for _, group_accepted, _ in record_groups):
        for group_label, group_accepted, _ in record_groups:
            if len(record_groups) > 1:
                lines.append(f"### {group_label}")
                lines.append("")
            if group_accepted:
                lines.append("| Page ID | Answer type | Question | Answer | Source |")
                lines.append("| ---: | --- | --- | --- | --- |")
                for record in group_accepted:
                    lines.append(
                        "| {page_id} | `{answer_type}` | {question} | {answer} | {url} |".format(
                            page_id=_record_page_id(record),
                            answer_type=_escape_table_text(_record_answer_type(record)),
                            question=_escape_table_text(str(record.get("question", ""))),
                            answer=_escape_table_text(str(record.get("answer", ""))),
                            url=_escape_table_text(str(record.get("source_metadata", {}).get("canonical_url") or record.get("source_metadata", {}).get("stream_source_url") or "")),
                        )
                    )
            else:
                lines.append("No accepted candidates in this scope.")
            lines.append("")
    else:
        lines.append("No accepted candidates in this run.")
    _append_second_stage_filtering_responses_section(
        lines,
        record_groups=record_groups,
        rerun_records=rerun_records,
    )
    lines.append("")
    lines.append("## Rejected And Rerun Decisions")
    lines.append("")
    if any(group_rejected for _, _, group_rejected in record_groups) or rerun_records:
        for group_label, _, group_rejected in record_groups:
            if len(record_groups) > 1:
                lines.append(f"### {group_label}")
                lines.append("")
            if group_rejected:
                lines.append("| Page ID | Stage | Exact reason | Page/question |")
                lines.append("| ---: | --- | --- | --- |")
                for record in group_rejected:
                    lines.append(
                        "| {page_id} | `{stage}` | `{reason}` | {question} |".format(
                            page_id=_record_page_id(record),
                            stage=_rejection_stage(record),
                            reason=_escape_table_text(_exact_failure_reason(record)),
                            question=_escape_table_text(str(record.get("question", ""))),
                        )
                    )
            else:
                lines.append("No rejected decisions in this scope.")
            lines.append("")
        if rerun_records:
            lines.append("### Rerun Records")
            lines.append("")
            lines.append("| Page ID | Stage | Exact reason | Page/question |")
            lines.append("| ---: | --- | --- | --- |")
            for record in rerun_records:
                lines.append(
                    "| {page_id} | `{stage}` | `{reason}` | {url} |".format(
                        page_id=record.get("page_id", ""),
                        stage=_rerun_stage(record),
                        reason=_escape_table_text(str(record.get("reason", ""))),
                        url=_escape_table_text(str(record.get("url", ""))),
                    )
                )
    else:
        lines.append("No rejected or rerun decisions in this run.")
    lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _append_in_run_rerun_outcomes_section(
    lines: list[str],
    *,
    summary: dict,
    accepted_records: list[dict],
    rejected_records: list[dict],
    rerun_records: list[dict],
) -> None:
    """Append final outcomes for page IDs retried from the rerun pool during this invocation."""
    if not rerun_records:
        return
    accepted_by_page_id = {_record_page_id(record): record for record in accepted_records}
    rejected_by_page_id = {_record_page_id(record): record for record in rejected_records}
    rerun_pool_ids = {
        page_id
        for page_id in summary.get("rerun_pool_ids_after_run", [])
        if page_id not in {None, ""}
    }
    attempt_counts: dict[int | str, int] = {}
    first_reason: dict[int | str, str] = {}
    for record in rerun_records:
        page_id = record.get("page_id", "")
        if page_id in {None, ""}:
            continue
        attempt_counts[page_id] = attempt_counts.get(page_id, 0) + 1
        first_reason.setdefault(page_id, str(record.get("reason", "")))
    if not attempt_counts:
        return

    lines.append("### In-Run Rerun Outcomes")
    lines.append("")
    lines.append(
        "These rows show transient rerun-pool attempts and whether the same page ID later reached a final decision in this invocation."
    )
    lines.append("")
    lines.append("| Page ID | Rerun attempts | Final outcome | Final reason/question | First transient reason |")
    lines.append("| ---: | ---: | --- | --- | --- |")
    for page_id in sorted(attempt_counts, key=lambda value: str(value)):
        if page_id in accepted_by_page_id:
            outcome = "accepted"
            detail = str(accepted_by_page_id[page_id].get("question", ""))
        elif page_id in rejected_by_page_id:
            outcome = "rejected"
            detail = _exact_failure_reason(rejected_by_page_id[page_id])
        elif page_id in rerun_pool_ids:
            outcome = "still_in_rerun_pool"
            detail = ""
        else:
            outcome = "not_finalized_in_this_invocation"
            detail = ""
        lines.append(
            "| {page_id} | {attempts} | `{outcome}` | {detail} | `{reason}` |".format(
                page_id=page_id,
                attempts=attempt_counts[page_id],
                outcome=outcome,
                detail=_escape_table_text(detail),
                reason=_escape_table_text(first_reason.get(page_id, "")),
            )
        )


def _append_phase_timings_section(
    lines: list[str],
    *,
    summary: dict,
    existing_accepted_records: list[dict],
    existing_rejected_records: list[dict],
    accepted_records: list[dict],
    rejected_records: list[dict],
) -> None:
    """Append timing tables for the incremental segment and full displayed run."""
    incremental_records = [*accepted_records, *rejected_records]
    total_records = [
        *existing_accepted_records,
        *existing_rejected_records,
        *accepted_records,
        *rejected_records,
    ]
    incremental_stats = summary.get("phase_timing_stats_seconds")
    if not isinstance(incremental_stats, dict):
        incremental_stats = _phase_timing_stats(incremental_records)
    total_stats = _phase_timing_stats(total_records)
    is_incremental = bool(existing_accepted_records or existing_rejected_records)

    lines.append("### Phase Timings")
    lines.append("")
    lines.append(
        "Timing nesting: `wall_clock_seconds` is the whole run. "
        "`total_generation_seconds` contains page fetch/paragraph/table parse/LLM QA generation for one page. "
        "`total_processing_seconds` contains rewrite, number margin, DuckDuckGo search, second-stage grading when enabled, "
        "shared validation, and dedup checks for one generated candidate. "
        "`candidate_processing_seconds` is an alias of `total_processing_seconds`. "
        "Child phase totals are useful for bottlenecks, but they should not be added to parent totals."
    )
    if is_incremental:
        lines.append(
            "For incremental walkthroughs, `Incremental run` means only the current segment. "
            "`Total displayed run` means the endpoint records loaded at resume plus the current segment."
        )
    lines.append("")
    lines.append("| Pipeline order | Phase | Parent/child | Additive? | Meaning |")
    lines.append("| ---: | --- | --- | --- | --- |")
    for row in _phase_timing_explanation_rows():
        lines.append(
            "| {order} | `{phase}` | {kind} | {additive} | {meaning} |".format(
                order=row["order"],
                phase=row["phase"],
                kind=row["kind"],
                additive=row["additive"],
                meaning=row["meaning"],
            )
        )
    lines.append("")

    if is_incremental:
        _append_phase_scope_summary_table(
            lines,
            summary=summary,
            incremental_stats=incremental_stats,
            total_stats=total_stats,
            incremental_record_count=len(incremental_records),
            total_record_count=len(total_records),
        )
        lines.append("")
        lines.append("#### Incremental Run Phase Timings")
    else:
        lines.append("#### Current Run Phase Timings")
    lines.append("")
    _append_phase_stats_table(lines, incremental_stats)
    if is_incremental:
        lines.append("")
        lines.append("#### Total Displayed Run Phase Timings")
        lines.append("")
        _append_phase_stats_table(lines, total_stats)


def _append_phase_scope_summary_table(
    lines: list[str],
    *,
    summary: dict,
    incremental_stats: dict,
    total_stats: dict,
    incremental_record_count: int,
    total_record_count: int,
) -> None:
    """Append compact timing totals for the incremental and cumulative scopes."""
    lines.append("#### Time Stats By Scope")
    lines.append("")
    lines.append(
        "| Scope | Wall-clock seconds | Page IDs/records | Final decision records | "
        "Total generation seconds | Avg generation seconds | Total processing seconds | "
        "Avg processing seconds | Total second-stage seconds | Avg second-stage seconds |"
    )
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    attempted = int(summary.get("attempted_page_ids", 0) or 0)
    incremental_pages = attempted
    endpoint_resume = summary.get("endpoint_resume", {})
    if not isinstance(endpoint_resume, dict):
        endpoint_resume = {}
    existing_record_count = max(0, total_record_count - incremental_record_count)
    final_decisions_loaded = endpoint_resume.get("final_decisions_loaded")
    try:
        existing_pages = int(final_decisions_loaded)
    except (TypeError, ValueError):
        existing_pages = existing_record_count
    total_pages = existing_pages + attempted
    lines.append(
        _phase_scope_summary_row(
            scope="Incremental run",
            wall_clock_seconds=_optional_float(summary.get("wall_clock_seconds")),
            page_count=incremental_pages,
            record_count=incremental_record_count,
            stats=incremental_stats,
        )
    )
    lines.append(
        _phase_scope_summary_row(
            scope="Total displayed run",
            wall_clock_seconds=_walkthrough_total_wall_clock_seconds(summary),
            page_count=total_pages,
            record_count=total_record_count,
            stats=total_stats,
        )
    )


def _phase_scope_summary_row(
    *,
    scope: str,
    wall_clock_seconds: float | None,
    page_count: int,
    record_count: int,
    stats: dict,
) -> str:
    """Return one compact timing summary row."""
    generation = _phase_stats_for(stats, "total_generation_seconds")
    processing = _phase_stats_for(stats, "total_processing_seconds")
    second_stage = _phase_stats_for(stats, "second_stage_grading_seconds")
    return (
        "| {scope} | {wall_clock} | {page_count} | {record_count} | "
        "{generation_total} | {generation_avg} | {processing_total} | {processing_avg} | "
        "{second_stage_total} | {second_stage_avg} |"
    ).format(
        scope=scope,
        wall_clock=_format_optional_seconds(wall_clock_seconds),
        page_count=page_count,
        record_count=record_count,
        generation_total=_format_optional_seconds(generation.get("total")),
        generation_avg=_format_optional_seconds(generation.get("average")),
        processing_total=_format_optional_seconds(processing.get("total")),
        processing_avg=_format_optional_seconds(processing.get("average")),
        second_stage_total=_format_optional_seconds(second_stage.get("total")),
        second_stage_avg=_format_optional_seconds(second_stage.get("average")),
    )


def _append_phase_stats_table(lines: list[str], stats_by_phase: dict) -> None:
    """Append one detailed phase timing table."""
    lines.append("| Phase | Count | Total seconds | Average seconds | Max seconds |")
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    if not stats_by_phase:
        lines.append("| n/a | 0 | n/a | n/a | n/a |")
        return
    for phase, stats in stats_by_phase.items():
        if not isinstance(stats, dict):
            continue
        lines.append(
            "| `{phase}` | {count} | {total} | {average} | {max_value} |".format(
                phase=phase,
                count=int(stats.get("count", 0) or 0),
                total=_format_optional_seconds(stats.get("total")),
                average=_format_optional_seconds(stats.get("average")),
                max_value=_format_optional_seconds(stats.get("max")),
            )
        )


def _phase_stats_for(stats_by_phase: dict, phase: str) -> dict:
    """Return timing stats for one phase, with a stable empty fallback."""
    stats = stats_by_phase.get(phase, {})
    return stats if isinstance(stats, dict) else {}


def _format_optional_seconds(value: object) -> str:
    """Format seconds for markdown timing tables."""
    seconds = _optional_float(value)
    if seconds is None:
        return "n/a"
    return f"{seconds:.4f}"


def _optional_float(value: object) -> float | None:
    """Convert a value to float when possible."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _walkthrough_total_wall_clock_seconds(summary: dict) -> float | None:
    """Return cumulative wall-clock seconds for a resumed walkthrough when available."""
    current_wall_clock = _optional_float(summary.get("wall_clock_seconds"))
    if not isinstance(summary.get("endpoint_resume"), dict) or not summary["endpoint_resume"].get("enabled"):
        return current_wall_clock
    manifest_path = _walkthrough_manifest_path(summary)
    if manifest_path is None or not manifest_path.exists():
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, JSONDecodeError):
        return None
    segments = manifest.get("segments", [])
    if not isinstance(segments, list):
        return None
    summary_output = str(summary.get("summary_output") or "")
    segment_id = str(summary.get("run_segment_id") or "")
    total = 0.0
    for segment in segments:
        if not isinstance(segment, dict):
            continue
        segment_wall_clock = _optional_float(segment.get("wall_clock_seconds"))
        if segment_wall_clock is not None:
            total += segment_wall_clock
        if _manifest_segment_matches_summary(segment, summary_output=summary_output, segment_id=segment_id):
            return round(total, 4)
    if total > 0 and current_wall_clock is not None:
        return round(total + current_wall_clock, 4)
    return None


def _walkthrough_manifest_path(summary: dict) -> Path | None:
    """Return the most likely run artifact manifest path for this walkthrough."""
    raw_manifest_path = str(summary.get("run_artifact_manifest") or "").strip()
    if raw_manifest_path:
        return _workspace_relative_path(raw_manifest_path)
    output_path = str(summary.get("output_path") or "").strip()
    if output_path:
        accepted_path = _workspace_relative_path(output_path)
        suffix = "_accepted.jsonl"
        if accepted_path.name.endswith(suffix):
            run_group_id = accepted_path.name[: -len(suffix)]
            return accepted_path.parent / "run_manifests" / f"{run_group_id}.json"
    return None


def _workspace_relative_path(raw_path: str) -> Path:
    """Resolve a possibly relative artifact path against the repository root."""
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return ROOT / path


def _manifest_segment_matches_summary(segment: dict, *, summary_output: str, segment_id: str) -> bool:
    """Return whether one manifest segment is the current summary segment."""
    segment_summary_output = str(segment.get("summary_output") or "")
    segment_identifier = str(segment.get("segment_id") or "")
    return bool(
        (summary_output and segment_summary_output == summary_output)
        or (segment_id and segment_identifier == segment_id)
    )


def _append_overall_resume_stats(
    lines: list[str],
    *,
    summary: dict,
    existing_accepted_records: list[dict],
    existing_rejected_records: list[dict],
    accepted_records: list[dict],
    rejected_records: list[dict],
    rerun_records: list[dict],
) -> None:
    """Append overall counts across endpoint-loaded and incremental records."""
    existing_final = len(existing_accepted_records) + len(existing_rejected_records)
    attempted = int(summary.get("attempted_page_ids", 0) or 0)
    incremental_accepted = len(accepted_records)
    incremental_rejected = len(rejected_records)
    incremental_rerun = len(rerun_records)
    overall_pages = existing_final + attempted
    overall_accepted = len(existing_accepted_records) + incremental_accepted
    overall_rejected = len(existing_rejected_records) + incremental_rejected
    lines.append("### Overall Displayed Stats")
    lines.append("")
    lines.append("| Scope | Page IDs/records | Accepted | Rejected | Rerun | Accepted/page rate |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
    lines.append(
        "| Existing endpoint records | {records} | {accepted} | {rejected} | 0 | {rate:.1%} |".format(
            records=existing_final,
            accepted=len(existing_accepted_records),
            rejected=len(existing_rejected_records),
            rate=_rate(len(existing_accepted_records), existing_final),
        )
    )
    lines.append(
        "| Incremental run | {records} | {accepted} | {rejected} | {rerun} | {rate:.1%} |".format(
            records=attempted,
            accepted=incremental_accepted,
            rejected=incremental_rejected,
            rerun=incremental_rerun,
            rate=_rate(incremental_accepted, attempted),
        )
    )
    lines.append(
        "| Overall displayed | {records} | {accepted} | {rejected} | {rerun} | {rate:.1%} |".format(
            records=overall_pages,
            accepted=overall_accepted,
            rejected=overall_rejected,
            rerun=incremental_rerun,
            rate=_rate(overall_accepted, overall_pages),
        )
    )


def _append_record_attribute_stats_section(
    lines: list[str],
    *,
    title: str,
    attribute_label: str,
    extractor,
    record_groups: list[tuple[str, list[dict], list[dict]]],
) -> None:
    """Append accepted/rejected counts grouped by one record attribute."""
    lines.append(f"### {title}")
    lines.append("")
    lines.append(f"| Scope | {attribute_label} | Accepted | Rejected | Total | Accepted rate |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: |")
    wrote_row = False
    for group_label, group_accepted, group_rejected in record_groups:
        rows = _record_attribute_counts(group_accepted, group_rejected, extractor=extractor)
        for value, accepted_count, rejected_count in rows:
            total = accepted_count + rejected_count
            lines.append(
                f"| {group_label} | `{_escape_table_text(value)}` | {accepted_count} | "
                f"{rejected_count} | {total} | {_rate(accepted_count, total):.1%} |"
            )
            wrote_row = True
    if not wrote_row:
        lines.append("| n/a | n/a | 0 | 0 | 0 | 0.0% |")


def _record_attribute_counts(
    accepted_records: list[dict],
    rejected_records: list[dict],
    *,
    extractor,
) -> list[tuple[str, int, int]]:
    """Return sorted accepted/rejected counts for one extracted record attribute."""
    accepted_counts = Counter(extractor(record) for record in accepted_records)
    rejected_counts = Counter(extractor(record) for record in rejected_records)
    values = sorted(set(accepted_counts) | set(rejected_counts))
    return [
        (value, int(accepted_counts.get(value, 0)), int(rejected_counts.get(value, 0)))
        for value in values
    ]


def _record_answer_type(record: dict) -> str:
    """Return the SimpleQA Verified answer type for a JSONL record."""
    source_metadata = record.get("source_metadata", {})
    if not isinstance(source_metadata, dict):
        source_metadata = {}
    value = record.get("answer_type") or source_metadata.get("answer_type")
    if not str(value or "").strip():
        return "unknown"
    try:
        normalized = normalize_route3_answer_types([str(value or "")])
    except ValueError:
        normalized = ()
    if normalized:
        return normalized[0]
    return "Other"


def _record_reasoning_type(record: dict) -> str:
    """Return the Route 3 reasoning type for a JSONL record."""
    source_metadata = record.get("source_metadata", {})
    if not isinstance(source_metadata, dict):
        source_metadata = {}
    value = (
        source_metadata.get("reasoning_type")
        or record.get("relation_or_claim")
        or source_metadata.get("legacy_composition_type")
        or source_metadata.get("composition_type")
    )
    if str(value or "").strip() in {"", "wikipedia_table_fact"}:
        allowed_reasoning_types = source_metadata.get("allowed_reasoning_types")
        if isinstance(allowed_reasoning_types, list) and len(allowed_reasoning_types) == 1:
            value = allowed_reasoning_types[0]
    try:
        normalized = normalize_route3_reasoning_types([str(value or "")])
    except ValueError:
        normalized = ()
    if normalized:
        return normalized[0]
    return str(value or "unknown").strip() or "unknown"


def _walkthrough_record_groups(
    *,
    existing_accepted_records: list[dict],
    existing_rejected_records: list[dict],
    accepted_records: list[dict],
    rejected_records: list[dict],
) -> list[tuple[str, list[dict], list[dict]]]:
    """Return record scopes for walkthrough rendering."""
    if existing_accepted_records or existing_rejected_records:
        return [
            ("Existing Endpoint Records", existing_accepted_records, existing_rejected_records),
            ("Incremental Records", accepted_records, rejected_records),
        ]
    return [("Current Run Records", accepted_records, rejected_records)]


def _append_second_stage_filtering_responses_section(
    lines: list[str],
    *,
    record_groups: list[tuple[str, list[dict], list[dict]]],
    rerun_records: list[dict],
) -> None:
    """Append exact second-stage small-model QA responses to the walkthrough."""
    lines.append("## Second-Stage Filtering Responses")
    lines.append("")
    lines.append(
        "These are the small-model QA responses used by the second-stage filter: "
        "`openai/gpt-4.1-mini` and `google/gemini-3-flash-preview`."
    )
    lines.append("")
    if any(group_accepted or group_rejected for _, group_accepted, group_rejected in record_groups):
        for group_label, group_accepted, group_rejected in record_groups:
            records = [*group_accepted, *group_rejected]
            if len(record_groups) > 1:
                lines.append(f"### {group_label}")
                lines.append("")
            if records:
                lines.append("| Page ID | Question | Reference answer | openai/gpt-4.1-mini | google/gemini-3-flash-preview |")
                lines.append("| ---: | --- | --- | --- | --- |")
                for record in records:
                    features = _second_stage_panel_features(record)
                    lines.append(
                        "| {page_id} | {question} | {reference_answer} | {openai} | {gemini} |".format(
                            page_id=_record_page_id(record),
                            question=_escape_table_text(str(record.get("question", ""))),
                            reference_answer=_escape_table_text(_second_stage_reference_answer(record, features)),
                            openai=_escape_table_text(_second_stage_model_cell(features, "openai/gpt-4.1-mini")),
                            gemini=_escape_table_text(_second_stage_model_cell(features, "google/gemini-3-flash-preview")),
                        )
                    )
                lines.append("")
            else:
                lines.append("No final candidate records in this scope.")
                lines.append("")
    else:
        lines.append("No final candidate records were produced in this run.")
    if rerun_records:
        lines.append("")
        lines.append("Rerun-pool entries have no second-stage filtering response unless they reached the panel before the transient failure.")


def _second_stage_panel_features(record: dict) -> dict:
    """Return the stored second-stage panel features for an accepted or rejected record."""
    features = record.get("panel_grading_features")
    if isinstance(features, dict):
        return features
    notes = record.get("rejection_notes", {})
    if isinstance(notes, dict):
        features = notes.get("panel_grading_features")
        if isinstance(features, dict):
            return features
    return {}


def _second_stage_reference_answer(record: dict, features: dict) -> str:
    """Return the reference answer displayed for one second-stage row."""
    reference = features.get("reference_answer_for_grading") or features.get("gold_answer")
    if reference is not None:
        return str(reference)
    return str(record.get("answer", ""))


def _second_stage_model_cell(features: dict, model_name: str) -> str:
    """Return a compact grade/prediction cell for one panel model."""
    models = features.get("models")
    if not isinstance(models, list):
        return "not run"
    for row in models:
        if not isinstance(row, dict) or row.get("model") != model_name:
            continue
        grade = str(row.get("grade", "UNKNOWN")).strip() or "UNKNOWN"
        predicted_answer = str(row.get("predicted_answer", "")).strip()
        if predicted_answer:
            return f"{grade}; predicted_answer: {predicted_answer}"
        return f"{grade}; predicted_answer:"
    return "not run"


def _has_second_stage_model_responses(features: dict) -> bool:
    """Return whether panel features include concrete model answer rows."""
    models = features.get("models")
    return isinstance(models, list) and any(isinstance(row, dict) and row.get("predicted_answer") is not None for row in models)


def _record_page_id(record: dict) -> int | str:
    """Return the positive Wikipedia page ID represented by one output record."""
    page_id = _positive_record_page_id(record.get("page_id"))
    if page_id is not None:
        return page_id
    metadata = record.get("source_metadata", {})
    if isinstance(metadata, dict):
        page_id = _positive_record_page_id(metadata.get("page_id"))
        if page_id is not None:
            return page_id
        streaming = metadata.get("streaming_discovery", {})
        if isinstance(streaming, dict):
            page_id = _positive_record_page_id(streaming.get("page_id"))
            if page_id is not None:
                return page_id
        for key in ("source_url", "stream_source_url", "canonical_url"):
            page_id = _positive_record_page_id(normalize_wikipedia_page_id(str(metadata.get(key) or "")))
            if page_id is not None:
                return page_id
    return ""


def _positive_record_page_id(value: object) -> int | None:
    """Coerce one value into a positive Wikipedia page ID."""
    try:
        page_id = int(value)
    except (TypeError, ValueError):
        return None
    return page_id if page_id > 0 else None


def _escape_inline_code(value: str) -> str:
    return value.replace("`", "'").replace("\n", " ").strip()


def _escape_table_text(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


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


def _load_candidate_inputs(paths: list[Path], *, limit: int) -> list[GeneratedCandidate]:
    """Load serialized Route 3 candidates for downstream validation reruns."""
    candidates: list[GeneratedCandidate] = []
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            candidates.append(_candidate_from_record(json.loads(line)))
            if len(candidates) >= limit:
                return candidates
    return candidates


def _apply_allowed_reasoning_type_filter(candidate: GeneratedCandidate, allowed_reasoning_types: list[str]) -> None:
    """Mark a loaded Route 3 candidate rejected when it violates configured reasoning types."""
    if not allowed_reasoning_types:
        return
    metadata = candidate.source_metadata
    metadata["allowed_reasoning_types"] = list(allowed_reasoning_types)
    llm_response = metadata.get("llm_response")
    if not isinstance(llm_response, dict):
        llm_response = {}
    raw_reasoning_type = (
        metadata.get("reasoning_type")
        or llm_response.get("reasoning_type")
        or metadata.get("legacy_composition_type")
        or metadata.get("composition_type")
    )
    try:
        normalized_values = normalize_route3_reasoning_types([str(raw_reasoning_type or "")])
    except ValueError:
        normalized_values = ()
    reasoning_type = normalized_values[0] if normalized_values else ""
    if reasoning_type in allowed_reasoning_types:
        return
    if "wikipedia_infobox_reasoning_type_not_allowed" not in candidate.notes:
        candidate.notes.append("wikipedia_infobox_reasoning_type_not_allowed")
    rejected_value = reasoning_type or str(raw_reasoning_type or "<missing>").strip() or "<missing>"
    metadata["discard_reason"] = (
        "reasoning_type_not_allowed:"
        f"{rejected_value}; allowed={','.join(allowed_reasoning_types)}"
    )


def _apply_allowed_answer_type_filter(candidate: GeneratedCandidate, allowed_answer_types: list[str]) -> None:
    """Mark a loaded Route 3 candidate rejected when it violates configured answer types."""
    if not allowed_answer_types:
        return
    metadata = candidate.source_metadata
    metadata["allowed_answer_types"] = list(allowed_answer_types)
    llm_response = metadata.get("llm_response")
    if not isinstance(llm_response, dict):
        llm_response = {}
    answer_type = _normalize_answer_type(
        llm_response.get("answer_type") or metadata.get("answer_type") or candidate.answer_type,
        candidate.answer,
        candidate.question,
    )
    candidate.answer_type = answer_type
    metadata["answer_type"] = answer_type
    if answer_type in allowed_answer_types:
        return
    if "wikipedia_infobox_answer_type_not_allowed" not in candidate.notes:
        candidate.notes.append("wikipedia_infobox_answer_type_not_allowed")
    metadata["discard_reason"] = (
        "answer_type_not_allowed:"
        f"{answer_type or '<missing>'}; allowed={','.join(allowed_answer_types)}"
    )


def _attach_route3_extra_prompts(candidate: GeneratedCandidate, extra_prompts: list[str]) -> None:
    """Persist optional stricter prompt rules on a loaded candidate for rewrite prompts."""
    if extra_prompts:
        candidate.source_metadata["extra_prompts"] = list(extra_prompts)


def _attach_route3_table_filter_modes(candidate: GeneratedCandidate, table_filter_modes: list[str]) -> None:
    """Persist active Route 3 table filter modes on a loaded candidate."""
    candidate.source_metadata["table_filter_modes"] = list(table_filter_modes)


def _attach_route3_table_source_types(candidate: GeneratedCandidate, table_source_types: list[str]) -> None:
    """Persist active Route 3 source table types on a loaded candidate."""
    candidate.source_metadata["table_source_types"] = list(table_source_types)


def _attach_route3_prose_leakage_scoring(candidate: GeneratedCandidate, enabled: bool) -> None:
    """Persist the active Route 3 prose-leakage scoring toggle."""
    candidate.source_metadata["prose_leakage_scoring_enabled"] = bool(enabled)


def _candidate_from_record(record: dict) -> GeneratedCandidate:
    """Reconstruct a generated candidate from an accepted or rejected JSONL record."""
    source_metadata = dict(record.get("source_metadata") or {})
    source_metadata.pop("surface_validation_failure_reason", None)
    source_metadata.pop("llm_discard_reason", None)
    llm_response = source_metadata.get("llm_response")
    if not isinstance(llm_response, dict):
        llm_response = {}
    _ensure_small_model_response_metadata(source_metadata)

    question = str(record.get("rewritten_question") or record.get("question") or "").strip()
    answer = str(record.get("answer") or "").strip()
    answer_aliases = _string_list(record.get("answer_aliases", []))
    answer_type = str(record.get("answer_type") or source_metadata.get("answer_type") or "").strip()
    search_queries = _string_list(record.get("search_queries", []))
    relation_or_claim = str(
        record.get("relation_or_claim")
        or source_metadata.get("reasoning_type")
        or source_metadata.get("legacy_composition_type")
        or source_metadata.get("composition_type")
        or "wikipedia_table_fact"
    ).strip()

    if _should_use_llm_response(record, llm_response):
        _record_disabled_tie_warning(record, source_metadata)
        question = str(llm_response.get("question", question)).strip()
        raw_answer = llm_response.get("answer", answer)
        answer, answer_aliases = _normalize_generated_answer(
            raw_answer,
            _string_list(llm_response.get("answer_aliases", [])),
        )
        answer_type = _normalize_answer_type(llm_response.get("answer_type"), answer, question)
        answer_items = _answer_items(raw_answer)
        search_queries = _sanitize_answer_blind_queries(
            llm_response.get("search_queries", []),
            answer=answer,
            answer_aliases=answer_aliases,
            answer_items=answer_items,
        )
        source_metadata["answer_items"] = answer_items
        source_metadata["answer_is_list"] = bool(answer_items)
        source_metadata["answer_type"] = answer_type
        reasoning_type = _reasoning_type(llm_response)
        source_metadata["reasoning_type"] = reasoning_type
        if llm_response.get("composition_type") and "legacy_composition_type" not in source_metadata:
            source_metadata["legacy_composition_type"] = str(llm_response.get("composition_type", "")).strip()
        relation_or_claim = reasoning_type or relation_or_claim
    elif "reasoning_type" not in source_metadata:
        legacy_response = {
            "reasoning_type": source_metadata.get("reasoning_type"),
            "composition_type": source_metadata.get("legacy_composition_type") or source_metadata.get("composition_type"),
        }
        source_metadata["reasoning_type"] = _reasoning_type(legacy_response)
    if relation_or_claim == "wikipedia_table_composition":
        relation_or_claim = str(source_metadata.get("reasoning_type") or "wikipedia_table_fact")

    subject_entity = _entity_reference(record.get("subject_entity", {}))
    answer_entity = _entity_reference(record.get("answer_entity", {}), fallback_name=answer)
    evidence = _evidence_record(record.get("evidence", {}))
    source_table = _selected_source_table(source_metadata, llm_response)
    if source_table:
        source_metadata["selected_source_table"] = source_table
    if source_table.get("normalized_text"):
        evidence.text = str(source_table.get("normalized_text") or "")
        evidence.url = evidence.url or str(source_metadata.get("canonical_url") or source_metadata.get("source_url") or "")
        evidence.source_title = evidence.source_title or str(source_metadata.get("page_title") or "")
        evidence.section = evidence.section or str(source_table.get("section_heading") or "")
    elif not evidence.text:
        evidence.text = str(source_metadata.get("first_paragraph") or "")
        evidence.url = evidence.url or str(source_metadata.get("canonical_url") or source_metadata.get("source_url") or "")
        evidence.source_title = evidence.source_title or str(source_metadata.get("page_title") or "")

    notes = [
        str(note)
        for note in record.get("notes", [])
        if str(note) != "wikipedia_infobox_incomplete_tie_answer"
    ]
    candidate = GeneratedCandidate(
        source_type=str(record.get("source_type") or "wikipedia_tables"),
        generation_route=str(record.get("generation_route") or "route3_wikipedia_infobox"),
        question=question,
        canonical_question=str(record.get("canonical_question") or question),
        rewritten_question=question,
        answer=answer,
        answer_aliases=answer_aliases,
        subject_entity=subject_entity,
        answer_entity=answer_entity,
        relation_or_claim=relation_or_claim or "wikipedia_table_fact",
        evidence=evidence,
        question_family=str(record.get("question_family") or "wikipedia_infobox_table_fact"),
        answer_type=answer_type,
        topic=str(record.get("topic") or record.get("domain") or "Wikipedia semi-structured data"),
        target_time=str(record.get("target_time") or ""),
        source_template_domain=str(record.get("template_key") or "wikipedia_infobox_table"),
        search_queries=search_queries,
        notes=notes,
        source_metadata=source_metadata,
    )
    return candidate


def _record_disabled_tie_warning(record: dict, source_metadata: dict) -> None:
    """Preserve disabled incomplete-tie rejections as metadata warnings."""
    notes = {str(note) for note in record.get("notes", [])}
    if (
        str(record.get("rejection_reason", "")) != "wikipedia_infobox_incomplete_tie_answer"
        and "wikipedia_infobox_incomplete_tie_answer" not in notes
    ):
        return
    warnings = source_metadata.setdefault("route_guard_warnings", {})
    if isinstance(warnings, dict):
        warnings["wikipedia_infobox_incomplete_tie_answer"] = str(
            source_metadata.get("discard_reason") or "disabled_incomplete_tie_answer_guard"
        )


def _should_use_llm_response(record: dict, llm_response: dict) -> bool:
    """Return whether stored Route 3 LLM output should rebuild the candidate."""
    if not llm_response:
        return False
    if not str(llm_response.get("question", "")).strip():
        return False
    if not str(llm_response.get("answer", "")).strip() and not isinstance(llm_response.get("answer"), list):
        return False
    return True


def _entity_reference(value: object, *, fallback_name: str = "") -> EntityReference:
    """Convert a serialized entity object into an EntityReference."""
    if not isinstance(value, dict):
        return EntityReference(name=fallback_name)
    return EntityReference(
        name=str(value.get("name") or fallback_name),
        qid=str(value.get("qid") or ""),
        wikipedia_title=str(value.get("wikipedia_title") or ""),
        url=str(value.get("url") or ""),
    )


def _evidence_record(value: object) -> EvidenceRecord:
    """Convert a serialized evidence object into an EvidenceRecord."""
    if not isinstance(value, dict):
        return EvidenceRecord()
    return EvidenceRecord(
        text=str(value.get("text") or ""),
        url=str(value.get("url") or ""),
        source_title=str(value.get("source_title") or ""),
        section=str(value.get("section") or ""),
        retrieved_at=str(value.get("retrieved_at") or ""),
    )


def _selected_source_table(source_metadata: dict, llm_response: dict) -> dict:
    """Return selected source-table metadata from a prior run record."""
    selected = source_metadata.get("selected_source_table")
    if isinstance(selected, dict) and selected:
        return selected
    try:
        table_index = int(llm_response.get("source_table"))
    except (TypeError, ValueError):
        table_index = -1
    tables = source_metadata.get("parsed_tables", [])
    if isinstance(tables, list):
        for table in tables:
            if isinstance(table, dict) and int(table.get("table_index", -2)) == table_index:
                return table
    return {}


def _url_entries_from_candidates(candidates: list[GeneratedCandidate]) -> list[UrlEntry]:
    """Build summary URL rows from loaded candidate metadata."""
    entries: list[UrlEntry] = []
    seen: set[str] = set()
    for candidate in candidates:
        metadata = candidate.source_metadata
        url = str(metadata.get("source_url") or metadata.get("canonical_url") or candidate.subject_entity.url)
        if not url or url in seen:
            continue
        seen.add(url)
        entries.append(UrlEntry(url=url, domain=str(metadata.get("content_domain") or "")))
    return entries


def _string_list(value: object) -> list[str]:
    """Return a clean string list."""
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _optional_proxy(value: str) -> str | None:
    """Normalize CLI proxy values."""
    if value.strip().lower() in {"", "none", "direct", "off"}:
        return None
    return value


def _aggregate_phase_timings(accepted: list[dict], rejected: list[dict]) -> dict[str, float]:
    """Aggregate candidate phase timings across accepted and rejected records."""
    totals: dict[str, float] = {}
    for record in [*accepted, *rejected]:
        timings = record.get("source_metadata", {}).get("phase_timings_seconds", {})
        if not isinstance(timings, dict):
            continue
        for phase, seconds in timings.items():
            try:
                totals[phase] = round(totals.get(phase, 0.0) + float(seconds), 4)
            except (TypeError, ValueError):
                continue
    return totals


if __name__ == "__main__":
    raise SystemExit(main())
