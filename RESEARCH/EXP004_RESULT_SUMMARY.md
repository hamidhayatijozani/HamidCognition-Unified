# EXP-004 — Real EUR/USD Walk-Forward Result

Date: 2026-09-15
Status: EXECUTED_REAL_EXTERNAL_WALK_FORWARD
Outcome: **FAILS_PRIMARY_GATE / C-003 FALSIFIED**

## What was tested

EXP-004 evaluates the audited implementation `hamidcognition-realtime/models/predictor.py` recorded by EXP-002, not a substitute model. Direct inspection found that the direction produced by `ForexPredictor.predict_future()` is determined by a LinearRegression slope over the last 20 `Close` observations, with `predicted_price = current_price + slope * minute` when `cognitive_bias` is frozen at 0.

Because the predictor claims +5/+10/+20 minute forecasts, the experiment uses real EUR/USD 5-minute observations from Yahoo Finance. Two non-overlapping external snapshots were evaluated chronologically with no future features and no test-fold tuning.

## Primary +5 minute result

| Snapshot | N | Predictor accuracy | Majority baseline | Delta | Bootstrap 95% CI | Sign-flip p | Cost-aware return |
|---|---:|---:|---:|---:|---|---:|---:|
| A | 3,080 | 0.216558 | 0.507468 | -0.290909 | [-0.314610, -0.267857] | 0.000999 | -0.279231 |
| B | 3,173 | 0.255279 | 0.498267 | -0.242988 | [-0.266940, -0.218090] | 0.000999 | -0.311326 |

The predictor therefore underperformed the naive majority-direction baseline by approximately 24.3 to 29.1 percentage points in both independent snapshots. Both confidence intervals remain entirely below zero.

The +10 and +20 minute horizons were also negative in both snapshots. They are secondary evidence and were not required to trigger falsification.

## Integrity

- `future_features_used`: false
- `test_tuning`: false
- snapshots disjoint: true
- snapshot fingerprints: present
- source interval: 5m
- round-trip friction proxy: 0.0002
- source: Yahoo Finance `EURUSD=X`
- audited predictor source SHA: `df584043edb5fa5a2037adbc72f1bf90568ac9da`

Snapshot A SHA-256: `f53ba55ec94c1b748df31020550556b35f66bacf6e523a0a0dfeddde4be621a7`

Snapshot B SHA-256: `86d93162561a66c84fc92b3f5459fb5d38a345b8650851a24734232ce43eb007`

## Scientific conclusion

C-003 is **FALSIFIED under its pre-registered gate**. The evidence does not support the historical statement that the audited EUR/USD predictor demonstrated out-of-sample predictive skill.

This is a successful research outcome, not a failed experiment. The negative result is retained as evidence and is now an explicit ledger state rather than being hidden behind a failing CI job.

This result does **not** prove that every possible EUR/USD predictor is ineffective. A future predictor may be evaluated only as a new claim with new pre-registration, leakage controls, and independent real-data evidence.
