from state_bound.chemical_reactivity import ReactivityFactors, calculate_reactivity


def test_stable_high_activation_proceeds():
    result = calculate_reactivity(
        ReactivityFactors(0.95, 0.05, 1.0, 1.0, 1.0, 1.0)
    )
    assert result.mode == "PROCEED"
    assert result.reactivity >= 0.70


def test_inhibitor_overrides_high_activation():
    result = calculate_reactivity(
        ReactivityFactors(1.0, 0.90, 1.0, 1.0, 1.0, 1.0)
    )
    assert result.mode == "INHIBIT"


def test_state_drift_causes_hold():
    result = calculate_reactivity(
        ReactivityFactors(0.95, 0.05, 1.0, 0.20, 1.0, 1.0)
    )
    assert result.mode == "HOLD"


def test_weak_evidence_does_not_create_authority():
    result = calculate_reactivity(
        ReactivityFactors(1.0, 0.0, 1.0, 1.0, 0.20, 1.0)
    )
    assert result.mode in {"HOLD", "UNKNOWN"}


def test_reactivity_is_deterministic():
    factors = ReactivityFactors(0.8, 0.1, 0.9, 0.95, 0.9, 0.92)
    assert calculate_reactivity(factors) == calculate_reactivity(factors)


def test_hold_and_unknown_have_explicit_consumers():
    hold = calculate_reactivity(
        ReactivityFactors(0.9, 0.0, 1.0, 0.2, 1.0, 1.0)
    )
    unknown = calculate_reactivity(
        ReactivityFactors(0.4, 0.0, 1.0, 1.0, 1.0, 1.0)
    )
    assert hold.mode == "HOLD"
    assert hold.consumer_action == "REQUIRE_REEVALUATION"
    assert unknown.mode == "UNKNOWN"
    assert unknown.consumer_action == "REQUIRE_EVIDENCE"


def test_runtime_numeric_contract_rejects_boolean_values():
    try:
        ReactivityFactors(True, 0.0, 1.0, 1.0, 1.0, 1.0)
    except TypeError:
        return
    raise AssertionError("boolean activation must not satisfy the numeric contract")
