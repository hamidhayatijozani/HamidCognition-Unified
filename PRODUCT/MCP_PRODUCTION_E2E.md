# MCP Production E2E Verification

This repository contains a manual GitHub Actions workflow that verifies the deployed Streamable HTTP MCP endpoint from outside the deployment network.

## Required repository secrets

- `MCP_E2E_URL`: the public HTTPS MCP endpoint, for example `https://example.example/mcp`.
- `MCP_E2E_BEARER_TOKEN`: the bearer token configured for the MCP server. Leave unset only when the deployment intentionally runs without bearer authentication.

## What the test proves

The workflow performs the following sequence against the live endpoint:

1. MCP `initialize`.
2. MCP `tools/list`.
3. ALLOW path through `protected_read_public_file`.
4. DENY path through `protected_production_delete`.
5. Evidence and replay retrieval through `get_action_gate_evidence`.

A PASS proves that the endpoint is reachable over HTTPS, speaks the expected MCP protocol, exposes the governed tools, and completes the three product demonstration paths against the deployed system.

It does not prove universal security, customer policy correctness, regulatory compliance, or arbitrary downstream exactly-once semantics.

## Run

Open GitHub Actions and manually dispatch **MCP Production E2E** after the deployment is live.

Record the workflow run URL, commit SHA, endpoint, and resulting evidence with the deployment acceptance record.

The test source is `scripts/mcp_e2e_smoke.py`.


## Ephemeral evidence

The repository also contains a self-contained ephemeral HTTPS E2E workflow at
`.github/workflows/mcp-ephemeral-e2e.yml`. It builds the production Compose stack,
starts a temporary Cloudflare Quick Tunnel, verifies the authenticated MCP boundary,
executes both the ALLOW and DENY paths, retrieves evidence/replay, and uploads the
machine-readable result as the `mcp-ephemeral-e2e-evidence` artifact.

The ephemeral workflow is a transport and integration proof. It does not establish
that a customer's permanent hostname, identity provider, TLS configuration, or
ChatGPT client integration is production-ready. Those remain separate deployment
proofs.
