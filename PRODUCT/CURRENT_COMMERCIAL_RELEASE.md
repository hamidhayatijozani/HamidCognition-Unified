# Current Commercial Release Status

## Sellable release

The currently offerable Action Gate artifact is **v1.0.5**, published as GitHub release `action-gate-v1.0.5`.

Its immutable release target is:

`f3c77cbb314e76911cce37298d58202ffb451d6e`

The published release includes a versioned container archive, SHA-256 checksum, and release manifest.

## Release discipline

Commercial delivery is bound to the tagged v1.0.5 release artifact. Do not represent the mutable `main` branch as the customer's release artifact.

The current `main` branch contains subsequent engineering and research changes. Its GitHub Actions release-validation chain is currently not release-closed because the latest push at commit `e7e056fac6bea187495adf61705fa9ebec0e5591` has failed Actions jobs with zero executed steps. A minimal Actions execution probe was also rerun and failed before any step executed. The available GitHub evidence therefore does not establish a source-code test failure; it establishes that the hosted Actions execution layer is currently preventing fresh validation.

Until that infrastructure condition is resolved and the same-SHA validation chain is green, no new main-head release may be represented as commercially validated.

## Customer delivery rule

For a real customer transaction:

1. quote the exact product version;
2. identify the exact release/tag and source commit;
3. provide the release artifact and checksum;
4. apply the selected license and deployment scope;
5. run the customer acceptance procedure against the customer's deployment;
6. settle the invoice in USDT under the payment policy;
7. record the transaction hash and entitlement.

## Product boundary

Action Gate is a pre-execution authorization and evidence boundary for AI-agent tool execution. It does not claim universal AI safety, downstream tool correctness, regulatory certification, or guaranteed business outcomes.

## Commercial gate

A release is commercially closed only when its exact artifact, provenance, acceptance boundary, license terms, and payment/entitlement procedure are all identifiable. Repository documentation alone is not evidence of a completed sale.
