"""Outbound URL validation for the enforcement proxy.

The proxy does not accept arbitrary destination URLs. GATE_URL and TOOL_URL are
deployment configuration, while request paths are appended to those fixed
origins. This module makes that boundary explicit for static analysis and
runtime defense-in-depth.
"""
from __future__ import annotations

import ipaddress
import os
import socket
from urllib.parse import urlparse

_DEFAULT_ALLOWED_HOSTS = frozenset({
    "127.0.0.1",
    "localhost",
    "action-gate",
    "tool",
})

_env_hosts = os.environ.get("ENFORCEMENT_ALLOWED_HOSTS")
ALLOWED_HOSTS = frozenset(
    h.strip().lower().rstrip(".")
    for h in (_env_hosts.split(",") if _env_hosts else _DEFAULT_ALLOWED_HOSTS)
    if h.strip()
)

_BLOCKED = tuple(
    ipaddress.ip_network(value)
    for value in (
        "0.0.0.0/8",
        "10.0.0.0/8",
        "100.64.0.0/10",
        "127.0.0.0/8",
        "169.254.0.0/16",
        "172.16.0.0/12",
        "192.0.0.0/24",
        "192.168.0.0/16",
        "198.18.0.0/15",
        "224.0.0.0/4",
        "240.0.0.0/4",
        "::1/128",
        "fc00::/7",
        "fe80::/10",
    )
)

# These names are internal Docker service identities in the production
# compose file. Private addresses are therefore expected for these exact
# identities, but never for an arbitrary host supplied at runtime.
_INTERNAL_HOSTS = frozenset({"127.0.0.1", "localhost", "action-gate", "tool"})


def _is_blocked_ip(ip: ipaddress._BaseAddress) -> bool:
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        ip = ip.ipv4_mapped
    return any(ip in network for network in _BLOCKED)


def _resolve_all(host: str, port: int) -> tuple[ipaddress._BaseAddress, ...]:
    infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    addresses = []
    for _family, _socktype, _proto, _canonname, sockaddr in infos:
        addresses.append(ipaddress.ip_address(sockaddr[0]))
    return tuple(addresses)


def is_safe_url(url: str) -> bool:
    """Return True only for an explicitly configured, syntactically valid origin.

    For exact internal service identities, private addresses are allowed because
    they are the intended Docker-network destinations. Any other host must
    resolve only to public addresses.
    """
    try:
        parsed = urlparse(url)
    except ValueError:
        return False

    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return False
    if parsed.username or parsed.password:
        return False

    host = parsed.hostname.lower().rstrip(".")
    if host not in ALLOWED_HOSTS:
        return False

    try:
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        addresses = _resolve_all(host, port)
    except (OSError, ValueError):
        return False

    if not addresses:
        return False

    if host in _INTERNAL_HOSTS:
        return True

    return all(not _is_blocked_ip(ip) for ip in addresses)


def require_safe_url(url: str) -> str:
    """CodeQL-friendly sanitizer: reject unsafe outbound destinations."""
    if not is_safe_url(url):
        raise ValueError(f"Blocked outbound URL: {url!r}")
    return url
