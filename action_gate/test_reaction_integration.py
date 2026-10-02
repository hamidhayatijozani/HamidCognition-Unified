from action_gate.app import ActionRequest, evaluate_reaction_policy


def _request(**overrides):
    data = {
        "tenant_id": "t1",
        "agent_id": "agent1",
        "actor_id": "actor1",
        "session_id": "session1",
        "action": "read",
        "context": {"activation": 1.0, "inhibition": 0.9, "catalyst": 0.0, "state": {"valid": True}},
        "evidence": [{"verified": True, "source": "fixture"}],
    }
    data.update(overrides)
    return ActionRequest(**data)


def test_inhibit_is_binding_without_override():
    assessment, decision, checks = evaluate_reaction_policy(_request())
    assert assessment.network.mode == "INHIBIT"
    assert decision == "DENY"
    assert checks[0]["policy"] == "chemical-reaction-inhibitor"
    assert checks[0]["result"] == "DENY"


def test_inhibit_override_requires_reason_and_is_audited():
    assessment, decision, checks = evaluate_reaction_policy(
        _request(reaction_override=True, reaction_override_reason="documented emergency override")
    )
    assert assessment.network.mode == "INHIBIT"
    assert decision is None
    assert checks[0]["result"] == "OVERRIDE"
    assert checks[0]["reason"] == "documented emergency override"
