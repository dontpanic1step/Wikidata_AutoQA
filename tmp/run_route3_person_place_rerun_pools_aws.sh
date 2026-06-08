#!/usr/bin/env bash
set -euo pipefail

cd "$HOME/Wikidata_Framework_aws"
source "$HOME/.openrouter_env"
export PYTHONPATH="$HOME/Wikidata_Framework_aws/src"

python3 - <<'PY'
from pathlib import Path
import sys

from wikidata_simpleqa.wikipedia_streaming import PageIdStreamState

sys.path.insert(0, "scripts")
import run_wikipedia_infobox_pipeline as pipeline

print(
    "code_sync_ok",
    hasattr(PageIdStreamState, "rerun_error_details"),
    hasattr(pipeline, "_rerun_error_details_from_record"),
)
PY

base="outputs/recipe_segments/wikipedia_stream_recipe_200person_200place_single_fact_infobox_only_2026_06_02_supplement_accepteds_excluded"
common_args=(
  --stream-random-page-ids
  --stream-rerun-pool-only
  --stream-rerun-pool-limit 0
  --record-limit 1
  --run-group-id wikipedia_stream_recipe_200person_200place_single_fact_infobox_only_2026_06_02_supplement_accepteds_excluded
  --target-time 2024
  --cutoff-year 2025
  --timeout-seconds 45
  --proxy none
  --small-model-provider openrouter
  --small-model openai/gpt-4.1-mini
  --small-model-api-key-env OPENROUTER_API_KEY
  --small-model-base-url https://openrouter.ai/api/v1
  --small-model-max-tokens 1200
  --duckduckgo-top-k 5
  --duckduckgo-parallel-queries 3
  --generated-search-query-count 3
  --search-longtail-max-full-question-hit-rate 0.3
  --search-longtail-max-keyword-hit-rate 0.3
  --search-longtail-max-overall-hit-rate 0.3
  --stream-page-source table-search
  --stream-search-limit 50
  --stream-search-max-rounds 20
  --stream-discovery-max-retries 5
  --stream-discovery-retry-backoff-seconds 10
  --stream-discovery-retry-max-sleep-seconds 60
  --wikipedia-429-backoff-seconds 60
  --wikipedia-429-max-backoff-seconds 600
  --wikipedia-429-recovery-seconds 300
  --stream-search-initial-offset 0
  --stream-batch-size 10
  --stream-page-workers 4
  --wikipedia-concurrency-limit 4
  --duckduckgo-concurrency-limit 4
  --openrouter-generation-rewrite-concurrency-limit 10
  --second-stage-concurrency-limit 10
  --route3-reasoning-type single_fact
  --route3-table-source-type infobox
  --route3-prose-leakage-scoring
  --no-route3-llm-choose-table
  --enable-second-stage-grading
  --second-stage-grading-accuracy-threshold 0.1
  --big-batch-mode
  --compact-output
  --stream-search-query insource:Infobox
)

python3 scripts/run_wikipedia_infobox_pipeline.py \
  "${common_args[@]}" \
  --route3-answer-type Person \
  --run-segment-id 01_person_200_seed_accepteds_only \
  --stream-state "$base/01_person_200_seed_accepteds_only_state.json" \
  --output "$base/01_person_200_seed_accepteds_only_accepted.jsonl" \
  --rejected-output "$base/01_person_200_seed_accepteds_only_rejected.jsonl" \
  --summary-output "$base/01_person_200_seed_accepteds_only_summary.json"

python3 scripts/run_wikipedia_infobox_pipeline.py \
  "${common_args[@]}" \
  --route3-answer-type Place \
  --run-segment-id 02_place_200_seed_accepteds_only \
  --stream-state "$base/02_place_200_seed_accepteds_only_state.json" \
  --output "$base/02_place_200_seed_accepteds_only_accepted.jsonl" \
  --rejected-output "$base/02_place_200_seed_accepteds_only_rejected.jsonl" \
  --summary-output "$base/02_place_200_seed_accepteds_only_summary.json"

python3 - <<'PY'
import json
from pathlib import Path

base = Path("outputs/recipe_segments/wikipedia_stream_recipe_200person_200place_single_fact_infobox_only_2026_06_02_supplement_accepteds_excluded")
for label, name in [
    ("person", "01_person_200_seed_accepteds_only_state.json"),
    ("place", "02_place_200_seed_accepteds_only_state.json"),
]:
    payload = json.loads((base / name).read_text())
    print(
        label,
        "accepted",
        len(payload.get("accepted_ids", [])),
        "rejected",
        len(payload.get("rejected_ids", [])),
        "rerun_pool",
        len(payload.get("rerun_pool", [])),
        "rerun_error_details",
        len(payload.get("rerun_error_details", {})),
    )
PY
