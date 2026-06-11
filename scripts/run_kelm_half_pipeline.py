"""Run a 10-record KELM half-pipeline focused on long-tail filtering."""

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
from wikidata_simpleqa.generation_pipeline import process_generated_candidates
from wikidata_simpleqa.io import write_jsonl
from wikidata_simpleqa.kelm_generator import KELMTSVGenerator
from wikidata_simpleqa.llm_rewrite import make_rewrite_client
from wikidata_simpleqa.search_cli import (
    add_duckduckgo_transport_args,
    duckduckgo_settings_kwargs,
    duckduckgo_summary_fields,
)
from wikidata_simpleqa.search_client import DuckDuckGoSearchClient
from wikidata_simpleqa.wikidata_client import WikidataClient


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the KELM half-pipeline."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "data" / "kelm" / "quadruples-train.tsv",
    )
    parser.add_argument("--record-limit", type=int, default=10)
    parser.add_argument("--run-date", type=str, default=None)
    parser.add_argument("--cutoff-year", type=int, default=2025)
    parser.add_argument("--duckduckgo-top-k", type=int, default=5)
    add_duckduckgo_transport_args(parser)
    parser.add_argument("--search-longtail-max-full-question-hit-rate", type=float, default=0.3)
    parser.add_argument("--search-longtail-max-keyword-hit-rate", type=float, default=0.3)
    parser.add_argument("--search-longtail-max-overall-hit-rate", type=float, default=0.3)
    parser.add_argument("--proxy", type=str, default="none")
    parser.add_argument("--enable-kelm-rewrite", dest="enable_kelm_rewrite", action="store_true")
    parser.add_argument(
        "--enable-rewrite",
        dest="enable_kelm_rewrite",
        action="store_true",
        default=argparse.SUPPRESS,
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--rewrite-provider", type=str, default="openrouter")
    parser.add_argument("--kelm-rewrite-model", dest="kelm_rewrite_model", type=str, default="openai/gpt-4.1-mini")
    parser.add_argument(
        "--rewrite-model",
        dest="kelm_rewrite_model",
        type=str,
        default=argparse.SUPPRESS,
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--rewrite-api-key-env", type=str, default="OPENROUTER_API_KEY")
    parser.add_argument("--rewrite-base-url", type=str, default="https://openrouter.ai/api/v1")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs" / "kelm_half_pipeline_accepted.jsonl",
    )
    parser.add_argument(
        "--rejected-output",
        type=Path,
        default=ROOT / "outputs" / "kelm_half_pipeline_rejected.jsonl",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=ROOT / "outputs" / "kelm_half_pipeline_summary.json",
    )
    return parser.parse_args()


def main() -> int:
    """Run the small KELM half-pipeline and persist outputs."""
    args = parse_args()
    rewrite_llm = None
    if args.enable_kelm_rewrite:
        rewrite_llm = LLMConfig(
            provider=args.rewrite_provider,
            model=args.kelm_rewrite_model,
            api_key_env=args.rewrite_api_key_env,
            base_url=args.rewrite_base_url,
            proxy=args.proxy,
        )
    settings = Settings(
        target_time="2024",
        run_date=args.run_date or Settings(target_time="2024").run_date,
        pilot_total=args.record_limit,
        cutoff_year=args.cutoff_year,
        duckduckgo_top_k=args.duckduckgo_top_k,
        search_longtail_max_full_question_hit_rate=args.search_longtail_max_full_question_hit_rate,
        search_longtail_max_keyword_hit_rate=args.search_longtail_max_keyword_hit_rate,
        search_longtail_max_overall_hit_rate=args.search_longtail_max_overall_hit_rate,
        proxy=args.proxy,
        output_path=args.output,
        rejected_output_path=args.rejected_output,
        rewrite_enabled=args.enable_kelm_rewrite,
        rewrite_llm=rewrite_llm,
        **duckduckgo_settings_kwargs(args),
    )
    client = WikidataClient(
        user_agent=settings.user_agent,
        proxy=settings.proxy,
        timeout_seconds=settings.timeout_seconds,
        cache_dir=settings.cache_dir,
    )
    search_client = DuckDuckGoSearchClient(**settings.duckduckgo_client_kwargs())
    rewrite_client = None
    if settings.rewrite_enabled:
        rewrite_client = make_rewrite_client(settings.rewrite_llm, settings.timeout_seconds)
    generator = KELMTSVGenerator(
        input_path=args.input,
        record_limit=args.record_limit,
    )
    generated_candidates = generator.generate(client=client, run_date=settings.run_date)
    result = process_generated_candidates(
        generated_candidates,
        settings=settings,
        search_client=search_client,
        rewrite_client=rewrite_client,
    )
    summary = {
        "generated": len(generated_candidates),
        "accepted": len(result.accepted),
        "rejected": len(result.rejected),
        "input_path": str(args.input),
        "output_path": str(args.output),
        "rejected_output_path": str(args.rejected_output),
        "kelm_rewrite_enabled": bool(args.enable_kelm_rewrite),
        "kelm_rewrite_model": args.kelm_rewrite_model if args.enable_kelm_rewrite else "",
        "rewrite_enabled": bool(args.enable_kelm_rewrite),
        **duckduckgo_summary_fields(settings),
        "telemetry": result.telemetry,
    }
    write_jsonl(args.output, result.accepted)
    write_jsonl(args.rejected_output, result.rejected)
    args.summary_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
