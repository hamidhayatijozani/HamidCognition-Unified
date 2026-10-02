from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
import hashlib
import json

ReactionMode = Literal["PROCEED", "HOLD", "INHIBIT", "UNKNOWN"]


@dataclass(frozen=True)
class ReactionNode:
    """One bounded reaction step in an action trajectory.

    The chemistry terminology is an engineering analogy. Values are normalized
    control signals, not physical-chemistry measurements.
    """

    name: str
    activation: float
    inhibition: float
    stability: float
    evidence: float
    consequence: float = 0.0

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name must not be empty")
        for field in ("activation", "inhibition", "stability", "evidence", "consequence"):
            value = getattr(self, field)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field} must be in [0, 1]")


@dataclass(frozen=True)
class ReactionNetworkResult:
    mode: ReactionMode
    network_reactivity: float
    barrier: float
    cascade_pressure: float
    weakest_node: str
    trace: tuple[str, ...]
    trace_digest: str


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def evaluate_reaction_network(
    nodes: tuple[ReactionNode, ...],
    *,
    activation_threshold: float = 0.70,
    hold_threshold: float = 0.55,
    cascade_threshold: float = 0.60,
    catalyst: float = 0.0,
) -> ReactionNetworkResult:
    """Evaluate a trajectory as a bounded reaction chain.

    Three deliberate properties make this useful beyond the first model:
    1. inhibitors create a hard barrier rather than merely lowering a score;
    2. evidence can act as a bounded catalyst, but never creates authority;
    3. downstream consequence can propagate pressure through the trajectory.

    The result is advisory research state. Action Gate remains the execution
    authority and must independently authorize any external side effect.
    """
    if not nodes:
        raise ValueError("nodes must not be empty")
    for name, value in (
        ("activation_threshold", activation_threshold),
        ("hold_threshold", hold_threshold),
        ("cascade_threshold", cascade_threshold),
        ("catalyst", catalyst),
    ):
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} must be in [0, 1]")

    trace: list[str] = []
    previous_pressure = 0.0
    reactivities: list[float] = []

    for node in nodes:
        effective_evidence = _clamp(node.evidence + catalyst * (1.0 - node.evidence))
        local = _clamp(node.activation * node.stability * effective_evidence)
        pressure = _clamp(previous_pressure * 0.50 + node.consequence * 0.50)
        local_after_pressure = _clamp(local * (1.0 - pressure))
        reactivities.append(local_after_pressure)
        previous_pressure = pressure
        trace.append(
            f"{node.name}:local={local_after_pressure:.6f}:"
            f"pressure={pressure:.6f}:inhibition={node.inhibition:.6f}"
        )

    weakest_index = min(range(len(nodes)), key=lambda i: reactivities[i])
    weakest = nodes[weakest_index]
    weakest_reactivity = reactivities[weakest_index]

    barrier = max(
        weakest.inhibition,
        1.0 - weakest.stability,
        1.0 - weakest.evidence,
    )
    cascade_pressure = previous_pressure

    if weakest.inhibition >= 0.35:
        mode: ReactionMode = "INHIBIT"
        reason = "hard_inhibitor"
    elif cascade_pressure >= cascade_threshold:
        mode = "HOLD"
        reason = "cascade_pressure"
    elif barrier >= hold_threshold:
        mode = "HOLD"
        reason = "activation_barrier"
    elif weakest_reactivity >= activation_threshold:
        mode = "PROCEED"
        reason = "chain_conditions_satisfied"
    else:
        mode = "UNKNOWN"
        reason = "insufficient_reactivity"

    trace.append(f"decision={mode}:reason={reason}")
    trace_tuple = tuple(trace)
    trace_canonical = json.dumps({"trace": trace_tuple}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    trace_digest = hashlib.sha256(trace_canonical.encode("utf-8")).hexdigest()
    return ReactionNetworkResult(
        mode=mode,
        network_reactivity=sum(reactivities) / len(reactivities),
        barrier=barrier,
        cascade_pressure=cascade_pressure,
        weakest_node=weakest.name,
        trace=trace_tuple,
        trace_digest=trace_digest,
    )
