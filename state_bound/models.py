from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Literal
import hashlib, json

EpistemicState = Literal["KNOWN","UNKNOWN","CONFLICTED","STALE","UNVERIFIED"]
DecisionState = Literal["ALLOW","DENY","ASK","HOLD","SANDBOX","DEFER"]

def digest(value: Any) -> str:
    payload=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

@dataclass(frozen=True)
class WorldState:
    context: dict[str,Any]
    state: dict[str,Any]
    evidence: list[dict[str,Any]]
    trajectory: dict[str,Any]
    environment: dict[str,Any]
    policy: dict[str,Any]
    source: str = "test-fixture"
    observed_at_ns: int = 0
    freshness_bound_ns: int = 0

    def fingerprint(self) -> dict[str,str]:
        return {
            "context":digest(self.context),
            "state":digest(self.state),
            "evidence":digest(self.evidence),
            "trajectory":digest(self.trajectory),
            "environment":digest(self.environment),
            "policy":digest(self.policy),
        }

    def freshness_valid(self, now_ns: int) -> bool:
        return self.freshness_bound_ns <= 0 or now_ns - self.observed_at_ns <= self.freshness_bound_ns

@dataclass(frozen=True)
class Decision:
    decision: DecisionState
    epistemic_state: EpistemicState
    world_version: int = 1
    trajectory_digest: str = ""
    reason: str = ""

@dataclass(frozen=True)
class ExecutionAuthority:
    action: dict[str,Any]
    subject: str
    decision: Decision
    authorized_world: dict[str,str]
    issued_at_ns: int
    expires_at_ns: int
    nonce: str
    sequence: int = 1
    constraints: dict[str,Any] = field(default_factory=dict)

    @property
    def executable(self) -> bool:
        return self.decision.decision=="ALLOW" and self.decision.epistemic_state=="KNOWN"
