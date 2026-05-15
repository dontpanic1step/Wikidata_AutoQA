# Terminology

This project previously used a few names inconsistently. Use the canonical terms below in new code and docs.

## Canonical Terms

| Term | Meaning | Example |
|---|---|---|
| Template | A reusable question-generation pattern plus metadata. | The row for `benchmark_release_date` |
| Template key | The unique identifier for one template. | `benchmark_release_date` |
| Domain | The broad human-facing content area for a template. | `Architecture and Transportation` |
| Answer type | The expected answer category used by validators, grading, and reporting. | `Number`, `Date`, `Person` |
| Current status | The run/review-derived status used in reports. | `proven`, `frozen`, `unproven_no_result` |
| Legacy catalog bucket | The old catalog grouping field. | `active`, `blueprint`, `date_answer_pilot` |

## Legacy Mapping

| Legacy name | Canonical name | Notes |
|---|---|---|
| `DomainTemplate.domain` | `template_key` | Old code used `domain` for keys like `film_director`. New code should prefer `template.template_key`. |
| `DomainTemplate.topic` | `domain` | Old code used `topic` for broad categories like `Arts and Media`. New code should prefer `template.template_domain` or serialized `domain`. |
| `get_template_by_domain(...)` | `get_template_by_key(...)` | Kept as a compatibility alias for older scripts. |
| `FROZEN_TEMPLATE_DOMAINS` | `FROZEN_TEMPLATE_KEYS` | The frozen list contains template keys, not broad domains. |
| JSONL artifact field `domain` | `template_key` | Historical accepted/rejected/summary artifacts may still store template keys under `domain`; readers should accept both `template_key` and legacy `domain`. |
| `active` / `blueprint` | legacy catalog bucket | These labels came from the small-pilot era and should not drive current design decisions. |

## Naming Rule

New code should use `template_key` for identifiers and `domain` for broad content areas. If compatibility requires reading older artifacts, normalize legacy fields at the boundary rather than spreading old terminology into new modules.
