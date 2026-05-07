"""String normalization utilities for ambiguity checks."""

from __future__ import annotations

import re
import unicodedata


def normalize_name(text: str) -> str:
    """Normalize labels and aliases for collision detection."""
    normalized = unicodedata.normalize("NFKD", text)
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    normalized = normalized.lower()
    normalized = re.sub(r"\([^)]*\)", "", normalized)
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized
