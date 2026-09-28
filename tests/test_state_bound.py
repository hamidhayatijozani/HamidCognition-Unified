from state_bound.epistemic import issue_authority
from state_bound.models import Decision
from state_bound.oracle import StateOracle
from state_bound.semantics import equivalent_request
from state_bound.verifier import verify_authority

def fixture():
    oracle=StateOracle({"steps":["intent","authorize"],"within_boundary":True},{"source":"test"})
    s=oracle.latest(); action={"type":"transfer","amount":1000,"recipient":"B"}
    d=Decision("ALLOW","KNOWN",s.version,s.world.trajectory_digest(),"stable")
    a=issue_authority(action=action,subject="A",decision=d,nonce="n1",issued_at_ns=0,expires_at_ns=10000)
    return oracle,action,a

def test_ta001_stable_trajectory_executes_atomically():
    oracle,action,a=fixture(); calls=[]
    r=oracle.execute_if_valid(authority=a,action=action,subject="A",now_ns=1,verify=verify_authority,execute=lambda x,w:calls.append((x,w.version)))
    assert r.status=="VALID"; assert calls==[(action,1)]

def test_ta001_uses_latest_committed_snapshot():
    oracle,action,a=fixture(); oracle.append({"steps":["intent","authorize","execute"],"within_boundary":True})
    r=oracle.execute_if_valid(authority=a,action=action,subject="A",now_ns=1,verify=verify_authority,execute=lambda _a,_w:None)
    assert r.status=="HOLD"; assert "trajectory_consistent" in r.reason

def test_ta001_expired_authority_is_rejected():
    oracle,action,a=fixture()
    r=oracle.execute_if_valid(authority=a,action=action,subject="A",now_ns=10000,verify=verify_authority,execute=lambda _a,_w:None)
    assert r.status=="HOLD"; assert "authority_not_expired" in r.reason

def test_replay_equivalence_is_explicit_and_excludes_context():
    action={"type":"transfer","amount":1000,"recipient":"B"}
    assert equivalent_request({"action":action,"world_version":1,"epistemic_state":"KNOWN"},{"action":dict(action),"world_version":2,"epistemic_state":"STALE"})
    assert not equivalent_request({"action":action,"world_version":1,"epistemic_state":"KNOWN"},{"action":{**action,"amount":900},"world_version":1,"epistemic_state":"KNOWN"})
