#!/usr/bin/env python3
"""Static product-drift checks for mandatory Action Gate boundaries."""
from __future__ import annotations
from pathlib import Path
import json, os

checks={
"oanda_authority":"broker_runtime/oanda.py",
"mcp_e2e":"scripts/mcp_e2e_smoke.py",
"completion_control":"PRODUCT/PRODUCT_COMPLETION_CONTROL.md",
"customer_acceptance":"PRODUCT/CUSTOMER_ACCEPTANCE.md",
}
required={
"broker_runtime/oanda.py":("enforce_execution_authority","authority_token"),
"scripts/mcp_e2e_smoke.py":("protected_read_public_file","protected_production_delete","get_action_gate_evidence"),
"PRODUCT/PRODUCT_COMPLETION_CONTROL.md":("same source SHA","artifact digest"),
"PRODUCT/CUSTOMER_ACCEPTANCE.md":("replay","tenant-tampering","policy-binding-tampering"),
}
def main():
    results=[]
    for label,path in checks.items():
        p=Path(path)
        text=p.read_text(encoding="utf-8") if p.exists() else ""
        missing=[x for x in required.get(path,()) if x not in text]
        results.append({"check":label,"path":path,"exists":p.exists(),"missing":missing,
                        "status":"PASS" if p.exists() and not missing else "DRIFT"})
    out={"results":results,"drift_detected":any(x["status"]=="DRIFT" for x in results)}
    os.makedirs("artifacts/autonomous",exist_ok=True)
    Path("artifacts/autonomous/product_drift.json").write_text(json.dumps(out,indent=2),encoding="utf-8")
    print(json.dumps(out,indent=2))
    return 1 if out["drift_detected"] else 0
if __name__=="__main__":
    raise SystemExit(main())
