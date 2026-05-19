# Route 3 Raw-Dump Wikipedia Table Pilot - 2026-05-19 Rewrite Rerun

This walkthrough records the 30-URL Route 3 pilot rerun from Wikipedia table parsing and question generation through the two-stage filters. The run uses the revised subject-scope prompt (`subject_anchors` plus separate `safe_subject_aliases`) and the updated DuckDuckGo hit-rate thresholds: full question 0.3, keyword queries 0.3, and overall 0.3. Hit rates equal to 0.3 pass; only rates above 0.3 reject.

## Inputs and Discovery

- Raw page JSONL: `cache/wikipedia_1percent_dumps/raw_pages_all.jsonl`
- URL discovery output: `config/wikipedia_table_urls_rawdump_best20x2.tsv`
- Pipeline outputs: `outputs/wikipedia_infobox_rawdump_best20x2_rewrite_accepted.jsonl`, `outputs/wikipedia_infobox_rawdump_best20x2_rewrite_rejected.jsonl`, and `outputs/wikipedia_infobox_rawdump_best20x2_rewrite_summary.json`
- Discovery selected 30 URLs from 17 domains in the prior dump-backed seed step.
- Missing after this 1% slice remains: Computer Science and AI, Earth, Environment, and Space, People.

## Pipeline Settings

- Start stage: `generate`; pages were parsed and the small model rewrote/generated one QA per URL.
- Small model: `openai/gpt-4.1-mini` through OpenRouter.
- One QA attempt per URL.
- Generated search queries per candidate: 3.
- DuckDuckGo parallel query bound: 3.
- Search hit-rate thresholds: full question 0.3, keyword queries 0.3, overall 0.3.
- Second-stage grading accuracy threshold: 0.1 average correctness across the small-model QA panel.
- Disabled hard surface rules remain `lost_subject_anchor`, `mutable_fact_wording`, `generic_table_source_wording`, and `wikipedia_infobox_incomplete_tie_answer`; retained checks record warnings/metadata where applicable.
- Numeric answer leakage compares normalized numbers extracted from the question and answer.

## Exact Route 3 Rewriting Prompt

The exact per-candidate prompt, including the selected table payload, is stored in each JSONL record at `source_metadata.llm_prompt`. The stable instruction block from this rerun was:

```text
Generate one SimpleQA-style factual question from a Wikipedia infobox or table.
Return JSON only.

Requirements:
- Use a composition operation over table rows or values: max, min, sum, count, comparison, or ordinal.
- The answer must be a stable entity/value from the provided table content, or a complete list when the operation has a tie.
- If max/min/ordinal/count has tied answers, return answer as a JSON array containing every tied answer.
- If a table cell has a parenthetical alias, put the plain entity name in answer and the parenthetical text in answer_aliases.
- Choose from the top three ranked tables. Prefer rank 1 unless it cannot support a safe question.
- Do not choose an infobox when a higher-ranked article table supports a composition question.
- Prefer table facts that are not easily found in article prose outside tables.
- If the answer is a temporal value, the question must specify the requested precision or unit, such as what year, what month, what day, or how many months.
- If the answer is a full calendar date, ask `what day, month, and year ...` so the expected normalization is clear.
- If the answer is a number, specify the counted quantity or unit in the question, such as gallons, people, months, authors, tracks, seats, or metres.
- Do not add units to the reference answer or answer_aliases; keep numeric reference answers as normalized values only.
- Use subject_anchors only to understand the page/table scope; do not copy anchor text mechanically into the question.
- If the page title contains a cutoff-year marker, use one of safe_subject_aliases when you need to name the subject; do not use the cutoff-year title text.
- Let the table caption or nearby section heading define the safe scope. For example, `15 largest commercial banks` supports asking which bank is largest within that listed table, but not how many banks exist in Ukraine. A `1980 chart` table supports asking about facts in that 1980 chart, but not when a song first entered a chart because it may have entered in another year.
- Do not write `according to the table`, `according to the [source] table`, or `in the List of ...`. Name the actual entity, event, chart, list, or scope naturally. Only use `according to ...` when the source is a well-known named chart or list, such as a Billboard chart or UNESCO list.
- Do not ask cumulative-statistic questions such as how many goals Messi has scored, total wins, career points, revenue, downloads, citations, or followers unless the statistic is explicitly scoped to a historically settled slice, completed event, completed season, or fixed table/list.
- Do not use generic phrases like `the listed table`, `the tournament`, or `the award` without naming the source subject.
- Do not ask about current, latest, most recent, or live-status facts.
- Avoid mutable-sounding wording such as `total assets`, `total number`, `current`, or `as of`.
- For completed historical tables, phrase the comparison as a fixed result within the named event or list.
- Do not make the question text depend on events in 2025 or later.
- Do not include the answer or answer aliases in the question or search queries.
- Generate exactly 3 answer-blind search queries.
- If no safe composition question is possible, set discard_reason and leave the other fields empty.

Output schema:
{
  "question": string,
  "answer": string | string[],
  "answer_type": "Entity|Number|Date",
  "answer_aliases": string[],
  "search_queries": string[],
  "composition_type": "max|min|sum|count|comparison|ordinal|other",
  "source_table": integer,
  "derivation_summary": string,
  "discard_reason": string | null
}
```

## Pilot Result

- Attempted URLs/candidates: 30
- Accepted QAs: 14
- Rejected QAs: 16
- URL surviving rate: 14/30 = 0.467
- Rejection reasons: second_stage_grading_accuracy_threshold_exceeded: 8, wikipedia_infobox_generation_error:RemoteDisconnected: 1, search_longtail_verifier_rejected: 1, second_stage_grading_error: 3, wikipedia_infobox_generation_error:URLError: 2, rewrite_guard_rejected: 1

## Runtime Stats

| Scope | Phase | Mean s | Median s | Min s | Max s |
|---|---|---:|---:|---:|---:|
| accepted | table extraction | 0.460 | 0.296 | 0.069 | 1.335 |
| accepted | candidate filtering | 25.251 | 21.705 | 15.388 | 63.055 |
| accepted | total per QA | 34.110 | 29.576 | 21.996 | 70.237 |
| all attempts | table extraction | 0.392 | 0.289 | 0.069 | 1.335 |
| all attempts | candidate filtering | 19.512 | 16.977 | 0.000 | 63.055 |
| all attempts | total per QA | 28.824 | 24.284 | 10.138 | 70.237 |

Aggregate phase totals from the runner:

- `page_fetch_seconds`: 1.899s
- `first_paragraph_fetch_seconds`: 1.031s
- `table_parse_seconds`: 11.762s
- `llm_question_generation_seconds`: 209.180s
- `duckduckgo_search_seconds`: 138.608s
- `second_stage_grading_seconds`: 446.430s
- `candidate_processing_seconds`: 585.362s
- `total_generation_seconds`: 279.344s

## Judge Summary

- Graded candidates: 22
- `openai/gpt-4.1-mini`: runs=22, correct=6, incorrect=16, not_attempted=0, accuracy=0.273
- `google/gemini-3-flash-preview`: runs=22, correct=6, incorrect=16, not_attempted=0, accuracy=0.273

## Accepted QAs

| Domain | Subdomain | Question | Answer | Source URL | Table | Table extraction s | Filtering s | Total s | Overall hit rate | Judge accuracy | Judge grades |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---|
| Architecture and Transportation | airports | Which year had the highest passenger traffic at Visakhapatnam Airport? | 2024-2025 | https://en.wikipedia.org/wiki/Visakhapatnam_Airport | Annual passenger traffic and aircraft movement | 0.546 | 16.908 | 21.996 | 0.000 | 0.000 | openai/gpt-4.1-mini=INCORRECT, google/gemini-3-flash-preview=INCORRECT |
| Arts and Media | film awards | Which producer(s) won the Filmfare Award for Best Film – Telugu the most times in the 2010s? | Shobu Yarlagadda and Prasad Devineni | https://en.wikipedia.org/wiki/Filmfare_Award_for_Best_Film_%E2%80%93_Telugu | 2010s | 0.471 | 16.343 | 23.093 | 0.025 | 0.000 | openai/gpt-4.1-mini=INCORRECT, google/gemini-3-flash-preview=INCORRECT |
| Education | universities | Which president of Leipzig University served in the year 1918 and resigned? | Otto Hölder | https://en.wikipedia.org/wiki/Presidents_of_Leipzig_University | 20th century | 1.090 | 21.730 | 30.939 | 0.000 | 0.000 | openai/gpt-4.1-mini=INCORRECT, google/gemini-3-flash-preview=INCORRECT |
| Geography | islands | Which lighthouse in the Canary Islands has the tallest tower height? | La Isleta | https://en.wikipedia.org/wiki/List_of_lighthouses_in_the_Canary_Islands | Lighthouses | 0.167 | 63.055 | 70.237 | 0.125 | 0.000 | openai/gpt-4.1-mini=INCORRECT, google/gemini-3-flash-preview=INCORRECT |
| Language and Literature | books | Which books of the Protestant Bible have plays authored by women in the Sixty-Six Books collection? | Genesis; Exodus; Leviticus; Deuteronomy; Joshua; Ruth; 1 Chronicles; 2 Chronicles; Ezra; Esther; Psalms; Proverbs; Ecclesiastes; Song of Solomon; Isaiah; Lamentations; Ezekiel; Hosea; Joel; Amos; Obadiah; Jonah; Micah; Nahum; Habakkuk; Zephaniah; Haggai; Zechariah; Malachi; Matthew; Mark; Philippians; Colossians | https://en.wikipedia.org/wiki/Sixty-Six_Books | List of plays | 0.103 | 45.351 | 53.174 | 0.000 | 0.000 | openai/gpt-4.1-mini=INCORRECT, google/gemini-3-flash-preview=INCORRECT |
| Life Sciences | birds | Which Tangara species has the widest distribution across countries? | Blue-and-black tanager; Paradise tanager | https://en.wikipedia.org/wiki/Tangara_(bird) | Taxonomy and species list | 0.213 | 15.388 | 24.398 | 0.000 | 0.000 | openai/gpt-4.1-mini=INCORRECT, google/gemini-3-flash-preview=INCORRECT |
| Mathematics | mathematical constants | Which solvent has the highest ebullioscopic constant Kb in K⋅kg/mol? | Camphor | https://en.wikipedia.org/wiki/Ebullioscopic_constant | Values for some solvents | 0.069 | 17.046 | 23.599 | 0.000 | 0.000 | openai/gpt-4.1-mini=INCORRECT, google/gemini-3-flash-preview=INCORRECT |
| Medicine and Health | hospitals | Which NHS regional hospital board in England had the greatest number of county boroughs between 1947 and 1974? | Manchester | https://en.wikipedia.org/wiki/List_of_NHS_regional_hospital_boards_(1947%E2%80%931974) | List of NHS Regional Hospital Boards in England, 1947-1974 | 0.117 | 22.073 | 28.212 | 0.034 | 0.000 | openai/gpt-4.1-mini=INCORRECT, google/gemini-3-flash-preview=INCORRECT |
| Philosophy and Religion | religion demographics | Which ethnic group had the highest percentage reporting no religion in 2022 in Scotland? | Chinese | https://en.wikipedia.org/wiki/Religion_in_Scotland | Irreligious by Ethnic group [ 99 ] | 0.432 | 16.866 | 23.933 | 0.000 | 0.000 | openai/gpt-4.1-mini=INCORRECT, google/gemini-3-flash-preview=INCORRECT |
| Physical Sciences | stars | Which Ultimate Collector Series Lego Star Wars set has the highest number of pieces? | Millennium Falcon | https://en.wikipedia.org/wiki/Lego_Star_Wars | Ultimate Collector Series (UCS) | 1.212 | 21.677 | 27.960 | 0.125 | 0.000 | openai/gpt-4.1-mini=INCORRECT, google/gemini-3-flash-preview=INCORRECT |
| Politics and Law | elections | Which Arizona congressional district had the highest total number of votes in the 2016 House elections? | District 6 | https://en.wikipedia.org/wiki/2016_United_States_House_of_Representatives_elections_in_Arizona | By district | 1.335 | 23.311 | 34.309 | 0.000 | 0.000 | openai/gpt-4.1-mini=INCORRECT, google/gemini-3-flash-preview=INCORRECT |
| Society and Culture | museums | Which Nigerian state has the most listed National Monuments and Heritage Sites? | Bauchi State | https://en.wikipedia.org/wiki/National_Commission_for_Museums_and_Monuments | Listed National Monuments and Heritage Sites | 0.284 | 21.850 | 45.646 | 0.000 | 0.000 | openai/gpt-4.1-mini=INCORRECT, google/gemini-3-flash-preview=INCORRECT |
| Sports and Recreation | stadiums | Which team scored the most goals in a single match at the 2018 Asian Games Men's Football held at Wibawa Mukti Stadium? | Japan | https://en.wikipedia.org/wiki/Wibawa_Mukti_Stadium | 2018 Asian Games Men's Football | 0.088 | 30.239 | 37.199 | 0.075 | 0.000 | openai/gpt-4.1-mini=INCORRECT, google/gemini-3-flash-preview=INCORRECT |
| History | battles | Which brigade had the largest strength in Andrei Grigorevich Rosenberg's forces at Bassignana? | Miloradovich Musketeer Regiment, one battalion | https://en.wikipedia.org/wiki/Battle_of_Bassignana_(1799) | Andrei Grigorevich Rosenberg's forces at Bassignana [ 11 ] | 0.308 | 21.680 | 32.838 | 0.000 | 0.000 | openai/gpt-4.1-mini=INCORRECT, google/gemini-3-flash-preview=INCORRECT |

## All Attempts

| Status | Domain | Subdomain | Question | Answer | Answer type | Rejection reason | Rejection rule | Source URL | Table | Total s | Overall hit rate | Accuracy |
|---|---|---|---|---|---|---|---|---|---|---:|---:|---:|
| ACCEPTED | Architecture and Transportation | airports | Which year had the highest passenger traffic at Visakhapatnam Airport? | 2024-2025 | Entity |  |  | https://en.wikipedia.org/wiki/Visakhapatnam_Airport | Annual passenger traffic and aircraft movement | 21.996 | 0.000 | 0.000 |
| REJECTED | Architecture and Transportation | airports | In what year did Carlisle Lake District Airport handle the highest number of passengers? | 2019 | Date | second_stage_grading_accuracy_threshold_exceeded | accuracy_threshold_exceeded | https://en.wikipedia.org/wiki/Carlisle_Lake_District_Airport | Traffic statistics at Carlisle Lake District Airport | 17.949 | 0.100 | 0.500 |
| ACCEPTED | Arts and Media | film awards | Which producer(s) won the Filmfare Award for Best Film – Telugu the most times in the 2010s? | Shobu Yarlagadda and Prasad Devineni | Entity |  |  | https://en.wikipedia.org/wiki/Filmfare_Award_for_Best_Film_%E2%80%93_Telugu | 2010s | 23.093 | 0.025 | 0.000 |
| REJECTED | Arts and Media | film awards | Which director has won the most Nandi Award for Best Feature Film - Gold? | K. Viswanath | Entity | second_stage_grading_accuracy_threshold_exceeded | accuracy_threshold_exceeded | https://en.wikipedia.org/wiki/Nandi_Award_for_Best_Feature_Film | Best Feature Film - Gold | 31.403 | 0.000 | 1.000 |
| REJECTED | Economy and Business | banks | https://en.wikipedia.org/wiki/List_of_banks_in_Ukraine |  |  | wikipedia_infobox_generation_error:RemoteDisconnected |  | https://en.wikipedia.org/wiki/List_of_banks_in_Ukraine |  | 17.394 |  |  |
| REJECTED | Economy and Business | banks | Which bank had the highest total assets in Malaysia as of 31 December 2023? | Maybank | Entity | search_longtail_verifier_rejected | keyword_queries:hit_rate_exceeded | https://en.wikipedia.org/wiki/List_of_banks_in_Malaysia | List of Malaysian Banks ranked by total assets as of 31 December 2023 (In Billions of Malaysia Ringgit) | 29.459 | 0.286 |  |
| ACCEPTED | Education | universities | Which president of Leipzig University served in the year 1918 and resigned? | Otto Hölder | Entity |  |  | https://en.wikipedia.org/wiki/Presidents_of_Leipzig_University | 20th century | 30.939 | 0.000 | 0.000 |
| REJECTED | Education | universities | Which opponent had the highest attendance at a Boston University Terriers home game during the 2014–15 season? | Harvard | Entity | second_stage_grading_accuracy_threshold_exceeded | accuracy_threshold_exceeded | https://en.wikipedia.org/wiki/2014%E2%80%9315_Boston_University_Terriers_men%27s_ice_hockey_season | Schedule | 27.304 | 0.000 | 0.500 |
| REJECTED | Engineering and Technology | bridges | Which pontoon bridge is the longest in length? | SR 520 Albert D. Rosellini Evergreen Point Floating Bridge | Entity | second_stage_grading_accuracy_threshold_exceeded | accuracy_threshold_exceeded | https://en.wikipedia.org/wiki/List_of_pontoon_bridges | Longest | 20.794 | 0.000 | 0.500 |
| REJECTED | Food, Agriculture, and Daily Life | crop production | Which single produced by Travis Scott had the highest peak chart position in the US? | " Bitch Better Have My Money " | Entity | second_stage_grading_accuracy_threshold_exceeded | accuracy_threshold_exceeded | https://en.wikipedia.org/wiki/Travis_Scott_production_discography | List of singles produced, with selected chart positions and certifications, showing year released and album name | 21.685 | 0.000 | 0.500 |
| ACCEPTED | Geography | islands | Which lighthouse in the Canary Islands has the tallest tower height? | La Isleta | Entity |  |  | https://en.wikipedia.org/wiki/List_of_lighthouses_in_the_Canary_Islands | Lighthouses | 70.237 | 0.125 | 0.000 |
| REJECTED | Geography | islands | Which district in Siau Tagulandang Biaro Islands Regency has the largest area in square kilometers? | Siau Timur | Entity | second_stage_grading_error | RemoteDisconnected | https://en.wikipedia.org/wiki/Siau_Tagulandang_Biaro_Islands_Regency | Administrative districts | 60.304 | 0.025 |  |
| REJECTED | Language and Literature | books | Which book edition of The Great Controversy has the highest word count? | The Conflict of the Ages Series , 5 volumes: The Great Controversy Between Christ and Satan in the Christian Dispensation , Volume 5 | Entity | second_stage_grading_error | ValueError | https://en.wikipedia.org/wiki/The_Great_Controversy_(book) | Publishing and distribution | 23.760 | 0.000 |  |
| ACCEPTED | Language and Literature | books | Which books of the Protestant Bible have plays authored by women in the Sixty-Six Books collection? | Genesis; Exodus; Leviticus; Deuteronomy; Joshua; Ruth; 1 Chronicles; 2 Chronicles; Ezra; Esther; Psalms; Proverbs; Ecclesiastes; Song of Solomon; Isaiah; Lamentations; Ezekiel; Hosea; Joel; Amos; Obadiah; Jonah; Micah; Nahum; Habakkuk; Zephaniah; Haggai; Zechariah; Malachi; Matthew; Mark; Philippians; Colossians | Entity |  |  | https://en.wikipedia.org/wiki/Sixty-Six_Books | List of plays | 53.174 | 0.000 | 0.000 |
| REJECTED | Life Sciences | birds | Which Picus species has the widest geographic distribution? | Grey-headed woodpecker | Entity | second_stage_grading_accuracy_threshold_exceeded | accuracy_threshold_exceeded | https://en.wikipedia.org/wiki/Picus_(bird) | Taxonomy | 19.735 | 0.077 | 1.000 |
| ACCEPTED | Life Sciences | birds | Which Tangara species has the widest distribution across countries? | Blue-and-black tanager; Paradise tanager | Entity |  |  | https://en.wikipedia.org/wiki/Tangara_(bird) | Taxonomy and species list | 24.398 | 0.000 | 0.000 |
| REJECTED | Mathematics | mathematical constants | Which original 3 data bits have the maximum number of appended bits set to 1 in the 3-of-6 code? | 000 | Entity | second_stage_grading_accuracy_threshold_exceeded | accuracy_threshold_exceeded | https://en.wikipedia.org/wiki/Constant-weight_code | 3-of-6 code | 24.169 | 0.025 | 1.000 |
| ACCEPTED | Mathematics | mathematical constants | Which solvent has the highest ebullioscopic constant Kb in K⋅kg/mol? | Camphor | Entity |  |  | https://en.wikipedia.org/wiki/Ebullioscopic_constant | Values for some solvents | 23.599 | 0.000 | 0.000 |
| ACCEPTED | Medicine and Health | hospitals | Which NHS regional hospital board in England had the greatest number of county boroughs between 1947 and 1974? | Manchester | Entity |  |  | https://en.wikipedia.org/wiki/List_of_NHS_regional_hospital_boards_(1947%E2%80%931974) | List of NHS Regional Hospital Boards in England, 1947-1974 | 28.212 | 0.034 | 0.000 |
| ACCEPTED | Philosophy and Religion | religion demographics | Which ethnic group had the highest percentage reporting no religion in 2022 in Scotland? | Chinese | Entity |  |  | https://en.wikipedia.org/wiki/Religion_in_Scotland | Irreligious by Ethnic group [ 99 ] | 23.933 | 0.000 | 0.000 |
| REJECTED | Philosophy and Religion | religion demographics | Which Bad Religion single reached the highest peak position on the US Alternative chart? | "21st Century | Entity | second_stage_grading_accuracy_threshold_exceeded | accuracy_threshold_exceeded | https://en.wikipedia.org/wiki/Bad_Religion_discography | List of singles, with selected chart positions, showing year released and album name | 26.203 | 0.067 | 1.000 |
| REJECTED | Physical Sciences | stars | Who achieved the highest speed in miles per hour in the Isle of Man TT races listed? | Bernard Codd | Entity | second_stage_grading_error | ValueError | https://en.wikipedia.org/wiki/BSA_Gold_Star | Isle of Man TT wins | 18.514 | 0.000 |  |
| ACCEPTED | Physical Sciences | stars | Which Ultimate Collector Series Lego Star Wars set has the highest number of pieces? | Millennium Falcon | Entity |  |  | https://en.wikipedia.org/wiki/Lego_Star_Wars | Ultimate Collector Series (UCS) | 27.960 | 0.125 | 0.000 |
| ACCEPTED | Politics and Law | elections | Which Arizona congressional district had the highest total number of votes in the 2016 House elections? | District 6 | Entity |  |  | https://en.wikipedia.org/wiki/2016_United_States_House_of_Representatives_elections_in_Arizona | By district | 34.309 | 0.000 | 0.000 |
| REJECTED | Politics and Law | elections | https://en.wikipedia.org/wiki/2017_Japanese_general_election |  |  | wikipedia_infobox_generation_error:URLError |  | https://en.wikipedia.org/wiki/2017_Japanese_general_election |  | 19.859 |  |  |
| REJECTED | Society and Culture | museums | https://en.wikipedia.org/wiki/Leeds_Industrial_Museum_at_Armley_Mills |  |  | wikipedia_infobox_generation_error:URLError |  | https://en.wikipedia.org/wiki/Leeds_Industrial_Museum_at_Armley_Mills |  | 18.502 |  |  |
| ACCEPTED | Society and Culture | museums | Which Nigerian state has the most listed National Monuments and Heritage Sites? | Bauchi State | Entity |  |  | https://en.wikipedia.org/wiki/National_Commission_for_Museums_and_Monuments | Listed National Monuments and Heritage Sites | 45.646 | 0.000 | 0.000 |
| REJECTED | Sports and Recreation | stadiums | Which current football stadium in Algeria has the largest seating capacity? | 5 July 1962 Stadium | Entity | rewrite_guard_rejected | forbidden_temporal_phrase | https://en.wikipedia.org/wiki/List_of_football_stadiums_in_Algeria | Current stadiums | 10.138 |  |  |
| ACCEPTED | Sports and Recreation | stadiums | Which team scored the most goals in a single match at the 2018 Asian Games Men's Football held at Wibawa Mukti Stadium? | Japan | Entity |  |  | https://en.wikipedia.org/wiki/Wibawa_Mukti_Stadium | 2018 Asian Games Men's Football | 37.199 | 0.075 | 0.000 |
| ACCEPTED | History | battles | Which brigade had the largest strength in Andrei Grigorevich Rosenberg's forces at Bassignana? | Miloradovich Musketeer Regiment, one battalion | Entity |  |  | https://en.wikipedia.org/wiki/Battle_of_Bassignana_(1799) | Andrei Grigorevich Rosenberg's forces at Bassignana [ 11 ] | 32.838 | 0.000 | 0.000 |

## Notes

- The walkthrough does not display DuckDuckGo result URLs or snippets; machine-readable search evidence remains in the JSONL metadata.
- Accepted examples are pilot candidates, not final verified data; Route 3 stores provenance and downstream filtering evidence rather than route-local factual validation.
- The revised prompt no longer asks the model to copy `preferred_subject_anchor`; it passes table/page scope as context and explicitly bans `in the List of ...` wording.
- The relaxed full-question threshold increased the number of candidates reaching second-stage grading; final acceptance is still gated by search leakage, grading accuracy, deterministic surface checks, and evidence support.
