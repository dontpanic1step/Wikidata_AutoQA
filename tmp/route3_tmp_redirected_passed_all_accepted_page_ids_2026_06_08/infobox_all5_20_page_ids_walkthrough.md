# Route 3 Streaming Wikipedia Page-ID Walkthrough - 2026-06-08

## Stats

- Mode: `page_id_stream`
- Page source: `table-search`
- Table-search queries: `insource:"wikitable"`
- Attempted page IDs: 20
- Unique attempted page IDs: 20
- Stream state reset at run start: yes
- Accepted QAs: 0
- Rejected QAs/pages: 20
- Transient rerun attempts during run: 0
- Wall-clock runtime: 105.8671s
- DuckDuckGo top K: 5
- Generated search queries per QA: 2
- DuckDuckGo parallel queries: 3
- Minimum Route 3 table score: 0.0
- Route 3 reasoning_type constraint: `single_fact`
- Route 3 table filter modes: `no_external_links_tables, no_horizontal_companion_tables, no_picture_heavy_tables, no_incomplete_tables, not_number_dominant, no_social_science_research`
- Route 3 table source types: `infobox`
- Route 3 prose-leakage scoring: `enabled`
- Route 3 LLM table choice: `disabled`
- Stream page workers: 2
- Wikipedia concurrency limit: 2
- Wikipedia 429 backoff: 30.0s base, 300.0s max, 120.0s recovery
- DuckDuckGo service concurrency limit: 2
- OpenRouter generation/rewrite concurrency limit: 2
- Second-stage concurrency limit: 2
- Page-id bounds: 1 to 80000000
- Stream state: `tmp\route3_tmp_redirected_passed_all_accepted_page_ids_2026_06_08\infobox_all5_20_page_ids_state.json`
- Accepted output: `tmp\route3_tmp_redirected_passed_all_accepted_page_ids_2026_06_08\infobox_all5_20_page_ids_accepted.jsonl`
- Rejected output: `tmp\route3_tmp_redirected_passed_all_accepted_page_ids_2026_06_08\infobox_all5_20_page_ids_rejected.jsonl`
- Domain policy: `domain_and_subdomain_optional_for_page_id_streaming`
- Rerun pool after run: `empty`

### Survival By Layer

| Layer | Entered | Failed | Survived | Layer survival | Cumulative survival |
| --- | ---: | ---: | ---: | ---: | ---: |
| Page-id reservation | 20 | 0 | 20 | 100.0% | 100.0% |
| Unresolved or returned to rerun pool | 20 | 0 | 20 | 100.0% | 100.0% |
| Page extraction, table grading, and QA generation | 20 | 20 | 0 | 0.0% | 0.0% |
| Rewrite and surface validation | 0 | 0 | 0 | 0.0% | 0.0% |
| DuckDuckGo long-tail filtering | 0 | 0 | 0 | 0.0% | 0.0% |
| Second-stage model grading | 0 | 0 | 0 | 0.0% | 0.0% |
| Shared route-aware validation | 0 | 0 | 0 | 0.0% | 0.0% |
| Deduplication | 0 | 0 | 0 | 0.0% | 0.0% |
| Other rejection | 0 | 0 | 0 | 0.0% | 0.0% |

### Failure Reasons

| Stage | Reason | Count |
| --- | --- | ---: |
| `route_generation` | `wikipedia_pageview_prefilter_rejected:monthly_average_pageviews>5000.0000` | 20 |

### Answer Type Stats

| Scope | Answer type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `unknown` | 0 | 20 | 20 | 0.0% |

### Reasoning Type Stats

| Scope | Reasoning type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `single_fact` | 0 | 20 | 20 | 0.0% |

### Rerun Pool After Run

Rerun pool is empty.


### Phase Timings

Timing nesting: `wall_clock_seconds` is the whole run. `total_generation_seconds` contains page fetch/paragraph/table parse/LLM QA generation for one page. `total_processing_seconds` contains rewrite, number margin, DuckDuckGo search, second-stage grading when enabled, shared validation, and dedup checks for one generated candidate. `candidate_processing_seconds` is an alias of `total_processing_seconds`. Child phase totals are useful for bottlenecks, but they should not be added to parent totals.

| Pipeline order | Phase | Parent/child | Additive? | Meaning |
| ---: | --- | --- | --- | --- |
| 0 | `wall_clock_seconds` | run total | No | Elapsed time for the whole streaming command. |
| 1 | `page_fetch_seconds` | child of total_generation_seconds | Yes, within generation only | MediaWiki action=parse fetch for one page. |
| 2 | `first_paragraph_extract_seconds` | child of total_generation_seconds | Yes, within generation only | Local extraction of first paragraph from parse HTML. |
| 3 | `first_paragraph_fetch_seconds` | optional child of total_generation_seconds | Yes, within generation only | REST summary fallback when explicitly enabled and parse HTML lacks a paragraph. |
| 4 | `table_parse_seconds` | child of total_generation_seconds | Yes, within generation only | Local table/prose parsing and table ranking inputs. |
| 5 | `llm_question_generation_seconds` | child of total_generation_seconds | Yes, within generation only | Small-model Route 3 QA generation call. |
| 6 | `total_generation_seconds` | parent | No | Overall Route 3 generation time for one page. |
| 7 | `rewrite_seconds` | child of total_processing_seconds | Yes, within processing only | Shared rewrite call when enabled. |
| 8 | `number_reference_margin_seconds` | child of total_processing_seconds | Yes, within processing only | Numeric reference margin setup for Number answers. |
| 9 | `duckduckgo_search_seconds` | child of total_processing_seconds | Yes, within processing only | DuckDuckGo long-tail queries and leakage scoring. |
| 10 | `second_stage_grading_seconds` | optional child of total_processing_seconds | Yes, within processing only | Model-panel answerability grading when enabled. |
| 11 | `total_processing_seconds` | parent | No | Shared rewrite, filtering, grading, validation, and dedup processing for one candidate. |
| 12 | `candidate_processing_seconds` | alias | No | Alias of total_processing_seconds for compatibility. |

#### Current Run Phase Timings

| Phase | Count | Total seconds | Average seconds | Max seconds |
| --- | ---: | ---: | ---: | ---: |
| `candidate_processing_seconds` | 20 | 0.0079 | 0.0004 | 0.0009 |
| `number_reference_margin_seconds` | 20 | 0.0000 | 0.0000 | 0.0000 |
| `page_fetch_seconds` | 20 | 1.8572 | 0.0929 | 0.2221 |
| `pageview_prefilter_seconds` | 20 | 163.9782 | 8.1989 | 62.6307 |
| `rewrite_seconds` | 20 | 0.0000 | 0.0000 | 0.0000 |
| `table_parse_seconds` | 20 | 31.4078 | 1.5704 | 3.8971 |
| `total_generation_seconds` | 20 | 202.7334 | 10.1367 | 63.9535 |
| `total_processing_seconds` | 20 | 0.0079 | 0.0004 | 0.0009 |

## Accepted Candidates

No accepted candidates in this run.
## Second-Stage Filtering Responses

These are the small-model QA responses used by the second-stage filter: `openai/gpt-4.1-mini` and `google/gemini-3-flash-preview`.

| Page ID | Question | Reference answer | openai/gpt-4.1-mini | google/gemini-3-flash-preview |
| ---: | --- | --- | --- | --- |
| 17416221 | South Africa |  | not run | not run |
| 32611 | Vietnam War |  | not run | not run |
| 22093 | National Basketball Association |  | not run | not run |
| 9316 | England |  | not run | not run |
| 5489 | Chile |  | not run | not run |
| 21355232 | List of national parks of the United States |  | not run | not run |
| 199445 | Wayne Rooney |  | not run | not run |
| 31740 | University of Michigan |  | not run | not run |
| 8083 | Dr. Dre |  | not run | not run |
| 292259 | Deutsche Welle |  | not run | not run |
| 66958 | Renminbi |  | not run | not run |
| 41853326 | Inter Miami CF |  | not run | not run |
| 45367389 | Greater London |  | not run | not run |
| 60382764 | Reiwa era |  | not run | not run |
| 105908 | Ford Mustang |  | not run | not run |
| 55440889 | Pixel 2 |  | not run | not run |
| 22948 | Poseidon |  | not run | not run |
| 84952 | Marvelous Marvin Hagler |  | not run | not run |
| 235916 | Jada Pinkett Smith |  | not run | not run |
| 2924002 | Electronic dance music |  | not run | not run |


## Rejected And Rerun Decisions

| Page ID | Stage | Exact reason | Page/question |
| ---: | --- | --- | --- |
| 17416221 | `route_generation` | `wikipedia_pageview_prefilter_rejected:monthly_average_pageviews>5000.0000` | South Africa |
| 32611 | `route_generation` | `wikipedia_pageview_prefilter_rejected:monthly_average_pageviews>5000.0000` | Vietnam War |
| 22093 | `route_generation` | `wikipedia_pageview_prefilter_rejected:monthly_average_pageviews>5000.0000` | National Basketball Association |
| 9316 | `route_generation` | `wikipedia_pageview_prefilter_rejected:monthly_average_pageviews>5000.0000` | England |
| 5489 | `route_generation` | `wikipedia_pageview_prefilter_rejected:monthly_average_pageviews>5000.0000` | Chile |
| 21355232 | `route_generation` | `wikipedia_pageview_prefilter_rejected:monthly_average_pageviews>5000.0000` | List of national parks of the United States |
| 199445 | `route_generation` | `wikipedia_pageview_prefilter_rejected:monthly_average_pageviews>5000.0000` | Wayne Rooney |
| 31740 | `route_generation` | `wikipedia_pageview_prefilter_rejected:monthly_average_pageviews>5000.0000` | University of Michigan |
| 8083 | `route_generation` | `wikipedia_pageview_prefilter_rejected:monthly_average_pageviews>5000.0000` | Dr. Dre |
| 292259 | `route_generation` | `wikipedia_pageview_prefilter_rejected:monthly_average_pageviews>5000.0000` | Deutsche Welle |
| 66958 | `route_generation` | `wikipedia_pageview_prefilter_rejected:monthly_average_pageviews>5000.0000` | Renminbi |
| 41853326 | `route_generation` | `wikipedia_pageview_prefilter_rejected:monthly_average_pageviews>5000.0000` | Inter Miami CF |
| 45367389 | `route_generation` | `wikipedia_pageview_prefilter_rejected:monthly_average_pageviews>5000.0000` | Greater London |
| 60382764 | `route_generation` | `wikipedia_pageview_prefilter_rejected:monthly_average_pageviews>5000.0000` | Reiwa era |
| 105908 | `route_generation` | `wikipedia_pageview_prefilter_rejected:monthly_average_pageviews>5000.0000` | Ford Mustang |
| 55440889 | `route_generation` | `wikipedia_pageview_prefilter_rejected:monthly_average_pageviews>5000.0000` | Pixel 2 |
| 22948 | `route_generation` | `wikipedia_pageview_prefilter_rejected:monthly_average_pageviews>5000.0000` | Poseidon |
| 84952 | `route_generation` | `wikipedia_pageview_prefilter_rejected:monthly_average_pageviews>5000.0000` | Marvelous Marvin Hagler |
| 235916 | `route_generation` | `wikipedia_pageview_prefilter_rejected:monthly_average_pageviews>5000.0000` | Jada Pinkett Smith |
| 2924002 | `route_generation` | `wikipedia_pageview_prefilter_rejected:monthly_average_pageviews>5000.0000` | Electronic dance music |


