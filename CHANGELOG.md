# Changelog

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
