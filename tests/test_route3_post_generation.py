from __future__ import annotations

from contextlib import ExitStack, contextmanager
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from wikidata_simpleqa.config import Settings
from wikidata_simpleqa.generation_models import EvidenceRecord, GeneratedCandidate, EntityReference
from wikidata_simpleqa.generator_validators import SearchLongtailVerifierError
from wikidata_simpleqa.route3_openrouter import (
    DefiniteOpenRouterHTTPError,
    DefiniteOpenRouterResponseError,
)
from wikidata_simpleqa.route3_post_generation import (
    Route3ProcessingResult,
    process_route3_candidates,
)
import wikidata_simpleqa.route3_post_generation as post_generation


def candidate() -> GeneratedCandidate:
    return GeneratedCandidate(
        source_type="wikipedia_tables",
        generation_route="route3_wikipedia_infobox",
        question="Which venue hosted the Example Cup final?",
        canonical_question="Which venue hosted the Example Cup final?",
        answer="Willow Hall",
        answer_aliases=[],
        subject_entity=EntityReference(name="Example Cup"),
        answer_entity=EntityReference(name="Willow Hall"),
        relation_or_claim="host venue",
        evidence=EvidenceRecord(text="Final | Willow Hall"),
        answer_type="Other",
        source_metadata={"route3_slot_id": "Other"},
    )


def settings(*, second_stage: bool = False) -> Settings:
    return Settings(
        pilot_total=1,
        cutoff_year=2024,
        second_stage_grading_enabled=second_stage,
        second_stage_grading_accuracy_threshold=0.1,
        search_longtail_max_full_question_hit_rate=1.0,
        search_longtail_max_keyword_hit_rate=1.0,
        search_longtail_max_overall_hit_rate=1.0,
    )


def marked(order: list[str], name: str, result):
    def call(*args, **kwargs):
        order.append(name)
        return result

    return call


@contextmanager
def passing_local_stages(order: list[str]):
    with ExitStack() as stack:
        for name, label in (
            ("_post_rewrite_answer_popularity_failure", "surface_popularity"),
            ("_post_rewrite_self_containment_failure", "surface_self_containment"),
            ("_post_rewrite_answer_scope_ambiguity_failure", "surface_answer_scope"),
            ("_post_rewrite_time_invariance_failure", "surface_time_invariance"),
            ("_post_rewrite_award_year_precision_failure", "surface_award_precision"),
        ):
            stack.enter_context(patch.object(post_generation, name, side_effect=marked(order, label, None)))
        stack.enter_context(
            patch.object(
                post_generation,
                "validate_question_surface",
                side_effect=marked(order, "surface_validation", None),
            )
        )
        stack.enter_context(
            patch.object(
                post_generation,
                "evaluate_candidate_answer_type_gate",
                side_effect=marked(order, "answer_type_gate", SimpleNamespace(matched=True, details={})),
            )
        )
        stack.enter_context(
            patch.object(
                post_generation,
                "attach_rule_based_gate_result",
                side_effect=marked(order, "answer_type_metadata", None),
            )
        )
        stack.enter_context(
            patch.object(
                post_generation,
                "_apply_number_reference_margin",
                side_effect=marked(order, "number_reference", None),
            )
        )
        stack.enter_context(
            patch.object(
                post_generation,
                "validate_generated_candidate",
                side_effect=marked(order, "source_validation", (True, {"answer_in_evidence": True})),
            )
        )
        yield


class VerifierStore:
    def __init__(self, order: list[str], error: Exception | None = None) -> None:
        self.order = order
        self.error = error

    def verify(self, *args, **kwargs):
        self.order.append("duckduckgo")
        if self.error is not None:
            raise self.error
        return True, {"decision": "accept"}


def test_route3_stage_order_and_result_contract() -> None:
    order: list[str] = []
    with passing_local_stages(order), patch.object(
        post_generation,
        "evaluate_model_panel",
        side_effect=marked(order, "second_stage", {"accuracy": 0.0}),
    ):
        result = process_route3_candidates(
            [candidate()],
            settings=settings(second_stage=True),
            search_client=object(),
            ddg_verifier_result_store=VerifierStore(order),
            second_stage_model_clients=[object()],
            grading_grader_client=object(),
        )

    assert isinstance(result, Route3ProcessingResult)
    assert len(result.accepted) == 1
    assert result.rejected == []
    assert result.telemetry["process_route3_candidates"]["accepted"] == 1
    assert order == [
        "surface_popularity",
        "surface_self_containment",
        "surface_answer_scope",
        "surface_time_invariance",
        "surface_award_precision",
        "surface_validation",
        "answer_type_gate",
        "answer_type_metadata",
        "number_reference",
        "source_validation",
        "duckduckgo",
        "second_stage",
    ]


def test_route3_ddg_infrastructure_failure_propagates() -> None:
    order: list[str] = []
    failure = SearchLongtailVerifierError("DDG unavailable", features={"query_errors": []})
    with passing_local_stages(order), pytest.raises(SearchLongtailVerifierError) as raised:
        process_route3_candidates(
            [candidate()],
            settings=settings(),
            search_client=object(),
            ddg_verifier_result_store=VerifierStore(order, failure),
        )
    assert raised.value is failure

@pytest.mark.parametrize(
    ("failure", "reason"),
    [
        (
            DefiniteOpenRouterHTTPError(
                call_key="second_stage_answer/Other/model",
                request_hash="hash",
                status_code=403,
                body_text="forbidden",
            ),
            "openrouter_http_error:403",
        ),
        (
            DefiniteOpenRouterResponseError(
                call_key="second_stage_answer/Other/model",
                request_hash="hash",
                error=ValueError("invalid JSON"),
            ),
            "second_stage_unparseable_response",
        ),
    ],
)
def test_route3_persisted_second_stage_failures_are_terminal(
    failure: Exception,
    reason: str,
) -> None:
    order: list[str] = []
    with passing_local_stages(order), patch.object(
        post_generation,
        "evaluate_model_panel",
        side_effect=failure,
    ):
        result = process_route3_candidates(
            [candidate()],
            settings=settings(second_stage=True),
            search_client=object(),
            ddg_verifier_result_store=VerifierStore(order),
            second_stage_model_clients=[object()],
            grading_grader_client=object(),
        )

    assert result.accepted == []
    assert result.rejected[0]["rejection_reason"] == reason

def test_route3_retryable_openrouter_failure_propagates() -> None:
    order: list[str] = []
    failure = DefiniteOpenRouterHTTPError(
        call_key="second_stage_answer/Other/model",
        request_hash="hash",
        status_code=429,
        body_text="rate limited",
    )
    with passing_local_stages(order), patch.object(
        post_generation,
        "evaluate_model_panel",
        side_effect=failure,
    ), pytest.raises(DefiniteOpenRouterHTTPError) as raised:
        process_route3_candidates(
            [candidate()],
            settings=settings(second_stage=True),
            search_client=object(),
            ddg_verifier_result_store=VerifierStore(order),
            second_stage_model_clients=[object()],
            grading_grader_client=object(),
        )
    assert raised.value is failure
