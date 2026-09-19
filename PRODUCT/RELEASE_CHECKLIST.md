# Action Gate Release Checklist

## Engineering

- [x] Canonical version updated.
- [x] Runtime tests pass.
- [x] Validation Boundary tests pass.
- [x] HTTP enforcement passes.
- [x] MCP enforcement passes.
- [x] Production container builds and starts in CI.
- [x] PostgreSQL persistence passes.
- [x] Replay/persistence checks pass.
- [x] Evidence artifact retained for the exact release baseline.
- [x] Artifact SHA256 recorded for the exact release baseline.

## Security

- [x] No production secrets are committed in the product environment template.
- [ ] Signing material externally managed. This remains an operational deployment requirement.
- [x] Actor/session/tenant binding covered by the Action Gate validation boundary.
- [x] Nonce single-use covered by the validation boundary.
- [x] Evidence failure is fail-closed.
- [x] SANDBOX cannot cross the production execution boundary.
- [x] Direct downstream bypass path is explicitly constrained by the enforcement contract.

## Customer delivery

- [x] Deployment contract delivered.
- [x] Integration contract delivered.
- [x] Environment template delivered.
- [x] Operations runbook delivered.
- [x] Customer acceptance procedure delivered.
- [x] Release notes and provenance evidence identify the exact release baseline.

## Evidence rule

A checkbox is marked only when the corresponding behavior has executable or directly verifiable evidence. Documentation alone is not treated as behavioral proof.

## Release baseline

- Product: HamidCognition Action Gate
- Version: 1.0.0
- Baseline SHA: 8c7cf032f16a32382093d14f0e106d7b28af054d
- Clean-Room run: 35439993682
- Clean-Room artifact: 10583504006
- Clean-Room artifact digest: sha256:2d836a05b5a7c2551a14b08ce4c262f9622b097055c0066cc0cb58a8646ae12f
- Product Integrity run: 35439993568
- Production E2E run: 35439993618
- Release Candidate run: 35439993541
- Release Candidate artifact: 10583940385
- Release Candidate artifact digest: sha256:fb3348c4059028aa0711b5fb6fe4576e070bf17a3615172ca28c83c3d543f7e2

## Known boundary

This release evidence establishes the tested repository behavior at the stated SHA. It does not establish external cryptographic signing, HSM/KMS custody, customer infrastructure readiness, or live financial-trading performance.
