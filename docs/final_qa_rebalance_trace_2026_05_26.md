# Final QA Rebalance Trace, 2026-05-26

This note traces the final cleanup path for the Route 3 Wikipedia semi-structured QA batch:

`wikipedia_stream_recipe_2000_each_answer_type_single_fact_2026_05_24_bigbatch_fresh`

It records how misplaced answer-type records were moved, how the appended passed-all JSONLs were used, and how the final rebalanced sample was selected.

## Source Stages

The rule-based answer-type gate output is stored at:

`outputs/rule_based_qa_gate/wikipedia_stream_recipe_2000_each_answer_type_single_fact_2026_05_24_bigbatch_fresh_all_answer_types`

The final LLM judge output after the rule gate is stored at:

`outputs/final_llm_qa_filter/wikipedia_stream_recipe_2000_each_answer_type_single_fact_2026_05_24_bigbatch_fresh_after_rule_gate_all_answer_types`

The split final-judge passed/failed JSONLs are stored at:

`outputs/final_llm_qa_filter/wikipedia_stream_recipe_2000_each_answer_type_single_fact_2026_05_24_bigbatch_fresh_after_rule_gate_all_answer_types_split`

The manually appended passed-all JSONLs are stored at:

`outputs/final_llm_qa_filter/wikipedia_stream_recipe_2000_each_answer_type_single_fact_2026_05_24_bigbatch_fresh_after_rule_gate_all_answer_types_split/passed_all_with_manual_answer_type_moves`

The rebalanced final candidate JSONLs are stored at:

`outputs/rebalanced_final_qas/wikipedia_stream_recipe_2000_each_answer_type_single_fact_2026_05_24_bigbatch_fresh_simpleqa_matched_seed42`

## Cleanup Rules

The rule-based answer-type gate runs after second-stage long-tail filtering and before the final LLM judge.

- `Person`: tokenize the answer, ignore single-letter initials, and flag as mismatch when at least 50% of answer tokens are common English words after subtracting common name tokens.
- `Place`: compare the question's requested category against a broad geography whitelist seeded from SimpleQA Verified place questions and maintained geography categories.
- `Date`: accept year-only, month-year, and full-date answers; normalize parseable numeric dates to month-first text; reject ranges and vague era expressions.
- `Number` and `Other`: no deterministic rule-based gate yet.

The final LLM judge receives the question, answer, aliases, answer type, page title, first paragraph, and all stored parsed Markdown tables. It judges:

- `answer_derivable_from_context`
- `unique_and_stable_answer`
- `self_contained_question`
- `question_matches_answer_type`

It also assigns a topical domain from:

`Science & technology`, `Politics`, `Art`, `Geography`, `Sports`, `Music`, `TV Shows`, `History`, `Video Games`, `Other`

## Manual Answer-Type Moves

Records whose only final-judge failure was `question_matches_answer_type=NO` were reviewed separately. The following nine records were appended into the passed-all set under the answer type chosen for final review.

| ID | Original answer type | Target answer type | Question | Answer |
|---|---|---|---|---|
| `wikipedia_stream_000051` | Other | Person | Which individual served as mayor of Menasha, Wisconsin, immediately before John L. Klein's second term? | Kenneth E. Holmes |
| `wikipedia_stream_000055` | Other | Person | What is the name of the mayor who served in Abère from 2008 to 2014? | Claude Conte-Hourticq |
| `wikipedia_stream_000062` | Other | Person | What is the name of the mayor who served Arzacq-Arraziguet from 1995 to 2020? | Henri Fam |
| `wikipedia_stream_000068` | Other | Person | What is the name of the mayor who served Arget from 1995 to 2001? | Chantal Gallenmuller |
| `wikipedia_stream_000070` | Other | Person | What is the name of the mayor who served Ainharp from 1854 to 1855? | Alexandre Bente |
| `wikipedia_stream_000113` | Other | Person | Which player among the other batters in the 1945 Chicago Cubs season had the highest batting average? | Reggie Otero |
| `wikipedia_stream_000009` | Person | Place | What was the name of the township seat of Gosfield South in Essex County before the 1999 restructuring? | Kingsville |
| `wikipedia_stream_000036` | Place | Place | In which city did Kent Austin's team win the Grey Cup in 2007? | Saskatchewan |
| `wikipedia_stream_000052` | Place | Place | Which province won the Miss Dominican Republic title in the year 1978? | María Trinidad Sánchez |

The appended passed-all source counts were:

| Answer type | Count |
|---|---:|
| Date | 108 |
| Number | 141 |
| Other | 147 |
| Person | 91 |
| Place | 61 |
| Total | 548 |

## Rebalancing Target

The rebalanced set keeps all appended `Place` records. Because SimpleQA Verified has `Place` at 14.6%, keeping 61 Place records implies a final size of about 418 records. The answer-type quotas therefore are:

| Answer type | SimpleQA Verified target | Selected count |
|---|---:|---:|
| Place | 14.6% | 61 |
| Number | 18.5% | 77 |
| Person | 19.8% | 83 |
| Date | 22.2% | 93 |
| Other | 24.9% | 104 |
| Total | 100.0% | 418 |

The domain distribution cannot match SimpleQA Verified exactly because several SimpleQA-heavy domains are scarce in the appended source set. The strategy is:

1. Keep all records from domains whose availability is below the SimpleQA Verified ideal count.
2. Downsample overrepresented domains to fill the remaining slots.
3. Satisfy the answer-type quotas as hard constraints.
4. Sample within each answer-type/domain bucket only when selected count is lower than availability.

The selected domain counts are:

| Domain | SimpleQA Verified target | Available | Selected |
|---|---:|---:|---:|
| Science & technology | 16.0% | 11 | 11 |
| Politics | 17.6% | 110 | 110 |
| Art | 14.5% | 9 | 9 |
| Geography | 11.1% | 27 | 27 |
| Sports | 11.7% | 168 | 95 |
| Music | 10.2% | 23 | 23 |
| TV Shows | 2.0% | 57 | 15 |
| History | 5.2% | 39 | 39 |
| Video Games | 1.5% | 6 | 6 |
| Other | 10.2% | 98 | 83 |

## Cell Quotas

The final answer-type/domain quotas are:

| Answer type | Domain quotas |
|---|---|
| Date | Science & technology 1; Politics 16; Art 2; Geography 2; Sports 17; Music 6; TV Shows 14; History 15; Video Games 2; Other 18 |
| Number | Science & technology 1; Politics 12; Art 1; Geography 4; Sports 2; Music 7; History 8; Video Games 2; Other 40 |
| Other | Science & technology 6; Politics 31; Art 3; Geography 5; Sports 33; Music 3; History 7; Video Games 2; Other 14 |
| Person | Science & technology 2; Politics 40; Art 1; Geography 1; Sports 28; Music 1; TV Shows 1; History 4; Other 5 |
| Place | Science & technology 1; Politics 11; Art 2; Geography 15; Sports 15; Music 6; History 5; Other 6 |

## Reproducibility

Random seed: `42`

Selection algorithm:

1. Load the appended passed-all JSONLs.
2. Assign each record to `(answer_type, domain_choice)`.
3. Stable-sort each bucket by source file, source line index, id, question, and answer.
4. If the bucket quota equals availability, keep every record.
5. If the bucket quota is lower than availability, use `random.Random(42).sample(bucket, quota)` without replacement.
6. Sort selected records back into stable source order before writing each answer-type JSONL.

Each selected record includes a `rebalanced_selection` object with the selection seed, method, source file, source line index, answer type, domain, cell quota, cell availability, answer-type quota, and domain quota.

The machine-readable run summary is:

`outputs/rebalanced_final_qas/wikipedia_stream_recipe_2000_each_answer_type_single_fact_2026_05_24_bigbatch_fresh_simpleqa_matched_seed42/rebalance_summary.json`
