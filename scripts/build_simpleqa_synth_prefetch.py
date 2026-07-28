"""Build offline Verification Agent prefetch artifacts for SimpleQA Synth.

The builder joins public benchmark IDs to internal candidate IDs through the
durable public-ID registry, then locates the authoritative review record,
archived page, and stored DuckDuckGo snippets. It emits the same four primary
artifacts as the answer-aware Verification Agent prefetch runner.

The command is merge-safe. Separate generation runs may invoke it sequentially
with the same output directory and disjoint ``--segment-id`` values. Existing
topics are retained, identical duplicates are accepted, and conflicts fail.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


DEFAULT_CSV = Path(
    "outputs/evaluation_benchmarks/"
    "wikipedia_stream_recipe_integrated_2026_07_28/simpleqa_synth.csv"
)
DEFAULT_REVIEW_STATE = Path(
    "outputs/reviews/"
    "integrated_wikipedia_stream_recipe_3500alltypes_single_fact_2026_07_26_"
    "and_place_7000_excluding_alltypes_2026_07_27/review_state.json"
)
DEFAULT_PUBLIC_ID_REGISTRY = Path("outputs/public_ids/simpleqa_synth.json")
DEFAULT_PAGE_CACHE = Path("cache/route3_pages")
DEFAULT_EXPECTED_COUNT = 328
OUTPUT_SCHEMA_VERSION = 1

GUIDANCE_FILENAME = "topic_guidance_with_answer.jsonl"
FETCHED_FILENAME = "fetched_fulltext_pages.jsonl"
TRACE_FILENAME = "topic_grounding_trace_with_answer.jsonl"
REPORT_FILENAME = "run_prefetch_topic_evidence_with_answer_report.json"
TOPICS_FILENAME = "prefetch_topics.jsonl"
ID_MAP_FILENAME = "simpleqa_synth_id_map.jsonl"


def main() -> None:
    args = parse_args()
    report = build_prefetch_artifacts(
        csv_path=Path(args.csv),
        public_id_registry_path=Path(args.public_id_registry),
        review_state_paths=[Path(path) for path in args.review_state],
        page_cache_dirs=[Path(path) for path in args.page_cache_dir],
        output_dir=Path(args.output_dir),
        segment_ids=set(args.segment_id),
        expected_count=args.expected_count,
        max_page_chars=args.max_page_chars,
        max_ddg_results_per_topic=args.max_ddg_results_per_topic,
        include_answer_probe=args.include_answer_probe,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    unresolved_count = report["simpleqa_synth"]["unresolved_topic_count"]
    if args.require_complete and unresolved_count:
        raise SystemExit(
            "Prefetch merge is incomplete: "
            f"{unresolved_count} target topics remain unresolved."
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build and merge offline answer-aware prefetch artifacts for the "
            "328-question SimpleQA Synth benchmark."
        )
    )
    parser.add_argument("--csv", default=str(DEFAULT_CSV))
    parser.add_argument(
        "--public-id-registry",
        default=str(DEFAULT_PUBLIC_ID_REGISTRY),
    )
    parser.add_argument(
        "--review-state",
        action="append",
        default=None,
        help="Review-state JSON. Repeat for multiple generation runs.",
    )
    parser.add_argument(
        "--page-cache-dir",
        action="append",
        default=None,
        help="Page archive directory. Repeat or invoke the command again for another run.",
    )
    parser.add_argument(
        "--segment-id",
        action="append",
        default=[],
        help="Only add candidates from this segment. Repeat to select multiple segments.",
    )
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--expected-count", type=int, default=DEFAULT_EXPECTED_COUNT)
    parser.add_argument("--max-page-chars", type=int, default=30_000)
    parser.add_argument("--max-ddg-results-per-topic", type=int, default=15)
    parser.add_argument(
        "--include-answer-probe",
        action="store_true",
        help="Include answer-bearing DDG probe queries in fetched-page candidates.",
    )
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Exit nonzero after writing the merge if any target topic is unresolved.",
    )
    args = parser.parse_args()
    if args.review_state is None:
        args.review_state = [str(DEFAULT_REVIEW_STATE)]
    if args.page_cache_dir is None:
        args.page_cache_dir = [str(DEFAULT_PAGE_CACHE)]
    return args


def build_prefetch_artifacts(
    *,
    csv_path: Path,
    public_id_registry_path: Path,
    review_state_paths: list[Path],
    page_cache_dirs: list[Path],
    output_dir: Path,
    segment_ids: set[str] | None = None,
    expected_count: int = DEFAULT_EXPECTED_COUNT,
    max_page_chars: int = 30_000,
    max_ddg_results_per_topic: int = 15,
    include_answer_probe: bool = False,
) -> dict[str, Any]:
    if max_page_chars <= 0:
        raise ValueError("max_page_chars must be positive")
    if max_ddg_results_per_topic < 0:
        raise ValueError("max_ddg_results_per_topic must be non-negative")

    target_rows = load_target_rows(csv_path)
    if expected_count and len(target_rows) != expected_count:
        raise ValueError(
            f"Expected {expected_count} SimpleQA Synth rows, found {len(target_rows)}"
        )
    public_to_internal = load_public_id_assignments(public_id_registry_path)
    target_by_internal: dict[str, dict[str, Any]] = {}
    for row in target_rows:
        public_id = row["id"]
        internal_id = public_to_internal.get(public_id)
        if not internal_id:
            raise ValueError(f"Public ID has no registry assignment: {public_id}")
        if internal_id in target_by_internal:
            raise ValueError(f"Duplicate internal ID in target CSV: {internal_id}")
        row["internal_id"] = internal_id
        target_by_internal[internal_id] = row

    selected_segments = {value.strip() for value in (segment_ids or set()) if value.strip()}
    matched_bundles = load_matching_review_bundles(
        review_state_paths,
        target_internal_ids=set(target_by_internal),
        segment_ids=selected_segments,
    )

    existing = load_existing_outputs(output_dir)
    additions: list[dict[str, Any]] = []
    archive_found_count = 0
    archive_missing_count = 0
    ddg_result_count = 0
    question_revision_count = 0
    answer_revision_count = 0
    for internal_id, bundle in matched_bundles.items():
        target = target_by_internal[internal_id]
        built = build_topic_artifacts(
            target=target,
            bundle=bundle,
            page_cache_dirs=page_cache_dirs,
            max_page_chars=max_page_chars,
            max_ddg_results_per_topic=max_ddg_results_per_topic,
            include_answer_probe=include_answer_probe,
        )
        additions.append(built)
        archive_found_count += int(built["archive_found"])
        archive_missing_count += int(not built["archive_found"])
        ddg_result_count += built["ddg_result_count"]
        question_revision_count += int(built["question_revised_after_review"])
        answer_revision_count += int(built["answer_revised_after_review"])

    merged = merge_outputs(existing=existing, additions=additions)
    target_order = [row["id"] for row in target_rows]
    write_merged_outputs(output_dir=output_dir, merged=merged, target_order=target_order)

    completed_ids = set(merged["guidance"])
    unresolved = [row for row in target_rows if row["id"] not in completed_ids]
    report = {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "topic_count": len(completed_ids),
        "failed_topic_count": 0,
        "external_urls_enabled": True,
        "topic_grounding_path": str((output_dir / GUIDANCE_FILENAME).resolve()),
        "topic_guidance_path": str((output_dir / GUIDANCE_FILENAME).resolve()),
        "fetched_fulltext_path": str((output_dir / FETCHED_FILENAME).resolve()),
        "topic_grounding_trace_path": str((output_dir / TRACE_FILENAME).resolve()),
        "simpleqa_synth": {
            "target_csv": str(csv_path.resolve()),
            "target_csv_sha256": sha256_file(csv_path),
            "target_topic_count": len(target_rows),
            "added_or_confirmed_topic_count": len(additions),
            "completed_topic_count": len(completed_ids),
            "unresolved_topic_count": len(unresolved),
            "unresolved_topics": [
                {"id": row["id"], "internal_id": row["internal_id"]}
                for row in unresolved
            ],
            "review_states": [str(path.resolve()) for path in review_state_paths],
            "page_cache_dirs": [str(path.resolve()) for path in page_cache_dirs],
            "segment_ids": sorted(selected_segments),
            "archive_found_in_this_invocation": archive_found_count,
            "archive_missing_in_this_invocation": archive_missing_count,
            "ddg_results_added_in_this_invocation": ddg_result_count,
            "question_revisions_after_review_in_this_invocation": question_revision_count,
            "answer_revisions_after_review_in_this_invocation": answer_revision_count,
        },
    }
    atomic_write_json(output_dir / REPORT_FILENAME, report)
    return report


def load_target_rows(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"SimpleQA Synth CSV not found: {path}")
    rows: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_questions: set[str] = set()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for line_number, raw in enumerate(csv.DictReader(handle), start=2):
            public_id = clean_text(raw.get("id"))
            question = clean_text(raw.get("problem"))
            answer = clean_text(raw.get("answer"))
            urls = parse_urls(raw.get("urls"))
            if not public_id or not question or not answer or not urls:
                raise ValueError(f"Incomplete target CSV row at line {line_number}")
            if public_id in seen_ids:
                raise ValueError(f"Duplicate public ID in target CSV: {public_id}")
            if question in seen_questions:
                raise ValueError(f"Duplicate question text in target CSV: {question}")
            seen_ids.add(public_id)
            seen_questions.add(question)
            rows.append(
                {
                    "id": public_id,
                    "question": question,
                    "answer": answer,
                    "urls": urls,
                }
            )
    return rows


def load_public_id_assignments(path: Path) -> dict[str, str]:
    payload = load_json_object(path)
    assignments = payload.get("assignments")
    if not isinstance(assignments, list):
        raise ValueError(f"Public-ID registry has no assignments list: {path}")
    out: dict[str, str] = {}
    for item in assignments:
        if not isinstance(item, dict):
            raise ValueError(f"Invalid public-ID assignment in {path}")
        public_id = clean_text(item.get("public_id"))
        internal_id = clean_text(item.get("candidate_id"))
        if not public_id or not internal_id:
            raise ValueError(f"Incomplete public-ID assignment in {path}")
        if public_id in out and out[public_id] != internal_id:
            raise ValueError(f"Conflicting public-ID assignment: {public_id}")
        out[public_id] = internal_id
    return out


def load_matching_review_bundles(
    paths: Iterable[Path],
    *,
    target_internal_ids: set[str],
    segment_ids: set[str],
) -> dict[str, dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}
    for path in paths:
        payload = load_json_object(path)
        candidates = payload.get("candidates")
        if not isinstance(candidates, list):
            raise ValueError(f"Review state has no candidates list: {path}")
        for bundle in candidates:
            if not isinstance(bundle, dict):
                continue
            artifact = bundle.get("artifact")
            active = bundle.get("active_record")
            if not isinstance(artifact, dict) or not isinstance(active, dict):
                continue
            internal_id = clean_text(artifact.get("id"))
            if internal_id not in target_internal_ids:
                continue
            if clean_text(active.get("id")) != internal_id:
                raise ValueError(f"Review artifact/record ID mismatch: {internal_id}")
            metadata = active.get("source_metadata") or {}
            segment_id = clean_text(metadata.get("segment_id"))
            if segment_ids and segment_id not in segment_ids:
                continue
            compact = {
                "artifact": artifact,
                "active_record": active,
                "review_state": str(path.resolve()),
            }
            if internal_id in selected:
                assert_same_json(
                    selected[internal_id]["active_record"],
                    active,
                    label=f"review record {internal_id}",
                )
            else:
                selected[internal_id] = compact
    return selected


def build_topic_artifacts(
    *,
    target: dict[str, Any],
    bundle: dict[str, Any],
    page_cache_dirs: list[Path],
    max_page_chars: int,
    max_ddg_results_per_topic: int,
    include_answer_probe: bool,
) -> dict[str, Any]:
    active = bundle["active_record"]
    metadata = active.get("source_metadata") or {}
    public_id = target["id"]
    internal_id = target["internal_id"]
    question = target["question"]
    answer = target["answer"]

    active_question = clean_text(active.get("question") or active.get("canonical_question"))
    active_answer = clean_text(active.get("answer"))
    question_revised_after_review = active_question != question
    answer_revised_after_review = active_answer != answer

    evidence = active.get("evidence") or {}
    evidence_text = clean_multiline(evidence.get("text"))
    source_url = clean_text(evidence.get("url") or metadata.get("canonical_url"))
    source_title = clean_text(evidence.get("source_title") or metadata.get("page_title"))
    if not evidence_text or not source_url:
        raise ValueError(f"Missing authoritative evidence for {public_id}")
    if source_url not in target["urls"]:
        raise ValueError(f"Evidence URL is not present in final CSV for {public_id}")
    validation = active.get("validation") or {}
    if validation.get("answer_in_evidence") is not True:
        raise ValueError(f"Final record did not pass answer-in-evidence validation: {public_id}")

    page_archive_metadata = metadata.get("route3_page_archive") or {}
    if answer_revised_after_review and not evidence_contains_answer(evidence_text, answer):
        raise ValueError(
            f"Final CSV answer is not present in selected evidence for {public_id}"
        )
    stored_archive_path = clean_text(
        page_archive_metadata.get("archive_path")
        if isinstance(page_archive_metadata, dict)
        else ""
    )
    archive_path = locate_page_archive(stored_archive_path, page_cache_dirs)
    archive_payload = load_json_object(archive_path) if archive_path is not None else {}
    if archive_payload:
        archived_url = clean_text(
            archive_payload.get("canonical_url") or archive_payload.get("source_url")
        )
        if archived_url and archived_url != source_url:
            raise ValueError(f"Cached page URL mismatch for {public_id}: {archive_path}")

    external_full_text = compose_external_full_text(
        evidence_text=evidence_text,
        archive_payload=archive_payload,
        max_chars=max_page_chars,
    )
    external_url_id = f"{public_id}_EXT_U1"
    external_row = {
        "topic_id": public_id,
        "query": question,
        "url_id": external_url_id,
        "source_url": source_url,
        "source_title": source_title,
        "source_type": "external",
        "candidate_ids": [internal_id],
        "query_ids": ["trusted_url"],
        "fetch_error": None,
        "full_text": external_full_text,
    }

    ddg_rows, ddg_queries, ddg_candidates = build_ddg_rows(
        public_id=public_id,
        internal_id=internal_id,
        question=question,
        features=active.get("search_verification_features") or {},
        max_results=max_ddg_results_per_topic,
        include_answer_probe=include_answer_probe,
    )
    fetched_rows = [external_row, *ddg_rows]

    evidence_item = {
        "snippet_id": "S1",
        "source_url": source_url,
        "source_title": source_title,
        "content": evidence_text,
    }
    derivation = clean_text(metadata.get("derivation_summary"))
    if derivation and not (question_revised_after_review or answer_revised_after_review):
        derivation = re.sub(r"\bT\d+_E\d+\b", "the selected evidence", derivation)
        topic_guidance = f"{derivation.rstrip('.')} [S1]."
    else:
        topic_guidance = (
            "Use the selected table or infobox evidence [S1] to ground the requested fact."
        )
    answer_assessment = {
        "provided_answer": answer,
        "reasoning": (
            "The final reviewed candidate passed answer-in-evidence validation against "
            "the selected source table or infobox [S1]."
        ),
        "is_supported": True,
        "is_unique_answer": True,
        "canonical_answer": answer,
    }
    guidance = {
        "topic_id": public_id,
        "query": question,
        "answer": answer,
        "topic_guidance": topic_guidance,
        "evidence_items": [evidence_item],
        "answer_assessment": answer_assessment,
    }
    page_traces = [fetched_page_trace(row, max_page_chars) for row in fetched_rows]
    trace = {
        "topic_id": public_id,
        "query": question,
        "answer": answer,
        "claims": [{"claim_id": f"{public_id}_C1", "claim_text": question}],
        "search_queries": ddg_queries,
        "raw_search_candidates": ddg_candidates,
        "search_candidates_for_selection": ddg_candidates,
        "selected_search_urls": [
            {"url_id": row["url_id"], "url": row["source_url"]} for row in ddg_rows
        ],
        "external_fetched_pages": page_traces[:1],
        "selected_search_fetched_pages": page_traces[1:],
        "merged_fetched_pages": page_traces,
        "evidence_items": [
            {
                "snippet_id": "S1",
                "topic_id": public_id,
                "url_id": external_url_id,
                "source_url": source_url,
                "source_title": source_title,
                "source_type": "external",
                "relevant_text": evidence_text,
                "summary": derivation,
                "content": evidence_text,
            }
        ],
        "topic_brief": topic_guidance,
        "answer_assessment": answer_assessment,
        "simpleqa_synth": {
            "internal_id": internal_id,
            "segment_id": clean_text(metadata.get("segment_id")),
            "review_state": bundle["review_state"],
            "stored_archive_path": stored_archive_path,
            "resolved_archive_path": str(archive_path.resolve()) if archive_path else "",
        },
    }
    topic = {
        "id": public_id,
        "question": question,
        "answer": answer,
        "url": target["urls"],
    }
    id_map = {
        "id": public_id,
        "internal_id": internal_id,
        "query": question,
        "segment_id": clean_text(metadata.get("segment_id")),
        "source_url": source_url,
        "review_question": active_question,
        "review_answer": active_answer,
        "question_revised_after_review": question_revised_after_review,
        "answer_revised_after_review": answer_revised_after_review,
    }
    return {
        "topic_id": public_id,
        "guidance": guidance,
        "fetched": fetched_rows,
        "trace": trace,
        "topic": topic,
        "id_map": id_map,
        "archive_found": archive_path is not None,
        "ddg_result_count": len(ddg_rows),
        "question_revised_after_review": question_revised_after_review,
        "answer_revised_after_review": answer_revised_after_review,
    }


def build_ddg_rows(
    *,
    public_id: str,
    internal_id: str,
    question: str,
    features: dict[str, Any],
    max_results: int,
    include_answer_probe: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    queries = features.get("queries")
    if not isinstance(queries, list):
        queries = []
    audit_queries: list[dict[str, Any]] = []
    candidate_rows: list[dict[str, Any]] = []
    by_url: dict[str, dict[str, Any]] = {}
    for raw_query in queries:
        if not isinstance(raw_query, dict) or raw_query.get("error") is True:
            continue
        category = clean_text(raw_query.get("query_category"))
        if category == "answer_probe" and not include_answer_probe:
            continue
        query_name = clean_text(raw_query.get("query_name")) or category or "stored_query"
        query_text = clean_text(raw_query.get("query"))
        audit_queries.append(
            {
                "query_id": query_name,
                "query": query_text,
                "query_category": category,
                "source": "stored_ddg",
            }
        )
        results = raw_query.get("results")
        if not isinstance(results, list):
            continue
        for result in results:
            if not isinstance(result, dict):
                continue
            url = clean_text(result.get("url"))
            title = clean_text(result.get("title"))
            snippet = clean_text(result.get("snippet"))
            if not url or not (title or snippet):
                continue
            candidate = {
                "query_id": query_name,
                "query": query_text,
                "query_category": category,
                "title": title,
                "snippet": snippet,
                "url": url,
                "answer_hit": bool(result.get("answer_hit")),
            }
            candidate_rows.append(candidate)
            existing = by_url.get(url)
            if existing is None:
                by_url[url] = {
                    "title": title,
                    "snippet": snippet,
                    "query_ids": [query_name],
                }
            elif query_name not in existing["query_ids"]:
                existing["query_ids"].append(query_name)

    rows: list[dict[str, Any]] = []
    for url, item in list(by_url.items())[:max_results]:
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
        full_text = "\n\n".join(value for value in (item["title"], item["snippet"]) if value)
        rows.append(
            {
                "topic_id": public_id,
                "query": question,
                "url_id": f"{public_id}_DDG_{digest}",
                "source_url": url,
                "source_title": item["title"],
                "source_type": "search",
                "candidate_ids": [internal_id],
                "query_ids": item["query_ids"],
                "fetch_error": None,
                "full_text": full_text,
            }
        )
    return rows, audit_queries, candidate_rows


def locate_page_archive(stored_path: str, cache_dirs: Iterable[Path]) -> Path | None:
    if not stored_path:
        return None
    filename = PurePosixPath(stored_path.replace("\\", "/")).name
    matches: list[Path] = []
    for directory in cache_dirs:
        candidate = directory / filename
        if candidate.is_file():
            matches.append(candidate)
    if not matches:
        return None
    hashes = {sha256_file(path) for path in matches}
    if len(hashes) != 1:
        raise ValueError(f"Conflicting page archives for {filename}: {matches}")
    return matches[0]


def compose_external_full_text(
    *, evidence_text: str, archive_payload: dict[str, Any], max_chars: int
) -> str:
    parts = [evidence_text]
    first_paragraph = clean_multiline(archive_payload.get("first_paragraph"))
    prose = clean_multiline(archive_payload.get("prose_text"))
    for value in (first_paragraph, prose):
        if value and value not in parts:
            parts.append(value)
    text = "\n\n".join(parts)
    if len(text) <= max_chars:
        return text
    if len(evidence_text) >= max_chars:
        return evidence_text
    remaining = max_chars - len(evidence_text) - 2
    return evidence_text + "\n\n" + "\n\n".join(parts[1:])[: max(0, remaining)]


def fetched_page_trace(row: dict[str, Any], max_page_chars: int) -> dict[str, Any]:
    text_len = len(clean_multiline(row.get("full_text")))
    return {
        "topic_id": row["topic_id"],
        "query": row["query"],
        "url_id": row["url_id"],
        "source_url": row["source_url"],
        "source_title": row["source_title"],
        "source_type": row["source_type"],
        "candidate_ids": list(row.get("candidate_ids") or []),
        "query_ids": list(row.get("query_ids") or []),
        "fetch_error": row.get("fetch_error"),
        "text_char_len": text_len,
        "is_truncated": text_len >= max_page_chars if text_len else False,
        "max_page_text_chars": max_page_chars,
    }


def load_existing_outputs(output_dir: Path) -> dict[str, dict[Any, Any]]:
    guidance = rows_by_unique_key(
        read_jsonl_if_exists(output_dir / GUIDANCE_FILENAME),
        lambda row: clean_text(row.get("topic_id")),
        GUIDANCE_FILENAME,
    )
    trace = rows_by_unique_key(
        read_jsonl_if_exists(output_dir / TRACE_FILENAME),
        lambda row: clean_text(row.get("topic_id")),
        TRACE_FILENAME,
    )
    topics = rows_by_unique_key(
        read_jsonl_if_exists(output_dir / TOPICS_FILENAME),
        lambda row: clean_text(row.get("id")),
        TOPICS_FILENAME,
    )
    id_map = rows_by_unique_key(
        read_jsonl_if_exists(output_dir / ID_MAP_FILENAME),
        lambda row: clean_text(row.get("id")),
        ID_MAP_FILENAME,
    )
    fetched = rows_by_unique_key(
        read_jsonl_if_exists(output_dir / FETCHED_FILENAME),
        lambda row: (clean_text(row.get("topic_id")), clean_text(row.get("url_id"))),
        FETCHED_FILENAME,
    )
    return {
        "guidance": guidance,
        "fetched": fetched,
        "trace": trace,
        "topics": topics,
        "id_map": id_map,
    }


def merge_outputs(
    *, existing: dict[str, dict[Any, Any]], additions: list[dict[str, Any]]
) -> dict[str, dict[Any, Any]]:
    merged = {name: dict(rows) for name, rows in existing.items()}
    for item in additions:
        topic_id = item["topic_id"]
        merge_one(merged["guidance"], topic_id, item["guidance"], GUIDANCE_FILENAME)
        merge_one(merged["trace"], topic_id, item["trace"], TRACE_FILENAME)
        merge_one(merged["topics"], topic_id, item["topic"], TOPICS_FILENAME)
        merge_one(merged["id_map"], topic_id, item["id_map"], ID_MAP_FILENAME)
        for row in item["fetched"]:
            key = (topic_id, row["url_id"])
            merge_one(merged["fetched"], key, row, FETCHED_FILENAME)
    return merged


def merge_one(target: dict[Any, Any], key: Any, row: Any, label: str) -> None:
    if key in target:
        assert_same_json(target[key], row, label=f"{label} key {key!r}")
    else:
        target[key] = row


def write_merged_outputs(
    *, output_dir: Path, merged: dict[str, dict[Any, Any]], target_order: list[str]
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    order = {topic_id: index for index, topic_id in enumerate(target_order)}
    unknown_offset = len(order)

    def topic_sort(topic_id: str) -> tuple[int, str]:
        return order.get(topic_id, unknown_offset), topic_id

    guidance = sorted(
        merged["guidance"].values(), key=lambda row: topic_sort(row["topic_id"])
    )
    traces = sorted(merged["trace"].values(), key=lambda row: topic_sort(row["topic_id"]))
    topics = sorted(merged["topics"].values(), key=lambda row: topic_sort(row["id"]))
    id_rows = sorted(merged["id_map"].values(), key=lambda row: topic_sort(row["id"]))
    fetched = sorted(
        merged["fetched"].values(),
        key=lambda row: (*topic_sort(row["topic_id"]), row["url_id"]),
    )
    atomic_write_jsonl(output_dir / GUIDANCE_FILENAME, guidance)
    atomic_write_jsonl(output_dir / FETCHED_FILENAME, fetched)
    atomic_write_jsonl(output_dir / TRACE_FILENAME, traces)
    atomic_write_jsonl(output_dir / TOPICS_FILENAME, topics)
    atomic_write_jsonl(output_dir / ID_MAP_FILENAME, id_rows)


def rows_by_unique_key(
    rows: Iterable[dict[str, Any]], key_fn: Any, label: str
) -> dict[Any, dict[str, Any]]:
    out: dict[Any, dict[str, Any]] = {}
    for row in rows:
        key = key_fn(row)
        if not key or (isinstance(key, tuple) and not all(key)):
            raise ValueError(f"Missing key in existing {label}")
        if key in out:
            raise ValueError(f"Duplicate key in existing {label}: {key!r}")
        out[key] = row
    return out


def evidence_contains_answer(evidence_text: str, answer: str) -> bool:
    normalized_evidence = clean_text(evidence_text).casefold()
    normalized_answer = clean_text(answer).casefold()
    return bool(normalized_answer and normalized_answer in normalized_evidence)


def parse_urls(value: Any) -> list[str]:
    text = clean_text(value)
    if not text:
        return []
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = [part.strip() for part in text.split(",")]
    if isinstance(parsed, str):
        parsed = [parsed]
    if not isinstance(parsed, list):
        raise ValueError(f"URL field must be a JSON list or comma-separated string: {text}")
    urls: list[str] = []
    for raw in parsed:
        url = clean_text(raw)
        if not url:
            continue
        if not url.startswith(("http://", "https://")):
            raise ValueError(f"Unsupported source URL: {url}")
        if url not in urls:
            urls.append(url)
    return urls


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def clean_multiline(value: Any) -> str:
    lines = [line.rstrip() for line in str(value or "").replace("\r\n", "\n").split("\n")]
    return "\n".join(lines).strip()


def load_json_object(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def read_jsonl_if_exists(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"Expected object at {path}:{line_number}")
            rows.append(value)
    return rows


def assert_same_json(left: Any, right: Any, *, label: str) -> None:
    if canonical_json(left) != canonical_json(right):
        raise ValueError(f"Conflicting duplicate {label}")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    content = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    atomic_write_text(path, content)


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
            temp_name = handle.name
        os.replace(temp_name, path)
    finally:
        if temp_name:
            Path(temp_name).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
