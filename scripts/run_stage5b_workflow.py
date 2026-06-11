"""Run the Stage 5B workflow in explicit offline, live, rebuild, and report phases."""

from __future__ import annotations

import argparse
import os
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.config import Settings
from wikidata_simpleqa.domain_templates import get_template_by_key
from wikidata_simpleqa.io import write_jsonl
from wikidata_simpleqa.pipeline import run_pipeline_for_templates
from wikidata_simpleqa.wikidata_client import WikidataClient
from wikidata_simpleqa.workflow import (
    default_policy_registry_path,
    load_policy_registry,
    render_problem_backlog_markdown,
    render_policy_registry_markdown,
    summarize_phase_result,
)


DEFAULT_OFFLINE_TESTS = [
    "tests.test_time_invariance",
    "tests.test_composed_harvester",
    "tests.test_domain_templates",
    "tests.test_build_review_bundle",
    "tests.test_workflow",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phases",
        nargs="+",
        choices=["offline", "live", "rebuild", "report"],
        default=["offline", "rebuild", "report"],
    )
    parser.add_argument("--target-time", type=str, default="2026")
    parser.add_argument("--template-keys", "--domains", dest="template_keys", nargs="*", default=[])
    parser.add_argument("--pilot-total", type=int, default=1)
    parser.add_argument("--harvest-limit", type=int, default=3)
    parser.add_argument("--proxy", type=str, default="none")
    parser.add_argument(
        "--no-proxy",
        action="store_true",
        help="Disable proxy use for the live phase.",
    )
    parser.add_argument(
        "--run-name",
        type=str,
        default="workflow_focus",
        help="Output prefix used by the optional live phase.",
    )
    parser.add_argument(
        "--offline-tests",
        nargs="*",
        default=DEFAULT_OFFLINE_TESTS,
        help="Python unittest module names for the offline phase.",
    )
    parser.add_argument(
        "--report-output",
        type=Path,
        default=ROOT / "outputs" / "workflow_last_run_summary.json",
    )
    parser.add_argument(
        "--report-markdown",
        type=Path,
        default=ROOT / "outputs" / "workflow_last_run_summary.md",
    )
    return parser.parse_args()


def _run_subprocess(command: list[str], *, extra_env: dict[str, str] | None = None) -> dict[str, object]:
    """Run a subprocess and return a concise structured result."""
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False, env=env)
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def run_offline_phase(test_modules: list[str]) -> dict[str, object]:
    """Run deterministic local validation without touching the network."""
    pythonpath_parts = [str(ROOT / "tests"), str(ROOT / "src")]
    existing_pythonpath = os.environ.get("PYTHONPATH", "").strip()
    if existing_pythonpath:
        pythonpath_parts.append(existing_pythonpath)
    result = _run_subprocess(
        [sys.executable, "-m", "unittest", *test_modules],
        extra_env={"PYTHONPATH": os.pathsep.join(pythonpath_parts)},
    )
    status = "completed" if result["returncode"] == 0 else "failed"
    return summarize_phase_result(
        "offline",
        status=status,
        details={
            "test_modules": test_modules,
            "returncode": result["returncode"],
            "stdout_tail": str(result["stdout"])[-4000:],
            "stderr_tail": str(result["stderr"])[-4000:],
        },
    )


def run_live_phase(
    *,
    target_time: str,
    template_keys: list[str],
    pilot_total: int,
    harvest_limit: int,
    proxy: str,
    run_name: str,
) -> dict[str, object]:
    """Run a focused live generation pass for the requested template keys."""
    templates = []
    for template_key in template_keys:
        template = get_template_by_key(template_key)
        if template is None:
            raise ValueError(f"Unknown template key: {template_key}")
        templates.append(template)

    output = ROOT / "outputs" / f"{run_name}_accepted.jsonl"
    rejected = ROOT / "outputs" / f"{run_name}_rejected.jsonl"
    combined_accepted: list[dict] = []
    combined_rejected: list[dict] = []
    template_results: list[dict[str, object]] = []
    backlog_items: list[dict[str, str]] = []

    for template in templates:
        settings = Settings(
            target_time=target_time,
            pilot_total=pilot_total,
            harvest_limit_per_template=harvest_limit,
            proxy=proxy or None,
            output_path=output,
            rejected_output_path=rejected,
        )
        client = WikidataClient(
            user_agent=settings.user_agent,
            proxy=settings.proxy,
            timeout_seconds=settings.timeout_seconds,
            cache_dir=settings.cache_dir,
        )
        try:
            result = run_pipeline_for_templates(
                settings=settings,
                templates=[template],
                client=client,
            )
            combined_accepted.extend(result.accepted)
            combined_rejected.extend(result.rejected)
            telemetry = result.telemetry
            has_request_errors = bool(telemetry.get("errors", 0))
            if result.accepted:
                status = "accepted"
            elif result.rejected:
                status = "rejected_only"
            elif has_request_errors:
                status = "no_result_with_request_errors"
            else:
                status = "no_result"
            template_results.append(
                {
                    "domain": template.template_key,
                    "status": status,
                    "accepted": len(result.accepted),
                    "rejected": len(result.rejected),
                    "telemetry": telemetry,
                    "error_message": "",
                }
            )
            if has_request_errors:
                backlog_items.append(
                    {
                        "scope": template.template_key,
                        "title": "Live run completed with request-layer errors",
                        "evidence": json.dumps(telemetry, ensure_ascii=False)[:500],
                        "next_step": "Review request events and decide whether the instability is query-specific or environment-specific.",
                    }
                )
        except Exception as exc:  # noqa: BLE001
            telemetry = client.stats_snapshot()
            error_message = f"{type(exc).__name__}: {exc}"
            template_results.append(
                {
                    "domain": template.template_key,
                    "status": f"error:{type(exc).__name__}",
                    "accepted": 0,
                    "rejected": 0,
                    "telemetry": telemetry,
                    "error_message": error_message,
                }
            )
            backlog_items.append(
                {
                    "scope": template.template_key,
                    "title": "Live confirmation failed before template-level conclusion",
                    "evidence": error_message,
                    "next_step": "Inspect proxy/network settings and rerun with a stable connection before drawing template conclusions.",
                }
            )

    write_jsonl(output, combined_accepted)
    write_jsonl(rejected, combined_rejected)
    problem_backlog_path = ROOT / "outputs" / f"{run_name}_problem_backlog.md"
    problem_backlog_path.write_text(
        render_problem_backlog_markdown(backlog_items),
        encoding="utf-8",
    )
    summary = {
        "target_time": target_time,
        "domains": domains,
        "accepted": len(combined_accepted),
        "rejected": len(combined_rejected),
        "output_path": str(output),
        "rejected_output_path": str(rejected),
        "problem_backlog_path": str(problem_backlog_path),
        "template_results": template_results,
    }
    summary_path = ROOT / "outputs" / f"{run_name}_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summarize_phase_result(
        "live",
        status="failed" if any(str(row["status"]).startswith("error:") for row in template_results) else "completed",
        details={
            "summary_path": str(summary_path),
            **summary,
        },
    )


def run_rebuild_phase() -> dict[str, object]:
    """Rebuild derived review and status artifacts plus the policy registry report."""
    commands = [
        [sys.executable, "scripts/export_template_catalog.py"],
        [sys.executable, "scripts/build_review_bundle.py"],
        [sys.executable, "scripts/build_template_status_index.py"],
        [sys.executable, "scripts/build_template_salvage_board.py"],
        [sys.executable, "scripts/build_template_portfolio_report.py"],
    ]
    command_results = [_run_subprocess(command) for command in commands]
    failed = [result for result in command_results if result["returncode"] != 0]

    decisions = load_policy_registry(default_policy_registry_path(ROOT))
    policy_md_path = ROOT / "outputs" / "policy_override_registry.md"
    policy_md_path.write_text(render_policy_registry_markdown(decisions), encoding="utf-8")

    return summarize_phase_result(
        "rebuild",
        status="failed" if failed else "completed",
        details={
            "commands": command_results,
            "policy_registry_path": str(default_policy_registry_path(ROOT)),
            "policy_registry_markdown": str(policy_md_path),
        },
    )


def collect_problem_backlog_items(phase_results: list[dict[str, object]]) -> list[dict[str, str]]:
    """Collect higher-level workflow issues from phase results."""
    items: list[dict[str, str]] = []
    for result in phase_results:
        phase = str(result.get("phase", "")).strip()
        status = str(result.get("status", "")).strip()
        details = result.get("details", {})
        if phase == "offline" and status == "failed":
            items.append(
                {
                    "scope": "offline",
                    "title": "Offline validation failed",
                    "evidence": str(details.get("stderr_tail", "")).strip(),
                    "next_step": "Fix the local test or import-path problem before treating later phases as trustworthy.",
                }
            )
        if phase == "live":
            for row in details.get("template_results", []):
                if not isinstance(row, dict):
                    continue
                row_status = str(row.get("status", "")).strip()
                if row_status.startswith("error:"):
                    items.append(
                        {
                            "scope": str(row.get("domain", "")).strip() or "live",
                            "title": "Template live run failed",
                            "evidence": str(row.get("error_message", "")).strip(),
                            "next_step": "Review whether the issue is query design, proxy configuration, WDQS instability, or a real executor bug.",
                        }
                    )
        if phase == "rebuild" and status == "failed":
            items.append(
                {
                    "scope": "rebuild",
                    "title": "Derived artifacts did not rebuild cleanly",
                    "evidence": json.dumps(details, ensure_ascii=False)[:500],
                    "next_step": "Fix the failing report/build command before relying on downstream summaries.",
                }
            )
    return items


def render_workflow_report(phase_results: list[dict[str, object]]) -> str:
    """Render a human-readable Markdown summary for the latest workflow run."""
    lines = [
        "# Stage 5B Workflow Run",
        "",
        "| Phase | Status | Detail |",
        "|---|---|---|",
    ]
    for result in phase_results:
        phase = str(result.get("phase", "")).strip()
        status = str(result.get("status", "")).strip()
        details = result.get("details", {})
        detail_text = json.dumps(details, ensure_ascii=False)
        if len(detail_text) > 240:
            detail_text = detail_text[:237] + "..."
        lines.append(f"| {phase} | {status} | {detail_text} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    phase_results: list[dict[str, object]] = []

    for phase in args.phases:
        if phase == "offline":
            phase_results.append(run_offline_phase(args.offline_tests))
            continue
        if phase == "live":
            if not args.template_keys:
                raise ValueError("--template-keys is required for the live phase")
            phase_results.append(
                run_live_phase(
                    target_time=args.target_time,
                    template_keys=args.template_keys,
                    pilot_total=args.pilot_total,
                    harvest_limit=args.harvest_limit,
                    proxy="" if args.no_proxy else args.proxy,
                    run_name=args.run_name,
                )
            )
            continue
        if phase == "rebuild":
            phase_results.append(run_rebuild_phase())
            continue
        if phase == "report":
            phase_results.append(
                summarize_phase_result(
                    "report",
                    status="completed",
                    details={"report_output": str(args.report_output)},
                )
            )

    args.report_output.write_text(
        json.dumps({"phases": phase_results}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    args.report_markdown.write_text(render_workflow_report(phase_results), encoding="utf-8")
    backlog_path = ROOT / "outputs" / "workflow_problem_backlog.md"
    backlog_items = collect_problem_backlog_items(phase_results)
    backlog_path.write_text(render_problem_backlog_markdown(backlog_items), encoding="utf-8")

    has_failure = any(result.get("status") == "failed" for result in phase_results)
    print(
        json.dumps(
            {
                "report_output": str(args.report_output),
                "report_markdown": str(args.report_markdown),
                "problem_backlog": str(backlog_path),
                "phases": phase_results,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 1 if has_failure else 0


if __name__ == "__main__":
    raise SystemExit(main())
