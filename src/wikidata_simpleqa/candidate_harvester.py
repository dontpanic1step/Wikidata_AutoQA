"""Candidate harvesting and hydration for the Stage 1 slice."""

from __future__ import annotations

from datetime import date
import re
from typing import Any

from .config import Settings
from .composed_harvester import harvest_composed_candidates
from .date_answers import format_iso_date_for_answer, normalize_wikidata_date_literal
from .models import CandidateFact, DomainTemplate
from .reasoning import build_reasoning_hop, normalize_reasoning_style
from .sparql_queries import build_candidate_query, build_subject_seed_query
from .subject_resources import canonical_subject_resource
from .wikidata_client import WikidataClient

QID_LIKE_LABEL_PATTERN = re.compile(r"^Q\d+$")
WIKIDATA_ENTITY_PREFIX = "http://www.wikidata.org/entity/"
BROAD_STAGE_SUBJECT_TYPE_QIDS = {
    "Q5",        # human
    "Q7397",     # software
    "Q2424752",  # product
    "Q16521",    # taxon
    "Q11173",    # battery
    "Q44167",    # engine
}
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
    try:
        rows = client.sparql_query(query)
        rows = _filter_unique_rows(rows)
        return _rows_to_candidates(
            rows=rows,
            settings=settings,
            template=template,
            query=query,
            client=client,
        )
    except Exception as exc:  # noqa: BLE001
        client.record_problem(
            "direct_candidate_query_failed",
            "The direct WDQS candidate query failed before validation could start.",
            domain=template.domain,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        if not _use_staged_seed_strategy(template):
            return []

    client.record_problem(
        "staged_seed_strategy_used",
        "Used a staged WDQS seed query with local claim extraction for a broad template after a direct query failure.",
        domain=template.domain,
        subject_type_qid=template.subject_type_qid,
        date_property_pid=template.date_property_pid,
        target_property_pid=template.target_property_pid,
    )
    return _harvest_candidates_via_subject_seeds(
        client=client,
        settings=settings,
        template=template,
    )


def _use_staged_seed_strategy(template: DomainTemplate) -> bool:
    """Return whether this template should avoid a broad WDQS join query."""
    if template.exact_instance_only:
        return False
    if "staged_seed_query" in template.query_tags:
        return True
    return template.subject_type_qid in BROAD_STAGE_SUBJECT_TYPE_QIDS


def _harvest_candidates_via_subject_seeds(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
) -> list[CandidateFact]:
    """Harvest broad templates by seeding subjects, then extracting answers locally."""
    rows, query = _run_windowed_subject_seed_queries(
        client=client,
        settings=settings,
        template=template,
    )
    subject_qids = sorted(
        {
            row["item"]["value"].rsplit("/", 1)[-1]
            for row in rows
            if "item" in row and "value" in row["item"]
        }
    )
    entities = client.get_entities(subject_qids) if subject_qids else {}

    provisional_rows: list[dict[str, Any]] = []
    answer_qids: set[str] = set()
    for row in rows:
        subject_qid = row["item"]["value"].rsplit("/", 1)[-1]
        subject_entity = entities.get(subject_qid, {})
        answer_value = _extract_unique_answer_value(subject_entity, template)
        if answer_value is None:
            continue
        provisional_rows.append(
            {
                "subject_qid": subject_qid,
                "subject_entity": subject_entity,
                "date_value": normalize_wikidata_date_literal(row["date"]["value"]),
                "answer_value": answer_value,
            }
        )
        answer_qid = answer_value.get("qid")
        if answer_qid is not None:
            answer_qids.add(answer_qid)

    answer_entities = client.get_entities(sorted(answer_qids)) if answer_qids else {}
    related_qids = set(_collect_related_qids(entities))
    related_qids.update(_collect_related_qids(answer_entities))
    related_entities = client.get_entities(sorted(related_qids)) if related_qids else {}

    candidates: list[CandidateFact] = []
    for row in provisional_rows:
        candidate = _seed_row_to_candidate(
            row=row,
            answer_entities=answer_entities,
            related_entities=related_entities,
            settings=settings,
            template=template,
            query=query,
        )
        if candidate is not None:
            candidates.append(candidate)
    return candidates


def _rows_to_candidates(
    *,
    rows: list[dict[str, Any]],
    settings: Settings,
    template: DomainTemplate,
    query: str,
    client: WikidataClient,
) -> list[CandidateFact]:
    """Hydrate direct WDQS rows into pipeline candidates."""
    qids = _collect_qids(rows)
    entities = client.get_entities(qids) if qids else {}
    related_qids = _collect_related_qids(entities)
    related_entities = client.get_entities(related_qids) if related_qids else {}
    candidates: list[CandidateFact] = []
    for row in rows:
        candidates.append(
            _row_to_candidate(
                row=row,
                entities=entities,
                related_entities=related_entities,
                settings=settings,
                template=template,
                query=query,
            )
        )
    return candidates


def _run_windowed_subject_seed_queries(
    client: WikidataClient,
    settings: Settings,
    template: DomainTemplate,
) -> tuple[list[dict[str, Any]], str]:
    """Run staged subject seed queries over smaller date windows."""
    limit = min(settings.harvest_limit_per_template, template.retrieval_limit)
    all_rows: list[dict[str, Any]] = []
    seen_pairs: set[tuple[str, str]] = set()
    queries: list[str] = []
    window_days = _seed_window_days(template)
    for window_start, window_end in _iter_month_windows(
        settings.target_start_date,
        settings.date_upper_bound,
        window_days=window_days,
    ):
        query = build_subject_seed_query(
            template=template,
            target_start_date=window_start,
            date_upper_bound=window_end,
            limit=limit,
        )
        queries.append(query)
        try:
            rows = client.sparql_query(query)
        except Exception as exc:  # noqa: BLE001
            client.record_problem(
                "windowed_subject_seed_query_failed",
                "One staged WDQS subject-seed query failed; returning any rows collected so far.",
                domain=template.domain,
                window_start=window_start,
                window_end=window_end,
                error_type=type(exc).__name__,
                error_message=str(exc),
                partial_rows=len(all_rows),
            )
            break
        for row in rows:
            item_qid = row["item"]["value"].rsplit("/", 1)[-1]
            date_value = normalize_wikidata_date_literal(row["date"]["value"])
            key = (item_qid, date_value)
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            all_rows.append(row)
        if len(all_rows) >= max(limit * 5, limit):
            break
    client.record_problem(
        "windowed_subject_seed_queries_used",
        "Split broad subject seed discovery into smaller monthly WDQS windows.",
        domain=template.domain,
        query_count=len(queries),
    )
    return all_rows, "\n\n".join(queries)


def _seed_window_days(template: DomainTemplate) -> int | None:
    """Return an optional fixed seed-window size for very broad templates."""
    if "seed_window_daily" in template.query_tags:
        return 1
    if "seed_window_weekly" in template.query_tags:
        return 7
    if "seed_window_monthly" in template.query_tags:
        return None
    if template.subject_type_qid == "Q5":
        return 1
    return None


def _iter_month_windows(
    start_date: str,
    end_date: str,
    window_days: int | None = None,
) -> list[tuple[str, str]]:
    """Split an inclusive ISO date span into monthly or fixed-day windows."""
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    if window_days is not None:
        return _iter_fixed_day_windows(start, end, window_days)
    windows: list[tuple[str, str]] = []
    cursor = date(start.year, start.month, 1)
    while cursor <= end:
        next_month = _first_day_of_next_month(cursor)
        month_start = cursor if cursor >= start else start
        month_end = (
            date.fromordinal(next_month.toordinal() - 1)
            if next_month <= end
            else end
        )
        if month_start <= month_end:
            windows.append((month_start.isoformat(), month_end.isoformat()))
        cursor = next_month
    return windows


def _iter_fixed_day_windows(
    start: date,
    end: date,
    window_days: int,
) -> list[tuple[str, str]]:
    """Split an inclusive ISO date span into fixed-size day windows."""
    windows: list[tuple[str, str]] = []
    cursor = start
    while cursor <= end:
        window_end = min(date.fromordinal(cursor.toordinal() + window_days - 1), end)
        windows.append((cursor.isoformat(), window_end.isoformat()))
        cursor = date.fromordinal(window_end.toordinal() + 1)
    return windows


def _first_day_of_next_month(value: date) -> date:
    """Return the first day of the month after the given date."""
    if value.month == 12:
        return date(value.year + 1, 1, 1)
    return date(value.year, value.month + 1, 1)


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
        for pid in ("P31", "P279", "P131", "P17", "P276", "P150", "P921"):
            related_qids.update(_extract_claim_qids(entity, pid))
    return sorted(related_qids)


def _extract_unique_answer_value(
    subject_entity: dict[str, Any],
    template: DomainTemplate,
) -> dict[str, str] | None:
    """Extract one unique answer value from hydrated claims."""
    claims = subject_entity.get("claims", {}).get(template.target_property_pid, [])
    values: dict[str, dict[str, str]] = {}
    for claim in claims:
        if claim.get("rank") == "deprecated":
            continue
        mainsnak = claim.get("mainsnak", {})
        if mainsnak.get("snaktype") != "value":
            continue
        value = mainsnak.get("datavalue", {}).get("value")
        if template.answer_format == "date":
            time_value = value.get("time") if isinstance(value, dict) else None
            if not time_value:
                continue
            iso_value = normalize_wikidata_date_literal(time_value)
            values[f"VALUE:date:{iso_value}"] = {
                "record_qid": f"VALUE:date:{iso_value}",
                "label": format_iso_date_for_answer(iso_value),
                "label_source": "wikidata_date_literal",
                "alias": iso_value,
            }
            continue
        qid = value.get("id") if isinstance(value, dict) else None
        if not qid:
            continue
        values[qid] = {
            "qid": qid,
            "record_qid": qid,
        }
    if len(values) != 1:
        return None
    return next(iter(values.values()))


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
    subject_main_subject_labels = _extract_entity_labels(
        related_entities,
        _extract_claim_qids(subject_entity, "P921"),
    )
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
    subject_resource_url, subject_resource_key = canonical_subject_resource(
        subject_qid,
        subject_entity,
    )
    subject_wikipedia_title = _extract_enwiki_title(subject_entity)
    subject_wikipedia_url = _wikipedia_url_from_title(subject_wikipedia_title)

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
        subject_resource_url=subject_resource_url,
        subject_resource_key=subject_resource_key,
        source_metadata={
            "wikidata_access_date": settings.run_date,
            "retrieval_method": "WDQS + wbgetentities + wbsearchentities",
            "sparql_query": query,
            "subject_wikipedia_title": subject_wikipedia_title,
            "subject_wikipedia_url": subject_wikipedia_url,
            "subject_sitelink_count": _count_sitelinks(subject_entity),
            "subject_claim_count": _count_claims(subject_entity),
            "subject_description": _extract_description(subject_entity),
            "subject_type_labels": subject_type_labels,
            "subject_main_subject_labels": subject_main_subject_labels,
            "subject_location_labels": subject_location_labels,
            "answer_subdivision_labels": answer_subdivision_labels,
            "question_format_args": {"subject_kind": subject_kind},
            "subject_label_source": subject_label_source,
            "answer_label_source": answer_label_source,
        },
    )


def _seed_row_to_candidate(
    row: dict[str, Any],
    answer_entities: dict[str, Any],
    related_entities: dict[str, Any],
    settings: Settings,
    template: DomainTemplate,
    query: str,
) -> CandidateFact | None:
    """Build one candidate from a subject-seed row and local claim extraction."""
    subject_qid = str(row["subject_qid"])
    subject_entity = row["subject_entity"]
    answer_value = row["answer_value"]
    subject_label, subject_label_source = _select_label(subject_entity, None)
    if not _subject_matches_template_type(subject_entity, related_entities, template):
        return None

    answer_qid = answer_value.get("qid")
    answer_entity = answer_entities.get(answer_qid, {}) if answer_qid else {}
    if template.answer_format == "date":
        answer_label = answer_value["label"]
        answer_label_source = answer_value["label_source"]
        answer_aliases = [answer_value["alias"]]
        answer_record_qid = answer_value["record_qid"]
    else:
        answer_label, answer_label_source = _select_label(answer_entity, None)
        answer_aliases = _extract_aliases(answer_entity)
        answer_record_qid = answer_value["record_qid"]

    subject_aliases = _extract_aliases(subject_entity)
    subject_type_qids = _extract_claim_qids(subject_entity, "P31")
    subject_type_labels = _extract_entity_labels(related_entities, subject_type_qids)
    subject_main_subject_labels = _extract_entity_labels(
        related_entities,
        _extract_claim_qids(subject_entity, "P921"),
    )
    subject_location_qids = _extract_claim_qids(subject_entity, "P131") + _extract_claim_qids(
        subject_entity, "P276"
    )
    subject_location_labels = _extract_entity_labels(related_entities, subject_location_qids)
    answer_subdivision_labels = _extract_entity_labels(
        related_entities,
        _extract_claim_qids(answer_entity, "P150"),
    )
    date_value = str(row["date_value"])
    subject_kind = _select_subject_kind(template, subject_type_labels)
    subject_resource_url, subject_resource_key = canonical_subject_resource(
        subject_qid,
        subject_entity,
    )
    subject_wikipedia_title = _extract_enwiki_title(subject_entity)
    subject_wikipedia_url = _wikipedia_url_from_title(subject_wikipedia_title)

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
        answer_labels=[answer_label],
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
            "rule": "staged_subject_seed_claim_extraction",
        },
        provenance_complete=bool(subject_qid and answer_record_qid and answer_label),
        subject_resource_url=subject_resource_url,
        subject_resource_key=subject_resource_key,
        source_metadata={
            "wikidata_access_date": settings.run_date,
            "retrieval_method": "WDQS subject seed + wbgetentities claim extraction",
            "sparql_query": query,
            "subject_wikipedia_title": subject_wikipedia_title,
            "subject_wikipedia_url": subject_wikipedia_url,
            "subject_sitelink_count": _count_sitelinks(subject_entity),
            "subject_claim_count": _count_claims(subject_entity),
            "subject_description": _extract_description(subject_entity),
            "subject_type_labels": subject_type_labels,
            "subject_main_subject_labels": subject_main_subject_labels,
            "subject_location_labels": subject_location_labels,
            "answer_subdivision_labels": answer_subdivision_labels,
            "question_format_args": {"subject_kind": subject_kind},
            "subject_label_source": subject_label_source,
            "answer_label_source": answer_label_source,
        },
    )


def _subject_matches_template_type(
    subject_entity: dict[str, Any],
    related_entities: dict[str, Any],
    template: DomainTemplate,
) -> bool:
    """Return whether the hydrated subject matches the template type conservatively."""
    direct_type_qids = _extract_claim_qids(subject_entity, "P31")
    if template.subject_type_qid in direct_type_qids:
        return True
    for direct_type_qid in direct_type_qids:
        direct_type_entity = related_entities.get(direct_type_qid, {})
        if template.subject_type_qid in _extract_claim_qids(direct_type_entity, "P279"):
            return True
    return False


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


def _extract_enwiki_title(entity: dict[str, Any]) -> str:
    """Return the English Wikipedia sitelink title when available."""
    sitelinks = entity.get("sitelinks", {})
    enwiki = sitelinks.get("enwiki", {})
    return str(enwiki.get("title", "")).strip()


def _wikipedia_url_from_title(title: str) -> str:
    """Return the canonical English Wikipedia URL for a title."""
    if not title:
        return ""
    return "https://en.wikipedia.org/wiki/" + title.replace(" ", "_")


def _count_sitelinks(entity: dict[str, Any]) -> int:
    """Return the number of sitelinks on one hydrated entity."""
    sitelinks = entity.get("sitelinks", {})
    if not isinstance(sitelinks, dict):
        return 0
    return len(sitelinks)


def _count_claims(entity: dict[str, Any]) -> int:
    """Return the number of claim rows on one hydrated entity."""
    claims = entity.get("claims", {})
    if not isinstance(claims, dict):
        return 0
    return sum(len(rows) for rows in claims.values() if isinstance(rows, list))


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
