from state_bound.epistemic import issue_authority
from state_bound.models import Decision
from state_bound.oracle import StateOracle
from state_bound.verifier import verify_authority


def fixture():
    oracle = StateOracle(
        {"steps": ["intent", "authorize"], "within_boundary": True},
        {
            "context": {"tenant": "A", "recipient_status": "verified"},
            "state": {"balance": 10000},
            "evidence": {"policy": "P1", "fresh": True},
        },
    )
    snapshot = oracle.latest()
    action = {"type": "transfer", "amount": 1000, "recipient": "B"}
    decision = Decision(
        "ALLOW", "KNOWN", snapshot.version, snapshot.world.trajectory_digest(),
        "stable", snapshot.world.context_digest(), snapshot.world.state_digest(),
        snapshot.world.evidence_digest(),
    )
    authority = issue_authority(
        action=action, subject="A", decision=decision, nonce="trajectory-test",
        issued_at_ns=0, expires_at_ns=10**18,
    )
    assert authority is not None
    return oracle, action, authority


def execute(oracle, action, authority):
    return oracle.execute_if_valid(
        authority=authority, action=action, subject="A", now_ns=1,
        verify=verify_authority, execute=lambda _action, _world: None,
    )


def test_ta001_stable_trajectory_allows():
    oracle, action, authority = fixture()
    assert execute(oracle, action, authority).status == "VALID"


def test_ta002_context_drift_holds_for_re_evaluation():
    oracle, action, authority = fixture()
    oracle.update_context({"tenant": "A", "recipient_status": "changed"})
    result = execute(oracle, action, authority)
    assert result.status == "HOLD"
    assert "context_consistent" in result.reason


def test_ta003_state_drift_becomes_unknown():
    oracle, action, authority = fixture()
    oracle.update_state({"balance": 500})
    result = execute(oracle, action, authority)
    assert result.status == "UNKNOWN"
    assert "state_consistent" in result.reason


def test_ta004_evidence_invalidation_becomes_unknown():
    oracle, action, authority = fixture()
    oracle.update_evidence({"policy": "P1", "fresh": False})
    result = execute(oracle, action, authority)
    assert result.status == "UNKNOWN"
    assert "evidence_consistent" in result.reason


def test_ta005_trajectory_deviation_holds():
    oracle, action, authority = fixture()
    oracle.append({"steps": ["intent", "authorize", "unexpected_action"], "within_boundary": False})
    result = execute(oracle, action, authority)
    assert result.status == "HOLD"
    assert "trajectory_consistent" in result.reason


def test_unknown_decision_cannot_issue_authority():
    oracle, action, _authority = fixture()
    snapshot = oracle.latest()
    decision = Decision("ALLOW", "UNKNOWN", snapshot.version,
                        snapshot.world.trajectory_digest(), "insufficient_evidence")
    assert issue_authority(
        action=action, subject="A", decision=decision, nonce="unknown",
        issued_at_ns=0, expires_at_ns=10**18
    ) is None
