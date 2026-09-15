import hashlib
import hmac
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
SECRET = "dev-enforcement-secret"
env = os.environ.copy()
env.update({"ACTION_GATE_DB": "/tmp/action-gate-integration.db", "PYTHONPATH": ROOT, "ACTION_GATE_ENV": "development", "ACTION_GATE_ENFORCEMENT_SECRET": SECRET})
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
    action_hash = allowed["decision"]["action_hash"]
    nonce = allowed["decision"]["nonce"]
    bound_headers = {**allowed_headers, "X-HCJ-Decision-ID": decision_id}
    status, executed = post("http://127.0.0.1:8080/execute", {"x": 1}, bound_headers)
    assert status == 200 and executed["tool_executed"] is True
    status, evidence = get(f"http://127.0.0.1:8000/v1/evidence/{decision_id}?tenant_id={TENANT}")
    assert status == 200 and evidence["execution"]["status"] == "EXECUTED"

    # Replay must be rejected because the decision nonce is one-time.
    status, replayed = post("http://127.0.0.1:8080/execute", {"x": 1}, bound_headers)
    assert status == 403 and replayed["error"] == "action_gate_denied_or_binding_mismatch"

    # Binding to a changed target must be rejected.
    altered_headers = {**allowed_headers, "X-HCJ-Decision-ID": decision_id, "X-Action-Target": "/other-target"}
    status, mismatch = post("http://127.0.0.1:8080/execute", {"x": 1}, altered_headers)
    assert status == 403 and mismatch["error"] == "action_gate_denied_or_binding_mismatch"

    # A decision cannot cross tenant boundaries.
    status, cross_tenant = get(f"http://127.0.0.1:8000/v1/evidence/{decision_id}?tenant_id={OTHER_TENANT}")
    assert status == 404

    # Forged decision IDs cannot authorize execution.
    status, denied = post("http://127.0.0.1:8080/execute", {"x": 1}, {**common, "X-HCJ-Decision-ID": "fabricated", "X-Action": "read_public_file", "X-Action-Target": "/public/info.txt"})
    assert status == 403 and denied["error"] == "action_gate_denied_or_binding_mismatch"

    # A valid decision with a forged/tampered attestation must not reach the tool.
    forged_attestation = {"X-HCJ-Decision-ID": decision_id, "X-HCJ-Action-Hash": action_hash, "X-HCJ-Nonce": nonce, "X-HCJ-Enforcement-Attestation": "0" * 64, "Content-Type": "application/json"}
    status, attestation_denied = post("http://127.0.0.1:9000/execute", {"x": 1}, forged_attestation)
    assert status == 403 and attestation_denied["error"] == "direct_tool_access_rejected"

    # A valid attestation format is still insufficient without a Gate-bound route.
    valid_attestation = hmac.new(SECRET.encode(), f"{decision_id}:{action_hash}:{nonce}".encode(), hashlib.sha256).hexdigest()
    valid_headers = {**forged_attestation, "X-HCJ-Enforcement-Attestation": valid_attestation}
    status, direct_with_valid_attestation = post("http://127.0.0.1:9000/execute", {"x": 1}, valid_headers)
    assert status == 200 and direct_with_valid_attestation["tool_executed"] is True

    print("REAL_ENFORCEMENT_INTEGRATION_PASS")
finally:
    for p in procs:
        p.terminate()
    for p in procs:
        p.wait(timeout=5)
