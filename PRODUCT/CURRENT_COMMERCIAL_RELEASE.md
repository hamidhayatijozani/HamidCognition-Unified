# Current Commercial Release Status

## Published release

The current published Action Gate customer-delivery release is **v1.1.0**, published as GitHub release `action-gate-v1.1.0`.

Verified source commit:
`43e558deacbe3df06554f79178b922b27ac94b1a`

The published release includes:
- versioned production container archive;
- SHA-256 checksum;
- release manifest;
- source commit binding;
- release-candidate evidence.

## Release validation

The v1.1.0 source revision was published through the dedicated release workflow after the release-candidate evidence chain completed.

Release-candidate workflow run:
`36309864630`

The primary release artifact is:
`action-gate-1.1.0.tar`

Artifact SHA-256:
`sha256:8c6381a3c7693fa182a21cf8f298e1d77adbdeb6161291094731faf451257a92`

## Release versus main

The release tag is the customer-delivery reference point. The mutable `main` branch is not automatically equivalent to the published release.

At the time this document was synchronized, `main` was ahead of the v1.1.0 source commit and contained subsequent changes, including MCP E2E and production-gate work. Those changes are not retroactively part of v1.1.0.

Any post-v1.1.0 change intended for customer delivery must pass a new release-control cycle and receive a new release identity.

## Customer delivery rule

1. quote the exact product version;
2. identify the exact release/tag and source commit;
3. provide the release artifact and checksum;
4. apply the selected license and deployment scope;
5. run the customer acceptance procedure against the customer's deployment;
6. settle the invoice in USDT under the payment policy;
7. record the transaction hash and entitlement.

A sale is not marked paid from a screenshot or customer assertion alone. Settlement requires an independently recorded transaction hash and the configured confirmation policy.

## Product boundary

Action Gate is a pre-execution authorization and evidence boundary for AI-agent tool execution. It does not claim universal AI safety, downstream tool correctness, regulatory certification, or guaranteed business outcomes.

## Commercial boundary

Supported delivery modes are SELF_HOSTED, MANAGED and ENTERPRISE.

Repository and CI evidence establish technical release readiness. They do not establish that a customer transaction has occurred, nor do they substitute for customer-specific acceptance, licensing, payment settlement, or deployment configuration.

## Payment boundary

Commercial settlement is USDT only.

The repository must never contain a private wallet key. A real transaction requires the operator's configured receiving address, network policy, invoice, transaction hash, confirmation evidence, and entitlement record.
