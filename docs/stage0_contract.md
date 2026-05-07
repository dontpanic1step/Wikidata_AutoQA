# Stage 0 Contract

## Purpose

This document freezes the minimum implementation contract for the first runnable version of the Wikidata-to-SimpleQA-Verified-style dataset generator.

Stage 0 does not try to solve the full project. Its goal is to define a narrow, conservative target that later stages can implement without re-deciding core rules.

## Stage 0 Outcomes

The first implementation must optimize for precision, auditability, and deterministic validation.

The Stage 0 contract freezes:

- the MVP scope,
- the initial domain whitelist,
- the core data model,
- the rejection taxonomy,
- the validator contract,
- the output contract,
- the non-goals for the first runnable version.

## Core Principles

Every later stage must preserve these rules:

1. Questions must not contain years, dates, month names, or temporal expressions.
2. Gold answers must be time-invariant.
3. Mutable roles, relationships, affiliations, and cumulative statistics must be rejected.
4. Wikidata plus deterministic validators own factuality, uniqueness, ambiguity, and time-invariance decisions.
5. LLMs may rewrite wording once, but must never invent facts or judge uniqueness.
6. High precision is more important than high recall.
7. Outputs must be metadata-rich and auditable.

## MVP Scope

The first runnable implementation targets one conservative vertical slice and a small extension path.

### Mandatory Stage 1 Vertical Slice

The first end-to-end slice must support:

- one domain-property pair,
- deterministic candidate harvesting,
- deterministic validation,
- canonical question construction,
- accepted and rejected JSONL outputs.

Recommended first pair:

- domain: `film`
- date property: `P577`
- answer property: `P57`
- question intent: film -> director

### Allowed Initial Expansion Set

After the first vertical slice works, the implementation may expand to this whitelist only:

| Domain | Subject type intent | Date property | Answer property | Canonical question intent |
|---|---|---|---|---|
| `film` | film | `P577` | `P57` | `Who directed {descriptor}?` |
| `book` | novel or book | `P577` | `P50` | `Who wrote {descriptor}?` |
| `video_game` | video game | `P577` | `P178` | `Which company developed {descriptor}?` |
| `scholarly_article` | scholarly article | `P577` | `P1433` | `In which journal was {descriptor} published?` |
| `artwork` | artwork | `P571` or `P577` | `P170` | `Who created {descriptor}?` |
| `building` | building | `P571` | `P84` | `Who designed {descriptor}?` |
| `organization` | organization or company | `P571` | `P112` | `Who founded {descriptor}?` |
| `place` | place or infrastructure | `P571` | `P17` or `P131` | `In which country is {descriptor} located?` |

### Explicit Non-Goals for the First Runnable Version

The first runnable version must not target:

- current office holders,
- current affiliations,
- spouses or partners,
- cast lists,
- producers,
- genres,
- awards received,
- occupations,
- platforms,
- sports team membership,
- population,
- employee counts,
- box-office, revenue, sales, downloads, followers, citations, or net worth,
- upcoming or unreleased works,
- any question type that naturally requires `current`, `latest`, `recent`, or `as of`.

## Frozen Configuration Contract

The implementation must support at least these config fields:

```python
TARGET_TIME: str
TARGET_START_DATE: str
RUN_DATE: str
DATE_UPPER_BOUND: str
PILOT_TOTAL: int
HARVEST_LIMIT_PER_TEMPLATE: int
ALLOW_YEAR_IN_OFFICIAL_TITLE: bool = False
REJECT_FUTURE_DATED_CANDIDATES: bool = True
REJECT_CURRENT_OR_LATEST_FACTS: bool = True
REJECT_MUTABLE_RELATIONSHIPS: bool = True
REJECT_MUTABLE_AFFILIATIONS: bool = True
REJECT_CUMULATIVE_STATISTICS: bool = True
REJECT_UNRELEASED_WORKS: bool = True
USER_AGENT: str
PROXY: str | None
TIMEOUT_SECONDS: float
RANDOM_SEED: int = 42
```

Rules:

- `TARGET_TIME` is for candidate harvesting only, never for question wording.
- `TARGET_TIME` accepts `YYYY`, `YYYY-MM`, or `YYYY-MM-DD`.
- `DATE_UPPER_BOUND` defaults to the pipeline run date.
- `ALLOW_YEAR_IN_OFFICIAL_TITLE` must default to `False`.
- Strict rejection flags must default to `True`.

## Core Data Model Contract

The pipeline must use a metadata-rich candidate object that can survive audit and rejection analysis.

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class CandidateFact:
    subject_qid: str
    subject_label: str
    subject_aliases: list[str]
    domain: str
    subject_type_qids: list[str]
    target_property_pid: str
    target_property_label: str
    answer_qids: list[str]
    answer_labels: list[str]
    answer_aliases: list[str]
    date_property_pid: str
    date_value: str
    target_time: str
    canonical_question: str
    rewritten_question: str | None = None
    ambiguity_status: str = "unknown"
    disambiguation_signature: list[str] = field(default_factory=list)
    competitor_qids: list[str] = field(default_factory=list)
    validation_flags: dict[str, Any] = field(default_factory=dict)
    source_metadata: dict[str, Any] = field(default_factory=dict)
```

### Required Candidate Metadata

Each accepted or rejected candidate must be traceable through:

- subject QID,
- answer QID or QIDs,
- target property PID,
- date property PID,
- harvested date value,
- domain key,
- deterministic validation results,
- ambiguity status,
- competitor QIDs when applicable,
- retrieval metadata,
- rejection reason for rejected items.

## Frozen Rejection Taxonomy

The implementation must use stable machine-readable rejection reasons.

```python
REJECTION_REASONS = {
    "subject_label_contains_temporal_expression",
    "subject_label_contains_year",
    "answer_not_time_invariant",
    "future_dated_or_unsettled_fact",
    "mutable_relationship_or_status",
    "mutable_affiliation_or_office",
    "cumulative_statistic",
    "answer_not_unique",
    "no_english_label",
    "no_answer_label",
    "same_label_competitor_requires_temporal_disambiguation",
    "no_non_temporal_signature",
    "descriptor_leaks_answer",
    "canonical_question_failed_validation",
    "rewrite_contains_year",
    "rewrite_contains_temporal_expression",
    "rewrite_lost_required_anchor",
    "rewrite_leaks_answer",
    "duplicate_question",
    "quota_exceeded",
}
```

Notes:

- The taxonomy may expand later, but existing identifiers should not be renamed casually.
- Rejection reasons must be written to the rejected output, not only logs.

## Validator Contract

Validators are the core of the framework and must be deterministic.

### Required Validators Before Scaling

The first implementation must define clear interfaces for these validators:

1. Temporal question validator.
2. Time-invariance validator.
3. Answer uniqueness validator.
4. Subject ambiguity validator.
5. Non-temporal disambiguation validator.
6. Answer leakage validator.
7. Rewrite anchor-preservation validator.

### Minimum Validator Semantics

#### Temporal Question Validator

Reject if the question contains:

- a year,
- a date,
- a month name,
- a temporal phrase such as `current`, `currently`, `latest`, `recent`, `this year`, `last year`, `next year`, or `as of`.

#### Time-Invariance Validator

Accept only if the answer is a settled attribution or other stable fact whose answer will not change depending on when the question is asked.

Reject if the target fact is:

- a mutable role,
- a mutable relationship,
- a mutable affiliation,
- a current status,
- a cumulative statistic,
- future-dated,
- unreleased,
- planned but not settled.

#### Answer Uniqueness Validator

Accept only if:

- the candidate has exactly one answer under the target property,
- there are no conflicting non-deprecated statements that matter,
- temporal qualifiers are not required to decide which answer is correct.

#### Subject Ambiguity Validator

Accept only if the question can identify the intended subject without temporal wording.

#### Non-Temporal Disambiguation Validator

If a same-name competitor exists, the system must either:

- resolve the target using non-temporal descriptors, or
- reject the candidate.

If the only working descriptor is a year, date, or recency phrase, reject.

#### Answer Leakage Validator

Reject if the question directly includes the answer or a trivial form of it.

#### Rewrite Anchor-Preservation Validator

Reject rewritten questions that remove required non-temporal disambiguation anchors.

## Domain Template Contract

The implementation must use config-driven domain templates rather than hard-coded procedural branches.

Each domain template must define at least:

- a domain key,
- allowed subject type QIDs,
- a date property PID,
- a target answer property PID,
- a canonical question template,
- descriptor rules,
- high-risk exclusions if needed.

The canonical template must remain explicit enough to avoid property confusion.

Examples:

- prefer `Who directed the film {descriptor}?`
- avoid `Who created {subject}?` when the property-specific intent is unclear

## Wikidata Access Contract

The first implementation must support:

1. SPARQL candidate harvesting through WDQS.
2. `wbgetentities` hydration for subject and answer entities.
3. `wbsearchentities` competitor discovery.

Operational requirements:

- set a meaningful User-Agent,
- support proxy configuration,
- support request timeout,
- support retries with backoff,
- keep network usage conservative,
- prefer deterministic caching once file structure is added later.

## Output Contract

The first runnable generation path must produce:

- one accepted-output JSONL file,
- one rejected-output JSONL file.

### Accepted Output

Each accepted example must include at least:

```json
{
  "id": "wikidata_verified_pilot_000001",
  "question": "Who directed the film adaptation of Andy Weir's novel Project Hail Mary?",
  "answer": "Phil Lord and Christopher Miller",
  "answer_aliases": [],
  "subject_qid": "Q...",
  "answer_qids": ["Q..."],
  "property_pid": "P57",
  "domain": "film",
  "target_time": "2026",
  "date_filter": {
    "property": "P577",
    "value": "2026-..."
  },
  "ambiguity_status": "resolved_by_non_temporal_descriptor",
  "disambiguation_signature": [
    "film adaptation",
    "based on Andy Weir's novel"
  ],
  "canonical_question": "...",
  "rewritten_question": "...",
  "validation_flags": {
    "no_year": true,
    "no_temporal_expression": true,
    "answer_unique": true,
    "subject_unique_under_question": true,
    "answer_not_leaked": true
  },
  "source_metadata": {
    "retrieval_method": "WDQS + wbgetentities + wbsearchentities"
  }
}
```

### Rejected Output

Each rejected item must include at least:

- the candidate metadata available at the time of rejection,
- one primary rejection reason,
- optional supporting notes,
- retrieval metadata.

## Testing Contract

Tests must be added before scaling beyond the first vertical slice.

The first required test groups are:

1. temporal validator tests,
2. time-invariance tests,
3. ambiguity tests,
4. answer leakage tests,
5. name normalization tests.

The tests should prioritize representative failures over broad coverage.

## Deferred Until After Stage 0

These are intentionally not frozen as hard requirements for the first code-writing step:

- full caching layout,
- concurrency strategy,
- multi-provider rewrite support beyond the abstraction boundary,
- final balancing heuristics,
- LLM-based grading details,
- broad domain coverage,
- optimization for throughput.

## Definition of Done for Stage 0

Stage 0 is complete when the repository has an implementation-ready contract that answers:

1. What is the first vertical slice?
2. Which domains are allowed first?
3. What candidate metadata is mandatory?
4. Which rejection reasons are stable?
5. Which validators must exist before scaling?
6. What must accepted and rejected outputs contain?
7. Which problem areas are explicitly out of scope for the first runnable version?

This document is the source of truth for those decisions until implementation reveals a concrete mismatch.
