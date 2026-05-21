"""Expanded statusless single-hop template planning catalog."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
import re
from typing import Any

from .domain_templates import get_all_templates


ALLOWED_SINGLE_HOP_ANSWER_TYPES = ("Person", "Place", "Number", "Date", "Other")
SINGLE_HOP_TARGET_TOTAL = 400
SINGLE_HOP_TARGET_PER_DOMAIN = 20
SINGLE_HOP_TARGET_PER_ANSWER_TYPE = 80

SINGLE_HOP_EXPANSION_DOMAINS = (
    "Architecture and Transportation",
    "Arts and Media",
    "Computer Science and AI",
    "Earth, Environment, and Space",
    "Economy and Business",
    "Education",
    "Engineering and Technology",
    "Food, Agriculture, and Daily Life",
    "Geography",
    "History",
    "Language and Literature",
    "Life Sciences",
    "Mathematics",
    "Medicine and Health",
    "People",
    "Philosophy and Religion",
    "Physical Sciences",
    "Politics and Law",
    "Society and Culture",
    "Sports and Recreation",
)

LEGACY_ANSWER_TYPE_MAP = {
    "Date": "Date",
    "Person": "Person",
    "Place": "Place",
    "Number": "Number",
}

COMPARISON_WORDS = (
    "highest",
    "lowest",
    "largest",
    "smallest",
    "oldest",
    "newest",
    "youngest",
    "most",
    "least",
    "maximum",
    "minimum",
)


@dataclass(frozen=True, slots=True)
class SingleHopCatalogTemplate:
    """Statusless planning row for the expanded single-hop catalog."""

    template_key: str
    domain: str
    subdomain: str
    answer_type: str
    subject_type_qid: str
    date_property_pid: str
    target_property_pid: str
    canonical_question_template: str
    subject_type_label: str
    target_property_label: str
    candidate_search_query: str
    answer_format: str
    temporal_mode: str
    origin: str
    time_invariance_note: str
    legacy_template_key: str = ""
    legacy_answer_type: str = ""
    source_template_key: str = ""

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serializable row."""
        return asdict(self)


def _variant(
    answer_type: str,
    question: str,
    subject_type_label: str,
    target_property_label: str,
    *,
    answer_format: str | None = None,
    temporal_mode: str | None = None,
) -> dict[str, str]:
    """Build a compact generated-template variant."""
    return {
        "answer_type": answer_type,
        "canonical_question_template": question,
        "subject_type_label": subject_type_label,
        "target_property_label": target_property_label,
        "subject_type_qid": _subject_type_qid(subject_type_label),
        "target_property_pid": _target_property_pid(target_property_label),
        "answer_format": answer_format or ("date" if answer_type == "Date" else "number" if answer_type == "Number" else "entity"),
        "temporal_mode": temporal_mode or ("date_answer" if answer_type == "Date" else "atemporal"),
    }


def _spec(
    name: str,
    keywords: tuple[str, ...],
    person: tuple[str, str, str],
    place: tuple[str, str, str],
    number: tuple[str, str, str],
    date: tuple[str, str, str],
    other: tuple[str, str, str],
) -> dict[str, Any]:
    """Build one subdomain specification with all five answer-type variants."""
    return {
        "name": name,
        "keywords": keywords,
        "variants": {
            "Person": _variant("Person", *person),
            "Place": _variant("Place", *place),
            "Number": _variant("Number", *number),
            "Date": _variant("Date", *date),
            "Other": _variant("Other", *other),
        },
    }


SUBJECT_TYPE_QIDS = {
    "AI model": "Q1172284",
    "academic degree": "Q189533",
    "administrative entity": "Q56061",
    "aircraft": "Q11436",
    "airport": "Q1248784",
    "airport terminal": "Q849706",
    "album": "Q482994",
    "animal species": "Q16521",
    "anthology": "Q105420",
    "archaeological site": "Q839954",
    "archive": "Q166118",
    "artwork": "Q838948",
    "asteroid": "Q3863",
    "award": "Q618779",
    "bank": "Q22687",
    "battle": "Q178561",
    "beverage": "Q40050",
    "biology dataset": "Q1172284",
    "bridge": "Q12280",
    "building": "Q41176",
    "business book": "Q571",
    "business report": "Q10870555",
    "chemical compound": "Q11173",
    "church": "Q16970",
    "city": "Q515",
    "clinical guideline": "Q617602",
    "comic": "Q1004",
    "company": "Q783794",
    "computer interface": "Q23808",
    "computing standard": "Q317623",
    "constitution": "Q7755",
    "creative work": "Q17537576",
    "crop variety": "Q4886",
    "database": "Q8513",
    "dataset": "Q1172284",
    "dish": "Q746549",
    "earthquake": "Q7944",
    "electronic device": "Q1183543",
    "encyclical": "Q240157",
    "engine": "Q44167",
    "environmental report": "Q10870555",
    "exhibition": "Q464980",
    "festival": "Q132241",
    "film": "Q11424",
    "game": "Q11410",
    "genome": "Q7020",
    "genome project": "Q170584",
    "geological formation": "Q736917",
    "government agency": "Q327333",
    "heritage site": "Q9259",
    "historical event": "Q13418847",
    "hospital": "Q16917",
    "household appliance": "Q57583712",
    "human": "Q5",
    "island": "Q23442",
    "lake": "Q23397",
    "law": "Q7748",
    "legal case": "Q2334719",
    "library": "Q7075",
    "magazine": "Q41298",
    "magazine issue": "Q28869365",
    "mathematical theorem": "Q65943",
    "mathematics article": "Q13442814",
    "mathematics award": "Q618779",
    "mathematics book": "Q571",
    "mathematics software": "Q7397",
    "medical device": "Q6554101",
    "medical school": "Q3914",
    "medicine": "Q12140",
    "mineral": "Q7946",
    "monastery": "Q44613",
    "monument": "Q4989906",
    "mountain": "Q8502",
    "movement": "Q49773",
    "municipality": "Q15284",
    "museum": "Q33506",
    "nature reserve": "Q179049",
    "newspaper": "Q11032",
    "novel": "Q8261",
    "painting": "Q3305213",
    "park": "Q22698",
    "philosophy book": "Q571",
    "physics article": "Q13442814",
    "plant species": "Q16521",
    "play": "Q25379",
    "poem": "Q5185279",
    "political party": "Q7278",
    "port": "Q44782",
    "product": "Q2424752",
    "programming language": "Q9143",
    "protected area": "Q473972",
    "public office": "Q4164871",
    "race": "Q40231",
    "race course": "Q1777138",
    "railway line": "Q728937",
    "railway station": "Q55488",
    "recipe": "Q219239",
    "religious movement": "Q49773",
    "religious office": "Q246434",
    "religious text": "Q179461",
    "restaurant": "Q11707",
    "river": "Q4022",
    "robot": "Q11012",
    "rover": "Q11012",
    "satellite": "Q2537",
    "scholarly article": "Q13442814",
    "scholarship": "Q230788",
    "school": "Q3914",
    "science dataset": "Q1172284",
    "scientific instrument": "Q39546",
    "sculpture": "Q860861",
    "ship": "Q11446",
    "software": "Q7397",
    "space mission": "Q2133344",
    "spacecraft": "Q40218",
    "species": "Q16521",
    "sports club": "Q847017",
    "sports team": "Q12973014",
    "sports tournament": "Q132241",
    "sports venue": "Q1076486",
    "stadium": "Q483110",
    "star": "Q523",
    "stock exchange": "Q11654",
    "telescope": "Q4213",
    "television program": "Q15416",
    "television series": "Q5398426",
    "temple": "Q44539",
    "textbook": "Q571",
    "treaty": "Q131569",
    "university": "Q3918",
    "vaccine": "Q134808",
    "vehicle": "Q42889",
    "video game": "Q7889",
    "volcano": "Q8072",
}

TARGET_PROPERTY_PIDS = {
    "IATA airport code": "P238",
    "IUCN protected area category": "P814",
    "academic affiliation": "P1416",
    "academic degree": "P512",
    "active ingredient": "P3781",
    "adoption date": "P577",
    "age at death": "P570",
    "alcohol by volume": "P2665",
    "aperture": "P2048",
    "applies to jurisdiction": "P1001",
    "appointed by": "P748",
    "approval date": "P577",
    "archipelago": "P706",
    "architect": "P84",
    "architectural style": "P149",
    "archive type": "P31",
    "area": "P2046",
    "article number": "P1545",
    "author": "P50",
    "award amount": "P2121",
    "award received date": "P166",
    "battery capacity": "P4140",
    "bed capacity": "P6801",
    "beverage type": "P279",
    "body length": "P2043",
    "brand": "P1716",
    "breeder": "P170",
    "budget": "P2769",
    "campus area": "P2046",
    "capacity": "P1083",
    "charted date": "P575",
    "chemical formula": "P274",
    "citation count": "P2860",
    "city": "P131",
    "collection": "P195",
    "collection size": "P1436",
    "collection type": "P31",
    "commander": "P1029",
    "completion date": "P1619",
    "conferred by": "P1027",
    "construction start date": "P1619",
    "copyright license": "P275",
    "country": "P17",
    "country of citizenship": "P27",
    "country of launch": "P495",
    "country of manufacture": "P495",
    "country of origin": "P495",
    "country of publication": "P495",
    "country of recording": "P495",
    "court": "P4884",
    "creator": "P170",
    "crosses": "P177",
    "cuisine": "P2012",
    "culture": "P2596",
    "currency": "P38",
    "data rate": "P3086",
    "database size": "P3575",
    "dataset size": "P3575",
    "date of birth": "P569",
    "decision date": "P585",
    "degree date": "P585",
    "designation date": "P580",
    "designed by": "P287",
    "designer": "P287",
    "developer": "P178",
    "diameter": "P2386",
    "dimension": "P2048",
    "discoverer": "P61",
    "discovery date": "P575",
    "discovery place": "P189",
    "discovery site": "P189",
    "distance": "P2043",
    "docket number": "P3295",
    "doctoral advisor": "P184",
    "dose": "P3433",
    "dose volume": "P2234",
    "drafter": "P50",
    "drainage basin": "P4614",
    "duration": "P2047",
    "editor": "P98",
    "educated at": "P69",
    "elevation above sea level": "P2044",
    "employer": "P108",
    "enactment date": "P577",
    "engine type": "P516",
    "engineer": "P631",
    "episode duration": "P2047",
    "father": "P22",
    "field of study": "P812",
    "field of work": "P101",
    "file format": "P2701",
    "file size": "P3575",
    "first ascender": "P576",
    "first ascent date": "P571",
    "first flight date": "P606",
    "first location": "P276",
    "first work date": "P577",
    "floor area": "P2046",
    "founder": "P112",
    "founding membership": "P2124",
    "fuel type": "P618",
    "genome size": "P3488",
    "genre": "P136",
    "gross tonnage": "P1093",
    "height": "P2048",
    "heritage designation": "P1435",
    "hospital type": "P31",
    "illustrator": "P110",
    "inception date": "P571",
    "industry": "P452",
    "influenced by": "P737",
    "initial public offering price": "P2139",
    "inscription date": "P580",
    "instance of": "P31",
    "introduction date": "P571",
    "inventor": "P61",
    "jurisdiction": "P1001",
    "language of work": "P407",
    "launch date": "P619",
    "launch site": "P1427",
    "launch vehicle": "P375",
    "leader": "P1037",
    "league": "P118",
    "legal field": "P1001",
    "legal form": "P1454",
    "legislated by": "P467",
    "length": "P2043",
    "license": "P275",
    "line count": "P1104",
    "lithology": "P518",
    "location": "P276",
    "main subject": "P921",
    "mass": "P2067",
    "material": "P186",
    "material used": "P186",
    "medical condition treated": "P2175",
    "membership": "P2124",
    "molar mass": "P2067",
    "mountain range": "P4552",
    "named by": "P3938",
    "negotiator": "P1891",
    "notable work": "P800",
    "number of pages": "P1104",
    "occupation": "P106",
    "ocean": "P206",
    "opening date": "P1619",
    "operating location": "P276",
    "operating system": "P306",
    "opinion author": "P50",
    "orbit type": "P522",
    "original air date": "P577",
    "original language of work": "P364",
    "original network": "P449",
    "package size": "P3575",
    "painter": "P170",
    "parameter count": "P1114",
    "parent organization": "P749",
    "parent taxon": "P171",
    "part of": "P361",
    "philosophical school": "P135",
    "place of birth": "P19",
    "place of composition": "P1071",
    "platform": "P400",
    "playing time": "P2047",
    "point in time": "P585",
    "political ideology": "P1142",
    "position held": "P39",
    "power consumption": "P2791",
    "power output": "P2109",
    "power source": "P618",
    "premiere date": "P1191",
    "premiere location": "P4647",
    "presentation venue": "P276",
    "prize amount": "P2121",
    "prize money": "P2121",
    "producer": "P162",
    "project leader": "P1037",
    "protection category": "P814",
    "proved by": "P61",
    "publication date": "P577",
    "published in": "P1433",
    "publisher": "P123",
    "record label": "P264",
    "registered capital": "P2139",
    "registration date": "P571",
    "release date": "P577",
    "religion": "P140",
    "religious tradition": "P361",
    "route length": "P2043",
    "runway length": "P2043",
    "school type": "P31",
    "section number": "P1545",
    "serves city": "P931",
    "serving size": "P1114",
    "ship class": "P289",
    "signature date": "P577",
    "signing location": "P276",
    "software size": "P3575",
    "spacecraft": "P375",
    "spectral range": "P3737",
    "spectral type": "P215",
    "sponsor": "P859",
    "sport": "P641",
    "start date": "P580",
    "start time": "P580",
    "strength": "P1120",
    "student count": "P2196",
    "studied organism": "P703",
    "surface": "P765",
    "taxon author": "P405",
    "taxon description date": "P574",
    "term length": "P2097",
    "tick size": "P2884",
    "track gauge": "P1064",
    "tradition": "P361",
    "translator": "P655",
    "type locality": "P5307",
    "type system": "P31",
    "unveiling date": "P571",
    "wheelbase": "P3039",
    "wingspan": "P2050",
    "word size": "P282",
    "work location": "P937",
    "yield": "P2197",
}

DATE_PROPERTY_BY_SUBJECT = {
    "human": "P569",
    "earthquake": "P585",
    "battle": "P580",
    "historical event": "P580",
    "race": "P585",
    "sports tournament": "P580",
    "space mission": "P619",
    "satellite": "P619",
    "spacecraft": "P619",
    "asteroid": "P575",
    "mineral": "P575",
    "chemical compound": "P575",
    "film": "P577",
    "album": "P577",
    "television program": "P577",
    "television series": "P577",
    "video game": "P577",
    "software": "P577",
    "dataset": "P577",
    "database": "P577",
    "scholarly article": "P577",
    "physics article": "P577",
    "mathematics article": "P577",
    "book": "P577",
    "novel": "P577",
    "poem": "P577",
    "play": "P577",
    "anthology": "P577",
    "textbook": "P577",
    "clinical guideline": "P577",
    "recipe": "P577",
}


def _subject_type_qid(label: str) -> str:
    """Return the closest Wikidata class QID for a generated subject label."""
    if label in SUBJECT_TYPE_QIDS:
        return SUBJECT_TYPE_QIDS[label]
    lowered = label.casefold()
    if "article" in lowered:
        return "Q13442814"
    if "book" in lowered or "textbook" in lowered:
        return "Q571"
    if "dataset" in lowered or "benchmark" in lowered:
        return "Q1172284"
    if "software" in lowered:
        return "Q7397"
    if "report" in lowered:
        return "Q10870555"
    if "species" in lowered or "taxon" in lowered:
        return "Q16521"
    if "award" in lowered or "prize" in lowered:
        return "Q618779"
    if "event" in lowered or "competition" in lowered or "tournament" in lowered:
        return "Q1656682"
    if "building" in lowered or "terminal" in lowered:
        return "Q41176"
    if "device" in lowered:
        return "Q1183543"
    return "Q35120"


def _target_property_pid(label: str) -> str:
    """Return the closest Wikidata property PID for a generated target relation."""
    return TARGET_PROPERTY_PIDS.get(label, "P31")


def _date_property_pid(subject_type_label: str, target_property_pid: str, answer_type: str) -> str:
    """Choose the date property used for single-hop candidate-window discovery."""
    if answer_type == "Date":
        return target_property_pid
    return DATE_PROPERTY_BY_SUBJECT.get(subject_type_label, "P571")


def _candidate_search_query(
    *,
    subject_type_qid: str,
    date_property_pid: str,
    target_property_pid: str,
    answer_format: str,
) -> str:
    """Build a WDQS-style candidate search query for the template row."""
    answer_filter = ""
    if answer_format == "entity":
        answer_filter = "\n  FILTER(ISIRI(?answer))."
    return (
        "SELECT ?item ?answer ?date WHERE {\n"
        f"  ?item wdt:P31/wdt:P279* wd:{subject_type_qid};\n"
        f"        wdt:{date_property_pid} ?date;\n"
        f"        wdt:{target_property_pid} ?answer."
        f"{answer_filter}\n"
        "}\n"
        "LIMIT {limit}"
    )


SINGLE_HOP_SUBDOMAIN_SPECS: dict[str, list[dict[str, Any]]] = {
    "Architecture and Transportation": [
        _spec("buildings", ("building", "tower", "skyscraper", "arena", "hall"), ("Who designed the building {descriptor}?", "building", "architect"), ("In which city is the building {descriptor} located?", "building", "city"), ("What is the height of the building {descriptor} in meters?", "building", "height"), ("On what month, day, and year did construction of the building {descriptor} begin?", "building", "construction start date"), ("What architectural style is the building {descriptor} known for?", "building", "architectural style")),
        _spec("bridges", ("bridge", "span", "viaduct"), ("Who engineered the bridge {descriptor}?", "bridge", "engineer"), ("What body of water does the bridge {descriptor} cross?", "bridge", "crosses"), ("What is the total length of the bridge {descriptor} in meters?", "bridge", "length"), ("On what month, day, and year did the bridge {descriptor} open?", "bridge", "opening date"), ("What material is the bridge {descriptor} made from?", "bridge", "material used")),
        _spec("airports", ("airport", "terminal", "runway"), ("Who designed the airport terminal {descriptor}?", "airport terminal", "architect"), ("Which city does the airport {descriptor} serve?", "airport", "serves city"), ("What is the runway length of the airport {descriptor} in meters?", "airport", "runway length"), ("On what month, day, and year did the airport {descriptor} open?", "airport", "opening date"), ("What IATA code identifies the airport {descriptor}?", "airport", "IATA airport code")),
        _spec("rail systems", ("rail", "station", "metro", "subway", "tram"), ("Who designed the railway station {descriptor}?", "railway station", "architect"), ("In which country is the railway line {descriptor} located?", "railway line", "country"), ("What is the route length of the railway line {descriptor} in kilometers?", "railway line", "route length"), ("On what month, day, and year did the railway station {descriptor} open?", "railway station", "opening date"), ("What railway gauge does the line {descriptor} use?", "railway line", "track gauge")),
        _spec("ships and ports", ("ship", "port", "harbor", "ferry"), ("Who designed the ship {descriptor}?", "ship", "designer"), ("In which country is the port {descriptor} located?", "port", "country"), ("What is the tonnage of the ship {descriptor}?", "ship", "gross tonnage"), ("On what month, day, and year was the ship {descriptor} launched?", "ship", "launch date"), ("What class does the ship {descriptor} belong to?", "ship", "ship class")),
    ],
    "Arts and Media": [
        _spec("films", ("film", "movie", "screenwriter", "documentary", "animation"), ("Who edited the film {descriptor}?", "film", "editor"), ("In which country was the film {descriptor} produced?", "film", "country of origin"), ("What is the runtime of the film {descriptor} in minutes?", "film", "duration"), ("On what month, day, and year did the film {descriptor} premiere?", "film", "premiere date"), ("What genre is the film {descriptor}?", "film", "genre")),
        _spec("television", ("television", "tv", "series", "episode"), ("Who created the television program {descriptor}?", "television program", "creator"), ("In which country did the television series {descriptor} originate?", "television series", "country of origin"), ("What is the runtime of an episode of {descriptor} in minutes?", "television series", "episode duration"), ("On what month, day, and year did the television series {descriptor} first air?", "television series", "original air date"), ("What network first aired the television series {descriptor}?", "television series", "original network")),
        _spec("music", ("album", "song", "opera", "music", "label", "podcast"), ("Who produced the album {descriptor}?", "album", "producer"), ("In which country was the album {descriptor} recorded?", "album", "country of recording"), ("What is the duration of the album {descriptor} in minutes?", "album", "duration"), ("On what month, day, and year was the album {descriptor} released?", "album", "publication date"), ("What record label released the album {descriptor}?", "album", "record label")),
        _spec("visual art", ("artwork", "painting", "sculpture", "mural"), ("Who painted the artwork {descriptor}?", "painting", "painter"), ("In which museum is the artwork {descriptor} held?", "artwork", "collection"), ("What is the height of the sculpture {descriptor} in centimeters?", "sculpture", "height"), ("On what month, day, and year was the exhibition for {descriptor} opened?", "exhibition", "opening date"), ("What material was used in the artwork {descriptor}?", "artwork", "material used")),
        _spec("comics and games", ("comic", "manga", "video game", "game"), ("Who illustrated the comic {descriptor}?", "comic", "illustrator"), ("In which country was the video game {descriptor} developed?", "video game", "country of origin"), ("What is the file size of the video game {descriptor} in megabytes?", "video game", "file size"), ("On what month, day, and year was the video game {descriptor} released?", "video game", "publication date"), ("What platform was the video game {descriptor} released for?", "video game", "platform")),
    ],
    "Computer Science and AI": [
        _spec("programming languages", ("programming language", "language"), ("Who designed the programming language {descriptor}?", "programming language", "designed by"), ("In which country did the programming language {descriptor} originate?", "programming language", "country of origin"), ("What is the number of bits in the word size of {descriptor}?", "programming language", "word size"), ("On what month, day, and year was the programming language {descriptor} first released?", "programming language", "inception date"), ("What typing discipline does the programming language {descriptor} use?", "programming language", "type system")),
        _spec("software", ("software", "operating system", "framework"), ("Who created the software project {descriptor}?", "software", "creator"), ("In which country was the software project {descriptor} developed?", "software", "country of origin"), ("What is the binary size of {descriptor} in megabytes?", "software", "software size"), ("On what month, day, and year was the software {descriptor} first released?", "software", "publication date"), ("What license does the software {descriptor} use?", "software", "copyright license")),
        _spec("databases", ("database", "dataset", "benchmark"), ("Who created the database {descriptor}?", "database", "creator"), ("In which country was the database {descriptor} created?", "database", "country of origin"), ("What is the storage size of the database {descriptor} in gigabytes?", "database", "database size"), ("On what month, day, and year was the dataset {descriptor} published?", "dataset", "publication date"), ("What format does the dataset {descriptor} use?", "dataset", "file format")),
        _spec("AI models", ("ai", "model", "machine learning", "neural"), ("Who created the AI model {descriptor}?", "AI model", "creator"), ("In which country was the AI model {descriptor} developed?", "AI model", "country of origin"), ("What is the parameter count of the AI model {descriptor}?", "AI model", "parameter count"), ("On what month, day, and year was the AI model {descriptor} released?", "AI model", "release date"), ("What license was the AI model {descriptor} released under?", "AI model", "license")),
        _spec("computer hardware interfaces", ("protocol", "interface", "standard", "file system"), ("Who designed the computing standard {descriptor}?", "computing standard", "designer"), ("In which country was the computing standard {descriptor} developed?", "computing standard", "country of origin"), ("What is the bit rate of the interface {descriptor} in megabits per second?", "computer interface", "data rate"), ("On what month, day, and year was the standard {descriptor} published?", "computing standard", "publication date"), ("What organization published the standard {descriptor}?", "computing standard", "publisher")),
    ],
    "Earth, Environment, and Space": [
        _spec("space missions", ("space mission", "mission"), ("Who commanded the space mission {descriptor}?", "space mission", "commander"), ("From which launch site did the mission {descriptor} lift off?", "space mission", "launch site"), ("What was the mission duration of {descriptor} in days?", "space mission", "duration"), ("On what month, day, and year was the mission {descriptor} launched?", "space mission", "launch date"), ("What spacecraft was used for the mission {descriptor}?", "space mission", "spacecraft")),
        _spec("satellites", ("satellite",), ("Who designed the satellite {descriptor}?", "satellite", "designer"), ("From which country was the satellite {descriptor} launched?", "satellite", "country of launch"), ("What is the mass of the satellite {descriptor} in kilograms?", "satellite", "mass"), ("On what month, day, and year was the satellite {descriptor} launched?", "satellite", "launch date"), ("What orbit type does the satellite {descriptor} use?", "satellite", "orbit type")),
        _spec("geology", ("volcano", "earthquake", "geology", "mineral"), ("Who first described the mineral {descriptor}?", "mineral", "discoverer"), ("In which country is the volcano {descriptor} located?", "volcano", "country"), ("What is the elevation of the volcano {descriptor} in meters?", "volcano", "elevation above sea level"), ("On what month, day, and year did the earthquake {descriptor} occur?", "earthquake", "point in time"), ("What rock type is associated with {descriptor}?", "geological formation", "lithology")),
        _spec("climate and environment", ("climate", "environment", "conservation", "reserve"), ("Who authored the environmental report {descriptor}?", "environmental report", "author"), ("In which country is the protected area {descriptor} located?", "protected area", "country"), ("What is the area of the protected area {descriptor} in square kilometers?", "protected area", "area"), ("On what month, day, and year was the protected area {descriptor} established?", "protected area", "inception date"), ("What IUCN category applies to the protected area {descriptor}?", "protected area", "IUCN protected area category")),
        _spec("astronomy", ("planet", "asteroid", "comet", "star", "telescope"), ("Who discovered the asteroid {descriptor}?", "asteroid", "discoverer"), ("From which observatory was the asteroid {descriptor} discovered?", "asteroid", "discovery site"), ("What is the diameter of the asteroid {descriptor} in kilometers?", "asteroid", "diameter"), ("On what month, day, and year was the asteroid {descriptor} discovered?", "asteroid", "discovery date"), ("What spectral type is the star {descriptor}?", "star", "spectral type")),
    ],
    "Economy and Business": [
        _spec("companies", ("company", "startup", "business"), ("Who founded the company {descriptor}?", "company", "founder"), ("In which country was the company {descriptor} founded?", "company", "country of origin"), ("What was the initial share price of {descriptor} in dollars?", "company", "initial public offering price"), ("On what month, day, and year was the company {descriptor} founded?", "company", "inception date"), ("What industry is the company {descriptor} associated with?", "company", "industry")),
        _spec("products", ("product", "brand"), ("Who designed the product {descriptor}?", "product", "designer"), ("In which country was the product {descriptor} manufactured?", "product", "country of manufacture"), ("What is the weight of the product {descriptor} in grams?", "product", "mass"), ("On what month, day, and year was the product {descriptor} released?", "product", "release date"), ("What brand is associated with the product {descriptor}?", "product", "brand")),
        _spec("financial markets", ("exchange", "stock", "market"), ("Who founded the stock exchange {descriptor}?", "stock exchange", "founder"), ("In which city is the stock exchange {descriptor} located?", "stock exchange", "city"), ("What is the tick size of the exchange {descriptor}?", "stock exchange", "tick size"), ("On what month, day, and year was the stock exchange {descriptor} founded?", "stock exchange", "inception date"), ("What currency is used by the exchange {descriptor}?", "stock exchange", "currency")),
        _spec("banks", ("bank", "credit union"), ("Who founded the bank {descriptor}?", "bank", "founder"), ("In which country was the bank {descriptor} founded?", "bank", "country of origin"), ("What was the registered capital of the bank {descriptor}?", "bank", "registered capital"), ("On what month, day, and year was the bank {descriptor} founded?", "bank", "inception date"), ("What legal form does the bank {descriptor} have?", "bank", "legal form")),
        _spec("business publications", ("business book", "annual report", "report"), ("Who wrote the business book {descriptor}?", "business book", "author"), ("In which country was the business report {descriptor} published?", "business report", "country of publication"), ("What is the page count of the business book {descriptor}?", "business book", "number of pages"), ("On what month, day, and year was the business report {descriptor} published?", "business report", "publication date"), ("What publisher released the business book {descriptor}?", "business book", "publisher")),
    ],
    "Education": [
        _spec("schools", ("school",), ("Who founded the school {descriptor}?", "school", "founder"), ("In which city is the school {descriptor} located?", "school", "city"), ("What is the enrollment of the school {descriptor}?", "school", "student count"), ("On what month, day, and year was the school {descriptor} founded?", "school", "inception date"), ("What type of school is {descriptor}?", "school", "school type")),
        _spec("universities", ("university", "college"), ("Who founded the university {descriptor}?", "university", "founder"), ("In which country is the university {descriptor} located?", "university", "country"), ("What is the campus area of the university {descriptor} in hectares?", "university", "campus area"), ("On what month, day, and year was the university {descriptor} founded?", "university", "inception date"), ("What academic affiliation is associated with {descriptor}?", "university", "academic affiliation")),
        _spec("degrees", ("degree", "diploma"), ("Who established the degree {descriptor}?", "academic degree", "creator"), ("In which country is the degree {descriptor} awarded?", "academic degree", "country"), ("What is the normal duration of the degree {descriptor} in years?", "academic degree", "duration"), ("On what month, day, and year was the degree {descriptor} established?", "academic degree", "inception date"), ("What field of study is the degree {descriptor} for?", "academic degree", "field of study")),
        _spec("textbooks", ("textbook", "curriculum"), ("Who edited the textbook {descriptor}?", "textbook", "editor"), ("In which country was the textbook {descriptor} published?", "textbook", "country of publication"), ("What is the page count of the textbook {descriptor}?", "textbook", "number of pages"), ("On what month, day, and year was the textbook {descriptor} published?", "textbook", "publication date"), ("What publisher released the textbook {descriptor}?", "textbook", "publisher")),
        _spec("academic awards", ("education award", "scholarship", "fellowship"), ("Who established the scholarship {descriptor}?", "scholarship", "founder"), ("In which country is the scholarship {descriptor} awarded?", "scholarship", "country"), ("What is the monetary value of the scholarship {descriptor}?", "scholarship", "award amount"), ("On what month, day, and year was the scholarship {descriptor} established?", "scholarship", "inception date"), ("What organization awards the scholarship {descriptor}?", "scholarship", "conferred by")),
    ],
    "Engineering and Technology": [
        _spec("aircraft", ("aircraft", "airplane"), ("Who designed the aircraft {descriptor}?", "aircraft", "designer"), ("In which country was the aircraft {descriptor} manufactured?", "aircraft", "country of manufacture"), ("What is the wingspan of the aircraft {descriptor} in meters?", "aircraft", "wingspan"), ("On what month, day, and year did the aircraft {descriptor} first fly?", "aircraft", "first flight date"), ("What engine type powers the aircraft {descriptor}?", "aircraft", "engine type")),
        _spec("vehicles", ("vehicle", "car", "automobile", "train"), ("Who designed the vehicle {descriptor}?", "vehicle", "designer"), ("In which country was the vehicle {descriptor} produced?", "vehicle", "country of origin"), ("What is the wheelbase of the vehicle {descriptor} in millimeters?", "vehicle", "wheelbase"), ("On what month, day, and year was the vehicle {descriptor} introduced?", "vehicle", "introduction date"), ("What platform does the vehicle {descriptor} use?", "vehicle", "platform")),
        _spec("electronics", ("device", "phone", "camera", "computer"), ("Who designed the device {descriptor}?", "electronic device", "designer"), ("In which country was the device {descriptor} manufactured?", "electronic device", "country of manufacture"), ("What is the battery capacity of the device {descriptor} in milliamp-hours?", "electronic device", "battery capacity"), ("On what month, day, and year was the device {descriptor} released?", "electronic device", "release date"), ("What operating system does the device {descriptor} use?", "electronic device", "operating system")),
        _spec("robots", ("robot", "rover"), ("Who created the robot {descriptor}?", "robot", "creator"), ("On which planet or body did the rover {descriptor} operate?", "rover", "operating location"), ("What is the mass of the robot {descriptor} in kilograms?", "robot", "mass"), ("On what month, day, and year did the robot {descriptor} begin operation?", "robot", "start time"), ("What power source does the robot {descriptor} use?", "robot", "power source")),
        _spec("industrial systems", ("engine", "battery", "chip", "microprocessor", "turbine"), ("Who designed the engine {descriptor}?", "engine", "designer"), ("In which country was the engine {descriptor} built?", "engine", "country of manufacture"), ("What is the power output of the engine {descriptor} in kilowatts?", "engine", "power output"), ("On what month, day, and year was the engine {descriptor} introduced?", "engine", "introduction date"), ("What fuel type does the engine {descriptor} use?", "engine", "fuel type")),
    ],
    "Food, Agriculture, and Daily Life": [
        _spec("foods", ("food", "dish", "recipe"), ("Who created the dish {descriptor}?", "dish", "creator"), ("In which country did the dish {descriptor} originate?", "dish", "country of origin"), ("What is the serving size of {descriptor} in grams?", "dish", "serving size"), ("On what month, day, and year was the recipe {descriptor} published?", "recipe", "publication date"), ("What cuisine does the dish {descriptor} belong to?", "dish", "cuisine")),
        _spec("beverages", ("beverage", "drink", "beer", "wine"), ("Who created the beverage {descriptor}?", "beverage", "creator"), ("In which country did the beverage {descriptor} originate?", "beverage", "country of origin"), ("What is the alcohol by volume of the beverage {descriptor}?", "beverage", "alcohol by volume"), ("On what month, day, and year was the beverage {descriptor} introduced?", "beverage", "introduction date"), ("What beverage type is {descriptor}?", "beverage", "beverage type")),
        _spec("crops", ("crop", "cultivar", "variety"), ("Who developed the crop variety {descriptor}?", "crop variety", "breeder"), ("In which country was the crop variety {descriptor} developed?", "crop variety", "country of origin"), ("What is the average yield of the crop variety {descriptor} in tonnes per hectare?", "crop variety", "yield"), ("On what month, day, and year was the crop variety {descriptor} registered?", "crop variety", "registration date"), ("What crop species does the variety {descriptor} belong to?", "crop variety", "parent taxon")),
        _spec("restaurants", ("restaurant", "cafe"), ("Who founded the restaurant {descriptor}?", "restaurant", "founder"), ("In which city is the restaurant {descriptor} located?", "restaurant", "city"), ("What is the seating capacity of the restaurant {descriptor}?", "restaurant", "capacity"), ("On what month, day, and year did the restaurant {descriptor} open?", "restaurant", "opening date"), ("What cuisine is served at the restaurant {descriptor}?", "restaurant", "cuisine")),
        _spec("household products", ("appliance", "kitchen", "household"), ("Who designed the appliance {descriptor}?", "household appliance", "designer"), ("In which country was the appliance {descriptor} manufactured?", "household appliance", "country of manufacture"), ("What is the power consumption of the appliance {descriptor} in watts?", "household appliance", "power consumption"), ("On what month, day, and year was the appliance {descriptor} released?", "household appliance", "release date"), ("What material is the appliance {descriptor} made from?", "household appliance", "material")),
    ],
    "Geography": [
        _spec("rivers and lakes", ("river", "lake", "body of water"), ("Who named the river {descriptor}?", "river", "named by"), ("In which country is the lake {descriptor} located?", "lake", "country"), ("What is the length of the river {descriptor} in kilometers?", "river", "length"), ("On what month, day, and year was the lake {descriptor} designated?", "lake", "designation date"), ("What drainage basin contains the river {descriptor}?", "river", "drainage basin")),
        _spec("mountains", ("mountain", "peak"), ("Who first climbed the mountain {descriptor}?", "mountain", "first ascender"), ("In which country is the mountain {descriptor} located?", "mountain", "country"), ("What is the elevation of the mountain {descriptor} in meters?", "mountain", "elevation above sea level"), ("On what month, day, and year was the first ascent of {descriptor} recorded?", "mountain", "first ascent date"), ("What mountain range includes {descriptor}?", "mountain", "mountain range")),
        _spec("islands", ("island", "archipelago"), ("Who discovered the island {descriptor}?", "island", "discoverer"), ("In which ocean is the island {descriptor} located?", "island", "ocean"), ("What is the area of the island {descriptor} in square kilometers?", "island", "area"), ("On what month, day, and year was the island {descriptor} first charted?", "island", "charted date"), ("What archipelago includes the island {descriptor}?", "island", "archipelago")),
        _spec("administrative places", ("city", "town", "municipality", "province"), ("Who founded the city {descriptor}?", "city", "founder"), ("In which country is the municipality {descriptor} located?", "municipality", "country"), ("What is the area of the municipality {descriptor} in square kilometers?", "municipality", "area"), ("On what month, day, and year was the municipality {descriptor} established?", "municipality", "inception date"), ("What administrative type is {descriptor}?", "administrative entity", "instance of")),
        _spec("protected places", ("park", "reserve", "trail", "heritage"), ("Who established the park {descriptor}?", "park", "founder"), ("In which country is the nature reserve {descriptor} located?", "nature reserve", "country"), ("What is the area of the park {descriptor} in hectares?", "park", "area"), ("On what month, day, and year was the nature reserve {descriptor} established?", "nature reserve", "inception date"), ("What protection category applies to {descriptor}?", "protected area", "protection category")),
    ],
    "History": [
        _spec("battles", ("battle", "siege"), ("Who commanded the battle {descriptor}?", "battle", "commander"), ("Where did the battle {descriptor} take place?", "battle", "location"), ("What was the troop strength at the battle {descriptor}?", "battle", "strength"), ("On what month, day, and year did the battle {descriptor} begin?", "battle", "start date"), ("What conflict included the battle {descriptor}?", "battle", "part of")),
        _spec("treaties and agreements", ("treaty", "agreement"), ("Who negotiated the treaty {descriptor}?", "treaty", "negotiator"), ("Where was the treaty {descriptor} signed?", "treaty", "signing location"), ("What was the duration of the treaty {descriptor} in years?", "treaty", "duration"), ("On what month, day, and year was the treaty {descriptor} signed?", "treaty", "signature date"), ("What language was the treaty {descriptor} written in?", "treaty", "language of work")),
        _spec("archaeological sites", ("archaeological", "site", "excavation"), ("Who discovered the archaeological site {descriptor}?", "archaeological site", "discoverer"), ("In which country is the archaeological site {descriptor} located?", "archaeological site", "country"), ("What is the area of the archaeological site {descriptor} in hectares?", "archaeological site", "area"), ("On what month, day, and year was the archaeological site {descriptor} discovered?", "archaeological site", "discovery date"), ("What culture is associated with the archaeological site {descriptor}?", "archaeological site", "culture")),
        _spec("historic events", ("historic event", "revolution", "uprising"), ("Who led the event {descriptor}?", "historical event", "leader"), ("Where did the event {descriptor} take place?", "historical event", "location"), ("What was the duration of the event {descriptor} in days?", "historical event", "duration"), ("On what month, day, and year did the event {descriptor} begin?", "historical event", "start date"), ("What larger period included the event {descriptor}?", "historical event", "part of")),
        _spec("monuments", ("monument", "memorial"), ("Who designed the monument {descriptor}?", "monument", "designer"), ("In which city is the monument {descriptor} located?", "monument", "city"), ("What is the height of the monument {descriptor} in meters?", "monument", "height"), ("On what month, day, and year was the monument {descriptor} unveiled?", "monument", "unveiling date"), ("What material is the monument {descriptor} made from?", "monument", "material used")),
    ],
    "Language and Literature": [
        _spec("novels", ("novel", "novella"), ("Who illustrated the novel {descriptor}?", "novel", "illustrator"), ("In which country was the novel {descriptor} published?", "novel", "country of publication"), ("What is the page count of the novel {descriptor}?", "novel", "number of pages"), ("On what month, day, and year was the novel {descriptor} published?", "novel", "publication date"), ("What genre is the novel {descriptor}?", "novel", "genre")),
        _spec("poetry", ("poem", "poetry"), ("Who translated the poem {descriptor}?", "poem", "translator"), ("In which country was the poem {descriptor} first published?", "poem", "country of publication"), ("What is the line count of the poem {descriptor}?", "poem", "line count"), ("On what month, day, and year was the poem {descriptor} published?", "poem", "publication date"), ("What language was the poem {descriptor} written in?", "poem", "language of work")),
        _spec("plays", ("play", "drama"), ("Who translated the play {descriptor}?", "play", "translator"), ("Where did the play {descriptor} premiere?", "play", "premiere location"), ("What is the runtime of the play {descriptor} in minutes?", "play", "duration"), ("On what month, day, and year did the play {descriptor} premiere?", "play", "premiere date"), ("What genre is the play {descriptor}?", "play", "genre")),
        _spec("periodicals", ("magazine", "newspaper", "journal"), ("Who founded the magazine {descriptor}?", "magazine", "founder"), ("In which country is the newspaper {descriptor} based?", "newspaper", "country"), ("What is the page count of the magazine issue {descriptor}?", "magazine issue", "number of pages"), ("On what month, day, and year was the magazine {descriptor} first published?", "magazine", "inception date"), ("What language is used by the newspaper {descriptor}?", "newspaper", "language of work")),
        _spec("literary collections", ("collection", "essay", "anthology"), ("Who edited the anthology {descriptor}?", "anthology", "editor"), ("In which country was the anthology {descriptor} published?", "anthology", "country of publication"), ("What is the page count of the anthology {descriptor}?", "anthology", "number of pages"), ("On what month, day, and year was the anthology {descriptor} published?", "anthology", "publication date"), ("What publisher released the anthology {descriptor}?", "anthology", "publisher")),
    ],
    "Life Sciences": [
        _spec("species and taxonomy", ("species", "taxon", "taxonomy"), ("Who named the species {descriptor}?", "species", "taxon author"), ("Where is the type locality of {descriptor}?", "species", "type locality"), ("What is the body length of {descriptor} in millimeters?", "species", "body length"), ("On what month, day, and year was the species {descriptor} described?", "species", "taxon description date"), ("What genus contains the species {descriptor}?", "species", "parent taxon")),
        _spec("genomics", ("genome", "biobank"), ("Who led the genome project {descriptor}?", "genome project", "project leader"), ("In which country was the genome project {descriptor} based?", "genome project", "country"), ("What is the genome size of {descriptor} in base pairs?", "genome", "genome size"), ("On what month, day, and year was the genome project {descriptor} launched?", "genome project", "start date"), ("What organism was studied by the genome project {descriptor}?", "genome project", "studied organism")),
        _spec("biology datasets", ("biology dataset", "bioinformatics", "dataset"), ("Who created the biology dataset {descriptor}?", "biology dataset", "creator"), ("In which country was the biology dataset {descriptor} created?", "biology dataset", "country of origin"), ("What is the size of the biology dataset {descriptor} in gigabytes?", "biology dataset", "dataset size"), ("On what month, day, and year was the biology dataset {descriptor} published?", "biology dataset", "publication date"), ("What file format does the biology dataset {descriptor} use?", "biology dataset", "file format")),
        _spec("botany", ("plant", "botany", "cultivar"), ("Who described the plant species {descriptor}?", "plant species", "taxon author"), ("Where is the type locality of the plant {descriptor}?", "plant species", "type locality"), ("What is the plant height of {descriptor} in centimeters?", "plant species", "height"), ("On what month, day, and year was the plant species {descriptor} described?", "plant species", "taxon description date"), ("What family contains the plant species {descriptor}?", "plant species", "parent taxon")),
        _spec("zoology", ("animal", "bird", "fish", "insect"), ("Who described the animal species {descriptor}?", "animal species", "taxon author"), ("Where is the type locality of the animal species {descriptor}?", "animal species", "type locality"), ("What is the wingspan of {descriptor} in centimeters?", "animal species", "wingspan"), ("On what month, day, and year was the animal species {descriptor} described?", "animal species", "taxon description date"), ("What family contains the animal species {descriptor}?", "animal species", "parent taxon")),
    ],
    "Mathematics": [
        _spec("theorems", ("theorem", "lemma"), ("Who proved the theorem {descriptor}?", "mathematical theorem", "proved by"), ("At which institution was the theorem {descriptor} first presented?", "mathematical theorem", "presentation venue"), ("What is the dimension used in the theorem {descriptor}?", "mathematical theorem", "dimension"), ("On what month, day, and year was the theorem {descriptor} published?", "mathematical theorem", "publication date"), ("What field of mathematics includes the theorem {descriptor}?", "mathematical theorem", "field of work")),
        _spec("mathematical papers", ("math paper", "article"), ("Who wrote the mathematics article {descriptor}?", "mathematics article", "author"), ("In which journal was the mathematics article {descriptor} published?", "mathematics article", "published in"), ("What is the page count of the mathematics article {descriptor}?", "mathematics article", "number of pages"), ("On what month, day, and year was the mathematics article {descriptor} published?", "mathematics article", "publication date"), ("What main subject does the mathematics article {descriptor} cover?", "mathematics article", "main subject")),
        _spec("mathematical software", ("math software", "software"), ("Who created the mathematics software {descriptor}?", "mathematics software", "creator"), ("In which country was the mathematics software {descriptor} developed?", "mathematics software", "country of origin"), ("What is the package size of the mathematics software {descriptor} in megabytes?", "mathematics software", "package size"), ("On what month, day, and year was the mathematics software {descriptor} released?", "mathematics software", "release date"), ("What license does the mathematics software {descriptor} use?", "mathematics software", "license")),
        _spec("mathematics books", ("math book", "textbook"), ("Who edited the mathematics book {descriptor}?", "mathematics book", "editor"), ("In which country was the mathematics book {descriptor} published?", "mathematics book", "country of publication"), ("What is the page count of the mathematics book {descriptor}?", "mathematics book", "number of pages"), ("On what month, day, and year was the mathematics book {descriptor} published?", "mathematics book", "publication date"), ("What publisher released the mathematics book {descriptor}?", "mathematics book", "publisher")),
        _spec("mathematics awards", ("math award", "prize"), ("Who established the mathematics award {descriptor}?", "mathematics award", "founder"), ("In which country is the mathematics award {descriptor} presented?", "mathematics award", "country"), ("What is the prize amount of the mathematics award {descriptor}?", "mathematics award", "prize amount"), ("On what month, day, and year was the mathematics award {descriptor} established?", "mathematics award", "inception date"), ("What organization presents the mathematics award {descriptor}?", "mathematics award", "conferred by")),
    ],
    "Medicine and Health": [
        _spec("hospitals", ("hospital", "clinic"), ("Who founded the hospital {descriptor}?", "hospital", "founder"), ("In which city is the hospital {descriptor} located?", "hospital", "city"), ("What is the bed capacity of the hospital {descriptor}?", "hospital", "bed capacity"), ("On what month, day, and year was the hospital {descriptor} founded?", "hospital", "inception date"), ("What type of hospital is {descriptor}?", "hospital", "hospital type")),
        _spec("medicines", ("medicine", "medication", "drug"), ("Who discovered the medicine {descriptor}?", "medicine", "discoverer"), ("In which country was the medicine {descriptor} developed?", "medicine", "country of origin"), ("What dosage strength does the medicine {descriptor} have in milligrams?", "medicine", "dose"), ("On what month, day, and year was the medicine {descriptor} approved?", "medicine", "approval date"), ("What active ingredient is in the medicine {descriptor}?", "medicine", "active ingredient")),
        _spec("vaccines", ("vaccine",), ("Who developed the vaccine {descriptor}?", "vaccine", "developer"), ("In which country was the vaccine {descriptor} developed?", "vaccine", "country of origin"), ("What dose volume does the vaccine {descriptor} use in milliliters?", "vaccine", "dose volume"), ("On what month, day, and year was the vaccine {descriptor} approved?", "vaccine", "approval date"), ("What disease does the vaccine {descriptor} target?", "vaccine", "medical condition treated")),
        _spec("medical devices", ("medical device", "device"), ("Who invented the medical device {descriptor}?", "medical device", "inventor"), ("In which country was the medical device {descriptor} manufactured?", "medical device", "country of manufacture"), ("What is the weight of the medical device {descriptor} in grams?", "medical device", "mass"), ("On what month, day, and year was the medical device {descriptor} approved?", "medical device", "approval date"), ("What material is used in the medical device {descriptor}?", "medical device", "material")),
        _spec("guidelines and schools", ("guideline", "medical school"), ("Who wrote the clinical guideline {descriptor}?", "clinical guideline", "author"), ("In which country is the medical school {descriptor} located?", "medical school", "country"), ("What is the page count of the clinical guideline {descriptor}?", "clinical guideline", "number of pages"), ("On what month, day, and year was the guideline {descriptor} published?", "clinical guideline", "publication date"), ("What publisher released the guideline {descriptor}?", "clinical guideline", "publisher")),
    ],
    "People": [
        _spec("birth and death facts", ("birth", "death", "biography"), ("Who was the father of {descriptor}?", "human", "father"), ("Where was {descriptor} born?", "human", "place of birth"), ("What was the age of {descriptor} at death?", "human", "age at death"), ("On what month, day, and year was {descriptor} born?", "human", "date of birth"), ("What occupation is {descriptor} known for?", "human", "occupation")),
        _spec("education", ("university", "degree", "education"), ("Who supervised {descriptor}'s doctoral work?", "human", "doctoral advisor"), ("At which university did {descriptor} study?", "human", "educated at"), ("What was the duration of {descriptor}'s degree program in years?", "academic degree", "duration"), ("On what month, day, and year did {descriptor} receive the degree?", "human", "degree date"), ("What academic degree did {descriptor} receive?", "human", "academic degree")),
        _spec("creative careers", ("artist", "author", "composer", "creator"), ("Who influenced {descriptor}?", "human", "influenced by"), ("Where did {descriptor} work?", "human", "work location"), ("How long is the recorded work by {descriptor} in minutes?", "creative work", "duration"), ("On what month, day, and year was {descriptor}'s first work published?", "human", "first work date"), ("What notable work is associated with {descriptor}?", "human", "notable work")),
        _spec("scientific careers", ("scientist", "inventor", "researcher"), ("Who was the doctoral advisor of {descriptor}?", "human", "doctoral advisor"), ("At which institution did {descriptor} work?", "human", "employer"), ("What is the citation count of {descriptor}'s named paper?", "scholarly article", "citation count"), ("On what month, day, and year did {descriptor} receive the award?", "human", "award received date"), ("What field of work is associated with {descriptor}?", "human", "field of work")),
        _spec("public offices", ("office", "minister", "judge"), ("Who appointed {descriptor} to office?", "human", "appointed by"), ("In which country did {descriptor} hold office?", "human", "country of citizenship"), ("What was the term length of {descriptor}'s office in years?", "public office", "term length"), ("On what month, day, and year did {descriptor} take office?", "human", "start time"), ("What position did {descriptor} hold?", "human", "position held")),
    ],
    "Philosophy and Religion": [
        _spec("religious buildings", ("church", "temple", "monastery"), ("Who designed the temple {descriptor}?", "temple", "architect"), ("In which country is the monastery {descriptor} located?", "monastery", "country"), ("What is the height of the church {descriptor} in meters?", "church", "height"), ("On what month, day, and year was the temple {descriptor} completed?", "temple", "completion date"), ("What architectural style is the church {descriptor} known for?", "church", "architectural style")),
        _spec("religious texts", ("religious text", "scripture", "encyclical"), ("Who translated the religious text {descriptor}?", "religious text", "translator"), ("Where was the religious text {descriptor} composed?", "religious text", "place of composition"), ("What is the page count of the religious text {descriptor}?", "religious text", "number of pages"), ("On what month, day, and year was the encyclical {descriptor} published?", "encyclical", "publication date"), ("What language was the religious text {descriptor} originally written in?", "religious text", "original language of work")),
        _spec("philosophy books", ("philosophy book", "treatise"), ("Who translated the philosophy book {descriptor}?", "philosophy book", "translator"), ("In which country was the philosophy book {descriptor} published?", "philosophy book", "country of publication"), ("What is the page count of the philosophy book {descriptor}?", "philosophy book", "number of pages"), ("On what month, day, and year was the philosophy book {descriptor} published?", "philosophy book", "publication date"), ("What school of philosophy is associated with {descriptor}?", "philosophy book", "philosophical school")),
        _spec("religious offices", ("religious office", "leader"), ("Who founded the religious office {descriptor}?", "religious office", "founder"), ("In which country is the religious office {descriptor} based?", "religious office", "country"), ("What was the term length for the office {descriptor} in years?", "religious office", "term length"), ("On what month, day, and year was the office {descriptor} established?", "religious office", "inception date"), ("What religion is associated with the office {descriptor}?", "religious office", "religion")),
        _spec("belief systems", ("religion", "philosophy", "movement"), ("Who founded the movement {descriptor}?", "movement", "founder"), ("In which country did the movement {descriptor} originate?", "movement", "country of origin"), ("What was the membership size recorded for {descriptor}?", "religious movement", "membership"), ("On what month, day, and year was the movement {descriptor} founded?", "movement", "inception date"), ("What tradition is the movement {descriptor} part of?", "movement", "religious tradition")),
    ],
    "Physical Sciences": [
        _spec("physics papers", ("physics", "article", "paper"), ("Who wrote the physics article {descriptor}?", "physics article", "author"), ("In which journal was the physics article {descriptor} published?", "physics article", "published in"), ("What is the page count of the physics article {descriptor}?", "physics article", "number of pages"), ("On what month, day, and year was the physics article {descriptor} published?", "physics article", "publication date"), ("What main subject does the physics article {descriptor} cover?", "physics article", "main subject")),
        _spec("chemistry", ("chemistry", "chemical", "compound"), ("Who discovered the chemical compound {descriptor}?", "chemical compound", "discoverer"), ("Where was the compound {descriptor} discovered?", "chemical compound", "discovery place"), ("What is the molar mass of {descriptor} in grams per mole?", "chemical compound", "molar mass"), ("On what month, day, and year was the compound {descriptor} discovered?", "chemical compound", "discovery date"), ("What chemical formula identifies {descriptor}?", "chemical compound", "chemical formula")),
        _spec("scientific instruments", ("instrument", "telescope"), ("Who designed the instrument {descriptor}?", "scientific instrument", "designer"), ("Where is the instrument {descriptor} located?", "scientific instrument", "location"), ("What is the aperture of the telescope {descriptor} in meters?", "telescope", "aperture"), ("On what month, day, and year did the instrument {descriptor} begin operation?", "scientific instrument", "start time"), ("What wavelength range does the telescope {descriptor} observe?", "telescope", "spectral range")),
        _spec("spacecraft", ("spacecraft",), ("Who designed the spacecraft {descriptor}?", "spacecraft", "designer"), ("From which launch site was the spacecraft {descriptor} launched?", "spacecraft", "launch site"), ("What is the mass of the spacecraft {descriptor} in kilograms?", "spacecraft", "mass"), ("On what month, day, and year was the spacecraft {descriptor} launched?", "spacecraft", "launch date"), ("What launch vehicle carried the spacecraft {descriptor}?", "spacecraft", "launch vehicle")),
        _spec("science datasets", ("science dataset", "dataset"), ("Who created the science dataset {descriptor}?", "science dataset", "creator"), ("In which country was the science dataset {descriptor} created?", "science dataset", "country of origin"), ("What is the size of the science dataset {descriptor} in gigabytes?", "science dataset", "dataset size"), ("On what month, day, and year was the science dataset {descriptor} published?", "science dataset", "publication date"), ("What file format does the science dataset {descriptor} use?", "science dataset", "file format")),
    ],
    "Politics and Law": [
        _spec("laws", ("law", "act", "bill"), ("Who sponsored the law {descriptor}?", "law", "sponsor"), ("In which jurisdiction does the law {descriptor} apply?", "law", "applies to jurisdiction"), ("What section number identifies the law {descriptor}?", "law", "section number"), ("On what month, day, and year was the law {descriptor} enacted?", "law", "enactment date"), ("What legislature enacted the law {descriptor}?", "law", "legislated by")),
        _spec("court cases", ("court", "case", "legal"), ("Who wrote the opinion in the case {descriptor}?", "legal case", "opinion author"), ("Which court decided the case {descriptor}?", "legal case", "court"), ("What docket number identifies the case {descriptor}?", "legal case", "docket number"), ("On what month, day, and year was the case {descriptor} decided?", "legal case", "decision date"), ("What area of law does the case {descriptor} concern?", "legal case", "legal field")),
        _spec("constitutions", ("constitution",), ("Who drafted the constitution {descriptor}?", "constitution", "drafter"), ("To which jurisdiction does the constitution {descriptor} apply?", "constitution", "applies to jurisdiction"), ("What article number contains the clause in {descriptor}?", "constitution", "article number"), ("On what month, day, and year was the constitution {descriptor} adopted?", "constitution", "adoption date"), ("What language was the constitution {descriptor} written in?", "constitution", "language of work")),
        _spec("government agencies", ("agency", "department", "policy"), ("Who founded the agency {descriptor}?", "government agency", "founder"), ("Which jurisdiction does the agency {descriptor} serve?", "government agency", "jurisdiction"), ("What is the budget of the agency {descriptor}?", "government agency", "budget"), ("On what month, day, and year was the agency {descriptor} established?", "government agency", "inception date"), ("What parent department contains the agency {descriptor}?", "government agency", "parent organization")),
        _spec("political parties", ("political party", "party"), ("Who founded the political party {descriptor}?", "political party", "founder"), ("In which country was the political party {descriptor} founded?", "political party", "country"), ("What was the founding membership of the party {descriptor}?", "political party", "founding membership"), ("On what month, day, and year was the political party {descriptor} founded?", "political party", "inception date"), ("What ideology is associated with the political party {descriptor}?", "political party", "political ideology")),
    ],
    "Society and Culture": [
        _spec("museums", ("museum", "gallery"), ("Who founded the museum {descriptor}?", "museum", "founder"), ("In which city is the museum {descriptor} located?", "museum", "city"), ("What is the floor area of the museum {descriptor} in square meters?", "museum", "floor area"), ("On what month, day, and year did the museum {descriptor} open?", "museum", "opening date"), ("What collection type is the museum {descriptor} known for?", "museum", "collection type")),
        _spec("festivals", ("festival", "event"), ("Who founded the festival {descriptor}?", "festival", "founder"), ("In which city was the festival {descriptor} first held?", "festival", "first location"), ("What was the duration of the festival {descriptor} in days?", "festival", "duration"), ("On what month, day, and year did the festival {descriptor} first take place?", "festival", "inception date"), ("What cultural tradition is associated with the festival {descriptor}?", "festival", "tradition")),
        _spec("awards", ("award", "prize"), ("Who established the award {descriptor}?", "award", "founder"), ("In which country is the award {descriptor} presented?", "award", "country"), ("What is the monetary value of the award {descriptor}?", "award", "award amount"), ("On what month, day, and year was the award {descriptor} established?", "award", "inception date"), ("What organization confers the award {descriptor}?", "award", "conferred by")),
        _spec("libraries and archives", ("library", "archive"), ("Who founded the library {descriptor}?", "library", "founder"), ("In which country is the archive {descriptor} located?", "archive", "country"), ("What is the collection size of the library {descriptor}?", "library", "collection size"), ("On what month, day, and year was the archive {descriptor} founded?", "archive", "inception date"), ("What type of archive is {descriptor}?", "archive", "archive type")),
        _spec("heritage sites", ("heritage", "site", "monument"), ("Who designed the heritage site {descriptor}?", "heritage site", "designer"), ("In which country is the heritage site {descriptor} located?", "heritage site", "country"), ("What is the area of the heritage site {descriptor} in hectares?", "heritage site", "area"), ("On what month, day, and year was the heritage site {descriptor} inscribed?", "heritage site", "inscription date"), ("What heritage designation applies to {descriptor}?", "heritage site", "heritage designation")),
    ],
    "Sports and Recreation": [
        _spec("teams and clubs", ("team", "club"), ("Who founded the club {descriptor}?", "sports club", "founder"), ("In which city is the team {descriptor} based?", "sports team", "city"), ("What is the seating capacity of the team's home venue {descriptor}?", "sports venue", "capacity"), ("On what month, day, and year was the club {descriptor} founded?", "sports club", "inception date"), ("What league is the team {descriptor} associated with?", "sports team", "league")),
        _spec("stadiums", ("stadium", "venue"), ("Who designed the stadium {descriptor}?", "stadium", "architect"), ("In which city is the stadium {descriptor} located?", "stadium", "city"), ("What is the seating capacity of the stadium {descriptor}?", "stadium", "capacity"), ("On what month, day, and year did the stadium {descriptor} open?", "stadium", "opening date"), ("What surface does the stadium {descriptor} use?", "stadium", "surface")),
        _spec("tournaments", ("tournament", "competition"), ("Who founded the tournament {descriptor}?", "sports tournament", "founder"), ("In which country was the tournament {descriptor} held?", "sports tournament", "country"), ("What was the prize money of the tournament {descriptor}?", "sports tournament", "prize money"), ("On what month, day, and year did the tournament {descriptor} begin?", "sports tournament", "start date"), ("What sport is played in the tournament {descriptor}?", "sports tournament", "sport")),
        _spec("races", ("race", "grand prix", "marathon"), ("Who designed the race course {descriptor}?", "race course", "designer"), ("In which city was the race {descriptor} held?", "race", "city"), ("What is the distance of the race {descriptor} in kilometers?", "race", "distance"), ("On what month, day, and year did the race {descriptor} take place?", "race", "point in time"), ("What sport is associated with the race {descriptor}?", "race", "sport")),
        _spec("games and recreation", ("game", "recreation", "board game"), ("Who designed the game {descriptor}?", "game", "designer"), ("In which country did the game {descriptor} originate?", "game", "country of origin"), ("What is the playing time of the game {descriptor} in minutes?", "game", "playing time"), ("On what month, day, and year was the game {descriptor} published?", "game", "publication date"), ("What genre is the game {descriptor}?", "game", "genre")),
    ],
}


def get_single_hop_subdomain_plan() -> dict[str, list[str]]:
    """Return the proposed domain-to-subdomain diversification plan."""
    return {
        domain: [spec["name"] for spec in specs]
        for domain, specs in SINGLE_HOP_SUBDOMAIN_SPECS.items()
    }


def get_single_hop_template_catalog() -> list[SingleHopCatalogTemplate]:
    """Return the 400-row expanded statusless single-hop catalog."""
    extracted = _extract_existing_single_hop_templates()
    templates = extracted + _select_generated_templates(extracted)
    _validate_catalog_shape(templates)
    return templates


def single_hop_catalog_as_dicts() -> list[dict[str, str]]:
    """Return the expanded catalog as plain dictionaries."""
    return [template.to_dict() for template in get_single_hop_template_catalog()]


def single_hop_catalog_summary() -> dict[str, Any]:
    """Return summary counts for the expanded catalog."""
    rows = get_single_hop_template_catalog()
    return {
        "total_templates": len(rows),
        "domain_counts": dict(sorted(Counter(row.domain for row in rows).items())),
        "answer_type_counts": dict(sorted(Counter(row.answer_type for row in rows).items())),
        "origin_counts": dict(sorted(Counter(row.origin for row in rows).items())),
        "subdomains": get_single_hop_subdomain_plan(),
    }


def _extract_existing_single_hop_templates() -> list[SingleHopCatalogTemplate]:
    """Extract current single-fact, non-ordinal, non-count templates without status."""
    rows: list[SingleHopCatalogTemplate] = []
    subdomain_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for template in get_all_templates():
        question = template.canonical_question_template
        if template.template_domain not in SINGLE_HOP_EXPANSION_DOMAINS:
            continue
        if template.reasoning_style != "single_fact" or template.composition_style != "single_fact":
            continue
        if _is_ordinal_or_count_template(template.template_key, question):
            continue
        answer_type = LEGACY_ANSWER_TYPE_MAP.get(template.answer_type, "Other")
        subdomain = _select_existing_subdomain(template.template_domain, template.template_key, question, subdomain_counts)
        rows.append(
            SingleHopCatalogTemplate(
                template_key=f"existing_{template.template_key}",
                domain=template.template_domain,
                subdomain=subdomain,
                answer_type=answer_type,
                subject_type_qid=template.subject_type_qid,
                date_property_pid=template.date_property_pid,
                target_property_pid=template.target_property_pid,
                canonical_question_template=question,
                subject_type_label=template.subject_type_label,
                target_property_label=template.target_property_label,
                candidate_search_query=_candidate_search_query(
                    subject_type_qid=template.subject_type_qid,
                    date_property_pid=template.date_property_pid,
                    target_property_pid=template.target_property_pid,
                    answer_format=template.answer_format,
                ),
                answer_format=template.answer_format if answer_type != "Number" else "number",
                temporal_mode=template.temporal_mode,
                origin="existing_single_hop_non_ordinal_non_count",
                time_invariance_note=(
                    "Extracted from the current catalog without copying status; "
                    "route validators must still reject mutable live-status facts."
                ),
                legacy_template_key=template.template_key,
                legacy_answer_type=template.answer_type,
                source_template_key=template.template_key,
            )
        )
        subdomain_counts[template.template_domain][subdomain] += 1
    return rows


def _select_existing_subdomain(
    domain: str,
    template_key: str,
    question: str,
    subdomain_counts: dict[str, Counter[str]],
) -> str:
    """Assign an extracted legacy template to a diversification subdomain."""
    specs = SINGLE_HOP_SUBDOMAIN_SPECS[domain]
    haystack = f"{template_key} {question}".casefold()
    matching_specs = [
        spec for spec in specs if any(keyword.casefold() in haystack for keyword in spec["keywords"])
    ]
    candidates = matching_specs or specs
    return min(
        candidates,
        key=lambda spec: (subdomain_counts[domain][spec["name"]], spec["name"]),
    )["name"]


def _select_generated_templates(
    extracted: list[SingleHopCatalogTemplate],
) -> list[SingleHopCatalogTemplate]:
    """Select generated rows to hit 400 templates and balanced answer types."""
    selected = list(extracted)
    selected_keys = {row.template_key for row in selected}
    generated_by_domain_subdomain_type = _generated_candidate_index(selected_keys)
    domain_counts = Counter(row.domain for row in selected)
    answer_type_counts = Counter(row.answer_type for row in selected)
    subdomain_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in selected:
        subdomain_counts[row.domain][row.subdomain] += 1

    def add_candidate(domain: str, subdomain: str, answer_type: str) -> bool:
        if domain_counts[domain] >= SINGLE_HOP_TARGET_PER_DOMAIN:
            return False
        if answer_type_counts[answer_type] >= SINGLE_HOP_TARGET_PER_ANSWER_TYPE:
            return False
        if subdomain_counts[domain][subdomain] >= 10:
            return False
        candidate = generated_by_domain_subdomain_type.get((domain, subdomain, answer_type))
        if candidate is None:
            return False
        selected.append(candidate)
        domain_counts[domain] += 1
        answer_type_counts[answer_type] += 1
        subdomain_counts[domain][subdomain] += 1
        generated_by_domain_subdomain_type.pop((domain, subdomain, answer_type), None)
        return True

    # Fill each domain to 20 while preserving the global answer-type target.
    made_progress = True
    while made_progress:
        made_progress = False
        for domain in SINGLE_HOP_EXPANSION_DOMAINS:
            if domain_counts[domain] >= SINGLE_HOP_TARGET_PER_DOMAIN:
                continue
            for answer_type in _rank_answer_types_by_deficit(answer_type_counts):
                subdomains = sorted(
                    get_single_hop_subdomain_plan()[domain],
                    key=lambda name: (subdomain_counts[domain][name], name),
                )
                if any(add_candidate(domain, subdomain, answer_type) for subdomain in subdomains):
                    made_progress = True
                    break

    _repair_domain_and_answer_type_balance(
        selected=selected,
        remaining=generated_by_domain_subdomain_type,
        domain_counts=domain_counts,
        answer_type_counts=answer_type_counts,
        subdomain_counts=subdomain_counts,
    )

    generated = [row for row in selected if row.origin == "generated_single_hop_expansion"]
    return generated


def _repair_domain_and_answer_type_balance(
    *,
    selected: list[SingleHopCatalogTemplate],
    remaining: dict[tuple[str, str, str], SingleHopCatalogTemplate],
    domain_counts: Counter[str],
    answer_type_counts: Counter[str],
    subdomain_counts: dict[str, Counter[str]],
) -> None:
    """Repair rare greedy-fill dead ends with one-for-one type swaps."""
    while len(selected) < SINGLE_HOP_TARGET_TOTAL:
        missing_domains = [
            domain
            for domain in SINGLE_HOP_EXPANSION_DOMAINS
            if domain_counts[domain] < SINGLE_HOP_TARGET_PER_DOMAIN
        ]
        deficit_types = [
            answer_type
            for answer_type in ALLOWED_SINGLE_HOP_ANSWER_TYPES
            if answer_type_counts[answer_type] < SINGLE_HOP_TARGET_PER_ANSWER_TYPE
        ]
        repaired = False
        for missing_domain in missing_domains:
            for key, missing_candidate in list(remaining.items()):
                domain, subdomain, filled_type = key
                if domain != missing_domain or subdomain_counts[domain][subdomain] >= 10:
                    continue
                if answer_type_counts[filled_type] < SINGLE_HOP_TARGET_PER_ANSWER_TYPE:
                    selected.append(missing_candidate)
                    remaining.pop(key)
                    domain_counts[domain] += 1
                    answer_type_counts[filled_type] += 1
                    subdomain_counts[domain][subdomain] += 1
                    repaired = True
                    break
                for deficit_type in deficit_types:
                    donor_index = _find_swap_donor(
                        selected=selected,
                        remaining=remaining,
                        filled_type=filled_type,
                        deficit_type=deficit_type,
                    )
                    if donor_index is None:
                        continue
                    donor = selected.pop(donor_index)
                    donor_key = (donor.domain, donor.subdomain, donor.answer_type)
                    replacement_key = (donor.domain, donor.subdomain, deficit_type)
                    replacement = remaining.pop(replacement_key)
                    remaining[donor_key] = donor
                    selected.append(replacement)
                    answer_type_counts[donor.answer_type] -= 1
                    answer_type_counts[replacement.answer_type] += 1

                    selected.append(missing_candidate)
                    remaining.pop(key)
                    domain_counts[domain] += 1
                    answer_type_counts[filled_type] += 1
                    subdomain_counts[domain][subdomain] += 1
                    repaired = True
                    break
                if repaired:
                    break
            if repaired:
                break
        if not repaired:
            break


def _find_swap_donor(
    *,
    selected: list[SingleHopCatalogTemplate],
    remaining: dict[tuple[str, str, str], SingleHopCatalogTemplate],
    filled_type: str,
    deficit_type: str,
) -> int | None:
    """Find a generated selected row that can be swapped to the deficit type."""
    for index, row in enumerate(selected):
        if row.origin != "generated_single_hop_expansion":
            continue
        if row.answer_type != filled_type:
            continue
        if (row.domain, row.subdomain, deficit_type) in remaining:
            return index
    return None


def _rank_answer_types_by_deficit(answer_type_counts: Counter[str]) -> list[str]:
    """Return answer types ordered by remaining global deficit."""
    return sorted(
        ALLOWED_SINGLE_HOP_ANSWER_TYPES,
        key=lambda answer_type: (
            SINGLE_HOP_TARGET_PER_ANSWER_TYPE - answer_type_counts[answer_type],
            answer_type,
        ),
        reverse=True,
    )


def _generated_candidate_index(
    selected_keys: set[str],
) -> dict[tuple[str, str, str], SingleHopCatalogTemplate]:
    """Return all generated candidates keyed by domain/subdomain/answer type."""
    candidates: dict[tuple[str, str, str], SingleHopCatalogTemplate] = {}
    for domain, specs in SINGLE_HOP_SUBDOMAIN_SPECS.items():
        for spec in specs:
            subdomain = spec["name"]
            for answer_type, variant in spec["variants"].items():
                template_key = f"generated_{_slug(domain)}_{_slug(subdomain)}_{answer_type.casefold()}"
                question = variant["canonical_question_template"]
                if template_key in selected_keys:
                    continue
                date_property_pid = _date_property_pid(
                    variant["subject_type_label"],
                    variant["target_property_pid"],
                    answer_type,
                )
                candidates[(domain, subdomain, answer_type)] = SingleHopCatalogTemplate(
                    template_key=template_key,
                    domain=domain,
                    subdomain=subdomain,
                    answer_type=answer_type,
                    subject_type_qid=variant["subject_type_qid"],
                    date_property_pid=date_property_pid,
                    target_property_pid=variant["target_property_pid"],
                    canonical_question_template=question,
                    subject_type_label=variant["subject_type_label"],
                    target_property_label=variant["target_property_label"],
                    candidate_search_query=_candidate_search_query(
                        subject_type_qid=variant["subject_type_qid"],
                        date_property_pid=date_property_pid,
                        target_property_pid=variant["target_property_pid"],
                        answer_format=variant["answer_format"],
                    ),
                    answer_format=variant["answer_format"],
                    temporal_mode=variant["temporal_mode"],
                    origin="generated_single_hop_expansion",
                    time_invariance_note=(
                        "Template asks for an intrinsic or historically anchored single fact; "
                        "reject if the harvested claim is live, ambiguous, or not uniquely settled."
                    ),
                )
    return candidates


def _is_ordinal_or_count_template(template_key: str, question: str) -> bool:
    """Return whether a template is ordinal, aggregate/count, or comparison-like."""
    normalized = f"{template_key} {question}".casefold()
    if "{ordinal}" in normalized or "ordinal" in normalized:
        return True
    if "how many" in normalized or template_key.endswith("_count") or "_count_" in template_key:
        return True
    return any(word in normalized for word in COMPARISON_WORDS)


def _slug(value: str) -> str:
    """Return a compact ASCII slug for generated template keys."""
    return re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")


def _validate_catalog_shape(rows: list[SingleHopCatalogTemplate]) -> None:
    """Raise a clear error if the generated catalog shape drifts."""
    if len(rows) != SINGLE_HOP_TARGET_TOTAL:
        raise RuntimeError(f"expected 400 single-hop templates, got {len(rows)}")
    domains = Counter(row.domain for row in rows)
    answer_types = Counter(row.answer_type for row in rows)
    for domain in SINGLE_HOP_EXPANSION_DOMAINS:
        if domains[domain] != SINGLE_HOP_TARGET_PER_DOMAIN:
            raise RuntimeError(f"expected 20 templates for {domain}, got {domains[domain]}")
    for answer_type in ALLOWED_SINGLE_HOP_ANSWER_TYPES:
        if answer_types[answer_type] != SINGLE_HOP_TARGET_PER_ANSWER_TYPE:
            raise RuntimeError(
                f"expected 80 {answer_type} templates, got {answer_types[answer_type]}"
            )
    keys = [row.template_key for row in rows]
    if len(keys) != len(set(keys)):
        raise RuntimeError("single-hop expanded template catalog has duplicate template keys")


