from .models import Decision,ExecutionAuthority

def issue_authority(*,action:dict,subject:str,decision:Decision,nonce:str,issued_at_ns:int,expires_at_ns:int)->ExecutionAuthority|None:
    if decision.decision!="ALLOW" or decision.epistemic_state!="KNOWN": return None
    if expires_at_ns<=issued_at_ns: raise ValueError("expiry_must_follow_issue_time")
    return ExecutionAuthority(action,subject,decision,issued_at_ns,expires_at_ns,nonce)
