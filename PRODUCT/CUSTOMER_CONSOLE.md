# HamidCognition Customer Console

The repository now contains a browser-facing Action Gate console.

## Runtime

- Web console: dashboard/
- Console API: dashboard/app.py
- Action Gate API: action-gate:8000 on the private backend network
- Public entry: Caddy HTTPS on the configured DOMAIN
- MCP remains available at /mcp

## What is real

The console does not fake decisions. Its Evaluate buttons call the running Action Gate /v1/action/evaluate endpoint and display the returned decision ID, policy hash, action hash, nonce and evidence hash.

The destructive demo request targets production/customer-db and exercises the real policy path.

## Security boundary

The Action Gate API token stays inside the Docker network. Browser JavaScript never receives it. The console is a presentation and operator surface, not a replacement for Action Gate enforcement.

## Deployment

Use action_gate/docker-compose.production.yml with a real DOMAIN and production secrets. Caddy terminates HTTPS and routes / to the console, /mcp to the MCP service, and keeps the Action Gate enforcement path behind the edge.

This console is the first customer-visible surface. It is not a claim that TopChange payment detection is automatic.
