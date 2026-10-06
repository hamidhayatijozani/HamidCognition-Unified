from RESEARCH.algorithm_orchestrator import run_all_executable_algorithms


def test_all_executable_research_algorithms_are_called():
    result = run_all_executable_algorithms()
    assert result["status"] == "RESEARCH_ONLY"
    assert all(value in {"EXECUTED", "VALIDATED"} for value in result["algorithms"].values())
    assert result["market_lab"]["experiment"] == "MAAT-THOTH-PAPER-001"
    assert result["pre_execution"]["mode"] in {"PROCEED", "HOLD", "INHIBIT", "UNKNOWN"}
    assert len(result["shock_recovery"]) == 5
    assert result["contradiction_ledger"]["valid"] is True
