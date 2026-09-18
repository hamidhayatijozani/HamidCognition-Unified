# Action Gate Operations Runbook

## Health

Monitor runtime availability and dependency health. A healthy process is not equivalent to a healthy enforcement boundary.

## Key signals

Track at minimum:

- request count
- decisions by ALLOW/DENY/ASK/SANDBOX
- decision latency
- execution latency
- authentication failures
- actor/session binding mismatches
- nonce reuse attempts
- evidence reservation/persistence failures
- database connection failures
- replay/validation failures

## Incident priority

### Evidence failure

If required evidence cannot be reserved or persisted, production execution must remain blocked. Restore the evidence path before reopening production execution.

### Identity mismatch

A binding mismatch is a security event. Investigate actor, session, tenant, nonce, and correlation data. Do not bypass the gate to restore throughput.

### Database failure

Treat inability to persist required audit/evidence state as fail-closed for protected production actions.

### Unexpected decision distribution

A sudden change in DENY/ASK/SANDBOX/ALLOW distribution should be investigated as a policy/configuration or integration change.

## Recovery

1. Preserve incident evidence.
2. Record version and configuration fingerprint.
3. Confirm dependency health.
4. Restore persistence if needed.
5. Run acceptance/replay checks.
6. Re-enable production execution only after the boundary is verified.
7. Record recovery evidence.

## Backup/restore

Backups must include the persistent evidence store and must be periodically restored into an isolated environment. A backup that has never been restored is a hypothesis wearing a file extension.

## Change control

Every production change should identify:

- previous version
- new version
- commit/image digest
- configuration change
- acceptance evidence
- rollback target
