from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .market_lab.experiment import run_snapshot_experiment
from .market_lab.maat import PriceObservation
from state_bound.pre_execution_signals import ReactivityFactors, calculate_reactivity
from .SHOCK_RECOVERY.shock_recovery import RecoveryEngine
from .CONTRADICTION_LEDGER import ContradictionLedger


ROOT = Path(__file__).resolve().parent
FIXTURE = ROOT / "fixtures" / "maat_thoth_snapshot.json"


def run_all_executable_algorithms() -> dict:
    """Run the executable research algorithms on one frozen, synthetic input.

    This is an orchestration/evidence harness, not a claim that the algorithms
    predict markets or authorize execution. Each algorithm keeps its own
    semantic boundary and the combined result is explicitly research-only.
    """

    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    observations = [PriceObservation(**row) for row in fixture["observations"]]
    market = run_snapshot_experiment(observations, fixture["symbol"])

    factors = ReactivityFactors(
        activation=0.82,
        inhibition=0.10,
        context_stability=0.92,
        state_stability=0.91,
        evidence_strength=0.88,
        trajectory_stability=0.90,
    )
    pre_execution = asdict(calculate_reactivity(factors))

    recovery = RecoveryEngine()
    recovery_trace = [recovery.step(d) for d in (0.0, 0.8, 1.4, 0.7, 0.2)]

    ledger = ContradictionLedger()
    ledger_valid, ledger_errors = ledger.validate()

    return {
        "harness": "HHJ-RESEARCH-ALGORITHM-ORCHESTRATOR-001",
        "status": "RESEARCH_ONLY",
        "fixture": fixture["fixture_status"],
        "algorithms": {
            "MAAT": "EXECUTED",
            "THOTH": "EXECUTED",
            "PAPER_TRADER": "EXECUTED",
            "PRE_EXECUTION_REACTIVITY": "EXECUTED",
            "SHOCK_RECOVERY": "EXECUTED",
            "CONTRADICTION_LEDGER": "VALIDATED",
        },
        "market_lab": market,
        "pre_execution": pre_execution,
        "shock_recovery": recovery_trace,
        "contradiction_ledger": {
            "valid": ledger_valid,
            "errors": ledger_errors,
        },
        "claims_not_established": [
            "live_market_predictive_skill",
            "profitability",
            "external_provider_integrity",
            "live_trading_safety",
            "execution_authority_from_research_signals",
        ],
    }


def main() -> None:
    result = run_all_executable_algorithms()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
