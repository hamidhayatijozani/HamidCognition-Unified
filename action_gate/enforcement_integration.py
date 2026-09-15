import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(__file__)
TENANT = "integration-tenant"
OTHER_TENANT = "other-tenant"
env = os.environ.copy()
env.update({"ACTION_GATE_DB": "/tmp/action-gate-integration.db", "PYTHONPATH": ROOT, "ACTION_GATE_ENV": "development", "ACTION_GATE_ENFORCEMENT_SECRET": "dev-enforcement-secret"})
procs = [
    subprocess.Popen([sys.executable, "app.py"], cwd=ROOT, env={**env, "ACTION_GATE_ENV": "development"}),
    subprocess.Popen([sys.executable, "tool_server.py"], cwd=ROOT, env=env),
    subprocess.Popen([sys.executable, "enforcement_proxy.py"], cwd=ROOT, env={**env, "MODE": "http", "PORT": "8080"}),
]
try:
    time.sleep(3)

    def post(url, payload, headers=None):
        req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json", **(headers or {})})
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def get(url):
        req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    common = {"X-Agent-ID": "demo", "X-Actor-ID": "actor-1", "X-Tenant-ID": TENANT}
    blocked_headers = {**common, "X-Action": "delete_file", "X-Action-Target": "/production/data.db"}
    status, blocked = post("http://127.0.0.1:8080/execute", {"x": 1}, blocked_headers)
    assert status == 200 and blocked["enforced"] is False and blocked["decision"]["decision"] == "DENY"

    allowed_headers = {**common, "X-Action": "read_public_file", "X-Action-Target": "/public/info.txt"}
    status, allowed = post("http://127.0.0.1:8080/execute", {"x": 1}, allowed_headers)
    assert status == 200 and allowed["enforced"] is True
    decision_id = allowed["decision"]["decision_id"]
    bound_headers = {**allowed_headers, "X-HCJ-Decision-ID": decision_id}
    status, executed = post("http://127.0.0.1:8080/execute", {"x": 1}, bound_headers)
    assert status == 200 and executed["tool_executed"] is True
    status, evidence = get(f"http://127.0.0.1:8000/v1/evidence/{decision_id}?tenant_id={TENANT}")
    assert status == 200 and evidence["execution"]["status"] == "EXECUTED"

    status, replayed = post("http://127.0.0.1:8080/execute", {"x": 1}, bound_headers)
    assert status == 403 and replayed["error"] == "action_gate_denied_or_binding_mismatch"

    altered_headers = {**allowed_headers, "X-HCJ-Decision-ID": decision_id, "X-Action-Target": "/other-target"}
    status, mismatch = post("http://127.0.0.1:8080/execute", {"x": 1}, altered_headers)
    assert status == 403 and mismatch["error"] == "action_gate_denied_or_binding_mismatch"

    status, cross_tenant = get(f"http://127.0.0.1:8000/v1/evidence/{decision_id}?tenant_id={OTHER_TENANT}")
    assert status == 404

    status, forged = post("http://127.0.0.1:8080/execute", {"x": 1}, {**common, "X-HCJ-Decision-ID": "fabricated", "X-Action": "read_public_file", "X-Action-Target": "/public/info.txt"})
    assert status == 403 and forged["error"] == "action_gate_denied_or_binding_mismatch"

    # Tampered attestation must be rejected at the tool boundary.
    status, attestation_denied = post("http://127.0.0.1:9000/execute", {"x": 1}, {"X-HCJ-Decision-ID": decision_id, "X-HCJ-Action-Hash": evidence["action_hash"], "X-HCJ-Nonce": evidence["nonce"], "X-HCJ-Enforcement-Attestation": "0" * 64})
    assert status == 403 and attestation_denied["error"] == "direct_tool_access_rejected"

    print("REAL_ENFORCEMENT_INTEGRATION_PASS")
finally:
    for p in procs:
        p.terminate()
    for p in procs:
        p.wait(timeout=5)
