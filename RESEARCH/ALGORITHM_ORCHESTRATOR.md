# Research Algorithm Orchestrator

This harness calls the currently executable deterministic research algorithms that can safely share the frozen synthetic market fixture and explicit condition inputs:

- MAAT: multi-source consensus and provenance fingerprinting.
- Thoth: bounded-window momentum/volatility signal.
- Paper Trader: fee/slippage-aware simulated execution.
- Pre-execution Reactivity: bounded condition signal.
- Shock Recovery: deterministic recovery-state transition.
- Contradiction Ledger: validation of research contradictions.

The orchestrator does not merge these signals into execution authority. Action Gate remains the only execution boundary.

Algorithms that require external data, live providers, or unresolved protocol evidence remain explicitly unexecuted rather than being fed invented data. That distinction is intentional: a fake execution is not evidence merely because a human put a green checkmark beside it.

Run:

    python -m RESEARCH.algorithm_orchestrator

The result is research evidence only. It does not establish predictive skill, profitability, live-market safety, external-provider integrity, or execution authority.
