from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from wikidata_simpleqa.generation_models import (
    EntityReference,
    EvidenceRecord,
    GeneratedCandidate,
)
from wikidata_simpleqa.generator_validators import SearchLongtailVerifierError
from wikidata_simpleqa.route3_ddg import Route3DDGVerifierResultStore


class RecordingSearchClient:
    """Return configured rows while recording candidate-verifier queries."""

    def __init__(
        self,
        results_by_query: dict[str, list[dict[str, str]]] | None = None,
        *,
        error: BaseException | None = None,
    ) -> None:
        self.results_by_query = results_by_query or {}
        self.error = error
        self.calls: list[tuple[str, int]] = []
        self.request_events: list[dict] = []

    def search(self, query: str, *, max_results: int = 5):
        self.calls.append((query, max_results))
        if self.error is not None:
            raise self.error
        rows = self.results_by_query.get(query, [])[:max_results]
        return [type("SearchResult", (), row)() for row in rows]


def candidate(
    *,
    page_id: int,
    slot: str = "Person",
    revision_number: int | None = None,
) -> GeneratedCandidate:
    """Build one minimal formal Route 3 candidate."""
    metadata = {
        "canonical_page_id": page_id,
        "original_candidate_slot": slot,
    }
    if revision_number is not None:
        metadata["route3_revision_number"] = revision_number
    return GeneratedCandidate(
        source_type="wikipedia_infobox_table",
        generation_route="route3_wikipedia_infobox",
        question=f"Who directed Example Film {page_id}?",
        answer="Jane Doe",
        answer_aliases=["J. Doe"],
        subject_entity=EntityReference(name=f"Example Film {page_id}"),
        answer_entity=EntityReference(name="Jane Doe"),
        relation_or_claim="director",
        evidence=EvidenceRecord(text="Jane Doe"),
        answer_type="Person",
        search_queries=[f"Example Film {page_id} director"],
        source_metadata=metadata,
    )


def verify(
    store: Route3DDGVerifierResultStore,
    item: GeneratedCandidate,
    client: RecordingSearchClient,
) -> tuple[bool, dict]:
    """Run the durable verifier with fixed formal test settings."""
    return store.verify(
        item,
        search_client=client,
        top_k=5,
        max_full_question_hit_rate=0.0,
        max_keyword_hit_rate=0.1,
        max_overall_hit_rate=0.1,
        max_parallel_queries=1,
    )


class Route3DDGVerifierResultStoreTests(unittest.TestCase):
    """Check candidate-level DDG result persistence and resume behavior."""

    def test_completed_result_is_reused_with_identical_audit_and_order(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = Route3DDGVerifierResultStore(
                Path(temp_dir) / "ddg_verifier_results",
                segment_fingerprint="segment-sha",
            )
            item = candidate(page_id=101)
            first_client = RecordingSearchClient()

            first = verify(store, item, first_client)
            second = verify(store, item, RecordingSearchClient(error=AssertionError("recalled")))

            self.assertEqual(first, second)
            self.assertEqual(
                [row["query"] for row in first[1]["queries"]],
                [
                    "Who directed Example Film 101?",
                    "Example Film 101 director",
                ],
            )
            self.assertEqual(len(first_client.calls), 2)
            result_paths = list((Path(temp_dir) / "ddg_verifier_results").rglob("result.json"))
            self.assertEqual(len(result_paths), 1)
            record = json.loads(result_paths[0].read_text(encoding="utf-8"))
            self.assertEqual(record["features"], first[1])
            self.assertEqual(record["candidate_slot"], "Person")
            self.assertEqual(record["segment_fingerprint"], "segment-sha")

    def test_interrupt_reuses_first_candidate_and_restarts_only_current_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = Route3DDGVerifierResultStore(
                Path(temp_dir) / "ddg_verifier_results",
                segment_fingerprint="segment-sha",
            )
            first = candidate(page_id=101)
            second = candidate(page_id=102)
            third = candidate(page_id=103)
            verify(store, first, RecordingSearchClient())

            with self.assertRaises(KeyboardInterrupt):
                verify(
                    store,
                    second,
                    RecordingSearchClient(error=KeyboardInterrupt()),
                )

            resume_client = RecordingSearchClient()
            verify(store, first, resume_client)
            verify(store, second, resume_client)
            verify(store, third, resume_client)

            self.assertEqual(
                [query for query, _ in resume_client.calls],
                [
                    "Who directed Example Film 102?",
                    "Example Film 102 director",
                    "Who directed Example Film 103?",
                    "Example Film 103 director",
                ],
            )
            self.assertEqual(
                len(list((Path(temp_dir) / "ddg_verifier_results").rglob("result.json"))),
                3,
            )

    def test_infrastructure_failure_is_not_persisted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "ddg_verifier_results"
            store = Route3DDGVerifierResultStore(
                root,
                segment_fingerprint="segment-sha",
            )
            item = candidate(page_id=101)

            with self.assertRaises(SearchLongtailVerifierError):
                verify(store, item, RecordingSearchClient(error=RuntimeError("DDG unavailable")))
            self.assertEqual(list(root.rglob("result.json")), [])

            recovery_client = RecordingSearchClient()
            passed, _features = verify(store, item, recovery_client)
            self.assertTrue(passed)
            self.assertEqual(len(recovery_client.calls), 2)

    def test_normal_rejection_is_persisted_and_not_reclassified_as_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = Route3DDGVerifierResultStore(
                Path(temp_dir) / "ddg_verifier_results",
                segment_fingerprint="segment-sha",
            )
            item = candidate(page_id=101)
            rows = {
                item.final_question: [
                    {
                        "title": "Jane Doe directed Example Film 101",
                        "snippet": "Archived result",
                        "url": "https://example.test/result",
                    }
                ]
            }

            first = verify(store, item, RecordingSearchClient(rows))
            second = verify(store, item, RecordingSearchClient(error=AssertionError("recalled")))

            self.assertFalse(first[0])
            self.assertEqual(first, second)
            self.assertEqual(
                first[1]["triggered_rule"],
                "full_question:answer_in_title",
            )

    def test_revision_number_changes_candidate_key(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = Route3DDGVerifierResultStore(
                Path(temp_dir),
                segment_fingerprint="segment-sha",
            )

            original_key = store.candidate_key(candidate(page_id=101))
            revision_key = store.candidate_key(
                candidate(page_id=101, revision_number=2)
            )

            self.assertEqual(
                original_key,
                "allocation/101/candidate/Person/segment/segment-sha",
            )
            self.assertEqual(
                revision_key,
                "allocation/101/revision/2/candidate/Person/segment/segment-sha",
            )


if __name__ == "__main__":
    unittest.main()
