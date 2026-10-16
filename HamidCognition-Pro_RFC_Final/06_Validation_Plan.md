# Validation Plan

All thresholds below are proposed acceptance criteria, not achieved results.

| Metric | Proposed threshold | Evidence required |
|---|---:|---|
| Replay stability | >= 95% | 1,000 frozen-input replays across restarts |
| Replay correctness | >= 99% | Independent expected-decision fixtures |
| False-allow rate | <= 1% | Adversarial cases with explicit labels |
| False-deny rate | <= 5% | Controlled legitimate-action set |
| Predictive edge | Must beat baselines after costs | Untouched chronological holdout and uncertainty intervals |

## Test groups
1. Missing, stale, duplicated, and out-of-order market data.
2. Forged evidence references and modified decision records.
3. Concurrent execution attempts, restart, timeout, and provider outage.
4. Model comparison against naive and simple baselines.
5. Paper-trading with spread, fees, slippage, and position limits.

Publish raw sample counts, exclusions, version hashes, confidence intervals, and failed runs. CI success is not proof of live deployment or profitability.