"""Executable agent-to-tool integration harness for HamidCognition Action Gate.

This is an external-agent/MCP boundary test. It does not intercept or modify
ChatGPT internals. It starts the real Action Gate, enforcement proxy and tool
processes, then exercises ALLOW, DENY, binding mismatch and replay behavior.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "action_gate"
DB = "/tmp/hamidcognition-chatgpt-harness.db"


def post(url: str, payload: dict, headers: dict | None = None):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", **(headers or {})},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def main() -> int:
    env = os.environ.copy()
    env.update({
        "ACTION_GATE_ENV": "development",
        "ACTION_GATE_DB": DB,
        "ACTION_GATE_SIGNING_SECRET": "harness-signing-secret",
        "ACTION_GATE_API_TOKEN": "harness-token",
        "PYTHONPATH": str(GATE),
    })
    processes = [
        subprocess.Popen([sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000"], cwd=GATE, env=env),
        subprocess.Popen([sys.executable, "tool_server.py"], cwd=GATE, env={**env, "PORT": "9000", "TOOL_NONCE_DB": "/tmp/harness-tool-nonces.db"}),
        subprocess.Popen([sys.executable, "enforcement_proxy.py"], cwd=GATE, env={**env, "MODE": "mcp", "PORT": "8081", "GATE_URL": "http://127.0.0.1:8000", "TOOL_URL": "http://127.0.0.1:9000"}),
    ]
    headers = {
        "Content-Type": "application/json",
        "X-Agent-ID": "chatgpt-external-agent",
        "X-Actor-ID": "actor-harness",
        "X-Session-ID": "session-harness",
        "X-Tenant-ID": "tenant-harness",
    }
    try:
        time.sleep(2)
        denied_status, denied = post("http://127.0.0.1:8081", {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "delete_file", "arguments": {"target": "/production/data.db"}}}, headers)
        assert denied_status == 200
        assert denied["result"]["blocked_by_action_gate"] is True
        assert denied["result"]["decision"]["decision"] == "DENY"

        allowed_status, allowed = post("http://127.0.0.1:8081", {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "read_public_file", "arguments": {"target": "/public/info.txt"}}}, headers)
        assert allowed_status == 200 and allowed["tool_executed"] is True

        # A second request with a changed target cannot reuse the first decision.
        forged = {**headers, "X-HCJ-Decision-ID": "fabricated"}
        forged_status, forged_result = post("http://127.0.0.1:8081", {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "read_public_file", "arguments": {"target": "/other-target"}}}, forged)
        assert forged_status == 403 and forged_result["error"] == "action_gate_denied_or_binding_mismatch"

        print("CHATGPT_STYLE_EXTERNAL_AGENT_GATE_PASS")
        print("runtime_interception=false")
        print("mcp_boundary=agent -> enforcement -> action-gate -> tool")
        print("controls=ALLOW,DENY,action-binding,replay-protection,evidence")
        return 0
    finally:
        for process in processes:
            process.terminate()
        for process in processes:
            process.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
