# Chemical-Reactivity-Inspired Action Model

Status: EXPERIMENTAL / RESEARCH-ONLY

## Purpose

This experiment transfers a small set of observable concepts from chemistry into a
deterministic model for AI-agent execution conditions.

It does **not** claim that chemical laws prove the security architecture, and it does
not replace Action Gate authorization.

## Mapping hypothesis

| Chemistry-inspired behavior | Execution analogue |
|---|---|
| Reactivity | likelihood that execution conditions permit progression |
| Activation conditions | minimum conditions required before progression |
| Inhibitor | condition that suppresses progression |
| Equilibrium / stability | persistence of valid context, state, evidence and trajectory |
| Reaction environment | execution context and current world state |
| Chain reaction | downstream actions changing conditions for subsequent actions |

## Implemented model

`reactivity = activation × geometric_mean(context, state, evidence, trajectory) × (1 - inhibition)`

The result is bounded to `[0,1]`.

Decision semantics:

- `PROCEED`: activation threshold is met and stability is sufficient.
- `INHIBIT`: inhibition threshold is reached.
- `HOLD`: stability has fallen below the configured floor.
- `UNKNOWN`: conditions are insufficient to justify progression.

The model is deterministic and parameterized so experiments can be replayed.

## Safety boundary

The reactivity result is **not** execution authority. A `PROCEED` result cannot
authorize a tool call by itself. Action Gate remains the enforcement boundary.

The model must never:

- grant itself authority;
- bypass nonce, subject, action, expiry, or world-state verification;
- mutate production state from research;
- turn an analogy into an unsupported scientific claim.

## First falsification experiments

1. Hold activation constant and mutate one stability factor. Expected result:
   reactivity decreases monotonically.
2. Hold all stability factors constant and increase inhibition. Expected result:
   reactivity decreases and eventually reaches `INHIBIT`.
3. Replay identical factors. Expected result: identical result and score.
4. Compare chemical model output with existing `state_bound.verifier` outcomes.
   A mismatch is evidence for model revision, not a reason to override the verifier.

## Promotion gate

Promotion beyond research requires measured improvement against a baseline,
including false-allow behavior, false-deny behavior, latency, deterministic replay,
adversarial drift handling, and enforcement-boundary regression tests.


## Import and authority boundary

The direction is one-way:

**Action Gate may consume a research assessment; the chemical/state-bound research layer must not import or invoke Action Gate.**

The current implementation keeps the chemical modules independent of `action_gate.*`.
A subprocess runtime probe verifies that importing `state_bound` does not load any
`action_gate` module. This runtime check complements static inspection because AST
inspection alone cannot detect dynamic imports.

`PROCEED` means **REQUEST_ACTION_GATE_AUTHORIZATION** and never grants authority.
`HOLD` means **REQUIRE_REEVALUATION**; Action Gate consumes it as `ASK`.
`UNKNOWN` means **REQUIRE_EVIDENCE**; Action Gate consumes it as `ASK`.
`INHIBIT` means **BLOCK_REACTION**; Action Gate consumes it as `DENY`.

The research output is a condition signal, not an authority token. Only Action Gate converts the signal into an execution decision.

## Determinism proof boundary

Determinism is tested both twice in-process and across two fresh Python processes.
A single hash fixture is therefore not treated as proof of cross-version
determinism. Python-version upgrades remain a separate reproducibility dimension.
