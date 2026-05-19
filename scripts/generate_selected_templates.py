"""Generate examples for selected template keys."""

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
from wikidata_simpleqa.domain_templates import get_template_by_key
from wikidata_simpleqa.generation_pipeline import run_generation_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-time", type=str, required=True)
    parser.add_argument("--date-upper-bound", type=str, default=None)
    parser.add_argument("--template-keys", "--domains", dest="template_keys", nargs="+", required=True)
    parser.add_argument("--pilot-total", type=int, default=10)
    parser.add_argument("--harvest-limit", type=int, default=10)
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--duckduckgo-top-k", type=int, default=10)
    parser.add_argument("--proxy", type=str, default="socks5://127.0.0.1:7897")
    parser.add_argument("--disable-route1-light-fallback", action="store_true")
    parser.add_argument(
        "--route1-subject-seed-window-granularity",
        choices=["year", "month", "day"],
        default="year",
    )
    parser.add_argument("--enable-rewrite", action="store_true")
    parser.add_argument("--rewrite-provider", type=str, default="openrouter")
    parser.add_argument("--rewrite-model", type=str, default="openai/gpt-4.1-mini")
    parser.add_argument("--rewrite-api-key-env", type=str, default="OPENROUTER_API_KEY")
    parser.add_argument("--rewrite-base-url", type=str, default="https://openrouter.ai/api/v1")
    parser.add_argument("--enable-second-stage-grading", action="store_true")
    parser.add_argument("--second-stage-grading-accuracy-threshold", type=float, default=0.5)
    parser.add_argument("--search-longtail-max-full-question-hit-rate", type=float, default=0.3)
    parser.add_argument("--search-longtail-max-keyword-hit-rate", type=float, default=0.3)
    parser.add_argument("--search-longtail-max-overall-hit-rate", type=float, default=0.3)
    parser.add_argument(
        "--live-probe-mode",
        action="store_true",
        help="Use smaller harvest and hydration batches plus checkpoint logs for live debugging probes.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs" / "selected_templates_accepted.jsonl",
    )
    parser.add_argument(
        "--rejected-output",
        type=Path,
        default=ROOT / "outputs" / "selected_templates_rejected.jsonl",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=ROOT / "outputs" / "selected_templates_summary.json",
    )
    return parser.parse_args()


def _optional_proxy(value: str) -> str | None:
    """Normalize CLI proxy values."""
    if value.strip().lower() in {"", "none", "direct", "off"}:
        return None
    return value


def main() -> int:
    args = parse_args()
    templates = []
    for template_key in args.template_keys:
        template = get_template_by_key(template_key)
        if template is None:
            raise ValueError(f"Unknown template key: {template_key}")
        templates.append(template)
    proxy = _optional_proxy(args.proxy)
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
        pilot_total=args.pilot_total,
        harvest_limit_per_template=args.harvest_limit,
        timeout_seconds=args.timeout_seconds,
        duckduckgo_top_k=args.duckduckgo_top_k,
        search_longtail_max_full_question_hit_rate=args.search_longtail_max_full_question_hit_rate,
        search_longtail_max_keyword_hit_rate=args.search_longtail_max_keyword_hit_rate,
        search_longtail_max_overall_hit_rate=args.search_longtail_max_overall_hit_rate,
        second_stage_grading_enabled=args.enable_second_stage_grading,
        second_stage_grading_accuracy_threshold=args.second_stage_grading_accuracy_threshold,
        enabled_routes=("route1_wikidata_light",),
        proxy=proxy,
        route1_light_fallback_enabled=not args.disable_route1_light_fallback,
        route1_subject_seed_window_granularity=args.route1_subject_seed_window_granularity,
        live_probe_mode=args.live_probe_mode,
        output_path=args.output,
        rejected_output_path=args.rejected_output,
        rewrite_enabled=args.enable_rewrite,
        rewrite_llm=rewrite_llm,
    )
    result = run_generation_pipeline(settings=settings, templates=templates)
    summary = {
        "accepted": len(result.accepted),
        "rejected": len(result.rejected),
        "template_keys": args.template_keys,
        "output_path": str(args.output),
        "rejected_output_path": str(args.rejected_output),
        "summary_output": str(args.summary_output),
        "settings": {
            "target_time": settings.target_time,
            "date_upper_bound": settings.date_upper_bound,
            "pilot_total": settings.pilot_total,
            "harvest_limit_per_template": settings.harvest_limit_per_template,
            "timeout_seconds": settings.timeout_seconds,
            "route1_subject_seed_window_granularity": settings.route1_subject_seed_window_granularity,
            "enabled_routes": list(settings.enabled_routes),
            "duckduckgo_top_k": settings.duckduckgo_top_k,
            "search_longtail_thresholds": {
                "full_question": settings.search_longtail_max_full_question_hit_rate,
                "keyword_queries": settings.search_longtail_max_keyword_hit_rate,
                "overall": settings.search_longtail_max_overall_hit_rate,
            },
            "rewrite_enabled": settings.rewrite_enabled,
            "second_stage_grading_enabled": settings.second_stage_grading_enabled,
            "second_stage_grading_accuracy_threshold": settings.second_stage_grading_accuracy_threshold,
            "second_stage_grading_models": [
                config.model for config in settings.second_stage_grading_models
            ],
            "second_stage_grader_model": (
                settings.second_stage_grading_grader_llm.model
                if settings.second_stage_grading_grader_llm is not None
                else None
            ),
        },
        "telemetry": result.telemetry,
    }
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
