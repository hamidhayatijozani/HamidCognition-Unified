import hashlib
import hmac
import json
import os
import tempfile

os.environ["ACTION_GATE_DB"] = os.path.join(tempfile.gettempdir(), "hamidcognition-enterprise-security.db")
os.environ["ACTION_GATE_ENV"] = "production"
os.environ["ACTION_GATE_API_TOKEN"] = "enterprise-token"
os.environ["ACTION_GATE_SIGNING_SECRET"] = "legacy-secret"
os.environ["ACTION_GATE_APPROVAL_SECRET"] = "approval-secret"
os.environ["ACTION_GATE_REQUIRE_SESSION_BINDING"] = "1"

from fastapi.testclient import TestClient
import app as gate

client = TestClient(gate.app)


def payload(**extra):
    base = {
        "tenant_id": "enterprise-tenant",
        "agent_id": "enterprise-agent",
        "actor_id": "actor-1",
        "session_id": "session-1",
        "action": "read_public_file",
        "target": "/public/info.txt",
        "parameters": {"x": 1},
    }
    base.update(extra)
    return base


def auth():
    return {"Authorization": "Bearer enterprise-token"}


def approval_signature(value):
    unsigned = {k: v for k, v in value.items() if k != "approval_signature"}
    raw = json.dumps(unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hmac.new(b"approval-secret", raw, hashlib.sha256).hexdigest()


def test_production_requires_session_binding():
    r = client.post("/v1/action/evaluate", headers=auth(), json=payload(session_id=None))
    assert r.status_code == 422
    assert r.json()["detail"] == "session_id_required"


def test_execution_cannot_cross_session_boundary():
    r = client.post("/v1/action/evaluate", headers=auth(), json=payload())
    assert r.status_code == 200
    d = r.json()
    wrong = {
        "tenant_id": d["tenant_id"],
        "actor_id": d["actor_id"],
        "session_id": "attacker-session",
        "action_hash": d["action_hash"],
        "nonce": d["nonce"],
    }
    assert client.post(f"/v1/action/{d['decision_id']}/execution/reserve", headers=auth(), json=wrong).status_code == 409


def test_sandbox_is_not_executable():
    r = client.post("/v1/action/evaluate", headers=auth(), json=payload(action="transfer_funds", target="account-1"))
    assert r.status_code == 200
    d = r.json()
    assert d["decision"] == "SANDBOX"
    body = {**{k: d[k] for k in ("tenant_id", "actor_id", "session_id", "action_hash", "nonce")}}
    assert client.post(f"/v1/action/{d['decision_id']}/execution/reserve", headers=auth(), json=body).status_code == 403


def test_production_approval_requires_valid_signature():
    r = client.post("/v1/action/evaluate", headers=auth(), json=payload(action="send_email", target="external"))
    assert r.status_code == 200
    d = r.json()
    approval = {
        "approver_id": "human-1",
        "approved": True,
        "reason": "verified",
        "action_hash": d["action_hash"],
        "tenant_id": d["tenant_id"],
        "policy_version": d["policy_version"],
    }
    bad = client.post(f"/v1/action/{d['decision_id']}/approve", headers=auth(), json=approval)
    assert bad.status_code == 401
    approval["approval_signature"] = approval_signature(approval)
    good = client.post(f"/v1/action/{d['decision_id']}/approve", headers=auth(), json=approval)
    assert good.status_code == 200


def test_signing_key_rotation_verifies_old_decision():
    import canonicalization
    import decision_authority
    old_keys = os.environ.get("ACTION_GATE_SIGNING_KEYS")
    old_key_id = os.environ.get("ACTION_GATE_KEY_ID")
    old_gate_key_id = gate.KEY_ID
    try:
        os.environ["ACTION_GATE_SIGNING_KEYS"] = json.dumps({"key-old": "old-secret", "key-new": "new-secret"})
        os.environ["ACTION_GATE_KEY_ID"] = "key-old"
        canonicalization.KEY_ID = "key-old"
        gate.KEY_ID = "key-old"
        d = client.post("/v1/action/evaluate", headers=auth(), json=payload()).json()
        record = gate.load(d["decision_id"], "enterprise-tenant")
        assert record["key_id"] == "key-old"
        os.environ["ACTION_GATE_KEY_ID"] = "key-new"
        canonicalization.KEY_ID = "key-new"
        gate.KEY_ID = "key-new"
        assert gate.verify_signature(record)
    finally:
        if old_keys is None:
            os.environ.pop("ACTION_GATE_SIGNING_KEYS", None)
        else:
            os.environ["ACTION_GATE_SIGNING_KEYS"] = old_keys
        if old_key_id is None:
            os.environ.pop("ACTION_GATE_KEY_ID", None)
        else:
            os.environ["ACTION_GATE_KEY_ID"] = old_key_id
        canonicalization.KEY_ID = old_key_id or "hhj-csg-1"
        gate.KEY_ID = old_gate_key_id
