import time

import pytest

from action_gate.security_authority import AuthorityError, issue_authority
from action_gate.tool_server import verify_execution_authority


SECRET = b"tool-test-secret"
ACTION = {"action": "protected.execute", "target": "prod"}
POLICY = {"version": "policy-1"}


def mint():
    return issue_authority(
        secret=SECRET,
        decision_id="dec-tool-test",
        tenant_id="tenant-a",
        action=ACTION,
        policy=POLICY,
        decision="ALLOW",
        ttl_seconds=300,
    ).token()


def test_tool_boundary_binds_action_and_policy(monkeypatch, tmp_path):
    monkeypatch.setenv("ACTION_GATE_AUTHORITY_SECRET", SECRET.decode())
    monkeypatch.setenv("TOOL_NONCE_DB", str(tmp_path / "nonce.db"))
    token = mint()
    payload = {"tenant_id": "tenant-a", "action": ACTION, "policy": POLICY, "parameters": {"x": 1}}
    verify_execution_authority(token, "tenant-a", payload)


def test_tool_boundary_rejects_payload_tampering(monkeypatch, tmp_path):
    monkeypatch.setenv("ACTION_GATE_AUTHORITY_SECRET", SECRET.decode())
    monkeypatch.setenv("TOOL_NONCE_DB", str(tmp_path / "nonce.db"))
    token = mint()
    tampered = {"tenant_id": "tenant-a", "action": {"action": "protected.execute", "target": "attacker"}, "policy": POLICY}
    with pytest.raises(AuthorityError, match="action_binding_mismatch"):
        verify_execution_authority(token, "tenant-a", tampered)


def test_tool_boundary_rejects_sandbox_authority(monkeypatch, tmp_path):
    monkeypatch.setenv("ACTION_GATE_AUTHORITY_SECRET", SECRET.decode())
    monkeypatch.setenv("TOOL_NONCE_DB", str(tmp_path / "nonce.db"))
    token = issue_authority(
        secret=SECRET,
        decision_id="dec-sandbox",
        tenant_id="tenant-a",
        action=ACTION,
        policy=POLICY,
        decision="SANDBOX",
        ttl_seconds=300,
    ).token()
    payload = {"tenant_id": "tenant-a", "action": ACTION, "policy": POLICY}
    with pytest.raises(AuthorityError, match="decision_not_executable"):
        verify_execution_authority(token, "tenant-a", payload)
