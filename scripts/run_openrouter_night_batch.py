"""Run the overnight OpenRouter prediction and judging batch.

This script:
1. Samples 100 QA records while preserving answer-type proportions.
2. Runs OpenRouter predictions for the sample with 4 rounds.
3. Runs OpenRouter predictions for the full set with 1 round.
4. Judges both prediction output directories.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = (
    ROOT
    / "outputs"
    / "rebalanced_final_qas"
    / "wikipedia_stream_recipe_2000_each_answer_type_single_fact_2026_05_24_bigbatch_fresh_simpleqa_matched_seed42"
)
RUN_ID = "openrouter_eval_rebalanced_2026_05_26_seed42"
SAMPLE_QUOTAS = {
    "date": 22,
    "number": 18,
    "other": 25,
    "person": 20,
    "place": 15,
}


def main() -> None:
    args = parse_args()
    source_dir = Path(args.source_dir)
    run_root = Path(args.run_root)
    sample_dir = run_root / "sample_100_qas"
    sample_predictions_dir = run_root / "sample_100_predictions_4_rounds"
    full_predictions_dir = run_root / "full_418_predictions_1_round"
    sample_judged_dir = run_root / "sample_100_judged_4_rounds"
    full_judged_dir = run_root / "full_418_judged_1_round"
    log_path = Path(args.log_path)

    log_path.parent.mkdir(parents=True, exist_ok=True)
    run_root.mkdir(parents=True, exist_ok=True)
    log(log_path, f"run_root={run_root}")
    log(log_path, f"source_dir={source_dir}")

    sample_summary = make_sample(
        source_dir=source_dir,
        sample_dir=sample_dir,
        seed=args.seed,
        log_path=log_path,
    )
    write_manifest(
        run_root=run_root,
        source_dir=source_dir,
        sample_dir=sample_dir,
        sample_predictions_dir=sample_predictions_dir,
        full_predictions_dir=full_predictions_dir,
        sample_judged_dir=sample_judged_dir,
        full_judged_dir=full_judged_dir,
        log_path=log_path,
        sample_summary=sample_summary,
    )
    if args.prepare_only:
        log(log_path, "PREPARE_ONLY_DONE")
        return

    run_step(
        [
            sys.executable,
            "-u",
            str(ROOT / "scripts" / "run_openrouter_batch_predictions.py"),
            str(sample_dir),
            "--output-dir",
            str(sample_predictions_dir),
            "--rounds",
            "4",
            "--proxy",
            args.proxy,
        ],
        log_path=log_path,
        step_name="sample_100_predictions_4_rounds",
    )
    run_step(
        [
            sys.executable,
            "-u",
            str(ROOT / "scripts" / "run_openrouter_batch_predictions.py"),
            str(source_dir),
            "--output-dir",
            str(full_predictions_dir),
            "--rounds",
            "1",
            "--proxy",
            args.proxy,
        ],
        log_path=log_path,
        step_name="full_418_predictions_1_round",
    )
    run_step(
        [
            sys.executable,
            "-u",
            str(ROOT / "scripts" / "judge_openrouter_batch_predictions.py"),
            str(sample_predictions_dir),
            "--output-dir",
            str(sample_judged_dir),
            "--proxy",
            args.proxy,
        ],
        log_path=log_path,
        step_name="sample_100_judge",
    )
    run_step(
        [
            sys.executable,
            "-u",
            str(ROOT / "scripts" / "judge_openrouter_batch_predictions.py"),
            str(full_predictions_dir),
            "--output-dir",
            str(full_judged_dir),
            "--proxy",
            args.proxy,
        ],
        log_path=log_path,
        step_name="full_418_judge",
    )
    log(log_path, "ALL_DONE")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run overnight OpenRouter evaluation batch.")
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--run-root", type=Path, default=ROOT / "outputs" / RUN_ID)
    parser.add_argument("--log-path", type=Path, default=ROOT / "outputs" / RUN_ID / "night_batch.log")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--proxy", default="socks5://127.0.0.1:7897")
    parser.add_argument("--prepare-only", action="store_true")
    return parser.parse_args()


def make_sample(
    *,
    source_dir: Path,
    sample_dir: Path,
    seed: int,
    log_path: Path,
) -> dict[str, Any]:
    sample_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    summary: dict[str, Any] = {"seed": seed, "quotas": SAMPLE_QUOTAS, "files": {}}
    for answer_type, quota in SAMPLE_QUOTAS.items():
        source_path = source_dir / f"{answer_type}.rebalanced.jsonl"
        records = read_jsonl(source_path)
        if len(records) < quota:
            raise ValueError(f"Not enough records in {source_path}: need {quota}, got {len(records)}")
        sampled = rng.sample(records, quota)
        output_path = sample_dir / f"{answer_type}.sample_100_seed{seed}.jsonl"
        write_jsonl(output_path, sampled)
        summary["files"][answer_type] = {
            "source": str(source_path),
            "output": str(output_path),
            "available": len(records),
            "selected": len(sampled),
        }
        log(log_path, f"sampled {answer_type}: {len(sampled)} from {len(records)} -> {output_path}")
    log(log_path, f"sample_total={sum(row['selected'] for row in summary['files'].values())}")
    return summary


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return records


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_manifest(
    *,
    run_root: Path,
    source_dir: Path,
    sample_dir: Path,
    sample_predictions_dir: Path,
    full_predictions_dir: Path,
    sample_judged_dir: Path,
    full_judged_dir: Path,
    log_path: Path,
    sample_summary: dict[str, Any],
) -> None:
    manifest = {
        "created_at": now(),
        "source_dir": str(source_dir),
        "sample_dir": str(sample_dir),
        "sample_predictions_dir": str(sample_predictions_dir),
        "full_predictions_dir": str(full_predictions_dir),
        "sample_judged_dir": str(sample_judged_dir),
        "full_judged_dir": str(full_judged_dir),
        "log_path": str(log_path),
        "sample_summary": sample_summary,
    }
    (run_root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def run_step(command: list[str], *, log_path: Path, step_name: str) -> None:
    log(log_path, f"START {step_name}: {command}")
    with log_path.open("a", encoding="utf-8") as log_handle:
        log_handle.write(f"\n===== {now()} START {step_name} =====\n")
        log_handle.flush()
        completed = subprocess.run(
            command,
            cwd=ROOT,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            env=child_env(),
        )
        log_handle.write(f"\n===== {now()} END {step_name} rc={completed.returncode} =====\n")
        log_handle.flush()
    if completed.returncode != 0:
        log(log_path, f"FAILED {step_name} rc={completed.returncode}")
        raise SystemExit(completed.returncode)
    log(log_path, f"DONE {step_name}")


def log(path: Path, message: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{now()} {message}\n")
        handle.flush()
    print(message, flush=True)


def child_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    return env


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


if __name__ == "__main__":
    main()
