# Route 3 Streaming Wikipedia Page-ID Walkthrough - 2026-05-20

## Stats

- Run group ID: `wikipedia_stream_fast40_person_single_fact_no_social_science_2026_05_20`
- Run segment ID: `fresh40_person_single_fact_no_social_science_2026_05_20`
- Artifact manifest: `D:\Study\AI\My-research\Wikidata_Framework\outputs\run_manifests\wikipedia_stream_fast40_person_single_fact_no_social_science_2026_05_20.json`
- Mode: `page_id_stream`
- Page source: `table-search`
- Table-search queries: `insource:"wikitable"`
- Attempted page IDs: 42
- Unique attempted page IDs: 40
- Stream state reset at run start: yes
- Auto rerun pool once: yes
- Auto-rerun attempted page IDs: 2
- Accepted QAs: 2
- Rejected QAs/pages: 37
- Transient rerun attempts during run: 3
- Wall-clock runtime: 246.9274s
- DuckDuckGo top K: 5
- Generated search queries per QA: 3
- DuckDuckGo parallel queries: 3
- Minimum Route 3 table score: 0.0
- Route 3 reasoning_type constraint: `single_fact`
- Route 3 answer_type constraint: `Person`
- Route 3 extra prompt rules: `Ask factual questions, not questions about the findings or conclusions of social science research, such as results derived from census studies.`
- Stream page workers: 4
- Wikipedia concurrency limit: 4
- DuckDuckGo service concurrency limit: 4
- OpenRouter generation/rewrite concurrency limit: 10
- Second-stage concurrency limit: 10
- Page-id bounds: 1 to 80000000
- Stream state: `outputs\wikipedia_stream_fast40_person_single_fact_no_social_science_2026_05_20_state.json`
- Accepted output: `outputs\wikipedia_stream_fast40_person_single_fact_no_social_science_2026_05_20_accepted.jsonl`
- Rejected output: `outputs\wikipedia_stream_fast40_person_single_fact_no_social_science_2026_05_20_rejected.jsonl`
- Domain policy: `domain_and_subdomain_optional_for_page_id_streaming`
- Rerun pool after run: `260996`

### Survival By Layer

| Layer | Entered | Failed | Survived | Layer survival | Cumulative survival |
| --- | ---: | ---: | ---: | ---: | ---: |
| Page-id reservation | 42 | 0 | 42 | 100.0% | 100.0% |
| Unresolved or returned to rerun pool | 42 | 0 | 42 | 100.0% | 100.0% |
| Page extraction, table grading, and QA generation | 42 | 9 | 33 | 78.6% | 78.6% |
| Rewrite and surface validation | 33 | 3 | 30 | 90.9% | 71.4% |
| DuckDuckGo long-tail filtering | 30 | 5 | 25 | 83.3% | 59.5% |
| Second-stage model grading | 25 | 21 | 4 | 16.0% | 9.5% |
| Shared route-aware validation | 4 | 2 | 2 | 50.0% | 4.8% |
| Deduplication | 2 | 0 | 2 | 100.0% | 4.8% |
| Other rejection | 2 | 0 | 2 | 100.0% | 4.8% |

### Failure Reasons

| Stage | Exact reason | Count |
| --- | --- | ---: |
| `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | 21 |
| `search_longtail` | `search_longtail_verifier_error` | 3 |
| `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | 2 |
| `route_generation` | `wikipedia_infobox_extra_prompt_violation:no_social_science_research_prompt:census` | 2 |
| `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | 2 |
| `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | 1 |
| `route_generation` | `wikipedia_infobox_extra_prompt_violation:no_social_science_research_prompt:american community survey` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No person name is provided as a historically settled fact for the College of Engineering; the college is not named after a person.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No person name is provided in the table for any broadcast language start; thus no safe single_fact question with a Person answer can be generated.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No person name is provided in the twin cities table; only city names are listed.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No person-related factual data is present in the table to form a valid single_fact question with a Person answer.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No person-type factual data present in the table to form a valid question` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The capital entries are place names, not persons, so no valid Person answer can be generated from the top tables.` | 1 |
| `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | 1 |
| `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | 1 |

### Answer Type Stats

| Scope | Answer type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `Person` | 2 | 28 | 30 | 6.7% |
| Current Run Records | `unknown` | 0 | 9 | 9 | 0.0% |

### Reasoning Type Stats

| Scope | Reasoning type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `single_fact` | 2 | 28 | 30 | 6.7% |
| Current Run Records | `wikipedia_table_fact` | 0 | 9 | 9 | 0.0% |

### Rerun Pool After Run

| Page ID | Exact reason |
| ---: | --- |
| 260996 | `search_longtail_verifier_error` |

### In-Run Rerun Outcomes

These rows show transient rerun-pool attempts and whether the same page ID later reached a final decision in this invocation.

| Page ID | Rerun attempts | Final outcome | Final reason/question | First transient reason |
| ---: | ---: | --- | --- | --- |
| 19653842 | 1 | `accepted` | Who studied the organism-like similarities between siphonophores and jellyfish? | `search_longtail_verifier_error` |
| 260996 | 2 | `still_in_rerun_pool` |  | `search_longtail_verifier_error` |

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
| `candidate_processing_seconds` | 39 | 402.8002 | 10.3282 | 24.0451 |
| `duckduckgo_search_seconds` | 27 | 100.4078 | 3.7188 | 13.2430 |
| `first_paragraph_extract_seconds` | 39 | 10.5786 | 0.2712 | 0.9017 |
| `llm_question_generation_seconds` | 39 | 194.7596 | 4.9938 | 11.0263 |
| `number_reference_margin_seconds` | 27 | 0.0000 | 0.0000 | 0.0000 |
| `page_fetch_seconds` | 39 | 1.9559 | 0.0502 | 0.4037 |
| `rewrite_seconds` | 30 | 100.4225 | 3.3474 | 6.4295 |
| `second_stage_grading_seconds` | 25 | 201.9407 | 8.0776 | 13.0768 |
| `table_parse_seconds` | 39 | 38.7668 | 0.9940 | 4.5376 |
| `total_generation_seconds` | 39 | 249.9919 | 6.4100 | 12.3485 |
| `total_processing_seconds` | 39 | 402.8002 | 10.3282 | 24.0451 |

## Accepted Candidates

| Page ID | Question | Answer | Source |
| ---: | --- | --- | --- |
| 217231 | Who are the commentators on the pilot episode in the DVD release of Curb Your Enthusiasm Season 1? | Larry David; Jeff Garlin; Cheryl Hines; Robert B. Weide | https://en.wikipedia.org/wiki/Curb_Your_Enthusiasm |
| 19653842 | Who studied the organism-like similarities between siphonophores and jellyfish? | Jack A. Wilson | https://en.wikipedia.org/wiki/Organism |

## Second-Stage Filtering Responses

These are the small-model QA responses used by the second-stage filter: `openai/gpt-4.1-mini` and `google/gemini-3-flash-preview`.

| Page ID | Question | Reference answer | openai/gpt-4.1-mini | google/gemini-3-flash-preview |
| ---: | --- | --- | --- | --- |
| 217231 | Who are the commentators on the pilot episode in the DVD release of Curb Your Enthusiasm Season 1? | Larry David; Jeff Garlin; Cheryl Hines; Robert B. Weide | INCORRECT; predicted_answer: The commentators on the pilot episode of *Curb Your Enthusiasm* Season 1 DVD release are Larry David and Jeff Garlin. | INCORRECT; predicted_answer: The commentators on the pilot episode ("The Larry David Story") are **Larry David**, **Jeff Garlin**, and **Robert B. Weide**. |
| 19653842 | Who studied the organism-like similarities between siphonophores and jellyfish? | Jack A. Wilson | INCORRECT; predicted_answer: The organism-like similarities between siphonophores and jellyfish were studied by Ernst Haeckel, a 19th-century German biologist and naturalist. | INCORRECT; predicted_answer: **Ernst Haeckel** is the most prominent scientist who studied and popularized the organism-like similarities between siphonophores and jellyfish, particularly through his "medusome" theory and his detailed illustrations in *Kunstformen der Natur*. |
| 9316 | England |  | not run | not run |
| 5489 | What is the capital of the Libertador General Bernardo O'Higgins region in Chile? | Rancagua | not run | not run |
| 738 | Albania |  | not run | not run |
| 17416221 | What is the provincial capital of KwaZulu-Natal in South Africa? | Pietermaritzburg | not run | not run |
| 32611 | Who was the president of the United States during the year with the highest number of US military deaths in the Vietnam War? | Lyndon B. Johnson | CORRECT; predicted_answer: The year with the highest number of U.S. military deaths in the Vietnam War was 1968. The president of the United States during that year was Lyndon B. Johnson. | not run |
| 14849 | Who is the person associated with the largest self-reported ancestry group in Illinois according to the 2022 American Community Survey? | German | not run | not run |
| 22093 | Who won the National Basketball Association championship in 2016? | Cleveland Cavaliers | CORRECT; predicted_answer: The Cleveland Cavaliers won the National Basketball Association (NBA) championship in 2016. | not run |
| 13277 | Which ruling family controlled the largest territory of the Holy Roman Empire in 1648 after the Thirty Years' War? | Austrian Habsburgs | CORRECT; predicted_answer: After the Thirty Years' War ended in 1648, the Habsburg family controlled the largest territory within the Holy Roman Empire. | not run |
| 11857 | Who was the director of the 1977 film Star Wars? | George Lucas | CORRECT; predicted_answer: The director of the 1977 film Star Wars was George Lucas. | not run |
| 19261 | Who is the person historically linked to the founding or ruling of Monaco? | Prince Rainier III | INCORRECT; predicted_answer: The person historically linked to the founding and ruling of Monaco is François Grimaldi. He is known for capturing the Rock of Monaco in 1297, establishing the Grimaldi family's long-standing rule over Monaco. | INCORRECT; predicted_answer: The person historically linked to the founding of the current ruling dynasty is **Francesco Grimaldi** (known as *Malizia* or "The Cunning"), who captured the Rock of Monaco in 1297. The sovereignty of the nation is tied to the **House of Grimaldi**, which has ruled Monaco for over 700 years. |
| 31740 | University of Michigan |  | not run | not run |
| 292259 | Deutsche Welle |  | not run | not run |
| 199445 | Who managed Derby County between 14 November 2020 and 26 June 2022? | Wayne Rooney | CORRECT; predicted_answer: Wayne Rooney managed Derby County between 14 November 2020 and 26 June 2022. | not run |
| 21355232 | Who started the Lewis and Clark Expedition that is commemorated by the Gateway Arch? | Thomas Jefferson | CORRECT; predicted_answer: The Lewis and Clark Expedition was started by President Thomas Jefferson. | not run |
| 5488 | Who is the person after whom the capital city of Chad is named? | N'Djamena | not run | not run |
| 40010153 | Who is the patron saint of Goa whose mortal remains are kept in the Bom Jesus Basilica? | Saint Francis Xavier | not run | not run |
| 8083 | Who received the 2024 Grammy Lifetime Achievement Award as a member of N.W.A.? | Himself | CORRECT; predicted_answer: Dr. Dre received the 2024 Grammy Lifetime Achievement Award as a member of N.W.A. | not run |
| 39776 | Who fixed the Memcached amplification vulnerability related to the denial-of-service attack in version 1.5.6? | Memcached developers | INCORRECT; predicted_answer: The Memcached amplification vulnerability related to the denial-of-service attack in version 1.5.6 was fixed by Brian Aker. | INCORRECT; predicted_answer: The Memcached development team, led by maintainer **Dormando** (Alan Kasindorf), fixed the vulnerability in version 1.5.6 by disabling the UDP protocol by default. |
| 1640 | Who became king after Æthelred around 871? | Alfred | CORRECT; predicted_answer: After Æthelred, his brother Alfred became king around 871. | not run |
| 151603 | Who was the actor that portrayed Matt Helm in the 1966 movie The Silencers? | Dean Martin | CORRECT; predicted_answer: Dean Martin portrayed Matt Helm in the 1966 movie The Silencers. | not run |
| 45367389 | Greater London |  | not run | not run |
| 41853326 | Who was the top goalscorer for Inter Miami CF in the 2025 MLS season? | Lionel Messi | not run | not run |
| 60382764 | Who became the 126th Emperor of Japan and began the Reiwa era on 1 May 2019? | Naruhito | CORRECT; predicted_answer: Emperor Naruhito became the 126th Emperor of Japan and began the Reiwa era on 1 May 2019. | not run |
| 105908 | Who is the person credited with developing the Ford Mustang? | Lee Iacocca | CORRECT; predicted_answer: The person credited with developing the Ford Mustang is Lee Iacocca. | not run |
| 66958 | Who issues the renminbi, the official currency of the People's Republic of China? | People's Bank of China | CORRECT; predicted_answer: The renminbi is issued by the People's Bank of China. | not run |
| 12186 | Who is the person linked to the city of Bissau in Guinea-Bissau? | Bissau | not run | not run |
| 34411 | Who is the Sumero-Babylonian figure linked to the zodiac sign Aries? | Dumuzi | CORRECT; predicted_answer: The Sumero-Babylonian figure linked to the zodiac sign Aries is the god **Dumuzi (Tammuz)**, often associated with the ram. Aries is symbolized by a ram, reflecting this connection. | not run |
| 5643 | Who was the historical ruler of the Duchy of Normandy, from which the Channel Islands originate? | William the Conqueror | CORRECT; predicted_answer: The historical ruler of the Duchy of Normandy was William the Conqueror. | not run |
| 55440889 | Pixel 2 |  | not run | not run |
| 2924002 | Who won the British Dance Act award at the BRIT Awards in 2025? | Charli XCX | not run | not run |
| 84952 | Who did Marvelous Marvin Hagler fight on April 6, 1987? | Sugar Ray Leonard | CORRECT; predicted_answer: Marvelous Marvin Hagler fought Sugar Ray Leonard on April 6, 1987. | not run |
| 235916 | Who portrayed the character Niobe in the film The Matrix Reloaded? | Jada Pinkett Smith | CORRECT; predicted_answer: Jada Pinkett Smith portrayed the character Niobe in the film The Matrix Reloaded. | not run |
| 22948 | Who is the mother of Triton, the child of Poseidon? | Amphitrite | CORRECT; predicted_answer: The mother of Triton, the child of Poseidon, is Amphitrite. | not run |
| 30292 | Who is the descendant of kings restored to his ancestral throne in The Hobbit? | Aragorn | INCORRECT; predicted_answer: The descendant of kings restored to his ancestral throne in *The Hobbit* is Thorin Oakenshield. | CORRECT; predicted_answer: **Thorin Oakenshield** is the descendant of kings (specifically the grandson of Thror, King under the Mountain) who is restored to his ancestral throne in *The Hobbit*. |
| 33094374 | Who was the inventor of the electrical telegraph in telecommunications? | Samuel Morse | CORRECT; predicted_answer: The electrical telegraph in telecommunications was invented by Samuel Morse. | not run |
| 235959 | Who portrayed Jill Munroe in Charlie's Angels? | Farrah Fawcett | CORRECT; predicted_answer: Farrah Fawcett portrayed Jill Munroe in Charlie's Angels. | not run |
| 91195 | Who holds the record as the oldest men's singles champion at the Wimbledon Championships? | Arthur Gore | CORRECT; predicted_answer: The oldest men's singles champion at the Wimbledon Championships is Arthur Gore, who won the title in 1909 at the age of 41. | not run |


Rerun-pool entries have no second-stage filtering response unless they reached the panel before the transient failure.

## Rejected And Rerun Decisions

| Page ID | Stage | Exact reason | Page/question |
| ---: | --- | --- | --- |
| 9316 | `route_generation` | `wikipedia_infobox_llm_discarded:No person-related factual data is present in the table to form a valid single_fact question with a Person answer.` | England |
| 5489 | `route_generation` | `wikipedia_infobox_extra_prompt_violation:no_social_science_research_prompt:census` | What is the capital of the Libertador General Bernardo O'Higgins region in Chile? |
| 738 | `route_generation` | `wikipedia_infobox_llm_discarded:The capital entries are place names, not persons, so no valid Person answer can be generated from the top tables.` | Albania |
| 17416221 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What is the provincial capital of KwaZulu-Natal in South Africa? |
| 32611 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who was the president of the United States during the year with the highest number of US military deaths in the Vietnam War? |
| 14849 | `route_generation` | `wikipedia_infobox_extra_prompt_violation:no_social_science_research_prompt:american community survey` | Who is the person associated with the largest self-reported ancestry group in Illinois according to the 2022 American Community Survey? |
| 22093 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who won the National Basketball Association championship in 2016? |
| 13277 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which ruling family controlled the largest territory of the Holy Roman Empire in 1648 after the Thirty Years' War? |
| 11857 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who was the director of the 1977 film Star Wars? |
| 19261 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | Who is the person historically linked to the founding or ruling of Monaco? |
| 31740 | `route_generation` | `wikipedia_infobox_llm_discarded:No person name is provided as a historically settled fact for the College of Engineering; the college is not named after a person.` | University of Michigan |
| 292259 | `route_generation` | `wikipedia_infobox_llm_discarded:No person name is provided in the table for any broadcast language start; thus no safe single_fact question with a Person answer can be generated.` | Deutsche Welle |
| 199445 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who managed Derby County between 14 November 2020 and 26 June 2022? |
| 21355232 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who started the Lewis and Clark Expedition that is commemorated by the Gateway Arch? |
| 5488 | `route_generation` | `wikipedia_infobox_extra_prompt_violation:no_social_science_research_prompt:census` | Who is the person after whom the capital city of Chad is named? |
| 40010153 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | Who is the patron saint of Goa whose mortal remains are kept in the Bom Jesus Basilica? |
| 8083 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who received the 2024 Grammy Lifetime Achievement Award as a member of N.W.A.? |
| 39776 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | Who fixed the Memcached amplification vulnerability related to the denial-of-service attack in version 1.5.6? |
| 1640 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who became king after Æthelred around 871? |
| 151603 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who was the actor that portrayed Matt Helm in the 1966 movie The Silencers? |
| 45367389 | `route_generation` | `wikipedia_infobox_llm_discarded:No person name is provided in the twin cities table; only city names are listed.` | Greater London |
| 41853326 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | Who was the top goalscorer for Inter Miami CF in the 2025 MLS season? |
| 60382764 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who became the 126th Emperor of Japan and began the Reiwa era on 1 May 2019? |
| 105908 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who is the person credited with developing the Ford Mustang? |
| 66958 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who issues the renminbi, the official currency of the People's Republic of China? |
| 12186 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | Who is the person linked to the city of Bissau in Guinea-Bissau? |
| 34411 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who is the Sumero-Babylonian figure linked to the zodiac sign Aries? |
| 5643 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who was the historical ruler of the Duchy of Normandy, from which the Channel Islands originate? |
| 55440889 | `route_generation` | `wikipedia_infobox_llm_discarded:No person-type factual data present in the table to form a valid question` | Pixel 2 |
| 2924002 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | Who won the British Dance Act award at the BRIT Awards in 2025? |
| 84952 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who did Marvelous Marvin Hagler fight on April 6, 1987? |
| 235916 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who portrayed the character Niobe in the film The Matrix Reloaded? |
| 22948 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who is the mother of Triton, the child of Poseidon? |
| 30292 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who is the descendant of kings restored to his ancestral throne in The Hobbit? |
| 33094374 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who was the inventor of the electrical telegraph in telecommunications? |
| 235959 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who portrayed Jill Munroe in Charlie's Angels? |
| 91195 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who holds the record as the oldest men's singles champion at the Wimbledon Championships? |

### Rerun Records

| Page ID | Stage | Exact reason | Page/question |
| ---: | --- | --- | --- |
| 19653842 | `search_longtail` | `search_longtail_verifier_error` | https://en.wikipedia.org/w/index.php?pageid=19653842 |
| 260996 | `search_longtail` | `search_longtail_verifier_error` | https://en.wikipedia.org/w/index.php?pageid=260996 |
| 260996 | `search_longtail` | `search_longtail_verifier_error` | https://en.wikipedia.org/w/index.php?pageid=260996 |

