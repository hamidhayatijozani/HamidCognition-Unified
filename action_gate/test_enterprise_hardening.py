import json

import pytest

from action_gate_sdk import verify_hmac_attestation
from keyring import configured_key_ids, current_key_id
from policy_store import load_policy, policy_hash


def test_policy_is_versioned_and_hashed():
    policy = load_policy()
    assert policy["policy_version"]
    assert policy_hash(policy)
    assert len(policy_hash(policy)) == 64


def test_default_keyring_has_stable_key_id():
    assert current_key_id()
    assert isinstance(configured_key_ids(), list)


def test_attestation_is_exactly_bound():
    assert verify_hmac_attestation("dec-1", "a" * 64, "b" * 32,
                                   verify_hmac_attestation.__module__ is not None and
                                   __import__("hmac").new(
                                       b"secret", b"dec-1:" + b"a" * 64 + b":" + b"b" * 32,
                                       __import__("hashlib").sha256,
                                   ).hexdigest(),
                                   "secret")
    assert not verify_hmac_attestation("dec-1", "a" * 64, "b" * 32, "0" * 64, "secret")


def test_session_identity_is_part_of_action_binding(client=None):
    from test_action_gate import client as gate_client

    evaluated = gate_client.post("/v1/action/evaluate", json={
        "tenant_id": "session-tenant",
        "agent_id": "agent",
        "actor_id": "actor-a",
        "session_id": "session-a",
        "action": "read_public_file",
    })
    assert evaluated.status_code == 200
    data = evaluated.json()
    wrong = gate_client.post(
        f"/v1/action/{data['decision_id']}/execution/reserve",
        json={
            "tenant_id": "session-tenant",
            "actor_id": "actor-a",
            "session_id": "session-b",
            "action_hash": data["action_hash"],
            "nonce": data["nonce"],
        },
    )
    assert wrong.status_code == 409
    assert wrong.json()["detail"] == "execution_session_binding_mismatch"


def test_sandbox_never_crosses_direct_execution_boundary():
    from test_action_gate import client as gate_client

    evaluated = gate_client.post("/v1/action/evaluate", json={
        "tenant_id": "sandbox-tenant",
        "agent_id": "agent",
        "action": "transfer_funds",
        "target": "account-1",
    })
    data = evaluated.json()
    response = gate_client.post(
        f"/v1/action/{data['decision_id']}/execution",
        json={
            "tenant_id": "sandbox-tenant",
            "action_hash": data["action_hash"],
            "nonce": data["nonce"],
            "outcome": {"attempt": True},
        },
    )
    assert response.status_code == 403


def test_invalid_policy_configuration_fails_closed(monkeypatch):
    monkeypatch.setenv("ACTION_GATE_POLICY_JSON", "{invalid-json")
    with pytest.raises(RuntimeError, match="invalid_action_gate_policy_json"):
        load_policy()


@pytest.mark.parametrize("failure_point", ["risk", "decision"])
def test_policy_evaluation_failure_returns_unavailable_without_persisting(
    monkeypatch, failure_point
):
    from fastapi import HTTPException
    import app as gate_app

    monkeypatch.setattr(gate_app, "ENVIRONMENT", "development")
    monkeypatch.setattr(gate_app, "REQUIRE_SESSION_BINDING", False)
    monkeypatch.setattr(gate_app, "require_auth", lambda authorization: None)
    monkeypatch.setattr(
        gate_app, "enforce_rate_limit", lambda authorization, tenant_id: None
    )

    def fail_policy(*args, **kwargs):
        raise RuntimeError("simulated policy evaluator outage")

    if failure_point == "risk":
        monkeypatch.setattr(gate_app, "evaluate_risk", fail_policy)
    else:
        monkeypatch.setattr(
            gate_app, "evaluate_risk", lambda req: ("LOW", ["test"])
        )
        monkeypatch.setattr(gate_app, "decide", fail_policy)

    saved = []
    monkeypatch.setattr(gate_app, "save", lambda *args, **kwargs: saved.append(args))
    request = gate_app.ActionRequest(
        tenant_id="fail-closed-tenant",
        agent_id="test-agent",
        action="read_public_file",
    )

    with pytest.raises(HTTPException) as error:
        gate_app.evaluate(request, authorization=None)

    assert error.value.status_code == 503
    assert error.value.detail == "policy_evaluation_unavailable"
    assert saved == []
