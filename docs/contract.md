# Project Contract

This contract summarizes the non-negotiable project rules from `AGENTS.md`, canonical terminology from `docs/terminology.md`, and the runtime contracts visible in the current pipeline code. `AGENTS.md` remains the highest-authority instruction when documents conflict.

## Goal

Build a conservative generator for SimpleQA / SimpleQA Verified-style short factual questions: natural, fact-seeking questions with one stable gold answer. The implementation method is secondary; Wikidata, Wikipedia, search APIs, and other semi-structured public sources are all acceptable when the output is auditable and stable.

Prefer high precision over high recall. Treat early pilot outputs as candidate generation, not final verified data.

## Document And Terminology Rules

- Update `docs/design.md` before implementation when it still encodes older constraints.
- Use `docs/terminology.md` for canonical terms.
- Use `template key` for identifiers such as `benchmark_release_date`.
- Use `domain` for broad content areas such as `Architecture and Transportation`.
- Normalize legacy fields at compatibility boundaries instead of spreading old terminology.
- Do not modify files under `docs/human_notes/`.
- All code comments and docstrings must be in English.

## Question Contract

- Questions must be short, natural, and fact-seeking.
- Each accepted example must have exactly one intended gold answer.
- Gold answers must be time-invariant.
- Years, dates, and temporal anchors are allowed for historically settled facts.
- By default, reject question text that depends on events in 2025 or later unless project config explicitly overrides the cutoff.
- Reject live-status wording such as `current`, `currently`, `latest`, `most recent`, and `as of now`.
- Reject mutable statuses, current roles, relationships, affiliations, and cumulative statistics by default.
- Historically settled slices of mutable properties are allowed only when deterministic provenance shows the slice is fixed.
- Do not let disambiguation descriptors or question wording leak the answer.
- Prefer natural category names over pipeline or relation labels.
- If the answer is temporal, the question must specify the requested precision or unit, such as `what year`, `what month`, `what day`, or `how many months`.
- If the answer is a full calendar date, ask `what day, month, and year ...` for better answer normalization.
- If the answer is numeric, the question must specify the counted quantity or unit, such as `how many gallons`, and the reference answer should not include the unit.

## Source And Route Contract

- Keep the multi-generator architecture with shared LLM rewriting and shared long-tail filtering.
- Route-specific harvesting and route-specific validation are allowed and expected.
- Route 1 is template-led and uses templates to construct candidate questions before shared rewriting.
- Wikidata grounding, Wikidata disambiguation, time-invariance checks, and Wikidata-specific dedupe are Route 1 validators that may be reused only when appropriate.
- Non-Wikidata routes must define their own validation assumptions and failure modes.
- Route 3 (`route3_wikipedia_infobox`) is Wikipedia-only, uses directly supplied Wikipedia URLs, and treats side infoboxes plus article tables as semi-structured sources.
- Route 3 stores provenance and parsed tables, but does not perform route-local factual validation beyond provenance and downstream shared checks.

## Candidate Schema Contract

The shared candidate shape is `GeneratedCandidate`.

Required candidate fields include:

- `source_type`
- `generation_route`
- `question`
- `answer`
- `answer_aliases`
- `subject_entity`
- `answer_entity`
- `relation_or_claim`

Important optional/audit fields include:

- `evidence`
- `canonical_question`
- `rewritten_question`
- `question_family`
- `answer_type`
- `topic`
- `target_time`
- `source_template_domain`
- `search_queries`
- `validation`
- `notes`
- `source_metadata`
- `source_candidate` for Wikidata-backed routes

For numeric answers, store the normalized reference value without units. For temporal answers, make the question text responsible for declaring whether the expected answer is a year, month, full date, duration, or other temporal unit.

Accepted JSONL records include the final question, answer, aliases, route, source entities, evidence, canonical and rewritten question fields, template key/domain compatibility fields, search metadata, grading metadata, validation metadata, notes, and `source_metadata`.

Rejected JSONL records use the same audit shape plus `rejection_reason` and `rejection_notes`.

## Metadata Contract

Every accepted or rejected example should store enough metadata to audit and regenerate it:

- source URLs or IDs
- retrieval method
- source entity IDs when available
- parsed source records or table snippets when applicable
- query strings
- search result titles, snippets, URLs, hit flags, and rejection rules when allowed
- answer aliases
- generation route
- route-local failure notes
- validation, search, and grading evidence
- per-phase timings when the route records them

Record query, search, harvesting, and validation failures for review.

## Filtering Contract

Do not use internal popularity proxies such as Wikidata sitelink count or claim count as first-stage long-tail rejection gates.

The shared filtering flow is:

1. Route-local early rejection notes.
2. Optional LLM rewrite or route-provided final question.
3. Deterministic surface validation.
4. DuckDuckGo search-based long-tail verifier.
5. Optional SimpleQA Verified-style model grading panel.
6. Shared route-aware validation.
7. Duplicate subject and duplicate question checks.

Stage 1 long-tail filtering is DuckDuckGo search-based evidence. Stage 2 is optional SimpleQA-style model grading. The search verifier stores queries, result counts, titles, snippets, URLs, answer-hit flags, category hit rates, thresholds, and triggered rules.

Do not use a standalone cheap-model exact-match QA phase as a rejection gate. LLMs are allowed for rewriting and optional review, but not for inventing facts, proving uniqueness, or serving as the primary factuality validator.

## Validation Contract

Shared surface validation must reject:

- missing questions
- lost subject anchors
- answer leakage
- bridge entity leakage for Wikidata multi-hop candidates
- lost required reasoning clues when shortcut checks apply
- mutable fact wording
- non-SimpleQA question shape
- forbidden temporal phrasing
- cutoff-year violations

Route 3 validation is intentionally limited:

- `stable_answer` is treated as true by route policy.
- `answer_in_evidence` must pass by finding the answer or alias in stored evidence text.
- `question_unambiguous` requires a subject URL.
- shared rewrite/surface guards still apply.
- metadata records `route_local_factual_validation` as false and names the provenance-only policy.

## Search Contract

The search verifier always includes the full final question. It uses route-provided answer-blind `search_queries` when present; otherwise it may add subject/relation fallback queries for non-special routes.

Answer hits are detected in titles and snippets using normalized answer strings, aliases, conservative country/date variants, and numeric variants or margins where applicable. Exact final-question hits and answer-hit rates can reject a candidate according to configured thresholds.

## Grading Contract

The optional second-stage grading panel asks answer models the final question, then grades predictions as:

- `CORRECT`
- `INCORRECT`
- `NOT_ATTEMPTED`

The grader may use deterministic alias matching, deterministic numeric margins, or a configured LLM grader. Accuracy above the configured threshold rejects a candidate as too easy for the selected model panel.

## Runtime Defaults From Code

General settings currently default to:

- `cutoff_year`: `2025`
- `duckduckgo_top_k`: `10`
- `second_stage_grading_enabled`: `true`
- search hit-rate thresholds: full question `0.0`, keyword queries `0.3`, overall `0.3`
- second-stage accuracy threshold: `0.1`  
- default second-stage answer models: `openai/gpt-4.1-mini`, `google/gemini-3-flash-preview`
- default grader: `openai/gpt-4.1-mini`
- OpenRouter key environment variable: `OPENROUTER_API_KEY`
- default proxy: `socks5://127.0.0.1:7897`
- default cache directory: `cache/wikidata`

The Wikipedia infobox/table runner currently defaults to:

- script: `scripts/run_wikipedia_infobox_pipeline.py`
- repeated `--url` and optional `--url-file`
- `--record-limit 10`
- one QA attempt per URL
- small model: `openai/gpt-4.1-mini`
- small-model provider/base URL: OpenRouter at `https://openrouter.ai/api/v1`
- outputs under `outputs/wikipedia_infobox_*`

## Network And Secrets Contract

Network runs with batch size <= 10 examples, URLs, or records do not require advance permission; run them when needed for the task, including Wikipedia, Wikidata, search API, and OpenRouter calls.

Ask before:

- network-heavy runs above batch size 10
- installing dependencies
- destructive actions
- credential changes
- secret-handling changes

Do not commit or print secrets. Read API keys from environment variables.

## Implementation Contract

- Start with a small end-to-end vertical slice before adding breadth.
- Add tests for validators and grading rules before scaling.
- Keep outputs metadata-rich and auditable.
- Prefer general solutions over one-off patches.
- Preserve unrelated worktree changes.
- Do not revert user changes unless explicitly asked.
