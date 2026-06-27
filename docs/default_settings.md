# Default Settings

This file is the defaults ledger for the current branch. When a code default changes, update this file in the same change.

Last updated: 2026-06-11.

## Route 1 Multi-Hop Join Runner

These defaults come from `scripts/run_route1_multihop_pipeline.py`.

| Setting | Default | Notes |
| --- | --- | --- |
| Route | `route1_wikidata_multihop_join` | QID-first, join-only Route 1 multi-hop scale path. |
| `--target-time` | `2024` | Conservative pre-2025 default. |
| `--date-upper-bound` | `2024-12-31` | Keeps candidate facts settled before the default cutoff year. |
| `--cutoff-year` | `2025` | Shared surface validation rejects question wording that depends on this year or later. |
| `--record-limit` | `10` | Number of QID seed units to process in one invocation. |
| `--harvest-limit` | `100` | Candidate harvest limit passed to Route 1 template executors. |
| `--accepted-target` | `0` | `0` means process the record limit rather than stopping at an accepted count. |
| `--final-target` | `300` | Final deduplicated/rebalanced review target. |
| Default templates | join-only | Uses `person_first_degree_university`, `film_source_work_author`, `tv_series_source_work_author`, `company_that_released_product_founder`, `company_that_developed_benchmark_founder`, and `terminal_operator_country`. |
| Ordinal/aggregate templates | excluded | Ordinals stay out of the default Route 1 multi-hop scale path; number/count templates are not selected by default. |
| `--duckduckgo-top-k` | `5` | Fast pool-generation default. |
| `--generated-search-query-count` | `2` | Fast pool-generation default. |
| `--duckduckgo-parallel-queries` | `3` | Shared search verifier per-candidate parallelism. |
| `--candidate-workers` | `4` | Concurrent candidate processing workers. |
| `--wikidata-concurrency-limit` | `1` | Bounded Wikidata calls during generation/validation. |
| `--duckduckgo-concurrency-limit` | `4` | Shared DuckDuckGo semaphore across candidate workers. |
| `--openrouter-generation-rewrite-concurrency-limit` | `10` | Shared rewrite semaphore when rewrite is enabled. |
| `--second-stage-concurrency-limit` | `10` | Shared second-stage grading semaphore when grading is enabled. |
| `--enable-rewrite` | `False` | Uses the shared rewrite contract when enabled. |
| `--enable-second-stage-grading` | `False` | Optional SimpleQA Verified-style difficulty review. |
| `--second-stage-grading-accuracy-threshold` | `0.1` | Rejects candidates solved above the threshold when grading is enabled. |
| `--start-from-endpoint` | `False` | Loads existing accepted/rejected JSONL as the checkpoint. |
| `--state` | `outputs/route1_multihop_join_state.json` | Persistent QID seed state with used, in-progress, accepted, rejected, and rerun seed keys. |
| `--output` | `outputs/route1_multihop_join_accepted.jsonl` | Accepted pool endpoint. |
| `--rejected-output` | `outputs/route1_multihop_join_rejected.jsonl` | Rejected endpoint. |
| `--final-output` | `outputs/route1_multihop_join_final.jsonl` | Final deduplicated/rebalanced review candidates. |

## Route 4 Wikidata Two-Hop Runner

These defaults come from `scripts/run_route4_two_hop_pipeline.py`.

| Setting | Default | Notes |
| --- | --- | --- |
| Route | `route4_wikidata_two_hop` | Composes validated single-hop facts around one hidden entity. |
| `--target-time` | `2024` | Conservative pre-2025 default. |
| `--date-upper-bound` | `2024-12-31` | Keeps candidate facts settled before the default cutoff year. |
| `--cutoff-year` | `2025` | Shared surface validation rejects question wording that depends on this year or later. |
| `--record-limit` | `10` | Number of composed seed units to process in one invocation. |
| `--harvest-limit` | `100` | Candidate harvest limit per single-hop template. |
| `--final-target` | `300` | Final deduplicated/rebalanced review target. |
| Default templates | reviewed Route 4 one-hop templates that appear in the two-hop pair catalog | The route validates single-hop facts first, then composes compatible pairs. Current catalog coverage: 329 combinable one-hop templates and 25 uncombined one-hop templates. |
| `--duckduckgo-top-k` | `5` | Fast pool-generation default. |
| `--generated-search-query-count` | `2` | Fast pool-generation default. |
| `--duckduckgo-parallel-queries` | `3` | Shared search verifier per-candidate parallelism. |
| `--candidate-workers` | `4` | Concurrent candidate processing workers. |
| `--wikidata-concurrency-limit` | `1` | Bounded Wikidata calls during generation/validation. |
| `--duckduckgo-concurrency-limit` | `4` | Shared DuckDuckGo semaphore across candidate workers. |
| `--openrouter-generation-rewrite-concurrency-limit` | `10` | Shared rewrite semaphore when rewrite is enabled. |
| `--second-stage-concurrency-limit` | `10` | Shared second-stage grading semaphore when grading is enabled. |
| `--enable-rewrite` | `False` | Uses the shared rewrite contract when enabled. |
| `--enable-second-stage-grading` | `False` | Optional SimpleQA Verified-style difficulty review. |
| `--state` | `outputs/route4_two_hop_state.json` | Persistent seed state with used, in-progress, accepted, rejected, and rerun seed keys. |
| `--output` | `outputs/route4_two_hop_accepted.jsonl` | Accepted pool endpoint. |
| `--rejected-output` | `outputs/route4_two_hop_rejected.jsonl` | Rejected endpoint. |
| `--final-output` | `outputs/route4_two_hop_final.jsonl` | Final deduplicated/rebalanced review candidates. |

The current reviewed Route 4 catalog has 25 one-hop templates that do not join on either side of the two-hop template catalog:

- `existing_product_release_date`
- `existing_policy_department`
- `existing_event_venue`
- `existing_novella_original_language`
- `existing_animation_studio`
- `existing_spacecraft_operator`
- `existing_framework_license`
- `existing_port_operator`
- `existing_beverage_manufacturer`
- `existing_crop_variety_developer`
- `existing_kitchen_appliance_manufacturer`
- `existing_database_system_developer`
- `generated_computer_science_and_ai_computer_hardware_interfaces_number`
- `generated_food_agriculture_and_daily_life_beverages_date`
- `generated_architecture_and_transportation_rail_systems_number`
- `generated_sports_and_recreation_games_and_recreation_date`
- `generated_arts_and_media_television_date`
- `generated_people_public_offices_number`
- `generated_physical_sciences_scientific_instruments_number`
- `generated_society_and_culture_libraries_and_archives_date`
- `generated_computer_science_and_ai_databases_number`
- `generated_language_and_literature_periodicals_number`
- `generated_economy_and_business_products_date`
- `generated_geography_rivers_and_lakes_date`
- `route4_rocket_diameter`

## Disabled Route 1 Hidden-Entity Runner

`route1_wikidata_hidden_entity_two_hop` remains only as a disabled legacy route id for historical artifacts. `scripts/run_route1_hidden_entity_two_hop_pipeline.py` is not maintained for new runs and should not be used for scaling.

## Route 3 Runner

These defaults come from `scripts/run_wikipedia_infobox_pipeline.py`.

| Setting | Default | Notes |
| --- | --- | --- |
| Input URLs | none | Non-stream `generate` mode requires `--url` or `--url-file`. |
| `--url` | `[]` | Can be repeated. |
| `--url-file` | `None` | Text file, one URL or tab-separated URL row per line. |
| `--candidate-input` | `[]` | Required only for `--start-stage validation`. |
| `--start-stage` | `generate` | Other value: `validation`. |
| `--start-from-endpoint` | `False` | When enabled, existing accepted/rejected endpoint JSONL files are loaded as a checkpoint. Streaming mode syncs page-ID state and processes only the remaining requested total; URL mode skips completed URLs and appends new records instead of overwriting. |
| `--record-limit` | `10` | Compatibility-only limit for non-streaming URL-list or validation mode. Streaming mode uses `--stream-reuse-cached-page-count`, `--stream-fresh-cached-page-count`, and an internal/recipe page target instead. |
| `--target-time` | `2024` | Passed into shared settings. |
| `--run-date` | `None` | Falls back to `Settings(...).run_date`. |
| `--cutoff-year` | `2025` | Avoid generated question text depending on this year or later. |
| `--timeout-seconds` | `30.0` | Used by Wikipedia, search, and LLM clients. |
| `--proxy` | `none` | No proxy by default; pass a proxy URL to enable one. |
| `--duckduckgo-prefer-ddgs` | `True` | `--no-duckduckgo-prefer-ddgs` disables the `ddgs` primary path for diagnosis. |
| `--duckduckgo-ddgs-backend` | `auto` | Passed to `DDGS.text(..., backend=...)`. |
| `--duckduckgo-ddgs-max-attempts` | `2` | Bounded `ddgs` attempts before legacy fallback. |
| `--duckduckgo-disable-fallback` | `[]` | Diagnostic-only fallback disable list. Default leaves `ddgs`, legacy HTML/Lite, Lite endpoint fallback, and direct fallback enabled. Repeat the flag or pass comma-separated values such as `ddgs`, `legacy`, `lite`, or `direct`. |
| `--duckduckgo-cooldown` | `True` | `--no-duckduckgo-cooldown` disables process-global cooldown for repeated DDG throttle/transport failures. |
| `--duckduckgo-cooldown-failure-threshold` | `3` | Consecutive cooldown-worthy failures before sleeping. |
| `--duckduckgo-cooldown-initial-seconds` | `60.0` | First shared cooldown sleep. |
| `--duckduckgo-cooldown-max-seconds` | `300.0` | Maximum shared cooldown sleep. |
| `--output` | `outputs/wikipedia_infobox_accepted.jsonl` | Accepted JSONL. |
| `--rejected-output` | `outputs/wikipedia_infobox_rejected.jsonl` | Rejected JSONL. |
| `--summary-output` | `outputs/wikipedia_infobox_summary.json` | Run summary JSON. |
| `--walkthrough-output` | `None` | No markdown walkthrough unless explicitly set. |

## Route 3 Page Fetching

| Setting | Default | Notes |
| --- | --- | --- |
| Fetch API | `action=parse` | Route 3 parses page title, HTML text, infoboxes, and wikitables from MediaWiki parse payloads. |
| First paragraph source | parse HTML only | Extracted from the already-fetched parse HTML. |
| Parser noise suppression | enabled | Table/prose extraction skips `script` and `style` text, including `.mw-parser-output` CSS fragments that otherwise leak into cells and marker checks. |
| REST summary fallback | `False` | `--enable-rest-summary-fallback` opts in. Missing parse paragraphs should not create another network dependency by default. |
| Route 3 page archive cache | `cache/route3_pages` | Unified per-page JSON archive containing parse payload, parsed HTML, extracted table metadata, optional pageview request/response, computed pageview metrics when present, hashes, timestamps, and errors. |
| Shared rewrite first paragraph | not passed | Route 3 keeps using the generic shared rewrite payload; first paragraph is only in the Route 3 generation prompt and metadata. |
| Minimum table score | `0.0` | `--min-table-score`. Tables with rank score below this value are dropped before first-paragraph alias/context extraction and before Route 3 generation. If no table survives, the page is rejected before any LLM call. |
| Minimum total table rows | `3` | Tables with two or fewer parsed rows, counting title/header rows, are rejected before generation. Row count is not used to add or subtract ranking score. |
| Wikipedia request attempts per path | `2` | `WIKIPEDIA_REQUEST_ATTEMPTS_PER_PATH`. |
| Wikipedia retry initial sleep | `0.5` seconds | Exponential backoff base. |
| Wikipedia retry max sleep | `4.0` seconds | Per retry sleep cap. |
| Wikipedia retry jitter | `0.25` seconds | Random jitter added to retry sleep. |
| Wikipedia 429 shared backoff | `30.0` seconds | `--wikipedia-429-backoff-seconds`. A 429 from Wikipedia pauses all workers sharing the client before later network attempts. |
| Wikipedia 429 max shared backoff | `300.0` seconds | `--wikipedia-429-max-backoff-seconds`. Consecutive 429s double the shared pause up to this cap. |
| Wikipedia 429 recovery window | `120.0` seconds | `--wikipedia-429-recovery-seconds`. A successful quiet window resets the shared backoff to the base delay. |
| Wikipedia request headers | `Accept: application/json`, `Accept-Encoding: identity`, `Connection: close` | Used to reduce flaky compressed/kept-alive fetch behavior. |

## Route 3 Streaming

These defaults apply when `--stream-random-page-ids` is enabled.

| Setting | Default | Notes |
| --- | --- | --- |
| Streaming enabled | `False` | Enable with `--stream-random-page-ids`. |
| `--stream-state` | `outputs/wikipedia_infobox_stream_state.json` | Persistent used/in-progress/accepted/rejected/rerun state. |
| `--stream-page-id-min` | `1` | Lower page ID bound. |
| `--stream-page-id-max` | `80000000` | Upper page ID bound. |
| `--stream-page-source` | `table-search` | Other value: `random-page-id`. |
| Default table-search queries | `insource:"wikitable"` | The broad query is not included by default. |
| Broad table-search query | off | `--enable-broad-table-search` adds `insource:/\{\|/`. |
| `--stream-search-query` | `[]` | Explicit queries replace the default query list. |
| `--stream-search-limit` | `50` | MediaWiki search limit per query/offset. |
| `--stream-search-max-rounds` | `10` | Max query-offset rounds while reserving IDs. |
| `--stream-random-seed` | derived | Random page ID sampling seed. When omitted, the runner derives a deterministic seed from the run/segment identity so incremental runs do not reuse the same default stream. |
| `--stream-batch-size` | `10` | Page IDs reserved per streaming batch. |
| `--stream-page-workers` | `4` | Concurrent page IDs processed in streaming mode. Runs with `--stream-accepted-target` stay sequential to avoid overshooting the accepted target. |
| `--wikipedia-concurrency-limit` | `4` | Max concurrent Wikipedia API calls across streaming workers. |
| `--duckduckgo-concurrency-limit` | `4` | Max concurrent DuckDuckGo searches across streaming workers and per-candidate search query parallelism. |
| `--openrouter-generation-rewrite-concurrency-limit` | `10` | Max concurrent OpenRouter calls used for Route 3 QA generation and shared rewrite. Can be raised, for example to `20`, when the account/network tolerates it. |
| `--second-stage-concurrency-limit` | `10` | Max concurrent OpenRouter calls used by second-stage answer models and grader calls. Can be raised, for example to `20`, for larger runs. |
| `--stream-accepted-target` | `0` | `0` means process the configured streaming page budget rather than stopping at an accepted count. |
| `--run-group-id` | empty | When set, summaries update a run-group manifest so resumed segments can be found together without mixing with other runs. |
| Recipe append/top-up mode | disabled | `scripts/run_wikipedia_infobox_recipe.py --append-to-existing-run` creates suffixed segment artifacts, appends combined outputs, and seeds the shared recipe page-ID exclusion file from prior summaries/states. Use `--append-run-label` for a stable suffix. |
| `--run-segment-id` | summary filename stem | Unique invocation label inside a run group. |
| `--run-artifact-manifest` | `outputs/run_manifests/<run-group-id>.json` | Manifest path used when `--run-group-id` is set. |
| `--run-artifact-include-summary` | `[]` | Existing segment summaries to backfill into the manifest. Can be repeated. |
| Rerun pool | enabled | Recovered in-progress IDs and transient generation failures are retried before fresh IDs. |
| `--stream-reuse-cached-page-count` | `all` | Cached-page reuse budget. Use a non-negative integer, or `all` to reuse eligible cached pages until the page target is met or reusable cache is exhausted. |
| `--stream-fresh-cached-page-count` | `fill` | Fresh page discovery/fetch/cache budget. Use a non-negative integer, or `fill` to request fresh pages after cached reuse until the page target is met. |
| `--stream-reuse-cached-page-used-id-file` | `[]` | Optional helper-generated used-ID JSON/JSONL/plain files for cache reuse. Page-only and triadic entries are both treated as strict numeric page-level exclusions. |
| Cached page reuse source | `--route3-page-archive-dir` | Reusable archives must have a positive numeric `page_id` and cached `parse_payload` or `parsed_html`, then continue through the shared pageview/table scoring/generation/filtering path as read-only archive inputs. |
| Domain/subdomain policy | optional | Streaming does not reject only because no planned domain/subdomain exists. |

## Route 3 Model And Filters

| Setting | Default | Notes |
| --- | --- | --- |
| Generation-model provider | `openrouter` | `--small-model-provider`; provider for the Route 3 table/infobox generation call. |
| Generation model | `openai/gpt-4.1-mini` | `--generation-model`; legacy `--small-model` is accepted as a hidden compatibility alias. |
| Generation-model API key env | `OPENROUTER_API_KEY` | `--small-model-api-key-env`. |
| Generation-model base URL | `https://openrouter.ai/api/v1` | `--small-model-base-url`. |
| Generation-model max tokens | `1200` | `--small-model-max-tokens`. |
| KELM rewrite enabled | `False` | Enable the optional post-generation KELM-style rewrite pass with `--enable-kelm-rewrite`. |
| KELM rewrite model | `openai/gpt-4.1-mini` | `--kelm-rewrite-model`; used only when KELM rewrite is enabled. |
| Second-stage grading enabled | `False` | Enable with `--enable-second-stage-grading`. |
| Second-stage grading accuracy threshold | `0.1` | Route 3 runner override. Shared `Settings` default is `0.5`. |
| Second-stage answer model execution | parallel | Panel answer models are run concurrently when second-stage grading is enabled. |
| Second-stage grader execution | batched | The grader scores all executed panel predictions in one JSON call when a grader model is configured. |
| Second-stage early stop | enabled | If the first panel model is graded correct and that alone exceeds the accuracy threshold, remaining panel answers are skipped. |
| DuckDuckGo top K | `5` | `--duckduckgo-top-k`. Fast default for initial Route 3 streaming; run slower survivor review separately when needed. |
| DuckDuckGo parallel queries | `3` | `--duckduckgo-parallel-queries`. |
| DuckDuckGo ddgs backend | `auto` | `--duckduckgo-ddgs-backend`. Recipe segments pass this through to the Route 3 pipeline. |
| DuckDuckGo ddgs attempts | `2` | `--duckduckgo-ddgs-max-attempts`. |
| DuckDuckGo disabled fallbacks | `[]` | `--duckduckgo-disable-fallback`. Normal runs leave every fallback enabled; use this only for path-isolation probes. |
| DuckDuckGo global cooldown | enabled | Controlled by `--duckduckgo-cooldown` / `--no-duckduckgo-cooldown` plus the threshold/initial/max cooldown flags. |
| Generated search query count | `2` | Route 3 prompt asks for this many answer-blind queries. Fast default for initial Route 3 streaming; run slower survivor review separately when needed. |
| Minimum table score | `0.0` | `--min-table-score`. The same cutoff is used for URL and streaming Route 3 runs. |
| Route 3 reasoning types | `single_fact` | `--route3-reasoning-type`. When omitted, Route 3 prompts use the fixed `single_fact` reasoning contract and Route 3 writes `reasoning_type=single_fact` directly into candidates without asking the model to output that field. Repeat the flag or pass comma-separated values to let the model choose among multiple reasoning types such as `max`, `min`, `count`, or `ordinal`. |
| Route 3 prose-leakage scoring | enabled | `--route3-prose-leakage-scoring` / `--no-route3-prose-leakage-scoring`. When enabled, table value leakage below `0.2` adds `0.5` points and leakage above `0.8` subtracts `0.5` points. Leakage stats are still recorded when scoring is disabled. |
| Route 3 answer-type table hints | enabled only for single-mode, single-answer-type runs | Shared wikitable/infobox table ranking adds answer-type bonuses only when `--route3-answer-type-mode single` and exactly one `--route3-answer-type` are configured: `Person` +1 for adjacent initial-capitalized non-common words, `Place` +2 for seeded place-category markers, and `Date` +2 for month names, no-comma 1500-2040 years, or numeric month/day/year markers such as `3/6/2026`. These bonuses do not apply to `all5`, unspecified answer-type runs, or multiple allowed answer types. |
| Route 3 table source types | `infobox`, `wikitable` | `--route3-table-source-type` can restrict generation to only `infobox`, only `wikitable`, or both/all. The same setting is passed through recipe segments and recorded in summaries/metadata. |
| Route 3 LLM table choice | disabled | By default only the single top-ranked surviving table is passed to the generation LLM. `--route3-llm-choose-table` passes the top three surviving ranked tables and includes table-choice prompt text. |
| Route 3 table filter modes | `no_external_links_tables`, `no_horizontal_companion_tables`, `no_picture_heavy_tables`, `no_incomplete_tables`, `not_number_dominant`, `no_social_science_research` | `--route3-table-filter-mode` enables modes and `--disable-route3-table-filter-mode` removes defaults for a run. These filters drop matching wikitables before the generation prompt. Infoboxes are cleaned before ranking: image-bearing rows and precise media captions/titles are removed, then each key-value row is checked against incomplete, number-dominance, and social-science markers; failing rows are removed. |
| Route 3 answer-type mode | `single` | `--route3-answer-type-mode`. `single` preserves the legacy one-candidate output shape. `all5` asks one generation prompt to return exactly five fixed slots, one each for `Person`, `Place`, `Number`, `Date`, and `Other`; unsupported slots are rejected with `discard_reason` while supported slots can still produce candidates. |
| Route 3 pageview prefilter | disabled | `--route3-pageview-prefilter` / `--no-route3-pageview-prefilter`. When disabled, metadata records `enabled=false`, `status=disabled`, `decision=allow`, and `reason=pageview_prefilter_disabled`; no pageview request is made and no pageview placeholder rejection is emitted. When enabled, it runs before table grading and before the generation LLM. |
| Route 3 pageview window | `12` months | `--route3-pageview-window-months`. Uses the most recent complete months available in the page archive/pageview response. |
| Route 3 pageview max monthly average | `5000` | `--route3-max-monthly-average-pageviews`. Pages with the full 12-month window observed and above this average are rejected as too popular before table grading. |
| Route 3 underfilled-window max single-month pageviews | `10000` | `--route3-max-underfilled-monthly-pageviews`. When fewer than 12 months are observed, pages with any observed month above this value are rejected; otherwise they are allowed and the underfilled-window rule is recorded. |
| Route 3 pageview unavailable policy | `allow` | `--route3-pageview-unavailable-policy`. Applies only when the pageview prefilter is enabled. Missing or failed pageview data is recorded but does not block generation by default. |
| Route 3 infobox removed-row max rate | `0.60` | `--route3-infobox-max-removed-row-rate`. Infoboxes with a removed non-header row rate greater than this value are rejected. Exactly `0.60` is allowed by this rule. |
| Route 3 infobox minimum remaining rows | `5` | `--route3-infobox-min-remaining-rows`. After cleanup, infoboxes with fewer than five remaining non-header rows are rejected before ranking. |
| Route 3 prompt channel | source-specific | Infoboxes and wikitables use separate prompt builders and filter/ranking channels. The initial prompts are near-copies of the existing Route 3 prompt for later manual tuning. |
| Big batch mode | disabled | `--big-batch-mode` is intended for large Route 3 recipes. It retries transient table-search discovery failures and aligns `--stream-batch-size` with `--stream-search-limit` for table-search streams. It does not compact accepted or rejected records. |
| Compact output | disabled and ignored for Route 3 | `--compact-output` is deprecated for Route 3. Accepted and rejected records retain full audit metadata in every mode. |
| Compact rejected output | disabled and ignored for Route 3 | `--compact-rejected-output` is deprecated for Route 3. Rejected records retain full audit metadata, including prompts, page archive metadata, pageview metadata/data, LLM responses, search evidence, and grading evidence. |
| Search full-question hit-rate threshold | `0.3` | Reject when above threshold. |
| Search keyword hit-rate threshold | `0.3` | Reject when above threshold. |
| Search overall hit-rate threshold | `0.3` | Reject when above threshold. |

## Shared DuckDuckGo Client

These defaults come from `src/wikidata_simpleqa/search_client.py` and apply to routes that use `DuckDuckGoSearchClient`.

| Setting | Default | Notes |
| --- | --- | --- |
| Primary backend | `ddgs` | The client tries the optional `ddgs` package before legacy HTML/Lite search. Install `ddgs` in production and probe environments that run DuckDuckGo search. |
| `--duckduckgo-ddgs-backend` / `ddgs_backend` | `auto` | Passed to `DDGS.text(..., backend=...)`. Use explicit values such as `duckduckgo` only for path-isolation probes. |
| `--duckduckgo-ddgs-max-attempts` / `ddgs_max_attempts` | `2` | Two bounded attempts before legacy fallback. |
| Legacy HTML/Lite fallback | enabled | Used when `ddgs` is unavailable or fails, unless disabled by the diagnostic fallback list. |
| HTML holding-status fallback | `202`, `403`, `429`, `500`, `502`, `503`, `504` | Matching HTML responses switch to Lite instead of retrying HTML. |
| Lite max attempts | `2` | Bounded retry for Lite holding/rate-limit/transient failures. |
| Direct fallback | enabled when a proxy path fails | A direct pass is meaningful only after a configured proxy path fails. |
| Disabled fallbacks | none | Diagnostic names include `ddgs`, `legacy`/`html`, `lite`, and `direct`/`direct_fallback`. |
| `--duckduckgo-cooldown` / global cooldown enabled | `True` | Shared process-level cooldown for repeated DDG 202/403 or transport failures. |
| `--duckduckgo-cooldown-failure-threshold` | `3` | Consecutive cooldown-worthy DDG failures before triggering sleep. |
| `--duckduckgo-cooldown-initial-seconds` | `60.0` seconds | Minute-level pause after the threshold is reached. |
| `--duckduckgo-cooldown-max-seconds` | `300.0` seconds | Consecutive cooldowns grow up to this cap. |
| `ddgs_no_results` cooldown behavior | not cooldown-worthy | A plain `ddgs` "No results found" outcome is recorded but does not trigger global cooldown. |
| SOCKS dependency | `PySocks` | Required for the legacy urllib client to use `socks5://...` proxies. Without it, proxy setup failure is recorded and direct fallback may still run. |

## Shared Settings

These defaults come from `src/wikidata_simpleqa/config.py` and are used by broader generation entry points unless a script overrides them.

| Setting | Default |
| --- | --- |
| `run_date` | current local date |
| `date_upper_bound` | `run_date` |
| `pilot_total` | `20` |
| `harvest_limit_per_template` | `100` |
| `cutoff_year` | `2025` |
| `enabled_routes` | `("route2_wikidata_wikipedia_hybrid", "route1_wikidata_light")` |
| `duckduckgo_top_k` | `10` |
| `duckduckgo_parallel_queries` | `3` |
| `generated_search_query_count` | `3` |
| `second_stage_grading_enabled` | `False` |
| `second_stage_grading_accuracy_threshold` | `0.5` |
| `longtail_prefilter_max_sitelinks` | `80` |
| `longtail_prefilter_max_claims` | `400` |
| `search_longtail_max_full_question_hit_rate` | `0.3` |
| `search_longtail_max_keyword_hit_rate` | `0.3` |
| `search_longtail_max_overall_hit_rate` | `0.3` |
| `allow_year_in_official_title` | `False` |
| `reject_future_dated_candidates` | `True` |
| `reject_current_or_latest_facts` | `True` |
| `reject_mutable_relationships` | `True` |
| `reject_mutable_affiliations` | `True` |
| `reject_cumulative_statistics` | `True` |
| `reject_unreleased_works` | `True` |
| `user_agent` | `wikidata-simpleqa-generator/0.1` |
| `proxy` | `None` |
| `timeout_seconds` | `30.0` |
| `wikidata_max_entity_ids_per_request` | `50` |
| `wikidata_log_checkpoints` | `False` |
| `live_probe_mode` | `False` |
| `live_probe_harvest_limit` | `2` |
| `live_probe_max_entity_ids_per_request` | `10` |
| `route1_light_fallback_enabled` | `True` |
| `route1_subject_seed_window_granularity` | `year` |
| `random_seed` | `42` |
| `cache_dir` | `cache/wikidata` |
| `output_path` | `outputs/pilot_accepted.jsonl` |
| `rejected_output_path` | `outputs/pilot_rejected.jsonl` |
| `rewrite_enabled` | `False` |
| `rewrite_llm` | `None` |

## Default Second-Stage Panel

The shared default panel is configured but inactive unless second-stage grading is enabled.

| Role | Provider | Model | Max tokens |
| --- | --- | --- | --- |
| Answer model 1 | `openrouter` | `openai/gpt-4.1-mini` | `128` |
| Answer model 2 | `openrouter` | `google/gemini-3-flash-preview` | `128` |
| Grader | `openrouter` | `openai/gpt-4.1-mini` | `128` |
