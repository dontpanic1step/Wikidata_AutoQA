"""Tests for the Wikipedia infobox recipe runner."""

from __future__ import annotations

import sys
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
    _recipe_summary,
    _segment_stream_search_initial_offset,
    _segment_command,
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
        "small_model": "openai/gpt-4.1-mini",
        "small_model_api_key_env": "OPENROUTER_API_KEY",
        "small_model_base_url": "https://openrouter.ai/api/v1",
        "small_model_max_tokens": 1200,
        "duckduckgo_top_k": 5,
        "duckduckgo_parallel_queries": 3,
        "generated_search_query_count": 2,
        "search_longtail_max_full_question_hit_rate": 0.3,
        "search_longtail_max_keyword_hit_rate": 0.3,
        "search_longtail_max_overall_hit_rate": 0.3,
        "stream_page_source": "table-search",
        "stream_search_limit": 50,
        "stream_search_max_rounds": 10,
        "stream_batch_size": 10,
        "stream_page_workers": 4,
        "wikipedia_concurrency_limit": 4,
        "duckduckgo_concurrency_limit": 4,
        "openrouter_generation_rewrite_concurrency_limit": 10,
        "second_stage_concurrency_limit": 10,
        "route3_extra_prompt": [],
        "disable_route3_table_filter_mode": [],
        "enable_rewrite": True,
        "rewrite_model": "openai/gpt-4.1-mini",
        "enable_second_stage_grading": True,
        "second_stage_grading_accuracy_threshold": 0.1,
        "disable_auto_rerun_once": False,
        "stream_search_query": ['insource:"wikitable"'],
        "enable_broad_table_search": False,
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
