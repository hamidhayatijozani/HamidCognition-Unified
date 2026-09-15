# Migration Decisions — Phase 0.5

## Decision 001 — Do not merge yet
The target repository is being treated as an integration workspace, not as permission to flatten the source history. No source implementation is copied into canonical/ until the behavioral audit is complete.

## Decision 002 — Baseline P/S/T candidate
The normalized P/S/T engine represented by:
- `hamidcognition-complete/core/hamid_cognition.py`
- `hamidcognition-v0-max/core/behavior.py`

is the current **baseline candidate**, because the two files are exactly identical by SHA.

This is a provisional engineering designation, not a claim that the implementation is scientifically validated.

## Decision 003 — Realtime engine remains a variant
`hamidcognition-realtime/core/hamid_cognition.py` remains separate because its API and thresholds materially differ. It contains capabilities useful for an operational platform, but those changes must be tested before being merged into the baseline model.

## Decision 004 — GradientBoosting is the current baseline predictor candidate
The GradientBoosting predictor in `hamidcognition-complete/model.py` and `hamidcognition-v0-max/core/model.py` is exactly duplicated by SHA. It is therefore one implementation lineage, not two competing predictors.

It is **not yet a validated forecasting model**. The training code currently lacks a documented out-of-sample evaluation protocol, baseline comparison, walk-forward validation and leakage audit. Canonicalization must not imply predictive validity.

## Decision 005 — Realtime predictor is an alternative, not LSTM
`hamidcognition-realtime/models/predictor.py` is actually based on LinearRegression, despite its LSTM wording. It will be retained as an alternative short-horizon predictor until evaluated against the GradientBoosting baseline.

## Decision 006 — Standalone EUR/USD engines remain research artifacts
`HamidCognition/eurusd_engine.py` and `eurusd_engine_real.py` are useful for simulation/prototyping but must not be represented as live trading capability. The inspected implementation uses `MockMT5`, and successful orders are simulated. Real-world market data may come from yfinance, but order execution remains mocked.

## Decision 007 — Web-only implementation is legacy/variant
`hamidcognition-web/app.py` embeds its own cognition and prediction logic. It will not be treated as canonical merely because it is simple or deployable.

## Decision 008 — Generated files excluded
`__pycache__`, `.pyc`, transient state and generated reports are evidence/artifacts, not canonical source, unless a specific reproducibility experiment explicitly requires them.

## Decision 009 — README claims are non-authoritative
README prose is treated as a hypothesis about system capability. Source code, reproducible execution and measured tests outrank marketing language.

## Decision 010 — Git history preservation
A `PROVENANCE.md`/lineage record alone does not preserve Git history. If historical Git objects must be preserved inside Unified, the eventual migration must use actual Git object/merge/ref techniques or retain the original repositories as immutable sources. We will not claim history preservation merely because commit hashes were written into a document.

## Next gate

Before source consolidation:
1. compare remaining files by SHA;
2. establish dependency/runtime compatibility;
3. build behavioral tests for each P/S/T implementation;
4. test predictors using the same frozen dataset and walk-forward protocol;
5. identify broken/stale README claims;
6. then create the first canonical implementation with explicit lineage back to source blobs.
