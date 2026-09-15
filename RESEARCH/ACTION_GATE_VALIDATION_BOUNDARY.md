# Action Gate Validation Boundary v0.1

**Status:** IMPLEMENTED / ADVERSARIAL TESTED
**Scope:** HamidCognition Action Gate
**Originator:** Hamid Hayati Jozani
**Date:** 2026-09-15

## Purpose

The Validation Boundary is the epistemic and executable boundary immediately before Action Gate execution. It answers a narrow question:

> Is this exact action request accompanied by a structurally valid, fresh, request-bound Decision Object whose execution state is permitted by the boundary?

It does **not** decide whether a claim is true, whether evidence proves the world, or whether an action is morally/correctly desirable. Those are separate layers.

## Core separation

```text
CLAIM          != FACT
EVIDENCE       != TRUTH
VALIDATION     != AUTHORIZATION
DECISION       != EXECUTION
EXECUTION      != OBSERVATION
OBSERVATION    != INTERPRETATION
```

A narrative field, confidence score, model label, or evidence citation cannot silently become an authorization primitive.

## Boundary contract

```text
ActionRequest
    |
    v
[ REQUEST VALIDATION ]
    |
    v
[ EVIDENCE VALIDATION ]
    |
    v
[ DECISION BINDING + FRESHNESS ]
    |
    v
Decision Object
    |
    +--> DENY / ASK / DEFER  --> STOP
    |
    +--> ALLOW / SANDBOX ----> EXECUTION LATCH
                                  |
                                  v
                               ACTION
                                  |
                                  v
                             OBSERVATION
```

The final execution latch is deliberately stricter than ordinary decision validation.

## Machine-checkable invariants

1. **No validation bypass:** an action cannot execute without a valid Decision Object.
2. **Exact-request binding:** the decision must contain the canonical SHA-256 digest of the exact request being executed.
3. **No stale authority:** an expired decision cannot authorize execution.
4. **No future authority:** a decision issued materially in the future cannot authorize execution.
5. **No label authority:** interpretation, confidence, or narrative fields cannot authorize execution.
6. **Fail closed:** malformed, missing, conflicting, invalid, or unverifiable evidence cannot produce an executable ALLOW.
7. **Decision-state closure:** only ALLOW and SANDBOX are executable states. DENY, ASK, and DEFER terminate the execution path.
8. **Mutation resistance:** changing target, parameters, requester, or other request material after validation invalidates the binding.
9. **Boundary versioning:** a decision is valid only against a supported boundary version.
10. **No truth laundering:** successful validation means only that the object satisfies the boundary contract. It does not establish that its claims are true.

## Evidence states

```text
PRESENT       artifact_ref + sha256 required
MISSING       evidence unavailable
INVALID       evidence structure or integrity invalid
STALE         evidence outside declared freshness boundary
CONFLICTING   independent evidence disagrees
```

The boundary validates evidence metadata and declared state. It does not independently certify external reality merely because a hash exists.

## Adversarial test surface

The initial test suite deliberately attacks the boundary rather than rewarding its happy path:

- request/decision replay across different targets
- parameter mutation after validation
- forged ALLOW with missing evidence
- invalid evidence states
- expired decisions
- future-dated decisions
- DENY/ASK/DEFER execution attempts
- label/confidence injection
- changing a DENY to ALLOW while leaving a forged request digest
- canonicalization stability for equivalent JSON key order
- valid SANDBOX execution with exact request binding

These tests are **negative controls**. A test passes when the boundary rejects the attempted bypass. A green CI result therefore means the attack was contained, not that the world is safe. Humanity survives another test suite.

## What the boundary deliberately does not claim

The boundary does not establish:

- scientific truth;
- correctness of an external provider;
- safety of an arbitrary real-world action;
- identity authenticity beyond the identity material supplied to it;
- absence of hidden side effects;
- authorization policy completeness;
- adversarial security completeness.

Those require independent controls and evidence.

## Promotion meaning

```text
VALIDATION_PASS
    means
BOUNDARY_CONTRACT_SATISFIED

not

WORLD_TRUTH_ESTABLISHED
```

This distinction is mandatory for all downstream reporting.

## Next boundary expansion

The next version should add a cryptographically or otherwise independently anchored **execution receipt** connecting:

```text
request_digest
    + decision_digest
    + executor identity
    + execution start/end
    + observed result
    + output digest
```

to prevent a valid pre-action decision from becoming a false post-action history. This is the natural next frontier because pre-action validation alone cannot prove that the action actually executed as authorized.
