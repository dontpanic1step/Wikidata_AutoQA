# Compatibility Legacy Settings

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
