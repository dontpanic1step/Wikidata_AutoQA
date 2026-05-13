"""Runtime configuration for the Stage 1 vertical slice."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
import re


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
    longtail_prefilter_max_sitelinks: int = 80
    longtail_prefilter_max_claims: int = 400
    search_longtail_max_full_question_hit_rate: float = 0.0
    search_longtail_max_keyword_hit_rate: float = 0.1
    search_longtail_max_overall_hit_rate: float = 0.1
    allow_year_in_official_title: bool = False
    reject_future_dated_candidates: bool = True
    reject_current_or_latest_facts: bool = True
    reject_mutable_relationships: bool = True
    reject_mutable_affiliations: bool = True
    reject_cumulative_statistics: bool = True
    reject_unreleased_works: bool = True
    user_agent: str = "wikidata-simpleqa-generator/0.1"
    proxy: str | None = "socks5://127.0.0.1:7897"
    timeout_seconds: float = 30.0
    random_seed: int = 42
    cache_dir: Path = Path("cache/wikidata")
    output_path: Path = Path("outputs/pilot_accepted.jsonl")
    rejected_output_path: Path = Path("outputs/pilot_rejected.jsonl")
    rewrite_enabled: bool = False
    rewrite_llm: LLMConfig | None = None

    def __post_init__(self) -> None:
        if self.date_upper_bound is None:
            self.date_upper_bound = self.run_date
        self.target_time = self.target_time.strip()
        self._validate_target_time()

    @property
    def target_start_date(self) -> str:
        """Return the lower date bound in ISO format."""
        parts = self.target_time.split("-")
        if len(parts) == 1:
            return f"{parts[0]}-01-01"
        if len(parts) == 2:
            return f"{parts[0]}-{parts[1]}-01"
        return self.target_time

    def _validate_target_time(self) -> None:
        """Validate the accepted target-time formats."""
        pattern = r"^\d{4}(-\d{2}){0,2}$"
        if not re.fullmatch(pattern, self.target_time):
            raise ValueError(
                "target_time must use one of these formats: YYYY, YYYY-MM, or YYYY-MM-DD"
            )
        _ = date.fromisoformat(self.target_start_date)
