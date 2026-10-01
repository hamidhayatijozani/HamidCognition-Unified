from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

GATE_URL = os.getenv("ACTION_GATE_URL", "http://action-gate:8000").rstrip("/")
GATE_TOKEN = os.getenv("ACTION_GATE_API_TOKEN", "")
TENANT_ID = os.getenv("DASHBOARD_TENANT_ID", "dashboard-demo")
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
