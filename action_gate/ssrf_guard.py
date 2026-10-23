"""Outbound URL validation for the enforcement proxy.

Only explicitly configured origins are accepted. Internal service names are
allowed only when every resolved address belongs to an expected private/local
range; arbitrary public hosts resolving to private addresses are rejected.
"""
from __future__ import annotations

import ipaddress
import os
import socket
from urllib.parse import urlparse

_DEFAULT_ALLOWED_HOSTS = frozenset({"127.0.0.1", "localhost", "action-gate", "tool"})
_env_hosts = os.environ.get("ENFORCEMENT_ALLOWED_HOSTS")
ALLOWED_HOSTS = frozenset(
    h.strip().lower().rstrip(".")
    for h in (_env_hosts.split(",") if _env_hosts else _DEFAULT_ALLOWED_HOSTS)
    if h.strip()
)
_BLOCKED = tuple(ipaddress.ip_network(value) for value in (
    "0.0.0.0/8", "100.64.0.0/10", "169.254.0.0/16",
    "192.0.0.0/24", "198.18.0.0/15", "224.0.0.0/4", "240.0.0.0/4",
    "::/128", "::1/128", "fc00::/7", "fe80::/10", "ff00::/8",
))
_INTERNAL_HOSTS = frozenset({"127.0.0.1", "localhost", "action-gate", "tool"})
_INTERNAL_NETWORKS = tuple(ipaddress.ip_network(value) for value in (
    "127.0.0.0/8", "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16",
    "::1/128", "fc00::/7", "fe80::/10",
))


def _is_blocked_ip(ip: ipaddress._BaseAddress) -> bool:
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        ip = ip.ipv4_mapped
    return (not ip.is_global) or any(ip in network for network in _BLOCKED)


def _resolve_all(host: str, port: int) -> tuple[ipaddress._BaseAddress, ...]:
    infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    return tuple(ipaddress.ip_address(info[4][0]) for info in infos)


def is_safe_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            return False
        if parsed.username or parsed.password:
            return False
        host = parsed.hostname.lower().rstrip(".")
        if host not in ALLOWED_HOSTS:
            return False
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        addresses = _resolve_all(host, port)
    except (OSError, ValueError, UnicodeError):
        return False
    if not addresses:
        return False
    # Do not let an allowlisted hostname resolve to a different trust zone.
    if host in _INTERNAL_HOSTS:
        return all(any(ip in network for network in _INTERNAL_NETWORKS) for ip in addresses)
    return all(not _is_blocked_ip(ip) for ip in addresses)


def require_safe_url(url: str) -> str:
    if not is_safe_url(url):
        raise ValueError(f"Blocked outbound URL: {url!r}")
    return url
