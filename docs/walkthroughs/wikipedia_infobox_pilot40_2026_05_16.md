# Wikipedia Route 3 Pilot 40 Walkthrough

Run date: 2026-05-16

This pilot used the clarified reusable domain axis from `docs/template_catalog_review.md` plus `History`: 20 domains, two subdomains per domain, one Wikipedia URL per subdomain. The seed file is `config/wikipedia_table_urls_40.tsv`; the URL-generation prompt is `docs/wikipedia_route3_url_seed_prompt.md`.

No DuckDuckGo result URLs or snippets are displayed here. They remain in the JSONL artifacts for audit where allowed by the pipeline metadata contract.

## Settings

- URL attempts: 40
- Open failures during URL preparation: 0
- Small generation model: `openai/gpt-4.1-mini` through OpenRouter
- Generated keyword query count: 3
- DuckDuckGo bounded parallel queries per candidate: 3
- Search hit-rate thresholds: full question 0.0, keyword queries 0.3, overall 0.3
- Second-stage accuracy threshold: 0.1

## Outcome

- Generated candidates: 40
- Accepted QAs: 4
- Rejected QAs: 36
- URL surviving rate: 4/40 = 10.0%
- Candidates reaching search: 21
- Candidates reaching second-stage grading: 11

Rejection reasons:
- `rewrite_guard_rejected`: 15
- `search_longtail_verifier_rejected`: 10
- `second_stage_grading_accuracy_threshold_exceeded`: 7
- `wikipedia_infobox_incomplete_tie_answer`: 4

Runtime stats over all 40 URL attempts:
- Table extraction: mean 0.836s; median 0.620s; p95 2.100s; max 3.219s
- Filtering: mean 5.947s; median 0.082s; p95 21.162s; max 42.739s
- Total generation before/including Route 3 generation metadata: mean 6.424s; median 6.283s; p95 8.840s; max 9.601s

Aggregate phase timings:
- `page_fetch_seconds`: 0.5173s
- `first_paragraph_fetch_seconds`: 0.0749s
- `table_parse_seconds`: 33.4318s
- `llm_question_generation_seconds`: 217.7359s
- `duckduckgo_search_seconds`: 52.3389s
- `second_stage_grading_seconds`: 185.4559s
- `candidate_processing_seconds`: 237.8838s
- `total_generation_seconds`: 256.9487s

## Accepted QAs

| Domain | Subdomain | QA | Answer | Table | Hit rate | Accuracy | Runtime table/filter/total | Source URL |
|---|---|---|---|---|---:|---:|---:|---|
| Arts and Media | music chart | Which Billboard Hot 100 top-ten single in 1984 spent the most weeks in the top ten? | Owner of a Lonely Heart; Jump; Against All Odds; Hello | List of Billboard Hot 100 top ten singles which peaked in 1984 | 0.0% | 0.0% | 0.161/19.584/6.152 | https://en.wikipedia.org/wiki/List_of_Billboard_Hot_100_top-ten_singles_in_1984 |
| Life Sciences | bird populations | Which bird taxonomic order has the highest estimated population in the List of birds by population? | Apodiformes | By taxonomy | 0.0% | 0.0% | 0.436/21.162/4.645 | https://en.wikipedia.org/wiki/List_of_birds_by_population |
| People | award records | Who was the oldest nominee at the Academy Awards according to the List of Academy Award records? | Jack Nicholson | Age-related records | 0.0% | 0.0% | 0.666/15.768/4.403 | https://en.wikipedia.org/wiki/List_of_Academy_Award_records |
| History | battles | Which siege in the List of battles by casualties had the highest estimated casualties? | Siege of Baghdad | Sieges and urban combat | 0.0% | 0.0% | 0.948/26.468/5.409 | https://en.wikipedia.org/wiki/List_of_battles_by_casualties |

## All Pilot Results

| # | Status | Domain | Subdomain | QA | Answer | Table | Overall hit | Keyword hit | Full-question hit | Accuracy | Judge result | Runtime table/filter/total | Source URL | Rejection |
|---:|---|---|---|---|---|---|---:|---:|---:|---:|---|---:|---|---|
| 1 | rejected | Architecture and Transportation | tall buildings | Which building was the tallest in Fort Wayne from 1930 to 1970 according to the Timeline of tallest buildings? | Lincoln Bank Tower | Timeline of tallest buildings | n/a | n/a | n/a | n/a | not run | 0.154/0.001/6.322 | https://en.wikipedia.org/wiki/List_of_tallest_buildings_in_Fort_Wayne | rewrite_guard_rejected |
| 2 | rejected | Architecture and Transportation | airports | Which airport had the highest total passenger traffic in 2021 according to the List of busiest airports by passenger traffic? | Hartsfield–Jackson Atlanta International Airport | 2021 statistics | n/a | n/a | n/a | n/a | not run | 0.875/0.001/6.915 | https://en.wikipedia.org/wiki/List_of_busiest_airports_by_passenger_traffic | rewrite_guard_rejected |
| 3 | rejected | Arts and Media | film awards | 23rd Independent Spirit Awards | n/a | n/a | n/a | n/a | n/a | n/a | not run | 0.125/0.000/7.449 | https://en.wikipedia.org/wiki/23rd_Independent_Spirit_Awards | wikipedia_infobox_incomplete_tie_answer |
| 4 | accepted | Arts and Media | music chart | Which Billboard Hot 100 top-ten single in 1984 spent the most weeks in the top ten? | Owner of a Lonely Heart; Jump; Against All Odds; Hello | List of Billboard Hot 100 top ten singles which peaked in 1984 | 0.0% | 0.0% | 0.0% | 0.0% | openai/gpt-4.1-mini=INCORRECT, google/gemini-3-flash-preview=INCORRECT | 0.161/19.584/6.152 | https://en.wikipedia.org/wiki/List_of_Billboard_Hot_100_top-ten_singles_in_1984 | n/a |
| 5 | rejected | Computer Science and AI | supercomputers | Which country has the highest number of supercomputers in the TOP500 list as of November 2025? | United States | Distribution of supercomputers in the TOP500 list by country (as of November 2025 [update] ) [ 3 ] | n/a | n/a | n/a | n/a | not run | 0.873/0.000/9.024 | https://en.wikipedia.org/wiki/TOP500 | rewrite_guard_rejected |
| 6 | rejected | Computer Science and AI | programming languages | Which programming language has the highest lines ratio in the expressiveness comparison? | Python | Expressiveness | n/a | n/a | n/a | n/a | not run | 0.532/0.000/6.751 | https://en.wikipedia.org/wiki/Comparison_of_programming_languages | rewrite_guard_rejected |
| 7 | rejected | Earth, Environment, and Space | impact structures | Which confirmed impact structure in Europe has the largest diameter in kilometres? | Siljan | Confirmed impact structures | 50.0% | 40.0% | 60.0% | n/a | not run | 0.232/0.111/5.026 | https://en.wikipedia.org/wiki/List_of_impact_structures_in_Europe | search_longtail_verifier_rejected |
| 8 | rejected | Earth, Environment, and Space | observatories | Which astronomical observatory was established earliest according to the List of astronomical observatories? | Armagh Observatory | Observatories | 0.0% | 0.0% | 0.0% | 50.0% | openai/gpt-4.1-mini=CORRECT, google/gemini-3-flash-preview=INCORRECT | 0.574/15.358/5.997 | https://en.wikipedia.org/wiki/List_of_astronomical_observatories | second_stage_grading_accuracy_threshold_exceeded |
| 9 | rejected | Economy and Business | banks | Which bank had the highest total assets in December 2025 according to the List of largest banks? | Industrial and Commercial Bank of China | By total assets | n/a | n/a | n/a | n/a | not run | 0.244/0.001/7.173 | https://en.wikipedia.org/wiki/List_of_largest_banks | rewrite_guard_rejected |
| 10 | rejected | Economy and Business | companies | Which company has the highest profit among the largest companies by revenue? | Alphabet | List | n/a | n/a | n/a | n/a | not run | 0.301/0.001/3.830 | https://en.wikipedia.org/wiki/List_of_largest_companies_by_revenue | rewrite_guard_rejected |
| 11 | rejected | Education | colleges | Which college or university in Maine had the highest enrollment in Fall 2024? | University of Maine | Open institutions | n/a | n/a | n/a | n/a | not run | 0.283/0.001/4.407 | https://en.wikipedia.org/wiki/List_of_colleges_and_universities_in_Maine | rewrite_guard_rejected |
| 12 | rejected | Education | university rankings | Academic Ranking of World Universities | n/a | n/a | n/a | n/a | n/a | n/a | not run | 0.229/0.000/6.244 | https://en.wikipedia.org/wiki/Academic_Ranking_of_World_Universities | wikipedia_infobox_incomplete_tie_answer |
| 13 | rejected | Engineering and Technology | bridges | Which bridge had the longest suspension span in the history of longest suspension spans? | Çanakkale 1915 Bridge | History of longest suspension spans | n/a | n/a | n/a | n/a | not run | 0.806/0.001/6.170 | https://en.wikipedia.org/wiki/List_of_longest_suspension_bridge_spans | rewrite_guard_rejected |
| 14 | rejected | Engineering and Technology | dams | Which dam has the maximum installed capacity in megawatts among the largest dams? | Three Gorges Dam | n/a | 60.0% | 60.0% | 0.0% | n/a | not run | 0.156/3.307/4.477 | https://en.wikipedia.org/wiki/List_of_largest_dams | search_longtail_verifier_rejected |
| 15 | rejected | Food, Agriculture, and Daily Life | cereal production | Which country had the highest cereal production in thousands of tons according to the List of countries by cereal production? | China | Production by country | 16.7% | 15.0% | 20.0% | n/a | not run | 0.261/0.144/5.595 | https://en.wikipedia.org/wiki/List_of_countries_by_cereal_production | search_longtail_verifier_rejected |
| 16 | rejected | Food, Agriculture, and Daily Life | wine production | Which country had the highest wine production in tonnes in 2021 according to the List of wine-producing regions? | Italy | Wine production by country in 2021 | 0.0% | 0.0% | 0.0% | 100.0% | openai/gpt-4.1-mini=CORRECT, google/gemini-3-flash-preview=CORRECT | 0.759/12.787/8.450 | https://en.wikipedia.org/wiki/List_of_wine-producing_regions | second_stage_grading_accuracy_threshold_exceeded |
| 17 | rejected | Geography | lakes | Which lake in the list of lakes of Minnesota has the largest area in acres? | Alexander | n/a | 0.0% | 0.0% | 0.0% | 100.0% | openai/gpt-4.1-mini=CORRECT, google/gemini-3-flash-preview=CORRECT | 3.219/16.883/8.840 | https://en.wikipedia.org/wiki/List_of_lakes_of_Minnesota | second_stage_grading_accuracy_threshold_exceeded |
| 18 | rejected | Geography | islands | Which island has the largest area in the List of islands by area? | Greenland | Islands with areas of 1,000 km 2 (390 sq mi) or greater | 0.0% | 0.0% | 0.0% | 100.0% | openai/gpt-4.1-mini=CORRECT, google/gemini-3-flash-preview=CORRECT | 0.433/15.758/5.801 | https://en.wikipedia.org/wiki/List_of_islands_by_area | second_stage_grading_accuracy_threshold_exceeded |
| 19 | rejected | Language and Literature | literary awards | Which author won the Cybils Award for Picture book in 2009? | Liz Garton Scanlon | Picture book (2006–) | 20.0% | 0.0% | 20.0% | n/a | not run | 1.522/3.400/6.654 | https://en.wikipedia.org/wiki/Cybils_Award | search_longtail_verifier_rejected |
| 20 | rejected | Language and Literature | book awards | Which author won the National Book Award for Nonfiction most recently according to the list from 1984 to present? | Ned Blackhawk | National Book Award for Nonfiction winners, 1984 to present | n/a | n/a | n/a | n/a | not run | 1.425/0.000/5.625 | https://en.wikipedia.org/wiki/List_of_winners_of_the_National_Book_Award | rewrite_guard_rejected |
| 21 | accepted | Life Sciences | bird populations | Which bird taxonomic order has the highest estimated population in the List of birds by population? | Apodiformes | By taxonomy | 0.0% | 0.0% | 0.0% | 0.0% | openai/gpt-4.1-mini=INCORRECT, google/gemini-3-flash-preview=INCORRECT | 0.436/21.162/4.645 | https://en.wikipedia.org/wiki/List_of_birds_by_population | n/a |
| 22 | rejected | Life Sciences | cephalopod size | Which cephalopod species has the maximum recorded mantle length in the Cephalopod size table? | Mesonychoteuthis hamiltoni | Mantle length | 20.0% | 0.0% | 20.0% | n/a | not run | 1.215/2.358/5.281 | https://en.wikipedia.org/wiki/Cephalopod_size | search_longtail_verifier_rejected |
| 23 | rejected | Mathematics | mathematical constants | Which mathematical constant listed in the 'Sequences of constants' table was discovered most recently by year? | Hyperharmonic number | Sequences of constants | n/a | n/a | n/a | n/a | not run | 1.574/0.001/6.761 | https://en.wikipedia.org/wiki/List_of_mathematical_constants | rewrite_guard_rejected |
| 24 | rejected | Mathematics | polyhedra | Which uniform star polyhedron has the greatest number of vertices in the List of uniform polyhedra? | Great disnub dirhombidodecahedron | Uniform star polyhedra | 10.0% | 0.0% | 10.0% | n/a | not run | 0.539/2.370/5.974 | https://en.wikipedia.org/wiki/List_of_uniform_polyhedra | search_longtail_verifier_rejected |
| 25 | rejected | Medicine and Health | hospitals | Which hospital in the list of hospitals in Russia was established earliest? | Burdenko Main Military Clinical Hospital | Hospitals in Russia | 11.1% | 0.0% | 11.1% | n/a | not run | 0.140/3.196/4.369 | https://en.wikipedia.org/wiki/List_of_hospitals_in_Russia | search_longtail_verifier_rejected |
| 26 | rejected | Medicine and Health | epidemics | Which epidemic that started in the 2000s had the highest estimated death toll? | 2009 swine flu pandemic | Chronological table of epidemic and pandemic events that started in the 2000s | n/a | n/a | n/a | n/a | not run | 1.052/0.001/6.556 | https://en.wikipedia.org/wiki/List_of_epidemics_and_pandemics | rewrite_guard_rejected |
| 27 | rejected | People | nobel laureates | Which Nobel laureate received the Chemistry prize in 1911? | Marie Curie | .mw-parser-output .sr-only{border:0;clip:rect(0,0,0,0);clip-path:polygon(0px 0px,0px 0px,0px 0px);height:1px;margin:-1px;overflow:hidden;padding:0;position:absolute;width:1px;white-space:nowrap} list of laureates | n/a | n/a | n/a | n/a | not run | 0.694/0.000/5.014 | https://en.wikipedia.org/wiki/List_of_Nobel_laureates | rewrite_guard_rejected |
| 28 | accepted | People | award records | Who was the oldest nominee at the Academy Awards according to the List of Academy Award records? | Jack Nicholson | Age-related records | 0.0% | 0.0% | 0.0% | 0.0% | openai/gpt-4.1-mini=INCORRECT, google/gemini-3-flash-preview=INCORRECT | 0.666/15.768/4.403 | https://en.wikipedia.org/wiki/List_of_Academy_Award_records | n/a |
| 29 | rejected | Philosophy and Religion | popes | Which pope of the 10th century had the longest papacy duration? | John X | Popes of the 10th century | n/a | n/a | n/a | n/a | not run | 1.306/0.000/6.532 | https://en.wikipedia.org/wiki/List_of_popes | rewrite_guard_rejected |
| 30 | rejected | Philosophy and Religion | religion demographics | Religion in the United States | n/a | n/a | n/a | n/a | n/a | n/a | not run | 2.100/0.000/7.601 | https://en.wikipedia.org/wiki/Religion_in_the_United_States | wikipedia_infobox_incomplete_tie_answer |
| 31 | rejected | Physical Sciences | chemical elements | Which chemical element has the highest density according to the List of chemical elements? | Osmium | List | 0.0% | 0.0% | 0.0% | 100.0% | openai/gpt-4.1-mini=CORRECT, google/gemini-3-flash-preview=CORRECT | 0.547/42.739/7.780 | https://en.wikipedia.org/wiki/List_of_chemical_elements | second_stage_grading_accuracy_threshold_exceeded |
| 32 | rejected | Physical Sciences | nearby stars | Which star known to have passed or will pass within 5 light-years of the Sun has the minimum closest approach distance? | Gliese 710 | Stars that are known to have passed or will pass within 5 light-years of the Sun in the past or future [ 82 ] [ 83 ] [ 84 ] | n/a | n/a | n/a | n/a | not run | 1.098/0.001/6.736 | https://en.wikipedia.org/wiki/List_of_nearest_stars | rewrite_guard_rejected |
| 33 | rejected | Politics and Law | municipal elections | Who received the highest number of votes in the 47th Ward General election in the 2019 Chicago aldermanic election? | Matt Martin | 47th Ward General election [ 41 ] [ 22 ] | 10.0% | 10.0% | 10.0% | n/a | not run | 2.688/3.950/8.659 | https://en.wikipedia.org/wiki/2019_Chicago_aldermanic_election | search_longtail_verifier_rejected |
| 34 | rejected | Politics and Law | court cases | Which case in United States Reports, volume 1 was decided in the earliest year? | Anonymous | List of cases in 1 U.S. (1 Dall.) | 0.0% | 0.0% | 0.0% | 50.0% | openai/gpt-4.1-mini=INCORRECT, google/gemini-3-flash-preview=CORRECT | 0.363/15.052/7.934 | https://en.wikipedia.org/wiki/United_States_Reports,_volume_1 | second_stage_grading_accuracy_threshold_exceeded |
| 35 | rejected | Society and Culture | museums | Which county in Kentucky has the most museums listed in the List of museums in Kentucky? | Fayette | Museums | 0.0% | 0.0% | 0.0% | 50.0% | openai/gpt-4.1-mini=CORRECT, google/gemini-3-flash-preview=INCORRECT | 0.547/17.308/4.940 | https://en.wikipedia.org/wiki/List_of_museums_in_Kentucky | second_stage_grading_accuracy_threshold_exceeded |
| 36 | rejected | Society and Culture | public art | Which public artwork in the St. Vincent / Greenbriar neighborhood of Indianapolis has the greatest height in feet? | Untitled | St. Vincent / Greenbriar | n/a | n/a | n/a | n/a | not run | 1.050/0.001/9.601 | https://en.wikipedia.org/wiki/List_of_public_art_in_Indianapolis | rewrite_guard_rejected |
| 37 | rejected | Sports and Recreation | tournament venues | Which stadium has the highest seating capacity among the venues for the 23rd FIFA World Cup? | AT&T Stadium | List of tournament venues | 10.0% | 5.0% | 20.0% | n/a | not run | 1.963/0.120/7.535 | https://en.wikipedia.org/wiki/2026_FIFA_World_Cup | search_longtail_verifier_rejected |
| 38 | rejected | Sports and Recreation | athletics results | Which nation won the most gold medals at the 2014 World Junior Championships in Athletics? | United States | Medal table | 65.0% | 70.0% | 60.0% | n/a | not run | 0.515/0.053/5.899 | https://en.wikipedia.org/wiki/2014_World_Junior_Championships_in_Athletics | search_longtail_verifier_rejected |
| 39 | accepted | History | battles | Which siege in the List of battles by casualties had the highest estimated casualties? | Siege of Baghdad | Sieges and urban combat | 0.0% | 0.0% | 0.0% | 0.0% | openai/gpt-4.1-mini=INCORRECT, google/gemini-3-flash-preview=INCORRECT | 0.948/26.468/5.409 | https://en.wikipedia.org/wiki/List_of_battles_by_casualties | n/a |
| 40 | rejected | History | empires | List of largest empires | n/a | n/a | n/a | n/a | n/a | n/a | not run | 0.826/0.000/8.419 | https://en.wikipedia.org/wiki/List_of_largest_empires | wikipedia_infobox_incomplete_tie_answer |

## Prompt Reproducibility

The strong-model URL seed prompt is stored in `docs/wikipedia_route3_url_seed_prompt.md`. The exact per-candidate Route 3 rewriting prompt, including the three selected tables given to the small model, is stored in each JSONL record at `source_metadata.llm_prompt`.

The stable instruction prefix used by the Route 3 rewriting prompt was:

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
- Unless explicitly stated otherwise, treat all table entries as local, bounded facts rather than global or exhaustive claims. Do not infer uniqueness or completeness from a table entry. For example, if a table states that "Song X entered the UK chart top 10 in 1980," avoid asking "In which year did song X enter the UK chart top 10?" because the song may have entered the top 10 in other years as well.
- The question must contain one preferred_subject_anchor exactly or in a very close natural form.
- Do not use generic phrases like `the listed table`, `the tournament`, or `the award` without naming the source subject.
- Use a preferred_subject_anchor instead of the page title when the page title contains a year at or after the cutoff.
- For the 2026 FIFA World Cup page, use `23rd FIFA World Cup` instead of `2026 FIFA World Cup`.
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

## Notes

- The current-code run accepted 4 pilot candidates. The incomplete grouped nomination tie that previously slipped through is now rejected as `wikipedia_infobox_incomplete_tie_answer` before shared filtering.
- Search filtering was faster than model grading in aggregate, but the 40-record run still spent most wall-clock time in LLM generation plus second-stage grading.
