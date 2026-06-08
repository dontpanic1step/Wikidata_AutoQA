"""Temporary pageview/long-tail analysis for Route 3 recipe outputs.

This script intentionally lives under scripts/tmp_* and writes only to tmp/.
It samples accepted examples and rejected examples whose rejection reason is
directly related to long-tail/difficulty filtering, then fetches recent
Wikipedia pageviews for the source page.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median
from typing import Any


DEFAULT_BASE = Path(
    "outputs/recipe_segments/"
    "wikipedia_stream_recipe_2000_each_answer_type_single_fact_2026_05_24_bigbatch_fresh"
)
DEFAULT_OUT_DIR = Path("tmp/pageview_longtail_analysis")
NEGATIVE_REASONS = {
    "second_stage_grading_accuracy_threshold_exceeded",
    "search_longtail_verifier_rejected",
}
START_MONTH = "2025050100"
END_MONTH = "2026040100"
USER_AGENT = (
    "WikidataFrameworkPageviewLongtailAnalysis/0.1 "
    "(local research; contact: local)"
)


@dataclass
class SampleRecord:
    answer_type: str
    label: str
    source_file: str
    title: str
    question: str
    answer: str
    rejection_reason: str
    failing_reason: str
    panel_accuracy: float | None


def infer_answer_type(path: Path, rec: dict[str, Any]) -> str:
    if rec.get("answer_type"):
        return str(rec["answer_type"])
    parts = path.name.split("_")
    if len(parts) >= 2:
        return parts[1].title()
    return "Unknown"


def extract_title(rec: dict[str, Any]) -> str:
    subject = rec.get("subject_entity") or {}
    metadata = rec.get("source_metadata") or {}
    title = (
        subject.get("wikipedia_title")
        or subject.get("name")
        or metadata.get("page_title")
        or rec.get("page_title")
        or ""
    )
    title = str(title).strip()
    return title.replace(" ", "_")


def load_records(base: Path) -> tuple[list[SampleRecord], Counter[str]]:
    records: list[SampleRecord] = []
    rejection_counts: Counter[str] = Counter()
    for path in sorted(base.glob("*.jsonl")):
        if path.name.endswith("_accepted.jsonl"):
            status = "accepted"
        elif path.name.endswith("_rejected.jsonl"):
            status = "rejected"
        else:
            continue

        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                rec = json.loads(line)
                answer_type = infer_answer_type(path, rec)
                reason = str(rec.get("rejection_reason") or "")
                if status == "rejected":
                    rejection_counts[f"{answer_type}\t{reason}"] += 1
                    if reason not in NEGATIVE_REASONS:
                        continue
                    label = "not_long_tail"
                else:
                    label = "long_tail"

                title = extract_title(rec)
                if not title:
                    continue
                panel = rec.get("panel_grading_features") or {}
                accuracy = panel.get("accuracy")
                records.append(
                    SampleRecord(
                        answer_type=answer_type,
                        label=label,
                        source_file=path.name,
                        title=title,
                        question=str(rec.get("question") or ""),
                        answer=str(rec.get("answer") or ""),
                        rejection_reason=reason,
                        failing_reason=str(rec.get("failing_reason") or ""),
                        panel_accuracy=float(accuracy)
                        if isinstance(accuracy, (int, float))
                        else None,
                    )
                )
    return records, rejection_counts


def sample_records(
    records: list[SampleRecord], max_per_cell: int, seed: int
) -> list[SampleRecord]:
    rng = random.Random(seed)
    grouped: dict[tuple[str, str], list[SampleRecord]] = defaultdict(list)
    for rec in records:
        grouped[(rec.answer_type, rec.label)].append(rec)

    sampled: list[SampleRecord] = []
    for key in sorted(grouped):
        bucket = grouped[key]
        rng.shuffle(bucket)
        seen_titles: set[str] = set()
        chosen: list[SampleRecord] = []
        for rec in bucket:
            if rec.title in seen_titles:
                continue
            chosen.append(rec)
            seen_titles.add(rec.title)
            if len(chosen) >= max_per_cell:
                break
        if len(chosen) < max_per_cell:
            for rec in bucket:
                if rec in chosen:
                    continue
                chosen.append(rec)
                if len(chosen) >= max_per_cell:
                    break
        sampled.extend(chosen)
    return sampled


def fetch_pageviews(
    title: str,
    cache: dict[str, Any],
    sleep_seconds: float,
    retry_failed: bool = True,
    max_retries: int = 4,
) -> dict[str, Any]:
    key = f"enwiki:{title}:{START_MONTH}:{END_MONTH}:monthly"
    if key in cache and not (
        retry_failed
        and not cache[key].get("ok")
        and "429" in str(cache[key].get("error") or "")
    ):
        return cache[key]

    quoted_title = urllib.parse.quote(title, safe="")
    url = (
        "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
        f"en.wikipedia.org/all-access/user/{quoted_title}/monthly/"
        f"{START_MONTH}/{END_MONTH}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    result: dict[str, Any] = {
        "title": title,
        "url": url,
        "ok": False,
        "views_12m": None,
        "months": 0,
        "error": "",
    }
    for attempt in range(max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
            items = payload.get("items") or []
            views = sum(int(item.get("views") or 0) for item in items)
            result.update(
                {
                    "ok": True,
                    "views_12m": views,
                    "months": len(items),
                    "monthly": [
                        {
                            "timestamp": item.get("timestamp"),
                            "views": int(item.get("views") or 0),
                        }
                        for item in items
                    ],
                }
            )
            break
        except urllib.error.HTTPError as exc:
            result["error"] = f"HTTP {exc.code}: {exc.reason}"
            if exc.code != 429 or attempt >= max_retries:
                break
            time.sleep(max(2.0, sleep_seconds) * (attempt + 1))
        except Exception as exc:  # pragma: no cover - temporary diagnostics script.
            result["error"] = repr(exc)
            break

    cache[key] = result
    if sleep_seconds > 0:
        time.sleep(sleep_seconds)
    return result


def percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * pct
    low = math.floor(rank)
    high = math.ceil(rank)
    if low == high:
        return ordered[low]
    frac = rank - low
    return ordered[low] * (1 - frac) + ordered[high] * frac


def summarize_values(values: list[float]) -> dict[str, Any]:
    if not values:
        return {
            "n": 0,
            "mean": None,
            "median": None,
            "p25": None,
            "p75": None,
            "min": None,
            "max": None,
        }
    return {
        "n": len(values),
        "mean": mean(values),
        "median": median(values),
        "p25": percentile(values, 0.25),
        "p75": percentile(values, 0.75),
        "min": min(values),
        "max": max(values),
    }


def corr(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(xs) != len(ys):
        return None
    mx = mean(xs)
    my = mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mx) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - my) ** 2 for y in ys))
    if den_x == 0 or den_y == 0:
        return None
    return num / (den_x * den_y)


def auc_nonlongtail_higher(rows: list[dict[str, Any]]) -> float | None:
    positives = [r["avg_monthly"] for r in rows if r["label"] == "not_long_tail"]
    negatives = [r["avg_monthly"] for r in rows if r["label"] == "long_tail"]
    if not positives or not negatives:
        return None
    wins = 0.0
    total = 0
    for pos in positives:
        for neg in negatives:
            total += 1
            if pos > neg:
                wins += 1.0
            elif pos == neg:
                wins += 0.5
    return wins / total


def evaluate_thresholds(rows: list[dict[str, Any]]) -> dict[str, Any]:
    usable = [r for r in rows if r.get("avg_monthly") is not None]
    if not usable:
        return {}
    thresholds = sorted({float(r["avg_monthly"]) for r in usable})
    best: dict[str, Any] | None = None
    for threshold in thresholds:
        tp = fp = tn = fn = 0
        for row in usable:
            pred_long = float(row["avg_monthly"]) <= threshold
            actual_long = row["label"] == "long_tail"
            if pred_long and actual_long:
                tp += 1
            elif pred_long and not actual_long:
                fp += 1
            elif not pred_long and actual_long:
                fn += 1
            else:
                tn += 1
        recall = tp / (tp + fn) if tp + fn else 0.0
        specificity = tn / (tn + fp) if tn + fp else 0.0
        precision = tp / (tp + fp) if tp + fp else 0.0
        balanced_accuracy = (recall + specificity) / 2
        candidate = {
            "threshold_avg_monthly": threshold,
            "tp": tp,
            "fp": fp,
            "tn": tn,
            "fn": fn,
            "recall_long_tail": recall,
            "specificity_not_long_tail": specificity,
            "precision_long_tail": precision,
            "balanced_accuracy": balanced_accuracy,
        }
        if best is None:
            best = candidate
        elif (
            candidate["balanced_accuracy"],
            candidate["precision_long_tail"],
            candidate["recall_long_tail"],
        ) > (
            best["balanced_accuracy"],
            best["precision_long_tail"],
            best["recall_long_tail"],
        ):
            best = candidate
    return best or {}


def write_outputs(out_dir: Path, rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "sample_with_pageviews.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    columns = [
        "answer_type",
        "label",
        "title",
        "avg_monthly",
        "views_12m",
        "months",
        "rejection_reason",
        "panel_accuracy",
        "question",
        "answer",
        "source_file",
    ]
    with (out_dir / "sample_with_pageviews.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    with (out_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--max-per-cell", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--sleep-seconds", type=float, default=0.05)
    args = parser.parse_args()

    records, rejection_counts = load_records(args.base)
    sampled = sample_records(records, args.max_per_cell, args.seed)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    cache_path = args.out_dir / "pageviews_cache.json"
    if cache_path.exists():
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
    else:
        cache = {}

    rows: list[dict[str, Any]] = []
    for idx, rec in enumerate(sampled, 1):
        pageviews = fetch_pageviews(rec.title, cache, args.sleep_seconds)
        cache_path.write_text(
            json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        views_12m = pageviews.get("views_12m")
        months = pageviews.get("months") or 0
        avg_monthly = (views_12m / months) if views_12m is not None and months else None
        rows.append(
            {
                "answer_type": rec.answer_type,
                "label": rec.label,
                "source_file": rec.source_file,
                "title": rec.title,
                "question": rec.question,
                "answer": rec.answer,
                "rejection_reason": rec.rejection_reason,
                "failing_reason": rec.failing_reason,
                "panel_accuracy": rec.panel_accuracy,
                "views_12m": views_12m,
                "months": months,
                "avg_monthly": avg_monthly,
                "pageview_ok": pageviews.get("ok"),
                "pageview_error": pageviews.get("error"),
            }
        )
        print(
            f"[{idx}/{len(sampled)}] {rec.answer_type} {rec.label} "
            f"{rec.title}: avg_monthly={avg_monthly}"
        )

    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")

    summary: dict[str, Any] = {
        "base": str(args.base),
        "sample_size_per_answer_type_label": args.max_per_cell,
        "seed": args.seed,
        "pageview_metric": {
            "project": "en.wikipedia.org",
            "agent": "all-access",
            "user_type": "user",
            "granularity": "monthly",
            "start_month": START_MONTH,
            "end_month": END_MONTH,
            "derived_metric": "average monthly pageviews over 2025-05 through 2026-04",
        },
        "negative_rejection_reasons": sorted(NEGATIVE_REASONS),
        "rejection_reason_counts": dict(sorted(rejection_counts.items())),
        "sample_counts": {
            f"{answer_type}\t{label}": count
            for (answer_type, label), count in Counter(
                (r["answer_type"], r["label"]) for r in rows
            ).items()
        },
        "by_answer_type_label": {},
        "by_answer_type": {},
        "overall": {},
    }

    for answer_type in sorted({r["answer_type"] for r in rows}):
        type_rows = [
            r
            for r in rows
            if r["answer_type"] == answer_type and r.get("avg_monthly") is not None
        ]
        summary["by_answer_type"][answer_type] = {
            "threshold_eval": evaluate_thresholds(type_rows),
            "auc_not_longtail_has_higher_pageviews": auc_nonlongtail_higher(type_rows),
            "point_biserial_corr_longtail_vs_log10_pageviews": corr(
                [1.0 if r["label"] == "long_tail" else 0.0 for r in type_rows],
                [math.log10(float(r["avg_monthly"]) + 1.0) for r in type_rows],
            ),
        }
        for label in ("long_tail", "not_long_tail"):
            values = [
                float(r["avg_monthly"])
                for r in type_rows
                if r["label"] == label and r.get("avg_monthly") is not None
            ]
            summary["by_answer_type_label"][f"{answer_type}\t{label}"] = summarize_values(
                values
            )

    usable_rows = [r for r in rows if r.get("avg_monthly") is not None]
    summary["overall"] = {
        "threshold_eval": evaluate_thresholds(usable_rows),
        "auc_not_longtail_has_higher_pageviews": auc_nonlongtail_higher(usable_rows),
        "point_biserial_corr_longtail_vs_log10_pageviews": corr(
            [1.0 if r["label"] == "long_tail" else 0.0 for r in usable_rows],
            [math.log10(float(r["avg_monthly"]) + 1.0) for r in usable_rows],
        ),
    }

    write_outputs(args.out_dir, rows, summary)
    print(f"Wrote {args.out_dir / 'sample_with_pageviews.jsonl'}")
    print(f"Wrote {args.out_dir / 'sample_with_pageviews.csv'}")
    print(f"Wrote {args.out_dir / 'summary.json'}")


if __name__ == "__main__":
    main()
