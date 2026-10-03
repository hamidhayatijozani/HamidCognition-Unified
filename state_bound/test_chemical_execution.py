from state_bound.chemical_execution import ReactionEnvironment, build_reaction_assessment


def test_reaction_environment_is_replayable():
    env = ReactionEnvironment(
        context={"valid": True},
        state={"valid": True},
        evidence=({"source": "test", "verified": True},),
        trajectory=({"action": "observe"},),
        activation=0.95,
        inhibition=0.0,
        catalyst=0.2,
    )
    assert build_reaction_assessment(env) == build_reaction_assessment(env)


def test_state_drift_becomes_hold_or_unknown():
    env = ReactionEnvironment(
        context={"valid": True},
        state={"valid": False, "drift": True},
        evidence=({"source": "test", "verified": True},),
        trajectory=({"action": "observe"},),
        activation=1.0,
        inhibition=0.0,
    )
    result = build_reaction_assessment(env)
    assert result.network.mode in {"HOLD", "UNKNOWN"}
    assert result.state_transition_required


def test_missing_evidence_cannot_proceed():
    env = ReactionEnvironment(
        context={"valid": True},
        state={"valid": True},
        evidence=(),
        trajectory=({"action": "observe"},),
        activation=1.0,
        inhibition=0.0,
    )
    result = build_reaction_assessment(env)
    assert result.network.mode in {"HOLD", "UNKNOWN"}
    assert result.network.barrier >= 1.0


def test_inhibitor_is_preserved_as_architectural_block():
    env = ReactionEnvironment(
        context={"valid": True},
        state={"valid": True},
        evidence=({"source": "test", "verified": True},),
        trajectory=({"action": "observe"},),
        activation=1.0,
        inhibition=0.9,
    )
    result = build_reaction_assessment(env)
    assert result.network.mode == "INHIBIT"
    assert result.network.weakest_node in {
        "context_activation",
        "state_transition",
        "trajectory_continuation",
    }
