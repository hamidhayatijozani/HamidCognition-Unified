from __future__ import annotations

import hashlib
import hmac
import os
from datetime import datetime, timezone

os.environ.setdefault("ACTION_GATE_API_TOKEN", "ci-csg-token")
os.environ.setdefault("ACTION_GATE_SIGNING_SECRET", "ci-csg-secret")
os.environ.setdefault("ACTION_GATE_ENV", "test")

from fastapi.testclient import TestClient

from app import app
from canonicalization import canonicalize


def sign(payload: dict) -> str:
    return hmac.new(os.environ["ACTION_GATE_SIGNING_SECRET"].encode(), canonicalize(payload), hashlib.sha256).hexdigest()


def payload(request_id="evt-001", action="read_public"):
    return {
        "contract_version": "hhj-csg/1.0", "request_id": request_id, "tenant_id": "tenant-a", "agent_id": "agentrq-poc",
        "actor_id": "actor-1", "session_id": "session-1", "action": action, "target": "public-resource",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "parameters": {"limit": 10}, "context": {"source": "simulator"},
    }


def test_contract_first_allow_and_idempotency():
    client = TestClient(app)
    body = payload()
    headers = {"Authorization": "Bearer ci-csg-token", "Idempotency-Key": "evt-001", "X-HCJ-Request-Signature": sign(body)}
    first = client.post("/v1/csg/decide", json=body, headers=headers)
    second = client.post("/v1/csg/decide", json=body, headers=headers)
    assert first.status_code == 200, first.text
    assert second.status_code == 200, second.text
    assert first.json()["decision"] == "ALLOW"
    assert first.json()["decision_id"] == second.json()["decision_id"]
    assert first.json()["request_digest"] == second.json()["request_digest"]


def test_idempotency_rejects_changed_request():
    client = TestClient(app)
    body = payload("evt-002")
    headers = {"Authorization": "Bearer ci-csg-token", "Idempotency-Key": "evt-002", "X-HCJ-Request-Signature": sign(body)}
    assert client.post("/v1/csg/decide", json=body, headers=headers).status_code == 200
    changed = dict(body)
    changed["parameters"] = {"limit": 99}
    changed_headers = dict(headers)
    changed_headers["X-HCJ-Request-Signature"] = sign(changed)
    response = client.post("/v1/csg/decide", json=changed, headers=changed_headers)
    assert response.status_code == 409
    assert response.json()["detail"] == "idempotency_key_reused_for_different_request"


def test_signature_failure_is_rejected():
    client = TestClient(app)
    body = payload("evt-003")
    response = client.post("/v1/csg/decide", json=body, headers={"Authorization": "Bearer ci-csg-token", "Idempotency-Key": "evt-003", "X-HCJ-Request-Signature": "0" * 64})
    assert response.status_code == 401
    assert response.json()["detail"] == "request_signature_invalid"


def test_risk_decisions_are_deterministic_and_fail_closed():
    client = TestClient(app)
    cases = [("transfer_funds", "SANDBOX"), ("delete_database", "DENY"), ("send_email", "ASK"), ("read_public", "ALLOW")]
    for index, (action, expected) in enumerate(cases, start=10):
        body = payload(f"evt-{index}", action)
        if action == "delete_database": body["target"] = "production-db"
        headers = {"Authorization": "Bearer ci-csg-token", "Idempotency-Key": body["request_id"], "X-HCJ-Request-Signature": sign(body)}
        response = client.post("/v1/csg/decide", json=body, headers=headers)
        assert response.status_code == 200, response.text
        assert response.json()["decision"] == expected
        assert response.json()["request_digest"] == hashlib.sha256(canonicalize(body)).hexdigest()
        assert len(response.json()["decision_digest"]) == 64
        assert response.json()["signature_algorithm"] == "HMAC-SHA256"


def test_malformed_contract_is_rejected_with_correlation_id():
    client = TestClient(app)
    body = payload("evt-malformed")
    body.pop("contract_version")
    response = client.post("/v1/csg/decide", json=body, headers={"Authorization": "Bearer ci-csg-token", "Idempotency-Key": "evt-malformed", "X-Correlation-ID": "corr-malformed"})
    assert response.status_code == 422
    assert response.json() == {"detail": "schema_validation_failed", "correlation_id": "corr-malformed"}


def test_invalid_json_is_rejected_with_correlation_id():
    client = TestClient(app)
    response = client.post("/v1/csg/decide", content=b"{not-json", headers={"Authorization": "Bearer ci-csg-token", "Idempotency-Key": "evt-invalid-json", "X-Correlation-ID": "corr-invalid-json", "Content-Type": "application/json"})
    assert response.status_code == 400
    assert response.json() == {"detail": "invalid_json", "correlation_id": "corr-invalid-json"}
