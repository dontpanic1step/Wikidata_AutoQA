#!/usr/bin/env bash
set -euo pipefail

cd "$HOME/Wikidata_Framework_aws"
base="outputs/recipe_segments/wikipedia_stream_recipe_200person_200place_single_fact_infobox_only_2026_06_02_supplement_accepteds_excluded"

tar -xzf "$HOME/route3_restore_person_place_before_bad_rerun.tgz" -C "$base"

python3 - <<'PY'
import json
from pathlib import Path

base = Path("outputs/recipe_segments/wikipedia_stream_recipe_200person_200place_single_fact_infobox_only_2026_06_02_supplement_accepteds_excluded")
for label, prefix in [
    ("person", "01_person_200_seed_accepteds_only"),
    ("place", "02_place_200_seed_accepteds_only"),
]:
    state = json.loads((base / f"{prefix}_state.json").read_text())
    summary = json.loads((base / f"{prefix}_summary.json").read_text())
    print(
        "restored",
        label,
        "accepted",
        len(state.get("accepted_ids", [])),
        "rejected",
        len(state.get("rejected_ids", [])),
        "rerun_pool",
        len(state.get("rerun_pool", [])),
        "summary_model",
        summary.get("small_model"),
        "summary_date",
        summary.get("run_date"),
    )
PY

source "$HOME/.openrouter_env"
python3 - <<'PY'
import json
import os
import urllib.request

key = os.environ["OPENROUTER_API_KEY"]
for model in ["openai/gpt-4.1-mini", "google/gemini-3-flash-preview"]:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Answer with OK."}],
        "max_tokens": 2,
        "temperature": 0,
    }
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    print("model_probe_ok", model, bool(body.get("choices")))
PY
