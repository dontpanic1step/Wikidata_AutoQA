# AGENTS.md

## Project north star

Build a conservative generator for **SimpleQA / SimpleQA Verified-style short factual questions**.

The main target is the **question style and evaluation setting**: short, natural, fact-seeking questions with a single stable gold answer. The implementation method is secondary and may change if another route better reproduces SimpleQA-like examples.

When project documents conflict, this file is the highest-level instruction. Update `docs/design.md` before implementing code if the design still encodes older constraints.

Use `docs/terminology.md` for canonical project terms. In particular, use **template key** for identifiers such as `benchmark_release_date`, and **domain** for broad content areas such as `Architecture and Transportation`. Older code/artifacts may still use `domain` to mean template key; normalize that at compatibility boundaries instead of spreading the legacy wording.

## Current strategic direction

- Replicate SimpleQA-style questions through one conservative, auditable production path.
- Route 3, the Wikipedia semi-structured table/infobox route, is the only formal generation route.
- `scripts/run_wikipedia_infobox_recipe.py` is the only user-facing generation entry point.
- `scripts/run_wikipedia_infobox_pipeline.py` is an internal segment worker and is not a second user-facing workflow.
- Route 1, Route 2, KELM, and the old finalization workflow are historical code. Do not extend, repair, or present them as part of the formal method during the reconstruction milestones.
- `scripts/run_openrouter_night_batch.py` is an unused historical evaluation orchestrator. It is not one of the protected evaluation tools and must not be used by the formal workflow.
- The rule-based gates explicitly removed by `docs/reconstruction/milestones.md` are not part of the formal Route 3 method. Do not replace them with new heuristics.
- Preserve `scripts/run_openrouter_batch_predictions.py` and `scripts/judge_openrouter_batch_predictions.py` as independent SimpleQA Verified-style evaluation tools. They are not generation, manual review, second-stage filtering, or finalization components.
- Do not reorganize the protected evaluation prompts, grading labels, examples, or unparseable-output semantics while stabilizing Route 3.
- Prefer a minimal runnable vertical slice that can produce a small manually reviewable pilot batch before scaling.
- Treat pilot output as candidate generation, not final verified data.

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
- If the answer is temporal, the question must specify the requested precision or unit, such as `what year`, `what month`, `what day`, or `how many months`.
- If the answer is a full calendar date, ask `what day, month, and year ...` so the reference answer can normalize cleanly.
- If the answer is a number, specify the counted quantity or unit in the question, such as `how many gallons`, and keep the reference answer unit-free.

## Candidate sources and long-tail validation

- Do not use internal popularity proxies such as sitelink count, claim count, or similar Wikidata-wide indices as first-stage long-tail filters.
- Use external retrieval as the hard long-tail leakage filter:
  - Stage 1: DuckDuckGo search-based evidence.
  - Stage 2: SimpleQA Verified-style model grading/difficulty review, when enabled.
- Prefer search-based evidence as the first long-tail signal.
- A useful first heuristic: call a search API and inspect the top results. Mark a candidate as more long-tail if the direct answer is absent from the top results or requires nontrivial cross-source lookup.
- Keep the long-tail heuristic auditable: store query strings, top-result titles/snippets/URLs when allowed, and the rule that accepted or rejected the candidate.
- Do not use a standalone cheap-model exact-match QA phase as a rejection gate. SimpleQA Verified uses autorated model answers for difficulty/evaluation, so model-based difficulty checks should live in the grading panel instead.
- Consider more clever search-based signals later, such as exact-title hits, answer-string hits, snippet answer leakage, and whether the answer appears in the first page of results.
- Use LLMs for rewriting or optional review, not for inventing facts, proving uniqueness, or serving as the primary factuality validator.

## Content directions to explore

- Semi-structured public data, such as rankings, tables, lists, infoboxes, and Wikipedia right-side info cards.
- Historically settled facts exposed by Wikipedia tables and infoboxes.
- Other sources and multi-hop methods are future research directions, not formal generation routes in the current reconstruction.

## Factuality, uniqueness, and grading

- Every accepted example must have exactly one intended gold answer.
- Store enough metadata to audit and regenerate the example: source URLs or IDs, retrieval method, query strings, entity IDs when available, answer aliases, and rejection reasons.
- Use deterministic checks where possible for factuality, uniqueness, ambiguity, answer leakage, and time-invariance.
- Validators must remain decoupled from the rest of the pipeline. Route 3 validators should reflect Wikipedia table provenance and Route 3 failure modes rather than historical Wikidata-route assumptions.
- Historical route validators may remain import-time dependencies until their removal is explicitly scheduled, but they are not part of the formal Route 3 method.
- Include an automatic grader inspired by SimpleQA / SimpleQA Verified: `CORRECT`, `INCORRECT`, and `NOT_ATTEMPTED`.
- Prefer high precision over high recall.

## Implementation style

- Start with a small end-to-end pipeline before adding breadth.
- Add tests for validators and grading rules before scaling.
- Keep outputs metadata-rich and auditable.
- Prefer general solutions over one-off patches.
- Record query, search, harvesting, and validation failures so they can be reviewed later.
- All code comments and docstrings must be in English.
- Network runs with batch size <= 10 examples, URLs, or records do not require advance permission; just run them when needed for the task, including Wikipedia, Wikidata, search API, and OpenRouter calls. Ask before network-heavy runs above that size, dependency installs, destructive actions, credential changes, or secret-handling changes.
- Do not use destructive commands, including `git clean -fd`, unless the user explicitly requests that exact action.
- Do not modify files under `docs/human_notes/`.
