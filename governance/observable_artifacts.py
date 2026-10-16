"""Validated, serializable records for governance decisions."""
from dataclasses import asdict, dataclass
from datetime import datetime
import math
from typing import Any


@dataclass
class ObservableArtifact:
    trace_id: str
    agent_id: str
    timestamp: str
    claims: list[dict[str, Any]]
    evidence: list[dict[str, Any]]
    tool_events: list[dict[str, Any]]
    confidence: float
    decision_object: dict[str, Any]
    execution_result: dict[str, Any]

    def validate(self) -> bool:
        if not all(isinstance(v, str) and v.strip() for v in
                   (self.trace_id, self.agent_id, self.timestamp)):
            return False
        try:
            datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
        except (TypeError, ValueError):
            return False
        if not isinstance(self.confidence, (int, float)) or not math.isfinite(self.confidence):
            return False
        if not 0.0 <= self.confidence <= 1.0:
            return False
        if not all(isinstance(v, list) for v in (self.claims, self.evidence, self.tool_events)):
            return False
        if not all(isinstance(x, dict) for x in self.claims + self.evidence + self.tool_events):
            return False
        return isinstance(self.decision_object, dict) and isinstance(self.execution_result, dict)

    def to_dict(self) -> dict[str, Any]:
        if not self.validate():
            raise ValueError("invalid observable artifact")
        return asdict(self)
