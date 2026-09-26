# Action Gate Commercial Readiness

## Release baseline

**HamidCognition Action Gate v1.0.5** is the current published engineering and commercial-delivery baseline.

## Included

- Action Gate runtime
- HTTP enforcement integration
- MCP enforcement integration
- decision evidence and replay
- actor/session binding
- production authentication
- fail-closed execution boundary
- persistent PostgreSQL storage
- persistent execution-authority nonce state
- production Compose deployment
- validation evidence and clean-room verification
- versioned release artifact

## Customer delivery package

1. versioned runtime artifact or container image;
2. deployment configuration template;
3. policy configuration template;
4. integration/API contract;
5. security boundary;
6. operations runbook;
7. customer acceptance procedure;
8. versioned release notes;
9. provenance and license terms;
10. delivery manifest.

## Commercial modes

SELF_HOSTED means the customer operates the runtime.
MANAGED means HamidCognition operates the service boundary.
ENTERPRISE means self-hosted or managed deployment plus negotiated support, security review, integration, and SLA terms.

The repository does not assert prices. Pricing is a business decision and must be governed by a separate commercial schedule.

## Acceptance evidence

Historical v1.0.5 evidence may be referenced as historical provenance only. It does not automatically validate the current main branch.

A current commercial release must record the exact source commit, successful same-SHA release-readiness run, release-candidate artifact digest and published release record.

## Not included by default

- customer-specific legal compliance certification;
- universal safety guarantees;
- downstream tool correctness;
- customer-specific policy design;
- 24/7 support;
- guaranteed business outcomes.

Those require explicit scope and evidence.

## Live-sale dependency

The product package is prepared for commercial delivery. A live checkout requires a connected payment provider and an activated product/price/payment link. No payment credential or live checkout endpoint is stored in this repository.
