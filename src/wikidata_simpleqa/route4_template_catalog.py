"""Reviewed single-hop template catalog for Route 4 two-hop generation."""

from __future__ import annotations

from dataclasses import replace

from .models import DomainTemplate
from .single_hop_template_catalog import single_hop_catalog_as_dicts


ROUTE4_REVIEWED_STATUS = "route4_reviewed"

DISCARDED_ROUTE4_TEMPLATE_KEYS = {
    "existing_train_manufacturer",
    "generated_architecture_and_transportation_buildings_person",
    "generated_arts_and_media_television_number",
    "generated_computer_science_and_ai_ai_models_number",
    "existing_ai_model_developer",
    "existing_video_game_developer",
    "generated_computer_science_and_ai_programming_languages_place",
    "existing_operating_system_developer",
    "existing_satellite_manufacturer",
    "generated_economy_and_business_business_publications_place",
    "generated_economy_and_business_products_number",
    "existing_product_manufacturer",
    "generated_education_degrees_date",
    "generated_education_degrees_other",
    "generated_education_degrees_number",
    "existing_degree_granting_university",
    "existing_curriculum_author",
    "existing_university_country",
    "generated_engineering_and_technology_robots_number",
    "generated_engineering_and_technology_robots_other",
    "generated_engineering_and_technology_vehicles_place",
    "generated_food_agriculture_and_daily_life_beverages_number",
    "generated_food_agriculture_and_daily_life_beverages_person",
    "generated_food_agriculture_and_daily_life_foods_place",
    "generated_food_agriculture_and_daily_life_foods_date",
    "generated_food_agriculture_and_daily_life_foods_number",
    "generated_food_agriculture_and_daily_life_household_products_place",
    "generated_food_agriculture_and_daily_life_household_products_date",
    "generated_food_agriculture_and_daily_life_household_products_number",
    "generated_food_agriculture_and_daily_life_restaurants_person",
    "generated_geography_islands_date",
    "generated_geography_rivers_and_lakes_number",
    "generated_history_battles_number",
    "generated_history_battles_person",
    "existing_literary_magazine_country",
    "generated_life_sciences_zoology_number",
    "generated_medicine_and_health_medical_devices_number",
    "existing_medical_device_manufacturer",
    "generated_medicine_and_health_vaccines_number",
    "existing_biography_occupation_recent_subject",
    "generated_people_creative_careers_number",
    "generated_people_creative_careers_date",
    "generated_people_creative_careers_place",
    "generated_people_creative_careers_person",
    "generated_people_education_date",
    "generated_people_education_number",
    "generated_people_education_person",
    "generated_people_public_offices_other",
    "existing_biography_notable_work_recent_subject",
    "generated_people_public_offices_date",
    "generated_people_scientific_careers_number",
    "existing_space_telescope_operator",
    "existing_instrument_manufacturer",
    "existing_scientific_instrument_operator",
    "generated_physical_sciences_spacecraft_place",
    "generated_physical_sciences_spacecraft_number",
    "generated_physical_sciences_spacecraft_person",
    "existing_spacecraft_manufacturer",
    "generated_politics_and_law_constitutions_place",
    "generated_politics_and_law_court_cases_place",
    "generated_society_and_culture_festivals_number",
    "generated_sports_and_recreation_games_and_recreation_other",
    "generated_sports_and_recreation_games_and_recreation_number",
    "existing_sports_league_operator",
    "generated_sports_and_recreation_races_place",
    "generated_sports_and_recreation_races_date",
    "generated_sports_and_recreation_races_number",
    "generated_sports_and_recreation_races_person",
    "generated_sports_and_recreation_tournaments_other",
    "existing_competition_venue",
}

ROUTE4_TEMPLATE_OVERRIDES: dict[str, dict[str, str]] = {
    "generated_architecture_and_transportation_airports_number": {
        "subject_type_qid": "Q849706",
        "subject_type_label": "airport terminal",
        "target_property_pid": "P2046",
        "target_property_label": "floor area",
        "canonical_question_template": "What is the floor area of the airport terminal {descriptor} in square meters?",
    },
    "existing_lighthouse_country": {
        "target_property_pid": "P131",
        "target_property_label": "located in administrative territorial entity",
        "canonical_question_template": "In which administrative area is the lighthouse {descriptor} located?",
    },
    "generated_architecture_and_transportation_rail_systems_number": {
        "canonical_question_template": "What was the route length of the railway line {descriptor} in kilometers in {month} {year}?",
    },
    "generated_architecture_and_transportation_ships_and_ports_number": {
        "canonical_question_template": "What is the gross tonnage of the ship {descriptor} in tons?",
    },
    "existing_theater_location": {
        "target_property_pid": "P131",
        "target_property_label": "located in administrative territorial entity",
        "canonical_question_template": "In which administrative area is the theatre {descriptor} located?",
    },
    "existing_film_screenwriter": {
        "canonical_question_template": "Who wrote the script for the film {descriptor}?",
    },
    "existing_tv_series_creator": {
        "subject_type_qid": "Q3464665",
        "subject_type_label": "television season",
        "canonical_question_template": "Who created the television season {descriptor}?",
    },
    "generated_arts_and_media_visual_art_date": {
        "canonical_question_template": "On what month, day, and year was the exhibition {descriptor} opened?",
    },
    "generated_earth_environment_and_space_geology_place": {
        "target_property_pid": "P131",
        "target_property_label": "located in administrative territorial entity",
        "canonical_question_template": "In which administrative area is the volcano {descriptor} located?",
    },
    "generated_earth_environment_and_space_satellites_place": {
        "target_property_pid": "P1427",
        "target_property_label": "launch site",
        "canonical_question_template": "From which launch site was the satellite {descriptor} launched?",
    },
    "existing_space_mission_launch_site": {
        "canonical_question_template": "From which launch site was {descriptor} launched?",
    },
    "generated_economy_and_business_banks_number": {
        "canonical_question_template": "What was the registered capital of the bank {descriptor} in dollars in {year}?",
    },
    "generated_economy_and_business_financial_markets_number": {
        "canonical_question_template": "What was the tick size of the exchange {descriptor} in {year}?",
    },
    "existing_stock_exchange_country": {
        "target_property_pid": "P131",
        "target_property_label": "located in administrative territorial entity",
        "canonical_question_template": "In which administrative area is the stock exchange {descriptor} located?",
    },
    "generated_education_academic_awards_number": {
        "canonical_question_template": "What was the monetary value of the scholarship {descriptor} in {year}?",
    },
    "generated_education_textbooks_date": {
        "canonical_question_template": "On what month, day, and year was the original edition of the textbook {descriptor} published?",
    },
    "generated_education_textbooks_number": {
        "canonical_question_template": "What is the page count of the original edition of the textbook {descriptor}?",
    },
    "existing_textbook_publisher": {
        "canonical_question_template": "Which publisher released the original edition of the textbook {descriptor} in {year}?",
    },
    "generated_education_universities_place": {
        "target_property_pid": "P131",
        "target_property_label": "located in administrative territorial entity",
        "canonical_question_template": "In which administrative area is the university {descriptor} located?",
    },
    "existing_product_release_date": {
        "canonical_question_template": "On what month, day, and year was {descriptor} first released?",
    },
    "generated_engineering_and_technology_electronics_date": {
        "subject_type_qid": "Q19723451",
        "subject_type_label": "smartphone model",
        "canonical_question_template": "On what month, day, and year was the smartphone {descriptor} released?",
    },
    "generated_engineering_and_technology_electronics_other": {
        "subject_type_qid": "Q19723451",
        "subject_type_label": "smartphone model",
        "canonical_question_template": "What operating system does the smartphone {descriptor} use?",
    },
    "generated_engineering_and_technology_electronics_person": {
        "subject_type_qid": "Q19723451",
        "subject_type_label": "smartphone model",
        "canonical_question_template": "Who designed the smartphone {descriptor}?",
    },
    "existing_device_manufacturer": {
        "subject_type_qid": "Q19723451",
        "subject_type_label": "smartphone model",
        "canonical_question_template": "Which company manufactured the smartphone {descriptor}?",
    },
    "generated_engineering_and_technology_vehicles_date": {
        "subject_type_qid": "Q193692",
        "subject_type_label": "electric car",
        "canonical_question_template": "On what month, day, and year was the electric car {descriptor} introduced?",
    },
    "generated_engineering_and_technology_vehicles_number": {
        "subject_type_qid": "Q193692",
        "subject_type_label": "electric car",
        "canonical_question_template": "What is the wheelbase of the electric car {descriptor} in millimeters?",
    },
    "existing_vehicle_designer": {
        "subject_type_qid": "Q193692",
        "subject_type_label": "electric car",
        "canonical_question_template": "Who designed the electric car {descriptor}?",
    },
    "generated_food_agriculture_and_daily_life_beverages_date": {
        "subject_type_qid": "Q429949",
        "subject_type_label": "energy drink",
        "canonical_question_template": "On what month, day, and year was the energy drink {descriptor} introduced?",
    },
    "existing_beverage_manufacturer": {
        "subject_type_label": "baijiu",
        "canonical_question_template": "Which company manufactured the baijiu {descriptor}?",
    },
    "generated_food_agriculture_and_daily_life_crops_number": {
        "canonical_question_template": "What is the average yield of the crop variety {descriptor} in tonnes per hectare in {year}?",
    },
    "generated_food_agriculture_and_daily_life_restaurants_number": {
        "canonical_question_template": "What was the seating capacity of the restaurant {descriptor} in {year}?",
    },
    "generated_geography_administrative_places_number": {
        "canonical_question_template": "What was the area of the municipality {descriptor} in square kilometers in {year}?",
    },
    "existing_new_metro_station_country": {
        "target_property_pid": "P131",
        "target_property_label": "located in administrative territorial entity",
        "canonical_question_template": "In which administrative area is the metro station {descriptor} located?",
    },
    "existing_new_dam_country": {
        "target_property_pid": "P131",
        "target_property_label": "located in administrative territorial entity",
        "canonical_question_template": "In which administrative area is the dam {descriptor} located?",
    },
    "generated_geography_mountains_place": {
        "target_property_pid": "P131",
        "target_property_label": "located in administrative territorial entity",
        "canonical_question_template": "In which administrative area is the mountain {descriptor} located?",
    },
    "generated_geography_protected_places_number": {
        "canonical_question_template": "What was the area of the park {descriptor} in hectares in {year}?",
    },
    "existing_new_nature_reserve_country": {
        "target_property_pid": "P131",
        "target_property_label": "located in administrative territorial entity",
        "canonical_question_template": "In which administrative area is the nature reserve {descriptor} located?",
    },
    "generated_language_and_literature_literary_collections_number": {
        "canonical_question_template": "What is the page count in the original edition of the anthology {descriptor}?",
    },
    "generated_language_and_literature_novels_number": {
        "canonical_question_template": "What is the page count in the original edition of the novel {descriptor}?",
    },
    "generated_language_and_literature_poetry_person": {
        "canonical_question_template": "Who translated the poem {descriptor} into {language}?",
    },
    "generated_life_sciences_botany_date": {
        "canonical_question_template": "On what month, day, and year was the plant species {descriptor} first described?",
    },
    "generated_life_sciences_zoology_date": {
        "canonical_question_template": "On what month, day, and year was the animal species {descriptor} first described?",
    },
    "generated_mathematics_mathematics_awards_number": {
        "canonical_question_template": "What was the prize amount of the mathematics award {descriptor} in {year}?",
    },
    "generated_mathematics_mathematics_books_number": {
        "canonical_question_template": "What is the page count of the original edition of the mathematics book {descriptor}?",
    },
    "existing_math_textbook_author": {
        "canonical_question_template": "Who wrote the original edition of the mathematics book {descriptor}?",
    },
    "existing_biography_place_of_death_recent_subject": {
        "canonical_question_template": "In which city did {descriptor} die?",
    },
    "generated_philosophy_and_religion_belief_systems_date": {
        "date_answer_granularity": "year",
        "canonical_question_template": "In what year was the movement {descriptor} founded?",
    },
    "generated_philosophy_and_religion_philosophy_books_number": {
        "canonical_question_template": "What is the page count of the original edition of the philosophy book {descriptor}?",
    },
    "generated_philosophy_and_religion_philosophy_books_person": {
        "canonical_question_template": "Who translated the philosophy book {descriptor} into {language}?",
    },
    "existing_church_country": {
        "target_property_pid": "P131",
        "target_property_label": "located in administrative territorial entity",
        "canonical_question_template": "In which administrative area is the church {descriptor} located?",
    },
    "generated_philosophy_and_religion_religious_buildings_place": {
        "target_property_pid": "P131",
        "target_property_label": "located in administrative territorial entity",
        "canonical_question_template": "In which administrative area is the monastery {descriptor} located?",
    },
    "existing_temple_country": {
        "target_property_pid": "P131",
        "target_property_label": "located in administrative territorial entity",
        "canonical_question_template": "In which administrative area is the temple {descriptor} located?",
    },
    "generated_philosophy_and_religion_religious_offices_place": {
        "target_property_pid": "P131",
        "target_property_label": "located in administrative territorial entity",
        "canonical_question_template": "In which administrative area is the religious office {descriptor} based?",
    },
    "existing_library_country": {
        "target_property_pid": "P131",
        "target_property_label": "located in administrative territorial entity",
        "canonical_question_template": "In which administrative area is the library {descriptor} located?",
    },
    "existing_tournament_host_country": {
        "target_property_pid": "P276",
        "target_property_label": "location",
        "canonical_question_template": "Which city hosted {descriptor} in {year}?",
    },
}


def get_route4_reviewed_single_hop_templates() -> list[DomainTemplate]:
    """Return reviewed single-hop templates selected for Route 4."""
    templates = [
        _domain_template_from_row(row)
        for row in single_hop_catalog_as_dicts()
        if row["template_key"] not in DISCARDED_ROUTE4_TEMPLATE_KEYS
    ]
    templates.extend(_new_user_templates())
    return _dedupe_by_key(templates)


def get_route4_reviewed_template_by_key(template_key: str) -> DomainTemplate | None:
    """Return one reviewed Route 4 template by key."""
    for template in get_route4_reviewed_single_hop_templates():
        if template.template_key == template_key:
            return template
    return None


def get_route4_reviewed_template_summary() -> dict[str, object]:
    """Return summary counts for the reviewed Route 4 template set."""
    templates = get_route4_reviewed_single_hop_templates()
    return {
        "total": len(templates),
        "discarded_review_rows": len(DISCARDED_ROUTE4_TEMPLATE_KEYS),
        "new_user_templates": len(_new_user_templates()),
        "answer_types": _counts(template.answer_type for template in templates),
        "domains": _counts(template.template_domain for template in templates),
    }


def _domain_template_from_row(row: dict[str, str]) -> DomainTemplate:
    """Convert one reviewed single-hop planning row to a DomainTemplate."""
    data = {**row, **ROUTE4_TEMPLATE_OVERRIDES.get(row["template_key"], {})}
    answer_format = data["answer_format"]
    if data["answer_type"] == "Number":
        answer_format = "number"
    elif data["answer_type"] == "Date":
        answer_format = "date"
    return DomainTemplate(
        domain=data["template_key"],
        topic=data["domain"],
        answer_type=data["answer_type"],
        question_family=data["template_key"],
        subject_type_qid=data["subject_type_qid"],
        subject_type_label=data["subject_type_label"],
        date_property_pid=data["date_property_pid"],
        target_property_pid=data["target_property_pid"],
        target_property_label=data["target_property_label"],
        canonical_question_template=data["canonical_question_template"],
        answer_format=answer_format,
        date_answer_granularity=data.get("date_answer_granularity") or ("day" if answer_format == "date" else None),
        temporal_mode=data["temporal_mode"],
        status=ROUTE4_REVIEWED_STATUS,
        reasoning_recipe={
            "source": "reviewed_single_hop_catalog",
            "subdomain": data["subdomain"],
            "origin": data["origin"],
            "legacy_template_key": data.get("legacy_template_key", ""),
        },
        exact_instance_only=False,
    )


def _new_template(
    key: str,
    domain: str,
    subdomain: str,
    answer_type: str,
    subject_type_qid: str,
    subject_type_label: str,
    date_property_pid: str,
    target_property_pid: str,
    target_property_label: str,
    canonical_question_template: str,
    *,
    answer_format: str | None = None,
    date_answer_granularity: str | None = None,
) -> DomainTemplate:
    resolved_answer_format = answer_format or (
        "date" if answer_type == "Date" else "number" if answer_type == "Number" else "entity"
    )
    return DomainTemplate(
        domain=key,
        topic=domain,
        answer_type=answer_type,
        question_family=key,
        subject_type_qid=subject_type_qid,
        subject_type_label=subject_type_label,
        date_property_pid=date_property_pid,
        target_property_pid=target_property_pid,
        target_property_label=target_property_label,
        canonical_question_template=canonical_question_template,
        answer_format=resolved_answer_format,
        date_answer_granularity=date_answer_granularity or ("day" if resolved_answer_format == "date" else None),
        temporal_mode="date_answer" if resolved_answer_format == "date" else "atemporal",
        status=ROUTE4_REVIEWED_STATUS,
        reasoning_recipe={"source": "user_review_sheet_2", "subdomain": subdomain},
    )


def _new_user_templates() -> list[DomainTemplate]:
    """Return templates added by the user on the workbook's second sheet."""
    return [
        _new_template("route4_metro_line_operator", "Architecture and Transportation", "rail systems", "Other", "Q15079663", "metro line", "P571", "P137", "operator", "What is the operator of the metro line {descriptor}?"),
        _new_template("route4_metro_line_color", "Architecture and Transportation", "rail systems", "Other", "Q15079663", "metro line", "P571", "P462", "color", "What is the line color of the metro line {descriptor}?"),
        _new_template("route4_bank_forbes_global_2000_rank", "Economy and Business", "banks", "Number", "Q22687", "bank", "P571", "P1352", "ranking", "What was the ranking of the bank {descriptor} in Forbes Global 2000 in {year}?"),
        _new_template("route4_bank_total_assets", "Economy and Business", "banks", "Number", "Q22687", "bank", "P571", "P2403", "total assets", "What were the total assets of the bank {descriptor} in {year}?", answer_format="number"),
        _new_template("route4_earthquake_coordinate_location", "Earth, Environment, and Space", "geology", "Other", "Q7944", "earthquake", "P585", "P625", "coordinate location", "What is the coordinate location of the earthquake {descriptor}?", answer_format="value"),
        _new_template("route4_earthquake_fault", "Earth, Environment, and Space", "geology", "Other", "Q7944", "earthquake", "P585", "P828", "has cause", "What fault was related to the earthquake {descriptor}?"),
        _new_template("route4_stele_discovery_date", "History", "archaeological sites", "Date", "Q178743", "stele", "P571", "P575", "discovery date", "On what month, day, and year was the stele {descriptor} first discovered?"),
        _new_template("route4_stele_discovery_administrative_area", "History", "archaeological sites", "Place", "Q178743", "stele", "P571", "P131", "located in administrative territorial entity", "In which administrative area was the stele {descriptor} first discovered?"),
        _new_template("route4_stele_inception_year", "History", "archaeological sites", "Date", "Q178743", "stele", "P571", "P571", "inception", "In what year was the stele {descriptor} made?", date_answer_granularity="year"),
        _new_template("route4_stele_material", "History", "archaeological sites", "Other", "Q178743", "stele", "P571", "P186", "material used", "What material was the stele {descriptor} made from?"),
        _new_template("route4_stele_width", "History", "archaeological sites", "Number", "Q178743", "stele", "P571", "P2049", "width", "What is the width of the stele {descriptor} in centimeters?"),
        _new_template("route4_person_cause_of_death", "People", "birth and death facts", "Other", "Q5", "human", "P570", "P509", "cause of death", "What was the cause of death of {descriptor}?"),
        _new_template("route4_spaceflight_follows", "Earth, Environment, and Space", "space missions", "Other", "Q752783", "spaceflight", "P619", "P155", "follows", "What spaceflight does {descriptor} follow?"),
        _new_template("route4_spaceflight_motto", "Earth, Environment, and Space", "space missions", "Other", "Q752783", "spaceflight", "P619", "P1451", "motto text", "What is the motto of the spaceflight {descriptor}?", answer_format="value"),
        _new_template("route4_spaceflight_duration", "Earth, Environment, and Space", "space missions", "Number", "Q752783", "spaceflight", "P619", "P2047", "duration", "What is the duration of the spaceflight {descriptor} in minutes?"),
        _new_template("route4_spaceflight_vessel", "Earth, Environment, and Space", "space missions", "Other", "Q752783", "spaceflight", "P619", "P1876", "vessel", "What is the vessel of the spaceflight {descriptor}?"),
        _new_template("route4_spaceflight_start_point", "Earth, Environment, and Space", "space missions", "Place", "Q752783", "spaceflight", "P619", "P1427", "launch site", "What is the start point of the spaceflight {descriptor}?"),
        _new_template("route4_hadron_collider_length", "Physical Sciences", "scientific instruments", "Number", "Q13393265", "hadron collider", "P571", "P2043", "length", "What is the length of the hadron collider {descriptor} in kilometers?"),
        _new_template("route4_hadron_collider_opening_date", "Physical Sciences", "scientific instruments", "Date", "Q13393265", "hadron collider", "P1619", "P1619", "official opening", "On what month, day, and year did the hadron collider {descriptor} officially open?"),
        _new_template("route4_hadron_collider_force", "Physical Sciences", "scientific instruments", "Number", "Q13393265", "hadron collider", "P571", "P5708", "force", "What is the force of the hadron collider {descriptor} in amperes?"),
        _new_template("route4_hadron_collider_beam_energy", "Physical Sciences", "scientific instruments", "Number", "Q13393265", "hadron collider", "P571", "P13413", "beam energy", "What is the beam energy of the hadron collider {descriptor} in gigaelectronvolts?"),
        _new_template("route4_rocket_diameter", "Engineering and Technology", "aircraft", "Number", "Q41291", "rocket", "P571", "P2386", "diameter", "What is the diameter of the rocket {descriptor} in miles?"),
        _new_template("route4_tournament_start_month_day", "Sports and Recreation", "tournaments", "Date", "Q132241", "tournament", "P580", "P580", "start time", "On what month and day did {descriptor} start in {year}?", date_answer_granularity="day"),
        _new_template("route4_tournament_end_month_day", "Sports and Recreation", "tournaments", "Date", "Q132241", "tournament", "P582", "P582", "end time", "On what month and day did {descriptor} end in {year}?", date_answer_granularity="day"),
    ]


def _dedupe_by_key(templates: list[DomainTemplate]) -> list[DomainTemplate]:
    """Return templates deduplicated by key."""
    seen = set()
    unique = []
    for template in templates:
        if template.template_key in seen:
            continue
        seen.add(template.template_key)
        unique.append(template)
    return unique


def _counts(values) -> dict[str, int]:
    """Return sorted value counts."""
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def replace_template(template: DomainTemplate, **changes: str) -> DomainTemplate:
    """Return a modified DomainTemplate; useful for tests and future review tooling."""
    return replace(template, **changes)
