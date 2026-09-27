from __future__ import annotations

import hashlib
import json

from shock_recovery import RecoveryConfig, run_trajectory

CONFIG = RecoveryConfig()


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def test_no_shock_preserves_baseline() -> None:
    trajectory = run_trajectory([0.0] * 12, config=CONFIG)
    assert all(row["T"] == 0.5 for row in trajectory)
    assert all(row["R"] == 0 for row in trajectory)


def test_shock_degrades_t() -> None:
    trajectory = run_trajectory([0.0, 10.0], config=CONFIG)
    assert trajectory[-1]["R"] == 0
    assert trajectory[-1]["T"] < 0.5
    assert round(trajectory[-1]["T"], 4) == 0.3182


def test_persistent_shock_never_recovers() -> None:
    trajectory = run_trajectory([10.0] * 20, config=CONFIG)
    assert all(row["R"] == 0 for row in trajectory)
    assert all(trajectory[i]["T"] <= trajectory[i - 1]["T"] for i in range(1, len(trajectory)))
    assert trajectory[-1]["T"] == CONFIG.t_min


def test_shock_removal_recovers_monotonically() -> None:
    trajectory = run_trajectory([0.0, 10.0, 8.0, 6.0, 4.0, 2.0, 1.0, 0.5, 0.2, 0.1, 0.05, 0.02, 0.0], config=CONFIG)
    recovered = [row["T"] for row in trajectory[2:]]
    assert all(row["R"] == 1 for row in trajectory[2:])
    assert all(recovered[i] >= recovered[i - 1] for i in range(1, len(recovered)))
    assert recovered[-1] <= CONFIG.t_max


def test_replay_is_byte_identical() -> None:
    distances = [0.0, 10.0, 8.0, 6.0, 4.0, 2.0, 1.0, 0.5, 0.2, 0.1, 0.05, 0.02, 0.0]
    first = run_trajectory(distances, config=CONFIG)
    second = run_trajectory(distances, config=CONFIG)
    assert canonical_bytes(first) == canonical_bytes(second)
    assert hashlib.sha256(canonical_bytes(first)).hexdigest() == hashlib.sha256(canonical_bytes(second)).hexdigest()
