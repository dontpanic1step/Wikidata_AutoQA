"""Build an ordered review bundle from accepted runs."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.domain_templates import RETIRED_TEMPLATE_NOTES, get_template_by_key
from wikidata_simpleqa.models import CandidateFact
from wikidata_simpleqa.subject_resources import canonical_subject_resource
from wikidata_simpleqa.validators import (
    candidate_matches_topic_constraints,
    question_leaks_answer,
    question_leaks_location_answer_context,
)
from wikidata_simpleqa.workflow import review_run_artifacts


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def _subject_resource_key(record: dict) -> str:
    """Return the canonical subject-resource key for a stored record."""
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


def _record_template_key(record: dict) -> str:
    """Return the template key from canonical or legacy artifact fields."""
    for field in ("template_key", "legacy_domain", "domain"):
        value = str(record.get(field, "")).strip()
        if value:
            return value
    return ""


def record_invalid_reasons(record: dict) -> list[str]:
    """Return deterministic reasons why a stored accepted record is no longer valid."""
    template_key = _record_template_key(record)
    if template_key in RETIRED_TEMPLATE_NOTES:
        return ["retired_template"]
    template = get_template_by_key(template_key)
    if template is None:
        return ["unknown_template"]
    candidate = CandidateFact(
        subject_qid=str(record.get("subject_qid", "")).strip(),
        subject_label=str(record.get("subject_label", "")).strip(),
        subject_aliases=[],
        domain=template.domain,
        topic=template.topic,
        answer_type=template.answer_type,
        question_family=template.question_family,
        subject_type_qids=[],
        target_property_pid=str(record.get("property_pid", "")).strip(),
        target_property_label="",
        answer_qids=[str(value) for value in record.get("answer_qids", [])],
        answer_labels=[str(record.get("answer", "")).strip()] if record.get("answer") else [],
        answer_aliases=[str(value) for value in record.get("answer_aliases", [])],
        date_property_pid=str(record.get("date_filter", {}).get("property", "")).strip(),
        date_value=str(record.get("date_filter", {}).get("value", "")).strip(),
        target_time=str(record.get("target_time", "")).strip(),
        canonical_question=str(record.get("canonical_question", record.get("question", ""))).strip(),
        rewritten_question=str(record.get("rewritten_question", "")).strip() or None,
        subject_resource_url=str(record.get("subject_resource_url", "")).strip(),
        subject_resource_key=_subject_resource_key(record),
        source_metadata=dict(record.get("source_metadata", {})),
    )
    question = str(record.get("question", "")).strip()
    reasons: list[str] = []
    if question_leaks_answer(question, candidate.answer_labels):
        reasons.append("answer_leaked_in_question")
    if question_leaks_location_answer_context(question, candidate):
        reasons.append("location_context_leaked")
    if not candidate_matches_topic_constraints(candidate, template):
        reasons.append("subject_topic_mismatch")
    return reasons


def main() -> int:
    ordered_sources = [
        (artifact.source_name, artifact.accepted_path)
        for artifact in review_run_artifacts(ROOT)
    ]
    rows: list[dict[str, str]] = []
    seen_template_keys: set[str] = set()
    seen_questions: set[str] = set()
    seen_subject_resources: set[str] = set()

    for source_name, path in ordered_sources:
        for record in _read_jsonl(path):
            template_key = _record_template_key(record)
            question = str(record.get("question", "")).strip()
            subject_resource_key = _subject_resource_key(record)
            if record_invalid_reasons(record):
                continue
            if not template_key or template_key in seen_template_keys:
                continue
            if question and question in seen_questions:
                continue
            if subject_resource_key and subject_resource_key in seen_subject_resources:
                continue
            rows.append(
                {
                    "domain": str(record.get("template_domain", record.get("topic", record.get("domain", "")))).strip(),
                    "template_key": template_key,
                    "question_family": str(record.get("question_family", "")).strip(),
                    "question": question,
                    "answer": str(record.get("answer", "")).strip(),
                    "source_run": source_name,
                }
            )
            seen_template_keys.add(template_key)
            if question:
                seen_questions.add(question)
            if subject_resource_key:
                seen_subject_resources.add(subject_resource_key)

    tsv_path = ROOT / "outputs" / "review_2026_all_generated_qas.tsv"
    md_path = ROOT / "outputs" / "review_2026_all_generated_qas.md"

    with tsv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["template_key", "domain", "question_family", "question", "answer", "source_run"])
        for row in rows:
            writer.writerow(
                [
                    row["template_key"],
                    row["domain"],
                    row["question_family"],
                    row["question"],
                    row["answer"],
                    row["source_run"],
                ]
            )

    lines = [
        "# 2026 Generated QA Review",
        "",
        f"- Review rows: `{len(rows)}`",
        "",
        "| Template | Domain | Question Family | Question | Reference Answer | Source Run |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['template_key']} | {row['domain']} | {row['question_family']} | {row['question']} | {row['answer']} | {row['source_run']} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(rows), "tsv_path": str(tsv_path), "md_path": str(md_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
