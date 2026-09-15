# Canonicalization Gate

Canonicalization is a research conclusion, not a naming decision.

An implementation may become canonical only when all applicable gates pass:

1. **Lineage**: source repository, path, commit and derivation are recorded.
2. **Contract**: inputs, outputs, state variables, bounds, failure behavior and time semantics are explicit.
3. **Conformance**: frozen vectors and behavioral tests pass against the declared contract.
4. **Reproducibility**: the same inputs and declared environment reproduce the same result within the declared tolerance.
5. **Comparative evidence**: materially different variants are tested on identical conditions before one is promoted.
6. **Regression protection**: a test exists for every previously discovered material behavior or failure.
7. **Dependency compatibility**: runtime and dependency constraints are demonstrated, not inferred from requirements files.
8. **Claim hygiene**: names and documentation match the implementation. A docstring cannot upgrade LinearRegression into LSTM, and a simulated execution cannot become live-world evidence by optimism.
9. **Unknown accounting**: unresolved behaviors remain explicitly linked to UNKNOWN or HYPOTHESIS records.
10. **No history destruction**: promotion must preserve source lineage and must not require deleting source repositories.

## Decision classes

- `CANONICAL`: all applicable gates passed with reproducible evidence.
- `CANDIDATE`: plausible baseline, but one or more gates remain open.
- `EXPERIMENTAL`: useful implementation under active investigation.
- `LEGACY`: retained for lineage or compatibility, not recommended as the default.
- `REJECTED`: evidence shows the implementation fails a required contract.
- `UNRESOLVED`: evidence is insufficient to classify safely.

## Current rule

No P/S/T implementation is canonical yet. The normalized complete/v0-max implementation is only the baseline candidate because it has exact duplicate lineage. That lineage is evidence of identity, not evidence of superiority.

No predictor is canonical. Predictor claims require temporal validation, leakage audit, naive baseline comparison and repeated walk-forward evaluation.

No trading result is live-world evidence while execution remains simulated or uses `MockMT5`.
