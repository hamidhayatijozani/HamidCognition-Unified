import os
import sys

os.environ["ACTION_GATE_DB"] = "/tmp/hamidcognition-pre-execution-signal.db"
os.environ["ACTION_GATE_ENV"] = "development"
os.environ["ACTION_GATE_API_TOKEN"] = "integration-test-token"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "action_gate"))

from fastapi.testclient import TestClient
from app import app
from state_bound.pre_execution_signals import ReactivityFactors, calculate_reactivity

client = TestClient(app)


def test_research_inhibit_is_consumed_by_action_gate():
    result = calculate_reactivity(
        ReactivityFactors(
            activation=1.0,
            inhibition=0.90,
            context_stability=1.0,
            state_stability=1.0,
            evidence_strength=1.0,
            trajectory_stability=1.0,
        )
    )
    assert result.mode == "INHIBIT"
    assert result.consumer_action == "BLOCK_REACTION"

    response = client.post("/v1/action/evaluate", headers={"Authorization": "Bearer integration-test-token"}, json={
        "tenant_id": "signal-tenant",
        "agent_id": "research-agent",
        "actor_id": "research-actor",
        "session_id": "research-session",
        "action": "read_public_file",
        "target": "/public/info.txt",
        "pre_execution_signal": {
            "mode": result.mode,
            "reactivity": result.reactivity,
            "reason": result.reason,
            "consumer_action": result.consumer_action,
        },
    })

    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "DENY"
    assert data["policy_checks"][0]["policy"] == "pre-execution-signal"

    replay = client.get(
        f"/v1/replay/{data['decision_id']}?tenant_id=signal-tenant",
        headers={"Authorization": "Bearer integration-test-token"},
    )
    assert replay.status_code == 200
    assert replay.json()["replayed_decision"] == "DENY"
    assert replay.json()["match"] is True


def test_research_proceed_does_not_bypass_action_gate_policy():
    result = calculate_reactivity(
        ReactivityFactors(
            activation=1.0,
            inhibition=0.0,
            context_stability=1.0,
            state_stability=1.0,
            evidence_strength=1.0,
            trajectory_stability=1.0,
        )
    )
    assert result.mode == "PROCEED"

    response = client.post("/v1/action/evaluate", headers={"Authorization": "Bearer integration-test-token"}, json={
        "tenant_id": "signal-tenant",
        "agent_id": "research-agent",
        "actor_id": "research-actor",
        "session_id": "research-session",
        "action": "delete_file",
        "target": "/production/data.db",
        "pre_execution_signal": {
            "mode": result.mode,
            "reactivity": result.reactivity,
            "reason": result.reason,
            "consumer_action": result.consumer_action,
        },
    })

    assert response.status_code == 200
    assert response.json()["decision"] == "DENY"
