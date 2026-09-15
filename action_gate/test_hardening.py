import os
import tempfile

os.environ["ACTION_GATE_DB"] = os.path.join(tempfile.gettempdir(), "hamidcognition-action-gate-hardening.db")

from fastapi.testclient import TestClient
import app

client = TestClient(app.app)


def test_policy_snapshot_and_action_binding_are_replayable():
    r = client.post("/v1/action/evaluate", json={"agent_id": "a", "action": "send_email", "target": "customer@example.com", "parameters": {"body": "one"}})
    data = r.json()
    assert data["decision"] == "ASK"
    assert data["policy_hash"]
    assert data["action_hash"]
    decision_id = data["decision_id"]
    client.post(f"/v1/action/{decision_id}/approve", json={"approver_id": "human-1", "approved": True})
    replay = client.get(f"/v1/replay/{decision_id}").json()
    assert replay["match"] is True
    assert replay["policy_hash_match"] is True
    assert replay["action_hash_match"] is True


def test_auth_can_be_enabled_fail_closed(monkeypatch):
    monkeypatch.setattr(app, "API_TOKEN", "test-token")
    assert client.post("/v1/action/evaluate", json={"agent_id": "a", "action": "read_file"}).status_code == 401
    assert client.post("/v1/action/evaluate", headers={"Authorization": "Bearer test-token"}, json={"agent_id": "a", "action": "read_file"}).status_code == 200
    monkeypatch.setattr(app, "API_TOKEN", None)


def test_action_hash_changes_with_payload():
    a = client.post("/v1/action/evaluate", json={"agent_id": "a", "action": "send_email", "target": "customer@example.com", "parameters": {"body": "one"}}).json()
    b = client.post("/v1/action/evaluate", json={"agent_id": "a", "action": "send_email", "target": "customer@example.com", "parameters": {"body": "two"}}).json()
    assert a["action_hash"] != b["action_hash"]
