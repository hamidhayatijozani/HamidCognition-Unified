from __future__ import annotations
import os
from typing import Any
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

GATE_URL = os.getenv("ACTION_GATE_URL", "http://action-gate:8000").rstrip("/")
GATE_TOKEN = os.getenv("ACTION_GATE_API_TOKEN", "")
app = FastAPI(title="HamidCognition Console", version="1.0.0")

INDEX = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>HamidCognition Action Gate</title>
<style>
body{font-family:system-ui,sans-serif;margin:0;background:#0b1020;color:#e8ecf4}main{max-width:1100px;margin:auto;padding:28px}
header{display:flex;justify-content:space-between;align-items:center;margin-bottom:24px}.brand{font-size:24px;font-weight:800}
.badge{padding:7px 12px;border-radius:999px;background:#17351f;color:#8ff0a4}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.card{background:#121a2d;border:1px solid #26314a;border-radius:16px;padding:20px}.wide{grid-column:1/-1}
button{border:0;border-radius:10px;padding:12px 16px;margin:5px;background:#2a6df4;color:white;font-weight:700;cursor:pointer}
button.danger{background:#a93232}pre{white-space:pre-wrap;word-break:break-word;background:#080c16;padding:14px;border-radius:10px;overflow:auto}
.metric{font-size:28px;font-weight:800}.muted{color:#9da8bd}input{width:100%;box-sizing:border-box;background:#0b1020;color:#fff;border:1px solid #34415d;border-radius:9px;padding:11px;margin:6px 0 12px}
@media(max-width:760px){.grid{grid-template-columns:1fr}.wide{grid-column:auto}}
</style></head>
<body><main>
<header><div class="brand">HAMIDCOGNITION · ACTION GATE</div><div id="status" class="badge">CHECKING</div></header>
<div class="grid">
<section class="card"><div class="muted">Runtime</div><div id="runtime" class="metric">...</div><p class="muted">Policy-enforced execution boundary</p></section>
<section class="card"><div class="muted">Product</div><div id="product" class="metric">...</div><p class="muted">Evidence-backed decision service</p></section>
<section class="card">
<h2>Live Decision Test</h2>
<p class="muted">These buttons call the real Action Gate API.</p>
<button onclick="evaluateAction('read_customer','customer/123')">ALLOW · read</button>
<button class="danger" onclick="evaluateAction('delete_database','production/customer-db')">DENY · destructive</button>
<label>Custom action</label><input id="action" value="send_report"><label>Target</label><input id="target" value="customer/123">
<button onclick="customEval()">Evaluate custom action</button>
</section>
<section class="card"><h2>Decision</h2><pre id="decision">No request yet.</pre></section>
<section class="card wide"><h2>Evidence</h2><pre id="evidence">Every decision is returned with decision ID, policy hash, action hash, nonce and evidence hash.</pre></section>
</div></main>
<script>
async function evaluateAction(action,target){
 const r=await fetch('/api/evaluate',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({action,target})});
 const d=await r.json(); document.getElementById('decision').textContent=JSON.stringify(d,null,2);
 document.getElementById('evidence').textContent=JSON.stringify(d,null,2);
}
async function customEval(){evaluateAction(document.getElementById('action').value,document.getElementById('target').value)}
async function boot(){
 try{const r=await fetch('/api/health');const d=await r.json();
 document.getElementById('runtime').textContent=d.status.toUpperCase();
 document.getElementById('product').textContent=d.version;
 document.getElementById('status').textContent=d.status==='ok'?'ONLINE':'DEGRADED';
 }catch(e){document.getElementById('status').textContent='OFFLINE';document.getElementById('runtime').textContent='OFFLINE'}
} boot();
</script></body></html>"""

def gate_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {GATE_TOKEN}"} if GATE_TOKEN else {}

@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return INDEX

@app.get("/health")
async def public_health() -> dict[str, Any]:
    return await health()

@app.get("/api/health")
async def health() -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.get(f"{GATE_URL}/health", headers=gate_headers())
    if r.status_code >= 400:
        raise HTTPException(r.status_code, "action_gate_unavailable")
    return r.json()

@app.post("/api/evaluate")
async def evaluate(payload: dict[str, Any]) -> dict[str, Any]:
    action = str(payload.get("action", "")).strip()
    target = str(payload.get("target", "")).strip() or None
    if not action:
        raise HTTPException(422, "action_required")
    body = {
        "tenant_id": "dashboard-demo",
        "agent_id": "hamidcognition-console",
        "actor_id": "dashboard-user",
        "session_id": "dashboard-session",
        "action": action,
        "target": target,
        "parameters": {},
        "context": {"surface": "customer-console"},
        "evidence": [{"source": "dashboard-input", "verified": True, "supports": ["requested_action"]}],
    }
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(f"{GATE_URL}/v1/action/evaluate", headers=gate_headers(), json=body)
    try:
        data = r.json()
    except Exception:
        data = {"detail": r.text}
    if r.status_code >= 400:
        raise HTTPException(r.status_code, detail=data)
    return data
