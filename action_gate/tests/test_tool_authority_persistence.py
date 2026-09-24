import importlib

import pytest

from action_gate.security_authority import AuthorityError, issue_authority


SECRET = b"test-only-action-gate-secret"


def test_tool_nonce_claim_survives_module_reload(tmp_path, monkeypatch):
    db = tmp_path / "tool_authority.db"
    monkeypatch.setenv("TOOL_NONCE_DB", str(db))
    import action_gate.tool_server as tool_server
    tool_server.TOOL_NONCE_DB = str(db)

    authority = issue_authority(
        secret=SECRET,
        decision_id="dec-1",
        tenant_id="tenant-a",
        action={"verb": "write", "resource": "customer/42"},
        policy={"version": "p1"},
        decision="ALLOW",
        now=1000,
        nonce="nonce-persistent",
        ttl_seconds=300,
    )
    tool_server._claim_nonce(authority.nonce, authority.decision_id, authority.expires_at)

    reloaded = importlib.reload(tool_server)
    reloaded.TOOL_NONCE_DB = str(db)
    with pytest.raises(AuthorityError, match="nonce_reuse"):
        reloaded._claim_nonce(authority.nonce, authority.decision_id, authority.expires_at)


def test_tool_rejects_sandbox_authority():
    import action_gate.tool_server as tool_server
    tool_server.SIGNING_SECRET = SECRET
    authority = issue_authority(
        secret=SECRET,
        decision_id="dec-2",
        tenant_id="tenant-a",
        action={"verb": "write", "resource": "customer/42"},
        policy={"version": "p1"},
        decision="SANDBOX",
        now=1000,
        nonce="nonce-sandbox",
    )
    with pytest.raises(AuthorityError, match="decision_not_executable"):
        tool_server.verify_execution_authority(
            authority.token(),
            "tenant-a",
            authority.action_digest,
        )
