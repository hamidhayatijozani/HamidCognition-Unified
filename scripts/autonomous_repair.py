#!/usr/bin/env python3
"""Deterministic autonomous recovery: retry infrastructure failures, preserve code-failure evidence."""
from __future__ import annotations
import json, os, subprocess
from pathlib import Path
REPO=os.environ["GITHUB_REPOSITORY"]
def run(cmd): return subprocess.run(cmd,text=True,capture_output=True)
def main():
    p=Path("artifacts/autonomous/repair_plan.json")
    plan=json.loads(p.read_text()) if p.exists() else {"plans":[]}
    results=[]
    for item in plan["plans"]:
        rid=str(item["run_id"])
        if item["failure_class"]=="infrastructure":
            x=run(["gh","run","rerun",rid,"--repo",REPO,"--failed"])
            results.append({"run_id":rid,"action":"rerun_failed_jobs","exit_code":x.returncode})
        else:
            x=run(["gh","run","view",rid,"--repo",REPO,"--log-failed"])
            Path(f"artifacts/autonomous/failure_{rid}.log").write_text(x.stdout+x.stderr,encoding="utf-8")
            results.append({"run_id":rid,"action":"collect_failure_evidence","exit_code":x.returncode})
    Path("artifacts/autonomous/repair_results.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
    print(json.dumps(results,indent=2))
if __name__=="__main__": main()
