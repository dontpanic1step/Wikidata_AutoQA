#!/usr/bin/env bash
set -u

cd /home/chenyue/Wikidata_Framework_aws || exit 1

run="route3_place50_fresh50_no_reuse_gemini3flashpreview_2026_07_14_193621"
script_key="run_route3_place50_fresh50_no_reuse_20260714_193621"
archive="/home/chenyue/${run}_artifacts.tgz"

echo "--- process ---"
pgrep -af "run_wikipedia_infobox_recipe.py|${script_key}" || true

echo "--- top-level artifacts ---"
for file in \
  "outputs/${run}_summary.json" \
  "outputs/${run}_accepted.jsonl" \
  "outputs/${run}_rejected.jsonl" \
  "outputs/run_manifests/${run}.json" \
  "outputs/aws_run_logs/${run}.log" \
  "docs/walkthroughs/${run}.md"; do
  if [ -e "$file" ]; then
    ls -lh "$file"
  else
    echo "missing:$file"
  fi
done

echo "--- segment artifacts ---"
find "outputs/recipe_segments/${run}" -maxdepth 1 -type f -printf '%TY-%Tm-%Td %TH:%TM:%TS %s %p\n' 2>/dev/null | sort || true

files=()
for file in "outputs/aws_run_logs/${run}.log" "outputs/recipe_segments/${run}"/*.jsonl "outputs/recipe_segments/${run}"/*.json; do
  if [ -f "$file" ]; then
    files+=("$file")
  fi
done

echo "--- line counts ---"
for file in "outputs/${run}_accepted.jsonl" "outputs/${run}_rejected.jsonl" "outputs/recipe_segments/${run}"/*.jsonl; do
  if [ -f "$file" ]; then
    lines=$(wc -l "$file" | awk '{print $1}')
    printf '%s\t%s\n' "$file" "$lines"
  fi
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

echo "--- log tail ---"
tail -n 80 "outputs/aws_run_logs/${run}.log" 2>/dev/null || true

if pgrep -f "run_wikipedia_infobox_recipe.py|${script_key}" >/dev/null; then
  echo "STATUS:RUNNING"
  exit 0
fi

if [ ! -f "outputs/${run}_summary.json" ] || [ ! -f "outputs/${run}_accepted.jsonl" ] || [ ! -f "outputs/${run}_rejected.jsonl" ]; then
  echo "STATUS:STOPPED_WITHOUT_TOP_LEVEL_ARTIFACTS"
  exit 0
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
echo "STATUS:PACKAGED"
