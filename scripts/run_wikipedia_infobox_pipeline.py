"""Run the Wikipedia infobox/table QA route over supplied page URLs."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.cheap_model_qa import make_cheap_model_qa_client
from wikidata_simpleqa.config import LLMConfig, Settings
from wikidata_simpleqa.generation_pipeline import process_generated_candidates
from wikidata_simpleqa.io import write_jsonl
from wikidata_simpleqa.llm_rewrite import make_rewrite_client
from wikidata_simpleqa.search_client import DuckDuckGoSearchClient
from wikidata_simpleqa.wikipedia_client import WikipediaClient, normalize_wikipedia_title
from wikidata_simpleqa.wikipedia_infobox_generator import WikipediaInfoboxTableGenerator


@dataclass(slots=True)
class UrlEntry:
    """One Wikipedia URL and its optional broad content domain."""

    url: str
    domain: str = ""


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the Wikipedia table route."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", action="append", default=[], help="Wikipedia URL. Can be repeated.")
    parser.add_argument("--url-file", type=Path, default=None, help="Text file with one Wikipedia URL per line.")
    parser.add_argument("--record-limit", type=int, default=10)
    parser.add_argument("--target-time", type=str, default="2024")
    parser.add_argument("--run-date", type=str, default=None)
    parser.add_argument("--cutoff-year", type=int, default=2025)
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--duckduckgo-top-k", type=int, default=10)
    parser.add_argument("--proxy", type=str, default="socks5://127.0.0.1:7897")
    parser.add_argument("--small-model-provider", type=str, default="openrouter")
    parser.add_argument("--small-model", type=str, default="openai/gpt-4.1-mini")
    parser.add_argument("--small-model-api-key-env", type=str, default="OPENROUTER_API_KEY")
    parser.add_argument("--small-model-base-url", type=str, default="https://openrouter.ai/api/v1")
    parser.add_argument("--small-model-max-tokens", type=int, default=1200)
    parser.add_argument("--enable-rewrite", action="store_true")
    parser.add_argument("--rewrite-model", type=str, default="openai/gpt-4.1-mini")
    parser.add_argument("--enable-second-stage-grading", action="store_true")
    parser.add_argument("--second-stage-grading-accuracy-threshold", type=float, default=0.1)
    parser.add_argument("--search-longtail-max-full-question-hit-rate", type=float, default=0.0)
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
    url_entries = _load_url_entries(args.url, args.url_file)
    urls = [entry.url for entry in url_entries]
    if not urls:
        raise ValueError("Provide at least one Wikipedia URL with --url or --url-file.")
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
        pilot_total=args.record_limit,
        cutoff_year=args.cutoff_year,
        timeout_seconds=args.timeout_seconds,
        duckduckgo_top_k=args.duckduckgo_top_k,
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
    generator = WikipediaInfoboxTableGenerator(
        urls=urls,
        wikipedia_client=wikipedia_client,
        llm_client=llm_client,
        record_limit=args.record_limit,
        url_domains=_url_domain_map(url_entries),
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
    write_jsonl(args.output, result.accepted)
    write_jsonl(args.rejected_output, result.rejected)
    summary = {
        "attempted_urls": min(len(urls), args.record_limit),
        "url_domains": [
            {"url": entry.url, "domain": entry.domain}
            for entry in url_entries[: args.record_limit]
        ],
        "generated": len(generated_candidates),
        "accepted": len(result.accepted),
        "rejected": len(result.rejected),
        "output_path": str(args.output),
        "rejected_output_path": str(args.rejected_output),
        "summary_output": str(args.summary_output),
        "enabled_routes": list(settings.enabled_routes),
        "small_model": args.small_model,
        "rewrite_enabled": settings.rewrite_enabled,
        "second_stage_grading_enabled": settings.second_stage_grading_enabled,
        "aggregate_phase_timings_seconds": _aggregate_phase_timings(result.accepted, result.rejected),
        "telemetry": {
            **result.telemetry,
            "wikipedia": wikipedia_client.request_events.copy(),
            "search": search_client.request_events.copy(),
        },
    }
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


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
    """Parse ``url`` or ``domain<TAB>url`` lines from a Route 3 URL file."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    if "\t" in stripped:
        domain, url = stripped.split("\t", 1)
        return UrlEntry(url=url.strip(), domain=domain.strip())
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
