# Route 3 Streaming Wikipedia Page-ID Walkthrough - 2026-07-14

## Stats

- Run group ID: `route3_place50_fresh50_no_reuse_gemini3flashpreview_2026_07_14_193621`
- Run segment ID: `recipe_combined`
- Artifact manifest: ``
- Mode: `page_id_stream_recipe`
- Page source: `table-search`
- Table-search queries: `insource:"wikitable"`
- Attempted page IDs: 50
- Unique attempted page IDs: 50
- Stream state reset at run start: yes
- Auto rerun pool once: yes
- Auto-rerun attempted page IDs: 0
- Accepted QAs: 0
- Rejected QAs/pages: 50
- LLM generation table yield: 0.0% (0 accepted QAs / 23 input tables)
- Transient rerun attempts during run: 0
- Wall-clock runtime: 85.4689s
- DuckDuckGo top K: 5
- Generated search queries per QA: 2
- DuckDuckGo parallel queries: 3
- DuckDuckGo ddgs primary path: `enabled`, backend `auto`, attempts 2
- DuckDuckGo global cooldown: `enabled`, threshold 3, 60.0s to 300.0s
- Route 3 reasoning_type constraint: `single_fact`
- Route 3 answer_type constraint: `Place`
- Route 3 table filter modes: `no_external_links_tables, no_horizontal_companion_tables, no_picture_heavy_tables, no_incomplete_tables, not_number_dominant, no_social_science_research`
- Route 3 table source types: `infobox, wikitable`
- Route 3 prose-leakage scoring: `enabled`
- Route 3 LLM table choice: `disabled`
- Page-id bounds: None to None
- Stream state: `separate_segment_stream_states`
- Accepted output: `/home/chenyue/Wikidata_Framework_aws/outputs/route3_place50_fresh50_no_reuse_gemini3flashpreview_2026_07_14_193621_accepted.jsonl`
- Rejected output: `/home/chenyue/Wikidata_Framework_aws/outputs/route3_place50_fresh50_no_reuse_gemini3flashpreview_2026_07_14_193621_rejected.jsonl`
- Domain policy: `domain_and_subdomain_optional_for_page_id_streaming`
- Rerun pool after run: `empty`

### Recipe Segments

| Configured answer_type | Target | Attempted page IDs | Accepted | Rejected | Rerun |
| --- | ---: | ---: | ---: | ---: | ---: |
| Place | 50 | 50 | 0 | 50 | 0 |

### Survival By Layer

| Layer | Unit | Entered | Failed | Survived | Layer survival |
| --- | --- | ---: | ---: | ---: | ---: |
| Page-id reservation | page IDs | 50 | 0 | 50 | 100.0% |
| Unresolved or returned to rerun pool | page IDs | 50 | 0 | 50 | 100.0% |
| Source, pageview, and table filters before generation LLM | page IDs | 50 | 27 | 23 | 46.0% |
| Tables sent to generation LLM | tables | 23 | 0 | 23 | 100.0% |
| Generation LLM output and route-local checks | QA candidates/slots | 23 | 8 | 15 | 65.2% |
| Rewrite and surface validation | QA candidates/slots | 15 | 9 | 6 | 40.0% |
| Shared deterministic route-aware validation | QA candidates/slots | 6 | 0 | 6 | 100.0% |
| DuckDuckGo long-tail filtering | QA candidates/slots | 6 | 5 | 1 | 16.7% |
| Second-stage model grading | QA candidates/slots | 1 | 1 | 0 | 0.0% |
| Deduplication | QA candidates/slots | 0 | 0 | 0 | 0.0% |
| Other rejection | QA candidates/slots | 0 | 0 | 0 | 0.0% |

### Failure Reasons

| Stage | Reason | Count |
| --- | --- | ---: |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant` | 16 |
| `rewrite_surface` | `rule_based_answer_type_gate_rejected:place_question_category_whitelist` | 5 |
| `route_generation` | `wikipedia_infobox_no_tables` | 5 |
| `search_longtail` | `search_longtail_verifier_rejected` | 5 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | 3 |
| `rewrite_surface` | `answer_too_popular:United States` | 2 |
| `rewrite_surface` | `rewrite_guard_rejected:forbidden_temporal_phrase` | 2 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables` | 2 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table 'Japanese powderly green tea' contains information about tea processing methods, features, and consumption methods, but it does not contain any geographic entities, locations, or place names required for the 'Place' answer_type.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table contains abstract character alignment categories (e.g., 'Lawful good', 'Neutral evil') for a role-playing game. It does not contain any data related to geographic entities, locations, or places on Earth, making it impossible to generate a question with a 'Place' answer type.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table contains chemical oxidation states and formulas for chromium compounds. It does not contain any geographic entities, locations, or place names required for the 'Place' answer_type.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table contains compass directions (North, East, NEbN, etc.) and their corresponding azimuths. While these are directions, they do not qualify as 'Place' answer types (specific geographic entities on Earth like cities, countries, rivers, or mountains) as required by the prompt instructions. Therefore, no valid question can be generated within the 'Place' scope.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table contains statistical data regarding funding sources and study outcomes for Bisphenol A; it does not contain any geographic entities, locations, or place names required for the 'Place' answer_type.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table for 'Atrial fibrillation' does not contain any data points that are geographic entities or locations (Place answer_type). All values in the table refer to medical symptoms, specialties, complications, or diagnostic methods.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The required answer_type is 'Place' (geographic entity), but the source table only contains linguistic data (letters, phonemes, and positions). It is impossible to generate a 'Place' answer from this table.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The required answer_type is 'Place', but the only available data points in this table are names (People) and years (Time). No geographic locations or places are present in the provided table content.` | 1 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables` | 1 |
| `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded` | 1 |

### Answer Type Stats

| Scope | Answer type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `Place` | 0 | 15 | 15 | 0.0% |
| Current Run Records | `unknown` | 0 | 35 | 35 | 0.0% |

### Reasoning Type Stats

| Scope | Reasoning type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `single_fact` | 0 | 50 | 50 | 0.0% |

### Rerun Pool After Run

Rerun pool is empty.


### Phase Timings

Timing nesting: `wall_clock_seconds` is the whole run. `total_generation_seconds` contains page fetch/cache reuse, table parse, optional pageview prefilter, first-paragraph extraction, and generation LLM work for one page. `total_processing_seconds` contains rewrite/surface checks, number margin, shared validation, DuckDuckGo search, second-stage grading when enabled, and dedup checks for one generated candidate. `candidate_processing_seconds` is an alias of `total_processing_seconds`. Route-local output checks, shared validation, and dedup currently do not have standalone child timers. Generation/source timings are deduplicated by page or LLM prompt so all5 slots do not multiply shared work. Child phase totals are useful for bottlenecks, but they should not be added to parent totals.

| Pipeline order | Phase | Parent/child | Additive? | Meaning |
| ---: | --- | --- | --- | --- |
| 0 | `wall_clock_seconds` | run total | No | Elapsed time for the whole streaming command. |
| 1 | `page_fetch_seconds` | child of total_generation_seconds | Yes, within generation only | MediaWiki action=parse fetch for one page, or zero when a cached archive supplies the parse payload. |
| 2 | `table_parse_seconds` | child of total_generation_seconds | Yes, within generation only | Local table/prose parsing and table-ranking inputs for one page. |
| 3 | `pageview_prefilter_seconds` | child of total_generation_seconds | Yes, within generation only | Optional pageview popularity prefilter before table selection and generation LLM calls. |
| 4 | `first_paragraph_extract_seconds` | child of total_generation_seconds | Yes, within generation only | Local extraction of first paragraph from parse HTML after a table survives source filters. |
| 5 | `first_paragraph_fetch_seconds` | optional child of total_generation_seconds | Yes, within generation only | REST summary fallback when explicitly enabled and parse HTML lacks a paragraph. |
| 6 | `llm_question_generation_seconds` | child of total_generation_seconds | Yes, within generation only | Route 3 table-grounded QA generation LLM call. |
| 7 | `total_generation_seconds` | parent | No | Overall Route 3 generation time for one page. |
| 8 | `rewrite_seconds` | child of total_processing_seconds | Yes, within processing only | Shared rewrite call when enabled. |
| 9 | `number_reference_margin_seconds` | child of total_processing_seconds | Yes, within processing only | Numeric reference margin setup after rewrite/surface checks and before shared validation. |
| 10 | `duckduckgo_search_seconds` | child of total_processing_seconds | Yes, within processing only | DuckDuckGo long-tail queries and leakage scoring after shared deterministic validation. |
| 11 | `second_stage_grading_seconds` | optional child of total_processing_seconds | Yes, within processing only | Model-panel answerability grading when enabled. |
| 12 | `total_processing_seconds` | parent | No | Shared rewrite, surface checks, validation, search, grading, and dedup processing for one candidate. |
| 13 | `candidate_processing_seconds` | alias | No | Alias of total_processing_seconds for compatibility. |

#### Current Run Phase Timings

| Phase | Count | Total seconds | Average seconds | Max seconds |
| --- | ---: | ---: | ---: | ---: |
| `candidate_processing_seconds` | 50 | 41.8396 | 0.8368 | 15.6978 |
| `duckduckgo_search_seconds` | 6 | 40.2799 | 6.7133 | 15.6949 |
| `first_paragraph_extract_seconds` | 23 | 2.8516 | 0.1240 | 0.3781 |
| `llm_question_generation_seconds` | 23 | 48.1227 | 2.0923 | 2.9256 |
| `number_reference_margin_seconds` | 6 | 0.0000 | 0.0000 | 0.0000 |
| `page_fetch_seconds` | 50 | 0.0000 | 0.0000 | 0.0000 |
| `pageview_prefilter_seconds` | 50 | 0.0001 | 0.0000 | 0.0001 |
| `rewrite_seconds` | 15 | 0.0000 | 0.0000 | 0.0000 |
| `second_stage_grading_seconds` | 1 | 1.5202 | 1.5202 | 1.5202 |
| `table_parse_seconds` | 50 | 16.1031 | 0.3221 | 0.9425 |
| `total_generation_seconds` | 50 | 234.1787 | 4.6836 | 19.0596 |
| `total_processing_seconds` | 50 | 41.8396 | 0.8368 | 15.6978 |

## Accepted Candidates

No accepted candidates in this run.
## Second-Stage Filtering Responses

These are the small-model QA responses used by the second-stage filter: `openai/gpt-4.1-mini` and `google/gemini-3-flash-preview`.

| Page ID | Question | Reference answer | openai/gpt-4.1-mini | google/gemini-3-flash-preview |
| ---: | --- | --- | --- | --- |
| 186191 | According to the production history of the T-72 main battle tank, in which country did the vehicle originate? | Soviet Union | CORRECT; predicted_answer: The T-72 main battle tank originated in the Soviet Union. | not run |


## Rejected And Rerun Decisions

| Page ID | Table type | Answer type | Question | Answer | Source | Exact reason |
| ---: | --- | --- | --- | --- | --- | --- |
| 338344 | `unknown` | `unknown` | List of tallest buildings |  | https://en.wikipedia.org/wiki/List_of_tallest_buildings | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` |
| 31843 | `unknown` | `unknown` | Uruguay |  | https://en.wikipedia.org/wiki/Uruguay | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km,mi` |
| 5489 | `unknown` | `unknown` | Chile |  | https://en.wikipedia.org/wiki/Chile | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km` |
| 803 | `unknown` | `unknown` | Arabic |  | https://en.wikipedia.org/wiki/Arabic | `wikipedia_infobox_llm_discarded:The required answer_type is 'Place' (geographic entity), but the source table only contains linguistic data (letters, phonemes, and positions). It is impossible to generate a 'Place' answer from this table.` |
| 26989 | `unknown` | `unknown` | Sony |  | https://en.wikipedia.org/wiki/Sony | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=1` |
| 16949861 | `unknown` | `unknown` | Mississippi |  | https://en.wikipedia.org/wiki/Mississippi | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=1` |
| 39776 | `unknown` | `unknown` | Denial-of-service attack |  | https://en.wikipedia.org/wiki/Denial-of-service_attack | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=2` |
| 17766232 | `wikitable` | `Place` | In which city was the 1982 Eurovision Song Contest held when the United Kingdom hosted the event? | Harrogate | https://en.wikipedia.org/wiki/United_Kingdom_in_the_Eurovision_Song_Contest | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` |
| 1486684 | `wikitable` | `Place` | In which city was the professional ice hockey team that lost the 1924 Stanley Cup finals based? | Calgary | https://en.wikipedia.org/wiki/List_of_Stanley_Cup_champions | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` |
| 728776 | `infobox` | `Place` | According to his biographical records, in what Swedish city was the professional footballer Zlatan Ibrahimović born? | Malmö | https://en.wikipedia.org/wiki/Zlatan_Ibrahimović | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` |
| 276447 | `unknown` | `unknown` | Fortune 500 |  | https://en.wikipedia.org/wiki/Fortune_500 | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=20` |
| 132101 | `unknown` | `unknown` | Norrbotten County |  | https://en.wikipedia.org/wiki/Norrbotten_County | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=16` |
| 407239 | `infobox` | `Place` | In which specific sector of Noida is the headquarters of the newspaper The Indian Express located? | Sector 10 | https://en.wikipedia.org/wiki/The_Indian_Express | `rule_based_answer_type_gate_rejected:place_question_category_whitelist` |
| 339183 | `wikitable` | `Place` | In the traditional Chinese 24-point compass system, which cardinal or ordinal direction is represented by the point known as xùn? | southeast | https://en.wikipedia.org/wiki/Points_of_the_compass | `rule_based_answer_type_gate_rejected:place_question_category_whitelist` |
| 18952765 | `unknown` | `unknown` | Succulent plant |  | https://en.wikipedia.org/wiki/Succulent_plant | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:citation needed` |
| 4558294 | `infobox` | `Place` | According to the film's production credits, in which country was the 1980 musical action comedy The Blues Brothers produced? | United States | https://en.wikipedia.org/wiki/The_Blues_Brothers_(film) | `answer_too_popular:United States` |
| 3314970 | `unknown` | `unknown` | List of members of the AVN Hall of Fame |  | https://en.wikipedia.org/wiki/List_of_members_of_the_AVN_Hall_of_Fame | `wikipedia_infobox_llm_discarded:The required answer_type is 'Place', but the only available data points in this table are names (People) and years (Time). No geographic locations or places are present in the provided table content.` |
| 5669 | `unknown` | `unknown` | Chromium |  | https://en.wikipedia.org/wiki/Chromium | `wikipedia_infobox_llm_discarded:The provided table contains chemical oxidation states and formulas for chromium compounds. It does not contain any geographic entities, locations, or place names required for the 'Place' answer_type.` |
| 150473 | `unknown` | `unknown` | Shreveport, Louisiana |  | https://en.wikipedia.org/wiki/Shreveport,_Louisiana | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=18` |
| 25480 | `wikitable` | `Place` | In the 1989 International Race of Champions season, at which racing circuit did Richard Petty finish in 12th place during the second race of the series? | Nazareth Speedway | https://en.wikipedia.org/wiki/Richard_Petty | `rule_based_answer_type_gate_rejected:place_question_category_whitelist` |
| 26197 | `unknown` | `unknown` | Radiocarbon dating |  | https://en.wikipedia.org/wiki/Radiocarbon_dating | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=thousand` |
| 601399 | `unknown` | `unknown` | Display resolution |  | https://en.wikipedia.org/wiki/Display_resolution | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=45` |
| 48586 | `unknown` | `unknown` | Pulitzer Prize for Fiction |  | https://en.wikipedia.org/wiki/Pulitzer_Prize_for_Fiction | `wikipedia_infobox_no_tables` |
| 195468 | `unknown` | `unknown` | Ring of Fire |  | https://en.wikipedia.org/wiki/Ring_of_Fire | `wikipedia_infobox_no_tables` |
| 236850 | `unknown` | `unknown` | Conflict of interest |  | https://en.wikipedia.org/wiki/Conflict_of_interest | `wikipedia_infobox_llm_discarded:The provided table contains statistical data regarding funding sources and study outcomes for Bisphenol A; it does not contain any geographic entities, locations, or place names required for the 'Place' answer_type.` |
| 904826 | `unknown` | `unknown` | Alignment (Dungeons & Dragons) |  | https://en.wikipedia.org/wiki/Alignment_(Dungeons_&_Dragons) | `wikipedia_infobox_llm_discarded:The provided table contains abstract character alignment categories (e.g., 'Lawful good', 'Neutral evil') for a role-playing game. It does not contain any data related to geographic entities, locations, or places on Earth, making it impossible to generate a question with a 'Place' answer type.` |
| 200085 | `unknown` | `unknown` | Cardinal direction |  | https://en.wikipedia.org/wiki/Cardinal_direction | `wikipedia_infobox_llm_discarded:The provided table contains compass directions (North, East, NEbN, etc.) and their corresponding azimuths. While these are directions, they do not qualify as 'Place' answer types (specific geographic entities on Earth like cities, countries, rivers, or mountains) as required by the prompt instructions. Therefore, no valid question can be generated within the 'Place' scope.` |
| 23572499 | `unknown` | `unknown` | Matcha |  | https://en.wikipedia.org/wiki/Matcha | `wikipedia_infobox_llm_discarded:The provided table 'Japanese powderly green tea' contains information about tea processing methods, features, and consumption methods, but it does not contain any geographic entities, locations, or place names required for the 'Place' answer_type.` |
| 232894 | `infobox` | `Place` | To which ceremonial county does the town of Blackpool belong? | Lancashire | https://en.wikipedia.org/wiki/Blackpool | `search_longtail_verifier_rejected:full_question:answer_in_title` |
| 18600829 | `infobox` | `Place` | In which city did Jeff Gordon participate in his first NASCAR O'Reilly Auto Parts Series race, the 1990 AC-Delco 200? | Rockingham | https://en.wikipedia.org/wiki/Jeff_Gordon | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` |
| 11420440 | `unknown` | `unknown` | Sovereign wealth fund |  | https://en.wikipedia.org/wiki/Sovereign_wealth_fund | `wikipedia_infobox_no_tables` |
| 17627213 | `unknown` | `unknown` | List of music recording certifications |  | https://en.wikipedia.org/wiki/List_of_music_recording_certifications | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=7` |
| 313646 | `unknown` | `unknown` | Western Cape |  | https://en.wikipedia.org/wiki/Western_Cape | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=m` |
| 37284 | `infobox` | `Place` | According to the five-year survival rate statistics for brain tumors, in which country is the average survival rate recorded as 33%? | United States | https://en.wikipedia.org/wiki/Brain_tumor | `answer_too_popular:United States` |
| 164938 | `unknown` | `unknown` | Airbus A321 |  | https://en.wikipedia.org/wiki/Airbus_A321 | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,gal,km,lb,mi,mph,m` |
| 9603757 | `unknown` | `unknown` | SiriusXM |  | https://en.wikipedia.org/wiki/SiriusXM | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` |
| 1300 | `unknown` | `unknown` | Abalone |  | https://en.wikipedia.org/wiki/Abalone | `wikipedia_infobox_no_tables` |
| 462421 | `unknown` | `unknown` | Oxygen toxicity |  | https://en.wikipedia.org/wiki/Oxygen_toxicity | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` |
| 54761 | `wikitable` | `Place` | According to the distribution of Chinese surnames, which Chinese province or region has a high concentration of the surname Fú (符)? | Hainan | https://en.wikipedia.org/wiki/Chinese_surname | `rule_based_answer_type_gate_rejected:place_question_category_whitelist` |
| 186191 | `infobox` | `Place` | According to the production history of the T-72 main battle tank, in which country did the vehicle originate? | Soviet Union | https://en.wikipedia.org/wiki/T-72 | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` |
| 59733 | `unknown` | `unknown` | Hexagon |  | https://en.wikipedia.org/wiki/Hexagon | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=7` |
| 353891 | `unknown` | `unknown` | Full-time equivalent |  | https://en.wikipedia.org/wiki/Full-time_equivalent | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=5` |
| 879015 | `infobox` | `Place` | In which city in the United States was the actor and former White House staff member Kal Penn born? | Montclair | https://en.wikipedia.org/wiki/Kal_Penn | `rewrite_guard_rejected:forbidden_temporal_phrase` |
| 1963 | `unknown` | `unknown` | Absolute magnitude |  | https://en.wikipedia.org/wiki/Absolute_magnitude | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km,m` |
| 31039 | `unknown` | `unknown` | Turboprop |  | https://en.wikipedia.org/wiki/Turboprop | `wikipedia_infobox_no_tables` |
| 20869694 | `unknown` | `unknown` | Atrial fibrillation |  | https://en.wikipedia.org/wiki/Atrial_fibrillation | `wikipedia_infobox_llm_discarded:The provided table for 'Atrial fibrillation' does not contain any data points that are geographic entities or locations (Place answer_type). All values in the table refer to medical symptoms, specialties, complications, or diagnostic methods.` |
| 44914 | `wikitable` | `Place` | Which national park in the Indian state of Karnataka is separated from Bandipur National Park by the Kabini reservoir? | Nagarhole National Park | https://en.wikipedia.org/wiki/List_of_national_parks_of_India | `rule_based_answer_type_gate_rejected:place_question_category_whitelist` |
| 567809 | `unknown` | `unknown` | Goaltender |  | https://en.wikipedia.org/wiki/Goaltender | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=10` |
| 184378 | `unknown` | `unknown` | Vauxhall Motors |  | https://en.wikipedia.org/wiki/Vauxhall_Motors | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` |
| 1225381 | `infobox` | `Place` | In which city was the former NFL tight end Tony Gonzalez born? | Torrance | https://en.wikipedia.org/wiki/Tony_Gonzalez | `rewrite_guard_rejected:forbidden_temporal_phrase` |


