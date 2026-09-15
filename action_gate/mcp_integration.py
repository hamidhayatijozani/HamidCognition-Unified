from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(__file__)
TENANT = "mcp-tenant"
env = os.environ.copy()
env.update({"ACTION_GATE_DB": "/tmp/action-gate-mcp.db", "PYTHONPATH": ROOT, "ACTION_GATE_ENV": "development"})
procs = [
    subprocess.Popen([sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000"], cwd=ROOT, env=env),
    subprocess.Popen([sys.executable, "tool_server.py"], cwd=ROOT, env=env),
    subprocess.Popen([sys.executable, "enforcement_proxy.py"], cwd=ROOT, env={**env, "MODE": "mcp", "PORT": "8081"}),
]
try:
    time.sleep(2)

    def call(message, tenant=TENANT):
        req = urllib.request.Request(
            "http://127.0.0.1:8081",
            data=json.dumps(message).encode(),
            headers={
                "Content-Type": "application/json",
                "X-Agent-ID": "mcp-demo",
                "X-Actor-ID": "actor-mcp",
                "X-Tenant-ID": tenant,
            },
        )
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    status, denied = call({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "delete_file", "arguments": {"target": "/production/data.db"}}})
    assert status == 200
    assert denied["result"]["blocked_by_action_gate"] is True
    assert denied["result"]["decision"]["decision"] == "DENY"

    status, allowed = call({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "read_public_file", "arguments": {"target": "/public/info.txt"}}})
    assert status == 200
    assert allowed["tool_executed"] is True

    # MCP must reject unsupported methods before any tool execution path is reached.
    status, unsupported = call({"jsonrpc": "2.0", "id": 3, "method": "resources/read", "params": {"uri": "file:///public/info.txt"}})
    assert status == 400
    assert unsupported["error"] == "MCP adapter permits tools/call only"

    # A forged attestation must never authorize the direct tool endpoint.
    forged_headers = {
        "Content-Type": "application/json",
        "X-HCJ-Decision-ID": "fabricated-decision-id",
        "X-HCJ-Action-Hash": "fabricated-action-hash",
        "X-HCJ-Nonce": "fabricated-nonce",
        "X-HCJ-Enforcement-Attestation": "fabricated-attestation",
    }
    try:
        urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:9000", data=b"{}", headers=forged_headers))
        raise AssertionError("forged tool attestation unexpectedly succeeded")
    except urllib.error.HTTPError as e:
        assert e.code == 403

    # Missing enforcement authority must also be rejected by the direct tool endpoint.
    try:
        urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:9000", data=b"{}", headers={"Content-Type": "application/json"}))
        raise AssertionError("direct tool bypass unexpectedly succeeded")
    except urllib.error.HTTPError as e:
        assert e.code == 403
    print("REAL_MCP_ENFORCEMENT_INTEGRATION_PASS")
finally:
    for p in procs:
        p.terminate()
    for p in procs:
        p.wait(timeout=5)
