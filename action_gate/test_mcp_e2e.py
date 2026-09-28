from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

BASE_URL = os.getenv("MCP_TEST_URL", "http://127.0.0.1:8787")
TOKEN = os.getenv("MCP_BEARER_TOKEN", "")


def rpc(method: str, params: dict, request_id: int) -> object:
    body = json.dumps({
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params,
    }, separators=(",", ":")).encode()
    req = urllib.request.Request(
        f"{BASE_URL}/mcp",
        data=body,
        headers={
            "content-type": "application/json",
            "accept": "application/json, text/event-stream",
            "authorization": f"Bearer {TOKEN}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        raw = response.read().decode()
    if raw.lstrip().startswith("data:"):
        chunks = [line[5:].strip() for line in raw.splitlines() if line.startswith("data:")]
        raw = chunks[-1] if chunks else "{}"
    return json.loads(raw)


def tool_call(name: str, arguments: dict, request_id: int) -> dict:
    response = rpc("tools/call", {"name": name, "arguments": arguments}, request_id)
    if not isinstance(response, dict):
        raise AssertionError(f"unexpected MCP response: {response!r}")
    return response


def main() -> None:
    if not TOKEN:
        raise SystemExit("MCP_BEARER_TOKEN is required")

    initialized = rpc(
        "initialize",
        {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "sbat-demo-e2e", "version": "1.0"},
        },
        1,
    )
    if not isinstance(initialized, dict) or "result" not in initialized:
        raise SystemExit(f"MCP initialize failed: {initialized!r}")

    allowed = tool_call(
        "protected_read_public_file",
        {"target": "/public/info.txt"},
        2,
    )
    result = allowed.get("result", {})
    structured = result.get("structuredContent", {}) if isinstance(result, dict) else {}
    if structured.get("decision") != "ALLOW" or structured.get("executed") is not True:
        raise SystemExit(f"ALLOW proof failed: {allowed!r}")
    if not structured.get("decision_id") or not structured.get("evidence") or not structured.get("replay"):
        raise SystemExit(f"ALLOW evidence proof failed: {allowed!r}")

    denied = tool_call(
        "protected_production_delete",
        {"target": "/production/data.db"},
        3,
    )
    denied_result = denied.get("result", {})
    denied_structured = denied_result.get("structuredContent", {}) if isinstance(denied_result, dict) else {}
    if denied_structured.get("decision") != "DENY" or denied_structured.get("executed") is not False:
        raise SystemExit(f"DENY proof failed: {denied!r}")
    if not denied_structured.get("decision_id") or not denied_structured.get("evidence"):
        raise SystemExit(f"DENY evidence proof failed: {denied!r}")

    evidence = tool_call(
        "get_action_gate_evidence",
        {"decision_id": structured["decision_id"]},
        4,
    )
    evidence_result = evidence.get("result", {})
    evidence_structured = evidence_result.get("structuredContent", {}) if isinstance(evidence_result, dict) else {}
    if evidence_structured.get("decision_id") != structured["decision_id"]:
        raise SystemExit(f"EVIDENCE lookup failed: {evidence!r}")
    if "evidence" not in evidence_structured or "replay" not in evidence_structured:
        raise SystemExit(f"EVIDENCE payload incomplete: {evidence!r}")

    print("MCP_E2E_ALLOW=PASS")
    print("MCP_E2E_DENY=PASS")
    print("MCP_E2E_EVIDENCE=PASS")


if __name__ == "__main__":
    main()
