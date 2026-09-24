#!/usr/bin/env python3
"""PostgreSQL persistence verifier. Expects DATABASE_URL."""
from __future__ import annotations
import os, sys, time
try:
    import psycopg
except Exception as exc:
    print(f"psycopg import failed: {exc}", file=sys.stderr); raise SystemExit(2)
url=os.environ.get("DATABASE_URL")
if not url: print("DATABASE_URL missing", file=sys.stderr); raise SystemExit(2)
with psycopg.connect(url) as c:
    with c.cursor() as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS evidence_persistence(id INTEGER PRIMARY KEY, value TEXT NOT NULL)")
        cur.execute("DELETE FROM evidence_persistence")
        cur.executemany("INSERT INTO evidence_persistence VALUES (%s,%s)", [(i,f"v-{i}") for i in range(200)])
        c.commit()
        cur.execute("SELECT count(*) FROM evidence_persistence")
        before=cur.fetchone()[0]
result={"protocol":"POSTGRES-PERSISTENCE","rows_before_restart":before}
import json
os.makedirs("evidence",exist_ok=True)
open("evidence/postgres_seed.json","w").write(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
