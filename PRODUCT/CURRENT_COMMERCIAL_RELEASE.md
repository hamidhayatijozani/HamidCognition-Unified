# Current Commercial Release Status

## Current development line

The current Action Gate product version on `main` is **v1.1.0**, sourced from `action_gate/VERSION`.

This is the current development/release-candidate line. It is **not yet an independently validated published commercial release** merely because the version file says 1.1.0.

## Last validated published release

The last independently validated and published Action Gate release is **v1.0.10**, published as GitHub release `action-gate-v1.0.10`.

Verified source commit: `77d820e99dc78a6a9e3217d3c1c49d5cdf07813f`.

The published release includes:
- versioned production container archive;
- SHA-256 checksum;
- release manifest;
- source commit binding;
- release-candidate evidence.

Release-candidate workflow run: `36303350191`.

The v1.0.10 release artifact digest is:
`sha256:10bb53b69b56ff86146f5c71e3e5d7e34dacb4e12dba2adafc59f9d5276abd91`.

## v1.1.0 release rule

v1.1.0 becomes an offerable published release only after all of the following refer to the same source SHA:
1. product gates pass;
2. security validation passes;
3. Clean-Room verification passes;
4. production E2E validation passes;
5. release-readiness validation passes;
6. reproducible release artifact is produced and hashed;
7. release record/tag is published against that exact source revision.

Until then, customer-facing material must describe v1.1.0 as the current development/release-candidate line and v1.0.10 as the last validated published release.

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
