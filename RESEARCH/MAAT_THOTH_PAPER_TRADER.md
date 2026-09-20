# Maat / Thoth / Paper Trader Research Layer

Status: IMPLEMENTED research harness. Not a validated trading system.

This layer extends the canonical HamidCognition research program without changing the Action Gate product boundary.

## Architecture

~~~text
External Snapshot
      |
      v
     Maat -----> Consensus + provenance fingerprint
      |
      v
    Thoth -----> Signal + confidence + volatility
      |
      v
 Paper Trader -> Simulated execution
      |
      v
 Evidence / Replay
~~~

Maat uses deterministic multi-source consensus. It deduplicates by source, takes the newest observation per source, computes a median center, rejects observations outside a configured relative-dispersion bound, and fingerprints the evidence.

Thoth computes bounded-window momentum and volatility. Its signal is a research artifact, not evidence of predictive skill.

Paper Trader simulates execution with explicit fees and slippage. It never connects to a live trading account.

## Falsification targets

1. Does consensus remain stable when one source is corrupted?
2. Does the signal remain deterministic under replay?
3. Does paper execution remain accounting-consistent under fees and slippage?
4. Does performance survive out-of-sample and walk-forward testing?
5. Does apparent edge disappear under shuffled labels, delayed data, missing sources, or adversarial inputs?

No trading advantage is claimed until these tests produce independent evidence.
