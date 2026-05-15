# Branch 5-13-restored Notes

This note summarizes the difference between `5-13-after-incident` and the restored branch snapshot `5-13-restored`.

## Restoration Scope

`5-13-after-incident` preserved tracked files after the incident but lost several untracked recovery files. `5-13-restored` recreates the missing modules, completes the planned staged implementation through the validated vertical slice, and records the final walkthrough.

The restored branch should be treated as the canonical continuation of the 5-13 design.

## Recovered Missing Files

The branch restores the missing recovery files needed for importability, grading, route-local validation, and tests:

- `scripts/grade_predictions.py`
- `src/wikidata_simpleqa/cheap_model_qa.py`
- `src/wikidata_simpleqa/grading.py`
- `src/wikidata_simpleqa/number_reference.py`
- `src/wikidata_simpleqa/route1_validators.py`
- `tests/test_grading.py`
- `tests/test_number_reference.py`
- `tests/test_route1_validators.py`
- `tests/test_wikidata_client.py`

It also adds documentation artifacts:

- `docs/branch_5_13_notes.md`
- `docs/branch_5_13_restored_notes.md`
- `docs/terminology.md`
- `docs/walkthroughs/product_manufacturer_walkthrough_5_13_restored.md`

## Design Changes Since 5-13-after-incident

- `docs/design.md` now describes the restored branch rather than only the intended pre-incident 5-13 plan.
- Route 1 remains template-led inside the shared multi-generator pipeline.
- The rewrite contract is shared across routes and asks for a rewritten question, exactly five search queries, answer aliases, and an optional discard reason.
- The rewrite prompt now explicitly says not to add or change information from the canonical question and not to include the answer or answer aliases in the rewritten question.
- The old internal sitelink/claim-count popularity gates remain disabled as long-tail filters. They are retained only as metadata.
- DuckDuckGo stage-1 filtering now records all result evidence and uses normalized answer/alias matching.
- DuckDuckGo title answer hits are thresholded rather than unconditional rejection rules, so debug thresholds of `1.0` truly let candidates pass.
- SimpleQA Verified-style model-panel grading replaces the earlier idea of a standalone cheap-model rejection gate.
- For `Number` templates, answers are normalized during candidate construction, and SimpleQA Verified-style margin handling is available for grading and search evidence logic.

## Route 1 And Wikidata Changes

- Route 1 now has an explicit Wikidata validator bundle in `route1_validators.py`.
- Route 1 validation rejects missing subject labels before ambiguity search.
- The Wikidata client now treats HTTP-200 API payloads containing an `error` object as API errors rather than successful responses.
- Retryable API errors such as `maxlag` are recorded and retried according to the configured retry policy.
- Blank `wbsearchentities` queries are skipped and recorded instead of sent to the API.
- Heavy WDQS harvesting is attempted first where intended.
- The light Wikibase API path (`wbsearchentities` plus `wbgetentities`) is retained only as fallback and can be disabled.
- The Route 1 subject-seed fallback supports year, month, and day window granularities, with year as the default and descending-order windows when a smaller granularity is used.
- The API-light fallback repairs subject labels from seed text when hydration lacks a usable English label and drops candidates that still have no label.

## Long-Tail And Grading Changes

- Stage 1 uses DuckDuckGo evidence over the rewritten question plus five rewrite-generated search queries.
- Stored DuckDuckGo evidence includes query text, result titles, URLs, snippets, answer inclusion flags, hit counts, category hit rates, and triggered rules.
- Answer aliases generated or carried through the pipeline are used in DuckDuckGo string-inclusion checks.
- Cheap-model QA is no longer allowed to reject candidates directly for SimpleQA Verified alignment.
- Stage 2 runs a configurable small-model answer panel and then grades those answers using a SimpleQA Verified-style autograder.
- The default answer models are `openai/gpt-4.1-mini` and `google/gemini-3-flash-preview`.
- The default grader model is `openai/gpt-4.1-mini`.
- Accuracy thresholds remain configurable.

## Template Catalog And Terminology Changes

- Terminology was cleaned up so broad areas such as `Architecture and Transportation` are called domains, while identifiers such as `benchmark_release_date` are called template keys.
- `docs/terminology.md` records legacy term mappings so future code does not drift.
- `AGENTS.md` and `docs/design.md` cite the canonical terminology expectations.
- Every template now carries an `answer_type`.
- Template status reporting includes answer-type statistics.
- The human-readable template status index moved from `outputs/template_status_index.md` to `docs/template_status_index.md`.
- `outputs/template_status_index.json` remains the machine-readable companion.
- The obsolete `active` / `blueprint` pilot-era distinction no longer drives the human-facing status index.
- The `frozen` bucket is documented and preserved as an explicit template-key override while retaining run-derived diagnostic status metadata.

## Validation Walkthrough

The restored branch was validated with the `product_manufacturer` template:

- Canonical question: `Which company manufactured the product PlayStation 5 Pro?`
- Rewritten question: `Who is the manufacturer of the PlayStation 5 Pro?`
- Gold answer: `Sony Interactive Entertainment`
- Accepted candidates: `1`
- Rejected candidates: `0`
- DuckDuckGo stage-1 thresholds: `1.0`
- Model-panel accuracy threshold: `1.0`
- Model-panel accuracy: `1.0`

The walkthrough is recorded in `docs/walkthroughs/product_manufacturer_walkthrough_5_13_restored.md`. It includes every DuckDuckGo URL, snippet, string-inclusion result, small-model answer, grader judgement, phase timing, bottleneck, and observed network problem.

## Known Operational Notes

- WDQS remains the main bottleneck. In the final walkthrough, the heavy direct WDQS path and day-window subject-seed path timed out before the API-light fallback succeeded.
- The API-light fallback is therefore important for small vertical-slice validation, but it should remain fallback-only.
- The PowerShell profile on the local machine prints a broken conda-hook warning for `D:\python2022\Scripts\conda.exe`. The warning appears after commands complete and did not affect the successful run.
- `docs/human_notes/` is not part of the restoration documentation contract and should remain human-maintained.

## Test Coverage Added Or Expanded

The restored branch adds or expands tests for:

- Route 1 validator behavior
- Wikidata client API error handling and blank search-query handling
- grading and model-panel summarization
- number reference normalization and margin behavior
- candidate harvesting window granularity and API-light fallback
- generation pipeline timing and stage-2 grading
- DuckDuckGo threshold behavior and answer-alias matching
- template catalog terminology and answer-type reporting

The final focused validation set passed before snapshotting:

- `python -m unittest discover -s tests -p "test_wikidata_client.py"`
- `python -m unittest discover -s tests -p "test_route1_validators.py"`
- `python -m unittest discover -s tests -p "test_candidate_harvester.py"`
- `python -m unittest discover -s tests -p "test_generator_validators.py"`
- `python -m unittest discover -s tests -p "test_generation_pipeline.py"`

The final full local suite also passed:

- `python -m unittest discover -s tests`
- Result: `231 tests in 5.799s, OK`
