# Action Gate Quickstart

## Product

Action Gate is a policy-enforcement boundary between an agent and protected tools. It evaluates an action, binds the decision to tenant/actor/session/action identity, records evidence, and authorizes execution only through the governed path.

The canonical product version is defined only by `action_gate/VERSION`. The published release identity is maintained in `PRODUCT/CURRENT_COMMERCIAL_RELEASE.md`.

## Controlled pilot deployment

Run from the repository root on the deployment host:

```bash
cp PRODUCT/.env.production.example action_gate/.env.production
chmod 600 action_gate/.env.production
# Replace every placeholder with a unique value or customer-specific endpoint.
# Keep the file on the deployment host; never commit it.

docker compose --env-file action_gate/.env.production -f action_gate/docker-compose.production.yml config --quiet
docker compose --env-file action_gate/.env.production -f action_gate/docker-compose.production.yml up -d --build
docker compose --env-file action_gate/.env.production -f action_gate/docker-compose.production.yml ps
docker compose --env-file action_gate/.env.production -f action_gate/docker-compose.production.yml logs --tail=200 postgres action-gate enforcement tool dashboard chatgpt-mcp
```

The production Compose contract requires independent values for API authentication, decision signing, execution authority, state-oracle signing, approval signing, enforcement authentication, PostgreSQL, and MCP bearer authentication. Do not reuse one secret across roles.

The public edge is Caddy on ports 80/443. Action Gate, PostgreSQL, enforcement internals, and the protected tool remain on the private Compose network. Do not expose ports 5432, 8000, or 9000 directly to the Internet.

## Initial pilot safety boundary

Start with one isolated tenant, one non-production protected tool, non-sensitive and reversible actions, and no production credentials, payment rails, or real-money activity.

**Important:** `ACTION_GATE_PRODUCTION_EXECUTION=false` in `PRODUCT/.env.example` is a template marker, not a runtime kill switch. Do not rely on that variable to prevent side effects. Isolation of the pilot tool, credentials, network, and test data is mandatory.

## Acceptance

The customer acceptance procedure is a checklist, not a single in-container command. Execute `PRODUCT/CUSTOMER_ACCEPTANCE.md` and `docs/ACTION_GATE_PILOT_OPERATIONS_RUNBOOK.md` against the actual pilot host.

A deployment is not accepted merely because containers are healthy. Required evidence includes identity and tenant binding, decision integrity, HTTP/MCP enforcement, stale-world rejection, nonce single-use under concurrency, fail-closed evidence handling, PostgreSQL persistence after restart, audit immutability, and direct-bypass rejection.

Record the exact release/version, source commit, image digest, policy fingerprint, timestamp, raw redacted results, rollback target, and customer sign-off. A green CI run is engineering evidence, not customer acceptance.

## Delivery modes

- SELF_HOSTED: customer operates the deployment.
- MANAGED: HamidCognition operates the service boundary under a separate written scope.
- ENTERPRISE: negotiated integration, security review, support, deployment architecture, and SLA scope.

No delivery mode is a claim of universal safety, legal compliance, or guaranteed business outcome.
