#!/usr/bin/env python3
"""Minimal, dependency-free, non-destructive Action Gate customer smoke test."""
from __future__ import annotations
import json, os, sys, urllib.error, urllib.request
BASE=os.getenv("ACTION_GATE_URL","http://localhost:8080").rstrip("/")
TOKEN=os.getenv("ACTION_GATE_API_TOKEN")
TENANT=os.getenv("ACTION_GATE_TENANT_ID","customer-acceptance")
ACTOR=os.getenv("ACTION_GATE_ACTOR_ID","acceptance-runner")
SESSION=os.getenv("ACTION_GATE_SESSION_ID","acceptance-smoke")
ACTION="example.read_only_check"
def request(method,path,payload=None):
    body=None if payload is None else json.dumps(payload).encode()
    headers={"Accept":"application/json"}
    if body is not None: headers["Content-Type"]="application/json"
    if TOKEN: headers["Authorization"]=f"Bearer {TOKEN}"
    req=urllib.request.Request(BASE+path,data=body,headers=headers,method=method)
    try:
        with urllib.request.urlopen(req,timeout=10) as r: return r.status,json.loads(r.read())
    except urllib.error.HTTPError as exc:
        detail=exc.read().decode(errors="replace")
        raise RuntimeError(f"{method} {path}: HTTP {exc.code}: {detail}") from exc
def fail(message):
    print(json.dumps({"status":"FAIL","error":message},sort_keys=True)); raise SystemExit(1)
def main():
    try:
        status,health=request("GET","/health")
        if status!=200 or health.get("status") not in {"ok","degraded"}: fail(f"health check failed: {health}")
        payload={"tenant_id":TENANT,"agent_id":"customer-acceptance-agent","actor_id":ACTOR,"session_id":SESSION,"action":ACTION,"target":"local://acceptance","parameters":{},"context":{"purpose":"acceptance-smoke"},"evidence":[{"source":"customer-acceptance-smoke","verified":True}]}
        _,decision=request("POST","/v1/action/evaluate",payload)
        required=["decision_id","tenant_id","nonce","action_hash","policy_hash"]
        missing=[k for k in required if not decision.get(k)]
        if missing: fail(f"decision missing required fields: {missing}")
        if decision.get("decision")!="ALLOW": fail("inert acceptance action was not allowed: "+str(decision.get("decision")))
        did=decision["decision_id"]
        execution={"tenant_id":TENANT,"actor_id":ACTOR,"session_id":SESSION,"action_hash":decision["action_hash"],"nonce":decision["nonce"],"outcome":{"status":"acceptance_smoke_ok","side_effect":False}}
        _,reserved=request("POST",f"/v1/action/{did}/execution/reserve",execution)
        if reserved.get("execution",{}).get("status")!="RESERVED": fail("execution reservation was not recorded")
        _,executed=request("POST",f"/v1/action/{did}/execution",execution)
        if executed.get("execution",{}).get("status")!="EXECUTED": fail("execution was not recorded as EXECUTED")
        _,evidence=request("GET",f"/v1/evidence/{did}?tenant_id={TENANT}")
        _,replay=request("GET",f"/v1/replay/{did}?tenant_id={TENANT}")
        if replay.get("match") is not True: fail(f"replay mismatch: {replay}")
        if not evidence.get("evidence_hash"): fail("evidence record has no evidence_hash")
        print(json.dumps({"status":"PASS","product":health.get("product"),"version":health.get("version"),"decision_id":did,"decision":decision.get("decision"),"execution":executed.get("execution",{}).get("status"),"replay_match":replay.get("match"),"policy_hash":decision.get("policy_hash"),"evidence_hash":evidence.get("evidence_hash")},sort_keys=True))
    except (RuntimeError,OSError,ValueError) as exc: fail(str(exc))
if __name__=="__main__": main()
