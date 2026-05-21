"""Route 4 hidden-entity two-hop composition support.

The old Route 1 hidden-entity route id is retained only as a disabled
compatibility alias for historical artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from .entity_normalization import normalize_name
from .models import CandidateFact, DomainTemplate
from .reasoning import build_reasoning_hop, normalize_reasoning_style

ROUTE4_WIKIDATA_TWO_HOP_ROUTE = "route4_wikidata_two_hop"
ROUTE4_TWO_HOP_CONTRACT = "route4_two_hop"
ROUTE1_HIDDEN_ENTITY_TWO_HOP_ROUTE = "route1_wikidata_hidden_entity_two_hop"
ROUTE1_HIDDEN_ENTITY_CONTRACT = "route1_hidden_entity_two_hop"
HIDDEN_ENTITY_REASONING_STYLE = "multi_hop_hidden_entity"

CLUE_HIDDEN_SUBJECT = "hidden_subject"
CLUE_HIDDEN_OBJECT = "hidden_object"


@dataclass(slots=True)
class Route1HiddenEntityTwoHopSeedUnit:
    """One Route 4 hidden-entity two-hop seed unit."""

    answer_template_key: str
    clue_template_key: str
    hidden_qid: str
    answer_qid: str
    visible_clue_key: str
    clue_orientation: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def state_key(self) -> str:
        """Return the stable state key for this composed seed."""
        explicit_key = str(self.metadata.get("route4_two_hop_seed_key", "")).strip()
        if explicit_key:
            return explicit_key
        explicit_key = str(self.metadata.get("route1_hidden_entity_seed_key", "")).strip()
        if explicit_key:
            return explicit_key
        parts = [
            self.answer_template_key,
            self.clue_template_key,
            self.clue_orientation,
            self.hidden_qid,
            self.answer_qid,
            self.visible_clue_key,
        ]
        return "|".join(part or "-" for part in parts)

    def to_metadata(self) -> dict[str, Any]:
        """Serialize this seed unit for candidate metadata."""
        return {
            "answer_template_key": self.answer_template_key,
            "clue_template_key": self.clue_template_key,
            "hidden_qid": self.hidden_qid,
            "answer_qid": self.answer_qid,
            "visible_clue_key": self.visible_clue_key,
            "clue_orientation": self.clue_orientation,
            "state_key": self.state_key,
        }


@dataclass(slots=True)
class Route1HiddenEntityTwoHopComposer:
    """Compose validated single-hop facts around a hidden entity."""

    max_pairs_per_hidden_entity: int = 8

    def compose(
        self,
        prepared_by_template: dict[str, list[CandidateFact]],
        template_by_key: dict[str, DomainTemplate],
    ) -> list[CandidateFact]:
        """Return composed hidden-entity two-hop candidates."""
        candidates = [
            candidate
            for candidates_for_template in prepared_by_template.values()
            for candidate in candidates_for_template
        ]
        by_subject: dict[str, list[CandidateFact]] = {}
        by_answer_qid: dict[str, list[CandidateFact]] = {}
        for candidate in candidates:
            if not _usable_single_hop(candidate):
                continue
            by_subject.setdefault(candidate.subject_qid, []).append(candidate)
            answer_qid = _first_answer_qid(candidate)
            if answer_qid and not answer_qid.startswith("VALUE:"):
                by_answer_qid.setdefault(answer_qid, []).append(candidate)

        provisional: list[CandidateFact] = []
        for answer_hop in candidates:
            if not _usable_single_hop(answer_hop):
                continue
            hidden_qid = answer_hop.subject_qid
            pair_count = 0
            for clue_hop in by_subject.get(hidden_qid, []):
                if pair_count >= self.max_pairs_per_hidden_entity:
                    break
                composed = _compose_pair(
                    answer_hop=answer_hop,
                    clue_hop=clue_hop,
                    answer_template=template_by_key[answer_hop.domain],
                    clue_template=template_by_key[clue_hop.domain],
                    clue_orientation=CLUE_HIDDEN_SUBJECT,
                )
                if composed is not None:
                    provisional.append(composed)
                    pair_count += 1
            for clue_hop in by_answer_qid.get(hidden_qid, []):
                if pair_count >= self.max_pairs_per_hidden_entity:
                    break
                composed = _compose_pair(
                    answer_hop=answer_hop,
                    clue_hop=clue_hop,
                    answer_template=template_by_key[answer_hop.domain],
                    clue_template=template_by_key[clue_hop.domain],
                    clue_orientation=CLUE_HIDDEN_OBJECT,
                )
                if composed is not None:
                    provisional.append(composed)
                    pair_count += 1

        return _drop_ambiguous_clue_paths(provisional)


def get_route1_hidden_entity_single_hop_templates(
    templates: Iterable[DomainTemplate],
) -> list[DomainTemplate]:
    """Return single-hop templates usable by the hidden-entity composer."""
    return [
        template
        for template in templates
        if normalize_reasoning_style(template.reasoning_style or template.composition_style) == "single_fact"
        and template.status != "frozen"
    ]


def hidden_entity_seed_unit_from_candidate(candidate: CandidateFact) -> Route1HiddenEntityTwoHopSeedUnit:
    """Build a stable seed unit from one hidden-entity candidate."""
    metadata = candidate.source_metadata
    answer_hop = metadata.get("answer_hop", {})
    clue_hop = metadata.get("clue_hop", {})
    visible_clue = metadata.get("visible_clue", {})
    unit = Route1HiddenEntityTwoHopSeedUnit(
        answer_template_key=str(answer_hop.get("template_key", candidate.domain)),
        clue_template_key=str(clue_hop.get("template_key", "")),
        hidden_qid=candidate.subject_qid,
        answer_qid=_first_answer_qid(candidate),
        visible_clue_key=str(visible_clue.get("qid") or visible_clue.get("value") or ""),
        clue_orientation=str(metadata.get("clue_orientation", "")),
    )
    unit.metadata["route4_two_hop_seed_key"] = unit.state_key
    return unit


def attach_hidden_entity_seed_metadata(candidate: CandidateFact) -> Route1HiddenEntityTwoHopSeedUnit:
    """Attach hidden-entity seed metadata to one candidate."""
    unit = hidden_entity_seed_unit_from_candidate(candidate)
    candidate.source_metadata["route4_two_hop_seed_key"] = unit.state_key
    candidate.source_metadata["route4_two_hop_seed_unit"] = unit.to_metadata()
    return unit


def hidden_entity_seed_key_from_record(record: dict[str, Any]) -> str:
    """Return a hidden-entity seed key from an accepted/rejected record."""
    metadata = record.get("source_metadata", {})
    if isinstance(metadata, dict):
        for key_name in ("route4_two_hop_seed_key", "route1_hidden_entity_seed_key", "route1_qid_seed_key"):
            key = str(metadata.get(key_name, "")).strip()
            if key:
                return key
    return ""


def _compose_pair(
    *,
    answer_hop: CandidateFact,
    clue_hop: CandidateFact,
    answer_template: DomainTemplate,
    clue_template: DomainTemplate,
    clue_orientation: str,
) -> CandidateFact | None:
    if answer_hop.target_property_pid == clue_hop.target_property_pid:
        return None
    if answer_hop.subject_qid == _first_answer_qid(answer_hop):
        return None
    visible_clue = _visible_clue(answer_hop, clue_hop, clue_orientation)
    if visible_clue is None:
        return None
    if _visible_clue_aliases_answer(visible_clue, answer_hop):
        return None

    answer_label = answer_hop.answer_labels[0] if answer_hop.answer_labels else ""
    visible_label = visible_clue["label"]
    if not answer_label or not visible_label:
        return None

    clue_source_qid = clue_hop.subject_qid
    clue_source_label = clue_hop.subject_label
    clue_target_qid = _first_answer_qid(clue_hop)
    clue_target_label = clue_hop.answer_labels[0] if clue_hop.answer_labels else ""
    answer_hop_record = _hop_metadata(answer_hop, answer_template)
    clue_hop_record = _hop_metadata(clue_hop, clue_template)
    required_clues = _required_reasoning_clues(clue_hop, visible_label)
    source_metadata = {
        "wikidata_access_date": answer_hop.source_metadata.get("wikidata_access_date", ""),
        "retrieval_method": "validated Wikidata single-hop fact composition for Route 4",
        "answer_hop": answer_hop_record,
        "clue_hop": clue_hop_record,
        "clue_orientation": clue_orientation,
        "hidden_entities": [
            {
                "qid": answer_hop.subject_qid,
                "label": answer_hop.subject_label,
                "aliases": answer_hop.subject_aliases,
                "role": "hidden_subject",
            }
        ],
        "visible_clue": visible_clue,
        "visible_clue_entities_or_values": [visible_clue],
        "required_reasoning_clues": required_clues,
        "answer_template_key": answer_template.template_key,
        "clue_template_key": clue_template.template_key,
        "answer_hop_canonical_question": answer_hop.canonical_question,
        "clue_hop_canonical_question": clue_hop.canonical_question,
        "multi_hop_unique": True,
        "question_format_args": {
            "subject_kind": answer_template.subject_type_label,
            "visible_clue": visible_label,
        },
    }
    canonical_question = _build_hidden_entity_canonical_question(
        answer_hop=answer_hop,
        answer_template=answer_template,
        clue_hop=clue_hop,
        clue_orientation=clue_orientation,
        visible_label=visible_label,
    )
    composed = CandidateFact(
        subject_qid=answer_hop.subject_qid,
        subject_label=answer_hop.subject_label,
        subject_aliases=answer_hop.subject_aliases.copy(),
        domain=f"{answer_template.template_key}__via__{clue_template.template_key}",
        topic=answer_hop.topic,
        answer_type=answer_hop.answer_type,
        question_family=f"{answer_hop.question_family}__hidden_entity_two_hop",
        subject_type_qids=answer_hop.subject_type_qids.copy(),
        target_property_pid=answer_hop.target_property_pid,
        target_property_label=answer_hop.target_property_label,
        answer_qids=answer_hop.answer_qids.copy(),
        answer_labels=answer_hop.answer_labels.copy(),
        answer_aliases=answer_hop.answer_aliases.copy(),
        date_property_pid=answer_hop.date_property_pid,
        date_value=answer_hop.date_value,
        target_time=answer_hop.target_time,
        canonical_question=canonical_question,
        ambiguity_status=answer_hop.ambiguity_status,
        disambiguation_signature=answer_hop.disambiguation_signature.copy(),
        competitor_qids=answer_hop.competitor_qids.copy(),
        newness_metadata=answer_hop.newness_metadata.copy(),
        reasoning_style=HIDDEN_ENTITY_REASONING_STYLE,
        hop_count=2,
        reasoning_path=[
            build_reasoning_hop(
                source_qid=clue_source_qid,
                source_label=clue_source_label,
                property_pid=clue_hop.target_property_pid,
                property_label=clue_hop.target_property_label,
                target_qid=clue_target_qid,
                target_label=clue_target_label,
                role="clue",
            ),
            build_reasoning_hop(
                source_qid=answer_hop.subject_qid,
                source_label=answer_hop.subject_label,
                property_pid=answer_hop.target_property_pid,
                property_label=answer_hop.target_property_label,
                target_qid=_first_answer_qid(answer_hop),
                target_label=answer_label,
                role="answer",
            ),
        ],
        bridge_entities=[
            {"qid": answer_hop.subject_qid, "label": answer_hop.subject_label, "role": "hidden_entity"}
        ],
        derivation_signature={
            "style": HIDDEN_ENTITY_REASONING_STYLE,
            "rule": "validated_single_hop_hidden_entity_composition",
            "answer_template_key": answer_template.template_key,
            "clue_template_key": clue_template.template_key,
            "answer_property_pid": answer_hop.target_property_pid,
            "clue_property_pid": clue_hop.target_property_pid,
            "clue_orientation": clue_orientation,
        },
        provenance_complete=True,
        subject_resource_url=answer_hop.subject_resource_url,
        subject_resource_key=answer_hop.subject_resource_key,
        source_metadata=source_metadata,
    )
    attach_hidden_entity_seed_metadata(composed)
    return composed


def _drop_ambiguous_clue_paths(candidates: list[CandidateFact]) -> list[CandidateFact]:
    hidden_by_key: dict[tuple[str, ...], set[str]] = {}
    for candidate in candidates:
        key = _clue_uniqueness_key(candidate)
        hidden_by_key.setdefault(key, set()).add(candidate.subject_qid)
    return [
        candidate
        for candidate in candidates
        if len(hidden_by_key.get(_clue_uniqueness_key(candidate), set())) == 1
    ]


def _clue_uniqueness_key(candidate: CandidateFact) -> tuple[str, ...]:
    metadata = candidate.source_metadata
    answer_hop = metadata.get("answer_hop", {})
    clue_hop = metadata.get("clue_hop", {})
    visible_clue = metadata.get("visible_clue", {})
    return (
        str(answer_hop.get("template_key", "")),
        candidate.target_property_pid,
        str(metadata.get("clue_orientation", "")),
        str(clue_hop.get("template_key", "")),
        str(clue_hop.get("property_pid", "")),
        str(visible_clue.get("qid") or visible_clue.get("value") or visible_clue.get("label") or ""),
    )


def _usable_single_hop(candidate: CandidateFact) -> bool:
    return (
        normalize_reasoning_style(candidate.reasoning_style) == "single_fact"
        and candidate.provenance_complete
        and bool(candidate.subject_qid)
        and bool(candidate.subject_label)
        and len(candidate.answer_qids) == 1
        and len(candidate.answer_labels) == 1
    )


def _first_answer_qid(candidate: CandidateFact) -> str:
    return candidate.answer_qids[0] if candidate.answer_qids else ""


def _visible_clue(
    answer_hop: CandidateFact,
    clue_hop: CandidateFact,
    clue_orientation: str,
) -> dict[str, Any] | None:
    if clue_orientation == CLUE_HIDDEN_SUBJECT:
        if clue_hop.subject_qid != answer_hop.subject_qid:
            return None
        return {
            "qid": _first_answer_qid(clue_hop),
            "label": clue_hop.answer_labels[0] if clue_hop.answer_labels else "",
            "aliases": clue_hop.answer_aliases.copy(),
            "role": "clue_object",
        }
    if clue_orientation == CLUE_HIDDEN_OBJECT:
        if _first_answer_qid(clue_hop) != answer_hop.subject_qid:
            return None
        return {
            "qid": clue_hop.subject_qid,
            "label": clue_hop.subject_label,
            "aliases": clue_hop.subject_aliases.copy(),
            "role": "clue_subject",
        }
    return None


def _visible_clue_aliases_answer(visible_clue: dict[str, Any], answer_hop: CandidateFact) -> bool:
    clue_values = [visible_clue.get("label", ""), *visible_clue.get("aliases", [])]
    answer_values = [*answer_hop.answer_labels, *answer_hop.answer_aliases]
    normalized_answers = {
        normalize_name(str(value))
        for value in answer_values
        if normalize_name(str(value))
    }
    return any(normalize_name(str(value)) in normalized_answers for value in clue_values)


def _hop_metadata(candidate: CandidateFact, template: DomainTemplate) -> dict[str, Any]:
    return {
        "template_key": template.template_key,
        "subject_qid": candidate.subject_qid,
        "subject_label": candidate.subject_label,
        "property_pid": candidate.target_property_pid,
        "property_label": candidate.target_property_label,
        "answer_qids": candidate.answer_qids.copy(),
        "answer_labels": candidate.answer_labels.copy(),
        "answer_aliases": candidate.answer_aliases.copy(),
        "answer_type": candidate.answer_type,
        "subject_type_label": template.subject_type_label,
    }


def _required_reasoning_clues(clue_hop: CandidateFact, visible_label: str) -> list[str]:
    clues = []
    for clue in (clue_hop.target_property_label, visible_label):
        normalized = normalize_name(clue)
        if normalized and normalized not in {normalize_name(value) for value in clues}:
            clues.append(clue)
    return clues


def _build_hidden_entity_canonical_question(
    *,
    answer_hop: CandidateFact,
    answer_template: DomainTemplate,
    clue_hop: CandidateFact,
    clue_orientation: str,
    visible_label: str,
) -> str:
    wh = _wh_phrase(answer_hop.answer_type)
    subject_kind = str(
        answer_hop.source_metadata.get("question_format_args", {}).get(
            "subject_kind",
            answer_template.subject_type_label,
        )
    ).strip() or answer_template.subject_type_label
    answer_relation = answer_hop.target_property_label
    clue_relation = clue_hop.target_property_label
    if clue_orientation == CLUE_HIDDEN_OBJECT:
        return f"{wh} was the {answer_relation} of the {subject_kind} that was the {clue_relation} of {visible_label}?"
    return f"{wh} was the {answer_relation} of the {subject_kind} whose {clue_relation} was {visible_label}?"


def _wh_phrase(answer_type: str) -> str:
    if answer_type == "Person":
        return "Who"
    if answer_type == "Place":
        return "Which place"
    if answer_type == "Date":
        return "When"
    return "What"
