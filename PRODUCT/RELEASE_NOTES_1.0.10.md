# HamidCognition Action Gate v1.0.10

## Release basis

- Version: **1.0.10**
- Release purpose: correct the production container build so the customer acceptance smoke test is packaged into the Action Gate image from the repository-root build context.
- Container build correction: production Compose now builds from the repository root and explicitly targets `action_gate/Dockerfile`.
- Image contents: `PRODUCT/customer_acceptance_smoke.py` is copied into the production image so the documented in-container acceptance command is executable.
- Dockerfile correction: the configurable Python base-image reference uses valid shell expansion syntax.
- Deployment documentation: the production acceptance path is aligned with the internal Action Gate API exposed inside the Compose network; no unpublished host port is required.
- Security boundary: these changes are packaging and deployment corrections. They do not weaken the execution-authority, policy-binding, fail-closed, or evidence-enforcement semantics.

## Validation

The release candidate must pass the same-SHA product, security, Clean-Room, production E2E, release-readiness, and release-publication gates.

## Commercial boundary

This is an engineering product release. Customer deployment, acceptance, integrations, licensing, payment, and commercial claims remain subject to the documented customer acceptance and deployment procedures.
