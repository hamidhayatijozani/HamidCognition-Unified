#!/usr/bin/env python3
"""Verify that CI evidence is internally coherent before a PASS claim."""
from __future__ import annotations
import json, os, subprocess
REPO=os.environ.get("GITHUB_REPOSITORY","")
TARGETS=("MCP Ephemeral HTTPS E2E","Action Gate Production E2E Smoke","Broker Gateway Tests","Product Verification")

def gh(args):
    p=subprocess.run(["gh",*args],text=True,capture_output=True,check=True)
    return json.loads(p.stdout)

def main():
    report=[]
    for name in TARGETS:
        runs=gh(["run","list","--repo",REPO,"--workflow",name,"--branch","main","--limit","3",
                 "--json","databaseId,status,conclusion,headSha,createdAt,url"])
        if not runs:
            report.append({"workflow":name,"status":"UNPROVEN","reason":"no_run"})
            continue
        r=runs[0]
        report.append({"workflow":name,"run_id":r["databaseId"],"sha":r.get("headSha"),
                       "status":r.get("status"),"conclusion":r.get("conclusion"),
                       "verified_pass":r.get("status")=="completed" and r.get("conclusion")=="success",
                       "url":r.get("url")})
    # A truth gate reports facts; it does not manufacture a release verdict.
    out={"repository":REPO,"targets":report,
         "release_claim_allowed":False,
         "rule":"exact source SHA + workflow evidence + artifact/release evidence must agree"}
    os.makedirs("artifacts/autonomous",exist_ok=True)
    with open("artifacts/autonomous/evidence_truth.json","w",encoding="utf-8") as f:
        json.dump(out,f,indent=2,ensure_ascii=False)
    print(json.dumps(out,indent=2,ensure_ascii=False))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
