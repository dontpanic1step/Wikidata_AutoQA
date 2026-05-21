"""Candidate generators for the staged multi-generator pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .canonical_questions import build_canonical_question
from .candidate_harvester import harvest_candidates
from .generation_models import EntityReference, EvidenceRecord, GeneratedCandidate
from .models import CandidateFact, DomainTemplate
from .reasoning import normalize_reasoning_style
from .route4_two_hop import (
    ROUTE4_WIKIDATA_TWO_HOP_ROUTE,
    Route4TwoHopComposer,
    get_route4_two_hop_single_hop_templates,
)
from .route1_validators import validate_route1_candidate
from .route1_multihop import ROUTE1_MULTIHOP_JOIN_ROUTE, attach_seed_metadata
from .wikipedia_client import WikipediaClient


@dataclass(slots=True)
class CandidateGenerator:
    """Abstract generator contract for the new pipeline."""

    route_name: str
    source_type: str

    def generate(
        self,
        *,
        templates: Iterable[DomainTemplate],
        settings,
        client,
    ) -> list[GeneratedCandidate]:
        """Generate route-specific candidates."""
        raise NotImplementedError


@dataclass(slots=True)
class WikidataLightGenerator(CandidateGenerator):
    """Baseline Route 1 generator using Wikidata-derived candidates."""

    route_name: str = "route1_wikidata_light"
    source_type: str = "wikidata"

    def generate(
        self,
        *,
        templates: Iterable[DomainTemplate],
        settings,
        client,
    ) -> list[GeneratedCandidate]:
        generated: list[GeneratedCandidate] = []
        for template in templates:
            for raw_candidate in harvest_candidates(client=client, settings=settings, template=template):
                prepared = _prepare_candidate_fact(
                    client=client,
                    settings=settings,
                    template=template,
                    candidate=raw_candidate,
                )
                if prepared is None:
                    continue
                generated.append(
                    _build_generated_candidate(
                        candidate=prepared,
                        template=template,
                        route_name=self.route_name,
                        source_type=self.source_type,
                        evidence=EvidenceRecord(
                            text=(
                                f"{prepared.subject_label} {template.target_property_label} "
                                f"{prepared.answer_labels[0] if prepared.answer_labels else ''}"
                            ).strip(),
                            url=prepared.subject_resource_url,
                            source_title=prepared.subject_label,
                            section="wikidata_statement",
                            retrieved_at=settings.run_date,
                        ),
                    )
                )
        return generated


@dataclass(slots=True)
class WikidataMultiHopJoinGenerator(CandidateGenerator):
    """Route 1 QID-first multi-hop join generator."""

    route_name: str = ROUTE1_MULTIHOP_JOIN_ROUTE
    source_type: str = "wikidata"

    def generate(
        self,
        *,
        templates: Iterable[DomainTemplate],
        settings,
        client,
    ) -> list[GeneratedCandidate]:
        generated: list[GeneratedCandidate] = []
        for template in templates:
            reasoning_style = normalize_reasoning_style(
                template.reasoning_style or template.composition_style
            )
            if reasoning_style != "multi_hop_join":
                continue
            if template.answer_format == "number" or template.answer_type == "Number":
                continue
            for raw_candidate in harvest_candidates(client=client, settings=settings, template=template):
                raw_candidate.reasoning_style = normalize_reasoning_style(raw_candidate.reasoning_style)
                if raw_candidate.reasoning_style != "multi_hop_join":
                    continue
                attach_seed_metadata(raw_candidate, template)
                prepared = _prepare_candidate_fact(
                    client=client,
                    settings=settings,
                    template=template,
                    candidate=raw_candidate,
                )
                if prepared is None:
                    continue
                generated.append(
                    _build_generated_candidate(
                        candidate=prepared,
                        template=template,
                        route_name=self.route_name,
                        source_type=self.source_type,
                        evidence=_build_wikidata_join_evidence(prepared, settings.run_date),
                    )
                )
        return generated


@dataclass(slots=True)
class WikidataHiddenEntityTwoHopGenerator(CandidateGenerator):
    """Route 4 two-hop generator composed from validated single-hop facts."""

    route_name: str = ROUTE4_WIKIDATA_TWO_HOP_ROUTE
    source_type: str = "wikidata"
    composer: Route4TwoHopComposer = field(default_factory=Route4TwoHopComposer)

    def generate(
        self,
        *,
        templates: Iterable[DomainTemplate],
        settings,
        client,
    ) -> list[GeneratedCandidate]:
        single_hop_templates = get_route4_two_hop_single_hop_templates(templates)
        template_by_key = {template.template_key: template for template in single_hop_templates}
        prepared_by_template: dict[str, list[CandidateFact]] = {}
        for template in single_hop_templates:
            prepared_by_template[template.template_key] = []
            for raw_candidate in harvest_candidates(client=client, settings=settings, template=template):
                raw_candidate.reasoning_style = normalize_reasoning_style(raw_candidate.reasoning_style)
                if raw_candidate.reasoning_style != "single_fact":
                    continue
                prepared = _prepare_candidate_fact(
                    client=client,
                    settings=settings,
                    template=template,
                    candidate=raw_candidate,
                )
                if prepared is not None:
                    prepared_by_template[template.template_key].append(prepared)

        composed_candidates = self.composer.compose(prepared_by_template, template_by_key)
        return [
            _build_generated_candidate(
                candidate=candidate,
                template=template_by_key[candidate.source_metadata["answer_hop"]["template_key"]],
                route_name=self.route_name,
                source_type=self.source_type,
                evidence=_build_wikidata_join_evidence(candidate, settings.run_date),
            )
            for candidate in composed_candidates
        ]


@dataclass(slots=True, kw_only=True)
class WikidataWikipediaHybridGenerator(CandidateGenerator):
    """Primary Route 2 generator with Wikipedia-backed evidence."""

    wikipedia_client: WikipediaClient
    route_name: str = "route2_wikidata_wikipedia_hybrid"
    source_type: str = "hybrid"

    def generate(
        self,
        *,
        templates: Iterable[DomainTemplate],
        settings,
        client,
    ) -> list[GeneratedCandidate]:
        generated: list[GeneratedCandidate] = []
        for template in templates:
            for raw_candidate in harvest_candidates(client=client, settings=settings, template=template):
                prepared = _prepare_candidate_fact(
                    client=client,
                    settings=settings,
                    template=template,
                    candidate=raw_candidate,
                )
                if prepared is None:
                    continue
                title = str(prepared.source_metadata.get("subject_wikipedia_title", "")).strip()
                if not title:
                    continue
                summary = self.wikipedia_client.fetch_summary(title)
                evidence = _build_wikipedia_evidence(summary, settings.run_date)
                if not evidence.text:
                    continue
                subject_kind_override = _extract_subject_kind_from_summary(
                    title=title,
                    summary_text=evidence.text,
                )
                if subject_kind_override:
                    prepared.source_metadata.setdefault("question_format_args", {})["subject_kind"] = subject_kind_override
                    descriptor = prepared.source_metadata.get("question_format_args", {}).get(
                        "descriptor",
                        prepared.subject_label,
                    )
                    prepared.canonical_question = template.canonical_question_template.format(
                        descriptor=descriptor,
                        subject_kind=subject_kind_override,
                    )
                generated.append(
                    _build_generated_candidate(
                        candidate=prepared,
                        template=template,
                        route_name=self.route_name,
                        source_type=self.source_type,
                        evidence=evidence,
                    )
                )
        return generated


def _prepare_candidate_fact(
    *,
    client,
    settings,
    template: DomainTemplate,
    candidate: CandidateFact,
) -> CandidateFact | None:
    """Validate one harvested candidate and attach a canonical question."""
    resolution = validate_route1_candidate(client, settings, candidate, template)
    if not hasattr(resolution, "descriptor"):
        return None
    candidate.ambiguity_status = resolution.status
    candidate.disambiguation_signature = resolution.signature
    candidate.competitor_qids = resolution.competitor_qids
    candidate.source_metadata.setdefault("question_format_args", {})["descriptor"] = resolution.descriptor
    candidate.canonical_question = build_canonical_question(candidate, template, resolution)
    return candidate


def _build_generated_candidate(
    *,
    candidate: CandidateFact,
    template: DomainTemplate,
    route_name: str,
    source_type: str,
    evidence: EvidenceRecord,
) -> GeneratedCandidate:
    """Convert one prepared CandidateFact into the shared GeneratedCandidate."""
    subject_wikipedia_title = str(candidate.source_metadata.get("subject_wikipedia_title", "")).strip()
    subject_wikipedia_url = str(candidate.source_metadata.get("subject_wikipedia_url", "")).strip()
    return GeneratedCandidate(
        source_type=source_type,
        generation_route=route_name,
        question=candidate.canonical_question or candidate.subject_label,
        canonical_question=candidate.canonical_question or candidate.subject_label,
        answer=candidate.answer_labels[0] if candidate.answer_labels else "",
        answer_aliases=candidate.answer_aliases.copy(),
        subject_entity=EntityReference(
            name=candidate.subject_label,
            qid=candidate.subject_qid,
            wikipedia_title=subject_wikipedia_title,
            url=subject_wikipedia_url or candidate.subject_resource_url,
        ),
        answer_entity=EntityReference(
            name=candidate.answer_labels[0] if candidate.answer_labels else "",
            qid=candidate.answer_qids[0] if candidate.answer_qids else "",
        ),
        relation_or_claim=template.target_property_label,
        evidence=evidence,
        question_family=candidate.question_family,
        answer_type=candidate.answer_type,
        topic=candidate.topic,
        target_time=candidate.target_time,
        source_template_domain=candidate.domain or template.domain,
        source_metadata=candidate.source_metadata.copy(),
        source_candidate=candidate,
    )


def _build_wikipedia_evidence(summary: dict, retrieved_at: str) -> EvidenceRecord:
    """Build one evidence record from a MediaWiki summary payload."""
    text = str(summary.get("extract", "")).strip()
    page_url = (
        summary.get("content_urls", {})
        .get("desktop", {})
        .get("page", "")
    )
    return EvidenceRecord(
        text=text,
        url=str(page_url),
        source_title=str(summary.get("title", "")).strip(),
        section="summary",
        retrieved_at=retrieved_at,
    )


def _build_wikidata_join_evidence(candidate: CandidateFact, retrieved_at: str) -> EvidenceRecord:
    """Build compact evidence text from a validated Wikidata multi-hop path."""
    hop_text = []
    for hop in candidate.reasoning_path:
        source = str(hop.get("source_label", "")).strip()
        relation = str(hop.get("property_label", "")).strip()
        target = str(hop.get("target_label", "")).strip()
        if source and relation and target:
            hop_text.append(f"{source} -- {relation} -- {target}")
    text = "; ".join(hop_text).strip()
    if not text:
        text = (
            f"{candidate.subject_label} {candidate.target_property_label} "
            f"{candidate.answer_labels[0] if candidate.answer_labels else ''}"
        ).strip()
    return EvidenceRecord(
        text=text,
        url=candidate.subject_resource_url,
        source_title=candidate.subject_label,
        section="wikidata_multi_hop_join",
        retrieved_at=retrieved_at,
    )


def _extract_subject_kind_from_summary(*, title: str, summary_text: str) -> str:
    """Extract a conservative subject-kind phrase from one summary sentence."""
    normalized_title = title.replace("_", " ").strip()
    prefixes = (
        f"{normalized_title} is a ",
        f"{normalized_title} is an ",
        f"{normalized_title} is the ",
    )
    lowered_summary = summary_text.strip()
    for prefix in prefixes:
        if lowered_summary.startswith(prefix):
            remainder = lowered_summary[len(prefix):]
            descriptor = remainder
            for boundary in (" directed by ", " written by ", " created by ", " published by ", ",", " that ", " which "):
                descriptor = descriptor.split(boundary, 1)[0]
            descriptor = descriptor.strip(" .")
            words = descriptor.split()
            if not words:
                return ""
            filtered_words = [word for word in words if not word.isdigit()]
            if not filtered_words:
                filtered_words = words
            if len(filtered_words) > 4:
                filtered_words = filtered_words[-4:]
            return " ".join(filtered_words).strip()
    return ""
