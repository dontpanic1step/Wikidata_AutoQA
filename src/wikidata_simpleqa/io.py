"""I/O helpers for JSONL output."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


def write_jsonl(path: Path, records: Iterable[dict]) -> None:
    """Write iterable records to a JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def append_jsonl(path: Path, records: Iterable[dict]) -> None:
    """Append iterable records to a JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
