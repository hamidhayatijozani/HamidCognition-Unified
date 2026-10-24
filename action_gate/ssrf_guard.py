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

# Addresses that are never safe as an outbound destination for external hosts.
# Loopback and link-local are intentionally excluded here because internal
# service names have their own dedicated check via _INTERNAL_NETWORKS.
_BLOCKED = tuple(ipaddress.ip_network(value) for value in (
    "0.0.0.0/8",
    "100.64.0.0/10",   # shared address space
    "169.254.0.0/16",  # link-local
    "192.0.0.0/24",    # IETF protocol assignments
    "198.18.0.0/15",   # benchmarking
    "224.0.0.0/4",     # multicast
    "240.0.0.0/4",     # reserved
    "::/128",
    "::1/128",
    "fc00::/7",        # ULA
    "fe80::/10",       # link-local v6
    "ff00::/8",        # multicast v6
))

# These are the only hostnames that may resolve to private/internal addresses.
_INTERNAL_HOSTS = frozenset({"127.0.0.1", "localhost", "action-gate", "tool"})
_INTERNAL_NETWORKS = tuple(ipaddress.ip_network(value) for value in (
    "127.0.0.0/8",
    "10.0.0.0/8",
    "172.16.0.0/12",
    "192.168.0.0/16",
    "::1/128",
    "fc00::/7",
    "fe80::/10",
))


def _is_private_ip(ip: ipaddress._BaseAddress) -> bool:
    """Return True if the address is in a private or reserved range."""
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        ip = ip.ipv4_mapped
    if ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
        return True
    return any(ip in network for network in _BLOCKED)


def _resolve_all(host: str, port: int) -> tuple[ipaddress._BaseAddress, ...]:
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror:
        return ()
    return tuple(ipaddress.ip_address(info[4][0]) for info in infos)


def is_safe_url(url: str) -> bool:
    """Return True only for an explicitly configured, syntactically valid origin.

    Internal service names may resolve to private addresses. Any other host
    must resolve exclusively to global (non-private) addresses.
    """
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
    except (ValueError, UnicodeError):
        return False

    if not addresses:
        return False

    if host in _INTERNAL_HOSTS:
        # Every resolved address must be in an expected internal range.
        return all(
            any(ip in network for network in _INTERNAL_NETWORKS)
            for ip in addresses
        )

    # External allowlisted hosts must not resolve to any private/reserved range.
    return all(not _is_private_ip(ip) for ip in addresses)


def require_safe_url(url: str) -> str:
    """CodeQL-friendly sanitizer: reject unsafe outbound destinations."""
    if not is_safe_url(url):
        raise ValueError(f"Blocked outbound URL: {url!r}")
    return url
