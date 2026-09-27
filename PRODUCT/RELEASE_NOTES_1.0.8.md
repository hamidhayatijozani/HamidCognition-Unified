# HamidCognition Action Gate v1.0.8

## Release basis

- Version: **1.0.8**
- Release purpose: align the customer-facing product documentation and acceptance boundary with the validated Action Gate enforcement state.
- Enforcement basis: execution authority is independently bound to the action digest and policy digest at the protected tool boundary.
- Fail-closed behavior: forged authority, missing authority, mismatched action binding, mismatched policy binding, and unsupported MCP methods are rejected by the enforcement path.
- Evidence boundary: execution reservation and execution finalization remain part of the enforced evidence chain.

## Documentation alignment

This release makes the current product documentation agree on:
- the canonical product version;
- the customer acceptance procedure;
- the protected-tool policy-binding requirement;
- the delivery manifest and commercial-release boundary.

## Validation

The release candidate must pass the same-SHA product, security, Clean-Room, production E2E, release-readiness, and release-publication gates.

## Commercial boundary

This is an engineering product release. Customer deployment, acceptance, integrations, licensing, payment, and commercial claims remain subject to the documented customer acceptance and deployment procedures.
