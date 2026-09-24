# STI-001 — Transition Integrity Discrimination Test

**Status:** PROTOCOL  
**Date:** 2026-09-24

## Question

Can explicit transition-integrity features detect a class of failures that outcome-only, confidence-only, and provenance-only evaluation miss?

## Experimental factors

Construct controlled trajectories with identical final outputs but different hidden transition conditions:

- valid evidence-aligned transition;
- unsupported level jump;
- corrupted provenance;
- semantic drift;
- common-mode validator failure;
- missing evidence;
- contradictory evidence.

## Evaluators

A. Outcome-only  
B. Confidence-only  
C. Provenance-only  
D. Explicit STI dimensions

No composite STI score is allowed in the first experiment.

## Ground truth

Synthetic ground truth must be generated before evaluator results are observed. Each trajectory receives an independently specified failure label.

## Primary outcome

Detection of transition-integrity failures at fixed false-positive rates.

## Secondary outcomes

- calibration;
- false negatives by failure type;
- sensitivity to missing evidence;
- robustness under reordered events;
- replay divergence;
- cross-version semantic drift detection.

## Required controls

- simple rule-based baseline;
- shuffled-transition control;
- provenance-complete-but-wrong control;
- correct-final-output/wrong-transition control;
- repeated seeds.

## Falsification criteria

The STI representation should be rejected or narrowed if it:

1. does not outperform the simpler baselines on a pre-registered failure class;
2. only detects failures because it receives information unavailable to baselines;
3. collapses under modest perturbation;
4. depends on post-hoc labels;
5. cannot distinguish semantic drift from ordinary state change.

## Evidence record

Every run must record the existing experiment fingerprint fields:

dataset, preprocessing, parameters, seed, code commit, environment, execution timestamps, output hashes and result status.

## Promotion rule

A successful synthetic result is evidence for continued research only. It is not evidence of general cognitive validity.

