import os
import sys

os.environ["ACTION_GATE_DB"] = "/tmp/hamidcognition-pre-execution-signal-v31.db"
os.environ["ACTION_GATE_ENV"] = "development"
os.environ["ACTION_GATE_API_TOKEN"] = "integration-test-token"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "action_gate"))

from fastapi.testclient import TestClient

import app as gate
from app import app


gate.API_TOKEN = "integration-test-token"
client = TestClient(app)


def headers():
    return {"Authorization": "Bearer integration-test-token"}


def test_client_cannot_send_signal():
    response = client.post(
        "/v1/action/evaluate",
        headers=headers(),
        json={
            "tenant_id": "t1",
            "agent_id": "a1",
            "action": "read_file",
            "target": "/tmp/x",
            "pre_execution_signal": {
                "mode": "PROCEED",
                "reactivity": 0.1,
                "reason": "client supplied",
                "consumer_action": "REQUEST_ACTION_GATE_AUTHORIZATION",
            },
        },
    )
    assert response.status_code == 422


def test_critical_action_denies_without_client_signal():
    response = client.post(
        "/v1/action/evaluate",
        headers=headers(),
        json={
            "tenant_id": "t1",
            "agent_id": "a1",
            "action": "financial_transfer",
            "target": "acct-1",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "DENY"
    assert body["policy_checks"][0]["signal_mode"] == "INHIBIT"


def test_replay_reconstructs_recorded_signal_and_matches_recomputed_signal():
    response = client.post(
        "/v1/action/evaluate",
        headers=headers(),
        json={
            "tenant_id": "t1",
            "agent_id": "a1",
            "action": "financial_transfer",
            "target": "acct-1",
        },
    )
    assert response.status_code == 200
    body = response.json()

    evidence = client.get(
        f"/v1/evidence/{body['decision_id']}?tenant_id=t1",
        headers=headers(),
    )
    assert evidence.status_code == 200
    record = evidence.json()

    req = gate.ActionRequest.model_validate(record["request"])
    recomputed = gate.compute_signal(req, record["risk_assessment"]["level"], record["policy_snapshot"])
    assert record["pre_execution_signal"] == recomputed.model_dump()

    replay = client.get(
        f"/v1/replay/{body['decision_id']}?tenant_id=t1",
        headers=headers(),
    )
    assert replay.status_code == 200
    replay_body = replay.json()
    assert replay_body["replayed_decision"] == body["decision"]
    assert replay_body["match"] is True
