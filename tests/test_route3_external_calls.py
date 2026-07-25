from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from wikidata_simpleqa.route3_external_calls import ExternalCallRecordStore


class Route3ExternalCallRecordTests(unittest.TestCase):
    def test_definite_response_is_reused_by_call_key_and_request_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ExternalCallRecordStore(
                Path(temp_dir) / "external_calls",
                canonical_page_id=101,
            )
            store.commit(
                call_key="generation",
                record_kind="intent",
                request_hash="request-hash",
                payload={"model": "google/gemini-3-flash-preview"},
            )
            store.commit(
                call_key="generation",
                record_kind="response",
                request_hash="request-hash",
                payload={"text": "{\"answer\": \"A\"}"},
            )

            outcome = store.load_matching_outcome(
                call_key="generation",
                request_hash="request-hash",
            )

            self.assertIsNotNone(outcome)
            self.assertEqual(outcome["record_kind"], "response")
            self.assertEqual(outcome["payload"]["text"], "{\"answer\": \"A\"}")

    def test_call_key_is_allocation_scoped_not_attempt_scoped(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ExternalCallRecordStore(
                Path(temp_dir) / "external_calls",
                canonical_page_id=202,
            )
            first_path = store.commit(
                call_key="second_stage_answer/Person/openai/gpt-4.1-mini",
                record_kind="response",
                request_hash="same-request",
                payload={"text": "answer"},
            )

            resumed_store = ExternalCallRecordStore(
                Path(temp_dir) / "external_calls",
                canonical_page_id=202,
            )
            outcome = resumed_store.load_matching_outcome(
                call_key="second_stage_answer/Person/openai/gpt-4.1-mini",
                request_hash="same-request",
            )

            self.assertEqual(len(outcome["call_key_hash"]), 64)
            self.assertEqual(outcome["payload"], {"text": "answer"})
            self.assertIn("p202", first_path.parts)
            self.assertIn("attempt001", first_path.parts)
            self.assertNotIn("attempt002", first_path.parts)

    def test_request_hash_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ExternalCallRecordStore(
                Path(temp_dir) / "external_calls",
                canonical_page_id=303,
            )
            store.commit(
                call_key="generation",
                record_kind="response",
                request_hash="first-request",
                payload={"text": "response"},
            )

            with self.assertRaisesRegex(ValueError, "request hash mismatch"):
                store.load_matching_outcome(
                    call_key="generation",
                    request_hash="changed-request",
                )

    def test_intent_without_outcome_is_not_a_definite_result(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ExternalCallRecordStore(
                Path(temp_dir) / "external_calls",
                canonical_page_id=404,
            )
            store.commit(
                call_key="generation",
                record_kind="intent",
                request_hash="request-hash",
                payload={"model": "google/gemini-3-flash-preview"},
            )

            self.assertIsNone(
                store.load_matching_outcome(
                    call_key="generation",
                    request_hash="request-hash",
                )
            )


if __name__ == "__main__":
    unittest.main()
