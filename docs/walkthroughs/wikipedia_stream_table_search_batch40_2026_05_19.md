# Route 3 Streaming Wikipedia Page-ID Walkthrough - 2026-05-19

## Stats

- Mode: `page_id_stream`
- Page source: `table-search`
- Table-search queries: `insource:"wikitable"; insource:/\{\|/`
- Attempted page IDs: 40
- Accepted QAs: 12
- Rejected QAs/pages: 28
- Returned to rerun pool without final decision: 0
- Page-id bounds: 1 to 80000000
- Stream state: `outputs\wikipedia_stream_table_search_batch40_2026_05_19_state.json`
- Accepted output: `outputs\wikipedia_stream_table_search_batch40_2026_05_19_accepted.jsonl`
- Rejected output: `outputs\wikipedia_stream_table_search_batch40_2026_05_19_rejected.jsonl`
- Domain policy: `domain_and_subdomain_optional_for_page_id_streaming`

### Survival By Layer

| Layer | Entered | Failed | Survived | Layer survival | Cumulative survival |
| --- | ---: | ---: | ---: | ---: | ---: |
| Page-id reservation | 40 | 0 | 40 | 100.0% | 100.0% |
| Unresolved or returned to rerun pool | 40 | 0 | 40 | 100.0% | 100.0% |
| Page extraction, table grading, and QA generation | 40 | 9 | 31 | 77.5% | 77.5% |
| Rewrite and surface validation | 31 | 3 | 28 | 90.3% | 70.0% |
| DuckDuckGo long-tail filtering | 28 | 16 | 12 | 42.9% | 30.0% |
| Second-stage model grading | 12 | 0 | 12 | 100.0% | 30.0% |
| Shared route-aware validation | 12 | 0 | 12 | 100.0% | 30.0% |
| Deduplication | 12 | 0 | 12 | 100.0% | 30.0% |
| Other rejection | 12 | 0 | 12 | 100.0% | 30.0% |

### Failure Reasons

| Stage | Exact reason | Count |
| --- | --- | ---: |
| `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | 9 |
| `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1017)>` | 7 |
| `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | 3 |
| `search_longtail` | `search_longtail_verifier_error` | 3 |
| `route_generation` | `wikipedia_infobox_generation_error:RemoteDisconnected:Remote end closed connection without response` | 2 |
| `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | 1 |
| `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | 1 |
| `search_longtail` | `search_longtail_verifier_rejected:keyword_query_2:answer_in_title` | 1 |
| `search_longtail` | `search_longtail_verifier_rejected:keyword_query_3:answer_in_title` | 1 |

### Phase Timings

| Phase | Count | Total seconds | Average seconds | Max seconds |
| --- | ---: | ---: | ---: | ---: |
| `candidate_processing_seconds` | 40 | 669.0571 | 16.7264 | 66.3116 |
| `duckduckgo_search_seconds` | 28 | 434.2138 | 15.5076 | 62.7081 |
| `first_paragraph_fetch_seconds` | 38 | 162.0486 | 4.2644 | 15.4562 |
| `llm_question_generation_seconds` | 31 | 230.0593 | 7.4213 | 18.8753 |
| `number_reference_margin_seconds` | 28 | 0.0010 | 0.0000 | 0.0002 |
| `page_fetch_seconds` | 38 | 301.9729 | 7.9467 | 50.2617 |
| `rewrite_seconds` | 31 | 234.7596 | 7.5729 | 22.3765 |
| `table_parse_seconds` | 38 | 37.4810 | 0.9863 | 2.6506 |
| `total_generation_seconds` | 40 | 923.1481 | 23.0787 | 75.0495 |
| `total_processing_seconds` | 40 | 669.0571 | 16.7264 | 66.3116 |

## Accepted Candidates

| Page ID | Question | Answer | Source |
| ---: | --- | --- | --- |
| 9316 | What language ranks second in number of native speakers in England? | Polish | https://en.wikipedia.org/wiki/England |
| 22093 | Which National Basketball Association team has the arena with the largest seating capacity? | Chicago Bulls | https://en.wikipedia.org/wiki/National_Basketball_Association |
| 199445 | For which club did Wayne Rooney score the highest number of league goals? | Manchester United | https://en.wikipedia.org/wiki/Wayne_Rooney |
| 21355232 | Which U.S. state has the greatest number of national parks according to the List of national parks of the United States? | California | https://en.wikipedia.org/wiki/List_of_national_parks_of_the_United_States |
| 45367389 | What country of birth has the second largest population in Greater London according to the 2021 United Kingdom Census? | India | https://en.wikipedia.org/wiki/Greater_London |
| 55440889 | What cellular network generation supported by Pixel 2 uses the LTE-FDD standard? | 4G | https://en.wikipedia.org/wiki/Pixel_2 |
| 235916 | In which films did Jada Pinkett Smith voice the character Gloria? | Madagascar; Madagascar: Escape 2 Africa; Madagascar 3: Europe's Most Wanted; Penguins of Madagascar | https://en.wikipedia.org/wiki/Jada_Pinkett_Smith |
| 342334 | Which finding in stroke can be present for the longest duration? | Mononuclear inflammatory cells; Macrophages | https://en.wikipedia.org/wiki/Autopsy |
| 17278765 | Which school has won the highest number of College football national championships in NCAA Division I FBS since 1936? | Alabama | https://en.wikipedia.org/wiki/College_football_national_championships_in_NCAA_Division_I_FBS |
| 68761 | Which country published the highest total number of titles in 2022? | Turkey | https://en.wikipedia.org/wiki/Publishing |
| 214179 | Who was an additional or touring musician for Ministry active in 1988 and contributed to the album 'The Mind Is a Terrible Thing to Taste'? | Jeff Ward | https://en.wikipedia.org/wiki/Ministry_(band) |
| 324 | What year had the highest number of viewers in millions for the Academy Awards television ratings? | 1998 | https://en.wikipedia.org/wiki/Academy_Awards |

## Rejected And Rerun Decisions

| Page ID | Stage | Exact reason | Page/question |
| ---: | --- | --- | --- |
| 32611 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What year saw the highest number of military deaths for South Vietnam during the Vietnam War from 1955 to 1975? |
| 17416221 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which province in South Africa had the largest population according to 2022 data? |
| 5489 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which region in Chile has the largest population? |
| 31740 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | Which academic year between 2013 and 2026 had the highest total enrollment at the University of Michigan-Ann Arbor? |
| 8083 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which work won Dr. Dre the Grammy Award for Best Rap Solo Performance? |
| 292259 | `route_generation` | `wikipedia_infobox_generation_error:RemoteDisconnected:Remote end closed connection without response` | https://en.wikipedia.org/w/index.php?pageid=292259 |
| 66958 | `route_generation` | `wikipedia_infobox_generation_error:RemoteDisconnected:Remote end closed connection without response` | https://en.wikipedia.org/w/index.php?pageid=66958 |
| 41853326 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | Who was the top goalscorer for Inter Miami CF in the 2025 MLS season? |
| 60382764 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What year is Reiwa 4 in the Japanese calendar? |
| 105908 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What model year of the Ford Mustang had the highest US sales in the 1970s? |
| 22948 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Who is the child of Poseidon and Amphitrite? |
| 84952 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | On what date did Marvelous Marvin Hagler have his final professional boxing match? |
| 2924002 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_2:answer_in_title` | Which organization is responsible for presenting the Top 100 DJs poll in electronic dance music? |
| 569459 | `search_longtail` | `search_longtail_verifier_error` | How many subspecies does the white-tailed deer have? |
| 105391 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1017)>` | https://en.wikipedia.org/w/index.php?pageid=105391 |
| 156745 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1017)>` | https://en.wikipedia.org/w/index.php?pageid=156745 |
| 599 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1017)>` | https://en.wikipedia.org/w/index.php?pageid=599 |
| 151451 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1017)>` | https://en.wikipedia.org/w/index.php?pageid=151451 |
| 7549995 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which U.S. state has the largest estimated population of elk? |
| 43088 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | What year did Yogi Berra manage the New York Yankees and lose the World Series to the St. Louis Cardinals? |
| 80482 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_3:answer_in_title` | Who was the Prime Minister with the longest continuous term during the reign of Beatrix of the Netherlands? |
| 32005912 | `search_longtail` | `search_longtail_verifier_error` | What year did Grimes play Princess Peach on Saturday Night Live? |
| 57877 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1017)>` | https://en.wikipedia.org/w/index.php?pageid=57877 |
| 407239 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1017)>` | https://en.wikipedia.org/w/index.php?pageid=407239 |
| 13270 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | Which island in Hawaii has the highest maximum elevation? |
| 13277 | `search_longtail` | `search_longtail_verifier_error` | Which state had the largest population in the Holy Roman Empire during the early 17th century? |
| 380845 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | Which country has the highest GDP forecast by the IMF for the year 2026? |
| 19261 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1017)>` | https://en.wikipedia.org/w/index.php?pageid=19261 |

