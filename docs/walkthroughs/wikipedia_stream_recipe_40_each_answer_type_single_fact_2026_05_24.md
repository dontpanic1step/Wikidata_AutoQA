# Route 3 Streaming Wikipedia Page-ID Walkthrough - 2026-05-24

## Stats

- Run group ID: `wikipedia_stream_recipe_40_each_answer_type_single_fact_2026_05_24`
- Run segment ID: `recipe_combined`
- Artifact manifest: ``
- Mode: `page_id_stream_recipe`
- Page source: `table-search`
- Table-search queries: `insource:"wikitable"`
- Attempted page IDs: 316
- Unique attempted page IDs: 200
- Stream state reset at run start: yes
- Auto rerun pool once: yes
- Auto-rerun attempted page IDs: 0
- Accepted QAs: 0
- Rejected QAs/pages: 84
- Transient rerun attempts during run: 232
- Wall-clock runtime: 415.7223s
- DuckDuckGo top K: 5
- Generated search queries per QA: 3
- DuckDuckGo parallel queries: 3
- Route 3 reasoning_type constraint: `single_fact`
- Route 3 answer_type constraint: `Person, Place, Other, Number, Date`
- Route 3 table filter modes: `no_picture_heavy_tables, no_approximate_tables, no_incomplete_tables, not_number_dominant, no_social_science_research`
- Page-id bounds: None to None
- Stream state: `separate_segment_stream_states`
- Accepted output: `D:\Study\AI\My-research\Wikidata_Framework\outputs\wikipedia_stream_recipe_40_each_answer_type_single_fact_2026_05_24_accepted.jsonl`
- Rejected output: `D:\Study\AI\My-research\Wikidata_Framework\outputs\wikipedia_stream_recipe_40_each_answer_type_single_fact_2026_05_24_rejected.jsonl`
- Domain policy: `domain_and_subdomain_optional_for_page_id_streaming`
- Rerun pool after run: `599, 1064, 1640, 5643, 8083, 10134, 12628, 14849, 15049, 16384, 17740, 21026, 22948, 26873, 26941, 30217, 30292, 30374, 30403, 30418, 30498, 31740, 31924, 34556, 38264, 43088, 43710, 45576, 47734, 53273, 53762, 56636, 57659, 58846, 59385, 66524, 66958, 67749, 76988, 79915, 80482, 84952, 85099, 91195, 92408, 96875, 101965, 129619, 143759, 144968, 151451, 151603, 156745, 158177, 158595, 168263, 168576, 169833, 184860, 188257, 188746, 191280, 199445, 211917, 217231, 218746, 225502, 232863, 235916, 235959, 250858, 255627, 260996, 276433, 292259, 306724, 339183, 359520, 363002, 385155, 400595, 420162, 439959, 481605, 481708, 485429, 521984, 540317, 563616, 662351, 682403, 904826, 2186423, 2924002, 15868164, 17278765, 18482905, 18947898, 19653842, 20556859, 20646803, 21189337, 21355232, 23473595, 23976719, 24109126, 36762240, 36991518, 38962787, 40218034, 41853326, 43745773, 46735704, 47864412, 60382764, 63376140`

### Recipe Segments

| Configured answer_type | Record limit | Attempted page IDs | Accepted | Rejected | Rerun |
| --- | ---: | ---: | ---: | ---: | ---: |
| Person | 40 | 62 | 0 | 18 | 44 |
| Place | 40 | 61 | 0 | 19 | 42 |
| Other | 40 | 66 | 0 | 14 | 52 |
| Number | 40 | 64 | 0 | 16 | 48 |
| Date | 40 | 63 | 0 | 17 | 46 |

### Survival By Layer

| Layer | Entered | Failed | Survived | Layer survival | Cumulative survival |
| --- | ---: | ---: | ---: | ---: | ---: |
| Page-id reservation | 316 | 0 | 316 | 100.0% | 100.0% |
| Unresolved or returned to rerun pool | 316 | 0 | 316 | 100.0% | 100.0% |
| Page extraction, table grading, and QA generation | 316 | 84 | 232 | 73.4% | 73.4% |
| Rewrite and surface validation | 232 | 0 | 232 | 100.0% | 73.4% |
| DuckDuckGo long-tail filtering | 232 | 0 | 232 | 100.0% | 73.4% |
| Second-stage model grading | 232 | 0 | 232 | 100.0% | 73.4% |
| Shared route-aware validation | 232 | 0 | 232 | 100.0% | 73.4% |
| Deduplication | 232 | 0 | 232 | 100.0% | 73.4% |
| Other rejection | 232 | 0 | 232 | 100.0% | 73.4% |

### Failure Reasons

| Stage | Reason | Count |
| --- | --- | ---: |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant` | 50 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables` | 19 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | 4 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:active` | 2 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:present` | 2 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | 2 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_approximate_tables` | 2 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:caption:active` | 1 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:incumbent` | 1 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables` | 1 |

### Answer Type Stats

| Scope | Answer type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `unknown` | 0 | 84 | 84 | 0.0% |

### Reasoning Type Stats

| Scope | Reasoning type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `single_fact` | 0 | 84 | 84 | 0.0% |

### Rerun Pool After Run

| Page ID | Exact reason |
| ---: | --- |
| 599 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 1064 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 1640 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 5643 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 8083 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 10134 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 12628 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 14849 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 15049 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 16384 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 17740 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 21026 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 22948 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 26873 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 26941 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 30217 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 30292 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 30374 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 30403 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 30418 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 30498 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 31740 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 31924 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 34556 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 38264 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 43088 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 43710 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 45576 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 47734 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 53273 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 53762 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 56636 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 57659 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 58846 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 59385 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 66524 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 66958 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 67749 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 76988 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 79915 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 80482 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 84952 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 85099 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 91195 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 92408 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 96875 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 101965 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 129619 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 143759 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 144968 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 151451 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 151603 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 156745 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 158177 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 158595 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 168263 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 168576 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 169833 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 184860 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 188257 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 188746 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 191280 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 199445 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 211917 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 217231 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 218746 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 225502 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 232863 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 235916 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 235959 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 250858 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 255627 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 260996 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 276433 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 292259 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 306724 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 339183 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 359520 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 363002 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 385155 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 400595 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 420162 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 439959 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 481605 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 481708 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 485429 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 521984 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 540317 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 563616 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 662351 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 682403 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 904826 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 2186423 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 2924002 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 15868164 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 17278765 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 18482905 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 18947898 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 19653842 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 20556859 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 20646803 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 21189337 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 21355232 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 23473595 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 23976719 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 24109126 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 36762240 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 36991518 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 38962787 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 40218034 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 41853326 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 43745773 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 46735704 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 47864412 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 60382764 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |
| 63376140 | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` |


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
| `candidate_processing_seconds` | 84 | 0.0000 | 0.0000 | 0.0000 |
| `page_fetch_seconds` | 84 | 13.5648 | 0.1615 | 0.5327 |
| `table_parse_seconds` | 84 | 126.0254 | 1.5003 | 7.2757 |
| `total_generation_seconds` | 84 | 165.2141 | 1.9668 | 8.1804 |
| `total_processing_seconds` | 84 | 0.0000 | 0.0000 | 0.0000 |

## Accepted Candidates

No accepted candidates in this run.
## Second-Stage Filtering Responses

These are the small-model QA responses used by the second-stage filter: `openai/gpt-4.1-mini` and `google/gemini-3-flash-preview`.

| Page ID | Question | Reference answer | openai/gpt-4.1-mini | google/gemini-3-flash-preview |
| ---: | --- | --- | --- | --- |
| 22093 | National Basketball Association |  | not run | not run |
| 9316 | England |  | not run | not run |
| 17416221 | South Africa |  | not run | not run |
| 32611 | Vietnam War |  | not run | not run |
| 5489 | Chile |  | not run | not run |
| 13277 | Holy Roman Empire |  | not run | not run |
| 738 | Albania |  | not run | not run |
| 19261 | Monaco |  | not run | not run |
| 11857 | George Lucas |  | not run | not run |
| 40010153 | Goa |  | not run | not run |
| 39776 | Denial-of-service attack |  | not run | not run |
| 5488 | Chad |  | not run | not run |
| 45367389 | Greater London |  | not run | not run |
| 105908 | Ford Mustang |  | not run | not run |
| 34411 | Zodiac |  | not run | not run |
| 12186 | Guinea-Bissau |  | not run | not run |
| 55440889 | Pixel 2 |  | not run | not run |
| 33094374 | Telecommunications |  | not run | not run |
| 60921 | Battle of the Somme |  | not run | not run |
| 35723752 | PlayStation 4 |  | not run | not run |
| 85023 | Appalachian Mountains |  | not run | not run |
| 34352 | Yerevan |  | not run | not run |
| 65433 | Patagonia |  | not run | not run |
| 101359 | Gatwick Airport |  | not run | not run |
| 149561 | Donna Summer |  | not run | not run |
| 347422 | Republika Srpska |  | not run | not run |
| 39458161 | Xbox One |  | not run | not run |
| 52812 | Humidity |  | not run | not run |
| 5668 | Calcium |  | not run | not run |
| 342334 | Autopsy |  | not run | not run |
| 105391 | B movie |  | not run | not run |
| 569459 | White-tailed deer |  | not run | not run |
| 68761 | Publishing |  | not run | not run |
| 229275 | Lamb and mutton |  | not run | not run |
| 246920 | Visa Inc. |  | not run | not run |
| 2114995 | Dextromethorphan |  | not run | not run |
| 1625048 | Kingdom of Bohemia |  | not run | not run |
| 19006979 | Mac (computer) |  | not run | not run |
| 48235 | Vaudeville |  | not run | not run |
| 39848 | Chevrolet |  | not run | not run |
| 42374 | Ljubljana |  | not run | not run |
| 100180 | Iron Cross |  | not run | not run |
| 1644 | Algiers |  | not run | not run |
| 65153 | Tahiti |  | not run | not run |
| 77432 | Hypertension |  | not run | not run |
| 8080 | List of decades, centuries, and millennia |  | not run | not run |
| 500409 | A Coruña |  | not run | not run |
| 7549995 | Elk |  | not run | not run |
| 57905 | Sakha Republic |  | not run | not run |
| 31730 | British Armed Forces |  | not run | not run |
| 26457880 | Air India |  | not run | not run |
| 276773 | SAP |  | not run | not run |
| 70581 | St. John's, Newfoundland and Labrador |  | not run | not run |
| 5659 | Chemical element |  | not run | not run |
| 5215 | Casino |  | not run | not run |
| 275515 | Mont-Saint-Michel |  | not run | not run |
| 13677 | Hindus |  | not run | not run |
| 4446 | Booker Prize |  | not run | not run |
| 99627 | Mannheim |  | not run | not run |
| 23713759 | Hodgkin lymphoma |  | not run | not run |
| 149349 | Dortmund |  | not run | not run |
| 601399 | Display resolution |  | not run | not run |
| 57877 | Sodium hydroxide |  | not run | not run |
| 32005912 | Grimes |  | not run | not run |
| 214179 | Ministry (band) |  | not run | not run |
| 407239 | The Indian Express |  | not run | not run |
| 35412202 | Wikidata |  | not run | not run |
| 4595356 | 1910 United States census |  | not run | not run |
| 27856145 | Siena |  | not run | not run |
| 195468 | Ring of Fire |  | not run | not run |
| 40880638 | UEFA Euro 2024 |  | not run | not run |
| 2369 | Aston Martin |  | not run | not run |
| 87851 | Stoat |  | not run | not run |
| 19342760 | Seven Wonders of the Ancient World |  | not run | not run |
| 733497 | Hydroxyzine |  | not run | not run |
| 39345917 | Big Hero 6 (film) |  | not run | not run |
| 2209490 | Romanization of Arabic |  | not run | not run |
| 422038 | Vigo |  | not run | not run |
| 23906 | Peterborough |  | not run | not run |
| 67923 | East Sussex |  | not run | not run |
| 1161220 | Khushbu Sundar |  | not run | not run |
| 47498 | All your base are belong to us |  | not run | not run |
| 113933 | Iowa City, Iowa |  | not run | not run |
| 22461 | Osteoporosis |  | not run | not run |


## Rejected And Rerun Decisions

| Page ID | Stage | Exact reason | Page/question |
| ---: | --- | --- | --- |
| 22093 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | National Basketball Association |
| 9316 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=trillion` | England |
| 17416221 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km` | South Africa |
| 32611 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=24` | Vietnam War |
| 5489 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km` | Chile |
| 13277 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=9` | Holy Roman Empire |
| 738 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=13` | Albania |
| 19261 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | Monaco |
| 11857 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | George Lucas |
| 40010153 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=2` | Goa |
| 39776 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=2` | Denial-of-service attack |
| 5488 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:active` | Chad |
| 45367389 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | Greater London |
| 105908 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=10` | Ford Mustang |
| 34411 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=14` | Zodiac |
| 12186 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=10` | Guinea-Bissau |
| 55440889 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=g` | Pixel 2 |
| 33094374 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Telecommunications |
| 60921 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=12` | Battle of the Somme |
| 35723752 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=m` | PlayStation 4 |
| 85023 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=feet,ft,meters` | Appalachian Mountains |
| 34352 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,millimetres` | Yerevan |
| 65433 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km` | Patagonia |
| 101359 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=24` | Gatwick Airport |
| 149561 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=pound` | Donna Summer |
| 347422 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:present` | Republika Srpska |
| 39458161 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Xbox One |
| 52812 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=oz,yd,g` | Humidity |
| 5668 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mg` | Calcium |
| 342334 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:present` | Autopsy |
| 105391 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:active` | B movie |
| 569459 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=1` | White-tailed deer |
| 68761 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=36` | Publishing |
| 229275 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=18` | Lamb and mutton |
| 246920 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million,billion` | Visa Inc. |
| 2114995 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=15` | Dextromethorphan |
| 1625048 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km2` | Kingdom of Bohemia |
| 19006979 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | Mac (computer) |
| 48235 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=1` | Vaudeville |
| 39848 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=41` | Chevrolet |
| 42374 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Ljubljana |
| 100180 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=5` | Iron Cross |
| 1644 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=42` | Algiers |
| 65153 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km,mi` | Tahiti |
| 77432 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Hypertension |
| 8080 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=6` | List of decades, centuries, and millennia |
| 500409 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=feet,metres` | A Coruña |
| 7549995 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=27` | Elk |
| 57905 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=126` | Sakha Republic |
| 31730 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=16` | British Armed Forces |
| 26457880 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=tonnes` | Air India |
| 276773 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=13` | SAP |
| 70581 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,ft,m` | St. John's, Newfoundland and Labrador |
| 5659 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | Chemical element |
| 5215 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=12` | Casino |
| 275515 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:alpha_character_rate=0.2278` | Mont-Saint-Michel |
| 13677 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=12` | Hindus |
| 4446 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=60` | Booker Prize |
| 99627 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:incumbent` | Mannheim |
| 23713759 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_approximate_tables:approximately` | Hodgkin lymphoma |
| 149349 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=19` | Dortmund |
| 601399 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=45` | Display resolution |
| 57877 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ml,g,m` | Sodium hydroxide |
| 32005912 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Grimes |
| 214179 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | Ministry (band) |
| 407239 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_approximate_tables:approximate` | The Indian Express |
| 35412202 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=2` | Wikidata |
| 4595356 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=153` | 1910 United States census |
| 27856145 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=15` | Siena |
| 195468 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:caption:active` | Ring of Fire |
| 40880638 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=54` | UEFA Euro 2024 |
| 2369 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=114` | Aston Martin |
| 87851 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=5` | Stoat |
| 19342760 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:incomplete` | Seven Wonders of the Ancient World |
| 733497 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=2` | Hydroxyzine |
| 39345917 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Big Hero 6 (film) |
| 2209490 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ha,g` | Romanization of Arabic |
| 422038 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,metres,millimetres,m` | Vigo |
| 23906 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=29` | Peterborough |
| 67923 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | East Sussex |
| 1161220 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Khushbu Sundar |
| 47498 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | All your base are belong to us |
| 113933 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Iowa City, Iowa |
| 22461 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Osteoporosis |


