# Action Gate Security Boundary

## Trust boundary

caller/agent -> authenticated Action Gate -> identity binding -> policy evaluation -> evidence reservation -> execution authority -> governed enforcement adapter -> protected tool

A protected production tool must not have an alternate direct execution path.

## Fail-closed conditions

Protected execution stops when authentication is unavailable, decision integrity fails, tenant/actor/session/action binding fails, the decision is expired or its nonce is consumed, required evidence cannot be persisted, or the request falls outside the authorized decision boundary.

## Customer responsibilities

Customers control secret/key custody, infrastructure security, identity-provider configuration, PostgreSQL security and backup protection, policy correctness, downstream tool security, monitoring integrations, and regulatory obligations.

## Evidence rule

A security property becomes a product claim only when executable validation exists and the release evidence identifies the exact code and execution baseline.


## Protected-tool enforcement

Protected production endpoints must import `action_gate.enforcement.require_execution_authority` (or the equivalent SDK adapter) as a mandatory dependency. Requests without `X-Action-Gate-Authority` are rejected before the protected handler runs.

The authority is signed with the dedicated `ACTION_GATE_AUTHORITY_SECRET`. In production this secret is separate from `ACTION_GATE_API_TOKEN`, `ACTION_GATE_SIGNING_SECRET`, and `ACTION_GATE_APPROVAL_SECRET`. The caller/agent must never receive the authority secret.

The protected-tool layer verifies the authority signature, expiry, executable decision, tenant binding, action binding, and policy binding. It then consumes the nonce through the ACID-backed `authority_nonces` table. The database uniqueness constraint makes concurrent replay attempts fail atomically.

The authority token is integrity-protected, not encrypted. It is a short-lived signed artifact and therefore must be transported over TLS and treated as sensitive.

The protected tool remains responsible for comparing the verified authority context with the exact action it is about to execute. A valid authority for one tenant/action/policy is not authorization for another.


### Execution-authority nonce retention

Consumed authority nonces are retained in the configured database and can be purged by trusted operations staff with:

`python scripts/cleanup_authority_nonces.py --older-than-seconds 86400`

The retention interval must be chosen to exceed the maximum replay-relevant evidence window. Purging removes replay-prevention records, so it must not be configured shorter than the operational authority lifetime plus the required audit window.

### Reference protected-tool boundary

`protected_tools/reference_tool.py` is a side-effect-free reference runtime used to prove the boundary and acceptance tests. It requires `Depends(require_execution_authority)` and then binds tenant, action and policy digests before returning an execution result.

The nonce transaction prevents the same authority from being accepted twice by the Gate boundary. It does not by itself provide distributed exactly-once semantics for an arbitrary downstream external system. A real side effect must additionally use an idempotency key or transactional mechanism appropriate to that downstream system.
