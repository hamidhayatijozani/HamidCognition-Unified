"""Capability boundary for the chemistry-inspired reaction assessor.

The module exposes only pure data contracts and a pure assessment function.
It has no import path into Action Gate and no execution capability.
Action Gate may consume the resulting assessment; the reaction layer cannot
authorize, reserve, execute, approve, or mutate external state.
"""

from dataclasses import dataclass
from typing import Any, Mapping

from .chemical_execution import ReactionAssessment, ReactionEnvironment, build_reaction_assessment


@dataclass(frozen=True)
class ReactionAssessmentRequest:
    environment: ReactionEnvironment


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
        "reaction_summary_digest": result.post_reaction_digest,
        "trace": tuple(result.network.trace),
    }
