"""Two-hop template pairing catalog for Route 4."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import DomainTemplate
from .reasoning import normalize_reasoning_style
from .route1_hidden_entity import CLUE_HIDDEN_OBJECT, CLUE_HIDDEN_SUBJECT
from .route4_template_catalog import get_route4_reviewed_single_hop_templates


@dataclass(frozen=True, slots=True)
class Route4TwoHopTemplate:
    """One ordered Route 4 answer-hop/clue-hop template pair."""

    template_key: str
    answer_template_key: str
    clue_template_key: str
    clue_orientation: str
    hidden_subject_type_qid: str
    hidden_subject_type_label: str
    answer_property_pid: str
    answer_property_label: str
    clue_property_pid: str
    clue_property_label: str
    answer_type: str
    visible_clue_answer_type: str
    join_basis: str


PERSON_QIDS = {"Q5"}
PLACE_OBJECT_JOIN_PIDS = {"P17", "P131"}
PLACE_LEVEL_BY_SUBJECT_QID: dict[str, str] = {
    "Q6256": "place:country",
    "Q3624078": "place:country",
    "Q515": "place:city",
    "Q15284": "place:municipality",
    "Q56061": "place:administrative_area",
}

OBJECT_TYPE_KEYS_BY_PID: dict[str, set[str]] = {
    "P61": {"group:person"},
    "P84": {"group:person"},
    "P86": {"group:person"},
    "P98": {"group:person"},
    "P112": {"group:person"},
    "P170": {"group:person"},
    "P175": {"group:person"},
    "P287": {"group:person"},
    "P371": {"group:person"},
    "P405": {"group:person"},
    "P655": {"group:person"},
    "P1891": {"group:person"},
    "P50": {"group:person"},
    "P57": {"group:person"},
    "P58": {"group:person"},
    "P1037": {"group:person"},
}


def get_route4_two_hop_template_catalog(
    templates: Iterable[DomainTemplate] | None = None,
) -> list[Route4TwoHopTemplate]:
    """Return every ordered Route 4 two-hop template pair."""
    single_hop_templates = _usable_single_hop_templates(
        templates if templates is not None else get_route4_reviewed_single_hop_templates()
    )
    pairs: list[Route4TwoHopTemplate] = []
    seen: set[str] = set()
    for answer_template in single_hop_templates:
        for clue_template in single_hop_templates:
            same_property = answer_template.target_property_pid == clue_template.target_property_pid
            if not same_property:
                subject_basis = _hidden_subject_join_basis(answer_template, clue_template)
                if subject_basis:
                    _append_pair(
                        pairs,
                        seen,
                        answer_template=answer_template,
                        clue_template=clue_template,
                        clue_orientation=CLUE_HIDDEN_SUBJECT,
                        join_basis=subject_basis,
                    )
            object_basis = _hidden_object_join_basis(answer_template, clue_template)
            if object_basis:
                _append_pair(
                    pairs,
                    seen,
                    answer_template=answer_template,
                    clue_template=clue_template,
                    clue_orientation=CLUE_HIDDEN_OBJECT,
                    join_basis=object_basis,
                )
    return pairs


def get_route4_combinable_single_hop_templates(
    templates: Iterable[DomainTemplate] | None = None,
) -> list[DomainTemplate]:
    """Return one-hop templates that participate in at least one Route 4 pair."""
    single_hop_templates = _usable_single_hop_templates(
        templates if templates is not None else get_route4_reviewed_single_hop_templates()
    )
    used_keys = _participating_template_keys(get_route4_two_hop_template_catalog(single_hop_templates))
    return [template for template in single_hop_templates if template.template_key in used_keys]


def get_route4_uncombined_single_hop_templates(
    templates: Iterable[DomainTemplate] | None = None,
) -> list[DomainTemplate]:
    """Return one-hop templates that are not compatible with any Route 4 pair."""
    single_hop_templates = _usable_single_hop_templates(
        templates if templates is not None else get_route4_reviewed_single_hop_templates()
    )
    used_keys = _participating_template_keys(get_route4_two_hop_template_catalog(single_hop_templates))
    return [template for template in single_hop_templates if template.template_key not in used_keys]


def get_route4_two_hop_template_summary(
    templates: Iterable[DomainTemplate] | None = None,
) -> dict[str, object]:
    """Return compact counts for the Route 4 two-hop template catalog."""
    single_hop_templates = _usable_single_hop_templates(
        templates if templates is not None else get_route4_reviewed_single_hop_templates()
    )
    pairs = get_route4_two_hop_template_catalog(single_hop_templates)
    uncombined = get_route4_uncombined_single_hop_templates(single_hop_templates)
    return {
        "single_hop_templates": len(single_hop_templates),
        "two_hop_templates": len(pairs),
        "combinable_single_hop_templates": len(single_hop_templates) - len(uncombined),
        "uncombined_single_hop_templates": len(uncombined),
        "clue_orientations": _counts(pair.clue_orientation for pair in pairs),
        "join_bases": _counts(pair.join_basis for pair in pairs),
        "uncombined_template_keys": [template.template_key for template in uncombined],
    }


def _append_pair(
    pairs: list[Route4TwoHopTemplate],
    seen: set[str],
    *,
    answer_template: DomainTemplate,
    clue_template: DomainTemplate,
    clue_orientation: str,
    join_basis: str,
) -> None:
    template_key = "__".join(
        [
            "route4_two_hop",
            answer_template.template_key,
            clue_orientation,
            clue_template.template_key,
        ]
    )
    if template_key in seen:
        return
    seen.add(template_key)
    pairs.append(
        Route4TwoHopTemplate(
            template_key=template_key,
            answer_template_key=answer_template.template_key,
            clue_template_key=clue_template.template_key,
            clue_orientation=clue_orientation,
            hidden_subject_type_qid=answer_template.subject_type_qid,
            hidden_subject_type_label=answer_template.subject_type_label,
            answer_property_pid=answer_template.target_property_pid,
            answer_property_label=answer_template.target_property_label,
            clue_property_pid=clue_template.target_property_pid,
            clue_property_label=clue_template.target_property_label,
            answer_type=answer_template.answer_type,
            visible_clue_answer_type=clue_template.answer_type,
            join_basis=join_basis,
        )
    )


def _usable_single_hop_templates(templates: Iterable[DomainTemplate]) -> list[DomainTemplate]:
    return [
        template
        for template in templates
        if normalize_reasoning_style(template.reasoning_style or template.composition_style) == "single_fact"
        and template.status != "frozen"
    ]


def _hidden_subject_join_basis(answer_template: DomainTemplate, clue_template: DomainTemplate) -> str:
    if answer_template.subject_type_qid and answer_template.subject_type_qid == clue_template.subject_type_qid:
        return "same_subject_type_qid"
    if _normalized_label(answer_template.subject_type_label) == _normalized_label(clue_template.subject_type_label):
        return "same_subject_type_label"
    return ""


def _hidden_object_join_basis(answer_template: DomainTemplate, clue_template: DomainTemplate) -> str:
    same_relation_place_basis = _same_relation_place_object_join_basis(answer_template, clue_template)
    if same_relation_place_basis:
        return same_relation_place_basis
    hidden_type_keys = _subject_type_keys(answer_template)
    clue_answer_type_keys = _answer_object_type_keys(clue_template)
    overlap = sorted(hidden_type_keys.intersection(clue_answer_type_keys))
    if not overlap:
        return ""
    return f"clue_object_matches_hidden_subject:{overlap[0]}"


def _same_relation_place_object_join_basis(answer_template: DomainTemplate, clue_template: DomainTemplate) -> str:
    if answer_template.target_property_pid != clue_template.target_property_pid:
        return ""
    if answer_template.target_property_pid not in PLACE_OBJECT_JOIN_PIDS:
        return ""
    if clue_template.answer_format != "entity" or clue_template.answer_type != "Place":
        return ""
    return f"same_place_relation:{answer_template.target_property_pid}"


def _subject_type_keys(template: DomainTemplate) -> set[str]:
    keys = {f"qid:{template.subject_type_qid}"} if template.subject_type_qid else set()
    normalized_label = _normalized_label(template.subject_type_label)
    if normalized_label:
        keys.add(f"label:{normalized_label}")
    if template.subject_type_qid in PERSON_QIDS:
        keys.add("group:person")
    place_level = _place_level_for_subject_template(template)
    if place_level:
        keys.add(place_level)
    return keys


def _answer_object_type_keys(template: DomainTemplate) -> set[str]:
    if template.answer_format != "entity" or template.answer_type in {"Date", "Number"}:
        return set()
    keys: set[str] = set()
    if template.answer_type == "Person":
        keys.add("group:person")
    elif template.answer_type == "Place":
        place_level = _place_level_from_label(template.target_property_label)
        if place_level:
            keys.add(place_level)
    keys.update(OBJECT_TYPE_KEYS_BY_PID.get(template.target_property_pid, set()))
    return keys


def _participating_template_keys(pairs: Iterable[Route4TwoHopTemplate]) -> set[str]:
    keys: set[str] = set()
    for pair in pairs:
        keys.add(pair.answer_template_key)
        keys.add(pair.clue_template_key)
    return keys


def _counts(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def _normalized_label(value: str) -> str:
    return " ".join(value.casefold().split())


def _place_level_for_subject_template(template: DomainTemplate) -> str:
    return PLACE_LEVEL_BY_SUBJECT_QID.get(template.subject_type_qid) or _place_level_from_label(
        template.subject_type_label
    )


def _place_level_from_label(value: str) -> str:
    label = _normalized_label(value)
    if "country" in label:
        return "place:country"
    if "city" in label:
        return "place:city"
    if "municipality" in label:
        return "place:municipality"
    if "administrative" in label:
        return "place:administrative_area"
    return ""
