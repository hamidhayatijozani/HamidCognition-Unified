from state_bound.models import Decision
from state_bound.oracle import StateOracle
from state_bound.epistemic import issue_authority
from state_bound.verifier import verify_authority
from state_bound.ta002 import ACTION, DRIFTED_CONTEXT, INITIAL_CONTEXT, TRAJECTORY, run_ta002

def make_authority(oracle):
    world=oracle.latest().world
    decision=Decision("ALLOW","KNOWN",world.version,world.trajectory_digest(),"context_bound",context_digest=world.context_digest())
    return issue_authority(action=ACTION,subject="account-A",decision=decision,nonce="test-ta002",issued_at_ns=0,expires_at_ns=1000)

def test_context_drift_is_detected_without_trajectory_change():
    oracle=StateOracle(TRAJECTORY,{"source":"test","context":INITIAL_CONTEXT})
    authority=make_authority(oracle)
    before=oracle.latest().world
    after=oracle.update_context(DRIFTED_CONTEXT).world
    assert after.version==before.version
    assert after.trajectory_digest()==before.trajectory_digest()
    assert after.context_digest()!=before.context_digest()
    result=verify_authority(authority,current_world=after,current_action=ACTION,subject="account-A",now_ns=1)
    assert result.status=="INVALID"
    assert "context_consistent" in result.reason
    assert not result.executable

def test_stable_context_remains_valid():
    oracle=StateOracle(TRAJECTORY,{"source":"test","context":INITIAL_CONTEXT})
    authority=make_authority(oracle)
    result=verify_authority(authority,current_world=oracle.latest().world,current_action=ACTION,subject="account-A",now_ns=1)
    assert result.status=="VALID"

def test_ta002_benchmark_detects_baseline_false_allow():
    result=run_ta002(iterations=100)
    assert result["drift_setup"]["trajectory_version_unchanged"]
    assert result["drift_setup"]["trajectory_digest_unchanged"]
    assert result["drift_setup"]["context_digest_changed"]
    assert result["baseline"]["false_allow_rate"]==1.0
    assert result["experimental"]["false_allow_rate"]==0.0
    assert result["experimental"]["false_deny_rate_on_stable"]==0.0
