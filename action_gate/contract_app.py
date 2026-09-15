"""HHJ-CSG contract-first vertical slice.

This app is intentionally small and independent from the legacy Action Gate
MVP endpoint. It establishes the wire contract before AgentRQ simulation grows.
Run with: uvicorn action_gate.contract_app:app --port 8090
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request
from jsonschema import Draft202012Validator, FormatChecker

try:
    from .contract import (
        DECISION_CONTRACT_VERSION,
        REQUEST_CONTRACT_VERSION,
        CANONICALIZATION_VERSION,
        SIGNATURE_ALGORITHM,
        decision_signing_payload,
        hmac_sha256,
        load_schema,
        sha256_digest,
        verify_hmac,
    )
except ImportError:
    from contract import (
        DECISION_CONTRACT_VERSION,
        REQUEST_CONTRACT_VERSION,
        CANONICALIZATION_VERSION,
        SIGNATURE_ALGORITHM,
        decision_signing_payload,
        hmac_sha256,
        load_schema,
        sha256_digest,
        verify_hmac,
    )

API_KEY = os.getenv("HHJ_CSG_API_KEY")
HMAC_SECRET = os.getenv("HHJ_CSG_HMAC_SECRET")
HMAC_KEY_ID = os.getenv("HHJ_CSG_HMAC_KEY_ID", "poc-key-1")
MAX_REQUEST_AGE_SECONDS = int(os.getenv("HHJ_CSG_MAX_REQUEST_AGE_SECONDS", "300"))
FUTURE_SKEW_SECONDS = int(os.getenv("HHJ_CSG_FUTURE_SKEW_SECONDS", "5"))
DECISION_TTL_SECONDS = int(os.getenv("HHJ_CSG_DECISION_TTL_SECONDS", "300"))

app = FastAPI(title="HHJ-CSG Contract-First Vertical Slice", version="0.1.0")
_request_validator = Draft202012Validator(load_schema("permission_request.schema.json"), format_checker=FormatChecker())
_decision_validator = Draft202012Validator(load_schema("decision_object.schema.json"), format_checker=FormatChecker())
_idempotency: dict[str, tuple[str, dict[str, Any]]] = {}
_audit: list[dict[str, Any]] = []

POLICY_VERSION = "hhj-csg-policy-0.1"
ALGORITHM_VERSION = "deterministic-policy-0.1"


def _error(code: str, detail: Any, status: int = 422) -> None:
    raise HTTPException(status_code=status, detail={"code": code, "detail": detail})


def authenticate(api_key: str | None) -> None:
    if API_KEY is not None and api_key != API_KEY:
        _error("AUTHENTICATION_FAILED", "invalid_api_key", 401)


def verify_request_signature(request: dict[str, Any], signature: str | None) -> None:
    if HMAC_SECRET is None:
        return
    payload = {"contract_version": REQUEST_CONTRACT_VERSION, "request_digest": sha256_digest(request)}
    if not verify_hmac(payload, signature or "", HMAC_SECRET):
        _error("SIGNATURE_INVALID", "request_hmac_verification_failed", 401)


def validate_timestamp(value: str) -> None:
    try:
        ts = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        _error("TIMESTAMP_INVALID", "timestamp_must_be_iso8601", 422)
    if ts.tzinfo is None:
        _error("TIMESTAMP_INVALID", "timestamp_requires_timezone", 422)
    age = (datetime.now(timezone.utc) - ts.astimezone(timezone.utc)).total_seconds()
    if age > MAX_REQUEST_AGE_SECONDS:
        _error("REPLAY_TIMESTAMP_EXPIRED", "request_timestamp_too_old", 409)
    if age < -FUTURE_SKEW_SECONDS:
        _error("TIMESTAMP_IN_FUTURE", "request_timestamp_too_far_in_future", 409)


def deterministic_policy(request: dict[str, Any]) -> tuple[str, str, float]:
    action = request["action"].lower()
    target = request["target"].lower()
    if action in {"transfer_funds", "transfer_money"}:
        return "SANDBOX", "critical_financial_action", 0.99
    if action in {"delete_database", "delete_customer"} and ("prod" in target or "production" in target):
        return "DENY", "production_destructive_action", 0.99
    if action in {"delete_file", "delete_customer", "delete_database", "send_email", "send_external_email", "http_post_external"}:
        return "ASK", "sensitive_action_requires_approval", 0.95
    return "ALLOW", "no_blocking_policy_matched", 0.90


def make_decision(request: dict[str, Any], trace_id: str) -> dict[str, Any]:
    request_digest = sha256_digest(request)
    decision, reason, score = deterministic_policy(request)
    issued = datetime.now(timezone.utc)
    expires = issued + timedelta(seconds=DECISION_TTL_SECONDS)
    # The decision core is deterministic for replay. Runtime metadata is not.
    core = {
        "contract_version": DECISION_CONTRACT_VERSION,
        "request_id": request["request_id"],
        "request_digest": request_digest,
        "decision": decision,
        "risk_level": "CRITICAL" if score >= 0.99 else ("HIGH" if score >= 0.95 else "LOW"),
        "policy_version": POLICY_VERSION,
        "algorithm_version": ALGORITHM_VERSION,
        "canonicalization_version": CANONICALIZATION_VERSION,
        "metrics_snapshot": {"deterministic_score": score, "policy_reason": reason},
    }
    decision_id = "dec_" + sha256_digest(core)[:32]
    nonce = uuid.uuid4().hex
    result = {
        **core,
        "decision_id": decision_id,
        "issued_at": issued.isoformat(),
        "expires_at": expires.isoformat(),
        "nonce": nonce,
        "key_id": HMAC_KEY_ID,
        "signature_algorithm": SIGNATURE_ALGORITHM,
        "execution_receipt": {"status": "PENDING_EXECUTION", "decision_id": decision_id, "request_digest": request_digest},
        "trace_id": trace_id,
    }
    if HMAC_SECRET is None:
        # No secret means the POC can still exercise the contract, but it must
        # never be described as authenticated. The signature field is absent.
        result["signature"] = "0" * 64
    else:
        result["signature"] = hmac_sha256(decision_signing_payload(result), HMAC_SECRET)
    result["decision_digest"] = sha256_digest({k: v for k, v in result.items() if k not in {"decision_digest", "signature"}})
    if HMAC_SECRET is not None:
        result["signature"] = hmac_sha256(decision_signing_payload(result), HMAC_SECRET)
    return result


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "service": "HHJ-CSG", "contract": REQUEST_CONTRACT_VERSION, "decision_contract": DECISION_CONTRACT_VERSION}


@app.post("/decide")
async def decide(request: Request, x_api_key: str | None = Header(default=None), x_hhj_signature: str | None = Header(default=None), x_hhj_key_id: str | None = Header(default=None), x_hhj_canonicalization: str | None = Header(default=None)) -> dict[str, Any]:
    authenticate(x_api_key)
    if x_hhj_canonicalization not in (None, CANONICALIZATION_VERSION):
        _error("CANONICALIZATION_UNSUPPORTED", x_hhj_canonicalization, 422)
    if x_hhj_key_id not in (None, HMAC_KEY_ID):
        _error("KEY_ID_UNKNOWN", x_hhj_key_id, 401)
    try:
        body = await request.json()
    except Exception:
        _error("MALFORMED_JSON", "request_body_is_not_valid_json", 400)
    if not isinstance(body, dict):
        _error("INVALID_REQUEST", "permission_request_must_be_object", 422)
    errors = sorted(_request_validator.iter_errors(body), key=lambda e: list(e.path))
    if errors:
        _error("SCHEMA_INVALID", [{"path": list(e.path), "message": e.message} for e in errors], 422)
    validate_timestamp(body["timestamp"])
    request_digest = sha256_digest(body)
    verify_request_signature(body, x_hhj_signature)
    idem = body["idempotency_key"]
    prior = _idempotency.get(idem)
    if prior is not None:
        prior_digest, prior_response = prior
        if prior_digest != request_digest:
            _error("IDEMPOTENCY_KEY_REUSED", "same_key_with_different_request_digest", 409)
        return {**prior_response, "replayed": True}
    trace_id = "trace_" + uuid.uuid4().hex
    response = make_decision(body, trace_id)
    decision_errors = sorted(_decision_validator.iter_errors(response), key=lambda e: list(e.path))
    if decision_errors:
        _error("INTERNAL_CONTRACT_VIOLATION", [e.message for e in decision_errors], 500)
    _idempotency[idem] = (request_digest, response)
    _audit.append({"correlation_id": trace_id, "raw_request": body, "request_digest": request_digest, "validation": "VALID", "decision_digest": response["decision_digest"], "decision": response["decision"]})
    return {**response, "replayed": False}


@app.get("/audit/{correlation_id}")
def audit(correlation_id: str, x_api_key: str | None = Header(default=None)) -> dict[str, Any]:
    authenticate(x_api_key)
    for event in _audit:
        if event["correlation_id"] == correlation_id:
            return event
    _error("AUDIT_NOT_FOUND", correlation_id, 404)
