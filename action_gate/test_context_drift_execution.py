from __future__ import annotations

import copy

from fastapi.testclient import TestClient

import app as gate


def test_http_execution_reservation_rejects_stale_world_and_accepts_stable_control(monkeypatch):
    """Exercise the real FastAPI evaluate/reserve routes across a state transition."""
    monkeypatch.setattr(gate, "API_TOKEN", "integration-token")
    monkeypatch.setattr(gate, "ENVIRONMENT", "development")
    monkeypatch.setattr(gate, "REQUIRE_SESSION_BINDING", True)
    monkeypatch.setattr(gate, "SIGNING_SECRET", "integration-signing-secret")

    state = {
        "snapshot_id": "snap-A",
        "world_version": "wv-A",
        "snapshot_hash": "hash-A",
        "snapshot": {"risk_tier": "low"},
        "committed_at": "2026-10-20T00:00:00+00:00",
    }
    records = {}
    reservations = set()

    monkeypatch.setattr(gate, "get_current_snapshot", lambda: copy.deepcopy(state))
    monkeypatch.setattr(
        gate,
        "save",
        lambda record, _event: records.__setitem__(record["decision_id"], record),
    )

    def load_record(decision_id, tenant_id):
        record = records.get(decision_id)
        if record is None or record["tenant_id"] != tenant_id:
            raise gate.HTTPException(404, "evidence_not_found")
        return record

    def reserve_once(decision_id, nonce, _started_at):
        key = (decision_id, nonce)
        if key in reservations:
            return False
        reservations.add(key)
        return True

    monkeypatch.setattr(gate, "load", load_record)
    monkeypatch.setattr(gate, "reserve_execution", reserve_once)

    client = TestClient(gate.app)
    headers = {"Authorization": "Bearer integration-token"}
    request = {
        "tenant_id": "tenant-context-drift",
        "agent_id": "agent-test",
        "actor_id": "actor-test",
        "session_id": "session-test",
        "action": "read_public_file",
        "target": "/public/context.txt",
        "parameters": {"target": "/public/context.txt"},
        "context": {"risk_tier": "low"},
    }

    first = client.post("/v1/action/evaluate", headers=headers, json=request)
    assert first.status_code == 200, first.text
    stale = first.json()
    assert stale["decision"] == "ALLOW"
    assert stale["world_version"] == "wv-A"

    # Context changes after ALLOW. A new context requires a new immutable world_version.
    state.update(
        snapshot_id="snap-B",
        world_version="wv-B",
        snapshot_hash="hash-B",
        snapshot={"risk_tier": "blocked"},
    )
    stale_reservation = client.post(
        f"/v1/action/{stale['decision_id']}/execution/reserve",
        headers=headers,
        json={
            "tenant_id": request["tenant_id"],
            "actor_id": request["actor_id"],
            "session_id": request["session_id"],
            "action_hash": stale["action_hash"],
            "nonce": stale["nonce"],
            "world_version": "wv-A",
        },
    )
    assert stale_reservation.status_code == 409
    assert stale_reservation.json()["detail"] == "execution_world_state_changed"
    assert not any(decision_id == stale["decision_id"] for decision_id, _ in reservations)

    # Negative control: a fresh decision under the current world can be reserved once.
    current = client.post("/v1/action/evaluate", headers=headers, json=request)
    assert current.status_code == 200, current.text
    fresh = current.json()
    assert fresh["decision"] == "ALLOW"
    assert fresh["world_version"] == "wv-B"

    valid_reservation = client.post(
        f"/v1/action/{fresh['decision_id']}/execution/reserve",
        headers=headers,
        json={
            "tenant_id": request["tenant_id"],
            "actor_id": request["actor_id"],
            "session_id": request["session_id"],
            "action_hash": fresh["action_hash"],
            "nonce": fresh["nonce"],
            "world_version": "wv-B",
        },
    )
    assert valid_reservation.status_code == 200, valid_reservation.text
    assert valid_reservation.json()["execution"]["status"] == "RESERVED"
    assert valid_reservation.json()["execution_authority"]
