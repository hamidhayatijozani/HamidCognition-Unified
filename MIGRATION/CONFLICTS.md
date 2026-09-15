# Phase 0.5 — Conflict Analysis

## 1. P/S/T engines

### Baseline family: exact duplicate
`hamidcognition-complete/core/hamid_cognition.py` and `hamidcognition-v0-max/core/behavior.py` are byte-identical by Git blob SHA `1c71fd77b7bf3cde5665a7eb413d3a55aac0e402`.

The two repositories therefore contain the same P/S/T implementation under different paths.

### Realtime family: distinct evolution
`hamidcognition-realtime/core/hamid_cognition.py` uses a different API and different semantics:
- initial state 0.75 / 0.65 / 0.50 instead of 0.88 / 0.78 / 0.40;
- phase convergence threshold 0.12 rather than 0.15;
- T instability threshold 0.40 rather than 0.45;
- P/S synthesis thresholds 0.80 / 0.75 rather than 0.85 / 0.80;
- market-context driven `update()`;
- `get_decision_bias()`;
- `jump_risk` and `convergence` outputs.

This is a real variant, not a duplicate.

### Standalone engine: related but distinct
`HamidCognition/hamid_cognition_engine.py` shares the same incremental transition equations with the baseline family, but adds state recording and jump-risk calculation and uses normalized 0–1 clipping. It is best treated as a related historical implementation until behavioral tests establish whether it is intended as the same engine.

### Absolute engine: incompatible semantics
`HamidCognitionEngine/hamid_cognition_engine.py` uses `P_new=P*pressure`, `S_new=S*novelty`, `T_new=T/freedom` and absolute phase thresholds P/S > 1.5. This is not a drop-in replacement for the normalized engine.

## 2. Predictors

### GradientBoosting predictor
`hamidcognition-complete/model.py` and `hamidcognition-v0-max/core/model.py` are exact duplicates by SHA `3d7c10c3ea868e3d9652dfaddcfbb399cd49116c`.

It uses `GradientBoostingRegressor` with 100 estimators, learning rate 0.1 and max depth 3, plus five engineered features.

### Realtime predictor
`hamidcognition-realtime/models/predictor.py` is not an LSTM implementation despite its module docstring claiming LSTM. The actual model is `LinearRegression`, with MinMax scaling and a trend-based forecast. It also injects cognitive bias and constructs confidence intervals.

Therefore the predictor families are complementary/alternative implementations, not synonyms. The LSTM claim is currently unverified and should be removed or corrected before being treated as evidence.

## 3. Market feeds

`hamidcognition-complete/market_feed.py` and `hamidcognition-v0-max/data/market_feed.py` are exact duplicates by SHA `84204f60af2fce96d9b35881acd6078cb3e7972c`.

The realtime platform has a materially richer `ForexDataProvider` with caching, yfinance, an Alpha Vantage fallback, historical data and technical indicators.

## 4. Web platforms

`hamidcognition-web/app.py` embeds its own P/S/T engine and a simple trend/bias forecast directly inside Flask. It is not a thin UI over the other engines.

`hamidcognition-complete` uses `main.py` + `core.hamid_cognition` + `model.py` and serves `templates/index.html`.

`hamidcognition-v0-max` uses `main.py` + `core.behavior` + `core.model` + `data.market_feed` and serves the same dashboard blob under a different path.

`hamidcognition-realtime` is architecturally richer: separate cognition, data provider, predictor, API and UI layers.

## 5. Generated artifacts

Multiple repositories contain `__pycache__` and `.pyc` files. These are generated artifacts, not source implementations. They must never become canonical product code.

## 6. Claims requiring verification

The repositories contain README claims such as “real-time”, “accurate prediction”, “LSTM”, “professional”, and trade results. These descriptions are not treated as evidence. Runtime tests, reproducible data, out-of-sample evaluation and provenance are required before those claims enter the canonical product description.

## Current conflict policy

Do not merge conflicting implementations by textual convenience. Preserve distinct variants until a behavioral test demonstrates equivalence or superiority for a defined purpose.
