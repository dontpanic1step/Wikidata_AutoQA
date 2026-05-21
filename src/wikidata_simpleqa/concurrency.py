"""Shared semaphore wrappers for bounded route processing."""

from __future__ import annotations

from dataclasses import dataclass
from threading import Lock, Semaphore
from typing import Any


@dataclass(slots=True)
class SharedPipelineConcurrency:
    """Shared locks and service limits for scalable route runners."""

    commit_lock: Lock
    wikidata_semaphore: Semaphore
    duckduckgo_semaphore: Semaphore
    generation_rewrite_semaphore: Semaphore
    second_stage_semaphore: Semaphore


class SemaphoreWrappedClient:
    """Proxy a client and bound selected method calls with a semaphore."""

    def __init__(self, client: Any, semaphore: Semaphore, methods: set[str]) -> None:
        self._client = client
        self._semaphore = semaphore
        self._methods = methods

    def __getattr__(self, name: str):
        attr = getattr(self._client, name)
        if name not in self._methods or not callable(attr):
            return attr

        def wrapped(*args, **kwargs):
            with self._semaphore:
                return attr(*args, **kwargs)

        return wrapped


def build_shared_pipeline_concurrency(
    *,
    wikidata_limit: int = 1,
    duckduckgo_limit: int = 4,
    generation_rewrite_limit: int = 10,
    second_stage_limit: int = 10,
) -> SharedPipelineConcurrency:
    """Build a concurrency context shared by scalable route runners."""
    return SharedPipelineConcurrency(
        commit_lock=Lock(),
        wikidata_semaphore=Semaphore(max(1, int(wikidata_limit))),
        duckduckgo_semaphore=Semaphore(max(1, int(duckduckgo_limit))),
        generation_rewrite_semaphore=Semaphore(max(1, int(generation_rewrite_limit))),
        second_stage_semaphore=Semaphore(max(1, int(second_stage_limit))),
    )
