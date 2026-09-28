from .benchmark import baseline_action_authorization, build_stable_fixture, run_ta001
from .epistemic import issue_authority
from .models import Decision

def test_ta001_baseline_and_experimental_both_allow():
    action, world, authority = build_stable_fixture()
    assert baseline_action_authorization(action, action) == "ALLOW"
    result = run_ta001(iterations=100)
    assert result.experimental == "VALID"
    assert result.false_deny == 0
    assert result.false_allow == 0
    assert result.replay_equivalence == 1
    assert result.p95_verify_us >= result.median_verify_us

def test_unknown_cannot_issue_authority():
    action, world, _ = build_stable_fixture()
    decision = Decision("ALLOW","UNKNOWN",world,reason="unknown")
    assert issue_authority(action=action,world=world,decision=decision,nonce="unknown") is None
