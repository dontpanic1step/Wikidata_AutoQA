"""Config-driven domain template catalog."""

from __future__ import annotations

from .models import DomainTemplate
from .reasoning import normalize_reasoning_style


PROVEN_TEMPLATE_RUNS: dict[str, list[str]] = {
    "film_director": ["stage5a_single_fact", "stage5b_pilot"],
    "novel_author": ["stage5a_single_fact", "stage5b_pilot"],
    "book_original_language": ["stage5a_single_fact", "stage5b_pilot"],
    "video_game_developer": ["stage5a_single_fact", "stage5b_pilot"],
    "software_developer": ["stage5a_single_fact", "stage5b_pilot"],
    "scholarly_article_journal": ["stage5a_single_fact", "stage5b_pilot"],
    "artwork_creator": ["stage5a_single_fact", "stage5b_pilot"],
    "album_performer": ["stage5a_single_fact", "stage5b_pilot"],
    "building_architect": ["stage5a_single_fact", "stage5b_pilot"],
    "rail_station_country": ["stage5a_single_fact", "stage5b_pilot"],
    "museum_country": ["stage5a_single_fact", "stage5b_pilot"],
    "company_founder": ["stage5a_single_fact", "stage5b_pilot"],
    "ordinal_tournament_winner": ["stage5b_pilot"],
    "person_first_degree_university": ["stage5b_pilot"],
    "film_source_work_author": ["stage5b_pilot"],
    "benchmark_release_date": ["stage5b_pilot"],
    "product_release_date": ["stage5b_pilot"],
    "terminal_opening_date": ["stage5b_pilot"],
}


PENDING_TEMPLATE_NOTES: dict[str, str] = {}


def _template(
    domain: str,
    topic: str,
    answer_type: str,
    question_family: str,
    subject_type_qid: str,
    subject_type_label: str,
    date_property_pid: str,
    target_property_pid: str,
    target_property_label: str,
    canonical_question_template: str,
    *,
    answer_format: str = "entity",
    date_answer_granularity: str | None = None,
    composition_style: str = "single_fact",
    reasoning_style: str | None = None,
    temporal_mode: str = "atemporal",
    reasoning_recipe: dict | None = None,
    status: str = "active",
    exact_instance_only: bool = False,
) -> DomainTemplate:
    """Build a domain template with explicit metadata."""
    normalized_reasoning_style = normalize_reasoning_style(
        reasoning_style or composition_style
    )
    evidence_runs = (
        PROVEN_TEMPLATE_RUNS.get(domain, [])
        if status in {"active", "multi_hop_pilot", "date_answer_pilot"}
        else []
    )
    evidence_status = "proven_in_runs" if evidence_runs else "not_yet_proven"
    return DomainTemplate(
        domain=domain,
        topic=topic,
        answer_type=answer_type,
        question_family=question_family,
        subject_type_qid=subject_type_qid,
        subject_type_label=subject_type_label,
        date_property_pid=date_property_pid,
        target_property_pid=target_property_pid,
        target_property_label=target_property_label,
        canonical_question_template=canonical_question_template,
        answer_format=answer_format,
        date_answer_granularity=date_answer_granularity,
        composition_style=composition_style,
        reasoning_style=normalized_reasoning_style,
        temporal_mode=temporal_mode,
        reasoning_recipe=reasoning_recipe or {},
        status=status,
        evidence_status=evidence_status,
        evidence_runs=evidence_runs.copy(),
        evidence_notes=PENDING_TEMPLATE_NOTES.get(domain, ""),
        exact_instance_only=exact_instance_only,
    )


ACTIVE_TEMPLATE_CATALOG = [
    _template(
        "film_director",
        "Arts and Media",
        "Person",
        "who_directed_film",
        "Q11424",
        "film",
        "P577",
        "P57",
        "director",
        "Who directed the {subject_kind} {descriptor}?",
    ),
    _template(
        "novel_author",
        "Language and Literature",
        "Person",
        "who_wrote_novel",
        "Q8261",
        "novel",
        "P577",
        "P50",
        "author",
        "Who wrote the {subject_kind} {descriptor}?",
    ),
    _template(
        "book_original_language",
        "Language and Literature",
        "Language",
        "what_language_originally_written",
        "Q571",
        "book",
        "P577",
        "P364",
        "original language of work",
        "What language was the {subject_kind} {descriptor} originally written in?",
    ),
    _template(
        "video_game_developer",
        "Computer Science and AI",
        "Organization",
        "which_company_developed_video_game",
        "Q7889",
        "video game",
        "P577",
        "P178",
        "developer",
        "Which company developed the {subject_kind} {descriptor}?",
    ),
    _template(
        "software_developer",
        "Computer Science and AI",
        "Organization",
        "which_company_developed_software",
        "Q7397",
        "software",
        "P577",
        "P178",
        "developer",
        "Which company developed the {subject_kind} {descriptor}?",
        exact_instance_only=True,
    ),
    _template(
        "scholarly_article_journal",
        "Physical Sciences",
        "Organization",
        "which_journal_published_article",
        "Q13442814",
        "scholarly article",
        "P577",
        "P1433",
        "published in",
        "In which journal was the {subject_kind} {descriptor} published?",
    ),
    _template(
        "artwork_creator",
        "Arts and Media",
        "Person",
        "who_created_artwork",
        "Q838948",
        "artwork",
        "P571",
        "P170",
        "creator",
        "Who created the {subject_kind} {descriptor}?",
        exact_instance_only=True,
    ),
    _template(
        "album_performer",
        "Arts and Media",
        "Person",
        "which_artist_released_album",
        "Q482994",
        "album",
        "P577",
        "P175",
        "performer",
        "Which artist released the {subject_kind} {descriptor}?",
    ),
    _template(
        "building_architect",
        "Architecture and Transportation",
        "Person",
        "who_designed_building",
        "Q41176",
        "building",
        "P571",
        "P84",
        "architect",
        "Who designed the {subject_kind} {descriptor}?",
        exact_instance_only=True,
    ),
    _template(
        "rail_station_country",
        "Architecture and Transportation",
        "Place",
        "which_country_station_located",
        "Q55488",
        "railway station",
        "P571",
        "P17",
        "country",
        "In which country is the {subject_kind} {descriptor} located?",
        exact_instance_only=True,
    ),
    _template(
        "museum_country",
        "Society and Culture",
        "Place",
        "which_country_museum_located",
        "Q33506",
        "museum",
        "P571",
        "P17",
        "country",
        "In which country is the {subject_kind} {descriptor} located?",
        exact_instance_only=True,
    ),
    _template(
        "company_founder",
        "Economy and Business",
        "Person",
        "who_founded_company",
        "Q783794",
        "company",
        "P571",
        "P112",
        "founder",
        "Who founded the {subject_kind} {descriptor}?",
        exact_instance_only=True,
    ),
]


MULTI_HOP_PILOT_TEMPLATE_CATALOG = [
    _template(
        "ordinal_tournament_winner",
        "Sports and Recreation",
        "Entity",
        "who_won_ordinal_tournament",
        "Q132241",
        "tournament edition",
        "P585",
        "P1346",
        "winner",
        "Who won the {ordinal} edition of {descriptor}?",
        composition_style="ordinal_fact",
        temporal_mode="time_related_join",
        reasoning_recipe={
            "required_reasoning_clues": ["edition"],
            "surface_bridge_entities": False,
            "new_element_slot": "subject",
            "new_element_hop": 1,
        },
        status="multi_hop_pilot",
    ),
    _template(
        "person_first_degree_university",
        "People",
        "Organization",
        "which_university_first_degree",
        "Q5",
        "human",
        "P69",
        "P69",
        "educated at",
        "From which university did {descriptor} receive a first degree?",
        composition_style="fact_join",
        temporal_mode="time_related_join",
        reasoning_recipe={
            "required_reasoning_clues": ["first degree"],
            "surface_bridge_entities": False,
            "new_element_slot": "relation",
            "new_element_hop": 1,
        },
        status="multi_hop_pilot",
    ),
    _template(
        "film_source_work_author",
        "Arts and Media",
        "Person",
        "who_wrote_source_work_for_film",
        "Q11424",
        "film",
        "P577",
        "P50",
        "author",
        "Who wrote the work that the film {descriptor} was based on?",
        composition_style="fact_join",
        temporal_mode="time_related_join",
        reasoning_recipe={
            "required_reasoning_clues": ["based on"],
            "surface_bridge_entities": False,
            "new_element_slot": "subject",
            "new_element_hop": 1,
        },
        status="multi_hop_pilot",
    ),
]


DATE_ANSWER_PILOT_TEMPLATE_CATALOG = [
    _template(
        "benchmark_release_date",
        "Computer Science and AI",
        "Date",
        "when_benchmark_released",
        "Q1172284",
        "dataset",
        "P577",
        "P577",
        "publication date",
        "On what day, month, and year was the benchmark {descriptor} released?",
        answer_format="date",
        temporal_mode="date_answer",
        date_answer_granularity="day",
        status="date_answer_pilot",
        exact_instance_only=True,
    ),
    _template(
        "product_release_date",
        "Engineering and Technology",
        "Date",
        "when_product_released",
        "Q2424752",
        "product",
        "P577",
        "P577",
        "publication date",
        "On what day, month, and year was the product {descriptor} released?",
        answer_format="date",
        temporal_mode="date_answer",
        date_answer_granularity="day",
        status="date_answer_pilot",
        exact_instance_only=True,
    ),
    _template(
        "terminal_opening_date",
        "Architecture and Transportation",
        "Date",
        "when_terminal_opened",
        "Q55488",
        "terminal",
        "P571",
        "P571",
        "inception",
        "On what day, month, and year did the terminal {descriptor} open?",
        answer_format="date",
        temporal_mode="date_answer",
        date_answer_granularity="day",
        status="date_answer_pilot",
        exact_instance_only=True,
    ),
]


BLUEPRINT_TEMPLATE_CATALOG = [
    # People
    _template("wedding_age_gap", "People", "Number", "what_age_gap_couple", "Q27020041", "wedding", "P585", "P1534", "end cause", "What was the age gap between the couple in {descriptor}?", answer_format="number", composition_style="fact_join", status="blueprint"),
    _template("marriage_spouse", "People", "Person", "who_married_person", "Q171318", "marriage", "P580", "P26", "spouse", "Who married {descriptor}?", composition_style="fact_join", status="blueprint"),
    _template("biography_birth_place_recent_subject", "People", "Place", "where_person_born", "Q5", "human", "P569", "P19", "place of birth", "Where was {descriptor} born?", status="blueprint"),
    _template("biography_native_language_recent_subject", "People", "Language", "what_native_language_person", "Q5", "human", "P569", "P103", "native language", "What is the native language of {descriptor}?", status="blueprint"),
    _template("person_first_degree_university", "People", "Organization", "which_university_first_degree", "Q5", "human", "P69", "P69", "educated at", "From which university did {descriptor} receive a degree?", composition_style="fact_join", temporal_mode="time_related_join", reasoning_recipe={"new_element_slot": "relation", "new_element_hop": 1}, status="blueprint"),
    # Geography
    _template("new_park_country", "Geography", "Place", "which_country_park_located", "Q22698", "park", "P571", "P17", "country", "In which country is the park {descriptor} located?", status="blueprint"),
    _template("new_metro_station_country", "Geography", "Place", "which_country_station_located", "Q928830", "metro station", "P571", "P17", "country", "In which country is the metro station {descriptor} located?", status="blueprint"),
    _template("new_bridge_crosses", "Geography", "Place", "what_body_of_water_bridge_crosses", "Q12280", "bridge", "P571", "P177", "crosses", "What body of water does the bridge {descriptor} cross?", status="blueprint"),
    _template("new_airport_serves_city", "Geography", "Place", "which_city_airport_serves", "Q1248784", "airport", "P571", "P131", "located in administrative territorial entity", "Which city includes the airport {descriptor}?", status="blueprint"),
    _template("new_trail_country", "Geography", "Place", "which_country_trail_located", "Q179049", "trail", "P571", "P17", "country", "In which country is the trail {descriptor} located?", status="blueprint"),
    # Politics and Law
    _template("law_jurisdiction", "Politics and Law", "Place", "which_jurisdiction_law", "Q7748", "law", "P577", "P1001", "applies to jurisdiction", "In which jurisdiction does the law {descriptor} apply?", status="blueprint"),
    _template("law_legislature", "Politics and Law", "Organization", "which_legislature_passed_law", "Q7748", "law", "P577", "P467", "legislated by", "Which legislature enacted the law {descriptor}?", status="blueprint"),
    _template("treaty_signatory_country", "Politics and Law", "Place", "which_country_signed_treaty", "Q131569", "treaty", "P577", "P17", "country", "Which country is associated with the treaty {descriptor}?", status="blueprint"),
    _template("court_case_court", "Politics and Law", "Organization", "which_court_decided_case", "Q2334719", "legal case", "P585", "P1591", "defendant", "Which court decided the case {descriptor}?", status="blueprint"),
    _template("policy_department", "Politics and Law", "Organization", "which_department_issued_policy", "Q49884", "government policy", "P577", "P749", "parent organization", "Which department issued the policy {descriptor}?", status="blueprint"),
    # Economy and Business
    _template("startup_founder", "Economy and Business", "Person", "who_founded_startup", "Q4830453", "business", "P571", "P112", "founder", "Who founded the startup {descriptor}?", status="blueprint"),
    _template("company_founded_country", "Economy and Business", "Place", "which_country_company_founded", "Q783794", "company", "P571", "P495", "country of origin", "In which country was the company {descriptor} founded?", status="blueprint"),
    _template("product_manufacturer", "Economy and Business", "Organization", "which_company_manufactured_product", "Q2424752", "product", "P577", "P176", "manufacturer", "Which company manufactured the product {descriptor}?", status="blueprint"),
    _template("exchange_operator", "Economy and Business", "Organization", "which_company_operates_exchange", "Q11654", "stock exchange", "P571", "P137", "operator", "Which company operates the exchange {descriptor}?", status="blueprint"),
    # Society and Culture
    _template("festival_host_city", "Society and Culture", "Place", "which_city_hosts_festival", "Q132241", "festival", "P585", "P131", "located in administrative territorial entity", "Which city hosted {descriptor}?", status="blueprint"),
    _template("museum_founder", "Society and Culture", "Person", "who_founded_museum", "Q33506", "museum", "P571", "P112", "founder", "Who founded the museum {descriptor}?", status="blueprint"),
    _template("award_conferred_by", "Society and Culture", "Organization", "which_body_conferred_award", "Q618779", "award", "P571", "P1027", "conferred by", "Which organization confers the award {descriptor}?", status="blueprint"),
    _template("exhibition_museum", "Society and Culture", "Organization", "which_museum_hosted_exhibition", "Q464980", "exhibition", "P585", "P276", "location", "Which museum hosted the exhibition {descriptor}?", status="blueprint"),
    _template("event_venue", "Society and Culture", "Place", "where_event_held", "Q1656682", "event", "P585", "P276", "location", "Where was {descriptor} held?", status="blueprint"),
    # Philosophy and Religion
    _template("religious_leader_successor", "Philosophy and Religion", "Person", "who_succeeded_religious_leader", "Q246434", "religious office", "P580", "P156", "followed by", "Who succeeded {descriptor}?", composition_style="fact_join", status="blueprint"),
    _template("encyclical_author", "Philosophy and Religion", "Person", "who_wrote_encyclical", "Q240157", "encyclical", "P577", "P50", "author", "Who wrote the encyclical {descriptor}?", status="blueprint"),
    _template("religious_text_language", "Philosophy and Religion", "Language", "what_language_religious_text", "Q179461", "religious text", "P577", "P364", "original language of work", "What language was the religious text {descriptor} originally written in?", status="blueprint"),
    _template("temple_country", "Philosophy and Religion", "Place", "which_country_temple_located", "Q44539", "temple", "P571", "P17", "country", "In which country is the temple {descriptor} located?", status="blueprint"),
    _template("philosophy_book_author", "Philosophy and Religion", "Person", "who_wrote_philosophy_book", "Q571", "book", "P577", "P50", "author", "Who wrote the philosophy book {descriptor}?", status="blueprint"),
    # Language and Literature
    _template("poetry_collection_author", "Language and Literature", "Person", "who_wrote_poetry_collection", "Q12106333", "poetry collection", "P577", "P50", "author", "Who wrote the poetry collection {descriptor}?", status="blueprint"),
    _template("book_publisher", "Language and Literature", "Organization", "which_publisher_released_book", "Q571", "book", "P577", "P123", "publisher", "Which publisher released the book {descriptor}?", status="blueprint"),
    _template("novella_original_language", "Language and Literature", "Language", "what_language_novella_originally_written", "Q1238720", "novella", "P577", "P364", "original language of work", "What language was the novella {descriptor} originally written in?", status="blueprint"),
    _template("essay_collection_author", "Language and Literature", "Person", "who_wrote_essay_collection", "Q267628", "essay collection", "P577", "P50", "author", "Who wrote the essay collection {descriptor}?", status="blueprint"),
    _template("literary_magazine_country", "Language and Literature", "Place", "which_country_literary_magazine", "Q41298", "magazine", "P571", "P17", "country", "In which country is the magazine {descriptor} based?", status="blueprint"),
    # Arts and Media
    _template("film_screenwriter", "Arts and Media", "Person", "who_wrote_film", "Q11424", "film", "P577", "P58", "screenwriter", "Who wrote the film {descriptor}?", status="blueprint"),
    _template("film_based_on", "Arts and Media", "Work", "what_work_film_based_on", "Q11424", "film", "P577", "P144", "based on", "What work was the film {descriptor} based on?", status="blueprint"),
    _template("tv_series_creator", "Arts and Media", "Person", "who_created_series", "Q5398426", "television series", "P577", "P170", "creator", "Who created the television series {descriptor}?", status="blueprint"),
    _template("documentary_narrator", "Arts and Media", "Person", "who_narrated_documentary", "Q93204", "documentary film", "P577", "P2438", "narrator", "Who narrated the documentary {descriptor}?", status="blueprint"),
    _template("music_video_director", "Arts and Media", "Person", "who_directed_music_video", "Q64100970", "music video", "P577", "P57", "director", "Who directed the music video {descriptor}?", status="blueprint"),
    _template("podcast_host", "Arts and Media", "Person", "who_hosts_podcast", "Q24634210", "podcast", "P577", "P371", "presenter", "Who hosts the podcast {descriptor}?", status="blueprint"),
    _template("album_label", "Arts and Media", "Organization", "which_label_released_album", "Q482994", "album", "P577", "P264", "record label", "Which label released the album {descriptor}?", status="blueprint"),
    _template("comic_writer", "Arts and Media", "Person", "who_wrote_comic", "Q1004", "comic", "P577", "P50", "author", "Who wrote the comic {descriptor}?", status="blueprint"),
    _template("animation_studio", "Arts and Media", "Organization", "which_studio_produced_animation", "Q202866", "animated film", "P577", "P272", "production company", "Which studio produced the animated film {descriptor}?", status="blueprint"),
    _template("theater_location", "Arts and Media", "Place", "where_theater_located", "Q24354", "theatre", "P571", "P17", "country", "In which country is the theatre {descriptor} located?", status="blueprint"),
    # Sports and Recreation
    _template("tournament_host_country", "Sports and Recreation", "Place", "which_country_hosted_tournament", "Q132241", "tournament", "P585", "P17", "country", "Which country hosted {descriptor}?", status="blueprint"),
    _template("stadium_architect", "Sports and Recreation", "Person", "who_designed_stadium", "Q483110", "stadium", "P571", "P84", "architect", "Who designed the stadium {descriptor}?", status="blueprint"),
    _template("sports_venue_city", "Sports and Recreation", "Place", "which_city_sports_venue_located", "Q1076486", "sports venue", "P571", "P131", "located in administrative territorial entity", "Which city includes the sports venue {descriptor}?", status="blueprint"),
    _template("club_founder", "Sports and Recreation", "Person", "who_founded_club", "Q847017", "sports club", "P571", "P112", "founder", "Who founded the club {descriptor}?", status="blueprint"),
    _template("competition_venue", "Sports and Recreation", "Place", "where_competition_held", "Q16510064", "sports competition", "P585", "P276", "location", "Where was {descriptor} held?", status="blueprint"),
    # Education
    _template("graduate_before_employer", "Education", "Organization", "which_university_before_employer", "Q5", "human", "P569", "P69", "educated at", "From which university did {descriptor} graduate before working at {employer_label}?", composition_style="fact_join", status="blueprint"),
    _template("degree_granting_university", "Education", "Organization", "which_university_granted_degree", "Q189533", "degree", "P577", "P1027", "conferred by", "Which university grants the degree {descriptor}?", status="blueprint"),
    _template("school_founder", "Education", "Person", "who_founded_school", "Q3914", "school", "P571", "P112", "founder", "Who founded the school {descriptor}?", status="blueprint"),
    _template("curriculum_author", "Education", "Person", "who_wrote_curriculum", "Q11774891", "curriculum", "P577", "P50", "author", "Who wrote the curriculum {descriptor}?", status="blueprint"),
    _template("textbook_publisher", "Education", "Organization", "which_publisher_released_textbook", "Q571", "textbook", "P577", "P123", "publisher", "Which publisher released the textbook {descriptor}?", status="blueprint"),
    # Mathematics
    _template("math_textbook_author", "Mathematics", "Person", "who_wrote_math_textbook", "Q571", "book", "P577", "P50", "author", "Who wrote the mathematics book {descriptor}?", status="blueprint"),
    _template("math_software_developer", "Mathematics", "Organization", "which_company_developed_math_software", "Q7397", "software", "P577", "P178", "developer", "Which company developed the mathematics software {descriptor}?", status="blueprint"),
    _template("math_paper_journal", "Mathematics", "Organization", "which_journal_published_math_article", "Q13442814", "scholarly article", "P577", "P1433", "published in", "In which journal was the mathematics article {descriptor} published?", status="blueprint"),
    _template("dataset_creator_math", "Mathematics", "Person", "who_created_math_dataset", "Q1172284", "dataset", "P577", "P170", "creator", "Who created the dataset {descriptor}?", status="blueprint"),
    # Physical Sciences
    _template("chemistry_article_journal", "Physical Sciences", "Organization", "which_journal_published_chemistry_article", "Q13442814", "scholarly article", "P577", "P1433", "published in", "In which journal was the chemistry article {descriptor} published?", status="blueprint"),
    _template("physics_book_author", "Physical Sciences", "Person", "who_wrote_physics_book", "Q571", "book", "P577", "P50", "author", "Who wrote the physics book {descriptor}?", status="blueprint"),
    _template("instrument_manufacturer", "Physical Sciences", "Organization", "which_company_made_instrument", "Q34379", "scientific instrument", "P577", "P176", "manufacturer", "Which company manufactured the instrument {descriptor}?", status="blueprint"),
    _template("space_telescope_operator", "Physical Sciences", "Organization", "which_agency_operates_telescope", "Q2133344", "space telescope", "P571", "P137", "operator", "Which agency operates the telescope {descriptor}?", status="blueprint"),
    _template("physical_science_dataset_creator", "Physical Sciences", "Person", "who_created_science_dataset", "Q1172284", "dataset", "P577", "P170", "creator", "Who created the physical science dataset {descriptor}?", status="blueprint"),
    # Life Sciences
    _template("genome_project_lead_org", "Life Sciences", "Organization", "which_org_led_genome_project", "Q3966", "genome project", "P577", "P749", "parent organization", "Which organization led the genome project {descriptor}?", status="blueprint"),
    _template("species_described_by", "Life Sciences", "Person", "who_described_species", "Q16521", "taxon", "P577", "P405", "taxon author", "Who first described the species {descriptor}?", status="blueprint"),
    _template("bioinformatics_software_developer", "Life Sciences", "Organization", "which_company_developed_bioinformatics_software", "Q7397", "software", "P577", "P178", "developer", "Which company developed the bioinformatics software {descriptor}?", status="blueprint"),
    _template("biology_article_journal", "Life Sciences", "Organization", "which_journal_published_biology_article", "Q13442814", "scholarly article", "P577", "P1433", "published in", "In which journal was the biology article {descriptor} published?", status="blueprint"),
    _template("biobank_country", "Life Sciences", "Place", "which_country_biobank_located", "Q4915012", "biobank", "P571", "P17", "country", "In which country is the biobank {descriptor} located?", status="blueprint"),
    # Medicine and Health
    _template("medicine_active_ingredient", "Medicine and Health", "Other", "what_active_ingredient_medicine", "Q12140", "medication", "P577", "P3781", "active ingredient in pharmaceutical product", "What is the main active ingredient in the medicine {descriptor}?", status="blueprint"),
    _template("vaccine_developer", "Medicine and Health", "Organization", "which_company_developed_vaccine", "Q877194", "vaccine", "P577", "P178", "developer", "Which company developed the vaccine {descriptor}?", status="blueprint"),
    _template("hospital_country", "Medicine and Health", "Place", "which_country_hospital_located", "Q16917", "hospital", "P571", "P17", "country", "In which country is the hospital {descriptor} located?", status="blueprint"),
    _template("clinical_guideline_author", "Medicine and Health", "Organization", "which_body_wrote_guideline", "Q617602", "clinical guideline", "P577", "P50", "author", "Which organization wrote the guideline {descriptor}?", status="blueprint"),
    _template("medical_device_manufacturer", "Medicine and Health", "Organization", "which_company_made_medical_device", "Q174784", "medical device", "P577", "P176", "manufacturer", "Which company manufactured the medical device {descriptor}?", status="blueprint"),
    # Earth, Environment, and Space
    _template("spacecraft_operator", "Earth, Environment, and Space", "Organization", "which_agency_operates_spacecraft", "Q40218", "spacecraft", "P577", "P137", "operator", "Which agency operates the spacecraft {descriptor}?", status="blueprint"),
    _template("space_mission_launch_site", "Earth, Environment, and Space", "Place", "where_space_mission_launched", "Q2133344", "space mission", "P585", "P1427", "start point", "From where was {descriptor} launched?", status="blueprint"),
    _template("climate_report_author", "Earth, Environment, and Space", "Organization", "which_body_wrote_report", "Q10870555", "report", "P577", "P50", "author", "Which organization wrote the report {descriptor}?", status="blueprint"),
    _template("satellite_manufacturer", "Earth, Environment, and Space", "Organization", "which_company_built_satellite", "Q2537", "artificial satellite", "P577", "P176", "manufacturer", "Which company built the satellite {descriptor}?", status="blueprint"),
    _template("environmental_project_lead", "Earth, Environment, and Space", "Person", "who_led_environment_project", "Q170584", "project", "P571", "P1037", "director / manager", "Who led the project {descriptor}?", status="blueprint"),
    # Computer Science and AI
    _template("ai_model_developer", "Computer Science and AI", "Organization", "which_company_developed_model", "Q7397", "software", "P577", "P178", "developer", "Which company developed the model {descriptor}?", status="blueprint"),
    _template("programming_language_designer", "Computer Science and AI", "Person", "who_designed_programming_language", "Q9143", "programming language", "P577", "P287", "designed by", "Who designed the programming language {descriptor}?", status="blueprint"),
    _template("framework_license", "Computer Science and AI", "Other", "what_license_framework", "Q271680", "software framework", "P577", "P275", "copyright license", "What license does the framework {descriptor} use?", status="blueprint"),
    _template("dataset_creator_ai", "Computer Science and AI", "Person", "who_created_ai_dataset", "Q1172284", "dataset", "P577", "P170", "creator", "Who created the dataset {descriptor}?", status="blueprint"),
    _template("paper_conference_ai", "Computer Science and AI", "Organization", "which_conference_published_ai_paper", "Q13442814", "scholarly article", "P577", "P1433", "published in", "At which venue was the AI paper {descriptor} published?", status="blueprint"),
    _template("benchmark_release_date", "Computer Science and AI", "Date", "when_benchmark_released", "Q1172284", "dataset", "P577", "P577", "publication date", "On what day, month, and year was the benchmark {descriptor} released?", answer_format="date", temporal_mode="date_answer", date_answer_granularity="day", status="blueprint"),
    # Engineering and Technology
    _template("device_manufacturer", "Engineering and Technology", "Organization", "which_company_made_device", "Q1183543", "device", "P577", "P176", "manufacturer", "Which company manufactured the device {descriptor}?", status="blueprint"),
    _template("robot_creator", "Engineering and Technology", "Person", "who_created_robot", "Q11012", "robot", "P571", "P170", "creator", "Who created the robot {descriptor}?", status="blueprint"),
    _template("vehicle_designer", "Engineering and Technology", "Person", "who_designed_vehicle", "Q42889", "vehicle", "P577", "P287", "designed by", "Who designed the vehicle {descriptor}?", status="blueprint"),
    _template("chip_architecture_designer", "Engineering and Technology", "Organization", "which_company_designed_chip_architecture", "Q11426", "microprocessor", "P577", "P287", "designed by", "Which company designed the chip {descriptor}?", status="blueprint"),
    _template("product_release_date", "Engineering and Technology", "Date", "when_product_released", "Q2424752", "product", "P577", "P577", "publication date", "On what day, month, and year was the product {descriptor} released?", answer_format="date", temporal_mode="date_answer", date_answer_granularity="day", status="blueprint"),
    # Architecture and Transportation
    _template("rail_station_country", "Architecture and Transportation", "Place", "which_country_station_located_arch", "Q55488", "railway station", "P571", "P17", "country", "In which country is the railway station {descriptor} located?", status="blueprint"),
    _template("bridge_architect", "Architecture and Transportation", "Person", "who_designed_bridge", "Q12280", "bridge", "P571", "P84", "architect", "Who designed the bridge {descriptor}?", status="blueprint"),
    _template("port_operator", "Architecture and Transportation", "Organization", "which_company_operates_port", "Q44782", "port", "P571", "P137", "operator", "Which organization operates the port {descriptor}?", status="blueprint"),
    _template("train_manufacturer", "Architecture and Transportation", "Organization", "which_company_built_train", "Q870", "train", "P577", "P176", "manufacturer", "Which company built the train {descriptor}?", status="blueprint"),
    _template("terminal_opening_date", "Architecture and Transportation", "Date", "when_terminal_opened", "Q55488", "terminal", "P571", "P571", "inception", "On what day, month, and year did the terminal {descriptor} open?", answer_format="date", temporal_mode="date_answer", date_answer_granularity="day", status="blueprint"),
    # Food, Agriculture, and Daily Life
    _template("beverage_manufacturer", "Food, Agriculture, and Daily Life", "Organization", "which_company_made_beverage", "Q40050", "beverage", "P577", "P176", "manufacturer", "Which company manufactured the beverage {descriptor}?", status="blueprint"),
    _template("crop_variety_developer", "Food, Agriculture, and Daily Life", "Organization", "which_org_developed_crop_variety", "Q11004", "crop", "P577", "P178", "developer", "Which organization developed the crop variety {descriptor}?", status="blueprint"),
    _template("kitchen_appliance_manufacturer", "Food, Agriculture, and Daily Life", "Organization", "which_company_made_appliance", "Q260521", "kitchen appliance", "P577", "P176", "manufacturer", "Which company manufactured the kitchen appliance {descriptor}?", status="blueprint"),
    _template("restaurant_founder", "Food, Agriculture, and Daily Life", "Person", "who_founded_restaurant", "Q11707", "restaurant", "P571", "P112", "founder", "Who founded the restaurant {descriptor}?", status="blueprint"),
    # Additional atemporal expansion templates
    _template("biography_place_of_death_recent_subject", "People", "Place", "where_person_died", "Q5", "human", "P569", "P20", "place of death", "Where did {descriptor} die?", status="blueprint"),
    _template("biography_occupation_recent_subject", "People", "Other", "what_occupation_person", "Q5", "human", "P569", "P106", "occupation", "What is the occupation of {descriptor}?", status="blueprint"),
    _template("biography_notable_work_recent_subject", "People", "Work", "what_notable_work_person", "Q5", "human", "P569", "P800", "notable work", "What is a notable work by {descriptor}?", status="blueprint"),
    _template("new_dam_country", "Geography", "Place", "which_country_dam_located", "Q12323", "dam", "P571", "P17", "country", "In which country is the dam {descriptor} located?", status="blueprint"),
    _template("new_nature_reserve_country", "Geography", "Place", "which_country_nature_reserve_located", "Q473972", "nature reserve", "P571", "P17", "country", "In which country is the nature reserve {descriptor} located?", status="blueprint"),
    _template("constitution_jurisdiction", "Politics and Law", "Place", "which_jurisdiction_constitution", "Q7755", "constitution", "P577", "P1001", "applies to jurisdiction", "To which jurisdiction does the constitution {descriptor} apply?", status="blueprint"),
    _template("government_agency_jurisdiction", "Politics and Law", "Place", "which_jurisdiction_agency", "Q327333", "government agency", "P571", "P1001", "applies to jurisdiction", "To which jurisdiction does the government agency {descriptor} apply?", status="blueprint"),
    _template("company_parent_organization", "Economy and Business", "Organization", "which_parent_company", "Q783794", "company", "P571", "P749", "parent organization", "Which organization is the parent of the company {descriptor}?", status="blueprint"),
    _template("company_industry", "Economy and Business", "Other", "what_industry_company", "Q783794", "company", "P571", "P452", "industry", "What industry is the company {descriptor} in?", status="blueprint"),
    _template("stock_exchange_country", "Economy and Business", "Place", "which_country_exchange_located", "Q11654", "stock exchange", "P571", "P17", "country", "In which country is the stock exchange {descriptor} located?", status="blueprint"),
    _template("library_country", "Society and Culture", "Place", "which_country_library_located", "Q7075", "library", "P571", "P17", "country", "In which country is the library {descriptor} located?", status="blueprint"),
    _template("heritage_site_country", "Society and Culture", "Place", "which_country_heritage_site_located", "Q9259", "heritage site", "P571", "P17", "country", "In which country is the heritage site {descriptor} located?", status="blueprint"),
    _template("church_country", "Philosophy and Religion", "Place", "which_country_church_located", "Q16970", "church building", "P571", "P17", "country", "In which country is the church {descriptor} located?", status="blueprint"),
    _template("monastery_country", "Philosophy and Religion", "Place", "which_country_monastery_located", "Q44613", "monastery", "P571", "P17", "country", "In which country is the monastery {descriptor} located?", status="blueprint"),
    _template("play_author", "Language and Literature", "Person", "who_wrote_play", "Q25379", "play", "P577", "P50", "author", "Who wrote the play {descriptor}?", status="blueprint"),
    _template("poem_author", "Language and Literature", "Person", "who_wrote_poem", "Q5185279", "poem", "P577", "P50", "author", "Who wrote the poem {descriptor}?", status="blueprint"),
    _template("newspaper_country", "Language and Literature", "Place", "which_country_newspaper_based", "Q11032", "newspaper", "P571", "P17", "country", "In which country is the newspaper {descriptor} based?", status="blueprint"),
    _template("opera_composer", "Arts and Media", "Person", "who_composed_opera", "Q1344", "opera", "P577", "P86", "composer", "Who composed the opera {descriptor}?", status="blueprint"),
    _template("film_production_company", "Arts and Media", "Organization", "which_company_produced_film", "Q11424", "film", "P577", "P272", "production company", "Which company produced the film {descriptor}?", status="blueprint"),
    _template("manga_author", "Arts and Media", "Person", "who_wrote_manga", "Q8274", "manga", "P577", "P50", "author", "Who wrote the manga {descriptor}?", status="blueprint"),
    _template("sports_league_operator", "Sports and Recreation", "Organization", "which_body_operates_league", "Q15991303", "sports league", "P571", "P137", "operator", "Which organization operates the league {descriptor}?", status="blueprint"),
    _template("sports_team_home_venue", "Sports and Recreation", "Place", "which_venue_team_plays_home", "Q847017", "sports club", "P571", "P115", "home venue", "At which venue does the team {descriptor} play home matches?", status="blueprint"),
    _template("university_country", "Education", "Place", "which_country_university_located", "Q3918", "university", "P571", "P17", "country", "In which country is the university {descriptor} located?", status="blueprint"),
    _template("textbook_author", "Education", "Person", "who_wrote_textbook", "Q571", "textbook", "P577", "P50", "author", "Who wrote the textbook {descriptor}?", status="blueprint"),
    _template("math_article_main_subject", "Mathematics", "Other", "what_subject_math_article", "Q13442814", "scholarly article", "P577", "P921", "main subject", "What is the main subject of the mathematics article {descriptor}?", status="blueprint"),
    _template("math_award_presenter", "Mathematics", "Organization", "which_body_presents_math_award", "Q618779", "award", "P571", "P1027", "conferred by", "Which organization confers the mathematics award {descriptor}?", status="blueprint"),
    _template("spacecraft_manufacturer", "Physical Sciences", "Organization", "which_company_built_spacecraft", "Q40218", "spacecraft", "P577", "P176", "manufacturer", "Which company built the spacecraft {descriptor}?", status="blueprint"),
    _template("scientific_instrument_operator", "Physical Sciences", "Organization", "which_body_operates_instrument", "Q34379", "scientific instrument", "P577", "P137", "operator", "Which organization operates the scientific instrument {descriptor}?", status="blueprint"),
    _template("species_parent_taxon", "Life Sciences", "Other", "what_parent_taxon_species", "Q16521", "taxon", "P577", "P171", "parent taxon", "What is the parent taxon of {descriptor}?", status="blueprint"),
    _template("taxonomy_database_creator", "Life Sciences", "Person", "who_created_taxonomy_dataset", "Q1172284", "dataset", "P577", "P170", "creator", "Who created the taxonomy dataset {descriptor}?", status="blueprint"),
    _template("medical_school_country", "Medicine and Health", "Place", "which_country_medical_school_located", "Q3914", "medical school", "P571", "P17", "country", "In which country is the medical school {descriptor} located?", status="blueprint"),
    _template("clinical_guideline_publisher", "Medicine and Health", "Organization", "which_publisher_guideline", "Q617602", "clinical guideline", "P577", "P123", "publisher", "Which publisher released the guideline {descriptor}?", status="blueprint"),
    _template("satellite_operator", "Earth, Environment, and Space", "Organization", "which_agency_operates_satellite", "Q2537", "artificial satellite", "P577", "P137", "operator", "Which agency operates the satellite {descriptor}?", status="blueprint"),
    _template("report_publisher", "Earth, Environment, and Space", "Organization", "which_publisher_report", "Q10870555", "report", "P577", "P123", "publisher", "Which publisher released the report {descriptor}?", status="blueprint"),
    _template("operating_system_developer", "Computer Science and AI", "Organization", "which_company_developed_operating_system", "Q9135", "operating system", "P577", "P178", "developer", "Which company developed the operating system {descriptor}?", status="blueprint"),
    _template("database_system_developer", "Computer Science and AI", "Organization", "which_company_developed_database_system", "Q176165", "database management system", "P577", "P178", "developer", "Which company developed the database system {descriptor}?", status="blueprint"),
    _template("software_license", "Computer Science and AI", "Other", "what_license_software", "Q7397", "software", "P577", "P275", "copyright license", "What license does the software {descriptor} use?", status="blueprint"),
    _template("aircraft_manufacturer", "Engineering and Technology", "Organization", "which_company_built_aircraft", "Q11436", "aircraft", "P577", "P176", "manufacturer", "Which company built the aircraft {descriptor}?", status="blueprint"),
    _template("engine_designer", "Engineering and Technology", "Person", "who_designed_engine", "Q44167", "engine", "P577", "P287", "designed by", "Who designed the engine {descriptor}?", status="blueprint"),
    _template("battery_manufacturer", "Engineering and Technology", "Organization", "which_company_made_battery", "Q11173", "battery", "P577", "P176", "manufacturer", "Which company manufactured the battery {descriptor}?", status="blueprint"),
    _template("airport_operator", "Architecture and Transportation", "Organization", "which_body_operates_airport", "Q1248784", "airport", "P571", "P137", "operator", "Which organization operates the airport {descriptor}?", status="blueprint"),
    _template("lighthouse_country", "Architecture and Transportation", "Place", "which_country_lighthouse_located", "Q39715", "lighthouse", "P571", "P17", "country", "In which country is the lighthouse {descriptor} located?", status="blueprint"),
    _template("cookbook_author", "Food, Agriculture, and Daily Life", "Person", "who_wrote_cookbook", "Q571", "cookbook", "P577", "P50", "author", "Who wrote the cookbook {descriptor}?", status="blueprint"),
    # Additional time-related join and date-answer templates
    _template("company_that_released_product_founder", "Economy and Business", "Person", "who_founded_company_that_released_product", "Q2424752", "product", "P577", "COMPOSED_PRODUCT_MANUFACTURER_FOUNDER", "founder of manufacturer", "Who founded the company that released the product {descriptor}?", composition_style="fact_join", temporal_mode="time_related_join", reasoning_recipe={"new_element_slot": "subject", "new_element_hop": 1, "required_reasoning_clues": ["released"]}, status="blueprint"),
    _template("company_that_developed_benchmark_founder", "Computer Science and AI", "Person", "who_founded_company_that_developed_benchmark", "Q1172284", "benchmark", "P577", "COMPOSED_BENCHMARK_DEVELOPER_FOUNDER", "founder of developer", "Who founded the organization that developed the benchmark {descriptor}?", composition_style="fact_join", temporal_mode="time_related_join", reasoning_recipe={"new_element_slot": "subject", "new_element_hop": 1, "required_reasoning_clues": ["developed"]}, status="blueprint"),
    _template("terminal_operator_country", "Architecture and Transportation", "Place", "which_country_operator_of_terminal", "Q55488", "terminal", "P571", "COMPOSED_TERMINAL_OPERATOR_COUNTRY", "country of operator", "In which country is the organization that operates the terminal {descriptor} based?", composition_style="fact_join", temporal_mode="time_related_join", reasoning_recipe={"new_element_slot": "subject", "new_element_hop": 1, "required_reasoning_clues": ["operates"]}, status="blueprint"),
    _template("tv_series_source_work_author", "Arts and Media", "Person", "who_wrote_source_work_for_series", "Q5398426", "television series", "P577", "COMPOSED_SOURCE_WORK_AUTHOR", "author of source work", "Who wrote the work that the television series {descriptor} was based on?", composition_style="fact_join", temporal_mode="time_related_join", reasoning_recipe={"new_element_slot": "subject", "new_element_hop": 1, "required_reasoning_clues": ["based on"]}, status="blueprint"),
    _template("footballer_goals_in_ordinal_tournament", "Sports and Recreation", "Number", "how_many_goals_footballer_in_ordinal_tournament", "Q937857", "association football player", "P585", "COMPOSED_ORDINAL_TOURNAMENT_GOALS", "goals scored in ordinal tournament", "How many goals did {descriptor} score in the {ordinal} tournament?", answer_format="number", composition_style="ordinal_fact", temporal_mode="time_related_join", reasoning_recipe={"new_element_slot": "relation", "new_element_hop": 2, "required_reasoning_clues": ["goals", "tournament"]}, status="blueprint"),
    _template("acquisition_purchase_price", "Economy and Business", "Number", "how_many_dollars_company_spent_to_acquire_target", "Q783794", "company", "P571", "COMPOSED_ACQUISITION_PRICE", "acquisition purchase price", "How many dollars did {acquirer_label} spend to acquire {descriptor}?", answer_format="number", composition_style="fact_join", temporal_mode="time_related_join", reasoning_recipe={"new_element_slot": "relation", "new_element_hop": 1, "required_reasoning_clues": ["acquire"]}, status="blueprint"),
    _template("person_birth_date", "People", "Date", "when_person_born", "Q5", "human", "P569", "P569", "date of birth", "On what day, month, and year was {descriptor} born?", answer_format="date", temporal_mode="date_answer", date_answer_granularity="day", status="blueprint"),
    _template("person_death_date", "People", "Date", "when_person_died", "Q5", "human", "P570", "P570", "date of death", "On what day, month, and year did {descriptor} die?", answer_format="date", temporal_mode="date_answer", date_answer_granularity="day", status="blueprint"),
    _template("film_release_date", "Arts and Media", "Date", "when_film_released", "Q11424", "film", "P577", "P577", "publication date", "On what day, month, and year was the film {descriptor} released?", answer_format="date", temporal_mode="date_answer", date_answer_granularity="day", status="blueprint"),
    # Number-related templates
    _template("paper_author_count", "Physical Sciences", "Number", "how_many_authors_paper", "Q13442814", "scholarly article", "P577", "P50", "author", "How many authors wrote the article {descriptor}?", answer_format="number", composition_style="fact_join", status="blueprint"),
    _template("math_article_author_count", "Mathematics", "Number", "how_many_authors_math_article", "Q13442814", "scholarly article", "P577", "P50", "author", "How many authors wrote the mathematics article {descriptor}?", answer_format="number", composition_style="fact_join", status="blueprint"),
    _template("biology_article_author_count", "Life Sciences", "Number", "how_many_authors_biology_article", "Q13442814", "scholarly article", "P577", "P50", "author", "How many authors wrote the biology article {descriptor}?", answer_format="number", composition_style="fact_join", status="blueprint"),
    _template("guideline_author_count", "Medicine and Health", "Number", "how_many_authors_guideline", "Q617602", "clinical guideline", "P577", "P50", "author", "How many authors wrote the guideline {descriptor}?", answer_format="number", composition_style="fact_join", status="blueprint"),
    _template("report_author_count", "Earth, Environment, and Space", "Number", "how_many_authors_report", "Q10870555", "report", "P577", "P50", "author", "How many authors wrote the report {descriptor}?", answer_format="number", composition_style="fact_join", status="blueprint"),
    _template("album_track_count", "Arts and Media", "Number", "how_many_tracks_album", "Q482994", "album", "P577", "P658", "tracklist", "How many tracks are on the album {descriptor}?", answer_format="number", composition_style="fact_join", status="blueprint"),
    _template("story_collection_story_count", "Language and Literature", "Number", "how_many_stories_collection", "Q13136", "short story collection", "P577", "P527", "has part", "How many stories are in the collection {descriptor}?", answer_format="number", composition_style="fact_join", status="blueprint"),
    _template("company_founder_count", "Economy and Business", "Number", "how_many_founders_company", "Q783794", "company", "P571", "P112", "founder", "How many founders did the company {descriptor} have?", answer_format="number", composition_style="fact_join", status="blueprint"),
    _template("startup_founder_count", "Economy and Business", "Number", "how_many_founders_startup", "Q4830453", "business", "P571", "P112", "founder", "How many founders did the startup {descriptor} have?", answer_format="number", composition_style="fact_join", status="blueprint"),
    _template("treaty_signatory_count", "Politics and Law", "Number", "how_many_signatories_treaty", "Q131569", "treaty", "P577", "P17", "country", "How many signatories did the treaty {descriptor} have?", answer_format="number", composition_style="fact_join", status="blueprint"),
    _template("festival_day_count", "Society and Culture", "Number", "how_many_days_festival", "Q132241", "festival", "P585", "P580", "start time", "How many days did {descriptor} last?", answer_format="number", composition_style="fact_join", status="blueprint"),
    _template("spacecraft_crew_count", "Earth, Environment, and Space", "Number", "how_many_crew_spacecraft", "Q40218", "spacecraft", "P577", "P1029", "crew member", "How many crew members were on {descriptor}?", answer_format="number", composition_style="fact_join", status="blueprint"),
    _template("spacecraft_payload_count", "Earth, Environment, and Space", "Number", "how_many_payloads_spacecraft", "Q40218", "spacecraft", "P577", "P527", "has part", "How many payloads did {descriptor} carry?", answer_format="number", composition_style="fact_join", status="blueprint"),
    _template("rover_wheel_count", "Engineering and Technology", "Number", "how_many_wheels_rover", "Q11012", "robot", "P571", "P527", "has part", "How many wheels does the rover {descriptor} have?", answer_format="number", composition_style="fact_join", status="blueprint"),
    _template("patent_inventor_count", "Engineering and Technology", "Number", "how_many_inventors_patent", "Q253623", "patent", "P577", "P61", "discoverer or inventor", "How many inventors are listed on the patent {descriptor}?", answer_format="number", composition_style="fact_join", status="blueprint"),
    _template("bridge_span_count", "Architecture and Transportation", "Number", "how_many_spans_bridge", "Q12280", "bridge", "P571", "P527", "has part", "How many spans does the bridge {descriptor} have?", answer_format="number", composition_style="fact_join", status="blueprint"),
    _template("sports_event_host_count", "Sports and Recreation", "Number", "how_many_host_cities_event", "Q16510064", "sports competition", "P585", "P276", "location", "How many host locations were used for {descriptor}?", answer_format="number", composition_style="fact_join", status="blueprint"),
    _template("textbook_editor_count", "Education", "Number", "how_many_editors_textbook", "Q571", "textbook", "P577", "P98", "editor", "How many editors worked on the textbook edition {descriptor}?", answer_format="number", composition_style="fact_join", status="blueprint"),
    _template("medicine_ingredient_count", "Medicine and Health", "Number", "how_many_active_ingredients_medicine", "Q12140", "medication", "P577", "P3781", "active ingredient in pharmaceutical product", "How many active ingredients are in the medicine {descriptor}?", answer_format="number", composition_style="fact_join", status="blueprint"),
    _template("dataset_language_count", "Computer Science and AI", "Number", "how_many_languages_dataset", "Q1172284", "dataset", "P577", "P407", "language of work or name", "How many languages are represented in the dataset {descriptor}?", answer_format="number", composition_style="fact_join", status="blueprint"),
    _template("project_partner_count", "Engineering and Technology", "Number", "how_many_partners_project", "Q170584", "project", "P571", "P749", "parent organization", "How many partner organizations were involved in the project {descriptor}?", answer_format="number", composition_style="fact_join", status="blueprint"),
    # Dynamic ordinal templates
    _template("ordinal_country_president", "Politics and Law", "Person", "who_was_ordinal_president", "Q6256", "country", "P585", "P39", "position held", "Who was the {ordinal} president of {descriptor}?", composition_style="ordinal_fact", status="blueprint"),
    _template("ordinal_country_prime_minister", "Politics and Law", "Person", "who_was_ordinal_prime_minister", "Q6256", "country", "P585", "P39", "position held", "Who was the {ordinal} prime minister of {descriptor}?", composition_style="ordinal_fact", status="blueprint"),
    _template("ordinal_tournament_winner", "Sports and Recreation", "Person", "who_won_ordinal_tournament", "Q132241", "tournament", "P585", "P1346", "winner", "Who won the {ordinal} edition of {descriptor}?", composition_style="ordinal_fact", temporal_mode="time_related_join", reasoning_recipe={"new_element_slot": "subject", "new_element_hop": 1}, status="blueprint"),
    _template("ordinal_tournament_host_city", "Sports and Recreation", "Place", "which_city_hosted_ordinal_tournament", "Q132241", "tournament", "P585", "P131", "located in administrative territorial entity", "Which city hosted the {ordinal} edition of {descriptor}?", composition_style="ordinal_fact", status="blueprint"),
    _template("ordinal_religious_leader", "Philosophy and Religion", "Person", "who_was_ordinal_religious_leader", "Q246434", "religious office", "P580", "P39", "position held", "Who was the {ordinal} leader of {descriptor}?", composition_style="ordinal_fact", status="blueprint"),
    _template("ordinal_university_chancellor", "Education", "Person", "who_was_ordinal_university_chancellor", "Q3918", "university", "P585", "P39", "position held", "Who was the {ordinal} chancellor of {descriptor}?", composition_style="ordinal_fact", status="blueprint"),
    _template("ordinal_company_ceo", "Economy and Business", "Person", "who_was_ordinal_company_ceo", "Q783794", "company", "P585", "P169", "chief executive officer", "Who was the {ordinal} chief executive officer of {descriptor}?", composition_style="ordinal_fact", status="blueprint"),
    _template("ordinal_space_mission_commander", "Earth, Environment, and Space", "Person", "who_was_ordinal_space_mission_commander", "Q2133344", "space mission", "P585", "P1037", "director / manager", "Who was the {ordinal} commander associated with {descriptor}?", composition_style="ordinal_fact", status="blueprint"),
    _template("ordinal_film_in_series_director", "Arts and Media", "Person", "who_directed_ordinal_film_in_series", "Q24856", "film series", "P577", "P57", "director", "Who directed the {ordinal} film in the series {descriptor}?", composition_style="ordinal_fact", status="blueprint"),
    _template("ordinal_volume_author", "Language and Literature", "Person", "who_wrote_ordinal_volume", "Q571", "book series", "P577", "P50", "author", "Who wrote the {ordinal} volume in the series {descriptor}?", composition_style="ordinal_fact", status="blueprint"),
]


FILM_DIRECTOR_TEMPLATE = ACTIVE_TEMPLATE_CATALOG[0]


def get_active_templates() -> list[DomainTemplate]:
    """Return the currently active conservative template catalog."""
    return ACTIVE_TEMPLATE_CATALOG.copy()


def get_blueprint_templates() -> list[DomainTemplate]:
    """Return the large-scale blueprint catalog for future expansion."""
    return BLUEPRINT_TEMPLATE_CATALOG.copy()


def get_multi_hop_pilot_templates() -> list[DomainTemplate]:
    """Return the revalidated compositional multi-hop pilot templates."""
    return MULTI_HOP_PILOT_TEMPLATE_CATALOG.copy()


def get_date_answer_pilot_templates() -> list[DomainTemplate]:
    """Return the Stage 5B date-answer pilot templates."""
    return DATE_ANSWER_PILOT_TEMPLATE_CATALOG.copy()


def get_stage5b_templates() -> list[DomainTemplate]:
    """Return the Stage 5B activation set."""
    return (
        get_active_templates()
        + get_multi_hop_pilot_templates()
        + get_date_answer_pilot_templates()
    )


def get_all_templates() -> list[DomainTemplate]:
    """Return active, multi-hop pilot, and blueprint templates."""
    return (
        get_active_templates()
        + get_multi_hop_pilot_templates()
        + get_date_answer_pilot_templates()
        + get_blueprint_templates()
    )


def get_template_by_domain(domain: str) -> DomainTemplate | None:
    """Return a template by its domain key."""
    for template in get_all_templates():
        if template.domain == domain:
            return template
    return None


def get_stage1_templates() -> list[DomainTemplate]:
    """Backward-compatible alias for existing callers."""
    return get_active_templates()
