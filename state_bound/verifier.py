from __future__ import annotations
from dataclasses import dataclass
from .models import ExecutionAuthority,WorldState

@dataclass(frozen=True)
class VerificationResult:
    status:str
    reason:str
    invariant_results:dict[str,bool]
    @property
    def executable(self)->bool:
        return self.status=="VALID"

def verify_authority(authority:ExecutionAuthority,*,current_world:WorldState,current_action:dict,subject:str,now_ns:int)->VerificationResult:
    decision=authority.decision
    if authority.subject!=subject:
        return VerificationResult("INVALID","subject_mismatch",{})
    if current_action!=authority.action:
        return VerificationResult("INVALID","action_mismatch",{"action_consistent":False})
    if not authority.executable:
        return VerificationResult("HOLD","authority_not_executable",{})

    trajectory_ok=current_world.version==decision.world_version and current_world.trajectory_digest()==decision.trajectory_digest
    context_ok=not decision.context_digest or current_world.context_digest()==decision.context_digest
    state_ok=not decision.state_digest or current_world.state_digest()==decision.state_digest
    evidence_ok=not decision.evidence_digest or current_world.evidence_digest()==decision.evidence_digest
    expiry_ok=authority.issued_at_ns<=now_ns<authority.expires_at_ns

    if not expiry_ok:
        return VerificationResult("INVALID","authority_expired",{"authority_not_expired":False})
    if not trajectory_ok:
        return VerificationResult("HOLD","trajectory_consistent_changed",{"trajectory_consistent":False})
    if not context_ok:
        return VerificationResult("HOLD","context_consistent_changed",{"context_consistent":False})
    if not state_ok:
        return VerificationResult("UNKNOWN","state_consistent_changed",{"state_consistent":False})
    if not evidence_ok:
        return VerificationResult("UNKNOWN","evidence_consistent_changed",{"evidence_consistent":False})

    return VerificationResult("VALID","all_bound_invariants_hold",{"action_consistent":True,"trajectory_consistent":True,"context_consistent":True,"state_consistent":True,"evidence_consistent":True,"authority_not_expired":True})
