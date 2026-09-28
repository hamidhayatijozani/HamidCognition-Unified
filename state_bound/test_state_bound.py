from .benchmark import baseline_action_authorization, build_stable_fixture, run_ta001
from .epistemic import issue_authority
from .models import Decision
from .oracle import StateOracle
from .semantics import equivalent_request
from .verifier import verify_authority


def test_ta001_baseline_and_experimental_both_allow():
    action, _world, authority = build_stable_fixture()

    assert baseline_action_authorization(action, action) == "ALLOW"

    oracle = StateOracle(
        {"steps": ["intent", "authorize"], "within_boundary": True},
        {"source": "test"},
    )
    result = oracle.execute_if_valid(
        authority=authority,
        action=action,
        subject="account-A",
        now_ns=1,
        verify=verify_authority,
        execute=lambda _action, _world: None,
    )

    assert result.status == "VALID"

    benchmark = run_ta001(iterations=100)
    assert benchmark["false_deny"] == 0
    assert benchmark["false_allow"] == 0
    assert benchmark["replay_equivalence"] == 1
    assert benchmark["experimental"]["p95_us"] >= benchmark["experimental"]["median_us"]


def test_ta001_uses_latest_committed_snapshot():
    action, _world, authority = build_stable_fixture()
    oracle = StateOracle(
        {"steps": ["intent", "authorize"], "within_boundary": True},
        {"source": "test"},
    )
    oracle.append(
        {"steps": ["intent", "authorize", "execute"], "within_boundary": True}
    )

    result = oracle.execute_if_valid(
        authority=authority,
        action=action,
        subject="account-A",
        now_ns=1,
        verify=verify_authority,
        execute=lambda _action, _world: None,
    )

    assert result.status == "INVALID"
    assert "trajectory_consistent" in result.reason


def test_ta001_expired_authority_is_rejected():
    action, _world, authority = build_stable_fixture()
    oracle = StateOracle(
        {"steps": ["intent", "authorize"], "within_boundary": True},
        {"source": "test"},
    )

    result = oracle.execute_if_valid(
        authority=authority,
        action=action,
        subject="account-A",
        now_ns=10**18,
        verify=verify_authority,
        execute=lambda _action, _world: None,
    )

    assert result.status == "INVALID"
    assert "authority_not_expired" in result.reason


def test_replay_equivalence_is_explicit_and_excludes_context():
    action = {"type": "transfer", "amount": 1000, "recipient": "B"}

    assert equivalent_request(
        {"action": action, "world_version": 1, "epistemic_state": "KNOWN"},
        {"action": dict(action), "world_version": 2, "epistemic_state": "STALE"},
    )

    assert not equivalent_request(
        {"action": action, "world_version": 1, "epistemic_state": "KNOWN"},
        {
            "action": {**action, "amount": 900},
            "world_version": 1,
            "epistemic_state": "KNOWN",
        },
    )


def test_unknown_cannot_issue_authority():
    action, world, _authority = build_stable_fixture()
    decision = Decision(
        decision="ALLOW",
        epistemic_state="UNKNOWN",
        world_version=world.version,
        trajectory_digest=world.trajectory_digest(),
        reason="unknown",
    )

    assert (
        issue_authority(
            action=action,
            subject="account-A",
            decision=decision,
            nonce="unknown",
            issued_at_ns=0,
            expires_at_ns=10**18,
        )
        is None
    )
