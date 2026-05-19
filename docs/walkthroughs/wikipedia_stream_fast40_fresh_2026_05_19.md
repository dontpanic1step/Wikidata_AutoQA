# Route 3 Streaming Wikipedia Page-ID Walkthrough - 2026-05-19

## Stats

- Mode: `page_id_stream`
- Page source: `table-search`
- Table-search queries: `insource:"wikitable"`
- Attempted page IDs: 40
- Accepted QAs: 5
- Rejected QAs/pages: 35
- Returned to rerun pool without final decision: 0
- Wall-clock runtime: 832.1680s
- DuckDuckGo top K: 5
- Generated search queries per QA: 2
- DuckDuckGo parallel queries: 3
- Page-id bounds: 1 to 80000000
- Stream state: `outputs\wikipedia_stream_fast40_fresh_2026_05_19_state.json`
- Accepted output: `outputs\wikipedia_stream_fast40_2026_05_19_accepted.jsonl`
- Rejected output: `outputs\wikipedia_stream_fast40_2026_05_19_rejected.jsonl`
- Domain policy: `domain_and_subdomain_optional_for_page_id_streaming`
- Rerun pool after run: `empty`

### Survival By Layer

| Layer | Entered | Failed | Survived | Layer survival | Cumulative survival |
| --- | ---: | ---: | ---: | ---: | ---: |
| Page-id reservation | 40 | 0 | 40 | 100.0% | 100.0% |
| Unresolved or returned to rerun pool | 40 | 0 | 40 | 100.0% | 100.0% |
| Page extraction, table grading, and QA generation | 40 | 0 | 40 | 100.0% | 100.0% |
| Rewrite and surface validation | 40 | 5 | 35 | 87.5% | 87.5% |
| DuckDuckGo long-tail filtering | 35 | 16 | 19 | 54.3% | 47.5% |
| Second-stage model grading | 19 | 14 | 5 | 26.3% | 12.5% |
| Shared route-aware validation | 5 | 0 | 5 | 100.0% | 12.5% |
| Deduplication | 5 | 0 | 5 | 100.0% | 12.5% |
| Other rejection | 5 | 0 | 5 | 100.0% | 12.5% |

### Failure Reasons

| Stage | Exact reason | Count |
| --- | --- | ---: |
| `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | 12 |
| `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | 7 |
| `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=1.0;threshold=0.1` | 7 |
| `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | 4 |
| `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | 3 |
| `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | 1 |
| `search_longtail` | `search_longtail_verifier_rejected:keyword_query_2:answer_in_title` | 1 |

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
| `candidate_processing_seconds` | 40 | 544.3788 | 13.6095 | 35.9131 |
| `duckduckgo_search_seconds` | 35 | 125.3265 | 3.5808 | 7.0719 |
| `first_paragraph_extract_seconds` | 40 | 7.3794 | 0.1845 | 0.3653 |
| `llm_question_generation_seconds` | 40 | 174.8260 | 4.3706 | 7.9092 |
| `number_reference_margin_seconds` | 35 | 0.0000 | 0.0000 | 0.0000 |
| `page_fetch_seconds` | 40 | 90.1757 | 2.2544 | 8.6836 |
| `rewrite_seconds` | 40 | 150.1641 | 3.7541 | 33.2139 |
| `second_stage_grading_seconds` | 19 | 268.8414 | 14.1495 | 23.4871 |
| `table_parse_seconds` | 40 | 12.9148 | 0.3229 | 0.7539 |
| `total_generation_seconds` | 40 | 287.0777 | 7.1769 | 12.7030 |
| `total_processing_seconds` | 40 | 544.3788 | 13.6095 | 35.9131 |

## Accepted Candidates

| Page ID | Question | Answer | Source |
| ---: | --- | --- | --- |
| 40010153 | What year saw the highest number of tourist arrivals in Goa? | 2015 | https://en.wikipedia.org/wiki/Goa |
| 39776 | Which protocol has the maximum amplification factor in UDP-based amplification denial-of-service attacks? | Mitel MiCollab | https://en.wikipedia.org/wiki/Denial-of-service_attack |
| 217231 | Which seasons of Curb Your Enthusiasm have a 100% rating on Rotten Tomatoes? | 2; 3; 5 | https://en.wikipedia.org/wiki/Curb_Your_Enthusiasm |
| 235916 | In which films did Jada Pinkett Smith voice the character Gloria? | Madagascar; Madagascar: Escape 2 Africa; Madagascar 3: Europe's Most Wanted; Penguins of Madagascar | https://en.wikipedia.org/wiki/Jada_Pinkett_Smith |
| 33094374 | Which equipment had the highest worldwide sales in the year 2008? | Cell phones | https://en.wikipedia.org/wiki/Telecommunications |

## Second-Stage Filtering Responses

These are the small-model QA responses used by the second-stage filter: `openai/gpt-4.1-mini` and `google/gemini-3-flash-preview`. Route 3 generation and rewrite outputs are listed separately below.

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


## Route 3 Generation Responses

These are the source-page QA generation and rewrite responses, not the second-stage small-model QA panel.

### Page 40010153 - accepted

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

### Page 39776 - accepted

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

### Page 217231 - accepted

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

### Page 235916 - accepted

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

### Page 33094374 - accepted

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

### Page 32611 - second_stage_grading

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

### Page 17416221 - search_longtail

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

### Page 9316 - search_longtail

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

### Page 22093 - second_stage_grading

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

### Page 5489 - second_stage_grading

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

### Page 738 - search_longtail

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

### Page 13277 - second_stage_grading

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

### Page 14849 - second_stage_grading

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

### Page 19261 - search_longtail

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

### Page 11857 - search_longtail

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

### Page 199445 - search_longtail

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

### Page 21355232 - search_longtail

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

### Page 31740 - rewrite_surface

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

### Page 8083 - search_longtail

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

### Page 292259 - search_longtail

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

### Page 5488 - second_stage_grading

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

### Page 1640 - search_longtail

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

### Page 151603 - search_longtail

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

### Page 66958 - rewrite_surface

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

### Page 41853326 - rewrite_surface

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

### Page 60382764 - second_stage_grading

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

### Page 45367389 - second_stage_grading

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

### Page 105908 - second_stage_grading

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

### Page 34411 - second_stage_grading

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

### Page 12186 - rewrite_surface

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

### Page 5643 - search_longtail

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

### Page 19653842 - second_stage_grading

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

### Page 22948 - search_longtail

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

### Page 55440889 - second_stage_grading

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

### Page 84952 - search_longtail

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

### Page 2924002 - rewrite_surface

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

### Page 30292 - second_stage_grading

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

### Page 260996 - search_longtail

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

### Page 235959 - second_stage_grading

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

### Page 91195 - search_longtail

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


## Rejected And Rerun Decisions

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


