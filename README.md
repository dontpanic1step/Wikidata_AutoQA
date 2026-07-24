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

The automated flow does not remove candidates solely because they share a subject resource or exact question. Page-level deduplication is deferred until finalization after manual review.

## Durable runs, resume, and top-up

A non-dry formal run requires a clean Git worktree. Commit code and configuration changes before starting it. For a run that may cross midnight, set `--run-date` explicitly so the resolved fingerprint remains stable.

Run a bounded 10-page Person segment:

```powershell
python scripts\run_wikipedia_infobox_recipe.py `
  --page-attempt-count 10 `
  --answer-type Person `
  --route3-answer-type-mode single `
  --run-id route3_person_pilot `
  --run-date 2026-07-24
```

The segment artifacts are organized as follows:

```text
outputs/recipe_segments/<run-id>/
  01_person_10/
    segment_manifest.json
    page_attempts/
      p<canonical_page_id>_attempt001.json
  01_person_10_accepted.jsonl
  01_person_10_rejected.jsonl
  01_person_10_summary.json
  01_person_10_state.json
outputs/<run-id>_accepted.jsonl
outputs/<run-id>_rejected.jsonl
outputs/<run-id>_summary.json
outputs/<run-id>_walkthrough.md
```

The page-attempt ledger is authoritative. Stream state is a runtime cache, while accepted JSONL, rejected JSONL, and the segment summary are rebuilt from committed ledger files. Page archives are written atomically, and their SHA-256 hashes are stored in candidate provenance.

Resume an interrupted segment by running the exact same command with the same resolved arguments, Git commit, prompt code, run ID, seed, and run date. An incomplete matching segment resumes; a complete matching segment is reused without generation. Reusing the same segment with a different fingerprint fails and requires a new run or top-up segment.

Add a separate top-up segment without modifying the prior segment:

```powershell
python scripts\run_wikipedia_infobox_recipe.py `
  --page-attempt-count 10 `
  --answer-type Person `
  --route3-answer-type-mode single `
  --run-id route3_person_pilot `
  --run-date 2026-07-24 `
  --append-to-existing-run `
  --append-run-label topup_01
```

Inspect the durable-run tests with:

```powershell
python -m pytest tests\test_route3_run_ledger.py `
  tests\test_wikipedia_infobox_recipe.py `
  tests\test_wikipedia_infobox_generator.py -q
```

## Pre-review quantity prediction

After a segment finishes automated processing, its `segment_manifest.json` contains `pre_review_quantity_prediction` with:

- accepted candidate count;
- canonical unique-page and multi-QA-page counts;
- answer-type counts after choosing one candidate per page;
- the recorded recipe seed;
- rebalance `N`, projected per-type targets, and projected final total.

The prediction uses the formal canonical-page allocation and answer-type ratios. It does not select or delete topics; topic review starts in the later review milestones.

## Manual review loop

Install the project dependency before creating review workbooks:

```powershell
python -m pip install -e .
```

Export accepted candidates to durable review state, Markdown, and XLSX:

```powershell
python scripts\run_route3_review.py export `
  --accepted-input outputs\<run-id>_accepted.jsonl `
  --segment-manifest outputs\recipe_segments\<run-id>\<segment-id>\segment_manifest.json `
  --state-output outputs\reviews\<run-id>\review_state.json `
  --markdown-output outputs\reviews\<run-id>\review.md `
  --xlsx-output outputs\reviews\<run-id>\review.xlsx `
  --run-id <run-id>
```

Repeat `--segment-manifest` for every top-up segment represented in the accepted JSONL. The Markdown contains accepted candidates only, with stable ID, Q/A, answer type, Wikipedia page, selected table, and two-model answers.

The XLSX columns are exactly:

```text
id
question
reference_answer
wikipedia_url
topic
delete
edited_question
edited_reference_answer
edit_reason
```

`delete` defaults to `No` and has a `Yes/No` dropdown. `topic` has the formal ten-topic dropdown. Empty topics are allowed during review but are rejected by finalization.

After editing the workbook, apply it and produce the next review round:

```powershell
python scripts\run_route3_review.py apply `
  --state-input outputs\reviews\<run-id>\review_state.json `
  --xlsx-input outputs\reviews\<run-id>\review.xlsx `
  --state-output outputs\reviews\<run-id>\review_state.json `
  --markdown-output outputs\reviews\<run-id>\review.md `
  --xlsx-output outputs\reviews\<run-id>\review.xlsx `
  --run-id <run-id>
```

Deleted rows skip validation. Q/A edits preserve the stable ID and immutable generation provenance, append a revision, clear stale checks, and rerun the formal post-generation checks, DuckDuckGo filter, and two-model second stage. This apply command makes network calls only when the state contains Q/A edits or pending reruns. The next Markdown/XLSX contains only latest accepted revisions.

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
