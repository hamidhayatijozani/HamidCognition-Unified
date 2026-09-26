# HamidCognition Action Gate v1.0.5

## Enforcement release

v1.0.5 extends the hardened Action Gate baseline with structured active-defense security signals at the protected execution boundary.

## Security and enforcement

- High-signal enforcement failures can be classified as structured security telemetry.
- Signals include invalid signatures, malformed authorities, nonce reuse, tenant-binding failures, action-binding failures, and policy-binding failures.
- Security signals retain decision, tenant, nonce fingerprint, severity, reason, and observation time without exposing authority secrets.
- Active-defense telemetry does not claim attacker attribution, automatic quarantine, or IP blacklisting.
- The protected execution boundary continues to enforce Gate-issued authority, tenant/action/policy binding, nonce single-use, and fail-closed behavior.

## Validation boundary

The release is validated only for the controls exercised by the repository's automated tests and acceptance procedures. It does not establish universal AI safety, regulatory certification, customer policy correctness, downstream correctness, or business outcomes.

## Commercial delivery

The commercial entry point remains a narrowly scoped pilot around one high-impact agent tool or MCP action. Customer acceptance evidence must be generated against the customer's actual deployment before production recommendation.

Production secrets remain outside source control. Commercial delivery remains subject to the written license, deployment model, and customer acceptance procedure.
