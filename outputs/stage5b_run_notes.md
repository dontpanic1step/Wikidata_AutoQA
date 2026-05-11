Stage 5B run date: 2026-05-06

Summary

- Accepted domains: 16
- Missing domains: 2
- Accepted output files:
  - `outputs/stage5b_pilot_accepted.jsonl`
  - `outputs/stage5b_pilot_rejected.jsonl`
  - `outputs/stage5b_pilot_summary.json`

What improved in this run

- Tier D date-answer questions now work with SimpleQA-Verified-style surfaces such as `On what day, month, and year ...`.
- The previous false rejection for hidden bridge entities with the same surface label as the subject no longer blocks `film_source_work_author`.
- Date-answer templates are now using exact-instance harvesting, which removed the earlier `product_release_date` timeout.
- The `ordinal_tournament_winner` seed query no longer times out after adding the edition type constraint.

Remaining problems to fix later

1. `person_first_degree_university` still times out at the WDQS seed-query stage.
   - Current issue: even the lighter seed query over `p:P69` + `pq:P582` is too expensive.
   - Likely next direction: move to a more selective statement pattern, probably requiring degree qualifiers or another narrow eligibility signal before local derivation.
   - Important constraint: keep the final selection deterministic and do not solve this by hand-picking specific people.

2. `ordinal_tournament_winner` now completes without timeout but returns no accepted or rejected candidates.
   - Current issue: the 2026 window plus the current `P179` / `P585` / `P1346` pattern may be too sparse or too strict.
   - Likely next direction: inspect whether recent tournament editions are using different dating properties or winner modeling, then generalize the ordinal harvester instead of custom-patching one series.

3. English-label availability is still a recurring rejection source.
   - Rejection examples in this run:
     - `video_game_developer`
     - `scholarly_article_journal`
     - `album_performer`
     - `benchmark_release_date`
   - Current issue: some recent items still have no usable English label in either `wbgetentities` or the WDQS fallback path.
   - Likely next direction: add a stricter "label-ready candidate" filter earlier in harvesting or enrich the fallback policy without silently accepting weak labels.

4. Same-name ambiguity is still correctly blocking some otherwise valid-looking candidates.
   - Rejection examples in this run:
     - `rail_station_country`: `Haga station`
     - `terminal_opening_date`: `Haga station`
   - Current issue: the current non-temporal disambiguation policy remains conservative when the subject name collides within the same medium.
   - Likely next direction: support additional non-temporal descriptors only when they are generalizable and do not leak the answer.

5. Location-answer leakage remains an active and useful rejection path.
   - Rejection example in this run:
     - `museum_country`: `Football Museum of Wales and Wrexham Museum`
   - Current issue: titles or location context can still reveal the answer country through subdivisions or constituent regions.
   - Keep this validator; it is doing useful work.

6. Metadata naming for date-answer validation is slightly misleading.
   - `validation_flags.no_year` and `validation_flags.no_temporal_expression` remain `true` for accepted date-answer questions because those checks are intentionally bypassed for Tier D.
   - Likely next direction: rename or split these flags so the output contract makes the exemption explicit.

WDQS / SPARQL-specific notes

- Adding early type constraints materially improved stability.
  - This was enough to make `ordinal_tournament_winner` complete instead of timing out.
- Exact-instance harvesting also materially improved stability for broad date-answer domains.
  - This was enough to make `product_release_date` succeed.
- The hardest remaining WDQS problem is still qualifier-heavy harvesting over human education statements.
  - The bottleneck is not downstream validation; it is candidate discovery itself.
