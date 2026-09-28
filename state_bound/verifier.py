from __future__ import annotations

from dataclasses import dataclass

from .models import ExecutionAuthority, WorldState


@dataclass(frozen=True)
class VerificationResult:
    status: str
    reason: str
    invariant_results: dict[str, bool]

    @property
    def executable(self) -> bool:
        return self.status == "VALID"


def verify_authority(
    authority: ExecutionAuthority,
    *,
    current_world: WorldState,
    current_action: dict,
    subject: str,
    now_ns: int,
) -> VerificationResult:
    decision = authority.decision
    invariants = {
        "action_consistent": current_action == authority.action,
        "trajectory_consistent": (
            current_world.version == decision.world_version
            and current_world.trajectory_digest() == decision.trajectory_digest
        ),
        "context_consistent": (
            not decision.context_digest
            or current_world.context_digest() == decision.context_digest
        ),
        "state_consistent": (
            not decision.state_digest
            or current_world.state_digest() == decision.state_digest
        ),
        "evidence_consistent": (
            not decision.evidence_digest
            or current_world.evidence_digest() == decision.evidence_digest
        ),
        "authority_not_expired": authority.issued_at_ns <= now_ns < authority.expires_at_ns,
    }

    if authority.subject != subject:
        return VerificationResult("INVALID", "subject_mismatch", invariants)

    if not authority.executable:
        return VerificationResult("HOLD", "authority_not_executable", invariants)

    if not all(invariants.values()):
        failed = [key for key, value in invariants.items() if not value]

        # Loss of evidence or live state makes authority epistemically unsafe.
        if "evidence_consistent" in failed or "state_consistent" in failed:
            return VerificationResult(
                "UNKNOWN",
                "epistemic_state_invalidated:" + ",".join(failed),
                invariants,
            )

        # Context and trajectory drift require re-evaluation, not a silent deny.
        return VerificationResult(
            "HOLD",
            "re_evaluation_required:" + ",".join(failed),
            invariants,
        )

    return VerificationResult("VALID", "all_bound_invariants_hold", invariants)
