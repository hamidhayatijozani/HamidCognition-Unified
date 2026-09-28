from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Literal
import hashlib, json

EpistemicState = Literal["KNOWN","UNKNOWN","CONFLICTED","STALE","UNVERIFIED"]
DecisionState = Literal["ALLOW","DENY","ASK","HOLD","SANDBOX","DEFER"]

def digest(value: Any) -> str:
    payload=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

@dataclass(frozen=True)
class WorldState:
    version:int
    trajectory:dict[str,Any]
    metadata:dict[str,Any]
    def trajectory_digest(self)->str: return digest(self.trajectory)

@dataclass(frozen=True)
class Decision:
    decision:DecisionState
    epistemic_state:EpistemicState
    world_version:int
    trajectory_digest:str
    reason:str=""

@dataclass(frozen=True)
class ExecutionAuthority:
    action:dict[str,Any]
    subject:str
    decision:Decision
    issued_at_ns:int
    expires_at_ns:int
    nonce:str
    @property
    def executable(self)->bool:
        return self.decision.decision=="ALLOW" and self.decision.epistemic_state=="KNOWN"
