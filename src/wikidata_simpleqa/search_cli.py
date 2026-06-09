"""Command-line helpers for shared search-client options."""

from __future__ import annotations

import argparse
from typing import Any

from .search_client import (
    DUCKDUCKGO_COOLDOWN_FAILURE_THRESHOLD,
    DUCKDUCKGO_COOLDOWN_INITIAL_SECONDS,
    DUCKDUCKGO_COOLDOWN_MAX_SECONDS,
    DUCKDUCKGO_DDGS_MAX_ATTEMPTS,
)


def add_duckduckgo_transport_args(parser: argparse.ArgumentParser) -> None:
    """Add shared DuckDuckGo transport and fallback arguments to a parser."""
    parser.add_argument(
        "--duckduckgo-prefer-ddgs",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Prefer the ddgs package before legacy DuckDuckGo HTML/Lite search. Default: enabled.",
    )
    parser.add_argument(
        "--duckduckgo-ddgs-backend",
        default="auto",
        help='Backend passed to DDGS.text(...). Default: "auto".',
    )
    parser.add_argument(
        "--duckduckgo-ddgs-max-attempts",
        type=int,
        default=DUCKDUCKGO_DDGS_MAX_ATTEMPTS,
        help="Maximum ddgs attempts before legacy fallback. Default: 2.",
    )
    parser.add_argument(
        "--duckduckgo-disable-fallback",
        action="append",
        default=[],
        help=(
            "Disable a DuckDuckGo fallback path for debugging. Repeat or pass comma-separated values. "
            "Known values: ddgs, legacy/html, lite, direct/direct_fallback. Default: no disabled fallbacks."
        ),
    )
    parser.add_argument(
        "--duckduckgo-cooldown",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable process-global cooldown after repeated DDG throttle/transport failures. Default: enabled.",
    )
    parser.add_argument(
        "--duckduckgo-cooldown-failure-threshold",
        type=int,
        default=DUCKDUCKGO_COOLDOWN_FAILURE_THRESHOLD,
        help="Consecutive DDG throttle/transport failures before global cooldown starts. Default: 3.",
    )
    parser.add_argument(
        "--duckduckgo-cooldown-initial-seconds",
        type=float,
        default=DUCKDUCKGO_COOLDOWN_INITIAL_SECONDS,
        help="Initial shared DDG cooldown sleep in seconds. Default: 60.",
    )
    parser.add_argument(
        "--duckduckgo-cooldown-max-seconds",
        type=float,
        default=DUCKDUCKGO_COOLDOWN_MAX_SECONDS,
        help="Maximum shared DDG cooldown sleep in seconds. Default: 300.",
    )


def duckduckgo_settings_kwargs(args: argparse.Namespace) -> dict[str, Any]:
    """Return Settings keyword arguments from shared DuckDuckGo CLI options."""
    return {
        "duckduckgo_prefer_ddgs": bool(getattr(args, "duckduckgo_prefer_ddgs", True)),
        "duckduckgo_ddgs_backend": str(getattr(args, "duckduckgo_ddgs_backend", "auto")),
        "duckduckgo_ddgs_max_attempts": int(
            getattr(args, "duckduckgo_ddgs_max_attempts", DUCKDUCKGO_DDGS_MAX_ATTEMPTS)
        ),
        "duckduckgo_disable_fallbacks": tuple(getattr(args, "duckduckgo_disable_fallback", []) or ()),
        "duckduckgo_cooldown_enabled": bool(getattr(args, "duckduckgo_cooldown", True)),
        "duckduckgo_cooldown_failure_threshold": int(
            getattr(args, "duckduckgo_cooldown_failure_threshold", DUCKDUCKGO_COOLDOWN_FAILURE_THRESHOLD)
        ),
        "duckduckgo_cooldown_initial_seconds": float(
            getattr(args, "duckduckgo_cooldown_initial_seconds", DUCKDUCKGO_COOLDOWN_INITIAL_SECONDS)
        ),
        "duckduckgo_cooldown_max_seconds": float(
            getattr(args, "duckduckgo_cooldown_max_seconds", DUCKDUCKGO_COOLDOWN_MAX_SECONDS)
        ),
    }


def duckduckgo_summary_fields(settings) -> dict[str, object]:
    """Return shared summary fields for DuckDuckGo transport settings."""
    return {
        "duckduckgo_prefer_ddgs": settings.duckduckgo_prefer_ddgs,
        "duckduckgo_ddgs_backend": settings.duckduckgo_ddgs_backend,
        "duckduckgo_ddgs_max_attempts": settings.duckduckgo_ddgs_max_attempts,
        "duckduckgo_disabled_fallbacks": list(settings.duckduckgo_disable_fallbacks),
        "duckduckgo_cooldown_enabled": settings.duckduckgo_cooldown_enabled,
        "duckduckgo_cooldown_failure_threshold": settings.duckduckgo_cooldown_failure_threshold,
        "duckduckgo_cooldown_initial_seconds": settings.duckduckgo_cooldown_initial_seconds,
        "duckduckgo_cooldown_max_seconds": settings.duckduckgo_cooldown_max_seconds,
    }
