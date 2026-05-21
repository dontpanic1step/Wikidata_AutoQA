# Route 3 Streaming Wikipedia Page-ID Walkthrough - 2026-05-20

## Stats

- Run group ID: `wikipedia_stream_fast40_place_no_social_science_2026_05_20`
- Run segment ID: `fresh40_place_no_social_science_2026_05_20`
- Artifact manifest: `D:\Study\AI\My-research\Wikidata_Framework\outputs\run_manifests\wikipedia_stream_fast40_place_no_social_science_2026_05_20.json`
- Mode: `page_id_stream`
- Page source: `table-search`
- Table-search queries: `insource:"wikitable"`
- Attempted page IDs: 41
- Unique attempted page IDs: 40
- Stream state reset at run start: yes
- Auto rerun pool once: yes
- Auto-rerun attempted page IDs: 1
- Accepted QAs: 3
- Rejected QAs/pages: 37
- Transient rerun attempts during run: 1
- Wall-clock runtime: 328.9936s
- DuckDuckGo top K: 5
- Generated search queries per QA: 3
- DuckDuckGo parallel queries: 3
- Minimum Route 3 table score: 0.0
- Route 3 answer_type constraint: `Place`
- Route 3 extra prompt rules: `Ask factual questions, not questions about the findings or conclusions of social science research, such as results derived from census studies.`
- Stream page workers: 4
- Wikipedia concurrency limit: 4
- DuckDuckGo service concurrency limit: 4
- OpenRouter generation/rewrite concurrency limit: 10
- Second-stage concurrency limit: 10
- Page-id bounds: 1 to 80000000
- Stream state: `outputs\wikipedia_stream_fast40_place_no_social_science_2026_05_20_state.json`
- Accepted output: `outputs\wikipedia_stream_fast40_place_no_social_science_2026_05_20_accepted.jsonl`
- Rejected output: `outputs\wikipedia_stream_fast40_place_no_social_science_2026_05_20_rejected.jsonl`
- Domain policy: `domain_and_subdomain_optional_for_page_id_streaming`
- Rerun pool after run: `empty`

### Survival By Layer

| Layer | Entered | Failed | Survived | Layer survival | Cumulative survival |
| --- | ---: | ---: | ---: | ---: | ---: |
| Page-id reservation | 41 | 0 | 41 | 100.0% | 100.0% |
| Unresolved or returned to rerun pool | 41 | 0 | 41 | 100.0% | 100.0% |
| Page extraction, table grading, and QA generation | 41 | 0 | 41 | 100.0% | 100.0% |
| Rewrite and surface validation | 41 | 8 | 33 | 80.5% | 80.5% |
| DuckDuckGo long-tail filtering | 33 | 6 | 27 | 81.8% | 65.8% |
| Second-stage model grading | 27 | 24 | 3 | 11.1% | 7.3% |
| Shared route-aware validation | 3 | 0 | 3 | 100.0% | 7.3% |
| Deduplication | 3 | 0 | 3 | 100.0% | 7.3% |
| Other rejection | 3 | 0 | 3 | 100.0% | 7.3% |

### Failure Reasons

| Stage | Exact reason | Count |
| --- | --- | ---: |
| `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | 24 |
| `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | 8 |
| `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | 4 |
| `search_longtail` | `search_longtail_verifier_error` | 1 |
| `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | 1 |

### Answer Type Stats

| Scope | Answer type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `Place` | 3 | 37 | 40 | 7.5% |

### Reasoning Type Stats

| Scope | Reasoning type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `max` | 1 | 11 | 12 | 8.3% |
| Current Run Records | `ordinal` | 1 | 2 | 3 | 33.3% |
| Current Run Records | `single_fact` | 1 | 24 | 25 | 4.0% |

### Rerun Pool After Run

Rerun pool is empty.

### In-Run Rerun Outcomes

These rows show transient rerun-pool attempts and whether the same page ID later reached a final decision in this invocation.

| Page ID | Rerun attempts | Final outcome | Final reason/question | First transient reason |
| ---: | ---: | --- | --- | --- |
| 45367389 | 1 | `accepted` | Which city was the first to become a twin city of Greater London by year? | `search_longtail_verifier_error` |

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
| `candidate_processing_seconds` | 40 | 590.1816 | 14.7545 | 34.0975 |
| `duckduckgo_search_seconds` | 32 | 169.4727 | 5.2960 | 12.1113 |
| `first_paragraph_extract_seconds` | 40 | 37.6392 | 0.9410 | 3.4452 |
| `llm_question_generation_seconds` | 40 | 225.9052 | 5.6476 | 9.5557 |
| `number_reference_margin_seconds` | 32 | 0.0000 | 0.0000 | 0.0000 |
| `page_fetch_seconds` | 40 | 2.5868 | 0.0647 | 0.2929 |
| `rewrite_seconds` | 40 | 161.1001 | 4.0275 | 9.5663 |
| `second_stage_grading_seconds` | 27 | 259.5356 | 9.6124 | 22.1431 |
| `table_parse_seconds` | 40 | 98.9066 | 2.4727 | 8.7776 |
| `total_generation_seconds` | 40 | 375.4415 | 9.3860 | 18.3950 |
| `total_processing_seconds` | 40 | 590.1816 | 14.7545 | 34.0975 |

## Accepted Candidates

| Page ID | Question | Answer | Source |
| ---: | --- | --- | --- |
| 151603 | Where did Dean Martin portray an unnamed gambler in a 1958 television episode? | Las Vegas | https://en.wikipedia.org/wiki/Dean_Martin |
| 84952 | Where did Marvelous Marvin Hagler have the highest number of professional boxing matches? | Boston Garden, Boston, Massachusetts, U.S. | https://en.wikipedia.org/wiki/Marvelous_Marvin_Hagler |
| 45367389 | Which city was the first to become a twin city of Greater London by year? | Berlin | https://en.wikipedia.org/wiki/Greater_London |

## Second-Stage Filtering Responses

These are the small-model QA responses used by the second-stage filter: `openai/gpt-4.1-mini` and `google/gemini-3-flash-preview`.

| Page ID | Question | Reference answer | openai/gpt-4.1-mini | google/gemini-3-flash-preview |
| ---: | --- | --- | --- | --- |
| 151603 | Where did Dean Martin portray an unnamed gambler in a 1958 television episode? | Las Vegas | INCORRECT; predicted_answer: Dean Martin portrayed an unnamed gambler in a 1958 episode of the television series *The Restless Gun*. | INCORRECT; predicted_answer: Dean Martin portrayed an unnamed gambler in the episode **"The Night the Phone Rang"** of the anthology series **The Danny Thomas Show** (also known as *Make Room for Daddy*), which aired on October 13, 1958. |
| 84952 | Where did Marvelous Marvin Hagler have the highest number of professional boxing matches? | Boston Garden, Boston, Massachusetts, U.S. | INCORRECT; predicted_answer: Marvelous Marvin Hagler had the highest number of professional boxing matches in the United States. | INCORRECT; predicted_answer: Marvelous Marvin Hagler had the highest number of professional boxing matches in **Brockton, Massachusetts**, where he fought 24 times. |
| 45367389 | Which city was the first to become a twin city of Greater London by year? | Berlin | INCORRECT; predicted_answer: The first city to become a twin city of Greater London was New York City, established in 1963. | INCORRECT; predicted_answer: **Berlin**, Germany, was the first city to become a twin city of Greater London, with the partnership established in **1967**. |
| 9316 | What place is linked to the language with the largest number of native speakers in England? | England | not run | not run |
| 22093 | Which team won the first National Basketball Association championship in 1947? | Philadelphia/San Francisco/Golden State Warriors | not run | not run |
| 17416221 | Which province in South Africa has the greatest land area? | Northern Cape | not run | not run |
| 32611 | Which place experienced the highest number of military deaths in a single year during the Vietnam War? | South Vietnam | CORRECT; predicted_answer: The place that experienced the highest number of military deaths in a single year during the Vietnam War was South Vietnam, particularly during the Tet Offensive in 1968. This year saw the peak of combat fatalities for U.S. and allied forces as well as heavy casualties among North Vietnamese and Viet Cong troops. | not run |
| 738 | Which county in Albania has the greatest land area? | Korçë | CORRECT; predicted_answer: The county in Albania with the greatest land area is Korçë County. | not run |
| 13277 | Which state within the Holy Roman Empire had the largest population in Imperial Italy in the early 17th century? | Duchy of Milan | CORRECT; predicted_answer: In the early 17th century, the Duchy of Milan was the state within the Holy Roman Empire with the largest population in Imperial Italy. | not run |
| 5489 | What is the capital of the Chilean region with the greatest area? | Punta Arenas | INCORRECT; predicted_answer: The Chilean region with the greatest area is the Antofagasta Region. Its capital is Antofagasta. | CORRECT; predicted_answer: The capital is **Punta Arenas**, which serves as the administrative center of the Magallanes and Chilean Antarctica Region. |
| 14849 | What place of birth has the largest foreign-born population in Illinois in 2022? | Mexico | CORRECT; predicted_answer: In Illinois in 2022, the place of birth with the largest foreign-born population is Mexico. | not run |
| 19261 | In which month was the highest temperature recorded in Monaco's climate data from 1966 to present? | August | CORRECT; predicted_answer: The highest temperature in Monaco's climate data from 1966 to present was recorded in August. | not run |
| 11857 | Where was the first feature film directed by George Lucas released? | United States | CORRECT; predicted_answer: The first feature film directed by George Lucas, *THX 1138*, was released in the United States. | not run |
| 8083 | What is the setting of the video game 'Grand Theft Auto Online: The Cayo Perico Heist' in which Dr. Dre voiced himself? | Cayo Perico | not run | not run |
| 21355232 | Which U.S. state has the greatest number of national parks according to the List of national parks of the United States? | California | not run | not run |
| 31740 | Where is the University of Michigan located? | Ann Arbor, Michigan | not run | not run |
| 199445 | What was the first team Wayne Rooney managed as a head coach? | Derby County | CORRECT; predicted_answer: Wayne Rooney's first team as a head coach was Derby County. | not run |
| 40010153 | What is the capital place of the state of Goa? | Panaji | not run | not run |
| 292259 | In which place is the German state-funded television network Deutsche Welle based? | Germany | not run | not run |
| 39776 | Which place is linked to the origin of the Mitel MiCollab protocol involved in UDP-based amplification denial-of-service attacks? | Canada | CORRECT; predicted_answer: The place linked to the origin of the Mitel MiCollab protocol involved in UDP-based amplification denial-of-service attacks is **Canada**. | not run |
| 5488 | What city is the capital of Chad? | N'Djamena | CORRECT; predicted_answer: The capital of Chad is N'Djamena. | not run |
| 1640 | Where was Alfred the Great born? | Wantage, Berkshire | CORRECT; predicted_answer: Alfred the Great was born in Wantage, which is in present-day Oxfordshire, England. | not run |
| 41853326 | Where is Inter Miami CF located? | Miami | not run | not run |
| 60382764 | Which place is linked to the Reiwa era that started in 2019? | Japan | CORRECT; predicted_answer: The Reiwa era, which started in 2019, is linked to Japan. | not run |
| 66958 | Which place issues the currency called Renminbi? | People's Republic of China | CORRECT; predicted_answer: The currency called Renminbi is issued by the People's Republic of China. | not run |
| 105908 | In which place were Ford Mustang sales recorded during the 1970 model year? | United States | not run | not run |
| 12186 | What is the most populous city in Guinea-Bissau based on the 2015 estimate? | Bissau | not run | not run |
| 217231 | What city is the primary setting of the television show Curb Your Enthusiasm? | Los Angeles | CORRECT; predicted_answer: The primary setting of the television show *Curb Your Enthusiasm* is Los Angeles. | not run |
| 5643 | Which island has the largest area in the Channel Islands? | Jersey | CORRECT; predicted_answer: Jersey is the island with the largest area in the Channel Islands. | not run |
| 34411 | Which Zodiac constellation has the longest duration of solar stay according to the 1977 IAU boundaries? | Virgo | CORRECT; predicted_answer: According to the 1977 IAU constellation boundaries, the Zodiac constellation with the longest duration of solar stay is **Virgo**. The Sun spends about 44 days in Virgo, longer than in any other Zodiac constellation. | not run |
| 19653842 | What place is cited as an example of a superorganism in Queller and Strassmann's perspective on organisms at different levels of biological organisation? | Ant colony | INCORRECT; predicted_answer: Queller and Strassmann cite a **bee colony** as an example of a superorganism in their perspective on organisms at different levels of biological organization. | CORRECT; predicted_answer: Queller and Strassmann cite **social insect colonies** (such as those of honeybees, ants, and termites) as the primary example of a superorganism. |
| 235916 | In which place was the English dub of the film 'Princess Mononoke' featuring Jada Pinkett Smith's voice role released? | English dub | not run | not run |
| 55440889 | Which place uses the 2G GSM cellular network bands 850, 900, 1800, and 1900 for the Pixel 2? | GSM | not run | not run |
| 22948 | Which place is named after a child of Poseidon? | Rhodos | CORRECT; predicted_answer: The island of Rhodes is named after Rhodos, who was a daughter of Poseidon in Greek mythology. | not run |
| 30292 | What place marks the start of the quest in The Hobbit? | Bag End in the Shire | CORRECT; predicted_answer: The quest in *The Hobbit* starts at Bilbo Baggins' home, Bag End, in the Shire. | not run |
| 33094374 | Which place is linked to the 2007 advertising expenditures data in Telecommunications? | United States | CORRECT; predicted_answer: The place linked to the 2007 advertising expenditures data in Telecommunications is the United States. | not run |
| 2924002 | Where is the DJ Awards, the only global electronic dance music DJ awards event held annually, hosted? | Ibiza | CORRECT; predicted_answer: The DJ Awards is hosted annually in Ibiza, Spain. | not run |
| 260996 | At which venue did Christian Slater appear in the play 'Spamalot'? | The Hollywood Bowl | INCORRECT; predicted_answer: Christian Slater appeared in the play 'Spamalot' at the Palace Theatre in London. | CORRECT; predicted_answer: Christian Slater appeared in *Spamalot* at the **Hollywood Bowl**. |
| 235959 | Where was the play 'Butterflies are Free' performed in which Farrah Fawcett acted? | Jupiter, Florida | INCORRECT; predicted_answer: Farrah Fawcett acted in the play "Butterflies Are Free" at the Huntington Hartford Theater in Los Angeles. | CORRECT; predicted_answer: Farrah Fawcett performed in *Butterflies Are Free* at the **Burt Reynolds Dinner Theatre** in Jupiter, Florida, in 1980. |
| 91195 | Where is the Wimbledon Championships held each year? | Wimbledon, London | CORRECT; predicted_answer: The Wimbledon Championships are held each year at the All England Lawn Tennis and Croquet Club in London, England. | not run |


Rerun-pool entries have no second-stage filtering response unless they reached the panel before the transient failure.

## Rejected And Rerun Decisions

| Page ID | Stage | Exact reason | Page/question |
| ---: | --- | --- | --- |
| 9316 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | What place is linked to the language with the largest number of native speakers in England? |
| 22093 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which team won the first National Basketball Association championship in 1947? |
| 17416221 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which province in South Africa has the greatest land area? |
| 32611 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which place experienced the highest number of military deaths in a single year during the Vietnam War? |
| 738 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which county in Albania has the greatest land area? |
| 13277 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which state within the Holy Roman Empire had the largest population in Imperial Italy in the early 17th century? |
| 5489 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the capital of the Chilean region with the greatest area? |
| 14849 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What place of birth has the largest foreign-born population in Illinois in 2022? |
| 19261 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which month was the highest temperature recorded in Monaco's climate data from 1966 to present? |
| 11857 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Where was the first feature film directed by George Lucas released? |
| 8083 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | What is the setting of the video game 'Grand Theft Auto Online: The Cayo Perico Heist' in which Dr. Dre voiced himself? |
| 21355232 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which U.S. state has the greatest number of national parks according to the List of national parks of the United States? |
| 31740 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | Where is the University of Michigan located? |
| 199445 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What was the first team Wayne Rooney managed as a head coach? |
| 40010153 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | What is the capital place of the state of Goa? |
| 292259 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In which place is the German state-funded television network Deutsche Welle based? |
| 39776 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which place is linked to the origin of the Mitel MiCollab protocol involved in UDP-based amplification denial-of-service attacks? |
| 5488 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What city is the capital of Chad? |
| 1640 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Where was Alfred the Great born? |
| 41853326 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | Where is Inter Miami CF located? |
| 60382764 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which place is linked to the Reiwa era that started in 2019? |
| 66958 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which place issues the currency called Renminbi? |
| 105908 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | In which place were Ford Mustang sales recorded during the 1970 model year? |
| 12186 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | What is the most populous city in Guinea-Bissau based on the 2015 estimate? |
| 217231 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What city is the primary setting of the television show Curb Your Enthusiasm? |
| 5643 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which island has the largest area in the Channel Islands? |
| 34411 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which Zodiac constellation has the longest duration of solar stay according to the 1977 IAU boundaries? |
| 19653842 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What place is cited as an example of a superorganism in Queller and Strassmann's perspective on organisms at different levels of biological organisation? |
| 235916 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | In which place was the English dub of the film 'Princess Mononoke' featuring Jada Pinkett Smith's voice role released? |
| 55440889 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | Which place uses the 2G GSM cellular network bands 850, 900, 1800, and 1900 for the Pixel 2? |
| 22948 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which place is named after a child of Poseidon? |
| 30292 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What place marks the start of the quest in The Hobbit? |
| 33094374 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which place is linked to the 2007 advertising expenditures data in Telecommunications? |
| 2924002 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Where is the DJ Awards, the only global electronic dance music DJ awards event held annually, hosted? |
| 260996 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | At which venue did Christian Slater appear in the play 'Spamalot'? |
| 235959 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Where was the play 'Butterflies are Free' performed in which Farrah Fawcett acted? |
| 91195 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Where is the Wimbledon Championships held each year? |

### Rerun Records

| Page ID | Stage | Exact reason | Page/question |
| ---: | --- | --- | --- |
| 45367389 | `search_longtail` | `search_longtail_verifier_error` | https://en.wikipedia.org/w/index.php?pageid=45367389 |

