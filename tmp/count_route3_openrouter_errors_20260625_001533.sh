#!/usr/bin/env bash
set -euo pipefail

cd /home/chenyue/Wikidata_Framework_aws

run="route3_all5_no_table_type_cached100_second_stage_2026_06_25_001533"
files=()
for file in \
  "outputs/${run}_accepted.jsonl" \
  "outputs/${run}_rejected.jsonl" \
  "outputs/recipe_segments/${run}"/*.jsonl \
  "outputs/aws_run_logs/${run}.log"; do
  if [ -f "$file" ]; then
    files+=("$file")
  fi
done

echo "--- matched files ---"
for file in "${files[@]}"; do
  printf '%s ' "$file"
  wc -l < "$file"
done

echo "--- exact-ish error counts ---"
for pattern in \
  'HTTP Error 403' \
  '403' \
  'Forbidden' \
  'forbidden' \
  'Unauthorized' \
  'unauthorized' \
  'User not found' \
  'quota' \
  'rate limit' \
  'insufficient' \
  'OpenRouter' \
  'openrouter'; do
  count=0
  if [ "${#files[@]}" -gt 0 ]; then
    count=$(grep -Fih "$pattern" "${files[@]}" 2>/dev/null | wc -l)
  fi
  printf '%s\t%s\n' "$pattern" "$count"
done

echo "--- first 403/forbidden context, if any ---"
grep -FinH -m 5 '403' "${files[@]}" 2>/dev/null || true
grep -FinH -m 5 'Forbidden' "${files[@]}" 2>/dev/null || true
grep -FinH -m 5 'forbidden' "${files[@]}" 2>/dev/null || true

echo "--- process ---"
pgrep -af "run_wikipedia_infobox_recipe.py|run_route3_all5_no_table_type_20260625_001533" || true
