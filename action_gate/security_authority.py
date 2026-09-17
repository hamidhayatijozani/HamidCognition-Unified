"""Security/authority primitives for Action Gate MVP.

The module is intentionally dependency-free. It binds an authority token to
one canonical decision scope and rejects expiry, nonce reuse, tenant mismatch,
and action/resource mismatch before execution.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass, asdict
from typing import Any, Mapping


def canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_digest(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


class AuthorityError(ValueError):
    pass


@dataclass(frozen=True)
class Authority:
    decision_id: str
    tenant_id: str
    action_digest: str
    policy_digest: str
    nonce: str
    issued_at: int
    expires_at: int
    decision: str
    signature: str

    def payload(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("signature")
        return d

    def token(self) -> str:
        raw = canonical_json(asdict(self)).encode()
        return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def issue_authority(*, secret: bytes, decision_id: str, tenant_id: str,
                    action: Mapping[str, Any], policy: Mapping[str, Any],
                    decision: str, ttl_seconds: int = 300,
                    now: int | None = None, nonce: str | None = None) -> Authority:
    issued = int(time.time()) if now is None else int(now)
    if ttl_seconds <= 0:
        raise AuthorityError("ttl_seconds must be positive")
    payload = {
        "decision_id": decision_id,
        "tenant_id": tenant_id,
        "action_digest": canonical_digest(action),
        "policy_digest": canonical_digest(policy),
        "nonce": nonce or secrets.token_urlsafe(18),
        "issued_at": issued,
        "expires_at": issued + ttl_seconds,
        "decision": decision,
    }
    signature = hmac.new(secret, canonical_json(payload).encode(), hashlib.sha256).hexdigest()
    return Authority(**payload, signature=signature)


def verify_authority(*, authority: Authority, secret: bytes,
                     tenant_id: str, action: Mapping[str, Any],
                     policy: Mapping[str, Any], now: int | None = None,
                     used_nonces: set[str] | None = None) -> None:
    current = int(time.time()) if now is None else int(now)
    expected = hmac.new(secret, canonical_json(authority.payload()).encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, authority.signature):
        raise AuthorityError("invalid_signature")
    if authority.tenant_id != tenant_id:
        raise AuthorityError("tenant_mismatch")
    if current >= authority.expires_at or current < authority.issued_at:
        raise AuthorityError("expired_or_not_yet_valid")
    if authority.action_digest != canonical_digest(action):
        raise AuthorityError("action_binding_mismatch")
    if authority.policy_digest != canonical_digest(policy):
        raise AuthorityError("policy_binding_mismatch")
    if used_nonces is not None:
        if authority.nonce in used_nonces:
            raise AuthorityError("nonce_reuse")
        used_nonces.add(authority.nonce)
    if authority.decision not in {"ALLOW", "SANDBOX"}:
        raise AuthorityError("decision_not_executable")
