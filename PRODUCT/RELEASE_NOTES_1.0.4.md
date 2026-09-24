# HamidCognition Action Gate v1.0.4

## Final hardened baseline

v1.0.4 is the final release candidate baseline after the security and release-pipeline hardening completed in this cycle.

## Security

- Persistent execution-authority nonce state is stored in SQLite and mounted on a persistent production volume.
- The tool boundary executes only Gate-issued ALLOW authority and rejects SANDBOX execution.
- Release write privileges are isolated from evidence/build workflows.
- Reachable Git history receives a high-confidence secret regression scan.
- The history scanner avoids pipe deadlock and skips oversized blobs before content scanning.
- The production tool image initializes the persistent nonce volume with the correct runtime ownership.

## Release integrity

- Product release generation is downstream of an aggregate same-SHA Release Readiness Gate.
- Release Readiness requires successful Product Gates, Product Integrity, Clean-Room Verification, Production E2E Smoke, Security Authority Gate, Product Verification, Master Evidence Gate, Security History Secret Scan, and Action Gate MVP.
- The release candidate checks out the exact validated workflow SHA.
- The publisher creates the release only from the exact release-candidate artifact.

## Validation boundary

The validation establishes the tested decision, enforcement, tool, evidence, persistence, replay, clean-room, security, and production E2E properties exercised by the repository. It does not establish universal AI safety, regulatory certification, customer policy correctness, downstream correctness, or business outcomes.

## Distribution

The repository is private. Production secrets remain outside source control. Commercial delivery remains subject to the separate written license and customer acceptance procedure.
