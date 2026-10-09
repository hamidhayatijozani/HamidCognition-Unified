# Action Gate Commercial Readiness

## Canonical product

The latest published technical release is **HamidCognition Action Gate v1.1.1**. It is the current customer-facing release baseline, not proof of customer acceptance. A customer quote must identify the immutable release tag, source revision, artifact and checksum. The mutable main branch has a different SHA from the published release source; equivalence is not established.

## Included

- Action Gate runtime
- HTTP enforcement integration
- authenticated MCP enforcement integration
- decision evidence and replay
- tenant / actor / session binding
- production authentication
- fail-closed execution boundary
- persistent PostgreSQL storage
- persistent execution-authority nonce state
- production Compose deployment
- validation evidence
- Clean-Room verification
- versioned release artifact and checksum

## Current published release

- Product: HamidCognition Action Gate
- Version: 1.1.1
- Release tag: `action-gate-v1.1.1`
- Source commit: `e9ea7565f4ddea91f5c45104237bd20564c80894`
- Release-candidate workflow run: `36966012148`
- Artifact: `action-gate-1.1.1.tar`
- Artifact digest: `sha256:517064de0427286ff4f346d46996642aca3b9def891d1c08bfaebc25546fb791`

## Customer delivery package

1. versioned runtime artifact or container image;
2. deployment configuration template;
3. policy configuration template;
4. integration/API contract;
5. security boundary;
6. operations runbook;
7. customer acceptance matrix and procedure;
8. versioned release notes;
9. provenance and license terms;
10. delivery manifest.

## Commercial modes

**SELF_HOSTED** means the customer operates the runtime.

**MANAGED** means HamidCognition operates the service boundary.

**ENTERPRISE** means self-hosted or managed deployment plus negotiated integration, security review, support and SLA terms.

The repository does not represent Managed or Enterprise operations as already delivered to a paying customer.

## Pilot entry point

The current standard offer is **USD $2,500 fixed / 30 days** for one customer-selected high-impact HTTP/MCP tool, one controlled test environment, agreed acceptance cases, deployment assistance and a reproducible evidence package. Expanded scope requires a separate written quote. The pilot measures the actual execution boundary; it is not a universal security guarantee.

Acceptance is based on executable behavior:

- unauthorized direct downstream access is rejected;
- authority is bound to intended tenant, actor, session, action and policy;
- expired authority is rejected;
- replay is rejected;
- tampering is rejected;
- persistence survives restart;
- evidence can be reproduced from the customer's deployment.

## Live-sale dependency

Technical release readiness is not revenue.

A completed sale requires:

1. named buyer and technical owner;
2. written scope and acceptance criteria;
3. price and license/usage terms;
4. invoice or payment request;
5. verified payment settlement;
6. customer acceptance evidence;
7. entitlement/delivery record.

### Current settlement route

The operator's only supplied settlement account is:

- Provider: TopChange
- Wallet: کیف پول دلار
- Wallet ID: `USD2134914`

This is not a blockchain address. Until a real on-chain address and network are supplied, the sale flow must use provider/manual settlement verification rather than pretending that blockchain transaction-hash verification exists.

## Commercial truth rule

Do not call the product sold, customer validated, revenue-generating, production proven with customers, or compliant unless the corresponding external evidence exists.

## Launch assets

- `SALES/ONE_PAGER.md`
- `SALES/PILOT_OFFER.md`
- `SALES/DEMO_SCRIPT.md`
- `SALES/ICP_AND_POSITIONING.md`
- `SALES/OUTBOUND_EMAILS.md`
- `SALES/OBJECTIONS.md`
- `SALES/PRICING_AND_SCOPE.md`
- `SALES/COMMERCIAL_LAUNCH_PLAN.md`
