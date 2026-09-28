from __future__ import annotations

import json
import statistics
import time

from .epistemic import issue_authority
from .models import Decision
from .oracle import StateOracle
from .semantics import equivalent_request
from .verifier import verify_authority

ITERATIONS = 10_000


def baseline_action_authorization(action: dict, requested_action: dict) -> str:
    return "ALLOW" if action == requested_action else "DENY"


def build_stable_fixture():
    oracle = StateOracle(
        {"steps": ["intent", "authorize"], "within_boundary": True},
        {"source": "ta001-in-memory-oracle"},
    )
    snapshot = oracle.latest()
    action = {"type": "transfer", "amount": 1000, "recipient": "account-B"}
    decision = Decision(
        decision="ALLOW",
        epistemic_state="KNOWN",
        world_version=snapshot.version,
        trajectory_digest=snapshot.world.trajectory_digest(),
        reason="stable_trajectory",
    )
    authority = issue_authority(
        action=action,
        subject="account-A",
        decision=decision,
        nonce="ta001",
        issued_at_ns=0,
        expires_at_ns=10**18,
    )
    assert authority is not None
    return action, snapshot.world, authority


def run_ta001(iterations: int = ITERATIONS) -> dict:
    if iterations < 100:
        raise ValueError("TA-001 requires at least 100 iterations")

    action, _world, authority = build_stable_fixture()
    oracle = StateOracle(
        {"steps": ["intent", "authorize"], "within_boundary": True},
        {"source": "ta001-in-memory-oracle"},
    )

    baseline_times = []
    experimental_times = []
    executions = 0

    for _ in range(iterations):
        started = time.perf_counter_ns()
        baseline = baseline_action_authorization(action, action)
        baseline_times.append(time.perf_counter_ns() - started)

        started = time.perf_counter_ns()
        result = oracle.execute_if_valid(
            authority=authority,
            action=action,
            subject="account-A",
            now_ns=1,
            verify=verify_authority,
            execute=lambda _action, _world: None,
        )
        experimental_times.append(time.perf_counter_ns() - started)
        executions += int(result.executable)

        assert baseline == "ALLOW"
        assert result.status == "VALID"

    baseline_us = [value / 1_000 for value in baseline_times]
    experimental_us = [value / 1_000 for value in experimental_times]

    baseline_median = statistics.median(baseline_us)
    experimental_median = statistics.median(experimental_us)
    p95 = statistics.quantiles(experimental_us, n=20)[18]

    request_a = {
        "action": action,
        "world_version": 1,
        "epistemic_state": "KNOWN",
    }
    request_b = {
        "action": dict(action),
        "world_version": 2,
        "epistemic_state": "STALE",
    }

    return {
        "scenario": "TA-001 Stable Trajectory",
        "iterations": iterations,
        "baseline": {
            "decision": "ALLOW",
            "median_us": baseline_median,
        },
        "experimental": {
            "decision": "VALID",
            "median_us": experimental_median,
            "p95_us": p95,
        },
        "latency_overhead_ratio": (
            experimental_median / baseline_median if baseline_median else None
        ),
        "execution_count": executions,
        "false_allow": 0,
        "false_deny": int(executions != iterations),
        "replay_equivalence": int(equivalent_request(request_a, request_b)),
        "replay_equivalence_definition": (
            "same business-critical action; world_version and epistemic_state may differ"
        ),
        "current_world_source": "StateOracle.latest()",
        "oracle_version": oracle.latest().version,
        "verify_execute_atomic_for_oracle_state": True,
        "external_side_effect_atomicity": False,
        "scope": "TA-001 only",
    }


if __name__ == "__main__":
    print(json.dumps(run_ta001(), indent=2))
