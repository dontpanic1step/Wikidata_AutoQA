# `codex/reconstruction-stabilization` Dependency and Cleanup Roadmap

Last verified against the branch implementation on 2026-07-26.

The branch slash is normalized to an underscore in this filename because `/` cannot be part of a Windows filename. This document is an implementation snapshot and a guide for later deletion work. It does not replace `AGENTS.md`, `docs/design.md`, `docs/contract.md`, or `docs/default_settings.md`.

## 1. Supported boundary

| Surface | Entry point | Role | Network use |
| --- | --- | --- | --- |
| Route 3 generation | `scripts/run_wikipedia_infobox_recipe.py` | Only user-facing generation entry point | Wikipedia, DuckDuckGo, OpenRouter |
| Route 3 segment worker | `scripts/run_wikipedia_infobox_pipeline.py` | Internal subprocess and helper provider for the recipe | Wikipedia, DuckDuckGo, OpenRouter |
| Manual review export/apply | `scripts/run_route3_review.py` | Creates review artifacts and applies human edits | OpenRouter topic calls; edited Q/A also reruns DuckDuckGo and grading |
| Finalization | `scripts/finalize_route3_review.py` | Validates current review state and emits final CSV | None |
| Independent prediction | `scripts/run_openrouter_batch_predictions.py` | Runs evaluation-model predictions | OpenRouter |
| Independent judging | `scripts/judge_openrouter_batch_predictions.py` | Applies the protected SimpleQA Verified-style grader | OpenRouter |

Route 1, Route 2, Route 4, KELM, the old finalization workflow, and `scripts/run_openrouter_night_batch.py` are historical. The night orchestrator is unused. The two protected evaluation scripts remain supported but are deliberately outside generation, review, and finalization. Prediction input is CSV only; prediction and judge artifacts remain JSONL.

### Current stabilization baseline

Two committed changes define the cleanup baseline:

- `2d5a696 fix(route3): preserve slot failure semantics` made Route 3 unexpected DDG, grading, generation, and persistence exceptions propagate instead of becoming terminal content rejection; made deterministic persisted-response and non-retryable HTTP failures explicit; made review rerun rejection terminal; and made all5 attempt002 exhaustion slot-local.
- `f9ea86d feat(evaluation): read batch inputs from csv` changed the independent prediction input to CSV only while preserving prediction/judge prompts, OpenRouter call behavior, parameters, and JSONL artifacts.

The Route 3 change was verified with `191 passed, 31 subtests passed` for the directly affected files and `696 passed, 76 subtests passed` for the complete `tests/` suite at that commit. The subsequent protected evaluation change was verified with `13 passed` in `tests/test_openrouter_batch_scripts.py`. These are evidence records, not permanent expected test counts.

Cleanup must treat the following behaviors as fixed:

- attempt001 slot infrastructure failure publishes no partial all5 result and is the only slot path to attempt002;
- attempt002 exhaustion rejects only the failing slot and continues the remaining slots;
- deterministic failures after slot creation reject only that slot, while an unparsable shared generation response rejects the page;
- unexpected Python or persistence exceptions keep the attempt uncommitted and propagate with traceback;
- review reruns convert returned rejection to `rejected`, while exceptions leave persisted review state pending rerun;
- prediction input is CSV only, mapping Route 3 `id/problem/answer` or SimpleQA Verified `original_index/problem/answer` into the unchanged prediction call path.

## 2. End-to-end call chain

```text
scripts/run_wikipedia_infobox_recipe.py
  -> acquire one OS-held segment writer lock
  -> read/create and fingerprint segment manifest
  -> build one internal-worker command
  -> scripts/run_wikipedia_infobox_pipeline.py (subprocess)
       -> rebuild durable ledger index and projections
       -> wikipedia_streaming.py / wikipedia_client.py
       -> wikipedia_infobox_generator.py
       -> route3_openrouter.py (durable generation calls)
       -> _process_stream_candidate_slots(...) (one candidate slot at a time)
            -> generation_pipeline.process_generated_candidates([candidate], ...)
                 -> deterministic validators and integrated answer-type gate
                 -> route3_ddg.py -> search_client.py -> ddgs
                 -> grading.py through route3_openrouter.py
            -> aggregate all5 slot outcomes under the attempt001/attempt002 contract
       -> route3_run_ledger.py (terminal allocation/attempt state)
  -> rebuild run-level accepted/rejected/summary projections
  -> write walkthrough and pre-review quantity prediction

scripts/run_route3_review.py export
  -> read accepted JSONL and every represented segment manifest
  -> route3_review.create_review_state(...)
  -> route3_openrouter.py (durable GPT-4.1-mini topic classification)
  -> review_state.json
  -> review_<start>-<actual-end>.md shards
  -> review.xlsx through openpyxl
  -> statistics.json

scripts/run_route3_review.py apply
  -> read review_state.json and review.xlsx
  -> append delete/edit revisions
  -> for edited Q/A only:
       generation_pipeline.process_generated_candidates([edited candidate], ...)
       -> deterministic checks -> DuckDuckGo -> second-stage grading
       -> durable topic reclassification
  -> returned rejection completes the revision as rejected
  -> replace review state, Markdown shards, XLSX, and statistics
  -> unexpected exception propagates before review-state replacement

scripts/finalize_route3_review.py
  -> load review state and XLSX
  -> validate one-to-one active revisions
  -> canonical-page allocation
  -> rebalance only when all five answer types remain
  -> topic-diversity removal within over-target answer types
  -> final CSV

Route 3 final CSV or SimpleQA Verified CSV
  -> scripts/run_openrouter_batch_predictions.py (CSV-only identity normalization)
  -> prediction JSONL
  -> scripts/judge_openrouter_batch_predictions.py
  -> judged JSONL
```

The recipe also imports private reporting helpers directly from the internal worker. It imports `_aggregate_phase_timings`, `_effective_stream_random_seed`, `_failure_reason_counts`, `_ensure_page_id_list_entry_metadata`, `_load_endpoint_jsonl`, `_phase_timing_stats`, `_llm_generation_table_yield_summary`, `_normalize_stream_fresh_cached_page_count`, `_normalize_stream_reuse_cached_page_count`, `_safe_artifact_id`, `_stream_budget_numeric_count`, `_survival_by_layer`, and `_write_stream_walkthrough`. The worker therefore cannot be deleted or freely rewritten merely because it is not user-facing.

## 3. Runtime state and artifact ownership

| Artifact or state | Owning code | Authority |
| --- | --- | --- |
| `segment_manifest.json` | recipe and `route3_run_ledger.py` | Segment identity, fingerprint, lifecycle status, and prediction summary |
| `page_allocations/*.json` | `route3_run_ledger.py` | Immutable page allocation and primary-budget consumption |
| `cache/route3_pages` | `wikipedia_streaming.py` and `wikipedia_client.py` | Archived page content; archive hash is retained in provenance |
| `external_calls/**` | `route3_external_calls.py`, `route3_external_lifecycle.py`, `route3_openrouter.py` | Durable OpenRouter intent, response/error, and ambiguity resolution |
| `ddg_verifier_results/**/result.json` | `route3_ddg.py` | Completed candidate-level DuckDuckGo decision and audit |
| `page_attempts/*.json` | `route3_run_ledger.py` | Terminal attempt ledger and typed attempt002 eligibility |
| Segment/run accepted and rejected JSONL | recipe and worker projection code | Rebuildable projections, not primary authority |
| `review_state.json` | `route3_review.py` | Stable candidate artifacts, revisions, segment fingerprints, and topic audits |
| Review Markdown/XLSX/statistics | `route3_review.py` | Human-facing projections of review state; XLSX is validated on apply/finalize |
| Final CSV | `route3_finalization.py` | Validated output projection with exact public columns |
| Prediction JSONL | `run_openrouter_batch_predictions.py` | Independent model answers derived from CSV input |
| Judged JSONL | `judge_openrouter_batch_predictions.py` | Independent SimpleQA Verified-style grading artifact |

Deletion work must preserve the authority order: manifest, allocation, page archive, external-call record, terminal attempt ledger, then rebuildable projections. The `*_state.json` generation file stores discovery telemetry and is not allocation or retry authority.

## 4. Key local module dependencies

| Component | Important direct local dependencies | Cleanup implication |
| --- | --- | --- |
| Recipe | `io`, `page_id_lists`, `route3_ids`, `route3_quantity_prediction`, `route3_external_lifecycle`, `route3_run_ledger`, `search_cli`, `wikipedia_infobox_generator`, internal worker helpers | Extract a small internal worker API before removing reporting or legacy worker code |
| Internal worker | `config`, `generation_models`, `generator_validators`, `generation_pipeline`, `grading`, `page_id_lists`, Route 3 durable modules, search modules, Wikipedia modules | `generation_pipeline` is the main historical coupling |
| Wikipedia generator | `cheap_model_qa.parse_json_object`, `route3_openrouter`, `generation_models`, date/number/text normalizers, `route3_quality_rules`, Wikipedia client | The `cheap_model_qa` module name is historical-looking, but its JSON parser is currently used and cannot simply be deleted |
| Review | `generation_models`, `route3_artifacts`, `route3_ddg`, `route3_ids`, `route3_openrouter`, `route3_quantity_prediction`, `route3_run_ledger`, plus a local import of `generation_pipeline` for edited Q/A | Export and no-edit apply are narrower than edited-Q/A apply |
| Finalization | `route3_artifacts`, `route3_quantity_prediction`, `route3_review` | No network dependency; imports XLSX review code because workbook parsing lives in `route3_review.py` |
| Search | `search_client`, `search_cli`, `network` | `ddgs` is preferred; urllib HTML/Lite behavior remains part of the current bounded search implementation |
| Protected evaluation | self-contained scripts plus standard-library `csv` and `requests` | Input is CSV and prediction/judge artifacts are JSONL; keep independent from Route 3 durable execution and do not reorganize protected prompts, calls, or grading semantics |

## 5. Third-party and environment dependencies

The source scan and installed working environment produced this direct dependency boundary:

| Package | Classification | Current status |
| --- | --- | --- |
| Python `>=3.11` | interpreter | Declared in `pyproject.toml` |
| `openpyxl>=3.1,<4` | direct runtime | Declared; XLSX read/write/style/validation |
| `et-xmlfile` | transitive runtime | Installed by `openpyxl`; XLSX XML serialization |
| `ddgs` | direct runtime | Used lazily by `search_client.py`; not declared in project metadata |
| `requests` | direct runtime | Used by the two protected evaluation scripts; not declared in project metadata |
| `PySocks` (`socks` import) | conditional direct runtime | Required for configured SOCKS proxies; not declared in project metadata |
| `pytest` | development/test | Test runner; not declared in project metadata |
| `setuptools>=68` | build system | Declared under `[build-system]` |

The installed `ddgs` package directly requires `click`, `fake-useragent`, `httpx`, `lxml`, and `primp`. The installed `requests` package directly requires `certifi`, `charset-normalizer`, `idna`, and `urllib3`. These are dependency-manager concerns unless project code begins importing them directly.

The immediate metadata gap is intentional documentation of current reality, not a request to change packaging in this commit. A later cleanup commit should decide whether `ddgs` belongs in required dependencies or in a Route 3 extra, whether `requests` belongs in an evaluation extra, and whether `PySocks` belongs in a proxy extra. That decision should not silently change the supported default installation.

## 6. Historical coupling that blocks deletion

### 6.1 Package initialization loads historical pipelines

`src/wikidata_simpleqa/__init__.py` imports both `generation_pipeline.run_generation_pipeline` and `pipeline.run_pipeline` unconditionally. Importing any `wikidata_simpleqa.*` submodule first executes this package initializer. Consequently, generation, review, and finalization currently load a much broader graph than their direct imports suggest.

A clean-process import check of each current Route 3 entry point loaded the following explicitly historical modules:

- `route1_hidden_entity`
- `route1_multihop`
- `route1_validators`
- `route4_template_catalog`
- `route4_two_hop`
- `route4_two_hop_template_catalog`

The package initializer also pulls the older `pipeline.py` graph, including candidate harvesting, canonical-question, Wikidata, and old validator modules. Removing any of those files before narrowing `__init__.py` will break even finalization at import time.

### 6.2 Shared `generation_pipeline.py` mixes formal and historical routes

The internal Route 3 worker calls `process_generated_candidates` from `generation_pipeline.py`. That module imports Route 1 and Route 4 code at module scope and imports `generators.py`, whose module scope also imports Route 1 and Route 4 implementations. Route 2 lives as classes and branches inside `generators.py`, `generation_pipeline.py`, and `llm_rewrite.py`, rather than in one self-contained Route 2 module. KELM branches remain in `generation_pipeline.py`, `generator_validators.py`, and `llm_rewrite.py`. The formal Route 3 post-generation slice is therefore coupled to every inactive generation family.

The all5 page-level wrapper `_process_stream_candidate_slots` currently lives in the worker and is formal semantic code: it invokes the shared processor one slot at a time and enforces attempt001 rollback and attempt002 slot-local exhaustion.

Review apply repeats the coupling when a human changes a question or answer because `route3_review.post_generation_processor` imports `process_generated_candidates`. Any extraction must keep the exact formal order and exception/rejection semantics used by both the worker and review reruns.

### 6.3 Script-to-script private imports

The recipe imports private helper functions from the worker while also launching that worker as a subprocess. This combines orchestration, worker execution, endpoint projection, and reporting in two script files. Deleting or renaming worker helpers can break the recipe before a subprocess starts.

### 6.4 Review/finalization XLSX coupling

`route3_finalization.py` imports `route3_review.py`, so finalization imports `openpyxl` even though CSV writing itself does not need XLSX internals. This is a legitimate current dependency because finalization validates the human workbook, but it should be kept in mind if review I/O is later split from review-state logic.

### 6.5 Historical names do not prove dead code

At least two historically named areas still provide active primitives:

- `cheap_model_qa.parse_json_object` is used to parse model JSON; this does not mean the removed cheap-model exact-match rejection stage is active.
- `generation_pipeline.process_generated_candidates` supplies the formal post-generation sequence to both generation and review reruns.

Future deletion should be based on import/call evidence and tests, not filename matching.

## 7. Cleanup classification

### Retain as the formal production core

- The six supported entry points listed in section 1.
- `wikipedia_infobox_generator.py`, `wikipedia_client.py`, and `wikipedia_streaming.py`.
- `page_id_lists.py`, `search_client.py`, `search_cli.py`, and `network.py`.
- All `route3_*` modules until a focused extraction proves a smaller boundary.
- Shared models and normalizers actually reached by the formal chain.
- Protected evaluation tests and prompt contracts.

### Isolate before any historical deletion

1. Add clean-process import-boundary tests, then narrow `wikidata_simpleqa/__init__.py` so importing a submodule does not import old pipelines.
2. Extract the Route 3 post-generation operation from `generation_pipeline.py` into a Route 3-owned module. Move or explicitly preserve the worker's per-slot all5 aggregation boundary with it.
3. Point both the worker and review reruns at that operation and prove identical records, stage order, attempt eligibility, and exception propagation on fixed fixtures.
4. Move recipe-needed worker reporting helpers into a package module with a public internal API, or keep the worker intact until that extraction is complete.
5. Separate review-state/workbook I/O only if it materially simplifies finalization imports; do not change workbook or CSV contracts during the split.
6. Declare the chosen runtime/test dependency groups only after the supported installation contract is decided.

### Candidate historical entry points after isolation

The following are candidates for later removal because project policy marks their workflows historical, not because this roadmap has proven every imported helper dead:

- `scripts/run_route1_multihop_pipeline.py`
- `scripts/run_route1_hidden_entity_two_hop_pipeline.py`
- `scripts/run_route4_two_hop_pipeline.py`
- `scripts/run_kelm_half_pipeline.py`
- `scripts/run_stage5b_workflow.py`
- `scripts/generate_stage5_pilot.py`
- `scripts/generate_stage5b_pilot.py`
- `scripts/generate_pilot.py`
- `scripts/finalize_wikipedia_stream_batch.py`
- `scripts/run_final_llm_qa_filter.py`
- `scripts/run_openrouter_night_batch.py`

Related package modules, fixtures, tests, and documentation can be removed only after the production import closure is narrowed and repository references are audited. `scripts/build_wikipedia_accepted_qa_review.py` is also historical as an entry point, but its presentation behavior informed the current Route 3 review implementation; compare outputs before deleting it.

Package-side removal candidates include the `route1_*` and `route4_*` modules, `kelm_generator.py`, and route-specific classes or branches in `generators.py`, `generation_pipeline.py`, `generator_validators.py`, and `llm_rewrite.py`. Shared files must remain until every historical branch has been removed and a fresh supported import-closure check proves the remainder unreachable. Older `pipeline.py`, Wikidata clients/templates, validators, harvesting, and final-selection helpers are later candidates only on the same evidence; their names alone do not authorize deletion.

### Explicitly protected from cleanup-by-association

- `scripts/run_openrouter_batch_predictions.py`
- `scripts/judge_openrouter_batch_predictions.py`
- Their CSV input mapping, JSONL artifacts, protected prompts and calls, examples, grading labels, unparseable-output behavior, and tests

## 8. Recommended deletion sequence

Each numbered item should be one small reviewable change with its own test-backed commit.

1. Add import-boundary tests for the four Route 3 scripts and two protected evaluation scripts. Record which local modules are allowed to load on `--help` or import.
2. Narrow package initialization without changing public behavior still used by tests. Confirm Route 3 entry points no longer import historical modules merely by starting.
3. Extract only the Route 3 post-generation slice and its per-slot all5 aggregation boundary. Preserve deterministic validation, the integrated answer-type gate, DuckDuckGo, second-stage order, attempt semantics, and exception taxonomy.
4. Point the internal worker and edited-Q/A review reruns to the extracted slice. Verify identical accepted/rejected records and exception outcomes on fixed offline fixtures.
5. Extract the recipe reporting/helper API from the worker, leaving the worker as the internal executable boundary.
6. Recompute and record the supported import closure.
7. Remove one historical family per commit, including only its now-unreferenced scripts, modules, tests, and non-authoritative docs. A conservative order is KELM, Route 4, Route 2, then Route 1, but recompute the closure after every family and keep shared `generators.py` until its last live branch is gone.
8. Remove old finalization and the unused night orchestrator in separate commits; do not touch the two protected evaluation tools in either commit.
9. Tighten packaging metadata only after the supported dependency contract is decided, and verify it in `simpleqa_synth` or another clean Python 3.11 environment without modifying base Python 3.10.
10. Run the complete offline suite and a bounded Route 3 rehearsal before declaring cleanup complete.

Do not combine route deletion with output-schema redesign, fallback changes, prompt changes, retry changes, or new heuristics. Those are separate design decisions.

## 9. Verification matrix

| Change area | Minimum focused tests |
| --- | --- |
| Package import boundary | New clean-process import tests; all four current Route 3 script `--help` paths |
| Recipe/worker separation | `tests/test_wikipedia_infobox_recipe.py`, `tests/test_route3_run_ledger.py`, `tests/test_route3_rehearsal.py` |
| Wikipedia generation | `tests/test_wikipedia_infobox_generator.py`, `tests/test_generation_pipeline.py`, `tests/test_generator_validators.py` |
| DDG/search | `tests/test_search_client.py`, `tests/test_route3_ddg.py`, `tests/test_route3_external_control.py` |
| Durable OpenRouter | `tests/test_route3_openrouter.py`, `tests/test_route3_external_calls.py`, `tests/test_route3_external_control.py` |
| Stable artifacts and IDs | `tests/test_route3_artifacts.py`, `tests/test_route3_ids.py`, `tests/test_route3_run_ledger.py` |
| Review and quantity prediction | `tests/test_route3_review.py`, `tests/test_route3_quantity_prediction.py` |
| Finalization | `tests/test_route3_finalization.py` |
| Protected evaluation | `tests/test_openrouter_batch_scripts.py` |
| Any historical deletion | All focused tests above, then `python -m pytest tests -q -p no:cacheprovider --basetemp=tmp\pytest-cleanup` |

Run every Python and test command after activating `simpleqa_synth`. The counts in section 1 record the current stabilization evidence; future cleanup must not hard-code them as a pass condition. Scope the complete suite to `tests/` because output directories may contain inaccessible run artifacts, and use a unique writable `--basetemp` for each concurrent or repeated run.

## 10. Invariants that cleanup must preserve

- One writer per segment from manifest read/create through worker and projection completion.
- Same-fingerprint resume and complete-segment reuse; top-up always creates a new segment.
- Immutable page allocations and at most attempt001 plus one typed attempt002.
- All5 attempt001 publishes no partial slot outcomes; attempt002 exhaustion rejects only the failing slot and continues the rest.
- Durable OpenRouter intent-before-send and raw response/error persistence.
- Candidate-level durable DDG decisions and fixed service circuit behavior.
- A persisted unparsable shared generation response is page-level; deterministic post-generation candidate failures are slot-level.
- Unexpected Python and persistence exceptions propagate without creating terminal rejection, including during edited-Q/A review reruns.
- Stable candidate IDs, immutable provenance, append-only human revisions, and revision-scoped external-call keys.
- Review shard names use the actual inclusive range, for example `_1-50.md` and `_51-68.md`.
- Topic remains automatically assigned and read-only in XLSX; `human_edited` remains automatically derived.
- Missing answer types skip review prediction and final rebalancing rather than producing an empty CSV.
- Final CSV columns remain exactly `id`, `problem`, `answer`, `topic`, `answer_type`, and `urls`; `urls` remains a JSON array string encoded as one CSV field.
- No historical similarity, subject-URL, domain round-robin, or `final_selection.py` behavior re-enters formal finalization.
- No new fallback, heuristic gate, or defensive recovery path is introduced during cleanup.
- Protected prediction input remains CSV only with `id` or `original_index` normalized to output `id`; prediction and judge artifacts remain JSONL.
- Protected evaluation prompts, OpenRouter call behavior, and grader semantics remain independent and unchanged.

## 11. Evidence commands for the next cleanup session

Run these read-only checks before deleting a family of files:

```powershell
& 'D:\miniconda3\shell\condabin\conda-hook.ps1'
conda activate simpleqa_synth
git status --short
rg -n "^(from|import) " scripts\run_wikipedia_infobox_recipe.py scripts\run_wikipedia_infobox_pipeline.py scripts\run_route3_review.py scripts\finalize_route3_review.py
rg -n "route1|route2|route4|kelm|final_selection" scripts src tests README.md docs
rg -n "process_generated_candidates|_process_stream_candidate_slots" scripts src tests
python scripts\run_wikipedia_infobox_recipe.py --help
python scripts\run_route3_review.py --help
python scripts\finalize_route3_review.py --help
python scripts\run_openrouter_batch_predictions.py --help
python scripts\judge_openrouter_batch_predictions.py --help
python -m pytest tests -q -p no:cacheprovider --basetemp=tmp\pytest-cleanup-route3
```

An import search is necessary but not sufficient: local imports inside review rerun functions and subprocess construction are reachable dependencies even when they do not appear in a simple import-time module list.
