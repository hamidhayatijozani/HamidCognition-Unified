from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from storage import save_validation_event


async def handle_validation_error(request: Request, exc: RequestValidationError):
    correlation_id = request.headers.get("X-Correlation-ID") or f"corr_{uuid.uuid4().hex}"
    body = (await request.body()).decode("utf-8", errors="replace")
    save_validation_event(
        correlation_id=correlation_id,
        tenant_id=None,
        request_id=None,
        idempotency_key=request.headers.get("Idempotency-Key"),
        request_digest=None,
        validation_result="REJECT",
        error_code="schema_validation_failed",
        raw_request=body,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    return JSONResponse(status_code=422, content={"detail": "schema_validation_failed", "correlation_id": correlation_id})
