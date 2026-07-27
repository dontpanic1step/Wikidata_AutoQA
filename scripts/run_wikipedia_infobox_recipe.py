"""Run a Route 3 Wikipedia table batch recipe across answer types."""

from __future__ import annotations

import argparse
from contextlib import ExitStack, contextmanager
import inspect
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.cli_output import print_json_summary
from wikidata_simpleqa.io import append_jsonl, write_jsonl
from wikidata_simpleqa.page_id_lists import (
    PageIdListEntry,
    build_page_id_entries,
    extract_page_id_entries_from_payload,
)
from wikidata_simpleqa.route3_ids import assign_unique_route3_record_ids
from wikidata_simpleqa.route3_quantity_prediction import predict_pre_review_quantities
from wikidata_simpleqa.route3_external_lifecycle import (
    resolve_ambiguous_external_calls,
    write_ambiguous_external_call_reports,
)
from wikidata_simpleqa.route3_run_ledger import (
    SegmentLedgerIndex,
    atomic_write_json,
    build_segment_fingerprint,
    canonical_json_sha256,
    create_segment_manifest,
    derive_segment_manifest_state,
    ledger_summary,
    load_segment_manifest,
    rebuild_derived_outputs,
    rebuild_summary_from_ledger,
    require_matching_fingerprint,
    update_segment_manifest,
)
from wikidata_simpleqa.search_cli import add_duckduckgo_transport_args, duckduckgo_settings_kwargs
from wikidata_simpleqa.wikipedia_infobox_generator import (
    DEFAULT_ROUTE3_ANSWER_TYPE_MODE,
    DEFAULT_ROUTE3_INFOBOX_MAX_REMOVED_ROW_RATE,
    DEFAULT_ROUTE3_INFOBOX_MIN_REMAINING_ROWS,
    DEFAULT_ROUTE3_PAGE_ARCHIVE_DIR,
    ROUTE3_ANSWER_TYPES,
    DEFAULT_ROUTE3_REASONING_TYPES,
    DEFAULT_ROUTE3_TABLE_FILTER_MODES,
    DEFAULT_ROUTE3_TABLE_SOURCE_TYPES,
    normalize_route3_answer_types,
    normalize_route3_answer_type_mode,
    build_route3_infobox_prompt,
    build_route3_wikitable_prompt,
    build_wikipedia_infobox_prompt,
    normalize_route3_table_source_types,
)
from wikidata_simpleqa.route3_worker_support import (
    aggregate_phase_timings,
    effective_stream_random_seed,
    failure_reason_counts,
    ensure_page_id_list_entry_metadata,
    load_endpoint_jsonl,
    phase_timing_stats,
    llm_generation_table_yield_summary,
    normalize_stream_fresh_cached_page_count,
    normalize_stream_reuse_cached_page_count,
    safe_artifact_id,
    stream_budget_numeric_count,
    survival_by_layer,
    write_stream_walkthrough,
)

@dataclass(frozen=True, slots=True)
class RecipeItem:
    """One answer-type segment in a Route 3 recipe."""

    answer_type: str
    record_limit: int


ALL_TYPES_RECIPE_ANSWER_TYPE = "AllTypes"


def _apply_recipe_big_batch_mode(args: argparse.Namespace) -> None:
    """Apply recipe-level large-run defaults before segment commands are built."""
    if not getattr(args, "big_batch_mode", False):
        return
    args.stream_batch_size = max(1, int(getattr(args, "stream_search_limit", 50) or 50))
    args.stream_search_max_rounds = max(500, int(getattr(args, "stream_search_max_rounds", 10) or 10))


def parse_args() -> argparse.Namespace:
    """Parse recipe runner arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--page-attempt-count",
        type=int,
        default=None,
        help="Number of primary Wikipedia pages to attempt; required except with --status.",
    )
    parser.add_argument(
        "--answer-type",
        choices=[*ROUTE3_ANSWER_TYPES, ALL_TYPES_RECIPE_ANSWER_TYPE],
        default=None,
        help="One specific answer type for single mode, or AllTypes for all5 mode; required except with --status.",
    )
    parser.add_argument(
        "--route3-table-source-type",
        action="append",
        default=[],
        help=(
            "Shared Route 3 source table types: infobox, wikitable, or both/all. "
            "Repeat or pass comma-separated values. Default: both."
        ),
    )
    parser.add_argument(
        "--route3-answer-type-mode",
        choices=["single", "all5"],
        default=DEFAULT_ROUTE3_ANSWER_TYPE_MODE,
        help=(
            "Shared Route 3 answer-type mode. Recipe items named AllTypes/all5 force all5 for that segment."
        ),
    )
    parser.add_argument(
        "--route3-page-archive-dir",
        type=Path,
        default=ROOT / DEFAULT_ROUTE3_PAGE_ARCHIVE_DIR,
        help="Directory for unified Route 3 page archives.",
    )
    parser.add_argument(
        "--route3-infobox-max-removed-row-rate",
        type=float,
        default=DEFAULT_ROUTE3_INFOBOX_MAX_REMOVED_ROW_RATE,
    )
    parser.add_argument(
        "--route3-infobox-min-remaining-rows",
        type=int,
        default=DEFAULT_ROUTE3_INFOBOX_MIN_REMAINING_ROWS,
    )
    parser.add_argument("--run-id", default="", help="Path-safe batch ID. Defaults to a dated recipe ID.")
    parser.add_argument(
        "--exclude-run-id",
        default="",
        help="Older recipe run whose canonical page IDs are excluded from this new run.",
    )
    parser.add_argument("--run-date", default=None)
    parser.add_argument("--cutoff-year", type=int, default=2025)
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--proxy", default="none")
    parser.add_argument("--small-model-provider", default="openrouter")
    parser.add_argument("--generation-model", dest="generation_model", default="google/gemini-3-flash-preview")
    parser.add_argument(
        "--small-model",
        dest="generation_model",
        default=argparse.SUPPRESS,
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--small-model-api-key-env", default="OPENROUTER_API_KEY")
    parser.add_argument("--small-model-base-url", default="https://openrouter.ai/api/v1")
    parser.add_argument("--small-model-max-tokens", type=int, default=4096)
    parser.add_argument("--enable-second-stage-grading", action="store_true", default=True)
    parser.add_argument("--second-stage-grading-accuracy-threshold", type=float, default=0.1)
    parser.add_argument("--duckduckgo-top-k", type=int, default=5)
    parser.add_argument("--duckduckgo-parallel-queries", type=int, default=3)
    add_duckduckgo_transport_args(parser)
    parser.add_argument("--generated-search-query-count", type=int, default=2)
    parser.add_argument("--search-longtail-max-full-question-hit-rate", type=float, default=0.3)
    parser.add_argument("--search-longtail-max-keyword-hit-rate", type=float, default=0.3)
    parser.add_argument("--search-longtail-max-overall-hit-rate", type=float, default=0.3)
    parser.add_argument("--stream-search-limit", type=int, default=50)
    parser.add_argument("--stream-search-max-rounds", type=int, default=10)
    parser.add_argument(
        "--stream-random-seed",
        type=int,
        default=None,
        help=(
            "Base seed for recipe streaming. When omitted, each segment gets a deterministic "
            "run/segment-specific seed."
        ),
    )
    parser.add_argument("--stream-batch-size", type=int, default=10)
    parser.add_argument("--stream-discovery-max-retries", type=int, default=5)
    parser.add_argument("--stream-discovery-retry-backoff-seconds", type=float, default=10.0)
    parser.add_argument("--stream-discovery-retry-max-sleep-seconds", type=float, default=60.0)
    parser.add_argument(
        "--stream-reuse-cached-page-count",
        default="all",
        help="Recipe-level cached-page budget: a non-negative integer or 'all' to reuse cache until segment targets are met.",
    )
    parser.add_argument(
        "--stream-fresh-cached-page-count",
        default="fill",
        help="Recipe-level fresh-page budget: a non-negative integer or 'fill' to fetch fresh pages until segment targets are met.",
    )
    parser.add_argument("--wikipedia-429-backoff-seconds", type=float, default=30.0)
    parser.add_argument("--wikipedia-429-max-backoff-seconds", type=float, default=300.0)
    parser.add_argument("--wikipedia-429-recovery-seconds", type=float, default=120.0)
    parser.add_argument("--stream-page-workers", type=int, default=4)
    parser.add_argument("--wikipedia-concurrency-limit", type=int, default=4)
    parser.add_argument("--duckduckgo-concurrency-limit", type=int, default=4)
    parser.add_argument("--openrouter-generation-rewrite-concurrency-limit", type=int, default=10)
    parser.add_argument("--second-stage-concurrency-limit", type=int, default=10)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--rejected-output", type=Path, default=None)
    parser.add_argument("--summary-output", type=Path, default=None)
    parser.add_argument("--walkthrough-output", type=Path, default=None)
    parser.add_argument("--stream-state", type=Path, default=None)
    parser.add_argument("--segment-dir", type=Path, default=None)
    parser.add_argument("--compact-rejected-output", action="store_true")
    parser.add_argument("--compact-output", action="store_true")
    parser.add_argument("--big-batch-mode", action="store_true")
    parser.add_argument(
        "--append-to-existing-run",
        action="store_true",
        help=(
            "Top up an existing recipe run with a new segment. "
            "The run-group allocation ledger excludes every previously allocated page."
        ),
    )
    parser.add_argument(
        "--append-run-label",
        default="",
        help="Path-safe suffix for --append-to-existing-run segment artifacts. Defaults to a UTC timestamp.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume an existing same-fingerprint segment from durable records.",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Print ledger-derived status for --run-id without running a worker.",
    )
    parser.add_argument(
        "--resolve-ambiguous",
        choices=("retry", "abandon"),
        default=None,
        help="Resolve every unresolved ambiguous call during --resume.",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    """Hold segment writer locks for the complete recipe invocation."""
    with ExitStack() as segment_writer_locks:
        return _main(segment_writer_locks)


def _main(segment_writer_locks: ExitStack) -> int:
    """Run the recipe segments and combine their artifacts."""
    args = parse_args()
    _validate_lifecycle_args(args)
    if args.status:
        run_id = safe_artifact_id(args.run_id, fallback="route3_recipe")
        segment_dir = args.segment_dir or ROOT / "outputs" / "recipe_segments" / run_id
        print_json_summary(_recipe_status_payload(run_id, segment_dir))
        return 0
    _apply_recipe_big_batch_mode(args)
    run_started = perf_counter()
    args.run_date = args.run_date or date.today().isoformat()
    recipe_items, reasoning_types = _parse_recipe(args)
    args.route3_answer_type_mode = normalize_route3_answer_type_mode(args.route3_answer_type_mode)
    table_filter_modes = list(DEFAULT_ROUTE3_TABLE_FILTER_MODES)
    table_source_types = list(
        normalize_route3_table_source_types(args.route3_table_source_type or DEFAULT_ROUTE3_TABLE_SOURCE_TYPES)
    )
    args.route3_infobox_max_removed_row_rate = max(0.0, min(1.0, float(args.route3_infobox_max_removed_row_rate)))
    args.route3_infobox_min_remaining_rows = max(0, int(args.route3_infobox_min_remaining_rows))
    args.stream_reuse_cached_page_count = normalize_stream_reuse_cached_page_count(
        args.stream_reuse_cached_page_count
    )
    args.stream_fresh_cached_page_count = normalize_stream_fresh_cached_page_count(
        args.stream_fresh_cached_page_count
    )
    run_id = _recipe_run_id(args, recipe_items, reasoning_types)
    segment_dir = args.segment_dir or ROOT / "outputs" / "recipe_segments" / run_id
    output = args.output or ROOT / "outputs" / f"{run_id}_accepted.jsonl"
    rejected_output = args.rejected_output or ROOT / "outputs" / f"{run_id}_rejected.jsonl"
    summary_output = args.summary_output or ROOT / "outputs" / f"{run_id}_summary.json"
    walkthrough_output = args.walkthrough_output or ROOT / "outputs" / f"{run_id}_walkthrough.md"
    stream_state_base = args.stream_state or segment_dir / "stream_state.json"
    append_label = _recipe_append_label(args)
    if not args.dry_run:
        _require_clean_worktree()

    segment_dir.mkdir(parents=True, exist_ok=True)
    if not args.dry_run:
        segment_writer_locks.enter_context(_recipe_group_lock(segment_dir))
    segment_summaries: list[dict] = []
    remaining_reuse_cached_page_count = args.stream_reuse_cached_page_count
    remaining_fresh_cached_page_count = args.stream_fresh_cached_page_count
    for index, item in enumerate(recipe_items):
        segment_reuse_cached_page_count = _recipe_segment_budget(
            remaining_reuse_cached_page_count,
            item.record_limit,
        )
        segment_fresh_cached_page_count = _recipe_segment_budget(
            remaining_fresh_cached_page_count,
            item.record_limit,
        )
        base_segment_id = _base_segment_id_for_run(
            segment_dir=segment_dir,
            item=item,
            index=index,
            append_label=append_label,
        )
        segment_id = _append_segment_id(base_segment_id, append_label)
        if not args.dry_run:
            segment_writer_locks.enter_context(_segment_writer_lock(segment_dir / segment_id))
        excluded_page_ids_file: Path | None = None
        external_page_exclusion: dict | None = None
        if args.exclude_run_id:
            excluded_page_ids_file = segment_dir / segment_id / EXCLUDED_PAGE_IDS_FILENAME
            if not args.dry_run:
                external_page_exclusion = _create_or_load_external_page_exclusion(
                    segment_root=segment_dir / segment_id,
                    exclude_run_id=args.exclude_run_id,
                )
        base_stream_search_initial_offset = _segment_stream_search_initial_offset(
            recipe_items,
            index,
            args.stream_search_limit,
        )
        segment_stream_search_initial_offset = base_stream_search_initial_offset
        command, paths = _segment_command(
            args=args,
            item=item,
            index=index,
            run_id=run_id,
            segment_dir=segment_dir,
            stream_state_base=stream_state_base,
            stream_search_initial_offset=segment_stream_search_initial_offset,
            table_source_types=table_source_types,
            append_label=append_label,
            base_segment_id=base_segment_id,
            stream_reuse_cached_page_count=segment_reuse_cached_page_count,
            stream_fresh_cached_page_count=segment_fresh_cached_page_count,
            excluded_page_ids_file=excluded_page_ids_file,
        )
        manifest: dict | None = None
        if not args.dry_run:
            segment_seed = _recipe_segment_seed(
                args=args,
                run_id=run_id,
                segment_id=segment_id,
                answer_type=item.answer_type,
                index=index,
            )
            fingerprint = _segment_fingerprint(
                args=args,
                item=item,
                run_id=run_id,
                segment_id=segment_id,
                stream_random_seed=segment_seed,
                table_source_types=table_source_types,
                stream_reuse_cached_page_count=segment_reuse_cached_page_count,
                stream_fresh_cached_page_count=segment_fresh_cached_page_count,
                external_page_exclusion=external_page_exclusion,
            )
            if append_label:
                _require_top_up_prerequisites(
                    segment_dir=segment_dir,
                    run_group_id=run_id,
                    base_segment_id=base_segment_id,
                    current_segment_id=segment_id,
                    requested_fingerprint=fingerprint,
                )
            manifest = load_segment_manifest(paths["manifest"])
            if manifest is None and args.resume:
                raise ValueError(f"--resume requires an existing segment: {paths['manifest']}")
            if manifest is not None and not args.resume:
                raise ValueError(f"Existing segment requires --resume: {paths['manifest']}")
            if manifest is None:
                manifest = create_segment_manifest(
                    run_group_id=run_id,
                    segment_id=segment_id,
                    fingerprint=fingerprint,
                    artifacts={
                        "accepted": str(paths["accepted"]),
                        "rejected": str(paths["rejected"]),
                        "summary": str(paths["summary"]),
                        "stream_state": str(paths["stream_state"]),
                        "page_allocation_ledger": str(paths["allocations"]),
                        "page_attempt_ledger": str(paths["ledger"]),
                        "external_call_records": str(paths["external_calls"]),
                        "ddg_verifier_results": str(paths["ddg_results"]),
                        "ambiguous_external_calls_json": str(paths["ambiguous_json"]),
                        "ambiguous_external_calls_markdown": str(paths["ambiguous_markdown"]),
                        **(
                            {"external_page_exclusion": str(paths["excluded_page_ids"])}
                            if external_page_exclusion is not None
                            else {}
                        ),
                    },
                )
                atomic_write_json(paths["manifest"], manifest)
            else:
                require_matching_fingerprint(
                    manifest,
                    fingerprint,
                    path=paths["manifest"],
                )
                if args.resolve_ambiguous:
                    resolve_ambiguous_external_calls(
                        paths["external_calls"],
                        action=args.resolve_ambiguous,
                    )
        if not args.dry_run and _segment_complete(paths):
            if manifest is None:
                raise RuntimeError("Segment manifest was not initialized before projection.")
            summary, manifest = _project_segment_from_ledger(
                paths=paths,
                manifest=manifest,
                item=item,
                stream_reuse_cached_page_count=segment_reuse_cached_page_count,
                stream_fresh_cached_page_count=segment_fresh_cached_page_count,
                recipe_seed=segment_seed,
                base_summary=_segment_summary_base(paths),
            )
            segment_summaries.append(summary)
            remaining_reuse_cached_page_count = _decrement_recipe_budget(
                remaining_reuse_cached_page_count,
                int(summary.get("stream_reused_cached_page_count", 0) or 0),
            )
            remaining_fresh_cached_page_count = _decrement_recipe_budget(
                remaining_fresh_cached_page_count,
                int(summary.get("stream_fresh_processed_page_count", 0) or 0),
            )
            continue
        if args.dry_run:
            print(" ".join(command))
            remaining_reuse_cached_page_count = _decrement_recipe_budget(
                remaining_reuse_cached_page_count,
                stream_budget_numeric_count(segment_reuse_cached_page_count),
            )
            remaining_fresh_cached_page_count = _decrement_recipe_budget(
                remaining_fresh_cached_page_count,
                stream_budget_numeric_count(segment_fresh_cached_page_count),
            )
            continue
        subprocess.run(command, cwd=ROOT, check=True)
        worker_summary = json.loads(paths["summary"].read_text(encoding="utf-8"))
        if manifest is None:
            raise RuntimeError("Segment manifest was not initialized before execution.")
        summary, manifest = _project_segment_from_ledger(
            paths=paths,
            manifest=manifest,
            item=item,
            stream_reuse_cached_page_count=segment_reuse_cached_page_count,
            stream_fresh_cached_page_count=segment_fresh_cached_page_count,
            recipe_seed=segment_seed,
            base_summary=worker_summary,
        )
        if manifest["status"] != "complete":
            if not manifest.get("blocking_reasons"):
                ledger = manifest.get("ledger_summary", {})
                raise RuntimeError(
                    "Recipe segment stopped before its allocation target was terminal: "
                    f"{manifest.get('segment_id', '')} "
                    f"primary_pages={ledger.get('primary_pages', 0)} "
                    f"terminal_pages={ledger.get('terminal_pages', 0)}"
                )
            print_json_summary(_recipe_status_payload(run_id, segment_dir))
            return 2
        segment_summaries.append(summary)
        remaining_reuse_cached_page_count = _decrement_recipe_budget(
            remaining_reuse_cached_page_count,
            int(summary.get("stream_reused_cached_page_count", 0) or 0),
        )
        remaining_fresh_cached_page_count = _decrement_recipe_budget(
            remaining_fresh_cached_page_count,
            int(summary.get("stream_fresh_processed_page_count", 0) or 0),
        )
    if args.dry_run:
        return 0

    accepted_id_offset = 0
    if append_label:
        existing_accepted_records, _ = load_endpoint_jsonl(output, label="accepted")
        accepted_id_offset = len(existing_accepted_records)
    accepted_records, rejected_records = _combine_segment_records(
        run_id=run_id,
        segment_summaries=segment_summaries,
        accepted_id_offset=accepted_id_offset,
    )
    if append_label:
        append_jsonl(output, accepted_records)
        append_jsonl(rejected_output, rejected_records)
    else:
        write_jsonl(output, accepted_records)
        write_jsonl(rejected_output, rejected_records)

    summary = _recipe_summary(
        args=args,
        run_id=run_id,
        recipe_items=recipe_items,
        reasoning_types=reasoning_types,
        table_filter_modes=table_filter_modes,
        table_source_types=table_source_types,
        segment_summaries=segment_summaries,
        accepted_records=accepted_records,
        rejected_records=rejected_records,
        output=output,
        rejected_output=rejected_output,
        summary_output=summary_output,
        walkthrough_output=walkthrough_output,
        stream_state_base=stream_state_base,
        append_label=append_label,
        wall_clock_seconds=round(perf_counter() - run_started, 4),
    )
    summary_output.parent.mkdir(parents=True, exist_ok=True)
    summary_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_stream_walkthrough(
        path=walkthrough_output,
        summary=summary,
        accepted_records=accepted_records,
        rejected_records=rejected_records,
        rerun_records=[],
        existing_accepted_records=[],
        existing_rejected_records=[],
    )
    print_json_summary(summary)
    return 0



def _recipe_segment_budget(budget: int | str, target_count: int) -> int | str:
    """Return the segment-local budget for one recipe item."""
    if isinstance(budget, str):
        return budget
    return min(max(0, int(budget)), max(0, int(target_count)))


def _decrement_recipe_budget(budget: int | str, used_count: int) -> int | str:
    """Subtract actual or planned segment use from a recipe-level numeric budget."""
    if isinstance(budget, str):
        return budget
    return max(0, int(budget) - max(0, int(used_count)))


def _attach_recipe_segment_budget_summary(
    summary: dict,
    *,
    item: RecipeItem,
    stream_reuse_cached_page_count: int | str,
    stream_fresh_cached_page_count: int | str,
) -> None:
    """Attach recipe target and segment budget metadata to one segment summary."""
    target_count = int(item.record_limit)
    actual_reused = int(summary.get("stream_reused_cached_page_count", 0) or 0)
    resolved_fresh_budget = int(summary.get("stream_fresh_cached_page_count", 0) or 0)
    expected_page_count = min(target_count, actual_reused + resolved_fresh_budget)
    summary["recipe_answer_type"] = item.answer_type
    summary["recipe_target_count"] = target_count
    summary["recipe_record_limit"] = target_count
    summary["recipe_record_limit_deprecated_alias"] = True
    summary["recipe_segment_reuse_cached_page_count"] = stream_reuse_cached_page_count
    summary["recipe_segment_fresh_cached_page_count"] = stream_fresh_cached_page_count
    summary["recipe_segment_expected_page_count"] = expected_page_count

def _parse_recipe(args: argparse.Namespace) -> tuple[list[RecipeItem], list[str]]:
    """Build one formal segment and enforce answer-type/mode combinations."""
    if args.page_attempt_count is None or args.answer_type is None:
        raise ValueError("--page-attempt-count and --answer-type are required unless --status is used.")
    page_attempt_count = int(args.page_attempt_count)
    if page_attempt_count < 1:
        raise ValueError("--page-attempt-count must be positive.")
    answer_type = _normalize_recipe_answer_types([args.answer_type])[0]
    answer_type_mode = normalize_route3_answer_type_mode(args.route3_answer_type_mode)
    if answer_type == ALL_TYPES_RECIPE_ANSWER_TYPE and answer_type_mode != "all5":
        raise ValueError("AllTypes requires --route3-answer-type-mode all5.")
    if answer_type != ALL_TYPES_RECIPE_ANSWER_TYPE and answer_type_mode != "single":
        raise ValueError("A specific answer type requires --route3-answer-type-mode single.")
    reasoning_types = list(DEFAULT_ROUTE3_REASONING_TYPES)
    return [RecipeItem(answer_type=answer_type, record_limit=page_attempt_count)], reasoning_types


def _normalize_recipe_answer_types(values: list[str]) -> list[str]:
    """Return normalized recipe answer types, including the AllTypes pseudo segment."""
    normalized_values: list[str] = []
    seen: set[str] = set()
    normal_parts: list[str] = []
    for raw_value in values:
        for part in str(raw_value or "").split(","):
            text = part.strip()
            if not text:
                continue
            if _is_all_types_recipe_answer_type(text):
                if ALL_TYPES_RECIPE_ANSWER_TYPE not in seen:
                    normalized_values.append(ALL_TYPES_RECIPE_ANSWER_TYPE)
                    seen.add(ALL_TYPES_RECIPE_ANSWER_TYPE)
                continue
            normal_parts.append(text)
    for answer_type in normalize_route3_answer_types(normal_parts):
        if answer_type not in seen:
            normalized_values.append(answer_type)
            seen.add(answer_type)
    return normalized_values


def _is_all_types_recipe_answer_type(value: str) -> bool:
    """Return whether a recipe token means the all5 answer-type mode segment."""
    normalized = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    return normalized in {"alltypes", "all_types", "all5", "all_5", "all"}


def _recipe_run_id(args: argparse.Namespace, recipe_items: list[RecipeItem], reasoning_types: list[str]) -> str:
    """Return a path-safe run ID for this recipe."""
    if args.run_id.strip():
        return safe_artifact_id(args.run_id, fallback="route3_recipe")
    count_text = "_".join(f"{item.record_limit}{item.answer_type.lower()}" for item in recipe_items)
    reasoning_text = "_".join(reasoning_types or ["single_fact"])
    return safe_artifact_id(
        f"wikipedia_stream_recipe_{count_text}_{reasoning_text}_{date.today().isoformat().replace('-', '_')}",
        fallback="route3_recipe",
    )


def _validate_lifecycle_args(args: argparse.Namespace) -> None:
    """Validate the recipe lifecycle mode before reading or writing artifacts."""
    if args.status:
        if not str(args.run_id or "").strip():
            raise ValueError("--status requires --run-id.")
        if args.resume or args.append_to_existing_run or args.resolve_ambiguous:
            raise ValueError("--status cannot be combined with resume, top-up, or ambiguous resolution.")
    if args.resolve_ambiguous and not args.resume:
        raise ValueError("--resolve-ambiguous requires --resume.")
    if args.resolve_ambiguous and args.append_to_existing_run:
        raise ValueError("--resolve-ambiguous is not valid for a top-up segment.")
    if args.append_run_label and not args.append_to_existing_run:
        raise ValueError("--append-run-label requires --append-to-existing-run.")


def _recipe_append_label(args: argparse.Namespace) -> str:
    """Return the segment suffix for recipe append/top-up mode."""
    if not getattr(args, "append_to_existing_run", False):
        return ""
    raw_label = str(getattr(args, "append_run_label", "") or "").strip()
    if not raw_label:
        raw_label = "append_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return safe_artifact_id(raw_label, fallback="append")


def _base_segment_id(item: RecipeItem, index: int) -> str:
    """Return the unsuffixed deterministic segment ID for one recipe item."""
    return f"{index + 1:02d}_{item.answer_type.lower()}_{item.record_limit}"


def _base_segment_id_for_run(
    *,
    segment_dir: Path,
    item: RecipeItem,
    index: int,
    append_label: str,
) -> str:
    """Return the original manifest-backed segment ID for a top-up."""
    default_id = _base_segment_id(item, index)
    if not append_label:
        return default_id
    answer_type = re.escape(item.answer_type.lower())
    base_pattern = re.compile(rf"^\d+_{answer_type}_\d+$")
    candidates: set[str] = set()
    for manifest_path in segment_dir.glob("*/segment_manifest.json"):
        manifest = load_segment_manifest(manifest_path)
        if manifest is None:
            continue
        segment_id = str(manifest.get("segment_id", ""))
        if base_pattern.fullmatch(segment_id):
            candidates.add(segment_id)
    if not candidates:
        raise ValueError(
            f"Top-up requires an original {item.answer_type} segment manifest in {segment_dir}"
        )
    return sorted(candidates, key=lambda value: (value.split("_")[0], value))[0]


def _append_segment_id(base_segment_id: str, append_label: str) -> str:
    """Return the segment ID with an optional append suffix."""
    return f"{base_segment_id}_{append_label}" if append_label else base_segment_id


def _segment_stream_state(stream_state_base: Path, *, segment_dir: Path, segment_id: str) -> Path:
    """Return the isolated stream-state path for one recipe segment."""
    base = Path(stream_state_base)
    if base.name == "stream_state.json":
        return segment_dir / f"{segment_id}_state.json"
    suffix = base.suffix or ".json"
    return base.with_name(f"{base.stem}_{segment_id}{suffix}")


def _recipe_segment_seed(
    *,
    args: argparse.Namespace,
    run_id: str,
    segment_id: str,
    answer_type: str,
    index: int,
) -> int:
    """Return the deterministic recipe-level seed shared by every segment."""
    if args.stream_random_seed is not None:
        return int(args.stream_random_seed)
    seed_args = argparse.Namespace(
        stream_random_seed=None,
        run_group_id=run_id,
        run_segment_id="recipe",
        summary_output=f"{run_id}:recipe",
        stream_state=f"{run_id}:recipe",
        start_from_endpoint=False,
    )
    return effective_stream_random_seed(seed_args)


def _require_clean_worktree() -> None:
    """Require a clean Git worktree for a formal network run."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    if result.stdout.strip():
        raise RuntimeError("Formal Route 3 runs require a clean Git worktree.")


EXCLUDED_PAGE_IDS_FILENAME = "excluded_page_ids.json"


def _read_external_page_exclusion(path: Path) -> dict:
    """Read and verify one frozen page-ID exclusion snapshot."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    page_ids = sorted({int(page_id) for page_id in payload["page_ids"]})
    page_ids_sha256 = canonical_json_sha256(page_ids)
    if len(page_ids) != int(payload["page_id_count"]):
        raise ValueError(f"External page exclusion count mismatch: {path}")
    if page_ids_sha256 != str(payload["page_ids_sha256"]):
        raise ValueError(f"External page exclusion hash mismatch: {path}")
    return {
        "schema_version": 1,
        "source_run_id": str(payload["source_run_id"]),
        "page_id_count": len(page_ids),
        "page_ids_sha256": page_ids_sha256,
        "page_ids": page_ids,
    }


def _create_or_load_external_page_exclusion(
    *,
    segment_root: Path,
    exclude_run_id: str,
) -> dict:
    """Freeze one older run's canonical allocation IDs for this segment."""
    source_run_id = safe_artifact_id(exclude_run_id, fallback="excluded_run")
    snapshot_path = segment_root / EXCLUDED_PAGE_IDS_FILENAME
    if snapshot_path.exists():
        snapshot = _read_external_page_exclusion(snapshot_path)
        if snapshot["source_run_id"] != source_run_id:
            raise ValueError(f"External page exclusion source mismatch: {snapshot_path}")
        return snapshot

    source_root = ROOT / "outputs" / "recipe_segments" / source_run_id
    allocation_paths = sorted(source_root.glob("*/page_allocations/a*_p*.json"))
    if not allocation_paths:
        raise FileNotFoundError(f"No page allocations found for excluded run: {source_run_id}")
    page_ids = sorted(
        {
            int(json.loads(path.read_text(encoding="utf-8"))["canonical_page_id"])
            for path in allocation_paths
        }
    )
    snapshot = {
        "schema_version": 1,
        "source_run_id": source_run_id,
        "page_id_count": len(page_ids),
        "page_ids_sha256": canonical_json_sha256(page_ids),
        "page_ids": page_ids,
    }
    atomic_write_json(snapshot_path, snapshot)
    return snapshot


def _external_page_exclusion_summary(
    ledger_index: SegmentLedgerIndex,
    snapshot: dict,
) -> dict:
    """Return exclusion audit fields and reject canonical page overlap."""
    external_excluded_page_ids = set(snapshot["page_ids"])
    collisions = ledger_index.primary_page_ids & external_excluded_page_ids
    if collisions:
        raise RuntimeError("external page exclusion violated")
    return {
        "external_excluded_page_count": snapshot["page_id_count"],
        "external_excluded_page_ids_sha256": snapshot["page_ids_sha256"],
        "external_exclusion_collision_count": len(collisions),
    }


@contextmanager
def _exclusive_writer_lock(lock_path: Path, unavailable_message: str):
    """Hold one non-blocking exclusive OS lock."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = lock_path.open("a+b")
    handle.seek(0, 2)
    if handle.tell() == 0:
        handle.write(b"\0")
        handle.flush()
    handle.seek(0)
    try:
        if sys.platform == "win32":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as exc:
        handle.close()
        raise RuntimeError(unavailable_message) from exc
    try:
        yield
    finally:
        handle.close()


@contextmanager
def _recipe_group_lock(segment_dir: Path):
    """Hold the non-blocking writer lock for one recipe run group."""
    with _exclusive_writer_lock(
        segment_dir / ".recipe_group.lock",
        f"Run group already has an active recipe writer: {segment_dir}",
    ):
        yield


@contextmanager
def _segment_writer_lock(segment_root: Path):
    """Hold one non-blocking OS lock for the segment writer lifetime."""
    with _exclusive_writer_lock(
        segment_root / ".recipe_writer.lock",
        f"Segment already has an active recipe writer: {segment_root}",
    ):
        yield


def _git_sha() -> str:
    """Return the current Git commit SHA."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _generation_prompt_hash() -> str:
    """Hash the exact source of the formal Route 3 prompt builders."""
    sources = [
        inspect.getsource(build_wikipedia_infobox_prompt),
        inspect.getsource(build_route3_infobox_prompt),
        inspect.getsource(build_route3_wikitable_prompt),
    ]
    return build_segment_fingerprint({"prompt_sources": sources})["sha256"]


def _segment_fingerprint(
    *,
    args: argparse.Namespace,
    item: RecipeItem,
    run_id: str,
    segment_id: str,
    stream_random_seed: int,
    table_source_types: list[str],
    stream_reuse_cached_page_count: int | str,
    stream_fresh_cached_page_count: int | str,
    external_page_exclusion: dict | None = None,
) -> dict:
    """Build the complete resolved fingerprint for one formal segment."""
    resolved_config = {
        "run_date": args.run_date,
        "cutoff_year": args.cutoff_year,
        "timeout_seconds": args.timeout_seconds,
        "proxy": args.proxy,
        "generation_provider": args.small_model_provider,
        "generation_base_url": args.small_model_base_url,
        "generation_api_key_env": args.small_model_api_key_env,
        "generated_search_query_count": args.generated_search_query_count,
        "stream_search_limit": args.stream_search_limit,
        "stream_search_max_rounds": args.stream_search_max_rounds,
        "stream_discovery_max_retries": args.stream_discovery_max_retries,
        "stream_discovery_retry_backoff_seconds": args.stream_discovery_retry_backoff_seconds,
        "stream_discovery_retry_max_sleep_seconds": args.stream_discovery_retry_max_sleep_seconds,
        "wikipedia_429_backoff_seconds": args.wikipedia_429_backoff_seconds,
        "wikipedia_429_max_backoff_seconds": args.wikipedia_429_max_backoff_seconds,
        "wikipedia_429_recovery_seconds": args.wikipedia_429_recovery_seconds,
        "stream_batch_size": args.stream_batch_size,
        "stream_page_workers": args.stream_page_workers,
        "wikipedia_concurrency_limit": args.wikipedia_concurrency_limit,
        "duckduckgo_concurrency_limit": args.duckduckgo_concurrency_limit,
        "openrouter_generation_rewrite_concurrency_limit": args.openrouter_generation_rewrite_concurrency_limit,
        "second_stage_concurrency_limit": args.second_stage_concurrency_limit,
    }
    return build_segment_fingerprint(
        {
            "git_sha": _git_sha(),
            "prompt_hash": _generation_prompt_hash(),
            "run_group_id": run_id,
            "segment_id": segment_id,
            "resolved_result_affecting_config": resolved_config,
            "generation": {
                "model": args.generation_model,
                "max_tokens": args.small_model_max_tokens,
            },
            "answer_mode": {
                "answer_type": item.answer_type,
                "answer_type_mode": "all5" if item.answer_type == ALL_TYPES_RECIPE_ANSWER_TYPE else args.route3_answer_type_mode,
            },
            "source_mode": list(table_source_types),
            "page_attempt_count": item.record_limit,
            **(
                {
                    "external_page_exclusion": {
                        "source_run_id": external_page_exclusion["source_run_id"],
                        "page_id_count": external_page_exclusion["page_id_count"],
                        "page_ids_sha256": external_page_exclusion["page_ids_sha256"],
                    }
                }
                if external_page_exclusion is not None
                else {}
            ),
            "seed": stream_random_seed,
            "cache_policy": {
                "reuse_cached_page_count": stream_reuse_cached_page_count,
                "fresh_cached_page_count": stream_fresh_cached_page_count,
                "page_archive_dir": str(args.route3_page_archive_dir),
            },
            "table_ranking_and_filters": {
                "filter_modes": list(DEFAULT_ROUTE3_TABLE_FILTER_MODES),
                "prose_leakage_scoring": True,
                "minimum_table_score": 0.0,
                "infobox_max_removed_row_rate": args.route3_infobox_max_removed_row_rate,
                "infobox_min_remaining_rows": args.route3_infobox_min_remaining_rows,
            },
            "duckduckgo": {
                "top_k": args.duckduckgo_top_k,
                "parallel_queries": args.duckduckgo_parallel_queries,
                "max_full_question_hit_rate": args.search_longtail_max_full_question_hit_rate,
                "max_keyword_hit_rate": args.search_longtail_max_keyword_hit_rate,
                "max_overall_hit_rate": args.search_longtail_max_overall_hit_rate,
                **duckduckgo_settings_kwargs(args),
            },
            "second_stage": {
                "enabled": args.enable_second_stage_grading,
                "accuracy_threshold": args.second_stage_grading_accuracy_threshold,
                "answer_models": ["openai/gpt-4.1-mini", "google/gemini-3-flash-preview"],
                "grader_model": "openai/gpt-4.1-mini",
            },
        }
    )


def _generation_protocol_compatibility_fingerprint(fingerprint: dict) -> dict:
    """Build the protocol fingerprint shared by initial and top-up segments."""
    inputs = dict(fingerprint.get("inputs", {}))
    inputs.pop("segment_id", None)
    inputs.pop("page_attempt_count", None)
    cache_policy = dict(inputs.get("cache_policy", {}))
    cache_policy.pop("reuse_cached_page_count", None)
    cache_policy.pop("fresh_cached_page_count", None)
    inputs["cache_policy"] = cache_policy
    return build_segment_fingerprint(inputs)


def _require_top_up_prerequisites(
    *,
    segment_dir: Path,
    run_group_id: str,
    base_segment_id: str,
    current_segment_id: str,
    requested_fingerprint: dict,
) -> None:
    """Require complete prior segments and a matching generation protocol."""
    prior_manifests: dict[str, tuple[Path, dict]] = {}
    for manifest_path in sorted(segment_dir.glob("*/segment_manifest.json")):
        manifest = load_segment_manifest(manifest_path)
        if manifest is None:
            continue
        segment_id = str(manifest.get("segment_id", ""))
        if segment_id == current_segment_id:
            continue
        if str(manifest.get("run_group_id", "")) != run_group_id:
            raise ValueError(f"Unexpected run group in {manifest_path}")
        index = SegmentLedgerIndex(
            allocation_dir=manifest_path.parent / "page_allocations",
            attempt_dir=manifest_path.parent / "page_attempts",
            run_group_id=run_group_id,
            segment_id=segment_id,
            run_group_segments_dir=segment_dir,
        )
        derived = derive_segment_manifest_state(manifest, index)
        if manifest.get("status") != "complete" or derived.get("status") != "complete":
            raise ValueError(f"Top-up requires complete prior segment: {segment_id}")
        prior_manifests[segment_id] = (manifest_path, manifest)
    if base_segment_id not in prior_manifests:
        raise ValueError(f"Top-up base segment is not complete: {base_segment_id}")
    base_path, base_manifest = prior_manifests[base_segment_id]
    base_fingerprint = base_manifest.get("fingerprint", {})
    existing_protocol = _generation_protocol_compatibility_fingerprint(base_fingerprint)
    requested_protocol = _generation_protocol_compatibility_fingerprint(requested_fingerprint)
    if existing_protocol["sha256"] != requested_protocol["sha256"]:
        raise ValueError(
            "Top-up generation protocol fingerprint mismatch for "
            f"{base_path}: existing={existing_protocol['sha256']} "
            f"requested={requested_protocol['sha256']}"
        )


def _segment_stream_search_initial_offset(
    recipe_items: list[RecipeItem],
    index: int,
    stream_search_limit: int,
) -> int:
    """Return a disjoint table-search starting offset for one recipe segment."""
    search_limit = max(1, int(stream_search_limit))
    offset = 0
    for item in recipe_items[:index]:
        chunks = max(1, (int(item.record_limit) + search_limit - 1) // search_limit)
        offset += chunks * search_limit
    return offset


def _summary_page_ids(summary: dict) -> set[int]:
    """Return attempted page IDs recorded by one segment summary."""
    page_ids: set[int] = set()
    for raw_page_id in summary.get("page_ids", []):
        try:
            page_id = int(raw_page_id)
        except (TypeError, ValueError):
            continue
        if page_id > 0:
            page_ids.add(page_id)
    return page_ids


def _summary_page_id_entries(summary: dict) -> set[PageIdListEntry]:
    """Return page-ID entries represented by one segment summary."""
    raw_entries = summary.get("page_id_list_entries", [])
    if raw_entries:
        return {
            entry
            for entry in read_page_id_entries_from_summary_payload(raw_entries)
            if entry.page_id > 0
        }
    answer_types = _summary_answer_types(summary)
    table_types = _summary_table_types(summary)
    return build_page_id_entries(_summary_page_ids(summary), answer_types=answer_types, table_types=table_types)


def read_page_id_entries_from_summary_payload(payload: object) -> set[PageIdListEntry]:
    """Read page-ID entries from a summary field payload."""
    return extract_page_id_entries_from_payload(payload)


def _summary_answer_types(summary: dict) -> list[str]:
    values = summary.get("route3_answer_types", [])
    if isinstance(values, list) and values:
        return [str(value) for value in values if str(value or "").strip()]
    recipe_answer_type = str(summary.get("recipe_answer_type", "") or "").strip()
    if recipe_answer_type and recipe_answer_type != ALL_TYPES_RECIPE_ANSWER_TYPE:
        return [recipe_answer_type]
    if recipe_answer_type == ALL_TYPES_RECIPE_ANSWER_TYPE:
        return list(ROUTE3_ANSWER_TYPES)
    return [str(value) for value in ROUTE3_ANSWER_TYPES]


def _summary_table_types(summary: dict) -> list[str]:
    values = summary.get("route3_table_source_types", [])
    if isinstance(values, list) and values:
        return [str(value) for value in values if str(value or "").strip()]
    return list(DEFAULT_ROUTE3_TABLE_SOURCE_TYPES)


def _segment_command(
    *,
    args: argparse.Namespace,
    item: RecipeItem,
    index: int,
    run_id: str,
    segment_dir: Path,
    stream_state_base: Path,
    stream_search_initial_offset: int,
    table_source_types: list[str] | None = None,
    append_label: str = "",
    base_segment_id: str | None = None,
    stream_reuse_cached_page_count: int | str | None = None,
    stream_fresh_cached_page_count: int | str | None = None,
    excluded_page_ids_file: Path | None = None,
) -> tuple[list[str], dict[str, Path]]:
    """Build the pipeline subprocess command for one recipe segment."""
    normalized_table_source_types = list(
        normalize_route3_table_source_types(table_source_types or DEFAULT_ROUTE3_TABLE_SOURCE_TYPES)
    )
    segment_id = _append_segment_id(base_segment_id or _base_segment_id(item, index), append_label)
    segment_root = segment_dir / segment_id
    segment_manifest = segment_root / "segment_manifest.json"
    page_allocation_ledger_dir = segment_root / "page_allocations"
    page_attempt_ledger_dir = segment_root / "page_attempts"
    external_call_record_dir = segment_root / "external_calls"
    ddg_verifier_result_dir = segment_root / "ddg_verifier_results"
    ambiguous_json = segment_root / "ambiguous_external_calls.json"
    ambiguous_markdown = segment_root / "ambiguous_external_calls.md"
    accepted = segment_dir / f"{segment_id}_accepted.jsonl"
    rejected = segment_dir / f"{segment_id}_rejected.jsonl"
    summary = segment_dir / f"{segment_id}_summary.json"
    stream_state = _segment_stream_state(stream_state_base, segment_dir=segment_dir, segment_id=segment_id)
    stream_random_seed = _recipe_segment_seed(
        args=args,
        run_id=run_id,
        segment_id=segment_id,
        answer_type=item.answer_type,
        index=index,
    )
    segment_answer_type_mode = (
        "all5" if item.answer_type == ALL_TYPES_RECIPE_ANSWER_TYPE else args.route3_answer_type_mode
    )
    effective_reuse_cached_page_count = (
        getattr(args, "stream_reuse_cached_page_count", "all")
        if stream_reuse_cached_page_count is None
        else stream_reuse_cached_page_count
    )
    effective_fresh_cached_page_count = (
        getattr(args, "stream_fresh_cached_page_count", "fill")
        if stream_fresh_cached_page_count is None
        else stream_fresh_cached_page_count
    )
    command = [
        sys.executable,
        str(ROOT / "scripts" / "run_wikipedia_infobox_pipeline.py"),
        "--stream-page-processing-target",
        str(item.record_limit),
        "--route3-answer-type-mode",
        segment_answer_type_mode,
        "--run-group-id",
        run_id,
        "--run-segment-id",
        segment_id,
        "--stream-state",
        str(stream_state),
        "--output",
        str(accepted),
        "--rejected-output",
        str(rejected),
        "--summary-output",
        str(summary),
        "--page-allocation-ledger-dir",
        str(page_allocation_ledger_dir),
        "--page-attempt-ledger-dir",
        str(page_attempt_ledger_dir),
        "--run-group-segments-dir",
        str(segment_dir),
        "--external-call-record-dir",
        str(external_call_record_dir),
        "--ddg-verifier-result-dir",
        str(ddg_verifier_result_dir),
        "--cutoff-year",
        str(args.cutoff_year),
        "--timeout-seconds",
        str(args.timeout_seconds),
        "--proxy",
        str(args.proxy),
        "--small-model-provider",
        str(args.small_model_provider),
        "--generation-model",
        str(args.generation_model),
        "--small-model-api-key-env",
        str(args.small_model_api_key_env),
        "--small-model-base-url",
        str(args.small_model_base_url),
        "--small-model-max-tokens",
        str(args.small_model_max_tokens),
        "--duckduckgo-top-k",
        str(args.duckduckgo_top_k),
        "--duckduckgo-parallel-queries",
        str(args.duckduckgo_parallel_queries),
        "--duckduckgo-ddgs-backend",
        str(args.duckduckgo_ddgs_backend),
        "--duckduckgo-ddgs-max-attempts",
        str(args.duckduckgo_ddgs_max_attempts),
        "--duckduckgo-cooldown-failure-threshold",
        str(args.duckduckgo_cooldown_failure_threshold),
        "--duckduckgo-cooldown-initial-seconds",
        str(args.duckduckgo_cooldown_initial_seconds),
        "--duckduckgo-cooldown-max-seconds",
        str(args.duckduckgo_cooldown_max_seconds),
        "--generated-search-query-count",
        str(args.generated_search_query_count),
        "--search-longtail-max-full-question-hit-rate",
        str(args.search_longtail_max_full_question_hit_rate),
        "--search-longtail-max-keyword-hit-rate",
        str(args.search_longtail_max_keyword_hit_rate),
        "--search-longtail-max-overall-hit-rate",
        str(args.search_longtail_max_overall_hit_rate),
        "--stream-search-limit",
        str(args.stream_search_limit),
        "--stream-search-max-rounds",
        str(args.stream_search_max_rounds),
        "--stream-discovery-max-retries",
        str(args.stream_discovery_max_retries),
        "--stream-discovery-retry-backoff-seconds",
        str(args.stream_discovery_retry_backoff_seconds),
        "--stream-discovery-retry-max-sleep-seconds",
        str(args.stream_discovery_retry_max_sleep_seconds),
        "--stream-reuse-cached-page-count",
        str(effective_reuse_cached_page_count),
        "--stream-fresh-cached-page-count",
        str(effective_fresh_cached_page_count),
        "--wikipedia-429-backoff-seconds",
        str(args.wikipedia_429_backoff_seconds),
        "--wikipedia-429-max-backoff-seconds",
        str(args.wikipedia_429_max_backoff_seconds),
        "--wikipedia-429-recovery-seconds",
        str(args.wikipedia_429_recovery_seconds),
        "--stream-search-initial-offset",
        str(max(0, int(stream_search_initial_offset))),
        "--stream-random-seed",
        str(stream_random_seed),
        "--stream-batch-size",
        str(args.stream_batch_size),
        "--stream-page-workers",
        str(args.stream_page_workers),
        "--wikipedia-concurrency-limit",
        str(args.wikipedia_concurrency_limit),
        "--duckduckgo-concurrency-limit",
        str(args.duckduckgo_concurrency_limit),
        "--openrouter-generation-rewrite-concurrency-limit",
        str(args.openrouter_generation_rewrite_concurrency_limit),
        "--second-stage-concurrency-limit",
        str(args.second_stage_concurrency_limit),
        "--route3-page-archive-dir",
        str(args.route3_page_archive_dir),
        "--route3-infobox-max-removed-row-rate",
        str(args.route3_infobox_max_removed_row_rate),
        "--route3-infobox-min-remaining-rows",
        str(args.route3_infobox_min_remaining_rows),
    ]
    if excluded_page_ids_file is not None:
        command.extend(["--excluded-page-ids-file", str(excluded_page_ids_file)])
    for fallback in args.duckduckgo_disable_fallback:
        command.extend(["--duckduckgo-disable-fallback", str(fallback)])
    command.append("--duckduckgo-prefer-ddgs" if args.duckduckgo_prefer_ddgs else "--no-duckduckgo-prefer-ddgs")
    command.append("--duckduckgo-cooldown" if args.duckduckgo_cooldown else "--no-duckduckgo-cooldown")
    if item.answer_type != ALL_TYPES_RECIPE_ANSWER_TYPE:
        command.extend(["--route3-answer-type", item.answer_type])
    if args.run_date:
        command.extend(["--run-date", str(args.run_date)])
    for source_type in normalized_table_source_types:
        command.extend(["--route3-table-source-type", source_type])
    if args.enable_second_stage_grading:
        command.extend(
            [
                "--enable-second-stage-grading",
                "--second-stage-grading-accuracy-threshold",
                str(args.second_stage_grading_accuracy_threshold),
            ]
        )
    if args.big_batch_mode:
        command.append("--big-batch-mode")
    if not segment_manifest.exists():
        command.append("--reset-stream-state")
    return command, {
        "accepted": accepted,
        "rejected": rejected,
        "summary": summary,
        "stream_state": stream_state,
        "segment_root": segment_root,
        "manifest": segment_manifest,
        "allocations": page_allocation_ledger_dir,
        "ledger": page_attempt_ledger_dir,
        "segments_dir": segment_dir,
        "external_calls": external_call_record_dir,
        "ddg_results": ddg_verifier_result_dir,
        "ambiguous_json": ambiguous_json,
        "ambiguous_markdown": ambiguous_markdown,
        "excluded_page_ids": excluded_page_ids_file or segment_root / EXCLUDED_PAGE_IDS_FILENAME,
    }


def _segment_ledger_index(paths: dict[str, Path]) -> SegmentLedgerIndex:
    """Build one index for a segment boundary or recovery operation."""
    manifest = load_segment_manifest(paths["manifest"])
    if manifest is None:
        raise ValueError(f"Missing segment manifest: {paths['manifest']}")
    return SegmentLedgerIndex(
        allocation_dir=paths["allocations"],
        attempt_dir=paths["ledger"],
        run_group_id=str(manifest.get("run_group_id", "")),
        segment_id=str(manifest.get("segment_id", "")),
        run_group_segments_dir=paths["segments_dir"],
    )


def _recipe_status_payload(run_id: str, segment_dir: Path) -> dict:
    """Return read-only ledger-derived status for every segment in one run group."""
    segments: list[dict] = []
    for manifest_path in sorted(segment_dir.glob("*/segment_manifest.json")):
        manifest = load_segment_manifest(manifest_path)
        if manifest is None:
            continue
        if str(manifest.get("run_group_id", "")) != run_id:
            raise ValueError(f"Unexpected run group in {manifest_path}")
        segment_id = str(manifest.get("segment_id", ""))
        index = SegmentLedgerIndex(
            allocation_dir=manifest_path.parent / "page_allocations",
            attempt_dir=manifest_path.parent / "page_attempts",
            run_group_id=run_id,
            segment_id=segment_id,
            run_group_segments_dir=segment_dir,
        )
        derived = derive_segment_manifest_state(manifest, index)
        segments.append(
            {
                "segment_id": segment_id,
                "status": derived["status"],
                "manifest_status": manifest.get("status", "incomplete"),
                "blocking_reasons": list(manifest.get("blocking_reasons", [])),
                "ledger": ledger_summary(index),
                "manifest": str(manifest_path),
            }
        )
    overall_status = "missing"
    if segments:
        overall_status = (
            "complete"
            if all(
                row["status"] == "complete" and not row["blocking_reasons"]
                for row in segments
            )
            else "incomplete"
        )
    return {
        "run_group_id": run_id,
        "status": overall_status,
        "segment_dir": str(segment_dir),
        "segments": segments,
    }


def _open_circuit_states(summary: dict) -> list[dict[str, str]]:
    """Return manifest blocking records for invocation circuits that opened."""
    circuits = summary.get("service_circuits", {})
    if not isinstance(circuits, dict):
        return []
    return [
        {
            "state": "blocked_external_service",
            "service": str(service),
            "reason": str(snapshot.get("open_reason", "")),
        }
        for service, snapshot in sorted(circuits.items())
        if isinstance(snapshot, dict) and bool(snapshot.get("open", False))
    ]


def _project_segment_from_ledger(
    *,
    paths: dict[str, Path],
    manifest: dict,
    item: RecipeItem,
    stream_reuse_cached_page_count: int | str,
    stream_fresh_cached_page_count: int | str,
    recipe_seed: int,
    base_summary: dict,
) -> tuple[dict, dict]:
    """Rebuild segment projections and manifest state from durable records."""
    segment_ledger = _segment_ledger_index(paths)
    accepted_records, _rejected_records, _retry_pending_records = rebuild_derived_outputs(
        segment_ledger,
        accepted_path=paths["accepted"],
        rejected_path=paths["rejected"],
    )
    summary = rebuild_summary_from_ledger(
        paths["summary"],
        segment_ledger,
        base_summary=base_summary,
    )
    exclusion_path = paths.get("excluded_page_ids")
    if exclusion_path is not None and exclusion_path.exists():
        external_page_exclusion = _read_external_page_exclusion(exclusion_path)
        summary.update(_external_page_exclusion_summary(segment_ledger, external_page_exclusion))

    _attach_recipe_segment_budget_summary(
        summary,
        item=item,
        stream_reuse_cached_page_count=stream_reuse_cached_page_count,
        stream_fresh_cached_page_count=stream_fresh_cached_page_count,
    )
    ambiguous_rows = write_ambiguous_external_call_reports(
        paths["external_calls"],
        json_path=paths["ambiguous_json"],
        markdown_path=paths["ambiguous_markdown"],
    )
    external_states = [*ambiguous_rows, *_open_circuit_states(summary)]
    summary["ambiguous_external_calls"] = {
        "count": len(ambiguous_rows),
        "json": str(paths["ambiguous_json"]),
        "markdown": str(paths["ambiguous_markdown"]),
    }
    manifest = update_segment_manifest(
        paths["manifest"],
        manifest,
        segment_state=derive_segment_manifest_state(
            manifest,
            segment_ledger,
            external_states,
        ),
        ledger_summary=ledger_summary(segment_ledger),
        pre_review_quantity_prediction=predict_pre_review_quantities(
            accepted_records,
            recipe_seed=recipe_seed,
        ),
        service_circuits=dict(summary.get("service_circuits", {})),
    )
    summary["segment_accepted_output"] = str(paths["accepted"])
    summary["segment_rejected_output"] = str(paths["rejected"])
    atomic_write_json(paths["summary"], summary)
    return summary, manifest


def _segment_complete(paths: dict[str, Path]) -> bool:
    """Return whether allocation and attempt records prove segment completion."""
    manifest = load_segment_manifest(paths["manifest"])
    if manifest is None or manifest.get("blocking_reasons"):
        return False
    state = derive_segment_manifest_state(manifest, _segment_ledger_index(paths))
    return state["status"] == "complete"


def _segment_summary_base(paths: dict[str, Path]) -> dict:
    """Load an existing summary or reconstruct its segment identity from the manifest."""
    if paths["summary"].exists():
        try:
            payload = json.loads(paths["summary"].read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = None
        if isinstance(payload, dict):
            return payload
    manifest = load_segment_manifest(paths["manifest"])
    if manifest is None:
        raise ValueError(f"Missing segment manifest: {paths['manifest']}")
    fingerprint = manifest.get("fingerprint", {})
    inputs = fingerprint.get("inputs", {}) if isinstance(fingerprint, dict) else {}
    answer_mode = inputs.get("answer_mode", {}) if isinstance(inputs, dict) else {}
    page_attempt_count = int(inputs.get("page_attempt_count", 0) or 0)
    return {
        "run_group_id": manifest.get("run_group_id", ""),
        "run_segment_id": manifest.get("segment_id", ""),
        "recipe_answer_type": answer_mode.get("answer_type", "") if isinstance(answer_mode, dict) else "",
        "recipe_record_limit": page_attempt_count,
        "recipe_target_count": page_attempt_count,
        "recipe_segment_expected_page_count": page_attempt_count,
        "summary_output": str(paths["summary"]),
        "output_path": str(paths["accepted"]),
        "rejected_output_path": str(paths["rejected"]),
    }


def _combine_segment_records(
    *,
    run_id: str,
    segment_summaries: list[dict],
    accepted_id_offset: int = 0,
) -> tuple[list[dict], list[dict]]:
    """Load segment JSONLs, attach recipe metadata, and renumber accepted rows."""
    accepted_records: list[dict] = []
    rejected_records: list[dict] = []
    for summary in segment_summaries:
        answer_type = str(summary.get("recipe_answer_type", ""))
        record_limit = int(summary.get("recipe_record_limit", 0) or 0)
        accepted, _ = load_endpoint_jsonl(Path(str(summary.get("segment_accepted_output"))), label="accepted")
        rejected, _ = load_endpoint_jsonl(Path(str(summary.get("segment_rejected_output"))), label="rejected")
        for record in [*accepted, *rejected]:
            if _is_compact_big_batch_record(record):
                continue
            metadata = record.setdefault("source_metadata", {})
            if isinstance(metadata, dict):
                metadata["recipe_id"] = run_id
                metadata["recipe_answer_type"] = answer_type
                metadata["recipe_record_limit"] = record_limit
                metadata["recipe_segment_id"] = summary.get("run_segment_id", "")
                metadata["recipe_segment_run_date"] = summary.get("run_date", "")
                metadata["recipe_segment_summary"] = summary.get("summary_output", "")
                ensure_page_id_list_entry_metadata(record)
        accepted_records.extend(accepted)
        rejected_records.extend(rejected)
    assign_unique_route3_record_ids(accepted_records)
    for index, record in enumerate(accepted_records, start=max(0, int(accepted_id_offset)) + 1):
        if not str(record.get("id") or "").strip():
            record["id"] = f"simpleqa_candidate_{index:06d}"
    return accepted_records, rejected_records


def _is_compact_big_batch_record(record: dict) -> bool:
    """Return whether a segment record is already in compact production shape."""
    if "failing_reason" in record:
        return True
    return "reasoning_type" in record and "relation_or_claim" not in record


def _recipe_summary(
    *,
    args: argparse.Namespace,
    run_id: str,
    recipe_items: list[RecipeItem],
    reasoning_types: list[str],
    table_filter_modes: list[str],
    segment_summaries: list[dict],
    accepted_records: list[dict],
    rejected_records: list[dict],
    output: Path,
    rejected_output: Path,
    summary_output: Path,
    walkthrough_output: Path,
    stream_state_base: Path,
    append_label: str,
    wall_clock_seconds: float,
    table_source_types: list[str] | None = None,
) -> dict:
    """Build the combined recipe summary."""
    normalized_table_source_types = list(
        normalize_route3_table_source_types(table_source_types or DEFAULT_ROUTE3_TABLE_SOURCE_TYPES)
    )
    attempted = sum(int(summary.get("attempted_page_ids", 0) or 0) for summary in segment_summaries)
    page_ids = [
        page_id
        for summary in segment_summaries
        for page_id in summary.get("page_ids", [])
    ]
    page_id_entries = sorted(
        {
            entry
            for summary in segment_summaries
            for entry in _summary_page_id_entries(summary)
        }
    )
    stream_states = _segment_stream_states(segment_summaries)
    state_stats = _aggregate_stream_state_stats(segment_summaries)
    segment_wall_clock_seconds = round(
        sum(float(summary.get("wall_clock_seconds", 0.0) or 0.0) for summary in segment_summaries),
        4,
    )
    displayed_wall_clock_seconds = round(max(segment_wall_clock_seconds, wall_clock_seconds), 4)
    ddg_settings = duckduckgo_settings_kwargs(args)
    return {
        "run_group_id": run_id,
        "run_segment_id": "recipe_combined",
        "recipe_id": run_id,
        "external_excluded_page_count": (
            segment_summaries[0].get("external_excluded_page_count", 0) if segment_summaries else 0
        ),
        "external_excluded_page_ids_sha256": (
            segment_summaries[0].get("external_excluded_page_ids_sha256", "") if segment_summaries else ""
        ),
        "external_exclusion_collision_count": sum(
            int(summary.get("external_exclusion_collision_count", 0) or 0) for summary in segment_summaries
        ),
        "recipe_items": [
            {"answer_type": item.answer_type, "target_count": item.record_limit, "record_limit": item.record_limit}
            for item in recipe_items
        ],
        "recipe_segments": [
            {
                "answer_type": summary.get("recipe_answer_type", ""),
                "target_count": summary.get("recipe_target_count", summary.get("recipe_record_limit", 0)),
                "record_limit": summary.get("recipe_record_limit", 0),
                "expected_page_count": summary.get("recipe_segment_expected_page_count", 0),
                "stream_reuse_cached_page_count": summary.get("recipe_segment_reuse_cached_page_count", ""),
                "stream_fresh_cached_page_count": summary.get("recipe_segment_fresh_cached_page_count", ""),
                "attempted_page_ids": summary.get("attempted_page_ids", 0),
                "accepted": summary.get("accepted", 0),
                "rejected": summary.get("rejected", 0),
                "retry_pending": summary.get("retry_pending", 0),
                "wall_clock_seconds": summary.get("wall_clock_seconds"),
                "random_seed": summary.get("random_seed"),
                "stream_state": summary.get("stream_state", ""),
                "summary_output": summary.get("summary_output", ""),
                "accepted_output": summary.get("segment_accepted_output", ""),
                "rejected_output": summary.get("segment_rejected_output", ""),
            }
            for summary in segment_summaries
        ],
        "start_stage": "generate",
        "start_from_endpoint": False,
        "endpoint_resume": {"enabled": False},
        "streaming_mode": "page_id_stream_recipe",
        "stream_page_source": "table-search",
        "stream_search_queries": segment_summaries[0].get("stream_search_queries", []) if segment_summaries else [],
        "run_date": args.run_date or (segment_summaries[0].get("run_date") if segment_summaries else ""),
        "stream_state": "separate_segment_stream_states",
        "stream_state_base": str(stream_state_base),
        "stream_states": stream_states,
        "stream_state_stats": state_stats,
        "stream_state_reset": True,
        "append_to_existing_run": bool(getattr(args, "append_to_existing_run", False)),
        "append_run_label": append_label,
        "stream_reuse_cached_page_count": args.stream_reuse_cached_page_count,
        "stream_reused_cached_page_count": sum(
            int(summary.get("stream_reused_cached_page_count", 0) or 0)
            for summary in segment_summaries
        ),
        "stream_reused_cached_page_ids": [
            page_id
            for summary in segment_summaries
            for page_id in summary.get("stream_reused_cached_page_ids", [])
        ],
        "recipe_target_count": sum(item.record_limit for item in recipe_items),
        "record_limit": sum(item.record_limit for item in recipe_items),
        "record_limit_deprecated_alias": True,
        "attempted_page_ids": attempted,
        "attempted_page_ids_unique": len({_coerce_int(page_id) for page_id in page_ids if _coerce_int(page_id)}),
        "page_ids": page_ids,
        "page_id_list_entries": [entry.to_record() for entry in page_id_entries],
        "accepted": len(accepted_records),
        "accepted_total": len(accepted_records),
        "rejected": len(rejected_records),
        "rejected_total": len(rejected_records),
        "retry_pending": sum(int(summary.get("retry_pending", 0) or 0) for summary in segment_summaries),
        "wall_clock_seconds": displayed_wall_clock_seconds,
        "recipe_segment_wall_clock_seconds": segment_wall_clock_seconds,
        "recipe_runner_wall_clock_seconds": wall_clock_seconds,
        "output_path": str(output),
        "rejected_output_path": str(rejected_output),
        "summary_output": str(summary_output),
        "walkthrough_output": str(walkthrough_output),
        "domain_policy": "domain_and_subdomain_optional_for_page_id_streaming",
        "enabled_routes": ["route3_wikipedia_infobox"],
        "generation_model": args.generation_model,
        "small_model": args.generation_model,
        "second_stage_grading_enabled": bool(args.enable_second_stage_grading),
        "duckduckgo_top_k": args.duckduckgo_top_k,
        "duckduckgo_parallel_queries": args.duckduckgo_parallel_queries,
        "duckduckgo_prefer_ddgs": ddg_settings["duckduckgo_prefer_ddgs"],
        "duckduckgo_ddgs_backend": ddg_settings["duckduckgo_ddgs_backend"],
        "duckduckgo_ddgs_max_attempts": ddg_settings["duckduckgo_ddgs_max_attempts"],
        "duckduckgo_disabled_fallbacks": list(ddg_settings["duckduckgo_disable_fallbacks"]),
        "duckduckgo_cooldown_enabled": ddg_settings["duckduckgo_cooldown_enabled"],
        "duckduckgo_cooldown_failure_threshold": ddg_settings["duckduckgo_cooldown_failure_threshold"],
        "duckduckgo_cooldown_initial_seconds": ddg_settings["duckduckgo_cooldown_initial_seconds"],
        "duckduckgo_cooldown_max_seconds": ddg_settings["duckduckgo_cooldown_max_seconds"],
        "generated_search_query_count": args.generated_search_query_count,
        "route3_reasoning_types": reasoning_types,
        "route3_answer_types": [item.answer_type for item in recipe_items],
        "route3_answer_type_mode": args.route3_answer_type_mode,
        "route3_table_filter_modes": table_filter_modes,
        "route3_table_source_types": normalized_table_source_types,
        "route3_prose_leakage_scoring_enabled": True,
        "min_table_score": 0.0,
        "route3_page_archive_dir": str(args.route3_page_archive_dir),
        "route3_infobox_max_removed_row_rate": args.route3_infobox_max_removed_row_rate,
        "route3_infobox_min_remaining_rows": args.route3_infobox_min_remaining_rows,
        "compact_output": False,
        "compact_output_ignored": bool(args.compact_output or args.big_batch_mode),
        "compact_rejected_output": False,
        "compact_rejected_output_ignored": bool(args.compact_rejected_output or args.compact_output or args.big_batch_mode),
        "big_batch_mode": bool(args.big_batch_mode),
        "stream_discovery_max_retries": args.stream_discovery_max_retries,
        "stream_discovery_retry_backoff_seconds": args.stream_discovery_retry_backoff_seconds,
        "stream_discovery_retry_max_sleep_seconds": args.stream_discovery_retry_max_sleep_seconds,
        "wikipedia_429_backoff_seconds": args.wikipedia_429_backoff_seconds,
        "wikipedia_429_max_backoff_seconds": args.wikipedia_429_max_backoff_seconds,
        "wikipedia_429_recovery_seconds": args.wikipedia_429_recovery_seconds,
        **llm_generation_table_yield_summary(accepted_records, rejected_records),
        "survival_by_layer": survival_by_layer(
            attempted_count=attempted,
            accepted_records=accepted_records,
            rejected_records=rejected_records,
            rerun_records=[],
        ),
        "failure_reason_counts": failure_reason_counts(rejected_records, []),
        "phase_timing_stats_seconds": phase_timing_stats([*accepted_records, *rejected_records]),
        "aggregate_phase_timings_seconds": aggregate_phase_timings(accepted_records, rejected_records),
        "accepted_by_recipe_answer_type": _records_by_recipe_answer_type(accepted_records),
        "rejected_by_recipe_answer_type": _records_by_recipe_answer_type(rejected_records),
    }


def _segment_stream_states(segment_summaries: list[dict]) -> list[str]:
    """Return stream-state paths used by recipe segments."""
    states: list[str] = []
    seen: set[str] = set()
    for summary in segment_summaries:
        state = str(summary.get("stream_state", "") or "")
        if state and state not in seen:
            states.append(state)
            seen.add(state)
    return states


def _aggregate_stream_state_stats(segment_summaries: list[dict]) -> dict[str, int]:
    """Aggregate per-segment stream-state stats for the combined recipe summary."""
    totals = {
        "used": 0,
        "in_progress": 0,
        "accepted": 0,
        "rejected": 0,
        "rerun_pool": 0,
        "table_search_queries": 0,
    }
    for summary in segment_summaries:
        stats = summary.get("stream_state_stats", {})
        if not isinstance(stats, dict):
            continue
        for key in totals:
            totals[key] += int(stats.get(key, 0) or 0)
    totals["used"] = max(0, totals["used"])
    return totals


def _records_by_recipe_answer_type(records: list[dict]) -> dict[str, int]:
    """Count records by configured recipe answer_type."""
    counts: dict[str, int] = {}
    for record in records:
        metadata = record.get("source_metadata", {})
        answer_type = ""
        if isinstance(metadata, dict):
            answer_type = str(metadata.get("recipe_answer_type", "") or "")
        counts[answer_type] = counts.get(answer_type, 0) + 1
    return counts


def _coerce_int(value) -> int | None:
    """Coerce a value to int when possible."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


if __name__ == "__main__":
    raise SystemExit(main())
