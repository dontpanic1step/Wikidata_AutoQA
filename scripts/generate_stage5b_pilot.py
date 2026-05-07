"""Generate a Stage 5B pilot with active, multi-hop, and date-answer templates."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.config import Settings
from wikidata_simpleqa.domain_templates import get_stage5b_templates
from wikidata_simpleqa.io import write_jsonl
from wikidata_simpleqa.pipeline import run_pipeline_for_templates
from wikidata_simpleqa.wikidata_client import WikidataClient

RESUME_VERSION = 5


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def _renumber_ids(records: list[dict], prefix: str) -> list[dict]:
    renumbered: list[dict] = []
    for index, record in enumerate(records, start=1):
        updated = dict(record)
        updated["id"] = f"{prefix}_{index:06d}"
        renumbered.append(updated)
    return renumbered


def _read_resume_manifest(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    accepted: list[dict] = []
    rejected: list[dict] = []
    template_results: list[dict[str, object]] = []
    accepted_domains: set[str] = set()

    for template in get_stage5b_templates():
        accepted_tmp_path = ROOT / "outputs" / f"tmp_stage5b_{template.domain}_accepted.jsonl"
        rejected_tmp_path = ROOT / "outputs" / f"tmp_stage5b_{template.domain}_rejected.jsonl"
        resume_manifest_path = ROOT / "outputs" / f"tmp_stage5b_{template.domain}_resume.json"
        resume_manifest = _read_resume_manifest(resume_manifest_path)
        can_resume = bool(
            resume_manifest
            and resume_manifest.get("resume_version") == RESUME_VERSION
            and resume_manifest.get("domain") == template.domain
            and resume_manifest.get("target_time") == "2026"
        )
        cached_accepted = _read_jsonl(accepted_tmp_path) if can_resume else []
        cached_rejected = _read_jsonl(rejected_tmp_path) if can_resume else []
        if can_resume and (cached_accepted or cached_rejected):
            accepted.extend(cached_accepted[:1])
            if cached_accepted:
                accepted_domains.add(template.domain)
            rejected.extend(cached_rejected)
            template_results.append(
                {
                    "domain": template.domain,
                    "accepted": len(cached_accepted),
                    "rejected": len(cached_rejected),
                    "status": "resumed_from_cache",
                }
            )
            continue

        settings = Settings(
            target_time="2026",
            pilot_total=1,
            harvest_limit_per_template=5,
            output_path=accepted_tmp_path,
            rejected_output_path=rejected_tmp_path,
            cache_dir=ROOT / "cache" / "wikidata",
        )
        last_error = None
        last_error_message = None
        client = None
        for attempt in range(3):
            client = WikidataClient(
                user_agent=settings.user_agent,
                proxy=settings.proxy,
                timeout_seconds=settings.timeout_seconds,
                cache_dir=settings.cache_dir,
            )
            try:
                result = run_pipeline_for_templates(settings=settings, templates=[template], client=client)
                accepted.extend(result.accepted[:1])
                if result.accepted:
                    accepted_domains.add(template.domain)
                rejected.extend(result.rejected)
                template_results.append(
                    {
                        "domain": template.domain,
                        "accepted": len(result.accepted),
                        "rejected": len(result.rejected),
                        "status": "ok" if attempt == 0 else f"ok_after_retry_{attempt}",
                        "telemetry": result.telemetry,
                    }
                )
                resume_manifest_path.write_text(
                    json.dumps(
                        {
                            "resume_version": RESUME_VERSION,
                            "domain": template.domain,
                            "target_time": "2026",
                        },
                        indent=2,
                    )
                    + "\n",
                    encoding="utf-8",
                )
                last_error = None
                break
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                last_error_message = str(exc)
                time.sleep(3)
        if last_error is not None:
            template_results.append(
                {
                    "domain": template.domain,
                    "accepted": 0,
                    "rejected": 0,
                    "status": f"error:{type(last_error).__name__}",
                    "error_message": last_error_message,
                    "telemetry": client.stats_snapshot() if client is not None else {},
                }
            )
        time.sleep(1)

    accepted_path = ROOT / "outputs" / "stage5b_pilot_accepted.jsonl"
    rejected_path = ROOT / "outputs" / "stage5b_pilot_rejected.jsonl"
    summary_path = ROOT / "outputs" / "stage5b_pilot_summary.json"

    accepted = _renumber_ids(accepted, "wikidata_verified_stage5b")
    write_jsonl(accepted_path, accepted)
    write_jsonl(rejected_path, rejected)
    summary_path.write_text(
        json.dumps(
            {
                "accepted_total": len(accepted),
                "rejected_total": len(rejected),
                "accepted_domains": sorted(accepted_domains),
                "missing_domains": [
                    template.domain
                    for template in get_stage5b_templates()
                    if template.domain not in accepted_domains
                ],
                "template_results": template_results,
                "accepted_path": str(accepted_path),
                "rejected_path": str(rejected_path),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(summary_path.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
