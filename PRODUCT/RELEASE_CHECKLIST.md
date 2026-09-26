# Action Gate Release Checklist

## Engineering

- [x] Canonical product release is 1.0.5.
- [x] Versioned release artifact published.
- [x] Release checksum asset published.
- [x] Release manifest asset published.
- [x] Publisher records verified source commit.
- [ ] Current-main CI status independently green at the latest main commit. This must be verified from the current workflow runs before treating main as fully release-closed.
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
- Version: 1.0.5
- Release tag: action-gate-v1.0.5
- Source commit recorded by publisher: f3c77cbb314e76911cce37298d58202ffb451d6e
- Release-candidate workflow run: 36087744393
- Release artifact: action-gate-1.0.5.tar
- Release artifact digest: sha256:a4612aaeda25ee35fcb92f35a179666e7c578794f448eac5b3e28ce39f5b630d
- Release checksum asset: action-gate-1.0.5.tar.sha256
- Release checksum digest: sha256:3b7d58861219a656d892e00c8f64e9ffc101df014d13e466bf1a69e0e98a19aa
- Manifest asset: action-gate-1.0.5.manifest.txt
- Manifest digest: sha256:15ee71cf278dd3199e5874c7854bbd1c99a1d3b5e697c2978f73fb6315abaf90

## Known boundary

This evidence establishes the published release artifact and its recorded source provenance. It does not establish customer infrastructure readiness, external signing-key custody, regulatory certification, or live financial-trading performance.

## Commercial close condition

A sale is complete only after a real payment provider has an active product/price and checkout/payment link, followed by an actual successful transaction. Repository documentation alone is not a sale.
