from src.awareness_components import canonical_contracts
from src.awareness_registry import AwarenessRegistry
from src.awareness_supervisor import AwarenessSupervisor

def test_canonical_tree_is_valid():
    registry=AwarenessRegistry(canonical_contracts())
    assert len(registry.contracts)==15
    assert len(registry.children("ROOT"))==4

def test_descendants_preserve_hierarchy():
    registry=AwarenessRegistry(canonical_contracts())
    ids={c.component_id for c in registry.descendants("COGNITION")}
    assert {"SELF-MODEL","CREATOR-CONTEXT","MARKET-INTELLIGENCE","REASONING"}<=ids

def test_supervisor_routes_authorized_need():
    supervisor=AwarenessSupervisor(AwarenessRegistry(canonical_contracts()))
    result=supervisor.process("MARKET-INTELLIGENCE",lambda:[{"stale":True}],lambda o:"research_market" if o["stale"] else None)
    assert result["decisions"][0]["mode"]=="EXECUTE"

def test_unauthorized_need_escalates():
    supervisor=AwarenessSupervisor(AwarenessRegistry(canonical_contracts()))
    result=supervisor.process("SELF-MODEL",lambda:[{"danger":True}],lambda o:"delete" if o["danger"] else None)
    assert result["decisions"][0]["mode"]=="ESCALATE"
