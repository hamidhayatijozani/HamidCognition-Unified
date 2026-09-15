# ClaimLab — Epistemic Integrity Check Review

**Review status:** ACCEPTED AS ENGINEERING/RESEARCH CRITIQUE
**Date:** 2026-09-15
**Scope:** Review of the previously presented ClaimLab-style integrity scoring implementation and its reported test results.

## 1. Purpose

This document records a critical review of the implementation claims around an epistemic-integrity score. It is deliberately conservative: an implementation can be executable without its scoring model being scientifically validated.

## 2. Findings

### Finding F-001 — Syntax defects

The reviewed code excerpt contains three syntax/entry-point defects:

- `0.4E` must be expressed as multiplication, e.g. `0.4 * E`.
- `def init` is not a Python constructor; the constructor is `def __init__`.
- `if name == "main"` is not the Python module entry-point guard; the canonical form is `if __name__ == "__main__":`.

**Assessment:** VERIFIED against the reviewed source excerpt, if that exact excerpt is the artifact under test.

### Finding F-002 — The score is heuristic

A formula of the form

`0.4 * E + 0.25 * (1 - J) + 0.2 * C - 0.15 * O`

contains manually selected weights unless an empirical calibration, optimization procedure, or theoretical derivation establishes otherwise.

**Assessment:** The score must be classified as **HEURISTIC** unless such evidence is separately recorded. The existence of a numerical score does not establish scientific validity, optimality, calibration, or predictive validity.

### Finding F-003 — Boolean evidence presence is insufficient

`evidence_present=True` collapses materially different evidence states into one bit. At minimum, an evidence record should distinguish presence from source identity, provenance, reproducibility, and verification status.

A structured representation should therefore carry fields such as:

```json
{
  "present": true,
  "source": "IRNA article 2024-05-12",
  "provenance_hash": "sha256:...",
  "reproducible": true
}
```

The example above is a schema illustration, not a claim that the cited source has been independently verified by this repository.

### Finding F-004 — Score and verdict must remain separate

An integrity score is an assessment signal, not a verdict by itself.

For example:

```json
{
  "integrity_score": 0.82,
  "verdict": "WEAK",
  "decision": "ASK"
}
```

The exact thresholds and mapping from score to verdict/decision require their own specification and evidence. A score of `0.82` must never be silently interpreted as `ALLOW`, `VALID`, or equivalent.

### Finding F-005 — Naming boundary

The capability should be described as **Epistemic Integrity Check**, not **Truth Detector**, unless the system can substantiate the much stronger claim implied by the latter name.

The preferred boundary is:

> evaluates evidence and epistemic integrity signals; it does not determine objective truth.

### Finding F-006 — Synthetic test data does not establish real-world validity

If the reported `test_results` were produced from ten synthetic texts, those results establish, at most, behavior on that synthetic test set. They do not establish performance on real-world claims, sources, or distributions.

A corrected implementation therefore must not inherit scientific validity from synthetic test results alone.

## 3. Required implementation boundary

The following distinction is mandatory for future ClaimLab-related work:

`implementation != validation != scientific support`

Likewise:

`target metric != measured metric`

`test definition != executed result`

`synthetic fixture != real-world evidence`

## 4. Required next-state contract

Before an Epistemic Integrity Check is used as evidence in a decision engine, the artifact should expose separately:

1. structured evidence metadata;
2. integrity score, explicitly labeled heuristic unless calibrated;
3. verdict, with an independently specified mapping;
4. downstream decision, if any;
5. provenance and reproducibility state;
6. test-data class (synthetic, fixture, or real external source);
7. execution record sufficient to reproduce the reported result.

## 5. Benchmark restriction

Unless and until the score is empirically calibrated and independently validated, the score **must not be presented as a scientific benchmark, accuracy measure, truth probability, or objective truth detector**.

It may be used as a heuristic signal inside a decision system, provided that the downstream system preserves the distinction between signal, verdict, and enforcement decision.

## 6. Repository interpretation

This review is an evidence-boundary document. It does not certify the reviewed implementation, its historical `test_results`, or any scientific claim not backed by an executable and reproducible artifact in this repository.

The repository's governing rule remains:

> وجود کد ≠ اعتبار علمی

and, more specifically for ClaimLab:

> numerical score ≠ truth
> 
> evidence flag ≠ provenance
> 
> synthetic test ≠ real-world validation

## 7. Disposition

**Accepted as a corrective engineering/research review.**

Future changes should implement the corrections above and then add executable tests demonstrating the new behavior. The review itself is not evidence that those corrections have already been implemented.
