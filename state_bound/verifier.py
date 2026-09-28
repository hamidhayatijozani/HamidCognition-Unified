from __future__ import annotations
from dataclasses import dataclass
from .models import ExecutionAuthority, WorldState, digest

INVARIANTS = ("action","context","state","evidence","trajectory","environment","policy")

@dataclass(frozen=True)
class VerificationResult:
    status: str
    reasons: tuple[str,...]
    latency_us: float = 0.0
    @property
    def executable(self) -> bool:
        return self.status == "VALID"

def verify_authority(authority: ExecutionAuthority, *, action: dict, current_world: WorldState, consumed_nonces: set[str] | None = None, now_ns: int = 1_000_000) -> VerificationResult:
    import time
    start=time.perf_counter_ns()
    reasons=[]
    if not current_world.freshness_valid(now_ns):
        reasons.append("current_world_stale")
    if not authority.executable:
        reasons.append("decision_or_epistemic_state_not_executable")
    if not (authority.issued_at_ns <= now_ns < authority.expires_at_ns):
        reasons.append("authority_expired_or_not_yet_valid")
    if digest(action) != digest(authority.action):
        reasons.append("action_invariant_failed")
    current=current_world.fingerprint()
    for key in INVARIANTS[1:]:
        if current[key] != authority.authorized_world[key]:
            reasons.append(f"{key}_invariant_failed")
    if consumed_nonces is not None and authority.nonce in consumed_nonces:
        reasons.append("replay_detected")
    latency_us=(time.perf_counter_ns()-start)/1000
    return VerificationResult("INVALID" if reasons else "VALID",tuple(reasons),latency_us)

def execute_once(authority: ExecutionAuthority, *, action: dict, current_world: WorldState, consumed_nonces: set[str], now_ns: int = 1_000_000) -> VerificationResult:
    result=verify_authority(authority,action=action,current_world=current_world,consumed_nonces=consumed_nonces,now_ns=now_ns)
    if result.executable:
        consumed_nonces.add(authority.nonce)
    return result
