"""Execution policy for bounded awareness actions in BESAZ."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from .awareness_layer import ActionPermission, ActionMode, AwarenessComponent

class Decision(str, Enum):
    ALLOW="ALLOW"; PROPOSE="PROPOSE"; ESCALATE="ESCALATE"; DENY="DENY"

@dataclass(frozen=True)
class Authorization:
    decision: Decision
    component_id: str
    action: str
    reason: str
    approval_required: bool = False

def authorize(component: AwarenessComponent, action: str, approval: bool=False) -> Authorization:
    permission: ActionPermission|None = component.contract.permission_for(action)
    if permission is None:
        return Authorization(Decision.DENY, component.contract.component_id, action, "action is outside contract")
    if permission.mode is ActionMode.ESCALATE:
        return Authorization(Decision.ESCALATE, component.contract.component_id, action, "contract requires escalation")
    if permission.mode is ActionMode.PROPOSE:
        return Authorization(Decision.PROPOSE, component.contract.component_id, action, "action is proposal-only")
    if permission.requires_approval and not approval:
        return Authorization(Decision.PROPOSE, component.contract.component_id, action, "explicit approval required", True)
    return Authorization(Decision.ALLOW, component.contract.component_id, action, "authorized for execution", permission.requires_approval)

def execute_if_authorized(component: AwarenessComponent, action: str, evidence_ref: str|None=None, approval: bool=False) -> Authorization:
    decision=authorize(component, action, approval)
    if decision.decision is not Decision.ALLOW:
        raise PermissionError(f"{decision.decision.value}: {decision.reason}")
    component.request_action(action)
    component.complete_action(action, evidence_ref)
    return decision
