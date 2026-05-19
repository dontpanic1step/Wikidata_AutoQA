# Route 3 Streaming Wikipedia Page-ID Walkthrough - 2026-05-19

## Stats

- Mode: `page_id_stream`
- Page source: `table-search`
- Table-search queries: `insource:"wikitable"; insource:/\{\|/`
- Attempted page IDs: 5
- Accepted QAs: 1
- Rejected QAs/pages: 4
- Returned to rerun pool without final decision: 0
- Page-id bounds: 1 to 80000000
- Stream state: `D:\Study\AI\My-research\Wikidata_Framework\outputs\wikipedia_infobox_stream_state.json`
- Accepted output: `outputs\wikipedia_stream_table_search_smoke5_accepted.jsonl`
- Rejected output: `outputs\wikipedia_stream_table_search_smoke5_rejected.jsonl`
- Domain policy: `domain_and_subdomain_optional_for_page_id_streaming`

### Survival By Layer

| Layer | Entered | Failed | Survived | Layer survival | Cumulative survival |
| --- | ---: | ---: | ---: | ---: | ---: |
| Page-id reservation | 5 | 0 | 5 | 100.0% | 100.0% |
| Unresolved or returned to rerun pool | 5 | 0 | 5 | 100.0% | 100.0% |
| Page extraction, table grading, and QA generation | 5 | 0 | 5 | 100.0% | 100.0% |
| Rewrite and surface validation | 5 | 1 | 4 | 80.0% | 80.0% |
| DuckDuckGo long-tail filtering | 4 | 3 | 1 | 25.0% | 20.0% |
| Second-stage model grading | 1 | 0 | 1 | 100.0% | 20.0% |
| Shared route-aware validation | 1 | 0 | 1 | 100.0% | 20.0% |
| Deduplication | 1 | 0 | 1 | 100.0% | 20.0% |
| Other rejection | 1 | 0 | 1 | 100.0% | 20.0% |

### Failure Reasons

| Stage | Exact reason | Count |
| --- | --- | ---: |
| `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | 2 |
| `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | 1 |
| `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | 1 |

### Phase Timings

| Phase | Count | Total seconds | Average seconds | Max seconds |
| --- | ---: | ---: | ---: | ---: |
| `candidate_processing_seconds` | 5 | 88.4021 | 17.6804 | 30.4774 |
| `duckduckgo_search_seconds` | 4 | 50.7034 | 12.6759 | 16.5041 |
| `first_paragraph_fetch_seconds` | 5 | 24.9588 | 4.9918 | 9.7639 |
| `llm_question_generation_seconds` | 5 | 36.1700 | 7.2340 | 9.4325 |
| `number_reference_margin_seconds` | 4 | 0.0003 | 0.0001 | 0.0002 |
| `page_fetch_seconds` | 5 | 64.6658 | 12.9332 | 18.3780 |
| `rewrite_seconds` | 5 | 37.6890 | 7.5378 | 13.9662 |
| `table_parse_seconds` | 5 | 6.0399 | 1.2080 | 1.7455 |
| `total_generation_seconds` | 5 | 132.4618 | 26.4924 | 37.5511 |
| `total_processing_seconds` | 5 | 88.4021 | 17.6804 | 30.4774 |

## Accepted Candidates

| Page ID | Question | Answer | Source |
| ---: | --- | --- | --- |
| 21355232 | Which U.S. state has the greatest number of national parks according to the List of national parks of the United States? | California | https://en.wikipedia.org/wiki/List_of_national_parks_of_the_United_States |

## Rejected And Rerun Decisions

| Page ID | Stage | Exact reason | Page/question |
| ---: | --- | --- | --- |
| 32611 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What year saw the highest number of military deaths for South Vietnam during the Vietnam War from 1955 to 1975? |
| 17416221 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which province in South Africa had the largest population according to 2022 data? |
| 199445 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | What year did Wayne Rooney score the highest number of goals for the England national team? |
| 66958 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | What was the daily volume proportion of the Renminbi in global foreign exchange market turnover in April 2025? |

