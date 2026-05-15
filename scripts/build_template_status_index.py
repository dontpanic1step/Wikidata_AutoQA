"""Build the canonical template-status index from current run artifacts."""

from __future__ import annotations

import json
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.template_status import (  # noqa: E402
    build_template_status_index,
    render_template_status_markdown,
)
from wikidata_simpleqa.workflow import (  # noqa: E402
    status_accepted_paths,
    status_rejected_paths,
    status_summary_paths,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--status-mode",
        choices=["latest_live_status", "best_known_semantic_status"],
        default="latest_live_status",
        help="Choose whether current_status reflects the newest live run or the best known semantic verdict.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    index = build_template_status_index(
        review_bundle_path=ROOT / "outputs" / "review_2026_all_generated_qas.tsv",
        summary_paths=status_summary_paths(ROOT),
        rejected_paths=status_rejected_paths(ROOT),
        accepted_paths=status_accepted_paths(ROOT),
        status_mode=args.status_mode,
    )
    json_path = ROOT / "outputs" / "template_status_index.json"
    md_path = ROOT / "docs" / "template_status_index.md"
    json_path.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_template_status_markdown(index), encoding="utf-8")
    print(
        json.dumps(
            {
                "json_path": str(json_path),
                "md_path": str(md_path),
                "status_mode": args.status_mode,
                "counts": index["counts"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
