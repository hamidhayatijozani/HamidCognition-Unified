"""Typed capability boundary for the chemistry-inspired reaction assessor.

The module exposes pure data contracts and pure assessment functions.
It has no import path into Action Gate and no execution capability.
Action Gate consumes the typed assessment and remains the execution authority.
"""


from dataclasses import dataclass
from typing import Any, Mapping

from .chemical_execution import ReactionAssessment, ReactionEnvironment, build_reaction_assessment


@dataclass(frozen=True)
class ReactionAssessmentRequest:
    environment: ReactionEnvironment


@dataclass(frozen=True)
class ReactionPolicyInput:
    assessment: ReactionAssessment
    override_requested: bool = False
    override_reason: str | None = None


def assess_reaction(request: ReactionAssessmentRequest) -> ReactionAssessment:
    return build_reaction_assessment(request.environment)


def assessment_record(result: ReactionAssessment) -> Mapping[str, Any]:
    return {
        "mode": result.network.mode,
        "network_reactivity": result.network.network_reactivity,
        "barrier": result.network.barrier,
        "cascade_pressure": result.network.cascade_pressure,
        "weakest_node": result.network.weakest_node,
        "environment_digest": result.environment_digest,
        "reaction_summary_digest": result.reaction_summary_digest,
        "state_transition_observation_required": result.state_transition_observation_required,
        "trace": list(result.network.trace),
    }
