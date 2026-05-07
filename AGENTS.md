# AGENTS.md

## Project goal

Build a conservative Wikidata-to-SimpleQA-Verified-style dataset generator.

## Non-negotiable rules

- Questions must not contain years, dates, month names, or temporal expressions.
- Gold answers must be time-invariant.
- Reject mutable statuses, current roles, relationships, affiliations, and cumulative statistics.
- Use Wikidata and deterministic validators for factuality, uniqueness, ambiguity, and time-invariance.
- Use LLMs only for one-shot question rewriting, never for fact invention or uniqueness judgment.
- Prefer high precision over high recall.
- All code comments and docstrings must be in English.
- Ask before installing dependencies or making network-heavy changes.

## Implementation style

- Start with a minimal runnable vertical slice.
- Add tests for validators before scaling.
- Keep outputs metadata-rich and auditable.