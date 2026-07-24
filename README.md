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

Use `python scripts\run_wikipedia_infobox_recipe.py --help` for the current argument list. Options scheduled for removal by later reconstruction milestones are not endorsed merely because they still appear before that milestone is committed.

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
