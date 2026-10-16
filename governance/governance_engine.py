"""Conservative policy mapping; this module does not execute tools or trades."""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class GovernanceDecision:
    action: str
    reason: str
    hais_score: float
    drs_score: float


class GovernanceDecisionEngine:
    def decide(self, hais_score: float, drs_score: float) -> GovernanceDecision:
        for name, score in (("HAIS", hais_score), ("DRS", drs_score)):
            if not isinstance(score, (int, float)) or not math.isfinite(score) or not 0 <= score <= 1:
                return GovernanceDecision("DENY", f"invalid_{name.lower()}_score", -1.0, -1.0)
        if hais_score >= 0.85 and drs_score <= 0.30:
            return GovernanceDecision("ALLOW", "thresholds_satisfied", float(hais_score), float(drs_score))
        if hais_score >= 0.85:
            return GovernanceDecision("ASK", "risk_requires_human_review", float(hais_score), float(drs_score))
        if drs_score <= 0.30:
            return GovernanceDecision("SANDBOX", "epistemic_score_below_allow_threshold", float(hais_score), float(drs_score))
        return GovernanceDecision("DENY", "epistemic_and_risk_thresholds_not_satisfied", float(hais_score), float(drs_score))
