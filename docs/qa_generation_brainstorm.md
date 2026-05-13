# Brainstorm: Automated Generation of SimpleQA-like Long-tail QA

## 1. Project Goal

We want to automatically generate **SimpleQA-like long-tail factual questions**.

The target questions should be:

- Natural and human-like.
- Short factual questions with a single, stable, unambiguous answer.
- Similar in spirit to SimpleQA Verified.
- Preferably long-tail: not easily answered from highly popular web snippets or common benchmark-style knowledge.
- Auditable: each question should have evidence and a reliable answer source.
- Automatically scorable: the answer should be short and have aliases when needed.

The goal is **not** to maximize reasoning complexity.  
The goal is to produce natural, stable, verifiable, long-tail factual QA.

---

## 2. Core Design Principle

Do not treat each route as a complete end-to-end pipeline.

Instead, design the system as:

```text
multiple candidate generators
    -> unified normalization
    -> deduplication
    -> evidence grounding
    -> question naturalization / rewrite
    -> long-tail verification
    -> answer validation
    -> optional LLM judge
    -> optional small human audit
```

Each route should be a **candidate generator**.

The final quality should be enforced by shared filters and validators.

This makes the system extensible: Wikidata, Wikipedia, tables, search, external APIs, and existing QA datasets can all contribute candidates.

---

## 3. Unified Candidate Schema

Every generator should output the same basic structure.

```json
{
  "id": "...",
  "question": "...",
  "answer": "...",
  "answer_aliases": [],
  "source_type": "wikidata | wikipedia | infobox | table | list | external_api | search | hybrid",
  "subject_entity": {
    "name": "...",
    "qid": "...",
    "wikipedia_title": "...",
    "url": "..."
  },
  "answer_entity": {
    "name": "...",
    "qid": "...",
    "url": "..."
  },
  "relation_or_claim": "...",
  "evidence": {
    "text": "...",
    "url": "...",
    "source_title": "...",
    "section": "...",
    "retrieved_at": "..."
  },
  "generation_route": "...",
  "longtail_features": {
    "wikipedia_pageviews": null,
    "wikidata_sitelinks": null,
    "wikidata_degree": null,
    "search_topk_answer_leakage": null,
    "search_result_count": null,
    "subject_ambiguity_score": null
  },
  "validation": {
    "answer_in_evidence": true,
    "answer_unique": true,
    "question_unambiguous": true,
    "stable_answer": true,
    "needs_time_context": false
  },
  "notes": []
}
```

Small tips:

- Keep raw evidence and intermediate metadata.
- Do not only save the final question and answer.
- Long-tail QA generation is noisy; auditability matters.

---

## 4. Shared Filters

All routes should eventually use the same filters.

### 4.1 Stability Filter

Reject questions whose answers may change over time.

Bad examples:

- Who is the current CEO of X?
- How many goals has player Y scored in his career?
- Who is currently married to X?

Good examples:

- Who directed the 1978 documentary film X?
- Which publisher released the first edition of X?
- Who won the X Award in 2006?

Small tips:

- Historical dates are allowed when they help disambiguate.
- Avoid recent events after a configurable cutoff year unless intentionally included.
- Avoid “currently”, “now”, “as of today”, “latest”, “career total”, etc.

### 4.2 Ambiguity Filter

Reject or rewrite questions if the subject is ambiguous.

Signals:

- Subject title is very short.
- Search results point to multiple entities.
- Multiple Wikipedia pages have similar names.
- The answer differs across sources.
- The question omits necessary descriptors.

Example:

Bad:

```text
Who directed X?
```

Better:

```text
Who directed the 1978 Canadian documentary film X?
```

Small tips:

- Use descriptors from the Wikipedia lead sentence.
- Add year, country, type, or creator only when needed.
- If the subject remains ambiguous after rewriting, discard the candidate.

### 4.3 Long-tail Filter

Use multiple approximate signals:

- Low Wikipedia pageviews.
- Low Wikidata sitelink count.
- Low Wikidata degree.
- Low search result count.
- Top-k search snippets do not directly reveal the answer.
- The exact question does not already appear online.
- The subject-answer pair is not too prominently repeated.

Small tips:

- Search should mostly be used as a **leakage verifier**, not necessarily as the main candidate generator.
- Use a long-tail score instead of a hard binary rule.
- Store search snippets for audit.

### 4.4 Evidence Filter

Keep only candidates where the answer is supported by evidence.

Possible checks:

- Exact answer string appears in evidence.
- Answer alias appears in evidence.
- Wikidata statement matches Wikipedia text.
- Infobox value matches lead/body/table value.
- LLM entailment judge confirms that evidence supports the answer.

Small tips:

- Use conservative validation.
- It is better to discard many candidates than to keep noisy ones.
- Store both evidence and rejection reasons.

### 4.5 Naturalness Filter

Reject questions that look too artificial.

Bad examples:

- What is the P57 of entity Q123?
- What is the director property of the film X?
- Which entity is connected to X by relation Y?

Better examples:

- Who directed the film X?
- Which company published the novel X?
- What network originally aired the television series X?

Small tips:

- Use relation-specific paraphrase banks.
- Use one rewrite pass.
- Save both the deterministic pre-rewrite question and the rewritten question.
- Reject rewrites that change the answer.

---

## 5. Existing Three Routes

## Route 1: Wikidata-first, WDQS-light Single-hop

### Idea

Keep the current Wikidata-based fact generation approach, but avoid heavy WDQS queries.

Use lightweight Wikidata APIs:

- `wbsearchentities`
- `wbgetentities`
- direct QID fetch
- sitelinks
- entity labels and aliases
- preselected property families

### Strengths

- Closest to the existing codebase.
- Auditable.
- Easy to normalize answers.
- Good for stable one-hop facts.

### Weaknesses

- Questions may sound template-like.
- Wikidata modeling quirks.
- Some relations are too unnatural for SimpleQA-style questions.

### Small tips

- Do not query arbitrary properties.
- Use curated property families.
- Add descriptors from Wikipedia lead sentences.
- Use NQ/SimpleQA-style paraphrases to reduce template flavor.
- Treat this as a high-control baseline, not the only route.

## Route 2: Wikidata Seed + Wikipedia Evidence Hybrid

### Idea

Use Wikidata to get the answer, but use Wikipedia text to write a more natural question.

Basic flow:

```text
Wikidata subject + property + object
    -> find corresponding Wikipedia page
    -> locate sentence or paragraph mentioning the object
    -> verify the sentence supports the relation
    -> rewrite into natural question
```

### Strengths

- Combines structured answer reliability with natural evidence.
- More natural than pure Wikidata templates.
- Good auditability.

### Weaknesses

- Mapping Wikidata statements to Wikipedia paragraphs is hard.
- Object labels may not appear exactly.
- Dates, quantities, and aliases need normalization.

### Small tips

Start with a weak alignment version:

- Subject QID -> English Wikipedia sitelink.
- Object label or alias exact match in page text.
- Relation-specific cue words.
- LLM entailment judge only after cheap string matching.
- Keep both the Wikidata statement and Wikipedia evidence.

## Route 3: Search-first Candidate Mining, Wikidata-backed Normalization

### Idea

Use search results to discover candidate facts first, then use Wikidata only to normalize or validate answers.

### Strengths

- Potentially captures naturally phrased facts.
- May directly target long-tail web content.

### Weaknesses

- Hard to control.
- Hard to normalize entities.
- Hard to verify answer uniqueness.
- Search snippets may be noisy.
- Not ideal as the main route.

### Small tips

Do not use this as the primary generation route at first.

Better uses of search:

- Long-tail leakage verification.
- Ambiguity detection.
- Natural query style mining.
- Subject-answer co-occurrence checking.

---

# 6. Additional Candidate Generation Routes

## Route 4: Wikipedia-first Atomic Claim Extraction

### Idea

Start from Wikipedia pages, extract atomic factual claims from natural prose, then turn them into QA.

Flow:

```text
sample long-tail Wikipedia pages
    -> extract lead/body sentences
    -> identify atomic claims
    -> entity-link subject and answer
    -> rewrite claim into question
    -> validate with evidence/Wikidata
```

### Strengths

- Naturally phrased evidence.
- Less template-like.
- Good source diversity.

### Weaknesses

- Claim extraction can be noisy.
- Some sentences contain multiple facts.
- Requires strong filtering.

### Small tips

- Start with lead sentences and early sections.
- Prefer sentences with one clear subject and one clear answer.
- Avoid sentences with many entities.
- Use LLM to split complex sentences into atomic claims.
- Keep only claims whose answer is short.

## Route 5: Wikipedia Infobox-first

### Idea

Parse Wikipedia infoboxes directly and generate questions from stable fields.

Good domains:

- Films
- Books
- Albums
- TV series
- Buildings
- Organizations
- People
- Sports teams
- Species

Example fields:

- film -> director, producer, music by, cinematographer
- book -> author, illustrator, publisher, original language
- album -> artist, producer, label, release date
- building -> architect, location, opened
- TV series -> original network, composer, number of seasons

### Strengths

- Does not depend heavily on WDQS.
- Semi-structured.
- High yield.
- Easier than full paragraph alignment.

### Weaknesses

- Infobox templates are inconsistent.
- Field names vary.
- Some values are lists or ambiguous.

### Small tips

- Build per-domain field allowlists.
- Reject fields with too many values.
- Cross-check with Wikidata or page body when possible.
- Normalize dates and names.
- Avoid overly database-like fields unless they sound natural.

## Route 6: Wikidata Statement -> Wikipedia Evidence Alignment

### Idea

A stronger version of Route 2.

Given a Wikidata statement:

```text
(subject, property, object)
```

Find the exact Wikipedia sentence or paragraph that expresses the same fact.

### Alignment signals

- Object label appears in text.
- Object alias appears in text.
- Date or quantity appears in normalized form.
- Relation-specific cue words appear.
- The sentence is in a relevant section.
- LLM entailment confirms support.

### Strengths

- High auditability.
- Natural evidence.
- Strong method-section value.

### Weaknesses

- Engineering complexity.
- Alias/date matching is hard.

### Small tips

Implement in stages:

1. Exact object label match.
2. Alias match.
3. Date normalization.
4. Quantity/unit normalization.
5. Relation cue word scoring.
6. LLM entailment judge.

## Route 7: Wikipedia Category-first Domain Balancing

### Idea

Use Wikipedia categories to sample entities across domains.

Examples:

- 19th-century women writers
- Railway stations opened in 1912
- Japanese independent films
- Defunct newspapers
- Buildings and structures in a region
- Minor planets named for people
- Species described in a certain year

### Strengths

- Good domain balancing.
- Less dependent on Wikidata ontology.
- Useful for long-tail sampling.

### Weaknesses

- Category graph is messy.
- Categories overlap.
- Some categories are too broad or too narrow.

### Small tips

- Use category seeds as sampling pools, not as final evidence.
- Deduplicate pages across categories.
- Keep category metadata for domain labels.
- Avoid overfitting to a small number of categories.

## Route 8: Wikipedia Pageview-first Long-tail Sampling

### Idea

First select long-tail Wikipedia pages using pageview statistics, then generate questions from those pages.

### Strengths

- Directly targets tail entities.
- Can be combined with infobox/table/prose extraction.

### Weaknesses

- Very low-pageview pages may have poor evidence.
- Some pages are stubs.
- Low popularity does not always mean good QA material.

### Small tips

- Use pageview as a soft score, not a hard rule.
- Combine with page length and infobox presence.
- Reject pages that are too short.
- Use domain quotas to avoid narrow distributions.

## Route 9: Lead-sentence Descriptor Route

### Idea

Use the Wikipedia lead sentence to create natural descriptors for the subject.

Example:

```text
Lead:
X is a 1978 Canadian documentary film directed by Y.

Question:
Who directed the 1978 Canadian documentary film X?

Answer:
Y
```

### Strengths

- Produces natural disambiguation.
- Very useful for obscure works/entities.
- Reduces ambiguity.

### Weaknesses

- Descriptors may become too long.
- Lead sentences can contain too much information.

### Small tips

- Extract short descriptors: year + nationality + type.
- Avoid copying the entire lead sentence.
- Use descriptor only when needed.
- Good for films, books, albums, people, buildings, and organizations.

## Route 10: Wikidata Qualifiers-first

### Idea

Use Wikidata qualifiers to generate constrained factual questions.

Examples:

- Who won the X Award in 2006?
- Which club did player X play for during the 2012 season?
- Which publisher released the first edition of book X?

### Strengths

- More natural than bare triples.
- Creates useful constraints.
- Good for historical facts.

### Weaknesses

- Qualifier structures are complex.
- Validation is harder.
- Risk of non-unique answers.

### Small tips

- Start with a small set of well-understood qualifier patterns.
- Always check uniqueness.
- Use time qualifiers only for historical stable facts.
- Avoid current or ongoing statuses.

## Route 11: Wikidata References-first

### Idea

Prefer Wikidata statements that have references, then use reference metadata or pages as supporting evidence.

### Strengths

- Strong auditability.
- Better factual reliability.
- Useful for high-precision subsets.

### Weaknesses

- References are inconsistent.
- Some references are dead links.
- Many references are hard to parse.

### Small tips

- Prioritize accessible references.
- Store reference URL and title.
- Use references as validation, not necessarily as naturalization input.
- Good for official databases, books, and authority files.

## Route 12: Wikipedia Table-first

### Idea

Extract facts from Wikipedia tables.

Good table types:

- Award winners
- Filmographies
- Discographies
- Sports seasons
- Election results
- Railway stations
- Heritage lists
- Academic prize recipients
- Chart positions
- Episode lists

### Strengths

- High yield.
- Naturally supports semi-structured QA.
- Adds domain diversity.

### Weaknesses

- Tables vary in structure.
- Some tables contain dynamic or incomplete information.
- Questions can sound like table lookup.

### Small tips

- Use table caption, page title, and column names as context.
- Require answer uniqueness within the table.
- Avoid tables with too many missing values.
- Prefer stable historical tables.
- Store row and column evidence.

## Route 13: Wikipedia List-page Route

### Idea

Extract facts from list pages, including bullet lists and sectioned lists.

Examples:

- List of churches in ...
- List of newspapers in ...
- List of diplomatic missions of ...
- List of compositions by ...
- List of awards and nominations received by ...

### Strengths

- Huge coverage.
- Excellent for long-tail domains.
- Less constrained than infoboxes.

### Weaknesses

- HTML structures are inconsistent.
- Bullet lists may be messy.
- Some lists are incomplete.

### Small tips

- Use section titles as context.
- Prefer lists with clear repeated structure.
- Reject overly long or vague rows.
- Pair with search leakage check.

## Route 14: Infobox + Table Cross-check

### Idea

Keep only facts that appear in both an infobox and another source such as a table, lead sentence, or page body.

### Strengths

- High precision.
- Good for building a trusted validation subset.

### Weaknesses

- Lower recall.
- More engineering required.

### Small tips

- Use this for high-quality examples shown to humans.
- Do not require this for all candidates, or recall will collapse.
- Useful for evaluating noise rate of other routes.

## Route 15: Natural Questions Style Transfer

### Idea

Use Natural Questions or similar real-user-query datasets as a style bank, not necessarily as a fact source.

Flow:

```text
mine natural question patterns
    -> map patterns to relation families
    -> apply patterns to generated facts
    -> rewrite for fluency
```

### Strengths

- Improves naturalness.
- Reduces template flavor.
- Gives realistic question wording.

### Weaknesses

- Pattern transfer can create unnatural mismatches.
- Requires relation-specific constraints.

### Small tips

- Use this as a rewrite/paraphrase component.
- Keep original deterministic template for audit.
- Save both pre-rewrite and post-rewrite question.
- Reject rewrites that change the answer.

## Route 16: SimpleQuestions / WebQuestions Pattern Mining

### Idea

Use existing KBQA datasets to learn how people ask about specific relations.

Example:

```text
P57 director:
- Who directed {film}?
- What person directed {film}?

P123 publisher:
- Who published {book}?
- Which publisher released {book}?
```

### Strengths

- Useful relation paraphrase bank.
- Cheap to implement.
- Directly helps the Wikidata-first route.

### Weaknesses

- Old KBQA datasets may sound less natural than SimpleQA.
- Mapping Freebase/DBpedia/Wikidata relations can be noisy.

### Small tips

- Use mined patterns as candidates, not final questions.
- Filter patterns manually for top relation families.
- Combine with LLM rewrite.

## Route 17: DBpedia / Infobox Ontology Route

### Idea

Use DBpedia or DBpedia-like extracted infobox facts as another structured source.

### Strengths

- Close to Wikipedia infobox structure.
- Useful schema comparison against Wikidata.
- May simplify some relation mappings.

### Weaknesses

- Coverage and freshness may vary.
- Ecosystem may be less convenient than Wikidata.
- Still requires normalization.

### Small tips

- Treat DBpedia as a supplementary source.
- Use it to validate infobox-property mappings.
- Do not make it the only source unless it proves easier.

## Route 18: OpenAlex / Crossref Academic Metadata Route

### Idea

Generate QA from academic metadata.

Question types:

- Who is the first author of paper X?
- In which journal was paper X published?
- What is the DOI of paper X?
- Which institution is associated with author X in paper Y?

### Strengths

- Strong long-tail potential.
- API-friendly.
- Stable metadata.

### Weaknesses

- Paper titles may be very long.
- Some questions may feel database-like.
- Author name ambiguity.

### Small tips

- Use short paper titles only.
- Prefer older papers.
- Avoid questions where the answer is a long author list.
- Use DOI/title as evidence metadata.

## Route 19: MusicBrainz Route

### Idea

Use music metadata.

Question types:

- Which label released album X?
- Which artist recorded track X?
- When was album X released?

### Strengths

- Excellent long-tail coverage.
- Good for music domain diversity.

### Weaknesses

- Multiple releases and editions create ambiguity.
- Need careful normalization.

### Small tips

- Start with albums or recordings with one official release.
- Avoid questions where many releases have different dates or labels.
- Use disambiguation comments when available.

## Route 20: Open Library / Book Metadata Route

### Idea

Use book metadata from Open Library, WorldCat-like sources, or other bibliographic databases.

Question types:

- Who illustrated book X?
- Which publisher released book X?
- What is the original language of book X?

### Strengths

- Good for humanities and literature.
- Long-tail potential.
- Stable historical facts.

### Weaknesses

- Editions and translations cause ambiguity.
- Publisher can differ by edition.

### Small tips

- Prefer first edition only when clearly available.
- Include edition/year context if needed.
- Reject books with conflicting metadata.

## Route 21: Museum Collection Metadata Route

### Idea

Use open museum collection APIs.

Possible sources:

- Metropolitan Museum
- Rijksmuseum
- Smithsonian
- British Museum
- Other public museum collections

Question types:

- Which artist created object X?
- What medium was used for object X?
- Which museum holds object X?
- What is the accession number of object X?

### Strengths

- Very strong long-tail potential.
- Good art/culture diversity.
- Usually auditable.

### Weaknesses

- Object titles can be generic or duplicated.
- Some fields may be too database-like.

### Small tips

- Add museum name or accession number for disambiguation.
- Prefer objects with distinctive titles.
- Avoid overly obscure accession-number-only questions unless needed.

## Route 22: Government / Heritage Registry Route

### Idea

Use official registries for buildings, monuments, heritage sites, protected areas, etc.

Question types:

- In which municipality is heritage site X located?
- Which architect designed building X?
- In what year was site X listed?

### Strengths

- Stable.
- Auditable.
- Good long-tail source.

### Weaknesses

- Data formats differ across countries.
- Some registries are hard to scrape.

### Small tips

- Start with one or two clean registries.
- Store source URL and record ID.
- Prefer fields with short answers.

## Route 23: Sports Historical Archive Route

### Idea

Generate questions from historical sports records.

Question types:

- Which team won the X final in 1987?
- Which venue hosted the X final?
- Who coached team X during season Y?

### Strengths

- Natural and familiar.
- Good for long-tail if using lower-profile leagues/events.

### Weaknesses

- Popular sports facts may be too head-heavy.
- Some stats are dynamic or disputed.
- Data licensing may be an issue.

### Small tips

- Focus on completed historical events.
- Avoid career totals and current teams.
- Use less popular competitions for long-tail coverage.

## Route 24: Taxonomy / Biodiversity Route

### Idea

Use species and taxonomy databases.

Question types:

- Who first described species X?
- In which family is species X classified?
- What is the type locality of species X?

### Strengths

- Huge long-tail space.
- Good science diversity.
- Many stable facts.

### Weaknesses

- Taxonomy changes over time.
- Synonyms and reclassification can cause answer instability.
- Questions can become too specialized.

### Small tips

- Prefer authorship and original description facts.
- Be careful with current classification.
- Store taxon IDs and synonyms.

## Route 25: Search Leakage Verifier

### Idea

Use search API to check whether the answer is too easily exposed.

Flow:

```text
search exact question
search subject + relation phrase
search subject + answer
inspect top-k titles/snippets
flag answer leakage
```

### Strengths

- Practical long-tail proxy.
- Easy to add after generation.
- Useful across all routes.

### Weaknesses

- Search APIs differ.
- Snippets can be unstable.
- Search absence is not proof of long-tail.

### Small tips

- Use it as a score, not a binary truth.
- Save snippets for audit.
- Check both exact question and subject-answer co-occurrence.
- Penalize candidates where answer appears in top results.

## Route 26: Search-style Naturalization

### Idea

Use search query style to make questions more natural.

Examples:

- who played X in Y
- what channel was X on
- who illustrated X book
- where was X filmed

### Strengths

- Helps mimic real user wording.
- Reduces stiff KG-style phrasing.

### Weaknesses

- Search-style queries may be ungrammatical.
- Needs cleanup for final dataset.

### Small tips

- Use as rewrite inspiration, not final output.
- Pair with grammar and answer-preservation checks.

## Route 27: Search Result Diversity Ambiguity Check

### Idea

Search the subject name and see whether results refer to multiple entities.

### Strengths

- Good proxy for ambiguity.
- Helps decide whether descriptors are needed.

### Weaknesses

- Search result diversity can be noisy.
- Obscure entities may have no results.

### Small tips

- If multiple entities appear, add descriptor from lead sentence.
- If ambiguity remains, discard.
- Useful before final question rewrite.

## Route 28: Entity Descriptor + Single Fact

### Idea

Generate questions that look slightly composed but still ask one factual answer.

Example:

```text
Which actor played the title character in the film directed by X?
```

Internally:

```text
X directed film Y.
Y has title character actor Z.
Answer: Z.
```

### Strengths

- More natural and challenging.
- Still answerable if uniqueness is verified.

### Weaknesses

- More complex validation.
- May drift away from SimpleQA simplicity.

### Small tips

- Keep this as a hard subset.
- Require strict uniqueness.
- Avoid long chains.

## Route 29: List Intersection Route

### Idea

Ask about the unique item satisfying two constraints.

Example:

```text
Which film directed by X was nominated for award Y?
```

### Strengths

- Natural composed factual questions.
- Good difficulty control.

### Weaknesses

- Uniqueness is critical.
- Easy to create ambiguous questions.

### Small tips

- Always compute candidate set size.
- Keep only cases where exactly one answer exists.
- Store both constraints as evidence.

## Route 30: Temporal Qualifier Route

### Idea

Use historical time constraints to make questions specific and stable.

Examples:

- Who won the X Award in 2006?
- Which company published X in 1984?
- Which venue hosted the X final in 1997?

### Strengths

- Natural.
- Useful for disambiguation.
- Stable if historical.

### Weaknesses

- Too many year-based questions can feel repetitive.
- Recent years can create cutoff issues.

### Small tips

- Use years as context, not as the only trick.
- Avoid very recent events by default.
- Make cutoff year configurable.

---

# 7. Recommended Relation Families

Organize generation by human-natural relation families, not only by Wikidata property IDs.

## 7.1 Creative Works

Useful relations:

- director
- screenwriter
- producer
- composer
- cinematographer
- publisher
- illustrator
- translator
- original language
- record label
- album producer
- original network

Example questions:

- Who directed the film X?
- Which publisher released the novel X?
- What network originally aired the series X?

## 7.2 Awards and Honors

Useful relations:

- winner
- recipient
- award category
- host
- nominated work
- ceremony venue

Example questions:

- Who won the X Award in 2006?
- Which work won the X category at Y?

## 7.3 Places and Buildings

Useful relations:

- architect
- location
- opened
- heritage designation
- named after
- original owner

Example questions:

- Who designed the building X?
- In which city is X located?

## 7.4 Organizations

Useful relations:

- founder
- headquarters
- parent organization
- predecessor
- successor
- official publication

Example questions:

- Who founded organization X?
- Where is organization X headquartered?

## 7.5 Academic and Scientific Metadata

Useful relations:

- first author
- journal
- institution
- doctoral advisor
- taxon author
- discoverer
- named after

Example questions:

- Who first described species X?
- In which journal was paper X published?

## 7.6 Sports

Useful relations:

- winner
- venue
- coach
- team in season
- medalist
- competition host

Example questions:

- Which venue hosted the X final?
- Who coached team X during the Y season?

---

# 8. Recommended MVP

Start with a small multi-generator prototype.

## 8.1 MVP Generators

Use these first:

1. Wikipedia infobox-first.
2. Wikipedia table/list-first.
3. Wikidata-first WDQS-light.
4. Wikidata statement -> Wikipedia evidence alignment, simple exact-match version.
5. Existing QA pattern transfer for natural question templates.

## 8.2 MVP Validators

Use these first:

1. Answer appears in evidence.
2. Question has one short answer.
3. No current/dynamic wording.
4. Search top-k does not directly reveal answer.
5. Subject ambiguity check.
6. LLM judge for final question naturalness and answer support.

## 8.3 MVP Output

Generate 20 candidates per route.

For each candidate, save:

- question
- answer
- aliases
- route
- source URL
- evidence text
- subject
- relation
- long-tail scores
- validation flags

Small tip:

The first goal is not to generate thousands of questions.

The first goal is to compare routes by:

- yield
- naturalness
- answer reliability
- long-tailness
- implementation cost

---

# 9. Five Small Experiments to Run First

## Experiment 1: Infobox-first Pilot

Generate 20 questions from:

- films
- books
- albums
- buildings
- TV series

Compare naturalness and validation difficulty.

## Experiment 2: Table/List-first Pilot

Generate 20 questions from:

- award winner tables
- episode lists
- station lists
- heritage lists
- sports result tables

Check whether the questions sound too table-like.

## Experiment 3: Wikidata-Wikipedia Alignment Pilot

Use a small set of Wikidata statements.

Start with exact object label matching in Wikipedia text.

Measure:

- alignment success rate
- answer support quality
- question naturalness

## Experiment 4: Rewrite Comparison

For the same facts, generate:

- template question
- NQ-style rewritten question
- SimpleQA-style rewritten question

Compare which style best matches SimpleQA-like QA.

## Experiment 5: Search Leakage Filter

For 100 candidate questions:

- search exact question
- search subject + answer
- search subject + relation phrase

Record whether the answer appears in top-k titles/snippets.

Use this to design the long-tail score.

---

# 10. Implementation Suggestions for Codex

## 10.1 Modular Generator Design

Use an interface like:

```python
class CandidateGenerator:
    def generate(self, limit: int) -> list[QACandidate]:
        ...
```

Possible generator classes:

- WikidataLightGenerator
- WikipediaInfoboxGenerator
- WikipediaTableGenerator
- WikipediaListPageGenerator
- WikipediaClaimGenerator
- WikidataWikipediaAlignmentGenerator
- OpenAlexGenerator
- MusicBrainzGenerator
- MuseumCollectionGenerator

## 10.2 Shared Validator Design

Use separate validators:

- StabilityValidator
- EvidenceValidator
- AmbiguityValidator
- LongTailValidator
- AnswerUniquenessValidator
- NaturalnessJudge
- Deduplicator

Small tip:

Do not bake validation into each generator too deeply.  
Generators should generate; validators should filter.

## 10.3 Config-driven Design

Use config files for:

```yaml
cutoff_year: 2024
search_top_k: 10

allowed_domains:
  - film
  - book
  - album
  - building
  - award
  - science
  - sports

relation_families:
  film:
    - director
    - composer
    - original_network
  book:
    - author
    - illustrator
    - publisher

longtail_thresholds:
  max_pageviews: 1000
  max_sitelinks: 20
```

Small tips:

- Make the cutoff year configurable.
- Make domain quotas configurable.
- Keep relation-family definitions outside code where possible.

## 10.4 Save Intermediate Artifacts

Save:

- `raw_candidates.jsonl`
- `validated_candidates.jsonl`
- `rejected_candidates.jsonl`
- `final_questions.jsonl`
- `audit_samples.jsonl`

For rejected candidates, save rejection reasons.

Example:

```json
{
  "question": "...",
  "answer": "...",
  "rejected_by": ["search_leakage", "ambiguous_subject"],
  "reason": "Answer appeared in 7 of top 10 snippets."
}
```

Small tip:

Rejection analysis will help improve the pipeline much faster than only inspecting final outputs.

## 10.5 Keep Deterministic and LLM Components Separate

Deterministic components:

- API fetching
- parsing
- string matching
- normalization
- search leakage
- deduplication
- schema validation

LLM components:

- claim extraction
- question rewrite
- entailment judgment
- naturalness judgment
- ambiguity judgment

Small tips:

- Always store the deterministic pre-rewrite question.
- This helps debug whether the LLM rewrite changed meaning.
- Log prompts and model outputs for every LLM call.

---

# 11. Main Risks and Mitigations

## Risk 1: Questions Become Too Template-like

Mitigation:

- Use Wikipedia descriptors.
- Use NQ/SimpleQA pattern transfer.
- Use rewrite pass.
- Use naturalness judge.

## Risk 2: Questions Become Ambiguous

Mitigation:

- Use subject descriptors.
- Search ambiguity check.
- Answer uniqueness validation.
- Reject short generic titles.

## Risk 3: Answers Are Unstable

Mitigation:

- Avoid current status.
- Prefer historical facts.
- Reject career totals and live statistics.
- Use configurable cutoff year.

## Risk 4: Evidence Does Not Actually Support the Answer

Mitigation:

- Require answer string or alias in evidence.
- Use entailment judge.
- Cross-check infobox/body/Wikidata.
- Store evidence with each candidate.

## Risk 5: Long-tail Filter Becomes Too Strict

Mitigation:

- Use long-tail score instead of binary rule.
- Keep borderline candidates for manual review.
- Combine multiple weak signals.

## Risk 6: Pipeline Overuses Wikidata and Loses Naturalness

Mitigation:

- Add Wikipedia-first and table/list-first routes.
- Use Wikidata as answer anchor, not always as question source.

## Risk 7: Search-first Generation Becomes Uncontrollable

Mitigation:

- Do not use search-first as the main generation route initially.
- Use search mainly for leakage, ambiguity, and style signals.

---

# 12. Recommended Final Strategy

The most practical strategy is:

```text
Wikipedia infobox/table/list-first candidate generation
    + Wikidata or page evidence validation
    + SimpleQA/NQ-style rewrite
    + search top-k leakage filter
    + ambiguity and stability checks
```

Wikidata-first should remain as a reliable baseline.

Search-first should not be the main route at the beginning.  
Search is more useful as a verifier and filter.

External structured sources should be added later to improve domain diversity.

---

# 13. Priority Ranking

## Highest Priority

1. Wikipedia infobox-first.
2. Wikipedia table/list-first.
3. Wikidata-Wikipedia evidence alignment, simple version.
4. Search leakage verifier.
5. Existing QA pattern transfer.

## Medium Priority

6. Wikipedia-first atomic claim extraction.
7. Category-first domain balancing.
8. Wikidata qualifiers-first.
9. Infobox + table cross-check.
10. Lead-sentence descriptor route.

## Later Extensions

11. OpenAlex / Crossref.
12. MusicBrainz.
13. Museum collections.
14. Government / heritage registries.
15. Biodiversity databases.
16. Sports historical archives.
17. Light composed / intersection questions.

---

# 14. Short Version for Planning

Build a multi-route candidate-generation system.

Do not choose only one route.

Use these routes first:

1. Wikipedia infobox-first.
2. Wikipedia table/list-first.
3. Wikidata-light single-hop.
4. Wikidata statement -> Wikipedia evidence alignment.
5. QA-pattern-based natural rewrite.
6. Search-based long-tail leakage filter.

The core system should optimize for:

- naturalness
- stable single answer
- evidence support
- long-tailness
- auditability
- automatic scoring

The best near-term direction is:

```text
Generate candidates from Wikipedia semi-structured content,
anchor or validate answers with Wikidata/page evidence,
rewrite into SimpleQA-like questions,
then filter using search leakage and ambiguity checks.
```
