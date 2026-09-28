from src.awareness_integration import build_besaz_registry, system_health
from src.awareness_policy import Decision, authorize, execute_if_authorized
from src.awareness_layer import ActionPermission, ActionMode, AwarenessContract, Maturity, hierarchy_valid

def test_besaz_registry_has_full_tree():
    registry=build_besaz_registry()
    assert len(registry.contracts)==15
    assert system_health(registry)["project"]=="BESAZ"
    assert system_health(registry)["bindings"]==15

def test_cycle_is_rejected():
    a=AwarenessContract("A","B","a",Maturity.VERIFIED,(),(),(),(),())
    b=AwarenessContract("B","A","b",Maturity.VERIFIED,(),(),(),(),())
    assert not hierarchy_valid([a,b])

def test_approval_gate_blocks_execution_until_approved():
    c=AwarenessContract("A","ROOT","a",Maturity.VERIFIED,(),(),(),(),(
        ActionPermission("publish",ActionMode.EXECUTE,reversible=False,requires_approval=True),
    ))
    from src.awareness_layer import AwarenessComponent
    component=AwarenessComponent(c)
    assert authorize(component,"publish").decision is Decision.PROPOSE
    assert authorize(component,"publish",approval=True).decision is Decision.ALLOW

def test_propose_is_not_execute():
    c=AwarenessContract("A","ROOT","a",Maturity.VERIFIED,(),(),(),(),(
        ActionPermission("update",ActionMode.PROPOSE),
    ))
    from src.awareness_layer import AwarenessComponent
    assert authorize(AwarenessComponent(c),"update").decision is Decision.PROPOSE

def test_unknown_need_escalates_to_parent():
    registry=build_besaz_registry()
    decision=registry.route_need("SELF-MODEL","unrecognized_action")
    assert decision.mode=="ESCALATE"
    assert decision.component_id=="COGNITION"

def test_authorized_execution_records_evidence():
    registry=build_besaz_registry()
    component=registry.component("VERIFICATION")
    result=execute_if_authorized(component,"verify","evidence:test-001")
    assert result.decision is Decision.ALLOW
    assert component.state.status=="VERIFIED"
    assert "evidence:test-001" in component.state.evidence_refs
