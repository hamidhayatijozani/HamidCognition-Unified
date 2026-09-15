# HamidCognition Action Gate v0.2

**Runtime Action Governance with Replayable Decision Evidence**

This directory is the executable product candidate. It is deliberately narrower than the broader HamidCognition research program.

## Secure product contract

`Agent -> Action Gate -> Decision -> Enforcement -> Tool -> Outcome -> Evidence -> Replay`

The Gate independently evaluates risk. `risk_hint` from an agent is untrusted and cannot lower intrinsic risk.

Decisions: `ALLOW`, `DENY`, `ASK`, `SANDBOX`, `DEFER`.

## v0.2 acceptance controls

- authenticated API when a token is configured; production mode refuses to start serving decisions without authentication configuration
- tenant-bound evidence access and cross-tenant denial
- immutable policy snapshot plus policy hash inside each decision record
- action hash bound to tenant, actor, action, target and parameters
- cryptographic decision signature material
- decision expiry and one-time execution nonce
- approval bound to tenant, action hash and policy version
- append-only audit events linked by a SHA-256 hash chain
- fail-closed enforcement when Gate/tool/evidence operations fail
- HTTP enforcement adapter
- MCP `tools/call` adapter
- forged decision, altered action and replay attempts rejected
- direct tool calls rejected unless a Gate-issued HMAC attestation is present

## API

```text
POST /v1/action/evaluate
POST /v1/action/{decision_id}/approve
POST /v1/action/{decision_id}/execution
GET  /v1/evidence/{decision_id}?tenant_id=...
GET  /v1/replay/{decision_id}?tenant_id=...
GET  /health
```

An Evidence Record contains tenant, actor, request, normalized action, action hash, nonce, policy version and snapshot, policy hash, independent risk assessment, evidence, decision, constraints, approval, execution, outcome, expiry, replay reference and decision signature.

## Local execution

```bash
cd action_gate
pip install -r requirements.txt
uvicorn app:app --reload
python demo.py
```

Expected decisions:

```text
delete production file => DENY
external customer email => ASK
financial transfer       => SANDBOX
```

## Real enforcement tests

```bash
python enforcement_integration.py
python mcp_integration.py
pytest -q
```

The integration gates exercise real processes, not mocks: Gate, enforcement proxy and tool server. They test denied actions, successful allowed execution, exact action binding, forged decisions, one-time nonce replay and direct-tool bypass rejection.

## Docker pilot stack

`docker-compose.yml` defines three services:

```text
Agent/client -> enforcement -> action-gate
                         \-> tool (attestation required)
```

Required environment variables are `ACTION_GATE_API_TOKEN` and `ACTION_GATE_ENFORCEMENT_SECRET`. Do not commit either secret.

The tool service is intentionally not exposed as a host port in Compose. The enforcement service is the host-facing boundary.

## Important scope limits

This is **Secure Multi-Tenant Enforcement MVP**, not an Enterprise production claim.

`SANDBOX` currently means **sandbox-required decision state**. It is not proof that a real isolation sandbox has been provisioned.

SQLite is retained for the MVP. A production pilot still needs PostgreSQL or equivalent durable concurrent storage, external identity/authorization, rate limiting, TLS, key management/rotation, operational metrics, stronger append-only storage, and network policy that prevents alternate direct routes to tools.

The HMAC enforcement secret is a shared-secret MVP mechanism, not a final enterprise key-management design.

MCP support is an executable adapter and integration gate, not a claim of complete protocol certification.

No decision is claimed to be objectively correct or safe. The product records, constrains and enforces a decision under a versioned policy and its available evidence.
