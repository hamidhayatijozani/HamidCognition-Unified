# Action Gate Customer Acceptance Test

## Purpose
This procedure verifies that a customer deployment preserves the security and execution boundary demonstrated by v1.0.0.

## Required tests

### Identity binding
- production actor identity is required where configured;
- changing actor identity after evaluation cannot execute the decision;
- changing session identity when session binding is enabled cannot execute the decision.

### Decision integrity
- decision integrity verification succeeds;
- action hash matches the execution request;
- tenant mismatch cannot retrieve or execute another tenant's decision;
- expired decisions are rejected;
- a consumed nonce cannot be reused.

### Policy boundary
- ALLOW may cross the production execution boundary;
- DENY cannot execute;
- ASK cannot execute until the configured approval path changes the decision;
- SANDBOX cannot cross the production execution boundary.

### Evidence failure
- failure to reserve or record execution fails closed;
- no downstream tool call is treated as authorized when evidence reservation fails.

### Persistence
- restart does not invalidate valid persisted decisions unexpectedly;
- replay after restart reproduces the stored decision and hashes.

## Acceptance result
A deployment is accepted only when all required tests produce recorded evidence.

A passing test suite does not establish that customer policy is correct. Customer policy must be separately reviewed and versioned.
