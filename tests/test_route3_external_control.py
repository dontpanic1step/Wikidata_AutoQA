from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from wikidata_simpleqa.config import LLMConfig
from wikidata_simpleqa.generation_models import (
    EntityReference,
    EvidenceRecord,
    GeneratedCandidate,
)
from wikidata_simpleqa.generator_validators import SearchLongtailVerifierError
from wikidata_simpleqa.route3_circuit import CircuitOpenError, ServiceCircuit
from wikidata_simpleqa.route3_ddg import Route3DDGVerifierResultStore
from wikidata_simpleqa.route3_external_calls import ExternalCallRecordStore
from wikidata_simpleqa.route3_external_lifecycle import (
    resolve_ambiguous_external_calls,
    scan_ambiguous_external_calls,
    write_ambiguous_external_call_reports,
)
from wikidata_simpleqa.route3_openrouter import (
    AbandonedExternalCallError,
    AmbiguousExternalCallError,
    OpenRouterAmbiguousTransportError,
    OpenRouterHTTPError,
    OpenRouterRawResponse,
    Route3DurableOpenRouterExecutor,
)


RESPONSE_BODY = '{"choices":[{"message":{"content":"answer"}}]}'


class SequenceTransport:
    """Return or raise configured outcomes while counting physical calls."""

    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = 0

    def send_once(self, _payload):
        self.calls += 1
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


class FailingSearchClient:
    """Raise one configured transport error for every query."""

    def __init__(self) -> None:
        self.calls = 0
        self.request_events = []

    def search(self, _query: str, *, max_results: int = 5):
        self.calls += 1
        raise RuntimeError("DDG unavailable")


def _candidate(page_id: int) -> GeneratedCandidate:
    return GeneratedCandidate(
        source_type="wikipedia_infobox_table",
        generation_route="route3_wikipedia_infobox",
        question=f"Who directed Example Film {page_id}?",
        answer="Jane Doe",
        answer_aliases=[],
        subject_entity=EntityReference(name=f"Example Film {page_id}"),
        answer_entity=EntityReference(name="Jane Doe"),
        relation_or_claim="director",
        evidence=EvidenceRecord(text="Jane Doe"),
        answer_type="Person",
        search_queries=[f"Example Film {page_id} director"],
        source_metadata={
            "canonical_page_id": page_id,
            "original_candidate_slot": "Person",
        },
    )


def _verify(store, item, client):
    return store.verify(
        item,
        search_client=client,
        top_k=5,
        max_full_question_hit_rate=0.0,
        max_keyword_hit_rate=0.1,
        max_overall_hit_rate=0.1,
        max_parallel_queries=1,
    )


class Route3CircuitTests(unittest.TestCase):
    def test_threshold_success_reset_and_sticky_open(self) -> None:
        circuit = ServiceCircuit("openrouter")
        circuit.record_failure(reason="one")
        circuit.record_failure(reason="two")
        self.assertFalse(circuit.is_open)

        circuit.record_success()
        circuit.record_failure(reason="one")
        circuit.record_failure(reason="two")
        self.assertFalse(circuit.is_open)
        circuit.record_failure(reason="three")
        self.assertTrue(circuit.is_open)

        circuit.record_success()
        self.assertTrue(circuit.is_open)
        with self.assertRaises(CircuitOpenError):
            circuit.before_call()
        self.assertEqual(circuit.snapshot()["threshold"], 3)

    def test_openrouter_status_classification_and_no_send_after_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            circuit = ServiceCircuit("openrouter")
            transport = SequenceTransport(
                [
                    OpenRouterHTTPError(status_code=429, body_text="rate"),
                    OpenRouterHTTPError(status_code=500, body_text="server"),
                    OpenRouterHTTPError(status_code=408, body_text="timeout"),
                ]
            )
            for page_id in (1, 2, 3):
                executor = Route3DurableOpenRouterExecutor(
                    store=ExternalCallRecordStore(root, canonical_page_id=page_id),
                    transport=transport,
                    circuit=circuit,
                )
                with self.assertRaises(Exception):
                    executor.execute(
                        call_key="generation",
                        request_payload={"model": "test/model", "messages": [page_id]},
                    )
            self.assertTrue(circuit.is_open)

            blocked = Route3DurableOpenRouterExecutor(
                store=ExternalCallRecordStore(root, canonical_page_id=4),
                transport=transport,
                circuit=circuit,
            )
            with self.assertRaises(CircuitOpenError):
                blocked.execute(
                    call_key="generation",
                    request_payload={"model": "test/model", "messages": [4]},
                )
            self.assertEqual(transport.calls, 3)

    def test_openrouter_401_trips_immediately_and_403_does_not(self) -> None:
        for status, expected_open in ((401, True), (402, True), (403, False)):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as temp_dir:
                circuit = ServiceCircuit("openrouter")
                transport = SequenceTransport(
                    [OpenRouterHTTPError(status_code=status, body_text="failure")]
                )
                executor = Route3DurableOpenRouterExecutor(
                    store=ExternalCallRecordStore(Path(temp_dir), canonical_page_id=1),
                    transport=transport,
                    circuit=circuit,
                )
                with self.assertRaises(Exception):
                    executor.execute(
                        call_key="generation",
                        request_payload={"model": "test/model", "messages": []},
                    )
                self.assertEqual(circuit.is_open, expected_open)

    def test_transport_ambiguity_counts_toward_openrouter_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            circuit = ServiceCircuit("openrouter")
            transport = SequenceTransport(
                [OpenRouterAmbiguousTransportError("lost") for _ in range(3)]
            )
            for page_id in (1, 2, 3):
                executor = Route3DurableOpenRouterExecutor(
                    store=ExternalCallRecordStore(Path(temp_dir), canonical_page_id=page_id),
                    transport=transport,
                    circuit=circuit,
                )
                with self.assertRaises(AmbiguousExternalCallError):
                    executor.execute(
                        call_key="generation",
                        request_payload={"model": "test/model", "messages": [page_id]},
                    )
            self.assertTrue(circuit.is_open)

    def test_ddg_counts_only_exhausted_verifiers_and_blocks_new_verifier(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            circuit = ServiceCircuit("duckduckgo")
            store = Route3DDGVerifierResultStore(
                Path(temp_dir),
                segment_fingerprint="segment",
                circuit=circuit,
            )
            clients = []
            for page_id in (1, 2, 3):
                client = FailingSearchClient()
                clients.append(client)
                with self.assertRaises(SearchLongtailVerifierError):
                    _verify(store, _candidate(page_id), client)
            self.assertTrue(circuit.is_open)

            blocked_client = FailingSearchClient()
            with self.assertRaises(CircuitOpenError):
                _verify(store, _candidate(4), blocked_client)
            self.assertEqual(blocked_client.calls, 0)


class Route3AmbiguousLifecycleTests(unittest.TestCase):
    def _commit_intent(self, root: Path, *, page_id: int = 11) -> tuple[dict, ExternalCallRecordStore]:
        request = {"model": "test/model", "messages": []}
        store = ExternalCallRecordStore(root, canonical_page_id=page_id)
        from wikidata_simpleqa.route3_run_ledger import canonical_json_sha256

        store.commit(
            call_key="generation",
            record_kind="intent",
            request_hash=canonical_json_sha256(request),
            payload={"request_payload": request},
        )
        return request, store

    def test_report_contains_required_audit_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "external_calls"
            self._commit_intent(root)
            json_path = Path(temp_dir) / "ambiguous_external_calls.json"
            md_path = Path(temp_dir) / "ambiguous_external_calls.md"

            rows = write_ambiguous_external_call_reports(
                root,
                json_path=json_path,
                markdown_path=md_path,
            )

            self.assertEqual(len(rows), 1)
            row = rows[0]
            for field in (
                "page_id",
                "allocation",
                "attempt",
                "call_purpose",
                "call_key",
                "model",
                "request_hash",
                "intent_time",
                "error",
                "retry_eligibility",
                "possible_duplicate_billing_note",
            ):
                self.assertIn(field, row)
            self.assertTrue(json_path.exists())
            self.assertIn("Unresolved calls: 1", md_path.read_text(encoding="utf-8"))

    def test_retry_authorizes_attempt002_and_never_attempt003(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "external_calls"
            request, store = self._commit_intent(root)

            acted = resolve_ambiguous_external_calls(root, action="retry")
            self.assertEqual(acted[0]["resolution_action"], "retry")
            transport = SequenceTransport([OpenRouterAmbiguousTransportError("lost again")])
            executor = Route3DurableOpenRouterExecutor(store=store, transport=transport)
            with self.assertRaises(AmbiguousExternalCallError) as caught:
                executor.execute(call_key="generation", request_payload=request)
            self.assertEqual(caught.exception.call_attempt, 2)
            self.assertEqual(transport.calls, 1)

            with self.assertRaisesRegex(ValueError, "attempt003"):
                resolve_ambiguous_external_calls(root, action="retry")
            self.assertFalse(store.record_path(
                "generation",
                "intent",
                call_attempt=2,
            ).parent.parent.joinpath("attempt003").exists())

    def test_abandon_commits_terminal_outcome_and_audit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "external_calls"
            request, store = self._commit_intent(root)

            acted = resolve_ambiguous_external_calls(root, action="abandon")

            self.assertEqual(acted[0]["resolution_action"], "abandon")
            self.assertEqual(scan_ambiguous_external_calls(root), [])
            resolution = store.load(
                call_key="generation",
                record_kind="resolution",
            )
            terminal = store.load(
                call_key="generation",
                record_kind="abandoned_ambiguous",
            )
            self.assertEqual(resolution["payload"]["action"], "abandon")
            self.assertEqual(terminal["payload"]["action"], "abandon")
            executor = Route3DurableOpenRouterExecutor(
                store=store,
                transport=SequenceTransport([]),
            )
            with self.assertRaises(AbandonedExternalCallError):
                executor.execute(call_key="generation", request_payload=request)


if __name__ == "__main__":
    unittest.main()
