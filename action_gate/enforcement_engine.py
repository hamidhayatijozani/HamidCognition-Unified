from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from enterprise_models import AuthorityBinding, DecisionContext, EnterpriseArchitectureError, EnforcementResult, ExecutionProfile
from policy_graph import PolicyGraph


class EnforcementEngine:
    """Fail-closed, stateless authorization decision at the protected boundary."""

    def __init__(self, *, graph: PolicyGraph, context_secret: str, nonce_claim: Callable[[str], bool]) -> None:
        self._graph = graph
        self._context_secret = context_secret
        self._nonce_claim = nonce_claim

    def authorize(self, *, context: DecisionContext, authority: AuthorityBinding,
                  profile: ExecutionProfile, evidence_complete: bool,
                  replay_available: bool, human_review: bool,
                  now: datetime | None = None) -> EnforcementResult:
        try:
            context.verify(self._context_secret)
            current = now or datetime.now(timezone.utc)
            if current >= datetime.fromisoformat(context.expires_at.replace("Z", "+00:00")):
                raise EnterpriseArchitectureError("decision_context_expired")
            if authority.tenant_id != context.tenant_id:
                raise EnterpriseArchitectureError("tenant_binding_mismatch")
            if authority.agent_id != context.agent_id:
                raise EnterpriseArchitectureError("agent_binding_mismatch")
            if authority.policy_id != context.policy_id or authority.policy_digest != context.policy_digest:
                raise EnterpriseArchitectureError("policy_binding_mismatch")
            if authority.tool_id != context.tool_id:
                raise EnterpriseArchitectureError("tool_binding_mismatch")
            if profile.profile_id != context.execution_profile_id:
                raise EnterpriseArchitectureError("execution_profile_mismatch")
            graph_path = self._graph.validate(tenant_id=context.tenant_id, agent_id=context.agent_id,
                                               policy_id=context.policy_id, tool_id=context.tool_id,
                                               authority_id=authority.authority_id)
            if profile.requires_full_evidence() and not evidence_complete:
                raise EnterpriseArchitectureError("execution_profile_requires_full_evidence")
            if profile.replay_required and not replay_available:
                raise EnterpriseArchitectureError("execution_profile_requires_replay")
            if profile.human_review_required and not human_review:
                raise EnterpriseArchitectureError("execution_profile_requires_human_review")
            if not self._nonce_claim(authority.nonce):
                raise EnterpriseArchitectureError("nonce_reuse")
            return EnforcementResult(True, "authorized", profile.profile_id, graph_path,
                                     ("context_signature", "tenant_binding", "agent_binding",
                                      "policy_binding", "tool_binding", "policy_graph_path",
                                      "execution_profile", "nonce_single_use"))
        except EnterpriseArchitectureError as exc:
            return EnforcementResult(False, str(exc), profile.profile_id)
