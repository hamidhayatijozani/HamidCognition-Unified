from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from canonicalization import KEY_ID, hmac_sha256, sha256_digest, verify_hmac
from csg_contract import DecisionObject


class DecisionAuthorityError(ValueError):
    """Raised when a stored decision cannot be proven authoritative."""


def verify_decision_authority(
    decision: DecisionObject,
    request_payload: dict[str, Any],
    *,
    now: datetime | None = None,
    require_unexpired: bool = True,
) -> None:
    """Verify exact request binding, decision digest and HMAC authority.

    Replay may call this with ``require_unexpired=False`` because replay
    reconstructs historical authority evidence and does not re-authorize a
    new execution. Execution paths must keep the default expiry check.
    """
    if decision.key_id != KEY_ID:
        raise DecisionAuthorityError("decision_key_id_not_current")

    request_digest = sha256_digest(request_payload)
    if request_digest != decision.request_digest:
        raise DecisionAuthorityError("decision_request_digest_mismatch")

    payload = decision.model_dump(mode="json", exclude_none=True)
    expected_digest = DecisionObject.digest_without_digest_fields(payload)
    if not _constant_time_equal(expected_digest, decision.decision_digest):
        raise DecisionAuthorityError("decision_digest_invalid")

    signed_fields = {
        "request_digest": decision.request_digest,
        "decision_digest": decision.decision_digest,
        "decision_id": decision.decision_id,
        "tenant_id": decision.tenant_id,
        "nonce": decision.nonce,
    }
    secret = __import__("os").getenv("ACTION_GATE_SIGNING_SECRET")
    if not secret:
        raise DecisionAuthorityError("decision_signing_secret_not_configured")
    if not verify_hmac(signed_fields, decision.signature, secret):
        raise DecisionAuthorityError("decision_signature_invalid")

    if require_unexpired:
        reference = now or datetime.now(timezone.utc)
        if decision.expires_at <= reference:
            raise DecisionAuthorityError("decision_expired")
        if decision.issued_at > reference:
            raise DecisionAuthorityError("decision_not_yet_valid")


def _constant_time_equal(left: str, right: str) -> bool:
    return hmac_sha256({"value": left}, "decision-authority-compare") == hmac_sha256(
        {"value": right}, "decision-authority-compare"
    )
