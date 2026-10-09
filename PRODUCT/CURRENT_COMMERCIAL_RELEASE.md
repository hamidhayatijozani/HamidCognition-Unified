# Current Commercial Release Status

## Customer-facing technical baseline

The latest published Action Gate release is **v1.1.1**, GitHub release/tag `action-gate-v1.1.1`.

- Exact release source revision: recorded in `PRODUCT/COMMERCIAL_RELEASE.json` and the published release manifest.
- Release workflow run: `36966012148` — GitHub reports `completed / success`
- Artifact: `action-gate-1.1.1.tar`
- Artifact SHA-256: `517064de0427286ff4f346d46996642aca3b9def891d1c08bfaebc25546fb791`

## Main branch is not the release artifact

At the 2026-10-08 audit, GitHub reported main SHA `a27a8a8f15dada67fba6567fb32ddb3ef37f6563`; `action_gate/VERSION` on main reads `1.1.1`. The main SHA differs from the published release source SHA.

Therefore:
- main's version string matches the release label;
- equivalence of main's code/artifact to the published release is **not established**;
- quote and deliver the immutable published tag/artifact until a new same-SHA release chain validates a newer source.

```text
RELEASE_VERIFIED(immutable-release-source-SHA)
!=
MAIN_VERIFIED(a27a8a8f15dada67fba6567fb32ddb3ef37f6563)
```

## Technical release rule

The recorded v1.1.1 release workflow reports success for its exact source revision and published artifact. This is technical release evidence only. It is not proof of customer acceptance, customer production use, payment, revenue, regulatory certification, or universal security.

## Customer delivery rule

1. Quote the exact product version and immutable tag.
2. Identify the source commit, release asset and checksum.
3. Apply the selected license and deployment scope.
4. Run acceptance against the customer's deployment and customer-selected tool.
5. Record failures, limitations and acceptance evidence.
6. Settle through the explicitly agreed payment route and preserve auditable settlement evidence.
7. Record entitlement only after the applicable commercial conditions are met.

## Product boundary

Action Gate is a pre-execution authorization and evidence boundary for AI-agent tool execution. It does not claim universal AI safety, downstream tool correctness, regulatory certification, or guaranteed business outcomes.

## Delivery modes

- **SELF_HOSTED:** customer operates the deployment.
- **MANAGED:** operator runs the service boundary.
- **ENTERPRISE:** separately scoped integration, security review, support, deployment architecture and SLA.

## Payment boundary

The current operator settlement account is TopChange Wallet ID `USD2134914`. This is an account/wallet identifier, not a blockchain address. No automatic on-chain USDT settlement is claimed. Until a blockchain address and network are explicitly configured, payment verification is provider/manual and must create an auditable settlement record before entitlement.

## Commercial truth

Do not claim sold, customer-validated, revenue-generating, customer-production-proven, or compliant unless the corresponding external evidence exists.
