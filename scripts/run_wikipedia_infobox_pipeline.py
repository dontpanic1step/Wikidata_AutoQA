"""Run the Wikipedia infobox/table QA route over supplied page URLs."""

from __future__ import annotations

import argparse
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
from time import perf_counter

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
from wikidata_simpleqa.search_client import DuckDuckGoSearchClient
from wikidata_simpleqa.wikipedia_client import WikipediaClient, normalize_wikipedia_page_id, normalize_wikipedia_title
from wikidata_simpleqa.wikipedia_infobox_generator import (
    WikipediaInfoboxTableGenerator,
    _answer_items,
    _normalize_answer_type,
    _normalize_generated_answer,
    _reasoning_type,
    _sanitize_answer_blind_queries,
)
from wikidata_simpleqa.wikipedia_streaming import (
    BROAD_TABLE_SEARCH_QUERY,
    DEFAULT_PAGE_ID_MAX,
    DEFAULT_PAGE_ID_MIN,
    DEFAULT_TABLE_SEARCH_QUERIES,
    PageIdStreamState,
    build_pageid_url,
)


@dataclass(slots=True)
class UrlEntry:
    """One Wikipedia URL and its optional broad content domain."""

    url: str
    domain: str = ""
    subdomain: str = ""


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
    parser.add_argument("--stream-random-seed", type=int, default=42)
    parser.add_argument("--stream-batch-size", type=int, default=10)
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
    parser.add_argument("--generated-search-query-count", type=int, default=2)
    parser.add_argument(
        "--min-table-score",
        type=float,
        default=0.0,
        help="Drop Route 3 candidate tables with rank score below this value before paragraph/alias extraction and LLM generation.",
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
    endpoint_resume = _load_endpoint_resume(args)
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
    if args.run_artifact_manifest is not None and not args.run_group_id.strip():
        raise ValueError("--run-artifact-manifest requires --run-group-id.")
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
    )
    wikipedia_client = WikipediaClient(
        user_agent=settings.user_agent,
        proxy=settings.proxy,
        timeout_seconds=settings.timeout_seconds,
        cache_dir=settings.cache_dir,
    )
    search_client = DuckDuckGoSearchClient(
        user_agent=settings.user_agent,
        proxy=settings.proxy,
        timeout_seconds=settings.timeout_seconds,
        cache_dir=settings.cache_dir,
    )
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
    _renumber_accepted_records(result.accepted, offset=endpoint_resume.accepted_count if args.start_from_endpoint else 0)
    if args.start_from_endpoint:
        append_jsonl(args.output, result.accepted)
        append_jsonl(args.rejected_output, result.rejected)
    else:
        write_jsonl(args.output, result.accepted)
        write_jsonl(args.rejected_output, result.rejected)
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
        "generated_search_query_count": settings.generated_search_query_count,
        "min_table_score": args.min_table_score,
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
        "record_limit": summary.get("record_limit", 0),
        "attempted_page_ids": summary.get("attempted_page_ids", summary.get("attempted_urls", 0)),
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


def _renumber_accepted_records(records: list[dict], *, offset: int) -> None:
    """Keep appended accepted records from reusing existing JSONL IDs."""
    for index, record in enumerate(records, start=offset + 1):
        record["id"] = f"simpleqa_candidate_{index:06d}"


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
        {"fetch_summary", "fetch_parse", "search_page_ids"},
    )
    search_client = SemaphoreWrappedClient(
        search_client,
        concurrency.duckduckgo_semaphore,
        {"search"},
    )
    llm_client = SemaphoreWrappedClient(
        llm_client,
        concurrency.generation_rewrite_semaphore,
        {"complete_text"},
    )
    if rewrite_client is not None:
        rewrite_client = SemaphoreWrappedClient(
            rewrite_client,
            concurrency.generation_rewrite_semaphore,
            {"rewrite_question"},
        )
    second_stage_model_clients = _build_streaming_second_stage_model_panel(settings, concurrency)
    grading_grader_client = _build_streaming_second_stage_grader_client(settings, concurrency)
    state = PageIdStreamState.load(args.stream_state)
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
    ids_remaining = max(0, int(args.record_limit))
    if args.start_from_endpoint:
        ids_remaining = _remaining_after_endpoint(args.record_limit, endpoint_resume.final_decision_count)
    page_workers = 1 if accepted_target else max(1, int(args.stream_page_workers))

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
        "run_date": settings.run_date,
        "stream_state": str(args.stream_state),
        "stream_state_stats": state.stats(),
        "rerun_pool_ids_after_run": state.rerun_pool.copy(),
        "rerun_pool_failure_reasons_after_run": {
            str(page_id): state.failure_reasons.get(page_id, "")
            for page_id in state.rerun_pool
        },
        "recovered_stale_in_progress_ids": recovered_ids,
        "page_id_bounds": {
            "min": args.stream_page_id_min,
            "max": args.stream_page_id_max,
        },
        "random_seed": args.stream_random_seed,
        "record_limit": args.record_limit,
        "record_limit_remaining_at_start": ids_remaining + len(processed_ids),
        "stream_batch_size": args.stream_batch_size,
        "stream_page_workers": page_workers,
        "wikipedia_concurrency_limit": args.wikipedia_concurrency_limit,
        "duckduckgo_concurrency_limit": args.duckduckgo_concurrency_limit,
        "openrouter_generation_rewrite_concurrency_limit": args.openrouter_generation_rewrite_concurrency_limit,
        "second_stage_concurrency_limit": args.second_stage_concurrency_limit,
        "stream_accepted_target": args.stream_accepted_target,
        "stream_accepted_target_remaining_at_start": accepted_target,
        "attempted_page_ids": len(processed_ids),
        "page_ids": processed_ids,
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
        "generated_search_query_count": settings.generated_search_query_count,
        "min_table_score": args.min_table_score,
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
) -> dict:
    """Run one page ID through generation and shared processing."""
    url = build_pageid_url(page_id)
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
        candidate = generated_candidates[0]
        _attach_stream_metadata(candidate, page_id=page_id, url=url, args=args)
        result = process_generated_candidates(
            [candidate],
            settings=settings,
            search_client=search_client,
            rewrite_client=rewrite_client,
            second_stage_model_clients=second_stage_model_clients,
            grading_grader_client=grading_grader_client,
        )
        if result.accepted:
            with concurrency.commit_lock:
                for index, record in enumerate(result.accepted):
                    record["id"] = f"wikipedia_stream_{len(state.accepted_ids) + index + 1:06d}"
                    _attach_stream_record_metadata(record, page_id=page_id, url=url, args=args)
                append_jsonl(args.output, result.accepted)
                state.mark_accepted(page_id)
            return {
                "status": "accepted",
                "page_id": page_id,
                "url": url,
                "accepted_records": result.accepted,
                "rejected_records": [],
            }
        if result.rejected:
            for record in result.rejected:
                _attach_stream_record_metadata(record, page_id=page_id, url=url, args=args)
            reason = _exact_failure_reason(result.rejected[0])
            if _should_rerun_stream_rejection(result.rejected[0]):
                with concurrency.commit_lock:
                    state.mark_rerun(page_id, reason=reason)
                return {
                    "status": "rerun",
                    "page_id": page_id,
                    "url": url,
                    "accepted_records": [],
                    "rejected_records": [],
                    "reason": reason,
                }
            with concurrency.commit_lock:
                append_jsonl(args.rejected_output, result.rejected)
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
        reason = f"pipeline_exception:{type(exc).__name__}"
        with concurrency.commit_lock:
            state.mark_rerun(page_id, reason=reason)
        return {
            "status": "rerun",
            "page_id": page_id,
            "url": url,
            "reason": reason,
            "error_message": str(exc),
        }


def _should_rerun_stream_rejection(record: dict) -> bool:
    """Return whether a rejected stream record represents a transient retryable failure."""
    reason = str(record.get("rejection_reason", "")).strip()
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
    )
    return any(marker in error_text for marker in retryable_markers)


def _reserve_stream_page_ids(
    *,
    state: PageIdStreamState,
    args: argparse.Namespace,
    wikipedia_client: WikipediaClient,
    rng: random.Random,
    count: int,
) -> list[int]:
    """Reserve page IDs from the configured streaming discovery source."""
    if args.stream_page_source == "random-page-id":
        return state.reserve_ids(
            count=count,
            lower_bound=args.stream_page_id_min,
            upper_bound=args.stream_page_id_max,
            rng=rng,
            prefer_rerun_pool=True,
        )

    selected = state.reserve_candidate_ids(
        [],
        count=count,
        source="rerun_pool",
        prefer_rerun_pool=True,
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
            try:
                hits = wikipedia_client.search_page_ids(
                    query,
                    namespace=0,
                    limit=args.stream_search_limit,
                    offset=offset,
                )
            except Exception as exc:  # noqa: BLE001
                state.record_discovery_error(
                    source=f"table_search:{query}:offset={offset}",
                    error=f"{type(exc).__name__}:{exc}",
                )
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


def _attach_stream_metadata(candidate: GeneratedCandidate, *, page_id: int, url: str, args: argparse.Namespace) -> None:
    """Attach stream sampling metadata to a generated candidate."""
    _ensure_small_model_response_metadata(candidate.source_metadata)
    _attach_run_artifact_metadata(candidate.source_metadata, args=args)
    candidate.source_metadata["page_id"] = page_id
    candidate.source_metadata["stream_source_url"] = url
    candidate.source_metadata["streaming_discovery"] = {
        "mode": "page_id_stream",
        "page_source": args.stream_page_source,
        "page_id": page_id,
        "pageid_url": url,
        "page_id_min": args.stream_page_id_min,
        "page_id_max": args.stream_page_id_max,
        "random_seed": args.stream_random_seed,
        "domain_policy": "domain_and_subdomain_optional",
    }


def _attach_stream_record_metadata(record: dict, *, page_id: int, url: str, args: argparse.Namespace) -> None:
    """Attach stream sampling metadata to a serialized output record."""
    metadata = record.setdefault("source_metadata", {})
    if isinstance(metadata, dict):
        _ensure_small_model_response_metadata(metadata)
        _attach_run_artifact_metadata(metadata, args=args)
        metadata["page_id"] = page_id
        metadata["stream_source_url"] = url
        metadata["streaming_discovery"] = {
            "mode": "page_id_stream",
            "page_source": args.stream_page_source,
            "page_id": page_id,
            "pageid_url": url,
            "page_id_min": args.stream_page_id_min,
            "page_id_max": args.stream_page_id_max,
            "random_seed": args.stream_random_seed,
            "domain_policy": "domain_and_subdomain_optional",
        }


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
    if rerun_records:
        stage_failures["unresolved_rerun"] += len(rerun_records)
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
    """Return exact failure reasons grouped by stage."""
    counts: Counter[tuple[str, str]] = Counter()
    for record in rejected_records:
        counts[(_rejection_stage(record), _exact_failure_reason(record))] += 1
    for record in rerun_records:
        counts[("unresolved_rerun", str(record.get("reason", "unresolved")))] += 1
    return [
        {"stage": stage, "reason": reason, "count": count}
        for (stage, reason), count in sorted(counts.items(), key=lambda item: (-item[1], item[0][0], item[0][1]))
    ]


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
    if reason.startswith("wikipedia_infobox_"):
        return "route_generation"
    if reason in {"llm_rewrite_discarded", "rewrite_guard_rejected"}:
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
    notes = record.get("rejection_notes", {})
    if not isinstance(notes, dict):
        return reason
    if reason == "rewrite_guard_rejected":
        rule = record.get("rejection_rule") or notes.get("failure_reason") or notes.get("surface_validation_failure_reason")
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
    lines.append(f"- Accepted QAs: {summary.get('accepted', 0)}")
    if isinstance(endpoint_resume, dict) and endpoint_resume.get("enabled"):
        lines.append(f"- Accepted QAs after resume: {summary.get('accepted_total', 0)}")
    lines.append(f"- Rejected QAs/pages: {summary.get('rejected', 0)}")
    if isinstance(endpoint_resume, dict) and endpoint_resume.get("enabled"):
        lines.append(f"- Rejected QAs/pages after resume: {summary.get('rejected_total', 0)}")
    lines.append(f"- Returned to rerun pool without final decision: {summary.get('rerun', 0)}")
    if summary.get("wall_clock_seconds") is not None:
        lines.append(f"- Wall-clock runtime: {float(summary.get('wall_clock_seconds', 0.0)):.4f}s")
    lines.append(f"- DuckDuckGo top K: {summary.get('duckduckgo_top_k', '')}")
    lines.append(f"- Generated search queries per QA: {summary.get('generated_search_query_count', '')}")
    lines.append(f"- DuckDuckGo parallel queries: {summary.get('duckduckgo_parallel_queries', '')}")
    if summary.get("min_table_score") is not None:
        lines.append(f"- Minimum Route 3 table score: {summary.get('min_table_score', '')}")
    if summary.get("stream_page_workers") is not None:
        lines.append(f"- Stream page workers: {summary.get('stream_page_workers', '')}")
        lines.append(f"- Wikipedia concurrency limit: {summary.get('wikipedia_concurrency_limit', '')}")
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
    lines.append("| Stage | Exact reason | Count |")
    lines.append("| --- | --- | ---: |")
    for row in summary.get("failure_reason_counts", []):
        lines.append(f"| `{row.get('stage', '')}` | `{_escape_table_text(str(row.get('reason', '')))}` | {row.get('count', 0)} |")
    if not summary.get("failure_reason_counts"):
        lines.append("| n/a | n/a | 0 |")
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
                lines.append("| Page ID | Question | Answer | Source |")
                lines.append("| ---: | --- | --- | --- |")
                for record in group_accepted:
                    lines.append(
                        "| {page_id} | {question} | {answer} | {url} |".format(
                            page_id=_record_page_id(record),
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
                    "| {page_id} | `unresolved_rerun` | `{reason}` | {url} |".format(
                        page_id=record.get("page_id", ""),
                        reason=_escape_table_text(str(record.get("reason", ""))),
                        url=_escape_table_text(str(record.get("url", ""))),
                    )
                )
    else:
        lines.append("No rejected or rerun decisions in this run.")
    lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


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
    metadata = record.get("source_metadata", {})
    if isinstance(metadata, dict):
        page_id = metadata.get("page_id")
        if page_id:
            return page_id
        source_url = str(metadata.get("source_url") or metadata.get("stream_source_url") or "")
        parsed = normalize_wikipedia_page_id(source_url)
        if parsed is not None:
            return parsed
    return ""


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
