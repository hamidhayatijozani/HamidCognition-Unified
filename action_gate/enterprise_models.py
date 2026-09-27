from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import asdict, dataclass
from typing import Any, Mapping


def canonical(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


class EnterpriseArchitectureError(ValueError):
    pass


@dataclass(frozen=True)
class DecisionContext:
    request_id: str
    tenant_id: str
    actor_id: str
    session_id: str
    agent_id: str
    action: str
    tool_id: str
    target: str | None
    parameters_digest: str
    policy_id: str
    policy_version: str
    policy_digest: str
    risk_level: str
    execution_profile_id: str
    created_at: str
    expires_at: str
    context_digest: str
    signature: str

    def unsigned(self) -> dict[str, Any]:
        value = asdict(self)
        value.pop("signature")
        return value

    def verify(self, secret: str) -> None:
        expected = hmac.new(secret.encode(), canonical(self.unsigned()).encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, self.signature):
            raise EnterpriseArchitectureError("decision_context_signature_invalid")


@dataclass(frozen=True)
class ExecutionProfile:
    profile_id: str
    risk_level: str
    latency_budget_ms: int
    evidence_level: str
    replay_required: bool
    human_review_required: bool = False

    def requires_full_evidence(self) -> bool:
        return self.evidence_level.lower() == "full"


@dataclass(frozen=True)
class AuthorityBinding:
    authority_id: str
    decision_id: str
    tenant_id: str
    agent_id: str
    policy_id: str
    policy_digest: str
    tool_id: str
    action_digest: str
    nonce: str


@dataclass(frozen=True)
class EnforcementResult:
    permitted: bool
    reason: str
    profile_id: str
    graph_path: tuple[str, ...] = ()
    checks: tuple[str, ...] = ()
