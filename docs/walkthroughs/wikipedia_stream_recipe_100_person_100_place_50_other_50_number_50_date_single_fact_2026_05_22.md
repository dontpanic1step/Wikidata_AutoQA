# Route 3 Streaming Wikipedia Page-ID Walkthrough - 2026-05-22

## Stats

- Run group ID: `wikipedia_stream_recipe_100_person_100_place_50_other_50_number_50_date_single_fact_2026_05_22`
- Run segment ID: `recipe_combined`
- Artifact manifest: ``
- Mode: `page_id_stream_recipe`
- Page source: `table-search`
- Table-search queries: `insource:"wikitable"`
- Attempted page IDs: 355
- Unique attempted page IDs: 120
- Stream state reset at run start: yes
- Auto rerun pool once: yes
- Auto-rerun attempted page IDs: 0
- Accepted QAs: 30
- Rejected QAs/pages: 315
- Transient rerun attempts during run: 10
- Wall-clock runtime: 1410.1563s
- DuckDuckGo top K: 5
- Generated search queries per QA: 3
- DuckDuckGo parallel queries: 3
- Route 3 reasoning_type constraint: `single_fact`
- Route 3 answer_type constraint: `Person, Place, Other, Number, Date`
- Route 3 table filter modes: `no_incomplete_tables, not_number_dominant, no_social_science_research`
- Page-id bounds: None to None
- Stream state: `separate_segment_stream_states`
- Accepted output: `D:\Study\AI\My-research\Wikidata_Framework\outputs\wikipedia_stream_recipe_100_person_100_place_50_other_50_number_50_date_single_fact_2026_05_22_accepted.jsonl`
- Rejected output: `D:\Study\AI\My-research\Wikidata_Framework\outputs\wikipedia_stream_recipe_100_person_100_place_50_other_50_number_50_date_single_fact_2026_05_22_rejected.jsonl`
- Domain policy: `domain_and_subdomain_optional_for_page_id_streaming`
- Rerun pool after run: `47498, 57905, 83316, 194910, 47864412`

### Recipe Segments

| Configured answer_type | Record limit | Attempted page IDs | Accepted | Rejected | Rerun |
| --- | ---: | ---: | ---: | ---: | ---: |
| Person | 100 | 100 | 7 | 93 | 0 |
| Place | 100 | 102 | 10 | 88 | 4 |
| Other | 50 | 52 | 4 | 44 | 4 |
| Number | 50 | 50 | 5 | 45 | 0 |
| Date | 50 | 51 | 4 | 45 | 2 |

### Survival By Layer

| Layer | Entered | Failed | Survived | Layer survival | Cumulative survival |
| --- | ---: | ---: | ---: | ---: | ---: |
| Page-id reservation | 355 | 0 | 355 | 100.0% | 100.0% |
| Unresolved or returned to rerun pool | 355 | 0 | 355 | 100.0% | 100.0% |
| Page extraction, table grading, and QA generation | 355 | 155 | 200 | 56.3% | 56.3% |
| Rewrite and surface validation | 200 | 36 | 164 | 82.0% | 46.2% |
| DuckDuckGo long-tail filtering | 164 | 11 | 153 | 93.3% | 43.1% |
| Second-stage model grading | 153 | 102 | 51 | 33.3% | 14.4% |
| Shared route-aware validation | 51 | 11 | 40 | 78.4% | 11.3% |
| Deduplication | 40 | 0 | 40 | 100.0% | 11.3% |
| Other rejection | 40 | 0 | 40 | 100.0% | 11.3% |

### Failure Reasons

| Stage | Reason | Count |
| --- | --- | ---: |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant` | 116 |
| `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded` | 102 |
| `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | 14 |
| `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | 12 |
| `search_longtail` | `search_longtail_verifier_rejected` | 11 |
| `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | 11 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | 6 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables` | 5 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:active` | 4 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | 4 |
| `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | 3 |
| `rewrite_surface` | `rewrite_guard_rejected:forbidden_temporal_phrase` | 3 |
| `rewrite_surface` | `rewrite_guard_rejected:not_simple_question` | 3 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:present` | 3 |
| `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:example` | 1 |
| `route_generation` | `wikipedia_infobox_answer_type_not_allowed:answer_type_not_allowed:Number; allowed=Number` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No Person answer type data available in the top three tables to generate a valid question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No date or year information is present in the top-ranked tables to form a valid Date-type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No numeric data available in the top-ranked table to form a valid single numeric answer question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No person name is provided in the table for any club's foundation; thus, no single-fact question with a Person answer type can be generated.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No person name is provided in the table for any language broadcast start; thus no safe single person answer can be derived.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No person names are present in the top-ranked table to form a valid single_fact question with a Person answer type.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No person names are present in the top-ranked table to form a valid single_fact question with a Person answer.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No person names are provided in the twin cities table to support a single_fact question with a Person answer.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No person-related data in the top-ranked tables to form a valid single_fact question with a Person answer.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No person-type answer available in the top three tables; tables contain only phonetic symbols, no persons.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No suitable factual place-based data available in the top-ranked table to generate a single-answer question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No suitable person-related factual data in the top-ranked table to generate a single-fact question with a person answer.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No suitable place-type factual data available in the top-ranked table to form a single-answer question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any person names, so no single person answer can be derived.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any person names; it only lists program types and their ranks, so no valid Person answer can be derived.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any place or location information for osmium compounds, so no valid single_fact Place question can be generated.` | 1 |

### Answer Type Stats

| Scope | Answer type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `Date` | 4 | 26 | 30 | 13.3% |
| Current Run Records | `Number` | 5 | 23 | 28 | 17.9% |
| Current Run Records | `Other` | 4 | 19 | 23 | 17.4% |
| Current Run Records | `Person` | 7 | 41 | 48 | 14.6% |
| Current Run Records | `Place` | 10 | 51 | 61 | 16.4% |
| Current Run Records | `unknown` | 0 | 155 | 155 | 0.0% |

### Reasoning Type Stats

| Scope | Reasoning type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `single_fact` | 30 | 315 | 345 | 8.7% |

### Rerun Pool After Run

| Page ID | Exact reason |
| ---: | --- |
| 47498 | `search_longtail_verifier_error` |
| 57905 | `search_longtail_verifier_error` |
| 83316 | `search_longtail_verifier_error` |
| 194910 | `search_longtail_verifier_error` |
| 47864412 | `search_longtail_verifier_error` |


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
| `candidate_processing_seconds` | 345 | 2372.0500 | 6.8755 | 30.9821 |
| `duckduckgo_search_seconds` | 154 | 925.9154 | 6.0124 | 18.6689 |
| `first_paragraph_extract_seconds` | 207 | 41.1230 | 0.1987 | 1.0173 |
| `llm_question_generation_seconds` | 207 | 978.4094 | 4.7266 | 15.8871 |
| `number_reference_margin_seconds` | 154 | 0.0009 | 0.0000 | 0.0002 |
| `page_fetch_seconds` | 345 | 32.3785 | 0.0939 | 0.7896 |
| `rewrite_seconds` | 190 | 0.0000 | 0.0000 | 0.0000 |
| `second_stage_grading_seconds` | 143 | 1445.8579 | 10.1109 | 24.4466 |
| `table_parse_seconds` | 345 | 205.0016 | 0.5942 | 3.0762 |
| `total_generation_seconds` | 345 | 1311.7057 | 3.8020 | 16.5450 |
| `total_processing_seconds` | 345 | 2372.0500 | 6.8755 | 30.9821 |

## Accepted Candidates

| Page ID | Question | Answer | Source |
| ---: | --- | --- | --- |
| 19653842 | Who are the authors of the view that organisms are cooperating entities at differing levels of biological organisation? | Queller and Strassmann | https://en.wikipedia.org/wiki/Organism |
| 2924002 | Who most recently won the British Dance Act award at the BRIT Awards before its hiatus ended in 2021? | Charli XCX | https://en.wikipedia.org/wiki/Electronic_dance_music |
| 96875 | Who granted royal assent to the Great Western Railway Act in 1835? | Parliament of the United Kingdom | https://en.wikipedia.org/wiki/Great_Western_Railway |
| 599 | Who is the author referenced for the data on the "prefix conjugation" in Afroasiatic languages? | Gragg | https://en.wikipedia.org/wiki/Afroasiatic_languages |
| 15049 | Who was inducted into the Indianapolis Colts Ring of Honor in 2011? | Marvin Harrison | https://en.wikipedia.org/wiki/Indianapolis_Colts |
| 1064 | Who is credited with the binomial name of the almond species Prunus amygdalus? | Batsch | https://en.wikipedia.org/wiki/Almond |
| 18938412 | Who was nominated for the Top New Artist award in 1987 according to the Awards and nominations table? | Richard Marx | https://en.wikipedia.org/wiki/Richard_Marx |
| 60382764 | Which place is associated with the era spanning from 645 to 650 known as Taika? | Nara | https://en.wikipedia.org/wiki/Reiwa_era |
| 235916 | In which location was the Interactive Achievement Award won by Jada Pinkett Smith for Outstanding Achievement in Character Performance – Female for the work Enter the Matrix awarded? | United States | https://en.wikipedia.org/wiki/Jada_Pinkett_Smith |
| 569459 | In which geographic region is the white-tailed deer subspecies found according to the range map of subspecies? | North America | https://en.wikipedia.org/wiki/White-tailed_deer |
| 76988 | From which anatomical area of the heart do the inferior ECG leads record electrical activity? | inferior surface | https://en.wikipedia.org/wiki/Electrocardiography |
| 18938412 | In which city was the film 'Stories to Tell' featuring Richard Marx as himself filmed? | London | https://en.wikipedia.org/wiki/Richard_Marx |
| 38657800 | Which operating system family does the Pixel Launcher use? | Unix-like | https://en.wikipedia.org/wiki/Google_Pixel |
| 104944 | In which place did Charles XII of Sweden die? | Fredrikshald, Denmark–Norway | https://en.wikipedia.org/wiki/Charles_XII_of_Sweden |
| 42042635 | At which award ceremony did Ekta Kapoor win the Best Upcoming Drama Series award in 2015? | Star Guild Awards | https://en.wikipedia.org/wiki/Kumkum_Bhagya |
| 438269 | In which place was the DVD art for the Complete Second Season of Batman Beyond designed? | RDI | https://en.wikipedia.org/wiki/Batman_Beyond |
| 241559 | In which country was the Red Velvet limited edition Oreo flavor also available besides the United States? | Indonesia | https://en.wikipedia.org/wiki/Oreo |
| 57905 | Which time zone abbreviation is used for the districts of Abyysky, Allaikhovsky, Momsky, Nizhnekolymsky, Srednekolymsky, and Verkhnekolymsky in the Sakha Republic? | MAGT | https://en.wikipedia.org/wiki/Sakha_Republic |
| 214179 | Which instrument did Max Brody play in the band Ministry? | saxophone | https://en.wikipedia.org/wiki/Ministry_(band) |
| 18938412 | Which song by Richard Marx won the Most Performed Songs award in 1990? | Satisfied | https://en.wikipedia.org/wiki/Richard_Marx |
| 38657800 | What is the operating system family used by the Pixel Launcher? | Unix-like | https://en.wikipedia.org/wiki/Google_Pixel |
| 151451 | How many documentaries featuring Busta Rhymes were released in the year 2006? | 5 | https://en.wikipedia.org/wiki/Busta_Rhymes |
| 156745 | How many awards did Julia Roberts win for her roles related to Pretty Woman according to the accolades table? | 4 | https://en.wikipedia.org/wiki/Pretty_Woman |
| 57659 | How many football championships has Espérance Sportive de Tunis won? | 20 | https://en.wikipedia.org/wiki/Tunis |
| 214179 | How many years was Mike Scaccia active as a member of Ministry in total? | 18 | https://en.wikipedia.org/wiki/Ministry_(band) |
| 540317 | How many selectable terrain modes are included in the Ford Explorer's Terrain Management System? | 4 | https://en.wikipedia.org/wiki/Ford_Explorer |
| 1064 | In what year was the binomial name Prunus amygdalus for the almond officially published? | 1801 | https://en.wikipedia.org/wiki/Almond |
| 18938412 | In what year did Richard Marx receive a nomination for the Top New Artist award? | 1987 | https://en.wikipedia.org/wiki/Richard_Marx |
| 441357 | In the Somali language numbers table, what is the Somali Latin term for the number thirteen? | saddex iyo toban | https://en.wikipedia.org/wiki/Somali_language |
| 1787105 | In what year were the four basic animal mating systems categorized in sociobiology and behavioural ecology? | 160–161 | https://en.wikipedia.org/wiki/Animal_sexual_behaviour |

## Second-Stage Filtering Responses

These are the small-model QA responses used by the second-stage filter: `openai/gpt-4.1-mini` and `google/gemini-3-flash-preview`.

| Page ID | Question | Reference answer | openai/gpt-4.1-mini | google/gemini-3-flash-preview |
| ---: | --- | --- | --- | --- |
| 19653842 | Who are the authors of the view that organisms are cooperating entities at differing levels of biological organisation? | Queller and Strassmann | INCORRECT; predicted_answer: The view that organisms are cooperating entities at differing levels of biological organization is prominently associated with authors like David Sloan Wilson and Elliott Sober. They have extensively discussed multilevel selection and cooperation in evolution. Additionally, Peter Godfrey-Smith and Samir Okasha have contributed to this perspective in philosophy of biology. | INCORRECT; predicted_answer: The primary authors associated with the view of organisms as nested levels of cooperation (often termed **Multilevel Selection Theory** or **Major Evolutionary Transitions**) include:  *   **John Maynard Smith and Eörs Szathmáry:** Authors of *The Major Transitions in Evolution* (1995), which details how independent replicators combined to form higher-level cooperative units (e.g., genes into chromosomes, cells into multicellular organisms). *   **Leo Buss:** Author of *The Evolution of Individuality* (1987), focusing on the transition from single cells to multicellular individuals. |
| 2924002 | Who most recently won the British Dance Act award at the BRIT Awards before its hiatus ended in 2021? | Charli XCX | INCORRECT; predicted_answer: The most recent winner of the British Dance Act award at the BRIT Awards before its hiatus ended in 2021 was Rudimental in 2019. | INCORRECT; predicted_answer: **Jamiroquai** won the award in 2004, the final year it was presented before its 18-year hiatus. |
| 96875 | Who granted royal assent to the Great Western Railway Act in 1835? | Parliament of the United Kingdom | INCORRECT; predicted_answer: The Great Western Railway Act of 1835 received royal assent from King William IV. | INCORRECT; predicted_answer: **King William IV** granted royal assent to the Great Western Railway Act on August 31, 1835. |
| 599 | Who is the author referenced for the data on the "prefix conjugation" in Afroasiatic languages? | Gragg | INCORRECT; predicted_answer: The author referenced for the data on the "prefix conjugation" in Afroasiatic languages is Hetzron. | INCORRECT; predicted_answer: The author most commonly referenced for data and reconstruction of the "prefix conjugation" in Afroasiatic languages is **Otto Rössler**. His work, particularly his 1950 study *Verbum und Nomen im Semitischen und Hamitischen*, established the prefix conjugation as a shared ancestral feature of the phylum. |
| 15049 | Who was inducted into the Indianapolis Colts Ring of Honor in 2011? | Marvin Harrison | INCORRECT; predicted_answer: In 2011, Peyton Manning was inducted into the Indianapolis Colts Ring of Honor. | INCORRECT; predicted_answer: **Marshall Faulk** was inducted into the Indianapolis Colts Ring of Honor in 2011. |
| 1064 | Who is credited with the binomial name of the almond species Prunus amygdalus? | Batsch | INCORRECT; predicted_answer: The binomial name Prunus amygdalus is credited to Carl Linnaeus. | INCORRECT; predicted_answer: **Philipp Conrad Fabricius** is credited with the binomial name *Prunus amygdalus*. |
| 18938412 | Who was nominated for the Top New Artist award in 1987 according to the Awards and nominations table? | Richard Marx | INCORRECT; predicted_answer: According to the Awards and nominations table, the nominees for the Top New Artist award in 1987 were:  - Tiffany   - Glass Tiger   - Nu Shooz   - Bruce Hornsby & the Range   - Billy Vera & the Beaters | INCORRECT; predicted_answer: According to the Awards and nominations table for 1987, the nominees for **Top New Artist** were:  *   **The Judds** (Winner) *   **Restless Heart** *   **Holly Dunn** *   **Dwight Yoakam** *   **T. Graham Brown** |
| 60382764 | Which place is associated with the era spanning from 645 to 650 known as Taika? | Nara | INCORRECT; predicted_answer: The era spanning from 645 to 650 known as Taika is associated with Japan. | INCORRECT; predicted_answer: The Taika era is primarily associated with **Naniwa-no-nagara-no-toyosaki-no-miya** (the Naniwa Palace) in modern-day **Osaka**, Japan, which served as the capital during the Taika Reforms. |
| 235916 | In which location was the Interactive Achievement Award won by Jada Pinkett Smith for Outstanding Achievement in Character Performance – Female for the work Enter the Matrix awarded? | United States | INCORRECT; predicted_answer: The Interactive Achievement Award won by Jada Pinkett Smith for Outstanding Achievement in Character Performance – Female for Enter the Matrix was awarded in Las Vegas, Nevada. | INCORRECT; predicted_answer: The award was presented at the **Palms Casino Resort** in **Las Vegas, Nevada**. |
| 569459 | In which geographic region is the white-tailed deer subspecies found according to the range map of subspecies? | North America | INCORRECT; predicted_answer: The white-tailed deer subspecies is found primarily in the eastern and central regions of North America according to the range map of subspecies. | INCORRECT; predicted_answer: White-tailed deer (*Odocoileus virginianus*) are found across a vast geographic region that spans from **southern Canada**, throughout most of the **continental United States**, and down through **Mexico and Central America** into **northern South America** (as far south as Peru and Brazil). |
| 76988 | From which anatomical area of the heart do the inferior ECG leads record electrical activity? | inferior surface | INCORRECT; predicted_answer: The inferior ECG leads (leads II, III, and aVF) record electrical activity from the inferior wall of the heart, primarily supplied by the right coronary artery. | INCORRECT; predicted_answer: The inferior ECG leads (II, III, and aVF) record electrical activity from the **inferior wall of the left ventricle**. |
| 18938412 | In which city was the film 'Stories to Tell' featuring Richard Marx as himself filmed? | London | INCORRECT; predicted_answer: The film "Stories to Tell" featuring Richard Marx as himself was filmed in Chicago. | INCORRECT; predicted_answer: The film *Stories to Tell* (2021) was filmed in **Los Angeles**, California. |
| 38657800 | Which operating system family does the Pixel Launcher use? | Unix-like | INCORRECT; predicted_answer: The Pixel Launcher uses the Android operating system family. | INCORRECT; predicted_answer: The Pixel Launcher uses the **Android** operating system family. |
| 104944 | In which place did Charles XII of Sweden die? | Fredrikshald, Denmark–Norway | INCORRECT; predicted_answer: Charles XII of Sweden died in Fredrikshald, Norway. | INCORRECT; predicted_answer: Charles XII of Sweden died at the fortress of **Fredriksten** in **Halden**, Norway. |
| 42042635 | At which award ceremony did Ekta Kapoor win the Best Upcoming Drama Series award in 2015? | Star Guild Awards | INCORRECT; predicted_answer: Ekta Kapoor won the Best Upcoming Drama Series award in 2015 at the Indian Television Academy Awards. | INCORRECT; predicted_answer: Ekta Kapoor won the Best Upcoming Drama Series award for *Itna Karo Na Mujhe Pyaar* at the **14th Indian Telly Awards** in 2015. |
| 438269 | In which place was the DVD art for the Complete Second Season of Batman Beyond designed? | RDI | INCORRECT; predicted_answer: The DVD art for the Complete Second Season of Batman Beyond was designed at Warner Bros. Animation. | INCORRECT; predicted_answer: The DVD art for *Batman Beyond: The Complete Second Season* was designed in **Burbank, California**, by the Warner Bros. Home Entertainment creative team. |
| 241559 | In which country was the Red Velvet limited edition Oreo flavor also available besides the United States? | Indonesia | INCORRECT; predicted_answer: The Red Velvet limited edition Oreo flavor was also available in Canada besides the United States. | INCORRECT; predicted_answer: The Red Velvet limited edition Oreo flavor was also available in **China**. |
| 57905 | Which time zone abbreviation is used for the districts of Abyysky, Allaikhovsky, Momsky, Nizhnekolymsky, Srednekolymsky, and Verkhnekolymsky in the Sakha Republic? | MAGT | INCORRECT; predicted_answer: The districts of Abyysky, Allaikhovsky, Momsky, Nizhnekolymsky, Srednekolymsky, and Verkhnekolymsky in the Sakha Republic use the time zone abbreviation **VLAT** (Vladivostok Time), which is UTC+10. | INCORRECT; predicted_answer: The time zone abbreviation used for these districts is **SRET** (Srednekolymsk Time). |
| 214179 | Which instrument did Max Brody play in the band Ministry? | saxophone | INCORRECT; predicted_answer: Max Brody played drums in the band Ministry. | INCORRECT; predicted_answer: Max Brody played **drums** and **saxophone** in Ministry. |
| 18938412 | Which song by Richard Marx won the Most Performed Songs award in 1990? | Satisfied | INCORRECT; predicted_answer: The song by Richard Marx that won the Most Performed Songs award in 1990 is "Right Here Waiting." | INCORRECT; predicted_answer: Richard Marx won the BMI Most Performed Songs award in 1990 for **"Right Here Waiting."** |
| 38657800 | What is the operating system family used by the Pixel Launcher? | Unix-like | INCORRECT; predicted_answer: The Pixel Launcher is used on the Android operating system family. | INCORRECT; predicted_answer: The Pixel Launcher uses the **Android** operating system family. |
| 151451 | How many documentaries featuring Busta Rhymes were released in the year 2006? | 5 (acceptable range: anything between 4 and 6) | INCORRECT; predicted_answer: In 2006, there was 1 documentary featuring Busta Rhymes released. | INCORRECT; predicted_answer: There were **two** documentaries featuring Busta Rhymes released in 2006:  1.  **Dave Chappelle's Block Party** 2.  **The Hip Hop Project** |
| 156745 | How many awards did Julia Roberts win for her roles related to Pretty Woman according to the accolades table? | 4 (acceptable range: anything between 3 and 5) | INCORRECT; predicted_answer: Julia Roberts won 3 awards for her role related to Pretty Woman according to the accolades table. | INCORRECT; predicted_answer: According to the accolades table, Julia Roberts won **3** awards for her role in *Pretty Woman*:  1.  **Golden Globe Award** for Best Actress – Motion Picture Musical or Comedy 2.  **Kids' Choice Award** for Favorite Movie Actress 3.  **ShoWest Award** for Female Star of the Year |
| 57659 | How many football championships has Espérance Sportive de Tunis won? | 20 (acceptable range: anything between 19 and 21) | INCORRECT; predicted_answer: Espérance Sportive de Tunis has won 32 Tunisian Ligue Professionnelle 1 championships. | INCORRECT; predicted_answer: Espérance Sportive de Tunis has won **33** Tunisian Ligue Professionnelle 1 titles. |
| 214179 | How many years was Mike Scaccia active as a member of Ministry in total? | 18 (acceptable range: anything between 17 and 19) | INCORRECT; predicted_answer: Mike Scaccia was active as a member of Ministry during two periods: from 1989 to 1996 and from 2003 until his death in 2012.   - First period: 1989 to 1996 → 7 years   - Second period: 2003 to 2012 → 9 years    In total, he was active in Ministry for 16 years. | INCORRECT; predicted_answer: Mike Scaccia was a member of Ministry for a total of **11 years** (1989–1995, 2003–2006, and 2011–2012). |
| 540317 | How many selectable terrain modes are included in the Ford Explorer's Terrain Management System? | 4 (acceptable range: anything between 3 and 5) | INCORRECT; predicted_answer: The Ford Explorer's Terrain Management System includes six selectable terrain modes. | INCORRECT; predicted_answer: The Ford Explorer’s Terrain Management System includes **seven** selectable drive modes. |
| 1064 | In what year was the binomial name Prunus amygdalus for the almond officially published? | 1801 | INCORRECT; predicted_answer: The binomial name Prunus amygdalus for the almond was officially published in 1753. | INCORRECT; predicted_answer: The binomial name *Prunus amygdalus* was officially published in **1768** by the botanist Philip Miller in the eighth edition of *The Gardeners Dictionary*. |
| 18938412 | In what year did Richard Marx receive a nomination for the Top New Artist award? | 1987 | INCORRECT; predicted_answer: Richard Marx received a nomination for the Top New Artist award in 1988. | INCORRECT; predicted_answer: Richard Marx was nominated for the **Billboard Music Award** for Top New Artist in **1988**. |
| 441357 | In the Somali language numbers table, what is the Somali Latin term for the number thirteen? | saddex iyo toban | INCORRECT; predicted_answer: The Somali Latin term for the number thirteen is "toban iyo saddex." | INCORRECT; predicted_answer: The Somali Latin term for the number thirteen is **toban iyo saddex**. |
| 1787105 | In what year were the four basic animal mating systems categorized in sociobiology and behavioural ecology? | 160–161 | INCORRECT; predicted_answer: The four basic animal mating systems were categorized in sociobiology and behavioral ecology in 1976. | INCORRECT; predicted_answer: The four basic animal mating systems (monogamy, polygyny, polyandry, and promiscuity) were categorized in **1977** by Stephen T. Emlen and Lewis W. Oring in their landmark paper, "Ecology, Sexual Selection, and the Evolution of Mating Systems." |
| 22093 | National Basketball Association |  | not run | not run |
| 17416221 | South Africa |  | not run | not run |
| 9316 | England |  | not run | not run |
| 32611 | Vietnam War |  | not run | not run |
| 5489 | Chile |  | not run | not run |
| 13277 | Holy Roman Empire |  | not run | not run |
| 11857 | George Lucas |  | not run | not run |
| 19261 | Monaco |  | not run | not run |
| 14849 | Who is the person associated with the slogan "Land of Lincoln" for the state of Illinois? | Abraham Lincoln | not run | not run |
| 738 | Who was the President of Albania according to the Politics table? | Bajram Begaj | NOT_ATTEMPTED; predicted_answer: I don’t see a Politics table in the current context. Could you please provide the table or more details? | CORRECT; predicted_answer: Since you haven't provided the specific table, I cannot give you the name listed in your document. However, the current President of Albania is **Bajram Begaj**. |
| 31740 | Which school at the University of Michigan was ranked number 1 in the U.S. News Best Schools for Social Work in 2024? | School of Social Work | not run | not run |
| 292259 | Deutsche Welle |  | not run | not run |
| 21355232 | Which person is credited with founding the National Park Service in the United States? | Stephen Mather | CORRECT; predicted_answer: Stephen Mather is credited with founding the National Park Service in the United States. | not run |
| 39776 | Denial-of-service attack |  | not run | not run |
| 40010153 | Goa |  | not run | not run |
| 5488 | Chad |  | not run | not run |
| 199445 | Who scored 8 goals for England in international matches in the year 2014? | Wayne Rooney | CORRECT; predicted_answer: Wayne Rooney scored 8 goals for England in international matches in the year 2014. | not run |
| 1640 | Who succeeded Æthelred as king around the year 871 according to the chronology of Alfred the Great? | Alfred | not run | not run |
| 8083 | Who won the Grammy Award for Best Rap Solo Performance in 1994 for the song "Let Me Ride"? | Dr. Dre | CORRECT; predicted_answer: Dr. Dre won the Grammy Award for Best Rap Solo Performance in 1994 for the song "Let Me Ride." | not run |
| 151603 | Who played the role of Gurd Canliss in the 1964 episode "Canliss" of the television program Rawhide? | Dean Martin | INCORRECT; predicted_answer: The role of Gurd Canliss in the 1964 episode "Canliss" of the television program Rawhide was played by actor John Carradine. | CORRECT; predicted_answer: **Dean Martin** played the role of Gurd Canliss. |
| 45367389 | Greater London |  | not run | not run |
| 41853326 | Who was the head coach of Inter Miami CF as of April 14, 2026? | Guillermo Hoyos | not run | not run |
| 105908 | Ford Mustang |  | not run | not run |
| 60382764 | Who was the emperor of Japan during the Taika era from 645 to 650? | Emperor Kōtoku | not run | not run |
| 12186 | Guinea-Bissau |  | not run | not run |
| 66958 | Who is the person associated with the official currency of the People's Republic of China? | People's Bank of China | not run | not run |
| 5643 | Channel Islands |  | not run | not run |
| 34411 | Who is the brightest star in the constellation that the Sun stays in from 10 August to 15 September according to the 1977 IAU boundaries? | Regulus | CORRECT; predicted_answer: From 10 August to 15 September, the Sun is in the constellation Leo according to the 1977 IAU boundaries. The brightest star in Leo is Regulus. | not run |
| 217231 | Which person provided commentary on the pilot episode in the DVD release of Curb Your Enthusiasm Season 1? | Larry David | CORRECT; predicted_answer: Larry David provided commentary on the pilot episode in the DVD release of Curb Your Enthusiasm Season 1. | not run |
| 55440889 | Pixel 2 |  | not run | not run |
| 235916 | Who won the Interactive Achievement Award for Outstanding Achievement in Character Performance – Female for the work Enter the Matrix in 2004? | Jada Pinkett Smith | not run | not run |
| 30292 | Who is the descendant of kings restored to his ancestral throne in The Lord of the Rings according to Randel Helms's analysis of quest structure? | Aragorn | not run | not run |
| 33094374 | Telecommunications |  | not run | not run |
| 22948 | Who is the mother of the offspring named Arion according to the earliest source Apollodorus? | Demeter | CORRECT; predicted_answer: According to the earliest source Apollodorus, the mother of Arion is the goddess Demeter. | not run |
| 84952 | Who succeeded Marvelous Marvin Hagler as the WBC middleweight champion after his reign ended on April 6, 1987? | Sugar Ray Leonard | CORRECT; predicted_answer: After Marvelous Marvin Hagler's reign ended on April 6, 1987, Sugar Ray Leonard succeeded him as the WBC middleweight champion. | not run |
| 91195 | Who holds the record for the most singles titles in the Open Era at the Wimbledon Gentlemen's Championships? | Roger Federer | CORRECT; predicted_answer: Roger Federer holds the record for the most singles titles in the Open Era at the Wimbledon Gentlemen's Championships, with 8 titles. | not run |
| 235959 | Who played the role of Holly 13 in the 1976 film Logan's Run? | Farrah Fawcett | INCORRECT; predicted_answer: Jenny Agutter played the role of Holly 13 in the 1976 film Logan's Run. | CORRECT; predicted_answer: **Farrah Fawcett** played the role of Holly 13 in the 1976 film *Logan's Run*. |
| 260996 | Who played the role of Clifford Glimmer in the 1999 stage production of Side Man at the John Golden Theatre? | Christian Slater | INCORRECT; predicted_answer: The role of Clifford Glimmer in the 1999 stage production of Side Man at the John Golden Theatre was played by Frank Wood. | INCORRECT; predicted_answer: **Kevin Geer** played the role of Clifford Glimmer in the 1999 stage production of *Side Man* at the John Golden Theatre. |
| 342334 | Autopsy |  | not run | not run |
| 105391 | B movie |  | not run | not run |
| 68761 | Publishing |  | not run | not run |
| 229275 | Lamb and mutton |  | not run | not run |
| 246920 | Visa Inc. |  | not run | not run |
| 2114995 | Dextromethorphan |  | not run | not run |
| 569459 | White-tailed deer |  | not run | not run |
| 1625048 | Kingdom of Bohemia |  | not run | not run |
| 17278765 | Who was the winning team in the 1931 Rose Bowl that served as the title game for the Albert Russel Erskine Trophy and the Dickinson System's Knute Rockne Memorial Trophy? | USC | not run | not run |
| 7549995 | Elk |  | not run | not run |
| 151451 | Who played the role of Rasaan in the 2000 film Shaft? | Busta Rhymes | not run | not run |
| 43088 | Who was the manager of the New York Mets during the 1973 season when the team lost the World Series to the Oakland Athletics? | Yogi Berra | not run | not run |
| 156745 | Who won the Golden Globe Award for Best Actress in a Motion Picture – Musical or Comedy for the film Pretty Woman? | Julia Roberts | CORRECT; predicted_answer: Julia Roberts won the Golden Globe Award for Best Actress in a Motion Picture – Musical or Comedy for the film Pretty Woman. | not run |
| 26457880 | Air India |  | not run | not run |
| 31730 | British Armed Forces |  | not run | not run |
| 57905 | Sakha Republic |  | not run | not run |
| 47864412 | Nepali language |  | not run | not run |
| 18947898 | Who served as the Secretary General of Amnesty International from 1992 to 2001? | Pierre Sané | CORRECT; predicted_answer: Pierre Sané served as the Secretary General of Amnesty International from 1992 to 2001. | not run |
| 57877 | Sodium hydroxide |  | not run | not run |
| 32005912 | Grimes |  | not run | not run |
| 407239 | The Indian Express |  | not run | not run |
| 57659 | Tunis |  | not run | not run |
| 80482 | Who was the Prime Minister of the Netherlands at the start of Queen Beatrix's reign in 1980? | Dries van Agt | CORRECT; predicted_answer: The Prime Minister of the Netherlands at the start of Queen Beatrix's reign in 1980 was Dries van Agt. | not run |
| 214179 | Which former member of Ministry played drums, backing vocals, keyboards, and guitar and was active from 1986 to 1994 before passing away in 2020? | William "Bill" Rieflin | CORRECT; predicted_answer: The former member of Ministry who played drums, backing vocals, keyboards, and guitar, was active from 1986 to 1994, and passed away in 2020 is Bill Rieflin. | not run |
| 76988 | Which method used in time-frequency analysis of ECG signal processing is suitable for fully non-stationary and nonlinear signals and provides instantaneous frequency distribution? | Hilbert–Huang transform | CORRECT; predicted_answer: The **Hilbert-Huang Transform (HHT)** is suitable for fully non-stationary and nonlinear ECG signals and provides an instantaneous frequency distribution. It involves Empirical Mode Decomposition (EMD) followed by the Hilbert Transform to extract instantaneous frequency components. | not run |
| 35412202 | Who is credited with centralizing the information of interlanguage links for Wikipedia articles prior to the introduction of Wikidata? | Wikidata | not run | not run |
| 2209490 | Romanization of Arabic |  | not run | not run |
| 422038 | Vigo |  | not run | not run |
| 23906 | Peterborough |  | not run | not run |
| 67923 | East Sussex |  | not run | not run |
| 1161220 | Khushbu Sundar |  | not run | not run |
| 113933 | Iowa City, Iowa |  | not run | not run |
| 22461 | Osteoporosis |  | not run | not run |
| 129619 | Who won the Academy Award for Best Supporting Actress for the film Ghost (1990)? | Whoopi Goldberg | CORRECT; predicted_answer: Whoopi Goldberg won the Academy Award for Best Supporting Actress for the film *Ghost* (1990). | not run |
| 47498 | Who is credited with the creation of the poorly translated phrase featured in the opening cutscene of the Japanese video game Zero Wing? | Toaplan | INCORRECT; predicted_answer: The poorly translated phrase "All your base are belong to us" from the opening cutscene of the Japanese video game Zero Wing is credited to the game's English localization team, specifically the translators responsible for the English version. The exact individual translator is not publicly known. | INCORRECT; predicted_answer: The phrase "All your base are belong to us" is credited to **Tatsuya Uemura**, the game's lead programmer and composer, who also handled the English translation for the Sega Mega Drive port. |
| 540317 | Who is the person associated with the development or introduction of the Terrain Management System in the Ford Explorer? | Ford Motor Company | INCORRECT; predicted_answer: The person most associated with the development and introduction of the Terrain Management System in the Ford Explorer is Raj Nair, who was Ford's Chief Technical Officer and played a key role in advancing the vehicle's technology features. | INCORRECT; predicted_answer: The development of the Terrain Management System for the Ford Explorer is most closely associated with **Jeff Seaman**, who served as the vehicle engineering manager for the 2011 Ford Explorer. |
| 250230 | Mazda RX-7 |  | not run | not run |
| 261671 | 1989 Loma Prieta earthquake |  | not run | not run |
| 15240 | Imam |  | not run | not run |
| 67436 | Pseudoephedrine |  | not run | not run |
| 695780 | Who won the 20/20 Award for Best Film Editing for the 1995 film Casino? | Thelma Schoonmaker | CORRECT; predicted_answer: The 20/20 Award for Best Film Editing for the 1995 film *Casino* was won by Thelma Schoonmaker. | not run |
| 200129 | Hair loss |  | not run | not run |
| 57951 | Who was the capital city of the Batavian Department that contained the territory of Southern Holland up to the Meuse and Southwestern Utrecht? | Delft | INCORRECT; predicted_answer: The capital city of the Batavian Department that contained the territory of Southern Holland up to the Meuse and Southwestern Utrecht was The Hague. | CORRECT; predicted_answer: The capital city of the **Department of the Delf** (Departement van de Delf) was **Delft**. |
| 38657800 | Who is the developer of the Pixel Launcher? | Google | CORRECT; predicted_answer: The developer of the Pixel Launcher is Google. | not run |
| 2056103 | Who won the Tamil Nadu State Film Award for Best Actor in 1970 for the film Kaaviya Thalaivi? | Gemini Ganesan | INCORRECT; predicted_answer: The Tamil Nadu State Film Award for Best Actor in 1970 was won by Sivaji Ganesan for the film **Kaaviya Thalaivi**. | CORRECT; predicted_answer: **Gemini Ganesan** won the Tamil Nadu State Film Award for Best Actor in 1970 for his performance in *Kaaviya Thalaivi*. |
| 441357 | Who is the person associated with the creation of the Osmanya script used for writing the Somali language? | Osmanya | not run | not run |
| 479109 | Southern Methodist University |  | not run | not run |
| 356375 | Yoruba language |  | not run | not run |
| 241717 | Clinical trial |  | not run | not run |
| 52374650 | King |  | not run | not run |
| 86224 | Which person was the president of the International Olympic Committee during the 1928 Summer Olympics? | Henri de Baillet-Latour | CORRECT; predicted_answer: The president of the International Olympic Committee during the 1928 Summer Olympics was Henri de Baillet-Latour. | not run |
| 221478 | Who starred as Arnold in the 1982 Broadway production of Torch Song Trilogy? | Harvey Fierstein | CORRECT; predicted_answer: Harvey Fierstein starred as Arnold in the 1982 Broadway production of Torch Song Trilogy. | not run |
| 167051 | Who directed the 1960 film in which Connie Francis played the role of Angie? | Henry Levin | CORRECT; predicted_answer: The 1960 film in which Connie Francis played the role of Angie is "Where the Boys Are," directed by Henry Levin. | not run |
| 20804 | Who was the mayor of Magdeburg according to the infobox? | Lars Winter | INCORRECT; predicted_answer: The mayor of Magdeburg according to the infobox is Lutz Trümper. | INCORRECT; predicted_answer: The current mayor of Magdeburg is **Simone Borris**. |
| 22304 | Osmium |  | not run | not run |
| 45367389 | Which city in the Île-de-France region is a twin city of Greater London? | Paris | not run | not run |
| 105908 | Ford Mustang |  | not run | not run |
| 66958 | In which country is the renminbi the official currency? | People's Republic of China | CORRECT; predicted_answer: The renminbi is the official currency of China. | not run |
| 41853326 | From which club did Inter Miami CF acquire the player Lionel Messi as a Designated Player? | Paris Saint-Germain | CORRECT; predicted_answer: Inter Miami CF acquired Lionel Messi as a Designated Player from Paris Saint-Germain (PSG). | not run |
| 12186 | Guinea-Bissau |  | not run | not run |
| 5643 | Channel Islands |  | not run | not run |
| 19653842 | Which place is the example organism classified as a superorganism in Queller and Strassmann's view of organisms at differing levels of biological organisation? | Ant colony | not run | not run |
| 34411 | Which constellation has the brightest star named Regulus according to the 1977 IAU boundaries? | Leo | CORRECT; predicted_answer: The constellation Leo contains the brightest star named Regulus according to the 1977 IAU boundaries. | not run |
| 217231 | In which region was the DVD for Season 3 of Curb Your Enthusiasm released on February 7, 2005? | Region 2 | INCORRECT; predicted_answer: The DVD for Season 3 of Curb Your Enthusiasm was released in Region 1 on February 7, 2005. | CORRECT; predicted_answer: The DVD for Season 3 of *Curb Your Enthusiasm* was released in **Region 2** (specifically the United Kingdom) on February 7, 2005. |
| 55440889 | Pixel 2 |  | not run | not run |
| 84952 | Which boxer succeeded Marvelous Marvin Hagler as the WBC middleweight champion? | Sugar Ray Leonard | CORRECT; predicted_answer: Sugar Ray Leonard succeeded Marvelous Marvin Hagler as the WBC middleweight champion. | not run |
| 33094374 | Telecommunications |  | not run | not run |
| 22948 | Which place is the mother of the offspring named Antaeus according to the earliest source Apollodorus? | Gaia | CORRECT; predicted_answer: According to the earliest source Apollodorus, the mother of Antaeus is the Earth (Gaia). | not run |
| 2924002 | In which place is the annual DJ Awards event, known for nominating and awarding international DJs in 11 categories, held? | Ibiza, Spain | CORRECT; predicted_answer: The annual DJ Awards event is held in Ibiza, Spain. | not run |
| 30292 | In the quest structure of The Hobbit, where does the journey start? | The Shire | CORRECT; predicted_answer: In the quest structure of *The Hobbit*, the journey starts in the Shire, specifically in Bilbo Baggins' home at Bag End. | not run |
| 91195 | In which place is the Wimbledon Championships tennis tournament annually held? | Wimbledon, London | CORRECT; predicted_answer: The Wimbledon Championships tennis tournament is annually held in London, England. | not run |
| 235959 | In which location was the play 'Butterflies are Free' starring Farrah Fawcett staged? | Jupiter, Florida | INCORRECT; predicted_answer: The play "Butterflies Are Free" starring Farrah Fawcett was staged at the Helen Hayes Theatre in New York City. | CORRECT; predicted_answer: Farrah Fawcett starred in a production of *Butterflies Are Free* at the **Burt Reynolds Dinner Theatre** in Jupiter, Florida, in 1980. |
| 260996 | At which venue did Christian Slater perform the role of Tom Wingfield in 2005? | Ethel Barrymore Theatre | INCORRECT; predicted_answer: In 2005, Christian Slater performed the role of Tom Wingfield at the American Airlines Theatre in New York City. | CORRECT; predicted_answer: Christian Slater performed the role of Tom Wingfield at the **Ethel Barrymore Theatre** on Broadway. |
| 342334 | Autopsy |  | not run | not run |
| 105391 | B movie |  | not run | not run |
| 68761 | Publishing |  | not run | not run |
| 229275 | Lamb and mutton |  | not run | not run |
| 246920 | Visa Inc. |  | not run | not run |
| 2114995 | Dextromethorphan |  | not run | not run |
| 1625048 | Kingdom of Bohemia |  | not run | not run |
| 96875 | Which city was the Great Western Railway originally intended to connect Bristol to by joining the London and Birmingham Railway near it? | London | not run | not run |
| 17278765 | In which city was the 1931 Rose Bowl game played where No. 2 USC defeated No. 1 Tulane? | Pasadena | CORRECT; predicted_answer: The 1931 Rose Bowl game was played in Pasadena, California. | not run |
| 7549995 | Elk |  | not run | not run |
| 151451 | In which location was the documentary titled 'Orange Rockcorps at the Royal Albert Hall' filmed? | Royal Albert Hall | not run | not run |
| 156745 | At which awards ceremony did Julia Roberts win Best Actress in a Motion Picture – Musical or Comedy for Pretty Woman? | Golden Globe Awards | CORRECT; predicted_answer: Julia Roberts won Best Actress in a Motion Picture – Musical or Comedy for Pretty Woman at the Golden Globe Awards. | not run |
| 599 | In which Afroasiatic language branch is the numeral for 'seven' represented as 'sabʕa' in the masculine form? | Arabic | CORRECT; predicted_answer: The numeral for 'seven' as **"sabʕa"** in the masculine form is found in the **Semitic** branch of the Afroasiatic language family. | not run |
| 43088 | In which city did Yogi Berra's team lose the World Series in 1964 as a manager? | St. Louis | CORRECT; predicted_answer: Yogi Berra's team, the New York Yankees, lost the 1964 World Series in St. Louis. | not run |
| 26457880 | Air India |  | not run | not run |
| 31730 | British Armed Forces |  | not run | not run |
| 47864412 | Which place is represented by the bilabial nasal consonant phoneme in the Nepali language? | Bilabial | not run | not run |
| 18947898 | What is the country of origin of the Amnesty International Secretary General who served from 1992 to 2001? | Senegal | CORRECT; predicted_answer: The Amnesty International Secretary General who served from 1992 to 2001, Pierre Sané, is from Senegal. | not run |
| 57877 | Sodium hydroxide |  | not run | not run |
| 407239 | The Indian Express |  | not run | not run |
| 32005912 | Grimes |  | not run | not run |
| 214179 | In which city was the American industrial metal band Ministry founded in 1981? | Chicago | CORRECT; predicted_answer: Ministry was founded in Chicago in 1981. | not run |
| 15049 | In which city did the Indianapolis Colts' Ring of Honor inductee Robert Irsay serve as owner from 1972 to 1997? | Indianapolis | not run | not run |
| 80482 | During Beatrix of the Netherlands' reign, which polity had Henny Eman serving as Prime Minister starting in 1986? | Aruba | CORRECT; predicted_answer: During Beatrix of the Netherlands' reign, Henny Eman served as Prime Minister of Aruba starting in 1986. | not run |
| 35412202 | Before the introduction of Wikidata, where were the interlanguage links for a Wikipedia article listed as they appeared in an edit box and on the article's page? | Wikipedia | not run | not run |
| 57659 | Which stadium is shared by both Club Africain and Espérance Sportive de Tunis according to the sports clubs table in Tunis? | Stade Olympique de Radès Stade El Menzah | INCORRECT; predicted_answer: According to the sports clubs table in Tunis, both Club Africain and Espérance Sportive de Tunis share the Stade Olympique de Radès. | CORRECT; predicted_answer: The stadium shared by both Club Africain and Espérance Sportive de Tunis is the **Stade Olympique de Hammadi Agrebi** (commonly known as the **Stade de Radès**). |
| 1064 | In which order is the almond tree classified according to its scientific classification? | Rosales | CORRECT; predicted_answer: The almond tree is classified in the order **Rosales**. | not run |
| 2209490 | Romanization of Arabic |  | not run | not run |
| 422038 | Vigo |  | not run | not run |
| 23906 | Peterborough |  | not run | not run |
| 67923 | East Sussex |  | not run | not run |
| 1161220 | Khushbu Sundar |  | not run | not run |
| 113933 | Iowa City, Iowa |  | not run | not run |
| 22461 | Osteoporosis |  | not run | not run |
| 47498 | All your base are belong to us |  | not run | not run |
| 129619 | At which awards ceremony did Whoopi Goldberg win Best Supporting Actress for her role in the film Ghost? | Academy Awards | CORRECT; predicted_answer: Whoopi Goldberg won Best Supporting Actress for her role in the film *Ghost* at the Academy Awards (Oscars). | not run |
| 540317 | Which terrain mode is the default start selection in the Ford Explorer's Terrain Management System? | Normal Driving mode | CORRECT; predicted_answer: The default start selection in the Ford Explorer's Terrain Management System is the **Normal** mode. | not run |
| 261671 | 1989 Loma Prieta earthquake |  | not run | not run |
| 250230 | Mazda RX-7 |  | not run | not run |
| 15240 | Imam |  | not run | not run |
| 67436 | Pseudoephedrine |  | not run | not run |
| 2056103 | In which Indian state was the Tamil Nadu State Film Award for Best Actor won by Gemini Ganesan for the film Kaaviya Thalaivi in 1970? | Tamil Nadu | not run | not run |
| 695780 | In which country is the Nastro d'Argento award, won by Dante Ferretti for Best Production Design for the film Casino, presented? | Italy | CORRECT; predicted_answer: The Nastro d'Argento award is presented in Italy. | not run |
| 200129 | Hair loss |  | not run | not run |
| 57951 | Which modern territory corresponds mostly to the French Department of the Mouths of the Meuse? | South Holland | INCORRECT; predicted_answer: The French Department of the Mouths of the Meuse mostly corresponds to the modern territory of Zeeland in the Netherlands. | CORRECT; predicted_answer: The modern territory that corresponds mostly to the French Department of the Mouths of the Meuse (*Bouches-de-la-Meuse*) is the **South Holland** (*Zuid-Holland*) province of the **Netherlands**. |
| 20804 | Which district of Magdeburg includes the former municipality of Beyendorf-Sohlen? | Beyendorf-Sohlen | not run | not run |
| 221478 | At which venue did Harvey Fierstein's play 'Casa Valentina' premiere on Broadway? | Samuel J. Friedman Theatre | CORRECT; predicted_answer: Harvey Fierstein's play "Casa Valentina" premiered on Broadway at the Samuel J. Friedman Theatre. | not run |
| 356375 | In the Yoruba language vowel system, which place of articulation corresponds to the nasal vowel represented as ũ? | Back | CORRECT; predicted_answer: In the Yoruba vowel system, the nasal vowel represented as **ũ** corresponds to the **back** place of articulation. | not run |
| 241717 | Clinical trial |  | not run | not run |
| 52374650 | King |  | not run | not run |
| 441357 | In which place is the Somali language primarily spoken as a mother tongue? | Greater Somalia | INCORRECT; predicted_answer: The Somali language is primarily spoken as a mother tongue in Somalia. | INCORRECT; predicted_answer: Somali is primarily spoken as a mother tongue in the **Horn of Africa**, specifically in **Somalia**, **Somaliland**, **Djibouti**, the **Somali Region of Ethiopia**, and the **North Eastern Province of Kenya**. |
| 479109 | In which place is the university located that has a graduate Business program ranked 34th by USNWR? | University Park, Texas | INCORRECT; predicted_answer: The university with a graduate Business program ranked 34th by USNWR is located in Ann Arbor, Michigan. | INCORRECT; predicted_answer: The university with the graduate business program ranked 34th by U.S. News & World Report (2024-2025) is the **University of Rochester** (Simon Business School), located in **Rochester, New York**. |
| 22304 | Osmium |  | not run | not run |
| 86224 | Which country ranked second in the medal count at the 1928 Summer Olympics? | Germany | INCORRECT; predicted_answer: The United States ranked second in the medal count at the 1928 Summer Olympics. | CORRECT; predicted_answer: **Germany** ranked second in the medal count at the 1928 Summer Olympics, winning a total of 31 medals (10 gold, 7 silver, and 14 bronze). |
| 167051 | In which place was the director Raoul Walsh, who directed the 1958 film featuring Connie Francis as the singing voice of Miss Kate, primarily active? | United States | CORRECT; predicted_answer: Raoul Walsh was primarily active in Hollywood, United States. | not run |
| 1069583 | Which place is symbolized by the natural teacher that is steadfastly productive, gets abused, heals, and is steady in giving nourishment according to the 24 teachers from nature in Dattatreya's teachings? | Earth | not run | not run |
| 683599 | At which venue did Hedley Verity achieve his best bowling figures of 10 wickets for 10 runs in a County Championship innings in 1932? | Headingley | CORRECT; predicted_answer: Hedley Verity achieved his best bowling figures of 10 wickets for 10 runs in a County Championship innings in 1932 at Headingley. | not run |
| 1787105 | In animal mating systems, which system involves a single male mating with multiple females? | Polygyny | CORRECT; predicted_answer: The mating system in which a single male mates with multiple females is called **polygyny**. | not run |
| 32551521 | Which dependency is associated with the legal nationality of Denmark according to FIFA eligibility rules? | Faroe Islands | CORRECT; predicted_answer: According to FIFA eligibility rules, the Faroe Islands is the dependency associated with the legal nationality of Denmark. | not run |
| 180763 | According to the THE Subject Ranking 2024, in which country is the university ranked 4th nationally for Life sciences? | Germany | INCORRECT; predicted_answer: According to the THE Subject Ranking 2024, the university ranked 4th nationally for Life Sciences is in the United Kingdom. | INCORRECT; predicted_answer: According to the THE World University Rankings 2024 by subject (Life Sciences), the university ranked 4th nationally in the **United Kingdom** is the **University of Edinburgh**. |
| 4595410 | 1970 United States census |  | not run | not run |
| 56668 | In which order is the apricot classified according to its scientific classification? | Rosales | CORRECT; predicted_answer: The apricot is classified in the order **Rosales**. | not run |
| 83316 | In which country did Ray Davies' 2010 studio album 'See My Friends' reach its highest peak chart position? | United Kingdom | CORRECT; predicted_answer: Ray Davies' 2010 studio album "See My Friends" reached its highest peak chart position in the United Kingdom. | not run |
| 333199 | Which airline alliance did Continental Airlines join after exiting SkyTeam in October 2009? | Star Alliance | CORRECT; predicted_answer: After exiting SkyTeam in October 2009, Continental Airlines joined the Star Alliance. | not run |
| 107825 | Newport Beach, California |  | not run | not run |
| 1146123 | In which city was the San Diego Film Festival held where Colin Hanks won the Soaring Star Award in 2005? | San Diego | not run | not run |
| 61795854 | All India Institutes of Medical Sciences |  | not run | not run |
| 31940 | In which location was the United Nations Convention on the Law of the Sea signed? | Montego Bay, Jamaica | CORRECT; predicted_answer: The United Nations Convention on the Law of the Sea was signed in Montego Bay, Jamaica. | not run |
| 226734 | Which Nigerian state was created in 1996 from the East Central region and is listed in the 1996 column of the chronology table? | Ebonyi | not run | not run |
| 16801 | In which country was the self-defense system Krav Maga developed for the military forces? | Israel | CORRECT; predicted_answer: Krav Maga was developed in Israel for the military forces. | not run |
| 342334 | Autopsy |  | not run | not run |
| 105391 | B movie |  | not run | not run |
| 68761 | Publishing |  | not run | not run |
| 229275 | Lamb and mutton |  | not run | not run |
| 246920 | Visa Inc. |  | not run | not run |
| 2114995 | Dextromethorphan |  | not run | not run |
| 1625048 | Kingdom of Bohemia |  | not run | not run |
| 569459 | What is the geographic range of the white-tailed deer subspecies listed in the South America range map? | Central and South America | not run | not run |
| 17278765 | Which trophy was awarded in the 1931 Rose Bowl that served as a title game for the Albert Russel Erskine Trophy and the Dickinson System's Knute Rockne Memorial Trophy? | Albert Russel Erskine Trophy | not run | not run |
| 96875 | What is the long title of the Act of Parliament that authorized the construction of the Great Western Railway? | An Act for making a Railway from Bristol to join the London and Birmingham Railway near London, to be called "The Great Western Railway," with Branches therefrom to the Towns of Bradford and Trowbridge in the County of Wilts. | INCORRECT; predicted_answer: The long title of the Act of Parliament that authorized the construction of the Great Western Railway is:  "An Act for making a Railway from London to Bristol and Exeter." | CORRECT; predicted_answer: An Act for making a Railway from Bristol to join the London and Birmingham Railway near London, to be called "The Great Western Railway," with Branches therefrom to the Towns of Bradford and Trowbridge in the County of Wilts. |
| 7549995 | Elk |  | not run | not run |
| 599 | In the Afroasiatic numeral system table, which language branch uses the term 'wāḥid' for the masculine form of the numeral one? | Arabic | CORRECT; predicted_answer: The Semitic branch of the Afroasiatic numeral system uses the term 'wāḥid' for the masculine form of the numeral one. | not run |
| 43088 | Which team did Yogi Berra manage when he lost the World Series to the Oakland Athletics? | NYM | INCORRECT; predicted_answer: Yogi Berra managed the New York Yankees when he lost the World Series to the Oakland Athletics. | CORRECT; predicted_answer: Yogi Berra managed the **New York Mets** when they lost the 1973 World Series to the Oakland Athletics. |
| 151451 | What role did Busta Rhymes voice in the 1998 film The Rugrats Movie? | Reptar Wagon | INCORRECT; predicted_answer: Busta Rhymes voiced the character Spike, the dog, in the 1998 film The Rugrats Movie. | CORRECT; predicted_answer: Busta Rhymes voiced the **Reptar Wagon**. |
| 26457880 | Air India |  | not run | not run |
| 31730 | British Armed Forces |  | not run | not run |
| 156745 | Which song won the BMI Film & TV Award for Most Performed Song from a Film related to Pretty Woman? | It Must Have Been Love | INCORRECT; predicted_answer: The song "Oh, Pretty Woman" by Roy Orbison won the BMI Film & TV Award for Most Performed Song from a Film related to Pretty Woman. | CORRECT; predicted_answer: The song is **"It Must Have Been Love,"** written by Per Gessle and performed by Roxette. |
| 18947898 | Which country is the origin of the Amnesty International Secretary General who served from 1992 to 2001? | Senegal | CORRECT; predicted_answer: The Amnesty International Secretary General who served from 1992 to 2001, Pierre Sané, is from Senegal. | not run |
| 57877 | Sodium hydroxide |  | not run | not run |
| 32005912 | Grimes |  | not run | not run |
| 407239 | The Indian Express |  | not run | not run |
| 57659 | Which stadium is shared by both Club Africain and Espérance Sportive de Tunis? | Stade Olympique de Radès Stade El Menzah | INCORRECT; predicted_answer: Both Club Africain and Espérance Sportive de Tunis share the Stade Olympique de Radès. | CORRECT; predicted_answer: The stadium shared by both Club Africain and Espérance Sportive de Tunis is the **Stade Olympique de Hammadi Agrebi** (commonly known as the **Stade de Radès**). |
| 80482 | Which award did Beatrix of the Netherlands receive in 1996? | Charlemagne Prize | CORRECT; predicted_answer: In 1996, Beatrix of the Netherlands received the Charlemagne Prize. | not run |
| 15049 | Which position did Dallas Clark hold when he was inducted into the Indianapolis Colts Ring of Honor? | TE | not run | not run |
| 76988 | Which time-frequency analysis method in ECG signal processing is suitable for fully non-stationary and nonlinear signals and provides instantaneous frequency distribution? | Hilbert–Huang transform | CORRECT; predicted_answer: The **Hilbert-Huang Transform (HHT)** is suitable for fully non-stationary and nonlinear ECG signals and provides an instantaneous frequency distribution. It involves Empirical Mode Decomposition (EMD) to adaptively decompose the signal into intrinsic mode functions, followed by the Hilbert transform to obtain instantaneous frequency. | not run |
| 35412202 | What link currently allows readers to edit interlanguage and interwiki links centralized by Wikidata? | The "Edit interlanguage links" link | not run | not run |
| 1064 | What is the subgenus classification of the almond tree? | Prunus subg. Amygdalus | CORRECT; predicted_answer: The almond tree (Prunus dulcis) is classified under the subgenus **Amygdalus**. | not run |
| 2209490 | Romanization of Arabic |  | not run | not run |
| 422038 | Vigo |  | not run | not run |
| 23906 | Peterborough |  | not run | not run |
| 67923 | East Sussex |  | not run | not run |
| 1161220 | Khushbu Sundar |  | not run | not run |
| 113933 | Iowa City, Iowa |  | not run | not run |
| 22461 | Osteoporosis |  | not run | not run |
| 129619 | Which award did Whoopi Goldberg win for her role in the film that is listed under the Academy Awards category? | Best Supporting Actress | not run | not run |
| 540317 | What is the default start selection mode in the Ford Explorer's Terrain Management System? | Normal Driving mode | CORRECT; predicted_answer: The default start selection mode in the Ford Explorer's Terrain Management System is **Normal** mode. | not run |
| 250230 | Mazda RX-7 |  | not run | not run |
| 261671 | 1989 Loma Prieta earthquake |  | not run | not run |
| 15240 | Imam |  | not run | not run |
| 67436 | Pseudoephedrine |  | not run | not run |
| 695780 | Which recipient won the 20/20 Awards for Best Film Editing for the film Casino (1995)? | Thelma Schoonmaker | INCORRECT; predicted_answer: The recipient who won the 20/20 Awards for Best Film Editing for the film Casino (1995) is Martin Hunter. | CORRECT; predicted_answer: **Thelma Schoonmaker** won the 20/20 Award for Best Film Editing for *Casino*. |
| 57951 | What is the French name of the department that mostly corresponds to the modern territory of Zeeland? | Département des Bouches-de-l'Escaut | INCORRECT; predicted_answer: The French name of the department that mostly corresponds to the modern territory of Zeeland is **Zélande**. | CORRECT; predicted_answer: The French name of the department was **Bouches-de-l'Escaut**. |
| 200129 | Hair loss |  | not run | not run |
| 2056103 | Which award did Gemini Ganesan win for his performance in the film Kaaviya Thalaivi? | Tamil Nadu State Film Award for Best Actor | INCORRECT; predicted_answer: Gemini Ganesan did not act in the film *Kaaviya Thalaivi*. The film stars Kangana Ranaut, and Gemini Ganesan is not associated with it. | CORRECT; predicted_answer: Gemini Ganesan won the **Tamil Nadu State Film Award for Best Actor** for his performance in *Kaaviya Thalaivi* (1970). |
| 7549995 | Elk |  | not run | not run |
| 599 | How many different Afroasiatic language branches are represented in the numeral table for the number 'Seven' in masculine form? | 6 (acceptable range: anything between 5 and 7) | CORRECT; predicted_answer: The numeral table for the number 'Seven' in masculine form represents **6 different Afroasiatic language branches**. | not run |
| 43088 | How many regular season games did Yogi Berra manage for the New York Yankees in 1964? | 162 (acceptable range: anything between 160 and 164) | INCORRECT; predicted_answer: Yogi Berra managed 57 regular season games for the New York Yankees in 1964. | CORRECT; predicted_answer: Yogi Berra managed **162** regular season games for the New York Yankees in 1964. |
| 26457880 | Air India |  | not run | not run |
| 31730 | British Armed Forces |  | not run | not run |
| 47864412 | How many distinct Nepali consonant phonemes are listed in the table under the 'Consonants' section? | 33 | not run | not run |
| 57905 | How many time zones does the Sakha Republic span? | 3 (acceptable range: anything between 2 and 4) | CORRECT; predicted_answer: The Sakha Republic spans 3 time zones. | not run |
| 18947898 | How many years did Martin Ennals serve as Secretary General of Amnesty International? | 12 (acceptable range: anything between 11 and 13) | INCORRECT; predicted_answer: Martin Ennals served as Secretary General of Amnesty International for 10 years, from 1968 to 1977. | CORRECT; predicted_answer: Martin Ennals served as Secretary General of Amnesty International for **12 years**, from 1968 to 1980. |
| 57877 | Sodium hydroxide |  | not run | not run |
| 32005912 | Grimes |  | not run | not run |
| 407239 | The Indian Express |  | not run | not run |
| 80482 | How many sons did Beatrix of the Netherlands have? | 3 (acceptable range: anything between 2 and 4) | CORRECT; predicted_answer: Beatrix of the Netherlands had three sons. | not run |
| 76988 | What is the maximum duration in milliseconds of the PR interval as measured on a standard ECG graph paper? | 200 (acceptable range: anything between 198 and 202) | CORRECT; predicted_answer: The maximum normal duration of the PR interval on a standard ECG is **200 milliseconds**. | not run |
| 1064 | How many taxonomic clades are listed in the scientific classification of the almond in the infobox? | 4 | not run | not run |
| 35412202 | How many item statements did Wikidata have as of early 2025? | 1650000000 | not run | not run |
| 15049 | How many years did Peyton Manning play for the Indianapolis Colts according to the Ring of Honor table? | 14 (acceptable range: anything between 13 and 15) | CORRECT; predicted_answer: According to the Ring of Honor table, Peyton Manning played for the Indianapolis Colts for 14 years (1998–2011). | not run |
| 2209490 | Romanization of Arabic |  | not run | not run |
| 422038 | Vigo |  | not run | not run |
| 23906 | Peterborough |  | not run | not run |
| 67923 | East Sussex |  | not run | not run |
| 1161220 | Khushbu Sundar |  | not run | not run |
| 113933 | Iowa City, Iowa |  | not run | not run |
| 22461 | Osteoporosis |  | not run | not run |
| 47498 | All your base are belong to us |  | not run | not run |
| 129619 | How many Academy Awards did the film Ghost win? | 2 (acceptable range: anything between 1 and 3) | CORRECT; predicted_answer: The film *Ghost* won 2 Academy Awards. | not run |
| 250230 | Mazda RX-7 |  | not run | not run |
| 261671 | 1989 Loma Prieta earthquake |  | not run | not run |
| 15240 | Imam |  | not run | not run |
| 67436 | Pseudoephedrine |  | not run | not run |
| 2056103 | In which year did Gemini Ganesan win the Tamil Nadu State Film Award for Best Actor? | 1970 | not run | not run |
| 18938412 | How many songs by Richard Marx won the 'Most Performed Songs' award according to the listed awards and nominations? | 14 | not run | not run |
| 200129 | Hair loss |  | not run | not run |
| 38657800 | How many months ago was the latest release of Pixel Launcher as of January 3, 2025? | 16 | not run | not run |
| 57951 | How many departments were there in the Batavian Republic reorganization of the Netherlands from 1798 to 1801? | 8 (acceptable range: anything between 7 and 9) | CORRECT; predicted_answer: There were 8 departments in the Batavian Republic reorganization of the Netherlands from 1798 to 1801. | not run |
| 695780 | How many total nominations did Sharon Stone receive for Best Actress or equivalent categories for the 1995 film Casino? | 4 (acceptable range: anything between 3 and 5) | INCORRECT; predicted_answer: Sharon Stone received a total of 5 nominations for Best Actress or equivalent categories for the 1995 film *Casino*. | INCORRECT; predicted_answer: Sharon Stone received **6** major nominations for Best Actress for her role in *Casino*:  1.  **Academy Awards (Oscars):** Best Actress 2.  **Golden Globe Awards:** Best Actress – Motion Picture Drama (**Won**) 3.  **Screen Actors Guild (SAG) Awards:** Outstanding Performance by a Female Actor in a Leading Role 4.  **Chicago Film Critics Association:** Best Actress 5.  **Dallas-Fort Worth Film Critics Association:** Best Actress 6.  **MTV Movie Awards:** Best Female Performance |
| 221478 | How many different venues hosted the Broadway productions of Harvey Fierstein's written works listed in the writing table? | 9 | not run | not run |
| 441357 | How many numbers are listed in the Somali language numbers table from eleven to twenty? | 10 | not run | not run |
| 356375 | How many oral vowel sounds are listed in the Yoruba language vowel table? | 7 | not run | not run |
| 241717 | Clinical trial |  | not run | not run |
| 52374650 | King |  | not run | not run |
| 167051 | How many films listed in Connie Francis's filmography were released before 1960? | 3 | not run | not run |
| 22304 | What is the highest positive oxidation state of osmium listed in its chemical properties table? | 8 | not run | not run |
| 86224 | How many gold medals did the United States win at the 1928 Summer Olympics? | 22 (acceptable range: anything between 21 and 23) | CORRECT; predicted_answer: The United States won 22 gold medals at the 1928 Summer Olympics. | not run |
| 479109 | What was the USNWR graduate school ranking of the Business program at Southern Methodist University? | 34 (acceptable range: anything between 33 and 35) | INCORRECT; predicted_answer: As of the most recent U.S. News & World Report graduate school rankings, Southern Methodist University's Cox School of Business is ranked #39 among Best Business Schools. | CORRECT; predicted_answer: In the 2024-2025 *U.S. News & World Report* rankings, the Full-Time MBA program at SMU (Cox) is ranked **#34** in the nation. |
| 20804 | How many Stadtteile (districts) is the city of Magdeburg divided into? | 40 (acceptable range: anything between 39 and 41) | INCORRECT; predicted_answer: The city of Magdeburg is divided into 11 Stadtteile (districts). | CORRECT; predicted_answer: Magdeburg is divided into **40** Stadtteile (districts). |
| 57877 | Sodium hydroxide |  | not run | not run |
| 32005912 | Grimes |  | not run | not run |
| 407239 | The Indian Express |  | not run | not run |
| 214179 | In what year did former Ministry band member William "Bill" Rieflin die? | 2020 | not run | not run |
| 15049 | In what year was Tony Dungy inducted into the Indianapolis Colts Ring of Honor? | 2010 | not run | not run |
| 57659 | In what year was the football club Espérance Sportive de Tunis founded? | 1919 | CORRECT; predicted_answer: Espérance Sportive de Tunis was founded in 1919. | not run |
| 80482 | In what year did Mark Rutte begin his term as Prime Minister of the Netherlands during Beatrix's reign? | 2010 | CORRECT; predicted_answer: Mark Rutte began his term as Prime Minister of the Netherlands in 2010 during Queen Beatrix's reign. | not run |
| 76988 | What is the duration range in milliseconds of the PR interval as measured on a standard ECG? | 120 to 200 ms | CORRECT; predicted_answer: The normal duration range of the PR interval on a standard ECG is **120 to 200 milliseconds**. | not run |
| 35412202 | In what year was the initial rollout of Wikidata's centralized interlanguage links feature implemented? | 2012 | INCORRECT; predicted_answer: The initial rollout of Wikidata's centralized interlanguage links feature was implemented in 2013. | INCORRECT; predicted_answer: The initial rollout of Wikidata's centralized interlanguage links feature was implemented in **2013**. |
| 2209490 | Romanization of Arabic |  | not run | not run |
| 422038 | Vigo |  | not run | not run |
| 23906 | Peterborough |  | not run | not run |
| 67923 | East Sussex |  | not run | not run |
| 1161220 | Khushbu Sundar |  | not run | not run |
| 113933 | Iowa City, Iowa |  | not run | not run |
| 22461 | Osteoporosis |  | not run | not run |
| 47498 | In what year was the video game Zero Wing, which features the phrase 'All your base are belong to us,' originally released in Japanese arcades? | 1989 | CORRECT; predicted_answer: Zero Wing was originally released in Japanese arcades in 1989. | not run |
| 129619 | In what year did the film Ghost win the Academy Award for Best Supporting Actress? | 1991 | CORRECT; predicted_answer: The film Ghost won the Academy Award for Best Supporting Actress in 1991. | not run |
| 540317 | In what model years did the Ford Explorer receive a 'Marginal' rating for the small overlap frontal offset (driver side) according to NHTSA scores? | 2013-2019 | INCORRECT; predicted_answer: The Ford Explorer received a 'Marginal' rating for the small overlap frontal offset (driver side) in the 2011 and 2012 model years according to NHTSA scores. | INCORRECT; predicted_answer: The NHTSA does not perform a "small overlap frontal offset" test; that specific test is conducted by the **Insurance Institute for Highway Safety (IIHS)**.  According to the IIHS, the Ford Explorer received a **Marginal** rating for the driver-side small overlap front test for model years **2011 through 2019**. |
| 261671 | 1989 Loma Prieta earthquake |  | not run | not run |
| 250230 | Mazda RX-7 |  | not run | not run |
| 15240 | Imam |  | not run | not run |
| 67436 | Pseudoephedrine |  | not run | not run |
| 57951 | In what year did the Netherlands become fully part of France, leading to the establishment of French departments with borders largely maintained? | 1810 | CORRECT; predicted_answer: The Netherlands became fully part of France in 1810, leading to the establishment of French departments with borders largely maintained. | not run |
| 695780 | In what year did the film Casino win the Golden Globe Award for Best Actress in a Motion Picture – Drama? | 1996 | CORRECT; predicted_answer: The film Casino won the Golden Globe Award for Best Actress in a Motion Picture – Drama in 1996. | not run |
| 200129 | Hair loss |  | not run | not run |
| 2056103 | In what year did Gemini Ganesan receive the Padma Shri award? | 1971 | CORRECT; predicted_answer: Gemini Ganesan received the Padma Shri award in 1971. | not run |
| 38657800 | On what date was the latest release of the Pixel Launcher, Android 16, made available? | January 3, 2025 | not run | not run |
| 221478 | In what year did Harvey Fierstein's play 'Torch Song Trilogy' premiere at the Little Theatre on Broadway? | 1982 | CORRECT; predicted_answer: Harvey Fierstein's play "Torch Song Trilogy" premiered at the Little Theatre on Broadway in 1982. | not run |
| 356375 | Yoruba language |  | not run | not run |
| 241717 | Clinical trial |  | not run | not run |
| 52374650 | King |  | not run | not run |
| 479109 | What was the USNWR graduate school ranking of Southern Methodist University's Business program? | 34 | INCORRECT; predicted_answer: As of the most recent U.S. News & World Report graduate school rankings, Southern Methodist University's Cox School of Business is ranked #39 among Best Business Schools (MBA programs). | CORRECT; predicted_answer: For the 2024-2025 edition, Southern Methodist University (Cox) is ranked **#34** in Best Business Schools by *U.S. News & World Report*. |
| 22304 | What is the highest oxidation state of osmium listed in the chemical properties table? | +8 | not run | not run |
| 86224 | In what year were the Summer Olympics held in Amsterdam where the United States ranked first in the medal count? | 1928 | CORRECT; predicted_answer: The Summer Olympics were held in Amsterdam in 1928, where the United States ranked first in the medal count. | not run |
| 167051 | In what year was the film 'Where the Boys Are', in which Connie Francis played the role of Angie, released? | 1960 | CORRECT; predicted_answer: The film "Where the Boys Are," in which Connie Francis played the role of Angie, was released in 1960. | not run |
| 20804 | In what year was the city of Magdeburg divided into its 40 Stadtteile (districts)? | 2024 | INCORRECT; predicted_answer: The city of Magdeburg was divided into its 40 Stadtteile (districts) in the year 1990. | INCORRECT; predicted_answer: Magdeburg was divided into its current 40 districts (*Stadtteile*) on **October 5, 1995**, following a decision by the City Council. |
| 180763 | In what year was the ARWU Subject Ranking that listed the University of Göttingen's ranking in Agricultural Sciences as 14 globally and 1 nationally published? | 2023 | not run | not run |
| 1069583 | In the legend of Dattatreya's 24 teachers from nature, which natural element is observed to wax and wane but whose oneness does not change, symbolizing the continuous eternal reality of the soul's birth, death, and rebirth cycle? | Moon | not run | not run |
| 32551521 | In what year was Article 6.1 of the Regulations Governing the Applications of Statutes, which allows players to represent another FIFA member association after five years residency if they share the same legal nationality, established? | 2020 | not run | not run |
| 683599 | In what year did Hedley Verity achieve the best bowling in an innings with a total of 10/10 in the County Championship? | 1932 | CORRECT; predicted_answer: Hedley Verity achieved the best bowling in an innings with a total of 10/10 in the County Championship in the year 1932. | not run |
| 4595410 | 1970 United States census |  | not run | not run |
| 104944 | On what month, day, and year was Charles XII of Sweden coronated? | December 14, 1697 | CORRECT; predicted_answer: Charles XII of Sweden was coronated on December 14, 1697. | not run |
| 56668 | In what year was the apricot scientifically classified under the type species Prunus armeniaca L.? | 1753 | CORRECT; predicted_answer: The apricot was scientifically classified under the type species Prunus armeniaca L. in the year 1753. | not run |
| 333199 | On what month, day, and year did Alitalia exit the SkyTeam airline alliance? | October 15, 2021 | INCORRECT; predicted_answer: Alitalia exited the SkyTeam airline alliance on October 14, 2021. | CORRECT; predicted_answer: Alitalia exited the SkyTeam alliance on **October 15, 2021**, the same day the airline ceased all operations. |


## Rejected And Rerun Decisions

| Page ID | Stage | Exact reason | Page/question |
| ---: | --- | --- | --- |
| 22093 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | National Basketball Association |
| 17416221 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km` | South Africa |
| 9316 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=trillion` | England |
| 32611 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=24` | Vietnam War |
| 5489 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km` | Chile |
| 13277 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=9` | Holy Roman Empire |
| 11857 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | George Lucas |
| 19261 | `route_generation` | `wikipedia_infobox_llm_discarded:No person names are provided in the twin cities table to support a single_fact question with a Person answer.` | Monaco |
| 14849 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | Who is the person associated with the slogan "Land of Lincoln" for the state of Illinois? |
| 738 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who was the President of Albania according to the Politics table? |
| 31740 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_3:answer_in_title` | Which school at the University of Michigan was ranked number 1 in the U.S. News Best Schools for Social Work in 2024? |
| 292259 | `route_generation` | `wikipedia_infobox_llm_discarded:No person name is provided in the table for any language broadcast start; thus no safe single person answer can be derived.` | Deutsche Welle |
| 21355232 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which person is credited with founding the National Park Service in the United States? |
| 39776 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=2` | Denial-of-service attack |
| 40010153 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=2` | Goa |
| 5488 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:active` | Chad |
| 199445 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who scored 8 goals for England in international matches in the year 2014? |
| 1640 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | Who succeeded Æthelred as king around the year 871 according to the chronology of Alfred the Great? |
| 8083 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who won the Grammy Award for Best Rap Solo Performance in 1994 for the song "Let Me Ride"? |
| 151603 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who played the role of Gurd Canliss in the 1964 episode "Canliss" of the television program Rawhide? |
| 45367389 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any person names, so no single person answer can be derived.` | Greater London |
| 41853326 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | Who was the head coach of Inter Miami CF as of April 14, 2026? |
| 105908 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=10` | Ford Mustang |
| 60382764 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | Who was the emperor of Japan during the Taika era from 645 to 650? |
| 12186 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=10` | Guinea-Bissau |
| 66958 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | Who is the person associated with the official currency of the People's Republic of China? |
| 5643 | `route_generation` | `wikipedia_infobox_llm_discarded:No suitable person-related factual data in the top-ranked table to generate a single-fact question with a person answer.` | Channel Islands |
| 34411 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who is the brightest star in the constellation that the Sun stays in from 10 August to 15 September according to the 1977 IAU boundaries? |
| 217231 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which person provided commentary on the pilot episode in the DVD release of Curb Your Enthusiasm Season 1? |
| 55440889 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=g` | Pixel 2 |
| 235916 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Who won the Interactive Achievement Award for Outstanding Achievement in Character Performance – Female for the work Enter the Matrix in 2004? |
| 30292 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | Who is the descendant of kings restored to his ancestral throne in The Lord of the Rings according to Randel Helms's analysis of quest structure? |
| 33094374 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Telecommunications |
| 22948 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who is the mother of the offspring named Arion according to the earliest source Apollodorus? |
| 84952 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who succeeded Marvelous Marvin Hagler as the WBC middleweight champion after his reign ended on April 6, 1987? |
| 91195 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who holds the record for the most singles titles in the Open Era at the Wimbledon Gentlemen's Championships? |
| 235959 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who played the role of Holly 13 in the 1976 film Logan's Run? |
| 260996 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | Who played the role of Clifford Glimmer in the 1999 stage production of Side Man at the John Golden Theatre? |
| 342334 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:present` | Autopsy |
| 105391 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:active` | B movie |
| 68761 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Publishing |
| 229275 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=kt` | Lamb and mutton |
| 246920 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million,billion` | Visa Inc. |
| 2114995 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=15` | Dextromethorphan |
| 569459 | `route_generation` | `wikipedia_infobox_llm_discarded:No person-related data in the top-ranked tables to form a valid single_fact question with a Person answer.` | White-tailed deer |
| 1625048 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km2` | Kingdom of Bohemia |
| 17278765 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | Who was the winning team in the 1931 Rose Bowl that served as the title game for the Albert Russel Erskine Trophy and the Dickinson System's Knute Rockne Memorial Trophy? |
| 7549995 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=18` | Elk |
| 151451 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Who played the role of Rasaan in the 2000 film Shaft? |
| 43088 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | Who was the manager of the New York Mets during the 1973 season when the team lost the World Series to the Oakland Athletics? |
| 156745 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who won the Golden Globe Award for Best Actress in a Motion Picture – Musical or Comedy for the film Pretty Woman? |
| 26457880 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=tonnes` | Air India |
| 31730 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=16` | British Armed Forces |
| 57905 | `route_generation` | `wikipedia_infobox_llm_discarded:No person names are present in the top-ranked table to form a valid single_fact question with a Person answer.` | Sakha Republic |
| 47864412 | `route_generation` | `wikipedia_infobox_llm_discarded:No Person answer type data available in the top three tables to generate a valid question.` | Nepali language |
| 18947898 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who served as the Secretary General of Amnesty International from 1992 to 2001? |
| 57877 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ml,g,m` | Sodium hydroxide |
| 32005912 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Grimes |
| 407239 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | The Indian Express |
| 57659 | `route_generation` | `wikipedia_infobox_llm_discarded:No person name is provided in the table for any club's foundation; thus, no single-fact question with a Person answer type can be generated.` | Tunis |
| 80482 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who was the Prime Minister of the Netherlands at the start of Queen Beatrix's reign in 1980? |
| 214179 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which former member of Ministry played drums, backing vocals, keyboards, and guitar and was active from 1986 to 1994 before passing away in 2020? |
| 76988 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which method used in time-frequency analysis of ECG signal processing is suitable for fully non-stationary and nonlinear signals and provides instantaneous frequency distribution? |
| 35412202 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | Who is credited with centralizing the information of interlanguage links for Wikipedia articles prior to the introduction of Wikidata? |
| 2209490 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ha,g` | Romanization of Arabic |
| 422038 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,metres,millimetres,m` | Vigo |
| 23906 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=39` | Peterborough |
| 67923 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | East Sussex |
| 1161220 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Khushbu Sundar |
| 113933 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Iowa City, Iowa |
| 22461 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Osteoporosis |
| 129619 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who won the Academy Award for Best Supporting Actress for the film Ghost (1990)? |
| 47498 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | Who is credited with the creation of the poorly translated phrase featured in the opening cutscene of the Japanese video game Zero Wing? |
| 540317 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | Who is the person associated with the development or introduction of the Terrain Management System in the Ford Explorer? |
| 250230 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,kg,kw,lb` | Mazda RX-7 |
| 261671 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=m` | 1989 Loma Prieta earthquake |
| 15240 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:unknown` | Imam |
| 67436 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=18` | Pseudoephedrine |
| 695780 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who won the 20/20 Award for Best Film Editing for the 1995 film Casino? |
| 200129 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=3` | Hair loss |
| 57951 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who was the capital city of the Batavian Department that contained the territory of Southern Holland up to the Meuse and Southwestern Utrecht? |
| 38657800 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who is the developer of the Pixel Launcher? |
| 2056103 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who won the Tamil Nadu State Film Award for Best Actor in 1970 for the film Kaaviya Thalaivi? |
| 441357 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | Who is the person associated with the creation of the Osmanya script used for writing the Somali language? |
| 479109 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any person names; it only lists program types and their ranks, so no valid Person answer can be derived.` | Southern Methodist University |
| 356375 | `route_generation` | `wikipedia_infobox_llm_discarded:No person-type answer available in the top three tables; tables contain only phonetic symbols, no persons.` | Yoruba language |
| 241717 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=2` | Clinical trial |
| 52374650 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | King |
| 86224 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which person was the president of the International Olympic Committee during the 1928 Summer Olympics? |
| 221478 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who starred as Arnold in the 1982 Broadway production of Torch Song Trilogy? |
| 167051 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Who directed the 1960 film in which Connie Francis played the role of Angie? |
| 20804 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | Who was the mayor of Magdeburg according to the infobox? |
| 22304 | `route_generation` | `wikipedia_infobox_llm_discarded:No person names are present in the top-ranked table to form a valid single_fact question with a Person answer type.` | Osmium |
| 45367389 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | Which city in the Île-de-France region is a twin city of Greater London? |
| 105908 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=10` | Ford Mustang |
| 66958 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which country is the renminbi the official currency? |
| 41853326 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | From which club did Inter Miami CF acquire the player Lionel Messi as a Designated Player? |
| 12186 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=10` | Guinea-Bissau |
| 5643 | `route_generation` | `wikipedia_infobox_llm_discarded:No suitable factual place-based data available in the top-ranked table to generate a single-answer question.` | Channel Islands |
| 19653842 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:example` | Which place is the example organism classified as a superorganism in Queller and Strassmann's view of organisms at differing levels of biological organisation? |
| 34411 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which constellation has the brightest star named Regulus according to the 1977 IAU boundaries? |
| 217231 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which region was the DVD for Season 3 of Curb Your Enthusiasm released on February 7, 2005? |
| 55440889 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=g` | Pixel 2 |
| 84952 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which boxer succeeded Marvelous Marvin Hagler as the WBC middleweight champion? |
| 33094374 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Telecommunications |
| 22948 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which place is the mother of the offspring named Antaeus according to the earliest source Apollodorus? |
| 2924002 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which place is the annual DJ Awards event, known for nominating and awarding international DJs in 11 categories, held? |
| 30292 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In the quest structure of The Hobbit, where does the journey start? |
| 91195 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which place is the Wimbledon Championships tennis tournament annually held? |
| 235959 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which location was the play 'Butterflies are Free' starring Farrah Fawcett staged? |
| 260996 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | At which venue did Christian Slater perform the role of Tom Wingfield in 2005? |
| 342334 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:present` | Autopsy |
| 105391 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:active` | B movie |
| 68761 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Publishing |
| 229275 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=kt` | Lamb and mutton |
| 246920 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million,billion` | Visa Inc. |
| 2114995 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=15` | Dextromethorphan |
| 1625048 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km2` | Kingdom of Bohemia |
| 96875 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | Which city was the Great Western Railway originally intended to connect Bristol to by joining the London and Birmingham Railway near it? |
| 17278765 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which city was the 1931 Rose Bowl game played where No. 2 USC defeated No. 1 Tulane? |
| 7549995 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=18` | Elk |
| 151451 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | In which location was the documentary titled 'Orange Rockcorps at the Royal Albert Hall' filmed? |
| 156745 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | At which awards ceremony did Julia Roberts win Best Actress in a Motion Picture – Musical or Comedy for Pretty Woman? |
| 599 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which Afroasiatic language branch is the numeral for 'seven' represented as 'sabʕa' in the masculine form? |
| 43088 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which city did Yogi Berra's team lose the World Series in 1964 as a manager? |
| 26457880 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=tonnes` | Air India |
| 31730 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=16` | British Armed Forces |
| 47864412 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | Which place is represented by the bilabial nasal consonant phoneme in the Nepali language? |
| 18947898 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the country of origin of the Amnesty International Secretary General who served from 1992 to 2001? |
| 57877 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ml,g,m` | Sodium hydroxide |
| 407239 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | The Indian Express |
| 32005912 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Grimes |
| 214179 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which city was the American industrial metal band Ministry founded in 1981? |
| 15049 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | In which city did the Indianapolis Colts' Ring of Honor inductee Robert Irsay serve as owner from 1972 to 1997? |
| 80482 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | During Beatrix of the Netherlands' reign, which polity had Henny Eman serving as Prime Minister starting in 1986? |
| 35412202 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | Before the introduction of Wikidata, where were the interlanguage links for a Wikipedia article listed as they appeared in an edit box and on the article's page? |
| 57659 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which stadium is shared by both Club Africain and Espérance Sportive de Tunis according to the sports clubs table in Tunis? |
| 1064 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which order is the almond tree classified according to its scientific classification? |
| 2209490 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ha,g` | Romanization of Arabic |
| 422038 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,metres,millimetres,m` | Vigo |
| 23906 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=39` | Peterborough |
| 67923 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | East Sussex |
| 1161220 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Khushbu Sundar |
| 113933 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Iowa City, Iowa |
| 22461 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Osteoporosis |
| 47498 | `route_generation` | `wikipedia_infobox_llm_discarded:No suitable place-type factual data available in the top-ranked table to form a single-answer question.` | All your base are belong to us |
| 129619 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | At which awards ceremony did Whoopi Goldberg win Best Supporting Actress for her role in the film Ghost? |
| 540317 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which terrain mode is the default start selection in the Ford Explorer's Terrain Management System? |
| 261671 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=m` | 1989 Loma Prieta earthquake |
| 250230 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,kg,kw,lb` | Mazda RX-7 |
| 15240 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:unknown` | Imam |
| 67436 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=18` | Pseudoephedrine |
| 2056103 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | In which Indian state was the Tamil Nadu State Film Award for Best Actor won by Gemini Ganesan for the film Kaaviya Thalaivi in 1970? |
| 695780 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which country is the Nastro d'Argento award, won by Dante Ferretti for Best Production Design for the film Casino, presented? |
| 200129 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=3` | Hair loss |
| 57951 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which modern territory corresponds mostly to the French Department of the Mouths of the Meuse? |
| 20804 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | Which district of Magdeburg includes the former municipality of Beyendorf-Sohlen? |
| 221478 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | At which venue did Harvey Fierstein's play 'Casa Valentina' premiere on Broadway? |
| 356375 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In the Yoruba language vowel system, which place of articulation corresponds to the nasal vowel represented as ũ? |
| 241717 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=2` | Clinical trial |
| 52374650 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | King |
| 441357 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In which place is the Somali language primarily spoken as a mother tongue? |
| 479109 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In which place is the university located that has a graduate Business program ranked 34th by USNWR? |
| 22304 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any place or location information for osmium compounds, so no valid single_fact Place question can be generated.` | Osmium |
| 86224 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which country ranked second in the medal count at the 1928 Summer Olympics? |
| 167051 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which place was the director Raoul Walsh, who directed the 1958 film featuring Connie Francis as the singing voice of Miss Kate, primarily active? |
| 1069583 | `rewrite_surface` | `rewrite_guard_rejected:not_simple_question` | Which place is symbolized by the natural teacher that is steadfastly productive, gets abused, heals, and is steady in giving nourishment according to the 24 teachers from nature in Dattatreya's teachings? |
| 683599 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | At which venue did Hedley Verity achieve his best bowling figures of 10 wickets for 10 runs in a County Championship innings in 1932? |
| 1787105 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In animal mating systems, which system involves a single male mating with multiple females? |
| 32551521 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which dependency is associated with the legal nationality of Denmark according to FIFA eligibility rules? |
| 180763 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | According to the THE Subject Ranking 2024, in which country is the university ranked 4th nationally for Life sciences? |
| 4595410 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=153` | 1970 United States census |
| 56668 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which order is the apricot classified according to its scientific classification? |
| 83316 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which country did Ray Davies' 2010 studio album 'See My Friends' reach its highest peak chart position? |
| 333199 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which airline alliance did Continental Airlines join after exiting SkyTeam in October 2009? |
| 107825 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=miles` | Newport Beach, California |
| 1146123 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | In which city was the San Diego Film Festival held where Colin Hanks won the Soaring Star Award in 2005? |
| 61795854 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | All India Institutes of Medical Sciences |
| 31940 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which location was the United Nations Convention on the Law of the Sea signed? |
| 226734 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | Which Nigerian state was created in 1996 from the East Central region and is listed in the 1996 column of the chronology table? |
| 16801 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In which country was the self-defense system Krav Maga developed for the military forces? |
| 342334 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:present` | Autopsy |
| 105391 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:active` | B movie |
| 68761 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Publishing |
| 229275 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=kt` | Lamb and mutton |
| 246920 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million,billion` | Visa Inc. |
| 2114995 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=15` | Dextromethorphan |
| 1625048 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km2` | Kingdom of Bohemia |
| 569459 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | What is the geographic range of the white-tailed deer subspecies listed in the South America range map? |
| 17278765 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | Which trophy was awarded in the 1931 Rose Bowl that served as a title game for the Albert Russel Erskine Trophy and the Dickinson System's Knute Rockne Memorial Trophy? |
| 96875 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the long title of the Act of Parliament that authorized the construction of the Great Western Railway? |
| 7549995 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=18` | Elk |
| 599 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In the Afroasiatic numeral system table, which language branch uses the term 'wāḥid' for the masculine form of the numeral one? |
| 43088 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which team did Yogi Berra manage when he lost the World Series to the Oakland Athletics? |
| 151451 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What role did Busta Rhymes voice in the 1998 film The Rugrats Movie? |
| 26457880 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=tonnes` | Air India |
| 31730 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=16` | British Armed Forces |
| 156745 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which song won the BMI Film & TV Award for Most Performed Song from a Film related to Pretty Woman? |
| 18947898 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which country is the origin of the Amnesty International Secretary General who served from 1992 to 2001? |
| 57877 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ml,g,m` | Sodium hydroxide |
| 32005912 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Grimes |
| 407239 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | The Indian Express |
| 57659 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which stadium is shared by both Club Africain and Espérance Sportive de Tunis? |
| 80482 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which award did Beatrix of the Netherlands receive in 1996? |
| 15049 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | Which position did Dallas Clark hold when he was inducted into the Indianapolis Colts Ring of Honor? |
| 76988 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which time-frequency analysis method in ECG signal processing is suitable for fully non-stationary and nonlinear signals and provides instantaneous frequency distribution? |
| 35412202 | `rewrite_surface` | `rewrite_guard_rejected:forbidden_temporal_phrase` | What link currently allows readers to edit interlanguage and interwiki links centralized by Wikidata? |
| 1064 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the subgenus classification of the almond tree? |
| 2209490 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ha,g` | Romanization of Arabic |
| 422038 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,metres,millimetres,m` | Vigo |
| 23906 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=39` | Peterborough |
| 67923 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | East Sussex |
| 1161220 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Khushbu Sundar |
| 113933 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Iowa City, Iowa |
| 22461 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Osteoporosis |
| 129619 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | Which award did Whoopi Goldberg win for her role in the film that is listed under the Academy Awards category? |
| 540317 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the default start selection mode in the Ford Explorer's Terrain Management System? |
| 250230 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,kg,kw,lb` | Mazda RX-7 |
| 261671 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=m` | 1989 Loma Prieta earthquake |
| 15240 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:unknown` | Imam |
| 67436 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=18` | Pseudoephedrine |
| 695780 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which recipient won the 20/20 Awards for Best Film Editing for the film Casino (1995)? |
| 57951 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the French name of the department that mostly corresponds to the modern territory of Zeeland? |
| 200129 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=3` | Hair loss |
| 2056103 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | Which award did Gemini Ganesan win for his performance in the film Kaaviya Thalaivi? |
| 7549995 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=18` | Elk |
| 599 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many different Afroasiatic language branches are represented in the numeral table for the number 'Seven' in masculine form? |
| 43088 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many regular season games did Yogi Berra manage for the New York Yankees in 1964? |
| 26457880 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=tonnes` | Air India |
| 31730 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=16` | British Armed Forces |
| 47864412 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | How many distinct Nepali consonant phonemes are listed in the table under the 'Consonants' section? |
| 57905 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many time zones does the Sakha Republic span? |
| 18947898 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many years did Martin Ennals serve as Secretary General of Amnesty International? |
| 57877 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ml,g,m` | Sodium hydroxide |
| 32005912 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Grimes |
| 407239 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | The Indian Express |
| 80482 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many sons did Beatrix of the Netherlands have? |
| 76988 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the maximum duration in milliseconds of the PR interval as measured on a standard ECG graph paper? |
| 1064 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | How many taxonomic clades are listed in the scientific classification of the almond in the infobox? |
| 35412202 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | How many item statements did Wikidata have as of early 2025? |
| 15049 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many years did Peyton Manning play for the Indianapolis Colts according to the Ring of Honor table? |
| 2209490 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ha,g` | Romanization of Arabic |
| 422038 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,metres,millimetres,m` | Vigo |
| 23906 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=39` | Peterborough |
| 67923 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | East Sussex |
| 1161220 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Khushbu Sundar |
| 113933 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Iowa City, Iowa |
| 22461 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Osteoporosis |
| 47498 | `route_generation` | `wikipedia_infobox_llm_discarded:No numeric data available in the top-ranked table to form a valid single numeric answer question.` | All your base are belong to us |
| 129619 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many Academy Awards did the film Ghost win? |
| 250230 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,kg,kw,lb` | Mazda RX-7 |
| 261671 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=m` | 1989 Loma Prieta earthquake |
| 15240 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:unknown` | Imam |
| 67436 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=18` | Pseudoephedrine |
| 2056103 | `route_generation` | `wikipedia_infobox_answer_type_not_allowed:answer_type_not_allowed:Number; allowed=Number` | In which year did Gemini Ganesan win the Tamil Nadu State Film Award for Best Actor? |
| 18938412 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | How many songs by Richard Marx won the 'Most Performed Songs' award according to the listed awards and nominations? |
| 200129 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=3` | Hair loss |
| 38657800 | `rewrite_surface` | `rewrite_guard_rejected:cutoff_year_exceeded` | How many months ago was the latest release of Pixel Launcher as of January 3, 2025? |
| 57951 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many departments were there in the Batavian Republic reorganization of the Netherlands from 1798 to 1801? |
| 695780 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | How many total nominations did Sharon Stone receive for Best Actress or equivalent categories for the 1995 film Casino? |
| 221478 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | How many different venues hosted the Broadway productions of Harvey Fierstein's written works listed in the writing table? |
| 441357 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | How many numbers are listed in the Somali language numbers table from eleven to twenty? |
| 356375 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | How many oral vowel sounds are listed in the Yoruba language vowel table? |
| 241717 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=2` | Clinical trial |
| 52374650 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | King |
| 167051 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | How many films listed in Connie Francis's filmography were released before 1960? |
| 22304 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | What is the highest positive oxidation state of osmium listed in its chemical properties table? |
| 86224 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many gold medals did the United States win at the 1928 Summer Olympics? |
| 479109 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What was the USNWR graduate school ranking of the Business program at Southern Methodist University? |
| 20804 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | How many Stadtteile (districts) is the city of Magdeburg divided into? |
| 57877 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ml,g,m` | Sodium hydroxide |
| 32005912 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Grimes |
| 407239 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | The Indian Express |
| 214179 | `rewrite_surface` | `rewrite_guard_rejected:forbidden_temporal_phrase` | In what year did former Ministry band member William "Bill" Rieflin die? |
| 15049 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year was Tony Dungy inducted into the Indianapolis Colts Ring of Honor? |
| 57659 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the football club Espérance Sportive de Tunis founded? |
| 80482 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Mark Rutte begin his term as Prime Minister of the Netherlands during Beatrix's reign? |
| 76988 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the duration range in milliseconds of the PR interval as measured on a standard ECG? |
| 35412202 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year was the initial rollout of Wikidata's centralized interlanguage links feature implemented? |
| 2209490 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ha,g` | Romanization of Arabic |
| 422038 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,metres,millimetres,m` | Vigo |
| 23906 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=39` | Peterborough |
| 67923 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | East Sussex |
| 1161220 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Khushbu Sundar |
| 113933 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Iowa City, Iowa |
| 22461 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Osteoporosis |
| 47498 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the video game Zero Wing, which features the phrase 'All your base are belong to us,' originally released in Japanese arcades? |
| 129619 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the film Ghost win the Academy Award for Best Supporting Actress? |
| 540317 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what model years did the Ford Explorer receive a 'Marginal' rating for the small overlap frontal offset (driver side) according to NHTSA scores? |
| 261671 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=m` | 1989 Loma Prieta earthquake |
| 250230 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,kg,kw,lb` | Mazda RX-7 |
| 15240 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:unknown` | Imam |
| 67436 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=18` | Pseudoephedrine |
| 57951 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the Netherlands become fully part of France, leading to the establishment of French departments with borders largely maintained? |
| 695780 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the film Casino win the Golden Globe Award for Best Actress in a Motion Picture – Drama? |
| 200129 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=3` | Hair loss |
| 2056103 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Gemini Ganesan receive the Padma Shri award? |
| 38657800 | `rewrite_surface` | `rewrite_guard_rejected:forbidden_temporal_phrase` | On what date was the latest release of the Pixel Launcher, Android 16, made available? |
| 221478 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Harvey Fierstein's play 'Torch Song Trilogy' premiere at the Little Theatre on Broadway? |
| 356375 | `route_generation` | `wikipedia_infobox_llm_discarded:No date or year information is present in the top-ranked tables to form a valid Date-type question.` | Yoruba language |
| 241717 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=2` | Clinical trial |
| 52374650 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | King |
| 479109 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What was the USNWR graduate school ranking of Southern Methodist University's Business program? |
| 22304 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | What is the highest oxidation state of osmium listed in the chemical properties table? |
| 86224 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year were the Summer Olympics held in Amsterdam where the United States ranked first in the medal count? |
| 167051 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the film 'Where the Boys Are', in which Connie Francis played the role of Angie, released? |
| 20804 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year was the city of Magdeburg divided into its 40 Stadtteile (districts)? |
| 180763 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | In what year was the ARWU Subject Ranking that listed the University of Göttingen's ranking in Agricultural Sciences as 14 globally and 1 nationally published? |
| 1069583 | `rewrite_surface` | `rewrite_guard_rejected:not_simple_question` | In the legend of Dattatreya's 24 teachers from nature, which natural element is observed to wax and wane but whose oneness does not change, symbolizing the continuous eternal reality of the soul's birth, death, and rebirth cycle? |
| 32551521 | `rewrite_surface` | `rewrite_guard_rejected:not_simple_question` | In what year was Article 6.1 of the Regulations Governing the Applications of Statutes, which allows players to represent another FIFA member association after five years residency if they share the same legal nationality, established? |
| 683599 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Hedley Verity achieve the best bowling in an innings with a total of 10/10 in the County Championship? |
| 4595410 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=153` | 1970 United States census |
| 104944 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was Charles XII of Sweden coronated? |
| 56668 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the apricot scientifically classified under the type species Prunus armeniaca L.? |
| 333199 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did Alitalia exit the SkyTeam airline alliance? |


