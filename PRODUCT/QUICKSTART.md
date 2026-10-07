# Action Gate Quickstart

## Product

Action Gate is a deployable policy-enforcement boundary between an agent and protected tools. It evaluates an action, binds the decision to tenant/actor/session/action identity, records evidence, and authorizes execution only through the governed path.

The canonical product version is defined only by action_gate/VERSION. The published release identity is maintained in PRODUCT/CURRENT_COMMERCIAL_RELEASE.md. This document deliberately does not duplicate a version or release tag.

## Local deployment commands

From the repository root:

```bash
cp PRODUCT/.env.example .env
# Replace every REPLACE_IN_SECRET_MANAGER value with unique secrets.
# Also set POSTGRES_PASSWORD, DOMAIN, ACTION_GATE_API_TOKEN,
# ACTION_GATE_AUTHORITY_SECRET and MCP_BEARER_TOKEN.

docker compose -f action_gate/docker-compose.production.yml --env-file .env build
docker compose -f action_gate/docker-compose.production.yml --env-file .env up -d
docker compose -f action_gate/docker-compose.production.yml --env-file .env ps
docker compose -f action_gate/docker-compose.production.yml --env-file .env logs --tail=200 action-gate enforcement tool
```

The public edge is Caddy on ports 80/443. Action Gate and the protected tool are not directly published. Do not expose ports 8000 or 9000 to the Internet.

For a first non-production smoke test, keep production execution disabled and complete the acceptance procedure before enabling real execution.

## Production deployment

The production Compose definition is action_gate/docker-compose.production.yml.

1. Copy PRODUCT/.env.example into deployment-only configuration.
2. Generate unique values for API authentication, decision signing, approval signing, and enforcement secrets.
3. Set a real PostgreSQL password and domain.
4. Keep production execution disabled until the customer acceptance procedure passes.
5. Start the stack and verify Action Gate health.
6. Run the customer acceptance procedure from inside the Action Gate service.
7. Record version, commit/image digest, policy fingerprint, acceptance evidence, and rollback target.
8. Verify the tool authority nonce database is on the persistent production volume configured by the Compose file.

The smoke test is deliberately executed against the internal Action Gate API. The production edge does not publish the Action Gate API directly, which preserves the protected boundary.

## Acceptance

A running container is not an accepted security boundary. Acceptance requires evidence for identity binding, decision integrity, nonce single-use, expiry, tenant isolation, ALLOW/DENY/ASK/SANDBOX enforcement, evidence fail-closed behavior, persistence/replay, and absence of a direct downstream bypass.

## Delivery modes

SELF_HOSTED: customer operates the deployment.

MANAGED: HamidCognition operates the service boundary.

ENTERPRISE: negotiated integration, security review, support, and SLA scope.

No mode is a claim of universal safety, legal compliance, or guaranteed business outcome.
