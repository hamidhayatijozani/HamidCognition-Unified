# Action Gate Customer Acceptance Test

## Purpose

This procedure verifies that a customer deployment preserves the security and execution boundary demonstrated by the current Action Gate v1.0.7 release.

## Required tests

### Identity binding
- production actor identity is required where configured;
- changing actor identity after evaluation cannot execute the decision;
- changing session identity when session binding is enabled cannot execute the decision.

### Decision integrity
- decision integrity verification succeeds;
- a protected endpoint rejects direct access without `X-Action-Gate-Authority` before its handler executes;
- a downstream tool rejects a call without Gate-issued execution authority;
- replaying the same authority concurrently permits at most one request to cross the enforcement barrier;
- action hash matches the execution request;
- tenant mismatch cannot retrieve or execute another tenant's decision;
- expired decisions are rejected;
- a consumed nonce cannot be reused;
- nonce reuse remains rejected after the tool service is restarted.

### Policy boundary
- ALLOW may cross the production execution boundary;
- DENY cannot execute;
- ASK cannot execute until the configured approval path changes the decision;
- SANDBOX cannot cross the production execution boundary.

### Policy-binding enforcement
- an execution authority with a mismatched policy digest is rejected at the protected tool boundary;
- a missing policy binding is rejected fail-closed;
- a valid authority with matching action and policy binding remains executable.

### Evidence failure
- failure to reserve or record execution fails closed;
- no downstream tool call is treated as authorized when evidence reservation fails.

### Persistence
- restart does not invalidate valid persisted decisions unexpectedly;
- replay after restart reproduces the stored decision and hashes;
- the execution-authority nonce database is stored on persistent production storage.

## Acceptance result

A deployment is accepted only when all required tests produce recorded evidence.

A passing test suite does not establish that customer policy is correct. Customer policy must be separately reviewed and versioned.

## Protected-tool bypass suite

The automated acceptance suite includes direct-access, replay, tenant-tampering, action-tampering, policy-binding-tampering, and atomic nonce-consumption tests. The production acceptance run must execute these tests against the same storage and deployment topology used by the protected tools.
