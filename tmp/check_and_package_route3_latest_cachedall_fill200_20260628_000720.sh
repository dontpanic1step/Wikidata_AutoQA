#!/usr/bin/env bash
set -euo pipefail

cd /home/chenyue/Wikidata_Framework_aws

run="route3_all5_latest_cachedall_fill200_gemini3flashpreview_2026_06_28_000720"
archive="/home/chenyue/${run}_artifacts.tgz"

echo "--- process ---"
pgrep -af "run_wikipedia_infobox_recipe.py|run_route3_all5_latest_cachedall_fill200_20260628_000720" || true

echo "--- required artifacts ---"
missing=0
for file in \
  "outputs/${run}_summary.json" \
  "outputs/${run}_accepted.jsonl" \
  "outputs/${run}_rejected.jsonl" \
  "outputs/run_manifests/${run}.json" \
  "outputs/aws_run_logs/${run}.log" \
  "docs/walkthroughs/${run}.md" \
  "outputs/recipe_segments/${run}/01_alltypes_200_summary.json"; do
  if [ -e "$file" ]; then
    ls -lh "$file"
  else
    echo "missing:$file"
    missing=1
  fi
done

if pgrep -f "run_wikipedia_infobox_recipe.py|run_route3_all5_latest_cachedall_fill200_20260628_000720" >/dev/null; then
  echo "NOT_DONE: process still running"
  exit 2
fi

if [ "$missing" -ne 0 ]; then
  echo "NOT_DONE: required artifacts missing"
  exit 3
fi

tar -czf "$archive" \
  "outputs/${run}_summary.json" \
  "outputs/${run}_accepted.jsonl" \
  "outputs/${run}_rejected.jsonl" \
  "outputs/run_manifests/${run}.json" \
  "outputs/aws_run_logs/${run}.log" \
  "outputs/recipe_segments/${run}" \
  "docs/walkthroughs/${run}.md"

echo "--- archive ---"
ls -lh "$archive"
