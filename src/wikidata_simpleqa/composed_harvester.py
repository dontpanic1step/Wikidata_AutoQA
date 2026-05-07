"""Backward-compatible compositional multi-hop executor entry points."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
import re
from typing import Any, Callable

from .config import Settings
from .models import CandidateFact, DomainTemplate
from .reasoning import (
    build_bridge_entity,
    build_reasoning_hop,
    normalize_reasoning_style,
)
from .wikidata_client import WikidataClient

JoinExecutor = Callable[[WikidataClient, Settings, DomainTemplate], list[CandidateFact]]


def harvest_composed_candidates(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
) -> list[CandidateFact]:
    """Harvest candidates for supported compositional multi-hop templates."""
    reasoning_style = normalize_reasoning_style(template.reasoning_style)
    executor = REASONING_EXECUTORS.get(reasoning_style)
    if executor is None:
        return []
    return executor(client, settings, replace(template, reasoning_style=reasoning_style))


def build_wedding_age_gap_candidate_from_person_qid(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
    person_qid: str,
) -> CandidateFact | None:
    """Build a wedding age-gap candidate from one person's spouse claims."""
    entities = client.get_entities([person_qid])
    person = entities.get(person_qid, {})
    person_label = _label(person)
    person_birth = _claim_time(person, "P569")
    if not person_label or person_birth is None:
        return None

    spouse_claims = person.get("claims", {}).get("P26", [])
    for claim in spouse_claims:
        spouse_qid = claim.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id")
        qualifiers = claim.get("qualifiers", {})
        start = _qualifier_time(qualifiers, "P580")
        if not spouse_qid or start is None or start < settings.target_start_date:
            continue
        if start > settings.date_upper_bound:
            continue
        if _qualifier_precision(qualifiers, "P580") != 11:
            continue
        spouse_entity = client.get_entities([spouse_qid]).get(spouse_qid, {})
        spouse_label = _label(spouse_entity)
        spouse_birth = _claim_time(spouse_entity, "P569")
        if not spouse_label or spouse_birth is None:
            continue
        age_gap = _age_gap_years(person_birth, spouse_birth, start)
        if age_gap is None:
            continue
        return CandidateFact(
            subject_qid=person_qid,
            subject_label=person_label,
            subject_aliases=[],
            domain=template.domain,
            topic=template.topic,
            answer_type=template.answer_type,
            question_family=template.question_family,
            subject_type_qids=[template.subject_type_qid],
            target_property_pid="COMPOSED_AGE_GAP",
            target_property_label="age gap at wedding",
            answer_qids=[f"VALUE:number:{age_gap}"],
            answer_labels=[str(age_gap)],
            answer_aliases=[],
            date_property_pid="P580",
            date_value=start,
            target_time=settings.target_time,
            canonical_question="",
            newness_metadata={
                "anchor_kind": "statement_qualifier",
                "anchor_property_pid": "P580",
                "anchor_value": start,
                "reason": "marriage_start_time_not_earlier_than_target_time",
                "what_is_new": "the marriage event",
            },
            reasoning_style="multi_hop_aggregate",
            hop_count=2,
            reasoning_path=[
                build_reasoning_hop(
                    source_qid=person_qid,
                    source_label=person_label,
                    property_pid="P26",
                    property_label="spouse",
                    target_qid=spouse_qid,
                    target_label=spouse_label,
                    role="bridge",
                ),
                build_reasoning_hop(
                    source_qid=spouse_qid,
                    source_label=spouse_label,
                    property_pid="DERIVED_AGE_GAP_AT_EVENT",
                    property_label="age gap at wedding",
                    target_qid=f"VALUE:number:{age_gap}",
                    target_label=str(age_gap),
                    role="answer",
                ),
            ],
            bridge_entities=[build_bridge_entity(qid=spouse_qid, label=spouse_label, role="spouse")],
            derivation_signature={
                "style": "multi_hop_aggregate",
                "rule": "age_gap_at_marriage_start",
            },
            provenance_complete=True,
            source_metadata={
                "wikidata_access_date": settings.run_date,
                "retrieval_method": "wbgetentities composed claims",
                "question_format_args": {
                    "descriptor": f"{person_label} and {spouse_label} at their wedding"
                },
                "composed_from": {
                    "person_qid": person_qid,
                    "spouse_qid": spouse_qid,
                    "birth_dates": [person_birth, spouse_birth],
                    "marriage_start": start,
                },
                "multi_hop_unique": True,
            },
        )
    return None


def build_first_degree_candidate_from_person_entity(
    settings: Settings,
    template: DomainTemplate,
    person_qid: str,
    person: dict[str, Any],
    related_entities: dict[str, dict[str, Any]],
) -> CandidateFact | None:
    """Build a first-degree-university candidate from a person's claims."""
    person_label = _label(person)
    if not person_label:
        return None

    education_claims = person.get("claims", {}).get("P69", [])
    university_records: list[tuple[str, str, str, str]] = []
    referenced_qids: set[str] = set()
    for claim in education_claims:
        university_qid = claim.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id")
        if not university_qid:
            continue
        qualifiers = claim.get("qualifiers", {})
        end_date = _qualifier_time(qualifiers, "P582")
        if end_date is None:
            continue
        degree_qid = _qualifier_qid(qualifiers, "P512")
        if degree_qid is None:
            continue
        referenced_qids.add(university_qid)
        referenced_qids.add(degree_qid)
        university_records.append((university_qid, degree_qid, end_date, claim.get("rank", "normal")))

    if not university_records:
        return None

    university_like_types = {"Q3918", "Q615150", "Q62078547", "Q2085381", "Q23002039"}
    filtered_records: list[tuple[str, str, str, str]] = []
    for university_qid, degree_qid, end_date, rank in university_records:
        institution = related_entities.get(university_qid, {})
        label = _label(institution)
        type_qids = _claim_qids(institution, "P31")
        if label and university_like_types.intersection(type_qids):
            filtered_records.append((university_qid, degree_qid, end_date, rank))

    if not filtered_records:
        return None

    filtered_records.sort(key=lambda item: (item[2], item[0], item[1]))
    first_end_date = filtered_records[0][2]
    earliest_records = [record for record in filtered_records if record[2] == first_end_date]
    if len(earliest_records) != 1:
        return None

    university_qid, degree_qid, _, _ = earliest_records[0]
    university_label = _label(related_entities.get(university_qid, {}))
    if not university_label:
        return None
    degree_label = _label(related_entities.get(degree_qid, {})) or degree_qid
    if first_end_date < settings.target_start_date or first_end_date > settings.date_upper_bound:
        return None

    return CandidateFact(
        subject_qid=person_qid,
        subject_label=person_label,
        subject_aliases=[],
        domain=template.domain,
        topic=template.topic,
        answer_type=template.answer_type,
        question_family=template.question_family,
        subject_type_qids=[template.subject_type_qid],
        target_property_pid="COMPOSED_FIRST_DEGREE_UNIVERSITY",
        target_property_label="first degree university",
        answer_qids=[university_qid],
        answer_labels=[university_label],
        answer_aliases=[],
        date_property_pid="P582",
        date_value=first_end_date,
        target_time=settings.target_time,
        canonical_question="",
        newness_metadata={
            "anchor_kind": "statement_qualifier",
            "anchor_property_pid": "P582",
            "anchor_value": first_end_date,
            "reason": "education_end_time_not_earlier_than_target_time",
            "what_is_new": "the first degree completion",
        },
        reasoning_style="multi_hop_join",
        hop_count=2,
        reasoning_path=[
            build_reasoning_hop(
                source_qid=person_qid,
                source_label=person_label,
                property_pid="P69",
                property_label="educated at",
                target_qid=university_qid,
                target_label=university_label,
                role="bridge",
                qualifiers={"P512": degree_qid, "P582": first_end_date},
            ),
            build_reasoning_hop(
                source_qid=university_qid,
                source_label=university_label,
                property_pid="DERIVED_FIRST_DEGREE_SELECTION",
                property_label="first degree selection",
                target_qid=university_qid,
                target_label=university_label,
                role="answer",
            ),
        ],
        bridge_entities=[build_bridge_entity(qid=university_qid, label=university_label, role="university")],
        derivation_signature={
            "style": "multi_hop_join",
            "rule": "earliest_unique_degree_completion",
            "selected_end_date": first_end_date,
            "selected_degree_qid": degree_qid,
        },
        provenance_complete=True,
        source_metadata={
            "wikidata_access_date": settings.run_date,
            "retrieval_method": "wbgetentities composed claims",
            "question_format_args": {"descriptor": person_label},
            "composed_from": {
                "person_qid": person_qid,
                "selected_university_qid": university_qid,
                "selected_degree_qid": degree_qid,
                "selected_degree_label": degree_label,
                "selected_end_date": first_end_date,
            },
            "multi_hop_unique": True,
            "required_reasoning_clues": ["first degree"],
        },
    )


def build_first_degree_candidate_from_person_qid(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
    person_qid: str,
) -> CandidateFact | None:
    """Build a first-degree-university candidate from one person qid."""
    people = client.get_entities([person_qid])
    person = people.get(person_qid, {})
    if not person:
        return None

    referenced_qids: set[str] = set()
    for claim in person.get("claims", {}).get("P69", []):
        university_qid = claim.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id")
        if university_qid:
            referenced_qids.add(university_qid)
        degree_qid = _qualifier_qid(claim.get("qualifiers", {}), "P512")
        if degree_qid:
            referenced_qids.add(degree_qid)
    related_entities = client.get_entities(sorted(referenced_qids)) if referenced_qids else {}
    return build_first_degree_candidate_from_person_entity(
        settings=settings,
        template=template,
        person_qid=person_qid,
        person=person,
        related_entities=related_entities,
    )


def _dispatch_join_executor(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
) -> list[CandidateFact]:
    if template.domain == "wedding_age_gap":
        return _harvest_wedding_age_gap(client, settings, template)
    if template.domain == "person_first_degree_university":
        return _harvest_person_first_degree_university(client, settings, template)
    if template.domain == "film_source_work_author":
        return _harvest_film_source_work_author(client, settings, template)
    return []


def _dispatch_ordinal_executor(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
) -> list[CandidateFact]:
    if template.domain == "ordinal_tournament_winner":
        return _harvest_ordinal_tournament_winner(client, settings, template)
    return []


def _dispatch_aggregate_executor(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
) -> list[CandidateFact]:
    return []


REASONING_EXECUTORS: dict[str, JoinExecutor] = {
    "multi_hop_join": _dispatch_join_executor,
    "multi_hop_ordinal": _dispatch_ordinal_executor,
    "multi_hop_aggregate": _dispatch_aggregate_executor,
}


def _harvest_wedding_age_gap(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
) -> list[CandidateFact]:
    query = f"""
SELECT ?person ?personLabel ?spouse ?spouseLabel ?start ?birth1 ?birth2 WHERE {{
  ?person p:P26 ?stmt.
  ?stmt ps:P26 ?spouse;
        pq:P580 ?start.
  ?person wdt:P569 ?birth1.
  ?spouse wdt:P569 ?birth2.
  FILTER(?start >= "{settings.target_start_date}T00:00:00Z"^^xsd:dateTime)
  FILTER(?start <= "{settings.date_upper_bound}T23:59:59Z"^^xsd:dateTime)
  FILTER(STR(?person) < STR(?spouse))
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
LIMIT {settings.harvest_limit_per_template}
""".strip()
    rows = client.sparql_query(query)
    candidates: list[CandidateFact] = []
    for row in rows:
        person_qid = _qid(row["person"]["value"])
        spouse_qid = _qid(row["spouse"]["value"])
        person_label = row["personLabel"]["value"]
        spouse_label = row["spouseLabel"]["value"]
        start = row["start"]["value"][:10]
        birth1 = row["birth1"]["value"][:10]
        birth2 = row["birth2"]["value"][:10]
        age_gap = _age_gap_years(birth1, birth2, start)
        if age_gap is None:
            continue
        descriptor = f"{person_label} and {spouse_label} at their wedding"
        candidates.append(
            CandidateFact(
                subject_qid=person_qid,
                subject_label=person_label,
                subject_aliases=[],
                domain=template.domain,
                topic=template.topic,
                answer_type=template.answer_type,
                question_family=template.question_family,
                subject_type_qids=[template.subject_type_qid],
                target_property_pid="COMPOSED_AGE_GAP",
                target_property_label="age gap at wedding",
                answer_qids=[f"VALUE:number:{age_gap}"],
                answer_labels=[str(age_gap)],
                answer_aliases=[],
                date_property_pid=template.date_property_pid,
                date_value=start,
                target_time=settings.target_time,
                canonical_question="",
                newness_metadata={
                    "anchor_kind": "statement_qualifier",
                    "anchor_property_pid": "P580",
                    "anchor_value": start,
                    "reason": "marriage_start_time_not_earlier_than_target_time",
                    "what_is_new": "the marriage event",
                },
                reasoning_style="multi_hop_aggregate",
                hop_count=2,
                reasoning_path=[
                    build_reasoning_hop(
                        source_qid=person_qid,
                        source_label=person_label,
                        property_pid="P26",
                        property_label="spouse",
                        target_qid=spouse_qid,
                        target_label=spouse_label,
                        role="bridge",
                    ),
                    build_reasoning_hop(
                        source_qid=spouse_qid,
                        source_label=spouse_label,
                        property_pid="DERIVED_AGE_GAP_AT_EVENT",
                        property_label="age gap at wedding",
                        target_qid=f"VALUE:number:{age_gap}",
                        target_label=str(age_gap),
                        role="answer",
                    ),
                ],
                bridge_entities=[build_bridge_entity(qid=spouse_qid, label=spouse_label, role="spouse")],
                derivation_signature={
                    "style": "multi_hop_aggregate",
                    "rule": "age_gap_at_marriage_start",
                },
                provenance_complete=True,
                source_metadata={
                    "wikidata_access_date": settings.run_date,
                    "retrieval_method": "WDQS composed query",
                    "sparql_query": query,
                    "question_format_args": {"descriptor": descriptor},
                    "composed_from": {
                        "person_qid": person_qid,
                        "spouse_qid": spouse_qid,
                        "birth_dates": [birth1, birth2],
                        "marriage_start": start,
                    },
                    "multi_hop_unique": True,
                    "required_reasoning_clues": ["wedding"],
                },
            )
        )
    return candidates


def _harvest_person_first_degree_university(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
) -> list[CandidateFact]:
    query = f"""
SELECT DISTINCT ?person ?end WHERE {{
  ?person wdt:P31 wd:Q5.
  ?person p:P69 ?stmt.
  ?stmt ps:P69 ?university;
        pq:P512 ?degree;
        pq:P582 ?end.
  ?university wdt:P31/wdt:P279* wd:Q3918.
  FILTER(?end >= "{settings.target_start_date}T00:00:00Z"^^xsd:dateTime)
  FILTER(?end <= "{settings.date_upper_bound}T23:59:59Z"^^xsd:dateTime)
}}
LIMIT {max(settings.harvest_limit_per_template * 5, settings.harvest_limit_per_template)}
""".strip()
    rows = client.sparql_query(query)
    candidates: list[CandidateFact] = []
    person_qids: list[str] = []
    seen_people: set[str] = set()
    for row in rows:
        person_qid = _qid(row["person"]["value"])
        if person_qid in seen_people:
            continue
        seen_people.add(person_qid)
        person_qids.append(person_qid)
    if not person_qids:
        return candidates

    people = client.get_entities(person_qids)
    referenced_qids: set[str] = set()
    for person_qid in person_qids:
        person = people.get(person_qid, {})
        for claim in person.get("claims", {}).get("P69", []):
            university_qid = claim.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id")
            if university_qid:
                referenced_qids.add(university_qid)
            degree_qid = _qualifier_qid(claim.get("qualifiers", {}), "P512")
            if degree_qid:
                referenced_qids.add(degree_qid)
    related_entities = client.get_entities(sorted(referenced_qids)) if referenced_qids else {}

    for person_qid in person_qids:
        person = people.get(person_qid, {})
        candidate = build_first_degree_candidate_from_person_entity(
            settings=settings,
            template=template,
            person_qid=person_qid,
            person=person,
            related_entities=related_entities,
        )
        if candidate is None:
            continue
        candidate.source_metadata["retrieval_method"] = (
            "WDQS person seed + batched wbgetentities composed claims"
        )
        candidate.source_metadata["sparql_query"] = query
        candidates.append(candidate)
        if len(candidates) >= settings.harvest_limit_per_template:
            break
    return candidates


def _harvest_film_source_work_author(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
) -> list[CandidateFact]:
    query = f"""
SELECT ?film ?filmLabel ?sourceWork ?sourceWorkLabel ?author ?authorLabel ?date WHERE {{
  ?film wdt:P31/wdt:P279* wd:Q11424;
        wdt:P577 ?date;
        wdt:P144 ?sourceWork.
  ?sourceWork wdt:P50 ?author.
  FILTER(?date >= "{settings.target_start_date}T00:00:00Z"^^xsd:dateTime)
  FILTER(?date <= "{settings.date_upper_bound}T23:59:59Z"^^xsd:dateTime)
  FILTER NOT EXISTS {{
    ?film wdt:P144 ?otherSourceWork.
    FILTER(?otherSourceWork != ?sourceWork)
  }}
  FILTER NOT EXISTS {{
    ?sourceWork wdt:P50 ?otherAuthor.
    FILTER(?otherAuthor != ?author)
  }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
LIMIT {settings.harvest_limit_per_template}
""".strip()
    rows = client.sparql_query(query)
    candidates: list[CandidateFact] = []
    for row in rows:
        film_qid = _qid(row["film"]["value"])
        film_label = row["filmLabel"]["value"]
        source_work_qid = _qid(row["sourceWork"]["value"])
        source_work_label = row["sourceWorkLabel"]["value"]
        author_qid = _qid(row["author"]["value"])
        author_label = row["authorLabel"]["value"]
        date_value = row["date"]["value"][:10]
        candidates.append(
            CandidateFact(
                subject_qid=film_qid,
                subject_label=film_label,
                subject_aliases=[],
                domain=template.domain,
                topic=template.topic,
                answer_type=template.answer_type,
                question_family=template.question_family,
                subject_type_qids=[template.subject_type_qid],
                target_property_pid="COMPOSED_SOURCE_WORK_AUTHOR",
                target_property_label="author of source work",
                answer_qids=[author_qid],
                answer_labels=[author_label],
                answer_aliases=[],
                date_property_pid=template.date_property_pid,
                date_value=date_value,
                target_time=settings.target_time,
                canonical_question="",
                newness_metadata={
                    "anchor_kind": "subject_date_property",
                    "anchor_property_pid": template.date_property_pid,
                    "anchor_value": date_value,
                    "reason": "film_release_date_not_earlier_than_target_time",
                },
                reasoning_style="multi_hop_join",
                hop_count=2,
                reasoning_path=[
                    build_reasoning_hop(
                        source_qid=film_qid,
                        source_label=film_label,
                        property_pid="P144",
                        property_label="based on",
                        target_qid=source_work_qid,
                        target_label=source_work_label,
                        role="bridge",
                    ),
                    build_reasoning_hop(
                        source_qid=source_work_qid,
                        source_label=source_work_label,
                        property_pid="P50",
                        property_label="author",
                        target_qid=author_qid,
                        target_label=author_label,
                        role="answer",
                    ),
                ],
                bridge_entities=[build_bridge_entity(qid=source_work_qid, label=source_work_label, role="source_work")],
                derivation_signature={
                    "style": "multi_hop_join",
                    "rule": "film_based_on_source_work_author",
                    "bridge_property_pid": "P144",
                    "answer_property_pid": "P50",
                },
                provenance_complete=True,
                source_metadata={
                    "wikidata_access_date": settings.run_date,
                    "retrieval_method": "WDQS compositional multi-hop query",
                    "sparql_query": query,
                    "question_format_args": {"descriptor": film_label},
                    "multi_hop_unique": True,
                    "required_reasoning_clues": ["based on"],
                    "bridge_labels": [source_work_label],
                },
            )
        )
    return candidates


def _harvest_ordinal_tournament_winner(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
) -> list[CandidateFact]:
    query = f"""
SELECT ?edition ?series ?winner ?date ?seriesPropertyPid ?datePropertyPid WHERE {{
  {{
    ?edition wdt:P31/wdt:P279* wd:{template.subject_type_qid};
             wdt:P179 ?series;
             wdt:P585 ?date;
             wdt:{template.target_property_pid} ?winner.
    BIND("P179" AS ?seriesPropertyPid)
    BIND("P585" AS ?datePropertyPid)
  }}
  UNION
  {{
    ?edition wdt:P31/wdt:P279* wd:Q27020041;
             wdt:P3450 ?series;
             wdt:{template.target_property_pid} ?winner.
    OPTIONAL {{ ?edition wdt:P582 ?seasonEnd }}
    OPTIONAL {{ ?edition wdt:P580 ?seasonStart }}
    BIND(COALESCE(?seasonEnd, ?seasonStart) AS ?date)
    FILTER(BOUND(?date))
    BIND("P3450" AS ?seriesPropertyPid)
    BIND(IF(BOUND(?seasonEnd), "P582", "P580") AS ?datePropertyPid)
  }}
  FILTER(?date >= "{settings.target_start_date}T00:00:00Z"^^xsd:dateTime)
  FILTER(?date <= "{settings.date_upper_bound}T23:59:59Z"^^xsd:dateTime)
  FILTER NOT EXISTS {{
    ?edition wdt:{template.target_property_pid} ?otherWinner.
    FILTER(?otherWinner != ?winner)
  }}
}}
ORDER BY ?date
LIMIT {max(settings.harvest_limit_per_template * 5, settings.harvest_limit_per_template)}
""".strip()
    rows = client.sparql_query(query)
    entity_qids: set[str] = set()
    for row in rows:
        entity_qids.add(_qid(row["edition"]["value"]))
        entity_qids.add(_qid(row["series"]["value"]))
        entity_qids.add(_qid(row["winner"]["value"]))
    entities = client.get_entities(sorted(entity_qids)) if entity_qids else {}
    candidates: list[CandidateFact] = []
    for row in rows:
        edition_qid = _qid(row["edition"]["value"])
        series_qid = _qid(row["series"]["value"])
        winner_qid = _qid(row["winner"]["value"])
        series_property_pid = row.get("seriesPropertyPid", {}).get("value", "P179")
        date_property_pid = row.get("datePropertyPid", {}).get("value", template.date_property_pid)
        edition_label = _label(entities.get(edition_qid, {})) or edition_qid
        series_label = _label(entities.get(series_qid, {})) or series_qid
        winner_label = _label(entities.get(winner_qid, {})) or winner_qid
        if not series_label:
            continue
        descriptor = _strip_year_tokens(series_label)
        if not descriptor:
            continue
        if not winner_label or winner_label == winner_qid:
            continue
        date_value = row["date"]["value"][:10]
        ordinal_value, history_complete = _ordinal_for_series_edition(
            client=client,
            series_qid=series_qid,
            edition_qid=edition_qid,
            series_property_pid=series_property_pid,
            date_property_pid=date_property_pid,
        )
        if ordinal_value is None:
            continue
        ordinal_rendered = _render_ordinal(ordinal_value)
        candidates.append(
            CandidateFact(
                subject_qid=series_qid,
                subject_label=descriptor,
                subject_aliases=[],
                domain=template.domain,
                topic=template.topic,
                answer_type=template.answer_type,
                question_family=template.question_family,
                subject_type_qids=[template.subject_type_qid],
                target_property_pid=template.target_property_pid,
                target_property_label=template.target_property_label,
                answer_qids=[winner_qid],
                answer_labels=[winner_label],
                answer_aliases=[],
                date_property_pid=template.date_property_pid,
                date_value=date_value,
                target_time=settings.target_time,
                canonical_question="",
                newness_metadata={
                    "anchor_kind": "edition_date_property",
                    "anchor_property_pid": date_property_pid,
                    "anchor_value": date_value,
                    "reason": "tournament_edition_date_not_earlier_than_target_time",
                    "what_is_new": "the tournament edition",
                },
                reasoning_style="multi_hop_ordinal",
                hop_count=2,
                reasoning_path=[
                    build_reasoning_hop(
                        source_qid=series_qid,
                        source_label=descriptor,
                        property_pid=series_property_pid,
                        property_label="has edition",
                        target_qid=edition_qid,
                        target_label=edition_label,
                        role="bridge",
                    ),
                    build_reasoning_hop(
                        source_qid=edition_qid,
                        source_label=edition_label,
                        property_pid=template.target_property_pid,
                        property_label=template.target_property_label,
                        target_qid=winner_qid,
                        target_label=winner_label,
                        role="answer",
                    ),
                ],
                bridge_entities=[build_bridge_entity(qid=edition_qid, label=edition_label, role="edition")],
                derivation_signature={
                    "style": "multi_hop_ordinal",
                    "rule": "ordinal_series_edition_winner",
                    "ordinal_value": ordinal_value,
                    "ordinal_rendered": ordinal_rendered,
                    "series_property_pid": series_property_pid,
                    "date_property_pid": date_property_pid,
                },
                provenance_complete=True,
                source_metadata={
                    "wikidata_access_date": settings.run_date,
                    "retrieval_method": "WDQS edition seed + wbgetentities + WDQS ordinal history query",
                    "sparql_query": query,
                    "question_format_args": {
                        "descriptor": descriptor,
                        "ordinal": ordinal_rendered,
                    },
                    "ordinal_metadata": {
                        "ordinal_value": ordinal_value,
                        "ordinal_rendered": ordinal_rendered,
                        "edition_qid": edition_qid,
                        "series_qid": series_qid,
                        "descriptor": descriptor,
                        "series_label_raw": series_label,
                        "series_history_complete": history_complete,
                        "series_property_pid": series_property_pid,
                        "date_property_pid": date_property_pid,
                    },
                    "multi_hop_unique": True,
                    "required_reasoning_clues": ["edition", ordinal_rendered],
                },
            )
        )
        if len(candidates) >= settings.harvest_limit_per_template:
            break
    return candidates


def _ordinal_for_series_edition(
    client: WikidataClient,
    series_qid: str,
    edition_qid: str,
    series_property_pid: str,
    date_property_pid: str,
) -> tuple[int | None, bool]:
    """Return the ordinal position of one edition within its series."""
    query = f"""
SELECT ?edition ?date WHERE {{
  ?edition wdt:{series_property_pid} wd:{series_qid};
           wdt:{date_property_pid} ?date.
}}
""".strip()
    rows = client.sparql_query(query)
    dated_editions: list[tuple[str, str]] = []
    for row in rows:
        dated_editions.append((_qid(row["edition"]["value"]), row["date"]["value"][:10]))
    if not dated_editions:
        return None, False
    sorted_editions = sorted(dated_editions, key=lambda item: (item[1], item[0]))
    ordinal_lookup = {qid: index for index, (qid, _) in enumerate(sorted_editions, start=1)}
    return ordinal_lookup.get(edition_qid), True


def _qid(uri: str) -> str:
    return uri.rsplit("/", 1)[-1]


def _label(entity: dict[str, Any]) -> str:
    return entity.get("labels", {}).get("en", {}).get("value", "")


def _claim_time(entity: dict[str, Any], pid: str) -> str | None:
    claims = entity.get("claims", {}).get(pid, [])
    if not claims:
        return None
    value = claims[0].get("mainsnak", {}).get("datavalue", {}).get("value", {})
    time = value.get("time")
    if not time:
        return None
    return time[1:11]


def _claim_qids(entity: dict[str, Any], pid: str) -> list[str]:
    claims = entity.get("claims", {}).get(pid, [])
    qids: list[str] = []
    for claim in claims:
        qid = claim.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id")
        if qid:
            qids.append(qid)
    return qids


def _qualifier_time(qualifiers: dict[str, list[dict[str, Any]]], pid: str) -> str | None:
    values = qualifiers.get(pid, [])
    if not values:
        return None
    time = values[0].get("datavalue", {}).get("value", {}).get("time")
    if not time:
        return None
    return time[1:11]


def _qualifier_qid(qualifiers: dict[str, list[dict[str, Any]]], pid: str) -> str | None:
    values = qualifiers.get(pid, [])
    if not values:
        return None
    return values[0].get("datavalue", {}).get("value", {}).get("id")


def _qualifier_precision(qualifiers: dict[str, list[dict[str, Any]]], pid: str) -> int | None:
    values = qualifiers.get(pid, [])
    if not values:
        return None
    return values[0].get("datavalue", {}).get("value", {}).get("precision")


def _age_gap_years(birth1: str, birth2: str, event_date: str) -> int | None:
    """Compute the age gap in whole years at an event date."""
    b1 = date.fromisoformat(birth1)
    b2 = date.fromisoformat(birth2)
    event = date.fromisoformat(event_date)
    if b1 > event or b2 > event:
        return None
    age1 = _age_on_date(b1, event)
    age2 = _age_on_date(b2, event)
    return abs(age1 - age2)


def _age_on_date(birth_date: date, event_date: date) -> int:
    years = event_date.year - birth_date.year
    if (event_date.month, event_date.day) < (birth_date.month, birth_date.day):
        years -= 1
    return years


def _render_ordinal(value: int) -> str:
    """Render a positive integer as an English ordinal."""
    if 10 <= value % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(value % 10, "th")
    return f"{value}{suffix}"


def _strip_year_tokens(label: str) -> str:
    """Remove year tokens from a label to form a non-temporal descriptor."""
    text = re.sub(r"\b(17|18|19|20|21)\d{2}\b", "", label)
    text = re.sub(r"\s+", " ", text).strip(" -,:")
    return text.strip()
