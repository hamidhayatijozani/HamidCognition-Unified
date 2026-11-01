# Action Gate Release Closure Status

Evidence snapshot: 2026-11-01 (UTC)

## Last published release

The last published immutable release recorded in the repository is **Action Gate v1.1.1**:

- tag: `action-gate-v1.1.1`
- source commit: `e9ea7565f4ddea91f5c45104237bd20564c80894`
- artifact: `action-gate-1.1.1.tar`
- artifact SHA-256: `517064de0427286ff4f346d46996642aca3b9def891d1c08bfaebc25546fb791`

## Current main is not that release

Current main is `5acd7fa4a600f99281f9f5396eef5f7df5e14343`, 509 commits ahead of the v1.1.1 tag. PR #243 and PR #244 were merged after the tagged source commit. The latest complete Action Gate Product Gates and Production E2E evidence found in this snapshot is tied to PR #244 head `9120f63e3014d98876ab5075c2eb538ca0341abe`.

No new immutable release artifact or customer deployment for current main is claimed by this file.

## Release claims remain limited to

- runtime authorization and enforcement;
- tenant / actor / session / action binding;
- decision integrity and single-use nonce enforcement;
- fail-closed HTTP/MCP enforcement boundaries;
- PostgreSQL evidence persistence and replay for the tested CI path;
- reproducible evidence for the exact tested source revision.

## Explicit exclusions

This file does not claim regulatory certification, universal AI safety, correctness of every customer policy, downstream business outcome safety, exactly-once external side effects, multi-replica tool nonce coordination, customer-host deployment, customer acceptance, or revenue.

A release may be closed only against one immutable tag, source SHA, artifact checksum, and the required same-SHA validation evidence. Customer deployment and acceptance remain separate gates.
