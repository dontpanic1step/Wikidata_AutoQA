from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.run_wikipedia_infobox_pipeline import _write_stream_walkthrough  # noqa: E402


def read_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: build_unpacked_route3_walkthrough.py <unpacked_dir> <run_id>", file=sys.stderr)
        return 2
    unpacked_dir = Path(sys.argv[1]).resolve()
    run_id = sys.argv[2]
    summary_path = unpacked_dir / "outputs" / f"{run_id}_summary.json"
    accepted_path = unpacked_dir / "outputs" / f"{run_id}_accepted.jsonl"
    rejected_path = unpacked_dir / "outputs" / f"{run_id}_rejected.jsonl"
    output_path = unpacked_dir / "walkthrough.md"

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["output_path"] = str(accepted_path)
    summary["rejected_output_path"] = str(rejected_path)
    summary["summary_output"] = str(summary_path)
    summary["walkthrough_output"] = str(output_path)
    manifest_path = unpacked_dir / "outputs" / "run_manifests" / f"{run_id}.json"
    if manifest_path.exists():
        summary["run_artifact_manifest"] = str(manifest_path)

    accepted_records = read_jsonl(accepted_path)
    rejected_records = read_jsonl(rejected_path)
    _write_stream_walkthrough(
        path=output_path,
        summary=summary,
        accepted_records=accepted_records,
        rejected_records=rejected_records,
        rerun_records=[],
        existing_accepted_records=[],
        existing_rejected_records=[],
    )
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
