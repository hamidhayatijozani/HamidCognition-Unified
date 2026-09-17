"""Bind the legacy Action Gate record to the Validation Boundary.

This adapter grants no authority. It converts the persisted legacy record into
an explicit Validation Boundary request/decision pair and invokes the final
execution latch so the legacy endpoint cannot become a second execution path.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

try:
    from .execution_latch import ExecutionAuthorization, authorize_execution
    from .validation_boundary import digest
except ImportError:
    from execution_latch import ExecutionAuthorization, authorize_execution
    from validation_boundary import digest

BOUNDARY_VERSION = "VB-0.1"


def build_boundary_request(record: Mapping[str, Any]) -> dict[str, Any]:
    source = dict(record["request"])
    target = source.get("target")
    if not isinstance(target, str) or not target.strip():
        target = "<unspecified>"
    return {
        "request_id": str(record["request_id"]),
        "action": str(source["action"]),
        "target": target,
        "parameters": dict(source.get("parameters") or {}),
        "requester": str(
            source.get("agent_id")
            or record.get("identity", {}).get("agent_id")
            or "unknown"
        ),
        "timestamp": str(record["created_at"]),
    }


def build_boundary_evidence(record: Mapping[str, Any]) -> dict[str, Any]:
    """Bind evidence to the persisted decision basis, not to a truth claim."""
    artifact = {
        "decision_id": record["decision_id"],
        "action_hash": record["action_hash"],
        "policy_hash": record["policy_hash"],
        "policy_version": record["policy_version"],
    }
    return {
        "state": "PRESENT",
        "artifact_ref": f"decision://{record['decision_id']}/decision-basis",
        "sha256": digest(artifact),
    }


def build_boundary_decision(record: Mapping[str, Any]) -> dict[str, Any]:
    request = build_boundary_request(record)
    issued_at = record["created_at"]
    approval = record.get("approval")
    if approval and approval.get("approved") and approval.get("timestamp"):
        issued_at = approval["timestamp"]
    return {
        "decision_id": str(record["decision_id"]),
        "request_digest": digest(request),
        "decision": str(record["decision"]),
        "issued_at": str(issued_at),
        "boundary_version": BOUNDARY_VERSION,
        "evidence": build_boundary_evidence(record),
        "nonce": str(record["nonce"]),
    }


def _rejected(record: Mapping[str, Any], reason: str):
    decision = build_boundary_decision(record)
    authorization = ExecutionAuthorization(
        permitted=False,
        reason=reason,
        request_digest=decision["request_digest"],
        decision_id=decision["decision_id"],
        nonce="",
        boundary_version=BOUNDARY_VERSION,
    )
    return authorization, build_boundary_request(record), decision


def authorize_legacy_execution(
    record: Mapping[str, Any],
    *,
    action_hash: str,
    nonce: str,
    now: datetime | None = None,
) -> tuple[ExecutionAuthorization, dict[str, Any], dict[str, Any]]:
    if record.get("action_hash") != action_hash:
        return _rejected(record, "execution_action_binding_mismatch")
    if record.get("nonce") != nonce:
        return _rejected(record, "execution_nonce_mismatch")
    request = build_boundary_request(record)
    decision = build_boundary_decision(record)
    authorization = authorize_execution(request, decision, now=now)
    return authorization, request, decision
