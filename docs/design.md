# Wikidata-to-SimpleQA-Verified-Style Dataset Generator

## 0. Purpose

Build an open-source framework that generates **SimpleQA Verified-style short factual questions** from Wikidata.

The framework should:

1. Use a configurable target year, e.g. `TARGET_YEAR = 2026`.
2. Prefer entities or facts whose relevant event/release/publication/inception date is on or after `TARGET_YEAR-01-01`.
3. Generate questions that have **exactly one unique answer**.
4. Ensure every gold answer is **time-invariant**: once the relevant entity/event exists, the answer should not change over time.
5. **Absolutely forbid years, dates, and temporal expressions in the question text**, including explicit years like `2026` and vague temporal phrases like `this year`, `recently`, `current`, `latest`, or `as of`.
6. Use Wikidata APIs and deterministic rules as much as possible.
7. Use an LLM only once per candidate, ideally only to rewrite a verified canonical template into a natural short question.
8. Include an automatic grading/evaluation system inspired by SimpleQA / SimpleQA Verified scoring.
9. Generate a first pilot batch of **20 total questions across multiple domains** for manual review.
10. Use English comments in all source code because the project may be open-sourced.
11. Support multiple LLM providers: OpenAI, Anthropic, OpenRouter, and possibly other OpenAI-compatible APIs.
12. Support a SOCKS proxy such as:

```python
PROXY = "socks5://127.0.0.1:7897"
```

This project is not intended to let an LLM invent facts. The LLM is only a surface-form rewriting module. Wikidata and deterministic validators must own factuality, time-invariance, uniqueness, and ambiguity checks. A separate automatic grader evaluates model predictions after dataset generation.

---

## 1. Design Inspiration

This framework is inspired by SimpleQA and SimpleQA Verified.

SimpleQA focuses on short, fact-seeking questions with a single, indisputable answer. SimpleQA Verified further emphasizes reliability by addressing noisy labels, topic bias, question redundancy, multi-stage filtering, de-duplication, topic balancing, and source reconciliation.

This framework should follow the same spirit:

- Short fact-seeking questions.
- A single, stable answer.
- Easy grading.
- No hidden temporal assumptions in the question.
- Strong deterministic filtering before any LLM call.
- Metadata-rich examples so that each question can be audited and regenerated.

---

## 2. Non-Negotiable Requirements

### 2.1 No Temporal Clues in Questions

The final question text must not contain:

- Any year: `\b(17|18|19|20|21)\d{2}\b`
- Full or partial dates.
- Month names.
- Temporal phrases, including but not limited to:
  - `this year`
  - `last year`
  - `next year`
  - `recent`
  - `recently`
  - `current`
  - `currently`
  - `latest`
  - `newest`
  - `former`
  - `previous`
  - `as of`
  - `in the year`
  - `released in`
  - `published in`
  - `opened in`
  - `founded in`
  - `established in`

Important nuance:

- If an official entity label itself contains a year, the first implementation should reject it.
- Later versions may add a config flag such as `ALLOW_YEAR_IN_OFFICIAL_TITLE = False`, but the default must be strict.

### 2.2 Target-Year Filter Comes Early

The target year is not used for question wording. It is used only for candidate harvesting.

The framework should prioritize:

```python
TARGET_YEAR = 2026
TARGET_START_DATE = "2026-01-01T00:00:00Z"

# Default: avoid future scheduled/planned facts.
# This value can be set to the pipeline run date.
DATE_UPPER_BOUND = "RUN_DATE"
```

Candidate facts should be harvested only if the relevant date property satisfies:

```text
TARGET_START_DATE <= date_value <= DATE_UPPER_BOUND
```

This upper bound is important. The dataset should prefer facts that have already happened, been published, been released, or otherwise become settled. Do **not** include future scheduled releases, planned events, announced appointments, or unreleased works by default.

Examples of relevant date properties:

| Domain | Preferred date property |
|---|---|
| Film / TV / media works | `P577` publication date |
| Books / written works | `P577` publication date |
| Video games | `P577` publication date |
| Scholarly articles | `P577` publication date |
| Organizations / companies | `P571` inception |
| Buildings / infrastructure | `P571` inception or completion-related properties if available |
| Sports/events | `P585` point in time, `P580` start time |
| Awards/ceremonies | `P585` point in time |
| Artworks | `P571` inception, when available |

This date filtering must happen before LLM rewriting and before expensive ambiguity checks.

### 2.3 No Time-Based Disambiguation

If an entity requires a year/date to distinguish it from another same-name entity, reject it.

Example:

- `Project Hail Mary` has both a novel and a film.
- The question must not say `the 2026 film`.
- The candidate can only be accepted if it can be uniquely identified by a non-temporal descriptor such as:
  - `the film adaptation of Andy Weir's novel Project Hail Mary`
  - `the science-fiction novel Project Hail Mary`

If the only reliable disambiguator is a year, date, or phrase like `the latest`, reject the candidate.

### 2.4 Time-Invariant Gold Answers

Gold answers should be stable in the SimpleQA / SimpleQA Verified sense: the answer should not change over time.

Important interpretation:

- A question is acceptable when it asks about an intrinsic, historical, or settled attribution of an entity/event/work.
- A question is not acceptable when it asks about a mutable status, a current relationship, an office/job, a cumulative statistic, or a value that can naturally change over a person's life/career or an organization's operation.
- Do **not** accept a mutable fact merely because it is unlikely to change soon. For example, even if a footballer is very unlikely to retire in the target year, their career goal count is still mutable and should be rejected.
- Historically settled slices of otherwise mutable properties may still be accepted when deterministic provenance proves that the slice is fixed.
  - Example: a person's `first spouse` can be acceptable if the ordinal spouse sequence is derived from dated spouse statements and the historical slot is settled.
  - Example: goals scored in one completed tournament edition can be acceptable if the total is tied to that finished edition rather than to a live or career total.
  - Example: an ordinal office/role answer can be acceptable only when the executor reconstructs a complete dated historical sequence rather than asking for a current office holder.

Acceptable examples:

- The author of a published novel.
- The director of a released film, if the film is already released and the director credit is settled.
- The developer of a released video game.
- The journal in which a published article appeared.
- The architect of a completed building.
- The creator of an artwork.
- The winner of a completed, specifically named event, if the event name itself does not contain a forbidden year/date and does not require temporal disambiguation.
- The country where a fixed geographic place is located, unless the place is politically disputed or the answer is time-dependent.

Reject examples:

- A person's current wife/husband/spouse/partner. Relationships can change through divorce, death, remarriage, etc.
- A person's current employer, club, team, job title, office, or affiliation.
- Current CEO.
- Current president, mayor, minister, or office holder.
- Current population.
- Current number of employees.
- Career totals, such as how many goals Erling Haaland has scored in his career.
- Any cumulative live statistic: goals, appearances, citations, followers, box-office revenue, sales, downloads, wins, losses, medals, publications, or net worth.
- Latest winner.
- Most recent album.
- Upcoming film director if the film is not yet released.
- Planned event venue if the event has not happened.
- Any fact that requires `current`, `currently`, `latest`, `most recent`, `career total`, `as of`, or a date to be true.

Implementation rule:

```text
If the answer might differ depending on when the question is asked, reject the candidate.
If the value is a mutable status, relationship, affiliation, office, or cumulative statistic, reject it even when it looks stable in the short run, unless the candidate explicitly proves a historically settled slice with deterministic provenance.
```

Recommended metadata:

```json
{
  "time_invariance": {
    "status": "passed",
    "reason": "settled_historical_attribution",
    "date_upper_bound": "RUN_DATE",
    "reject_if_future_dated": true,
    "reject_mutable_status": true,
    "reject_cumulative_statistics": true
  }
}
```

For the first version, enforce a conservative rule:

```python
REJECT_FUTURE_DATED_CANDIDATES = True
REJECT_CURRENT_OR_LATEST_FACTS = True
REJECT_MUTABLE_RELATIONSHIPS = True
REJECT_MUTABLE_AFFILIATIONS = True
REJECT_CUMULATIVE_STATISTICS = True
REJECT_UNRELEASED_WORKS = True
```

### 2.5 Pilot Output Requirement

The initial implementation should generate:

```python
PILOT_TOTAL = 20
```

These 20 examples should be distributed across multiple domains, not concentrated in films or entertainment.

They are **pilot candidates**, not final verified examples. The pilot output should include full metadata for manual inspection.

### 2.6 English Code Comments

All source code comments and docstrings must be in English.

Good:

```python
# Reject candidates whose question would require temporal disambiguation.
```

Bad:

```python
# 如果问题需要年份消歧，就丢弃
```

---

## 3. High-Level Pipeline

```text
Domain-property template library
  ↓
Wikidata candidate harvesting with TARGET_YEAR and DATE_UPPER_BOUND filters
  ↓
Time-invariance and settled-fact check
  ↓
Answer uniqueness check
  ↓
Subject label/alias ambiguity search
  ↓
Non-temporal disambiguation signature search
  ↓
Canonical question construction
  ↓
One LLM rewrite call
  ↓
Post-rewrite deterministic validation
  ↓
Deduplication and topic balancing
  ↓
Pilot output: 20 metadata-rich examples
  ↓
Automatic evaluation / grading system for model predictions
```

Critical rule:

> Do not ask the LLM whether the answer is unique. Do not ask the LLM to find the answer. Do not ask the LLM to decide whether a candidate is ambiguous. Use Wikidata and deterministic code for those tasks.

---

## 4. Wikidata Access Strategy

Use a hybrid Wikidata access strategy.

### 4.1 WDQS / SPARQL for Candidate Harvesting

Use the Wikidata Query Service for structured batch retrieval.

Use it for:

- Finding items in a domain.
- Applying date thresholds.
- Checking candidate `(subject, property, answer)` triples.
- Getting labels.
- Getting answer counts.

Endpoint examples:

```text
https://query.wikidata.org/sparql
https://query.wikidata.org/bigdata/namespace/wdq/sparql
```

Use a meaningful User-Agent header.

### 4.2 Wikibase API: `wbgetentities`

Use the Wikibase API to hydrate specific entities.

Endpoint:

```text
https://www.wikidata.org/w/api.php
```

Typical parameters:

```text
action=wbgetentities
ids=Q...
props=labels|aliases|descriptions|claims|sitelinks
languages=en
format=json
```

Use it for:

- Labels.
- Aliases.
- Descriptions.
- Claims.
- Sitelinks.
- Full statement inspection.
- Competitor entity hydration.

### 4.3 Wikibase API: `wbsearchentities`

Use `wbsearchentities` to find possible same-name or near-name competitors.

Typical parameters:

```text
action=wbsearchentities
search=Project Hail Mary
language=en
type=item
limit=50
format=json
```

Use it for:

- Label collision detection.
- Alias collision detection.
- Candidate subject ambiguity checks.
- Finding same-title items across domains.

Important:

`wbsearchentities` should only construct a competitor set. It is not a final source of truth. Hydrate returned QIDs with `wbgetentities` and inspect claims.

### 4.4 Avoid WDQS Regex Search for Names

Do not use expensive `FILTER(REGEX(...))` on labels for fuzzy search. Use `wbsearchentities` for search-like tasks.

---

## 5. Core Data Model

Use a metadata-rich object for each candidate.

```python
from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class CandidateFact:
    subject_qid: str
    subject_label: str
    subject_aliases: list[str]

    domain: str
    subject_type_qids: list[str]

    target_property_pid: str
    target_property_label: str

    answer_qids: list[str]
    answer_labels: list[str]
    answer_aliases: list[str]

    date_property_pid: str
    date_value: str
    target_year: int

    canonical_question: str
    rewritten_question: Optional[str] = None

    ambiguity_status: str = "unknown"
    disambiguation_signature: list[str] = field(default_factory=list)
    competitor_qids: list[str] = field(default_factory=list)

    validation_flags: dict[str, Any] = field(default_factory=dict)

    source_metadata: dict[str, Any] = field(default_factory=dict)
```

Final JSONL output should include at least:

```json
{
  "id": "wikidata_verified_pilot_000001",
  "question": "Who directed the film adaptation of Andy Weir's novel Project Hail Mary?",
  "answer": "Phil Lord and Christopher Miller",
  "answer_aliases": [],
  "subject_qid": "Q...",
  "answer_qids": ["Q...", "Q..."],
  "property_pid": "P57",
  "domain": "film",
  "target_year": 2026,
  "date_filter": {
    "property": "P577",
    "value": "2026-..."
  },
  "ambiguity_status": "resolved_by_non_temporal_descriptor",
  "disambiguation_signature": [
    "film adaptation",
    "based on Andy Weir's novel"
  ],
  "competitor_qids": ["Q...", "Q..."],
  "canonical_question": "...",
  "rewritten_question": "...",
  "validation_flags": {
    "no_year": true,
    "no_temporal_expression": true,
    "answer_unique": true,
    "subject_unique_under_question": true,
    "answer_not_leaked": true
  },
  "source_metadata": {
    "wikidata_access_date": "YYYY-MM-DD",
    "retrieval_method": "WDQS + wbgetentities + wbsearchentities"
  }
}
```

---

## 6. Domain-Property Template Library

Implement a config-driven template library. Do not hard-code everything in procedural logic.

### 6.1 Key Wikidata Properties

Common properties:

| PID | Meaning |
|---|---|
| `P31` | instance of |
| `P279` | subclass of |
| `P577` | publication date |
| `P571` | inception |
| `P585` | point in time |
| `P580` | start time |
| `P582` | end time |
| `P50` | author |
| `P57` | director |
| `P58` | screenwriter |
| `P178` | developer |
| `P123` | publisher |
| `P175` | performer |
| `P1433` | published in |
| `P170` | creator |
| `P84` | architect |
| `P112` | founded by |
| `P17` | country |
| `P131` | located in administrative territorial entity |
| `P144` | based on |
| `P179` | part of the series |
| `P136` | genre |
| `P495` | country of origin |
| `P407` | language of work or name |
| `P361` | part of |

### 6.2 Initial Domain Coverage

For the first pilot, aim for 20 total examples across at least 5 domains.

Recommended domains:

| Domain | Entity type | Date property | Target property | Template |
|---|---|---|---|---|
| Film | film | `P577` | director `P57` | `Who directed the film {subject_descriptor}?` |
| Books / literature | novel/book | `P577` | author `P50` | `Who wrote the novel {subject_descriptor}?` |
| Video games | video game | `P577` | developer `P178` | `Which company developed the video game {subject_descriptor}?` |
| Scholarly articles | scholarly article | `P577` | published in `P1433` | `In which journal was the article {subject_descriptor} published?` |
| Artworks | artwork | `P571` or `P577` | creator `P170` | `Who created the artwork {subject_descriptor}?` |
| Buildings / architecture | building | `P571` | architect `P84` | `Who designed the building {subject_descriptor}?` |
| Organizations | organization/company | `P571` | founded by `P112` | `Who founded {subject_descriptor}?` |
| Places | place/infrastructure | `P571` | country `P17` or admin entity `P131` | `In which country is {subject_descriptor} located?` |
| Music albums | album | `P577` | performer `P175` | `Which artist released the album {subject_descriptor}?` |
| Awards/prizes | prize/category | `P571` | conferred by / part of | Use cautiously |

Start with high-precision domains:

1. Films: director.
2. Books/novels: author.
3. Video games: developer.
4. Scholarly articles: journal.
5. Artworks/buildings: creator/architect.
6. Organizations/places: founder/country.

Avoid in the first version:

- Songs.
- Cast members.
- Producers.
- Current office holders.
- Current CEOs.
- Population.
- Number of employees.
- Sports season winners if the official label requires a year.
- Any fact whose question naturally requires `current`, `latest`, or `as of`.
- Narrower template variants whose answer set is a real semantic subset of a broader existing question family already present in our template catalog.

Template-generation rule:

- If template `B` only adds a topic adjective or surface specialization to template `A`, and `A` is already an existing question family in our template catalog, but every valid `B` question is still just an instance of `A`, do not keep both templates.
- Keep the broader template and delete the narrower one from the catalog instead of relying on runtime deduplication.
- Example: keep `how_many_authors_paper`, and do not create parallel templates like `how_many_authors_math_article` or `how_many_authors_biology_article`.

---

## 7. Candidate Harvesting

### 7.1 Example SPARQL: Film Director Candidates

```sparql
SELECT ?item ?itemLabel ?answer ?answerLabel ?date WHERE {
  ?item wdt:P31/wdt:P279* wd:Q11424;   # film
        wdt:P577 ?date;
        wdt:P57 ?answer.               # director

  FILTER(?date >= "2026-01-01T00:00:00Z"^^xsd:dateTime)

  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en".
  }
}
LIMIT 1000
```

### 7.2 Example SPARQL: Unique Answer Check

```sparql
SELECT ?item ?itemLabel (COUNT(DISTINCT ?answer) AS ?n_answers) WHERE {
  ?item wdt:P31/wdt:P279* wd:Q11424;
        wdt:P577 ?date;
        wdt:P57 ?answer.

  FILTER(?date >= "2026-01-01T00:00:00Z"^^xsd:dateTime)

  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en".
  }
}
GROUP BY ?item ?itemLabel
HAVING(COUNT(DISTINCT ?answer) = 1)
LIMIT 1000
```

### 7.3 Candidate Harvesting Rules

For each domain-property pair:

1. Query candidates with the target-year filter.
2. Require exactly one best-rank/truthy answer for the target property.
3. Hydrate the subject and answer entities.
4. Reject candidates without English labels.
5. Reject candidates whose subject label contains a year or date.
6. Reject candidates whose official label requires parenthetical temporal disambiguation.
7. Reject candidates with insufficient metadata, unless the domain is intentionally long-tail.

---

## 8. Answer Uniqueness

A candidate must satisfy:

```text
COUNT(DISTINCT answer) == 1
```

But this is not enough.

Also check:

1. No conflicting non-deprecated full statements.
2. No multiple normal-rank values that are hidden by truthy `wdt:` simplification.
3. No temporal qualifiers that are necessary to identify the answer.
4. No target property from the high-risk list unless explicitly whitelisted.

High-risk target properties:

- Cast member.
- Producer.
- Award received.
- Occupation.
- Genre.
- Platform.
- Member of sports team.
- Population.
- CEO/head of government/current office holder.
- Number of employees.
- Spouse / partner / unmarried partner.
- Employer / affiliation / member of political party.
- Sports statistics, career totals, goals, appearances, points, wins, losses, rankings.
- Citation counts, follower counts, sales counts, box-office totals, downloads, revenue, net worth.

Default rule:

```text
Reject mutable status properties and cumulative-statistic properties, even if the value is unlikely to change soon.
```

---

## 9. Subject Ambiguity and Competitor Search

The candidate subject must be uniquely identifiable from the final question without a date.

### 9.1 Name Normalization

Implement a strict normalization function.

```python
import re
import unicodedata

def normalize_name(text: str) -> str:
    """Normalize labels and aliases for collision detection."""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()

    # Remove parenthetical disambiguators, e.g. "Title (film)".
    text = re.sub(r"\([^)]*\)", "", text)

    # Remove punctuation and collapse spaces.
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
```

### 9.2 Competitor Set

For each subject:

1. Search by English label.
2. Search by important aliases.
3. Hydrate returned QIDs with `wbgetentities`.
4. Include competitors whose normalized label or aliases match the subject.
5. Include same-domain competitors even when the exact normalized label differs slightly.
6. Store the competitor QIDs in metadata.

Pseudo-code:

```python
def build_competitor_set(subject_entity, wikidata_client, search_limit=50):
    """Find possible entities that could be confused with the subject."""
    names = [subject_entity.label] + subject_entity.aliases
    qids = set()

    for name in names:
        if not name:
            continue
        results = wikidata_client.search_entities(name, limit=search_limit)
        qids.update(result.qid for result in results)

    entities = wikidata_client.get_entities(sorted(qids))

    subject_names = {normalize_name(subject_entity.label)}
    subject_names |= {normalize_name(a) for a in subject_entity.aliases}

    competitors = []
    for entity in entities:
        candidate_names = {normalize_name(entity.label)}
        candidate_names |= {normalize_name(a) for a in entity.aliases}

        if entity.qid == subject_entity.qid:
            continue

        if subject_names & candidate_names:
            competitors.append(entity)

    return competitors
```

---

## 10. Non-Temporal Disambiguation Signature

If the subject label is not unique, find a non-temporal descriptor set that uniquely identifies the subject among competitors.

### 10.1 Allowed Descriptor Types

Allowed descriptors:

1. Medium/type:
   - film
   - novel
   - video game
   - album
   - scholarly article
   - artwork
   - building
   - organization

2. Subtype/genre:
   - animated film
   - documentary film
   - science-fiction novel
   - role-playing video game

3. Source/adaptation relation:
   - based on X
   - adaptation of X
   - based on the novel by Y

4. Series/franchise:
   - part of X series
   - part of X franchise

5. Stable context:
   - country
   - original language
   - publisher
   - developer
   - journal
   - collection
   - located in

### 10.2 Forbidden Descriptor Types

Forbidden descriptors:

- Publication date.
- Release date.
- Inception date.
- Point in time.
- Start time.
- End time.
- Current/latest/recent/former.
- Ordinals if used chronologically.
- Any descriptor that leaks the answer.

Example:

If the target property is `P57` director, do not use the director as a descriptor.

If the target property is `P175` performer, do not use the performer as a descriptor.

### 10.3 Signature Search

Pseudo-code:

```python
from itertools import combinations

def find_non_temporal_signature(target, competitors, descriptors, max_size=3):
    """Find the smallest non-temporal descriptor set that uniquely identifies the target."""
    clean_descriptors = [
        d for d in descriptors
        if not d.is_temporal
        and not d.leaks_answer
        and d.is_stable
    ]

    for k in range(1, max_size + 1):
        for combo in combinations(clean_descriptors, k):
            if uniquely_identifies_target(target, competitors, combo):
                return list(combo)

    return None
```

Where:

```python
def uniquely_identifies_target(target, competitors, descriptor_combo):
    """Return True if only the target entity satisfies the descriptor combination."""
    if not entity_satisfies_all(target, descriptor_combo):
        return False

    for competitor in competitors:
        if entity_satisfies_all(competitor, descriptor_combo):
            return False

    return True
```

### 10.4 Rejection Rule

Reject if:

```text
subject has same-label or alias competitors
AND no non-temporal descriptor signature exists
```

This is especially important for:

- Same-title films from different years.
- Works with film/book/song/album variants.
- Sports seasons.
- Award ceremonies.
- Entities whose common disambiguator is a year.

---

## 11. Canonical Question Construction

The canonical question is deterministic.

Examples:

```text
Who directed the film {descriptor}?
Who wrote the novel {descriptor}?
Which company developed the video game {descriptor}?
In which journal was the article {descriptor} published?
Who created the artwork {descriptor}?
Who designed the building {descriptor}?
Who founded {descriptor}?
```

The `{descriptor}` can be:

1. Just the subject label if label-unique.
2. A non-temporal disambiguated phrase if label-ambiguous.

Examples:

```text
Project Hail Mary
the film adaptation of Andy Weir's novel Project Hail Mary
the science-fiction novel Project Hail Mary
the video game in the Final Fantasy series titled X
the album X by the band Y
```

Be careful with answer leakage:

- If the question asks for the performer, do not say `the album X by Y`.
- If the question asks for the developer, do not say `the video game X developed by Y`.
- If the question asks for the author, do not say `the novel X by Y`.

---

## 12. LLM Rewrite Module

The LLM should only rewrite the canonical question.

### 12.1 LLM Input Contract

Input:

```json
{
  "canonical_question": "Who directed the film adaptation of Andy Weir's novel Project Hail Mary?",
  "answer": "Phil Lord and Christopher Miller",
  "required_anchors": [
    "film adaptation",
    "Andy Weir",
    "novel",
    "Project Hail Mary"
  ],
  "forbidden_patterns": [
    "years",
    "dates",
    "this year",
    "current",
    "latest",
    "recent",
    "as of"
  ],
  "target_property": "director",
  "domain": "film"
}
```

Prompt:

```text
Rewrite the canonical question into one concise SimpleQA-style fact-seeking question.

Rules:
- Return JSON only: {"question": "..."}.
- Do not answer the question.
- Do not add or remove factual constraints.
- Preserve all required anchors.
- Do not include any year, date, month, or temporal phrase.
- Do not use words like current, latest, recent, former, previous, or as of.
- Do not include the answer or any answer alias.
- Do not change the target relation.
- Prefer a short, plain, natural question.
```

### 12.2 Rewrite Fallback

If the LLM response fails validation:

1. Do not call the LLM again by default.
2. Fall back to the canonical question.
3. Mark:

```json
{
  "llm_rewrite_used": false,
  "rewrite_failure_reason": "temporal_expression_detected"
}
```

This keeps cost low and avoids hidden iterative model behavior.

---

## 13. LLM Provider Abstraction

Implement one provider interface.

```python
from abc import ABC, abstractmethod

class RewriteClient(ABC):
    """Abstract interface for one-shot question rewriting."""

    @abstractmethod
    def rewrite_question(self, payload: dict) -> dict:
        """Return a JSON object with a rewritten question."""
        raise NotImplementedError
```

### 13.1 Provider Config

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class LLMConfig:
    provider: str  # "openai", "anthropic", "openrouter", "openai_compatible"
    model: str
    api_key_env: str
    base_url: Optional[str] = None
    proxy: Optional[str] = None
    temperature: float = 0.0
    max_tokens: int = 256
```

Example config:

```python
PROXY = "socks5://127.0.0.1:7897"

OPENROUTER_CONFIG = LLMConfig(
    provider="openrouter",
    model="google/gemini-flash-1.5",  # Example only; choose current small model later.
    api_key_env="OPENROUTER_API_KEY",
    base_url="https://openrouter.ai/api/v1",
    proxy=PROXY,
)
```

### 13.2 Proxy Support

Recommended HTTP backend: `httpx`.

Install with SOCKS support:

```bash
pip install "httpx[socks]"
```

Use the proxy when creating clients:

```python
import httpx

def make_http_client(proxy: str | None = None, timeout: float = 60.0) -> httpx.Client:
    """Create an HTTP client with optional SOCKS/HTTP proxy support."""
    if proxy:
        return httpx.Client(proxy=proxy, timeout=timeout)
    return httpx.Client(timeout=timeout)
```

### 13.3 OpenAI Client

OpenAI's newer primary API is the Responses API, but Chat Completions remains useful for OpenAI-compatible providers. For the rewrite module, either is acceptable.

Use official OpenAI for `provider="openai"`.

```python
import os
from openai import OpenAI

class OpenAIRewriteClient(RewriteClient):
    """Rewrite client using the official OpenAI SDK."""

    def __init__(self, config: LLMConfig):
        self.config = config
        http_client = make_http_client(config.proxy)
        self.client = OpenAI(
            api_key=os.environ[config.api_key_env],
            http_client=http_client,
            base_url=config.base_url,
        )

    def rewrite_question(self, payload: dict) -> dict:
        """Rewrite a canonical question using an OpenAI-compatible chat call."""
        messages = [
            {
                "role": "system",
                "content": "You rewrite verified factual questions. Return JSON only."
            },
            {
                "role": "user",
                "content": build_rewrite_prompt(payload)
            },
        ]

        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        text = response.choices[0].message.content
        return parse_json_object(text)
```

### 13.4 OpenRouter Client

OpenRouter can be called through its OpenAI-compatible Chat Completions endpoint.

```python
class OpenRouterRewriteClient(OpenAIRewriteClient):
    """Rewrite client for OpenRouter via OpenAI-compatible API."""

    def __init__(self, config: LLMConfig):
        if not config.base_url:
            config.base_url = "https://openrouter.ai/api/v1"
        super().__init__(config)
```

Optional headers such as `HTTP-Referer` and `X-OpenRouter-Title` can be supported later, but do not make them mandatory.

### 13.5 Anthropic Client

Use Anthropic's Messages API via the official SDK.

```python
import os
import anthropic

class AnthropicRewriteClient(RewriteClient):
    """Rewrite client using the official Anthropic SDK."""

    def __init__(self, config: LLMConfig):
        self.config = config
        http_client = make_http_client(config.proxy)
        self.client = anthropic.Anthropic(
            api_key=os.environ[config.api_key_env],
            http_client=http_client,
        )

    def rewrite_question(self, payload: dict) -> dict:
        """Rewrite a canonical question using Anthropic Messages API."""
        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            system="You rewrite verified factual questions. Return JSON only.",
            messages=[
                {
                    "role": "user",
                    "content": build_rewrite_prompt(payload)
                }
            ],
        )

        text = response.content[0].text
        return parse_json_object(text)
```

### 13.6 OpenAI-Compatible Generic Client

For providers with OpenAI-compatible APIs:

```python
GENERIC_CONFIG = LLMConfig(
    provider="openai_compatible",
    model="provider/model-name",
    api_key_env="GENERIC_API_KEY",
    base_url="https://example.com/v1",
    proxy=PROXY,
)
```

Reuse `OpenAIRewriteClient`.

---

## 14. Post-Rewrite Validation

Every final question must pass deterministic validators.

### 14.1 Temporal Validator

```python
import re

YEAR_RE = re.compile(r"\b(17|18|19|20|21)\d{2}\b")

TEMPORAL_TERMS = {
    "this year",
    "last year",
    "next year",
    "recent",
    "recently",
    "current",
    "currently",
    "latest",
    "newest",
    "former",
    "previous",
    "as of",
    "released in",
    "published in",
    "opened in",
    "founded in",
    "established in",
}

MONTH_TERMS = {
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
}

def has_temporal_expression(question: str) -> bool:
    """Return True if the question contains forbidden temporal expressions."""
    q = question.lower()

    if YEAR_RE.search(q):
        return True

    if any(term in q for term in TEMPORAL_TERMS):
        return True

    if any(month in q for month in MONTH_TERMS):
        return True

    return False
```

### 14.1.1 Mutable-Fact Validator

In addition to checking whether the question contains explicit temporal words, reject question templates and target properties that are inherently mutable.

```python
MUTABLE_RELATIONSHIP_PROPERTIES = {
    "P26",    # spouse
    "P451",   # unmarried partner
}

MUTABLE_AFFILIATION_PROPERTIES = {
    "P54",    # member of sports team
    "P108",   # employer
    "P39",    # position held
    "P102",   # member of political party
}

CUMULATIVE_STATISTIC_PROPERTIES = {
    # Add sport-specific and platform-specific statistic properties here.
    # Default policy: avoid numeric live/career totals in v1.
}

def is_inherently_mutable_property(pid: str) -> bool:
    """Return True for properties whose values naturally change over time."""
    return (
        pid in MUTABLE_RELATIONSHIP_PROPERTIES
        or pid in MUTABLE_AFFILIATION_PROPERTIES
        or pid in CUMULATIVE_STATISTIC_PROPERTIES
    )
```

For v1, avoid all live numeric statistics unless a property-specific exception is explicitly added and the value is historically fixed.

### 14.2 Answer Leakage Validator

```python
def leaks_answer(question: str, answer_labels: list[str], answer_aliases: list[str]) -> bool:
    """Return True if the question contains the answer or an answer alias."""
    q = normalize_name(question)
    names = answer_labels + answer_aliases

    for name in names:
        if not name:
            continue
        if normalize_name(name) and normalize_name(name) in q:
            return True

    return False
```

### 14.3 Anchor Preservation Validator

```python
def preserves_required_anchors(question: str, anchors: list[str]) -> bool:
    """Check whether all required non-temporal disambiguation anchors are preserved."""
    q = normalize_name(question)

    for anchor in anchors:
        if normalize_name(anchor) not in q:
            return False

    return True
```

### 14.4 Question Simplicity Validator

Reject if:

- The question is too long, unless it contains a long scholarly article title.
- The question asks multiple things.
- The question contains `and why`, `explain`, `compare`, `list all`, or other non-SimpleQA patterns.
- The question contains multiple blanks or multi-hop reasoning demands beyond disambiguation.

---

## 15. Deduplication and Topic Balancing

### 15.1 Deduplication

Remove duplicates by:

- Exact normalized question.
- Same subject + same target property.
- Same answer dominating too many examples.
- Near-duplicate question templates.

Pseudo-code:

```python
def deduplicate(candidates):
    """Remove exact and structural duplicates."""
    seen_questions = set()
    seen_subject_property = set()
    output = []

    for c in candidates:
        q_key = normalize_name(c.rewritten_question or c.canonical_question)
        sp_key = (c.subject_qid, c.target_property_pid)

        if q_key in seen_questions:
            continue
        if sp_key in seen_subject_property:
            continue

        seen_questions.add(q_key)
        seen_subject_property.add(sp_key)
        output.append(c)

    return output
```

### 15.2 Pilot Balancing

For the 20-question pilot, use a simple quota:

```python
PILOT_DOMAIN_QUOTAS = {
    "film": 3,
    "books": 3,
    "video_games": 3,
    "scholarly_articles": 3,
    "art_architecture": 3,
    "organizations_places": 3,
    "music_albums": 2,
}
```

If a domain cannot produce enough high-confidence candidates, redistribute to other high-confidence domains.

Do not lower quality to satisfy quota.

---

## 16. Automatic Scoring / Evaluation System

The framework should include an evaluation system, not only a dataset generator.

The scoring module should be inspired by SimpleQA / SimpleQA Verified:

- Each model response is graded as one of:
  - `CORRECT`
  - `INCORRECT`
  - `NOT_ATTEMPTED`
- Compute:
  - `accuracy`: proportion of all questions answered correctly.
  - `incorrect_rate`: proportion answered incorrectly.
  - `not_attempted_rate`: proportion not attempted.
  - `attempt_rate`: proportion attempted.
  - `accuracy_given_attempted`: correct / attempted.
  - `f1`: harmonic mean of `accuracy` and `accuracy_given_attempted`.

### 16.1 Grading Labels

Use the following semantics.

#### CORRECT

A predicted answer is `CORRECT` if:

1. It contains the important information in the gold answer.
2. It does not contradict the gold answer.
3. It may include harmless extra context.
4. Semantic equivalence matters more than capitalization, punctuation, order, or minor typos.
5. For entities, accepted aliases should be considered correct.
6. For questions where the answer type is implicitly clear from the question, shorter forms may be accepted if unambiguous.

Example:

```text
Gold: Malia Obama and Sasha Obama
Prediction: Sasha and Malia
Grade: CORRECT
```

#### INCORRECT

A predicted answer is `INCORRECT` if:

1. It contradicts the gold answer.
2. It gives a different entity/value.
3. It includes the correct answer but also adds a contradictory or wrong answer.
4. It makes a false factual claim relevant to the answer.
5. It presents several alternatives and at least one contradicts the gold answer.

Example:

```text
Gold: Malia Obama and Sasha Obama
Prediction: Malia, Sasha, and Susan
Grade: INCORRECT
```

#### NOT_ATTEMPTED

A predicted answer is `NOT_ATTEMPTED` if:

1. It explicitly says it does not know.
2. It refuses to answer.
3. It asks for more context without giving a contradictory factual answer.
4. It gives a vague range or generic statement that neither confirms nor contradicts the gold answer.
5. It gives only partial information and the missing part is essential, while not contradicting the gold answer.

Example:

```text
Gold: Malia Obama and Sasha Obama
Prediction: I know one is Malia, but I am not sure about the other.
Grade: NOT_ATTEMPTED
```

### 16.2 Deterministic Pre-Grader

Before calling an autorater, implement a deterministic pre-grader for easy cases.

```python
def deterministic_grade(prediction: str, gold: str, aliases: list[str]) -> str | None:
    """Return a grade for easy cases, or None if an LLM autorater is needed."""
    if is_empty_or_refusal(prediction):
        return "NOT_ATTEMPTED"

    if exact_or_alias_match(prediction, gold, aliases):
        return "CORRECT"

    if clearly_contains_wrong_alternative(prediction, gold, aliases):
        return "INCORRECT"

    return None
```

This reduces autorater cost, but should stay conservative. If uncertain, return `None`.

### 16.3 LLM Autorater

For ambiguous cases, call a grader model once.

The grader prompt should be based on the SimpleQA / SimpleQA Verified style:

```text
Your job is to look at a question, a gold target, and a predicted answer,
and assign one grade: CORRECT, INCORRECT, or NOT_ATTEMPTED.

Use semantic equivalence. Do not require exact string match.
Do not punish capitalization, punctuation, grammar, order, or minor typos.
A correct answer must include the important information in the gold target
and must not contradict it.
If the predicted answer contradicts the gold target, grade INCORRECT.
If the predicted answer does not include the important information but also
does not contradict the gold target, grade NOT_ATTEMPTED.

Return JSON only:
{"grade": "CORRECT" | "INCORRECT" | "NOT_ATTEMPTED"}
```

Use the same LLM provider abstraction as the rewrite module, but with a separate `GraderClient`.

```python
class GraderClient(ABC):
    """Abstract interface for grading model predictions."""

    @abstractmethod
    def grade_answer(self, payload: dict) -> dict:
        """Return a JSON object with a grade."""
        raise NotImplementedError
```

Recommended grading payload:

```json
{
  "question": "...",
  "gold_answer": "...",
  "gold_aliases": ["..."],
  "answer_type": "person",
  "predicted_answer": "...",
  "grading_rules": {
    "allow_semantic_equivalence": true,
    "allow_minor_typos": true,
    "penalize_contradictions": true
  }
}
```

### 16.4 Metrics

Implement metrics exactly and store all intermediate counts.

```python
def compute_simpleqa_metrics(grades: list[str]) -> dict:
    """Compute SimpleQA-style metrics from CORRECT/INCORRECT/NOT_ATTEMPTED grades."""
    n = len(grades)
    correct = sum(g == "CORRECT" for g in grades)
    incorrect = sum(g == "INCORRECT" for g in grades)
    not_attempted = sum(g == "NOT_ATTEMPTED" for g in grades)
    attempted = correct + incorrect

    accuracy = correct / n if n else 0.0
    incorrect_rate = incorrect / n if n else 0.0
    not_attempted_rate = not_attempted / n if n else 0.0
    attempt_rate = attempted / n if n else 0.0
    accuracy_given_attempted = correct / attempted if attempted else 0.0

    if accuracy + accuracy_given_attempted > 0:
        f1 = 2 * accuracy * accuracy_given_attempted / (accuracy + accuracy_given_attempted)
    else:
        f1 = 0.0

    return {
        "n": n,
        "correct": correct,
        "incorrect": incorrect,
        "not_attempted": not_attempted,
        "attempted": attempted,
        "accuracy": accuracy,
        "incorrect_rate": incorrect_rate,
        "not_attempted_rate": not_attempted_rate,
        "attempt_rate": attempt_rate,
        "accuracy_given_attempted": accuracy_given_attempted,
        "f1": f1,
    }
```

### 16.5 Evaluation Input / Output Format

Predictions input JSONL:

```json
{
  "id": "wikidata_verified_pilot_000001",
  "question": "...",
  "gold_answer": "...",
  "gold_aliases": ["..."],
  "predicted_answer": "..."
}
```

Graded output JSONL:

```json
{
  "id": "wikidata_verified_pilot_000001",
  "question": "...",
  "gold_answer": "...",
  "predicted_answer": "...",
  "grade": "CORRECT",
  "grader": {
    "method": "deterministic" ,
    "model": null
  }
}
```

If an LLM autorater is used:

```json
{
  "grader": {
    "method": "llm_autorater",
    "provider": "openrouter",
    "model": "openai/gpt-4.1",
    "temperature": 0.0
  }
}
```

Metrics output JSON:

```json
{
  "model_name": "model-under-evaluation",
  "dataset_path": "outputs/pilot_20.jsonl",
  "prediction_path": "outputs/predictions.jsonl",
  "n": 20,
  "accuracy": 0.45,
  "incorrect_rate": 0.30,
  "not_attempted_rate": 0.25,
  "attempt_rate": 0.75,
  "accuracy_given_attempted": 0.60,
  "f1": 0.5142857143
}
```

### 16.6 Evaluation Scripts

Add:

```text
scripts/
  run_eval.py
  grade_predictions.py
  summarize_metrics.py
```

Example usage:

```bash
python scripts/grade_predictions.py \
  --dataset outputs/pilot_20.jsonl \
  --predictions outputs/model_predictions.jsonl \
  --output outputs/graded_predictions.jsonl \
  --grader-provider openrouter \
  --grader-model "openai/gpt-4.1" \
  --proxy socks5://127.0.0.1:7897

python scripts/summarize_metrics.py \
  --graded outputs/graded_predictions.jsonl \
  --output outputs/metrics.json
```

### 16.7 Grading Pitfalls

Important grading pitfalls:

1. Do not use pure string matching as the only scorer.
2. Do not mark a hedged answer as wrong if it contains the full correct answer and no contradiction.
3. Do mark an answer incorrect if it gives the correct answer plus a wrong alternative.
4. Do not punish minor typos or harmless name variants.
5. Use accepted aliases from Wikidata, but do not allow aliases that are themselves ambiguous.
6. Numeric answers require special handling:
   - exact known values should match the precision of the gold answer,
   - acceptable ranges can be stored in metadata where appropriate,
   - if no tolerance is specified, avoid numeric questions in the first version.
7. Date answers should generally be avoided because the question text forbids temporal clues and the project prioritizes time-invariant entity/fact answers.

## 17. Suggested Project Structure

```text
wikidata_simpleqa/
  README.md
  pyproject.toml
  src/
    wikidata_simpleqa/
      __init__.py
      config.py
      constants.py
      wikidata_client.py
      sparql_queries.py
      domain_templates.py
      candidate_harvester.py
      entity_normalization.py
      ambiguity.py
      descriptors.py
      canonical_questions.py
      llm_rewrite.py
      grading.py
      grader_clients.py
      metrics.py
      validators.py
      dedup.py
      balance.py
      pipeline.py
      io.py
  scripts/
    generate_pilot.py
    inspect_candidates.py
    grade_predictions.py
    summarize_metrics.py
    run_eval.py
  outputs/
    pilot_20.jsonl
    rejected_candidates.jsonl
  tests/
    test_temporal_validator.py
    test_normalize_name.py
    test_answer_leakage.py
    test_disambiguation.py
```

---

## 18. Main Pipeline Pseudo-Code

```python
def run_pipeline(config):
    """Run the full Wikidata-to-SimpleQA-style generation pipeline."""
    wikidata = WikidataClient(
        user_agent=config.user_agent,
        proxy=config.proxy,
        timeout=config.timeout,
    )

    rewrite_client = make_rewrite_client(config.llm)

    all_candidates = []

    for template in config.domain_templates:
        # Step 1: Harvest candidates with the target-year filter.
        raw_candidates = harvest_candidates(
            wikidata=wikidata,
            template=template,
            target_year=config.target_year,
            limit=config.harvest_limit_per_template,
        )

        for raw in raw_candidates:
            # Step 2: Hydrate subject and answer entities.
            candidate = hydrate_candidate(wikidata, raw, template)

            # Step 3: Reject unstable or not-yet-settled facts.
            if not verify_time_invariance(candidate, run_date=config.run_date):
                reject(candidate, reason="answer_not_time_invariant")
                continue

            # Step 4: Early rejection for temporal labels.
            if has_temporal_expression(candidate.subject_label):
                reject(candidate, reason="subject_label_contains_temporal_expression")
                continue

            # Step 5: Verify answer uniqueness.
            if not verify_answer_uniqueness(wikidata, candidate):
                reject(candidate, reason="answer_not_unique")
                continue

            # Step 6: Build competitor set.
            competitors = build_competitor_set(candidate.subject_entity, wikidata)

            # Step 7: Try direct label uniqueness first.
            if not competitors:
                candidate.ambiguity_status = "label_unique"
                descriptor = make_basic_descriptor(candidate)
            else:
                # Step 8: Find a non-temporal disambiguation signature.
                descriptors = extract_descriptors(candidate, competitors)
                signature = find_non_temporal_signature(
                    target=candidate.subject_entity,
                    competitors=competitors,
                    descriptors=descriptors,
                )

                if not signature:
                    reject(candidate, reason="requires_temporal_or_unavailable_disambiguation")
                    continue

                candidate.ambiguity_status = "resolved_by_non_temporal_descriptor"
                candidate.disambiguation_signature = [d.text for d in signature]
                descriptor = render_descriptor(candidate, signature)

            # Step 9: Build deterministic canonical question.
            candidate.canonical_question = build_canonical_question(
                template=template,
                descriptor=descriptor,
            )

            # Step 10: Validate canonical question.
            if not validate_question(candidate.canonical_question, candidate):
                reject(candidate, reason="canonical_question_failed_validation")
                continue

            # Step 11: One-shot LLM rewrite.
            rewrite_payload = build_rewrite_payload(candidate)
            rewritten = rewrite_client.rewrite_question(rewrite_payload)

            candidate.rewritten_question = rewritten.get("question")

            # Step 12: Validate rewritten question; fallback to canonical if needed.
            if not validate_question(candidate.rewritten_question, candidate):
                candidate.validation_flags["llm_rewrite_used"] = False
                candidate.validation_flags["rewrite_failed"] = True
                candidate.rewritten_question = candidate.canonical_question
            else:
                candidate.validation_flags["llm_rewrite_used"] = True

            all_candidates.append(candidate)

    # Step 13: Deduplicate and balance.
    all_candidates = deduplicate(all_candidates)
    pilot = balance_by_domain(all_candidates, quotas=config.pilot_domain_quotas)

    # Step 14: Write output.
    write_jsonl(pilot, config.output_path)
    write_jsonl(get_rejections(), config.rejected_output_path)

    return pilot
```

---

## 19. Important Pitfalls

### 18.1 Label Uniqueness Is Not Enough

A subject may have a unique label, but the generated question may still be ambiguous if the descriptor is too vague.

Example:

```text
Who created X?
```

This could mean author, artist, developer, founder, or creator depending on domain.

Use property-specific templates:

```text
Who wrote the novel X?
Who created the artwork X?
Which company developed the video game X?
```

### 18.2 Answer Uniqueness Is Not Subject Uniqueness

Even if `subject + property` has exactly one answer, the question may refer to another same-title subject.

Reject or disambiguate using non-temporal descriptors.

### 18.3 Same-Name Works Across Media

Common collisions:

- Book vs. film.
- Film vs. TV series.
- Song vs. album.
- Video game vs. franchise.
- Artwork vs. exhibition.
- Building vs. organization.

Resolve using medium/type descriptors, not years.

### 18.4 Same-Name Works Within the Same Medium

Most dangerous case:

- Multiple films with the same title.
- Multiple songs with the same title.
- Multiple albums with the same title.

If they can only be distinguished by year, reject.

### 18.5 Official Labels With Years

Many sports seasons, award ceremonies, competitions, and events have official labels containing years.

Because the strict default forbids all years in questions, reject those candidates in the first version.

### 18.6 Temporal or Current Facts

Avoid:

- Current CEO.
- Current president.
- Current mayor.
- Latest winner.
- Current population.
- Latest album.
- Recent episode.

These facts need temporal framing. They violate the no-time-clue rule.

### 18.7 Wikidata Truthy Statements Can Hide Complexity

`wdt:` properties are convenient but may hide statement rank and qualifier complexity.

Use full claims via `wbgetentities` when necessary, especially for:

- Multiple normal-rank values.
- Deprecated statements.
- Qualifiers.
- Temporal statements.

### 18.8 LLM Rewrite Can Accidentally Remove Disambiguation

Example:

Canonical:

```text
Who directed the film adaptation of Andy Weir's novel Project Hail Mary?
```

Bad rewrite:

```text
Who directed Project Hail Mary?
```

This loses the `film adaptation` descriptor and becomes ambiguous.

The anchor preservation validator must catch this.

### 18.9 LLM Rewrite Can Add Temporal Phrases

Bad rewrite:

```text
Who directed the recent film adaptation of Project Hail Mary?
```

Reject and fall back to canonical.

### 18.10 LLM Rewrite Can Leak the Answer

Bad rewrite:

```text
Which journal published the Nature article X?
```

If the answer is `Nature`, this leaks the answer.

Reject.

### 18.11 Topic Imbalance

Wikidata coverage may overproduce films, music, and sports.

Use quotas and do not allow one domain to dominate the pilot or final dataset.

### 18.12 Open-Source Reproducibility

Store:

- Target year.
- Access date.
- Query template.
- Wikidata QIDs/PIDs.
- Rejection reasons.
- LLM provider/model.
- Whether the final question is canonical or LLM-rewritten.

---

## 20. Rejection Reasons

Use structured rejection reasons for debugging and analysis.

```python
REJECTION_REASONS = {
    "subject_label_contains_temporal_expression",
    "answer_not_time_invariant",
    "future_dated_or_unsettled_fact",
    "mutable_relationship_or_status",
    "mutable_affiliation_or_office",
    "cumulative_statistic",
    "answer_not_unique",
    "no_english_label",
    "no_answer_label",
    "same_label_competitor_requires_temporal_disambiguation",
    "no_non_temporal_signature",
    "descriptor_leaks_answer",
    "canonical_question_failed_validation",
    "rewrite_contains_year",
    "rewrite_contains_temporal_expression",
    "rewrite_lost_required_anchor",
    "rewrite_leaks_answer",
    "duplicate_question",
    "quota_exceeded",
}
```

Write all rejected candidates to `rejected_candidates.jsonl`.

---

## 21. Testing Requirements

Implement tests before scaling.

### 21.0 Time-Invariance Tests

Cases that must fail:

```text
Who is the current CEO of X?
Who is the latest winner of X?
Who will direct the upcoming film X?
Where is the planned event X scheduled to be held?
How many employees does X currently have?
Who is X's current wife?
Who is X married to?
Which club does X currently play for?
How many career goals has Erling Haaland scored?
How many total citations does article X have?
How many followers does X have?
What is X's net worth?
```

Cases that may pass:

```text
Who wrote the published novel X?
Who directed the released film adaptation of X?
In which journal was the published article X published?
Who designed the completed building X?
Who won the completed event X?
```

### 21.1 Temporal Validator Tests

Cases that must fail:

```text
Who directed the 2026 film X?
Who directed X this year?
Who is the current CEO of X?
Who won the latest edition of X?
Who published X in January?
```

Cases that may pass:

```text
Who directed the film adaptation of Andy Weir's novel Project Hail Mary?
Who wrote the science-fiction novel Project Hail Mary?
```

### 21.2 Ambiguity Tests

Create fixture entities for:

- Book + film with same title.
- Two films with same title, different years.
- Song + album with same title.
- Label-unique scholarly article.

Expected behavior:

- Book + film can pass only with medium/source descriptor.
- Two same-title films must fail if no non-temporal descriptor distinguishes them.
- Song/album must use medium descriptor.
- Label-unique scholarly article can pass directly.

### 21.3 Answer Leakage Tests

If answer is `Nature`, reject:

```text
In which journal was the Nature article X published?
```

If answer is `Andy Weir`, reject:

```text
Who wrote Andy Weir's novel Project Hail Mary?
```

when the target property is author.

---

## 22. First Pilot Generation

The first runnable script should be:

```bash
python scripts/generate_pilot.py \
  --target-year 2026 \
  --pilot-total 20 \
  --proxy socks5://127.0.0.1:7897 \
  --llm-provider openrouter \
  --llm-model "some-small-model"
```

Output:

```text
outputs/pilot_20.jsonl
outputs/rejected_candidates.jsonl
```

The pilot should be manually inspected before scaling.

Pilot examples should not be called final verified questions.

---

## 23. Minimum Viable Implementation Order

Implement in this order:

1. `WikidataClient`
   - SPARQL query.
   - `wbgetentities`.
   - `wbsearchentities`.
   - User-Agent.
   - Proxy.
   - Timeout/retry.

2. `domain_templates.py`
   - Domain-property-date configs.
   - Canonical templates.
   - Descriptor rules.

3. Candidate harvesting with early target-year filter.

4. Temporal expression validator.

5. Time-invariance and settled-fact validator.

6. Answer uniqueness validator.

7. Competitor search.

8. Non-temporal descriptor extraction and signature search.

9. Canonical question builder.

10. LLM rewrite clients.

11. Post-rewrite validators.

12. Deduplication and domain balancing.

13. Automatic grading system and SimpleQA-style metrics.

14. Pilot script.

15. Tests.

---

## 24. Useful Implementation Notes

### 23.1 Dependencies

Suggested:

```bash
pip install httpx "httpx[socks]" pydantic tenacity pandas tqdm python-dotenv
pip install openai anthropic
```

Optional:

```bash
pip install SPARQLWrapper
```

However, a direct `httpx` implementation is often enough.

### 23.2 User-Agent

Set a meaningful User-Agent for Wikimedia requests:

```python
USER_AGENT = "wikidata-simpleqa-generator/0.1 (contact: your-email@example.com)"
```

### 23.3 Rate Limiting

Add:

- Retries with exponential backoff.
- Request timeout.
- Small concurrency at first.
- Cache `wbgetentities` results by QID.
- Cache `wbsearchentities` results by normalized search string.

### 23.4 Caching

Recommended cache files:

```text
cache/entities/{qid}.json
cache/search/{normalized_query}.json
cache/sparql/{hash}.json
```

### 23.5 Deterministic Seeds

For reproducibility:

```python
RANDOM_SEED = 42
```

Use deterministic ordering when sampling candidates.

---

## 24. External References for Implementation

Useful references:

- SimpleQA paper: https://arxiv.org/abs/2411.04368
- OpenAI SimpleQA reference implementation: https://github.com/openai/simple-evals/blob/main/simpleqa_eval.py
- SimpleQA Verified paper: https://arxiv.org/abs/2509.07968
- SimpleQA Verified dataset card: https://huggingface.co/datasets/google/simpleqa-verified
- Inspect Evals SimpleQA / SimpleQA Verified implementation notes: https://ukgovernmentbeis.github.io/inspect_evals/evals/knowledge/simpleqa/
- Wikidata data access: https://www.wikidata.org/wiki/Wikidata:Data_access
- Wikibase API documentation: https://www.mediawiki.org/wiki/Wikibase/API/en
- Wikidata Query Service manual: https://www.mediawiki.org/wiki/Wikidata_Query_Service/User_Manual

## 25. Summary of the Core Philosophy

The framework should be conservative.

Accept a candidate only if:

1. It is recent/new according to `TARGET_YEAR`.
2. The question itself contains no temporal clue.
3. The gold answer is time-invariant and does not depend on when the question is asked; mutable relationships, offices, affiliations, and cumulative statistics are rejected.
4. The answer is unique.
5. The subject is uniquely identifiable without time-based disambiguation.
6. The non-temporal descriptor does not leak the answer.
7. The LLM rewrite preserves all constraints.
8. The example can be audited through Wikidata metadata.
9. The example can be evaluated with a SimpleQA-style automatic grader.

If any of these fail, reject the candidate.

High precision matters more than high recall, especially in the first version.

## Template Status Maintenance

Maintain a canonical template-status index in `outputs/template_status_index.json` and `outputs/template_status_index.md`.

- Rebuild it after every meaningful rerun or review-bundle update.
- Every template in the catalog must have a current status such as `proven`, `rejected_only`, `error`, or another explicit non-proven state.
- `rejected_only` and `error` entries must carry machine-readable reasons taken from the latest available run artifacts.
- The review bundle defines the current `proven` set; stale historical accepts do not remain proven if they are filtered out by newer deterministic rules.
