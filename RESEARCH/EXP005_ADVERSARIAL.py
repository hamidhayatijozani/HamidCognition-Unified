from __future__ import annotations
import copy, json
from pathlib import Path
from EXP004_VALIDATOR import validate_exp004

ROOT = Path(__file__).resolve().parent

def load_artifact():
    return json.loads((ROOT / "EXP004RESULT.json").read_text(encoding="utf-8"))

def valid(name, p):
    ok, errors = validate_exp004(p)
    if not ok: raise AssertionError(f"{name}: expected valid, got {errors}")

def invalid(name, p):
    ok, errors = validate_exp004(p)
    if ok: raise AssertionError(f"{name}: expected rejection")

def main():
    canonical = load_artifact(); valid("canonical", canonical)
    cases = {}
    p = copy.deepcopy(canonical); p["interpretation"]="SURVIVES_PRELIMINARY"; p["promotion"]="BLOCKED_PENDING_INDEPENDENT_REPRODUCTION"; p["primary_summary"]["all_snapshots_positive"]=True; cases["forged_survival_label"]=p
    p = copy.deepcopy(canonical); p["primary_summary"]["all_snapshots_positive"]=True; cases["forged_positive_aggregate"]=p
    p = copy.deepcopy(canonical)
    for name in ("snapshot_A", "snapshot_B"):
        s=p["snapshots"][name]["metrics"]["5"]; s["model_accuracy"]=s["majority_baseline_accuracy"]+0.01; s["accuracy_delta_vs_majority"]=0.01; s["cost_aware_return"]=0.01
    p["primary_summary"]["snapshot_deltas_vs_majority"]=[0.01,0.01]; p["primary_summary"]["all_snapshots_positive"]=True
    cases["both_snapshots_positive_but_falsified_label"]=p
    p = copy.deepcopy(canonical); p["snapshots"]["snapshot_A"]["metrics"]["5"]["accuracy_delta_vs_majority"]=0.01; cases["forged_delta"]=p
    p = copy.deepcopy(canonical); p["integrity"]["snapshots_disjoint"]=False; cases["overlap"]=p
    p = copy.deepcopy(canonical); p["snapshots"]["snapshot_B"]["metrics"]["5"]["integrity"]["future_features_used"]=True; cases["future_features"]=p
    p = copy.deepcopy(canonical); p["snapshots"]["snapshot_A"]["raw_sha256"]="tampered"; cases["tampered_fingerprint"]=p
    for name,p in cases.items(): invalid(name,p)
    p=copy.deepcopy(canonical)
    for name in ("snapshot_A","snapshot_B"):
        s=p["snapshots"][name]["metrics"]["5"]; s["model_accuracy"]=0.60; s["majority_baseline_accuracy"]=0.50; s["accuracy_delta_vs_majority"]=0.10; s["cost_aware_return"]=0.10
    p["primary_summary"]["snapshot_deltas_vs_majority"]=[0.10,0.10]; p["primary_summary"]["all_snapshots_positive"]=True; p["interpretation"]="SURVIVES_PRELIMINARY"; p["promotion"]="BLOCKED_PENDING_INDEPENDENT_REPRODUCTION"; valid("coherent_survival",p)
    print(json.dumps({"experiment":"EXP-005","status":"EXECUTED_ADVERSARIAL_VALIDATOR_TEST","cases_total":len(cases)+2,"malicious_or_inconsistent_cases_rejected":len(cases),"canonical_falsification_accepted":True,"coherent_survival_path_accepted":True,"validator_is_label_independent":True,"validator_derives_delta_from_accuracy":True,"result":"PASS","scope":"Registered mutation set only; not a proof of completeness."},indent=2,sort_keys=True))

if __name__ == "__main__": raise SystemExit(main())
