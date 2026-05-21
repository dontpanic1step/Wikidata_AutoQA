# Route 3 Streaming Wikipedia Page-ID Walkthrough - 2026-05-19

## Stats

- Run group ID: `wikipedia_stream_fast40_2026_05_19`
- Run segment ID: `wikipedia_stream_fast40_incremental3_2026_05_19`
- Artifact manifest: `outputs\run_manifests\wikipedia_stream_fast40_2026_05_19.json`
- Mode: `page_id_stream`
- Page source: `table-search`
- Table-search queries: `insource:wikitable`
- Endpoint resume: 38 accepted and 140 rejected records loaded
- Existing accepted QAs before run: 38
- Existing rejected QAs/pages before run: 140
- Attempted page IDs: 5
- Accepted QAs: 3
- Accepted QAs after resume: 41
- Rejected QAs/pages: 2
- Rejected QAs/pages after resume: 142
- Transient rerun attempts during run: 0
- Wall-clock runtime: 71.7513s
- DuckDuckGo top K: 5
- Generated search queries per QA: 2
- DuckDuckGo parallel queries: 3
- Minimum Route 3 table score: 0.0
- Stream page workers: 4
- Wikipedia concurrency limit: 4
- DuckDuckGo service concurrency limit: 4
- OpenRouter generation/rewrite concurrency limit: 10
- Second-stage concurrency limit: 10
- Page-id bounds: 1 to 80000000
- Stream state: `outputs\wikipedia_stream_fast40_fresh_2026_05_19_state.json`
- Accepted output: `outputs\wikipedia_stream_fast40_2026_05_19_accepted.jsonl`
- Rejected output: `outputs\wikipedia_stream_fast40_2026_05_19_rejected.jsonl`
- Domain policy: `domain_and_subdomain_optional_for_page_id_streaming`
- Rerun pool after run: `empty`

### Overall Displayed Stats

| Scope | Page IDs/records | Accepted | Rejected | Rerun | Accepted/page rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| Existing endpoint records | 178 | 38 | 140 | 0 | 21.3% |
| Incremental run | 5 | 3 | 2 | 0 | 60.0% |
| Overall displayed | 183 | 41 | 142 | 0 | 22.4% |

### Survival By Layer

| Layer | Entered | Failed | Survived | Layer survival | Cumulative survival |
| --- | ---: | ---: | ---: | ---: | ---: |
| Page-id reservation | 5 | 0 | 5 | 100.0% | 100.0% |
| Unresolved or returned to rerun pool | 5 | 0 | 5 | 100.0% | 100.0% |
| Page extraction, table grading, and QA generation | 5 | 0 | 5 | 100.0% | 100.0% |
| Rewrite and surface validation | 5 | 0 | 5 | 100.0% | 100.0% |
| DuckDuckGo long-tail filtering | 5 | 0 | 5 | 100.0% | 100.0% |
| Second-stage model grading | 5 | 2 | 3 | 60.0% | 60.0% |
| Shared route-aware validation | 3 | 0 | 3 | 100.0% | 60.0% |
| Deduplication | 3 | 0 | 3 | 100.0% | 60.0% |
| Other rejection | 3 | 0 | 3 | 100.0% | 60.0% |

### Failure Reasons

| Stage | Exact reason | Count |
| --- | --- | ---: |
| `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | 2 |

### Rerun Pool After Run

Rerun pool is empty.


### Phase Timings

Timing nesting: `wall_clock_seconds` is the whole run. `total_generation_seconds` contains page fetch/paragraph/table parse/LLM QA generation for one page. `total_processing_seconds` contains rewrite, number margin, DuckDuckGo search, second-stage grading when enabled, shared validation, and dedup checks for one generated candidate. `candidate_processing_seconds` is an alias of `total_processing_seconds`. Child phase totals are useful for bottlenecks, but they should not be added to parent totals.
For incremental walkthroughs, `Incremental run` means only the current segment. `Total displayed run` means the endpoint records loaded at resume plus the current segment.

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

#### Time Stats By Scope

| Scope | Wall-clock seconds | Page IDs/records | Final decision records | Total generation seconds | Avg generation seconds | Total processing seconds | Avg processing seconds | Total second-stage seconds | Avg second-stage seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Incremental run | 71.7513 | 5 | 5 | 51.9910 | 10.3982 | 129.5812 | 25.9162 | 98.1436 | 19.6287 |
| Total displayed run | 2862.7252 | 183 | 183 | 1808.5098 | 9.8826 | 3489.4744 | 19.0682 | 1796.6394 | 15.2258 |

#### Incremental Run Phase Timings

| Phase | Count | Total seconds | Average seconds | Max seconds |
| --- | ---: | ---: | ---: | ---: |
| `candidate_processing_seconds` | 5 | 129.5812 | 25.9162 | 54.0864 |
| `duckduckgo_search_seconds` | 5 | 12.4845 | 2.4969 | 3.7948 |
| `first_paragraph_extract_seconds` | 5 | 4.4206 | 0.8841 | 1.3751 |
| `llm_question_generation_seconds` | 5 | 30.6509 | 6.1302 | 12.8554 |
| `number_reference_margin_seconds` | 5 | 0.0003 | 0.0001 | 0.0002 |
| `page_fetch_seconds` | 5 | 0.7266 | 0.1453 | 0.2972 |
| `rewrite_seconds` | 5 | 18.9373 | 3.7875 | 4.2984 |
| `second_stage_grading_seconds` | 5 | 98.1436 | 19.6287 | 47.5780 |
| `table_parse_seconds` | 5 | 14.5121 | 2.9024 | 4.9610 |
| `total_generation_seconds` | 5 | 51.9910 | 10.3982 | 17.6132 |
| `total_processing_seconds` | 5 | 129.5812 | 25.9162 | 54.0864 |

#### Total Displayed Run Phase Timings

| Phase | Count | Total seconds | Average seconds | Max seconds |
| --- | ---: | ---: | ---: | ---: |
| `candidate_processing_seconds` | 183 | 3489.4744 | 19.0682 | 92.4232 |
| `duckduckgo_search_seconds` | 171 | 913.2937 | 5.3409 | 51.3839 |
| `first_paragraph_extract_seconds` | 180 | 42.4351 | 0.2358 | 1.3751 |
| `llm_question_generation_seconds` | 180 | 993.3308 | 5.5185 | 19.5365 |
| `number_reference_margin_seconds` | 171 | 0.0043 | 0.0000 | 0.0016 |
| `page_fetch_seconds` | 182 | 667.6063 | 3.6682 | 17.2844 |
| `rewrite_seconds` | 180 | 779.2406 | 4.3291 | 33.2139 |
| `second_stage_grading_seconds` | 118 | 1796.6394 | 15.2258 | 47.5780 |
| `table_parse_seconds` | 182 | 90.0698 | 0.4949 | 4.9610 |
| `total_generation_seconds` | 183 | 1808.5098 | 9.8826 | 32.2263 |
| `total_processing_seconds` | 183 | 3489.4744 | 19.0682 | 92.4232 |

## Accepted Candidates

Existing endpoint records are shown first; incremental records are the records appended by this run.

### Existing Endpoint Records

| Page ID | Question | Answer | Source |
| ---: | --- | --- | --- |
| 40010153 | What year saw the highest number of tourist arrivals in Goa? | 2015 | https://en.wikipedia.org/wiki/Goa |
| 39776 | Which protocol has the maximum amplification factor in UDP-based amplification denial-of-service attacks? | Mitel MiCollab | https://en.wikipedia.org/wiki/Denial-of-service_attack |
| 217231 | Which seasons of Curb Your Enthusiasm have a 100% rating on Rotten Tomatoes? | 2; 3; 5 | https://en.wikipedia.org/wiki/Curb_Your_Enthusiasm |
| 235916 | In which films did Jada Pinkett Smith voice the character Gloria? | Madagascar; Madagascar: Escape 2 Africa; Madagascar 3: Europe's Most Wanted; Penguins of Madagascar | https://en.wikipedia.org/wiki/Jada_Pinkett_Smith |
| 569459 | How many subspecies does the white-tailed deer have? | 38 | https://en.wikipedia.org/wiki/White-tailed_deer |
| 105391 | Which studio had the longest average film length among B movies in the 1930s? | MGM | https://en.wikipedia.org/wiki/B_movie |
| 342334 | Which stroke finding can persist for the longest duration according to autopsy? | Mononuclear inflammatory cells; Macrophages | https://en.wikipedia.org/wiki/Autopsy |
| 68761 | Which country published the greatest total number of titles in 2022? | Turkey | https://en.wikipedia.org/wiki/Publishing |
| 246920 | What year did Visa Inc. record its highest net income in million US dollars according to the Finance table? | 2024 | https://en.wikipedia.org/wiki/Visa_Inc. |
| 2114995 | At which site does dextromethorphan (DXM) exhibit the lowest K i binding value range in rats? | SERT Tooltip Serotonin transporter | https://en.wikipedia.org/wiki/Dextromethorphan |
| 96875 | What year did the Great Western Railway carry the greatest number of passengers according to passenger services data? | 1924 | https://en.wikipedia.org/wiki/Great_Western_Railway |
| 1625048 | Which district had the highest population in the Kingdom of Bohemia according to the 1910 language distribution by district? | Budweis | https://en.wikipedia.org/wiki/Kingdom_of_Bohemia |
| 57905 | What year saw the highest number of live births in the Sakha Republic according to vital statistics? | 1985 | https://en.wikipedia.org/wiki/Sakha_Republic |
| 67923 | What was the gross value added in East Sussex in million pounds in 2023? | 11576 | https://en.wikipedia.org/wiki/East_Sussex |
| 1161220 | What percentage of votes did Khushbu Sundar receive in the 2021 Tamil Nadu assembly election for the Thousand Lights constituency? | 28.99 | https://en.wikipedia.org/wiki/Khushbu_Sundar |
| 2056103 | For which film did Gemini Ganesan receive the Tamil Nadu State Film Award for Best Actor in 1970? | Kaaviya Thalaivi | https://en.wikipedia.org/wiki/Gemini_Ganesan |
| 250230 | Which Mazda RX-7 Series 8 model produces the highest maximum power? | Type R | https://en.wikipedia.org/wiki/Mazda_RX-7 |
| 18938412 | What year marks Richard Marx's first appearance in a film or show according to his filmography? | 1980 | https://en.wikipedia.org/wiki/Richard_Marx |
| 67436 | Among pseudoephedrine and related agents, which compound has the lowest EC50 for releasing norepinephrine? | Dextroamphetamine | https://en.wikipedia.org/wiki/Pseudoephedrine |
| 32551521 | Which FIFA national teams represent the legal nationality of the United Kingdom according to FIFA eligibility rules? | Great Britain; England; Northern Ireland; Scotland; Wales; Anguilla; Bermuda; British Virgin Islands; Cayman Islands; Gibraltar; Montserrat; Turks and Caicos Islands | https://en.wikipedia.org/wiki/FIFA_eligibility_rules |
| 31940 | Which breadth claim had the greatest number of states claiming territorial waters in 1960 according to the United Nations Convention on the Law of the Sea? | 12-mile limit | https://en.wikipedia.org/wiki/United_Nations_Convention_on_the_Law_of_the_Sea |
| 15606 | Which Japanese dialect had the lowest intelligibility percentage to students from Tokyo and the Kantō region in 1967? | Himi, Toyama | https://en.wikipedia.org/wiki/Japanese_language |
| 12542 | What song did the Grateful Dead perform live the greatest number of times? | Me and My Uncle | https://en.wikipedia.org/wiki/Grateful_Dead |
| 30217 | What age group had the largest total population in the Turks and Caicos Islands according to the 1 August 2017 estimates? | 35–39 | https://en.wikipedia.org/wiki/Turks_and_Caicos_Islands |
| 384695 | Which program at the University of Illinois Urbana-Champaign has the highest global subject ranking? | Materials Science | https://en.wikipedia.org/wiki/University_of_Illinois_Urbana-Champaign |
| 73199 | Who was the named printer at Cambridge University Press between 1886 and 1916? | Charles Felix Clay | https://en.wikipedia.org/wiki/Cambridge_University_Press |
| 1564433 | Which state had the highest effective literacy rate for Scheduled Castes according to the 2011 census? | Mizoram | https://en.wikipedia.org/wiki/Scheduled_Castes_and_Scheduled_Tribes |
| 52812 | At what temperature in degrees Celsius does Earth's atmosphere at sea level have the highest absolute humidity at 100% relative humidity? | 50 | https://en.wikipedia.org/wiki/Humidity |
| 56636 | What city has been a twin town or sister city of Colombo since 1874? | Biratnagar | https://en.wikipedia.org/wiki/Colombo |
| 164390 | What year did John Hurt receive the BAFTA Special Award? | 2011 | https://en.wikipedia.org/wiki/John_Hurt |
| 28229246 | At which venue did Paul Pogba score his first goal for the international team? | Central Stadium, Gomel, Belarus | https://en.wikipedia.org/wiki/Paul_Pogba |
| 563616 | Which Ubisoft subsidiary was established first? | Ubisoft Reflections | https://en.wikipedia.org/wiki/Ubisoft |
| 101965 | What is the ICD-10 code for Psoriatic arthritis related to Psoriasis? | L40.50 | https://en.wikipedia.org/wiki/Psoriasis |
| 1024289 | What is the amount of earnings before interest and taxes (EBIT) in the example statement of income? | 3355 | https://en.wikipedia.org/wiki/Earnings_before_interest_and_taxes |
| 56494 | How many people of Polish ancestry were among minorities in Bergen on 1 January 2024? | 6755 | https://en.wikipedia.org/wiki/Bergen |
| 227931 | What percentage of protein is found in the original tamarind seed kernel composition? | 7.6% | https://en.wikipedia.org/wiki/Tamarind |
| 22573 | What degrees are required in education to become an otorhinolaryngologist? | Doctor of Medicine; Doctor of Osteopathic Medicine; Bachelor of Medicine, Bachelor of Surgery | https://en.wikipedia.org/wiki/Otorhinolaryngology |
| 963152 | What is the estimated population of Spaniards in Mexico? | 120000000 | https://en.wikipedia.org/wiki/Spaniards |

### Incremental Records

| Page ID | Question | Answer | Source |
| ---: | --- | --- | --- |
| 11423229 | How many White people were recorded in Cheyenne, Wyoming in the 2020 census? | 51728 | https://en.wikipedia.org/wiki/Cheyenne,_Wyoming |
| 75698 | What draw type corresponds to having 5 outs in Texas hold 'em? | One Pair to Two Pair or Trips | https://en.wikipedia.org/wiki/Texas_hold_'em |
| 339183 | What is the traditional Mediterranean wind point name for the compass direction South? | Ostro | https://en.wikipedia.org/wiki/Points_of_the_compass |

## Second-Stage Filtering Responses

These are the small-model QA responses used by the second-stage filter: `openai/gpt-4.1-mini` and `google/gemini-3-flash-preview`.

### Existing Endpoint Records

| Page ID | Question | Reference answer | openai/gpt-4.1-mini | google/gemini-3-flash-preview |
| ---: | --- | --- | --- | --- |
| 40010153 | What year saw the highest number of tourist arrivals in Goa? | 2015 | INCORRECT; predicted_answer: The year 2019 saw the highest number of tourist arrivals in Goa. | INCORRECT; predicted_answer: The year with the highest number of tourist arrivals in Goa was **2019**, with approximately **8.06 million** visitors. |
| 39776 | Which protocol has the maximum amplification factor in UDP-based amplification denial-of-service attacks? | Mitel MiCollab | INCORRECT; predicted_answer: The **Memcached** protocol has the maximum amplification factor in UDP-based amplification denial-of-service (DDoS) attacks. Memcached amplification can reach factors of up to 50,000 times, far exceeding other protocols like DNS or NTP. | INCORRECT; predicted_answer: **Memcached** has the maximum amplification factor, with a potential ratio of up to **51,000:1**. |
| 217231 | Which seasons of Curb Your Enthusiasm have a 100% rating on Rotten Tomatoes? | 2; 3; 5 | INCORRECT; predicted_answer: The seasons of *Curb Your Enthusiasm* with a 100% rating on Rotten Tomatoes are Seasons 1, 3, 4, 5, 7, 8, 9, and 11. | INCORRECT; predicted_answer: Seasons **3, 5, 7, and 10** of *Curb Your Enthusiasm* have a 100% rating on Rotten Tomatoes. |
| 235916 | In which films did Jada Pinkett Smith voice the character Gloria? | Madagascar; Madagascar: Escape 2 Africa; Madagascar 3: Europe's Most Wanted; Penguins of Madagascar | INCORRECT; predicted_answer: Jada Pinkett Smith voiced the character Gloria in the following films:  1. **Madagascar** (2005)   2. **Madagascar: Escape 2 Africa** (2008)   3. **Madagascar 3: Europe's Most Wanted** (2012) | INCORRECT; predicted_answer: Jada Pinkett Smith voiced Gloria the hippopotamus in the following films:  *   **Madagascar** (2005) *   **Madagascar: Escape 2 Africa** (2008) *   **Madagascar 3: Europe's Most Wanted** (2012) *   **Merry Madagascar** (2009) – TV Special *   **Madly Madagascar** (2013) – Short film/Special |
| 569459 | How many subspecies does the white-tailed deer have? | 38 (acceptable range: anything between 37 and 39) | INCORRECT; predicted_answer: The white-tailed deer (Odocoileus virginianus) has about 26 recognized subspecies. | INCORRECT; predicted_answer: There are currently **30 to 38** recognized subspecies of white-tailed deer, depending on the taxonomic authority. Of these, 17 occur in North America. |
| 105391 | Which studio had the longest average film length among B movies in the 1930s? | MGM | INCORRECT; predicted_answer: The studio with the longest average film length among B movies in the 1930s was Columbia Pictures. | INCORRECT; predicted_answer: **Republic Pictures** generally held the longest average film length among B-movie studios in the 1930s, with many of its features and Westerns averaging between **54 and 60 minutes**, often exceeding the shorter 45-to-50-minute runtimes of competitors like Monogram or PRC. |
| 342334 | Which stroke finding can persist for the longest duration according to autopsy? | Mononuclear inflammatory cells; Macrophages | INCORRECT; predicted_answer: The stroke finding that can persist for the longest duration according to autopsy is **hemosiderin-laden macrophages**. These macrophages indicate old hemorrhage and can remain in brain tissue for months to years after the stroke event. | INCORRECT; predicted_answer: According to autopsy findings, the **cystic cavity** (or encephalomalacia) is the stroke finding that persists for the longest duration, often remaining for the rest of the individual's life.  Following a cerebral infarction, the necrotic brain tissue is cleared by macrophages, leaving behind a fluid-filled space surrounded by a glial scar (gliosis). This permanent structural change serves as a "pathological scar" indicating a remote stroke. |
| 68761 | Which country published the greatest total number of titles in 2022? | Turkey | INCORRECT; predicted_answer: To determine which country published the greatest total number of titles in 2022, I need to see the relevant data or image. Please provide the data or image showing the number of titles published by country in 2022. | INCORRECT; predicted_answer: **China** published the greatest total number of titles in 2022. |
| 246920 | What year did Visa Inc. record its highest net income in million US dollars according to the Finance table? | 2024 | INCORRECT; predicted_answer: Visa Inc. recorded its highest net income in the year 2022 according to the Finance table. | INCORRECT; predicted_answer: Visa Inc. recorded its highest net income in **2023**, with a total of **$17,273 million**. |
| 2114995 | At which site does dextromethorphan (DXM) exhibit the lowest K i binding value range in rats? | SERT Tooltip Serotonin transporter | INCORRECT; predicted_answer: Dextromethorphan (DXM) exhibits the lowest K_i binding value range in rats at the **sigma-1 receptor** site. | INCORRECT; predicted_answer: In rats, dextromethorphan (DXM) exhibits its lowest $K_i$ binding value range at the **sigma-1 ($\sigma_1$) receptor**. Typical reported values range from approximately **40 to 200 nM**. |
| 96875 | What year did the Great Western Railway carry the greatest number of passengers according to passenger services data? | 1924 | INCORRECT; predicted_answer: Please provide the passenger services data or an image of it so I can determine the year the Great Western Railway carried the greatest number of passengers. | INCORRECT; predicted_answer: The Great Western Railway carried its greatest number of passengers in **1923**, with a total of **140,540,000** passengers. |
| 1625048 | Which district had the highest population in the Kingdom of Bohemia according to the 1910 language distribution by district? | Budweis | INCORRECT; predicted_answer: According to the 1910 language distribution by district in the Kingdom of Bohemia, the district with the highest population was Prague. | INCORRECT; predicted_answer: According to the 1910 census, the district with the highest population in the Kingdom of Bohemia was **Prague** (Prag), which had a population of **223,741**. |
| 57905 | What year saw the highest number of live births in the Sakha Republic according to vital statistics? | 1985 | INCORRECT; predicted_answer: The year 2014 saw the highest number of live births in the Sakha Republic according to the vital statistics. | INCORRECT; predicted_answer: According to vital statistics, the year with the highest number of live births in the Sakha Republic (Yakutia) was **1986**, with **25,545** births. |
| 67923 | What was the gross value added in East Sussex in million pounds in 2023? | 11576 (acceptable range: anything between 11460 and 11692) | INCORRECT; predicted_answer: The gross value added (GVA) in East Sussex in 2023 was £12,000 million. | INCORRECT; predicted_answer: Official Gross Value Added (GVA) data for 2023 has not yet been released by the Office for National Statistics (ONS). The most recent available data is for **2022**, in which the GVA for East Sussex was **£11,444 million**. |
| 1161220 | What percentage of votes did Khushbu Sundar receive in the 2021 Tamil Nadu assembly election for the Thousand Lights constituency? | 28.99 (acceptable range: anything between 28.7001 and 29.2799) | INCORRECT; predicted_answer: Khushbu Sundar received 39.98% of the votes in the 2021 Tamil Nadu assembly election for the Thousand Lights constituency. | INCORRECT; predicted_answer: Khushbu Sundar received **22.72%** of the votes in the 2021 Tamil Nadu assembly election for the Thousand Lights constituency. |
| 2056103 | For which film did Gemini Ganesan receive the Tamil Nadu State Film Award for Best Actor in 1970? | Kaaviya Thalaivi | INCORRECT; predicted_answer: Gemini Ganesan received the Tamil Nadu State Film Award for Best Actor in 1970 for the film **"Kandan Karunai."** | INCORRECT; predicted_answer: Gemini Ganesan received the Tamil Nadu State Film Award for Best Actor in 1970 for the film **Kaaviya Thalaivan**. |
| 250230 | Which Mazda RX-7 Series 8 model produces the highest maximum power? | Type R | INCORRECT; predicted_answer: The Mazda RX-7 Series 8 model with the highest maximum power is the RX-7 Spirit R Type A, producing up to 276 hp. | INCORRECT; predicted_answer: The **Mazda RX-7 Type RS** and **Type RZ** produce the highest maximum power of the Series 8 models, rated at **280 PS (276 hp / 206 kW)**. |
| 18938412 | What year marks Richard Marx's first appearance in a film or show according to his filmography? | 1980 | INCORRECT; predicted_answer: Richard Marx's first appearance in a film or show according to his filmography is in 1984. | INCORRECT; predicted_answer: According to his filmography, Richard Marx's first appearance was in **1982** in the television film ***Sister, Sister***, where he played the role of a singer. |
| 67436 | Among pseudoephedrine and related agents, which compound has the lowest EC50 for releasing norepinephrine? | Dextroamphetamine | INCORRECT; predicted_answer: Among pseudoephedrine and related agents, **ephedrine** typically has the lowest EC50 for releasing norepinephrine, indicating it is the most potent at inducing norepinephrine release. | INCORRECT; predicted_answer: Among pseudoephedrine and its related phenethylamine stereoisomers, **(+)-ephedrine** (the (1S, 2R) isomer) typically exhibits the lowest EC50 for releasing norepinephrine.  While all four isomers (pseudoephedrine and ephedrine enantiomers) act as norepinephrine releasing agents, (+)-ephedrine is the most potent, followed by (-)-ephedrine. Pseudoephedrine isomers are significantly less potent in their norepinephrine-releasing capacity. |
| 32551521 | Which FIFA national teams represent the legal nationality of the United Kingdom according to FIFA eligibility rules? | Great Britain; England; Northern Ireland; Scotland; Wales; Anguilla; Bermuda; British Virgin Islands; Cayman Islands; Gibraltar; Montserrat; Turks and Caicos Islands | INCORRECT; predicted_answer: The FIFA national teams that represent the legal nationality of the United Kingdom according to FIFA eligibility rules are:  - England - Scotland - Wales - Northern Ireland  Each of these teams represents one of the four constituent countries of the UK, and players eligible for the UK can represent any of these teams based on their specific eligibility criteria. | INCORRECT; predicted_answer: According to FIFA eligibility rules, there is no single "United Kingdom" national team. Instead, the legal nationality of the United Kingdom is represented by four distinct national teams:  1.  **England** (The Football Association) 2.  **Scotland** (Scottish Football Association) 3.  **Wales** (Football Association of Wales) 4.  **Northern Ireland** (Irish Football Association)  Under the **Home Nations agreement**, a player holding British nationality is eligible to represent any of these four associations if they (or a parent or grandparent) were born in the relevant territory, or if |
| 31940 | Which breadth claim had the greatest number of states claiming territorial waters in 1960 according to the United Nations Convention on the Law of the Sea? | 12-mile limit | INCORRECT; predicted_answer: In 1960, the breadth claim of **3 nautical miles** had the greatest number of states claiming territorial waters according to the United Nations Convention on the Law of the Sea. | INCORRECT; predicted_answer: In 1960, the **3-nautical-mile** limit was the breadth claim held by the greatest number of states. |
| 15606 | Which Japanese dialect had the lowest intelligibility percentage to students from Tokyo and the Kantō region in 1967? | Himi, Toyama | INCORRECT; predicted_answer: In 1967, the Japanese dialect with the lowest intelligibility percentage to students from Tokyo and the Kantō region was the **Tsugaru dialect**. | INCORRECT; predicted_answer: The **Tsugaru dialect** (Aomori Prefecture) had the lowest intelligibility percentage, with students from Tokyo and the Kantō region understanding only approximately **12%** of the speech in a 1967 study. |
| 12542 | What song did the Grateful Dead perform live the greatest number of times? | Me and My Uncle | INCORRECT; predicted_answer: The Grateful Dead performed the song "Sugar Magnolia" live the greatest number of times. | INCORRECT; predicted_answer: The Grateful Dead performed **"Playing in the Band"** live more than any other song, with 602 documented performances. |
| 30217 | What age group had the largest total population in the Turks and Caicos Islands according to the 1 August 2017 estimates? | 35–39 | INCORRECT; predicted_answer: The age group 0-14 years had the largest total population in the Turks and Caicos Islands according to the 1 August 2017 estimates. | INCORRECT; predicted_answer: According to the 2017 estimates, the **30–34** age group had the largest total population in the Turks and Caicos Islands. |
| 384695 | Which program at the University of Illinois Urbana-Champaign has the highest global subject ranking? | Materials Science | INCORRECT; predicted_answer: The University of Illinois Urbana-Champaign's program with the highest global subject ranking is its Engineering program. | INCORRECT; predicted_answer: The University of Illinois Urbana-Champaign’s **Library and Information Science** program has the highest global subject ranking, consistently placing **#1 in the world** according to the *QS World University Rankings by Subject*. |
| 73199 | Who was the named printer at Cambridge University Press between 1886 and 1916? | Charles Felix Clay | INCORRECT; predicted_answer: The named printer at Cambridge University Press between 1886 and 1916 was John Clay. | INCORRECT; predicted_answer: The named printer at Cambridge University Press between 1886 and 1916 was **John Clay**. |
| 1564433 | Which state had the highest effective literacy rate for Scheduled Castes according to the 2011 census? | Mizoram | INCORRECT; predicted_answer: According to the 2011 census, Kerala had the highest effective literacy rate for Scheduled Castes. | INCORRECT; predicted_answer: According to the 2011 Census, **Daman and Diu** (a Union Territory) had the highest effective literacy rate for Scheduled Castes at **92.6%**. Among the states, **Mizoram** had the highest rate at **92.4%**. |
| 52812 | At what temperature in degrees Celsius does Earth's atmosphere at sea level have the highest absolute humidity at 100% relative humidity? | 50 (acceptable range: anything between 49 and 51) | INCORRECT; predicted_answer: At 100% relative humidity, the absolute humidity (maximum water vapor content) increases with temperature because warmer air can hold more moisture.  The highest absolute humidity at sea level occurs at the highest temperature. For example, at around 30°C, the saturation vapor pressure is about 42.4 hPa, corresponding to roughly 30 grams of water vapor per cubic meter of air.  In summary:   **The highest absolute humidity at 100% relative humidity at sea level occurs at the highest temperature present, typically around 30–35°C or higher, where the air can hold the maximum amount of water vapor.** | INCORRECT; predicted_answer: Earth's atmosphere has the highest absolute humidity at the **highest possible ambient temperature** recorded at sea level.  Because the water-holding capacity of air increases exponentially with temperature, the maximum absolute humidity occurs at the highest recorded dew point. The world record dew point is approximately **35°C (95°F)**, recorded in Dhahran, Saudi Arabia. At this temperature and 100% relative humidity, the air contains approximately **39.6 grams of water per cubic meter**. |
| 56636 | What city has been a twin town or sister city of Colombo since 1874? | Biratnagar | INCORRECT; predicted_answer: Colombo has been a twin town or sister city with Nuremberg, Germany since 1874. | INCORRECT; predicted_answer: No city has been a sister city of Colombo since 1874. The concept of modern sister cities began in the 20th century, and Colombo's oldest such partnership is with **Saint Petersburg**, Russia, established in 1997. |
| 164390 | What year did John Hurt receive the BAFTA Special Award? | 2011 | INCORRECT; predicted_answer: John Hurt received the BAFTA Special Award in 2013. | INCORRECT; predicted_answer: John Hurt received the BAFTA Special Award (the Outstanding British Contribution to Cinema Award) in **2012**. |
| 28229246 | At which venue did Paul Pogba score his first goal for the international team? | Central Stadium, Gomel, Belarus | INCORRECT; predicted_answer: Paul Pogba scored his first goal for the France international team at the Stade de France. | INCORRECT; predicted_answer: Paul Pogba scored his first international goal for France at the **Stade de France** in Saint-Denis. It occurred on March 22, 2013, during a World Cup qualifying match against Georgia. |
| 563616 | Which Ubisoft subsidiary was established first? | Ubisoft Reflections | INCORRECT; predicted_answer: The first Ubisoft subsidiary established was **Ubisoft Montreal**, founded in 1997. | INCORRECT; predicted_answer: **Ubisoft Paris** (originally established simply as Ubisoft) was the first subsidiary, founded in **1986**. |
| 101965 | What is the ICD-10 code for Psoriatic arthritis related to Psoriasis? | L40.50 | INCORRECT; predicted_answer: The ICD-10 code for Psoriatic arthritis related to Psoriasis is **L40.5**. | INCORRECT; predicted_answer: The primary ICD-10 code for psoriatic arthritis is **L40.50** (Arthropathic psoriasis, unspecified).  Depending on the specific presentation, more specific codes include: *   **L40.51:** Distal interphalangeal psoriatic arthropathy *   **L40.52:** Psoriatic arthritis mutilans *   **L40.53:** Psoriatic spondylitis *   **L40.59:** Other psoriatic arthropathy |
| 1024289 | What is the amount of earnings before interest and taxes (EBIT) in the example statement of income? | 3355 (acceptable range: anything between 3321 and 3389) | NOT_ATTEMPTED; predicted_answer: Please provide the example statement of income or an image of it so I can identify the EBIT amount. | NOT_ATTEMPTED; predicted_answer: To provide the specific amount, please provide the image or text of the "example statement of income" you are referring to.  In a standard income statement, **EBIT** is calculated as: **Revenue - Cost of Goods Sold (COGS) - Operating Expenses.** |
| 56494 | How many people of Polish ancestry were among minorities in Bergen on 1 January 2024? | 6755 (acceptable range: anything between 6687 and 6823) | INCORRECT; predicted_answer: On 1 January 2024, there were 2,276 people of Polish ancestry among the minorities in Bergen. | INCORRECT; predicted_answer: As of 1 January 2024, there were **11,147** people of Polish ancestry (immigrants and Norwegian-born to immigrant parents) living in Bergen. They remain the largest minority group in the municipality. |
| 227931 | What percentage of protein is found in the original tamarind seed kernel composition? | 7.6% | INCORRECT; predicted_answer: The original tamarind seed kernel composition contains approximately 17-30% protein. | INCORRECT; predicted_answer: The original tamarind seed kernel typically contains between **17% and 20%** protein. |
| 22573 | What degrees are required in education to become an otorhinolaryngologist? | Doctor of Medicine; Doctor of Osteopathic Medicine; Bachelor of Medicine, Bachelor of Surgery | INCORRECT; predicted_answer: To become an otorhinolaryngologist (ENT specialist), you typically need:  1. A bachelor's degree (pre-medical or related field) 2. A medical degree (MD or DO) 3. Completion of a residency program in otorhinolaryngology (ENT)  Additional fellowship training may be pursued for subspecialties. | INCORRECT; predicted_answer: To become an otorhinolaryngologist (ENT doctor), you must complete the following educational steps:  1.  **Bachelor’s Degree:** A four-year undergraduate degree (typically in a science-related field). 2.  **Medical Degree:** A four-year degree from an accredited medical school (either a **Doctor of Medicine [MD]** or a **Doctor of Osteopathic Medicine [DO]**). 3.  **Residency:** A five-year **Residency in Otolaryngology**, which includes one year of general surgery training and four years of specialized ENT training. |
| 963152 | What is the estimated population of Spaniards in Mexico? | 120000000 (acceptable range: anything between 118800000 and 121200000) | INCORRECT; predicted_answer: The estimated population of Spaniards living in Mexico is around 20,000 to 30,000 people. | INCORRECT; predicted_answer: According to the 2020 Census by INEGI, there are approximately **144,553** Spanish citizens living in Mexico. However, data from Spain’s Register of Spaniards Resident Abroad (PERE) estimates the number to be higher, at approximately **155,000 to 160,000** individuals. |
| 32611 | What year saw the highest number of military deaths for South Vietnam during the Vietnam War from 1955 to 1975? | 1972 | INCORRECT; predicted_answer: The year with the highest number of military deaths for South Vietnam during the Vietnam War was 1968. | CORRECT; predicted_answer: The year with the highest number of military deaths for South Vietnam (ARVN) was **1972**, during which approximately 39,587 soldiers were killed, largely due to the North Vietnamese Easter Offensive. |
| 17416221 | Which province in South Africa had the largest population in 2022? | Gauteng | not run | not run |
| 9316 | What language has the second highest number of native speakers in England? | Polish | not run | not run |
| 22093 | Which National Basketball Association team has the arena with the largest seating capacity? | Chicago Bulls | INCORRECT; predicted_answer: The New York Knicks play in Madison Square Garden, which has the largest seating capacity of any NBA arena. | CORRECT; predicted_answer: The **Chicago Bulls** play at the United Center, which has the largest seating capacity in the NBA at **20,917**. |
| 5489 | Which administrative region of Chile has the largest population? | Santiago Metropolitan | CORRECT; predicted_answer: The Santiago Metropolitan Region (Región Metropolitana de Santiago) has the largest population in Chile. | CORRECT; predicted_answer: The **Santiago Metropolitan Region** (Región Metropolitana de Santiago) has the largest population in Chile. |
| 738 | Which county in Albania had the largest population in 2023? | Tirana | not run | not run |
| 13277 | Which state had the largest population in the Holy Roman Empire during early 17th century Imperial Italy? | Duchy of Milan | CORRECT; predicted_answer: In early 17th century Imperial Italy, the state with the largest population within the Holy Roman Empire was the Duchy of Milan. | CORRECT; predicted_answer: The **Duchy of Milan** had the largest population in Imperial Italy during the early 17th century, with approximately 1.1 to 1.2 million inhabitants. |
| 14849 | Which ancestry group had the largest population alone or in any combination in Illinois in 2022? | German | CORRECT; predicted_answer: The ancestry group with the largest population alone or in any combination in Illinois in 2022 was German. | CORRECT; predicted_answer: According to the U.S. Census Bureau's 2022 American Community Survey (ACS) 1-year estimates, **German** was the largest ancestry group in Illinois (alone or in any combination), with approximately 2.1 million people. |
| 19261 | Which ward in Monaco has the largest area measured in hectares? | Monte-Carlo | not run | not run |
| 11857 | What is the title of the 1977 feature film directed by George Lucas? | Star Wars | not run | not run |
| 199445 | During which season did Wayne Rooney score the highest number of total goals for Manchester United? | 2009–10 | not run | not run |
| 21355232 | Which U.S. state has the greatest number of national parks according to the List of national parks of the United States? | California | not run | not run |
| 31740 | Which academic year between 2013 and 2026 had the highest total enrollment at the University of Michigan-Ann Arbor? | 2025-2026 | not run | not run |
| 8083 | Which work earned Dr. Dre the Grammy Award for Best Rap Solo Performance? | Let Me Ride | not run | not run |
| 292259 | What language started broadcasting on Deutsche Welle in 1953? | German | not run | not run |
| 5488 | Which province of Chad had the highest population on 1 July 2023? | N'Djamena | CORRECT; predicted_answer: On 1 July 2023, the province of Chad with the highest population was N'Djamena. | CORRECT; predicted_answer: The province of Chad with the highest population on 1 July 2023 was **N'Djamena** (the capital city province). |
| 1640 | On what day, month, and year did Alfred the Great die? | 899 | not run | not run |
| 151603 | Which television program had the highest number of episodes featuring Dean Martin? | The Dean Martin Show | not run | not run |
| 66958 | Which currency had the largest share of daily volume in the global foreign exchange market turnover in April 2025? | U.S. dollar | not run | not run |
| 41853326 | Who was the top goalscorer for Inter Miami CF in the 2025 MLS season? | Lionel Messi | not run | not run |
| 60382764 | What year is Reiwa 5 in the Japanese calendar? | 2023 | CORRECT; predicted_answer: Reiwa 5 corresponds to the year 2023 in the Gregorian calendar. | CORRECT; predicted_answer: Reiwa 5 is **2023**. |
| 45367389 | What country of birth had the second largest population in Greater London according to the 2021 United Kingdom Census? | India | CORRECT; predicted_answer: According to the 2021 United Kingdom Census, the country of birth with the second largest population in Greater London was India. | CORRECT; predicted_answer: According to the 2021 Census, **India** was the country of birth with the second largest population in Greater London (after the United Kingdom). |
| 105908 | Which model year of the Ford Mustang had the highest US sales during the 1970s? | 1974 | INCORRECT; predicted_answer: The 1970 Ford Mustang had the highest US sales during the 1970s. | CORRECT; predicted_answer: The **1974** Ford Mustang (the debut year of the Mustang II) had the highest U.S. sales of the 1970s, with approximately **385,993** units sold. |
| 34411 | What is the Latin name of the zodiac sign whose ecliptic longitude begins at 150°? | Virgo | INCORRECT; predicted_answer: The zodiac sign whose ecliptic longitude begins at 150° is Libra. Its Latin name is **Libra**. | CORRECT; predicted_answer: **Virgo** |
| 12186 | What city in Guinea-Bissau had the largest population according to the 2015 estimate? | Bissau | not run | not run |
| 5643 | Which island in the Channel Islands has the greatest population? | Jersey | not run | not run |
| 19653842 | What example is provided for the biological organisation level called 'Swarming protistan'? | Dictyostelium | CORRECT; predicted_answer: The example provided for the biological organisation level called "Swarming protistan" is *Dictyostelium discoideum*. | INCORRECT; predicted_answer: The example provided for a swarming protistan is **slime molds**. |
| 22948 | Which child of Poseidon has Amphitrite as their mother? | Triton | not run | not run |
| 55440889 | What cellular network generation supported by Pixel 2 uses the LTE-FDD standard? | 4G | CORRECT; predicted_answer: The Pixel 2 supports 4G LTE networks, and the LTE-FDD (Frequency Division Duplex) standard is used in 4G LTE. Therefore, the Pixel 2 uses LTE-FDD as part of its 4G LTE cellular network generation. | CORRECT; predicted_answer: The Pixel 2 supports the **4G** (Fourth Generation) cellular network generation using the LTE-FDD standard. |
| 84952 | Who was Marvelous Marvin Hagler's opponent in his final professional boxing match? | Sugar Ray Leonard | not run | not run |
| 2924002 | Who won the BRIT Awards British Dance Act in 2025? | Charli XCX | not run | not run |
| 30292 | What is the name of the place where the quest begins in The Hobbit? | Bag End in the Shire | INCORRECT; predicted_answer: The quest in The Hobbit begins in Hobbiton. | CORRECT; predicted_answer: The quest begins at **Bag End**, the hobbit-hole of Bilbo Baggins in **Hobbiton**. |
| 260996 | What year did Christian Slater act in the stage play Macbeth? | 1982 | not run | not run |
| 235959 | During which years did Farrah Fawcett play Jill Munroe in the television series "Charlie's Angels"? | 1976-1980 | INCORRECT; predicted_answer: Farrah Fawcett played Jill Munroe in "Charlie's Angels" from 1976 to 1977. | CORRECT; predicted_answer: Farrah Fawcett played Jill Munroe as a series regular from **1976 to 1977** (Season 1). She later returned for guest appearances between **1978 and 1980**. |
| 91195 | Who holds the record as the oldest singles champion at the Wimbledon Championships and what was their age at the time? | Arthur Gore | not run | not run |
| 17278765 | Which school has the highest number of College football national championships in NCAA Division I FBS during the poll era from 1936 to present? | Alabama | CORRECT; predicted_answer: The University of Alabama has the highest number of College football national championships in NCAA Division I FBS during the poll era from 1936 to present. | CORRECT; predicted_answer: The **University of Alabama** holds the record for the most national championships in the poll era (1936–present) with **13** titles. |
| 229275 | Which country produced the most lamb and mutton in 2012? | China | CORRECT; predicted_answer: In 2012, China produced the most lamb and mutton. | CORRECT; predicted_answer: **China** produced the most lamb and mutton in 2012. |
| 156745 | Who won the Golden Globe Award for Best Actress in a Motion Picture – Musical or Comedy for Pretty Woman? | Julia Roberts | not run | not run |
| 599 | Which Afroasiatic language uses the prefix conjugation form 'a-parras' for the first person singular? | Akkadian | INCORRECT; predicted_answer: The Afroasiatic language that uses the prefix conjugation form "a-parras" for the first person singular is **Tigrinya**. | CORRECT; predicted_answer: **Akkadian** (specifically in the G-stem present/durative tense). |
| 151451 | What is the title of the 2017 documentary that features Busta Rhymes? | Can't Stop, Won't Stop: A Bad Boy Story | INCORRECT; predicted_answer: The 2017 documentary that features Busta Rhymes is titled **"Busta Rhymes: The Coming."** | CORRECT; predicted_answer: The 2017 documentary featuring Busta Rhymes is titled **Can't Stop Won't Stop: A Bad Boy Story**. |
| 7549995 | Which U.S. state has the largest estimated population of elk? | Colorado | not run | not run |
| 43088 | What year did Yogi Berra achieve his highest regular season winning percentage as a manager? | 1964 | CORRECT; predicted_answer: Yogi Berra achieved his highest regular season winning percentage as a manager in 1964. | CORRECT; predicted_answer: Yogi Berra achieved his highest regular season winning percentage as a manager in **1964**, when he led the New York Yankees to a **.611** winning percentage (99–63). |
| 47864412 | Which Indian state had the highest number of Nepali language speakers according to the 2011 census? | West Bengal | CORRECT; predicted_answer: According to the 2011 census, West Bengal had the highest number of Nepali language speakers among Indian states. | CORRECT; predicted_answer: According to the 2011 Census, **West Bengal** had the highest number of Nepali language speakers in India. |
| 26457880 | What year did Air India record the highest number of passengers in millions according to the business trends data? | 2023-2024 | INCORRECT; predicted_answer: Air India recorded the highest number of passengers in the year 2019 according to the business trends data. | CORRECT; predicted_answer: According to Air India's business trends data, the airline recorded its highest number of passengers in **2023**, carrying **25.6 million** passengers. |
| 31730 | Which branch of the British Armed Forces has the largest total number of personnel? | Army and Gurkhas | CORRECT; predicted_answer: The British Army has the largest total number of personnel among the branches of the British Armed Forces. | CORRECT; predicted_answer: The **British Army** is the largest branch of the British Armed Forces by total number of personnel. |
| 18947898 | Who served as Secretary General of Amnesty International from 1992 to 2001? | Pierre Sané | not run | not run |
| 80482 | Who was the Prime Minister with the longest continuous term during the reign of Beatrix of the Netherlands? | Ruud Lubbers | not run | not run |
| 32005912 | What year did Grimes serve as a judge on the television series Alter Ego? | 2021 | CORRECT; predicted_answer: Grimes served as a judge on the television series Alter Ego in 2021. | CORRECT; predicted_answer: Grimes served as a judge on *Alter Ego* in **2021**. |
| 214179 | Which additional or touring musicians contributed to Ministry (band)'s 1989 release 'The Mind Is a Terrible Thing to Taste'? | Jeff Ward; Chris Connelly | INCORRECT; predicted_answer: The additional or touring musicians who contributed to Ministry's 1989 album *The Mind Is a Terrible Thing to Taste* were:  - Paul Barker (bass, programming, production) - Bill Rieflin (drums, programming) - Chris Connelly (vocals) - Nivek Ogre (vocals) - William Tucker (guitar) - Martin Atkins (drums)  These musicians supported the core members Al Jourgensen and Paul Barker on the album. | CORRECT; predicted_answer: The following musicians contributed to the studio recording or the subsequent tour for *The Mind Is a Terrible Thing to Taste*:  **Studio Personnel (Additional Musicians):** *   **Chris Connelly:** Vocals *   **William Rieflin:** Drums, programming *   **Mars Williams:** Saxophone *   **The Grand Wizard (K. J. Knight):** Backing vocals *   **Bobby DiBartollo:** Backing vocals *   **Angela Lukic:** Backing vocals  **Touring Musicians (1989–1990):** *   **Chris |
| 57877 | What is the molar concentration of sodium hydroxide when its mass fraction is 30 wt%? | 9.95 (acceptable range: anything between 9.8505 and 10.0495) | CORRECT; predicted_answer: To find the molar concentration (molarity, \( C \)) of sodium hydroxide (NaOH) solution with a 30 wt% mass fraction, follow these steps:  1. **Assume 1 liter of solution** for convenience.  2. **Find the density of 30 wt% NaOH solution.**      Typical density of 30 wt% NaOH is about **1.33 g/mL** (or 1330 g/L).  3. **Calculate the mass of NaOH in 1 L solution:**      \[    \text{mass of NaOH} = 0. | CORRECT; predicted_answer: To calculate the molar concentration (molarity) of 30 wt% sodium hydroxide (NaOH), you must account for the density of the solution, which is approximately **1.328 g/mL** at 20°C.  **Calculation:** 1.  **Density ($\rho$):** $1328 \text{ g/L}$ 2.  **Mass Fraction ($w$):** $0.30$ 3.  **Molar Mass of NaOH ($M$):** $\approx 40.00 \text{ g/mol |
| 407239 | Which city has the highest approximate daily circulation of The Indian Express? | Mumbai | not run | not run |
| 57659 | Which suburb of Tunis had the highest population in 2004? | Ettadhamen-Mnihla | INCORRECT; predicted_answer: The suburb of Tunis with the highest population in 2004 was El Mourouj. | CORRECT; predicted_answer: **Ettadhamen-Mnihla** had the highest population of any suburb in the Tunis governorate in 2004, with 118,487 residents. |
| 76988 | What time-frequency analysis method in electrocardiography is suitable for fully non-stationary and nonlinear signals and provides instantaneous frequency distribution? | Hilbert–Huang transform | CORRECT; predicted_answer: The Hilbert-Huang Transform (HHT) is suitable for fully non-stationary and nonlinear electrocardiographic signals and provides an instantaneous frequency distribution. | CORRECT; predicted_answer: The **Hilbert-Huang Transform (HHT)** is the most suitable method for fully non-stationary and nonlinear signals, as it provides an adaptive instantaneous frequency distribution through Empirical Mode Decomposition (EMD) and Hilbert Spectral Analysis. |
| 15049 | In what year was Tony Dungy inducted into the Indianapolis Colts Ring of Honor? | 2010 | not run | not run |
| 1064 | Which country was the largest producer of almonds in 2023 measured in tonnes? | United States | not run | not run |
| 35412202 | What day, month, and year did Wikidata launch? | 2012-10-29 | CORRECT; predicted_answer: Wikidata launched on October 29, 2012. | CORRECT; predicted_answer: Wikidata launched on **October 29, 2012**. |
| 2209490 | Which Arabic letter corresponds to the Unicode value 062C and is called 'jīm' in the Romanization of Arabic? | ج | not run | not run |
| 129619 | Who won the Best Supporting Actress award for the film Ghost (1990)? | Whoopi Goldberg | not run | not run |
| 23906 | What was the population of Peterborough in 2021? | 215700 (acceptable range: anything between 213543 and 217857) | INCORRECT; predicted_answer: The population of Peterborough in 2021 was approximately 121,000. | CORRECT; predicted_answer: According to the 2021 Census, the population of Peterborough was **215,700**. |
| 422038 | Which country had the largest foreign-born population in Vigo in 2024? | Venezuela | CORRECT; predicted_answer: In 2024, the country with the largest foreign-born population in Vigo was Venezuela. | CORRECT; predicted_answer: As of 2024, **Venezuela** has the largest foreign-born population in Vigo, Spain. |
| 540317 | What calendar year saw the highest US sales for the Ford Explorer? | 2000 | INCORRECT; predicted_answer: The highest US sales for the Ford Explorer occurred in the calendar year 1997. | CORRECT; predicted_answer: The Ford Explorer saw its highest U.S. sales in the calendar year **2000**, with **445,157** units sold. |
| 47498 | What English phrase from the 1991 version of Zero Wing became an internet meme? | All your base are belong to us | not run | not run |
| 113933 | Which employer had the largest number of employees in Iowa City according to the top employers list? | University of Iowa Hospitals & Clinics | INCORRECT; predicted_answer: The University of Iowa had the largest number of employees in Iowa City according to the top employers list. | CORRECT; predicted_answer: The **University of Iowa** (including the University of Iowa Hospitals & Clinics) is the largest employer in Iowa City. |
| 22461 | Which WHO category has the highest rate of hip fractures per 1000 person-years? | Osteoporosis | not run | not run |
| 57951 | Which province of the European Netherlands had the largest population on 1 January 2023? | South Holland | not run | not run |
| 261671 | What was the magnitude of the largest aftershock following the 1989 Loma Prieta earthquake? | 5.4 (acceptable range: anything between 5.346 and 5.454) | INCORRECT; predicted_answer: The largest aftershock following the 1989 Loma Prieta earthquake had a magnitude of 6.5. | CORRECT; predicted_answer: The largest aftershock following the 1989 Loma Prieta earthquake had a magnitude of **5.4**. It occurred 37 minutes after the main shock. |
| 15240 | Who is recognized as the first imam and successor of Muhammad in Shia Islam according to Twelver doctrine? | Ali ibn Abi Talib | CORRECT; predicted_answer: According to Twelver Shia Islam, Ali ibn Abi Talib is recognized as the first imam and the rightful successor of Muhammad. | not run |
| 695780 | Who won the Golden Globe Award for Best Actress in a Motion Picture – Drama for Casino (1995 film)? | Sharon Stone | INCORRECT; predicted_answer: Sharon Stone was nominated for the Golden Globe Award for Best Actress in a Motion Picture – Drama for Casino (1995), but she did not win. The winner that year (1996 ceremony) was Emma Thompson for "Sense and Sensibility." | CORRECT; predicted_answer: **Sharon Stone** won the Golden Globe Award for Best Actress in a Motion Picture – Drama for her role in *Casino*. |
| 38657800 | What was the first Google Pixel phone model announced? | Pixel / XL | CORRECT; predicted_answer: The first Google Pixel phone model announced was the Google Pixel, unveiled in October 2016. | not run |
| 200129 | Which gene is linked to the LAH2 type of hair loss? | LIPH | not run | not run |
| 479109 | What race or ethnicity group makes up the largest percentage of the student body at Southern Methodist University as of May 2, 2022? | White | not run | not run |
| 441357 | What is the word for Friday in the Somali language? | Jimce; Jimco | CORRECT; predicted_answer: The word for Friday in the Somali language is "Jimco." | not run |
| 356375 | In which countries is the Yoruba language native? | Benin; Nigeria; Togo | not run | not run |
| 221478 | What year did Harvey Fierstein appear on the television show "The Simpsons"? | 1990 | INCORRECT; predicted_answer: Harvey Fierstein appeared on "The Simpsons" in the year 1996. | CORRECT; predicted_answer: Harvey Fierstein appeared on *The Simpsons* in **1990**. He voiced the character Karl in the episode "Simpson and Delilah." |
| 86224 | What was the venue with the largest capacity at the 1928 Summer Olympics? | Olympic Stadium | not run | not run |
| 167051 | What year did Connie Francis appear in the film "Where the Boys Are"? | 1960 | not run | not run |
| 241717 | Which phase of clinical trials usually tests the largest number of participants? | Phase III | CORRECT; predicted_answer: Phase 3 clinical trials usually test the largest number of participants. | not run |
| 22304 | What is the maximum oxidation state of osmium? | +8 | CORRECT; predicted_answer: The maximum oxidation state of osmium is +8. | not run |
| 180763 | https://en.wikipedia.org/w/index.php?pageid=180763 |  | not run | not run |
| 1787105 | What are the four basic mating systems defined by the number of males and females involved in animal sexual behaviour? | Monogamy; Polygyny; Polyandry; Polygynandry | INCORRECT; predicted_answer: The four basic mating systems are:  1. **Monogamy** – one male mates with one female. 2. **Polygyny** – one male mates with multiple females. 3. **Polyandry** – one female mates with multiple males. 4. **Promiscuity** – multiple males mate with multiple females without exclusive bonds. | CORRECT; predicted_answer: The four basic mating systems are:  1.  **Monogamy:** One male and one female. 2.  **Polygyny:** One male and multiple females. 3.  **Polyandry:** One female and multiple males. 4.  **Polygynandry (or Promiscuity):** Multiple males and multiple females. |
| 683599 | Who achieved the best bowling figures in an innings in the County Championship with 10 wickets for 10 runs? | Hedley Verity | INCORRECT; predicted_answer: George Lohmann achieved the best bowling figures in an innings in the County Championship with 10 wickets for 10 runs. | CORRECT; predicted_answer: **Hedley Verity** achieved these figures for Yorkshire against Nottinghamshire at Headingley in 1932. |
| 56668 | Which country was the largest producer of apricots in 2023 measured in tonnes? | Turkey | not run | not run |
| 104944 | What was the result of the Battle of Poltava on 8 July 1709 in the campaigns of Charles XII of Sweden? | Defeat | not run | not run |
| 333199 | Which former member affiliate of full members left SkyTeam last? | Austral Líneas Aéreas | not run | not run |
| 4595410 | Which state had the highest population according to the 1970 United States census? | California | not run | not run |
| 1069583 | Who are the parents of Dattatreya? | Atri and Anasuya | not run | not run |
| 194910 | What year did Steve Earle receive the Spirit of Americana/Free Speech Award? | 2004 | not run | not run |
| 107825 | Which employer had the largest number of employees in Newport Beach, California? | Hoag Memorial Hospital Presbyterian | CORRECT; predicted_answer: The employer with the largest number of employees in Newport Beach, California, is Hoag Memorial Hospital Presbyterian. | not run |
| 42042635 | Who received the Best Actress in Negative Role (Popular) award at the 11th Keshking Gold Awards for Kumkum Bhagya? | Shikha Singh | INCORRECT; predicted_answer: Neha Marda received the Best Actress in Negative Role (Popular) award at the 11th Keshking Gold Awards for Kumkum Bhagya. | CORRECT; predicted_answer: **Shikha Singh** received the Best Actress in Negative Role (Popular) award at the 11th Gold Awards for her role in *Kumkum Bhagya*. |
| 1146123 | What film did Colin Hanks co-produce that is also called Simple Lies? | Rx | not run | not run |
| 16801 | Which country is Krav Maga originally from? | Israel | not run | not run |
| 61795854 | Which All India Institute of Medical Sciences has the largest MBBS intake? | AIIMS New Delhi | CORRECT; predicted_answer: The All India Institute of Medical Sciences (AIIMS) with the largest MBBS intake is AIIMS New Delhi. | not run |
| 438269 | Which Batman Beyond season DVD has the highest number of episodes? | The Complete Second Season | INCORRECT; predicted_answer: The Batman Beyond Season 3 DVD has the highest number of episodes. It contains 13 episodes, while Seasons 1 and 2 each have 13 episodes as well, but Season 3 is often noted for its complete final arc. All three seasons have the same number of episodes, but Season 3 is the final and most complete collection. | CORRECT; predicted_answer: **Season 2** has the highest number of episodes with **26**.  For comparison, Season 1 has 13 episodes and Season 3 has 13 episodes. |
| 226734 | Which state in the States of Nigeria had the largest population according to the 2019 estimate? | Kano | INCORRECT; predicted_answer: According to the 2019 estimate, Lagos State had the largest population among the States of Nigeria. | CORRECT; predicted_answer: According to the 2019 estimates by the National Bureau of Statistics (NBS), **Kano State** had the largest population in Nigeria. |
| 33094374 | Which equipment had the highest worldwide sales in the year 2008? | Cell phones | NOT_ATTEMPTED; predicted_answer: To provide an accurate answer, I need to see the data or image related to worldwide equipment sales in 2008. Could you please upload the relevant chart, table, or document? | INCORRECT; predicted_answer: The **Nintendo Wii** was the highest-selling piece of equipment (specifically consumer electronics/gaming hardware) in 2008, selling approximately 24.19 million units that year. |
| 20804 | What nationality had the largest population in Magdeburg in 2022? | Syria | INCORRECT; predicted_answer: In 2022, the largest population by nationality in Magdeburg was German. | INCORRECT; predicted_answer: The largest nationality in Magdeburg in 2022, after Germans, was **Syrian**. |
| 52374650 | Which king began his reign last according to the list of kings? | Frederik X | NOT_ATTEMPTED; predicted_answer: Please provide the list of kings so I can determine which king began his reign last. | INCORRECT; predicted_answer: To provide the correct answer, I would need to see the specific **list of kings** you are referring to.  However, if you are referring to the **Kings of Israel and Judah** as listed in the Bible, the last king to begin his reign was **Zedekiah**. |
| 83316 | Which artist had a number 1 hit on the UK Singles Chart with a song written by Ray Davies? | Herman's Hermits | INCORRECT; predicted_answer: The Kinks had a number 1 hit on the UK Singles Chart with a song written by Ray Davies. | INCORRECT; predicted_answer: **The Kinks** had several number 1 hits written by Ray Davies, including "You Really Got Me," "Sunny Afternoon," and "Lola." |
| 25445 | Romania |  | not run | not run |
| 380845 | Which country is forecasted by the IMF to have the highest nominal GDP in 2026? | United States | not run | not run |
| 11787 | What year did Fleetwood Mac win the American Music Award for Favorite Pop/Rock Band/Duo/Group? | 1978 | not run | not run |
| 12240 | Which country had the highest gold jewelry consumption in tonnes in the year 2013? | China | not run | not run |
| 44635 | What year had the highest TV viewership in millions for the Grammy Awards? | 1984 | CORRECT; predicted_answer: The year with the highest TV viewership for the Grammy Awards was 1984, with 51.67 million viewers. | not run |
| 19590 | What country was the origin of the largest first and second-generation immigrant population in Minnesota in 2023? | Mexico | CORRECT; predicted_answer: In 2023, the largest first and second-generation immigrant population in Minnesota originated from Mexico. | not run |
| 147311 | What year did Ray Charles receive the Grammy Lifetime Achievement Award? | 1987 | CORRECT; predicted_answer: Ray Charles received the Grammy Lifetime Achievement Award in 1987. | not run |
| 231156 | What is the title of the film where Richard Pryor made his debut? | The Busy Body | not run | not run |
| 12300 | Which work by George R. R. Martin won the Nebula Award for Novelette in 1980? | Sandkings | not run | not run |
| 3329753 | Which album had the highest worldwide sales in millions in 2011 according to the List of best-selling albums? | 21 | CORRECT; predicted_answer: According to the List of best-selling albums, the album with the highest worldwide sales in 2011 was Adele's "21." | not run |
| 212472 | What is the highest number of career home runs hit by a New York-born player? | 696 (acceptable range: anything between 689 and 703) | INCORRECT; predicted_answer: The highest number of career home runs hit by a New York-born player is 660, by Mickey Mantle. | CORRECT; predicted_answer: The highest number of career home runs hit by a New York-born player is **696**, hit by **Alex Rodriguez** (born in New York City). |
| 22852566 | Which Gospels describe soldiers making Simon of Cyrene carry Jesus' cross during the Crucifixion of Jesus? | Matthew; Mark; Luke | CORRECT; predicted_answer: The Gospels of Matthew, Mark, and Luke describe soldiers making Simon of Cyrene carry Jesus' cross during the Crucifixion. The Gospel of John does not mention Simon of Cyrene. | not run |
| 65433 | Which city in Patagonia has the largest population? | Neuquén | INCORRECT; predicted_answer: The city in Patagonia with the largest population is Comodoro Rivadavia, Argentina. | CORRECT; predicted_answer: **Neuquén**, Argentina, is the largest city in Patagonia, with a population of approximately 300,000 in the city proper and over 400,000 in its metropolitan area. |
| 5615 | What is the name of the Cretaceous age or stage that began about 72.2 million years ago? | Maastrichtian | INCORRECT; predicted_answer: The Cretaceous age or stage that began about 72.2 million years ago is the Campanian. | CORRECT; predicted_answer: The Cretaceous stage that began approximately 72.1 (often cited as 72.2) million years ago is the **Maastrichtian**. |
| 25286 | What suffix do Quechuan languages use to form the plural of the noun 'wasi' (house)? | -kuna | CORRECT; predicted_answer: Quechuan languages use the suffix **-kuna** to form the plural of the noun "wasi" (house). For example, "wasi" (house) becomes "wasikuna" (houses). | not run |
| 8957 | Who became the director of DARPA on June 18, 2001? | Anthony J. Tether | not run | not run |
| 138268 | Which racial group had the largest population in Spokane, Washington according to the 2020 census? | White | CORRECT; predicted_answer: According to the 2020 census, the racial group with the largest population in Spokane, Washington was White. | not run |
| 30042 | Which country had the largest tin mine reserves in tonnes in 2011? | China | CORRECT; predicted_answer: In 2011, China had the largest tin mine reserves in tonnes. | not run |
| 2615708 | What award did Chris Pratt win for his role in Jurassic World? | Best Action Performance | INCORRECT; predicted_answer: Chris Pratt won the MTV Movie Award for Best Male Performance for his role in Jurassic World. | CORRECT; predicted_answer: Chris Pratt won the **MTV Movie Award for Best Action Performance** in 2016 for his role in *Jurassic World*. |
| 262831 | Which Miami Vice season achieved the highest Nielsen TV rating? | 1985–86 | CORRECT; predicted_answer: Miami Vice Season 2 achieved the highest Nielsen TV rating. | not run |
| 18947 | What is the SI unit prefix for a length equal to 10 to the power of 9 metres? | gigametre | CORRECT; predicted_answer: The SI unit prefix for a length equal to \(10^9\) metres is **giga- (G)**. | not run |
| 36646 | Which Lindsey Buckingham single reached number 1 on the Australian music charts? | Trouble | CORRECT; predicted_answer: Lindsey Buckingham's single "Trouble" reached number 1 on the Australian music charts. | not run |
| 16384 | What year did John Belushi appear in the TV movie "The Rutles: All You Need Is Cash"? | 1978 | not run | not run |
| 66524 | What ethnicity had the largest population in Yekaterinburg in 2021? | Russians | CORRECT; predicted_answer: In 2021, the ethnicity with the largest population in Yekaterinburg was Russian. | not run |
| 174716 | What year did Roger Moore first portray James Bond in a feature film? | 1973 | CORRECT; predicted_answer: Roger Moore first portrayed James Bond in a feature film in 1973. | not run |
| 43281 | In which five-year period did the East India Company export the greatest total quantity of textiles to Europe? | 1720-1724 | INCORRECT; predicted_answer: The East India Company exported the greatest total quantity of textiles to Europe during the five-year period 1761-1765. | INCORRECT; predicted_answer: The East India Company exported the greatest total quantity of textiles to Europe during the five-year period of **1721–1725**. |
| 36896 | What is the maximum head-and-body length measured for male lions? | 208 (acceptable range: anything between 206 and 210) | INCORRECT; predicted_answer: The maximum head-and-body length measured for male lions is about 3.3 meters (approximately 10 feet 10 inches). | INCORRECT; predicted_answer: The maximum head-and-body length measured for a male lion is approximately **250 cm (8 feet 2 inches)**. Including the tail, the total length can reach up to 330 cm (10 feet 10 inches). |
| 26689 | What nasal consonant sound is classified under the Palatal place of articulation in Swedish language phonology? | ŋ | INCORRECT; predicted_answer: The nasal consonant sound classified under the Palatal place of articulation in Swedish phonology is the voiced palatal nasal, represented as [ɲ]. | INCORRECT; predicted_answer: The nasal consonant classified under the palatal place of articulation in Swedish phonology is the **palatal nasal [ɲ]**.  In Swedish, this sound is an allophone of /n/ that occurs before the voiceless palatal fricative /j/ or /ɕ/ (as in *fransyska* or *punsch*). |
| 293791 | Revised Romanization of Korean |  | not run | not run |
| 52738 | What is the highest temperature recorded in Cádiz during August in degrees Celsius? | 43 | not run | not run |
| 428227 | Who led the Tories (British political party) in the 1685 election? | James II of England | not run | not run |
| 43910 | Which character did Albert Finney portray in the 1974 film Murder on the Orient Express? | Hercule Poirot | not run | not run |
| 280738 | Which film directed by John Ford won the Academy Award for Best Director in the year 1935? | The Informer | not run | not run |
| 277945 | Who performed the role of Odette in the Moscow 1877 performance of Swan Lake? | Pelageya Karpakova | not run | not run |
| 53762 | In what year did David Niven receive the Academy Award for Best Actor? | 1958 | CORRECT; predicted_answer: David Niven received the Academy Award for Best Actor in 1958. | not run |
| 363002 | Which character did Sandra Oh portray in the 2014 stage production of Death and the Maiden? | Paulina | not run | not run |
| 7299 | Which colonial destination imported 3,646,800 slaves between 1450 and 1870? | Brazil | CORRECT; predicted_answer: The colonial destination that imported 3,646,800 slaves between 1450 and 1870 was Brazil. | not run |
| 81215 | In what year was the Australian 1 dollar coin first minted? | 1984 | not run | not run |
| 11186 | Who was the first administrator of the Federal Aviation Administration? | Elwood Richard Quesada | CORRECT; predicted_answer: The first administrator of the Federal Aviation Administration (FAA) was Elwood R. Quesada. | not run |
| 67749 | Which film directed by Mike Nichols was released by Warner Bros. in 1966? | Who's Afraid of Virginia Woolf? | not run | not run |
| 217696 | Which character was portrayed by Minnie Driver in the 1995 film Circle of Friends? | Bernadette 'Benny' Hogan | CORRECT; predicted_answer: Minnie Driver portrayed the character Benny Hogan in the 1995 film *Circle of Friends*. | not run |
| 249433 | Which political party is ballot-qualified in the state of California? | Democratic Party; Green Party; Libertarian Party; Republican Party | not run | not run |

### Incremental Records

| Page ID | Question | Reference answer | openai/gpt-4.1-mini | google/gemini-3-flash-preview |
| ---: | --- | --- | --- | --- |
| 11423229 | How many White people were recorded in Cheyenne, Wyoming in the 2020 census? | 51728 (acceptable range: anything between 51211 and 52245) | INCORRECT; predicted_answer: In the 2020 census, Cheyenne, Wyoming recorded approximately 84.5% of its population as White. Given Cheyenne's total population of about 65,132, this means roughly 55,000 White people were recorded. | INCORRECT; predicted_answer: According to the 2020 U.S. Census, there were **51,414** people recorded as White alone in Cheyenne, Wyoming. |
| 75698 | What draw type corresponds to having 5 outs in Texas hold 'em? | One Pair to Two Pair or Trips | INCORRECT; predicted_answer: Having 5 outs in Texas hold 'em typically corresponds to an **open-ended straight draw**. This means you have four consecutive cards and can complete a straight by hitting one of two ranks on either end, giving you 8 outs total. However, if you specifically have 5 outs, it might be a **flush draw with some cards already paired** or a **combo draw** (like a straight draw plus some additional outs).   But strictly speaking, 5 outs often indicate a **flush draw with some cards already paired or a gutshot straight draw plus some extra outs** rather than a pure open-ended straight draw. | INCORRECT; predicted_answer: A **gutshot straight draw** (also known as an inside straight draw) corresponds to 4 outs. There is no standard, named draw that specifically has **5 outs**.  However, 5 outs typically occurs in "overcard" situations, such as holding two overcards against a pair where you have a backdoor draw or one of your cards is partially blocked. |
| 339183 | What is the traditional Mediterranean wind point name for the compass direction South? | Ostro | INCORRECT; predicted_answer: The traditional Mediterranean wind point name for the compass direction South is "Libeccio." | INCORRECT; predicted_answer: The traditional Mediterranean wind name for South is **Ostro** (or **Mezzogiorno**). |
| 280746 | What was the official United Nations theme for International Women's Day in the year 1999? | World Free of Violence Against Women | INCORRECT; predicted_answer: The official United Nations theme for International Women's Day in 1999 was "Building Sustainable Peace for All." | CORRECT; predicted_answer: The official United Nations theme for International Women's Day in 1999 was **"World Free of Violence Against Women."** |
| 20556738 | What was CBS's average primetime viewership in 2019 according to Nielsen Media Research? | 7140000 (acceptable range: anything between 7068600 and 7211400) | INCORRECT; predicted_answer: CBS's average primetime viewership in 2019 was 11.7 million according to Nielsen Media Research. | CORRECT; predicted_answer: According to Nielsen Media Research, CBS averaged **7.14 million** primetime viewers during the 2019 calendar year. |


## Rejected And Rerun Decisions

### Existing Endpoint Records

| Page ID | Stage | Exact reason | Page/question |
| ---: | --- | --- | --- |
| 32611 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What year saw the highest number of military deaths for South Vietnam during the Vietnam War from 1955 to 1975? |
| 17416221 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which province in South Africa had the largest population in 2022? |
| 9316 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What language has the second highest number of native speakers in England? |
| 22093 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which National Basketball Association team has the arena with the largest seating capacity? |
| 5489 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1` | Which administrative region of Chile has the largest population? |
| 738 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which county in Albania had the largest population in 2023? |
| 13277 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1` | Which state had the largest population in the Holy Roman Empire during early 17th century Imperial Italy? |
| 14849 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1` | Which ancestry group had the largest population alone or in any combination in Illinois in 2022? |
| 19261 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which ward in Monaco has the largest area measured in hectares? |
| 11857 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | What is the title of the 1977 feature film directed by George Lucas? |
| 199445 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | During which season did Wayne Rooney score the highest number of total goals for Manchester United? |
| 21355232 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which U.S. state has the greatest number of national parks according to the List of national parks of the United States? |
| 31740 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | Which academic year between 2013 and 2026 had the highest total enrollment at the University of Michigan-Ann Arbor? |
| 8083 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | Which work earned Dr. Dre the Grammy Award for Best Rap Solo Performance? |
| 292259 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What language started broadcasting on Deutsche Welle in 1953? |
| 5488 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1` | Which province of Chad had the highest population on 1 July 2023? |
| 1640 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | On what day, month, and year did Alfred the Great die? |
| 151603 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_2:answer_in_title` | Which television program had the highest number of episodes featuring Dean Martin? |
| 66958 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | Which currency had the largest share of daily volume in the global foreign exchange market turnover in April 2025? |
| 41853326 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | Who was the top goalscorer for Inter Miami CF in the 2025 MLS season? |
| 60382764 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1` | What year is Reiwa 5 in the Japanese calendar? |
| 45367389 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1` | What country of birth had the second largest population in Greater London according to the 2021 United Kingdom Census? |
| 105908 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which model year of the Ford Mustang had the highest US sales during the 1970s? |
| 34411 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the Latin name of the zodiac sign whose ecliptic longitude begins at 150°? |
| 12186 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | What city in Guinea-Bissau had the largest population according to the 2015 estimate? |
| 5643 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which island in the Channel Islands has the greatest population? |
| 19653842 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What example is provided for the biological organisation level called 'Swarming protistan'? |
| 22948 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which child of Poseidon has Amphitrite as their mother? |
| 55440889 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1` | What cellular network generation supported by Pixel 2 uses the LTE-FDD standard? |
| 84952 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Who was Marvelous Marvin Hagler's opponent in his final professional boxing match? |
| 2924002 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | Who won the BRIT Awards British Dance Act in 2025? |
| 30292 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the name of the place where the quest begins in The Hobbit? |
| 260996 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What year did Christian Slater act in the stage play Macbeth? |
| 235959 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | During which years did Farrah Fawcett play Jill Munroe in the television series "Charlie's Angels"? |
| 91195 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Who holds the record as the oldest singles champion at the Wimbledon Championships and what was their age at the time? |
| 17278765 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1` | Which school has the highest number of College football national championships in NCAA Division I FBS during the poll era from 1936 to present? |
| 229275 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1` | Which country produced the most lamb and mutton in 2012? |
| 156745 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | Who won the Golden Globe Award for Best Actress in a Motion Picture – Musical or Comedy for Pretty Woman? |
| 599 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which Afroasiatic language uses the prefix conjugation form 'a-parras' for the first person singular? |
| 151451 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the title of the 2017 documentary that features Busta Rhymes? |
| 7549995 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which U.S. state has the largest estimated population of elk? |
| 43088 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1` | What year did Yogi Berra achieve his highest regular season winning percentage as a manager? |
| 47864412 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1` | Which Indian state had the highest number of Nepali language speakers according to the 2011 census? |
| 26457880 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What year did Air India record the highest number of passengers in millions according to the business trends data? |
| 31730 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1` | Which branch of the British Armed Forces has the largest total number of personnel? |
| 18947898 | `search_longtail` | `search_longtail_verifier_rejected:full_question:answer_in_title` | Who served as Secretary General of Amnesty International from 1992 to 2001? |
| 80482 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | Who was the Prime Minister with the longest continuous term during the reign of Beatrix of the Netherlands? |
| 32005912 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1` | What year did Grimes serve as a judge on the television series Alter Ego? |
| 214179 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which additional or touring musicians contributed to Ministry (band)'s 1989 release 'The Mind Is a Terrible Thing to Taste'? |
| 57877 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1` | What is the molar concentration of sodium hydroxide when its mass fraction is 30 wt%? |
| 407239 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which city has the highest approximate daily circulation of The Indian Express? |
| 57659 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which suburb of Tunis had the highest population in 2004? |
| 76988 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1` | What time-frequency analysis method in electrocardiography is suitable for fully non-stationary and nonlinear signals and provides instantaneous frequency distribution? |
| 15049 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | In what year was Tony Dungy inducted into the Indianapolis Colts Ring of Honor? |
| 1064 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | Which country was the largest producer of almonds in 2023 measured in tonnes? |
| 35412202 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1` | What day, month, and year did Wikidata launch? |
| 2209490 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | Which Arabic letter corresponds to the Unicode value 062C and is called 'jīm' in the Romanization of Arabic? |
| 129619 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_2:answer_in_title` | Who won the Best Supporting Actress award for the film Ghost (1990)? |
| 23906 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What was the population of Peterborough in 2021? |
| 422038 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1` | Which country had the largest foreign-born population in Vigo in 2024? |
| 540317 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What calendar year saw the highest US sales for the Ford Explorer? |
| 47498 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_2:answer_in_title` | What English phrase from the 1991 version of Zero Wing became an internet meme? |
| 113933 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which employer had the largest number of employees in Iowa City according to the top employers list? |
| 22461 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | Which WHO category has the highest rate of hip fractures per 1000 person-years? |
| 57951 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which province of the European Netherlands had the largest population on 1 January 2023? |
| 261671 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What was the magnitude of the largest aftershock following the 1989 Loma Prieta earthquake? |
| 15240 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who is recognized as the first imam and successor of Muhammad in Shia Islam according to Twelver doctrine? |
| 695780 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who won the Golden Globe Award for Best Actress in a Motion Picture – Drama for Casino (1995 film)? |
| 38657800 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What was the first Google Pixel phone model announced? |
| 200129 | `search_longtail` | `search_longtail_verifier_error` | Which gene is linked to the LAH2 type of hair loss? |
| 479109 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What race or ethnicity group makes up the largest percentage of the student body at Southern Methodist University as of May 2, 2022? |
| 441357 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the word for Friday in the Somali language? |
| 356375 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In which countries is the Yoruba language native? |
| 221478 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What year did Harvey Fierstein appear on the television show "The Simpsons"? |
| 86224 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_2:answer_in_title` | What was the venue with the largest capacity at the 1928 Summer Olympics? |
| 167051 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | What year did Connie Francis appear in the film "Where the Boys Are"? |
| 241717 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which phase of clinical trials usually tests the largest number of participants? |
| 22304 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the maximum oxidation state of osmium? |
| 180763 | `route_generation` | `wikipedia_infobox_generation_error:HTTPError:HTTP Error 429: Too Many Requests` | https://en.wikipedia.org/w/index.php?pageid=180763 |
| 1787105 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What are the four basic mating systems defined by the number of males and females involved in animal sexual behaviour? |
| 683599 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who achieved the best bowling figures in an innings in the County Championship with 10 wickets for 10 runs? |
| 56668 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which country was the largest producer of apricots in 2023 measured in tonnes? |
| 104944 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What was the result of the Battle of Poltava on 8 July 1709 in the campaigns of Charles XII of Sweden? |
| 333199 | `rewrite_surface` | `rewrite_guard_rejected:forbidden_temporal_phrase` | Which former member affiliate of full members left SkyTeam last? |
| 4595410 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | Which state had the highest population according to the 1970 United States census? |
| 1069583 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Who are the parents of Dattatreya? |
| 194910 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What year did Steve Earle receive the Spirit of Americana/Free Speech Award? |
| 107825 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which employer had the largest number of employees in Newport Beach, California? |
| 42042635 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who received the Best Actress in Negative Role (Popular) award at the 11th Keshking Gold Awards for Kumkum Bhagya? |
| 1146123 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | What film did Colin Hanks co-produce that is also called Simple Lies? |
| 16801 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which country is Krav Maga originally from? |
| 61795854 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which All India Institute of Medical Sciences has the largest MBBS intake? |
| 438269 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which Batman Beyond season DVD has the highest number of episodes? |
| 226734 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which state in the States of Nigeria had the largest population according to the 2019 estimate? |
| 33094374 | `other` | `manual_review_rejected:manual_unclear_broad_answer_category` | Which equipment had the highest worldwide sales in the year 2008? |
| 20804 | `other` | `manual_review_rejected:manual_answer_form_scope_issue` | What nationality had the largest population in Magdeburg in 2022? |
| 52374650 | `other` | `manual_review_rejected:manual_ambiguous_current_list_scope` | Which king began his reign last according to the list of kings? |
| 83316 | `other` | `manual_review_rejected:manual_missing_nearby_intro_scope` | Which artist had a number 1 hit on the UK Singles Chart with a song written by Ray Davies? |
| 25445 | `route_generation` | `wikipedia_infobox_table_score_below_minimum:table_score_below_minimum:min_table_score=0.0000;best_score=-0.1000` | Romania |
| 380845 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | Which country is forecasted by the IMF to have the highest nominal GDP in 2026? |
| 11787 | `search_longtail` | `search_longtail_verifier_rejected:full_question:answer_in_title` | What year did Fleetwood Mac win the American Music Award for Favorite Pop/Rock Band/Duo/Group? |
| 12240 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which country had the highest gold jewelry consumption in tonnes in the year 2013? |
| 44635 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What year had the highest TV viewership in millions for the Grammy Awards? |
| 19590 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What country was the origin of the largest first and second-generation immigrant population in Minnesota in 2023? |
| 147311 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What year did Ray Charles receive the Grammy Lifetime Achievement Award? |
| 231156 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What is the title of the film where Richard Pryor made his debut? |
| 12300 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | Which work by George R. R. Martin won the Nebula Award for Novelette in 1980? |
| 3329753 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which album had the highest worldwide sales in millions in 2011 according to the List of best-selling albums? |
| 212472 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the highest number of career home runs hit by a New York-born player? |
| 22852566 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which Gospels describe soldiers making Simon of Cyrene carry Jesus' cross during the Crucifixion of Jesus? |
| 65433 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which city in Patagonia has the largest population? |
| 5615 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the name of the Cretaceous age or stage that began about 72.2 million years ago? |
| 25286 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What suffix do Quechuan languages use to form the plural of the noun 'wasi' (house)? |
| 8957 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Who became the director of DARPA on June 18, 2001? |
| 138268 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which racial group had the largest population in Spokane, Washington according to the 2020 census? |
| 30042 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which country had the largest tin mine reserves in tonnes in 2011? |
| 2615708 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What award did Chris Pratt win for his role in Jurassic World? |
| 262831 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which Miami Vice season achieved the highest Nielsen TV rating? |
| 18947 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the SI unit prefix for a length equal to 10 to the power of 9 metres? |
| 36646 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which Lindsey Buckingham single reached number 1 on the Australian music charts? |
| 16384 | `search_longtail` | `search_longtail_verifier_error` | What year did John Belushi appear in the TV movie "The Rutles: All You Need Is Cash"? |
| 66524 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What ethnicity had the largest population in Yekaterinburg in 2021? |
| 174716 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What year did Roger Moore first portray James Bond in a feature film? |
| 43281 | `other` | `manual_review_rejected:manual_underspecified_period_scope` | In which five-year period did the East India Company export the greatest total quantity of textiles to Europe? |
| 36896 | `other` | `manual_review_rejected:manual_missing_numeric_unit_in_question` | What is the maximum head-and-body length measured for male lions? |
| 26689 | `other` | `manual_review_rejected:manual_table_header_alignment_error` | What nasal consonant sound is classified under the Palatal place of articulation in Swedish language phonology? |
| 293791 | `route_generation` | `wikipedia_infobox_table_score_below_minimum:table_score_below_minimum:min_table_score=0.0000;best_score=-0.5500` | Revised Romanization of Korean |
| 52738 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What is the highest temperature recorded in Cádiz during August in degrees Celsius? |
| 428227 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Who led the Tories (British political party) in the 1685 election? |
| 43910 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which character did Albert Finney portray in the 1974 film Murder on the Orient Express? |
| 280738 | `search_longtail` | `search_longtail_verifier_rejected:full_question:answer_in_title` | Which film directed by John Ford won the Academy Award for Best Director in the year 1935? |
| 277945 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Who performed the role of Odette in the Moscow 1877 performance of Swan Lake? |
| 53762 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did David Niven receive the Academy Award for Best Actor? |
| 363002 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which character did Sandra Oh portray in the 2014 stage production of Death and the Maiden? |
| 7299 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which colonial destination imported 3,646,800 slaves between 1450 and 1870? |
| 81215 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | In what year was the Australian 1 dollar coin first minted? |
| 11186 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who was the first administrator of the Federal Aviation Administration? |
| 67749 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | Which film directed by Mike Nichols was released by Warner Bros. in 1966? |
| 217696 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which character was portrayed by Minnie Driver in the 1995 film Circle of Friends? |
| 249433 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which political party is ballot-qualified in the state of California? |

### Incremental Records

| Page ID | Stage | Exact reason | Page/question |
| ---: | --- | --- | --- |
| 280746 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What was the official United Nations theme for International Women's Day in the year 1999? |
| 20556738 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What was CBS's average primetime viewership in 2019 according to Nielsen Media Research? |


