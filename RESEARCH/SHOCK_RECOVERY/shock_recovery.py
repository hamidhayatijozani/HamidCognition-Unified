from __future__ import annotations

from dataclasses import dataclass


def sat(d: float) -> float:
    if d < 0:
        raise ValueError("D_must_be_nonnegative")
    return d / (1.0 + d)


@dataclass(frozen=True)
class RecoveryConfig:
    base: float = 0.50
    t_min: float = 0.01
    t_max: float = 0.80
    lambda_recovery: float = 0.20
    lambda_shock: float = 0.20
    shock_threshold: float = 1.0


@dataclass
class RecoveryEngine:
    config: RecoveryConfig = RecoveryConfig()
    T: float = 0.50
    previous_D: float = 0.0

    def step(self, D: float) -> dict[str, float | int]:
        if D < 0:
            raise ValueError("D_must_be_nonnegative")
        delta_D = D - self.previous_D
        R = 1 if (D <= self.config.shock_threshold and delta_D < 0) else 0
        degradation = self.config.lambda_shock * sat(D)
        recovery = self.config.lambda_recovery * (1.0 - self.T) * R
        self.T = min(
            self.config.t_max,
            max(self.config.t_min, self.T + recovery - degradation),
        )
        self.previous_D = D
        return {"D": D, "delta_D": delta_D, "R": R, "T": round(self.T, 10)}
