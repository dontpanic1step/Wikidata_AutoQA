"""Networking helpers for proxy-aware HTTP access."""

from __future__ import annotations

import socket
from urllib.parse import urlparse
from urllib.request import ProxyHandler, build_opener, install_opener

import socks

ORIGINAL_SOCKET = socket.socket


def install_proxy(proxy: str | None) -> None:
    """Install a process-wide proxy configuration for urllib-based clients."""
    if not proxy:
        return

    parsed = urlparse(proxy)
    scheme = parsed.scheme.lower()
    if scheme in {"http", "https"}:
        opener = build_opener(ProxyHandler({"http": proxy, "https": proxy}))
        install_opener(opener)
        return

    if scheme in {"socks5", "socks5h"}:
        socks.set_default_proxy(
            socks.SOCKS5,
            parsed.hostname,
            parsed.port,
            rdns=(scheme == "socks5h"),
            username=parsed.username,
            password=parsed.password,
        )
        socket.socket = socks.socksocket
        return

    raise ValueError(f"Unsupported proxy scheme: {parsed.scheme}")


def clear_proxy() -> None:
    """Reset urllib and socket state back to direct networking."""
    install_opener(build_opener())
    socket.socket = ORIGINAL_SOCKET
