# EXP-004 — EUR/USD Walk-Forward Predictive Test

Status: PRE-REGISTERED / IMPLEMENTATION REQUIRED

## Claim under test
C-003: the EUR/USD predictor has demonstrated out-of-sample predictive skill.

## Null hypothesis
H0: after costs, the predictor has no reproducible out-of-sample advantage over the declared baselines.

## Alternative
H1: the predictor beats the pre-registered primary baseline on the primary out-of-sample metric across the frozen walk-forward evaluation, without leakage.

## Data rule
Use only timestamped EUR/USD observations available before each prediction timestamp. No future-derived features, labels, scaling, hyperparameter tuning, threshold selection, or model selection may use the test interval.

## Evaluation design
1. Freeze dataset snapshot and cryptographic fingerprint before evaluation.
2. Chronological expanding-window walk-forward evaluation.
3. Each fold trains only on observations strictly preceding its test interval.
4. Primary task: one-step-ahead direction prediction.
5. Primary baseline: majority-direction classifier estimated from the corresponding training window.
6. Secondary baseline: previous-direction persistence.
7. Report accuracy, balanced accuracy, directional hit rate, and a cost-aware simulated return using fixed spread/slippage assumptions declared before scoring.
8. No threshold or parameter tuning on test folds.
9. Include permutation/null test and bootstrap confidence interval over fold-level outcomes.
10. A result is NOT VERIFIED merely because it is statistically positive. Promotion requires independent reproduction on a second frozen snapshot.

## Falsification / survival gate
- FAIL: any detected temporal leakage.
- FAIL: inability to reproduce the exact snapshot fingerprint.
- FAIL: primary metric does not beat the pre-registered baseline under the declared criterion.
- SURVIVES: all integrity checks pass and primary metric beats baseline under the declared criterion.
- VERIFIED remains blocked until independent reproduction succeeds.

## Current epistemic target
This experiment can resolve C-003 only if the predictor implementation and a real historical dataset are both evaluated under this frozen protocol. Synthetic data cannot resolve C-003.
