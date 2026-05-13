# KELM Half-Pipeline

This note describes the current `5-11-2` KELM half-pipeline as it exists now.

There is now only one active copy of this document:

- [docs/current/kelm_half_pipeline.md](D:/Study/AI/My-research/Wikidata_Framework/docs/current/kelm_half_pipeline.md)

The older duplicate at `docs/kelm_half_pipeline.md` is gone.

## Current status

The KELM path is now:

- KELM-seeded
- Wikidata-grounded through `wbsearchentities` and `wbgetentities`
- LLM-written for both:
  - the final question
  - the answer-blind search queries
- long-tail filtered by DuckDuckGo hit-rate checks

It is no longer template-led for question wording.
It also no longer carries KELM-only template-family or template-domain labels through rewrite and search.

The latest 10-record run finished successfully end to end:

- generated: `10`
- accepted: `0`
- rejected: `10`

This is now a policy result, not a crash result.

## End-to-end flow

1. Read up to `N` rows from [data/kelm/quadruples-train.tsv](D:/Study/AI/My-research/Wikidata_Framework/data/kelm/quadruples-train.tsv).
2. From each row, select the first triple whose relation is currently supported.
3. Ground the subject and answer with Wikidata API calls:
   - `wbsearchentities`
   - `wbgetentities`
4. Build a metadata-rich candidate with:
   - subject/answer entity data
   - KELM sentence
   - serialized triple
   - Wikidata sitelink count
   - Wikidata claim count
5. Run a cheap fact-level prefilter.
6. Send the serialized triple, KELM sentence, and answer to the LLM.
7. Ask the LLM to return:
   - `rewritten_question`
   - `search_queries`
   - `discard_reason`
8. Validate the rewritten question surface.
9. Query DuckDuckGo with:
   - the rewritten question
   - the LLM-generated answer-blind keyword queries
10. Compute search hit rates by category.
11. Reject or accept using configurable long-tail thresholds.
12. Run shared deterministic validation.
13. Write accepted and rejected JSONL outputs.

The orchestration is in [scripts/run_kelm_half_pipeline.py](D:/Study/AI/My-research/Wikidata_Framework/scripts/run_kelm_half_pipeline.py).

## KELM seeding

Current supported KELM relations:

- `date of birth`
- `date of death`
- `inception`
- `educated at`
- `narrator`
- `taxon rank`

This list is still active because it is not a template system. It is a temporary capability gate for the current KELM slice:

- each listed relation has an implemented grounding path
- each listed relation has an answer type the current validators can handle conservatively
- each listed relation is narrow enough for the current single-hop pilot

Rows without one of those relations are rejected as:

- `unsupported_relation_record`

Rows with a supported relation can still fail before rewrite if grounding does not resolve the subject or answer safely:

- `entity_grounding_failed`

## Wikidata grounding

The KELM route does not depend on WDQS.

It uses:

- `wbsearchentities` to find candidate IDs
- `wbgetentities` to hydrate labels, aliases, sitelinks, descriptions, and claims

Current subject matching is conservative:

1. normalize the KELM subject text
2. separate any parenthetical hint
3. search with `limit=5`
4. keep exact label matches only
5. if needed, use the parenthetical hint against the Wikidata description

If that conservative matching fails, the row is rejected.

### Cached text mapping

The current code now caches KELM text-to-Wikidata mappings in the Wikidata cache tree.

Purpose:

- avoid repeating the same `wbsearchentities` + `wbgetentities` resolution work
- keep KELM reruns fast when the same subject strings recur

This cache is handled by [src/wikidata_simpleqa/wikidata_client.py](D:/Study/AI/My-research/Wikidata_Framework/src/wikidata_simpleqa/wikidata_client.py) and used in [src/wikidata_simpleqa/kelm_generator.py](D:/Study/AI/My-research/Wikidata_Framework/src/wikidata_simpleqa/kelm_generator.py).

## Fact-level prefilter

This is the cheap first-stage long-tail filter.

Current inputs:

- subject sitelink count
- subject claim count
- subject label token count
- relation-family allowlist membership

Current default thresholds from [src/wikidata_simpleqa/config.py](D:/Study/AI/My-research/Wikidata_Framework/src/wikidata_simpleqa/config.py):

- `longtail_prefilter_max_sitelinks = 80`
- `longtail_prefilter_max_claims = 400`

This stage is high-recall and low-cost. It is not the main long-tail decision-maker.

## LLM rewrite step

The current KELM route does not start from a handcrafted question template.

Instead, the LLM gets:

- serialized triple
- KELM sentence
- answer
- forbidden text list
- cutoff year

and is asked to return JSON with:

```json
{
  "rewritten_question": "string",
  "search_queries": ["string"],
  "discard_reason": null
}
```

The prompt is implemented in [src/wikidata_simpleqa/llm_rewrite.py](D:/Study/AI/My-research/Wikidata_Framework/src/wikidata_simpleqa/llm_rewrite.py).

### Current rewrite policy

The LLM is told to:

- write a natural factual question
- preserve as much non-answer context as possible
- avoid leaking the answer
- avoid rigid templates
- avoid the answer and answer aliases in any casing, capitalization, or normalized variant
- generate `3-5` answer-blind keyword queries

## OpenRouter transport hardening

The original `URLError` problem is fixed.

What changed:

- OpenRouter requests now include:
  - `User-Agent`
  - `HTTP-Referer`
  - `X-OpenRouter-Title`
- the client retries failed requests
- if the SOCKS proxy path fails, the rewrite client falls back to a direct request

That fix lives in [src/wikidata_simpleqa/llm_rewrite.py](D:/Study/AI/My-research/Wikidata_Framework/src/wikidata_simpleqa/llm_rewrite.py).

## Search-based long-tail verification

This is now the main decision layer.

The search client is [src/wikidata_simpleqa/search_client.py](D:/Study/AI/My-research/Wikidata_Framework/src/wikidata_simpleqa/search_client.py).

It uses DuckDuckGo HTML search and records:

- queries
- titles
- snippets
- URLs
- answer-hit flags

### Current query set

For KELM candidates, the second-stage verifier now uses:

1. the rewritten question itself
2. the LLM-generated answer-blind keyword queries

It no longer falls back to fixed `subject + relation` or `subject + relation + answer` KELM probe queries.

### Current search depth

- `duckduckgo_top_k = 10`

So each query is evaluated on the top `10` results.

### Current hit-rate categories

The verifier computes:

- `full_question`
- `keyword_queries`
- `answer_probe`
- `overall`

For KELM, `answer_probe` is currently empty because the verifier now uses only the rewritten question plus LLM-generated keyword queries. The thresholds are applied to the question and keyword-query categories.

### Current thresholds

From [src/wikidata_simpleqa/config.py](D:/Study/AI/My-research/Wikidata_Framework/src/wikidata_simpleqa/config.py):

- `search_longtail_max_full_question_hit_rate = 0.0`
- `search_longtail_max_keyword_hit_rate = 0.1`
- `search_longtail_max_overall_hit_rate = 0.1`

### Practical meaning

At the moment, the filter is very strict:

- if answer leakage appears broadly in top results for the final question, reject
- if answer leakage appears too often in the keyword-query results, reject
- if the combined hit rate is too high, reject

## DuckDuckGo transport hardening

DuckDuckGo transport is also hardened now.

What changed:

- proxy-path retries
- direct fallback if the proxy path fails
- search errors no longer crash the whole batch
- if search still fails after retries, the candidate is rejected with:
  - `search_longtail_verifier_error`

This keeps the run stable even when the VPN/proxy path is unreliable.

## Current sample: rejected by search

### Sample 1: Shiels Jewellers

KELM input:

- serialized triple: `Shiels Jewellers inception 01 January 1945`
- sentence: `Shiels Jewellers is an Australian jewellery retailer and was founded by Jack Shiels in Adelaide in 1945.`
- answer: `1945`

LLM output:

- rewritten question:
  - `In which year was the Australian jewellery retailer Shiels Jewellers, founded by Jack Shiels in Adelaide, established?`
- keyword queries:
  - `Shiels Jewellers founding year`
  - `"Shiels Jewellers" establishment date Adelaide`
  - `Jack Shiels jewellery retailer foundation year`
  - `history of Shiels Jewellers in Australia`

Search result:

- `full_question` hit rate: `1.0`
- `keyword_queries` hit rate: `0.9`
- `overall` hit rate: `0.92`

Reason:

- top results expose `1945` immediately in snippets

Final outcome:

- `search_longtail_verifier_rejected`
- triggered rule:
  - `full_question:hit_rate_exceeded`

## Current sample: also rejected by search

### Sample 2: Peter Kelland

KELM input:

- serialized triple: `Peter Kelland educated at University of Cambridge`
- sentence: `After two years in the Marines Peter Kelland began his studies at the University of Cambridge.`
- answer: `University of Cambridge`

LLM output:

- rewritten question:
  - `Where did Peter Kelland begin his studies after serving two years in the Marines?`
- keyword queries included variants like:
  - `"Peter Kelland" education after Marines`
  - `Peter Kelland university studies post Marines`
  - `Peter Kelland academic background following military service`
  - `Peter Kelland studies after two years in Marines`

Search result:

- `full_question` hit rate: `1.0`
- `keyword_queries` hit rate: `0.5`
- `overall` hit rate: `0.6`

Reason:

- multiple snippets still expose `University of Cambridge`

Final outcome:

- `search_longtail_verifier_rejected`
- triggered rule:
  - `full_question:hit_rate_exceeded`

## Current sample: entity grounding early reject

### Sample 3: Mikhail Belyaev

This row is rejected before rewrite/search.

Reason:

- the row contains a supported relation, but conservative Wikidata grounding fails before rewrite

Final outcome:

- `entity_grounding_failed`

## Why the latest run has zero accepted

The current zero-accept result is consistent with the present policy:

- relation coverage is narrow
- grounding is conservative
- the second-stage long-tail thresholds are very strict
- KELM source sentences often leak the answer almost verbatim into search results

So the current bottleneck is not transport anymore. It is the strictness of the long-tail policy applied to these first 10 KELM rows.

## Current limitations

- only a small KELM relation subset is supported
- only the first supported triple per row is used
- answer-blind queries are better than before, but still often retrieve highly leaky pages
- the hit-rate thresholds are strict enough that many reasonable factual questions will fail
- KELM sentences often encode the answer in highly searchable phrasing

## Short summary

The current KELM half-pipeline is:

`KELM triple -> conservative Wikidata grounding -> cheap fact-level prefilter -> OpenRouter question+query generation -> DuckDuckGo hit-rate long-tail filtering -> deterministic validation -> reject or accept`

Right now it is stable, auditable, and strict, but not yet permissive enough to accept many KELM-derived questions.
