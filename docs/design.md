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

All route rewrite prompts must make answer normalization explicit. If the answer is temporal, the question should specify the requested precision or unit, such as `what year`, `what month`, `what day`, or `how many months`. If the answer is a full calendar date, the prompt should prefer wording like `what month, day, and year ...`, and the reference answer should use a month-first format such as `May 20, 2024`; month-level answers should use a format such as `May 2024`. If the answer is numeric, the question must state the counted quantity or unit, while the reference answer and answer aliases should remain unit-free normalized values.

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

- deterministic shared validation runs before both long-tail stages, after generation/rewrite has produced the candidate question and answer. This includes surface checks, answer-in-evidence checks, available time-invariance checks, and route-specific small-model output constraints such as configured Route 3 answer-type restrictions, so invalid candidates do not spend DuckDuckGo or model-grading calls
- search checks whether the answer is exposed too directly in public retrieval
- model grading checks whether configured answer models solve the question too reliably

There is no standalone cheap-model exact-match QA rejection gate. SimpleQA Verified uses autorated model answers for difficulty/evaluation rather than a separate cheap-model long-tail rejection phase, so model-answer judgment belongs in the grading panel.

DuckDuckGo filtering uses normalized answer matching over answer labels and aliases. It normalizes case, punctuation, common number forms, common date forms, and common country aliases where applicable. Search-result title hits and snippet hits are thresholded evidence signals, not unconditional rejection rules; setting thresholds to `1.0` intentionally lets candidates pass stage 1 for walkthrough/debug runs.

DuckDuckGo transport should prefer the maintained `ddgs` package when it is installed. The shared search client attempts `ddgs` first, using `backend="auto"` by default and two bounded attempts. Production or probe environments that use DuckDuckGo search should install both `ddgs` and `PySocks`: `ddgs` provides the primary search backend, while `PySocks` keeps the legacy urllib SOCKS proxy path usable when a `socks5://...` proxy is configured. If `ddgs` is unavailable or fails, the client may fall back to the legacy HTML/Lite implementation unless that fallback has been disabled for diagnosis.

DuckDuckGo retry behavior is intentionally narrow. Retries are for transient search-service jitter, rate limiting, or anti-bot holding responses, not for short-window bulk repetition of the same failing request. The HTML endpoint switches immediately to `lite.duckduckgo.com/lite/` on HTTP 202 without retrying the HTML endpoint. Lite holding/rate-limit/transient transport failures may get only a small bounded backoff retry. A direct fallback is meaningful only after a configured proxy path fails; no-proxy direct searches must not run an equivalent `direct_fallback` pass. Diagnostic runs may disable fallback families (`ddgs`, legacy HTML/Lite, Lite, or direct fallback) to isolate which path is failing, but normal runs leave every fallback enabled. Attempt diagnostics should record endpoint switches, retry reasons, path changes, backend choice, proxy use, and whether `ddgs` or legacy fallback handled the request so search failures remain auditable.

DuckDuckGo cooldown is global within the process. Consecutive DDG HTTP 202/403 responses or transport failures should trigger a minute-level shared cooldown before later DDG attempts continue; the cooldown should also count a request whose final result succeeds through fallback if the earlier DDG attempts were throttled or transport-failing. A plain `ddgs` "No results found" response is a query/backend outcome, not a transport failure, and must not by itself trigger cooldown.

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

Route 3 is a Wikipedia-only route for semi-structured public data. It starts from directly supplied English Wikipedia URLs or streamed page IDs, fetches the page through the MediaWiki API, extracts the page title, any first paragraph available in the already-fetched `action=parse` HTML, and structured infobox/table content, then asks a small model to propose table-grounded SimpleQA-style questions. REST summary fetching is an explicit opt-in fallback only; it is off by default so a missing paragraph does not add another network failure point.

Route 3 stores a unified per-page archive under the configured Route 3 page archive cache. The archive is a single JSON document per page containing the source URL, resolved page ID, title, canonical URL, parse API URL, raw parse payload, parsed HTML, first paragraph, prose text, extracted infobox/wikitable metadata, optional pageview request/response payloads, computed pageview metrics when present, timestamps, content hashes, and fetch errors. Generation reads this archive first and only fetches missing parse fields, plus missing pageview fields when the optional pageview prefilter is enabled, before writing fresh/generated archive state back. Cached-archive stream reuse treats the selected source archive as read-only: missing first-paragraph or pageview metadata may be computed for the current record, but the original archive file must not be rewritten. Accepted and rejected records must store enough archive metadata to reopen the archived page state, including the archive path, cache-hit status, archive hash, parse fetch status, pageview prefilter status, and whether the source archive was read-only.

Streaming Route 3 may also reuse already parsed page archives from the configured page archive cache instead of first discovering fresh page IDs and fetching Wikipedia. A cached archive is reusable when it has a positive numeric Wikipedia `page_id`, a stored parse payload or parsed HTML, and that numeric page ID is absent from the optional used-ID JSON supplied for cache reuse. The used-ID JSON may be a helper-generated page-only list, triadic `page_id`/`answer_type`/`table_type` list, or a mixture; cache reuse treats every entry as a page-level exclusion and matches by strict numeric `page_id` only, without context-scoped triadic matching. The selected reuse count is `min(requested_reuse_count, reusable_cached_page_count)`. Reused archives enter at the parsed-page boundary and then use the same pageview prefilter, table cleanup, table scoring, LLM generation, rewrite, search, grading, output, and page-ID summary paths as freshly streamed pages, but do not write parse, table, first-paragraph, or pageview updates back into the reused archive. Output metadata must mark the streaming page source as cached archive reuse and preserve the archive path.

The Route 3 pageview popularity prefilter is optional and disabled by default. When disabled, Route 3 records explicit disabled metadata (`enabled=false`, `status=disabled`, `decision=allow`, `reason=pageview_prefilter_disabled`) and continues to table grading and LLM generation without fetching pageviews or creating pageview rejection placeholders. When enabled, the prefilter runs before table grading and before any generation LLM call. The pageview signal is the average monthly views over the most recent 12 complete months, using Wikimedia pageview data. Pages with all 12 months observed and an average above `5000` monthly views are rejected as too popular before table grading. If fewer than 12 months are available, Route 3 falls back to a single-month pageview rule: any observed month above `10000` views rejects the page, otherwise the page is allowed while recording the underfilled-window decision. If pageview data is missing or the pageview request fails while the prefilter is enabled, the default policy is to allow the page through while recording the full unavailable/error status, request details, and retry decision in every output record derived from that page, and in the page archive only when the archive is not a read-only cached-reuse source.

Route 3 may ask table reasoning questions such as max/min/sum/count/comparison questions over structured rows, and may ask temporal ordinal questions such as which entity was first or second by date/order of occurrence. Ordinal reasoning is not magnitude ranking such as largest or second largest; use max/min for magnitude comparisons. It may also ask single fact questions when the answer is historically settled, cannot change, and the downstream long-tail filters judge it suitably obscure. By default, Route 3 restricts generation to `single_fact` and passes that value through without asking the model to output a `reasoning_type` field; runs with multiple allowed reasoning types ask the model to choose one and reject outputs whose declared `reasoning_type` is outside that configured list. Legacy artifacts may still contain `composition_type`; loaders normalize that field to `reasoning_type` at the compatibility boundary. The route may use first-paragraph aliases to avoid unsuitable temporal wording, such as asking about the `23rd FIFA World Cup` instead of using the page title `2026 FIFA World Cup`.

Route 3 may emit complete list answers when a table reasoning operation has a tie. The display `answer` remains a string for shared JSONL compatibility, while `source_metadata.answer_items` stores the individual answer elements. For these list answers, search leakage is counted only when every answer element appears in the same result title or snippet, and SimpleQA-style grading treats partial lists as incorrect.

Before prompting the model, Route 3 separates infoboxes and wikitables into source-specific grading channels. Each channel applies its own filters, ranking, and prompt builder from table grading through the generation prompt. The current infobox and wikitable prompt builders intentionally start as near-copies of the older shared Route 3 prompt, with only source-shape wording changed, so future prompt tuning can edit them independently. When both source types are enabled, the runner chooses the best surviving channel/table for the generation prompt and does not mix infoboxes and wikitables in one prompt.

Route 3 ranks extracted tables inside each source-specific channel. Prefer tables with useful subject/list context and row values that are not repeated in non-table prose; table type alone must not prioritize wikitables over infoboxes, and row count is no longer used to add or subtract ranking score. When ranked tables have the same score, choose infoboxes first, then the table with lower prose-leakage rate; row count must not participate in tie-breaking. Prose-leakage scoring is a configurable lightweight rank signal: by default leakage below `0.2` adds `0.5` points, leakage above `0.8` subtracts `0.5` points, and disabling the signal keeps leakage audit stats without changing table scores. Single-mode runs that explicitly restrict generation to exactly one answer type add shared wikitable/infobox answer-type hint bonuses during table ranking: `Person` adds `1.0` when table text has two adjacent initial-capitalized non-common words, `Place` adds `2.0` when table text contains a seeded place-category marker, and `Date` adds `2.0` when table text contains a month name, a no-comma four-digit year from 1500 through 2040, or a numeric month/day/year marker such as `3/6/2026` or `3-6-2026`. These bonuses do not apply to `all5` generation or to runs with no answer-type restriction or multiple allowed answer types.

The table extractor suppresses `script`/`style` text such as `.mw-parser-output` CSS noise, expands `rowspan` and `colspan` into a rectangular grid, combines multi-row headers into Markdown column labels, preserves blank cells, and records image-row and key-value-row indexes for later infobox cleanup; the older header-to-row-dictionary parser is disabled. A page may contribute at most one article-level infobox: only the first `infobox`-class table can qualify, it must start within the lead-page character threshold, and its caption or first visible row text must exactly match the page title after removing parenthetical disambiguation. When the first visible row provides that title, the extractor promotes it to the table caption so the title is not rendered as an ordinary data row. Tables with more than 40 parsed rows, more than 2500 Markdown characters, or two or fewer total parsed rows including title/header rows are rejected before any generation prompt. Numeric/comparable-value bonuses such as capacity/rank/count/date/votes fields are kept in code behind disabled switches for possible reuse, but they should not affect current page or table grading. Penalize oversized prose-like tables, placeholder/mutable tables such as live standings, and tables whose row values are already easy to recover from article text. A run may configure source table types as `infobox`, `wikitable`, or both; both are enabled by default.

Default early table filter modes drop unsuitable tables before any generation prompt. `no_external_links_tables` rejects External links-style sections. `no_horizontal_companion_tables` rejects small wikitable companion tables that are marked by HTML layout as horizontally adjacent to another such table under the same heading, while preserving the following normal vertical data table. Wikitables keep table-level quality filters: `no_picture_heavy_tables` rejects any wikitable with an image-bearing cell, `no_incomplete_tables` rejects incomplete/approximate/citation-needed table text, `not_number_dominant` rejects big-number-heavy or low-alpha table text, and `no_social_science_research` rejects table text with social-science markers such as `census`, `survey`, `demographic`, `self reported`, `ancestry group`, `ethinic group`, `ethinicity`, `population`, or `language speaker`. Infoboxes are cleaned before ranking and prompt construction instead of applying those three content filters globally: image-bearing infobox rows are removed together with precise media-caption rows such as `infobox-caption` and media title rows such as a `Signature` header immediately followed by a signature image; each remaining key-value row is checked against `no_incomplete_tables`, `not_number_dominant`, and `no_social_science_research`, and failing rows are removed. The image cleanup must not treat every full-width row adjacent to an image as a caption: when a row lacks a clear caption class or a narrow media-title signal, keep it so section headings for subsequent key-value rows, such as a heading before `Location`, are not accidentally dropped. The resulting infobox is rejected before ranking if cleanup removes more than `60%` of non-header rows or if fewer than `5` non-header rows remain. Store the ranking criteria, scores, cutoff, source types, source channel, filter modes, matched markers, removed infobox-row metadata, removal-rate decision, remaining-row decision, and cutoff/filter decisions as metadata so table choice can be audited.

A configurable `min_table_score` cutoff drops ranked tables before first-paragraph alias/context extraction and before the Route 3 generation prompt; the default cutoff is `0.0`. If no table survives the source-type restriction, size/row-count filters, score cutoff, live-scope filter, and enabled table filter modes, the page is rejected before any generation call. By default, `llm_choose_table` is disabled and only the single top-ranked surviving table is passed to the small model with table-choice prompt text omitted. When `llm_choose_table` is enabled, the top three surviving ranked tables are passed with table-choice instructions.

Route 3 prompt wording and rendered payload context must follow the actual table type passed to the small model. Default top-table prompts use that table's actual `table_type` and must not describe the source as `wikitable or infobox`; mixed wording is allowed only when `llm_choose_table` is enabled and the rendered candidate tables actually include both source types. The LLM-facing payload is rendered as concise Markdown rather than `json.dumps`, using English headings `### subject_anchors`, `### table context`, and `### table content`. Each small item under those headings uses label-value lines such as `page title`: ..., `safe_subject_aliases`: ..., `section_heading`: ..., `caption`: ..., and `nearby_intro`: .... `subject_anchors` renders `title_aliases` in place of the page title when aliases are available, while preserving `safe_subject_aliases` as a separate labeled line. Wikitable prompts render `first_paragraph`, `section_heading`, `caption`, and `nearby_intro` in `table context`; infobox prompts render only `first_paragraph` there. Table Markdown is always separated under `table content`. Audit metadata remains full and unchanged; this Markdown rendering controls only what is passed to the LLM. The model output schema includes `source_table` only when `llm_choose_table` is enabled, because default prompts already pass exactly one evidence table and can resolve old responses by falling back to that table.

After rewriting and post-rewrite surface checks, but before DuckDuckGo long-tail filtering, the shared pipeline applies deterministic post-rewrite guards and a rule-based answer-type gate for `Person`, `Place`, and `Date` candidates. Route 3 rejects exact popular answers such as `United States`, `China`, continent and ocean names, major city names, major language names, `male`, and `female` with precise failure reasons of the form `answer_too_popular:<answer>`. A separate post-rewrite answer-scope ambiguity gate rejects vague answer-range wording such as `meaning` and `genre` with failure reasons of the form `post_rewrite_answer_scope_ambiguous_phrase:<marker>`. The answer-type gate mirrors the standalone rule-gate script: `Person` rejects answers dominated by common non-name words after counting at most two name particles such as `al`, `el`, `bin`, `ibn`, `bint`, `abu`, `abd`, `ap`, `af`, `mac`, `mc`, `von`, `van`, `der`, `di`, and `de` as name tokens when they appear medially, with a smaller conservative subset also allowed at the beginning of a multi-token name, `Place` extracts an explicit place category from the final question and checks it against a seeded whitelist, and `Date` requires a standard or normalizable date answer and may normalize the answer while retaining the original as an alias for evidence checks. Rejections are recorded as `rule_based_answer_type_gate_rejected`.

For large Route 3 recipes, use big-batch mode so transient table-search discovery failures are retried instead of silently ending a segment, the stream batch size matches the MediaWiki search page size, and existing segment summaries are only reused when the segment actually used its requested page budget. Big-batch mode must not compact accepted or rejected JSONL records; all Route 3 outputs are full audit records in every mode. Page-fetch HTTP 429 responses from Wikipedia should trigger a shared polite backoff across Route 3 Wikipedia workers before new page fetch attempts continue; the backoff should grow while 429s continue and reset after a quiet recovery window. Production top-up runs should use append mode, which creates new segment artifact names, appends combined outputs instead of overwriting them, and seeds the shared recipe page-ID exclusion file from existing recipe summaries and stream states before discovering more pages. Top-up segments should first seed and process the rerun pool from prior states of the same answer-type segment, then discover fresh pages only when more IDs are needed; if a top-up reaches its target while seeded rerun IDs remain, clear those unresolved seeded IDs from the active rerun pool and free undecided page IDs so later discovery is not blocked by abandoned retries.

Route 3 page-ID list maintenance is handled by explicit helpers rather than manual editing for production runs. Used page-ID lists may mix legacy page-only entries and triadic entries with `page_id`, `answer_type`, and `table_type` (`infobox` or `wikitable`). A page-only entry means an accepted QA already exists for that page and blocks every future Route 3 context for the same page. A triadic entry means a newly generated or not-yet-verified QA context and blocks only the exact same `(page_id, answer_type, table_type)` context. Streamed generation writes triadic entries for the current run context, but must skip a candidate page when the list already contains either the same page-only ID or the exact same triadic entry. The `table_type` in a triadic entry must be the actual table type used by the generated or rejected decision record, not merely the configured set of allowed table types; only records with no decision metadata may fall back to configured table-source types. In `all5` mode, when a page is rejected before rewrite by a page-level source-stage failure and no concrete answer-type slot exists, streamed summaries should write a page-only entry because that page failed for all answer types in the current table-source context; slot-level failures and later-stage failures continue to write the default triadic context entries. Incomplete scoped entries are not treated as wildcards. Accepted and rejected Route 3 records should persist the numeric Wikipedia page ID in `source_metadata.page_id`; if the input URL is a title URL, the resolved `action=parse` page ID or page-archive metadata should backfill this field. When `page_id`, answer type, and actual selected table type are all known, accepted and rejected records should also store the explicit triadic object in `source_metadata.page_id_list_entry`. A helper may inherit an existing page-ID list into a new exclusion file, release entries by subtracting the entries represented by a run artifact directory from an existing list, or restore IDs from past accepted JSONL records. Inherit and accepted-restore helpers can write either page-only or triadic output; accepted restore defaults to page-only unless triadic output is explicitly requested. Accepted restore reads numeric page IDs from records and does not infer page IDs from `/wiki/Title` URLs, because title-to-ID lookup is a separate resolver step and should not be guessed silently. Directory-based release reads segment summaries, stream states, and accepted/rejected JSONL records; it does not use raw `used_ids` by default because those may include inherited external exclusions rather than pages actually consumed by the directory. Final release selection is expected to enforce one accepted record per `page_id`, and accepted page IDs should usually be represented as page-only entries in used page-ID lists.

Route 3 rejected placeholders are metadata carriers for source-stage failures, not QA attempts. If a page is rejected before a concrete QA is generated, downstream processing, summaries, compact review fields, stream-state failure reasons, and walkthroughs must report the original source-stage reason plus its metadata detail, such as `wikipedia_pageview_prefilter_rejected:monthly_average_pageviews>5000.0000`. Later placeholder validation failures, such as an empty answer failing `answer_in_evidence`, must not replace the original failure reason at any reporting layer.

The Route 3 small-model prompt emits `answer_type` using SimpleQA Verified-style categories: `Person`, `Place`, `Number`, `Date`, and `Other`; `Other` means the answer is not one of the first four types. A run may optionally restrict generation to one or more allowed answer types, and Route 3 rejects model outputs whose declared or normalized `answer_type` is outside that configured list. If exactly one `reasoning_type` is configured, the model output schema omits `reasoning_type` and Route 3 writes the configured value directly into candidates and metadata; only unrestricted or multi-reasoning runs ask the model to choose and output `reasoning_type`. In the default `single` answer-type mode, the prompt returns one candidate, preserving legacy JSON shape. In `all5` mode, one prompt returns a single JSON object whose `outputs` array contains exactly five fixed answer-type slots in this exact order: `Person`, `Place`, `Number`, `Date`, and `Other`. Each all5 slot's `answer_type` must equal the slot name. If the current table cannot support a class such as `Person`, only that slot should be discarded with `discard_reason` and empty question/answer/search fields; supported classes should still produce their own slots. Generated slots are accepted or rejected independently while sharing the same page archive, source table, prompt, and full model response audit. Route 3 answer-type inference treats temporal-answer questions with year/date/month/day/when wording as `Date` when the answer looks temporal, including era-qualified years such as `401 BC` or `402 BCE`, even if the model declared `Number`. The prompt follows the shared answer-normalization wording rule: temporal questions must name the requested precision, full-date answers should be requested as month, day, and year, and numeric questions must put the unit or counted quantity in the question rather than in the reference answer. Route 3 answer postprocessing removes footnote markers but does not split parenthetical answer text into aliases; if the model returns `Foo (Bar)`, that full string remains the reference answer. Pure rank-like aliases such as `#1` or `1st` are preserved when the model explicitly returns them. The prompt passes `subject_anchors` as page/table scope hints rather than required wording. These hints include the page title or title-derived aliases, safe first-paragraph aliases, and selected table context rendered as labeled Markdown lines rather than JSON. Wikitable-only guidance about subject-anchor copying, curated list pages, toy/tutorial tables, and caption/nearby-intro/section-heading scope is omitted from infobox-only prompts. Metadata-level `subject_anchor_aliases` use a fixed 2025 cutoff for compatibility with existing Route 3 artifacts, while the generation prompt and `subject_anchors` context continue to use the configured run `cutoff_year`. The model should use the scope hints to understand scope, for example that `15 largest commercial banks` supports asking which bank is largest within that table but not how many banks exist in Ukraine.

Route 3 outputs are never compacted. Even in big-batch mode, accepted and rejected records must preserve the full parsed source metadata, table-selection metadata, prompt, sanitized LLM request payload, full OpenRouter response body when available, raw assistant text, parsed model JSON, shared rewrite prompt/response when enabled, DuckDuckGo evidence, optional grading evidence, and page archive/pageview audit metadata. Accepted Route 3 record IDs should be deterministic from the run date plus the triadic page-ID record, using `route3_<yyyymmdd>_p<page_id>_<answer_type>_<table_type>` and adding a stable question hash only if that base ID collides. `--compact-output` and `--compact-rejected-output` are deprecated for Route 3 and must be ignored rather than changing the JSONL record shape.

Route 3 and shared rewriting prompts should avoid generic provenance phrasing such as `according to the table` or `according to the [source] table`, and Route 3 specifically should avoid `in the List of ...` wording. The question should name the actual subject, event, chart, list, or scope naturally. `According to ...` wording is preferred only for well-known named charts or lists such as Billboard charts or UNESCO lists. This is prompt guidance; the shared surface guard does not reject the wording directly.

Route 3 prompts may accept extra stricter prompt rules as literal text. Extra prompt rules are stored in metadata and also passed into the shared rewrite prompt so rewriting does not weaken the stricter run contract. The former `NO_SOCIAL_SCIENCE_RESEARCH_PROMPT` behavior is now represented by the default `no_social_science_research` table filter mode rather than prompt-only guidance.

Route 3 URL discovery should be a separate, auditable step. It should not default to hand-prepared URLs, because those bias pilots toward short-tail facts. Two discovery modes are supported:

- dump-backed discovery, which reads raw pages-articles XML slices extracted to JSONL while preserving wikitext table and infobox markup, scores candidate pages inside the Domain Axis from `docs/template_catalog_review.md` plus `History`, then opens and grades a bounded number of candidates with the same parsed-table quality scorer used by Route 3
- page-id streaming discovery, which first asks the MediaWiki search API for namespace-0 pages likely to contain tables. The default query set is deliberately narrow: `insource:"wikitable"` only. The broader-and-slower `insource:/\{\|/` query is an explicit opt-in for exploratory runs, not a default. Each discovered page ID then runs through `action=parse&pageid=<id>&prop=text|displaytitle` and the existing Route 3 page parsing, small-model generation, rewrite, validation, long-tail filtering, and optional grading pipeline. Raw random page IDs inside configured bounds remain an explicit fallback/probing mode, but are no longer the efficient default.

WikiExtractor-style plain-text extraction is not suitable for dump-backed discovery because it flattens away the table structures needed for source discovery. A cached Wikimedia title dump or bounded MediaWiki search can supplement sparse subdomains, but final URL choice must still come from table-quality grading.

For sparse pilot slices, dump-backed discovery may evaluate more than one subdomain per broad domain and then keep only the best-scoring subdomain plus the top URLs for that domain. This preserves the "one subdomain per domain" pilot shape while avoiding a brittle dependency on whichever subdomain appears first in the catalog plan. The URL file preserves `domain<TAB>subdomain<TAB>url` rows so accepted examples can report both source URL and source domain.

Page-id streaming discovery temporarily does not require broad domains or subdomains. Domain/subdomain requirements and reports must be treated as optional in this mode so otherwise valid QAs are not rejected only because a page did not arrive from a planned domain bucket. Streaming runs keep a persistent page-id state file with used IDs, in-progress IDs, accepted IDs, rejected IDs, table-search offsets, and a rerun pool. Recipe runs use a separate stream-state file and rerun pool per answer-type segment so transient failures from one segment do not consume the runtime budget of another segment. Fresh IDs are added to the used cache before processing so they are not sampled twice. IDs left in progress by a crash are moved to the rerun pool at the next startup, and caught per-page pipeline exceptions also move the page ID to the rerun pool instead of marking it accepted or rejected. When `--stream-random-seed` is omitted, streaming derives a deterministic seed from the run and segment identity rather than reusing a fixed global default; explicit seeds remain available for exact reproduction. Recipe append/top-up runs keep using the same shared page-ID exclusion file, but initialize it as a superset of prior segment summaries and stream-state used IDs so later segments and later invocations do not rediscover already attempted pages.

Streaming runs should write accepted and rejected JSONL records incrementally after each page decision. A scale-oriented batch target is roughly 2,000 sampled page IDs, about 1,000 accepted candidate QAs before final cleanup, then similarity-based deduplication and domain rebalancing down to roughly 300 final review candidates. Because streaming mode is domain-optional, domain rebalancing is best-effort: it uses any available `domain` or source metadata buckets, and otherwise falls back to a single Wikipedia semi-structured bucket.

Scale runs should process page IDs through a page-level worker pool with separate service semaphores for Wikipedia, DuckDuckGo, generation/rewrite OpenRouter calls, and second-stage OpenRouter calls. Accepted/rejected JSONL appends and stream-state updates are one locked commit unit per page so a crash does not split a decision from its page-ID state. Second-stage grading should run panel answer models in parallel, grade the executed predictions in one batched grader call when a grader is configured, and skip remaining panel models when the first answer is already correct enough to reject under the current accuracy threshold.

Long-running Route 3 jobs should be restartable from endpoint files. When endpoint resume is enabled, existing accepted/rejected JSONL outputs are treated as the checkpoint: streaming runs sync page-ID state from those records and process only the remaining requested total, while URL-list runs skip completed source URLs and append new decisions instead of overwriting prior endpoint data. Malformed trailing JSONL lines left by a crash are skipped and reported in the run summary rather than blocking resume. Fresh streaming runs may explicitly reset the stream-state file at startup. Reruns should be first-class rather than relying on manual record-limit arithmetic: a rerun-pool-only invocation processes the current rerun pool without discovering fresh page IDs, and a normal streaming invocation may optionally perform exactly one immediate rerun-pool pass after the main pass. If that one rerun pass still leaves IDs unresolved, the runner stops and preserves the remaining rerun pool for later review or another explicit rerun.

Resumed Route 3 jobs should use a stable run-group ID and one segment ID per invocation. When a run group is set, each summary updates a small manifest that indexes the accepted JSONL endpoint, rejected JSONL endpoint, summary files, walkthrough files, and stream-state files for all known segments in that group. New records should carry the run group and segment in `source_metadata` so later review can filter appended records without relying only on filename conventions.

Route 3 table prompts should include the immediate paragraph before a table as `nearby_intro`, especially because intros containing terms such as `following` or `above` often define row inclusion or exclusion. This is a cheap parser-side context addition, not a broad prose retrieval step. Tables whose caption, section heading, or nearby intro contains live-scope terms such as `current`, `active`, `incumbent`, `present`, or `latest` should be filtered out before the Route 3 generation prompt; if no safe tables remain, the page should be rejected before any generation call. The prompt should also discourage unclear answer categories, for example questions phrased as `What equipment ...`, and require domain-specific category wording.

Route 3 does not perform factual validation or uniqueness proof. Its conservative contract is auditability: accepted and rejected outputs must store the source URL, canonical page title, first paragraph, parsed table metadata, pageview prefilter metadata or evidence, model derivation summary, generated search queries, downstream DuckDuckGo evidence, optional grading evidence, and phase timings. Shared deterministic validation runs before DuckDuckGo and optional grading; Route 3-specific small-model output checks such as configured reasoning-type and answer-type restrictions happen during generation before shared processing. Because the route has no Wikidata grounding, shared processing must not require a Wikidata `source_candidate` for Route 3 candidates. Route 3 validation metadata may record that it uses a provenance-only route policy, but placeholder boolean failures such as `route_local_factual_validation: false` must not appear in validation dictionaries or failing-reason summaries.

### 3.8 Route 3 final QA cleanup

After Route 3 long-tail filtering and before final release selection, run an answer-type matching gate. The gate is deterministic where practical: `Person` flags answers whose tokenized words are at least 50% common English words after subtracting common given-name and surname lists, counting at most two name particles such as `al`, `el`, `bin`, `ibn`, `bint`, `abu`, `abd`, `ap`, `af`, `mac`, `mc`, `von`, `van`, `der`, `di`, and `de` as name tokens when they appear medially, with a smaller conservative subset also allowed at the beginning of a multi-token name, and applying conservative exceptions for monarch-style names whose prefix has no common non-name markers and whose suffix is either a Roman numeral or `the` plus one capitalized epithet word; `Place` checks the question's requested category against a broad geography whitelist seeded from SimpleQA Verified place questions and manually maintained geography terms; `Date` accepts year-only, month-year, and full-date answers, normalizes parseable numeric date forms to month-first text, and rejects ranges or vague eras. `Other` and `Number` currently have no deterministic gate. Matched records continue to final LLM filtering, while mismatched records are stored separately for later manual review instead of being discarded.

The final LLM QA judge is a standalone review phase over accepted Route 3 JSONLs. It receives the question, answer, aliases, answer type, page title, first paragraph, and every stored parsed Markdown table with table index, section heading, caption, and nearby intro. It judges four fixed rubrics: whether the answer is derivable from the supplied context, whether the answer is unique and stable, whether the question is self-contained, and whether the question asks for the declared answer type. It also assigns one topical domain from the fixed SimpleQA Verified-style domain set. Judge responses retain per-rubric reasons for audit, but do not store an `overall_reason`.

Final review may manually edit questions and recover records whose only final-judge failure is answer-type mismatch. Recovered records must be copied into the appended `passed_all` JSONLs under their corrected answer type, preserving the original judge metadata and adding manual move metadata that records the original answer type, target answer type, source mismatch file, and reason for recovery. These appended JSONLs are the source of truth for later final-set balancing.

The final release candidate set should be rebalanced against SimpleQA Verified answer-type and topical-domain distributions. When the available data cannot satisfy both distributions exactly, answer-type quotas are treated as hard constraints and domain balancing is constrained by availability. Scarce domains are kept first; overrepresented domains are downsampled within answer-type/domain buckets using a fixed random seed and stable source ordering. Each selected record should carry enough selection metadata to reproduce the sample, including source file, source line, answer type, domain, quota, seed, and selection method.

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
- for multi-hop join scale runs, use QID-first seed units rather than Wikipedia dumps or broad search discovery; hydrate those QIDs through Wikidata and then pass validated candidates into the shared downstream pipeline

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

Route 1 multi-hop join scale runs use a stricter QID-first variant:

```text
Route 1 QID seed discovery
  -> persistent QID seed state and endpoint resume
  -> Wikidata hydration and template-led multi-hop join construction
  -> Route 1 validators before rewrite
  -> shared LLM rewrite + query generation
  -> shared DuckDuckGo long-tail filter
  -> optional shared SimpleQA Verified-style model grading
  -> shared recording and final selection
```

This variant is identified as `route1_wikidata_multihop_join`. It reuses the shared DuckDuckGo, rewrite, second-stage grading, phase-timing, and output contracts that Route 3 exercises at scale, but keeps Route 1's stricter Wikidata grounding, disambiguation, time-invariance, uniqueness, bridge-leakage, and shortcut validation before the shared filters. Route 1 multi-hop discovery should not use Wikipedia dumps or heavy search as candidate sources; search is reserved for downstream long-tail leakage filtering.

The former Route 1 hidden-entity two-hop variant is disabled. The route id
`route1_wikidata_hidden_entity_two_hop` remains only for historical artifact
compatibility and should not be enabled, scaled, or updated.

Route 4 now owns the hidden-entity two-hop design:

```text
Route 4 single-hop template harvest
  -> strict Wikidata validation for each single-hop fact
  -> compose answer hop `(x, r1, a)` with clue hop `(x, r2, c)` or `(c, r2, x)`
  -> prune ambiguous clue paths and answer/clue leakage risks
  -> shared LLM rewrite from structured hop facts
  -> shared DuckDuckGo long-tail filter
  -> optional shared SimpleQA Verified-style model grading
  -> shared recording and final selection
```

This route is identified as `route4_wikidata_two_hop`. It keeps Route 1's join-template route intact, but uses ordinary single-hop templates as reusable facts. The default one-hop source is the reviewed Route 4 catalog, and a deterministic two-hop template catalog enumerates ordered answer/clue pairs for both ways of joining on the shared hidden entity: `(x, r1, a) + (x, r2, c)` and `(x, r1, a) + (c, r2, x)`. The final question asks for the answer-hop object `a` while identifying the hidden entity `x` only through the clue hop. The bridge `x` must be an entity, never a date, number, coordinate, or other literal value. Date and number values may still be final answers or visible clues when their single-hop templates pass validation. Object-side bridge inference is limited to human-to-human joins and place joins proven by same-level labels or by explicit same-relation chains, currently `P17 -> P17` for country and `P131 -> P131` for administrative area. Generic `Place` object clues such as `location` are too broad to imply every place subtype in the static pair catalog, and `Other` bridge rules are intentionally deferred. The hidden entity may be the subject or object of the clue hop, and its label/aliases must not appear in the final question.

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
- complete multi-hop provenance for multi-hop joins, including connected reasoning paths, hidden bridge leakage checks, and required reasoning clues

Preferred reuse source:

- existing `5-12` validator logic where still compatible, especially for disambiguation and deduplication

For the first scalable Route 1 multi-hop target, include only join-style templates with `reasoning_style = multi_hop_join`. Ordinal questions should stay with Route 3-style semi-structured/table reasoning for now, and aggregate/count templates should stay out of the default Route 1 multi-hop scale path until their stability validators are stronger.

For `route4_wikidata_two_hop`, use validated single-hop templates rather than multi-hop-only templates. All compatible non-frozen reviewed single-hop template pairs are attempted by default; static pairing removes same-property pairs and templates that cannot combine on either side of the triples, while runtime pruning removes answer/clue alias collisions, missing visible clues, and clue paths that identify more than one hidden entity in the validated pool.

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

`answer_type` is required for every template because downstream validation, number normalization, SimpleQA Verified-style margin handling, and reporting depend on it. Legacy Route 1 catalog rows may still contain older values such as `Organization`, `Work`, `Language`, and `Entity`, but new expansion catalogs should normalize to the SimpleQA-style set: `Person`, `Place`, `Number`, `Date`, and `Other`.

The expanded single-hop template catalog is a statusless, route-neutral planning artifact. It extracts current single-hop templates that are not ordinal/count templates, keeps their QIDs/PIDs and candidate search query shape, normalizes answer types to the five-value set, and adds generated templates across 20 domains, including `History`. Canonical questions in this catalog are for human review and future route migration; downstream multi-hop generation may use the QID/PID metadata without using those canonical questions directly.

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

For `route3_wikipedia_infobox`, the first implementation intentionally has no route-local factual validator beyond parsing success and model-output shape checks. It stores provenance and parsed source content as metadata, then relies on shared deterministic validation before long-tail filtering, DuckDuckGo long-tail filtering, optional model grading, and manual review. The lost-subject-anchor and incomplete-tie detectors are retained as review signals but are no longer hard rejection gates because pilot review showed too many false positives. Numeric answer-leakage checks compare extracted normalized number values rather than raw substrings, so a short answer such as `6` is not rejected merely because a year such as `2016` appears in the question. Shared answer-leakage checks also treat country name/adjective/demonym pairs and country/major-city pairs as bidirectional leakage cues.

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
