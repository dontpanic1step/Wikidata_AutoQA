"""Deterministic validators for single-fact and compositional multi-hop candidates."""

from __future__ import annotations

import re
from datetime import date
from typing import Iterable

from .constants import MONTH_NAMES, TEMPORAL_PHRASES
from .date_reference import date_answer_sort_key
from .entity_normalization import normalize_name
from .geographic_leakage import question_leaks_geographic_answer_context
from .models import CandidateFact, DomainTemplate
from .reasoning import is_multi_hop_reasoning_style, normalize_reasoning_style
from .text_normalization import text_contains_any

YEAR_PATTERN = re.compile(r"\b(17|18|19|20|21)\d{2}\b")
DATE_PATTERN = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
MONTH_PATTERN = re.compile(r"\b(" + "|".join(MONTH_NAMES) + r")\b", re.IGNORECASE)
TEMPORAL_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(phrase) for phrase in TEMPORAL_PHRASES) + r")\b",
    re.IGNORECASE,
)

MUTABLE_ROLE_PROPERTY_PIDS = {
    "P26",   # spouse
    "P39",   # position held
    "P54",   # member of sports team
    "P102",  # member of political party
    "P108",  # employer
    "P169",  # chief executive officer
    "P1037", # director / manager
}

HIGH_RISK_STATISTIC_PROPERTY_PIDS = {
    "P1351",  # number of points/goals/set scored
}

MUTABLE_OR_HIGH_RISK_PROPERTY_PIDS = MUTABLE_ROLE_PROPERTY_PIDS | HIGH_RISK_STATISTIC_PROPERTY_PIDS | {
    "P106",   # occupation
    "P136",   # genre
    "P161",   # cast member
    "P162",   # producer
    "P166",   # award received
    "P400",   # platform
    "P1082",  # population
    "P1128",  # employees
}

LOCATION_TOKEN_STOPWORDS = {
    "administrative",
    "area",
    "borough",
    "campus",
    "canton",
    "city",
    "country",
    "county",
    "district",
    "federal",
    "governorate",
    "island",
    "islands",
    "kingdom",
    "municipality",
    "north",
    "northern",
    "oblast",
    "park",
    "province",
    "railway",
    "region",
    "republic",
    "south",
    "southern",
    "state",
    "station",
    "territorial",
    "town",
    "united",
    "west",
}

LIVE_STATUS_TEMPORAL_PATTERN = re.compile(
    r"\b("
    r"this year|last year|next year|current|currently|latest|most recent|newest|recent|recently|as of|as of now"
    r")\b",
    re.IGNORECASE,
)


def has_forbidden_temporal_text(text: str) -> bool:
    """Return whether text contains forbidden temporal content."""
    if YEAR_PATTERN.search(text) or DATE_PATTERN.search(text):
        return True
    return bool(TEMPORAL_PATTERN.search(text))


def has_year(text: str) -> bool:
    """Return whether text contains a year token."""
    return bool(YEAR_PATTERN.search(text))


def violates_cutoff_year_policy(text: str, cutoff_year: int) -> bool:
    """Return whether text violates the route-level cutoff-year policy."""
    if LIVE_STATUS_TEMPORAL_PATTERN.search(text):
        return True
    years = [int(match.group(0)) for match in YEAR_PATTERN.finditer(text)]
    return any(year >= cutoff_year for year in years)


def is_settled_by_run_date(date_value: str, run_date: str) -> bool:
    """Return whether the candidate date is not in the future."""
    candidate_key = date_answer_sort_key(date_value)
    pipeline_key = date_answer_sort_key(run_date)
    if candidate_key is not None and pipeline_key is not None:
        return candidate_key <= pipeline_key
    candidate_date = date.fromisoformat(date_value[:10])
    pipeline_date = date.fromisoformat(run_date)
    return candidate_date <= pipeline_date


def candidate_is_time_invariant(candidate: CandidateFact, run_date: str) -> bool:
    """Return whether the candidate appears to be a settled, stable fact."""
    if not is_settled_by_run_date(candidate.date_value, run_date):
        return False
    if (
        candidate.target_property_pid in MUTABLE_OR_HIGH_RISK_PROPERTY_PIDS
        and not _allows_historically_settled_slice(candidate, candidate.target_property_pid)
    ):
        return False
    if is_multi_hop_reasoning_style(candidate.reasoning_style):
        for hop in candidate.reasoning_path:
            property_pid = hop.get("property_pid", "")
            if (
                property_pid in MUTABLE_OR_HIGH_RISK_PROPERTY_PIDS
                and not _allows_historically_settled_slice(candidate, property_pid)
            ):
                return False
    return True


def answer_is_unique(candidate: CandidateFact) -> bool:
    """Return whether the candidate has exactly one answer."""
    if len(set(candidate.answer_qids)) != 1 or len(candidate.answer_qids) != 1:
        return False
    return derivation_is_unique(candidate)


def derivation_is_unique(candidate: CandidateFact) -> bool:
    """Return whether the complete derivation resolves to a unique answer."""
    return bool(candidate.source_metadata.get("multi_hop_unique", True))


def find_exact_name_competitors(
    subject_qid: str,
    subject_label: str,
    search_results: Iterable[dict[str, str]],
) -> list[str]:
    """Return exact normalized-label competitors excluding the subject itself."""
    normalized_subject = normalize_name(subject_label)
    competitor_qids: list[str] = []
    for result in search_results:
        result_qid = result.get("id")
        result_label = result.get("label", "")
        if not result_qid or result_qid == subject_qid:
            continue
        if normalize_name(result_label) == normalized_subject:
            competitor_qids.append(result_qid)
    return competitor_qids


def question_leaks_answer(question: str, answer_labels: list[str]) -> bool:
    """Return whether the answer is visibly present in the question."""
    if text_contains_any(question, answer_labels):
        return True
    if question_leaks_geographic_answer_context(question, answer_labels):
        return True
    return False


def question_leaks_any_answer(
    question: str,
    answer_labels: list[str],
    answer_aliases: list[str],
) -> bool:
    """Return whether the question contains any answer label or alias."""
    return question_leaks_answer(question, answer_labels + answer_aliases)


def question_leaks_location_answer_context(question: str, candidate: CandidateFact) -> bool:
    """Return whether location context in the question makes the place answer too easy."""
    if candidate.target_property_pid != "P17":
        return False
    normalized_question = normalize_name(question)
    context_labels = candidate.source_metadata.get("subject_location_labels", [])
    context_labels += candidate.source_metadata.get("answer_subdivision_labels", [])
    if text_contains_any(question, context_labels):
        return True
    question_tokens = set(_tokenize_normalized_text(normalized_question))
    for token in _salient_location_tokens(context_labels):
        if token in question_tokens:
            return True
    return False


def candidate_matches_topic_constraints(
    candidate: CandidateFact,
    template: DomainTemplate,
) -> bool:
    """Return whether a candidate satisfies any required deterministic topic hints."""
    if not template.required_topic_keywords:
        return True
    evidence_texts = [
        candidate.subject_label,
        candidate.source_metadata.get("subject_description", ""),
    ]
    evidence_texts.extend(candidate.source_metadata.get("subject_type_labels", []))
    evidence_texts.extend(candidate.source_metadata.get("subject_main_subject_labels", []))
    normalized_evidence = " ".join(normalize_name(str(text)) for text in evidence_texts if text)
    if not normalized_evidence.strip():
        return False
    for keyword in template.required_topic_keywords:
        normalized_keyword = normalize_name(keyword)
        if normalized_keyword and normalized_keyword in normalized_evidence:
            return True
    return False


def question_leaks_bridge_entities(question: str, candidate: CandidateFact) -> bool:
    """Return whether the question exposes bridge entities that should stay latent."""
    if not is_multi_hop_reasoning_style(candidate.reasoning_style):
        return False
    if normalize_reasoning_style(candidate.reasoning_style) == "multi_hop_hidden_entity":
        return question_leaks_hidden_entities(question, candidate)
    if candidate.source_metadata.get("surface_bridge_entities", False):
        return False
    normalized_question = normalize_name(question)
    normalized_subject = normalize_name(candidate.subject_label)
    question_without_subject = normalized_question.replace(normalized_subject, " ")
    for bridge in candidate.bridge_entities:
        label = normalize_name(bridge.get("label", ""))
        if label and label == normalized_subject:
            continue
        if label and label in question_without_subject:
            return True
    return False


def question_leaks_hidden_entities(question: str, candidate: CandidateFact) -> bool:
    """Return whether a hidden-entity two-hop question exposes the hidden entity."""
    normalized_question = normalize_name(question)
    allowed_anchors = {
        normalize_name(str(value))
        for value in candidate.source_metadata.get("hidden_entity_disambiguation_anchors", [])
        if normalize_name(str(value))
    }
    hidden_entities = candidate.source_metadata.get("hidden_entities", [])
    if not isinstance(hidden_entities, list):
        hidden_entities = []
    values = [candidate.subject_label, *candidate.subject_aliases]
    for hidden in hidden_entities:
        if not isinstance(hidden, dict):
            continue
        values.append(str(hidden.get("label", "")))
        aliases = hidden.get("aliases", [])
        if isinstance(aliases, list):
            values.extend(str(alias) for alias in aliases)
    for value in values:
        normalized_value = normalize_name(str(value))
        if normalized_value in allowed_anchors:
            continue
        if normalized_value and normalized_value in normalized_question:
            return True
    return False


def preserves_required_anchors(question: str, anchors: list[str]) -> bool:
    """Return whether all required anchors survive in the rewritten question."""
    normalized_question = normalize_name(question)
    for anchor in anchors:
        normalized_anchor = normalize_name(anchor)
        if normalized_anchor and normalized_anchor not in normalized_question:
            return False
    return True


def reasoning_path_is_connected(candidate: CandidateFact) -> bool:
    """Return whether a multi-hop reasoning path is sequentially connected."""
    if not is_multi_hop_reasoning_style(candidate.reasoning_style):
        return True
    if normalize_reasoning_style(candidate.reasoning_style) == "multi_hop_hidden_entity":
        return _hidden_entity_reasoning_path_is_connected(candidate)
    if candidate.hop_count < 2 or len(candidate.reasoning_path) < 2:
        return False
    for current_hop, next_hop in zip(candidate.reasoning_path, candidate.reasoning_path[1:]):
        current_target_qid = current_hop.get("target_qid")
        next_source_qid = next_hop.get("source_qid")
        if current_target_qid is None or next_source_qid is None:
            return False
        if current_target_qid != next_source_qid:
            return False
    return True


def _hidden_entity_reasoning_path_is_connected(candidate: CandidateFact) -> bool:
    """Return whether hidden-entity hops both involve the hidden subject."""
    if candidate.hop_count != 2 or len(candidate.reasoning_path) != 2:
        return False
    hidden_qid = candidate.subject_qid
    if not hidden_qid:
        return False
    clue_hop = next((hop for hop in candidate.reasoning_path if hop.get("role") == "clue"), None)
    answer_hop = next((hop for hop in candidate.reasoning_path if hop.get("role") == "answer"), None)
    if clue_hop is None or answer_hop is None:
        return False
    answer_source_qid = answer_hop.get("source_qid")
    if answer_source_qid != hidden_qid:
        return False
    return clue_hop.get("source_qid") == hidden_qid or clue_hop.get("target_qid") == hidden_qid


def question_requires_all_hops(candidate: CandidateFact, question: str) -> bool:
    """Return whether the surfaced question preserves the required reasoning clues."""
    if not is_multi_hop_reasoning_style(candidate.reasoning_style):
        return True
    required_clues = candidate.source_metadata.get("required_reasoning_clues", [])
    normalized_question = normalize_name(question)
    return all(
        normalize_name(str(clue)) in normalized_question
        for clue in required_clues
        if normalize_name(str(clue))
    )


def shortcut_check(candidate: CandidateFact, question: str) -> dict[str, bool | str]:
    """Return structured anti-shortcut validation results."""
    if not is_multi_hop_reasoning_style(candidate.reasoning_style):
        return {"applies": False, "question_requires_all_hops": True, "shortcut_free": True}
    requires_all_hops = question_requires_all_hops(candidate, question)
    return {
        "applies": True,
        "question_requires_all_hops": requires_all_hops,
        "shortcut_free": requires_all_hops,
    }


def reasoning_path_is_temporally_safe(candidate: CandidateFact, *, cutoff_year: int = 2025) -> bool:
    """Return whether hop labels do not force temporal disambiguation."""
    check_temporal = has_forbidden_temporal_text
    if normalize_reasoning_style(candidate.reasoning_style) == "multi_hop_hidden_entity":
        check_temporal = lambda text: violates_cutoff_year_policy(text, cutoff_year)
    if check_temporal(candidate.subject_label):
        return False
    for hop in candidate.reasoning_path:
        if _hop_source_requires_temporal_ban(candidate, hop) and check_temporal(
            hop.get("source_label", "")
        ):
            return False
        if _hop_target_requires_temporal_ban(candidate, hop) and check_temporal(
            hop.get("target_label", "")
        ):
            return False
    return True


def _hop_target_requires_temporal_ban(candidate: CandidateFact, hop: dict[str, str]) -> bool:
    """Return whether a hop target label should be checked for temporal text."""
    if hop.get("role") == "bridge" and not candidate.source_metadata.get(
        "surface_bridge_entities",
        False,
    ):
        return False
    if candidate.answer_type != "Date":
        return True
    return hop.get("role") != "answer"


def _hop_source_requires_temporal_ban(candidate: CandidateFact, hop: dict[str, str]) -> bool:
    """Return whether a hop source label should be checked for temporal text."""
    source_qid = hop.get("source_qid")
    if source_qid == candidate.subject_qid:
        return False
    bridge_qids = {bridge.get("qid") for bridge in candidate.bridge_entities}
    if source_qid in bridge_qids and not candidate.source_metadata.get(
        "surface_bridge_entities",
        False,
    ):
        return False
    return hop.get("role") == "answer" or candidate.source_metadata.get(
        "surface_bridge_entities",
        False,
    )


def ordinal_candidate_is_safe(candidate: CandidateFact) -> bool:
    """Return whether an ordinal derivation has sufficient safety metadata."""
    if normalize_reasoning_style(candidate.reasoning_style) != "multi_hop_ordinal":
        return True
    ordinal_metadata = candidate.source_metadata.get("ordinal_metadata", {})
    if not ordinal_metadata:
        return False
    if not ordinal_metadata.get("series_history_complete", False):
        return False
    descriptor = ordinal_metadata.get("descriptor", "")
    if not descriptor or has_forbidden_temporal_text(descriptor):
        return False
    return True


def _allows_historically_settled_slice(candidate: CandidateFact, property_pid: str) -> bool:
    """Return whether a historically settled slice explicitly allows one risky property."""
    metadata = candidate.source_metadata.get("time_invariance", {})
    if not isinstance(metadata, dict):
        return False
    if not metadata.get("historically_settled", False):
        return False
    if not metadata.get("history_complete", False):
        return False
    allowed_pids = metadata.get("allowed_property_pids", [])
    if property_pid not in allowed_pids:
        return False
    return True


def reasoning_provenance_is_complete(candidate: CandidateFact) -> bool:
    """Return whether a candidate has a complete compositional provenance record."""
    if not is_multi_hop_reasoning_style(candidate.reasoning_style):
        return candidate.provenance_complete
    if not candidate.provenance_complete:
        return False
    if len(candidate.reasoning_path) != candidate.hop_count:
        return False
    return bool(candidate.derivation_signature)


def is_simple_question(question: str) -> bool:
    """Return whether the question looks like a short SimpleQA-style prompt."""
    lowered = question.lower()
    forbidden_patterns = ("and why", "explain", "compare", "list all")
    if any(pattern in lowered for pattern in forbidden_patterns):
        return False
    return len(question.strip()) <= 200


def _salient_location_tokens(labels: list[str]) -> set[str]:
    """Return conservative location tokens that would leak a country answer."""
    tokens: set[str] = set()
    for label in labels:
        for token in _tokenize_normalized_text(normalize_name(str(label))):
            if len(token) < 4:
                continue
            if token in LOCATION_TOKEN_STOPWORDS:
                continue
            tokens.add(token)
    return tokens


def _tokenize_normalized_text(text: str) -> list[str]:
    """Split normalized text into alphanumeric tokens."""
    return re.findall(r"[a-z0-9]+", text.lower())
