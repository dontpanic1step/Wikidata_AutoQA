# Trade_off_examples

This document collects design trade-off cases for later review. These are not necessarily bugs.

## Naomi C Futhey: first degree university

Main trade-off: long-tail people are useful because their facts are less likely to be obvious or memorized, but their Wikidata records may be incomplete. This can make a template sound like it asks for a full life-history fact, while the code only sees the partial structured data available in Wikidata.

Template key: `person_first_degree_university`

Question:

```text
From which university did Naomi C Futhey receive a first degree?
```

Accepted answer:

```text
University of British Columbia
```

The selected Wikidata statement was Naomi C Futhey's `educated at` claim for the University of British Columbia. That statement has:

- academic degree: Doctor of Medicine, `Q913404`
- end time: `2026-04-01`

### English wording issue

In English, "first degree" usually means a first university degree, often an undergraduate degree such as a bachelor's degree. It does not normally mean only a PhD or master's degree.

So the question wording is risky. A reader may think it asks where Naomi C Futhey earned her undergraduate degree. The pipeline does not check that.

### What the current code does

The template asks:

```text
From which university did {descriptor} receive a first degree?
```

The SPARQL looks for people with an `educated at` statement that has:

```sparql
?person p:P69 ?stmt.
?stmt ps:P69 ?university;
      pq:P512 ?degree;
      pq:P582 ?end.
?university wdt:P31/wdt:P279* wd:Q3918.
```

This means it checks for:

- the person has an education statement, `P69`
- some academic degree qualifier, `P512`
- an end-time qualifier, `P582`
- a university or subclass of university

It does not check that the degree is a PhD. It also does not check that the degree is a master's degree, bachelor's degree, undergraduate degree, medical degree, or any other specific level.

After that, local code sorts eligible education records by end date and picks the earliest unique one:

```text
earliest_unique_degree_completion
```

This means:

- if one eligible statement has the earliest end date, it is selected
- if two or more statements share the earliest end date, the candidate is rejected
- if an education statement lacks `P512` or `P582`, it is ignored
- degree level is not checked

### Why the Naomi case matters

The problem is probably incomplete Wikidata data. For less well-known people, Wikidata may not record every education experience.

In this case, public search snippets mention undergraduate research or a Bachelor of Science context associated with McGill. The pipeline selected UBC because that was the earliest eligible Wikidata education statement with both a degree qualifier and an end date.

So the question sounds like it asks for the person's first university degree in normal English. But the code is really answering:

```text
What is the earliest uniquely dated Wikidata education statement for this person that has any academic degree qualifier and points to a university?
```

This is the trade-off: long-tail examples are useful, but their Wikidata records may be too incomplete for templates that depend on full life history.

### Local references

- `src/wikidata_simpleqa/domain_templates.py`: `person_first_degree_university`
- `src/wikidata_simpleqa/composed_harvester.py`: `_harvest_person_first_degree_university`
- `outputs/stage5b_pilot_accepted.jsonl`: Naomi C Futhey accepted artifact
- `outputs/naomi_c_futhey_walkthrough.md`: search and grading walkthrough
