# Wikidata Framework Route 3 Runbook

This repository is being stabilized milestone by milestone according to `docs/reconstruction/milestones.md`. This runbook documents only workflows that are already implemented on the current branch.

## Formal workflow boundary

- Route 3 is the only formal generation route.
- `scripts/run_wikipedia_infobox_recipe.py` is the only user-facing generation entry point.
- `scripts/run_wikipedia_infobox_pipeline.py` is an internal segment worker. Do not invoke it as a separate user workflow.
- Route 1, Route 2, Route 4, KELM, the old finalization flow, and `scripts/run_openrouter_night_batch.py` are historical and are not part of this runbook.
- `scripts/run_openrouter_batch_predictions.py` and `scripts/judge_openrouter_batch_predictions.py` are independent evaluation tools, not generation commands.

## Environment

- Python 3.11 or newer.
- Run commands from the repository root.
- Network generation reads the OpenRouter key from `OPENROUTER_API_KEY`.
- Do not place API keys in commands, config files, logs, or committed artifacts.

## Define one formal segment

Every formal recipe invocation defines one segment with three selectors:

| Flag | Meaning |
| --- | --- |
| `--page-attempt-count N` | Number of primary Wikipedia pages to attempt. |
| `--answer-type TYPE` | `Person`, `Place`, `Number`, `Date`, `Other`, or `AllTypes`. |
| `--route3-answer-type-mode MODE` | `single` or `all5`. |

Valid combinations:

| Answer type | Mode |
| --- | --- |
| `Person`, `Place`, `Number`, `Date`, or `Other` | `single` |
| `AllTypes` | `all5` |

Specific answer type plus `all5`, and `AllTypes` plus `single`, are rejected.

`--page-attempt-count` is a primary-page budget, not an accepted-question target. Automatic reruns do not consume additional primary-page budget.

The former free-form `--recipe`, `--answer-type-count`, `--answer-types`, and `--per-answer-type` inputs are not supported.

## Formal defaults

| Setting | Default |
| --- | --- |
| Generation model | `google/gemini-3-flash-preview` |
| Generation maximum tokens | `4096` |
| Reasoning type | `single_fact` |
| Second-stage grading | enabled |
| Second-stage threshold | `0.1` |
| Second-stage answer models | `openai/gpt-4.1-mini`, `google/gemini-3-flash-preview` |
| Second-stage grader | `openai/gpt-4.1-mini` |
| Cached-page reuse | `all` |
| Fresh-page budget | `fill` |
| Page source | `table-search` |
| Search query | `insource:"wikitable"` |

The formal worker uses these fixed method settings; they are not CLI options:

| Setting | Fixed value |
| --- | --- |
| Table discovery | MediaWiki table search only |
| Custom, broad, or random page discovery | unavailable |
| Table filters | `no_external_links_tables`, `no_horizontal_companion_tables`, `no_picture_heavy_tables`, `no_incomplete_tables`, `not_number_dominant`, `no_social_science_research` |
| Prose-leakage scoring | enabled |
| Minimum table score | `0.0` |
| LLM table choice | disabled |
| Pageview prefilter | disabled |
| REST first-paragraph fallback | disabled |
| Extra generation prompt | unavailable |
| KELM rewrite | unavailable |

The recipe passes the selected answer type, answer-type mode, and table source type to the internal worker. The worker does not accept URL lists or an old validation-stage candidate input. Use the recipe entry point for both dry runs and network runs.

The DuckDuckGo thresholds retain their existing formal values during reconstruction.

The formal candidate checks run in this order:

1. table and source checks;
2. generation, parsing, and normalization;
3. effective surface and temporal checks;
4. the integrated answer-type gate;
5. answer support in the selected table;
6. DuckDuckGo long-tail filtering;
7. second-stage grading.

The integrated answer-type gate retains Date and Place rules. Person candidates have no local rule-based rejection heuristic and still pass through source validation, DuckDuckGo filtering, and second-stage grading.

## Safe dry-run examples

Inspect a 10-page Person segment without making generation calls:

```powershell
python scripts\run_wikipedia_infobox_recipe.py `
  --page-attempt-count 10 `
  --answer-type Person `
  --route3-answer-type-mode single `
  --run-id route3_person_dry_run `
  --dry-run
```

Inspect a 10-page all5 segment:

```powershell
python scripts\run_wikipedia_infobox_recipe.py `
  --page-attempt-count 10 `
  --answer-type AllTypes `
  --route3-answer-type-mode all5 `
  --run-id route3_all5_dry_run `
  --dry-run
```

Use `python scripts\run_wikipedia_infobox_recipe.py --help` for the current formal argument list.

## Candidate artifact API

`src/wikidata_simpleqa/route3_artifacts.py` defines the stable candidate artifact schema:

- `Route3CandidateIdentity`
- `Route3CandidateProvenance`
- `Route3CandidateRevision`
- `Route3CandidateArtifact`
- `create_route3_candidate_artifact(...)`
- `revise_route3_candidate_artifact(...)`

Candidate IDs are derived only from run group ID, segment ID, canonical page ID, and original candidate slot. Question or answer edits append a revision and do not change the ID or immutable provenance.

Run the schema and ID tests with:

```powershell
python -m pytest tests\test_route3_artifacts.py tests\test_route3_ids.py -q
```

## Verification

Run the recipe interface tests:

```powershell
python -m pytest tests\test_wikipedia_infobox_recipe.py -q
```

Run the complete offline suite:

```powershell
python -m pytest -q
```

The runbook will be extended only when later milestone commands are implemented and tested.
