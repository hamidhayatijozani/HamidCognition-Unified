# EXP-002 — EUR/USD Predictor Leakage and Walk-Forward Audit

Status: STATIC AUDIT + SYNTHETIC HARNESS READY; REAL MARKET OOS AUDIT NOT ESTABLISHED.

Source audited:
`hamidhayatijozani/hamidcognition-realtime/models/predictor.py`
source SHA: `df584043edb5fa5a2037adbc72f1bf90568ac9da`

## Findings from direct inspection

1. The module docstring says LSTM, but the implementation instantiates `LinearRegression`. This is a provenance/documentation contradiction and is preserved as an audit finding.
2. `prepare_features()` fits `MinMaxScaler` on the supplied window. This is safe only when the supplied window ends at or before the prediction timestamp.
3. `predict_future()` computes recent trend and volatility from the supplied dataframe. A caller that passes future rows would therefore create leakage at the evaluation boundary.
4. The implementation has no native train/test or walk-forward boundary. The audit harness must therefore own the temporal split.
5. `train()` fits the regression on the same normalized window used to construct its training target. This is not an out-of-sample validation procedure.
6. `datetime.now()` is used for training/prediction metadata, so timestamps are not deterministic model inputs and must be excluded from behavioral fingerprints.

## Synthetic audit purpose

The included harness verifies the evaluator can enforce a strict temporal boundary: every feature frame supplied to the model must end at or before the forecast origin, while evaluation targets come only from later rows.

The synthetic run is a harness validation, not evidence that the predictor performs well on EUR/USD.

## Promotion gate

A positive predictive claim remains blocked until a real historical EUR/USD dataset is frozen, source fingerprinted, split chronologically, evaluated walk-forward, compared with a naive baseline, and audited for leakage.
