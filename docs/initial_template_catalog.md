# Template Catalog Strategy

## Purpose

This document defines the template strategy for scaling the framework toward a dataset around the size of SimpleQA Verified.

The core constraints remain unchanged:

- every accepted fact must be time-invariant,
- every harvested subject or event must be new enough, meaning its relevant date is not earlier than `target_time`,
- questions must not contain years, dates, month names, or temporal expressions,
- mutable roles, affiliations, relationships, and cumulative statistics remain out of scope unless the question is anchored to a settled event or a settled historical relation,
- the answer may be an entity, a number, or a date, as long as the answer itself is stable.

## Review-Driven Clarifications

The following rules are now explicit:

1. Architecture, transportation, and location templates are only valid when the harvested subject itself is new enough under `target_time`.
   Example:
   `which_country_airport_located` is valid only when the airport itself passes the recentness filter.

2. Number questions are allowed only when the number is historically fixed or tied to a one-time event or a settled object.

3. Cumulative or live numbers remain forbidden.
   Examples:
   - `How many goals has X scored?`
   - `How many children does X have?`
   - `How many employees does X have?`

4. Event-bound or fixed-structure numbers are allowed.
   Examples:
   - number of co-authors on a newly published paper,
   - age gap in a wedding event,
   - number of spans in a bridge,
   - number of founders in a founding event.

5. Ordinal wording is allowed when it does not introduce temporal ambiguity by itself.
   Examples:
   - `Who won the {ordinal} edition of Y?`
   - `Who was the {ordinal} president of X?`

6. A template that leaks the answer by construction should not remain in the catalog.
   Example:
   `who_theorem_named_after` has been removed.

7. A narrower template should not remain in the catalog when it is only a real semantic subset of a broader existing question family already present in our template catalog.
   Example:
   keep `how_many_authors_paper`, but do not add separate templates such as `how_many_authors_math_article` or `how_many_authors_biology_article`.

## Important Clarification

The "newness" requirement applies to the harvested subject or event, not necessarily to every supporting fact used in composition.

That makes additional template families possible:

- a recent wedding can support a stable question about the age gap between the spouses,
- a recent law can support a stable question about the legislature or jurisdiction,
- a recent religious succession event can support a stable question about who succeeded whom,
- a recent graduation-then-employment fact pattern can support a question about the university,
- a recent medicine, spacecraft, product, or engineering project can support stable relation questions,
- a recent benchmark, model, report, or product can support a `when` question when the answer is a stable date.

## Two Catalog Layers

The repository now distinguishes between:

1. `active` templates
   These are the templates currently safe enough to run in the prototype pipeline.

2. `blueprint` templates
   These are richer candidate templates that represent the intended path to roughly 1K questions and about 100 template families.

The blueprint catalog is not a promise that every template is already implementation-ready. It is the design target the next stages should grow into.

## Template Metadata

Each template now carries:

- `topic`
- `answer_type`
- `question_family`
- `answer_format`
- `date_answer_granularity`
- `composition_style`
- `status`

This makes the catalog suitable for balancing by:

- topic,
- answer type,
- surface form,
- date vs non-date answers,
- single-fact vs composed-fact questions.

## Date Answers Are Allowed

Date answers are allowed under this framework if:

- the question itself contains no temporal clue,
- the answer is historically fixed,
- the template specifies the intended answer granularity,
- the fact is harvested from a subject or event that is not earlier than `target_time`.

Examples of allowed answer granularity:

- year,
- month,
- full date.

Examples of acceptable question shapes:

- `On what date was the product {descriptor} released?`
- `In which year was the benchmark {descriptor} released?`

The prohibition is on temporal wording inside the question prompt beyond the neutral "when/on what date/in which year" form and on using time as disambiguation, not on date answers themselves.

## Number Answers Are Allowed

Number answers are allowed if they satisfy all of the following:

- they are not cumulative,
- they are not expected to drift over time,
- they come from a one-time event or a fixed released/completed object,
- they can be audited deterministically from Wikidata claims.

The blueprint now contains at least 20 number-related templates because a 1K-scale dataset should not rely entirely on entity answers.

## Ordinal Templates Are Allowed

Ordinal language such as `first`, `second`, or `tenth` is allowed when:

- it refers to an ordering that is itself stable,
- it does not require a year or date to disambiguate the subject,
- the underlying fact chain is deterministic and auditable.

In practice, ordinal templates should be modeled as dynamic families using an ordinal slot such as `{ordinal}`, not as hard-coded one-off questions like only `second` or only `tenth`.

## Composed Facts Are Allowed

Composed templates are allowed when all links in the chain are deterministic and auditable.

Examples:

- `From which university did {descriptor} graduate before working at Google?`
- `Who succeeded {descriptor}?`
- `What was the age gap between the couple in {descriptor}?`

These require careful validator support, but they are in-scope for the blueprint.

## Active Catalog

The current active catalog remains conservative and is still the runtime source for the prototype generator.

It contains a small subset of safe templates spanning multiple topics and non-`Who` surface forms.

## Blueprint Coverage

The blueprint catalog now spans all of these topic areas:

- People
- Geography
- Politics and Law
- Economy and Business
- Society and Culture
- Philosophy and Religion
- Language and Literature
- Arts and Media
- Sports and Recreation
- Education
- Mathematics
- Physical Sciences
- Life Sciences
- Medicine and Health
- Earth, Environment, and Space
- Computer Science and AI
- Engineering and Technology
- Architecture and Transportation
- Food, Agriculture, and Daily Life

The blueprint is intentionally broad because a 1K-scale dataset should not depend on a handful of media templates.

## Expected Scale

The intended scaling direction is:

- about 100 template families,
- around 1K final questions as a flexible default target,
- multiple answer types,
- meaningful topic balance,
- a substantial fraction of non-`Who` question families.

## Remaining Implementation Gap

The current runtime can already support the metadata shape of this broader catalog, but it does not yet implement:

- full per-template query logic for all blueprint families,
- robust composed-fact harvesting,
- date-answer grading,
- quota control across the enlarged catalog,
- property-specific validators for every blueprint family.

That gap is expected. The blueprint exists to guide Stage 5 and later implementation, not to pretend the current pipeline can safely execute all 100 families today.
