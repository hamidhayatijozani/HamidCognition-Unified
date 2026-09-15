# Reproducibility Scorecard

Updated: 2026-09-15

This is an evidence-readiness score, not a scientific quality score.

| Criterion | State | Points |
|---|---|---:|
| Source lineage recorded | yes | 1 |
| Frozen deterministic input | yes | 1 |
| Executable runner | yes | 1 |
| Replay verification | yes, V001 | 1 |
| Machine-readable result | yes | 1 |
| Fingerprint chain | yes | 1 |
| Automated CI gate | configured | 1 |
| Immutable external-data fixture | no | 0 |
| Real OOS walk-forward result | no | 0 |
| Release-grade environment lock | no | 0 |

## Current score

**7 / 10 evidence-readiness points**

The score must not be interpreted as a 70% probability of correctness, scientific validity, or project completion. It measures only whether the reproducibility infrastructure needed for the currently recorded experiments exists.

## Promotion rule

A release candidate may not convert this infrastructure score into a scientific claim. Missing external-data evidence, unresolved P/S/T canonicalization, or an unexecuted preregistered hypothesis test remains a blocker for the corresponding claim.
