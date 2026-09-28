from __future__ import annotations
import json, statistics, time
from .epistemic import issue_authority
from .models import Decision
from .oracle import StateOracle
from .verifier import verify_authority

ITERATIONS=10000
ACTION={"type":"transfer","amount":1000,"recipient":"account-B"}
INITIAL_CONTEXT={"tenant":"tenant-A","risk_tier":"low","region":"EU"}
DRIFTED_CONTEXT={"tenant":"tenant-A","risk_tier":"blocked","region":"EU"}
TRAJECTORY={"steps":["intent","authorize"],"within_boundary":True}

def fixture():
    oracle=StateOracle(TRAJECTORY,{"source":"ta002-context-oracle","context":INITIAL_CONTEXT})
    before=oracle.latest().world
    decision=Decision("ALLOW","KNOWN",before.version,before.trajectory_digest(),"context_bound",context_digest=before.context_digest())
    authority=issue_authority(action=ACTION,subject="account-A",decision=decision,nonce="ta002",issued_at_ns=0,expires_at_ns=10**18)
    oracle.update_context(DRIFTED_CONTEXT)
    return oracle,authority

def run_ta002(iterations:int=ITERATIONS)->dict:
    oracle,authority=fixture(); current=oracle.latest().world
    stable_world=type(current)(current.version,current.trajectory,{"source":"ta002-context-oracle","context":INITIAL_CONTEXT})
    stable=[]; drift=[]; baseline_drift_allow=0; experimental_drift_allow=0; stable_valid=0
    for _ in range(iterations):
        t=time.perf_counter_ns()
        stable_result=verify_authority(authority,current_world=stable_world,current_action=ACTION,subject="account-A",now_ns=1)
        stable.append((time.perf_counter_ns()-t)/1000)
        stable_valid+=int(stable_result.status=="VALID")
        baseline_drift_allow+=int(ACTION==authority.action)
        t=time.perf_counter_ns()
        drift_result=verify_authority(authority,current_world=current,current_action=ACTION,subject="account-A",now_ns=1)
        drift.append((time.perf_counter_ns()-t)/1000)
        experimental_drift_allow+=int(drift_result.status=="VALID")
    p95=lambda xs: statistics.quantiles(xs,n=20)[18]
    return {"scenario":"TA-002 Context Drift","iterations":iterations,"drift_setup":{"trajectory_version_unchanged":current.version==authority.decision.world_version,"trajectory_digest_unchanged":current.trajectory_digest()==authority.decision.trajectory_digest,"context_digest_changed":current.context_digest()!=authority.decision.context_digest},"baseline":{"policy":"action-only authorization","drift_allows":baseline_drift_allow,"false_allow_rate":baseline_drift_allow/iterations},"experimental":{"stable_valid":stable_valid,"drift_allows":experimental_drift_allow,"false_allow_rate":experimental_drift_allow/iterations,"false_deny_rate_on_stable":1-stable_valid/iterations},"latency_us":{"stable_median":statistics.median(stable),"stable_p95":p95(stable),"drift_median":statistics.median(drift),"drift_p95":p95(drift)},"scope":"TA-002 context-only drift; in-memory oracle; no external side effects"}

if __name__=="__main__": print(json.dumps(run_ta002(),indent=2))
