"""Build a recurring portfolio report for the template salvage program."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.template_portfolio import (  # noqa: E402
    build_portfolio_report,
    build_salvage_board,
    default_salvage_registry_path,
    load_salvage_registry,
    render_portfolio_report_markdown,
)
from wikidata_simpleqa.template_status import build_template_status_index  # noqa: E402
from wikidata_simpleqa.workflow import (  # noqa: E402
    status_accepted_paths,
    status_rejected_paths,
    status_summary_paths,
)


def main() -> int:
    """Build and write the template portfolio program report."""
    status_index = build_template_status_index(
        review_bundle_path=ROOT / "outputs" / "review_2026_all_generated_qas.tsv",
        summary_paths=status_summary_paths(ROOT),
        rejected_paths=status_rejected_paths(ROOT),
        accepted_paths=status_accepted_paths(ROOT),
        status_mode="best_known_semantic_status",
    )
    registry = load_salvage_registry(default_salvage_registry_path(ROOT))
    board = build_salvage_board(
        status_index=status_index,
        registry=registry,
    )
    report = build_portfolio_report(board, status_index)
    json_path = ROOT / "outputs" / "template_portfolio_report.json"
    md_path = ROOT / "outputs" / "template_portfolio_report.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_portfolio_report_markdown(report), encoding="utf-8")
    print(
        json.dumps(
            {
                "json_path": str(json_path),
                "md_path": str(md_path),
                "headline": report["headline"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
