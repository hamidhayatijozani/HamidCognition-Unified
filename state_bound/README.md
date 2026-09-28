# State-Bound Execution Governance Prototype

Research-only experiment. It does not alter the production Action Gate release.

## TA-001 only

The first experiment deliberately tests one stable case before adversarial drift:

Decision -> Authority -> Execution verification

Baseline:
Action -> ALLOW

Experimental:
Action + authorized world snapshot -> VALID

The authorized world is represented by the WorldState object and its six fingerprints:
context, state, evidence, trajectory, environment, policy.

## Current-world boundary

TA-001 uses a deterministic in-memory WorldState. This is a test fixture, not a production freshness guarantee.

## Verification / execution boundary

The prototype measures verification only. It does not claim that a later external side effect is atomic with verification. A production adapter will require a transaction/CAS boundary or will document the residual TOCTOU risk.

## Replay equivalence

For TA-001, replay equivalence means:
baseline == ALLOW AND experimental == VALID

It is deliberately narrow and applies only to the unchanged stable fixture.

## Measurement

TA-001 records median and p95 verifier latency.

Run:
python -m pytest -q state_bound/test_state_bound.py
python -m state_bound.benchmark

No novelty claim is made. The next scenario is permitted only after TA-001 passes.
