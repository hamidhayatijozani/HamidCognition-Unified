# HamidCognition Action Gate v1.0.2

## Release status

v1.0.2 is an execution-boundary hardening release produced from a reverse audit of the v1.0.1 product path.

## Included

- Gate-issued execution authority is now created only after atomic execution reservation.
- Authority is bound to decision ID, tenant, action digest, policy digest, nonce, decision and expiry.
- The downstream tool verifies the Gate-issued authority before accepting a call.
- The OANDA broker adapter now verifies the same Gate-issued authority at the external trading side-effect boundary.
- The legacy enforcement-only attestation path is removed from production execution.
- Production Compose explicitly separates the public edge network from the internal backend network.
- Runtime and tool images include the authority verification code they actually execute.
- Direct-tool bypass and tampered-authority negative tests are part of the acceptance boundary.
- Customer acceptance and threat-model documentation now match the executable boundary.

## Boundary

This release strengthens the tested execution boundary. It does not establish universal agent safety, customer policy correctness, downstream business outcome safety, regulatory certification, or infrastructure security outside the documented deployment boundary.

## Verification

Promotion requires the full Product Gates, Product Integrity, Security Authority, Clean-Room and MVP workflows to pass on the same source revision. No percentage-based aggregate is used as a release substitute.
