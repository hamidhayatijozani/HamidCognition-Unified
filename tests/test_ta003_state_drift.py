from state_bound.models import Decision
from state_bound.oracle import StateOracle
from state_bound.epistemic import issue_authority
from state_bound.verifier import verify_authority
from state_bound.ta003 import ACTION, CONTEXT, DRIFTED_STATE, INITIAL_STATE, TRAJECTORY, run_ta003

def make_authority(oracle):
    world=oracle.latest().world
    decision=Decision("ALLOW","KNOWN",world.version,world.trajectory_digest(),"state_bound",context_digest=world.context_digest(),state_digest=world.state_digest())
    return issue_authority(action=ACTION,subject="account-A",decision=decision,nonce="test-ta003",issued_at_ns=0,expires_at_ns=1000)

def test_state_drift_is_detected_without_trajectory_or_context_change():
    oracle=StateOracle(TRAJECTORY,{"source":"test","context":CONTEXT,"state":INITIAL_STATE})
    authority=make_authority(oracle)
    before=oracle.latest().world
    after=oracle.update_state(DRIFTED_STATE).world
    assert after.version==before.version
    assert after.trajectory_digest()==before.trajectory_digest()
    assert after.context_digest()==before.context_digest()
    assert after.state_digest()!=before.state_digest()
    result=verify_authority(authority,current_world=after,current_action=ACTION,subject="account-A",now_ns=1)
    assert result.status=="UNKNOWN"
    assert "state_consistent" in result.reason
    assert not result.executable

def test_stable_state_remains_valid():
    oracle=StateOracle(TRAJECTORY,{"source":"test","context":CONTEXT,"state":INITIAL_STATE})
    authority=make_authority(oracle)
    result=verify_authority(authority,current_world=oracle.latest().world,current_action=ACTION,subject="account-A",now_ns=1)
    assert result.status=="VALID"

def test_ta003_benchmark_detects_baseline_false_allow():
    result=run_ta003(iterations=100)
    assert result["drift_setup"]["trajectory_version_unchanged"]
    assert result["drift_setup"]["trajectory_digest_unchanged"]
    assert result["drift_setup"]["context_digest_unchanged"]
    assert result["drift_setup"]["state_digest_changed"]
    assert result["baseline"]["false_allow_rate"]==1.0
    assert result["experimental"]["false_allow_rate"]==0.0
    assert result["experimental"]["false_deny_rate_on_stable"]==0.0
