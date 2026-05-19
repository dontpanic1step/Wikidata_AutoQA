# Wayne Rooney Two-Stage Filtering Rerun - 2026-05-19

## Stats

- Input QA: For which club did Wayne Rooney score the highest number of league goals?
- Gold answer: Manchester United
- Accepted: 0
- Rejected: 1
- Final rejection reason: `second_stage_grading_accuracy_threshold_exceeded`
- Rewrite enabled: true
- Second-stage grading enabled: true
- Output JSONL: `outputs\wayne_rooney_two_stage_rerun_2026_05_19_rejected.jsonl`
- Summary JSON: `outputs\wayne_rooney_two_stage_rerun_2026_05_19_summary.json`

## Stage Result

| Stage | Result | Notes |
| --- | --- | --- |
| Rewrite | survived | Stored in `source_metadata.small_model_rewrite_response`. |
| DuckDuckGo long-tail filter | survived | Search results showed obvious leakage, but configured hit-rate thresholds did not reject this run. |
| Second-stage model grading | rejected | Accuracy 1 exceeded threshold 0.1. Both answer models answered correctly. |

## Small Model QA Response

```json
{
  "question": "Which club did Wayne Rooney score the most league goals for?",
  "answer": "Manchester United",
  "answer_type": "Entity",
  "answer_aliases": [],
  "search_queries": [
    "Wayne Rooney league goals by club",
    "Wayne Rooney top scoring club",
    "Wayne Rooney Manchester United league goals"
  ],
  "reasoning_type": "max",
  "source_table": 2,
  "derivation_summary": "From the club appearances and goals table, Wayne Rooney scored 183 league goals for Manchester United, which is more than the league goals scored for any other club.",
  "discard_reason": null
}
```

## Small Model Rewrite Response

```json
{
  "rewritten_question": "For which club did Wayne Rooney score the highest number of league goals?",
  "search_queries": [
    "Wayne Rooney club with most league goals",
    "Wayne Rooney highest league goals by club",
    "Wayne Rooney league goals scored per club"
  ],
  "answer_aliases": [],
  "discard_reason": null
}
```

## Search Features

| Query | Category | Results | Title hits | Snippet hits | Answer-hit results | Triggered rule |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| full_question | full_question | 10 | 2 | 2 | 3 |  |
| keyword_query_1 | keyword_queries | 10 | 0 | 3 | 3 |  |
| keyword_query_2 | keyword_queries | 10 | 0 | 2 | 2 |  |
| keyword_query_3 | keyword_queries | 10 | 0 | 2 | 2 |  |

## Answer-Leaking Search Hits

| Query | Result title | Snippet |
| --- | --- | --- |
| full_question | Wayne Rooney Manchester United forward Profile, Stats & Career Record | Biography Wayne Rooney is widely regarded as one of the greatest footballers in Manchester United and England history. Known for his versatility, power, and football intelligence, Rooney spent the majority of his career at Manchester United |
| full_question | Wayne Rooney's Manchester United, Everton and England career in numbers | 27 - The highest tally of goals scored by Rooney in a single Premier League season (2011-12) and also the number of penalties he converted for the Manchester giants. 16 - Rooney was 16 years ... |
| full_question | Stats - Wayne Rooney | Everton Games 117 Goals 28 Assists 4 Yellow Cards 26 Red Cards 1 Manchester United Games 559 Goals 253 Assists 146 Yellow Cards 101 Red Cards 3 D.C. United Games 52 Goals 25 Assists 14 Yellow Cards 6 Red Cards 2 DERBY COUNTY Games 35 Goals  |
| keyword_query_1 | Wayne Rooney Stats, Goals, Records, Assists, Cups and more \| FBref.com | Check out the latest domestic and international stats, match logs, goals, height, weight and more for Manchester United FC, Everton FC and D.C. United playing for Wayne Rooney in the Premier League, Champions League and Major League Soccer |
| keyword_query_1 | Stats - Wayne Rooney | Everton Games 117 Goals 28 Assists 4 Yellow Cards 26 Red Cards 1 Manchester United Games 559 Goals 253 Assists 146 Yellow Cards 101 Red Cards 3 D.C. United Games 52 Goals 25 Assists 14 Yellow Cards 6 Red Cards 2 DERBY COUNTY Games 35 Goals  |
| keyword_query_1 | Wayne Rooney \| Biography & Facts \| Britannica | Wayne Rooney, English football (soccer) player who rose to international stardom as a teenager while playing with the English Premier League powerhouse Manchester United. By the time he left Man U in 2017, he had scored the most goals in th |
| keyword_query_2 | Wayne Rooney Stats, Goals, Records, Assists, Cups and more \| FBref.com | Check out the latest domestic and international stats, match logs, goals, height, weight and more for Manchester United FC, Everton FC and D.C. United playing for Wayne Rooney in the Premier League, Champions League and Major League Soccer |
| keyword_query_2 | Stats - Wayne Rooney | Everton Games 117 Goals 28 Assists 4 Yellow Cards 26 Red Cards 1 Manchester United Games 559 Goals 253 Assists 146 Yellow Cards 101 Red Cards 3 D.C. United Games 52 Goals 25 Assists 14 Yellow Cards 6 Red Cards 2 DERBY COUNTY Games 35 Goals  |
| keyword_query_3 | Wayne Rooney Stats, Goals, Records, Assists, Cups and more \| FBref.com | Check out the latest domestic and international stats, match logs, goals, height, weight and more for Manchester United FC, Everton FC and D.C. United playing for Wayne Rooney in the Premier League, Champions League and Major League Soccer |
| keyword_query_3 | Stats - Wayne Rooney | Everton Games 117 Goals 28 Assists 4 Yellow Cards 26 Red Cards 1 Manchester United Games 559 Goals 253 Assists 146 Yellow Cards 101 Red Cards 3 D.C. United Games 52 Goals 25 Assists 14 Yellow Cards 6 Red Cards 2 DERBY COUNTY Games 35 Goals  |

## Second-Stage Model Grading

- Accuracy: 1
- Accuracy threshold: 0.1
- Correct count: 2/2
- Duration seconds: 14.3001

| Model | Predicted answer | Grade | Grader reason |
| --- | --- | --- | --- |
| openai/gpt-4.1-mini | Wayne Rooney scored the highest number of league goals for Manchester United. | CORRECT | The predicted answer correctly identifies Manchester United as the club for which Wayne Rooney scored the highest number of league goals, matching the reference answer exactly without contradiction. |
| google/gemini-3-flash-preview | Wayne Rooney scored the highest number of league goals for **Manchester United**, where he netted 183 Premier League goals. | CORRECT | The predicted answer 'Manchester United' exactly matches the reference answer and is supported by the data showing Rooney scored 183 league goals for Manchester United, the highest among all clubs he played for. |

## Phase Timings

```json
{
  "page_fetch_seconds": 0.217,
  "first_paragraph_fetch_seconds": 0.0892,
  "table_parse_seconds": 2.1366,
  "llm_question_generation_seconds": 7.2853,
  "total_generation_seconds": 9.8857,
  "rewrite_seconds": 4.9242,
  "number_reference_margin_seconds": 0,
  "duckduckgo_search_seconds": 0.1479,
  "total_processing_seconds": 19.3727,
  "candidate_processing_seconds": 19.3727,
  "second_stage_grading_seconds": 14.3001
}
```
