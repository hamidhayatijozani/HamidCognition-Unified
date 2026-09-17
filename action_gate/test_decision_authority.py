from __future__ import annotations

from datetime import datetime, timezone

import pytest

from canonicalization import sha256_digest
from csg_contract import PermissionRequest
from csg_ingress import build_decision
from decision_authority import DecisionAuthorityError, verify_decision_authority


def make_request(now: datetime) -> PermissionRequest:
    return PermissionRequest(
        contract_version="hhj-csg/1.0",
        request_id="auth-001",
        tenant_id="tenant-a",
        agent_id="agent-a",
        actor_id="actor-a",
        action="send_email",
        target="external-recipient",
        timestamp=now.isoformat().replace("+00:00", "Z"),
        parameters={"subject": "test"},
        context={"source": "authority-test"},
    )


def test_valid_decision_is_bound_to_exact_request(monkeypatch):
    monkeypatch.setenv("ACTION_GATE_SIGNING_SECRET", "test-secret")
    now = datetime.now(timezone.utc)
    request = make_request(now)
    payload = request.model_dump(mode="json", exclude_none=True)
    decision = build_decision(request, sha256_digest(payload))

    verify_decision_authority(decision, payload, now=now)


def test_request_parameter_tampering_invalidates_authority(monkeypatch):
    monkeypatch.setenv("ACTION_GATE_SIGNING_SECRET", "test-secret")
    now = datetime.now(timezone.utc)
    request = make_request(now)
    payload = request.model_dump(mode="json", exclude_none=True)
    decision = build_decision(request, sha256_digest(payload))
    tampered = dict(payload)
    tampered["parameters"] = {"subject": "tampered"}

    with pytest.raises(DecisionAuthorityError, match="request_digest_mismatch"):
        verify_decision_authority(decision, tampered, now=now)


def test_decision_digest_tampering_is_rejected(monkeypatch):
    monkeypatch.setenv("ACTION_GATE_SIGNING_SECRET", "test-secret")
    now = datetime.now(timezone.utc)
    request = make_request(now)
    payload = request.model_dump(mode="json", exclude_none=True)
    decision = build_decision(request, sha256_digest(payload))
    tampered = decision.model_copy(update={"decision": "ALLOW"})

    with pytest.raises(DecisionAuthorityError, match="decision_digest_invalid"):
        verify_decision_authority(tampered, payload, now=now)


def test_signature_tampering_is_rejected(monkeypatch):
    monkeypatch.setenv("ACTION_GATE_SIGNING_SECRET", "test-secret")
    now = datetime.now(timezone.utc)
    request = make_request(now)
    payload = request.model_dump(mode="json", exclude_none=True)
    decision = build_decision(request, sha256_digest(payload))
    tampered = decision.model_copy(update={"signature": "0" * 64})

    with pytest.raises(DecisionAuthorityError, match="decision_signature_invalid"):
        verify_decision_authority(tampered, payload, now=now)


def test_expired_decision_cannot_authorize_execution_but_can_be_replayed(monkeypatch):
    monkeypatch.setenv("ACTION_GATE_SIGNING_SECRET", "test-secret")
    issued = datetime.now(timezone.utc)
    request = make_request(issued)
    payload = request.model_dump(mode="json", exclude_none=True)
    decision = build_decision(request, sha256_digest(payload))
    future = decision.expires_at.replace(microsecond=0) + __import__("datetime").timedelta(seconds=1)

    with pytest.raises(DecisionAuthorityError, match="decision_expired"):
        verify_decision_authority(decision, payload, now=future)

    verify_decision_authority(decision, payload, now=future, require_unexpired=False)
