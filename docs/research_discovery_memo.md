# Research Discovery Memo

Date: 2026-05-12

Purpose: keep an ongoing, engineering-oriented research record for the redesign toward SimpleQA-style question generation. This memo records confirmed findings, current project implications, candidate implementation routes, and user decisions gathered so far. Future research can extend this file.

## Current Working Decisions

- Preferred implementation direction: Route 2 (`Wikidata seed + Wikipedia evidence hybrid`)
- Fallback direction: Route 1 (`Wikidata-first, WDQS-light single-hop`)
- Temporal cutoff in question text: avoid questions that depend on events in `2025` or later by default
- First pilot source policy: a Wikidata source is required
- Search API for long-tail checks: DuckDuckGo
- First implementation target: single-hop only
- Date and Number answers: allowed, each should occupy around 10% of total QAs
- Wikimedia-source clarification: for the first pilot, the hard requirement is Wikidata; this may be relaxed later

## 1. Confirmed Findings

### A. How to write natural SimpleQA-style questions

- SimpleQA is explicitly a benchmark for short, fact-seeking questions with clear, unambiguously correct answers.
  Source: [Measuring short-form factuality in large language models](https://huggingface.co/papers/2411.04368)

- SimpleQA’s grading setup assumes one intended answer and uses `CORRECT`, `INCORRECT`, and `NOT_ATTEMPTED`, which strongly favors questions whose answer boundary is clean and easy to adjudicate.
  Source: [simple-evals/simpleqa_eval.py](https://github.com/openai/simple-evals/blob/main/simpleqa_eval.py)

- The official SimpleQA evaluator tolerates answer normalization when the omitted information is obvious from the question. It accepts examples like:
  - city without state
  - award name without the word `award`
  - a person’s first name without the last name when the identity is obvious
  - clear name typos
  Source: [simple-evals/simpleqa_eval.py](https://github.com/openai/simple-evals/blob/main/simpleqa_eval.py)

- SimpleQA Verified keeps the same short-form factual style but does not enforce a blanket ban on historical dates or years in question text. Its dataset card includes historical, temporally anchored questions and adds metadata such as `topic`, `answer_type`, `multi_step`, `requires_reasoning`, and supporting `urls`.
  Source: [google/simpleqa-verified · Datasets at Hugging Face](https://huggingface.co/datasets/google/simpleqa-verified)

- SimpleQA Verified is explicitly intended for no-tool evaluation; with search/retrieval tools, the benchmark becomes trivial. This is relevant because our generation pipeline can use tools to estimate whether a question is too easy or answer-leaky.
  Source: [google/simpleqa-verified · Datasets at Hugging Face](https://huggingface.co/datasets/google/simpleqa-verified)

- KGQA naturalness research shows that template-derived questions often remain unnatural even when they are grammatically valid, and that question naturalness materially affects downstream behavior.
  Source: [Would You Ask it that Way? Measuring and Improving Question Naturalness for Knowledge Graph Question Answering](https://huggingface.co/papers/2205.12768)

- Practical style implication from these sources: the target should be ordinary human phrasing around a single intended fact, not literal verbalization of graph relations.
  This is an implementation suggestion inferred from the sources above, not a direct source claim.

### B. Existing Wikidata-based automatic QA generation systems

- LC-QuAD 2.0 uses a staged generation workflow:
  1. generate SPARQL from templates
  2. convert to intermediate template questions
  3. crowd-verbalize to natural language
  4. paraphrase again
  This is a concrete example of using structured generation plus a separate naturalization stage.
  Source: [LC-QuAD 2.0](https://sda.tech/projects/lc-quad-2/)

- KGConv grounds each QA pair in a Wikidata fact and creates multiple question variants per fact using templates, human annotations, hand-crafted rules, and a neural question rewriting model.
  Source: [KGConv, a Conversational Corpus grounded in Wikidata](https://huggingface.co/papers/2308.15298)

- Wikidata’s own data-access guidance says WDQS should be used when you know the characteristics of the desired data, but not for text or fuzzy search, and not when the desired result set is very large.
  Source: [Wikidata:Data access](https://www.wikidata.org/wiki/Help%3AData_access)

- Wikidata’s guidance also says the API is appropriate for small groups of known entities in JSON form, while large-scale access should use dumps instead.
  Source: [Wikidata:Data access](https://www.wikidata.org/wiki/Help%3AData_access)

- Wikibase’s Action API supports `wbgetentities`, including resolution by IDs or by site/title pairs such as English Wikipedia titles, and `wbsearchentities`, which searches using labels and aliases.
  Source: [Wikibase/API](https://www.mediawiki.org/wiki/Wikibase/API)

- MediaWiki’s REST API is an official interface for wiki content access and is a plausible complement to Wikidata entity access when we want page-oriented evidence rather than graph-oriented querying.
  Source: [API:REST API](https://www.mediawiki.org/wiki/API%3AREST_API/en)

- EntityQuestions, which builds simple entity-centric questions from Wikidata facts, found that models generalize much better to common entities than to rare entities or unseen question patterns. That makes entity popularity and phrasing diversity important if we want nontrivial questions.
  Source: [Simple Entity-Centric Questions Challenge Dense Retrievers](https://collaborate.princeton.edu/en/publications/simple-entity-centric-questions-challenge-dense-retrievers)

### C. Lightweight methods for testing question long-tailness

- SimpleQA Verified’s own limitation note says the benchmark becomes trivial with tools. For our purposes, that means tool-assisted answer leakage is a useful screening signal even if it is not part of the benchmark itself.
  Source: [google/simpleqa-verified · Datasets at Hugging Face](https://huggingface.co/datasets/google/simpleqa-verified)

- SimpleQA Verified includes at least two supporting URLs for each gold answer. This suggests a useful separation between:
  - answer support
  - answer difficulty or leakage
  Source: [google/simpleqa-verified · Datasets at Hugging Face](https://huggingface.co/datasets/google/simpleqa-verified)

- Question-difficulty research identifies two useful axes:
  - `obscurity`: how rare the answer is
  - `opacity`: how indirect the question cues are
  These are useful conceptual anchors for long-tail heuristics.
  Source: [Opacity, obscurity, and the geometry of question-asking](https://www.sciencedirect.com/science/article/pii/S0010027719302446)

- Wikimedia provides official pageview endpoints for Wikimedia projects, including per-page pageview counts and most-viewed pages. These can be used as lightweight popularity features.
  Sources: [Page view analytics | Wikimedia Analytics API](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/reference/page-views.html), [Page metrics | Wikimedia Analytics API](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/examples/page-metrics.html)

### Uncertain assumptions and source gaps

- I have not yet extracted the full methodology from the SimpleQA Verified paper PDF itself; current claims rely on the dataset card and linked benchmark metadata.

- I have not yet found a primary-source benchmark paper that directly endorses a DuckDuckGo-style top-k snippet leakage test as the standard way to measure long-tailness. That part remains an engineering proposal rather than a literature-backed standard.

- I have not yet reviewed DuckDuckGo API terms/capabilities in detail for snippet availability, stability, or rate behavior. That needs separate validation before implementation planning.

## 2. Practical Implications for Our Project

- We should imitate SimpleQA’s short, direct, ordinary phrasing. Questions should sound like something a human would ask, not like a relation label verbalized from a graph.

- We should avoid:
  - literal property-label wording
  - graph-exposing phrasing
  - over-specified disambiguation text
  - explicit chain wording for multi-hop questions
  - live-status framing such as `current`, `latest`, or `as of now`

- The most reusable idea from prior QA-generation work is the hybrid pattern:
  1. select or validate facts structurally
  2. generate a rough question form
  3. naturalize it in a separate step
  4. run deterministic post-filters

- The most promising data-access strategy for the first pilot is:
  - Wikidata for entity normalization and stable identifiers
  - Wikipedia page/title access for human-readable phrasing and evidence
  - limited direct API use (`wbsearchentities`, `wbgetentities`, site/title mapping)
  - avoid making WDQS the critical-path dependency

- The easiest robust long-tailness strategy appears to be a small auditable bundle of heuristics:
  - DuckDuckGo top-k search on the final question
  - exact answer-string hit in result titles
  - exact or alias hit in snippets
  - exact question hit
  - optional Wikipedia pageview prior for the subject or answer

- For the first pilot, single-hop only is the safer choice.
  Reason: Route 2 already changes the evidence and phrasing strategy; adding multi-hop immediately would create too many moving parts and make it harder to isolate what improves question naturalness.
  This is my implementation suggestion, not a confirmed source claim.

## 3. Candidate Implementation Strategies

### Route 1. Wikidata-first, WDQS-light single-hop

- Reuses from the current project:
  - Wikidata client logic
  - validation scaffolding
  - output/audit structure
  - grading direction

- Changes:
  - shift critical-path retrieval from WDQS-heavy harvesting toward `wbsearchentities`, `wbgetentities`, and site/title mapping
  - allow historical years and dates under the new policy
  - rework question writing around SimpleQA-like wording instead of strict template literalism

- WDQS dependency: low

- Natural question generation:
  - hand-authored natural question families
  - optional one-shot rewrite for fluency
  - deterministic post-checks for answer leakage and unnatural wording

- Long-tailness verification:
  - DuckDuckGo top-k leakage checks
  - answer-in-title / answer-in-snippet flags
  - optional popularity prior from pageviews

- Benefits:
  - closest to the current project
  - keeps Wikidata normalization central
  - easier to audit

- Risks:
  - may still sound too template-like
  - natural wording may remain constrained by graph property structure

- Estimated implementation complexity: medium

### Route 2. Wikidata seed + Wikipedia evidence hybrid

- Reuses from the current project:
  - Wikidata normalization and validation ideas
  - answer alias handling
  - audit-focused outputs
  - grading direction

- Changes:
  - use Wikidata to identify candidate entities/facts
  - use Wikipedia-linked pages and page-native wording as the main phrasing/evidence layer
  - reduce dependence on WDQS in the online loop

- WDQS dependency: optional / near-zero on the critical path

- Natural question generation:
  - derive category wording from human-readable Wikipedia/Wikidata context
  - use compact question templates that reflect how humans refer to the subject type
  - allow a rewrite step only after deterministic content selection

- Long-tailness verification:
  - DuckDuckGo top-k leakage checks
  - answer leakage from titles/snippets
  - exact-question hit checks
  - optional pageview-based popularity prior

- Benefits:
  - strongest path toward natural SimpleQA-like style
  - preserves Wikidata-backed auditability
  - less exposed to WDQS instability

- Risks:
  - evidence extraction from page content may be messy
  - source phrasing may vary across topics
  - aligning page phrasing with a single stable Wikidata-backed fact needs care

- Estimated implementation complexity: medium

### Route 3. Search-first candidate mining with Wikidata normalization

- Reuses from the current project:
  - validation and audit ideas
  - answer alias and grading direction

- Changes:
  - candidate discovery starts from search results or curated source pages
  - Wikidata becomes a normalization/verification layer rather than the discovery layer

- WDQS dependency: none on the critical path

- Natural question generation:
  - closer to source-native phrasing
  - less graph-template pressure

- Long-tailness verification:
  - strongest by construction because the same search layer can reveal leakage immediately

- Benefits:
  - potentially very natural wording
  - minimal WDQS dependence

- Risks:
  - more normalization ambiguity
  - easier to drift away from the first-pilot requirement that Wikidata source evidence is mandatory
  - search-discovery and search-validation may become circular

- Estimated implementation complexity: medium-high

## 4. Open Questions for the Final Implementation Plan

- How strict should the DuckDuckGo leakage rules be?
  Examples:
  - reject if answer appears in any top-3 title
  - reject if answer appears in any top-5 snippet
  - reject only when both title and snippet leak

- What should count as enough Wikidata grounding for the first pilot?
  Options to decide later:
  - subject entity only
  - subject entity plus target property statement
  - subject entity plus answer entity plus supporting sitelink mapping

- For Date and Number questions, what deterministic grading policy should we aim for in v1?
  Examples:
  - exact match only
  - significance-aware numeric tolerance
  - date granularity-aware acceptance

- Should long-tailness be a hard filter in the first pilot, or only a ranking signal plus manual review field?

- Should the first pilot require Wikipedia-linked evidence for every accepted question, or is Wikidata-backed evidence sufficient even when Wikipedia phrasing is not used directly?
