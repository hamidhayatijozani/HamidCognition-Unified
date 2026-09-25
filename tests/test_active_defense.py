from datetime import datetime, timezone
from action_gate.active_defense import classify_enforcement_failure

def test_suspicious_enforcement_failure_creates_signal():
    signal = classify_enforcement_failure(
        error_code="nonce_reuse",
        decision_id="dec-1",
        tenant_id="tenant-a",
        nonce_fingerprint="fp",
        now=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    assert signal is not None
    assert signal.event_type == "SECURITY_SIGNAL_ENFORCEMENT_ANOMALY"
    assert signal.severity == "HIGH"
    assert signal.reason == "nonce_reuse"

def test_normal_policy_failure_does_not_create_active_defense_signal():
    assert classify_enforcement_failure(error_code="decision_not_executable") is None
