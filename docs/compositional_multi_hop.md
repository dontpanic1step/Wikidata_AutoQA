# Compositional Multi-Hop Provenance

## Purpose

This document defines the preferred terminology and runtime contract for questions that require deterministic reasoning over more than one Wikidata hop.

The project target does not change:

- short SimpleQA-style questions,
- a single stable answer,
- no supporting paragraph bundle in the main dataset,
- deterministic Wikidata-backed factuality and validation.

What changes is the internal and output representation for these examples. We treat them as **compositional multi-hop provenance** examples rather than generic "composed facts."

## Terminology

Use these labels in code and docs:

- `single_fact`: direct subject-property lookup
- `multi_hop_join`: deterministic join across two or more linked claims or items
- `multi_hop_ordinal`: deterministic ordering or edition-based reasoning over linked items
- `multi_hop_aggregate`: deterministic structural aggregation; disabled by default until number-policy validation is stronger

`fact_join` and `ordinal_fact` remain accepted as legacy input labels, but the runtime normalizes them to the reasoning styles above.

## Required Metadata

Every accepted compositional multi-hop candidate must include:

- `reasoning_style`
- `hop_count`
- `reasoning_path`
- `bridge_entities`
- `derivation_signature`
- `shortcut_checks`
- `provenance_complete`
- `question_requires_all_hops`

The final question should remain short and context-free, but the metadata must make the reasoning path auditable.

## Validation Rules

Multi-hop examples must pass all of the standard project rules plus these additional checks:

1. The reasoning path is connected.
2. The surfaced question requires all hops.
3. The derivation is unique at the full reasoning level, not only per local property.
4. No hop requires a temporal clue for disambiguation.
5. Bridge wording must not leak the answer or expose latent bridge entities unless the template explicitly allows it.
6. Ordinal examples must include explicit ordinal derivation metadata and a safe series descriptor.

## Activation Policy

- Active runtime templates should remain mostly single-fact by default.
- Multi-hop templates should use a separate pilot activation path.
- Count-based multi-hop templates stay disabled until aggregate-stability validators are implemented.
