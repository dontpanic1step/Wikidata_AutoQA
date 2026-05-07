"""Candidate harvesting and hydration for the Stage 1 slice."""

from __future__ import annotations

import re
from typing import Any

from .config import Settings
from .composed_harvester import harvest_composed_candidates
from .date_answers import format_iso_date_for_answer, normalize_wikidata_date_literal
from .models import CandidateFact, DomainTemplate
from .reasoning import build_reasoning_hop, normalize_reasoning_style
from .sparql_queries import build_candidate_query
from .wikidata_client import WikidataClient

QID_LIKE_LABEL_PATTERN = re.compile(r"^Q\d+$")
WIKIDATA_ENTITY_PREFIX = "http://www.wikidata.org/entity/"
ALLOWED_SUBJECT_KIND_OVERRIDES = {
    "artwork": {"mural", "painting", "sculpture", "work of art", "installation art"},
    "film": {"anime film", "feature film", "documentary film", "short film"},
    "album": {"studio album", "live album", "extended play", "ep"},
    "building": {"arena", "tower", "hall", "centre", "center"},
    "scholarly article": {"academic work", "working paper", "scholarly article"},
    "video game": {"fan disc", "visual novel", "role-playing video game"},
}


def harvest_candidates(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
) -> list[CandidateFact]:
    """Harvest and hydrate raw candidates for one template."""
    reasoning_style = normalize_reasoning_style(template.reasoning_style or template.composition_style)
    if reasoning_style != "single_fact":
        return harvest_composed_candidates(client=client, settings=settings, template=template)

    query = build_candidate_query(
        template=template,
        target_start_date=settings.target_start_date,
        date_upper_bound=settings.date_upper_bound,
        limit=min(settings.harvest_limit_per_template, template.retrieval_limit),
    )
    rows = client.sparql_query(query)
    rows = _filter_unique_rows(rows)
    qids = _collect_qids(rows)
    entities = client.get_entities(qids) if qids else {}
    related_qids = _collect_related_qids(entities)
    related_entities = client.get_entities(related_qids) if related_qids else {}
    candidates: list[CandidateFact] = []
    for row in rows:
        candidate = _row_to_candidate(
            row=row,
            entities=entities,
            related_entities=related_entities,
            settings=settings,
            template=template,
            query=query,
        )
        candidates.append(candidate)
    return candidates


def _collect_qids(rows: list[dict[str, Any]]) -> list[str]:
    qids: set[str] = set()
    for row in rows:
        item_qid = row["item"]["value"].rsplit("/", 1)[-1]
        qids.add(item_qid)
        answer_qid = _extract_entity_qid(row["answer"])
        if answer_qid is not None:
            qids.add(answer_qid)
    return sorted(qids)


def _filter_unique_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        item_qid = row["item"]["value"].rsplit("/", 1)[-1]
        date_value = row["date"]["value"][:10]
        grouped.setdefault((item_qid, date_value), []).append(row)

    filtered: list[dict[str, Any]] = []
    for grouped_rows in grouped.values():
        answer_qids = {
            _answer_key(row["answer"])
            for row in grouped_rows
        }
        if len(answer_qids) == 1:
            filtered.append(grouped_rows[0])
    return filtered


def _collect_related_qids(entities: dict[str, Any]) -> list[str]:
    related_qids: set[str] = set()
    for entity in entities.values():
        for pid in ("P31", "P131", "P17", "P276", "P150"):
            related_qids.update(_extract_claim_qids(entity, pid))
    return sorted(related_qids)


def _row_to_candidate(
    row: dict[str, Any],
    entities: dict[str, Any],
    related_entities: dict[str, Any],
    settings: Settings,
    template: DomainTemplate,
    query: str,
) -> CandidateFact:
    subject_qid = row["item"]["value"].rsplit("/", 1)[-1]
    answer_qid = _extract_entity_qid(row["answer"])
    subject_entity = entities.get(subject_qid, {})
    answer_entity = entities.get(answer_qid, {}) if answer_qid is not None else {}
    subject_label, subject_label_source = _select_label(
        subject_entity,
        row.get("itemLabel", {}).get("value"),
    )
    answer_label, answer_label_source, answer_aliases, answer_record_qid = _extract_answer_fields(
        answer_binding=row["answer"],
        answer_label_binding=row.get("answerLabel", {}).get("value"),
        answer_entity=answer_entity,
        template=template,
    )
    subject_aliases = _extract_aliases(subject_entity)
    subject_type_qids = _extract_claim_qids(subject_entity, "P31")
    subject_type_labels = _extract_entity_labels(related_entities, subject_type_qids)
    subject_location_qids = _extract_claim_qids(subject_entity, "P131") + _extract_claim_qids(
        subject_entity, "P276"
    )
    subject_location_labels = _extract_entity_labels(related_entities, subject_location_qids)
    answer_subdivision_labels = _extract_entity_labels(
        related_entities,
        _extract_claim_qids(answer_entity, "P150"),
    )
    date_value = row["date"]["value"][:10]
    subject_kind = _select_subject_kind(template, subject_type_labels)

    return CandidateFact(
        subject_qid=subject_qid,
        subject_label=subject_label,
        subject_aliases=subject_aliases,
        domain=template.domain,
        topic=template.topic,
        answer_type=template.answer_type,
        question_family=template.question_family,
        subject_type_qids=subject_type_qids,
        target_property_pid=template.target_property_pid,
        target_property_label=template.target_property_label,
        answer_qids=[answer_record_qid],
        answer_labels=[answer_label] if answer_label else [],
        answer_aliases=answer_aliases,
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
                target_qid=answer_record_qid,
                target_label=answer_label,
                role="answer",
            )
        ],
        derivation_signature={
            "style": "single_fact",
            "rule": "direct_subject_property_lookup",
        },
        provenance_complete=bool(subject_qid and answer_record_qid and answer_label),
        source_metadata={
            "wikidata_access_date": settings.run_date,
            "retrieval_method": "WDQS + wbgetentities + wbsearchentities",
            "sparql_query": query,
            "subject_description": _extract_description(subject_entity),
            "subject_type_labels": subject_type_labels,
            "subject_location_labels": subject_location_labels,
            "answer_subdivision_labels": answer_subdivision_labels,
            "question_format_args": {"subject_kind": subject_kind},
            "subject_label_source": subject_label_source,
            "answer_label_source": answer_label_source,
        },
    )


def _extract_label(entity: dict[str, Any], fallback: str | None) -> str:
    labels = entity.get("labels", {})
    label = labels.get("en", {}).get("value") or (fallback or "")
    if QID_LIKE_LABEL_PATTERN.fullmatch(label):
        return ""
    return label


def _select_label(entity: dict[str, Any], wdqs_fallback: str | None) -> tuple[str, str]:
    """Select a controlled label with source tracking."""
    hydrated = _extract_label(entity, None)
    if hydrated:
        return hydrated, "wbgetentities_en"
    fallback = _extract_label({}, wdqs_fallback)
    if fallback:
        return fallback, "wdqs_label_fallback"
    return "", "missing"


def _extract_answer_fields(
    *,
    answer_binding: dict[str, Any],
    answer_label_binding: str | None,
    answer_entity: dict[str, Any],
    template: DomainTemplate,
) -> tuple[str, str, list[str], str]:
    """Return answer label, source, aliases, and serialized answer id."""
    if template.answer_format == "date":
        iso_value = normalize_wikidata_date_literal(answer_binding["value"])
        return (
            format_iso_date_for_answer(iso_value),
            "wikidata_date_literal",
            [iso_value],
            f"VALUE:date:{iso_value}",
        )

    answer_label, answer_label_source = _select_label(answer_entity, answer_label_binding)
    return (
        answer_label,
        answer_label_source,
        _extract_aliases(answer_entity),
        _extract_entity_qid(answer_binding) or _answer_key(answer_binding),
    )


def _extract_aliases(entity: dict[str, Any]) -> list[str]:
    aliases = entity.get("aliases", {}).get("en", [])
    return [alias["value"] for alias in aliases if "value" in alias]


def _extract_description(entity: dict[str, Any]) -> str:
    descriptions = entity.get("descriptions", {})
    return descriptions.get("en", {}).get("value", "")


def _extract_claim_qids(entity: dict[str, Any], pid: str) -> list[str]:
    claims = entity.get("claims", {}).get(pid, [])
    qids: list[str] = []
    for claim in claims:
        mainsnak = claim.get("mainsnak", {})
        datavalue = mainsnak.get("datavalue", {})
        value = datavalue.get("value", {})
        qid = value.get("id")
        if qid:
            qids.append(qid)
    return qids


def _extract_entity_qid(binding: dict[str, Any]) -> str | None:
    if binding.get("type") != "uri":
        return None
    value = binding.get("value", "")
    if not value.startswith(WIKIDATA_ENTITY_PREFIX):
        return None
    return value.rsplit("/", 1)[-1]


def _answer_key(binding: dict[str, Any]) -> str:
    entity_qid = _extract_entity_qid(binding)
    if entity_qid is not None:
        return entity_qid
    datatype = binding.get("datatype", "literal")
    return f"VALUE:{datatype}:{binding.get('value', '')}"


def _extract_entity_labels(entities: dict[str, Any], qids: list[str]) -> list[str]:
    labels: list[str] = []
    for qid in qids:
        entity = entities.get(qid, {})
        label, _ = _select_label(entity, None)
        if label:
            labels.append(label)
    return labels


def _select_subject_kind(template: DomainTemplate, subject_type_labels: list[str]) -> str:
    default_kind = template.subject_type_label
    generic_labels = {
        default_kind.lower(),
        "entity",
        "creative work",
        "work",
        "object",
        "item",
    }
    allowed_overrides = ALLOWED_SUBJECT_KIND_OVERRIDES.get(default_kind.lower(), set())
    default_tokens = set(default_kind.lower().split())
    for label in subject_type_labels:
        normalized = label.lower()
        label_tokens = set(normalized.split())
        if normalized in generic_labels or len(label.split()) > 4:
            continue
        if default_tokens.intersection(label_tokens) or normalized in allowed_overrides:
            return label
    return default_kind
