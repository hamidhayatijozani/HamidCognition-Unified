# P/S/T Shock Recovery Research Engine v1.1

This directory is an isolated research artifact.

It is not the Canonical P/S/T v1.0 baseline and is not part of the commercial Action Gate runtime.

## State law

The research controller uses:

T(t+1) = clip(T(t) + lambda_r * (1-T(t)) * R(t) - lambda_s * sat(D(t)), Tmin, Tmax)

sat(D) = D / (1 + D)

Recovery gate:

R(t) = 1 only when D(t) <= shock_threshold and delta_D(t) < 0.
Otherwise R(t) = 0.

The phase observer is deliberately absent from this controller. No phase classification changes T.

## Falsification suite

1. No shock: T remains at the baseline.
2. Shock degradation: a spike lowers T.
3. Persistent shock: recovery remains disabled and T does not rise.
4. Shock removal: recovery activates and T rises monotonically.
5. Replay: identical input produces an identical SHA-256 trajectory digest.

The current implementation was executed locally because the repository's GitHub-hosted Actions jobs are currently failing before runner/step execution. Local execution is evidence of code execution, not a substitute for a GitHub Actions attestation.

## Boundary

Canonical P/S/T remains frozen. This research engine must not be described as a capability of the commercial Action Gate unless independently integrated, tested, and released.
