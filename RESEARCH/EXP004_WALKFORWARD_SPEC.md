# EXP-004 — EUR/USD Walk-Forward Predictive Test

Status: PRE-REGISTERED / EXECUTED-READY

## Claim under test
C-003: the EUR/USD predictor has demonstrated out-of-sample predictive skill.

## Predictor identity
The audited implementation is `hamidcognition-realtime/models/predictor.py`, source SHA recorded by EXP-002 as `df584043edb5fa5a2037adbc72f1bf90568ac9da`. Direct inspection established that `ForexPredictor.predict_future()` determines direction from a `LinearRegression` slope fitted to the last 20 `Close` observations, with `predicted_price = current_price + slope * minute` when `cognitive_bias` is frozen at 0. EXP-004 evaluates that exact direction-producing mechanism rather than substituting a new predictor.

## Null hypothesis
H0: after declared friction, the audited predictor has no reproducible out-of-sample advantage over the declared baselines.

## Alternative
H1: the audited predictor beats the pre-registered primary baseline on the primary out-of-sample metric across two disjoint real-data snapshots, without leakage.

## Data rule
Use real timestamped EUR/USD 5-minute observations from Yahoo Finance. Intraday data are required because the audited predictor produces +5/+10/+20 minute forecasts. Only observations strictly before each prediction origin may enter the feature window. No future-derived features, labels, scaling, hyperparameter tuning, threshold selection, or model selection may use the test interval.

## Evaluation design
1. Freeze and SHA-256 fingerprint two disjoint real external snapshots.
2. Use an expanding chronological walk-forward origin within each snapshot.
3. For every origin, the predictor receives only the prior 20 closes.
4. Evaluate +5, +10, and +20 minute direction; +5 minutes is the primary metric.
5. Primary baseline: majority-direction classifier from the corresponding training prefix.
6. Secondary baseline: previous-direction persistence.
7. Freeze cognitive bias at 0 so the core predictor is tested without importing an untested cognitive-state signal.
8. Use fixed round-trip friction of 0.0002 for the directional cost proxy.
9. Report accuracy, baseline deltas, cost-aware return, deterministic bootstrap 95% CI, and paired sign-flip permutation p-value.
10. No test-fold tuning or threshold selection.
11. A positive result is not automatically VERIFIED. Promotion remains blocked pending an independent reproduction after this run.

## Falsification / survival gate
- FAIL: any detected temporal leakage.
- FAIL: missing or unverifiable source fingerprints.
- FAIL: primary +5 minute accuracy does not beat the primary baseline in every independent snapshot, or cost-aware return is not positive in every snapshot.
- SURVIVES_PRELIMINARY: all integrity checks pass and both disjoint snapshots pass the primary gate.
- VERIFIED remains blocked until an independent reproduction succeeds.

## Important correction from the first implementation
The first EXP-004 implementation incorrectly used daily ECB observations and a newly invented last-5-return predictor. That could not resolve C-003 because the audited predictor is a minute-horizon intraday predictor. That implementation is superseded by the current EXP-004 evaluator.

## Current epistemic target
This experiment is intended to convert C-003 from `UNKNOWN` toward evidence-backed survival or falsification. It cannot legitimately promote the claim to VERIFIED by itself.
