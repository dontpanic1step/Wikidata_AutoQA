"""Invocation-scoped service circuits for formal Route 3 external calls."""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from typing import Any

from .route3_run_ledger import utc_now_iso


CIRCUIT_FAILURE_THRESHOLD = 3
CIRCUIT_SERVICES = {"openrouter", "duckduckgo"}


class CircuitOpenError(RuntimeError):
    """Raised before a new external operation when its service circuit is open."""

    def __init__(self, *, service: str, reason: str) -> None:
        self.service = str(service)
        self.reason = str(reason)
        super().__init__(f"{self.service} circuit is open: {self.reason}")


@dataclass(slots=True)
class ServiceCircuit:
    """Track consecutive infrastructure failures for one invocation and service."""

    service: str
    threshold: int = CIRCUIT_FAILURE_THRESHOLD
    _lock: Lock = field(default_factory=Lock, init=False, repr=False)
    _consecutive_failures: int = field(default=0, init=False)
    _opened: bool = field(default=False, init=False)
    _open_reason: str = field(default="", init=False)
    _events: list[dict[str, Any]] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        self.service = str(self.service)
        if self.service not in CIRCUIT_SERVICES:
            raise ValueError(f"Unsupported circuit service: {self.service}")
        if int(self.threshold) != CIRCUIT_FAILURE_THRESHOLD:
            raise ValueError(
                f"Formal Route 3 circuit threshold must be {CIRCUIT_FAILURE_THRESHOLD}"
            )

    def before_call(self) -> None:
        """Reject a new operation after the sticky invocation circuit opens."""
        with self._lock:
            if self._opened:
                raise CircuitOpenError(
                    service=self.service,
                    reason=self._open_reason,
                )

    def record_success(self) -> None:
        """Reset consecutive failures without closing an already-open circuit."""
        with self._lock:
            self._consecutive_failures = 0
            self._events.append(
                {
                    "event": "success",
                    "at_utc": utc_now_iso(),
                    "circuit_open": self._opened,
                }
            )

    def record_failure(self, *, reason: str, immediate_open: bool = False) -> None:
        """Record one infrastructure failure and open at the fixed threshold."""
        with self._lock:
            self._consecutive_failures += 1
            if immediate_open or self._consecutive_failures >= self.threshold:
                self._opened = True
                self._open_reason = str(reason)
            self._events.append(
                {
                    "event": "failure",
                    "reason": str(reason),
                    "at_utc": utc_now_iso(),
                    "consecutive_failures": self._consecutive_failures,
                    "immediate_open": bool(immediate_open),
                    "circuit_open": self._opened,
                }
            )

    @property
    def is_open(self) -> bool:
        """Return whether this invocation circuit is open."""
        with self._lock:
            return self._opened

    def snapshot(self) -> dict[str, Any]:
        """Return manifest-ready circuit state and audit events."""
        with self._lock:
            return {
                "service": self.service,
                "threshold": self.threshold,
                "consecutive_failures": self._consecutive_failures,
                "open": self._opened,
                "open_reason": self._open_reason,
                "events": [dict(event) for event in self._events],
            }
