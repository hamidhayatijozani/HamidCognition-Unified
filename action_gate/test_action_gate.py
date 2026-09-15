import os
import tempfile

os.environ["ACTION_GATE_DB"] = os.path.join(tempfile.gettempdir(), "hamidcognition-action-gate-test.db")

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_delete_production_is_denied():
    r = client.post("/v1/action/evaluate", json={"agent_id": "a", "action": "delete_file", "target": "/production/data.db"})
    assert r.status_code == 200
    assert r.json()["decision"] == "DENY"
    assert r.json()["risk_assessment"]["level"] == "CRITICAL"


def test_external_email_requires_approval_then_replay_matches_preapproval():
    r = client.post("/v1/action/evaluate", json={"agent_id": "a", "action": "send_email", "target": "customer@example.com"})
    data = r.json()
    assert data["decision"] == "ASK"
    decision_id = data["decision_id"]
    approved = client.post(f"/v1/action/{decision_id}/approve", json={"approver_id": "human-1", "approved": True})
    assert approved.json()["decision"] == "ALLOW"
    replay = client.get(f"/v1/replay/{decision_id}")
    assert replay.json()["match"] is True
    assert replay.json()["recorded_preapproval_decision"] == "ASK"


def test_financial_action_is_sandboxed():
    r = client.post("/v1/action/evaluate", json={"agent_id": "a", "action": "transfer_funds", "target": "account-1", "parameters": {"amount": 1000}})
    assert r.json()["decision"] == "SANDBOX"


def test_agent_risk_hint_cannot_lower_intrinsic_risk():
    r = client.post("/v1/action/evaluate", json={"agent_id": "a", "action": "delete_database", "target": "/prod/db", "risk_hint": "low"})
    assert r.json()["risk_assessment"]["level"] == "CRITICAL"
    assert r.json()["decision"] == "DENY"


def test_denied_action_cannot_execute():
    r = client.post("/v1/action/evaluate", json={"agent_id": "a", "action": "delete_file", "target": "/production/data.db"})
    decision_id = r.json()["decision_id"]
    blocked = client.post(f"/v1/action/{decision_id}/execution", json={"status": "should-not-run"})
    assert blocked.status_code == 403
