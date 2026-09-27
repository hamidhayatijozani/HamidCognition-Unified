from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timezone
from typing import Any, Mapping

from enterprise_models import DecisionContext, EnterpriseArchitectureError, canonical, digest


class DecisionContextService:
    """Build and sign an immutable execution context."""

    def __init__(self, signing_secret: str) -> None:
        if not signing_secret:
            raise EnterpriseArchitectureError("decision_context_signing_secret_required")
        self._secret = signing_secret

    def build(self, *, request_id: str, tenant_id: str, actor_id: str, session_id: str,
              agent_id: str, action: str, tool_id: str, target: str | None,
              parameters: Mapping[str, Any], policy_id: str, policy_version: str,
              policy_digest: str, risk_level: str, execution_profile_id: str,
              created_at: str, expires_at: str) -> DecisionContext:
        if not all((tenant_id, actor_id, session_id, agent_id, action, tool_id,
                    policy_id, policy_version, policy_digest)):
            raise EnterpriseArchitectureError("decision_context_identity_or_binding_missing")
        payload = {
            "request_id": request_id, "tenant_id": tenant_id, "actor_id": actor_id,
            "session_id": session_id, "agent_id": agent_id, "action": action.lower(),
            "tool_id": tool_id, "target": target, "parameters_digest": digest(dict(parameters)),
            "policy_id": policy_id, "policy_version": policy_version, "policy_digest": policy_digest,
            "risk_level": risk_level, "execution_profile_id": execution_profile_id,
            "created_at": created_at, "expires_at": expires_at,
        }
        context_digest = digest(payload)
        signature = hmac.new(self._secret.encode(),
                             canonical({**payload, "context_digest": context_digest}).encode(),
                             hashlib.sha256).hexdigest()
        return DecisionContext(**payload, context_digest=context_digest, signature=signature)

    @staticmethod
    def verify_time(context: DecisionContext, now: datetime | None = None) -> None:
        current = now or datetime.now(timezone.utc)
        created = datetime.fromisoformat(context.created_at.replace("Z", "+00:00"))
        expires = datetime.fromisoformat(context.expires_at.replace("Z", "+00:00"))
        if current < created:
            raise EnterpriseArchitectureError("decision_context_not_yet_valid")
        if current >= expires:
            raise EnterpriseArchitectureError("decision_context_expired")

    def verify(self, context: DecisionContext) -> None:
        context.verify(self._secret)
        self.verify_time(context)
