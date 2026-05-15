# Design 5-13

This document defines the intended design for branch `5-13`.

It replaces the `5-12` branch direction for new work on this branch, while keeping the same high-level project goal:

- generate conservative, auditable, SimpleQA-style short factual questions
- keep the multi-generator architecture
- keep shared LLM rewriting
- keep shared long-tail filtering

The main strategic change is that **Route 1 returns to template-led generation**.

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

## 3. Main Changes on 5-13

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

### 3.5 Long-tail filtering changes

The old first-stage long-tail filter based on internal popularity proxies should be removed.

Delete as long-tail gates:

- sitelink-count thresholds
- claim-count thresholds
- similar internal index-based popularity filters

New two-stage long-tail filtering:

1. DuckDuckGo search-based filtering
2. cheap, fast, small-model QA filtering

Suitable small-model examples include:

- GPT-4.1-mini
- Gemini 3.1 Flash

Design intent:

- search checks whether the answer is exposed too directly in public retrieval
- small-model QA checks whether the question is still too easy for a cheap general model

The cheap-model stage is a difficulty heuristic, not a factuality oracle.

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

- harvest from Wikidata-backed sources
- construct canonical questions from templates
- pass enough structured metadata downstream for shared rewrite and route-local validation

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
- do not narrow broad relations into more specific unsupported facts
- avoid answer leakage
- avoid live-status phrasing
- respect the temporal policy for question wording
- generate answer-blind or minimally leaky search queries
- return useful answer aliases or abbreviations for snippet matching audit

For Route 1, the rewrite layer should generally start from a template-derived canonical question rather than raw source text alone.

### 4.4 Long-tail layer

The long-tail layer is shared in structure, even if thresholds may vary.

Proposed order:

1. run DuckDuckGo search using:
   - the rewritten question
   - the LLM-generated query set
2. score answer exposure in search results
3. run cheap-model QA against the rewritten question
4. accept or reject using explicit configurable rules

Possible rejection patterns:

- search results expose the answer too directly
- a cheap model answers correctly too reliably
- combined search and cheap-model evidence shows the question is not long-tail enough

The exact thresholds can remain configurable and should be tuned from pilot evidence.

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
Route 1 harvest
  -> template selection
  -> candidate fact extraction
  -> Route 1 validators before rewrite
  -> canonical template question
  -> shared LLM rewrite + query generation
  -> DuckDuckGo long-tail filter
  -> cheap-model QA long-tail filter
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

## 6. Non-Wikidata Route Policy

Future routes are allowed, but they must not inherit Route 1 assumptions by default.

For a non-Wikidata route:

- define its own grounding scheme
- define its own ambiguity logic
- define its own temporal checks if the source semantics differ
- define its own deduplication and provenance rules where needed

The framework should share contracts, not forced source assumptions.

## 7. Auditing Requirements

Every accepted or rejected candidate should store enough information to reconstruct:

- route name
- generator-specific input payload
- canonical question before rewrite
- rewritten question after rewrite
- search queries used
- DuckDuckGo evidence
- cheap-model QA evidence
- validator decisions
- rejection reasons
- source identifiers and URLs where available

This remains critical because `5-13` is intended to stay conservative and reviewable.

## 8. Migration Guidance from 5-12

When implementing this branch, prefer the following migration logic:

1. keep the multi-generator scaffold
2. keep shared rewrite/output contracts
3. reintroduce templates for Route 1
4. remove sitelink/claim-count long-tail gating
5. add the second long-tail stage using a cheap QA model
6. separate validator bundles by route
7. reuse `5-12` disambiguation and deduplication logic where possible

## 9. Summary

Branch `5-13` keeps the newer shared-pipeline worldview from `5-12`, but changes the Route 1 and validator philosophy:

- Route 1 is template-led again
- years and dates are allowed when historically settled and earlier than 2025 by default
- validators are route-specific, not globally assumed
- one shared LLM call still produces both question rewrite and search queries
- long-tail filtering becomes:
  - DuckDuckGo search
  - cheap, fast, small-model QA
- existing `5-12` Wikidata validators should be reused where they still fit

This branch should therefore be treated as a **template-restored, route-decoupled evolution of `5-12`**, not as a return to the older all-in-one template architecture.
