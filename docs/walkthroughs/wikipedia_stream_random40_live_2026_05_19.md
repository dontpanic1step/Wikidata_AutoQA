# Route 3 Streaming Wikipedia Page-ID Walkthrough - 2026-05-19

## Stats

- Mode: `random_page_ids`
- Attempted page IDs: 40
- Accepted QAs: 4
- Rejected QAs/pages: 36
- Returned to rerun pool without final decision: 0
- Page-id bounds: 1 to 80000000
- Stream state: `outputs\wikipedia_stream_random40_live_state.json`
- Accepted output: `outputs\wikipedia_stream_random40_live_accepted.jsonl`
- Rejected output: `outputs\wikipedia_stream_random40_live_rejected.jsonl`
- Domain policy: `domain_and_subdomain_optional_for_random_page_id_streaming`

### Survival By Layer

| Layer | Entered | Failed | Survived | Layer survival | Cumulative survival |
| --- | ---: | ---: | ---: | ---: | ---: |
| Page-id reservation | 40 | 0 | 40 | 100.0% | 100.0% |
| Unresolved or returned to rerun pool | 40 | 0 | 40 | 100.0% | 100.0% |
| Page extraction, table grading, and QA generation | 40 | 34 | 6 | 15.0% | 15.0% |
| Rewrite and surface validation | 6 | 2 | 4 | 66.7% | 10.0% |
| DuckDuckGo long-tail filtering | 4 | 0 | 4 | 100.0% | 10.0% |
| Second-stage model grading | 4 | 0 | 4 | 100.0% | 10.0% |
| Shared route-aware validation | 4 | 0 | 4 | 100.0% | 10.0% |
| Deduplication | 4 | 0 | 4 | 100.0% | 10.0% |
| Other rejection | 4 | 0 | 4 | 100.0% | 10.0% |

### Failure Reasons

| Stage | Exact reason | Count |
| --- | --- | ---: |
| `route_generation` | `wikipedia_infobox_no_tables` | 29 |
| `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1017)>` | 5 |
| `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | 1 |
| `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | 1 |

### Phase Timings

| Phase | Count | Total seconds | Average seconds | Max seconds |
| --- | ---: | ---: | ---: | ---: |
| `candidate_processing_seconds` | 40 | 55.8360 | 1.3959 | 14.3028 |
| `duckduckgo_search_seconds` | 4 | 27.4402 | 6.8601 | 9.3460 |
| `first_paragraph_fetch_seconds` | 35 | 89.9753 | 2.5707 | 7.4035 |
| `llm_question_generation_seconds` | 6 | 63.1817 | 10.5303 | 23.0904 |
| `number_reference_margin_seconds` | 4 | 0.0001 | 0.0000 | 0.0001 |
| `page_fetch_seconds` | 38 | 148.1528 | 3.8988 | 13.8241 |
| `rewrite_seconds` | 6 | 28.3843 | 4.7307 | 7.4920 |
| `table_parse_seconds` | 35 | 1.3517 | 0.0386 | 0.6908 |
| `total_generation_seconds` | 40 | 328.4581 | 8.2115 | 30.4189 |
| `total_processing_seconds` | 40 | 55.8360 | 1.3959 | 14.3028 |

## Accepted Candidates

| Page ID | Question | Answer | Source |
| ---: | --- | --- | --- |
| 58767698 | Who was the President of Zhejiang University before Wu Zhaohui? | Lin Jianhua | https://en.wikipedia.org/wiki/Wu_Zhaohui |
| 2942266 | What is the maximum elevation in metres of Larceveau-Arros-Cibits? | 642 | https://en.wikipedia.org/wiki/Larceveau-Arros-Cibits |
| 16516792 | Who was the architect of Belém Palace? | João Pedro Ludovice | https://en.wikipedia.org/wiki/Belém_Palace |
| 37166529 | What is the highest effective radiated power in watts of WLMD (FM)? | 3300 | https://en.wikipedia.org/wiki/WLMD_(FM) |

## Rejected And Rerun Decisions

| Page ID | Stage | Exact reason | Page/question |
| ---: | --- | --- | --- |
| 22978779 | `route_generation` | `wikipedia_infobox_no_tables` | User talk:199.44.92.66 |
| 45727649 | `route_generation` | `wikipedia_infobox_no_tables` | User talk:Adrianofrazao~enwiki |
| 73448318 | `route_generation` | `wikipedia_infobox_no_tables` | https://en.wikipedia.org/w/index.php?curid=73448318 |
| 79171450 | `route_generation` | `wikipedia_infobox_no_tables` | Talk:James Ponder (disambiguation) |
| 62659710 | `route_generation` | `wikipedia_infobox_no_tables` | User talk:2A02:C7D:81F8:8C00:4582:D38:D284:F149 |
| 59651956 | `route_generation` | `wikipedia_infobox_no_tables` | https://en.wikipedia.org/w/index.php?curid=59651956 |
| 30479038 | `route_generation` | `wikipedia_infobox_no_tables` | Category talk:English women writers |
| 16853067 | `route_generation` | `wikipedia_infobox_no_tables` | https://en.wikipedia.org/w/index.php?curid=16853067 |
| 43920070 | `route_generation` | `wikipedia_infobox_no_tables` | Torkil Åmland |
| 51481392 | `route_generation` | `wikipedia_infobox_no_tables` | Module talk:Location map/data/United Kingdom London Newham |
| 34704627 | `route_generation` | `wikipedia_infobox_no_tables` | Ernst-Meister-Preis für Lyrik |
| 74262329 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1017)>` | https://en.wikipedia.org/w/index.php?curid=74262329 |
| 71931420 | `route_generation` | `wikipedia_infobox_no_tables` | https://en.wikipedia.org/w/index.php?curid=71931420 |
| 75905861 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1017)>` | https://en.wikipedia.org/w/index.php?curid=75905861 |
| 6997931 | `route_generation` | `wikipedia_infobox_no_tables` | User talk:Junkieperfectionist |
| 22060856 | `route_generation` | `wikipedia_infobox_no_tables` | https://en.wikipedia.org/w/index.php?curid=22060856 |
| 34612076 | `route_generation` | `wikipedia_infobox_no_tables` | Talk:Saint Patrick's Day in the United States |
| 5968844 | `route_generation` | `wikipedia_infobox_no_tables` | Talk:Coral Gold Cup |
| 69456847 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1017)>` | https://en.wikipedia.org/w/index.php?curid=69456847 |
| 79642122 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | Which event in 2025 had the largest size value according to User:ClueBot III/Detailed Indices/User talk:Theredproject/Archives/2025 1? |
| 54727528 | `route_generation` | `wikipedia_infobox_no_tables` | Wikipedia:Articles for deletion/Log/2017 August 6 |
| 9940679 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | Who had the longest lifespan based on the birth and death dates listed for Florence L. Barclay? |
| 67492275 | `route_generation` | `wikipedia_infobox_no_tables` | Talk:Sciaphilus |
| 39407085 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1017)>` | https://en.wikipedia.org/w/index.php?curid=39407085 |
| 9942806 | `route_generation` | `wikipedia_infobox_no_tables` | https://en.wikipedia.org/w/index.php?curid=9942806 |
| 71529407 | `route_generation` | `wikipedia_infobox_no_tables` | https://en.wikipedia.org/w/index.php?curid=71529407 |
| 66010827 | `route_generation` | `wikipedia_infobox_no_tables` | User talk:35.134.198.206 |
| 66635972 | `route_generation` | `wikipedia_infobox_no_tables` | https://en.wikipedia.org/w/index.php?curid=66635972 |
| 71491929 | `route_generation` | `wikipedia_infobox_no_tables` | Talk:NAF British Guiana |
| 75630307 | `route_generation` | `wikipedia_infobox_no_tables` | https://en.wikipedia.org/w/index.php?curid=75630307 |
| 25975405 | `route_generation` | `wikipedia_infobox_no_tables` | Focal subgroup theorem |
| 37732663 | `route_generation` | `wikipedia_infobox_no_tables` | Category:Algerian designers |
| 59352406 | `route_generation` | `wikipedia_infobox_no_tables` | User talk:41.222.181.65 |
| 3736228 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1017)>` | https://en.wikipedia.org/w/index.php?curid=3736228 |
| 8179036 | `route_generation` | `wikipedia_infobox_no_tables` | User talk:Joeykry |
| 5839157 | `route_generation` | `wikipedia_infobox_no_tables` | User talk:Radiotycoon |

