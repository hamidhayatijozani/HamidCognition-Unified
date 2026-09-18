import json
import socket
import time
import urllib.request

TOKEN = "ci-action-gate-token"
TENANT = "compose-tenant"
BASE = "http://127.0.0.1:8000"
ENFORCEMENT = "http://enforcement:8080"
H = {"Authorization": f"Bearer {TOKEN}"}


def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=H)))


def post(url, payload, headers):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
    return json.load(urllib.request.urlopen(req))


for _ in range(30):
    try:
        s = socket.create_connection(("enforcement", 8080), 2)
        s.close()
        break
    except OSError:
        time.sleep(1)
else:
    raise RuntimeError("enforcement_service_not_ready")

health = get(BASE + "/health")
assert health["status"] == "ok" and health["storage"]["backend"] == "postgresql", health

payload = {"tenant_id": TENANT, "agent_id": "compose-agent", "actor_id": "compose-actor", "session_id": "compose-session", "action": "read_public_file", "target": "/public/info.txt", "parameters": {}}
headers = {"Content-Type": "application/json", "X-Agent-ID": "compose-agent", "X-Actor-ID": "compose-actor", "X-Session-ID": "compose-session", "X-Tenant-ID": TENANT, "X-Action": "read_public_file", "X-Action-Target": "/public/info.txt"}

# Phase 1: evaluate only. The proxy deliberately does not execute the tool without a bound decision id.
out = post(ENFORCEMENT + "/execute", payload["parameters"], headers)
print("E2E_ENFORCEMENT_EVALUATE_RESPONSE", json.dumps(out, sort_keys=True))
assert out["enforced"] is True, out
did = out["decision"]["decision_id"]
pre = get(BASE + "/v1/evidence/" + did + "?tenant_id=" + TENANT)
print("E2E_PRE_EXECUTION_EVIDENCE", json.dumps(pre, sort_keys=True))
assert pre.get("execution") is None, pre

# Phase 2: bind the exact decision to the exact action and execute it through the enforcement boundary.
execute_headers = {**headers, "X-HCJ-Decision-ID": did}
executed = post(ENFORCEMENT + "/execute", payload["parameters"], execute_headers)
print("E2E_ENFORCEMENT_EXECUTION_RESPONSE", json.dumps(executed, sort_keys=True))
assert executed.get("tool_executed") is True, executed

evidence = get(BASE + "/v1/evidence/" + did + "?tenant_id=" + TENANT)
print("E2E_POST_EXECUTION_EVIDENCE", json.dumps(evidence, sort_keys=True))
assert evidence.get("execution") is not None, evidence
assert evidence["execution"].get("status") == "EXECUTED", evidence
assert evidence["tenant_id"] == TENANT, evidence
assert evidence["outcome"].get("tool_response", {}).get("tool_executed") is True, evidence
print("REAL_POSTGRES_E2E_SMOKE_PASS")
