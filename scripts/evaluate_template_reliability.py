"""Render pass-rate style reliability summaries for selected templates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.template_status import build_template_status_index  # noqa: E402
from wikidata_simpleqa.workflow import (  # noqa: E402
    status_accepted_paths,
    status_rejected_paths,
    status_summary_paths,
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--domains",
        nargs="+",
        required=True,
        help="One or more template domains to summarize.",
    )
    parser.add_argument(
        "--status-mode",
        choices=["latest_live_status", "best_known_semantic_status"],
        default="best_known_semantic_status",
        help="Choose which status view to include as current_status in the report.",
    )
    parser.add_argument(
        "--output-prefix",
        default="template_reliability",
        help="Output prefix written under outputs/ as <prefix>.json and <prefix>.md.",
    )
    return parser.parse_args()


def render_markdown(rows: list[dict[str, object]], *, status_mode: str) -> str:
    """Render a concise Markdown report for selected reliability rows."""
    lines = [
        "# Template Reliability Report",
        "",
        f"- Status mode: `{status_mode}`",
        "",
        "| Domain | Current | Live | Semantic | Pass Rate | Candidate Yield | Semantic Repro | Avg Network Requests |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        reliability = row.get("reliability", {})
        pass_rate = _format_ratio(
            reliability.get("request_clean_runs"),
            reliability.get("total_runs"),
        )
        candidate_yield = _format_ratio(
            reliability.get("candidate_yield_runs"),
            reliability.get("total_runs"),
        )
        semantic_repro = reliability.get("semantic_repro_rate")
        semantic_repro_text = "-" if semantic_repro is None else f"{semantic_repro:.2f}"
        avg_network_requests = reliability.get("average_network_requests", "-")
        lines.append(
            "| {domain} | {current} | {live} | {semantic} | {pass_rate} | {candidate_yield} | {semantic_repro} | {avg_network_requests} |".format(
                domain=row["domain"],
                current=row["current_status"],
                live=row["latest_live_status"],
                semantic=row["best_known_semantic_status"],
                pass_rate=pass_rate,
                candidate_yield=candidate_yield,
                semantic_repro=semantic_repro_text,
                avg_network_requests=avg_network_requests,
            )
        )
    return "\n".join(lines) + "\n"


def _format_ratio(numerator: object, denominator: object) -> str:
    """Render a short ratio string for Markdown tables."""
    if numerator is None or denominator in {None, 0}:
        return "-"
    return f"{numerator}/{denominator}"


def main() -> int:
    """Build and write the selected reliability report."""
    args = parse_args()
    index = build_template_status_index(
        review_bundle_path=ROOT / "outputs" / "review_2026_all_generated_qas.tsv",
        summary_paths=status_summary_paths(ROOT),
        rejected_paths=status_rejected_paths(ROOT),
        accepted_paths=status_accepted_paths(ROOT),
        status_mode=args.status_mode,
    )
    row_map = {row["domain"]: row for row in index["templates"]}
    rows: list[dict[str, object]] = []
    missing = []
    for domain in args.domains:
        row = row_map.get(domain)
        if row is None:
            missing.append(domain)
            continue
        rows.append(row)
    if missing:
        raise ValueError(f"Unknown template domains: {', '.join(sorted(missing))}")

    payload = {
        "status_mode": args.status_mode,
        "domains": args.domains,
        "templates": rows,
    }
    output_json = ROOT / "outputs" / f"{args.output_prefix}.json"
    output_md = ROOT / "outputs" / f"{args.output_prefix}.md"
    output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    output_md.write_text(render_markdown(rows, status_mode=args.status_mode), encoding="utf-8")
    print(
        json.dumps(
            {
                "json_path": str(output_json),
                "md_path": str(output_md),
                "domains": args.domains,
                "status_mode": args.status_mode,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
