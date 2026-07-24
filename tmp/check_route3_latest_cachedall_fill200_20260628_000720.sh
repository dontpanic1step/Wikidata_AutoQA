#!/usr/bin/env bash
set -u

cd /home/chenyue/Wikidata_Framework_aws || exit 1

run="route3_all5_latest_cachedall_fill200_gemini3flashpreview_2026_06_28_000720"

echo "--- process ---"
pgrep -af "run_wikipedia_infobox_recipe.py|run_route3_all5_latest_cachedall_fill200_20260628_000720" || true

echo "--- log tail ---"
tail -n 120 "outputs/aws_run_logs/${run}.log" 2>/dev/null || true

files=()
for file in "outputs/aws_run_logs/${run}.log" "outputs/recipe_segments/${run}"/*.jsonl "outputs/recipe_segments/${run}"/*.json; do
  if [ -f "$file" ]; then
    files+=("$file")
  fi
done

echo "--- matched files ---"
for file in "${files[@]}"; do
  lines=$(wc -l "$file" | awk '{print $1}')
  printf '%s\t%s\n' "$file" "$lines"
done

echo "--- error counts ---"
patterns=(
  "HTTP Error 401"
  "HTTP Error 403"
  "Unauthorized"
  "unauthorized"
  "Forbidden"
  "forbidden"
  "quota"
  "rate limit"
  "insufficient"
  "OpenRouter"
  "openrouter"
  "Traceback"
  "traceback"
  "Exception"
  "exception"
  "timed out"
  "timeout"
  "Permission denied"
)
for pattern in "${patterns[@]}"; do
  count=$(grep -Fih "$pattern" "${files[@]}" 2>/dev/null | wc -l)
  printf '%s\t%s\n' "$pattern" "$count"
done

echo "--- exact error samples ---"
grep -FinH -m 10 "HTTP Error" "${files[@]}" 2>/dev/null || true
grep -FinH -m 10 "Unauthorized" "${files[@]}" 2>/dev/null || true
grep -FinH -m 10 "Forbidden" "${files[@]}" 2>/dev/null || true
grep -FinH -m 10 "quota" "${files[@]}" 2>/dev/null || true
grep -FinH -m 10 "rate limit" "${files[@]}" 2>/dev/null || true

echo "--- artifacts ---"
find "outputs/recipe_segments/${run}" -maxdepth 1 -type f -printf '%TY-%Tm-%Td %TH:%TM:%TS %s %p\n' 2>/dev/null | sort || true
