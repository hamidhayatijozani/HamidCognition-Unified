# Action Gate Release Checklist

## Engineering

- [x] Canonical product release is 1.0.10.
- [x] Versioned release artifact published.
- [x] Release checksum asset published.
- [x] Release manifest asset published.
- [x] Publisher records verified source commit.
- [ ] Current-main CI status independently green at the v1.0.10 release source commit.
- [ ] Signing material externally managed. This remains an operational deployment requirement.

## Security

- [x] No production secrets are committed in the product environment template.
- [x] Actor/session/tenant binding is covered by the product validation boundary.
- [x] Nonce single-use and persistence are covered by the product acceptance boundary.
- [x] Evidence failure is fail-closed.
- [x] SANDBOX cannot cross the production execution boundary.
- [x] Direct downstream bypass is constrained by the enforcement contract.
- [x] Release write privileges are isolated from build/evidence workflows.

## Customer delivery

- [x] Deployment contract delivered.
- [x] Integration contract delivered.
- [x] Environment template delivered.
- [x] Operations runbook delivered.
- [x] Customer acceptance procedure delivered.
- [x] Delivery manifest delivered.
- [x] Versioned product release published.

## Exact published release evidence

- Product: HamidCognition Action Gate
- Version: 1.0.10
- Release tag: action-gate-v1.0.10
- Source commit recorded by publisher: 77d820e99dc78a6a9e3217d3c1c49d5cdf07813f
- Release-candidate workflow run: 36303350191
- Release artifact: action-gate-1.0.10.tar
- Release artifact digest: sha256:10bb53b69b56ff86146f5c71e3e5d7e34dacb4e12dba2adafc59f9d5276abd91
- Release checksum asset: action-gate-1.0.5.tar.sha256
- Release checksum digest: sha256:1f57c20d6d27608c817fd695f963b33b8bd5c69c3d37a9052a519f2d45fb4dfa
- Manifest asset: action-gate-1.0.5.manifest.txt
- Manifest digest: sha256:bcf4aceeee10e18bfbb358d95116d357e0f6fa9bb796527b2d2a930e8427f5e5

## Known boundary

This evidence establishes the published release artifact and its recorded source provenance. It does not establish customer infrastructure readiness, external signing-key custody, regulatory certification, or live financial-trading performance.

## Commercial close condition

A sale is complete only after a real payment provider has an active product/price and checkout/payment link, followed by an actual successful transaction. Repository documentation alone is not a sale.
