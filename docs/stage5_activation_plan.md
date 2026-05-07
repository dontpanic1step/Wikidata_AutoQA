# Stage 5 Activation Plan

## Goal

Turn the 102-template blueprint catalog into a safe multi-domain generation pipeline while preserving the non-negotiable rules:

- every accepted QA pair must be time-invariant,
- every harvested subject or event must have a relevant date not earlier than `target_time`,
- question text must not contain years, dates, month names, or temporal expressions,
- high precision is more important than high recall.

## Activation Principle

The blueprint catalog is broader than the current runtime on purpose. Stage 5 should not activate all templates at once.

Instead, templates should be activated in waves based on:

1. reliable date harvesting,
2. low ambiguity risk,
3. stable target property semantics,
4. low need for composed reasoning,
5. low answer leakage risk,
6. manageable answer-type coverage.

## Template Tiers

### Tier A: Activate First

These templates are the best candidates for the first multi-domain runtime expansion because they are mostly single-fact, recent-subject-safe, and already close to the current validator model.

1. `film_director`
2. `novel_author`
3. `book_original_language`
4. `video_game_developer`
5. `software_developer`
6. `scholarly_article_journal`
7. `artwork_creator`
8. `album_performer`
9. `building_architect`
10. `airport_country`
11. `museum_country`
12. `company_founder`
13. `book_publisher`
14. `novella_original_language`
15. `film_screenwriter`
16. `film_based_on`
17. `tv_series_creator`
18. `documentary_narrator`
19. `music_video_director`
20. `album_label`
21. `animation_studio`
22. `product_manufacturer`
23. `company_headquarters_country`
24. `new_park_country`
25. `new_airport_serves_city`
26. `law_jurisdiction`
27. `law_legislature`
28. `spacecraft_operator`
29. `device_manufacturer`
30. `beverage_manufacturer`

### Tier B: Activate After Additional Validators

These are still strong candidates, but they need more property-specific validation or a tighter ambiguity policy.

1. `podcast_host`
2. `comic_writer`
3. `poetry_collection_author`
4. `essay_collection_author`
5. `literary_magazine_country`
6. `festival_host_city`
7. `award_conferred_by`
8. `event_venue`
9. `temple_country`
10. `philosophy_book_author`
11. `tournament_host_country`
12. `stadium_architect`
13. `sports_venue_city`
14. `competition_venue`
15. `degree_granting_university`
16. `school_founder`
17. `curriculum_author`
18. `textbook_publisher`
19. `math_textbook_author`
20. `paper_author_count`
21. `math_paper_journal`
22. `chemistry_article_journal`
23. `physics_book_author`
24. `instrument_manufacturer`
25. `vaccine_developer`
26. `hospital_country`
27. `clinical_guideline_author`
28. `medical_device_manufacturer`
29. `satellite_manufacturer`
30. `rail_station_country`

### Tier C: Activate After Compositional Multi-Hop Provenance Support

These require deterministic multi-claim composition, explicit reasoning-path metadata, or richer answer typing.

1. `wedding_age_gap`
2. `marriage_spouse`
3. `person_first_degree_university`
4. `religious_leader_successor`
5. `graduate_before_employer`
6. `environmental_project_lead`
7. `ordinal_country_president`
8. `space_mission_launch_site`
9. `what_active_ingredient_medicine`
10. `which_university_before_employer`
11. `ordinal_tournament_winner`
12. `ordinal_religious_leader`
13. `ordinal_university_chancellor`
14. `ordinal_company_ceo`
15. `ordinal_space_mission_commander`

### Tier D: Activate After Date-Answer Support

These are valid under the framework, but they require date-granularity-aware grading and answer normalization.

1. `benchmark_release_date`
2. `product_release_date`
3. `terminal_opening_date`

## Validator Work Needed

Before Tier A can be run at scale, the pipeline should add:

1. per-template activation flags,
2. answer-type balancing,
3. question-family quotas,
4. topic quotas,
5. subject-property deduplication across templates.

Before Tier B:

1. stronger location-property validation,
2. improved answer leakage detection for organization and place names,
3. better same-medium ambiguity resolution.

Before Tier C:

1. deterministic fact-join execution,
2. ordering constraints such as "before working at Google",
3. ordinal-position extraction and validation with dynamic `{ordinal}` binding,
4. numeric-answer stability checks,
5. stronger provenance metadata for every joined claim,
6. connectedness validation so every accepted example truly requires all hops,
7. shortcut rejection for questions answerable without the bridge step.

Before Tier D:

1. date-answer normalization,
2. answer-granularity-aware grading,
3. exact date formatting policy.

## Suggested Target Mix for a 1K-Scale Dataset

This is a good first balancing target for about 1,000 final questions:

- 55% Tier A
- 25% Tier B
- 15% Tier C
- 5% Tier D

And by answer type:

- 30% Person
- 20% Organization
- 20% Place
- 10% Language
- 10% Work / Other entity
- 10% Number
- 5% Date

These are not hard rules, but they are useful defaults to avoid a person-heavy or `Who ...`-heavy dataset.

## Number Policy

Stage 5 should treat number templates with a separate safety policy:

- reject cumulative or live counts,
- allow one-time event counts,
- allow fixed structural counts,
- require deterministic counting logic per template family.
