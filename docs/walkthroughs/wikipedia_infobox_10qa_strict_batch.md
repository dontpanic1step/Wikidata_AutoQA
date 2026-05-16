# Wikipedia Infobox/Table Route 3 Strict Batch

Run date: 2026-05-16

This walkthrough records the 10-URL Route 3 batch that passed both filtering stages with the requested settings:

- URL source file: `config/wikipedia_table_urls.txt`
- Accepted output: `outputs/wikipedia_infobox_10qa_accepted.jsonl`
- Rejected output: `outputs/wikipedia_infobox_10qa_rejected.jsonl`
- Summary output: `outputs/wikipedia_infobox_10qa_summary.json`
- Small model: `openai/gpt-4.1-mini`
- Second-stage grading: enabled
- Search hit-rate thresholds: full question `0.0`, keyword queries `0.3`, overall `0.3`
- Second-stage accuracy threshold: `0.1`
- Result: 10 generated, 10 accepted, 0 rejected

No DuckDuckGo result URLs or snippets are displayed here.

## URL Generation Mechanism

`scripts/generate_wikipedia_table_urls.py` writes `domain<TAB>url` lines and scores candidate pages by fetching Wikipedia parse HTML, extracting infoboxes/wikitables, and ranking tables. The scoring prefers article tables with many rows, headers, numeric/comparable columns, and low prose leakage. The Route 3 runner accepts both URL-only lines and `domain<TAB>url`, preserving the domain in `source_metadata.content_domain`.

For this strict run, the final 10 URLs skewed toward historical chart/awards tables because they were much more likely to pass the full-question zero-hit filter and small-model grading gate.

## Top-3 Table Handoff

The route now passes only the top three ranked tables to the small-model generation step, while storing all parsed tables in metadata. This reduces prompt load and forces the model to choose among high-score table candidates.

List/tie answers are allowed. If the table operation yields a tie, the model may return `answer` as a JSON array; the pipeline stores a display answer plus `source_metadata.answer_items`. Search leakage for list answers counts as a hit only when every list item appears in the same title or snippet, and grading treats partial list predictions as incorrect.

## Prompt Template

The small-model prompt used by Route 3 is:

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
- The question must contain one preferred_subject_anchor exactly or in a very close natural form.
- Do not use generic phrases like `the listed table`, `the tournament`, or `the award` without naming the source subject.
- Use a preferred_subject_anchor instead of the page title when the page title contains a year at or after the cutoff.
- For the 2026 FIFA World Cup page, use `23rd FIFA World Cup` instead of `2026 FIFA World Cup`.
- Do not ask about current, latest, most recent, or live-status facts.
- Avoid mutable-sounding wording such as `total assets`, `total number`, `current`, or `as of`.
- For completed historical tables, phrase the comparison as a fixed result within the named event or list.
- Do not make the question text depend on events in 2025 or later.
- Do not include the answer or answer aliases in the question or search queries.
- Generate exactly five answer-blind search queries.
- If no safe composition question is possible, set discard_reason and leave the other fields empty.

Output schema:
{
  "question": string,
  "answer": string | string[],
  "answer_aliases": string[],
  "search_queries": string[],
  "composition_type": "max|min|sum|count|comparison|ordinal|other",
  "source_table": integer,
  "derivation_summary": string,
  "discard_reason": string | null
}

Payload:
<page title, canonical URL, first paragraph, subject anchors, top-3 ranked table summaries, and table rows>
```

## Accepted QAs

| # | Domain | Source URL | Table title | Question | Answer | Full hit | Keyword hit | Overall hit | Accuracy | Table parse (s) | Filtering (s) | Total (s) |
|---:|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | Film and Television | https://en.wikipedia.org/wiki/23rd_Independent_Spirit_Awards | Films that received multiple nominations | Which film received the highest number of nominations at the 23rd Independent Spirit Awards? | Juno | 0.000 | 0.000 | 0.000 | 0.000 | 0.134 | 21.277 | 27.753 |
| 2 | Music | https://en.wikipedia.org/wiki/List_of_UK_top-ten_singles_in_1978 | Entries by artist | Which artist had the most entries in the UK top-ten singles chart in 1978? | John Travolta | 0.000 | 0.000 | 0.000 | 0.000 | 0.376 | 31.358 | 39.024 |
| 3 | Music | https://en.wikipedia.org/wiki/List_of_UK_top-ten_singles_in_1979 | Chart debuts | Which artist had the highest number of top 10 singles in the UK top-ten singles chart in 1979? | Earth, Wind and Fire; The Police | 0.000 | 0.040 | 0.033 | 0.000 | 0.377 | 19.243 | 23.978 |
| 4 | Music | https://en.wikipedia.org/wiki/List_of_UK_top-ten_singles_in_1981 | Chart debuts | Which artist had the highest number of top 10 singles debuting in the UK top-ten singles chart in 1981? | Shakin' Stevens | 0.000 | 0.150 | 0.120 | 0.000 | 0.305 | 66.954 | 74.224 |
| 5 | Music | https://en.wikipedia.org/wiki/List_of_UK_top-ten_singles_in_1982 | Chart debuts | Which artist had the highest number of top 10 singles in the UK top-ten singles chart in 1982? | Bananarama; ABC; Shalamar | 0.000 | 0.000 | 0.000 | 0.000 | 0.272 | 25.114 | 30.404 |
| 6 | Music | https://en.wikipedia.org/wiki/List_of_UK_top-ten_singles_in_1983 | Chart debuts | Which artist had the highest number of top 10 singles debuting in the UK Singles Chart in 1983? | Eurythmics | 0.000 | 0.167 | 0.125 | 0.000 | 0.302 | 17.148 | 23.354 |
| 7 | Music | https://en.wikipedia.org/wiki/List_of_Billboard_Hot_100_top-ten_singles_in_1980 | List of Billboard Hot 100 top ten singles which peaked in 1980 | Which Billboard Hot 100 top-ten single in 1980 had the longest run in the top ten? | "Do That to Me One More Time" | 0.000 | 0.000 | 0.000 | 0.000 | 0.145 | 17.316 | 22.080 |
| 8 | Music | https://en.wikipedia.org/wiki/List_of_Billboard_Hot_100_top-ten_singles_in_1982 | List of Billboard Hot 100 top ten singles which peaked in 1982 | Which Billboard Hot 100 top-ten single in 1982 spent the longest time in the top ten? | "Harden My Heart"; "I Can't Go for That"; "Centerfold"; "I Love Rock 'n' Roll"; "Ebony and Ivory"; "Don't You Want Me" | 0.000 | 0.000 | 0.000 | 0.000 | 0.132 | 22.883 | 31.818 |
| 9 | Music | https://en.wikipedia.org/wiki/List_of_Billboard_Hot_100_top-ten_singles_in_1983 | List of Billboard Hot 100 top ten singles which peaked in 1983 | Which Billboard Hot 100 top-ten single in 1983 spent the longest time in the top ten? | "Flashdance... What a Feeling" | 0.000 | 0.000 | 0.000 | 0.000 | 0.134 | 17.738 | 22.340 |
| 10 | Music | https://en.wikipedia.org/wiki/List_of_Billboard_Hot_100_top-ten_singles_in_1984 | List of Billboard Hot 100 top ten singles which peaked in 1984 | Which Billboard Hot 100 top-ten single in 1984 spent the most weeks in the top ten? | Owner of a Lonely Heart; Jump; Against All Odds; Hello | 0.000 | 0.000 | 0.000 | 0.000 | 0.148 | 28.854 | 33.565 |

`Filtering (s)` is `candidate_processing_seconds`. `Total (s)` is `total_generation_seconds + candidate_processing_seconds`.

## Runtime Stats

| Phase | Min (s) | P50 (s) | Mean (s) | Max (s) | Sum (s) |
|---|---:|---:|---:|---:|---:|
| Table extraction | 0.132 | 0.210 | 0.232 | 0.377 | 2.324 |
| Candidate filtering | 17.148 | 22.080 | 26.788 | 66.954 | 267.883 |
| DuckDuckGo search | 0.095 | 8.306 | 12.220 | 52.180 | 122.197 |
| Second-stage grading | 9.193 | 13.949 | 14.563 | 23.115 | 145.629 |
| Generation only | 4.603 | 5.748 | 6.066 | 8.935 | 60.657 |
| End-to-end per QA | 22.080 | 29.079 | 32.854 | 74.224 | 328.540 |

## Filter Outcome

All 10 accepted QAs passed the DuckDuckGo long-tail verifier and the SimpleQA-style grading panel. The grading panel accuracy was `0.0` for every accepted QA, meaning neither configured small model produced a graded-correct answer for these questions in this run.
