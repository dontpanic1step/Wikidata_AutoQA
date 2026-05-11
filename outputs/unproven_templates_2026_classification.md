# 2026 Unproven Template Classification

- Target time: `2026`
- Accepted: `57`
- Rejected only: `4`
- Not implemented: `39`
- Implemented but empty at 2026: `61`
- Timeout or rate limited: `20`

## Bucket Definitions

- `not_implemented`: template produced `no_result` and made `0` Wikidata requests.
- `implemented_but_empty`: template produced `no_result` after making at least one Wikidata request.
- `timeout_or_rate_limited`: template ended with a runtime/API error such as `TimeoutError` or `HTTP 429`.
- `rejected_only`: template harvested candidates, but every candidate was rejected by the current validators.

## Rejected Only

- `competition_venue`: `unknown`
- `festival_host_city`: `unknown`
- `monastery_country`: `unknown`
- `tournament_host_country`: `unknown`

## Not Implemented

- `acquisition_purchase_price`
- `album_track_count`
- `biology_article_author_count`
- `bridge_span_count`
- `company_founder_count`
- `company_that_developed_benchmark_founder`
- `company_that_released_product_founder`
- `dataset_language_count`
- `festival_day_count`
- `footballer_goals_in_ordinal_tournament`
- `graduate_before_employer`
- `guideline_author_count`
- `marriage_spouse`
- `math_article_author_count`
- `medicine_ingredient_count`
- `ordinal_company_ceo`
- `ordinal_country_president`
- `ordinal_country_prime_minister`
- `ordinal_film_in_series_director`
- `ordinal_religious_leader`
- `ordinal_space_mission_commander`
- `ordinal_tournament_host_city`
- `ordinal_university_chancellor`
- `ordinal_volume_author`
- `paper_author_count`
- `patent_inventor_count`
- `project_partner_count`
- `religious_leader_successor`
- `report_author_count`
- `rover_wheel_count`
- `spacecraft_crew_count`
- `spacecraft_payload_count`
- `sports_event_host_count`
- `startup_founder_count`
- `story_collection_story_count`
- `terminal_operator_country`
- `textbook_editor_count`
- `treaty_signatory_count`
- `tv_series_source_work_author`

## Implemented But Empty At 2026

- `aircraft_manufacturer`
- `airport_operator`
- `beverage_manufacturer`
- `biobank_country`
- `bridge_architect`
- `chip_architecture_designer`
- `church_country`
- `clinical_guideline_author`
- `clinical_guideline_publisher`
- `club_founder`
- `constitution_jurisdiction`
- `crop_variety_developer`
- `curriculum_author`
- `database_system_developer`
- `degree_granting_university`
- `documentary_narrator`
- `encyclical_author`
- `environmental_project_lead`
- `exchange_operator`
- `film_release_date`
- `genome_project_lead_org`
- `heritage_site_country`
- `instrument_manufacturer`
- `kitchen_appliance_manufacturer`
- `law_legislature`
- `lighthouse_country`
- `math_article_main_subject`
- `medical_device_manufacturer`
- `medicine_active_ingredient`
- `museum_founder`
- `music_video_director`
- `new_airport_serves_city`
- `novella_original_language`
- `opera_composer`
- `operating_system_developer`
- `podcast_host`
- `poem_author`
- `poetry_collection_author`
- `policy_department`
- `port_operator`
- `programming_language_designer`
- `religious_text_language`
- `restaurant_founder`
- `robot_creator`
- `satellite_manufacturer`
- `satellite_operator`
- `school_founder`
- `scientific_instrument_operator`
- `space_mission_launch_site`
- `space_telescope_operator`
- `spacecraft_manufacturer`
- `spacecraft_operator`
- `species_described_by`
- `sports_league_operator`
- `stock_exchange_country`
- `temple_country`
- `theater_location`
- `train_manufacturer`
- `treaty_signatory_country`
- `vaccine_developer`
- `vehicle_designer`

## Timeout Or Rate Limited

- `ai_model_developer`: `error:TimeoutError`; `The read operation timed out`
- `battery_manufacturer`: `error:TimeoutError`; `The read operation timed out`
- `biography_birth_place_recent_subject`: `error:TimeoutError`; `The read operation timed out`
- `biography_native_language_recent_subject`: `error:TimeoutError`; `The read operation timed out`
- `biography_notable_work_recent_subject`: `error:TimeoutError`; `The read operation timed out`
- `biography_occupation_recent_subject`: `error:TimeoutError`; `The read operation timed out`
- `biography_place_of_death_recent_subject`: `error:TimeoutError`; `The read operation timed out`
- `bioinformatics_software_developer`: `error:TimeoutError`; `The read operation timed out`
- `comic_writer`: `error:HTTPError`; `HTTP Error 429: Too Many Requests`
- `engine_designer`: `error:TimeoutError`; `The read operation timed out`
- `film_based_on`: `error:HTTPError`; `HTTP Error 429: Too Many Requests`
- `math_software_developer`: `error:TimeoutError`; `The read operation timed out`
- `person_birth_date`: `error:TimeoutError`; `The read operation timed out`
- `person_death_date`: `error:TimeoutError`; `The read operation timed out`
- `person_first_degree_university`: `error:TimeoutError`; `The read operation timed out`
- `product_manufacturer`: `error:TimeoutError`; `The read operation timed out`
- `product_release_date`: `error:TimeoutError`; `The read operation timed out`
- `software_license`: `error:TimeoutError`; `The read operation timed out`
- `species_parent_taxon`: `error:TimeoutError`; `The read operation timed out`
- `wedding_age_gap`: `error:TimeoutError`; `The read operation timed out`
