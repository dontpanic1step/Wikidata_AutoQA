# Inspect Correction Registry

This document records lightweight helper files used to preserve manual QA corrections discovered during inspection. It is meant to be extended whenever a new inspect-side correction workflow is added.

## Route 3 Corrected Questions

Purpose:

- Keep an auditable JSONL plan of future Route 3 manual corrections without modifying historical output data.
- Preserve the original rebalanced-record metadata so each planned correction can still be traced back to its source page, table, filters, and grading metadata.
- Store explicit planned actions, including both deletions and updates, so a later applier can execute the plan in one pass.

Data flow:

1. Raw generation outputs are produced first under `D:\Study\AI\My-research\Wikidata_Framework\outputs\recipe_segments\wikipedia_stream_recipe_2000_each_answer_type_single_fact_2026_05_24_bigbatch_fresh`.
2. Rule-based QA gate consumes raw generation outputs and writes matched/mismatched answer-type gate results under `D:\Study\AI\My-research\Wikidata_Framework\outputs\rule_based_qa_gate\wikipedia_stream_recipe_2000_each_answer_type_single_fact_2026_05_24_bigbatch_fresh_all_answer_types`.
3. Final LLM judge/filter consumes rule-gate matched records and produces `passed_all` and related split files under `D:\Study\AI\My-research\Wikidata_Framework\outputs\final_llm_qa_filter\wikipedia_stream_recipe_2000_each_answer_type_single_fact_2026_05_24_bigbatch_fresh_after_rule_gate_all_answer_types_split`.
4. Rebalancing consumes the judged/filter-passed records and writes rebalanced QA records under `D:\Study\AI\My-research\Wikidata_Framework\outputs\rebalanced_final_qas\wikipedia_stream_recipe_2000_each_answer_type_single_fact_2026_05_24_bigbatch_fresh_simpleqa_matched_seed42`.
5. OpenRouter runs are executed on the rebalanced QA records.
6. The nine-model OpenRouter predictions and judged final results are stored under `D:\Study\AI\My-research\Wikidata_Framework\outputs\final_result`.

Code map:

- Raw Route 3 generation and segment orchestration: `scripts/run_wikipedia_infobox_recipe.py`, `scripts/run_wikipedia_infobox_pipeline.py`, and `src/wikidata_simpleqa/wikipedia_infobox_generator.py`.
- Rule-based QA gate: `scripts/run_rule_based_qa_gate.py`.
- Final LLM judge/filter: `scripts/run_final_llm_qa_filter.py`.
- Rebalanced QA selection: `scripts/finalize_wikipedia_stream_batch.py`.
- OpenRouter batch prediction run: `scripts/run_openrouter_night_batch.py` and `scripts/run_openrouter_batch_predictions.py`.
- OpenRouter prediction judging / final judged outputs: `scripts/run_openrouter_night_batch.py` and `scripts/judge_openrouter_batch_predictions.py`.

Files:

- Registry: `docs/inspect/route3_corrected_questions.jsonl`
- Helper: `docs/inspect/scripts/build_corrected_questions_jsonl.py`
- Source records and rebalanced lookup: `outputs/rebalanced_final_qas/wikipedia_stream_recipe_2000_each_answer_type_single_fact_2026_05_24_bigbatch_fresh_simpleqa_matched_seed42/*.rebalanced.jsonl`
- OpenRouter run-count lookup: `outputs/final_result/full_418_openrouter_2026_05_26/full_418_predictions_1_round`

Current operation:

- Registered manual Route 3 inspection decisions as planned actions across Date, Number, Other, Person, and Place answer types.
- `action: "delete"` records planned removals.
- `action: "update"` records planned field edits in `planned_changes`.
- This registry does not edit historical outputs. It is a pending change plan for a future execution step.

Registry schema:

- `rebalanced_id`: the matching rebalanced id and the stable key for the plan item.
- `original_id`: the pre-rebalanced `passed_all` record id.
- `action`: planned operation, currently `delete` or `update`.
- `status`: plan state, currently `planned`.
- `reason`: manual inspection note explaining why the action is needed.
- `planned_changes`: object containing fields to set during a future execution step. Empty for deletions.
- `original_answer_type`: the answer type stored in the original record.
- `original_question`: the question stored in `passed_all`.
- `original_answer`: the answer stored in `passed_all`.
- `original_answer_aliases`: the aliases stored in the original record.
- `openrouter_9_model_runs`: number of complete 9-model OpenRouter runs found for the rebalanced id. Expected values are currently 0, 1, or 5.
- All remaining non-duplicate fields are inherited from the original rebalanced record.

How to add another correction:

1. Add an item to `CHANGE_PLAN` in `docs/inspect/scripts/build_corrected_questions_jsonl.py` with `rebalanced_id`, `action`, `reason`, and optional `set` fields for planned updates.
2. Run:

   ```powershell
   python docs\inspect\scripts\build_corrected_questions_jsonl.py
   ```

3. Inspect the first fields of `docs/inspect/route3_corrected_questions.jsonl` and confirm the `action`, `planned_changes`, `rebalanced_id`, and `openrouter_9_model_runs` values.

Notes:

- `original_id` values can overlap across answer types, so corrections are keyed by `rebalanced_id`.
- The helper does not edit historical outputs. It only rebuilds the inspect-side registry.
