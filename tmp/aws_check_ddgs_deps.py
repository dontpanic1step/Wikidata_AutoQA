"""Check ddgs probe dependencies on the AWS host."""

from __future__ import annotations

import importlib.util
import sys

print("python", sys.executable)
print("ddgs_spec", importlib.util.find_spec("ddgs"))
print("socks_spec", importlib.util.find_spec("socks"))
try:
    import ddgs

    print("ddgs ok", getattr(ddgs, "__version__", "unknown"))
except Exception as exc:  # noqa: BLE001
    print("ddgs error", type(exc).__name__, exc)
try:
    import socks  # noqa: F401

    print("pysocks ok")
except Exception as exc:  # noqa: BLE001
    print("pysocks error", type(exc).__name__, exc)
