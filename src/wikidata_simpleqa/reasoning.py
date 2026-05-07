"""Reasoning-style helpers and compositional multi-hop metadata utilities."""

from __future__ import annotations

from typing import Any

LEGACY_REASONING_STYLE_MAP = {
    "single_fact": "single_fact",
    "fact_join": "multi_hop_join",
    "ordinal_fact": "multi_hop_ordinal",
    "multi_hop_join": "multi_hop_join",
    "multi_hop_ordinal": "multi_hop_ordinal",
    "multi_hop_aggregate": "multi_hop_aggregate",
}


def normalize_reasoning_style(style: str) -> str:
    """Normalize legacy and current reasoning-style labels."""
    return LEGACY_REASONING_STYLE_MAP.get(style, style)


def is_multi_hop_reasoning_style(style: str) -> bool:
    """Return whether a reasoning style represents compositional multi-hop logic."""
    normalized = normalize_reasoning_style(style)
    return normalized in {"multi_hop_join", "multi_hop_ordinal", "multi_hop_aggregate"}


def build_reasoning_hop(
    *,
    source_qid: str,
    source_label: str,
    property_pid: str,
    property_label: str,
    target_qid: str | None,
    target_label: str,
    role: str,
    qualifiers: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build one serialized reasoning hop."""
    hop = {
        "source_qid": source_qid,
        "source_label": source_label,
        "property_pid": property_pid,
        "property_label": property_label,
        "target_qid": target_qid,
        "target_label": target_label,
        "role": role,
    }
    if qualifiers:
        hop["qualifiers"] = qualifiers
    return hop


def build_bridge_entity(*, qid: str, label: str, role: str) -> dict[str, str]:
    """Build one serialized bridge-entity record."""
    return {
        "qid": qid,
        "label": label,
        "role": role,
    }
