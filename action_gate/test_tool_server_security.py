import pytest

import action_gate.tool_server as tool_server
from action_gate.security_authority import AuthorityError, issue_authority

SECRET = b"tool-test-secret"
ACTION = {"action": "protected.execute", "target": "prod"}
POLICY = {"version": "policy-1"}


def mint(decision="ALLOW"):
    return issue_authority(
        secret=SECRET,
        decision_id="dec-tool-test",
        tenant_id="tenant-a",
        action=ACTION,
        policy=POLICY,
        decision=decision,
        ttl_seconds=300,
    ).token()


def setup(monkeypatch, tmp_path):
    monkeypatch.setattr(tool_server, "AUTHORITY_SECRET", SECRET.decode())
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
