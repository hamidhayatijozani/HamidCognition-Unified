import json
import statistics
import time
from dataclasses import dataclass
from .authority import issue_authority
from .epistemic import EpistemicState
from .state import WorldState, digest
from .verifier import execute_once

SECRET = b"state-bound-experiment-secret"

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
    current_world_source: str
    freshness_valid: bool

def baseline_action_authorization(action, authorized_action):
    return "ALLOW" if digest(action) == digest(authorized_action) else "DENY"

def build_stable_fixture():
    action = {"action": "transfer", "amount": 1000, "recipient": "account-B"}
    world = WorldState(
        context={"account":"account-A"}, state={"balance":10000},
        evidence=[{"id":"balance-check","valid":True}],
        trajectory={"steps":["intent","authorize"]},
        policy={"version":"p1","transfer_limit":2000},
        environment={"region":"EU","service":"payments-v1"},
        source="stable-test-fixture", observed_at=1000, freshness_bound_seconds=0,
    )
    authority = issue_authority(
        subject="account-A", intent="transfer", action=action, world=world,
        epistemic_state=EpistemicState.KNOWN, risk="HIGH", secret=SECRET,
    )
    return action, world, authority

def run_ta001(iterations=1000):
    action, world, authority = build_stable_fixture()
    latencies=[]
    results=[]
    for _ in range(iterations):
        start=time.perf_counter_ns()
        result=execute_once(authority,current_world=world,current_action=action,tenant_subject="account-A",secret=SECRET,consumed_nonces=set())
        latencies.append((time.perf_counter_ns()-start)/1000)
        results.append(result)
    baseline=baseline_action_authorization(action, action)
    experimental=results[-1].status
    return StableResult(
        scenario="TA-001 Stable Trajectory",
        baseline=baseline,
        experimental=experimental,
        false_allow=0,
        false_deny=int(any(r.status!="VALID" for r in results)),
        replay_equivalence=int(baseline=="ALLOW" and experimental=="VALID"),
        median_verify_us=statistics.median(latencies),
        p95_verify_us=sorted(latencies)[int(iterations*0.95)-1],
        current_world_source=world.source,
        freshness_valid=world.freshness_valid(1000),
    )

if __name__ == "__main__":
    print(json.dumps(run_ta001().__dict__, indent=2))
