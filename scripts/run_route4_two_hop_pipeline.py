"""Run Route 4 Wikidata two-hop generation through shared filters."""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from json import JSONDecodeError
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.concurrency import SemaphoreWrappedClient, build_shared_pipeline_concurrency
from wikidata_simpleqa.config import LLMConfig, Settings
from wikidata_simpleqa.domain_templates import get_all_templates, get_template_by_key
from wikidata_simpleqa.final_selection import select_final_records
from wikidata_simpleqa.generation_pipeline import (
    build_second_stage_grader_client,
    build_second_stage_model_panel,
    process_generated_candidates,
)
from wikidata_simpleqa.generators import WikidataHiddenEntityTwoHopGenerator
from wikidata_simpleqa.grading import ModelPanelMember
from wikidata_simpleqa.io import append_jsonl, write_jsonl
from wikidata_simpleqa.llm_rewrite import make_rewrite_client
from wikidata_simpleqa.reasoning import normalize_reasoning_style
from wikidata_simpleqa.route4_two_hop import (
    ROUTE4_WIKIDATA_TWO_HOP_ROUTE,
    route4_two_hop_seed_key_from_record,
    route4_two_hop_seed_unit_from_candidate,
)
from wikidata_simpleqa.route1_multihop import Route1QidSeedState
from wikidata_simpleqa.search_client import DuckDuckGoSearchClient
from wikidata_simpleqa.wikidata_client import WikidataClient


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
        """Return a compact endpoint-resume summary."""
        return {
            "enabled": self.enabled,
            "accepted_records_loaded": self.accepted_count,
            "rejected_records_loaded": self.rejected_count,
            "final_decisions_loaded": self.final_decision_count,
            "skipped_malformed_lines": len(self.skipped_lines),
            "skipped_line_details": self.skipped_lines[:20],
        }


def parse_args() -> argparse.Namespace:
    """Parse Route 4 two-hop runner arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-time", type=str, default="2024")
    parser.add_argument("--date-upper-bound", type=str, default="2024-12-31")
    parser.add_argument("--cutoff-year", type=int, default=2025)
    parser.add_argument("--record-limit", type=int, default=10)
    parser.add_argument("--harvest-limit", type=int, default=100)
    parser.add_argument("--accepted-target", type=int, default=0)
    parser.add_argument("--final-target", type=int, default=300)
    parser.add_argument("--template-keys", nargs="*", default=[])
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--proxy", type=str, default="socks5://127.0.0.1:7897")
    parser.add_argument("--duckduckgo-top-k", type=int, default=5)
    parser.add_argument("--duckduckgo-parallel-queries", type=int, default=3)
    parser.add_argument("--generated-search-query-count", type=int, default=2)
    parser.add_argument("--candidate-workers", type=int, default=4)
    parser.add_argument("--wikidata-concurrency-limit", type=int, default=1)
    parser.add_argument("--duckduckgo-concurrency-limit", type=int, default=4)
    parser.add_argument("--openrouter-generation-rewrite-concurrency-limit", type=int, default=10)
    parser.add_argument("--second-stage-concurrency-limit", type=int, default=10)
    parser.add_argument("--enable-rewrite", action="store_true")
    parser.add_argument("--rewrite-provider", type=str, default="openrouter")
    parser.add_argument("--rewrite-model", type=str, default="openai/gpt-4.1-mini")
    parser.add_argument("--rewrite-api-key-env", type=str, default="OPENROUTER_API_KEY")
    parser.add_argument("--rewrite-base-url", type=str, default="https://openrouter.ai/api/v1")
    parser.add_argument("--enable-second-stage-grading", action="store_true")
    parser.add_argument("--second-stage-grading-accuracy-threshold", type=float, default=0.1)
    parser.add_argument("--start-from-endpoint", action="store_true")
    parser.add_argument("--reset-state", action="store_true")
    parser.add_argument("--run-group-id", type=str, default="")
    parser.add_argument("--run-segment-id", type=str, default="")
    parser.add_argument("--state", type=Path, default=ROOT / "outputs" / "route4_two_hop_state.json")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs" / "route4_two_hop_accepted.jsonl")
    parser.add_argument(
        "--rejected-output",
        type=Path,
        default=ROOT / "outputs" / "route4_two_hop_rejected.jsonl",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=ROOT / "outputs" / "route4_two_hop_summary.json",
    )
    parser.add_argument(
        "--final-output",
        type=Path,
        default=ROOT / "outputs" / "route4_two_hop_final.jsonl",
    )
    parser.add_argument(
        "--final-summary-output",
        type=Path,
        default=ROOT / "outputs" / "route4_two_hop_final_summary.json",
    )
    return parser.parse_args()


def main() -> int:
    """Run the Route 4 Wikidata two-hop pipeline."""
    args = parse_args()
    started = perf_counter()
    proxy = _optional_proxy(args.proxy)
    concurrency = build_shared_pipeline_concurrency(
        wikidata_limit=args.wikidata_concurrency_limit,
        duckduckgo_limit=args.duckduckgo_concurrency_limit,
        generation_rewrite_limit=args.openrouter_generation_rewrite_concurrency_limit,
        second_stage_limit=args.second_stage_concurrency_limit,
    )
    rewrite_llm = None
    if args.enable_rewrite:
        rewrite_llm = LLMConfig(
            provider=args.rewrite_provider,
            model=args.rewrite_model,
            api_key_env=args.rewrite_api_key_env,
            base_url=args.rewrite_base_url,
            proxy=proxy,
        )
    settings = Settings(
        target_time=args.target_time,
        date_upper_bound=args.date_upper_bound,
        pilot_total=1,
        harvest_limit_per_template=args.harvest_limit,
        cutoff_year=args.cutoff_year,
        duckduckgo_top_k=args.duckduckgo_top_k,
        duckduckgo_parallel_queries=args.duckduckgo_parallel_queries,
        generated_search_query_count=args.generated_search_query_count,
        second_stage_grading_enabled=args.enable_second_stage_grading,
        second_stage_grading_accuracy_threshold=args.second_stage_grading_accuracy_threshold,
        enabled_routes=(ROUTE4_WIKIDATA_TWO_HOP_ROUTE,),
        proxy=proxy,
        timeout_seconds=args.timeout_seconds,
        output_path=args.output,
        rejected_output_path=args.rejected_output,
        rewrite_enabled=args.enable_rewrite,
        rewrite_llm=rewrite_llm,
    )
    endpoint_resume = _load_endpoint_resume(args)
    state = Route1QidSeedState(path=args.state) if args.reset_state else Route1QidSeedState.load(args.state)
    if args.reset_state:
        state.save()
    endpoint_sync = {"accepted_keys_synced": 0, "rejected_keys_synced": 0}
    if args.start_from_endpoint:
        endpoint_sync = state.sync_decided_keys(
            accepted_keys=_endpoint_seed_keys(endpoint_resume.accepted_records),
            rejected_keys=_endpoint_seed_keys(endpoint_resume.rejected_records),
        )
    recovered_keys = state.recover_stale_in_progress()

    wikidata_client = SemaphoreWrappedClient(
        WikidataClient(
            user_agent=settings.user_agent,
            proxy=settings.proxy,
            timeout_seconds=settings.timeout_seconds,
            max_entity_ids_per_request=settings.wikidata_max_entity_ids_per_request,
            log_checkpoints=settings.wikidata_log_checkpoints,
            cache_dir=settings.cache_dir,
        ),
        concurrency.wikidata_semaphore,
        {"sparql_query", "get_entities", "search_entities"},
    )
    search_client = SemaphoreWrappedClient(
        DuckDuckGoSearchClient(
            user_agent=settings.user_agent,
            proxy=settings.proxy,
            timeout_seconds=settings.timeout_seconds,
            cache_dir=settings.cache_dir,
        ),
        concurrency.duckduckgo_semaphore,
        {"search"},
    )
    rewrite_client = make_rewrite_client(settings.rewrite_llm, settings.timeout_seconds) if settings.rewrite_enabled else None
    if rewrite_client is not None:
        rewrite_client = SemaphoreWrappedClient(
            rewrite_client,
            concurrency.generation_rewrite_semaphore,
            {"rewrite_question"},
        )
    second_stage_model_clients = _build_second_stage_model_panel(settings, concurrency.second_stage_semaphore)
    grading_grader_client = _build_second_stage_grader_client(settings, concurrency.second_stage_semaphore)

    templates = _selected_single_hop_templates(args.template_keys)
    generated_candidates = WikidataHiddenEntityTwoHopGenerator().generate(
        templates=templates,
        settings=settings,
        client=wikidata_client,
    )
    seed_units = []
    candidate_by_seed_key = {}
    for candidate in generated_candidates:
        if candidate.source_candidate is None:
            continue
        unit = route4_two_hop_seed_unit_from_candidate(candidate.source_candidate)
        seed_units.append(unit)
        candidate_by_seed_key[unit.state_key] = candidate
    remaining_limit = (
        _remaining_after_endpoint(args.record_limit, endpoint_resume.final_decision_count)
        if args.start_from_endpoint
        else args.record_limit
    )
    reserved_units = state.reserve_seed_units(
        seed_units,
        count=max(0, remaining_limit),
        prefer_rerun_pool=True,
    )

    accepted_records: list[dict] = []
    rejected_records: list[dict] = []
    rerun_records: list[dict] = []
    workers = max(1, int(args.candidate_workers))
    if args.accepted_target:
        workers = 1
    with ThreadPoolExecutor(max_workers=min(workers, max(1, len(reserved_units)))) as executor:
        futures = {
            executor.submit(
                _process_one_candidate,
                candidate_by_seed_key[unit.state_key],
                seed_key=unit.state_key,
                settings=settings,
                state=state,
                args=args,
                search_client=search_client,
                rewrite_client=rewrite_client,
                second_stage_model_clients=second_stage_model_clients,
                grading_grader_client=grading_grader_client,
                commit_lock=concurrency.commit_lock,
            ): unit.state_key
            for unit in reserved_units
            if unit.state_key in candidate_by_seed_key
        }
        for future in as_completed(futures):
            decision = future.result()
            accepted_records.extend(decision.get("accepted_records", []))
            rejected_records.extend(decision.get("rejected_records", []))
            if decision.get("status") == "rerun":
                rerun_records.append(decision)
            if args.accepted_target and len(accepted_records) >= args.accepted_target:
                break

    final_records, final_summary = _write_final_selection(args)
    summary = {
        "route": ROUTE4_WIKIDATA_TWO_HOP_ROUTE,
        "target_time": settings.target_time,
        "date_upper_bound": settings.date_upper_bound,
        "cutoff_year": settings.cutoff_year,
        "template_keys": [template.template_key for template in templates],
        "record_limit": args.record_limit,
        "record_limit_remaining_at_start": remaining_limit,
        "generated_candidates": len(generated_candidates),
        "reserved_seed_units": len(reserved_units),
        "accepted": len(accepted_records),
        "accepted_total": endpoint_resume.accepted_count + len(accepted_records),
        "rejected": len(rejected_records),
        "rejected_total": endpoint_resume.rejected_count + len(rejected_records),
        "rerun": len(rerun_records),
        "endpoint_resume": {**endpoint_resume.summary(), **endpoint_sync},
        "recovered_stale_in_progress_keys": recovered_keys,
        "state": str(args.state),
        "state_stats": state.stats(),
        "rerun_pool_keys_after_run": state.rerun_pool.copy(),
        "output_path": str(args.output),
        "rejected_output_path": str(args.rejected_output),
        "summary_output": str(args.summary_output),
        "final_output": str(args.final_output),
        "final_selected": len(final_records),
        "final_summary_output": str(args.final_summary_output),
        "final_selection": final_summary,
        "settings": {
            "duckduckgo_top_k": settings.duckduckgo_top_k,
            "duckduckgo_parallel_queries": settings.duckduckgo_parallel_queries,
            "generated_search_query_count": settings.generated_search_query_count,
            "rewrite_enabled": settings.rewrite_enabled,
            "second_stage_grading_enabled": settings.second_stage_grading_enabled,
            "second_stage_grading_accuracy_threshold": settings.second_stage_grading_accuracy_threshold,
        },
        "concurrency": {
            "candidate_workers": workers,
            "wikidata": args.wikidata_concurrency_limit,
            "duckduckgo": args.duckduckgo_concurrency_limit,
            "generation_rewrite": args.openrouter_generation_rewrite_concurrency_limit,
            "second_stage": args.second_stage_concurrency_limit,
        },
        "wall_clock_seconds": round(perf_counter() - started, 4),
    }
    _attach_run_artifact_metadata(args, summary)
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


def _process_one_candidate(
    candidate,
    *,
    seed_key: str,
    settings: Settings,
    state: Route1QidSeedState,
    args: argparse.Namespace,
    search_client,
    rewrite_client,
    second_stage_model_clients,
    grading_grader_client,
    commit_lock,
) -> dict:
    """Process one generated candidate through the shared downstream pipeline."""
    try:
        result = process_generated_candidates(
            [candidate],
            settings=settings,
            search_client=search_client,
            rewrite_client=rewrite_client,
            second_stage_model_clients=second_stage_model_clients,
            grading_grader_client=grading_grader_client,
        )
        if result.accepted:
            with commit_lock:
                for index, record in enumerate(result.accepted):
                    record["id"] = f"route4_two_hop_{len(state.accepted_keys) + index + 1:06d}"
                    _attach_record_metadata(record, seed_key=seed_key, args=args)
                append_jsonl(args.output, result.accepted)
                state.mark_accepted(seed_key)
            return {"status": "accepted", "seed_key": seed_key, "accepted_records": result.accepted}
        if result.rejected:
            for record in result.rejected:
                _attach_record_metadata(record, seed_key=seed_key, args=args)
            reason = _exact_failure_reason(result.rejected[0])
            if _should_rerun_route4_rejection(result.rejected[0]):
                with commit_lock:
                    state.mark_rerun(seed_key, reason=reason)
                return {"status": "rerun", "seed_key": seed_key, "reason": reason}
            with commit_lock:
                append_jsonl(args.rejected_output, result.rejected)
                state.mark_rejected(seed_key, reason=reason)
            return {
                "status": "rejected",
                "seed_key": seed_key,
                "rejected_records": result.rejected,
                "reason": reason,
            }
        with commit_lock:
            state.mark_rerun(seed_key, reason="pipeline_no_accept_or_reject")
        return {"status": "rerun", "seed_key": seed_key, "reason": "pipeline_no_accept_or_reject"}
    except Exception as exc:  # noqa: BLE001
        reason = f"pipeline_exception:{type(exc).__name__}"
        with commit_lock:
            state.mark_rerun(seed_key, reason=reason)
        return {"status": "rerun", "seed_key": seed_key, "reason": reason, "error_message": str(exc)}


def _selected_single_hop_templates(template_keys: list[str]) -> list:
    if not template_keys:
        return [
            template
            for template in get_all_templates()
            if normalize_reasoning_style(template.reasoning_style or template.composition_style) == "single_fact"
            and template.status != "frozen"
        ]
    templates = []
    for key in template_keys:
        template = get_template_by_key(key)
        if (
            template is not None
            and normalize_reasoning_style(template.reasoning_style or template.composition_style) == "single_fact"
            and template.status != "frozen"
        ):
            templates.append(template)
    return templates


def _build_second_stage_model_panel(settings: Settings, semaphore) -> list[ModelPanelMember]:
    """Build a second-stage model panel wrapped by a shared semaphore."""
    if not settings.second_stage_grading_enabled:
        return []
    members = build_second_stage_model_panel(settings)
    return [
        ModelPanelMember(name=member.name, client=SemaphoreWrappedClient(member.client, semaphore, {"complete_text"}))
        for member in members
    ]


def _build_second_stage_grader_client(settings: Settings, semaphore):
    """Build a second-stage grader client wrapped by a shared semaphore."""
    if not settings.second_stage_grading_enabled:
        return None
    client = build_second_stage_grader_client(settings)
    if client is None:
        return None
    return SemaphoreWrappedClient(client, semaphore, {"complete_text"})


def _write_final_selection(args: argparse.Namespace) -> tuple[list[dict], dict]:
    """Write final deduplicated and rebalanced review candidates."""
    records, skipped = _read_jsonl_tolerant(args.output)
    final_records, summary = select_final_records(records, target_count=max(0, int(args.final_target)), domain_key="domain")
    for index, record in enumerate(final_records, start=1):
        record["id"] = f"route4_two_hop_final_{index:06d}"
    write_jsonl(args.final_output, final_records)
    summary["skipped_malformed_lines"] = len(skipped)
    summary["skipped_line_details"] = skipped[:20]
    args.final_summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.final_summary_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return final_records, summary


def _load_endpoint_resume(args: argparse.Namespace) -> EndpointResumeState:
    """Load accepted/rejected endpoint JSONL files when resume is enabled."""
    if not args.start_from_endpoint:
        return EndpointResumeState(enabled=False)
    accepted_records, accepted_skipped = _read_jsonl_tolerant(args.output)
    rejected_records, rejected_skipped = _read_jsonl_tolerant(args.rejected_output)
    return EndpointResumeState(
        enabled=True,
        accepted_records=accepted_records,
        rejected_records=rejected_records,
        skipped_lines=[*accepted_skipped, *rejected_skipped],
    )


def _read_jsonl_tolerant(path: Path) -> tuple[list[dict], list[dict[str, object]]]:
    """Read JSONL while reporting malformed lines rather than failing."""
    if not path.exists():
        return [], []
    records: list[dict] = []
    skipped: list[dict[str, object]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except JSONDecodeError as exc:
            skipped.append({"path": str(path), "line_number": line_number, "error": str(exc)})
            continue
        if isinstance(payload, dict):
            records.append(payload)
    return records, skipped


def _endpoint_seed_keys(records: list[dict]) -> list[str]:
    """Return non-empty hidden-entity seed keys from endpoint records."""
    return [key for key in (route4_two_hop_seed_key_from_record(record) for record in records) if key]


def _remaining_after_endpoint(record_limit: int, final_decision_count: int) -> int:
    """Return how many new records are still needed after endpoint resume."""
    return max(0, int(record_limit) - max(0, int(final_decision_count)))


def _exact_failure_reason(record: dict) -> str:
    """Return the most specific failure reason for one rejected record."""
    return str(record.get("rejection_rule") or record.get("rejection_reason") or "").strip()


def _should_rerun_route4_rejection(record: dict) -> bool:
    """Return whether a Route 4 rejection is transient and worth rerunning."""
    reason = str(record.get("rejection_reason", "")).strip()
    return reason in {"search_longtail_verifier_error", "second_stage_grading_error"}


def _attach_record_metadata(record: dict, *, seed_key: str, args: argparse.Namespace) -> None:
    """Attach Route 4 run metadata to an accepted or rejected record."""
    metadata = record.setdefault("source_metadata", {})
    if isinstance(metadata, dict):
        metadata["route4_two_hop_seed_key"] = seed_key
        run_group_id = _safe_artifact_id(args.run_group_id)
        run_segment_id = _run_segment_id(args)
        if run_group_id:
            metadata["run_group_id"] = run_group_id
        if run_segment_id:
            metadata["run_segment_id"] = run_segment_id


def _attach_run_artifact_metadata(args: argparse.Namespace, summary: dict) -> None:
    """Update the optional run-group artifact manifest."""
    run_group_id = _safe_artifact_id(args.run_group_id)
    if not run_group_id:
        return
    manifest_path = ROOT / "outputs" / "run_manifests" / f"{run_group_id}.json"
    segment = {
        "segment_id": _run_segment_id(args),
        "summary_output": str(args.summary_output),
        "output_path": str(args.output),
        "rejected_output_path": str(args.rejected_output),
        "final_output": str(args.final_output),
        "state": str(args.state),
        "accepted": summary.get("accepted", 0),
        "rejected": summary.get("rejected", 0),
        "rerun": summary.get("rerun", 0),
    }
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        segments = [row for row in manifest.get("segments", []) if row.get("segment_id") != segment["segment_id"]]
    else:
        segments = []
    segments.append(segment)
    manifest = {
        "manifest_version": 1,
        "run_group_id": run_group_id,
        "route": ROUTE4_WIKIDATA_TWO_HOP_ROUTE,
        "segments": segments,
        "artifact_index": {
            "accepted_jsonl": sorted({str(row.get("output_path", "")) for row in segments if row.get("output_path")}),
            "rejected_jsonl": sorted({str(row.get("rejected_output_path", "")) for row in segments if row.get("rejected_output_path")}),
            "summary_json": sorted({str(row.get("summary_output", "")) for row in segments if row.get("summary_output")}),
            "final_jsonl": sorted({str(row.get("final_output", "")) for row in segments if row.get("final_output")}),
            "state_json": sorted({str(row.get("state", "")) for row in segments if row.get("state")}),
        },
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    summary["run_group_id"] = run_group_id
    summary["run_segment_id"] = segment["segment_id"]
    summary["run_artifact_manifest"] = str(manifest_path)


def _run_segment_id(args: argparse.Namespace) -> str:
    """Return a stable segment ID for this invocation."""
    explicit = _safe_artifact_id(args.run_segment_id)
    if explicit:
        return explicit
    return _safe_artifact_id(args.summary_output.stem, fallback="segment")


def _safe_artifact_id(value: str, *, fallback: str = "") -> str:
    """Return a path-safe artifact identifier."""
    cleaned = "".join(char if char.isalnum() or char in "._-" else "_" for char in value.strip()).strip("._-")
    return cleaned or fallback


def _optional_proxy(value: str) -> str | None:
    """Normalize CLI proxy values."""
    if value.strip().lower() in {"", "none", "direct", "off"}:
        return None
    return value


if __name__ == "__main__":
    raise SystemExit(main())
