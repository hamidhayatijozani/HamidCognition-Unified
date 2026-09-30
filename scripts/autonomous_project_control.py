#!/usr/bin/env python3
"""Evidence-bound autonomous project controller.

Never declares a product/release PASS from a single workflow. It observes the
latest runs, classifies failures, records durable failure memory, and emits a
machine-readable next-action plan for CI.
"""
from __future__ import annotations
import json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

REPO=os.environ.get("GITHUB_REPOSITORY","")
WORKFLOWS=("MCP Ephemeral HTTPS E2E","Action Gate Production E2E Smoke","Broker Gateway Tests","Product Verification")
STATE=Path(os.environ.get("AUTONOMOUS_STATE_DIR","artifacts/autonomous"))
STATE.mkdir(parents=True,exist_ok=True)
MEMORY=STATE/"failure_memory.jsonl"

def gh(args:list[str]):
    p=subprocess.run(["gh",*args],text=True,capture_output=True,check=True)
    return json.loads(p.stdout)

def observe():
    rows=[]
    for workflow in WORKFLOWS:
        data=gh(["run","list","--repo",REPO,"--workflow",workflow,"--branch","main","--limit","5",
                 "--json","databaseId,status,conclusion,headSha,createdAt,url,name"])
        latest=data[0] if data else {}
        rows.append({"workflow":workflow,"runs":data,"latest":latest})
    return rows

def classify(row):
    r=row["latest"]
    c=r.get("conclusion")
    s=r.get("status")
    if not r: return "MISSING_RUN"
    if s in {"queued","in_progress","waiting","requested","pending"}: return "ACTIVE"
    if c=="success": return "PASS"
    if c in {"failure","timed_out","cancelled","startup_failure"}: return "FAILED"
    return "UNKNOWN"

def main():
    observed=observe()
    actions=[]
    now=datetime.now(timezone.utc).isoformat()
    for row in observed:
        state=classify(row)
        latest=row["latest"]
        if state=="FAILED":
            actions.append({"type":"RETRY_FAILED_JOBS","workflow":row["workflow"],"run_id":latest["databaseId"],
                            "reason":"recoverable_ci_failure"})
            entry={"timestamp":now,"workflow":row["workflow"],"run_id":latest["databaseId"],
                   "sha":latest.get("headSha"),"conclusion":latest.get("conclusion"),
                   "url":latest.get("url"),"action":"RETRY_FAILED_JOBS"}
            with MEMORY.open("a",encoding="utf-8") as f: f.write(json.dumps(entry,ensure_ascii=False)+"\n")
        elif state=="MISSING_RUN":
            actions.append({"type":"OBSERVE","workflow":row["workflow"],"reason":"no_run_found"})
        elif state=="ACTIVE":
            actions.append({"type":"WAIT","workflow":row["workflow"],"run_id":latest.get("databaseId")})
    result={"timestamp":now,"repository":REPO,"observed":observed,"actions":actions,
            "policy":{"pass_requires_same_sha_evidence":True,"release_claim_requires_artifact":True}}
    (STATE/"control_state.json").write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({"actions":actions,"state_file":str(STATE/"control_state.json")},ensure_ascii=False,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
