# Current Route 3 Design

This document describes the supported design implemented on the current branch. `AGENTS.md` remains the highest-level instruction. The branch roadmap under `docs/reconstruction/` records present import dependencies that may be removed later without redefining this method.

## Formal method

Route 3 is the only formal generation route.

- User entry point: `scripts/run_wikipedia_infobox_recipe.py`.
- Internal segment worker: `scripts/run_wikipedia_infobox_pipeline.py`.
- The worker is invoked by the recipe and is not a second user-facing workflow.
- The recipe owns resolved configuration, segment execution, and run-level artifacts.
- Pilot output is candidate generation for audit and manual review, not final verified data.

The formal automated order is:

```text
table/source checks
-> generation
-> parse and normalize
-> effective surface and temporal checks
-> integrated answer-type gate
-> answer-in-selected-table validation
-> DuckDuckGo long-tail filtering
-> second-stage grading
```

Only typed DuckDuckGo or OpenRouter infrastructure failures may make a page eligible for `attempt002`. Content rejection is terminal, and an unexpected Python exception leaves the segment incomplete and propagates to the recipe. Durable execution, review, and finalization do not change the formal stage order.

The automated flow preserves candidates that share a subject resource or exact question. Page-level deduplication happens only during finalization after manual review.

## Formal boundaries

The following are historical code, not formal generation methods:

- Route 1, Route 2, and Route 4 generation;
- KELM generation or rewriting;
- the old finalization, standalone rule gate, final LLM judge, similarity deduplication, subject-URL deduplication, and domain round-robin workflows.
- the unused `scripts/run_openrouter_night_batch.py` evaluation orchestrator.

Historical modules still remain in the repository and some remain in Route 3's import closure. Their presence does not make them supported methods. Removal work must preserve the supported Route 3 and protected evaluation surfaces documented here.

Formal Route 3 validation keeps effective surface and temporal checks, selected-table provenance, answer-in-evidence validation, DuckDuckGo filtering, and second-stage grading. Person answers have no local rule-based rejection heuristic. Do not add replacement heuristics.

## Formal configuration surface

The supported recipe surface includes primary page-attempt count; answer type and single/all5 mode; infobox/wikitable/both source mode; generation model and maximum tokens; cache reuse and fresh-page budgets; run identity and seed; lifecycle controls; output paths; and bounded concurrency/network parameters. The exact current defaults are listed in `docs/default_settings.md`.

The formal segment selectors are `--page-attempt-count`, `--answer-type`, and `--route3-answer-type-mode`. The legacy free-form recipe and per-answer-type input syntaxes are not supported.

Specific answer types use single mode. `AllTypes` uses all5 mode. The page-attempt count is a unique allocation target, not an accepted-question target. Eligible attempt002 work does not consume another allocation.

Table filters, prose-leakage scoring, and minimum table score remain fixed at their current formal values. They are method internals, not user switches. Other legacy CLI surfaces are catalogued in `docs/compatibility_legacy_settings.md`.

## Durable segment execution

Formal non-dry runs require a clean Git worktree. Before reading or creating a segment manifest, the recipe acquires a non-blocking OS-held exclusive writer lock for that segment and holds it through worker execution and projection. The OS releases the lock when the recipe exits or is killed; durable artifacts remain responsible for crash recovery. Each segment owns a `segment_manifest.json` whose fingerprint covers the Git SHA, generation prompt hash, resolved result-affecting configuration, model parameters, answer and source modes, primary page budget, seed, cache policy, table ranking and filters, DuckDuckGo settings, and second-stage settings. A complete segment with the same fingerprint is reused; an incomplete segment with the same fingerprint resumes. A different fingerprint requires a new run or an explicit compatible top-up segment. Incomplete legacy schemas are rejected rather than migrated. Manifest status is either `incomplete` or `complete`; the derived `blocking_reasons` set records `external_service` and/or `ambiguous` without inventing allocations or retries.

The authoritative hierarchy is:

```text
segment manifest
-> immutable page allocations
-> external-call records and page attempts
-> terminal page-attempt ledger
-> rebuildable accepted/rejected/summary artifacts
```

An allocation identifies one canonical page in one segment and consumes one primary-page budget unit. Attempt identity is derived from allocation history: `attempt001` is the primary execution and `attempt002` is the only allowed page-level rerun. A committed allocation with no attempt remains pending primary work after interruption. State files cannot allocate, release, retry, or reinterpret pages.

The durable boundaries are the allocation record, Wikipedia page archive, external-call records, terminal page-attempt ledger, and derived projections. Page preparation and deterministic validation are safe to recompute within the same attempt and have no independent checkpoints. All5 uses stable answer-type slot keys and commits all terminal slot outcomes atomically in one page attempt. Attempt002 reuses matching external-call results by stable logical call key and request hash. Each independently published artifact uses a same-directory unique temporary file followed by close and `os.replace`; local stages do not form a generic hash graph or lock registry.

Route 3 OpenRouter calls use a thin one-request transport under a durable executor. The executor persists request intent before sending and persists the raw response or explicit HTTP error immediately after return. A persisted response is reused. Intent without a persisted response is `ambiguous_external_call` and is never retried without explicit batch resolution. An unparsable persisted model response is a deterministic rejection. The transport owns no prompt, parsing, retry, proxy switching, fallback, checkpoint, circuit, or page state. These rules apply to Gemini 3 Flash generation, second-stage answer calls, and GPT-4.1-mini grading; the protected batch prediction and judge scripts do not use this executor.

DuckDuckGo persists one completed verifier result per candidate slot, including the final decision, complete queries, results, and request audit. A completed candidate result is reused after resume; interruption during a verifier reruns only that candidate's bounded query set. There are no per-query checkpoints. Existing bounded DDG retry, cooldown, endpoint, fallback order, query text, and thresholds remain unchanged, and normal long-tail rejection is not an infrastructure failure.

The worker has two service circuits, `openrouter` and `duckduckgo`, with a fixed threshold of three consecutive infrastructure failures. OpenRouter 401/402 opens its circuit immediately; 403 is a definite non-retryable failure for that call but does not immediately open the global circuit. A successful service operation resets that service's counter. An open circuit starts no new service calls or page allocations, does not consume a rerun, and leaves waiting attempts pending. The segment remains `incomplete` and records `external_service` and/or `ambiguous` in `blocking_reasons`; no model, endpoint, proxy, or fallback is substituted. Circuits do not auto-close within an invocation, and a user-initiated same-fingerprint resume starts new invocation-local counters.

Ambiguous OpenRouter calls are quarantined by default while healthy pages may continue if the circuit remains closed. The recipe is the only resolution entry point: batch `retry` may create `attempt002` for eligible calls and records possible duplicate billing, while `abandon` commits an `abandoned_ambiguous` terminal outcome. Attempt002 cannot create attempt003. Resolution is allowed only on same-fingerprint resume and is recorded in audit without changing the fingerprint.

The fixed scheduling order is:

```text
rebuild ledger index
-> quarantine unresolved ambiguity
-> resume unfinished attempts
-> fill missing primary allocations
-> complete the primary phase
-> run eligible attempt002 work
-> commit terminal attempts
-> rebuild projections
```

Initial runs create a new run group and segment. Resume continues the same allocations and attempts. Rerun means `attempt002` of the same allocation, never a generic rerun-pool mode. Top-up requires all earlier segments to be complete, creates a new compatible segment, and allocates only page IDs never allocated anywhere in the run group. Top-up does not read, transfer, clear, or modify old segment state or attempts. Rejected, exhausted, abandoned, and accepted pages remain consumed allocations.

The worker scans allocation and attempt files once at startup into a segment ledger index. Commits update that index under lock. Accepted/rejected/summary outputs are rebuilt at recovery, batch boundaries, and segment completion rather than after every page. A segment is complete only when its allocation target is met, every allocation has a terminal outcome, no checkpoint or eligible retry remains, no ambiguous or circuit-blocked work remains, and projection rebuild succeeds.

## Pre-review quantity prediction

After automated acceptance, the segment manifest records accepted count, canonical unique pages, multi-QA pages, answer-type counts after canonical-page allocation, recipe seed, rebalance `N`, projected per-type targets, and projected final total. Single-QA pages count directly. Multi-QA pages are processed by canonical page ID; allocation minimizes the current post-page-dedup type count, then the pre-review raw type count, then uses the recipe seed among tied available types. Multiple candidates of the chosen type on one page are ordered by lower DuckDuckGo overall hit rate and then candidate ID.

This stage predicts quantities only. It does not inspect, select, or delete topics.

## Manual review loop

Before review artifacts are written, GPT-4.1-mini classifies each accepted question and reference answer into exactly one formal review topic. The request uses temperature `0`, `max_tokens=256`, and a fixed prompt that requires one exact label from the ten-topic enumeration. The calls run with bounded concurrency through the durable Route 3 OpenRouter executor. Review state retains the request, the complete raw OpenRouter response, the returned text, and the parsed topic; the durable response record also retains the exact HTTP body. An assistant response that is not exactly one allowed label rejects that candidate from review without retry or fallback. Generation-stage content labels are never used as review topics.

Each run exports accepted candidates only to Markdown shards of at most 50 candidates and one XLSX with the exact English columns `id`, `question`, `reference_answer`, `wikipedia_url`, `topic`, `human_edited`, `delete`, `edited_question`, `edited_reference_answer`, and `edit_reason`. Each shard suffix records its actual inclusive candidate range, so 68 candidates produce `_1-50.md` and `_51-68.md`. Markdown includes stable identity, authoritative Q/A, answer type, canonical Wikipedia page, selected-table Markdown, the automatic topic, and the automatic human-edit indicator. Each small-model answer and judge reason is rendered in its own labeled blockquote so response Markdown cannot merge with the surrounding review structure. The workbook displays the automatic topic without a dropdown and rejects topic edits. `human_edited` is computed from Q/A revision history, defaults to `No`, becomes `Yes` after a human Q/A edit, and is also read-only. Only `delete` uses a `Yes/No` dropdown.

The review export also writes `statistics.json` beside the XLSX with the original pre-human-review total, per-answer-type counts and two-decimal percentages, and projected final total and per-type counts. If any original answer type has zero QAs, prediction is skipped and the artifact records the missing types and risk.

Review state maps every candidate to its stable artifact and current full processing record, maps each segment identity to its own fingerprint, and stores the topic-classification audit for every classified revision. Top-up candidates therefore rerun with their own segment configuration. A deletion appends a rejected revision and skips validation. A Q/A edit appends a rerun revision, preserves immutable generation provenance and stable ID, applies the artifact alias rules, clears the old topic and checks, and reruns all post-generation checks, DuckDuckGo, second-stage grading, and topic classification. Revision DDG results and OpenRouter calls include the revision number in their stable keys, so changed requests cannot collide with the original candidate or an earlier revision. Each new Markdown/XLSX contains only latest accepted revisions.

## Formal finalization

Finalization requires no unprocessed Q/A edits, no rerun revisions, valid topics on every active row, and an exact XLSX-to-current-revision ID and value match. It reuses canonical-page allocation to select at most one candidate per page. When all five answer types are present, it computes `N = min(ceil(n_i / p_i))` and `target_i = min(n_i, ceil(N * p_i))`; if at least one type is absent, it skips answer-type rebalancing and outputs every page-allocated candidate.

Excess answer-type rows are removed globally and iteratively. Only over-target types are eligible; candidates in the currently largest eligible global topic are removed first, and seed-based selection resolves ties after stable ID ordering. Topic totals update after each removal. The method does not fit answer-type by topic cells and does not invoke historical similarity, subject-URL, or domain-round-robin selection.

The final CSV columns are exactly `id`, `problem`, `answer`, `topic`, `answer_type`, and `urls`, with `urls` encoded as a JSON array string.

## Candidate artifact schema

Each formal candidate has one stable ID derived only from:

```text
run_group_id
+ segment_id
+ canonical_page_id
+ original_candidate_slot
```

Single mode uses the fixed `single` slot. All5 mode uses the original answer-type slot. Top-up work uses a new segment ID. Human edits never change the candidate ID.

The artifact keeps immutable run/segment/page-attempt data, canonical page and selected-table evidence, page archive hash, generation prompt/request/raw response, original Q/A/aliases/search queries, answer type, model parameters, and recipe seed.

An append-only revision stores the authoritative question and reference answer, active aliases and search queries, topic, delete flag, edit reason, source validation, integrated answer-type gate, DuckDuckGo evidence, second-stage evidence, and accepted/rejected/rerun status.

Question-only edits retain the answer, aliases, and search queries. An answer edit clears active aliases. Any Q/A edit clears active validation, DuckDuckGo, and second-stage results and moves the revision to rerun. Original values remain in immutable provenance and revision history; selected-table evidence, answer type, and candidate ID do not change.

The schema implementation is `src/wikidata_simpleqa/route3_artifacts.py`.

## Protected evaluation tools

The following scripts are retained, independent SimpleQA Verified-style evaluation tools:

- `scripts/run_openrouter_batch_predictions.py`
- `scripts/judge_openrouter_batch_predictions.py`

Their flow is separate from generation:

```text
final CSV or evaluation input
-> run_openrouter_batch_predictions.py
-> model predictions
-> judge_openrouter_batch_predictions.py
-> SimpleQA Verified-style grading
```

Generation, manual review, revision, and finalization must not call these scripts. Their prediction prompt/message construction, `GRADER_TEMPLATE`, grading labels, examples, and default handling of unparseable grader output are protected behavior.

## Maintenance boundary

Future cleanup may delete historical Route 1, Route 2, Route 4, KELM, old finalization, and experimental code only after the current import closure is isolated. Cleanup must preserve the entry points, artifact schemas, prompts, lifecycle rules, review behavior, final CSV contract, and protected evaluation tools described above.
