# Route 3 Streaming Wikipedia Page-ID Walkthrough - 2026-05-23

## Stats

- Run group ID: `wikipedia_stream_recipe_40_each_answer_type_single_fact_2026_05_23`
- Run segment ID: `recipe_combined`
- Artifact manifest: ``
- Mode: `page_id_stream_recipe`
- Page source: `table-search`
- Table-search queries: `insource:"wikitable"`
- Attempted page IDs: 208
- Unique attempted page IDs: 200
- Stream state reset at run start: yes
- Auto rerun pool once: yes
- Auto-rerun attempted page IDs: 0
- Accepted QAs: 14
- Rejected QAs/pages: 180
- Transient rerun attempts during run: 14
- Wall-clock runtime: 906.1088s
- DuckDuckGo top K: 5
- Generated search queries per QA: 3
- DuckDuckGo parallel queries: 3
- Route 3 reasoning_type constraint: `single_fact`
- Route 3 answer_type constraint: `Person, Place, Other, Number, Date`
- Route 3 table filter modes: `no_picture_heavy_tables, no_incomplete_tables, not_number_dominant, no_social_science_research`
- Page-id bounds: None to None
- Stream state: `separate_segment_stream_states`
- Accepted output: `D:\Study\AI\My-research\Wikidata_Framework\outputs\wikipedia_stream_recipe_40_each_answer_type_single_fact_2026_05_23_accepted.jsonl`
- Rejected output: `D:\Study\AI\My-research\Wikidata_Framework\outputs\wikipedia_stream_recipe_40_each_answer_type_single_fact_2026_05_23_rejected.jsonl`
- Domain policy: `domain_and_subdomain_optional_for_page_id_streaming`
- Rerun pool after run: `67749, 168263, 168576, 214179, 400595, 43745773`

### Recipe Segments

| Configured answer_type | Record limit | Attempted page IDs | Accepted | Rejected | Rerun |
| --- | ---: | ---: | ---: | ---: | ---: |
| Person | 40 | 40 | 2 | 38 | 0 |
| Place | 40 | 40 | 4 | 36 | 0 |
| Other | 40 | 44 | 4 | 34 | 6 |
| Number | 40 | 41 | 2 | 37 | 2 |
| Date | 40 | 43 | 2 | 35 | 6 |

### Survival By Layer

| Layer | Entered | Failed | Survived | Layer survival | Cumulative survival |
| --- | ---: | ---: | ---: | ---: | ---: |
| Page-id reservation | 208 | 0 | 208 | 100.0% | 100.0% |
| Unresolved or returned to rerun pool | 208 | 0 | 208 | 100.0% | 100.0% |
| Page extraction, table grading, and QA generation | 208 | 101 | 107 | 51.4% | 51.4% |
| Rewrite and surface validation | 107 | 16 | 91 | 85.0% | 43.8% |
| DuckDuckGo long-tail filtering | 91 | 10 | 81 | 89.0% | 38.9% |
| Second-stage model grading | 81 | 48 | 33 | 40.7% | 15.9% |
| Shared route-aware validation | 33 | 5 | 28 | 84.9% | 13.5% |
| Deduplication | 28 | 0 | 28 | 100.0% | 13.5% |
| Other rejection | 28 | 0 | 28 | 100.0% | 13.5% |

### Failure Reasons

| Stage | Reason | Count |
| --- | --- | ---: |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant` | 58 |
| `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded` | 48 |
| `route_generation` | `wikipedia_infobox_generation_error:HTTPError:HTTP Error 429: Too Many Requests` | 19 |
| `search_longtail` | `search_longtail_verifier_rejected` | 10 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables` | 7 |
| `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | 5 |
| `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:table` | 4 |
| `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | 3 |
| `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | 3 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | 3 |
| `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | 2 |
| `rewrite_surface` | `rewrite_guard_rejected:forbidden_temporal_phrase` | 2 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:active` | 2 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:present` | 2 |
| `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:example` | 1 |
| `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_time_invariance_forbidden_phrase:recent` | 1 |
| `route_generation` | `wikipedia_infobox_answer_type_not_allowed:answer_type_not_allowed:Other; allowed=Other` | 1 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:caption:active` | 1 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:incumbent` | 1 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No Person answer available in the top-ranked tables for a single_fact question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No person names are provided in the top-ranked table to form a valid single-answer question about a person.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No suitable factual place-based data available in the top-ranked table to generate a valid single_fact question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No suitable person-type single fact question can be generated from the provided table as it contains no relevant data.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No usable factual data in the top-ranked table to generate a valid single-answer question.` | 1 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables` | 1 |

### Answer Type Stats

| Scope | Answer type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `Date` | 2 | 20 | 22 | 9.1% |
| Current Run Records | `Number` | 2 | 13 | 15 | 13.3% |
| Current Run Records | `Other` | 4 | 13 | 17 | 23.5% |
| Current Run Records | `Person` | 2 | 19 | 21 | 9.5% |
| Current Run Records | `Place` | 4 | 14 | 18 | 22.2% |
| Current Run Records | `unknown` | 0 | 101 | 101 | 0.0% |

### Reasoning Type Stats

| Scope | Reasoning type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `single_fact` | 14 | 180 | 194 | 7.2% |

### Rerun Pool After Run

| Page ID | Exact reason |
| ---: | --- |
| 67749 | `search_longtail_verifier_error` |
| 168263 | `search_longtail_verifier_error` |
| 168576 | `search_longtail_verifier_error` |
| 214179 | `search_longtail_verifier_error` |
| 400595 | `search_longtail_verifier_error` |
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
| `candidate_processing_seconds` | 194 | 949.7275 | 4.8955 | 27.0885 |
| `duckduckgo_search_seconds` | 77 | 343.8185 | 4.4652 | 14.3825 |
| `first_paragraph_extract_seconds` | 99 | 56.9905 | 0.5757 | 3.0371 |
| `llm_question_generation_seconds` | 99 | 418.6643 | 4.2289 | 9.3558 |
| `number_reference_margin_seconds` | 77 | 0.0009 | 0.0000 | 0.0002 |
| `page_fetch_seconds` | 175 | 396.4919 | 2.2657 | 20.7229 |
| `rewrite_seconds` | 93 | 0.0000 | 0.0000 | 0.0000 |
| `second_stage_grading_seconds` | 67 | 605.7737 | 9.0414 | 21.5996 |
| `table_parse_seconds` | 175 | 333.8757 | 1.9079 | 12.5049 |
| `total_generation_seconds` | 194 | 1369.6267 | 7.0599 | 26.4981 |
| `total_processing_seconds` | 194 | 949.7275 | 4.8955 | 27.0885 |

## Accepted Candidates

| Page ID | Question | Answer | Source |
| ---: | --- | --- | --- |
| 34411 | Who is the brightest star in the constellation that the Sun stays in for approximately 7 days according to the 1977 IAU boundaries? | Antares | https://en.wikipedia.org/wiki/Zodiac |
| 19653842 | Who proposed the view of organisms as cooperating entities at differing levels of biological organisation? | Queller and Strassmann | https://en.wikipedia.org/wiki/Organism |
| 21026 | In which film did Meat Loaf play the character named Roy Budnitz? | Americathon | https://en.wikipedia.org/wiki/Meat_Loaf |
| 16384 | In which location was the TV movie featuring John Belushi as Ron Decline produced? | The Rutles: All You Need Is Cash | https://en.wikipedia.org/wiki/John_Belushi |
| 169833 | At which awards ceremony did Tracy Chapman win the Best International Album award in 1989? | Danish Music Awards | https://en.wikipedia.org/wiki/Tracy_Chapman |
| 101965 | Which place is associated with the ICD-10 code L40.3 for a type of psoriasis? | Pustulosis palmaris et plantaris | https://en.wikipedia.org/wiki/Psoriasis |
| 38962787 | Which association awarded The Blacklist for Outstanding Stunt Coordination for a Drama Series, Miniseries, or Movie in 2014? | Primetime Creative Arts Emmy Awards | https://en.wikipedia.org/wiki/The_Blacklist |
| 306724 | In which video game did Eddie Guerrero make his first appearance? | WCW vs. the World | https://en.wikipedia.org/wiki/Eddie_Guerrero |
| 682403 | Which authority is credited with naming both the large numbers googol and googolplex? | Kasner and Newman, dictionaries | https://en.wikipedia.org/wiki/Names_of_large_numbers |
| 57905 | Which time zone abbreviation corresponds to the time zone used in the districts of Abyysky, Allaikhovsky, Momsky, Nizhnekolymsky, Srednekolymsky, and Verkhnekolymsky in the Sakha Republic? | MAGT | https://en.wikipedia.org/wiki/Sakha_Republic |
| 23713759 | How many cycles of BEACOPP escalated regimen are tested in the German Hodgkin Study Group HD15 trial? | 8 | https://en.wikipedia.org/wiki/Hodgkin_lymphoma |
| 57659 | How many football championships has Espérance Sportive de Tunis won? | 20 | https://en.wikipedia.org/wiki/Tunis |
| 31924 | On what month, day, and year did Stanley B. Freeborn start his term as chancellor of the University of California, Davis? | September 25, 1958 | https://en.wikipedia.org/wiki/University_of_California,_Davis |
| 363002 | In what year did Sandra Oh perform the role of Paulina in the play Death and the Maiden at Victory Gardens Theater? | 2014 | https://en.wikipedia.org/wiki/Sandra_Oh |

## Second-Stage Filtering Responses

These are the small-model QA responses used by the second-stage filter: `openai/gpt-4.1-mini` and `google/gemini-3-flash-preview`.

| Page ID | Question | Reference answer | openai/gpt-4.1-mini | google/gemini-3-flash-preview |
| ---: | --- | --- | --- | --- |
| 34411 | Who is the brightest star in the constellation that the Sun stays in for approximately 7 days according to the 1977 IAU boundaries? | Antares | INCORRECT; predicted_answer: The Sun stays in the constellation **Libra** for approximately 7 days according to the 1977 IAU boundaries. The brightest star in Libra is **Zubeneschamali (Beta Librae)**. | INCORRECT; predicted_answer: The constellation is **Ophiuchus**, and its brightest star is **Rasalhague** (Alpha Ophiuchi). |
| 19653842 | Who proposed the view of organisms as cooperating entities at differing levels of biological organisation? | Queller and Strassmann | INCORRECT; predicted_answer: The view of organisms as cooperating entities at differing levels of biological organization was notably proposed by Ernst Mayr and further developed by biologists like Richard Dawkins and David Sloan Wilson, who emphasized multilevel selection theory. However, the concept is most closely associated with **David Sloan Wilson**, who extensively articulated the idea of cooperation and selection operating at multiple biological levels. | INCORRECT; predicted_answer: **Leo Buss** proposed this view in his 1987 book, *The Evolution of Individuality*. |
| 21026 | In which film did Meat Loaf play the character named Roy Budnitz? | Americathon | INCORRECT; predicted_answer: Meat Loaf played the character named Roy Budnitz in the film **"Fight Club" (1999)**. | INCORRECT; predicted_answer: Meat Loaf played Roy Budnitz in the 1980 film **Roadie**. |
| 16384 | In which location was the TV movie featuring John Belushi as Ron Decline produced? | The Rutles: All You Need Is Cash | INCORRECT; predicted_answer: The TV movie featuring John Belushi as Ron Decline, titled **"The Last Detail" (1973)**, was primarily filmed in **New York City** and **Washington, D.C.** | INCORRECT; predicted_answer: The TV movie, titled **The Rutles: All You Need Is Cash**, was primarily produced and filmed in **London, England**, with additional filming locations in **New York City**. |
| 169833 | At which awards ceremony did Tracy Chapman win the Best International Album award in 1989? | Danish Music Awards | INCORRECT; predicted_answer: Tracy Chapman won the Best International Album award in 1989 at the Brit Awards. | INCORRECT; predicted_answer: Tracy Chapman won the Best International Album award at the **1989 BRIT Awards**. |
| 101965 | Which place is associated with the ICD-10 code L40.3 for a type of psoriasis? | Pustulosis palmaris et plantaris | INCORRECT; predicted_answer: The ICD-10 code L40.3 is associated with "Pustulosis palmaris et plantaris," which affects the palms of the hands and the soles of the feet. | INCORRECT; predicted_answer: ICD-10 code L40.3 refers to **Pustulosis palmaris et plantaris**, which is associated with the **palms of the hands** and the **soles of the feet**. |
| 38962787 | Which association awarded The Blacklist for Outstanding Stunt Coordination for a Drama Series, Miniseries, or Movie in 2014? | Primetime Creative Arts Emmy Awards | INCORRECT; predicted_answer: The Blacklist was awarded for Outstanding Stunt Coordination for a Drama Series, Miniseries, or Movie in 2014 by the **Primetime Emmy Awards**. | INCORRECT; predicted_answer: The **Academy of Television Arts & Sciences** (the organization that presents the **Primetime Emmy Awards**) awarded *The Blacklist* for Outstanding Stunt Coordination for a Drama Series, Miniseries, or Movie in 2014. |
| 306724 | In which video game did Eddie Guerrero make his first appearance? | WCW vs. the World | INCORRECT; predicted_answer: Eddie Guerrero made his first video game appearance in **WCW/nWo Revenge** for the Nintendo 64. | INCORRECT; predicted_answer: Eddie Guerrero made his first video game appearance in **Virtual Pro Wrestling** (released in 1996 for the PlayStation in Japan), where he appeared under his **Black Tiger** persona. |
| 682403 | Which authority is credited with naming both the large numbers googol and googolplex? | Kasner and Newman, dictionaries | INCORRECT; predicted_answer: The authority credited with naming both the large numbers googol and googolplex is the American mathematician Edward Kasner. | INCORRECT; predicted_answer: **Milton Sirotta**, the nine-year-old nephew of American mathematician Edward Kasner, is credited with naming both terms. |
| 57905 | Which time zone abbreviation corresponds to the time zone used in the districts of Abyysky, Allaikhovsky, Momsky, Nizhnekolymsky, Srednekolymsky, and Verkhnekolymsky in the Sakha Republic? | MAGT | INCORRECT; predicted_answer: The time zone abbreviation for the districts of Abyysky, Allaikhovsky, Momsky, Nizhnekolymsky, Srednekolymsky, and Verkhnekolymsky in the Sakha Republic is **VLAT** (Vladivostok Time), which is UTC+10. | INCORRECT; predicted_answer: The time zone abbreviation for those districts is **SRET** (Srednekolymsk Time). |
| 23713759 | How many cycles of BEACOPP escalated regimen are tested in the German Hodgkin Study Group HD15 trial? | 8 (acceptable range: anything between 7 and 9) | INCORRECT; predicted_answer: The German Hodgkin Study Group HD15 trial tested 2 to 4 cycles of the BEACOPP escalated regimen. | INCORRECT; predicted_answer: In the GHSG HD15 trial, patients were randomized to receive either **6 or 8 cycles** of escalated BEACOPP (compared against 8 cycles of BEACOPP-14). The trial concluded that **6 cycles** of escalated BEACOPP was the most effective and least toxic regimen. |
| 57659 | How many football championships has Espérance Sportive de Tunis won? | 20 (acceptable range: anything between 19 and 21) | INCORRECT; predicted_answer: Espérance Sportive de Tunis has won 32 Tunisian Ligue Professionnelle 1 championships. | INCORRECT; predicted_answer: Espérance Sportive de Tunis has won **33** Tunisian Ligue Professionnelle 1 titles. |
| 31924 | On what month, day, and year did Stanley B. Freeborn start his term as chancellor of the University of California, Davis? | September 25, 1958 | INCORRECT; predicted_answer: Stanley B. Freeborn started his term as chancellor of the University of California, Davis on July 1, 1958. | INCORRECT; predicted_answer: Stanley B. Freeborn started his term as chancellor of the University of California, Davis, on **July 1, 1952**. |
| 363002 | In what year did Sandra Oh perform the role of Paulina in the play Death and the Maiden at Victory Gardens Theater? | 2014 | INCORRECT; predicted_answer: Sandra Oh performed the role of Paulina in the play Death and the Maiden at Victory Gardens Theater in 1994. | INCORRECT; predicted_answer: Sandra Oh performed the role of Paulina in *Death and the Maiden* at Victory Gardens Theater in **2011**. |
| 9316 | England |  | not run | not run |
| 22093 | National Basketball Association |  | not run | not run |
| 17416221 | South Africa |  | not run | not run |
| 32611 | Vietnam War |  | not run | not run |
| 5489 | Chile |  | not run | not run |
| 13277 | Holy Roman Empire |  | not run | not run |
| 738 | Albania |  | not run | not run |
| 11857 | George Lucas |  | not run | not run |
| 19261 | Monaco |  | not run | not run |
| 14849 | Who is the person associated with the slogan "Land of Lincoln" in the state symbols of Illinois? | Abraham Lincoln | not run | not run |
| 31740 | Which school at the University of Michigan was ranked number 1 in the U.S. News Best Schools for Social Work in 2024? | School of Social Work | not run | not run |
| 21355232 | Which person is credited with the establishment of the National Park Service in the United States? | Stephen Mather | CORRECT; predicted_answer: Stephen Mather is credited with the establishment of the National Park Service in the United States. | not run |
| 292259 | Deutsche Welle |  | not run | not run |
| 40010153 | Goa |  | not run | not run |
| 8083 | Who won the Grammy Award for Producer of the Year, Non-Classical in 2001? | Dr. Dre | CORRECT; predicted_answer: The Grammy Award for Producer of the Year, Non-Classical in 2001 was won by Dr. Dre. | not run |
| 39776 | Denial-of-service attack |  | not run | not run |
| 5488 | Chad |  | not run | not run |
| 199445 | Who scored 8 goals for the England national team in the year 2014? | Wayne Rooney | CORRECT; predicted_answer: Wayne Rooney scored 8 goals for the England national team in the year 2014. | not run |
| 1640 | Who succeeded Æthelred as king according to the chronology of Alfred the Great? | Alfred | not run | not run |
| 151603 | Who played the role of Gurd Canliss in the 1964 episode "Canliss" of the television program Rawhide? | Dean Martin | INCORRECT; predicted_answer: The role of Gurd Canliss in the 1964 episode "Canliss" of the television program Rawhide was played by actor John Anderson. | CORRECT; predicted_answer: **Dean Martin** played the role of Gurd Canliss. |
| 60382764 | Who ascended the Chrysanthemum Throne as the 126th Emperor of Japan on 1 May 2019? | Naruhito | not run | not run |
| 66958 | Renminbi |  | not run | not run |
| 105908 | Ford Mustang |  | not run | not run |
| 217231 | Which person provided commentary on the pilot episode in the DVD release of Curb Your Enthusiasm Season 1? | Larry David | CORRECT; predicted_answer: Larry David provided commentary on the pilot episode in the DVD release of Curb Your Enthusiasm Season 1. | not run |
| 12186 | Guinea-Bissau |  | not run | not run |
| 45367389 | Who was the mayor of Greater London when the twin city agreement with Berlin was established in 2000? | Ken Livingstone | CORRECT; predicted_answer: The mayor of Greater London in 2000 was Ken Livingstone. He was the first Mayor of London, taking office in May 2000. | not run |
| 41853326 | Who was the shirt sponsor for Inter Miami CF in the 2021 season? | XBTO | INCORRECT; predicted_answer: The shirt sponsor for Inter Miami CF in the 2021 season was American Family Insurance. | CORRECT; predicted_answer: Inter Miami CF did not have a primary shirt sponsor for the first half of the 2021 season. In May 2021, they signed a deal with **XBTO**, a crypto finance firm, whose logo appeared on the jerseys for the remainder of the season. |
| 5643 | Channel Islands |  | not run | not run |
| 55440889 | Pixel 2 |  | not run | not run |
| 2924002 | Who most recently won the British Dance Act award at the BRIT Awards before the hiatus ended? | Charli XCX | not run | not run |
| 235916 | Who won the Interactive Achievement Award for Outstanding Achievement in Character Performance – Female for the work Enter the Matrix? | Jada Pinkett Smith | not run | not run |
| 33094374 | Telecommunications |  | not run | not run |
| 84952 | Who succeeded Marvelous Marvin Hagler as the WBC middleweight champion after his reign ended on April 6, 1987? | Sugar Ray Leonard | not run | not run |
| 22948 | Who is the mother of the offspring named Polyphemus according to the earliest source Hom. Ody.? | Thoosa | not run | not run |
| 30292 | Who is the descendant of kings restored to his ancestral throne in The Lord of the Rings according to Randel Helms's analysis of quest structure? | Aragorn | not run | not run |
| 235959 | Who played the role of Marjorie in the 1986 film Extremities? | Farrah Fawcett | CORRECT; predicted_answer: Farrah Fawcett played the role of Marjorie in the 1986 film Extremities. | not run |
| 91195 | Who holds the record for the most singles titles in the Open Era at the Wimbledon Gentlemen's Championships? | Roger Federer | CORRECT; predicted_answer: Roger Federer holds the record for the most singles titles in the Open Era at the Wimbledon Gentlemen's Championships, with 8 titles. | not run |
| 260996 | Who played the role of Clifford Glimmer in the 1999 stage production of Side Man? | Christian Slater | INCORRECT; predicted_answer: In the 1999 stage production of *Side Man*, the role of Clifford Glimmer was played by Frank Wood. | INCORRECT; predicted_answer: **Robert Sella** played the role of Clifford Glimmer in the 1999 Broadway production of *Side Man*. |
| 35723752 | PlayStation 4 |  | not run | not run |
| 60921 | Battle of the Somme |  | not run | not run |
| 34352 | Yerevan |  | not run | not run |
| 65433 | Patagonia |  | not run | not run |
| 85023 | Appalachian Mountains |  | not run | not run |
| 101359 | Gatwick Airport |  | not run | not run |
| 26941 | Which distributor released Spike Lee's 1992 directed feature film? | Warner Bros. | CORRECT; predicted_answer: Spike Lee's 1992 directed feature film, *Malcolm X*, was released by Warner Bros. Pictures. | not run |
| 30217 | In which place is the labour force distribution categorized by skill level with 53% unskilled/manual workers according to the 2006 data? | Turks and Caicos Islands | INCORRECT; predicted_answer: The place with a labour force distribution categorized by skill level showing 53% unskilled/manual workers according to the 2006 data is **India**. | INCORRECT; predicted_answer: According to 2006 data, **Dharavi** (Mumbai, India) is the place where the labor force distribution was categorized with approximately 53% unskilled or manual workers. |
| 481605 | At which awards ceremony did Batman Begins win the Best Fantasy Film category in 2006? | Saturn Awards | CORRECT; predicted_answer: Batman Begins won the Best Fantasy Film category at the 2006 Saturn Awards. | not run |
| 149561 | Donna Summer |  | not run | not run |
| 347422 | Republika Srpska |  | not run | not run |
| 58846 | Which new region did the former region of Lorraine become part of after the reform and mergers of regions in France? | Grand Est | not run | not run |
| 39458161 | Xbox One |  | not run | not run |
| 47734 | What is the headquarter of the district where Bhilai is the largest city in Chhattisgarh? | Durg | not run | not run |
| 225502 | In which place was the TV movie 'Who Will Love My Children?' featuring Ann-Margret as Lucile Fray produced? | United States | not run | not run |
| 184860 | https://en.wikipedia.org/w/index.php?pageid=184860 |  | not run | not run |
| 23473595 | https://en.wikipedia.org/w/index.php?pageid=23473595 |  | not run | not run |
| 158177 | In which place did Condoleezza Rice serve as Provost from 1993 to 1999? | Stanford University | CORRECT; predicted_answer: Condoleezza Rice served as Provost at Stanford University from 1993 to 1999. | not run |
| 30374 | In Taekwondo terminology, which place is represented by the Korean term '관' and the Hanja character '館'? | School | INCORRECT; predicted_answer: In Taekwondo terminology, the Korean term '관' (Hanja: 館) refers to a "dojang," which is the training hall or place where Taekwondo practice takes place. | CORRECT; predicted_answer: In Taekwondo terminology, the term **관 (Gwan)** and the Hanja character **館** represent a **school**, **institute**, or **hall**. It is most commonly used to refer to the original martial arts schools (the "Five Kwans") that formed the foundation of modern Taekwondo. |
| 52812 | Humidity |  | not run | not run |
| 92408 | Pasadena, California |  | not run | not run |
| 563616 | Which city was the Ubisoft studio named 'Related Designs' located in before it was closed in June 2014? | Mainz, Germany | CORRECT; predicted_answer: The Ubisoft studio named Related Designs was located in Mainz, Germany before it was closed in June 2014. | not run |
| 66524 | Which stadium is the home venue for the bandy club Uralsky Trubnik? | Uralsky Trubnik Stadium | CORRECT; predicted_answer: The home venue for the bandy club Uralsky Trubnik is Uralsky Trubnik Stadium. | not run |
| 5668 | Calcium |  | not run | not run |
| 18482905 | In which place is the British television soap opera Coronation Street first broadcast? | United Kingdom | INCORRECT; predicted_answer: The British television soap opera Coronation Street was first broadcast in Granada Television's studios in Manchester, England. | INCORRECT; predicted_answer: *Coronation Street* was first broadcast on **Granada Television** in the North West of England. |
| 255627 | Which city served as the location of the United States Congress when it first convened in the United States Capitol in 1800? | Washington, D.C. | CORRECT; predicted_answer: The city was Washington, D.C. | not run |
| 342334 | Autopsy |  | not run | not run |
| 105391 | B movie |  | not run | not run |
| 569459 | White-tailed deer |  | not run | not run |
| 68761 | Publishing |  | not run | not run |
| 229275 | Lamb and mutton |  | not run | not run |
| 246920 | Visa Inc. |  | not run | not run |
| 1625048 | Kingdom of Bohemia |  | not run | not run |
| 2114995 | Dextromethorphan |  | not run | not run |
| 17278765 | Which team won the 1931 Rose Bowl game that served as the title game for the Albert Russel Erskine Trophy and the Dickinson System's Knute Rockne Memorial Trophy? | USC | not run | not run |
| 96875 | Which parliament passed the act authorizing the construction of the Great Western Railway? | Parliament of the United Kingdom | CORRECT; predicted_answer: The British Parliament passed the act authorizing the construction of the Great Western Railway. | not run |
| 19006979 | Mac (computer) |  | not run | not run |
| 53273 | Which academic program at Duke University was ranked number one nationally as of 2026? | Physician Assistant | not run | not run |
| 48235 | Vaudeville |  | not run | not run |
| 23976719 | Which football code includes the variants Sevens, Tens, X, Touch, Tag, American flag, Mini, Beach, Snow, Tambo, Wheelchair, and Underwater? | Rugby Football Union | INCORRECT; predicted_answer: These variants are all part of Rugby. | CORRECT; predicted_answer: **Rugby union.** |
| 42374 | Ljubljana |  | not run | not run |
| 39848 | What racing category was the 1984 Chevrolet Corvette GTP built for? | IMSA GTP | CORRECT; predicted_answer: The 1984 Chevrolet Corvette GTP was built for the IMSA GTP (Grand Touring Prototype) racing category. | not run |
| 100180 | Iron Cross |  | not run | not run |
| 1644 | Algiers |  | not run | not run |
| 21189337 | In which film did David Duchovny play a character named Tom Warshaw and also serve as the writer and director? | House of D | CORRECT; predicted_answer: David Duchovny played the character Tom Warshaw and also served as the writer and director in the film **"House of D" (2004)**. | not run |
| 56636 | Which city suburb corresponds to the postal number Colombo 7 in the city limits of Colombo? | Cinnamon Gardens | CORRECT; predicted_answer: Colombo 7 corresponds to the suburb of Cinnamon Gardens in the city limits of Colombo. | not run |
| 188746 | What was the vote of Senator Barry Goldwater on the Civil Rights Act of 1964? | Nay | CORRECT; predicted_answer: Senator Barry Goldwater voted against the Civil Rights Act of 1964. | not run |
| 65153 | Tahiti |  | not run | not run |
| 77432 | Hypertension |  | not run | not run |
| 24109126 | Grand Rapids, Michigan |  | not run | not run |
| 2186423 | https://en.wikipedia.org/w/index.php?pageid=2186423 |  | not run | not run |
| 40218034 | https://en.wikipedia.org/w/index.php?pageid=40218034 |  | not run | not run |
| 662351 | https://en.wikipedia.org/w/index.php?pageid=662351 |  | not run | not run |
| 45576 | https://en.wikipedia.org/w/index.php?pageid=45576 |  | not run | not run |
| 79915 | https://en.wikipedia.org/w/index.php?pageid=79915 |  | not run | not run |
| 144968 | https://en.wikipedia.org/w/index.php?pageid=144968 |  | not run | not run |
| 143759 | https://en.wikipedia.org/w/index.php?pageid=143759 |  | not run | not run |
| 8080 | List of decades, centuries, and millennia |  | not run | not run |
| 36762240 | What is the superorder classification of shrimp according to their scientific classification? | Eucarida | CORRECT; predicted_answer: Shrimp belong to the superorder **Eucarida** in their scientific classification. | not run |
| 500409 | A Coruña |  | not run | not run |
| 7549995 | Elk |  | not run | not run |
| 43088 | In which year did Yogi Berra's team finish 1st in the American League during the regular season and lose the World Series to the St. Louis Cardinals? | 1964 | not run | not run |
| 599 | In the Afroasiatic numeral systems table, which language branch uses the term 'gáal' for the masculine form of the numeral one? | Beja | not run | not run |
| 151451 | What role did Busta Rhymes play in the 2000 film Shaft? | Rasaan | INCORRECT; predicted_answer: In the 2000 film *Shaft*, Busta Rhymes played the role of Pookie, a member of the antagonist's gang. | CORRECT; predicted_answer: Busta Rhymes played the role of **Rasaan**, the loyal driver and assistant to Samuel L. Jackson's character, John Shaft. |
| 26457880 | Air India |  | not run | not run |
| 156745 | Which award did the film Pretty Woman win for its film music? | Film Music Award | INCORRECT; predicted_answer: The film Pretty Woman won the ASCAP Award for its film music. | CORRECT; predicted_answer: The film *Pretty Woman* won the **BMI Film Music Award** in 1991, awarded to composer James Newton Howard. |
| 31730 | British Armed Forces |  | not run | not run |
| 18947898 | What is the country of origin of the Amnesty International Secretary General who served from 1992 to 2001? | Senegal | CORRECT; predicted_answer: The Amnesty International Secretary General who served from 1992 to 2001, Pierre Sané, is from Senegal. | not run |
| 47864412 | Which diacritic is combined with the letter ब to form the Nepali syllable 'बु'? | ◌ु | CORRECT; predicted_answer: The diacritic combined with the letter ब to form the Nepali syllable 'बु' is the "ु" (called "u-kar" or "short u vowel sign"). | not run |
| 85099 | Which company was the kit manufacturer for Watford F.C. during the 1993 to 1995 period? | Hummel | INCORRECT; predicted_answer: The kit manufacturer for Watford F.C. during the 1993 to 1995 period was Umbro. | CORRECT; predicted_answer: The kit manufacturer for Watford F.C. from 1993 to 1995 was **Hummel**. |
| 276773 | SAP |  | not run | not run |
| 70581 | St. John's, Newfoundland and Labrador |  | not run | not run |
| 10134 | How many distinct regions of the electromagnetic spectrum are listed in the table describing their main interactions with matter? | 8 | not run | not run |
| 5659 | Chemical element |  | not run | not run |
| 275515 | Mont-Saint-Michel |  | not run | not run |
| 5215 | Casino |  | not run | not run |
| 30498 | How many editions of the Tour de France had been held as of 2025? | 112 | not run | not run |
| 13677 | Hindus |  | not run | not run |
| 15868164 | In how many Indian Premier League seasons did Mumbai Indians finish 1st in the league standing between 2008 and 2026? | 6 | not run | not run |
| 359520 | In how many different years did Joan Jett appear in films or television shows according to her filmography? | 21 (acceptable range: anything between 20 and 22) | INCORRECT; predicted_answer: Joan Jett appeared in films or television shows in 9 different years according to her filmography. | INCORRECT; predicted_answer: According to her filmography, Joan Jett has appeared in films or television shows in **35** different years. |
| 99627 | Mannheim |  | not run | not run |
| 4446 | Booker Prize |  | not run | not run |
| 149349 | Dortmund |  | not run | not run |
| 904826 | How many distinct alignments are shown in the alignment grid of Dungeons & Dragons? | 9 (acceptable range: anything between 8 and 10) | CORRECT; predicted_answer: The alignment grid in Dungeons & Dragons shows 9 distinct alignments. | not run |
| 26873 | How many seconds are there in one day according to the definition based on the division of the day? | 86400 (acceptable range: anything between 85536 and 87264) | CORRECT; predicted_answer: There are 86,400 seconds in one day according to the standard division of the day:  - 1 day = 24 hours   - 1 hour = 60 minutes   - 1 minute = 60 seconds    So, \(24 \times 60 \times 60 = 86,400\) seconds. | not run |
| 36991518 | How many deputy prime ministers are listed for the Jazira Region in the Democratic Autonomous Administration of North and East Syria? | 3 | not run | not run |
| 601399 | Display resolution |  | not run | not run |
| 158595 | How many times was Rupert Grint nominated for an award in the year 2011 according to the awards and nominations table? | 6 | not run | not run |
| 232863 | How many times did The Fairly OddParents win the BMI Cable Award according to the awards and nominations table? | 4 | not run | not run |
| 250858 | https://en.wikipedia.org/w/index.php?pageid=250858 |  | not run | not run |
| 481708 | https://en.wikipedia.org/w/index.php?pageid=481708 |  | not run | not run |
| 43710 | https://en.wikipedia.org/w/index.php?pageid=43710 |  | not run | not run |
| 17740 | https://en.wikipedia.org/w/index.php?pageid=17740 |  | not run | not run |
| 38264 | https://en.wikipedia.org/w/index.php?pageid=38264 |  | not run | not run |
| 20646803 | https://en.wikipedia.org/w/index.php?pageid=20646803 |  | not run | not run |
| 20556859 | https://en.wikipedia.org/w/index.php?pageid=20556859 |  | not run | not run |
| 191280 | https://en.wikipedia.org/w/index.php?pageid=191280 |  | not run | not run |
| 276433 | https://en.wikipedia.org/w/index.php?pageid=276433 |  | not run | not run |
| 218746 | https://en.wikipedia.org/w/index.php?pageid=218746 |  | not run | not run |
| 57877 | Sodium hydroxide |  | not run | not run |
| 407239 | The Indian Express |  | not run | not run |
| 32005912 | Grimes |  | not run | not run |
| 76988 | What is the maximum duration in milliseconds of the PR interval as measured on a standard ECG graph paper? | 200 (acceptable range: anything between 198 and 202) | CORRECT; predicted_answer: The maximum normal duration of the PR interval on a standard ECG is **200 milliseconds**. | not run |
| 1064 | How many clades are listed in the scientific classification of the almond in the infobox? | 4 | not run | not run |
| 35412202 | Wikidata |  | not run | not run |
| 80482 | How many years did Ruud Lubbers serve as Prime Minister of the Netherlands during Beatrix's reign? | 12 (acceptable range: anything between 11 and 13) | CORRECT; predicted_answer: Ruud Lubbers served as Prime Minister of the Netherlands from 1982 to 1994. Queen Beatrix reigned from 1980 to 2013. Therefore, Lubbers served as Prime Minister for 12 years during Beatrix's reign. | not run |
| 15049 | How many years did Peyton Manning play for the Indianapolis Colts? | 14 (acceptable range: anything between 13 and 15) | CORRECT; predicted_answer: Peyton Manning played for the Indianapolis Colts for 14 years, from 1998 to 2011. | not run |
| 4595356 | 1910 United States census |  | not run | not run |
| 30403 | In the example state table for the 3-state 2-symbol busy beaver reduced to 5-tuples, what is the final state when the current state is C and the scanned symbol is 1? | H | not run | not run |
| 27856145 | Siena |  | not run | not run |
| 485429 | In the context of martial morality in Chinese martial arts, what is the Pinyin romanization for the concept of 'Respect'? | lǐ | not run | not run |
| 195468 | Ring of Fire |  | not run | not run |
| 211917 | In the National Program Rankings table, what is the ranking of the Physics program at the University of California, Santa Barbara? | 9 | not run | not run |
| 420162 | On what exact date was the Rai 3 television channel launched? | December 15, 1979 | CORRECT; predicted_answer: Rai 3 was launched on December 15, 1979. | not run |
| 30418 | On what month, day, and year did the premiere of The Marriage of Figaro take place at the Burgtheater in Vienna? | May 1, 1786 | CORRECT; predicted_answer: The premiere of The Marriage of Figaro at the Burgtheater in Vienna took place on May 1, 1786. | not run |
| 12628 | In what version of GIMP was the XCF file size extended to more than 4 GB? | 2.9.6 | INCORRECT; predicted_answer: The XCF file size was extended to more than 4 GB starting with GIMP version 2.10.20. | INCORRECT; predicted_answer: The XCF file size limit was extended beyond 4 GB in **GIMP 2.10.0**. |
| 34556 | On what exact date was Rajiv Gandhi, former prime minister of India, assassinated? | May 21, 1991 | not run | not run |
| 46735704 | In what year was Kehlani nominated for the Grammy Award for Best Urban Contemporary Album for their album You Should Be Here? | 2016 | CORRECT; predicted_answer: Kehlani was nominated for the Grammy Award for Best Urban Contemporary Album for their album *You Should Be Here* in 2016. | not run |
| 87851 | Stoat |  | not run | not run |
| 521984 | In what year did Emily Watson play the role of Jacqueline du Pré in the film Hilary and Jackie? | 1998 | CORRECT; predicted_answer: Emily Watson played the role of Jacqueline du Pré in the film *Hilary and Jackie* in 1998. | not run |
| 2369 | In what year was the Aston Martin DBR4 Formula One racecar introduced? | 1959 | CORRECT; predicted_answer: The Aston Martin DBR4 Formula One racecar was introduced in 1959. | not run |
| 63376140 | On what month, day, and year was the first episode of the first season of Arcane originally released? | November 6, 2021 | CORRECT; predicted_answer: The first episode of the first season of Arcane was originally released on November 6, 2021. | not run |
| 19342760 | Seven Wonders of the Ancient World |  | not run | not run |
| 40880638 | On what date was the host for UEFA Euro 2024 selected in Nyon, Switzerland? | September 27, 2018 | CORRECT; predicted_answer: The host for UEFA Euro 2024 was selected on 27 September 2018 in Nyon, Switzerland. | not run |
| 59385 | In what year was the binomial name Amanita muscaria (L.) Lam. officially established? | 1783 | CORRECT; predicted_answer: The binomial name Amanita muscaria (L.) Lam. was officially established in 1783. | not run |
| 339183 | At what angle is the Chinese compass point labeled '乾 qián' positioned? | 315° | CORRECT; predicted_answer: The Chinese compass point labeled '乾 qián' is positioned at 315°. | not run |
| 439959 | In what year was Herb Alpert's studio album 'Whipped Cream & Other Delights' released? | 1965 | CORRECT; predicted_answer: Herb Alpert's studio album "Whipped Cream & Other Delights" was released in 1965. | not run |
| 733497 | Hydroxyzine |  | not run | not run |
| 188257 | In what year did Paul McCartney and Wings first include Laurence Juber as a guitarist and Steve Holley as a drummer in their line-up? | 1978 | CORRECT; predicted_answer: Paul McCartney and Wings first included Laurence Juber as a guitarist and Steve Holley as a drummer in their line-up in 1978. | not run |
| 39345917 | Big Hero 6 (film) |  | not run | not run |
| 53762 | In what year did David Niven win the Academy Award for Best Actor? | 1958 | CORRECT; predicted_answer: David Niven won the Academy Award for Best Actor in 1958. | not run |
| 385155 | In what year did Guglielmo Marconi receive the Nobel Prize in Physics? | 1909 | CORRECT; predicted_answer: Guglielmo Marconi received the Nobel Prize in Physics in 1909. | not run |
| 2209490 | Romanization of Arabic |  | not run | not run |
| 422038 | Vigo |  | not run | not run |
| 23906 | Peterborough |  | not run | not run |
| 67923 | East Sussex |  | not run | not run |
| 1161220 | Khushbu Sundar |  | not run | not run |
| 47498 | All your base are belong to us |  | not run | not run |
| 113933 | Iowa City, Iowa |  | not run | not run |
| 22461 | Osteoporosis |  | not run | not run |
| 129619 | In what year did the film Ghost win the Academy Award for Best Supporting Actress? | 1991 | CORRECT; predicted_answer: The film *Ghost* won the Academy Award for Best Supporting Actress in 1991. | not run |
| 540317 | In what model year did the Ford Explorer first begin production? | 1991 | CORRECT; predicted_answer: The Ford Explorer first began production in the 1991 model year. | not run |


## Rejected And Rerun Decisions

| Page ID | Stage | Exact reason | Page/question |
| ---: | --- | --- | --- |
| 9316 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=trillion` | England |
| 22093 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | National Basketball Association |
| 17416221 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km` | South Africa |
| 32611 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=24` | Vietnam War |
| 5489 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km` | Chile |
| 13277 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=9` | Holy Roman Empire |
| 738 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km` | Albania |
| 11857 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | George Lucas |
| 19261 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | Monaco |
| 14849 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | Who is the person associated with the slogan "Land of Lincoln" in the state symbols of Illinois? |
| 31740 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_3:answer_in_title` | Which school at the University of Michigan was ranked number 1 in the U.S. News Best Schools for Social Work in 2024? |
| 21355232 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which person is credited with the establishment of the National Park Service in the United States? |
| 292259 | `route_generation` | `wikipedia_infobox_llm_discarded:No person names are provided in the top-ranked table to form a valid single-answer question about a person.` | Deutsche Welle |
| 40010153 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=2` | Goa |
| 8083 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who won the Grammy Award for Producer of the Year, Non-Classical in 2001? |
| 39776 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=2` | Denial-of-service attack |
| 5488 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:active` | Chad |
| 199445 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who scored 8 goals for the England national team in the year 2014? |
| 1640 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | Who succeeded Æthelred as king according to the chronology of Alfred the Great? |
| 151603 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who played the role of Gurd Canliss in the 1964 episode "Canliss" of the television program Rawhide? |
| 60382764 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | Who ascended the Chrysanthemum Throne as the 126th Emperor of Japan on 1 May 2019? |
| 66958 | `route_generation` | `wikipedia_infobox_llm_discarded:No Person answer available in the top-ranked tables for a single_fact question.` | Renminbi |
| 105908 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=10` | Ford Mustang |
| 217231 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which person provided commentary on the pilot episode in the DVD release of Curb Your Enthusiasm Season 1? |
| 12186 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=10` | Guinea-Bissau |
| 45367389 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who was the mayor of Greater London when the twin city agreement with Berlin was established in 2000? |
| 41853326 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who was the shirt sponsor for Inter Miami CF in the 2021 season? |
| 5643 | `route_generation` | `wikipedia_infobox_llm_discarded:No suitable person-type single fact question can be generated from the provided table as it contains no relevant data.` | Channel Islands |
| 55440889 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=g` | Pixel 2 |
| 2924002 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_time_invariance_forbidden_phrase:recent` | Who most recently won the British Dance Act award at the BRIT Awards before the hiatus ended? |
| 235916 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | Who won the Interactive Achievement Award for Outstanding Achievement in Character Performance – Female for the work Enter the Matrix? |
| 33094374 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Telecommunications |
| 84952 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_2:answer_in_title` | Who succeeded Marvelous Marvin Hagler as the WBC middleweight champion after his reign ended on April 6, 1987? |
| 22948 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Who is the mother of the offspring named Polyphemus according to the earliest source Hom. Ody.? |
| 30292 | `search_longtail` | `search_longtail_verifier_rejected:full_question:answer_in_title` | Who is the descendant of kings restored to his ancestral throne in The Lord of the Rings according to Randel Helms's analysis of quest structure? |
| 235959 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who played the role of Marjorie in the 1986 film Extremities? |
| 91195 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who holds the record for the most singles titles in the Open Era at the Wimbledon Gentlemen's Championships? |
| 260996 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | Who played the role of Clifford Glimmer in the 1999 stage production of Side Man? |
| 35723752 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=m` | PlayStation 4 |
| 60921 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=12` | Battle of the Somme |
| 34352 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,millimetres` | Yerevan |
| 65433 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km` | Patagonia |
| 85023 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=feet,ft,meters` | Appalachian Mountains |
| 101359 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | Gatwick Airport |
| 26941 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which distributor released Spike Lee's 1992 directed feature film? |
| 30217 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In which place is the labour force distribution categorized by skill level with 53% unskilled/manual workers according to the 2006 data? |
| 481605 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | At which awards ceremony did Batman Begins win the Best Fantasy Film category in 2006? |
| 149561 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=pound` | Donna Summer |
| 347422 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:present` | Republika Srpska |
| 58846 | `rewrite_surface` | `rewrite_guard_rejected:forbidden_temporal_phrase` | Which new region did the former region of Lorraine become part of after the reform and mergers of regions in France? |
| 39458161 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Xbox One |
| 47734 | `search_longtail` | `search_longtail_verifier_rejected:full_question:answer_in_title` | What is the headquarter of the district where Bhilai is the largest city in Chhattisgarh? |
| 225502 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In which place was the TV movie 'Who Will Love My Children?' featuring Ann-Margret as Lucile Fray produced? |
| 184860 | `route_generation` | `wikipedia_infobox_generation_error:HTTPError:HTTP Error 429: Too Many Requests` | https://en.wikipedia.org/w/index.php?pageid=184860 |
| 23473595 | `route_generation` | `wikipedia_infobox_generation_error:HTTPError:HTTP Error 429: Too Many Requests` | https://en.wikipedia.org/w/index.php?pageid=23473595 |
| 158177 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which place did Condoleezza Rice serve as Provost from 1993 to 1999? |
| 30374 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In Taekwondo terminology, which place is represented by the Korean term '관' and the Hanja character '館'? |
| 52812 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=oz,yd,g` | Humidity |
| 92408 | `route_generation` | `wikipedia_infobox_llm_discarded:No suitable factual place-based data available in the top-ranked table to generate a valid single_fact question.` | Pasadena, California |
| 563616 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which city was the Ubisoft studio named 'Related Designs' located in before it was closed in June 2014? |
| 66524 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which stadium is the home venue for the bandy club Uralsky Trubnik? |
| 5668 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mg` | Calcium |
| 18482905 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In which place is the British television soap opera Coronation Street first broadcast? |
| 255627 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which city served as the location of the United States Congress when it first convened in the United States Capitol in 1800? |
| 342334 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:present` | Autopsy |
| 105391 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:active` | B movie |
| 569459 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=1` | White-tailed deer |
| 68761 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Publishing |
| 229275 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=kt` | Lamb and mutton |
| 246920 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million,billion` | Visa Inc. |
| 1625048 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km2` | Kingdom of Bohemia |
| 2114995 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=15` | Dextromethorphan |
| 17278765 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | Which team won the 1931 Rose Bowl game that served as the title game for the Albert Russel Erskine Trophy and the Dickinson System's Knute Rockne Memorial Trophy? |
| 96875 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which parliament passed the act authorizing the construction of the Great Western Railway? |
| 19006979 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | Mac (computer) |
| 53273 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | Which academic program at Duke University was ranked number one nationally as of 2026? |
| 48235 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:image_cell_rate=1.0000` | Vaudeville |
| 23976719 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which football code includes the variants Sevens, Tens, X, Touch, Tag, American flag, Mini, Beach, Snow, Tambo, Wheelchair, and Underwater? |
| 42374 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Ljubljana |
| 39848 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What racing category was the 1984 Chevrolet Corvette GTP built for? |
| 100180 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:image_cell_rate=0.5000` | Iron Cross |
| 1644 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=42` | Algiers |
| 21189337 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which film did David Duchovny play a character named Tom Warshaw and also serve as the writer and director? |
| 56636 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which city suburb corresponds to the postal number Colombo 7 in the city limits of Colombo? |
| 188746 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What was the vote of Senator Barry Goldwater on the Civil Rights Act of 1964? |
| 65153 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km,mi` | Tahiti |
| 77432 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Hypertension |
| 24109126 | `route_generation` | `wikipedia_infobox_llm_discarded:No usable factual data in the top-ranked table to generate a valid single-answer question.` | Grand Rapids, Michigan |
| 2186423 | `route_generation` | `wikipedia_infobox_generation_error:HTTPError:HTTP Error 429: Too Many Requests` | https://en.wikipedia.org/w/index.php?pageid=2186423 |
| 40218034 | `route_generation` | `wikipedia_infobox_generation_error:HTTPError:HTTP Error 429: Too Many Requests` | https://en.wikipedia.org/w/index.php?pageid=40218034 |
| 662351 | `route_generation` | `wikipedia_infobox_generation_error:HTTPError:HTTP Error 429: Too Many Requests` | https://en.wikipedia.org/w/index.php?pageid=662351 |
| 45576 | `route_generation` | `wikipedia_infobox_generation_error:HTTPError:HTTP Error 429: Too Many Requests` | https://en.wikipedia.org/w/index.php?pageid=45576 |
| 79915 | `route_generation` | `wikipedia_infobox_generation_error:HTTPError:HTTP Error 429: Too Many Requests` | https://en.wikipedia.org/w/index.php?pageid=79915 |
| 144968 | `route_generation` | `wikipedia_infobox_generation_error:HTTPError:HTTP Error 429: Too Many Requests` | https://en.wikipedia.org/w/index.php?pageid=144968 |
| 143759 | `route_generation` | `wikipedia_infobox_generation_error:HTTPError:HTTP Error 429: Too Many Requests` | https://en.wikipedia.org/w/index.php?pageid=143759 |
| 8080 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=6` | List of decades, centuries, and millennia |
| 36762240 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the superorder classification of shrimp according to their scientific classification? |
| 500409 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=feet,metres` | A Coruña |
| 7549995 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:image_cell_rate=0.4821` | Elk |
| 43088 | `route_generation` | `wikipedia_infobox_answer_type_not_allowed:answer_type_not_allowed:Other; allowed=Other` | In which year did Yogi Berra's team finish 1st in the American League during the regular season and lose the World Series to the St. Louis Cardinals? |
| 599 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:table` | In the Afroasiatic numeral systems table, which language branch uses the term 'gáal' for the masculine form of the numeral one? |
| 151451 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What role did Busta Rhymes play in the 2000 film Shaft? |
| 26457880 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=tonnes` | Air India |
| 156745 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which award did the film Pretty Woman win for its film music? |
| 31730 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=16` | British Armed Forces |
| 18947898 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the country of origin of the Amnesty International Secretary General who served from 1992 to 2001? |
| 47864412 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which diacritic is combined with the letter ब to form the Nepali syllable 'बु'? |
| 85099 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which company was the kit manufacturer for Watford F.C. during the 1993 to 1995 period? |
| 276773 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=13` | SAP |
| 70581 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,ft,m` | St. John's, Newfoundland and Labrador |
| 10134 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | How many distinct regions of the electromagnetic spectrum are listed in the table describing their main interactions with matter? |
| 5659 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | Chemical element |
| 275515 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:alpha_character_rate=0.2278` | Mont-Saint-Michel |
| 5215 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Casino |
| 30498 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | How many editions of the Tour de France had been held as of 2025? |
| 13677 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:image_cell_rate=0.2857` | Hindus |
| 15868164 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | In how many Indian Premier League seasons did Mumbai Indians finish 1st in the league standing between 2008 and 2026? |
| 359520 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In how many different years did Joan Jett appear in films or television shows according to her filmography? |
| 99627 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:incumbent` | Mannheim |
| 4446 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ha` | Booker Prize |
| 149349 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=16` | Dortmund |
| 904826 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many distinct alignments are shown in the alignment grid of Dungeons & Dragons? |
| 26873 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many seconds are there in one day according to the definition based on the division of the day? |
| 36991518 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | How many deputy prime ministers are listed for the Jazira Region in the Democratic Autonomous Administration of North and East Syria? |
| 601399 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=45` | Display resolution |
| 158595 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:table` | How many times was Rupert Grint nominated for an award in the year 2011 according to the awards and nominations table? |
| 232863 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:table` | How many times did The Fairly OddParents win the BMI Cable Award according to the awards and nominations table? |
| 250858 | `route_generation` | `wikipedia_infobox_generation_error:HTTPError:HTTP Error 429: Too Many Requests` | https://en.wikipedia.org/w/index.php?pageid=250858 |
| 481708 | `route_generation` | `wikipedia_infobox_generation_error:HTTPError:HTTP Error 429: Too Many Requests` | https://en.wikipedia.org/w/index.php?pageid=481708 |
| 43710 | `route_generation` | `wikipedia_infobox_generation_error:HTTPError:HTTP Error 429: Too Many Requests` | https://en.wikipedia.org/w/index.php?pageid=43710 |
| 17740 | `route_generation` | `wikipedia_infobox_generation_error:HTTPError:HTTP Error 429: Too Many Requests` | https://en.wikipedia.org/w/index.php?pageid=17740 |
| 38264 | `route_generation` | `wikipedia_infobox_generation_error:HTTPError:HTTP Error 429: Too Many Requests` | https://en.wikipedia.org/w/index.php?pageid=38264 |
| 20646803 | `route_generation` | `wikipedia_infobox_generation_error:HTTPError:HTTP Error 429: Too Many Requests` | https://en.wikipedia.org/w/index.php?pageid=20646803 |
| 20556859 | `route_generation` | `wikipedia_infobox_generation_error:HTTPError:HTTP Error 429: Too Many Requests` | https://en.wikipedia.org/w/index.php?pageid=20556859 |
| 191280 | `route_generation` | `wikipedia_infobox_generation_error:HTTPError:HTTP Error 429: Too Many Requests` | https://en.wikipedia.org/w/index.php?pageid=191280 |
| 276433 | `route_generation` | `wikipedia_infobox_generation_error:HTTPError:HTTP Error 429: Too Many Requests` | https://en.wikipedia.org/w/index.php?pageid=276433 |
| 218746 | `route_generation` | `wikipedia_infobox_generation_error:HTTPError:HTTP Error 429: Too Many Requests` | https://en.wikipedia.org/w/index.php?pageid=218746 |
| 57877 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ml,g,m` | Sodium hydroxide |
| 407239 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | The Indian Express |
| 32005912 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Grimes |
| 76988 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the maximum duration in milliseconds of the PR interval as measured on a standard ECG graph paper? |
| 1064 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | How many clades are listed in the scientific classification of the almond in the infobox? |
| 35412202 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:image_cell_rate=0.6667` | Wikidata |
| 80482 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many years did Ruud Lubbers serve as Prime Minister of the Netherlands during Beatrix's reign? |
| 15049 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many years did Peyton Manning play for the Indianapolis Colts? |
| 4595356 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:image_cell_rate=0.4904` | 1910 United States census |
| 30403 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:example` | In the example state table for the 3-state 2-symbol busy beaver reduced to 5-tuples, what is the final state when the current state is C and the scanned symbol is 1? |
| 27856145 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:image_cell_rate=0.4688` | Siena |
| 485429 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | In the context of martial morality in Chinese martial arts, what is the Pinyin romanization for the concept of 'Respect'? |
| 195468 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:caption:active` | Ring of Fire |
| 211917 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:table` | In the National Program Rankings table, what is the ranking of the Physics program at the University of California, Santa Barbara? |
| 420162 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what exact date was the Rai 3 television channel launched? |
| 30418 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did the premiere of The Marriage of Figaro take place at the Burgtheater in Vienna? |
| 12628 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what version of GIMP was the XCF file size extended to more than 4 GB? |
| 34556 | `rewrite_surface` | `rewrite_guard_rejected:forbidden_temporal_phrase` | On what exact date was Rajiv Gandhi, former prime minister of India, assassinated? |
| 46735704 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was Kehlani nominated for the Grammy Award for Best Urban Contemporary Album for their album You Should Be Here? |
| 87851 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=1` | Stoat |
| 521984 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Emily Watson play the role of Jacqueline du Pré in the film Hilary and Jackie? |
| 2369 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Aston Martin DBR4 Formula One racecar introduced? |
| 63376140 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the first episode of the first season of Arcane originally released? |
| 19342760 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:incomplete` | Seven Wonders of the Ancient World |
| 40880638 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what date was the host for UEFA Euro 2024 selected in Nyon, Switzerland? |
| 59385 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the binomial name Amanita muscaria (L.) Lam. officially established? |
| 339183 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | At what angle is the Chinese compass point labeled '乾 qián' positioned? |
| 439959 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was Herb Alpert's studio album 'Whipped Cream & Other Delights' released? |
| 733497 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=2` | Hydroxyzine |
| 188257 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Paul McCartney and Wings first include Laurence Juber as a guitarist and Steve Holley as a drummer in their line-up? |
| 39345917 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Big Hero 6 (film) |
| 53762 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did David Niven win the Academy Award for Best Actor? |
| 385155 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Guglielmo Marconi receive the Nobel Prize in Physics? |
| 2209490 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ha,g` | Romanization of Arabic |
| 422038 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,metres,millimetres,m` | Vigo |
| 23906 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=29` | Peterborough |
| 67923 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | East Sussex |
| 1161220 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Khushbu Sundar |
| 47498 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | All your base are belong to us |
| 113933 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Iowa City, Iowa |
| 22461 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Osteoporosis |
| 129619 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the film Ghost win the Academy Award for Best Supporting Actress? |
| 540317 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what model year did the Ford Explorer first begin production? |


