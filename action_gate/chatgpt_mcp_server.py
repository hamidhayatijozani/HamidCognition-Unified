from __future__ import annotations

import json
import os
import urllib.request
from typing import Any

from mcp.server.fastmcp import FastMCP

from action_gate_sdk import ActionGateClient, ActionGateError


GATE_URL = os.getenv("ACTION_GATE_URL", "http://127.0.0.1:8000")
TOOL_URL = os.getenv("PROTECTED_TOOL_URL", "http://127.0.0.1:9000")
GATE_TOKEN = os.getenv("ACTION_GATE_API_TOKEN")
TENANT_ID = os.getenv("DEMO_TENANT_ID", "chatgpt-demo")
ACTOR_ID = os.getenv("DEMO_ACTOR_ID", "chatgpt-user")
AGENT_ID = os.getenv("DEMO_AGENT_ID", "chatgpt-demo-agent")
SESSION_ID = os.getenv("DEMO_SESSION_ID", "chatgpt-demo-session")

mcp = FastMCP(
    "HamidCognition Action Gate Demo",
    instructions=(
        "Demonstration MCP server for HamidCognition Action Gate. "
        "Every protected action is evaluated by Action Gate before the protected "
        "tool is reached. The server exposes the resulting decision and evidence."
    ),
    stateless_http=True,
    json_response=True,
    host=os.getenv("MCP_HOST", "0.0.0.0"),
    port=int(os.getenv("MCP_PORT", "8787")),
)


def gate() -> ActionGateClient:
    return ActionGateClient(GATE_URL, token=GATE_TOKEN)


def call_protected_tool(*, authority: str, action_hash: str, policy_hash: str, target: str) -> dict[str, Any]:
    payload = {
        "tenant_id": TENANT_ID,
        "action": "read_public_file",
        "target": target,
        "parameters": {"target": target},
    }
    request = urllib.request.Request(
        TOOL_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "X-HCJ-Execution-Authority": authority,
            "X-HCJ-Action-Hash": action_hash,
            "X-HCJ-Policy-Hash": policy_hash,
            "X-Tenant-ID": TENANT_ID,
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read())


def _evidence(client: ActionGateClient, decision_id: str) -> dict[str, Any]:
    try:
        return client.evidence(decision_id, TENANT_ID)
    except ActionGateError as exc:
        return {"error": str(exc)}


def _replay(client: ActionGateClient, decision_id: str) -> dict[str, Any]:
    try:
        return client.replay(decision_id, TENANT_ID)
    except ActionGateError as exc:
        return {"error": str(exc)}


@mcp.tool()
def protected_read_public_file(target: str) -> dict[str, Any]:
    """Read a demo public resource through the real Action Gate -> authority -> protected-tool path."""
    if not target.startswith("/public/"):
        return {
            "executed": False,
            "decision": "DENY",
            "reason": "demo_tool_only_allows_public_targets",
        }

    client = gate()
    evaluated = client.evaluate(
        tenant_id=TENANT_ID,
        agent_id=AGENT_ID,
        actor_id=ACTOR_ID,
        session_id=SESSION_ID,
        action="read_public_file",
        target=target,
        parameters={"target": target},
    )
    decision_id = evaluated["decision_id"]

    if evaluated["decision"] != "ALLOW":
        return {
            "executed": False,
            "decision": evaluated["decision"],
            "decision_id": decision_id,
            "reason": evaluated.get("reason"),
            "evidence": _evidence(client, decision_id),
            "replay": _replay(client, decision_id),
        }

    reserved = client.reserve_execution(
        decision_id,
        tenant_id=TENANT_ID,
        actor_id=ACTOR_ID,
        session_id=SESSION_ID,
        action_hash=evaluated["action_hash"],
        nonce=evaluated["nonce"],
    )
    try:
        result = call_protected_tool(
            authority=reserved["execution_authority"],
            action_hash=evaluated["action_hash"],
            policy_hash=evaluated["policy_hash"],
            target=target,
        )
        outcome = {"tool_executed": result.get("tool_executed", False), "tool_result": result}
        client.record_execution(
            decision_id,
            tenant_id=TENANT_ID,
            actor_id=ACTOR_ID,
            session_id=SESSION_ID,
            action_hash=evaluated["action_hash"],
            nonce=evaluated["nonce"],
            outcome=outcome,
        )
    except Exception as exc:
        try:
            client.record_execution(
                decision_id,
                tenant_id=TENANT_ID,
                actor_id=ACTOR_ID,
                session_id=SESSION_ID,
                action_hash=evaluated["action_hash"],
                nonce=evaluated["nonce"],
                outcome={"tool_error": type(exc).__name__},
            )
        except Exception:
            pass
        raise

    return {
        "executed": True,
        "decision": "ALLOW",
        "decision_id": decision_id,
        "action_hash": evaluated["action_hash"],
        "policy_hash": evaluated["policy_hash"],
        "evidence": _evidence(client, decision_id),
        "replay": _replay(client, decision_id),
    }


@mcp.tool()
def protected_production_delete(target: str) -> dict[str, Any]:
    """Attempt a high-impact production deletion. This demo action is expected to be denied by policy."""
    client = gate()
    evaluated = client.evaluate(
        tenant_id=TENANT_ID,
        agent_id=AGENT_ID,
        actor_id=ACTOR_ID,
        session_id=SESSION_ID,
        action="delete_file",
        target=target,
        parameters={"target": target},
    )
    decision_id = evaluated["decision_id"]
    return {
        "executed": False,
        "decision": evaluated["decision"],
        "decision_id": decision_id,
        "reason": evaluated.get("reason"),
        "evidence": _evidence(client, decision_id),
        "replay": _replay(client, decision_id),
    }


@mcp.tool()
def get_action_gate_evidence(decision_id: str) -> dict[str, Any]:
    """Retrieve the immutable decision evidence and replay result for a demo decision."""
    client = gate()
    return {
        "decision_id": decision_id,
        "evidence": _evidence(client, decision_id),
        "replay": _replay(client, decision_id),
    }


if __name__ == "__main__":
    # Containers must bind to all interfaces so the reverse proxy can reach the MCP server.
    mcp.run(transport="streamable-http")
