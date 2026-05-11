"""Helpers for canonical subject-resource URLs and deduplication keys."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote


def wikidata_entity_url(qid: str) -> str:
    """Return the canonical Wikidata URL for one entity qid."""
    return f"https://www.wikidata.org/wiki/{qid}"


def wikipedia_url_from_entity(entity: dict[str, Any]) -> str | None:
    """Return the canonical English Wikipedia URL when a sitelink exists."""
    title = (
        entity.get("sitelinks", {})
        .get("enwiki", {})
        .get("title")
    )
    if not title:
        return None
    return "https://en.wikipedia.org/wiki/" + quote(title.replace(" ", "_"))


def canonical_subject_resource(
    subject_qid: str,
    entity: dict[str, Any] | None = None,
) -> tuple[str, str]:
    """Return a stable subject-resource URL and deduplication key."""
    wikipedia_url = wikipedia_url_from_entity(entity or {})
    if wikipedia_url is not None:
        return wikipedia_url, wikipedia_url
    wikidata_url = wikidata_entity_url(subject_qid)
    return wikidata_url, wikidata_url
