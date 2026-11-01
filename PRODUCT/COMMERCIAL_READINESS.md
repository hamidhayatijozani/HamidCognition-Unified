# Action Gate Commercial Readiness

Evidence snapshot: 2026-11-01 (UTC)

## Last published immutable release

The last published release artifact recorded by the repository is **HamidCognition Action Gate v1.1.1**:

- Release tag: `action-gate-v1.1.1`
- Tagged source commit: `e9ea7565f4ddea91f5c45104237bd20564c80894`
- Release-candidate workflow run: `36966012148`
- Artifact: `action-gate-1.1.1.tar`
- Artifact digest: `sha256:517064de0427286ff4f346d46996642aca3b9def891d1c08bfaebc25546fb791`

The tag still resolves to the recorded source commit. Current `main` is `5acd7fa4a600f99281f9f5396eef5f7df5e14343`, 509 commits ahead of that tag. PR #243 and PR #244 were merged after the v1.1.1 source commit. Therefore, the v1.1.1 archive must not be represented as containing those later changes, and current `main` must not be represented as a newly published release.

## Current source and validation evidence

Current `main`:

- SHA: `5acd7fa4a600f99281f9f5396eef5f7df5e14343`
- PR #243 merged as `81543c44dee6d5b72722649568986e49907caec1`: deterministic Gate conflict status/body preserved across HTTP and MCP enforcement.
- PR #244 merged as `e44552f63f73c7fbf54e0a32bc0981220221b8f7`: production approval-signing secret injected into the Action Gate verifier.

The latest complete Action Gate validation evidence located for these changes is on PR #244 head SHA `9120f63e3014d98876ab5075c2eb538ca0341abe`, not on current `main` and not on a customer host:

- 20/20 GitHub check runs succeeded.
- [Action Gate Product Gates run #41172304753](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/41172304753) passed. Its steps include real HTTP enforcement, real MCP enforcement, production Compose, PostgreSQL checks, concurrent nonce contention, approval verification, 200-event replay, and replay after service restart.
- [Production E2E Smoke run #41172304650](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/41172304650) passed, including PostgreSQL evidence retrieval after an Action Gate restart.
- [Clean-Room Verification run #41172304789](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/41172304789) passed.
- [Security Authority Gate run #41172305010](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/41172305010) passed.

On current `main`, [Evidence Chain Integrity run #41244586257](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/41244586257) passed and created a Sigstore witness for that source SHA. This is evidence-chain verification, not a substitute for the full Action Gate Product Gates suite.

The current-main release chain did not publish a new artifact. The readiness, candidate, and publisher jobs at runs #41204043688, #41204057084, and #41204067836 completed as successful no-ops: validated-SHA publication, candidate checkout/build, and release verification/publication were skipped. No new release is claimed.

## Runtime and deployment boundary

[Production Runtime Supervisor run #41267310701](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/41267310701) checked current `main`, but its log states that `PRODUCTION_BASE_URL` is not configured and the runtime probe was skipped. The recorded production status is **UNKNOWN**, not healthy or deployed.

The repository's production Compose configuration uses a separate SQLite nonce registry for the protected tool, stored at `/data/tool_authority.db` on the persistent `tool_data` volume. For the current implementation:

- keep the protected tool at one instance for the limited pilot;
- preserve and back up `tool_data` as well as PostgreSQL;
- do not horizontally scale the tool or claim multi-replica nonce consistency;
- if the nonce volume is lost or restored from a stale backup, keep execution disabled until outstanding authorities are invalidated and the nonce state is safely re-established.

A customer host, DNS/TLS endpoint, externally reachable deployment, and customer-host acceptance run have not been evidenced.

## Security boundary

The tested product boundary covers the exact execution paths and cases represented by the cited CI runs. It does not establish universal AI safety, correctness of customer policies, downstream business correctness, regulatory certification, HSM/KMS custody, multi-replica nonce coordination, or replay of external world state and side effects.

## Commercial and legal boundary

The proposed first pilot remains **2,500 USDT fixed for 30 days**, limited to one customer-selected HTTP or MCP tool in one controlled test environment. This is a proposal, not a market-validated price or an existing transaction.

The repository's `LICENSE` states that the repository is proprietary and grants no commercial licence by public visibility alone. A separate written pilot licence/permission and agreed scope must be in place before customer delivery. The IP evidence register is explicitly a partial draft, not a legal opinion or proof of exclusive ownership.

No customer acceptance, signed pilot contract, payment settlement, or revenue evidence is recorded here.

## Go / No-Go

**NO-GO for production customer execution today.** The current-main product validation, release artifact, production endpoint, and customer acceptance are not all established on one immutable source/deployment identity.

**Eligible next step:** a restricted technical evaluation using one tool, one tool instance, synthetic or reversible actions, a controlled customer environment, a written licence/scope, and the full acceptance matrix. Production actions remain disabled until the customer-host checks pass.

## Required delivery package

1. exact immutable release tag, source SHA, artifact and checksum;
2. secret-free deployment and policy templates;
3. integration/API contract;
4. security boundary and known limitations;
5. operations and rollback runbook, including the single-instance nonce-store constraint;
6. customer acceptance matrix and raw evidence bundle;
7. written licence and pilot agreement;
8. delivery and entitlement record.
