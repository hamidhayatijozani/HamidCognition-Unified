"""Strict execution guard for the legacy Action Gate endpoint.

This adapter preserves the legacy record shape while enforcing the same
non-bypassable invariants as the Validation Boundary: signed decision,
request binding, executable decision, live nonce, and approval validity.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

EXECUTABLE = frozenset({"ALLOW", "SANDBOX"})


def _utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp_requires_timezone")
    return parsed.astimezone(timezone.utc)


def validate_legacy_execution(
    record: Mapping[str, Any],
    *,
    action_hash: str,
    nonce: str,
    signature_valid: bool,
    now: datetime | None = None,
) -> tuple[bool, str]:
    """Return whether this exact legacy decision may cross the execution gate."""
    if not signature_valid:
        return False, "decision_signature_invalid"
    if record.get("decision") not in EXECUTABLE:
        return False, "execution_not_permitted_by_gate"
    if record.get("action_hash") != action_hash:
        return False, "execution_action_binding_mismatch"
    if record.get("nonce") != nonce:
        return False, "execution_nonce_mismatch"
    if record.get("consumed_at") is not None:
        return False, "decision_nonce_already_consumed"
    try:
        if _utc(record["expires_at"]) <= (now or datetime.now(timezone.utc)).astimezone(timezone.utc):
            return False, "decision_expired"
    except (KeyError, TypeError, ValueError):
        return False, "decision_expiry_invalid"
    approval = record.get("approval")
    if approval and approval.get("approved"):
        try:
            if _utc(approval["expires_at"]) <= (now or datetime.now(timezone.utc)).astimezone(timezone.utc):
                return False, "approval_expired"
        except (KeyError, TypeError, ValueError):
            return False, "approval_expiry_invalid"
    return True, "validated_execution_guard"
