"""HamidCognition Action Gate Validation Boundary.

The boundary is deliberately narrower than authorization. It validates whether a
request and a decision are structurally bound, fresh, and internally coherent.
It never turns a claim into truth and never executes an action.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Mapping

DECISIONS = frozenset({"ALLOW", "DENY", "ASK", "SANDBOX", "DEFER"})
EXECUTABLE_DECISIONS = frozenset({"ALLOW", "SANDBOX"})
EVIDENCE_STATES = frozenset({"PRESENT", "MISSING", "INVALID", "STALE", "CONFLICTING"})


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _parse_time(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("timestamp must be an ISO-8601 string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: tuple[str, ...]
    boundary_version: str = "VB-0.1"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self) | {"errors": list(self.errors)}


def validate_request(request: Mapping[str, Any]) -> ValidationResult:
    errors: list[str] = []
    required = ("request_id", "action", "target", "parameters", "requester", "timestamp")
    for key in required:
        if key not in request:
            errors.append(f"missing:{key}")
    if errors:
        return ValidationResult(False, tuple(errors))

    for key in ("request_id", "action", "target", "requester"):
        if not isinstance(request[key], str) or not request[key].strip():
            errors.append(f"invalid:{key}")
    if not isinstance(request["parameters"], Mapping):
        errors.append("invalid:parameters")
    try:
        _parse_time(request["timestamp"])
    except (TypeError, ValueError) as exc:
        errors.append(f"invalid:timestamp:{exc}")

    return ValidationResult(not errors, tuple(errors))


def validate_evidence(evidence: Mapping[str, Any] | None) -> ValidationResult:
    if evidence is None:
        return ValidationResult(False, ("evidence:missing",))
    state = evidence.get("state")
    errors: list[str] = []
    if state not in EVIDENCE_STATES:
        errors.append("evidence:invalid_state")
    if state == "PRESENT":
        if not evidence.get("artifact_ref"):
            errors.append("evidence:present_without_artifact_ref")
        if not evidence.get("sha256"):
            errors.append("evidence:present_without_sha256")
    return ValidationResult(not errors, tuple(errors))


def validate_decision(
    request: Mapping[str, Any],
    decision: Mapping[str, Any],
    *,
    now: datetime | None = None,
    max_age_seconds: int = 300,
) -> ValidationResult:
    errors: list[str] = []
    request_result = validate_request(request)
    errors.extend(f"request:{e}" for e in request_result.errors)

    required = ("decision_id", "request_digest", "decision", "issued_at", "boundary_version")
    for key in required:
        if key not in decision:
            errors.append(f"missing_decision:{key}")

    if errors and not all(key in decision for key in required):
        return ValidationResult(False, tuple(errors))

    if decision["decision"] not in DECISIONS:
        errors.append("invalid_decision:value")

    expected_digest = digest(dict(request))
    if decision["request_digest"] != expected_digest:
        errors.append("binding:request_digest_mismatch")

    try:
        issued = _parse_time(decision["issued_at"])
        reference = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        age = (reference - issued).total_seconds()
        if age < -5:
            errors.append("freshness:issued_in_future")
        elif age > max_age_seconds:
            errors.append("freshness:decision_expired")
    except (TypeError, ValueError) as exc:
        errors.append(f"invalid:issued_at:{exc}")

    evidence_result = validate_evidence(decision.get("evidence"))
    errors.extend(evidence_result.errors)

    # Evidence can constrain a decision, but its mere presence never proves truth.
    if decision["decision"] == "ALLOW" and decision.get("evidence", {}).get("state") != "PRESENT":
        errors.append("allow:requires_present_evidence")

    if decision.get("boundary_version") != "VB-0.1":
        errors.append("boundary:unsupported_version")

    return ValidationResult(not errors, tuple(errors))


def validate_execution_attempt(
    request: Mapping[str, Any],
    decision: Mapping[str, Any],
    *,
    now: datetime | None = None,
) -> ValidationResult:
    """Final pre-execution latch.

    This is intentionally stricter than decision validation. Execution is allowed
    only for a valid, request-bound ALLOW or SANDBOX decision. DENY/ASK/DEFER are
    never executable, and a decision for another request cannot be replayed.
    """
    result = validate_decision(request, decision, now=now)
    errors = list(result.errors)
    if decision.get("decision") not in EXECUTABLE_DECISIONS:
        errors.append(f"execution:not_executable_decision:{decision.get('decision')}")
    return ValidationResult(not errors, tuple(errors))


def make_decision(request: Mapping[str, Any], decision: str, issued_at: str, evidence: Mapping[str, Any]) -> dict[str, Any]:
    """Create a minimal decision object bound to the exact request."""
    if decision not in DECISIONS:
        raise ValueError(f"unsupported decision: {decision}")
    return {
        "decision_id": f"dec-{digest({'request': dict(request), 'issued_at': issued_at})[:16]}",
        "request_digest": digest(dict(request)),
        "decision": decision,
        "issued_at": issued_at,
        "boundary_version": "VB-0.1",
        "evidence": dict(evidence),
    }
