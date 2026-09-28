from __future__ import annotations
from .models import Decision, ExecutionAuthority, WorldState

def issue_authority(*, action: dict, world: WorldState, decision: Decision, nonce: str, subject: str = "test-subject", issued_at_ns: int = 1_000_000, ttl_ns: int = 1_000_000) -> ExecutionAuthority | None:
    if decision.epistemic_state != "KNOWN" or decision.decision != "ALLOW":
        return None
    if ttl_ns <= 0:
        raise ValueError("ttl_ns_must_be_positive")
    return ExecutionAuthority(
        action=action,
        subject=subject,
        decision=decision,
        authorized_world=world.fingerprint(),
        nonce=nonce,
        issued_at_ns=issued_at_ns,
        expires_at_ns=issued_at_ns + ttl_ns,
    )
