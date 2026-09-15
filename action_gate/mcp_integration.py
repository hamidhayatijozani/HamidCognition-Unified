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
TOOL_PORT = "19001"
MCP_PORT = "18081"
SECRET = "mcp-enforcement-secret"

env = os.environ.copy()
env.update({
    "ACTION_GATE_DB": "/tmp/action-gate-mcp.db",
    "PYTHONPATH": ROOT,
    "ACTION_GATE_ENV": "development",
    "ACTION_GATE_ENFORCEMENT_SECRET": SECRET,
    "TOOL_PORT": TOOL_PORT,
})

procs = [
    subprocess.Popen([sys.executable, "tool_server.py"], cwd=ROOT, env=env),
    subprocess.Popen([sys.executable, "enforcement_proxy.py"], cwd=ROOT, env={
        **env,
        "MODE": "mcp",
        "PORT": MCP_PORT,
        "TOOL_URL": f"http://127.0.0.1:{TOOL_PORT}",
    }),
]


def wait_for(url, timeout=10):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=0.5):
                return
        except urllib.error.HTTPError:
            return
        except Exception:
            time.sleep(0.1)
    raise RuntimeError(f"service_not_ready: {url}")


def call(message):
    req = urllib.request.Request(
        f"http://127.0.0.1:{MCP_PORT}",
        data=json.dumps(message).encode(),
        headers={"Content-Type": "application/json", "X-Agent-ID": "mcp-demo", "X-Actor-ID": "actor-mcp", "X-Tenant-ID": TENANT},
    )
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


try:
    wait_for(f"http://127.0.0.1:{TOOL_PORT}/health")
    wait_for(f"http://127.0.0.1:{MCP_PORT}/health")

    status, denied = call({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "delete_file", "arguments": {"target": "/production/data.db"}}})
    assert status == 200
    assert denied["result"]["blocked_by_action_gate"] is True
    assert denied["result"]["decision"]["decision"] == "DENY"

    status, allowed = call({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "read_public_file", "arguments": {"target": "/public/info.txt"}}})
    assert status == 200
    assert allowed["tool_executed"] is True

    status, forged = call({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "read_public_file", "arguments": {"target": "/public/info.txt"}}, "x-hcj-decision-id": "fabricated"})
    assert status == 200 and forged.get("tool_executed") is True

    try:
        urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{TOOL_PORT}", data=b"{}", headers={"Content-Type": "application/json"}))
        raise AssertionError("direct tool bypass unexpectedly succeeded")
    except urllib.error.HTTPError as e:
        assert e.code == 403
    print("REAL_MCP_ENFORCEMENT_INTEGRATION_PASS")
finally:
    for p in procs:
        p.terminate()
    for p in procs:
        p.wait(timeout=5)
