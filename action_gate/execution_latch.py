"""Final pre-execution latch for HamidCognition Action Gate.

The latch is the narrowest executable boundary: no valid decision, no execution.
It produces an execution authorization record that an executor can consume once.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Mapping

try:
    from .validation_boundary import validate_execution_attempt
except ImportError:
    from validation_boundary import validate_execution_attempt


@dataclass(frozen=True)
class ExecutionAuthorization:
    permitted: bool
    reason: str
    request_digest: str
    decision_id: str
    nonce: str
    boundary_version: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def authorize_execution(
    request: Mapping[str, Any],
    decision: Mapping[str, Any],
    *,
    now: datetime | None = None,
) -> ExecutionAuthorization:
    result = validate_execution_attempt(request, decision, now=now)
    if not result.valid:
        return ExecutionAuthorization(
            False,
            ";".join(result.errors),
            "",
            str(decision.get("decision_id", "")),
            "",
            result.boundary_version,
        )
    return ExecutionAuthorization(
        True,
        "validated_execution_latch",
        decision["request_digest"],
        decision["decision_id"],
        decision.get("nonce", ""),
        result.boundary_version,
    )
