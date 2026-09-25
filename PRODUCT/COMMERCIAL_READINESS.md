# Action Gate Commercial Readiness

## Release baseline

**HamidCognition Action Gate v1.0.4** is the current engineering and commercial-delivery baseline.

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

The v1.0.4 release was validated on the exact release commit by Product Gates, Product Integrity, Production E2E, Product Verification, Security Authority Gate, Master Evidence Gate, Security History Secret Scan, Action Gate MVP, Clean-Room Verification, Release Readiness Gate, and Release Candidate workflows. The final publisher attached the versioned tar, checksum, and manifest to the product release.

## Not included by default

- customer-specific legal compliance certification;
- universal safety guarantees;
- downstream tool correctness;
- customer-specific policy design;
- 24/7 support;
- guaranteed business outcomes.

Those require explicit scope and evidence.
