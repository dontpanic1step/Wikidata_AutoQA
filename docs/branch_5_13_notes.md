# Branch 5-13 Notes

This note summarizes the intended difference between branch `5-13` and `5-11-2`.

## What Changed From 5-11-2

- `5-11-2` moved the project away from a purely template-centered Wikidata pipeline toward flexible SimpleQA-style generation.
- `5-13` keeps that shared-pipeline worldview, but restores Route 1 as template-led because templates remain useful for conservative Wikidata candidate construction.
- `5-13` explicitly separates route-local validators from shared pipeline steps.
- `5-13` replaces the blanket temporal-expression ban with a cutoff-year policy: historical pre-2025 dates and years are allowed by default, while live-status and 2025+ dependent wording are rejected.
- `5-13` removes sitelink-count and claim-count thresholds as first-stage long-tail gates. Those fields remain useful metadata, but they should not decide long-tailness.

## Shared Pipeline Direction

The shared pipeline still has:

- multiple generators
- shared LLM rewriting
- shared long-tail filtering
- metadata-rich accepted and rejected records

The key architectural distinction is that route-specific harvesting and validation happen before candidates enter the shared rewrite and long-tail stages.

## Route 1 Direction

Route 1 is now the concrete Wikidata route:

- harvest Wikidata-backed facts
- build canonical questions from templates
- validate through a Wikidata-route bundle
- pass the canonical question plus Wikidata triplet text to the rewrite step
- run shared DuckDuckGo long-tail filtering and optional SimpleQA Verified-style model grading

Future non-Wikidata routes should not inherit Route 1 validators by default.

## Implementation Status After Incident Recovery

The incident removed untracked recovery files while preserving tracked integration changes. Phase 1 recreates the missing modules and tests needed for importability, Route 1 validation, OpenRouter-backed model calls, grading, and branch-specific docs.
