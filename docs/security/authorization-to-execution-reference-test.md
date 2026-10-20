# Authorization-to-execution state-change reference test

## Purpose

A deterministic, standard-library-only fixture for the stale-authorization invariant proposed in [OASB issue #257](https://github.com/opena2a-org/oasb/issues/257).

## Run

```bash
python3 -m unittest discover -s tests/security -p 'test_authz_state_change.py' -v
```

## Expected cases

- State changes from A to B after authorization: block.
- Same action and same context version: allow.
- Action payload is substituted after authorization: block.
- Current context is unavailable: fail closed.
- Policy decision is deny: do not execute.

## Scope and limitations

This is a reference-model test, not proof that the BESAZ runtime currently enforces these properties. The fixture has no real tool side effects, database, concurrency, or OASB adapter. It does not claim OASB compatibility, benchmark success, maintainer acceptance, or production readiness. A next integration step must bind the same assertions to the actual BESAZ enforcement path and prove that a denied/stale operation causes zero protected side effects.
