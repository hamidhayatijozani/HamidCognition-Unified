# ChatGPT MCP Proof-of-Execution

## Product purpose

HamidCognition Action Gate can sit between an AI client and a protected tool exposed through MCP.

The product boundary is:

```
ChatGPT / Agent
    |
    | MCP Streamable HTTP
    v
HamidCognition MCP facade
    |
    | evaluate exact action
    v
Action Gate
    |
    | signed execution authority
    v
Protected Tool / MCP backend
    |
    +--> execution result
    |
    +--> evidence + replay
```

The MCP facade is an integration surface, not a second authorization engine.

## Demonstration tools

- `protected_read_public_file`: read-only ALLOW path. The protected tool is reached only after Action Gate evaluation and authority reservation.
- `protected_production_delete`: high-impact DENY path. It evaluates the action and returns evidence without calling the protected tool.
- `get_action_gate_evidence`: retrieves evidence and replay for a decision.

The read tool is annotated as read-only and the delete tool as write-capable so MCP-aware clients can reason about their impact.

## Identity model

Local/demo mode may use fixed environment identities.

Authenticated mode accepts a Bearer token at the MCP HTTP boundary. The current implementation contains a deliberately simple static-token verifier for proof and integration testing. It is not a production identity provider.

For a customer deployment, replace that verifier with an OAuth/OIDC JWT verifier or token introspection service. The MCP principal should then determine the tenant, actor, agent and session context passed into Action Gate. Do not accept those identities from tool arguments.

This follows the MCP authorization model: the MCP server is the resource server, verifies the bearer token, and obtains the authenticated principal from the validated token. citeturn3search3turn3search10

## Local run

Install the MCP dependency:

```bash
pip install -r action_gate/requirements-mcp.txt
```

Run the unauthenticated local proof:

```bash
ACTION_GATE_URL=http://127.0.0.1:8000 \
PROTECTED_TOOL_URL=http://127.0.0.1:9000 \
ACTION_GATE_API_TOKEN=ci-test-token \
python action_gate/chatgpt_mcp_server.py
```

The endpoint is:

```
http://127.0.0.1:8787/mcp
```

Authenticated local proof:

```export MCP_BEARER_TOKEN='replace-with-a-random-secret'
export MCP_RESOURCE_URL='http://127.0.0.1:8787/mcp'
export MCP_ISSUER_URL='https://auth.example.com'
python action_gate/chatgpt_mcp_server.py
```

The static verifier is intentionally a bridge to a real OAuth/OIDC verifier, not a claim of enterprise identity management.

## Temporary remote test

The repository includes `docker-compose.chatgpt-quick-tunnel.yml`, which creates a temporary Cloudflare Quick Tunnel.

Use it only for short-lived, non-sensitive demonstrations:

```bash
docker compose \
  -f action_gate/docker-compose.production.yml \
  -f action_gate/docker-compose.chatgpt-quick-tunnel.yml \
  up -d --build
```

Then inspect the tunnel log for the temporary `https://*.trycloudflare.com` endpoint and append `/mcp`.

Do not put customer data, credentials, destructive tools, or production systems behind an unauthenticated Quick Tunnel. Human beings have repeatedly demonstrated that "temporary" has a disturbing tendency to become "still running six months later."

## Stable deployment

For a customer or persistent demo:

1. Run the production Compose stack on a reachable host.
2. Give the host a stable DNS name.
3. Let Caddy terminate HTTPS.
4. Set `MCP_BEARER_TOKEN` only for bootstrap/integration testing, or connect the MCP resource server to a real OAuth/OIDC verifier.
5. Set `MCP_RESOURCE_URL=https://<domain>/mcp`.
6. Keep the protected tool on the private backend network. Never publish port 9000.
7. Keep Action Gate's signing, authority and database secrets outside source control.
8. Use a distinct tenant and principal for every customer.
9. Rotate temporary demo credentials after every public demonstration.

ChatGPT connects to remote MCP servers rather than directly to a local/private listener. OpenAI's current documentation says custom MCP apps are configured with a remote endpoint and can use an authentication mechanism; private/on-premises servers can use Secure MCP Tunnel. Full MCP/write support is currently rolling out for Business, Enterprise and Edu, while Pro supports custom MCP connections with read/fetch permissions. citeturn0search0turn0search7

## ChatGPT test sequence

For a live demonstration, use this exact sequence:

1. Connect the remote endpoint ending in `/mcp`.
2. Call `protected_read_public_file` with `/public/info.txt`.
3. Verify:
   - `decision=ALLOW`
   - `executed=true`
   - a decision ID exists
   - evidence exists
   - replay reports a matching decision
4. Call `protected_production_delete` with `/production/data.db`.
5. Verify:
   - `decision=DENY`
   - `executed=false`
   - the protected tool was not called
6. Call `get_action_gate_evidence` with the returned decision ID.
7. Show the buyer the chain: request → policy → decision → authority → execution/evidence.

The point of the demo is not that ChatGPT is safe. The point is that the protected tool has an independent authorization boundary and refuses to rely on agent intent alone.

## OpenAI API proof

The repository also contains `openai_remote_mcp_demo.py`. It uses the Responses API's remote MCP tool surface.

For an authenticated MCP server:

```bash
export OPENAI_API_KEY='...'
export MCP_SERVER_URL='https://<domain>/mcp'
export MCP_BEARER_TOKEN='...'
python action_gate/openai_remote_mcp_demo.py
```

The current OpenAI API reference supports a remote MCP `server_url`, an allowed-tool filter, optional approval settings, and HTTP headers for authentication. It also supports an OAuth authorization token when the application performs the OAuth flow. citeturn1search0

For a first proof, keep the allowed tools constrained to the two demo tools. Do not use `require_approval="never"` for destructive customer tools. The sample uses that setting only to make the non-destructive proof deterministic.

## What this proves

The current demo can establish the following narrow claim:

> A remote MCP tool invocation can be routed through HamidCognition Action Gate, authorized against the exact action context, executed only after authority is issued, and returned with evidence and replay.

It does not establish universal AI safety, correctness of customer policy, downstream system safety, regulatory certification, or security of an external identity provider.

## Production hardening boundary

Before a real customer deployment, replace or add:

- real OAuth/OIDC verification
- tenant/principal mapping
- secret rotation
- rate limits at the public edge
- observability and alerting
- durable evidence retention policy
- KMS/HSM-backed signing where required
- customer-specific policy configuration
- backup/restore and disaster recovery
- penetration testing and customer security review

The architecture deliberately keeps these concerns outside the narrow Action Gate decision boundary so that the core authorization claim remains testable.
