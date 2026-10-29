"""Fail-closed regression test for policy-engine failures."""
import os
import tempfile

os.environ.setdefault(
    "ACTION_GATE_DB",
    os.path.join(tempfile.gettempdir(), "action-gate-policy-engine-fail-closed.db"),
)
os.environ.setdefault("ACTION_GATE_ENV", "development")

from fastapi.testclient import TestClient
import app as gate


def test_policy_engine_unavailable_returns_deny_and_blocks_execution(monkeypatch):
    gate.ENVIRONMENT = "development"
    gate.REQUIRE_SESSION_BINDING = False
    client = TestClient(gate.app)

    def unavailable(*_args, **_kwargs):
        raise RuntimeError("simulated policy engine outage")

    monkeypatch.setattr(gate, "decide", unavailable)
    tenant_id = "policy-engine-outage-test"
    response = client.post(
        "/v1/action/evaluate",
        json={
            "tenant_id": tenant_id,
            "agent_id": "test-agent",
            "action": "read_public_file",
            "target": "/public/fixture.txt",
        },
    )

    assert response.status_code == 200, response.text
    decision = response.json()
    assert decision["decision"] == "DENY"
    assert {
        "policy": "policy-engine",
        "result": "DENY",
        "reason": "policy_engine_unavailable",
    } in decision["policy_checks"]

    execution = client.post(
        f"/v1/action/{decision['decision_id']}/execution",
        json={
            "tenant_id": tenant_id,
            "action_hash": decision["action_hash"],
            "nonce": decision["nonce"],
            "outcome": {"test_only": True},
        },
    )
    assert execution.status_code == 403, execution.text
    assert execution.json()["detail"] == "execution_not_permitted_by_gate"
