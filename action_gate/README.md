# HamidCognition Action Gate v1.1.1

**Runtime Action Governance with Replayable Decision Evidence**

This directory contains the executable product. It is deliberately narrower than the broader HamidCognition research program.

## Product contract

`Agent -> Action Gate -> Decision -> Enforcement -> Tool -> Outcome -> Evidence -> Replay`

The Gate independently evaluates risk. `risk_hint` from an agent is untrusted and cannot lower intrinsic risk.

Runtime decisions: `ALLOW`, `DENY`, `ASK`, `SANDBOX`. `DEFER` remains outside the current executable policy surface.

## Enforced controls

- tenant-bound evidence access and cross-tenant denial
- immutable policy snapshot plus policy hash inside each decision record
- action hash bound to tenant, actor, action, target and parameters
- cryptographic decision signature material with environment-driven key rotation and historical-key verification
- explicit actor and session identity binding from request through execution
- production approval signatures bound to approver, tenant, action and policy
- versioned policy configuration with deterministic policy hash
- dependency-free Python SDK for the core HTTP contract
- decision expiry and one-time execution nonce
- approval bound to tenant, action hash and policy version
- append-only audit events linked by a SHA-256 hash chain
- durable PostgreSQL storage for deployments, SQLite retained for local development
- HTTP enforcement adapter and MCP `tools/call` adapter
- forged decision, altered action and replay attempts rejected
- execution is reserved atomically before the HTTP/MCP tool side effect; final outcome, consumed state, record version, and audit event are committed atomically after the tool response
- direct tool calls require a Gate-issued, tenant/action/expiry/nonce-bound execution authority
- Compose stack configuration with PostgreSQL and Caddy TLS termination

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

## Getting started in 60 seconds (local demo)

This is a local development demo, not a deployment or customer acceptance test. It requires Python 3.11+ and a terminal.

Terminal 1:

```bash
cd action_gate
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8000
```

Terminal 2, from the same `action_gate` directory and virtual environment:

```bash
python demo.py
```

The demo calls the running local API. It exits with an error if the API is not reachable. The default local development database is SQLite; this does not validate PostgreSQL configuration, TLS, customer credentials, or runtime health.

## Environment template

A template is provided at `.env.example` for `docker-compose.production.yml`. Copy it to `.env`, replace every `REPLACE_ME_...` value with a unique cryptographically random secret, set `DOMAIN` to a DNS name that points to the deployment host, and keep `.env` out of Git. Never use the example values as real credentials.

Generate each secret independently, for example with `openssl rand -hex 32`. Do not reuse one secret across variables.

## Local development

```bash
cd action_gate
pip install -r requirements.txt
uvicorn app:app --reload
python demo.py
```

Local development defaults to SQLite when `ACTION_GATE_DATABASE_URL` is absent.

## Deployment configuration

Requirements: Docker Compose, a DNS record pointing `DOMAIN` to the deployment host, and generated secrets.

```bash
cd action_gate
export DOMAIN=gate.example.com
export POSTGRES_PASSWORD='<strong-random-password>'
export ACTION_GATE_API_TOKEN='<strong-random-token>'
export ACTION_GATE_SIGNING_SECRET='<strong-random-secret>'
export ACTION_GATE_APPROVAL_SECRET='<strong-random-secret>'
export ACTION_GATE_REQUIRE_SESSION_BINDING='1'
docker compose -f docker-compose.production.yml up -d --build
```

The configured stack is:

```text
Internet -> Caddy TLS -> enforcement -> Action Gate -> PostgreSQL
                                      \-> tool
```

Caddy terminates HTTPS and obtains certificates for the configured domain. PostgreSQL, the tool service and the enforcement service are intended to remain private to the Compose network.

Do not commit secrets. For rotation, configure `ACTION_GATE_SIGNING_KEYS` as a JSON object of key IDs to secrets and set `ACTION_GATE_KEY_ID` to the active key.

## Integration tests

```bash
python enforcement_integration.py
python mcp_integration.py
pytest -q
```

The integration tests exercise real local processes. They cover denied actions, allowed execution, exact action binding, forged decisions, one-time nonce replay and direct-tool bypass rejection. `test_production_storage.py` verifies the storage abstraction and deployment configuration.

## Reproduce

Tests run against local fixtures — no production database or live tools required.

## Coverage boundaries
- In scope: tool-call binding, single-use authority, evidence persistence, tenant isolation
- Out of scope: model alignment, prompt-injection defense, rate limiting, cost governance
- Not production-hardened: no SLA, no load testing claims

## Current product boundary

HSM/KMS custody, external identity federation, SIEM integration and HA orchestration remain deployment-specific controls and are not represented as implemented features.

`SANDBOX` means **sandbox-required decision state**. It is not proof that a real isolation sandbox has been provisioned.

No decision is claimed to be objectively correct or safe. The product records, constrains and enforces a decision under a versioned policy and its available evidence.
