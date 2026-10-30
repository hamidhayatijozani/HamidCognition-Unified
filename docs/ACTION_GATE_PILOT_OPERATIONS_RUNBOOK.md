# Action Gate / BESAZ — Limited Pilot Operations Runbook

This runbook is the operational handoff for a **restricted, non-production pilot**. Passing GitHub Actions proves the checked-in CI path, not that a public deployment exists or that a customer has accepted the product.

## 1. Deployment boundary

- Start with one isolated tenant and non-sensitive, reversible test actions.
- Do not connect unrestricted tools, production credentials, payment rails, or real-money trading.
- Keep Action Gate, PostgreSQL, enforcement, and tool services on the private Compose network.
- Expose only a reviewed TLS reverse proxy or authenticated tunnel. The production Compose file does not by itself establish public TLS, DNS, or a deployed endpoint.
- Keep a rollback path: stop the stack and revoke pilot credentials before deleting data or volumes.

## 2. Required configuration

Copy `PRODUCT/.env.production.example` to `action_gate/.env.production` on the deployment host, replace every placeholder, and run `chmod 600 action_gate/.env.production`. Never commit the resulting file.

Required values from the production Compose contract:
- `POSTGRES_PASSWORD`
- `ACTION_GATE_API_TOKEN`
- `ACTION_GATE_SIGNING_SECRET`
- `ACTION_GATE_AUTHORITY_SECRET`
- `ACTION_GATE_STATE_ORACLE_SECRET`
- `ACTION_GATE_APPROVAL_SECRET`
- `MCP_BEARER_TOKEN`

Use unique, high-entropy values for every secret. Do not reuse one secret across roles. Restrict file permissions (`chmod 600 action_gate/.env.production`). Configure optional values only after reviewing the Compose file and the intended pilot policy. Do not paste secrets into CI logs, issues, chat, or screenshots.

## 3. Validate and start

Run from the repository root on the deployment host:

```sh
docker compose --env-file action_gate/.env.production -f action_gate/docker-compose.production.yml config --quiet
docker compose --env-file action_gate/.env.production -f action_gate/docker-compose.production.yml up -d --build
docker compose --env-file action_gate/.env.production -f action_gate/docker-compose.production.yml ps
```

If config validation fails, do not start. If any service is unhealthy or restarting, stop and inspect logs before allowing traffic:

```sh
docker compose --env-file action_gate/.env.production -f action_gate/docker-compose.production.yml logs --tail=200 postgres action-gate enforcement tool dashboard
```

The service names above must match the checked-in Compose file; if it changes, update this runbook with it.

## 4. Required acceptance checks

Record timestamp, Git commit, image/build identity, result, and redacted evidence for every check.

1. **Health:** PostgreSQL is healthy and the Action Gate `/health` endpoint reports `status=ok` with backend `postgresql`.
2. **Decision:** submit a harmless, reversible test action and capture the decision ID and policy snapshot.
3. **Enforcement:** prove a permitted test action reaches only the isolated test tool; prove a denied action does not reach it.
4. **Authority:** verify missing, expired, wrong-tenant, wrong-action, stale-world, and reused-nonce authority is rejected.
5. **HTTP/MCP parity:** replay the same canonical test cases through HTTP and MCP and compare decision, enforcement result, and evidence references.
6. **Durability:** create a test decision, restart the Action Gate service while retaining the PostgreSQL volume, then retrieve the same evidence and replay the decision. Confirm audit UPDATE/DELETE attempts fail in PostgreSQL.
7. **Access control:** unauthenticated and invalid-token requests fail closed; no internal service port is exposed publicly.
8. **Recovery:** demonstrate a rollback/credential-revocation procedure and preserve the evidence bundle.

A green CI job is not a substitute for checks against the actual pilot host. If a check has no raw evidence, mark it `UNKNOWN`, not PASS.

## 5. Go / No-Go

**GO for a limited pilot only when every required acceptance check above passes on the target host**, a named operator can revoke access, and the customer explicitly approves scope and data handling.

**NO-GO** if database health, replay, nonce consumption, world revalidation, tenant isolation, HTTP/MCP parity, or deny enforcement is unproven. Do not route production actions while any item is UNKNOWN or FAIL.

## 6. Evidence bundle

Store the following outside the source repository in access-controlled storage:
- commit SHA and container image digests;
- redacted Compose validation output and service health;
- HTTP/MCP request and response fixtures with secrets removed;
- ALLOW and DENY enforcement traces;
- replay-after-restart result and audit immutability check;
- security exception list, operator, timestamp, and explicit Go/No-Go decision.

Do not include API tokens, signing keys, raw customer secrets, or unnecessary personal data.

## 7. Current known evidence boundary

The repository's Product Gates CI has exercised production Compose, PostgreSQL E2E, authenticated MCP, customer console E2E, and 200-event replay-after-restart. These are automated CI-container results. A real externally reachable deployment, TLS/DNS, customer acceptance, and revenue remain unverified until separately evidenced.
