"""Protected-tool enforcement for HamidCognition Action Gate."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Mapping

from fastapi import Header, HTTPException

from .security_authority import Authority, AuthorityError, verify_authority
from .storage import consume_authority_nonce

AUTHORITY_HEADER = "X-Action-Gate-Authority"


def _authority_secret() -> bytes:
    secret = os.getenv("ACTION_GATE_AUTHORITY_SECRET")
    if not secret:
        raise HTTPException(503, "misconfigured_enforcement_secret")
    return secret.encode()


def enforce_execution_authority(
    raw_authority: str | None,
    *,
    expected_tenant_id: str | None = None,
    expected_action: Mapping[str, Any] | None = None,
    expected_policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Verify bindings, then atomically consume the authority nonce."""
    if not raw_authority:
        raise HTTPException(403, "direct_execution_bypassed_gate: Missing Execution Authority")

    try:
        authority = Authority.from_token(raw_authority)
        verify_authority(
            authority=authority,
            secret=_authority_secret(),
            tenant_id=expected_tenant_id or authority.tenant_id,
            action=expected_action or {},
            policy=expected_policy or {},
        )
    except AuthorityError as exc:
        code = str(exc)
        if code in {
            "tenant_mismatch",
            "action_binding_mismatch",
            "policy_binding_mismatch",
            "expired_or_not_yet_valid",
            "decision_not_executable",
        }:
            raise HTTPException(403, code) from exc
        raise HTTPException(403, f"invalid_execution_authority: {code}") from exc

    if not consume_authority_nonce(
        authority.nonce,
        authority.decision_id,
        datetime.now(timezone.utc).isoformat(),
    ):
        raise HTTPException(403, "nonce_reuse")

    return {
        "decision_id": authority.decision_id,
        "tenant_id": authority.tenant_id,
        "action_digest": authority.action_digest,
        "policy_digest": authority.policy_digest,
        "nonce": authority.nonce,
        "issued_at": authority.issued_at,
        "expires_at": authority.expires_at,
        "decision": authority.decision,
    }


def require_execution_authority(
    raw_authority: str | None = Header(default=None, alias=AUTHORITY_HEADER),
) -> dict[str, Any]:
    """FastAPI dependency. Endpoint code must also bind payload to this context."""
    return enforce_execution_authority(raw_authority)
