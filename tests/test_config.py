"""Tests for configuration parsing."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.config import LLMConfig, Settings


class ConfigTests(unittest.TestCase):
    """Check formal Route 3 runtime configuration."""

    def test_invalid_second_stage_grading_threshold_raises(self) -> None:
        with self.assertRaises(ValueError):
            Settings(second_stage_grading_accuracy_threshold=1.5)

    def test_invalid_query_settings_raise(self) -> None:
        with self.assertRaises(ValueError):
            Settings(duckduckgo_parallel_queries=0)
        with self.assertRaises(ValueError):
            Settings(generated_search_query_count=-1)

    def test_duckduckgo_client_kwargs_include_transport_settings(self) -> None:
        settings = Settings(
            proxy="socks5://127.0.0.1:7890",
            duckduckgo_ddgs_backend="duckduckgo",
            duckduckgo_ddgs_max_attempts=3,
            duckduckgo_disable_fallbacks=("ddgs,legacy", "direct"),
            duckduckgo_cooldown_failure_threshold=4,
            duckduckgo_cooldown_initial_seconds=120.0,
            duckduckgo_cooldown_max_seconds=600.0,
        )
        kwargs = settings.duckduckgo_client_kwargs()
        self.assertEqual(kwargs["proxy"], "socks5://127.0.0.1:7890")
        self.assertTrue(kwargs["prefer_ddgs"])
        self.assertEqual(kwargs["ddgs_backend"], "duckduckgo")
        self.assertEqual(kwargs["ddgs_max_attempts"], 3)
        self.assertEqual(kwargs["disable_fallbacks"], ("ddgs", "legacy", "direct"))
        self.assertEqual(kwargs["cooldown_failure_threshold"], 4)
        self.assertEqual(kwargs["cooldown_initial_seconds"], 120.0)
        self.assertEqual(kwargs["cooldown_max_seconds"], 600.0)

    def test_invalid_duckduckgo_transport_settings_raise(self) -> None:
        with self.assertRaises(ValueError):
            Settings(duckduckgo_ddgs_max_attempts=0)
        with self.assertRaises(ValueError):
            Settings(duckduckgo_cooldown_failure_threshold=0)
        with self.assertRaises(ValueError):
            Settings(duckduckgo_cooldown_initial_seconds=-1.0)
        with self.assertRaises(ValueError):
            Settings(
                duckduckgo_cooldown_initial_seconds=120.0,
                duckduckgo_cooldown_max_seconds=60.0,
            )

    def test_default_search_hit_rate_thresholds_are_uniform_point_three(self) -> None:
        settings = Settings()
        self.assertEqual(settings.search_longtail_max_full_question_hit_rate, 0.3)
        self.assertEqual(settings.search_longtail_max_keyword_hit_rate, 0.3)
        self.assertEqual(settings.search_longtail_max_overall_hit_rate, 0.3)

    def test_default_proxy_is_none(self) -> None:
        self.assertIsNone(Settings().proxy)

    def test_default_second_stage_panel_matches_formal_route3_models(self) -> None:
        settings = Settings()

        self.assertEqual(
            [config.model for config in settings.second_stage_grading_models],
            ["openai/gpt-4.1-mini", "google/gemini-3-flash-preview"],
        )
        self.assertIsNotNone(settings.second_stage_grading_grader_llm)
        self.assertEqual(settings.second_stage_grading_grader_llm.model, "openai/gpt-4.1-mini")

    def test_none_proxy_values_normalize_to_none(self) -> None:
        settings = Settings(proxy="none")
        llm_config = LLMConfig(
            provider="openrouter",
            model="openai/gpt-4.1-mini",
            api_key_env="OPENROUTER_API_KEY",
            proxy="none",
        )
        self.assertIsNone(settings.proxy)
        self.assertIsNone(llm_config.proxy)


if __name__ == "__main__":
    unittest.main()
