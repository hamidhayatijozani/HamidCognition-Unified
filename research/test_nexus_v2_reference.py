from nexus_v2_reference import SCALE, NexusReferenceEngine, ShadowAdaptiveWeights


def test_reference_engine_is_deterministic():
    engine = NexusReferenceEngine()
    kwargs = dict(
        base_risk=4000,
        confidence=9000,
        evidence=7000,
        stabilization=9000,
        params={"command": "echo", "args": ["hello"]},
        tool_class="standard",
    )
    assert engine.evaluate(**kwargs) == engine.evaluate(**kwargs)


def test_parameter_hash_binds_canonical_structure():
    engine = NexusReferenceEngine()
    a = engine.evaluate(
        base_risk=1000,
        confidence=9000,
        evidence=9000,
        stabilization=10000,
        params={"b": 2, "a": 1},
        tool_class="standard",
    )
    b = engine.evaluate(
        base_risk=1000,
        confidence=9000,
        evidence=9000,
        stabilization=10000,
        params={"a": 1, "b": 3},
        tool_class="standard",
    )
    assert a.params_hash != b.params_hash


def test_high_risk_tool_class_is_explicit():
    engine = NexusReferenceEngine()
    heal = engine.evaluate(
        base_risk=9000,
        confidence=9000,
        evidence=9000,
        stabilization=10000,
        params={},
        tool_class="exec_command",
    )
    deny = engine.evaluate(
        base_risk=9000,
        confidence=9000,
        evidence=9000,
        stabilization=10000,
        params={},
        tool_class="standard",
    )
    assert heal.verdict == "HEAL"
    assert deny.verdict == "DENY"


def test_shadow_learning_does_not_change_active_engine_weights():
    engine = NexusReferenceEngine()
    learner = ShadowAdaptiveWeights()
    old = (engine.w_gap, engine.w_instability)
    proposed = learner.propose(9000, 9000, anomaly=True)
    assert (engine.w_gap, engine.w_instability) == old
    assert sum(proposed) in {9999, 10000, 10001}
