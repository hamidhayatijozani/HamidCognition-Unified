import os
import tempfile

os.environ["ACTION_GATE_DB"] = os.path.join(tempfile.gettempdir(), "hamidcognition-action-gate-test.db")

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def evaluate(payload):
    r = client.post("/v1/action/evaluate", json=payload)
    assert r.status_code == 200
    return r.json()


def test_delete_production_is_denied():
    data = evaluate({"agent_id": "a", "action": "delete_file", "target": "/production/data.db"})
    assert data["decision"] == "DENY"
    assert data["risk_assessment"]["level"] == "CRITICAL"


def test_external_email_requires_action_bound_approval_then_replay_matches_preapproval():
    data = evaluate({"agent_id": "a", "action": "send_email", "target": "customer@example.com"})
    assert data["decision"] == "ASK"
    decision_id = data["decision_id"]
    bad = client.post(f"/v1/action/{decision_id}/approve", json={"approver_id": "human-1", "approved": True, "action_hash": "wrong"})
    assert bad.status_code == 409
    approved = client.post(f"/v1/action/{decision_id}/approve", json={"approver_id": "human-1", "approved": True, "action_hash": data["action_hash"], "ttl_seconds": 300})
    assert approved.status_code == 200
    assert approved.json()["decision"] == "ALLOW"
    replay = client.get(f"/v1/replay/{decision_id}")
    assert replay.json()["match"] is True
    assert replay.json()["recorded_preapproval_decision"] == "ASK"
    execution = client.post(f"/v1/action/{decision_id}/execution", json={"action_hash": data["action_hash"], "outcome": {"sent": True}})
    assert execution.status_code == 200


def test_financial_action_is_sandboxed():
    data = evaluate({"agent_id": "a", "action": "transfer_funds", "target": "account-1", "parameters": {"amount": 1000}})
    assert data["decision"] == "SANDBOX"


def test_agent_risk_hint_cannot_lower_intrinsic_risk():
    data = evaluate({"agent_id": "a", "action": "delete_database", "target": "/prod/db", "risk_hint": "low"})
    assert data["risk_assessment"]["level"] == "CRITICAL"
    assert data["decision"] == "DENY"


def test_denied_action_cannot_execute():
    data = evaluate({"agent_id": "a", "action": "delete_file", "target": "/production/data.db"})
    blocked = client.post(f"/v1/action/{data['decision_id']}/execution", json={"action_hash": data["action_hash"], "outcome": {"status": "should-not-run"}})
    assert blocked.status_code == 403


def test_allowed_execution_requires_exact_action_hash():
    data = evaluate({"agent_id": "a", "action": "read_public_file", "target": "/public/info.txt", "parameters": {"mode": "read"}})
    bad = client.post(f"/v1/action/{data['decision_id']}/execution", json={"action_hash": "tampered", "outcome": {"ok": True}})
    assert bad.status_code == 409
    good = client.post(f"/v1/action/{data['decision_id']}/execution", json={"action_hash": data["action_hash"], "outcome": {"ok": True}})
    assert good.status_code == 200


def test_health_exposes_product_version():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["product"] == "HamidCognition Action Gate"
    assert r.json()["version"] == "0.3.0-mvp"
