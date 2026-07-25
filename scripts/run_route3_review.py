"""Export and apply the formal Route 3 manual review loop."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.config import LLMConfig, Settings
from wikidata_simpleqa.grading import ModelPanelMember
from wikidata_simpleqa.route3_circuit import ServiceCircuit
from wikidata_simpleqa.route3_openrouter import Route3OpenRouterClientFactory
from wikidata_simpleqa.route3_run_ledger import load_segment_manifest
from wikidata_simpleqa.route3_review import (
    accepted_review_bundles,
    apply_review_rows,
    create_review_state,
    load_review_state,
    post_generation_processor,
    read_review_workbook,
    render_review_markdown,
    rerun_review_candidates,
    write_review_state,
    write_review_workbook,
)
from wikidata_simpleqa.search_client import DuckDuckGoSearchClient


def parse_args() -> argparse.Namespace:
    """Parse review export or apply arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    export = subparsers.add_parser("export", help="Create review state, Markdown, and XLSX from accepted JSONL.")
    export.add_argument("--accepted-input", type=Path, required=True)
    export.add_argument("--segment-manifest", type=Path, action="append", required=True)
    export.add_argument("--state-output", type=Path, required=True)
    export.add_argument("--markdown-output", type=Path, required=True)
    export.add_argument("--xlsx-output", type=Path, required=True)
    export.add_argument("--run-id", required=True)

    apply = subparsers.add_parser("apply", help="Apply XLSX decisions and rerun edited candidates.")
    apply.add_argument("--state-input", type=Path, required=True)
    apply.add_argument("--xlsx-input", type=Path, required=True)
    apply.add_argument("--state-output", type=Path, required=True)
    apply.add_argument("--markdown-output", type=Path, required=True)
    apply.add_argument("--xlsx-output", type=Path, required=True)
    apply.add_argument("--run-id", required=True)
    return parser.parse_args()


def main() -> int:
    """Run the selected review operation."""
    args = parse_args()
    if args.command == "export":
        state = _export_state(args)
    else:
        state = _apply_state(args)
    write_review_state(args.state_output, state)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(
        render_review_markdown(state, run_id=args.run_id),
        encoding="utf-8",
    )
    write_review_workbook(args.xlsx_output, state)
    summary = {
        "run_id": args.run_id,
        "review_state": str(args.state_output),
        "markdown": str(args.markdown_output),
        "xlsx": str(args.xlsx_output),
        "accepted": len(accepted_review_bundles(state)),
        "rerun": _status_count(state, "rerun"),
        "rejected": _status_count(state, "rejected"),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


def _export_state(args: argparse.Namespace) -> dict:
    records = _read_jsonl(args.accepted_input)
    segment_fingerprints: dict[str, dict] = {}
    segment_artifact_roots: dict[str, str] = {}
    for path in args.segment_manifest:
        manifest = load_segment_manifest(path)
        if manifest is None:
            raise ValueError(f"Missing segment manifest: {path}")
        segment_id = str(manifest["segment_id"])
        if segment_id in segment_fingerprints:
            raise ValueError(f"Duplicate segment manifest: {segment_id}")
        segment_fingerprints[segment_id] = manifest["fingerprint"]
        segment_artifact_roots[segment_id] = str(path.parent.resolve())
    return create_review_state(
        records,
        segment_fingerprints=segment_fingerprints,
        segment_artifact_roots=segment_artifact_roots,
    )


def _apply_state(args: argparse.Namespace) -> dict:
    state = load_review_state(args.state_input)
    rows = read_review_workbook(args.xlsx_input)
    state = apply_review_rows(state, rows)
    if _status_count(state, "rerun"):
        processors: dict[str, object] = {}
        openrouter_circuit = ServiceCircuit("openrouter")
        duckduckgo_circuit = ServiceCircuit("duckduckgo")

        def processor(candidate):
            segment_id = str(candidate.source_metadata["segment_id"])
            segment_processor = processors.get(segment_id)
            if segment_processor is None:
                settings = _settings_from_fingerprint(state["segment_fingerprints"][segment_id])
                search_client = DuckDuckGoSearchClient(**settings.duckduckgo_client_kwargs())
                segment_processor = post_generation_processor(
                    settings=settings,
                    search_client=search_client,
                    second_stage_model_clients=_build_route3_model_panel(settings, openrouter_circuit),
                    grading_grader_client=_build_route3_grader(settings, openrouter_circuit),
                    external_call_record_root=(
                        Path(state["segment_artifact_roots"][segment_id]) / "external_calls"
                    ),
                    ddg_verifier_result_root=(
                        Path(state["segment_artifact_roots"][segment_id])
                        / "ddg_verifier_results"
                    ),
                    segment_fingerprint=str(
                        state["segment_fingerprints"][segment_id]["sha256"]
                    ),
                    duckduckgo_circuit=duckduckgo_circuit,
                )
                processors[segment_id] = segment_processor
            return segment_processor(candidate)

        state = rerun_review_candidates(state, processor=processor)
    return state


def _build_route3_model_panel(settings: Settings, circuit: ServiceCircuit) -> list[ModelPanelMember] | None:
    """Build durable answer-model factories for one review rerun."""
    if not settings.second_stage_grading_enabled:
        return None
    members = []
    for config in settings.second_stage_grading_models:
        factory = _route3_openrouter_factory(config, settings, circuit)
        members.append(ModelPanelMember(name=config.model, client=factory))
    return members


def _build_route3_grader(settings: Settings, circuit: ServiceCircuit):
    """Build the durable grader factory for one review rerun."""
    if not settings.second_stage_grading_enabled:
        return None
    config = settings.second_stage_grading_grader_llm
    if config is None:
        return None
    return _route3_openrouter_factory(config, settings, circuit)


def _route3_openrouter_factory(
    config: LLMConfig,
    settings: Settings,
    circuit: ServiceCircuit,
) -> Route3OpenRouterClientFactory:
    """Build one formal OpenRouter factory from reconstructed settings."""
    if config.provider != "openrouter":
        raise ValueError(f"Formal Route 3 requires OpenRouter, got: {config.provider}")
    return Route3OpenRouterClientFactory.from_config(
        config,
        timeout_seconds=settings.timeout_seconds,
        circuit=circuit,
    )


def _settings_from_fingerprint(fingerprint: dict) -> Settings:
    """Reconstruct formal post-generation settings from the segment fingerprint."""
    inputs = fingerprint["inputs"]
    resolved = inputs["resolved_result_affecting_config"]
    duckduckgo = inputs["duckduckgo"]
    second_stage = inputs["second_stage"]
    settings = Settings(
        target_time=str(resolved["target_time"]),
        run_date=str(resolved["run_date"]),
        cutoff_year=int(resolved["cutoff_year"]),
        timeout_seconds=float(resolved["timeout_seconds"]),
        proxy=resolved["proxy"],
        generated_search_query_count=int(resolved["generated_search_query_count"]),
        duckduckgo_top_k=int(duckduckgo["top_k"]),
        duckduckgo_parallel_queries=int(duckduckgo["parallel_queries"]),
        duckduckgo_prefer_ddgs=bool(duckduckgo["duckduckgo_prefer_ddgs"]),
        duckduckgo_ddgs_backend=str(duckduckgo["duckduckgo_ddgs_backend"]),
        duckduckgo_ddgs_max_attempts=int(duckduckgo["duckduckgo_ddgs_max_attempts"]),
        duckduckgo_disable_fallbacks=tuple(duckduckgo["duckduckgo_disable_fallbacks"]),
        duckduckgo_cooldown_enabled=bool(duckduckgo["duckduckgo_cooldown_enabled"]),
        duckduckgo_cooldown_failure_threshold=int(duckduckgo["duckduckgo_cooldown_failure_threshold"]),
        duckduckgo_cooldown_initial_seconds=float(duckduckgo["duckduckgo_cooldown_initial_seconds"]),
        duckduckgo_cooldown_max_seconds=float(duckduckgo["duckduckgo_cooldown_max_seconds"]),
        search_longtail_max_full_question_hit_rate=float(duckduckgo["max_full_question_hit_rate"]),
        search_longtail_max_keyword_hit_rate=float(duckduckgo["max_keyword_hit_rate"]),
        search_longtail_max_overall_hit_rate=float(duckduckgo["max_overall_hit_rate"]),
        second_stage_grading_enabled=bool(second_stage["enabled"]),
        second_stage_grading_accuracy_threshold=float(second_stage["accuracy_threshold"]),
        enabled_routes=("route3_wikipedia_infobox",),
        rewrite_enabled=False,
        rewrite_llm=None,
    )
    for llm in (*settings.second_stage_grading_models, settings.second_stage_grading_grader_llm):
        if llm is not None:
            llm.proxy = settings.proxy
    return settings


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _status_count(state: dict, status: str) -> int:
    count = 0
    for bundle in state["candidates"]:
        revisions = bundle["artifact"]["revisions"]
        if revisions[-1]["status"] == status:
            count += 1
    return count


if __name__ == "__main__":
    raise SystemExit(main())
