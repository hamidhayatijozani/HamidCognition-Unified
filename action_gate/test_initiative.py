from initiative import InitiativeMode, InitiativeRequest, propose


def test_builds_new_route_from_blocker():
    result = propose(InitiativeRequest(
        goal="restore service",
        state={"blockers": ["database unavailable"]},
        evidence=({"source": "health-check", "verified": True},),
    ))
    assert result.status == "PROPOSED"
    assert result.candidates[0].mode is InitiativeMode.REPAIR
    assert "database unavailable" in result.candidates[0].action


def test_missing_evidence_creates_verification_path():
    result = propose(InitiativeRequest(
        goal="verify release",
        state={"missing_evidence": ["post-merge CI"]},
    ))
    assert result.candidates[0].mode is InitiativeMode.VERIFY
    assert result.candidates[0].action.startswith("collect_evidence:")


def test_contradiction_creates_discriminating_test():
    result = propose(InitiativeRequest(
        goal="resolve behavior",
        state={"contradictions": ["result differs from baseline"]},
    ))
    assert result.candidates[0].mode is InitiativeMode.EXPLORE


def test_unknown_is_explored_not_reclassified_as_failure():
    result = propose(InitiativeRequest(
        goal="understand system",
        state={"unknowns": ["unexplained transition"]},
    ))
    assert result.candidates[0].mode is InitiativeMode.EXPLORE


def test_exact_prior_fingerprint_is_rejected():
    first = propose(InitiativeRequest(
        goal="restore service",
        state={"blockers": ["database unavailable"]},
    ))
    prior = ({"fingerprint": first.candidates[0].fingerprint},)
    second = propose(InitiativeRequest(
        goal="restore service",
        state={"blockers": ["database unavailable"]},
        prior_actions=prior,
    ))
    assert second.status == "PROPOSED"
    assert second.candidates[0].mode is InitiativeMode.VERIFY


def test_semantic_originality_is_not_claimed():
    result = propose(InitiativeRequest(goal="do something"))
    assert "semantic_novelty_not_proven" in result.reasoning_trace


def test_external_execution_remains_gate_bound():
    result = propose(InitiativeRequest(
        goal="change production",
        state={"alternate_path": "modify_production_config"},
        allow_external_side_effect=True,
    ))
    assert result.candidates
    assert "execution_authority:action_gate" in result.reasoning_trace
