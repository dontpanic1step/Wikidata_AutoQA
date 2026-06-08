#!/usr/bin/env bash
set -euo pipefail

cd "$HOME/Wikidata_Framework_aws"
source "$HOME/.openrouter_env"
export PYTHONPATH="$HOME/Wikidata_Framework_aws/src"

python3 scripts/run_wikipedia_infobox_recipe.py \
  --recipe "200 Person, 200 Place, single_fact" \
  --run-id wikipedia_stream_recipe_200person_200place_single_fact_infobox_only_2026_06_02_supplement_accepteds_excluded \
  --target-time 2024 \
  --cutoff-year 2025 \
  --timeout-seconds 45 \
  --proxy none \
  --enable-second-stage-grading \
  --second-stage-grading-accuracy-threshold 0.1 \
  --duckduckgo-top-k 5 \
  --duckduckgo-parallel-queries 3 \
  --generated-search-query-count 3 \
  --stream-page-source table-search \
  --stream-search-query insource:Infobox \
  --stream-search-limit 50 \
  --stream-page-workers 4 \
  --wikipedia-concurrency-limit 4 \
  --duckduckgo-concurrency-limit 4 \
  --openrouter-generation-rewrite-concurrency-limit 10 \
  --second-stage-concurrency-limit 10 \
  --big-batch-mode \
  --append-to-existing-run \
  --append-run-label seed_accepteds_only \
  --route3-table-source-type infobox
