"""Generate one example for each template that has not yet been proven in runs."""

from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.config import Settings
from wikidata_simpleqa.domain_templates import get_all_templates
from wikidata_simpleqa.io import write_jsonl
from wikidata_simpleqa.pipeline import run_pipeline_for_templates
from wikidata_simpleqa.subject_resources import canonical_subject_resource
from wikidata_simpleqa.wikidata_client import WikidataClient

RESUME_VERSION = 2


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def _read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _renumber_ids(records: list[dict], prefix: str) -> list[dict]:
    renumbered: list[dict] = []
    for index, record in enumerate(records, start=1):
        updated = dict(record)
        updated["id"] = f"{prefix}_{index:06d}"
        renumbered.append(updated)
    return renumbered


def _subject_resource_key(record: dict) -> str:
    """Return the canonical subject-resource key stored in an output record."""
    resource_key = str(record.get("subject_resource_key", "")).strip()
    if resource_key:
        return resource_key
    resource_url = str(record.get("subject_resource_url", "")).strip()
    if resource_url:
        return resource_url
    subject_qid = str(record.get("subject_qid", "")).strip()
    if subject_qid:
        _, fallback_key = canonical_subject_resource(subject_qid)
        return fallback_key
    return ""


def _aggregate_problem_counts(results: list[dict[str, object]]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for result in results:
        for event in result.get("telemetry", {}).get("events", []):
            if event.get("status") == "error":
                error_type = str(event.get("error_type", "unknown"))
                counter[f"request_error:{error_type}"] += 1
                message = str(event.get("error_message", ""))
                if "429" in message:
                    counter["network_limit:http_429"] += 1
                if "timed out" in message.lower() or "timeout" in message.lower():
                    counter["network_limit:timeout"] += 1
        for problem in result.get("telemetry", {}).get("problems", []):
            kind = str(problem.get("kind", "unknown"))
            counter[f"problem:{kind}"] += 1
        status = str(result.get("status", ""))
        if status == "no_result":
            counter["outcome:no_result"] += 1
        elif status == "rejected_only":
            counter["outcome:rejected_only"] += 1
        elif status.startswith("error:"):
            counter[status] += 1
    return dict(sorted(counter.items()))


def _write_run_notes(path: Path, summary: dict[str, object]) -> None:
    lines = [
        "# 2026 Unproven Template Sweep Notes",
        "",
        f"- Target time: `{summary['target_time']}`",
        f"- Templates attempted: `{summary['template_total']}`",
        f"- Accepted templates: `{summary['accepted_total']}`",
        f"- Rejected-only templates: `{len(summary['rejected_only_domains'])}`",
        f"- No-result templates: `{len(summary['no_result_domains'])}`",
        f"- Error templates: `{len(summary['error_domains'])}`",
        "",
        "## Problem Summary",
        "",
    ]
    problem_counts = summary["problem_counts"]
    if problem_counts:
        for key, value in problem_counts.items():
            lines.append(f"- `{key}`: `{value}`")
    else:
        lines.append("- No recurring problems recorded.")
    lines.extend(
        [
            "",
            "## No-Result Templates",
            "",
        ]
    )
    if summary["no_result_domains"]:
        for domain in summary["no_result_domains"]:
            lines.append(f"- `{domain}`")
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Error Templates",
            "",
        ]
    )
    if summary["error_domains"]:
        for domain in summary["error_domains"]:
            lines.append(f"- `{domain}`")
    else:
        lines.append("- None")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    templates = [
        template
        for template in get_all_templates()
        if template.evidence_status != "proven_in_runs"
    ]
    accepted: list[dict] = []
    rejected: list[dict] = []
    template_results: list[dict[str, object]] = []
    accepted_domains: set[str] = set()
    rejected_only_domains: list[str] = []
    no_result_domains: list[str] = []
    error_domains: list[str] = []
    seen_questions: set[str] = set()
    seen_subject_resources: set[str] = set()

    for prior_path in (
        ROOT / "outputs" / "stage5b_pilot_accepted.jsonl",
        ROOT / "outputs" / "stage5_pilot_accepted.jsonl",
    ):
        for record in _read_jsonl(prior_path):
            question = str(record.get("question", "")).strip()
            if question:
                seen_questions.add(question)
            resource_key = _subject_resource_key(record)
            if resource_key:
                seen_subject_resources.add(resource_key)

    for template in templates:
        accepted_tmp_path = ROOT / "outputs" / f"tmp_unproven_{template.domain}_accepted.jsonl"
        rejected_tmp_path = ROOT / "outputs" / f"tmp_unproven_{template.domain}_rejected.jsonl"
        resume_manifest_path = ROOT / "outputs" / f"tmp_unproven_{template.domain}_resume.json"
        resume_manifest = _read_json(resume_manifest_path)
        can_resume = bool(
            resume_manifest
            and resume_manifest.get("resume_version") == RESUME_VERSION
            and resume_manifest.get("domain") == template.domain
            and resume_manifest.get("target_time") == "2026"
        )
        cached_accepted = _read_jsonl(accepted_tmp_path) if can_resume else []
        cached_rejected = _read_jsonl(rejected_tmp_path) if can_resume else []
        if can_resume:
            accepted.extend(cached_accepted[:1])
            rejected.extend(cached_rejected)
            for record in cached_accepted[:1]:
                question = str(record.get("question", "")).strip()
                if question:
                    seen_questions.add(question)
                resource_key = _subject_resource_key(record)
                if resource_key:
                    seen_subject_resources.add(resource_key)
            status = str(resume_manifest.get("status", "resumed_from_cache"))
            if cached_accepted:
                accepted_domains.add(template.domain)
            elif status == "rejected_only":
                rejected_only_domains.append(template.domain)
            elif status == "no_result":
                no_result_domains.append(template.domain)
            elif status.startswith("error:"):
                error_domains.append(template.domain)
            template_results.append(
                {
                    "domain": template.domain,
                    "accepted": len(cached_accepted),
                    "rejected": len(cached_rejected),
                    "status": status,
                    "telemetry": resume_manifest.get("telemetry", {}),
                    "notes": resume_manifest.get("notes", {}),
                }
            )
            continue

        settings = Settings(
            target_time="2026",
            pilot_total=1,
            harvest_limit_per_template=10,
            output_path=accepted_tmp_path,
            rejected_output_path=rejected_tmp_path,
            cache_dir=ROOT / "cache" / "wikidata",
        )
        client = WikidataClient(
            user_agent=settings.user_agent,
            proxy=settings.proxy,
            timeout_seconds=settings.timeout_seconds,
            cache_dir=settings.cache_dir,
        )
        status = "no_result"
        notes: dict[str, object] = {}
        try:
            result = run_pipeline_for_templates(
                settings=settings,
                templates=[template],
                client=client,
                seen_questions=seen_questions,
                seen_subject_resources=seen_subject_resources,
            )
            accepted.extend(result.accepted[:1])
            rejected.extend(result.rejected)
            if result.accepted:
                accepted_domains.add(template.domain)
                status = "accepted"
            elif result.rejected:
                rejected_only_domains.append(template.domain)
                status = "rejected_only"
                notes["rejection_reasons"] = sorted(
                    {record.get("reason", "unknown") for record in result.rejected}
                )
            else:
                no_result_domains.append(template.domain)
                status = "no_result"
        except Exception as exc:  # noqa: BLE001
            error_domains.append(template.domain)
            status = f"error:{type(exc).__name__}"
            notes["error_message"] = str(exc)
        template_result = {
            "domain": template.domain,
            "accepted": 1 if status == "accepted" else 0,
            "rejected": len(_read_jsonl(rejected_tmp_path)),
            "status": status,
            "telemetry": client.stats_snapshot(),
            "notes": notes,
        }
        template_results.append(template_result)
        resume_manifest_path.write_text(
            json.dumps(
                {
                    "resume_version": RESUME_VERSION,
                    "domain": template.domain,
                    "target_time": "2026",
                    "status": status,
                    "telemetry": client.stats_snapshot(),
                    "notes": notes,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        time.sleep(1)

    accepted_path = ROOT / "outputs" / "unproven_templates_2026_accepted.jsonl"
    rejected_path = ROOT / "outputs" / "unproven_templates_2026_rejected.jsonl"
    summary_path = ROOT / "outputs" / "unproven_templates_2026_summary.json"
    notes_path = ROOT / "outputs" / "unproven_templates_2026_notes.md"

    accepted = _renumber_ids(accepted, "wikidata_verified_unproven_2026")
    write_jsonl(accepted_path, accepted)
    write_jsonl(rejected_path, rejected)

    summary = {
        "target_time": "2026",
        "template_total": len(templates),
        "accepted_total": len(accepted),
        "rejected_total": len(rejected),
        "accepted_domains": sorted(accepted_domains),
        "rejected_only_domains": sorted(rejected_only_domains),
        "no_result_domains": sorted(no_result_domains),
        "error_domains": sorted(error_domains),
        "problem_counts": _aggregate_problem_counts(template_results),
        "template_results": template_results,
        "accepted_path": str(accepted_path),
        "rejected_path": str(rejected_path),
    }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    _write_run_notes(notes_path, summary)
    print(summary_path.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
