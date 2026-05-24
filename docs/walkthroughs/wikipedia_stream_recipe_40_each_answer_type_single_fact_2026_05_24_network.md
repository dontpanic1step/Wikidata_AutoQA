# Route 3 Streaming Wikipedia Page-ID Walkthrough - 2026-05-24

## Stats

- Run group ID: `wikipedia_stream_recipe_40_each_answer_type_single_fact_2026_05_24_network`
- Run segment ID: `recipe_combined`
- Artifact manifest: ``
- Mode: `page_id_stream_recipe`
- Page source: `table-search`
- Table-search queries: `insource:"wikitable"`
- Attempted page IDs: 207
- Unique attempted page IDs: 200
- Stream state reset at run start: yes
- Auto rerun pool once: yes
- Auto-rerun attempted page IDs: 0
- Accepted QAs: 13
- Rejected QAs/pages: 182
- Transient rerun attempts during run: 12
- Wall-clock runtime: 655.6711s
- DuckDuckGo top K: 5
- Generated search queries per QA: 3
- DuckDuckGo parallel queries: 3
- Route 3 reasoning_type constraint: `single_fact`
- Route 3 answer_type constraint: `Person, Place, Other, Number, Date`
- Route 3 table filter modes: `no_picture_heavy_tables, no_approximate_tables, no_incomplete_tables, not_number_dominant, no_social_science_research`
- Page-id bounds: None to None
- Stream state: `separate_segment_stream_states`
- Accepted output: `D:\Study\AI\My-research\Wikidata_Framework\outputs\wikipedia_stream_recipe_40_each_answer_type_single_fact_2026_05_24_network_accepted.jsonl`
- Rejected output: `D:\Study\AI\My-research\Wikidata_Framework\outputs\wikipedia_stream_recipe_40_each_answer_type_single_fact_2026_05_24_network_rejected.jsonl`
- Domain policy: `domain_and_subdomain_optional_for_page_id_streaming`
- Rerun pool after run: `67749, 168263, 188257, 2186423, 43745773`

### Recipe Segments

| Configured answer_type | Record limit | Attempted page IDs | Accepted | Rejected | Rerun |
| --- | ---: | ---: | ---: | ---: | ---: |
| Person | 40 | 40 | 1 | 39 | 0 |
| Place | 40 | 40 | 3 | 37 | 0 |
| Other | 40 | 41 | 4 | 35 | 2 |
| Number | 40 | 42 | 2 | 38 | 2 |
| Date | 40 | 44 | 3 | 33 | 8 |

### Survival By Layer

| Layer | Entered | Failed | Survived | Layer survival | Cumulative survival |
| --- | ---: | ---: | ---: | ---: | ---: |
| Page-id reservation | 207 | 0 | 207 | 100.0% | 100.0% |
| Unresolved or returned to rerun pool | 207 | 0 | 207 | 100.0% | 100.0% |
| Page extraction, table grading, and QA generation | 207 | 104 | 103 | 49.8% | 49.8% |
| Rewrite and surface validation | 103 | 18 | 85 | 82.5% | 41.1% |
| DuckDuckGo long-tail filtering | 85 | 8 | 77 | 90.6% | 37.2% |
| Second-stage model grading | 77 | 46 | 31 | 40.3% | 15.0% |
| Shared route-aware validation | 31 | 6 | 25 | 80.7% | 12.1% |
| Deduplication | 25 | 0 | 25 | 100.0% | 12.1% |
| Other rejection | 25 | 0 | 25 | 100.0% | 12.1% |

### Failure Reasons

| Stage | Reason | Count |
| --- | --- | ---: |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant` | 55 |
| `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded` | 46 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables` | 23 |
| `search_longtail` | `search_longtail_verifier_rejected` | 8 |
| `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | 6 |
| `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | 6 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | 5 |
| `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:table` | 4 |
| `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | 3 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_approximate_tables` | 3 |
| `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | 2 |
| `rewrite_surface` | `rewrite_guard_rejected:forbidden_temporal_phrase` | 2 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:active` | 2 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:present` | 2 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | 2 |
| `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_time_invariance_forbidden_phrase:recent` | 1 |
| `route_generation` | `wikipedia_infobox_answer_type_not_allowed:answer_type_not_allowed:Number; allowed=Number` | 1 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:caption:active` | 1 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:incumbent` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No person answer type supported by the top three tables on the Renminbi page.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The only available table is an empty or incomplete climate chart with no factual data to form a valid question with a single indisputable answer of type Other.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The only available table is an infobox with no person-related data or any factual entries suitable for a single-person answer question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The only table available does not contain any person names or data suitable for a Person answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The only table available is an incomplete climate chart with no factual place data to form a valid single-answer Place question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any person-related data; only language and broadcast dates are listed.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any place names or geographic entities related to the films, only film titles, years, roles, and notes.` | 1 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables` | 1 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_social_science_research` | 1 |

### Answer Type Stats

| Scope | Answer type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `Date` | 3 | 16 | 19 | 15.8% |
| Current Run Records | `Number` | 2 | 15 | 17 | 11.8% |
| Current Run Records | `Other` | 4 | 15 | 19 | 21.1% |
| Current Run Records | `Person` | 1 | 17 | 18 | 5.6% |
| Current Run Records | `Place` | 3 | 15 | 18 | 16.7% |
| Current Run Records | `unknown` | 0 | 104 | 104 | 0.0% |

### Reasoning Type Stats

| Scope | Reasoning type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `single_fact` | 13 | 182 | 195 | 6.7% |

### Rerun Pool After Run

| Page ID | Exact reason |
| ---: | --- |
| 67749 | `search_longtail_verifier_error` |
| 168263 | `search_longtail_verifier_error` |
| 188257 | `search_longtail_verifier_error` |
| 2186423 | `search_longtail_verifier_error` |
| 43745773 | `search_longtail_verifier_error` |


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
| `candidate_processing_seconds` | 195 | 733.2530 | 3.7603 | 27.1094 |
| `duckduckgo_search_seconds` | 73 | 203.8530 | 2.7925 | 13.8414 |
| `first_paragraph_extract_seconds` | 99 | 23.9026 | 0.2414 | 1.0480 |
| `llm_question_generation_seconds` | 99 | 380.9613 | 3.8481 | 8.7804 |
| `number_reference_margin_seconds` | 73 | 0.0002 | 0.0000 | 0.0001 |
| `page_fetch_seconds` | 195 | 73.7699 | 0.3783 | 6.9067 |
| `rewrite_seconds` | 91 | 0.0000 | 0.0000 | 0.0000 |
| `second_stage_grading_seconds` | 65 | 529.3212 | 8.1434 | 24.8133 |
| `table_parse_seconds` | 195 | 127.9236 | 0.6560 | 3.5822 |
| `total_generation_seconds` | 195 | 636.5387 | 3.2643 | 13.2786 |
| `total_processing_seconds` | 195 | 733.2530 | 3.7603 | 27.1094 |

## Accepted Candidates

| Page ID | Question | Answer | Source |
| ---: | --- | --- | --- |
| 19653842 | Who proposed the analysis that places siphonophores and jellyfish in a boundary zone between definite colonies and definite organisms? | Jack A. Wilson | https://en.wikipedia.org/wiki/Organism |
| 26941 | Which city is associated with the distributor of Spike Lee's 1992 directed feature film Malcolm X? | Warner Bros. | https://en.wikipedia.org/wiki/Spike_Lee |
| 169833 | At which awards ceremony did Tracy Chapman win the Best International Album award in 1989? | Denmark | https://en.wikipedia.org/wiki/Tracy_Chapman |
| 66524 | Which stadium is the home venue for the ice hockey club Avtomobilist Yekaterinburg? | UMMC Arena | https://en.wikipedia.org/wiki/Yekaterinburg |
| 38962787 | Which association awarded The Blacklist for Outstanding Stunt Coordination for a Drama Series, Miniseries, or Movie in 2014? | Primetime Creative Arts Emmy Awards | https://en.wikipedia.org/wiki/The_Blacklist |
| 151451 | What is the title of the documentary released in 2014 related to Busta Rhymes? | Nas: Time Is Illmatic | https://en.wikipedia.org/wiki/Busta_Rhymes |
| 599 | What is the term used for the first person singular prefix conjugation in the Preterite form of Akkadian (Semitic)? | a-prus | https://en.wikipedia.org/wiki/Afroasiatic_languages |
| 47864412 | What is the IPA pronunciation of the Nepali ligature formed by combining the letters क and ष? | IPA: /t͡sʰjʌ/, /ksʌ/ | https://en.wikipedia.org/wiki/Nepali_language |
| 57659 | How many football championships has Espérance Sportive de Tunis won? | 20 | https://en.wikipedia.org/wiki/Tunis |
| 359520 | How many films or television productions did Joan Jett appear in during the 2000s decade according to her filmography? | 9 | https://en.wikipedia.org/wiki/Joan_Jett |
| 420162 | On what month, day, and year was Rai Ladinia launched? | September 26, 1988 | https://en.wikipedia.org/wiki/RAI |
| 485429 | In the context of martial morality in Chinese martial arts, what is the Pinyin romanization for the concept of humility? | qiān | https://en.wikipedia.org/wiki/Chinese_martial_arts |
| 363002 | In what year did Sandra Oh perform in the play titled 'Death and the Maiden' at the Victory Gardens Theater? | 2014 | https://en.wikipedia.org/wiki/Sandra_Oh |

## Second-Stage Filtering Responses

These are the small-model QA responses used by the second-stage filter: `openai/gpt-4.1-mini` and `google/gemini-3-flash-preview`.

| Page ID | Question | Reference answer | openai/gpt-4.1-mini | google/gemini-3-flash-preview |
| ---: | --- | --- | --- | --- |
| 19653842 | Who proposed the analysis that places siphonophores and jellyfish in a boundary zone between definite colonies and definite organisms? | Jack A. Wilson | INCORRECT; predicted_answer: This analysis was proposed by William M. Wheeler. | INCORRECT; predicted_answer: **Julian Huxley** proposed this analysis, most notably in his 1912 book *The Individual in the Animal Kingdom*. |
| 26941 | Which city is associated with the distributor of Spike Lee's 1992 directed feature film Malcolm X? | Warner Bros. | INCORRECT; predicted_answer: The distributor of Spike Lee's 1992 film *Malcolm X* is Warner Bros., which is associated with Burbank, California. | INCORRECT; predicted_answer: **Burbank**, California (the headquarters of Warner Bros.). |
| 169833 | At which awards ceremony did Tracy Chapman win the Best International Album award in 1989? | Denmark | INCORRECT; predicted_answer: Tracy Chapman won the Best International Album award in 1989 at the Brit Awards. | INCORRECT; predicted_answer: Tracy Chapman won the Best International Album award at the **1989 BRIT Awards**. |
| 66524 | Which stadium is the home venue for the ice hockey club Avtomobilist Yekaterinburg? | UMMC Arena | INCORRECT; predicted_answer: The home venue for the ice hockey club Avtomobilist Yekaterinburg is the KRK Uralets. | INCORRECT; predicted_answer: The home venue for Avtomobilist Yekaterinburg is the **KRK Uralets** (Cultural and Entertainment Complex "Uralets"). |
| 38962787 | Which association awarded The Blacklist for Outstanding Stunt Coordination for a Drama Series, Miniseries, or Movie in 2014? | Primetime Creative Arts Emmy Awards | INCORRECT; predicted_answer: The Blacklist was awarded Outstanding Stunt Coordination for a Drama Series, Miniseries, or Movie in 2014 by the **Primetime Emmy Awards**. | INCORRECT; predicted_answer: The **Academy of Television Arts & Sciences** (the organization that presents the **Primetime Emmy Awards**) awarded *The Blacklist* for Outstanding Stunt Coordination for a Drama Series, Miniseries, or Movie in 2014. |
| 151451 | What is the title of the documentary released in 2014 related to Busta Rhymes? | Nas: Time Is Illmatic | INCORRECT; predicted_answer: The title of the documentary released in 2014 related to Busta Rhymes is "Busta Rhymes: The Big Bang." | INCORRECT; predicted_answer: The documentary released in 2014 related to Busta Rhymes is titled **Everything or Nothing: The Untold Story of Busta Rhymes**. |
| 599 | What is the term used for the first person singular prefix conjugation in the Preterite form of Akkadian (Semitic)? | a-prus | INCORRECT; predicted_answer: The term used for the first person singular prefix conjugation in the Preterite form of Akkadian is the **"preterite prefix conjugation"** or more specifically the **"preterite 1st person singular prefix form"**. In Akkadian grammar, this form typically uses the prefix **"a-"** attached to the verb stem to indicate "I [verb]" in the preterite (past) tense. | INCORRECT; predicted_answer: The term for the first-person singular prefix conjugation in the Akkadian Preterite is the **"a-"** prefix (or simply the **a-** prefix). |
| 47864412 | What is the IPA pronunciation of the Nepali ligature formed by combining the letters क and ष? | IPA: /t͡sʰjʌ/, /ksʌ/ | INCORRECT; predicted_answer: The Nepali ligature formed by combining क (ka) and ष (ṣa) is क्ष. Its IPA pronunciation is [kʰʃ]. | INCORRECT; predicted_answer: The IPA pronunciation of the ligature **क्ष** (kṣa) in Nepali is **[ksʌ]**. |
| 57659 | How many football championships has Espérance Sportive de Tunis won? | 20 (acceptable range: anything between 19 and 21) | INCORRECT; predicted_answer: Espérance Sportive de Tunis has won 32 Tunisian Ligue Professionnelle 1 championships. | INCORRECT; predicted_answer: Espérance Sportive de Tunis has won **33** Tunisian Ligue Professionnelle 1 titles. |
| 359520 | How many films or television productions did Joan Jett appear in during the 2000s decade according to her filmography? | 9 (acceptable range: anything between 8 and 10) | INCORRECT; predicted_answer: Joan Jett appeared in 3 films or television productions during the 2000s decade according to her filmography. | INCORRECT; predicted_answer: According to her filmography, Joan Jett appeared in **4** film or television productions during the 2000s decade:  1.  **The Runner** (1999/2000) – Film (as Kaylee) 2.  **Walker, Texas Ranger** (2000) – TV Series (as Dierdre Harris) 3.  **The Sexina Files** (2007) – Film (as herself) 4.  **Lock and Roll Forever** (2008) – Film (as Charlotte) |
| 420162 | On what month, day, and year was Rai Ladinia launched? | September 26, 1988 | INCORRECT; predicted_answer: Rai Ladinia was launched on February 2, 1988. | INCORRECT; predicted_answer: Rai Ladinia was launched on **August 5, 1946**. |
| 485429 | In the context of martial morality in Chinese martial arts, what is the Pinyin romanization for the concept of humility? | qiān | INCORRECT; predicted_answer: The Pinyin romanization for the concept of humility in the context of martial morality in Chinese martial arts is **"qiān xū" (谦虚)**. | INCORRECT; predicted_answer: The Pinyin romanization for humility is **Qiānxū** (谦虚). |
| 363002 | In what year did Sandra Oh perform in the play titled 'Death and the Maiden' at the Victory Gardens Theater? | 2014 | INCORRECT; predicted_answer: Sandra Oh performed in the play "Death and the Maiden" at the Victory Gardens Theater in 1994. | INCORRECT; predicted_answer: Sandra Oh performed in *Death and the Maiden* at the Victory Gardens Theater in **2004**. |
| 32611 | Vietnam War |  | not run | not run |
| 9316 | England |  | not run | not run |
| 22093 | National Basketball Association |  | not run | not run |
| 17416221 | South Africa |  | not run | not run |
| 5489 | Chile |  | not run | not run |
| 13277 | Holy Roman Empire |  | not run | not run |
| 738 | Albania |  | not run | not run |
| 19261 | Monaco |  | not run | not run |
| 11857 | George Lucas |  | not run | not run |
| 14849 | Who is the person associated with the slogan "Land of Lincoln" in the state symbols of Illinois? | Abraham Lincoln | not run | not run |
| 8083 | Who won the Grammy Award for Best Rap Solo Performance in 1994? | Dr. Dre | CORRECT; predicted_answer: The Grammy Award for Best Rap Solo Performance in 1994 was won by Dr. Dre for the song "Let Me Ride." | not run |
| 199445 | Who was the England national football team player with 11 appearances and 6 goals in 2004? | Wayne Rooney | CORRECT; predicted_answer: The England national football team player with 11 appearances and 6 goals in 2004 was Wayne Rooney. | not run |
| 40010153 | Goa |  | not run | not run |
| 39776 | Denial-of-service attack |  | not run | not run |
| 5488 | Chad |  | not run | not run |
| 21355232 | Who is the person credited with the establishment of the National Park Service in the United States? | Stephen Mather | CORRECT; predicted_answer: Stephen Mather is credited with the establishment of the National Park Service in the United States. | not run |
| 292259 | Deutsche Welle |  | not run | not run |
| 1640 | Who succeeded Æthelred as king according to the chronology of Alfred the Great's reign? | Alfred | not run | not run |
| 31740 | Who is the person credited with founding the oldest institution of higher education in Michigan in 1817? | Lewis Cass | INCORRECT; predicted_answer: The person credited with founding the University of Michigan, the oldest institution of higher education in Michigan established in 1817, is Father Gabriel Richard. | INCORRECT; predicted_answer: The University of Michigan (originally the Catholepistemiad) was co-founded in 1817 by **Reverend John Monteith**, **Father Gabriel Richard**, and **Judge Augustus B. Woodward**. |
| 151603 | Who played the role of Gurd Canliss in the 1964 episode "Canliss" of the television program Rawhide? | Dean Martin | INCORRECT; predicted_answer: The role of Gurd Canliss in the 1964 episode "Canliss" of the television program Rawhide was played by actor John Anderson. | CORRECT; predicted_answer: **Dean Martin** played the role of Gurd Canliss. |
| 45367389 | Greater London |  | not run | not run |
| 105908 | Ford Mustang |  | not run | not run |
| 66958 | Renminbi |  | not run | not run |
| 34411 | Zodiac |  | not run | not run |
| 12186 | Guinea-Bissau |  | not run | not run |
| 60382764 | Who ascended the Chrysanthemum Throne as the 126th Emperor of Japan on 1 May 2019, marking the beginning of the Reiwa era? | Naruhito | not run | not run |
| 5643 | Channel Islands |  | not run | not run |
| 217231 | Which person provided commentary on the pilot episode in the DVD release of Curb Your Enthusiasm Season 1? | Larry David | CORRECT; predicted_answer: Larry David provided commentary on the pilot episode in the DVD release of Curb Your Enthusiasm Season 1. | not run |
| 41853326 | Who was the shirt sponsor for Inter Miami CF during the 2023 season? | XBTO | INCORRECT; predicted_answer: The shirt sponsor for Inter Miami CF during the 2023 season was Bally Sports. | CORRECT; predicted_answer: The shirt sponsor for Inter Miami CF during the 2023 season was **XBTO**. |
| 55440889 | Pixel 2 |  | not run | not run |
| 22948 | Who is the mother of the offspring named Polyphemus according to the earliest source listed? | Thoosa | not run | not run |
| 235916 | Who won the Interactive Achievement Award for Outstanding Achievement in Character Performance – Female for the work Enter the Matrix? | Jada Pinkett Smith | not run | not run |
| 33094374 | Telecommunications |  | not run | not run |
| 2924002 | Who was the winner of the British Dance Act award at the BRIT Awards most recently before the hiatus between 2005 and 2021? | Charli XCX | not run | not run |
| 84952 | Who succeeded Marvelous Marvin Hagler as the WBC middleweight champion after his reign ended on April 6, 1987? | Sugar Ray Leonard | not run | not run |
| 91195 | Wimbledon Championships |  | not run | not run |
| 235959 | Who played the role of Marjorie in the 1986 film Extremities? | Farrah Fawcett | CORRECT; predicted_answer: Farrah Fawcett played the role of Marjorie in the 1986 film Extremities. | not run |
| 30292 | Which person is restored to their ancestral throne at the climax of the quest in The Lord of the Rings according to Randel Helms's analysis? | Aragorn | not run | not run |
| 260996 | Who played the role of Clifford Glimmer in the 1999 stage production of Side Man? | Christian Slater | INCORRECT; predicted_answer: In the 1999 stage production of *Side Man*, the role of Clifford Glimmer was played by Frank Wood. | INCORRECT; predicted_answer: **Robert Sella** played the role of Clifford Glimmer in the 1999 Broadway production of *Side Man*. |
| 60921 | Battle of the Somme |  | not run | not run |
| 35723752 | PlayStation 4 |  | not run | not run |
| 34352 | Yerevan |  | not run | not run |
| 85023 | Appalachian Mountains |  | not run | not run |
| 65433 | Patagonia |  | not run | not run |
| 101359 | Gatwick Airport |  | not run | not run |
| 21026 | Meat Loaf |  | not run | not run |
| 30217 | Which geographic entity is described by the labour force distribution in the 2006 economy table showing 53% unskilled/manual workers? | Turks and Caicos Islands | not run | not run |
| 481605 | At which awards ceremony did Batman Begins win the Best Fantasy Film category in 2006? | Saturn Awards | CORRECT; predicted_answer: Batman Begins won the Best Fantasy Film category at the 2006 Saturn Awards. | not run |
| 149561 | Donna Summer |  | not run | not run |
| 347422 | Republika Srpska |  | not run | not run |
| 39458161 | Xbox One |  | not run | not run |
| 58846 | Which new French administrative region was formed by merging the former regions of Burgundy and Franche-Comté? | Bourgogne-Franche-Comté | not run | not run |
| 225502 | In which television program did Ann-Margret voice the character Ann-Margrock? | The Flintstones | not run | not run |
| 47734 | What is the headquarter city of the district in Chhattisgarh where Bhilai is the largest city? | Durg | not run | not run |
| 23473595 | Light-year |  | not run | not run |
| 158177 | Which university did Condoleezza Rice serve as provost from 1993 to 1999? | Stanford University | CORRECT; predicted_answer: Condoleezza Rice served as provost at Stanford University from 1993 to 1999. | not run |
| 30374 | In Taekwondo terminology, what is the Korean term for the 'Country Flag'? | South Korea | INCORRECT; predicted_answer: In Taekwondo terminology, the Korean term for the "Country Flag" is **"Gukgi" (국기)**. | INCORRECT; predicted_answer: The Korean term for the country flag is **Gukgi** (국기). |
| 184860 | In which city was the film 'My Blueberry Nights', featuring Norah Jones in her film debut, primarily set? | New York City | CORRECT; predicted_answer: The film "My Blueberry Nights," featuring Norah Jones in her film debut, was primarily set in New York City. | not run |
| 52812 | Humidity |  | not run | not run |
| 92408 | Pasadena, California |  | not run | not run |
| 563616 | Which city was the Ubisoft studio named 'Ubisoft Casablanca' located in before it closed in June 2016? | Casablanca | not run | not run |
| 5668 | Calcium |  | not run | not run |
| 16384 | In which television TV movie did John Belushi play the role of Ron Decline? | The Rutles: All You Need Is Cash | INCORRECT; predicted_answer: John Belushi played the role of Ron Decline in the television TV movie **"The Last Detail" (1973)**. | CORRECT; predicted_answer: John Belushi played Ron Decline in the 1978 TV movie **The Rutles: All You Need Is Cash**. |
| 255627 | Which city served as the national capital of the United States where the United States Capitol was first used as the meeting place of Congress starting November 17, 1800? | Washington, D.C. | CORRECT; predicted_answer: The city is Washington, D.C. | not run |
| 18482905 | In which city is the fictional setting of the British television soap opera Coronation Street located? | Weatherfield | INCORRECT; predicted_answer: The fictional setting of the British television soap opera Coronation Street is located in the city of Manchester. | CORRECT; predicted_answer: The fictional setting of *Coronation Street* is located in **Weatherfield**, a town in Greater Manchester. |
| 101965 | Which psoriasis type is classified under the ICD-10 code L40.4? | Guttate psoriasis | CORRECT; predicted_answer: The ICD-10 code L40.4 corresponds to "Guttate psoriasis." | not run |
| 342334 | Autopsy |  | not run | not run |
| 105391 | B movie |  | not run | not run |
| 569459 | White-tailed deer |  | not run | not run |
| 68761 | Publishing |  | not run | not run |
| 229275 | Lamb and mutton |  | not run | not run |
| 246920 | Visa Inc. |  | not run | not run |
| 2114995 | Dextromethorphan |  | not run | not run |
| 1625048 | Kingdom of Bohemia |  | not run | not run |
| 17278765 | Which city hosted the 1931 Rose Bowl game where No. 2 USC defeated No. 1 Tulane? | Pasadena | not run | not run |
| 96875 | Which parliament passed the act authorizing the construction of the Great Western Railway? | Parliament of the United Kingdom | CORRECT; predicted_answer: The British Parliament passed the act authorizing the construction of the Great Western Railway. | not run |
| 19006979 | Mac (computer) |  | not run | not run |
| 53273 | Which academic program at Duke University holds the top national ranking as of 2026? | Physician Assistant | not run | not run |
| 400595 | In which film did Patricia Arquette play the role of Miss Katherine "Kissin' Kate" Barlow? | Holes | CORRECT; predicted_answer: Patricia Arquette played the role of Miss Katherine "Kissin' Kate" Barlow in the film *Holes* (2003). | not run |
| 48235 | Vaudeville |  | not run | not run |
| 39848 | Chevrolet |  | not run | not run |
| 42374 | Ljubljana |  | not run | not run |
| 23976719 | Which variant of football is associated with the Rugby Football Union established in 1871 and includes formats such as Sevens, Tens, and Beach? | Rugby union with minor modifications | CORRECT; predicted_answer: The variant of football associated with the Rugby Football Union established in 1871, which includes formats such as Sevens, Tens, and Beach, is **Rugby Union**. | not run |
| 306724 | In which video game did Eddie Guerrero make his first WWF/E video game appearance? | WWF No Mercy | INCORRECT; predicted_answer: Eddie Guerrero made his first WWF/E video game appearance in **WWF SmackDown!** released in 2000. | CORRECT; predicted_answer: Eddie Guerrero made his first WWF/E video game appearance in **WWF No Mercy**, released in 2000 for the Nintendo 64. |
| 85099 | Which company was the kit manufacturer for Watford F.C. during the 1993 to 1995 period? | Hummel | INCORRECT; predicted_answer: The kit manufacturer for Watford F.C. during the 1993 to 1995 period was Umbro. | CORRECT; predicted_answer: The kit manufacturer for Watford F.C. from 1993 to 1995 was **Hummel**. |
| 100180 | Iron Cross |  | not run | not run |
| 1644 | Algiers |  | not run | not run |
| 56636 | Which city is listed as a twin town or sister city of Colombo in the Morang District of Nepal? | Biratnagar | not run | not run |
| 188746 | What was the vote cast by Senator Barry Goldwater on the Civil Rights Act of 1964? | Nay | CORRECT; predicted_answer: Senator Barry Goldwater voted against the Civil Rights Act of 1964. | not run |
| 168576 | Which award did James Woods win for his performance in the animated program Hercules: The Animated Series? | Daytime Emmy Awards | CORRECT; predicted_answer: James Woods won a Daytime Emmy Award for his performance in the animated program *Hercules: The Animated Series*. | not run |
| 65153 | Tahiti |  | not run | not run |
| 77432 | Hypertension |  | not run | not run |
| 682403 | What is the name given to the number represented as 10 to the power of 100? | googol | CORRECT; predicted_answer: The number represented as 10 to the power of 100 is called a **googol**. | not run |
| 21189337 | In which film did David Duchovny play a character named Tom Warshaw and also serve as the writer and director? | House of D | CORRECT; predicted_answer: David Duchovny played the character Tom Warshaw and also served as the writer and director in the film **"House of D" (2004)**. | not run |
| 24109126 | Grand Rapids, Michigan |  | not run | not run |
| 40218034 | Fifty Shades of Grey (film) |  | not run | not run |
| 144968 | Inverness |  | not run | not run |
| 36762240 | What is the superorder classification of shrimp according to their scientific classification? | Eucarida | CORRECT; predicted_answer: Shrimp belong to the superorder **Eucarida** in their scientific classification. | not run |
| 45576 | County Donegal |  | not run | not run |
| 79915 | Baron |  | not run | not run |
| 500409 | A Coruña |  | not run | not run |
| 8080 | List of decades, centuries, and millennia |  | not run | not run |
| 143759 | North Yorkshire |  | not run | not run |
| 662351 | Which location served as the base camp for the Italy team during the 13th UEFA European Championship? | Baden bei Wien | INCORRECT; predicted_answer: The Italy team used the city of Seville, Spain, as their base camp during the 13th UEFA European Championship (Euro 2020). | CORRECT; predicted_answer: The Italy national team used **Baden bei Wien**, Austria, as their base camp during UEFA Euro 2008. |
| 7549995 | Elk |  | not run | not run |
| 156745 | Which award did the film music composer James Newton Howard win for Pretty Woman? | Film Music Award | CORRECT; predicted_answer: James Newton Howard won the BMI Film Music Award for Pretty Woman. | not run |
| 57905 | Sakha Republic |  | not run | not run |
| 43088 | What was the postseason result for the New York Yankees in the 1964 season under Yogi Berra's management? | Lost World Series | INCORRECT; predicted_answer: In the 1964 season under Yogi Berra's management, the New York Yankees did not make the postseason. They finished in 6th place in the American League and did not qualify for the playoffs. | CORRECT; predicted_answer: The New York Yankees lost the 1964 World Series to the St. Louis Cardinals in seven games. |
| 26457880 | Air India |  | not run | not run |
| 31730 | British Armed Forces |  | not run | not run |
| 18947898 | What is the origin nationality of the Amnesty International Secretary General who served from 1992 to 2001? | Senegal | CORRECT; predicted_answer: The Amnesty International Secretary General who served from 1992 to 2001 was Pierre Sané, and his origin nationality is Senegalese. | not run |
| 276773 | SAP |  | not run | not run |
| 70581 | St. John's, Newfoundland and Labrador |  | not run | not run |
| 5215 | Casino |  | not run | not run |
| 5659 | Chemical element |  | not run | not run |
| 275515 | Mont-Saint-Michel |  | not run | not run |
| 10134 | How many distinct regions of the electromagnetic spectrum are listed in the table describing their main interactions with matter? | 8 | not run | not run |
| 13677 | Hindus |  | not run | not run |
| 30498 | How many editions of the oldest and most prestigious of the three Grand Tours had been held as of 2025? | 112 | not run | not run |
| 15868164 | In how many Indian Premier League seasons did Mumbai Indians finish 1st in the league standing between 2008 and 2026? | 6 | not run | not run |
| 4446 | Booker Prize |  | not run | not run |
| 99627 | Mannheim |  | not run | not run |
| 23713759 | Hodgkin lymphoma |  | not run | not run |
| 149349 | Dortmund |  | not run | not run |
| 36991518 | How many prime ministers are listed for the administrative divisions of the Democratic Autonomous Administration of North and East Syria? | 2 | not run | not run |
| 158595 | How many times was Rupert Grint nominated for an award in the year 2011 according to the awards and nominations table? | 6 | not run | not run |
| 601399 | Display resolution |  | not run | not run |
| 232863 | How many BMI Cable Awards did The Fairly OddParents win according to the awards and nominations table? | 4 | not run | not run |
| 904826 | How many distinct alignments are shown in the alignment grid of Dungeons & Dragons? | 9 (acceptable range: anything between 8 and 10) | CORRECT; predicted_answer: The alignment grid in Dungeons & Dragons shows 9 distinct alignments. | not run |
| 250858 | Tramadol |  | not run | not run |
| 38264 | Granada |  | not run | not run |
| 481708 | Imperial Japanese Army |  | not run | not run |
| 43710 | Silicon dioxide |  | not run | not run |
| 20556859 | Matrix (mathematics) |  | not run | not run |
| 17740 | In which year was Louis Pasteur's publication titled 'Studies on Beer' released? | 1876 | not run | not run |
| 20646803 | How many types of degrees are listed as required education for becoming a professor? | 4 | not run | not run |
| 191280 | Private equity |  | not run | not run |
| 218746 | How many total points did Rob Brown score in the 1986–87 Western Hockey League season? | 212 (acceptable range: anything between 210 and 214) | CORRECT; predicted_answer: Rob Brown scored a total of 212 points in the 1986–87 Western Hockey League season. | not run |
| 276433 | How many episodes did Haley Joel Osment appear in for the television series Future Man? | 14 (acceptable range: anything between 13 and 15) | INCORRECT; predicted_answer: Haley Joel Osment appeared in 3 episodes of the television series *Future Man*. | CORRECT; predicted_answer: Haley Joel Osment appeared in **14 episodes** of *Future Man*. |
| 57877 | Sodium hydroxide |  | not run | not run |
| 32005912 | Grimes |  | not run | not run |
| 214179 | Ministry (band) |  | not run | not run |
| 407239 | The Indian Express |  | not run | not run |
| 76988 | What is the maximum duration in milliseconds of the PR interval as measured on a standard ECG graph paper? | 200 (acceptable range: anything between 198 and 202) | CORRECT; predicted_answer: The maximum normal duration of the PR interval on a standard ECG is **200 milliseconds**. | not run |
| 80482 | How many years did Ruud Lubbers serve as Prime Minister of the Netherlands during Beatrix's reign? | 12 (acceptable range: anything between 11 and 13) | CORRECT; predicted_answer: Ruud Lubbers served as Prime Minister of the Netherlands from 1982 to 1994. Queen Beatrix reigned from 1980 to 2013. Therefore, Lubbers served as Prime Minister for 12 years during Beatrix's reign. | not run |
| 35412202 | Wikidata |  | not run | not run |
| 15049 | How many years did Marvin Harrison play with the Indianapolis Colts? | 13 (acceptable range: anything between 12 and 14) | CORRECT; predicted_answer: Marvin Harrison played 13 years with the Indianapolis Colts, from 1996 to 2008. | not run |
| 1064 | How many clades are listed in the scientific classification of the almond tree? | 4 | not run | not run |
| 26873 | How many seconds are there in one day according to the definition based on the division of the day into hours, minutes, and seconds? | 86400 (acceptable range: anything between 85536 and 87264) | CORRECT; predicted_answer: There are 86,400 seconds in one day.  Calculation:   1 day = 24 hours   1 hour = 60 minutes   1 minute = 60 seconds    So,   24 × 60 × 60 = 86,400 seconds. | not run |
| 4595356 | 1910 United States census |  | not run | not run |
| 27856145 | Siena |  | not run | not run |
| 30403 | In the 3-state 2-symbol busy beaver state table, what is the next state when the machine is in state C and the scanned symbol is 1? | H | not run | not run |
| 195468 | Ring of Fire |  | not run | not run |
| 30418 | On what month, day, and year did the premiere of The Marriage of Figaro take place at the Burgtheater in Vienna? | May 1, 1786 | CORRECT; predicted_answer: The premiere of The Marriage of Figaro at the Burgtheater in Vienna took place on May 1, 1786. | not run |
| 211917 | In what year was the University of California, Santa Barbara established as an independent teachers college before joining the University of California system? | 1891 | INCORRECT; predicted_answer: The University of California, Santa Barbara was established as an independent teachers college in 1944 before joining the University of California system. | INCORRECT; predicted_answer: UC Santa Barbara was established as an independent teachers college (known as the **Santa Barbara State Teachers College**) in **1921**. |
| 31924 | In what year was the University of California, Davis established as an agricultural branch of the University of California system? | 1905 | CORRECT; predicted_answer: The University of California, Davis was established as an agricultural branch of the University of California system in 1905. | not run |
| 12628 | In what version of GIMP was the XCF file size extended to more than 4 GB? | 2.9.6 | INCORRECT; predicted_answer: The XCF file size was extended to more than 4 GB starting with GIMP version 2.10.20. | INCORRECT; predicted_answer: The XCF file size limit was extended beyond 4 GB in **GIMP 2.10.0**. |
| 40880638 | UEFA Euro 2024 |  | not run | not run |
| 2369 | Aston Martin |  | not run | not run |
| 87851 | Stoat |  | not run | not run |
| 34556 | On what month, day, and year was Rajiv Gandhi, former prime minister of India, assassinated? | May 21, 1991 | not run | not run |
| 46735704 | In what year was Kehlani nominated for the Grammy Award for Best Urban Contemporary Album for their album You Should Be Here? | 2016 | CORRECT; predicted_answer: Kehlani was nominated for the Grammy Award for Best Urban Contemporary Album for their album *You Should Be Here* in 2016. | not run |
| 19342760 | Seven Wonders of the Ancient World |  | not run | not run |
| 63376140 | On what month, day, and year was the first episode of the first season of Arcane originally released? | November 6, 2021 | CORRECT; predicted_answer: The first episode of the first season of Arcane was originally released on November 6, 2021. | not run |
| 521984 | In what year did Emily Watson play the role of Jacqueline du Pré in the film Hilary and Jackie? | 1998 | CORRECT; predicted_answer: Emily Watson played the role of Jacqueline du Pré in the film *Hilary and Jackie* in 1998. | not run |
| 59385 | In what year was the binomial name Amanita muscaria (L.) Lam. officially published? | 1783 | CORRECT; predicted_answer: The binomial name Amanita muscaria (L.) Lam. was officially published in 1783. | not run |
| 339183 | At what angle is the Chinese compass point labeled '乾 qián' located? | 315° | CORRECT; predicted_answer: The Chinese compass point labeled '乾 qián' is located at 315°. | not run |
| 733497 | Hydroxyzine |  | not run | not run |
| 439959 | In what year was Herb Alpert's studio album 'Whipped Cream & Other Delights' released? | 1965 | CORRECT; predicted_answer: Herb Alpert's studio album "Whipped Cream & Other Delights" was released in 1965. | not run |
| 39345917 | Big Hero 6 (film) |  | not run | not run |
| 385155 | In what year did Guglielmo Marconi receive the Nobel Prize in Physics? | 1909 | CORRECT; predicted_answer: Guglielmo Marconi received the Nobel Prize in Physics in 1909. | not run |
| 53762 | In what year did David Niven win the Academy Award for Best Actor? | 1958 | CORRECT; predicted_answer: David Niven won the Academy Award for Best Actor in 1958. | not run |
| 2209490 | Romanization of Arabic |  | not run | not run |
| 422038 | Vigo |  | not run | not run |
| 23906 | Peterborough |  | not run | not run |
| 67923 | East Sussex |  | not run | not run |
| 1161220 | Khushbu Sundar |  | not run | not run |
| 47498 | All your base are belong to us |  | not run | not run |
| 113933 | Iowa City, Iowa |  | not run | not run |
| 22461 | Osteoporosis |  | not run | not run |
| 129619 | In what year did the film Ghost win the Academy Award for Best Supporting Actress? | 1991 | CORRECT; predicted_answer: The film *Ghost* won the Academy Award for Best Supporting Actress in 1991. | not run |
| 540317 | In what year range was the Ford Explorer rated as Marginal for the small overlap frontal offset on the driver side by NHTSA? | 2013-2019 | INCORRECT; predicted_answer: The Ford Explorer was rated as Marginal for the small overlap frontal offset on the driver side by NHTSA in the year range 2011 to 2015. | INCORRECT; predicted_answer: The Ford Explorer was rated **Marginal** for the driver-side small overlap frontal offset test for the model years **2011 through 2019**.  *(Note: This specific crash test is conducted by the **IIHS** (Insurance Institute for Highway Safety), rather than the NHTSA, which performs different frontal and side impact tests.)* |


## Rejected And Rerun Decisions

| Page ID | Stage | Exact reason | Page/question |
| ---: | --- | --- | --- |
| 32611 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=24` | Vietnam War |
| 9316 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=trillion` | England |
| 22093 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | National Basketball Association |
| 17416221 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km` | South Africa |
| 5489 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km` | Chile |
| 13277 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=9` | Holy Roman Empire |
| 738 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=13` | Albania |
| 19261 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | Monaco |
| 11857 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | George Lucas |
| 14849 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | Who is the person associated with the slogan "Land of Lincoln" in the state symbols of Illinois? |
| 8083 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who won the Grammy Award for Best Rap Solo Performance in 1994? |
| 199445 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who was the England national football team player with 11 appearances and 6 goals in 2004? |
| 40010153 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=2` | Goa |
| 39776 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=2` | Denial-of-service attack |
| 5488 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:active` | Chad |
| 21355232 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who is the person credited with the establishment of the National Park Service in the United States? |
| 292259 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any person-related data; only language and broadcast dates are listed.` | Deutsche Welle |
| 1640 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | Who succeeded Æthelred as king according to the chronology of Alfred the Great's reign? |
| 31740 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | Who is the person credited with founding the oldest institution of higher education in Michigan in 1817? |
| 151603 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who played the role of Gurd Canliss in the 1964 episode "Canliss" of the television program Rawhide? |
| 45367389 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | Greater London |
| 105908 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=10` | Ford Mustang |
| 66958 | `route_generation` | `wikipedia_infobox_llm_discarded:No person answer type supported by the top three tables on the Renminbi page.` | Renminbi |
| 34411 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=14` | Zodiac |
| 12186 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=10` | Guinea-Bissau |
| 60382764 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | Who ascended the Chrysanthemum Throne as the 126th Emperor of Japan on 1 May 2019, marking the beginning of the Reiwa era? |
| 5643 | `route_generation` | `wikipedia_infobox_llm_discarded:The only available table is an infobox with no person-related data or any factual entries suitable for a single-person answer question.` | Channel Islands |
| 217231 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which person provided commentary on the pilot episode in the DVD release of Curb Your Enthusiasm Season 1? |
| 41853326 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who was the shirt sponsor for Inter Miami CF during the 2023 season? |
| 55440889 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=g` | Pixel 2 |
| 22948 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | Who is the mother of the offspring named Polyphemus according to the earliest source listed? |
| 235916 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | Who won the Interactive Achievement Award for Outstanding Achievement in Character Performance – Female for the work Enter the Matrix? |
| 33094374 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Telecommunications |
| 2924002 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_time_invariance_forbidden_phrase:recent` | Who was the winner of the British Dance Act award at the BRIT Awards most recently before the hiatus between 2005 and 2021? |
| 84952 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_3:answer_in_title` | Who succeeded Marvelous Marvin Hagler as the WBC middleweight champion after his reign ended on April 6, 1987? |
| 91195 | `route_generation` | `wikipedia_infobox_llm_discarded:The only table available does not contain any person names or data suitable for a Person answer type question.` | Wimbledon Championships |
| 235959 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who played the role of Marjorie in the 1986 film Extremities? |
| 30292 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Which person is restored to their ancestral throne at the climax of the quest in The Lord of the Rings according to Randel Helms's analysis? |
| 260996 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | Who played the role of Clifford Glimmer in the 1999 stage production of Side Man? |
| 60921 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=12` | Battle of the Somme |
| 35723752 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=m` | PlayStation 4 |
| 34352 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,millimetres` | Yerevan |
| 85023 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=feet,ft,meters` | Appalachian Mountains |
| 65433 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km` | Patagonia |
| 101359 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=24` | Gatwick Airport |
| 21026 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any place names or geographic entities related to the films, only film titles, years, roles, and notes.` | Meat Loaf |
| 30217 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:table` | Which geographic entity is described by the labour force distribution in the 2006 economy table showing 53% unskilled/manual workers? |
| 481605 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | At which awards ceremony did Batman Begins win the Best Fantasy Film category in 2006? |
| 149561 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=pound` | Donna Summer |
| 347422 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:present` | Republika Srpska |
| 39458161 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Xbox One |
| 58846 | `rewrite_surface` | `rewrite_guard_rejected:forbidden_temporal_phrase` | Which new French administrative region was formed by merging the former regions of Burgundy and Franche-Comté? |
| 225502 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | In which television program did Ann-Margret voice the character Ann-Margrock? |
| 47734 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | What is the headquarter city of the district in Chhattisgarh where Bhilai is the largest city? |
| 23473595 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_approximate_tables:approximate,approximately` | Light-year |
| 158177 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which university did Condoleezza Rice serve as provost from 1993 to 1999? |
| 30374 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In Taekwondo terminology, what is the Korean term for the 'Country Flag'? |
| 184860 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which city was the film 'My Blueberry Nights', featuring Norah Jones in her film debut, primarily set? |
| 52812 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=oz,yd,g` | Humidity |
| 92408 | `route_generation` | `wikipedia_infobox_llm_discarded:The only table available is an incomplete climate chart with no factual place data to form a valid single-answer Place question.` | Pasadena, California |
| 563616 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | Which city was the Ubisoft studio named 'Ubisoft Casablanca' located in before it closed in June 2016? |
| 5668 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mg` | Calcium |
| 16384 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which television TV movie did John Belushi play the role of Ron Decline? |
| 255627 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which city served as the national capital of the United States where the United States Capitol was first used as the meeting place of Congress starting November 17, 1800? |
| 18482905 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which city is the fictional setting of the British television soap opera Coronation Street located? |
| 101965 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which psoriasis type is classified under the ICD-10 code L40.4? |
| 342334 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:present` | Autopsy |
| 105391 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:active` | B movie |
| 569459 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=1` | White-tailed deer |
| 68761 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=36` | Publishing |
| 229275 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=18` | Lamb and mutton |
| 246920 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million,billion` | Visa Inc. |
| 2114995 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=15` | Dextromethorphan |
| 1625048 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km2` | Kingdom of Bohemia |
| 17278765 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | Which city hosted the 1931 Rose Bowl game where No. 2 USC defeated No. 1 Tulane? |
| 96875 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which parliament passed the act authorizing the construction of the Great Western Railway? |
| 19006979 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | Mac (computer) |
| 53273 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | Which academic program at Duke University holds the top national ranking as of 2026? |
| 400595 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which film did Patricia Arquette play the role of Miss Katherine "Kissin' Kate" Barlow? |
| 48235 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=1` | Vaudeville |
| 39848 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=41` | Chevrolet |
| 42374 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Ljubljana |
| 23976719 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which variant of football is associated with the Rugby Football Union established in 1871 and includes formats such as Sevens, Tens, and Beach? |
| 306724 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which video game did Eddie Guerrero make his first WWF/E video game appearance? |
| 85099 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which company was the kit manufacturer for Watford F.C. during the 1993 to 1995 period? |
| 100180 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=5` | Iron Cross |
| 1644 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=42` | Algiers |
| 56636 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | Which city is listed as a twin town or sister city of Colombo in the Morang District of Nepal? |
| 188746 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What was the vote cast by Senator Barry Goldwater on the Civil Rights Act of 1964? |
| 168576 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which award did James Woods win for his performance in the animated program Hercules: The Animated Series? |
| 65153 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km,mi` | Tahiti |
| 77432 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Hypertension |
| 682403 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the name given to the number represented as 10 to the power of 100? |
| 21189337 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which film did David Duchovny play a character named Tom Warshaw and also serve as the writer and director? |
| 24109126 | `route_generation` | `wikipedia_infobox_llm_discarded:The only available table is an empty or incomplete climate chart with no factual data to form a valid question with a single indisputable answer of type Other.` | Grand Rapids, Michigan |
| 40218034 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | Fifty Shades of Grey (film) |
| 144968 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=foot` | Inverness |
| 36762240 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the superorder classification of shrimp according to their scientific classification? |
| 45576 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=22` | County Donegal |
| 79915 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_social_science_research:population` | Baron |
| 500409 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=feet,metres` | A Coruña |
| 8080 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=6` | List of decades, centuries, and millennia |
| 143759 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | North Yorkshire |
| 662351 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which location served as the base camp for the Italy team during the 13th UEFA European Championship? |
| 7549995 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=27` | Elk |
| 156745 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which award did the film music composer James Newton Howard win for Pretty Woman? |
| 57905 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=126` | Sakha Republic |
| 43088 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What was the postseason result for the New York Yankees in the 1964 season under Yogi Berra's management? |
| 26457880 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=tonnes` | Air India |
| 31730 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=16` | British Armed Forces |
| 18947898 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the origin nationality of the Amnesty International Secretary General who served from 1992 to 2001? |
| 276773 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=13` | SAP |
| 70581 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,ft,m` | St. John's, Newfoundland and Labrador |
| 5215 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=12` | Casino |
| 5659 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | Chemical element |
| 275515 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:alpha_character_rate=0.2278` | Mont-Saint-Michel |
| 10134 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | How many distinct regions of the electromagnetic spectrum are listed in the table describing their main interactions with matter? |
| 13677 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=12` | Hindus |
| 30498 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | How many editions of the oldest and most prestigious of the three Grand Tours had been held as of 2025? |
| 15868164 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | In how many Indian Premier League seasons did Mumbai Indians finish 1st in the league standing between 2008 and 2026? |
| 4446 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=60` | Booker Prize |
| 99627 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:incumbent` | Mannheim |
| 23713759 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_approximate_tables:approximately` | Hodgkin lymphoma |
| 149349 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=19` | Dortmund |
| 36991518 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | How many prime ministers are listed for the administrative divisions of the Democratic Autonomous Administration of North and East Syria? |
| 158595 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:table` | How many times was Rupert Grint nominated for an award in the year 2011 according to the awards and nominations table? |
| 601399 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=45` | Display resolution |
| 232863 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:table` | How many BMI Cable Awards did The Fairly OddParents win according to the awards and nominations table? |
| 904826 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many distinct alignments are shown in the alignment grid of Dungeons & Dragons? |
| 250858 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ml` | Tramadol |
| 38264 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=36` | Granada |
| 481708 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=30` | Imperial Japanese Army |
| 43710 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=14` | Silicon dioxide |
| 20556859 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=10` | Matrix (mathematics) |
| 17740 | `route_generation` | `wikipedia_infobox_answer_type_not_allowed:answer_type_not_allowed:Number; allowed=Number` | In which year was Louis Pasteur's publication titled 'Studies on Beer' released? |
| 20646803 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | How many types of degrees are listed as required education for becoming a professor? |
| 191280 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=15` | Private equity |
| 218746 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many total points did Rob Brown score in the 1986–87 Western Hockey League season? |
| 276433 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many episodes did Haley Joel Osment appear in for the television series Future Man? |
| 57877 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ml,g,m` | Sodium hydroxide |
| 32005912 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Grimes |
| 214179 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | Ministry (band) |
| 407239 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_approximate_tables:approximate` | The Indian Express |
| 76988 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the maximum duration in milliseconds of the PR interval as measured on a standard ECG graph paper? |
| 80482 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many years did Ruud Lubbers serve as Prime Minister of the Netherlands during Beatrix's reign? |
| 35412202 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=2` | Wikidata |
| 15049 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many years did Marvin Harrison play with the Indianapolis Colts? |
| 1064 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | How many clades are listed in the scientific classification of the almond tree? |
| 26873 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many seconds are there in one day according to the definition based on the division of the day into hours, minutes, and seconds? |
| 4595356 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=153` | 1910 United States census |
| 27856145 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=15` | Siena |
| 30403 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:table` | In the 3-state 2-symbol busy beaver state table, what is the next state when the machine is in state C and the scanned symbol is 1? |
| 195468 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:caption:active` | Ring of Fire |
| 30418 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did the premiere of The Marriage of Figaro take place at the Burgtheater in Vienna? |
| 211917 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year was the University of California, Santa Barbara established as an independent teachers college before joining the University of California system? |
| 31924 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the University of California, Davis established as an agricultural branch of the University of California system? |
| 12628 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what version of GIMP was the XCF file size extended to more than 4 GB? |
| 40880638 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=54` | UEFA Euro 2024 |
| 2369 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=114` | Aston Martin |
| 87851 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=5` | Stoat |
| 34556 | `rewrite_surface` | `rewrite_guard_rejected:forbidden_temporal_phrase` | On what month, day, and year was Rajiv Gandhi, former prime minister of India, assassinated? |
| 46735704 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was Kehlani nominated for the Grammy Award for Best Urban Contemporary Album for their album You Should Be Here? |
| 19342760 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:incomplete` | Seven Wonders of the Ancient World |
| 63376140 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the first episode of the first season of Arcane originally released? |
| 521984 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Emily Watson play the role of Jacqueline du Pré in the film Hilary and Jackie? |
| 59385 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the binomial name Amanita muscaria (L.) Lam. officially published? |
| 339183 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | At what angle is the Chinese compass point labeled '乾 qián' located? |
| 733497 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=2` | Hydroxyzine |
| 439959 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was Herb Alpert's studio album 'Whipped Cream & Other Delights' released? |
| 39345917 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Big Hero 6 (film) |
| 385155 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Guglielmo Marconi receive the Nobel Prize in Physics? |
| 53762 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did David Niven win the Academy Award for Best Actor? |
| 2209490 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ha,g` | Romanization of Arabic |
| 422038 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,metres,millimetres,m` | Vigo |
| 23906 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=29` | Peterborough |
| 67923 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | East Sussex |
| 1161220 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Khushbu Sundar |
| 47498 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | All your base are belong to us |
| 113933 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Iowa City, Iowa |
| 22461 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Osteoporosis |
| 129619 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the film Ghost win the Academy Award for Best Supporting Actress? |
| 540317 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year range was the Ford Explorer rated as Marginal for the small overlap frontal offset on the driver side by NHTSA? |


