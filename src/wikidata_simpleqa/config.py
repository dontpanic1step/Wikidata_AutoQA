"""Runtime configuration for the Stage 1 vertical slice."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
import re


def normalize_proxy(value: str | None) -> str | None:
    """Normalize user-facing proxy values to the internal optional proxy form."""
    if value is None:
        return None
    stripped = value.strip()
    if not stripped or stripped.lower() in {"none", "direct", "off", "false"}:
        return None
    return stripped


def _default_second_stage_grading_models() -> tuple["LLMConfig", ...]:
    """Return the default small-model panel for post-filter grading."""
    return (
        LLMConfig(
            provider="openrouter",
            model="openai/gpt-4.1-mini",
            api_key_env="OPENROUTER_API_KEY",
            base_url="https://openrouter.ai/api/v1",
            temperature=0.0,
            max_tokens=256,
        ),
        LLMConfig(
            provider="openrouter",
            model="google/gemini-3-flash-preview",
            api_key_env="OPENROUTER_API_KEY",
            base_url="https://openrouter.ai/api/v1",
            temperature=0.0,
            max_tokens=256,
        ),
    )


def _default_second_stage_grading_grader_llm() -> "LLMConfig":
    """Return the default grader config for post-filter panel scoring."""
    return LLMConfig(
        provider="openrouter",
        model="openai/gpt-4.1-mini",
        api_key_env="OPENROUTER_API_KEY",
        base_url="https://openrouter.ai/api/v1",
        temperature=0.0,
        max_tokens=128,
    )


@dataclass(slots=True)
class LLMConfig:
    """Configuration for one-shot rewrite calls."""

    provider: str
    model: str
    api_key_env: str
    base_url: str | None = None
    proxy: str | None = None
    temperature: float = 0.0
    max_tokens: int = 256

    def __post_init__(self) -> None:
        self.proxy = normalize_proxy(self.proxy)


@dataclass(slots=True)
class Settings:
    """Configuration for generation and output writing."""

    target_time: str
    run_date: str = field(default_factory=lambda: date.today().isoformat())
    date_upper_bound: str | None = None
    pilot_total: int = 20
    harvest_limit_per_template: int = 100
    cutoff_year: int = 2025
    enabled_routes: tuple[str, ...] = (
        "route2_wikidata_wikipedia_hybrid",
        "route1_wikidata_light",
    )
    duckduckgo_top_k: int = 10
    duckduckgo_parallel_queries: int = 3
    duckduckgo_prefer_ddgs: bool = True
    duckduckgo_ddgs_backend: str = "auto"
    duckduckgo_ddgs_max_attempts: int = 2
    duckduckgo_disable_fallbacks: str | tuple[str, ...] | list[str] | set[str] | None = field(default_factory=tuple)
    duckduckgo_cooldown_enabled: bool = True
    duckduckgo_cooldown_failure_threshold: int = 3
    duckduckgo_cooldown_initial_seconds: float = 60.0
    duckduckgo_cooldown_max_seconds: float = 300.0
    generated_search_query_count: int = 3
    second_stage_grading_enabled: bool = False
    second_stage_grading_models: tuple[LLMConfig, ...] = field(
        default_factory=_default_second_stage_grading_models
    )
    second_stage_grading_accuracy_threshold: float = 0.5
    second_stage_grading_grader_llm: LLMConfig | None = field(
        default_factory=_default_second_stage_grading_grader_llm
    )
    longtail_prefilter_max_sitelinks: int = 80
    longtail_prefilter_max_claims: int = 400
    search_longtail_max_full_question_hit_rate: float = 0.3
    search_longtail_max_keyword_hit_rate: float = 0.3
    search_longtail_max_overall_hit_rate: float = 0.3
    allow_year_in_official_title: bool = False
    reject_future_dated_candidates: bool = True
    reject_current_or_latest_facts: bool = True
    reject_mutable_relationships: bool = True
    reject_mutable_affiliations: bool = True
    reject_cumulative_statistics: bool = True
    reject_unreleased_works: bool = True
    user_agent: str = "wikidata-simpleqa-generator/0.1"
    proxy: str | None = None
    timeout_seconds: float = 30.0
    wikidata_max_entity_ids_per_request: int = 50
    wikidata_log_checkpoints: bool = False
    live_probe_mode: bool = False
    live_probe_harvest_limit: int = 2
    live_probe_max_entity_ids_per_request: int = 10
    route1_light_fallback_enabled: bool = True
    route1_subject_seed_window_granularity: str = "year"
    random_seed: int = 42
    cache_dir: Path = Path("cache/wikidata")
    output_path: Path = Path("outputs/pilot_accepted.jsonl")
    rejected_output_path: Path = Path("outputs/pilot_rejected.jsonl")
    rewrite_enabled: bool = False
    rewrite_llm: LLMConfig | None = None

    def __post_init__(self) -> None:
        self.proxy = normalize_proxy(self.proxy)
        if self.date_upper_bound is None:
            self.date_upper_bound = self.run_date
        self.target_time = self.target_time.strip()
        self._validate_target_time()
        if not 0.0 <= self.second_stage_grading_accuracy_threshold <= 1.0:
            raise ValueError("second_stage_grading_accuracy_threshold must be between 0.0 and 1.0")
        if self.duckduckgo_parallel_queries < 1:
            raise ValueError("duckduckgo_parallel_queries must be at least 1")
        self.duckduckgo_ddgs_backend = self.duckduckgo_ddgs_backend.strip() or "auto"
        self.duckduckgo_ddgs_max_attempts = int(self.duckduckgo_ddgs_max_attempts)
        if self.duckduckgo_ddgs_max_attempts < 1:
            raise ValueError("duckduckgo_ddgs_max_attempts must be at least 1")
        self.duckduckgo_disable_fallbacks = _normalize_sequence(self.duckduckgo_disable_fallbacks)
        self.duckduckgo_cooldown_failure_threshold = int(self.duckduckgo_cooldown_failure_threshold)
        if self.duckduckgo_cooldown_failure_threshold < 1:
            raise ValueError("duckduckgo_cooldown_failure_threshold must be at least 1")
        self.duckduckgo_cooldown_initial_seconds = float(self.duckduckgo_cooldown_initial_seconds)
        self.duckduckgo_cooldown_max_seconds = float(self.duckduckgo_cooldown_max_seconds)
        if self.duckduckgo_cooldown_initial_seconds < 0.0:
            raise ValueError("duckduckgo_cooldown_initial_seconds must be non-negative")
        if self.duckduckgo_cooldown_max_seconds < 0.0:
            raise ValueError("duckduckgo_cooldown_max_seconds must be non-negative")
        if self.duckduckgo_cooldown_max_seconds < self.duckduckgo_cooldown_initial_seconds:
            raise ValueError("duckduckgo_cooldown_max_seconds must be at least duckduckgo_cooldown_initial_seconds")
        if self.generated_search_query_count < 0:
            raise ValueError("generated_search_query_count must be non-negative")
        if self.route1_subject_seed_window_granularity not in {"year", "month", "day"}:
            raise ValueError("route1_subject_seed_window_granularity must be one of: year, month, day")
        if self.live_probe_mode:
            self.harvest_limit_per_template = min(
                self.harvest_limit_per_template,
                self.live_probe_harvest_limit,
            )
            self.wikidata_max_entity_ids_per_request = min(
                self.wikidata_max_entity_ids_per_request,
                self.live_probe_max_entity_ids_per_request,
            )
            self.wikidata_log_checkpoints = True

    @property
    def target_start_date(self) -> str:
        """Return the lower date bound in ISO format."""
        parts = self.target_time.split("-")
        if len(parts) == 1:
            return f"{parts[0]}-01-01"
        if len(parts) == 2:
            return f"{parts[0]}-{parts[1]}-01"
        return self.target_time

    def duckduckgo_client_kwargs(self) -> dict[str, object]:
        """Return keyword arguments for the shared DuckDuckGo search client."""
        return {
            "user_agent": self.user_agent,
            "proxy": self.proxy,
            "timeout_seconds": self.timeout_seconds,
            "cache_dir": self.cache_dir,
            "prefer_ddgs": self.duckduckgo_prefer_ddgs,
            "ddgs_backend": self.duckduckgo_ddgs_backend,
            "ddgs_max_attempts": self.duckduckgo_ddgs_max_attempts,
            "disable_fallbacks": self.duckduckgo_disable_fallbacks,
            "cooldown_enabled": self.duckduckgo_cooldown_enabled,
            "cooldown_failure_threshold": self.duckduckgo_cooldown_failure_threshold,
            "cooldown_initial_seconds": self.duckduckgo_cooldown_initial_seconds,
            "cooldown_max_seconds": self.duckduckgo_cooldown_max_seconds,
        }

    def _validate_target_time(self) -> None:
        """Validate the accepted target-time formats."""
        pattern = r"^\d{4}(-\d{2}){0,2}$"
        if not re.fullmatch(pattern, self.target_time):
            raise ValueError(
                "target_time must use one of these formats: YYYY, YYYY-MM, or YYYY-MM-DD"
            )
        _ = date.fromisoformat(self.target_start_date)


def _normalize_sequence(value: str | tuple[str, ...] | list[str] | set[str] | None) -> tuple[str, ...]:
    """Normalize CLI-style repeated or comma-separated string values."""
    if value is None:
        return ()
    if isinstance(value, str):
        raw_items = re.split(r"[,;\s]+", value)
    else:
        raw_items = []
        for item in value:
            raw_items.extend(re.split(r"[,;\s]+", str(item)))
    return tuple(item.strip() for item in raw_items if item.strip())
