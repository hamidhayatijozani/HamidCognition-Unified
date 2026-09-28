from state_bound.epistemic import issue_authority
from state_bound.models import Decision, WorldState
from state_bound.verifier import consume_if_valid


def world():
    return WorldState(
        context={"account": "A"},
        state={"balance": 10000},
        evidence=[{"source": "ledger", "fresh": True}],
        trajectory={"spent_today": 0, "limit": 2000},
        environment={"region": "EU", "mode": "production"},
        policy={"version": "P1", "max_transfer": 1000},
    )


def decision(w):
    return Decision("ALLOW", "KNOWN", w, "stable")


def authority():
    w = world()
    return issue_authority(action={"type": "transfer", "amount": 1000}, world=w,
                           decision=decision(w), nonce="n1")


def test_ta001_stable_trajectory_executes():
    a = authority()
    result = consume_if_valid(a, action=a.action, current_world=world(), consumed_nonces=set())
    assert result.status == "VALID"


def test_ta002_context_drift_invalidates():
    a = authority()
    w = world()
    w = WorldState({"account": "B"}, w.state, w.evidence, w.trajectory, w.environment, w.policy)
    result = consume_if_valid(a, action=a.action, current_world=w, consumed_nonces=set())
    assert "context_invariant_failed" in result.reasons


def test_ta003_state_drift_invalidates():
    a = authority()
    w = world()
    w = WorldState(w.context, {"balance": 8500}, w.evidence, w.trajectory, w.environment, w.policy)
    result = consume_if_valid(a, action=a.action, current_world=w, consumed_nonces=set())
    assert "state_invariant_failed" in result.reasons


def test_ta004_evidence_invalidation():
    a = authority()
    w = world()
    w = WorldState(w.context, w.state, [{"source": "ledger", "fresh": False}], w.trajectory, w.environment, w.policy)
    result = consume_if_valid(a, action=a.action, current_world=w, consumed_nonces=set())
    assert "evidence_invariant_failed" in result.reasons


def test_ta005_trajectory_violation():
    a = authority()
    w = world()
    w = WorldState(w.context, w.state, w.evidence, {"spent_today": 1500, "limit": 2000}, w.environment, w.policy)
    result = consume_if_valid(a, action=a.action, current_world=w, consumed_nonces=set())
    assert "trajectory_invariant_failed" in result.reasons


def test_ta006_policy_drift():
    a = authority()
    w = world()
    w = WorldState(w.context, w.state, w.evidence, w.trajectory, w.environment, {"version": "P2", "max_transfer": 1000})
    result = consume_if_valid(a, action=a.action, current_world=w, consumed_nonces=set())
    assert "policy_invariant_failed" in result.reasons


def test_ta007_identical_payload_is_not_enough():
    a = authority()
    w = world()
    w = WorldState(w.context, {"balance": 9000}, w.evidence, w.trajectory, w.environment, w.policy)
    result = consume_if_valid(a, action=a.action, current_world=w, consumed_nonces=set())
    assert result.status == "INVALID"


def test_ta008_replay_is_rejected():
    a = authority()
    consumed = {"n1"}
    result = consume_if_valid(a, action=a.action, current_world=world(), consumed_nonces=consumed)
    assert "replay_detected" in result.reasons


def test_ta009_unknown_never_issues_authority():
    w = world()
    d = Decision("HOLD", "UNKNOWN", w, "trajectory_state_changed")
    a = issue_authority(action={"type": "transfer", "amount": 1000}, world=w,
                        decision=d, nonce="n-unknown")
    assert a is None
