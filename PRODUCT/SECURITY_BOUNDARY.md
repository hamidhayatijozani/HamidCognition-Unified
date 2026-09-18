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
