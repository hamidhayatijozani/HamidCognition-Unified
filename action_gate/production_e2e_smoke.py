import json
import socket
import time
import urllib.request
import urllib.error
import uuid
from concurrent.futures import ThreadPoolExecutor

import storage
from log_redaction import redact_for_log

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


def wait_for_service(host: str, port: int, name: str) -> None:
    for _ in range(30):
        try:
            s = socket.create_connection((host, port), 2)
            s.close()
            return
        except OSError:
            time.sleep(1)
    raise RuntimeError(f"{name}_service_not_ready")

wait_for_service("enforcement", 8080, "enforcement")
wait_for_service("tool", 9000, "tool")

# Negative control: direct tool access without Gate-issued authority must fail closed.
try:
    req = urllib.request.Request("http://tool:9000/direct", data=b"{}", headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req)
    raise AssertionError("direct_tool_access_bypassed_action_gate")
except urllib.error.HTTPError as exc:
    assert exc.code == 403, exc.code

health = get(BASE + "/health")
assert health["status"] == "ok" and health["storage"]["backend"] == "postgresql", health
assert storage.backend() == "postgresql", "nonce_race_requires_real_postgresql"

# Exercise the actual PostgreSQL conditional UPDATE under contention. A successful
# claim must be unique even when many requests race across independent connections.
race_id = "ci-nonce-race-" + uuid.uuid4().hex
race_nonce = "nonce-" + uuid.uuid4().hex
race_record = {
    "decision_id": race_id,
    "trace_id": race_id,
    "nonce": race_nonce,
    "consumed_at": None,
}
con = storage.connect()
try:
    con.execute(
        "INSERT INTO records(decision_id, trace_id, record) VALUES (%s, %s, %s)",
        (race_id, race_id, json.dumps(race_record, separators=(",", ":"))),
    )
    con.commit()
finally:
    con.close()

try:
    with ThreadPoolExecutor(max_workers=16) as pool:
        claims = list(pool.map(
            lambda i: storage.consume_nonce(
                race_id, race_nonce, f"2026-10-29T00:00:{i:02d}+00:00"
            ),
            range(16),
        ))
    assert claims.count(True) == 1, {"successful_claims": claims.count(True), "claims": claims}
    assert claims.count(False) == 15, {"rejected_claims": claims.count(False), "claims": claims}
    con = storage.connect()
    try:
        row = con.execute(
            "SELECT record::jsonb->>'consumed_at' FROM records WHERE decision_id=%s",
            (race_id,),
        ).fetchone()
    finally:
        con.close()
    assert row and row[0], "nonce_claim_was_not_persisted"
    print("POSTGRES_NONCE_CONCURRENCY_PASS", json.dumps({
        "workers": len(claims), "successful_claims": claims.count(True),
        "rejected_claims": claims.count(False), "persisted": True,
    }, sort_keys=True))
finally:
    con = storage.connect()
    try:
        con.execute("DELETE FROM records WHERE decision_id=%s", (race_id,))
        con.commit()
    finally:
        con.close()

payload = {"tenant_id": TENANT, "agent_id": "compose-agent", "actor_id": "compose-actor", "session_id": "compose-session", "action": "read_public_file", "target": "/public/info.txt", "parameters": {}}
headers = {"Content-Type": "application/json", "X-Agent-ID": "compose-agent", "X-Actor-ID": "compose-actor", "X-Session-ID": "compose-session", "X-Tenant-ID": TENANT, "X-Action": "read_public_file", "X-Action-Target": "/public/info.txt"}

# Phase 1: evaluate only. The proxy deliberately does not execute the tool without a bound decision id.
out = post(ENFORCEMENT + "/execute", payload["parameters"], headers)
print("E2E_ENFORCEMENT_EVALUATE_RESPONSE", json.dumps(redact_for_log(out), sort_keys=True))
assert out["enforced"] is True, redact_for_log(out)
did = out["decision"]["decision_id"]
print("E2E_DECISION_ID=" + did, flush=True)
pre = get(BASE + "/v1/evidence/" + did + "?tenant_id=" + TENANT)
print("E2E_PRE_EXECUTION_EVIDENCE", json.dumps(redact_for_log(pre), sort_keys=True))
assert pre.get("execution") is None, redact_for_log(pre)

# Phase 2: bind the exact decision to the exact action and execute it through the enforcement boundary.
execute_headers = {**headers, "X-HCJ-Decision-ID": did}
executed = post(ENFORCEMENT + "/execute", payload["parameters"], execute_headers)
print("E2E_ENFORCEMENT_EXECUTION_RESPONSE", json.dumps(redact_for_log(executed), sort_keys=True))
assert executed.get("tool_executed") is True, redact_for_log(executed)

evidence = get(BASE + "/v1/evidence/" + did + "?tenant_id=" + TENANT)
print("E2E_POST_EXECUTION_EVIDENCE", json.dumps(redact_for_log(evidence), sort_keys=True))
assert evidence.get("execution") is not None, redact_for_log(evidence)
assert evidence["execution"].get("status") == "EXECUTED", redact_for_log(evidence)
assert evidence["tenant_id"] == TENANT, redact_for_log(evidence)
assert evidence["outcome"].get("tool_response", {}).get("tool_executed") is True, redact_for_log(evidence)
print("REAL_POSTGRES_E2E_SMOKE_PASS")
