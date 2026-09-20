"""Research-only NEXUS v2 reference model.

This module is deliberately not a ZK implementation and is not wired into
Action Gate production. It provides a deterministic reference semantics that
a future Circom circuit must reproduce exactly.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any

SCALE = 10_000


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class RiskFeatures:
    confidence_gap: int
    instability: int


@dataclass(frozen=True)
class Decision:
    base_risk: int
    entropy: int
    adjusted_risk: int
    verdict: str
    params_hash: str


class BayesianAnomalyModel:
    """Beta-Bernoulli posterior for observed execution anomalies."""

    def __init__(self, alpha: float = 1.0, beta: float = 9.0) -> None:
        if alpha <= 0 or beta <= 0:
            raise ValueError("beta prior parameters must be positive")
        self.alpha = alpha
        self.beta = beta

    @property
    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    def observe(self, anomaly: bool) -> float:
        if anomaly:
            self.alpha += 1.0
        else:
            self.beta += 1.0
        return self.mean


class ShadowAdaptiveWeights:
    """Proposes weights from telemetry; never mutates a production policy."""

    def __init__(self, w_gap: int = 4000, w_instability: int = 4000) -> None:
        self.w_gap = w_gap
        self.w_instability = w_instability
        self.anomaly_model = BayesianAnomalyModel()

    def propose(self, confidence_gap: int, instability: int, anomaly: bool) -> tuple[int, int]:
        posterior = self.anomaly_model.observe(anomaly)
        pressure_gap = confidence_gap / SCALE
        pressure_instability = instability / SCALE

        # Research proposal only. The active policy is never changed here.
        gap = min(8000, max(1000, round(4000 + 4000 * posterior * pressure_gap)))
        instability_weight = min(
            8000, max(1000, round(4000 + 4000 * posterior * pressure_instability))
        )
        total = gap + instability_weight
        return round(gap * SCALE / total), round(instability_weight * SCALE / total)


class NexusReferenceEngine:
    def __init__(self, w_gap: int = 4000, w_instability: int = 4000) -> None:
        if w_gap < 0 or w_instability < 0 or w_gap + w_instability == 0:
            raise ValueError("weights must be non-negative and not both zero")
        self.w_gap = w_gap
        self.w_instability = w_instability

    @staticmethod
    def features(confidence: int, evidence: int, stabilization: int) -> RiskFeatures:
        for name, value in {
            "confidence": confidence,
            "evidence": evidence,
            "stabilization": stabilization,
        }.items():
            if not 0 <= value <= SCALE:
                raise ValueError(f"{name} must be in [0, {SCALE}]")
        return RiskFeatures(
            confidence_gap=abs(confidence - evidence),
            instability=SCALE - stabilization,
        )

    def evaluate(
        self,
        *,
        base_risk: int,
        confidence: int,
        evidence: int,
        stabilization: int,
        params: dict[str, Any],
        tool_class: str,
    ) -> Decision:
        if not 0 <= base_risk <= SCALE:
            raise ValueError("base_risk must be in [0, 10000]")

        f = self.features(confidence, evidence, stabilization)
        raw_entropy = self.w_gap * f.confidence_gap + self.w_instability * f.instability
        entropy = raw_entropy // SCALE
        adjusted = min(SCALE, base_risk + entropy)

        if adjusted >= 8000:
            verdict = "HEAL" if tool_class == "exec_command" else "DENY"
        elif adjusted >= 5000:
            verdict = "ASK"
        else:
            verdict = "ALLOW"

        return Decision(
            base_risk=base_risk,
            entropy=entropy,
            adjusted_risk=adjusted,
            verdict=verdict,
            params_hash=sha256_hex(params),
        )
