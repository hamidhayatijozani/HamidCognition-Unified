"""Hierarchical awareness contracts for HamidCognition."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256
import json
from typing import Any, Callable, Iterable

class Maturity(str, Enum):
    SPECIFIED="SPECIFIED"; PROTOTYPE="PROTOTYPE"; VERIFIED="VERIFIED"; PRODUCTION="PRODUCTION"

class ActionMode(str, Enum):
    OBSERVE="OBSERVE"; PROPOSE="PROPOSE"; EXECUTE="EXECUTE"; ESCALATE="ESCALATE"

@dataclass(frozen=True)
class ActionPermission:
    action: str
    mode: ActionMode
    reversible: bool = True
    requires_approval: bool = False

@dataclass
class AwarenessState:
    status: str = "READY"
    observations: list[dict[str,Any]] = field(default_factory=list)
    detected_needs: list[str] = field(default_factory=list)
    pending_actions: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    last_error: str|None = None

@dataclass(frozen=True)
class AwarenessContract:
    component_id: str
    parent_id: str
    purpose: str
    maturity: Maturity
    observables: tuple[str,...]
    triggers: tuple[str,...]
    capabilities: tuple[str,...]
    limits: tuple[str,...]
    permissions: tuple[ActionPermission,...]
    escalation_target: str|None = None
    def permission_for(self, action:str):
        return next((p for p in self.permissions if p.action==action), None)

class AwarenessComponent:
    def __init__(self, contract:AwarenessContract, observer:Callable[[],Iterable[dict[str,Any]]]|None=None):
        self.contract=contract; self.state=AwarenessState(); self._observer=observer
    def observe(self):
        self.state.observations=[] if self._observer is None else [dict(x) for x in self._observer()]
        self.state.status="OBSERVED"; return self.state.observations
    def detect_need(self,predicate:Callable[[dict[str,Any]],str|None]):
        needs=[n for o in self.state.observations if (n:=predicate(o))]
        self.state.detected_needs=list(dict.fromkeys(needs))
        self.state.status="NEED_DETECTED" if needs else "READY"; return self.state.detected_needs
    def request_action(self,action:str):
        permission=self.contract.permission_for(action)
        if permission is None: raise PermissionError(f"{self.contract.component_id} is not authorized for {action}")
        self.state.pending_actions.append(action); return permission
    def complete_action(self,action:str,evidence_ref:str|None=None):
        if action in self.state.pending_actions: self.state.pending_actions.remove(action)
        if not evidence_ref and self.contract.maturity in (Maturity.VERIFIED, Maturity.PRODUCTION):
            self.state.status="ACTION_COMPLETED"
            raise PermissionError(f"{self.contract.component_id} requires evidence for completion")
        if evidence_ref and not str(evidence_ref).strip():
            raise PermissionError(f"{self.contract.component_id} requires a non-empty evidence reference")
        if evidence_ref: self.state.evidence_refs.append(evidence_ref)
        self.state.status="VERIFIED" if evidence_ref else "ACTION_COMPLETED"
    def escalate(self,reason:str):
        self.state.last_error=reason; self.state.status="ESCALATED"
        return self.contract.escalation_target or "HUMAN_APPROVAL"
    def snapshot(self):
        return {"component_id":self.contract.component_id,"parent_id":self.contract.parent_id,"maturity":self.contract.maturity.value,"state":self.state.__dict__.copy()}

def hierarchy_valid(contracts:Iterable[AwarenessContract])->bool:
    items=list(contracts); ids={c.component_id for c in items}
    if len(ids)!=len(items): return False
    if not all(c.component_id!=c.parent_id and (c.parent_id=="ROOT" or c.parent_id in ids) for c in items):
        return False
    parents={c.component_id:c.parent_id for c in items}
    for start in ids:
        seen=set()
        current=start
        while current!="ROOT":
            if current in seen: return False
            seen.add(current)
            current=parents.get(current)
            if current is None: return False
    return True

def canonical_hash(value:Any)->str:
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def audit_record(component:AwarenessComponent,event:str):
    snapshot=component.snapshot()
    contract={"component_id":component.contract.component_id,"parent_id":component.contract.parent_id,"purpose":component.contract.purpose,"maturity":component.contract.maturity.value,"observables":component.contract.observables,"triggers":component.contract.triggers,"capabilities":component.contract.capabilities,"limits":component.contract.limits,"permissions":[p.__dict__ | {"mode":p.mode.value} for p in component.contract.permissions]}
    record={"event":event,"component":snapshot,"contract_hash":canonical_hash(contract)}
    record["record_hash"]=canonical_hash(record); return record
