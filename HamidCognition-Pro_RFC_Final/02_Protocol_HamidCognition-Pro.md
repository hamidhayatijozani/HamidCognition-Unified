# HamidCognition-Pro Protocol: Four Research Phases

## Goal
Build a measurable, auditable agent-assisted market-research system. Terms such as “self-evolving” describe hypotheses until repeatable experiments demonstrate them.

## Phase 1: data ingestion
Ingest timestamped market data from an explicitly configured provider. Validate schema, sequence, timestamps, gaps, and market-session status. Flag anomalies for review; never silently rewrite source data.

## Phase 2: decision research
Train candidate models offline. Compare against naive and simple baselines using chronological splits, transaction costs, slippage, and leakage checks. No model may self-promote to live trading.

## Phase 3: execution boundary
Keep broker integration disabled by default. Before any live-order capability, require explicit credentials supplied securely, sandbox tests, position/risk limits, idempotency, reconciliation, and a separate human-approved deployment decision.

## Phase 4: adaptive research
Permit parameter experiments only in isolated research runs. Version every dataset, feature set, model, config, and result. Freeze candidate models before out-of-sample evaluation; prohibit tuning on the evaluation window.

## Required invariant
Missing data, stale state, failed provenance, or an unavailable risk check means **HOLD / no execution**, not a guessed action.
