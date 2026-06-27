#!/usr/bin/env bash
set -u

cd /home/chenyue/Wikidata_Framework_aws || exit 1

run="route3_all5_no_table_type_cached100_second_stage_2026_06_25_001533"
files=()
for file in "outputs/recipe_segments/${run}"/*.jsonl "outputs/aws_run_logs/${run}.log"; do
  if [ -f "$file" ]; then
    files+=("$file")
  fi
done

echo "--- counts ---"
for file in "${files[@]}"; do
  line_count=$(wc -l "$file" | awk '{print $1}')
  printf '%s\t%s\n' "$file" "$line_count"
done

echo "--- patterns ---"
patterns=(
  "HTTP Error 403"
  "403"
  "Forbidden"
  "forbidden"
  "Unauthorized"
  "unauthorized"
  "User not found"
  "quota"
  "rate limit"
  "insufficient"
  "OpenRouter"
  "openrouter"
)

for pattern in "${patterns[@]}"; do
  count=$(grep -Fih "$pattern" "${files[@]}" 2>/dev/null | wc -l)
  printf '%s\t%s\n' "$pattern" "$count"
done

echo "--- 403 samples ---"
grep -FinH -m 5 "403" "${files[@]}" 2>/dev/null

echo "--- process ---"
pgrep -af "run_wikipedia_infobox_recipe.py|run_route3_all5_no_table_type_20260625_001533"
