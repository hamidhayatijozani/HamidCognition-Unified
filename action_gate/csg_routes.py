from __future__ import annotations

import hashlib
import hmac
import json
import uuid

from datetime import datetime, timezone

from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from canonicalization import canonicalize
from csg_contract import PermissionRequest
from csg_ingress import decide, deterministic_decision
from storage import load_idempotency, load_validation_request, save_validation_event

router = APIRouter(prefix="/v1/csg", tags=["HHJ-CSG"])


def request_digest(payload: dict) -> str:
    return hashlib.sha256(canonicalize(payload)).hexdigest()


@router.post("/decide")
async def csg_decide(
    request: Request,
    authorization: str | None = Header(default=None),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    request_signature: str | None = Header(default=None, alias="X-HCJ-Request-Signature"),
    correlation_id: str | None = Header(default=None, alias="X-Correlation-ID"),
):
    correlation = correlation_id or f"corr_{uuid.uuid4().hex}"
    raw = (await request.body()).decode("utf-8", errors="replace")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        save_validation_event(
            correlation_id=correlation, tenant_id=None, request_id=None, idempotency_key=idempotency_key,
            request_digest=None, validation_result="REJECT", error_code="invalid_json", raw_request=raw,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        return JSONResponse(status_code=400, content={"detail": "invalid_json", "correlation_id": correlation})

    try:
        req = PermissionRequest.model_validate(payload)
    except ValidationError:
        save_validation_event(
            correlation_id=correlation,
            tenant_id=payload.get("tenant_id") if isinstance(payload, dict) else None,
            request_id=payload.get("request_id") if isinstance(payload, dict) else None,
            idempotency_key=idempotency_key,
            request_digest=None,
            validation_result="REJECT",
            error_code="schema_validation_failed",
            raw_request=raw,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        return JSONResponse(status_code=422, content={"detail": "schema_validation_failed", "correlation_id": correlation})

    try:
        decision, correlation = decide(req, authorization, idempotency_key, request_signature, correlation, raw_payload=payload)
        save_validation_event(
            correlation_id=correlation, tenant_id=req.tenant_id, request_id=req.request_id,
            idempotency_key=idempotency_key, request_digest=decision.request_digest,
            validation_result="PASS", error_code=None, raw_request=raw,
            created_at=decision.issued_at.isoformat(),
        )
        return {"correlation_id": correlation, **decision.model_dump(mode="json")}
    except HTTPException as exc:
        save_validation_event(
            correlation_id=correlation, tenant_id=req.tenant_id, request_id=req.request_id,
            idempotency_key=idempotency_key, request_digest=None, validation_result="REJECT",
            error_code=str(exc.detail), raw_request=raw, created_at=datetime.now(timezone.utc).isoformat(),
        )
        raise


@router.get("/replay/{request_id}")
async def csg_replay(
    request_id: str,
    tenant_id: str,
    authorization: str | None = Header(default=None),
):
    """Replay-check a stored CSG request and decision without reissuing authority or executing anything."""
    from csg_ingress import authenticate

    authenticate(authorization)
    raw = load_validation_request(tenant_id, request_id)
    if raw is None:
        raise HTTPException(404, "csg_request_not_found")
    try:
        payload = json.loads(raw)
        req = PermissionRequest.model_validate(payload)
    except (json.JSONDecodeError, ValidationError):
        raise HTTPException(500, "stored_csg_request_corrupt")

    stored = load_idempotency(tenant_id, request_id)
    if stored is None:
        raise HTTPException(409, "csg_decision_not_persisted")
    stored_digest, stored_response = stored
    digest = request_digest(payload)
    if digest != stored_digest:
        raise HTTPException(500, "stored_csg_request_digest_mismatch")

    decision, risk, _ = deterministic_decision(req)
    stored_decision = json.loads(stored_response)
    decision_match = stored_decision.get("decision") == decision
    request_match = stored_decision.get("request_digest") == digest
    return {
        "request_id": request_id,
        "tenant_id": tenant_id,
        "replayed_decision": decision,
        "recorded_decision": stored_decision.get("decision"),
        "risk": risk,
        "request_digest": digest,
        "recorded_request_digest": stored_decision.get("request_digest"),
        "decision_match": decision_match,
        "request_digest_match": request_match,
        "match": decision_match and request_match,
        "side_effect_executed": False,
        "world_state_replay": False,
    }
