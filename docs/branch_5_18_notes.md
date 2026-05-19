# Branch 5-18 Notes

## Route 3 Streaming Wikipedia Page-ID Pipeline

- Added a streaming Route 3 mode that can process Wikipedia pages by page ID using URLs such as `https://en.wikipedia.org/w/index.php?curid=12345`.
- Added a persistent page-ID state file that tracks used IDs, in-progress IDs, accepted IDs, rejected IDs, table-search offsets, and a rerun pool for unresolved failures.
- Added incremental JSONL appending so accepted and rejected QA records are stored as each page reaches a final decision.
- Added endpoint resume support so a stopped run can continue from existing accepted/rejected output files instead of losing completed decisions.
- Added rerun-pool handling for pages that fail without a final accepted/rejected decision.

## Page Discovery

- Added table-search streaming as the default Route 3 page source using MediaWiki search for `insource:"wikitable"`.
- Kept the broader `insource:/\{\|/` search disabled by default because it is slower and noisier.
- Kept random page ID streaming available as an alternate source.
- Added small rerun-pool URL extraction output for preserving old unresolved page IDs without overwriting prior state.

## Route 3 Generation And Validation

- Updated Route 3 generation schema from `composition_type` to `reasoning_type`.
- Allowed `single_fact` questions when they are long-tail and stable.
- Kept the shared rewrite stage from receiving first-paragraph prose, while Route 3 generation still gets page/table context.
- Made domain/subdomain requirements optional for page-ID streaming to avoid false rejections.
- Added number-answer reference margin support in downstream grading.

## Network Reliability And Defaults

- Reduced MediaWiki retry count to 2.
- Added more robust MediaWiki request handling for transient TLS/connection failures.
- Turned REST summary fallback off by default.
- Recorded default settings in `docs/default_settings.md`.
- Changed the fast DuckDuckGo defaults to:
  - `--duckduckgo-top-k 5`
  - `--generated-search-query-count 2`
  - `--duckduckgo-parallel-queries 3`

## Walkthroughs And Auditability

- Added markdown walkthrough generation for streaming runs.
- Walkthroughs now include survival rate by layer, exact failure reasons, rerun-pool contents, phase timings, and timing nesting explanations.
- Fast40 walkthroughs show both fresh and incremental batches.
- Incremental walkthroughs include overall displayed stats across existing endpoint records and newly appended records.
- Second-stage filtering responses are displayed compactly by page ID, question, reference answer, and the GPT-4.1-mini/Gemini 3 Flash grade plus predicted answer.

## Final Selection

- Added a final-selection/deduplication path for scaling toward a larger accepted pool followed by similarity deduplication and domain rebalancing.

## Test Coverage

- Added tests for Wikipedia streaming state behavior.
- Added tests for endpoint resume, Route 3 defaults, REST summary fallback behavior, MediaWiki retry limits, second-stage grading display, and compact walkthrough rendering.
