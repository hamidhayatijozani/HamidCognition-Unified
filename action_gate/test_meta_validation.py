from fastapi.testclient import TestClient
import app as gate

client = TestClient(gate.app)
TENANT = "meta-tenant"
ACTOR = "meta-actor"
SESSION = "meta-session"


def audit(**overrides):
    payload = {
        "tenant_id": TENANT,
        "actor_id": ACTOR,
        "session_id": SESSION,
        "action": "report_release_status",
        "claim": "release version verified",
        "evidence": [{"source": "VERSION", "verified": True, "supports": ["release", "version", "verified"]}],
    }
    payload.update(overrides)
    return client.post("/v1/self-audit", json=payload)


def test_meta_validation_verified_claim_allows():
    response = audit()
    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "ALLOW"
    assert body["executable"] is True


def test_meta_validation_internal_claim_denies():
    response = audit(requires_model_internal_access=True)
    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "DENY"
    assert body["executable"] is False
    assert "model_internal_state_not_observable" in body["reasons"]


def test_meta_validation_unverified_side_effect_requires_review():
    response = audit(evidence=[], external_side_effect=True)
    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "ASK"
    assert body["executable"] is False


def test_meta_validation_unverified_non_mutating_claim_defers():
    response = audit(evidence=[])
    assert response.status_code == 200
    assert response.json()["decision"] == "DEFER"


def test_meta_validation_identity_is_mandatory():
    response = audit(actor_id="")
    assert response.status_code == 200
    assert response.json()["decision"] == "DENY"


def test_meta_validation_is_deterministic_for_same_request():
    first = audit().json()
    second = audit().json()
    assert first == second
