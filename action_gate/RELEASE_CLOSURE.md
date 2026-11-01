# Action Gate Release Closure Status

Evidence snapshot: 2026-11-01 (UTC)

## Last published immutable release

The last published immutable Action Gate release is **v1.1.1**:

- tag: `action-gate-v1.1.1`
- tagged source commit: `e9ea7565f4ddea91f5c45104237bd20564c80894`
- artifact: `action-gate-1.1.1.tar`
- artifact SHA-256: `517064de0427286ff4f346d46996642aca3b9def891d1c08bfaebc25546fb791`

This is the only release artifact in this snapshot that may be offered as the published v1.1.1 build.

## Current main and validation identity

Current main HEAD at this snapshot:

`679d584913ae16a7e7e7257abe012b75ac9b2bea`

The latest complete Action Gate Product Gates run is **#41274729257**, on source SHA:

`eceb6e3d46e5fe9c34ce8e690fec107850345657`

The following checks also completed successfully on that same source SHA:

- Product Gates #41274729257: real HTTP and MCP enforcement, production Compose, PostgreSQL checks, audit immutability, 200-event replay, restart and persistence replay, evidence-pack generation.
- Production E2E #41274729288: production stack startup, State Oracle initialization, E2E smoke, and PostgreSQL evidence retrieval after Action Gate restart.
- Security Authority Gate #41274729282.
- Clean-Room Verification #41274729263.
- Canonical gates-local #41274729293.
- Product Verification #41274729286.

The validated source SHA is an ancestor of current main. The GitHub compare between that SHA and current main reports two later commits changing only these awareness data files:

- `data/awareness/experiment-history.json`
- `data/awareness/innovation-report.json`
- `data/awareness/self-observation.json`

No Action Gate runtime, deployment, or product-contract file changed after the validated source SHA in that comparison. However, the Product Gates run is not a same-SHA run on current main HEAD; retain the exact distinction.

## Release status for current main

The canonical `action_gate/VERSION` file still reads `1.1.1`, but the current main source is not the source commit behind the published `action-gate-v1.1.1` tag.

The release workflow requires the version tag to point to the exact validated source SHA. For the current development source, the release path did not produce a candidate:

- Release Readiness Gate #41274843577 completed, but the validated-source publication step was skipped.
- Release Candidate #41274855051 completed, but checkout/build/archive/checksum/manifest/upload steps were skipped.
- Product Release Publisher #41274861554 completed, but candidate verification and publication steps were skipped.
- Those three runs have no release artifacts.

Therefore:

- **Published release:** v1.1.1 at the immutable tag and source commit above.
- **Current development source:** main HEAD `679d584913ae16a7e7e7257abe012b75ac9b2bea`.
- **Current-main release artifact:** NOT BUILT.
- Do not distribute current main under the published v1.1.1 artifact identity. A new release requires a new version, exact source tag, same-SHA validation, artifact, checksum, and published release record.

## Verified security and persistence boundary

The current tested application path has CI evidence for:

- fail-closed HTTP and authenticated MCP enforcement;
- execution-authority binding and one-time nonce enforcement;
- production PostgreSQL decision/evidence persistence;
- append-only audit protections;
- 200-event replay and replay after Action Gate service restart.

The production Compose topology has an important limit: the protected tool keeps a separate SQLite nonce registry at `/data/tool_authority.db` on the persistent `tool_data:/data` volume. The limited pilot must use one protected-tool instance, retain and back up that volume, and must not claim multi-replica or multi-host nonce consistency. Action Gate PostgreSQL persistence does not remove this separate protected-tool storage constraint.

## Explicit exclusions

This evidence does not establish:

- deployment on a customer-controlled host;
- customer TLS/DNS, public endpoint, backup restoration, or incident exercise;
- acceptance by a customer, signed contract, settled payment, or revenue;
- multi-replica protected-tool nonce consistency;
- regulatory certification, universal AI safety, exactly-once external side effects, or correctness of every customer policy.

## Pilot release decision

The repository has a tested production-like CI path and a documented restricted-pilot topology. A customer pilot remains **BLOCKED** until the exact offered immutable build is deployed in the agreed customer test environment and the customer acceptance procedure passes with retained raw evidence and buyer sign-off.

A green GitHub run is engineering evidence, not customer deployment or acceptance.
