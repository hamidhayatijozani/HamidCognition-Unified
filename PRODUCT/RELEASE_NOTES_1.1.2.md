# HamidCognition Action Gate v1.1.2

Status: release-candidate preparation. This document is not proof that v1.1.2 has been tagged, packaged, or published.

## Validated product boundary

The release candidate is intended to package the Action Gate runtime after same-source validation of these behaviors:

- HTTP and authenticated MCP requests pass through the governed execution boundary; ALLOW, DENY, and evidence retrieval are exercised end to end.
- Execution authority is bound to tenant, actor, session, action, policy, expiry, and single-use nonce.
- PostgreSQL is used for Action Gate decision and evidence persistence. The production E2E path restarts Action Gate and retrieves the same execution evidence afterward.
- PostgreSQL audit events are append-only, with database-level protections against UPDATE and DELETE.
- The production validation path replays 200 persisted decisions after service restart.
- Clean-room verification compiles the runtime, runs repository tests, builds the production container from an immutable base image, and emits a source-bound verification manifest.

The exact source SHA and workflow-run IDs for the v1.1.2 release must be recorded by the release-readiness and release-candidate workflows after the versioned tag is created.

## Deployment constraints

- The protected tool keeps a separate SQLite nonce registry at `/data/tool_authority.db` on the persistent `tool_data` volume.
- The restricted pilot topology is one protected-tool instance. Preserve and back up both PostgreSQL and the `tool_data` volume.
- Multi-replica or multi-host nonce consistency, high availability, and exactly-once external side effects are not established.
- A customer-controlled host, public TLS/DNS endpoint, backup restoration, and customer acceptance must be verified separately.

## Security and commercial limits

This release does not claim universal AI safety, correctness of every customer policy, regulatory certification, legal compliance, customer acceptance, revenue, or guaranteed business outcomes.

The proposed limited pilot remains one customer-selected HTTP or MCP tool in one controlled test environment, with non-sensitive and reversible actions. Written pilot permission, data handling, rollback responsibilities, and acceptance criteria must be agreed before customer delivery.

## Publication rule

Do not describe v1.1.2 as published or distribute it as a release until all of the following identify the same source:

1. `action_gate/VERSION` = `1.1.2`;
2. immutable tag `action-gate-v1.1.2`;
3. successful same-SHA release-readiness validation;
4. release-candidate archive, manifest, and SHA-256 checksum;
5. published GitHub Release containing those verified artifacts.

The last published commercial release remains v1.1.1 until that publication sequence completes.
