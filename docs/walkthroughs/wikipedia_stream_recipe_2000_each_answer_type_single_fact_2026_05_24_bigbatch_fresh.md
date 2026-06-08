# Route 3 Streaming Wikipedia Page-ID Walkthrough - 2026-05-25

## Stats

- Run group ID: `wikipedia_stream_recipe_2000_each_answer_type_single_fact_2026_05_24_bigbatch_fresh`
- Run segment ID: `recipe_combined`
- Artifact manifest: ``
- Mode: `page_id_stream_recipe`
- Page source: `table-search`
- Table-search queries: `insource:"wikitable"; insource:/\{\|/`
- Attempted page IDs: 1889
- Unique attempted page IDs: 1700
- Stream state reset at run start: yes
- Auto rerun pool once: yes
- Auto-rerun attempted page IDs: 0
- Accepted QAs: 88
- Rejected QAs/pages: 1520
- Transient rerun attempts during run: 281
- Wall-clock runtime: 7415.3935s
- DuckDuckGo top K: 5
- Generated search queries per QA: 3
- DuckDuckGo parallel queries: 3
- Route 3 reasoning_type constraint: `single_fact`
- Route 3 answer_type constraint: `Date`
- Route 3 table filter modes: `no_picture_heavy_tables, no_incomplete_tables, not_number_dominant, no_social_science_research`
- Route 3 LLM table choice: `disabled`
- Page-id bounds: None to None
- Stream state: `separate_segment_stream_states`
- Accepted output: `D:\Study\AI\My-research\Wikidata_Framework\outputs\wikipedia_stream_recipe_2000_each_answer_type_single_fact_2026_05_24_bigbatch_fresh_accepted.jsonl`
- Rejected output: `D:\Study\AI\My-research\Wikidata_Framework\outputs\wikipedia_stream_recipe_2000_each_answer_type_single_fact_2026_05_24_bigbatch_fresh_rejected.jsonl`
- Domain policy: `domain_and_subdomain_optional_for_page_id_streaming`
- Rerun pool after run: `8341, 26243, 42147, 53078, 76366, 83316, 140594, 143425, 150292, 176888, 181998, 223632, 233415, 249875, 253413, 255474, 271181, 296558, 333680, 384163, 426335, 462914, 472486, 509738, 522916, 595323, 615865, 656544, 659697, 689567, 712154, 757835, 870016, 900024, 939668, 966935, 1124684, 1124716, 1159215, 1160811, 1344011, 1371710, 1776674, 1781836, 1924548, 1964020, 1967693, 2152050, 2321132, 2380290, 2462149, 2496880, 2497333, 2583361, 3941629, 4056032, 4207096, 4278374, 4411216, 5885099, 6730560, 7958128, 9707508, 10433447, 10593104, 11557885, 12311469, 12907693, 13837592, 14302690, 14646325, 14768644, 16206708, 16561337, 17938013, 18494414, 18830712, 20647359, 26282330, 26444143, 26673818, 40566019, 41251289, 46965651, 47048173, 47574413, 47756506, 47804196, 50512917, 57645522, 59702217, 60637832`

### Recipe Segments

| Configured answer_type | Record limit | Attempted page IDs | Accepted | Rejected | Rerun |
| --- | ---: | ---: | ---: | ---: | ---: |
| Date | 1700 | 1889 | 88 | 1520 | 281 |

### Survival By Layer

| Layer | Entered | Failed | Survived | Layer survival | Cumulative survival |
| --- | ---: | ---: | ---: | ---: | ---: |
| Page-id reservation | 1889 | 0 | 1889 | 100.0% | 100.0% |
| Unresolved or returned to rerun pool | 1889 | 0 | 1889 | 100.0% | 100.0% |
| Page extraction, table grading, and QA generation | 1889 | 1041 | 848 | 44.9% | 44.9% |
| Rewrite and surface validation | 848 | 39 | 809 | 95.4% | 42.8% |
| DuckDuckGo long-tail filtering | 809 | 61 | 748 | 92.5% | 39.6% |
| Second-stage model grading | 748 | 333 | 415 | 55.5% | 22.0% |
| Shared route-aware validation | 415 | 46 | 369 | 88.9% | 19.5% |
| Deduplication | 369 | 0 | 369 | 100.0% | 19.5% |
| Other rejection | 369 | 0 | 369 | 100.0% | 19.5% |

### Failure Reasons

| Stage | Reason | Count |
| --- | --- | ---: |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant` | 488 |
| `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded` | 333 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables` | 140 |
| `route_generation` | `wikipedia_infobox_no_tables` | 66 |
| `search_longtail` | `search_longtail_verifier_rejected` | 61 |
| `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | 46 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables` | 45 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | 32 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a valid Date answer type question.` | 22 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | 21 |
| `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | 12 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | 12 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date answer type question.` | 11 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:present` | 9 |
| `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | 7 |
| `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:list` | 5 |
| `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:table` | 5 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information or usable data to generate a Date-type question.` | 5 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information, so it cannot support a Date answer type question.` | 5 |
| `rewrite_surface` | `rewrite_guard_rejected:forbidden_temporal_phrase` | 4 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:active` | 4 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information to form a valid Date answer type question.` | 4 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to support a Date answer type question.` | 4 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information, so no valid Date answer type question can be generated.` | 4 |
| `route_generation` | `wikipedia_infobox_table_filter_rejected:no_social_science_research` | 4 |
| `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_time_invariance_forbidden_phrase:recent` | 3 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:incumbent` | 3 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:latest` | 3 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No date or temporal values present in the table to form a Date answer type question.` | 3 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information or any data suitable for generating a Date answer type question.` | 3 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information or any factual data suitable for generating a Date-type question.` | 3 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information to form a Date-type question.` | 3 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information to support a Date answer type question.` | 3 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or temporal information to form a Date-type question.` | 3 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information, so it cannot support a question with a Date answer type.` | 3 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date, year, or month information to form a valid Date answer type question.` | 3 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table only contains color codes and their corresponding race result categories, none of which are dates. Therefore, no valid Date-type question can be generated from this table.` | 3 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information to support a Date answer type question.` | 3 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information, so no valid Date answer question can be generated.` | 3 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information, so no valid Date-type question can be generated.` | 3 |
| `route_generation` | `wikipedia_infobox_table_score_below_minimum:table_score_below_minimum:min_table_score=0.0000;best_score=-0.1000` | 3 |
| `route_generation` | `wikipedia_infobox_table_score_below_minimum:table_score_below_minimum:min_table_score=0.0000;best_score=-2.0000` | 3 |
| `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_time_invariance_forbidden_phrase:current` | 2 |
| `route_generation` | `wikipedia_infobox_generation_error:IncompleteRead:IncompleteRead(77 bytes read)` | 2 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:caption:current` | 2 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:present` | 2 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No date-type answers available in the provided table.` | 2 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table contains phonetic consonant data without any date or temporal information, so it cannot support a Date answer type question.` | 2 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information or any factual data suitable for generating a Date answer type question.` | 2 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information to form a valid Date-type question.` | 2 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information, so no valid Date-type question can be generated.` | 2 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date information to support a Date answer type question.` | 2 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or temporal data to form a Date-type question.` | 2 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information; no suitable Date answer type question can be generated.` | 2 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information; therefore, no valid Date answer question can be generated.` | 2 |
| `route_generation` | `wikipedia_infobox_table_score_below_minimum:table_score_below_minimum:min_table_score=0.0000;best_score=-0.4000` | 2 |
| `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:in_the_table` | 1 |
| `route_generation` | `wikipedia_infobox_generation_error:IncompleteRead:IncompleteRead(11 bytes read)` | 1 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:caption:latest` | 1 |
| `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:caption:present` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No date information is present in the provided table or nearby text to support a Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No date information is present in the provided table to support a Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No date or temporal data available in the provided table to generate a Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No date or temporal data available in the table to generate a Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No date or year information available in the provided table to generate a Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No date or year information available in the table to form a Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No date or year information available in the table to form a valid Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No date or year information is present in the table to support a Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No date or year information is provided in the table to support a Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No date or year values present in the table to generate a Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No date-type answer available in the table to form a valid question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No date-type answers available in the table to form a valid Date answer_type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No date-type answers available in the table to form a valid question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:No date-type answers available in the table to generate a Date answer_type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The answer is a numeric count, not a date, so it does not match the required Date answer type.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The answer is a term length, not a specific date or year, so it does not meet the Date answer type requirement.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The answer is not a date, month, or year, which is required by the prompt for answer_type Date.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The answer type is not a Date, so the question is discarded.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The answer type is not a date but a parity change indicator, so it does not meet the required Date answer type.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table 'Out on loan' contains only header row and no data rows, thus it does not support generating a factual question with a Date answer type.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table 'Out on loan' contains only headers and no data rows, so it does not support generating a factual question with a Date answer type.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table 'Slovene vowels' does not contain any date or year information, so it cannot support a Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table and text do not contain any date or year information; thus, no valid Date answer question can be generated.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table contains only a legend with no factual date information to generate a Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table contains only consonant phonemes and no date or temporal information, so no valid Date-type question can be generated.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table contains only staff positions and names without any date or temporal information, so no valid Date-type question can be generated.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table contains personal pronouns and does not include any date or temporal information to form a Date-type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table contains phoneme data without any date or temporal information, so it cannot support a Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table contains phonological consonant data without any date or temporal information, so it cannot support a Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information or any factual data that can be answered with a date; it only contains a note about a symbol without any date values.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information or data that can be answered with a Date type. It only contains a legend explaining symbols related to wins per year without actual year or date data.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information or factual data suitable for generating a Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information or factual data suitable for generating a Date-type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information or usable data to generate a factual date question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information related to the city council members or their appointments.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information suitable for forming a Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information suitable for forming a Date-type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information to generate a Date-type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information, so a date answer cannot be derived from it.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information; it only contains a key for player status and positions, so no valid Date-type question can be generated.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information; it only contains a legend for NFL career achievements without any date values.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information; no date-type factual question can be generated.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information; therefore, no valid Date-type question can be generated.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or temporal information to form a valid Date-type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information for Unicode characters, so no valid Date answer question can be generated.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information related to the decorations and awards, so no valid Date answer question can be generated.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to answer a Date type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information, only phonetic vowel data, which is not suitable for a Date answer type.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information, only terminology related to the number of columns at the front of ancient Greek temples. Therefore, it cannot support a factual question with a Date answer type.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information; it only contains legend explanations without factual data suitable for a Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information; it only lists administrative divisions and their names in Chinese and Pinyin, which cannot support a Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information; it only lists categories of tournament results without dates.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information; it only lists instruction mnemonics and their descriptions, so no Date answer type question can be generated.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information; therefore, no valid Date-type question can be generated.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date values or date-related data to form a valid Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date, month, or year values to form a valid Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date, year, or month information to form a Date-type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date, year, or month information; it only lists Vedas, recensions, shakhas, and principal Upanishads without any temporal data.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any specific date information or factual data suitable for generating a Date-type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table is a key/legend for Grand Slam performance timelines and does not contain any date values or factual data with date answers. Therefore, no valid Date-type question can be generated from this table.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table lists districts and neighbourhoods of Plovdiv without any date or temporal information, so it cannot support a Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table only contains a color key with symbols and descriptions, without any date information to support a Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table only contains a key for abbreviations without any actual date data, so it cannot support a Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table only contains a key for abbreviations without any date values or factual data to form a date answer question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table only contains a legend with no factual date information; it does not support generating a Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table only contains star spectral type categories without any date information, so no valid Date-type question can be generated.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The provided table only contains symbols and their meanings, not any date information; therefore, no valid Date-type question can be generated.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date information about the officials' election or term start dates.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date information for the awards, so no valid Date answer can be extracted.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date information related to the classification or any other date facts; thus no valid Date answer question can be generated.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date information to form a Date-type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date information; no Date answer type question can be generated.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date information; no date-type factual question can be generated from it.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date information; no date-type factual question can be generated.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or temporal data to form a Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or temporal information to support a Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information for any brand, so no valid Date answer question can be generated.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information for awards or nominations, only counts, so it cannot support a Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information related to the seat counts, so no valid Date answer question can be generated.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information to answer a Date type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information to form a valid Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information; no Date answer type question can be generated.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information; therefore, no valid Date answer type question can be generated.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information; therefore, no valid Date-type question can be generated.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information; thus, no valid Date answer question can be generated.` | 1 |
| `route_generation` | `wikipedia_infobox_llm_discarded:The table is empty and does not contain any date information to support a Date answer type question.` | 1 |
| `route_generation` | `wikipedia_infobox_table_score_below_minimum:table_score_below_minimum:min_table_score=0.0000;best_score=-0.2500` | 1 |
| `route_generation` | `wikipedia_infobox_table_score_below_minimum:table_score_below_minimum:min_table_score=0.0000;best_score=-0.5500` | 1 |

### Answer Type Stats

| Scope | Answer type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `Date` | 88 | 0 | 88 | 100.0% |
| Current Run Records | `unknown` | 0 | 1520 | 1520 | 0.0% |

### Reasoning Type Stats

| Scope | Reasoning type | Accepted | Rejected | Total | Accepted rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Current Run Records | `unknown` | 88 | 1520 | 1608 | 5.5% |

### Rerun Pool After Run

| Page ID | Exact reason |
| ---: | --- |
| 8341 | `search_longtail_verifier_error` |
| 26243 | `search_longtail_verifier_error` |
| 42147 | `search_longtail_verifier_error` |
| 53078 | `search_longtail_verifier_error` |
| 76366 | `search_longtail_verifier_error` |
| 83316 | `search_longtail_verifier_error` |
| 140594 | `second_stage_grading_error` |
| 143425 | `search_longtail_verifier_error` |
| 150292 | `search_longtail_verifier_error` |
| 176888 | `search_longtail_verifier_error` |
| 181998 | `search_longtail_verifier_error` |
| 223632 | `search_longtail_verifier_error` |
| 233415 | `wikipedia_infobox_generation_error:URLError:<urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1017)>` |
| 249875 | `search_longtail_verifier_error` |
| 253413 | `search_longtail_verifier_error` |
| 255474 | `search_longtail_verifier_error` |
| 271181 | `search_longtail_verifier_error` |
| 296558 | `search_longtail_verifier_error` |
| 333680 | `search_longtail_verifier_error` |
| 384163 | `second_stage_grading_error` |
| 426335 | `search_longtail_verifier_error` |
| 462914 | `search_longtail_verifier_error` |
| 472486 | `search_longtail_verifier_error` |
| 509738 | `search_longtail_verifier_error` |
| 522916 | `search_longtail_verifier_error` |
| 595323 | `search_longtail_verifier_error` |
| 615865 | `search_longtail_verifier_error` |
| 656544 | `search_longtail_verifier_error` |
| 659697 | `search_longtail_verifier_error` |
| 689567 | `search_longtail_verifier_error` |
| 712154 | `search_longtail_verifier_error` |
| 757835 | `search_longtail_verifier_error` |
| 870016 | `wikipedia_infobox_generation_error:URLError:<urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1017)>` |
| 900024 | `search_longtail_verifier_error` |
| 939668 | `search_longtail_verifier_error` |
| 966935 | `search_longtail_verifier_error` |
| 1124684 | `search_longtail_verifier_error` |
| 1124716 | `search_longtail_verifier_error` |
| 1159215 | `search_longtail_verifier_error` |
| 1160811 | `search_longtail_verifier_error` |
| 1344011 | `search_longtail_verifier_error` |
| 1371710 | `search_longtail_verifier_error` |
| 1776674 | `search_longtail_verifier_error` |
| 1781836 | `search_longtail_verifier_error` |
| 1924548 | `search_longtail_verifier_error` |
| 1964020 | `search_longtail_verifier_error` |
| 1967693 | `search_longtail_verifier_error` |
| 2152050 | `second_stage_grading_error` |
| 2321132 | `search_longtail_verifier_error` |
| 2380290 | `search_longtail_verifier_error` |
| 2462149 | `search_longtail_verifier_error` |
| 2496880 | `second_stage_grading_error` |
| 2497333 | `search_longtail_verifier_error` |
| 2583361 | `search_longtail_verifier_error` |
| 3941629 | `search_longtail_verifier_error` |
| 4056032 | `second_stage_grading_error` |
| 4207096 | `search_longtail_verifier_error` |
| 4278374 | `search_longtail_verifier_error` |
| 4411216 | `search_longtail_verifier_error` |
| 5885099 | `search_longtail_verifier_error` |
| 6730560 | `search_longtail_verifier_error` |
| 7958128 | `search_longtail_verifier_error` |
| 9707508 | `search_longtail_verifier_error` |
| 10433447 | `search_longtail_verifier_error` |
| 10593104 | `search_longtail_verifier_error` |
| 11557885 | `search_longtail_verifier_error` |
| 12311469 | `search_longtail_verifier_error` |
| 12907693 | `wikipedia_infobox_generation_error:URLError:<urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1017)>` |
| 13837592 | `search_longtail_verifier_error` |
| 14302690 | `search_longtail_verifier_error` |
| 14646325 | `search_longtail_verifier_error` |
| 14768644 | `wikipedia_infobox_generation_error:URLError:<urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1017)>` |
| 16206708 | `search_longtail_verifier_error` |
| 16561337 | `wikipedia_infobox_generation_error:URLError:<urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1017)>` |
| 17938013 | `search_longtail_verifier_error` |
| 18494414 | `search_longtail_verifier_error` |
| 18830712 | `search_longtail_verifier_error` |
| 20647359 | `search_longtail_verifier_error` |
| 26282330 | `search_longtail_verifier_error` |
| 26444143 | `search_longtail_verifier_error` |
| 26673818 | `search_longtail_verifier_error` |
| 40566019 | `search_longtail_verifier_error` |
| 41251289 | `search_longtail_verifier_error` |
| 46965651 | `search_longtail_verifier_error` |
| 47048173 | `search_longtail_verifier_error` |
| 47574413 | `wikipedia_infobox_generation_error:URLError:<urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1017)>` |
| 47756506 | `search_longtail_verifier_error` |
| 47804196 | `search_longtail_verifier_error` |
| 50512917 | `search_longtail_verifier_error` |
| 57645522 | `search_longtail_verifier_error` |
| 59702217 | `search_longtail_verifier_error` |
| 60637832 | `search_longtail_verifier_error` |


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
| `candidate_processing_seconds` | 1608 | 10033.9893 | 6.2400 | 90.2669 |
| `duckduckgo_search_seconds` | 528 | 3422.5294 | 6.4821 | 60.5843 |
| `first_paragraph_extract_seconds` | 797 | 179.5689 | 0.2253 | 2.3675 |
| `llm_question_generation_seconds` | 794 | 5369.0527 | 6.7620 | 31.4108 |
| `number_reference_margin_seconds` | 528 | 0.0000 | 0.0000 | 0.0000 |
| `page_fetch_seconds` | 1608 | 101.7783 | 0.0633 | 0.5549 |
| `rewrite_seconds` | 567 | 0.0000 | 0.0000 | 0.0000 |
| `second_stage_grading_seconds` | 467 | 6610.7829 | 14.1559 | 86.8884 |
| `table_parse_seconds` | 1608 | 848.6329 | 0.5278 | 11.7306 |
| `total_generation_seconds` | 1608 | 6803.8686 | 4.2313 | 32.0084 |
| `total_processing_seconds` | 1608 | 10033.9893 | 6.2400 | 90.2669 |

## Accepted Candidates

| Page ID | Question | Answer | Source |
| ---: | --- | --- | --- |
|  | On what month, day, and year did Lil Wayne appear on MTV Cribs? | September 22, 2004 |  |
|  | In what year did John Hurt win the BAFTA Award for Best Actor for his role in The Elephant Man? | 1980 |  |
|  | In what year did Eddie Guerrero make his first video game appearance? | 1997 |  |
|  | In what year did Frank Oz win the Disney Legends award for Outstanding Film and Television Contributions to The Walt Disney Company? | 2024 |  |
|  | In what year did Mansfield Town F.C. first have Umbro as their kit supplier? | 1975 |  |
|  | In what year was the baronetcy last awarded according to the infobox? | 1990 |  |
|  | In what year did Agatha Christie's Poirot win the Edgar Award for Best Episode in a TV Series? | 1992 |  |
|  | On what month, day, and year was The Complete First Season DVD of The King of Queens released in Region 1 (US)? | November 18, 2003 |  |
|  | In what year did Club Necaxa first have Adidas as their kit manufacturer? | 1987 |  |
|  | In what year did Jimmy Snuka make his video game debut? | 2001 |  |
|  | In what year was the Kingdom of Cilicia annexed by the Achaemenid Empire? | 401 BC |  |
|  | What is the temporal range in million years ago (Ma) during which seaweed has existed according to the infobox? | 1000–0 Ma |  |
|  | What was the exact duration of Felix Trinidad's longest reign as a world welterweight champion? | 7 years, 11 months, 2 weeks and 2 days |  |
|  | In what years did Grant Morrison write for the Batman comic series? | 2006-2009 |  |
|  | On what month and day is the Light up the Night Parade held in Moscow, Idaho? | December 1 |  |
|  | On what month, day, and year did Subhi Bay Barakat al-Khalidi start his term as Head of State under the Mandate for Syria and the Lebanon? | January 1, 1925 |  |
|  | In what year was Mauretania established as a political entity? | 225 BC |  |
|  | In what year did the Nordstrom restaurant 'Marketplace Cafe' debut after being rebranded from Classic Cafe? | 1998 |  |
|  | In what year was the Gold Certificate series of the United States one-hundred-dollar bill issued? | 1928 |  |
|  | In what year did Lisbeth L. Petersen begin her term as mayor of Tórshavn? | 1991 |  |
|  | On what month, day, and year did Olga Khokhlova's term of office as a representative in the Federation Council of Vladimir Oblast begin? | October 5, 2018 |  |
|  | In what year was Super Tuesday inaugurated as a United States presidential primary election day? | 1984 |  |
|  | In what year did the station WVNY in Burlington, Vermont / Plattsburgh, New York end its affiliation with the Global Television Network? | 1990 |  |
|  | In what year was the Shiji first published? | c. 91 BC |  |
|  | In what year did Art Carney win the Academy Award for Best Actor for his role in Harry and Tonto? | 1974 |  |
|  | In what verse range does the New Revised Standard Version of the Bible label the heading 'The Coming Messenger' in the Book of Malachi? | 3:1–7 |  |
|  | In what year did Cyprus change from being a fief of the Grand Vizier to an eyalet (province)? | 1745 |  |
|  | In what year did Ken Watanabe first appear in the television series Taiyō ni Hoero!? | 1983 |  |
|  | On what month, day, and year did Phil Taylor first set the world record for the highest televised average in darts? | December 5, 1991 |  |
|  | In what year did the town of Son lose its town status due to a municipal merger? | 1963 |  |
|  | In what year did John Debney win the ASCAP Award for Top Box Office Films for I Know What You Did Last Summer? | 1997 |  |
|  | On what month, day, and year was the complete DVD collection of Chicago Hope released in Region 2? | December 14, 2015 |  |
|  | In what year did the USFL use the seven-official system in gridiron football? | 2022 |  |
|  | On what month, day, and year did Taisuke Ishii first enter office as mayor of Kawasaki? | October 18, 1924 |  |
|  | In what years did Enver Marić play in the Yugoslav First League? | 1967–1976, 1978–1985 |  |
|  | On what month, day, and year did Joe Calzaghe win The Ring light-heavyweight title against Bernard Hopkins? | April 19, 2008 |  |
|  | In what year did The Miseducation of Lauryn Hill achieve its peak position on the Greek Albums (IFPI) chart? | 2022 |  |
|  | On what month, day, and year did John McDonald take over as leader of the Alberta Liberal Party? | March 28, 1930 |  |
|  | In what year was the 3rd revision of the volume titled 'Major Ships' of the Ships of the Royal Navy published? | 2006 |  |
|  | On what month, day, and year did Willie Stargell hit for the cycle? | July 22, 1964 |  |
|  | In what year did Foxboro Stadium stop serving as the home of the New England Patriots? | 2002 |  |
|  | In what year did Brent Musburger first serve as the play-by-play announcer for the BCS National Championship Game broadcast on ESPN Radio? | 2007 |  |
|  | In what year was John Brown elected as the Council President of Warren, Ohio? | 2025 |  |
|  | On what month, day, and year did Guy T. McBride, Jr. end his term as president of Colorado School of Mines? | July 31, 1984 |  |
|  | In what year did Platt Adams serve as the technical director for the men's Italian national athletics team? | 1920 |  |
|  | On what date was the Canadian premium television network Crave originally launched? | February 1, 1983 |  |
|  | In what year did FC Mariupol start using Nike as their football kit sponsor with AIG as the shirt sponsor? | 2014 |  |
|  | In what year did the Oxford team from Christ Church compete against the Cambridge team from Caius in the Men's Collegiate Boat Race? | 2011 |  |
|  | In what year did Marcos Ambrose drive car number 09 for Richard Petty Motorsports in the NASCAR Nationwide Series? | 2014 |  |
|  | In what year did the Annals of Emperor Ping, as recorded in the Book of Han, end? | 5 CE |  |
|  | On what month, day, and year did Tammy Baldwin's term as chair of the Congressional Equality Caucus begin? | June 4, 2008 |  |
|  | In what year did the Toyota franchise last win the PBA Philippine Cup championship? | 1978 |  |
|  | In what year is the Ohio Bobcats football team scheduled to play a non-conference game at James Madison? | 2035 |  |
|  | On what month, day, and year was the Dangerous Minds soundtrack released? | August 10, 1995 |  |
|  | On what month, day, and year did the mining disaster with the highest death toll occur in the Rhondda Valley? | November 8, 1867 |  |
|  | In what year did Willie Gault appear in the TV movie Sporting Chance? | 1988 |  |
|  | What were the exact dates on which the 1988 Stanley Cup Final took place? | May 18–26, 1988 |  |
|  | In what year did the production of the Cadillac Eldorado begin? | 1952 |  |
|  | On what month, day, and year was the episode "Anarchy in Royston Vasey" from Series 2 originally released? | February 11, 2000 |  |
|  | In what year did Jessica Lynch play the role of Beth Barlow in a film? | 2016 |  |
|  | In the Muscogee language, what past tense form of the verb 'to buy' is used to indicate an action that happened about a year ago? | Past 3 |  |
|  | In what month and year was the destroyer Akishimo of the Imperial Japanese Navy commissioned during World War II? | 1944-03 |  |
|  | In what year did Billy Bingham play for Sunderland in the First Division season when he made 36 league appearances and scored 7 league goals? | 1951 |  |
|  | In what year did Raquel Atawo reach the semifinals in the Australian Open doubles tournament for the first time? | 2013 |  |
|  | On what month, day, and year was Major Francis Peirson appointed as lieutenant governor of Jersey? | January 6, 1781 |  |
|  | On what month, day, and year was the Salle Favart (1st) theatre destroyed by fire? | January 14, 1838 |  |
|  | In what year was Zhoukoudian made into a township? | 1953 |  |
|  | In what year did Arthur H. Bartholomew begin his term as mayor of Ansonia, Connecticut? | 1893 |  |
|  | In what year did the Hampton Pirates football team win the Central Intercollegiate Athletics Association championship with a perfect 6–0 overall record under coach L.L. Pepin? | 1913 |  |
|  | On what month, day, and year did Roberto Durán win the NBA super middleweight title by defeating Pat Lawlor? | June 16, 2000 |  |
|  | On what month, day, and year did John Palin leave office as Chief Justice of the Supreme Court in the Province of North Carolina? | October 18, 1732 |  |
|  | On what month, day, and year was the soundtrack album for Evan Almighty released? | July 3, 2007 |  |
|  | In what year was the Menai Suspension Bridge designed by Thomas Telford? | 1826 |  |
|  | On what month and day is the feast of Baruch ben Neriah celebrated in the Catholic Church? | 15 November |  |
|  | In what year did the Venezuelan Football Federation become affiliated with FIFA? | 1937 |  |
|  | In what year did the OFC Men's Nations Cup first use a format with two-legged semi-finals and a two-legged final? | 1996 |  |
|  | In what year did the Committee to Protect Journalists pause publication of its Global Impunity Index? | 2025 |  |
|  | In what year did Hapoel Petah Tikva F.C. win the Lilian Cup? | 1989 |  |
|  | In what year was the Embraer EMB 120 turboprop aircraft retired from the Delta Connection historical fleet? | 2015 |  |
|  | What is the typical time to return to diving after a middle ear barotrauma classified as grade 5 with perforation of the tympanic membrane? | Three months |  |
|  | In what year was the naval rank Oberleutnant zur See formed in Germany? | 1898 |  |
|  | In what year did Joey Ryan appear in the short film titled 'Jesse Ventura for President?' | 2010 |  |
|  | On what date did the Prince George of Denmark (Exhibition of Bill) Act 1688 receive royal assent? | April 3, 1689 |  |
|  | On what month, day, and year was George L. Smith formally installed as the successor for the Louisiana 4th district after Rep-elect Samuel Peters died before taking his seat? | November 24, 1873 |  |
|  | In what year was the extension called Multi-mode GKP codes introduced for the Gottesman-Kitaev-Preskill (GKP) code? | 2022 |  |
|  | On what month, day, and year did Season 1 of MTV Cribs premiere? | September 20, 2000 |  |
|  | In what year was the Florida's 2nd Congressional District election held where Allen Boyd was the Democratic candidate? | 2006 |  |
|  | By what historical period did Andalusi Romance become extinct? | by the Late Middle Ages |  |

## Second-Stage Filtering Responses

These are the small-model QA responses used by the second-stage filter: `openai/gpt-4.1-mini` and `google/gemini-3-flash-preview`.

| Page ID | Question | Reference answer | openai/gpt-4.1-mini | google/gemini-3-flash-preview |
| ---: | --- | --- | --- | --- |
|  | On what month, day, and year did Lil Wayne appear on MTV Cribs? | September 22, 2004 | INCORRECT; predicted_answer: Lil Wayne appeared on MTV Cribs on March 3, 2006. | INCORRECT; predicted_answer: Lil Wayne appeared on MTV Cribs on **September 20, 2001** (Season 3, Episode 10). |
|  | In what year did John Hurt win the BAFTA Award for Best Actor for his role in The Elephant Man? | 1980 | INCORRECT; predicted_answer: John Hurt won the BAFTA Award for Best Actor for his role in The Elephant Man in 1981. | INCORRECT; predicted_answer: John Hurt won the BAFTA Award for Best Actor for his role in *The Elephant Man* in **1981**. |
|  | In what year did Eddie Guerrero make his first video game appearance? | 1997 | INCORRECT; predicted_answer: Eddie Guerrero made his first video game appearance in 1999. | INCORRECT; predicted_answer: Eddie Guerrero made his first video game appearance in **1994** in the Japanese arcade game ***Virtual Pro Wrestling*** (also known as *Let's Shake in the Ring*), where he appeared under his "Black Tiger" persona. |
|  | In what year did Frank Oz win the Disney Legends award for Outstanding Film and Television Contributions to The Walt Disney Company? | 2024 | INCORRECT; predicted_answer: Frank Oz won the Disney Legends award for Outstanding Film and Television Contributions to The Walt Disney Company in 2008. | INCORRECT; predicted_answer: Frank Oz was named a Disney Legend in **2011**. |
|  | In what year did Mansfield Town F.C. first have Umbro as their kit supplier? | 1975 | INCORRECT; predicted_answer: Mansfield Town F.C. first had Umbro as their kit supplier in 2010. | INCORRECT; predicted_answer: Mansfield Town F.C. first had Umbro as their kit supplier in **1974**. |
|  | In what year was the baronetcy last awarded according to the infobox? | 1990 | INCORRECT; predicted_answer: The baronetcy was last awarded in 1964 according to the infobox. | INCORRECT; predicted_answer: According to the infobox, the baronetcy was last awarded in **1964**. |
|  | In what year did Agatha Christie's Poirot win the Edgar Award for Best Episode in a TV Series? | 1992 | INCORRECT; predicted_answer: Agatha Christie's Poirot won the Edgar Award for Best Episode in a TV Series in 1991. | INCORRECT; predicted_answer: *Agatha Christie's Poirot* won the Edgar Award for Best Episode in a TV Series in **2010** for the episode "The Lost Mine." |
|  | On what month, day, and year was The Complete First Season DVD of The King of Queens released in Region 1 (US)? | November 18, 2003 | INCORRECT; predicted_answer: The Complete First Season DVD of The King of Queens was released in Region 1 (US) on October 7, 2003. | INCORRECT; predicted_answer: The King of Queens: The Complete First Season was released on DVD in Region 1 on **November 11, 2003**. |
|  | In what year did Club Necaxa first have Adidas as their kit manufacturer? | 1987 | INCORRECT; predicted_answer: Club Necaxa first had Adidas as their kit manufacturer in 2013. | INCORRECT; predicted_answer: Club Necaxa first had Adidas as their kit manufacturer in **2024**. |
|  | In what year did Jimmy Snuka make his video game debut? | 2001 | INCORRECT; predicted_answer: Jimmy Snuka made his video game debut in 1986. | INCORRECT; predicted_answer: Jimmy Snuka made his video game debut in **1989** in the Nintendo Entertainment System (NES) game ***WWF WrestleMania***. |
|  | In what year was the Kingdom of Cilicia annexed by the Achaemenid Empire? | 401 BC | INCORRECT; predicted_answer: The Kingdom of Cilicia was annexed by the Achaemenid Empire in 540 BCE. | INCORRECT; predicted_answer: The Kingdom of Cilicia was annexed by the Achaemenid Empire in approximately **540 BC**, following the campaigns of Cyrus the Great. |
|  | What is the temporal range in million years ago (Ma) during which seaweed has existed according to the infobox? | 1000–0 Ma | INCORRECT; predicted_answer: According to the infobox, seaweed has existed from 1,500 million years ago (Ma) to the present. | INCORRECT; predicted_answer: According to the fossil record, seaweed has existed from approximately **1,600 million years ago (Ma)** to the present. |
|  | What was the exact duration of Felix Trinidad's longest reign as a world welterweight champion? | 7 years, 11 months, 2 weeks and 2 days | INCORRECT; predicted_answer: Felix Trinidad's longest reign as a world welterweight champion lasted exactly 3 years, 11 months, and 14 days. He held the IBF welterweight title from March 12, 1996, to March 26, 2000. | INCORRECT; predicted_answer: Felix Trinidad’s reign as the IBF welterweight champion lasted **6 years, 8 months, and 14 days** (June 19, 1993, to March 3, 2000). |
|  | In what years did Grant Morrison write for the Batman comic series? | 2006-2009 | INCORRECT; predicted_answer: Grant Morrison wrote for the Batman comic series primarily from 2006 to 2013. | INCORRECT; predicted_answer: Grant Morrison wrote the main *Batman* title and its core interconnected storylines from **2006 to 2013**. |
|  | On what month and day is the Light up the Night Parade held in Moscow, Idaho? | December 1 | INCORRECT; predicted_answer: The Light up the Night Parade in Moscow, Idaho is held on the first Friday in December. | INCORRECT; predicted_answer: The Light up the Night Parade in Moscow, Idaho, is held on the **second Thursday of December**. |
|  | On what month, day, and year did Subhi Bay Barakat al-Khalidi start his term as Head of State under the Mandate for Syria and the Lebanon? | January 1, 1925 | INCORRECT; predicted_answer: Subhi Bay Barakat al-Khalidi started his term as Head of State under the Mandate for Syria and the Lebanon on **March 8, 1922**. | INCORRECT; predicted_answer: Subhi Bay Barakat al-Khalidi started his term as Head of State on **June 28, 1922**. |
|  | In what year was Mauretania established as a political entity? | 225 BC | INCORRECT; predicted_answer: Mauretania was established as a political entity in 3 BCE as a Roman client kingdom. | INCORRECT; predicted_answer: Mauretania was established as a formal Roman province in **40 AD**, following the annexation of the kingdom by Emperor Caligula and its subsequent reorganization by Emperor Claudius. |
|  | In what year did the Nordstrom restaurant 'Marketplace Cafe' debut after being rebranded from Classic Cafe? | 1998 | INCORRECT; predicted_answer: The Nordstrom restaurant "Marketplace Cafe" debuted in 2014 after being rebranded from Classic Cafe. | INCORRECT; predicted_answer: The Marketplace Cafe debuted in **1999**. |
|  | In what year was the Gold Certificate series of the United States one-hundred-dollar bill issued? | 1928 | INCORRECT; predicted_answer: The Gold Certificate series of the United States one-hundred-dollar bill was issued in 1900. | INCORRECT; predicted_answer: The United States issued $100 Gold Certificates in several series years, most notably **1863, 1882, 1907, and 1922**, as well as the small-size series of **1928**. |
|  | In what year did Lisbeth L. Petersen begin her term as mayor of Tórshavn? | 1991 | INCORRECT; predicted_answer: Lisbeth L. Petersen began her term as mayor of Tórshavn in 1993. | INCORRECT; predicted_answer: Lisbeth L. Petersen began her term as mayor of Tórshavn in **1993**. |
|  | On what month, day, and year did Olga Khokhlova's term of office as a representative in the Federation Council of Vladimir Oblast begin? | October 5, 2018 | INCORRECT; predicted_answer: Olga Khokhlova's term of office as a representative in the Federation Council of Vladimir Oblast began on October 5, 2021. | INCORRECT; predicted_answer: Olga Khokhlova's term of office began on **September 18, 2018**. |
|  | In what year was Super Tuesday inaugurated as a United States presidential primary election day? | 1984 | INCORRECT; predicted_answer: Super Tuesday was inaugurated as a United States presidential primary election day in 1988. | INCORRECT; predicted_answer: Super Tuesday was inaugurated in **1988**. |
|  | In what year did the station WVNY in Burlington, Vermont / Plattsburgh, New York end its affiliation with the Global Television Network? | 1990 | INCORRECT; predicted_answer: WVNY ended its affiliation with the Global Television Network in 2002. | INCORRECT; predicted_answer: WVNY ended its affiliation with the Global Television Network in **1977**. |
|  | In what year was the Shiji first published? | c. 91 BC | INCORRECT; predicted_answer: The Shiji was first completed around 94 BCE. | INCORRECT; predicted_answer: The *Shiji* (Records of the Grand Historian) was completed around **94 BC**. Because it was written before the invention of the printing press, it was initially circulated via hand-copied manuscripts rather than a formal publication date. |
|  | In what year did Art Carney win the Academy Award for Best Actor for his role in Harry and Tonto? | 1974 | INCORRECT; predicted_answer: Art Carney won the Academy Award for Best Actor in 1975 for his role in Harry and Tonto. | INCORRECT; predicted_answer: Art Carney won the Academy Award for Best Actor in **1975** (for the 47th Academy Awards, honoring films from 1974). |
|  | In what verse range does the New Revised Standard Version of the Bible label the heading 'The Coming Messenger' in the Book of Malachi? | 3:1–7 | INCORRECT; predicted_answer: In the New Revised Standard Version (NRSV) of the Bible, the heading "The Coming Messenger" in the Book of Malachi is labeled over Malachi 3:1–5. | INCORRECT; predicted_answer: In the New Revised Standard Version (NRSV), the heading "The Coming Messenger" covers **Malachi 3:1–5**. |
|  | In what year did Cyprus change from being a fief of the Grand Vizier to an eyalet (province)? | 1745 | INCORRECT; predicted_answer: Cyprus changed from being a fief of the Grand Vizier to an eyalet (province) in the year 1670. | INCORRECT; predicted_answer: Cyprus became an eyalet (province) of the Ottoman Empire in **1571**, immediately following its conquest from the Venetians. |
|  | In what year did Ken Watanabe first appear in the television series Taiyō ni Hoero!? | 1983 | INCORRECT; predicted_answer: Ken Watanabe first appeared in the television series Taiyō ni Hoero!? in 1980. | INCORRECT; predicted_answer: Ken Watanabe first appeared in *Taiyō ni Hoero!* in **1982** (Episode 511). |
|  | On what month, day, and year did Phil Taylor first set the world record for the highest televised average in darts? | December 5, 1991 | INCORRECT; predicted_answer: Phil Taylor first set the world record for the highest televised average in darts on January 3, 2010. | INCORRECT; predicted_answer: Phil Taylor first set the world record for the highest televised average on **May 4, 2002**, with an average of 118.66 against Kevin Painter. |
|  | In what year did the town of Son lose its town status due to a municipal merger? | 1963 | INCORRECT; predicted_answer: The town of Son lost its town status in 1964 due to a municipal merger. | INCORRECT; predicted_answer: The town of Son lost its town status in **1964** when it merged with the municipality of Hølen to form the new municipality of Vestby. |
|  | In what year did John Debney win the ASCAP Award for Top Box Office Films for I Know What You Did Last Summer? | 1997 | INCORRECT; predicted_answer: John Debney won the ASCAP Award for Top Box Office Films for *I Know What You Did Last Summer* in 1998. | INCORRECT; predicted_answer: John Debney won the ASCAP Award for Top Box Office Films for *I Know What You Did Last Summer* in **1998**. |
|  | On what month, day, and year was the complete DVD collection of Chicago Hope released in Region 2? | December 14, 2015 | INCORRECT; predicted_answer: The complete DVD collection of Chicago Hope was released in Region 2 on November 12, 2012. | INCORRECT; predicted_answer: The complete DVD collection of *Chicago Hope* was released in Region 2 on **August 1, 2016**. |
|  | In what year did the USFL use the seven-official system in gridiron football? | 2022 | INCORRECT; predicted_answer: The USFL used the seven-official system in gridiron football in 1984. | INCORRECT; predicted_answer: The USFL used the seven-official system during its entire original run from **1983 to 1985**. |
|  | On what month, day, and year did Taisuke Ishii first enter office as mayor of Kawasaki? | October 18, 1924 | INCORRECT; predicted_answer: Taisuke Ishii first entered office as mayor of Kawasaki on November 30, 2021. | INCORRECT; predicted_answer: Taisuke Ishii first entered office as mayor of Kawasaki on **October 27, 1971**. |
|  | In what years did Enver Marić play in the Yugoslav First League? | 1967–1976, 1978–1985 | INCORRECT; predicted_answer: Enver Marić played in the Yugoslav First League from 1967 to 1978. | INCORRECT; predicted_answer: Enver Marić played in the Yugoslav First League from **1967 to 1976** and from **1981 to 1985**, representing Velež Mostar during both periods. |
|  | On what month, day, and year did Joe Calzaghe win The Ring light-heavyweight title against Bernard Hopkins? | April 19, 2008 | INCORRECT; predicted_answer: Joe Calzaghe won The Ring light-heavyweight title against Bernard Hopkins on April 3, 2009. | INCORRECT; predicted_answer: Joe Calzaghe won *The Ring* light-heavyweight title against Bernard Hopkins on **April 12, 2008**. |
|  | In what year did The Miseducation of Lauryn Hill achieve its peak position on the Greek Albums (IFPI) chart? | 2022 | INCORRECT; predicted_answer: The Miseducation of Lauryn Hill achieved its peak position on the Greek Albums (IFPI) chart in 1998. | INCORRECT; predicted_answer: **2021** (specifically in October, when it peaked at number 1). |
|  | On what month, day, and year did John McDonald take over as leader of the Alberta Liberal Party? | March 28, 1930 | INCORRECT; predicted_answer: John McDonald took over as leader of the Alberta Liberal Party on March 27, 2021. | INCORRECT; predicted_answer: John McDonald took over as leader of the Alberta Liberal Party on **January 14, 1930**. |
|  | In what year was the 3rd revision of the volume titled 'Major Ships' of the Ships of the Royal Navy published? | 2006 | INCORRECT; predicted_answer: The 3rd revision of the volume titled "Major Ships" of the Ships of the Royal Navy was published in 2004. | INCORRECT; predicted_answer: The 3rd revision of *Ships of the Royal Navy* (originally by J.J. Colledge) was published in **2003**. |
|  | On what month, day, and year did Willie Stargell hit for the cycle? | July 22, 1964 | INCORRECT; predicted_answer: Willie Stargell hit for the cycle on August 1, 1978. | INCORRECT; predicted_answer: Willie Stargell hit for the cycle on **May 29, 1964**. |
|  | In what year did Foxboro Stadium stop serving as the home of the New England Patriots? | 2002 | INCORRECT; predicted_answer: Foxboro Stadium stopped serving as the home of the New England Patriots in 2001. | INCORRECT; predicted_answer: Foxboro Stadium stopped serving as the home of the New England Patriots in **2001**. |
|  | In what year did Brent Musburger first serve as the play-by-play announcer for the BCS National Championship Game broadcast on ESPN Radio? | 2007 | INCORRECT; predicted_answer: Brent Musburger first served as the play-by-play announcer for the BCS National Championship Game broadcast on ESPN Radio in 2011. | INCORRECT; predicted_answer: Brent Musburger first served as the play-by-play announcer for the BCS National Championship Game on ESPN Radio in **2000** (the 2000 Sugar Bowl). |
|  | In what year was John Brown elected as the Council President of Warren, Ohio? | 2025 | INCORRECT; predicted_answer: John Brown was elected as the Council President of Warren, Ohio in 2023. | INCORRECT; predicted_answer: John Brown was elected as the Council President of Warren, Ohio, in **2019**. |
|  | On what month, day, and year did Guy T. McBride, Jr. end his term as president of Colorado School of Mines? | July 31, 1984 | INCORRECT; predicted_answer: Guy T. McBride, Jr. ended his term as president of Colorado School of Mines on June 30, 1997. | INCORRECT; predicted_answer: Guy T. McBride, Jr. ended his term as president of the Colorado School of Mines on **August 31, 1984**. |
|  | In what year did Platt Adams serve as the technical director for the men's Italian national athletics team? | 1920 | INCORRECT; predicted_answer: Platt Adams served as the technical director for the men's Italian national athletics team in 1935. | INCORRECT; predicted_answer: Platt Adams served as the technical director for the Italian national athletics team in **1924**, leading them during the Summer Olympics in Paris. |
|  | On what date was the Canadian premium television network Crave originally launched? | February 1, 1983 | INCORRECT; predicted_answer: The Canadian premium television network Crave was originally launched on December 12, 2014. | INCORRECT; predicted_answer: Crave (originally launched as CraveTV) was launched on **December 11, 2014**. |
|  | In what year did FC Mariupol start using Nike as their football kit sponsor with AIG as the shirt sponsor? | 2014 | INCORRECT; predicted_answer: FC Mariupol started using Nike as their football kit sponsor with AIG as the shirt sponsor in the year 2017. | INCORRECT; predicted_answer: FC Mariupol (then known as **Illichivets Mariupol**) began using Nike kits with AIG as the shirt sponsor in **2007**. |
|  | In what year did the Oxford team from Christ Church compete against the Cambridge team from Caius in the Men's Collegiate Boat Race? | 2011 | INCORRECT; predicted_answer: The Oxford team from Christ Church competed against the Cambridge team from Caius in the Men's Collegiate Boat Race in 2007. | INCORRECT; predicted_answer: The Oxford team from Christ Church competed against the Cambridge team from Gonville & Caius in **1829**. This was the first-ever Inter-University Boat Race. |
|  | In what year did Marcos Ambrose drive car number 09 for Richard Petty Motorsports in the NASCAR Nationwide Series? | 2014 | INCORRECT; predicted_answer: Marcos Ambrose drove car number 09 for Richard Petty Motorsports in the NASCAR Nationwide Series in 2012. | INCORRECT; predicted_answer: Marcos Ambrose drove the number 09 car for Richard Petty Motorsports in the NASCAR Nationwide Series in **2011**. |
|  | In what year did the Annals of Emperor Ping, as recorded in the Book of Han, end? | 5 CE | INCORRECT; predicted_answer: The Annals of Emperor Ping, as recorded in the Book of Han, end in the year 6 AD. | INCORRECT; predicted_answer: The Annals of Emperor Ping in the *Book of Han* end in **6 AD** (the 12th month of the 5th year of the Yuanshi era), following the Emperor's death. |
|  | On what month, day, and year did Tammy Baldwin's term as chair of the Congressional Equality Caucus begin? | June 4, 2008 | INCORRECT; predicted_answer: Tammy Baldwin's term as chair of the Congressional Equality Caucus began on January 3, 2023. | INCORRECT; predicted_answer: Tammy Baldwin’s term as chair of the Congressional Equality Caucus (then known as the Congressional Lesbian and Gay Caucus) began on **January 4, 2005**. |
|  | In what year did the Toyota franchise last win the PBA Philippine Cup championship? | 1978 | INCORRECT; predicted_answer: The Toyota franchise last won the PBA Philippine Cup championship in 1975. | INCORRECT; predicted_answer: The Toyota franchise (Toyota Super Corollas) last won the PBA Philippine Cup championship in **1982**. |
|  | In what year is the Ohio Bobcats football team scheduled to play a non-conference game at James Madison? | 2035 | INCORRECT; predicted_answer: The Ohio Bobcats football team is scheduled to play a non-conference game at James Madison in the year 2024. | INCORRECT; predicted_answer: The Ohio Bobcats are scheduled to play at James Madison on **September 20, 2025**. |
|  | On what month, day, and year was the Dangerous Minds soundtrack released? | August 10, 1995 | INCORRECT; predicted_answer: The Dangerous Minds soundtrack was released on August 11, 1995. | INCORRECT; predicted_answer: The *Dangerous Minds* soundtrack was released on **August 1, 1995**. |
|  | On what month, day, and year did the mining disaster with the highest death toll occur in the Rhondda Valley? | November 8, 1867 | INCORRECT; predicted_answer: The mining disaster with the highest death toll in the Rhondda Valley occurred on June 28, 1867. | INCORRECT; predicted_answer: The mining disaster with the highest death toll in the Rhondda Valley occurred on **June 23, 1894**, at the Albion Colliery in Cilfynydd. The explosion killed 290 men and boys. |
|  | In what year did Willie Gault appear in the TV movie Sporting Chance? | 1988 | INCORRECT; predicted_answer: Willie Gault appeared in the TV movie Sporting Chance in 1990. | INCORRECT; predicted_answer: Willie Gault appeared in the TV movie *Sporting Chance* in **1990**. |
|  | What were the exact dates on which the 1988 Stanley Cup Final took place? | May 18–26, 1988 | INCORRECT; predicted_answer: The 1988 Stanley Cup Final took place from May 17 to May 25, 1988. | INCORRECT; predicted_answer: The 1988 Stanley Cup Final took place on the following dates:  *   **Game 1:** May 18 *   **Game 2:** May 20 *   **Game 3:** May 22 *   **Game 4:** May 24 (Suspended due to power failure) *   **Game 4 (Rescheduled):** May 26 |
|  | In what year did the production of the Cadillac Eldorado begin? | 1952 | INCORRECT; predicted_answer: The production of the Cadillac Eldorado began in 1953. | INCORRECT; predicted_answer: Production of the Cadillac Eldorado began in **1953**. |
|  | On what month, day, and year was the episode "Anarchy in Royston Vasey" from Series 2 originally released? | February 11, 2000 | INCORRECT; predicted_answer: The episode "Anarchy in Royston Vasey" from Series 2 was originally released on March 7, 2000. | INCORRECT; predicted_answer: "Anarchy in Royston Vasey" originally aired on **February 18, 2000**. |
|  | In what year did Jessica Lynch play the role of Beth Barlow in a film? | 2016 | INCORRECT; predicted_answer: Jessica Lynch played the role of Beth Barlow in the film "The Texas Chainsaw Massacre" in the year 2003. | INCORRECT; predicted_answer: Jessica Lynch played the role of Beth Barlow in the film **2014** (specifically in the movie *Virtuous*). |
|  | In the Muscogee language, what past tense form of the verb 'to buy' is used to indicate an action that happened about a year ago? | Past 3 | INCORRECT; predicted_answer: In the Muscogee language, to indicate a past action that happened about a year ago, the **remote past tense** form of the verb "to buy" is used. This form specifically conveys that the action occurred in the distant past, such as roughly a year ago. | INCORRECT; predicted_answer: In the Muscogee (Creek) language, the **fourth past tense** (indicated by the suffix **-vnt-**) is used for actions that occurred a year or more ago.  For the verb "to buy" (**nesetv**), the form is **nesvntis**. |
|  | In what month and year was the destroyer Akishimo of the Imperial Japanese Navy commissioned during World War II? | 1944-03 | INCORRECT; predicted_answer: The destroyer Akishimo of the Imperial Japanese Navy was commissioned in December 1943. | INCORRECT; predicted_answer: The destroyer *Akishimo* was commissioned on **March 11, 1944**. |
|  | In what year did Billy Bingham play for Sunderland in the First Division season when he made 36 league appearances and scored 7 league goals? | 1951 | INCORRECT; predicted_answer: Billy Bingham played for Sunderland in the First Division during the 1966–67 season, when he made 36 league appearances and scored 7 league goals. | INCORRECT; predicted_answer: Billy Bingham achieved those statistics during the **1959–60** season. |
|  | In what year did Raquel Atawo reach the semifinals in the Australian Open doubles tournament for the first time? | 2013 | INCORRECT; predicted_answer: Raquel Atawo reached the semifinals in the Australian Open doubles tournament for the first time in 2016. | INCORRECT; predicted_answer: Raquel Atawo reached the semifinals of the Australian Open doubles tournament for the first time in **2014**. |
|  | On what month, day, and year was Major Francis Peirson appointed as lieutenant governor of Jersey? | January 6, 1781 | INCORRECT; predicted_answer: Major Francis Peirson was appointed as lieutenant governor of Jersey on January 1, 1781. | INCORRECT; predicted_answer: Major Francis Peirson was appointed Lieutenant Governor of Jersey on **July 11, 1780**. |
|  | On what month, day, and year was the Salle Favart (1st) theatre destroyed by fire? | January 14, 1838 | INCORRECT; predicted_answer: The Salle Favart (1st) theatre was destroyed by fire on May 25, 1838. | INCORRECT; predicted_answer: The first Salle Favart was destroyed by fire on **January 15, 1838**. |
|  | In what year was Zhoukoudian made into a township? | 1953 | INCORRECT; predicted_answer: Zhoukoudian was made into a township in the year 1983. | INCORRECT; predicted_answer: Zhoukoudian was made into a township in **1989**. |
|  | In what year did Arthur H. Bartholomew begin his term as mayor of Ansonia, Connecticut? | 1893 | INCORRECT; predicted_answer: Arthur H. Bartholomew began his term as mayor of Ansonia, Connecticut, in 1913. | INCORRECT; predicted_answer: Arthur H. Bartholomew began his term as mayor of Ansonia, Connecticut, in **1913**. |
|  | In what year did the Hampton Pirates football team win the Central Intercollegiate Athletics Association championship with a perfect 6–0 overall record under coach L.L. Pepin? | 1913 | INCORRECT; predicted_answer: The Hampton Pirates football team won the Central Intercollegiate Athletics Association championship with a perfect 6–0 overall record under coach L.L. Pepin in 1926. | INCORRECT; predicted_answer: The Hampton Pirates won the CIAA championship with a 6–0 record under coach L.L. Pepin in **1914**. |
|  | On what month, day, and year did Roberto Durán win the NBA super middleweight title by defeating Pat Lawlor? | June 16, 2000 | INCORRECT; predicted_answer: Roberto Durán never won the NBA super middleweight title by defeating Pat Lawlor. | INCORRECT; predicted_answer: Roberto Durán never won an NBA super middleweight title; however, he defeated Pat Lawlor to win the **NBA (National Boxing Association)** super middleweight title on **June 16, 1997**. |
|  | On what month, day, and year did John Palin leave office as Chief Justice of the Supreme Court in the Province of North Carolina? | October 18, 1732 | INCORRECT; predicted_answer: John Palin left office as Chief Justice of the Supreme Court in the Province of North Carolina on May 29, 1776. | INCORRECT; predicted_answer: John Palin left office as Chief Justice of the Supreme Court in the Province of North Carolina on **July 27, 1734**. |
|  | On what month, day, and year was the soundtrack album for Evan Almighty released? | July 3, 2007 | INCORRECT; predicted_answer: The soundtrack album for Evan Almighty was released on June 13, 2007. | INCORRECT; predicted_answer: The soundtrack album for *Evan Almighty* was released on **June 19, 2007**. |
|  | In what year was the Menai Suspension Bridge designed by Thomas Telford? | 1826 | INCORRECT; predicted_answer: The Menai Suspension Bridge was designed by Thomas Telford in 1819. | INCORRECT; predicted_answer: Thomas Telford designed the Menai Suspension Bridge in **1818**, with construction beginning in 1819. |
|  | On what month and day is the feast of Baruch ben Neriah celebrated in the Catholic Church? | 15 November | INCORRECT; predicted_answer: The feast of Baruch ben Neriah is celebrated on September 28 in the Catholic Church. | INCORRECT; predicted_answer: The Catholic Church celebrates the feast of Baruch ben Neriah on **September 28**. |
|  | In what year did the Venezuelan Football Federation become affiliated with FIFA? | 1937 | INCORRECT; predicted_answer: The Venezuelan Football Federation became affiliated with FIFA in 1952. | INCORRECT; predicted_answer: The Venezuelan Football Federation (FVF) became affiliated with FIFA in **1952**. |
|  | In what year did the OFC Men's Nations Cup first use a format with two-legged semi-finals and a two-legged final? | 1996 | INCORRECT; predicted_answer: The OFC Men's Nations Cup first used a format with two-legged semi-finals and a two-legged final in 2004. | INCORRECT; predicted_answer: The OFC Men's Nations Cup first used a format with two-legged semi-finals and a two-legged final in **2004**. |
|  | In what year did the Committee to Protect Journalists pause publication of its Global Impunity Index? | 2025 | INCORRECT; predicted_answer: The Committee to Protect Journalists paused publication of its Global Impunity Index in 2020. | INCORRECT; predicted_answer: The Committee to Protect Journalists paused publication of its Global Impunity Index in **2023**. |
|  | In what year did Hapoel Petah Tikva F.C. win the Lilian Cup? | 1989 | INCORRECT; predicted_answer: Hapoel Petah Tikva F.C. won the Lilian Cup in 1985. | INCORRECT; predicted_answer: Hapoel Petah Tikva F.C. won the Lilian Cup in **1986**. |
|  | In what year was the Embraer EMB 120 turboprop aircraft retired from the Delta Connection historical fleet? | 2015 | INCORRECT; predicted_answer: The Embraer EMB 120 turboprop aircraft was retired from the Delta Connection historical fleet in 2003. | INCORRECT; predicted_answer: The Embraer EMB 120 was retired from the Delta Connection fleet in **2010**. |
|  | What is the typical time to return to diving after a middle ear barotrauma classified as grade 5 with perforation of the tympanic membrane? | Three months | INCORRECT; predicted_answer: For a middle ear barotrauma classified as grade 5 with tympanic membrane perforation, the typical recommended time to return to diving is usually **6 to 8 weeks** after complete healing of the perforation. Diving should only be resumed once the tympanic membrane has fully healed, there is no middle ear infection, and normal middle ear function is confirmed by an ENT specialist. Premature return to diving risks worsening injury or infection. | INCORRECT; predicted_answer: The typical time to return to diving after a Grade 5 middle ear barotrauma with a perforated tympanic membrane is **6 to 12 weeks**, provided the eardrum has completely healed and Eustachian tube function has returned to normal.  Before returning to the water, a diver must be cleared by an ENT specialist or a physician trained in dive medicine to ensure the membrane is intact and capable of withstanding pressure changes. If the perforation does not heal spontaneously, surgical repair (tympanoplasty) may be required, which significantly extends the recovery timeline. |
|  | In what year was the naval rank Oberleutnant zur See formed in Germany? | 1898 | INCORRECT; predicted_answer: The naval rank Oberleutnant zur See was formed in Germany in the year 1890. | INCORRECT; predicted_answer: The naval rank *Oberleutnant zur See* was formed in Germany in **1890**. |
|  | In what year did Joey Ryan appear in the short film titled 'Jesse Ventura for President?' | 2010 | INCORRECT; predicted_answer: Joey Ryan appeared in the short film titled "Jesse Ventura for President" in the year 2012. | INCORRECT; predicted_answer: Joey Ryan appeared in the short film *Jesse Ventura for President* in **2004**. |
|  | On what date did the Prince George of Denmark (Exhibition of Bill) Act 1688 receive royal assent? | April 3, 1689 | INCORRECT; predicted_answer: The Prince George of Denmark (Exhibition of Bill) Act 1688 received royal assent on 20 May 1689. | INCORRECT; predicted_answer: The Prince George of Denmark (Exhibition of Bill) Act 1688 received royal assent on **April 9, 1689**. |
|  | On what month, day, and year was George L. Smith formally installed as the successor for the Louisiana 4th district after Rep-elect Samuel Peters died before taking his seat? | November 24, 1873 | INCORRECT; predicted_answer: George L. Smith was formally installed as the successor for the Louisiana 4th district on December 20, 1821, after Rep-elect Samuel Peters died before taking his seat. | INCORRECT; predicted_answer: George L. Smith was formally installed on **December 3, 1873**. |
|  | In what year was the extension called Multi-mode GKP codes introduced for the Gottesman-Kitaev-Preskill (GKP) code? | 2022 | INCORRECT; predicted_answer: The extension called Multi-mode GKP codes for the Gottesman-Kitaev-Preskill (GKP) code was introduced in 2019. | INCORRECT; predicted_answer: Multi-mode GKP codes were introduced in **2001** by Daniel Gottesman, Alexei Kitaev, and John Preskill in their foundational paper, "Encoding a qubit in an oscillator." |
|  | On what month, day, and year did Season 1 of MTV Cribs premiere? | September 20, 2000 | INCORRECT; predicted_answer: Season 1 of MTV Cribs premiered on August 26, 2000. | INCORRECT; predicted_answer: Season 1 of MTV Cribs premiered on **September 13, 2000**. |
|  | In what year was the Florida's 2nd Congressional District election held where Allen Boyd was the Democratic candidate? | 2006 | INCORRECT; predicted_answer: Allen Boyd was the Democratic candidate in Florida's 2nd Congressional District election in 2010. | INCORRECT; predicted_answer: Allen Boyd was the Democratic candidate for Florida's 2nd Congressional District in every general election from **1996 through 2010** (specifically 1996, 1998, 2000, 2002, 2004, 2006, 2008, and 2010). |
|  | By what historical period did Andalusi Romance become extinct? | by the Late Middle Ages | INCORRECT; predicted_answer: Andalusi Romance became extinct by the late 15th century, around the time of the Reconquista and the fall of Granada in 1492. | INCORRECT; predicted_answer: Andalusi Romance (also known as Mozarabic) became extinct by the **late 13th century or early 14th century**.  Its decline was driven by the Almoravid and Almohad persecutions in the 12th century, which forced many speakers to flee to Christian kingdoms, and was finalized by the *Reconquista*, where it was absorbed or replaced by the prestige languages of the conquerors (Castilian, Catalan, and Portuguese). |
| 380845 | List of countries by GDP (nominal) |  | not run | not run |
| 18618509 | Wikimedia Foundation |  | not run | not run |
| 22943 | Papua New Guinea |  | not run | not run |
| 14649921 | List of largest cities |  | not run | not run |
| 16795291 | In what year did the Boston Celtics and San Francisco/Golden State Warriors most recently face each other in the NBA Finals? | 2022 | not run | not run |
| 4829 | Balkans |  | not run | not run |
| 26828 | Suriname |  | not run | not run |
| 13270 | In what year was the Hawaii state quarter released? | 2008 | not run | not run |
| 324 | In what year did Walt Disney receive his first Academy Award? | 1932 | not run | not run |
| 8099 | In what year did Dave Grohl make an uncredited cameo appearance in the television series The X-Files? | 1996 | not run | not run |
| 147311 | In what year did Ray Charles make his first voice and final film role in Blue's Big Musical Movie? | 2000 | not run | not run |
| 8522 | Denver |  | not run | not run |
| 34953684 | Charli XCX |  | not run | not run |
| 31150160 | 2011 Tōhoku earthquake and tsunami |  | not run | not run |
| 160904 | List of English monarchs |  | not run | not run |
| 11759 | McDonnell Douglas F-4 Phantom II |  | not run | not run |
| 63973 | Wi-Fi |  | not run | not run |
| 32905 | As of what month and year were the largest private employers in West Virginia ranked in the provided table? | 2019-03 | not run | not run |
| 45661106 | Top Gear (2002 TV series) |  | not run | not run |
| 270673 | In what year was the £100 coin, which has unlimited legal tender status, first produced? | 2015 | not run | not run |
| 7892 | In what year did David Cronenberg win the Silver Bear award at the Berlin International Film Festival for the film eXistenZ? | 1999 | not run | not run |
| 21222169 | James McAvoy |  | not run | not run |
| 174716 | Roger Moore |  | not run | not run |
| 1564433 | Scheduled Castes and Scheduled Tribes |  | not run | not run |
| 32388 | Victoria, British Columbia |  | not run | not run |
| 398602 | In what year did William H. Macy play the role of Jerry Lundegaard in the film Fargo? | 1996 | not run | not run |
| 88213 | Apsis |  | not run | not run |
| 2949977 | Allied-occupied Germany |  | not run | not run |
| 3164979 | In what year did Josh Hutcherson host an episode of Saturday Night Live? | 2013 | not run | not run |
| 164939 | In what year did the Airbus A330-300 variant take its maiden flight? | 1992-11 | not run | not run |
| 33295 | In what month and year were the solstices and equinoxes adopted as Lesser Sabbats by members of the Bricket Wood coven? | 1958 | not run | not run |
| 8429 | Density |  | not run | not run |
| 18932702 | Alan Moore |  | not run | not run |
| 3372377 | Optical fiber |  | not run | not run |
| 31130 | Thuringia |  | not run | not run |
| 659310 | In what year did Mary-Louise Parker perform in the Broadway production of "Bus Stop"? | 1996 | not run | not run |
| 89775 | Virginity |  | not run | not run |
| 25211041 | Puberty |  | not run | not run |
| 25168720 | On what month, day, and year was the first theatrical release of the movie Twilight? | November 21, 2008 | not run | not run |
| 22645 | Orkney |  | not run | not run |
| 32066 | Ulster |  | not run | not run |
| 416798 | History of the Jews in Poland |  | not run | not run |
| 3569822 | In what year did the film A Beautiful Mind win the Academy Award for Best Picture? | 2002 | not run | not run |
| 31921 | University of California |  | not run | not run |
| 23295 | Printing press |  | not run | not run |
| 19373302 | In what year did Christina Applegate play the role of Veronica Corningstone in the film Anchorman: The Legend of Ron Burgundy? | 2004 | not run | not run |
| 202295 | In what year was the basketball club UNICS Kazan founded? | 1991 | not run | not run |
| 143117 | In what year did the Old Gujarati language, from which Gujarati is descended, exist until? | 1500 | not run | not run |
| 34411 | Zodiac |  | not run | not run |
| 12186 | Guinea-Bissau |  | not run | not run |
| 5643 | Channel Islands |  | not run | not run |
| 19653842 | Organism |  | not run | not run |
| 149561 | Donna Summer |  | not run | not run |
| 347422 | Republika Srpska |  | not run | not run |
| 58846 | In what year did the reform and mergers of French regions, such as the creation of Grand Est from Alsace, Champagne-Ardenne, and Lorraine, take place? | 2016 | not run | not run |
| 47734 | On what month, day, and year was Chhattisgarh granted statehood with Raipur as its designated state capital? | November 1, 2000 | not run | not run |
| 39458161 | Xbox One |  | not run | not run |
| 225502 | In what year did Ann-Margret star in the film Tommy where she was nominated for an Academy Award for Best Actress? | 1975 | not run | not run |
| 30374 | Taekwondo |  | not run | not run |
| 217231 | What month, day, and year was the DVD for Season 1 of Curb Your Enthusiasm released in Region 1? | January 13, 2004 | not run | not run |
| 23473595 | Light-year |  | not run | not run |
| 158177 | In what year did Condoleezza Rice begin her term as United States Secretary of State? | 2005 | not run | not run |
| 184860 | In what year did Norah Jones make her film debut in My Blueberry Nights? | 2007 | not run | not run |
| 19006979 | Mac (computer) |  | not run | not run |
| 53273 | As of what year are the national program rankings listed in the Duke University rankings and reputation table? | 2026 | not run | not run |
| 400595 | In what year did Patricia Arquette play the role of Olivia Evans in the film Boyhood? | 2014 | not run | not run |
| 48235 | Vaudeville |  | not run | not run |
| 39848 | Chevrolet |  | not run | not run |
| 42374 | Ljubljana |  | not run | not run |
| 23976719 | In what year did the Rugby Football Union begin according to the football codes board? | 1871 | not run | not run |
| 38962787 | In what year did The Blacklist win the Primetime Creative Arts Emmy Award for Outstanding Stunt Coordination for a Drama Series, Miniseries, or Movie? | 2014 | not run | not run |
| 85629 | In what year did Mary-Kate Olsen and Ashley Olsen win the Young Artist Award for Best Young Actor/Actress Under Five Years of Age? | 1990 | not run | not run |
| 50853 | Holy Roman Emperor |  | not run | not run |
| 48129 | Alsace |  | not run | not run |
| 166410 | Yunnan |  | not run | not run |
| 959699 | The Doctor |  | not run | not run |
| 160112 | Order of Canada |  | not run | not run |
| 85099 | In what year did Watford F.C. first have Puma as their kit manufacturer? | 2012 | not run | not run |
| 25534 | Romanian language |  | not run | not run |
| 29369 | Sex organ |  | not run | not run |
| 19525 | Muay Thai |  | not run | not run |
| 3469 | British Virgin Islands |  | not run | not run |
| 8196151 | List of states of Mexico |  | not run | not run |
| 501984 | On what date did the Mexican troops under President General Antonio López de Santa Anna begin their march into San Antonio de Béxar during the Battle of the Alamo? | February 23, 1836 | not run | not run |
| 142715 | Emirates (airline) |  | not run | not run |
| 15147 | On what month, day, and year was the International Olympic Committee formed? | June 23, 1894 | not run | not run |
| 27680 | Supernova |  | not run | not run |
| 81024 | Pan Am |  | not run | not run |
| 21132373 | In what year did Jeff Goldblum perform in the play "The Pillowman" at the Booth Theatre on Broadway? | 2005 | not run | not run |
| 20596557 | Watermelon |  | not run | not run |
| 32498 | Volume |  | not run | not run |
| 8397 | Danny Elfman |  | not run | not run |
| 97851 | Australian Open |  | not run | not run |
| 6967012 | In what year did Seth Green first appear in the film "Austin Powers: International Man of Mystery"? | 1997 | not run | not run |
| 45371 | On what month, day, and year did Dominique Baudis end his term as mayor of Toulouse? | January 23, 2001 | not run | not run |
| 63503 | Duluth, Minnesota |  | not run | not run |
| 178796 | In what year was the Saskatoon Hilltops Canadian football junior club established? | 1947 | not run | not run |
| 150473 | Shreveport, Louisiana |  | not run | not run |
| 25336 | Quantum entanglement |  | not run | not run |
| 7043 | Chemical formula |  | not run | not run |
| 11472953 | In what year did Toni Kroos score the highest number of goals for the Germany national team according to the appearances and goals by national team and year table? | 2014 | not run | not run |
| 18823 | Mary Pickford |  | not run | not run |
| 309661 | Gauteng |  | not run | not run |
| 5070109 | Spanish Armada |  | not run | not run |
| 21272 | Neutron |  | not run | not run |
| 542300 | Ilkhanate |  | not run | not run |
| 129368 | In what year did the film Rain Man win the Academy Award for Best Picture? | 1989 | not run | not run |
| 21438242 | Lava |  | not run | not run |
| 4497 | Bugatti |  | not run | not run |
| 2822936 | In what year was the soundtrack album for Titanic: Music from the Motion Picture released? | 1997 | not run | not run |
| 508593 | In what year did Rip Torn appear in the television film "Sophia Loren: Her Own Story"? | 1980 | not run | not run |
| 80666 | Upanishads |  | not run | not run |
| 225073 | He (pronoun) |  | not run | not run |
| 140537 | In what year was the 2021 reissue of the twelfth and final studio album by the English rock band the Beatles charted on the Australian Albums (ARIA) chart? | 2021 | not run | not run |
| 50030 | La Marseillaise |  | not run | not run |
| 44944 | 'Ndrangheta |  | not run | not run |
| 69442 | Waterfall |  | not run | not run |
| 931406 | Royal Canadian Air Force |  | not run | not run |
| 236850 | Conflict of interest |  | not run | not run |
| 67135 | Tatarstan |  | not run | not run |
| 428979 | Michael Vick |  | not run | not run |
| 25721 | What month, day, and year was the Blu-ray release date for Series XI of Red Dwarf in Region A? | November 8, 2016 | not run | not run |
| 81726 | Santa Cruz, California |  | not run | not run |
| 30148 | Tokelau |  | not run | not run |
| 23087494 | Lily Collins |  | not run | not run |
| 6127993 | UTC+00:00 |  | not run | not run |
| 566405 | Saltwater crocodile |  | not run | not run |
| 341111 | List of islands in the Pacific Ocean |  | not run | not run |
| 167975 | In what year did Peter Ustinov begin his term as Chancellor of the University of Durham? | 1992 | not run | not run |
| 26365423 | On what date did Hawaii Five-0 win the People's Choice Award for Favorite New TV Drama? | January 5, 2011 | not run | not run |
| 52052 | Mainland Southeast Asia |  | not run | not run |
| 12104 | Guglielmo Marconi |  | not run | not run |
| 228592 | Lottery |  | not run | not run |
| 804161 | TotalEnergies |  | not run | not run |
| 58733 | Staffordshire |  | not run | not run |
| 17015903 | In what year was Abduwali Muse convicted and sentenced to prison for his role in the hijacking of the MV Maersk Alabama? | 2011 | not run | not run |
| 44731 | Calcium carbonate |  | not run | not run |
| 150374 | Self-harm |  | not run | not run |
| 17166443 | Isles of Scilly |  | not run | not run |
| 11062 | Friction |  | not run | not run |
| 70962 | Hawaiʻi (island) |  | not run | not run |
| 647757 | United States women's national soccer team |  | not run | not run |
| 18436536 | In what year did the film 2012 win the Satellite Award for Best Visual Effects? | 2009 | not run | not run |
| 54060 | In what year did the parliamentary constituency of St Marylebone change to Westminster North? | 1983 | not run | not run |
| 22080893 | In what year did Ellie Kemper play the role of Becca in the film Bridesmaids? | 2011 | not run | not run |
| 29963050 | On what month, day, and year was the final match of the 58th season of Europe's premier club football tournament organised by UEFA held at Wembley Stadium, London? | May 25, 2013 | not run | not run |
| 3155 | Lockheed AC-130 |  | not run | not run |
| 15530283 | List of paraphilias |  | not run | not run |
| 182553 | Plovdiv |  | not run | not run |
| 50556 | On what month, day, and year was King James V, son of James IV, born? | April 10, 1512 | not run | not run |
| 44757 | In what year did the University of California, Irvine become a member of the Association of American Universities? | 1996 | not run | not run |
| 5681823 | Knight's Cross of the Iron Cross |  | not run | not run |
| 2184258 | Nandamuri Balakrishna |  | not run | not run |
| 206481 | In what historical period were the Elamite god Humban worshiped by Persians? | early Achaemenid times | not run | not run |
| 483492 | In what year did Martin Freeman perform in the play titled 'Richard III' at Trafalgar Studios? | 2014 | not run | not run |
| 46380 | Coaxial cable |  | not run | not run |
| 665172 | Las Vegas Valley |  | not run | not run |
| 29408 | Samuel Taylor Coleridge |  | not run | not run |
| 989692 | In what year did Peter Sarsgaard perform the role of Hamlet at the Classic Stage Company? | 2015 | not run | not run |
| 14349 | Harmonica |  | not run | not run |
| 10223 | Estonian language |  | not run | not run |
| 278513 | In what year did Adam West play the role of Bruce Wayne / Batman in the film titled 'Batman'? | 1966 | not run | not run |
| 28135 | Slovene language |  | not run | not run |
| 1053453 | In what year did Garth Lagerwey begin his tenure as general manager of Real Salt Lake? | 2007 | not run | not run |
| 518192 | Need for Speed |  | not run | not run |
| 43591321 | Asus |  | not run | not run |
| 26865 | List of leaders of the Soviet Union |  | not run | not run |
| 173652 | Hemorrhoid |  | not run | not run |
| 81088 | List of cities and counties in Virginia |  | not run | not run |
| 457055 | Comune |  | not run | not run |
| 618770 | In what year did Dianne Wiest perform the role of Cassandra in the play Agamemnon at the Delacorte Theatre? | 1977 | not run | not run |
| 166215 | In what year was the Faculty of Pharmaceutical Sciences at the University of Tokyo founded? | 1958 | not run | not run |
| 525314 | In what year was the film nominated by the American Film Institute for its Top 10 Animation Films list? | 2008 | not run | not run |
| 17627213 | List of music recording certifications |  | not run | not run |
| 313646 | Western Cape |  | not run | not run |
| 145415 | Division (military) |  | not run | not run |
| 37284 | Brain tumor |  | not run | not run |
| 186191 | T-72 |  | not run | not run |
| 267235 | Super Rugby |  | not run | not run |
| 55023 | In what year did the Jin dynasty begin? | 1115 | not run | not run |
| 6313 | Classical element |  | not run | not run |
| 46709 | County Cork |  | not run | not run |
| 218232 | ITunes Store |  | not run | not run |
| 204971 | Historic counties of England |  | not run | not run |
| 113288 | In what year was the FK Vojvodina football club founded? | 1914 | not run | not run |
| 57708 | Topeka, Kansas |  | not run | not run |
| 532125 | UEFA Euro 2000 |  | not run | not run |
| 54761 | In what year was the report published that identified Wang and Li as the most common Chinese surnames, each shared by over 100 million people in China? | 2019 | not run | not run |
| 3201113 | In what year did Eric Dane first appear in the television series Grey's Anatomy? | 2006 | not run | not run |
| 1118679 | In what year did Domino's Pizza begin sponsoring the British soap opera Hollyoaks? | 2015 | not run | not run |
| 7199 | List of cat breeds |  | not run | not run |
| 33883 | Wade–Giles |  | not run | not run |
| 6787 | Chiapas |  | not run | not run |
| 8724 | Doppler effect |  | not run | not run |
| 164225 | Japanese name |  | not run | not run |
| 751489 | Summit |  | not run | not run |
| 44723 | Printing |  | not run | not run |
| 14985 | In what year did Edward Pearson Warner begin his term as president of the International Civil Aviation Organization council? | 1947 | not run | not run |
| 66575 | Nutrient |  | not run | not run |
| 598459 | In what year did Greg Kinnear play the role of John F. Kennedy in the television series The Kennedys? | 2011 | not run | not run |
| 54476844 | Boolean algebra |  | not run | not run |
| 3364 | Bit |  | not run | not run |
| 16858 | Knights of Columbus |  | not run | not run |
| 143062 | In what year did the general election occur after which West Sussex has been represented by three Conservative, three Labour, and three Liberal Democrat Members of Parliament? | 2024 | not run | not run |
| 143100 | Provinces of Ireland |  | not run | not run |
| 29359 | Sinhalese people |  | not run | not run |
| 146607 | Al-Ghazali |  | not run | not run |
| 49681637 | Mindhunter (TV series) |  | not run | not run |
| 19947 | Mannerism |  | not run | not run |
| 332961 | Greater Sudbury |  | not run | not run |
| 269645 | In what year did Tim Conway win the Primetime Emmy Award for Outstanding Individual Performance in a Variety or Music Program for the first time? | 1973 | not run | not run |
| 745082 | In what year did Lee Majors play the role of Frank Harbin in the film Strait-Jacket? | 1964 | not run | not run |
| 440038 | 1918 United Kingdom general election |  | not run | not run |
| 500004 | On-Line Encyclopedia of Integer Sequences |  | not run | not run |
| 70566 | Valparaíso |  | not run | not run |
| 638381 | In what year did Charles Durning make his Broadway debut in the play Poor Bitos? | 1964 | not run | not run |
| 206997 | In what year did Hermann zu Hohenlohe-Langenburg begin his term as Imperial Governor of Alsace–Lorraine? | 1894 | not run | not run |
| 477968 | In the sexagenary cycle, what is the designation of the 17th term? | Metal Dragon | not run | not run |
| 77783 | Guildford |  | not run | not run |
| 1690376 | List of legal entity types by country |  | not run | not run |
| 227690 | Kei car |  | not run | not run |
| 154809 | McDonnell Douglas |  | not run | not run |
| 21140 | Noble gas |  | not run | not run |
| 141390 | In what year did Gordie Howe receive the NHL Lifetime Achievement Award? | 2008 | not run | not run |
| 1099413 | Orbital eccentricity |  | not run | not run |
| 344462 | In what year did cross country running first appear in the Olympic Games? | 1912 | not run | not run |
| 2471540 | Security hacker |  | not run | not run |
| 371516 | In what century was the Glauberg kings graves site in Wetteraukreis, Hesse dated to? | 5th century BC | not run | not run |
| 293632 | In what year was the subgenre popularity data for romance novels in the United States recorded? | 2006 | not run | not run |
| 31923 | University of California, Santa Cruz |  | not run | not run |
| 27123 | Saarland |  | not run | not run |
| 304691 | Larry Brown (basketball) |  | not run | not run |
| 13830 | Hastings |  | not run | not run |
| 8254 | In what year was the thermionic diode invented by John Ambrose Fleming? | 1904 | not run | not run |
| 256305 | Santa Catarina (state) |  | not run | not run |
| 3270829 | List of Dragonlance novels |  | not run | not run |
| 2839975 | Locus (genetics) |  | not run | not run |
| 62633 | Les Invalides |  | not run | not run |
| 17733874 | Potential enlargement of the European Union |  | not run | not run |
| 76165 | On what month, day, and year was the Pontiac automobile brand officially declared defunct? | October 31, 2010 | not run | not run |
| 89276 | Sprint (running) |  | not run | not run |
| 598491 | In what year did Timothy Hutton star in the film Ordinary People? | 1980 | not run | not run |
| 268075 | In what year were the QS World University Rankings by broad subject area published that included the University of Hong Kong's world ranks? | 2023 | not run | not run |
| 592311 | On what month, day, and year was the International Tennis Federation formed? | March 1, 1913 | not run | not run |
| 172911 | Nuclear weapon design |  | not run | not run |
| 357520 | Disney anthology television series |  | not run | not run |
| 405944 | Time complexity |  | not run | not run |
| 412827 | Guanajuato |  | not run | not run |
| 188497 | Femur |  | not run | not run |
| 372315 | Moscow Oblast |  | not run | not run |
| 443459 | In what year did Miranda Otto perform the role of Nora Helmer in the play A Doll’s House with the Sydney Theatre Company? | 2002 | not run | not run |
| 867865 | Warsaw Ghetto Uprising |  | not run | not run |
| 56099 | Red dwarf |  | not run | not run |
| 847879 | Age of the universe |  | not run | not run |
| 173109 | Warped Tour |  | not run | not run |
| 1171713 | Cerezo Osaka |  | not run | not run |
| 26288711 | Coulomb's law |  | not run | not run |
| 59742 | Menorca |  | not run | not run |
| 17643 | Lavandula |  | not run | not run |
| 77260 | Olmecs |  | not run | not run |
| 26897 | Spice |  | not run | not run |
| 59733 | Hexagon |  | not run | not run |
| 24795 | Private (rank) |  | not run | not run |
| 20491903 | Velocity |  | not run | not run |
| 505173 | NAC Breda |  | not run | not run |
| 31039 | Turboprop |  | not run | not run |
| 2517159 | In what year did Mike Bobo previously serve as an Offensive Analyst for Georgia before becoming the Offensive coordinator / quarterbacks? | 2022 | not run | not run |
| 963887 | In what year was the University of South Carolina founded? | 1801 | not run | not run |
| 137193 | St. George, Utah |  | not run | not run |
| 577473 | On what month, day, and year was All India Radio officially launched? | June 8, 1936 | not run | not run |
| 1787105 | Animal sexual behaviour |  | not run | not run |
| 32551521 | FIFA eligibility rules |  | not run | not run |
| 58685 | Hypothalamus |  | not run | not run |
| 1069583 | Dattatreya |  | not run | not run |
| 56668 | Apricot |  | not run | not run |
| 4595410 | 1970 United States census |  | not run | not run |
| 333199 | SkyTeam |  | not run | not run |
| 34062 | WAV |  | not run | not run |
| 782140 | The Shard |  | not run | not run |
| 104944 | On what month, day, and year was Charles XII of Sweden born? | June 17, 1682 | not run | not run |
| 34382035 | Phases of clinical research |  | not run | not run |
| 320965 | Pennsylvania Railroad |  | not run | not run |
| 379971 | In what year did the album In Utero achieve its peak chart positions listed in the weekly chart performance table? | 1993 | not run | not run |
| 10328596 | List of Unicode characters |  | not run | not run |
| 296565 | Steve Young |  | not run | not run |
| 65508 | Great Seal of the United States |  | not run | not run |
| 151069 | On what month, day, and year was Maximilian II, Holy Roman Emperor, born? | July 31, 1527 | not run | not run |
| 72227 | In what year did Joyce list the general indication of grading rules for typical Western plywood grades? | 1970 | not run | not run |
| 11315968 | Youth Olympic Games |  | not run | not run |
| 430074 | In what century did Jarudism take over as the dominant current among Zaydis according to the theological distinctions between Batri and Jarudi? | 9th century | not run | not run |
| 34050 | Warrant officer |  | not run | not run |
| 396394 | National Assembly of Quebec |  | not run | not run |
| 845294 | Service star |  | not run | not run |
| 1780815 | Radius |  | not run | not run |
| 89514 | New London, Connecticut |  | not run | not run |
| 337740 | In what year did Bram Stoker's Dracula (1992 film) win the Academy Award for Best Costume Design? | 1993 | not run | not run |
| 1286819 | Grand Tour (cycling) |  | not run | not run |
| 3977980 | Women's Cricket World Cup |  | not run | not run |
| 4836072 | In what year did the film My Fair Lady win the Academy Award for Best Picture? | 1965 | not run | not run |
| 59038 | Fourier series |  | not run | not run |
| 310845 | In what year did Michel Doukeris become the leader of the Anheuser-Busch subsidiary? | 2018 | not run | not run |
| 409309 | Alcohol by volume |  | not run | not run |
| 745601 | In what year did Valerie Bertinelli appear in the film titled 'Number One with a Bullet'? | 1987 | not run | not run |
| 1978269 | In what year was the American publishing house Alfred A. Knopf, Inc. founded? | 1915 | not run | not run |
| 543312 | The Mars Volta |  | not run | not run |
| 1234326 | Gmina |  | not run | not run |
| 377819 | Pagliacci |  | not run | not run |
| 424342 | Pepperdine University |  | not run | not run |
| 2043791 | Persepolis F.C. |  | not run | not run |
| 8192 | Detective fiction |  | not run | not run |
| 222254 | Tamaulipas |  | not run | not run |
| 21438575 | Bass (voice type) |  | not run | not run |
| 4651 | Beta decay |  | not run | not run |
| 244481 | Kaifeng |  | not run | not run |
| 830589 | Bohemian F.C. |  | not run | not run |
| 118474 | In what century were volumes 97 to 130 of the Patrologia Latina published according to Baronius? | 9th century | not run | not run |
| 7632 | Cerebrospinal fluid |  | not run | not run |
| 517620 | On what month, day, and year did Tom Seaver pitch a no-hitter? | June 16, 1978 | not run | not run |
| 77655 | Louis XII |  | not run | not run |
| 199306 | VX (nerve agent) |  | not run | not run |
| 8707 | In what year was the German automotive company DKW founded? | 1916 | not run | not run |
| 70841 | City status in the United Kingdom |  | not run | not run |
| 24516 | In what year did Polybius write the Histories that mention the Polybius square cipher? | c. 200 – c. 118 BC | not run | not run |
| 322010 | In what year was the ARWU global ranking of Queen's University Belfast recorded as between 301 and 400? | 2025 | not run | not run |
| 19811 | Murray River |  | not run | not run |
| 548229 | Lili Taylor |  | not run | not run |
| 6535529 | List of airports in Alberta |  | not run | not run |
| 47238088 | List of municipalities in West Virginia |  | not run | not run |
| 94320 | Virus classification |  | not run | not run |
| 6355 | Chloroplast |  | not run | not run |
| 28833 | Sir Gawain and the Green Knight |  | not run | not run |
| 302617 | León, Spain |  | not run | not run |
| 7910935 | The Penguin Guide to Jazz |  | not run | not run |
| 3540710 | National Register of Historic Places listings in Wisconsin |  | not run | not run |
| 88446 | List of Portuguese monarchs |  | not run | not run |
| 309769 | Spanish dollar |  | not run | not run |
| 1117292 | Toyota Yaris |  | not run | not run |
| 111852 | Moline, Illinois |  | not run | not run |
| 10467798 | 1989 Soviet census |  | not run | not run |
| 456601 | On what month, day, and year was the Academy Award ceremony held where The Fly won Best Makeup? | March 30, 1987 | not run | not run |
| 188537 | In what year was Volume IV of the Dictionary of American Naval Fighting Ships published? | 1969 | not run | not run |
| 31475895 | Development Panel of ICC Umpires |  | not run | not run |
| 1144172 | On what month, day, and year was the Sideways soundtrack album by Rolfe Kent released? | October 12, 2004 | not run | not run |
| 8215253 | A roads in Zone 4 of the Great Britain numbering scheme |  | not run | not run |
| 4109042 | In what year were the signaling pathways based on receptor families that control gene activity, such as Frizzled and Receptor Tyrosine Kinase pathways, first overviewed in the referenced sources? | 2000 | not run | not run |
| 252781 | List of governors of Pennsylvania |  | not run | not run |
| 24387628 | 2010 Russian census |  | not run | not run |
| 2232427 | Suzuki Jimny |  | not run | not run |
| 3540772 | National Register of Historic Places listings in Alaska |  | not run | not run |
| 79379 | In what year did the Cal State Northridge Matadors join the Big Sky Conference? | 1996 | not run | not run |
| 117105 | Bay City, Michigan |  | not run | not run |
| 532922 | In what year did the television series St. Elsewhere first air on NBC? | 1982 | not run | not run |
| 80208 | In what year did William Westmoreland become the Superintendent of the United States Military Academy? | 1960 | not run | not run |
| 1217448 | In what month and year did the character Wolverine first appear in comics? | 1974-10 | not run | not run |
| 111579 | Alton, Illinois |  | not run | not run |
| 28161 | List of brightest stars |  | not run | not run |
| 390896 | In what year did Roman Abramovich begin his term as governor of the Chukotka Autonomous Okrug? | 2000 | not run | not run |
| 1077688 | Catechin |  | not run | not run |
| 1582694 | Wisden Cricketers' Almanack |  | not run | not run |
| 900231 | Team America: World Police |  | not run | not run |
| 135478 | Killeen, Texas |  | not run | not run |
| 113190 | Posthumous name |  | not run | not run |
| 180486 | Oshawa |  | not run | not run |
| 217428 | Abitur |  | not run | not run |
| 414741 | In what year was the European Coal and Steel Community established? | 1952 | not run | not run |
| 795554 | Oak leaf cluster |  | not run | not run |
| 82050 | Royal Norwegian Navy |  | not run | not run |
| 812281 | In what year was the main international basketball competition for the senior men's national teams of primarily European countries founded? | 1935 | not run | not run |
| 2801560 | Ocean acidification |  | not run | not run |
| 30871458 | Color index |  | not run | not run |
| 7025 | Cranberry |  | not run | not run |
| 142207 | Singular value decomposition |  | not run | not run |
| 14558843 | Nirvana (Buddhism) |  | not run | not run |
| 183852 | Gifu Prefecture |  | not run | not run |
| 274238 | On what month, day, and year was the United States Department of War removed from the Cabinet? | September 18, 1947 | not run | not run |
| 14856 | Inner product space |  | not run | not run |
| 557097 | In what year was the International Alphabet of Sanskrit Transliteration formalized by the Transliteration Committee of the Geneva Oriental Congress? | 1894 | not run | not run |
| 998780 | Seven Days Battles |  | not run | not run |
| 18952991 | Gila monster |  | not run | not run |
| 373452 | What is the frequency of performing the Deva-yajna (homa) sacrifice according to the Kalpa Sutras? | Daily | not run | not run |
| 42093526 | In what year did the first season of Unbreakable Kimmy Schmidt receive seven Primetime Emmy Award nominations? | 2015 | not run | not run |
| 505086 | In what year was the Dungeons & Dragons module titled 'The Elixir of Life' published? | 1983 | not run | not run |
| 2305669 | List of most expensive films |  | not run | not run |
| 18582 | In what year did the BBB party first win seats in the States-Provincial elections in Limburg (Netherlands)? | 2023 | not run | not run |
| 22959267 | List of Latin phrases (V) |  | not run | not run |
| 282299 | Muzzle velocity |  | not run | not run |
| 1019389 | Lund |  | not run | not run |
| 122386 | Starkville, Mississippi |  | not run | not run |
| 496361 | As of what month, day, and year is the student body composition data for Sacred Heart University reported? | May 2, 2022 | not run | not run |
| 127579 | Peekskill, New York |  | not run | not run |
| 2114 | IBM AIX |  | not run | not run |
| 472779 | Arkhangelsk Oblast |  | not run | not run |
| 310169 | Indian philosophy |  | not run | not run |
| 40056 | On what exact date was ski jumping first played by Olaf Rye at Eidsberg church in Norway? | November 22, 1808 | not run | not run |
| 58278 | In what year was the former Kansas County in Kansas dissolved into Seward County? | 1883 | not run | not run |
| 55417368 | 2016 Australian census |  | not run | not run |
| 31958 | United Nations Economic and Social Council |  | not run | not run |
| 46251870 | Geographical distribution of French speakers |  | not run | not run |
| 1721369 | On what month, day, and year did The Ultimate Fighter television series first release? | January 17, 2005 | not run | not run |
| 145478 | TIFF |  | not run | not run |
| 5802344 | Baseball in Cuba |  | not run | not run |
| 99306 | College Park, Maryland |  | not run | not run |
| 66057 | On what month, day, and year was the DuMont Television Network officially launched? | August 15, 1946 | not run | not run |
| 204019 | Notting Hill (film) |  | not run | not run |
| 388193 | Air Koryo |  | not run | not run |
| 9413800 | Guangzhou F.C. |  | not run | not run |
| 1478772 | In what year did the New England Patriots begin their longest streak of consecutive playoff appearances? | 2009 | not run | not run |
| 437808 | Bank of Baroda |  | not run | not run |
| 43221 | In what year was Dichlorodifluoromethane banned in all countries in compliance with the Montreal Protocol? | 1987 | not run | not run |
| 864183 | In what year did the film Indecent Proposal win the BMI Film Music Award for John Barry? | 1993 | not run | not run |
| 155650 | Fluoride |  | not run | not run |
| 224021 | Hidalgo (state) |  | not run | not run |
| 62305884 | Ōshima Strait |  | not run | not run |
| 3135637 | Gut microbiota |  | not run | not run |
| 7404943 | Jamie Murray |  | not run | not run |
| 497311 | Cayenne |  | not run | not run |
| 212068 | In what year did Dario Argento act as a paramedic in the film Innocent Blood? | 1992 | not run | not run |
| 1219810 | Historic preservation |  | not run | not run |
| 2723793 | In what year was the sire Halo, ancestor of Sunday Silence, born? | 1969 | not run | not run |
| 330869 | Rotorua |  | not run | not run |
| 32237 | UMTS |  | not run | not run |
| 183477 | Iwate Prefecture |  | not run | not run |
| 5300318 | Districts of the Czech Republic |  | not run | not run |
| 182283 | Miles per hour |  | not run | not run |
| 58858 | Regions of New Zealand |  | not run | not run |
| 154708 | List of national legal systems |  | not run | not run |
| 1038535 | State of the Teutonic Order |  | not run | not run |
| 364879 | In what year did Billy West first voice the character Cecil in the television show The New Adventures of Beany and Cecil? | 1988 | not run | not run |
| 19869 | Massachusetts Bay Transportation Authority |  | not run | not run |
| 48922 | Leadville, Colorado |  | not run | not run |
| 65666080 | In what year did the 125th season of the Australian Football League (AFL) take place? | 2021 | not run | not run |
| 806560 | Contemporary philosophy |  | not run | not run |
| 2500686 | Magnitude (astronomy) |  | not run | not run |
| 844184 | Malwa |  | not run | not run |
| 4644269 | On what month, day, and year did the 24th annual WrestleMania event take place? | March 30, 2008 | not run | not run |
| 5964336 | Fastest lap |  | not run | not run |
| 11037 | Freyr |  | not run | not run |
| 639573 | Dry Tortugas National Park |  | not run | not run |
| 21391870 | In what year did Alan Turing prove that the halting problem is undecidable? | 1937 | not run | not run |
| 314803 | In what year was the University of Zurich ranked 59th in the ARWU World university rankings? | 2023 | not run | not run |
| 32099 | In what year was the University of Manitoba founded as the first university in Western Canada? | 1877 | not run | not run |
| 1088294 | Demographics of sexual orientation |  | not run | not run |
| 1782201 | Kleshas (Buddhism) |  | not run | not run |
| 108346 | Beale Air Force Base |  | not run | not run |
| 45032 | Dordogne |  | not run | not run |
| 588111 | In what year did the Rs. 10/- coin of the official currency of the Islamic Republic of Pakistan first enter circulation? | 2016 | not run | not run |
| 174706 | Laplace operator |  | not run | not run |
| 1189137 | Joe McCarthy (baseball manager) |  | not run | not run |
| 922245 | Swimming at the Summer Olympics |  | not run | not run |
| 18308 | Lanthanide |  | not run | not run |
| 83324 | On what month, day, and year did Jim Bunning pitch a perfect game? | June 21, 1964 | not run | not run |
| 10017154 | In what year did the Indiana Hoosiers men's basketball team win the NCAA National Championship by defeating Michigan in the final game? | 1976 | not run | not run |
| 3790938 | Western theater of the American Civil War |  | not run | not run |
| 2019918 | List of NFL Most Valuable Player awards |  | not run | not run |
| 4557237 | List of solar eclipses in the 21st century |  | not run | not run |
| 34417 | Zero-sum game |  | not run | not run |
| 999303 | According to the USGA Handicap System overview table, when a golfer has submitted 11 or 12 rounds, how many lowest differentials are used to calculate the handicap index? | lowest 4 | not run | not run |
| 2510506 | Indo-Aryan migrations |  | not run | not run |
| 82022 | Merced County, California |  | not run | not run |
| 5050 | In what year did Bill Bryson begin his term as Chancellor of Durham University? | 2005 | not run | not run |
| 9938623 | In what year did Michelle O'Neill begin serving as Vice President of Sinn Féin? | 2018 | not run | not run |
| 317435 | In what year was the Finnish Air Force founded? | 1918 | not run | not run |
| 524875 | Voiced postalveolar fricative |  | not run | not run |
| 74160 | In what year did Kevin Sorbo play the role of Kull in the film Kull the Conqueror? | 1997 | not run | not run |
| 2140677 | In what year did the rivalry known as the Battle of the Birds between Sydney Roosters and Manly Warringah Sea Eagles begin? | 1947 | not run | not run |
| 839943 | Bone fracture |  | not run | not run |
| 18424 | In what years were the labia and other genital structures of 50 women measured in the study conducted by the Department of Gynaecology at Elizabeth Garrett Anderson Hospital in London? | 2003 to 2004 | not run | not run |
| 287264 | On what date did NORAD propose the adoption of the readiness conditions of the Joint Chiefs of Staff system? | January 12, 1966 | not run | not run |
| 82075 | Santa Cruz County, California |  | not run | not run |
| 1439959 | In what century did Prudentius write the poem Psychomachia that allegorically represented Christian morality as a struggle between seven sins and seven virtues? | 5th century | not run | not run |
| 3775531 | On what month, day, and year was the final match of the 1994–95 UEFA Champions League held at Ernst-Happel-Stadion in Vienna? | May 24, 1995 | not run | not run |
| 3253221 | African Games |  | not run | not run |
| 512470 | Rubber band |  | not run | not run |
| 579089 | In what year was the ECAC Hockey conference founded? | 1961 | not run | not run |
| 30931401 | Dutch Caribbean |  | not run | not run |
| 145612 | Ludwigshafen |  | not run | not run |
| 41920 | Compact Disc Digital Audio |  | not run | not run |
| 448061 | Isfahan province |  | not run | not run |
| 109566 | Winter Park, Florida |  | not run | not run |
| 251405 | Charlestown, Boston |  | not run | not run |
| 27884299 | Danville, Illinois |  | not run | not run |
| 1073488 | In what year did Keeley Browse win the Sir Terry Wogan Fundraiser of the Year Award? | 2018 | not run | not run |
| 571630 | Venus figurine |  | not run | not run |
| 2648955 | List of weapons in the American Civil War |  | not run | not run |
| 4601182 | Senegalese Football Federation |  | not run | not run |
| 213948 | On what month, day, and year was the Group of 77 formed? | June 15, 1964 | not run | not run |
| 152333 | Provinces of Belgium |  | not run | not run |
| 51963 | In what year did Steinway & Sons acquire the company Louis Renner GmbH? | 2019 | not run | not run |
| 434937 | On what month, day, and year was the title King of Italy officially formed? | September 4, 476 | not run | not run |
| 45186 | In what year was the Utah Flash basketball team established? | 2007 | not run | not run |
| 545518 | In what year did Indiana win its first NCAA Division I men's soccer tournament championship? | 1982 | not run | not run |
| 1908748 | Vehicle registration plates of Poland |  | not run | not run |
| 306966 | Kataeb Party |  | not run | not run |
| 7349689 | Satellite Catalog Number |  | not run | not run |
| 404595 | In what year did the NCAA Division I Football Championship first take place at Paulson Stadium in Statesboro, Georgia? | 1989 | not run | not run |
| 179573 | Krefeld |  | not run | not run |
| 58576 | Lawrence Welk |  | not run | not run |
| 457235 | Helmand Province |  | not run | not run |
| 8802070 | List of major commands of the United States Air Force |  | not run | not run |
| 502038 | Question |  | not run | not run |
| 24577701 | Kent, Ohio |  | not run | not run |
| 231676 | Skirt |  | not run | not run |
| 227335 | In what year did Olivia Hussey play the role of Mary, Mother of Jesus in the miniseries Jesus of Nazareth? | 1977 | not run | not run |
| 116362 | Towson, Maryland |  | not run | not run |
| 6793142 | In what year was the Niigata Albirex BB basketball club established? | 2000 | not run | not run |
| 4668 | Binomial coefficient |  | not run | not run |
| 203688 | At what historical time of day is the Sixth Hour (Sext) service traditionally held according to the daily cycle of canonical hours? | At noon | not run | not run |
| 448514 | Tom Arnold (actor) |  | not run | not run |
| 6793346 | Kumamoto |  | not run | not run |
| 753103 | Chicago Police Department |  | not run | not run |
| 832492 | In what month and year did the Radio Free Asia Tibetan language service launch? | 1996-12 | not run | not run |
| 458469 | In what year did the Progressive Conservative Association of Alberta begin its uninterrupted run as the governing party of Alberta? | 1971 | not run | not run |
| 239964 | F Sharp (programming language) |  | not run | not run |
| 42106513 | Batman: Arkham Knight |  | not run | not run |
| 275932 | County Louth |  | not run | not run |
| 118790 | Royal Oak, Michigan |  | not run | not run |
| 70748 | On what month and day is the birthday of King Willem-Alexander, also known as Koningsdag (King's Day), officially celebrated according to the Dutch flag-flying days? | 27 April | not run | not run |
| 148730 | In what year was the Cheshire Cat as illustrated by John Tenniel first published? | 1865 | not run | not run |
| 81600 | List of counties in Colorado |  | not run | not run |
| 634316 | Prednisolone |  | not run | not run |
| 57853 | Pierre, South Dakota |  | not run | not run |
| 714452 | Chronic kidney disease |  | not run | not run |
| 191300 | Glossary of Buddhism |  | not run | not run |
| 239528 | What month, day, and year did the Founding Conference of the Independent Labour Party take place? | January 14, 1893 | not run | not run |
| 646771 | Clear Channel memorandum |  | not run | not run |
| 91287 | Manassas, Virginia |  | not run | not run |
| 64100 | Serif |  | not run | not run |
| 220713 | Kumamoto Prefecture |  | not run | not run |
| 82208 | International Mathematical Olympiad |  | not run | not run |
| 5596305 | Sushruta Samhita |  | not run | not run |
| 4483507 | 1820 United States census |  | not run | not run |
| 452226 | Utah Territory |  | not run | not run |
| 701802 | On what month, day, and year did Chip Roy become chair of the subcommittee on The Constitution and Limited Government in the 118th Congress? | October 26, 2023 | not run | not run |
| 50387 | Containerization |  | not run | not run |
| 431272 | Commissioner |  | not run | not run |
| 2467 | Aargau |  | not run | not run |
| 26541290 | In what year was the Bundesverband Musikindustrie formed? | 2007 | not run | not run |
| 632929 | What month, day, and year was the first episode of the first season of Joey originally released? | September 9, 2004 | not run | not run |
| 58062027 | On what dates was the 2018 World Series played? | October 23–28, 2018 | not run | not run |
| 76216 | List of regions of Quebec |  | not run | not run |
| 1480126 | Underwater habitat |  | not run | not run |
| 14381 | Hamiltonian (quantum mechanics) |  | not run | not run |
| 880497 | Linoleic acid |  | not run | not run |
| 83171 | Laon |  | not run | not run |
| 2667490 | Ashton Gate (stadium) |  | not run | not run |
| 2065189 | 1995 NBA draft |  | not run | not run |
| 551604 | Pee-wee Herman |  | not run | not run |
| 19836 | Molecular mass |  | not run | not run |
| 208144 | X chromosome |  | not run | not run |
| 372308 | Sakhalin Oblast |  | not run | not run |
| 166004 | Drupal |  | not run | not run |
| 171581 | On what month, day, and year were the 65th Academy Awards held? | March 29, 1993 | not run | not run |
| 535649 | List of municipalities in Louisiana |  | not run | not run |
| 41944809 | In what month, day, and year was the 2015 Major League Baseball draft held to assign amateur baseball players to MLB teams? | June 8, 2015 | not run | not run |
| 237014 | Quorum |  | not run | not run |
| 17484978 | What is the time period defined for the initial phase of cold water immersion syndrome known as cold shock? | First 2–3 minutes | not run | not run |
| 75149 | In what year did AZS AJP Gorzów Wielkopolski women's basketball team win the Polish Cup? | 2025 | not run | not run |
| 107991 | Chino, California |  | not run | not run |
| 309257 | Whistler, British Columbia |  | not run | not run |
| 597263 | Near-open front unrounded vowel |  | not run | not run |
| 111021 | Northbrook, Illinois |  | not run | not run |
| 2367141 | 1993 NFL season |  | not run | not run |
| 116732 | Taunton, Massachusetts |  | not run | not run |
| 1741957 | In what year did Wuhan Three Towns win the China League One? | 2021 | not run | not run |
| 3663192 | National Register of Historic Places listings in Bristol County, Massachusetts |  | not run | not run |
| 130832 | Klamath Falls, Oregon |  | not run | not run |
| 6535522 | List of airports in the Northwest Territories |  | not run | not run |
| 1809036 | List of House episodes |  | not run | not run |
| 667977 | In what year was women's basketball first played at Smith College in Massachusetts? | 1892 | not run | not run |
| 1347879 | In what century did Karaikkal Ammaiyar, one of the three female Nayanars, live? | 6th century | not run | not run |
| 3645403 | In what year was the Constitution of the Federal Republic of Nigeria, which assumes a National Assembly consisting of a Senate and a House of Representatives, established? | 1999 | not run | not run |
| 1560673 | In what year did IF Brommapojkarna win the Superettan league for the first time? | 2017 | not run | not run |
| 372988 | Tamil literature |  | not run | not run |
| 329044 | In what year was the Toyota Red Terriers women's softball team established? | 1948 | not run | not run |
| 2061310 | North Central Railway zone |  | not run | not run |
| 23200639 | On what month, day, and year was the 2010 Major League Baseball draft held? | June 7, 2010 | not run | not run |
| 239002 | In what year did BMW make its first entry in the Formula One World Championship? | 1952 | not run | not run |
| 12745881 | On what month, day, and year did Samuel Onunaka Mbakwe take office as Governor of Imo State? | October 1, 1979 | not run | not run |
| 160028 | In what year was the Co-operative Commonwealth Federation founded? | 1932 | not run | not run |
| 1572523 | On-board diagnostics |  | not run | not run |
| 1055466 | In what year did Edward Norton win the Golden Globe Award for Best Supporting Actor for his role in Primal Fear? | 1997 | not run | not run |
| 283824 | In what year was the Malacañang Palace property set aside as the summer residence of the Governor General by royal decrees? | 1847 | not run | not run |
| 28857549 | Third Dynasty of Egypt |  | not run | not run |
| 39709452 | Acceptance of evolution by religious groups |  | not run | not run |
| 181809 | M6 motorway |  | not run | not run |
| 134361 | Aiken, South Carolina |  | not run | not run |
| 252948 | 16th arrondissement of Paris |  | not run | not run |
| 11920264 | Bombardier CRJ100/200 |  | not run | not run |
| 3754242 | List of Volkswagen Group diesel engines |  | not run | not run |
| 530183 | Adirondack Park |  | not run | not run |
| 377611 | Elijah Parish Lovejoy |  | not run | not run |
| 963537 | Gloucester Rugby |  | not run | not run |
| 8910 | In what year was Dean Koontz's novel 'Midnight' nominated for the Bram Stoker Award? | 1989 | not run | not run |
| 2533444 | List of roller coaster rankings |  | not run | not run |
| 1244920 | What month and year was the Dornier 228 introduced? | 1982-07 | not run | not run |
| 8739635 | In what year did the European Parliament election in the United Kingdom, summarized by the post-election groupings of each party, take place? | 2009 | not run | not run |
| 8246804 | A roads in Zone 6 of the Great Britain numbering scheme |  | not run | not run |
| 173290 | Proton Holdings |  | not run | not run |
| 37839 | Ion thruster |  | not run | not run |
| 6018611 | Switzerland–European Union relations |  | not run | not run |
| 272893 | Black-crowned night heron |  | not run | not run |
| 3120845 | In what year was the Australian Football Council (AFC) formed, which later became responsible for the laws of Australian rules football? | 1905 | not run | not run |
| 322808 | List of universities in Switzerland |  | not run | not run |
| 6967081 | In what year did Elisha Scott begin his international football career with the Ireland national football team? | 1920 | not run | not run |
| 7172268 | ISU Junior Grand Prix of Figure Skating |  | not run | not run |
| 240945 | In what year did Anne Meara perform the role of Nurse in the Joseph Papp Public Theater production of Romeo and Juliet? | 1988 | not run | not run |
| 335537 | On what month and year was the final list of referees for the third edition of the FIFA Women's World Cup published? | 1999-04 | not run | not run |
| 2311040 | In what year did the song "Another Day in Paradise" reach its peak chart positions listed in the weekly charts table? | 1989 | not run | not run |
| 138007 | Kirkland, Washington |  | not run | not run |
| 4433643 | National Register of Historic Places listings in Philadelphia |  | not run | not run |
| 1460 | Asgard |  | not run | not run |
| 1652975 | Appomattox campaign |  | not run | not run |
| 113441 | In what year did Morgan State College begin its presidency under Dwight O.W. Holmes? | 1937 | not run | not run |
| 833671 | In what year did Isaac Norton Rendall begin his presidency at Lincoln University in Pennsylvania? | 1865 | not run | not run |
| 6020545 | Demographics of Africa |  | not run | not run |
| 714729 | Southern England |  | not run | not run |
| 913125 | Anti-German sentiment |  | not run | not run |
| 1326920 | Mexican Air Force |  | not run | not run |
| 46231 | Super 8 film |  | not run | not run |
| 660597 | Old Trafford Cricket Ground |  | not run | not run |
| 558550 | Wylie transliteration |  | not run | not run |
| 34099767 | Disability sport classification |  | not run | not run |
| 4846076 | Southwestern China |  | not run | not run |
| 14724846 | In what year did the action comedy TV series Peacemaker first air? | 2022 | not run | not run |
| 82394 | On what month, day, and year did Julio César Chávez lose to Kostya Tszyu for the WBC light welterweight title? | July 29, 2000 | not run | not run |
| 27442274 | In what year was the Major League Baseball draft held that included the supplemental first round picks such as Brian Goodwin and Blake Snell? | 2011 | not run | not run |
| 317860 | On what month, day, and year was Infante Juan, Count of Barcelona, born? | June 20, 1913 | not run | not run |
| 196078 | Lamborghini Murciélago |  | not run | not run |
| 3878 | Biostatistics |  | not run | not run |
| 1532351 | Western Suburbs Magpies |  | not run | not run |
| 1792288 | What month, day, and year did the Soviet Union begin competing at the 1988 Summer Olympics in Seoul, South Korea? | September 17, 1988 | not run | not run |
| 519158 | In what year did Argentina allow same-sex couples to jointly petition for adoption? | 2010 | not run | not run |
| 387766 | Radical Party (France) |  | not run | not run |
| 80566 | Lassen County, California |  | not run | not run |
| 1565499 | Human rights in North Korea |  | not run | not run |
| 171288 | In what year was the basketball club AGE Chalkida BC founded in Chalkida? | 1976 | not run | not run |
| 1057852 | 4-4-0 |  | not run | not run |
| 12641290 | Buddhist logico-epistemology |  | not run | not run |
| 8328 | Divergence |  | not run | not run |
| 578129 | On what month, day, and year did Benjamin Bullivant begin his term as Attorney General of the Dominion of New England? | July 26, 1686 | not run | not run |
| 15717485 | In what year did Fatehgarh Sahib district record 219 road accidents? | 2022 | not run | not run |
| 605671 | Census geographic units of Canada |  | not run | not run |
| 10438439 | Framing (social sciences) |  | not run | not run |
| 584665 | Treaties of Tilsit |  | not run | not run |
| 155269 | Krzysztof Kieślowski |  | not run | not run |
| 370315 | In what year was the Band-e-Amir Dragons cricket club established? | 2013 | not run | not run |
| 39390739 | List of fermented foods |  | not run | not run |
| 746231 | Budget of NASA |  | not run | not run |
| 452048 | In what year was the film 'Sister Act' featuring Kathy Najimy as Sister Mary Patrick released? | 1992 | not run | not run |
| 33084475 | On what month, day, and year was the 2012 Major League Baseball draft held? | June 4, 2012 | not run | not run |
| 90599 | Bas-Rhin |  | not run | not run |
| 791662 | In what year did Ted Levine play the role of Jame 'Buffalo Bill' Gumb in the film The Silence of the Lambs? | 1991 | not run | not run |
| 353303 | Seventeen (American magazine) |  | not run | not run |
| 637662 | Middle Tennessee State University |  | not run | not run |
| 1306531 | Sterling Sharpe |  | not run | not run |
| 11190657 | Sebastian Giovinco |  | not run | not run |
| 19067583 | List of first ladies of the United States |  | not run | not run |
| 11617 | Feynman diagram |  | not run | not run |
| 1182314 | Norwegian Americans |  | not run | not run |
| 4985099 | Boxing at the Summer Olympics |  | not run | not run |
| 2412855 | Administrative divisions of Armenia |  | not run | not run |
| 149283 | Vukovar |  | not run | not run |
| 10497504 | Image sensor format |  | not run | not run |
| 344536 | Hepatitis A |  | not run | not run |
| 7954764 | In what year did Robert M. Rosenzweig begin his term as Executive of the Association of American Universities? | 1983 | not run | not run |
| 1147681 | Topanga, California |  | not run | not run |
| 555625 | 2002–03 NHL season |  | not run | not run |
| 26854708 | In what year did the song "We Are Young" achieve its year-end chart positions listed in the table? | 2012 | not run | not run |
| 298622 | Gorizia |  | not run | not run |
| 956857 | In what year did Jesse B. Thomas first serve as a Class II senator for Illinois in the United States Senate? | 1817 | not run | not run |
| 4530612 | Jürgen Melzer |  | not run | not run |
| 7295539 | In what month and year did Roy Halladay win the American League Pitcher of the Month award for the first time in the 2003 Major League Baseball season? | 2003-05 | not run | not run |
| 276741 | Medium-density fibreboard |  | not run | not run |
| 1929375 | Lacombe, Alberta |  | not run | not run |
| 2457822 | Pressure swing adsorption |  | not run | not run |
| 823229 | Ancient Greek temple |  | not run | not run |
| 114705 | Emporia, Kansas |  | not run | not run |
| 69178 | Bilabial consonant |  | not run | not run |
| 74868 | In what year did The Last Picture Show win the Academy Award for Best Supporting Actor? | 1972 | not run | not run |
| 4952904 | In what year did the United States participate in the Summer Olympics held in London where Ralph Craig was the flag bearer? | 1948 | not run | not run |
| 1292296 | Wellington Regional Stadium |  | not run | not run |
| 8245873 | On what month, day, and year was the High-End Loft Stuff pack for The Sims 3 released in North America? | February 2, 2010 | not run | not run |
| 43610555 | Hamadan |  | not run | not run |
| 1745163 | Interim Biogeographic Regionalisation for Australia |  | not run | not run |
| 1860503 | The Apotheosis of Washington |  | not run | not run |
| 63676175 | Timeline of the COVID-19 pandemic in the United Kingdom (January–June 2020) |  | not run | not run |
| 35052231 | In what year was the restaurant Le Clos des Sens in Annecy first awarded three Michelin stars? | 2019 | not run | not run |
| 5630920 | Russian Railways |  | not run | not run |
| 49800 | In what year were the 2002 Kids' Choice Awards, where Angelina Jolie was nominated for Favorite Butt Kicker, held? | 2002 | not run | not run |
| 1145084 | North Eastern Railway (United Kingdom) |  | not run | not run |
| 50255 | Canadian Alliance |  | not run | not run |
| 54165 | Columbia County, New York |  | not run | not run |
| 185808 | Midland Main Line |  | not run | not run |
| 16987896 | LGBTQ rights in Africa |  | not run | not run |
| 2512977 | Vedic chant |  | not run | not run |
| 719484 | University of New Orleans |  | not run | not run |
| 1873300 | Vale S.A. |  | not run | not run |
| 54338 | Greene County, New York |  | not run | not run |
| 26991526 | In what month and year were the Bamum script characters added to the Unicode standard? | 2009-10 | not run | not run |
| 45893 | As of what month, day, and year was the student body composition data recorded for Michigan Technological University? | May 2, 2022 | not run | not run |
| 2048162 | In what year did the ITF Grand Prix Circuit begin? | 1970 | not run | not run |
| 171191 | On what month and year does Tromsø experience the midnight sun according to the sunrise and sunset times on the 15th of each month? | 2010-06 | not run | not run |
| 46332935 | In what season did Kalvin Phillips score 7 league goals for Leeds United in the Championship? | 2017-2018 | not run | not run |
| 23618017 | Central Texas |  | not run | not run |
| 1045799 | In what year did Bubba Smith first appear in the Police Academy film series? | 1984 | not run | not run |
| 32416559 | List of acts of the Parliament of England from 1485 |  | not run | not run |
| 840505 | List of United States Naval officer designators |  | not run | not run |
| 4629650 | Citation of United Kingdom legislation |  | not run | not run |
| 217809 | In what year did Jane Alexander play the role of Eleanor Bachman in the film The Great White Hope? | 1970 | not run | not run |
| 39147 | Finite difference |  | not run | not run |
| 440479 | Influenza A virus |  | not run | not run |
| 2213051 | As of what month, day, and year is the list of Gainsborough Trinity F.C. club officials current? | November 14, 2023 | not run | not run |
| 180747 | Saga Prefecture |  | not run | not run |
| 663861 | Private network |  | not run | not run |
| 2976107 | In what year did The Italian Job receive a Special Achievement Award at the AAFCA Awards? | 2003 | not run | not run |
| 1907135 | Demographics of Chicago |  | not run | not run |
| 647345 | Chiefs (Super Rugby) |  | not run | not run |
| 15290967 | 2011 Copa América |  | not run | not run |
| 597146 | Close back unrounded vowel |  | not run | not run |
| 2101553 | Saline water |  | not run | not run |
| 493118 | Counties of Lithuania |  | not run | not run |
| 15380778 | QF 12-pounder 12 cwt naval gun |  | not run | not run |
| 259613 | Durham, New Hampshire |  | not run | not run |
| 849500 | Trent Bridge |  | not run | not run |
| 91246 | Spotsylvania County, Virginia |  | not run | not run |
| 5149842 | Kalpa (Vedanga) |  | not run | not run |
| 3898076 | List of AMD graphics processing units |  | not run | not run |
| 70855 | Stadtholder |  | not run | not run |
| 42785028 | Tunceli Province |  | not run | not run |
| 1143974 | Aerial firefighting |  | not run | not run |
| 58346527 | Science Publishing Group |  | not run | not run |
| 56527 | Galactose |  | not run | not run |
| 330691 | Saint-Denis, Réunion |  | not run | not run |
| 467036 | Al Anbar Governorate |  | not run | not run |
| 49860 | Fauna of Australia |  | not run | not run |
| 570255 | Open list |  | not run | not run |
| 322335 | List of rivers of Australia |  | not run | not run |
| 56170 | Otsego County, New York |  | not run | not run |
| 40979 | Crystal oscillator |  | not run | not run |
| 2913030 | Book size |  | not run | not run |
| 1112273 | Heat of combustion |  | not run | not run |
| 1039080 | Kokborok |  | not run | not run |
| 12188699 | Passaddhi |  | not run | not run |
| 54421 | Sex-selective abortion |  | not run | not run |
| 35572416 | Lists of New Testament minuscules |  | not run | not run |
| 3368967 | Rohtak |  | not run | not run |
| 184346 | 1987 Cricket World Cup |  | not run | not run |
| 149270 | Atlantic Wall |  | not run | not run |
| 63542764 | 2020 Tablighi Jamaat COVID-19 hotspot in Delhi |  | not run | not run |
| 265324 | Cost of goods sold |  | not run | not run |
| 597142 | Wetaskiwin |  | not run | not run |
| 306175 | In what year was John Addenbrooke, the founder of Addenbrooke's Hospital, born? | 1680 | not run | not run |
| 53565652 | 2017 Westminster attack |  | not run | not run |
| 1332800 | What month, day, and year did the original release of the TV series Hunter begin? | September 18, 1984 | not run | not run |
| 1566172 | Representation of the People Act 1918 |  | not run | not run |
| 326413 | List of exceptional asteroids |  | not run | not run |
| 2055880 | In what year was Clark International Airport known as Diosdado Macapagal International Airport? | 2003 | not run | not run |
| 6025636 | Plasma protein binding |  | not run | not run |
| 96235 | Jackson County, Illinois |  | not run | not run |
| 205899 | Radula |  | not run | not run |
| 2579172 | Cumann na mBan |  | not run | not run |
| 3698121 | Andreas Seppi |  | not run | not run |
| 772315 | Jack Kramer |  | not run | not run |
| 1364371 | Sinéad Cusack |  | not run | not run |
| 23812915 | Service number (United States Air Force) |  | not run | not run |
| 236906 | On what month, day, and year did Paolo Veronese die in Venice, Venetian Republic? | April 19, 1588 | not run | not run |
| 2288 | Self-propelled anti-aircraft weapon |  | not run | not run |
| 107671 | Rancho Palos Verdes, California |  | not run | not run |
| 9970733 | Fórmula Truck |  | not run | not run |
| 1035700 | In what year did James Avery first appear in the television film Antony and Cleopatra? | 1983 | not run | not run |
| 11685701 | Religion in Finland |  | not run | not run |
| 4039690 | In what year did Maidstone United win the Football Conference? | 1988-1989 | not run | not run |
| 111069 | Wilmette, Illinois |  | not run | not run |
| 576326 | In what year did Pancho Gonzales win the U.S. Pro tournament for the first time? | 1953 | not run | not run |
| 871448 | In what year did Paulina Porizkova appear in the film 'Arizona Dream'? | 1993 | not run | not run |
| 795518 | Vietnam Campaign Medal |  | not run | not run |
| 10184754 | Northeastern Huskies |  | not run | not run |
| 322178 | Thurgau |  | not run | not run |
| 361870 | In what year did the institution currently known as Truman State University adopt its present name? | 1996 | not run | not run |
| 633554 | Football in Brazil |  | not run | not run |
| 4139007 | List of airports in the Lower Mainland |  | not run | not run |
| 326949 | In what year was the Tamil film featuring Silambam titled 'Periya Idathu Penn' released? | 1963 | not run | not run |
| 1125337 | List of common Chinese surnames |  | not run | not run |
| 1066029 | In what age range are students typically in the tenth year of formal or compulsory education? | 15-16 | not run | not run |
| 411056 | In what year did John Ranby serve his first magisterial term as Past Master of the Company of Surgeons? | 1745 | not run | not run |
| 448735 | In what year did the film Elf win the ASCAP award for Top Box Office Films? | 2004 | not run | not run |
| 1130632 | Lost season 1 |  | not run | not run |
| 34524946 | 52nd National Film Awards |  | not run | not run |
| 70076 | Hel (location) |  | not run | not run |
| 48988 | Idaho Springs, Colorado |  | not run | not run |
| 2441 | House of Ascania |  | not run | not run |
| 26333 | Robotech |  | not run | not run |
| 254062 | Mast cell |  | not run | not run |
| 583461 | Stratum (linguistics) |  | not run | not run |
| 67500634 | COVID-19 vaccination in Nigeria |  | not run | not run |
| 2793706 | Club Guaraní |  | not run | not run |
| 4565015 | Wallisian language |  | not run | not run |
| 28925 | Science fiction fandom |  | not run | not run |
| 359531 | President of the Soviet Union |  | not run | not run |
| 4168703 | Kathy Jordan |  | not run | not run |
| 591767 | Nicomachean Ethics |  | not run | not run |
| 33457900 | In what year did the 116th season of the Australian Football League (AFL) take place? | 2012 | not run | not run |
| 50779174 | MacGyver (2016 TV series) |  | not run | not run |
| 5981379 | On what month, day, and year was the UEFA Champions League final played where Real Madrid scored 3 goals against Valencia? | May 24, 2000 | not run | not run |
| 47063538 | Districts of Ivory Coast |  | not run | not run |
| 210617 | List of London Underground stations |  | not run | not run |
| 68039895 | COVID-19 vaccination in Fiji |  | not run | not run |
| 9109 | Diophantine equation |  | not run | not run |
| 1364160 | Ağrı Province |  | not run | not run |
| 22287644 | List of census-designated places in Washington |  | not run | not run |
| 104879 | Redstone Arsenal |  | not run | not run |
| 199884 | Osteopathic medicine in the United States |  | not run | not run |
| 98615 | Danube Delta |  | not run | not run |
| 83205 | Ardennes (department) |  | not run | not run |
| 155025 | Byzantine text-type |  | not run | not run |
| 10009538 | List of Malaysian electoral districts |  | not run | not run |
| 293971 | Friuli |  | not run | not run |
| 208458 | Filoviridae |  | not run | not run |
| 8971 | DEC Alpha |  | not run | not run |
| 742537 | List of airports in Canada (A–B) |  | not run | not run |
| 6495369 | Phillip Island Grand Prix Circuit |  | not run | not run |
| 172052 | Hastings, New Zealand |  | not run | not run |
| 12733279 | On what month and day was the 2003 Major League Baseball draft held? | June 3 and 4, 2003 | not run | not run |
| 23592780 | 10 Gigabit Ethernet |  | not run | not run |
| 5681617 | List of Brazilian federative units by Human Development Index |  | not run | not run |
| 1182568 | Stalag Luft III |  | not run | not run |
| 43285 | Common Object Request Broker Architecture |  | not run | not run |
| 43536 | Beeswax |  | not run | not run |
| 178838 | Ajax, Ontario |  | not run | not run |
| 769781 | Bill Self |  | not run | not run |
| 6752609 | Underwater vision |  | not run | not run |
| 127328 | Montauk, New York |  | not run | not run |
| 12414930 | Oxy–fuel welding and cutting |  | not run | not run |
| 11598240 | On what month and day was the 2004 Major League Baseball draft held? | June 7 and 8, 2004 | not run | not run |
| 16048129 | Operation Priboi |  | not run | not run |
| 2928059 | WMMS |  | not run | not run |
| 424587 | Hingham, Massachusetts |  | not run | not run |
| 33310519 | List of population centres in Alberta |  | not run | not run |
| 21238 | Neva |  | not run | not run |
| 83212 | Aude |  | not run | not run |
| 471987 | Bet365 Stadium |  | not run | not run |
| 93988 | London Borough of Hounslow |  | not run | not run |
| 2122924 | Bunun language |  | not run | not run |
| 64226248 | 365 Days (2020 film) |  | not run | not run |
| 36054427 | List of lieutenant generals in the United States Air Force before 1960 |  | not run | not run |
| 10592503 | Charging station |  | not run | not run |
| 43771597 | In what year did Russia make its sixth consecutive appearance at the Summer Olympics as an independent nation? | 2016 | not run | not run |
| 419223 | Nebula Award for Best Novel |  | not run | not run |
| 1191870 | AGM-28 Hound Dog |  | not run | not run |
| 5401325 | In what year was the first Costa Book Award given? | 1971 | not run | not run |
| 42099152 | Rail transport in China |  | not run | not run |
| 166831 | In what year did Gerry Anderson work as a dubbing editor and assembly cutter for the film Appointment in London? | 1953 | not run | not run |
| 434330 | In what year was Peter Forsberg inducted into the IIHF Hall of Fame? | 2013 | not run | not run |
| 268021 | Mariehamn |  | not run | not run |
| 28706 | SECAM |  | not run | not run |
| 240011 | Coherence (physics) |  | not run | not run |
| 913041 | Kapitänleutnant |  | not run | not run |
| 18880361 | In what year did Boston College win the Hockey East Tournament championship with a 5–3 score against Providence? | 2001 | not run | not run |
| 3660773 | Royal Society of New Zealand |  | not run | not run |
| 382592 | Inter-American Development Bank |  | not run | not run |
| 159281 | In what year did Charisma Carpenter first appear in the television series Buffy the Vampire Slayer? | 1997 | not run | not run |
| 510620 | Provinces of Cambodia |  | not run | not run |
| 30087669 | Shades of white |  | not run | not run |
| 752720 | Gemination |  | not run | not run |
| 69990317 | Timeline of the COVID-19 pandemic in Belarus (2022) |  | not run | not run |
| 436512 | Stake (Latter Day Saints) |  | not run | not run |
| 108668 | Fort Lupton, Colorado |  | not run | not run |
| 67546313 | Timeline of the COVID-19 pandemic in May 2021 |  | not run | not run |
| 524874 | Voiced pharyngeal fricative |  | not run | not run |
| 108523 | Walsenburg, Colorado |  | not run | not run |
| 209874 | Density functional theory |  | not run | not run |
| 19604151 | Atomic mass |  | not run | not run |
| 898992 | Inguinal hernia |  | not run | not run |
| 6754209 | In what year was the NHK Trophy figure skating competition inaugurated? | 1979 | not run | not run |
| 1601502 | In what year does the term of the Toronto District School Board trustees listed in the 2022-2026 Board of Trustees begin? | 2022 | not run | not run |
| 10911216 | In what year did V. Nagayya act in the film titled 'Gruhalakshmi'? | 1938 | not run | not run |
| 460448 | List of diving hazards and precautions |  | not run | not run |
| 416998 | In what year did Richard Roeper first appear as a guest on Late Night with Conan O'Brien? | 2000 | not run | not run |
| 4374512 | Ethel Barrymore Theatre |  | not run | not run |
| 1039161 | Congress of South African Trade Unions |  | not run | not run |
| 1738605 | Culture of Asia |  | not run | not run |
| 108607 | Rocky Ford, Colorado |  | not run | not run |
| 14752637 | Edward D. Thalmann |  | not run | not run |
| 416195 | In what year was Beethoven's song "Adelaide" composed? | 1794-1795 | not run | not run |
| 38528078 | Amarasi language |  | not run | not run |
| 52951710 | Alternative facts |  | not run | not run |
| 801247 | 1987 World Championships in Athletics |  | not run | not run |
| 68779 | Flemish Brabant |  | not run | not run |
| 1954987 | Wilcoxon signed-rank test |  | not run | not run |
| 63890492 | List of PlayStation 5 games |  | not run | not run |
| 407888 | In what year did Mike Rogers begin serving as the U.S. representative for Alabama's 3rd congressional district? | 2003 | not run | not run |
| 381506 | What year did the 2004 United States Senate elections take place? | 2004 | not run | not run |
| 698151 | On what month, day, and year was the first In Your House professional wrestling event held? | May 14, 1995 | not run | not run |
| 37336686 | Veraʼa language |  | not run | not run |
| 116267 | Biddeford, Maine |  | not run | not run |
| 1755878 | Porsche Panamera |  | not run | not run |
| 57737470 | In what year did Brian Schnuckel win the Primetime Creative Arts Emmy Award for Outstanding Multi-Camera Picture Editing for a Comedy Series for his work on "Jeopardé, Sobrieté and Infidelité"? | 2021 | not run | not run |
| 1581839 | In what month and year was the single "Love Will Tear Us Apart" by Joy Division released? | 1980-06 | not run | not run |
| 8315 | Diamagnetism |  | not run | not run |
| 219730 | Acrostic |  | not run | not run |
| 638354 | Daqing |  | not run | not run |
| 27346 | Slovenian Armed Forces |  | not run | not run |
| 2039988 | Orders, decorations, and medals of Canada |  | not run | not run |
| 5297519 | Utah Utes |  | not run | not run |
| 689521 | In what year did the television series China Beach win the Golden Globe Award for Best Television Series – Drama? | 1990 | not run | not run |
| 9005839 | Philippine Basketball Association draft |  | not run | not run |
| 19182802 | In what year was the FIBA Under-17 Basketball World Cup founded? | 2010 | not run | not run |
| 123412 | Havre, Montana |  | not run | not run |
| 1581712 | President of Estonia |  | not run | not run |
| 19763287 | VP8 |  | not run | not run |
| 3013008 | Kambera language |  | not run | not run |
| 3079144 | In what year did Jonathan Stark win the French Open men's doubles title? | 1994 | not run | not run |
| 1798106 | Order of the Netherlands Lion |  | not run | not run |
| 33396262 | List of the busiest airports in China |  | not run | not run |
| 260097 | Southampton, New York |  | not run | not run |
| 1593643 | Hyperlipidemia |  | not run | not run |
| 34839260 | Nunukan Tidung |  | not run | not run |
| 314843 | Campaign history of the Roman military |  | not run | not run |
| 450661 | List of villages in Japan |  | not run | not run |
| 1577389 | In what year was the soundtrack for The Remains of the Day film released? | 1993 | not run | not run |
| 11742 | Finite set |  | not run | not run |
| 334701 | List of state routes in New York |  | not run | not run |
| 886693 | In what year was Vladislav Tretiak inducted into the International Ice Hockey Federation Hall of Fame? | 1997 | not run | not run |
| 252776 | List of governors of Virginia |  | not run | not run |
| 399463 | During which period did the reign of King Wu Ding occur according to the dating of oracle bones? | Period I | not run | not run |
| 717842 | Soap Opera Digest |  | not run | not run |
| 36985 | Warren Mitchell |  | not run | not run |
| 641672 | In what year did Mamye BaCote graduate from Virginia Union University? | 1961 | not run | not run |
| 4846157 | South Central China |  | not run | not run |
| 34031613 | On what exact month, day, and year was the U.S. Fleet Cyber Command officially activated? | January 29, 2010 | not run | not run |
| 1434658 | In what year did Stevie Wonder's song "Superstition" reach its peak chart positions listed in the weekly chart performance table? | 1972 | not run | not run |
| 1158955 | Fingerstyle guitar |  | not run | not run |
| 445291 | Clive James |  | not run | not run |
| 40486863 | On what month, day, and year did the gymnastics events at the 2020 Summer Olympics begin? | July 24, 2021 | not run | not run |
| 153681 | Celestial equator |  | not run | not run |
| 276526 | Fiber bundle |  | not run | not run |
| 313971 | Sunset Strip |  | not run | not run |
| 255812 | Sorsogon |  | not run | not run |
| 775344 | Scout Motto |  | not run | not run |
| 1784313 | Tests of general relativity |  | not run | not run |
| 3734136 | Deportivo Táchira F.C. |  | not run | not run |
| 1694492 | On what month, day, and year was Garrett Withers formally installed as a U.S. Senator to finish the term after Alben W. Barkley resigned? | January 20, 1949 | not run | not run |
| 266325 | Sovereign (British coin) |  | not run | not run |
| 264434 | Albanian lek |  | not run | not run |
| 4495 | British thermal unit |  | not run | not run |
| 9616 | In what year was the concept of evolutionarily stable strategy proposed by John Maynard Smith and George R. Price? | 1972 | not run | not run |
| 58306941 | Technology readiness level |  | not run | not run |
| 31759897 | List of massacres in Mexico |  | not run | not run |
| 988765 | Sator Square |  | not run | not run |
| 1987049 | Damon Allen |  | not run | not run |
| 1519860 | On what month, day, and year did Michael Jackson perform at the Seoul Olympic Stadium during the HIStory World Tour? | October 11, 1996 | not run | not run |
| 646132 | Frankie Frisch |  | not run | not run |
| 26636274 | List of long-distance footpaths in the United Kingdom |  | not run | not run |
| 36169584 | What month, day, and year did the 2014–15 figure skating season begin? | July 1, 2014 | not run | not run |
| 54164 | Cortland County, New York |  | not run | not run |
| 2417390 | On what month, day, and year was Thomas M. Patterson formally installed as the successor for the Colorado At-large district in the 45th United States Congress? | December 13, 1877 | not run | not run |
| 27805952 | In what year was the 75th season of the American Hockey League, which featured the Binghamton Senators winning the Calder Cup? | 2010 | not run | not run |
| 117439 | Petoskey, Michigan |  | not run | not run |
| 441611 | Broadcast television systems |  | not run | not run |
| 25541697 | On what month, day, and year was the complete first season of Louie released on DVD and Blu-ray Disc in Region 1? | June 21, 2011 | not run | not run |
| 498814 | In what year did the debut album by American recording artist Norah Jones reach number 1 on the US Billboard 200 chart? | 2002 | not run | not run |
| 5366864 | Gestrinone |  | not run | not run |
| 317144 | List of airports by IATA airport code: S |  | not run | not run |
| 5873951 | Mongolian names |  | not run | not run |
| 1004027 | In what year did Carlos Bocanegra play for the Chicago Fire in Major League Soccer and make 26 league appearances scoring 2 goals? | 2002 | not run | not run |
| 4644242 | List of United States representatives from Maryland |  | not run | not run |
| 20811169 | Águilas Doradas |  | not run | not run |
| 5826767 | Simferopol International Airport |  | not run | not run |
| 1075838 | In what year was the film The Life Aquatic with Steve Zissou released in the United States? | 2004 | not run | not run |
| 690870 | Progressive Federal Party |  | not run | not run |
| 395945 | Pärnu County |  | not run | not run |
| 12885352 | List of quadrangles on Mars |  | not run | not run |
| 1540834 | In what year did Moscow, Russian SFSR, unsuccessfully bid to host the Summer Olympics? | 1976 | not run | not run |
| 212855 | Memory card |  | not run | not run |
| 2107046 | Gilles Müller |  | not run | not run |
| 97438 | Pulaski County, Arkansas |  | not run | not run |
| 3450570 | In what year did the film A Star Is Born receive nominations and wins at the Academy Awards, Golden Globe Awards, and other major film award ceremonies? | 1955 | not run | not run |
| 51960492 | C band (IEEE) |  | not run | not run |
| 53680300 | Local Now |  | not run | not run |
| 378938 | Magnesium in biology |  | not run | not run |
| 58227 | Arcadia (regional unit) |  | not run | not run |
| 545795 | In what month and year was the soundtrack album for the film The Big Chill released? | 1983-09 | not run | not run |
| 17292183 | In what year was the film New York, I Love You released? | 2008 | not run | not run |
| 122064 | Stillwater, Minnesota |  | not run | not run |
| 16896790 | As of what month and year was the status of Kosovo's EU accession chapters reported in the European Commission report? | 2025-11 | not run | not run |
| 1460518 | Riba |  | not run | not run |
| 1599554 | National Stadium of Peru |  | not run | not run |
| 392031 | In what year did Cheongju establish its sister city relationship with Wuhan in Hubei, China? | 2000 | not run | not run |
| 651709 | Le Nouvel Obs |  | not run | not run |
| 251243 | Gamla Uppsala |  | not run | not run |
| 415874 | List of astronomical observatories |  | not run | not run |
| 881523 | Brixen |  | not run | not run |
| 83399 | In what year was the Royal Armoured Corps established as an active unit? | 1939 | not run | not run |
| 151474 | Aliasing |  | not run | not run |
| 1778618 | Indiana Supreme Court |  | not run | not run |
| 33231502 | 20th National Film Awards |  | not run | not run |
| 17721855 | In what month and year was Dean Holdsworth first awarded Manager of the Month during the 2009–10 Football Conference season? | 2009-09 | not run | not run |
| 41149 | Fiber Distributed Data Interface |  | not run | not run |
| 1108342 | 1998 African Cup of Nations |  | not run | not run |
| 10173807 | Teymuraz Gabashvili |  | not run | not run |
| 5762383 | Timeline of the Troubles |  | not run | not run |
| 796996 | Berry College |  | not run | not run |
| 1838434 | In what year was the Sturt Football Club Hall of Fame launched? | 2004 | not run | not run |
| 5099468 | In what year did the Air Force Falcons football team play in the Bluebonnet Bowl against Texas? | 1985 | not run | not run |
| 21319587 | Hrusish languages |  | not run | not run |
| 308675 | British Columbia Social Credit Party |  | not run | not run |
| 190814 | Jämtland |  | not run | not run |
| 97665 | St. Tammany Parish, Louisiana |  | not run | not run |
| 42000251 | In what year was Will Forte first nominated for the Primetime Emmy Award for Outstanding Lead Actor in a Comedy Series for The Last Man on Earth? | 2015 | not run | not run |
| 51557631 | 2019 Ukrainian presidential election |  | not run | not run |
| 116866 | Westford, Massachusetts |  | not run | not run |
| 11958238 | In what year was the scheme of nobility insignia proposed for use with the 1905/1911 military uniforms in the Qing dynasty? | 1909 | not run | not run |
| 527837 | State University of New York at Cortland |  | not run | not run |
| 10174473 | In what year was the Wireless Application Protocol Forum Limited formed? | 1998 | not run | not run |
| 953669 | Wally Lewis |  | not run | not run |
| 519903 | Spaniel |  | not run | not run |
| 107661 | Montebello, California |  | not run | not run |
| 10200458 | In what year did Alla Kudryavtseva reach the semifinals in the Tour Championships doubles event? | 2014 | not run | not run |
| 25686 | In what year was the Rubáiyát of Omar Khayyám, translated by Edward FitzGerald, first published? | 1859 | not run | not run |
| 6791864 | In what year did Vitaly Petrov achieve his highest final standing in the GP2 Series according to the complete results table? | 2009 | not run | not run |
| 14873003 | In what year were the clubs Consadole Sapporo, Kyoto Purple Sanga, and Tokyo Verdy promoted from the J2 League to participate in the 2008 J.League Division 1 season? | 2007 | not run | not run |
| 4683430 | .300 Winchester Magnum |  | not run | not run |
| 2849652 | In what year did the school with the most Ohio High School Athletic Association team titles win its first title? | 1978 | not run | not run |
| 10793855 | What year did the HRT Formula 1 Team make its first entry in the Formula One World Championship? | 2010 | not run | not run |
| 4510663 | Special Frontier Force |  | not run | not run |
| 16821356 | German submarine U-101 (1940) |  | not run | not run |
| 246124 | Dave Eggers |  | not run | not run |
| 427980 | ISO/IEC 8859-4 |  | not run | not run |
| 824692 | Perfluorooctanoic acid |  | not run | not run |
| 40820246 | 2014 Ukrainian parliamentary election |  | not run | not run |
| 4401278 | Lyric Theatre (New York City, 1998) |  | not run | not run |
| 845756 | Central Bosnia Canton |  | not run | not run |
| 311001 | Green's function |  | not run | not run |
| 514218 | Piracicaba |  | not run | not run |
| 18694060 | List of solar eclipses in the 20th century |  | not run | not run |
| 132561 | Uniontown, Pennsylvania |  | not run | not run |
| 1093875 | Orlen |  | not run | not run |
| 6950063 | In what year did Mark Pocan begin serving as a member of the U.S. House of Representatives from Wisconsin's 2nd congressional district? | 2013 | not run | not run |
| 1245250 | West Virginia State University |  | not run | not run |
| 4091278 | On what exact month, day, and year did Hamengkubuwono X become the incumbent Sultan of Yogyakarta? | March 7, 1989 | not run | not run |
| 2382246 | In what year was the Medical Scientist Training Program at Northwestern University founded? | 1964 | not run | not run |
| 9912930 | Jewish Babylonian Aramaic |  | not run | not run |
| 98957 | In what year did Annie Sprinkle appear in the film titled 'The Ganja Express'? | 1978 | not run | not run |
| 6336280 | HIV/AIDS in South Africa |  | not run | not run |
| 187926 | Centroid |  | not run | not run |
| 9737149 | Football at the 2004 Summer Olympics – Men's tournament |  | not run | not run |
| 28570035 | Japanese pagoda |  | not run | not run |
| 81167 | Provinces of France |  | not run | not run |
| 730257 | In what year was the number of native speakers of Judeo-Berber recorded as 200? | 2023 | not run | not run |
| 573875 | Measurement in quantum mechanics |  | not run | not run |
| 3345447 | On what month and day did the 1986 NFL draft begin? | April 29, 1986 | not run | not run |
| 75903 | ISO/IEC 8859-3 |  | not run | not run |
| 137733 | Woodbridge, Virginia |  | not run | not run |
| 23658 | In what year was the Philip K. Dick Award first presented? | 1983 | not run | not run |
| 8416397 | Long hair |  | not run | not run |
| 8244461 | Jongno District |  | not run | not run |
| 664497 | Parallel (geometry) |  | not run | not run |
| 284629 | Welland Canal |  | not run | not run |
| 8410979 | 1992 AFL season |  | not run | not run |
| 3161572 | Economy of Wales |  | not run | not run |
| 108823 | Lyme, Connecticut |  | not run | not run |
| 294735 | Oberstleutnant |  | not run | not run |
| 11958301 | In what year did the London Grand Prix Gold badminton tournament first appear in the BWF Grand Prix Gold and Grand Prix series? | 2013 | not run | not run |
| 64776868 | 2020 US Open – Men's singles |  | not run | not run |
| 3013157 | List of civil parishes in Lincolnshire |  | not run | not run |
| 330122 | List of islands of Ireland |  | not run | not run |
| 794151 | 1965 Canadian federal election |  | not run | not run |
| 21758543 | On what month, day, and year did the Spain national under-20 football team play their first international match? | June 28, 1977 | not run | not run |
| 4421189 | In what year did the team Toros Neftekamsk achieve their highest final regular season rank in the All-Russian Hockey League? | 2014 | not run | not run |
| 282905 | Provençal dialect |  | not run | not run |
| 2445647 | Lanxess Arena |  | not run | not run |
| 150961 | Ponca City, Oklahoma |  | not run | not run |
| 40157682 | Socialist Autonomous Province of Vojvodina |  | not run | not run |
| 2405252 | Toulouse Olympique |  | not run | not run |
| 428023 | ISO/IEC 8859-16 |  | not run | not run |
| 2643686 | Aga Khan University |  | not run | not run |
| 4958471 | Brandon Marshall |  | not run | not run |
| 466804 | METAR |  | not run | not run |
| 5235555 | Pittsburgh Bureau of Fire |  | not run | not run |
| 1578061 | The Michigan Daily |  | not run | not run |
| 1674149 | Chifeng |  | not run | not run |
| 1491100 | Flavin adenine dinucleotide |  | not run | not run |
| 8093228 | Marcin Matkowski |  | not run | not run |
| 923348 | E. G. Marshall |  | not run | not run |
| 9513184 | On what month, day, and year was the 21st annual Royal Rumble professional wrestling pay-per-view event produced by World Wrestling Entertainment held? | January 27, 2008 | not run | not run |
| 3044443 | In what year were the Toto numerals documented by van Driem as shown in the table? | 1995 | not run | not run |
| 17257420 | 2000–01 Football League |  | not run | not run |
| 24998899 | In what year did Joël Matip score his only international goal for Cameroon? | 2014 | not run | not run |
| 1640791 | List of William Shakespeare screen adaptations |  | not run | not run |
| 650007 | Paget's disease of bone |  | not run | not run |
| 5196351 | In what year did Schumer receive 92% of the vote in a Senate race according to the recent election results from statewide races? | 2016 | not run | not run |
| 13477403 | List of National Historic Landmarks in Vermont |  | not run | not run |
| 303051 | Gallo-Romance languages |  | not run | not run |
| 37119588 | German submarine U-475 |  | not run | not run |
| 214067 | Virgo Cluster |  | not run | not run |
| 12308004 | 508th Aerospace Sustainment Wing |  | not run | not run |
| 530365 | In what year did Joan Bennett appear on the radio program Philip Morris Playhouse? | 1941 | not run | not run |
| 531432 | Autostereogram |  | not run | not run |
| 63417 | Fountains Abbey |  | not run | not run |
| 196819 | On what month, day, and year was the album Darkness on the Edge of Town by Bruce Springsteen released? | June 2, 1978 | not run | not run |
| 3833573 | List of mayors of Long Beach, California |  | not run | not run |
| 83943 | Indonesia Raya |  | not run | not run |
| 4576492 | In what year did the National Association of Basketball Coaches stop having Independents in District 13? | 2014-2015 | not run | not run |
| 7117467 | 2006 United States broadcast television realignment |  | not run | not run |
| 9427377 | Maine Democratic Party |  | not run | not run |
| 26473291 | List of hot sauces |  | not run | not run |
| 16099880 | 2010 IndyCar Series |  | not run | not run |
| 9571698 | Carnivoramorpha |  | not run | not run |
| 50555549 | On what month, day, and year was the final match of the 115th staging of the Copa del Rey held? | May 27, 2017 | not run | not run |
| 2153241 | Unicode subscripts and superscripts |  | not run | not run |
| 15029 | Industry Standard Architecture |  | not run | not run |
| 880626 | Tokyo Electric Power Company |  | not run | not run |
| 475016 | In what year was Yueju Opera inscribed on the UNESCO Intangible Cultural Heritage list? | 2009 | not run | not run |
| 1302610 | On what month, day, and year was the Omni Television system launched? | September 16, 2002 | not run | not run |
| 5562328 | In what season did Garry Monk play 15 league matches on loan for Sheffield Wednesday? | 2002-2003 | not run | not run |
| 3761368 | In what season did Stoke win the Birmingham & District League championship? | 1910-1911 | not run | not run |
| 1083426 | From what year did Pinot gris become the only allowed designation, replacing Tokay d'Alsace and Tokay Pinot gris, in the Alsace AOC varietal labeling? | 2007 | not run | not run |
| 3212306 | What is the full date of birth of Colin Kazim-Richards? | August 26, 1986 | not run | not run |
| 263886 | Differential operator |  | not run | not run |
| 3360323 | Washington State Democratic Party |  | not run | not run |
| 545100 | Association of Zoos and Aquariums |  | not run | not run |
| 5771288 | Alians |  | not run | not run |
| 838084 | What month and year is the next planned franchise change for the InterCity East Coast franchise? | 2023-06 | not run | not run |
| 55681284 | On what exact date was the FT8 digital mode of radio communication released by its creators Joe Taylor and Steve Franke? | June 29, 2017 | not run | not run |
| 3613999 | In what year did the United National Independence Party (UNIP) first win 125 seats in the National Assembly elections of Zambia? | 1973 | not run | not run |
| 12026076 | Exoribonuclease |  | not run | not run |
| 6172 | Cantor set |  | not run | not run |
| 1529985 | Badges of the United States Coast Guard |  | not run | not run |
| 28814296 | King Abdullah Sports City Stadium |  | not run | not run |
| 15418318 | In what year did the song "I Could Fall in Love" achieve its peak chart positions listed in the weekly chart performance table? | 1995 | not run | not run |
| 57476308 | In what year did Liverpool F.C. complete the season with 38 matches played, 30 wins, 7 draws, and 1 loss? | 2019 | not run | not run |
| 8624941 | On what month, day, and year did the KAI KF-21 Boramae have its first flight? | July 19, 2022 | not run | not run |
| 1304443 | In what year did the United States presidential election take place in Pennsylvania where Bush and Kerry competed by congressional district? | 2004 | not run | not run |
| 7628511 | Weinan |  | not run | not run |
| 7719033 | Languages of Afghanistan |  | not run | not run |
| 2849796 | In what year were the Black Reel Awards first presented in Washington, DC? | 2000 | not run | not run |
| 32795358 | On what month, day, and year was the UFC match between Diaz and Miller broadcast on the Fox network? | May 5, 2012 | not run | not run |
| 1910396 | Luis Horna |  | not run | not run |
| 69129560 | On what month, day, and year was the E5 series Shinkansen train set U29 delivered? | December 7, 2015 | not run | not run |
| 947310 | United States Department of Energy National Laboratories |  | not run | not run |
| 24402113 | Metropolitan Fresno |  | not run | not run |
| 11404831 | Scottish Canadians |  | not run | not run |
| 338435 | Filicide |  | not run | not run |
| 57208313 | On what month, day, and year was the Brazilian mountain biking team named for the 2020 Summer Olympics? | May 31, 2021 | not run | not run |
| 53608466 | In what month and year was the Transkei Defence Force disbanded? | 1994-04 | not run | not run |
| 495884 | Sound pressure |  | not run | not run |
| 16921855 | On what month, day, and year did the second annual Night of Champions professional wrestling event take place? | June 29, 2008 | not run | not run |
| 2194706 | Angela Mortimer |  | not run | not run |
| 2452013 | Grand chancellor (China) |  | not run | not run |
| 32269679 | 2011 NBA lockout |  | not run | not run |
| 1842129 | KMAX-TV |  | not run | not run |
| 505664 | In what year did the album by the American alternative rock band the Smashing Pumpkins reach number 1 on the Australian Albums (ARIA) chart? | 1998 | not run | not run |
| 1226460 | In what year did Henri Pescarolo win the French Formula Three Championship? | 1967 | not run | not run |
| 188896 | Neutron moderator |  | not run | not run |
| 4821319 | Sari, Iran |  | not run | not run |
| 539170 | Baltistan |  | not run | not run |
| 2156220 | Tema |  | not run | not run |
| 294608 | Doboj |  | not run | not run |
| 71411822 | Judo Grand Slam |  | not run | not run |
| 1331885 | Yingkou |  | not run | not run |
| 7571233 | Pennsylvania's 17th congressional district |  | not run | not run |
| 1500696 | On what month, day, and year were the 47th Annual Grammy Awards held? | February 13, 2005 | not run | not run |
| 1148574 | In what year did the official record chart in the United Kingdom begin using Record Retailer as the canonical source for singles charts? | 1960 | not run | not run |
| 25820233 | On what month, day, and year was the top professional association football division in Costa Rica founded? | June 13, 1921 | not run | not run |
| 1882706 | Medal ribbon |  | not run | not run |
| 2253558 | AngloGold Ashanti |  | not run | not run |
| 845033 | KHON-TV |  | not run | not run |
| 1797559 | Linfen |  | not run | not run |
| 642489 | Porsche 911 (996) |  | not run | not run |
| 55093710 | In what year did Scott Ryan win the award for Best Lead Actor in a Television Drama for the first time according to the awards and nominations table? | 2019 | not run | not run |
| 182890 | Kronecker delta |  | not run | not run |
| 2254778 | Brisbane Entertainment Centre |  | not run | not run |
| 1387121 | Elections in Portugal |  | not run | not run |
| 1928528 | American Contract Bridge League |  | not run | not run |
| 3701174 | American Civil War corps badges |  | not run | not run |
| 4236804 | Yule log (cake) |  | not run | not run |
| 669903 | In what year did Rainer Schüttler achieve his career-high ATP singles ranking of world No. 5? | 2004-04 | not run | not run |
| 13544419 | MIMO |  | not run | not run |
| 2336136 | Tenth Dynasty of Egypt |  | not run | not run |
| 1861711 | Yulin, Shaanxi |  | not run | not run |
| 1701840 | In what year was the survey conducted that recorded 1,030,254 Kumaoni speakers in India? | 1961 | not run | not run |
| 93260 | Pitt County, North Carolina |  | not run | not run |
| 665071 | In what month and year was the French gunboat Vierge-de-Grâce recaptured and scuttled during the Siege of Acre? | 1799-05 | not run | not run |
| 1140090 | In what year was the 25th season of the Fédération Internationale de l'Automobile's Formula One motor racing held? | 1971 | not run | not run |
| 380087 | Litchfield, Connecticut |  | not run | not run |
| 46965920 | List of Televisa telenovelas and series (2010s) |  | not run | not run |
| 5069114 | Cinema of Ireland |  | not run | not run |
| 15745082 | Administrative divisions of Cambodia |  | not run | not run |
| 1283281 | ISO 20022 |  | not run | not run |
| 548738 | Zenica-Doboj Canton |  | not run | not run |
| 1487550 | In what year did John Edward Bromby begin his period as headmaster of Melbourne Grammar School? | 1858 | not run | not run |
| 5802918 | Toto Cup |  | not run | not run |
| 247169 | Music of Argentina |  | not run | not run |
| 12692065 | In what year was the 64th Air Division inactivated at Stewart Air Force Base, New York? | 1963 | not run | not run |
| 774572 | Evolutionary game theory |  | not run | not run |
| 1909983 | In what year did Pierre Gemayel begin his tenure as president of the governing body of association football in Lebanon? | 1935 | not run | not run |
| 638972 | Football at the 2000 Summer Olympics – Men's tournament |  | not run | not run |
| 364774 | Conformal field theory |  | not run | not run |
| 8025346 | PFC Lokomotiv Tashkent |  | not run | not run |
| 91204 | Jefferson County, Washington |  | not run | not run |
| 3951896 | List of nominations to the Supreme Court of the United States |  | not run | not run |
| 803607 | Chorea |  | not run | not run |
| 538031 | List of municipalities in Tennessee |  | not run | not run |
| 25739 | Rich Text Format |  | not run | not run |
| 7349465 | Kermanshah County |  | not run | not run |
| 14456578 | In what years was the 453rd Bombardment Group active during its first period of service? | 1943-1945 | not run | not run |
| 13042838 | Fernando Muslera |  | not run | not run |
| 33038936 | In what month, day, and year were the Italian Athletics Championships held in Bari? | 3–4 March 2007 | not run | not run |
| 1689476 | On what month, day, and year was the complete first season of Tom & Jerry Kids released on DVD? | April 30, 2013 | not run | not run |
| 2170226 | In what year did Chase Elliott win the NASCAR Rookie of the Year award? | 2016 | not run | not run |
| 350708 | MultiMediaCard |  | not run | not run |
| 5175973 | Military ranks of South Korea |  | not run | not run |
| 141839 | Magdalen Islands |  | not run | not run |
| 930108 | Ivanovo |  | not run | not run |
| 714854 | Department of Junín |  | not run | not run |
| 460528 | Heart Sutra |  | not run | not run |
| 315548 | Stabat Mater |  | not run | not run |
| 232872 | Family Affairs |  | not run | not run |
| 40377 | In what year did Ole Einar Bjørndalen compete in the 2006–07 World Cup season? | 2006 | not run | not run |
| 2447894 | Census in the United Kingdom |  | not run | not run |
| 11584912 | In what year did the number of higher education institutions divesting from South Africa reach 128? | 1987 | not run | not run |
| 39227262 | 2013–14 Süper Lig |  | not run | not run |
| 368004 | On what exact date was the Royal Logistic Corps officially formed? | April 5, 1993 | not run | not run |
| 25286976 | Solar eclipse of March 29, 2025 |  | not run | not run |
| 253068 | Governor of Hawaii |  | not run | not run |
| 391267 | Positron emission |  | not run | not run |
| 383485 | In what year was the 1957 orthography of the Zhuang name for Beihai recorded? | 1957 | not run | not run |
| 16278495 | Outline of Brazil |  | not run | not run |
| 1904477 | In what year did the reissued single "West End Girls" achieve its peak chart positions listed in the weekly charts? | 1986 | not run | not run |
| 22133191 | 2009–10 Bundesliga |  | not run | not run |
| 1969542 | Extraocular muscles |  | not run | not run |
| 7978444 | In what year was the original video animation titled 'Sakura Diaries' directed by Kunitoshi Okajima released? | 1997 | not run | not run |
| 432487 | Washburn University |  | not run | not run |
| 35636402 | In what season did Manchester win the North Division 2 rugby union league championship? | 1992-1993 | not run | not run |
| 1658720 | In what season did Rigobert Song play for Salernitana in Serie A? | 1998-1999 | not run | not run |
| 735501 | In what year did the reign of the Later Tang ruler Li Cunxu, known by the temple name Zhuāngzōng, begin? | 923 | not run | not run |
| 12064241 | Funny Girl (film) |  | not run | not run |
| 29828333 | In what year did the Lake Forest Foresters football team reach the second round of the NCAA Division III playoffs? | 2024 | not run | not run |
| 53906279 | On what month, day, and year was the WWE Great Balls of Fire event held? | July 9, 2017 | not run | not run |
| 1997961 | On what month, day, and year was Caroline Matilda of Great Britain born? | July 11, 1751 | not run | not run |
| 151175 | Mansfield, Texas |  | not run | not run |
| 59076 | German submarine U-553 |  | not run | not run |
| 469948 | Muslims (ethnic group) |  | not run | not run |
| 16454455 | 1965–66 Football League |  | not run | not run |
| 2383962 | Malky Mackay |  | not run | not run |
| 847398 | Balsamic vinegar |  | not run | not run |
| 17104279 | Kiev Governorate |  | not run | not run |
| 1699287 | Cardium pottery |  | not run | not run |
| 140103 | Riverton, Wyoming |  | not run | not run |
| 862690 | Cirebon |  | not run | not run |
| 507522 | Aggie Bonfire |  | not run | not run |
| 19369391 | Sanitation worker |  | not run | not run |
| 119272 | Redford, Michigan |  | not run | not run |
| 898353 | Philadelphia Big 5 |  | not run | not run |
| 461025 | Aetolia-Acarnania |  | not run | not run |
| 1718061 | Shangri-La, Yunnan |  | not run | not run |
| 1138307 | Prijepolje |  | not run | not run |
| 1660205 | Tabarka |  | not run | not run |
| 32257023 | 1944 Republican Party presidential primaries |  | not run | not run |
| 898653 | Derek Luke |  | not run | not run |
| 246768 | Biliran |  | not run | not run |
| 39913555 | 1976 United States presidential election in New York |  | not run | not run |
| 6230784 | Hong Kong Cantonese |  | not run | not run |
| 9489115 | Gong language |  | not run | not run |
| 87505 | Yukon–Koyukuk Census Area, Alaska |  | not run | not run |
| 48344963 | Puduvoyal |  | not run | not run |
| 6795916 | Gough's Cave |  | not run | not run |
| 1187279 | Islam in Bangladesh |  | not run | not run |
| 2513744 | Nissan Motor Manufacturing UK |  | not run | not run |
| 4906966 | British Standard Pipe |  | not run | not run |
| 16454482 | 1972–73 Football League |  | not run | not run |
| 65217524 | List of solar eclipses in the Middle Ages |  | not run | not run |
| 30079114 | 2014 Ukrainian presidential election |  | not run | not run |
| 482383 | In what year did Paul D. Zimmerman win the BAFTA Award for Best Original Screenplay for The King of Comedy? | 1983 | not run | not run |
| 23758509 | List of solar eclipses in the 22nd century |  | not run | not run |
| 632394 | Transit of Mercury |  | not run | not run |
| 171193 | Hedmark |  | not run | not run |
| 13963241 | QF 3-inch 20 cwt |  | not run | not run |
| 971658 | Helminthiasis |  | not run | not run |
| 1338980 | Gatineau Olympiques |  | not run | not run |
| 57587117 | In what year was iOS 12 released? | 2018 | not run | not run |
| 8551616 | Payment Card Industry Data Security Standard |  | not run | not run |
| 12935706 | Timea Bacsinszky |  | not run | not run |
| 14693333 | In what year did the debut single by the American rapper Flo Rida featuring T-Pain reach its peak position on the US Billboard Hot 100 chart? | 2008 | not run | not run |
| 219172 | What is the time zone offset during British Summer Time (DST) for the Home Counties in England? | UTC+01:00 | not run | not run |
| 42280433 | List of Albania international footballers |  | not run | not run |
| 93298 | Haywood County, North Carolina |  | not run | not run |
| 12336148 | https://en.wikipedia.org/w/index.php?pageid=12336148 |  | not run | not run |
| 690646 | https://en.wikipedia.org/w/index.php?pageid=690646 |  | not run | not run |
| 7050925 | Czech Americans |  | not run | not run |
| 91258 | Rappahannock County, Virginia |  | not run | not run |
| 1108299 | 1994 African Cup of Nations |  | not run | not run |
| 1092454 | Malazan Book of the Fallen |  | not run | not run |
| 9029387 | AFI's 100 Years...100 Movies (10th Anniversary Edition) |  | not run | not run |
| 414163 | https://en.wikipedia.org/w/index.php?pageid=414163 |  | not run | not run |
| 23692 | Prime number theorem |  | not run | not run |
| 50087781 | 1976 United States presidential election in Texas |  | not run | not run |
| 109769 | Altamonte Springs, Florida |  | not run | not run |
| 64986718 | Structure of the United States Space Force |  | not run | not run |
| 32108299 | WSG Tirol |  | not run | not run |
| 516942 | On what month, day, and year was the Qing dynasty abolished? | February 12, 1912 | not run | not run |
| 7219253 | German submarine U-31 (1936) |  | not run | not run |
| 17257417 | In what year was the 101st completed season of The Football League, known as the 1999–2000 Football League, held? | 1999-2000 | not run | not run |
| 467353 | Suwannee River |  | not run | not run |
| 3052138 | Submarine pen |  | not run | not run |
| 2732512 | Estadio La Rosaleda |  | not run | not run |
| 46694908 | In what year did Grêmio Novorizontino win the Campeonato Paulista Série A3 title? | 2014 | not run | not run |
| 747878 | Lishui |  | not run | not run |
| 26005083 | In what year was Adrián Menéndez Maceiras born? | 1985 | not run | not run |
| 25287038 | Solar eclipse of June 12, 2029 |  | not run | not run |
| 2297339 | Salina Regional Airport |  | not run | not run |
| 30002680 | In what year was the Surrey Rugby Football Union involved in a County Championship final that ended with the title being shared after a drawn replay? | 1967 | not run | not run |
| 543502 | In what year did Brigham Young University–Idaho transition from a junior college to a baccalaureate institution? | 2001 | not run | not run |
| 415282 | List of kings of Athens |  | not run | not run |
| 42345 | On what month, day, and year was Hyman G. Rickover born? | January 27, 1900 | not run | not run |
| 13523509 | Estonian Land Forces |  | not run | not run |
| 452068 | Discovery Program |  | not run | not run |
| 134805 | Mitchell, South Dakota |  | not run | not run |
| 43050178 | In what year was the Bangalore railway division formed? | 1971 | not run | not run |
| 3648904 | In what year did Barry Williams first appear in the television series The Brady Bunch? | 1969 | not run | not run |
| 47073183 | On what month, day, and year did the WWE event 'The Beast in the East' take place at the Ryōgoku Kokugikan in Tokyo, Japan? | July 4, 2015 | not run | not run |
| 3082583 | On what month, day, and year did the Indian rupee decimalisation change to 1 rupee equaling 100 naye paise? | April 1, 1957 | not run | not run |
| 998762 | Communes of the Bas-Rhin department |  | not run | not run |
| 30613979 | Member states of the Arab League |  | not run | not run |
| 64109900 | List of Indonesian snacks |  | not run | not run |
| 56189 | Interlaced video |  | not run | not run |
| 750002 | Cultural regions of Lithuania |  | not run | not run |
| 40242680 | 1988 United States presidential election in Texas |  | not run | not run |
| 57055767 | What month, day, and year was the song "I Like It" by Cardi B, Bad Bunny, and J Balvin released to radio stations through Atlantic Records? | May 25, 2018 | not run | not run |
| 43791114 | German submarine U-764 |  | not run | not run |
| 64177252 | Emmett Till Antilynching Act |  | not run | not run |
| 207162 | In what year did the Frankford Yellow Jackets win the NFL Championship? | 1926 | not run | not run |
| 15156688 | In what year did the Chattanooga Moccasins join the SoCon conference? | 1977 | not run | not run |
| 1942258 | Table wine |  | not run | not run |
| 4239846 | In what year did Donald Trump first win the presidential vote in Ohio's 4th congressional district according to the election results? | 2016 | not run | not run |
| 58977186 | On what month, day, and year was the National Board of Review Awards ceremony held where The Green Knight won Top Independent Films? | December 2, 2021 | not run | not run |
| 1345744 | WPHL-TV |  | not run | not run |
| 1354709 | Two knights endgame |  | not run | not run |
| 2061661 | Korvettenkapitän |  | not run | not run |
| 22201341 | Telefol language |  | not run | not run |
| 76391 | In what year was the linguistic source referenced for the morphology of transitive verb endings in Bislama published? | 2018 | not run | not run |
| 246612 | In what year was the IQD 25 banknote featuring Saddam Hussein with the Battle of al-Qādisiyyah in the background issued in the Swiss dinar series? | 1986 | not run | not run |
| 61520198 | In what year was the Justicialist Party led by Alberto Fernández a member party of the Frente de Todos coalition? | 2023 | not run | not run |
| 333697 | Uniform Resource Name |  | not run | not run |
| 5121902 | Ferrari 312T |  | not run | not run |
| 110941 | Barrington, Illinois |  | not run | not run |
| 22198326 | On what dates were the second round matches of the 2009–10 Copa del Rey played? | September 1, 2, 3, 9, and 16, 2009 | not run | not run |
| 59834648 | Mattel Films |  | not run | not run |
| 476776 | On what month, day, and year was the Criminal Code of Canada assented to? | July 9, 1892 | not run | not run |
| 91733 | Hardin County, Tennessee |  | not run | not run |
| 771734 | Rugby union at the Summer Olympics |  | not run | not run |
| 496312 | Nuclease |  | not run | not run |
| 40701845 | German submarine U-706 |  | not run | not run |
| 5184238 | In what year did Schumer receive 67% of the vote in a Senate election in New York's 20th congressional district? | 2016 | not run | not run |
| 39950440 | 1964 United States presidential election in New York |  | not run | not run |
| 24298824 | Somali mythology |  | not run | not run |
| 683742 | In what year did the television series The District first air on CBS? | 2000 | not run | not run |
| 25323835 | In what year was the Czech Technical University in Prague ranked 12th in the QS Emerging Europe and Central Asia regional overall rankings? | 2022 | not run | not run |
| 1706399 | Budapest Metro |  | not run | not run |
| 91227 | Wythe County, Virginia |  | not run | not run |
| 316858 | Eastern Armenian |  | not run | not run |
| 5722 | Call of Cthulhu (role-playing game) |  | not run | not run |
| 71778950 | Shakespeare's influence on Tolkien |  | not run | not run |
| 7600694 | In what year was the Emphatic Diaglott New Testament translation published? | 1864 | not run | not run |
| 67194640 | 2018 San Francisco Board of Education election |  | not run | not run |
| 29336870 | 2011 Tippeligaen |  | not run | not run |
| 17185703 | On what month, day, and year was the 2009 Daytona 500 held? | February 15, 2009 | not run | not run |
| 1530689 | Complementarity (physics) |  | not run | not run |
| 967668 | Ansan |  | not run | not run |
| 3396363 | Honda CBR600RR |  | not run | not run |
| 5483165 | In what year did the Minnesota's 6th congressional district first record election results under the 2013–2023 boundaries for the office of President? | 2012 | not run | not run |
| 1156819 | Population ecology |  | not run | not run |
| 911362 | Billy Pierce |  | not run | not run |
| 7348749 | Urmia County |  | not run | not run |
| 979683 | Digicel |  | not run | not run |
| 1187925 | Women's Auxiliary Air Force |  | not run | not run |
| 420528 | In what year did James Stewart begin his tenure as Duke of Richmond? | 1641 | not run | not run |
| 298534 | CompactFlash |  | not run | not run |
| 1848827 | Lancaster Royal Grammar School |  | not run | not run |
| 15602925 | Merville, Nord |  | not run | not run |
| 35555518 | Russian Braille |  | not run | not run |
| 88735 | Móði and Magni |  | not run | not run |
| 308022 | In what year was the venue White Eagle Hall in Jersey City established? | 1910 | not run | not run |
| 29603083 | On what date was the Thiruvananthapuram Railway Division formed? | October 2, 1979 | not run | not run |
| 423933 | Cracking (chemistry) |  | not run | not run |
| 7268183 | German submarine U-371 |  | not run | not run |
| 39596181 | In what year did The Sopranos season 1 receive nominations and wins for various awards including the Primetime Emmy Awards, Golden Globe Awards, and Screen Actors Guild Awards? | 1999 | not run | not run |
| 5866273 | German submarine U-75 (1940) |  | not run | not run |
| 7126758 | Al-Shamal SC |  | not run | not run |
| 91871 | Lexington County, South Carolina |  | not run | not run |
| 608992 | Tarpaulin |  | not run | not run |
| 6983416 | Signal Corps in the American Civil War |  | not run | not run |
| 14192171 | SpongeBob SquarePants season 2 |  | not run | not run |
| 1342939 | List of extreme points of India |  | not run | not run |
| 6007224 | In what year was the Pensacola Standard Metropolitan Statistical Area first defined? | 1958 | not run | not run |
| 23847876 | In what year was the football club FC Vaslui founded? | 2002 | not run | not run |
| 3095917 | In what years did Mohammad Hafeez serve as the Pakistani national cricket captain for T20I? | 2012-2014 | not run | not run |
| 16454477 | In what season did Arsenal become the champions of The Football League? | 1970-1971 | not run | not run |
| 20754105 | BMW Z4 (E89) |  | not run | not run |
| 2976501 | Kizilsu Kyrgyz Autonomous Prefecture |  | not run | not run |
| 533423 | Solar water heating |  | not run | not run |
| 124728 | Poplar Bluff, Missouri |  | not run | not run |
| 46345037 | German submarine U-956 |  | not run | not run |
| 137888 | Longview, Washington |  | not run | not run |
| 844866 | Manado Malay |  | not run | not run |
| 1411599 | In what year did the song "Won't Get Fooled Again" reach its peak chart positions listed in the weekly charts table? | 1971 | not run | not run |
| 117162 | La Crescenta-Montrose, California |  | not run | not run |
| 1179011 | In what year did Ian Callaghan play for the Fort Lauderdale Strikers in the NASL? | 1978 | not run | not run |
| 332236 | IFAF World Championship |  | not run | not run |
| 1007705 | In what year was the Lancashire League rugby competition instituted? | 1895 | not run | not run |
| 588643 | Colorado Party (Uruguay) |  | not run | not run |
| 933786 | In what year did the AT&T Pebble Beach Pro-Am first include Spyglass Hill Golf Course as a tournament host? | 1967 | not run | not run |
| 4847416 | In what year did the NCAA Division I-A football season feature 105 teams and have Oklahoma as the preseason AP No. 1? | 1985 | not run | not run |
| 80493 | In what year did the film Henry V receive the Academy Honorary Award? | 1944 | not run | not run |
| 30863884 | Performing arts in Detroit |  | not run | not run |
| 1840325 | Shippensburg University |  | not run | not run |
| 69730243 | In what year did James Madison move from the CAA (FCS) conference to the Sun Belt (FBS) conference? | 2022 | not run | not run |
| 69055344 | 2022 Havering London Borough Council election |  | not run | not run |
| 1412020 | In what year did W. A. Miller begin his presidency at Texas A&M University–Corpus Christi? | 1952 | not run | not run |
| 1882322 | IARC group 1 |  | not run | not run |
| 10760098 | In what year did the European Junior Swimming Championships begin? | 1967 | not run | not run |
| 11080001 | 343d Wing |  | not run | not run |
| 32148625 | List of donkey breeds |  | not run | not run |
| 11728413 | In what year was the id Tech 4 game engine released? | 2004 | not run | not run |
| 473278 | In what year was the ISO 31 international standard concerning physical quantities and units first published? | 1992 | not run | not run |
| 1774491 | Neighborhoods in Washington, D.C. |  | not run | not run |
| 45367766 | In what season did All Stars F.C. achieve 3rd place in the National First Division? | 2021-2022 | not run | not run |
| 762953 | Central College (Iowa) |  | not run | not run |
| 11056278 | 2000 CART FedEx Championship Series |  | not run | not run |
| 1017722 | Szolnok |  | not run | not run |
| 36229955 | German submarine U-431 |  | not run | not run |
| 343355 | Municipalities of Armenia |  | not run | not run |
| 6779185 | Reisinger |  | not run | not run |
| 1756402 | In what years was Pat McCrory the Republican nominee for Governor of North Carolina? | 2008, 2012, 2016 | not run | not run |
| 4782774 | Durbanville |  | not run | not run |
| 5329771 | In what year did the song "Déjà Vu" by Beyoncé achieve its peak chart positions listed in the weekly chart performance table? | 2006 | not run | not run |
| 748114 | On what month, day, and year did Ted Lyons pitch a no-hitter? | August 21, 1926 | not run | not run |
| 1939189 | In what year was the Wilmington Hammerheads Football Club dissolved? | 2017 | not run | not run |
| 344242 | Average absolute deviation |  | not run | not run |
| 15307973 | In what year did Jean-Marie Bidaux begin his term as mayor of Alaincourt? | 2001 | not run | not run |
| 94561 | Platte County, Missouri |  | not run | not run |
| 225205 | On what month, day, and year was Edward C. Cabell formally installed as the representative for Florida At-large after Florida was admitted to the Union? | October 6, 1845 | not run | not run |
| 66196 | In what biblical book and chapter is the passage that describes the Lord coming down from heaven with a loud command, the voice of the archangel, and the trumpet call of God? | 1 Thessalonians 4 | not run | not run |
| 27449035 | In what year did TheWrap win the Best Entertainment Website (Internet-only) award from the Los Angeles Press Club’s National Arts and Entertainment Journalism Awards? | 2018 | not run | not run |
| 508406 | In what year was the film 'Dances With Wolves', featuring Mary McDonnell as Stands With A Fist, released? | 1990 | not run | not run |
| 633282 | In what year did the production of the BMW 7 Series begin? | 1977 | not run | not run |
| 5007829 | In what year was the Alhambra Theatre in El Paso, Texas, designed by Henry C. Trost, completed? | 1914 | not run | not run |
| 275601 | Classification of demons |  | not run | not run |
| 992991 | Vowel length |  | not run | not run |
| 219101 | In what year did the song "Jumpin' Jack Flash" reach its peak chart positions listed in the weekly charts? | 1968 | not run | not run |
| 914132 | Mardy Fish |  | not run | not run |
| 1028188 | Code page 437 |  | not run | not run |
| 107632 | In what year were the top employers in Gardena, California, reported according to the city's Annual Comprehensive Financial Report? | 2020 | not run | not run |
| 1433736 | In what year did Balachandra Menon act in the film 'April 18'? | 1984 | not run | not run |
| 2396042 | In what week of the 1983 NFL season did the Dallas team first lose a game in the National Football Conference East division? | Week 8 | not run | not run |
| 57918689 | On what month, day, and year was the second leg of the fourth round originally scheduled in the 2022 FIFA World Cup qualification (AFC)? | November 16, 2021 | not run | not run |
| 3292213 | Hazard analysis |  | not run | not run |
| 414186 | In the AJCC Prognostic Stage Groups for oral cancer, what stage group corresponds to the classification when T is T2, N is N0, and M is M0? | II | not run | not run |
| 773431 | On what month, day, and year did the 8th World Championships in Athletics begin? | August 3, 2001 | not run | not run |
| 308606 | In what year did the United Nations Development Programme (UNDP) in Thailand begin tracking progress on human development at a sub-national level using the Human achievement index? | 2003 | not run | not run |
| 53785948 | In what year did Jason Gilchrist become the top scorer in the third season under English football's new title of National League? | 2017 | not run | not run |
| 848405 | In what season did Duncan Ferguson play 38 league games and score 15 league goals for Dundee United in the Scottish Premier Division? | 1991-1992 | not run | not run |
| 1688653 | In what year did the 67th Legislature of the Montana House of Representatives convene? | 2021 | not run | not run |
| 17158820 | Boatswain's mate (United States Navy) |  | not run | not run |
| 426743 | Graph coloring |  | not run | not run |
| 2525308 | In what year was the most recent season for which the Women's National Basketball League awarded the Most Valuable Player to Isobel Borlase? | 2025 | not run | not run |
| 764257 | In what month and year were the existing Air Force research laboratories merged into four superlabs? | 1990-12 | not run | not run |
| 35734292 | In what year was the Dowry Prohibition Act, which prohibits families from taking a dowry punishable with imprisonment, passed in India? | 1961 | not run | not run |
| 1610581 | Voltage-gated calcium channel |  | not run | not run |
| 578812 | In what season did the Louisville Thunder win their only National Professional Soccer League championship? | 86–87 | not run | not run |
| 357365 | On what month, day, and year did Lucien Louis Joseph Napoleon Bonaparte, 4th Prince of Canino and Musignano and later a Cardinal, die? | November 19, 1895 | not run | not run |
| 40504132 | On what month, day, and year did the 1994 World Rowing Championships begin? | September 11, 1994 | not run | not run |
| 179241 | In what year did Michael Warren begin his term as President and CEO of Canada Post? | 1981 | not run | not run |
| 52024346 | In what year was the television series Atypical nominated for the Satellite Awards in the Best Musical or Comedy Series category? | 2018 | not run | not run |
| 56316870 | In what year did Quinn Hughes win the James Norris Memorial Trophy? | 2024 | not run | not run |
| 2454457 | In what week of the 1975 NFL season did the Minnesota team first achieve a 10–0–0 record in the Central division? | Week 10 | not run | not run |
| 129801 | Portsmouth, Ohio |  | not run | not run |
| 1438469 | On what month, day, and year did the IRT Lexington Avenue Line platforms at Grand Central–42nd Street station open? | July 17, 1918 | not run | not run |
| 2326934 | In what year was the Seventeenth Dynasty of Egypt established? | c. 1580 BC | not run | not run |
| 2444452 | Ion Țiriac |  | not run | not run |
| 488965 | On what month, day, and year was Frank McCloskey formally installed as the successor for Indiana's 8th district in the 99th United States Congress? | May 1, 1985 | not run | not run |
| 3611140 | In what year did LFLS Kaunas win the top division of professional football in Lithuania during the Interbellum period? | 1922 | not run | not run |
| 1313008 | In what year were the United States Senate elections held that included candidates such as D 38 Fla. and R 39 N.J. running? | 1952 | not run | not run |
| 447977 | What month, day, and year was the last ship of the Gato class commissioned? | April 21, 1944 | not run | not run |
| 2465491 | In what year did Terry Jones start his tenure as Editor-in-Chief of the United Kingdom edition of i-D magazine? | 1980 | not run | not run |
| 2453900 | In what week of the 57th regular season of the National Football League did the Dallas team first achieve a 4–0–0 record in the East division? | Week 4 | not run | not run |
| 463116 | In what year was the Norm Smith Medal first awarded? | 1979 | not run | not run |
| 6627016 | In what year did the Calcutta Football League first have its matches broadcast by Tara Newz? | 2005 | not run | not run |
| 143451 | Province of Cádiz |  | not run | not run |
| 5776334 | Kateryna Volodko |  | not run | not run |
| 464836 | In what year did Ant McPartlin first appear as the character PJ in the television series Byker Grove? | 1990 | not run | not run |
| 35898391 | In what year was the number of native Satawalese speakers recorded as 500? | 2016 | not run | not run |
| 1135 | On what month, day, and year did Abner Doubleday begin his command of the I Corps in the Army of the Potomac? | July 1, 1863 | not run | not run |
| 2458670 | In what year was the NHL season held when Gump Worsley and Ed Giacomin were named to the All-Star teams? | 1967 | not run | not run |
| 14907 | What is the range of the usual principal value of the arccos inverse trigonometric function? | 0 ≤ cos⁻¹ | not run | not run |
| 8903118 | In what year did the movie Agnisakshi win the most Kerala State Film Awards? | 1998 | not run | not run |
| 108729 | In what month and year was Simsbury, Connecticut incorporated as a town? | 1670-05 | not run | not run |
| 1243492 | In what season did Alana Beard win the first John R. Wooden Award for women? | 2003-2004 | not run | not run |
| 5801331 | In what year was the highest amateur football league in the Netherlands, known as the Tweede Divisie, originally founded? | 1956 | not run | not run |
| 1448951 | On what month, day, and year was John W. Moore installed as the successor for Kentucky's 3rd district after Charles W. Roark died? | June 1, 1929 | not run | not run |
| 350267 | On what month, day, and year did the Penarth Extension Railway Act 1876 receive royal assent? | August 11, 1876 | not run | not run |
| 66345 | In what year did Robin Givens appear in the film titled 'Boomerang'? | 1992 | not run | not run |
| 2604805 | In what week of the 1968 NFL season did the Minnesota team first have a losing record in the Central Division standings? | Week 3 | not run | not run |
| 191105 | On what month, day, and year did the original release of Schoolhouse Rock! begin? | January 6, 1973 | not run | not run |
| 2159571 | On what month, day, and year was Daniel Inouye formally installed as the successor for the new Hawaii at-large seat after Hawaii achieved statehood? | August 21, 1959 | not run | not run |
| 2317530 | Tommy McDonald (American football) |  | not run | not run |
| 5592225 | On what month, day, and year did the Pahela Baishakh attack on Ramna Batamul in Bangladesh occur? | April 14, 2001 | not run | not run |
| 5643269 | In what year was the California Government Operations Agency created to help modernize the government? | 2012 | not run | not run |
| 18117921 | South Bird's Head languages |  | not run | not run |
| 713664 | In what year did India develop the formal hierarchical system of gun salutes during the British Raj as listed in the table? | 1947 | not run | not run |
| 19908651 | 1994 PPG Indy Car World Series |  | not run | not run |
| 24205 | In what year was the first Prometheus Award given? | 1979 | not run | not run |
| 1001441 | In what season did Luis García play for Liverpool in the Premier League and make 29 league appearances? | 2004-2005 | not run | not run |
| 618149 | In what year did John McTiernan win the Hochi Film Award for Best International Picture for the film Die Hard? | 1989 | not run | not run |
| 188780 | In what year did the production of the Ford Taunus begin? | 1939 | not run | not run |
| 529237 | In what year did the College of Idaho win the NAIA Single Division Baseball National Championship? | 1998 | not run | not run |
| 26113731 | In what year did Eric Murray and Hamish Bond win the Lonsdale Cup together? | 2012 | not run | not run |
| 1226514 | On what month, day, and year did the Formula One fatal accident involving Peter Collins occur? | August 3, 1958 | not run | not run |
| 62284195 | Patrick Surtain II |  | not run | not run |
| 3690441 | Billy Kilmer |  | not run | not run |


## Rejected And Rerun Decisions

| Page ID | Stage | Exact reason | Page/question |
| ---: | --- | --- | --- |
| 380845 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=5` | List of countries by GDP (nominal) |
| 18618509 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=84` | Wikimedia Foundation |
| 22943 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Papua New Guinea |
| 14649921 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=83` | List of largest cities |
| 16795291 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_time_invariance_forbidden_phrase:recent` | In what year did the Boston Celtics and San Francisco/Golden State Warriors most recently face each other in the NBA Finals? |
| 4829 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:present` | Balkans |
| 26828 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Suriname |
| 13270 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year was the Hawaii state quarter released? |
| 324 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Walt Disney receive his first Academy Award? |
| 8099 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year did Dave Grohl make an uncredited cameo appearance in the television series The X-Files? |
| 147311 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Ray Charles make his first voice and final film role in Blue's Big Musical Movie? |
| 8522 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information or usable data to generate a Date-type question.` | Denver |
| 34953684 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information or any factual data suitable for generating a Date answer type question.` | Charli XCX |
| 31150160 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=9` | 2011 Tōhoku earthquake and tsunami |
| 160904 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=7` | List of English monarchs |
| 11759 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | McDonnell Douglas F-4 Phantom II |
| 63973 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=18` | Wi-Fi |
| 32905 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:table` | As of what month and year were the largest private employers in West Virginia ranked in the provided table? |
| 45661106 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=35` | Top Gear (2002 TV series) |
| 270673 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year was the £100 coin, which has unlimited legal tender status, first produced? |
| 7892 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year did David Cronenberg win the Silver Bear award at the Berlin International Film Festival for the film eXistenZ? |
| 21222169 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=meter,mw` | James McAvoy |
| 174716 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Roger Moore |
| 1564433 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | Scheduled Castes and Scheduled Tribes |
| 32388 | `route_generation` | `wikipedia_infobox_llm_discarded:No date or year values present in the table to generate a Date answer type question.` | Victoria, British Columbia |
| 398602 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did William H. Macy play the role of Jerry Lundegaard in the film Fargo? |
| 88213 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date information; no date-type factual question can be generated.` | Apsis |
| 2949977 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | Allied-occupied Germany |
| 3164979 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | In what year did Josh Hutcherson host an episode of Saturday Night Live? |
| 164939 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the Airbus A330-300 variant take its maiden flight? |
| 33295 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what month and year were the solstices and equinoxes adopted as Lesser Sabbats by members of the Bricket Wood coven? |
| 8429 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:approximate,approximately` | Density |
| 18932702 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Alan Moore |
| 3372377 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=bytes,km` | Optical fiber |
| 31130 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:latest` | Thuringia |
| 659310 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Mary-Louise Parker perform in the Broadway production of "Bus Stop"? |
| 89775 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=44` | Virginity |
| 25211041 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ml` | Puberty |
| 25168720 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | On what month, day, and year was the first theatrical release of the movie Twilight? |
| 22645 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=m` | Orkney |
| 32066 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date answer type question.` | Ulster |
| 416798 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=24` | History of the Jews in Poland |
| 3569822 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | In what year did the film A Beautiful Mind win the Academy Award for Best Picture? |
| 31921 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=10` | University of California |
| 23295 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=1` | Printing press |
| 19373302 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year did Christina Applegate play the role of Veronica Corningstone in the film Anchorman: The Legend of Ron Burgundy? |
| 202295 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | In what year was the basketball club UNICS Kazan founded? |
| 143117 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the Old Gujarati language, from which Gujarati is descended, exist until? |
| 34411 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=14` | Zodiac |
| 12186 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Guinea-Bissau |
| 5643 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information or usable data to generate a Date-type question.` | Channel Islands |
| 19653842 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Organism |
| 149561 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Donna Summer |
| 347422 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | Republika Srpska |
| 58846 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year did the reform and mergers of French regions, such as the creation of Grand Est from Alsace, Champagne-Ardenne, and Lorraine, take place? |
| 47734 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | On what month, day, and year was Chhattisgarh granted statehood with Raipur as its designated state capital? |
| 39458161 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Xbox One |
| 225502 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Ann-Margret star in the film Tommy where she was nominated for an Academy Award for Best Actress? |
| 30374 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Taekwondo |
| 217231 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What month, day, and year was the DVD for Season 1 of Curb Your Enthusiasm released in Region 1? |
| 23473595 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:approximate,approximately` | Light-year |
| 158177 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | In what year did Condoleezza Rice begin her term as United States Secretary of State? |
| 184860 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | In what year did Norah Jones make her film debut in My Blueberry Nights? |
| 19006979 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | Mac (computer) |
| 53273 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | As of what year are the national program rankings listed in the Duke University rankings and reputation table? |
| 400595 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year did Patricia Arquette play the role of Olivia Evans in the film Boyhood? |
| 48235 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=1` | Vaudeville |
| 39848 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=41` | Chevrolet |
| 42374 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,ha,km,mi,mw,m` | Ljubljana |
| 23976719 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the Rugby Football Union begin according to the football codes board? |
| 38962787 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did The Blacklist win the Primetime Creative Arts Emmy Award for Outstanding Stunt Coordination for a Drama Series, Miniseries, or Movie? |
| 85629 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year did Mary-Kate Olsen and Ashley Olsen win the Young Artist Award for Best Young Actor/Actress Under Five Years of Age? |
| 50853 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=15` | Holy Roman Emperor |
| 48129 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:unknown` | Alsace |
| 166410 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information; it only lists administrative divisions and their names in Chinese and Pinyin, which cannot support a Date answer type question.` | Yunnan |
| 959699 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | The Doctor |
| 160112 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,mw` | Order of Canada |
| 85099 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Watford F.C. first have Puma as their kit manufacturer? |
| 25534 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information, so it cannot support a Date answer type question.` | Romanian language |
| 29369 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=2` | Sex organ |
| 19525 | `route_generation` | `wikipedia_infobox_llm_discarded:No date information is present in the provided table or nearby text to support a Date answer type question.` | Muay Thai |
| 3469 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=1` | British Virgin Islands |
| 8196151 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=32` | List of states of Mexico |
| 501984 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what date did the Mexican troops under President General Antonio López de Santa Anna begin their march into San Antonio de Béxar during the Battle of the Alamo? |
| 142715 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw,tonnes,m` | Emirates (airline) |
| 15147 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | On what month, day, and year was the International Olympic Committee formed? |
| 27680 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=3` | Supernova |
| 81024 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=miles` | Pan Am |
| 21132373 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | In what year did Jeff Goldblum perform in the play "The Pillowman" at the Booth Theatre on Broadway? |
| 20596557 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=oz,g` | Watermelon |
| 32498 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=barrel,cubic metre,gallon,litre,metre,ounce,ounces,yd` | Volume |
| 8397 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information for awards or nominations, only counts, so it cannot support a Date answer type question.` | Danny Elfman |
| 97851 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information to form a valid Date answer type question.` | Australian Open |
| 6967012 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Seth Green first appear in the film "Austin Powers: International Man of Mystery"? |
| 45371 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did Dominique Baudis end his term as mayor of Toulouse? |
| 63503 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information or usable data to generate a Date-type question.` | Duluth, Minnesota |
| 178796 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Saskatoon Hilltops Canadian football junior club established? |
| 150473 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Shreveport, Louisiana |
| 25336 | `route_generation` | `wikipedia_infobox_no_tables` | Quantum entanglement |
| 7043 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information to form a Date-type question.` | Chemical formula |
| 11472953 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:table` | In what year did Toni Kroos score the highest number of goals for the Germany national team according to the appearances and goals by national team and year table? |
| 18823 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Mary Pickford |
| 309661 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Gauteng |
| 5070109 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw,tons` | Spanish Armada |
| 21272 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,kg,mw` | Neutron |
| 542300 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a valid Date answer type question.` | Ilkhanate |
| 129368 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the film Rain Man win the Academy Award for Best Picture? |
| 21438242 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=55` | Lava |
| 4497 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Bugatti |
| 2822936 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the soundtrack album for Titanic: Music from the Motion Picture released? |
| 508593 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | In what year did Rip Torn appear in the television film "Sophia Loren: Her Own Story"? |
| 80666 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date, year, or month information; it only lists Vedas, recensions, shakhas, and principal Upanishads without any temporal data.` | Upanishads |
| 225073 | `route_generation` | `wikipedia_infobox_table_score_below_minimum:table_score_below_minimum:min_table_score=0.0000;best_score=-0.4000` | He (pronoun) |
| 140537 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | In what year was the 2021 reissue of the twelfth and final studio album by the English rock band the Beatles charted on the Australian Albums (ARIA) chart? |
| 50030 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | La Marseillaise |
| 44944 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:approximately` | 'Ndrangheta |
| 69442 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=9` | Waterfall |
| 931406 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | Royal Canadian Air Force |
| 236850 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Conflict of interest |
| 67135 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=145` | Tatarstan |
| 428979 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,kg,lb,yards,m` | Michael Vick |
| 25721 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | What month, day, and year was the Blu-ray release date for Series XI of Red Dwarf in Region A? |
| 81726 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=degrees` | Santa Cruz, California |
| 30148 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=22` | Tokelau |
| 23087494 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Lily Collins |
| 6127993 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=m` | UTC+00:00 |
| 566405 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:citation needed` | Saltwater crocodile |
| 341111 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km` | List of islands in the Pacific Ocean |
| 167975 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year did Peter Ustinov begin his term as Chancellor of the University of Durham? |
| 26365423 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what date did Hawaii Five-0 win the People's Choice Award for Favorite New TV Drama? |
| 52052 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=7` | Mainland Southeast Asia |
| 12104 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information suitable for forming a Date answer type question.` | Guglielmo Marconi |
| 228592 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=3` | Lottery |
| 804161 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=13` | TotalEnergies |
| 58733 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=12` | Staffordshire |
| 17015903 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was Abduwali Muse convicted and sentenced to prison for his role in the hijacking of the MV Maersk Alabama? |
| 44731 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,kg,mg,mw,g` | Calcium carbonate |
| 150374 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date answer type question.` | Self-harm |
| 17166443 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,m` | Isles of Scilly |
| 11062 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=4;no_incomplete_tables:approximate,citation needed` | Friction |
| 70962 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,km,mi,mw,m` | Hawaiʻi (island) |
| 647757 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=39` | United States women's national soccer team |
| 18436536 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the film 2012 win the Satellite Award for Best Visual Effects? |
| 54060 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year did the parliamentary constituency of St Marylebone change to Westminster North? |
| 22080893 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | In what year did Ellie Kemper play the role of Becca in the film Bridesmaids? |
| 29963050 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the final match of the 58th season of Europe's premier club football tournament organised by UEFA held at Wembley Stadium, London? |
| 3155 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Lockheed AC-130 |
| 15530283 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information, so no valid Date-type question can be generated.` | List of paraphilias |
| 182553 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table lists districts and neighbourhoods of Plovdiv without any date or temporal information, so it cannot support a Date answer type question.` | Plovdiv |
| 50556 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was King James V, son of James IV, born? |
| 44757 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the University of California, Irvine become a member of the Association of American Universities? |
| 5681823 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=1` | Knight's Cross of the Iron Cross |
| 2184258 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Nandamuri Balakrishna |
| 206481 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what historical period were the Elamite god Humban worshiped by Persians? |
| 483492 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Martin Freeman perform in the play titled 'Richard III' at Trafalgar Studios? |
| 46380 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | Coaxial cable |
| 665172 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=7` | Las Vegas Valley |
| 29408 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Samuel Taylor Coleridge |
| 989692 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Peter Sarsgaard perform the role of Hamlet at the Classic Stage Company? |
| 14349 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Harmonica |
| 10223 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table contains phoneme data without any date or temporal information, so it cannot support a Date answer type question.` | Estonian language |
| 278513 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Adam West play the role of Bruce Wayne / Batman in the film titled 'Batman'? |
| 28135 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table 'Slovene vowels' does not contain any date or year information, so it cannot support a Date answer type question.` | Slovene language |
| 1053453 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Garth Lagerwey begin his tenure as general manager of Real Salt Lake? |
| 518192 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:alpha_character_rate=0.4773` | Need for Speed |
| 43591321 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a valid Date answer type question.` | Asus |
| 26865 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=16` | List of leaders of the Soviet Union |
| 173652 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=8` | Hemorrhoid |
| 81088 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=38` | List of cities and counties in Virginia |
| 457055 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=48` | Comune |
| 618770 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Dianne Wiest perform the role of Cassandra in the play Agamemnon at the Delacorte Theatre? |
| 166215 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Faculty of Pharmaceutical Sciences at the University of Tokyo founded? |
| 525314 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:list` | In what year was the film nominated by the American Film Institute for its Top 10 Animation Films list? |
| 17627213 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=99` | List of music recording certifications |
| 313646 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a valid Date answer type question.` | Western Cape |
| 145415 | `route_generation` | `wikipedia_infobox_no_tables` | Division (military) |
| 37284 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:unknown` | Brain tumor |
| 186191 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:image_cell_rate=0.6667` | T-72 |
| 267235 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Super Rugby |
| 55023 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the Jin dynasty begin? |
| 6313 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=1` | Classical element |
| 46709 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km,mi` | County Cork |
| 218232 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=2` | ITunes Store |
| 204971 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | Historic counties of England |
| 113288 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the FK Vojvodina football club founded? |
| 57708 | `route_generation` | `wikipedia_infobox_llm_discarded:No date or year information available in the table to form a valid Date answer type question.` | Topeka, Kansas |
| 532125 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date information to form a Date-type question.` | UEFA Euro 2000 |
| 54761 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the report published that identified Wang and Li as the most common Chinese surnames, each shared by over 100 million people in China? |
| 3201113 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Eric Dane first appear in the television series Grey's Anatomy? |
| 1118679 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Domino's Pizza begin sponsoring the British soap opera Hollyoaks? |
| 7199 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=94;no_incomplete_tables:citation needed` | List of cat breeds |
| 33883 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Wade–Giles |
| 6787 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Chiapas |
| 8724 | `route_generation` | `wikipedia_infobox_no_tables` | Doppler effect |
| 164225 | `route_generation` | `wikipedia_infobox_table_score_below_minimum:table_score_below_minimum:min_table_score=0.0000;best_score=-2.0000` | Japanese name |
| 751489 | `route_generation` | `wikipedia_infobox_no_tables` | Summit |
| 44723 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=4` | Printing |
| 14985 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Edward Pearson Warner begin his term as president of the International Civil Aviation Organization council? |
| 66575 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mg` | Nutrient |
| 598459 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Greg Kinnear play the role of John F. Kennedy in the television series The Kennedys? |
| 54476844 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=4` | Boolean algebra |
| 3364 | `route_generation` | `wikipedia_infobox_no_tables` | Bit |
| 16858 | `route_generation` | `wikipedia_infobox_llm_discarded:The answer is a term length, not a specific date or year, so it does not meet the Date answer type requirement.` | Knights of Columbus |
| 143062 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year did the general election occur after which West Sussex has been represented by three Conservative, three Labour, and three Liberal Democrat Members of Parliament? |
| 143100 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Provinces of Ireland |
| 29359 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=9` | Sinhalese people |
| 146607 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information or factual data suitable for generating a Date-type question.` | Al-Ghazali |
| 49681637 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=miles,mw` | Mindhunter (TV series) |
| 19947 | `route_generation` | `wikipedia_infobox_no_tables` | Mannerism |
| 332961 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Greater Sudbury |
| 269645 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Tim Conway win the Primetime Emmy Award for Outstanding Individual Performance in a Variety or Music Program for the first time? |
| 745082 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Lee Majors play the role of Frank Harbin in the film Strait-Jacket? |
| 440038 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:image_cell_rate=0.3889` | 1918 United Kingdom general election |
| 500004 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=1` | On-Line Encyclopedia of Integer Sequences |
| 70566 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | Valparaíso |
| 638381 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Charles Durning make his Broadway debut in the play Poor Bitos? |
| 206997 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Hermann zu Hohenlohe-Langenburg begin his term as Imperial Governor of Alsace–Lorraine? |
| 477968 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In the sexagenary cycle, what is the designation of the 17th term? |
| 77783 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km,miles,mw` | Guildford |
| 1690376 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information, so no valid Date-type question can be generated.` | List of legal entity types by country |
| 227690 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=kw,mw,m` | Kei car |
| 154809 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | McDonnell Douglas |
| 21140 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date information to support a Date answer type question.` | Noble gas |
| 141390 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Gordie Howe receive the NHL Lifetime Achievement Award? |
| 1099413 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=43` | Orbital eccentricity |
| 344462 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did cross country running first appear in the Olympic Games? |
| 2471540 | `route_generation` | `wikipedia_infobox_table_score_below_minimum:table_score_below_minimum:min_table_score=0.0000;best_score=-2.0000` | Security hacker |
| 371516 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what century was the Glauberg kings graves site in Wetteraukreis, Hesse dated to? |
| 293632 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year was the subgenre popularity data for romance novels in the United States recorded? |
| 31923 | `route_generation` | `wikipedia_infobox_llm_discarded:No date or year information is provided in the table to support a Date answer type question.` | University of California, Santa Cruz |
| 27123 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | Saarland |
| 304691 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information to form a valid Date answer type question.` | Larry Brown (basketball) |
| 13830 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=2` | Hastings |
| 8254 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the thermionic diode invented by John Ambrose Fleming? |
| 256305 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Santa Catarina (state) |
| 3270829 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | List of Dragonlance novels |
| 2839975 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:citation needed` | Locus (genetics) |
| 62633 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Les Invalides |
| 17733874 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=78` | Potential enlargement of the European Union |
| 76165 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the Pontiac automobile brand officially declared defunct? |
| 89276 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=metre,metres` | Sprint (running) |
| 598491 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Timothy Hutton star in the film Ordinary People? |
| 268075 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year were the QS World University Rankings by broad subject area published that included the University of Hong Kong's world ranks? |
| 592311 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the International Tennis Federation formed? |
| 172911 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=10` | Nuclear weapon design |
| 357520 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=m` | Disney anthology television series |
| 405944 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=38` | Time complexity |
| 412827 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion,trillion` | Guanajuato |
| 188497 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or temporal information to support a Date answer type question.` | Femur |
| 372315 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=12` | Moscow Oblast |
| 443459 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Miranda Otto perform the role of Nora Helmer in the play A Doll’s House with the Sydney Theatre Company? |
| 867865 | `route_generation` | `wikipedia_infobox_llm_discarded:No date or temporal values present in the table to form a Date answer type question.` | Warsaw Ghetto Uprising |
| 56099 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:present` | Red dwarf |
| 847879 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=2` | Age of the universe |
| 173109 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=1` | Warped Tour |
| 1171713 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=31` | Cerezo Osaka |
| 26288711 | `route_generation` | `wikipedia_infobox_no_tables` | Coulomb's law |
| 59742 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=4` | Menorca |
| 17643 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date, year, or month information to form a valid Date answer type question.` | Lavandula |
| 77260 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=2` | Olmecs |
| 26897 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=tonnes` | Spice |
| 59733 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Hexagon |
| 24795 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Private (rank) |
| 20491903 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=1` | Velocity |
| 505173 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | NAC Breda |
| 31039 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | Turboprop |
| 2517159 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Mike Bobo previously serve as an Offensive Analyst for Georgia before becoming the Offensive coordinator / quarterbacks? |
| 963887 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the University of South Carolina founded? |
| 137193 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:latest` | St. George, Utah |
| 577473 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was All India Radio officially launched? |
| 1787105 | `route_generation` | `wikipedia_infobox_table_score_below_minimum:table_score_below_minimum:min_table_score=0.0000;best_score=-0.4000` | Animal sexual behaviour |
| 32551521 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=14` | FIFA eligibility rules |
| 58685 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information, so it cannot support a Date answer type question.` | Hypothalamus |
| 1069583 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table and text do not contain any date or year information; thus, no valid Date answer question can be generated.` | Dattatreya |
| 56668 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a valid Date answer type question.` | Apricot |
| 4595410 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=153` | 1970 United States census |
| 333199 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw,m` | SkyTeam |
| 34062 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=hz` | WAV |
| 782140 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information; no suitable Date answer type question can be generated.` | The Shard |
| 104944 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was Charles XII of Sweden born? |
| 34382035 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:approx.` | Phases of clinical research |
| 320965 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=miles,ton` | Pennsylvania Railroad |
| 379971 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | In what year did the album In Utero achieve its peak chart positions listed in the weekly chart performance table? |
| 10328596 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information for Unicode characters, so no valid Date answer question can be generated.` | List of Unicode characters |
| 296565 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information; it only contains a legend for NFL career achievements without any date values.` | Steve Young |
| 65508 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=11` | Great Seal of the United States |
| 151069 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was Maximilian II, Holy Roman Emperor, born? |
| 72227 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:list` | In what year did Joyce list the general indication of grading rules for typical Western plywood grades? |
| 11315968 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | Youth Olympic Games |
| 430074 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_time_invariance_forbidden_phrase:current` | In what century did Jarudism take over as the dominant current among Zaydis according to the theological distinctions between Batri and Jarudi? |
| 34050 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=5` | Warrant officer |
| 396394 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | National Assembly of Quebec |
| 845294 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=7` | Service star |
| 1780815 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=7` | Radius |
| 89514 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | New London, Connecticut |
| 337740 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Bram Stoker's Dracula (1992 film) win the Academy Award for Best Costume Design? |
| 1286819 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information or data that can be answered with a Date type. It only contains a legend explaining symbols related to wins per year without actual year or date data.` | Grand Tour (cycling) |
| 3977980 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=6` | Women's Cricket World Cup |
| 4836072 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the film My Fair Lady win the Academy Award for Best Picture? |
| 59038 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=21` | Fourier series |
| 310845 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Michel Doukeris become the leader of the Anheuser-Busch subsidiary? |
| 409309 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:citation needed` | Alcohol by volume |
| 745601 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Valerie Bertinelli appear in the film titled 'Number One with a Bullet'? |
| 1978269 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the American publishing house Alfred A. Knopf, Inc. founded? |
| 543312 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | The Mars Volta |
| 1234326 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km` | Gmina |
| 377819 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Pagliacci |
| 424342 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=19` | Pepperdine University |
| 2043791 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table contains only staff positions and names without any date or temporal information, so no valid Date-type question can be generated.` | Persepolis F.C. |
| 8192 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:unknown` | Detective fiction |
| 222254 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Tamaulipas |
| 21438575 | `route_generation` | `wikipedia_infobox_no_tables` | Bass (voice type) |
| 4651 | `route_generation` | `wikipedia_infobox_llm_discarded:The answer type is not a date but a parity change indicator, so it does not meet the required Date answer type.` | Beta decay |
| 244481 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a valid Date answer type question.` | Kaifeng |
| 830589 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Bohemian F.C. |
| 118474 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what century were volumes 97 to 130 of the Patrologia Latina published according to Baronius? |
| 7632 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=1` | Cerebrospinal fluid |
| 517620 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did Tom Seaver pitch a no-hitter? |
| 77655 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=9` | Louis XII |
| 199306 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,kg,mw,g` | VX (nerve agent) |
| 8707 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the German automotive company DKW founded? |
| 70841 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=13` | City status in the United Kingdom |
| 24516 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year did Polybius write the Histories that mention the Polybius square cipher? |
| 322010 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year was the ARWU global ranking of Queen's University Belfast recorded as between 301 and 400? |
| 19811 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=acres,km,mile` | Murray River |
| 548229 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information to support a Date answer type question.` | Lili Taylor |
| 6535529 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=200` | List of airports in Alberta |
| 47238088 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | List of municipalities in West Virginia |
| 94320 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information; therefore, no valid Date-type question can be generated.` | Virus classification |
| 6355 | `route_generation` | `wikipedia_infobox_no_tables` | Chloroplast |
| 28833 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=1` | Sir Gawain and the Green Knight |
| 302617 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=m` | León, Spain |
| 7910935 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | The Penguin Guide to Jazz |
| 3540710 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | National Register of Historic Places listings in Wisconsin |
| 88446 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=31` | List of Portuguese monarchs |
| 309769 | `route_generation` | `wikipedia_infobox_no_tables` | Spanish dollar |
| 1117292 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:citation needed` | Toyota Yaris |
| 111852 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Moline, Illinois |
| 10467798 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=3` | 1989 Soviet census |
| 456601 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the Academy Award ceremony held where The Fly won Best Makeup? |
| 188537 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was Volume IV of the Dictionary of American Naval Fighting Ships published? |
| 31475895 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | Development Panel of ICC Umpires |
| 1144172 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the Sideways soundtrack album by Rolfe Kent released? |
| 8215253 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=83;no_incomplete_tables:unknown,citation needed` | A roads in Zone 4 of the Great Britain numbering scheme |
| 4109042 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year were the signaling pathways based on receptor families that control gene activity, such as Frizzled and Receptor Tyrosine Kinase pathways, first overviewed in the referenced sources? |
| 252781 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | List of governors of Pennsylvania |
| 24387628 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:citation needed` | 2010 Russian census |
| 2232427 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any specific date information or factual data suitable for generating a Date-type question.` | Suzuki Jimny |
| 3540772 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | National Register of Historic Places listings in Alaska |
| 79379 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the Cal State Northridge Matadors join the Big Sky Conference? |
| 117105 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,km,mi,mw,m` | Bay City, Michigan |
| 532922 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the television series St. Elsewhere first air on NBC? |
| 80208 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did William Westmoreland become the Superintendent of the United States Military Academy? |
| 1217448 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what month and year did the character Wolverine first appear in comics? |
| 111579 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=1` | Alton, Illinois |
| 28161 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table only contains star spectral type categories without any date information, so no valid Date-type question can be generated.` | List of brightest stars |
| 390896 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Roman Abramovich begin his term as governor of the Chukotka Autonomous Okrug? |
| 1077688 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=kg,mg,mw,g` | Catechin |
| 1582694 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=1` | Wisden Cricketers' Almanack |
| 900231 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | Team America: World Police |
| 135478 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=157` | Killeen, Texas |
| 113190 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Posthumous name |
| 180486 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,ft,m` | Oshawa |
| 217428 | `route_generation` | `wikipedia_infobox_llm_discarded:The answer type is not a Date, so the question is discarded.` | Abitur |
| 414741 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the European Coal and Steel Community established? |
| 795554 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information related to the decorations and awards, so no valid Date answer question can be generated.` | Oak leaf cluster |
| 82050 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=1` | Royal Norwegian Navy |
| 812281 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the main international basketball competition for the senior men's national teams of primarily European countries founded? |
| 2801560 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:present` | Ocean acidification |
| 30871458 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=18` | Color index |
| 7025 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or temporal information to form a valid Date-type question.` | Cranberry |
| 142207 | `route_generation` | `wikipedia_infobox_no_tables` | Singular value decomposition |
| 14558843 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Nirvana (Buddhism) |
| 183852 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Gifu Prefecture |
| 274238 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the United States Department of War removed from the Cabinet? |
| 14856 | `route_generation` | `wikipedia_infobox_no_tables` | Inner product space |
| 557097 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the International Alphabet of Sanskrit Transliteration formalized by the Transliteration Committee of the Geneva Oriental Congress? |
| 998780 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:image_cell_rate=0.2857` | Seven Days Battles |
| 18952991 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | Gila monster |
| 373452 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the frequency of performing the Deva-yajna (homa) sacrifice according to the Kalpa Sutras? |
| 42093526 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the first season of Unbreakable Kimmy Schmidt receive seven Primetime Emmy Award nominations? |
| 505086 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Dungeons & Dragons module titled 'The Elixir of Life' published? |
| 2305669 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | List of most expensive films |
| 18582 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the BBB party first win seats in the States-Provincial elections in Limburg (Netherlands)? |
| 22959267 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:citation needed` | List of Latin phrases (V) |
| 282299 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,m` | Muzzle velocity |
| 1019389 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:approx.,approximately` | Lund |
| 122386 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Starkville, Mississippi |
| 496361 | `rewrite_surface` | `rewrite_guard_rejected:forbidden_temporal_phrase` | As of what month, day, and year is the student body composition data for Sacred Heart University reported? |
| 127579 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,km,mi,mw,m` | Peekskill, New York |
| 2114 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | IBM AIX |
| 472779 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=57` | Arkhangelsk Oblast |
| 310169 | `route_generation` | `wikipedia_infobox_llm_discarded:No date-type answers available in the table to form a valid Date answer_type question.` | Indian philosophy |
| 40056 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what exact date was ski jumping first played by Olaf Rye at Eidsberg church in Norway? |
| 58278 | `rewrite_surface` | `rewrite_guard_rejected:forbidden_temporal_phrase` | In what year was the former Kansas County in Kansas dissolved into Seward County? |
| 55417368 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=34` | 2016 Australian census |
| 31958 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | United Nations Economic and Social Council |
| 46251870 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=99` | Geographical distribution of French speakers |
| 1721369 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did The Ultimate Fighter television series first release? |
| 145478 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=18` | TIFF |
| 5802344 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=7` | Baseball in Cuba |
| 99306 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | College Park, Maryland |
| 66057 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the DuMont Television Network officially launched? |
| 204019 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | Notting Hill (film) |
| 388193 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a valid Date answer type question.` | Air Koryo |
| 9413800 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a valid Date answer type question.` | Guangzhou F.C. |
| 1478772 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the New England Patriots begin their longest streak of consecutive playoff appearances? |
| 437808 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Bank of Baroda |
| 43221 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year was Dichlorodifluoromethane banned in all countries in compliance with the Montreal Protocol? |
| 864183 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year did the film Indecent Proposal win the BMI Film Music Award for John Barry? |
| 155650 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw,g` | Fluoride |
| 224021 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Hidalgo (state) |
| 62305884 | `route_generation` | `wikipedia_infobox_llm_discarded:No date or temporal values present in the table to form a Date answer type question.` | Ōshima Strait |
| 3135637 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information, so it cannot support a question with a Date answer type.` | Gut microbiota |
| 7404943 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table only contains a key for abbreviations without any actual date data, so it cannot support a Date answer type question.` | Jamie Murray |
| 497311 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=millimetres,m` | Cayenne |
| 212068 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Dario Argento act as a paramedic in the film Innocent Blood? |
| 1219810 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=5` | Historic preservation |
| 2723793 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the sire Halo, ancestor of Sunday Silence, born? |
| 330869 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=2` | Rotorua |
| 32237 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=4` | UMTS |
| 183477 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Iwate Prefecture |
| 5300318 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=77` | Districts of the Czech Republic |
| 182283 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,km,mi,mph,m` | Miles per hour |
| 58858 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:caption:current` | Regions of New Zealand |
| 154708 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=42` | List of national legal systems |
| 1038535 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | State of the Teutonic Order |
| 364879 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Billy West first voice the character Cecil in the television show The New Adventures of Beany and Cecil? |
| 19869 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=m` | Massachusetts Bay Transportation Authority |
| 48922 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Leadville, Colorado |
| 65666080 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the 125th season of the Australian Football League (AFL) take place? |
| 806560 | `route_generation` | `wikipedia_infobox_no_tables` | Contemporary philosophy |
| 2500686 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,m` | Magnitude (astronomy) |
| 844184 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,km,mi,m` | Malwa |
| 4644269 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did the 24th annual WrestleMania event take place? |
| 5964336 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information or any factual data suitable for generating a Date-type question.` | Fastest lap |
| 11037 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Freyr |
| 639573 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=105` | Dry Tortugas National Park |
| 21391870 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year did Alan Turing prove that the halting problem is undecidable? |
| 314803 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the University of Zurich ranked 59th in the ARWU World university rankings? |
| 32099 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the University of Manitoba founded as the first university in Western Canada? |
| 1088294 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=13` | Demographics of sexual orientation |
| 1782201 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Kleshas (Buddhism) |
| 108346 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Beale Air Force Base |
| 45032 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information related to the seat counts, so no valid Date answer question can be generated.` | Dordogne |
| 588111 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the Rs. 10/- coin of the official currency of the Islamic Republic of Pakistan first enter circulation? |
| 174706 | `route_generation` | `wikipedia_infobox_no_tables` | Laplace operator |
| 1189137 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=3` | Joe McCarthy (baseball manager) |
| 922245 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:caption:current` | Swimming at the Summer Olympics |
| 18308 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information to support a Date answer type question.` | Lanthanide |
| 83324 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did Jim Bunning pitch a perfect game? |
| 10017154 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the Indiana Hoosiers men's basketball team win the NCAA National Championship by defeating Michigan in the final game? |
| 3790938 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=6` | Western theater of the American Civil War |
| 2019918 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information or factual data suitable for generating a Date answer type question.` | List of NFL Most Valuable Player awards |
| 4557237 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=224` | List of solar eclipses in the 21st century |
| 34417 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or temporal information to form a Date-type question.` | Zero-sum game |
| 999303 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:table` | According to the USGA Handicap System overview table, when a golfer has submitted 11 or 12 rounds, how many lowest differentials are used to calculate the handicap index? |
| 2510506 | `route_generation` | `wikipedia_infobox_llm_discarded:The table is empty and does not contain any date information to support a Date answer type question.` | Indo-Aryan migrations |
| 82022 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=72` | Merced County, California |
| 5050 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Bill Bryson begin his term as Chancellor of Durham University? |
| 9938623 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Michelle O'Neill begin serving as Vice President of Sinn Féin? |
| 317435 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Finnish Air Force founded? |
| 524875 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Voiced postalveolar fricative |
| 74160 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Kevin Sorbo play the role of Kull in the film Kull the Conqueror? |
| 2140677 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the rivalry known as the Battle of the Birds between Sydney Roosters and Manly Warringah Sea Eagles begin? |
| 839943 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Bone fracture |
| 18424 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what years were the labia and other genital structures of 50 women measured in the study conducted by the Department of Gynaecology at Elizabeth Garrett Anderson Hospital in London? |
| 287264 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | On what date did NORAD propose the adoption of the readiness conditions of the Joint Chiefs of Staff system? |
| 82075 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=90` | Santa Cruz County, California |
| 1439959 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what century did Prudentius write the poem Psychomachia that allegorically represented Christian morality as a struggle between seven sins and seven virtues? |
| 3775531 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the final match of the 1994–95 UEFA Champions League held at Ernst-Happel-Stadion in Vienna? |
| 3253221 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=713` | African Games |
| 512470 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Rubber band |
| 579089 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the ECAC Hockey conference founded? |
| 30931401 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Dutch Caribbean |
| 145612 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=11;no_incomplete_tables:approximately` | Ludwigshafen |
| 41920 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=2` | Compact Disc Digital Audio |
| 448061 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=107` | Isfahan province |
| 109566 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=10` | Winter Park, Florida |
| 251405 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=105` | Charlestown, Boston |
| 27884299 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information or usable data to generate a Date-type question.` | Danville, Illinois |
| 1073488 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Keeley Browse win the Sir Terry Wogan Fundraiser of the Year Award? |
| 571630 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:approx.` | Venus figurine |
| 2648955 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=5` | List of weapons in the American Civil War |
| 4601182 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date answer type question.` | Senegalese Football Federation |
| 213948 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the Group of 77 formed? |
| 152333 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:present` | Provinces of Belgium |
| 51963 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Steinway & Sons acquire the company Louis Renner GmbH? |
| 434937 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | On what month, day, and year was the title King of Italy officially formed? |
| 45186 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Utah Flash basketball team established? |
| 545518 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Indiana win its first NCAA Division I men's soccer tournament championship? |
| 1908748 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=103` | Vehicle registration plates of Poland |
| 306966 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Kataeb Party |
| 7349689 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:active` | Satellite Catalog Number |
| 404595 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the NCAA Division I Football Championship first take place at Paulson Stadium in Statesboro, Georgia? |
| 179573 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | Krefeld |
| 58576 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=gal` | Lawrence Welk |
| 457235 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km,mi,mw` | Helmand Province |
| 8802070 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | List of major commands of the United States Air Force |
| 502038 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Question |
| 24577701 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=centimeters,cm` | Kent, Ohio |
| 231676 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=19;no_incomplete_tables:citation needed` | Skirt |
| 227335 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Olivia Hussey play the role of Mary, Mother of Jesus in the miniseries Jesus of Nazareth? |
| 116362 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Towson, Maryland |
| 6793142 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Niigata Albirex BB basketball club established? |
| 4668 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=pascal` | Binomial coefficient |
| 203688 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | At what historical time of day is the Sixth Hour (Sext) service traditionally held according to the daily cycle of canonical hours? |
| 448514 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mile,mw` | Tom Arnold (actor) |
| 6793346 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Kumamoto |
| 753103 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Chicago Police Department |
| 832492 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what month and year did the Radio Free Asia Tibetan language service launch? |
| 458469 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the Progressive Conservative Association of Alberta begin its uninterrupted run as the governing party of Alberta? |
| 239964 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ml,mw` | F Sharp (programming language) |
| 42106513 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Batman: Arkham Knight |
| 275932 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=m` | County Louth |
| 118790 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,km,mi,mw,m` | Royal Oak, Michigan |
| 70748 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month and day is the birthday of King Willem-Alexander, also known as Koningsdag (King's Day), officially celebrated according to the Dutch flag-flying days? |
| 148730 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Cheshire Cat as illustrated by John Tenniel first published? |
| 81600 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information, so no valid Date answer question can be generated.` | List of counties in Colorado |
| 634316 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw,g` | Prednisolone |
| 57853 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=14` | Pierre, South Dakota |
| 714452 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Chronic kidney disease |
| 191300 | `route_generation` | `wikipedia_infobox_llm_discarded:The answer is not a date, month, or year, which is required by the prompt for answer_type Date.` | Glossary of Buddhism |
| 239528 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | What month, day, and year did the Founding Conference of the Independent Labour Party take place? |
| 646771 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=degrees` | Clear Channel memorandum |
| 91287 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:present` | Manassas, Virginia |
| 64100 | `route_generation` | `wikipedia_infobox_no_tables` | Serif |
| 220713 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=28` | Kumamoto Prefecture |
| 82208 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | International Mathematical Olympiad |
| 5596305 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:incomplete` | Sushruta Samhita |
| 4483507 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=100` | 1820 United States census |
| 452226 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=30` | Utah Territory |
| 701802 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | On what month, day, and year did Chip Roy become chair of the subcommittee on The Constitution and Limited Government in the 118th Congress? |
| 50387 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,mw,tons,m` | Containerization |
| 431272 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | Commissioner |
| 2467 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=152` | Aargau |
| 26541290 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Bundesverband Musikindustrie formed? |
| 632929 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What month, day, and year was the first episode of the first season of Joey originally released? |
| 58062027 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what dates was the 2018 World Series played? |
| 76216 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km,mi` | List of regions of Quebec |
| 1480126 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=4` | Underwater habitat |
| 14381 | `route_generation` | `wikipedia_infobox_no_tables` | Hamiltonian (quantum mechanics) |
| 880497 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:present` | Linoleic acid |
| 83171 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=170` | Laon |
| 2667490 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=4` | Ashton Gate (stadium) |
| 2065189 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table only contains symbols and their meanings, not any date information; therefore, no valid Date-type question can be generated.` | 1995 NBA draft |
| 551604 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=8` | Pee-wee Herman |
| 19836 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=g` | Molecular mass |
| 208144 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=79` | X chromosome |
| 372308 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to answer a Date type question.` | Sakhalin Oblast |
| 166004 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:caption:latest` | Drupal |
| 171581 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year were the 65th Academy Awards held? |
| 535649 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km,mi` | List of municipalities in Louisiana |
| 41944809 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what month, day, and year was the 2015 Major League Baseball draft held to assign amateur baseball players to MLB teams? |
| 237014 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information, so no valid Date-type question can be generated.` | Quorum |
| 17484978 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the time period defined for the initial phase of cold water immersion syndrome known as cold shock? |
| 75149 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year did AZS AJP Gorzów Wielkopolski women's basketball team win the Polish Cup? |
| 107991 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=4` | Chino, California |
| 309257 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Whistler, British Columbia |
| 597263 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to support a Date answer type question.` | Near-open front unrounded vowel |
| 111021 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | Northbrook, Illinois |
| 2367141 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=4` | 1993 NFL season |
| 116732 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | Taunton, Massachusetts |
| 1741957 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Wuhan Three Towns win the China League One? |
| 3663192 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=134` | National Register of Historic Places listings in Bristol County, Massachusetts |
| 130832 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Klamath Falls, Oregon |
| 6535522 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=40` | List of airports in the Northwest Territories |
| 1809036 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=24` | List of House episodes |
| 667977 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was women's basketball first played at Smith College in Massachusetts? |
| 1347879 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what century did Karaikkal Ammaiyar, one of the three female Nayanars, live? |
| 3645403 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Constitution of the Federal Republic of Nigeria, which assumes a National Assembly consisting of a Senate and a House of Representatives, established? |
| 1560673 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did IF Brommapojkarna win the Superettan league for the first time? |
| 372988 | `route_generation` | `wikipedia_infobox_no_tables` | Tamil literature |
| 329044 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Toyota Red Terriers women's softball team established? |
| 2061310 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date answer type question.` | North Central Railway zone |
| 23200639 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the 2010 Major League Baseball draft held? |
| 239002 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did BMW make its first entry in the Formula One World Championship? |
| 12745881 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did Samuel Onunaka Mbakwe take office as Governor of Imo State? |
| 160028 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Co-operative Commonwealth Federation founded? |
| 1572523 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=7` | On-board diagnostics |
| 1055466 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Edward Norton win the Golden Globe Award for Best Supporting Actor for his role in Primal Fear? |
| 283824 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Malacañang Palace property set aside as the summer residence of the Governor General by royal decrees? |
| 28857549 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=4` | Third Dynasty of Egypt |
| 39709452 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,feet` | Acceptance of evolution by religious groups |
| 181809 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=17` | M6 motorway |
| 134361 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Aiken, South Carolina |
| 252948 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | 16th arrondissement of Paris |
| 11920264 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,gal,kg,km,lb,mi,mph,m` | Bombardier CRJ100/200 |
| 3754242 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | List of Volkswagen Group diesel engines |
| 530183 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=acres,ha,km,miles` | Adirondack Park |
| 377611 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Elijah Parish Lovejoy |
| 963537 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date answer type question.` | Gloucester Rugby |
| 8910 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was Dean Koontz's novel 'Midnight' nominated for the Bram Stoker Award? |
| 2533444 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information to generate a Date-type question.` | List of roller coaster rankings |
| 1244920 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What month and year was the Dornier 228 introduced? |
| 8739635 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year did the European Parliament election in the United Kingdom, summarized by the post-election groupings of each party, take place? |
| 8246804 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=100;no_incomplete_tables:citation needed` | A roads in Zone 6 of the Great Britain numbering scheme |
| 173290 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Proton Holdings |
| 37839 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:approximately,citation needed` | Ion thruster |
| 6018611 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=27` | Switzerland–European Union relations |
| 272893 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,oz,g` | Black-crowned night heron |
| 3120845 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year was the Australian Football Council (AFC) formed, which later became responsible for the laws of Australian rules football? |
| 322808 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=12` | List of universities in Switzerland |
| 6967081 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Elisha Scott begin his international football career with the Ireland national football team? |
| 7172268 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table only contains a color key with symbols and descriptions, without any date information to support a Date answer type question.` | ISU Junior Grand Prix of Figure Skating |
| 240945 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Anne Meara perform the role of Nurse in the Joseph Papp Public Theater production of Romeo and Juliet? |
| 335537 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:list` | On what month and year was the final list of referees for the third edition of the FIFA Women's World Cup published? |
| 2311040 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | In what year did the song "Another Day in Paradise" reach its peak chart positions listed in the weekly charts table? |
| 138007 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Kirkland, Washington |
| 4433643 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information to support a Date answer type question.` | National Register of Historic Places listings in Philadelphia |
| 1460 | `route_generation` | `wikipedia_infobox_no_tables` | Asgard |
| 1652975 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:image_cell_rate=0.2667` | Appomattox campaign |
| 113441 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Morgan State College begin its presidency under Dwight O.W. Holmes? |
| 833671 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Isaac Norton Rendall begin his presidency at Lincoln University in Pennsylvania? |
| 6020545 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=12` | Demographics of Africa |
| 714729 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km` | Southern England |
| 913125 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=23` | Anti-German sentiment |
| 1326920 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date information to support a Date answer type question.` | Mexican Air Force |
| 46231 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | Super 8 film |
| 660597 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Old Trafford Cricket Ground |
| 558550 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ha` | Wylie transliteration |
| 34099767 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information, so no valid Date answer type question can be generated.` | Disability sport classification |
| 4846076 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=10` | Southwestern China |
| 14724846 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the action comedy TV series Peacemaker first air? |
| 82394 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did Julio César Chávez lose to Kostya Tszyu for the WBC light welterweight title? |
| 27442274 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Major League Baseball draft held that included the supplemental first round picks such as Brian Goodwin and Blake Snell? |
| 317860 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was Infante Juan, Count of Barcelona, born? |
| 196078 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=kg,kw,lb,mw` | Lamborghini Murciélago |
| 3878 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=4` | Biostatistics |
| 1532351 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:alpha_character_rate=0.3468` | Western Suburbs Magpies |
| 1792288 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What month, day, and year did the Soviet Union begin competing at the 1988 Summer Olympics in Seoul, South Korea? |
| 519158 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Argentina allow same-sex couples to jointly petition for adoption? |
| 387766 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=31` | Radical Party (France) |
| 80566 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=56` | Lassen County, California |
| 1565499 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:citation needed` | Human rights in North Korea |
| 171288 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the basketball club AGE Chalkida BC founded in Chalkida? |
| 1057852 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:image_cell_rate=0.4000` | 4-4-0 |
| 12641290 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date answer type question.` | Buddhist logico-epistemology |
| 8328 | `route_generation` | `wikipedia_infobox_no_tables` | Divergence |
| 578129 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did Benjamin Bullivant begin his term as Attorney General of the Dominion of New England? |
| 15717485 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Fatehgarh Sahib district record 219 road accidents? |
| 605671 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_social_science_research:census` | Census geographic units of Canada |
| 10438439 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Framing (social sciences) |
| 584665 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | Treaties of Tilsit |
| 155269 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Krzysztof Kieślowski |
| 370315 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Band-e-Amir Dragons cricket club established? |
| 39390739 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=25;no_incomplete_tables:unknown` | List of fermented foods |
| 746231 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=trillion` | Budget of NASA |
| 452048 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the film 'Sister Act' featuring Kathy Najimy as Sister Mary Patrick released? |
| 33084475 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the 2012 Major League Baseball draft held? |
| 90599 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | Bas-Rhin |
| 791662 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Ted Levine play the role of Jame 'Buffalo Bill' Gumb in the film The Silence of the Lambs? |
| 353303 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=33` | Seventeen (American magazine) |
| 637662 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:unknown` | Middle Tennessee State University |
| 1306531 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table only contains a legend with no factual date information; it does not support generating a Date answer type question.` | Sterling Sharpe |
| 11190657 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,mw,m` | Sebastian Giovinco |
| 19067583 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:incumbent` | List of first ladies of the United States |
| 11617 | `route_generation` | `wikipedia_infobox_no_tables` | Feynman diagram |
| 1182314 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=53` | Norwegian Americans |
| 4985099 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=85` | Boxing at the Summer Olympics |
| 2412855 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Administrative divisions of Armenia |
| 149283 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:citation needed` | Vukovar |
| 10497504 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,mi` | Image sensor format |
| 344536 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date information related to the classification or any other date facts; thus no valid Date answer question can be generated.` | Hepatitis A |
| 7954764 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Robert M. Rosenzweig begin his term as Executive of the Association of American Universities? |
| 1147681 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Topanga, California |
| 555625 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date information; no Date answer type question can be generated.` | 2002–03 NHL season |
| 26854708 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | In what year did the song "We Are Young" achieve its year-end chart positions listed in the table? |
| 298622 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=1` | Gorizia |
| 956857 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year did Jesse B. Thomas first serve as a Class II senator for Illinois in the United States Senate? |
| 4530612 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Jürgen Melzer |
| 7295539 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what month and year did Roy Halladay win the American League Pitcher of the Month award for the first time in the 2003 Major League Baseball season? |
| 276741 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information, so no valid Date answer question can be generated.` | Medium-density fibreboard |
| 1929375 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km,mi` | Lacombe, Alberta |
| 2457822 | `route_generation` | `wikipedia_infobox_no_tables` | Pressure swing adsorption |
| 823229 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information, only terminology related to the number of columns at the front of ancient Greek temples. Therefore, it cannot support a factual question with a Date answer type.` | Ancient Greek temple |
| 114705 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=157` | Emporia, Kansas |
| 69178 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or temporal data to form a Date-type question.` | Bilabial consonant |
| 74868 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did The Last Picture Show win the Academy Award for Best Supporting Actor? |
| 4952904 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the United States participate in the Summer Olympics held in London where Ralph Craig was the flag bearer? |
| 1292296 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | Wellington Regional Stadium |
| 8245873 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the High-End Loft Stuff pack for The Sims 3 released in North America? |
| 43610555 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=1` | Hamadan |
| 1745163 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=74` | Interim Biogeographic Regionalisation for Australia |
| 1860503 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=6` | The Apotheosis of Washington |
| 63676175 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Timeline of the COVID-19 pandemic in the United Kingdom (January–June 2020) |
| 35052231 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the restaurant Le Clos des Sens in Annecy first awarded three Michelin stars? |
| 5630920 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km` | Russian Railways |
| 49800 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | In what year were the 2002 Kids' Choice Awards, where Angelina Jolie was nominated for Favorite Butt Kicker, held? |
| 1145084 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=25` | North Eastern Railway (United Kingdom) |
| 50255 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Canadian Alliance |
| 54165 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=79` | Columbia County, New York |
| 185808 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=78` | Midland Main Line |
| 16987896 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=136` | LGBTQ rights in Africa |
| 2512977 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:alpha_character_rate=0.1480` | Vedic chant |
| 719484 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:unknown` | University of New Orleans |
| 1873300 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Vale S.A. |
| 54338 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=79` | Greene County, New York |
| 26991526 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what month and year were the Bamum script characters added to the Unicode standard? |
| 45893 | `rewrite_surface` | `rewrite_guard_rejected:forbidden_temporal_phrase` | As of what month, day, and year was the student body composition data recorded for Michigan Technological University? |
| 2048162 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the ITF Grand Prix Circuit begin? |
| 171191 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | On what month and year does Tromsø experience the midnight sun according to the sunrise and sunset times on the 15th of each month? |
| 46332935 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what season did Kalvin Phillips score 7 league goals for Leeds United in the Championship? |
| 23618017 | `route_generation` | `wikipedia_infobox_table_score_below_minimum:table_score_below_minimum:min_table_score=0.0000;best_score=-0.1000` | Central Texas |
| 1045799 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Bubba Smith first appear in the Police Academy film series? |
| 32416559 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=21` | List of acts of the Parliament of England from 1485 |
| 840505 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date answer type question.` | List of United States Naval officer designators |
| 4629650 | `route_generation` | `wikipedia_infobox_llm_discarded:No date or year information is present in the table to support a Date answer type question.` | Citation of United Kingdom legislation |
| 217809 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Jane Alexander play the role of Eleanor Bachman in the film The Great White Hope? |
| 39147 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=2` | Finite difference |
| 440479 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a valid Date answer type question.` | Influenza A virus |
| 2213051 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:list` | As of what month, day, and year is the list of Gainsborough Trinity F.C. club officials current? |
| 180747 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Saga Prefecture |
| 663861 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Private network |
| 2976107 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did The Italian Job receive a Special Achievement Award at the AAFCA Awards? |
| 1907135 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Demographics of Chicago |
| 647345 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=9` | Chiefs (Super Rugby) |
| 15290967 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information or any data suitable for generating a Date answer type question.` | 2011 Copa América |
| 597146 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information to answer a Date type question.` | Close back unrounded vowel |
| 2101553 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,g` | Saline water |
| 493118 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=10` | Counties of Lithuania |
| 15380778 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ha,kg,tons` | QF 12-pounder 12 cwt naval gun |
| 259613 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=32` | Durham, New Hampshire |
| 849500 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:image_cell_rate=0.3846` | Trent Bridge |
| 91246 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information, so no valid Date answer question can be generated.` | Spotsylvania County, Virginia |
| 5149842 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information, so it cannot support a Date answer type question.` | Kalpa (Vedanga) |
| 3898076 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:latest` | List of AMD graphics processing units |
| 70855 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=16` | Stadtholder |
| 42785028 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=9` | Tunceli Province |
| 1143974 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=gal,gallons,litres` | Aerial firefighting |
| 58346527 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Science Publishing Group |
| 56527 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,mw,g` | Galactose |
| 330691 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=m` | Saint-Denis, Réunion |
| 467036 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or temporal data to form a Date answer type question.` | Al Anbar Governorate |
| 49860 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=22` | Fauna of Australia |
| 570255 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=4` | Open list |
| 322335 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km,miles` | List of rivers of Australia |
| 56170 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=106` | Otsego County, New York |
| 40979 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,mw` | Crystal oscillator |
| 2913030 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information; therefore, no valid Date answer type question can be generated.` | Book size |
| 1112273 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:citation needed` | Heat of combustion |
| 1039080 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table contains phonetic consonant data without any date or temporal information, so it cannot support a Date answer type question.` | Kokborok |
| 12188699 | `route_generation` | `wikipedia_infobox_no_tables` | Passaddhi |
| 54421 | `route_generation` | `wikipedia_infobox_no_tables` | Sex-selective abortion |
| 35572416 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:unknown` | Lists of New Testament minuscules |
| 3368967 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=169` | Rohtak |
| 184346 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=21` | 1987 Cricket World Cup |
| 149270 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=18` | Atlantic Wall |
| 63542764 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=2` | 2020 Tablighi Jamaat COVID-19 hotspot in Delhi |
| 265324 | `route_generation` | `wikipedia_infobox_table_score_below_minimum:table_score_below_minimum:min_table_score=0.0000;best_score=-0.1000` | Cost of goods sold |
| 597142 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=19` | Wetaskiwin |
| 306175 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year was John Addenbrooke, the founder of Addenbrooke's Hospital, born? |
| 53565652 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw,m` | 2017 Westminster attack |
| 1332800 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | What month, day, and year did the original release of the TV series Hunter begin? |
| 1566172 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=pounds` | Representation of the People Act 1918 |
| 326413 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:citation needed` | List of exceptional asteroids |
| 2055880 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year was Clark International Airport known as Diosdado Macapagal International Airport? |
| 6025636 | `route_generation` | `wikipedia_infobox_table_score_below_minimum:table_score_below_minimum:min_table_score=0.0000;best_score=-0.1000` | Plasma protein binding |
| 96235 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information or usable data to generate a factual date question.` | Jackson County, Illinois |
| 205899 | `route_generation` | `wikipedia_infobox_no_tables` | Radula |
| 2579172 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=4` | Cumann na mBan |
| 3698121 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Andreas Seppi |
| 772315 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,m` | Jack Kramer |
| 1364371 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Sinéad Cusack |
| 23812915 | `route_generation` | `wikipedia_infobox_no_tables` | Service number (United States Air Force) |
| 236906 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | On what month, day, and year did Paolo Veronese die in Venice, Venetian Republic? |
| 2288 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=48` | Self-propelled anti-aircraft weapon |
| 107671 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Rancho Palos Verdes, California |
| 9970733 | `route_generation` | `wikipedia_infobox_llm_discarded:No date or year information available in the table to form a Date answer type question.` | Fórmula Truck |
| 1035700 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year did James Avery first appear in the television film Antony and Cleopatra? |
| 11685701 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=52` | Religion in Finland |
| 4039690 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Maidstone United win the Football Conference? |
| 111069 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Wilmette, Illinois |
| 576326 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Pancho Gonzales win the U.S. Pro tournament for the first time? |
| 871448 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year did Paulina Porizkova appear in the film 'Arizona Dream'? |
| 795518 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:unknown` | Vietnam Campaign Medal |
| 10184754 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date information; no date-type factual question can be generated from it.` | Northeastern Huskies |
| 322178 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=127` | Thurgau |
| 361870 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_time_invariance_forbidden_phrase:current` | In what year did the institution currently known as Truman State University adopt its present name? |
| 633554 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=22` | Football in Brazil |
| 4139007 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=36` | List of airports in the Lower Mainland |
| 326949 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | In what year was the Tamil film featuring Silambam titled 'Periya Idathu Penn' released? |
| 1125337 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ha,mw,ton` | List of common Chinese surnames |
| 1066029 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what age range are students typically in the tenth year of formal or compulsory education? |
| 411056 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year did John Ranby serve his first magisterial term as Past Master of the Company of Surgeons? |
| 448735 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year did the film Elf win the ASCAP award for Top Box Office Films? |
| 1130632 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Lost season 1 |
| 34524946 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=23` | 52nd National Film Awards |
| 70076 | `route_generation` | `wikipedia_infobox_no_tables` | Hel (location) |
| 48988 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Idaho Springs, Colorado |
| 2441 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=104;no_incomplete_tables:unknown` | House of Ascania |
| 26333 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Robotech |
| 254062 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=2` | Mast cell |
| 583461 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=1` | Stratum (linguistics) |
| 67500634 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=114` | COVID-19 vaccination in Nigeria |
| 2793706 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table 'Out on loan' contains only header row and no data rows, thus it does not support generating a factual question with a Date answer type.` | Club Guaraní |
| 4565015 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table contains only consonant phonemes and no date or temporal information, so no valid Date-type question can be generated.` | Wallisian language |
| 28925 | `route_generation` | `wikipedia_infobox_no_tables` | Science fiction fandom |
| 359531 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | President of the Soviet Union |
| 4168703 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a valid Date answer type question.` | Kathy Jordan |
| 591767 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Nicomachean Ethics |
| 33457900 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year did the 116th season of the Australian Football League (AFL) take place? |
| 50779174 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | MacGyver (2016 TV series) |
| 5981379 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | On what month, day, and year was the UEFA Champions League final played where Real Madrid scored 3 goals against Valencia? |
| 47063538 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km2,m2` | Districts of Ivory Coast |
| 210617 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=272` | List of London Underground stations |
| 68039895 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_social_science_research:population` | COVID-19 vaccination in Fiji |
| 9109 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=7` | Diophantine equation |
| 1364160 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km,mi` | Ağrı Province |
| 22287644 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km,mw,yard` | List of census-designated places in Washington |
| 104879 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Redstone Arsenal |
| 199884 | `route_generation` | `wikipedia_infobox_no_tables` | Osteopathic medicine in the United States |
| 98615 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ha,mw` | Danube Delta |
| 83205 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | Ardennes (department) |
| 155025 | `route_generation` | `wikipedia_infobox_no_tables` | Byzantine text-type |
| 10009538 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information, so no valid Date answer type question can be generated.` | List of Malaysian electoral districts |
| 293971 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=1` | Friuli |
| 208458 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a valid Date answer type question.` | Filoviridae |
| 8971 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information; it only lists instruction mnemonics and their descriptions, so no Date answer type question can be generated.` | DEC Alpha |
| 742537 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information to support a Date answer type question.` | List of airports in Canada (A–B) |
| 6495369 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=53` | Phillip Island Grand Prix Circuit |
| 172052 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=1` | Hastings, New Zealand |
| 12733279 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month and day was the 2003 Major League Baseball draft held? |
| 23592780 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km` | 10 Gigabit Ethernet |
| 5681617 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=27` | List of Brazilian federative units by Human Development Index |
| 1182568 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=13` | Stalag Luft III |
| 43285 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Common Object Request Broker Architecture |
| 43536 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information, so no valid Date answer type question can be generated.` | Beeswax |
| 178838 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:citation needed` | Ajax, Ontario |
| 769781 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft` | Bill Self |
| 6752609 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:approximate,citation needed` | Underwater vision |
| 127328 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=degrees` | Montauk, New York |
| 12414930 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=feet,foot,ft,litres,metres,millimetres,mw` | Oxy–fuel welding and cutting |
| 11598240 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month and day was the 2004 Major League Baseball draft held? |
| 16048129 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=7` | Operation Priboi |
| 2928059 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=2` | WMMS |
| 424587 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Hingham, Massachusetts |
| 33310519 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km` | List of population centres in Alberta |
| 21238 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=acres,hectares,km` | Neva |
| 83212 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | Aude |
| 471987 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | Bet365 Stadium |
| 93988 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=86` | London Borough of Hounslow |
| 2122924 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table contains personal pronouns and does not include any date or temporal information to form a Date-type question.` | Bunun language |
| 64226248 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | 365 Days (2020 film) |
| 36054427 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:active` | List of lieutenant generals in the United States Air Force before 1960 |
| 10592503 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=kw` | Charging station |
| 43771597 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_1:answer_in_title` | In what year did Russia make its sixth consecutive appearance at the Summer Olympics as an independent nation? |
| 419223 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=thousand,million` | Nebula Award for Best Novel |
| 1191870 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=feet,kg,km,miles,mw,pounds,m` | AGM-28 Hound Dog |
| 5401325 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | In what year was the first Costa Book Award given? |
| 42099152 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Rail transport in China |
| 166831 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Gerry Anderson work as a dubbing editor and assembly cutter for the film Appointment in London? |
| 434330 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year was Peter Forsberg inducted into the IIHF Hall of Fame? |
| 268021 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=24` | Mariehamn |
| 28706 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=17` | SECAM |
| 240011 | `route_generation` | `wikipedia_infobox_no_tables` | Coherence (physics) |
| 913041 | `route_generation` | `wikipedia_infobox_llm_discarded:No date-type answer available in the table to form a valid question.` | Kapitänleutnant |
| 18880361 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Boston College win the Hockey East Tournament championship with a 5–3 score against Providence? |
| 3660773 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=miles` | Royal Society of New Zealand |
| 382592 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Inter-American Development Bank |
| 159281 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Charisma Carpenter first appear in the television series Buffy the Vampire Slayer? |
| 510620 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km` | Provinces of Cambodia |
| 30087669 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Shades of white |
| 752720 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information; therefore, no valid Date-type question can be generated.` | Gemination |
| 69990317 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=124` | Timeline of the COVID-19 pandemic in Belarus (2022) |
| 436512 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:active` | Stake (Latter Day Saints) |
| 108668 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,km,mi,mw,m` | Fort Lupton, Colorado |
| 67546313 | `route_generation` | `wikipedia_infobox_table_score_below_minimum:table_score_below_minimum:min_table_score=0.0000;best_score=-2.0000` | Timeline of the COVID-19 pandemic in May 2021 |
| 524874 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or temporal data to form a Date-type question.` | Voiced pharyngeal fricative |
| 108523 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Walsenburg, Colorado |
| 209874 | `route_generation` | `wikipedia_infobox_no_tables` | Density functional theory |
| 19604151 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=g` | Atomic mass |
| 898992 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Inguinal hernia |
| 6754209 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the NHK Trophy figure skating competition inaugurated? |
| 1601502 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | In what year does the term of the Toronto District School Board trustees listed in the 2022-2026 Board of Trustees begin? |
| 10911216 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_2:answer_in_title` | In what year did V. Nagayya act in the film titled 'Gruhalakshmi'? |
| 460448 | `route_generation` | `wikipedia_infobox_no_tables` | List of diving hazards and precautions |
| 416998 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Richard Roeper first appear as a guest on Late Night with Conan O'Brien? |
| 4374512 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:present` | Ethel Barrymore Theatre |
| 1039161 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | Congress of South African Trade Unions |
| 1738605 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=13;no_incomplete_tables:unknown` | Culture of Asia |
| 108607 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,km,mi,mw,m` | Rocky Ford, Colorado |
| 14752637 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date information for the awards, so no valid Date answer can be extracted.` | Edward D. Thalmann |
| 416195 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was Beethoven's song "Adelaide" composed? |
| 38528078 | `route_generation` | `wikipedia_infobox_llm_discarded:No date or temporal values present in the table to form a Date answer type question.` | Amarasi language |
| 52951710 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Alternative facts |
| 801247 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=27` | 1987 World Championships in Athletics |
| 68779 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Flemish Brabant |
| 1954987 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=10` | Wilcoxon signed-rank test |
| 63890492 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information or any data suitable for generating a Date answer type question.` | List of PlayStation 5 games |
| 407888 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year did Mike Rogers begin serving as the U.S. representative for Alabama's 3rd congressional district? |
| 381506 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | What year did the 2004 United States Senate elections take place? |
| 698151 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | On what month, day, and year was the first In Your House professional wrestling event held? |
| 37336686 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information, so it cannot support a Date answer type question.` | Veraʼa language |
| 116267 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,km,mi,mw,m` | Biddeford, Maine |
| 1755878 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=kg,km,mph,g` | Porsche Panamera |
| 57737470 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_2:answer_in_title` | In what year did Brian Schnuckel win the Primetime Creative Arts Emmy Award for Outstanding Multi-Camera Picture Editing for a Comedy Series for his work on "Jeopardé, Sobrieté and Infidelité"? |
| 1581839 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what month and year was the single "Love Will Tear Us Apart" by Joy Division released? |
| 8315 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=11` | Diamagnetism |
| 219730 | `route_generation` | `wikipedia_infobox_no_tables` | Acrostic |
| 638354 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Daqing |
| 27346 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Slovenian Armed Forces |
| 2039988 | `route_generation` | `wikipedia_infobox_no_tables` | Orders, decorations, and medals of Canada |
| 5297519 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to support a Date answer type question.` | Utah Utes |
| 689521 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year did the television series China Beach win the Golden Globe Award for Best Television Series – Drama? |
| 9005839 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a valid Date answer type question.` | Philippine Basketball Association draft |
| 19182802 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year was the FIBA Under-17 Basketball World Cup founded? |
| 123412 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Havre, Montana |
| 1581712 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=1` | President of Estonia |
| 19763287 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=4` | VP8 |
| 3013008 | `route_generation` | `wikipedia_infobox_llm_discarded:No date-type answers available in the provided table.` | Kambera language |
| 3079144 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_2:answer_in_title` | In what year did Jonathan Stark win the French Open men's doubles title? |
| 1798106 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=degrees` | Order of the Netherlands Lion |
| 33396262 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=242` | List of the busiest airports in China |
| 260097 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date answer type question.` | Southampton, New York |
| 1593643 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:citation needed` | Hyperlipidemia |
| 34839260 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table contains phonological consonant data without any date or temporal information, so it cannot support a Date answer type question.` | Nunukan Tidung |
| 314843 | `route_generation` | `wikipedia_infobox_no_tables` | Campaign history of the Roman military |
| 450661 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km` | List of villages in Japan |
| 1577389 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year was the soundtrack for The Remains of the Day film released? |
| 11742 | `route_generation` | `wikipedia_infobox_no_tables` | Finite set |
| 334701 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a valid Date answer type question.` | List of state routes in New York |
| 886693 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | In what year was Vladislav Tretiak inducted into the International Ice Hockey Federation Hall of Fame? |
| 252776 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=1` | List of governors of Virginia |
| 399463 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_2:answer_in_title` | During which period did the reign of King Wu Ding occur according to the dating of oracle bones? |
| 717842 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=1` | Soap Opera Digest |
| 36985 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Warren Mitchell |
| 641672 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Mamye BaCote graduate from Virginia Union University? |
| 4846157 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | South Central China |
| 34031613 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | On what exact month, day, and year was the U.S. Fleet Cyber Command officially activated? |
| 1434658 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | In what year did Stevie Wonder's song "Superstition" reach its peak chart positions listed in the weekly chart performance table? |
| 1158955 | `route_generation` | `wikipedia_infobox_table_score_below_minimum:table_score_below_minimum:min_table_score=0.0000;best_score=-0.2500` | Fingerstyle guitar |
| 445291 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=1` | Clive James |
| 40486863 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did the gymnastics events at the 2020 Summer Olympics begin? |
| 153681 | `route_generation` | `wikipedia_infobox_no_tables` | Celestial equator |
| 276526 | `route_generation` | `wikipedia_infobox_no_tables` | Fiber bundle |
| 313971 | `route_generation` | `wikipedia_infobox_no_tables` | Sunset Strip |
| 255812 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Sorsogon |
| 775344 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ha` | Scout Motto |
| 1784313 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=7` | Tests of general relativity |
| 3734136 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table 'Out on loan' contains only headers and no data rows, so it does not support generating a factual question with a Date answer type.` | Deportivo Táchira F.C. |
| 1694492 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | On what month, day, and year was Garrett Withers formally installed as a U.S. Senator to finish the term after Alben W. Barkley resigned? |
| 266325 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=10` | Sovereign (British coin) |
| 264434 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=14` | Albanian lek |
| 4495 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:citation needed` | British thermal unit |
| 9616 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year was the concept of evolutionarily stable strategy proposed by John Maynard Smith and George R. Price? |
| 58306941 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information to support a Date answer type question.` | Technology readiness level |
| 31759897 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:unknown,approximately` | List of massacres in Mexico |
| 988765 | `route_generation` | `wikipedia_infobox_no_tables` | Sator Square |
| 1987049 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,kg,lb,m` | Damon Allen |
| 1519860 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | On what month, day, and year did Michael Jackson perform at the Seoul Olympic Stadium during the HIStory World Tour? |
| 646132 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=4` | Frankie Frisch |
| 26636274 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km,mi,miles` | List of long-distance footpaths in the United Kingdom |
| 36169584 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What month, day, and year did the 2014–15 figure skating season begin? |
| 54164 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=78` | Cortland County, New York |
| 2417390 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was Thomas M. Patterson formally installed as the successor for the Colorado At-large district in the 45th United States Congress? |
| 27805952 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the 75th season of the American Hockey League, which featured the Binghamton Senators winning the Calder Cup? |
| 117439 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Petoskey, Michigan |
| 441611 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=62` | Broadcast television systems |
| 25541697 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the complete first season of Louie released on DVD and Blu-ray Disc in Region 1? |
| 498814 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year did the debut album by American recording artist Norah Jones reach number 1 on the US Billboard 200 chart? |
| 5366864 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw,g` | Gestrinone |
| 317144 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date, year, or month information to form a valid Date answer type question.` | List of airports by IATA airport code: S |
| 5873951 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=20` | Mongolian names |
| 1004027 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Carlos Bocanegra play for the Chicago Fire in Major League Soccer and make 26 league appearances scoring 2 goals? |
| 4644242 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=miles` | List of United States representatives from Maryland |
| 20811169 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=14` | Águilas Doradas |
| 5826767 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=13` | Simferopol International Airport |
| 1075838 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year was the film The Life Aquatic with Steve Zissou released in the United States? |
| 690870 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Progressive Federal Party |
| 395945 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=19` | Pärnu County |
| 12885352 | `route_generation` | `wikipedia_infobox_llm_discarded:No date or temporal data available in the table to generate a Date answer type question.` | List of quadrangles on Mars |
| 1540834 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Moscow, Russian SFSR, unsuccessfully bid to host the Summer Olympics? |
| 212855 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mb` | Memory card |
| 2107046 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Gilles Müller |
| 97438 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date information about the officials' election or term start dates.` | Pulaski County, Arkansas |
| 3450570 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year did the film A Star Is Born receive nominations and wins at the Academy Awards, Golden Globe Awards, and other major film award ceremonies? |
| 51960492 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=20` | C band (IEEE) |
| 53680300 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:approximately` | Local Now |
| 378938 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | Magnesium in biology |
| 58227 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:present` | Arcadia (regional unit) |
| 545795 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what month and year was the soundtrack album for the film The Big Chill released? |
| 17292183 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the film New York, I Love You released? |
| 122064 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,km,mi,mw,m` | Stillwater, Minnesota |
| 16896790 | `rewrite_surface` | `rewrite_guard_rejected:forbidden_temporal_phrase` | As of what month and year was the status of Kosovo's EU accession chapters reported in the European Commission report? |
| 1460518 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Riba |
| 1599554 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,mw,m` | National Stadium of Peru |
| 392031 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Cheongju establish its sister city relationship with Wuhan in Hubei, China? |
| 651709 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=1` | Le Nouvel Obs |
| 251243 | `route_generation` | `wikipedia_infobox_no_tables` | Gamla Uppsala |
| 415874 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information or any data suitable for generating a Date answer type question.` | List of astronomical observatories |
| 881523 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=18` | Brixen |
| 83399 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Royal Armoured Corps established as an active unit? |
| 151474 | `route_generation` | `wikipedia_infobox_no_tables` | Aliasing |
| 1778618 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | Indiana Supreme Court |
| 33231502 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=12` | 20th National Film Awards |
| 17721855 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what month and year was Dean Holdsworth first awarded Manager of the Month during the 2009–10 Football Conference season? |
| 41149 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=1` | Fiber Distributed Data Interface |
| 1108342 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=16` | 1998 African Cup of Nations |
| 10173807 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a valid Date answer type question.` | Teymuraz Gabashvili |
| 5762383 | `route_generation` | `wikipedia_infobox_no_tables` | Timeline of the Troubles |
| 796996 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Berry College |
| 1838434 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Sturt Football Club Hall of Fame launched? |
| 5099468 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the Air Force Falcons football team play in the Bluebonnet Bowl against Texas? |
| 21319587 | `route_generation` | `wikipedia_infobox_llm_discarded:No date-type answers available in the table to form a valid question.` | Hrusish languages |
| 308675 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=17` | British Columbia Social Credit Party |
| 190814 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km,mi,mw` | Jämtland |
| 97665 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:incumbent` | St. Tammany Parish, Louisiana |
| 42000251 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was Will Forte first nominated for the Primetime Emmy Award for Outstanding Lead Actor in a Comedy Series for The Last Man on Earth? |
| 51557631 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=51` | 2019 Ukrainian presidential election |
| 116866 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=4` | Westford, Massachusetts |
| 11958238 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year was the scheme of nobility insignia proposed for use with the 1905/1911 military uniforms in the Qing dynasty? |
| 527837 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a valid Date answer type question.` | State University of New York at Cortland |
| 10174473 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Wireless Application Protocol Forum Limited formed? |
| 953669 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information or any factual data that can be answered with a date; it only contains a note about a symbol without any date values.` | Wally Lewis |
| 519903 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=25` | Spaniel |
| 107661 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Montebello, California |
| 10200458 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Alla Kudryavtseva reach the semifinals in the Tour Championships doubles event? |
| 25686 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Rubáiyát of Omar Khayyám, translated by Edward FitzGerald, first published? |
| 6791864 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:table` | In what year did Vitaly Petrov achieve his highest final standing in the GP2 Series according to the complete results table? |
| 14873003 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year were the clubs Consadole Sapporo, Kyoto Purple Sanga, and Tokyo Verdy promoted from the J2 League to participate in the 2008 J.League Division 1 season? |
| 4683430 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,yard,g,m` | .300 Winchester Magnum |
| 2849652 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the school with the most Ohio High School Athletic Association team titles win its first title? |
| 10793855 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What year did the HRT Formula 1 Team make its first entry in the Formula One World Championship? |
| 4510663 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mi` | Special Frontier Force |
| 16821356 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,ft,km,kw,mi,mph,tons,yard,m` | German submarine U-101 (1940) |
| 246124 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=1` | Dave Eggers |
| 427980 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=1` | ISO/IEC 8859-4 |
| 824692 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,mw,g` | Perfluorooctanoic acid |
| 40820246 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:active` | 2014 Ukrainian parliamentary election |
| 4401278 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Lyric Theatre (New York City, 1998) |
| 845756 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km,mi,mw` | Central Bosnia Canton |
| 311001 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=51` | Green's function |
| 514218 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=5` | Piracicaba |
| 18694060 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=228` | List of solar eclipses in the 20th century |
| 132561 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Uniontown, Pennsylvania |
| 1093875 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information; no date-type factual question can be generated.` | Orlen |
| 6950063 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Mark Pocan begin serving as a member of the U.S. House of Representatives from Wisconsin's 2nd congressional district? |
| 1245250 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:unknown` | West Virginia State University |
| 4091278 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what exact month, day, and year did Hamengkubuwono X become the incumbent Sultan of Yogyakarta? |
| 2382246 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Medical Scientist Training Program at Northwestern University founded? |
| 9912930 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information, so it cannot support a question with a Date answer type.` | Jewish Babylonian Aramaic |
| 98957 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Annie Sprinkle appear in the film titled 'The Ganja Express'? |
| 6336280 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=22` | HIV/AIDS in South Africa |
| 187926 | `route_generation` | `wikipedia_infobox_no_tables` | Centroid |
| 9737149 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=2` | Football at the 2004 Summer Olympics – Men's tournament |
| 28570035 | `route_generation` | `wikipedia_infobox_no_tables` | Japanese pagoda |
| 81167 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=27` | Provinces of France |
| 730257 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year was the number of native speakers of Judeo-Berber recorded as 200? |
| 573875 | `route_generation` | `wikipedia_infobox_no_tables` | Measurement in quantum mechanics |
| 3345447 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month and day did the 1986 NFL draft begin? |
| 75903 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=1` | ISO/IEC 8859-3 |
| 137733 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information or usable data to generate a Date-type question.` | Woodbridge, Virginia |
| 23658 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Philip K. Dick Award first presented? |
| 8416397 | `route_generation` | `wikipedia_infobox_no_tables` | Long hair |
| 8244461 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km,mi,mw` | Jongno District |
| 664497 | `route_generation` | `wikipedia_infobox_no_tables` | Parallel (geometry) |
| 284629 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Welland Canal |
| 8410979 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a valid Date answer type question.` | 1992 AFL season |
| 3161572 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | Economy of Wales |
| 108823 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=12` | Lyme, Connecticut |
| 294735 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date, year, or month information to form a Date-type question.` | Oberstleutnant |
| 11958301 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the London Grand Prix Gold badminton tournament first appear in the BWF Grand Prix Gold and Grand Prix series? |
| 64776868 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information suitable for forming a Date-type question.` | 2020 US Open – Men's singles |
| 3013157 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information, so no valid Date-type question can be generated.` | List of civil parishes in Lincolnshire |
| 330122 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=acres,hectares` | List of islands of Ireland |
| 794151 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:image_cell_rate=0.3500` | 1965 Canadian federal election |
| 21758543 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | On what month, day, and year did the Spain national under-20 football team play their first international match? |
| 4421189 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the team Toros Neftekamsk achieve their highest final regular season rank in the All-Russian Hockey League? |
| 282905 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=1` | Provençal dialect |
| 2445647 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=thousand` | Lanxess Arena |
| 150961 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Ponca City, Oklahoma |
| 40157682 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km,mi,mw` | Socialist Autonomous Province of Vojvodina |
| 2405252 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=18` | Toulouse Olympique |
| 428023 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=1` | ISO/IEC 8859-16 |
| 2643686 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=10` | Aga Khan University |
| 4958471 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information or any factual data suitable for generating a Date answer type question.` | Brandon Marshall |
| 466804 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information; thus, no valid Date answer question can be generated.` | METAR |
| 5235555 | `route_generation` | `wikipedia_infobox_llm_discarded:No date information is present in the provided table to support a Date answer type question.` | Pittsburgh Bureau of Fire |
| 1578061 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=1` | The Michigan Daily |
| 1674149 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a valid Date answer type question.` | Chifeng |
| 1491100 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:image_cell_rate=0.2759` | Flavin adenine dinucleotide |
| 8093228 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information; it only lists categories of tournament results without dates.` | Marcin Matkowski |
| 923348 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | E. G. Marshall |
| 9513184 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the 21st annual Royal Rumble professional wrestling pay-per-view event produced by World Wrestling Entertainment held? |
| 3044443 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:in_the_table` | In what year were the Toto numerals documented by van Driem as shown in the table? |
| 17257420 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=24` | 2000–01 Football League |
| 24998899 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Joël Matip score his only international goal for Cameroon? |
| 1640791 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=25` | List of William Shakespeare screen adaptations |
| 650007 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Paget's disease of bone |
| 5196351 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_time_invariance_forbidden_phrase:recent` | In what year did Schumer receive 92% of the vote in a Senate race according to the recent election results from statewide races? |
| 13477403 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information to form a Date-type question.` | List of National Historic Landmarks in Vermont |
| 303051 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date, year, or month information to form a valid Date answer type question.` | Gallo-Romance languages |
| 37119588 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,ft,km,kw,mi,mph,tons,tonnes,yard,m` | German submarine U-475 |
| 214067 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km` | Virgo Cluster |
| 12308004 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:image_cell_rate=0.2692` | 508th Aerospace Sustainment Wing |
| 530365 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Joan Bennett appear on the radio program Philip Morris Playhouse? |
| 531432 | `route_generation` | `wikipedia_infobox_no_tables` | Autostereogram |
| 63417 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Fountains Abbey |
| 196819 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the album Darkness on the Edge of Town by Bruce Springsteen released? |
| 3833573 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=8` | List of mayors of Long Beach, California |
| 83943 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Indonesia Raya |
| 4576492 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year did the National Association of Basketball Coaches stop having Independents in District 13? |
| 7117467 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | 2006 United States broadcast television realignment |
| 9427377 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Maine Democratic Party |
| 26473291 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | List of hot sauces |
| 16099880 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table only contains color codes and their corresponding race result categories, none of which are dates. Therefore, no valid Date-type question can be generated from this table.` | 2010 IndyCar Series |
| 9571698 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=1` | Carnivoramorpha |
| 50555549 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the final match of the 115th staging of the Copa del Rey held? |
| 2153241 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information, so no valid Date answer type question can be generated.` | Unicode subscripts and superscripts |
| 15029 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information, so it cannot support a question with a Date answer type.` | Industry Standard Architecture |
| 880626 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=billion` | Tokyo Electric Power Company |
| 475016 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:list` | In what year was Yueju Opera inscribed on the UNESCO Intangible Cultural Heritage list? |
| 1302610 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the Omni Television system launched? |
| 5562328 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what season did Garry Monk play 15 league matches on loan for Sheffield Wednesday? |
| 3761368 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what season did Stoke win the Birmingham & District League championship? |
| 1083426 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | From what year did Pinot gris become the only allowed designation, replacing Tokay d'Alsace and Tokay Pinot gris, in the Alsace AOC varietal labeling? |
| 3212306 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the full date of birth of Colin Kazim-Richards? |
| 263886 | `route_generation` | `wikipedia_infobox_no_tables` | Differential operator |
| 3360323 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=39` | Washington State Democratic Party |
| 545100 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km` | Association of Zoos and Aquariums |
| 5771288 | `route_generation` | `wikipedia_infobox_no_tables` | Alians |
| 838084 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What month and year is the next planned franchise change for the InterCity East Coast franchise? |
| 55681284 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what exact date was the FT8 digital mode of radio communication released by its creators Joe Taylor and Steve Franke? |
| 3613999 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the United National Independence Party (UNIP) first win 125 seats in the National Assembly elections of Zambia? |
| 12026076 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to support a Date answer type question.` | Exoribonuclease |
| 6172 | `route_generation` | `wikipedia_infobox_no_tables` | Cantor set |
| 1529985 | `route_generation` | `wikipedia_infobox_no_tables` | Badges of the United States Coast Guard |
| 28814296 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=10` | King Abdullah Sports City Stadium |
| 15418318 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | In what year did the song "I Could Fall in Love" achieve its peak chart positions listed in the weekly chart performance table? |
| 57476308 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Liverpool F.C. complete the season with 38 matches played, 30 wins, 7 draws, and 1 loss? |
| 8624941 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did the KAI KF-21 Boramae have its first flight? |
| 1304443 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the United States presidential election take place in Pennsylvania where Bush and Kerry competed by congressional district? |
| 7628511 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=11` | Weinan |
| 7719033 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=20` | Languages of Afghanistan |
| 2849796 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year were the Black Reel Awards first presented in Washington, DC? |
| 32795358 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the UFC match between Diaz and Miller broadcast on the Fox network? |
| 1910396 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Luis Horna |
| 69129560 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the E5 series Shinkansen train set U29 delivered? |
| 947310 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=26` | United States Department of Energy National Laboratories |
| 24402113 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information to form a valid Date-type question.` | Metropolitan Fresno |
| 11404831 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=19` | Scottish Canadians |
| 338435 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:unknown` | Filicide |
| 57208313 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | On what month, day, and year was the Brazilian mountain biking team named for the 2020 Summer Olympics? |
| 53608466 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what month and year was the Transkei Defence Force disbanded? |
| 495884 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:citation needed` | Sound pressure |
| 16921855 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did the second annual Night of Champions professional wrestling event take place? |
| 2194706 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Angela Mortimer |
| 2452013 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date answer type question.` | Grand chancellor (China) |
| 32269679 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:approximately` | 2011 NBA lockout |
| 1842129 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,kw,mw,m` | KMAX-TV |
| 505664 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year did the album by the American alternative rock band the Smashing Pumpkins reach number 1 on the Australian Albums (ARIA) chart? |
| 1226460 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Henri Pescarolo win the French Formula Three Championship? |
| 188896 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information, so a date answer cannot be derived from it.` | Neutron moderator |
| 4821319 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=156` | Sari, Iran |
| 539170 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=10` | Baltistan |
| 2156220 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=millimetres` | Tema |
| 294608 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=47` | Doboj |
| 71411822 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=19` | Judo Grand Slam |
| 1331885 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information or any factual data suitable for generating a Date-type question.` | Yingkou |
| 7571233 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=2` | Pennsylvania's 17th congressional district |
| 1500696 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year were the 47th Annual Grammy Awards held? |
| 1148574 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the official record chart in the United Kingdom begin using Record Retailer as the canonical source for singles charts? |
| 25820233 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the top professional association football division in Costa Rica founded? |
| 1882706 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Medal ribbon |
| 2253558 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ounces` | AngloGold Ashanti |
| 845033 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,kw,mw,m` | KHON-TV |
| 1797559 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a valid Date answer type question.` | Linfen |
| 642489 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km,kw,mph` | Porsche 911 (996) |
| 55093710 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:table` | In what year did Scott Ryan win the award for Best Lead Actor in a Television Drama for the first time according to the awards and nominations table? |
| 182890 | `route_generation` | `wikipedia_infobox_no_tables` | Kronecker delta |
| 2254778 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=12` | Brisbane Entertainment Centre |
| 1387121 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=9` | Elections in Portugal |
| 1928528 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information; therefore, no valid Date answer question can be generated.` | American Contract Bridge League |
| 3701174 | `route_generation` | `wikipedia_infobox_no_tables` | American Civil War corps badges |
| 4236804 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:image_cell_rate=0.2857` | Yule log (cake) |
| 669903 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Rainer Schüttler achieve his career-high ATP singles ranking of world No. 5? |
| 13544419 | `route_generation` | `wikipedia_infobox_no_tables` | MIMO |
| 2336136 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=2` | Tenth Dynasty of Egypt |
| 1861711 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=6` | Yulin, Shaanxi |
| 1701840 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the survey conducted that recorded 1,030,254 Kumaoni speakers in India? |
| 93260 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=70` | Pitt County, North Carolina |
| 665071 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what month and year was the French gunboat Vierge-de-Grâce recaptured and scuttled during the Siege of Acre? |
| 1140090 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year was the 25th season of the Fédération Internationale de l'Automobile's Formula One motor racing held? |
| 380087 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=8` | Litchfield, Connecticut |
| 46965920 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mi,mw` | List of Televisa telenovelas and series (2010s) |
| 5069114 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:citation needed` | Cinema of Ireland |
| 15745082 | `route_generation` | `wikipedia_infobox_table_score_below_minimum:table_score_below_minimum:min_table_score=0.0000;best_score=-0.5500` | Administrative divisions of Cambodia |
| 1283281 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=8` | ISO 20022 |
| 548738 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | Zenica-Doboj Canton |
| 1487550 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did John Edward Bromby begin his period as headmaster of Melbourne Grammar School? |
| 5802918 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information; no Date answer type question can be generated.` | Toto Cup |
| 247169 | `route_generation` | `wikipedia_infobox_no_tables` | Music of Argentina |
| 12692065 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the 64th Air Division inactivated at Stewart Air Force Base, New York? |
| 774572 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or temporal information to form a Date-type question.` | Evolutionary game theory |
| 1909983 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Pierre Gemayel begin his tenure as president of the governing body of association football in Lebanon? |
| 638972 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=2` | Football at the 2000 Summer Olympics – Men's tournament |
| 364774 | `route_generation` | `wikipedia_infobox_no_tables` | Conformal field theory |
| 8025346 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information to form a valid Date answer type question.` | PFC Lokomotiv Tashkent |
| 91204 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=56` | Jefferson County, Washington |
| 3951896 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=g` | List of nominations to the Supreme Court of the United States |
| 803607 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date, month, or year values to form a valid Date answer type question.` | Chorea |
| 538031 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km,mi,mw` | List of municipalities in Tennessee |
| 25739 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=11` | Rich Text Format |
| 7349465 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=62` | Kermanshah County |
| 14456578 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what years was the 453rd Bombardment Group active during its first period of service? |
| 13042838 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information to form a valid Date answer type question.` | Fernando Muslera |
| 33038936 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what month, day, and year were the Italian Athletics Championships held in Bari? |
| 1689476 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the complete first season of Tom & Jerry Kids released on DVD? |
| 2170226 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Chase Elliott win the NASCAR Rookie of the Year award? |
| 350708 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mb` | MultiMediaCard |
| 5175973 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=15` | Military ranks of South Korea |
| 141839 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,ft,km,metres,mi` | Magdalen Islands |
| 930108 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,km,mi,mw,m` | Ivanovo |
| 714854 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Department of Junín |
| 460528 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=4` | Heart Sutra |
| 315548 | `route_generation` | `wikipedia_infobox_no_tables` | Stabat Mater |
| 232872 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=miles,pascal` | Family Affairs |
| 40377 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | In what year did Ole Einar Bjørndalen compete in the 2006–07 World Cup season? |
| 2447894 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_social_science_research:census` | Census in the United Kingdom |
| 11584912 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the number of higher education institutions divesting from South Africa reach 128? |
| 39227262 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=36` | 2013–14 Süper Lig |
| 368004 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what exact date was the Royal Logistic Corps officially formed? |
| 25286976 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=30` | Solar eclipse of March 29, 2025 |
| 253068 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:incumbent` | Governor of Hawaii |
| 391267 | `route_generation` | `wikipedia_infobox_no_tables` | Positron emission |
| 383485 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | In what year was the 1957 orthography of the Zhuang name for Beihai recorded? |
| 16278495 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=27` | Outline of Brazil |
| 1904477 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | In what year did the reissued single "West End Girls" achieve its peak chart positions listed in the weekly charts? |
| 22133191 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=18` | 2009–10 Bundesliga |
| 1969542 | `route_generation` | `wikipedia_infobox_llm_discarded:No date-type answers available in the table to generate a Date answer_type question.` | Extraocular muscles |
| 7978444 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the original video animation titled 'Sakura Diaries' directed by Kunitoshi Okajima released? |
| 432487 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:present` | Washburn University |
| 35636402 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what season did Manchester win the North Division 2 rugby union league championship? |
| 1658720 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what season did Rigobert Song play for Salernitana in Serie A? |
| 735501 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the reign of the Later Tang ruler Li Cunxu, known by the temple name Zhuāngzōng, begin? |
| 12064241 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:citation needed` | Funny Girl (film) |
| 29828333 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the Lake Forest Foresters football team reach the second round of the NCAA Division III playoffs? |
| 53906279 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the WWE Great Balls of Fire event held? |
| 1997961 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was Caroline Matilda of Great Britain born? |
| 151175 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=meter` | Mansfield, Texas |
| 59076 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,ft,km,kw,mi,mph,tons,tonnes,yard,m` | German submarine U-553 |
| 469948 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=6` | Muslims (ethnic group) |
| 16454455 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=24` | 1965–66 Football League |
| 2383962 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,m` | Malky Mackay |
| 847398 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:citation needed` | Balsamic vinegar |
| 17104279 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=12` | Kiev Governorate |
| 1699287 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:present` | Cardium pottery |
| 140103 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Riverton, Wyoming |
| 862690 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=36` | Cirebon |
| 507522 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:approx.` | Aggie Bonfire |
| 19369391 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Sanitation worker |
| 119272 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,km,mi,mw,m` | Redford, Michigan |
| 898353 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date values or date-related data to form a valid Date answer type question.` | Philadelphia Big 5 |
| 461025 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:present` | Aetolia-Acarnania |
| 1718061 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a valid Date answer type question.` | Shangri-La, Yunnan |
| 1138307 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=3` | Prijepolje |
| 1660205 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=2` | Tabarka |
| 32257023 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=4` | 1944 Republican Party presidential primaries |
| 898653 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=miles,mw` | Derek Luke |
| 246768 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=1` | Biliran |
| 39913555 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=261` | 1976 United States presidential election in New York |
| 6230784 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a valid Date answer type question.` | Hong Kong Cantonese |
| 9489115 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table contains phonetic consonant data without any date or temporal information, so it cannot support a Date answer type question.` | Gong language |
| 87505 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=22` | Yukon–Koyukuk Census Area, Alaska |
| 48344963 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or temporal information to form a Date-type question.` | Puduvoyal |
| 6795916 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,m` | Gough's Cave |
| 1187279 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=127` | Islam in Bangladesh |
| 2513744 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=42` | Nissan Motor Manufacturing UK |
| 4906966 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a valid Date answer type question.` | British Standard Pipe |
| 16454482 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=71` | 1972–73 Football League |
| 65217524 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=8` | List of solar eclipses in the Middle Ages |
| 30079114 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=26` | 2014 Ukrainian presidential election |
| 482383 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | In what year did Paul D. Zimmerman win the BAFTA Award for Best Original Screenplay for The King of Comedy? |
| 23758509 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=m` | List of solar eclipses in the 22nd century |
| 632394 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=6` | Transit of Mercury |
| 171193 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=23` | Hedmark |
| 13963241 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=feet,kg,pounds,m` | QF 3-inch 20 cwt |
| 971658 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:approx.` | Helminthiasis |
| 1338980 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=57` | Gatineau Olympiques |
| 57587117 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year was iOS 12 released? |
| 8551616 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:nearby_intro:current` | Payment Card Industry Data Security Standard |
| 12935706 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table only contains a key for abbreviations without any date values or factual data to form a date answer question.` | Timea Bacsinszky |
| 14693333 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year did the debut single by the American rapper Flo Rida featuring T-Pain reach its peak position on the US Billboard Hot 100 chart? |
| 219172 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | What is the time zone offset during British Summer Time (DST) for the Home Counties in England? |
| 42280433 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information; it only contains a key for player status and positions, so no valid Date-type question can be generated.` | List of Albania international footballers |
| 93298 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=61` | Haywood County, North Carolina |
| 12336148 | `route_generation` | `wikipedia_infobox_generation_error:IncompleteRead:IncompleteRead(11 bytes read)` | https://en.wikipedia.org/w/index.php?pageid=12336148 |
| 690646 | `route_generation` | `wikipedia_infobox_generation_error:IncompleteRead:IncompleteRead(77 bytes read)` | https://en.wikipedia.org/w/index.php?pageid=690646 |
| 7050925 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=1` | Czech Americans |
| 91258 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=25` | Rappahannock County, Virginia |
| 1108299 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=12` | 1994 African Cup of Nations |
| 1092454 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:approximate` | Malazan Book of the Fallen |
| 9029387 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=77` | AFI's 100 Years...100 Movies (10th Anniversary Edition) |
| 414163 | `route_generation` | `wikipedia_infobox_generation_error:IncompleteRead:IncompleteRead(77 bytes read)` | https://en.wikipedia.org/w/index.php?pageid=414163 |
| 23692 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=39` | Prime number theorem |
| 50087781 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=757` | 1976 United States presidential election in Texas |
| 109769 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=11` | Altamonte Springs, Florida |
| 64986718 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=95` | Structure of the United States Space Force |
| 32108299 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | WSG Tirol |
| 516942 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | On what month, day, and year was the Qing dynasty abolished? |
| 7219253 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,ft,km,kw,mi,mph,tons,yard,m` | German submarine U-31 (1936) |
| 17257417 | `rewrite_surface` | `rewrite_guard_rejected:answer_leakage` | In what year was the 101st completed season of The Football League, known as the 1999–2000 Football League, held? |
| 467353 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=32` | Suwannee River |
| 3052138 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,kg,km,lb,meters,metre,metres,mile,yard,yards` | Submarine pen |
| 2732512 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=6` | Estadio La Rosaleda |
| 46694908 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | In what year did Grêmio Novorizontino win the Campeonato Paulista Série A3 title? |
| 747878 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a valid Date answer type question.` | Lishui |
| 26005083 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was Adrián Menéndez Maceiras born? |
| 25287038 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=30` | Solar eclipse of June 12, 2029 |
| 2297339 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a valid Date answer type question.` | Salina Regional Airport |
| 30002680 | `search_longtail` | `search_longtail_verifier_rejected:keyword_query_2:answer_in_title` | In what year was the Surrey Rugby Football Union involved in a County Championship final that ended with the title being shared after a drawn replay? |
| 543502 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year did Brigham Young University–Idaho transition from a junior college to a baccalaureate institution? |
| 415282 | `route_generation` | `wikipedia_infobox_no_tables` | List of kings of Athens |
| 42345 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was Hyman G. Rickover born? |
| 13523509 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=3` | Estonian Land Forces |
| 452068 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=16` | Discovery Program |
| 134805 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Mitchell, South Dakota |
| 43050178 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Bangalore railway division formed? |
| 3648904 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Barry Williams first appear in the television series The Brady Bunch? |
| 47073183 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did the WWE event 'The Beast in the East' take place at the Ryōgoku Kokugikan in Tokyo, Japan? |
| 3082583 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did the Indian rupee decimalisation change to 1 rupee equaling 100 naye paise? |
| 998762 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft` | Communes of the Bas-Rhin department |
| 30613979 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | Member states of the Arab League |
| 64109900 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=38` | List of Indonesian snacks |
| 56189 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information or any factual data suitable for generating a Date-type question.` | Interlaced video |
| 750002 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=10` | Cultural regions of Lithuania |
| 40242680 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=758` | 1988 United States presidential election in Texas |
| 57055767 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What month, day, and year was the song "I Like It" by Cardi B, Bad Bunny, and J Balvin released to radio stations through Atlantic Records? |
| 43791114 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,ft,km,kw,mi,mph,mw,tons,tonnes,yard,m` | German submarine U-764 |
| 64177252 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=1` | Emmett Till Antilynching Act |
| 207162 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the Frankford Yellow Jackets win the NFL Championship? |
| 15156688 | `search_longtail` | `search_longtail_verifier_rejected:full_question:hit_rate_exceeded` | In what year did the Chattanooga Moccasins join the SoCon conference? |
| 1942258 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=23` | Table wine |
| 4239846 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Donald Trump first win the presidential vote in Ohio's 4th congressional district according to the election results? |
| 58977186 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | On what month, day, and year was the National Board of Review Awards ceremony held where The Green Knight won Top Independent Films? |
| 1345744 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,kw,mw,m` | WPHL-TV |
| 1354709 | `route_generation` | `wikipedia_infobox_no_tables` | Two knights endgame |
| 2061661 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information; therefore, no valid Date answer question can be generated.` | Korvettenkapitän |
| 22201341 | `route_generation` | `wikipedia_infobox_llm_discarded:No date or temporal data available in the provided table to generate a Date answer type question.` | Telefol language |
| 76391 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year was the linguistic source referenced for the morphology of transitive verb endings in Bislama published? |
| 246612 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the IQD 25 banknote featuring Saddam Hussein with the Battle of al-Qādisiyyah in the background issued in the Swiss dinar series? |
| 61520198 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year was the Justicialist Party led by Alberto Fernández a member party of the Frente de Todos coalition? |
| 333697 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=7` | Uniform Resource Name |
| 5121902 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:citation needed` | Ferrari 312T |
| 110941 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Barrington, Illinois |
| 22198326 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what dates were the second round matches of the 2009–10 Copa del Rey played? |
| 59834648 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:citation needed` | Mattel Films |
| 476776 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the Criminal Code of Canada assented to? |
| 91733 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=53` | Hardin County, Tennessee |
| 771734 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=4` | Rugby union at the Summer Olympics |
| 496312 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information; therefore, no valid Date-type question can be generated.` | Nuclease |
| 40701845 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=3` | German submarine U-706 |
| 5184238 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Schumer receive 67% of the vote in a Senate election in New York's 20th congressional district? |
| 39950440 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=253` | 1964 United States presidential election in New York |
| 24298824 | `route_generation` | `wikipedia_infobox_no_tables` | Somali mythology |
| 683742 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the television series The District first air on CBS? |
| 25323835 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Czech Technical University in Prague ranked 12th in the QS Emerging Europe and Central Asia regional overall rankings? |
| 1706399 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:word_marker=million` | Budapest Metro |
| 91227 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=59` | Wythe County, Virginia |
| 316858 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information, only phonetic vowel data, which is not suitable for a Date answer type.` | Eastern Armenian |
| 5722 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=6` | Call of Cthulhu (role-playing game) |
| 71778950 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information to support a Date answer type question.` | Shakespeare's influence on Tolkien |
| 7600694 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Emphatic Diaglott New Testament translation published? |
| 67194640 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=23` | 2018 San Francisco Board of Education election |
| 29336870 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=16` | 2011 Tippeligaen |
| 17185703 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the 2009 Daytona 500 held? |
| 1530689 | `route_generation` | `wikipedia_infobox_no_tables` | Complementarity (physics) |
| 967668 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=1` | Ansan |
| 3396363 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=ft,kg,km,kw,lb,mi,mph,mw` | Honda CBR600RR |
| 5483165 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the Minnesota's 6th congressional district first record election results under the 2013–2023 boundaries for the office of President? |
| 1156819 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_social_science_research:demographic,population` | Population ecology |
| 911362 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=1` | Billy Pierce |
| 7348749 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=93` | Urmia County |
| 979683 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information for any brand, so no valid Date answer question can be generated.` | Digicel |
| 1187925 | `route_generation` | `wikipedia_infobox_no_tables` | Women's Auxiliary Air Force |
| 420528 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did James Stewart begin his tenure as Duke of Richmond? |
| 298534 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information to form a valid Date-type question.` | CompactFlash |
| 1848827 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=6` | Lancaster Royal Grammar School |
| 15602925 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=5` | Merville, Nord |
| 35555518 | `route_generation` | `wikipedia_infobox_llm_discarded:No date-type answers available in the provided table.` | Russian Braille |
| 88735 | `route_generation` | `wikipedia_infobox_no_tables` | Móði and Magni |
| 308022 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the venue White Eagle Hall in Jersey City established? |
| 29603083 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what date was the Thiruvananthapuram Railway Division formed? |
| 423933 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=7` | Cracking (chemistry) |
| 7268183 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,ft,km,kw,mi,mph,tons,tonnes,yard,m` | German submarine U-371 |
| 39596181 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did The Sopranos season 1 receive nominations and wins for various awards including the Primetime Emmy Awards, Golden Globe Awards, and Screen Actors Guild Awards? |
| 5866273 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=9` | German submarine U-75 (1940) |
| 7126758 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:section_heading:current` | Al-Shamal SC |
| 91871 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=63` | Lexington County, South Carolina |
| 608992 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:approx.` | Tarpaulin |
| 6983416 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:out_of_allowed_no_comma_range_count=1` | Signal Corps in the American Civil War |
| 14192171 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | SpongeBob SquarePants season 2 |
| 1342939 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | List of extreme points of India |
| 6007224 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year was the Pensacola Standard Metropolitan Statistical Area first defined? |
| 23847876 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the football club FC Vaslui founded? |
| 3095917 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what years did Mohammad Hafeez serve as the Pakistani national cricket captain for T20I? |
| 16454477 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what season did Arsenal become the champions of The Football League? |
| 20754105 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=9` | BMW Z4 (E89) |
| 2976501 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km` | Kizilsu Kyrgyz Autonomous Prefecture |
| 533423 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=28` | Solar water heating |
| 124728 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm` | Poplar Bluff, Missouri |
| 46345037 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,ft,km,kw,mi,mph,tons,tonnes,yard,m` | German submarine U-956 |
| 137888 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,ft,metre` | Longview, Washington |
| 844866 | `route_generation` | `wikipedia_infobox_llm_discarded:No date or year information available in the provided table to generate a Date answer type question.` | Manado Malay |
| 1411599 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | In what year did the song "Won't Get Fooled Again" reach its peak chart positions listed in the weekly charts table? |
| 117162 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=mw` | La Crescenta-Montrose, California |
| 1179011 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Ian Callaghan play for the Fort Lauderdale Strikers in the NASL? |
| 332236 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:image_cell_rate=0.2857` | IFAF World Championship |
| 1007705 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Lancashire League rugby competition instituted? |
| 588643 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=52` | Colorado Party (Uruguay) |
| 933786 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the AT&T Pebble Beach Pro-Am first include Spyglass Hill Golf Course as a tournament host? |
| 4847416 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the NCAA Division I-A football season feature 105 teams and have Oklahoma as the preseason AP No. 1? |
| 80493 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year did the film Henry V receive the Academy Honorary Award? |
| 30863884 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=22` | Performing arts in Detroit |
| 1840325 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_incomplete_tables:unknown` | Shippensburg University |
| 69730243 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did James Madison move from the CAA (FCS) conference to the Sun Belt (FBS) conference? |
| 69055344 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=4` | 2022 Havering London Borough Council election |
| 1412020 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year did W. A. Miller begin his presidency at Texas A&M University–Corpus Christi? |
| 1882322 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=7` | IARC group 1 |
| 10760098 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the European Junior Swimming Championships begin? |
| 11080001 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:image_cell_rate=0.4444` | 343d Wing |
| 32148625 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=88` | List of donkey breeds |
| 11728413 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the id Tech 4 game engine released? |
| 473278 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the ISO 31 international standard concerning physical quantities and units first published? |
| 1774491 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km,mi` | Neighborhoods in Washington, D.C. |
| 45367766 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what season did All Stars F.C. achieve 3rd place in the National First Division? |
| 762953 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Central College (Iowa) |
| 11056278 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table only contains color codes and their corresponding race result categories, none of which are dates. Therefore, no valid Date-type question can be generated from this table.` | 2000 CART FedEx Championship Series |
| 1017722 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Szolnok |
| 36229955 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=cm,ft,km,kw,mi,mph,mw,tons,tonnes,yard,m` | German submarine U-431 |
| 343355 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:unit_marker=km` | Municipalities of Armenia |
| 6779185 | `route_generation` | `wikipedia_infobox_live_table_scope:live_table_scope:caption:present` | Reisinger |
| 1756402 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what years was Pat McCrory the Republican nominee for Governor of North Carolina? |
| 4782774 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:decimal_number_count=5` | Durbanville |
| 5329771 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | In what year did the song "Déjà Vu" by Beyoncé achieve its peak chart positions listed in the weekly chart performance table? |
| 748114 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did Ted Lyons pitch a no-hitter? |
| 1939189 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Wilmington Hammerheads Football Club dissolved? |
| 344242 | `route_generation` | `wikipedia_infobox_table_filter_rejected:no_picture_heavy_tables:wikitable_image_cell_count=4` | Average absolute deviation |
| 15307973 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Jean-Marie Bidaux begin his term as mayor of Alaincourt? |
| 94561 | `route_generation` | `wikipedia_infobox_table_filter_rejected:not_number_dominant:comma_number_count=71` | Platte County, Missouri |
| 225205 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was Edward C. Cabell formally installed as the representative for Florida At-large after Florida was admitted to the Union? |
| 66196 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what biblical book and chapter is the passage that describes the Lord coming down from heaven with a loud command, the voice of the archangel, and the trumpet call of God? |
| 27449035 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did TheWrap win the Best Entertainment Website (Internet-only) award from the Los Angeles Press Club’s National Arts and Entertainment Journalism Awards? |
| 508406 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the film 'Dances With Wolves', featuring Mary McDonnell as Stands With A Fist, released? |
| 633282 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the production of the BMW 7 Series begin? |
| 5007829 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Alhambra Theatre in El Paso, Texas, designed by Henry C. Trost, completed? |
| 275601 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date answer type question.` | Classification of demons |
| 992991 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Vowel length |
| 219101 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | In what year did the song "Jumpin' Jack Flash" reach its peak chart positions listed in the weekly charts? |
| 914132 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Mardy Fish |
| 1028188 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to support a Date answer type question.` | Code page 437 |
| 107632 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year were the top employers in Gardena, California, reported according to the city's Annual Comprehensive Financial Report? |
| 1433736 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Balachandra Menon act in the film 'April 18'? |
| 2396042 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what week of the 1983 NFL season did the Dallas team first lose a game in the National Football Conference East division? |
| 57918689 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was the second leg of the fourth round originally scheduled in the 2022 FIFA World Cup qualification (AFC)? |
| 3292213 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information, so no valid Date-type question can be generated.` | Hazard analysis |
| 414186 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In the AJCC Prognostic Stage Groups for oral cancer, what stage group corresponds to the classification when T is T2, N is N0, and M is M0? |
| 773431 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did the 8th World Championships in Athletics begin? |
| 308606 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the United Nations Development Programme (UNDP) in Thailand begin tracking progress on human development at a sub-national level using the Human achievement index? |
| 53785948 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Jason Gilchrist become the top scorer in the third season under English football's new title of National League? |
| 848405 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what season did Duncan Ferguson play 38 league games and score 15 league goals for Dundee United in the Scottish Premier Division? |
| 1688653 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the 67th Legislature of the Montana House of Representatives convene? |
| 17158820 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date answer type question.` | Boatswain's mate (United States Navy) |
| 426743 | `route_generation` | `wikipedia_infobox_llm_discarded:The answer is a numeric count, not a date, so it does not match the required Date answer type.` | Graph coloring |
| 2525308 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_time_invariance_forbidden_phrase:recent` | In what year was the most recent season for which the Women's National Basketball League awarded the Most Valuable Player to Isobel Borlase? |
| 764257 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what month and year were the existing Air Force research laboratories merged into four superlabs? |
| 35734292 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Dowry Prohibition Act, which prohibits families from taking a dowry punishable with imprisonment, passed in India? |
| 1610581 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information to form a Date-type question.` | Voltage-gated calcium channel |
| 578812 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what season did the Louisville Thunder win their only National Professional Soccer League championship? |
| 357365 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did Lucien Louis Joseph Napoleon Bonaparte, 4th Prince of Canino and Musignano and later a Cardinal, die? |
| 40504132 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did the 1994 World Rowing Championships begin? |
| 179241 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Michael Warren begin his term as President and CEO of Canada Post? |
| 52024346 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the television series Atypical nominated for the Satellite Awards in the Best Musical or Comedy Series category? |
| 56316870 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Quinn Hughes win the James Norris Memorial Trophy? |
| 2454457 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what week of the 1975 NFL season did the Minnesota team first achieve a 10–0–0 record in the Central division? |
| 129801 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information related to the city council members or their appointments.` | Portsmouth, Ohio |
| 1438469 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did the IRT Lexington Avenue Line platforms at Grand Central–42nd Street station open? |
| 2326934 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Seventeenth Dynasty of Egypt established? |
| 2444452 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information to form a valid Date answer type question.` | Ion Țiriac |
| 488965 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was Frank McCloskey formally installed as the successor for Indiana's 8th district in the 99th United States Congress? |
| 3611140 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did LFLS Kaunas win the top division of professional football in Lithuania during the Interbellum period? |
| 1313008 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year were the United States Senate elections held that included candidates such as D 38 Fla. and R 39 N.J. running? |
| 447977 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What month, day, and year was the last ship of the Gato class commissioned? |
| 2465491 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Terry Jones start his tenure as Editor-in-Chief of the United Kingdom edition of i-D magazine? |
| 2453900 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what week of the 57th regular season of the National Football League did the Dallas team first achieve a 4–0–0 record in the East division? |
| 463116 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the Norm Smith Medal first awarded? |
| 6627016 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the Calcutta Football League first have its matches broadcast by Tara Newz? |
| 143451 | `route_generation` | `wikipedia_infobox_llm_discarded:The table does not contain any date or year information; no suitable Date answer type question can be generated.` | Province of Cádiz |
| 5776334 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table is a key/legend for Grand Slam performance timelines and does not contain any date values or factual data with date answers. Therefore, no valid Date-type question can be generated from this table.` | Kateryna Volodko |
| 464836 | `search_longtail` | `search_longtail_verifier_rejected:keyword_queries:hit_rate_exceeded` | In what year did Ant McPartlin first appear as the character PJ in the television series Byker Grove? |
| 35898391 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year was the number of native Satawalese speakers recorded as 500? |
| 1135 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did Abner Doubleday begin his command of the I Corps in the Army of the Potomac? |
| 2458670 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the NHL season held when Gump Worsley and Ed Giacomin were named to the All-Star teams? |
| 14907 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | What is the range of the usual principal value of the arccos inverse trigonometric function? |
| 8903118 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the movie Agnisakshi win the most Kerala State Film Awards? |
| 108729 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what month and year was Simsbury, Connecticut incorporated as a town? |
| 1243492 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what season did Alana Beard win the first John R. Wooden Award for women? |
| 5801331 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the highest amateur football league in the Netherlands, known as the Tweede Divisie, originally founded? |
| 1448951 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was John W. Moore installed as the successor for Kentucky's 3rd district after Charles W. Roark died? |
| 350267 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did the Penarth Extension Railway Act 1876 receive royal assent? |
| 66345 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Robin Givens appear in the film titled 'Boomerang'? |
| 2604805 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what week of the 1968 NFL season did the Minnesota team first have a losing record in the Central Division standings? |
| 191105 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did the original release of Schoolhouse Rock! begin? |
| 2159571 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year was Daniel Inouye formally installed as the successor for the new Hawaii at-large seat after Hawaii achieved statehood? |
| 2317530 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information; it only contains legend explanations without factual data suitable for a Date answer type question.` | Tommy McDonald (American football) |
| 5592225 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did the Pahela Baishakh attack on Ramna Batamul in Bangladesh occur? |
| 5643269 | `shared_validation` | `shared_validation_failed:answer_in_evidence,route_local_factual_validation` | In what year was the California Government Operations Agency created to help modernize the government? |
| 18117921 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date or year information, so it cannot support a Date answer type question.` | South Bird's Head languages |
| 713664 | `rewrite_surface` | `rewrite_guard_rejected:post_rewrite_self_containment_forbidden_phrase:listed` | In what year did India develop the formal hierarchical system of gun salutes during the British Raj as listed in the table? |
| 19908651 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table only contains color codes and their corresponding race result categories, none of which are dates. Therefore, no valid Date-type question can be generated from this table.` | 1994 PPG Indy Car World Series |
| 24205 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year was the first Prometheus Award given? |
| 1001441 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what season did Luis García play for Liverpool in the Premier League and make 29 league appearances? |
| 618149 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did John McTiernan win the Hochi Film Award for Best International Picture for the film Die Hard? |
| 188780 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the production of the Ford Taunus begin? |
| 529237 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did the College of Idaho win the NAIA Single Division Baseball National Championship? |
| 26113731 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | In what year did Eric Murray and Hamish Bond win the Lonsdale Cup together? |
| 1226514 | `second_stage_grading` | `second_stage_grading_accuracy_threshold_exceeded:accuracy=0.5;threshold=0.1` | On what month, day, and year did the Formula One fatal accident involving Peter Collins occur? |
| 62284195 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table does not contain any date information to form a Date-type question.` | Patrick Surtain II |
| 3690441 | `route_generation` | `wikipedia_infobox_llm_discarded:The provided table contains only a legend with no factual date information to generate a Date answer type question.` | Billy Kilmer |


