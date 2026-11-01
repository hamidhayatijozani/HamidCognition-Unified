# Security & Authority Gate

This document describes the current execution-authority boundary and separates verified single-instance behavior from controls that remain unproven.

## Acceptance invariants

- **Decision binding:** a signed authority is bound to one decision, tenant, canonical action digest, policy digest, nonce, issue time, and expiry.
- **Forgery resistance:** malformed or invalidly signed authority is denied.
- **Expiry:** authorities outside their validity interval are denied.
- **Tenant isolation:** an authority issued for tenant A cannot authorize tenant B.
- **Executable decision set:** only `ALLOW` and the explicitly supported `SANDBOX` authority type can pass the authority primitive. The production tool boundary must still enforce its configured sandbox restrictions; a decision label alone does not create an isolation sandbox.
- **Action/policy binding:** the protected tool validates the actual request payload against the Gate decision before consuming the nonce.
- **World-state binding:** when live world revalidation is enabled, missing or changed world version is rejected before the protected tool side effect.
- **Single use:** a consumed or concurrently claimed nonce cannot authorize a second execution on the same configured persistence boundary.
- **Fail closed:** missing authority, invalid configuration, Gate revalidation failure, invalid bindings, and persistence errors must not result in tool execution.

## Persistence boundaries

There are two distinct nonce stores in the current implementation:

1. **Action Gate authority nonce:** `enforcement.py` calls `storage.consume_authority_nonce`. With PostgreSQL configured, the store uses a unique nonce row and `INSERT ... ON CONFLICT DO NOTHING RETURNING` so only one concurrent claim succeeds. Decision-level execution reservation also uses a conditional database update before the external side effect.
2. **Protected-tool nonce:** `tool_server.py` maintains a separate SQLite nonce registry at `TOOL_NONCE_DB`. Production Compose mounts this path under the persistent `tool_data:/data` volume. This survives a container restart only while that volume is retained. It is not a shared multi-replica database.

**Pilot topology constraint:** use one protected-tool instance and preserve/back up the `tool_data` volume. Horizontal scaling, multi-host failover, or a claim of distributed nonce consistency is not supported by the evidence in this release line. A shared transactional nonce backend and cross-replica race tests are required before such a topology is allowed.

## World-state and adapter boundary

- The protected tool requires a valid Gate-issued authority and checks the issued world version against the current signed State Oracle snapshot when revalidation is enabled.
- Missing world version, changed world version, action mutation, policy mutation, tenant mismatch, and direct tool access are rejected in the integration paths.
- HTTP and MCP adapters route protected execution through the enforcement boundary. Deterministic Gate HTTP errors are preserved; unexpected transport/storage failures remain fail-closed.
- Decision replay reproduces the recorded decision/evidence contract. It does not replay arbitrary external world state or external side effects.

## Evidence

The latest complete Action Gate candidate evidence found in the 2026-11-01 snapshot is on PR #244 head SHA `9120f63e3014d98876ab5075c2eb538ca0341abe`, not current main or a customer host:

- [Product Gates #41172304753](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/41172304753): PASS.
- [Production E2E Smoke #41172304650](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/41172304650): PASS.
- [Clean-Room Verification #41172304789](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/41172304789): PASS.
- [Security Authority Gate #41172305010](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/41172305010): PASS.

The Product Gates run exercises real HTTP and MCP integration, production PostgreSQL, 16 concurrent nonce claims with one winner, audit immutability, approval verification, 200-event replay, and replay after Action Gate restart.

## Remaining production hardening and deployment proof

- shared nonce persistence across multiple protected-tool replicas;
- asymmetric signing, external key custody, and independently verified key-rotation procedures;
- external identity federation and customer principal/session lifecycle;
- actual customer-host deployment, TLS/DNS, backup/restore, monitoring, and incident exercises;
- customer-specific policy validation and signed acceptance evidence.

These are not inferred from a green CI run. Each must be separately implemented or verified before the corresponding production claim is made.
