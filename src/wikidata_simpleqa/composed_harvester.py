"""Backward-compatible compositional multi-hop executor entry points."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
import re
from typing import Any, Callable

from .config import Settings
from .date_answers import normalize_wikidata_date_literal
from .models import CandidateFact, DomainTemplate
from .reasoning import (
    build_bridge_entity,
    build_reasoning_hop,
    normalize_reasoning_style,
)
from .sparql_queries import build_candidate_query, build_count_candidate_query
from .subject_resources import canonical_subject_resource
from .wikidata_client import WikidataClient

JoinExecutor = Callable[[WikidataClient, Settings, DomainTemplate], list[CandidateFact]]
QID_LIKE_LABEL_PATTERN = re.compile(r"^Q\d+$")
HEAVY_QUERY_PROBLEM_KINDS = {
    "chunked_office_holder_lookup_failed",
    "chunked_office_history_lookup_failed",
    "chunked_acquisition_price_lookup_failed",
    "chunked_player_goal_lookup_failed",
    "time_windowed_tournament_seed_failed",
    "time_windowed_acquisition_seed_failed",
}


def harvest_composed_candidates(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
) -> list[CandidateFact]:
    """Harvest candidates for supported compositional multi-hop templates."""
    reasoning_style = normalize_reasoning_style(template.reasoning_style)
    executor = REASONING_EXECUTORS.get(reasoning_style)
    if executor is None:
        client.record_problem(
            "unsupported_reasoning_style",
            "No harvesting executor is registered for this reasoning style.",
            domain=template.domain,
            reasoning_style=reasoning_style,
        )
        _run_support_probe_if_possible(client, settings, template)
        return []
    normalized_template = replace(template, reasoning_style=reasoning_style)
    candidates = executor(client, settings, normalized_template)
    if candidates:
        return candidates
    fallback_candidates = _generic_count_candidates(client, settings, normalized_template)
    if fallback_candidates:
        return fallback_candidates
    _run_support_probe_if_possible(client, settings, normalized_template)
    return []


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
        subject_resource_url, subject_resource_key = canonical_subject_resource(
            person_qid,
            person,
        )
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
            subject_resource_url=subject_resource_url,
            subject_resource_key=subject_resource_key,
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
    subject_resource_url, subject_resource_key = canonical_subject_resource(
        person_qid,
        person,
    )

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
        subject_resource_url=subject_resource_url,
        subject_resource_key=subject_resource_key,
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
    if template.domain == "tv_series_source_work_author":
        return _harvest_source_work_author(client, settings, template)
    if template.domain == "company_that_released_product_founder":
        return _harvest_bridge_org_founder(
            client=client,
            settings=settings,
            template=template,
            bridge_property_pid="P176",
            bridge_property_label="manufacturer",
            answer_property_pid="P112",
            answer_property_label="founder",
            unique_rule="product_manufacturer_founder",
        )
    if template.domain == "company_that_developed_benchmark_founder":
        return _harvest_bridge_org_founder(
            client=client,
            settings=settings,
            template=template,
            bridge_property_pid="P178",
            bridge_property_label="developer",
            answer_property_pid="P112",
            answer_property_label="founder",
            unique_rule="benchmark_developer_founder",
        )
    if template.domain == "terminal_operator_country":
        return _harvest_bridge_org_country(
            client=client,
            settings=settings,
            template=template,
            bridge_property_pid="P137",
            bridge_property_label="operator",
            answer_property_pid="P17",
            answer_property_label="country",
            unique_rule="terminal_operator_country",
        )
    if template.domain == "acquisition_purchase_price":
        return _harvest_acquisition_purchase_price(client, settings, template)
    if template.answer_format == "number" and not template.target_property_pid.startswith("COMPOSED_"):
        return _generic_count_candidates(client, settings, template)
    if not template.target_property_pid.startswith("COMPOSED_"):
        return _generic_direct_candidates(client, settings, template)
    client.record_problem(
        "missing_join_executor",
        "No domain-specific multi-hop join executor is implemented for this template.",
        domain=template.domain,
        target_property_pid=template.target_property_pid,
    )
    return []


def _dispatch_ordinal_executor(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
) -> list[CandidateFact]:
    if template.domain == "ordinal_tournament_winner":
        return _harvest_ordinal_tournament_winner(client, settings, template)
    if template.domain in {"ordinal_tournament_host_city", "ordinal_tournament_host_country"}:
        return _harvest_ordinal_tournament_answer_property(client, settings, template)
    if template.domain == "ordinal_film_in_series_director":
        return _harvest_series_member_answer_property(
            client=client,
            settings=settings,
            template=template,
            member_type_qid="Q11424",
        )
    if template.domain == "ordinal_volume_author":
        return _harvest_series_member_answer_property(
            client=client,
            settings=settings,
            template=template,
            member_type_qid="Q571",
        )
    if template.domain == "ordinal_spouse":
        return _harvest_subject_role_history_answer_property(
            client=client,
            settings=settings,
            template=template,
            subject_type_qid="Q5",
            role_property_pid="P26",
        )
    if template.domain == "ordinal_country_president":
        return _harvest_associated_office_holder_history_answer_property(
            client=client,
            settings=settings,
            template=template,
            subject_type_qid="Q6256",
            office_label_terms=("president",),
            office_association_property_pids=("P1001", "P17"),
            statement_association_qualifier_pids=("P17", "P1001", "P642"),
        )
    if template.domain == "ordinal_country_prime_minister":
        return _harvest_associated_office_holder_history_answer_property(
            client=client,
            settings=settings,
            template=template,
            subject_type_qid="Q6256",
            office_label_terms=("prime minister",),
            office_association_property_pids=("P1001", "P17"),
            statement_association_qualifier_pids=("P17", "P1001", "P642"),
        )
    if template.domain == "ordinal_religious_leader":
        return _harvest_associated_office_holder_history_answer_property(
            client=client,
            settings=settings,
            template=template,
            subject_type_qid="Q246434",
            direct_subject_office=True,
        )
    if template.domain == "ordinal_university_chancellor":
        return _harvest_associated_office_holder_history_answer_property(
            client=client,
            settings=settings,
            template=template,
            subject_type_qid="Q3918",
            office_label_terms=("chancellor",),
            office_association_property_pids=("P1001", "P642", "P17"),
            statement_association_qualifier_pids=("P642", "P108", "P1001"),
        )
    if template.domain == "footballer_goals_in_ordinal_tournament":
        return _harvest_footballer_goals_in_ordinal_tournament(client, settings, template)
    if template.domain == "ordinal_company_ceo":
        return _harvest_subject_role_history_answer_property(
            client=client,
            settings=settings,
            template=template,
            subject_type_qid="Q783794",
            role_property_pid="P169",
        )
    if template.domain == "ordinal_space_mission_commander":
        return _harvest_subject_role_history_answer_property(
            client=client,
            settings=settings,
            template=template,
            subject_type_qid="Q2133344",
            role_property_pid="P1037",
        )
    client.record_problem(
        "missing_ordinal_executor",
        "No domain-specific ordinal executor is implemented for this template.",
        domain=template.domain,
        target_property_pid=template.target_property_pid,
    )
    return []


def _dispatch_aggregate_executor(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
) -> list[CandidateFact]:
    if template.answer_format == "number" and not template.target_property_pid.startswith("COMPOSED_"):
        return _generic_count_candidates(client, settings, template)
    client.record_problem(
        "missing_aggregate_executor",
        "No domain-specific aggregate executor is implemented for this template.",
        domain=template.domain,
        target_property_pid=template.target_property_pid,
    )
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
    return _harvest_source_work_author(client, settings, template)


def _harvest_source_work_author(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
) -> list[CandidateFact]:
    query = f"""
SELECT ?subject ?subjectLabel ?sourceWork ?sourceWorkLabel ?author ?authorLabel ?date WHERE {{
  ?subject wdt:P31/wdt:P279* wd:{template.subject_type_qid};
           wdt:{template.date_property_pid} ?date;
           wdt:P144 ?sourceWork.
  ?sourceWork wdt:P50 ?author.
  FILTER(?date >= "{settings.target_start_date}T00:00:00Z"^^xsd:dateTime)
  FILTER(?date <= "{settings.date_upper_bound}T23:59:59Z"^^xsd:dateTime)
  FILTER NOT EXISTS {{
    ?subject wdt:P144 ?otherSourceWork.
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
        subject_qid = _qid(row["subject"]["value"])
        subject_label = row["subjectLabel"]["value"]
        source_work_qid = _qid(row["sourceWork"]["value"])
        source_work_label = row["sourceWorkLabel"]["value"]
        author_qid = _qid(row["author"]["value"])
        author_label = row["authorLabel"]["value"]
        date_value = row["date"]["value"][:10]
        subject_resource_url, subject_resource_key = canonical_subject_resource(subject_qid)
        candidates.append(
            CandidateFact(
                subject_qid=subject_qid,
                subject_label=subject_label,
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
                    "reason": "subject_release_date_not_earlier_than_target_time",
                },
                reasoning_style="multi_hop_join",
                hop_count=2,
                reasoning_path=[
                    build_reasoning_hop(
                        source_qid=subject_qid,
                        source_label=subject_label,
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
                    "rule": "subject_based_on_source_work_author",
                    "bridge_property_pid": "P144",
                    "answer_property_pid": "P50",
                },
                provenance_complete=True,
                subject_resource_url=subject_resource_url,
                subject_resource_key=subject_resource_key,
                source_metadata={
                    "wikidata_access_date": settings.run_date,
                    "retrieval_method": "WDQS compositional multi-hop query",
                    "sparql_query": query,
                    "question_format_args": {"descriptor": subject_label},
                    "multi_hop_unique": True,
                    "required_reasoning_clues": ["based on"],
                    "bridge_labels": [source_work_label],
                },
            )
        )
    return candidates


def _harvest_bridge_org_founder(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
    *,
    bridge_property_pid: str,
    bridge_property_label: str,
    answer_property_pid: str,
    answer_property_label: str,
    unique_rule: str,
) -> list[CandidateFact]:
    """Harvest subject -> organization -> founder joins with uniqueness checks."""
    query = f"""
SELECT ?subject ?subjectLabel ?bridgeOrg ?bridgeOrgLabel ?founder ?founderLabel ?date WHERE {{
  ?subject wdt:P31/wdt:P279* wd:{template.subject_type_qid};
           wdt:{template.date_property_pid} ?date;
           wdt:{bridge_property_pid} ?bridgeOrg.
  ?bridgeOrg wdt:{answer_property_pid} ?founder.
  FILTER(?date >= "{settings.target_start_date}T00:00:00Z"^^xsd:dateTime)
  FILTER(?date <= "{settings.date_upper_bound}T23:59:59Z"^^xsd:dateTime)
  FILTER NOT EXISTS {{
    ?subject wdt:{bridge_property_pid} ?otherBridgeOrg.
    FILTER(?otherBridgeOrg != ?bridgeOrg)
  }}
  FILTER NOT EXISTS {{
    ?bridgeOrg wdt:{answer_property_pid} ?otherFounder.
    FILTER(?otherFounder != ?founder)
  }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
LIMIT {settings.harvest_limit_per_template}
""".strip()
    rows = client.sparql_query(query)
    renamed_rows: list[dict[str, Any]] = []
    for row in rows:
        updated = dict(row)
        updated["answer"] = updated.pop("founder")
        updated["answerLabel"] = updated.pop("founderLabel")
        renamed_rows.append(updated)
    return _build_bridge_join_candidates(
        rows=renamed_rows,
        settings=settings,
        template=template,
        bridge_property_pid=bridge_property_pid,
        bridge_property_label=bridge_property_label,
        answer_property_pid=answer_property_pid,
        answer_property_label=answer_property_label,
        unique_rule=unique_rule,
        query=query,
    )


def _harvest_bridge_org_country(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
    *,
    bridge_property_pid: str,
    bridge_property_label: str,
    answer_property_pid: str,
    answer_property_label: str,
    unique_rule: str,
) -> list[CandidateFact]:
    """Harvest subject -> organization -> country joins with uniqueness checks."""
    query = f"""
SELECT ?subject ?subjectLabel ?bridgeOrg ?bridgeOrgLabel ?country ?countryLabel ?date WHERE {{
  ?subject wdt:P31/wdt:P279* wd:{template.subject_type_qid};
           wdt:{template.date_property_pid} ?date;
           wdt:{bridge_property_pid} ?bridgeOrg.
  ?bridgeOrg wdt:{answer_property_pid} ?country.
  FILTER(?date >= "{settings.target_start_date}T00:00:00Z"^^xsd:dateTime)
  FILTER(?date <= "{settings.date_upper_bound}T23:59:59Z"^^xsd:dateTime)
  FILTER NOT EXISTS {{
    ?subject wdt:{bridge_property_pid} ?otherBridgeOrg.
    FILTER(?otherBridgeOrg != ?bridgeOrg)
  }}
  FILTER NOT EXISTS {{
    ?bridgeOrg wdt:{answer_property_pid} ?otherCountry.
    FILTER(?otherCountry != ?country)
  }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
LIMIT {settings.harvest_limit_per_template}
""".strip()
    rows = client.sparql_query(query)
    renamed_rows: list[dict[str, Any]] = []
    for row in rows:
        updated = dict(row)
        updated["answer"] = updated.pop("country")
        updated["answerLabel"] = updated.pop("countryLabel")
        renamed_rows.append(updated)
    return _build_bridge_join_candidates(
        rows=renamed_rows,
        settings=settings,
        template=template,
        bridge_property_pid=bridge_property_pid,
        bridge_property_label=bridge_property_label,
        answer_property_pid=answer_property_pid,
        answer_property_label=answer_property_label,
        unique_rule=unique_rule,
        query=query,
    )


def _build_bridge_join_candidates(
    *,
    rows: list[dict[str, Any]],
    settings: Settings,
    template: DomainTemplate,
    bridge_property_pid: str,
    bridge_property_label: str,
    answer_property_pid: str,
    answer_property_label: str,
    unique_rule: str,
    query: str,
) -> list[CandidateFact]:
    """Build serialized two-hop candidates from bridge-join query rows."""
    candidates: list[CandidateFact] = []
    for row in rows:
        subject_qid = _qid(row["subject"]["value"])
        subject_label = row["subjectLabel"]["value"]
        bridge_qid = _qid(row["bridgeOrg"]["value"])
        bridge_label = row["bridgeOrgLabel"]["value"]
        answer_qid = _qid(row["answer"]["value"])
        answer_label = row["answerLabel"]["value"]
        date_value = row["date"]["value"][:10]
        subject_resource_url, subject_resource_key = canonical_subject_resource(subject_qid)
        candidates.append(
            CandidateFact(
                subject_qid=subject_qid,
                subject_label=subject_label,
                subject_aliases=[],
                domain=template.domain,
                topic=template.topic,
                answer_type=template.answer_type,
                question_family=template.question_family,
                subject_type_qids=[template.subject_type_qid],
                target_property_pid=template.target_property_pid,
                target_property_label=template.target_property_label,
                answer_qids=[answer_qid],
                answer_labels=[answer_label],
                answer_aliases=[],
                date_property_pid=template.date_property_pid,
                date_value=date_value,
                target_time=settings.target_time,
                canonical_question="",
                newness_metadata={
                    "anchor_kind": "subject_date_property",
                    "anchor_property_pid": template.date_property_pid,
                    "anchor_value": date_value,
                    "reason": "subject_or_event_date_not_earlier_than_target_time",
                },
                reasoning_style="multi_hop_join",
                hop_count=2,
                reasoning_path=[
                    build_reasoning_hop(
                        source_qid=subject_qid,
                        source_label=subject_label,
                        property_pid=bridge_property_pid,
                        property_label=bridge_property_label,
                        target_qid=bridge_qid,
                        target_label=bridge_label,
                        role="bridge",
                    ),
                    build_reasoning_hop(
                        source_qid=bridge_qid,
                        source_label=bridge_label,
                        property_pid=answer_property_pid,
                        property_label=answer_property_label,
                        target_qid=answer_qid,
                        target_label=answer_label,
                        role="answer",
                    ),
                ],
                bridge_entities=[build_bridge_entity(qid=bridge_qid, label=bridge_label, role="organization")],
                derivation_signature={
                    "style": "multi_hop_join",
                    "rule": unique_rule,
                    "bridge_property_pid": bridge_property_pid,
                    "answer_property_pid": answer_property_pid,
                },
                provenance_complete=True,
                subject_resource_url=subject_resource_url,
                subject_resource_key=subject_resource_key,
                source_metadata={
                    "wikidata_access_date": settings.run_date,
                    "retrieval_method": "WDQS compositional multi-hop query",
                    "sparql_query": query,
                    "question_format_args": {"descriptor": subject_label},
                    "multi_hop_unique": True,
                    "required_reasoning_clues": template.reasoning_recipe.get(
                        "required_reasoning_clues",
                        [bridge_property_label],
                    ),
                    "bridge_labels": [bridge_label],
                },
            )
        )
    return candidates


def _harvest_ordinal_tournament_winner(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
) -> list[CandidateFact]:
    return _harvest_ordinal_tournament_answer_property(client, settings, template)


def _harvest_ordinal_tournament_answer_property(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
) -> list[CandidateFact]:
    query = f"""
SELECT ?edition ?series ?answer ?date ?seriesPropertyPid ?datePropertyPid WHERE {{
  {{
    ?edition wdt:P31/wdt:P279* wd:{template.subject_type_qid};
             wdt:P179 ?series;
             wdt:P585 ?date;
             wdt:{template.target_property_pid} ?answer.
    BIND("P179" AS ?seriesPropertyPid)
    BIND("P585" AS ?datePropertyPid)
  }}
  UNION
  {{
    ?edition wdt:P31/wdt:P279* wd:Q27020041;
             wdt:P3450 ?series;
             wdt:{template.target_property_pid} ?answer.
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
    ?edition wdt:{template.target_property_pid} ?otherAnswer.
    FILTER(?otherAnswer != ?answer)
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
        entity_qids.add(_qid(row["answer"]["value"]))
    entities = client.get_entities(sorted(entity_qids)) if entity_qids else {}
    candidates: list[CandidateFact] = []
    for row in rows:
        edition_qid = _qid(row["edition"]["value"])
        series_qid = _qid(row["series"]["value"])
        answer_qid = _qid(row["answer"]["value"])
        series_property_pid = row.get("seriesPropertyPid", {}).get("value", "P179")
        date_property_pid = row.get("datePropertyPid", {}).get("value", template.date_property_pid)
        edition_label = _label(entities.get(edition_qid, {})) or edition_qid
        series_label = _label(entities.get(series_qid, {})) or series_qid
        answer_label = _label(entities.get(answer_qid, {})) or answer_qid
        if not series_label:
            continue
        descriptor = _strip_year_tokens(series_label)
        if not descriptor:
            continue
        if not answer_label or answer_label == answer_qid:
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
        subject_resource_url, subject_resource_key = canonical_subject_resource(
            series_qid,
            entities.get(series_qid, {}),
        )
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
                answer_qids=[answer_qid],
                answer_labels=[answer_label],
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
                        target_qid=answer_qid,
                        target_label=answer_label,
                        role="answer",
                    ),
                ],
                bridge_entities=[build_bridge_entity(qid=edition_qid, label=edition_label, role="edition")],
                derivation_signature={
                    "style": "multi_hop_ordinal",
                    "rule": "ordinal_series_edition_answer",
                    "ordinal_value": ordinal_value,
                    "ordinal_rendered": ordinal_rendered,
                    "series_property_pid": series_property_pid,
                    "date_property_pid": date_property_pid,
                },
                provenance_complete=True,
                subject_resource_url=subject_resource_url,
                subject_resource_key=subject_resource_key,
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


def _harvest_series_member_answer_property(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
    *,
    member_type_qid: str,
) -> list[CandidateFact]:
    """Harvest ordinal candidates where a series member provides the answer."""
    query = f"""
SELECT ?series ?seriesLabel ?member ?memberLabel ?answer ?answerLabel ?date WHERE {{
  ?member wdt:P31/wdt:P279* wd:{member_type_qid};
          wdt:P179 ?series;
          wdt:{template.date_property_pid} ?date;
          wdt:{template.target_property_pid} ?answer.
  FILTER(?date >= "{settings.target_start_date}T00:00:00Z"^^xsd:dateTime)
  FILTER(?date <= "{settings.date_upper_bound}T23:59:59Z"^^xsd:dateTime)
  FILTER NOT EXISTS {{
    ?member wdt:{template.target_property_pid} ?otherAnswer.
    FILTER(?otherAnswer != ?answer)
  }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
ORDER BY ?series ?date ?member
LIMIT {max(settings.harvest_limit_per_template * 5, settings.harvest_limit_per_template)}
""".strip()
    rows = client.sparql_query(query)
    entity_qids: set[str] = set()
    for row in rows:
        entity_qids.add(_qid(row["series"]["value"]))
        entity_qids.add(_qid(row["member"]["value"]))
        entity_qids.add(_qid(row["answer"]["value"]))
    entities = client.get_entities(sorted(entity_qids)) if entity_qids else {}
    candidates: list[CandidateFact] = []
    for row in rows:
        series_qid = _qid(row["series"]["value"])
        member_qid = _qid(row["member"]["value"])
        answer_qid = _qid(row["answer"]["value"])
        series_label = _label(entities.get(series_qid, {})) or row["seriesLabel"]["value"]
        member_label = _label(entities.get(member_qid, {})) or row["memberLabel"]["value"]
        answer_label = _label(entities.get(answer_qid, {})) or row["answerLabel"]["value"]
        if not series_label or not member_label or not answer_label:
            continue
        descriptor = _strip_year_tokens(series_label)
        if not descriptor:
            continue
        date_value = row["date"]["value"][:10]
        ordinal_value, history_complete = _ordinal_for_series_member(
            client=client,
            series_qid=series_qid,
            member_type_qid=member_type_qid,
            date_property_pid=template.date_property_pid,
            member_qid=member_qid,
        )
        if ordinal_value is None:
            continue
        ordinal_rendered = _render_ordinal(ordinal_value)
        subject_resource_url, subject_resource_key = canonical_subject_resource(
            series_qid,
            entities.get(series_qid, {}),
        )
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
                answer_qids=[answer_qid],
                answer_labels=[answer_label],
                answer_aliases=[],
                date_property_pid=template.date_property_pid,
                date_value=date_value,
                target_time=settings.target_time,
                canonical_question="",
                newness_metadata={
                    "anchor_kind": "member_date_property",
                    "anchor_property_pid": template.date_property_pid,
                    "anchor_value": date_value,
                    "reason": "series_member_date_not_earlier_than_target_time",
                    "what_is_new": "the series member",
                },
                reasoning_style="multi_hop_ordinal",
                hop_count=2,
                reasoning_path=[
                    build_reasoning_hop(
                        source_qid=series_qid,
                        source_label=descriptor,
                        property_pid="P179",
                        property_label="part of the series",
                        target_qid=member_qid,
                        target_label=member_label,
                        role="bridge",
                    ),
                    build_reasoning_hop(
                        source_qid=member_qid,
                        source_label=member_label,
                        property_pid=template.target_property_pid,
                        property_label=template.target_property_label,
                        target_qid=answer_qid,
                        target_label=answer_label,
                        role="answer",
                    ),
                ],
                bridge_entities=[build_bridge_entity(qid=member_qid, label=member_label, role="series_member")],
                derivation_signature={
                    "style": "multi_hop_ordinal",
                    "rule": "ordinal_series_member_answer",
                    "ordinal_value": ordinal_value,
                    "ordinal_rendered": ordinal_rendered,
                    "member_type_qid": member_type_qid,
                },
                provenance_complete=True,
                subject_resource_url=subject_resource_url,
                subject_resource_key=subject_resource_key,
                source_metadata={
                    "wikidata_access_date": settings.run_date,
                    "retrieval_method": "WDQS series-member seed + WDQS ordinal history query",
                    "sparql_query": query,
                    "question_format_args": {
                        "descriptor": descriptor,
                        "ordinal": ordinal_rendered,
                    },
                    "ordinal_metadata": {
                        "ordinal_value": ordinal_value,
                        "ordinal_rendered": ordinal_rendered,
                        "member_qid": member_qid,
                        "series_qid": series_qid,
                        "descriptor": descriptor,
                        "series_label_raw": series_label,
                        "series_history_complete": history_complete,
                    },
                    "multi_hop_unique": True,
                    "required_reasoning_clues": ["series", ordinal_rendered],
                },
            )
        )
        if len(candidates) >= settings.harvest_limit_per_template:
            break
    return candidates


def _ordinal_for_series_member(
    client: WikidataClient,
    series_qid: str,
    member_type_qid: str,
    date_property_pid: str,
    member_qid: str,
) -> tuple[int | None, bool]:
    """Return the ordinal position of one series member among dated members."""
    query = f"""
SELECT ?member ?date WHERE {{
  ?member wdt:P31/wdt:P279* wd:{member_type_qid};
          wdt:P179 wd:{series_qid};
          wdt:{date_property_pid} ?date.
}}
""".strip()
    rows = client.sparql_query(query)
    dated_members = [(_qid(row["member"]["value"]), row["date"]["value"][:10]) for row in rows]
    if not dated_members:
        return None, False
    sorted_members = sorted(dated_members, key=lambda item: (item[1], item[0]))
    ordinal_lookup = {qid: index for index, (qid, _) in enumerate(sorted_members, start=1)}
    return ordinal_lookup.get(member_qid), True


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


def _harvest_subject_role_history_answer_property(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
    *,
    subject_type_qid: str,
    role_property_pid: str,
) -> list[CandidateFact]:
    """Harvest ordinal role-history candidates from subject-side qualified statements."""
    query = f"""
SELECT ?subject ?answer ?start WHERE {{
  ?subject wdt:P31/wdt:P279* wd:{subject_type_qid};
           p:{role_property_pid} ?stmt.
  ?stmt ps:{role_property_pid} ?answer;
        pq:P580 ?start.
  FILTER(?start >= "{settings.target_start_date}T00:00:00Z"^^xsd:dateTime)
  FILTER(?start <= "{settings.date_upper_bound}T23:59:59Z"^^xsd:dateTime)
}}
ORDER BY ?start ?subject
LIMIT {max(settings.harvest_limit_per_template * 5, settings.harvest_limit_per_template)}
""".strip()
    rows = client.sparql_query(query)
    history_map = _load_subject_role_history_map(
        client=client,
        subject_qids=sorted({_qid(row["subject"]["value"]) for row in rows}),
        role_property_pid=role_property_pid,
    )
    entity_qids: set[str] = set()
    for row in rows:
        entity_qids.add(_qid(row["subject"]["value"]))
        entity_qids.add(_qid(row["answer"]["value"]))
    entities = client.get_entities(sorted(entity_qids)) if entity_qids else {}
    candidates: list[CandidateFact] = []
    for row in rows:
        subject_qid = _qid(row["subject"]["value"])
        answer_qid = _qid(row["answer"]["value"])
        subject_label = _label(entities.get(subject_qid, {}))
        answer_label = _label(entities.get(answer_qid, {}))
        if not subject_label or not answer_label:
            continue
        descriptor = _strip_year_tokens(subject_label)
        if not descriptor:
            continue
        start_value = row["start"]["value"][:10]
        ordinal_value, history_complete = _ordinal_from_dated_pairs(
            history_map.get(subject_qid, []),
            target_qid=answer_qid,
            target_date=start_value,
        )
        if ordinal_value is None:
            continue
        ordinal_rendered = _render_ordinal(ordinal_value)
        statement_qid = (
            f"STATEMENT:{subject_qid}:{role_property_pid}:{start_value}:{answer_qid}"
        )
        subject_resource_url, subject_resource_key = canonical_subject_resource(
            subject_qid,
            entities.get(subject_qid, {}),
        )
        candidates.append(
            CandidateFact(
                subject_qid=subject_qid,
                subject_label=descriptor,
                subject_aliases=[],
                domain=template.domain,
                topic=template.topic,
                answer_type=template.answer_type,
                question_family=template.question_family,
                subject_type_qids=[template.subject_type_qid],
                target_property_pid=template.target_property_pid,
                target_property_label=template.target_property_label,
                answer_qids=[answer_qid],
                answer_labels=[answer_label],
                answer_aliases=_aliases(entities.get(answer_qid, {})),
                date_property_pid="P580",
                date_value=start_value,
                target_time=settings.target_time,
                canonical_question="",
                newness_metadata={
                    "anchor_kind": "statement_qualifier",
                    "anchor_property_pid": "P580",
                    "anchor_value": start_value,
                    "reason": "role_start_time_not_earlier_than_target_time",
                    "what_is_new": "the role appointment",
                },
                reasoning_style="multi_hop_ordinal",
                hop_count=2,
                reasoning_path=[
                    build_reasoning_hop(
                        source_qid=subject_qid,
                        source_label=descriptor,
                        property_pid=role_property_pid,
                        property_label=template.target_property_label,
                        target_qid=statement_qid,
                        target_label=f"{template.target_property_label} tenure",
                        role="bridge",
                        qualifiers={"P580": start_value},
                    ),
                    build_reasoning_hop(
                        source_qid=statement_qid,
                        source_label=f"{template.target_property_label} tenure",
                        property_pid="DERIVED_ORDINAL_ROLE_OCCUPANT",
                        property_label="ordinal role occupant",
                        target_qid=answer_qid,
                        target_label=answer_label,
                        role="answer",
                    ),
                ],
                bridge_entities=[
                    build_bridge_entity(
                        qid=statement_qid,
                        label=f"{template.target_property_label} tenure",
                        role="role_statement",
                    )
                ],
                derivation_signature={
                    "style": "multi_hop_ordinal",
                    "rule": "ordinal_subject_role_history_answer",
                    "ordinal_value": ordinal_value,
                    "ordinal_rendered": ordinal_rendered,
                    "role_property_pid": role_property_pid,
                },
                provenance_complete=True,
                subject_resource_url=subject_resource_url,
                subject_resource_key=subject_resource_key,
                source_metadata={
                    "wikidata_access_date": settings.run_date,
                    "retrieval_method": "WDQS qualified-role seed + batched WDQS role-history query",
                    "sparql_query": query,
                    "question_format_args": {
                        "descriptor": descriptor,
                        "ordinal": ordinal_rendered,
                    },
                    "ordinal_metadata": {
                        "ordinal_value": ordinal_value,
                        "ordinal_rendered": ordinal_rendered,
                        "descriptor": descriptor,
                        "subject_qid": subject_qid,
                        "subject_label_raw": subject_label,
                        "answer_qid": answer_qid,
                        "role_property_pid": role_property_pid,
                        "start_value": start_value,
                        "series_history_complete": history_complete,
                    },
                    "time_invariance": {
                        "historically_settled": True,
                        "history_complete": history_complete,
                        "allowed_property_pids": [role_property_pid],
                        "reason": "historical_role_sequence",
                    },
                    "multi_hop_unique": True,
                    "required_reasoning_clues": [ordinal_rendered],
                },
            )
        )
        if len(candidates) >= settings.harvest_limit_per_template:
            break
    return candidates


def _ordinal_for_subject_statement_series(
    client: WikidataClient,
    subject_qid: str,
    role_property_pid: str,
    answer_qid: str,
    start_value: str,
) -> tuple[int | None, bool]:
    """Return the ordinal of one dated subject-side role statement."""
    query = f"""
SELECT ?answer ?start WHERE {{
  wd:{subject_qid} p:{role_property_pid} ?stmt.
  ?stmt ps:{role_property_pid} ?answer;
        pq:P580 ?start.
}}
""".strip()
    rows = client.sparql_query(query)
    dated_roles = [(_qid(row["answer"]["value"]), row["start"]["value"][:10]) for row in rows]
    if not dated_roles:
        return None, False
    sorted_roles = sorted(dated_roles, key=lambda item: (item[1], item[0]))
    ordinal_lookup: dict[tuple[str, str], int] = {}
    seen_pairs: set[tuple[str, str]] = set()
    for index, pair in enumerate(sorted_roles, start=1):
        if pair in seen_pairs:
            continue
        seen_pairs.add(pair)
        ordinal_lookup[pair] = len(ordinal_lookup) + 1
    return ordinal_lookup.get((answer_qid, start_value)), True


def _harvest_associated_office_holder_history_answer_property(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
    *,
    subject_type_qid: str,
    office_label_terms: tuple[str, ...] = (),
    office_association_property_pids: tuple[str, ...] = (),
    statement_association_qualifier_pids: tuple[str, ...] = (),
    direct_subject_office: bool = False,
) -> list[CandidateFact]:
    """Harvest ordinal office-holder candidates from holder-side position statements."""
    subject_office_pairs = _load_subject_office_pairs(
        client=client,
        subject_type_qid=subject_type_qid,
        office_label_terms=office_label_terms,
        office_association_property_pids=office_association_property_pids,
        direct_subject_office=direct_subject_office,
    )
    rows = _load_recent_office_holder_rows(
        client=client,
        subject_office_pairs=subject_office_pairs,
        target_start_date=settings.target_start_date,
        date_upper_bound=settings.date_upper_bound,
        limit=max(settings.harvest_limit_per_template * 5, settings.harvest_limit_per_template),
        problem_domain=template.domain,
    )
    office_history_map = _load_office_holder_history_map(
        client=client,
        office_qids=sorted({_qid(row["office"]["value"]) for row in rows}),
        problem_domain=template.domain,
    )
    entity_qids: set[str] = set()
    for row in rows:
        entity_qids.add(_qid(row["subject"]["value"]))
        entity_qids.add(_qid(row["office"]["value"]))
        entity_qids.add(_qid(row["answer"]["value"]))
    entities = client.get_entities(sorted(entity_qids)) if entity_qids else {}
    candidates: list[CandidateFact] = []
    for row in rows:
        subject_qid = _qid(row["subject"]["value"])
        office_qid = _qid(row["office"]["value"])
        answer_qid = _qid(row["answer"]["value"])
        subject_label = _label(entities.get(subject_qid, {}))
        office_label = _label(entities.get(office_qid, {}))
        answer_label = _label(entities.get(answer_qid, {}))
        if not subject_label or not office_label or not answer_label:
            continue
        if office_label_terms and not _office_label_matches(office_label, office_label_terms):
            continue
        descriptor = _strip_year_tokens(subject_label)
        if not descriptor:
            continue
        start_value = row["start"]["value"][:10]
        ordinal_value, history_complete = _ordinal_from_dated_pairs(
            office_history_map.get(office_qid, []),
            target_qid=answer_qid,
            target_date=start_value,
        )
        if ordinal_value is None:
            continue
        ordinal_rendered = _render_ordinal(ordinal_value)
        statement_qid = f"STATEMENT:{office_qid}:P39:{start_value}:{answer_qid}"
        subject_resource_url, subject_resource_key = canonical_subject_resource(
            subject_qid,
            entities.get(subject_qid, {}),
        )
        candidates.append(
            CandidateFact(
                subject_qid=subject_qid,
                subject_label=descriptor,
                subject_aliases=[],
                domain=template.domain,
                topic=template.topic,
                answer_type=template.answer_type,
                question_family=template.question_family,
                subject_type_qids=[template.subject_type_qid],
                target_property_pid=template.target_property_pid,
                target_property_label=template.target_property_label,
                answer_qids=[answer_qid],
                answer_labels=[answer_label],
                answer_aliases=_aliases(entities.get(answer_qid, {})),
                date_property_pid="P580",
                date_value=start_value,
                target_time=settings.target_time,
                canonical_question="",
                newness_metadata={
                    "anchor_kind": "statement_qualifier",
                    "anchor_property_pid": "P580",
                    "anchor_value": start_value,
                    "reason": "office_holder_start_time_not_earlier_than_target_time",
                    "what_is_new": "the office appointment",
                },
                reasoning_style="multi_hop_ordinal",
                hop_count=3,
                reasoning_path=[
                    build_reasoning_hop(
                        source_qid=subject_qid,
                        source_label=descriptor,
                        property_pid="DERIVED_ASSOCIATED_OFFICE",
                        property_label="associated office",
                        target_qid=office_qid,
                        target_label=office_label,
                        role="bridge",
                    ),
                    build_reasoning_hop(
                        source_qid=office_qid,
                        source_label=office_label,
                        property_pid="P39",
                        property_label="position held",
                        target_qid=statement_qid,
                        target_label="office-holder tenure",
                        role="bridge",
                        qualifiers={"P580": start_value},
                    ),
                    build_reasoning_hop(
                        source_qid=statement_qid,
                        source_label="office-holder tenure",
                        property_pid="DERIVED_ORDINAL_ASSOCIATED_OFFICE_HOLDER",
                        property_label="ordinal associated office holder",
                        target_qid=answer_qid,
                        target_label=answer_label,
                        role="answer",
                    ),
                ],
                bridge_entities=[
                    build_bridge_entity(qid=office_qid, label=office_label, role="office"),
                    build_bridge_entity(qid=statement_qid, label="office-holder tenure", role="role_statement"),
                ],
                derivation_signature={
                    "style": "multi_hop_ordinal",
                    "rule": "ordinal_associated_office_holder_history_answer",
                    "ordinal_value": ordinal_value,
                    "ordinal_rendered": ordinal_rendered,
                    "office_qid": office_qid,
                    "office_label_terms": list(office_label_terms),
                },
                provenance_complete=True,
                subject_resource_url=subject_resource_url,
                subject_resource_key=subject_resource_key,
                source_metadata={
                    "wikidata_access_date": settings.run_date,
                    "retrieval_method": "WDQS office-holder seed + batched WDQS office history query",
                    "sparql_query": "office-first seed + batched office-holder history query",
                    "question_format_args": {
                        "descriptor": descriptor,
                        "ordinal": ordinal_rendered,
                    },
                    "ordinal_metadata": {
                        "ordinal_value": ordinal_value,
                        "ordinal_rendered": ordinal_rendered,
                        "descriptor": descriptor,
                        "subject_qid": subject_qid,
                        "office_qid": office_qid,
                        "office_label_raw": office_label,
                        "answer_qid": answer_qid,
                        "start_value": start_value,
                        "series_history_complete": history_complete,
                    },
                    "time_invariance": {
                        "historically_settled": True,
                        "history_complete": history_complete,
                        "allowed_property_pids": ["P39"],
                        "reason": "historical_office_holder_sequence",
                    },
                    "multi_hop_unique": True,
                    "required_reasoning_clues": [ordinal_rendered],
                },
            )
        )
        if len(candidates) >= settings.harvest_limit_per_template:
            break
    return candidates


def _ordinal_for_associated_office_holder_series(
    client: WikidataClient,
    *,
    subject_qid: str,
    office_qid: str,
    answer_qid: str,
    start_value: str,
    office_label_terms: tuple[str, ...],
    office_association_property_pids: tuple[str, ...],
    statement_association_qualifier_pids: tuple[str, ...],
    direct_subject_office: bool,
) -> tuple[int | None, bool]:
    """Return the ordinal of one dated office-holder statement for a subject-linked office."""
    association_block = _office_subject_association_block(
        subject_var=f"wd:{subject_qid}",
        office_var="?office",
        statement_var="?stmt",
        office_association_property_pids=office_association_property_pids,
        statement_association_qualifier_pids=statement_association_qualifier_pids,
        direct_subject_office=direct_subject_office,
    )
    label_filter = _office_label_filter(office_var="?office", office_label_terms=office_label_terms)
    query = f"""
SELECT ?answer ?start WHERE {{
  BIND(wd:{subject_qid} AS ?subject)
  ?answer p:P39 ?stmt.
  ?stmt ps:P39 ?office;
        pq:P580 ?start.
  FILTER(?office = wd:{office_qid})
  {association_block}
  {label_filter}
}}
""".strip()
    rows = client.sparql_query(query)
    dated_roles = [(_qid(row["answer"]["value"]), row["start"]["value"][:10]) for row in rows]
    if not dated_roles:
        return None, False
    sorted_roles = sorted(dated_roles, key=lambda item: (item[1], item[0]))
    ordinal_lookup: dict[tuple[str, str], int] = {}
    seen_pairs: set[tuple[str, str]] = set()
    for pair in sorted_roles:
        if pair in seen_pairs:
            continue
        seen_pairs.add(pair)
        ordinal_lookup[pair] = len(ordinal_lookup) + 1
    return ordinal_lookup.get((answer_qid, start_value)), True


def _load_subject_office_pairs(
    client: WikidataClient,
    *,
    subject_type_qid: str,
    office_label_terms: tuple[str, ...],
    office_association_property_pids: tuple[str, ...],
    direct_subject_office: bool,
) -> list[tuple[str, str]]:
    """Load candidate `(subject_qid, office_qid)` pairs before holder expansion."""
    if direct_subject_office:
        query = f"""
SELECT ?subject WHERE {{
  ?subject wdt:P31/wdt:P279* wd:{subject_type_qid}.
}}
LIMIT 50
""".strip()
        rows = client.sparql_query(query)
        return [(_qid(row["subject"]["value"]), _qid(row["subject"]["value"])) for row in rows]

    association_clauses = " UNION ".join(
        f"{{ ?office wdt:{pid} ?subject. }}" for pid in office_association_property_pids
    )
    label_filter = _office_label_filter(office_var="?office", office_label_terms=office_label_terms)
    query = f"""
SELECT ?subject ?office WHERE {{
  ?subject wdt:P31/wdt:P279* wd:{subject_type_qid}.
  {association_clauses}
  {label_filter}
}}
LIMIT 50
""".strip()
    rows = client.sparql_query(query)
    pairs: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for row in rows:
        pair = (_qid(row["subject"]["value"]), _qid(row["office"]["value"]))
        if pair in seen:
            continue
        seen.add(pair)
        pairs.append(pair)
    return pairs


def _load_recent_office_holder_rows(
    client: WikidataClient,
    *,
    subject_office_pairs: list[tuple[str, str]],
    target_start_date: str,
    date_upper_bound: str,
    limit: int,
    problem_domain: str | None = None,
) -> list[dict[str, Any]]:
    """Load recent dated holders for a fixed set of subject-office pairs."""
    if not subject_office_pairs:
        return []
    collected_rows: list[dict[str, Any]] = []
    chunk_limit = max(3, min(10, limit))
    per_chunk_limit = max(limit, chunk_limit)
    for pair_chunk in _chunked(subject_office_pairs, chunk_limit):
        values = " ".join(f"(wd:{subject_qid} wd:{office_qid})" for subject_qid, office_qid in pair_chunk)
        query = f"""
SELECT ?subject ?office ?answer ?start WHERE {{
  VALUES (?subject ?office) {{ {values} }}
  ?answer p:P39 ?stmt.
  ?stmt ps:P39 ?office;
        pq:P580 ?start.
  FILTER(?start >= "{target_start_date}T00:00:00Z"^^xsd:dateTime)
  FILTER(?start <= "{date_upper_bound}T23:59:59Z"^^xsd:dateTime)
}}
ORDER BY ?start ?subject
LIMIT {per_chunk_limit}
""".strip()
        try:
            rows = client.sparql_query(query)
        except Exception as exc:  # pragma: no cover - exercised in live runs
            client.record_problem(
                "chunked_office_holder_lookup_failed",
                "A later office-holder chunk failed; continuing with partial results.",
                domain=problem_domain,
                chunk_size=len(pair_chunk),
                collected_rows=len(collected_rows),
                error_type=type(exc).__name__,
                error_message=str(exc),
            )
            break
        collected_rows.extend(_normalize_subject_office_rows(rows, pair_chunk))
        if len(collected_rows) >= limit:
            break
    collected_rows.sort(
        key=lambda row: (
            row["start"]["value"],
            row["subject"]["value"],
            row["office"]["value"],
            row["answer"]["value"],
        )
    )
    return collected_rows[:limit]


def _load_subject_role_history_map(
    client: WikidataClient,
    *,
    subject_qids: list[str],
    role_property_pid: str,
) -> dict[str, list[tuple[str, str]]]:
    """Load dated role histories for many subjects in one WDQS query."""
    if not subject_qids:
        return {}
    values = " ".join(f"wd:{qid}" for qid in subject_qids)
    query = f"""
SELECT ?subject ?answer ?start WHERE {{
  VALUES ?subject {{ {values} }}
  ?subject p:{role_property_pid} ?stmt.
  ?stmt ps:{role_property_pid} ?answer;
        pq:P580 ?start.
}}
""".strip()
    rows = client.sparql_query(query)
    histories: dict[str, list[tuple[str, str]]] = {}
    default_subject_qid = subject_qids[0] if len(subject_qids) == 1 else ""
    for row in rows:
        subject_qid = _qid(row["subject"]["value"]) if "subject" in row else default_subject_qid
        if not subject_qid:
            continue
        histories.setdefault(subject_qid, []).append(
            (_qid(row["answer"]["value"]), row["start"]["value"][:10])
        )
    return histories


def _load_office_holder_history_map(
    client: WikidataClient,
    *,
    office_qids: list[str],
    problem_domain: str | None = None,
) -> dict[str, list[tuple[str, str]]]:
    """Load dated office-holder histories for many offices in one WDQS query."""
    if not office_qids:
        return {}
    histories: dict[str, list[tuple[str, str]]] = {}
    for office_chunk in _chunked(office_qids, 10):
        values = " ".join(f"wd:{qid}" for qid in office_chunk)
        query = f"""
SELECT ?office ?answer ?start WHERE {{
  VALUES ?office {{ {values} }}
  ?answer p:P39 ?stmt.
  ?stmt ps:P39 ?office;
        pq:P580 ?start.
}}
""".strip()
        try:
            rows = client.sparql_query(query)
        except Exception as exc:  # pragma: no cover - exercised in live runs
            client.record_problem(
                "chunked_office_history_lookup_failed",
                "A later office-history chunk failed; continuing with partial histories.",
                domain=problem_domain,
                chunk_size=len(office_chunk),
                loaded_offices=len(histories),
                error_type=type(exc).__name__,
                error_message=str(exc),
            )
            break
        default_office_qid = office_chunk[0] if len(office_chunk) == 1 else ""
        for row in rows:
            office_qid = _qid(row["office"]["value"]) if "office" in row else default_office_qid
            if not office_qid:
                continue
            histories.setdefault(office_qid, []).append(
                (_qid(row["answer"]["value"]), row["start"]["value"][:10])
            )
    return histories


def _ordinal_from_dated_pairs(
    dated_pairs: list[tuple[str, str]],
    *,
    target_qid: str,
    target_date: str,
) -> tuple[int | None, bool]:
    """Return an ordinal lookup from preloaded dated `(qid, date)` pairs."""
    if not dated_pairs:
        return None, False
    sorted_pairs = sorted(dated_pairs, key=lambda item: (item[1], item[0]))
    ordinal_lookup: dict[tuple[str, str], int] = {}
    seen_pairs: set[tuple[str, str]] = set()
    for pair in sorted_pairs:
        if pair in seen_pairs:
            continue
        seen_pairs.add(pair)
        ordinal_lookup[pair] = len(ordinal_lookup) + 1
    return ordinal_lookup.get((target_qid, target_date)), True


def _office_subject_association_block(
    *,
    subject_var: str,
    office_var: str,
    statement_var: str,
    office_association_property_pids: tuple[str, ...],
    statement_association_qualifier_pids: tuple[str, ...],
    direct_subject_office: bool,
) -> str:
    """Return a SPARQL block linking an office-holder statement back to the subject entity."""
    if direct_subject_office:
        return f"FILTER({office_var} = {subject_var})"
    clauses: list[str] = []
    for pid in office_association_property_pids:
        clauses.append(f"{{ {office_var} wdt:{pid} {subject_var}. }}")
    for pid in statement_association_qualifier_pids:
        clauses.append(f"{{ {statement_var} pq:{pid} {subject_var}. }}")
    if not clauses:
        return ""
    return "{\n    " + "\n    UNION\n    ".join(clauses) + "\n  }"


def _office_label_filter(*, office_var: str, office_label_terms: tuple[str, ...]) -> str:
    """Return a SPARQL filter that restricts office labels to the expected title family."""
    if not office_label_terms:
        return ""
    filter_checks = " || ".join(
        f'CONTAINS(LCASE(STR(?officeLabel)), "{term.lower()}")'
        for term in office_label_terms
    )
    return (
        f"{office_var} rdfs:label ?officeLabel.\n"
        f'  FILTER(LANG(?officeLabel) = "en")\n'
        f"  FILTER({filter_checks})"
    )


def _office_label_matches(office_label: str, office_label_terms: tuple[str, ...]) -> bool:
    """Return whether one office label matches the expected title family."""
    normalized = office_label.lower()
    return any(term.lower() in normalized for term in office_label_terms)


def _harvest_acquisition_purchase_price(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
) -> list[CandidateFact]:
    """Harvest acquisition-price candidates from qualified ownership statements."""
    seed_rows, seed_query = _load_recent_acquisition_seed_rows(
        client,
        target_start_date=settings.target_start_date,
        date_upper_bound=settings.date_upper_bound,
        limit=max(settings.harvest_limit_per_template * 6, settings.harvest_limit_per_template),
        problem_domain=template.domain,
    )
    raw_rows = _load_acquisition_price_rows(
        client,
        seed_rows=seed_rows,
        limit=max(settings.harvest_limit_per_template * 5, settings.harvest_limit_per_template),
        problem_domain=template.domain,
    )
    rows = _filter_unique_acquisition_price_rows(raw_rows)
    entity_qids: set[str] = set()
    for row in rows:
        entity_qids.add(_qid(row["target"]["value"]))
        entity_qids.add(_qid(row["acquirer"]["value"]))
    entities = client.get_entities(sorted(entity_qids)) if entity_qids else {}
    candidates: list[CandidateFact] = []
    for row in rows:
        target_qid = _qid(row["target"]["value"])
        acquirer_qid = _qid(row["acquirer"]["value"])
        target_label = _label(entities.get(target_qid, {}))
        acquirer_label = _label(entities.get(acquirer_qid, {}))
        if not target_label or not acquirer_label:
            continue
        price_label = _normalize_numeric_label(row.get("priceAmount", {}).get("value", ""))
        if price_label is None:
            continue
        start_value = row["start"]["value"][:10]
        subject_resource_url, subject_resource_key = canonical_subject_resource(
            target_qid,
            entities.get(target_qid, {}),
        )
        candidates.append(
            CandidateFact(
                subject_qid=target_qid,
                subject_label=target_label,
                subject_aliases=_aliases(entities.get(target_qid, {})),
                domain=template.domain,
                topic=template.topic,
                answer_type=template.answer_type,
                question_family=template.question_family,
                subject_type_qids=[template.subject_type_qid],
                target_property_pid=template.target_property_pid,
                target_property_label=template.target_property_label,
                answer_qids=[f"VALUE:number:{price_label}"],
                answer_labels=[price_label],
                answer_aliases=[],
                date_property_pid="P580",
                date_value=start_value,
                target_time=settings.target_time,
                canonical_question="",
                newness_metadata={
                    "anchor_kind": "statement_qualifier",
                    "anchor_property_pid": "P580",
                    "anchor_value": start_value,
                    "reason": "ownership_change_start_time_not_earlier_than_target_time",
                    "what_is_new": "the acquisition event",
                },
                reasoning_style="multi_hop_join",
                hop_count=2,
                reasoning_path=[
                    build_reasoning_hop(
                        source_qid=target_qid,
                        source_label=target_label,
                        property_pid="P127",
                        property_label="owned by",
                        target_qid=acquirer_qid,
                        target_label=acquirer_label,
                        role="bridge",
                        qualifiers={"P580": start_value, "P2130": price_label},
                    ),
                    build_reasoning_hop(
                        source_qid=acquirer_qid,
                        source_label=acquirer_label,
                        property_pid="DERIVED_ACQUISITION_PRICE",
                        property_label="acquisition price",
                        target_qid=f"VALUE:number:{price_label}",
                        target_label=price_label,
                        role="answer",
                    ),
                ],
                bridge_entities=[
                    build_bridge_entity(qid=acquirer_qid, label=acquirer_label, role="acquirer"),
                ],
                derivation_signature={
                    "style": "multi_hop_join",
                    "rule": "qualified_owned_by_acquisition_price",
                    "currency_qid": "Q4917",
                },
                provenance_complete=True,
                subject_resource_url=subject_resource_url,
                subject_resource_key=subject_resource_key,
                source_metadata={
                    "wikidata_access_date": settings.run_date,
                    "retrieval_method": "WDQS acquisition statement seed + batched price lookup",
                    "sparql_query": seed_query,
                    "question_format_args": {
                        "descriptor": target_label,
                        "acquirer_label": acquirer_label,
                    },
                    "time_invariance": {
                        "historically_settled": True,
                        "history_complete": True,
                        "allowed_property_pids": ["P2130"],
                        "reason": "completed_acquisition_price_statement",
                    },
                    "multi_hop_unique": True,
                    "required_reasoning_clues": ["acquire"],
                },
            )
        )
        if len(candidates) >= settings.harvest_limit_per_template:
            break
    return candidates


def _collect_series_history_requests(rows: list[dict[str, Any]]) -> list[tuple[str, str, str]]:
    """Return unique `(series_qid, series_property_pid, date_property_pid)` keys."""
    seen: set[tuple[str, str, str]] = set()
    ordered: list[tuple[str, str, str]] = []
    for row in rows:
        key = (
            _qid(row["series"]["value"]),
            row.get("seriesPropertyPid", {}).get("value", "P179"),
            row.get("datePropertyPid", {}).get("value", "P585"),
        )
        if key in seen:
            continue
        seen.add(key)
        ordered.append(key)
    return ordered


def _load_series_edition_history_map(
    client: WikidataClient,
    *,
    requests: list[tuple[str, str, str]],
) -> dict[tuple[str, str, str], list[tuple[str, str]]]:
    """Load dated edition histories grouped by `(series, series-pid, date-pid)`."""
    history_map: dict[tuple[str, str, str], list[tuple[str, str]]] = {}
    for series_qid, series_property_pid, date_property_pid in requests:
        query = f"""
SELECT ?edition ?date WHERE {{
  ?edition wdt:{series_property_pid} wd:{series_qid};
           wdt:{date_property_pid} ?date.
}}
""".strip()
        rows = client.sparql_query(query)
        history_map[(series_qid, series_property_pid, date_property_pid)] = [
            (_qid(row["edition"]["value"]), row["date"]["value"][:10])
            for row in rows
        ]
    return history_map


def _ordinal_from_series_history_map(
    history_map: dict[tuple[str, str, str], list[tuple[str, str]]],
    *,
    series_qid: str,
    edition_qid: str,
    series_property_pid: str,
    date_property_pid: str,
) -> tuple[int | None, bool]:
    """Return one edition ordinal from a preloaded series-history map."""
    dated_editions = history_map.get((series_qid, series_property_pid, date_property_pid), [])
    if not dated_editions:
        return None, False
    sorted_editions = sorted(dated_editions, key=lambda item: (item[1], item[0]))
    ordinal_lookup = {qid: index for index, (qid, _) in enumerate(sorted_editions, start=1)}
    return ordinal_lookup.get(edition_qid), True


def _harvest_footballer_goals_in_ordinal_tournament(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
) -> list[CandidateFact]:
    """Harvest settled tournament-goal totals tied to completed tournament editions."""
    edition_seed_rows, edition_seed_query = _load_recent_tournament_edition_rows(
        client,
        target_start_date=settings.target_start_date,
        date_upper_bound=settings.date_upper_bound,
        limit=max(settings.harvest_limit_per_template * 6, settings.harvest_limit_per_template),
        problem_domain=template.domain,
    )
    raw_rows = _load_player_goal_rows_for_editions(
        client,
        edition_rows=edition_seed_rows,
        subject_type_qid=template.subject_type_qid,
        limit=max(settings.harvest_limit_per_template * 12, settings.harvest_limit_per_template),
        problem_domain=template.domain,
    )
    rows = _filter_unique_player_edition_goal_rows(raw_rows)
    entity_qids: set[str] = set()
    for row in rows:
        entity_qids.add(_qid(row["player"]["value"]))
        entity_qids.add(_qid(row["edition"]["value"]))
        entity_qids.add(_qid(row["series"]["value"]))
    entities = client.get_entities(sorted(entity_qids)) if entity_qids else {}
    edition_history_map = _load_series_edition_history_map(
        client=client,
        requests=_collect_series_history_requests(rows),
    )
    candidates: list[CandidateFact] = []
    for row in rows:
        player_qid = _qid(row["player"]["value"])
        edition_qid = _qid(row["edition"]["value"])
        series_qid = _qid(row["series"]["value"])
        player_label = _label(entities.get(player_qid, {}))
        series_label = _label(entities.get(series_qid, {}))
        edition_label = _label(entities.get(edition_qid, {}))
        if not player_label or not series_label or not edition_label:
            continue
        descriptor = _strip_year_tokens(series_label)
        if not descriptor:
            continue
        goals_value = _parse_count_binding(row.get("goals", {}).get("value", ""))
        if goals_value is None:
            continue
        date_value = row["date"]["value"][:10]
        series_property_pid = row.get("seriesPropertyPid", {}).get("value", "P179")
        date_property_pid = row.get("datePropertyPid", {}).get("value", template.date_property_pid)
        ordinal_value, history_complete = _ordinal_from_series_history_map(
            edition_history_map,
            series_qid=series_qid,
            edition_qid=edition_qid,
            series_property_pid=series_property_pid,
            date_property_pid=date_property_pid,
        )
        if ordinal_value is None:
            continue
        ordinal_rendered = _render_ordinal(ordinal_value)
        statement_qid = f"STATEMENT:{player_qid}:P1344:{edition_qid}"
        subject_resource_url, subject_resource_key = canonical_subject_resource(
            player_qid,
            entities.get(player_qid, {}),
        )
        candidates.append(
            CandidateFact(
                subject_qid=player_qid,
                subject_label=player_label,
                subject_aliases=_aliases(entities.get(player_qid, {})),
                domain=template.domain,
                topic=template.topic,
                answer_type=template.answer_type,
                question_family=template.question_family,
                subject_type_qids=[template.subject_type_qid],
                target_property_pid=template.target_property_pid,
                target_property_label=template.target_property_label,
                answer_qids=[f"VALUE:number:{goals_value}"],
                answer_labels=[str(goals_value)],
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
                hop_count=3,
                reasoning_path=[
                    build_reasoning_hop(
                        source_qid=player_qid,
                        source_label=player_label,
                        property_pid="P1344",
                        property_label="participant in",
                        target_qid=statement_qid,
                        target_label="tournament participation statement",
                        role="bridge",
                        qualifiers={"edition_qid": edition_qid, "P1351": str(goals_value)},
                    ),
                    build_reasoning_hop(
                        source_qid=statement_qid,
                        source_label="tournament participation statement",
                        property_pid="DERIVED_PARTICIPATION_EDITION",
                        property_label="tournament edition",
                        target_qid=edition_qid,
                        target_label=edition_label,
                        role="bridge",
                    ),
                    build_reasoning_hop(
                        source_qid=edition_qid,
                        source_label=edition_label,
                        property_pid="P1351",
                        property_label="number of points/goals/set scored",
                        target_qid=f"VALUE:number:{goals_value}",
                        target_label=str(goals_value),
                        role="answer",
                    ),
                ],
                bridge_entities=[
                    build_bridge_entity(qid=statement_qid, label="tournament participation statement", role="participation_statement"),
                    build_bridge_entity(qid=edition_qid, label=edition_label, role="edition"),
                ],
                derivation_signature={
                    "style": "multi_hop_ordinal",
                    "rule": "player_goals_in_ordinal_tournament_edition",
                    "ordinal_value": ordinal_value,
                    "ordinal_rendered": ordinal_rendered,
                    "series_property_pid": series_property_pid,
                    "date_property_pid": date_property_pid,
                    "count_property_pid": "P1351",
                },
                provenance_complete=True,
                subject_resource_url=subject_resource_url,
                subject_resource_key=subject_resource_key,
                source_metadata={
                    "wikidata_access_date": settings.run_date,
                    "retrieval_method": "WDQS edition seed + player-goal lookup + batched WDQS ordinal history query",
                    "sparql_query": edition_seed_query,
                    "question_format_args": {
                        "player_label": player_label,
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
                    "time_invariance": {
                        "historically_settled": True,
                        "history_complete": history_complete,
                        "allowed_property_pids": ["P1351"],
                        "reason": "completed_tournament_stat_slice",
                    },
                    "multi_hop_unique": True,
                    "required_reasoning_clues": ["goals", "edition", ordinal_rendered],
                },
            )
        )
        if len(candidates) >= settings.harvest_limit_per_template:
            break
    return candidates


def _filter_unique_player_edition_goal_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep only player-edition rows with one unique goal total."""
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        key = (_qid(row["player"]["value"]), _qid(row["edition"]["value"]))
        grouped.setdefault(key, []).append(row)
    filtered: list[dict[str, Any]] = []
    for grouped_rows in grouped.values():
        goals = {row.get("goals", {}).get("value", "") for row in grouped_rows}
        if len(goals) == 1:
            filtered.append(grouped_rows[0])
    return filtered


def _filter_unique_acquisition_price_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep only acquisition rows with one unique price per target/acquirer/start."""
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        key = (
            _qid(row["target"]["value"]),
            _qid(row["acquirer"]["value"]),
            row["start"]["value"][:10],
        )
        grouped.setdefault(key, []).append(row)
    filtered: list[dict[str, Any]] = []
    for grouped_rows in grouped.values():
        prices = {row.get("priceAmount", {}).get("value", "") for row in grouped_rows}
        if len(prices) == 1:
            filtered.append(grouped_rows[0])
    return filtered


def _normalize_subject_office_rows(
    rows: list[dict[str, Any]],
    subject_office_pairs: list[tuple[str, str]],
) -> list[dict[str, Any]]:
    """Fill subject/office bindings when one `(subject, office)` pair was queried."""
    if len(subject_office_pairs) != 1:
        return rows
    subject_qid, office_qid = subject_office_pairs[0]
    normalized_rows: list[dict[str, Any]] = []
    for row in rows:
        normalized = dict(row)
        if "subject" not in normalized:
            normalized["subject"] = {"value": f"http://www.wikidata.org/entity/{subject_qid}"}
        if "office" not in normalized:
            normalized["office"] = {"value": f"http://www.wikidata.org/entity/{office_qid}"}
        normalized_rows.append(normalized)
    return normalized_rows


def _load_acquisition_price_rows(
    client: WikidataClient,
    *,
    seed_rows: list[dict[str, Any]],
    limit: int,
    problem_domain: str | None = None,
) -> list[dict[str, Any]]:
    """Load acquisition prices for a bounded set of ownership statements."""
    if not seed_rows:
        return []
    statement_map: dict[str, dict[str, Any]] = {}
    for row in seed_rows:
        statement_map[row["stmt"]["value"]] = row
    collected_rows: list[dict[str, Any]] = []
    for statement_chunk in _chunked(list(statement_map), 8):
        values = " ".join(f"<{stmt_uri}>" for stmt_uri in statement_chunk)
        query = f"""
SELECT ?stmt ?priceAmount WHERE {{
  VALUES ?stmt {{ {values} }}
  ?stmt pqv:P2130 ?priceNode.
  ?priceNode wikibase:quantityAmount ?priceAmount;
             wikibase:quantityUnit wd:Q4917.
}}
""".strip()
        try:
            rows = client.sparql_query(query)
        except Exception as exc:  # pragma: no cover - exercised in live runs
            client.record_problem(
                "chunked_acquisition_price_lookup_failed",
                "A later acquisition-price chunk failed; continuing with partial results.",
                domain=problem_domain,
                chunk_size=len(statement_chunk),
                collected_rows=len(collected_rows),
                error_type=type(exc).__name__,
                error_message=str(exc),
            )
            break
        for row in rows:
            statement_row = statement_map.get(row["stmt"]["value"])
            if statement_row is None:
                continue
            collected_rows.append(
                {
                    "target": statement_row["target"],
                    "acquirer": statement_row["acquirer"],
                    "start": statement_row["start"],
                    "priceAmount": row["priceAmount"],
                }
            )
        if len(collected_rows) >= limit:
            break
    return collected_rows[:limit]


def _load_player_goal_rows_for_editions(
    client: WikidataClient,
    *,
    edition_rows: list[dict[str, Any]],
    subject_type_qid: str,
    limit: int,
    problem_domain: str | None = None,
) -> list[dict[str, Any]]:
    """Load player-goal rows for a bounded set of recent tournament editions."""
    if not edition_rows:
        return []
    edition_map: dict[str, dict[str, Any]] = {}
    for row in edition_rows:
        edition_qid = _qid(row["edition"]["value"])
        edition_map[edition_qid] = row
    collected_rows: list[dict[str, Any]] = []
    for edition_chunk in _chunked(list(edition_map), 5):
        values = " ".join(f"wd:{edition_qid}" for edition_qid in edition_chunk)
        query = f"""
SELECT ?player ?edition ?goals WHERE {{
  VALUES ?edition {{ {values} }}
  ?player wdt:P31/wdt:P279* wd:{subject_type_qid};
          p:P1344 ?stmt.
  ?stmt ps:P1344 ?edition;
        pq:P1351 ?goals.
}}
ORDER BY ?edition ?player
LIMIT {max(limit, 100)}
""".strip()
        try:
            rows = client.sparql_query(query)
        except Exception as exc:  # pragma: no cover - exercised in live runs
            client.record_problem(
                "chunked_player_goal_lookup_failed",
                "A later player-goal chunk failed; continuing with partial results.",
                domain=problem_domain,
                chunk_size=len(edition_chunk),
                collected_rows=len(collected_rows),
                error_type=type(exc).__name__,
                error_message=str(exc),
            )
            break
        for row in rows:
            edition_qid = _qid(row["edition"]["value"])
            edition_row = edition_map.get(edition_qid)
            if edition_row is None:
                continue
            collected_rows.append(
                {
                    "player": row["player"],
                    "edition": row["edition"],
                    "series": edition_row["series"],
                    "date": edition_row["date"],
                    "goals": row["goals"],
                    "seriesPropertyPid": edition_row["seriesPropertyPid"],
                    "datePropertyPid": edition_row["datePropertyPid"],
                }
            )
        if len(collected_rows) >= limit:
            break
    return collected_rows[:limit]


def _chunked(values: list[Any], size: int) -> list[list[Any]]:
    """Return `values` split into chunks with at most `size` items."""
    if size <= 0:
        raise ValueError("chunk size must be positive")
    return [values[index : index + size] for index in range(0, len(values), size)]


def _load_recent_tournament_edition_rows(
    client: WikidataClient,
    *,
    target_start_date: str,
    date_upper_bound: str,
    limit: int,
    problem_domain: str | None = None,
) -> tuple[list[dict[str, Any]], str]:
    """Load recent tournament editions via smaller time-windowed queries."""
    query_templates = [
        """
SELECT ?edition ?series ?date ?seriesPropertyPid ?datePropertyPid WHERE {{
  ?edition wdt:P179 ?series;
           wdt:P585 ?date.
  FILTER(?date >= "{window_start}T00:00:00Z"^^xsd:dateTime)
  FILTER(?date <= "{window_end}T23:59:59Z"^^xsd:dateTime)
  BIND("P179" AS ?seriesPropertyPid)
  BIND("P585" AS ?datePropertyPid)
}}
ORDER BY ?date ?edition
LIMIT {window_limit}
""".strip(),
        """
SELECT ?edition ?series ?date ?seriesPropertyPid ?datePropertyPid WHERE {{
  ?edition wdt:P3450 ?series.
  OPTIONAL {{ ?edition wdt:P582 ?seasonEnd }}
  OPTIONAL {{ ?edition wdt:P580 ?seasonStart }}
  BIND(COALESCE(?seasonEnd, ?seasonStart) AS ?date)
  FILTER(BOUND(?date))
  FILTER(?date >= "{window_start}T00:00:00Z"^^xsd:dateTime)
  FILTER(?date <= "{window_end}T23:59:59Z"^^xsd:dateTime)
  BIND("P3450" AS ?seriesPropertyPid)
  BIND(IF(BOUND(?seasonEnd), "P582", "P580") AS ?datePropertyPid)
}}
ORDER BY ?date ?edition
LIMIT {window_limit}
""".strip(),
    ]
    rows: list[dict[str, Any]] = []
    seen_editions: set[tuple[str, str, str]] = set()
    first_query_text = ""
    window_limit = max(limit, 12)
    for window_start, window_end in _monthly_windows(target_start_date, date_upper_bound):
        for query_template in query_templates:
            query = query_template.format(
                window_start=window_start,
                window_end=window_end,
                window_limit=window_limit,
            )
            if not first_query_text:
                first_query_text = query
            try:
                query_rows = client.sparql_query(query)
            except Exception as exc:  # pragma: no cover - exercised in live runs
                client.record_problem(
                    "time_windowed_tournament_seed_failed",
                    "A tournament-edition seed window failed; continuing with other windows.",
                    domain=problem_domain,
                    window_start=window_start,
                    window_end=window_end,
                    error_type=type(exc).__name__,
                    error_message=str(exc),
                )
                continue
            for row in query_rows:
                key = (
                    _qid(row["edition"]["value"]),
                    row.get("seriesPropertyPid", {}).get("value", "P179"),
                    row.get("datePropertyPid", {}).get("value", "P585"),
                )
                if key in seen_editions:
                    continue
                seen_editions.add(key)
                rows.append(row)
            if rows:
                return rows[:limit], first_query_text
    return rows[:limit], first_query_text


def _load_recent_acquisition_seed_rows(
    client: WikidataClient,
    *,
    target_start_date: str,
    date_upper_bound: str,
    limit: int,
    problem_domain: str | None = None,
) -> tuple[list[dict[str, Any]], str]:
    """Load recent acquisition statement seeds via smaller time-windowed queries."""
    rows: list[dict[str, Any]] = []
    seen_statements: set[str] = set()
    first_query_text = ""
    window_limit = max(limit, 12)
    query_template = """
SELECT ?stmt ?target ?acquirer ?start WHERE {{
  ?target p:P127 ?stmt.
  ?stmt ps:P127 ?acquirer;
        pq:P580 ?start;
        pq:P2130 ?priceLiteral.
  FILTER(?start >= "{window_start}T00:00:00Z"^^xsd:dateTime)
  FILTER(?start <= "{window_end}T23:59:59Z"^^xsd:dateTime)
}}
ORDER BY ?start ?target
LIMIT {window_limit}
""".strip()
    for window_start, window_end in _monthly_windows(target_start_date, date_upper_bound):
        query = query_template.format(
            window_start=window_start,
            window_end=window_end,
            window_limit=window_limit,
        )
        if not first_query_text:
            first_query_text = query
        try:
            query_rows = client.sparql_query(query)
        except Exception as exc:  # pragma: no cover - exercised in live runs
            client.record_problem(
                "time_windowed_acquisition_seed_failed",
                "An acquisition seed window failed; continuing with other windows.",
                domain=problem_domain,
                window_start=window_start,
                window_end=window_end,
                error_type=type(exc).__name__,
                error_message=str(exc),
            )
            continue
        for row in query_rows:
            statement_uri = row["stmt"]["value"]
            if statement_uri in seen_statements:
                continue
            seen_statements.add(statement_uri)
            rows.append(row)
        if rows:
            return rows[:limit], first_query_text
    return rows[:limit], first_query_text


def _monthly_windows(start_date: str, end_date: str) -> list[tuple[str, str]]:
    """Return inclusive month windows covering one ISO date range."""
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    windows: list[tuple[str, str]] = []
    year = start.year
    month = start.month
    while (year, month) <= (end.year, end.month):
        window_start = start if (year, month) == (start.year, start.month) else date(year, month, 1)
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)
        window_end = min(end, date.fromordinal(next_month.toordinal() - 1))
        windows.append((window_start.isoformat(), window_end.isoformat()))
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
    return windows


def _qid(uri: str) -> str:
    return uri.rsplit("/", 1)[-1]


def _generic_count_candidates(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
) -> list[CandidateFact]:
    """Build count-style candidates for generic fixed-structure templates."""
    if template.answer_format != "number":
        return []
    if template.target_property_pid.startswith("COMPOSED_"):
        return []

    query = build_count_candidate_query(
        template=template,
        target_start_date=settings.target_start_date,
        date_upper_bound=settings.date_upper_bound,
        limit=min(settings.harvest_limit_per_template, template.retrieval_limit),
    )
    rows = client.sparql_query(query)
    if not rows:
        return []

    client.record_problem(
        "generic_count_fallback_used",
        "Used the generic count fallback because no domain-specific executor returned candidates.",
        domain=template.domain,
        target_property_pid=template.target_property_pid,
    )

    qids = sorted({_qid(row["item"]["value"]) for row in rows})
    entities = client.get_entities(qids) if qids else {}
    candidates: list[CandidateFact] = []
    for row in rows:
        subject_qid = _qid(row["item"]["value"])
        subject_entity = entities.get(subject_qid, {})
        subject_label, subject_label_source = _select_controlled_label(
            subject_entity,
            row.get("itemLabel", {}).get("value"),
        )
        if not subject_label:
            continue
        count_value = _parse_count_binding(row.get("answerCount", {}).get("value", ""))
        if count_value is None:
            continue
        date_value = normalize_wikidata_date_literal(row["date"]["value"])
        subject_resource_url, subject_resource_key = canonical_subject_resource(
            subject_qid,
            subject_entity,
        )
        candidates.append(
            CandidateFact(
                subject_qid=subject_qid,
                subject_label=subject_label,
                subject_aliases=[],
                domain=template.domain,
                topic=template.topic,
                answer_type=template.answer_type,
                question_family=template.question_family,
                subject_type_qids=[template.subject_type_qid],
                target_property_pid=template.target_property_pid,
                target_property_label=template.target_property_label,
                answer_qids=[f"VALUE:number:{count_value}"],
                answer_labels=[str(count_value)],
                answer_aliases=[],
                date_property_pid=template.date_property_pid,
                date_value=date_value,
                target_time=settings.target_time,
                canonical_question="",
                newness_metadata={
                    "anchor_kind": "subject_date_property",
                    "anchor_property_pid": template.date_property_pid,
                    "anchor_value": date_value,
                    "reason": "subject_or_event_date_not_earlier_than_target_time",
                },
                reasoning_style="single_fact",
                hop_count=1,
                reasoning_path=[
                    build_reasoning_hop(
                        source_qid=subject_qid,
                        source_label=subject_label,
                        property_pid=template.target_property_pid,
                        property_label=template.target_property_label,
                        target_qid=f"VALUE:number:{count_value}",
                        target_label=str(count_value),
                        role="answer",
                    )
                ],
                derivation_signature={
                    "style": "single_fact",
                    "rule": "generic_count_fallback",
                    "counted_property_pid": template.target_property_pid,
                },
                provenance_complete=True,
                subject_resource_url=subject_resource_url,
                subject_resource_key=subject_resource_key,
                source_metadata={
                    "wikidata_access_date": settings.run_date,
                    "retrieval_method": "WDQS generic count fallback",
                    "sparql_query": query,
                    "multi_hop_unique": True,
                    "question_format_args": {"descriptor": subject_label},
                    "subject_label_source": subject_label_source,
                },
            )
        )
    return candidates


def _generic_direct_candidates(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
) -> list[CandidateFact]:
    """Build direct single-hop candidates for join templates that need no custom logic."""
    if template.target_property_pid.startswith("COMPOSED_"):
        return []
    if template.answer_format == "number":
        return []

    query = build_candidate_query(
        template=template,
        target_start_date=settings.target_start_date,
        date_upper_bound=settings.date_upper_bound,
        limit=min(settings.harvest_limit_per_template, template.retrieval_limit),
    )
    rows = _filter_direct_unique_rows(client.sparql_query(query))
    if not rows:
        return []

    qids = _collect_direct_qids(rows)
    entities = client.get_entities(qids) if qids else {}
    related_qids = _collect_direct_related_qids(entities)
    related_entities = client.get_entities(sorted(related_qids)) if related_qids else {}
    candidates: list[CandidateFact] = []
    for row in rows:
        candidate = _direct_row_to_candidate(
            row=row,
            entities=entities,
            related_entities=related_entities,
            settings=settings,
            template=template,
            query=query,
        )
        if candidate is not None:
            candidates.append(candidate)
    return candidates


def _run_support_probe_if_possible(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
) -> None:
    """Run a lightweight seed query so unsupported templates still reach Wikidata."""
    if _has_heavy_query_problem(client, domain=template.domain):
        client.record_problem(
            "support_probe_skipped",
            "Skipped generic support probe because a prior heavy-query failure already explains the outcome.",
            domain=template.domain,
            target_property_pid=template.target_property_pid,
        )
        return
    if template.target_property_pid.startswith("COMPOSED_"):
        client.record_problem(
            "support_probe_skipped",
            "Skipped generic support probe because the template uses a synthetic composed property.",
            domain=template.domain,
            target_property_pid=template.target_property_pid,
        )
        return
    query = build_count_candidate_query(
        template=template,
        target_start_date=settings.target_start_date,
        date_upper_bound=settings.date_upper_bound,
        limit=1,
    )
    try:
        rows = client.sparql_query(query)
    except Exception as exc:  # noqa: BLE001
        client.record_problem(
            "support_probe_failed",
            "The generic support probe failed.",
            domain=template.domain,
            target_property_pid=template.target_property_pid,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        raise
    client.record_problem(
        "support_probe_completed",
        "Ran a generic support probe for a template without a domain-specific executor.",
        domain=template.domain,
        target_property_pid=template.target_property_pid,
        probe_result_count=len(rows),
    )


def _has_heavy_query_problem(client: WikidataClient, *, domain: str) -> bool:
    """Return whether the client already recorded a heavy-query failure for the domain."""
    recorded_problems = getattr(client, "recorded_problems", None)
    if recorded_problems is None:
        recorded_problems = getattr(client, "problem_reports", [])
    for problem in recorded_problems:
        if problem.get("kind") not in HEAVY_QUERY_PROBLEM_KINDS:
            continue
        context = problem.get("context", {})
        if context.get("domain") == domain:
            return True
    return False


def _parse_count_binding(value: str) -> int | None:
    """Parse an integer count value from a SPARQL aggregate binding."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _normalize_numeric_label(value: str) -> str | None:
    """Normalize a decimal-like binding to a compact human-readable number string."""
    text = str(value).strip()
    if not text:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    if number.is_integer():
        return str(int(number))
    return text.rstrip("0").rstrip(".")


def _label(entity: dict[str, Any]) -> str:
    return entity.get("labels", {}).get("en", {}).get("value", "")


def _aliases(entity: dict[str, Any]) -> list[str]:
    values = entity.get("aliases", {}).get("en", [])
    return [alias.get("value", "") for alias in values if alias.get("value")]


def _description(entity: dict[str, Any]) -> str:
    return entity.get("descriptions", {}).get("en", {}).get("value", "")


def _extract_controlled_label(entity: dict[str, Any], fallback: str | None) -> str:
    """Return a safe label, dropping raw QID-like placeholders."""
    label = _label(entity) or (fallback or "")
    if QID_LIKE_LABEL_PATTERN.fullmatch(label):
        return ""
    return label


def _select_controlled_label(
    entity: dict[str, Any],
    wdqs_fallback: str | None,
) -> tuple[str, str]:
    """Select a controlled label with source tracking for fallback harvesters."""
    hydrated = _extract_controlled_label(entity, None)
    if hydrated:
        return hydrated, "wbgetentities_en"
    fallback = _extract_controlled_label({}, wdqs_fallback)
    if fallback:
        return fallback, "wdqs_label_fallback"
    return "", "missing"


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


def _entity_qid(binding: dict[str, Any]) -> str | None:
    if binding.get("type") != "uri":
        return None
    value = binding.get("value", "")
    if "/entity/" not in value:
        return None
    return value.rsplit("/", 1)[-1]


def _collect_direct_qids(rows: list[dict[str, Any]]) -> list[str]:
    qids: set[str] = set()
    for row in rows:
        qids.add(_qid(row["item"]["value"]))
        answer_qid = _entity_qid(row["answer"])
        if answer_qid:
            qids.add(answer_qid)
    return sorted(qids)


def _collect_direct_related_qids(entities: dict[str, dict[str, Any]]) -> set[str]:
    related_qids: set[str] = set()
    for entity in entities.values():
        for pid in ("P31", "P279", "P131", "P17", "P276", "P150", "P921"):
            related_qids.update(_claim_qids(entity, pid))
    return related_qids


def _filter_direct_unique_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        key = (_qid(row["item"]["value"]), row["date"]["value"][:10])
        grouped.setdefault(key, []).append(row)
    filtered: list[dict[str, Any]] = []
    for grouped_rows in grouped.values():
        answer_qids = {_entity_qid(row["answer"]) or row["answer"].get("value", "") for row in grouped_rows}
        if len(answer_qids) == 1:
            filtered.append(grouped_rows[0])
    return filtered


def _entity_labels(entities: dict[str, dict[str, Any]], qids: list[str]) -> list[str]:
    labels: list[str] = []
    for qid in qids:
        label = _label(entities.get(qid, {}))
        if label:
            labels.append(label)
    return labels


def _direct_row_to_candidate(
    *,
    row: dict[str, Any],
    entities: dict[str, dict[str, Any]],
    related_entities: dict[str, dict[str, Any]],
    settings: Settings,
    template: DomainTemplate,
    query: str,
) -> CandidateFact | None:
    subject_qid = _qid(row["item"]["value"])
    answer_qid = _entity_qid(row["answer"])
    if answer_qid is None:
        return None
    subject_entity = entities.get(subject_qid, {})
    answer_entity = entities.get(answer_qid, {})
    subject_label = _label(subject_entity) or row.get("itemLabel", {}).get("value", "")
    answer_label = _label(answer_entity) or row.get("answerLabel", {}).get("value", "")
    if not subject_label or not answer_label:
        return None
    date_value = normalize_wikidata_date_literal(row["date"]["value"])
    subject_resource_url, subject_resource_key = canonical_subject_resource(subject_qid, subject_entity)
    subject_type_qids = _claim_qids(subject_entity, "P31")
    subject_type_labels = _entity_labels(related_entities, subject_type_qids)
    subject_main_subject_labels = _entity_labels(
        related_entities,
        _claim_qids(subject_entity, "P921"),
    )
    subject_location_labels = _entity_labels(
        related_entities,
        _claim_qids(subject_entity, "P131") + _claim_qids(subject_entity, "P276"),
    )
    answer_subdivision_labels = _entity_labels(
        related_entities,
        _claim_qids(answer_entity, "P150"),
    )
    return CandidateFact(
        subject_qid=subject_qid,
        subject_label=subject_label,
        subject_aliases=_aliases(subject_entity),
        domain=template.domain,
        topic=template.topic,
        answer_type=template.answer_type,
        question_family=template.question_family,
        subject_type_qids=subject_type_qids or [template.subject_type_qid],
        target_property_pid=template.target_property_pid,
        target_property_label=template.target_property_label,
        answer_qids=[answer_qid],
        answer_labels=[answer_label],
        answer_aliases=_aliases(answer_entity),
        date_property_pid=template.date_property_pid,
        date_value=date_value,
        target_time=settings.target_time,
        canonical_question="",
        newness_metadata={
            "anchor_kind": "subject_date_property",
            "anchor_property_pid": template.date_property_pid,
            "anchor_value": date_value,
            "reason": "subject_or_event_date_not_earlier_than_target_time",
        },
        reasoning_style="single_fact",
        hop_count=1,
        reasoning_path=[
            build_reasoning_hop(
                source_qid=subject_qid,
                source_label=subject_label,
                property_pid=template.target_property_pid,
                property_label=template.target_property_label,
                target_qid=answer_qid,
                target_label=answer_label,
                role="answer",
            )
        ],
        derivation_signature={
            "style": "single_fact",
            "rule": "composed_template_direct_lookup",
        },
        provenance_complete=True,
        subject_resource_url=subject_resource_url,
        subject_resource_key=subject_resource_key,
        source_metadata={
            "wikidata_access_date": settings.run_date,
            "retrieval_method": "WDQS direct lookup for composed template",
            "sparql_query": query,
            "subject_description": _description(subject_entity),
            "subject_type_labels": subject_type_labels,
            "subject_main_subject_labels": subject_main_subject_labels,
            "subject_location_labels": subject_location_labels,
            "answer_subdivision_labels": answer_subdivision_labels,
            "question_format_args": {"descriptor": subject_label},
            "multi_hop_unique": True,
        },
    )


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
