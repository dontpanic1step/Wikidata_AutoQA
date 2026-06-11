"""Deterministic geographic answer-leakage helpers."""

from __future__ import annotations

import re
from typing import Iterable, NamedTuple

from .entity_normalization import normalize_name
from .text_normalization import text_contains_any


class CountryLeakageGroup(NamedTuple):
    """Country terms with adjectival/demonym and major-city leakage cues."""

    country_terms: frozenset[str]
    demonym_terms: frozenset[str]
    city_terms: frozenset[str]


QUESTION_AMBIGUOUS_COUNTRY_TERMS = frozenset({"us"})
BARE_US_COUNTRY_PATTERN = re.compile(r"\bUS\b")


def _normalize_terms(terms: Iterable[str]) -> frozenset[str]:
    """Return normalized non-empty static terms."""
    normalized_terms = {normalize_name(term) for term in terms}
    return frozenset(term for term in normalized_terms if term)


def _group(
    country_terms: tuple[str, ...],
    demonym_terms: tuple[str, ...],
    city_terms: tuple[str, ...],
) -> CountryLeakageGroup:
    """Build one normalized geographic leakage group."""
    return CountryLeakageGroup(
        country_terms=_normalize_terms(country_terms),
        demonym_terms=_normalize_terms(demonym_terms),
        city_terms=_normalize_terms(city_terms),
    )


COUNTRY_LEAKAGE_GROUPS = (
    _group(
        ("united states", "united states of america", "usa", "us", "u s", "u s a", "america"),
        ("american",),
        (
            "new york",
            "new york city",
            "nyc",
            "los angeles",
            "chicago",
            "houston",
            "phoenix",
            "philadelphia",
            "san antonio",
            "san diego",
            "dallas",
            "san jose",
            "san francisco",
            "washington dc",
            "boston",
            "miami",
            "atlanta",
            "seattle",
        ),
    ),
    _group(
        ("china", "people s republic of china", "prc", "p r c"),
        ("chinese",),
        (
            "beijing",
            "shanghai",
            "guangzhou",
            "shenzhen",
            "chengdu",
            "wuhan",
            "chongqing",
            "tianjin",
            "nanjing",
            "hangzhou",
            "xi an",
            "hong kong",
        ),
    ),
    _group(
        ("norway",),
        ("norwegian", "norwagion"),
        ("oslo", "bergen", "trondheim", "stavanger"),
    ),
    _group(
        ("united kingdom", "uk", "u k", "great britain", "britain"),
        ("british", "briton"),
        ("london", "birmingham", "manchester", "glasgow", "liverpool", "edinburgh", "leeds"),
    ),
    _group(
        ("england",),
        ("english",),
        ("london", "birmingham", "manchester", "liverpool", "leeds"),
    ),
    _group(
        ("scotland",),
        ("scottish", "scot"),
        ("glasgow", "edinburgh", "aberdeen", "dundee"),
    ),
    _group(
        ("wales",),
        ("welsh",),
        ("cardiff", "swansea", "newport", "wrexham"),
    ),
    _group(
        ("ireland", "republic of ireland"),
        ("irish",),
        ("dublin", "cork", "galway", "limerick"),
    ),
    _group(
        ("france",),
        ("french",),
        ("paris", "marseille", "lyon", "toulouse", "nice", "nantes", "bordeaux", "lille"),
    ),
    _group(
        ("germany",),
        ("german",),
        ("berlin", "hamburg", "munich", "muenchen", "cologne", "frankfurt", "stuttgart", "dusseldorf"),
    ),
    _group(
        ("italy",),
        ("italian",),
        ("rome", "milan", "naples", "turin", "palermo", "florence", "venice", "bologna"),
    ),
    _group(
        ("spain",),
        ("spanish",),
        ("madrid", "barcelona", "valencia", "seville", "zaragoza", "malaga", "bilbao"),
    ),
    _group(
        ("portugal",),
        ("portuguese",),
        ("lisbon", "porto", "braga", "coimbra"),
    ),
    _group(
        ("netherlands", "holland"),
        ("dutch",),
        ("amsterdam", "rotterdam", "the hague", "utrecht", "eindhoven"),
    ),
    _group(
        ("belgium",),
        ("belgian",),
        ("brussels", "antwerp", "ghent", "bruges", "liege"),
    ),
    _group(
        ("switzerland",),
        ("swiss",),
        ("zurich", "geneva", "basel", "bern", "lausanne"),
    ),
    _group(
        ("austria",),
        ("austrian",),
        ("vienna", "graz", "linz", "salzburg", "innsbruck"),
    ),
    _group(
        ("sweden",),
        ("swedish",),
        ("stockholm", "gothenburg", "goteborg", "malmo", "uppsala"),
    ),
    _group(
        ("denmark",),
        ("danish", "dane"),
        ("copenhagen", "aarhus", "odense", "aalborg"),
    ),
    _group(
        ("finland",),
        ("finnish", "finn"),
        ("helsinki", "espoo", "tampere", "turku"),
    ),
    _group(
        ("iceland",),
        ("icelandic",),
        ("reykjavik",),
    ),
    _group(
        ("poland",),
        ("polish", "pole"),
        ("warsaw", "krakow", "lodz", "wroclaw", "poznan", "gdansk"),
    ),
    _group(
        ("czechia", "czech republic"),
        ("czech",),
        ("prague", "brno", "ostrava"),
    ),
    _group(
        ("greece",),
        ("greek",),
        ("athens", "thessaloniki", "patras", "heraklion"),
    ),
    _group(
        ("turkey", "turkiye"),
        ("turkish",),
        ("istanbul", "ankara", "izmir", "bursa", "antalya"),
    ),
    _group(
        ("russia", "russian federation"),
        ("russian",),
        ("moscow", "saint petersburg", "st petersburg", "novosibirsk", "yekaterinburg", "kazan"),
    ),
    _group(
        ("ukraine",),
        ("ukrainian",),
        ("kyiv", "kiev", "kharkiv", "odesa", "odessa", "dnipro", "lviv"),
    ),
    _group(
        ("japan",),
        ("japanese",),
        ("tokyo", "osaka", "kyoto", "yokohama", "nagoya", "sapporo", "fukuoka", "kobe"),
    ),
    _group(
        ("south korea", "republic of korea"),
        ("korean", "south korean"),
        ("seoul", "busan", "incheon", "daegu", "daejeon", "gwangju"),
    ),
    _group(
        ("north korea", "democratic people s republic of korea", "dprk", "d p r k"),
        ("korean", "north korean"),
        ("pyongyang", "hamhung", "chongjin"),
    ),
    _group(
        ("india",),
        ("indian",),
        (
            "mumbai",
            "bombay",
            "delhi",
            "new delhi",
            "bangalore",
            "bengaluru",
            "kolkata",
            "calcutta",
            "chennai",
            "hyderabad",
            "pune",
            "ahmedabad",
        ),
    ),
    _group(
        ("pakistan",),
        ("pakistani",),
        ("karachi", "lahore", "islamabad", "faisalabad", "rawalpindi"),
    ),
    _group(
        ("bangladesh",),
        ("bangladeshi",),
        ("dhaka", "chittagong", "khulna", "rajshahi"),
    ),
    _group(
        ("indonesia",),
        ("indonesian",),
        ("jakarta", "surabaya", "bandung", "medan", "semarang"),
    ),
    _group(
        ("malaysia",),
        ("malaysian",),
        ("kuala lumpur", "george town", "johor bahru", "ipoh"),
    ),
    _group(
        ("singapore",),
        ("singaporean",),
        ("singapore",),
    ),
    _group(
        ("thailand",),
        ("thai",),
        ("bangkok", "chiang mai", "phuket", "pattaya"),
    ),
    _group(
        ("vietnam",),
        ("vietnamese",),
        ("hanoi", "ho chi minh city", "saigon", "da nang", "haiphong"),
    ),
    _group(
        ("philippines",),
        ("philippine", "filipino"),
        ("manila", "quezon city", "davao city", "cebu city", "caloocan"),
    ),
    _group(
        ("iran",),
        ("iranian",),
        ("tehran", "mashhad", "isfahan", "shiraz", "tabriz"),
    ),
    _group(
        ("iraq",),
        ("iraqi",),
        ("baghdad", "basra", "mosul", "erbil", "najaf"),
    ),
    _group(
        ("saudi arabia",),
        ("saudi", "saudi arabian"),
        ("riyadh", "jeddah", "mecca", "medina", "dammam"),
    ),
    _group(
        ("united arab emirates", "uae", "u a e"),
        ("emirati",),
        ("dubai", "abu dhabi", "sharjah", "al ain"),
    ),
    _group(
        ("israel",),
        ("israeli",),
        ("jerusalem", "tel aviv", "haifa", "beersheba"),
    ),
    _group(
        ("egypt",),
        ("egyptian",),
        ("cairo", "alexandria", "giza", "luxor", "aswan"),
    ),
    _group(
        ("morocco",),
        ("moroccan",),
        ("casablanca", "rabat", "marrakesh", "marrakech", "fes", "tangier"),
    ),
    _group(
        ("south africa",),
        ("south african",),
        ("johannesburg", "cape town", "durban", "pretoria", "soweto"),
    ),
    _group(
        ("nigeria",),
        ("nigerian",),
        ("lagos", "abuja", "kano", "ibadan", "port harcourt"),
    ),
    _group(
        ("kenya",),
        ("kenyan",),
        ("nairobi", "mombasa", "kisumu", "nakuru"),
    ),
    _group(
        ("ethiopia",),
        ("ethiopian",),
        ("addis ababa", "dire dawa", "mekelle", "gondar"),
    ),
    _group(
        ("canada",),
        ("canadian",),
        ("toronto", "montreal", "vancouver", "ottawa", "calgary", "edmonton", "quebec city"),
    ),
    _group(
        ("mexico",),
        ("mexican",),
        ("mexico city", "guadalajara", "monterrey", "puebla", "tijuana"),
    ),
    _group(
        ("brazil",),
        ("brazilian",),
        ("sao paulo", "rio de janeiro", "brasilia", "salvador", "fortaleza", "belo horizonte"),
    ),
    _group(
        ("argentina",),
        ("argentine", "argentinian"),
        ("buenos aires", "cordoba", "rosario", "mendoza", "la plata"),
    ),
    _group(
        ("chile",),
        ("chilean",),
        ("santiago", "valparaiso", "concepcion", "antofagasta"),
    ),
    _group(
        ("colombia",),
        ("colombian",),
        ("bogota", "medellin", "cali", "barranquilla", "cartagena"),
    ),
    _group(
        ("peru",),
        ("peruvian",),
        ("lima", "arequipa", "cusco", "trujillo"),
    ),
    _group(
        ("venezuela",),
        ("venezuelan",),
        ("caracas", "maracaibo", "valencia", "barquisimeto"),
    ),
    _group(
        ("australia",),
        ("australian",),
        ("sydney", "melbourne", "brisbane", "perth", "adelaide", "canberra", "gold coast"),
    ),
    _group(
        ("new zealand",),
        ("new zealand", "new zealander"),
        ("auckland", "wellington", "christchurch", "hamilton", "dunedin"),
    ),
)


def question_leaks_geographic_answer_context(question: str, answer_labels: Iterable[str]) -> bool:
    """Return whether country adjectives/demonyms or major cities leak a geographic answer."""
    if not question.strip():
        return False
    answer_terms = _answer_terms(answer_labels)
    if not answer_terms:
        return False
    for group in COUNTRY_LEAKAGE_GROUPS:
        answer_is_country = bool(answer_terms.intersection(group.country_terms))
        answer_is_demonym = bool(answer_terms.intersection(group.demonym_terms))
        answer_is_city = bool(answer_terms.intersection(group.city_terms))
        question_country_terms = _question_country_terms(group, question)
        if answer_is_country and (
            _contains_any_phrase(question, group.demonym_terms)
            or _contains_any_phrase(question, group.city_terms)
        ):
            return True
        if answer_is_demonym and _contains_any_phrase(question, question_country_terms):
            return True
        if answer_is_city and _contains_any_phrase(question, question_country_terms):
            return True
    return False


def _answer_terms(answer_labels: Iterable[str]) -> set[str]:
    """Return exact normalized answer terms plus article-stripped variants."""
    terms: set[str] = set()
    for label in answer_labels:
        normalized = normalize_name(str(label))
        if not normalized:
            continue
        terms.add(normalized)
        if normalized.startswith("the "):
            terms.add(normalized.removeprefix("the "))
    return terms


def _question_country_terms(group: CountryLeakageGroup, question: str) -> frozenset[str]:
    """Return country terms that are safe to match inside the question text."""
    terms = group.country_terms - QUESTION_AMBIGUOUS_COUNTRY_TERMS
    if "us" in group.country_terms and BARE_US_COUNTRY_PATTERN.search(question):
        return terms | frozenset({"us"})
    return terms


def _contains_any_phrase(text: str, phrases: Iterable[str]) -> bool:
    """Return whether text contains any phrase as a token-bounded phrase."""
    return text_contains_any(text, phrases)
