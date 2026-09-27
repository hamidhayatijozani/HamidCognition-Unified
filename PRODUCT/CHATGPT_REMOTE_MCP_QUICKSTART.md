# ChatGPT / OpenAI Remote MCP Demo

This is a short-lived integration path for proving the real MCP surface from an OpenAI model.

## 1. Start the product

From the repository:

```bash
cd action_gate
export POSTGRES_PASSWORD=demo-postgres-password
export ACTION_GATE_API_TOKEN=demo-action-gate-token
export ACTION_GATE_SIGNING_SECRET=demo-signing-secret
export ACTION_GATE_APPROVAL_SECRET=demo-approval-secret
export ACTION_GATE_ENFORCEMENT_SECRET=demo-enforcement-secret
export ACTION_GATE_AUTHORITY_SECRET=demo-authority-secret

docker compose -f docker-compose.production.yml -f docker-compose.chatgpt-quick-tunnel.yml up -d --build
```

Then read the temporary public URL:

```bash
docker compose -f docker-compose.production.yml -f docker-compose.chatgpt-quick-tunnel.yml logs chatgpt-quick-tunnel
```

Cloudflare Quick Tunnels generate a temporary `trycloudflare.com` URL and are intended for testing/development, not production. citeturn5search1

The MCP endpoint is:

```text
https://<temporary-host>.trycloudflare.com/mcp
```

## 2. Test through the OpenAI API

Install:

```bash
pip install -r action_gate/requirements-openai-mcp.txt
```

Then:

```bash
export OPENAI_API_KEY='...'
export MCP_SERVER_URL='https://<temporary-host>.trycloudflare.com/mcp'
python action_gate/openai_remote_mcp_demo.py
```

The Responses API supports remote MCP tools with a `server_url`, tool filtering, and an explicit approval policy. citeturn4search0turn4search4

## 3. Test inside ChatGPT

For a custom ChatGPT MCP app, use the same `/mcp` endpoint in Developer Mode. OpenAI's current documentation says ChatGPT connects to remote MCP servers, and custom apps with full MCP/write support are currently available on Business and Enterprise/Edu; Pro can connect MCPs with read/fetch permissions. The setup is on ChatGPT web, not mobile. citeturn3search0

For a private/local server, OpenAI recommends Secure MCP Tunnel rather than exposing the origin directly. citeturn3search0

## Security boundary

This Quick Tunnel file is DEMO ONLY. It does not turn the MCP facade into a production authenticated service.

Production requirements remain:

- HTTPS or Secure MCP Tunnel
- authenticated MCP caller identity
- tenant/actor/agent/session derived from the authenticated principal
- protected tool kept off the public network
- managed tunnel/host instead of Quick Tunnel
- OAuth/OIDC or another supported authenticated MCP authorization flow

The Action Gate remains the independent authorization boundary.
