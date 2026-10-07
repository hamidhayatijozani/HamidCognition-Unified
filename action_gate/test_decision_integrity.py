from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app import ActionRequest, evidence_gate, normalized_action


def test_unknown_evidence_never_passes():
    status, normalized, contradictions = evidence_gate([
        {"key": "host.health", "value": True, "state": "UNKNOWN", "source": "agent"}
    ])
    assert status == "BLOCK"
    assert contradictions == []
    assert normalized[0]["state"] == "UNKNOWN"


def test_stale_evidence_never_passes():
    expired = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
    status, normalized, contradictions = evidence_gate([
        {"key": "host.health", "value": True, "state": "VERIFIED_FACT", "expires_at": expired}
    ])
    assert status == "BLOCK"
    assert normalized[0]["state"] == "STALE"
    assert contradictions == []


def test_conflicting_evidence_is_detected():
    status, normalized, contradictions = evidence_gate([
        {"key": "host.cpu", "value": 8, "state": "OBSERVATION"},
        {"key": "host.cpu", "value": 2, "state": "OBSERVATION"},
    ])
    assert status == "BLOCK"
    assert len(contradictions) == 1
    assert contradictions[0]["key"] == "host.cpu"


def test_verified_evidence_can_pass():
    status, normalized, contradictions = evidence_gate([
        {
            "key": "host.health",
            "value": True,
            "state": "VERIFIED_FACT",
            "source": "attestation",
            "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
        }
    ])
    assert status == "PASS"
    assert normalized[0]["state"] == "VERIFIED_FACT"
    assert contradictions == []


def test_world_version_is_bound_into_request_record():
    req = ActionRequest(
        tenant_id="t",
        agent_id="a",
        actor_id="actor",
        session_id="s",
        action="read_public_file",
        target="local://test",
        world_version="W-1",
    )
    normalized = normalized_action(req)
    assert normalized["pre_execution_signal"]["mode"] == "PROCEED"
