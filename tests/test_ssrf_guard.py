import ipaddress

from action_gate import ssrf_guard


def test_blocks_unsafe_schemes_and_hosts():
    for url in (
        "file:///etc/passwd",
        "gopher://evil.example.com/",
        "http://evil.example.com/",
        "https://api.openai.com.evil.com/",
    ):
        assert not ssrf_guard.is_safe_url(url)


def test_blocks_private_addresses_for_non_internal_hosts(monkeypatch):
    monkeypatch.setattr(
        ssrf_guard,
        "ALLOWED_HOSTS",
        frozenset({"public.example"}),
    )
    monkeypatch.setattr(
        ssrf_guard,
        "_resolve_all",
        lambda host, port: (ipaddress.ip_address("10.0.0.1"),),
    )
    assert not ssrf_guard.is_safe_url("https://public.example/")


def test_blocks_ipv4_mapped_ipv6():
    assert ssrf_guard._is_blocked_ip(
        ipaddress.ip_address("::ffff:127.0.0.1")
    )


def test_allows_configured_internal_service(monkeypatch):
    monkeypatch.setattr(
        ssrf_guard,
        "_resolve_all",
        lambda host, port: (ipaddress.ip_address("172.20.0.5"),),
    )
    assert ssrf_guard.is_safe_url("http://action-gate:8000/health")
    assert ssrf_guard.is_safe_url("http://tool:9000/call")


def test_rejects_internal_service_suffix_attack():
    assert not ssrf_guard.is_safe_url("http://action-gate.evil.example/")


def test_require_safe_url_is_a_hard_failure(monkeypatch):
    monkeypatch.setattr(ssrf_guard, "ALLOWED_HOSTS", frozenset())
    try:
        ssrf_guard.require_safe_url("https://evil.example/")
    except ValueError:
        pass
    else:
        raise AssertionError("unsafe URL was not rejected")
