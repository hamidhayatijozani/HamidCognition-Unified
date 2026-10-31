import json
import hashlib
import hmac
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(__file__)
TENANT = "integration-tenant"
OTHER_TENANT = "other-tenant"
API_TOKEN = os.environ.get("ACTION_GATE_API_TOKEN", "ci-test-token")
env = os.environ.copy()
env.update({
    "ACTION_GATE_DB": "/tmp/action-gate-integration.db",
    "PYTHONPATH": ROOT,
    "ACTION_GATE_ENV": "development",
    "ACTION_GATE_SIGNING_SECRET": "dev-signing-secret",
    "ACTION_GATE_API_TOKEN": API_TOKEN,
    "ACTION_GATE_AUTHORITY_SECRET": "ci-authority-secret",
    "ACTION_GATE_STATE_ORACLE_SECRET": "ci-state-oracle-secret",
    "TOOL_NONCE_DB": "/tmp/action-gate-tool-authority.db",
    # Explicit enablement: production default is fail-closed (off).
    "ACTION_GATE_WORLD_REVALIDATION": "1",
})
procs = [
    subprocess.Popen([sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000"], cwd=ROOT, env=env),
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

    def get(url, headers=None):
        req = urllib.request.Request(url, headers=headers or {})
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    gate_headers = {"Authorization": f"Bearer {API_TOKEN}"}
    snapshot_payload = {"world_version": "ci-world-v1", "snapshot": {"environment": "ci", "revision": "integration-test"}}
    canonical_snapshot = json.dumps(snapshot_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    snapshot_signature = hmac.new(b"ci-state-oracle-secret", canonical_snapshot.encode(), hashlib.sha256).hexdigest()
    status, committed = post("http://127.0.0.1:8000/v1/state/commit", {**snapshot_payload, "oracle_signature": snapshot_signature}, gate_headers)
    assert status == 200 and committed["world_version"] == "ci-world-v1"

    common = {"X-Agent-ID": "demo", "X-Actor-ID": "actor-1", "X-Tenant-ID": TENANT, "X-Session-ID": "session-1"}
    blocked_headers = {**common, "X-Action": "delete_file", "X-Action-Target": "/production/data.db"}
    status, blocked = post("http://127.0.0.1:8080/execute", {"x": 1}, blocked_headers)
    assert status == 200 and blocked["enforced"] is False and blocked["decision"]["decision"] == "DENY"
    assert blocked["decision"]["enforcement_action_hash"] == blocked["decision"]["action_hash"]

    allowed_headers = {**common, "X-Action": "read_public_file", "X-Action-Target": "/public/info.txt"}
    status, allowed = post("http://127.0.0.1:8080/execute", {"x": 1}, allowed_headers)
    assert allowed["decision"]["enforcement_action_hash"] == allowed["decision"]["action_hash"]
    assert status == 200 and allowed["enforced"] is True
    decision_id = allowed["decision"]["decision_id"]
    bound_headers = {**allowed_headers, "X-HCJ-Decision-ID": decision_id}
    status, executed = post("http://127.0.0.1:8080/execute", {"x": 1}, bound_headers)
    assert status == 200 and executed["tool_executed"] is True
    status, evidence = get(f"http://127.0.0.1:8000/v1/evidence/{decision_id}?tenant_id={TENANT}", gate_headers)
    assert status == 200 and evidence["execution"]["status"] == "EXECUTED"

    # Replay reaches the Gate, which rejects the consumed nonce; the enforcement layer must fail closed.
    status, replayed = post("http://127.0.0.1:8080/execute", {"x": 1}, bound_headers)
    assert status == 409 and replayed["detail"] == "decision_nonce_already_consumed"

    altered_headers = {**allowed_headers, "X-HCJ-Decision-ID": decision_id, "X-Action-Target": "/other-target"}
    status, mismatch = post("http://127.0.0.1:8080/execute", {"x": 1}, altered_headers)
    assert status == 403 and mismatch["error"] == "action_gate_denied_or_binding_mismatch"

    altered_actor_headers = {**allowed_headers, "X-HCJ-Decision-ID": decision_id, "X-Actor-ID": "actor-2"}
    status, actor_mismatch = post("http://127.0.0.1:8080/execute", {"x": 1}, altered_actor_headers)
    assert status == 403 and actor_mismatch["error"] == "action_gate_denied_or_binding_mismatch"

    altered_session_headers = {**allowed_headers, "X-HCJ-Decision-ID": decision_id, "X-Session-ID": "session-2"}
    status, session_mismatch = post("http://127.0.0.1:8080/execute", {"x": 1}, altered_session_headers)
    assert status == 403 and session_mismatch["error"] == "action_gate_denied_or_binding_mismatch"

    status, cross_tenant = get(f"http://127.0.0.1:8000/v1/evidence/{decision_id}?tenant_id={OTHER_TENANT}", gate_headers)
    assert status == 404

    status, forged = post("http://127.0.0.1:8080/execute", {"x": 1}, {**common, "X-HCJ-Decision-ID": "fabricated", "X-Action": "read_public_file", "X-Action-Target": "/public/info.txt"})
    assert status == 403 and forged["error"] == "action_gate_denied_or_binding_mismatch"

    status, authority_denied = post("http://127.0.0.1:9000/execute", {"x": 1}, {"X-HCJ-Decision-ID": decision_id, "X-HCJ-Action-Hash": evidence["action_hash"], "X-HCJ-Nonce": evidence["nonce"]})
    assert status == 403 and authority_denied["error"] == "execution_authority_invalid"

    print("REAL_ENFORCEMENT_INTEGRATION_PASS")
finally:
    for p in procs:
        p.terminate()
    for p in procs:
        p.wait(timeout=5)
