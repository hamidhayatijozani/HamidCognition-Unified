from self_audit import Evidence, GateDecision, SelfAuditRequest, audit


def ev(source, supports=()):
    return Evidence(source=source, verified=True, supports=tuple(supports))


def test_self_audit_allows_verified_factual_status():
    result = audit(SelfAuditRequest(
        actor_id="assistant",
        session_id="current-session",
        action="report_release_status",
        claim="release version verified",
        evidence=(ev("VERSION file", ("release", "version", "verified")),),
    ))
    assert result.decision is GateDecision.ALLOW
    assert result.executable is True
    assert result.evidence_coverage == 1.0
    assert result.claim_evidence_gap == 0.0


def test_self_audit_denies_unobservable_model_internal_claim():
    result = audit(SelfAuditRequest(
        actor_id="assistant",
        session_id="current-session",
        action="assert_model_internal_installation",
        claim="Action Gate is installed in model weights",
        evidence=(ev("conversation", ("action",)),),
        requires_model_internal_access=True,
    ))
    assert result.decision is GateDecision.DENY
    assert result.executable is False
    assert "model_internal_state_not_observable" in result.reasons


def test_self_audit_asks_before_external_side_effect():
    result = audit(SelfAuditRequest(
        actor_id="assistant",
        session_id="current-session",
        action="modify_repository",
        target="github repository",
        evidence=(ev("explicit user instruction", ("modify", "repository")),),
        external_side_effect=True,
        mutating=True,
    ))
    assert result.decision is GateDecision.ASK
    assert result.executable is False


def test_self_audit_defers_unverified_claim():
    result = audit(SelfAuditRequest(
        actor_id="assistant",
        session_id="current-session",
        action="report_post_merge_ci",
        claim="post-merge CI passed",
        evidence=(),
    ))
    assert result.decision is GateDecision.DEFER
    assert result.executable is False


def test_self_audit_denies_missing_identity_binding():
    result = audit(SelfAuditRequest(
        actor_id="",
        session_id="current-session",
        action="report_status",
        evidence=(ev("verified source"),),
    ))
    assert result.decision is GateDecision.DENY
    assert result.reasons == ("actor_identity_missing",)


def test_self_audit_is_deterministic_for_same_input():
    request = SelfAuditRequest(
        actor_id="assistant",
        session_id="current-session",
        action="report_release_status",
        evidence=(ev("VERSION file", ("version",)),),
    )
    assert audit(request) == audit(request)
