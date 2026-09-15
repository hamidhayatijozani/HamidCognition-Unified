"""Adversarial tests for the Action Gate Validation Boundary.

The tests are negative-control heavy on purpose: a trustworthy boundary must
reject plausible bypasses, not merely accept a happy-path request.
"""
import copy
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from action_gate.validation_boundary import (  # noqa: E402
    digest,
    make_decision,
    validate_decision,
    validate_execution_attempt,
    validate_request,
)

NOW = datetime(2026, 9, 15, 16, 0, tzinfo=timezone.utc)
ISSUED = "2026-09-15T15:59:00+00:00"


def request():
    return {
        "request_id": "req-001",
        "action": "send_email",
        "target": "recipient-A",
        "parameters": {"subject": "test", "body": "controlled"},
        "requester": "agent-A",
        "timestamp": "2026-09-15T15:58:30+00:00",
    }


def evidence():
    return {"state": "PRESENT", "artifact_ref": "evidence/001.json", "sha256": "a" * 64}


def test_request_digest_is_canonical_and_stable():
    a = request()
    b = copy.deepcopy(a)
    b["parameters"] = {"body": "controlled", "subject": "test"}
    assert digest(a) == digest(b)


def test_valid_allow_is_executable():
    r = request()
    d = make_decision(r, "ALLOW", ISSUED, evidence())
    assert validate_request(r).valid
    assert validate_decision(r, d, now=NOW).valid
    assert validate_execution_attempt(r, d, now=NOW).valid


def test_missing_evidence_cannot_allow():
    r = request()
    d = make_decision(r, "ALLOW", ISSUED, {"state": "MISSING"})
    result = validate_execution_attempt(r, d, now=NOW)
    assert not result.valid
    assert "allow:requires_present_evidence" in result.errors


def test_forged_interpretation_or_claim_is_not_an_authorizer():
    r = request()
    d = make_decision(r, "DENY", ISSUED, evidence())
    d["interpretation"] = "SAFE_AND_VERIFIED"
    d["confidence"] = 0.999
    result = validate_execution_attempt(r, d, now=NOW)
    assert not result.valid
    assert any(e.startswith("execution:not_executable_decision") for e in result.errors)


def test_replayed_decision_for_different_request_is_blocked():
    r1 = request()
    d = make_decision(r1, "ALLOW", ISSUED, evidence())
    r2 = copy.deepcopy(r1)
    r2["target"] = "recipient-B"
    result = validate_execution_attempt(r2, d, now=NOW)
    assert not result.valid
    assert "binding:request_digest_mismatch" in result.errors


def test_parameter_mutation_after_validation_is_blocked():
    r = request()
    d = make_decision(r, "ALLOW", ISSUED, evidence())
    r["parameters"]["body"] = "mutated-after-validation"
    result = validate_execution_attempt(r, d, now=NOW)
    assert not result.valid
    assert "binding:request_digest_mismatch" in result.errors


def test_expired_decision_is_blocked():
    r = request()
    issued = (NOW - timedelta(minutes=6)).isoformat()
    d = make_decision(r, "ALLOW", issued, evidence())
    result = validate_execution_attempt(r, d, now=NOW)
    assert not result.valid
    assert "freshness:decision_expired" in result.errors


def test_future_decision_is_blocked():
    r = request()
    issued = (NOW + timedelta(seconds=30)).isoformat()
    d = make_decision(r, "ALLOW", issued, evidence())
    result = validate_execution_attempt(r, d, now=NOW)
    assert not result.valid
    assert "freshness:issued_in_future" in result.errors


def test_deny_ask_defer_never_execute():
    r = request()
    for decision in ("DENY", "ASK", "DEFER"):
        d = make_decision(r, decision, ISSUED, evidence())
        result = validate_execution_attempt(r, d, now=NOW)
        assert not result.valid


def test_sandbox_is_executable_but_remains_bound():
    r = request()
    d = make_decision(r, "SANDBOX", ISSUED, evidence())
    assert validate_execution_attempt(r, d, now=NOW).valid


def test_invalid_evidence_state_is_blocked():
    r = request()
    d = make_decision(r, "ALLOW", ISSUED, {"state": "MAGIC"})
    result = validate_execution_attempt(r, d, now=NOW)
    assert not result.valid
    assert "evidence:invalid_state" in result.errors


def test_changing_decision_label_cannot_repair_bad_binding():
    r = request()
    d = make_decision(r, "DENY", ISSUED, evidence())
    d["request_digest"] = "0" * 64
    d["decision"] = "ALLOW"
    result = validate_execution_attempt(r, d, now=NOW)
    assert not result.valid
    assert "binding:request_digest_mismatch" in result.errors


if __name__ == "__main__":
    import unittest
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    raise SystemExit(0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1)
