from concurrent.futures import ThreadPoolExecutor

import pytest

import action_gate.tool_server as tool_server
from action_gate.security_authority import AuthorityError, issue_authority

SECRET = b"tool-test-secret"
ACTION = {"action": "protected.execute", "target": "prod"}
POLICY = {"version": "policy-1"}


def mint(decision="ALLOW", now=None):
    return issue_authority(secret=SECRET, decision_id="dec-tool-test", tenant_id="tenant-a", action=ACTION, policy=POLICY, decision=decision, ttl_seconds=300, now=now).token()


def setup(monkeypatch, tmp_path):
    monkeypatch.setattr(tool_server, "AUTHORITY_SECRET", SECRET.decode())
    monkeypatch.setattr(tool_server, "_verify_live_world_binding", lambda authority, tenant_id: None)
    monkeypatch.setattr(tool_server, "TOOL_NONCE_DB", str(tmp_path / "nonce.db"))


def test_tool_boundary_binds_action_and_policy(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path)
    payload = {"tenant_id": "tenant-a", "action": ACTION, "policy": POLICY, "parameters": {"x": 1}}
    tool_server.verify_execution_authority(mint(), "tenant-a", payload)


def test_tool_boundary_rejects_payload_tampering(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path)
    tampered = {"tenant_id": "tenant-a", "action": {"action": "protected.execute", "target": "attacker"}, "policy": POLICY}
    with pytest.raises(AuthorityError, match="action_binding_mismatch"):
        tool_server.verify_execution_authority(mint(), "tenant-a", tampered)


def test_tool_boundary_rejects_sandbox_authority(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path)
    payload = {"tenant_id": "tenant-a", "action": ACTION, "policy": POLICY}
    with pytest.raises(AuthorityError, match="decision_not_executable"):
        tool_server.verify_execution_authority(mint("SANDBOX"), "tenant-a", payload)


def test_tool_boundary_rejects_expired_authority(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path)
    monkeypatch.setattr(tool_server.time, "time", lambda: 2000)
    payload = {"tenant_id": "tenant-a", "action": ACTION, "policy": POLICY}
    with pytest.raises(AuthorityError, match="expired_or_not_yet_valid"):
        tool_server.verify_execution_authority(mint(now=1000), "tenant-a", payload)


def test_tool_boundary_rejects_tenant_substitution(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path)
    payload = {"tenant_id": "tenant-a", "action": ACTION, "policy": POLICY}
    with pytest.raises(AuthorityError, match="tenant_mismatch"):
        tool_server.verify_execution_authority(mint(), "tenant-b", payload)


def test_tool_boundary_rejects_policy_tampering(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path)
    payload = {"tenant_id": "tenant-a", "action": ACTION, "policy": {"version": "policy-attacker"}}
    with pytest.raises(AuthorityError, match="policy_binding_mismatch"):
        tool_server.verify_execution_authority(mint(), "tenant-a", payload)


def test_same_nonce_is_consumed_only_once_under_concurrency(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path)
    token = mint()
    payload = {"tenant_id": "tenant-a", "action": ACTION, "policy": POLICY}
    def attempt(_):
        try:
            tool_server.verify_execution_authority(token, "tenant-a", payload)
            return "accepted"
        except AuthorityError as exc:
            return str(exc)
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(attempt, range(8)))
    assert results.count("accepted") == 1
    assert results.count("nonce_reuse") == 7


def test_consumed_nonce_survives_database_reopen(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path)
    token = mint()
    payload = {"tenant_id": "tenant-a", "action": ACTION, "policy": POLICY}
    tool_server.verify_execution_authority(token, "tenant-a", payload)
    database_path = tool_server.TOOL_NONCE_DB
    monkeypatch.setattr(tool_server, "TOOL_NONCE_DB", database_path)
    with pytest.raises(AuthorityError, match="nonce_reuse"):
        tool_server.verify_execution_authority(token, "tenant-a", payload)


def test_world_revalidation_disabled_fails_closed(monkeypatch):
    monkeypatch.setattr(tool_server, "WORLD_REVALIDATION_ENABLED", False)
    authority = issue_authority(secret=SECRET, decision_id="d", tenant_id="tenant-a", action=ACTION, policy=POLICY, decision="ALLOW", ttl_seconds=60)
    with pytest.raises(AuthorityError, match="world_revalidation_not_configured"):
        tool_server._verify_live_world_binding(authority, "tenant-a")


def test_live_world_revalidation_fails_closed_when_gate_is_unreachable(monkeypatch):
    import urllib.error
    monkeypatch.setattr(tool_server, "WORLD_REVALIDATION_ENABLED", True)
    monkeypatch.setattr(tool_server, "GATE_API_TOKEN", "test-api-token")
    monkeypatch.setattr(tool_server.urllib.request, "urlopen", lambda *args, **kwargs: (_ for _ in ()).throw(urllib.error.URLError("simulated Gate outage")))
    authority = issue_authority(secret=SECRET, decision_id="d", tenant_id="tenant-a", action=ACTION, policy=POLICY, decision="ALLOW", ttl_seconds=60)
    with pytest.raises(AuthorityError, match="world_revalidation_unavailable"):
        tool_server._verify_live_world_binding(authority, "tenant-a")


def test_missing_world_version_fails_closed(monkeypatch):
    import json
    class Response:
        def __init__(self, value): self.value = value
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self): return json.dumps(self.value).encode()
    monkeypatch.setattr(tool_server, "WORLD_REVALIDATION_ENABLED", True)
    monkeypatch.setattr(tool_server, "GATE_API_TOKEN", "test-api-token")
    authority = issue_authority(secret=SECRET, decision_id="d", tenant_id="tenant-a", action=ACTION, policy=POLICY, decision="ALLOW", ttl_seconds=60)
    monkeypatch.setattr(tool_server.urllib.request, "urlopen", lambda *args, **kwargs: Response({"tenant_id": "tenant-a", "decision": "ALLOW", "nonce": authority.nonce, "decision_id": "d"}))
    with pytest.raises(AuthorityError, match="world_version_missing"):
        tool_server._verify_live_world_binding(authority, "tenant-a")
