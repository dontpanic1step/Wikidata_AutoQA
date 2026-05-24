"""Build a reviewer-facing markdown view for accepted Route 3 QAs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-id",
        default="",
        help=(
            "Run id used to infer outputs/<run-id>_accepted.jsonl and "
            "docs/walkthroughs/<run-id>_accepted_qa_review.md."
        ),
    )
    parser.add_argument("--accepted-input", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    """Build the accepted QA review markdown."""
    args = parse_args()
    accepted_input = _accepted_input_path(args)
    output = _output_path(args, accepted_input)
    records = _read_jsonl(accepted_input)
    run_id = args.run_id.strip() or accepted_input.name.removesuffix("_accepted.jsonl")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        _render_review(run_id=run_id, accepted_input=accepted_input, records=records),
        encoding="utf-8",
    )
    print(output)
    print(f"accepted_records={len(records)}")
    return 0


def _accepted_input_path(args: argparse.Namespace) -> Path:
    """Return the accepted JSONL path."""
    if args.accepted_input is not None:
        return args.accepted_input
    run_id = args.run_id.strip()
    if not run_id:
        raise ValueError("Pass --run-id or --accepted-input.")
    return ROOT / "outputs" / f"{run_id}_accepted.jsonl"


def _output_path(args: argparse.Namespace, accepted_input: Path) -> Path:
    """Return the review markdown output path."""
    if args.output is not None:
        return args.output
    run_id = args.run_id.strip() or accepted_input.name.removesuffix("_accepted.jsonl")
    return ROOT / "docs" / "walkthroughs" / f"{run_id}_accepted_qa_review.md"


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read JSONL records."""
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def _render_review(
    *,
    run_id: str,
    accepted_input: Path,
    records: list[dict[str, Any]],
) -> str:
    """Render the full review document."""
    lines = [
        f"# Accepted QA Review: `{run_id}`",
        "",
        f"Source accepted JSONL: `{accepted_input}`",
        "",
        f"Accepted records: {len(records)}",
        "",
        (
            "Each section shows the accepted QA, answer type, page URL, the corresponding "
            "rendered source table, and the two second-stage small-model answers with "
            "judge result and judge reason."
        ),
        "",
        (
            "`Model-selected provided table rank` is the 1-based rank of the source table "
            "chosen by the generation model within the post-filter, score-ranked tables "
            "that were included in the generation prompt; it is not the page's raw table index."
        ),
        "",
    ]
    for index, record in enumerate(records, start=1):
        lines.extend(_render_record(index, record))
    return "\n".join(lines).rstrip() + "\n"


def _render_record(index: int, record: dict[str, Any]) -> list[str]:
    """Render one accepted QA section."""
    metadata = _metadata(record)
    source_table = metadata.get("selected_source_table") or {}
    if not isinstance(source_table, dict):
        source_table = {}
    table_index = source_table.get("table_index")
    rank, rank_total, score = _selected_table_rank(metadata, table_index)
    page_url = _page_url(record, metadata)
    answer_type = _clean(record.get("answer_type") or metadata.get("answer_type"))
    recipe_answer_type = _clean(metadata.get("recipe_answer_type"))
    table_description = _source_table_description(source_table)
    rank_text = (
        f"`{rank}/{rank_total}` (score `{score}`)"
        if rank is not None
        else "`n/a`"
    )
    lines = [
        f"## {index}. {_clean(record.get('question'))}",
        "",
        f"Answer type: `{answer_type}`"
        + (
            f" (recipe segment `{recipe_answer_type}`)"
            if recipe_answer_type and recipe_answer_type != answer_type
            else ""
        ),
        "",
        f"Reference answer: **{_clean(record.get('answer'))}**",
        "",
        f"Page URL: [{page_url}]({page_url})" if page_url else "Page URL: n/a",
        "",
        table_description,
        "",
        f"Model-selected provided table rank: {rank_text}",
        "",
        f"<details open><summary>Rendered source table for QA {index}</summary>",
        "",
        _clean(source_table.get("markdown")) or "n/a",
        "",
        "</details>",
        "",
    ]
    panel = record.get("panel_grading_features")
    if not isinstance(panel, dict):
        panel = {}
    models = panel.get("models")
    if not isinstance(models, list) or not models:
        lines.extend(["Second-stage model answers: n/a", ""])
        return lines
    for model in models:
        if isinstance(model, dict):
            lines.extend(_render_model_grading(model))
    return lines


def _metadata(record: dict[str, Any]) -> dict[str, Any]:
    """Return source metadata when present."""
    metadata = record.get("source_metadata")
    return metadata if isinstance(metadata, dict) else {}


def _page_url(record: dict[str, Any], metadata: dict[str, Any]) -> str:
    """Return the best page URL for a record."""
    evidence = record.get("evidence")
    if not isinstance(evidence, dict):
        evidence = {}
    return _clean(metadata.get("canonical_url") or evidence.get("url") or metadata.get("source_url"))


def _source_table_description(source_table: dict[str, Any]) -> str:
    """Return one-line source table metadata."""
    parts = [
        f"Source table: table `{source_table.get('table_index')}`",
        f"type `{_clean(source_table.get('table_type'))}`",
    ]
    section = _clean(source_table.get("section_heading"))
    caption = _clean(source_table.get("caption"))
    if section:
        parts.append(f"section `{section}`")
    if caption:
        parts.append(f"caption `{caption}`")
    return ", ".join(parts)


def _selected_table_rank(
    metadata: dict[str, Any],
    selected_table_index: Any,
) -> tuple[int | None, int, Any]:
    """Return selected table rank among prompt-provided tables."""
    table_selection = metadata.get("table_selection")
    if not isinstance(table_selection, list):
        return None, 0, None
    provided_rows = [
        row
        for row in table_selection
        if isinstance(row, dict)
        and not _clean(row.get("table_filter_rejection_reason"))
        and not row.get("below_min_table_score")
        and not _clean(row.get("live_scope_rejection_reason"))
    ][:3]
    for rank, row in enumerate(provided_rows, start=1):
        if row.get("table_index") == selected_table_index:
            return rank, len(provided_rows), row.get("score")
    return None, len(provided_rows), None


def _render_model_grading(model: dict[str, Any]) -> list[str]:
    """Render one second-stage model result."""
    return [
        f"**{_model_label(model.get('model'))}**",
        "",
        "Model response:",
        "",
        _blockquote(model.get("predicted_answer")),
        "",
        f"Judge result: `{_clean(model.get('grade')) or 'n/a'}`",
        "",
        "Judge reason:",
        "",
        _blockquote(model.get("reason")),
        "",
    ]


def _model_label(model: Any) -> str:
    """Return a compact display label for known model ids."""
    value = _clean(model)
    labels = {
        "openai/gpt-4.1-mini": "GPT-4.1-mini",
        "google/gemini-3-flash-preview": "Gemini-3-flash",
    }
    return labels.get(value, value or "Model")


def _blockquote(value: Any) -> str:
    """Render text as a markdown blockquote."""
    text = _clean(value)
    if not text:
        return "> n/a"
    return "\n".join(f"> {line}" if line else ">" for line in text.splitlines())


def _clean(value: Any) -> str:
    """Return a stripped string."""
    return str(value or "").strip()


if __name__ == "__main__":
    raise SystemExit(main())
