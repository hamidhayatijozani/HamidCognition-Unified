from __future__ import annotations
from dataclasses import dataclass
from .models import ExecutionAuthority,WorldState,digest

@dataclass(frozen=True)
class VerificationResult:
    status:str
    reason:str
    invariant_results:dict[str,bool]
    @property
    def executable(self)->bool: return self.status=="VALID"

def verify_authority(authority:ExecutionAuthority,*,current_world:WorldState,current_action:dict,subject:str,now_ns:int)->VerificationResult:
    invariants={"action_consistent":digest(current_action)==digest(authority.action),"trajectory_consistent":current_world.version==authority.decision.world_version and current_world.trajectory_digest()==authority.decision.trajectory_digest,"authority_not_expired":authority.issued_at_ns<=now_ns<authority.expires_at_ns}
    if authority.subject!=subject: return VerificationResult("INVALID","subject_mismatch",invariants)
    if not authority.executable: return VerificationResult("HOLD","authority_not_executable",invariants)
    if not all(invariants.values()):
        failed=",".join(k for k,v in invariants.items() if not v)
        return VerificationResult("INVALID",f"invariant_failed:{failed}",invariants)
    return VerificationResult("VALID","all_ta001_invariants_hold",invariants)
