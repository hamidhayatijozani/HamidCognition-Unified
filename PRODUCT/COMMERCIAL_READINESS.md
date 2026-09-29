# Action Gate Commercial Readiness

## Canonical product

**HamidCognition Action Gate v1.0.10** is the current customer-facing validated product boundary.

A customer quote must identify the exact release tag, source commit, artifact and checksum being offered.

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
- Version: 1.0.10
- Release tag: `action-gate-v1.0.10`
- Source commit: `77d820e99dc78a6a9e3217d3c1c49d5cdf07813f`
- Release-candidate workflow run: `36303350191`
- Artifact: `action-gate-1.0.10.tar`
- Artifact digest: `sha256:10bb53b69b56ff86146f5c71e3e5d7e34dacb4e12dba2adafc59f9d5276abd91`

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

The first commercial transaction is a narrow one-tool pilot. The pilot protects one customer-selected high-impact HTTP or MCP tool and measures the actual execution boundary.

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
