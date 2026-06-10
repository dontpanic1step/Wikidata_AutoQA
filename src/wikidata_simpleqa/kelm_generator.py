"""KELM-backed half-pipeline candidate generator."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .date_reference import format_date_answer, format_date_year, parse_date_answer
from .generation_models import EntityReference, EvidenceRecord, GeneratedCandidate
from .models import CandidateFact
from .subject_resources import canonical_subject_resource
from .wikidata_client import WikidataClient

PAREN_LABEL_PATTERN = re.compile(r"\s*\(\s*(?P<inner>[^)]+?)\s*\)\s*")

SUPPORTED_RELATIONS: dict[str, dict[str, str]] = {
    "date of birth": {
        "property_pid": "P569",
        "answer_type": "Date",
    },
    "date of death": {
        "property_pid": "P570",
        "answer_type": "Date",
    },
    "inception": {
        "property_pid": "P571",
        "answer_type": "Date",
    },
    "educated at": {
        "property_pid": "P69",
        "answer_type": "Organization",
    },
    "narrator": {
        "property_pid": "P2438",
        "answer_type": "Person",
    },
    "taxon rank": {
        "property_pid": "P105",
        "answer_type": "Entity",
    },
}


@dataclass(slots=True)
class KELMTSVGenerator:
    """Generate shared candidates from a small slice of KELM TSV rows."""

    input_path: Path
    record_limit: int = 10
    route_name: str = "kelm_bootstrap_half_pipeline"
    source_type: str = "external_kelm"

    def generate(self, *, client: WikidataClient, run_date: str) -> list[GeneratedCandidate]:
        """Extract a small set of KELM records and turn them into shared candidates."""
        generated: list[GeneratedCandidate] = []
        with self.input_path.open(encoding="utf-8") as handle:
            for index, line in enumerate(handle):
                if index >= self.record_limit:
                    break
                payload = json.loads(line)
                candidate, rejection_reason = self._build_candidate(payload, client=client, run_date=run_date)
                if candidate is None:
                    generated.append(
                        self._build_rejected_placeholder(
                            payload=payload,
                            reason=rejection_reason,
                        )
                    )
                    continue
                generated.append(candidate)
        return generated

    def _build_candidate(
        self,
        payload: dict[str, Any],
        *,
        client: WikidataClient,
        run_date: str,
    ) -> tuple[GeneratedCandidate | None, str]:
        """Build one candidate from a KELM JSON row."""
        triple = _select_supported_triple(payload.get("triples", []))
        if triple is None:
            return None, "unsupported_relation_record"
        subject_text, relation_text, answer_text = triple
        relation_spec = SUPPORTED_RELATIONS[relation_text]

        subject_resolution = _resolve_wikidata_entity(subject_text, client=client)
        if subject_resolution is None:
            return None, "entity_grounding_failed"

        answer_resolution = _resolve_answer_entity(
            relation_text=relation_text,
            answer_text=answer_text,
            client=client,
        )
        if answer_resolution is None:
            return None, "entity_grounding_failed"

        answer_aliases = [answer_text] if answer_resolution.qid.startswith("VALUE:") else []
        subject_resource_url, subject_resource_key = canonical_subject_resource(
            subject_resolution.qid,
            subject_resolution.entity_payload,
        )
        source_candidate = CandidateFact(
            subject_qid=subject_resolution.qid,
            subject_label=subject_resolution.name,
            subject_aliases=subject_resolution.aliases,
            domain=f"kelm_{relation_text.replace(' ', '_')}",
            topic="KELM bootstrap",
            answer_type=relation_spec["answer_type"],
            question_family=f"kelm_{relation_text.replace(' ', '_')}",
            subject_type_qids=[],
            target_property_pid=relation_spec["property_pid"],
            target_property_label=relation_text,
            answer_qids=[answer_resolution.qid],
            answer_labels=[answer_resolution.name],
            answer_aliases=answer_aliases,
            date_property_pid=relation_spec["property_pid"],
            date_value=_normalize_date_value(answer_text),
            target_time=run_date[:4],
            canonical_question="",
            ambiguity_status="kelm_grounded",
            provenance_complete=True,
            subject_resource_url=subject_resource_url,
            subject_resource_key=subject_resource_key,
            source_metadata={
                "wikidata_access_date": run_date,
                "retrieval_method": "KELM TSV + wbsearchentities + wbgetentities",
                "subject_wikipedia_title": subject_resolution.wikipedia_title,
                "subject_wikipedia_url": subject_resolution.url,
                "subject_sitelink_count": subject_resolution.sitelink_count,
                "subject_claim_count": subject_resolution.claim_count,
                "stable_answer_override": relation_text in {"date of birth", "date of death", "inception", "educated at", "narrator", "taxon rank"},
                "kelm_sentence": str(payload.get("sentence", "")).strip(),
                "kelm_serialized_triples": str(payload.get("serialized_triples", "")).strip(),
            },
        )
        return GeneratedCandidate(
            source_type=self.source_type,
            generation_route=self.route_name,
            question="",
            canonical_question="",
            answer=answer_resolution.name,
            answer_aliases=answer_aliases,
            subject_entity=EntityReference(
                name=subject_resolution.name,
                qid=subject_resolution.qid,
                wikipedia_title=subject_resolution.wikipedia_title,
                url=subject_resolution.url or subject_resource_url,
            ),
            answer_entity=EntityReference(
                name=answer_resolution.name,
                qid=answer_resolution.qid,
                wikipedia_title=answer_resolution.wikipedia_title,
                url=answer_resolution.url,
            ),
            relation_or_claim=relation_text,
            evidence=EvidenceRecord(
                text=str(payload.get("sentence", "")).strip(),
                url=subject_resolution.url,
                source_title=subject_resolution.wikipedia_title or subject_resolution.name,
                section="kelm_sentence",
                retrieved_at=run_date,
            ),
            answer_type=relation_spec["answer_type"],
            topic="KELM bootstrap",
            target_time=run_date[:4],
            source_metadata=source_candidate.source_metadata.copy(),
            source_candidate=source_candidate,
        ), ""

    def _build_rejected_placeholder(self, *, payload: dict[str, Any], reason: str) -> GeneratedCandidate:
        """Build a placeholder candidate so shared rejection output still records the row."""
        sentence = str(payload.get("sentence", "")).strip()
        return GeneratedCandidate(
            source_type=self.source_type,
            generation_route=self.route_name,
            question="",
            canonical_question="",
            answer="",
            answer_aliases=[],
            subject_entity=EntityReference(name=""),
            answer_entity=EntityReference(name=""),
            relation_or_claim="",
            evidence=EvidenceRecord(
                text=sentence,
                retrieved_at="",
            ),
            topic="KELM bootstrap",
            notes=[reason],
            source_metadata={
                "kelm_sentence": sentence,
                "kelm_serialized_triples": str(payload.get("serialized_triples", "")).strip(),
            },
        )


@dataclass(slots=True)
class _ResolvedEntity:
    """One resolved Wikidata entity."""

    name: str
    qid: str
    aliases: list[str]
    wikipedia_title: str
    url: str
    sitelink_count: int
    claim_count: int
    entity_payload: dict[str, Any]


def _select_supported_triple(triples: list[list[str]]) -> tuple[str, str, str] | None:
    """Return the first supported simple triple from one KELM row."""
    for triple in triples:
        if len(triple) != 3:
            continue
        subject_text, relation_text, answer_text = (str(value).strip() for value in triple)
        if relation_text in SUPPORTED_RELATIONS:
            return subject_text, relation_text, answer_text
    return None


def _resolve_wikidata_entity(name: str, *, client: WikidataClient) -> _ResolvedEntity | None:
    """Resolve a named entity using wbsearchentities followed by wbgetentities."""
    query, parenthetical = _normalize_search_label(name)
    mapping_key = f"{query}\n{parenthetical}"
    cached_payload = client.load_text_mapping("kelm_entity_resolution", mapping_key)
    if cached_payload is not None:
        return _resolved_entity_from_payload(cached_payload)
    search_results = client.search_entities(query, limit=5)
    exact_match = _pick_exact_match(search_results, query, parenthetical=parenthetical)
    if exact_match is None:
        return None
    entity_payload = client.get_entities([exact_match["id"]]).get(exact_match["id"], {})
    sitelinks = entity_payload.get("sitelinks", {})
    wikipedia_title = str(sitelinks.get("enwiki", {}).get("title", "")).strip()
    aliases = [
        str(alias.get("value", "")).strip()
        for alias in entity_payload.get("aliases", {}).get("en", [])
        if str(alias.get("value", "")).strip()
    ]
    resolved = _ResolvedEntity(
        name=str(entity_payload.get("labels", {}).get("en", {}).get("value", exact_match.get("label", query))).strip(),
        qid=str(exact_match["id"]),
        aliases=aliases,
        wikipedia_title=wikipedia_title,
        url="https://en.wikipedia.org/wiki/" + wikipedia_title.replace(" ", "_") if wikipedia_title else "",
        sitelink_count=len(sitelinks) if isinstance(sitelinks, dict) else 0,
        claim_count=sum(
            len(rows)
            for rows in entity_payload.get("claims", {}).values()
            if isinstance(rows, list)
        ),
        entity_payload=entity_payload,
    )
    client.store_text_mapping(
        "kelm_entity_resolution",
        mapping_key,
        {
            "name": resolved.name,
            "qid": resolved.qid,
            "aliases": resolved.aliases,
            "wikipedia_title": resolved.wikipedia_title,
            "url": resolved.url,
            "sitelink_count": resolved.sitelink_count,
            "claim_count": resolved.claim_count,
            "entity_payload": resolved.entity_payload,
        },
    )
    return resolved


def _resolve_answer_entity(
    *,
    relation_text: str,
    answer_text: str,
    client: WikidataClient,
) -> _ResolvedEntity | EntityReference | None:
    """Resolve an answer entity or build a literal answer reference."""
    if relation_text in {"date of birth", "date of death", "inception"}:
        return EntityReference(
            name=_render_date_answer(answer_text, relation_text=relation_text),
            qid=f"VALUE:date:{_normalize_date_value(answer_text)}",
        )
    resolved = _resolve_wikidata_entity(answer_text, client=client)
    if resolved is not None:
        return resolved
    if relation_text == "taxon rank":
        return EntityReference(name=answer_text, qid=f"VALUE:string:{answer_text}")
    return None


def _pick_exact_match(
    search_results: list[dict[str, Any]],
    query: str,
    *,
    parenthetical: str,
) -> dict[str, Any] | None:
    """Choose one exact or description-backed entity match conservatively."""
    normalized_query = _normalize_name(query)
    normalized_parenthetical = _normalize_name(parenthetical)
    exact_matches = [
        result
        for result in search_results
        if _normalize_name(str(result.get("label", ""))) == normalized_query
    ]
    if len(exact_matches) == 1:
        return exact_matches[0]
    if exact_matches and normalized_parenthetical:
        for result in exact_matches:
            description = _normalize_name(str(result.get("description", "")))
            if normalized_parenthetical and normalized_parenthetical in description:
                return result
    return None


def _normalize_search_label(text: str) -> tuple[str, str]:
    """Return a search label and extracted parenthetical hint."""
    cleaned = " ".join(text.replace("Â", " ").split())
    match = PAREN_LABEL_PATTERN.search(cleaned)
    if not match:
        return cleaned, ""
    inner = " ".join(match.group("inner").split())
    base = PAREN_LABEL_PATTERN.sub("", cleaned).strip()
    return base, inner


def _resolved_entity_from_payload(payload: dict[str, Any]) -> _ResolvedEntity:
    """Build one resolved entity from a cached payload."""
    return _ResolvedEntity(
        name=str(payload.get("name", "")).strip(),
        qid=str(payload.get("qid", "")).strip(),
        aliases=[
            str(alias).strip()
            for alias in payload.get("aliases", [])
            if str(alias).strip()
        ],
        wikipedia_title=str(payload.get("wikipedia_title", "")).strip(),
        url=str(payload.get("url", "")).strip(),
        sitelink_count=int(payload.get("sitelink_count", 0) or 0),
        claim_count=int(payload.get("claim_count", 0) or 0),
        entity_payload=dict(payload.get("entity_payload", {})),
    )


def _normalize_name(text: str) -> str:
    """Normalize one label for exact-match comparisons."""
    return " ".join(text.lower().split())


def _normalize_date_value(text: str) -> str:
    """Return an ISO-like normalized date fallback for literal date answers."""
    parts = parse_date_answer(text)
    if parts is not None:
        signed_year = f"-{parts.year}" if parts.era in {"BC", "BCE"} else str(parts.year)
        return f"{signed_year}-{parts.month or 1:02d}-{parts.day or 1:02d}"
    return "1900-01-01"


def _render_date_answer(text: str, *, relation_text: str) -> str:
    """Return a human-readable answer string for one date literal."""
    date_parts = parse_date_answer(text)
    if date_parts is not None:
        if relation_text == "inception":
            return format_date_year(date_parts)
        return format_date_answer(date_parts)
    normalized = " ".join(text.split()).replace(",", "")
    parts = normalized.split()
    if relation_text == "inception" and parts:
        return parts[-1]
    if len(parts) == 1 and parts[0].isdigit():
        return parts[0]
    return normalized
