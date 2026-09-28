# Trajectory / Reality Evaluation Boundary

## Status

**EXPERIMENTAL / RESEARCH-ONLY**

This document defines the v1.1.0 research boundary for testing state-bound execution authority. It does not change the validated v1.0.10 commercial artifact and does not make a commercial safety claim.

## Hypothesis

Action-level authorization can approve an action that becomes unsafe or insufficiently evidenced before execution because relevant context, live state, evidence, trajectory, or environment has changed.

The testable question is:

> Can execution-time evaluation of the authorized action against a committed world state reduce false-allow outcomes relative to action-only authorization without introducing unacceptable false-deny or latency cost?

## Control model

Baseline:

    Action -> Policy -> ALLOW / DENY

Experimental:

    Action
      -> Context
      -> Evidence
      -> Trajectory
      -> Reality State
      -> Decision
      -> Execution Authority
      -> Protected Execution

The prototype intentionally separates:

- Decision: what the current evidence supports;
- Authority: the bounded right to execute;
- Execution: consumption of that authority;
- Outcome: what was observed after execution.

## Epistemic semantics

'DENY' means available evidence establishes that execution is prohibited.

'UNKNOWN' means evidence is insufficient or has been invalidated and therefore cannot establish execution authority.

'UNKNOWN' must never issue execution authority.

'HOLD' means authority requires re-evaluation because a bound invariant changed but the prototype has not classified the situation as epistemically unknown.

## Current test matrix

| Test | Mutation after authority issuance | Expected |
|---|---|---|
| TA-001 | none | VALID |
| TA-002 | context drift | HOLD |
| TA-003 | live state drift | UNKNOWN |
| TA-004 | evidence invalidation | UNKNOWN |
| TA-005 | trajectory deviation | HOLD |

The executable tests are in 'tests/test_trajectory_reality.py'.

The deterministic benchmark is 'state_bound/trajectory_benchmark.py'.

The baseline-versus-experimental latency benchmark for the stable case is 'state_bound/benchmark.py'.

## Oracle contract

The current prototype uses an in-memory 'StateOracle'.

It provides:

- latest committed snapshot;
- monotonic world version for trajectory commits;
- explicit context, state and evidence refresh;
- atomic verification plus prototype callback execution under one oracle lock.

This atomicity applies only to state owned by the oracle. It does not provide distributed exactly-once semantics for arbitrary external side effects.

## Promotion rule

The experimental boundary may enter the commercial Action Gate only if the following are demonstrated on reproducible evidence:

1. false-allow reduction against an explicit baseline;
2. bounded false-deny impact;
3. acceptable p50/p95/p99 latency overhead;
4. deterministic replay;
5. correct UNKNOWN/HOLD semantics under adversarial mutation;
6. protected-tool enforcement at the real execution boundary;
7. no regression in existing HTTP/MCP authorization and replay controls.

Until those conditions are demonstrated, the trajectory/reality layer remains a research extension rather than a customer-facing guarantee.
