from __future__ import annotations

from datetime import datetime, timedelta, timezone

from decision_context_service import DecisionContextService
from enterprise_models import AuthorityBinding
from evidence_ledger import EvidenceLedger
from execution_profile import ExecutionProfileService
from policy_graph import PolicyGraph
from enforcement_engine import EnforcementEngine
from post_execution_forensics import PostExecutionForensics


SECRET = "enterprise-test-secret"


def make_context(risk="LOW", profile="low"):
    now = datetime.now(timezone.utc)
    return DecisionContextService(SECRET).build(
        request_id="req-1",
        tenant_id="tenant-a",
        actor_id="actor-a",
        session_id="session-a",
        agent_id="agent-a",
        action="read_public_file",
        tool_id="mcp-server-a",
        target="/public/info.txt",
        parameters={"target": "/public/info.txt"},
        policy_id="policy-read",
        policy_version="v1",
        policy_digest="policy-digest-a",
        risk_level=risk,
        execution_profile_id=profile,
        created_at=now.isoformat(),
        expires_at=(now + timedelta(minutes=5)).isoformat(),
    )


def make_graph(authority_id="auth-1"):
    return PolicyGraph.from_edges([
        ("tenant:tenant-a", "governs", "policy:policy-read"),
        ("agent:agent-a", "uses", "policy:policy-read"),
        ("policy:policy-read", "binds", "tool:mcp-server-a"),
        ("policy:policy-read", "issues", f"authority:{authority_id}"),
    ])


def make_authority(authority_id="auth-1", policy_digest="policy-digest-a"):
    return AuthorityBinding(
        authority_id=authority_id,
        decision_id="dec-1",
        tenant_id="tenant-a",
        agent_id="agent-a",
        policy_id="policy-read",
        policy_digest=policy_digest,
        tool_id="mcp-server-a",
        action_digest="action-digest-a",
        nonce="nonce-1",
    )


def test_full_enterprise_path_authorizes():
    claimed = set()
    engine = EnforcementEngine(graph=make_graph(), context_secret=SECRET,
                               nonce_claim=lambda n: not (n in claimed or claimed.add(n)))
    result = engine.authorize(
        context=make_context(),
        authority=make_authority(),
        profile=ExecutionProfileService().get("LOW"),
        evidence_complete=True,
        replay_available=True,
        human_review=False,
    )
    assert result.permitted is True
    assert "policy_graph_path" in result.checks


def test_policy_graph_cut_fails_closed():
    broken = PolicyGraph.from_edges([
        ("tenant:tenant-a", "governs", "policy:policy-read"),
        ("agent:agent-a", "uses", "policy:policy-read"),
        ("policy:policy-read", "issues", "authority:auth-1"),
    ])
    engine = EnforcementEngine(graph=broken, context_secret=SECRET, nonce_claim=lambda n: True)
    result = engine.authorize(
        context=make_context(),
        authority=make_authority(),
        profile=ExecutionProfileService().get("LOW"),
        evidence_complete=True,
        replay_available=True,
        human_review=False,
    )
    assert result.permitted is False
    assert result.reason == "policy_tool_edge_missing"


def test_policy_binding_mismatch_fails_closed():
    engine = EnforcementEngine(graph=make_graph(), context_secret=SECRET, nonce_claim=lambda n: True)
    result = engine.authorize(
        context=make_context(),
        authority=make_authority(policy_digest="different"),
        profile=ExecutionProfileService().get("LOW"),
        evidence_complete=True,
        replay_available=True,
        human_review=False,
    )
    assert result.permitted is False
    assert result.reason == "policy_binding_mismatch"


def test_high_risk_requires_full_evidence_and_replay():
    engine = EnforcementEngine(graph=make_graph(), context_secret=SECRET, nonce_claim=lambda n: True)
    result = engine.authorize(
        context=make_context("HIGH", "high"),
        authority=make_authority(),
        profile=ExecutionProfileService().get("HIGH"),
        evidence_complete=False,
        replay_available=False,
        human_review=False,
    )
    assert result.permitted is False
    assert result.reason == "execution_profile_requires_full_evidence"


def test_ledger_is_hash_chained_and_append_only():
    ledger = EvidenceLedger()
    ledger.append("e1", "DECISION", "trace-1", {"policy_id": "p"})
    ledger.append("e2", "EXECUTION", "trace-1", {"action": "read", "policy_id": "p", "authority_id": "a"})
    assert ledger.verify_chain()
    try:
        ledger.delete("e1")
    except PermissionError:
        pass
    else:
        raise AssertionError("ledger delete unexpectedly succeeded")


def test_forensics_detects_repetition_and_authority_churn():
    ledger = EvidenceLedger()
    for i in range(3):
        ledger.append(f"e{i}", "EXECUTION", "trace-1",
                      {"action": "delete_file", "policy_id": "p", "authority_id": f"a{i}"})
    types = {s.signal_type for s in PostExecutionForensics().analyze(ledger.events())}
    assert "repeated_action_pattern" in types
    assert "authority_churn" in types


def test_critical_profile_requires_human_review():
    engine = EnforcementEngine(graph=make_graph(), context_secret=SECRET, nonce_claim=lambda n: True)
    result = engine.authorize(
        context=make_context("CRITICAL", "critical"),
        authority=make_authority(),
        profile=ExecutionProfileService().get("CRITICAL"),
        evidence_complete=True,
        replay_available=True,
        human_review=False,
    )
    assert result.permitted is False
    assert result.reason == "execution_profile_requires_human_review"


def test_nonce_is_single_use():
    claimed = set()
    engine = EnforcementEngine(graph=make_graph(), context_secret=SECRET,
                               nonce_claim=lambda n: not (n in claimed or claimed.add(n)))
    kwargs = dict(context=make_context(), authority=make_authority(),
                  profile=ExecutionProfileService().get("LOW"),
                  evidence_complete=True, replay_available=True, human_review=False)
    assert engine.authorize(**kwargs).permitted is True
    assert engine.authorize(**kwargs).reason == "nonce_reuse"
