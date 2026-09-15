from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Header, HTTPException

from canonicalization import KEY_ID, SIGNATURE_ALGORITHM, hmac_sha256, sha256_digest, verify_hmac
from csg_contract import ALGORITHM_VERSION, CANONICALIZATION_VERSION, CONTRACT_VERSION, DecisionObject, PermissionRequest
from storage import load_idempotency, save_idempotency

REQUEST_TTL_SKEW_SECONDS = int(os.getenv("ACTION_GATE_REQUEST_TTL_SKEW_SECONDS", "300"))
DECISION_TTL_SECONDS = int(os.getenv("ACTION_GATE_DECISION_TTL_SECONDS", "300"))
SIGNING_SECRET = os.getenv("ACTION_GATE_SIGNING_SECRET")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def authenticate(authorization: str | None) -> None:
    token = os.getenv("ACTION_GATE_API_TOKEN")
    if not token:
        raise HTTPException(503, "csg_authentication_not_configured")
    if authorization != f"Bearer {token}":
        raise HTTPException(401, "invalid_action_gate_credentials")


def validate_timestamp(timestamp: datetime) -> None:
    if timestamp.tzinfo is None:
        raise HTTPException(422, "timestamp_must_be_timezone_aware")
    age = abs((utc_now() - timestamp).total_seconds())
    if age > REQUEST_TTL_SKEW_SECONDS:
        raise HTTPException(408, "request_timestamp_outside_allowed_window")


def request_payload(req: PermissionRequest) -> dict[str, Any]:
    return req.model_dump(mode="json", exclude_none=True)


def decision_payload(decision: DecisionObject) -> dict[str, Any]:
    return decision.model_dump(mode="json", exclude={"decision_digest", "signature"})


def deterministic_decision(req: PermissionRequest) -> tuple[str, str, list[str]]:
    action = req.action.lower()
    if action in {"transfer_funds", "transfer_money"}:
        return "SANDBOX", "CRITICAL", ["critical_financial_action"]
    if action in {"delete_database", "delete_customer", "delete_file"} and req.target and "prod" in req.target.lower():
        return "DENY", "CRITICAL", ["production_destructive_action"]
    if action in {"delete_database", "delete_customer", "delete_file", "send_email", "send_external_email", "http_post_external"}:
        return "ASK", "HIGH", ["sensitive_action_requires_approval"]
    return "ALLOW", "LOW", ["no_blocking_policy_matched"]


def build_decision(req: PermissionRequest) -> DecisionObject:
    decision, risk, constraints = deterministic_decision(req)
    issued = utc_now()
    expires = issued + timedelta(seconds=DECISION_TTL_SECONDS)
    nonce = uuid.uuid4().hex
    request_digest = sha256_digest(request_payload(req))
    unsigned = {
        "contract_version": CONTRACT_VERSION,
        "decision_id": f"dec_{uuid.uuid4().hex}",
        "request_id": req.request_id,
        "tenant_id": req.tenant_id,
        "decision": decision,
        "risk_level": risk,
        "request_digest": request_digest,
        "signature_algorithm": SIGNATURE_ALGORITHM,
        "key_id": KEY_ID,
        "canonicalization_version": CANONICALIZATION_VERSION,
        "policy_version": "hhj-csg-policy/1.0",
        "algorithm_version": ALGORITHM_VERSION,
        "issued_at": issued.isoformat(),
        "expires_at": expires.isoformat(),
        "nonce": nonce,
        "metrics_snapshot": {"validation": "PASS", "decision_determinism": "deterministic-v1"},
        "execution_receipt": None,
        "constraints": constraints,
    }
    decision_digest = sha256_digest(unsigned)
    if not SIGNING_SECRET:
        raise HTTPException(503, "csg_signing_secret_not_configured")
    signature = hmac_sha256({"request_digest": request_digest, "decision_digest": decision_digest, "decision_id": unsigned["decision_id"], "tenant_id": req.tenant_id, "nonce": nonce}, SIGNING_SECRET)
    return DecisionObject(**unsigned, decision_digest=decision_digest, signature=signature)


def verify_request_signature(req: PermissionRequest, signature: str | None) -> None:
    if not SIGNING_SECRET:
        raise HTTPException(503, "csg_signing_secret_not_configured")
    if not signature or not verify_hmac(request_payload(req), signature, SIGNING_SECRET):
        raise HTTPException(401, "request_signature_invalid")


def decide(req: PermissionRequest, authorization: str | None, idempotency_key: str | None, request_signature: str | None, correlation_id: str | None) -> tuple[DecisionObject, str]:
    authenticate(authorization)
    if not idempotency_key or len(idempotency_key) > 128:
        raise HTTPException(400, "idempotency_key_required")
    validate_timestamp(req.timestamp)
    verify_request_signature(req, request_signature)
    request_digest = sha256_digest(request_payload(req))
    existing = load_idempotency(req.tenant_id, idempotency_key)
    if existing:
        old_digest, old_response = existing
        if old_digest != request_digest:
            raise HTTPException(409, "idempotency_key_reused_for_different_request")
        return DecisionObject.model_validate_json(old_response), correlation_id or f"corr_{uuid.uuid4().hex}"
    decision = build_decision(req)
    response = decision.model_dump_json()
    save_idempotency(req.tenant_id, idempotency_key, request_digest, response, utc_now().isoformat())
    return decision, correlation_id or f"corr_{uuid.uuid4().hex}"
