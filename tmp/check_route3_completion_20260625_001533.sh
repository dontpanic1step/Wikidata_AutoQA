#!/usr/bin/env bash
set -u

cd /home/chenyue/Wikidata_Framework_aws || exit 1

run="route3_all5_no_table_type_cached100_second_stage_2026_06_25_001533"

echo "--- process ---"
pgrep -af "run_wikipedia_infobox_recipe.py|run_route3_all5_no_table_type_20260625_001533" || true

echo "--- top-level artifacts ---"
for file in \
  "outputs/${run}_summary.json" \
  "outputs/${run}_accepted.jsonl" \
  "outputs/${run}_rejected.jsonl" \
  "outputs/run_manifests/${run}.json" \
  "outputs/aws_run_logs/${run}.log" \
  "/home/chenyue/run_route3_all5_no_table_type_20260625_001533.nohup.log"; do
  if [ -e "$file" ]; then
    ls -lh "$file"
    stat -c 'mtime=%y size=%s path=%n' "$file"
  else
    echo "missing:$file"
  fi
done

echo "--- segment artifacts ---"
find "outputs/recipe_segments/${run}" -maxdepth 1 -type f -printf '%TY-%Tm-%Td %TH:%TM:%TS %s %p\n' 2>/dev/null | sort || true

echo "--- line counts ---"
for file in "outputs/${run}_accepted.jsonl" "outputs/${run}_rejected.jsonl" "outputs/recipe_segments/${run}"/*.jsonl; do
  if [ -f "$file" ]; then
    lines=$(wc -l "$file" | awk '{print $1}')
    echo "$lines $file"
  fi
done

echo "--- state tail ---"
tail -n 80 "outputs/recipe_segments/${run}/01_alltypes_100_state.json" 2>/dev/null || true

echo "--- summary tail ---"
tail -n 80 "outputs/recipe_segments/${run}/01_alltypes_100_summary.json" 2>/dev/null || true

echo "--- nohup tail ---"
tail -n 80 "/home/chenyue/run_route3_all5_no_table_type_20260625_001533.nohup.log" 2>/dev/null || true
