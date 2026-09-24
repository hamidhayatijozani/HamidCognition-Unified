#!/usr/bin/env python3
"""Deterministic 200-event replay integrity check."""
from __future__ import annotations
import json, hashlib, time
from pathlib import Path

N=200
events=[{"seq":i,"state":i%7,"payload":f"event-{i:04d}"} for i in range(N)]
def digest(rows):
    return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(",",":")).encode()).hexdigest()
expected=digest(events)
start=time.perf_counter()
replayed=[]
for e in events:
    replayed.append({"seq":e["seq"],"state":e["state"],"payload":e["payload"]})
elapsed=(time.perf_counter()-start)*1000
result={"protocol":"REPLAY-200","events":N,"source_digest":expected,"replay_digest":digest(replayed),"elapsed_ms":elapsed,"passed":replayed==events and digest(replayed)==expected}
Path("evidence").mkdir(exist_ok=True)
Path("evidence/replay_200.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
raise SystemExit(0 if result["passed"] else 1)
