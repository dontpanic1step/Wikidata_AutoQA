#!/usr/bin/env bash
set -euo pipefail

cd /home/chenyue/Wikidata_Framework_aws

run="route3_all5_no_table_type_cached100_second_stage_2026_06_25_001533"
pattern='openrouter|403|forbidden|unauthorized|quota|rate limit|insufficient|HTTP Error|error'

echo "--- files ---"
ls -lh \
  "outputs/${run}_accepted.jsonl" \
  "outputs/${run}_rejected.jsonl" \
  "outputs/recipe_segments/${run}"/* 2>/dev/null || true

echo "--- openrouter/403 grep in top-level jsonl ---"
grep -Ein "$pattern" \
  "outputs/${run}_accepted.jsonl" \
  "outputs/${run}_rejected.jsonl" 2>/dev/null | tail -n 120 || true

echo "--- openrouter/403 grep in segment files ---"
grep -RInE "$pattern" "outputs/recipe_segments/${run}" 2>/dev/null | tail -n 160 || true

echo "--- counts ---"
for file in "outputs/${run}_accepted.jsonl" "outputs/${run}_rejected.jsonl" "outputs/recipe_segments/${run}"/*.jsonl; do
  if [ -f "$file" ]; then
    printf '%s ' "$file"
    wc -l < "$file"
  fi
done

echo "--- process ---"
pgrep -af "run_wikipedia_infobox_recipe.py|run_route3_all5_no_table_type_20260625_001533" || true
