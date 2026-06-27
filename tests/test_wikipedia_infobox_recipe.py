"""Tests for the Wikipedia infobox recipe runner."""

from __future__ import annotations

import sys
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from test_support import ROOT  # noqa: F401

SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from run_wikipedia_infobox_pipeline import EndpointResumeState, _effective_stream_random_seed  # noqa: E402
from run_wikipedia_infobox_recipe import (  # noqa: E402
    RecipeItem,
    _apply_recipe_big_batch_mode,
    _append_stream_search_initial_offset,
    _base_segment_id_for_run,
    _combine_segment_records,
    _clear_rerun_pool_ids_from_states,
    _existing_recipe_page_ids,
    _matching_segment_rerun_pool_seed,
    _parse_recipe,
    _recipe_summary,
    _recipe_segment_budget,
    _decrement_recipe_budget,
    _segment_complete,
    _segment_used_count,
    _segment_stream_search_initial_offset,
    _segment_command,
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
        "run_date": None,
        "target_time": "2024",
        "cutoff_year": 2025,
        "timeout_seconds": 30.0,
        "proxy": "none",
        "small_model_provider": "openrouter",
        "generation_model": "openai/gpt-4.1-mini",
        "small_model_api_key_env": "OPENROUTER_API_KEY",
        "small_model_base_url": "https://openrouter.ai/api/v1",
        "small_model_max_tokens": 1200,
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
        "stream_page_source": "table-search",
        "stream_search_limit": 50,
        "stream_search_max_rounds": 10,
        "stream_batch_size": 10,
        "stream_discovery_max_retries": 5,
        "stream_discovery_retry_backoff_seconds": 10.0,
        "stream_discovery_retry_max_sleep_seconds": 60.0,
        "stream_reuse_cached_page_count": "all",
        "stream_fresh_cached_page_count": "fill",
        "stream_reuse_cached_page_used_id_file": [],
        "wikipedia_429_backoff_seconds": 30.0,
        "wikipedia_429_max_backoff_seconds": 300.0,
        "wikipedia_429_recovery_seconds": 120.0,
        "stream_page_workers": 4,
        "wikipedia_concurrency_limit": 4,
        "duckduckgo_concurrency_limit": 4,
        "openrouter_generation_rewrite_concurrency_limit": 10,
        "second_stage_concurrency_limit": 10,
        "route3_extra_prompt": [],
        "route3_answer_type_mode": "single",
        "route3_table_source_type": [],
        "route3_prose_leakage_scoring": True,
        "route3_llm_choose_table": False,
        "route3_page_archive_dir": ROOT / "cache" / "route3_pages",
        "route3_pageview_prefilter": False,
        "route3_pageview_window_months": 12,
        "route3_max_monthly_average_pageviews": 5000.0,
        "route3_max_underfilled_monthly_pageviews": 10000.0,
        "route3_pageview_unavailable_policy": "allow",
        "route3_infobox_max_removed_row_rate": 0.60,
        "route3_infobox_min_remaining_rows": 5,
        "disable_route3_table_filter_mode": [],
        "enable_kelm_rewrite": True,
        "kelm_rewrite_model": "openai/gpt-4.1-mini",
        "enable_second_stage_grading": True,
        "second_stage_grading_accuracy_threshold": 0.1,
        "disable_auto_rerun_once": False,
        "stream_search_query": ['insource:"wikitable"'],
        "enable_broad_table_search": False,
        "compact_output": False,
        "compact_rejected_output": False,
        "big_batch_mode": False,
        "append_to_existing_run": False,
        "append_run_label": "",
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
        "stream_rerun_pool_only": False,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _command_value(command: list[str], flag: str) -> str:
    """Return the value immediately following a command flag."""
    return command[command.index(flag) + 1]


class WikipediaInfoboxRecipeTests(unittest.TestCase):
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
                stream_exclusion_file=segment_dir / "recipe_page_id_exclusions.json",
                stream_search_initial_offset=0,
                reasoning_types=["single_fact"],
                table_filter_modes=["not_number_dominant"],
            )
            second_command, second_paths = _segment_command(
                args=args,
                item=RecipeItem(answer_type="Date", record_limit=40),
                index=1,
                run_id="recipe",
                segment_dir=segment_dir,
                stream_state_base=segment_dir / "stream_state.json",
                stream_exclusion_file=segment_dir / "recipe_page_id_exclusions.json",
                stream_search_initial_offset=50,
                reasoning_types=["single_fact"],
                table_filter_modes=["not_number_dominant"],
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
            _command_value(second_command, "--stream-exclude-page-id-file"),
            str(segment_dir / "recipe_page_id_exclusions.json"),
        )
        self.assertEqual(_command_value(first_command, "--generation-model"), "openai/gpt-4.1-mini")
        self.assertNotIn("--small-model", first_command)
        self.assertIn("--enable-kelm-rewrite", first_command)
        self.assertEqual(_command_value(first_command, "--kelm-rewrite-model"), "openai/gpt-4.1-mini")
        self.assertNotIn("--enable-rewrite", first_command)
        self.assertNotIn("--rewrite-model", first_command)

    def test_recipe_parses_alltypes_segment_and_commands_all5_mode(self) -> None:
        args = _recipe_args(
            recipe=["200 AllTypes", "single_fact"],
            answer_type_count=[],
            answer_types=[],
            per_answer_type=0,
            route3_reasoning_type=[],
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
                stream_exclusion_file=segment_dir / "recipe_page_id_exclusions.json",
                stream_search_initial_offset=0,
                reasoning_types=reasoning_types,
                table_filter_modes=["not_number_dominant"],
            )

        self.assertEqual(_command_value(command, "--route3-answer-type-mode"), "all5")
        self.assertNotIn("--route3-answer-type", command)
        self.assertEqual(_command_value(command, "--route3-max-underfilled-monthly-pageviews"), "10000.0")
        self.assertTrue(str(paths["accepted"]).endswith("01_alltypes_200_accepted.jsonl"))

    def test_recipe_segment_disables_route3_llm_table_choice_by_default(self) -> None:
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
                stream_exclusion_file=segment_dir / "recipe_page_id_exclusions.json",
                stream_search_initial_offset=0,
                reasoning_types=["single_fact"],
                table_filter_modes=["not_number_dominant"],
            )

        self.assertIn("--no-route3-llm-choose-table", command)

    def test_recipe_segment_can_enable_route3_llm_table_choice(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            segment_dir = Path(tmpdir) / "segments"
            args = _recipe_args(route3_llm_choose_table=True)

            command, _paths = _segment_command(
                args=args,
                item=RecipeItem(answer_type="Person", record_limit=40),
                index=0,
                run_id="recipe",
                segment_dir=segment_dir,
                stream_state_base=segment_dir / "stream_state.json",
                stream_exclusion_file=segment_dir / "recipe_page_id_exclusions.json",
                stream_search_initial_offset=0,
                reasoning_types=["single_fact"],
                table_filter_modes=["not_number_dominant"],
            )

        self.assertIn("--route3-llm-choose-table", command)
        self.assertNotIn("--no-route3-llm-choose-table", command)

    def test_recipe_segment_disables_pageview_prefilter_by_default(self) -> None:
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
                stream_exclusion_file=segment_dir / "recipe_page_id_exclusions.json",
                stream_search_initial_offset=0,
                reasoning_types=["single_fact"],
                table_filter_modes=["not_number_dominant"],
            )

        self.assertIn("--no-route3-pageview-prefilter", command)
        self.assertNotIn("--route3-pageview-prefilter", command)

    def test_recipe_segment_can_enable_pageview_prefilter(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            segment_dir = Path(tmpdir) / "segments"
            args = _recipe_args(route3_pageview_prefilter=True)

            command, _paths = _segment_command(
                args=args,
                item=RecipeItem(answer_type="Person", record_limit=40),
                index=0,
                run_id="recipe",
                segment_dir=segment_dir,
                stream_state_base=segment_dir / "stream_state.json",
                stream_exclusion_file=segment_dir / "recipe_page_id_exclusions.json",
                stream_search_initial_offset=0,
                reasoning_types=["single_fact"],
                table_filter_modes=["not_number_dominant"],
            )

        self.assertIn("--route3-pageview-prefilter", command)
        self.assertNotIn("--no-route3-pageview-prefilter", command)

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
                stream_exclusion_file=segment_dir / "recipe_page_id_exclusions.json",
                stream_search_initial_offset=0,
                reasoning_types=["single_fact"],
                table_filter_modes=["not_number_dominant"],
                table_source_types=["infobox"],
            )

        source_values = [
            command[index + 1]
            for index, value in enumerate(command)
            if value == "--route3-table-source-type"
        ]
        self.assertEqual(source_values, ["infobox"])

    def test_recipe_segment_can_disable_route3_prose_leakage_scoring(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            segment_dir = Path(tmpdir) / "segments"
            args = _recipe_args(route3_prose_leakage_scoring=False)

            command, _paths = _segment_command(
                args=args,
                item=RecipeItem(answer_type="Person", record_limit=40),
                index=0,
                run_id="recipe",
                segment_dir=segment_dir,
                stream_state_base=segment_dir / "stream_state.json",
                stream_exclusion_file=segment_dir / "recipe_page_id_exclusions.json",
                stream_search_initial_offset=0,
                reasoning_types=["single_fact"],
                table_filter_modes=["not_number_dominant"],
            )

        self.assertIn("--no-route3-prose-leakage-scoring", command)
        self.assertNotIn("--route3-prose-leakage-scoring", command)

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
                stream_exclusion_file=segment_dir / "recipe_page_id_exclusions.json",
                stream_search_initial_offset=0,
                reasoning_types=["single_fact"],
                table_filter_modes=["not_number_dominant"],
            )

        self.assertEqual(_command_value(command, "--stream-batch-size"), "50")
        self.assertEqual(_command_value(command, "--stream-search-max-rounds"), "500")
        self.assertNotIn("--compact-output", command)
        self.assertNotIn("--compact-rejected-output", command)
        self.assertIn("--big-batch-mode", command)
        self.assertEqual(_command_value(command, "--stream-discovery-max-retries"), "5")
        self.assertEqual(_command_value(command, "--wikipedia-429-backoff-seconds"), "30.0")

    def test_append_recipe_segment_uses_suffixed_artifacts_and_prior_offsets(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            segment_dir = Path(tmpdir) / "segments"
            segment_dir.mkdir()
            (segment_dir / "01_person_2000_state.json").write_text(
                json.dumps(
                    {
                        "used_ids": [101, 102],
                        "table_search_offsets": {'insource:"wikitable"': 2400},
                    }
                ),
                encoding="utf-8",
            )
            args = _recipe_args(append_to_existing_run=True, append_run_label="topup1")
            offset = _append_stream_search_initial_offset(
                segment_dir=segment_dir,
                base_segment_id="01_person_2000",
                base_offset=0,
            )

            command, paths = _segment_command(
                args=args,
                item=RecipeItem(answer_type="Person", record_limit=2000),
                index=0,
                run_id="recipe",
                segment_dir=segment_dir,
                stream_state_base=segment_dir / "stream_state.json",
                stream_exclusion_file=segment_dir / "recipe_page_id_exclusions.json",
                stream_search_initial_offset=offset,
                reasoning_types=["single_fact"],
                table_filter_modes=["not_number_dominant"],
                append_label="topup1",
            )

        self.assertTrue(str(paths["accepted"]).endswith("01_person_2000_topup1_accepted.jsonl"))
        self.assertTrue(str(paths["stream_state"]).endswith("01_person_2000_topup1_state.json"))
        self.assertEqual(_command_value(command, "--stream-search-initial-offset"), "2400")
        self.assertIn("--reset-stream-state", command)

    def test_append_recipe_offset_ignores_zero_attempt_topup_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            segment_dir = Path(tmpdir) / "segments"
            segment_dir.mkdir()
            (segment_dir / "01_person_2000_state.json").write_text(
                json.dumps({"table_search_offsets": {'insource:"wikitable"': 2400}}),
                encoding="utf-8",
            )
            (segment_dir / "01_person_2000_topup_1_state.json").write_text(
                json.dumps({"table_search_offsets": {'insource:"wikitable"': 5250}}),
                encoding="utf-8",
            )
            (segment_dir / "01_person_2000_topup_1_summary.json").write_text(
                json.dumps({"attempted_page_ids": 0, "stream_state_stats": {"used": 6153}}),
                encoding="utf-8",
            )

            offset = _append_stream_search_initial_offset(
                segment_dir=segment_dir,
                base_segment_id="01_person_2000",
                base_offset=0,
            )

        self.assertEqual(offset, 2400)

    def test_append_recipe_command_seeds_matching_rerun_pool(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            segment_dir = Path(tmpdir) / "segments"
            segment_dir.mkdir()
            seed_file = segment_dir / "01_person_2000_topup1_rerun_pool_seed.json"
            seed_file.write_text(json.dumps([101, 102]), encoding="utf-8")
            args = _recipe_args(append_to_existing_run=True, append_run_label="topup1")

            command, _paths = _segment_command(
                args=args,
                item=RecipeItem(answer_type="Person", record_limit=2000),
                index=0,
                run_id="recipe",
                segment_dir=segment_dir,
                stream_state_base=segment_dir / "stream_state.json",
                stream_exclusion_file=segment_dir / "recipe_page_id_exclusions.json",
                stream_search_initial_offset=2400,
                reasoning_types=["single_fact"],
                table_filter_modes=["not_number_dominant"],
                append_label="topup1",
                rerun_pool_seed_file=seed_file,
            )

        self.assertEqual(_command_value(command, "--stream-rerun-pool-seed-file"), str(seed_file))
        self.assertIn("--stream-prefer-rerun-pool", command)
        self.assertIn("--stream-free-seeded-rerun-pool-on-completion", command)

    def test_matching_segment_rerun_pool_seed_uses_same_segment_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            segment_dir = Path(tmpdir) / "segments"
            segment_dir.mkdir()
            (segment_dir / "01_person_2000_state.json").write_text(
                json.dumps({"rerun_pool": [101, 102], "accepted_ids": []}),
                encoding="utf-8",
            )
            (segment_dir / "01_person_2000_topup_1_state.json").write_text(
                json.dumps({"rerun_pool": [103], "accepted_ids": [102]}),
                encoding="utf-8",
            )
            (segment_dir / "02_place_2000_state.json").write_text(
                json.dumps({"rerun_pool": [201]}),
                encoding="utf-8",
            )

            seed_ids, source_paths = _matching_segment_rerun_pool_seed(
                segment_dir=segment_dir,
                base_segment_id="01_person_2000",
                current_segment_id="01_person_2000_topup_2",
            )

        self.assertEqual(seed_ids, [101, 103])
        self.assertEqual({path.name for path in source_paths}, {"01_person_2000_state.json", "01_person_2000_topup_1_state.json"})

    def test_append_subset_recipe_reuses_existing_answer_type_segment_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            segment_dir = Path(tmpdir) / "segments"
            segment_dir.mkdir()
            (segment_dir / "02_place_2000_state.json").write_text(
                json.dumps({"rerun_pool": [201, 202]}),
                encoding="utf-8",
            )

            base_segment_id = _base_segment_id_for_run(
                segment_dir=segment_dir,
                item=RecipeItem(answer_type="Place", record_limit=933),
                index=0,
                append_label="topup_1",
            )

        self.assertEqual(base_segment_id, "02_place_2000")

    def test_place_only_append_can_target_existing_rerun_pool_without_fresh_lane(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            segment_dir = Path(tmpdir) / "segments"
            segment_dir.mkdir()
            (segment_dir / "02_place_2000_state.json").write_text(
                json.dumps({"rerun_pool": [201, 202]}),
                encoding="utf-8",
            )
            seed_ids, _source_paths = _matching_segment_rerun_pool_seed(
                segment_dir=segment_dir,
                base_segment_id="02_place_2000",
                current_segment_id="02_place_2000_topup_1",
            )
            seed_file = segment_dir / "02_place_2000_topup_1_rerun_pool_seed.json"
            seed_file.write_text(json.dumps(seed_ids), encoding="utf-8")
            args = _recipe_args(append_to_existing_run=True, append_run_label="topup_1")

            command, paths = _segment_command(
                args=args,
                item=RecipeItem(answer_type="Place", record_limit=2),
                index=0,
                run_id="recipe",
                segment_dir=segment_dir,
                stream_state_base=segment_dir / "stream_state.json",
                stream_exclusion_file=segment_dir / "recipe_page_id_exclusions.json",
                stream_search_initial_offset=6300,
                reasoning_types=["single_fact"],
                table_filter_modes=["not_number_dominant"],
                append_label="topup_1",
                rerun_pool_seed_file=seed_file,
                base_segment_id="02_place_2000",
            )

        self.assertEqual(seed_ids, [201, 202])
        self.assertTrue(str(paths["accepted"]).endswith("02_place_2000_topup_1_accepted.jsonl"))
        self.assertTrue(str(paths["stream_state"]).endswith("02_place_2000_topup_1_state.json"))
        self.assertNotIn("--record-limit", command)
        self.assertEqual(_command_value(command, "--stream-page-processing-target"), "2")
        self.assertEqual(_command_value(command, "--stream-rerun-pool-seed-file"), str(seed_file))
        self.assertIn("--stream-prefer-rerun-pool", command)

    def test_clear_rerun_pool_ids_from_states_frees_undecided_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(
                json.dumps({"used_ids": [101, 102], "rerun_pool": [101, 102], "accepted_ids": [102]}),
                encoding="utf-8",
            )

            cleared = _clear_rerun_pool_ids_from_states(
                state_paths=[state_path],
                page_ids=[101, 102],
                reason="test_transfer",
            )
            state = json.loads(state_path.read_text(encoding="utf-8"))

        self.assertEqual(cleared, {str(state_path): 2})
        self.assertNotIn(101, state["used_ids"])
        self.assertIn(102, state["used_ids"])
        self.assertEqual(state["rerun_pool"], [])

    def test_segment_used_count_subtracts_append_exclusions(self) -> None:
        summary = {
            "attempted_page_ids": 0,
            "stream_excluded_page_ids": 6153,
            "stream_state_stats": {"used": 6153},
        }

        self.assertEqual(_segment_used_count(summary), 0)

    def test_existing_recipe_page_ids_reads_exclusion_summaries_and_states(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            segment_dir = Path(tmpdir) / "segments"
            segment_dir.mkdir()
            exclusion_file = segment_dir / "recipe_page_id_exclusions.json"
            exclusion_file.write_text(json.dumps([101]), encoding="utf-8")
            (segment_dir / "01_person_2000_summary.json").write_text(
                json.dumps({"page_ids": [201, "202"]}),
                encoding="utf-8",
            )
            (segment_dir / "01_person_2000_state.json").write_text(
                json.dumps({"used_ids": [301], "in_progress_ids": [301], "rerun_pool": [401], "accepted_ids": [501]}),
                encoding="utf-8",
            )

            page_ids = _existing_recipe_page_ids(segment_dir, exclusion_file)

        self.assertEqual(page_ids, {101, 301, 401, 501})

    def test_existing_recipe_page_ids_ignores_summary_page_ids_when_state_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            segment_dir = Path(tmpdir) / "segments"
            segment_dir.mkdir()
            exclusion_file = segment_dir / "recipe_page_id_exclusions.json"
            (segment_dir / "01_person_2000_summary.json").write_text(
                json.dumps({"page_ids": [101, 102, 201]}),
                encoding="utf-8",
            )
            (segment_dir / "01_person_2000_state.json").write_text(
                json.dumps({"accepted_ids": [201], "rejected_ids": [301]}),
                encoding="utf-8",
            )

            page_ids = _existing_recipe_page_ids(segment_dir, exclusion_file)

        self.assertEqual(page_ids, {201, 301})

    def test_existing_recipe_page_ids_does_not_reexclude_raw_append_used_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            segment_dir = Path(tmpdir) / "segments"
            segment_dir.mkdir()
            exclusion_file = segment_dir / "recipe_page_id_exclusions.json"
            (segment_dir / "01_person_2000_topup_1_summary.json").write_text(
                json.dumps({"page_ids": [201]}),
                encoding="utf-8",
            )
            (segment_dir / "01_person_2000_topup_1_state.json").write_text(
                json.dumps(
                    {
                        "used_ids": [101, 102, 201, 301, 401],
                        "accepted_ids": [201],
                        "rejected_ids": [301],
                        "in_progress_ids": [401],
                        "rerun_pool": [501],
                    }
                ),
                encoding="utf-8",
            )

            page_ids = _existing_recipe_page_ids(segment_dir, exclusion_file)

        self.assertEqual(page_ids, {201, 301, 401, 501})
        self.assertNotIn(101, page_ids)
        self.assertNotIn(102, page_ids)

    def test_incomplete_existing_segment_is_not_reused(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            paths = {
                "accepted": root / "accepted.jsonl",
                "rejected": root / "rejected.jsonl",
                "summary": root / "summary.json",
            }
            paths["accepted"].write_text("", encoding="utf-8")
            paths["rejected"].write_text("", encoding="utf-8")
            paths["summary"].write_text(
                json.dumps({"record_limit": 2000, "stream_state_stats": {"used": 190}}),
                encoding="utf-8",
            )

            self.assertFalse(_segment_complete(paths))

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
        self.assertEqual(accepted[0]["id"], "route3_20260525_p123_person_infobox")
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
                "rerun": 3,
                "wall_clock_seconds": 12.5,
                "random_seed": 123,
                "stream_state": "person_state.json",
                "stream_state_stats": {"used": 40, "accepted": 2, "rejected": 35, "rerun_pool": 3},
                "rerun_pool_ids_after_run": [101],
                "rerun_pool_failure_reasons_after_run": {"101": "search_longtail_verifier_error"},
                "page_ids": [1, 2],
            },
            {
                "run_segment_id": "02_date_40",
                "recipe_answer_type": "Date",
                "recipe_record_limit": 40,
                "attempted_page_ids": 40,
                "accepted": 1,
                "rejected": 38,
                "rerun": 1,
                "wall_clock_seconds": 20.0,
                "random_seed": 456,
                "stream_state": "date_state.json",
                "stream_state_stats": {"used": 42, "accepted": 1, "rejected": 38, "rerun_pool": 1},
                "stream_excluded_page_ids": 2,
                "rerun_pool_ids_after_run": [101, 202],
                "rerun_pool_failure_reasons_after_run": {
                    "101": "second_stage_grading_error",
                    "202": "search_longtail_verifier_error",
                },
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
        self.assertEqual(summary["rerun_pool_ids_after_run"], [101, 202])
        self.assertIn("01_person_40:101", summary["rerun_pool_failure_reasons_after_run"])
        self.assertIn("02_date_40:101", summary["rerun_pool_failure_reasons_after_run"])
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
