import importlib
from datetime import datetime, timedelta, timezone

import pytest

from action_gate.agent_rq_simulator import make_event
from action_gate.contract import hmac_sha256
from action_gate.contract_execution import execute_simulated, reset_nonce_ledger


def build_decision(monkeypatch):
    monkeypatch.setenv("HHJ_CSG_HMAC_SECRET", "exec-secret")
    monkeypatch.setenv("HHJ_CSG_API_KEY", "exec-api-key")
    import action_gate.contract_app as module
    module = importlib.reload(module)
    module._idempotency.clear()
    module._audit.clear()
    reset_nonce_ledger()
    body = make_event(42)
    # Simulator uses a different secret by default; sign only the request here.
    from action_gate.contract import sha256_digest
    payload = {"contract_version": "PR-0.1", "request_digest": sha256_digest(body)}
    return module, body, payload


@pytest.mark.anyio
async def test_allow_decision_can_cross_simulated_execution_boundary(monkeypatch):
    module, body, payload = build_decision(monkeypatch)
    from httpx import ASGITransport, AsyncClient
    headers = {
        "X-API-Key": "exec-api-key",
        "X-HHJ-Canonicalization": "JCS-LITE-0.1",
        "X-HHJ-Key-Id": module.HMAC_KEY_ID,
        "X-HHJ-Signature": hmac_sha256(payload, "exec-secret"),
        "Idempotency-Key": body["idempotency_key"],
    }
    async with AsyncClient(transport=ASGITransport(app=module.app), base_url="http://test") as client:
        decision_response = await client.post("/decide", json=body, headers=headers)
    assert decision_response.status_code == 200
    decision = decision_response.json()
    receipt = execute_simulated(body, decision, secret="exec-secret", now=datetime.now(timezone.utc))
    assert receipt["status"] == "EXECUTED"
    assert receipt["decision_id"] == decision["decision_id"]
    assert receipt["request_digest"] == decision["request_digest"]


def test_tampered_decision_digest_is_rejected(monkeypatch):
    module, body, payload = build_decision(monkeypatch)
    from action_gate.contract import sha256_digest
    request_digest = sha256_digest(body)
    decision = module.make_decision(body, "trace-test")
    decision["decision_digest"] = "0" * 64
    with pytest.raises(ValueError, match="decision_digest_mismatch"):
        execute_simulated(body, decision, secret="exec-secret")


def test_wrong_request_cannot_reuse_decision(monkeypatch):
    module, body, payload = build_decision(monkeypatch)
    decision = module.make_decision(body, "trace-test")
    changed = {**body, "target": "attacker/target"}
    with pytest.raises(ValueError, match="request_digest_mismatch"):
        execute_simulated(changed, decision, secret="exec-secret")


def test_nonce_can_only_be_consumed_once(monkeypatch):
    module, body, payload = build_decision(monkeypatch)
    decision = module.make_decision(body, "trace-test")
    execute_simulated(body, decision, secret="exec-secret")
    with pytest.raises(ValueError, match="nonce_already_consumed"):
        execute_simulated(body, decision, secret="exec-secret")


def test_expired_decision_is_rejected(monkeypatch):
    module, body, payload = build_decision(monkeypatch)
    decision = module.make_decision(body, "trace-test")
    now = datetime.fromisoformat(decision["expires_at"]) + timedelta(seconds=1)
    with pytest.raises(ValueError, match="decision_expired"):
        execute_simulated(body, decision, secret="exec-secret", now=now)
