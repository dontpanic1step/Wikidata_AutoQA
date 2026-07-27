# Current Route 3 Contract

This document summarizes the implemented, non-negotiable method from `AGENTS.md` and `docs/design.md`. `AGENTS.md` has highest authority.

## Formal ownership

- Route 3 is the only formal generation route.
- `scripts/run_wikipedia_infobox_recipe.py` is the only user-facing generation entry point.
- A formal invocation defines one segment with `--page-attempt-count`, `--answer-type`, and `--route3-answer-type-mode`; free-form legacy recipe inputs are not accepted.
- `scripts/run_wikipedia_infobox_pipeline.py` is an internal segment worker.
- Route 1, Route 2, Route 4, KELM, and the old finalization workflow are historical code.
- `scripts/run_openrouter_night_batch.py` is an unused historical orchestrator, not a formal evaluation entry point.
- Historical modules may remain import-time dependencies, but must not be presented, maintained, or invoked as formal generation paths.
- Only legacy rule-based gates explicitly scheduled for removal are excluded. This is not a blanket removal: implemented rule-based gates that were not explicitly removed remain part of the formal pipeline, and removed gates must not be replaced by new heuristics.

## Formal automated order

```text
table/source checks
-> generation
-> parse and normalize
-> effective surface and temporal guards
-> integrated answer-type gate
-> answer-in-selected-table validation
-> DuckDuckGo long-tail filtering
-> second-stage grading
```

Only typed exhausted DuckDuckGo or OpenRouter infrastructure failures may create retry eligibility. Content rejection is terminal; unexpected exceptions keep the segment incomplete and propagate. Durable execution does not reorder the formal method.

## Question and validation contract

- Questions are short, natural, self-contained, fact-seeking, and have exactly one stable intended answer.
- Historically settled temporal anchors are allowed; live-status wording and mutable current-status questions are rejected by effective guards.
- By default, question text must not depend on events in 2025 or later unless configuration explicitly changes the cutoff.
- Temporal questions state the requested precision. Numeric questions state the counted quantity or unit while keeping the reference answer unit-free.
- The answer or an active alias must occur in the selected-table evidence.
- Effective surface and temporal guards remain active when obsolete placeholder fields are removed.
- The integrated answer-type gate remains except for the explicitly removed Person common-word/common-name heuristic.
- Internal popularity proxies are not long-tail gates. DuckDuckGo is the hard first-stage long-tail filter; the configured SimpleQA Verified-style model panel is the second stage.
- Do not use a standalone cheap-model exact-match QA rejection gate.
- LLMs may generate or review candidates but do not invent source facts or prove factual uniqueness.

## Audit contract

Accepted, rejected, and rerun outcomes remain traceable to their source page, selected table, generation exchange, validation results, search evidence, grading evidence, and exact decision reason. Stable IDs, immutable provenance, revisions, ledgers, review sheets, and final CSV fields are required parts of the current implementation.

Temporal audit uses `run_date`, evidence `retrieved_at`, and the effective `cutoff_year` only. The formal CLI, runtime settings, candidate schema, accepted/rejected JSONL, review reconstruction, and segment fingerprint have no `target_time` field. No target-time compatibility path is part of the current contract.

## Durable execution contract

- Formal non-dry runs require a clean Git worktree.
- The generation worker, recipe summary/status, review, and finalization JSON summaries configure stdout as UTF-8 before printing, independently of the inherited Windows console encoding.
- A segment fingerprint fixes the Git SHA, prompt hash, resolved result-affecting configuration, model parameters, answer/source modes, primary allocation target, seed, cache policy, table method, DuckDuckGo settings, and second-stage settings.
- Only an identical fingerprint may resume or reuse a segment. Complete segments reuse; incomplete segments resume; incompatible or legacy incomplete schemas are rejected. Top-ups use new segment IDs.
- The authority order is manifest, immutable page allocations, Wikipedia page archives, external-call records, terminal attempt ledgers, then rebuildable accepted/rejected/summary outputs. State is discovery telemetry only.
- Each unique allocation consumes one primary-page unit. Attempt001 is derived as primary; attempt002 is the sole permitted rerun. Callers cannot label attempts primary or secondary, and attempt003 is invalid.
- An allocated page with no started attempt resumes as attempt001. Interruption never creates retry eligibility. Only a typed exhausted DDG or OpenRouter infrastructure failure may make attempt002 eligible.
- Unexpected Python exceptions preserve traceback, keep the segment incomplete, and propagate instead of becoming reruns.
- Page preparation and deterministic validation have no independent checkpoints and may be recomputed within the same attempt. Attempt002 reuses completed external calls through allocation-scoped stable call keys and matching request hashes.
- All5 slot work has stable keys and commits atomically in one terminal page attempt. A typed slot-level DDG or OpenRouter infrastructure failure during attempt001 makes the page eligible for attempt002 without publishing partial outcomes. During attempt002, exhaustion rejects only the failing slot and processing continues for the other slots. Deterministic candidate failures after slot creation reject only their slot, including persisted-response failures; a persisted-response failure in shared page generation rejects the page. Unexpected Python or persistence exceptions propagate and leave the attempt uncommitted. A terminal attempt stores generation audit, all candidates, DDG and second-stage evidence, outcomes, candidate IDs, and timings.
- Route 3 OpenRouter request intent is persisted before one physical send, then the raw response or explicit HTTP error is persisted immediately. Intent without response is ambiguous and cannot retry without explicit same-fingerprint batch resolution.
- A persisted unparsable model response is a deterministic rejection. Formal OpenRouter transport has no hidden retry, proxy-to-direct switch, endpoint/model fallback, or page state.
- DuckDuckGo persists one completed verifier result per candidate slot. An interrupted verifier reruns that candidate's bounded query set; there are no per-query checkpoints. Existing bounded transport retry, cooldown, endpoint, fallback order, query text, and thresholds remain unchanged.
- OpenRouter and DuckDuckGo each have an invocation-local circuit with a fixed consecutive-failure threshold of three. OpenRouter 401/402 opens immediately; 403 terminates only the current call. An open circuit starts no new calls or allocations, consumes no rerun, performs no fallback switch, and leaves the segment `incomplete` with derived `blocking_reasons`.
- Ambiguous OpenRouter calls default to quarantine. The recipe may batch-resolve them as `retry` or `abandon`; retry records possible duplicate billing and may create only eligible attempt002.
- Worker scheduling is fixed: rebuild index, quarantine ambiguity, resume unfinished attempts, fill missing primary allocations, finish primary work, run eligible attempt002, commit terminal attempts, rebuild projections.
- Top-up requires earlier segments to be complete and protocol-compatible, creates a new segment, and allocates only page IDs never allocated in the run group. It never reads, transfers, clears, or modifies prior segment retry/state artifacts.
- Cache and fresh discovery use the same run-group allocation exclusion set. Accepted, rejected, exhausted, and abandoned page IDs remain consumed.
- Allocation/attempt files are scanned once at startup into an in-memory index; commits update the index under lock. Derived endpoints rebuild only during recovery, batch boundaries, or completion.
- Segment status is either `incomplete` or `complete`, with `blocking_reasons` drawn from `external_service` and `ambiguous`. A segment is complete only when its allocation target is met, all allocations are terminal, no unresolved external call, retry, ambiguity, or circuit block remains, and projection is rebuildable.
- Independently published artifacts use same-directory unique temporary files, close, and `os.replace`. The formal workflow does not add a generic stage hash graph, lock registry, or `fsync` requirement for deterministic local stages; page archive SHA-256 hashes remain in provenance.
- The protected batch prediction and judge tools and the unused night orchestrator do not use the Route 3 durable executor.

## Pre-review prediction contract

- The segment manifest records accepted total, canonical unique pages, multi-QA pages, post-allocation answer-type counts, recipe seed, rebalance `N`, projected answer-type targets, and projected final total.
- Canonical-page allocation is independent of input order and may choose only an answer type present on that page.
- Allocation uses current post-page-dedup type count, then raw pre-review type count, then recipe seed; same-page same-type candidates use lower DuckDuckGo overall hit rate and then candidate ID.
- Quantity prediction must not perform topic selection or deletion.
- Review export writes `statistics.json` with original total, per-type counts, two-decimal percentages, and projected totals.
- If any original answer type has zero rows, review statistics skip prediction and report the missing types and risk.

## Manual review contract

- Review Markdown and XLSX contain latest accepted candidates only.
- GPT-4.1-mini assigns exactly one of the ten fixed topics before export; invalid labels reject the candidate without retry or fallback.
- Topic calls use the durable Route 3 executor, and review state retains request and raw response audits.
- XLSX headers and order are fixed in English; delete defaults to `No`, delete values are `Yes/No`, and topic values use the formal ten-topic enumeration.
- Duplicate or unknown IDs, invalid topics, invalid delete values, and deleted rows with Q/A edits are rejected. Finalization additionally rejects empty topics.
- Question-only, answer-only, and combined Q/A edits are allowed and never change stable identity or immutable generation provenance.
- Deleted rows skip validation. Q/A edits clear old checks and rerun the complete post-generation validation, DuckDuckGo, and second-stage sequence using that candidate's segment fingerprint. A returned rejection is terminal for that revision; an unexpected exception propagates before persisted review state is replaced and leaves the revision pending rerun.
- Answer edits clear active aliases; revision history retains all original and prior values.

## Finalization contract

- Finalization rejects pending edits, reruns, missing or invalid active topics, and any XLSX that is not one-to-one with current active revisions.
- Each canonical page contributes at most one candidate, using the deterministic canonical-page allocation algorithm.
- When all five answer types are present after page allocation, targets use the fixed ratios and exact `N`/`target_i` formulas; final total may differ from `N`. If any type is absent, finalization skips rebalancing and emits every page-allocated candidate.
- Topic diversity removes rows only from over-target answer types, prioritizes the largest eligible global topic, uses the recipe seed for ties, and updates counts after every removal.
- Historical similarity deduplication, subject-URL deduplication, domain round-robin, and `final_selection.py` are not part of formal finalization.
- Final CSV columns are exactly `id`, `problem`, `answer`, `topic`, `answer_type`, and `urls`; `urls` is a JSON array string.
- Candidate identity remains internal through selection. Its visible form is `page{canonical_page_id}_{slot}_{digest}`, while its digest continues to bind the immutable run-group, segment, page, and slot identity.
- Finalization requires a durable public-ID registry. New candidates receive monotonic `simpleqa_synth_000001`-style IDs in deterministic candidate-ID order; existing mappings are immutable, removed IDs are not reused, and final CSV row order follows public-ID sequence.
- The registry is locked for one writer and atomically persisted before the CSV. Related releases must reuse and version the same registry rather than regenerate IDs from page metadata or current row order.

## Candidate artifact contract

- Candidate IDs use only run group ID, segment ID, canonical page ID, and original candidate slot, and render as `page{canonical_page_id}_{slot}_{digest}`.
- Single uses the fixed `single` slot; all5 uses the original answer-type slot; top-up uses a new segment ID.
- Question/answer edits never change IDs or immutable generation provenance.
- Immutable provenance includes run/segment/page attempt, canonical page URL/ID, selected table/type, page archive hash, generation prompt/request/raw response, original Q/A/aliases/search queries, answer type, generation model/parameters, and recipe seed.
- Each revision contains the authoritative Q/A, active aliases/search queries, topic, delete flag, edit reason, source validation, integrated answer-type gate, DuckDuckGo results, second-stage results, and accepted/rejected/rerun status.
- Question-only edits keep the answer, aliases, and search queries.
- Answer edits clear active aliases while preserving old answer/aliases in history.
- Any Q/A edit clears old validation, DuckDuckGo, and second-stage results before rerun.
- Selected-table evidence, answer type, and candidate ID are immutable across revisions.

## Protected evaluation contract

The independent evaluation flow is:

```text
Route 3 final CSV or SimpleQA Verified CSV
-> scripts/run_openrouter_batch_predictions.py
-> model predictions
-> scripts/judge_openrouter_batch_predictions.py
-> SimpleQA Verified-style grading
```

The prediction script accepts CSV only: `id/problem/answer` for Route 3 final output or `original_index/problem/answer` for SimpleQA Verified, with `original_index` normalized to prediction `id` and extra columns accepted. Prediction and judge artifacts remain JSONL. These scripts are retained formal tools, but are not generation, second-stage filtering, manual review, revision, or finalization components. Their prediction prompt/message construction, OpenRouter call settings, `GRADER_TEMPLATE`, grading labels, examples, and default unparseable-output mapping are protected behavior.

Before any prediction request, the script resolves reasoning configuration for the complete selected-model list. Unknown models without an audited default, explicit effort, or explicit provider-default opt-in reject the entire batch and are reported together. Explicit effort values are sent unchanged; reasoning cannot be disabled by this tool.

## Maintenance contract

- Keep `README.md`, `docs/design.md`, `docs/contract.md`, and `docs/default_settings.md` aligned with executable behavior.
- Activate the dedicated Python 3.11 `simpleqa_synth` conda environment for every cleanup and verification command; do not modify the base Python 3.10 environment.
- Before deleting Route 1, Route 2, Route 4, or KELM, narrow `wikidata_simpleqa/__init__.py` and extract the Route 3 post-generation operation from `generation_pipeline.py`.
- The extracted operation must preserve stage order, all5 atomic slot aggregation, typed attempt002 eligibility, attempt002 slot-only exhaustion, explicit deterministic rejection classes, and propagation of unexpected exceptions.
- Recompute the supported import closure after extraction, then remove one historical family per reviewable commit.
- Run the focused Route 3 and protected-evaluation tests after each dependency cut and the complete `tests/` suite before declaring a family removed.
- Preserve the CSV-only prediction input mapping and the JSONL prediction/judge artifact contract.
- Do not add unspecified fallback behavior or defensive programming.
- Stop and report any newly discovered high-risk design flaw.
- Preserve stable artifact formats and completed-run resume semantics unless an explicit design change authorizes migration.
- Preserve unrelated worktree changes and exclude them from commits without explicit authorization.
