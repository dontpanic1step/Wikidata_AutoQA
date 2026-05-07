# Template Catalog Review

## Definitions

- `activation_status`: where the template sits in the rollout lifecycle (`active`, `multi_hop_pilot`, `date_answer_pilot`, `blueprint`).
- `evidence_status`: whether the template has already produced an accepted example in a recorded pilot run.
- `temporal_mode`: `atemporal` for normal SimpleQA-style questions, `time_related_join` for compositional target-time joins, and `date_answer` for explicit date questions.

## Headline Stats

- Total templates: `199`
- Number-answer templates: `24`
- Date-answer templates: `9`
- Time-related templates (including date-answer): `20`

## Status Axis

| Activation Status | Count |
|---|---:|
| active | 12 |
| blueprint | 181 |
| date_answer_pilot | 3 |
| multi_hop_pilot | 3 |

## Evidence Axis

| Evidence Status | Count |
|---|---:|
| not_yet_proven | 181 |
| proven_in_runs | 18 |

## Domain Axis

| Topic | Count |
|---|---:|
| Architecture and Transportation | 12 |
| Arts and Media | 21 |
| Computer Science and AI | 14 |
| Earth, Environment, and Space | 11 |
| Economy and Business | 13 |
| Education | 9 |
| Engineering and Technology | 12 |
| Food, Agriculture, and Daily Life | 5 |
| Geography | 7 |
| Language and Literature | 12 |
| Life Sciences | 8 |
| Mathematics | 7 |
| Medicine and Health | 9 |
| People | 11 |
| Philosophy and Religion | 8 |
| Physical Sciences | 9 |
| Politics and Law | 10 |
| Society and Culture | 9 |
| Sports and Recreation | 12 |

## Answer Type Axis

| Answer Type | Count |
|---|---:|
| Date | 9 |
| Entity | 1 |
| Language | 4 |
| Number | 24 |
| Organization | 55 |
| Other | 7 |
| Person | 57 |
| Place | 40 |
| Work | 2 |

## Answer Format Axis

| Answer Format | Count |
|---|---:|
| date | 9 |
| entity | 166 |
| number | 24 |

## Temporal Axis

| Temporal Mode | Count |
|---|---:|
| atemporal | 179 |
| date_answer | 9 |
| time_related_join | 11 |

## Full Catalog

| Domain | Activation Status | Evidence Status | Topic | Answer Type | Answer Format | Temporal Mode | Reasoning Style | Subject Type | Date PID | Target PID | Runs | Canonical Template |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| film_director | active | proven_in_runs | Arts and Media | Person | entity | atemporal | single_fact | film (Q11424) | P577 | P57 | stage5a_single_fact,stage5b_pilot | Who directed the {subject_kind} {descriptor}? |
| novel_author | active | proven_in_runs | Language and Literature | Person | entity | atemporal | single_fact | novel (Q8261) | P577 | P50 | stage5a_single_fact,stage5b_pilot | Who wrote the {subject_kind} {descriptor}? |
| book_original_language | active | proven_in_runs | Language and Literature | Language | entity | atemporal | single_fact | book (Q571) | P577 | P364 | stage5a_single_fact,stage5b_pilot | What language was the {subject_kind} {descriptor} originally written in? |
| video_game_developer | active | proven_in_runs | Computer Science and AI | Organization | entity | atemporal | single_fact | video game (Q7889) | P577 | P178 | stage5a_single_fact,stage5b_pilot | Which company developed the {subject_kind} {descriptor}? |
| software_developer | active | proven_in_runs | Computer Science and AI | Organization | entity | atemporal | single_fact | software (Q7397) | P577 | P178 | stage5a_single_fact,stage5b_pilot | Which company developed the {subject_kind} {descriptor}? |
| scholarly_article_journal | active | proven_in_runs | Physical Sciences | Organization | entity | atemporal | single_fact | scholarly article (Q13442814) | P577 | P1433 | stage5a_single_fact,stage5b_pilot | In which journal was the {subject_kind} {descriptor} published? |
| artwork_creator | active | proven_in_runs | Arts and Media | Person | entity | atemporal | single_fact | artwork (Q838948) | P571 | P170 | stage5a_single_fact,stage5b_pilot | Who created the {subject_kind} {descriptor}? |
| album_performer | active | proven_in_runs | Arts and Media | Person | entity | atemporal | single_fact | album (Q482994) | P577 | P175 | stage5a_single_fact,stage5b_pilot | Which artist released the {subject_kind} {descriptor}? |
| building_architect | active | proven_in_runs | Architecture and Transportation | Person | entity | atemporal | single_fact | building (Q41176) | P571 | P84 | stage5a_single_fact,stage5b_pilot | Who designed the {subject_kind} {descriptor}? |
| rail_station_country | active | proven_in_runs | Architecture and Transportation | Place | entity | atemporal | single_fact | railway station (Q55488) | P571 | P17 | stage5a_single_fact,stage5b_pilot | In which country is the {subject_kind} {descriptor} located? |
| museum_country | active | proven_in_runs | Society and Culture | Place | entity | atemporal | single_fact | museum (Q33506) | P571 | P17 | stage5a_single_fact,stage5b_pilot | In which country is the {subject_kind} {descriptor} located? |
| company_founder | active | proven_in_runs | Economy and Business | Person | entity | atemporal | single_fact | company (Q783794) | P571 | P112 | stage5a_single_fact,stage5b_pilot | Who founded the {subject_kind} {descriptor}? |
| ordinal_tournament_winner | multi_hop_pilot | proven_in_runs | Sports and Recreation | Entity | entity | time_related_join | multi_hop_ordinal | tournament edition (Q132241) | P585 | P1346 | stage5b_pilot | Who won the {ordinal} edition of {descriptor}? |
| person_first_degree_university | multi_hop_pilot | proven_in_runs | People | Organization | entity | time_related_join | multi_hop_join | human (Q5) | P69 | P69 | stage5b_pilot | From which university did {descriptor} receive a first degree? |
| film_source_work_author | multi_hop_pilot | proven_in_runs | Arts and Media | Person | entity | time_related_join | multi_hop_join | film (Q11424) | P577 | P50 | stage5b_pilot | Who wrote the work that the film {descriptor} was based on? |
| benchmark_release_date | date_answer_pilot | proven_in_runs | Computer Science and AI | Date | date | date_answer | single_fact | dataset (Q1172284) | P577 | P577 | stage5b_pilot | On what day, month, and year was the benchmark {descriptor} released? |
| product_release_date | date_answer_pilot | proven_in_runs | Engineering and Technology | Date | date | date_answer | single_fact | product (Q2424752) | P577 | P577 | stage5b_pilot | On what day, month, and year was the product {descriptor} released? |
| terminal_opening_date | date_answer_pilot | proven_in_runs | Architecture and Transportation | Date | date | date_answer | single_fact | terminal (Q55488) | P571 | P571 | stage5b_pilot | On what day, month, and year did the terminal {descriptor} open? |
| wedding_age_gap | blueprint | not_yet_proven | People | Number | number | atemporal | multi_hop_join | wedding (Q27020041) | P585 | P1534 |  | What was the age gap between the couple in {descriptor}? |
| marriage_spouse | blueprint | not_yet_proven | People | Person | entity | atemporal | multi_hop_join | marriage (Q171318) | P580 | P26 |  | Who married {descriptor}? |
| biography_birth_place_recent_subject | blueprint | not_yet_proven | People | Place | entity | atemporal | single_fact | human (Q5) | P569 | P19 |  | Where was {descriptor} born? |
| biography_native_language_recent_subject | blueprint | not_yet_proven | People | Language | entity | atemporal | single_fact | human (Q5) | P569 | P103 |  | What is the native language of {descriptor}? |
| person_first_degree_university | blueprint | not_yet_proven | People | Organization | entity | time_related_join | multi_hop_join | human (Q5) | P69 | P69 |  | From which university did {descriptor} receive a degree? |
| new_park_country | blueprint | not_yet_proven | Geography | Place | entity | atemporal | single_fact | park (Q22698) | P571 | P17 |  | In which country is the park {descriptor} located? |
| new_metro_station_country | blueprint | not_yet_proven | Geography | Place | entity | atemporal | single_fact | metro station (Q928830) | P571 | P17 |  | In which country is the metro station {descriptor} located? |
| new_bridge_crosses | blueprint | not_yet_proven | Geography | Place | entity | atemporal | single_fact | bridge (Q12280) | P571 | P177 |  | What body of water does the bridge {descriptor} cross? |
| new_airport_serves_city | blueprint | not_yet_proven | Geography | Place | entity | atemporal | single_fact | airport (Q1248784) | P571 | P131 |  | Which city includes the airport {descriptor}? |
| new_trail_country | blueprint | not_yet_proven | Geography | Place | entity | atemporal | single_fact | trail (Q179049) | P571 | P17 |  | In which country is the trail {descriptor} located? |
| law_jurisdiction | blueprint | not_yet_proven | Politics and Law | Place | entity | atemporal | single_fact | law (Q7748) | P577 | P1001 |  | In which jurisdiction does the law {descriptor} apply? |
| law_legislature | blueprint | not_yet_proven | Politics and Law | Organization | entity | atemporal | single_fact | law (Q7748) | P577 | P467 |  | Which legislature enacted the law {descriptor}? |
| treaty_signatory_country | blueprint | not_yet_proven | Politics and Law | Place | entity | atemporal | single_fact | treaty (Q131569) | P577 | P17 |  | Which country is associated with the treaty {descriptor}? |
| court_case_court | blueprint | not_yet_proven | Politics and Law | Organization | entity | atemporal | single_fact | legal case (Q2334719) | P585 | P1591 |  | Which court decided the case {descriptor}? |
| policy_department | blueprint | not_yet_proven | Politics and Law | Organization | entity | atemporal | single_fact | government policy (Q49884) | P577 | P749 |  | Which department issued the policy {descriptor}? |
| startup_founder | blueprint | not_yet_proven | Economy and Business | Person | entity | atemporal | single_fact | business (Q4830453) | P571 | P112 |  | Who founded the startup {descriptor}? |
| company_founded_country | blueprint | not_yet_proven | Economy and Business | Place | entity | atemporal | single_fact | company (Q783794) | P571 | P495 |  | In which country was the company {descriptor} founded? |
| product_manufacturer | blueprint | not_yet_proven | Economy and Business | Organization | entity | atemporal | single_fact | product (Q2424752) | P577 | P176 |  | Which company manufactured the product {descriptor}? |
| exchange_operator | blueprint | not_yet_proven | Economy and Business | Organization | entity | atemporal | single_fact | stock exchange (Q11654) | P571 | P137 |  | Which company operates the exchange {descriptor}? |
| festival_host_city | blueprint | not_yet_proven | Society and Culture | Place | entity | atemporal | single_fact | festival (Q132241) | P585 | P131 |  | Which city hosted {descriptor}? |
| museum_founder | blueprint | not_yet_proven | Society and Culture | Person | entity | atemporal | single_fact | museum (Q33506) | P571 | P112 |  | Who founded the museum {descriptor}? |
| award_conferred_by | blueprint | not_yet_proven | Society and Culture | Organization | entity | atemporal | single_fact | award (Q618779) | P571 | P1027 |  | Which organization confers the award {descriptor}? |
| exhibition_museum | blueprint | not_yet_proven | Society and Culture | Organization | entity | atemporal | single_fact | exhibition (Q464980) | P585 | P276 |  | Which museum hosted the exhibition {descriptor}? |
| event_venue | blueprint | not_yet_proven | Society and Culture | Place | entity | atemporal | single_fact | event (Q1656682) | P585 | P276 |  | Where was {descriptor} held? |
| religious_leader_successor | blueprint | not_yet_proven | Philosophy and Religion | Person | entity | atemporal | multi_hop_join | religious office (Q246434) | P580 | P156 |  | Who succeeded {descriptor}? |
| encyclical_author | blueprint | not_yet_proven | Philosophy and Religion | Person | entity | atemporal | single_fact | encyclical (Q240157) | P577 | P50 |  | Who wrote the encyclical {descriptor}? |
| religious_text_language | blueprint | not_yet_proven | Philosophy and Religion | Language | entity | atemporal | single_fact | religious text (Q179461) | P577 | P364 |  | What language was the religious text {descriptor} originally written in? |
| temple_country | blueprint | not_yet_proven | Philosophy and Religion | Place | entity | atemporal | single_fact | temple (Q44539) | P571 | P17 |  | In which country is the temple {descriptor} located? |
| philosophy_book_author | blueprint | not_yet_proven | Philosophy and Religion | Person | entity | atemporal | single_fact | book (Q571) | P577 | P50 |  | Who wrote the philosophy book {descriptor}? |
| poetry_collection_author | blueprint | not_yet_proven | Language and Literature | Person | entity | atemporal | single_fact | poetry collection (Q12106333) | P577 | P50 |  | Who wrote the poetry collection {descriptor}? |
| book_publisher | blueprint | not_yet_proven | Language and Literature | Organization | entity | atemporal | single_fact | book (Q571) | P577 | P123 |  | Which publisher released the book {descriptor}? |
| novella_original_language | blueprint | not_yet_proven | Language and Literature | Language | entity | atemporal | single_fact | novella (Q1238720) | P577 | P364 |  | What language was the novella {descriptor} originally written in? |
| essay_collection_author | blueprint | not_yet_proven | Language and Literature | Person | entity | atemporal | single_fact | essay collection (Q267628) | P577 | P50 |  | Who wrote the essay collection {descriptor}? |
| literary_magazine_country | blueprint | not_yet_proven | Language and Literature | Place | entity | atemporal | single_fact | magazine (Q41298) | P571 | P17 |  | In which country is the magazine {descriptor} based? |
| film_screenwriter | blueprint | not_yet_proven | Arts and Media | Person | entity | atemporal | single_fact | film (Q11424) | P577 | P58 |  | Who wrote the film {descriptor}? |
| film_based_on | blueprint | not_yet_proven | Arts and Media | Work | entity | atemporal | single_fact | film (Q11424) | P577 | P144 |  | What work was the film {descriptor} based on? |
| tv_series_creator | blueprint | not_yet_proven | Arts and Media | Person | entity | atemporal | single_fact | television series (Q5398426) | P577 | P170 |  | Who created the television series {descriptor}? |
| documentary_narrator | blueprint | not_yet_proven | Arts and Media | Person | entity | atemporal | single_fact | documentary film (Q93204) | P577 | P2438 |  | Who narrated the documentary {descriptor}? |
| music_video_director | blueprint | not_yet_proven | Arts and Media | Person | entity | atemporal | single_fact | music video (Q64100970) | P577 | P57 |  | Who directed the music video {descriptor}? |
| podcast_host | blueprint | not_yet_proven | Arts and Media | Person | entity | atemporal | single_fact | podcast (Q24634210) | P577 | P371 |  | Who hosts the podcast {descriptor}? |
| album_label | blueprint | not_yet_proven | Arts and Media | Organization | entity | atemporal | single_fact | album (Q482994) | P577 | P264 |  | Which label released the album {descriptor}? |
| comic_writer | blueprint | not_yet_proven | Arts and Media | Person | entity | atemporal | single_fact | comic (Q1004) | P577 | P50 |  | Who wrote the comic {descriptor}? |
| animation_studio | blueprint | not_yet_proven | Arts and Media | Organization | entity | atemporal | single_fact | animated film (Q202866) | P577 | P272 |  | Which studio produced the animated film {descriptor}? |
| theater_location | blueprint | not_yet_proven | Arts and Media | Place | entity | atemporal | single_fact | theatre (Q24354) | P571 | P17 |  | In which country is the theatre {descriptor} located? |
| tournament_host_country | blueprint | not_yet_proven | Sports and Recreation | Place | entity | atemporal | single_fact | tournament (Q132241) | P585 | P17 |  | Which country hosted {descriptor}? |
| stadium_architect | blueprint | not_yet_proven | Sports and Recreation | Person | entity | atemporal | single_fact | stadium (Q483110) | P571 | P84 |  | Who designed the stadium {descriptor}? |
| sports_venue_city | blueprint | not_yet_proven | Sports and Recreation | Place | entity | atemporal | single_fact | sports venue (Q1076486) | P571 | P131 |  | Which city includes the sports venue {descriptor}? |
| club_founder | blueprint | not_yet_proven | Sports and Recreation | Person | entity | atemporal | single_fact | sports club (Q847017) | P571 | P112 |  | Who founded the club {descriptor}? |
| competition_venue | blueprint | not_yet_proven | Sports and Recreation | Place | entity | atemporal | single_fact | sports competition (Q16510064) | P585 | P276 |  | Where was {descriptor} held? |
| graduate_before_employer | blueprint | not_yet_proven | Education | Organization | entity | atemporal | multi_hop_join | human (Q5) | P569 | P69 |  | From which university did {descriptor} graduate before working at {employer_label}? |
| degree_granting_university | blueprint | not_yet_proven | Education | Organization | entity | atemporal | single_fact | degree (Q189533) | P577 | P1027 |  | Which university grants the degree {descriptor}? |
| school_founder | blueprint | not_yet_proven | Education | Person | entity | atemporal | single_fact | school (Q3914) | P571 | P112 |  | Who founded the school {descriptor}? |
| curriculum_author | blueprint | not_yet_proven | Education | Person | entity | atemporal | single_fact | curriculum (Q11774891) | P577 | P50 |  | Who wrote the curriculum {descriptor}? |
| textbook_publisher | blueprint | not_yet_proven | Education | Organization | entity | atemporal | single_fact | textbook (Q571) | P577 | P123 |  | Which publisher released the textbook {descriptor}? |
| math_textbook_author | blueprint | not_yet_proven | Mathematics | Person | entity | atemporal | single_fact | book (Q571) | P577 | P50 |  | Who wrote the mathematics book {descriptor}? |
| math_software_developer | blueprint | not_yet_proven | Mathematics | Organization | entity | atemporal | single_fact | software (Q7397) | P577 | P178 |  | Which company developed the mathematics software {descriptor}? |
| math_paper_journal | blueprint | not_yet_proven | Mathematics | Organization | entity | atemporal | single_fact | scholarly article (Q13442814) | P577 | P1433 |  | In which journal was the mathematics article {descriptor} published? |
| dataset_creator_math | blueprint | not_yet_proven | Mathematics | Person | entity | atemporal | single_fact | dataset (Q1172284) | P577 | P170 |  | Who created the dataset {descriptor}? |
| chemistry_article_journal | blueprint | not_yet_proven | Physical Sciences | Organization | entity | atemporal | single_fact | scholarly article (Q13442814) | P577 | P1433 |  | In which journal was the chemistry article {descriptor} published? |
| physics_book_author | blueprint | not_yet_proven | Physical Sciences | Person | entity | atemporal | single_fact | book (Q571) | P577 | P50 |  | Who wrote the physics book {descriptor}? |
| instrument_manufacturer | blueprint | not_yet_proven | Physical Sciences | Organization | entity | atemporal | single_fact | scientific instrument (Q34379) | P577 | P176 |  | Which company manufactured the instrument {descriptor}? |
| space_telescope_operator | blueprint | not_yet_proven | Physical Sciences | Organization | entity | atemporal | single_fact | space telescope (Q2133344) | P571 | P137 |  | Which agency operates the telescope {descriptor}? |
| physical_science_dataset_creator | blueprint | not_yet_proven | Physical Sciences | Person | entity | atemporal | single_fact | dataset (Q1172284) | P577 | P170 |  | Who created the physical science dataset {descriptor}? |
| genome_project_lead_org | blueprint | not_yet_proven | Life Sciences | Organization | entity | atemporal | single_fact | genome project (Q3966) | P577 | P749 |  | Which organization led the genome project {descriptor}? |
| species_described_by | blueprint | not_yet_proven | Life Sciences | Person | entity | atemporal | single_fact | taxon (Q16521) | P577 | P405 |  | Who first described the species {descriptor}? |
| bioinformatics_software_developer | blueprint | not_yet_proven | Life Sciences | Organization | entity | atemporal | single_fact | software (Q7397) | P577 | P178 |  | Which company developed the bioinformatics software {descriptor}? |
| biology_article_journal | blueprint | not_yet_proven | Life Sciences | Organization | entity | atemporal | single_fact | scholarly article (Q13442814) | P577 | P1433 |  | In which journal was the biology article {descriptor} published? |
| biobank_country | blueprint | not_yet_proven | Life Sciences | Place | entity | atemporal | single_fact | biobank (Q4915012) | P571 | P17 |  | In which country is the biobank {descriptor} located? |
| medicine_active_ingredient | blueprint | not_yet_proven | Medicine and Health | Other | entity | atemporal | single_fact | medication (Q12140) | P577 | P3781 |  | What is the main active ingredient in the medicine {descriptor}? |
| vaccine_developer | blueprint | not_yet_proven | Medicine and Health | Organization | entity | atemporal | single_fact | vaccine (Q877194) | P577 | P178 |  | Which company developed the vaccine {descriptor}? |
| hospital_country | blueprint | not_yet_proven | Medicine and Health | Place | entity | atemporal | single_fact | hospital (Q16917) | P571 | P17 |  | In which country is the hospital {descriptor} located? |
| clinical_guideline_author | blueprint | not_yet_proven | Medicine and Health | Organization | entity | atemporal | single_fact | clinical guideline (Q617602) | P577 | P50 |  | Which organization wrote the guideline {descriptor}? |
| medical_device_manufacturer | blueprint | not_yet_proven | Medicine and Health | Organization | entity | atemporal | single_fact | medical device (Q174784) | P577 | P176 |  | Which company manufactured the medical device {descriptor}? |
| spacecraft_operator | blueprint | not_yet_proven | Earth, Environment, and Space | Organization | entity | atemporal | single_fact | spacecraft (Q40218) | P577 | P137 |  | Which agency operates the spacecraft {descriptor}? |
| space_mission_launch_site | blueprint | not_yet_proven | Earth, Environment, and Space | Place | entity | atemporal | single_fact | space mission (Q2133344) | P585 | P1427 |  | From where was {descriptor} launched? |
| climate_report_author | blueprint | not_yet_proven | Earth, Environment, and Space | Organization | entity | atemporal | single_fact | report (Q10870555) | P577 | P50 |  | Which organization wrote the report {descriptor}? |
| satellite_manufacturer | blueprint | not_yet_proven | Earth, Environment, and Space | Organization | entity | atemporal | single_fact | artificial satellite (Q2537) | P577 | P176 |  | Which company built the satellite {descriptor}? |
| environmental_project_lead | blueprint | not_yet_proven | Earth, Environment, and Space | Person | entity | atemporal | single_fact | project (Q170584) | P571 | P1037 |  | Who led the project {descriptor}? |
| ai_model_developer | blueprint | not_yet_proven | Computer Science and AI | Organization | entity | atemporal | single_fact | software (Q7397) | P577 | P178 |  | Which company developed the model {descriptor}? |
| programming_language_designer | blueprint | not_yet_proven | Computer Science and AI | Person | entity | atemporal | single_fact | programming language (Q9143) | P577 | P287 |  | Who designed the programming language {descriptor}? |
| framework_license | blueprint | not_yet_proven | Computer Science and AI | Other | entity | atemporal | single_fact | software framework (Q271680) | P577 | P275 |  | What license does the framework {descriptor} use? |
| dataset_creator_ai | blueprint | not_yet_proven | Computer Science and AI | Person | entity | atemporal | single_fact | dataset (Q1172284) | P577 | P170 |  | Who created the dataset {descriptor}? |
| paper_conference_ai | blueprint | not_yet_proven | Computer Science and AI | Organization | entity | atemporal | single_fact | scholarly article (Q13442814) | P577 | P1433 |  | At which venue was the AI paper {descriptor} published? |
| benchmark_release_date | blueprint | not_yet_proven | Computer Science and AI | Date | date | date_answer | single_fact | dataset (Q1172284) | P577 | P577 |  | On what day, month, and year was the benchmark {descriptor} released? |
| device_manufacturer | blueprint | not_yet_proven | Engineering and Technology | Organization | entity | atemporal | single_fact | device (Q1183543) | P577 | P176 |  | Which company manufactured the device {descriptor}? |
| robot_creator | blueprint | not_yet_proven | Engineering and Technology | Person | entity | atemporal | single_fact | robot (Q11012) | P571 | P170 |  | Who created the robot {descriptor}? |
| vehicle_designer | blueprint | not_yet_proven | Engineering and Technology | Person | entity | atemporal | single_fact | vehicle (Q42889) | P577 | P287 |  | Who designed the vehicle {descriptor}? |
| chip_architecture_designer | blueprint | not_yet_proven | Engineering and Technology | Organization | entity | atemporal | single_fact | microprocessor (Q11426) | P577 | P287 |  | Which company designed the chip {descriptor}? |
| product_release_date | blueprint | not_yet_proven | Engineering and Technology | Date | date | date_answer | single_fact | product (Q2424752) | P577 | P577 |  | On what day, month, and year was the product {descriptor} released? |
| rail_station_country | blueprint | not_yet_proven | Architecture and Transportation | Place | entity | atemporal | single_fact | railway station (Q55488) | P571 | P17 |  | In which country is the railway station {descriptor} located? |
| bridge_architect | blueprint | not_yet_proven | Architecture and Transportation | Person | entity | atemporal | single_fact | bridge (Q12280) | P571 | P84 |  | Who designed the bridge {descriptor}? |
| port_operator | blueprint | not_yet_proven | Architecture and Transportation | Organization | entity | atemporal | single_fact | port (Q44782) | P571 | P137 |  | Which organization operates the port {descriptor}? |
| train_manufacturer | blueprint | not_yet_proven | Architecture and Transportation | Organization | entity | atemporal | single_fact | train (Q870) | P577 | P176 |  | Which company built the train {descriptor}? |
| terminal_opening_date | blueprint | not_yet_proven | Architecture and Transportation | Date | date | date_answer | single_fact | terminal (Q55488) | P571 | P571 |  | On what day, month, and year did the terminal {descriptor} open? |
| beverage_manufacturer | blueprint | not_yet_proven | Food, Agriculture, and Daily Life | Organization | entity | atemporal | single_fact | beverage (Q40050) | P577 | P176 |  | Which company manufactured the beverage {descriptor}? |
| crop_variety_developer | blueprint | not_yet_proven | Food, Agriculture, and Daily Life | Organization | entity | atemporal | single_fact | crop (Q11004) | P577 | P178 |  | Which organization developed the crop variety {descriptor}? |
| kitchen_appliance_manufacturer | blueprint | not_yet_proven | Food, Agriculture, and Daily Life | Organization | entity | atemporal | single_fact | kitchen appliance (Q260521) | P577 | P176 |  | Which company manufactured the kitchen appliance {descriptor}? |
| restaurant_founder | blueprint | not_yet_proven | Food, Agriculture, and Daily Life | Person | entity | atemporal | single_fact | restaurant (Q11707) | P571 | P112 |  | Who founded the restaurant {descriptor}? |
| biography_place_of_death_recent_subject | blueprint | not_yet_proven | People | Place | entity | atemporal | single_fact | human (Q5) | P569 | P20 |  | Where did {descriptor} die? |
| biography_occupation_recent_subject | blueprint | not_yet_proven | People | Other | entity | atemporal | single_fact | human (Q5) | P569 | P106 |  | What is the occupation of {descriptor}? |
| biography_notable_work_recent_subject | blueprint | not_yet_proven | People | Work | entity | atemporal | single_fact | human (Q5) | P569 | P800 |  | What is a notable work by {descriptor}? |
| new_dam_country | blueprint | not_yet_proven | Geography | Place | entity | atemporal | single_fact | dam (Q12323) | P571 | P17 |  | In which country is the dam {descriptor} located? |
| new_nature_reserve_country | blueprint | not_yet_proven | Geography | Place | entity | atemporal | single_fact | nature reserve (Q473972) | P571 | P17 |  | In which country is the nature reserve {descriptor} located? |
| constitution_jurisdiction | blueprint | not_yet_proven | Politics and Law | Place | entity | atemporal | single_fact | constitution (Q7755) | P577 | P1001 |  | To which jurisdiction does the constitution {descriptor} apply? |
| government_agency_jurisdiction | blueprint | not_yet_proven | Politics and Law | Place | entity | atemporal | single_fact | government agency (Q327333) | P571 | P1001 |  | To which jurisdiction does the government agency {descriptor} apply? |
| company_parent_organization | blueprint | not_yet_proven | Economy and Business | Organization | entity | atemporal | single_fact | company (Q783794) | P571 | P749 |  | Which organization is the parent of the company {descriptor}? |
| company_industry | blueprint | not_yet_proven | Economy and Business | Other | entity | atemporal | single_fact | company (Q783794) | P571 | P452 |  | What industry is the company {descriptor} in? |
| stock_exchange_country | blueprint | not_yet_proven | Economy and Business | Place | entity | atemporal | single_fact | stock exchange (Q11654) | P571 | P17 |  | In which country is the stock exchange {descriptor} located? |
| library_country | blueprint | not_yet_proven | Society and Culture | Place | entity | atemporal | single_fact | library (Q7075) | P571 | P17 |  | In which country is the library {descriptor} located? |
| heritage_site_country | blueprint | not_yet_proven | Society and Culture | Place | entity | atemporal | single_fact | heritage site (Q9259) | P571 | P17 |  | In which country is the heritage site {descriptor} located? |
| church_country | blueprint | not_yet_proven | Philosophy and Religion | Place | entity | atemporal | single_fact | church building (Q16970) | P571 | P17 |  | In which country is the church {descriptor} located? |
| monastery_country | blueprint | not_yet_proven | Philosophy and Religion | Place | entity | atemporal | single_fact | monastery (Q44613) | P571 | P17 |  | In which country is the monastery {descriptor} located? |
| play_author | blueprint | not_yet_proven | Language and Literature | Person | entity | atemporal | single_fact | play (Q25379) | P577 | P50 |  | Who wrote the play {descriptor}? |
| poem_author | blueprint | not_yet_proven | Language and Literature | Person | entity | atemporal | single_fact | poem (Q5185279) | P577 | P50 |  | Who wrote the poem {descriptor}? |
| newspaper_country | blueprint | not_yet_proven | Language and Literature | Place | entity | atemporal | single_fact | newspaper (Q11032) | P571 | P17 |  | In which country is the newspaper {descriptor} based? |
| opera_composer | blueprint | not_yet_proven | Arts and Media | Person | entity | atemporal | single_fact | opera (Q1344) | P577 | P86 |  | Who composed the opera {descriptor}? |
| film_production_company | blueprint | not_yet_proven | Arts and Media | Organization | entity | atemporal | single_fact | film (Q11424) | P577 | P272 |  | Which company produced the film {descriptor}? |
| manga_author | blueprint | not_yet_proven | Arts and Media | Person | entity | atemporal | single_fact | manga (Q8274) | P577 | P50 |  | Who wrote the manga {descriptor}? |
| sports_league_operator | blueprint | not_yet_proven | Sports and Recreation | Organization | entity | atemporal | single_fact | sports league (Q15991303) | P571 | P137 |  | Which organization operates the league {descriptor}? |
| sports_team_home_venue | blueprint | not_yet_proven | Sports and Recreation | Place | entity | atemporal | single_fact | sports club (Q847017) | P571 | P115 |  | At which venue does the team {descriptor} play home matches? |
| university_country | blueprint | not_yet_proven | Education | Place | entity | atemporal | single_fact | university (Q3918) | P571 | P17 |  | In which country is the university {descriptor} located? |
| textbook_author | blueprint | not_yet_proven | Education | Person | entity | atemporal | single_fact | textbook (Q571) | P577 | P50 |  | Who wrote the textbook {descriptor}? |
| math_article_main_subject | blueprint | not_yet_proven | Mathematics | Other | entity | atemporal | single_fact | scholarly article (Q13442814) | P577 | P921 |  | What is the main subject of the mathematics article {descriptor}? |
| math_award_presenter | blueprint | not_yet_proven | Mathematics | Organization | entity | atemporal | single_fact | award (Q618779) | P571 | P1027 |  | Which organization confers the mathematics award {descriptor}? |
| spacecraft_manufacturer | blueprint | not_yet_proven | Physical Sciences | Organization | entity | atemporal | single_fact | spacecraft (Q40218) | P577 | P176 |  | Which company built the spacecraft {descriptor}? |
| scientific_instrument_operator | blueprint | not_yet_proven | Physical Sciences | Organization | entity | atemporal | single_fact | scientific instrument (Q34379) | P577 | P137 |  | Which organization operates the scientific instrument {descriptor}? |
| species_parent_taxon | blueprint | not_yet_proven | Life Sciences | Other | entity | atemporal | single_fact | taxon (Q16521) | P577 | P171 |  | What is the parent taxon of {descriptor}? |
| taxonomy_database_creator | blueprint | not_yet_proven | Life Sciences | Person | entity | atemporal | single_fact | dataset (Q1172284) | P577 | P170 |  | Who created the taxonomy dataset {descriptor}? |
| medical_school_country | blueprint | not_yet_proven | Medicine and Health | Place | entity | atemporal | single_fact | medical school (Q3914) | P571 | P17 |  | In which country is the medical school {descriptor} located? |
| clinical_guideline_publisher | blueprint | not_yet_proven | Medicine and Health | Organization | entity | atemporal | single_fact | clinical guideline (Q617602) | P577 | P123 |  | Which publisher released the guideline {descriptor}? |
| satellite_operator | blueprint | not_yet_proven | Earth, Environment, and Space | Organization | entity | atemporal | single_fact | artificial satellite (Q2537) | P577 | P137 |  | Which agency operates the satellite {descriptor}? |
| report_publisher | blueprint | not_yet_proven | Earth, Environment, and Space | Organization | entity | atemporal | single_fact | report (Q10870555) | P577 | P123 |  | Which publisher released the report {descriptor}? |
| operating_system_developer | blueprint | not_yet_proven | Computer Science and AI | Organization | entity | atemporal | single_fact | operating system (Q9135) | P577 | P178 |  | Which company developed the operating system {descriptor}? |
| database_system_developer | blueprint | not_yet_proven | Computer Science and AI | Organization | entity | atemporal | single_fact | database management system (Q176165) | P577 | P178 |  | Which company developed the database system {descriptor}? |
| software_license | blueprint | not_yet_proven | Computer Science and AI | Other | entity | atemporal | single_fact | software (Q7397) | P577 | P275 |  | What license does the software {descriptor} use? |
| aircraft_manufacturer | blueprint | not_yet_proven | Engineering and Technology | Organization | entity | atemporal | single_fact | aircraft (Q11436) | P577 | P176 |  | Which company built the aircraft {descriptor}? |
| engine_designer | blueprint | not_yet_proven | Engineering and Technology | Person | entity | atemporal | single_fact | engine (Q44167) | P577 | P287 |  | Who designed the engine {descriptor}? |
| battery_manufacturer | blueprint | not_yet_proven | Engineering and Technology | Organization | entity | atemporal | single_fact | battery (Q11173) | P577 | P176 |  | Which company manufactured the battery {descriptor}? |
| airport_operator | blueprint | not_yet_proven | Architecture and Transportation | Organization | entity | atemporal | single_fact | airport (Q1248784) | P571 | P137 |  | Which organization operates the airport {descriptor}? |
| lighthouse_country | blueprint | not_yet_proven | Architecture and Transportation | Place | entity | atemporal | single_fact | lighthouse (Q39715) | P571 | P17 |  | In which country is the lighthouse {descriptor} located? |
| cookbook_author | blueprint | not_yet_proven | Food, Agriculture, and Daily Life | Person | entity | atemporal | single_fact | cookbook (Q571) | P577 | P50 |  | Who wrote the cookbook {descriptor}? |
| company_that_released_product_founder | blueprint | not_yet_proven | Economy and Business | Person | entity | time_related_join | multi_hop_join | product (Q2424752) | P577 | COMPOSED_PRODUCT_MANUFACTURER_FOUNDER |  | Who founded the company that released the product {descriptor}? |
| company_that_developed_benchmark_founder | blueprint | not_yet_proven | Computer Science and AI | Person | entity | time_related_join | multi_hop_join | benchmark (Q1172284) | P577 | COMPOSED_BENCHMARK_DEVELOPER_FOUNDER |  | Who founded the organization that developed the benchmark {descriptor}? |
| terminal_operator_country | blueprint | not_yet_proven | Architecture and Transportation | Place | entity | time_related_join | multi_hop_join | terminal (Q55488) | P571 | COMPOSED_TERMINAL_OPERATOR_COUNTRY |  | In which country is the organization that operates the terminal {descriptor} based? |
| tv_series_source_work_author | blueprint | not_yet_proven | Arts and Media | Person | entity | time_related_join | multi_hop_join | television series (Q5398426) | P577 | COMPOSED_SOURCE_WORK_AUTHOR |  | Who wrote the work that the television series {descriptor} was based on? |
| footballer_goals_in_ordinal_tournament | blueprint | not_yet_proven | Sports and Recreation | Number | number | time_related_join | multi_hop_ordinal | association football player (Q937857) | P585 | COMPOSED_ORDINAL_TOURNAMENT_GOALS |  | How many goals did {descriptor} score in the {ordinal} tournament? |
| acquisition_purchase_price | blueprint | not_yet_proven | Economy and Business | Number | number | time_related_join | multi_hop_join | company (Q783794) | P571 | COMPOSED_ACQUISITION_PRICE |  | How many dollars did {acquirer_label} spend to acquire {descriptor}? |
| person_birth_date | blueprint | not_yet_proven | People | Date | date | date_answer | single_fact | human (Q5) | P569 | P569 |  | On what day, month, and year was {descriptor} born? |
| person_death_date | blueprint | not_yet_proven | People | Date | date | date_answer | single_fact | human (Q5) | P570 | P570 |  | On what day, month, and year did {descriptor} die? |
| film_release_date | blueprint | not_yet_proven | Arts and Media | Date | date | date_answer | single_fact | film (Q11424) | P577 | P577 |  | On what day, month, and year was the film {descriptor} released? |
| paper_author_count | blueprint | not_yet_proven | Physical Sciences | Number | number | atemporal | multi_hop_join | scholarly article (Q13442814) | P577 | P50 |  | How many authors wrote the article {descriptor}? |
| math_article_author_count | blueprint | not_yet_proven | Mathematics | Number | number | atemporal | multi_hop_join | scholarly article (Q13442814) | P577 | P50 |  | How many authors wrote the mathematics article {descriptor}? |
| biology_article_author_count | blueprint | not_yet_proven | Life Sciences | Number | number | atemporal | multi_hop_join | scholarly article (Q13442814) | P577 | P50 |  | How many authors wrote the biology article {descriptor}? |
| guideline_author_count | blueprint | not_yet_proven | Medicine and Health | Number | number | atemporal | multi_hop_join | clinical guideline (Q617602) | P577 | P50 |  | How many authors wrote the guideline {descriptor}? |
| report_author_count | blueprint | not_yet_proven | Earth, Environment, and Space | Number | number | atemporal | multi_hop_join | report (Q10870555) | P577 | P50 |  | How many authors wrote the report {descriptor}? |
| album_track_count | blueprint | not_yet_proven | Arts and Media | Number | number | atemporal | multi_hop_join | album (Q482994) | P577 | P658 |  | How many tracks are on the album {descriptor}? |
| story_collection_story_count | blueprint | not_yet_proven | Language and Literature | Number | number | atemporal | multi_hop_join | short story collection (Q13136) | P577 | P527 |  | How many stories are in the collection {descriptor}? |
| company_founder_count | blueprint | not_yet_proven | Economy and Business | Number | number | atemporal | multi_hop_join | company (Q783794) | P571 | P112 |  | How many founders did the company {descriptor} have? |
| startup_founder_count | blueprint | not_yet_proven | Economy and Business | Number | number | atemporal | multi_hop_join | business (Q4830453) | P571 | P112 |  | How many founders did the startup {descriptor} have? |
| treaty_signatory_count | blueprint | not_yet_proven | Politics and Law | Number | number | atemporal | multi_hop_join | treaty (Q131569) | P577 | P17 |  | How many signatories did the treaty {descriptor} have? |
| festival_day_count | blueprint | not_yet_proven | Society and Culture | Number | number | atemporal | multi_hop_join | festival (Q132241) | P585 | P580 |  | How many days did {descriptor} last? |
| spacecraft_crew_count | blueprint | not_yet_proven | Earth, Environment, and Space | Number | number | atemporal | multi_hop_join | spacecraft (Q40218) | P577 | P1029 |  | How many crew members were on {descriptor}? |
| spacecraft_payload_count | blueprint | not_yet_proven | Earth, Environment, and Space | Number | number | atemporal | multi_hop_join | spacecraft (Q40218) | P577 | P527 |  | How many payloads did {descriptor} carry? |
| rover_wheel_count | blueprint | not_yet_proven | Engineering and Technology | Number | number | atemporal | multi_hop_join | robot (Q11012) | P571 | P527 |  | How many wheels does the rover {descriptor} have? |
| patent_inventor_count | blueprint | not_yet_proven | Engineering and Technology | Number | number | atemporal | multi_hop_join | patent (Q253623) | P577 | P61 |  | How many inventors are listed on the patent {descriptor}? |
| bridge_span_count | blueprint | not_yet_proven | Architecture and Transportation | Number | number | atemporal | multi_hop_join | bridge (Q12280) | P571 | P527 |  | How many spans does the bridge {descriptor} have? |
| sports_event_host_count | blueprint | not_yet_proven | Sports and Recreation | Number | number | atemporal | multi_hop_join | sports competition (Q16510064) | P585 | P276 |  | How many host locations were used for {descriptor}? |
| textbook_editor_count | blueprint | not_yet_proven | Education | Number | number | atemporal | multi_hop_join | textbook (Q571) | P577 | P98 |  | How many editors worked on the textbook edition {descriptor}? |
| medicine_ingredient_count | blueprint | not_yet_proven | Medicine and Health | Number | number | atemporal | multi_hop_join | medication (Q12140) | P577 | P3781 |  | How many active ingredients are in the medicine {descriptor}? |
| dataset_language_count | blueprint | not_yet_proven | Computer Science and AI | Number | number | atemporal | multi_hop_join | dataset (Q1172284) | P577 | P407 |  | How many languages are represented in the dataset {descriptor}? |
| project_partner_count | blueprint | not_yet_proven | Engineering and Technology | Number | number | atemporal | multi_hop_join | project (Q170584) | P571 | P749 |  | How many partner organizations were involved in the project {descriptor}? |
| ordinal_country_president | blueprint | not_yet_proven | Politics and Law | Person | entity | atemporal | multi_hop_ordinal | country (Q6256) | P585 | P39 |  | Who was the {ordinal} president of {descriptor}? |
| ordinal_country_prime_minister | blueprint | not_yet_proven | Politics and Law | Person | entity | atemporal | multi_hop_ordinal | country (Q6256) | P585 | P39 |  | Who was the {ordinal} prime minister of {descriptor}? |
| ordinal_tournament_winner | blueprint | not_yet_proven | Sports and Recreation | Person | entity | time_related_join | multi_hop_ordinal | tournament (Q132241) | P585 | P1346 |  | Who won the {ordinal} edition of {descriptor}? |
| ordinal_tournament_host_city | blueprint | not_yet_proven | Sports and Recreation | Place | entity | atemporal | multi_hop_ordinal | tournament (Q132241) | P585 | P131 |  | Which city hosted the {ordinal} edition of {descriptor}? |
| ordinal_religious_leader | blueprint | not_yet_proven | Philosophy and Religion | Person | entity | atemporal | multi_hop_ordinal | religious office (Q246434) | P580 | P39 |  | Who was the {ordinal} leader of {descriptor}? |
| ordinal_university_chancellor | blueprint | not_yet_proven | Education | Person | entity | atemporal | multi_hop_ordinal | university (Q3918) | P585 | P39 |  | Who was the {ordinal} chancellor of {descriptor}? |
| ordinal_company_ceo | blueprint | not_yet_proven | Economy and Business | Person | entity | atemporal | multi_hop_ordinal | company (Q783794) | P585 | P169 |  | Who was the {ordinal} chief executive officer of {descriptor}? |
| ordinal_space_mission_commander | blueprint | not_yet_proven | Earth, Environment, and Space | Person | entity | atemporal | multi_hop_ordinal | space mission (Q2133344) | P585 | P1037 |  | Who was the {ordinal} commander associated with {descriptor}? |
| ordinal_film_in_series_director | blueprint | not_yet_proven | Arts and Media | Person | entity | atemporal | multi_hop_ordinal | film series (Q24856) | P577 | P57 |  | Who directed the {ordinal} film in the series {descriptor}? |
| ordinal_volume_author | blueprint | not_yet_proven | Language and Literature | Person | entity | atemporal | multi_hop_ordinal | book series (Q571) | P577 | P50 |  | Who wrote the {ordinal} volume in the series {descriptor}? |
