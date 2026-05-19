"""Deduplicate and rebalance accepted Route 3 streaming records."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.final_selection import select_final_records
from wikidata_simpleqa.io import write_jsonl


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--accepted-input",
        type=Path,
        required=True,
        help="Accepted JSONL file from the streaming Route 3 runner.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs" / "wikipedia_stream_final_300.jsonl",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=ROOT / "outputs" / "wikipedia_stream_final_300_summary.json",
    )
    parser.add_argument("--target-count", type=int, default=300)
    parser.add_argument("--similarity-threshold", type=float, default=0.88)
    parser.add_argument("--domain-key", type=str, default="domain")
    return parser.parse_args()


def main() -> int:
    """Run final selection and write JSONL plus a compact summary."""
    args = parse_args()
    records = _read_jsonl(args.accepted_input)
    selected, summary = select_final_records(
        records,
        target_count=args.target_count,
        similarity_threshold=args.similarity_threshold,
        domain_key=args.domain_key,
    )
    write_jsonl(args.output, selected)
    summary.update(
        {
            "accepted_input": str(args.accepted_input),
            "output": str(args.output),
            "summary_output": str(args.summary_output),
        }
    )
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


def _read_jsonl(path: Path) -> list[dict]:
    """Read records from one JSONL file."""
    records: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


if __name__ == "__main__":
    raise SystemExit(main())
