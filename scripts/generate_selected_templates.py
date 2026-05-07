"""Generate examples for selected template domain keys."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.config import Settings
from wikidata_simpleqa.domain_templates import get_template_by_domain
from wikidata_simpleqa.pipeline import run_pipeline_for_templates


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-time", type=str, required=True)
    parser.add_argument("--domains", nargs="+", required=True)
    parser.add_argument("--pilot-total", type=int, default=10)
    parser.add_argument("--harvest-limit", type=int, default=10)
    parser.add_argument("--proxy", type=str, default="socks5://127.0.0.1:7897")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs" / "selected_templates_accepted.jsonl",
    )
    parser.add_argument(
        "--rejected-output",
        type=Path,
        default=ROOT / "outputs" / "selected_templates_rejected.jsonl",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    templates = []
    for domain in args.domains:
        template = get_template_by_domain(domain)
        if template is None:
            raise ValueError(f"Unknown template domain: {domain}")
        templates.append(template)
    settings = Settings(
        target_time=args.target_time,
        pilot_total=args.pilot_total,
        harvest_limit_per_template=args.harvest_limit,
        proxy=args.proxy,
        output_path=args.output,
        rejected_output_path=args.rejected_output,
    )
    result = run_pipeline_for_templates(settings=settings, templates=templates)
    print(
        json.dumps(
            {
                "accepted": len(result.accepted),
                "rejected": len(result.rejected),
                "domains": args.domains,
                "output_path": str(args.output),
                "rejected_output_path": str(args.rejected_output),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
