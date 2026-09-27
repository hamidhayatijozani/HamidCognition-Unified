"""Research-only P/S/T shock-degradation and recovery engine.

This module is deliberately isolated from the canonical baseline and the
commercial Action Gate. It implements a falsifiable T-state controller.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import hashlib
from typing import Iterable


@dataclass(frozen=True)
class RecoveryConfig:
    lambda_recovery: float = 0.08
    lambda_shock: float = 0.25
    t_min: float = 0.01
    t_max: float = 0.80
    epsilon: float = 1e-12


def saturated_shock(d: float) -> float:
    d = max(0.0, float(d))
    return d / (1.0 + d)


def recovery_gate(d: float, previous_d: float | None) -> int:
    if previous_d is None:
        return 0
    return int(d < previous_d)


def update_t(
    t: float,
    d: float,
    previous_d: float | None,
    config: RecoveryConfig = RecoveryConfig(),
) -> tuple[float, int, float, float]:
    gate = recovery_gate(d, previous_d)
    shock = saturated_shock(d)
    recovery = config.lambda_recovery * (1.0 - t) * gate
    degradation = config.lambda_shock * shock
    next_t = min(config.t_max, max(config.t_min, t + recovery - degradation))
    return next_t, gate, recovery, degradation


def phase_observer(p: float, s: float, t: float) -> str:
    if abs(p - s) < 0.1:
        return "RUPTURE_IMMINENT"
    if t < 0.45:
        return "UNSTABLE_CREATIVITY"
    return "STEADY"


def energy(p: float, s: float, t: float, epsilon: float = 1e-12) -> float:
    return (p * s) / (1.1 - t + epsilon)


def run_trajectory(
    d_values: Iterable[float],
    *,
    p: float = 0.5,
    s: float = 0.5,
    t0: float = 0.5,
    config: RecoveryConfig = RecoveryConfig(),
) -> list[dict]:
    rows: list[dict] = []
    previous_d: float | None = None
    t = t0
    for step, d in enumerate(d_values, 1):
        t, gate, recovery, degradation = update_t(t, d, previous_d, config)
        rows.append(
            {
                "step": step,
                "D": round(float(d), 12),
                "P": round(p, 12),
                "S": round(s, 12),
                "T": round(t, 12),
                "R": gate,
                "shock": round(degradation, 12),
                "recovery": round(recovery, 12),
                "E": round(energy(p, s, t), 12),
                "phase": phase_observer(p, s, t),
            }
        )
        previous_d = float(d)
    return rows


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def trajectory_sha256(rows: list[dict]) -> str:
    return hashlib.sha256(canonical_json(rows).encode("utf-8")).hexdigest()
