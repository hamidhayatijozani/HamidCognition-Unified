import pytest
from governance.epistemic_evaluation import HAISCalculator
from governance.decision_risk import DecisionRiskScore
from governance.governance_engine import GovernanceDecisionEngine


def test_hais_formula_and_classification():
    calc = HAISCalculator()
    assert calc.calculate(1, 0, 1, 1, 0) == 1.0
    assert calc.classify(0.85) == "TRUSTED"
    assert calc.classify(0.65) == "REVIEW_REQUIRED"
    assert calc.classify(0.64) == "UNSAFE"


def test_hais_rejects_out_of_range():
    with pytest.raises(ValueError):
        HAISCalculator().calculate(1.1, 0, 0, 0, 0)


def test_risk_increases_with_irreversibility():
    low = DecisionRiskScore(0.2, 0.2, 0.0, 0.2).calculate()
    high = DecisionRiskScore(0.2, 0.2, 1.0, 0.2).calculate()
    assert high > low


def test_invalid_score_fails_closed():
    result = GovernanceDecisionEngine().decide(float("nan"), 0.1)
    assert result.action == "DENY"
