# Route 3 Streaming Wikipedia Page-ID Walkthrough - 2026-05-22

## Stats

- Run group ID: `wikipedia_stream_recipe_40_each_answer_type_single_fact_2026_05_22_network`
- Run segment ID: `recipe_combined`
- Artifact manifest: ``
- Mode: `page_id_stream_recipe`
- Page source: `table-search`
- Table-search queries: `insource:"wikitable"`
- Attempted page IDs: 223
- Unique attempted page IDs: 40
- Stream state reset at run start: yes
- Auto rerun pool once: yes
- Auto-rerun attempted page IDs: 0
- Accepted QAs: 16
- Rejected QAs/pages: 182
- Transient rerun attempts during run: 25
- Wall-clock runtime: 1976.6681s
- DuckDuckGo top K: 5
- Generated search queries per QA: 3
- DuckDuckGo parallel queries: 3
- Route 3 reasoning_type constraint: `single_fact`
- Route 3 answer_type constraint: `Person, Place, Other, Date, Number`
- Route 3 table filter modes: `no_big_numbers, no_social_science_research`
- Page-id bounds: None to None
- Stream state: `separate_segment_stream_states`
- Accepted output: `D:\Study\AI\My-research\Wikidata_Framework\outputs\wikipedia_stream_recipe_40_each_answer_type_single_fact_2026_05_22_network_accepted.jsonl`
- Rejected output: `D:\Study\AI\My-research\Wikidata_Framework\outputs\wikipedia_stream_recipe_40_each_answer_type_single_fact_2026_05_22_network_rejected.jsonl`
- Domain policy: `domain_and_subdomain_optional_for_page_id_streaming`
- Rerun pool after run: `1640, 41853326`

### Recipe Segments

| Configured answer_type | Record limit | Attempted page IDs | Accepted | Rejected | Rerun |
| --- | ---: | ---: | ---: | ---: | ---: |
| Person | 40 | 43 | 1 | 39 | 3 |
| Place | 40 | 41 | 1 | 38 | 2 |
| Other | 40 | 44 | 6 | 34 | 4 |
| Date | 40 | 45 | 4 | 36 | 5 |
| Number | 40 | 50 | 4 | 35 | 11 |

### Survival By Layer

| Layer | Entered | Failed | Survived | Layer survival | Cumulative survival |
| --- | ---: | ---: | ---: | ---: | ---: |
| Page-id reservation | 223 | 0 | 223 | 100.0% | 100.0% |
| Unresolved or returned to rerun pool | 223 | 0 | 223 | 100.0% | 100.0% |
| Page extraction, table grading, and QA generation | 223 | 75 | 148 | 66.4% | 66.4% |
| Rewrite and surface validation | 148 | 14 | 134 | 90.5% | 60.1% |
| DuckDuckGo long-tail filtering | 134 | 24 | 110 | 82.1% | 49.3% |
| Second-stage model grading | 110 | 64 | 46 | 41.8% | 20.6% |
| Shared route-aware validation | 46 | 5 | 41 | 89.1% | 18.4% |
| Deduplication | 41 | 0 | 41 | 100.0% | 18.4% |
| Other rejection | 41 | 0 | 41 | 100.0% | 18.4% |

### Failure Reasons

| Stage | Reason | Count |
| --- | --- | ---: |
| `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded` | 64 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_social_science_research` | 35 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers` | 30 |
| `search_longtail` | `search_longtail_verifier_rejected` | 24 |
| `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | 7 |
| `route_generation` | `wikipedia_infobox_answer_type_not_allowed:answer_type_not_allowed:Number; allowed=Number` | 6 |
| `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | 5 |
| `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | 5 |
| `rewrite_surface` | `rewrite_guard_rejected:forbidden_temporal_phrase` | 2 |
| `route_generation` | `wikipedia_infobox_answer_type_not_allowed:answer_type_not_allowed:Other; allowed=Other` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No person name is provided or implied in the twin cities table; thus no single person answer can be safely extracted.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No person names are present in the twin cities table to form a valid single_fact question with a Person answer.` | 1 |
| `route_generation` | `wikipedia_infobox_single_fact_list_answer:single_fact_list_answer_not_allowed` | 1 |

### Answer Type Stats

| Scope | Answer type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `Date` | 4 | 23 | 27 | 14.8% |
| Current Run Records | `Number` | 4 | 16 | 20 | 20.0% |
| Current Run Records | `Other` | 6 | 20 | 26 | 23.1% |
| Current Run Records | `Person` | 1 | 23 | 24 | 4.2% |
| Current Run Records | `Place` | 1 | 25 | 26 | 3.9% |
| Current Run Records | `unknown` | 0 | 75 | 75 | 0.0% |

### Reasoning Type Stats

| Scope | Reasoning type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `single_fact` | 16 | 182 | 198 | 8.1% |

### Rerun Pool After Run

| Page ID | Exact reason |
| ---: | --- |
| 1640 | `search_longtail_verifier_error` |
| 41853326 | `second_stage_grading_error` |


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
| `candidate_processing_seconds` | 198 | 3279.6349 | 16.5638 | 105.8556 |
| `duckduckgo_search_seconds` | 109 | 1679.1877 | 15.4054 | 51.7730 |
| `first_paragraph_extract_seconds` | 133 | 47.3375 | 0.3559 | 1.4563 |
| `llm_question_generation_seconds` | 133 | 948.1342 | 7.1288 | 22.9969 |
| `number_reference_margin_seconds` | 109 | 0.0013 | 0.0000 | 0.0003 |
| `page_fetch_seconds` | 198 | 15.8208 | 0.0799 | 0.5113 |
| `rewrite_seconds` | 123 | 0.0001 | 0.0000 | 0.0001 |
| `second_stage_grading_seconds` | 85 | 1600.3268 | 18.8274 | 54.0768 |
| `table_parse_seconds` | 198 | 208.7832 | 1.0545 | 4.2219 |
| `total_generation_seconds` | 198 | 1265.6538 | 6.3922 | 25.8004 |
| `total_processing_seconds` | 198 | 3279.6349 | 16.5638 | 105.8556 |

## Accepted Candidates

| Page ID | Question | Answer | Source |
| ---: | --- | --- | --- |
| 19653842 | Who are the authors of the view that organisms can be understood as cooperating entities at differing levels of biological organisation? | Queller and Strassmann | https://en.wikipedia.org/wiki/Organism |
| 217231 | In which city was the DVD release of Curb Your Enthusiasm Season 3's Region 2 version made available on February 7, 2005? | Aspen | https://en.wikipedia.org/wiki/Curb_Your_Enthusiasm |
| 19261 | What is the average sea temperature in Monaco during the month of August? | 23.6 °C | https://en.wikipedia.org/wiki/Monaco |
| 292259 | Which language broadcast by Deutsche Welle was closed on 1 January 2024? | German | https://en.wikipedia.org/wiki/Deutsche_Welle |
| 41853326 | Which company was the kit manufacturer for Inter Miami CF in the 2023 season? | Fracht Group | https://en.wikipedia.org/wiki/Inter_Miami_CF |
| 217231 | What bonus feature is included in the DVD release of Season 10 of Curb Your Enthusiasm? | "What Finally Broke Them" | https://en.wikipedia.org/wiki/Curb_Your_Enthusiasm |
| 30292 | What event marks the success of the quest in The Hobbit according to Randel Helms's analysis? | Arrival of Great Eagles | https://en.wikipedia.org/wiki/The_Hobbit |
| 19653842 | According to Jack A. Wilson's analysis, what is the buoyancy mechanism of a colonial siphonophore? | Top of colony is gas-filled | https://en.wikipedia.org/wiki/Organism |
| 19261 | In what year did Monaco establish its twinning relationship with Macau, China? | 1992 | https://en.wikipedia.org/wiki/Monaco |
| 31740 | In what year was the University of Michigan—Ann Arbor ranked 20th (tie) in the U.S. News Best National Universities? | 2025 | https://en.wikipedia.org/wiki/University_of_Michigan |
| 217231 | What month, day, and year was the pilot episode of Curb Your Enthusiasm originally released? | October 17, 1999 | https://en.wikipedia.org/wiki/Curb_Your_Enthusiasm |
| 8083 | In what year did Dr. Dre first provide a voice role and likeness for a video game? | 2005 | https://en.wikipedia.org/wiki/Dr._Dre |
| 22948 | How many offspring of Poseidon are listed with a source date in the 1st or 2nd century AD? | 26 | https://en.wikipedia.org/wiki/Poseidon |
| 19261 | What is the average sea temperature in degrees Celsius for the month of July in Monaco? | 23.1 | https://en.wikipedia.org/wiki/Monaco |
| 2924002 | How many categories does the global DJ awards event held annually in Ibiza nominate and award international DJs in? | 11 | https://en.wikipedia.org/wiki/Electronic_dance_music |
| 260996 | How many stage productions did Christian Slater perform in during the 1980s according to the listed roles and venues? | 6 | https://en.wikipedia.org/wiki/Christian_Slater |

## Second-Stage Filtering Responses

These are the small-model QA responses used by the second-stage filter: `openai/gpt-4.1-mini` and `google/gemini-3-flash-preview`.

| Page ID | Question | Reference answer | openai/gpt-4.1-mini | google/gemini-3-flash-preview |
| ---: | --- | --- | --- | --- |
| 19653842 | Who are the authors of the view that organisms can be understood as cooperating entities at differing levels of biological organisation? | Queller and Strassmann | INCORRECT; predicted_answer: The authors most associated with the view that organisms can be understood as cooperating entities at differing levels of biological organization include David Sloan Wilson and Elliott Sober. They have extensively developed the concept of multilevel selection theory, which explains how cooperation and selection operate at multiple biological levels, from genes to groups. | INCORRECT; predicted_answer: The primary authors associated with the view of organisms as nested levels of cooperation—often referred to as **Major Transitions in Evolution**—are **John Maynard Smith** and **Eörs Szathmáry**.  Other key contributors to this perspective include:  *   **Leo Buss:** Focused on the transition from individual cells to multicellular units (*The Evolution of Individuality*). *   **Richard Michod:** Developed theories on how cooperation overcomes internal conflict during evolutionary transitions. *   **Lynn Margulis:** Proposed the endosymbiotic theory, viewing the eukaryotic cell as a cooperative arrangement of formerly free- |
| 217231 | In which city was the DVD release of Curb Your Enthusiasm Season 3's Region 2 version made available on February 7, 2005? | Aspen | INCORRECT; predicted_answer: The DVD release of Curb Your Enthusiasm Season 3's Region 2 version was made available in London on February 7, 2005. | INCORRECT; predicted_answer: The Region 2 version of *Curb Your Enthusiasm* Season 3 was released in the **United Kingdom** (and specifically made available in cities across the UK, such as **London**) on February 7, 2005. |
| 19261 | What is the average sea temperature in Monaco during the month of August? | 23.6 °C | INCORRECT; predicted_answer: The average sea temperature in Monaco during the month of August is around 25 to 27°C (77 to 81°F). | INCORRECT; predicted_answer: The average sea temperature in Monaco during August is **25.3°C (77.5°F)**. Typical ranges fluctuate between 23.5°C and 27.5°C. |
| 292259 | Which language broadcast by Deutsche Welle was closed on 1 January 2024? | German | INCORRECT; predicted_answer: The Turkish language broadcast by Deutsche Welle was closed on 1 January 2024. | INCORRECT; predicted_answer: Deutsche Welle closed its **Vietnamese** language service on 1 January 2024. |
| 41853326 | Which company was the kit manufacturer for Inter Miami CF in the 2023 season? | Fracht Group | INCORRECT; predicted_answer: The kit manufacturer for Inter Miami CF in the 2023 season was Adidas. | INCORRECT; predicted_answer: **Adidas** was the kit manufacturer for Inter Miami CF in the 2023 season. |
| 217231 | What bonus feature is included in the DVD release of Season 10 of Curb Your Enthusiasm? | "What Finally Broke Them" | INCORRECT; predicted_answer: The DVD release of Season 10 of *Curb Your Enthusiasm* includes a bonus feature titled "Larry David: Curb Your Enthusiasm Season 10 Commentary," where Larry David provides commentary on select episodes. | INCORRECT; predicted_answer: The DVD release of *Curb Your Enthusiasm* Season 10 includes a featurette titled **"The Party"**, which provides a behind-the-scenes look at the making of the season. |
| 30292 | What event marks the success of the quest in The Hobbit according to Randel Helms's analysis? | Arrival of Great Eagles | INCORRECT; predicted_answer: According to Randel Helms's analysis, the success of the quest in *The Hobbit* is marked by the Battle of Five Armies. | INCORRECT; predicted_answer: According to Randel Helms in *Tolkien's World*, the success of the quest is marked by **Bilbo Baggins's decision to give the Arkenstone to Bard and the Elvenking.**  Helms argues that while the physical journey ends at the Lonely Mountain, the moral and spiritual success of the quest is achieved only when Bilbo transcends his greed and "burglar" instincts to perform a selfless act of statesmanship, thereby preventing unnecessary bloodshed and resolving the conflict. |
| 19653842 | According to Jack A. Wilson's analysis, what is the buoyancy mechanism of a colonial siphonophore? | Top of colony is gas-filled | INCORRECT; predicted_answer: According to Jack A. Wilson's analysis, the buoyancy mechanism of a colonial siphonophore involves specialized gas-filled structures called pneumatophores. These pneumatophores regulate buoyancy by controlling the volume and composition of gas within them, allowing the colony to maintain neutral buoyancy and adjust its position in the water column. | INCORRECT; predicted_answer: According to Jack A. Wilson, the buoyancy mechanism of a colonial siphonophore is primarily regulated by the **pneumatophore** (a gas-filled float). This structure contains a gas gland that secretes a mixture of gases, predominantly **carbon monoxide**, to maintain or adjust the organism's vertical position in the water column. |
| 19261 | In what year did Monaco establish its twinning relationship with Macau, China? | 1992 | INCORRECT; predicted_answer: Monaco established its twinning relationship with Macau, China, in 2009. | INCORRECT; predicted_answer: Monaco and Macau established their twinning relationship in **2006**. |
| 31740 | In what year was the University of Michigan—Ann Arbor ranked 20th (tie) in the U.S. News Best National Universities? | 2025 | INCORRECT; predicted_answer: The University of Michigan—Ann Arbor was ranked 20th (tie) in the U.S. News Best National Universities in the year 2024. | INCORRECT; predicted_answer: The University of Michigan—Ann Arbor was ranked 20th (tie) in the **2011** edition of the *U.S. News & World Report* Best National Universities rankings. |
| 217231 | What month, day, and year was the pilot episode of Curb Your Enthusiasm originally released? | October 17, 1999 | INCORRECT; predicted_answer: The pilot episode of *Curb Your Enthusiasm* was originally released on October 15, 2000. | INCORRECT; predicted_answer: The pilot episode of *Curb Your Enthusiasm* originally aired on **October 15, 2000**. |
| 8083 | In what year did Dr. Dre first provide a voice role and likeness for a video game? | 2005 | INCORRECT; predicted_answer: Dr. Dre first provided a voice role and likeness for a video game in 2004, in "Grand Theft Auto: San Andreas." | INCORRECT; predicted_answer: Dr. Dre first provided his voice and likeness for a video game in **2004** for the title *Def Jam: Fight for NY*. |
| 22948 | How many offspring of Poseidon are listed with a source date in the 1st or 2nd century AD? | 26 (acceptable range: anything between 25 and 27) | INCORRECT; predicted_answer: There are 3 offspring of Poseidon listed with a source date in the 1st or 2nd century AD. | INCORRECT; predicted_answer: Based on the *Bibliotheca* of Pseudo-Apollodorus (1st or 2nd century AD), there are approximately **50 to 60** offspring of Poseidon listed.  The exact number varies slightly depending on whether one counts distinct individuals or groups (such as the Aloadae), but the *Bibliotheca* provides the most comprehensive catalog of his progeny from that specific era. |
| 19261 | What is the average sea temperature in degrees Celsius for the month of July in Monaco? | 23.1 (acceptable range: anything between 22.869 and 23.331) | INCORRECT; predicted_answer: The average sea temperature in Monaco in July is approximately 24°C. | INCORRECT; predicted_answer: The average sea temperature in Monaco during the month of July is approximately **24°C** (75°F). |
| 2924002 | How many categories does the global DJ awards event held annually in Ibiza nominate and award international DJs in? | 11 (acceptable range: anything between 10 and 12) | INCORRECT; predicted_answer: The Global DJ Awards held annually in Ibiza nominate and award international DJs in 16 categories. | INCORRECT; predicted_answer: The DJ Awards, held annually in Ibiza, typically features approximately **12 to 14** categories, though the exact number varies slightly each year to reflect evolving music trends. |
| 260996 | How many stage productions did Christian Slater perform in during the 1980s according to the listed roles and venues? | 6 (acceptable range: anything between 5 and 7) | INCORRECT; predicted_answer: Christian Slater performed in 2 stage productions during the 1980s according to the listed roles and venues:  1. "The House of Blue Leaves" (1986) – Broadway, Vivian Beaumont Theater   2. "The Boys Next Door" (1988) – Off-Broadway, WPA Theatre | INCORRECT; predicted_answer: Christian Slater performed in **7** stage productions during the 1980s:  1.  **The Music Man** (1980) – New York City Center 2.  **Copperfield** (1981) – ANTA Playhouse 3.  **Merlin** (1983) – Mark Hellinger Theatre 4.  **Landscape of the Body** (1984) – Second Stage Theatre 5.  **Between Rock and a Hard Place** (1984) – New York City 6.  **Dry |
| 9316 | England |  | not run | not run |
| 17416221 | South Africa |  | not run | not run |
| 32611 | Vietnam War |  | not run | not run |
| 5489 | Chile |  | not run | not run |
| 13277 | Holy Roman Empire |  | not run | not run |
| 19261 | Monaco |  | not run | not run |
| 11857 | George Lucas |  | not run | not run |
| 738 | Who is the President of Albania according to the Politics section? | Bajram Begaj | not run | not run |
| 14849 | Who is the person honored by the state slogan of Illinois known as the "Land of Lincoln"? | Abraham Lincoln | not run | not run |
| 22093 | Which person was the head coach of the Chicago Bulls during their six NBA championship wins in the 1990s? | Phil Jackson | not run | not run |
| 31740 | Who is the person associated with the development of the Klein–Goldberger macroeconomic model at the University of Michigan? | Lawrence Klein | not run | not run |
| 8083 | Who won the Grammy Award for Producer of the Year, Non-Classical in 2001? | Dr. Dre | not run | not run |
| 40010153 | Goa |  | not run | not run |
| 39776 | Denial-of-service attack |  | not run | not run |
| 5488 | Chad |  | not run | not run |
| 199445 | Who scored 8 goals for England in international matches in the year 2014? | Wayne Rooney | CORRECT; predicted_answer: Wayne Rooney scored 8 goals for England in international matches in the year 2014. | not run |
| 1640 | Who succeeded Æthelred as king in c. 871 according to the chronology of Alfred the Great? | Alfred | not run | not run |
| 292259 | Who was the person responsible for starting the English broadcast service of Deutsche Welle in 1954? | Peter von Zahn | INCORRECT; predicted_answer: The person responsible for starting the English broadcast service of Deutsche Welle in 1954 was Hans-Ulrich Werner. | INCORRECT; predicted_answer: The person responsible for starting the English broadcast service of Deutsche Welle in 1954 was **Hans-Otto Meissner**. |
| 151603 | Who played the role of Gurd Canliss in the 1964 episode "Canliss" of the television program Rawhide? | Dean Martin | INCORRECT; predicted_answer: The role of Gurd Canliss in the 1964 episode "Canliss" of the television program Rawhide was played by actor John Carradine. | CORRECT; predicted_answer: **Dean Martin** played the role of Gurd Canliss. |
| 66958 | Who is credited with the formal currency name of the official currency of the People's Republic of China? | rénmínbì | not run | not run |
| 105908 | Ford Mustang |  | not run | not run |
| 60382764 | Who ascended the Chrysanthemum Throne as the 126th Emperor of Japan on 1 May 2019? | Naruhito | not run | not run |
| 41853326 | Who was the head coach of Inter Miami CF from July 10, 2023 to November 22, 2024? | Gerardo Martino | CORRECT; predicted_answer: Gerardo Martino was the head coach of Inter Miami CF from July 10, 2023 to November 22, 2024. | not run |
| 217231 | Who provided commentary on the pilot episode in the Region 1 DVD release of Curb Your Enthusiasm Season 1? | Larry David; Jeff Garlin; Cheryl Hines; Robert B. Weide | not run | not run |
| 12186 | Guinea-Bissau |  | not run | not run |
| 5643 | Channel Islands |  | not run | not run |
| 34411 | Who is the brightest star in the zodiac constellation that the Sun stays in for 7 days according to the 1977 IAU boundaries? | Antares | CORRECT; predicted_answer: The Sun stays in the zodiac constellation **Scorpius** for about 7 days according to the 1977 IAU boundaries. The brightest star in Scorpius is **Antares**. | not run |
| 55440889 | Pixel 2 |  | not run | not run |
| 2924002 | Who most recently won the BRIT Award for British Dance Act as of 2025? | Charli XCX | not run | not run |
| 235916 | Who won the Interactive Achievement Award for Outstanding Achievement in Character Performance – Female for the work Enter the Matrix in 2004? | Jada Pinkett Smith | not run | not run |
| 84952 | Who succeeded Marvelous Marvin Hagler as the WBC middleweight champion? | Sugar Ray Leonard | not run | not run |
| 22948 | Who is the mother of the offspring named Polyphemus according to the earliest source listed in the table? | Thoosa | not run | not run |
| 260996 | Who played the role of Randle Patrick "Mac" McMurphy in the 2004–2005 production of One Flew Over the Cuckoo's Nest at the Gielgud Theatre? | Christian Slater | not run | not run |
| 30292 | Who is the descendant of kings restored to his ancestral throne in The Lord of the Rings according to Randel Helms's analysis of quest structure? | Aragorn | not run | not run |
| 235959 | Who played the role of Marjorie in the 1986 film Extremities? | Farrah Fawcett | CORRECT; predicted_answer: Farrah Fawcett played the role of Marjorie in the 1986 film Extremities. | not run |
| 33094374 | Who is credited with inventing the electrical telegraph, a key long-distance telecommunication technology developed in the 19th century? | Samuel Morse | CORRECT; predicted_answer: Samuel Morse is credited with inventing the electrical telegraph in the 19th century. | not run |
| 91195 | Who won the Gentlemen's singles title at the 2025 Wimbledon Championships? | Jannik Sinner | not run | not run |
| 45367389 | Greater London |  | not run | not run |
| 21355232 | Which person is credited with founding the National Park Service in the United States? | Stephen Mather | CORRECT; predicted_answer: Stephen Mather is credited with founding the National Park Service in the United States. | not run |
| 17416221 | South Africa |  | not run | not run |
| 9316 | England |  | not run | not run |
| 32611 | Vietnam War |  | not run | not run |
| 5489 | Chile |  | not run | not run |
| 13277 | Holy Roman Empire |  | not run | not run |
| 738 | In which place does the President Bajram Begaj serve according to the Politics section of the Albania article? | Albania | not run | not run |
| 11857 | George Lucas |  | not run | not run |
| 14849 | Which place is represented by the state fossil known as the Tully monster? | Illinois | not run | not run |
| 19261 | Which city in Belgium has been a twin city of Monaco since 1958? | Ostend | not run | not run |
| 22093 | Which NBA team won the championship in 1977? | Portland Trail Blazers | not run | not run |
| 31740 | In which U.S. state is the University of Michigan, the oldest institution of higher education in that state, located? | Michigan | not run | not run |
| 21355232 | Which U.S. state contains exactly five national parks, all of which are exclusive to that state? | Utah | not run | not run |
| 40010153 | Goa |  | not run | not run |
| 199445 | For which national team did Wayne Rooney make 120 appearances? | England | not run | not run |
| 39776 | Denial-of-service attack |  | not run | not run |
| 5488 | Chad |  | not run | not run |
| 292259 | In which place did Deutsche Welle begin broadcasting in the Persian language in 1962? | Persian | not run | not run |
| 8083 | In which video game did Dr. Dre provide the voice and likeness for the character named Grizz? | 50 Cent: Bulletproof | not run | not run |
| 151603 | In which television program did Dean Martin play the character Gurd Canliss in 1964? | Rawhide | not run | not run |
| 66958 | In which place is the official currency called renminbi used? | People's Republic of China | not run | not run |
| 105908 | Ford Mustang |  | not run | not run |
| 45367389 | Which city in the Île-de-France region is a twin city of Greater London? | Paris | not run | not run |
| 34411 | Which constellation has the brightest star named Regulus? | Leo | CORRECT; predicted_answer: The constellation Leo has the brightest star named Regulus. | not run |
| 12186 | Guinea-Bissau |  | not run | not run |
| 5643 | Channel Islands |  | not run | not run |
| 60382764 | Which era of Japan immediately preceded the Reiwa era? | Heisei | CORRECT; predicted_answer: The era that immediately preceded the Reiwa era in Japan was the Heisei era. | not run |
| 41853326 | Which country is the nationality of the Inter Miami CF head coach Guillermo Hoyos? | Argentina | CORRECT; predicted_answer: Guillermo Hoyos is from Argentina. | not run |
| 19653842 | In Queller and Strassmann's view of organisms at differing levels of biological organisation, which place is given as the example of a superorganism? | Ant colony | CORRECT; predicted_answer: In Queller and Strassmann's framework, a **social insect colony** (such as an ant or termite colony) is given as the example of a **superorganism**. | not run |
| 55440889 | Pixel 2 |  | not run | not run |
| 235916 | In which television series did Jada Pinkett Smith play the role of Christina Hawthorne? | Hawthorne | not run | not run |
| 2924002 | In which place is the only global DJ awards event that nominates and awards international DJs in 11 categories held annually? | Ibiza | not run | not run |
| 30292 | In The Hobbit, from which place does the quest start? | Bag End in the Shire | CORRECT; predicted_answer: In The Hobbit, the quest starts from the Shire, specifically from Bilbo Baggins' home in Hobbiton. | not run |
| 33094374 | In which place were the worldwide sales of cell phones first recorded as 180 million units according to the telecommunications equipment sales data? | Worldwide | not run | not run |
| 22948 | Which place is the mother of the offspring Parnassus according to the list of Poseidon's offspring and their mothers? | Cleodora | CORRECT; predicted_answer: The mother of the offspring Parnassus, according to the list of Poseidon's offspring and their mothers, is the place **Cleodora**. | not run |
| 84952 | Which boxer preceded Marvelous Marvin Hagler as the WBA middleweight champion? | Alan Minter | CORRECT; predicted_answer: Alan Minter preceded Marvelous Marvin Hagler as the WBA middleweight champion. | not run |
| 235959 | In which city was the play 'Butterflies are Free' starring Farrah Fawcett staged at the Burt Reynolds Dinner Theater? | Jupiter | CORRECT; predicted_answer: The play "Butterflies are Free" starring Farrah Fawcett was staged at the Burt Reynolds Dinner Theater in Jupiter, Florida. | not run |
| 260996 | At which venue did Christian Slater perform the role of Winthrop Paroo in the 1980 stage production of The Music Man? | New York City Center | INCORRECT; predicted_answer: Christian Slater performed the role of Winthrop Paroo in the 1980 stage production of The Music Man at the Westport Country Playhouse. | CORRECT; predicted_answer: Christian Slater performed the role of Winthrop Paroo at the **City Center 55th Street Theater** (often referred to simply as New York City Center) in New York City. |
| 91195 | In which location is the oldest and most prestigious tennis tournament, the Wimbledon Championships, annually held? | Wimbledon, London | CORRECT; predicted_answer: The Wimbledon Championships are annually held in London, England. | not run |
| 9316 | England |  | not run | not run |
| 17416221 | South Africa |  | not run | not run |
| 32611 | Vietnam War |  | not run | not run |
| 5489 | Chile |  | not run | not run |
| 13277 | Holy Roman Empire |  | not run | not run |
| 11857 | George Lucas |  | not run | not run |
| 14849 | What is the official state fossil of Illinois? | Tully monster | CORRECT; predicted_answer: The official state fossil of Illinois is the Tully Monster (Tullimonstrum gregarium). | not run |
| 22093 | Which NBA team has the highest number of NBA Finals wins? | Boston Celtics | INCORRECT; predicted_answer: The Boston Celtics and the Los Angeles Lakers are tied for the highest number of NBA Finals wins, each with 17 championships. | CORRECT; predicted_answer: The **Boston Celtics** have the highest number of NBA Finals wins, with **18** championships. |
| 199445 | In which year did Wayne Rooney score the highest number of goals for the England national team? | 2014 | not run | not run |
| 21355232 | Which U.S. state has the highest number of exclusive national parks? | California | CORRECT; predicted_answer: California has the highest number of exclusive national parks in the U.S. | not run |
| 40010153 | Goa |  | not run | not run |
| 39776 | Denial-of-service attack |  | not run | not run |
| 5488 | Chad |  | not run | not run |
| 31740 | Which school at the University of Michigan was ranked number 1 in the U.S. News Best Schools for Social Work in 2024? | School of Social Work | CORRECT; predicted_answer: The University of Michigan's School of Social Work was ranked number 1 in the U.S. News Best Schools for Social Work in 2024. | not run |
| 1640 | What title did Alfred declare for himself after conquering London around 886? | king of the Anglo-Saxons | CORRECT; predicted_answer: After conquering London around 886, Alfred declared himself "King of the Anglo-Saxons." | not run |
| 151603 | In which television program did Dean Martin play the role of Nancy's Fairy Goduncle? | Movin' with Nancy | INCORRECT; predicted_answer: Dean Martin played the role of Nancy's Fairy Goduncle in the television program **"Nancy" (1970)**. | CORRECT; predicted_answer: Dean Martin played Nancy's Fairy Goduncle in the 1966 television special **"The Nancy Sinatra Show"** (also known as *Movin' with Nancy*). |
| 45367389 | Which city is listed as a twin city of Greater London and is located in the Île-de-France region? | Paris | not run | not run |
| 105908 | Ford Mustang |  | not run | not run |
| 60382764 | What is the Japanese era name corresponding to the Gregorian calendar years 806 to 810? | Daidō | CORRECT; predicted_answer: The Japanese era name corresponding to the years 806 to 810 is **Daidō** (大同). | not run |
| 12186 | Guinea-Bissau |  | not run | not run |
| 5643 | Channel Islands |  | not run | not run |
| 34411 | What is the brightest star in the zodiac constellation that the Sun stays in for approximately 7 days according to the 1977 IAU boundaries? | Antares | CORRECT; predicted_answer: The Sun stays in the zodiac constellation **Scorpius** for approximately 7 days according to the 1977 IAU boundaries. The brightest star in Scorpius is **Antares**. | not run |
| 55440889 | Pixel 2 |  | not run | not run |
| 2924002 | Which organization presents the award titled 'Best DJ Award' annually in Ibiza, Spain? | DJ Awards | INCORRECT; predicted_answer: The International Dance Music Awards (IDMA) present the "Best DJ Award" annually in Ibiza, Spain. | CORRECT; predicted_answer: The **DJ Awards** organization presents the "Best DJ Award" annually in Ibiza, Spain. |
| 22948 | Which offspring of Poseidon was born to the mother Amphitrite according to the earliest source Hesiod's Theogony? | Triton | CORRECT; predicted_answer: According to Hesiod's *Theogony*, the offspring of Poseidon and Amphitrite is Triton. | not run |
| 33094374 | What type of telecommunication equipment had sales of 180 million units worldwide in 1998? | Cell phones | CORRECT; predicted_answer: In 1998, mobile phones had sales of 180 million units worldwide. | not run |
| 235916 | Which award did Jada Pinkett Smith win for Outstanding Achievement in Character Performance – Female? | Interactive Achievement Awards | INCORRECT; predicted_answer: Jada Pinkett Smith won the NAACP Image Award for Outstanding Achievement in Character Performance – Female. | CORRECT; predicted_answer: Jada Pinkett Smith won the **Interactive Achievement Award** (now known as the D.I.C.E. Awards) for Outstanding Achievement in Character Performance – Female for her role as Niobe in the video game ***Enter the Matrix*** (2004). |
| 84952 | In which video game released in 1993 did Marvelous Marvin Hagler appear as a playable character? | Boxing Legends of the Ring | INCORRECT; predicted_answer: Marvelous Marvin Hagler appeared as a playable character in the 1993 video game **"Saturday Night Slam Masters."** | CORRECT; predicted_answer: Marvelous Marvin Hagler appeared as a playable character in **Boxing Legends of the Ring**. |
| 91195 | Which team won the mixed doubles title at the 2025 Wimbledon Championships? | Sem Verbeek Kateřina Siniaková | not run | not run |
| 235959 | In which film did Farrah Fawcett play a character named Alex and receive a Razzie Award nomination for Worst Actress? | Saturn 3 | CORRECT; predicted_answer: Farrah Fawcett played a character named Alex in the film **"Saturn 3"** (1980) and received a Razzie Award nomination for Worst Actress for her role in that film. | not run |
| 260996 | In which venue did Christian Slater perform the role of Sir Galahad in the stage production of Spamalot? | The Hollywood Bowl | INCORRECT; predicted_answer: Christian Slater performed the role of Sir Galahad in the stage production of Spamalot at the St. James Theatre in New York City. | CORRECT; predicted_answer: Christian Slater performed the role of Sir Galahad in the production of *Spamalot* at the **Hollywood Bowl**. |
| 66958 | What is the formal name in English for one-tenth of a unit of the official currency of the People's Republic of China? | jiao | CORRECT; predicted_answer: The formal name in English for one-tenth of a unit of the official currency of the People's Republic of China is the "jiao." | not run |
| 8083 | In which video game did Dr. Dre provide the voice and likeness for the character named Grizz? | 50 Cent: Bulletproof | not run | not run |
| 738 | What is the official title held by Bajram Begaj in Albania? | President | CORRECT; predicted_answer: Bajram Begaj holds the official title of President of Albania. | not run |
| 9316 | England |  | not run | not run |
| 17416221 | South Africa |  | not run | not run |
| 32611 | Vietnam War |  | not run | not run |
| 5489 | Chile |  | not run | not run |
| 13277 | Holy Roman Empire |  | not run | not run |
| 22093 | In what year did the Boston Celtics most recently win the NBA championship? | 2024 | not run | not run |
| 11857 | George Lucas |  | not run | not run |
| 14849 | In what year was the Illinois state quarter released? | 2003 | CORRECT; predicted_answer: The Illinois state quarter was released in 2003. | not run |
| 738 | In what year did Bajram Begaj become President of Albania? | 2022 | CORRECT; predicted_answer: Bajram Begaj became President of Albania in 2022. | not run |
| 199445 | In what year did Wayne Rooney make the highest number of appearances for the England national team? | 2014 | INCORRECT; predicted_answer: Wayne Rooney made the highest number of appearances for the England national team in 2010. | CORRECT; predicted_answer: Wayne Rooney made his highest number of appearances for the England national team in **2014**, playing in **13** matches. |
| 40010153 | Goa |  | not run | not run |
| 39776 | Denial-of-service attack |  | not run | not run |
| 5488 | Chad |  | not run | not run |
| 21355232 | In what year was the United States National Park System established? | 1916 | CORRECT; predicted_answer: The United States National Park System was established in 1916. | not run |
| 292259 | In what year did Deutsche Welle begin broadcasting in the Persian language? | 1962 | INCORRECT; predicted_answer: Deutsche Welle began broadcasting in the Persian language in 1992. | CORRECT; predicted_answer: Deutsche Welle began broadcasting in Persian in **1962**. |
| 1640 | On what month, day, and year did Alfred the Great die? | 26 October 899 | CORRECT; predicted_answer: Alfred the Great died on October 26, 899. | not run |
| 151603 | In what year did Dean Martin appear in the episode 7 of The Frank Sinatra Show? | 1957 | INCORRECT; predicted_answer: Dean Martin appeared in episode 7 of The Frank Sinatra Show in the year 1950. | CORRECT; predicted_answer: Dean Martin appeared in episode 7 of *The Frank Sinatra Show* in **1957** (specifically, the episode aired on November 29, 1957). |
| 66958 | What is the formal Chinese name for the official currency of the People's Republic of China? | 人民币 | CORRECT; predicted_answer: The formal Chinese name for the official currency of the People's Republic of China is **人民币** (Rénmínbì). | not run |
| 105908 | Ford Mustang |  | not run | not run |
| 41853326 | What month, day, and year did Gerardo Martino's tenure as head coach of Inter Miami CF end? | November 22, 2024 | INCORRECT; predicted_answer: Gerardo Martino's tenure as head coach of Inter Miami CF ended on October 10, 2023. | CORRECT; predicted_answer: Gerardo Martino's tenure as head coach of Inter Miami CF officially ended on **November 22, 2024**, when he held a final press conference to announce his resignation for personal reasons. |
| 12186 | Guinea-Bissau |  | not run | not run |
| 5643 | Channel Islands |  | not run | not run |
| 45367389 | In what year did Greater London establish its twin city agreement with Berlin? | 2000 | INCORRECT; predicted_answer: Greater London established its twin city agreement with Berlin in 1967. | CORRECT; predicted_answer: Greater London and Berlin established their twin city agreement in **2000**. |
| 19653842 | In what year was Jack A. Wilson's analysis of the similar organism-like nature of siphonophores and jellyfish published? | 2008 | INCORRECT; predicted_answer: Jack A. Wilson's analysis of the similar organism-like nature of siphonophores and jellyfish was published in 1908. | INCORRECT; predicted_answer: Jack A. Wilson's analysis, titled "The Siphonophores and the Evolutionary Theory of Organismal Individuality," was published in **2005**. |
| 34411 | What month, day, and year mark the beginning of the 1977 IAU boundaries for the constellation Leo? | August 10 | INCORRECT; predicted_answer: The 1977 IAU boundaries for the constellation Leo were established on **January 1, 1977**. | INCORRECT; predicted_answer: The IAU constellation boundaries are defined for the **equinox of 1875.0**, but they were officially adopted by the IAU in **1928** and published in **1930**.  There is no specific "1977" start date for these boundaries; however, the coordinates for the boundaries are often recalculated for modern epochs (like J2000.0) to account for precession. |
| 55440889 | Pixel 2 |  | not run | not run |
| 22948 | In what century was the earliest source that recorded Poseidon's offspring Triton with Amphitrite? | 8th cent. BC | CORRECT; predicted_answer: The earliest source that records Poseidon's offspring Triton with Amphitrite dates to the 8th century BCE. | not run |
| 235916 | In what year did Jada Pinkett Smith win the Interactive Achievement Award for Outstanding Achievement in Character Performance – Female for her work in Enter the Matrix? | 2004 | CORRECT; predicted_answer: Jada Pinkett Smith won the Interactive Achievement Award for Outstanding Achievement in Character Performance – Female for her work in Enter the Matrix in 2004. | not run |
| 84952 | In what year was the video game 'Boxing Legends of the Ring' featuring Marvelous Marvin Hagler as a playable character released? | 1993 | CORRECT; predicted_answer: The video game "Boxing Legends of the Ring," featuring Marvelous Marvin Hagler as a playable character, was released in 1993. | not run |
| 30292 | In the quest structure analysis by Randel Helms, what is the location where the quest in The Hobbit starts? | From Bag End in the Shire | CORRECT; predicted_answer: In Randel Helms' quest structure analysis, the quest in *The Hobbit* starts at Bilbo's home, Bag End. | not run |
| 33094374 | In what year did worldwide sales of cell phones first reach 400 million units according to the telecommunications equipment sales data? | 2000 | INCORRECT; predicted_answer: Worldwide sales of cell phones first reached 400 million units in the year 2004 according to the telecommunications equipment sales data. | CORRECT; predicted_answer: Worldwide sales of cell phones first reached 400 million units in **2000**. |
| 91195 | In what year were the most recent Wimbledon Championships finals held where Jannik Sinner won the Gentlemen's singles title? | 2025 | not run | not run |
| 235959 | In what year did Farrah Fawcett star in the film 'Logan's Run' credited as Farrah Fawcett-Majors? | 1976 | CORRECT; predicted_answer: Farrah Fawcett starred in the film "Logan's Run" in 1976, credited as Farrah Fawcett-Majors. | not run |
| 60382764 | In what year did the first year of the Reiwa era begin according to the Gregorian calendar? | 2019 | CORRECT; predicted_answer: The first year of the Reiwa era began in 2019 according to the Gregorian calendar. | not run |
| 2924002 | In what year did the Project X Magazine hold its only Electronic Dance Music Awards ceremony? | 1995 | INCORRECT; predicted_answer: The Project X Magazine held its only Electronic Dance Music Awards ceremony in 1993. | CORRECT; predicted_answer: Project X Magazine held its only Electronic Dance Music Awards ceremony in **1995**. |
| 260996 | In what year did Christian Slater perform the role of Winthrop Paroo in the stage production of The Music Man at New York City Center? | 1980 | INCORRECT; predicted_answer: Christian Slater performed the role of Winthrop Paroo in the stage production of The Music Man at New York City Center in 2000. | CORRECT; predicted_answer: Christian Slater performed the role of Winthrop Paroo in *The Music Man* at New York City Center in **1980**. |
| 9316 | England |  | not run | not run |
| 17416221 | South Africa |  | not run | not run |
| 32611 | Vietnam War |  | not run | not run |
| 5489 | Chile |  | not run | not run |
| 13277 | Holy Roman Empire |  | not run | not run |
| 14849 | How many years ago was the Illinois state quarter released? | 2003 | not run | not run |
| 11857 | George Lucas |  | not run | not run |
| 22093 | How many NBA championships have the Boston Celtics won? | 18 (acceptable range: anything between 17 and 19) | INCORRECT; predicted_answer: The Boston Celtics have won 17 NBA championships. | CORRECT; predicted_answer: The Boston Celtics have won **18** NBA championships. |
| 31740 | What was the U.S. News Best Engineering Schools rank for the College of Engineering at the University of Michigan in 2025? | 11 | not run | not run |
| 292259 | In what year did Deutsche Welle begin broadcasting in the Persian language? | 1962 | not run | not run |
| 40010153 | Goa |  | not run | not run |
| 39776 | Denial-of-service attack |  | not run | not run |
| 5488 | Chad |  | not run | not run |
| 8083 | How many Grammy Awards has Dr. Dre won? | 7 (acceptable range: anything between 6 and 8) | CORRECT; predicted_answer: Dr. Dre has won 7 Grammy Awards. | not run |
| 199445 | How many international appearances did Wayne Rooney make for England in the year 2014? | 13 (acceptable range: anything between 12 and 14) | INCORRECT; predicted_answer: Wayne Rooney made 9 international appearances for England in the year 2014. | CORRECT; predicted_answer: Wayne Rooney made **13** international appearances for England in 2014. |
| 151603 | How many episodes did Dean Martin appear in on The Dean Martin Show between 1965 and 1974? | 264 (acceptable range: anything between 261 and 267) | CORRECT; predicted_answer: Dean Martin appeared in 264 episodes of The Dean Martin Show between 1965 and 1974. | not run |
| 21355232 | How many total national parks are located in the state of California? | 9 (acceptable range: anything between 8 and 10) | CORRECT; predicted_answer: California has 9 national parks. | not run |
| 45367389 | In what year did Greater London establish its twin city agreement with Berlin? | 2000 | not run | not run |
| 105908 | Ford Mustang |  | not run | not run |
| 66958 | How many tenths of a yuan are represented by the formal name 'jiǎo' in the renminbi currency system? | 1 (acceptable range: anything between 0 and 2) | CORRECT; predicted_answer: The formal name "jiǎo" (角) in the renminbi currency system represents 1 tenth of a yuan. | not run |
| 60382764 | How many years does the Daidō era span according to the given era periods? | 4 (acceptable range: anything between 3 and 5) | CORRECT; predicted_answer: The Daidō era spans 4 years, from 806 to 810. | not run |
| 12186 | Guinea-Bissau |  | not run | not run |
| 5643 | Channel Islands |  | not run | not run |
| 19653842 | How many cells compose a jellyfish according to Jack A. Wilson's analysis of organism-like colonies? | Many | not run | not run |
| 55440889 | Pixel 2 |  | not run | not run |
| 84952 | In what year was the video game 'Boxing Legends of the Ring' featuring Marvelous Marvin Hagler as a playable character released? | 1993 | not run | not run |
| 33094374 | How many million cell phones were sold worldwide in the year 2008 according to the telecommunications equipment sales data? | 1000 | not run | not run |
| 235959 | In what year was the film 'Saturn 3', in which Farrah Fawcett played the role of Alex, released? | 1980 | not run | not run |
| 91195 | How many sets were played in the Gentlemen's singles final at the 2025 Wimbledon Championships? | 4 | not run | not run |
| 1640 | In what year did Alfred the Great die according to the chronology table? | 899 (acceptable range: anything between 890 and 908) | CORRECT; predicted_answer: Alfred the Great died in the year 899 according to the chronology table. | not run |
| 738 | How many individuals are listed with political titles in the Politics section of the Albania Wikipedia page table? | 2 (acceptable range: anything between 1 and 3) | INCORRECT; predicted_answer: There are 6 individuals listed with political titles in the Politics section of the Albania Wikipedia page table. | INCORRECT; predicted_answer: There are **4** individuals listed with political titles in the "Politics" section table of the Albania Wikipedia page:  1. **Bajram Begaj** (President) 2. **Lindita Nikolla** (Chairwoman of Parliament) 3. **Edi Rama** (Prime Minister) 4. **Sokol Sadushi** (Chief Justice) |
| 34411 | How many days does the Sun stay in the Virgo constellation according to the 1977 IAU boundaries? | 45 (acceptable range: anything between 44 and 46) | CORRECT; predicted_answer: According to the 1977 IAU constellation boundaries, the Sun stays in the Virgo constellation for about 44 days, from approximately August 16 to September 29. | not run |
| 217231 | How many episodes were there in the tenth season of Curb Your Enthusiasm? | 10 (acceptable range: anything between 9 and 11) | CORRECT; predicted_answer: The tenth season of *Curb Your Enthusiasm* has 10 episodes. | not run |
| 30292 | How many phases are explicitly identified in the quest structure analysis of The Hobbit according to Randel Helms? | 2 (acceptable range: anything between 1 and 3) | INCORRECT; predicted_answer: Randel Helms explicitly identifies **six phases** in the quest structure analysis of *The Hobbit*. | INCORRECT; predicted_answer: According to Randel Helms in his analysis "The Hobbit and Archetypal Criticism," the quest structure is explicitly identified as having **four** phases. |
| 235916 | How many episodes did Jada Pinkett Smith appear in during her role as Lena James in the television series A Different World? | 46 (acceptable range: anything between 45 and 47) | INCORRECT; predicted_answer: Jada Pinkett Smith appeared in 3 episodes of the television series *A Different World* as Lena James. | CORRECT; predicted_answer: Jada Pinkett Smith appeared in **46 episodes** of *A Different World* as Lena James. |


## Rejected And Rerun Decisions

| Page ID | Stage | Exact reason | Page/question |
| ---: | --- | --- | --- |
| 9316 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=3;no_social_science_research:population` | England |
| 17416221 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=km;no_social_science_research:population` | South Africa |
| 32611 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=24` | Vietnam War |
| 5489 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=km;no_social_science_research:population` | Chile |
| 13277 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=9;no_social_science_research:population` | Holy Roman Empire |
| 19261 | `route_generation` | `wikipedia_infobox_llm_discarded:No person name is provided or implied in the twin cities table; thus no single person answer can be safely extracted.` | Monaco |
| 11857 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=1` | George Lucas |
| 738 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Who is the President of Albania according to the Politics section? |
| 14849 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | Who is the person honored by the state slogan of Illinois known as the "Land of Lincoln"? |
| 22093 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which person was the head coach of the Chicago Bulls during their six NBA championship wins in the 1990s? |
| 31740 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Who is the person associated with the development of the Klein–Goldberger macroeconomic model at the University of Michigan? |
| 8083 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | Who won the Grammy Award for Producer of the Year, Non-Classical in 2001? |
| 40010153 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=2` | Goa |
| 39776 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=2` | Denial-of-service attack |
| 5488 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=20;no_social_science_research:census,population` | Chad |
| 199445 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who scored 8 goals for England in international matches in the year 2014? |
| 1640 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | Who succeeded Æthelred as king in c. 871 according to the chronology of Alfred the Great? |
| 292259 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | Who was the person responsible for starting the English broadcast service of Deutsche Welle in 1954? |
| 151603 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who played the role of Gurd Canliss in the 1964 episode "Canliss" of the television program Rawhide? |
| 66958 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | Who is credited with the formal currency name of the official currency of the People's Republic of China? |
| 105908 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=10` | Ford Mustang |
| 60382764 | `search_longtail` | `search_longtail_verifier_rejected:full_question:answer_in_title` | Who ascended the Chrysanthemum Throne as the 126th Emperor of Japan on 1 May 2019? |
| 41853326 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who was the head coach of Inter Miami CF from July 10, 2023 to November 22, 2024? |
| 217231 | `route_generation` | `wikipedia_infobox_single_fact_list_answer:single_fact_list_answer_not_allowed` | Who provided commentary on the pilot episode in the Region 1 DVD release of Curb Your Enthusiasm Season 1? |
| 12186 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=10;no_social_science_research:population` | Guinea-Bissau |
| 5643 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=acres,km,mi;no_social_science_research:population` | Channel Islands |
| 34411 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who is the brightest star in the zodiac constellation that the Sun stays in for 7 days according to the 1977 IAU boundaries? |
| 55440889 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=g` | Pixel 2 |
| 2924002 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | Who most recently won the BRIT Award for British Dance Act as of 2025? |
| 235916 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Who won the Interactive Achievement Award for Outstanding Achievement in Character Performance – Female for the work Enter the Matrix in 2004? |
| 84952 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Who succeeded Marvelous Marvin Hagler as the WBC middleweight champion? |
| 22948 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Who is the mother of the offspring named Polyphemus according to the earliest source listed in the table? |
| 260996 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | Who played the role of Randle Patrick "Mac" McMurphy in the 2004–2005 production of One Flew Over the Cuckoo's Nest at the Gielgud Theatre? |
| 30292 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | Who is the descendant of kings restored to his ancestral throne in The Lord of the Rings according to Randel Helms's analysis of quest structure? |
| 235959 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who played the role of Marjorie in the 1986 film Extremities? |
| 33094374 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who is credited with inventing the electrical telegraph, a key long-distance telecommunication technology developed in the 19th century? |
| 91195 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | Who won the Gentlemen's singles title at the 2025 Wimbledon Championships? |
| 45367389 | `route_generation` | `wikipedia_infobox_llm_discarded:No person names are present in the twin cities table to form a valid single_fact question with a Person answer.` | Greater London |
| 21355232 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which person is credited with founding the National Park Service in the United States? |
| 17416221 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=km;no_social_science_research:population` | South Africa |
| 9316 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=3;no_social_science_research:population` | England |
| 32611 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=24` | Vietnam War |
| 5489 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=km;no_social_science_research:population` | Chile |
| 13277 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=9;no_social_science_research:population` | Holy Roman Empire |
| 738 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | In which place does the President Bajram Begaj serve according to the Politics section of the Albania article? |
| 11857 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=1` | George Lucas |
| 14849 | `search_longtail` | `search_longtail_verifier_rejected:full_question:answer_in_title` | Which place is represented by the state fossil known as the Tully monster? |
| 19261 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which city in Belgium has been a twin city of Monaco since 1958? |
| 22093 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which NBA team won the championship in 1977? |
| 31740 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | In which U.S. state is the University of Michigan, the oldest institution of higher education in that state, located? |
| 21355232 | `search_longtail` | `search_longtail_verifier_rejected:full_question:answer_in_title` | Which U.S. state contains exactly five national parks, all of which are exclusive to that state? |
| 40010153 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=2` | Goa |
| 199445 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | For which national team did Wayne Rooney make 120 appearances? |
| 39776 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=2` | Denial-of-service attack |
| 5488 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=20;no_social_science_research:census,population` | Chad |
| 292259 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | In which place did Deutsche Welle begin broadcasting in the Persian language in 1962? |
| 8083 | `search_longtail` | `search_longtail_verifier_rejected:full_question:answer_in_title` | In which video game did Dr. Dre provide the voice and likeness for the character named Grizz? |
| 151603 | `search_longtail` | `search_longtail_verifier_rejected:full_question:answer_in_title` | In which television program did Dean Martin play the character Gurd Canliss in 1964? |
| 66958 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In which place is the official currency called renminbi used? |
| 105908 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=10` | Ford Mustang |
| 45367389 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | Which city in the Île-de-France region is a twin city of Greater London? |
| 34411 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which constellation has the brightest star named Regulus? |
| 12186 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=10;no_social_science_research:population` | Guinea-Bissau |
| 5643 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=acres,km,mi;no_social_science_research:population` | Channel Islands |
| 60382764 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which era of Japan immediately preceded the Reiwa era? |
| 41853326 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which country is the nationality of the Inter Miami CF head coach Guillermo Hoyos? |
| 19653842 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In Queller and Strassmann's view of organisms at differing levels of biological organisation, which place is given as the example of a superorganism? |
| 55440889 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=g` | Pixel 2 |
| 235916 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | In which television series did Jada Pinkett Smith play the role of Christina Hawthorne? |
| 2924002 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | In which place is the only global DJ awards event that nominates and awards international DJs in 11 categories held annually? |
| 30292 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In The Hobbit, from which place does the quest start? |
| 33094374 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | In which place were the worldwide sales of cell phones first recorded as 180 million units according to the telecommunications equipment sales data? |
| 22948 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which place is the mother of the offspring Parnassus according to the list of Poseidon's offspring and their mothers? |
| 84952 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which boxer preceded Marvelous Marvin Hagler as the WBA middleweight champion? |
| 235959 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which city was the play 'Butterflies are Free' starring Farrah Fawcett staged at the Burt Reynolds Dinner Theater? |
| 260996 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | At which venue did Christian Slater perform the role of Winthrop Paroo in the 1980 stage production of The Music Man? |
| 91195 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which location is the oldest and most prestigious tennis tournament, the Wimbledon Championships, annually held? |
| 9316 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=3;no_social_science_research:population` | England |
| 17416221 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=km;no_social_science_research:population` | South Africa |
| 32611 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=24` | Vietnam War |
| 5489 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=km;no_social_science_research:population` | Chile |
| 13277 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=9;no_social_science_research:population` | Holy Roman Empire |
| 11857 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=1` | George Lucas |
| 14849 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the official state fossil of Illinois? |
| 22093 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which NBA team has the highest number of NBA Finals wins? |
| 199445 | `route_generation` | `wikipedia_infobox_answer_type_not_allowed:answer_type_not_allowed:Other; allowed=Other` | In which year did Wayne Rooney score the highest number of goals for the England national team? |
| 21355232 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which U.S. state has the highest number of exclusive national parks? |
| 40010153 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=2` | Goa |
| 39776 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=2` | Denial-of-service attack |
| 5488 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=20;no_social_science_research:census,population` | Chad |
| 31740 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which school at the University of Michigan was ranked number 1 in the U.S. News Best Schools for Social Work in 2024? |
| 1640 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What title did Alfred declare for himself after conquering London around 886? |
| 151603 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which television program did Dean Martin play the role of Nancy's Fairy Goduncle? |
| 45367389 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | Which city is listed as a twin city of Greater London and is located in the Île-de-France region? |
| 105908 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=10` | Ford Mustang |
| 60382764 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the Japanese era name corresponding to the Gregorian calendar years 806 to 810? |
| 12186 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=10;no_social_science_research:population` | Guinea-Bissau |
| 5643 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=acres,km,mi;no_social_science_research:population` | Channel Islands |
| 34411 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the brightest star in the zodiac constellation that the Sun stays in for approximately 7 days according to the 1977 IAU boundaries? |
| 55440889 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=g` | Pixel 2 |
| 2924002 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which organization presents the award titled 'Best DJ Award' annually in Ibiza, Spain? |
| 22948 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which offspring of Poseidon was born to the mother Amphitrite according to the earliest source Hesiod's Theogony? |
| 33094374 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What type of telecommunication equipment had sales of 180 million units worldwide in 1998? |
| 235916 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which award did Jada Pinkett Smith win for Outstanding Achievement in Character Performance – Female? |
| 84952 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which video game released in 1993 did Marvelous Marvin Hagler appear as a playable character? |
| 91195 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | Which team won the mixed doubles title at the 2025 Wimbledon Championships? |
| 235959 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which film did Farrah Fawcett play a character named Alex and receive a Razzie Award nomination for Worst Actress? |
| 260996 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which venue did Christian Slater perform the role of Sir Galahad in the stage production of Spamalot? |
| 66958 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the formal name in English for one-tenth of a unit of the official currency of the People's Republic of China? |
| 8083 | `search_longtail` | `search_longtail_verifier_rejected:full_question:answer_in_title` | In which video game did Dr. Dre provide the voice and likeness for the character named Grizz? |
| 738 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the official title held by Bajram Begaj in Albania? |
| 9316 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=3;no_social_science_research:population` | England |
| 17416221 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=km;no_social_science_research:population` | South Africa |
| 32611 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=24` | Vietnam War |
| 5489 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=km;no_social_science_research:population` | Chile |
| 13277 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=9;no_social_science_research:population` | Holy Roman Empire |
| 22093 | `rewrite_surface` | `rewrite_guard_rejected:forbidden_temporal_phrase` | In what year did the Boston Celtics most recently win the NBA championship? |
| 11857 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=1` | George Lucas |
| 14849 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Illinois state quarter released? |
| 738 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Bajram Begaj become President of Albania? |
| 199445 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Wayne Rooney make the highest number of appearances for the England national team? |
| 40010153 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=2` | Goa |
| 39776 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=2` | Denial-of-service attack |
| 5488 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=20;no_social_science_research:census,population` | Chad |
| 21355232 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the United States National Park System established? |
| 292259 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Deutsche Welle begin broadcasting in the Persian language? |
| 1640 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did Alfred the Great die? |
| 151603 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Dean Martin appear in the episode 7 of The Frank Sinatra Show? |
| 66958 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the formal Chinese name for the official currency of the People's Republic of China? |
| 105908 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=10` | Ford Mustang |
| 41853326 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What month, day, and year did Gerardo Martino's tenure as head coach of Inter Miami CF end? |
| 12186 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=10;no_social_science_research:population` | Guinea-Bissau |
| 5643 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=acres,km,mi;no_social_science_research:population` | Channel Islands |
| 45367389 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Greater London establish its twin city agreement with Berlin? |
| 19653842 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year was Jack A. Wilson's analysis of the similar organism-like nature of siphonophores and jellyfish published? |
| 34411 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | What month, day, and year mark the beginning of the 1977 IAU boundaries for the constellation Leo? |
| 55440889 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=g` | Pixel 2 |
| 22948 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what century was the earliest source that recorded Poseidon's offspring Triton with Amphitrite? |
| 235916 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Jada Pinkett Smith win the Interactive Achievement Award for Outstanding Achievement in Character Performance – Female for her work in Enter the Matrix? |
| 84952 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the video game 'Boxing Legends of the Ring' featuring Marvelous Marvin Hagler as a playable character released? |
| 30292 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In the quest structure analysis by Randel Helms, what is the location where the quest in The Hobbit starts? |
| 33094374 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did worldwide sales of cell phones first reach 400 million units according to the telecommunications equipment sales data? |
| 91195 | `rewrite_surface` | `rewrite_guard_rejected:forbidden_temporal_phrase` | In what year were the most recent Wimbledon Championships finals held where Jannik Sinner won the Gentlemen's singles title? |
| 235959 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Farrah Fawcett star in the film 'Logan's Run' credited as Farrah Fawcett-Majors? |
| 60382764 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the first year of the Reiwa era begin according to the Gregorian calendar? |
| 2924002 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the Project X Magazine hold its only Electronic Dance Music Awards ceremony? |
| 260996 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Christian Slater perform the role of Winthrop Paroo in the stage production of The Music Man at New York City Center? |
| 9316 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=3;no_social_science_research:population` | England |
| 17416221 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=km;no_social_science_research:population` | South Africa |
| 32611 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=24` | Vietnam War |
| 5489 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=km;no_social_science_research:population` | Chile |
| 13277 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=9;no_social_science_research:population` | Holy Roman Empire |
| 14849 | `route_generation` | `wikipedia_infobox_answer_type_not_allowed:answer_type_not_allowed:Number; allowed=Number` | How many years ago was the Illinois state quarter released? |
| 11857 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=1` | George Lucas |
| 22093 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many NBA championships have the Boston Celtics won? |
| 31740 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | What was the U.S. News Best Engineering Schools rank for the College of Engineering at the University of Michigan in 2025? |
| 292259 | `route_generation` | `wikipedia_infobox_answer_type_not_allowed:answer_type_not_allowed:Number; allowed=Number` | In what year did Deutsche Welle begin broadcasting in the Persian language? |
| 40010153 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=2` | Goa |
| 39776 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=2` | Denial-of-service attack |
| 5488 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=20;no_social_science_research:census,population` | Chad |
| 8083 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many Grammy Awards has Dr. Dre won? |
| 199445 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many international appearances did Wayne Rooney make for England in the year 2014? |
| 151603 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many episodes did Dean Martin appear in on The Dean Martin Show between 1965 and 1974? |
| 21355232 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many total national parks are located in the state of California? |
| 45367389 | `route_generation` | `wikipedia_infobox_answer_type_not_allowed:answer_type_not_allowed:Number; allowed=Number` | In what year did Greater London establish its twin city agreement with Berlin? |
| 105908 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=10` | Ford Mustang |
| 66958 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many tenths of a yuan are represented by the formal name 'jiǎo' in the renminbi currency system? |
| 60382764 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many years does the Daidō era span according to the given era periods? |
| 12186 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:over_1000_count=10;no_social_science_research:population` | Guinea-Bissau |
| 5643 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=acres,km,mi;no_social_science_research:population` | Channel Islands |
| 19653842 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | How many cells compose a jellyfish according to Jack A. Wilson's analysis of organism-like colonies? |
| 55440889 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_big_numbers:unit_marker=g` | Pixel 2 |
| 84952 | `route_generation` | `wikipedia_infobox_answer_type_not_allowed:answer_type_not_allowed:Number; allowed=Number` | In what year was the video game 'Boxing Legends of the Ring' featuring Marvelous Marvin Hagler as a playable character released? |
| 33094374 | `route_generation` | `wikipedia_infobox_answer_type_not_allowed:answer_type_not_allowed:Number; allowed=Number` | How many million cell phones were sold worldwide in the year 2008 according to the telecommunications equipment sales data? |
| 235959 | `route_generation` | `wikipedia_infobox_answer_type_not_allowed:answer_type_not_allowed:Number; allowed=Number` | In what year was the film 'Saturn 3', in which Farrah Fawcett played the role of Alex, released? |
| 91195 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | How many sets were played in the Gentlemen's singles final at the 2025 Wimbledon Championships? |
| 1640 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Alfred the Great die according to the chronology table? |
| 738 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | How many individuals are listed with political titles in the Politics section of the Albania Wikipedia page table? |
| 34411 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many days does the Sun stay in the Virgo constellation according to the 1977 IAU boundaries? |
| 217231 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many episodes were there in the tenth season of Curb Your Enthusiasm? |
| 30292 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | How many phases are explicitly identified in the quest structure analysis of The Hobbit according to Randel Helms? |
| 235916 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many episodes did Jada Pinkett Smith appear in during her role as Lena James in the television series A Different World? |


