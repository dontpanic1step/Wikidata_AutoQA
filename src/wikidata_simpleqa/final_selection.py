"""Final accepted-record cleanup for review batches."""

from __future__ import annotations

import re
from collections import defaultdict, deque
from difflib import SequenceMatcher
from typing import Any

from .entity_normalization import normalize_name

TOKEN_PATTERN = re.compile(r"\b\w+\b")


def select_final_records(
    records: list[dict[str, Any]],
    *,
    target_count: int,
    similarity_threshold: float = 0.88,
    domain_key: str = "domain",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Deduplicate by similarity and rebalance records across available domains."""
    deduped, dedup_summary = deduplicate_similar_records(
        records,
        similarity_threshold=similarity_threshold,
    )
    selected = rebalance_records(
        deduped,
        target_count=target_count,
        domain_key=domain_key,
    )
    summary = {
        "input_count": len(records),
        "deduped_count": len(deduped),
        "selected_count": len(selected),
        "target_count": target_count,
        "similarity_threshold": similarity_threshold,
        "domain_key": domain_key,
        "deduplication": dedup_summary,
        "domain_counts": _domain_counts(selected, domain_key=domain_key),
    }
    return selected, summary


def deduplicate_similar_records(
    records: list[dict[str, Any]],
    *,
    similarity_threshold: float,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Drop near-duplicate questions and duplicate subject resources."""
    kept: list[dict[str, Any]] = []
    kept_signatures: list[tuple[str, set[str], str]] = []
    duplicate_reasons: list[dict[str, Any]] = []
    seen_subjects: set[str] = set()
    for record in records:
        subject_key = _subject_key(record)
        if subject_key and subject_key in seen_subjects:
            duplicate_reasons.append(
                {
                    "reason": "duplicate_subject_resource",
                    "question": record.get("question", ""),
                    "subject_key": subject_key,
                }
            )
            continue
        normalized_question, question_tokens = _question_signature(record)
        duplicate_reason = _similar_duplicate_reason(
            normalized_question,
            question_tokens,
            kept_signatures,
            threshold=similarity_threshold,
        )
        if duplicate_reason:
            duplicate_reasons.append(
                {
                    "reason": duplicate_reason,
                    "question": record.get("question", ""),
                    "subject_key": subject_key,
                }
            )
            continue
        kept.append(record)
        kept_signatures.append((normalized_question, question_tokens, subject_key))
        if subject_key:
            seen_subjects.add(subject_key)
    return kept, {
        "removed_count": len(duplicate_reasons),
        "removed_reasons": duplicate_reasons,
    }


def rebalance_records(
    records: list[dict[str, Any]],
    *,
    target_count: int,
    domain_key: str = "domain",
) -> list[dict[str, Any]]:
    """Round-robin records across available domain buckets."""
    if target_count <= 0:
        return []
    buckets: dict[str, deque[dict[str, Any]]] = defaultdict(deque)
    domain_order: list[str] = []
    for record in records:
        domain = _domain_value(record, domain_key=domain_key)
        if domain not in buckets:
            domain_order.append(domain)
        buckets[domain].append(record)
    selected: list[dict[str, Any]] = []
    active_domains = deque(sorted(domain_order, key=lambda value: (-len(buckets[value]), value)))
    while active_domains and len(selected) < target_count:
        domain = active_domains.popleft()
        bucket = buckets[domain]
        if bucket:
            selected.append(bucket.popleft())
        if bucket:
            active_domains.append(domain)
    return selected


def _similar_duplicate_reason(
    normalized_question: str,
    question_tokens: set[str],
    kept_signatures: list[tuple[str, set[str], str]],
    *,
    threshold: float,
) -> str:
    for kept_question, kept_tokens, _subject_key in kept_signatures:
        if normalized_question and normalized_question == kept_question:
            return "duplicate_question"
        if not normalized_question or not kept_question:
            continue
        sequence_ratio = SequenceMatcher(None, normalized_question, kept_question).ratio()
        token_ratio = _jaccard(question_tokens, kept_tokens)
        if max(sequence_ratio, token_ratio) >= threshold:
            return "similar_question"
    return ""


def _question_signature(record: dict[str, Any]) -> tuple[str, set[str]]:
    question = str(record.get("question") or record.get("rewritten_question") or "")
    normalized = normalize_name(question)
    tokens = {token for token in TOKEN_PATTERN.findall(normalized) if token}
    return normalized, tokens


def _subject_key(record: dict[str, Any]) -> str:
    subject_resource_key = str(record.get("subject_resource_key") or "").strip()
    if subject_resource_key:
        return subject_resource_key
    subject_entity = record.get("subject_entity", {})
    if isinstance(subject_entity, dict):
        return str(subject_entity.get("url") or subject_entity.get("qid") or subject_entity.get("wikipedia_title") or "").strip()
    return ""


def _domain_value(record: dict[str, Any], *, domain_key: str) -> str:
    value = str(record.get(domain_key) or "").strip()
    if value:
        return value
    metadata = record.get("source_metadata", {})
    if isinstance(metadata, dict):
        for key in ("content_domain", "domain", "topic"):
            metadata_value = str(metadata.get(key) or "").strip()
            if metadata_value:
                return metadata_value
    return "Wikipedia semi-structured data"


def _domain_counts(records: list[dict[str, Any]], *, domain_key: str) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for record in records:
        counts[_domain_value(record, domain_key=domain_key)] += 1
    return dict(sorted(counts.items()))


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)
