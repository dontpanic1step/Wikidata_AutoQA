from __future__ import annotations

from pathlib import Path

root = Path("/home/chenyue/Wikidata_Framework_aws")
run = "route3_all5_no_table_type_cached100_second_stage_2026_06_25_001533"
files = [
    root / "outputs" / "recipe_segments" / run / "01_alltypes_100_accepted.jsonl",
    root / "outputs" / "recipe_segments" / run / "01_alltypes_100_rejected.jsonl",
    root / "outputs" / "aws_run_logs" / f"{run}.log",
]
patterns = [
    "HTTP Error 403",
    "403",
    "Forbidden",
    "forbidden",
    "Unauthorized",
    "quota",
    "rate limit",
    "insufficient",
    "OpenRouter",
    "openrouter",
]

for path in files:
    if not path.exists():
        continue
    print(f"--- {path.relative_to(root)} ---")
    shown = 0
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_no, line in enumerate(handle, 1):
            lower = line.lower()
            matched = [p for p in patterns if p.lower() in lower]
            if not matched:
                continue
            for pattern in matched:
                index = lower.find(pattern.lower())
                start = max(0, index - 90)
                end = min(len(line), index + len(pattern) + 140)
                snippet = line[start:end].replace("\n", "\\n")
                print(f"line={line_no} pattern={pattern!r} snippet={snippet!r}")
                shown += 1
                if shown >= 20:
                    break
            if shown >= 20:
                break
    if shown == 0:
        print("no matches")
