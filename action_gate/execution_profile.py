from __future__ import annotations

from enterprise_models import EnterpriseArchitectureError, ExecutionProfile

DEFAULT_PROFILES = {
    "LOW": ExecutionProfile("low", "LOW", 1000, "minimal", False, False),
    "HIGH": ExecutionProfile("high", "HIGH", 500, "full", True, False),
    "CRITICAL": ExecutionProfile("critical", "CRITICAL", 500, "full", True, True),
}


class ExecutionProfileService:
    def __init__(self, profiles: dict[str, ExecutionProfile] | None = None) -> None:
        self._profiles = dict(profiles or DEFAULT_PROFILES)

    def get(self, risk_level: str) -> ExecutionProfile:
        try:
            return self._profiles[risk_level.upper()]
        except KeyError as exc:
            raise EnterpriseArchitectureError("execution_profile_not_defined") from exc

    def validate(self, profile: ExecutionProfile, *, evidence_complete: bool,
                 replay_available: bool, human_review: bool) -> None:
        if profile.requires_full_evidence() and not evidence_complete:
            raise EnterpriseArchitectureError("execution_profile_requires_full_evidence")
        if profile.replay_required and not replay_available:
            raise EnterpriseArchitectureError("execution_profile_requires_replay")
        if profile.human_review_required and not human_review:
            raise EnterpriseArchitectureError("execution_profile_requires_human_review")
