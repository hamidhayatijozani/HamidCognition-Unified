from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from csg_contract import PermissionRequest
from csg_ingress import decide
from storage import save_validation_event

router = APIRouter(prefix="/v1/csg", tags=["HHJ-CSG"])


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
            correlation_id=correlation,
            tenant_id=None,
            request_id=None,
            idempotency_key=idempotency_key,
            request_digest=None,
            validation_result="REJECT",
            error_code="invalid_json",
            raw_request=raw,
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
        save_validation_event(correlation_id=correlation, tenant_id=req.tenant_id, request_id=req.request_id, idempotency_key=idempotency_key, request_digest=decision.request_digest, validation_result="PASS", error_code=None, raw_request=raw, created_at=decision.issued_at.isoformat())
        return {"correlation_id": correlation, **decision.model_dump(mode="json")}
    except HTTPException as exc:
        save_validation_event(correlation_id=correlation, tenant_id=req.tenant_id, request_id=req.request_id, idempotency_key=idempotency_key, request_digest=None, validation_result="REJECT", error_code=str(exc.detail), raw_request=raw, created_at=datetime.now(timezone.utc).isoformat())
        raise
