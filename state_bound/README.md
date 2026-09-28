# State-Bound Execution Governance Prototype

Research-only. This module does not alter the immutable Action Gate commercial release path.

## Tested hypothesis

An execution authority can become invalid or require re-evaluation when the world relevant to the authorization changes after decision issuance.

The prototype distinguishes:

- 'VALID': all bound invariants still hold;
- 'HOLD': authority exists, but context or trajectory drift requires re-evaluation;
- 'UNKNOWN': evidence or live state is no longer sufficient to establish authority;
- 'INVALID': structural authority requirements fail.

'UNKNOWN' never issues execution authority.

## TA scenarios

- TA-001: stable trajectory → 'VALID'
- TA-002: context drift → 'HOLD'
- TA-003: live state drift → 'UNKNOWN'
- TA-004: evidence invalidation → 'UNKNOWN'
- TA-005: trajectory deviation → 'HOLD'

The scenarios are deterministic and executable in 'tests/test_trajectory_reality.py'.

## Current oracle contract

'StateOracle' is an in-memory authoritative prototype:

- writes are append-style or explicit state/context/evidence refreshes;
- 'latest()' returns the latest committed snapshot;
- verify and prototype execution occur under the same oracle lock;
- external side-effect atomicity is explicitly not guaranteed.

## Replay semantics

'equivalent_request()' compares the business-critical action object while allowing world version and epistemic state to differ. This definition is executable, not documentation-only.

## Benchmark boundary

'state_bound/benchmark.py' measures baseline action-only authorization against experimental state-bound verification for TA-001.

'state_bound/trajectory_benchmark.py' verifies expected outcomes for TA-001 through TA-005.

No claim of scientific novelty or universal safety is made by this prototype.
