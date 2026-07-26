"""Finalize reviewed Route 3 candidates into the formal CSV."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.cli_output import print_json_summary
from wikidata_simpleqa.public_ids import (
    load_public_id_registry,
    public_id_registry_lock,
    write_public_id_registry,
)
from wikidata_simpleqa.route3_finalization import finalize_review_state, write_final_csv
from wikidata_simpleqa.route3_review import load_review_state, read_review_workbook


def parse_args() -> argparse.Namespace:
    """Parse finalization arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-input", type=Path, required=True)
    parser.add_argument("--xlsx-input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--id-registry", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    """Validate review state and write the final CSV."""
    args = parse_args()
    with public_id_registry_lock(args.id_registry):
        result = finalize_review_state(
            load_review_state(args.state_input),
            review_rows=read_review_workbook(args.xlsx_input),
            public_id_registry=load_public_id_registry(args.id_registry),
        )
        write_public_id_registry(args.id_registry, result["public_id_registry"])
        write_final_csv(args.output, result["records"])
    summary = {
        **result["summary"],
        "output": str(args.output),
        "id_registry": str(args.id_registry),
    }
    print_json_summary(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
