"""Registry and supervisor primitives for the hierarchical awareness layer."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from .awareness_layer import AwarenessContract, AwarenessComponent, hierarchy_valid

@dataclass(frozen=True)
class SupervisorDecision:
    component_id: str
    action: str
    reason: str
    mode: str

class AwarenessRegistry:
    def __init__(self, contracts: Iterable[AwarenessContract]):
        self.contracts={c.component_id:c for c in contracts}
        if not hierarchy_valid(self.contracts.values()):
            raise ValueError("invalid awareness hierarchy")
        self.components={cid:AwarenessComponent(c) for cid,c in self.contracts.items()}

    def component(self, component_id:str)->AwarenessComponent:
        return self.components[component_id]

    def children(self,parent_id:str):
        return [c for c in self.contracts.values() if c.parent_id==parent_id]

    def descendants(self,parent_id:str):
        result=[]
        stack=[parent_id]
        while stack:
            current=stack.pop()
            kids=self.children(current)
            result.extend(kids)
            stack.extend(c.component_id for c in kids)
        return result

    def health(self):
        return {
            cid:{
                "status":component.state.status,
                "needs":list(component.state.detected_needs),
                "pending_actions":list(component.state.pending_actions),
                "evidence_refs":list(component.state.evidence_refs),
            } for cid,component in self.components.items()
        }

    def route_need(self,component_id:str,need:str)->SupervisorDecision:
        component=self.component(component_id)
        for permission in component.contract.permissions:
            if permission.action==need:
                return SupervisorDecision(component_id,need,"authorized local capability",permission.mode.value)
        parent=component.contract.parent_id
        if parent!="ROOT":
            return SupervisorDecision(parent,need,f"child {component_id} lacks authority; escalate to parent","ESCALATE")
        return SupervisorDecision("HUMAN_APPROVAL",need,f"no authorized route for {component_id}:{need}","ESCALATE")
