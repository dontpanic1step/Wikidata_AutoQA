# Route 3 Streaming Wikipedia Page-ID Walkthrough - 2026-05-22

## Stats

- Run group ID: `wikipedia_stream_recipe_40_each_answer_type_single_fact_2026_05_22`
- Run segment ID: `recipe_combined`
- Artifact manifest: ``
- Mode: `page_id_stream_recipe`
- Page source: `table-search`
- Table-search queries: `insource:"wikitable"`
- Attempted page IDs: 335
- Unique attempted page IDs: 40
- Stream state reset at run start: yes
- Auto rerun pool once: yes
- Auto-rerun attempted page IDs: 0
- Accepted QAs: 0
- Rejected QAs/pages: 65
- Transient rerun attempts during run: 0
- Wall-clock runtime: 748.1519s
- DuckDuckGo top K: 5
- Generated search queries per QA: 3
- DuckDuckGo parallel queries: 3
- Route 3 reasoning_type constraint: `single_fact`
- Route 3 answer_type constraint: `Person, Place, Other, Date, Number`
- Route 3 table filter modes: `no_big_numbers, no_social_science_research`
- Page-id bounds: None to None
- Stream state: `separate_segment_stream_states`
- Accepted output: `D:\Study\AI\My-research\Wikidata_Framework\outputs\wikipedia_stream_recipe_40_each_answer_type_single_fact_2026_05_22_accepted.jsonl`
- Rejected output: `D:\Study\AI\My-research\Wikidata_Framework\outputs\wikipedia_stream_recipe_40_each_answer_type_single_fact_2026_05_22_rejected.jsonl`
- Domain policy: `domain_and_subdomain_optional_for_page_id_streaming`
- Rerun pool after run: `empty`

### Recipe Segments

| Configured answer_type | Record limit | Attempted page IDs | Accepted | Rejected | Rerun |
| --- | ---: | ---: | ---: | ---: | ---: |
| Person | 40 | 67 | 0 | 13 | 0 |
| Place | 40 | 67 | 0 | 13 | 0 |
| Other | 40 | 67 | 0 | 13 | 0 |
| Date | 40 | 67 | 0 | 13 | 0 |
| Number | 40 | 67 | 0 | 13 | 0 |

### Survival By Layer

| Layer | Entered | Failed | Survived | Layer survival | Cumulative survival |
| --- | ---: | ---: | ---: | ---: | ---: |
| Page-id reservation | 335 | 0 | 335 | 100.0% | 100.0% |
| Unresolved or returned to rerun pool | 335 | 0 | 335 | 100.0% | 100.0% |
| Page extraction, table grading, and QA generation | 335 | 65 | 270 | 80.6% | 80.6% |
| Rewrite and surface validation | 270 | 0 | 270 | 100.0% | 80.6% |
| DuckDuckGo long-tail filtering | 270 | 0 | 270 | 100.0% | 80.6% |
| Second-stage model grading | 270 | 0 | 270 | 100.0% | 80.6% |
| Shared route-aware validation | 270 | 0 | 270 | 100.0% | 80.6% |
| Deduplication | 270 | 0 | 270 | 100.0% | 80.6% |
| Other rejection | 270 | 0 | 270 | 100.0% | 80.6% |

### Failure Reasons

| Stage | Reason | Count |
| --- | --- | ---: |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_social_science_research` | 35 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers` | 30 |

### Answer Type Stats

| Scope | Answer type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `unknown` | 0 | 65 | 65 | 0.0% |

### Reasoning Type Stats

| Scope | Reasoning type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `single_fact` | 0 | 65 | 65 | 0.0% |

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
| `candidate_processing_seconds` | 65 | 0.0000 | 0.0000 | 0.0000 |
| `page_fetch_seconds` | 65 | 9.9269 | 0.1527 | 0.6161 |
| `table_parse_seconds` | 65 | 216.0832 | 3.3244 | 8.9982 |
| `total_generation_seconds` | 65 | 259.5233 | 3.9927 | 10.0570 |
| `total_processing_seconds` | 65 | 0.0000 | 0.0000 | 0.0000 |

## Accepted Candidates

No accepted candidates in this run.
## Second-Stage Filtering Responses

These are the small-model QA responses used by the second-stage filter: `openai/gpt-4.1-mini` and `google/gemini-3-flash-preview`.

| Page ID | Question | Reference answer | openai/gpt-4.1-mini | google/gemini-3-flash-preview |
| ---: | --- | --- | --- | --- |
| 9316 | England |  | not run | not run |
| 17416221 | South Africa |  | not run | not run |
| 32611 | Vietnam War |  | not run | not run |
| 5489 | Chile |  | not run | not run |
| 13277 | Holy Roman Empire |  | not run | not run |
| 11857 | George Lucas |  | not run | not run |
| 40010153 | Goa |  | not run | not run |
| 39776 | Denial-of-service attack |  | not run | not run |
| 5488 | Chad |  | not run | not run |
| 105908 | Ford Mustang |  | not run | not run |
| 5643 | Channel Islands |  | not run | not run |
| 12186 | Guinea-Bissau |  | not run | not run |
| 55440889 | Pixel 2 |  | not run | not run |
| 9316 | England |  | not run | not run |
| 17416221 | South Africa |  | not run | not run |
| 32611 | Vietnam War |  | not run | not run |
| 5489 | Chile |  | not run | not run |
| 13277 | Holy Roman Empire |  | not run | not run |
| 11857 | George Lucas |  | not run | not run |
| 40010153 | Goa |  | not run | not run |
| 39776 | Denial-of-service attack |  | not run | not run |
| 5488 | Chad |  | not run | not run |
| 105908 | Ford Mustang |  | not run | not run |
| 5643 | Channel Islands |  | not run | not run |
| 12186 | Guinea-Bissau |  | not run | not run |
| 55440889 | Pixel 2 |  | not run | not run |
| 9316 | England |  | not run | not run |
| 17416221 | South Africa |  | not run | not run |
| 32611 | Vietnam War |  | not run | not run |
| 5489 | Chile |  | not run | not run |
| 13277 | Holy Roman Empire |  | not run | not run |
| 11857 | George Lucas |  | not run | not run |
| 40010153 | Goa |  | not run | not run |
| 39776 | Denial-of-service attack |  | not run | not run |
| 5488 | Chad |  | not run | not run |
| 105908 | Ford Mustang |  | not run | not run |
| 5643 | Channel Islands |  | not run | not run |
| 12186 | Guinea-Bissau |  | not run | not run |
| 55440889 | Pixel 2 |  | not run | not run |
| 9316 | England |  | not run | not run |
| 17416221 | South Africa |  | not run | not run |
| 32611 | Vietnam War |  | not run | not run |
| 5489 | Chile |  | not run | not run |
| 13277 | Holy Roman Empire |  | not run | not run |
| 11857 | George Lucas |  | not run | not run |
| 40010153 | Goa |  | not run | not run |
| 39776 | Denial-of-service attack |  | not run | not run |
| 5488 | Chad |  | not run | not run |
| 105908 | Ford Mustang |  | not run | not run |
| 5643 | Channel Islands |  | not run | not run |
| 12186 | Guinea-Bissau |  | not run | not run |
| 55440889 | Pixel 2 |  | not run | not run |
| 9316 | England |  | not run | not run |
| 17416221 | South Africa |  | not run | not run |
| 32611 | Vietnam War |  | not run | not run |
| 5489 | Chile |  | not run | not run |
| 13277 | Holy Roman Empire |  | not run | not run |
| 11857 | George Lucas |  | not run | not run |
| 40010153 | Goa |  | not run | not run |
| 39776 | Denial-of-service attack |  | not run | not run |
| 5488 | Chad |  | not run | not run |
| 105908 | Ford Mustang |  | not run | not run |
| 5643 | Channel Islands |  | not run | not run |
| 12186 | Guinea-Bissau |  | not run | not run |
| 55440889 | Pixel 2 |  | not run | not run |


## Rejected And Rerun Decisions

| Page ID | Stage | Exact reason | Page/question |
| ---: | --- | --- | --- |
| 9316 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=3;no_social_science_research:population` | England |
| 17416221 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=km;no_social_science_research:population` | South Africa |
| 32611 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=24` | Vietnam War |
| 5489 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=km;no_social_science_research:population` | Chile |
| 13277 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=9;no_social_science_research:population` | Holy Roman Empire |
| 11857 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=1` | George Lucas |
| 40010153 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=2` | Goa |
| 39776 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=2` | Denial-of-service attack |
| 5488 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=20;no_social_science_research:census,population` | Chad |
| 105908 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=10` | Ford Mustang |
| 5643 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=acres,km,mi;no_social_science_research:population` | Channel Islands |
| 12186 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=10;no_social_science_research:population` | Guinea-Bissau |
| 55440889 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=g` | Pixel 2 |
| 9316 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=3;no_social_science_research:population` | England |
| 17416221 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=km;no_social_science_research:population` | South Africa |
| 32611 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=24` | Vietnam War |
| 5489 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=km;no_social_science_research:population` | Chile |
| 13277 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=9;no_social_science_research:population` | Holy Roman Empire |
| 11857 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=1` | George Lucas |
| 40010153 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=2` | Goa |
| 39776 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=2` | Denial-of-service attack |
| 5488 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=20;no_social_science_research:census,population` | Chad |
| 105908 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=10` | Ford Mustang |
| 5643 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=acres,km,mi;no_social_science_research:population` | Channel Islands |
| 12186 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=10;no_social_science_research:population` | Guinea-Bissau |
| 55440889 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=g` | Pixel 2 |
| 9316 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=3;no_social_science_research:population` | England |
| 17416221 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=km;no_social_science_research:population` | South Africa |
| 32611 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=24` | Vietnam War |
| 5489 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=km;no_social_science_research:population` | Chile |
| 13277 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=9;no_social_science_research:population` | Holy Roman Empire |
| 11857 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=1` | George Lucas |
| 40010153 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=2` | Goa |
| 39776 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=2` | Denial-of-service attack |
| 5488 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=20;no_social_science_research:census,population` | Chad |
| 105908 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=10` | Ford Mustang |
| 5643 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=acres,km,mi;no_social_science_research:population` | Channel Islands |
| 12186 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=10;no_social_science_research:population` | Guinea-Bissau |
| 55440889 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=g` | Pixel 2 |
| 9316 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=3;no_social_science_research:population` | England |
| 17416221 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=km;no_social_science_research:population` | South Africa |
| 32611 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=24` | Vietnam War |
| 5489 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=km;no_social_science_research:population` | Chile |
| 13277 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=9;no_social_science_research:population` | Holy Roman Empire |
| 11857 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=1` | George Lucas |
| 40010153 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=2` | Goa |
| 39776 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=2` | Denial-of-service attack |
| 5488 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=20;no_social_science_research:census,population` | Chad |
| 105908 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=10` | Ford Mustang |
| 5643 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=acres,km,mi;no_social_science_research:population` | Channel Islands |
| 12186 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=10;no_social_science_research:population` | Guinea-Bissau |
| 55440889 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=g` | Pixel 2 |
| 9316 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=3;no_social_science_research:population` | England |
| 17416221 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=km;no_social_science_research:population` | South Africa |
| 32611 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=24` | Vietnam War |
| 5489 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=km;no_social_science_research:population` | Chile |
| 13277 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=9;no_social_science_research:population` | Holy Roman Empire |
| 11857 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=1` | George Lucas |
| 40010153 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=2` | Goa |
| 39776 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=2` | Denial-of-service attack |
| 5488 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=20;no_social_science_research:census,population` | Chad |
| 105908 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=10` | Ford Mustang |
| 5643 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=acres,km,mi;no_social_science_research:population` | Channel Islands |
| 12186 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=10;no_social_science_research:population` | Guinea-Bissau |
| 55440889 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=g` | Pixel 2 |


