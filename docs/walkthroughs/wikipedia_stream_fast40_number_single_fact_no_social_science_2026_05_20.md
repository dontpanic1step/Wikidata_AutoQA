# Route 3 Streaming Wikipedia Page-ID Walkthrough - 2026-05-20

## Stats

- Run group ID: `wikipedia_stream_fast40_number_single_fact_no_social_science_2026_05_20`
- Run segment ID: `fresh40_number_single_fact_no_social_science_2026_05_20`
- Artifact manifest: `D:\Study\AI\My-research\Wikidata_Framework\outputs\run_manifests\wikipedia_stream_fast40_number_single_fact_no_social_science_2026_05_20.json`
- Mode: `page_id_stream`
- Page source: `table-search`
- Table-search queries: `insource:"wikitable"`
- Attempted page IDs: 40
- Unique attempted page IDs: 40
- Stream state reset at run start: yes
- Auto rerun pool once: yes
- Auto-rerun attempted page IDs: 0
- Accepted QAs: 8
- Rejected QAs/pages: 32
- Transient rerun attempts during run: 0
- Wall-clock runtime: 338.7963s
- DuckDuckGo top K: 5
- Generated search queries per QA: 3
- DuckDuckGo parallel queries: 3
- Minimum Route 3 table score: 0.0
- Route 3 reasoning_type constraint: `single_fact`
- Route 3 answer_type constraint: `Number`
- Route 3 extra prompt rules: `Ask factual questions, not questions about the findings or conclusions of social science research, such as results derived from census studies.`
- Stream page workers: 4
- Wikipedia concurrency limit: 4
- DuckDuckGo service concurrency limit: 4
- OpenRouter generation/rewrite concurrency limit: 10
- Second-stage concurrency limit: 10
- Page-id bounds: 1 to 80000000
- Stream state: `outputs\wikipedia_stream_fast40_number_single_fact_no_social_science_2026_05_20_state.json`
- Accepted output: `outputs\wikipedia_stream_fast40_number_single_fact_no_social_science_2026_05_20_accepted.jsonl`
- Rejected output: `outputs\wikipedia_stream_fast40_number_single_fact_no_social_science_2026_05_20_rejected.jsonl`
- Domain policy: `domain_and_subdomain_optional_for_page_id_streaming`
- Rerun pool after run: `empty`

### Survival By Layer

| Layer | Entered | Failed | Survived | Layer survival | Cumulative survival |
| --- | ---: | ---: | ---: | ---: | ---: |
| Page-id reservation | 40 | 0 | 40 | 100.0% | 100.0% |
| Unresolved or returned to rerun pool | 40 | 0 | 40 | 100.0% | 100.0% |
| Page extraction, table grading, and QA generation | 40 | 5 | 35 | 87.5% | 87.5% |
| Rewrite and surface validation | 35 | 3 | 32 | 91.4% | 80.0% |
| DuckDuckGo long-tail filtering | 32 | 4 | 28 | 87.5% | 70.0% |
| Second-stage model grading | 28 | 20 | 8 | 28.6% | 20.0% |
| Shared route-aware validation | 8 | 0 | 8 | 100.0% | 20.0% |
| Deduplication | 8 | 0 | 8 | 100.0% | 20.0% |
| Other rejection | 8 | 0 | 8 | 100.0% | 20.0% |

### Failure Reasons

| Stage | Exact reason | Count |
| --- | --- | ---: |
| `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | 20 |
| `route_generation` | `wikipedia_infobox_answer_type_not_allowed:answer_type_not_allowed:Number; allowed=Number` | 3 |
| `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | 2 |
| `route_generation` | `wikipedia_infobox_extra_prompt_violation:no_social_science_research_prompt:census` | 2 |
| `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | 2 |
| `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | 1 |
| `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | 1 |
| `search_longtail` | `search_longtail_verifier_rejected:keyword_query_2:answer_in_title` | 1 |

### Answer Type Stats

| Scope | Answer type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `Number` | 8 | 27 | 35 | 22.9% |
| Current Run Records | `unknown` | 0 | 5 | 5 | 0.0% |

### Reasoning Type Stats

| Scope | Reasoning type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `single_fact` | 8 | 27 | 35 | 22.9% |
| Current Run Records | `wikipedia_table_fact` | 0 | 5 | 5 | 0.0% |

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
| `candidate_processing_seconds` | 40 | 704.0063 | 17.6002 | 37.7076 |
| `duckduckgo_search_seconds` | 32 | 208.3282 | 6.5103 | 14.0674 |
| `first_paragraph_extract_seconds` | 40 | 34.6998 | 0.8675 | 2.9930 |
| `llm_question_generation_seconds` | 40 | 273.4801 | 6.8370 | 15.4988 |
| `number_reference_margin_seconds` | 32 | 0.0044 | 0.0001 | 0.0009 |
| `page_fetch_seconds` | 40 | 2.1144 | 0.0529 | 0.2489 |
| `rewrite_seconds` | 35 | 153.4709 | 4.3849 | 10.3290 |
| `second_stage_grading_seconds` | 28 | 342.1702 | 12.2204 | 25.8157 |
| `table_parse_seconds` | 40 | 100.3872 | 2.5097 | 7.5119 |
| `total_generation_seconds` | 40 | 420.1515 | 10.5038 | 17.6324 |
| `total_processing_seconds` | 40 | 704.0063 | 17.6002 | 37.7076 |

## Accepted Candidates

| Page ID | Question | Answer | Source |
| ---: | --- | --- | --- |
| 9316 | How many native speakers of Cornish were there in England according to language data? | 0.6 | https://en.wikipedia.org/wiki/England |
| 13277 | What was the population number of the Duchy of Milan (Spanish) within the Holy Roman Empire in the early 17th century? | 1350000 | https://en.wikipedia.org/wiki/Holy_Roman_Empire |
| 14849 | What was the number of foreign-born residents from Mexico living in Illinois in 2022? | 621541 | https://en.wikipedia.org/wiki/Illinois |
| 40010153 | What was the gross state domestic product in millions of rupees for Goa in 1995? | 33190 | https://en.wikipedia.org/wiki/Goa |
| 12186 | What was the population of the 7th largest city in Guinea-Bissau according to the 2015 estimate? | 12922 | https://en.wikipedia.org/wiki/Guinea-Bissau |
| 55440889 | How many cellular frequency bands does the Pixel 2 support for the 4G LTE-FDD standard? | 19 | https://en.wikipedia.org/wiki/Pixel_2 |
| 2924002 | How many categories does the DJ Awards event nominate and award international DJs in each year? | 11 | https://en.wikipedia.org/wiki/Electronic_dance_music |
| 33094374 | How many million cell phones were sold worldwide in 2004 according to telecommunications equipment sales data? | 660 | https://en.wikipedia.org/wiki/Telecommunications |

## Second-Stage Filtering Responses

These are the small-model QA responses used by the second-stage filter: `openai/gpt-4.1-mini` and `google/gemini-3-flash-preview`.

| Page ID | Question | Reference answer | openai/gpt-4.1-mini | google/gemini-3-flash-preview |
| ---: | --- | --- | --- | --- |
| 9316 | How many native speakers of Cornish were there in England according to language data? | 0.6 (acceptable range: anything between 0.59 and 0.61) | INCORRECT; predicted_answer: Cornish became extinct as a native language in the late 18th century, so there are no native speakers of Cornish in England today according to language data. However, there are several hundred to a few thousand people who speak Cornish as a second language due to revival efforts. | INCORRECT; predicted_answer: According to the 2021 Census for England and Wales, there were **471** people who reported Cornish as their main language. |
| 13277 | What was the population number of the Duchy of Milan (Spanish) within the Holy Roman Empire in the early 17th century? | 1350000 (acceptable range: anything between 1336500 and 1363500) | INCORRECT; predicted_answer: The population of the Duchy of Milan (under Spanish rule) in the early 17th century was approximately 2 to 2.5 million people. | INCORRECT; predicted_answer: In the early 17th century (c. 1600), the population of the Duchy of Milan was approximately **1.1 to 1.2 million** people.  This number declined significantly following the devastating plague of 1629–1630, which killed nearly half the population in major urban centers. |
| 14849 | What was the number of foreign-born residents from Mexico living in Illinois in 2022? | 621541 (acceptable range: anything between 615326 and 627756) | INCORRECT; predicted_answer: In 2022, there were 1,040,000 foreign-born residents from Mexico living in Illinois. | INCORRECT; predicted_answer: In 2022, there were approximately **583,907** foreign-born residents from Mexico living in Illinois. |
| 40010153 | What was the gross state domestic product in millions of rupees for Goa in 1995? | 33190 (acceptable range: anything between 32858 and 33522) | INCORRECT; predicted_answer: The gross state domestic product (GSDP) for Goa in 1995 was 3,230 million rupees. | INCORRECT; predicted_answer: The gross state domestic product (GSDP) for Goa in 1995 (fiscal year 1995–96) was approximately **21,140 million rupees** at current prices. |
| 12186 | What was the population of the 7th largest city in Guinea-Bissau according to the 2015 estimate? | 12922 (acceptable range: anything between 12793 and 13051) | INCORRECT; predicted_answer: The 7th largest city in Guinea-Bissau according to the 2015 estimate was Bafatá, with a population of approximately 24,000. | INCORRECT; predicted_answer: According to 2015 estimates, the 7th largest city in Guinea-Bissau is **Catió**, with a population of approximately **9,814**. |
| 55440889 | How many cellular frequency bands does the Pixel 2 support for the 4G LTE-FDD standard? | 19 (acceptable range: anything between 18 and 20) | INCORRECT; predicted_answer: The Pixel 2 supports 12 cellular frequency bands for the 4G LTE-FDD standard. | INCORRECT; predicted_answer: The Pixel 2 supports **21** cellular frequency bands for the 4G LTE-FDD standard. |
| 2924002 | How many categories does the DJ Awards event nominate and award international DJs in each year? | 11 (acceptable range: anything between 10 and 12) | INCORRECT; predicted_answer: The DJ Awards event nominates and awards international DJs in 16 categories each year. | INCORRECT; predicted_answer: The DJ Awards typically features approximately **20 to 25 categories** each year, though the exact number fluctuates depending on the edition. These categories are generally split between **voted categories** (e.g., Best Deep House, Best Trance) and **special industry awards** (e.g., Lifetime Achievement, Ibiza Night). |
| 33094374 | How many million cell phones were sold worldwide in 2004 according to telecommunications equipment sales data? | 660 (acceptable range: anything between 653 and 667) | INCORRECT; predicted_answer: In 2004, approximately 850 million cell phones were sold worldwide according to telecommunications equipment sales data. | INCORRECT; predicted_answer: Approximately **674 million** mobile phones were sold worldwide in 2004. |
| 22093 | How many National Basketball Association championships have the Boston Celtics won? | 18 | not run | not run |
| 32611 | How many US military deaths occurred in 1968 during the Vietnam War? | 16899 (acceptable range: anything between 16730 and 17068) | CORRECT; predicted_answer: In 1968, there were approximately 16,899 U.S. military deaths during the Vietnam War. | not run |
| 17416221 | What is the total area in square kilometers of the Northern Cape province in South Africa? | 372889 (acceptable range: anything between 369160 and 376618) | CORRECT; predicted_answer: The total area of the Northern Cape province in South Africa is approximately 372,889 square kilometers. | not run |
| 5489 | What is the total area in square kilometers of the Magallanes and Chilean Antarctica region in Chile? | 132297.2 (acceptable range: anything between 130974.228 and 133620.172) | CORRECT; predicted_answer: The total area of the Magallanes and Chilean Antarctica region in Chile is approximately 132,291 square kilometers. | not run |
| 738 | What is the total area in square kilometers of Korçë county in Albania? | 3711 (acceptable range: anything between 3674 and 3748) | CORRECT; predicted_answer: The total area of Korçë County in Albania is approximately 3,711 square kilometers. | not run |
| 11857 | In what year was the film THX 1138 directed by George Lucas released? | 1971 | not run | not run |
| 19261 | How many days per year does Monaco have an average precipitation of at least 1.0 mm based on 1981–2010 climate data? | 62.4 (acceptable range: anything between 61.776 and 63.024) | CORRECT; predicted_answer: Monaco has an average of 62 days per year with at least 1.0 mm of precipitation based on 1981–2010 climate data. | not run |
| 31740 | What was the number of first-time fall freshmen applicants at the University of Michigan, Ann Arbor in 2025? | 109112 | not run | not run |
| 292259 | In what year did Deutsche Welle begin broadcasting in the Pashto language? | 1970 | not run | not run |
| 199445 | How many matches did Wayne Rooney manage for Derby County between 14 November 2020 and 26 June 2022? | 85 | not run | not run |
| 8083 | How many Grammy Awards has Dr. Dre won? | 7 (acceptable range: anything between 6 and 8) | CORRECT; predicted_answer: Dr. Dre has won 7 Grammy Awards. | not run |
| 21355232 | How many national parks are there in California according to the List of national parks of the United States? | 9 (acceptable range: anything between 8 and 10) | CORRECT; predicted_answer: According to the List of national parks of the United States, California has 9 national parks. | not run |
| 5488 | What was the population of the city of Abéché in Chad according to the 2009 census? | 97,963 | not run | not run |
| 39776 | What is the amplification factor of the Memcached protocol in UDP amplification attacks related to denial-of-service attacks? | 50000 (acceptable range: anything between 49500 and 50500) | CORRECT; predicted_answer: The amplification factor of the Memcached protocol in UDP amplification attacks can be extremely high, often reported to be around **50,000 times** or more. This means an attacker can send a small UDP request to a vulnerable Memcached server, which then responds with a payload up to 50,000 times larger, greatly amplifying the volume of traffic directed at the victim in a denial-of-service attack. | not run |
| 1640 | What year did Alfred the Great die? | 899 | not run | not run |
| 151603 | How many episodes of The Colgate Comedy Hour featured Dean Martin? | 28 (acceptable range: anything between 27 and 29) | INCORRECT; predicted_answer: Dean Martin appeared in 45 episodes of The Colgate Comedy Hour. | CORRECT; predicted_answer: Dean Martin appeared in **28** episodes of *The Colgate Comedy Hour* as part of the Martin and Lewis comedy team. |
| 45367389 | According to the 2021 United Kingdom Census, how many people in Greater London were born in Romania? | 175991 | not run | not run |
| 66958 | What was the daily volume percentage of the renminbi in global foreign exchange market turnover in April 2025? | 8.5 | not run | not run |
| 41853326 | How many games did Inter Miami CF play during the 2023 MLS season? | 34 | not run | not run |
| 217231 | How many episodes are in season 7 of Curb Your Enthusiasm? | 10 (acceptable range: anything between 9 and 11) | CORRECT; predicted_answer: Season 7 of *Curb Your Enthusiasm* has 10 episodes. | not run |
| 60382764 | How many years did the Jōgan era last according to the era periods including the Reiwa era? | 18 (acceptable range: anything between 17 and 19) | CORRECT; predicted_answer: The Jōgan era lasted from 859 to 877, which is 18 years. | not run |
| 105908 | How many Ford Mustang cars were sold in the United States during the 1974 model year? | 385993 (acceptable range: anything between 382133 and 389853) | INCORRECT; predicted_answer: During the 1974 model year, approximately 110,000 Ford Mustang cars were sold in the United States. | CORRECT; predicted_answer: Ford sold **385,993** Mustangs during the 1974 model year. |
| 19653842 | How many cells make up a jellyfish according to Jack A. Wilson's study of organism-like colonies? | Many | not run | not run |
| 34411 | How many days does the Sun spend in the Virgo constellation according to the 1977 IAU boundaries? | 45 (acceptable range: anything between 44 and 46) | CORRECT; predicted_answer: According to the 1977 IAU constellation boundaries, the Sun spends about 44 days in the Virgo constellation. | not run |
| 5643 | What is the area in square kilometers of Sark island in the Channel Islands? | 5.45 (acceptable range: anything between 5.3955 and 5.5045) | CORRECT; predicted_answer: The area of Sark island in the Channel Islands is approximately 5.45 square kilometers. | not run |
| 22948 | How many sons did Poseidon have with Halia according to the list of his offspring and their mothers? | 6 (acceptable range: anything between 5 and 7) | CORRECT; predicted_answer: Poseidon had six sons with Halia according to the list of his offspring and their mothers. | not run |
| 235916 | How many episodes of A Different World featured Jada Pinkett Smith as Lena James? | 46 (acceptable range: anything between 45 and 47) | INCORRECT; predicted_answer: Jada Pinkett Smith appeared as Lena James in 3 episodes of *A Different World*. | CORRECT; predicted_answer: Jada Pinkett Smith appeared in **46 episodes** of *A Different World* as Lena James. |
| 84952 | How many rounds were fought by Marvelous Marvin Hagler in his professional boxing match against Alan Minter on September 27, 1980? | 3 (acceptable range: anything between 2 and 4) | INCORRECT; predicted_answer: Marvelous Marvin Hagler fought Alan Minter for 15 rounds on September 27, 1980. | CORRECT; predicted_answer: The match lasted **3 rounds**. Hagler won by TKO after the referee stopped the fight due to severe cuts on Minter's face. |
| 260996 | In which year did Christian Slater perform the role of Tiny Tim Cratchit at the Trinity Theatre? | 1978 | not run | not run |
| 30292 | How many distinct quest phases does Randel Helms identify in his analysis of the quest structure in The Hobbit and The Lord of the Rings? | 6 (acceptable range: anything between 5 and 7) | CORRECT; predicted_answer: Randel Helms identifies **six distinct quest phases** in his analysis of the quest structure in *The Hobbit* and *The Lord of the Rings*. | not run |
| 235959 | How many episodes of the television series Good Sports featured Farrah Fawcett? | 15 (acceptable range: anything between 14 and 16) | INCORRECT; predicted_answer: Farrah Fawcett appeared in 2 episodes of the television series *Good Sports*. | CORRECT; predicted_answer: Farrah Fawcett appeared in all **15** episodes of *Good Sports*. |
| 91195 | How many singles titles did Helen Wills win at the Wimbledon Championships during the Amateur Era? | 8 (acceptable range: anything between 7 and 9) | CORRECT; predicted_answer: Helen Wills won 8 singles titles at the Wimbledon Championships during the Amateur Era. | not run |


## Rejected And Rerun Decisions

| Page ID | Stage | Exact reason | Page/question |
| ---: | --- | --- | --- |
| 22093 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | How many National Basketball Association championships have the Boston Celtics won? |
| 32611 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many US military deaths occurred in 1968 during the Vietnam War? |
| 17416221 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the total area in square kilometers of the Northern Cape province in South Africa? |
| 5489 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the total area in square kilometers of the Magallanes and Chilean Antarctica region in Chile? |
| 738 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the total area in square kilometers of Korçë county in Albania? |
| 11857 | `route_generation` | `wikipedia_infobox_answer_type_not_allowed:answer_type_not_allowed:Number; allowed=Number` | In what year was the film THX 1138 directed by George Lucas released? |
| 19261 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many days per year does Monaco have an average precipitation of at least 1.0 mm based on 1981–2010 climate data? |
| 31740 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | What was the number of first-time fall freshmen applicants at the University of Michigan, Ann Arbor in 2025? |
| 292259 | `route_generation` | `wikipedia_infobox_answer_type_not_allowed:answer_type_not_allowed:Number; allowed=Number` | In what year did Deutsche Welle begin broadcasting in the Pashto language? |
| 199445 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | How many matches did Wayne Rooney manage for Derby County between 14 November 2020 and 26 June 2022? |
| 8083 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many Grammy Awards has Dr. Dre won? |
| 21355232 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many national parks are there in California according to the List of national parks of the United States? |
| 5488 | `route_generation` | `wikipedia_infobox_extra_prompt_violation:no_social_science_research_prompt:census` | What was the population of the city of Abéché in Chad according to the 2009 census? |
| 39776 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the amplification factor of the Memcached protocol in UDP amplification attacks related to denial-of-service attacks? |
| 1640 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_2:answer_in_title` | What year did Alfred the Great die? |
| 151603 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many episodes of The Colgate Comedy Hour featured Dean Martin? |
| 45367389 | `route_generation` | `wikipedia_infobox_extra_prompt_violation:no_social_science_research_prompt:census` | According to the 2021 United Kingdom Census, how many people in Greater London were born in Romania? |
| 66958 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | What was the daily volume percentage of the renminbi in global foreign exchange market turnover in April 2025? |
| 41853326 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | How many games did Inter Miami CF play during the 2023 MLS season? |
| 217231 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many episodes are in season 7 of Curb Your Enthusiasm? |
| 60382764 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many years did the Jōgan era last according to the era periods including the Reiwa era? |
| 105908 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many Ford Mustang cars were sold in the United States during the 1974 model year? |
| 19653842 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | How many cells make up a jellyfish according to Jack A. Wilson's study of organism-like colonies? |
| 34411 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many days does the Sun spend in the Virgo constellation according to the 1977 IAU boundaries? |
| 5643 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the area in square kilometers of Sark island in the Channel Islands? |
| 22948 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many sons did Poseidon have with Halia according to the list of his offspring and their mothers? |
| 235916 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many episodes of A Different World featured Jada Pinkett Smith as Lena James? |
| 84952 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many rounds were fought by Marvelous Marvin Hagler in his professional boxing match against Alan Minter on September 27, 1980? |
| 260996 | `route_generation` | `wikipedia_infobox_answer_type_not_allowed:answer_type_not_allowed:Number; allowed=Number` | In which year did Christian Slater perform the role of Tiny Tim Cratchit at the Trinity Theatre? |
| 30292 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many distinct quest phases does Randel Helms identify in his analysis of the quest structure in The Hobbit and The Lord of the Rings? |
| 235959 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many episodes of the television series Good Sports featured Farrah Fawcett? |
| 91195 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many singles titles did Helen Wills win at the Wimbledon Championships during the Amateur Era? |


