# Default Settings

This file is the defaults ledger for the current branch. When a code default changes, update this file in the same change.

Last updated: 2026-05-19.

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
| `--stream-random-seed` | `42` | Random page ID sampling seed. |
| `--stream-batch-size` | `10` | Page IDs reserved per streaming batch. |
| `--stream-accepted-target` | `0` | `0` means process `--record-limit` IDs rather than stopping at an accepted count. |
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
| DuckDuckGo top K | `5` | `--duckduckgo-top-k`. Fast default for initial Route 3 streaming; run slower survivor review separately when needed. |
| DuckDuckGo parallel queries | `3` | `--duckduckgo-parallel-queries`. |
| Generated search query count | `2` | Route 3 prompt asks for this many answer-blind queries. Fast default for initial Route 3 streaming; run slower survivor review separately when needed. |
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
