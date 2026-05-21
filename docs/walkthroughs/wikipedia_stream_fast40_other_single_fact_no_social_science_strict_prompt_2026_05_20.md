# Route 3 Streaming Wikipedia Page-ID Walkthrough - 2026-05-20

## Stats

- Run group ID: `wikipedia_stream_fast40_other_single_fact_no_social_science_strict_prompt_2026_05_20`
- Run segment ID: `fresh40_other_single_fact_no_social_science_strict_prompt_2026_05_20`
- Artifact manifest: `D:\Study\AI\My-research\Wikidata_Framework\outputs\run_manifests\wikipedia_stream_fast40_other_single_fact_no_social_science_strict_prompt_2026_05_20.json`
- Mode: `page_id_stream`
- Page source: `table-search`
- Table-search queries: `insource:"wikitable"`
- Attempted page IDs: 40
- Unique attempted page IDs: 40
- Stream state reset at run start: yes
- Auto rerun pool once: yes
- Auto-rerun attempted page IDs: 0
- Accepted QAs: 7
- Rejected QAs/pages: 33
- Transient rerun attempts during run: 0
- Wall-clock runtime: 302.8098s
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
- Stream state: `outputs\wikipedia_stream_fast40_other_single_fact_no_social_science_strict_prompt_2026_05_20_state.json`
- Accepted output: `outputs\wikipedia_stream_fast40_other_single_fact_no_social_science_strict_prompt_2026_05_20_accepted.jsonl`
- Rejected output: `outputs\wikipedia_stream_fast40_other_single_fact_no_social_science_strict_prompt_2026_05_20_rejected.jsonl`
- Domain policy: `domain_and_subdomain_optional_for_page_id_streaming`
- Rerun pool after run: `empty`

### Survival By Layer

| Layer | Entered | Failed | Survived | Layer survival | Cumulative survival |
| --- | ---: | ---: | ---: | ---: | ---: |
| Page-id reservation | 40 | 0 | 40 | 100.0% | 100.0% |
| Unresolved or returned to rerun pool | 40 | 0 | 40 | 100.0% | 100.0% |
| Page extraction, table grading, and QA generation | 40 | 4 | 36 | 90.0% | 90.0% |
| Rewrite and surface validation | 36 | 1 | 35 | 97.2% | 87.5% |
| DuckDuckGo long-tail filtering | 35 | 1 | 34 | 97.1% | 85.0% |
| Second-stage model grading | 34 | 27 | 7 | 20.6% | 17.5% |
| Shared route-aware validation | 7 | 0 | 7 | 100.0% | 17.5% |
| Deduplication | 7 | 0 | 7 | 100.0% | 17.5% |
| Other rejection | 7 | 0 | 7 | 100.0% | 17.5% |

### Failure Reasons

| Stage | Exact reason | Count |
| --- | --- | ---: |
| `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | 27 |
| `route_generation` | `wikipedia_infobox_single_fact_list_answer:single_fact_list_answer_not_allowed` | 4 |
| `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | 1 |
| `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | 1 |

### Answer Type Stats

| Scope | Answer type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `Other` | 7 | 29 | 36 | 19.4% |
| Current Run Records | `unknown` | 0 | 4 | 4 | 0.0% |

### Reasoning Type Stats

| Scope | Reasoning type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `single_fact` | 7 | 29 | 36 | 19.4% |
| Current Run Records | `wikipedia_table_fact` | 0 | 4 | 4 | 0.0% |

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
| `candidate_processing_seconds` | 40 | 617.4643 | 15.4366 | 28.3720 |
| `duckduckgo_search_seconds` | 35 | 143.6580 | 4.1045 | 11.6913 |
| `first_paragraph_extract_seconds` | 40 | 41.8702 | 1.0468 | 3.7484 |
| `llm_question_generation_seconds` | 40 | 225.5503 | 5.6388 | 24.0871 |
| `number_reference_margin_seconds` | 35 | 0.0000 | 0.0000 | 0.0000 |
| `page_fetch_seconds` | 40 | 2.8307 | 0.0708 | 0.4623 |
| `rewrite_seconds` | 36 | 124.4416 | 3.4567 | 7.4659 |
| `second_stage_grading_seconds` | 34 | 349.3114 | 10.2739 | 22.7027 |
| `table_parse_seconds` | 40 | 116.3660 | 2.9091 | 9.6511 |
| `total_generation_seconds` | 40 | 397.3659 | 9.9341 | 28.0572 |
| `total_processing_seconds` | 40 | 617.4643 | 15.4366 | 28.3720 |

## Accepted Candidates

| Page ID | Question | Answer | Source |
| ---: | --- | --- | --- |
| 738 | What is the Human Development Index (HDI) value of Vlorë county in Albania according to its administrative divisions? | 0.814 | https://en.wikipedia.org/wiki/Albania |
| 151603 | What role did Dean Martin play in the 1967 television special Movin' with Nancy? | Nancy's Fairy Goduncle | https://en.wikipedia.org/wiki/Dean_Martin |
| 217231 | What bonus features come with the DVD release of Season 5 of Curb Your Enthusiasm? | "The History of Curb ... so far" and "The History of Curb ... even further" featurettes | https://en.wikipedia.org/wiki/Curb_Your_Enthusiasm |
| 235916 | What genre of film is 'Moe's World' in which Jada Pinkett Smith played Natalie? | Television film | https://en.wikipedia.org/wiki/Jada_Pinkett_Smith |
| 2924002 | Which organization organized the only Electronic Dance Music Awards ceremony held in 1995? | Project X Magazine | https://en.wikipedia.org/wiki/Electronic_dance_music |
| 30292 | What event signifies the success of the quest in The Hobbit according to Randel Helms's analysis? | Arrival of Great Eagles | https://en.wikipedia.org/wiki/The_Hobbit |
| 33094374 | Which advertising medium had the highest spending in the US in 2007 related to telecommunications? | Magazine | https://en.wikipedia.org/wiki/Telecommunications |

## Second-Stage Filtering Responses

These are the small-model QA responses used by the second-stage filter: `openai/gpt-4.1-mini` and `google/gemini-3-flash-preview`.

| Page ID | Question | Reference answer | openai/gpt-4.1-mini | google/gemini-3-flash-preview |
| ---: | --- | --- | --- | --- |
| 738 | What is the Human Development Index (HDI) value of Vlorë county in Albania according to its administrative divisions? | 0.814 | INCORRECT; predicted_answer: The Human Development Index (HDI) value of Vlorë County in Albania is approximately 0.796 as of 2021. | INCORRECT; predicted_answer: As of the most recent subnational data (2022), the Human Development Index (HDI) value for **Vlorë County** is **0.781**. |
| 151603 | What role did Dean Martin play in the 1967 television special Movin' with Nancy? | Nancy's Fairy Goduncle | INCORRECT; predicted_answer: Dean Martin appeared as a guest star in the 1967 television special *Movin' with Nancy*. | INCORRECT; predicted_answer: Dean Martin appeared as himself in a guest role, performing the duet "Things" with Nancy Sinatra. |
| 217231 | What bonus features come with the DVD release of Season 5 of Curb Your Enthusiasm? | "The History of Curb ... so far" and "The History of Curb ... even further" featurettes | INCORRECT; predicted_answer: The DVD release of Season 5 of *Curb Your Enthusiasm* includes the following bonus features:  - Deleted Scenes   - Behind-the-Scenes Featurettes   - Cast and Crew Interviews   - Audio Commentaries on Select Episodes    These extras provide additional insights and humorous content related to the season. | INCORRECT; predicted_answer: The DVD release of *Curb Your Enthusiasm* Season 5 includes the following bonus features:  *   **"HBO Comedy Special: The Making of Curb Your Enthusiasm"**: A behind-the-scenes look at the production of the show. *   **"A Conversation with Larry David"**: An interview with the series creator and star conducted by former HBO CEO Chris Albrecht. |
| 235916 | What genre of film is 'Moe's World' in which Jada Pinkett Smith played Natalie? | Television film | INCORRECT; predicted_answer: 'Moe's World,' in which Jada Pinkett Smith played Natalie, is a drama film. | INCORRECT; predicted_answer: *Moe's World* is a **drama** film (specifically a television movie). |
| 2924002 | Which organization organized the only Electronic Dance Music Awards ceremony held in 1995? | Project X Magazine | INCORRECT; predicted_answer: The only Electronic Dance Music Awards ceremony held in 1995 was organized by the International Dance Music Awards (IDMA). | INCORRECT; predicted_answer: The 1995 Electronic Dance Music Awards were organized by **DMA (Dance Music Authority)** magazine. |
| 30292 | What event signifies the success of the quest in The Hobbit according to Randel Helms's analysis? | Arrival of Great Eagles | INCORRECT; predicted_answer: According to Randel Helms's analysis, the success of the quest in *The Hobbit* is signified by Bilbo's acquisition of the Arkenstone. | INCORRECT; predicted_answer: According to Randel Helms in *Tolkien's World*, the success of the quest is signified by **Bilbo’s return to the Shire and his discovery that he has been presumed dead.**  Helms argues that the true "victory" is not the recovery of the gold or the death of Smaug, but Bilbo’s internal transformation. His arrival during the auction of his own belongings represents his "rebirth" as a new person who has successfully integrated his "Tookish" (adventurous) and "Baggins" (stable) sides, achieving a state of psychological wholeness |
| 33094374 | Which advertising medium had the highest spending in the US in 2007 related to telecommunications? | Magazine | INCORRECT; predicted_answer: In 2007, the advertising medium with the highest spending in the US related to telecommunications was Television. | INCORRECT; predicted_answer: **Television** was the advertising medium with the highest spending in the U.S. telecommunications sector in 2007. |
| 17416221 | Which city is the largest in the Eastern Cape province of South Africa? | Port Elizabeth | CORRECT; predicted_answer: The largest city in the Eastern Cape province of South Africa is Port Elizabeth, also known as Gqeberha. | not run |
| 9316 | Which language has the fewest native speakers in the England language table? | Cornish | NOT_ATTEMPTED; predicted_answer: Please provide the England language table you are referring to, so I can identify which language has the fewest native speakers. | CORRECT; predicted_answer: According to the 2021 Census data for England and Wales, the language with the fewest native speakers listed in the main language tables is **Cornish**. |
| 32611 | What was the total US expenditure in South Vietnam from 1953 to 1974 measured in 2015 dollars during the Vietnam War? | $1 trillion | INCORRECT; predicted_answer: The total US expenditure in South Vietnam from 1953 to 1974 during the Vietnam War was approximately $168 billion measured in 2015 dollars. | CORRECT; predicted_answer: The total U.S. expenditure in South Vietnam from 1953 to 1974 was approximately **$1 trillion** when measured in 2015 dollars. |
| 22093 | How many NBA Finals appearances have the Boston Celtics made in the National Basketball Association? | 23 | INCORRECT; predicted_answer: The Boston Celtics have made 22 NBA Finals appearances. | CORRECT; predicted_answer: The Boston Celtics have made **23** NBA Finals appearances. |
| 14849 | What are the top five countries of origin for immigrants in Illinois as of 2018 and 2023? | Mexico; India; Poland; Philippines; China | not run | not run |
| 5489 | What city is the capital of the Libertador General Bernardo O'Higgins region in Chile? | Rancagua | CORRECT; predicted_answer: The capital of the Libertador General Bernardo O'Higgins region in Chile is Rancagua. | not run |
| 13277 | What was the political affiliation of the Duchy of Milan within the Holy Roman Empire in the early 17th century? | Spanish | CORRECT; predicted_answer: In the early 17th century, the Duchy of Milan was politically affiliated with the Spanish Habsburgs and was part of the Spanish Empire, not directly governed by the Holy Roman Empire despite being a nominal Imperial fief. | not run |
| 11857 | What feature film did George Lucas direct in 1973? | American Graffiti | CORRECT; predicted_answer: George Lucas directed the feature film *American Graffiti* in 1973. | not run |
| 19261 | What Köppen climate classification does Monaco have? | hot-summer Mediterranean climate | CORRECT; predicted_answer: Monaco has a Mediterranean climate, classified as Csa in the Köppen climate classification. | not run |
| 31740 | What was the SAT score range for first-time fall freshmen admitted to the University of Michigan in 2023? | 1350–1530 | not run | not run |
| 199445 | Which football club did Wayne Rooney manage from 14 November 2020 to 26 June 2022? | Derby County | CORRECT; predicted_answer: Wayne Rooney managed Derby County from 14 November 2020 to 26 June 2022. | not run |
| 8083 | Which character was voiced by Dr. Dre in the 2005 video game 50 Cent: Bulletproof? | Grizz | INCORRECT; predicted_answer: Dr. Dre voiced the character K Dog in the 2005 video game 50 Cent: Bulletproof. | CORRECT; predicted_answer: Dr. Dre voiced the character **Grizz**, a veteran war hero and arms dealer. |
| 21355232 | What unique ecosystem does the National Park of American Samoa protect? | coral reefs, rainforests, volcanic mountains, and white beaches | CORRECT; predicted_answer: The National Park of American Samoa protects a unique tropical rainforest and coral reef ecosystem found in the South Pacific, preserving rare Samoan rainforest, volcanic islands, and vibrant coral reefs. | not run |
| 292259 | Which languages listed in Deutsche Welle's broadcast languages table have ceased their broadcasts? | German; Hungarian; Sanskrit; Japanese; Danish; Belarusian | not run | not run |
| 39776 | Which fixed software version resolved the Memcached amplification denial-of-service vulnerability? | version 1.5.6 | CORRECT; predicted_answer: The Memcached amplification denial-of-service vulnerability was resolved in **Memcached version 1.5.6**. | not run |
| 40010153 | What is the Köppen climate classification of Goa? | extreme tropical monsoon climate | CORRECT; predicted_answer: The Köppen climate classification of Goa is **Am**, which stands for a tropical monsoon climate. | not run |
| 5488 | In which region of Chad is the city of Abéché located? | Ouaddaï | CORRECT; predicted_answer: The city of Abéché is located in the Ouaddaï region of Chad. | not run |
| 1640 | What religious role did Æthelgifu, a relative of Alfred the Great, hold? | Abbess of Shaftesbury | CORRECT; predicted_answer: Æthelgifu, a relative of Alfred the Great, held the religious role of an abbess. | not run |
| 45367389 | What is the ethnic group category labeled as 'Other' that includes Arab and any other ethnic group in the 2021 Greater London ethnic groups data? | Arab; Any other ethnic group | not run | not run |
| 41853326 | Who was the kit manufacturer for Inter Miami CF starting in the 2026 season? | Lowe's | not run | not run |
| 66958 | What does the formal currency name Renminbi literally translate to? | people's currency | CORRECT; predicted_answer: The formal currency name "Renminbi" (人民币) literally translates to "People's Currency." | not run |
| 60382764 | What was the name of the Japanese era from 810 to 824? | Kōnin | CORRECT; predicted_answer: The Japanese era from 810 to 824 was called the Kōnin era. | not run |
| 105908 | What were the US sales figures for the Ford Mustang in the 1974 model year? | 385,993 | INCORRECT; predicted_answer: The US sales figures for the Ford Mustang in the 1974 model year were approximately 110,000 units. | CORRECT; predicted_answer: Ford sold **385,993** Mustangs in the United States for the 1974 model year. |
| 5643 | What are the names of the uninhabited islets in the Bailiwick of Jersey? | The Minquiers; Écréhous; Les Dirouilles; Les Pierres de Lecq | not run | not run |
| 34411 | What Unicode emoji represents the zodiac sign Leo? | ♌️ | CORRECT; predicted_answer: The Unicode emoji that represents the zodiac sign Leo is ♌ (U+264C). | not run |
| 12186 | Which region is the city of Bubaque located in within Guinea-Bissau? | Bolama | CORRECT; predicted_answer: The city of Bubaque is located in the Bolama Region of Guinea-Bissau. | not run |
| 19653842 | According to Queller and Strassmann's perspective on organisms at different biological organization levels, what organisms compose a lichen? | Organisms of different species | CORRECT; predicted_answer: According to Queller and Strassmann, a lichen is composed of multiple distinct organisms—primarily a fungus and one or more photosynthetic partners (algae or cyanobacteria)—living together in a symbiotic association. | not run |
| 55440889 | Which 2G cellular network standard is supported by the Pixel 2? | GSM | CORRECT; predicted_answer: The Pixel 2 supports the GSM standard for 2G cellular networks. | not run |
| 22948 | Who is the mythological mother of Pegasus and Chrysaor, offspring of Poseidon? | Medusa | CORRECT; predicted_answer: The mythological mother of Pegasus and Chrysaor, offspring of Poseidon, is Medusa. | not run |
| 84952 | What is the title of the 1993 video game featuring Marvelous Marvin Hagler as a playable character? | Boxing Legends of the Ring | CORRECT; predicted_answer: The title of the 1993 video game featuring Marvelous Marvin Hagler as a playable character is **"Boxing Legends of the Ring."** | not run |
| 235959 | Which play written by William Mastrosimone featured Farrah Fawcett as the character Marjorie? | Extremities | CORRECT; predicted_answer: The play written by William Mastrosimone that featured Farrah Fawcett as the character Marjorie is **"Extremities."** | not run |
| 260996 | Which character was portrayed by Christian Slater in the stage production of Spamalot? | Sir Galahad | INCORRECT; predicted_answer: Christian Slater portrayed the character King Arthur in the stage production of Spamalot. | CORRECT; predicted_answer: Christian Slater portrayed **Sir Galahad** in the 2015 Hollywood Bowl production of *Spamalot*. |
| 91195 | What is the record number of mixed doubles titles won during the Amateur Era at the Wimbledon Championships? | 7 | INCORRECT; predicted_answer: The record number of mixed doubles titles won during the Amateur Era at the Wimbledon Championships is 4. | CORRECT; predicted_answer: The record for the most mixed doubles titles won during the Amateur Era at Wimbledon is **7**, held by **Elizabeth Ryan**. She won these titles in 1919, 1921, 1923, 1927, 1928, 1930, and 1932. |


## Rejected And Rerun Decisions

| Page ID | Stage | Exact reason | Page/question |
| ---: | --- | --- | --- |
| 17416221 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which city is the largest in the Eastern Cape province of South Africa? |
| 9316 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which language has the fewest native speakers in the England language table? |
| 32611 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What was the total US expenditure in South Vietnam from 1953 to 1974 measured in 2015 dollars during the Vietnam War? |
| 22093 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many NBA Finals appearances have the Boston Celtics made in the National Basketball Association? |
| 14849 | `route_generation` | `wikipedia_infobox_single_fact_list_answer:single_fact_list_answer_not_allowed` | What are the top five countries of origin for immigrants in Illinois as of 2018 and 2023? |
| 5489 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What city is the capital of the Libertador General Bernardo O'Higgins region in Chile? |
| 13277 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What was the political affiliation of the Duchy of Milan within the Holy Roman Empire in the early 17th century? |
| 11857 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What feature film did George Lucas direct in 1973? |
| 19261 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What Köppen climate classification does Monaco have? |
| 31740 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | What was the SAT score range for first-time fall freshmen admitted to the University of Michigan in 2023? |
| 199445 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which football club did Wayne Rooney manage from 14 November 2020 to 26 June 2022? |
| 8083 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which character was voiced by Dr. Dre in the 2005 video game 50 Cent: Bulletproof? |
| 21355232 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What unique ecosystem does the National Park of American Samoa protect? |
| 292259 | `route_generation` | `wikipedia_infobox_single_fact_list_answer:single_fact_list_answer_not_allowed` | Which languages listed in Deutsche Welle's broadcast languages table have ceased their broadcasts? |
| 39776 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which fixed software version resolved the Memcached amplification denial-of-service vulnerability? |
| 40010153 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the Köppen climate classification of Goa? |
| 5488 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which region of Chad is the city of Abéché located? |
| 1640 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What religious role did Æthelgifu, a relative of Alfred the Great, hold? |
| 45367389 | `route_generation` | `wikipedia_infobox_single_fact_list_answer:single_fact_list_answer_not_allowed` | What is the ethnic group category labeled as 'Other' that includes Arab and any other ethnic group in the 2021 Greater London ethnic groups data? |
| 41853326 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | Who was the kit manufacturer for Inter Miami CF starting in the 2026 season? |
| 66958 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What does the formal currency name Renminbi literally translate to? |
| 60382764 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What was the name of the Japanese era from 810 to 824? |
| 105908 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What were the US sales figures for the Ford Mustang in the 1974 model year? |
| 5643 | `route_generation` | `wikipedia_infobox_single_fact_list_answer:single_fact_list_answer_not_allowed` | What are the names of the uninhabited islets in the Bailiwick of Jersey? |
| 34411 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What Unicode emoji represents the zodiac sign Leo? |
| 12186 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which region is the city of Bubaque located in within Guinea-Bissau? |
| 19653842 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | According to Queller and Strassmann's perspective on organisms at different biological organization levels, what organisms compose a lichen? |
| 55440889 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which 2G cellular network standard is supported by the Pixel 2? |
| 22948 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who is the mythological mother of Pegasus and Chrysaor, offspring of Poseidon? |
| 84952 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the title of the 1993 video game featuring Marvelous Marvin Hagler as a playable character? |
| 235959 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which play written by William Mastrosimone featured Farrah Fawcett as the character Marjorie? |
| 260996 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which character was portrayed by Christian Slater in the stage production of Spamalot? |
| 91195 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the record number of mixed doubles titles won during the Amateur Era at the Wimbledon Championships? |


