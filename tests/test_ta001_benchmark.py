from state_bound.benchmark import assert_ta001_contract, run_ta001


def test_ta001_benchmark_is_self_validating():
    """The validation process is itself a TA-001 execution test."""
    result = run_ta001(iterations=1000)
    assert_ta001_contract(result)
