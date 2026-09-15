from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(__file__)
env = os.environ.copy()
env.update({"ACTION_GATE_DB": "/tmp/action-gate-integration.db", "PYTHONPATH": ROOT})
procs = [
    subprocess.Popen([sys.executable, "tool_server.py"], cwd=ROOT, env=env),
    subprocess.Popen([sys.executable, "enforcement_proxy.py"], cwd=ROOT, env={**env, "MODE": "http", "PORT": "8080"}),
]
try:
    time.sleep(2)

    def post(url, payload, headers=None):
        req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json", **(headers or {})})
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    status, blocked = post("http://127.0.0.1:8080/execute", {"x": 1}, {"X-Agent-ID": "demo", "X-Action": "delete_file", "X-Action-Target": "/production/data.db"})
    assert status == 200 and blocked["enforced"] is False and blocked["decision"]["decision"] == "DENY"

    status, allowed = post("http://127.0.0.1:8080/execute", {"x": 1}, {"X-Agent-ID": "demo", "X-Action": "read_public_file", "X-Action-Target": "/public/info.txt"})
    assert status == 200 and allowed["enforced"] is True
    decision_id = allowed["decision"]["decision_id"]
    status, executed = post("http://127.0.0.1:8080/execute", {"x": 1}, {"X-HCJ-Decision-ID": decision_id})
    assert status == 200 and executed["tool_executed"] is True

    status, denied = post("http://127.0.0.1:8080/execute", {"x": 1}, {"X-HCJ-Decision-ID": "fabricated"})
    assert status == 403 and denied["error"] == "action_gate_denied"
    print("REAL_ENFORCEMENT_INTEGRATION_PASS")
finally:
    for p in procs:
        p.terminate()
    for p in procs:
        p.wait(timeout=5)
