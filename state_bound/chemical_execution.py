from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .chemical_reaction_network import ReactionNode, ReactionNetworkResult, evaluate_reaction_network


@dataclass(frozen=True)
class ReactionEnvironment:
    """Immutable execution snapshot used by the chemistry-inspired layer.

    This is an engineering control model. It is not a physical-chemistry model.
    The snapshot is deliberately explicit so the assessment can be replayed.
    """

    context: dict[str, Any]
    state: dict[str, Any]
    evidence: tuple[dict[str, Any], ...]
    trajectory: tuple[dict[str, Any], ...]
    activation: float
    inhibition: float
    catalyst: float = 0.0

    def __post_init__(self) -> None:
        for name in ("activation", "inhibition", "catalyst"):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0, 1]")


@dataclass(frozen=True)
class ReactionAssessment:
    environment_digest: str
    network: ReactionNetworkResult
    reaction_summary_digest: str
    state_transition_observation_required: bool


def _canonical(value: Any) -> str:
    import json
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    import hashlib
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _evidence_strength(evidence: tuple[dict[str, Any], ...]) -> float:
    if not evidence:
        return 0.0
    verified = sum(1 for item in evidence if item.get("verified") is True)
    return verified / len(evidence)


def _stability(value: Any) -> float:
    if not isinstance(value, dict):
        return 0.0
    if value.get("valid") is False or value.get("drift") is True:
        return 0.0
    return 1.0


def build_reaction_assessment(env: ReactionEnvironment) -> ReactionAssessment:
    """Turn one execution snapshot into a replayable reaction-network assessment.

    The returned summary describes the assessment only. It is not a
    post-transition state because this function performs no state mutation.
    """

    evidence_strength = _evidence_strength(env.evidence)
    context_stability = _stability(env.context)
    state_stability = _stability(env.state)
    trajectory_stability = 1.0 if env.trajectory else 0.0

    nodes: list[ReactionNode] = [
        ReactionNode(
            "context_activation",
            env.activation,
            env.inhibition,
            context_stability,
            evidence_strength,
            consequence=0.0,
        ),
        ReactionNode(
            "state_transition",
            env.activation,
            env.inhibition,
            state_stability,
            evidence_strength,
            consequence=0.0,
        ),
        ReactionNode(
            "trajectory_continuation",
            env.activation,
            env.inhibition,
            trajectory_stability,
            evidence_strength,
            consequence=min(1.0, len(env.trajectory) / 10.0),
        ),
    ]

    network = evaluate_reaction_network(tuple(nodes), catalyst=env.catalyst)
    snapshot = {
        "context": env.context,
        "state": env.state,
        "evidence": env.evidence,
        "trajectory": env.trajectory,
        "activation": env.activation,
        "inhibition": env.inhibition,
        "catalyst": env.catalyst,
    }
    environment_digest = _digest(snapshot)

    reaction_summary = {
        "environment_digest": environment_digest,
        "mode": network.mode,
        "weakest_node": network.weakest_node,
        "network_reactivity": network.network_reactivity,
        "barrier": network.barrier,
        "cascade_pressure": network.cascade_pressure,
        "trace": network.trace,
    }

    return ReactionAssessment(
        environment_digest=environment_digest,
        network=network,
        reaction_summary_digest=_digest(reaction_summary),
        state_transition_observation_required=network.mode in {"PROCEED", "HOLD", "INHIBIT"},
    )
