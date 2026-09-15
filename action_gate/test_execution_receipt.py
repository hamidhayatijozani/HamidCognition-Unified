"""Adversarial tests for Execution Receipt binding and integrity."""
import copy
from datetime import datetime, timezone, timedelta

from execution_receipt import make_receipt, validate_receipt, digest

NOW = datetime(2026, 9, 15, 16, 0, tzinfo=timezone.utc)
START = (NOW - timedelta(seconds=10)).isoformat()
FINISH = NOW.isoformat()
REQUEST = {"action": "send_email", "target": "recipient-A", "parameters": {"body": "controlled"}}
REQUEST_DIGEST = digest(REQUEST)
DECISION_ID = "dec-001"
DECISION_DIGEST = digest({"decision_id": DECISION_ID, "decision": "ALLOW"})
ACTION_HASH = digest({"action": REQUEST["action"], "target": REQUEST["target"], "parameters": REQUEST["parameters"]})
NONCE = "nonce-001"


def receipt():
    return make_receipt(
        request=REQUEST,
        request_digest=REQUEST_DIGEST,
        decision_id=DECISION_ID,
        decision_digest=DECISION_DIGEST,
        action_hash=ACTION_HASH,
        nonce=NONCE,
        executor_id="executor-A",
        started_at=START,
        finished_at=FINISH,
        status="EXECUTED",
        outcome={"provider_status": 200},
    )


def validate(r):
    return validate_receipt(r, request=REQUEST, request_digest=REQUEST_DIGEST,
                            decision_id=DECISION_ID, decision_digest=DECISION_DIGEST,
                            action_hash=ACTION_HASH, nonce=NONCE)


def test_valid_receipt():
    assert validate(receipt()).valid


def test_request_rebinding_fails():
    r = receipt(); r["request_digest"] = digest({"action": "delete_file"})
    assert not validate(r).valid


def test_decision_rebinding_fails():
    r = receipt(); r["decision_id"] = "dec-attacker"
    assert not validate(r).valid


def test_action_rebinding_fails():
    r = receipt(); r["action_hash"] = "0" * 64
    assert not validate(r).valid


def test_nonce_rebinding_fails():
    r = receipt(); r["nonce"] = "attacker-nonce"
    assert not validate(r).valid


def test_tampered_outcome_fails_integrity():
    r = receipt(); r["outcome"]["provider_status"] = 500
    assert not validate(r).valid
    assert "integrity:receipt_digest_mismatch" in validate(r).errors


def test_finished_before_started_fails():
    r = receipt(); r["finished_at"] = (NOW - timedelta(seconds=20)).isoformat()
    # Re-signing is intentionally omitted: both temporal and integrity controls matter.
    assert not validate(r).valid


def test_status_cannot_be_invented():
    r = receipt(); r["status"] = "SUCCESSFUL_IN_THE_REAL_WORLD"
    assert not validate(r).valid


def test_receipt_digest_is_not_a_free_pass():
    r = receipt(); r["executor_id"] = "attacker"; r["receipt_digest"] = digest({k: r[k] for k in r if k != "receipt_digest"})
    assert validate(r).valid is True
    # Executor identity is part of the signed/bound receipt, so changing it alone
    # changes the evidence but does not make it invalid cryptographically. Identity
    # authorization belongs outside this evidence-format boundary.
