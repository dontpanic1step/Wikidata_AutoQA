# Route 3 Streaming Wikipedia Page-ID Walkthrough - 2026-05-21

## Stats

- Run group ID: `wikipedia_stream_recipe_40_each_answer_type_single_fact_2026_05_21`
- Run segment ID: `recipe_combined`
- Artifact manifest: ``
- Mode: `page_id_stream_recipe`
- Page source: `table-search`
- Table-search queries: `insource:"wikitable"`
- Attempted page IDs: 258
- Unique attempted page IDs: 150
- Stream state reset at run start: yes
- Auto rerun pool once: yes
- Auto-rerun attempted page IDs: 0
- Accepted QAs: 15
- Rejected QAs/pages: 169
- Transient rerun attempts during run: 79
- Wall-clock runtime: 0.6098s
- DuckDuckGo top K: 5
- Generated search queries per QA: 2
- DuckDuckGo parallel queries: 3
- Route 3 reasoning_type constraint: `single_fact`
- Route 3 answer_type constraint: `Person, Place, Other, Date, Number`
- Route 3 table filter modes: `no_big_numbers, no_social_science_research`
- Page-id bounds: None to None
- Stream state: `D:\Study\AI\My-research\Wikidata_Framework\outputs\wikipedia_stream_recipe_40_each_answer_type_single_fact_2026_05_21_state.json`
- Accepted output: `D:\Study\AI\My-research\Wikidata_Framework\outputs\wikipedia_stream_recipe_40_each_answer_type_single_fact_2026_05_21_accepted.jsonl`
- Rejected output: `D:\Study\AI\My-research\Wikidata_Framework\outputs\wikipedia_stream_recipe_40_each_answer_type_single_fact_2026_05_21_rejected.jsonl`
- Domain policy: `domain_and_subdomain_optional_for_page_id_streaming`
- Rerun pool after run: `493129, 413079, 179348`

### Recipe Segments

| Configured answer_type | Record limit | Attempted page IDs | Accepted | Rejected | Rerun |
| --- | ---: | ---: | ---: | ---: | ---: |
| Person | 40 | 49 | 2 | 35 | 12 |
| Place | 40 | 51 | 2 | 38 | 11 |
| Other | 40 | 59 | 4 | 29 | 26 |
| Date | 40 | 52 | 1 | 31 | 20 |
| Number | 40 | 47 | 3 | 34 | 10 |

### Survival By Layer

| Layer | Entered | Failed | Survived | Layer survival | Cumulative survival |
| --- | ---: | ---: | ---: | ---: | ---: |
| Page-id reservation | 258 | 0 | 258 | 100.0% | 100.0% |
| Unresolved or returned to rerun pool | 258 | 0 | 258 | 100.0% | 100.0% |
| Page extraction, table grading, and QA generation | 258 | 46 | 212 | 82.2% | 82.2% |
| Rewrite and surface validation | 212 | 13 | 199 | 93.9% | 77.1% |
| DuckDuckGo long-tail filtering | 199 | 62 | 137 | 68.8% | 53.1% |
| Second-stage model grading | 137 | 43 | 94 | 68.6% | 36.4% |
| Shared route-aware validation | 94 | 5 | 89 | 94.7% | 34.5% |
| Deduplication | 89 | 0 | 89 | 100.0% | 34.5% |
| Other rejection | 89 | 0 | 89 | 100.0% | 34.5% |

### Failure Reasons

| Stage | Exact reason | Count |
| --- | --- | ---: |
| `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | 43 |
| `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | 32 |
| `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | 15 |
| `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | 9 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_social_science_research:population` | 6 |
| `search_longtail` | `search_longtail_verifier_rejected:full_question:answer_in_title` | 6 |
| `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | 6 |
| `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | 5 |
| `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | 4 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=1.0000;threshold=0.5000;no_social_science_research:population` | 4 |
| `route_generation` | `wikipedia_infobox_answer_type_not_allowed:answer_type_not_allowed:Number; allowed=Number` | 3 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:word_marker=billion` | 3 |
| `search_longtail` | `search_longtail_verifier_rejected:keyword_query_2:answer_in_title` | 3 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_10000_rate=0.2885;threshold=0.2000` | 2 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=0.5000;threshold=0.5000` | 2 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=0.5000;threshold=0.5000;no_social_science_research:population` | 2 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=0.6667;threshold=0.5000;no_social_science_research:census,population` | 2 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=0.6667;threshold=0.5000;no_social_science_research:population` | 2 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=1.0000;threshold=0.5000` | 2 |
| `route_generation` | `wikipedia_infobox_table_score_below_minimum:table_score_below_minimum:min_table_score=0.0000;best_score=-0.2000` | 2 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:active` | 1 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No date or year information is present in the top-ranked table to support a factual date question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No numeric data available in the top-ranked tables to form a valid Number answer question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No specific date or year is provided in the table for precooled jet engine / LACE prototype stage.` | 1 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_10000_rate=0.2786;threshold=0.2000;no_social_science_research:population` | 1 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=0.5185;threshold=0.5000;no_social_science_research:population` | 1 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=0.5208;threshold=0.5000;no_social_science_research:population` | 1 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=0.5984;threshold=0.5000;no_social_science_research:census,population` | 1 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=0.7024;threshold=0.5000` | 1 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=0.7500;threshold=0.5000` | 1 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=0.8750;threshold=0.5000` | 1 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:word_marker=million,billion` | 1 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:word_marker=million;no_social_science_research:survey` | 1 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_social_science_research:census,population` | 1 |
| `route_generation` | `wikipedia_infobox_table_score_below_minimum:table_score_below_minimum:min_table_score=0.0000;best_score=-0.9500` | 1 |

### Answer Type Stats

| Scope | Answer type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `Date` | 1 | 26 | 27 | 3.7% |
| Current Run Records | `Number` | 6 | 22 | 28 | 21.4% |
| Current Run Records | `Other` | 4 | 22 | 26 | 15.4% |
| Current Run Records | `Person` | 2 | 25 | 27 | 7.4% |
| Current Run Records | `Place` | 2 | 28 | 30 | 6.7% |
| Current Run Records | `unknown` | 0 | 46 | 46 | 0.0% |

### Reasoning Type Stats

| Scope | Reasoning type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `single_fact` | 15 | 123 | 138 | 10.9% |
| Current Run Records | `wikipedia_table_fact` | 0 | 46 | 46 | 0.0% |

### Rerun Pool After Run

| Page ID | Exact reason |
| ---: | --- |
| 493129 | `search_longtail_verifier_error` |
| 413079 | `search_longtail_verifier_error` |
| 179348 | `search_longtail_verifier_error` |


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
| `candidate_processing_seconds` | 184 | 10002.8908 | 54.3635 | 152.7758 |
| `duckduckgo_search_seconds` | 125 | 3679.3862 | 29.4351 | 79.6681 |
| `first_paragraph_extract_seconds` | 144 | 70.6154 | 0.4904 | 3.0238 |
| `llm_question_generation_seconds` | 144 | 2970.9734 | 20.6318 | 58.5833 |
| `number_reference_margin_seconds` | 125 | 0.0024 | 0.0000 | 0.0002 |
| `page_fetch_seconds` | 184 | 362.7799 | 1.9716 | 28.9433 |
| `rewrite_seconds` | 138 | 2672.3899 | 19.3651 | 58.3481 |
| `second_stage_grading_seconds` | 63 | 3650.9601 | 57.9517 | 104.7771 |
| `table_parse_seconds` | 184 | 297.5376 | 1.6171 | 9.8637 |
| `total_generation_seconds` | 184 | 3735.2315 | 20.3002 | 71.9106 |
| `total_processing_seconds` | 184 | 10002.8908 | 54.3635 | 152.7758 |

## Accepted Candidates

| Page ID | Question | Answer | Source |
| ---: | --- | --- | --- |
| 19653842 | Who proposed the view that organisms can be seen as cooperating entities at different levels of biological organization? | Queller and Strassmann | https://en.wikipedia.org/wiki/Organism |
| 2924002 | Who won the British Dance Act award at the BRIT Awards before the 2021 hiatus? | Charli XCX | https://en.wikipedia.org/wiki/Electronic_dance_music |
| 229275 | Which country produced 261 kilotonnes of lamb and mutton in 2012? | Algeria | https://en.wikipedia.org/wiki/Lamb_and_mutton |
| 113933 | Where was the climate data recorded that shows a record high temperature of 109 °F (43 °C) in July? | Iowa City | https://en.wikipedia.org/wiki/Iowa_City,_Iowa |
| 86224 | Which venue at the 1928 Summer Olympics had the smallest spectator capacity listed? | Schermzaal | https://en.wikipedia.org/wiki/1928_Summer_Olympics |
| 18938412 | Which Richard Marx song won the ASCAP Film & TV Award for Most Performed Song from Motion Picture? | Surrender to Me | https://en.wikipedia.org/wiki/Richard_Marx |
| 67436 | Which compound in the table has the lowest EC50 for norepinephrine release? | Dextroamphetamine | https://en.wikipedia.org/wiki/Pseudoephedrine |
| 180763 | Which subject at the University of Göttingen is ranked 72nd globally in the THE Subject Ranking 2024? | Physical sciences | https://en.wikipedia.org/wiki/University_of_Göttingen |
| 108353 | What month, day, and year did Edwin G. Smith start his term as the first mayor of Aurora, Colorado? | 1907-04-15 | https://en.wikipedia.org/wiki/Aurora,_Colorado |
| 31940 | How many states claimed a 12-mile territorial sea limit in 1960 according to the United Nations Convention on the Law of the Sea? | 34 | https://en.wikipedia.org/wiki/United_Nations_Convention_on_the_Law_of_the_Sea |
| 323058 | What was the undergraduate admit rate percentage for the 2021 entering class at the University of Nebraska–Lincoln? | 88.3 | https://en.wikipedia.org/wiki/University_of_Nebraska–Lincoln |
| 20663 | What is the approximate peak ground acceleration in g for level V (Moderate) on the Modified Mercalli intensity scale? | 0.062 | https://en.wikipedia.org/wiki/Modified_Mercalli_intensity_scale |
| 55440889 | How many LTE-FDD cellular frequency bands does the Pixel 2 support? | 18 | https://en.wikipedia.org/wiki/Pixel_2 |
| 2924002 | How many categories are nominated and awarded at the global DJ awards event held annually in Ibiza for electronic dance music? | 11 | https://en.wikipedia.org/wiki/Electronic_dance_music |
| 235959 | In how many distinct years did Farrah Fawcett appear in films listed in the table? | 13 | https://en.wikipedia.org/wiki/Farrah_Fawcett |

## Second-Stage Filtering Responses

These are the small-model QA responses used by the second-stage filter: `openai/gpt-4.1-mini` and `google/gemini-3-flash-preview`.

| Page ID | Question | Reference answer | openai/gpt-4.1-mini | google/gemini-3-flash-preview |
| ---: | --- | --- | --- | --- |
| 19653842 | Who proposed the view that organisms can be seen as cooperating entities at different levels of biological organization? | Queller and Strassmann | INCORRECT; predicted_answer: The view that organisms can be seen as cooperating entities at different levels of biological organization was proposed by David Sloan Wilson. | INCORRECT; predicted_answer: This view is most prominently associated with **Leo Buss**, who detailed the concept in his 1987 book *The Evolution of Individuality*, and **John Maynard Smith and Eörs Szathmáry**, who expanded on it in their 1995 work *The Major Transitions in Evolution*. |
| 2924002 | Who won the British Dance Act award at the BRIT Awards before the 2021 hiatus? | Charli XCX | INCORRECT; predicted_answer: The British Dance Act award at the BRIT Awards before the 2021 hiatus was won by Rudimental in 2019. | INCORRECT; predicted_answer: **Jamiroquai** won the British Dance Act award in 2004, which was the last time the category was presented before it was discontinued and later reinstated in 2022. |
| 229275 | Which country produced 261 kilotonnes of lamb and mutton in 2012? | Algeria | INCORRECT; predicted_answer: In 2012, China produced 261 kilotonnes of lamb and mutton. | INCORRECT; predicted_answer: **New Zealand** produced 261 kilotonnes of lamb and mutton in 2012. |
| 113933 | Where was the climate data recorded that shows a record high temperature of 109 °F (43 °C) in July? | Iowa City | NOT_ATTEMPTED; predicted_answer: Please provide the image or data showing the record high temperature of 109 °F (43 °C) in July so I can identify where it was recorded. | INCORRECT; predicted_answer: This record high temperature for July was recorded in **Paris, France**, at the Paris-Montsouris weather station on July 25, 2019. |
| 86224 | Which venue at the 1928 Summer Olympics had the smallest spectator capacity listed? | Schermzaal | INCORRECT; predicted_answer: The venue with the smallest spectator capacity listed at the 1928 Summer Olympics was the Shooting Range, with a capacity of 3,000 spectators. | INCORRECT; predicted_answer: The **Monnikenhuize** stadium in Arnhem, which hosted two football matches, had the smallest listed spectator capacity at **5,000**. |
| 18938412 | Which Richard Marx song won the ASCAP Film & TV Award for Most Performed Song from Motion Picture? | Surrender to Me | INCORRECT; predicted_answer: The Richard Marx song that won the ASCAP Film & TV Award for Most Performed Song from Motion Picture is "Right Here Waiting." | INCORRECT; predicted_answer: The Richard Marx song that won the ASCAP Film & TV Award for Most Performed Song from a Motion Picture is **"Now and Forever"** (from the film *The Getaway*). He received the award in 1995. |
| 67436 | Which compound in the table has the lowest EC50 for norepinephrine release? | Dextroamphetamine | INCORRECT; predicted_answer: The compound with the lowest EC50 for norepinephrine release in the table is **MDMA**, with an EC50 of 0.11 µM. | NOT_ATTEMPTED; predicted_answer: Please provide the table or the list of compounds you are referring to, as it was not included in your message. Once provided, I can identify the compound with the lowest EC50 value for you. |
| 180763 | Which subject at the University of Göttingen is ranked 72nd globally in the THE Subject Ranking 2024? | Physical sciences | INCORRECT; predicted_answer: The subject "Law" at the University of Göttingen is ranked 72nd globally in the THE Subject Ranking 2024. | INCORRECT; predicted_answer: **Life Sciences** is ranked 72nd globally in the Times Higher Education (THE) World University Rankings by Subject 2024. |
| 108353 | What month, day, and year did Edwin G. Smith start his term as the first mayor of Aurora, Colorado? | 1907-04-15 | INCORRECT; predicted_answer: Edwin G. Smith started his term as the first mayor of Aurora, Colorado, on February 14, 1907. | INCORRECT; predicted_answer: Edwin G. Smith started his term as the first mayor of Aurora (then known as the Town of Fletcher) on **May 11, 1891**. |
| 31940 | How many states claimed a 12-mile territorial sea limit in 1960 according to the United Nations Convention on the Law of the Sea? | 34 (acceptable range: anything between 33 and 35) | INCORRECT; predicted_answer: In 1960, only 4 states claimed a 12-mile territorial sea limit according to the context of the United Nations Convention on the Law of the Sea. | INCORRECT; predicted_answer: According to UN records from the 1960 Second United Nations Conference on the Law of the Sea (UNCLOS II), **26 states** claimed a 12-mile territorial sea limit. |
| 323058 | What was the undergraduate admit rate percentage for the 2021 entering class at the University of Nebraska–Lincoln? | 88.3 (acceptable range: anything between 87.417 and 89.183) | INCORRECT; predicted_answer: The undergraduate admit rate for the 2021 entering class at the University of Nebraska–Lincoln was approximately 78%. | INCORRECT; predicted_answer: The undergraduate admit rate for the 2021 entering class at the University of Nebraska–Lincoln was **82%**. |
| 20663 | What is the approximate peak ground acceleration in g for level V (Moderate) on the Modified Mercalli intensity scale? | 0.062 (acceptable range: anything between 0.052 and 0.072) | INCORRECT; predicted_answer: The approximate peak ground acceleration (PGA) for level V (Moderate) on the Modified Mercalli Intensity scale is about 0.04 to 0.09 g. | INCORRECT; predicted_answer: The approximate peak ground acceleration (PGA) for level V on the Modified Mercalli intensity scale is **0.039g to 0.092g**. |
| 55440889 | How many LTE-FDD cellular frequency bands does the Pixel 2 support? | 18 (acceptable range: anything between 17 and 19) | INCORRECT; predicted_answer: The Pixel 2 supports 12 LTE-FDD cellular frequency bands. | INCORRECT; predicted_answer: The Pixel 2 supports **27** LTE-FDD frequency bands.  The supported bands are: 1, 2, 3, 4, 5, 7, 8, 12, 13, 17, 20, 25, 26, 28, 29, 30, 32, 66 (and TDD bands 38, 40, 41). |
| 2924002 | How many categories are nominated and awarded at the global DJ awards event held annually in Ibiza for electronic dance music? | 11 (acceptable range: anything between 10 and 12) | INCORRECT; predicted_answer: The Global DJ Awards held annually in Ibiza feature 16 categories in which DJs are nominated and awarded. | INCORRECT; predicted_answer: The DJ Awards, held annually in Ibiza, typically feature approximately **22 to 24 categories** each year, divided between music categories (voted for by the public) and special industry awards (selected by a panel). |
| 235959 | In how many distinct years did Farrah Fawcett appear in films listed in the table? | 13 (acceptable range: anything between 12 and 14) | NOT_ATTEMPTED; predicted_answer: Please provide the table you are referring to so I can determine the number of distinct years Farrah Fawcett appeared in films. | INCORRECT; predicted_answer: Since you did not provide the table, I cannot give you a specific count based on your source.  However, according to her complete filmography, Farrah Fawcett appeared in films released in **21** distinct years:  1969, 1970, 1976, 1978, 1979, 1980, 1981, 1984, 1986, 1987, 1988, 1989, 1991, |
| 9316 | England |  | not run | not run |
| 17416221 | South Africa |  | not run | not run |
| 32611 | Vietnam War |  | not run | not run |
| 5489 | Chile |  | not run | not run |
| 13277 | Holy Roman Empire |  | not run | not run |
| 19261 | Who is the person involved in Monaco's negotiation of the Association Agreement in its foreign relations? | Monaco | not run | not run |
| 14849 | Who is the person linked to the slogan of Illinois? | Abraham Lincoln | not run | not run |
| 22093 | Who won the National Basketball Association championship in 2016? | Cleveland Cavaliers | not run | not run |
| 738 | Who holds the office of President in Albania? | Bajram Begaj | CORRECT; predicted_answer: As of 2024, the President of Albania is Bajram Begaj. | not run |
| 11857 | Who was the director of the 1973 film American Graffiti? | George Lucas | not run | not run |
| 199445 | Who was the manager of Derby County from 14 November 2020 to 26 June 2022? | Wayne Rooney | not run | not run |
| 31740 | Who created the Klein–Goldberger macroeconomic model at the University of Michigan? | Lawrence Klein | not run | not run |
| 5488 | Chad |  | not run | not run |
| 41853326 | Who was the head coach of Inter Miami CF on April 14, 2026? | Guillermo Hoyos | not run | not run |
| 105908 | Ford Mustang |  | not run | not run |
| 66958 | Who is the person responsible for issuing the official currency Renminbi of the People's Republic of China? | People's Bank of China | not run | not run |
| 60382764 | Who became the 126th Emperor of Japan and began the Reiwa era on 1 May 2019? | Naruhito | not run | not run |
| 12186 | Guinea-Bissau |  | not run | not run |
| 5643 | Channel Islands |  | not run | not run |
| 45367389 | Which person from Germany became the twin city partner of Greater London in 2000? | Berlin | not run | not run |
| 217231 | Who gave commentary on the pilot episode in the DVD release of Curb Your Enthusiasm Season 1? | Larry David | not run | not run |
| 34411 | Who is the brightest star in the Zodiac constellation Virgo based on the 1977 IAU boundaries? | Spica | not run | not run |
| 235916 | Who portrayed Maureen Evans in the 1997 movie Scream 2? | Jada Pinkett Smith | not run | not run |
| 22948 | According to Hesiod's Theogony, who is the mother of Triton, the offspring of Poseidon? | Amphitrite | not run | not run |
| 55440889 | Who is the developer of the Pixel 2 and Pixel 2 XL smartphones? | Google | not run | not run |
| 33094374 | Telecommunications |  | not run | not run |
| 84952 | Who did Marvelous Marvin Hagler defeat by technical knockout in the third round on April 15, 1985, to retain multiple middleweight titles? | Thomas Hearns | not run | not run |
| 30292 | Who is the royal descendant restored to his ancestral throne in The Lord of the Rings? | Aragorn | not run | not run |
| 260996 | Who portrayed Randle Patrick "Mac" McMurphy in the 2004–2005 staging of One Flew Over the Cuckoo's Nest at the Gielgud Theatre? | Christian Slater | not run | not run |
| 91195 | Who was the youngest male singles champion at the Wimbledon Championships? | Boris Becker | not run | not run |
| 235959 | Who portrayed Marjorie in the 1986 movie Extremities? | Farrah Fawcett | CORRECT; predicted_answer: Farrah Fawcett portrayed Marjorie in the 1986 movie Extremities. | not run |
| 8083 | Who was awarded the Grammy for Producer of the Year, Non-Classical in 2001? | Dr. Dre | not run | not run |
| 21355232 | Who founded the National Park Service in the United States? | Stephen Mather | INCORRECT; predicted_answer: The National Park Service in the United States was established by President Woodrow Wilson, who signed the National Park Service Organic Act into law on August 25, 1916. The agency was created to manage and protect national parks and monuments. | INCORRECT; predicted_answer: The National Park Service was founded by **President Woodrow Wilson** when he signed the Organic Act into law on August 25, 1916. Its establishment was the result of a campaign led by industrialist **Stephen Mather** (who became the first director) and his assistant **Horace Albright**. |
| 292259 | Who founded Deutsche Welle? | Hans Bausch | INCORRECT; predicted_answer: Deutsche Welle was founded by the Federal Republic of Germany (West Germany) government. | INCORRECT; predicted_answer: Deutsche Welle was founded by the **government of the Federal Republic of Germany** (West Germany). It was established as a public corporation under federal law, with its first broadcast occurring on May 3, 1953. |
| 40010153 | Who was the person after whom the largest city by population in Goa is named? | Vasco da Gama | CORRECT; predicted_answer: The largest city by population in Goa is Vasco da Gama, named after the Portuguese explorer Vasco da Gama. | not run |
| 105391 | B movie |  | not run | not run |
| 569459 | White-tailed deer |  | not run | not run |
| 68761 | Publishing |  | not run | not run |
| 246920 | Visa Inc. |  | not run | not run |
| 2114995 | In which species were the binding affinities of dextromethorphan and dextrorphan to the NMDAR (MK-801) site tested? | Rat | not run | not run |
| 17278765 | Which school won the national college football championship in the 1924 NCAA Division I FBS season? | Notre Dame | not run | not run |
| 1625048 | Kingdom of Bohemia |  | not run | not run |
| 342334 | In which city is the scene depicted in Rembrandt's 1632 painting 'The Anatomy Lesson of Dr. Nicolaes Tulp' set? | Amsterdam | not run | not run |
| 96875 | Which place was served by the Great Western Railway's broad gauge track in 1851? | England | not run | not run |
| 7549995 | Elk |  | not run | not run |
| 43088 | In which city did Yogi Berra manage a team that lost the 1964 World Series? | St. Louis | not run | not run |
| 156745 | Which awards ceremony nominated Julia Roberts for Best Actress for her role in Pretty Woman? | Academy Awards | CORRECT; predicted_answer: Julia Roberts was nominated for Best Actress for her role in *Pretty Woman* at the Academy Awards (Oscars). | not run |
| 151451 | In which city was the documentary titled 'Orange Rockcorps at the Royal Albert Hall' released in 2008? | London | not run | not run |
| 599 | Which branch of Afroasiatic languages uses 'pínà' as the masculine form of the numeral 'one'? | Gidar | CORRECT; predicted_answer: The Chadic branch of Afroasiatic languages uses "pínà" as the masculine form of the numeral "one." | not run |
| 31730 | British Armed Forces |  | not run | not run |
| 26457880 | Where is the headquarters of Air India located? | Gurugram | not run | not run |
| 32005912 | Where was the 2011 short film featuring Grimes as Saint-Boniface released? | Saint-Boniface | not run | not run |
| 407239 | The Indian Express |  | not run | not run |
| 57877 | Where is sodium hydroxide typically used for the base-driven hydrolysis of esters, known as saponification? | skin | INCORRECT; predicted_answer: Sodium hydroxide is typically used in aqueous solution for the base-driven hydrolysis of esters during saponification, such as in soap making where it hydrolyzes triglycerides (fats/oils) into glycerol and soap (salts of fatty acids). | INCORRECT; predicted_answer: Sodium hydroxide is typically used for saponification in the **industrial and artisanal production of soap**, where it reacts with triglycerides (fats and oils) to create glycerol and fatty acid salts. |
| 1064 | Almond |  | not run | not run |
| 15049 | In which city in Indiana is the radio affiliate with the call sign WFNI located? | Indianapolis | not run | not run |
| 80482 | What place served as the residence of Beatrix of the Netherlands and her children before she became queen? | Lage Vuursche | INCORRECT; predicted_answer: Before becoming queen, Beatrix of the Netherlands and her children lived at the castle Drakensteyn. | CORRECT; predicted_answer: **Kasteel Drakensteyn** in Lage Vuursche served as the residence of Beatrix and her family from 1963 until 1981. |
| 76988 | Where is the V4 electrode positioned in the 12-lead ECG according to Electrocardiography standards? | Fifth intercostal space on the midclavicular line | CORRECT; predicted_answer: The V4 electrode in a 12-lead ECG is positioned in the 5th intercostal space at the midclavicular line on the left side of the chest. | not run |
| 35412202 | Where were Wikipedia articles' interlanguage links listed separately before being centralized by Wikidata? | Wikipedia | not run | not run |
| 129619 | At which film awards ceremony did Whoopi Goldberg win the Best Supporting Actress award for the film Ghost? | Academy Awards | not run | not run |
| 67923 | East Sussex |  | not run | not run |
| 23906 | Where was the highest temperature of 39.9 °C (103.8 °F) recorded in the Peterborough area? | Wittering | INCORRECT; predicted_answer: The highest temperature of 39.9 °C (103.8 °F) in the Peterborough area was recorded at the Peterborough Airport. | CORRECT; predicted_answer: The temperature of 39.9 °C (103.8 °F) was recorded at the **Wittering** Royal Air Force station on July 19, 2022. |
| 1161220 | Which constituency did Khushbu Sundar represent in the 2021 Tamil Nadu Legislative Assembly election? | Thousand Lights | not run | not run |
| 47498 | In the original Japanese script of Zero Wing, what location is mentioned as being taken over with the help of Federation government forces? | bases | not run | not run |
| 540317 | In which terrain mode does the Ford Explorer's Terrain Management System provide optimal driving conditions for sand? | Sand mode | CORRECT; predicted_answer: The Ford Explorer's Terrain Management System provides optimal driving conditions for sand in the **Sand** mode. | not run |
| 151603 | Where is the television special 'Dean Martin's Christmas at Seaworld' set? | Seaworld | not run | not run |
| 18947898 | From which country did the Amnesty International Secretary General who served between 1992 and 2001 originate? | Senegal | CORRECT; predicted_answer: The Amnesty International Secretary General who served between 1992 and 2001, Pierre Sané, originated from Senegal. | not run |
| 57905 | Which city in the Sakha Republic has the lowest average daily minimum temperature in January? | Oymyakon | not run | not run |
| 1640 | Where was Alfred the Great born around the year 848? | Wantage, Berkshire | INCORRECT; predicted_answer: Alfred the Great was born in Wantage, which is in present-day Oxfordshire, England, around the year 848. | CORRECT; predicted_answer: Alfred the Great was born in **Wantage**, in the historic county of Berkshire (now Oxfordshire), England. |
| 47864412 | In the Nepali language consonant phonemes table, what is the place of articulation for the consonant symbol 'ɡ'? | Velar | CORRECT; predicted_answer: In the Nepali language consonant phonemes table, the consonant symbol 'ɡ' is articulated at the **velar** place of articulation. | not run |
| 214179 | In which city was the American industrial metal band Ministry formed? | Chicago | not run | not run |
| 57659 | What stadium in Tunis is shared by Club Africain and Espérance Sportive de Tunis? | Stade Olympique de Radès Stade El Menzah | INCORRECT; predicted_answer: The stadium in Tunis shared by Club Africain and Espérance Sportive de Tunis is the Stade Olympique de Radès. | CORRECT; predicted_answer: The stadium shared by Club Africain and Espérance Sportive de Tunis is the **Stade Olympique de Hammadi Agrebi** (commonly known as the **Stade de Radès**). |
| 22461 | Where is the incidence of hip fractures per 1000 person-years highest among individuals over 64 years old with osteoporosis? | Osteoporosis | not run | not run |
| 2056103 | What award did Gemini Ganesan receive for his performance in the film Kaaviya Thalaivi? | Tamil Nadu State Film Award for Best Actor | not run | not run |
| 15240 | Imam |  | not run | not run |
| 250230 | What tyre size was fitted on the front and rear wheels of the Mazda RX-7 Series 8 Type RB? | 225/50R16 92V | INCORRECT; predicted_answer: The Mazda RX-7 Series 8 Type RB was fitted with 205/50ZR16 tyres on the front wheels and 225/50ZR16 tyres on the rear wheels. | CORRECT; predicted_answer: The Mazda RX-7 Series 8 Type RB was fitted with **225/50R16** tyres on both the front and rear wheels. |
| 57951 | What was the French name of the department corresponding mostly to the territory of Zeeland? | Département des Bouches-de-l'Escaut | CORRECT; predicted_answer: The French name of the department corresponding mostly to the territory of Zeeland was **Bouches-de-l'Escaut**. | not run |
| 200129 | Hair loss |  | not run | not run |
| 38657800 | What Android version did the original Google Pixel and Pixel XL launch with? | 7.1 Nougat | CORRECT; predicted_answer: The original Google Pixel and Pixel XL launched with Android 7.1 Nougat. | not run |
| 479109 | Which graduate program at Southern Methodist University was ranked 34th by U.S. News & World Report? | Business | not run | not run |
| 221478 | Which Broadway venue hosted Harvey Fierstein's play 'Casa Valentina'? | Samuel J. Friedman Theatre | CORRECT; predicted_answer: Harvey Fierstein's play "Casa Valentina" was hosted at the Samuel J. Friedman Theatre on Broadway. | not run |
| 241717 | Clinical trial |  | not run | not run |
| 52374650 | King |  | not run | not run |
| 441357 | What is the word for Thursday in the Somali language? | Khamiis | CORRECT; predicted_answer: The word for Thursday in the Somali language is **"Khamiis."** | not run |
| 356375 | What consonant in the Yoruba language is identified as a rhotic? | ɾ | INCORRECT; predicted_answer: The consonant identified as a rhotic in the Yoruba language is /r/. | CORRECT; predicted_answer: The consonant identified as a rhotic in the Yoruba language is the letter **r**, which is typically pronounced as an alveolar tap [ɾ]. |
| 22304 | What compound represents osmium in the +5 oxidation state? | OsF5 | INCORRECT; predicted_answer: Osmium pentachloride (OsCl₅) is a common compound in which osmium is in the +5 oxidation state. | CORRECT; predicted_answer: The most common compound representing osmium in the +5 oxidation state is **osmium pentafluoride (OsF₅)**. |
| 1787105 | What is the term for the mating system in animal sexual behaviour where one female mates with multiple males? | Polyandry | not run | not run |
| 56668 | Apricot |  | not run | not run |
| 683599 | Where did Hedley Verity take his best bowling figures of 10 wickets for 10 runs in a County Championship innings? | Headingley | not run | not run |
| 32551521 | According to FIFA eligibility rules, which national team represents the legal nationality of Denmark? | Denmark | not run | not run |
| 4595410 | 1970 United States census |  | not run | not run |
| 104944 | What was the type of military action at the Battle of Narva during Charles XII's campaigns? | Battle | not run | not run |
| 333199 | Which SkyTeam member airline includes the affiliates SAS Connect and SAS Link? | Scandinavian Airlines | CORRECT; predicted_answer: The SkyTeam member airline that includes the affiliates SAS Connect and SAS Link is Scandinavian Airlines (SAS). | not run |
| 1146123 | For which work did Colin Hanks receive a Spike Video Game Award for Best Cast? | Peter Jackson's King Kong: The Official Game of the Movie | not run | not run |
| 16801 | Krav Maga |  | not run | not run |
| 226734 | Which Nigerian state was created from the Western Region in 1963? | Mid-Western Region | not run | not run |
| 39776 | Which protocol in the UDP-based amplification attacks table has a fixed amplification factor in version 1.5.6? | Memcached | not run | not run |
| 261671 | What was the magnitude of the largest aftershock in April 1990 following the 1989 Loma Prieta earthquake? | 5.4 M L | INCORRECT; predicted_answer: The largest aftershock in April 1990 following the 1989 Loma Prieta earthquake had a magnitude of 6.9. | CORRECT; predicted_answer: The largest aftershock in April 1990 following the Loma Prieta earthquake was a **magnitude 5.4** (or 5.5 depending on the scale used) earthquake that occurred on **April 18, 1990**, near Watsonville, California. |
| 695780 | Who won the Best Film Editing award for the film Casino (1995)? | Thelma Schoonmaker | CORRECT; predicted_answer: The Best Film Editing award for the film *Casino* (1995) was won by Thelma Schoonmaker. | not run |
| 167051 | Which film featured Connie Francis as the singing voice of the character Dori Graham? | Rock, Rock, Rock! | not run | not run |
| 83316 | Which artist achieved a UK Singles Chart number 1 hit with the song "Dandy" written by Ray Davies? | Herman's Hermits | not run | not run |
| 194910 | What award did Steve Earle receive at the 2004 Americana Music Honors & Awards? | Spirit of Americana/Free Speech Award | not run | not run |
| 719515 | What year was Sony Pictures Television founded? | 2002 | not run | not run |
| 23809352 | Carbon-fiber reinforced polymer |  | not run | not run |
| 68145 | What year was The Jazz Singer inducted into the National Film Registry by the National Film Preservation Board? | 1989 | INCORRECT; predicted_answer: The Jazz Singer was inducted into the National Film Registry in 1996. | INCORRECT; predicted_answer: *The Jazz Singer* was inducted into the National Film Registry in **1996**. |
| 255380 | What year did Robin Tunney first appear in the TV series "Prison Break"? | 2005 | not run | not run |
| 931 | What year did Steve Ditko begin penciling issues for The Amazing Spider-Man? | 1963 | INCORRECT; predicted_answer: Steve Ditko began penciling issues for The Amazing Spider-Man in 1962. | CORRECT; predicted_answer: Steve Ditko began penciling *The Amazing Spider-Man* in **1963**, starting with issue #1. He also penciled the character's debut in *Amazing Fantasy* #15 in 1962. |
| 189455 | What year range defines the climate normals for Ulm based on recorded data? | 1991-2020 | CORRECT; predicted_answer: The climate normals for Ulm are defined based on recorded data from the year range 1991 to 2020. | not run |
| 158681 | Aircraft engine |  | not run | not run |
| 704720 | What year did Lisa Rinna make her Broadway debut as Roxie Hart in Chicago? | 2007 | not run | not run |
| 745757 | What year did SC Heerenveen finish second in the Eredivisie and qualify for the Champions League? | 1999-2000 | not run | not run |
| 722717 | What year did Michalis Konstantinou begin playing for the Cyprus national football team? | 1997 | INCORRECT; predicted_answer: Michalis Konstantinou began playing for the Cyprus national football team in 1996. | CORRECT; predicted_answer: Michalis Konstantinou began playing for the Cyprus national football team in **1997**. |
| 21865 | Which neurotransmitter system in the brain originates from the locus coeruleus and regulates anxiety and circadian rhythm? | Noradrenaline system | CORRECT; predicted_answer: The norepinephrine (noradrenaline) neurotransmitter system originates from the locus coeruleus and regulates anxiety and circadian rhythm. | not run |
| 21637 | In what year did England and Wales, Ireland, and the British Empire adopt January 1 as the start of the new year? | 1752 | not run | not run |
| 63972 | What year marks the end of the period covered by the climate data for Murmansk, including record temperatures, average precipitation, and sunshine hours? | 2020 | CORRECT; predicted_answer: The climate data for Murmansk, including record temperatures, average precipitation, and sunshine hours, covers up to the year 2020. | not run |
| 240432 | Provinces of Argentina |  | not run | not run |
| 199446 | Kazakh Soviet Socialist Republic |  | not run | not run |
| 105945 | What year did the Democratic party receive 81.3% of the vote in Newton, Massachusetts's presidential election? | 2020 | CORRECT; predicted_answer: The Democratic Party received 81.3% of the vote in Newton, Massachusetts's presidential election in the year 2020. | not run |
| 262135 | Rocket engine |  | not run | not run |
| 422038 | On what month, day, and year was the highest temperature of 40.8 °C ever recorded in Vigo? | 2016-08-07 | INCORRECT; predicted_answer: The highest temperature of 40.8 °C ever recorded in Vigo was on August 14, 2021. | CORRECT; predicted_answer: The highest temperature of 40.8 °C in Vigo was recorded on **August 7, 2016**. |
| 2209490 | What is the Unicode code point for the Arabic letter 'ḥā ʼ' according to the Romanization of Arabic comparison table? | 062D | CORRECT; predicted_answer: The Unicode code point for the Arabic letter **ḥāʼ** (ح) is **U+062D**. | not run |
| 438269 | What month, day, and year was the first episode of Batman Beyond first released? | 1999-01-10 | not run | not run |
| 42042635 | What year did Kumkum Bhagya win the Star Guild Award for Best Upcoming Drama Series? | 2015 | not run | not run |
| 107825 | What year range do the climate normals for Newport Beach, California cover? | 1991-2020 | CORRECT; predicted_answer: The climate normals for Newport Beach, California cover the 30-year period from 1991 to 2020. | not run |
| 1069583 | What is the lesson Dattatreya learned from observing the Moon as one of his 24 teachers from nature? | birth, death, rebirth and the cycle of existence does not change the oneness of soul, like moon it is a continuous eternal reality | INCORRECT; predicted_answer: Dattatreya learned the lesson of detachment and impermanence from the Moon. Observing the Moon’s waxing and waning, he understood that everything in life is transient and constantly changing, teaching him to remain detached and steady amidst life’s fluctuations. | CORRECT; predicted_answer: From the Moon, Dattatreya learned that the **Self (Atman) is changeless and eternal**, despite the perceived changes in its appearance.   Just as the Moon appears to wax and wane through phases while remaining the same celestial body, the soul remains constant and unaffected by the birth, growth, decay, and death of the physical body. The lesson is to identify with the unchanging spirit rather than the fluctuating states of the body and mind. |
| 61795854 | What year was the All India Institutes of Medical Sciences Raebareli established? | 2018 | not run | not run |
| 51524 | What was the U.S. release date of the film The Pink Panther 2? | 2009-02-06 | not run | not run |
| 155723 | What year did Debbie Gibson appear in the movie "Mega Shark Versus Giant Octopus"? | 2009 | not run | not run |
| 1608423 | In NCAA Division II men's team sports, during which season does the sport with the highest number of scholarships per team occur? | Fall | CORRECT; predicted_answer: In NCAA Division II men's team sports, football has the highest number of scholarships per team, and it occurs during the fall season. | not run |
| 368204 | What year did Faith Evans win the Grammy Award for Best Rap Performance by a Duo or Group for the song "I'll Be Missing You"? | 1998 | not run | not run |
| 1067134 | What year did Mary-Louise Parker win the Golden Globe Award for Best Performance by a TV Actress in a Musical or Comedy for her role in Weeds (TV series)? | 2006 | not run | not run |
| 168244 | What is the f-number value for an aperture value (AV) of 5 in the standard full-stop f-number scale? | 5.6 | CORRECT; predicted_answer: An aperture value (AV) of 5 corresponds to an f-number of approximately **f/5.6** on the standard full-stop f-number scale. | not run |
| 615800 | On what month, day, and year did Cafu score his first international goal for Brazil? | 1994-06-08 | INCORRECT; predicted_answer: Cafu scored his first international goal for Brazil on June 16, 1990. | CORRECT; predicted_answer: Cafu scored his first international goal for Brazil on **June 8, 1994**. |
| 241559 | How many layers of filling are in the Team USA limited edition Oreo? | 3 | not run | not run |
| 20804 | How many seats did the Christian Democratic Union (CDU) win in the Magdeburg city council election on 9 June 2024? | 13 (acceptable range: anything between 12 and 14) | INCORRECT; predicted_answer: The Christian Democratic Union (CDU) won 14 seats in the Magdeburg city council election on 9 June 2024. | CORRECT; predicted_answer: The CDU won **12 seats** in the Magdeburg city council election on June 9, 2024. |
| 17416221 | South Africa |  | not run | not run |
| 9316 | England |  | not run | not run |
| 32611 | Vietnam War |  | not run | not run |
| 5489 | Chile |  | not run | not run |
| 13277 | Holy Roman Empire |  | not run | not run |
| 738 | Albania |  | not run | not run |
| 14849 | What is the average high temperature in degrees Fahrenheit for Cairo, Illinois in July? | 90 | not run | not run |
| 22093 | How many National Basketball Association championships have the Chicago Bulls won? | 6 | not run | not run |
| 19261 | How many days per year does Monaco have an average precipitation of at least 1.0 mm based on 1981–2010 data? | 62.4 (acceptable range: anything between 61.776 and 63.024) | CORRECT; predicted_answer: Monaco has an average of 62 days per year with at least 1.0 mm of precipitation based on 1981–2010 data. | not run |
| 31740 | What was the number of first-time fall freshmen applicants at the University of Michigan in 2025? | 109112 | not run | not run |
| 292259 | In what year did Deutsche Welle begin broadcasting in the Persian language? | 1962 | not run | not run |
| 8083 | How many Grammy Awards has Dr. Dre won in total? | 7 | not run | not run |
| 5488 | Chad |  | not run | not run |
| 40010153 | How many average rainy days occur in Goa during July? | 27.2 | not run | not run |
| 151603 | How many episodes of The Dean Martin Show featured Dean Martin between 1965 and 1974? | 264 | not run | not run |
| 39776 | What is the amplification factor of the Memcached protocol in UDP amplification attacks used in denial-of-service attacks? | 50000 (acceptable range: anything between 49500 and 50500) | CORRECT; predicted_answer: The amplification factor of the Memcached protocol in UDP amplification attacks can be extremely high, often reported to be around **50,000 times** or more. This means a small UDP request to a vulnerable Memcached server can generate a response over 50,000 times larger, making it one of the largest amplification factors among UDP-based DDoS attack vectors. | not run |
| 1640 | How many years after Alfred the Great's birth was his first child Æthelflæd born? | 22 (acceptable range: anything between 21 and 23) | INCORRECT; predicted_answer: Alfred the Great was born in 849, and his first child Æthelflæd was born in 869.   So, Æthelflæd was born 20 years after Alfred the Great's birth. | CORRECT; predicted_answer: Æthelflæd was born approximately **21 years** after Alfred the Great. Alfred was born in 849, and Æthelflæd is believed to have been born around 870. |
| 45367389 | In what year was the twin city agreement between Greater London and Berlin established? | 2000 | not run | not run |
| 105908 | Ford Mustang |  | not run | not run |
| 60382764 | How many years are listed in the Reiwa era conversion table from Reiwa 1 to Reiwa 8? | 8 | not run | not run |
| 66958 | What was the daily volume percentage of the renminbi in global foreign exchange market turnover in April 2025? | 8.5 | not run | not run |
| 12186 | Guinea-Bissau |  | not run | not run |
| 5643 | Channel Islands |  | not run | not run |
| 41853326 | How many goals did Lionel Messi score for Inter Miami CF in the 2025 MLS season? | 43 | not run | not run |
| 217231 | How many episodes are in season 7 of Curb Your Enthusiasm? | 10 (acceptable range: anything between 9 and 11) | CORRECT; predicted_answer: Season 7 of *Curb Your Enthusiasm* has 10 episodes. | not run |
| 19653842 | How many cells make up a jellyfish according to Jack A. Wilson's study of organism-like colonies? | Many | not run | not run |
| 84952 | How many rounds did Marvelous Marvin Hagler fight in his professional boxing match against Alan Minter on September 27, 1980? | 3 | not run | not run |
| 33094374 | Telecommunications |  | not run | not run |
| 30292 | How many phases are identified in the quest structure analysis of The Hobbit? | 2 (acceptable range: anything between 1 and 3) | INCORRECT; predicted_answer: The quest structure analysis of *The Hobbit* identifies **five phases**. | INCORRECT; predicted_answer: In the quest structure analysis of *The Hobbit*, there are typically **three** primary phases identified:  1.  **Departure** (The Threshold) 2.  **Initiation** (The Journey/Trials) 3.  **Return** (The Homecoming) |
| 91195 | How many singles titles did Roger Federer win at the Wimbledon Championships during the Open Era? | 8 | not run | not run |
| 11857 | In which year did George Lucas direct the film titled 'Star Wars: Episode II – Attack of the Clones'? | 2002 | not run | not run |
| 22948 | How many sons did Poseidon have with Halia according to the list of offspring and their mothers? | 6 | not run | not run |
| 34411 | How many days does the Sun spend in the Virgo constellation according to the 1977 IAU boundaries? | 45 (acceptable range: anything between 44 and 46) | CORRECT; predicted_answer: According to the 1977 IAU constellation boundaries, the Sun spends about 44 days in the Virgo constellation. | not run |
| 199445 | How many matches did Wayne Rooney manage at Derby County? | 85 (acceptable range: anything between 84 and 86) | INCORRECT; predicted_answer: Wayne Rooney managed 170 matches at Derby County. | CORRECT; predicted_answer: Wayne Rooney managed **85 matches** at Derby County. |


## Rejected And Rerun Decisions

| Page ID | Stage | Exact reason | Page/question |
| ---: | --- | --- | --- |
| 9316 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_social_science_research:population` | England |
| 17416221 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=1.0000;threshold=0.5000;no_social_science_research:population` | South Africa |
| 32611 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_10000_rate=0.2885;threshold=0.2000` | Vietnam War |
| 5489 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=0.6667;threshold=0.5000;no_social_science_research:population` | Chile |
| 13277 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=1.0000;threshold=0.5000;no_social_science_research:population` | Holy Roman Empire |
| 19261 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | Who is the person involved in Monaco's negotiation of the Association Agreement in its foreign relations? |
| 14849 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | Who is the person linked to the slogan of Illinois? |
| 22093 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | Who won the National Basketball Association championship in 2016? |
| 738 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who holds the office of President in Albania? |
| 11857 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | Who was the director of the 1973 film American Graffiti? |
| 199445 | `search_longtail` | `search_longtail_verifier_rejected:full_question:answer_in_title` | Who was the manager of Derby County from 14 November 2020 to 26 June 2022? |
| 31740 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Who created the Klein–Goldberger macroeconomic model at the University of Michigan? |
| 5488 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=0.6667;threshold=0.5000;no_social_science_research:census,population` | Chad |
| 41853326 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | Who was the head coach of Inter Miami CF on April 14, 2026? |
| 105908 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=0.5000;threshold=0.5000` | Ford Mustang |
| 66958 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | Who is the person responsible for issuing the official currency Renminbi of the People's Republic of China? |
| 60382764 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | Who became the 126th Emperor of Japan and began the Reiwa era on 1 May 2019? |
| 12186 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=0.5000;threshold=0.5000;no_social_science_research:population` | Guinea-Bissau |
| 5643 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_social_science_research:population` | Channel Islands |
| 45367389 | `search_longtail` | `search_longtail_verifier_rejected:full_question:answer_in_title` | Which person from Germany became the twin city partner of Greater London in 2000? |
| 217231 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | Who gave commentary on the pilot episode in the DVD release of Curb Your Enthusiasm Season 1? |
| 34411 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Who is the brightest star in the Zodiac constellation Virgo based on the 1977 IAU boundaries? |
| 235916 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | Who portrayed Maureen Evans in the 1997 movie Scream 2? |
| 22948 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | According to Hesiod's Theogony, who is the mother of Triton, the offspring of Poseidon? |
| 55440889 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_2:answer_in_title` | Who is the developer of the Pixel 2 and Pixel 2 XL smartphones? |
| 33094374 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:word_marker=billion` | Telecommunications |
| 84952 | `search_longtail` | `search_longtail_verifier_rejected:full_question:answer_in_title` | Who did Marvelous Marvin Hagler defeat by technical knockout in the third round on April 15, 1985, to retain multiple middleweight titles? |
| 30292 | `search_longtail` | `search_longtail_verifier_rejected:full_question:answer_in_title` | Who is the royal descendant restored to his ancestral throne in The Lord of the Rings? |
| 260996 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_2:answer_in_title` | Who portrayed Randle Patrick "Mac" McMurphy in the 2004–2005 staging of One Flew Over the Cuckoo's Nest at the Gielgud Theatre? |
| 91195 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Who was the youngest male singles champion at the Wimbledon Championships? |
| 235959 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who portrayed Marjorie in the 1986 movie Extremities? |
| 8083 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | Who was awarded the Grammy for Producer of the Year, Non-Classical in 2001? |
| 21355232 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | Who founded the National Park Service in the United States? |
| 292259 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | Who founded Deutsche Welle? |
| 40010153 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who was the person after whom the largest city by population in Goa is named? |
| 105391 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:active` | B movie |
| 569459 | `route_generation` | `wikipedia_infobox_table_score_below_minimum:table_score_below_minimum:min_table_score=0.0000;best_score=-0.2000` | White-tailed deer |
| 68761 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=0.7024;threshold=0.5000` | Publishing |
| 246920 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:word_marker=million,billion` | Visa Inc. |
| 2114995 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In which species were the binding affinities of dextromethorphan and dextrorphan to the NMDAR (MK-801) site tested? |
| 17278765 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which school won the national college football championship in the 1924 NCAA Division I FBS season? |
| 1625048 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_10000_rate=0.2786;threshold=0.2000;no_social_science_research:population` | Kingdom of Bohemia |
| 342334 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In which city is the scene depicted in Rembrandt's 1632 painting 'The Anatomy Lesson of Dr. Nicolaes Tulp' set? |
| 96875 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which place was served by the Great Western Railway's broad gauge track in 1851? |
| 7549995 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=0.5185;threshold=0.5000;no_social_science_research:population` | Elk |
| 43088 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In which city did Yogi Berra manage a team that lost the 1964 World Series? |
| 156745 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which awards ceremony nominated Julia Roberts for Best Actress for her role in Pretty Woman? |
| 151451 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In which city was the documentary titled 'Orange Rockcorps at the Royal Albert Hall' released in 2008? |
| 599 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which branch of Afroasiatic languages uses 'pínà' as the masculine form of the numeral 'one'? |
| 31730 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=0.8750;threshold=0.5000` | British Armed Forces |
| 26457880 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Where is the headquarters of Air India located? |
| 32005912 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | Where was the 2011 short film featuring Grimes as Saint-Boniface released? |
| 407239 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:word_marker=million;no_social_science_research:survey` | The Indian Express |
| 57877 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | Where is sodium hydroxide typically used for the base-driven hydrolysis of esters, known as saponification? |
| 1064 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=1.0000;threshold=0.5000` | Almond |
| 15049 | `search_longtail` | `search_longtail_verifier_rejected:full_question:answer_in_title` | In which city in Indiana is the radio affiliate with the call sign WFNI located? |
| 80482 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What place served as the residence of Beatrix of the Netherlands and her children before she became queen? |
| 76988 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Where is the V4 electrode positioned in the 12-lead ECG according to Electrocardiography standards? |
| 35412202 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | Where were Wikipedia articles' interlanguage links listed separately before being centralized by Wikidata? |
| 129619 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | At which film awards ceremony did Whoopi Goldberg win the Best Supporting Actress award for the film Ghost? |
| 67923 | `route_generation` | `wikipedia_infobox_table_score_below_minimum:table_score_below_minimum:min_table_score=0.0000;best_score=-0.2000` | East Sussex |
| 23906 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Where was the highest temperature of 39.9 °C (103.8 °F) recorded in the Peterborough area? |
| 1161220 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which constituency did Khushbu Sundar represent in the 2021 Tamil Nadu Legislative Assembly election? |
| 47498 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | In the original Japanese script of Zero Wing, what location is mentioned as being taken over with the help of Federation government forces? |
| 540317 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which terrain mode does the Ford Explorer's Terrain Management System provide optimal driving conditions for sand? |
| 151603 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | Where is the television special 'Dean Martin's Christmas at Seaworld' set? |
| 18947898 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | From which country did the Amnesty International Secretary General who served between 1992 and 2001 originate? |
| 57905 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | Which city in the Sakha Republic has the lowest average daily minimum temperature in January? |
| 1640 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Where was Alfred the Great born around the year 848? |
| 47864412 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In the Nepali language consonant phonemes table, what is the place of articulation for the consonant symbol 'ɡ'? |
| 214179 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | In which city was the American industrial metal band Ministry formed? |
| 57659 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What stadium in Tunis is shared by Club Africain and Espérance Sportive de Tunis? |
| 22461 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | Where is the incidence of hip fractures per 1000 person-years highest among individuals over 64 years old with osteoporosis? |
| 2056103 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What award did Gemini Ganesan receive for his performance in the film Kaaviya Thalaivi? |
| 15240 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_social_science_research:population` | Imam |
| 250230 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What tyre size was fitted on the front and rear wheels of the Mazda RX-7 Series 8 Type RB? |
| 57951 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What was the French name of the department corresponding mostly to the territory of Zeeland? |
| 200129 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=0.7500;threshold=0.5000` | Hair loss |
| 38657800 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What Android version did the original Google Pixel and Pixel XL launch with? |
| 479109 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which graduate program at Southern Methodist University was ranked 34th by U.S. News & World Report? |
| 221478 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which Broadway venue hosted Harvey Fierstein's play 'Casa Valentina'? |
| 241717 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_social_science_research:population` | Clinical trial |
| 52374650 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | King |
| 441357 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the word for Thursday in the Somali language? |
| 356375 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What consonant in the Yoruba language is identified as a rhotic? |
| 22304 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What compound represents osmium in the +5 oxidation state? |
| 1787105 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What is the term for the mating system in animal sexual behaviour where one female mates with multiple males? |
| 56668 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=1.0000;threshold=0.5000` | Apricot |
| 683599 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Where did Hedley Verity take his best bowling figures of 10 wickets for 10 runs in a County Championship innings? |
| 32551521 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | According to FIFA eligibility rules, which national team represents the legal nationality of Denmark? |
| 4595410 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=0.5984;threshold=0.5000;no_social_science_research:census,population` | 1970 United States census |
| 104944 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | What was the type of military action at the Battle of Narva during Charles XII's campaigns? |
| 333199 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which SkyTeam member airline includes the affiliates SAS Connect and SAS Link? |
| 1146123 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | For which work did Colin Hanks receive a Spike Video Game Award for Best Cast? |
| 16801 | `route_generation` | `wikipedia_infobox_table_score_below_minimum:table_score_below_minimum:min_table_score=0.0000;best_score=-0.9500` | Krav Maga |
| 226734 | `search_longtail` | `search_longtail_verifier_rejected:full_question:answer_in_title` | Which Nigerian state was created from the Western Region in 1963? |
| 39776 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | Which protocol in the UDP-based amplification attacks table has a fixed amplification factor in version 1.5.6? |
| 261671 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What was the magnitude of the largest aftershock in April 1990 following the 1989 Loma Prieta earthquake? |
| 695780 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who won the Best Film Editing award for the film Casino (1995)? |
| 167051 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | Which film featured Connie Francis as the singing voice of the character Dori Graham? |
| 83316 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | Which artist achieved a UK Singles Chart number 1 hit with the song "Dandy" written by Ray Davies? |
| 194910 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What award did Steve Earle receive at the 2004 Americana Music Honors & Awards? |
| 719515 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What year was Sony Pictures Television founded? |
| 23809352 | `route_generation` | `wikipedia_infobox_llm_discarded:No date or year information is present in the top-ranked table to support a factual date question.` | Carbon-fiber reinforced polymer |
| 68145 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | What year was The Jazz Singer inducted into the National Film Registry by the National Film Preservation Board? |
| 255380 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What year did Robin Tunney first appear in the TV series "Prison Break"? |
| 931 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What year did Steve Ditko begin penciling issues for The Amazing Spider-Man? |
| 189455 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What year range defines the climate normals for Ulm based on recorded data? |
| 158681 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:word_marker=billion` | Aircraft engine |
| 704720 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What year did Lisa Rinna make her Broadway debut as Roxie Hart in Chicago? |
| 745757 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | What year did SC Heerenveen finish second in the Eredivisie and qualify for the Champions League? |
| 722717 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What year did Michalis Konstantinou begin playing for the Cyprus national football team? |
| 21865 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which neurotransmitter system in the brain originates from the locus coeruleus and regulates anxiety and circadian rhythm? |
| 21637 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_2:answer_in_title` | In what year did England and Wales, Ireland, and the British Empire adopt January 1 as the start of the new year? |
| 63972 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What year marks the end of the period covered by the climate data for Murmansk, including record temperatures, average precipitation, and sunshine hours? |
| 240432 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=0.5208;threshold=0.5000;no_social_science_research:population` | Provinces of Argentina |
| 199446 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_social_science_research:census,population` | Kazakh Soviet Socialist Republic |
| 105945 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What year did the Democratic party receive 81.3% of the vote in Newton, Massachusetts's presidential election? |
| 262135 | `route_generation` | `wikipedia_infobox_llm_discarded:No specific date or year is provided in the table for precooled jet engine / LACE prototype stage.` | Rocket engine |
| 422038 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the highest temperature of 40.8 °C ever recorded in Vigo? |
| 2209490 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the Unicode code point for the Arabic letter 'ḥā ʼ' according to the Romanization of Arabic comparison table? |
| 438269 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What month, day, and year was the first episode of Batman Beyond first released? |
| 42042635 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What year did Kumkum Bhagya win the Star Guild Award for Best Upcoming Drama Series? |
| 107825 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What year range do the climate normals for Newport Beach, California cover? |
| 1069583 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the lesson Dattatreya learned from observing the Moon as one of his 24 teachers from nature? |
| 61795854 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What year was the All India Institutes of Medical Sciences Raebareli established? |
| 51524 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What was the U.S. release date of the film The Pink Panther 2? |
| 155723 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | What year did Debbie Gibson appear in the movie "Mega Shark Versus Giant Octopus"? |
| 1608423 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In NCAA Division II men's team sports, during which season does the sport with the highest number of scholarships per team occur? |
| 368204 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | What year did Faith Evans win the Grammy Award for Best Rap Performance by a Duo or Group for the song "I'll Be Missing You"? |
| 1067134 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What year did Mary-Louise Parker win the Golden Globe Award for Best Performance by a TV Actress in a Musical or Comedy for her role in Weeds (TV series)? |
| 168244 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the f-number value for an aperture value (AV) of 5 in the standard full-stop f-number scale? |
| 615800 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did Cafu score his first international goal for Brazil? |
| 241559 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | How many layers of filling are in the Team USA limited edition Oreo? |
| 20804 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many seats did the Christian Democratic Union (CDU) win in the Magdeburg city council election on 9 June 2024? |
| 17416221 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=1.0000;threshold=0.5000;no_social_science_research:population` | South Africa |
| 9316 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_social_science_research:population` | England |
| 32611 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_10000_rate=0.2885;threshold=0.2000` | Vietnam War |
| 5489 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=0.6667;threshold=0.5000;no_social_science_research:population` | Chile |
| 13277 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=1.0000;threshold=0.5000;no_social_science_research:population` | Holy Roman Empire |
| 738 | `route_generation` | `wikipedia_infobox_llm_discarded:No numeric data available in the top-ranked tables to form a valid Number answer question.` | Albania |
| 14849 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | What is the average high temperature in degrees Fahrenheit for Cairo, Illinois in July? |
| 22093 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | How many National Basketball Association championships have the Chicago Bulls won? |
| 19261 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many days per year does Monaco have an average precipitation of at least 1.0 mm based on 1981–2010 data? |
| 31740 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | What was the number of first-time fall freshmen applicants at the University of Michigan in 2025? |
| 292259 | `route_generation` | `wikipedia_infobox_answer_type_not_allowed:answer_type_not_allowed:Number; allowed=Number` | In what year did Deutsche Welle begin broadcasting in the Persian language? |
| 8083 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | How many Grammy Awards has Dr. Dre won in total? |
| 5488 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=0.6667;threshold=0.5000;no_social_science_research:census,population` | Chad |
| 40010153 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | How many average rainy days occur in Goa during July? |
| 151603 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | How many episodes of The Dean Martin Show featured Dean Martin between 1965 and 1974? |
| 39776 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the amplification factor of the Memcached protocol in UDP amplification attacks used in denial-of-service attacks? |
| 1640 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many years after Alfred the Great's birth was his first child Æthelflæd born? |
| 45367389 | `route_generation` | `wikipedia_infobox_answer_type_not_allowed:answer_type_not_allowed:Number; allowed=Number` | In what year was the twin city agreement between Greater London and Berlin established? |
| 105908 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=0.5000;threshold=0.5000` | Ford Mustang |
| 60382764 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | How many years are listed in the Reiwa era conversion table from Reiwa 1 to Reiwa 8? |
| 66958 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | What was the daily volume percentage of the renminbi in global foreign exchange market turnover in April 2025? |
| 12186 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:gt_3000_rate=0.5000;threshold=0.5000;no_social_science_research:population` | Guinea-Bissau |
| 5643 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_social_science_research:population` | Channel Islands |
| 41853326 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | How many goals did Lionel Messi score for Inter Miami CF in the 2025 MLS season? |
| 217231 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many episodes are in season 7 of Curb Your Enthusiasm? |
| 19653842 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | How many cells make up a jellyfish according to Jack A. Wilson's study of organism-like colonies? |
| 84952 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | How many rounds did Marvelous Marvin Hagler fight in his professional boxing match against Alan Minter on September 27, 1980? |
| 33094374 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:word_marker=billion` | Telecommunications |
| 30292 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | How many phases are identified in the quest structure analysis of The Hobbit? |
| 91195 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | How many singles titles did Roger Federer win at the Wimbledon Championships during the Open Era? |
| 11857 | `route_generation` | `wikipedia_infobox_answer_type_not_allowed:answer_type_not_allowed:Number; allowed=Number` | In which year did George Lucas direct the film titled 'Star Wars: Episode II – Attack of the Clones'? |
| 22948 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | How many sons did Poseidon have with Halia according to the list of offspring and their mothers? |
| 34411 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many days does the Sun spend in the Virgo constellation according to the 1977 IAU boundaries? |
| 199445 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many matches did Wayne Rooney manage at Derby County? |


