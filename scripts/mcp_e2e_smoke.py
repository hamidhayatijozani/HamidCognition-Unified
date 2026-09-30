#!/usr/bin/env python3
"""End-to-end smoke test for the deployed Action Gate MCP endpoint.

Required:
  MCP_E2E_URL=https://example.com/mcp

Optional:
  MCP_E2E_BEARER_TOKEN=<token>
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.error


URL = os.environ.get("MCP_E2E_URL")
TOKEN = os.environ.get("MCP_E2E_BEARER_TOKEN")
if not URL:
    raise SystemExit("MCP_E2E_URL is required")

counter = 0


def rpc(method: str, params: dict | None = None, *, token: str | None = TOKEN, protocol_version: str | None = None):
    global counter
    counter += 1
    body = {
        "jsonrpc": "2.0",
        "id": counter,
        "method": method,
        "params": params or {},
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if protocol_version:
        headers["MCP-Protocol-Version"] = protocol_version

    req = urllib.request.Request(
        URL, data=json.dumps(body).encode(), headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read().decode()
            return response.status, dict(response.headers), raw
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode(errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {raw[:1000]}") from exc


def json_payload(raw: str):
    raw = raw.strip()
    if raw.startswith("data:"):
        parts = [line[6:].strip() for line in raw.splitlines() if line.startswith("data:")]
        raw = parts[-1] if parts else ""
    return json.loads(raw)


def result_from_tool(raw: str):
    message = json_payload(raw)
    if "error" in message:
        raise RuntimeError(message["error"])
    return message["result"]


def structured(result: dict):
    if "structuredContent" in result:
        return result["structuredContent"]
    for item in result.get("content", []):
        if item.get("type") == "text":
            try:
                return json.loads(item["text"])
            except json.JSONDecodeError:
                pass
    return result


status, _, raw = rpc(
    "initialize",
    {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "hamidcognition-e2e", "version": "1.0"},
    },
)
if status != 200:
    raise SystemExit(f"initialize failed: HTTP {status}")
init = json_payload(raw)
if "result" not in init:
    raise SystemExit(f"initialize returned no result: {init}")

negotiated_protocol = init["result"].get("protocolVersion", "2025-06-18")

status, _, raw = rpc("notifications/initialized", protocol_version=negotiated_protocol)
if status not in (200, 202):
    raise SystemExit(f"initialized notification failed: HTTP {status}")

status, _, raw = rpc("tools/list", protocol_version=negotiated_protocol)
tools_result = result_from_tool(raw)
tool_names = {tool.get("name") for tool in tools_result.get("tools", [])}
if not TOKEN:
    raise SystemExit("MCP_E2E_BEARER_TOKEN is required for the authenticated E2E")

try:
    rpc("tools/list", token=None, protocol_version=negotiated_protocol)
except RuntimeError as exc:
    if "HTTP 401" not in str(exc):
        raise SystemExit(f"unauthenticated request did not fail with HTTP 401: {exc}")
else:
    raise SystemExit("unauthenticated request unexpectedly succeeded")

try:
    rpc("tools/list", token="definitely-invalid-mcp-token", protocol_version=negotiated_protocol)
except RuntimeError as exc:
    if "HTTP 401" not in str(exc):
        raise SystemExit(f"invalid bearer token did not fail with HTTP 401: {exc}")
else:
    raise SystemExit("invalid bearer token unexpectedly succeeded")

required = {
    "protected_read_public_file",
    "protected_production_delete",
    "get_action_gate_evidence",
}
missing = required - tool_names
if missing:
    raise SystemExit(f"missing MCP tools: {sorted(missing)}")

status, _, raw = rpc(
    "tools/call",
    {
        "name": "protected_read_public_file",
        "arguments": {"target": "/public/e2e-smoke"},
    },
    protocol_version=negotiated_protocol,
)
allow = structured(result_from_tool(raw))
if allow.get("decision") != "ALLOW" or not allow.get("executed"):
    raise SystemExit(f"ALLOW path failed: {allow}")
decision_id = allow.get("decision_id")
if not decision_id:
    raise SystemExit(f"ALLOW path returned no decision_id: {allow}")

status, _, raw = rpc(
    "tools/call",
    {
        "name": "protected_production_delete",
        "arguments": {"target": "/production/e2e-smoke"},
    },
    protocol_version=negotiated_protocol,
)
deny = structured(result_from_tool(raw))
if deny.get("decision") != "DENY" or deny.get("executed"):
    raise SystemExit(f"DENY path failed: {deny}")

status, _, raw = rpc(
    "tools/call",
    {
        "name": "get_action_gate_evidence",
        "arguments": {"decision_id": decision_id},
    },
    protocol_version=negotiated_protocol,
)
evidence = structured(result_from_tool(raw))
if evidence.get("decision_id") != decision_id:
    raise SystemExit(f"EVIDENCE decision binding failed: {evidence}")
if "evidence" not in evidence or "replay" not in evidence:
    raise SystemExit(f"EVIDENCE/REPLAY path failed: {evidence}")

print(json.dumps({
    "status": "PASS",
    "endpoint": URL,
    "initialize": "PASS",
    "tools_list": sorted(tool_names),
    "allow": {"decision": allow.get("decision"), "decision_id": decision_id},
    "deny": {"decision": deny.get("decision"), "decision_id": deny.get("decision_id")},
    "evidence": "PASS",
    "replay": "PASS",
}, indent=2, sort_keys=True))
