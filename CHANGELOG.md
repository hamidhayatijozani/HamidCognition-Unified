# Changelog

## Unreleased — Deterministic BESAZ Sandbox Metrics

- Normalize the externally visible BESAZ sandbox `delta` metric with `round(delta, 10)` so replay, serialization and exact comparisons are stable across IEEE-754 representation noise.
- Treat the 10-decimal normalization as the metric's deterministic output contract; do not generalize this precision policy to unrelated metrics without defining their required scale.


## 1.0.2 — Execution Authority Boundary

- Put the previously dormant security-authority primitive on the real execution path.
- Issue a Gate-signed execution authority only after atomic reservation and bind it to decision, tenant, action digest, policy digest, nonce and expiry.
- Make the downstream tool reject calls without valid Gate-issued authority.
- Remove the separate enforcement-only attestation secret from the production path.
- Add explicit edge/backend network segmentation in production Compose.
- Add negative tests for direct tool bypass and tampered execution authority.

## 1.0.1 — Execution Evidence Integrity

- Atomically finalize execution outcome, one-time consumption, record version, and audit event in one database transaction.
- Preserve the append-only audit hash chain during concurrent execution finalization.
- Make production session binding fail-closed by default unless explicitly configured otherwise.
- Stop persisting raw bearer credentials in production rate-limit keys by storing a deterministic credential fingerprint instead.
- Added regression coverage for atomic finalization and one-time finalization semantics.


## 0.4.1 — Execution Boundary Hardening

- Added durable database-backed production rate limiting with tenant-scoped keys.
- Added atomic pre-execution reservation so HTTP and MCP tool calls cannot race through the one-time execution boundary.
- Added concurrent reservation and durable rate-limit tests.
- Production containers now run as a dedicated non-root user.


## 0.4.0 — Action Gate Product Readiness

- Added signed security-authority primitives with tenant, action, policy, expiry and nonce binding.
- Added production-mode sellable readiness gate covering authentication, tenant isolation, decision signatures, replay, single-use execution and human approval.
- Strengthened product evidence packaging so required production evidence is a hard gate.
- Verified real HTTP and MCP enforcement, PostgreSQL production deployment, 200-event decision replay and persistence replay after service restart in product CI.
- Added independent EXP-004 semantic validation and adversarial EXP-005 validator testing.
- Added explicit claim boundaries distinguishing decision replay from world-state replay and distinguishing evidence validation from universal safety claims.

## Boundary

This release is a deployable product candidate, not a regulatory certification or a guarantee of downstream business outcome safety. Enterprise deployment still requires customer-specific identity federation, secret/key lifecycle management, observability/SIEM integration and compliance controls where applicable.
