# Current Commercial Release Status

Evidence snapshot: 2026-11-01 (UTC)

## Last published immutable customer-facing release

The latest independently validated and published Action Gate release is **v1.1.1**:

- release tag: `action-gate-v1.1.1`
- tagged source commit: `e9ea7565f4ddea91f5c45104237bd20564c80894`
- artifact: `action-gate-1.1.1.tar`
- artifact SHA-256: `517064de0427286ff4f346d46996642aca3b9def891d1c08bfaebc25546fb791`

This immutable tag and artifact identify the published v1.1.1 build.

## Current development source is not the published artifact

At this evidence snapshot:

- current main HEAD: `679d584913ae16a7e7e7257abe012b75ac9b2bea`;
- `action_gate/VERSION` on main still reads `1.1.1`;
- the latest complete Action Gate Product Gates run is #41274729257 on source SHA `eceb6e3d46e5fe9c34ce8e690fec107850345657`;
- the two commits after that validated source changed only three `data/awareness/*.json` files, not Action Gate runtime or product-contract files.

This supports the tested runtime code path, but it does not make current main identical to the published v1.1.1 tag or artifact. The release workflow did not build or publish a candidate for current main: Release Candidate #41274855051 and Product Release Publisher #41274861554 completed with their build/publication steps skipped and no artifacts.

**Commercial rule:** offer the immutable v1.1.1 tag and its matching artifact only. Do not package or describe current main as the published v1.1.1 artifact. A new development source becomes a distributable release only after a new version/tag, exact-source validation, artifact checksum, and published release record all match.

## Verified v1.1.1 release rule

The published v1.1.1 release is offerable as a published software artifact because its release record contains an exact tag, source commit, archive, and SHA-256 digest.

For a new release, require:

1. product and security gates on the exact source SHA;
2. Clean-Room and production E2E validation on that SHA;
3. release-readiness validation against the exact version tag and SHA;
4. reproducible production artifact and checksum;
5. published release record bound to that same source revision.

## Customer delivery rule

1. quote the exact product version;
2. identify the exact immutable release tag and source commit;
3. provide the matching release artifact and checksum;
4. apply the selected license and deployment scope;
5. deploy and run customer acceptance against the customer's environment;
6. settle the invoice through the agreed commercial payment route;
7. record settlement evidence and entitlement.

## Product boundary

Action Gate is a pre-execution authorization and evidence boundary for AI-agent tool execution. It does not claim universal AI safety, downstream tool correctness, regulatory certification, or guaranteed business outcomes.

Supported delivery modes are SELF_HOSTED, MANAGED and ENTERPRISE. The limited pilot topology and protected-tool nonce-store constraints are documented in `docs/ACTION_GATE_PILOT_OPERATIONS_RUNBOOK.md`.

## Payment boundary

The operator's TopChange account identifier is configured out of band and is not published in repository source. It is not a blockchain address. The repository therefore does not claim automatic on-chain USDT settlement.

Until an on-chain address and network are actually configured, payment verification is provider/manual and must produce an auditable settlement record before entitlement.

## Commercial truth rule

Do not call the product sold, customer validated, revenue-generating, production proven with customers, or compliant unless the corresponding external evidence exists.
