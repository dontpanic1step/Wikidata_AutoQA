#!/usr/bin/env bash
set -euo pipefail

cd /home/chenyue/Wikidata_Framework_aws

run="route3_all5_no_table_type_cached100_second_stage_2026_06_24_165720"
paths=(
  "outputs/${run}_summary.json"
  "outputs/aws_run_logs/${run}.log"
  "outputs/${run}_accepted.jsonl"
  "outputs/${run}_rejected.jsonl"
  "outputs/run_manifests/${run}.json"
  "outputs/recipe_segments/${run}"
)

for path in "${paths[@]}"; do
  case "$path" in
    outputs/*)
      if [ -e "$path" ]; then
        rm -rf -- "$path"
        echo "removed:$path"
      fi
      ;;
    *)
      echo "refused:$path" >&2
      exit 1
      ;;
  esac
done

echo "remaining old run refs:"
find outputs -maxdepth 4 \( -type f -o -type d \) | grep "$run" || true
