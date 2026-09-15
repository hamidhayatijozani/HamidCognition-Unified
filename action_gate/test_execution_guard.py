from datetime import datetime, timedelta, timezone

from execution_guard import validate_legacy_execution


def base_record():
    return {
        "decision": "ALLOW",
        "action_hash": "a" * 64,
        "nonce": "n-1",
        "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
        "consumed_at": None,
        "approval": None,
    }


def test_valid_execution_crosses_guard():
    ok, reason = validate_legacy_execution(
        base_record(), action_hash="a" * 64, nonce="n-1", signature_valid=True
    )
    assert ok is True
    assert reason == "validated_execution_guard"


def test_signature_failure_denies_execution():
    ok, reason = validate_legacy_execution(
        base_record(), action_hash="a" * 64, nonce="n-1", signature_valid=False
    )
    assert ok is False
    assert reason == "decision_signature_invalid"


def test_rebinding_and_nonce_reuse_are_denied():
    record = base_record()
    ok, reason = validate_legacy_execution(
        record, action_hash="b" * 64, nonce="n-1", signature_valid=True
    )
    assert (ok, reason) == (False, "execution_action_binding_mismatch")

    ok, reason = validate_legacy_execution(
        record, action_hash="a" * 64, nonce="wrong", signature_valid=True
    )
    assert (ok, reason) == (False, "execution_nonce_mismatch")

    record["consumed_at"] = datetime.now(timezone.utc).isoformat()
    ok, reason = validate_legacy_execution(
        record, action_hash="a" * 64, nonce="n-1", signature_valid=True
    )
    assert (ok, reason) == (False, "decision_nonce_already_consumed")


def test_deny_ask_and_sandbox_rules_are_explicit():
    for decision in ("DENY", "ASK"):
        record = base_record()
        record["decision"] = decision
        ok, reason = validate_legacy_execution(
            record, action_hash="a" * 64, nonce="n-1", signature_valid=True
        )
        assert (ok, reason) == (False, "execution_not_permitted_by_gate")

    record = base_record()
    record["decision"] = "SANDBOX"
    ok, reason = validate_legacy_execution(
        record, action_hash="a" * 64, nonce="n-1", signature_valid=True
    )
    assert ok is True
    assert reason == "validated_execution_guard"


def test_expired_approval_denies_execution():
    record = base_record()
    record["approval"] = {
        "approved": True,
        "expires_at": (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat(),
    }
    ok, reason = validate_legacy_execution(
        record, action_hash="a" * 64, nonce="n-1", signature_valid=True
    )
    assert (ok, reason) == (False, "approval_expired")
