# Design 5-13-restored

This document defines the current design for branch `5-13-restored`.

It restores the intended `5-13` work after the incident on `5-13-after-incident`, while keeping the same high-level project goal:

- generate conservative, auditable, SimpleQA-style short factual questions
- keep the multi-generator architecture
- keep shared LLM rewriting
- keep shared long-tail filtering

The main strategic change is that **Route 1 returns to template-led generation inside the shared multi-generator pipeline**.

The validated restoration walkthrough is recorded in `docs/walkthroughs/product_manufacturer_walkthrough_5_13_restored.md`.

## 1. Goals

The branch should optimize for:

- short, natural, fact-seeking questions in the style of SimpleQA / SimpleQA Verified
- exactly one intended gold answer
- high auditability
- conservative acceptance
- route extensibility without forcing all routes into one Wikidata-specific validator stack

The project target remains the question style and evaluation setting, not loyalty to one retrieval source.

## 2. What Stays the Same from 5-12

The following design choices remain:

- multiple generators can feed a shared downstream pipeline
- the pipeline still has a shared LLM rewrite step
- the pipeline still has shared long-tail filtering
- the rewrite step should still ask the LLM for both:
  - the final rewritten question
  - query strings for long-tail verification
- outputs must stay metadata-rich and auditable
- the system should continue to prefer conservative deterministic validation for factuality and uniqueness

This branch is therefore not a rollback to the older monolithic template-only architecture. It is a **route reset for Route 1 inside the newer shared-pipeline design**.

## 3. Main Changes on 5-13-restored

### 3.1 Route 1 is template-led again

Route 1 should again generate candidate questions from templates.

Intended meaning:

- candidate harvesting and canonical question construction are controlled by structured templates
- templates should encode the fact type and expected wording frame
- the LLM does not invent the question from scratch for Route 1
- instead, the LLM rewrites a template-derived candidate into more natural SimpleQA-style wording

This change is specific to Route 1. Other routes may use different candidate construction methods.

### 3.2 Temporal policy is relaxed compared with older strict designs

Questions may include:

- years
- dates
- historically settled temporal anchors

Questions should still reject:

- `current`
- `currently`
- `latest`
- `most recent`
- `as of now`
- other live-status phrasing

Default conservative rule:

- do not allow question text that depends on `2025` or later

Important clarification:

- entities from any time period are allowed
- old entities are allowed
- newer entities are allowed if the final question does not depend on a temporal anchor in `2025` or later
- the restriction is about the question's dependency, not about the entity's existence date alone

### 3.3 Validators are decoupled and route-specific

The branch should stop treating the current validator stack as universally applicable.

Instead, the design should separate:

- shared pipeline interfaces
- route-specific validators
- reusable validator modules

For Route 1 and similar Wikidata-backed routes, the following validators remain appropriate:

- Wikidata grounding
- Wikidata-based disambiguation
- time-invariance checks
- deduplication

These validators should be implemented as **Wikidata-route validators**, not as assumptions for every future route.

For non-Wikidata routes, corresponding validators must be designed separately according to:

- source format
- grounding assumptions
- ambiguity patterns
- temporal failure modes
- deduplication needs

This design keeps reuse where it is valid without overfitting the entire framework to one source family.

### 3.4 Shared rewrite step remains, but route inputs may differ

The branch should keep the current design where one LLM call returns both:

- the rewritten question
- query strings for downstream long-tail filtering

However, the material shown to the LLM can vary by route.

For example:

- Route 1 may provide a template-derived canonical question plus structured source metadata
- a KELM-like route may provide a source sentence, triple, and grounded metadata
- a future semi-structured route may provide table fields or infobox values

Shared contract:

```json
{
  "rewritten_question": "string",
  "search_queries": ["string"],
  "answer_aliases": ["string"],
  "discard_reason": null
}
```

Route-specific prompt inputs are allowed as long as the output contract stays shared.

All route rewrite prompts must make answer normalization explicit. If the answer is temporal, the question should specify the requested precision or unit, such as `what year`, `what month`, `what day`, or `how many months`. If the answer is a full calendar date, the prompt should prefer wording like `what day, month, and year ...`. If the answer is numeric, the question must state the counted quantity or unit, while the reference answer and answer aliases should remain unit-free normalized values.

### 3.5 Long-tail filtering changes

The old first-stage long-tail filter based on internal popularity proxies should be removed.

Delete as long-tail gates:

- sitelink-count thresholds
- claim-count thresholds
- similar internal index-based popularity filters

New long-tail and difficulty filtering:

1. DuckDuckGo search-based filtering
2. optional SimpleQA Verified-style model grading/difficulty review

Design intent:

- search checks whether the answer is exposed too directly in public retrieval
- model grading checks whether configured answer models solve the question too reliably

There is no standalone cheap-model exact-match QA rejection gate. SimpleQA Verified uses autorated model answers for difficulty/evaluation rather than a separate cheap-model long-tail rejection phase, so model-answer judgment belongs in the grading panel.

DuckDuckGo filtering uses normalized answer matching over answer labels and aliases. It normalizes case, punctuation, common number forms, common date forms, and common country aliases where applicable. Search-result title hits and snippet hits are thresholded evidence signals, not unconditional rejection rules; setting thresholds to `1.0` intentionally lets candidates pass stage 1 for walkthrough/debug runs.

For `Number` templates, normalize the answer during candidate construction for future comparison and SimpleQA Verified-style margin generation. Compute the reference margin before DuckDuckGo filtering. For number answers outside the exact-integer `[-10, 30]` bucket, DuckDuckGo leakage matching extracts Arabic-number and English-number mentions from titles/snippets, normalizes them, and counts them as answer exposure when they fall inside the acceptable range. Exact integers in `[-10, 30]` keep the existing string/word matching plus optional snippet-judge rule instead of using margin matching. For `Date` answers, normalize common full-date, month-year, and year-only forms before first-stage matching.

Both stages must remain auditable:

- store query strings
- store top-result evidence where possible
- store model name and response metadata
- store the exact rule that caused acceptance or rejection

### 3.6 Reuse 5-12 validators where applicable

This branch should reuse the existing validator work from `5-12` whenever those modules still match the new architecture.

Priority reuse areas:

- disambiguation
- deduplication

More generally:

- if a validator from `5-12` is already cleanly reusable for a Wikidata-backed route, keep it
- only redesign validators where the old assumptions no longer match the new route boundary

### 3.7 Route 3: Wikipedia infobox and table generation

Route 3 is a Wikipedia-only route for semi-structured public data. It starts from directly supplied English Wikipedia URLs, fetches the page through the MediaWiki API, extracts the page title, first paragraph, and structured infobox/table content, then asks a small model to propose one composition-style question per URL.

Intended Route 3 question types are max/min/sum/ordinal questions over structured rows, for example asking which venue in an event table has the largest capacity. The route may use first-paragraph aliases to avoid unsuitable temporal wording, such as asking about the `23rd FIFA World Cup` instead of using the page title `2026 FIFA World Cup`.

Route 3 may emit complete list answers when a composition operation has a tie. The display `answer` remains a string for shared JSONL compatibility, while `source_metadata.answer_items` stores the individual answer elements. For these list answers, search leakage is counted only when every answer element appears in the same result title or snippet, and SimpleQA-style grading treats partial lists as incorrect.

Before prompting the model, Route 3 ranks extracted tables. Prefer article tables over infoboxes, tables with multiple structured rows, headers that expose comparable values such as capacity/rank/count/date/votes, and row values that are not repeated in non-table prose. Penalize short infobox-style summaries, oversized prose-like tables, placeholder/mutable tables such as live standings, and tables whose row values are already easy to recover from article text. Pass only the top three ranked tables to the small model so it focuses on the most useful evidence. Store the ranking criteria and scores as metadata so table choice can be audited.

The Route 3 small-model prompt emits `answer_type` as `Entity`, `Number`, or `Date`, and follows the shared answer-normalization wording rule: temporal questions must name the requested precision, full-date answers should be requested as day, month, and year, and numeric questions must put the unit or counted quantity in the question rather than in the reference answer. The prompt passes `subject_anchors` as page/table scope hints rather than required wording. These hints include the page title, title-derived aliases, and the selected tables' captions and nearby section headings. Safe first-paragraph aliases are passed separately as `safe_subject_aliases`; when the page title contains a cutoff-year marker, the model should use one of those aliases if it needs to name the subject. The model should use the scope hints to understand scope, for example that `15 largest commercial banks` supports asking which bank is largest within that table but not how many banks exist in Ukraine.

Route 3 and shared rewriting prompts should avoid generic provenance phrasing such as `according to the table` or `according to the [source] table`, and Route 3 specifically should avoid `in the List of ...` wording. The question should name the actual subject, event, chart, list, or scope naturally. `According to ...` wording is preferred only for well-known named charts or lists such as Billboard charts or UNESCO lists. This is prompt guidance; the shared surface guard does not reject the wording directly.

Route 3 URL discovery should be a separate, auditable step. It should not default to hand-prepared URLs, because those bias pilots toward short-tail facts. The preferred discovery path reads raw pages-articles XML slices extracted to JSONL while preserving wikitext table and infobox markup, scores candidate pages inside the Domain Axis from `docs/template_catalog_review.md` plus `History`, then opens and grades a bounded number of candidates with the same parsed-table quality scorer used by Route 3. WikiExtractor-style plain-text extraction is not suitable for this route because it flattens away the table structures needed for source discovery. A cached Wikimedia title dump or bounded MediaWiki search can supplement sparse subdomains, but final URL choice must still come from table-quality grading.

For sparse pilot slices, discovery may evaluate more than one subdomain per broad domain and then keep only the best-scoring subdomain plus the top URLs for that domain. This preserves the "one subdomain per domain" pilot shape while avoiding a brittle dependency on whichever subdomain appears first in the catalog plan. The URL file preserves `domain<TAB>subdomain<TAB>url` rows so accepted examples can report both source URL and source domain. Later runs may scale the seed target, subject to the project's network-use constraints.

Route 3 does not perform factual validation or uniqueness proof. Its conservative contract is auditability: accepted and rejected outputs must store the source URL, canonical page title, first paragraph, parsed table metadata, model derivation summary, generated search queries, downstream DuckDuckGo evidence, optional grading evidence, and phase timings. Because the route has no Wikidata grounding, shared processing must not require a Wikidata `source_candidate` for Route 3 candidates.

## 4. Recommended Architecture

The branch should organize the system into the following conceptual layers:

```text
generator route
  -> route-local candidate record
  -> route-local validator bundle
  -> shared rewrite contract
  -> shared long-tail filter contract
  -> shared acceptance / rejection recording
  -> shared output schema
```

### 4.1 Generator layer

Each route is responsible for:

- candidate harvesting
- source-specific normalization
- source-specific metadata collection
- initial canonical question construction when the route uses templates

For Route 1 specifically:

- try the heavy WDQS path first where intended
- fall back to the light Wikibase API path (`wbsearchentities`, `wbgetentities`) when WDQS fails or returns no candidates, unless the light fallback is disabled
- construct canonical questions from templates
- pass enough structured metadata downstream for shared rewrite and route-local validation

The light path is a fallback only. It must repair or reject malformed candidates before validation; a candidate with an empty subject label must not proceed to ambiguity search.

### 4.2 Validator layer

Each route should declare which validators apply.

Example split:

- shared interfaces:
  - `validate_candidate(candidate, context) -> ValidationResult`
  - `deduplicate(candidates) -> candidates`
- Wikidata-route validators:
  - grounding
  - non-answer leakage checks tied to Wikidata labels/aliases
  - disambiguation against Wikidata competitors
  - time-invariance checks for Wikidata-derived facts
- Wikidata client hardening:
  - HTTP-200 API payloads containing `error` are treated as API errors, not successful responses
  - retryable errors such as `maxlag` can sleep/retry and are recorded in telemetry
  - blank `wbsearchentities` queries are skipped and recorded instead of sent to the API
- future route validators:
  - route-specific grounding
  - route-specific ambiguity checks
  - route-specific provenance validation

Important rule:

- shared pipeline orchestration may call validators through a common interface
- but the concrete validator logic must stay route-aware

### 4.3 Rewrite layer

The rewrite layer remains shared and should support route-specific prompt assembly.

Required behavior:

- produce a short natural question
- preserve necessary disambiguating information
- preserve the same answer relation and information scope as the canonical question
- do not add or change information from the canonical question
- do not narrow broad relations into more specific unsupported facts
- avoid answer leakage
- avoid putting the answer or answer aliases in the rewritten question
- avoid live-status phrasing
- respect the temporal policy for question wording
- generate a configurable number of answer-blind or minimally leaky search queries, defaulting to three for efficiency-focused pilots
- return useful answer aliases or abbreviations for snippet matching audit

For Route 1, the rewrite layer should generally start from a template-derived canonical question rather than raw source text alone.

### 4.4 Long-tail layer

The long-tail layer is shared in structure, even if thresholds may vary. Search queries should run with bounded parallelism per candidate, and the verifier may early-reject once the configured hit-rate thresholds are mathematically impossible to recover from.

Proposed order:

1. run DuckDuckGo search using:
   - the rewritten question
   - the LLM-generated query set
2. score answer exposure in search results
3. optionally run a SimpleQA Verified-style answer-model panel and autorater
4. accept or reject using explicit configurable rules

Possible rejection patterns:

- search results expose the answer too directly
- the model panel accuracy exceeds the configured difficulty threshold

The exact thresholds can remain configurable and should be tuned from pilot evidence.

For restored branch validation, the `product_manufacturer` walkthrough used thresholds of `1.0` for both DuckDuckGo stage 1 and model-panel accuracy so the candidate could pass through the full vertical slice while still recording every evidence signal.

## 5. Route 1 Design

Route 1 is the main concrete design target on this branch.

### 5.1 Inputs

Route 1 should use Wikidata-backed or Wikidata-groundable sources and template definitions.

The route may use:

- Wikidata entities and claims
- Wikipedia or other pages when they can be grounded back to Wikidata
- semi-structured public data that still supports Wikidata-centered validation

### 5.2 Route 1 flow

```text
Route 1 heavy WDQS harvest
  -> light Wikibase API fallback when enabled and needed
  -> template selection
  -> candidate fact extraction
  -> Route 1 validators before rewrite
  -> canonical template question
  -> shared LLM rewrite + query generation
  -> DuckDuckGo long-tail filter
  -> optional SimpleQA Verified-style model grading/difficulty review
  -> Route 1 post-rewrite checks
  -> shared recording and output
```

### 5.3 Route 1 validators

Validators for Route 1 should include:

- Wikidata grounding validation
- answer uniqueness checks
- Wikidata-based ambiguity/disambiguation validation
- time-invariance validation
- answer leakage checks
- deduplication
- subject-label presence before ambiguity search
- client-level handling for Wikidata API `error` payloads

Preferred reuse source:

- existing `5-12` validator logic where still compatible, especially for disambiguation and deduplication

### 5.4 Route 1 template policy

Templates should be:

- short
- natural
- relation-aware
- conservative

Templates should avoid:

- pipeline-exposing phrasing
- over-specific wording that leaks the answer
- unnecessary temporal anchors
- live-status language

The template layer should make it easier to:

- control semantic scope
- preserve answer uniqueness
- reuse high-precision validator logic

## 6. Template Catalog And Status Index

Canonical terminology is defined in `docs/terminology.md`. New code and docs should use `template_key` for identifiers such as `benchmark_release_date`, and `domain` for broad content areas such as `Architecture and Transportation`.

The template catalog is a first-class planning artifact, not just a list of prompts. Each template must carry explicit metadata for:

- `template_key`
- `domain`
- `answer_type`
- `answer_format`
- `composition_style`
- `reasoning_style`
- `temporal_mode`
- `current_status` in reports

`answer_type` is required for every template because downstream validation, number normalization, SimpleQA Verified-style margin handling, and reporting depend on it. Current accepted values are `Person`, `Organization`, `Place`, `Work`, `Date`, `Number`, and `Entity`.

Older code kept template keys in `DomainTemplate.domain` and broad domains in `DomainTemplate.topic`. Those names are compatibility shims only. Future work should prefer `template.template_key` and `template.template_domain`, and artifact readers should accept old JSONL fields only at the boundary.

The old `active` / `blueprint` split came from the small-pilot era and should not drive current behavior. It may survive as a legacy catalog bucket for compatibility, but the human-facing reports should be organized by `current_status`, domain, template key, and answer type.

The `frozen` bucket is an explicit template-key override. If a template key is listed in `FROZEN_TEMPLATE_KEYS`, it should render as `current_status = frozen` even when its original/latest live status was `error`, `unproven_no_result`, or some other run-derived result. The original run-derived status must still be retained as metadata (`original_current_status`, `latest_live_status`, and `best_known_semantic_status`) so we can explain why the template was frozen rather than losing diagnostic history.

The main status buckets are:

- `proven`: a template has a known successful generated question in the review bundle or accepted artifacts.
- `rejected_only`: runs reached candidate generation but current review rejected the outputs.
- `error`: runs failed operationally.
- `unproven_no_result`: a real run produced no candidate, often because the 2026 window was sparse or an executor/probe was missing.
- `untracked`: the template has no usable current artifact trail.
- `frozen`: the catalog intentionally preserves the template for future design work while excluding it from normal activation.

The canonical human-readable status report is `docs/template_status_index.md`. The JSON companion may remain in `outputs/template_status_index.json` as a machine artifact.

Status reports are keyed by `template_key`. Every catalog template must have exactly one template key and one broad domain.

## 7. Non-Wikidata Route Policy

Future routes are allowed, but they must not inherit Route 1 assumptions by default.

For a non-Wikidata route:

- define its own grounding scheme
- define its own ambiguity logic
- define its own temporal checks if the source semantics differ
- define its own deduplication and provenance rules where needed

For `route3_wikipedia_infobox`, the first implementation intentionally has no route-local factual validator beyond parsing success and model-output shape checks. It stores provenance and parsed source content as metadata, then relies on shared surface checks, DuckDuckGo long-tail filtering, optional model grading, and manual review. The lost-subject-anchor and incomplete-tie detectors are retained as review signals but are no longer hard rejection gates because pilot review showed too many false positives. Numeric answer-leakage checks compare extracted normalized number values rather than raw substrings, so a short answer such as `6` is not rejected merely because a year such as `2016` appears in the question.

Route 3 runner invocations may resume from existing accepted/rejected JSONL at the validation stage. This path reconstructs generated candidates from stored metadata and LLM responses, clears stale surface-rejection metadata, and reruns the shared downstream filters without refetching pages or regenerating questions.

The framework should share contracts, not forced source assumptions.

## 8. Auditing Requirements

Every accepted or rejected candidate should store enough information to reconstruct:

- route name
- generator-specific input payload
- canonical question before rewrite
- rewritten question after rewrite
- search queries used
- DuckDuckGo evidence
- model grading evidence when enabled
- validator decisions
- rejection reasons
- source identifiers and URLs where available
- phase timings and bottlenecks
- Wikidata/search/model telemetry and operational failures

Walkthrough-grade runs should also record every DuckDuckGo query, result URL, snippet, string-inclusion result, small-model answer, and grader judgement. The restored branch includes such a walkthrough for the `product_manufacturer` template.

This remains critical because `5-13` is intended to stay conservative and reviewable.

## 9. Migration Guidance from 5-12

When implementing this branch, prefer the following migration logic:

1. keep the multi-generator scaffold
2. keep shared rewrite/output contracts
3. reintroduce templates for Route 1
4. remove sitelink/claim-count long-tail gating
5. add SimpleQA Verified-style grading/difficulty review rather than a standalone cheap-model QA rejection gate
6. separate validator bundles by route
7. reuse `5-12` disambiguation and deduplication logic where possible

## 10. Summary

Branch `5-13-restored` keeps the newer shared-pipeline worldview from `5-12`, but changes the Route 1 and validator philosophy:

- Route 1 is template-led again
- years and dates are allowed when historically settled and earlier than 2025 by default
- validators are route-specific, not globally assumed
- one shared LLM call still produces both question rewrite and search queries
- long-tail and difficulty filtering becomes:
  - DuckDuckGo search
  - optional SimpleQA Verified-style model grading
- existing `5-12` Wikidata validators should be reused where they still fit

This branch should therefore be treated as a **template-restored, route-decoupled evolution of `5-12`**, not as a return to the older all-in-one template architecture.
