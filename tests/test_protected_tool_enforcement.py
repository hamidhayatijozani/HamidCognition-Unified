import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from action_gate.enforcement import enforce_execution_authority
from action_gate.security_authority import issue_authority


SECRET = b"test-authority-secret"
ACTION = {"action": "protected.execute", "target": "prod"}
POLICY = {"version": "policy-1"}


@pytest.fixture()
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("ACTION_GATE_AUTHORITY_SECRET", SECRET.decode())
    import action_gate.storage as storage

    monkeypatch.setattr(storage, "SQLITE_PATH", str(tmp_path / "enforcement.db"))
    storage.init_db()

    from protected_tools.reference_tool import app

    return TestClient(app)


def mint(*, tenant_id="tenant-a", action=None, policy=None, ttl_seconds=300, now=None, nonce=None):
    return issue_authority(
        secret=SECRET,
        decision_id="dec_test",
        tenant_id=tenant_id,
        action=action or ACTION,
        policy=policy or POLICY,
        decision="ALLOW",
        ttl_seconds=ttl_seconds,
        now=int(time.time()) if now is None else now,
        nonce=nonce,
    )


def payload(*, tenant_id="tenant-a", action=None, policy=None):
    return {
        "tenant_id": tenant_id,
        "action": action or ACTION,
        "policy": policy or POLICY,
        "parameters": {"dry_run": True},
    }


def headers(token):
    return {"X-Action-Gate-Authority": token}


def test_direct_tool_access_is_forbidden(client):
    response = client.post("/v1/protected/execute", json=payload())
    assert response.status_code == 403
    assert "Missing Execution Authority" in response.text


def test_replay_is_forbidden(client):
    token = mint().token()
    assert client.post("/v1/protected/execute", json=payload(), headers=headers(token)).status_code == 200
    response = client.post("/v1/protected/execute", json=payload(), headers=headers(token))
    assert response.status_code == 403
    assert "nonce_reuse" in response.text


def test_tenant_tampering_is_forbidden(client):
    token = mint(tenant_id="tenant-a").token()
    response = client.post(
        "/v1/protected/execute",
        json=payload(tenant_id="tenant-b"),
        headers=headers(token),
    )
    assert response.status_code == 403
    assert "tenant_mismatch" in response.text


def test_action_tampering_is_forbidden(client):
    token = mint(action=ACTION).token()
    tampered_action = {"action": "protected.execute", "target": "different-prod"}
    response = client.post(
        "/v1/protected/execute",
        json=payload(action=tampered_action),
        headers=headers(token),
    )
    assert response.status_code == 403
    assert "action_binding_mismatch" in response.text


def test_policy_tampering_is_forbidden(client):
    token = mint(policy=POLICY).token()
    tampered_policy = {"version": "policy-2"}
    response = client.post(
        "/v1/protected/execute",
        json=payload(policy=tampered_policy),
        headers=headers(token),
    )
    assert response.status_code == 403
    assert "policy_binding_mismatch" in response.text


def test_expired_authority_is_forbidden(client):
    authority = mint(ttl_seconds=1, now=int(time.time()) - 10)
    response = client.post(
        "/v1/protected/execute",
        json=payload(),
        headers=headers(authority.token()),
    )
    assert response.status_code == 403
    assert "expired_or_not_yet_valid" in response.text


def test_nonce_consumption_is_atomic(monkeypatch, tmp_path):
    monkeypatch.setenv("ACTION_GATE_AUTHORITY_SECRET", SECRET.decode())
    import action_gate.storage as storage

    monkeypatch.setattr(storage, "SQLITE_PATH", str(tmp_path / "atomic.db"))
    storage.init_db()
    assert storage.consume_authority_nonce("nonce-1", "dec-1", "2026-09-25T00:00:00+00:00")
    assert not storage.consume_authority_nonce("nonce-1", "dec-1", "2026-09-25T00:00:01+00:00")


def test_concurrent_same_nonce_only_one_succeeds(monkeypatch, tmp_path):
    monkeypatch.setenv("ACTION_GATE_AUTHORITY_SECRET", SECRET.decode())
    import action_gate.storage as storage

    monkeypatch.setattr(storage, "SQLITE_PATH", str(tmp_path / "race.db"))
    storage.init_db()

    def consume(_):
        return storage.consume_authority_nonce(
            "shared-race-nonce", "dec-race", "2026-09-25T00:00:00+00:00"
        )

    with ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(consume, range(10)))
    assert sum(results) == 1


def test_low_level_binding_checks_remain_fail_closed(monkeypatch, tmp_path):
    monkeypatch.setenv("ACTION_GATE_AUTHORITY_SECRET", SECRET.decode())
    import action_gate.storage as storage

    monkeypatch.setattr(storage, "SQLITE_PATH", str(tmp_path / "binding.db"))
    storage.init_db()
    token = mint().token()

    with pytest.raises(Exception, match="action_binding_mismatch"):
        enforce_execution_authority(token, expected_action={"action": "other"})
