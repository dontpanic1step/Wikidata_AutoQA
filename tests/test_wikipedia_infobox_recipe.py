"""Tests for the Wikipedia infobox recipe runner."""

from __future__ import annotations

from contextlib import contextmanager
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from test_support import ROOT  # noqa: F401

from wikidata_simpleqa.route3_run_ledger import (
    atomic_write_json,
    build_segment_fingerprint,
    SegmentLedgerIndex,
    create_segment_manifest,
    derive_segment_manifest_state,
    file_sha256,
    ledger_summary,
    update_segment_manifest,
)
from wikidata_simpleqa.route3_artifacts import Route3CandidateIdentity
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from run_route3_review import _settings_from_fingerprint  # noqa: E402
from wikidata_simpleqa.route3_worker_support import (
    EndpointResumeState,
    effective_stream_random_seed as _effective_stream_random_seed,
)
from run_wikipedia_infobox_pipeline import parse_args as parse_worker_args, _stream_search_queries  # noqa: E402
from run_wikipedia_infobox_recipe import (  # noqa: E402
    RecipeItem,
    _apply_recipe_big_batch_mode,

    _base_segment_id_for_run,
    _combine_segment_records,
    _generation_protocol_compatibility_fingerprint,
    _parse_recipe,
    parse_args as parse_recipe_args,
    _recipe_status_payload,
    _recipe_summary,
    _require_clean_worktree,
    _require_top_up_prerequisites,
    _segment_fingerprint,
    _recipe_segment_budget,
    _decrement_recipe_budget,
    _segment_complete,
    _segment_stream_search_initial_offset,
    _segment_command,
    _segment_writer_lock,
    _validate_lifecycle_args,
    main as recipe_main,
)
from wikidata_simpleqa.search_client import (  # noqa: E402
    DUCKDUCKGO_COOLDOWN_FAILURE_THRESHOLD,
    DUCKDUCKGO_COOLDOWN_INITIAL_SECONDS,
    DUCKDUCKGO_COOLDOWN_MAX_SECONDS,
    DUCKDUCKGO_DDGS_MAX_ATTEMPTS,
)


def _recipe_args(**overrides):
    """Return a minimal recipe args namespace for helper tests."""
    values = {
        "stream_random_seed": None,
        "page_attempt_count": 10,
        "answer_type": "Person",
        "run_date": None,
        "target_time": "2024",
        "cutoff_year": 2025,
        "timeout_seconds": 30.0,
        "proxy": "none",
        "small_model_provider": "openrouter",
        "generation_model": "google/gemini-3-flash-preview",
        "small_model_api_key_env": "OPENROUTER_API_KEY",
        "small_model_base_url": "https://openrouter.ai/api/v1",
        "small_model_max_tokens": 4096,
        "duckduckgo_top_k": 5,
        "duckduckgo_parallel_queries": 3,
        "duckduckgo_prefer_ddgs": True,
        "duckduckgo_ddgs_backend": "auto",
        "duckduckgo_ddgs_max_attempts": DUCKDUCKGO_DDGS_MAX_ATTEMPTS,
        "duckduckgo_disable_fallback": [],
        "duckduckgo_cooldown": True,
        "duckduckgo_cooldown_failure_threshold": DUCKDUCKGO_COOLDOWN_FAILURE_THRESHOLD,
        "duckduckgo_cooldown_initial_seconds": DUCKDUCKGO_COOLDOWN_INITIAL_SECONDS,
        "duckduckgo_cooldown_max_seconds": DUCKDUCKGO_COOLDOWN_MAX_SECONDS,
        "generated_search_query_count": 2,
        "search_longtail_max_full_question_hit_rate": 0.3,
        "search_longtail_max_keyword_hit_rate": 0.3,
        "search_longtail_max_overall_hit_rate": 0.3,
        "stream_search_limit": 50,
        "stream_search_max_rounds": 10,
        "stream_batch_size": 10,
        "stream_discovery_max_retries": 5,
        "stream_discovery_retry_backoff_seconds": 10.0,
        "stream_discovery_retry_max_sleep_seconds": 60.0,
        "stream_reuse_cached_page_count": "all",
        "stream_fresh_cached_page_count": "fill",

        "wikipedia_429_backoff_seconds": 30.0,
        "wikipedia_429_max_backoff_seconds": 300.0,
        "wikipedia_429_recovery_seconds": 120.0,
        "stream_page_workers": 4,
        "wikipedia_concurrency_limit": 4,
        "duckduckgo_concurrency_limit": 4,
        "openrouter_generation_rewrite_concurrency_limit": 10,
        "second_stage_concurrency_limit": 10,
        "route3_answer_type_mode": "single",
        "route3_table_source_type": [],
        "route3_page_archive_dir": ROOT / "cache" / "route3_pages",
        "route3_infobox_max_removed_row_rate": 0.60,
        "route3_infobox_min_remaining_rows": 5,
        "enable_second_stage_grading": True,
        "second_stage_grading_accuracy_threshold": 0.1,
        "disable_auto_rerun_once": False,
        "compact_output": False,
        "compact_rejected_output": False,
        "big_batch_mode": False,
        "append_to_existing_run": False,
        "append_run_label": "",
        "resume": False,
        "status": False,
        "resolve_ambiguous": None,
        "run_id": "",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _pipeline_seed_args(**overrides):
    """Return a minimal pipeline args namespace for seed helper tests."""
    values = {
        "stream_random_seed": None,
        "run_group_id": "group",
        "run_segment_id": "fresh",
        "summary_output": Path("outputs/fresh_summary.json"),
        "stream_state": Path("outputs/fresh_state.json"),
        "start_from_endpoint": False,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _command_value(command: list[str], flag: str) -> str:
    """Return the value immediately following a command flag."""
    return command[command.index(flag) + 1]


def _parsed_main_args(
    root: Path,
    *,
    page_attempt_count: int,
    answer_type: str,
    answer_type_mode: str,
    resume: bool = False,
) -> SimpleNamespace:
    """Parse a complete formal recipe invocation rooted in a temporary directory."""
    argv = [
        "run_wikipedia_infobox_recipe.py",
        "--page-attempt-count",
        str(page_attempt_count),
        "--answer-type",
        answer_type,
        "--route3-answer-type-mode",
        answer_type_mode,
        "--run-id",
        "recipe",
        "--run-date",
        "2026-07-25",
        "--stream-random-seed",
        "42",
        "--segment-dir",
        str(root / "segments"),
        "--output",
        str(root / "accepted.jsonl"),
        "--rejected-output",
        str(root / "rejected.jsonl"),
        "--summary-output",
        str(root / "summary.json"),
        "--walkthrough-output",
        str(root / "walkthrough.md"),
    ]
    if resume:
        argv.append("--resume")
    with patch("sys.argv", argv):
        return parse_recipe_args()


def _complete_test_segment(
    root: Path,
    *,
    run_group_id: str,
    segment_id: str,
    page_ids: list[int],
    fingerprint: dict | None = None,
) -> tuple[dict, SegmentLedgerIndex]:
    """Create one complete manifest-backed segment for top-up tests."""
    fingerprint = fingerprint or build_segment_fingerprint(
        {
            "git_sha": "abc123",
            "prompt_hash": "prompt123",
            "run_group_id": run_group_id,
            "segment_id": segment_id,
            "generation": {"model": "google/gemini-3-flash-preview"},
            "answer_mode": {"answer_type": "AllTypes", "answer_type_mode": "all5"},
            "page_attempt_count": len(page_ids),
            "seed": 42,
            "cache_policy": {
                "reuse_cached_page_count": "all",
                "fresh_cached_page_count": "fill",
                "page_archive_dir": "cache/route3_pages",
            },
        }
    )
    segment_root = root / segment_id
    manifest_path = segment_root / "segment_manifest.json"
    manifest = create_segment_manifest(
        run_group_id=run_group_id,
        segment_id=segment_id,
        fingerprint=fingerprint,
        artifacts={},
    )
    index = SegmentLedgerIndex(
        allocation_dir=segment_root / "page_allocations",
        attempt_dir=segment_root / "page_attempts",
        run_group_id=run_group_id,
        segment_id=segment_id,
        run_group_segments_dir=root,
    )
    for ordinal, page_id in enumerate(page_ids, start=1):
        index.commit_allocation(canonical_page_id=page_id, page_source="fresh")
        index.commit_attempt(
            {
                "canonical_page_id": page_id,
                "attempt_number": 1,
                "status": "accepted" if ordinal <= len(page_ids) - 2 else "rejected",
                "accepted_records": [],
                "rejected_records": [],
                "error_details": {
                    "reason": (
                        "abandoned_ambiguous_external_call"
                        if ordinal == len(page_ids)
                        else "deterministic_rejection"
                    )
                },
            }
        )
    manifest = update_segment_manifest(
        manifest_path,
        manifest,
        segment_state=derive_segment_manifest_state(manifest, index),
        ledger_summary=ledger_summary(index),
        pre_review_quantity_prediction={},
    )
    return manifest, index

class WikipediaInfoboxRecipeTests(unittest.TestCase):
    def test_formal_run_requires_clean_worktree(self) -> None:
        with patch(
            "run_wikipedia_infobox_recipe.subprocess.run",
            return_value=SimpleNamespace(stdout=" M tracked.py\n"),
        ):
            with self.assertRaisesRegex(RuntimeError, "clean Git worktree"):
                _require_clean_worktree()

    def test_segment_writer_lock_is_exclusive_and_released_when_holder_is_killed(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            segment_root = Path(tmpdir) / "segment"
            child_code = (
                "import sys,time;"
                f"sys.path.insert(0,{str(SCRIPTS)!r});"
                "from run_wikipedia_infobox_recipe import _segment_writer_lock;"
                "from pathlib import Path;"
                f"lock=_segment_writer_lock(Path({str(segment_root)!r}));"
                "lock.__enter__();"
                "print('locked',flush=True);"
                "time.sleep(60)"
            )
            holder = subprocess.Popen(
                [sys._base_executable, "-c", child_code],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            try:
                self.assertEqual(holder.stdout.readline().strip(), "locked")
                with self.assertRaisesRegex(RuntimeError, "active recipe writer"):
                    with _segment_writer_lock(segment_root):
                        pass
            finally:
                holder.kill()
                holder.wait(timeout=10)

            with _segment_writer_lock(segment_root):
                self.assertTrue((segment_root / ".recipe_writer.lock").exists())

    def test_fresh_recipe_projects_zero_accepted_records_after_worker(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            args = _parsed_main_args(
                root,
                page_attempt_count=1,
                answer_type="Person",
                answer_type_mode="single",
            )
            lock_events = []

            @contextmanager
            def observed_lock(segment_root):
                self.assertFalse((segment_root / "segment_manifest.json").exists())
                lock_events.append("acquired")
                try:
                    yield
                finally:
                    lock_events.append("released")

            def checked_segment_command(**kwargs):
                self.assertEqual(lock_events, ["acquired"])
                return _segment_command(**kwargs)

            def checked_combine_segment_records(**kwargs):
                self.assertEqual(lock_events, ["acquired"])
                return _combine_segment_records(**kwargs)

            def fake_worker(command, *, cwd, check):  # noqa: ANN001
                self.assertEqual(lock_events, ["acquired"])
                index = SegmentLedgerIndex(
                    allocation_dir=Path(_command_value(command, "--page-allocation-ledger-dir")),
                    attempt_dir=Path(_command_value(command, "--page-attempt-ledger-dir")),
                    run_group_id="recipe",
                    segment_id="01_person_1",
                    run_group_segments_dir=Path(_command_value(command, "--run-group-segments-dir")),
                )
                index.commit_allocation(canonical_page_id=101, page_source="fresh")
                index.commit_attempt(
                    {
                        "canonical_page_id": 101,
                        "attempt_number": 1,
                        "status": "rejected",
                        "accepted_records": [],
                        "rejected_records": [],
                        "error_details": {"reason": "deterministic_rejection"},
                    }
                )
                atomic_write_json(
                    Path(_command_value(command, "--summary-output")),
                    {
                        "run_group_id": "recipe",
                        "run_segment_id": "01_person_1",
                        "run_date": "2026-07-25",
                        "stream_search_queries": ['insource:"wikitable"'],
                        "stream_state_stats": {"used": 1},
                        "stream_reused_cached_page_count": 0,
                        "stream_fresh_processed_page_count": 1,
                        "service_circuits": {},
                    },
                )
                return SimpleNamespace(returncode=0)

            with (
                patch("run_wikipedia_infobox_recipe.parse_args", return_value=args),
                patch("run_wikipedia_infobox_recipe._require_clean_worktree"),
                patch("run_wikipedia_infobox_recipe._git_sha", return_value="abc123"),
                patch("run_wikipedia_infobox_recipe._generation_prompt_hash", return_value="prompt123"),
                patch("run_wikipedia_infobox_recipe._segment_writer_lock", side_effect=observed_lock),
                patch("run_wikipedia_infobox_recipe._segment_command", side_effect=checked_segment_command),
                patch(
                    "run_wikipedia_infobox_recipe._combine_segment_records",
                    side_effect=checked_combine_segment_records,
                ),
                patch("run_wikipedia_infobox_recipe.subprocess.run", side_effect=fake_worker),
                patch("builtins.print"),
            ):
                result = recipe_main()

            manifest = json.loads(
                (root / "segments" / "01_person_1" / "segment_manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(result, 0)
            self.assertEqual(manifest["status"], "complete")
            self.assertEqual(manifest["pre_review_quantity_prediction"]["accepted_total"], 0)
            self.assertEqual((root / "accepted.jsonl").read_text(encoding="utf-8"), "")
            self.assertEqual(lock_events, ["acquired", "released"])

    def test_complete_segment_rebuilds_projection_without_worker(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            args = _parsed_main_args(
                root,
                page_attempt_count=2,
                answer_type="AllTypes",
                answer_type_mode="all5",
                resume=True,
            )
            with (
                patch("run_wikipedia_infobox_recipe._git_sha", return_value="abc123"),
                patch("run_wikipedia_infobox_recipe._generation_prompt_hash", return_value="prompt123"),
            ):
                fingerprint = _segment_fingerprint(
                    args=args,
                    item=RecipeItem("AllTypes", 2),
                    run_id="recipe",
                    segment_id="01_alltypes_2",
                    stream_random_seed=42,
                    table_source_types=["infobox", "wikitable"],
                    stream_reuse_cached_page_count="all",
                    stream_fresh_cached_page_count="fill",
                )
            _complete_test_segment(
                root / "segments",
                run_group_id="recipe",
                segment_id="01_alltypes_2",
                page_ids=[201, 202],
                fingerprint=fingerprint,
            )

            with (
                patch("run_wikipedia_infobox_recipe.parse_args", return_value=args),
                patch("run_wikipedia_infobox_recipe._require_clean_worktree"),
                patch("run_wikipedia_infobox_recipe._git_sha", return_value="abc123"),
                patch("run_wikipedia_infobox_recipe._generation_prompt_hash", return_value="prompt123"),
                patch("run_wikipedia_infobox_recipe.subprocess.run") as worker_run,
                patch("builtins.print"),
            ):
                result = recipe_main()

            worker_run.assert_not_called()
            manifest = json.loads(
                (root / "segments" / "01_alltypes_2" / "segment_manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(result, 0)
            self.assertEqual(manifest["pre_review_quantity_prediction"]["accepted_total"], 0)
            self.assertTrue((root / "segments" / "01_alltypes_2_accepted.jsonl").exists())
            self.assertTrue((root / "summary.json").exists())

    def test_blocked_worker_does_not_publish_combined_projection(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            args = _parsed_main_args(
                root,
                page_attempt_count=1,
                answer_type="Person",
                answer_type_mode="single",
            )

            def fake_worker(command, *, cwd, check):  # noqa: ANN001
                atomic_write_json(
                    Path(_command_value(command, "--summary-output")),
                    {
                        "run_group_id": "recipe",
                        "run_segment_id": "01_person_1",
                        "run_date": "2026-07-25",
                        "stream_state_stats": {"used": 0},
                        "service_circuits": {
                            "openrouter": {"open": True, "open_reason": "mock outage"}
                        },
                    },
                )
                return SimpleNamespace(returncode=0)

            with (
                patch("run_wikipedia_infobox_recipe.parse_args", return_value=args),
                patch("run_wikipedia_infobox_recipe._require_clean_worktree"),
                patch("run_wikipedia_infobox_recipe._git_sha", return_value="abc123"),
                patch("run_wikipedia_infobox_recipe._generation_prompt_hash", return_value="prompt123"),
                patch("run_wikipedia_infobox_recipe.subprocess.run", side_effect=fake_worker),
                patch("builtins.print"),
            ):
                result = recipe_main()

            manifest = json.loads(
                (root / "segments" / "01_person_1" / "segment_manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(result, 2)
            self.assertEqual(manifest["status"], "incomplete")
            self.assertEqual(manifest["blocking_reasons"], ["external_service"])
            self.assertFalse((root / "accepted.jsonl").exists())
            self.assertFalse((root / "summary.json").exists())

    def test_recipe_segments_use_separate_stream_states_and_shared_recipe_seed(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            segment_dir = Path(tmpdir) / "segments"
            args = _recipe_args()

            first_command, first_paths = _segment_command(
                args=args,
                item=RecipeItem(answer_type="Person", record_limit=40),
                index=0,
                run_id="recipe",
                segment_dir=segment_dir,
                stream_state_base=segment_dir / "stream_state.json",
                stream_search_initial_offset=0,
            )
            second_command, second_paths = _segment_command(
                args=args,
                item=RecipeItem(answer_type="Date", record_limit=40),
                index=1,
                run_id="recipe",
                segment_dir=segment_dir,
                stream_state_base=segment_dir / "stream_state.json",
                stream_search_initial_offset=50,
            )

        self.assertNotEqual(first_paths["stream_state"], second_paths["stream_state"])
        self.assertTrue(str(first_paths["stream_state"]).endswith("01_person_40_state.json"))
        self.assertTrue(str(second_paths["stream_state"]).endswith("02_date_40_state.json"))
        self.assertIn("--reset-stream-state", first_command)
        self.assertIn("--reset-stream-state", second_command)
        self.assertEqual(
            _command_value(first_command, "--stream-random-seed"),
            _command_value(second_command, "--stream-random-seed"),
        )
        self.assertEqual(_command_value(first_command, "--stream-search-initial-offset"), "0")
        self.assertEqual(_command_value(second_command, "--stream-search-initial-offset"), "50")

        self.assertEqual(
            _command_value(first_command, "--generation-model"),
            "google/gemini-3-flash-preview",
        )
        self.assertNotIn("--small-model", first_command)
        self.assertNotIn("--enable-kelm-rewrite", first_command)
        self.assertNotIn("--kelm-rewrite-model", first_command)
        self.assertNotIn("--enable-rewrite", first_command)
        self.assertNotIn("--rewrite-model", first_command)

    def test_existing_segment_manifest_makes_worker_resume_without_reset(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            segment_dir = Path(tmpdir) / "segments"
            args = _recipe_args()
            command, paths = _segment_command(
                args=args,
                item=RecipeItem("Person", 10),
                index=0,
                run_id="recipe",
                segment_dir=segment_dir,
                stream_state_base=segment_dir / "stream_state.json",
                stream_search_initial_offset=0,
            )
            self.assertIn("--reset-stream-state", command)
            atomic_write_json(
                paths["manifest"],
                create_segment_manifest(
                    run_group_id="recipe",
                    segment_id="01_person_10",
                    fingerprint=build_segment_fingerprint({"page_attempt_count": 10}),
                    artifacts={},
                ),
            )

            resumed_command, resumed_paths = _segment_command(
                args=args,
                item=RecipeItem("Person", 10),
                index=0,
                run_id="recipe",
                segment_dir=segment_dir,
                stream_state_base=segment_dir / "stream_state.json",
                stream_search_initial_offset=0,
            )

        self.assertNotIn("--reset-stream-state", resumed_command)
        self.assertEqual(resumed_paths["ledger"], paths["ledger"])

    def test_segment_fingerprint_contains_required_inputs(self) -> None:
        args = _recipe_args(run_date="2026-07-24")
        with (
            patch("run_wikipedia_infobox_recipe._git_sha", return_value="abc123"),
            patch("run_wikipedia_infobox_recipe._generation_prompt_hash", return_value="prompt123"),
        ):
            fingerprint = _segment_fingerprint(
                args=args,
                item=RecipeItem("Person", 10),
                run_id="recipe",
                segment_id="01_person_10",
                stream_random_seed=42,
                table_source_types=["infobox", "wikitable"],
                stream_reuse_cached_page_count="all",
                stream_fresh_cached_page_count="fill",
            )

        inputs = fingerprint["inputs"]
        self.assertEqual(inputs["git_sha"], "abc123")
        self.assertEqual(inputs["prompt_hash"], "prompt123")
        self.assertEqual(inputs["page_attempt_count"], 10)
        self.assertEqual(inputs["generation"]["model"], "google/gemini-3-flash-preview")
        self.assertEqual(inputs["answer_mode"]["answer_type"], "Person")
        self.assertEqual(inputs["source_mode"], ["infobox", "wikitable"])
        self.assertEqual(inputs["seed"], 42)
        self.assertIn("table_ranking_and_filters", inputs)
        self.assertIn("duckduckgo", inputs)
        self.assertIn("second_stage", inputs)

        settings = _settings_from_fingerprint(fingerprint)
        self.assertEqual(settings.target_time, args.target_time)
        self.assertEqual(settings.run_date, "2026-07-24")
        self.assertEqual(settings.duckduckgo_top_k, args.duckduckgo_top_k)
        self.assertEqual(settings.second_stage_grading_accuracy_threshold, 0.1)


    def test_recipe_parses_alltypes_segment_and_commands_all5_mode(self) -> None:
        args = _recipe_args(
            page_attempt_count=200,
            answer_type="AllTypes",
            route3_answer_type_mode="all5",
        )
        items, reasoning_types = _parse_recipe(args)

        self.assertEqual(items, [RecipeItem(answer_type="AllTypes", record_limit=200)])
        self.assertEqual(reasoning_types, ["single_fact"])

        with tempfile.TemporaryDirectory() as tmpdir:
            segment_dir = Path(tmpdir) / "segments"
            command, paths = _segment_command(
                args=args,
                item=items[0],
                index=0,
                run_id="recipe",
                segment_dir=segment_dir,
                stream_state_base=segment_dir / "stream_state.json",
                stream_search_initial_offset=0,
            )

        self.assertEqual(_command_value(command, "--route3-answer-type-mode"), "all5")
        self.assertNotIn("--route3-answer-type", command)
        self.assertNotIn("--route3-pageview-prefilter", command)
        self.assertTrue(str(paths["accepted"]).endswith("01_alltypes_200_accepted.jsonl"))

    def test_formal_specific_answer_type_uses_single_mode_and_page_budget(self) -> None:
        items, reasoning_types = _parse_recipe(
            _recipe_args(
                page_attempt_count=20,
                answer_type="Person",
                route3_answer_type_mode="single",
            )
        )

        self.assertEqual(items, [RecipeItem(answer_type="Person", record_limit=20)])
        self.assertEqual(reasoning_types, ["single_fact"])

    def test_formal_answer_type_mode_combinations_are_strict(self) -> None:
        with self.assertRaisesRegex(ValueError, "AllTypes requires"):
            _parse_recipe(
                _recipe_args(
                    answer_type="AllTypes",
                    route3_answer_type_mode="single",
                )
            )
        with self.assertRaisesRegex(ValueError, "specific answer type requires"):
            _parse_recipe(
                _recipe_args(
                    answer_type="Person",
                    route3_answer_type_mode="all5",
                )
            )

    def test_formal_page_attempt_count_must_be_positive(self) -> None:
        with self.assertRaisesRegex(ValueError, "page-attempt-count must be positive"):
            _parse_recipe(_recipe_args(page_attempt_count=0))

    def test_legacy_recipe_input_flags_are_not_accepted(self) -> None:
        with patch(
            "sys.argv",
            [
                "run_wikipedia_infobox_recipe.py",
                "--page-attempt-count",
                "10",
                "--answer-type",
                "Person",
                "--recipe",
                "10 Person",
            ],
        ):
            with self.assertRaises(SystemExit):
                parse_recipe_args()

    def test_status_cli_requires_only_run_id_and_is_read_only(self) -> None:
        with patch(
            "sys.argv",
            ["run_wikipedia_infobox_recipe.py", "--run-id", "recipe", "--status"],
        ):
            args = parse_recipe_args()

        _validate_lifecycle_args(args)
        self.assertTrue(args.status)
        self.assertIsNone(args.page_attempt_count)
        self.assertIsNone(args.answer_type)

    def test_lifecycle_cli_requires_explicit_resume_relationships(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires --resume"):
            _validate_lifecycle_args(_recipe_args(resolve_ambiguous="retry"))
        with self.assertRaisesRegex(ValueError, "requires --append-to-existing-run"):
            _validate_lifecycle_args(_recipe_args(append_run_label="topup"))
        _validate_lifecycle_args(_recipe_args(resume=True, resolve_ambiguous="abandon"))

    def test_cli_help_and_root_runbook_cover_the_formal_lifecycle(self) -> None:
        help_output = io.StringIO()
        with (
            patch("sys.argv", ["run_wikipedia_infobox_recipe.py", "--help"]),
            patch("sys.stdout", help_output),
            self.assertRaises(SystemExit) as raised,
        ):
            parse_recipe_args()

        self.assertEqual(raised.exception.code, 0)
        runbook = (ROOT / "README.md").read_text(encoding="utf-8")
        for option in (
            "--page-attempt-count",
            "--answer-type",
            "--route3-answer-type-mode",
            "--run-id",
            "--run-date",
            "--status",
            "--resume",
            "--resolve-ambiguous",
            "--append-to-existing-run",
            "--append-run-label",
        ):
            with self.subTest(option=option):
                self.assertIn(option, help_output.getvalue())
                self.assertIn(option, runbook)
        self.assertIn("internal segment worker", runbook)
        self.assertIn("scripts/run_openrouter_night_batch.py` are historical", runbook)

    def test_formal_recipe_defaults_match_milestone(self) -> None:
        with patch(
            "sys.argv",
            [
                "run_wikipedia_infobox_recipe.py",
                "--page-attempt-count",
                "10",
                "--answer-type",
                "Person",
            ],
        ):
            args = parse_recipe_args()

        self.assertEqual(args.generation_model, "google/gemini-3-flash-preview")
        self.assertEqual(args.small_model_max_tokens, 4096)
        self.assertTrue(args.enable_second_stage_grading)
        self.assertEqual(args.second_stage_grading_accuracy_threshold, 0.1)
        self.assertEqual(args.stream_reuse_cached_page_count, "all")
        self.assertEqual(args.stream_fresh_cached_page_count, "fill")

    def test_internal_worker_defaults_match_formal_recipe(self) -> None:
        with patch(
            "sys.argv",
            [
                "run_wikipedia_infobox_pipeline.py",
                "--page-allocation-ledger-dir",
                "allocations",
                "--page-attempt-ledger-dir",
                "ledger",
                "--run-group-segments-dir",
                "segments",
                "--external-call-record-dir",
                "external_calls",
                "--ddg-verifier-result-dir",
                "ddg_results",
            ],
        ):
            args = parse_worker_args()

        self.assertEqual(args.generation_model, "google/gemini-3-flash-preview")
        self.assertEqual(args.small_model_max_tokens, 4096)
        self.assertTrue(args.enable_second_stage_grading)
        self.assertEqual(args.second_stage_grading_accuracy_threshold, 0.1)
        self.assertEqual(args.stream_reuse_cached_page_count, "all")
        self.assertEqual(args.stream_fresh_cached_page_count, "fill")
        self.assertEqual(args.stream_page_source, "table-search")
        self.assertEqual(_stream_search_queries(), ['insource:"wikitable"'])

    def test_removed_route3_options_are_rejected_by_formal_interfaces(self) -> None:
        removed_options = [
            "--candidate-input",
            "--enable-broad-table-search",
            "--enable-kelm-rewrite",
            "--enable-rest-summary-fallback",
            "--route3-extra-prompt",
            "--route3-llm-choose-table",
            "--route3-pageview-prefilter",
            "--route3-prose-leakage-scoring",
            "--route3-reasoning-type",
            "--route3-table-filter-mode",
            "--start-stage",
            "--stream-page-source",
            "--stream-search-query",
            "--stream-exclude-page-id-file",
            "--stream-reuse-cached-page-used-id-file",
            "--url-file",
        ]
        for parse, argv in (
            (
                parse_recipe_args,
                ["run_wikipedia_infobox_recipe.py", "--page-attempt-count", "1", "--answer-type", "Person"],
            ),
            (parse_worker_args, ["run_wikipedia_infobox_pipeline.py"]),
        ):
            for option in removed_options:
                with self.subTest(parser=parse.__module__, option=option):
                    with patch("sys.argv", [*argv, option, "removed"]):
                        with self.assertRaises(SystemExit):
                            parse()

    def test_recipe_segment_passes_route3_table_source_types(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            segment_dir = Path(tmpdir) / "segments"
            args = _recipe_args()

            command, _paths = _segment_command(
                args=args,
                item=RecipeItem(answer_type="Person", record_limit=40),
                index=0,
                run_id="recipe",
                segment_dir=segment_dir,
                stream_state_base=segment_dir / "stream_state.json",
                stream_search_initial_offset=0,
                table_source_types=["infobox"],
            )

        source_values = [
            command[index + 1]
            for index, value in enumerate(command)
            if value == "--route3-table-source-type"
        ]
        self.assertEqual(source_values, ["infobox"])

    def test_big_batch_mode_aligns_batch_size_without_compacting_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            segment_dir = Path(tmpdir) / "segments"
            args = _recipe_args(big_batch_mode=True, stream_search_limit=50)
            _apply_recipe_big_batch_mode(args)

            command, _paths = _segment_command(
                args=args,
                item=RecipeItem(answer_type="Person", record_limit=2000),
                index=0,
                run_id="recipe",
                segment_dir=segment_dir,
                stream_state_base=segment_dir / "stream_state.json",
                stream_search_initial_offset=0,
            )

        self.assertEqual(_command_value(command, "--stream-batch-size"), "50")
        self.assertEqual(_command_value(command, "--stream-search-max-rounds"), "500")
        self.assertNotIn("--compact-output", command)
        self.assertNotIn("--compact-rejected-output", command)
        self.assertIn("--big-batch-mode", command)
        self.assertEqual(_command_value(command, "--stream-discovery-max-retries"), "5")
        self.assertEqual(_command_value(command, "--wikipedia-429-backoff-seconds"), "30.0")

    def test_append_recipe_segment_uses_new_artifacts_without_old_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            segment_dir = Path(tmpdir) / "segments"
            args = _recipe_args(append_to_existing_run=True, append_run_label="topup1")

            command, paths = _segment_command(
                args=args,
                item=RecipeItem(answer_type="Person", record_limit=10),
                index=0,
                run_id="recipe",
                segment_dir=segment_dir,
                stream_state_base=segment_dir / "stream_state.json",
                stream_search_initial_offset=0,
                append_label="topup1",
                base_segment_id="01_person_20",
            )

        self.assertTrue(str(paths["accepted"]).endswith("01_person_20_topup1_accepted.jsonl"))
        self.assertTrue(str(paths["stream_state"]).endswith("01_person_20_topup1_state.json"))
        self.assertEqual(_command_value(command, "--stream-search-initial-offset"), "0")
        self.assertNotIn("--stream-exclude-page-id-file", command)
        self.assertNotIn("--stream-reuse-cached-page-used-id-file", command)
        self.assertIn("--reset-stream-state", command)

    def test_append_recipe_command_has_no_generic_rerun_controls(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            segment_dir = Path(tmpdir) / "segments"
            segment_dir.mkdir()
            args = _recipe_args(append_to_existing_run=True, append_run_label="topup1")

            command, _paths = _segment_command(
                args=args,
                item=RecipeItem(answer_type="Person", record_limit=2000),
                index=0,
                run_id="recipe",
                segment_dir=segment_dir,
                stream_state_base=segment_dir / "stream_state.json",
                stream_search_initial_offset=2400,
                append_label="topup1",
            )

        self.assertNotIn("--stream-rerun-pool-seed-file", command)
        self.assertNotIn("--stream-prefer-rerun-pool", command)
        self.assertNotIn("--stream-free-seeded-rerun-pool-on-completion", command)
        self.assertNotIn("--stream-auto-rerun-once", command)

    def test_append_subset_recipe_reuses_existing_answer_type_segment_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            segment_dir = Path(tmpdir) / "segments"
            segment_dir.mkdir()
            manifest_path = segment_dir / "02_place_2000" / "segment_manifest.json"
            atomic_write_json(
                manifest_path,
                create_segment_manifest(
                    run_group_id="recipe",
                    segment_id="02_place_2000",
                    fingerprint=build_segment_fingerprint({"page_attempt_count": 2000}),
                    artifacts={},
                ),
            )

            base_segment_id = _base_segment_id_for_run(
                segment_dir=segment_dir,
                item=RecipeItem(answer_type="Place", record_limit=933),
                index=0,
                append_label="topup_1",
            )

        self.assertEqual(base_segment_id, "02_place_2000")

    def test_top_up_preserves_old_files_and_reaches_thirty_unique_allocations(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            segment_dir = Path(tmpdir) / "segments"
            base_manifest, _base_index = _complete_test_segment(
                segment_dir,
                run_group_id="recipe",
                segment_id="01_alltypes_20",
                page_ids=list(range(1, 21)),
            )
            requested_inputs = dict(base_manifest["fingerprint"]["inputs"])
            requested_inputs["segment_id"] = "01_alltypes_20_topup_10"
            requested_inputs["page_attempt_count"] = 10
            requested_inputs["cache_policy"] = {
                **requested_inputs["cache_policy"],
                "reuse_cached_page_count": 0,
                "fresh_cached_page_count": 10,
            }
            requested_fingerprint = build_segment_fingerprint(requested_inputs)
            self.assertEqual(
                _generation_protocol_compatibility_fingerprint(base_manifest["fingerprint"])["sha256"],
                _generation_protocol_compatibility_fingerprint(requested_fingerprint)["sha256"],
            )
            old_hashes = {
                path.relative_to(segment_dir).as_posix(): file_sha256(path)
                for path in (segment_dir / "01_alltypes_20").rglob("*")
                if path.is_file()
            }

            _require_top_up_prerequisites(
                segment_dir=segment_dir,
                run_group_id="recipe",
                base_segment_id="01_alltypes_20",
                current_segment_id="01_alltypes_20_topup_10",
                requested_fingerprint=requested_fingerprint,
            )
            top_up_index = SegmentLedgerIndex(
                allocation_dir=segment_dir / "01_alltypes_20_topup_10" / "page_allocations",
                attempt_dir=segment_dir / "01_alltypes_20_topup_10" / "page_attempts",
                run_group_id="recipe",
                segment_id="01_alltypes_20_topup_10",
                run_group_segments_dir=segment_dir,
            )
            self.assertTrue({19, 20}.issubset(top_up_index.run_group_page_ids))
            with self.assertRaisesRegex(ValueError, "already allocated"):
                top_up_index.commit_allocation(canonical_page_id=20, page_source="cache")
            for page_id in range(21, 31):
                top_up_index.commit_allocation(canonical_page_id=page_id, page_source="fresh")

            self.assertEqual(top_up_index.run_group_page_ids, set(range(1, 31)))
            self.assertEqual(
                old_hashes,
                {
                    path.relative_to(segment_dir).as_posix(): file_sha256(path)
                    for path in (segment_dir / "01_alltypes_20").rglob("*")
                    if path.is_file()
                },
            )

    def test_top_up_rejects_incomplete_or_incompatible_base_segment(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            segment_dir = Path(tmpdir) / "segments"
            base_manifest, _index = _complete_test_segment(
                segment_dir,
                run_group_id="recipe",
                segment_id="01_alltypes_2",
                page_ids=[1, 2],
            )
            requested_inputs = dict(base_manifest["fingerprint"]["inputs"])
            requested_inputs["segment_id"] = "01_alltypes_2_topup"
            requested_inputs["page_attempt_count"] = 1
            requested_inputs["generation"] = {"model": "different-model"}
            with self.assertRaisesRegex(ValueError, "protocol fingerprint mismatch"):
                _require_top_up_prerequisites(
                    segment_dir=segment_dir,
                    run_group_id="recipe",
                    base_segment_id="01_alltypes_2",
                    current_segment_id="01_alltypes_2_topup",
                    requested_fingerprint=build_segment_fingerprint(requested_inputs),
                )

            manifest_path = segment_dir / "01_alltypes_2" / "segment_manifest.json"
            incomplete = dict(base_manifest)
            incomplete["status"] = "incomplete"
            atomic_write_json(manifest_path, incomplete)
            with self.assertRaisesRegex(ValueError, "complete prior segment"):
                _require_top_up_prerequisites(
                    segment_dir=segment_dir,
                    run_group_id="recipe",
                    base_segment_id="01_alltypes_2",
                    current_segment_id="01_alltypes_2_topup",
                    requested_fingerprint=base_manifest["fingerprint"],
                )
    def test_incomplete_existing_segment_is_not_reused(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            paths = {
                "accepted": root / "accepted.jsonl",
                "rejected": root / "rejected.jsonl",
                "summary": root / "summary.json",
                "manifest": root / "segment_manifest.json",
                "allocations": root / "page_allocations",
                "ledger": root / "page_attempts",
                "segments_dir": root,
            }
            paths["accepted"].write_text("", encoding="utf-8")
            paths["rejected"].write_text("", encoding="utf-8")
            paths["summary"].write_text(
                json.dumps({"record_limit": 2000, "stream_state_stats": {"used": 190}}),
                encoding="utf-8",
            )
            manifest = create_segment_manifest(
                run_group_id="group",
                segment_id="segment",
                fingerprint=build_segment_fingerprint({"page_attempt_count": 2000}),
                artifacts={},
            )
            atomic_write_json(paths["manifest"], manifest)

            self.assertFalse(_segment_complete(paths))

    def test_complete_segment_requires_terminal_allocations(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            segment_root = root / "segment"
            paths = {
                "manifest": segment_root / "segment_manifest.json",
                "allocations": segment_root / "page_allocations",
                "ledger": segment_root / "page_attempts",
                "segments_dir": root,
            }
            manifest = create_segment_manifest(
                run_group_id="group",
                segment_id="segment",
                fingerprint=build_segment_fingerprint({"page_attempt_count": 1}),
                artifacts={},
            )
            index = SegmentLedgerIndex(
                allocation_dir=paths["allocations"],
                attempt_dir=paths["ledger"],
                run_group_id="group",
                segment_id="segment",
                run_group_segments_dir=paths["segments_dir"],
            )
            manifest = update_segment_manifest(
                paths["manifest"],
                manifest,
                segment_state=derive_segment_manifest_state(manifest, index),
                ledger_summary={"primary_pages": 0},
                pre_review_quantity_prediction={},
            )
            self.assertFalse(_segment_complete(paths))

            index.commit_allocation(canonical_page_id=1, page_source="fresh")
            index.commit_attempt(
                {
                    "canonical_page_id": 1,
                    "attempt_number": 1,
                    "status": "accepted",
                    "accepted_records": [],
                    "rejected_records": [],
                    "error_details": {},
                }
            )
            update_segment_manifest(
                paths["manifest"],
                manifest,
                segment_state=derive_segment_manifest_state(manifest, index),
                ledger_summary={"primary_pages": 1},
                pre_review_quantity_prediction={},
            )

            self.assertTrue(_segment_complete(paths))

            blocked = json.loads(paths["manifest"].read_text(encoding="utf-8"))
            blocked["status"] = "incomplete"
            blocked["blocking_reasons"] = ["ambiguous"]
            atomic_write_json(paths["manifest"], blocked)
            self.assertFalse(_segment_complete(paths))
            self.assertEqual(_recipe_status_payload("group", root)["status"], "incomplete")

    def test_combine_segment_records_offsets_ids_for_append_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            accepted_path = root / "accepted.jsonl"
            rejected_path = root / "rejected.jsonl"
            accepted_path.write_text(
                json.dumps(
                    {
                        "id": "old",
                        "question": "q",
                        "answer_type": "Person",
                        "source_metadata": {
                            "page_id": 123,
                            "run_group_id": "recipe",
                            "segment_id": "01_person_10_topup1",
                            "canonical_page_id": 123,
                            "original_candidate_slot": "single",
                            "selected_source_table": {"table_type": "infobox"},
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            rejected_path.write_text("", encoding="utf-8")
            summaries = [
                {
                    "recipe_answer_type": "Person",
                    "recipe_record_limit": 10,
                    "segment_accepted_output": str(accepted_path),
                    "segment_rejected_output": str(rejected_path),
                    "run_segment_id": "01_person_10_topup1",
                    "run_date": "2026-05-25",
                    "summary_output": str(root / "summary.json"),
                }
            ]

            accepted, rejected = _combine_segment_records(
                run_id="recipe",
                segment_summaries=summaries,
                accepted_id_offset=48,
            )

        self.assertEqual(rejected, [])
        self.assertEqual(
            accepted[0]["id"],
            Route3CandidateIdentity(
                run_group_id="recipe",
                segment_id="01_person_10_topup1",
                canonical_page_id=123,
                original_candidate_slot="single",
            ).candidate_id,
        )
        self.assertEqual(
            accepted[0]["source_metadata"]["page_id_list_entry"],
            {"page_id": 123, "answer_type": "Person", "table_type": "infobox"},
        )

    def test_recipe_numeric_reuse_and_fresh_budgets_allocate_left_to_right(self) -> None:
        recipe_items = [
            RecipeItem(answer_type="Person", record_limit=40),
            RecipeItem(answer_type="Place", record_limit=40),
        ]
        remaining_reuse: int | str = 30
        remaining_fresh: int | str = 60

        first_reuse = _recipe_segment_budget(remaining_reuse, recipe_items[0].record_limit)
        first_fresh = _recipe_segment_budget(remaining_fresh, recipe_items[0].record_limit)
        remaining_reuse = _decrement_recipe_budget(remaining_reuse, 30)
        remaining_fresh = _decrement_recipe_budget(remaining_fresh, 10)
        second_reuse = _recipe_segment_budget(remaining_reuse, recipe_items[1].record_limit)
        second_fresh = _recipe_segment_budget(remaining_fresh, recipe_items[1].record_limit)

        self.assertEqual((first_reuse, first_fresh), (30, 40))
        self.assertEqual((second_reuse, second_fresh), (0, 40))
        self.assertEqual(remaining_fresh, 50)
    def test_recipe_segments_use_disjoint_table_search_offsets(self) -> None:
        recipe_items = [
            RecipeItem(answer_type="Person", record_limit=40),
            RecipeItem(answer_type="Place", record_limit=40),
            RecipeItem(answer_type="Other", record_limit=120),
            RecipeItem(answer_type="Date", record_limit=40),
        ]

        offsets = [
            _segment_stream_search_initial_offset(recipe_items, index, stream_search_limit=50)
            for index in range(len(recipe_items))
        ]

        self.assertEqual(offsets, [0, 50, 100, 250])

    def test_recipe_summary_uses_segment_wall_time_and_aggregates_states(self) -> None:
        args = _recipe_args(route3_extra_prompt=[], duckduckgo_parallel_queries=3)
        segment_summaries = [
            {
                "run_segment_id": "01_person_40",
                "recipe_answer_type": "Person",
                "recipe_record_limit": 40,
                "attempted_page_ids": 40,
                "accepted": 2,
                "rejected": 35,
                "retry_pending": 3,
                "wall_clock_seconds": 12.5,
                "random_seed": 123,
                "stream_state": "person_state.json",
                "stream_state_stats": {"used": 40, "accepted": 2, "rejected": 35, "rerun_pool": 3},
                "page_ids": [1, 2],
            },
            {
                "run_segment_id": "02_date_40",
                "recipe_answer_type": "Date",
                "recipe_record_limit": 40,
                "attempted_page_ids": 40,
                "accepted": 1,
                "rejected": 38,
                "retry_pending": 1,
                "wall_clock_seconds": 20.0,
                "random_seed": 456,
                "stream_state": "date_state.json",
                "stream_state_stats": {"used": 40, "accepted": 1, "rejected": 38, "rerun_pool": 1},

                "page_ids": [3, 4],
            },
        ]

        summary = _recipe_summary(
            args=args,
            run_id="recipe",
            recipe_items=[
                RecipeItem(answer_type="Person", record_limit=40),
                RecipeItem(answer_type="Date", record_limit=40),
            ],
            reasoning_types=["single_fact"],
            table_filter_modes=["not_number_dominant"],
            segment_summaries=segment_summaries,
            accepted_records=[],
            rejected_records=[],
            output=Path("accepted.jsonl"),
            rejected_output=Path("rejected.jsonl"),
            summary_output=Path("summary.json"),
            walkthrough_output=Path("walkthrough.md"),
            stream_state_base=Path("stream_state.json"),
            append_label="",
            wall_clock_seconds=0.5,
        )

        self.assertEqual(summary["wall_clock_seconds"], 32.5)
        self.assertEqual(summary["recipe_segment_wall_clock_seconds"], 32.5)
        self.assertEqual(summary["recipe_runner_wall_clock_seconds"], 0.5)
        self.assertEqual(summary["stream_state"], "separate_segment_stream_states")
        self.assertEqual(summary["stream_states"], ["person_state.json", "date_state.json"])
        self.assertEqual(summary["stream_state_stats"]["used"], 80)
        self.assertEqual(summary["retry_pending"], 4)

        self.assertEqual(summary["route3_table_source_types"], ["infobox", "wikitable"])
        self.assertTrue(summary["route3_prose_leakage_scoring_enabled"])

    def test_default_stream_seed_changes_for_incremental_runs(self) -> None:
        fresh_seed = _effective_stream_random_seed(_pipeline_seed_args())
        incremental_seed = _effective_stream_random_seed(
            _pipeline_seed_args(
                run_segment_id="incremental",
                summary_output=Path("outputs/incremental_summary.json"),
                start_from_endpoint=True,
            ),
            EndpointResumeState(accepted_records=[{"question": "done"}]),
        )
        explicit_seed = _effective_stream_random_seed(_pipeline_seed_args(stream_random_seed=42))

        self.assertNotEqual(fresh_seed, incremental_seed)
        self.assertEqual(explicit_seed, 42)


if __name__ == "__main__":
    unittest.main()
