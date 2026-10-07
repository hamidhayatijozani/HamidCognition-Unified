from __future__ import annotations

import json
import os
import time
import urllib.request
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.auth.middleware.auth_context import get_access_token
from pydantic import AnyHttpUrl

from action_gate_sdk import ActionGateClient, ActionGateError


GATE_URL = os.getenv("ACTION_GATE_URL", "http://127.0.0.1:8000")
TOOL_URL = os.getenv("PROTECTED_TOOL_URL", "http://127.0.0.1:9000")
GATE_TOKEN = os.getenv("ACTION_GATE_API_TOKEN")
STATIC_MCP_BEARER_TOKEN = os.getenv("MCP_BEARER_TOKEN")
MCP_ISSUER_URL = os.getenv("MCP_ISSUER_URL", "https://auth.example.com")
MCP_RESOURCE_URL = os.getenv("MCP_RESOURCE_URL", "http://127.0.0.1:8787/mcp")
MCP_REQUIRED_SCOPE = os.getenv("MCP_REQUIRED_SCOPE", "mcp:execute")
TENANT_ID = os.getenv("DEMO_TENANT_ID", "chatgpt-demo")
ACTOR_ID = os.getenv("DEMO_ACTOR_ID", "chatgpt-user")
AGENT_ID = os.getenv("DEMO_AGENT_ID", "chatgpt-demo-agent")
SESSION_ID = os.getenv("DEMO_SESSION_ID", "chatgpt-demo-session")


class StaticBearerTokenVerifier(TokenVerifier):
    """Demo verifier. Replace with a real OAuth/OIDC JWT or introspection verifier."""

    async def verify_token(self, token: str) -> AccessToken | None:
        if not STATIC_MCP_BEARER_TOKEN or token != STATIC_MCP_BEARER_TOKEN:
            return None
        return AccessToken(
            token=token,
            client_id=os.getenv("MCP_CLIENT_ID", "chatgpt-demo-client"),
            scopes=[MCP_REQUIRED_SCOPE],
            expires_at=int(time.time()) + int(os.getenv("MCP_TOKEN_TTL_SECONDS", "3600")),
            subject=os.getenv("MCP_SUBJECT", ACTOR_ID),
        )


mcp_kwargs: dict[str, Any] = {
    "instructions": (
        "Demonstration MCP server for HamidCognition Action Gate. "
        "Every protected action is evaluated by Action Gate before the protected "
        "tool is reached. The server exposes the resulting decision and evidence."
    ),
    "stateless_http": True,
    "json_response": True,
    "host": os.getenv("MCP_HOST", "0.0.0.0"),
    "port": int(os.getenv("MCP_PORT", "8787")),
}

if STATIC_MCP_BEARER_TOKEN:
    mcp_kwargs["token_verifier"] = StaticBearerTokenVerifier()
    mcp_kwargs["auth"] = AuthSettings(
        issuer_url=AnyHttpUrl(MCP_ISSUER_URL),
        resource_server_url=AnyHttpUrl(MCP_RESOURCE_URL),
        required_scopes=[MCP_REQUIRED_SCOPE],
    )

mcp = FastMCP("HamidCognition Action Gate Demo", **mcp_kwargs)


def gate() -> ActionGateClient:
    return ActionGateClient(GATE_URL, token=GATE_TOKEN)


def caller_identity() -> tuple[str, str, str, str]:
    """Use the authenticated principal as the source of identity when bearer auth is enabled."""
    token = get_access_token()
    if token is None:
        return TENANT_ID, ACTOR_ID, AGENT_ID, SESSION_ID

    subject = token.subject or ACTOR_ID
    return (
        os.getenv("MCP_AUTHENTICATED_TENANT_ID", TENANT_ID),
        subject,
        os.getenv("MCP_AUTHENTICATED_AGENT_ID", AGENT_ID),
        os.getenv("MCP_AUTHENTICATED_SESSION_ID", SESSION_ID),
    )


def call_protected_tool(*, authority: str, action_hash: str, policy_hash: str, target: str, tenant_id: str) -> dict[str, Any]:
    payload = {
        "tenant_id": tenant_id,
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
            "X-Tenant-ID": tenant_id,
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read())


def _evidence(client: ActionGateClient, decision_id: str, tenant_id: str) -> dict[str, Any]:
    try:
        return client.evidence(decision_id, tenant_id)
    except ActionGateError as exc:
        return {"error": str(exc)}


def _replay(client: ActionGateClient, decision_id: str, tenant_id: str) -> dict[str, Any]:
    try:
        return client.replay(decision_id, tenant_id)
    except ActionGateError as exc:
        return {"error": str(exc)}


@mcp.tool(annotations={"readOnlyHint": True})
def protected_read_public_file(target: str) -> dict[str, Any]:
    """Read a demo public resource through the real Action Gate -> authority -> protected-tool path."""
    tenant_id, actor_id, agent_id, session_id = caller_identity()

    if not target.startswith("/public/"):
        return {
            "executed": False,
            "decision": "DENY",
            "reason": "demo_tool_only_allows_public_targets",
        }

    client = gate()
    evaluated = client.evaluate(
        tenant_id=tenant_id,
        agent_id=agent_id,
        actor_id=actor_id,
        session_id=session_id,
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
            "evidence": _evidence(client, decision_id, tenant_id),
            "replay": _replay(client, decision_id, tenant_id),
        }

    reserved = client.reserve_execution(
        decision_id,
        tenant_id=tenant_id,
        actor_id=actor_id,
        session_id=session_id,
        action_hash=evaluated["action_hash"],
        nonce=evaluated["nonce"],
        world_version=evaluated.get("world_version"),
    )
    try:
        result = call_protected_tool(
            authority=reserved["execution_authority"],
            action_hash=evaluated["action_hash"],
            policy_hash=evaluated["policy_hash"],
            target=target,
            tenant_id=tenant_id,
        )
        outcome = {"tool_executed": result.get("tool_executed", False), "tool_result": result}
        client.record_execution(
            decision_id,
            tenant_id=tenant_id,
            actor_id=actor_id,
            session_id=session_id,
            action_hash=evaluated["action_hash"],
            nonce=evaluated["nonce"],
            outcome=outcome,
        )
    except Exception as exc:
        try:
            client.record_execution(
                decision_id,
                tenant_id=tenant_id,
                actor_id=actor_id,
                session_id=session_id,
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
        "evidence": _evidence(client, decision_id, tenant_id),
        "replay": _replay(client, decision_id, tenant_id),
    }


@mcp.tool(annotations={"readOnlyHint": False})
def protected_production_delete(target: str) -> dict[str, Any]:
    """Attempt a high-impact production deletion. This demo action is expected to be denied by policy."""
    tenant_id, actor_id, agent_id, session_id = caller_identity()
    client = gate()
    evaluated = client.evaluate(
        tenant_id=tenant_id,
        agent_id=agent_id,
        actor_id=actor_id,
        session_id=session_id,
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
        "evidence": _evidence(client, decision_id, tenant_id),
        "replay": _replay(client, decision_id, tenant_id),
    }


@mcp.tool(annotations={"readOnlyHint": True})
def get_action_gate_evidence(decision_id: str) -> dict[str, Any]:
    """Retrieve the immutable decision evidence and replay result for a demo decision."""
    tenant_id, _, _, _ = caller_identity()
    client = gate()
    return {
        "decision_id": decision_id,
        "evidence": _evidence(client, decision_id, tenant_id),
        "replay": _replay(client, decision_id, tenant_id),
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
