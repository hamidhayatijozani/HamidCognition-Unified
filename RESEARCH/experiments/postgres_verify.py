#!/usr/bin/env python3
"""Verify rows survive an external PostgreSQL container restart."""
from __future__ import annotations
import os, json, sys
import psycopg
url=os.environ["DATABASE_URL"]
with psycopg.connect(url) as c:
    with c.cursor() as cur:
        cur.execute("SELECT count(*), min(id), max(id) FROM evidence_persistence")
        count, mn, mx=cur.fetchone()
result={"protocol":"POSTGRES-PERSISTENCE-AFTER-RESTART","rows_after_restart":count,"min_id":mn,"max_id":mx,"passed":count==200 and mn==0 and mx==199}
open("evidence/postgres_after_restart.json","w").write(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
raise SystemExit(0 if result["passed"] else 1)
