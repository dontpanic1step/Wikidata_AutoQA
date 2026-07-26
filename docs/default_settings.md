# Current Route 3 Default Settings

This file records defaults used by the supported scripts on the current branch. Values were verified against `scripts/run_wikipedia_infobox_recipe.py`, the internal worker, and the Route 3 modules on 2026-07-26. Historical Route 1, Route 2, Route 4, KELM, direct-worker, night-orchestrator, and old-finalization defaults are intentionally omitted.

The required project environment for this workspace is the dedicated Python 3.11 conda environment `simpleqa_synth`. Activate it before every command; the base Python 3.10 environment is outside the project contract and must not be modified.

## Ownership

- Generation entry point: `scripts/run_wikipedia_infobox_recipe.py`.
- Internal worker: `scripts/run_wikipedia_infobox_pipeline.py`; do not invoke it as a separate workflow.
- Review entry point: `scripts/run_route3_review.py` with `export` and `apply`.
- Finalization entry point: `scripts/finalize_route3_review.py`.
- Independent evaluation: `scripts/run_openrouter_batch_predictions.py` and `scripts/judge_openrouter_batch_predictions.py`.
- Runtime package details are listed in `README.md`; current import and metadata gaps are listed in the branch roadmap under `docs/reconstruction/`.

## Required segment selectors

These values have no operational default and are required except for `--status`:

| Setting | Accepted values |
| --- | --- |
| `--page-attempt-count` | positive primary-page allocation target |
| `--answer-type` | `Person`, `Place`, `Number`, `Date`, `Other`, `AllTypes` |
| `--route3-answer-type-mode` | default `single`; use `single` with one specific type and `all5` with `AllTypes` |

The page-attempt count is not an accepted-QA target. Attempt002 does not consume another primary allocation.

## Model and validation defaults

| Setting | Default |
| --- | --- |
| Target time | `2024` |
| Question cutoff year | `2025` |
| Request timeout | `30` seconds |
| Proxy | direct (`none`) |
| Provider | `openrouter` |
| Base URL | `https://openrouter.ai/api/v1` |
| API-key environment variable | `OPENROUTER_API_KEY` |
| Generation model | `google/gemini-3-flash-preview` |
| Generation temperature | `0.0` |
| Generation maximum tokens | `4096` |
| Reasoning type | `single_fact` |
| Second-stage grading | enabled |
| Second-stage accuracy threshold | `0.1` |
| Answer models | `openai/gpt-4.1-mini`, `google/gemini-3-flash-preview` |
| Answer-model temperature / maximum tokens | `0.0` / `256` |
| Grader | `openai/gpt-4.1-mini` |
| Grader temperature / maximum tokens | `0.0` / `128` |

## DuckDuckGo defaults

| Setting | Default |
| --- | --- |
| Results per query | `5` |
| Parallel queries | `3` |
| Generated keyword queries | `2` |
| Full-question hit-rate ceiling | `0.3` |
| Keyword-query hit-rate ceiling | `0.3` |
| Overall hit-rate ceiling | `0.3` |
| Prefer `ddgs` | enabled |
| `ddgs` backend | `auto` |
| `ddgs` attempts before legacy transport fallback | `2` |
| Disabled fallback paths | none |
| Shared cooldown | enabled |
| Cooldown failure threshold | `3` |
| Cooldown initial / maximum delay | `60` / `300` seconds |

Normal long-tail rejection is a content decision, not an infrastructure retry. The durable candidate verifier stores the completed decision and full audit.

## Discovery, cache, and concurrency defaults

| Setting | Default |
| --- | --- |
| Page source | MediaWiki table search |
| Search query | `insource:"wikitable"` |
| Table source types | both `infobox` and `wikitable` |
| Page archive | `cache/route3_pages` |
| Reuse cached pages | `all` |
| Fresh-page budget | `fill` |
| Search page size | `50` |
| Maximum search rounds | `10` |
| Processing batch size | `10` |
| Discovery retries | `5` |
| Discovery retry delay / maximum delay | `10` / `60` seconds |
| Page workers | `4` |
| Wikipedia concurrency | `4` |
| DuckDuckGo service concurrency | `4` |
| OpenRouter generation concurrency | `10` |
| Second-stage concurrency | `10` |
| Wikipedia 429 base / maximum / recovery delay | `30` / `300` / `120` seconds |
| Random seed | deterministic run/segment-derived seed when omitted |
| Run date | local current date when omitted; set explicitly for cross-midnight runs |
| Run ID | dated recipe ID when omitted |

`--big-batch-mode`, `--append-to-existing-run`, `--resume`, `--status`, `--compact-output`, and `--compact-rejected-output` default to disabled. Compact-output flags are compatibility surfaces; Route 3 records remain full audit records.

## Fixed Route 3 method internals

| Setting | Fixed value |
| --- | --- |
| Table filter modes | `no_external_links_tables`, `no_horizontal_companion_tables`, `no_picture_heavy_tables`, `no_incomplete_tables`, `not_number_dominant`, `no_social_science_research` |
| Minimum table score | `0.0` |
| Prose-leakage scoring | enabled |
| Low leakage threshold / bonus | `<0.2` / `+0.5` |
| High leakage threshold / penalty | `>0.8` / `-0.5` |
| Minimum total table rows | `3` |
| Maximum table rows passed onward | `40` |
| Maximum selected-table Markdown | `2500` characters |
| Infobox maximum removed-row rate | `0.60` |
| Infobox minimum remaining rows | `5` |
| LLM table choice | disabled |
| Pageview prefilter | disabled |
| REST first-paragraph fallback | disabled |

The Person common-word/common-name rejection heuristic is absent. Place and Date answer-type rules, effective temporal/current guards, selected-table answer support, DuckDuckGo, and second-stage grading remain active. Internal popularity proxies are not formal long-tail filters.

## Durable lifecycle defaults

- Non-dry runs require a clean Git worktree.
- Segment writer lock acquisition is non-blocking and covers manifest read/create through worker and projection completion.
- Service circuits are separate for OpenRouter and DuckDuckGo and use a threshold of three consecutive infrastructure failures.
- Ambiguous OpenRouter calls default to quarantine; `retry` and `abandon` require explicit same-fingerprint resume.
- Attempt001 is primary, attempt002 is the only retry, and attempt003 is invalid.
- All5 slot outcomes are committed atomically in one page attempt.
- A typed slot-level infrastructure failure in attempt001 creates page-level attempt002 eligibility without publishing partial outcomes.
- During attempt002, retry exhaustion rejects only the failing slot and remaining slots continue.
- Unexpected Python or persistence exceptions propagate and leave the attempt uncommitted; they have no rejection default.
- Cached and fresh allocations share the run-group exclusion ledger. Top-up creates a new segment and never modifies an older segment.

## Review defaults

| Setting | Default |
| --- | --- |
| Topic model | `openai/gpt-4.1-mini` |
| Topic temperature | `0.0` |
| Topic maximum tokens | `256` |
| Topic concurrency | `2` |
| Markdown shard size | `50` |
| XLSX worksheet | `review` |
| Delete value | `No` |
| Editable XLSX fields | `delete`, `edited_question`, `edited_reference_answer`, `edit_reason` |

Review export writes `review_state.json`, Markdown shards, `review.xlsx`, durable topic-call records, and `statistics.json`. If any original answer type count is zero, statistics prediction is skipped and the missing types and risk are reported. A deterministic rerun rejection completes the revision as `rejected`; an unexpected exception leaves persisted review state unchanged and the revision pending rerun.

## Finalization defaults

The fixed answer-type proportions are Person `19.8%`, Place `14.6%`, Number `18.5%`, Date `22.2%`, and Other `24.9%`. Rebalancing runs only when all five types remain after canonical-page allocation. If any type is absent, every page-allocated candidate is emitted without rebalancing.

The exact CSV columns are `id`, `problem`, `answer`, `topic`, `answer_type`, and `urls`. `urls` is a JSON array string inside the CSV field.

## Independent evaluation defaults

| Setting | Default or contract |
| --- | --- |
| Prediction input type | CSV only |
| Prediction input glob | `*.csv` |
| Route 3 input identity/question | `id` / `problem` |
| SimpleQA Verified input identity/question | `original_index` / `problem`; identity is normalized to `id` |
| Extra SimpleQA Verified columns | accepted and not used by prediction calls |
| Prediction output | per-input, per-model JSONL |
| Judge input glob | `*.jsonl` |

The audited prediction-model defaults are:

| Model | Default `reasoning.effort` | Model-specific extra settings |
| --- | --- | --- |
| `openai/gpt-5.6-sol` | `max` | — |
| `google/gemini-3.1-pro-preview` | `high` | — |
| `anthropic/claude-sonnet-5` | `max` | — |
| `deepseek/deepseek-v4-pro` | `xhigh` | — |
| `qwen/qwen3.7-max` | not set | — |
| `z-ai/glm-5.2` | `xhigh` | — |
| `moonshotai/kimi-k3` | `max` | — |
| `minimax/minimax-m3` | not set | — |
| `xiaomi/mimo-v2.5-pro` | not set | — |

In automatic mode, rows with an effort send that fixed effort. Rows marked `not set` send `reasoning.enabled=true` without an effort. Claude has no verbosity or other model-specific extra setting. A legal explicit `--reasoning-effort` overrides automatic selection and is sent unchanged, including `max`.

Before any evaluation request, the script resolves every selected model. Unknown models without explicit reasoning configuration terminate the whole batch in one error listing all unresolved model IDs. `--use-provider-reasoning-defaults` is the explicit opt-in for unknown models and omits their reasoning field.

The prediction prompt, model defaults, reasoning settings, request construction, retry/concurrency behavior, judge prompt, grading labels, and unparseable-output behavior are protected and are not cleanup settings.

## Cleanup preservation baseline

Historical Route 1, Route 2, Route 4, and KELM defaults remain intentionally absent. Their code may be deleted only after package initialization and the Route 3 post-generation path are isolated. The extracted Route 3 path must retain the durable lifecycle and review semantics above. After isolation, remove one historical family at a time and rerun the focused matrix in the reconstruction roadmap plus the complete `tests/` suite.
