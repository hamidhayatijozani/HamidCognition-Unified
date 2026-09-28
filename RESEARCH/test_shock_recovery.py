"""Falsification suite for the research-only shock/recovery engine."""
from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from RESEARCH.shock_recovery_engine import RecoveryConfig, run_trajectory, trajectory_sha256


CONFIG = RecoveryConfig(lambda_recovery=0.08, lambda_shock=0.25, t_min=0.01, t_max=0.80)


def assert_monotonic_non_decreasing(values):
    assert all(b >= a for a, b in zip(values, values[1:])), values


def run_suite():
    no_shock = run_trajectory([0.0] * 10, t0=0.5, config=CONFIG)
    assert all(abs(row["T"] - 0.25) < 1e-12 for row in no_shock) is False
    # A zero shock must not trigger recovery or degradation after initialization.
    assert all(row["R"] == 0 for row in no_shock)
    assert all(abs(row["T"] - 0.5) < 1e-12 for row in no_shock)

    shocked = run_trajectory([10.0], t0=0.5, config=CONFIG)
    degraded_t = shocked[-1]["T"]
    assert degraded_t < 0.5

    persistent = run_trajectory([10.0] * 40, t0=0.5, config=CONFIG)
    assert all(row["R"] == 0 for row in persistent[1:])
    assert persistent[-1]["T"] == CONFIG.t_min
    assert all(b <= a + 1e-12 for a, b in zip(
        [row["T"] for row in persistent],
        [row["T"] for row in persistent][1:],
    ))

    removal = run_trajectory([10.0] * 4 + [2.0, 1.0, 0.5, 0.1, 0.0] + [0.0] * 8, t0=0.5, config=CONFIG)
    shocked_t = removal[3]["T"]
    recovered = [row["T"] for row in removal[4:]]
    assert any(row["R"] == 1 for row in removal[4:])
    assert_monotonic_non_decreasing(recovered)
    assert recovered[-1] > shocked_t
    assert recovered[-1] <= CONFIG.t_max

    replay_input = [0.0, 10.0, 10.0, 10.0, 2.0, 1.0, 0.5, 0.1, 0.0, 0.0]
    replay_a = run_trajectory(replay_input, t0=0.5, config=CONFIG)
    replay_b = run_trajectory(replay_input, t0=0.5, config=CONFIG)
    sha_a = trajectory_sha256(replay_a)
    sha_b = trajectory_sha256(replay_b)
    assert replay_a == replay_b
    assert sha_a == sha_b

    return {
        "1_no_shock": {"pass": True, "final_T": no_shock[-1]["T"]},
        "2_shock_degradation": {"pass": True, "degraded_T": degraded_t},
        "3_persistent_shock_no_recovery": {
            "pass": True,
            "min_T_reached": persistent[-1]["T"],
            "all_recovery_gates_zero": all(row["R"] == 0 for row in persistent),
        },
        "4_shock_removal_recovery": {
            "pass": True,
            "initial_shocked_T": shocked_t,
            "final_recovered_T": recovered[-1],
        },
        "5_replay_sha256_integrity": {"pass": True, "sha256": sha_a},
    }


if __name__ == "__main__":
    result = run_suite()
    print(json.dumps(result, indent=2, sort_keys=True))
