from __future__ import annotations

import hmac
import os
from datetime import datetime, timezone
from typing import Any

from canonicalization import KEY_ID, sha256_digest, verify_hmac
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

    request_id = request_payload.get("request_id")
    tenant_id = request_payload.get("tenant_id")
    if request_id != decision.request_id:
        raise DecisionAuthorityError("decision_request_id_mismatch")
    if tenant_id != decision.tenant_id:
        raise DecisionAuthorityError("decision_tenant_id_mismatch")

    request_digest = sha256_digest(request_payload)
    if request_digest != decision.request_digest:
        raise DecisionAuthorityError("decision_request_digest_mismatch")

    # build_decision signs the complete unsigned object, including explicit
    # null fields such as execution_receipt. Preserve those fields here so
    # verification uses the exact same canonical representation.
    payload = decision.model_dump(mode="json", exclude_none=False)
    expected_digest = DecisionObject.digest_without_digest_fields(payload)
    if not hmac.compare_digest(expected_digest, decision.decision_digest):
        raise DecisionAuthorityError("decision_digest_invalid")

    signed_fields = {
        "request_digest": decision.request_digest,
        "decision_digest": decision.decision_digest,
        "decision_id": decision.decision_id,
        "tenant_id": decision.tenant_id,
        "nonce": decision.nonce,
    }
    secret = os.getenv("ACTION_GATE_SIGNING_SECRET")
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
