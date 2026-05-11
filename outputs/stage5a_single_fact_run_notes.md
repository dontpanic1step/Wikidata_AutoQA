# Stage 5A Single-Fact Run Notes

Run date: 2026-05-06
Command: `python scripts/generate_stage5_pilot.py`
Rewrite mode: disabled
Proxy: `socks5://127.0.0.1:7897`

## Outcome

- Active single-fact templates attempted: 12
- Accepted domains: 12
- Rejected candidates: 5
- Runtime: about 145 seconds for 12 template-specific runs

Accepted output:
- `outputs/stage5_pilot_accepted.jsonl`

Rejected output:
- `outputs/stage5_pilot_rejected.jsonl`

Summary:
- `outputs/stage5_pilot_summary.json`

## General Problems Observed

### 1. WDQS / SPARQL latency and retry pressure

Symptoms:
- The first full run timed out at 120 seconds.
- The successful run needed about 145 seconds.
- Some templates completed only after retry, for example `scholarly_article_journal` and `rail_station_country`.

Interpretation:
- The current one-template-at-a-time strategy works, but it is fragile against WDQS slowness.
- The current query pattern is simple, but repeated per-template runs still create a long wall-clock path.

General fixes to consider:
- Add persistent response caching for SPARQL by query hash.
- Add per-template checkpointing so a timed-out run can resume instead of restarting all templates.
- Separate transport failures from empty-result failures in summary metadata.
- Log request timing and retry counts per WDQS query.
- Consider smaller initial query limits plus progressive refill only when early rows are rejected.

### 2. Missing English labels from hydrated entities

Observed rejection reasons:
- `no_english_label`
- `no_answer_label`

Examples:
- `video_game_developer`: subject missing English label
- `video_game_developer`: answer missing English label
- `scholarly_article_journal`: subject missing English label
- `album_performer`: subject missing English label

Interpretation:
- WDQS returned usable candidate rows, but `wbgetentities` hydration did not yield a stable English label for the subject or answer.
- This is a data-quality and hydration-policy issue, not a question-template issue.

General fixes to consider:
- Distinguish between "no English label anywhere" and "English label missing only in hydration."
- Use WDQS `itemLabel` / `answerLabel` as a controlled fallback when the value is not QID-like and when it matches project label policy.
- Record whether the final accepted label came from hydration or WDQS service labels.
- Add a validator metric bucket for label-source reliability.

### 3. Ambiguity remains a real blocker for place-like subjects

Observed rejection reason:
- `same_label_competitor_requires_temporal_disambiguation`

Example:
- `rail_station_country`: `Haga station` collided with exact-name competitors.

Interpretation:
- Exact-name collision detection is doing its job.
- For infrastructure/place templates, same-name collisions are common and the current resolver is still conservative.

General fixes to consider:
- Expand non-temporal disambiguation rules for place/infrastructure templates using safe location descriptors.
- Add property-specific descriptor policies instead of relying only on subject type labels.
- Keep rejecting same-medium exact-name collisions when no non-temporal descriptor is available.

### 4. Aggregated pilot file currently reuses duplicate IDs

Observed issue:
- In `outputs/stage5_pilot_accepted.jsonl`, each accepted record currently has the same local ID pattern because each one-template run restarts numbering at `wikidata_verified_pilot_000001`.

Interpretation:
- This is not a data validity failure, but it is an output-contract bug.
- The per-template runner is aggregating accepted examples without reassigning globally unique IDs.

General fixes to consider:
- Reassign IDs after aggregation in `generate_stage5_pilot.py`.
- Or allow `run_pipeline_for_templates` to accept an `id_offset` or external ID allocator.

### 5. Current summary does not expose enough operational detail

Observed limitation:
- `stage5_pilot_summary.json` records accepted/rejected counts and retry-derived status strings, but it does not record request timing, exception type, or rejection breakdown by reason at the template level.

General fixes to consider:
- Add per-template timing.
- Add retry count and last exception type.
- Add rejection-reason histogram per template.
- Add a distinction between transport instability, empty harvests, and validator rejections.

## Rejection Breakdown From This Run

- `no_english_label`: 3
- `no_answer_label`: 1
- `same_label_competitor_requires_temporal_disambiguation`: 1

## Recommendations Before Stage 5A Scaling

1. Fix global ID assignment in the aggregated pilot writer.
2. Add WDQS timing / retry / exception logging.
3. Add controlled WDQS-label fallback for hydration gaps.
4. Improve place/infrastructure disambiguation with safe non-temporal descriptors.
5. Add resumable caching before larger multi-template or multi-hop runs.
