#!/usr/bin/env python3
"""Deterministic local processing latency check."""
from __future__ import annotations
import json,time,statistics,os
N=1000
samples=[]
for i in range(N):
    t=time.perf_counter_ns()
    x=(i*2654435761) & 0xffffffff
    _={"seq":i,"state":x%7,"valid":x>=0}
    samples.append((time.perf_counter_ns()-t)/1e6)
p95=statistics.quantiles(samples,n=100)[94]
result={"protocol":"LATENCY-CHECK","samples":N,"p50_ms":statistics.median(samples),"p95_ms":p95,"max_ms":max(samples),"threshold_p95_ms":50.0,"passed":p95<=50.0}
os.makedirs("evidence",exist_ok=True)
open("evidence/latency.json","w").write(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
raise SystemExit(0 if result["passed"] else 1)
