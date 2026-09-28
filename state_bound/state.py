from dataclasses import dataclass, field
from typing import Any
import hashlib
import json

def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()

@dataclass
class WorldState:
    context: dict[str, Any] = field(default_factory=dict)
    state: dict[str, Any] = field(default_factory=dict)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    trajectory: dict[str, Any] = field(default_factory=dict)
    policy: dict[str, Any] = field(default_factory=dict)
    environment: dict[str, Any] = field(default_factory=dict)
    source: str = "test-fixture"
    observed_at: int = 1_000
    freshness_bound_seconds: int = 0

    def fingerprint(self) -> dict[str, str]:
        return {k: digest(getattr(self, k)) for k in ("context","state","evidence","trajectory","policy","environment")}

    def clone(self):
        return WorldState(
            context=json.loads(canonical(self.context)),
            state=json.loads(canonical(self.state)),
            evidence=json.loads(canonical(self.evidence)),
            trajectory=json.loads(canonical(self.trajectory)),
            policy=json.loads(canonical(self.policy)),
            environment=json.loads(canonical(self.environment)),
            source=self.source,
            observed_at=self.observed_at,
            freshness_bound_seconds=self.freshness_bound_seconds,
        )

    def freshness_valid(self, now: int) -> bool:
        return now - self.observed_at <= self.freshness_bound_seconds

@dataclass(frozen=True)
class InvariantReport:
    action: bool
    context: bool
    state: bool
    evidence: bool
    trajectory: bool
    policy: bool
    environment: bool

    @property
    def valid(self):
        return all(vars(self).values())

    def failed(self):
        return [name for name, ok in vars(self).items() if not ok]
