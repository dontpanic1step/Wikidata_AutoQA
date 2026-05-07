"""Export the current template catalog for manual review."""

from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.domain_templates import get_all_templates


def _rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for template in get_all_templates():
        reasoning_recipe = template.reasoning_recipe or {}
        rows.append(
            {
                "domain": template.domain,
                "activation_status": template.status,
                "evidence_status": template.evidence_status,
                "evidence_runs": ",".join(template.evidence_runs),
                "evidence_notes": template.evidence_notes,
                "topic": template.topic,
                "answer_type": template.answer_type,
                "answer_format": template.answer_format,
                "temporal_mode": template.temporal_mode,
                "reasoning_style": template.reasoning_style,
                "composition_style": template.composition_style,
                "question_family": template.question_family,
                "subject_type_qid": template.subject_type_qid,
                "subject_type_label": template.subject_type_label,
                "date_property_pid": template.date_property_pid,
                "target_property_pid": template.target_property_pid,
                "target_property_label": template.target_property_label,
                "date_answer_granularity": template.date_answer_granularity or "",
                "exact_instance_only": str(template.exact_instance_only).lower(),
                "new_element_slot": str(reasoning_recipe.get("new_element_slot", "")),
                "new_element_hop": str(reasoning_recipe.get("new_element_hop", "")),
                "required_reasoning_clues": ",".join(reasoning_recipe.get("required_reasoning_clues", [])),
                "canonical_question_template": template.canonical_question_template,
            }
        )
    return rows


def _count_lines(rows: list[dict[str, str]], key: str) -> list[str]:
    counts = Counter(row[key] for row in rows)
    return [f"| {value} | {counts[value]} |" for value in sorted(counts)]


def _topic_lines(rows: list[dict[str, str]]) -> list[str]:
    counts = Counter(row["topic"] for row in rows)
    return [f"| {topic} | {counts[topic]} |" for topic in sorted(counts)]


def export_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    """Write the catalog as TSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def export_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    """Write the catalog as Markdown with axis-level stats."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporal_total = sum(1 for row in rows if row["temporal_mode"] != "atemporal")
    number_total = sum(1 for row in rows if row["answer_type"] == "Number" or row["answer_format"] == "number")
    date_total = sum(1 for row in rows if row["answer_format"] == "date")
    lines = [
        "# Template Catalog Review",
        "",
        "## Definitions",
        "",
        "- `activation_status`: where the template sits in the rollout lifecycle (`active`, `multi_hop_pilot`, `date_answer_pilot`, `blueprint`).",
        "- `evidence_status`: whether the template has already produced an accepted example in a recorded pilot run.",
        "- `temporal_mode`: `atemporal` for normal SimpleQA-style questions, `time_related_join` for compositional target-time joins, and `date_answer` for explicit date questions.",
        "",
        "## Headline Stats",
        "",
        f"- Total templates: `{len(rows)}`",
        f"- Number-answer templates: `{number_total}`",
        f"- Date-answer templates: `{date_total}`",
        f"- Time-related templates (including date-answer): `{temporal_total}`",
        "",
        "## Status Axis",
        "",
        "| Activation Status | Count |",
        "|---|---:|",
        *_count_lines(rows, "activation_status"),
        "",
        "## Evidence Axis",
        "",
        "| Evidence Status | Count |",
        "|---|---:|",
        *_count_lines(rows, "evidence_status"),
        "",
        "## Domain Axis",
        "",
        "| Topic | Count |",
        "|---|---:|",
        *_topic_lines(rows),
        "",
        "## Answer Type Axis",
        "",
        "| Answer Type | Count |",
        "|---|---:|",
        *_count_lines(rows, "answer_type"),
        "",
        "## Answer Format Axis",
        "",
        "| Answer Format | Count |",
        "|---|---:|",
        *_count_lines(rows, "answer_format"),
        "",
        "## Temporal Axis",
        "",
        "| Temporal Mode | Count |",
        "|---|---:|",
        *_count_lines(rows, "temporal_mode"),
        "",
        "## Full Catalog",
        "",
        "| Domain | Activation Status | Evidence Status | Topic | Answer Type | Answer Format | Temporal Mode | Reasoning Style | Subject Type | Date PID | Target PID | Runs | Canonical Template |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {domain} | {activation_status} | {evidence_status} | {topic} | {answer_type} | {answer_format} | {temporal_mode} | {reasoning_style} | {subject_type_label} ({subject_type_qid}) | {date_property_pid} | {target_property_pid} | {evidence_runs} | {canonical_question_template} |".format(
                **row
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    rows = _rows()
    export_tsv(ROOT / "outputs" / "template_catalog_review.tsv", rows)
    export_markdown(ROOT / "docs" / "template_catalog_review.md", rows)
    print(
        {
            "rows": len(rows),
            "tsv": str(ROOT / "outputs" / "template_catalog_review.tsv"),
            "markdown": str(ROOT / "docs" / "template_catalog_review.md"),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
