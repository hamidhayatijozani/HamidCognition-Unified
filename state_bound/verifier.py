from __future__ import annotations

from dataclasses import dataclass
from .models import ExecutionAuthority, WorldState, digest

INVARIANTS = ("action", "context", "state", "evidence", "trajectory", "environment", "policy")

@dataclass(frozen=True)
class VerificationResult:
    status: str
    reasons: tuple[str, ...]
    latency_us: float = 0.0

    @property
    def executable(self) -> bool:
        return self.status == "VALID"

def verify_authority(authority: ExecutionAuthority, *, action: dict, current_world: WorldState, consumed_nonces: set[str] | None = None) -> VerificationResult:
    import time
    start = time.perf_counter_ns()
    reasons = []
    if not authority.executable:
        reasons.append("decision_or_epistemic_state_not_executable")
    if digest(action) != digest(authority.action):
        reasons.append("action_invariant_failed")
    current = current_world.fingerprint()
    for key in INVARIANTS[1:]:
        if current[key] != authority.authorized_world[key]:
            reasons.append(f"{key}_invariant_failed")
    if consumed_nonces is not None and authority.nonce in consumed_nonces:
        reasons.append("replay_detected")
    latency_us = (time.perf_counter_ns() - start) / 1000
    if reasons:
        return VerificationResult("INVALID", tuple(reasons), latency_us)
    return VerificationResult("VALID", (), latency_us)

def execute_once(authority: ExecutionAuthority, *, action: dict, current_world: WorldState, consumed_nonces: set[str]) -> VerificationResult:
    result = verify_authority(authority, action=action, current_world=current_world, consumed_nonces=consumed_nonces)
    if result.executable:
        consumed_nonces.add(authority.nonce)
    return result
