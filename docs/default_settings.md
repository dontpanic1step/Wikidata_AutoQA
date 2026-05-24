# Default Settings

This file is the defaults ledger for the current branch. When a code default changes, update this file in the same change.

Last updated: 2026-05-21.

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
| `--record-limit` | `10` | Number of URLs/page IDs/candidates to process. |
| `--target-time` | `2024` | Passed into shared settings. |
| `--run-date` | `None` | Falls back to `Settings(...).run_date`. |
| `--cutoff-year` | `2025` | Avoid generated question text depending on this year or later. |
| `--timeout-seconds` | `30.0` | Used by Wikipedia, search, and LLM clients. |
| `--proxy` | `socks5://127.0.0.1:7897` | Use `--proxy none` to disable. |
| `--output` | `outputs/wikipedia_infobox_accepted.jsonl` | Accepted JSONL. |
| `--rejected-output` | `outputs/wikipedia_infobox_rejected.jsonl` | Rejected JSONL. |
| `--summary-output` | `outputs/wikipedia_infobox_summary.json` | Run summary JSON. |
| `--walkthrough-output` | `None` | No markdown walkthrough unless explicitly set. |

## Route 3 Page Fetching

| Setting | Default | Notes |
| --- | --- | --- |
| Fetch API | `action=parse` | Route 3 parses page title, HTML text, infoboxes, and wikitables from MediaWiki parse payloads. |
| First paragraph source | parse HTML only | Extracted from the already-fetched parse HTML. |
| REST summary fallback | `False` | `--enable-rest-summary-fallback` opts in. Missing parse paragraphs should not create another network dependency by default. |
| Shared rewrite first paragraph | not passed | Route 3 keeps using the generic shared rewrite payload; first paragraph is only in the Route 3 generation prompt and metadata. |
| Minimum table score | `0.0` | `--min-table-score`. Tables with rank score below this value are dropped before first-paragraph alias/context extraction and before Route 3 generation. If no table survives, the page is rejected before any LLM call. |
| Wikipedia request attempts per path | `2` | `WIKIPEDIA_REQUEST_ATTEMPTS_PER_PATH`. |
| Wikipedia retry initial sleep | `0.5` seconds | Exponential backoff base. |
| Wikipedia retry max sleep | `4.0` seconds | Per retry sleep cap. |
| Wikipedia retry jitter | `0.25` seconds | Random jitter added to retry sleep. |
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
| `--stream-accepted-target` | `0` | `0` means process `--record-limit` IDs rather than stopping at an accepted count. |
| `--run-group-id` | empty | When set, summaries update a run-group manifest so resumed segments can be found together without mixing with other runs. |
| `--run-segment-id` | summary filename stem | Unique invocation label inside a run group. |
| `--run-artifact-manifest` | `outputs/run_manifests/<run-group-id>.json` | Manifest path used when `--run-group-id` is set. |
| `--run-artifact-include-summary` | `[]` | Existing segment summaries to backfill into the manifest. Can be repeated. |
| Rerun pool | enabled | Recovered in-progress IDs and transient generation failures are retried before fresh IDs. |
| Domain/subdomain policy | optional | Streaming does not reject only because no planned domain/subdomain exists. |

## Route 3 Model And Filters

| Setting | Default | Notes |
| --- | --- | --- |
| Small-model provider | `openrouter` | `--small-model-provider`. |
| Small model | `openai/gpt-4.1-mini` | `--small-model`. |
| Small-model API key env | `OPENROUTER_API_KEY` | `--small-model-api-key-env`. |
| Small-model base URL | `https://openrouter.ai/api/v1` | `--small-model-base-url`. |
| Small-model max tokens | `1200` | `--small-model-max-tokens`. |
| Rewrite enabled | `False` | Enable with `--enable-rewrite`. |
| Rewrite model | `openai/gpt-4.1-mini` | Used only when rewrite is enabled. |
| Second-stage grading enabled | `False` | Enable with `--enable-second-stage-grading`. |
| Second-stage grading accuracy threshold | `0.1` | Route 3 runner override. Shared `Settings` default is `0.5`. |
| Second-stage answer model execution | parallel | Panel answer models are run concurrently when second-stage grading is enabled. |
| Second-stage grader execution | batched | The grader scores all executed panel predictions in one JSON call when a grader model is configured. |
| Second-stage early stop | enabled | If the first panel model is graded correct and that alone exceeds the accuracy threshold, remaining panel answers are skipped. |
| DuckDuckGo top K | `5` | `--duckduckgo-top-k`. Fast default for initial Route 3 streaming; run slower survivor review separately when needed. |
| DuckDuckGo parallel queries | `3` | `--duckduckgo-parallel-queries`. |
| Generated search query count | `2` | Route 3 prompt asks for this many answer-blind queries. Fast default for initial Route 3 streaming; run slower survivor review separately when needed. |
| Minimum table score | `0.0` | `--min-table-score`. The same cutoff is used for URL and streaming Route 3 runs. |
| Route 3 table filter modes | `no_picture_heavy_tables`, `no_approximate_tables`, `no_incomplete_tables`, `not_number_dominant`, `no_social_science_research` | `--route3-table-filter-mode` enables modes and `--disable-route3-table-filter-mode` removes defaults for a run. These filters drop matching tables before the generation prompt. |
| Search full-question hit-rate threshold | `0.3` | Reject when above threshold. |
| Search keyword hit-rate threshold | `0.3` | Reject when above threshold. |
| Search overall hit-rate threshold | `0.3` | Reject when above threshold. |

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
| `proxy` | `socks5://127.0.0.1:7897` |
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
