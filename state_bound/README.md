# State-Bound Execution Governance Prototype

Research-only prototype for testing one hypothesis:

> When authorization is separated from execution in time, action-level
> authorization can be insufficient if the world relevant to the decision
> has changed.

The prototype keeps four objects separate:

Decision -> Authority -> Execution -> Outcome

An authority is valid only while the bound invariants remain true:

- action
- context
- state
- evidence
- trajectory
- environment
- policy

This is not a novelty claim and is not part of the immutable Action Gate
v1.0.10 release. It is an experimental layer for adversarial evaluation.

UNKNOWN, CONFLICTED, STALE and UNVERIFIED epistemic states cannot issue
execution authority.

The first benchmark compares a baseline action-only check with this
state-bound verifier under controlled drift scenarios.
