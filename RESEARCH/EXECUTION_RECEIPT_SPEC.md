# HamidCognition Execution Receipt Boundary

**Version:** ER-0.1  
**Status:** Implemented specification  
**Date:** 2026-09-15

## Purpose

Execution Receipt closes the evidence chain after the Validation Boundary. It does not certify that an external-world outcome is true or desirable. It records what execution claims to have happened and cryptographically binds that record to the exact request, decision, action and nonce.

## Required chain

```text
REQUEST
  ↓ request_digest
DECISION
  ↓ decision_digest + decision_id + nonce
EXECUTION
  ↓
RECEIPT
  ↓ receipt_digest
OBSERVATION / OUTCOME
```

A receipt is invalid if any binding value changes.

## Required fields

`receipt_version`, `request_digest`, `decision_id`, `decision_digest`, `action_hash`, `nonce`, `executor_id`, `started_at`, `finished_at`, `status`, `outcome`, `receipt_digest`.

## Invariants

1. A receipt MUST reference the exact request digest.
2. A receipt MUST reference the exact Decision Object identity.
3. A receipt MUST reference the exact action hash and nonce.
4. Execution time MUST be internally ordered.
5. Receipt status MUST be one of `EXECUTED`, `FAILED`, `REJECTED`.
6. Receipt tampering MUST change `receipt_digest`.
7. When executor identity is known, the expected executor MUST match.
8. A receipt MUST NOT be interpreted as proof of external-world truth.

## Epistemic separation

```text
Execution Receipt = evidence about an execution event
                  ≠ proof that the action was correct
                  ≠ proof that the external world accepted it
                  ≠ scientific validation of the underlying claim
```

## Failure semantics

The system should preserve failed executions as evidence. A `FAILED` receipt is not a failed pipeline. It is a recorded execution outcome.
