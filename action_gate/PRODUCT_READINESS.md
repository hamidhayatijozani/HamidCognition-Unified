# HamidCognition Action Gate — Product Readiness

## Product contract

HamidCognition Action Gate is a runtime governance service that evaluates an intended agent action before a tool call and records replayable decision evidence.

Runtime path:

`Agent → Action Gate → Decision → Enforcement → Tool → Outcome → Evidence → Replay`

The service exposes HTTP APIs and can sit in front of an HTTP or MCP tool boundary through the repository's enforcement proxy/adapters.

## Enforced decisions

- `ALLOW`: execution may proceed.
- `ASK`: execution is held until an approval is recorded.
- `DENY`: execution is rejected.
- `SANDBOX`: execution is permitted only through the controlled enforcement path.
- `DEFER`: reserved for future policy workflows; it is not executable by default.

The agent-supplied risk hint is retained as evidence but is not authoritative for the gate decision.

## Security invariants

1. Production requires API authentication and a signing secret.
2. Decision signatures bind decision ID, tenant, action digest, policy digest, nonce, and expiry.
3. Tenant mismatch does not reveal another tenant's decision record.
4. Action and nonce bindings are checked again at execution time.
5. A consumed nonce cannot be executed twice, including concurrent requests sharing the production database.
6. Approval is bound to tenant, action digest, policy version, and approval expiry.
7. HTTP and MCP execution are routed through the gate before tool invocation.
8. Direct tool access is rejected unless the enforcement attestation is valid.
9. Persistent records and append-only audit events support post-execution inspection and replay.
10. Evidence packaging is a gate, not a best-effort artifact: required acceptance evidence must exist or the product workflow fails.

## Verified boundary

The repository's product CI exercises product tests, the Validation Boundary suite, real HTTP enforcement, real MCP enforcement, production PostgreSQL/E2E smoke, 200-event decision replay, persistence replay after service restart, and the sellable-product readiness gate.

These tests establish only the properties they execute. They do not establish downstream business outcome safety, correctness of every customer policy, infrastructure security outside the tested deployment, resistance to every adversarial input, or replay of external world state and side effects.

## Operational requirements for a customer deployment

Set at minimum:

- `ACTION_GATE_ENV=production`
- `ACTION_GATE_API_TOKEN`
- `ACTION_GATE_SIGNING_SECRET`
- `ACTION_GATE_DATABASE_URL` for PostgreSQL deployments
- `ACTION_GATE_ENFORCEMENT_SECRET` for the enforcement proxy/tool boundary

Secrets must be injected by the deployment platform's secret manager, not committed to the repository.

## Commercial boundary

This repository now contains a testable product runtime and production deployment path. "Sellable" here means a customer can deploy and exercise the documented governance boundary with deterministic evidence. It is not a claim of regulatory certification, universal security, or guaranteed safety of downstream tools.

Remaining enterprise hardening is intentionally separated from the core product contract: asymmetric key rotation, authenticated principal/session binding, structured observability, and a versioned customer policy management surface. Production rate limiting is now database-backed and coordinated across replicas; one-time execution replay protection is durable and concurrency-safe through the shared database transaction boundary, with pre-execution reservation before tool side effects.
