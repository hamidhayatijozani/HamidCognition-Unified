import importlib
import os
from datetime import datetime, timedelta, timezone

import pytest
from httpx import ASGITransport, AsyncClient


def load_app(monkeypatch, secret="test-secret"):
    monkeypatch.setenv("HHJ_CSG_HMAC_SECRET", secret)
    monkeypatch.setenv("HHJ_CSG_API_KEY", "test-api-key")
    import action_gate.contract_app as module
    module = importlib.reload(module)
    module._idempotency.clear()
    module._audit.clear()
    return module


def request_body(event_id="evt-001", action="read"):
    return {
        "contract_version": "PR-0.1",
        "request_id": event_id,
        "tenant_id": "tenant-a",
        "agent_id": "agentrq-sim",
        "action": action,
        "target": "fixture/resource",
        "parameters": {"limit": 10},
        "context": {"source": "simulator"},
        "evidence": [{"type": "fixture", "ref": "fixture-001"}],
        "risk_hint": "LOW",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "idempotency_key": event_id,
    }


def signed_headers(module, body):
    from action_gate.contract import hmac_sha256, sha256_digest
    payload = {"contract_version": "PR-0.1", "request_digest": sha256_digest(body)}
    return {
        "X-API-Key": "test-api-key",
        "X-HHJ-Canonicalization": "JCS-LITE-0.1",
        "X-HHJ-Key-Id": module.HMAC_KEY_ID,
        "X-HHJ-Signature": hmac_sha256(payload, "test-secret"),
    }


@pytest.mark.anyio
async def test_vertical_slice_valid_and_replay(monkeypatch):
    module = load_app(monkeypatch)
    body = request_body()
    async with AsyncClient(transport=ASGITransport(app=module.app), base_url="http://test") as client:
        first = await client.post("/decide", json=body, headers=signed_headers(module, body))
        second = await client.post("/decide", json=body, headers=signed_headers(module, body))
    assert first.status_code == 200
    assert second.status_code == 200
    a, b = first.json(), second.json()
    assert a["replayed"] is False
    assert b["replayed"] is True
    assert a["request_digest"] == b["request_digest"]
    assert a["decision_digest"] == b["decision_digest"]
    assert a["decision"] == b["decision"]


@pytest.mark.anyio
async def test_idempotency_key_cannot_bind_two_requests(monkeypatch):
    module = load_app(monkeypatch)
    body = request_body()
    changed = {**body, "parameters": {"limit": 11}}
    async with AsyncClient(transport=ASGITransport(app=module.app), base_url="http://test") as client:
        first = await client.post("/decide", json=body, headers=signed_headers(module, body))
        second = await client.post("/decide", json=changed, headers=signed_headers(module, changed))
    assert first.status_code == 200
    assert second.status_code == 409
    assert second.json()["detail"]["code"] == "IDEMPOTENCY_KEY_REUSED"


@pytest.mark.anyio
async def test_signature_failure_is_rejected(monkeypatch):
    module = load_app(monkeypatch)
    body = request_body()
    headers = signed_headers(module, body)
    headers["X-HHJ-Signature"] = "0" * 64
    async with AsyncClient(transport=ASGITransport(app=module.app), base_url="http://test") as client:
        response = await client.post("/decide", json=body, headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "SIGNATURE_INVALID"


@pytest.mark.anyio
async def test_schema_and_timestamp_boundaries(monkeypatch):
    module = load_app(monkeypatch)
    malformed = request_body()
    del malformed["agent_id"]
    async with AsyncClient(transport=ASGITransport(app=module.app), base_url="http://test") as client:
        bad_schema = await client.post("/decide", json=malformed, headers={"X-API-Key": "test-api-key"})
        stale = request_body("evt-stale")
        stale["timestamp"] = (datetime.now(timezone.utc) - timedelta(seconds=301)).isoformat()
        stale_headers = signed_headers(module, stale)
        stale_response = await client.post("/decide", json=stale, headers=stale_headers)
    assert bad_schema.status_code == 422
    assert bad_schema.json()["detail"]["code"] == "SCHEMA_INVALID"
    assert stale_response.status_code == 409
    assert stale_response.json()["detail"]["code"] == "REPLAY_TIMESTAMP_EXPIRED"


@pytest.mark.anyio
async def test_high_risk_is_non_executable(monkeypatch):
    module = load_app(monkeypatch)
    body = request_body("evt-high", "delete_database")
    body["target"] = "production/database"
    body["risk_hint"] = "CRITICAL"
    async with AsyncClient(transport=ASGITransport(app=module.app), base_url="http://test") as client:
        response = await client.post("/decide", json=body, headers=signed_headers(module, body))
    assert response.status_code == 200
    assert response.json()["decision"] == "DENY"
