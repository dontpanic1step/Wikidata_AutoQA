"""Candidate-scoped durable DuckDuckGo verifier results for formal Route 3."""

from __future__ import annotations

import json
import os
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any
from uuid import uuid4

from .generation_models import GeneratedCandidate
from .generator_validators import (
    SearchLongtailVerifierError,
    run_search_based_longtail_verifier,
)
from .route3_run_ledger import canonical_json_sha256, utc_now_iso


DDG_VERIFIER_RESULT_SCHEMA_VERSION = 1


def _atomic_create_json(path: Path, payload: dict[str, Any]) -> None:
    """Atomically create one complete JSON result without replacing an existing result."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.{os.getpid()}.{uuid4().hex}.tmp")
    try:
        temp_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.link(temp_path, path)
    finally:
        temp_path.unlink(missing_ok=True)


@dataclass(slots=True)
class Route3DDGVerifierResultStore:
    """Persist and reuse completed candidate-level DDG verifier decisions."""

    root: Path
    segment_fingerprint: str

    def __post_init__(self) -> None:
        self.root = Path(self.root)
        self.segment_fingerprint = str(self.segment_fingerprint).strip()
        if not self.segment_fingerprint:
            raise ValueError("segment_fingerprint is required")

    def verify(
        self,
        candidate: GeneratedCandidate,
        *,
        search_client: Any,
        top_k: int,
        max_full_question_hit_rate: float,
        max_keyword_hit_rate: float,
        max_overall_hit_rate: float,
        max_parallel_queries: int = 1,
    ) -> tuple[bool, dict[str, Any]]:
        """Return a persisted or newly completed candidate-level verifier decision."""
        candidate_key = self.candidate_key(candidate)
        input_payload = self._input_payload(
            candidate,
            top_k=top_k,
            max_full_question_hit_rate=max_full_question_hit_rate,
            max_keyword_hit_rate=max_keyword_hit_rate,
            max_overall_hit_rate=max_overall_hit_rate,
            max_parallel_queries=max_parallel_queries,
        )
        input_hash = canonical_json_sha256(input_payload)
        existing = self._load(candidate_key=candidate_key, input_hash=input_hash)
        if existing is not None:
            return bool(existing["passed"]), deepcopy(existing["features"])

        started = perf_counter()
        try:
            passed, features = run_search_based_longtail_verifier(
                candidate,
                search_client=search_client,
                top_k=top_k,
                max_full_question_hit_rate=max_full_question_hit_rate,
                max_keyword_hit_rate=max_keyword_hit_rate,
                max_overall_hit_rate=max_overall_hit_rate,
                max_parallel_queries=max_parallel_queries,
            )
        except SearchLongtailVerifierError as exc:
            exc.features["duration_seconds"] = round(perf_counter() - started, 4)
            raise
        durable_features = deepcopy(features)
        durable_features["duration_seconds"] = round(perf_counter() - started, 4)
        record = {
            "schema_version": DDG_VERIFIER_RESULT_SCHEMA_VERSION,
            "candidate_key": candidate_key,
            "candidate_key_hash": canonical_json_sha256(candidate_key),
            "canonical_page_id": int(candidate.source_metadata["canonical_page_id"]),
            "candidate_slot": self._candidate_slot(candidate),
            "segment_fingerprint": self.segment_fingerprint,
            "revision_number": self._revision_number(candidate),
            "input_hash": input_hash,
            "input_payload": input_payload,
            "passed": bool(passed),
            "features": durable_features,
            "committed_at_utc": utc_now_iso(),
        }
        path = self.result_path(candidate_key)
        try:
            _atomic_create_json(path, record)
        except FileExistsError:
            committed = self._load(candidate_key=candidate_key, input_hash=input_hash)
            if committed is None:
                raise
            return bool(committed["passed"]), deepcopy(committed["features"])
        return bool(passed), durable_features

    def candidate_key(self, candidate: GeneratedCandidate) -> str:
        """Return the stable allocation, slot, fingerprint, and revision key."""
        page_id = int(candidate.source_metadata["canonical_page_id"])
        slot = self._candidate_slot(candidate)
        revision_number = self._revision_number(candidate)
        parts = [f"allocation/{page_id}"]
        if revision_number is not None:
            parts.append(f"revision/{revision_number}")
        parts.extend(
            [
                f"candidate/{slot}",
                f"segment/{self.segment_fingerprint}",
            ]
        )
        return "/".join(parts)

    def result_path(self, candidate_key: str) -> Path:
        """Return the immutable result path for one candidate key."""
        page_id_text = str(candidate_key).split("/", 2)[1]
        return (
            self.root
            / f"p{int(page_id_text)}"
            / f"c_{canonical_json_sha256(candidate_key)}"
            / "result.json"
        )

    def _load(
        self,
        *,
        candidate_key: str,
        input_hash: str,
    ) -> dict[str, Any] | None:
        path = self.result_path(candidate_key)
        if not path.exists():
            return None
        record = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(record, dict):
            raise ValueError(f"DDG verifier result must contain a JSON object: {path}")
        if int(record.get("schema_version", 0)) != DDG_VERIFIER_RESULT_SCHEMA_VERSION:
            raise ValueError(f"Unsupported DDG verifier result schema: {path}")
        if str(record.get("candidate_key", "")) != candidate_key:
            raise ValueError(f"DDG verifier candidate key mismatch: {path}")
        if str(record.get("input_hash", "")) != input_hash:
            raise ValueError(f"DDG verifier input hash mismatch: {candidate_key}")
        return record

    def _input_payload(
        self,
        candidate: GeneratedCandidate,
        *,
        top_k: int,
        max_full_question_hit_rate: float,
        max_keyword_hit_rate: float,
        max_overall_hit_rate: float,
        max_parallel_queries: int,
    ) -> dict[str, Any]:
        metadata = candidate.source_metadata
        return {
            "question": candidate.final_question,
            "answer": candidate.answer,
            "answer_aliases": list(candidate.answer_aliases),
            "answer_type": candidate.answer_type,
            "search_queries": list(candidate.search_queries),
            "generation_route": candidate.generation_route,
            "subject_name": candidate.subject_entity.name,
            "relation_or_claim": candidate.relation_or_claim,
            "answer_items": deepcopy(metadata.get("answer_items", [])),
            "number_reference_margin": deepcopy(metadata.get("number_reference_margin", {})),
            "top_k": int(top_k),
            "max_parallel_queries": int(max_parallel_queries),
            "thresholds": {
                "full_question": float(max_full_question_hit_rate),
                "keyword_queries": float(max_keyword_hit_rate),
                "overall": float(max_overall_hit_rate),
            },
        }

    @staticmethod
    def _candidate_slot(candidate: GeneratedCandidate) -> str:
        slot = str(
            candidate.source_metadata.get("original_candidate_slot")
            or candidate.source_metadata.get("route3_slot_id")
            or ""
        ).strip()
        if not slot:
            raise ValueError("Route 3 candidate slot is required for DDG result persistence")
        return slot

    @staticmethod
    def _revision_number(candidate: GeneratedCandidate) -> int | None:
        value = candidate.source_metadata.get("route3_revision_number")
        return int(value) if value is not None else None
