# EXP-005 — Adversarial Evidence-Gate Validation

Date: 2026-09-15
Status: PRE-REGISTERED / EXECUTED IN CI

## Question

Can the EXP-004 evidence validator reject artifacts whose declared interpretation conflicts with the underlying evidence, rather than merely recognizing the canonical EXP-004 artifact?

## Core distinction

`FALSIFIED` is a scientific interpretation of an evaluated claim.
`FAILED` is a process or execution failure.
`VALIDATED(FALSIFIED)` means the validator established that the artifact satisfies the pre-declared rules for a falsification result. It does not mean the claim is universally false.

## Pre-registered adversarial cases

1. Canonical EXP-004 falsification must be accepted.
2. `FAILS_PRIMARY_GATE` relabeled as `SURVIVES_PRELIMINARY` with matching forged promotion must be rejected.
3. `all_snapshots_positive = true` while the underlying deltas remain non-positive must be rejected.
4. One snapshot with a positive primary delta must prevent acceptance of a falsification artifact under the all-snapshots gate.
5. A forged primary delta that does not equal `model_accuracy - majority_baseline_accuracy` must be rejected.
6. `snapshots_disjoint = false` must invalidate the artifact.
7. A snapshot marked with `future_features_used = true` must invalidate the artifact.
8. A malformed/tampered source fingerprint must invalidate the artifact.
9. The validator must not be hard-coded to reject survival: a coherent synthetic survival artifact must be accepted with `SURVIVES_PRELIMINARY` and `BLOCKED_PENDING_INDEPENDENT_REPRODUCTION`.

## Acceptance rule

EXP-005 PASS requires every adversarial mutation above to be rejected, the canonical falsification to be accepted, and the coherent survival path to be accepted.

## Scope boundary

PASS establishes resistance to this registered mutation set and demonstrates that interpretation is derived from tested evidence fields. It does not prove completeness, security against every possible mutation, cryptographic provenance, or universal validator correctness.

## Architectural consequence

The research pipeline is therefore treated as:

`Execution → Observation → Interpretation → Validation → Promotion`

with the additional requirement that Validation must independently derive and cross-check Interpretation from evidence rather than trust a result label emitted by the experiment runner.
