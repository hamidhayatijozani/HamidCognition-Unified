# Integration Guide

## Requirements
- Python 3.10 or newer.
- A pinned dependency set and repeatable CI environment.
- A market-data provider with documented timestamps and terms, if market research is enabled.

## Integration order
1. Run governance unit tests.
2. Connect the decision artifact to the existing API in a separate reviewed change.
3. Replace hard-coded metrics with measured, traceable inputs.
4. Add persistence and replay tests.
5. Add market-data ingestion in read-only mode.
6. Validate paper-trading with costs and risk limits.
7. Treat live trading as a separate release requiring explicit human approval.

No broker URL, package, credential, or endpoint in this document is asserted to be valid. Do not put secrets in source control.
