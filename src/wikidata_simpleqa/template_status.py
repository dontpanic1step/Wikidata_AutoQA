"""Build a canonical template-status index from run artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

NO_ROOM_FOR_REFINEMENT_NO_RESULT_TEMPLATE_KEYS = {
    "ordinal_country_prime_minister",
    "footballer_goals_in_ordinal_tournament",
    "acquisition_purchase_price",
}

DEGRADED_NO_RESULT_PROBLEM_KINDS = {
    "chunked_office_holder_lookup_failed",
    "chunked_office_history_lookup_failed",
    "chunked_acquisition_price_lookup_failed",
    "chunked_player_goal_lookup_failed",
    "time_windowed_tournament_seed_failed",
    "time_windowed_acquisition_seed_failed",
}

from .domain_templates import get_all_templates


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read a JSONL file if it exists."""
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def read_json(path: Path) -> dict[str, Any] | None:
    """Read a JSON file if it exists."""
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_review_bundle_proven_map(path: Path) -> dict[str, dict[str, str]]:
    """Return currently proven template keys from the review TSV bundle."""
    if not path.exists():
        return {}
    proven: dict[str, dict[str, str]] = {}
    with path.open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            template_key = _record_template_key(row)
            if not template_key:
                continue
            proven[template_key] = {
                "question": str(row.get("question", "")).strip(),
                "answer": str(row.get("answer", "")).strip(),
                "source_run": str(row.get("source_run", "")).strip(),
            }
    return proven


def collect_rejection_reasons(paths: list[Path]) -> dict[str, list[str]]:
    """Return normalized rejection reasons gathered from rejected JSONL files."""
    reasons_by_template_key: dict[str, set[str]] = {}
    for path in paths:
        for record in read_jsonl(path):
            template_key = _record_template_key(record)
            reason = str(record.get("rejection_reason", "")).strip()
            if not template_key or not reason:
                continue
            reasons_by_template_key.setdefault(template_key, set()).add(reason)
    return {
        template_key: sorted(reasons)
        for template_key, reasons in sorted(reasons_by_template_key.items())
    }


def collect_rejection_reasons_by_source(paths: list[Path]) -> dict[str, dict[str, list[str]]]:
    """Return normalized rejection reasons grouped by artifact source and template key."""
    reasons_by_source: dict[str, dict[str, set[str]]] = {}
    for path in paths:
        source_name = _artifact_source_name(path, "_rejected.jsonl")
        source_reasons = reasons_by_source.setdefault(source_name, {})
        for record in read_jsonl(path):
            template_key = _record_template_key(record)
            reason = str(record.get("rejection_reason", "")).strip()
            if not template_key or not reason:
                continue
            source_reasons.setdefault(template_key, set()).add(reason)
    return {
        source_name: {
            domain: sorted(reasons)
            for domain, reasons in sorted(domain_map.items())
        }
        for source_name, domain_map in sorted(reasons_by_source.items())
    }


def collect_latest_run_results(summary_paths: list[Path]) -> dict[str, dict[str, Any]]:
    """Return the latest known per-domain run result from ordered summaries."""
    latest: dict[str, dict[str, Any]] = {}
    for path in summary_paths:
        summary = read_json(path)
        if not summary:
            continue
        template_results = summary.get("template_results")
        if not isinstance(template_results, list):
            template_results = _coerce_template_results(summary)
        if not isinstance(template_results, list):
            continue
        for result in template_results:
            if not isinstance(result, dict):
                continue
            template_key = _record_template_key(result)
            if not template_key:
                continue
            latest[template_key] = {
                "template_key": template_key,
                "source_summary": str(path),
                "status": str(result.get("status", "")).strip(),
                "accepted": int(result.get("accepted", 0) or 0),
                "rejected": int(result.get("rejected", 0) or 0),
                "target_time": str(
                    result.get("target_time", summary.get("target_time", ""))
                ).strip(),
                "telemetry": result.get("telemetry", {}),
                "notes": result.get("notes", {}),
                "error_message": str(result.get("error_message", "")).strip(),
            }
    return latest


def collect_run_history(
    summary_paths: list[Path],
    *,
    accepted_paths: list[Path],
    rejected_paths: list[Path],
) -> dict[str, list[dict[str, Any]]]:
    """Return ordered per-domain run history with semantic evidence attached."""
    accepted_invalid_reasons_by_source = collect_accepted_invalid_reasons_by_source(accepted_paths)
    rejected_reasons_by_source = collect_rejection_reasons_by_source(rejected_paths)
    history: dict[str, list[dict[str, Any]]] = {}
    for path in summary_paths:
        summary = read_json(path)
        if not summary:
            continue
        template_results = summary.get("template_results")
        if not isinstance(template_results, list):
            template_results = _coerce_template_results(summary)
        if not isinstance(template_results, list):
            continue
        source_name = _artifact_source_name(path, "_summary.json")
        for result in template_results:
            if not isinstance(result, dict):
                continue
            template_key = _record_template_key(result)
            if not template_key:
                continue
            filtered_reasons = accepted_invalid_reasons_by_source.get(source_name, {}).get(template_key, [])
            rejection_reasons = rejected_reasons_by_source.get(source_name, {}).get(template_key, [])
            all_reasons = sorted(set(filtered_reasons) | set(rejection_reasons))
            normalized = {
                "template_key": template_key,
                "source_summary": str(path),
                "source_name": source_name,
                "status": str(result.get("status", "")).strip(),
                "accepted": int(result.get("accepted", 0) or 0),
                "rejected": int(result.get("rejected", 0) or 0),
                "target_time": str(
                    result.get("target_time", summary.get("target_time", ""))
                ).strip(),
                "telemetry": result.get("telemetry", {}),
                "notes": result.get("notes", {}),
                "error_message": str(result.get("error_message", "")).strip(),
                "filtered_reasons": filtered_reasons,
                "rejection_reasons": rejection_reasons,
                "all_rejection_reasons": all_reasons,
                "semantic_outcome": _resolve_run_semantic_outcome(
                    str(result.get("status", "")).strip(),
                    filtered_reasons,
                ),
            }
            history.setdefault(template_key, []).append(normalized)
    return history


def build_template_status_index(
    *,
    review_bundle_path: Path,
    summary_paths: list[Path],
    rejected_paths: list[Path],
    accepted_paths: list[Path],
    status_mode: str = "latest_live_status",
) -> dict[str, Any]:
    """Build the canonical status index for every catalog template."""
    if status_mode not in {"latest_live_status", "best_known_semantic_status"}:
        raise ValueError(f"Unsupported status_mode: {status_mode}")
    proven_map = load_review_bundle_proven_map(review_bundle_path)
    latest_results = collect_latest_run_results(summary_paths)
    run_history = collect_run_history(
        summary_paths,
        accepted_paths=accepted_paths,
        rejected_paths=rejected_paths,
    )
    rejection_reasons = collect_rejection_reasons(rejected_paths)
    latest_accepted_records = collect_latest_accepted_records(accepted_paths)

    statuses: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    for template in _unique_templates_by_key():
        template_key = template.template_key
        latest = latest_results.get(template_key, {})
        filtered_reasons = latest_accepted_records.get(template_key, {}).get(
            "invalid_reasons",
            [],
        )
        all_rejection_reasons = sorted(
            set(rejection_reasons.get(template_key, [])) | set(filtered_reasons)
        )
        latest_live_status = _resolve_template_status(
            template_key,
            proven_map,
            latest,
            filtered_reasons,
            [],
        )
        best_known_semantic_status = _resolve_template_status(
            template_key,
            proven_map,
            latest,
            filtered_reasons,
            all_rejection_reasons,
        )
        original_current_status = (
            best_known_semantic_status
            if status_mode == "best_known_semantic_status"
            else latest_live_status
        )
        status = "frozen" if template.status == "frozen" else original_current_status
        reliability = _build_reliability_summary(
            run_history.get(template_key, []),
            best_known_semantic_status=best_known_semantic_status,
        )
        counts[status] = counts.get(status, 0) + 1
        statuses.append(
            {
                "template_key": template_key,
                "template": template_key,
                "domain": template.template_domain,
                "answer_type": template.answer_type,
                "canonical_question_template": template.canonical_question_template,
                "question_family": template.question_family,
                "legacy_catalog_bucket": template.status,
                "current_status": status,
                "original_current_status": original_current_status,
                "status_mode": status_mode,
                "latest_live_status": latest_live_status,
                "best_known_semantic_status": best_known_semantic_status,
                "proven_example": proven_map.get(template_key),
                "latest_run": latest or None,
                "status_detail": _build_status_detail(status, latest),
                "rejection_reasons": all_rejection_reasons,
                "reliability": reliability,
            }
        )

    return {
        "review_bundle_path": str(review_bundle_path),
        "status_mode": status_mode,
        "summary_sources": [str(path) for path in summary_paths],
        "rejected_sources": [str(path) for path in rejected_paths],
        "accepted_sources": [str(path) for path in accepted_paths],
        "counts": dict(sorted(counts.items())),
        "templates": statuses,
    }


def render_template_status_markdown(index: dict[str, Any]) -> str:
    """Render a readable Markdown report for the template-status index."""
    templates = index["templates"]
    counts = index["counts"]
    lines = [
        "# Template Status Index",
        "",
        "## Counts",
        "",
    ]
    for key, value in counts.items():
        lines.append(f"- `{key}`: `{value}`")

    for bucket in (
        "proven",
        "frozen",
        "rejected_only",
        "error",
        "unproven_no_result",
        "untracked",
    ):
        bucket_rows = [row for row in templates if row["current_status"] == bucket]
        lines.extend(
            [
                "",
                f"## {bucket.replace('_', ' ').title()}",
                "",
            ]
        )
        if not bucket_rows:
            lines.append("- None")
            continue
        lines.extend(
            [
                "| Domain | Template | Answer Type | Canonical Question | Successful Generated Question |",
                "|---|---|---|---|---|",
            ]
        )
        for row in bucket_rows:
            example = row.get("proven_example") or {}
            lines.append(
                "| {domain} | {template} | {answer_type} | {canonical_question} | {success_question} |".format(
                    domain=row["domain"],
                    template=row["template_key"],
                    answer_type=row.get("answer_type", ""),
                    canonical_question=row.get("canonical_question_template", ""),
                    success_question=example.get("question", ""),
                )
            )
    return "\n".join(lines) + "\n"


def _resolve_template_status(
    template_key: str,
    proven_map: dict[str, dict[str, str]],
    latest_result: dict[str, Any],
    filtered_reasons: list[str],
    all_rejection_reasons: list[str] | None = None,
) -> str:
    """Resolve one canonical current status for a template."""
    if template_key in proven_map:
        return "proven"
    status = str(latest_result.get("status", "")).strip()
    if status == "accepted" and filtered_reasons:
        return "rejected_only"
    if status == "rejected_only":
        return "rejected_only"
    if status == "no_result_with_request_errors":
        if all_rejection_reasons:
            return "rejected_only"
        return "unproven_no_result"
    if status.startswith("error:"):
        return "error"
    if status == "no_result":
        return "unproven_no_result"
    return "untracked"


def _build_status_detail(status: str, latest_result: dict[str, Any]) -> dict[str, Any]:
    """Return a normalized explanation payload for the current status."""
    template_key = _record_template_key(latest_result)
    if status != "unproven_no_result":
        return {}

    telemetry = latest_result.get("telemetry", {})
    total_requests = int(telemetry.get("total_requests", 0) or 0)
    network_requests = int(telemetry.get("network_requests", 0) or 0)
    cache_hits = int(telemetry.get("cache_hits", 0) or 0)
    events = telemetry.get("events", [])
    if not isinstance(events, list):
        events = []
    problems = telemetry.get("problems", [])
    if not isinstance(problems, list):
        problems = []
    problem_kinds = [str(problem.get("kind", "")).strip() for problem in problems if isinstance(problem, dict)]
    probe_problem = next(
        (
            problem
            for problem in problems
            if isinstance(problem, dict)
            and str(problem.get("kind", "")).strip() in {"support_probe_completed", "support_probe_failed"}
        ),
        {},
    )
    probe_context = probe_problem.get("context", {}) if isinstance(probe_problem, dict) else {}
    probe_result_count = probe_context.get("probe_result_count")

    if any(
        kind in {
            "missing_join_executor",
            "missing_ordinal_executor",
            "missing_aggregate_executor",
            "unsupported_reasoning_style",
        }
        for kind in problem_kinds
    ):
        if "support_probe_skipped" in problem_kinds:
            return {
                "bucket": "missing_executor_no_probe",
                "summary": "No domain-specific executor exists, and the generic probe was skipped because the template uses a synthetic composed property.",
                "problem_kinds": problem_kinds,
                "network_requests": network_requests,
            }
        if "support_probe_completed" in problem_kinds:
            return {
                "bucket": "missing_executor_probe_only",
                "summary": "No domain-specific executor exists. The run only performed a lightweight support probe instead of the real reasoning path.",
                "problem_kinds": problem_kinds,
                "network_requests": network_requests,
                "probe_result_count": probe_result_count,
            }
        if "support_probe_failed" in problem_kinds:
            return {
                "bucket": "missing_executor_probe_failed",
                "summary": "No domain-specific executor exists, and even the lightweight support probe failed.",
                "problem_kinds": problem_kinds,
                "network_requests": network_requests,
            }
        return {
            "bucket": "missing_executor_other",
            "summary": "No domain-specific executor exists for this template.",
            "problem_kinds": problem_kinds,
            "network_requests": network_requests,
        }

    if "staged_seed_strategy_used" in problem_kinds:
        sparse_tag = _sparse_answer_tag(latest_result)
        return {
            "bucket": "implemented_sparse_2026_seeded",
            "summary": "A real staged seed search ran, but the 2026 window still looks sparse for this template.",
            "problem_kinds": problem_kinds,
            "total_requests": total_requests,
            "network_requests": network_requests,
            "tags": [sparse_tag] if sparse_tag else [],
        }

    if any(kind in DEGRADED_NO_RESULT_PROBLEM_KINDS for kind in problem_kinds):
        sparse_tag = _sparse_answer_tag(latest_result)
        tags = [sparse_tag] if sparse_tag else []
        if template_key in NO_ROOM_FOR_REFINEMENT_NO_RESULT_TEMPLATE_KEYS:
            tags.append("no_room_for_refinement")
        return {
            "bucket": "degraded_no_result_due_to_query_failure",
            "summary": "The run completed without a candidate, but recorded query/runtime failures mean this is not a normal sparse empty result.",
            "problem_kinds": problem_kinds,
            "total_requests": total_requests,
            "network_requests": network_requests,
            "tags": tags,
        }

    if total_requests > 0 or network_requests > 0 or cache_hits > 0 or events:
        sparse_tag = _sparse_answer_tag(latest_result)
        tags = [sparse_tag] if sparse_tag else []
        if template_key in NO_ROOM_FOR_REFINEMENT_NO_RESULT_TEMPLATE_KEYS:
            tags.append("no_room_for_refinement")
        return {
            "bucket": "implemented_sparse_2026",
            "summary": "A real search ran, but the 2026 window still looks sparse for this template.",
            "problem_kinds": problem_kinds,
            "total_requests": total_requests,
            "network_requests": network_requests,
            "tags": tags,
        }

    return {
        "bucket": "unexplained_no_result",
        "summary": "The template ended with no_result without enough telemetry to classify the failure more precisely.",
        "problem_kinds": problem_kinds,
        "total_requests": total_requests,
        "network_requests": network_requests,
    }


def _render_status_detail(detail: dict[str, Any]) -> str:
    """Render a concise Markdown explanation for one status detail payload."""
    if not detail:
        return ""
    bucket = str(detail.get("bucket", "")).strip()
    summary = str(detail.get("summary", "")).strip()
    total_requests = detail.get("total_requests")
    network_requests = detail.get("network_requests")
    probe_result_count = detail.get("probe_result_count")
    tags = detail.get("tags", [])
    extras: list[str] = []
    if bucket:
        extras.append(f"`{bucket}`")
    if isinstance(tags, list):
        extras.extend(f"`{str(tag).strip()}`" for tag in tags if str(tag).strip())
    if total_requests is not None:
        extras.append(f"`total_requests={total_requests}`")
    if network_requests is not None:
        extras.append(f"`network_requests={network_requests}`")
    if probe_result_count is not None:
        extras.append(f"`probe_result_count={probe_result_count}`")
    if summary and extras:
        return f"{summary} ({', '.join(extras)})"
    if summary:
        return summary
    return ", ".join(extras)


def _render_reliability_detail(reliability: dict[str, Any]) -> str:
    """Render a concise Markdown reliability summary."""
    if not reliability:
        return ""
    total_runs = reliability.get("total_runs")
    if not total_runs:
        return ""
    request_clean_runs = reliability.get("request_clean_runs")
    candidate_yield_runs = reliability.get("candidate_yield_runs")
    semantic_repro_rate = reliability.get("semantic_repro_rate")
    parts = [f"`pass_rate={request_clean_runs}/{total_runs}`"]
    if candidate_yield_runs is not None:
        parts.append(f"`candidate_yield={candidate_yield_runs}/{total_runs}`")
    if semantic_repro_rate is not None:
        parts.append(f"`semantic_repro_rate={semantic_repro_rate:.2f}`")
    return "Operational reliability " + ", ".join(parts)


def _sparse_answer_tag(latest_result: dict[str, Any]) -> str:
    """Return a normalized sparse-answer tag keyed by the run target time."""
    target_time = str(latest_result.get("target_time", "")).strip()
    if not target_time:
        return ""
    normalized = target_time.replace("-", "_")
    return f"sparse_answer_{normalized}"


def _unique_templates_by_key() -> list[Any]:
    """Return templates deduplicated by template key, keeping the first catalog entry."""
    unique = []
    seen_template_keys: set[str] = set()
    for template in get_all_templates():
        if template.template_key in seen_template_keys:
            continue
        seen_template_keys.add(template.template_key)
        unique.append(template)
    return unique


def _record_template_key(record: dict[str, Any]) -> str:
    """Return a template key from canonical or legacy artifact fields."""
    for field in ("template_key", "legacy_domain", "domain"):
        value = str(record.get(field, "")).strip()
        if value:
            return value
    return ""


def collect_latest_accepted_records(accepted_paths: list[Path]) -> dict[str, dict[str, Any]]:
    """Return the latest accepted record per template key with current invalid reasons."""
    latest: dict[str, dict[str, Any]] = {}
    for path in accepted_paths:
        records = read_jsonl(path)
        if not records:
            continue
        invalid_reason_resolver = _load_invalid_reason_resolver()
        for record in records:
            template_key = _record_template_key(record)
            if not template_key:
                continue
            latest[template_key] = {
                "source_path": str(path),
                "record": record,
                "invalid_reasons": invalid_reason_resolver(record),
            }
    return latest


def collect_accepted_invalid_reasons_by_source(paths: list[Path]) -> dict[str, dict[str, list[str]]]:
    """Return invalid accepted-record reasons grouped by artifact source and template key."""
    invalid_reason_resolver = _load_invalid_reason_resolver()
    grouped: dict[str, dict[str, list[str]]] = {}
    for path in paths:
        source_name = _artifact_source_name(path, "_accepted.jsonl")
        domain_map = grouped.setdefault(source_name, {})
        records = read_jsonl(path)
        if not records:
            continue
        for record in records:
            template_key = _record_template_key(record)
            if not template_key:
                continue
            domain_map[template_key] = invalid_reason_resolver(record)
    return grouped


def _load_invalid_reason_resolver():
    """Lazily import the review-bundle validator helper to avoid import cycles."""
    import importlib.util
    import sys

    module_name = "_build_review_bundle_helper"
    if module_name in sys.modules:
        module = sys.modules[module_name]
    else:
        script_path = Path(__file__).resolve().parents[2] / "scripts" / "build_review_bundle.py"
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        if spec is None or spec.loader is None:
            raise RuntimeError("Failed to load build_review_bundle.py for status validation")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    return module.record_invalid_reasons


def _coerce_template_results(summary: dict[str, Any]) -> list[dict[str, Any]]:
    """Coerce ad hoc rerun summaries into the standard template-results shape."""
    if isinstance(summary.get("results"), list):
        coerced: list[dict[str, Any]] = []
        for result in summary["results"]:
            if not isinstance(result, dict):
                continue
            coerced.append(
                {
                    "domain": result.get("domain", ""),
                    "status": result.get("status", ""),
                    "accepted": 1 if result.get("status") == "accepted" else 0,
                    "rejected": 0,
                    "notes": {"reasons": result.get("reasons", [])},
                    "error_message": result.get("error_message", ""),
                }
            )
        return coerced
    if "domain" in summary and "accepted_total" in summary:
        return [
            {
                "domain": summary.get("domain", ""),
                "status": "accepted" if summary.get("accepted_total", 0) else "rejected_only",
                "accepted": int(summary.get("accepted_total", 0) or 0),
                "rejected": int(summary.get("rejected_total", 0) or 0),
                "notes": {"reasons": summary.get("rejection_reasons", [])},
                "error_message": "",
            }
        ]
    return []


def _artifact_source_name(path: Path, suffix: str) -> str:
    """Return a normalized source stem from one artifact path."""
    return path.name.removesuffix(suffix)


def _resolve_run_semantic_outcome(status: str, filtered_reasons: list[str]) -> str | None:
    """Resolve whether one concrete run produced a semantic conclusion."""
    if status == "accepted":
        return "rejected_only" if filtered_reasons else "accepted"
    if status == "rejected_only":
        return "rejected_only"
    return None


def _build_reliability_summary(
    history: list[dict[str, Any]],
    *,
    best_known_semantic_status: str,
) -> dict[str, Any]:
    """Summarize pass-rate style reliability metrics from repeated runs."""
    if not history:
        return {}

    total_runs = len(history)
    request_error_runs = 0
    request_clean_runs = 0
    candidate_yield_runs = 0
    conclusive_runs = 0
    matching_semantic_runs = 0
    total_requests_sum = 0
    network_requests_sum = 0
    retry_count_sum = 0
    cache_hits_sum = 0

    target_semantic_outcome: str | None
    if best_known_semantic_status == "proven":
        target_semantic_outcome = "accepted"
    elif best_known_semantic_status == "rejected_only":
        target_semantic_outcome = "rejected_only"
    else:
        target_semantic_outcome = None

    outcome_counts: dict[str, int] = {}
    for run in history:
        status = str(run.get("status", "")).strip()
        telemetry = run.get("telemetry", {})
        if status.startswith("error:") or status == "no_result_with_request_errors":
            request_error_runs += 1
        else:
            request_clean_runs += 1
        if int(run.get("accepted", 0) or 0) > 0 or int(run.get("rejected", 0) or 0) > 0:
            candidate_yield_runs += 1
        semantic_outcome = run.get("semantic_outcome")
        if semantic_outcome:
            conclusive_runs += 1
            outcome_counts[str(semantic_outcome)] = outcome_counts.get(str(semantic_outcome), 0) + 1
            if semantic_outcome == target_semantic_outcome:
                matching_semantic_runs += 1
        total_requests_sum += int(telemetry.get("total_requests", 0) or 0)
        network_requests_sum += int(telemetry.get("network_requests", 0) or 0)
        retry_count_sum += int(telemetry.get("retry_count", 0) or 0)
        cache_hits_sum += int(telemetry.get("cache_hits", 0) or 0)

    return {
        "total_runs": total_runs,
        "request_clean_runs": request_clean_runs,
        "request_error_runs": request_error_runs,
        "pass_rate": round(request_clean_runs / total_runs, 4),
        "request_failure_rate": round(request_error_runs / total_runs, 4),
        "candidate_yield_runs": candidate_yield_runs,
        "candidate_yield_rate": round(candidate_yield_runs / total_runs, 4),
        "conclusive_runs": conclusive_runs,
        "semantic_outcome_counts": dict(sorted(outcome_counts.items())),
        "semantic_repro_rate": (
            round(matching_semantic_runs / conclusive_runs, 4)
            if conclusive_runs and target_semantic_outcome
            else None
        ),
        "average_total_requests": round(total_requests_sum / total_runs, 2),
        "average_network_requests": round(network_requests_sum / total_runs, 2),
        "average_retry_count": round(retry_count_sum / total_runs, 2),
        "average_cache_hits": round(cache_hits_sum / total_runs, 2),
        "latest_source_name": str(history[-1].get("source_name", "")).strip(),
        "target_semantic_outcome": target_semantic_outcome,
    }
