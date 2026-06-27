#!/usr/bin/env bash
set -euo pipefail

cd /home/chenyue/Wikidata_Framework_aws
source ~/.openrouter_env
export PYTHONPATH=src

RUN_ID="route3_all5_no_table_type_cached100_second_stage_2026_06_24_165720"
LOG_DIR="outputs/aws_run_logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/${RUN_ID}.log"

echo "Starting ${RUN_ID} at $(date -Is)" | tee "$LOG_FILE"

/home/chenyue/.venvs/wikidata-framework/bin/python scripts/run_wikipedia_infobox_recipe.py \
  --answer-type-count AllTypes=100 \
  --route3-reasoning-type single_fact \
  --route3-answer-type-mode all5 \
  --stream-reuse-cached-page-count 100 \
  --enable-second-stage-grading \
  --generation-model google/gemini-3.5-flash \
  --small-model-max-tokens 4096 \
  --run-id "$RUN_ID" \
  2>&1 | tee -a "$LOG_FILE"

status=${PIPESTATUS[0]}
echo "Finished ${RUN_ID} with status ${status} at $(date -Is)" | tee -a "$LOG_FILE"
exit "$status"
