# Branch 5-11-2 Notes

This note summarizes the main work carried out on branch `5-11-2` and explains how it differs from the older `5-11` branch.

## Branch role

`5-11` is treated as a historical snapshot.

`5-11-2` is the branch where the project direction changed from a template-centered Wikidata pipeline toward a more flexible **SimpleQA-style question generation** workflow with stronger emphasis on:

- natural question wording
- auditable long-tail filtering
- lighter-weight Wikidata retrieval
- incremental pilot-style experimentation

## Main changes discussed and implemented on 5-11-2

### 1. Test-first migration groundwork

Before broad refactoring, fixture-backed tests were added to lock current behavior for:

- artifact discovery
- template/status resolution
- workflow report generation

This created a safer baseline for later changes while keeping `5-11` frozen.

### 2. Small artifact-registry abstraction

A minimal artifact manifest/registry layer was introduced so active runtime logic no longer depends as directly on the old `5-11` output layout.

This was intentionally kept narrow:

- no broad module reorganization
- no output tree cleanup
- no destructive migration of historical artifacts

### 3. New strategic direction from research

The branch then moved into a research and source-review phase focused on:

- how to write natural SimpleQA-style questions
- Wikidata-based QA generation methods
- practical long-tail verification

The resulting direction on this branch is:

- prioritize SimpleQA-like style over preserving a Wikidata-template worldview
- use Wikidata when useful, but avoid getting blocked by WDQS
- prefer auditable search-based long-tail filtering
- keep the first pilot narrow and conservative

Research and live workflow notes were recorded in:

- [docs/research_discovery_memo.md](D:/Study/AI/My-research/Wikidata_Framework/docs/research_discovery_memo.md)
- [docs/reference.md](D:/Study/AI/My-research/Wikidata_Framework/docs/reference.md)
- [docs/current/README.md](D:/Study/AI/My-research/Wikidata_Framework/docs/current/README.md)

### 4. New staged generation foundation

The branch introduced a new multi-generator generation path with shared validation, rather than relying only on the old template execution loop.

Core ideas implemented here:

- shared generated-candidate contract
- shared validation path
- route-based generation
- two-stage long-tail filtering

The two-stage long-tail design is:

1. a cheap fact-level prefilter before rewrite
2. a stricter search-based verifier after rewrite

### 5. KELM half-pipeline

A KELM-backed half-pipeline was added as a concrete pilot path.

Current KELM behavior:

- seed from a small relation allowlist
- ground entities with `wbsearchentities` and `wbgetentities`
- rewrite questions with OpenRouter
- generate answer-blind search queries with the LLM
- verify long-tailness with DuckDuckGo

This path is documented in:

- [docs/current/kelm_half_pipeline.md](D:/Study/AI/My-research/Wikidata_Framework/docs/current/kelm_half_pipeline.md)
- [docs/current/kelm_pilot_walkthrough.md](D:/Study/AI/My-research/Wikidata_Framework/docs/current/kelm_pilot_walkthrough.md)

### 6. Network and retrieval hardening

The branch also hardened the online workflow:

- OpenRouter retries and proxy/direct fallback
- DuckDuckGo retries and proxy/direct fallback
- explicit handling for search verifier transport failures
- cached Wikidata text-to-entity mapping for repeated KELM grounding

### 7. Current pilot state

The latest 10-row KELM pilot remains conservative:

- generated: `10`
- accepted: `0`
- rejected: `10`

The failures are now informative rather than opaque, with clearer buckets such as:

- `unsupported_relation_record`
- `entity_grounding_failed`
- `search_longtail_verifier_rejected`

## Main difference between 5-11-2 and 5-11

The main difference is conceptual as much as technical.

### 5-11

`5-11` is centered on the older branch architecture:

- template-family management
- Stage 5 workflow orchestration
- review/status reporting around the template program
- stronger coupling to the historical output/reporting structure

### 5-11-2

`5-11-2` shifts the project toward a newer generation model:

- SimpleQA-style question quality is the primary target
- the pipeline is no longer template-led for KELM question writing
- search-based long-tail validation is a first-class component
- Wikidata retrieval favors `wbsearchentities` / `wbgetentities` over heavy WDQS dependence
- current work is organized around a small auditable pilot, not around expanding the old template catalog

In short:

`5-11` is the historical template-program branch.  
`5-11-2` is the transition branch toward a more flexible, search-aware, SimpleQA-style generator.

## Scope notes

- `docs/human_notes/` was left untouched.
- `outputs/` was not reorganized or deleted.
- Historical `5-11` artifacts were preserved rather than migrated away.
