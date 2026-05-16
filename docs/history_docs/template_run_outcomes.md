# Template Run Outcomes

## Purpose

This note explains how one template is processed in our generation pipeline, and how to interpret the template-level outcome buckets in later review and planning.

## Per-Template Flow

For a template run, the system does not usually try only one QA candidate.

The rough flow is:

1. Harvest a pool of candidate subjects for the template.
2. Convert each harvested subject into a candidate QA.
3. Validate candidates one by one.
4. Accept the first candidate that passes all validators.
5. If no candidate passes, classify the template based on what happened during the run.

Important implementation detail:

- In our sweep scripts, we usually run each template with `pilot_total=1`.
- That means the goal is to find one accepted QA per template.
- But the template may still examine many candidate subjects before either:
  - finding one accepted QA, or
  - exhausting the harvested pool.

The number of attempts is therefore not fixed at 1.

In practice it is bounded by the harvested candidate pool, which is controlled by settings such as `harvest_limit_per_template`.

For ordinary single-hop harvesters, the returned candidate count is usually capped by:

- `min(settings.harvest_limit_per_template, template.retrieval_limit)`

So if a sweep uses `harvest_limit_per_template=10`, one template may still try up to about 10 candidate QA attempts before it gives up.

The pipeline then validates those candidates in order and stops at the first accepted one.

This means:

- `pilot_total=1` does not mean "one subject tried".
- It means "stop after one accepted QA for that template run".

## What Counts As One Candidate Attempt

One candidate attempt is one subject-level QA candidate that reaches validation.

Example:

- Template: `textbook_author`
- Candidate 1: a novel
- Candidate 2: an audiobook
- Candidate 3: an art book
- Candidate 4: a real textbook

These are four separate candidate attempts for the same template.

If the first three fail and the fourth passes, the template is successful and becomes `proven` if that accepted QA survives the current review bundle.

Candidate attempts are different from template-level outcomes:

- Candidate attempts answer: "How many subject candidates did we test?"
- Template-level outcomes answer: "What happened overall after the run finished?"

## Template-Level Outcomes

### `proven`

Meaning:

- At least one candidate for the template was accepted.
- That accepted QA is still present in the current review bundle after current deterministic filtering and deduplication.

Interpretation:

- The template currently yields at least one usable QA under the present rules.

### `rejected_only`

Meaning:

- The run completed normally.
- The template did produce candidate QAs.
- But every candidate QA was rejected by validators.

Interpretation:

- The template is functioning enough to produce candidates.
- The problem is candidate quality, not pure runtime failure.
- This often means:
  - sparse answer space,
  - bad topic fit,
  - answer leakage,
  - duplicate subject collision,
  - missing English labels,
  - or other deterministic validation failures.

In our current planning convention:

- `rejected_only` templates under `target_time=2026` are often reserved for later `2025` reruns, especially when we think the template may work better with older data.

### `unproven_no_result`

Meaning:

- The run completed normally.
- No accepted QA was produced.
- No stable rejected-candidate outcome was recorded for the template in that run.
- The template effectively ended with `no_result`.

Interpretation:

- The pipeline finished, but nothing usable surfaced.
- This usually points to one of:
  - empty or overly sparse 2026 data for that template,
  - harvesting/query coverage problems,
  - unsupported executor paths,
  - or a template that currently does not reach viable candidates.

This is different from `rejected_only`:

- `rejected_only` means candidates existed and were rejected.
- `unproven_no_result` means the run finished without yielding a real candidate stream that could produce an accepted result.

### `error`

Meaning:

- The run did not finish cleanly for that template.
- A runtime failure interrupted the attempt.

Typical causes:

- WDQS timeout
- HTTP 429 / rate limiting
- request failure
- parsing or data-format bug
- other uncaught runtime exception

Interpretation:

- We do not yet have a trustworthy template outcome.
- The first thing to fix is the execution/query/runtime problem, not the template classification itself.

## Simple Decision Rule

When reading a template outcome:

- `proven`: the template currently works.
- `rejected_only`: the template produces candidates, but all are bad under current rules.
- `unproven_no_result`: the template run finishes, but nothing usable appears.
- `error`: the run breaks before we can trust the template outcome.

## Your Mental Model

The simplest correct way to think about one template run is:

1. The harvester tries to assemble a small candidate pool.
2. The pipeline validates candidate QAs one by one.
3. If one candidate passes, the template can become `proven`.
4. If candidates existed but every one failed validation, the template is `rejected_only`.
5. If the run finished but no usable candidate stream ever formed, the template is `unproven_no_result`.
6. If the run crashed or a request/runtime failure interrupted it, the template is `error`.

So your summary is essentially correct:

- if some runtime failure happens, it is `error`;
- if the run finishes and nothing usable returns, it is `unproven_no_result`;
- if candidate QAs are generated but all are rejected by validators, it is `rejected_only`.

The only nuance is that "tries several times" means "tries several candidate subjects", not "retries the same accepted QA idea".

## Why Candidate Counts Can Be Large

A single `rejected_only` template may have many rejected candidates.

That is normal because:

- one template can inspect many subject candidates in one run,
- we may rerun the same template multiple times,
- and each distinct subject candidate is recorded separately.

So:

- template-level status counts how many templates ended in each bucket,
- candidate-level rejection files count how many candidate attempts failed and why.

## Current Sweep Convention

For current Stage 5B work:

- We use `target_time=2026` to test whether a template can produce a valid modern QA.
- If a template is `rejected_only` at `2026`, we may reserve it for later `2025` reruns rather than dropping it immediately.
- If a template is `unproven_no_result`, we usually treat it as a stronger sign of harvesting/executor/coverage weakness at `2026`.
- If a template is `error`, we treat it as unresolved infrastructure or query failure.

## Focused Executor Reruns

We also use focused reruns after implementing new executor paths.

Example:

- On `2026-05-08`, we reran the newly executor-backed templates at `target_time=2026` with `pilot_total=1` per template.
- This kind of rerun is narrower than the full unproven sweep.
- Its purpose is to answer a specific question:
  - did the template move from "missing executor" to a real candidate search path?

In this workflow, the most important distinction is:

- if the rerun now produces accepted or rejected candidates, the executor gap is likely fixed;
- if it still ends in `no_result`, the remaining issue is probably query coverage, 2026 sparsity, or an overly strict uniqueness pattern;
- if it ends in `error`, the executor exists but the query/runtime path is still unstable.

### 2026-05-08 Focused Rerun Snapshot

- Templates rerun: `18`
- Accepted: `4`
- Rejected only: `0`
- No result: `12`
- Error: `2`

Accepted in that focused rerun:

- `tv_series_source_work_author`
- `terminal_operator_country`
- `ordinal_tournament_host_city`
- `ordinal_film_in_series_director`

Important interpretation:

- These acceptances mean the new executor path is real and can surface at least one viable 2026 candidate under current validators.
- The remaining `no_result` templates in that focused rerun should not automatically be treated as "still missing executor".
- Some of them executed real cached SPARQL requests and simply returned no viable candidate stream in the 2026 window.

### Problems To Record From That Rerun

The focused rerun surfaced three useful problem classes:

1. Executor fixed, but 2026 still looks empty.
   - Examples: `marriage_spouse`, `religious_leader_successor`, `guideline_author_count`, `story_collection_story_count`, `spacecraft_crew_count`, `spacecraft_payload_count`, `rover_wheel_count`, `patent_inventor_count`, `bridge_span_count`, `medicine_ingredient_count`, `project_partner_count`, `company_that_developed_benchmark_founder`.
   - Interpretation: the pipeline completed and touched real query artifacts, but no accepted candidate emerged.

2. Executor fixed, but the template may still be conceptually weak under our conservative rules.
   - Example: `marriage_spouse`.
   - Interpretation: even when the query path exists, the template may remain a poor fit for time-invariant QA because the target relation is mutable.

3. Executor fixed, but the query path is still runtime-fragile.
   - Examples: `company_that_released_product_founder`, `ordinal_volume_author`.
   - Observed error on `2026-05-08`: `URLError` with `Remote end closed connection without response`.
   - Interpretation: this is not a missing-executor problem anymore; it is a request/query stability problem.

### Reading Cached Reruns Correctly

One subtle but important detail:

- a focused rerun may complete mostly from cache;
- in that case, `network_requests` can be `0` even though the template really executed query logic;
- the presence of cached request events or nonzero total request counts still means the template followed a real implemented path.

So when classifying `no_result` templates after a cached rerun:

- do not equate `network_requests=0` with "not implemented";
- check whether the telemetry still shows actual cached request events or nonzero total request counts.

## Later Catalog Decisions

Two follow-up review decisions matter for interpreting older run artifacts:

1. `marriage_spouse` remained weak because it asks for broad spouse identity rather than one historically settled relationship slot.
   - Important implication: the executor problem and the invariance problem are different. A generic spouse query is still risky, but an ordinal spouse query may become admissible if it is backed by dated relationship-history provenance.

2. `company_industry` was retired instead of being kept with the surface question `What industry is the company {descriptor} in?`
   - Reason: broad industry labels such as `software industry` were judged too underspecified for a conservative single gold answer. Nearby alternatives like `information technology` can also feel acceptable to a human reviewer.
   - Important implication: older accepted examples for this domain should not be treated as current proof that the template still belongs in the catalog.

## Records To Check

When debugging a template outcome, the main records are:

- `outputs/review_2026_all_generated_qas.tsv`
- `outputs/template_status_index.json`
- the relevant accepted/rejected JSONL files
- the relevant rerun summary JSON files

These together tell us:

- whether the template currently has a surviving accepted QA,
- whether it ended in `rejected_only`, `unproven_no_result`, or `error`,
- and what candidate-level reasons caused the failure.

## 2026-05-09 Heavy Query Refinement Lessons

This pass focused on three templates that were still blocked after executor work:

- `ordinal_country_prime_minister`
- `footballer_goals_in_ordinal_tournament`
- `acquisition_purchase_price`

### Outcome Snapshot

- `ordinal_country_prime_minister` is still in `error`.
- `footballer_goals_in_ordinal_tournament` moved from `error` to `no_result`.
- `acquisition_purchase_price` moved from `error` to `no_result`.

The canonical status rebuild after this pass shows:

- `error`: `26`
- `proven`: `64`
- `rejected_only`: `22`
- `unproven_no_result`: `78`

### Problems We Learned To Distinguish

1. Monolithic heavy query.
   - Symptom: one broad WDQS query fails immediately with `HTTP 429` or timeout.
   - Better response: split the query into reusable stages, usually seed discovery first and detail lookup second.

2. Later chunk failure after early progress.
   - Symptom: the first chunk returns usable rows, but a later chunk fails under WDQS throttling.
   - Better response: keep partial results, record the chunk failure, and avoid treating the whole template as "missing logic."

3. Redundant support probing after a known heavy-query failure.
   - Symptom: the real executor path already recorded rate-limit problems, then the generic probe fires and adds another unrelated `HTTP 429`.
   - Better response: skip the support probe once a domain already has a recorded heavy-query failure.

### Template-Specific Lessons

#### `ordinal_country_prime_minister`

- The office-pair seed query is no longer the main problem.
- Chunking the recent office-holder expansion helped: early chunks can succeed and expose a viable subject-office pair.
- The remaining blocker is the office-history lookup itself, even when it is narrowed to a single office.

Interpretation:

- The current `P39` family is now structurally better instrumented.
- The next real improvement would likely need a different history source or a stronger cache hit, not just another small SPARQL rearrangement.

#### `footballer_goals_in_ordinal_tournament`

- Time-windowing the edition seed query reduced conceptual breadth, but every monthly window still hit WDQS throttling.
- The refinement is still useful because it converts the result into an auditable `no_result` with explicit seed-failure problems instead of a bare executor error.

Interpretation:

- When every small window still returns `HTTP 429`, the bottleneck is no longer just query complexity.
- At that point, more slicing may not be worth the extra request count.

#### `acquisition_purchase_price`

- Monthly statement-seed queries behaved similarly to the footballer template: cleaner logic, but still throttled in every window.
- The new path again gives us explicit problem records and a graceful `no_result` outcome.

Interpretation:

- A lighter seed query is worth doing when it helps us separate "bad executor" from "blocked external service."
- But if every month-window query still fails, further decomposition may add little value.

### General Refinement Heuristics For Future Templates

1. First remove unnecessary joins, labels, and anti-joins from the seed query.
2. Prefer a two-stage executor over a single all-in-one SPARQL query.
3. If the second stage is the bottleneck, chunk it and preserve partial results.
4. If all small windows still fail with the same rate-limit error, stop slicing further and record that WDQS throttling is now the dominant blocker.
5. Once a heavy-query failure is already recorded for the domain, do not fire a generic support probe that will only create more noise.

## 2026-05-11 Rejected-Only Retry And Label Filtering Notes

This pass retried the rejected-only templates whose current reasons included either:

- `canonical_question_failed_validation`
- `duplicate_subject_resource`

The focused domains were:

- `product_manufacturer`
- `event_venue`
- `dataset_creator_math`
- `dataset_creator_ai`
- `taxonomy_database_creator`
- `medical_school_country`
- `textbook_publisher`
- `new_nature_reserve_country`

### Live Retry Outcome

The rerun did not reach a meaningful candidate-level conclusion for any of those templates.
All eight hit request-layer `URLError` failures during the first live query or final staged-seed
window, so the retry did not tell us whether the newer search-next behavior would rescue them.

Interpretation:

- The retry was still worth doing because it separated "search-next may help" from "the network
  never let the template finish."
- Right now those domains should not be treated as clean rejected-only evidence for or against the
  search-next mechanism.

### What Changed In Code

1. Added optional English-subject-label query constraints for templates with repeated
   `no_english_label` failures.
2. Added `ordinal_tournament_host_country` as a reusable ordinal tournament variant, because
   year-bearing tournament-edition labels can often be normalized safely through the existing
   ordinal-series executor family.

### Lessons

1. Requiring an English subject label in the query does not increase raw recall; it increases the
   share of usable candidates inside a fixed harvest budget.
2. This filter is a good fit when the dominant failure is blank English subject labels, especially
   for direct single-fact templates.
3. Ordinal replacement is only safe when the underlying subject is a real edition/series member.
   It should not be applied mechanically to all year-bearing event templates.
