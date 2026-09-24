import importlib
import os

import pytest

from security_authority import issue_authority, AuthorityError


def test_tool_accepts_only_gate_issued_authority(monkeypatch, tmp_path):
    monkeypatch.setenv("ACTION_GATE_SIGNING_SECRET", "authority-test-secret")
    monkeypatch.setenv("TOOL_NONCE_DB", str(tmp_path / "tool-authority.db"))
    import tool_server
    importlib.reload(tool_server)

    action = {"tenant_id": "tenant-a", "actor_id": "actor-a", "session_id": "session-a", "action": "read_public_file", "target": "/public/info.txt", "parameters": {}}
    policy = {"policy_version": "test-policy", "rules": ["allow-read"]}
    authority = issue_authority(
        secret=b"authority-test-secret",
        decision_id="dec-1",
        tenant_id="tenant-a",
        action=action,
        policy=policy,
        decision="ALLOW" ,
        now=int(__import__("time").time()),
        nonce="nonce-1",
        ttl_seconds=300,
    )

    tool_server.verify_execution_authority(authority.token(), "tenant-a", authority.action_digest)

    with pytest.raises(AuthorityError, match="direct_tool_access_rejected"):
        tool_server.verify_execution_authority(None, "tenant-a", authority.action_digest)


def test_tool_rejects_tampered_authority(monkeypatch, tmp_path):
    monkeypatch.setenv("ACTION_GATE_SIGNING_SECRET", "authority-test-secret")
    monkeypatch.setenv("TOOL_NONCE_DB", str(tmp_path / "tool-authority.db"))
    import tool_server
    importlib.reload(tool_server)

    action = {"tenant_id": "tenant-a", "action": "read_public_file", "target": "/public/info.txt", "parameters": {}}
    policy = {"policy_version": "test-policy", "rules": ["allow-read"]}
    authority = issue_authority(
        secret=b"authority-test-secret",
        decision_id="dec-2",
        tenant_id="tenant-a",
        action=action,
        policy=policy,
        decision="ALLOW" ,
        now=int(__import__("time").time()),
        nonce="nonce-2",
        ttl_seconds=300,
    )
    tampered = authority.token()[:-1] + ("A" if authority.token()[-1] != "A" else "B")

    with pytest.raises(AuthorityError):
        tool_server.verify_execution_authority(tampered, "tenant-a", authority.action_digest)
