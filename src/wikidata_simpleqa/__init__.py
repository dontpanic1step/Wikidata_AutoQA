"""Top-level package for the Wikidata SimpleQA generator."""

from .config import Settings
from .pipeline import run_pipeline

__all__ = ["Settings", "run_pipeline"]
