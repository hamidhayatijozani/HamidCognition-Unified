import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from idea_to_sale import build_plan, ready_for_sale

def test_missing_evidence_blocks_sale():
    p=build_plan("AI gateway", customer_problem="unsafe tools", target_buyer="AI team", product_boundary="pre-execution gate")
    assert not ready_for_sale(p)
    assert p.next_action=="RESOLVE:evidence"

def test_complete_plan_reaches_human_approval():
    p=build_plan("AI gateway", customer_problem="unsafe tools", target_buyer="AI team", product_boundary="pre-execution gate", evidence=["same-SHA CI"], sales_assets=["one-pager"], validation_verified=True, pricing_defined=True, payment_path_configured=True)
    assert ready_for_sale(p)
    assert p.next_action=="HUMAN_APPROVAL"

def test_pricing_does_not_equal_payment():
    p=build_plan("X", customer_problem="Y", target_buyer="Z", product_boundary="B", evidence=["E"], sales_assets=["S"], validation_verified=True, pricing_defined=True, payment_path_configured=False)
    assert not ready_for_sale(p)