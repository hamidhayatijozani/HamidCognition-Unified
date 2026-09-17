"""Product Gate: deterministic pre-execution control for HamidCognition-Pro.

This gate is intentionally narrower than a model. It consumes an already-formed
proposal plus explicit runtime evidence and returns a bounded control decision.
It never executes an action and never grants authority by itself.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping


ALLOWED_ACTIONS = frozenset({
    "HOLD",
    "BUY_SMALL",
    "BUY_MEDIUM",
    "SELL_SMALL",
    "SELL_MEDIUM",
    "CLOSE_POSITION",
    "NO_TRADE",
})

META_ACTIONS = frozenset({
    "NO_CHANGE",
    "LOWER_EXPOSURE",
    "DISABLE_SYMBOL",
    "SWITCH_MODEL",
    "RAISE_REVIEW",
    "ENTER_SAFE_MODE",
    "ROLLBACK",
})


@dataclass(frozen=True)
class ProductGateResult:
    permitted: bool
    decision: str
    reasons: tuple[str, ...]
    gate_version: str = "PG-0.1"

    def as_dict(self) -> dict[str, Any]:
        return {
            "permitted": self.permitted,
            "decision": self.decision,
            "reasons": list(self.reasons),
            "gate_version": self.gate_version,
        }


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def evaluate_product_gate(
    proposal: Mapping[str, Any],
    observation: Mapping[str, Any],
    *,
    now: datetime | None = None,
    max_observation_age_seconds: int = 5,
    max_drawdown: float = 0.10,
    max_anomaly_score: float = 0.80,
) -> ProductGateResult:
    """Evaluate whether a proposal is eligible to reach the Action Gate.

    The result is advisory authority only. A caller must still pass the returned
    eligible proposal through the Action/Execution Boundary before side effects.
    Missing or malformed evidence fails closed.
    """
    reasons: list[str] = []
    action = proposal.get("action")
    if action not in ALLOWED_ACTIONS:
        return ProductGateResult(False, "DENY", ("unsupported_action",))

    if proposal.get("model_version") in (None, ""):
        reasons.append("missing_model_version")
    if proposal.get("feature_version") in (None, ""):
        reasons.append("missing_feature_version")
    if proposal.get("input_hash") in (None, ""):
        reasons.append("missing_input_hash")

    timestamp = _parse_timestamp(observation.get("timestamp"))
    reference_now = now or datetime.now(timezone.utc)
    if timestamp is None:
        reasons.append("invalid_observation_timestamp")
    elif (reference_now - timestamp).total_seconds() > max_observation_age_seconds:
        reasons.append("stale_observation")
    elif timestamp > reference_now:
        reasons.append("future_observation")

    if observation.get("connection_status") != "CONNECTED":
        reasons.append("data_connection_not_healthy")

    if observation.get("input_hash") != proposal.get("input_hash"):
        reasons.append("input_hash_mismatch")

    anomaly_score = observation.get("anomaly_score")
    if not isinstance(anomaly_score, (int, float)):
        reasons.append("missing_anomaly_score")
    elif anomaly_score >= max_anomaly_score:
        reasons.append("anomaly_threshold_exceeded")

    drawdown = observation.get("drawdown")
    if not isinstance(drawdown, (int, float)):
        reasons.append("missing_drawdown")
    elif drawdown > max_drawdown:
        reasons.append("drawdown_limit_exceeded")

    if reasons:
        return ProductGateResult(False, "SAFE_MODE", tuple(reasons))

    if action in {"HOLD", "NO_TRADE", "CLOSE_POSITION"}:
        return ProductGateResult(True, "ALLOW", ("bounded_non_opening_action",))

    return ProductGateResult(True, "ALLOW", ("proposal_passed_product_controls",))


def validate_meta_action(action: str) -> bool:
    """Validate a meta-controller command without executing it."""
    return action in META_ACTIONS
