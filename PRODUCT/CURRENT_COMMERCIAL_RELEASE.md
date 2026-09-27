# Current Commercial Release Status

## Sellable release

The current offerable Action Gate artifact is **v1.0.6**, published as GitHub release action-gate-v1.0.6.

Its immutable commercial release target is:

ee1e121f2af6f6099a77c08cb14854e69e2245b8

Release candidate workflow: #36284400509

The published release includes:
- versioned production container archive;
- SHA-256 checksum;
- release manifest;
- source commit binding;
- release-candidate evidence.

## Release validation

The v1.0.6 source commit passed the same-SHA production validation chain on GitHub Actions, including:
- Action Gate Product Gates;
- Action Gate Product Integrity;
- Action Gate Clean-Room Verification;
- Action Gate Production E2E Smoke;
- Action Gate Security Authority Gate;
- Product Verification;
- Security History Secret Scan;
- Action Gate MVP;
- Master Evidence Gate;
- Action Gate Release Source Evidence;
- Action Gate Release Readiness Gate;
- Action Gate Release Candidate;
- Product Release Publisher.

The production product-gate run exercised unit/product tests, validation-boundary conformance, real HTTP enforcement, real MCP enforcement, sellable readiness checks, package/runtime compilation, production Compose startup, PostgreSQL-backed E2E smoke, and 200-event decision replay/persistence validation.

## Customer delivery rule

1. quote the exact product version;
2. identify the exact release/tag and source commit;
3. provide the release artifact and checksum;
4. apply the selected license and deployment scope;
5. run the customer acceptance procedure against the customer's deployment;
6. settle the invoice in USDT under the payment policy;
7. record the transaction hash and entitlement.

A sale is not marked paid from a screenshot or customer assertion alone. Settlement requires an independently recorded transaction hash and the configured confirmation policy.

## Product boundary

Action Gate is a pre-execution authorization and evidence boundary for AI-agent tool execution. It does not claim universal AI safety, downstream tool correctness, regulatory certification, or guaranteed business outcomes.

## Commercial boundary

Supported delivery modes are SELF_HOSTED, MANAGED and ENTERPRISE.

Repository and CI evidence establish technical release readiness. They do not establish that a customer transaction has occurred, nor do they substitute for customer-specific acceptance, licensing, payment settlement, or deployment configuration.

## Payment boundary

Commercial settlement is USDT only.

The repository must never contain a private wallet key. A real transaction requires the operator's configured receiving address, network policy, invoice, transaction hash, confirmation evidence, and entitlement record.