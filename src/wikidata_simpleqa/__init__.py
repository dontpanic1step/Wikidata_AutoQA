"""Top-level package for the Wikidata SimpleQA generator."""

from .config import Settings
from .generation_pipeline import run_generation_pipeline
from .pipeline import run_pipeline

__all__ = ["Settings", "run_pipeline", "run_generation_pipeline"]
