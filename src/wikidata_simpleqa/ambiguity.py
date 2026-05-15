"""Conservative non-temporal ambiguity resolution."""

from __future__ import annotations

from .entity_normalization import normalize_name
from .models import AmbiguityResolution, CandidateFact, DomainTemplate


def resolve_subject_ambiguity(
    candidate: CandidateFact,
    template: DomainTemplate,
    competitor_entities: dict[str, dict],
    *,
    cutoff_year: int,
) -> AmbiguityResolution | None:
    """Resolve same-label competitors using medium descriptors when possible."""
    competitor_qids = sorted(competitor_entities)
    if not competitor_qids:
        return AmbiguityResolution(
            status="label_unique",
            descriptor=candidate.subject_label,
            signature=[],
            competitor_qids=[],
        )

    for entity in competitor_entities.values():
        competitor_type_qids = _extract_claim_qids(entity, "P31")
        if template.subject_type_qid in competitor_type_qids:
            break
    else:
        return AmbiguityResolution(
            status="resolved_by_non_temporal_descriptor",
            descriptor=candidate.subject_label,
            signature=[template.subject_type_label],
            competitor_qids=competitor_qids,
        )

    location_descriptor = _safe_location_descriptor(candidate, template)
    if location_descriptor is not None:
        return AmbiguityResolution(
            status="resolved_by_non_temporal_descriptor",
            descriptor=location_descriptor,
            signature=["location_descriptor"],
            competitor_qids=competitor_qids,
        )
    year_descriptor = _safe_year_descriptor(candidate, template, competitor_entities, cutoff_year)
    if year_descriptor is not None:
        return AmbiguityResolution(
            status="resolved_by_year_descriptor",
            descriptor=year_descriptor,
            signature=[str(_candidate_year(candidate))],
            competitor_qids=competitor_qids,
        )
    return None


def _safe_location_descriptor(candidate: CandidateFact, template: DomainTemplate) -> str | None:
    """Return a safe non-answer location descriptor when it will not leak the answer."""
    if not template.allow_non_answer_location_descriptor:
        return None
    base_label = candidate.subject_label.strip()
    if not base_label:
        return None
    normalized_forbidden = {
        normalize_name(label)
        for label in (
            candidate.answer_labels
            + candidate.answer_aliases
            + candidate.source_metadata.get("answer_subdivision_labels", [])
        )
        if normalize_name(label)
    }
    for location_label in candidate.source_metadata.get("subject_location_labels", []):
        normalized_location = normalize_name(str(location_label))
        if not normalized_location or normalized_location in normalized_forbidden:
            continue
        return f"{base_label} in {location_label}"
    return None


def _safe_year_descriptor(
    candidate: CandidateFact,
    template: DomainTemplate,
    competitor_entities: dict[str, dict],
    cutoff_year: int,
) -> str | None:
    """Return a safe pre-cutoff year descriptor for same-medium collisions."""
    candidate_year = _candidate_year(candidate)
    if candidate.answer_type == "Date":
        return None
    if candidate_year is None or candidate_year >= cutoff_year:
        return None
    same_type_competitors = []
    for entity in competitor_entities.values():
        competitor_type_qids = _extract_claim_qids(entity, "P31")
        if template.subject_type_qid in competitor_type_qids:
            same_type_competitors.append(entity)
    if not same_type_competitors:
        return None
    for entity in same_type_competitors:
        competitor_years = _extract_claim_years(entity, template.date_property_pid)
        if not competitor_years or candidate_year in competitor_years:
            return None
    return f"{candidate.subject_label} ({candidate_year})"


def _candidate_year(candidate: CandidateFact) -> int | None:
    """Return the candidate's anchor year when it is parseable."""
    try:
        return int(candidate.date_value[:4])
    except (TypeError, ValueError):
        return None


def _extract_claim_years(entity: dict, pid: str) -> set[int]:
    """Return claim years for one time-valued property."""
    claims = entity.get("claims", {}).get(pid, [])
    years: set[int] = set()
    for claim in claims:
        mainsnak = claim.get("mainsnak", {})
        datavalue = mainsnak.get("datavalue", {})
        value = datavalue.get("value", {})
        time_value = value.get("time")
        if not isinstance(time_value, str):
            continue
        stripped = time_value.lstrip("+")
        year_text = stripped[:4]
        if len(year_text) != 4 or not year_text.isdigit():
            continue
        years.add(int(year_text))
    return years


def _extract_claim_qids(entity: dict, pid: str) -> list[str]:
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
