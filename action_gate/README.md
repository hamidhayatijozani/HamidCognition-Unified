# HamidCognition Action Gate v0.4.2

**Runtime Action Governance with Replayable Decision Evidence**

This directory contains the executable product. It is deliberately narrower than the broader HamidCognition research program.

## Product contract

`Agent -> Action Gate -> Decision -> Enforcement -> Tool -> Outcome -> Evidence -> Replay`

The Gate independently evaluates risk. `risk_hint` from an agent is untrusted and cannot lower intrinsic risk.

Runtime decisions: `ALLOW`, `DENY`, `ASK`, `SANDBOX`. `DEFER` remains outside the current executable policy surface.

## Enforced controls

- production authentication is fail-closed when configuration is missing
- tenant-bound evidence access and cross-tenant denial
- immutable policy snapshot plus policy hash inside each decision record
- action hash bound to tenant, actor, action, target and parameters
- cryptographic decision signature material
- decision expiry and one-time execution nonce
- approval bound to tenant, action hash and policy version
- append-only audit events linked by a SHA-256 hash chain
- durable PostgreSQL storage for production deployments, SQLite retained only for local development
- HTTP enforcement adapter and MCP `tools/call` adapter
- forged decision, altered action and replay attempts rejected
- execution is reserved atomically before the HTTP/MCP tool side effect; final outcome is recorded only after the tool response
- direct tool calls rejected unless a Gate-issued HMAC attestation is present
- production Compose stack with PostgreSQL and Caddy TLS termination

## API

```text
POST /v1/action/evaluate
POST /v1/action/{decision_id}/approve
POST /v1/action/{decision_id}/execution/reserve
POST /v1/action/{decision_id}/execution
GET  /v1/evidence/{decision_id}?tenant_id=...
GET  /v1/replay/{decision_id}?tenant_id=...
GET  /health
```

An Evidence Record contains tenant, actor, request, normalized action, action hash, nonce, policy version and snapshot, policy hash, independent risk assessment, evidence, decision, constraints, approval, execution, outcome, expiry, replay reference and decision signature.

## Local development

```bash
cd action_gate
pip install -r requirements.txt
uvicorn app:app --reload
python demo.py
```

Local development defaults to SQLite when `ACTION_GATE_DATABASE_URL` is absent.

## Production deployment

Requirements: Docker Compose, a DNS record pointing `DOMAIN` to the deployment host, and generated secrets.

```bash
cd action_gate
export DOMAIN=gate.example.com
export POSTGRES_PASSWORD='<strong-random-password>'
export ACTION_GATE_API_TOKEN='<strong-random-token>'
export ACTION_GATE_SIGNING_SECRET='<strong-random-secret>'
export ACTION_GATE_ENFORCEMENT_SECRET='<strong-random-secret>'
docker compose -f docker-compose.production.yml up -d --build
```

The production stack is:

```text
Internet -> Caddy TLS -> enforcement -> Action Gate -> PostgreSQL
                                      \-> tool
```

Caddy terminates HTTPS and obtains certificates for the configured domain. PostgreSQL is not exposed to the host. The tool service is not exposed to the host. The enforcement service is also private to the Compose network and is reached through the TLS edge.

Do not commit production secrets.

## Integration tests

```bash
python enforcement_integration.py
python mcp_integration.py
pytest -q
```

The integration gates exercise real processes rather than mocks. They cover denied actions, allowed execution, exact action binding, forged decisions, one-time nonce replay and direct-tool bypass rejection. `test_production_storage.py` verifies the storage abstraction and production deployment configuration.

## Current product boundary

This release moves the runtime to a production-oriented PostgreSQL/TLS deployment path and hardens one-time execution against concurrent replay with a durable database-backed nonce claim. It does **not** claim full enterprise readiness. External identity federation, distributed rate limiting, managed key rotation/HSM integration, SIEM connectors, HA orchestration and customer-specific compliance evidence remain deployment/customer layers rather than fabricated features.

`SANDBOX` means **sandbox-required decision state**. It is not proof that a real isolation sandbox has been provisioned.

No decision is claimed to be objectively correct or safe. The product records, constrains and enforces a decision under a versioned policy and its available evidence.
