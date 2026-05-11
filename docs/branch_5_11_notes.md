# Branch Notes: `main` vs `5-10` vs `5-11`

## Purpose

This note explains how the current code base differs from the GitHub `main` branch and from the earlier `5-10` branch.

This document also serves as a preservation note: branch `5-11` is intended to preserve the current code base and the current generated `outputs/` snapshot before a major project restructuring.

The short version is:

- `main` is the simpler baseline.
- `5-10` is the Stage 5B expansion branch with stronger validation, richer status tracking, multi-hop/date-answer support, and a much larger template program.
- `5-11` keeps the `5-10` Stage 5B architecture, but adds better protection against WDQS-driven status regression and introduces a template salvage / portfolio management layer so we can systematically rewrite templates before retiring them.

## Compared with `main`

Relative to `main`, the `5-10` and `5-11` line adds several major capabilities:

- a much larger template catalog, including Stage 5B blueprint coverage
- compositional multi-hop and date-answer template support
- stronger deterministic validation, including topic mismatch checks and duplicate subject-resource checks
- review-bundle rebuilding and canonical template-status indexing
- workflow automation for offline, live, rebuild, and report phases
- richer output artifacts for template review, run outcomes, and policy tracking

Operationally, `main` is closer to a simpler direct-harvest baseline. The Stage 5B branches accept more complexity in exchange for broader coverage, more auditing, and stronger rejection logic.

## Compared with `5-10`

`5-11` is not a reset or a new architecture. It is an operational hardening layer on top of `5-10`.

### 1. Less destructive handling of WDQS instability

`5-11` changes the live-harvest/status behavior so request-layer failures do not erase previously learned semantic information.

Key behavior changes:

- single-fact harvesting now prefers direct WDQS queries first and uses staged seed queries as a fallback
- staged subject-seed harvesting can return partial results instead of collapsing the whole template immediately
- lighter direct queries remove some WDQS-side label constraints and move more filtering back into local validation
- live runs can end as `no_result_with_request_errors` instead of only surfacing as opaque top-level errors
- status indexing can expose either `latest_live_status` or `best_known_semantic_status`

This means `5-11` is better than `5-10` at separating:

- semantic template quality
- operational WDQS reliability

### 2. Reliability metrics are now first-class

`5-11` adds repeated-run reliability summaries to template status artifacts.

Per-template reliability now includes:

- pass rate
- request failure rate
- candidate yield rate
- semantic reproducibility rate
- average request / retry / cache behavior

This lets us distinguish:

- templates that are semantically bad
- templates that are semantically fine but operationally flaky
- templates that are sparse because of scope, not because of outright failure

### 3. New salvage-board and portfolio management layer

The biggest new addition in `5-11` is the template-program management layer for the “rewrite before retire” workflow.

New artifacts and logic include:

- a machine-readable salvage registry in `config/template_salvage_registry.json`
- a generated salvage board for all non-proven templates
- inferred salvage potential and workstream assignment
- explicit rewrite-tracking fields such as:
  - `salvage_stage`
  - `salvage_attempt_count`
  - `last_rewrite_type`
  - `rewrite_hypothesis`
  - `rewrite_outcome`
  - `retirement_blocker`
- a recurring portfolio report summarizing promotion candidates, diversity contribution, and rewrite progress

This is the main branch-level difference in project management philosophy:

- `5-10` can tell us what failed
- `5-11` can tell us what to rewrite next and how to prioritize the path toward roughly 200 proven templates

### 4. Rebuild workflow now emits program-management artifacts

The Stage 5B rebuild flow now generates not only:

- template catalog review
- review bundle
- template status index

but also:

- template salvage board
- template portfolio report

That keeps operational planning inside the same artifact pipeline as the rest of the project.

## What `5-11` is for

Use `5-11` when the goal is to move beyond isolated template reruns and manage the catalog as a full program:

- keep Stage 5B precision constraints
- preserve semantic evidence during WDQS trouble
- measure template reliability explicitly
- prioritize salvageable templates before retirement
- add new templates in a controlled, diversity-aware way

In that sense, `5-11` is the branch for scaling the template program toward a larger final dataset, not just debugging individual templates.
