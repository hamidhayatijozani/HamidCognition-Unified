# EXP-002 Reproducibility Package

Status: REPRODUCIBILITY PACKAGE READY — RESULT PRESERVED

## Purpose
Reproduce the existing EXP-002 audit outcome without changing the predictor, thresholds, or historical conclusion.

## Frozen identity
- Predictor source SHA: `df584043edb5fa5a2037adbc72f1bf90568ac9da`
- Claim: no out-of-sample performance claim is established.
- Required property: chronological separation between training/development information and evaluation data.
- Primary rule: reproduction must not tune the predictor against the evaluation result.

## Required artifacts
1. Predictor source at the frozen SHA.
2. Frozen input snapshot(s), with cryptographic fingerprint.
3. Exact feature-construction configuration.
4. Exact evaluation configuration.
5. Leakage audit output.
6. Reproduction result with PASS/FAIL/INCONCLUSIVE status.
7. Hashes for all immutable inputs and generated evidence.

## Execution sequence
1. Checkout the frozen predictor SHA.
2. Load only the frozen input snapshot.
3. Reconstruct features without using future evaluation observations.
4. Run the pre-registered evaluation procedure unchanged.
5. Run the leakage audit independently.
6. Compare the reproduced result with the archived EXP-002 result.
7. Record any byte-level or semantic difference as a reproducibility deviation.
8. Do not modify thresholds after observing the result.

## Acceptance gate
REPRODUCED only if:
- predictor identity matches;
- input fingerprint matches;
- evaluation configuration matches;
- leakage audit passes;
- result classification matches the archived conclusion.

Otherwise classify as DEVIATION and preserve the mismatch evidence.

## Scientific constraint
A negative result remains a valid result. This package exists to reproduce the existing finding, not to manufacture a positive trading result.

## Next linked work
- EXP-003: external-feed replay/provenance sensitivity.
- EXP-004: amplitude-dependent restoring-force experiment.
- EUR/USD walk-forward files currently carrying the EXP-004 name must be treated as a separate identity and corrected to avoid registry collision.