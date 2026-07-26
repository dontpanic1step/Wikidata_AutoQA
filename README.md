# Wikidata Framework Route 3 Runbook

This runbook describes the supported workflow on the current branch. Historical generation routes may still exist in the tree, but they are not supported entry points.

## Formal workflow boundary

- Route 3 is the only formal generation route.
- `scripts/run_wikipedia_infobox_recipe.py` is the only user-facing generation entry point.
- `scripts/run_wikipedia_infobox_pipeline.py` is an internal segment worker. Do not invoke it as a separate user workflow.
- Route 1, Route 2, Route 4, KELM, the old finalization flow, and `scripts/run_openrouter_night_batch.py` are historical and are not part of this runbook.
- `scripts/run_openrouter_batch_predictions.py` and `scripts/judge_openrouter_batch_predictions.py` are independent evaluation tools, not generation commands.

## Environment

- Python 3.11 or newer.
- In this workspace, activate the dedicated `simpleqa_synth` conda environment before every project or cleanup command. Do not upgrade or modify the base Python 3.10 environment.
- Run commands from the repository root.
- Network generation reads the OpenRouter key from `OPENROUTER_API_KEY`.
- Do not place API keys in commands, config files, logs, or committed artifacts.

Install the package and the two runtime packages that are not currently declared by `pyproject.toml`:

```powershell
python -m pip install -e .
python -m pip install ddgs requests
# Required only when a SOCKS proxy is configured:
python -m pip install PySocks
```

The supported surfaces use these packages:

| Package | Status | Used by |
| --- | --- | --- |
| `openpyxl>=3.1,<4` | direct dependency declared in `pyproject.toml` | Route 3 XLSX export, import, and validation |
| `et-xmlfile` | transitive dependency installed by `openpyxl` | XLSX XML serialization; project code does not import it directly |
| `ddgs` | direct runtime dependency not yet declared | Preferred DuckDuckGo search transport for Route 3 generation and review reruns |
| `requests` | direct runtime dependency not yet declared | Independent batch prediction and judge scripts |
| `PySocks` | conditional runtime dependency not yet declared | SOCKS proxy support used by the shared network helper and by `requests` when a SOCKS proxy is configured |
| `pytest` | development/test dependency not declared by project metadata | Offline test suite |

`ddgs` currently brings `click`, `fake-useragent`, `httpx`, `lxml`, and `primp`; `requests` brings `certifi`, `charset-normalizer`, `idna`, and `urllib3`. These are transitive dependencies, not direct imports in the supported project code. Apart from the packages listed above, the supported runtime code uses the Python standard library. The metadata gaps are recorded in the branch roadmap for later cleanup.


## Define one formal segment

Every formal recipe invocation defines one segment with three selectors:

| Flag | Meaning |
| --- | --- |
| `--page-attempt-count N` | Number of primary Wikipedia pages to attempt. |
| `--answer-type TYPE` | `Person`, `Place`, `Number`, `Date`, `Other`, or `AllTypes`. |
| `--route3-answer-type-mode MODE` | `single` or `all5`. |

Valid combinations:

| Answer type | Mode |
| --- | --- |
| `Person`, `Place`, `Number`, `Date`, or `Other` | `single` |
| `AllTypes` | `all5` |

Specific answer type plus `all5`, and `AllTypes` plus `single`, are rejected.

`--page-attempt-count` is a unique primary-allocation target, not an accepted-question target. Attempt001 is derived from an allocation; the only eligible page-level rerun is attempt002 and it does not consume another primary allocation.

The former free-form `--recipe`, `--answer-type-count`, `--answer-types`, and `--per-answer-type` inputs are not supported.

## Formal defaults

| Setting | Default |
| --- | --- |
| Generation model | `google/gemini-3-flash-preview` |
| Generation maximum tokens | `4096` |
| Reasoning type | `single_fact` |
| Second-stage grading | enabled |
| Second-stage threshold | `0.1` |
| Second-stage answer models | `openai/gpt-4.1-mini`, `google/gemini-3-flash-preview` |
| Second-stage grader | `openai/gpt-4.1-mini` |
| Cached-page reuse | `all` |
| Fresh-page budget | `fill` |
| Page source | `table-search` |
| Search query | `insource:"wikitable"` |

The formal worker uses these fixed method settings; they are not CLI options:

| Setting | Fixed value |
| --- | --- |
| Table discovery | MediaWiki table search only |
| Custom, broad, or random page discovery | unavailable |
| Table filters | `no_external_links_tables`, `no_horizontal_companion_tables`, `no_picture_heavy_tables`, `no_incomplete_tables`, `not_number_dominant`, `no_social_science_research` |
| Prose-leakage scoring | enabled |
| Minimum table score | `0.0` |
| LLM table choice | disabled |
| Pageview prefilter | disabled |
| REST first-paragraph fallback | disabled |
| Extra generation prompt | unavailable |
| KELM rewrite | unavailable |

The recipe passes the selected answer type, answer-type mode, and table source type to the internal worker. The worker does not accept URL lists or an old validation-stage candidate input. Use the recipe entry point for both dry runs and network runs.

The DuckDuckGo thresholds use the current values listed in `docs/default_settings.md`.

The formal candidate checks run in this order:

1. table and source checks;
2. generation, parsing, and normalization;
3. effective surface and temporal checks;
4. the integrated answer-type gate;
5. answer support in the selected table;
6. DuckDuckGo long-tail filtering;
7. second-stage grading.

The integrated answer-type gate retains Date and Place rules. Person candidates have no local rule-based rejection heuristic and still pass through source validation, DuckDuckGo filtering, and second-stage grading.

The automated flow does not remove candidates solely because they share a subject resource or exact question. Page-level deduplication is deferred until finalization after manual review.

## Durable runs, resume, and top-up

A non-dry formal run requires a clean Git worktree. Commit code and configuration changes before starting it. For a run that may cross midnight, set `--run-date` explicitly so the resolved fingerprint remains stable. The recipe holds an OS-managed exclusive writer lock from before the segment manifest is read or created until the worker and projections finish. A second recipe process for the same segment fails immediately; the lock is released automatically when the holder exits or is killed, so recovery still uses the normal `--resume` command and durable artifacts.

Run a bounded 10-page Person segment:

```powershell
python scripts\run_wikipedia_infobox_recipe.py `
  --page-attempt-count 10 `
  --answer-type Person `
  --route3-answer-type-mode single `
  --run-id route3_person_pilot `
  --run-date 2026-07-24
```

Check ledger-derived status without starting a worker or making a network call:

```powershell
python scripts\run_wikipedia_infobox_recipe.py `
  --run-id route3_person_pilot `
  --status
```

Resume an interrupted segment with the exact initial arguments and explicit resume mode:

```powershell
python scripts\run_wikipedia_infobox_recipe.py `
  --page-attempt-count 10 `
  --answer-type Person `
  --route3-answer-type-mode single `
  --run-id route3_person_pilot `
  --run-date 2026-07-24 `
  --resume
```

The durable segment artifact contract is:

```text
outputs/recipe_segments/<run-id>/
  01_person_10/
    segment_manifest.json
    page_allocations/
      a<allocation_ordinal>_p<canonical_page_id>.json
    page_attempts/
      p<canonical_page_id>_attempt001.json
      p<canonical_page_id>_attempt002.json   # only when typed retry is eligible
    external_calls/
      p<canonical_page_id>/
        c_<logical_call_key_hash>/
          attempt001/
            intent.json
            response.json | http_error.json
            resolution.json | abandoned_ambiguous.json
          attempt002/                 # only after explicit retry authorization
            intent.json
            response.json | http_error.json
            resolution.json | abandoned_ambiguous.json
    ambiguous_external_calls.json
    ambiguous_external_calls.md
    ddg_verifier_results/
      p<canonical_page_id>/
        c_<candidate_key_hash>/
          result.json
  01_person_10_accepted.jsonl
  01_person_10_rejected.jsonl
  01_person_10_summary.json
  01_person_10_state.json
outputs/<run-id>_accepted.jsonl
outputs/<run-id>_rejected.jsonl
outputs/<run-id>_summary.json
outputs/<run-id>_walkthrough.md
```

The authority order is manifest, immutable allocation, Wikipedia page archive, external-call records, terminal ledger, and then derived endpoints. State stores discovery offsets and telemetry only. It cannot create or release allocations or decide retry. Accepted JSONL, rejected JSONL, summary, and projection are rebuildable. Independently published artifacts use same-directory unique temporary files and `os.replace`; archive hashes remain in provenance.

Resume an interrupted segment by rerunning with the same resolved generation arguments plus explicit `--resume`. Pending allocations continue attempt001. Completed OpenRouter calls and completed candidate-level DDG verifier results are reused; DDG candidate keys include the allocation, candidate slot, segment fingerprint, and human revision number when present; page preparation and deterministic validation may be recomputed in the same attempt. A matching complete segment is reused, while a fingerprint mismatch and an incomplete legacy schema are rejected.

All5 publishes one atomic page attempt. A typed slot-level DDG or OpenRouter infrastructure failure during attempt001 discards all in-memory partial slot outcomes and makes the page eligible for its single attempt002. During attempt002, retry exhaustion rejects only the failing slot and processing continues for the remaining slots before the atomic commit. Deterministic candidate failures after slot creation also reject only their slot. A persisted unparsable response from shared page generation rejects the page; an equivalent candidate-level response rejects only that candidate. Any other unexpected Python or persistence exception propagates with its traceback and leaves the attempt uncommitted and the segment incomplete.

The worker uses bounded batches in a fixed order: unfinished attempt001 work, missing primary allocations, the remaining primary work, then ledger-authorized attempt002 work. There is no rerun-pool, rerun-seed, or caller-selected primary/secondary CLI in the formal workflow; retry eligibility comes only from immutable attempt history.

An OpenRouter intent without a persisted response is ambiguous. The default is quarantine: no automatic retry and no attempt003. The two reports under the segment root list every unresolved call and its audit fields. OpenRouter and DuckDuckGo circuits use a fixed threshold of three and stop new calls and allocations without switching model, endpoint, proxy, or fallback. The segment remains `incomplete` and records `external_service` and/or `ambiguous` in `blocking_reasons`. After confirming that a tripped service has recovered, run the same recipe command with `--resume`; circuit counters start fresh for that invocation while ledger retry eligibility remains unchanged.

Resolve all currently unresolved calls in the same-fingerprint segment, then resume it with the otherwise identical recipe command:

```powershell
# Authorize one final physical call as external attempt002.
python scripts\run_wikipedia_infobox_recipe.py <same arguments> --resume --resolve-ambiguous retry

# Commit terminal abandonment without another physical call.
python scripts\run_wikipedia_infobox_recipe.py <same arguments> --resume --resolve-ambiguous abandon
```

Retry records the possible duplicate billing risk. If attempt002 is also ambiguous, `retry` is rejected and only `abandon` is allowed. Neither action changes the segment fingerprint, and neither option is valid for a new or top-up segment.

Add a separate top-up segment without modifying the prior segment:

```powershell
python scripts\run_wikipedia_infobox_recipe.py `
  --page-attempt-count 10 `
  --answer-type Person `
  --route3-answer-type-mode single `
  --run-id route3_person_pilot `
  --run-date 2026-07-24 `
  --append-to-existing-run `
  --append-run-label topup_01
```

Top-up is permitted only after prior segments are complete and protocol-compatible. The immutable run-group allocation ledger is the single exclusion source for both cached archives and fresh discovery. A top-up creates a new segment and allocates only canonical page IDs never allocated anywhere in the run group. It does not move, seed, clear, or otherwise read old rerun/state work, and it does not modify prior segment files. Resume an interrupted top-up with the same append label and add `--resume`; do not manipulate worker state directly.

Inspect the durable-run tests with:

```powershell
python -m pytest tests\test_route3_run_ledger.py `
  tests\test_wikipedia_infobox_recipe.py `
  tests\test_wikipedia_infobox_generator.py -q
```

## Pre-review quantity prediction

After a segment finishes automated processing, its `segment_manifest.json` contains `pre_review_quantity_prediction` with:

- accepted candidate count;
- canonical unique-page and multi-QA-page counts;
- answer-type counts after choosing one candidate per page;
- the recorded recipe seed;
- rebalance `N`, projected per-type targets, and projected final total.

The manifest prediction uses canonical-page allocation and the formal answer-type formula. It does not select or delete topics. Review export performs topic classification and writes its own pre-human-review statistics.

## Manual review loop

Export accepted candidates to durable review state, Markdown, and XLSX:

```powershell
python scripts\run_route3_review.py export `
  --accepted-input outputs\<run-id>_accepted.jsonl `
  --segment-manifest outputs\recipe_segments\<run-id>\<segment-id>\segment_manifest.json `
  --state-output outputs\reviews\<run-id>\review_state.json `
  --markdown-output outputs\reviews\<run-id>\review.md `
  --xlsx-output outputs\reviews\<run-id>\review.xlsx `
  --topic-concurrency-limit 2 `
  --run-id <run-id>
```

Repeat `--segment-manifest` for every top-up segment represented in the accepted JSONL. Before writing review artifacts, GPT-4.1-mini classifies each Q/A into one of the ten formal topics with temperature `0`, `max_tokens=256`, and bounded concurrency. Calls use the durable Route 3 OpenRouter executor under `topic_classification_calls`; review state retains the complete raw response. Invalid labels reject the candidate without retry or fallback. `--markdown-output` is a base path: the command writes shards of at most 50 candidates, and the final suffix uses the actual last candidate number. For 68 candidates, the files are `review_1-50.md` and `review_51-68.md`. Each shard contains accepted candidates only, with stable ID, Q/A, answer type, Wikipedia page, selected table, automatic topic, automatic human-edit status, and separately quoted two-model answers.

The export also writes `statistics.json` beside the XLSX. It records the original pre-human-review total, per-type counts and two-decimal percentages, plus predicted final totals. If any original answer type is absent, prediction is skipped and the JSON and CLI summary identify the missing types and risk.


The XLSX columns are exactly:

```text
id
question
reference_answer
wikipedia_url
topic
human_edited
delete
edited_question
edited_reference_answer
edit_reason
```

`topic` is assigned automatically and has no dropdown. Changing it in the workbook is rejected. `human_edited` is generated from Q/A revision history, defaults to `No`, becomes `Yes` after a human Q/A edit, and is also read-only. `delete` defaults to `No` and has the only `Yes/No` dropdown.

After editing the workbook, apply it and produce the next review round:

```powershell
python scripts\run_route3_review.py apply `
  --state-input outputs\reviews\<run-id>\review_state.json `
  --xlsx-input outputs\reviews\<run-id>\review.xlsx `
  --state-output outputs\reviews\<run-id>\review_state.json `
  --markdown-output outputs\reviews\<run-id>\review.md `
  --xlsx-output outputs\reviews\<run-id>\review.xlsx `
  --topic-concurrency-limit 2 `
  --run-id <run-id>
```

Deleted rows skip validation. Q/A edits preserve the stable ID and immutable generation provenance, append a revision, clear stale checks and the old topic, and rerun the formal post-generation checks, DuckDuckGo filter, two-model second stage, and GPT-4.1-mini topic classification. A returned deterministic rejection makes that revision `rejected`; it is not converted back to `rerun`. An unexpected exception propagates before replacement of review state, so the persisted revision remains pending rerun. This apply command makes network calls only when the state contains Q/A edits or pending reruns. The next Markdown shards/XLSX contain only latest accepted revisions.

## Formal finalization

Finalization requires no pending Q/A edits, no rerun revisions, a valid topic on every active row, and an XLSX that exactly matches the latest active candidate revisions.

```powershell
python scripts\finalize_route3_review.py `
  --state-input outputs\reviews\<run-id>\review_state.json `
  --xlsx-input outputs\reviews\<run-id>\review.xlsx `
  --output outputs\reviews\<run-id>\final.csv
```

Finalization first selects at most one candidate per canonical page with the deterministic allocation algorithm. When all five answer types remain, it applies the formal ratios and removes excess candidates iteratively from the largest eligible global topic with the recorded recipe seed. If any type is absent, it skips rebalancing and writes every page-allocated candidate. It never calls the historical similarity deduplication, subject-URL deduplication, domain round-robin, or `final_selection.py` paths.

The final CSV columns are exactly:

```text
id
problem
answer
topic
answer_type
urls
```

`urls` is a JSON array string. In raw CSV text, its inner JSON quotes are doubled by standard CSV escaping; a CSV parser restores the value before JSON parsing. The command prints the seed, page-dedup count, whether rebalancing was skipped, missing types, rebalance `N`, targets, final counts, final total, and selected IDs as a JSON summary.

## Independent batch evaluation

The evaluation scripts run after finalization. They do not generate candidates, filter Route 3 output, perform manual review, or finalize a dataset. Do not use the historical `run_openrouter_night_batch.py` orchestrator.

Create model predictions directly from a directory of CSV inputs. JSON and JSONL are not prediction inputs. Route 3 final CSV rows use `id`, `problem`, and `answer`; Google SimpleQA Verified rows use `original_index`, `problem`, and `answer`, with any additional columns accepted. The prediction output remains JSONL and uses `id`, mapping it from `original_index` when necessary:

```powershell
python scripts\run_openrouter_batch_predictions.py inputs\evaluation `
  --output-dir outputs\openrouter_batch_predictions `
  --models <prediction-model> `
  --rounds 1 `
  --limit 10
```

The prediction command resolves reasoning for the complete model list before it creates the evaluation queue. Its audited nine-model defaults are recorded in `docs/default_settings.md`. An unknown model without an explicit `--reasoning-effort` causes the entire batch to exit and list every unresolved model before any evaluation request is sent. Explicit effort values are sent unchanged, including `max`; `--use-provider-reasoning-defaults` explicitly opts unknown models into an omitted reasoning field. There is no option to disable reasoning.

Grade one prediction JSONL file or every matching JSONL file in a directory with the protected SimpleQA Verified prompt. The default judge is `openai/gpt-4.1-mini`:

```powershell
python scripts\judge_openrouter_batch_predictions.py `
  outputs\openrouter_batch_predictions `
  --output-dir outputs\openrouter_batch_judged `
  --limit 10
```

Both commands read the OpenRouter key from `OPENROUTER_API_KEY` by default. Use each command's `--help` output for the retained batch-evaluation options.

### Project Verification Agent handoff

Use the offline adapter with an input directory and a new output directory:

```powershell
python scripts\convert_batch_evaluation_for_verification_agent.py `
  outputs\openrouter_batch_judged `
  outputs\verification_agent_inputs
```

The adapter scans only top-level `*.jsonl` files; it never recurses. A file qualifies by content, not by filename: every nonblank line must have the current batch prediction/judging output fields `id`, `question`, `answer`, and `predictions`, with `predictions` as a list of objects. Nonconforming JSONL files are skipped and listed in the summary.

Each qualifying source file is converted independently to a same-named JSONL file in the new output directory. The output directory must not already exist. `conversion_summary.json` records every converted and skipped source, output path, source-record count, response-row count, question-group count, skip reason, and every source item that could not become an agent response row.

Each source `predictions[]` item becomes one response row. Rows within each output file are clustered by stable `(question_id, query)`, so all rounds for a question remain contiguous. Dataset-level IDs such as `original_index` or `simpleqa_verified_id` take precedence over model/repeat-specific row IDs.

The output's primary fields are the exact first-choice fields read by the real Project Verification Agent entry point, `runs/run_simpleqa_entry.py`:

```json
{
  "original_index": "stable-question-id",
  "query": "The original question",
  "model": "provider/model",
  "response": "One model response",
  "reference_answer": "retained source metadata",
  "verification_agent_adapter": {
    "schema_version": 1,
    "source_file": "absolute source path",
    "source_line_number": 1,
    "prediction_index": 0,
    "prediction_count": 5,
    "batch_record": {},
    "batch_prediction": {}
  }
}
```

The agent groups equal `(id, query)` rows into one sample's model outputs; retrieval then shares a question evidence pool by exact `query` within that run. `reference_answer` is preserved for audit only and is not supplied as evidence or used as the claim verdict target.

No source JSON value is discarded: `batch_record` contains the unchanged parent fields except `predictions`, and `batch_prediction` contains the unchanged selected prediction, including raw OpenRouter responses, token usage, request settings, errors, and judge audit when present. Source file, line, prediction index, and prediction count make each original record reconstructable in source order.

The complete directory is inspected before the new output directory is created. Empty prediction lists, empty model responses, missing stable identity/question values, and unresolved model IDs are not emitted as agent claims. Instead, `unconverted_items` in `conversion_summary.json` retains the exact parent record (apart from its separately represented `predictions` list), exact prediction when present, source file/line/index/count, and reason. A qualifying file with no usable responses produces no empty agent JSONL and is listed as skipped, while its source data remains in the summary. Use `--model-fallback` only when the exact model ID cannot be recovered from record content or the current batch filename.

Project Verification Agent's current code slices raw input rows with `START_LINE` and `NUM_LINES` before grouping model outputs. Configure that entry to include the intended number of converted response rows; it does not interpret the limit as a question count and can cut through a contiguous question group.

## Historical-code cleanup preparation

Later cleanup may remove Route 1, Route 2, Route 4, KELM, old finalization, and other historical entry points only after the supported import closure is narrowed. Current Route 3 startup still reaches historical code through two main couplings:

- `wikidata_simpleqa/__init__.py` eagerly imports `generation_pipeline` and the old `pipeline`;
- both the internal worker and edited-Q/A review reruns call `generation_pipeline.process_generated_candidates`, whose module still imports and branches for Route 1, Route 2, Route 4, and KELM.

Use the detailed sequence in `docs/reconstruction/codex_reconstruction-stabilization_roadmap.md`. In summary:

1. add clean-process import-boundary tests;
2. narrow `wikidata_simpleqa/__init__.py`;
3. extract the exact Route 3 post-generation operation, including the exception and all5 slot semantics documented above;
4. point both the worker and review reruns at that Route 3-owned operation;
5. recompute the import closure, then remove one historical family per test-backed commit;
6. keep `run_openrouter_batch_predictions.py`, `judge_openrouter_batch_predictions.py`, their prompts, and the CSV-to-prediction contract protected.

Do not combine historical deletion with prompt edits, output-schema changes, fallback changes, new heuristics, or unrelated bug fixes.

## Safe dry-run examples

Inspect a 10-page Person segment without making generation calls:

```powershell
python scripts\run_wikipedia_infobox_recipe.py `
  --page-attempt-count 10 `
  --answer-type Person `
  --route3-answer-type-mode single `
  --run-id route3_person_dry_run `
  --dry-run
```

Inspect a 10-page all5 segment:

```powershell
python scripts\run_wikipedia_infobox_recipe.py `
  --page-attempt-count 10 `
  --answer-type AllTypes `
  --route3-answer-type-mode all5 `
  --run-id route3_all5_dry_run `
  --dry-run
```

Use `python scripts\run_wikipedia_infobox_recipe.py --help` for the current formal argument list.

## Candidate artifact API

`src/wikidata_simpleqa/route3_artifacts.py` defines the stable candidate artifact schema:

- `Route3CandidateIdentity`
- `Route3CandidateProvenance`
- `Route3CandidateRevision`
- `Route3CandidateArtifact`
- `create_route3_candidate_artifact(...)`
- `revise_route3_candidate_artifact(...)`

Candidate IDs are derived only from run group ID, segment ID, canonical page ID, and original candidate slot. Question or answer edits append a revision and do not change the ID or immutable provenance.

Run the schema and ID tests with:

```powershell
python -m pytest tests\test_route3_artifacts.py tests\test_route3_ids.py -q
```

## Verification

Run the recipe interface tests:

```powershell
python -m pytest tests\test_wikipedia_infobox_recipe.py -q
```

Run the complete offline suite:

```powershell
python -m pytest tests -q -p no:cacheprovider --basetemp=tmp\pytest-readme
```
