from __future__ import annotations

import os
import hashlib
import hmac
import json
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

GATE_URL = os.getenv("ACTION_GATE_URL", "http://action-gate:8000").rstrip("/")
GATE_TOKEN = os.getenv("ACTION_GATE_API_TOKEN", "")
TENANT_ID = os.getenv("DASHBOARD_TENANT_ID", "dashboard-demo")
APPROVAL_SECRET = os.getenv("ACTION_GATE_APPROVAL_SECRET", "")
ENFORCEMENT_URL = os.getenv("ENFORCEMENT_URL", "http://enforcement:8080").rstrip("/")
ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"

app = FastAPI(title="HamidCognition Console", version="2.0.1")
app.mount("/assets", StaticFiles(directory=STATIC_DIR), name="assets")


def gate_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {GATE_TOKEN}"} if GATE_TOKEN else {}


async def gate_request(
    method: str,
    path: str,
    *,
    json_body: dict[str, Any] | None = None,
    params: dict[str, str] | None = None,
) -> Any:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.request(
            method,
            f"{GATE_URL}{path}",
            headers=gate_headers(),
            json=json_body,
            params=params,
        )
    try:
        body = response.json()
    except Exception:
        body = {"detail": response.text}
    if response.status_code >= 400:
        detail = body.get("detail") if isinstance(body, dict) else body
        raise HTTPException(response.status_code, detail=detail)
    return body


@app.get("/", response_class=FileResponse)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def public_health() -> dict[str, Any]:
    return await health()


@app.get("/api/health")
async def health() -> dict[str, Any]:
    return await gate_request("GET", "/health")


@app.post("/api/evaluate")
async def evaluate(payload: dict[str, Any]) -> dict[str, Any]:
    action = str(payload.get("action", "")).strip()
    target = str(payload.get("target", "")).strip() or None
    agent_id = str(payload.get("agent_id", "")).strip() or "hamidcognition-console"
    actor_id = str(payload.get("actor_id", "")).strip() or "dashboard-user"
    if not action:
        raise HTTPException(422, "action_required")

    body = {
        "tenant_id": TENANT_ID,
        "agent_id": agent_id,
        "actor_id": actor_id,
        "session_id": "dashboard-session",
        "action": action,
        "target": target,
        "parameters": {},
        "context": {"surface": "customer-console"},
        "evidence": [
            {
                "source": "dashboard-input",
                "verified": True,
                "supports": ["requested_action"],
            }
        ],
    }
    return await gate_request("POST", "/v1/action/evaluate", json_body=body)


@app.post("/api/approve/{decision_id}")
async def approve(decision_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    tenant_id = str(payload.get("tenant_id") or TENANT_ID)
    evidence = await gate_request("GET", f"/v1/evidence/{decision_id}", params={"tenant_id": tenant_id})
    if evidence.get("decision") != "ASK":
        raise HTTPException(409, "decision_is_not_awaiting_approval")
    if not APPROVAL_SECRET:
        raise HTTPException(503, "approval_secret_not_configured")
    approval = {"approver_id": str(payload.get("approver_id") or "dashboard-operator"), "approved": bool(payload.get("approved", True)), "reason": str(payload.get("reason") or "Approved by Action Gate console"), "action_hash": evidence["action_hash"], "tenant_id": tenant_id, "policy_version": evidence["policy_version"]}
    canonical = json.dumps(approval, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    approval["approval_signature"] = hmac.new(APPROVAL_SECRET.encode(), canonical.encode(), hashlib.sha256).hexdigest()
    return await gate_request("POST", f"/v1/action/{decision_id}/approve", json_body=approval)


@app.post("/api/execute/{decision_id}")
async def execute(decision_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    tenant_id = str(payload.get("tenant_id") or TENANT_ID)
    actor_id = str(payload.get("actor_id") or "dashboard-user")
    agent_id = str(payload.get("agent_id") or "hamidcognition-console")
    session_id = str(payload.get("session_id") or "dashboard-session")
    action = str(payload.get("action") or "").strip()
    target = str(payload.get("target") or "").strip()
    parameters = payload.get("parameters") if isinstance(payload.get("parameters"), dict) else {}
    if not action or not target:
        raise HTTPException(422, "action_and_target_required")
    headers = {"X-Tenant-ID": tenant_id, "X-Actor-ID": actor_id, "X-Session-ID": session_id, "X-Agent-ID": agent_id, "X-Action": action, "X-Action-Target": target, "X-HCJ-Decision-ID": decision_id}
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(f"{ENFORCEMENT_URL}/tool", headers=headers, json=parameters)
    try:
        result = response.json()
    except Exception:
        result = {"detail": response.text}
    if response.status_code >= 400:
        raise HTTPException(response.status_code, detail=result)
    return {"executed": True, "decision_id": decision_id, "tool_response": result}


@app.get("/api/evidence/{decision_id}")
async def evidence(decision_id: str) -> dict[str, Any]:
    return await gate_request(
        "GET",
        f"/v1/evidence/{decision_id}",
        params={"tenant_id": TENANT_ID},
    )


@app.get("/api/replay/{decision_id}")
async def replay(decision_id: str) -> dict[str, Any]:
    return await gate_request(
        "GET",
        f"/v1/replay/{decision_id}",
        params={"tenant_id": TENANT_ID},
    )
