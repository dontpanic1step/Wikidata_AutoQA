from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str) -> ModuleType:
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"{name}_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def make_review_bundle(
    *,
    internal_id: str,
    question: str,
    answer: str,
    url: str,
    segment_id: str,
    archive_name: str,
) -> dict[str, object]:
    return {
        "artifact": {"id": internal_id},
        "active_record": {
            "id": internal_id,
            "question": question,
            "answer": answer,
            "evidence": {
                "text": f"Selected table row: {answer}",
                "url": url,
                "source_title": f"Source for {answer}",
            },
            "validation": {"answer_in_evidence": True},
            "source_metadata": {
                "segment_id": segment_id,
                "canonical_url": url,
                "page_title": f"Source for {answer}",
                "derivation_summary": f"The selected row gives {answer} as the value",
                "route3_page_archive": {
                    "archive_path": f"/aws/cache/{archive_name}"
                },
            },
            "search_verification_features": {
                "queries": [
                    {
                        "query_name": "full_question",
                        "query_category": "full_question",
                        "query": question,
                        "results": [
                            {
                                "title": f"Search result for {answer}",
                                "snippet": f"A snippet mentioning {answer}",
                                "url": f"https://search.example/{answer.lower()}",
                                "answer_hit": True,
                            }
                        ],
                    },
                    {
                        "query_name": "answer_probe",
                        "query_category": "answer_probe",
                        "query": f"{question} {answer}",
                        "results": [
                            {
                                "title": "Excluded probe",
                                "snippet": answer,
                                "url": f"https://probe.example/{answer.lower()}",
                            }
                        ],
                    },
                ]
            },
        },
    }


def test_simpleqa_synth_prefetch_merges_two_generation_runs(tmp_path: Path) -> None:
    module = load_script("build_simpleqa_synth_prefetch")
    csv_path = tmp_path / "simpleqa_synth.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["id", "problem", "answer", "topic", "answer_type", "urls"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "id": "simpleqa_synth_000001",
                "problem": "Question one?",
                "answer": "Alpha",
                "topic": "Other",
                "answer_type": "Other",
                "urls": json.dumps(["https://example.org/one"]),
            }
        )
        writer.writerow(
            {
                "id": "simpleqa_synth_000002",
                "problem": "Question two?",
                "answer": "Beta",
                "topic": "Other",
                "answer_type": "Other",
                "urls": json.dumps(["https://example.org/two"]),
            }
        )

    registry_path = tmp_path / "public_ids.json"
    write_json(
        registry_path,
        {
            "assignments": [
                {
                    "public_id": "simpleqa_synth_000001",
                    "candidate_id": "page1_other_alpha",
                },
                {
                    "public_id": "simpleqa_synth_000002",
                    "candidate_id": "page2_other_beta",
                },
            ]
        },
    )
    first_state = tmp_path / "first_review.json"
    second_state = tmp_path / "second_review.json"
    write_json(
        first_state,
        {
            "candidates": [
                make_review_bundle(
                    internal_id="page1_other_alpha",
                    question="Question one?",
                    answer="Alpha",
                    url="https://example.org/one",
                    segment_id="first_run",
                    archive_name="page_one.json",
                )
            ]
        },
    )
    write_json(
        second_state,
        {
            "candidates": [
                make_review_bundle(
                    internal_id="page2_other_beta",
                    question="Question two?",
                    answer="Beta",
                    url="https://example.org/two",
                    segment_id="second_run",
                    archive_name="page_two.json",
                )
            ]
        },
    )
    first_cache = tmp_path / "first_cache"
    second_cache = tmp_path / "second_cache"
    write_json(
        first_cache / "page_one.json",
        {
            "canonical_url": "https://example.org/one",
            "first_paragraph": "First page context.",
            "prose_text": "More first page context.",
        },
    )
    write_json(
        second_cache / "page_two.json",
        {
            "canonical_url": "https://example.org/two",
            "first_paragraph": "Second page context.",
            "prose_text": "More second page context.",
        },
    )
    output_dir = tmp_path / "prefetch"

    first_report = module.build_prefetch_artifacts(
        csv_path=csv_path,
        public_id_registry_path=registry_path,
        review_state_paths=[first_state],
        page_cache_dirs=[first_cache],
        output_dir=output_dir,
        segment_ids={"first_run"},
        expected_count=2,
    )
    assert first_report["topic_count"] == 1
    assert first_report["simpleqa_synth"]["unresolved_topic_count"] == 1

    second_report = module.build_prefetch_artifacts(
        csv_path=csv_path,
        public_id_registry_path=registry_path,
        review_state_paths=[second_state],
        page_cache_dirs=[second_cache],
        output_dir=output_dir,
        segment_ids={"second_run"},
        expected_count=2,
    )
    assert second_report["topic_count"] == 2
    assert second_report["simpleqa_synth"]["unresolved_topic_count"] == 0

    guidance = read_jsonl(output_dir / "topic_guidance_with_answer.jsonl")
    assert [row["topic_id"] for row in guidance] == [
        "simpleqa_synth_000001",
        "simpleqa_synth_000002",
    ]
    assert all(row["evidence_items"][0]["snippet_id"] == "S1" for row in guidance)
    fetched = read_jsonl(output_dir / "fetched_fulltext_pages.jsonl")
    assert len([row for row in fetched if row["source_type"] == "external"]) == 2
    assert len([row for row in fetched if row["source_type"] == "search"]) == 2
    assert not any("probe.example" in row["source_url"] for row in fetched)
    assert "First page context" in next(
        row["full_text"]
        for row in fetched
        if row["topic_id"] == "simpleqa_synth_000001"
        and row["source_type"] == "external"
    )
    id_map = read_jsonl(output_dir / "simpleqa_synth_id_map.jsonl")
    assert [row["internal_id"] for row in id_map] == [
        "page1_other_alpha",
        "page2_other_beta",
    ]


def test_simpleqa_verified_prefetch_preparation_repairs_only_unmatched_parentheses(
    tmp_path: Path,
) -> None:
    module = load_script("prepare_simpleqa_verified_prefetch")
    input_csv = tmp_path / "verified.csv"
    with input_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["original_index", "problem", "answer", "urls"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "original_index": "5",
                "problem": "Verified question?",
                "answer": "Gold",
                "urls": (
                    "https://example.org/article),"
                    "'https://en.wikipedia.org/wiki/Pillar_of_Fire_(sculpture)'"
                ),
            }
        )
    output_dir = tmp_path / "verified_prefetch"
    report = module.prepare_prefetch_topics(
        input_csv=input_csv,
        output_dir=output_dir,
        expected_count=1,
    )
    rows = read_jsonl(output_dir / "prefetch_topics.jsonl")
    assert rows == [
        {
            "id": "5",
            "question": "Verified question?",
            "answer": "Gold",
            "url": [
                "https://example.org/article",
                "https://en.wikipedia.org/wiki/Pillar_of_Fire_(sculpture)",
            ],
        }
    ]
    assert report["repaired_unmatched_trailing_parenthesis_count"] == 1


def test_verification_run_keeps_all_models_for_a_question_in_one_shard(
    tmp_path: Path,
) -> None:
    module = load_script("prepare_verification_agent_run")
    prefetch_path = tmp_path / "prefetch.jsonl"
    prefetch_rows = [
        {
            "topic_id": "q1",
            "query": "Question one?",
            "answer": "Gold one",
            "topic_guidance": "Ground with [S1].",
            "evidence_items": [
                {
                    "snippet_id": "S1",
                    "source_url": "https://example.org/one",
                    "source_title": "One",
                    "content": "Evidence one",
                }
            ],
            "answer_assessment": {},
        },
        {
            "topic_id": "q2",
            "query": "Question two?",
            "answer": "Gold two",
            "topic_guidance": "Ground with [S1].",
            "evidence_items": [
                {
                    "snippet_id": "S1",
                    "source_url": "https://example.org/two",
                    "source_title": "Two",
                    "content": "Evidence two",
                }
            ],
            "answer_assessment": {},
        },
    ]
    write_jsonl(prefetch_path, prefetch_rows)

    evaluation_dir = tmp_path / "evaluations"
    for model_name, suffix in (("vendor/model-a", "a"), ("vendor/model-b", "b")):
        write_jsonl(
            evaluation_dir / f"batch_{suffix}.jsonl",
            [
                {
                    "id": "q1",
                    "question": "Question one?",
                    "answer": "Gold one",
                    "predictions": [
                        {"model": model_name, "answer": f"Response {suffix}1"}
                    ],
                },
                {
                    "id": "q2",
                    "question": "Question two?",
                    "answer": "Gold two",
                    "predictions": [
                        {"model": model_name, "answer": f"Response {suffix}2"}
                    ],
                },
            ],
        )

    output_dir = tmp_path / "agent_run"
    report = module.prepare_verification_run(
        prefetch_inputs=[prefetch_path],
        evaluation_inputs=[evaluation_dir],
        output_dir=output_dir,
        questions_per_shard=1,
        expected_question_count=2,
        expected_response_count=4,
    )

    model_rows = read_jsonl(output_dir / "model_answers.jsonl")
    assert [row["original_index"] for row in model_rows] == ["q1", "q1", "q2", "q2"]
    lineage = read_jsonl(output_dir / "lineage_crosswalk.jsonl")
    assert [row["model_sequence_id"] for row in lineage] == [1, 2, 1, 2]
    first_shard = read_jsonl(output_dir / "shards/shard_001/model_answers.jsonl")
    second_shard = read_jsonl(output_dir / "shards/shard_002/model_answers.jsonl")
    assert {row["original_index"] for row in first_shard} == {"q1"}
    assert {row["original_index"] for row in second_shard} == {"q2"}
    assert report["question_count"] == 2
    assert report["response_count"] == 4
    assert report["shard_count"] == 2
