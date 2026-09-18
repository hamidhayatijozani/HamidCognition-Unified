import hashlib
import hmac
import json
import os
import tempfile

import pytest

os.environ["ACTION_GATE_DB"] = os.path.join(tempfile.gettempdir(), "hamidcognition-action-gate-final.db")
os.environ.setdefault("ACTION_GATE_API_TOKEN", "ci-csg-token")
os.environ.setdefault("ACTION_GATE_SIGNING_SECRET", "ci-csg-secret")
os.environ.setdefault("ACTION_GATE_ENV", "development")

from fastapi.testclient import TestClient
import app as gate


client = TestClient(gate.app)


@pytest.fixture(autouse=True)
def production_runtime():
    old = (gate.ENVIRONMENT, gate.API_TOKEN, gate.SIGNING_SECRET, gate.APPROVAL_SECRET, gate.REQUIRE_SESSION_BINDING)
    gate.ENVIRONMENT = "production"
    gate.API_TOKEN = "final-token"
    gate.SIGNING_SECRET = "final-signing-secret"
    gate.APPROVAL_SECRET = "final-approval-secret"
    gate.REQUIRE_SESSION_BINDING = True
    yield
    gate.ENVIRONMENT, gate.API_TOKEN, gate.SIGNING_SECRET, gate.APPROVAL_SECRET, gate.REQUIRE_SESSION_BINDING = old


def request_payload(**extra):
    value = {
        "tenant_id": "final-tenant",
        "agent_id": "final-agent",
        "actor_id": "final-actor",
        "session_id": "final-session",
        "action": "read_public_file",
        "target": "/public/info.txt",
        "parameters": {"proof": 1},
    }
    value.update(extra)
    return value


def headers():
    return {"Authorization": "Bearer final-token"}


def sign_approval(value):
    raw = json.dumps({k: v for k, v in value.items() if k != "approval_signature"}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hmac.new(b"final-approval-secret", raw, hashlib.sha256).hexdigest()


def test_production_requires_actor_and_session():
    no_actor = dict(request_payload(actor_id=None))
    assert client.post("/v1/action/evaluate", headers=headers(), json=no_actor).status_code == 422
    no_session = dict(request_payload(session_id=None))
    assert client.post("/v1/action/evaluate", headers=headers(), json=no_session).status_code == 422


def test_session_is_returned_and_cannot_be_substituted():
    response = client.post("/v1/action/evaluate", headers=headers(), json=request_payload())
    assert response.status_code == 200
    decision = response.json()
    assert decision["session_id"] == "final-session"
    body = {
        "tenant_id": decision["tenant_id"],
        "actor_id": decision["actor_id"],
        "session_id": "different-session",
        "action_hash": decision["action_hash"],
        "nonce": decision["nonce"],
    }
    assert client.post(f"/v1/action/{decision['decision_id']}/execution/reserve", headers=headers(), json=body).status_code == 409


def test_sandbox_never_becomes_executable():
    response = client.post("/v1/action/evaluate", headers=headers(), json=request_payload(action="transfer_funds", target="account-1"))
    assert response.status_code == 200
    decision = response.json()
    assert decision["decision"] == "SANDBOX"
    body = {k: decision[k] for k in ("tenant_id", "actor_id", "session_id", "action_hash", "nonce")}
    assert client.post(f"/v1/action/{decision['decision_id']}/execution/reserve", headers=headers(), json=body).status_code == 403


def test_approval_requires_signature_in_production():
    response = client.post("/v1/action/evaluate", headers=headers(), json=request_payload(action="send_email", target="external"))
    assert response.status_code == 200
    decision = response.json()
    approval = {
        "approver_id": "human-1",
        "approved": True,
        "reason": "approved",
        "action_hash": decision["action_hash"],
        "tenant_id": decision["tenant_id"],
        "policy_version": decision["policy_version"],
    }
    assert client.post(f"/v1/action/{decision['decision_id']}/approve", headers=headers(), json=approval).status_code == 401
    approval["approval_signature"] = sign_approval(approval)
    approved = client.post(f"/v1/action/{decision['decision_id']}/approve", headers=headers(), json=approval)
    assert approved.status_code == 200
    assert approved.json()["decision"] == "ALLOW"


def test_approval_signature_is_bound_to_policy_and_action():
    response = client.post("/v1/action/evaluate", headers=headers(), json=request_payload(action="send_email", target="external"))
    decision = response.json()
    approval = {
        "approver_id": "human-1",
        "approved": True,
        "reason": "approved",
        "action_hash": decision["action_hash"],
        "tenant_id": decision["tenant_id"],
        "policy_version": decision["policy_version"],
    }
    approval["approval_signature"] = sign_approval(approval)
    approval["action_hash"] = "0" * 64
    assert client.post(f"/v1/action/{decision['decision_id']}/approve", headers=headers(), json=approval).status_code == 409
