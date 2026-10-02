from state_bound.reaction_capability import ReactionAssessmentRequest, assess_reaction, assessment_record
from state_bound.chemical_execution import ReactionEnvironment


def test_capability_boundary_is_pure_and_replayable():
    env = ReactionEnvironment(
        context={"valid": True},
        state={"valid": True},
        evidence=({"source": "fixture", "verified": True},),
        trajectory=({"action": "observe"},),
        activation=0.9,
        inhibition=0.0,
        catalyst=0.1,
    )
    request = ReactionAssessmentRequest(env)
    first = assessment_record(assess_reaction(request))
    second = assessment_record(assess_reaction(request))
    assert first == second
    assert first["mode"] in {"PROCEED", "HOLD", "INHIBIT", "UNKNOWN"}


def test_reaction_layer_has_no_execution_authority():
    import state_bound.reaction_capability as capability
    assert not hasattr(capability, "execute")
    assert not hasattr(capability, "reserve")
    assert not hasattr(capability, "approve")
