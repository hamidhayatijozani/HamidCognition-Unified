from __future__ import annotations

import json

from .epistemic import issue_authority
from .models import Decision
from .oracle import StateOracle
from .verifier import verify_authority


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
        action=action, subject="A", decision=decision, nonce="trajectory-benchmark",
        issued_at_ns=0, expires_at_ns=10**18,
    )
    assert authority is not None
    return oracle, action, authority


def run_case(mutation=None):
    oracle, action, authority = fixture()
    if mutation:
        mutation(oracle)
    return oracle.execute_if_valid(
        authority=authority, action=action, subject="A", now_ns=1,
        verify=verify_authority, execute=lambda _a, _w: None,
    )


def run_trajectory_benchmark() -> dict:
    cases = {
        "TA-001": ("ALLOW", None),
        "TA-002": ("HOLD", lambda o: o.update_context(
            {"tenant": "A", "recipient_status": "changed"})),
        "TA-003": ("UNKNOWN", lambda o: o.update_state({"balance": 500})),
        "TA-004": ("UNKNOWN", lambda o: o.update_evidence(
            {"policy": "P1", "fresh": False})),
        "TA-005": ("HOLD", lambda o: o.append(
            {"steps": ["intent", "authorize", "unexpected_action"],
             "within_boundary": False})),
    }

    results = {}
    for name, (expected, mutation) in cases.items():
        observed = run_case(mutation)
        results[name] = {
            "expected": expected,
            "observed": observed.status,
            "passed": observed.status == expected,
            "reason": observed.reason,
            "invariants": observed.invariant_results,
        }

    return {
        "benchmark": "Trajectory/Reality Evaluation TA-001..TA-005",
        "results": results,
        "all_passed": all(item["passed"] for item in results.values()),
        "authority_issued_for_unknown": False,
        "external_side_effect_atomicity": False,
    }


if __name__ == "__main__":
    print(json.dumps(run_trajectory_benchmark(), indent=2))
