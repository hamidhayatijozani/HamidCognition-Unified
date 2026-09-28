from __future__ import annotations

from .models import Decision, ExecutionAuthority, WorldState


def issue_authority(
    *,
    action: dict,
    world: WorldState,
    decision: Decision,
    nonce: str,
) -> ExecutionAuthority | None:
    # UNKNOWN, CONFLICTED, STALE and UNVERIFIED can never mint execution authority.
    if decision.epistemic_state != "KNOWN" or decision.decision != "ALLOW":
        return None
    return ExecutionAuthority(
        action=action,
        decision=decision,
        authorized_world=world.fingerprint(),
        nonce=nonce,
    )
