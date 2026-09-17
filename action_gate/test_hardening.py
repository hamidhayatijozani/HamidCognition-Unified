import os
import tempfile

os.environ["ACTION_GATE_DB"] = os.path.join(tempfile.gettempdir(), "hamidcognition-action-gate-hardening.db")
os.environ["ACTION_GATE_ENV"] = "development"

from fastapi.testclient import TestClient
import app

client = TestClient(app.app)
TENANT = "tenant-hardening"


def test_policy_snapshot_and_action_binding_are_replayable():
    r = client.post("/v1/action/evaluate", json={"tenant_id": TENANT, "agent_id": "a", "action": "send_email", "target": "customer@example.com", "parameters": {"body": "one"}})
    data = r.json()
    assert data["decision"] == "ASK"
    assert data["policy_hash"]
    assert data["action_hash"]
    assert data["decision_signature"]
    decision_id = data["decision_id"]
    approved = client.post(f"/v1/action/{decision_id}/approve", json={"approver_id": "human-1", "approved": True, "action_hash": data["action_hash"], "tenant_id": TENANT, "policy_version": data["policy_version"]})
    assert approved.status_code == 200
    replay = client.get(f"/v1/replay/{decision_id}", params={"tenant_id": TENANT}).json()
    assert replay["match"] is True
    assert replay["policy_hash_match"] is True
    assert replay["action_hash_match"] is True


def test_auth_can_be_enabled_fail_closed(monkeypatch):
    monkeypatch.setattr(app, "API_TOKEN", "test-token")
    assert client.post("/v1/action/evaluate", json={"tenant_id": TENANT, "agent_id": "a", "action": "read_file"}).status_code == 401
    assert client.post("/v1/action/evaluate", headers={"Authorization": "Bearer test-token"}, json={"tenant_id": TENANT, "agent_id": "a", "action": "read_file"}).status_code == 200
    monkeypatch.setattr(app, "API_TOKEN", None)


def test_production_without_auth_configuration_fails_closed(monkeypatch):
    monkeypatch.setattr(app, "ENVIRONMENT", "production")
    monkeypatch.setattr(app, "API_TOKEN", None)
    assert client.post("/v1/action/evaluate", json={"tenant_id": TENANT, "agent_id": "a", "action": "read_file"}).status_code == 503
    monkeypatch.setattr(app, "ENVIRONMENT", "development")


def test_action_hash_changes_with_payload():
    a = client.post("/v1/action/evaluate", json={"tenant_id": TENANT, "agent_id": "a", "action": "send_email", "target": "customer@example.com", "parameters": {"body": "one"}}).json()
    b = client.post("/v1/action/evaluate", json={"tenant_id": TENANT, "agent_id": "a", "action": "send_email", "target": "customer@example.com", "parameters": {"body": "two"}}).json()
    assert a["action_hash"] != b["action_hash"]


def test_cross_tenant_evidence_is_not_disclosed():
    data = client.post("/v1/action/evaluate", json={"tenant_id": TENANT, "agent_id": "a", "action": "read_file"}).json()
    assert client.get(f"/v1/evidence/{data['decision_id']}", params={"tenant_id": "tenant-other"}).status_code == 404
