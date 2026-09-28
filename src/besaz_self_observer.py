"""Bounded self-observation for BESAZ.

The observer may inspect and propose work. It cannot grant authority or mutate
contracts. This is the first safe activation of the architecture against itself.
"""
from __future__ import annotations
from datetime import datetime, timezone
from .awareness_integration import build_besaz_registry, BESAZ_BINDINGS

def observe() -> dict:
    registry=build_besaz_registry()
    components=[]
    proposals=[]
    for c in registry.contracts.values():
        state=registry.component(c.component_id).snapshot()
        components.append({
            "component_id": c.component_id,
            "parent_id": c.parent_id,
            "maturity": c.maturity.value,
            "status": state["state"]["status"],
            "evidence_refs": state["evidence_refs"],
            "capabilities": list(c.capabilities),
            "limits": list(c.limits),
        })
        if c.maturity.value in {"SPECIFIED","PROTOTYPE"}:
            proposals.append({
                "component_id": c.component_id,
                "type": "VERIFY_OR_IMPLEMENT",
                "reason": f"maturity={c.maturity.value}",
                "next_action": "attach evidence or implement the next bounded capability",
            })
        if not state["evidence_refs"]:
            proposals.append({
                "component_id": c.component_id,
                "type": "EVIDENCE_GAP",
                "reason": "no evidence reference recorded in current runtime state",
                "next_action": "run a bounded verification task and record its evidence",
            })
    return {
        "project": "BESAZ",
        "observation_time": datetime.now(timezone.utc).isoformat(),
        "mode": "SELF_OBSERVE_ONLY",
        "authority": "NONE",
        "components": components,
        "bindings": [b.__dict__ for b in BESAZ_BINDINGS],
        "proposals": proposals,
        "hard_boundary": "self-observation cannot execute, self-upgrade, self-grant authority, or rewrite contracts",
    }

if __name__ == "__main__":
    import json
    print(json.dumps(observe(), ensure_ascii=False, indent=2, sort_keys=True))
