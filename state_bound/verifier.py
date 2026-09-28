from __future__ import annotations
from dataclasses import dataclass
from .models import ExecutionAuthority,WorldState

@dataclass(frozen=True)
class VerificationResult:
    status:str
    reason:str
    invariant_results:dict[str,bool]
    @property
    def executable(self)->bool: return self.status=="VALID"

def verify_authority(authority:ExecutionAuthority,*,current_world:WorldState,current_action:dict,subject:str,now_ns:int)->VerificationResult:
    decision=authority.decision
    invariants={
        "action_consistent":current_action==authority.action,
        "trajectory_consistent":current_world.version==decision.world_version and current_world.trajectory_digest()==decision.trajectory_digest,
        "context_consistent":not decision.context_digest or current_world.context_digest()==decision.context_digest,
        "state_consistent":not decision.state_digest or current_world.state_digest()==decision.state_digest,
        "authority_not_expired":authority.issued_at_ns<=now_ns<authority.expires_at_ns,
    }
    if authority.subject!=subject: return VerificationResult("INVALID","subject_mismatch",invariants)
    if not authority.executable: return VerificationResult("HOLD","authority_not_executable",invariants)
    if not all(invariants.values()):
        failed=",".join(k for k,v in invariants.items() if not v)
        return VerificationResult("INVALID",f"invariant_failed:{failed}",invariants)
    return VerificationResult("VALID","all_bound_invariants_hold",invariants)
