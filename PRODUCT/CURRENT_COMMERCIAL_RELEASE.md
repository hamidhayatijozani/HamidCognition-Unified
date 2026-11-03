# Current Commercial Release Status

Evidence snapshot: 2026-11-03 (UTC)

## Last published immutable customer-facing release

The latest published Action Gate release remains **v1.1.1**.

- Release tag: `action-gate-v1.1.1`
- Source commit: `e9ea7565f4ddea91f5c45104237bd20564c80894`
- GitHub Release: https://github.com/hamidhayatijozani/HamidCognition-Unified/releases/tag/action-gate-v1.1.1
- Artifact: `action-gate-1.1.1.tar`
- Artifact SHA-256: `517064de0427286ff4f346d46996642aca3b9def891d1c08bfaebc25546fb791`

The GitHub Release currently exposes the archive, checksum file, and manifest. This tag and artifact identify the published v1.1.1 build; they must not be silently replaced with mutable `main`.

## Current development source

As of this snapshot:

- Current `main` HEAD: `fe2ff4d1d3b2f9aafd9b30330ac282f284898a2f`.
- `action_gate/VERSION` on `main`: `1.1.2` (development candidate).
- The last complete Action Gate Product Gates run: [#41585249819](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/41585249819), on source SHA `47391ddf001b771c5a51abe8c30390ec4c6b3a14`.
- The corresponding Clean-Room run: [#41585249696](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/41585249696).
- The corresponding Production E2E run: [#41585249793](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/41585249793).
- The corresponding Security Authority run: [#41585249799](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/41585249799).
- GitHub compare from that validated source SHA to current `main` shows two later commits changing only three `data/awareness/*.json` files. No Action Gate runtime or product-contract files changed in those two commits.

This is evidence that the current runtime/product-contract files have not changed since the cited CI source SHA. It is **not** a same-SHA CI claim for current `main`.

## v1.1.2 publication status

The latest Action Gate Release Readiness Gate run, [#41585442134](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/41585442134), completed successfully on current `main`. This was a main/workflow-run readiness event, not the exact immutable release-tag push required to build and publish a candidate.

- Action Gate Release Candidate [#41585477670](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/41585477670): **skipped**; no candidate artifact was produced.
- Product Release Publisher [#41585483409](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/41585483409): **skipped**; no v1.1.2 GitHub Release was published.
- The historical `PRODUCT/COMMERCIAL_RELEASE.json` remains bound to v1.1.1 by design. Do not rewrite that immutable published-release record to describe an unpublished candidate.

**Commercial rule:** v1.1.1 is the only currently published delivery artifact. v1.1.2 is not yet tagged, packaged, or published. Do not quote or deliver `main` as a released v1.1.2 artifact.

A new distributable release requires all of the following to refer to the same source revision: canonical version, immutable tag, successful exact-SHA product/security/Clean-Room/production-E2E checks, release-readiness evidence, archive checksum, and published GitHub Release.

## Pilot scope and commercial conditions

The current proposed limited pilot is **2,500 USDT for 30 days**, covering one customer-selected protected HTTP or MCP tool in one controlled test environment. This is a proposal, not a market-validated price, signed quote, contract, received payment, or customer acceptance.

The production runbook currently requires one protected-tool instance because its nonce registry is stored separately in a persistent SQLite volume. Do not claim multi-replica or high-availability nonce consistency. Retain and back up the tool volume together with PostgreSQL, and test restoration before customer traffic.

The repository is publicly visible but carries a proprietary no-grant license notice. Public visibility does not grant customer-use or redistribution rights. Obtain separate written license/permission covering the exact pilot scope before delivery.

## Branch governance

The GitHub branch endpoint reports `main` as `protected=false`, and the repository rulesets endpoint currently returns an empty list. Treat this as a governance gap: required status checks and a protected merge path have not been evidenced. Do not treat green CI alone as branch protection.

## Customer delivery and acceptance

1. Quote the exact published version, tag, source commit, and artifact digest.
2. Obtain written license/permission and agree the pilot scope, data handling, operator, rollback, and payment terms.
3. Deploy the exact artifact to the customer's controlled environment.
4. Run `PRODUCT/CUSTOMER_ACCEPTANCE.md` and `docs/ACTION_GATE_PILOT_OPERATIONS_RUNBOOK.md` against that environment.
5. Record raw redacted evidence, image digests, policy fingerprint, operator, timestamp, rollback target, and customer sign-off.
6. Record settlement evidence and entitlement before describing the pilot as paid.

CI validates the checked-in automation path. It does not prove public deployment, customer-hosted TLS/DNS, customer acceptance, payment, or revenue.

## Product boundary

Action Gate is a pre-execution authorization and evidence boundary for AI-agent tool execution. It does not claim universal AI safety, downstream tool correctness, regulatory certification, or guaranteed business outcomes.

Supported delivery modes are SELF_HOSTED, MANAGED, and ENTERPRISE, subject to a separately agreed license and delivery scope.

## Payment boundary

The operator's TopChange account identifier is configured out of band and is not published in repository source. It is not a blockchain address. Do not claim automatic on-chain USDT settlement. Until a valid on-chain address and network are configured, payment verification is provider/manual and must produce an auditable settlement record before entitlement.

## Commercial truth rule

Do not call the product sold, customer-validated, revenue-generating, accepted in customer production, or compliant unless the corresponding external evidence exists.
