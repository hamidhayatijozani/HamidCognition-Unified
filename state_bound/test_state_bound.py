from .benchmark import baseline_action_authorization, build_stable_fixture, run_ta001
from .epistemic import issue_authority
from .models import Decision
from .oracle import StateOracle
from .semantics import equivalent_request
from .verifier import verify_authority

def test_ta001_baseline_and_experimental_both_allow():
    action, world, authority = build_stable_fixture()
    assert baseline_action_authorization(action, action) == "ALLOW"
    oracle = StateOracle({"steps": ["intent", "authorize"], "within_boundary": True},
                         {"source": "test"})
    result = oracle.execute_if_valid(authority=authority, action=action,
                                     subject="account-A", now_ns=1,
                                     verify=verify_authority,
                                     execute=lambda _a, _w: None)
    assert result.status == "VALID"
    benchmark = run_ta001(iterations=100)
    assert benchmark["false_deny"] == 0
    assert benchmark["false_allow"] == 0
    assert benchmark["replay_equivalence"] == 1
    assert benchmark["experimental"]["p95_us"] >= benchmark["experimental"]["median_us"]

def test_ta001_uses_latest_committed_snapshot():
    action, _world, authority = build_stable_fixture()
    oracle = StateOracle({"steps": ["intent", "authorize"], "within_boundary": True},
                         {"source": "test"})
    oracle.append({"steps": ["intent", "authorize", "execute"], "within_boundary": True})
    result = oracle.execute_if_valid(authority=authority, action=action,
                                     subject="account-A", now_ns=1,
                                     verify=verify_authority,
                                     execute=lambda _a, _w: None)
    assert result.status == "INVALID"
    assert "trajectory_consistent" in result.reason

def test_ta001_expired_authority_is_rejected():
    action, _world, authority = build_stable_fixture()
    oracle = StateOracle({"steps": ["intent", "authorize"], "within_boundary": True},
                         {"source": "test"})
    result = oracle.execute_if_valid(authority=authority, action=action,
                                     subject="account-A", now_ns=10**18,
                                     verify=verify_authority,
                                     execute=lambda _a, _w: None)
    assert result.status == "INVALID"
    assert "authority_not_expired" in result.reason

def test_replay_equivalence_is_explicit_and_excludes_context():
    action = {"type": "transfer", "amount": 1000, "recipient": "B"}
    assert equivalent_request(
        {"action": action, "world_version": 1, "epistemic_state": "KNOWN"},
        {"action": dict(action), "world_version": 2, "epistemic_state": "STALE"})
    assert not equivalent_request(
        {"action": action, "world_version": 1, "epistemic_state": "KNOWN"},
        {"action": {**action, "amount": 900}, "world_version": 1,
         "epistemic_state": "KNOWN"})

def test_unknown_cannot_issue_authority():
    action, world, _authority = build_stable_fixture()
    decision = Decision("ALLOW", "UNKNOWN", world.version,
                        world.trajectory_digest(), "unknown")
    assert issue_authority(action=action, subject="account-A", decision=decision,
                           nonce="unknown", issued_at_ns=0,
                           expires_at_ns=10**18) is None


def test_context_drift_after_authorization_blocks_execution():
    action = {"type": "transfer", "amount": 1000, "recipient": "account-B"}
    initial_context = {"tenant": "tenant-A", "risk_tier": "low", "region": "EU"}
    oracle = StateOracle(
        {"steps": ["intent", "authorize"], "within_boundary": True},
        {"source": "ta002-context-oracle-test", "context": initial_context},
    )
    authorized_world = oracle.latest().world
    decision = Decision(
        "ALLOW", "KNOWN", authorized_world.version,
        authorized_world.trajectory_digest(), "context_bound",
        context_digest=authorized_world.context_digest(),
    )
    authority = issue_authority(
        action=action, subject="account-A", decision=decision, nonce="ta002-drift",
        issued_at_ns=0, expires_at_ns=100,
    )
    assert authority is not None

    oracle.update_context({"tenant": "tenant-A", "risk_tier": "blocked", "region": "EU"})
    executed = []
    result = oracle.execute_if_valid(
        authority=authority, action=action, subject="account-A", now_ns=1,
        verify=verify_authority, execute=lambda a, _world: executed.append(a),
    )

    assert result.status == "HOLD"
    assert result.reason == "context_consistent_changed"
    assert executed == []


def test_unchanged_context_allows_valid_authority():
    action = {"type": "transfer", "amount": 1000, "recipient": "account-B"}
    context = {"tenant": "tenant-A", "risk_tier": "low", "region": "EU"}
    oracle = StateOracle(
        {"steps": ["intent", "authorize"], "within_boundary": True},
        {"source": "ta002-context-oracle-test", "context": context},
    )
    authorized_world = oracle.latest().world
    decision = Decision(
        "ALLOW", "KNOWN", authorized_world.version,
        authorized_world.trajectory_digest(), "context_bound",
        context_digest=authorized_world.context_digest(),
    )
    authority = issue_authority(
        action=action, subject="account-A", decision=decision, nonce="ta002-stable",
        issued_at_ns=0, expires_at_ns=100,
    )
    assert authority is not None

    executed = []
    result = oracle.execute_if_valid(
        authority=authority, action=action, subject="account-A", now_ns=1,
        verify=verify_authority, execute=lambda a, _world: executed.append(a),
    )

    assert result.status == "VALID"
    assert result.reason == "all_bound_invariants_hold"
    assert executed == [action]
