# Compatibility And Historical Settings

This file names code and settings that may remain temporarily for artifact compatibility or import stability but are outside the formal Route 3 method. Their presence does not make them supported interfaces. The sole formal user entry point is `scripts/run_wikipedia_infobox_recipe.py`.

## Historical routes and workflows

- Route 1, Route 2, Route 4, KELM, and their scripts/configuration are historical.
- The old finalization, standalone rule gate, final LLM judge, similarity deduplication, subject-URL deduplication, and domain round-robin workflows are historical.
- `scripts/run_openrouter_night_batch.py` is an unused historical evaluation orchestrator. Only the two protected scripts named below remain formal evaluation tools.
- Do not repair, extend, or invoke these paths during reconstruction unless a milestone requires the smallest compatibility edit needed for Route 3 startup.

## Internal worker compatibility surface

`scripts/run_wikipedia_infobox_pipeline.py` is retained as the recipe's internal segment worker. Direct invocation, URL-list operation, validation-stage operation, and other worker-only controls are not formal user interfaces.

The following controls are compatibility surfaces scheduled for removal from the formal recipe/worker interface:

- KELM rewrite and hidden `--enable-rewrite` aliases;
- LLM table choice;
- configurable reasoning-type selection;
- extra prompt text;
- pageview prefiltering;
- broad, custom, or random page discovery;
- REST first-paragraph fallback;
- table-filter toggles;
- prose-leakage toggles;
- minimum table-score CLI overrides;
- URL-list input;
- legacy validation CLI input/start-stage controls.

Removing a control keeps the milestone-specified formal behavior fixed. It does not authorize a replacement switch, fallback, or heuristic.

## Removed rule-based compatibility fields

These names are not formal Route 3 outputs and are removed in the scheduled cleanup milestone:

- `preferred_table_context`
- `no_oversized_tables`
- `person_common_words_minus_common_names`
- `question_unambiguous`
- `stable_answer`
- `rewrite_guard_passed`
- `high_sitelink_count`
- `high_claim_count`
- `relation_family_not_allowed`
- `short_subject_label`
- `wikipedia_infobox_incomplete_tie_answer`
- `question_targets_mutable_fact`
- `_uses_generic_table_source_wording`

Do not add substitute gates. Effective surface/temporal guards, selected-table provenance, answer-in-evidence validation, DuckDuckGo filtering, and second-stage grading remain formal.

## Protected tools are not legacy

`scripts/run_openrouter_batch_predictions.py` and `scripts/judge_openrouter_batch_predictions.py` are retained independent SimpleQA Verified-style evaluation tools. They must not be deleted or grouped with historical generation/finalization code. Generation, manual review, and finalization do not call them.

## Pre-stabilization compatibility inventory

This file lists Route 3 settings and artifact fields that are retained only for compatibility with existing scripts, summaries, walkthroughs, or downstream review tooling. They should not be used for new Route 3 streaming or recipe runs, and can be removed during a future stable-version cleanup after dependent artifacts are migrated.

## Route 3 Non-Streaming `--record-limit`

- Location: `scripts/run_wikipedia_infobox_pipeline.py`.
- Current use: limits URL-list generation, validation-stage candidate loading, and non-streaming Route 3 summaries.
- Streaming status: not used by Route 3 page-ID streaming or recipe segment commands. Streaming uses `--stream-reuse-cached-page-count`, `--stream-fresh-cached-page-count`, and an internal `--stream-page-processing-target` supplied by recipes or explicit direct invocations.
- Removal path: replace non-streaming uses with a narrower URL/candidate limit name before deleting this flag.

## Summary Alias Fields

- `record_limit`: retained in Route 3 streaming and recipe summaries as a deprecated alias for older manifest and walkthrough readers.
- `record_limit_remaining_at_start`: retained in streaming summaries as a deprecated alias for `stream_page_processing_target_remaining_at_start`.
- `recipe_record_limit`: retained in recipe segment metadata as a deprecated alias for `recipe_target_count`.

New consumers should prefer the explicit target and budget fields: `stream_requested_main_page_count`, `stream_page_processing_target`, `stream_reuse_cached_page_count`, `stream_fresh_cached_page_count`, `recipe_target_count`, and `recipe_segment_expected_page_count`.
