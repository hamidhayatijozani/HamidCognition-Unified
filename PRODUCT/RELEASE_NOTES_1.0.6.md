# HamidCognition Action Gate v1.0.6

## Release boundary

v1.0.6 is the first commercial release cut from the fully exercised operational product-gate chain after the authority-boundary and CI reproducibility repairs.

This release includes:

- Gate-issued execution authority bound to the exact action hash while preserving the original protected-tool payload;
- consistent packaged imports for authority verification and exception identity;
- HTTP and MCP enforcement integration coverage;
- CI-only authority environment isolation for clean-room, product, and integration tests;
- production PostgreSQL Compose validation;
- production HTTP E2E smoke validation;
- 200-event decision replay and persistence-after-restart acceptance;
- clean-room source verification and release-candidate evidence.

## Commercial boundary

Supported delivery modes are SELF_HOSTED, MANAGED, and ENTERPRISE.

The product does not claim universal AI safety, regulatory certification, downstream correctness, or guaranteed business outcomes. Customer-specific acceptance remains required before production execution is enabled.

## Payment boundary

Commercial settlement for this product is USDT only.

The repository contains no private wallet keys. Payment entitlement must be bound to the invoice, exact product/version, receiving-address fingerprint, transaction hash, settlement status, confirmation evidence, and delivery entitlement.

## Evidence boundary

Commercial validation is tied to the exact source commit and GitHub Actions evidence that produced the release artifact. The mutable main branch is not itself the customer artifact.

