"""UTF-8 console output helpers for user-facing JSON summaries."""

from __future__ import annotations

import json
import sys
from typing import Any, TextIO


def configure_utf8_stdout(stream: TextIO | None = None) -> TextIO:
    """Configure a reconfigurable output stream to emit UTF-8 text."""
    output = stream if stream is not None else sys.stdout
    reconfigure = getattr(output, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8")
    return output


def print_json_summary(payload: Any, *, stream: TextIO | None = None) -> None:
    """Print one human-readable JSON summary through a UTF-8 stream."""
    output = configure_utf8_stdout(stream)
    print(json.dumps(payload, indent=2, ensure_ascii=False), file=output)
