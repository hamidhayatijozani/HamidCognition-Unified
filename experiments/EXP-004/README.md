# EXP-004 — Amplitude-Dependent Restoring Force Retest v2

Status: PROTOCOL READY; EXECUTION BLOCKED UNTIL THE PRIOR DATA/IMPLEMENTATION IS FROZEN.

Hypothesis: in some regulated systems, restoring force may depend on shock amplitude, so normalized response may not be amplitude-invariant.

## Frozen requirements

For each amplitude A, record:
- seed
- parameter set
- code/source fingerprint
- initial state
- forcing/shock sequence
- x(t; A)
- deviation(t; A)
- normalized deviation(t; A)
- recovery/settling metrics only as secondary outcomes

## Pre-registration

The primary test is amplitude dependence of the normalized response, not recovery time alone. Thresholds and sensitivity ranges must be fixed before inspecting the new results.

## Falsification rule

If normalized trajectories remain within the preregistered equivalence band across amplitudes, the amplitude-dependent restoring-force hypothesis is not supported by that experiment.

A poor polynomial extrapolation is not evidence for the hypothesis by itself.
