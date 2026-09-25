import os
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from action_gate.enforcement import enforce_execution_authority, require_execution_authority
from action_gate.security_authority import issue_authority


@pytest.fixture()
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("ACTION_GATE_AUTHORITY_SECRET", "test-authority-secret")
    import action_gate.storage as storage
    monkeypatch.setattr(storage, "SQLITE_PATH", str(tmp_path / "enforcement.db"))
    storage.init_db()

    app = FastAPI()

    @app.post("/protected-tools/execute")
    def execute(auth_context=Depends(require_execution_authority)):
        return {"ok": True, "tenant_id": auth_context["tenant_id"]}

    return TestClient(app)


def mint(*, tenant_id="tenant-a", action=None):
    return issue_authority(
        secret=b"test-authority-secret",
        decision_id="dec_test",
        tenant_id=tenant_id,
        action=action or {"action": "protected.execute", "target": "prod"},
        policy={"version": "policy-1"},
        decision="ALLOW",
        ttl_seconds=300,
        now=int(time.time()),
    )


def test_direct_tool_access_is_forbidden(client):
    response = client.post("/protected-tools/execute")
    assert response.status_code == 403
    assert "Missing Execution Authority" in response.text


def test_replay_is_forbidden(client):
    token = mint().token()
    assert client.post("/protected-tools/execute", headers={"X-Action-Gate-Authority": token}).status_code == 200
    response = client.post("/protected-tools/execute", headers={"X-Action-Gate-Authority": token})
    assert response.status_code == 403
    assert "nonce_reuse" in response.text


def test_tenant_tampering_is_forbidden(monkeypatch, tmp_path):
    monkeypatch.setenv("ACTION_GATE_AUTHORITY_SECRET", "test-authority-secret")
    import action_gate.storage as storage
    monkeypatch.setattr(storage, "SQLITE_PATH", str(tmp_path / "tenant.db"))
    storage.init_db()
    token = mint(tenant_id="tenant-a").token()
    with pytest.raises(Exception) as exc:
        enforce_execution_authority(token, expected_tenant_id="tenant-b")
    assert "tenant_mismatch" in str(exc.value)


def test_action_tampering_is_forbidden(monkeypatch, tmp_path):
    monkeypatch.setenv("ACTION_GATE_AUTHORITY_SECRET", "test-authority-secret")
    import action_gate.storage as storage
    monkeypatch.setattr(storage, "SQLITE_PATH", str(tmp_path / "action.db"))
    storage.init_db()
    token = mint(action={"action": "protected.execute", "target": "prod"}).token()
    with pytest.raises(Exception) as exc:
        enforce_execution_authority(
            token,
            expected_action={"action": "protected.execute", "target": "different-prod"},
            expected_policy={"version": "policy-1"},
        )
    assert "action_binding_mismatch" in str(exc.value)


def test_nonce_consumption_is_atomic(monkeypatch, tmp_path):
    monkeypatch.setenv("ACTION_GATE_AUTHORITY_SECRET", "test-authority-secret")
    import action_gate.storage as storage
    monkeypatch.setattr(storage, "SQLITE_PATH", str(tmp_path / "atomic.db"))
    storage.init_db()
    assert storage.consume_authority_nonce("nonce-1", "dec-1", "2026-09-25T00:00:00+00:00")
    assert not storage.consume_authority_nonce("nonce-1", "dec-1", "2026-09-25T00:00:01+00:00")


def test_expired_authority_is_forbidden(monkeypatch, tmp_path):
    monkeypatch.setenv("ACTION_GATE_AUTHORITY_SECRET", "test-authority-secret")
    import action_gate.storage as storage
    monkeypatch.setattr(storage, "SQLITE_PATH", str(tmp_path / "expiry.db"))
    storage.init_db()
    authority = issue_authority(
        secret=b"test-authority-secret",
        decision_id="dec_expired",
        tenant_id="tenant-a",
        action={"action": "protected.execute", "target": "prod"},
        policy={"version": "policy-1"},
        decision="ALLOW",
        ttl_seconds=1,
        now=int(time.time()) - 10,
    )
    with pytest.raises(Exception) as exc:
        enforce_execution_authority(authority.token())
    assert "expired_or_not_yet_valid" in str(exc.value)

def test_concurrent_same_nonce_only_one_succeeds(monkeypatch, tmp_path):
    monkeypatch.setenv("ACTION_GATE_AUTHORITY_SECRET", "test-authority-secret")
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
