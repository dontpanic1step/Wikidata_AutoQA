# Route 3 Streaming Wikipedia Page-ID Walkthrough - 2026-05-19

## Stats

- Mode: `random_page_ids`
- Attempted page IDs: 40
- Accepted QAs: 0
- Rejected QAs/pages: 40
- Returned to rerun pool without final decision: 0
- Page-id bounds: 1 to 80000000
- Stream state: `outputs\wikipedia_stream_random40_state.json`
- Accepted output: `outputs\wikipedia_stream_random40_accepted.jsonl`
- Rejected output: `outputs\wikipedia_stream_random40_rejected.jsonl`
- Domain policy: `domain_and_subdomain_optional_for_random_page_id_streaming`

### Survival By Layer

| Layer | Entered | Failed | Survived | Layer survival | Cumulative survival |
| --- | ---: | ---: | ---: | ---: | ---: |
| Page-id reservation | 40 | 0 | 40 | 100.0% | 100.0% |
| Unresolved or returned to rerun pool | 40 | 0 | 40 | 100.0% | 100.0% |
| Page extraction, table grading, and QA generation | 40 | 40 | 0 | 0.0% | 0.0% |
| Rewrite and surface validation | 0 | 0 | 0 | 0.0% | 0.0% |
| DuckDuckGo long-tail filtering | 0 | 0 | 0 | 0.0% | 0.0% |
| Second-stage model grading | 0 | 0 | 0 | 0.0% | 0.0% |
| Shared route-aware validation | 0 | 0 | 0 | 0.0% | 0.0% |
| Deduplication | 0 | 0 | 0 | 0.0% | 0.0% |
| Other rejection | 0 | 0 | 0 | 0.0% | 0.0% |

### Failure Reasons

| Stage | Exact reason | Count |
| --- | --- | ---: |
| `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | 40 |

### Phase Timings

| Phase | Count | Total seconds | Average seconds | Max seconds |
| --- | ---: | ---: | ---: | ---: |
| `candidate_processing_seconds` | 40 | 0.0000 | 0.0000 | 0.0000 |
| `total_generation_seconds` | 40 | 1.4469 | 0.0362 | 0.0776 |
| `total_processing_seconds` | 40 | 0.0000 | 0.0000 | 0.0000 |

## Accepted Candidates

No accepted candidates in this run.

## Rejected And Rerun Decisions

| Page ID | Stage | Exact reason | Page/question |
| ---: | --- | --- | --- |
| 22978779 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=22978779 |
| 45727649 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=45727649 |
| 73448318 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=73448318 |
| 79171450 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=79171450 |
| 62659710 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=62659710 |
| 59651956 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=59651956 |
| 30479038 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=30479038 |
| 16853067 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=16853067 |
| 43920070 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=43920070 |
| 51481392 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=51481392 |
| 34704627 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=34704627 |
| 74262329 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=74262329 |
| 71931420 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=71931420 |
| 75905861 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=75905861 |
| 6997931 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=6997931 |
| 22060856 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=22060856 |
| 34612076 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=34612076 |
| 5968844 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=5968844 |
| 69456847 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=69456847 |
| 58767698 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=58767698 |
| 2942266 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=2942266 |
| 79642122 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=79642122 |
| 54727528 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=54727528 |
| 16516792 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=16516792 |
| 9940679 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=9940679 |
| 67492275 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=67492275 |
| 39407085 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=39407085 |
| 9942806 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=9942806 |
| 71529407 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=71529407 |
| 66010827 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=66010827 |
| 66635972 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=66635972 |
| 71491929 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=71491929 |
| 37166529 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=37166529 |
| 75630307 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=75630307 |
| 25975405 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=25975405 |
| 37732663 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=37732663 |
| 59352406 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=59352406 |
| 3736228 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=3736228 |
| 8179036 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=8179036 |
| 5839157 | `route_generation` | `wikipedia_infobox_generation_error:URLError:<urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>` | https://en.wikipedia.org/w/index.php?curid=5839157 |

