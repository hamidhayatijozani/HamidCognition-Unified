import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from z_freeze_lock import evaluate, Decision, TruthState

def cmd(**overrides):
    x = {
        "action": "AUDIT_DEEP",
        "payload": {},
        "signer": "HAMID-ALPHA",
        "moduleId": "test-module",
        "requestId": "req-001",
    }
    x.update(overrides)
    return x

def test_valid_command_is_simulated_not_claimed_enforced():
    r = evaluate(cmd())
    assert r.decision == Decision.ALLOW
    assert r.truth_state == TruthState.SIMULATED

def test_invalid_signer_is_denied():
    assert evaluate(cmd(signer="OTHER")).decision == Decision.DENY

def test_unknown_action_is_denied():
    assert evaluate(cmd(action="UNKNOWN")).decision == Decision.DENY

def test_failed_simulation_never_executes():
    r = evaluate(cmd(), simulation_ok=False)
    assert r.decision == Decision.DENY
    assert r.reason == "simulation_failed"

def test_runtime_can_explicitly_declare_enforced():
    r = evaluate(cmd(), runtime_enforced=True)
    assert r.truth_state == TruthState.ENFORCED
