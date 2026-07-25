from __future__ import annotations

import json
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
from unittest.mock import patch
from urllib.error import URLError

from wikidata_simpleqa.config import LLMConfig
from wikidata_simpleqa.route3_external_calls import ExternalCallRecordStore
from wikidata_simpleqa.route3_openrouter import (
    AmbiguousExternalCallError,
    DefiniteOpenRouterHTTPError,
    DefiniteOpenRouterResponseError,
    OpenRouterAmbiguousTransportError,
    OpenRouterHTTPError,
    OpenRouterRawResponse,
    Route3DurableOpenRouterClient,
    Route3DurableOpenRouterExecutor,
    Route3OpenRouterTransport,
)
from wikidata_simpleqa.route3_run_ledger import canonical_json_sha256


RESPONSE_BODY = json.dumps(
    {
        "choices": [
            {
                "message": {"content": "answer"},
                "finish_reason": "stop",
            }
        ]
    }
)


class FakeTransport:
    def __init__(self, outcome: object) -> None:
        self.outcome = outcome
        self.calls: list[dict] = []

    def send_once(self, payload: dict) -> OpenRouterRawResponse:
        self.calls.append(payload)
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self.outcome


class SynchronizedIntentStore(ExternalCallRecordStore):
    """Synchronize two intent commits to exercise the no-clobber boundary."""

    def __init__(self, root: Path, *, canonical_page_id: int, barrier: Barrier) -> None:
        super().__init__(root, canonical_page_id=canonical_page_id)
        self.barrier = barrier

    def commit(self, **kwargs) -> Path:
        if kwargs["record_kind"] == "intent":
            self.barrier.wait()
        return super().commit(**kwargs)

class FakeHTTPResponse:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None

    def read(self) -> bytes:
        return RESPONSE_BODY.encode("utf-8")


class Route3OpenRouterTests(unittest.TestCase):
    def make_executor(
        self,
        root: Path,
        transport: FakeTransport,
    ) -> tuple[ExternalCallRecordStore, Route3DurableOpenRouterExecutor]:
        store = ExternalCallRecordStore(root / "external_calls", canonical_page_id=101)
        return store, Route3DurableOpenRouterExecutor(store=store, transport=transport)

    def test_concurrent_logical_call_creates_one_intent_and_sends_once(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            transport = FakeTransport(OpenRouterRawResponse(200, RESPONSE_BODY))
            store = SynchronizedIntentStore(
                Path(temp_dir) / "external_calls",
                canonical_page_id=101,
                barrier=Barrier(2),
            )
            executor = Route3DurableOpenRouterExecutor(store=store, transport=transport)
            request = {"model": "test/model", "messages": []}

            with ThreadPoolExecutor(max_workers=2) as pool:
                futures = [
                    pool.submit(
                        executor.execute,
                        call_key="generation",
                        request_payload=request,
                    )
                    for _ in range(2)
                ]
            results = []
            failures = []
            for future in futures:
                try:
                    results.append(future.result())
                except AmbiguousExternalCallError as exc:
                    failures.append(exc)

            self.assertEqual(len(results), 1)
            self.assertEqual(len(failures), 1)
            self.assertEqual(len(transport.calls), 1)
    def test_no_intent_calls_once_and_reuses_persisted_response(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            transport = FakeTransport(OpenRouterRawResponse(200, RESPONSE_BODY))
            store, executor = self.make_executor(Path(temp_dir), transport)
            request = {"model": "test/model", "messages": []}

            first = executor.execute(call_key="generation", request_payload=request)
            second = executor.execute(call_key="generation", request_payload=request)

            self.assertEqual(first, second)
            self.assertEqual(len(transport.calls), 1)
            self.assertIsNotNone(store.load(call_key="generation", record_kind="intent"))
            self.assertIsNotNone(store.load(call_key="generation", record_kind="response"))

    def test_existing_intent_without_outcome_is_ambiguous_before_send(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            request = {"model": "test/model", "messages": []}
            request_hash = canonical_json_sha256(request)
            transport = FakeTransport(OpenRouterRawResponse(200, RESPONSE_BODY))
            store, executor = self.make_executor(Path(temp_dir), transport)
            store.commit(
                call_key="generation",
                record_kind="intent",
                request_hash=request_hash,
                payload={"request_payload": request},
            )

            with self.assertRaises(AmbiguousExternalCallError):
                executor.execute(call_key="generation", request_payload=request)

            self.assertEqual(transport.calls, [])

    def test_transport_ambiguity_is_not_retried_on_resume(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            transport = FakeTransport(OpenRouterAmbiguousTransportError("connection lost"))
            _, executor = self.make_executor(Path(temp_dir), transport)
            request = {"model": "test/model", "messages": []}

            with self.assertRaises(AmbiguousExternalCallError):
                executor.execute(call_key="generation", request_payload=request)
            with self.assertRaises(AmbiguousExternalCallError):
                executor.execute(call_key="generation", request_payload=request)

            self.assertEqual(len(transport.calls), 1)

    def test_response_returned_before_persist_crash_is_ambiguous_on_resume(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            transport = FakeTransport(OpenRouterRawResponse(200, RESPONSE_BODY))
            store, executor = self.make_executor(Path(temp_dir), transport)
            request = {"model": "test/model", "messages": []}
            original_commit = store.commit

            def crash_before_response_commit(**kwargs):
                if kwargs["record_kind"] == "response":
                    raise RuntimeError("injected response persistence crash")
                return original_commit(**kwargs)

            with patch.object(store, "commit", side_effect=crash_before_response_commit):
                with self.assertRaises(AmbiguousExternalCallError) as caught:
                    executor.execute(call_key="generation", request_payload=request)
                self.assertIn("outcome_persistence_failed", caught.exception.transport_error)

            resumed = Route3DurableOpenRouterExecutor(store=store, transport=transport)
            with self.assertRaises(AmbiguousExternalCallError):
                resumed.execute(call_key="generation", request_payload=request)
            self.assertEqual(len(transport.calls), 1)

    def test_explicit_http_error_is_persisted_and_reused(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            transport = FakeTransport(OpenRouterHTTPError(status_code=429, body_text="rate limited"))
            store, executor = self.make_executor(Path(temp_dir), transport)
            request = {"model": "test/model", "messages": []}

            for _ in range(2):
                with self.assertRaises(DefiniteOpenRouterHTTPError) as caught:
                    executor.execute(call_key="generation", request_payload=request)
                self.assertEqual(caught.exception.status_code, 429)

            self.assertEqual(len(transport.calls), 1)
            self.assertIsNotNone(store.load(call_key="generation", record_kind="http_error"))

    def test_invalid_raw_response_is_definite_and_not_recalled(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            transport = FakeTransport(OpenRouterRawResponse(200, "not-json"))
            _, executor = self.make_executor(Path(temp_dir), transport)
            request = {"model": "test/model", "messages": []}

            for _ in range(2):
                with self.assertRaises(DefiniteOpenRouterResponseError):
                    executor.execute(call_key="generation", request_payload=request)

            self.assertEqual(len(transport.calls), 1)

    def test_invalid_openrouter_envelope_is_definite_and_not_recalled(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            transport = FakeTransport(OpenRouterRawResponse(200, json.dumps({"choices": []})))
            _, executor = self.make_executor(Path(temp_dir), transport)
            client = Route3DurableOpenRouterClient(
                config=LLMConfig(
                    provider="openrouter",
                    model="test/model",
                    api_key_env="TEST_OPENROUTER_KEY",
                ),
                executor=executor,
                call_key="generation",
            )

            for _ in range(2):
                with self.assertRaises(DefiniteOpenRouterResponseError):
                    client.complete_text_with_audit("Generate.")

            self.assertEqual(len(transport.calls), 1)
    def test_durable_client_keeps_existing_request_and_audit_shape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            transport = FakeTransport(OpenRouterRawResponse(200, RESPONSE_BODY))
            _, executor = self.make_executor(Path(temp_dir), transport)
            config = LLMConfig(
                provider="openrouter",
                model="test/model",
                api_key_env="TEST_OPENROUTER_KEY",
                temperature=0.0,
                max_tokens=128,
            )
            client = Route3DurableOpenRouterClient(
                config=config,
                executor=executor,
                call_key="second_stage_answer/Person/test/model",
            )

            audit = client.complete_text_with_audit("Question?")

            self.assertEqual(audit["text"], "answer")
            self.assertEqual(audit["request_payload"]["model"], "test/model")
            self.assertEqual(audit["request_payload"]["messages"][-1]["content"], "Question?")
            self.assertTrue(client.disable_caller_retry)

    def test_artifacts_do_not_contain_api_key(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            transport = FakeTransport(OpenRouterRawResponse(200, RESPONSE_BODY))
            _, executor = self.make_executor(root, transport)
            executor.execute(
                call_key="generation",
                request_payload={"model": "test/model", "messages": []},
            )

            artifact_text = "\n".join(
                path.read_text(encoding="utf-8")
                for path in (root / "external_calls").rglob("*.json")
            )
            self.assertNotIn("secret-api-key", artifact_text)
            self.assertNotIn("Authorization", artifact_text)

    def test_thin_transport_performs_one_physical_request_without_retry(self) -> None:
        config = LLMConfig(
            provider="openrouter",
            model="test/model",
            api_key_env="TEST_OPENROUTER_KEY",
        )
        with patch.dict("os.environ", {"TEST_OPENROUTER_KEY": "secret-api-key"}, clear=False):
            transport = Route3OpenRouterTransport(config=config, timeout_seconds=30.0)
        with patch(
            "wikidata_simpleqa.route3_openrouter.urlopen",
            side_effect=URLError("offline"),
        ) as mocked_urlopen:
            with self.assertRaises(OpenRouterAmbiguousTransportError):
                transport.send_once({"model": "test/model", "messages": []})

        self.assertEqual(mocked_urlopen.call_count, 1)

    def test_thin_transport_returns_raw_body_without_parsing(self) -> None:
        config = LLMConfig(
            provider="openrouter",
            model="test/model",
            api_key_env="TEST_OPENROUTER_KEY",
        )
        with patch.dict("os.environ", {"TEST_OPENROUTER_KEY": "secret-api-key"}, clear=False):
            transport = Route3OpenRouterTransport(config=config, timeout_seconds=30.0)
        with patch(
            "wikidata_simpleqa.route3_openrouter.urlopen",
            return_value=FakeHTTPResponse(),
        ) as mocked_urlopen:
            response = transport.send_once({"model": "test/model", "messages": []})

        self.assertEqual(response.body_text, RESPONSE_BODY)
        self.assertEqual(mocked_urlopen.call_count, 1)


if __name__ == "__main__":
    unittest.main()
