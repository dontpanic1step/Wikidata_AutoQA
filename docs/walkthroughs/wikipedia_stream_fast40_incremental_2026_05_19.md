# Route 3 Streaming Wikipedia Page-ID Walkthrough - 2026-05-19

## Stats

- Mode: `page_id_stream`
- Page source: `table-search`
- Table-search queries: `insource:"wikitable"`
- Endpoint resume: 5 accepted and 35 rejected records loaded
- Existing accepted QAs before run: 5
- Existing rejected QAs/pages before run: 35
- Attempted page IDs: 40
- Accepted QAs: 11
- Accepted QAs after resume: 16
- Rejected QAs/pages: 29
- Rejected QAs/pages after resume: 64
- Returned to rerun pool without final decision: 0
- Wall-clock runtime: 993.1934s
- DuckDuckGo top K: 5
- Generated search queries per QA: 2
- DuckDuckGo parallel queries: 3
- Page-id bounds: 1 to 80000000
- Stream state: `outputs\wikipedia_stream_fast40_fresh_2026_05_19_state.json`
- Accepted output: `outputs\wikipedia_stream_fast40_2026_05_19_accepted.jsonl`
- Rejected output: `outputs\wikipedia_stream_fast40_2026_05_19_rejected.jsonl`
- Domain policy: `domain_and_subdomain_optional_for_page_id_streaming`
- Rerun pool after run: `empty`

### Overall Displayed Stats

| Scope | Page IDs/records | Accepted | Rejected | Rerun | Accepted/page rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| Existing endpoint records | 40 | 5 | 35 | 0 | 12.5% |
| Incremental run | 40 | 11 | 29 | 0 | 27.5% |
| Overall displayed | 80 | 16 | 64 | 0 | 20.0% |

### Survival By Layer

| Layer | Entered | Failed | Survived | Layer survival | Cumulative survival |
| --- | ---: | ---: | ---: | ---: | ---: |
| Page-id reservation | 40 | 0 | 40 | 100.0% | 100.0% |
| Unresolved or returned to rerun pool | 40 | 0 | 40 | 100.0% | 100.0% |
| Page extraction, table grading, and QA generation | 40 | 0 | 40 | 100.0% | 100.0% |
| Rewrite and surface validation | 40 | 1 | 39 | 97.5% | 97.5% |
| DuckDuckGo long-tail filtering | 39 | 10 | 29 | 74.4% | 72.5% |
| Second-stage model grading | 29 | 18 | 11 | 37.9% | 27.5% |
| Shared route-aware validation | 11 | 0 | 11 | 100.0% | 27.5% |
| Deduplication | 11 | 0 | 11 | 100.0% | 27.5% |
| Other rejection | 11 | 0 | 11 | 100.0% | 27.5% |

### Failure Reasons

| Stage | Exact reason | Count |
| --- | --- | ---: |
| `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1` | 10 |
| `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | 8 |
| `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | 3 |
| `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | 2 |
| `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | 2 |
| `search_longtail` | `search_longtail_verifier_rejected:keyword_query_2:answer_in_title` | 2 |
| `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | 1 |
| `search_longtail` | `search_longtail_verifier_rejected:full_question:answer_in_title` | 1 |

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

| Phase | Count | Total seconds | Average seconds | Max seconds |
| --- | ---: | ---: | ---: | ---: |
| `candidate_processing_seconds` | 40 | 688.9588 | 17.2240 | 32.3885 |
| `duckduckgo_search_seconds` | 39 | 141.1315 | 3.6188 | 5.8355 |
| `first_paragraph_extract_seconds` | 40 | 6.2919 | 0.1573 | 0.3826 |
| `llm_question_generation_seconds` | 40 | 163.8106 | 4.0953 | 8.0484 |
| `number_reference_margin_seconds` | 39 | 0.0011 | 0.0000 | 0.0004 |
| `page_fetch_seconds` | 40 | 120.5422 | 3.0136 | 8.3306 |
| `rewrite_seconds` | 40 | 122.6139 | 3.0653 | 6.2217 |
| `second_stage_grading_seconds` | 29 | 425.1218 | 14.6594 | 25.7056 |
| `table_parse_seconds` | 40 | 9.6904 | 0.2423 | 0.8560 |
| `total_generation_seconds` | 40 | 301.8117 | 7.5453 | 14.1057 |
| `total_processing_seconds` | 40 | 688.9588 | 17.2240 | 32.3885 |

## Accepted Candidates

Existing endpoint records are shown first; incremental records are the records appended by this run.

### Existing Endpoint Records

| Page ID | Question | Answer | Source |
| ---: | --- | --- | --- |
| 40010153 | What year saw the highest number of tourist arrivals in Goa? | 2015 | https://en.wikipedia.org/wiki/Goa |
| 39776 | Which protocol has the maximum amplification factor in UDP-based amplification denial-of-service attacks? | Mitel MiCollab | https://en.wikipedia.org/wiki/Denial-of-service_attack |
| 217231 | Which seasons of Curb Your Enthusiasm have a 100% rating on Rotten Tomatoes? | 2; 3; 5 | https://en.wikipedia.org/wiki/Curb_Your_Enthusiasm |
| 235916 | In which films did Jada Pinkett Smith voice the character Gloria? | Madagascar; Madagascar: Escape 2 Africa; Madagascar 3: Europe's Most Wanted; Penguins of Madagascar | https://en.wikipedia.org/wiki/Jada_Pinkett_Smith |
| 33094374 | Which equipment had the highest worldwide sales in the year 2008? | Cell phones | https://en.wikipedia.org/wiki/Telecommunications |

### Incremental Records

| Page ID | Question | Answer | Source |
| ---: | --- | --- | --- |
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

## Second-Stage Filtering Responses

These are the small-model QA responses used by the second-stage filter: `openai/gpt-4.1-mini` and `google/gemini-3-flash-preview`. Route 3 generation and rewrite outputs are listed separately below.

### Existing Endpoint Records

| Page ID | Question | Reference answer | openai/gpt-4.1-mini | google/gemini-3-flash-preview |
| ---: | --- | --- | --- | --- |
| 40010153 | What year saw the highest number of tourist arrivals in Goa? | 2015 | INCORRECT; predicted_answer: The year 2019 saw the highest number of tourist arrivals in Goa. | INCORRECT; predicted_answer: The year with the highest number of tourist arrivals in Goa was **2019**, with approximately **8.06 million** visitors. |
| 39776 | Which protocol has the maximum amplification factor in UDP-based amplification denial-of-service attacks? | Mitel MiCollab | INCORRECT; predicted_answer: The **Memcached** protocol has the maximum amplification factor in UDP-based amplification denial-of-service (DDoS) attacks. Memcached amplification can reach factors of up to 50,000 times, far exceeding other protocols like DNS or NTP. | INCORRECT; predicted_answer: **Memcached** has the maximum amplification factor, with a potential ratio of up to **51,000:1**. |
| 217231 | Which seasons of Curb Your Enthusiasm have a 100% rating on Rotten Tomatoes? | 2; 3; 5 | INCORRECT; predicted_answer: The seasons of *Curb Your Enthusiasm* with a 100% rating on Rotten Tomatoes are Seasons 1, 3, 4, 5, 7, 8, 9, and 11. | INCORRECT; predicted_answer: Seasons **3, 5, 7, and 10** of *Curb Your Enthusiasm* have a 100% rating on Rotten Tomatoes. |
| 235916 | In which films did Jada Pinkett Smith voice the character Gloria? | Madagascar; Madagascar: Escape 2 Africa; Madagascar 3: Europe's Most Wanted; Penguins of Madagascar | INCORRECT; predicted_answer: Jada Pinkett Smith voiced the character Gloria in the following films:  1. **Madagascar** (2005)   2. **Madagascar: Escape 2 Africa** (2008)   3. **Madagascar 3: Europe's Most Wanted** (2012) | INCORRECT; predicted_answer: Jada Pinkett Smith voiced Gloria the hippopotamus in the following films:  *   **Madagascar** (2005) *   **Madagascar: Escape 2 Africa** (2008) *   **Madagascar 3: Europe's Most Wanted** (2012) *   **Merry Madagascar** (2009) – TV Special *   **Madly Madagascar** (2013) – Short film/Special |
| 33094374 | Which equipment had the highest worldwide sales in the year 2008? | Cell phones | NOT_ATTEMPTED; predicted_answer: To provide an accurate answer, I need to see the data or image related to worldwide equipment sales in 2008. Could you please upload the relevant chart, table, or document? | INCORRECT; predicted_answer: The **Nintendo Wii** was the highest-selling piece of equipment (specifically consumer electronics/gaming hardware) in 2008, selling approximately 24.19 million units that year. |
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

### Incremental Records

| Page ID | Question | Reference answer | openai/gpt-4.1-mini | google/gemini-3-flash-preview |
| ---: | --- | --- | --- | --- |
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


## Route 3 Generation Responses

These are the source-page QA generation and rewrite responses, not the second-stage small-model QA panel.

### Existing Endpoint Records

#### Page 40010153 - accepted

- Exact failure/rejection reason: `accepted`

Route 3 generation response:

```json
{
  "answer": "2015",
  "answer_aliases": [],
  "answer_type": "Number",
  "derivation_summary": "The table 'Tourist Arrivals' lists total arrivals for various years; 2015 has the highest value of 5,297,902 arrivals.",
  "discard_reason": null,
  "question": "In what year did Goa have the highest number of tourist arrivals?",
  "reasoning_type": "max",
  "search_queries": [
    "Goa tourist arrivals by year",
    "year with highest tourist arrivals in Goa"
  ],
  "source_table": 4
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "What year saw the highest number of tourist arrivals in Goa?",
  "search_queries": [
    "Goa tourist arrivals by year",
    "year with maximum tourist arrivals in Goa"
  ]
}
```

#### Page 39776 - accepted

- Exact failure/rejection reason: `accepted`

Route 3 generation response:

```json
{
  "answer": "Mitel MiCollab",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "Selected the protocol with the maximum amplification factor value from the UDP-based amplification attacks table.",
  "discard_reason": null,
  "question": "Which protocol has the highest amplification factor in UDP-based amplification attacks?",
  "reasoning_type": "max",
  "search_queries": [
    "highest amplification factor UDP-based amplification attacks",
    "protocol with largest amplification factor in UDP attacks"
  ],
  "source_table": 1
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which protocol has the maximum amplification factor in UDP-based amplification denial-of-service attacks?",
  "search_queries": [
    "protocol with highest amplification factor in UDP amplification denial-of-service attacks",
    "UDP-based amplification denial-of-service attack protocols with maximum amplification factor"
  ]
}
```

#### Page 217231 - accepted

- Exact failure/rejection reason: `accepted`

Route 3 generation response:

```json
{
  "answer": [
    "2",
    "3",
    "5"
  ],
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "Selected seasons with a 100% Rotten Tomatoes rating from the Critical response table.",
  "discard_reason": null,
  "question": "Which seasons of Curb Your Enthusiasm have a 100% rating on Rotten Tomatoes?",
  "reasoning_type": "comparison",
  "search_queries": [
    "Curb Your Enthusiasm seasons with 100% Rotten Tomatoes rating",
    "Curb Your Enthusiasm Rotten Tomatoes ratings by season"
  ],
  "source_table": 3
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which seasons of Curb Your Enthusiasm have a 100% rating on Rotten Tomatoes?",
  "search_queries": [
    "Curb Your Enthusiasm seasons with 100% Rotten Tomatoes rating",
    "Rotten Tomatoes ratings for Curb Your Enthusiasm seasons"
  ]
}
```

#### Page 235916 - accepted

- Exact failure/rejection reason: `accepted`

Route 3 generation response:

```json
{
  "answer": [
    "Madagascar",
    "Madagascar: Escape 2 Africa",
    "Madagascar 3: Europe's Most Wanted",
    "Penguins of Madagascar"
  ],
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "From the Film table, Jada Pinkett Smith voiced the character Gloria in multiple Madagascar films, identified by the Role column and matching character name Gloria.",
  "discard_reason": null,
  "question": "Which film did Jada Pinkett Smith voice the character Gloria in?",
  "reasoning_type": "comparison",
  "search_queries": [
    "Jada Pinkett Smith voice role Gloria",
    "Films where Jada Pinkett Smith voiced Gloria"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "In which films did Jada Pinkett Smith voice the character Gloria?",
  "search_queries": [
    "Jada Pinkett Smith voice role Gloria films",
    "movies featuring Jada Pinkett Smith as Gloria"
  ]
}
```

#### Page 33094374 - accepted

- Exact failure/rejection reason: `accepted`

Route 3 generation response:

```json
{
  "answer": "Cell phones",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "Compared the sales values for Computers and Cell phones in 2008 and found Cell phones had the highest sales with 1000 units.",
  "discard_reason": null,
  "question": "Which equipment had the highest worldwide sales in 2008?",
  "reasoning_type": "max",
  "search_queries": [
    "worldwide equipment sales 2008 cell phones vs computers",
    "highest equipment sales 2008 telecommunications"
  ],
  "source_table": 3
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which equipment had the highest worldwide sales in the year 2008?",
  "search_queries": [
    "equipment with highest worldwide sales 2008",
    "top selling telecommunications equipment 2008"
  ]
}
```

#### Page 32611 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "1972",
  "answer_aliases": [],
  "answer_type": "Number",
  "derivation_summary": "From the 'Military deaths (1955–1975)' table, 1972 has the highest South Vietnam military deaths with 39,587.",
  "discard_reason": null,
  "question": "In what year did South Vietnam have the highest number of military deaths during the Vietnam War from 1955 to 1975?",
  "reasoning_type": "max",
  "search_queries": [
    "South Vietnam military deaths by year Vietnam War",
    "year with highest South Vietnam military deaths 1955-1975"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "What year saw the highest number of military deaths for South Vietnam during the Vietnam War from 1955 to 1975?",
  "search_queries": [
    "South Vietnam military deaths by year Vietnam War",
    "year with most South Vietnam military deaths Vietnam War 1955-1975"
  ]
}
```

#### Page 17416221 - search_longtail

- Exact failure/rejection reason: `search_longtail_verifier_rejected:full_question:hit_rate_exceeded`

Route 3 generation response:

```json
{
  "answer": "Gauteng",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "The table lists South African provinces with their populations in 2022; Gauteng has the highest population of 15,099,422.",
  "discard_reason": null,
  "question": "Which province in South Africa has the largest population according to the 2022 data?",
  "reasoning_type": "max",
  "search_queries": [
    "South Africa provinces population 2022",
    "largest population province in South Africa 2022"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which province in South Africa had the largest population in 2022?",
  "search_queries": [
    "South Africa province population 2022",
    "largest population province in South Africa 2022"
  ]
}
```

#### Page 9316 - search_longtail

- Exact failure/rejection reason: `search_longtail_verifier_rejected:full_question:hit_rate_exceeded`

Route 3 generation response:

```json
{
  "answer": "Polish",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "From the Language table, English has the highest number of native speakers (46,937 thousand), followed by Polish with 529 thousand native speakers, making Polish the second highest.",
  "discard_reason": null,
  "question": "Which language has the second highest number of native speakers in England?",
  "reasoning_type": "ordinal",
  "search_queries": [
    "native speakers of languages in England",
    "second most spoken native language in England"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "What language has the second highest number of native speakers in England?",
  "search_queries": [
    "second most spoken native language in England",
    "languages by number of native speakers in England"
  ]
}
```

#### Page 22093 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "Chicago Bulls",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "From the 'Overview of NBA teams' table, the Chicago Bulls have the largest arena capacity of 20,917 among all NBA teams listed.",
  "discard_reason": null,
  "question": "Which NBA team has the largest arena capacity?",
  "reasoning_type": "max",
  "search_queries": [
    "NBA teams arena capacity largest",
    "NBA team with biggest arena capacity"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which National Basketball Association team has the arena with the largest seating capacity?",
  "search_queries": [
    "NBA team with largest arena capacity",
    "National Basketball Association arena seating capacity by team"
  ]
}
```

#### Page 5489 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "Santiago Metropolitan",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "The table lists populations of Chilean regions; Santiago Metropolitan has the highest population of 7,400,741.",
  "discard_reason": null,
  "question": "Which region of Chile has the highest population according to the administrative divisions?",
  "reasoning_type": "max",
  "search_queries": [
    "Chile regions population",
    "most populous region in Chile"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which administrative region of Chile has the largest population?",
  "search_queries": [
    "population by administrative region in Chile",
    "Chile regions population statistics"
  ]
}
```

#### Page 738 - search_longtail

- Exact failure/rejection reason: `search_longtail_verifier_rejected:full_question:hit_rate_exceeded`

Route 3 generation response:

```json
{
  "answer": "Tirana",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "From the Administrative divisions table, Tirana county has the highest population value of 758,513 in 2023 among all listed counties.",
  "discard_reason": null,
  "question": "Which county in Albania has the largest population according to the 2023 data?",
  "reasoning_type": "max",
  "search_queries": [
    "Albania counties population 2023",
    "largest population county in Albania 2023"
  ],
  "source_table": 3
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which county in Albania had the largest population in 2023?",
  "search_queries": [
    "Albania county population 2023",
    "largest population county in Albania 2023"
  ]
}
```

#### Page 13277 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "Duchy of Milan",
  "answer_aliases": [
    "Spanish"
  ],
  "answer_type": "Entity",
  "derivation_summary": "Identified the state with the maximum population value in the 'States of Imperial Italy by population, early 17th century' table.",
  "discard_reason": null,
  "question": "Which state had the largest population in Imperial Italy in the early 17th century?",
  "reasoning_type": "max",
  "search_queries": [
    "largest population state Imperial Italy early 17th century",
    "Duchy of Milan population early 1600s"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [
    "Spanish"
  ],
  "discard_reason": null,
  "rewritten_question": "Which state had the largest population in the Holy Roman Empire during early 17th century Imperial Italy?",
  "search_queries": [
    "largest population state in Holy Roman Empire early 17th century Imperial Italy",
    "most populous state in Imperial Italy under Holy Roman Empire early 1600s"
  ]
}
```

#### Page 14849 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "German",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "From the Ancestry table, German ancestry has the highest number as of 2022 (Alone or in any combination) with 2,014,297 people.",
  "discard_reason": null,
  "question": "Which ancestry group had the largest number of people alone or in any combination in Illinois in 2022?",
  "reasoning_type": "max",
  "search_queries": [
    "largest ancestry group in Illinois 2022",
    "Illinois ancestry population 2022"
  ],
  "source_table": 7
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which ancestry group had the largest population alone or in any combination in Illinois in 2022?",
  "search_queries": [
    "largest ancestry group population in Illinois 2022",
    "Illinois ancestry groups population numbers 2022"
  ]
}
```

#### Page 19261 - search_longtail

- Exact failure/rejection reason: `search_longtail_verifier_rejected:full_question:hit_rate_exceeded`

Route 3 generation response:

```json
{
  "answer": "Monte-Carlo",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "From the Wards table, Monte-Carlo has the largest area of 43.7 hectares among all listed wards.",
  "discard_reason": null,
  "question": "Which ward in Monaco has the largest area in hectares?",
  "reasoning_type": "max",
  "search_queries": [
    "largest ward by area in Monaco",
    "Monaco wards area comparison"
  ],
  "source_table": 4
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which ward in Monaco has the largest area measured in hectares?",
  "search_queries": [
    "wards of Monaco by area in hectares",
    "largest ward in Monaco by area"
  ]
}
```

#### Page 11857 - search_longtail

- Exact failure/rejection reason: `search_longtail_verifier_rejected:keyword_query_1:answer_in_title`

Route 3 generation response:

```json
{
  "answer": "Star Wars",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "Selected the directed features table and identified the film directed by George Lucas in 1977.",
  "discard_reason": null,
  "question": "What is the title of the feature film directed by George Lucas in 1977?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "George Lucas directed films 1977",
    "Star Wars director year 1977"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "What is the title of the 1977 feature film directed by George Lucas?",
  "search_queries": [
    "1977 feature film directed by George Lucas",
    "George Lucas films released in 1977"
  ]
}
```

#### Page 199445 - search_longtail

- Exact failure/rejection reason: `search_longtail_verifier_rejected:full_question:hit_rate_exceeded`

Route 3 generation response:

```json
{
  "answer": "2009–10",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "From the club appearances and goals table, the 2009–10 season shows the highest total goals scored by Wayne Rooney for Manchester United with 34 goals.",
  "discard_reason": null,
  "question": "In which season did Wayne Rooney score the most total goals for Manchester United?",
  "reasoning_type": "max",
  "search_queries": [
    "Wayne Rooney most goals season Manchester United",
    "Wayne Rooney total goals by season Manchester United"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "During which season did Wayne Rooney score the highest number of total goals for Manchester United?",
  "search_queries": [
    "Wayne Rooney highest total goals season Manchester United",
    "Wayne Rooney most goals scored in a single season for Manchester United"
  ]
}
```

#### Page 21355232 - search_longtail

- Exact failure/rejection reason: `search_longtail_verifier_rejected:full_question:hit_rate_exceeded`

Route 3 generation response:

```json
{
  "answer": "California",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "From the 'States and Territories Containing National Parks' table, California has the highest total parks count of 9, which is more than any other state or territory listed.",
  "discard_reason": null,
  "question": "Which U.S. state contains the highest total number of national parks?",
  "reasoning_type": "max",
  "search_queries": [
    "U.S. state with most national parks",
    "state containing highest number of national parks"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which U.S. state has the greatest number of national parks according to the List of national parks of the United States?",
  "search_queries": [
    "U.S. state with the highest number of national parks",
    "List of national parks of the United States by state count"
  ]
}
```

#### Page 31740 - rewrite_surface

- Exact failure/rejection reason: `rewrite_guard_rejected:cutoff_year_exceeded`

Route 3 generation response:

```json
{
  "answer": "2025–2026",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "The table 'Enrollment in University of Michigan-Ann Arbor (2013–2026)' lists total enrollment by academic year. The highest total enrollment is 53,488 in the 2025–2026 academic year.",
  "discard_reason": null,
  "question": "Which academic year had the highest total enrollment at the University of Michigan-Ann Arbor between 2013 and 2026?",
  "reasoning_type": "max",
  "search_queries": [
    "University of Michigan enrollment highest total 2013 to 2026",
    "University of Michigan Ann Arbor total enrollment by year"
  ],
  "source_table": 5
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which academic year between 2013 and 2026 had the highest total enrollment at the University of Michigan-Ann Arbor?",
  "search_queries": [
    "University of Michigan-Ann Arbor total enrollment by academic year 2013 to 2026",
    "highest total enrollment academic year University of Michigan-Ann Arbor 2013-2026"
  ]
}
```

#### Page 8083 - search_longtail

- Exact failure/rejection reason: `search_longtail_verifier_rejected:keyword_query_1:answer_in_title`

Route 3 generation response:

```json
{
  "answer": "Let Me Ride",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "From the Grammy Awards table, 'Let Me Ride' is listed as winning Best Rap Solo Performance.",
  "discard_reason": null,
  "question": "Which work won Dr. Dre the Grammy Award for Best Rap Solo Performance?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "Dr. Dre Grammy Award Best Rap Solo Performance winner",
    "Let Me Ride Grammy Award Dr. Dre"
  ],
  "source_table": 4
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which work earned Dr. Dre the Grammy Award for Best Rap Solo Performance?",
  "search_queries": [
    "Dr. Dre Grammy Award Best Rap Solo Performance work",
    "Dr. Dre Grammy win for Best Rap Solo Performance"
  ]
}
```

#### Page 292259 - search_longtail

- Exact failure/rejection reason: `search_longtail_verifier_rejected:full_question:hit_rate_exceeded`

Route 3 generation response:

```json
{
  "answer": "German",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "From the Broadcast languages table, German is listed as the language that began broadcasting in 1953.",
  "discard_reason": null,
  "question": "Which language began broadcasting on Deutsche Welle in 1953?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "Deutsche Welle first broadcast language 1953",
    "Deutsche Welle language started in 1953"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "What language started broadcasting on Deutsche Welle in 1953?",
  "search_queries": [
    "language broadcast started Deutsche Welle 1953",
    "Deutsche Welle first language broadcast 1953"
  ]
}
```

#### Page 5488 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "N'Djamena",
  "answer_aliases": [
    "N'Djamena (capital)"
  ],
  "answer_type": "Entity",
  "derivation_summary": "From the Administrative divisions table, N'Djamena (capital) has the highest population value of 1,434,592 as of 1 July 2023 among all provinces.",
  "discard_reason": null,
  "question": "Which province of Chad had the largest population on 1 July 2023?",
  "reasoning_type": "max",
  "search_queries": [
    "largest population province in Chad July 2023",
    "Chad provinces population 2023"
  ],
  "source_table": 3
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which province of Chad had the highest population on 1 July 2023?",
  "search_queries": [
    "province population Chad 1 July 2023",
    "largest population province Chad July 2023"
  ]
}
```

#### Page 1640 - search_longtail

- Exact failure/rejection reason: `search_longtail_verifier_rejected:keyword_query_1:answer_in_title`

Route 3 generation response:

```json
{
  "answer": "899",
  "answer_aliases": [],
  "answer_type": "Date",
  "derivation_summary": "The Chronology table lists Alfred the Great's death year as 899.",
  "discard_reason": null,
  "question": "What day, month, and year did Alfred the Great die?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "Alfred the Great date of death",
    "When did Alfred the Great die"
  ],
  "source_table": 3
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "On what day, month, and year did Alfred the Great die?",
  "search_queries": [
    "Alfred the Great date of death",
    "When did Alfred the Great die"
  ]
}
```

#### Page 151603 - search_longtail

- Exact failure/rejection reason: `search_longtail_verifier_rejected:keyword_query_2:answer_in_title`

Route 3 generation response:

```json
{
  "answer": "The Dean Martin Show",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "From the Television table, 'The Dean Martin Show' has 264 episodes, the highest episode count among listed programs featuring Dean Martin.",
  "discard_reason": null,
  "question": "Which television program featured Dean Martin in the most episodes?",
  "reasoning_type": "max",
  "search_queries": [
    "Dean Martin television programs episode counts",
    "Dean Martin most episodes TV show"
  ],
  "source_table": 3
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which television program had the highest number of episodes featuring Dean Martin?",
  "search_queries": [
    "Dean Martin television programs episode count",
    "TV shows with most Dean Martin appearances"
  ]
}
```

#### Page 66958 - rewrite_surface

- Exact failure/rejection reason: `rewrite_guard_rejected:cutoff_year_exceeded`

Route 3 generation response:

```json
{
  "answer": "U.S. dollar",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "From the 'Most traded currencies by value' table, the U.S. dollar had the highest proportion of daily volume at 89.2% in April 2025.",
  "discard_reason": null,
  "question": "Which currency had the highest proportion of daily volume in the global foreign exchange market turnover in April 2025?",
  "reasoning_type": "max",
  "search_queries": [
    "most traded currency by daily volume April 2025",
    "currency with highest global forex turnover April 2025"
  ],
  "source_table": 4
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which currency had the largest share of daily volume in the global foreign exchange market turnover in April 2025?",
  "search_queries": [
    "global foreign exchange market turnover currency shares April 2025",
    "currency with highest daily volume proportion in forex market April 2025"
  ]
}
```

#### Page 41853326 - rewrite_surface

- Exact failure/rejection reason: `rewrite_guard_rejected:cutoff_year_exceeded`

Route 3 generation response:

```json
{
  "answer": "Lionel Messi",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "From the 'Seasons' table, the top goalscorer for the 2025 season is listed as Lionel Messi with 43 goals.",
  "discard_reason": null,
  "question": "Which player was the top goalscorer for Inter Miami CF in the 2025 MLS season?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "Inter Miami CF 2025 top goalscorer",
    "Inter Miami CF 2025 MLS season leading scorer"
  ],
  "source_table": 10
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Who was the top goalscorer for Inter Miami CF in the 2025 MLS season?",
  "search_queries": [
    "Inter Miami CF top goalscorer 2025 MLS season",
    "2025 MLS season leading scorer Inter Miami CF"
  ]
}
```

#### Page 60382764 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "2023",
  "answer_aliases": [],
  "answer_type": "Number",
  "derivation_summary": "Used the conversion table mapping Reiwa years to AD years to find the AD year for Reiwa 5.",
  "discard_reason": null,
  "question": "What year corresponds to Reiwa 5 in the Japanese calendar?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "Reiwa 5 year conversion",
    "What year is Reiwa 5 in AD"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "What year is Reiwa 5 in the Japanese calendar?",
  "search_queries": [
    "Reiwa 5 year in Japanese calendar",
    "What Gregorian year is Reiwa 5"
  ]
}
```

#### Page 45367389 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "India",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "From the 2021 United Kingdom Census table, the country with the largest population is United Kingdom, followed by India as the second largest country of birth population in Greater London.",
  "discard_reason": null,
  "question": "Which country of birth had the second largest population in Greater London according to the 2021 United Kingdom Census?",
  "reasoning_type": "ordinal",
  "search_queries": [
    "Greater London population by country of birth 2021 census",
    "second largest foreign-born population in Greater London 2021"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "What country of birth had the second largest population in Greater London according to the 2021 United Kingdom Census?",
  "search_queries": [
    "second largest country of birth population in Greater London 2021 Census",
    "Greater London population by country of birth 2021 UK Census"
  ]
}
```

#### Page 105908 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "1974",
  "answer_aliases": [],
  "answer_type": "Number",
  "derivation_summary": "Selected the model year with the maximum US sales value from the 1970s in the sales table.",
  "discard_reason": null,
  "question": "In what model year did the Ford Mustang have the highest US sales in the 1970s?",
  "reasoning_type": "max",
  "search_queries": [
    "Ford Mustang highest US sales 1970s",
    "Ford Mustang US sales by model year 1970-1979"
  ],
  "source_table": 3
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which model year of the Ford Mustang had the highest US sales during the 1970s?",
  "search_queries": [
    "Ford Mustang highest US sales 1970s model year",
    "Ford Mustang best selling model year in 1970s US"
  ]
}
```

#### Page 34411 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "Virgo",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "From the table listing zodiac signs by house and ecliptic longitude, the sign starting at 150° is Virgo.",
  "discard_reason": null,
  "question": "What is the Latin name of the zodiac sign with the ecliptic longitude starting at 150°?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "zodiac sign ecliptic longitude 150 degrees Latin name",
    "which zodiac sign starts at 150 degrees ecliptic longitude"
  ],
  "source_table": 1
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "What is the Latin name of the zodiac sign whose ecliptic longitude begins at 150°?",
  "search_queries": [
    "zodiac sign with ecliptic longitude starting at 150 degrees Latin name",
    "name of zodiac sign beginning at 150 degrees ecliptic longitude"
  ]
}
```

#### Page 12186 - rewrite_surface

- Exact failure/rejection reason: `rewrite_guard_rejected:answer_leakage`

Route 3 generation response:

```json
{
  "answer": "Bissau",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "From the Major cities table, Bissau has the highest population of 492,004 according to the 2015 estimate.",
  "discard_reason": null,
  "question": "Which city in Guinea-Bissau had the largest population according to the 2015 estimate?",
  "reasoning_type": "max",
  "search_queries": [
    "largest city in Guinea-Bissau 2015 population",
    "Guinea-Bissau major cities population 2015"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "What city in Guinea-Bissau had the largest population according to the 2015 estimate?",
  "search_queries": [
    "largest city population in Guinea-Bissau 2015",
    "Guinea-Bissau city population estimates 2015"
  ]
}
```

#### Page 5643 - search_longtail

- Exact failure/rejection reason: `search_longtail_verifier_rejected:full_question:hit_rate_exceeded`

Route 3 generation response:

```json
{
  "answer": "Jersey",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "From the List of islands table, Jersey has the largest population of 106,080 among the Channel Islands.",
  "discard_reason": null,
  "question": "Which island in the Channel Islands has the largest population?",
  "reasoning_type": "max",
  "search_queries": [
    "population of Channel Islands islands",
    "largest population island in Channel Islands"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which island in the Channel Islands has the greatest population?",
  "search_queries": [
    "largest population island in the Channel Islands",
    "Channel Islands island with highest population"
  ]
}
```

#### Page 19653842 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "Dictyostelium",
  "answer_aliases": [
    "cellular slime mould"
  ],
  "derivation_summary": "The table lists 'Dictyostelium (cellular slime mould)' as the example for the 'Swarming protistan' level of biological organisation.",
  "discard_reason": null,
  "question": "Which example is given for the level of biological organisation called 'Swarming protistan'?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "Swarming protistan example organism",
    "Dictyostelium biological organisation level"
  ],
  "source_table": 1
}
```

Rewrite response:

```json
{
  "answer_aliases": [
    "cellular slime mould"
  ],
  "discard_reason": null,
  "rewritten_question": "What example is provided for the biological organisation level called 'Swarming protistan'?",
  "search_queries": [
    "Swarming protistan example organism",
    "biological organisation level Swarming protistan example"
  ]
}
```

#### Page 22948 - search_longtail

- Exact failure/rejection reason: `search_longtail_verifier_rejected:full_question:hit_rate_exceeded`

Route 3 generation response:

```json
{
  "answer": "Triton",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "From the 'List of offspring and their mothers' table, Triton is listed as the offspring of Poseidon with Amphitrite as the mother.",
  "discard_reason": null,
  "question": "Which offspring of Poseidon has Amphitrite as their mother?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "Poseidon offspring Amphitrite mother",
    "Poseidon children and their mothers"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which child of Poseidon has Amphitrite as their mother?",
  "search_queries": [
    "child of Poseidon with Amphitrite as mother",
    "offspring of Poseidon and Amphitrite"
  ]
}
```

#### Page 55440889 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "4G",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "From the Cellular networks table, the LTE-FDD standard is listed under the 4G generation.",
  "discard_reason": null,
  "question": "Which cellular network generation supported by Pixel 2 uses the LTE-FDD standard?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "Pixel 2 cellular network generations",
    "Pixel 2 LTE-FDD standard generation"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "What cellular network generation supported by Pixel 2 uses the LTE-FDD standard?",
  "search_queries": [
    "Pixel 2 cellular network generation LTE-FDD",
    "Pixel 2 network technology LTE-FDD standard"
  ]
}
```

#### Page 84952 - search_longtail

- Exact failure/rejection reason: `search_longtail_verifier_rejected:full_question:hit_rate_exceeded`

Route 3 generation response:

```json
{
  "answer": "Sugar Ray Leonard",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "From the professional boxing record table, the last match (No. 67) lists Sugar Ray Leonard as the opponent.",
  "discard_reason": null,
  "question": "Who was Marvelous Marvin Hagler's opponent in his last professional boxing match?",
  "reasoning_type": "ordinal",
  "search_queries": [
    "Marvelous Marvin Hagler last professional boxing match opponent",
    "Marvelous Marvin Hagler final fight opponent"
  ],
  "source_table": 3
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Who was Marvelous Marvin Hagler's opponent in his final professional boxing match?",
  "search_queries": [
    "Marvelous Marvin Hagler final professional boxing match opponent",
    "Marvelous Marvin Hagler last boxing match opponent"
  ]
}
```

#### Page 2924002 - rewrite_surface

- Exact failure/rejection reason: `rewrite_guard_rejected:cutoff_year_exceeded`

Route 3 generation response:

```json
{
  "answer": "Charli XCX",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "Selected the most recent winner of the BRIT Awards British Dance Act from the Industry awards table.",
  "discard_reason": null,
  "question": "Which artist most recently won the BRIT Awards British Dance Act in 2025?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "BRIT Awards British Dance Act winner 2025",
    "Charli XCX BRIT Awards 2025"
  ],
  "source_table": 1
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Who won the BRIT Awards British Dance Act in 2025?",
  "search_queries": [
    "BRIT Awards British Dance Act winner 2025",
    "2025 BRIT Awards British Dance Act recipient"
  ]
}
```

#### Page 30292 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "Bag End in the Shire",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "The question is derived from the 'Start' event row in the table 'Randel Helms's analysis of quest structure in The Hobbit and The Lord of the Rings', which states the quest in The Hobbit starts from Bag End in the Shire.",
  "discard_reason": null,
  "question": "What is the name of the location where the quest in The Hobbit starts?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "The Hobbit quest starting location",
    "Where does The Hobbit quest begin"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "What is the name of the place where the quest begins in The Hobbit?",
  "search_queries": [
    "starting location of the quest in The Hobbit",
    "where does the quest start in The Hobbit"
  ]
}
```

#### Page 260996 - search_longtail

- Exact failure/rejection reason: `search_longtail_verifier_rejected:full_question:hit_rate_exceeded`

Route 3 generation response:

```json
{
  "answer": "1982",
  "answer_aliases": [],
  "answer_type": "Number",
  "derivation_summary": "Selected the 'Stage' table listing Christian Slater's stage performances with years; identified the year for the play 'Macbeth' as 1982.",
  "discard_reason": null,
  "question": "In what year did Christian Slater perform in the stage play \"Macbeth\"?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "Christian Slater Macbeth stage year",
    "Christian Slater stage plays 1982"
  ],
  "source_table": 6
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "What year did Christian Slater act in the stage play Macbeth?",
  "search_queries": [
    "Christian Slater Macbeth stage play year",
    "year Christian Slater performed in Macbeth"
  ]
}
```

#### Page 235959 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "1976–1980",
  "answer_aliases": [],
  "answer_type": "Date",
  "derivation_summary": "The television table lists Farrah Fawcett's role as Jill Munroe in \"Charlie's Angels\" with the year range 1976–1980.",
  "discard_reason": null,
  "question": "In what year did Farrah Fawcett appear in the television series \"Charlie's Angels\" as Jill Munroe?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "Farrah Fawcett Charlie's Angels year",
    "Farrah Fawcett Jill Munroe television appearance year"
  ],
  "source_table": 3
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "During which years did Farrah Fawcett play Jill Munroe in the television series \"Charlie's Angels\"?",
  "search_queries": [
    "Farrah Fawcett Jill Munroe Charlie's Angels years",
    "Farrah Fawcett acting period in Charlie's Angels"
  ]
}
```

#### Page 91195 - search_longtail

- Exact failure/rejection reason: `search_longtail_verifier_rejected:full_question:hit_rate_exceeded`

Route 3 generation response:

```json
{
  "answer": "Arthur Gore",
  "answer_aliases": [
    "41 years 6 months"
  ],
  "answer_type": "Entity",
  "derivation_summary": "From the 'Miscellaneous' table, the oldest singles champion for men is Arthur Gore with an age of 41 years 6 months in 1909.",
  "discard_reason": null,
  "question": "Who is the oldest singles champion in the Wimbledon Championships and what was their age?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "oldest singles champion Wimbledon",
    "Wimbledon oldest singles winner age"
  ],
  "source_table": 8
}
```

Rewrite response:

```json
{
  "answer_aliases": [
    "41 years 6 months"
  ],
  "discard_reason": null,
  "rewritten_question": "Who holds the record as the oldest singles champion at the Wimbledon Championships and what was their age at the time?",
  "search_queries": [
    "oldest singles champion Wimbledon Championships",
    "Wimbledon Championships oldest singles winner age"
  ]
}
```

### Incremental Records

#### Page 569459 - accepted

- Exact failure/rejection reason: `accepted`

Route 3 generation response:

```json
{
  "answer": "38",
  "answer_aliases": [],
  "answer_type": "Number",
  "derivation_summary": "The infobox states that the white-tailed deer has 38 subspecies.",
  "discard_reason": null,
  "question": "How many subspecies of the white-tailed deer are there?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "number of white-tailed deer subspecies",
    "white-tailed deer subspecies count"
  ],
  "source_table": 1
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "How many subspecies does the white-tailed deer have?",
  "search_queries": [
    "number of subspecies of white-tailed deer",
    "white-tailed deer subspecies count"
  ]
}
```

#### Page 105391 - accepted

- Exact failure/rejection reason: `accepted`

Route 3 generation response:

```json
{
  "answer": "MGM",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "Selected the studio with the maximum average duration value from the 1930s film studios table.",
  "discard_reason": null,
  "question": "Which studio had the longest average film duration in the 1930s?",
  "reasoning_type": "max",
  "search_queries": [
    "1930s film studios average duration",
    "longest average film duration studio 1930s"
  ],
  "source_table": 1
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which studio had the longest average film length among B movies in the 1930s?",
  "search_queries": [
    "1930s B movie studios average film duration",
    "studio with longest average B movie length 1930s"
  ]
}
```

#### Page 342334 - accepted

- Exact failure/rejection reason: `accepted`

Route 3 generation response:

```json
{
  "answer": [
    "Mononuclear inflammatory cells",
    "Macrophages"
  ],
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "The table lists findings in stroke with their presence durations; Mononuclear inflammatory cells and Macrophages both have the longest presence duration of up to 50 years.",
  "discard_reason": null,
  "question": "Which finding in stroke can be present for the longest duration?",
  "reasoning_type": "max",
  "search_queries": [
    "longest presence finding in stroke autopsy",
    "stroke autopsy findings duration"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which stroke finding can persist for the longest duration according to autopsy?",
  "search_queries": [
    "stroke findings duration autopsy",
    "longest lasting stroke finding autopsy"
  ]
}
```

#### Page 68761 - accepted

- Exact failure/rejection reason: `accepted`

Route 3 generation response:

```json
{
  "answer": "Turkey",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "Identified the country with the maximum value in the 'Total' column of the 'Total number of titles published by sector, 2022' table.",
  "discard_reason": null,
  "question": "Which country published the highest total number of titles in 2022?",
  "reasoning_type": "max",
  "search_queries": [
    "country with highest total number of published titles 2022",
    "total book titles published by country 2022"
  ],
  "source_table": 1
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which country published the greatest total number of titles in 2022?",
  "search_queries": [
    "country with highest number of published titles in 2022",
    "2022 publishing statistics by country total titles"
  ]
}
```

#### Page 246920 - accepted

- Exact failure/rejection reason: `accepted`

Route 3 generation response:

```json
{
  "answer": "2024",
  "answer_aliases": [],
  "answer_type": "Number",
  "derivation_summary": "The Finance table lists Visa Inc.'s net income in million US$ by year from 2005 to 2024. The highest net income value is 19,743 million US$ in 2024.",
  "discard_reason": null,
  "question": "In what year did Visa Inc. have the highest net income in million US$ according to the Finance table?",
  "reasoning_type": "max",
  "search_queries": [
    "Visa Inc. highest net income year",
    "Visa Inc. net income by year"
  ],
  "source_table": 3
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "What year did Visa Inc. record its highest net income in million US dollars according to the Finance table?",
  "search_queries": [
    "Visa Inc highest net income year Finance table",
    "Visa Inc peak net income million US dollars year"
  ]
}
```

#### Page 2114995 - accepted

- Exact failure/rejection reason: `accepted`

Route 3 generation response:

```json
{
  "answer": "SERT Tooltip Serotonin transporter",
  "answer_aliases": [
    "Serotonin transporter"
  ],
  "answer_type": "Entity",
  "derivation_summary": "From the pharmacodynamics table, the site with the lowest K i range for DXM in rats is the Serotonin transporter (SERT) with 23–40 nM, which is lower than other listed sites.",
  "discard_reason": null,
  "question": "At which site does dextromethorphan (DXM) have the lowest K i binding value range in rats?",
  "reasoning_type": "min",
  "search_queries": [
    "dextromethorphan binding affinity lowest Ki rat",
    "dextromethorphan pharmacodynamics serotonin transporter"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [
    "Serotonin transporter"
  ],
  "discard_reason": null,
  "rewritten_question": "At which site does dextromethorphan (DXM) exhibit the lowest K i binding value range in rats?",
  "search_queries": [
    "dextromethorphan DXM lowest Ki binding site in rats",
    "dextromethorphan binding affinity Ki values rat brain sites"
  ]
}
```

#### Page 96875 - accepted

- Exact failure/rejection reason: `accepted`

Route 3 generation response:

```json
{
  "answer": "1924",
  "answer_aliases": [],
  "answer_type": "Number",
  "derivation_summary": "The passenger services table lists passenger numbers for various years; 1924 has the highest passenger count of 140,241,113.",
  "discard_reason": null,
  "question": "In what year did the Great Western Railway carry the highest number of passengers according to the passenger services data?",
  "reasoning_type": "max",
  "search_queries": [
    "Great Western Railway passenger numbers by year",
    "Great Western Railway highest passenger year"
  ],
  "source_table": 4
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "What year did the Great Western Railway carry the greatest number of passengers according to passenger services data?",
  "search_queries": [
    "Great Western Railway highest passenger numbers year",
    "Great Western Railway passenger services max passengers year"
  ]
}
```

#### Page 1625048 - accepted

- Exact failure/rejection reason: `accepted`

Route 3 generation response:

```json
{
  "answer": "Budweis",
  "answer_aliases": [
    "Budějovice"
  ],
  "answer_type": "Entity",
  "derivation_summary": "From the 1910 language distribution by district table, Budweis (Budějovice) has the largest population of 120,659 among all listed districts.",
  "discard_reason": null,
  "question": "Which district had the largest population in the Kingdom of Bohemia according to the 1910 language distribution by district?",
  "reasoning_type": "max",
  "search_queries": [
    "largest population district Kingdom of Bohemia 1910",
    "district population 1910 Kingdom of Bohemia"
  ],
  "source_table": 5
}
```

Rewrite response:

```json
{
  "answer_aliases": [
    "Budějovice"
  ],
  "discard_reason": null,
  "rewritten_question": "Which district had the highest population in the Kingdom of Bohemia according to the 1910 language distribution by district?",
  "search_queries": [
    "1910 language distribution by district Kingdom of Bohemia largest population district",
    "district with largest population in Kingdom of Bohemia 1910 language distribution"
  ]
}
```

#### Page 57905 - accepted

- Exact failure/rejection reason: `accepted`

Route 3 generation response:

```json
{
  "answer": "1985",
  "answer_aliases": [],
  "answer_type": "Number",
  "derivation_summary": "The year 1985 has the highest value in the 'Live births' column with 22,823 live births in the vital statistics table.",
  "discard_reason": null,
  "question": "In what year did the Sakha Republic have the highest number of live births according to the vital statistics?",
  "reasoning_type": "max",
  "search_queries": [
    "Sakha Republic live births by year",
    "year with highest live births in Sakha Republic"
  ],
  "source_table": 4
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "What year saw the highest number of live births in the Sakha Republic according to vital statistics?",
  "search_queries": [
    "Sakha Republic highest number of live births year",
    "Sakha Republic vital statistics peak live births year"
  ]
}
```

#### Page 67923 - accepted

- Exact failure/rejection reason: `accepted`

Route 3 generation response:

```json
{
  "answer": "11576",
  "answer_aliases": [],
  "answer_type": "Number",
  "derivation_summary": "Selected the gross value added for the year 2023 from the Economy and demography table showing yearly values.",
  "discard_reason": null,
  "question": "What was the gross value added in East Sussex in the year 2023 in million pounds?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "East Sussex gross value added 2023",
    "East Sussex economy gross value added 2023"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "What was the gross value added in East Sussex in million pounds in 2023?",
  "search_queries": [
    "gross value added East Sussex 2023 million pounds",
    "East Sussex GVA 2023 value in million pounds"
  ]
}
```

#### Page 1161220 - accepted

- Exact failure/rejection reason: `accepted`

Route 3 generation response:

```json
{
  "answer": "28.99",
  "answer_aliases": [],
  "answer_type": "Number",
  "derivation_summary": "Extracted the vote percentage value for Khushbu Sundar from the 2021 Tamil Nadu assembly election table for the Thousand Lights constituency.",
  "discard_reason": null,
  "question": "What was the vote percentage received by Khushbu Sundar in the 2021 Tamil Nadu assembly election for the Thousand Lights constituency?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "Khushbu Sundar 2021 Tamil Nadu assembly election vote percentage Thousand Lights",
    "2021 Tamil Nadu assembly election Thousand Lights constituency results"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "What percentage of votes did Khushbu Sundar receive in the 2021 Tamil Nadu assembly election for the Thousand Lights constituency?",
  "search_queries": [
    "Khushbu Sundar vote percentage 2021 Tamil Nadu assembly election Thousand Lights",
    "2021 Tamil Nadu assembly election Thousand Lights constituency Khushbu Sundar votes"
  ]
}
```

#### Page 17278765 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "Alabama",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "From the 'Poll era national championships by school (1936–present)' table, Alabama has the highest number of titles with 13.",
  "discard_reason": null,
  "question": "Which school has won the most national championships in the poll era from 1936 to present?",
  "reasoning_type": "max",
  "search_queries": [
    "most national championships NCAA Division I FBS poll era",
    "school with most college football national titles since 1936"
  ],
  "source_table": 9
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which school has the highest number of College football national championships in NCAA Division I FBS during the poll era from 1936 to present?",
  "search_queries": [
    "College football national championships NCAA Division I FBS poll era most titles",
    "School with most College football national championships in NCAA Division I FBS since 1936"
  ]
}
```

#### Page 229275 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "China",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "Identified the country with the maximum sheep meat production value in 2012 from the 'Sheep meat production (kt)' table.",
  "discard_reason": null,
  "question": "Which country had the highest sheep meat production in 2012?",
  "reasoning_type": "max",
  "search_queries": [
    "highest sheep meat production by country 2012",
    "top sheep meat producing country 2012"
  ],
  "source_table": 1
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which country produced the most lamb and mutton in 2012?",
  "search_queries": [
    "2012 lamb and mutton production by country",
    "country with highest sheep meat production 2012"
  ]
}
```

#### Page 156745 - search_longtail

- Exact failure/rejection reason: `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded`

Route 3 generation response:

```json
{
  "answer": "Julia Roberts",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "From the Accolades table, Julia Roberts won the Golden Globe Award for Best Actress in a Motion Picture – Musical or Comedy for Pretty Woman.",
  "discard_reason": null,
  "question": "Which actress won the Golden Globe Award for Best Actress in a Motion Picture – Musical or Comedy for Pretty Woman?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "Pretty Woman Golden Globe Best Actress winner",
    "Julia Roberts Golden Globe awards Pretty Woman"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Who won the Golden Globe Award for Best Actress in a Motion Picture – Musical or Comedy for Pretty Woman?",
  "search_queries": [
    "Golden Globe Award Best Actress Musical or Comedy Pretty Woman winner",
    "Pretty Woman Golden Globe Best Actress Musical or Comedy"
  ]
}
```

#### Page 599 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "Akkadian",
  "answer_aliases": [
    "Akkadian (Semitic)"
  ],
  "answer_type": "Entity",
  "derivation_summary": "The table 'The \"prefix conjugation\" in Afroasiatic, following Gragg 2019' shows that the prefix conjugation form 'a-parras' for singular first person corresponds to Akkadian (Semitic).",
  "discard_reason": null,
  "question": "Which Afroasiatic language uses the prefix conjugation form 'a-parras' for the singular first person?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "Afroasiatic prefix conjugation singular first person a-parras",
    "language with prefix conjugation a-parras singular 1st person"
  ],
  "source_table": 12
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which Afroasiatic language uses the prefix conjugation form 'a-parras' for the first person singular?",
  "search_queries": [
    "Afroasiatic language prefix conjugation a-parras first person singular",
    "language in Afroasiatic family with prefix conjugation form a-parras singular first person"
  ]
}
```

#### Page 151451 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "Can't Stop, Won't Stop: A Bad Boy Story",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "Selected the documentary table and identified the documentary title corresponding to the year 2017.",
  "discard_reason": null,
  "question": "What is the title of the documentary released in 2017 featuring Busta Rhymes?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "Busta Rhymes 2017 documentary title",
    "documentary featuring Busta Rhymes released in 2017"
  ],
  "source_table": 5
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "What is the title of the 2017 documentary that features Busta Rhymes?",
  "search_queries": [
    "2017 documentary featuring Busta Rhymes",
    "Busta Rhymes documentary title 2017"
  ]
}
```

#### Page 7549995 - search_longtail

- Exact failure/rejection reason: `search_longtail_verifier_rejected:full_question:hit_rate_exceeded`

Route 3 generation response:

```json
{
  "answer": "Colorado",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "Identified the state with the maximum estimated number of elk from the 'U.S. states by estimated elk population' table.",
  "discard_reason": null,
  "question": "Which U.S. state has the largest estimated elk population?",
  "reasoning_type": "max",
  "search_queries": [
    "U.S. state with largest elk population",
    "state with most elk in United States"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which U.S. state has the largest estimated population of elk?",
  "search_queries": [
    "U.S. state with largest elk population",
    "state with highest estimated elk numbers in the U.S."
  ]
}
```

#### Page 43088 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "1964",
  "answer_aliases": [],
  "answer_type": "Number",
  "derivation_summary": "From the managerial record table, the year 1964 with the New York Yankees shows the highest regular season winning percentage of .611 among all listed years.",
  "discard_reason": null,
  "question": "In which year did Yogi Berra have the highest regular season winning percentage as a manager?",
  "reasoning_type": "max",
  "search_queries": [
    "Yogi Berra managerial record highest winning percentage year",
    "Yogi Berra best regular season win percentage as manager"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "What year did Yogi Berra achieve his highest regular season winning percentage as a manager?",
  "search_queries": [
    "Yogi Berra highest regular season winning percentage year as manager",
    "Year Yogi Berra had best regular season winning percentage managing"
  ]
}
```

#### Page 47864412 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "West Bengal",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "Identified the state with the maximum number of Nepali speakers from the 2011 census data in the 'Nepali speakers in India by state' table.",
  "discard_reason": null,
  "question": "Which state in India had the highest number of Nepali speakers according to the 2011 census?",
  "reasoning_type": "max",
  "search_queries": [
    "Nepali speakers by Indian state 2011 census",
    "state with most Nepali speakers in India 2011"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which Indian state had the highest number of Nepali language speakers according to the 2011 census?",
  "search_queries": [
    "Indian states by number of Nepali speakers 2011 census",
    "2011 census data Nepali language speakers by Indian state"
  ]
}
```

#### Page 26457880 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "2023-24",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "The business trends table lists the number of passengers in millions for each year. The maximum value is 39.49 million in 2023-24.",
  "discard_reason": null,
  "question": "In which year did Air India have the highest number of passengers in millions according to the business trends data?",
  "reasoning_type": "max",
  "search_queries": [
    "Air India number of passengers by year",
    "Air India passenger statistics highest year"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "What year did Air India record the highest number of passengers in millions according to the business trends data?",
  "search_queries": [
    "Air India highest passenger numbers by year business trends",
    "Air India annual passenger statistics peak year"
  ]
}
```

#### Page 31730 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "Army and Gurkhas",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "Compared the 'Total' personnel numbers across the Navy, Army and Gurkhas, and Air Force; Army and Gurkhas has the highest total personnel count of 109,060.",
  "discard_reason": null,
  "question": "Which service branch of the British Armed Forces has the highest total number of personnel?",
  "reasoning_type": "max",
  "search_queries": [
    "British Armed Forces personnel by service branch",
    "largest British Armed Forces service branch by total personnel"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which branch of the British Armed Forces has the largest total number of personnel?",
  "search_queries": [
    "British Armed Forces personnel numbers by service branch",
    "service branch with highest personnel in British Armed Forces"
  ]
}
```

#### Page 18947898 - search_longtail

- Exact failure/rejection reason: `search_longtail_verifier_rejected:full_question:answer_in_title`

Route 3 generation response:

```json
{
  "answer": "Pierre Sané",
  "answer_aliases": [
    "Pierre Sané"
  ],
  "answer_type": "Entity",
  "derivation_summary": "Selected the Secretary General who held office from 1992 to 2001 from the Amnesty International Secretaries General table.",
  "discard_reason": null,
  "question": "Who was the Secretary General of Amnesty International from 1992 to 2001?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "Amnesty International Secretary General 1992 to 2001",
    "Amnesty International leaders 1990s"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Who served as Secretary General of Amnesty International from 1992 to 2001?",
  "search_queries": [
    "Secretary General of Amnesty International 1992 to 2001",
    "Amnesty International leaders 1992-2001"
  ]
}
```

#### Page 80482 - search_longtail

- Exact failure/rejection reason: `search_longtail_verifier_rejected:keyword_query_1:answer_in_title`

Route 3 generation response:

```json
{
  "answer": "Ruud Lubbers",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "Calculated the longest continuous term by subtracting start year from end year for each Prime Minister during Beatrix's reign; Ruud Lubbers served from 1982 to 1994, the longest continuous period.",
  "discard_reason": null,
  "question": "Which Prime Minister served the longest continuous term during Beatrix of the Netherlands' reign?",
  "reasoning_type": "max",
  "search_queries": [
    "longest serving Prime Minister during Beatrix of the Netherlands reign",
    "Prime Minister with longest term 1980 to 2013 Netherlands"
  ],
  "source_table": 4
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Who was the Prime Minister with the longest continuous term during the reign of Beatrix of the Netherlands?",
  "search_queries": [
    "Prime Ministers longest continuous term during Beatrix of the Netherlands reign",
    "Beatrix of the Netherlands reign Prime Minister longest serving"
  ]
}
```

#### Page 32005912 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "2021",
  "answer_aliases": [],
  "answer_type": "Number",
  "derivation_summary": "Selected the year Grimes appeared as a judge in Alter Ego from the Film and television credits table.",
  "discard_reason": null,
  "question": "In what year did Grimes appear as a judge in the television series Alter Ego?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "Grimes Alter Ego judge year",
    "Grimes television appearances 2021"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "What year did Grimes serve as a judge on the television series Alter Ego?",
  "search_queries": [
    "Grimes judge television series Alter Ego year",
    "year Grimes appeared as judge on Alter Ego"
  ]
}
```

#### Page 214179 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": [
    "Jeff Ward",
    "Chris Connelly"
  ],
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "From the 'Additional/touring musicians' table, identified musicians who contributed to the 1989 release 'The Mind Is a Terrible Thing to Taste'. Both Jeff Ward and Chris Connelly are listed with this release contribution.",
  "discard_reason": null,
  "question": "Which additional/touring musician contributed to the release 'The Mind Is a Terrible Thing to Taste' in 1989?",
  "reasoning_type": "comparison",
  "search_queries": [
    "Ministry band additional musicians The Mind Is a Terrible Thing to Taste 1989",
    "Ministry band touring members release contributions 1989"
  ],
  "source_table": 4
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which additional or touring musicians contributed to Ministry (band)'s 1989 release 'The Mind Is a Terrible Thing to Taste'?",
  "search_queries": [
    "Ministry band The Mind Is a Terrible Thing to Taste 1989 additional musicians",
    "Ministry 1989 album The Mind Is a Terrible Thing to Taste touring contributors"
  ]
}
```

#### Page 57877 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "9.95",
  "answer_aliases": [],
  "answer_type": "Number",
  "derivation_summary": "Selected the molar concentration value corresponding to 30 wt% mass fraction of NaOH from the Saponification table.",
  "discard_reason": null,
  "question": "What is the molar concentration of sodium hydroxide at a 30 wt% mass fraction?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "molar concentration of sodium hydroxide at 30 percent mass fraction",
    "NaOH molar concentration 30 wt percent"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "What is the molar concentration of sodium hydroxide when its mass fraction is 30 wt%?",
  "search_queries": [
    "molar concentration of sodium hydroxide at 30 wt% mass fraction",
    "sodium hydroxide 30 wt% molarity"
  ]
}
```

#### Page 407239 - search_longtail

- Exact failure/rejection reason: `search_longtail_verifier_rejected:full_question:hit_rate_exceeded`

Route 3 generation response:

```json
{
  "answer": "Mumbai",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "From the 'Circulation in major cities' table, Mumbai has the highest approximate daily circulation of 160,000 among listed cities.",
  "discard_reason": null,
  "question": "Which city has the highest approximate daily circulation of The Indian Express?",
  "reasoning_type": "max",
  "search_queries": [
    "The Indian Express circulation by city",
    "city with highest daily circulation of The Indian Express"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which city has the highest approximate daily circulation of The Indian Express?",
  "search_queries": [
    "city with highest daily circulation of The Indian Express",
    "The Indian Express daily circulation by city"
  ]
}
```

#### Page 57659 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "Ettadhamen-Mnihla",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "From the Suburbs table, Ettadhamen-Mnihla has the highest population value of 118,487 in 2004 among listed suburbs.",
  "discard_reason": null,
  "question": "Which suburb of Tunis had the largest population in 2004?",
  "reasoning_type": "max",
  "search_queries": [
    "largest suburb population Tunis 2004",
    "Tunis suburb population statistics 2004"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which suburb of Tunis had the highest population in 2004?",
  "search_queries": [
    "suburbs of Tunis population 2004",
    "largest population suburb of Tunis 2004"
  ]
}
```

#### Page 76988 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "Hilbert–Huang transform",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "Selected a single fact lookup question from the 'Time-frequency analysis in ECG signal processing' table about the method suitable for fully non-stationary and nonlinear signals with instantaneous frequency distribution.",
  "discard_reason": null,
  "question": "Which time-frequency analysis method in ECG signal processing is suitable for fully non-stationary and nonlinear signals and provides instantaneous frequency distribution?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "time-frequency analysis methods in ECG signal processing",
    "ECG signal processing methods for non-stationary signals"
  ],
  "source_table": 7
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "What time-frequency analysis method in electrocardiography is suitable for fully non-stationary and nonlinear signals and provides instantaneous frequency distribution?",
  "search_queries": [
    "time-frequency analysis methods for non-stationary nonlinear ECG signals",
    "instantaneous frequency distribution methods in electrocardiography"
  ]
}
```

#### Page 15049 - search_longtail

- Exact failure/rejection reason: `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded`

Route 3 generation response:

```json
{
  "answer": "2010",
  "answer_aliases": [],
  "answer_type": "Number",
  "derivation_summary": "Selected the induction year of Tony Dungy from the Indianapolis Colts Ring of Honor table.",
  "discard_reason": null,
  "question": "What year was Tony Dungy inducted into the Indianapolis Colts Ring of Honor?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "Tony Dungy Indianapolis Colts Ring of Honor induction year",
    "Indianapolis Colts Ring of Honor inductees and years"
  ],
  "source_table": 5
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "In what year was Tony Dungy inducted into the Indianapolis Colts Ring of Honor?",
  "search_queries": [
    "Tony Dungy Indianapolis Colts Ring of Honor induction year",
    "Year Tony Dungy entered Indianapolis Colts Ring of Honor"
  ]
}
```

#### Page 1064 - search_longtail

- Exact failure/rejection reason: `search_longtail_verifier_rejected:keyword_query_1:answer_in_title`

Route 3 generation response:

```json
{
  "answer": "United States",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "The table 'Almonds production 2023, tonnes' lists almond production by country, with the United States having the highest production at 1,791,690 tonnes.",
  "discard_reason": null,
  "question": "Which country produced the most almonds in 2023 in tonnes?",
  "reasoning_type": "max",
  "search_queries": [
    "almond production by country 2023",
    "top almond producing country 2023"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which country was the largest producer of almonds in 2023 measured in tonnes?",
  "search_queries": [
    "almond production by country 2023 tonnes",
    "top almond producing countries 2023"
  ]
}
```

#### Page 35412202 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "29 October 2012",
  "answer_aliases": [],
  "answer_type": "Date",
  "derivation_summary": "Extracted the launch date of Wikidata from the infobox row labeled 'Launched'.",
  "discard_reason": null,
  "question": "What day, month, and year was Wikidata launched?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "Wikidata launch date",
    "When was Wikidata launched"
  ],
  "source_table": 1
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "What day, month, and year did Wikidata launch?",
  "search_queries": [
    "Wikidata launch date",
    "When was Wikidata launched"
  ]
}
```

#### Page 2209490 - rewrite_surface

- Exact failure/rejection reason: `rewrite_guard_rejected:answer_leakage`

Route 3 generation response:

```json
{
  "answer": "ج",
  "answer_aliases": [
    "jīm"
  ],
  "answer_type": "Entity",
  "derivation_summary": "Selected a single fact lookup from the Comparison table identifying the Arabic letter with Unicode 062C and its ALA name 'jīm'.",
  "discard_reason": null,
  "question": "Which Arabic letter has the Unicode value 062C and is named 'jīm' in the ALA romanization system?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "Arabic letter Unicode 062C",
    "ALA romanization name for Arabic letter 062C"
  ],
  "source_table": 1
}
```

Rewrite response:

```json
{
  "answer_aliases": [
    "jīm"
  ],
  "discard_reason": null,
  "rewritten_question": "Which Arabic letter corresponds to the Unicode value 062C and is called 'jīm' in the Romanization of Arabic?",
  "search_queries": [
    "Arabic letter Unicode 062C jīm Romanization",
    "Unicode 062C Arabic letter name jīm Romanization of Arabic"
  ]
}
```

#### Page 129619 - search_longtail

- Exact failure/rejection reason: `search_longtail_verifier_rejected:keyword_query_2:answer_in_title`

Route 3 generation response:

```json
{
  "answer": "Whoopi Goldberg",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "The Accolades table shows Whoopi Goldberg won multiple Best Supporting Actress awards for Ghost.",
  "discard_reason": null,
  "question": "Which actress won the Best Supporting Actress award for the film Ghost?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "Ghost 1990 Best Supporting Actress award winner",
    "Who won Best Supporting Actress for Ghost 1990"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Who won the Best Supporting Actress award for the film Ghost (1990)?",
  "search_queries": [
    "Best Supporting Actress award winner Ghost 1990 film",
    "Who won Best Supporting Actress for Ghost 1990 movie"
  ]
}
```

#### Page 23906 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "215700",
  "answer_aliases": [],
  "answer_type": "Number",
  "derivation_summary": "Extracted the population value for the city of Peterborough in the year 2021 from the Population table.",
  "discard_reason": null,
  "question": "What was the population of the city of Peterborough in the year 2021?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "Peterborough population 2021",
    "Peterborough city population by year"
  ],
  "source_table": 2
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "What was the population of Peterborough in 2021?",
  "search_queries": [
    "Peterborough population 2021",
    "population of Peterborough city in 2021"
  ]
}
```

#### Page 422038 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "Venezuela",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "Selected the country with the maximum population value from the 'Foreign population by country of birth (2024)' table.",
  "discard_reason": null,
  "question": "Which country has the largest foreign-born population in Vigo in 2024?",
  "reasoning_type": "max",
  "search_queries": [
    "largest foreign-born population in Vigo 2024 by country",
    "foreign population by country of birth Vigo 2024"
  ],
  "source_table": 3
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which country had the largest foreign-born population in Vigo in 2024?",
  "search_queries": [
    "largest foreign-born population by country in Vigo 2024",
    "foreign-born population statistics Vigo 2024 by country"
  ]
}
```

#### Page 540317 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "2000",
  "answer_aliases": [],
  "answer_type": "Number",
  "derivation_summary": "The sales table lists yearly US sales of the Ford Explorer; the maximum sales value is 445,157 in the year 2000.",
  "discard_reason": null,
  "question": "In which calendar year did the Ford Explorer have the highest US sales?",
  "reasoning_type": "max",
  "search_queries": [
    "Ford Explorer US sales by year",
    "Ford Explorer highest sales year"
  ],
  "source_table": 21
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "What calendar year saw the highest US sales for the Ford Explorer?",
  "search_queries": [
    "Ford Explorer highest US sales year",
    "Ford Explorer peak US sales calendar year"
  ]
}
```

#### Page 47498 - search_longtail

- Exact failure/rejection reason: `search_longtail_verifier_rejected:keyword_query_2:answer_in_title`

Route 3 generation response:

```json
{
  "answer": "All your base are belong to us",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "The table shows the English version (1991) of the Zero Wing transcript, where the phrase 'All your base are belong to us' appears as a key line.",
  "discard_reason": null,
  "question": "What is the English phrase from the 1991 version of Zero Wing that became an internet meme?",
  "reasoning_type": "single_fact",
  "search_queries": [
    "Zero Wing 1991 English version meme phrase",
    "All your base are belong to us origin"
  ],
  "source_table": 1
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "What English phrase from the 1991 version of Zero Wing became an internet meme?",
  "search_queries": [
    "1991 Zero Wing English meme phrase",
    "internet meme phrase from 1991 Zero Wing"
  ]
}
```

#### Page 113933 - second_stage_grading

- Exact failure/rejection reason: `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1`

Route 3 generation response:

```json
{
  "answer": "University of Iowa Hospitals & Clinics",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "Selected the employer with the maximum number of employees from the 'Top employers' table.",
  "discard_reason": null,
  "question": "Which employer had the highest number of employees in Iowa City according to the top employers list?",
  "reasoning_type": "max",
  "search_queries": [
    "largest employer in Iowa City by number of employees",
    "top employers in Iowa City employee count"
  ],
  "source_table": 5
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which employer had the largest number of employees in Iowa City according to the top employers list?",
  "search_queries": [
    "top employers by number of employees in Iowa City Iowa",
    "largest employer in Iowa City Iowa by employee count"
  ]
}
```

#### Page 22461 - search_longtail

- Exact failure/rejection reason: `search_longtail_verifier_rejected:keyword_query_1:answer_in_title`

Route 3 generation response:

```json
{
  "answer": "Osteoporosis",
  "answer_aliases": [],
  "answer_type": "Entity",
  "derivation_summary": "Selected the WHO category with the maximum value in the 'Overall' column for hip fractures per 1000 person-years.",
  "discard_reason": null,
  "question": "Which WHO category has the highest overall rate of hip fractures per 1000 person-years?",
  "reasoning_type": "max",
  "search_queries": [
    "WHO category hip fracture rates per 1000 person-years",
    "hip fracture rates by WHO category osteoporosis osteopenia normal"
  ],
  "source_table": 4
}
```

Rewrite response:

```json
{
  "answer_aliases": [],
  "discard_reason": null,
  "rewritten_question": "Which WHO category has the highest rate of hip fractures per 1000 person-years?",
  "search_queries": [
    "WHO categories hip fracture rates per 1000 person-years",
    "hip fracture incidence by WHO category"
  ]
}
```


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

### Incremental Records

| Page ID | Stage | Exact reason | Page/question |
| ---: | --- | --- | --- |
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


