"""Run a Route 3 Wikipedia table batch recipe across answer types."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.io import write_jsonl
from wikidata_simpleqa.wikipedia_infobox_generator import (
    DEFAULT_ROUTE3_TABLE_FILTER_MODES,
    normalize_route3_answer_types,
    normalize_route3_extra_prompts,
    normalize_route3_reasoning_types,
    normalize_route3_table_filter_modes,
)
from wikidata_simpleqa.wikipedia_streaming import PageIdStreamState

from run_wikipedia_infobox_pipeline import (
    _aggregate_phase_timings,
    _failure_reason_counts,
    _load_endpoint_jsonl,
    _phase_timing_stats,
    _safe_artifact_id,
    _survival_by_layer,
    _write_stream_walkthrough,
)


@dataclass(frozen=True, slots=True)
class RecipeItem:
    """One answer-type segment in a Route 3 recipe."""

    answer_type: str
    record_limit: int


def parse_args() -> argparse.Namespace:
    """Parse recipe runner arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--recipe",
        action="append",
        default=[],
        help=(
            "Recipe text such as '40 Person, 40 Place, single_fact'. "
            "Can be repeated; comma-separated chunks are merged."
        ),
    )
    parser.add_argument(
        "--answer-type-count",
        action="append",
        default=[],
        help="Explicit answer-type target such as Person=40 or '40 Person'. Can be repeated.",
    )
    parser.add_argument(
        "--answer-types",
        action="append",
        default=[],
        help="Answer types for --per-answer-type. Repeat or pass comma-separated values.",
    )
    parser.add_argument("--per-answer-type", type=int, default=0)
    parser.add_argument(
        "--route3-reasoning-type",
        action="append",
        default=[],
        help="Shared reasoning_type constraint. Defaults to single_fact when omitted from the recipe.",
    )
    parser.add_argument(
        "--route3-extra-prompt",
        action="append",
        default=[],
        help="Shared extra prompt text passed through to each segment.",
    )
    parser.add_argument(
        "--route3-table-filter-mode",
        action="append",
        default=list(DEFAULT_ROUTE3_TABLE_FILTER_MODES),
        help="Shared Route 3 table filter modes. Defaults are enabled.",
    )
    parser.add_argument(
        "--disable-route3-table-filter-mode",
        action="append",
        default=[],
        help="Disable one shared default Route 3 table filter mode.",
    )
    parser.add_argument("--run-id", default="", help="Path-safe batch ID. Defaults to a dated recipe ID.")
    parser.add_argument("--run-date", default=None)
    parser.add_argument("--target-time", default="2024")
    parser.add_argument("--cutoff-year", type=int, default=2025)
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--proxy", default="socks5://127.0.0.1:7897")
    parser.add_argument("--small-model-provider", default="openrouter")
    parser.add_argument("--small-model", default="openai/gpt-4.1-mini")
    parser.add_argument("--small-model-api-key-env", default="OPENROUTER_API_KEY")
    parser.add_argument("--small-model-base-url", default="https://openrouter.ai/api/v1")
    parser.add_argument("--small-model-max-tokens", type=int, default=1200)
    parser.add_argument("--enable-rewrite", action="store_true")
    parser.add_argument("--rewrite-model", default="openai/gpt-4.1-mini")
    parser.add_argument("--enable-second-stage-grading", action="store_true")
    parser.add_argument("--second-stage-grading-accuracy-threshold", type=float, default=0.1)
    parser.add_argument("--duckduckgo-top-k", type=int, default=5)
    parser.add_argument("--duckduckgo-parallel-queries", type=int, default=3)
    parser.add_argument("--generated-search-query-count", type=int, default=2)
    parser.add_argument("--search-longtail-max-full-question-hit-rate", type=float, default=0.3)
    parser.add_argument("--search-longtail-max-keyword-hit-rate", type=float, default=0.3)
    parser.add_argument("--search-longtail-max-overall-hit-rate", type=float, default=0.3)
    parser.add_argument("--stream-page-source", choices=["table-search", "random-page-id"], default="table-search")
    parser.add_argument("--stream-search-query", action="append", default=[])
    parser.add_argument("--enable-broad-table-search", action="store_true")
    parser.add_argument("--stream-search-limit", type=int, default=50)
    parser.add_argument("--stream-search-max-rounds", type=int, default=10)
    parser.add_argument("--stream-random-seed", type=int, default=42)
    parser.add_argument("--stream-batch-size", type=int, default=10)
    parser.add_argument("--stream-page-workers", type=int, default=4)
    parser.add_argument("--wikipedia-concurrency-limit", type=int, default=4)
    parser.add_argument("--duckduckgo-concurrency-limit", type=int, default=4)
    parser.add_argument("--openrouter-generation-rewrite-concurrency-limit", type=int, default=10)
    parser.add_argument("--second-stage-concurrency-limit", type=int, default=10)
    parser.add_argument(
        "--disable-auto-rerun-once",
        action="store_true",
        help="By default each segment immediately reruns its transient rerun pool once.",
    )
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--rejected-output", type=Path, default=None)
    parser.add_argument("--summary-output", type=Path, default=None)
    parser.add_argument("--walkthrough-output", type=Path, default=None)
    parser.add_argument("--stream-state", type=Path, default=None)
    parser.add_argument("--segment-dir", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    """Run the recipe segments and combine their artifacts."""
    args = parse_args()
    run_started = perf_counter()
    recipe_items, reasoning_types = _parse_recipe(args)
    if not recipe_items:
        raise ValueError("Recipe must include at least one answer-type count, e.g. '40 Person'.")
    if not reasoning_types:
        reasoning_types = ["single_fact"]
    args.route3_extra_prompt = list(normalize_route3_extra_prompts(args.route3_extra_prompt))
    enabled_filter_modes = list(normalize_route3_table_filter_modes(args.route3_table_filter_mode))
    disabled_filter_modes = set(normalize_route3_table_filter_modes(args.disable_route3_table_filter_mode))
    table_filter_modes = [mode for mode in enabled_filter_modes if mode not in disabled_filter_modes]

    run_id = _recipe_run_id(args, recipe_items, reasoning_types)
    segment_dir = args.segment_dir or ROOT / "outputs" / "recipe_segments" / run_id
    output = args.output or ROOT / "outputs" / f"{run_id}_accepted.jsonl"
    rejected_output = args.rejected_output or ROOT / "outputs" / f"{run_id}_rejected.jsonl"
    summary_output = args.summary_output or ROOT / "outputs" / f"{run_id}_summary.json"
    walkthrough_output = args.walkthrough_output or ROOT / "docs" / "walkthroughs" / f"{run_id}.md"
    stream_state = args.stream_state or ROOT / "outputs" / f"{run_id}_state.json"

    segment_dir.mkdir(parents=True, exist_ok=True)
    segment_summaries: list[dict] = []
    for index, item in enumerate(recipe_items):
        command, paths = _segment_command(
            args=args,
            item=item,
            index=index,
            run_id=run_id,
            segment_dir=segment_dir,
            stream_state=stream_state,
            reasoning_types=reasoning_types,
            table_filter_modes=table_filter_modes,
        )
        if _segment_complete(paths):
            summary = json.loads(paths["summary"].read_text(encoding="utf-8"))
            summary["recipe_answer_type"] = item.answer_type
            summary["recipe_record_limit"] = item.record_limit
            summary["segment_accepted_output"] = str(paths["accepted"])
            summary["segment_rejected_output"] = str(paths["rejected"])
            segment_summaries.append(summary)
            continue
        if args.dry_run:
            print(" ".join(command))
            continue
        subprocess.run(command, cwd=ROOT, check=True)
        summary = json.loads(paths["summary"].read_text(encoding="utf-8"))
        summary["recipe_answer_type"] = item.answer_type
        summary["recipe_record_limit"] = item.record_limit
        summary["segment_accepted_output"] = str(paths["accepted"])
        summary["segment_rejected_output"] = str(paths["rejected"])
        segment_summaries.append(summary)

    if args.dry_run:
        return 0

    accepted_records, rejected_records = _combine_segment_records(
        run_id=run_id,
        segment_summaries=segment_summaries,
    )
    write_jsonl(output, accepted_records)
    write_jsonl(rejected_output, rejected_records)

    summary = _recipe_summary(
        args=args,
        run_id=run_id,
        recipe_items=recipe_items,
        reasoning_types=reasoning_types,
        table_filter_modes=table_filter_modes,
        segment_summaries=segment_summaries,
        accepted_records=accepted_records,
        rejected_records=rejected_records,
        output=output,
        rejected_output=rejected_output,
        summary_output=summary_output,
        walkthrough_output=walkthrough_output,
        stream_state=stream_state,
        wall_clock_seconds=round(perf_counter() - run_started, 4),
    )
    summary_output.parent.mkdir(parents=True, exist_ok=True)
    summary_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    _write_stream_walkthrough(
        path=walkthrough_output,
        summary=summary,
        accepted_records=accepted_records,
        rejected_records=rejected_records,
        rerun_records=[],
        existing_accepted_records=[],
        existing_rejected_records=[],
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


def _parse_recipe(args: argparse.Namespace) -> tuple[list[RecipeItem], list[str]]:
    """Parse recipe text and explicit answer-type options."""
    raw_parts: list[str] = []
    for recipe_text in args.recipe:
        raw_parts.extend(part.strip() for part in str(recipe_text).split(","))
    raw_parts.extend(str(value).strip() for value in args.answer_type_count)
    items: list[RecipeItem] = []
    reasoning_types: list[str] = []
    for part in raw_parts:
        if not part:
            continue
        parsed_item = _parse_recipe_item(part)
        if parsed_item is not None:
            items.append(parsed_item)
            continue
        parsed_reasoning = normalize_route3_reasoning_types([part])
        if parsed_reasoning:
            reasoning_types.extend(value for value in parsed_reasoning if value not in reasoning_types)
            continue
        raise ValueError(f"Could not parse recipe part {part!r}.")
    if args.answer_types:
        if args.per_answer_type < 1:
            raise ValueError("--answer-types requires --per-answer-type >= 1.")
        for answer_type in normalize_route3_answer_types(args.answer_types):
            items.append(RecipeItem(answer_type=answer_type, record_limit=args.per_answer_type))
    for reasoning_type in normalize_route3_reasoning_types(args.route3_reasoning_type):
        if reasoning_type not in reasoning_types:
            reasoning_types.append(reasoning_type)
    return items, reasoning_types


def _parse_recipe_item(part: str) -> RecipeItem | None:
    """Parse one answer-type count recipe token."""
    count_first = re.fullmatch(r"(\d+)\s+([A-Za-z_ -]+)", part.strip())
    type_first = re.fullmatch(r"([A-Za-z_ -]+)\s*[:=]\s*(\d+)", part.strip())
    if count_first:
        count = int(count_first.group(1))
        answer_type_raw = count_first.group(2)
    elif type_first:
        count = int(type_first.group(2))
        answer_type_raw = type_first.group(1)
    else:
        return None
    answer_types = normalize_route3_answer_types([answer_type_raw])
    if len(answer_types) != 1:
        raise ValueError(f"Recipe part {part!r} must name exactly one answer_type.")
    if count < 1:
        raise ValueError(f"Recipe part {part!r} must use a positive count.")
    return RecipeItem(answer_type=answer_types[0], record_limit=count)


def _recipe_run_id(args: argparse.Namespace, recipe_items: list[RecipeItem], reasoning_types: list[str]) -> str:
    """Return a path-safe run ID for this recipe."""
    if args.run_id.strip():
        return _safe_artifact_id(args.run_id, fallback="route3_recipe")
    count_text = "_".join(f"{item.record_limit}{item.answer_type.lower()}" for item in recipe_items)
    reasoning_text = "_".join(reasoning_types or ["single_fact"])
    return _safe_artifact_id(
        f"wikipedia_stream_recipe_{count_text}_{reasoning_text}_{date.today().isoformat().replace('-', '_')}",
        fallback="route3_recipe",
    )


def _segment_command(
    *,
    args: argparse.Namespace,
    item: RecipeItem,
    index: int,
    run_id: str,
    segment_dir: Path,
    stream_state: Path,
    reasoning_types: list[str],
    table_filter_modes: list[str],
) -> tuple[list[str], dict[str, Path]]:
    """Build the pipeline subprocess command for one recipe segment."""
    safe_answer_type = item.answer_type.lower()
    segment_id = f"{index + 1:02d}_{safe_answer_type}_{item.record_limit}"
    accepted = segment_dir / f"{segment_id}_accepted.jsonl"
    rejected = segment_dir / f"{segment_id}_rejected.jsonl"
    summary = segment_dir / f"{segment_id}_summary.json"
    command = [
        sys.executable,
        str(ROOT / "scripts" / "run_wikipedia_infobox_pipeline.py"),
        "--stream-random-page-ids",
        "--record-limit",
        str(item.record_limit),
        "--route3-answer-type",
        item.answer_type,
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
        "--target-time",
        str(args.target_time),
        "--cutoff-year",
        str(args.cutoff_year),
        "--timeout-seconds",
        str(args.timeout_seconds),
        "--proxy",
        str(args.proxy),
        "--small-model-provider",
        str(args.small_model_provider),
        "--small-model",
        str(args.small_model),
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
        "--generated-search-query-count",
        str(args.generated_search_query_count),
        "--search-longtail-max-full-question-hit-rate",
        str(args.search_longtail_max_full_question_hit_rate),
        "--search-longtail-max-keyword-hit-rate",
        str(args.search_longtail_max_keyword_hit_rate),
        "--search-longtail-max-overall-hit-rate",
        str(args.search_longtail_max_overall_hit_rate),
        "--stream-page-source",
        str(args.stream_page_source),
        "--stream-search-limit",
        str(args.stream_search_limit),
        "--stream-search-max-rounds",
        str(args.stream_search_max_rounds),
        "--stream-random-seed",
        str(args.stream_random_seed),
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
    ]
    if args.run_date:
        command.extend(["--run-date", str(args.run_date)])
    for reasoning_type in reasoning_types:
        command.extend(["--route3-reasoning-type", reasoning_type])
    for extra_prompt in args.route3_extra_prompt:
        command.extend(["--route3-extra-prompt", extra_prompt])
    for mode in table_filter_modes:
        command.extend(["--route3-table-filter-mode", mode])
    for mode in args.disable_route3_table_filter_mode:
        command.extend(["--disable-route3-table-filter-mode", str(mode)])
    if args.enable_rewrite:
        command.extend(["--enable-rewrite", "--rewrite-model", str(args.rewrite_model)])
    if args.enable_second_stage_grading:
        command.extend(
            [
                "--enable-second-stage-grading",
                "--second-stage-grading-accuracy-threshold",
                str(args.second_stage_grading_accuracy_threshold),
            ]
        )
    if not args.disable_auto_rerun_once:
        command.append("--stream-auto-rerun-once")
    if index == 0:
        command.append("--reset-stream-state")
    for query in args.stream_search_query:
        command.extend(["--stream-search-query", str(query)])
    if args.enable_broad_table_search:
        command.append("--enable-broad-table-search")
    return command, {"accepted": accepted, "rejected": rejected, "summary": summary}


def _segment_complete(paths: dict[str, Path]) -> bool:
    """Return whether a recipe segment already has reusable artifacts."""
    return all(paths[name].exists() for name in ("accepted", "rejected", "summary"))


def _combine_segment_records(
    *,
    run_id: str,
    segment_summaries: list[dict],
) -> tuple[list[dict], list[dict]]:
    """Load segment JSONLs, attach recipe metadata, and renumber accepted rows."""
    accepted_records: list[dict] = []
    rejected_records: list[dict] = []
    for summary in segment_summaries:
        answer_type = str(summary.get("recipe_answer_type", ""))
        record_limit = int(summary.get("recipe_record_limit", 0) or 0)
        accepted, _ = _load_endpoint_jsonl(Path(str(summary.get("segment_accepted_output"))), label="accepted")
        rejected, _ = _load_endpoint_jsonl(Path(str(summary.get("segment_rejected_output"))), label="rejected")
        for record in [*accepted, *rejected]:
            metadata = record.setdefault("source_metadata", {})
            if isinstance(metadata, dict):
                metadata["recipe_id"] = run_id
                metadata["recipe_answer_type"] = answer_type
                metadata["recipe_record_limit"] = record_limit
                metadata["recipe_segment_id"] = summary.get("run_segment_id", "")
                metadata["recipe_segment_summary"] = summary.get("summary_output", "")
        accepted_records.extend(accepted)
        rejected_records.extend(rejected)
    for index, record in enumerate(accepted_records, start=1):
        record["id"] = f"simpleqa_candidate_{index:06d}"
    return accepted_records, rejected_records


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
    stream_state: Path,
    wall_clock_seconds: float,
) -> dict:
    """Build the combined recipe summary."""
    attempted = sum(int(summary.get("attempted_page_ids", 0) or 0) for summary in segment_summaries)
    page_ids = [
        page_id
        for summary in segment_summaries
        for page_id in summary.get("page_ids", [])
    ]
    state_stats = PageIdStreamState.load(stream_state).stats() if stream_state.exists() else {}
    rerun_pool_ids = []
    rerun_reasons = {}
    if stream_state.exists():
        state = PageIdStreamState.load(stream_state)
        rerun_pool_ids = state.rerun_pool.copy()
        rerun_reasons = {str(page_id): state.failure_reasons.get(page_id, "") for page_id in rerun_pool_ids}
    return {
        "run_group_id": run_id,
        "run_segment_id": "recipe_combined",
        "recipe_id": run_id,
        "recipe_items": [
            {"answer_type": item.answer_type, "record_limit": item.record_limit}
            for item in recipe_items
        ],
        "recipe_segments": [
            {
                "answer_type": summary.get("recipe_answer_type", ""),
                "record_limit": summary.get("recipe_record_limit", 0),
                "attempted_page_ids": summary.get("attempted_page_ids", 0),
                "accepted": summary.get("accepted", 0),
                "rejected": summary.get("rejected", 0),
                "rerun": summary.get("rerun", 0),
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
        "stream_page_source": args.stream_page_source,
        "stream_search_queries": segment_summaries[0].get("stream_search_queries", []) if segment_summaries else [],
        "run_date": args.run_date or (segment_summaries[0].get("run_date") if segment_summaries else ""),
        "stream_state": str(stream_state),
        "stream_state_stats": state_stats,
        "stream_state_reset": True,
        "stream_auto_rerun_once": not args.disable_auto_rerun_once,
        "rerun_pool_ids_after_run": rerun_pool_ids,
        "rerun_pool_failure_reasons_after_run": rerun_reasons,
        "record_limit": sum(item.record_limit for item in recipe_items),
        "attempted_page_ids": attempted,
        "attempted_page_ids_unique": len({_coerce_int(page_id) for page_id in page_ids if _coerce_int(page_id)}),
        "page_ids": page_ids,
        "accepted": len(accepted_records),
        "accepted_total": len(accepted_records),
        "rejected": len(rejected_records),
        "rejected_total": len(rejected_records),
        "rerun": sum(int(summary.get("rerun", 0) or 0) for summary in segment_summaries),
        "wall_clock_seconds": wall_clock_seconds,
        "output_path": str(output),
        "rejected_output_path": str(rejected_output),
        "summary_output": str(summary_output),
        "walkthrough_output": str(walkthrough_output),
        "domain_policy": "domain_and_subdomain_optional_for_page_id_streaming",
        "enabled_routes": ["route3_wikipedia_infobox"],
        "small_model": args.small_model,
        "rewrite_enabled": bool(args.enable_rewrite),
        "second_stage_grading_enabled": bool(args.enable_second_stage_grading),
        "duckduckgo_top_k": args.duckduckgo_top_k,
        "duckduckgo_parallel_queries": args.duckduckgo_parallel_queries,
        "generated_search_query_count": args.generated_search_query_count,
        "route3_reasoning_types": reasoning_types,
        "route3_answer_types": [item.answer_type for item in recipe_items],
        "route3_extra_prompts": args.route3_extra_prompt,
        "route3_table_filter_modes": table_filter_modes,
        "survival_by_layer": _survival_by_layer(
            attempted_count=attempted,
            rejected_records=rejected_records,
            rerun_records=[],
        ),
        "failure_reason_counts": _failure_reason_counts(rejected_records, []),
        "phase_timing_stats_seconds": _phase_timing_stats([*accepted_records, *rejected_records]),
        "aggregate_phase_timings_seconds": _aggregate_phase_timings(accepted_records, rejected_records),
        "accepted_by_recipe_answer_type": _records_by_recipe_answer_type(accepted_records),
        "rejected_by_recipe_answer_type": _records_by_recipe_answer_type(rejected_records),
    }


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
