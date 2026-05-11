"""Build a canonical template-status index from run artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

NO_ROOM_FOR_REFINEMENT_NO_RESULT_DOMAINS = {
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
    """Return currently proven domains from the review TSV bundle."""
    if not path.exists():
        return {}
    proven: dict[str, dict[str, str]] = {}
    with path.open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            domain = str(row.get("domain", "")).strip()
            if not domain:
                continue
            proven[domain] = {
                "question": str(row.get("question", "")).strip(),
                "answer": str(row.get("answer", "")).strip(),
                "source_run": str(row.get("source_run", "")).strip(),
            }
    return proven


def collect_rejection_reasons(paths: list[Path]) -> dict[str, list[str]]:
    """Return normalized rejection reasons gathered from rejected JSONL files."""
    reasons_by_domain: dict[str, set[str]] = {}
    for path in paths:
        for record in read_jsonl(path):
            domain = str(record.get("domain", "")).strip()
            reason = str(record.get("rejection_reason", "")).strip()
            if not domain or not reason:
                continue
            reasons_by_domain.setdefault(domain, set()).add(reason)
    return {
        domain: sorted(reasons)
        for domain, reasons in sorted(reasons_by_domain.items())
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
            domain = str(result.get("domain", "")).strip()
            if not domain:
                continue
            latest[domain] = {
                "domain": domain,
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


def build_template_status_index(
    *,
    review_bundle_path: Path,
    summary_paths: list[Path],
    rejected_paths: list[Path],
    accepted_paths: list[Path],
) -> dict[str, Any]:
    """Build the canonical status index for every catalog template."""
    proven_map = load_review_bundle_proven_map(review_bundle_path)
    latest_results = collect_latest_run_results(summary_paths)
    rejection_reasons = collect_rejection_reasons(rejected_paths)
    latest_accepted_records = collect_latest_accepted_records(accepted_paths)

    statuses: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    for template in _unique_templates_by_domain():
        latest = latest_results.get(template.domain, {})
        filtered_reasons = latest_accepted_records.get(template.domain, {}).get(
            "invalid_reasons",
            [],
        )
        status = _resolve_template_status(template.domain, proven_map, latest, filtered_reasons)
        all_rejection_reasons = sorted(
            set(rejection_reasons.get(template.domain, [])) | set(filtered_reasons)
        )
        counts[status] = counts.get(status, 0) + 1
        statuses.append(
            {
                "domain": template.domain,
                "topic": template.topic,
                "question_family": template.question_family,
                "catalog_status": template.status,
                "current_status": status,
                "proven_example": proven_map.get(template.domain),
                "latest_run": latest or None,
                "status_detail": _build_status_detail(status, latest),
                "rejection_reasons": all_rejection_reasons,
            }
        )

    return {
        "review_bundle_path": str(review_bundle_path),
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
        for row in bucket_rows:
            domain = row["domain"]
            if bucket == "proven":
                example = row.get("proven_example") or {}
                lines.append(
                    f"- `{domain}`: `{example.get('question', '')}` -> `{example.get('answer', '')}`"
                )
                continue
            if bucket == "rejected_only":
                reasons = row.get("rejection_reasons", [])
                rendered_reasons = ", ".join(f"`{reason}`" for reason in reasons) or "`unknown`"
                lines.append(f"- `{domain}`: {rendered_reasons}")
                continue
            if bucket == "error":
                latest = row.get("latest_run") or {}
                status = latest.get("status", "error")
                message = latest.get("error_message", "") or latest.get("notes", {}).get(
                    "error_message",
                    "",
                )
                detail = row.get("status_detail") or {}
                detail_text = _render_status_detail(detail)
                if detail_text:
                    lines.append(f"- `{domain}`: `{status}`; `{message}`; {detail_text}")
                else:
                    lines.append(f"- `{domain}`: `{status}`; `{message}`")
                continue
            latest = row.get("latest_run") or {}
            status = latest.get("status", "untracked")
            detail = row.get("status_detail") or {}
            detail_text = _render_status_detail(detail)
            if detail_text:
                lines.append(f"- `{domain}`: `{status}`; {detail_text}")
            else:
                lines.append(f"- `{domain}`: `{status}`")
    return "\n".join(lines) + "\n"


def _resolve_template_status(
    domain: str,
    proven_map: dict[str, dict[str, str]],
    latest_result: dict[str, Any],
    filtered_reasons: list[str],
) -> str:
    """Resolve one canonical current status for a template."""
    if domain in proven_map:
        return "proven"
    status = str(latest_result.get("status", "")).strip()
    if status == "accepted" and filtered_reasons:
        return "rejected_only"
    if status == "rejected_only":
        return "rejected_only"
    if status.startswith("error:"):
        return "error"
    if status == "no_result":
        return "unproven_no_result"
    return "untracked"


def _build_status_detail(status: str, latest_result: dict[str, Any]) -> dict[str, Any]:
    """Return a normalized explanation payload for the current status."""
    domain = str(latest_result.get("domain", "")).strip()
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
        if domain in NO_ROOM_FOR_REFINEMENT_NO_RESULT_DOMAINS:
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
        if domain in NO_ROOM_FOR_REFINEMENT_NO_RESULT_DOMAINS:
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


def _sparse_answer_tag(latest_result: dict[str, Any]) -> str:
    """Return a normalized sparse-answer tag keyed by the run target time."""
    target_time = str(latest_result.get("target_time", "")).strip()
    if not target_time:
        return ""
    normalized = target_time.replace("-", "_")
    return f"sparse_answer_{normalized}"


def _unique_templates_by_domain() -> list[Any]:
    """Return templates deduplicated by domain key, keeping the first catalog entry."""
    unique = []
    seen_domains: set[str] = set()
    for template in get_all_templates():
        if template.domain in seen_domains:
            continue
        seen_domains.add(template.domain)
        unique.append(template)
    return unique


def collect_latest_accepted_records(accepted_paths: list[Path]) -> dict[str, dict[str, Any]]:
    """Return the latest accepted record per domain with current invalid reasons."""
    latest: dict[str, dict[str, Any]] = {}
    for path in accepted_paths:
        records = read_jsonl(path)
        if not records:
            continue
        invalid_reason_resolver = _load_invalid_reason_resolver()
        for record in records:
            domain = str(record.get("domain", "")).strip()
            if not domain:
                continue
            latest[domain] = {
                "source_path": str(path),
                "record": record,
                "invalid_reasons": invalid_reason_resolver(record),
            }
    return latest


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
