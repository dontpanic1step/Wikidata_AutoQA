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
from wikidata_simpleqa.generation_models import EntityReference, EvidenceRecord, GeneratedCandidate
from wikidata_simpleqa.generation_pipeline import process_generated_candidates
from wikidata_simpleqa.io import write_jsonl
from wikidata_simpleqa.llm_rewrite import make_rewrite_client
from wikidata_simpleqa.search_client import DuckDuckGoSearchClient
from wikidata_simpleqa.wikipedia_client import WikipediaClient, normalize_wikipedia_title
from wikidata_simpleqa.wikipedia_infobox_generator import (
    WikipediaInfoboxTableGenerator,
    _answer_items,
    _normalize_answer_type,
    _normalize_generated_answer,
    _sanitize_answer_blind_queries,
)


@dataclass(slots=True)
class UrlEntry:
    """One Wikipedia URL and its optional broad content domain."""

    url: str
    domain: str = ""
    subdomain: str = ""


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the Wikipedia table route."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", action="append", default=[], help="Wikipedia URL. Can be repeated.")
    parser.add_argument("--url-file", type=Path, default=None, help="Text file with one Wikipedia URL per line.")
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
    parser.add_argument("--record-limit", type=int, default=10)
    parser.add_argument("--target-time", type=str, default="2024")
    parser.add_argument("--run-date", type=str, default=None)
    parser.add_argument("--cutoff-year", type=int, default=2025)
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--duckduckgo-top-k", type=int, default=10)
    parser.add_argument("--duckduckgo-parallel-queries", type=int, default=3)
    parser.add_argument("--generated-search-query-count", type=int, default=3)
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
    url_entries = _load_url_entries(args.url, args.url_file)
    urls = [entry.url for entry in url_entries]
    if args.start_stage == "generate" and not urls:
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
        pilot_total=args.record_limit,
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
    if args.start_stage == "validation":
        generated_candidates = _load_candidate_inputs(args.candidate_input, limit=args.record_limit)
        if not generated_candidates:
            raise ValueError("No candidates were loaded from --candidate-input.")
        if not url_entries:
            url_entries = _url_entries_from_candidates(generated_candidates)
    else:
        generator = WikipediaInfoboxTableGenerator(
            urls=urls,
            wikipedia_client=wikipedia_client,
            llm_client=llm_client,
            record_limit=args.record_limit,
            url_domains=_url_domain_map(url_entries),
            search_query_count=args.generated_search_query_count,
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
        "start_stage": args.start_stage,
        "candidate_input_paths": [str(path) for path in args.candidate_input],
        "attempted_urls": (
            min(len(urls), args.record_limit)
            if args.start_stage == "generate"
            else len(generated_candidates)
        ),
        "url_domains": [
            {"url": entry.url, "domain": entry.domain}
            | ({"subdomain": entry.subdomain} if entry.subdomain else {})
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
        "duckduckgo_parallel_queries": settings.duckduckgo_parallel_queries,
        "generated_search_query_count": settings.generated_search_query_count,
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

    question = str(record.get("rewritten_question") or record.get("question") or "").strip()
    answer = str(record.get("answer") or "").strip()
    answer_aliases = _string_list(record.get("answer_aliases", []))
    answer_type = str(record.get("answer_type") or source_metadata.get("answer_type") or "").strip()
    search_queries = _string_list(record.get("search_queries", []))
    relation_or_claim = str(record.get("relation_or_claim") or "wikipedia_table_composition").strip()

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
        relation_or_claim = str(llm_response.get("composition_type") or relation_or_claim).strip()

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
        relation_or_claim=relation_or_claim or "wikipedia_table_composition",
        evidence=evidence,
        question_family=str(record.get("question_family") or "wikipedia_infobox_table_composition"),
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
