#!/usr/bin/env python3
"""Bounded evidence-first autonomous repair planner."""
from __future__ import annotations
import json, os, subprocess
from pathlib import Path
from datetime import datetime, timezone
REPO=os.environ["GITHUB_REPOSITORY"]
TARGETS=("MCP Ephemeral HTTPS E2E","Action Gate Production E2E Smoke","Broker Gateway Tests","Product Verification")
def gh(args):
    p=subprocess.run(["gh",*args],text=True,capture_output=True,check=True); return json.loads(p.stdout)
def main():
    plans=[]
    for wf in TARGETS:
        runs=gh(["run","list","--repo",REPO,"--workflow",wf,"--branch","main","--limit","1","--json","databaseId,status,conclusion,headSha,url"])
        if not runs: continue
        r=runs[0]
        if r.get("conclusion") in {"failure","timed_out","cancelled"}:
            plans.append({"workflow":wf,"run_id":r["databaseId"],"sha":r.get("headSha"),
                          "failure_class":"infrastructure" if r["conclusion"]!="failure" else "code_or_configuration",
                          "status":"PLAN_ONLY","requires_independent_verification":True})
    out={"timestamp":datetime.now(timezone.utc).isoformat(),"repository":REPO,"plans":plans,
         "safety":{"fail_closed":True,"forbidden_actions":["release","publish","secret_change","credential_change","payment_change"]}}
    Path("artifacts/autonomous").mkdir(parents=True,exist_ok=True)
    Path("artifacts/autonomous/repair_plan.json").write_text(json.dumps(out,indent=2),encoding="utf-8")
    print(json.dumps(out,indent=2))
if __name__=="__main__": main()
