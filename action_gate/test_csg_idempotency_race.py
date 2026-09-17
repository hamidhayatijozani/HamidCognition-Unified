from __future__ import annotations

from datetime import datetime, timezone
import json

import csg_ingress
from canonicalization import sha256_digest
from csg_contract import PermissionRequest


def make_request() -> PermissionRequest:
    return PermissionRequest(
        contract_version="hhj-csg/1.0",
        request_id="race-test-001",
        tenant_id="tenant-race",
        agent_id="agent-race",
        actor_id="actor-race",
        action="read_public",
        target="public-resource",
        timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    )


def test_lost_idempotency_race_recovers_committed_winner(monkeypatch):
    request = make_request()
    payload = request.model_dump(mode="json", exclude_none=True)
    request_digest = sha256_digest(payload)

    winner = csg_ingress.build_decision(request, request_digest)
    winner_json = winner.model_dump_json()
    calls = {"load": 0}

    def fake_load(tenant_id, key):
        calls["load"] += 1
        if calls["load"] == 1:
            return None
        return request_digest, winner_json

    monkeypatch.setenv("ACTION_GATE_API_TOKEN", "race-token")
    monkeypatch.setenv("ACTION_GATE_SIGNING_SECRET", "race-secret")
    monkeypatch.setattr(csg_ingress, "load_idempotency", fake_load)
    monkeypatch.setattr(csg_ingress, "save_idempotency", lambda *args: False)
    monkeypatch.setattr(csg_ingress, "validate_timestamp", lambda timestamp: None)
    monkeypatch.setattr(csg_ingress, "verify_request_signature", lambda payload, signature: None)

    result, _ = csg_ingress.decide(
        request,
        "Bearer race-token",
        "race-key",
        "ignored",
        "corr-race",
        raw_payload=payload,
    )

    assert result.decision_id == winner.decision_id
    assert result.decision_digest == winner.decision_digest
    assert calls["load"] == 2
