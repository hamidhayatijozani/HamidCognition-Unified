# EXP-001 — P/S/T Variant Conformance and Replay

Status: EXECUTED (research evidence package)

EXP-001 compares four historically existing P/S/T implementations without selecting a winner in advance. The experiment freezes one deterministic input vector, maps that vector into each implementation's actual input contract, records source SHAs, computes trajectories, compares state divergence, and verifies replay determinism.

## Source variants

- V-A: `hamidhayatijozani/hamidcognition-complete/core/hamid_cognition.py`
  - source blob SHA: `1c71fd77b7bf3cde5665a7eb413d3a55aac0e402`
- V-B: `hamidhayatijozani/hamidcognition-realtime/core/hamid_cognition.py`
  - source blob SHA: `3cf67fec9a95198a1045dab98ee0ce6016d90e54`
- V-C: `hamidhayatijozani/HamidCognition/hamid_cognition_engine.py`
  - source blob SHA: `226c748173c98017d65446735c0fe87f09506073`
- V-D: `hamidhayatijozani/HamidCognitionEngine/hamid_cognition_engine.py`
  - source blob SHA: `589ab1e0e0330d0efaff088ef67bb79a8e86f04d`

## What the inspection established

V-A and V-C share the same broad transition equations but differ in clipping bounds, phase threshold (`0.15` vs `0.10`) and output precision. V-B derives pressure and novelty from market context and has different initial defaults, phase thresholds and a different T upper bound. V-D is not a normalized incremental P/S/T engine: it multiplies P and S by inputs and divides T by `freedom`, then uses an absolute threshold taxonomy.

Therefore a single arbitrary OHLC market vector would not be a valid common semantic input. EXP-001 instead uses controlled `pressure` and `novelty`, with an explicit lossless mapping for V-B: `volatility = pressure / 1.5`, `momentum = novelty / 2`. `trend_strength` is held constant because V-B reads it but does not use it in its transition equations. V-D receives the same pressure/novelty pair and a fixed `freedom=3.0` because those are its actual parameters.

## Frozen vector

`inputs/vector-001.json` contains 10 deterministic transitions from the common initial state `P=0.88, S=0.78, T=0.40`. It contains no expected outputs, so expected behavior is not smuggled into the input.

Vector SHA-256:
`54af954904c54efc7b70bdfe00ecf6b7b80bc8a9cdc628cfcba6e1beb068f16c4e620a`

## Verdict rule

EXP-001 does not define "best". It reports:

- `EQUIVALENT`: exact state trajectory equality under the frozen vector and comparison contract.
- `DIVERGENT`: both implementations are executable under the contract but their trajectories differ.
- `INCOMPATIBLE`: the implementation cannot be represented under the common input/output contract without semantic alteration.

For this run, all four implementations executed. All pairwise trajectories were divergent. V-D is additionally structurally incompatible with the normalized P/S/T semantics used by V-A/V-B/V-C, so its numerical divergence must not be interpreted as evidence that V-D is inferior.

## Replay

`replay.py` executes the same vector twice through every variant and compares the resulting fingerprints. The recorded run produced deterministic replay for all four variants.

This is evidence of deterministic replay for this vector and these source semantics only. It is not proof of global reproducibility, canonical correctness, or scientific validity.
