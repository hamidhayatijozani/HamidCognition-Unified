import os
import tempfile

os.environ["ACTION_GATE_DB"] = os.path.join(tempfile.gettempdir(), "hamidcognition-action-gate-test.db")
os.environ["ACTION_GATE_ENV"] = "development"

from fastapi.testclient import TestClient
from app import app, canonical, digest

client = TestClient(app)
TENANT = "tenant-a"


def evaluate(payload):
    payload = {"tenant_id": TENANT, **payload}
    r = client.post("/v1/action/evaluate", json=payload)
    assert r.status_code == 200
    return r.json()


def test_delete_production_is_denied():
    data = evaluate({"agent_id": "a", "action": "delete_file", "target": "/production/data.db"})
    assert data["decision"] == "DENY"
    assert data["risk_assessment"]["level"] == "CRITICAL"
    assert data["policy_version"]
    assert data["decision_signature"]


def test_external_email_requires_bound_approval_then_replay_matches():
    data = evaluate({"agent_id": "a", "action": "send_email", "target": "customer@example.com"})
    assert data["decision"] == "ASK"
    decision_id = data["decision_id"]
    bad = client.post(f"/v1/action/{decision_id}/approve", json={"approver_id": "human-1", "approved": True, "action_hash": "wrong", "tenant_id": TENANT, "policy_version": data["policy_version"]})
    assert bad.status_code == 409
    approved = client.post(f"/v1/action/{decision_id}/approve", json={"approver_id": "human-1", "approved": True, "action_hash": data["action_hash"], "tenant_id": TENANT, "policy_version": data["policy_version"]})
    assert approved.status_code == 200
    assert approved.json()["decision"] == "ALLOW"
    replay = client.get(f"/v1/replay/{decision_id}?tenant_id={TENANT}")
    assert replay.json()["match"] is True
    execution = client.post(f"/v1/action/{decision_id}/execution", json={"tenant_id": TENANT, "action_hash": data["action_hash"], "nonce": data["nonce"], "outcome": {"sent": True}})
    assert execution.status_code == 200
    replayed_nonce = client.post(f"/v1/action/{decision_id}/execution", json={"tenant_id": TENANT, "action_hash": data["action_hash"], "nonce": data["nonce"], "outcome": {"sent": True}})
    assert replayed_nonce.status_code == 409


def test_financial_action_is_sandboxed():
    data = evaluate({"agent_id": "a", "action": "transfer_funds", "target": "account-1", "parameters": {"amount": 1000}})
    assert data["decision"] == "SANDBOX"


def test_agent_risk_hint_cannot_lower_intrinsic_risk():
    data = evaluate({"agent_id": "a", "action": "delete_database", "target": "/prod/db", "risk_hint": "low"})
    assert data["risk_assessment"]["level"] == "CRITICAL"
    assert data["decision"] == "DENY"


def test_denied_action_cannot_execute():
    data = evaluate({"agent_id": "a", "action": "delete_file", "target": "/production/data.db"})
    blocked = client.post(f"/v1/action/{data['decision_id']}/execution", json={"tenant_id": TENANT, "action_hash": data["action_hash"], "nonce": data["nonce"], "outcome": {"status": "should-not-run"}})
    assert blocked.status_code == 403


def test_allowed_execution_requires_exact_hash_and_nonce():
    data = evaluate({"agent_id": "a", "action": "read_public_file", "target": "/public/info.txt", "parameters": {"mode": "read"}})
    bad = client.post(f"/v1/action/{data['decision_id']}/execution", json={"tenant_id": TENANT, "action_hash": "tampered", "nonce": data["nonce"], "outcome": {"ok": True}})
    assert bad.status_code == 409
    bad_nonce = client.post(f"/v1/action/{data['decision_id']}/execution", json={"tenant_id": TENANT, "action_hash": data["action_hash"], "nonce": "tampered", "outcome": {"ok": True}})
    assert bad_nonce.status_code == 409
    good = client.post(f"/v1/action/{data['decision_id']}/execution", json={"tenant_id": TENANT, "action_hash": data["action_hash"], "nonce": data["nonce"], "outcome": {"ok": True}})
    assert good.status_code == 200


def test_cross_tenant_access_is_hidden():
    data = evaluate({"agent_id": "a", "action": "read_public_file", "target": "/public/info.txt"})
    denied = client.get(f"/v1/evidence/{data['decision_id']}?tenant_id=tenant-b")
    assert denied.status_code == 404


def test_production_requires_auth_configuration():
    import app as module
    old_env, old_token = module.ENVIRONMENT, module.API_TOKEN
    module.ENVIRONMENT, module.API_TOKEN = "production", None
    try:
        r = client.get("/health")
        assert r.status_code == 200
        r = client.post("/v1/action/evaluate", json={"tenant_id": TENANT, "agent_id": "a", "action": "read_public_file"})
        assert r.status_code == 503
    finally:
        module.ENVIRONMENT, module.API_TOKEN = old_env, old_token


def test_production_requires_signing_secret():
    import app as module
    old_env, old_token, old_secret = module.ENVIRONMENT, module.API_TOKEN, module.SIGNING_SECRET
    module.ENVIRONMENT, module.API_TOKEN, module.SIGNING_SECRET = "production", "ci-token", None
    try:
        r = client.post("/v1/action/evaluate", headers={"Authorization": "Bearer ci-token"}, json={"tenant_id": TENANT, "agent_id": "a", "action": "read_public_file"})
        assert r.status_code == 503
    finally:
        module.ENVIRONMENT, module.API_TOKEN, module.SIGNING_SECRET = old_env, old_token, old_secret


def test_hmac_signature_verifies_and_detects_tampering():
    import app as module
    old_secret = module.SIGNING_SECRET
    module.SIGNING_SECRET = "unit-test-secret"
    try:
        data = evaluate({"agent_id": "a", "action": "read_public_file", "target": "/public/info.txt"})
        assert len(data["decision_signature"]) == 64
        record = module.load(data["decision_id"], TENANT)
        assert module.verify_signature(record)
        record["action_hash"] = "tampered"
        assert not module.verify_signature(record)
    finally:
        module.SIGNING_SECRET = old_secret


def test_rate_limit_is_enforced():
    import app as module
    old_limiter = module.limiter
    from rate_limit import SlidingWindowRateLimiter
    module.limiter = SlidingWindowRateLimiter(1, 60)
    try:
        first = client.post("/v1/action/evaluate", json={"tenant_id": "rate-tenant", "agent_id": "a", "action": "read_public_file"})
        second = client.post("/v1/action/evaluate", json={"tenant_id": "rate-tenant", "agent_id": "a", "action": "read_public_file"})
        assert first.status_code == 200
        assert second.status_code == 429
    finally:
        module.limiter = old_limiter


def test_evidence_versions_are_append_only():
    import app as module
    data = evaluate({"agent_id": "a", "action": "send_email", "target": "customer@example.com"})
    module.load(data["decision_id"], TENANT)
    con = module.db()
    versions = con.execute("SELECT COUNT(*) FROM record_versions WHERE decision_id=?", (data["decision_id"],)).fetchone()[0]
    con.close()
    assert versions >= 1


def test_health_version():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["version"] == "0.2.1-secure-multitenant-mvp"
