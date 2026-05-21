# Route 3 Streaming Wikipedia Page-ID Walkthrough - 2026-05-20

## Stats

- Run group ID: `wikipedia_stream_fast40_date_single_fact_no_social_science_2026_05_20`
- Run segment ID: `fresh40_date_single_fact_no_social_science_2026_05_20`
- Artifact manifest: `D:\Study\AI\My-research\Wikidata_Framework\outputs\run_manifests\wikipedia_stream_fast40_date_single_fact_no_social_science_2026_05_20.json`
- Mode: `page_id_stream`
- Page source: `table-search`
- Table-search queries: `insource:"wikitable"`
- Attempted page IDs: 43
- Unique attempted page IDs: 40
- Stream state reset at run start: yes
- Auto rerun pool once: yes
- Auto-rerun attempted page IDs: 3
- Accepted QAs: 6
- Rejected QAs/pages: 31
- Transient rerun attempts during run: 6
- Wall-clock runtime: 400.5300s
- DuckDuckGo top K: 5
- Generated search queries per QA: 3
- DuckDuckGo parallel queries: 3
- Minimum Route 3 table score: 0.0
- Route 3 reasoning_type constraint: `single_fact`
- Route 3 answer_type constraint: `Date`
- Route 3 extra prompt rules: `Ask factual questions, not questions about the findings or conclusions of social science research, such as results derived from census studies.`
- Stream page workers: 4
- Wikipedia concurrency limit: 4
- DuckDuckGo service concurrency limit: 4
- OpenRouter generation/rewrite concurrency limit: 10
- Second-stage concurrency limit: 10
- Page-id bounds: 1 to 80000000
- Stream state: `outputs\wikipedia_stream_fast40_date_single_fact_no_social_science_2026_05_20_state.json`
- Accepted output: `outputs\wikipedia_stream_fast40_date_single_fact_no_social_science_2026_05_20_accepted.jsonl`
- Rejected output: `outputs\wikipedia_stream_fast40_date_single_fact_no_social_science_2026_05_20_rejected.jsonl`
- Domain policy: `domain_and_subdomain_optional_for_page_id_streaming`
- Rerun pool after run: `105908, 66958, 235959`

### Survival By Layer

| Layer | Entered | Failed | Survived | Layer survival | Cumulative survival |
| --- | ---: | ---: | ---: | ---: | ---: |
| Page-id reservation | 43 | 0 | 43 | 100.0% | 100.0% |
| Unresolved or returned to rerun pool | 43 | 0 | 43 | 100.0% | 100.0% |
| Page extraction, table grading, and QA generation | 43 | 3 | 40 | 93.0% | 93.0% |
| Rewrite and surface validation | 40 | 0 | 40 | 100.0% | 93.0% |
| DuckDuckGo long-tail filtering | 40 | 9 | 31 | 77.5% | 72.1% |
| Second-stage model grading | 31 | 24 | 7 | 22.6% | 16.3% |
| Shared route-aware validation | 7 | 1 | 6 | 85.7% | 14.0% |
| Deduplication | 6 | 0 | 6 | 100.0% | 14.0% |
| Other rejection | 6 | 0 | 6 | 100.0% | 14.0% |

### Failure Reasons

| Stage | Exact reason | Count |
| --- | --- | ---: |
| `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | 24 |
| `search_longtail` | `search_longtail_verifier_error` | 6 |
| `route_generation` | `wikipedia_infobox_extra_prompt_violation:no_social_science_research_prompt:census` | 2 |
| `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | 2 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No date or year information is present in the table to form a valid Date answer_type question.` | 1 |
| `search_longtail` | `search_longtail_verifier_rejected:keyword_query_2:answer_in_title` | 1 |
| `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | 1 |

### Answer Type Stats

| Scope | Answer type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `Date` | 6 | 28 | 34 | 17.6% |
| Current Run Records | `unknown` | 0 | 3 | 3 | 0.0% |

### Reasoning Type Stats

| Scope | Reasoning type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `single_fact` | 6 | 28 | 34 | 17.6% |
| Current Run Records | `wikipedia_table_fact` | 0 | 3 | 3 | 0.0% |

### Rerun Pool After Run

| Page ID | Exact reason |
| ---: | --- |
| 105908 | `search_longtail_verifier_error` |
| 66958 | `search_longtail_verifier_error` |
| 235959 | `search_longtail_verifier_error` |

### In-Run Rerun Outcomes

These rows show transient rerun-pool attempts and whether the same page ID later reached a final decision in this invocation.

| Page ID | Rerun attempts | Final outcome | Final reason/question | First transient reason |
| ---: | ---: | --- | --- | --- |
| 105908 | 2 | `still_in_rerun_pool` |  | `search_longtail_verifier_error` |
| 235959 | 2 | `still_in_rerun_pool` |  | `search_longtail_verifier_error` |
| 66958 | 2 | `still_in_rerun_pool` |  | `search_longtail_verifier_error` |

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
| `candidate_processing_seconds` | 37 | 736.7328 | 19.9117 | 35.9757 |
| `duckduckgo_search_seconds` | 34 | 214.2690 | 6.3020 | 15.1042 |
| `first_paragraph_extract_seconds` | 37 | 31.2643 | 0.8450 | 2.6830 |
| `llm_question_generation_seconds` | 37 | 212.9153 | 5.7545 | 14.9919 |
| `number_reference_margin_seconds` | 34 | 0.0000 | 0.0000 | 0.0000 |
| `page_fetch_seconds` | 37 | 2.6017 | 0.0703 | 0.4502 |
| `rewrite_seconds` | 34 | 143.0057 | 4.2060 | 11.3553 |
| `second_stage_grading_seconds` | 31 | 379.4222 | 12.2394 | 25.7323 |
| `table_parse_seconds` | 37 | 102.4703 | 2.7695 | 9.5182 |
| `total_generation_seconds` | 37 | 359.8367 | 9.7253 | 25.9200 |
| `total_processing_seconds` | 37 | 736.7328 | 19.9117 | 35.9757 |

## Accepted Candidates

| Page ID | Question | Answer | Source |
| ---: | --- | --- | --- |
| 32611 | What year saw the highest number of military deaths in South Vietnam during the Vietnam War? | 1972 | https://en.wikipedia.org/wiki/Vietnam_War |
| 199445 | On what day, month, and year did Wayne Rooney begin managing Derby County? | 2020-11-14 | https://en.wikipedia.org/wiki/Wayne_Rooney |
| 12186 | What year does the population estimate for the major cities of Guinea-Bissau refer to? | 2015 | https://en.wikipedia.org/wiki/Guinea-Bissau |
| 34411 | What are the approximate start and end dates of the Sun's passage through the constellation Ophiuchus according to the 1977 IAU boundaries? | 30 November – 17 December | https://en.wikipedia.org/wiki/Zodiac |
| 217231 | What day, month, and year was the first episode of Curb Your Enthusiasm first released? | 1999-10-17 | https://en.wikipedia.org/wiki/Curb_Your_Enthusiasm |
| 235916 | What year did Jada Pinkett Smith make her first appearance in the film 'Moe's World'? | 1992 | https://en.wikipedia.org/wiki/Jada_Pinkett_Smith |

## Second-Stage Filtering Responses

These are the small-model QA responses used by the second-stage filter: `openai/gpt-4.1-mini` and `google/gemini-3-flash-preview`.

| Page ID | Question | Reference answer | openai/gpt-4.1-mini | google/gemini-3-flash-preview |
| ---: | --- | --- | --- | --- |
| 32611 | What year saw the highest number of military deaths in South Vietnam during the Vietnam War? | 1972 | INCORRECT; predicted_answer: The year 1968 saw the highest number of military deaths in South Vietnam during the Vietnam War. | INCORRECT; predicted_answer: The year with the highest number of military deaths in South Vietnam was **1968**, primarily due to the Tet Offensive. |
| 199445 | On what day, month, and year did Wayne Rooney begin managing Derby County? | 2020-11-14 | INCORRECT; predicted_answer: Wayne Rooney began managing Derby County on January 15, 2021. | INCORRECT; predicted_answer: Wayne Rooney began managing Derby County on **November 14, 2020**, initially in a caretaker role before being appointed permanently on January 15, 2021. |
| 12186 | What year does the population estimate for the major cities of Guinea-Bissau refer to? | 2015 | INCORRECT; predicted_answer: The population estimate for the major cities of Guinea-Bissau refers to the year 2023. | INCORRECT; predicted_answer: The population estimates for major cities in Guinea-Bissau typically refer to the **2009** General Population and Housing Census, which remains the most recent official source for city-specific data. |
| 34411 | What are the approximate start and end dates of the Sun's passage through the constellation Ophiuchus according to the 1977 IAU boundaries? | 30 November – 17 December | INCORRECT; predicted_answer: According to the 1977 IAU constellation boundaries, the Sun passes through Ophiuchus approximately from November 29 to December 18. | INCORRECT; predicted_answer: The Sun passes through the constellation Ophiuchus approximately from **November 30 to December 18**. |
| 217231 | What day, month, and year was the first episode of Curb Your Enthusiasm first released? | 1999-10-17 | INCORRECT; predicted_answer: The first episode of *Curb Your Enthusiasm* was released on October 15, 2000. | INCORRECT; predicted_answer: The first episode of *Curb Your Enthusiasm* was released on **October 15, 2000**. |
| 235916 | What year did Jada Pinkett Smith make her first appearance in the film 'Moe's World'? | 1992 | INCORRECT; predicted_answer: Jada Pinkett Smith made her first appearance in the film "Moe's World" in 1997. | INCORRECT; predicted_answer: Jada Pinkett Smith appeared in the television film *Moe's World* in **1990**. |
| 9316 | England |  | not run | not run |
| 22093 | What year did the original Baltimore Bullets win their only National Basketball Association championship? | 1948 | not run | not run |
| 17416221 | What year does the population data for the provinces of South Africa in the administrative divisions table come from? | 2022 | not run | not run |
| 5489 | In what year were the Arica and Parinacota and Los Ríos regions established in Chile? | 2007 | CORRECT; predicted_answer: The Arica and Parinacota region was established in 2007, and the Los Ríos region was established in 2007 as well. | not run |
| 14849 | What year did the U.S. Census record the population of Illinois as 12,419,293? | 2000 | not run | not run |
| 738 | What year was the system of urban and rural municipalities unified and simplified into municipalities in Albania? | 2015 | CORRECT; predicted_answer: The system of urban and rural municipalities in Albania was unified and simplified into municipalities in the year 2015. | not run |
| 13277 | In what year did the Thirty Years' War end, defining the territorial divisions of the Holy Roman Empire? | 1648 | CORRECT; predicted_answer: The Thirty Years' War ended in 1648. | not run |
| 19261 | What year range is covered by the climate data averages and extremes for Monaco in the table titled 'Climate data for Monaco (1981–2010 averages, extremes 1966–present)'? | 1981–2010 averages, extremes 1966–present | CORRECT; predicted_answer: The climate data averages cover the years 1981 to 2010, and the extremes cover the years from 1966 to the present. | not run |
| 11857 | What year was the film American Graffiti, directed by George Lucas, released? | 1973 | CORRECT; predicted_answer: The film American Graffiti, directed by George Lucas, was released in 1973. | not run |
| 8083 | What year did Dr. Dre receive the Grammy Lifetime Achievement Award as a member of N.W.A.? | 2024 | not run | not run |
| 21355232 | On what day, month, and year was Grand Teton National Park designated as a national park? | 1929-02-26 | CORRECT; predicted_answer: Grand Teton National Park was designated as a national park on February 26, 1929. | not run |
| 292259 | In what year did Deutsche Welle start broadcasting in Pashto? | 1970 | INCORRECT; predicted_answer: Deutsche Welle started broadcasting in Pashto in the year 2010. | CORRECT; predicted_answer: Deutsche Welle started broadcasting in Pashto in **1970**. |
| 31740 | During which academic year did the University of Michigan-Ann Arbor have a total enrollment of 50,278 students? | 2021-2022 | INCORRECT; predicted_answer: The University of Michigan-Ann Arbor had a total enrollment of 50,278 students during the 2022-2023 academic year. | CORRECT; predicted_answer: The University of Michigan-Ann Arbor had a total enrollment of 50,278 students during the **2021–2022** academic year. |
| 5488 | What year was the population census conducted that recorded N'Djamena's population as 951,418? | 2009 | not run | not run |
| 40010153 | What year did Goa have a total tourist arrival of 2,302,146? | 2005 | INCORRECT; predicted_answer: Goa had a total tourist arrival of 2,302,146 in the year 2017. | CORRECT; predicted_answer: Goa had a total tourist arrival of 2,302,146 in **2005**. |
| 39776 | In what year was the amplification vulnerability in the BitTorrent protocol's libuTP fixed to prevent denial-of-service attacks? | 2015 | INCORRECT; predicted_answer: The amplification vulnerability in the BitTorrent protocol's libuTP was fixed in 2017. | CORRECT; predicted_answer: The amplification vulnerability in the libuTP library was fixed in **2015**. |
| 1640 | In what year did Alfred the Great conquer London and proclaim himself king of the Anglo-Saxons? | c. 886 | CORRECT; predicted_answer: Alfred the Great conquered London and proclaimed himself king of the Anglo-Saxons in the year 886. | not run |
| 151603 | On what day, month, and year did Dean Martin appear in episode 7 of The Frank Sinatra Show? | 1957-11-29 | INCORRECT; predicted_answer: Dean Martin appeared in episode 7 of The Frank Sinatra Show on October 22, 1950. | CORRECT; predicted_answer: Dean Martin appeared in episode 7 of *The Frank Sinatra Show* on **November 29, 1957**. |
| 60382764 | In what year did the Reiwa era start according to the Gregorian calendar? | 2019 | CORRECT; predicted_answer: The Reiwa era started in the year 2019 according to the Gregorian calendar. | not run |
| 41853326 | What year did Luis Suarez become the top goalscorer for Inter Miami CF with 25 goals? | 2024 | INCORRECT; predicted_answer: Luis Suárez became the top goalscorer for Inter Miami CF with 25 goals in the year 2023. | CORRECT; predicted_answer: Luis Suárez achieved this milestone in **2024**. |
| 45367389 | In what year did Greater London form its twin city partnership with Berlin, Germany? | 2000 | INCORRECT; predicted_answer: Greater London formed its twin city partnership with Berlin, Germany, in 1967. | CORRECT; predicted_answer: Greater London formed its twin city partnership with Berlin in **2000**. |
| 5643 | In what year was the Bailiwick of Jersey established as a Crown Dependency within the Channel Islands? | 1204 | INCORRECT; predicted_answer: The Bailiwick of Jersey has been a Crown Dependency since 1204, when it remained loyal to the English Crown after the Duchy of Normandy was lost to France. | CORRECT; predicted_answer: The Bailiwick of Jersey was established as a Crown Dependency in **1204**, following the loss of continental Normandy by King John to France. |
| 19653842 | What year did Queller and Strassmann publish their perspective on organisms as cooperating entities at different levels of biological organization? | 2012 | INCORRECT; predicted_answer: Queller and Strassmann published their perspective on organisms as cooperating entities at different levels of biological organization in 2016. | INCORRECT; predicted_answer: Queller and Strassmann published their perspective, "Beyond society: the evolution of organismality," in **2009**. |
| 55440889 | What year was the 3G CDMA EVDO Rev A cellular network standard introduced? | 2006 | CORRECT; predicted_answer: The 3G CDMA EVDO Rev A cellular network standard was introduced in 2006. | not run |
| 84952 | On what day, month, and year did Marvelous Marvin Hagler defeat Alan Minter to win the WBA, WBC, and The Ring middleweight titles? | 1980-09-27 | CORRECT; predicted_answer: Marvelous Marvin Hagler defeated Alan Minter to win the WBA, WBC, and The Ring middleweight titles on September 27, 1980. | not run |
| 22948 | In what century is the earliest source that records Poseidon's offspring Triton by Amphitrite dated? | 8th cent. BC | CORRECT; predicted_answer: The earliest source that records Poseidon's offspring Triton by Amphitrite is dated to the 8th century BCE. | not run |
| 30292 | In what year was the novel The Hobbit first published? | 1937 | CORRECT; predicted_answer: The novel The Hobbit was first published in 1937. | not run |
| 2924002 | What year was the first and only Electronic Dance Music Awards held by Project X Magazine? | 1995 | INCORRECT; predicted_answer: The first and only Electronic Dance Music Awards held by Project X Magazine took place in 2017. | CORRECT; predicted_answer: The first and only Electronic Dance Music Awards held by *Project X Magazine* took place in **1995**. |
| 33094374 | What year did worldwide cell phone sales reach 180 million units? | 1998 | INCORRECT; predicted_answer: Worldwide cell phone sales reached 180 million units in the year 2000. | CORRECT; predicted_answer: Worldwide cell phone sales reached approximately 180 million units in **1998**. |
| 260996 | What year did Christian Slater play Winthrop Paroo in the stage production of The Music Man at New York City Center? | 1980 | INCORRECT; predicted_answer: Christian Slater played Winthrop Paroo in the stage production of The Music Man at New York City Center in 2021. | CORRECT; predicted_answer: Christian Slater played Winthrop Paroo in the 1980 production of *The Music Man* at New York City Center. |
| 91195 | What year did the Wimbledon Championships first give prize money to professional players? | 1968 | CORRECT; predicted_answer: The Wimbledon Championships first awarded prize money to professional players in 1968. | not run |


Rerun-pool entries have no second-stage filtering response unless they reached the panel before the transient failure.

## Rejected And Rerun Decisions

| Page ID | Stage | Exact reason | Page/question |
| ---: | --- | --- | --- |
| 9316 | `route_generation` | `wikipedia_infobox_llm_discarded:No date or year information is present in the table to form a valid Date answer_type question.` | England |
| 22093 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What year did the original Baltimore Bullets win their only National Basketball Association championship? |
| 17416221 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What year does the population data for the provinces of South Africa in the administrative divisions table come from? |
| 5489 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year were the Arica and Parinacota and Los Ríos regions established in Chile? |
| 14849 | `route_generation` | `wikipedia_infobox_extra_prompt_violation:no_social_science_research_prompt:census` | What year did the U.S. Census record the population of Illinois as 12,419,293? |
| 738 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What year was the system of urban and rural municipalities unified and simplified into municipalities in Albania? |
| 13277 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the Thirty Years' War end, defining the territorial divisions of the Holy Roman Empire? |
| 19261 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What year range is covered by the climate data averages and extremes for Monaco in the table titled 'Climate data for Monaco (1981–2010 averages, extremes 1966–present)'? |
| 11857 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What year was the film American Graffiti, directed by George Lucas, released? |
| 8083 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_2:answer_in_title` | What year did Dr. Dre receive the Grammy Lifetime Achievement Award as a member of N.W.A.? |
| 21355232 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what day, month, and year was Grand Teton National Park designated as a national park? |
| 292259 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Deutsche Welle start broadcasting in Pashto? |
| 31740 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | During which academic year did the University of Michigan-Ann Arbor have a total enrollment of 50,278 students? |
| 5488 | `route_generation` | `wikipedia_infobox_extra_prompt_violation:no_social_science_research_prompt:census` | What year was the population census conducted that recorded N'Djamena's population as 951,418? |
| 40010153 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What year did Goa have a total tourist arrival of 2,302,146? |
| 39776 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the amplification vulnerability in the BitTorrent protocol's libuTP fixed to prevent denial-of-service attacks? |
| 1640 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Alfred the Great conquer London and proclaim himself king of the Anglo-Saxons? |
| 151603 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what day, month, and year did Dean Martin appear in episode 7 of The Frank Sinatra Show? |
| 60382764 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the Reiwa era start according to the Gregorian calendar? |
| 41853326 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What year did Luis Suarez become the top goalscorer for Inter Miami CF with 25 goals? |
| 45367389 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Greater London form its twin city partnership with Berlin, Germany? |
| 5643 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Bailiwick of Jersey established as a Crown Dependency within the Channel Islands? |
| 19653842 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | What year did Queller and Strassmann publish their perspective on organisms as cooperating entities at different levels of biological organization? |
| 55440889 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What year was the 3G CDMA EVDO Rev A cellular network standard introduced? |
| 84952 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what day, month, and year did Marvelous Marvin Hagler defeat Alan Minter to win the WBA, WBC, and The Ring middleweight titles? |
| 22948 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what century is the earliest source that records Poseidon's offspring Triton by Amphitrite dated? |
| 30292 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the novel The Hobbit first published? |
| 2924002 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What year was the first and only Electronic Dance Music Awards held by Project X Magazine? |
| 33094374 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What year did worldwide cell phone sales reach 180 million units? |
| 260996 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What year did Christian Slater play Winthrop Paroo in the stage production of The Music Man at New York City Center? |
| 91195 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What year did the Wimbledon Championships first give prize money to professional players? |

### Rerun Records

| Page ID | Stage | Exact reason | Page/question |
| ---: | --- | --- | --- |
| 66958 | `search_longtail` | `search_longtail_verifier_error` | https://en.wikipedia.org/w/index.php?pageid=66958 |
| 105908 | `search_longtail` | `search_longtail_verifier_error` | https://en.wikipedia.org/w/index.php?pageid=105908 |
| 235959 | `search_longtail` | `search_longtail_verifier_error` | https://en.wikipedia.org/w/index.php?pageid=235959 |
| 105908 | `search_longtail` | `search_longtail_verifier_error` | https://en.wikipedia.org/w/index.php?pageid=105908 |
| 66958 | `search_longtail` | `search_longtail_verifier_error` | https://en.wikipedia.org/w/index.php?pageid=66958 |
| 235959 | `search_longtail` | `search_longtail_verifier_error` | https://en.wikipedia.org/w/index.php?pageid=235959 |

