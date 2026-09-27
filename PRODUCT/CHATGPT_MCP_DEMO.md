# ChatGPT MCP Proof-of-Execution

## Purpose

This proof server exposes the existing HamidCognition Action Gate runtime through a real MCP Streamable HTTP endpoint.

It is an integration surface, not a second authorization engine.

The execution path is:

```
ChatGPT
  -> MCP /mcp
  -> HamidCognition MCP facade
  -> Action Gate /v1/action/evaluate
  -> execution reservation + Gate-issued authority
  -> protected tool
  -> execution finalization
  -> evidence + replay
```

The demo exposes three tools:

- `protected_read_public_file`: expected ALLOW path. It reaches the protected tool only after Action Gate authorization and authority verification.
- `protected_production_delete`: expected DENY path for a production target. The protected tool is not called.
- `get_action_gate_evidence`: retrieves the stored evidence and replay result for a decision.

The demo identity is intentionally fixed by environment variables. A production deployment must derive tenant, actor, agent, and session identity from authenticated caller context rather than tool arguments.

## Local run

Start the existing Action Gate and protected tool, then install the MCP dependency:

```bash
pip install -r action_gate/requirements-mcp.txt
```

Run:

```ACTION_GATE_URL=http://127.0.0.1:8000 \
PROTECTED_TOOL_URL=http://127.0.0.1:9000 \
ACTION_GATE_API_TOKEN=ci-test-token \
python action_gate/chatgpt_mcp_server.py
```

The MCP endpoint is:

```
http://127.0.0.1:8787/mcp
```

For ChatGPT, the endpoint must be reachable through HTTPS or Secure MCP Tunnel. OpenAI's current ChatGPT integration uses MCP Streamable HTTP and exposes custom MCP apps through Developer Mode.

## ChatGPT test script

1. Connect the server endpoint ending in `/mcp`.
2. Call `protected_read_public_file` with `/public/info.txt`.
3. Verify `decision=ALLOW`, `executed=true`, and `replay.match=true`.
4. Call `protected_production_delete` with `/production/data.db`.
5. Verify `decision=DENY`, `executed=false`, and that no protected-tool execution occurred.
6. Use `get_action_gate_evidence` with the returned decision ID.

This gives a buyer a live demonstration of the actual boundary rather than a slide describing the boundary.

## Deployment boundary

The MCP facade should remain separate from the protected tool network. The protected tool must not be directly exposed to ChatGPT.

For production, add OAuth or another supported authenticated MCP authorization flow, derive identity from the authenticated principal, and retain the Action Gate as the independent authorization boundary. OpenAI's current guidance recommends stable HTTPS Streamable HTTP endpoints and authenticated authorization for private or write-capable tools.
