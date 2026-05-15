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

from wikidata_simpleqa.template_status import build_template_status_index
from wikidata_simpleqa.workflow import (
    status_accepted_paths,
    status_rejected_paths,
    status_summary_paths,
)


def _rows() -> list[dict[str, str]]:
    index = build_template_status_index(
        review_bundle_path=ROOT / "outputs" / "review_2026_all_generated_qas.tsv",
        summary_paths=status_summary_paths(ROOT),
        rejected_paths=status_rejected_paths(ROOT),
        accepted_paths=status_accepted_paths(ROOT),
        status_mode="latest_live_status",
    )
    rows: list[dict[str, str]] = []
    for template in index["templates"]:
        proven_example = template.get("proven_example") or {}
        rows.append(
            {
                "domain": str(template.get("topic", "")),
                "template": str(template.get("domain", "")),
                "canonical_question": str(template.get("canonical_question_template", "")),
                "status": str(template.get("current_status", "")),
                "activation_status": str(template.get("catalog_status", "")),
                "original_status": str(template.get("original_current_status", "")),
                "latest_live_status": str(template.get("latest_live_status", "")),
                "best_known_semantic_status": str(template.get("best_known_semantic_status", "")),
                "successful_generated_question": str(proven_example.get("question", "")),
            }
        )
    rows.sort(key=lambda row: (row["domain"], row["template"]))
    return rows


def _count_lines(rows: list[dict[str, str]], key: str) -> list[str]:
    counts = Counter(row[key] for row in rows)
    return [f"| {value} | {counts[value]} |" for value in sorted(counts)]


def export_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    """Write the catalog as TSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def export_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    """Write the catalog as Markdown with simple review stats."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Template Catalog Review",
        "",
        "## Headline Stats",
        "",
        f"- Total templates: `{len(rows)}`",
        "",
        "## Status Axis",
        "",
        "| Status | Count |",
        "|---|---:|",
        *_count_lines(rows, "status"),
        "",
        "## Activation Axis",
        "",
        "| Activation Status | Count |",
        "|---|---:|",
        *_count_lines(rows, "activation_status"),
        "",
        "## Original Status Axis",
        "",
        "| Original Status | Count |",
        "|---|---:|",
        *_count_lines(rows, "original_status"),
        "",
        "## Domain Axis",
        "",
        "| Domain | Count |",
        "|---|---:|",
        *_count_lines(rows, "domain"),
        "",
        "## Full Catalog",
        "",
        "| Domain | Template | Canonical Question | Status | Successful Generated Question |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {domain} | {template} | {canonical_question} | {status} | {successful_generated_question} |".format(
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
