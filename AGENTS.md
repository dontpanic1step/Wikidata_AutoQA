# AGENTS.md

## Project north star

Build a conservative generator for **SimpleQA / SimpleQA Verified-style short factual questions**.

The main target is the **question style and evaluation setting**: short, natural, fact-seeking questions with a single stable gold answer. The implementation method is secondary and may change if another route better reproduces SimpleQA-like examples.

When project documents conflict, this file is the highest-level instruction. Update `design.md` before implementing code if the design still encodes older constraints.

## Current strategic direction

- Replicate SimpleQA-style questions first; do not optimize prematurely for a particular Wikidata-only pipeline.
- The target matters more than the method. Wikidata, Wikipedia, search APIs, and semi-structured public data are all acceptable inputs if the resulting question is auditable and stable.
- Use Wikidata when it is convenient, but do not get blocked by WDQS. If WDQS is unreliable or too restrictive, use search APIs and direct Wikidata/Wikipedia URL construction where possible.
- Keep the current multi-generator architecture with shared LLM rewriting and shared long-tail filtering, but allow route-specific harvesting and route-specific validation layers.
- Route 1 is again template-led. It should use templates to construct candidate questions before shared rewriting.
- Prefer a minimal runnable vertical slice that can produce a small manually reviewable pilot batch before scaling.
- Treat the first pilot as candidate generation, not final verified data.

## Question policy

- Questions may contain years, dates, or temporal anchors when they refer to historically settled facts.
- Do not impose a blanket ban on all temporal expressions.
- Avoid questions whose temporal anchor is too recent or likely to fall after model knowledge cutoffs. As a default conservative threshold, avoid question text that depends on events in **2025 or later**, unless the project config explicitly overrides this.
- The purpose of the temporal policy is to avoid model refusals caused only by post-cutoff timing, not to remove all historical dates.
- It is acceptable to use entities from any time period. The time restriction applies to what the question text depends on, not to whether the entity itself is old or recent.
- Old or obscure facts are welcome. A niche question about a settled event from 2006 is acceptable if it has a unique, auditable answer.
- Reject questions requiring `current`, `currently`, `latest`, `most recent`, `as of now`, or other live-status framing.
- Gold answers must be time-invariant. Reject mutable statuses, current roles, relationships, affiliations, and cumulative statistics by default.
- Historically settled slices of otherwise mutable properties may be allowed only when deterministic provenance shows the slice is fixed.

## SimpleQA-style wording

- Keep questions short, natural, and fact-seeking.
- Prefer wording that a human would actually use.
- Rewrite unnatural relation labels into natural category names.
  - Bad: `Who developed the software GPT-5.4?`
  - Better: `Who developed the model GPT-5.4?`
  - Bad: calling every digital artifact `software`.
  - Better: use `model`, `video game`, `dataset`, `benchmark`, `film`, `album`, `article`, `building`, etc. as appropriate.
- Avoid over-engineered question wording that exposes the pipeline rather than the fact being asked.
- Do not let disambiguation descriptors leak the answer.

## Candidate sources and long-tail validation

- Do not use internal popularity proxies such as sitelink count, claim count, or similar Wikidata-wide indices as first-stage long-tail filters.
- Use a two-stage long-tail filter built from external retrieval and cheap model probing:
  - Stage 1: DuckDuckGo search-based evidence.
  - Stage 2: cheap, fast, small-model QA evaluation, such as GPT-4.1-mini or Gemini 3.1 Flash.
- Prefer search-based evidence as the first long-tail signal.
- A useful first heuristic: call a search API and inspect the top results. Mark a candidate as more long-tail if the direct answer is absent from the top results or requires nontrivial cross-source lookup.
- Keep the long-tail heuristic auditable: store query strings, top-result titles/snippets/URLs when allowed, and the rule that accepted or rejected the candidate.
- The small-model QA stage is a secondary filter, not a source of truth for factuality. It is used only as an auditable difficulty signal after search.
- Consider more clever search-based signals later, such as exact-title hits, answer-string hits, snippet answer leakage, and whether the answer appears in the first page of results.
- Use LLMs for rewriting or optional review, not for inventing facts, proving uniqueness, or serving as the primary factuality validator.

## Content directions to explore

- Multi-hop questions where the final answer requires composing two or more stable facts.
- Semi-structured public data, such as rankings, tables, lists, infoboxes, and Wikipedia right-side info cards.
- Wikipedia and Wikidata metadata when they provide stable, auditable facts.
- Other data sources besides Wikipedia and Wikidata, such as music websites.

## Factuality, uniqueness, and grading

- Every accepted example must have exactly one intended gold answer.
- Store enough metadata to audit and regenerate the example: source URLs or IDs, retrieval method, query strings, entity IDs when available, answer aliases, and rejection reasons.
- Use deterministic checks where possible for factuality, uniqueness, ambiguity, answer leakage, and time-invariance.
- Validators must be decoupled from the rest of the pipeline. Do not assume one validator stack applies to every route.
- Wikidata grounding, Wikidata-based disambiguation, time-invariance checks, and deduplication for Route 1 should be treated as Wikidata-route validators that can be reused by other Wikidata-based generators.
- Future non-Wikidata routes must define their own validators according to their source format, grounding assumptions, and failure modes.
- Include an automatic grader inspired by SimpleQA / SimpleQA Verified: `CORRECT`, `INCORRECT`, and `NOT_ATTEMPTED`.
- Prefer high precision over high recall.

## Implementation style

- Start with a small end-to-end pipeline before adding breadth.
- Add tests for validators and grading rules before scaling.
- Keep outputs metadata-rich and auditable.
- Prefer general solutions over one-off patches.
- Record query, search, harvesting, and validation failures so they can be reviewed later.
- All code comments and docstrings must be in English.
- Ask before installing dependencies or making network-heavy changes.
- Do not modify files under `docs/human_notes/`.
