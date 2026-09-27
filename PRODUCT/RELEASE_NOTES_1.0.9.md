# HamidCognition Action Gate v1.0.9

## Release basis

- Version: **1.0.9**
- Release purpose: make the customer acceptance smoke test part of the production Action Gate image and correct the deployment procedure so the smoke test runs through the internal Gate API rather than an unpublished edge port.
- Enforcement basis: execution authority is independently bound to the action digest and policy digest at the protected tool boundary.
- Fail-closed behavior: forged authority, missing authority, mismatched action binding, mismatched policy binding, and unsupported MCP methods are rejected by the enforcement path.
- Evidence boundary: execution reservation and execution finalization remain part of the enforced evidence chain.

## Validation

The release candidate must pass the same-SHA product, security, Clean-Room, production E2E, release-readiness, and release-publication gates.

## Commercial boundary

This is an engineering product release. Customer deployment, acceptance, integrations, licensing, payment, and commercial claims remain subject to the documented customer acceptance and deployment procedures.
