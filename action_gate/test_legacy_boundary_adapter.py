import os
import tempfile

os.environ["ACTION_GATE_DB"] = os.path.join(tempfile.gettempdir(), "hamidcognition-action-gate-boundary.db")
os.environ["ACTION_GATE_ENV"] = "development"

from fastapi.testclient import TestClient

import app

client = TestClient(app.app, headers={"Authorization": "Bearer dev-action-gate-token"})
TENANT = "tenant-boundary"


def test_legacy_execution_emits_validation_latch_receipt():
    data = client.post(
        "/v1/action/evaluate",
        json={"tenant_id": TENANT, "agent_id": "a", "action": "read_public_file", "target": "/public/info.txt"},
    ).json()
    response = client.post(
        f"/v1/action/{data['decision_id']}/execution",
        json={
            "tenant_id": TENANT,
            "action_hash": data["action_hash"],
            "nonce": data["nonce"],
            "outcome": {"ok": True},
        },
    )
    assert response.status_code == 200
    record = response.json()
    assert record["execution"]["boundary"] == "validation_latch"
    assert record["execution"]["boundary_version"] == "VB-0.1"
    assert record["execution"]["authorization"]["permitted"] is True
    assert record["execution_receipt"]["status"] == "EXECUTED"
    assert record["execution_receipt"]["request_digest"] == record["execution"]["authorization"]["request_digest"]


def test_legacy_execution_does_not_mutate_on_boundary_rejection():
    data = client.post(
        "/v1/action/evaluate",
        json={"tenant_id": TENANT, "agent_id": "a", "action": "read_public_file", "target": "/public/info.txt"},
    ).json()
    response = client.post(
        f"/v1/action/{data['decision_id']}/execution",
        json={
            "tenant_id": TENANT,
            "action_hash": "tampered",
            "nonce": data["nonce"],
            "outcome": {"should": "not-run"},
        },
    )
    assert response.status_code == 409
    stored = app.load(data["decision_id"], TENANT)
    assert stored["execution"] is None
    assert stored["outcome"] is None
    assert stored["consumed_at"] is None
