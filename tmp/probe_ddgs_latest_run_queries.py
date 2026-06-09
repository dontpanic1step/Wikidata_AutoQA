"""Probe DuckDuckGo with real queries from the latest Route 3 run."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from time import perf_counter, sleep
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.search_client import DuckDuckGoSearchClient, DuckDuckGoSearchError  # noqa: E402


DEFAULT_RUN_DIR = (
    ROOT
    / "outputs"
    / "recipe_segments"
    / "route3_reuse_cached_all5_infobox_only_2026_06_08_222053"
)


@dataclass(frozen=True)
class QueryItem:
    """One query attached to one generated QA record."""

    qa_index: int
    record_source: str
    record_id: str
    question: str
    answer: str
    subject: str
    answer_type: str
    query_index: int
    query_name: str
    query_category: str
    query: str


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--max-qa", type=int, default=10)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--proxy", default="socks5://127.0.0.1:7890")
    parser.add_argument("--timeout-seconds", type=float, default=15.0)
    parser.add_argument("--ddgs-backend", default="auto")
    parser.add_argument("--query-pause-seconds", type=float, default=1.0)
    parser.add_argument("--stage-pause-seconds", type=float, default=2.0)
    parser.add_argument(
        "--stage-mode",
        choices=["incremental", "cumulative"],
        default="incremental",
        help="incremental tests each new QA once; cumulative reruns all queries from QA 1..N at each stage.",
    )
    parser.add_argument(
        "--source-order",
        default="accepted,rejected",
        help="Comma-separated order of accepted/rejected JSONL files used to collect QA records.",
    )
    parser.add_argument(
        "--duckduckgo-disable-fallback",
        action="append",
        default=[],
        help="Disable fallback paths in DuckDuckGoSearchClient, e.g. direct,lite,legacy,ddgs.",
    )
    parser.add_argument("--cooldown-failure-threshold", type=int, default=3)
    parser.add_argument("--cooldown-initial-seconds", type=float, default=60.0)
    parser.add_argument("--cooldown-max-seconds", type=float, default=300.0)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument(
        "--records-output",
        type=Path,
        default=None,
        help="JSONL output with one current-format probe record per QA/stage.",
    )
    return parser.parse_args()


def _jsonl_paths(run_dir: Path, source_order: str) -> list[tuple[str, Path]]:
    """Return accepted/rejected JSONL files in the requested order."""
    paths: list[tuple[str, Path]] = []
    for source in [part.strip().lower() for part in source_order.split(",") if part.strip()]:
        pattern = f"*_{source}.jsonl"
        matches = sorted(run_dir.glob(pattern))
        if not matches:
            matches = sorted(run_dir.glob(f"*{source}*.jsonl"))
        for path in matches:
            paths.append((source, path))
    return paths


def _iter_records(paths: list[tuple[str, Path]]) -> Any:
    """Yield JSON records from JSONL files."""
    for source, path in paths:
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                yield source, path, line_number, record


def _record_queries(record: dict[str, Any]) -> list[tuple[str, str, str]]:
    """Extract query diagnostics from a generated QA record."""
    items: list[tuple[str, str, str]] = []
    verification = record.get("search_verification_features") or {}
    for query_index, query_record in enumerate(verification.get("queries") or [], start=1):
        query = str(query_record.get("query") or "").strip()
        if query:
            items.append(
                (
                    str(query_record.get("query_name") or f"verification_query_{query_index}"),
                    str(query_record.get("query_category") or ""),
                    query,
                )
            )
    if not items:
        question = str(record.get("rewritten_question") or record.get("canonical_question") or record.get("question") or "").strip()
        if question and question != str(record.get("subject_entity", {}).get("name") or "").strip():
            items.append(("full_question", "fallback_record_question", question))
        for query_index, query in enumerate(record.get("search_queries") or [], start=1):
            query = str(query).strip()
            if query:
                items.append((f"search_query_{query_index}", "fallback_search_queries", query))

    seen: set[str] = set()
    unique_items: list[tuple[str, str, str]] = []
    for query_name, query_category, query in items:
        if query in seen:
            continue
        seen.add(query)
        unique_items.append((query_name, query_category, query))
    return unique_items


def collect_query_items(run_dir: Path, *, max_qa: int, source_order: str) -> list[list[QueryItem]]:
    """Collect the first QA records with real search queries."""
    paths = _jsonl_paths(run_dir, source_order)
    if not paths:
        raise FileNotFoundError(f"No accepted/rejected JSONL files found under {run_dir}")
    qas: list[list[QueryItem]] = []
    for source, path, _line_number, record in _iter_records(paths):
        raw_queries = _record_queries(record)
        if not raw_queries:
            continue
        qa_index = len(qas) + 1
        record_id = str(record.get("id") or "")
        question = str(record.get("rewritten_question") or record.get("canonical_question") or record.get("question") or "")
        answer = record.get("answer")
        answer_text = ", ".join(str(item) for item in answer) if isinstance(answer, list) else str(answer or "")
        subject = str((record.get("subject_entity") or {}).get("name") or record.get("subject_resource_url") or "")
        answer_type = str(record.get("answer_type") or "")
        qa_items = [
            QueryItem(
                qa_index=qa_index,
                record_source=f"{source}:{path.name}",
                record_id=record_id,
                question=question,
                answer=answer_text,
                subject=subject,
                answer_type=answer_type,
                query_index=query_index,
                query_name=query_name,
                query_category=query_category,
                query=query,
            )
            for query_index, (query_name, query_category, query) in enumerate(raw_queries, start=1)
        ]
        qas.append(qa_items)
        if len(qas) >= max_qa:
            break
    return qas


def _event_summary(event: dict[str, Any]) -> dict[str, Any]:
    """Return compact diagnostics for one search-client request event."""
    attempts = event.get("attempts") or []
    endpoint_counts = Counter(str(attempt.get("endpoint") or "") for attempt in attempts)
    path_counts = Counter(str(attempt.get("path") or "") for attempt in attempts)
    statuses = [
        attempt.get("status", attempt.get("http_status"))
        for attempt in attempts
        if attempt.get("status", attempt.get("http_status")) is not None
    ]
    errors = Counter(
        str(attempt.get("error_type") or attempt.get("retry_reason") or attempt.get("fallback_reason") or "")
        for attempt in attempts
        if not attempt.get("ok", True)
    )
    return {
        "backend": event.get("backend"),
        "failed": bool(event.get("failed")),
        "duration_ms": event.get("duration_ms"),
        "used_ddgs": bool(event.get("used_ddgs")),
        "used_legacy_fallback": bool(event.get("used_legacy_fallback")),
        "used_direct_fallback": bool(event.get("used_direct_fallback")),
        "used_lite_fallback": bool(event.get("used_lite_fallback")),
        "attempt_count": len(attempts),
        "endpoint_counts": dict(endpoint_counts),
        "path_counts": dict(path_counts),
        "statuses": statuses,
        "errors": {key: value for key, value in errors.items() if key},
        "cooldown_triggered": any(attempt.get("cooldown_triggered") for attempt in attempts),
        "cooldown_waited": any(attempt.get("endpoint") == "global_cooldown" and attempt.get("ok") for attempt in attempts),
    }


def run_query(client: DuckDuckGoSearchClient, item: QueryItem, *, top_k: int) -> dict[str, Any]:
    """Run one query and return compact plus full diagnostics."""
    client.request_events.clear()
    started = perf_counter()
    try:
        results = client.search(item.query, max_results=top_k)
    except DuckDuckGoSearchError as exc:
        duration_seconds = perf_counter() - started
        event = client.request_events[-1] if client.request_events else {"attempts": exc.attempt_events, "failed": True}
        query_record = {
            "query_name": item.query_name,
            "query_category": item.query_category,
            "query": item.query,
            "duration_seconds": round(duration_seconds, 4),
            "error": True,
            "error_type": type(exc.original_error).__name__,
            "error_message": str(exc.original_error),
            "search_request_events": [event],
            "result_count": 0,
            "results": [],
            "probe_event_summary": _event_summary(event),
        }
        return {
            "qa": asdict(item),
            "ok": False,
            "duration_seconds": round(duration_seconds, 4),
            "result_count": 0,
            "error_type": type(exc.original_error).__name__,
            "error_message": str(exc.original_error),
            "event_summary": _event_summary(event),
            "query_record": query_record,
            "request_event": event,
        }
    duration_seconds = perf_counter() - started
    event = client.request_events[-1] if client.request_events else {}
    result_rows = [asdict(result) for result in results]
    query_record = {
        "query_name": item.query_name,
        "query_category": item.query_category,
        "query": item.query,
        "duration_seconds": round(duration_seconds, 4),
        "error": False,
        "search_request_events": [event],
        "result_count": len(results),
        "results": result_rows,
        "probe_event_summary": _event_summary(event),
    }
    return {
        "qa": asdict(item),
        "ok": True,
        "duration_seconds": round(duration_seconds, 4),
        "result_count": len(results),
        "first_titles": [result.title for result in results[:3]],
        "results": result_rows,
        "event_summary": _event_summary(event),
        "query_record": query_record,
        "request_event": event,
    }


def summarize_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize probe outcomes."""
    total = len(results)
    ok = sum(1 for result in results if result.get("ok"))
    backends = Counter(str(result.get("event_summary", {}).get("backend") or "") for result in results)
    errors = Counter(
        str(result.get("error_type") or "")
        for result in results
        if not result.get("ok") and result.get("error_type")
    )
    return {
        "total_queries": total,
        "ok_queries": ok,
        "failed_queries": total - ok,
        "ok_rate": round(ok / total, 4) if total else None,
        "backend_counts": dict(backends),
        "error_counts": dict(errors),
        "ddgs_successes": sum(
            1
            for result in results
            if result.get("ok") and result.get("event_summary", {}).get("backend") == "ddgs"
        ),
        "legacy_fallback_successes": sum(
            1
            for result in results
            if result.get("ok") and result.get("event_summary", {}).get("used_legacy_fallback")
        ),
        "cooldown_trigger_count": sum(
            1 for result in results if result.get("event_summary", {}).get("cooldown_triggered")
        ),
        "cooldown_wait_count": sum(
            1 for result in results if result.get("event_summary", {}).get("cooldown_waited")
        ),
    }


def build_current_format_probe_records(
    qas: list[list[QueryItem]],
    results: list[dict[str, Any]],
    *,
    top_k: int,
    stage_mode: str,
    summary: dict[str, Any],
) -> list[dict[str, Any]]:
    """Build probe records shaped like pipeline QA records with full query diagnostics."""
    items_by_qa: dict[int, list[QueryItem]] = {qa[0].qa_index: qa for qa in qas if qa}
    grouped: dict[tuple[int, int], list[dict[str, Any]]] = {}
    for result in results:
        qa_index = int(result.get("qa", {}).get("qa_index") or 0)
        stage = int(result.get("probe_stage") or qa_index or 0)
        grouped.setdefault((stage, qa_index), []).append(result)

    records: list[dict[str, Any]] = []
    for (stage, qa_index), group in sorted(grouped.items()):
        qa_items = items_by_qa.get(qa_index)
        if not qa_items:
            continue
        first_item = qa_items[0]
        query_records = [result["query_record"] for result in sorted(group, key=lambda value: value.get("qa", {}).get("query_index", 0))]
        record_summary = summarize_results(group)
        records.append(
            {
                "id": first_item.record_id or f"ddgs_probe_stage{stage:02d}_qa{qa_index:02d}",
                "question": first_item.question,
                "answer": first_item.answer,
                "answer_aliases": [],
                "source_type": "ddgs_probe_latest_run_queries",
                "generation_route": "route3_wikipedia_infobox",
                "subject_entity": {
                    "name": first_item.subject,
                    "qid": "",
                    "wikipedia_title": "",
                    "url": "",
                },
                "answer_entity": {
                    "name": first_item.answer,
                    "qid": "",
                    "wikipedia_title": "",
                    "url": "",
                },
                "canonical_question": first_item.question,
                "rewritten_question": first_item.question,
                "answer_type": first_item.answer_type,
                "search_queries": [item.query for item in qa_items],
                "search_verification_features": {
                    "top_k": top_k,
                    "max_parallel_queries": 1,
                    "early_stopped": False,
                    "queries": query_records,
                    "result_count": sum(int(query.get("result_count") or 0) for query in query_records),
                    "error_count": sum(1 for query in query_records if query.get("error")),
                    "probe_summary": record_summary,
                },
                "source_metadata": {
                    "probe_stage": stage,
                    "probe_stage_mode": stage_mode,
                    "probe_original_record_source": first_item.record_source,
                    "probe_qa_index": qa_index,
                    "probe_summary": summary,
                },
            }
        )
    return records


def main() -> int:
    """Run the probe."""
    args = parse_args()
    run_dir = args.run_dir.resolve()
    qas = collect_query_items(run_dir, max_qa=args.max_qa, source_order=args.source_order)
    if not qas:
        raise RuntimeError(f"No QA records with real search queries found in {run_dir}")

    DuckDuckGoSearchClient.reset_global_cooldown()
    client = DuckDuckGoSearchClient(
        user_agent="WikidataSimpleQA/0.1 (ddgs probe)",
        proxy=args.proxy or None,
        timeout_seconds=args.timeout_seconds,
        cache_dir=None,
        ddgs_backend=args.ddgs_backend,
        disable_fallbacks=args.duckduckgo_disable_fallback,
        cooldown_failure_threshold=args.cooldown_failure_threshold,
        cooldown_initial_seconds=args.cooldown_initial_seconds,
        cooldown_max_seconds=args.cooldown_max_seconds,
    )

    all_results: list[dict[str, Any]] = []
    stages: list[dict[str, Any]] = []
    print(
        f"Loaded {len(qas)} QA records from {run_dir}; "
        f"stage_mode={args.stage_mode}; proxy={args.proxy or 'direct'}; ddgs_backend={args.ddgs_backend}",
        flush=True,
    )
    for stage_index in range(1, len(qas) + 1):
        stage_items = [item for qa in (qas[:stage_index] if args.stage_mode == "cumulative" else [qas[stage_index - 1]]) for item in qa]
        stage_results: list[dict[str, Any]] = []
        for item_index, item in enumerate(stage_items, start=1):
            result = run_query(client, item, top_k=args.top_k)
            result["probe_stage"] = stage_index
            result["probe_stage_query_index"] = item_index
            stage_results.append(result)
            all_results.append(result)
            print(
                f"stage={stage_index:02d} query={item_index:02d}/{len(stage_items):02d} "
                f"qa={item.qa_index:02d} ok={result['ok']} results={result['result_count']} "
                f"backend={result.get('event_summary', {}).get('backend')} "
                f"query={item.query[:90]!r}",
                flush=True,
            )
            if args.query_pause_seconds > 0 and item_index < len(stage_items):
                sleep(args.query_pause_seconds)
        stage_summary = {
            "stage": stage_index,
            "qa_count": stage_index,
            "stage_query_count": len(stage_items),
            "stage_summary": summarize_results(stage_results),
            "cumulative_summary": summarize_results(all_results),
        }
        stages.append(stage_summary)
        cumulative = stage_summary["cumulative_summary"]
        print(
            f"stage={stage_index:02d} summary ok={cumulative['ok_queries']}/{cumulative['total_queries']} "
            f"ddgs_successes={cumulative['ddgs_successes']} "
            f"legacy_fallback_successes={cumulative['legacy_fallback_successes']} "
            f"cooldowns={cumulative['cooldown_trigger_count']}/{cumulative['cooldown_wait_count']}",
            flush=True,
        )
        if args.stage_pause_seconds > 0 and stage_index < len(qas):
            sleep(args.stage_pause_seconds)

    output_path = args.output
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = ROOT / "tmp" / f"ddgs_latest_query_probe_{timestamp}.json"
    records_output_path = args.records_output
    if records_output_path is None:
        records_output_path = output_path.with_name(output_path.stem + "_records.jsonl")
    summary = summarize_results(all_results)
    current_format_records = build_current_format_probe_records(
        qas,
        all_results,
        top_k=args.top_k,
        stage_mode=args.stage_mode,
        summary=summary,
    )
    output_payload = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "run_dir": str(run_dir),
        "settings": {
            "max_qa": args.max_qa,
            "top_k": args.top_k,
            "proxy": args.proxy,
            "timeout_seconds": args.timeout_seconds,
            "ddgs_backend": args.ddgs_backend,
            "stage_mode": args.stage_mode,
            "disabled_fallbacks": args.duckduckgo_disable_fallback,
            "cooldown_failure_threshold": args.cooldown_failure_threshold,
            "cooldown_initial_seconds": args.cooldown_initial_seconds,
            "cooldown_max_seconds": args.cooldown_max_seconds,
        },
        "qa_records": [[asdict(item) for item in qa] for qa in qas],
        "stages": stages,
        "summary": summary,
        "current_format_record_count": len(current_format_records),
        "current_format_records_output": str(records_output_path),
        "results": all_results,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    records_output_path.parent.mkdir(parents=True, exist_ok=True)
    with records_output_path.open("w", encoding="utf-8") as handle:
        for record in current_format_records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"Wrote probe diagnostics: {output_path}", flush=True)
    print(f"Wrote current-format probe records: {records_output_path}", flush=True)
    print(json.dumps(output_payload["summary"], indent=2, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
