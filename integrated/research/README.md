# P/S/T Shock Recovery Research Engine v1.1

This directory contains an isolated research model. It is not the Canonical P/S/T baseline and is not part of the commercial Action Gate runtime.

## Contract

For external shock distance D_t >= 0:

S(D_t) = D_t / (1 + D_t)

R_t = 1 only when D_t < D_(t-1).

T_(t+1) = clip(T_t + lambda_r * (1 - T_t) * R_t - lambda_s * S(D_t), T_min, T_max)

The phase engine is intentionally absent. This module controls only the research T state.

## Red lines

1. Canonical P/S/T v1.0 remains frozen.
2. Research Recovery Engine v1.1 is excluded from Action Gate commercial claims.
3. A passing local test suite is execution evidence, not GitHub Actions attestation.
4. Persistent shock must never activate recovery.

## Reproduction

From this directory:

python -m pytest -q test_shock_recovery.py

Then:

python run_shock_suite.py

The generated EVIDENCE_PACK.json is deterministic for the same source and input series. Its SHA-256 must be recorded with the commit that produced it.
