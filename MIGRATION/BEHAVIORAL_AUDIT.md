# Behavioral Audit — P/S/T Variants

## Status

This is a pre-integration behavioral audit. It is not a claim that the source repositories were executed in CI or production.

## Scope

Compared implementations:

- `hamidcognition-complete/core/hamid_cognition.py`
- `hamidcognition-v0-max/core/behavior.py` (same blob as the complete implementation)
- `hamidcognition-realtime/core/hamid_cognition.py`

The complete/v0-max implementation is SHA-identical (`1c71fd77b7bf3cde5665a7eb413d3a55aac0e402`), so it is one behavioral lineage, not two independent implementations.

## Contract dimensions

Every candidate must eventually be tested against the same frozen input sequence for:

1. Initial state.
2. P/S/T bounds after every transition.
3. Energy calculation and clipping.
4. Phase transition thresholds and priority.
5. Sensitivity to pressure/novelty.
6. History retention at 1000 states.
7. Determinism apart from timestamps.
8. Failure behavior for missing, NaN, infinite, negative, and extreme market inputs.
9. Serialization/export behavior.
10. Compatibility of downstream consumers expecting the returned state schema.

## Material behavioral differences found statically

### Initial state

Baseline lineage starts at P=0.88, S=0.78, T=0.40.

Realtime starts at P=0.75, S=0.65, T=0.50.

These are not cosmetic defaults. They change the first state, phase, energy, and every subsequent trajectory.

### Input transformation

Baseline `step()` consumes `market_pressure` and `market_novelty` directly.

Realtime `update()` first derives:

- `pressure = min(1.0, volatility * 1.5)`
- `novelty = min(1.0, abs(momentum) * 2.0)`

It also accepts `trend_strength` but does not use it in the state transition. That unused input is a contract smell and must not be advertised as causally active until tested.

### Bounds

Baseline clips T to 0.80.
Realtime clips T to 0.85.

P and S use the same 0.10–0.95 bounds.

### Phase thresholds

Baseline:

- rupture if `abs(P-S) < 0.15`
- unstable creativity if `T < 0.45`
- synthesis peak if `P > 0.85 and S > 0.80`
- otherwise steady exploration

Realtime:

- rupture if `abs(P-S) < 0.12`
- unstable creativity if `T < 0.40`
- synthesis peak if `P > 0.80 and S > 0.75`
- otherwise steady exploration

Therefore the same state can receive different phase labels. Phase semantics are not currently interoperable.

### Energy ceiling

Baseline clips energy to 1.5.
Realtime clips energy to 2.0.

The underlying energy formula is materially similar, but the output contract is different.

### Output schema

Baseline `step()` returns timestamp, P, S, T, energy, phase and exposes `get_bias_adjustment()` as a dictionary.

Realtime returns a richer state and exposes `get_state()`, `get_decision_bias()`, jump risk, convergence, market context, and history export.

The realtime implementation is therefore an extension/variant, not a drop-in replacement.

## Analytical trajectory check

A deterministic sequence of pressure/novelty inputs was propagated through the two transition equations to detect divergence before runtime integration. This was equation-level analysis, not execution of the repository code.

Sequence:

`[(0.8,0.4), (0.2,0.9), (0.9,0.7), (0.5,0.1), (0.1,0.9), (0.7,0.6)]`

The trajectories diverge immediately because the initial states differ and the realtime implementation transforms inputs before applying the transition. After six steps, the baseline reaches approximately `(P=0.950,S=0.910,T=0.653, energy=1.254)` while the realtime variant reaches approximately `(P=0.832,S=0.834,T=0.787, energy=1.168)` under the corresponding transformed inputs.

This is evidence of behavioral divergence, not evidence that either model is more correct.

## Current decision

Do **not** merge the realtime implementation into the canonical engine yet.

Do **not** discard it either. Preserve it as a behavioral variant until the following experiment is run:

- identical initial state;
- identical normalized pressure/novelty inputs;
- identical phase/energy contract;
- same frozen test vectors;
- exact state-by-state comparison;
- explicit acceptance thresholds registered before execution.

If the realtime-only features (jump risk, convergence, market context, export) prove useful, they should be added through an explicit versioned contract rather than silently replacing the baseline equations.

## Next gate

1. Build the frozen P/S/T conformance vectors.
2. Execute them against all variants.
3. Audit predictor implementations on the same frozen dataset and walk-forward protocol.
4. Audit dependency/runtime/entrypoint compatibility.
5. Only then create the first canonical source tree.
