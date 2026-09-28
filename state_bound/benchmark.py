from __future__ import annotations
import json
import statistics
from dataclasses import dataclass
from .models import Decision, WorldState, digest
from .epistemic import issue_authority
from .verifier import verify_authority

@dataclass
class StableResult:
    scenario: str
    baseline: str
    experimental: str
    false_allow: int
    false_deny: int
    replay_equivalence: int
    median_verify_us: float
    p95_verify_us: float

def baseline_action_authorization(action, authorized_action):
    return "ALLOW" if digest(action) == digest(authorized_action) else "DENY"

def build_stable_fixture():
    action={"action":"transfer","amount":1000,"recipient":"account-B"}
    world=WorldState(
        context={"account":"account-A"}, state={"balance":10000},
        evidence=[{"id":"balance-check","valid":True}],
        trajectory={"steps":["intent","authorize"]},
        environment={"region":"EU","service":"payments-v1"},
        policy={"version":"p1","transfer_limit":2000},
    )
    decision=Decision("ALLOW","KNOWN",world,reason="TA-001 stable fixture")
    authority=issue_authority(action=action,world=world,decision=decision,nonce="ta001-nonce")
    assert authority is not None
    return action,world,authority

def run_ta001(iterations=1000):
    action,world,authority=build_stable_fixture()
    samples=[]; results=[]
    for _ in range(iterations):
        result=verify_authority(authority,action=action,current_world=world,consumed_nonces=set())
        samples.append(result.latency_us)
        results.append(result)
    samples.sort()
    baseline=baseline_action_authorization(action,action)
    experimental=results[-1].status
    return StableResult(
        scenario="TA-001 Stable Trajectory",
        baseline=baseline,
        experimental=experimental,
        false_allow=0,
        false_deny=int(any(r.status!="VALID" for r in results)),
        replay_equivalence=int(baseline=="ALLOW" and experimental=="VALID"),
        median_verify_us=statistics.median(samples),
        p95_verify_us=samples[int(iterations*0.95)-1],
    )

if __name__=="__main__":
    print(json.dumps(run_ta001().__dict__,indent=2))
