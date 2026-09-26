"""Executable external-agent Action Gate integration and replay test.

This harness exercises the real HTTP and MCP enforcement boundaries. It does
not intercept or modify ChatGPT internals. It proves that an allowed action
reaches the protected tool once, that reusing the same execution authority is
rejected by the tool nonce guard, and that an authority cannot be rebound to a
changed HTTP target.
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
TOOL_NONCE_DB = "/tmp/harness-tool-nonces.db"


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
        raw = exc.read()
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = {"raw": raw.decode(errors="replace")}
        return exc.code, body


def get(url: str, headers: dict | None = None):
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = {"raw": raw.decode(errors="replace")}
        return exc.code, body


def wait_for(url: str, headers: dict, processes: list[subprocess.Popen], timeout: float = 15) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if any(p.poll() is not None for p in processes):
            raise RuntimeError("one of the Action Gate harness processes exited during startup")
        try:
            status, body = get(url, headers)
            if status == 200 and body.get("status") in {"ok", "degraded"}:
                return
        except Exception:
            pass
        time.sleep(0.2)
    raise RuntimeError(f"service did not become ready: {url}")


def main() -> int:
    for path in (DB, TOOL_NONCE_DB):
        try:
            os.remove(path)
        except FileNotFoundError:
            pass

    env = os.environ.copy()
    env.update({
        "ACTION_GATE_ENV": "development",
        "ACTION_GATE_DB": DB,
        "ACTION_GATE_SIGNING_SECRET": "harness-signing-secret",
        "ACTION_GATE_AUTHORITY_SECRET": "harness-signing-secret",
        "ACTION_GATE_API_TOKEN": "harness-token",
        "PYTHONPATH": str(GATE),
    })
    processes = [
        subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=GATE,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ),
        subprocess.Popen(
            [sys.executable, "tool_server.py"],
            cwd=GATE,
            env={**env, "PORT": "9000", "TOOL_NONCE_DB": TOOL_NONCE_DB},
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ),
        subprocess.Popen(
            [sys.executable, "enforcement_proxy.py"],
            cwd=GATE,
            env={**env, "MODE": "mcp", "PORT": "8081", "GATE_URL": "http://127.0.0.1:8000", "TOOL_URL": "http://127.0.0.1:9000"},
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ),
        subprocess.Popen(
            [sys.executable, "enforcement_proxy.py"],
            cwd=GATE,
            env={**env, "MODE": "http", "PORT": "8082", "GATE_URL": "http://127.0.0.1:8000", "TOOL_URL": "http://127.0.0.1:9000"},
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ),
    ]
    headers = {
        "Content-Type": "application/json",
        "X-Agent-ID": "chatgpt-external-agent",
        "X-Actor-ID": "actor-harness",
        "X-Session-ID": "session-harness",
        "X-Tenant-ID": "tenant-harness",
    }
    auth = {"Authorization": "Bearer harness-token"}
    gate_headers = {**headers, **auth}
    tool_headers = {"X-Tenant-ID": "tenant-harness"}

    try:
        wait_for("http://127.0.0.1:8000/health", auth, processes)
        wait_for("http://127.0.0.1:8081", {}, processes)
        wait_for("http://127.0.0.1:8082", {}, processes)

        denied_status, denied = post(
            "http://127.0.0.1:8081",
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "delete_file", "arguments": {"target": "/production/data.db"}}},
            gate_headers,
        )
        assert denied_status == 200
        assert denied["result"]["blocked_by_action_gate"] is True
        assert denied["result"]["decision"]["decision"] == "DENY"

        allowed_status, allowed = post(
            "http://127.0.0.1:8081",
            {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "read_public_file", "arguments": {"target": "/public/info.txt"}}},
            gate_headers,
        )
        assert allowed_status == 200 and allowed["tool_executed"] is True

        decision_id = allowed["decision_id"]
        evidence_status, evidence = get(
            f"http://127.0.0.1:8000/v1/evidence/{decision_id}?tenant_id=tenant-harness",
            auth,
        )
        assert evidence_status == 200
        authority = evidence["execution_authority"]
        action_hash = evidence["action_hash"]

        replay_status, replay = post(
            "http://127.0.0.1:9000",
            {"jsonrpc": "2.0", "id": 99, "method": "tools/call", "params": {"name": "read_public_file", "arguments": {"target": "/public/info.txt"}}},
            {
                **tool_headers,
                "X-HCJ-Execution-Authority": authority,
                "X-HCJ-Action-Hash": action_hash,
            },
        )
        assert replay_status == 403
        assert replay["error"] == "execution_authority_invalid"

        http_status, http_result = post(
            "http://127.0.0.1:8082",
            {"public": True},
            {**gate_headers, "X-Action": "read_public_file", "X-Action-Target": "/public/info.txt"},
        )
        assert http_status == 200 and http_result["enforced"] is True
        http_decision_id = http_result["decision"]["decision_id"]

        mismatch_status, mismatch = post(
            "http://127.0.0.1:8082",
            {"public": True},
            {**gate_headers, "X-Action": "read_public_file", "X-Action-Target": "/other-target", "X-HCJ-Decision-ID": http_decision_id},
        )
        assert mismatch_status == 403
        assert mismatch["error"] == "action_gate_denied_or_binding_mismatch"

        replay_check_status, replay_check = get(
            f"http://127.0.0.1:8000/v1/replay/{decision_id}?tenant_id=tenant-harness",
            auth,
        )
        assert replay_check_status == 200
        assert replay_check["match"] is True
        assert replay_check["policy_hash_match"] is True
        assert replay_check["action_hash_match"] is True

        print("CHATGPT_STYLE_EXTERNAL_AGENT_GATE_PASS")
        print("runtime_interception=false")
        print("mcp_boundary=agent -> enforcement -> action-gate -> tool")
        print("controls=ALLOW,DENY,action-binding,replay-protection,evidence")
        print("replay_attack=blocked")
        print("binding_attack=blocked")
        print("evidence_replay=verified")
        return 0
    finally:
        for process in processes:
            process.terminate()
        for process in processes:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
