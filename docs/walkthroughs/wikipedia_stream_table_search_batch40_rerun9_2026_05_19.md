# Route 3 Streaming Wikipedia Page-ID Walkthrough - 2026-05-19

## Stats

- Mode: `page_id_stream`
- Page source: `table-search`
- Table-search queries: `insource:"wikitable"; insource:/\{\|/`
- Attempted page IDs: 9
- Accepted QAs: 2
- Rejected QAs/pages: 4
- Returned to rerun pool without final decision: 3
- Page-id bounds: 1 to 80000000
- Stream state: `outputs\wikipedia_stream_table_search_batch40_2026_05_19_rerun_state.json`
- Accepted output: `outputs\wikipedia_stream_table_search_batch40_rerun9_2026_05_19_accepted.jsonl`
- Rejected output: `outputs\wikipedia_stream_table_search_batch40_rerun9_2026_05_19_rejected.jsonl`
- Domain policy: `domain_and_subdomain_optional_for_page_id_streaming`

### Survival By Layer

| Layer | Entered | Failed | Survived | Layer survival | Cumulative survival |
| --- | ---: | ---: | ---: | ---: | ---: |
| Page-id reservation | 9 | 0 | 9 | 100.0% | 100.0% |
| Unresolved or returned to rerun pool | 9 | 3 | 6 | 66.7% | 66.7% |
| Page extraction, table grading, and QA generation | 6 | 0 | 6 | 100.0% | 66.7% |
| Rewrite and surface validation | 6 | 1 | 5 | 83.3% | 55.6% |
| DuckDuckGo long-tail filtering | 5 | 3 | 2 | 40.0% | 22.2% |
| Second-stage model grading | 2 | 0 | 2 | 100.0% | 22.2% |
| Shared route-aware validation | 2 | 0 | 2 | 100.0% | 22.2% |
| Deduplication | 2 | 0 | 2 | 100.0% | 22.2% |
| Other rejection | 2 | 0 | 2 | 100.0% | 22.2% |

### Failure Reasons

| Stage | Exact reason | Count |
| --- | --- | ---: |
| `unresolved_rerun` | `wikipedia_infobox_generation_error:URLError:<urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1017)>` | 3 |
| `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | 2 |
| `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | 1 |
| `search_longtail` | `search_longtail_verifier_rejected:keyword_query_2:answer_in_title` | 1 |

### Phase Timings

| Phase | Count | Total seconds | Average seconds | Max seconds |
| --- | ---: | ---: | ---: | ---: |
| `candidate_processing_seconds` | 6 | 68.7658 | 11.4610 | 17.0774 |
| `duckduckgo_search_seconds` | 5 | 38.1924 | 7.6385 | 9.7933 |
| `first_paragraph_fetch_seconds` | 6 | 0.1296 | 0.0216 | 0.0364 |
| `llm_question_generation_seconds` | 6 | 48.5216 | 8.0869 | 17.6539 |
| `number_reference_margin_seconds` | 5 | 0.0001 | 0.0000 | 0.0001 |
| `page_fetch_seconds` | 6 | 0.2379 | 0.0396 | 0.0784 |
| `rewrite_seconds` | 6 | 30.5687 | 5.0948 | 9.0294 |
| `table_parse_seconds` | 6 | 1.8625 | 0.3104 | 0.4343 |
| `total_generation_seconds` | 6 | 50.9443 | 8.4907 | 18.0811 |
| `total_processing_seconds` | 6 | 68.7658 | 11.4610 | 17.0774 |

## Accepted Candidates

| Page ID | Question | Answer | Source |
| ---: | --- | --- | --- |
| 57877 | What is the molar concentration of sodium hydroxide in a solution with 30 weight percent? | 9.95 | https://en.wikipedia.org/wiki/Sodium_hydroxide |
| 407239 | Which city has the highest approximate daily circulation of The Indian Express newspaper? | Mumbai | https://en.wikipedia.org/wiki/The_Indian_Express |

## Rejected And Rerun Decisions

| Page ID | Stage | Exact reason | Page/question |
| ---: | --- | --- | --- |
| 292259 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which language was the first to be broadcast by Deutsche Welle? |
| 66958 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | Which currency ranked second in daily volume proportion in the global foreign exchange market turnover in April 2025? |
| 151451 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_2:answer_in_title` | What is the title of the 1997 documentary featuring Busta Rhymes? |
| 19261 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which ward in Monaco has the largest area measured in hectares? |
| 105391 | `unresolved_rerun` | `wikipedia_infobox_generation_error:URLError:<urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1017)>` | https://en.wikipedia.org/w/index.php?pageid=105391 |
| 156745 | `unresolved_rerun` | `wikipedia_infobox_generation_error:URLError:<urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1017)>` | https://en.wikipedia.org/w/index.php?pageid=156745 |
| 599 | `unresolved_rerun` | `wikipedia_infobox_generation_error:URLError:<urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1017)>` | https://en.wikipedia.org/w/index.php?pageid=599 |

