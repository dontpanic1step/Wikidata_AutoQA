# Route 3 Streaming Wikipedia Page-ID Walkthrough - 2026-05-20

## Stats

- Run group ID: `wikipedia_stream_fast40_other_single_fact_no_social_science_2026_05_20`
- Run segment ID: `fresh40_other_single_fact_no_social_science_2026_05_20`
- Artifact manifest: `D:\Study\AI\My-research\Wikidata_Framework\outputs\run_manifests\wikipedia_stream_fast40_other_single_fact_no_social_science_2026_05_20.json`
- Mode: `page_id_stream`
- Page source: `table-search`
- Table-search queries: `insource:"wikitable"`
- Attempted page IDs: 42
- Unique attempted page IDs: 40
- Stream state reset at run start: yes
- Auto rerun pool once: yes
- Auto-rerun attempted page IDs: 2
- Accepted QAs: 8
- Rejected QAs/pages: 31
- Transient rerun attempts during run: 3
- Wall-clock runtime: 369.7675s
- DuckDuckGo top K: 5
- Generated search queries per QA: 3
- DuckDuckGo parallel queries: 3
- Minimum Route 3 table score: 0.0
- Route 3 reasoning_type constraint: `single_fact`
- Route 3 answer_type constraint: `Other`
- Route 3 extra prompt rules: `Ask factual questions, not questions about the findings or conclusions of social science research, such as results derived from census studies.`
- Stream page workers: 4
- Wikipedia concurrency limit: 4
- DuckDuckGo service concurrency limit: 4
- OpenRouter generation/rewrite concurrency limit: 10
- Second-stage concurrency limit: 10
- Page-id bounds: 1 to 80000000
- Stream state: `outputs\wikipedia_stream_fast40_other_single_fact_no_social_science_2026_05_20_state.json`
- Accepted output: `outputs\wikipedia_stream_fast40_other_single_fact_no_social_science_2026_05_20_accepted.jsonl`
- Rejected output: `outputs\wikipedia_stream_fast40_other_single_fact_no_social_science_2026_05_20_rejected.jsonl`
- Domain policy: `domain_and_subdomain_optional_for_page_id_streaming`
- Rerun pool after run: `151603`

### Survival By Layer

| Layer | Entered | Failed | Survived | Layer survival | Cumulative survival |
| --- | ---: | ---: | ---: | ---: | ---: |
| Page-id reservation | 42 | 0 | 42 | 100.0% | 100.0% |
| Unresolved or returned to rerun pool | 42 | 0 | 42 | 100.0% | 100.0% |
| Page extraction, table grading, and QA generation | 42 | 2 | 40 | 95.2% | 95.2% |
| Rewrite and surface validation | 40 | 3 | 37 | 92.5% | 88.1% |
| DuckDuckGo long-tail filtering | 37 | 5 | 32 | 86.5% | 76.2% |
| Second-stage model grading | 32 | 24 | 8 | 25.0% | 19.1% |
| Shared route-aware validation | 8 | 0 | 8 | 100.0% | 19.1% |
| Deduplication | 8 | 0 | 8 | 100.0% | 19.1% |
| Other rejection | 8 | 0 | 8 | 100.0% | 19.1% |

### Failure Reasons

| Stage | Exact reason | Count |
| --- | --- | ---: |
| `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | 24 |
| `search_longtail` | `search_longtail_verifier_error` | 3 |
| `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | 2 |
| `route_generation` | `wikipedia_infobox_extra_prompt_violation:no_social_science_research_prompt:census` | 2 |
| `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | 1 |
| `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | 1 |
| `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | 1 |

### Answer Type Stats

| Scope | Answer type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `Other` | 8 | 29 | 37 | 21.6% |
| Current Run Records | `unknown` | 0 | 2 | 2 | 0.0% |

### Reasoning Type Stats

| Scope | Reasoning type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `single_fact` | 8 | 29 | 37 | 21.6% |
| Current Run Records | `wikipedia_table_fact` | 0 | 2 | 2 | 0.0% |

### Rerun Pool After Run

| Page ID | Exact reason |
| ---: | --- |
| 151603 | `search_longtail_verifier_error` |

### In-Run Rerun Outcomes

These rows show transient rerun-pool attempts and whether the same page ID later reached a final decision in this invocation.

| Page ID | Rerun attempts | Final outcome | Final reason/question | First transient reason |
| ---: | ---: | --- | --- | --- |
| 151603 | 2 | `still_in_rerun_pool` |  | `search_longtail_verifier_error` |
| 91195 | 1 | `rejected` | second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1 | `search_longtail_verifier_error` |

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
| `candidate_processing_seconds` | 39 | 727.3982 | 18.6512 | 36.8374 |
| `duckduckgo_search_seconds` | 34 | 209.3724 | 6.1580 | 14.4818 |
| `first_paragraph_extract_seconds` | 39 | 37.3226 | 0.9570 | 3.4880 |
| `llm_question_generation_seconds` | 39 | 184.2190 | 4.7236 | 7.4763 |
| `number_reference_margin_seconds` | 34 | 0.0000 | 0.0000 | 0.0000 |
| `page_fetch_seconds` | 39 | 3.0438 | 0.0780 | 0.3829 |
| `rewrite_seconds` | 37 | 125.1057 | 3.3812 | 6.3544 |
| `second_stage_grading_seconds` | 32 | 392.8646 | 12.2770 | 26.3059 |
| `table_parse_seconds` | 39 | 106.5857 | 2.7330 | 11.0152 |
| `total_generation_seconds` | 39 | 341.8177 | 8.7646 | 19.5738 |
| `total_processing_seconds` | 39 | 727.3982 | 18.6512 | 36.8374 |

## Accepted Candidates

| Page ID | Question | Answer | Source |
| ---: | --- | --- | --- |
| 738 | What was the Human Development Index (HDI) value for Vlorë county in Albania in 2022? | 0.814 | https://en.wikipedia.org/wiki/Albania |
| 13277 | What was the population of the Duchy of Milan in the early 1600s within the Holy Roman Empire? | 1,350,000 | https://en.wikipedia.org/wiki/Holy_Roman_Empire |
| 19261 | What is the highest temperature in degrees Celsius recorded in Monaco during August according to the 1981–2010 climate data? | 34.5 | https://en.wikipedia.org/wiki/Monaco |
| 292259 | What type of broadcast service did Deutsche Welle offer in the Russian language? | TV | https://en.wikipedia.org/wiki/Deutsche_Welle |
| 40010153 | What is the average monthly sunshine hours in Goa during May? | 297.6 | https://en.wikipedia.org/wiki/Goa |
| 217231 | What bonus features are included in the DVD release of Season 5 of Curb Your Enthusiasm? | "The History of Curb ... so far" and "The History of Curb ... even further" featurettes | https://en.wikipedia.org/wiki/Curb_Your_Enthusiasm |
| 12186 | What was the population of the city of Bafatá in Guinea-Bissau according to the 2015 estimate? | 37,985 | https://en.wikipedia.org/wiki/Guinea-Bissau |
| 33094374 | What percentage of advertising expenditure was allocated to Magazine media in the United States in 2007? | 20.4% | https://en.wikipedia.org/wiki/Telecommunications |

## Second-Stage Filtering Responses

These are the small-model QA responses used by the second-stage filter: `openai/gpt-4.1-mini` and `google/gemini-3-flash-preview`.

| Page ID | Question | Reference answer | openai/gpt-4.1-mini | google/gemini-3-flash-preview |
| ---: | --- | --- | --- | --- |
| 738 | What was the Human Development Index (HDI) value for Vlorë county in Albania in 2022? | 0.814 | INCORRECT; predicted_answer: The Human Development Index (HDI) value for Vlorë county in Albania in 2022 was 0.839. | INCORRECT; predicted_answer: The Human Development Index (HDI) value for Vlorë County in 2022 was **0.781**. |
| 13277 | What was the population of the Duchy of Milan in the early 1600s within the Holy Roman Empire? | 1,350,000 | INCORRECT; predicted_answer: The population of the Duchy of Milan in the early 1600s was approximately 1.2 to 1.5 million people. | INCORRECT; predicted_answer: In the early 1600s, the population of the Duchy of Milan was approximately **1.1 to 1.2 million** people. |
| 19261 | What is the highest temperature in degrees Celsius recorded in Monaco during August according to the 1981–2010 climate data? | 34.5 | INCORRECT; predicted_answer: The highest temperature recorded in Monaco during August according to the 1981–2010 climate data is 33.3°C. | INCORRECT; predicted_answer: The highest temperature recorded in Monaco during August according to the 1981–2010 climate data is **33.6°C**. |
| 292259 | What type of broadcast service did Deutsche Welle offer in the Russian language? | TV | INCORRECT; predicted_answer: Deutsche Welle offered international radio and television broadcast services in the Russian language. | INCORRECT; predicted_answer: Deutsche Welle offered a **shortwave radio** service in Russian for several decades, but it has since transitioned into a **digital multimedia service** providing news via its website, social media, and satellite television. |
| 40010153 | What is the average monthly sunshine hours in Goa during May? | 297.6 | INCORRECT; predicted_answer: The average monthly sunshine hours in Goa during May are approximately 280 to 300 hours. | INCORRECT; predicted_answer: The average monthly sunshine hours in Goa during May is approximately **290 to 300 hours**, averaging about 9.5 hours per day. |
| 217231 | What bonus features are included in the DVD release of Season 5 of Curb Your Enthusiasm? | "The History of Curb ... so far" and "The History of Curb ... even further" featurettes | INCORRECT; predicted_answer: The DVD release of Season 5 of *Curb Your Enthusiasm* includes the following bonus features:  - Deleted Scenes   - Audio Commentaries   - Behind-the-Scenes Featurettes   - Outtakes/Bloopers    These extras provide additional insights and humorous moments beyond the episodes themselves. | INCORRECT; predicted_answer: The DVD release of *Curb Your Enthusiasm* Season 5 includes the following bonus features:  *   **"HBO First Look: The Making of Curb Your Enthusiasm"**: A 25-minute behind-the-scenes documentary focusing on the production of the fifth season. *   **A Conversation with Larry David**: A featurette where Larry David discusses the season's themes and storylines. *   **Casper, Wyoming Premiere**: Footage from the season premiere event held in Casper, Wyoming. |
| 12186 | What was the population of the city of Bafatá in Guinea-Bissau according to the 2015 estimate? | 37,985 | INCORRECT; predicted_answer: The population of the city of Bafatá in Guinea-Bissau was estimated to be 34,760 in 2015. | INCORRECT; predicted_answer: According to the 2015 estimate, the population of Bafatá was approximately **23,038**. |
| 33094374 | What percentage of advertising expenditure was allocated to Magazine media in the United States in 2007? | 20.4% | INCORRECT; predicted_answer: In 2007, 14.3% of advertising expenditure in the United States was allocated to Magazine media. | INCORRECT; predicted_answer: In 2007, magazine advertising expenditure accounted for approximately **18.8%** of the total advertising market in the United States. |
| 17416221 | What city is the provincial capital of the Eastern Cape province in South Africa? | Bhisho | not run | not run |
| 22093 | How many NBA Finals appearances have the Minneapolis/Los Angeles Lakers made in the National Basketball Association? | 32 | not run | not run |
| 5489 | What is the official capital city of the Valparaíso region in Chile? | Valparaíso | not run | not run |
| 32611 | What was the total amount of US expenditures in South Vietnam from 1953 to 1974 measured in 2015 dollars during the Vietnam War? | $1 trillion | INCORRECT; predicted_answer: The total amount of US expenditures in South Vietnam from 1953 to 1974 during the Vietnam War was approximately $168 billion measured in 2015 dollars. | CORRECT; predicted_answer: The total U.S. expenditure in South Vietnam from 1953 to 1974 was approximately **$1 trillion** when measured in 2015 dollars. |
| 14849 | What is the percentage of the Asian alone (Non-Hispanic) population in Illinois according to the 2020 census? | 5.83% | not run | not run |
| 9316 | How many native speakers in thousands does the Cornish language have in England? | 0.6 | INCORRECT; predicted_answer: The Cornish language has about 500 native speakers in England. | CORRECT; predicted_answer: The Cornish language has **zero** (or near-zero) native speakers in the sense of an unbroken traditional lineage, as the last fluent speakers of the original language died in the late 18th century.  While there are approximately **0.5 to 0.6 thousand** (500–600) people who identify as fluent speakers or "new" native speakers (raised with the revived language at home), this figure is less than 1 in thousands. |
| 11857 | What is the title of the feature film directed by George Lucas in the year 1973? | American Graffiti | CORRECT; predicted_answer: The title of the feature film directed by George Lucas in 1973 is **"American Graffiti."** | not run |
| 21355232 | How many national parks are there in California according to the List of national parks of the United States? | 9 | CORRECT; predicted_answer: California has 9 national parks according to the List of national parks of the United States. | not run |
| 8083 | Which character was voiced by Dr. Dre in the 2005 video game 50 Cent: Bulletproof? | Grizz | INCORRECT; predicted_answer: Dr. Dre voiced the character K Dog in the 2005 video game 50 Cent: Bulletproof. | CORRECT; predicted_answer: Dr. Dre voiced the character **Grizz**, a veteran war hero and arms dealer. |
| 199445 | What win percentage did Wayne Rooney achieve as manager of Derby County? | 28.2 | INCORRECT; predicted_answer: Wayne Rooney achieved a win percentage of approximately 38.5% as manager of Derby County. | CORRECT; predicted_answer: Wayne Rooney achieved a win percentage of **28.2%** during his tenure as manager of Derby County (24 wins from 85 matches). |
| 31740 | What was the SAT score range for first-time fall freshmen admitted to the University of Michigan in the year 2023? | 1350–1530 | INCORRECT; predicted_answer: The SAT score range for first-time fall freshmen admitted to the University of Michigan in 2023 was 1340 to 1530. | CORRECT; predicted_answer: For first-time freshmen admitted to the University of Michigan for Fall 2023, the middle 50% SAT score range was **1350–1530**. |
| 5488 | In which region of Chad is the city of Moundou located? | Logone Occidental | CORRECT; predicted_answer: The city of Moundou is located in the Logone Occidental region of Chad. | not run |
| 39776 | What is the amplification factor of the CHARGEN protocol in UDP amplification attacks related to denial-of-service attacks? | 358.8 | INCORRECT; predicted_answer: The amplification factor of the CHARGEN protocol in UDP amplification attacks is typically around **358 to 400 times**. This means an attacker can send a small request to a CHARGEN server and cause it to reply with a response roughly 358 to 400 times larger, greatly amplifying the attack traffic. | CORRECT; predicted_answer: The amplification factor of the CHARGEN protocol is approximately **358.8**, making it one of the highest ratios among common UDP amplification vectors. |
| 1640 | What event led to Guthrum's conversion to Christianity during the reign of Alfred the Great? | Alfred defeats Guthrum decisively in the Battle of Edington | CORRECT; predicted_answer: Guthrum's conversion to Christianity was a result of his defeat by Alfred the Great at the Battle of Edington in 878. After his defeat, Guthrum agreed to a peace treaty and was baptized as part of the terms, marking his conversion. | not run |
| 45367389 | What is the percentage of the population born in India according to the 2021 United Kingdom Census for Greater London? | 3.7 | not run | not run |
| 60382764 | What is the name of the Japanese calendar era corresponding to the Gregorian calendar years 2019 through 2026? | Reiwa | not run | not run |
| 41853326 | Who was the kit manufacturer for Inter Miami CF starting in the 2026 season? | Lowe's | not run | not run |
| 34411 | What is the Unicode text symbol representing the zodiac sign Leo? | ♌︎ | CORRECT; predicted_answer: The Unicode text symbol for the zodiac sign Leo is ♌ (U+264C). | not run |
| 66958 | What is the literal translation of the formal name of the currency Renminbi used in the People's Republic of China? | people's currency | CORRECT; predicted_answer: The literal translation of "Renminbi" (人民币) is "People's Currency." | not run |
| 105908 | What were the US sales figures for the Ford Mustang in the 1974 model year? | 385,993 | INCORRECT; predicted_answer: The US sales figures for the Ford Mustang in the 1974 model year were approximately 110,000 units. | CORRECT; predicted_answer: Ford sold **385,993** Mustangs in the United States for the 1974 model year. |
| 5643 | What alternative name is used for the island Brecqhou in the Bailiwick of Guernsey within the Channel Islands? | Brechou | CORRECT; predicted_answer: The alternative name for the island Brecqhou is "Brechou." | not run |
| 19653842 | According to Queller and Strassmann's view of organisms at different levels of biological organisation, what organisms compose a lichen? | Organisms of different species | CORRECT; predicted_answer: According to Queller and Strassmann's view, a lichen is composed of multiple distinct organisms—specifically, a symbiotic association between a fungus and one or more photosynthetic partners (algae and/or cyanobacteria). These different organisms form a cooperative consortium rather than a single organism at one level of biological organization. | not run |
| 22948 | Who is the mother of Pegasus and Chrysaor, the offspring of Poseidon? | Medusa | CORRECT; predicted_answer: The mother of Pegasus and Chrysaor, offspring of Poseidon, is Medusa. | not run |
| 84952 | What was Marvelous Marvin Hagler's role in the 1993 video game Boxing Legends of the Ring? | Playable character | CORRECT; predicted_answer: In the 1993 video game *Boxing Legends of the Ring*, Marvelous Marvin Hagler appears as one of the playable legendary boxers. | not run |
| 55440889 | Which 4G LTE-FDD cellular network bands does the Pixel 2 support? | 1*, 2*, 3*, 4*, 5, 7*, 8, 12, 13, 17, 20, 25, 26, 28, 29, 30, 32, 66* | INCORRECT; predicted_answer: The Google Pixel 2 supports the following 4G LTE-FDD bands:  - Band 1 (2100 MHz)   - Band 2 (1900 MHz)   - Band 3 (1800 MHz)   - Band 4 (1700/2100 MHz)   - Band 5 (850 MHz)   - Band 7 (2600 MHz)   - Band 8 (900 MHz)   - Band 12 (700 MHz)   - Band 13 (700 MHz)   - Band 17 (700 MHz)   - Band 18 (800 MHz)   - Band 19 ( | CORRECT; predicted_answer: The Pixel 2 supports the following 4G LTE-FDD bands:  **1, 2, 3, 4, 5, 7, 8, 12, 13, 17, 20, 25, 26, 28, 29, 30, 32, and 66.** |
| 235916 | What type of film is the 1992 movie Moe's World featuring Jada Pinkett Smith as Natalie? | Television film | INCORRECT; predicted_answer: The 1992 movie *Moe's World* featuring Jada Pinkett Smith as Natalie is a drama film. | CORRECT; predicted_answer: *Moe's World* is a **television movie** (specifically a comedy pilot). |
| 30292 | What event in The Hobbit is signified by the arrival of the Great Eagles? | Arrival of Great Eagles | CORRECT; predicted_answer: The arrival of the Great Eagles in *The Hobbit* signifies the turning point during the Battle of the Five Armies, when they come to aid the forces of good and help defeat the attacking goblins and wargs. | not run |
| 2924002 | What award did Project X Magazine give in 1995 for electronic dance music? | Electronic Dance Music Awards | INCORRECT; predicted_answer: In 1995, Project X Magazine gave the award for "Best Electronic Dance Music Album" to The Prodigy for their album *Music for the Jilted Generation*. | CORRECT; predicted_answer: In 1995, *Project X Magazine* presented the **Electronic Dance Music Awards** (often referred to as the Project X EDM Awards). |
| 260996 | Which role did Christian Slater perform in the 1983 stage production of Merlin? | Young Merlin / Arthur | INCORRECT; predicted_answer: In the 1983 stage production of *Merlin*, Christian Slater performed the role of Mordred. | CORRECT; predicted_answer: Christian Slater played the role of **Young Merlin** (and Arthur). |
| 235959 | What is the title of the play by William Mastrosimone in which Farrah Fawcett portrayed Marjorie? | Extremities | CORRECT; predicted_answer: The title of the play by William Mastrosimone in which Farrah Fawcett portrayed Marjorie is **"Extremities."** | not run |
| 91195 | What was the prize money for the Ladies' singles winner at the 1984 Wimbledon Championships? | £90,000 | INCORRECT; predicted_answer: The prize money for the Ladies' singles winner at the 1984 Wimbledon Championships was £130,000. | CORRECT; predicted_answer: The prize money for the Ladies' singles winner at the 1984 Wimbledon Championships was **£90,000**. |


Rerun-pool entries have no second-stage filtering response unless they reached the panel before the transient failure.

## Rejected And Rerun Decisions

| Page ID | Stage | Exact reason | Page/question |
| ---: | --- | --- | --- |
| 17416221 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What city is the provincial capital of the Eastern Cape province in South Africa? |
| 22093 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | How many NBA Finals appearances have the Minneapolis/Los Angeles Lakers made in the National Basketball Association? |
| 5489 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | What is the official capital city of the Valparaíso region in Chile? |
| 32611 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What was the total amount of US expenditures in South Vietnam from 1953 to 1974 measured in 2015 dollars during the Vietnam War? |
| 14849 | `route_generation` | `wikipedia_infobox_extra_prompt_violation:no_social_science_research_prompt:census` | What is the percentage of the Asian alone (Non-Hispanic) population in Illinois according to the 2020 census? |
| 9316 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many native speakers in thousands does the Cornish language have in England? |
| 11857 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the title of the feature film directed by George Lucas in the year 1973? |
| 21355232 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many national parks are there in California according to the List of national parks of the United States? |
| 8083 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which character was voiced by Dr. Dre in the 2005 video game 50 Cent: Bulletproof? |
| 199445 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What win percentage did Wayne Rooney achieve as manager of Derby County? |
| 31740 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What was the SAT score range for first-time fall freshmen admitted to the University of Michigan in the year 2023? |
| 5488 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which region of Chad is the city of Moundou located? |
| 39776 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the amplification factor of the CHARGEN protocol in UDP amplification attacks related to denial-of-service attacks? |
| 1640 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What event led to Guthrum's conversion to Christianity during the reign of Alfred the Great? |
| 45367389 | `route_generation` | `wikipedia_infobox_extra_prompt_violation:no_social_science_research_prompt:census` | What is the percentage of the population born in India according to the 2021 United Kingdom Census for Greater London? |
| 60382764 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | What is the name of the Japanese calendar era corresponding to the Gregorian calendar years 2019 through 2026? |
| 41853326 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | Who was the kit manufacturer for Inter Miami CF starting in the 2026 season? |
| 34411 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the Unicode text symbol representing the zodiac sign Leo? |
| 66958 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the literal translation of the formal name of the currency Renminbi used in the People's Republic of China? |
| 105908 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What were the US sales figures for the Ford Mustang in the 1974 model year? |
| 5643 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What alternative name is used for the island Brecqhou in the Bailiwick of Guernsey within the Channel Islands? |
| 19653842 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | According to Queller and Strassmann's view of organisms at different levels of biological organisation, what organisms compose a lichen? |
| 22948 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who is the mother of Pegasus and Chrysaor, the offspring of Poseidon? |
| 84952 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What was Marvelous Marvin Hagler's role in the 1993 video game Boxing Legends of the Ring? |
| 55440889 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which 4G LTE-FDD cellular network bands does the Pixel 2 support? |
| 235916 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What type of film is the 1992 movie Moe's World featuring Jada Pinkett Smith as Natalie? |
| 30292 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What event in The Hobbit is signified by the arrival of the Great Eagles? |
| 2924002 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What award did Project X Magazine give in 1995 for electronic dance music? |
| 260996 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which role did Christian Slater perform in the 1983 stage production of Merlin? |
| 235959 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the title of the play by William Mastrosimone in which Farrah Fawcett portrayed Marjorie? |
| 91195 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What was the prize money for the Ladies' singles winner at the 1984 Wimbledon Championships? |

### Rerun Records

| Page ID | Stage | Exact reason | Page/question |
| ---: | --- | --- | --- |
| 151603 | `search_longtail` | `search_longtail_verifier_error` | https://en.wikipedia.org/w/index.php?pageid=151603 |
| 91195 | `search_longtail` | `search_longtail_verifier_error` | https://en.wikipedia.org/w/index.php?pageid=91195 |
| 151603 | `search_longtail` | `search_longtail_verifier_error` | https://en.wikipedia.org/w/index.php?pageid=151603 |

