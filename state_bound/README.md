# state_bound: TA-001 prototype

Research-only. Not part of immutable Action Gate v1.0.10.

TA-001 tests one narrow hypothesis: on a stable committed trajectory, state-bound execution authority can be verified and executed through one oracle boundary without changing the allowed outcome.

The in-memory StateOracle is append-only. latest() returns the latest committed snapshot and append() creates a new monotonically increasing version.

TA-001 activates only three invariants: action consistency, trajectory consistency, and authority expiry. Action comparison is structural equality and trajectory digest is computed once when a WorldState snapshot is committed, so the verifier does not re-hash the snapshot on every execution.

execute_if_valid() holds the oracle lock across snapshot read, verification and the prototype execution callback. This closes the verify/execute TOCTOU for state owned by this oracle only. External side effects remain outside the guarantee.

equivalent_request() is explicit: two requests are equivalent when their business-critical action objects are equal; world version and epistemic state may differ.

Benchmark scope: 10,000 executions, baseline action-only authorization versus experimental oracle/verifier execution. The first benchmark run showed excessive overhead, so the verifier was reduced to O(1) snapshot checks before further scenarios are allowed.

TA-002 through TA-005 are intentionally not implemented in this prototype.
