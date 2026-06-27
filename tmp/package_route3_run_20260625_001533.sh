#!/usr/bin/env bash
set -euo pipefail

cd /home/chenyue/Wikidata_Framework_aws

run="route3_all5_no_table_type_cached100_second_stage_2026_06_25_001533"
archive="/home/chenyue/${run}_artifacts.tgz"

tar -czf "$archive" \
  "outputs/${run}_summary.json" \
  "outputs/${run}_accepted.jsonl" \
  "outputs/${run}_rejected.jsonl" \
  "outputs/run_manifests/${run}.json" \
  "outputs/aws_run_logs/${run}.log" \
  "outputs/recipe_segments/${run}" \
  "docs/walkthroughs/${run}.md"

ls -lh "$archive"
