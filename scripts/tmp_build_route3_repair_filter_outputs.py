"""Build temporary Route 3 repair-filter outputs.

The repair order is:

1. Recreate redirected passed_all files from reviewed answer-type moves.
2. Apply the manual whitelist/correction plan for inspected full-418 cases.
3. Run the temporary Route 3 passed_all filter over the remaining records.

The script writes only new repair artifacts under outputs/ and does not modify
the original passed_all, rebalanced, or final-result files.
"""

from __future__ import annotations

import argparse
import copy
import csv
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scripts.tmp_apply_route3_answer_type_redirects import apply_manual_answer_type_redirects
from scripts.tmp_filter_route3_passed_all import route3_tmp_filter_rejection_reasons
from wikidata_simpleqa.route3_ids import assign_unique_route3_record_ids

ANSWER_TYPES = ("Date", "Number", "Other", "Person", "Place")
ANSWER_TYPE_KEYS = tuple(answer_type.lower() for answer_type in ANSWER_TYPES)
MODEL_ORDER = (
    "google__gemini-3.1-pro-preview",
    "openai__gpt-5.5",
    "deepseek__deepseek-v4-pro",
    "moonshotai__kimi-k2.6",
    "z-ai__glm-5.1",
    "qwen__qwen3.5-397b-a17b",
    "anthropic__claude-sonnet-4.6",
    "xiaomi__mimo-v2.5-pro",
    "minimax__minimax-m2.7",
)
MODEL_DISPLAY = {
    "anthropic__claude-sonnet-4.6": "Claude Sonnet 4.6",
    "deepseek__deepseek-v4-pro": "DeepSeek V4 Pro",
    "google__gemini-3.1-pro-preview": "Gemini 3.1 Pro Preview",
    "minimax__minimax-m2.7": "MiniMax M2.7",
    "moonshotai__kimi-k2.6": "Kimi K2.6",
    "openai__gpt-5.5": "GPT-5.5",
    "qwen__qwen3.5-397b-a17b": "Qwen3.5 397B-A17B",
    "xiaomi__mimo-v2.5-pro": "MiMo V2.5 Pro",
    "z-ai__glm-5.1": "GLM-5.1",
}

DEFAULT_SPLIT_DIR = ROOT / (
    "outputs/final_llm_qa_filter/"
    "wikipedia_stream_recipe_2000_each_answer_type_single_fact_2026_05_24_bigbatch_fresh_after_rule_gate_all_answer_types_split"
)
DEFAULT_REBALANCED_DIR = ROOT / (
    "outputs/rebalanced_final_qas/"
    "wikipedia_stream_recipe_2000_each_answer_type_single_fact_2026_05_24_bigbatch_fresh_simpleqa_matched_seed42"
)
DEFAULT_FULL_JUDGED_DIR = ROOT / "outputs/final_result/full_418_openrouter_2026_05_26/full_418_judged_1_round"
DEFAULT_SAMPLE_JUDGED_DIR = ROOT / "outputs/final_result/sample_100_openrouter_2026_05_26/sample_100_judged_4_rounds"


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split-dir", type=Path, default=DEFAULT_SPLIT_DIR)
    parser.add_argument("--redirected-passed-all-dir", type=Path, default=ROOT / "outputs/route3_tmp_redirected_passed_all")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs/route3_tmp_filter_repair_2026_06_01_v5")
    parser.add_argument("--corrections", type=Path, default=ROOT / "docs/inspect/route3_corrected_questions.jsonl")
    parser.add_argument(
        "--case-md",
        type=Path,
        default=ROOT / "docs/inspect/full_418_openrouter_incorrect_distribution_and_cases.md",
    )
    parser.add_argument("--rebalanced-dir", type=Path, default=DEFAULT_REBALANCED_DIR)
    parser.add_argument("--full-judged-dir", type=Path, default=DEFAULT_FULL_JUDGED_DIR)
    parser.add_argument("--sample-judged-dir", type=Path, default=DEFAULT_SAMPLE_JUDGED_DIR)
    parser.add_argument("--skip-redirect-refresh", action="store_true")
    return parser.parse_args()


def main() -> int:
    """Build the temporary repair outputs."""
    args = parse_args()
    output_dir = args.output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite existing output directory: {output_dir}")
    output_dir.mkdir(parents=True)

    redirect_summary: dict[str, Any] | None = None
    if not args.skip_redirect_refresh:
        redirect_summary = apply_manual_answer_type_redirects(
            split_dir=args.split_dir,
            output_dir=args.redirected_passed_all_dir,
        )
        (args.redirected_passed_all_dir / "summary.json").write_text(
            json.dumps(redirect_summary, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    summary = build_repair_outputs(
        output_dir=output_dir,
        redirected_passed_all_dir=args.redirected_passed_all_dir,
        corrections_path=args.corrections,
        case_md_path=args.case_md,
        rebalanced_dir=args.rebalanced_dir,
        full_judged_dir=args.full_judged_dir,
        sample_judged_dir=args.sample_judged_dir,
        redirect_summary=redirect_summary,
    )
    print(json.dumps({"output_dir": _rel(output_dir), "counts": summary["counts"]}, indent=2, ensure_ascii=False))
    return 0


def build_repair_outputs(
    *,
    output_dir: Path,
    redirected_passed_all_dir: Path,
    corrections_path: Path,
    case_md_path: Path,
    rebalanced_dir: Path,
    full_judged_dir: Path,
    sample_judged_dir: Path,
    redirect_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build whitelist, tmp_filter, distribution, metrics, and report outputs."""
    correction_plans = {row["rebalanced_id"]: row for row in _read_jsonl(corrections_path)}
    case_ids = _extract_case_ids(case_md_path)
    rebalanced_by_id, source_key_to_rebalanced = _load_rebalanced_records(rebalanced_dir)
    full_grades, sample_grades, full_ids, sample_ids = _load_final_result_grades(full_judged_dir, sample_judged_dir)

    def run_count(rebalanced_id: str | None) -> int:
        if rebalanced_id in sample_ids:
            return 5
        if rebalanced_id in full_ids:
            return 1
        return 0

    whitelist_passed: list[dict[str, Any]] = []
    whitelist_rejected: list[dict[str, Any]] = []
    whitelist_keys: set[tuple[str, int | None, str | None]] = set()
    for rebalanced_id in case_ids:
        base = rebalanced_by_id.get(rebalanced_id)
        plan = correction_plans.get(rebalanced_id)
        if not base:
            whitelist_rejected.append(
                {
                    "id": rebalanced_id,
                    "tmp_repair_source": "full_418_incorrect_cases_whitelist",
                    "tmp_repair_status": "rejected",
                    "rejection_reason": "manual_whitelist_missing_rebalanced_record",
                    "rejection_rule": "manual_whitelist_missing_rebalanced_record",
                }
            )
            continue
        selection = base.get("rebalanced_selection") or {}
        whitelist_keys.add(_source_key(selection.get("source_file"), selection.get("source_line_index"), selection.get("original_id")))
        if plan and plan.get("action") == "delete":
            whitelist_rejected.append(
                _mark(
                    base,
                    tmp_repair_source="full_418_incorrect_cases_whitelist",
                    tmp_repair_status="rejected",
                    tmp_repair_rebalanced_id=rebalanced_id,
                    tmp_repair_final_result_run_count=run_count(rebalanced_id),
                    rejection_reason="manual_correction_plan_delete",
                    rejection_rule=plan.get("reason") or "manual_correction_plan_delete",
                    tmp_repair_manual_correction=_plan_stub(plan),
                )
            )
        elif plan and plan.get("action") == "update":
            updated = _apply_planned_changes(base, plan)
            updated.update(
                tmp_repair_source="full_418_incorrect_cases_whitelist",
                tmp_repair_status="accepted_corrected_update",
                tmp_repair_rebalanced_id=rebalanced_id,
                tmp_repair_final_result_run_count=run_count(rebalanced_id),
            )
            whitelist_passed.append(updated)
        else:
            whitelist_passed.append(
                _mark(
                    base,
                    tmp_repair_source="full_418_incorrect_cases_whitelist",
                    tmp_repair_status="accepted_default_pass",
                    tmp_repair_rebalanced_id=rebalanced_id,
                    tmp_repair_final_result_run_count=run_count(rebalanced_id),
                )
            )

    tmp_passed: list[dict[str, Any]] = []
    tmp_rejected: list[dict[str, Any]] = []
    for path in sorted(redirected_passed_all_dir.glob("*.passed_all_appended.jsonl")):
        source = _rel(path)
        for line_index, record in enumerate(_iter_jsonl(path), start=1):
            key = _source_key(source, line_index, record.get("id"))
            rebalanced_id = source_key_to_rebalanced.get(key)
            final_run_count = run_count(rebalanced_id)
            if key in whitelist_keys:
                continue
            plan = correction_plans.get(rebalanced_id) if rebalanced_id else None
            reasons = route3_tmp_filter_rejection_reasons(record)
            if plan and plan.get("action") == "delete":
                tmp_rejected.append(
                    _mark(
                        record,
                        tmp_repair_source="passed_all_remainder_tmp_filter",
                        tmp_repair_status="rejected_manual_correction_delete",
                        tmp_repair_source_file=source,
                        tmp_repair_source_line=line_index,
                        tmp_repair_rebalanced_id=rebalanced_id,
                        tmp_repair_final_result_run_count=final_run_count,
                        rejection_reason="manual_correction_plan_delete",
                        rejection_rule=plan.get("reason") or "manual_correction_plan_delete",
                        tmp_repair_manual_correction=_plan_stub(plan),
                    )
                )
                continue
            if reasons:
                tmp_rejected.append(
                    _mark(
                        record,
                        tmp_repair_source="passed_all_remainder_tmp_filter",
                        tmp_repair_status="rejected_tmp_filter",
                        tmp_repair_source_file=source,
                        tmp_repair_source_line=line_index,
                        tmp_repair_rebalanced_id=rebalanced_id,
                        tmp_repair_final_result_run_count=final_run_count,
                        rejection_reason="tmp_route3_passed_all_filter_rejected",
                        rejection_rule=reasons[0],
                        tmp_filter_rejection_reasons=reasons,
                    )
                )
                continue
            accepted = _apply_planned_changes(record, plan) if plan and plan.get("action") == "update" else copy.deepcopy(record)
            accepted.update(
                tmp_repair_source="passed_all_remainder_tmp_filter",
                tmp_repair_status="accepted_corrected_update" if plan and plan.get("action") == "update" else "accepted_tmp_filter_pass",
                tmp_repair_source_file=source,
                tmp_repair_source_line=line_index,
                tmp_repair_rebalanced_id=rebalanced_id,
                tmp_repair_final_result_run_count=final_run_count,
            )
            tmp_passed.append(accepted)

    accepted = whitelist_passed + tmp_passed
    assign_unique_route3_record_ids(accepted)
    rejected = whitelist_rejected + tmp_rejected
    distribution = _answer_type_run_distribution(accepted)
    accepted_final_ids = {row.get("tmp_repair_rebalanced_id") for row in accepted if row.get("tmp_repair_rebalanced_id") in full_ids}
    accepted_five_run_ids = {row.get("tmp_repair_rebalanced_id") for row in accepted if row.get("tmp_repair_rebalanced_id") in sample_ids}
    first_run_metrics = _first_run_metrics(full_grades, accepted_final_ids)
    five_run_metrics = _five_run_metrics(full_grades, sample_grades, accepted_five_run_ids)

    _write_jsonl(output_dir / "whitelist.full_418_incorrect_cases.accepted.jsonl", whitelist_passed)
    _write_jsonl(output_dir / "whitelist.full_418_incorrect_cases.rejected.jsonl", whitelist_rejected)
    _write_jsonl(output_dir / "tmp_filter.passed_all_remainder.accepted.jsonl", tmp_passed)
    _write_jsonl(output_dir / "tmp_filter.passed_all_remainder.rejected.jsonl", tmp_rejected)
    _write_jsonl(output_dir / "accepted.whitelist_plus_tmp_filter.jsonl", accepted)
    _write_jsonl(output_dir / "rejected.whitelist_plus_tmp_filter.jsonl", rejected)
    _write_distribution_csv(output_dir / "answer_type_run_count_distribution.csv", distribution)
    _write_first_metrics_csv(output_dir / "metrics_first_run_full418_accepted.csv", first_run_metrics)
    _write_five_metrics_csv(output_dir / "metrics_five_run_sample100_accepted.csv", five_run_metrics)
    _write_tmp_filter_rejection_report(output_dir / "tmp_filter_rejection_report.md", tmp_rejected)

    summary = {
        "output_dir": _rel(output_dir),
        "redirect_summary": redirect_summary,
        "source_paths": {
            "redirected_passed_all_dir": _rel(redirected_passed_all_dir),
            "corrections": _rel(corrections_path),
            "incorrect_cases_md": _rel(case_md_path),
            "rebalanced_dir": _rel(rebalanced_dir),
            "full_judged_dir": _rel(full_judged_dir),
            "sample_judged_dir": _rel(sample_judged_dir),
        },
        "counts": {
            "incorrect_case_ids": len(case_ids),
            "correction_plan_records": len(correction_plans),
            "whitelist_accepted": len(whitelist_passed),
            "whitelist_rejected": len(whitelist_rejected),
            "tmp_filter_accepted": len(tmp_passed),
            "tmp_filter_rejected": len(tmp_rejected),
            "accepted_total": len(accepted),
            "rejected_total": len(rejected),
            "accepted_final_result_ids": len(accepted_final_ids),
            "accepted_five_run_ids": len(accepted_five_run_ids),
        },
        "distribution": distribution,
        "metrics_first_run_full418_accepted": first_run_metrics,
        "metrics_five_run_sample100_accepted": five_run_metrics,
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def _load_rebalanced_records(rebalanced_dir: Path) -> tuple[dict[str, dict[str, Any]], dict[tuple[str, int | None, str | None], str]]:
    by_id: dict[str, dict[str, Any]] = {}
    source_keys: dict[tuple[str, int | None, str | None], str] = {}
    for path in sorted(rebalanced_dir.glob("*.rebalanced.jsonl")):
        for record in _iter_jsonl(path):
            rebalanced_id = record.get("id")
            by_id[rebalanced_id] = record
            selection = record.get("rebalanced_selection") or {}
            key = _source_key(selection.get("source_file"), selection.get("source_line_index"), selection.get("original_id"))
            if key[0] and key[1] is not None and key[2]:
                source_keys[key] = rebalanced_id
    return by_id, source_keys


def _load_final_result_grades(
    full_judged_dir: Path,
    sample_judged_dir: Path,
) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, list[str]]], set[str], set[str]]:
    full_grades: dict[str, dict[str, str]] = defaultdict(dict)
    sample_grades: dict[str, dict[str, list[str]]] = defaultdict(dict)
    full_ids: set[str] = set()
    sample_ids: set[str] = set()
    for path in sorted(full_judged_dir.glob("*.judged.jsonl")):
        model_slug = _model_slug(path.name)
        for record_id, grades in _load_judged_file(path).items():
            if grades:
                full_grades[model_slug][record_id] = grades[0]
                full_ids.add(record_id)
    for path in sorted(sample_judged_dir.glob("*.judged.jsonl")):
        model_slug = _model_slug(path.name)
        for record_id, grades in _load_judged_file(path).items():
            if len(grades) >= 4:
                sample_grades[model_slug][record_id] = grades[:4]
                sample_ids.add(record_id)
    return full_grades, sample_grades, full_ids, sample_ids


def _extract_case_ids(case_md_path: Path) -> list[str]:
    text = case_md_path.read_text(encoding="utf-8")
    ids: list[str] = []
    seen: set[str] = set()
    for match in re.finditer(r"\b(?:date|number|other|person|place)_\d+\b", text):
        record_id = match.group(0)
        if record_id not in seen:
            ids.append(record_id)
            seen.add(record_id)
    return ids


def _apply_planned_changes(record: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    updated = copy.deepcopy(record)
    changes = plan.get("planned_changes") or {}
    for key, value in changes.items():
        updated[key] = value
    panel = updated.get("panel_grading_features")
    if isinstance(panel, dict):
        if "question" in changes:
            panel["question"] = changes["question"]
        if "answer" in changes:
            panel["gold_answer"] = changes["answer"]
            panel["reference_answer_for_grading"] = changes["answer"]
        if "answer_aliases" in changes:
            panel["gold_aliases"] = changes["answer_aliases"]
    gate = updated.get("rule_based_qa_gate")
    if isinstance(gate, dict) and "answer_type" in changes:
        gate["answer_type"] = changes["answer_type"]
    updated["tmp_repair_manual_correction"] = _plan_stub(plan)
    return updated


def _plan_stub(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "rebalanced_id": plan.get("rebalanced_id"),
        "original_id": plan.get("original_id"),
        "action": plan.get("action"),
        "reason": plan.get("reason"),
        "planned_changes": plan.get("planned_changes") or {},
    }


def _answer_type_run_distribution(records: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    counts: dict[str, Counter[int]] = defaultdict(Counter)
    for record in records:
        answer_type = _norm_answer_type(record.get("answer_type"))
        counts[answer_type][int(record.get("tmp_repair_final_result_run_count") or 0)] += 1
    return {
        answer_type: {
            "run_count_0": counts[answer_type][0],
            "run_count_1": counts[answer_type][1],
            "run_count_5": counts[answer_type][5],
            "total": sum(counts[answer_type].values()),
        }
        for answer_type in _sorted_answer_types(counts)
    }


def _first_run_metrics(full_grades: dict[str, dict[str, str]], accepted_ids: set[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for model_slug in MODEL_ORDER:
        grades = [full_grades[model_slug][record_id] for record_id in sorted(accepted_ids) if record_id in full_grades[model_slug]]
        rows.append({"model_slug": model_slug, "model": MODEL_DISPLAY.get(model_slug, model_slug), **_metrics_from_grades(grades)})
    return rows


def _five_run_metrics(
    full_grades: dict[str, dict[str, str]],
    sample_grades: dict[str, dict[str, list[str]]],
    accepted_ids: set[str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for model_slug in MODEL_ORDER:
        per_round = []
        for round_index in range(5):
            grades = []
            for record_id in sorted(accepted_ids):
                if round_index == 0:
                    grade = full_grades[model_slug].get(record_id)
                else:
                    sample_row = sample_grades[model_slug].get(record_id) or []
                    grade = sample_row[round_index - 1] if len(sample_row) >= round_index else None
                if grade:
                    grades.append(grade)
            per_round.append(_metrics_from_grades(grades))
        row: dict[str, Any] = {
            "model_slug": model_slug,
            "model": MODEL_DISPLAY.get(model_slug, model_slug),
            "n": per_round[0]["n"] if per_round else 0,
        }
        for key in ("f1", "accuracy", "accuracy_attempted", "attempted", "hedged"):
            values = [metrics[key] for metrics in per_round]
            row[f"{key}_mean"] = statistics.mean(values)
            row[f"{key}_variance"] = statistics.pvariance(values)
            row[f"{key}_stddev"] = statistics.pstdev(values)
        rows.append(row)
    return rows


def _metrics_from_grades(grades: list[str]) -> dict[str, Any]:
    grades = [grade for grade in grades if grade]
    total = len(grades)
    correct = sum(grade == "CORRECT" for grade in grades)
    incorrect = sum(grade == "INCORRECT" for grade in grades)
    not_attempted = sum(grade == "NOT_ATTEMPTED" for grade in grades)
    attempted = correct + incorrect
    accuracy = correct / total if total else 0.0
    accuracy_attempted = correct / attempted if attempted else 0.0
    f1 = 2 * accuracy * accuracy_attempted / (accuracy + accuracy_attempted) if accuracy + accuracy_attempted else 0.0
    return {
        "n": total,
        "f1": f1 * 100,
        "accuracy": accuracy * 100,
        "accuracy_attempted": accuracy_attempted * 100,
        "attempted": attempted / total * 100 if total else 0.0,
        "hedged": not_attempted / total * 100 if total else 0.0,
        "correct": correct,
        "incorrect": incorrect,
        "not_attempted": not_attempted,
    }


def _write_tmp_filter_rejection_report(path: Path, rows: list[dict[str, Any]]) -> None:
    reason_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        for reason in row.get("tmp_filter_rejection_reasons") or [row.get("rejection_rule") or "unknown"]:
            reason_rows[reason].append(row)
    overall = Counter(_norm_answer_type(row.get("answer_type")) for row in rows)
    by_reason = {reason: Counter(_norm_answer_type(row.get("answer_type")) for row in items) for reason, items in sorted(reason_rows.items())}
    lines = [
        "# Route 3 tmp_filter rejection report",
        "",
        f"Input: `{_rel(path.with_name('tmp_filter.passed_all_remainder.rejected.jsonl'))}`",
        f"Total records rejected by tmp_filter: **{len(rows)}**",
        "",
        "## Reason counts",
        "",
        "| Reason | Count |",
        "|---|---:|",
    ]
    for reason, items in sorted(reason_rows.items()):
        lines.append(f"| `{_esc(reason)}` | {len(items)} |")
    lines.extend(["", "## Overall answer type distribution", "", "| Answer type | Count |", "|---|---:|"])
    for answer_type in _sorted_answer_types(overall):
        lines.append(f"| {_esc(answer_type)} | {overall[answer_type]} |")
    lines.extend(
        [
            "",
            "## Answer type distribution by reason",
            "",
            "| Reason | Date | Number | Other | Person | Place | Unknown | Total |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for reason, counts in by_reason.items():
        unknown = sum(value for key, value in counts.items() if key not in ANSWER_TYPES)
        total = sum(counts.values())
        lines.append(
            f"| `{_esc(reason)}` | {counts['Date']} | {counts['Number']} | {counts['Other']} | "
            f"{counts['Person']} | {counts['Place']} | {unknown} | {total} |"
        )
    lines.extend(["", "## Examples by reason"])
    for reason, items in reason_rows.items():
        lines.extend(
            [
                "",
                f"### `{reason}`",
                "",
                "| ID | Rebalanced ID | Runs | Answer type | Q | A | URL | Accuracy |",
                "|---|---|---:|---|---|---|---|---:|",
            ]
        )
        for row in items[:5]:
            url = (row.get("subject_entity") or {}).get("url") or ""
            url_cell = f"[{_esc(url)}]({url})" if url else ""
            lines.append(
                "| "
                + " | ".join(
                    [
                        _esc(row.get("id")),
                        _esc(row.get("tmp_repair_rebalanced_id")),
                        str(row.get("tmp_repair_final_result_run_count", 0)),
                        _esc(_norm_answer_type(row.get("answer_type"))),
                        _esc(row.get("question")),
                        _esc(row.get("answer")),
                        url_cell,
                        _accuracy_cell(row),
                    ]
                )
                + " |"
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_distribution_csv(path: Path, distribution: dict[str, dict[str, int]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["answer_type", "run_count_0", "run_count_1", "run_count_5", "total"])
        writer.writeheader()
        for answer_type, row in distribution.items():
            writer.writerow({"answer_type": answer_type, **row})


def _write_first_metrics_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = ["model", "n", "f1", "accuracy", "accuracy_attempted", "attempted", "hedged"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row[key] for key in fields})


def _write_five_metrics_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = ["model", "n"]
    for key in ("f1", "accuracy", "accuracy_attempted", "attempted", "hedged"):
        fields.extend([f"{key}_mean", f"{key}_variance", f"{key}_stddev"])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row[key] for key in fields})


def _model_slug(filename: str) -> str:
    if ".sample_100_seed42." in filename:
        return filename.split(".sample_100_seed42.", 1)[1].removesuffix(".judged.jsonl")
    return filename.split(".rebalanced.", 1)[1].removesuffix(".judged.jsonl")


def _load_judged_file(path: Path) -> dict[str, list[str]]:
    records: dict[str, list[str]] = {}
    for record in _iter_jsonl(path):
        grades = []
        for prediction in record.get("predictions") or []:
            grade = (prediction.get("judge") or {}).get("grade")
            if grade:
                grades.append(str(grade).upper())
        records[record.get("id")] = grades
    return records


def _source_key(source_file: object, source_line_index: object, record_id: object) -> tuple[str, int | None, str | None]:
    return (_norm_source(source_file), _safe_int(source_line_index), str(record_id) if record_id else None)


def _norm_source(value: object) -> str:
    normalized = str(value or "").replace("\\", "/").lower()
    return normalized.rsplit("/", 1)[-1]


def _norm_answer_type(value: object) -> str:
    text = str(value or "").strip()
    for answer_type in ANSWER_TYPES:
        if text.lower() == answer_type.lower():
            return answer_type
    return text or "Unknown"


def _sorted_answer_types(counts: dict[str, Any] | Counter[str]) -> list[str]:
    return sorted(counts, key=lambda key: (ANSWER_TYPES.index(key) if key in ANSWER_TYPES else 99, key))


def _safe_int(value: object) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _mark(record: dict[str, Any], **fields: Any) -> dict[str, Any]:
    marked = copy.deepcopy(record)
    marked.update(fields)
    return marked


def _accuracy_cell(row: dict[str, Any]) -> str:
    value = (row.get("panel_grading_features") or {}).get("accuracy")
    try:
        return f"{float(value):.3f}" if value is not None else ""
    except (TypeError, ValueError):
        return str(value)


def _esc(value: object) -> str:
    return ("" if value is None else str(value)).replace("|", "\\|").replace("\n", "<br>")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return list(_iter_jsonl(path))


def _iter_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
