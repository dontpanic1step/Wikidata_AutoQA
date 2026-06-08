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
- Mutable statuses, current roles, relationships, affiliations, and cumulative statistics are risky and should be avoided in prompts, but the shared surface guard no longer rejects them directly.
- Historically settled slices of mutable properties are allowed only when deterministic provenance shows the slice is fixed.
- Do not let disambiguation descriptors or question wording leak the answer.
- Prefer natural category names over pipeline or relation labels.
- If the answer is temporal, the question must specify the requested precision or unit, such as `what year`, `what month`, `what day`, or `how many months`.
- If the answer is a full calendar date, ask `what month, day, and year ...` for better answer normalization.
- If the answer is numeric, the question must specify the counted quantity or unit, such as `how many gallons`, and the reference answer should not include the unit.
- Avoid generic source phrasing such as `according to the table` or `according to the [source] table` in prompts; Route 3 should also avoid `in the List of ...` wording. Name the actual subject/event/list naturally. This is prompt guidance only, not a surface-rejection gate.
- Avoid cumulative-statistic questions such as how many goals Messi has scored, total wins, career points, revenue, downloads, citations, or followers unless the statistic is explicitly scoped to a historically settled slice, completed event, completed season, or fixed table/list. This is prompt guidance; the shared surface guard no longer rejects cumulative wording directly.

## Source And Route Contract

- Keep the multi-generator architecture with shared LLM rewriting and shared long-tail filtering.
- Route-specific harvesting and route-specific validation are allowed and expected.
- Route 1 is template-led and uses templates to construct candidate questions before shared rewriting.
- Wikidata grounding, Wikidata disambiguation, time-invariance checks, and Wikidata-specific dedupe are Route 1 validators that may be reused only when appropriate.
- Route 1 multi-hop scale runs use `route1_wikidata_multihop_join`: a QID-first, join-only Wikidata route. It discovers and persists QID seed units, hydrates those QIDs through Wikidata, applies stricter Route 1 validation, and then feeds candidates into the shared rewrite, DuckDuckGo, and optional second-stage grading pipeline.
- `route1_wikidata_hidden_entity_two_hop` is a disabled legacy route id. It remains only so historical artifacts can be interpreted; it should not be enabled, scaled, or updated.
- Route 4 runs use `route4_wikidata_two_hop`: a Wikidata route that composes validated single-hop facts around one hidden entity. The answer hop is `(x, r1, a)`, the clue hop is either `(x, r2, c)` or `(c, r2, x)`, and the final answer is `a`. Its default template source is the reviewed Route 4 one-hop catalog; the two-hop template catalog enumerates every ordered compatible answer/clue pair and excludes one-hop templates that cannot join on either side of the triples. Same-property pairs are skipped except for explicit place-relation chains such as `P17 -> P17` for country and `P131 -> P131` for administrative area. Object-side bridge inference is limited to human-to-human joins and place joins proven either by same-level labels or by the same place relation. Generic `Place` clue properties such as `location` do not imply every place subtype for object-side joins, and `Other` bridge rules are not inferred yet. The shared bridge/hidden entity `x` must be an entity, not a date, number, coordinate, or other literal value; date and number values may still be final answers or visible clues when their own templates are otherwise valid.
- Route 1 multi-hop joins must not use Wikipedia dumps or broad search discovery as candidate sources. Search is the downstream long-tail leakage filter, not the Route 1 candidate harvester.
- Route 1 and Route 3 intentionally have different route-local contracts. Route 1 requires deterministic Wikidata factual validation before shared filtering; Route 3 stores source provenance and relies on downstream filtering plus manual review rather than proving Wikidata-style uniqueness.
- Non-Wikidata routes must define their own validation assumptions and failure modes.
- Route 3 (`route3_wikipedia_infobox`) is Wikipedia-only, uses directly supplied Wikipedia URLs, streamed page IDs, or reused cached parsed page archives, and treats side infoboxes plus article tables as semi-structured sources.
- Route 3 URL seed files may use `domain<TAB>subdomain<TAB>url`; domains should come from the Domain Axis in `docs/template_catalog_review.md` plus `History`.
- Route 3 URL discovery should default to dump-backed discovery, not hand-prepared URL lists. Prefer raw pages-articles XML slices extracted into JSONL while preserving wikitext table/infobox markup. A Wikimedia title dump or bounded MediaWiki search may be used as a fallback, but opened pages must still be grade-filtered by parsed table quality.
- Route 3 discovery may score multiple subdomains per broad domain, then keep the best-scoring subdomain and the top URLs for that domain. This preserves the reusable Domain Axis while avoiding brittle first-subdomain-only selection on sparse dump slices.
- Route 3 stores provenance and parsed tables, but does not perform route-local factual validation beyond provenance and downstream shared checks.
- Route 3 streaming cache reuse reads already parsed archives from the configured Route 3 page archive directory. Reusable cached pages must have a positive numeric Wikipedia `page_id` and cached `parse_payload` or `parsed_html`. The optional cache-reuse used-ID file may contain page-only IDs, triadic entries, or a mixture; for this path all entries are page-level exclusions matched only by strict numeric `page_id`. Cache reuse selects `min(requested_reuse_count, reusable_cached_page_count)` pages and then sends them through the same pageview prefilter, table scoring, generation, rewrite, search, grading, and output contracts as fresh streamed pages.
- Route 3 pageview prefiltering is optional and disabled by default. Disabled runs must record explicit pageview prefilter metadata (`enabled=false`, `status=disabled`, `decision=allow`, `reason=pageview_prefilter_disabled`) and must not fetch pageviews, emit `wikipedia_pageview_prefilter_rejected`, emit `wikipedia_pageview_prefilter_unavailable`, or replace later failures with pageview placeholder reasons.
- Route 3 questions may be single fact table/infobox questions or compositional questions. New model payloads and records use `reasoning_type`; legacy `composition_type` is accepted only at compatibility boundaries.
- Route 3 prompt payloads should pass subject scope as context, not mandatory question text. Render the LLM-facing payload as concise Markdown, not as a JSON dump, with English headings `### subject_anchors`, `### table context`, and `### table content`. Each small item under those headings should use label-value lines such as `page title`: ..., `safe_subject_aliases`: ..., `section_heading`: ..., `caption`: ..., and `nearby_intro`: .... In `subject_anchors`, render `title_aliases` in place of the page title when aliases are available, and pass safe first-paragraph aliases separately as `safe_subject_aliases`. Default prompts must use the actual top table type passed to the LLM, never `wikitable or infobox`; mixed wording is allowed only when `llm_choose_table` is enabled and rendered candidate tables include both types. Wikitable prompts may include section heading, caption, and nearby intro scope guidance; infobox prompts should render only first paragraph as table context and omit wikitable-only guidance. Include `source_table` in the model output schema only when `llm_choose_table` is enabled.
- Route 3 used page-ID files may mix page-only IDs and triadic entries with `page_id`, `answer_type`, and `table_type`. A page-only entry represents an accepted QA for that page and blocks every future Route 3 context with the same page ID. A triadic entry represents a newly generated or not-yet-verified QA context and blocks only the exact same `(page_id, answer_type, table_type)` context. Incomplete scoped entries are not wildcards. Streamed generation writes triadic entries for the current run context. The triadic `table_type` must be the actual selected/used table type from the decision record, not the configured allowed table-source set; configured table-source types are only a fallback for pages that have no decision record metadata. In `all5` mode, a page-level source-stage rejection before rewrite and before any concrete answer-type slot should be represented as a page-only used entry because it invalidates the page for all answer types in that source context; slot-level and later-stage failures remain triadic. Accepted and rejected records should carry the numeric Wikipedia page ID in `source_metadata.page_id`, using the resolved parse/page-archive page ID when the input was a title URL. When the answer type and actual selected table type are known, records should also carry `source_metadata.page_id_list_entry` with `page_id`, `answer_type`, and `table_type`. Restore and inherit helpers may write either page-only or triadic outputs; accepted restore defaults to page-only unless triadic output is explicitly requested. Accepted restore reads numeric page IDs only and must not silently guess IDs from `/wiki/Title` URLs.
- Route 3 rejected placeholders represent source-stage failures before a concrete QA exists. Every reporting layer, including JSONL `rejection_reason`, compact `failing_reason`, summaries, stream states, and walkthroughs, should preserve the original source-stage reason and detail instead of replacing it with placeholder QA validation failures. For example, a pageview prefilter rejection should report `wikipedia_pageview_prefilter_rejected:monthly_average_pageviews>5000.0000`, not `shared_validation_failed:answer_in_evidence`.

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

For `route1_wikidata_multihop_join`, `source_candidate` is required before shared processing, and it must carry complete multi-hop provenance:

- `reasoning_style = multi_hop_join`
- `hop_count >= 2`
- connected `reasoning_path`
- `bridge_entities`
- `derivation_signature`
- `provenance_complete = true`
- `source_metadata.required_reasoning_clues`
- a stable QID seed key in `source_metadata.route1_qid_seed_key` when produced by the scalable runner

For `route4_wikidata_two_hop`, `source_candidate` is also required before shared processing, and it must carry:

- `reasoning_style = multi_hop_hidden_entity`
- `hop_count = 2`
- ordered `reasoning_path` with `clue` and `answer` roles
- `source_metadata.answer_hop`
- `source_metadata.clue_hop`
- `source_metadata.clue_orientation`, either `hidden_subject` or `hidden_object`
- `source_metadata.hidden_entities`
- `source_metadata.visible_clue_entities_or_values`
- `source_metadata.required_reasoning_clues`
- `provenance_complete = true`
- a stable hidden-entity seed key in `source_metadata.route4_two_hop_seed_key`

For numeric answers, store the normalized reference value without units. For temporal answers, make the question text responsible for declaring whether the expected answer is a year, month, full date, duration, or other temporal unit. Route 3 generated candidates must include a SimpleQA Verified-style `answer_type`: `Person`, `Place`, `Number`, `Date`, or `Other`.

Accepted JSONL records include the final question, answer, aliases, route, source entities, evidence, canonical and rewritten question fields, template key/domain compatibility fields, search metadata, grading metadata, validation metadata, notes, and `source_metadata`. Route 3 accepted record IDs are deterministic from the run date plus `source_metadata.page_id_list_entry`: `route3_<yyyymmdd>_p<page_id>_<answer_type>_<table_type>`, with a stable question hash suffix only when that base ID collides.

Rejected JSONL records use the same audit shape plus `rejection_reason` and `rejection_notes`. Surface-guard rejections must also expose the exact violated rule as `rejection_rule`, `rejection_notes.failure_reason`, and `source_metadata.surface_validation_failure_reason` so reviewers can distinguish failures such as `answer_leakage` or `cutoff_year_exceeded`.

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
3. Deterministic surface validation and answer normalization helpers.
4. Shared route-aware validation, including evidence-presence, available time-invariance, and route-specific deterministic checks.
5. DuckDuckGo search-based long-tail verifier.
6. Optional SimpleQA Verified-style model grading panel.
7. Duplicate subject and duplicate question checks.

Stage 1 long-tail filtering is DuckDuckGo search-based evidence. Stage 2 is optional SimpleQA-style model grading. The search verifier stores queries, result counts, titles, snippets, URLs, answer-hit flags, category hit rates, thresholds, and triggered rules.

Rule-based validation must run before both long-tail stages once a final candidate question and answer are available. Route-specific small-model output constraints, such as Route 3 allowed `reasoning_type` or `answer_type`, may run during generation before the shared flow; the shared route-aware validator then catches cross-route deterministic failures before spending DuckDuckGo or model-grading calls.

Do not use a standalone cheap-model exact-match QA phase as a rejection gate. LLMs are allowed for rewriting and optional review, but not for inventing facts, proving uniqueness, or serving as the primary factuality validator.

## Validation Contract

Shared surface validation must reject:

- missing questions
- answer leakage
- bridge entity leakage for Wikidata multi-hop candidates
- lost required reasoning clues when shortcut checks apply
- non-SimpleQA question shape
- forbidden temporal phrasing
- cutoff-year violations

Lost subject anchors are recorded as non-blocking `surface_validation_warnings` because they produced too many false positives in Route 3 pilot review.

For numeric answers, answer-leakage validation must compare extracted normalized number values from the question and reference answer rather than raw substring containment. This prevents false positives such as answer `6` being treated as leaked by the year `2016`.

Route 3 validation is intentionally limited:

- `stable_answer` is treated as true by route policy.
- `answer_in_evidence` must pass by finding the answer or alias in stored evidence text.
- `question_unambiguous` requires a subject URL.
- shared rewrite/surface guards and shared route-aware validation apply before DuckDuckGo long-tail filtering and optional second-stage grading.
- metadata names the provenance-only policy without adding placeholder validation failures.
- the incomplete tied-answer detector is retained for review but is non-blocking; Route 3 records it under `source_metadata.route_guard_warnings.wikipedia_infobox_incomplete_tie_answer`.
- default table filter modes drop matching wikitables before the Route 3 generation prompt; infoboxes first remove image rows, then remove individual key-value rows that fail incomplete-data, number-dominance, or social-science checks, and selected/rejected metadata records active modes plus removed-row audit details.

Route 1 multi-hop join validation is intentionally stricter than Route 3:

- subject and answer must be Wikidata-grounded when the answer is an entity
- answer uniqueness and time-invariance must pass before shared filtering
- subject ambiguity is resolved through Wikidata search/hydration
- multi-hop reasoning paths must be connected and provenance-complete
- bridge entities must not leak into the final question unless the template explicitly allows it
- required reasoning clues must survive rewrite so the question cannot collapse into a shortcut single-hop question
- ordinal and aggregate/count reasoning styles are excluded from the default `route1_wikidata_multihop_join` scale path

Route 4 two-hop validation reuses the Wikidata strict validation policy where it applies and adds:

- each single-hop fact must pass existing Route 1 validation before composition
- the hidden bridge entity must participate in both hops and must not be a literal date, number, coordinate, or other value
- the hidden entity label and aliases must not appear in the final question
- the visible clue must not equal or alias the answer
- all compatible non-frozen reviewed single-hop templates may be attempted, with static template-pair coverage for both hidden-subject and hidden-object clue orientations
- clue paths that map to multiple hidden entities in the validated pool are pruned before shared filtering

## Search Contract

The search verifier always includes the full final question. It uses route-provided answer-blind `search_queries` when present; otherwise it may add subject/relation fallback queries for non-special routes.

Answer hits are detected in titles and snippets using normalized answer strings, aliases, conservative country/date variants, and numeric variants or margins where applicable. Date answers are normalized before first-stage matching in the same spirit as number answers. Exact final-question hits and answer-hit rates can reject a candidate according to configured thresholds. Search queries may run with bounded per-candidate parallelism and may early-reject when a threshold can no longer be recovered.

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
- `duckduckgo_parallel_queries`: `3`
- generated search query count: `3`
- `second_stage_grading_enabled`: `true`
- search hit-rate thresholds: full question `0.3`, keyword queries `0.3`, overall `0.3`; hit rates equal to the threshold pass, and only rates above the threshold reject
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
- URL seed helper: `scripts/generate_wikipedia_table_urls.py`
- raw dump extractor: `scripts/extract_wikipedia_raw_pages.py`
- preferred URL seed source: raw page JSONL from pages-articles XML slices, with wikitext tables preserved
- fallback URL seed source: Wikimedia `enwiki-latest-all-titles-in-ns0.gz`, cached under `cache/wikipedia_dumps/`, or bounded MediaWiki search for incomplete subdomains
- Route 3 URL seed format: URL-only, `domain<TAB>url`, or `domain<TAB>subdomain<TAB>url`

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
