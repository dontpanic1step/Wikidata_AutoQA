#!/usr/bin/env python3
"""Probe Route 3 DuckDuckGo behavior with the production verifier path.

This script intentionally calls run_search_based_longtail_verifier instead of
issuing ad hoc search_client.search calls. The goal is to exercise the same
DuckDuckGo query planning, parallel query execution, hit accounting, and error
wrapping used by the Route 3 pipeline.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from time import perf_counter
from typing import Any

from scripts.run_wikipedia_infobox_pipeline import _candidate_from_record
from wikidata_simpleqa.config import Settings
from wikidata_simpleqa.generation_models import EntityReference, EvidenceRecord, GeneratedCandidate
from wikidata_simpleqa.generator_validators import SearchLongtailVerifierError, run_search_based_longtail_verifier
from wikidata_simpleqa.search_client import DuckDuckGoSearchClient


def iter_jsonl(path: Path):
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            yield line_number, row


def _phase_seconds(record: dict[str, Any], key: str) -> float:
    timings = (record.get("source_metadata") or {}).get("phase_timings_seconds") or {}
    try:
        return float(timings.get(key) or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _has_full_candidate_metadata(record: dict[str, Any]) -> bool:
    metadata = record.get("source_metadata") or {}
    return isinstance(metadata.get("llm_response"), dict) or bool(record.get("subject_entity"))


def _compact_candidate_from_rejected(record: dict[str, Any], *, fallback_answer_type: str) -> GeneratedCandidate:
    """Build the best available candidate from compact rejected endpoint rows.

    Compact rejected rows in tmp_rowfilter_snapshot_2026_06_03 retain the real
    final question but not the generated keyword search queries. The full
    question remains an exact verifier query; fallback keyword queries are
    marked in the probe metadata as lower-fidelity reconstruction.
    """
    metadata = dict(record.get("source_metadata") or {})
    page_title = str(metadata.get("page_title") or record.get("page_title") or "").strip()
    page_url = str(record.get("page_url") or metadata.get("canonical_url") or "").strip()
    answer = str(record.get("answer") or "").strip()
    return GeneratedCandidate(
        source_type=str(record.get("source_type") or "wikipedia_tables"),
        generation_route=str(record.get("generation_route") or "route3_wikipedia_infobox"),
        question=str(record.get("question") or "").strip(),
        canonical_question=str(record.get("canonical_question") or record.get("question") or "").strip(),
        rewritten_question=str(record.get("rewritten_question") or record.get("question") or "").strip(),
        answer=answer,
        answer_aliases=[str(alias).strip() for alias in record.get("answer_aliases", []) if str(alias).strip()]
        if isinstance(record.get("answer_aliases"), list)
        else [],
        subject_entity=EntityReference(
            name=page_title,
            wikipedia_title=page_title.replace(" ", "_"),
            url=page_url,
        ),
        answer_entity=EntityReference(name=answer),
        relation_or_claim=str(metadata.get("reasoning_type") or record.get("reasoning_type") or "wikipedia_table_fact"),
        evidence=EvidenceRecord(
            text=str(metadata.get("first_paragraph") or ""),
            url=page_url,
            source_title=page_title,
        ),
        question_family=str(record.get("question_family") or "wikipedia_infobox_table_fact"),
        answer_type=str(record.get("answer_type") or metadata.get("answer_type") or fallback_answer_type),
        topic=str(record.get("topic") or "Wikipedia semi-structured data"),
        target_time=str(record.get("target_time") or ""),
        source_template_domain=str(record.get("template_key") or "wikipedia_infobox_table"),
        search_queries=[],
        source_metadata=metadata,
    )


def candidate_from_record(record: dict[str, Any], *, fallback_answer_type: str) -> tuple[GeneratedCandidate, str]:
    """Return a candidate and reconstruction-quality label."""
    if _has_full_candidate_metadata(record):
        candidate = _candidate_from_record(record)
        return candidate, "exact_candidate_reconstruction"
    return (
        _compact_candidate_from_rejected(record, fallback_answer_type=fallback_answer_type),
        "compact_rejected_full_question_probe",
    )


def collect_records(
    accepted_paths: list[Path],
    rejected_paths: list[Path],
    *,
    accepted_limit: int,
    rejected_limit: int,
    rejected_min_duckduckgo_seconds: float,
) -> list[dict[str, Any]]:
    """Collect accepted rows first, then compact rejected rows that reached DDG."""
    selected: list[dict[str, Any]] = []
    seen_questions: set[str] = set()

    if accepted_limit > 0:
        for path in accepted_paths:
            for line_number, record in iter_jsonl(path):
                if sum(1 for row in selected if row["source_kind"] == "accepted") >= accepted_limit:
                    break
                question = str(record.get("question") or "").strip()
                if not question or question in seen_questions:
                    continue
                seen_questions.add(question)
                selected.append(
                    {
                        "source_file": str(path),
                        "source_line": line_number,
                        "source_kind": "accepted",
                        "record": record,
                    }
                )

    rejected_candidates: list[tuple[float, Path, int, dict[str, Any]]] = []
    if rejected_limit > 0:
        for path in rejected_paths:
            for line_number, record in iter_jsonl(path):
                question = str(record.get("question") or "").strip()
                if not question or question in seen_questions:
                    continue
                ddg_seconds = _phase_seconds(record, "duckduckgo_search_seconds")
                if ddg_seconds <= rejected_min_duckduckgo_seconds:
                    continue
                rejected_candidates.append((ddg_seconds, path, line_number, record))
        rejected_candidates.sort(key=lambda item: item[0], reverse=True)
        for _, path, line_number, record in rejected_candidates[:rejected_limit]:
            seen_questions.add(str(record.get("question") or "").strip())
            selected.append(
                {
                    "source_file": str(path),
                    "source_line": line_number,
                    "source_kind": "rejected",
                    "record": record,
                }
            )
    return selected


def run_one_probe(
    item: dict[str, Any],
    *,
    search_client: DuckDuckGoSearchClient,
    settings: Settings,
    fallback_answer_type: str,
) -> dict[str, Any]:
    """Run the production long-tail verifier for one reconstructed candidate."""
    record = item["record"]
    candidate, reconstruction_quality = candidate_from_record(record, fallback_answer_type=fallback_answer_type)
    started = perf_counter()
    try:
        passed, features = run_search_based_longtail_verifier(
            candidate,
            search_client=search_client,
            snippet_judge_client=None,
            top_k=settings.duckduckgo_top_k,
            max_full_question_hit_rate=settings.search_longtail_max_full_question_hit_rate,
            max_keyword_hit_rate=settings.search_longtail_max_keyword_hit_rate,
            max_overall_hit_rate=settings.search_longtail_max_overall_hit_rate,
            max_parallel_queries=settings.duckduckgo_parallel_queries,
        )
        ok = True
        exception_payload: dict[str, Any] = {}
    except SearchLongtailVerifierError as exc:
        passed = False
        features = exc.features
        ok = False
        exception_payload = {
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "original_error_type": type(getattr(exc, "original_error", exc)).__name__,
            "original_error_message": str(getattr(exc, "original_error", exc)),
        }
    except Exception as exc:  # noqa: BLE001
        passed = False
        features = {}
        ok = False
        exception_payload = {
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
        }

    metadata = record.get("source_metadata") or {}
    return {
        "source_file": item["source_file"],
        "source_line": item["source_line"],
        "source_kind": item["source_kind"],
        "reconstruction_quality": reconstruction_quality,
        "compact_rejected_note": (
            "Full question is exact; generated keyword search_queries are unavailable in compact rejected rows."
            if reconstruction_quality == "compact_rejected_full_question_probe"
            else ""
        ),
        "page_title": metadata.get("page_title") or candidate.subject_entity.name,
        "question": candidate.final_question,
        "answer": candidate.answer,
        "answer_aliases": candidate.answer_aliases,
        "answer_type": candidate.answer_type,
        "subject_entity": {
            "name": candidate.subject_entity.name,
            "url": candidate.subject_entity.url,
        },
        "relation_or_claim": candidate.relation_or_claim,
        "search_queries_on_candidate": candidate.search_queries,
        "prior_duckduckgo_search_seconds": _phase_seconds(record, "duckduckgo_search_seconds"),
        "duration_seconds": round(perf_counter() - started, 4),
        "ok": ok,
        "passed": bool(passed),
        **exception_payload,
        "features": features,
    }


def _attempt_rows(probe_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for candidate_index, result in enumerate(probe_results, start=1):
        for query in (result.get("features") or {}).get("queries", []):
            for event in query.get("search_request_events", []):
                for attempt in event.get("attempts", []):
                    rows.append(
                        {
                            "candidate_index": candidate_index,
                            "source_kind": result.get("source_kind", ""),
                            "query_name": query.get("query_name", ""),
                            "query": query.get("query", ""),
                            **attempt,
                        }
                    )
    return rows


def summarize(probe_results: list[dict[str, Any]], *, settings: Settings, proxy_arg: str) -> dict[str, Any]:
    """Return compact aggregate diagnostics for the probe."""
    query_rows: list[dict[str, Any]] = []
    query_errors: list[dict[str, Any]] = []
    for result in probe_results:
        features = result.get("features") or {}
        query_rows.extend(features.get("queries", []))
        query_errors.extend(features.get("query_errors", []))

    attempts = _attempt_rows(probe_results)
    endpoint_counter = Counter(str(row.get("endpoint") or "") for row in attempts)
    path_counter = Counter(str(row.get("path") or "") for row in attempts)
    error_counter = Counter(
        f"{row.get('error_type')}:{row.get('http_status', row.get('status', ''))}:{row.get('endpoint')}:{row.get('path')}"
        for row in attempts
        if not row.get("ok")
    )
    lite_switch_count = sum(1 for row in attempts if row.get("switched_to_endpoint") == "lite")
    used_lite_query_count = sum(
        1
        for query in query_rows
        if any(
            attempt.get("endpoint") == "lite" or attempt.get("switched_to_endpoint") == "lite"
            for event in query.get("search_request_events", [])
            for attempt in event.get("attempts", [])
        )
    )
    return {
        "candidate_count": len(probe_results),
        "ok_candidate_count": sum(1 for row in probe_results if row.get("ok")),
        "error_candidate_count": sum(1 for row in probe_results if not row.get("ok")),
        "passed_candidate_count": sum(1 for row in probe_results if row.get("passed")),
        "query_count": len(query_rows),
        "query_error_count": len(query_errors),
        "result_count_total": sum(int(row.get("result_count") or 0) for row in query_rows),
        "zero_result_query_count": sum(
            1 for row in query_rows if not row.get("error") and int(row.get("result_count") or 0) == 0
        ),
        "used_lite_query_count": used_lite_query_count,
        "html_202_switch_count": lite_switch_count,
        "attempt_endpoint_counts": endpoint_counter.most_common(),
        "attempt_path_counts": path_counter.most_common(),
        "attempt_error_counts": error_counter.most_common(20),
        "query_errors": [
            {
                "query_name": row.get("query_name"),
                "query": row.get("query"),
                "error_type": row.get("error_type"),
                "error_message": row.get("error_message"),
            }
            for row in query_errors[:20]
        ],
        "effective_settings": {
            "user_agent": settings.user_agent,
            "proxy_arg": proxy_arg,
            "proxy_effective": settings.proxy,
            "timeout_seconds": settings.timeout_seconds,
            "duckduckgo_top_k": settings.duckduckgo_top_k,
            "duckduckgo_parallel_queries": settings.duckduckgo_parallel_queries,
            "search_longtail_max_full_question_hit_rate": settings.search_longtail_max_full_question_hit_rate,
            "search_longtail_max_keyword_hit_rate": settings.search_longtail_max_keyword_hit_rate,
            "search_longtail_max_overall_hit_rate": settings.search_longtail_max_overall_hit_rate,
            "cache_dir": str(settings.cache_dir),
        },
    }


def _optional_proxy(value: str) -> str | None:
    normalized = str(value or "").strip()
    if normalized.lower() in {"", "none", "direct", "no"}:
        return None
    return normalized


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accepted-jsonl", action="append", default=[], type=Path)
    parser.add_argument("--rejected-jsonl", action="append", default=[], type=Path)
    parser.add_argument("--output", type=Path, default=Path("tmp_duckduckgo_route3_verifier_probe.json"))
    parser.add_argument("--accepted-limit", type=int, default=4)
    parser.add_argument("--rejected-limit", type=int, default=4)
    parser.add_argument("--rejected-min-duckduckgo-seconds", type=float, default=0.0)
    parser.add_argument("--fallback-answer-type", default="Place")
    parser.add_argument("--target-time", default="2024")
    parser.add_argument("--run-date", default=None)
    parser.add_argument("--cutoff-year", type=int, default=2025)
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--proxy", default="none")
    parser.add_argument("--duckduckgo-top-k", type=int, default=5)
    parser.add_argument("--duckduckgo-parallel-queries", type=int, default=3)
    parser.add_argument("--search-longtail-max-full-question-hit-rate", type=float, default=0.3)
    parser.add_argument("--search-longtail-max-keyword-hit-rate", type=float, default=0.3)
    parser.add_argument("--search-longtail-max-overall-hit-rate", type=float, default=0.3)
    parser.add_argument("--cache-dir", type=Path, default=Path("cache/wikidata"))
    parser.add_argument("--user-agent", default="")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.accepted_jsonl and not args.rejected_jsonl:
        raise SystemExit("Provide --accepted-jsonl and/or --rejected-jsonl")

    settings = Settings(
        target_time=args.target_time,
        run_date=args.run_date or Settings(target_time=args.target_time).run_date,
        cutoff_year=args.cutoff_year,
        timeout_seconds=args.timeout_seconds,
        duckduckgo_top_k=args.duckduckgo_top_k,
        duckduckgo_parallel_queries=args.duckduckgo_parallel_queries,
        search_longtail_max_full_question_hit_rate=args.search_longtail_max_full_question_hit_rate,
        search_longtail_max_keyword_hit_rate=args.search_longtail_max_keyword_hit_rate,
        search_longtail_max_overall_hit_rate=args.search_longtail_max_overall_hit_rate,
        proxy=_optional_proxy(args.proxy),
    )
    settings.cache_dir = args.cache_dir
    if args.user_agent.strip():
        settings.user_agent = args.user_agent.strip()

    items = collect_records(
        args.accepted_jsonl,
        args.rejected_jsonl,
        accepted_limit=max(0, int(args.accepted_limit)),
        rejected_limit=max(0, int(args.rejected_limit)),
        rejected_min_duckduckgo_seconds=float(args.rejected_min_duckduckgo_seconds),
    )
    search_client = DuckDuckGoSearchClient(
        user_agent=settings.user_agent,
        proxy=settings.proxy,
        timeout_seconds=settings.timeout_seconds,
        cache_dir=settings.cache_dir,
    )
    started = perf_counter()
    results = [
        run_one_probe(
            item,
            search_client=search_client,
            settings=settings,
            fallback_answer_type=args.fallback_answer_type,
        )
        for item in items
    ]
    payload = {
        "summary": summarize(results, settings=settings, proxy_arg=args.proxy),
        "duration_seconds": round(perf_counter() - started, 4),
        "inputs": {
            "accepted_jsonl": [str(path) for path in args.accepted_jsonl],
            "rejected_jsonl": [str(path) for path in args.rejected_jsonl],
            "accepted_limit": args.accepted_limit,
            "rejected_limit": args.rejected_limit,
            "rejected_min_duckduckgo_seconds": args.rejected_min_duckduckgo_seconds,
        },
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
