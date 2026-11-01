# Action Gate Release Checklist

Evidence snapshot: 2026-11-01 (UTC)

## Last published immutable release

- [x] Versioned release tag exists: `action-gate-v1.1.1`.
- [x] Tag target: `e9ea7565f4ddea91f5c45104237bd20564c80894`.
- [x] Release-candidate workflow: `36966012148`.
- [x] Artifact: `action-gate-1.1.1.tar`.
- [x] Artifact SHA-256: `517064de0427286ff4f346d46996642aca3b9def891d1c08bfaebc25546fb791`.

This is the last published artifact found. It is not the current `main` build.

## Current main

- Current main SHA: `5acd7fa4a600f99281f9f5396eef5f7df5e14343`.
- PR #243 is merged: `81543c44dee6d5b72722649568986e49907caec1`.
- PR #244 is merged: `e44552f63f73c7fbf54e0a32bc0981220221b8f7`.
- Current main is 509 commits ahead of the v1.1.1 tag.
- No new immutable release artifact for current main is evidenced.
- Main branch protection is disabled and no repository rulesets were returned by the GitHub API.
- No complete same-SHA Action Gate Product Gates run was found for the current main SHA in this evidence snapshot.

## Latest full Action Gate candidate evidence

The following results are tied to PR #244 head SHA `9120f63e3014d98876ab5075c2eb538ca0341abe`, not current main and not a customer deployment:

- [x] 20/20 check runs succeeded.
- [x] Product Gates: [run #41172304753](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/41172304753).
- [x] Production PostgreSQL E2E and restart persistence: [run #41172304650](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/41172304650).
- [x] Clean-Room Verification: [run #41172304789](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/41172304789).
- [x] Security Authority Gate: [run #41172305010](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/41172305010).
- [x] Canonical Gates: [run #41172304733](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/41172304733).

The Product Gates run includes HTTP/MCP integration, production Compose, PostgreSQL audit immutability and ordering checks, a 16-worker nonce race with one winner, approval-signature verification, 200-event replay, and replay after service restart.

## Current-main evidence and release status

- [x] Evidence Chain Integrity on current main: [run #41244586257](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/41244586257).
- [ ] Full Action Gate Product Gates on the exact current main SHA: not evidenced in this snapshot.
- [ ] New release-readiness proof for current main: not established.
- [ ] Release candidate archive for current main: not produced.
- [ ] New release publication for current main: not performed.
- [ ] Production endpoint probe: UNKNOWN; `PRODUCTION_BASE_URL` is not configured, as recorded by [run #41267310701](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/41267310701).
- [ ] Customer-host acceptance: not evidenced.
- [ ] Written pilot licence and customer agreement: not evidenced.
- [ ] Customer acceptance, payment, and revenue: not evidenced.

The current-main release workflow runs #41204043688, #41204057084, and #41204067836 ended with success conclusions but skipped validated-SHA publication, candidate build, and release publication. They are successful no-ops, not a new release.

## Deployment constraints

- [ ] Keep one protected-tool instance for the limited pilot. Its nonce registry is SQLite at `/data/tool_authority.db` on the persistent `tool_data` volume; multi-replica nonce coordination is not established.
- [ ] Back up PostgreSQL and the separate `tool_data` volume.
- [ ] Configure the actual customer host, DNS/TLS, and production endpoint before probing.
- [ ] Run the full acceptance matrix against the exact deployed tag, source SHA, image digest, and policy fingerprint.

## Legal and commercial

- [ ] Obtain a written pilot licence/permission. The repository is proprietary; public visibility is not a commercial licence.
- [ ] Agree one-tool scope, data handling, rollback, responsibilities, and acceptance criteria in writing.
- [ ] Treat 2,500 USDT / 30 days as a proposed price only.
- [ ] Record payment settlement and customer acceptance only when external evidence exists.

## Release rule

Do not mark current main as released, production deployed, customer accepted, or revenue-generating until the exact-source release chain, customer-host checks, written licence, acceptance evidence, and commercial records exist.
