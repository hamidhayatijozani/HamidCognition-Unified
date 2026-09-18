import hashlib
import json
import os
import tempfile

os.environ["ACTION_GATE_DB"] = os.path.join(tempfile.gettempdir(), "hamidcognition-vb-conformance.db")
os.environ["ACTION_GATE_ENV"] = "development"

from fastapi.testclient import TestClient
import app as gate

client = TestClient(gate.app)
TENANT = "vb-tenant-a"
OTHER_TENANT = "vb-tenant-b"


def evaluate(action="read_public_file", target="/public/info.txt", **extra):
    payload = {"tenant_id": TENANT, "agent_id": "vb-agent", "actor_id": "vb-actor", "action": action, "target": target, **extra}
    response = client.post("/v1/action/evaluate", json=payload)
    assert response.status_code == 200
    return response.json()


def execute(data, tenant=TENANT, action_hash=None, nonce=None, outcome=None):
    reserve = client.post(f"/v1/action/{data['decision_id']}/execution/reserve", json={"tenant_id": tenant, "actor_id": data.get("actor_id"), "action_hash": action_hash or data["action_hash"], "nonce": nonce or data["nonce"]})
    if reserve.status_code != 200:
        return reserve
    return client.post(
        f"/v1/action/{data['decision_id']}/execution",
        json={
            "tenant_id": tenant,
            "actor_id": data.get("actor_id"),
            "action_hash": action_hash or data["action_hash"],
            "nonce": nonce or data["nonce"],
            "outcome": outcome or {"ok": True},
        },
    )


def test_vb01_canonical_action_binding_is_stable():
    data = evaluate(parameters={"b": 2, "a": 1})
    expected = gate.digest(gate.normalized_action(gate.ActionRequest.model_validate({"tenant_id": TENANT, "agent_id": "vb-agent", "actor_id": "vb-actor", "action": "read_public_file", "target": "/public/info.txt", "parameters": {"a": 1, "b": 2}})))
    assert data["action_hash"] == expected


def test_vb02_decision_integrity_signature_verifies():
    data = evaluate()
    record = gate.load(data["decision_id"], TENANT)
    assert gate.verify_signature(record)


def test_vb03_complete_mediation_denied_action_never_executes():
    data = evaluate("delete_file", "/production/data.db")
    assert data["decision"] == "DENY"
    assert execute(data).status_code == 403


def test_vb04_tenant_isolation_hides_evidence():
    data = evaluate()
    response = client.get(f"/v1/evidence/{data['decision_id']}?tenant_id={OTHER_TENANT}")
    assert response.status_code == 404


def test_vb05_actor_binding_is_recorded_in_evidence():
    data = evaluate()
    evidence = client.get(f"/v1/evidence/{data['decision_id']}?tenant_id={TENANT}").json()
    assert evidence["identity"]["actor_id"] == "vb-actor"


def test_vb06_one_time_execution_nonce_is_consumed():
    data = evaluate()
    assert execute(data).status_code == 200
    assert execute(data).status_code == 409


def test_vb07_attestation_signature_tampering_is_detected():
    data = evaluate()
    record = gate.load(data["decision_id"], TENANT)
    record["action_hash"] = "tampered"
    assert not gate.verify_signature(record)


def test_vb08_production_authentication_fails_closed():
    old_env, old_token = gate.ENVIRONMENT, gate.API_TOKEN
    gate.ENVIRONMENT, gate.API_TOKEN = "production", None
    try:
        response = client.post("/v1/action/evaluate", json={"tenant_id": TENANT, "agent_id": "a", "action": "read_public_file"})
        assert response.status_code == 503
    finally:
        gate.ENVIRONMENT, gate.API_TOKEN = old_env, old_token


def test_vb09_evidence_continuity_survives_execution():
    data = evaluate()
    assert execute(data).status_code == 200
    evidence = client.get(f"/v1/evidence/{data['decision_id']}?tenant_id={TENANT}").json()
    assert evidence["execution"]["status"] == "EXECUTED"
    assert evidence["outcome"]["ok"] is True
    assert evidence["evidence_hash"]


def test_vb10_replay_reconstructs_decision_without_side_effect():
    data = evaluate()
    before = gate.load(data["decision_id"], TENANT)["consumed_at"]
    replay = client.get(f"/v1/replay/{data['decision_id']}?tenant_id={TENANT}")
    after = gate.load(data["decision_id"], TENANT)["consumed_at"]
    assert replay.status_code == 200
    assert replay.json()["match"] is True
    assert before == after is None


def test_vb11_policy_snapshot_hash_is_immutable_in_record():
    data = evaluate()
    evidence = client.get(f"/v1/evidence/{data['decision_id']}?tenant_id={TENANT}").json()
    expected = hashlib.sha256(json.dumps(evidence["policy_snapshot"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert evidence["policy_hash"] == expected


def test_vb12_persistence_record_is_loadable_and_audited():
    data = evaluate()
    record = gate.load(data["decision_id"], TENANT)
    assert record["audit_event_hash"]
    assert record["evidence_hash"]


def test_adversarial_actor_change_cannot_redeem_authority():
    data = evaluate()
    wrong_actor = client.post(f"/v1/action/{data['decision_id']}/execution/reserve", json={"tenant_id": TENANT, "actor_id": "attacker", "action_hash": data["action_hash"], "nonce": data["nonce"]})
    assert wrong_actor.status_code == 409


def test_adversarial_parameter_change_changes_authority():
    data = evaluate(parameters={"amount": 10})
    request = gate.ActionRequest.model_validate({"tenant_id": TENANT, "agent_id": "vb-agent", "actor_id": "vb-actor", "action": "read_public_file", "target": "/public/info.txt", "parameters": {"amount": 11}})
    changed_hash = gate.digest(gate.normalized_action(request))
    assert changed_hash != data["action_hash"]
    assert execute(data, action_hash=changed_hash).status_code == 409


def test_adversarial_expired_decision_is_rejected():
    data = evaluate()
    record = gate.load(data["decision_id"], TENANT)
    record["expires_at"] = "2000-01-01T00:00:00+00:00"
    record["decision_signature"] = gate.sign({"decision_id": record["decision_id"], "tenant_id": record["tenant_id"], "action_hash": record["action_hash"], "policy_hash": record["policy_hash"], "nonce": record["nonce"], "expires_at": record["expires_at"]})
    record["evidence_hash"] = gate.digest(record)
    gate.save(record, "TEST_EXPIRE")
    assert execute(data).status_code == 403


def test_approval_is_bound_to_exact_action_and_policy():
    data = evaluate("send_email", "customer@example.com")
    wrong = client.post(f"/v1/action/{data['decision_id']}/approve", json={"approver_id": "human", "approved": True, "action_hash": "wrong", "tenant_id": TENANT, "policy_version": data["policy_version"]})
    assert wrong.status_code == 409
    correct = client.post(f"/v1/action/{data['decision_id']}/approve", json={"approver_id": "human", "approved": True, "action_hash": data["action_hash"], "tenant_id": TENANT, "policy_version": data["policy_version"]})
    assert correct.status_code == 200
    assert correct.json()["decision"] == "ALLOW"


def test_sandbox_cannot_cross_production_execution_boundary():
    data = evaluate("transfer_funds", "account-1", parameters={"amount": 1000})
    assert data["decision"] == "SANDBOX"
    response = client.post(f"/v1/action/{data["decision_id"]}/execution/reserve", json={"tenant_id": TENANT, "actor_id": data.get("actor_id"), "action_hash": data["action_hash"], "nonce": data["nonce"]})
    assert response.status_code == 403


def test_sandbox_is_not_allow_for_critical_financial_action():
    data = evaluate("transfer_funds", "account-1", parameters={"amount": 1000})
    assert data["decision"] == "SANDBOX"


def test_low_risk_hint_cannot_override_intrinsic_criticality():
    data = evaluate("delete_database", "/prod/db", risk_hint="low")
    assert data["risk_assessment"]["level"] == "CRITICAL"
    assert data["decision"] == "DENY"
