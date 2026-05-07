"""Conservative non-temporal ambiguity resolution."""

from __future__ import annotations

from .entity_normalization import normalize_name
from .models import AmbiguityResolution, CandidateFact, DomainTemplate


def resolve_subject_ambiguity(
    candidate: CandidateFact,
    template: DomainTemplate,
    competitor_entities: dict[str, dict],
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
    return None


def _safe_location_descriptor(candidate: CandidateFact, template: DomainTemplate) -> str | None:
    """Return a safe non-answer location descriptor when it will not leak the answer."""
    if candidate.target_property_pid == "P17":
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
