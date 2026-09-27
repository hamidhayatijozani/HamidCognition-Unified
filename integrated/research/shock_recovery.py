from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class RecoveryConfig:
    t_min: float = 0.01
    t_max: float = 0.80
    lambda_recovery: float = 0.35
    lambda_shock: float = 0.20
    shock_scale: float = 1.0


def saturated_shock(d: float) -> float:
    if d < 0:
        raise ValueError("shock_distance_must_be_non_negative")
    return d / (1.0 + d)


def recovery_gate(previous_d: float, current_d: float) -> int:
    return int(current_d < previous_d)


def step_t(t: float, previous_d: float, d: float, config: RecoveryConfig = RecoveryConfig()) -> tuple[float, int]:
    if not config.t_min <= t <= config.t_max:
        raise ValueError("t_out_of_bounds")
    gate = recovery_gate(previous_d, d)
    recovery = config.lambda_recovery * (1.0 - t) * gate
    degradation = config.lambda_shock * saturated_shock(d * config.shock_scale)
    next_t = min(max(t + recovery - degradation, config.t_min), config.t_max)
    return next_t, gate


def run_trajectory(distances: Iterable[float], *, t0: float = 0.50, config: RecoveryConfig = RecoveryConfig()) -> list[dict[str, float | int]]:
    values = list(distances)
    if not values:
        raise ValueError("distance_series_must_not_be_empty")
    if any(d < 0 for d in values):
        raise ValueError("shock_distance_must_be_non_negative")

    t = t0
    previous_d = values[0]
    trajectory: list[dict[str, float | int]] = [{"step": 0, "D": round(previous_d, 10), "T": round(t, 10), "R": 0}]
    for index, d in enumerate(values[1:], start=1):
        t, gate = step_t(t, previous_d, d, config)
        trajectory.append({"step": index, "D": round(d, 10), "T": round(t, 10), "R": gate})
        previous_d = d
    return trajectory
