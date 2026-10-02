from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
import math

ReactionMode = Literal["PROCEED", "HOLD", "INHIBIT", "UNKNOWN"]


@dataclass(frozen=True)
class ReactivityFactors:
    """Normalized factors inspired by chemical reaction conditions.

    This is a research model, not a scientific claim about physical chemistry.
    Every factor is explicit so experiments can be replayed and falsified.
    """

    activation: float
    inhibition: float
    context_stability: float
    state_stability: float
    evidence_strength: float
    trajectory_stability: float

    def __post_init__(self) -> None:
        for name in self.__dataclass_fields__:
            if name == "consumer_action":
                continue
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise TypeError(f"{name} must be a finite numeric value")
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0, 1]")


@dataclass(frozen=True)
class ReactivityResult:
    mode: ReactionMode
    reactivity: float
    activation_margin: float
    reason: str
    consumer_action: str


def calculate_reactivity(
    factors: ReactivityFactors,
    *,
    activation_threshold: float = 0.70,
    inhibition_threshold: float = 0.35,
    minimum_stability: float = 0.80,
) -> ReactivityResult:
    """Map execution conditions to a bounded experimental reactivity score.

    This mapping is deliberately simple and deterministic. It is a hypothesis
    surface for experiments, not a replacement for Action Gate authorization.
    """
    if not 0.0 <= activation_threshold <= 1.0:
        raise ValueError("activation_threshold must be in [0, 1]")
    if not 0.0 <= inhibition_threshold <= 1.0:
        raise ValueError("inhibition_threshold must be in [0, 1]")
    if not 0.0 <= minimum_stability <= 1.0:
        raise ValueError("minimum_stability must be in [0, 1]")

    stability = (
        factors.context_stability
        * factors.state_stability
        * factors.evidence_strength
        * factors.trajectory_stability
    ) ** 0.25

    reactivity = max(
        0.0,
        min(1.0, factors.activation * stability * (1.0 - factors.inhibition)),
    )
    margin = reactivity - activation_threshold

    if factors.inhibition >= inhibition_threshold:
        return ReactivityResult("INHIBIT", reactivity, margin, "inhibitor_above_threshold", "BLOCK_REACTION")
    if stability < minimum_stability:
        return ReactivityResult("HOLD", reactivity, margin, "stability_below_threshold", "REQUIRE_REEVALUATION")
    if reactivity >= activation_threshold:
        return ReactivityResult("PROCEED", reactivity, margin, "REQUEST_ACTION_GATE_AUTHORIZATION")
    return ReactivityResult("UNKNOWN", reactivity, margin, "REQUIRE_EVIDENCE")
