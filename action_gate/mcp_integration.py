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
env.update({"ACTION_GATE_API_TOKEN": os.environ.get("ACTION_GATE_API_TOKEN", "ci-test-token"), "ACTION_GATE_WORLD_REVALIDATION": "1", "ACTION_GATE_DB": "/tmp/action-gate-mcp.db", "PYTHONPATH": ROOT, "ACTION_GATE_ENV": "development", "ACTION_GATE_SIGNING_SECRET": "mcp-signing-secret", "ACTION_GATE_AUTHORITY_SECRET": "ci-authority-secret", "ACTION_GATE_STATE_ORACLE_SECRET": "ci-state-oracle-secret", "ACTION_GATE_DEBUG_AUTHORITY": "1", "TOOL_NONCE_DB": "/tmp/action-gate-mcp-tool-authority.db"})
procs = [
    subprocess.Popen([sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000"], cwd=ROOT, env=env),
    subprocess.Popen([sys.executable, "tool_server.py"], cwd=ROOT, env=env),
    subprocess.Popen([sys.executable, "enforcement_proxy.py"], cwd=ROOT, env={**env, "MODE": "mcp", "PORT": "8081"}),
]
try:
    def wait_for_port(host: str, port: int, label: str, attempts: int = 30) -> None:
        import socket
        last_error = None
        for attempt in range(1, attempts + 1):
            try:
                with socket.create_connection((host, port), timeout=2):
                    print(f"{label} ready on {host}:{port}")
                    return
            except OSError as exc:
                last_error = exc
                print(f"Waiting for {label} ({attempt}/{attempts}): {exc}")
                time.sleep(1)
        raise RuntimeError(f"{label} did not become ready: {last_error}")

    wait_for_port("127.0.0.1", 8000, "Action Gate")
    wait_for_port("127.0.0.1", 9000, "Tool server")
    wait_for_port("127.0.0.1", 8081, "MCP enforcement proxy")

    def reserve_execution(decision_id, tenant_id, actor_id, session_id, action_hash_value, nonce):
        req = urllib.request.Request(
            "http://127.0.0.1:8000/v1/action/" + decision_id + "/execution/reserve",
            data=json.dumps({
                "tenant_id": tenant_id,
                "actor_id": actor_id,
                "session_id": session_id,
                "action_hash": action_hash_value,
                "nonce": nonce,
            }).encode(),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {os.environ.get('ACTION_GATE_API_TOKEN', 'ci-test-token')}"},
        )
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())

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

    # Live world revalidation requires a signed current-world snapshot before any ALLOW.
    import hashlib
    import hmac

    initial_state_secret = "ci-state-oracle-secret"
    initial_state = {"world_version": "wv-mcp-initial", "snapshot": {"source": "mcp-integration", "status": "ready"}}
    initial_canonical = json.dumps(initial_state, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    initial_signature = hmac.new(initial_state_secret.encode(), initial_canonical.encode(), hashlib.sha256).hexdigest()
    initial_req = urllib.request.Request(
        "http://127.0.0.1:8000/v1/state/commit",
        data=json.dumps({**initial_state, "oracle_signature": initial_signature}).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {os.environ.get('ACTION_GATE_API_TOKEN', 'ci-test-token')}"},
    )
    with urllib.request.urlopen(initial_req) as response:
        assert response.status == 200

    status, denied = call({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "delete_file", "arguments": {"target": "/production/data.db"}}})
    assert status == 200
    assert denied["result"]["blocked_by_action_gate"] is True
    assert denied["result"]["decision"]["decision"] == "DENY"

    status, allowed = call({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "read_public_file", "arguments": {"target": "/public/info.txt"}}})
    assert status == 200
    assert allowed["tool_executed"] is True

    # A valid authority with a mismatched policy digest must never authorize the tool.
    status, evidence = call({"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "read_public_file", "arguments": {"target": "/public/policy-bound.txt"}}})
    assert status == 200
    assert evidence["tool_executed"] is True

    # The direct tool endpoint must independently enforce the policy binding carried by the authority.
    # Obtain a fresh ALLOW authority, then alter only the policy digest at the tool boundary.
    gate_req = urllib.request.Request(
        "http://127.0.0.1:8000/v1/action/evaluate",
        data=json.dumps({
            "agent_id": "mcp-demo",
            "actor_id": "actor-mcp",
            "tenant_id": TENANT,
            "action": "read_public_file",
            "target": "/public/policy-check.txt",
            "parameters": {"target": "/public/policy-check.txt"},
        }).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {os.environ.get('ACTION_GATE_API_TOKEN', 'ci-test-token')}"},
    )
    with urllib.request.urlopen(gate_req) as r:
        gate = json.loads(r.read())
    reserved = reserve_execution(gate["decision_id"], TENANT, "actor-mcp", None, gate["action_hash"], gate["nonce"])
    wrong_policy_headers = {
        "Content-Type": "application/json",
        "X-HCJ-Execution-Authority": reserved["execution_authority"],
        "X-HCJ-Action-Hash": gate["action_hash"],
        "X-HCJ-Policy-Hash": "0" * 64,
        "X-Tenant-ID": TENANT,
    }
    try:
        urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:9000", data=b"{}", headers=wrong_policy_headers))
        raise AssertionError("mismatched policy binding unexpectedly succeeded")
    except urllib.error.HTTPError as e:
        body = json.loads(e.read())
        assert e.code == 403
        assert body["diagnostic"] == "policy_binding_mismatch"

    # MCP must reject unsupported methods before any tool execution path is reached.
    status, unsupported = call({"jsonrpc": "2.0", "id": 3, "method": "resources/read", "params": {"uri": "file:///public/info.txt"}})
    assert status == 400
    assert unsupported["error"] == "MCP adapter permits tools/call only"

    # A forged attestation must never authorize the direct tool endpoint.
    forged_headers = {
        "Content-Type": "application/json",
        "X-HCJ-Execution-Authority": "fabricated-authority",
        "X-HCJ-Action-Hash": "fabricated-action-hash",
        "X-Tenant-ID": TENANT,
    }
    try:
        urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:9000", data=b"{}", headers=forged_headers))
        raise AssertionError("forged tool authority unexpectedly succeeded")
    except urllib.error.HTTPError as e:
        assert e.code == 403

    # Missing enforcement authority must also be rejected by the direct tool endpoint.
    try:
        urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:9000", data=b"{}", headers={"Content-Type": "application/json"}))
        raise AssertionError("direct tool bypass unexpectedly succeeded")
    except urllib.error.HTTPError as e:
        assert e.code == 403

    # Reproduce the authorization-to-execution race over the real Gate HTTP API
    # and verify that the MCP tool boundary cannot be reached with stale authority.
    import hashlib
    import hmac

    state_secret = "ci-state-oracle-secret"

    def commit_state(world_version, snapshot):
        payload = {"world_version": world_version, "snapshot": snapshot}
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        signature = hmac.new(state_secret.encode(), canonical.encode(), hashlib.sha256).hexdigest()
        req = urllib.request.Request(
            "http://127.0.0.1:8000/v1/state/commit",
            data=json.dumps({**payload, "oracle_signature": signature}).encode(),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.environ.get('ACTION_GATE_API_TOKEN', 'ci-test-token')}",
            },
        )
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())

    commit_state("wv-mcp-context-A", {"risk_tier": "low"})
    stale_req = urllib.request.Request(
        "http://127.0.0.1:8000/v1/action/evaluate",
        data=json.dumps({
            "agent_id": "mcp-context-race",
            "actor_id": "actor-mcp",
            "session_id": "session-context-race",
            "tenant_id": TENANT,
            "action": "read_public_file",
            "target": "/public/context-race.txt",
            "parameters": {"target": "/public/context-race.txt"},
            "context": {"risk_tier": "low"},
        }).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ.get('ACTION_GATE_API_TOKEN', 'ci-test-token')}",
        },
    )
    with urllib.request.urlopen(stale_req) as response:
        stale_decision = json.loads(response.read())
    assert stale_decision["decision"] == "ALLOW"
    assert stale_decision["world_version"] == "wv-mcp-context-A"

    # Reserve while world A is still current, then mutate the world before
    # the protected tool sees the otherwise valid signed authority.
    reserve_req = urllib.request.Request(
        f"http://127.0.0.1:8000/v1/action/{stale_decision['decision_id']}/execution/reserve",
        data=json.dumps({
            "tenant_id": TENANT,
            "actor_id": "actor-mcp",
            "session_id": "session-context-race",
            "action_hash": stale_decision["action_hash"],
            "nonce": stale_decision["nonce"],
            "world_version": "wv-mcp-context-A",
        }).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ.get('ACTION_GATE_API_TOKEN', 'ci-test-token')}",
        },
    )
    with urllib.request.urlopen(reserve_req) as response:
        reserved_stale = json.loads(response.read())
    assert reserved_stale["execution"]["status"] == "RESERVED"

    commit_state("wv-mcp-context-B", {"risk_tier": "blocked"})

    # The signed authority was valid when reserved, but must now fail at the
    # protected tool boundary after the world changes.
    stale_tool_headers = {
        "Content-Type": "application/json",
        "X-HCJ-Execution-Authority": reserved_stale["execution_authority"],
        "X-HCJ-Action-Hash": stale_decision["action_hash"],
        "X-HCJ-Policy-Hash": stale_decision["policy_hash"],
        "X-Tenant-ID": TENANT,
    }
    try:
        urllib.request.urlopen(urllib.request.Request(
            "http://127.0.0.1:9000",
            data=b"{}",
            headers=stale_tool_headers,
        ))
        raise AssertionError("stale signed authority unexpectedly reached protected tool")
    except urllib.error.HTTPError as e:
        body = json.loads(e.read())
        assert e.code == 403
        assert body["diagnostic"] == "execution_world_state_changed"

    # Re-reserving the original decision after drift must also fail closed.
    try:
        urllib.request.urlopen(reserve_req)
        raise AssertionError("stale authorization unexpectedly reserved after drift")
    except urllib.error.HTTPError as e:
        body = json.loads(e.read())
        assert e.code == 409
        assert body["detail"] == "execution_world_state_changed"

    # Even at the MCP tool endpoint, no authority means no execution.
    try:
        urllib.request.urlopen(urllib.request.Request(
            "http://127.0.0.1:9000",
            data=json.dumps({"target": "/public/context-race.txt"}).encode(),
            headers={"Content-Type": "application/json", "X-Tenant-ID": TENANT},
        ))
        raise AssertionError("MCP tool endpoint accepted request without fresh authority")
    except urllib.error.HTTPError as e:
        assert e.code == 403

    print("MCP_CONTEXT_DRIFT_HTTP_GATE_PASS")

    print("REAL_MCP_ENFORCEMENT_INTEGRATION_PASS")
finally:
    for p in procs:
        p.terminate()
    for p in procs:
        p.wait(timeout=5)
