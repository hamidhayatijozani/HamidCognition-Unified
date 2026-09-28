from src.awareness_layer import ActionMode,ActionPermission,AwarenessComponent,AwarenessContract,Maturity,audit_record,hierarchy_valid

def contract(component_id,parent_id="ROOT"):
    return AwarenessContract(component_id,parent_id,"test",Maturity.VERIFIED,("staleness",),("stale",),("refresh",),("no destructive actions",),(ActionPermission("refresh",ActionMode.EXECUTE),ActionPermission("publish",ActionMode.PROPOSE,requires_approval=True)),"HUMAN_APPROVAL")

def test_hierarchy_is_valid():
    assert hierarchy_valid([contract("A"),contract("B","A")])

def test_hierarchy_rejects_missing_parent():
    assert not hierarchy_valid([contract("B","MISSING")])

def test_component_detects_need_and_executes_authorized_action():
    c=AwarenessComponent(contract("A"),observer=lambda:[{"staleness":True}])
    c.observe(); assert c.detect_need(lambda o:"refresh" if o["staleness"] else None)==["refresh"]
    assert c.request_action("refresh").mode is ActionMode.EXECUTE
    c.complete_action("refresh","evidence:refresh-001"); assert c.state.status=="VERIFIED"

def test_unauthorized_action_is_rejected():
    c=AwarenessComponent(contract("A"))
    try: c.request_action("delete_everything")
    except PermissionError: pass
    else: raise AssertionError("unauthorized action was accepted")

def test_audit_record_is_hashed():
    r=audit_record(AwarenessComponent(contract("A")),"initialized")
    assert len(r["record_hash"])==64 and len(r["contract_hash"])==64
