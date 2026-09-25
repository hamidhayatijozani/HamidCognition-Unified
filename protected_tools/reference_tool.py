"""Reference protected tool boundary for HamidCognition Action Gate.

This runtime is deliberately side-effect-free. It demonstrates the required
execution boundary without pretending a demo endpoint is a production tool.
"""
from __future__ import annotations

from typing import Any

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from action_gate.enforcement import require_execution_authority
from action_gate.security_authority import canonical_digest

app = FastAPI(title="Reference Protected Tool Runtime", version="1.0.5")


class ActionRequest(BaseModel):
    tenant_id: str = Field(min_length=1)
    action: dict[str, Any]
    policy: dict[str, Any]
    parameters: dict[str, Any] = Field(default_factory=dict)


@app.post("/v1/protected/execute")
def execute_protected_action(
    request: ActionRequest,
    auth_context: dict[str, Any] = Depends(require_execution_authority),
) -> dict[str, Any]:
    """Execute only after the Action Gate authority has been consumed once.

    The dependency verifies signature, expiry, decision state and nonce.
    This handler additionally binds the concrete tenant/action/policy request
    to the authority digests before any side effect is permitted.
    """
    if auth_context["tenant_id"] != request.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="tenant_mismatch")
    if auth_context["action_digest"] != canonical_digest(request.action):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="action_binding_mismatch")
    if auth_context["policy_digest"] != canonical_digest(request.policy):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="policy_binding_mismatch")

    return {
        "status": "EXECUTED",
        "tenant_id": request.tenant_id,
        "action": request.action,
        "policy_snapshot": request.policy,
        "parameters": request.parameters,
        "decision_id": auth_context["decision_id"],
    }
