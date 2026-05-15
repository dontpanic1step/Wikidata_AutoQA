"""Generate a Stage 1 pilot dataset."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.config import Settings
from wikidata_simpleqa.config import LLMConfig
from wikidata_simpleqa.generation_pipeline import run_generation_pipeline


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for pilot generation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-time", type=str, required=True)
    parser.add_argument("--run-date", type=str, default=None)
    parser.add_argument("--pilot-total", type=int, default=20)
    parser.add_argument("--harvest-limit", type=int, default=100)
    parser.add_argument("--cutoff-year", type=int, default=2025)
    parser.add_argument("--duckduckgo-top-k", type=int, default=5)
    parser.add_argument("--proxy", type=str, default="socks5://127.0.0.1:7897")
    parser.add_argument("--disable-route1-light-fallback", action="store_true")
    parser.add_argument("--enable-rewrite", action="store_true")
    parser.add_argument("--rewrite-provider", type=str, default="openrouter")
    parser.add_argument("--rewrite-model", type=str, default="openai/gpt-4.1-mini")
    parser.add_argument("--rewrite-api-key-env", type=str, default="OPENROUTER_API_KEY")
    parser.add_argument("--rewrite-base-url", type=str, default="https://openrouter.ai/api/v1")
    parser.add_argument("--snippet-judge-provider", type=str, default="openrouter")
    parser.add_argument("--snippet-judge-model", type=str, default="openai/gpt-4.1-mini")
    parser.add_argument("--snippet-judge-api-key-env", type=str, default="OPENROUTER_API_KEY")
    parser.add_argument("--snippet-judge-base-url", type=str, default="https://openrouter.ai/api/v1")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs" / "pilot_accepted.jsonl",
    )
    parser.add_argument(
        "--rejected-output",
        type=Path,
        default=ROOT / "outputs" / "pilot_rejected.jsonl",
    )
    return parser.parse_args()


def main() -> int:
    """Run the Stage 1 pipeline from the command line."""
    args = parse_args()
    rewrite_llm = None
    if args.enable_rewrite:
        rewrite_llm = LLMConfig(
            provider=args.rewrite_provider,
            model=args.rewrite_model,
            api_key_env=args.rewrite_api_key_env,
            base_url=args.rewrite_base_url,
            proxy=args.proxy,
        )
    snippet_judge_llm = LLMConfig(
        provider=args.snippet_judge_provider,
        model=args.snippet_judge_model,
        api_key_env=args.snippet_judge_api_key_env,
        base_url=args.snippet_judge_base_url,
        proxy=args.proxy,
        temperature=0.0,
        max_tokens=128,
    )
    settings = Settings(
        target_time=args.target_time,
        run_date=args.run_date or Settings(target_time=args.target_time).run_date,
        pilot_total=args.pilot_total,
        harvest_limit_per_template=args.harvest_limit,
        cutoff_year=args.cutoff_year,
        duckduckgo_top_k=args.duckduckgo_top_k,
        route1_light_fallback_enabled=not args.disable_route1_light_fallback,
        number_snippet_judge_llm=snippet_judge_llm,
        proxy=args.proxy,
        output_path=args.output,
        rejected_output_path=args.rejected_output,
        rewrite_enabled=args.enable_rewrite,
        rewrite_llm=rewrite_llm,
    )
    result = run_generation_pipeline(settings)
    summary = {
        "accepted": len(result.accepted),
        "rejected": len(result.rejected),
        "output_path": str(settings.output_path),
        "rejected_output_path": str(settings.rejected_output_path),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
