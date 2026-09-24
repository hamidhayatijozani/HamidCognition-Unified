# Cross-Line Research Synthesis — 2026-09-24

## Purpose

This document records a cross-project synthesis derived from the current Unified repository and prior research artifacts. It identifies recurring mechanisms without converting conceptual similarity into proof.

## Highest-value recurring mechanisms

### 1. State transition over final output

Multiple research lines represent cognition as changing state over time rather than a static answer.

### 2. Evidence-to-claim lineage

The project repeatedly preserves the path:

```
source → evidence → experiment → observation → claim
```

This is stronger as a research primitive than a generic "confidence" field because lineage can be audited.

### 3. Epistemic distance

Claim strength can exceed evidence strength. The existing ClaimLab/RFC work provides an operational starting point for detecting this gap.

### 4. Epistemic integrity versus decision permission

The Action Gate architecture separates "what is supported" from "what may be executed". This prevents confidence from being treated as authorization.

### 5. Replay as a scientific object

A result is not fully characterized by its output. Re-execution, provenance and divergence are themselves measurable.

### 6. Contradiction and unknown as first-class states

The project explicitly avoids forcing anomalies into the current model. This creates a path for studying unexplained behavior instead of laundering it into a narrative.

### 7. Dynamic state + memory + regime change

P/S/T, LUMEN, market research and streaming/regime work share an abstract structure:

```
stream → memory → state estimate → transition/regime → action → feedback
```

The shared structure is a research observation, not proof that the underlying mechanisms are identical.

## Candidate unifying object

**State Transition Integrity (STI)** is introduced as a hypothesis connecting these mechanisms.

The central question:

> Can the integrity of a state transition be measured independently of the final outcome?

If yes, STI may provide a common measurement layer across cognitive-state, epistemic, governance and dynamic forecasting experiments.

If no, the abstraction should be rejected or narrowed.

## Research priority

The highest-information experiment is not another implementation. It is a controlled comparison between:

- outcome-only evaluation,
- provenance-only evaluation,
- confidence-only evaluation,
- explicit transition-integrity evaluation.

The test should use synthetic ground truth first, then independent real datasets where appropriate.

## Evidence boundary

Current repository evidence establishes implemented artifacts and several engineering/replay boundaries. It does not establish STI as a validated scientific construct, nor does it establish universal novelty.

## Anti-self-confirmation rule

Any experiment supporting STI must be paired with at least one experiment designed specifically to produce a failure case.

