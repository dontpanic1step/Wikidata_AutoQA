#!/usr/bin/env bash
set -euo pipefail

cd "$HOME/Wikidata_Framework_aws"
source "$HOME/.openrouter_env"
export PYTHONPATH="$HOME/Wikidata_Framework_aws/src"

run_id="wikipedia_stream_route3_all5_200_single_fact_infobox_only_inherited_redirected_passed_all_2026_06_08"
segment_id="01_all5_200_inherited_redirected_passed_all_infobox_only"
base="outputs/recipe_segments/$run_id"
inherit="tmp/route3_tmp_redirected_passed_all_accepted_page_ids_2026_06_08/accepted_page_ids.json"

mkdir -p "$base"
cp "$inherit" "$base/inherited_accepted_page_ids.json"

python3 scripts/run_wikipedia_infobox_pipeline.py \
  --stream-random-page-ids \
  --record-limit 200 \
  --route3-answer-type-mode all5 \
  --run-group-id "$run_id" \
  --run-segment-id "$segment_id" \
  --stream-state "$base/${segment_id}_state.json" \
  --output "$base/${segment_id}_accepted.jsonl" \
  --rejected-output "$base/${segment_id}_rejected.jsonl" \
  --summary-output "$base/${segment_id}_summary.json" \
  --target-time 2024 \
  --cutoff-year 2025 \
  --timeout-seconds 45 \
  --proxy none \
  --small-model-provider openrouter \
  --small-model openai/gpt-4.1-mini \
  --small-model-api-key-env OPENROUTER_API_KEY \
  --small-model-base-url https://openrouter.ai/api/v1 \
  --small-model-max-tokens 1200 \
  --duckduckgo-top-k 5 \
  --duckduckgo-parallel-queries 3 \
  --generated-search-query-count 3 \
  --search-longtail-max-full-question-hit-rate 0.3 \
  --search-longtail-max-keyword-hit-rate 0.3 \
  --search-longtail-max-overall-hit-rate 0.3 \
  --stream-page-source table-search \
  --stream-search-query insource:Infobox \
  --stream-search-limit 50 \
  --stream-search-max-rounds 500 \
  --stream-discovery-max-retries 5 \
  --stream-discovery-retry-backoff-seconds 10 \
  --stream-discovery-retry-max-sleep-seconds 60 \
  --wikipedia-429-backoff-seconds 60 \
  --wikipedia-429-max-backoff-seconds 600 \
  --wikipedia-429-recovery-seconds 300 \
  --stream-search-initial-offset 0 \
  --stream-exclude-page-id-file "$inherit" \
  --stream-batch-size 50 \
  --stream-page-workers 4 \
  --wikipedia-concurrency-limit 4 \
  --duckduckgo-concurrency-limit 4 \
  --openrouter-generation-rewrite-concurrency-limit 10 \
  --second-stage-concurrency-limit 10 \
  --route3-reasoning-type single_fact \
  --route3-table-source-type infobox \
  --route3-prose-leakage-scoring \
  --no-route3-llm-choose-table \
  --route3-pageview-prefilter \
  --enable-second-stage-grading \
  --second-stage-grading-accuracy-threshold 0.1 \
  --stream-auto-rerun-once \
  --big-batch-mode \
  --compact-output \
  --reset-stream-state
